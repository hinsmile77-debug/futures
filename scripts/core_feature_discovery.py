# -*- coding: utf-8 -*-
"""CORE 피처 발굴 스크리닝 — 전 피처의 방향 예측력을 동일 잣대로 평가 (읽기 전용).

목적: CLAUDE.md 절대원칙 §3의 CORE 피처(체크리스트 게이트)를 교체·보강할 후보를
전수 스크리닝으로 찾는다. 현행 CORE도 **같은 잣대로 함께 평가**해 비교 가능하게 한다.

방법론 — Phase 0/372차 교훈을 그대로 반영:
  · 신호단위 풀링이 아니라 **일자단위 독립관측**으로 유의성 판정
    (풀링하면 하루 수백 개 상관된 분봉이 표본수를 부풀려 t가 과대평가된다)
  · **다중비교 보정** — 피처 수 × 호라이즌 수만큼 검정하므로 Bonferroni 적용
  · **전·후반 분할 안정성** — 우연한 구간 적합을 걸러낸다
  · 미래참조 없음 — 시각 t의 피처 vs t→t+h 수익률, 일중으로만(오버나이트 제외)

지표:
  IC      — 일자별 Spearman(feature_t, fwd_ret) → 일자평균과 t
  hit     — sign(feature 중심화) == sign(fwd_ret) 적중률 → 일자평균과 t (게이트 형태의 유용성)

실행:
  python scripts/core_feature_discovery.py                  # 최근 120거래일, h=5/15/30
  python scripts/core_feature_discovery.py --days 60 --top 30
"""
from __future__ import print_function

import argparse
import json
import math
import os
import sqlite3
import sys
from collections import OrderedDict, defaultdict

import numpy as np

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
RAW_DB = os.path.join(_ROOT, "data", "db", "raw_data.db")

from utils.analysis_db import (  # noqa: E402
    connect_ro, guard_intraday, utf8_console,
)

# CLAUDE.md 절대원칙 §3 현행 CORE (비교 기준선)
INCUMBENT = {
    "cvd_divergence": "단기 CORE",
    "vwap_position":  "단·중기 CORE",
    "ofi_norm":       "단기 CORE",
    "opt_chain_pcr":  "장기 CORE",
}
# 체크리스트가 실제로 소비하는 값(파라미터명은 cvd_direction이나 실제는 cvd_delta_norm)
INCUMBENT_EXTRA = {"cvd_delta_norm": "단기 CORE 실소비값"}

HORIZONS = [5, 15, 30]      # 단기/중기/장기 대표
MIN_DAY_ROWS = 60           # 하루 최소 유효 분봉
MIN_DAYS = 20
MIN_COVERAGE = 0.80         # 피처 결측 허용 하한 (**첫 관측 이후** 구간 기준)
MIN_DISTINCT = 20           # 상수·이진 플래그 제외

# [456차 / F3] 첫 관측 이후 최소 관찰 거래일.
# 커버리지를 first_seen 이후로 재정의하면 "어제 생긴 피처"가 커버리지 100%로 통과해
# 2~3일 표본의 우연한 IC가 후보 상단에 올라온다. 그 반대편 실패를 막는 하한이다.
MIN_DAYS_SINCE_FIRST_SEEN = 15

#: build_matrix()가 마지막 호출에서 탈락시킨 피처 내역.
#: 반환 시그니처를 바꾸면 이 함수를 import 하는 horizon_signal_tradability.py·
#: ic_decay_catalog.py가 조용히 깨지므로, 3-tuple 반환은 유지하고 부가 정보는 여기 남긴다.
LAST_SCREENING_REPORT = {"kept": [], "dropped": [], "total_rows": 0, "total_days": 0}


def load(days, con=None):
    """최근 `days` 거래일의 (피처행, 종가맵, 날짜목록) 로드.

    [456차 / F3] `WHERE substr(ts,1,10) >= ?` → `WHERE ts >= ?`.
    `raw_features`/`raw_candles`의 자동 인덱스는 `ts` 위에 있는데, `substr()`로 감싸면
    인덱스를 못 타 **468MB 테이블 전체 스캔**이 된다. ts가
    'YYYY-MM-DD HH:MM:SS' 고정폭이라 사전순 비교가 날짜 비교와 동치이므로 결과는 같다.
    """
    own = con is None
    if own:
        con = connect_ro(RAW_DB)
    cur = con.cursor()
    cur.execute("SELECT DISTINCT substr(ts,1,10) d FROM raw_candles ORDER BY d DESC LIMIT ?", (days,))
    dates = sorted(r[0] for r in cur.fetchall())
    lo = dates[0]
    cur.execute("SELECT ts, close FROM raw_candles WHERE ts >= ? ORDER BY ts", (lo,))
    closes = {ts: float(c) for ts, c in cur.fetchall() if c is not None}
    cur.execute("SELECT ts, features FROM raw_features WHERE ts >= ? ORDER BY ts", (lo,))
    feats = []
    for ts, fj in cur.fetchall():
        if ts not in closes:
            continue
        try:
            feats.append((ts, json.loads(fj)))
        except Exception:
            continue
    if own:
        con.close()
    return feats, closes, dates


def build_matrix(feats, verbose=True):
    """공통 수치 피처만 추려 (이름목록, 값행렬, ts목록) 반환.

    [456차 / F3] 커버리지를 **피처별 첫 관측 이후** 구간 기준으로 계산한다.

    구 방식은 관찰창 전체 행수(`n`)로 나눴다. 관찰창 중간에 도입된 피처는 도입 전
    구간이 통째로 결측으로 잡혀, 도입 후 매일 100% 수집돼도 탈락했다.

    2026-08-10 실측: `--days 40` 62개 vs `--days 19` 82개 — **20개가 도입일 때문에만
    보이지 않았다**. 그중에 CLAUDE.md 절대원칙 §3이 30m CORE로 규정한 `opt_chain_pcr`,
    그리고 `vkospi`(2026-07-14 도입, 이후 19거래일 연속 95~100% 커버)가 있었다.
    즉 **신규 피처는 도입 후 약 한 달간 L1에서 구조적으로 보이지 않았다.**

    탈락 내역은 `LAST_SCREENING_REPORT`에 남기고 `verbose=True`면 출력한다 —
    구 버전은 통과 개수만 찍어 무엇이 왜 빠졌는지 알 길이 없었다(조용한 실패).
    """
    n = len(feats)
    dates = [ts[:10] for ts, _ in feats]
    total_days = len(set(dates))

    # 1) 피처별 첫 수치 관측 위치와 관측 수
    cnt = defaultdict(int)
    first_idx = {}
    for i, (_, f) in enumerate(feats):
        for k, v in f.items():
            if isinstance(v, bool):
                continue
            if isinstance(v, (int, float)) and not (isinstance(v, float) and math.isnan(v)):
                cnt[k] += 1
                if k not in first_idx:
                    first_idx[k] = i

    # 2) 첫 관측 이후 기준 커버리지 + 관찰기간 하한
    eligible = {k: max(1, n - first_idx[k]) for k in cnt}
    days_since = {k: len(set(dates[first_idx[k]:])) for k in cnt}
    dropped = []
    names = []
    for k in sorted(cnt):
        cov = cnt[k] / float(eligible[k])
        if cov < MIN_COVERAGE:
            dropped.append((k, "커버리지 %.1f%% < %.0f%% (첫관측 이후 %d행 중 %d행)"
                            % (cov * 100, MIN_COVERAGE * 100, eligible[k], cnt[k])))
            continue
        if days_since[k] < MIN_DAYS_SINCE_FIRST_SEEN:
            dropped.append((k, "관찰 %d거래일 < %d (첫관측 %s — 표본 부족)"
                            % (days_since[k], MIN_DAYS_SINCE_FIRST_SEEN,
                               dates[first_idx[k]])))
            continue
        names.append(k)

    X = np.full((n, len(names)), np.nan, dtype=np.float64)
    idx = {k: j for j, k in enumerate(names)}
    ts_list = []
    for i, (ts, f) in enumerate(feats):
        ts_list.append(ts)
        for k, v in f.items():
            j = idx.get(k)
            if j is None:
                continue
            if isinstance(v, bool):
                continue
            if isinstance(v, (int, float)):
                X[i, j] = float(v)

    # 3) 상수·저해상도(이진 플래그 등) 제외 — 커버리지도 first_seen 기준으로 재확인
    keep = []
    for j, k in enumerate(names):
        col = X[:, j]
        col = col[~np.isnan(col)]
        if col.size < eligible[k] * MIN_COVERAGE:
            dropped.append((k, "행렬화 후 커버리지 미달 (%d < %d)"
                            % (col.size, int(eligible[k] * MIN_COVERAGE))))
            continue
        nuniq = np.unique(col).size
        if nuniq < MIN_DISTINCT:
            dropped.append((k, "고유값 %d < %d (상수·플래그)" % (nuniq, MIN_DISTINCT)))
            continue
        keep.append(j)

    kept_names = [names[j] for j in keep]
    LAST_SCREENING_REPORT.update({
        "kept": kept_names,
        "dropped": sorted(dropped),
        "total_rows": n,
        "total_days": total_days,
        # [500차 4단계] 구성적 중복 검사는 **탈락분까지** 봐야 한다.
        # 사전필터(고유값>=20)가 떨어뜨리는 저해상도 피처가 바로 부호형
        # 중복이 사는 곳이다 — `ofi_pressure ≡ sign(ofi_norm)` 이 그 예다.
        # 통과 피처만 보면 그 항등식이 영원히 안 보인다(advisory 전용 저장).
        "all_names": list(names),
        "all_X": X,
    })
    if verbose:
        print_screening_report()
    return kept_names, X[:, keep], ts_list


def print_screening_report():
    """스크리닝 통과/탈락 내역 출력 (G3-A3 탈락 가시화).

    필터링하는 코드는 *제외된 것의 개수와 사유*를 반드시 남긴다 — 구 버전이 통과
    개수만 찍은 탓에 20개 누락이 몇 주간 드러나지 않았다.
    """
    rep = LAST_SCREENING_REPORT
    print("스크리닝 대상 피처 %d개 / 후보 %d개 (커버리지 %.0f%%+ · 고유값 %d+ · 첫관측후 %d거래일+)"
          % (len(rep["kept"]) + len(rep["dropped"]), len(rep["kept"]),
             MIN_COVERAGE * 100, MIN_DISTINCT, MIN_DAYS_SINCE_FIRST_SEEN))
    if not rep["dropped"]:
        print("  제외 0개")
        return
    print("  제외 %d개 — 이번 창에서 평가되지 않은 피처:" % len(rep["dropped"]))
    for nm, why in rep["dropped"]:
        print("    %-32s %s" % (nm, why))


def rankdata(a):
    """평균순위(동점 처리) — scipy 없이."""
    order = np.argsort(a, kind="mergesort")
    ranks = np.empty(a.size, dtype=np.float64)
    ranks[order] = np.arange(1, a.size + 1, dtype=np.float64)
    # 동점 평균 처리
    sa = a[order]
    i = 0
    while i < sa.size:
        j = i
        while j + 1 < sa.size and sa[j + 1] == sa[i]:
            j += 1
        if j > i:
            ranks[order[i:j + 1]] = (i + 1 + j + 1) / 2.0
        i = j + 1
    return ranks


def corr(x, y):
    xm, ym = x - x.mean(), y - y.mean()
    dx, dy = math.sqrt(float((xm * xm).sum())), math.sqrt(float((ym * ym).sum()))
    if dx == 0 or dy == 0:
        return float("nan")
    return float((xm * ym).sum() / (dx * dy))


def tstat(v):
    v = np.asarray([x for x in v if not math.isnan(x)], dtype=np.float64)
    if v.size < 3:
        return float("nan"), 0
    sd = v.std(ddof=1)
    if sd == 0:
        return float("nan"), v.size
    return float(v.mean() / (sd / math.sqrt(v.size))), v.size


def analyze(names, X, ts_list, closes, horizon):
    """피처별 (일자평균 IC, IC t, 일자평균 hit, hit t, 유효일수, 전·후반 IC)."""
    by_day = defaultdict(list)
    for i, ts in enumerate(ts_list):
        by_day[ts[:10]].append(i)
    days = sorted(by_day)

    nf = len(names)
    ic_days = [[] for _ in range(nf)]
    hit_days = [[] for _ in range(nf)]
    day_tag = []

    for d in days:
        rows = by_day[d]
        if len(rows) < MIN_DAY_ROWS + horizon:
            continue
        ts_arr = [ts_list[i] for i in rows]
        # 일중 전방 수익률 (오버나이트 제외)
        fwd = np.full(len(rows), np.nan)
        for a in range(len(rows) - horizon):
            t0, t1 = ts_arr[a], ts_arr[a + horizon]
            if t0[:10] != t1[:10]:
                continue
            fwd[a] = closes[t1] - closes[t0]
        valid = ~np.isnan(fwd)
        if valid.sum() < MIN_DAY_ROWS:
            continue
        day_tag.append(d)
        fr = fwd[valid]
        fr_rank = rankdata(fr)
        fr_sign = np.sign(fr)
        sub = X[np.array(rows)[valid], :]
        for j in range(nf):
            col = sub[:, j]
            ok = ~np.isnan(col)
            if ok.sum() < MIN_DAY_ROWS or np.unique(col[ok]).size < 3:
                ic_days[j].append(float("nan")); hit_days[j].append(float("nan")); continue
            c = col[ok]
            ic_days[j].append(corr(rankdata(c), fr_rank[ok]))
            # 게이트 형태: 일중 중앙값 기준 중심화 후 부호 일치율
            cs = np.sign(c - np.median(c))
            m = (cs != 0) & (fr_sign[ok] != 0)
            hit_days[j].append(float((cs[m] == fr_sign[ok][m]).mean()) if m.sum() >= 20 else float("nan"))

    half = len(day_tag) // 2
    out = []
    for j, nm in enumerate(names):
        ic = np.array(ic_days[j], dtype=np.float64)
        ht = np.array(hit_days[j], dtype=np.float64)
        ic_t, nd = tstat(ic)
        hit_t, _ = tstat(ht - 0.5)
        ic_v = ic[~np.isnan(ic)]

        def _half_mean(seg):
            # 전·후반 IC 평균. 유효값이 없으면 nan (np.nanmean의 빈 슬라이스 경고 회피)
            s = seg[~np.isnan(seg)]
            return float(s.mean()) if s.size else float("nan")

        ic1 = _half_mean(ic[:half]) if half > 2 else float("nan")
        ic2 = _half_mean(ic[half:]) if half > 2 else float("nan")
        out.append({
            "name": nm,
            "ic": float(ic_v.mean()) if ic_v.size else float("nan"),
            "ic_t": ic_t, "n_days": nd,
            "hit": float(np.nanmean(ht)) if np.isfinite(ht).any() else float("nan"),
            "hit_t": hit_t,
            "ic_h1": float(ic1), "ic_h2": float(ic2),
            "stable": (np.isfinite(ic1) and np.isfinite(ic2)
                       and np.sign(ic1) == np.sign(ic2) and abs(ic1) > 0.005 and abs(ic2) > 0.005),
        })
    return out, len(day_tag)


# ── 참고 계측 (판정 무영향) ─────────────────────────────────────────
# [2026-08-25 신설] 둘 다 **표시 전용**이다. Bonferroni 검정 수(n_tests)에도,
# 통과 판정(★·종합)에도 절대 들어가지 않는다 — 사전등록 기준을 건드리지 않는다는
# 뜻이다(§9-4). 근거: `docs/Spec for feature/피처_재검증_및_호라이즌배정_원칙.md` §3·§5.
DUP_R_THRESHOLD = 0.99
# 455차 기본값은 shuffle 3 + phase 2 = 5개인데, 그것은 L1'의 **소수 후보** 검정용이다.
# L1은 80여 개를 전수로 훑으므로 5개로는 "노이즈 최고 |t|" 하한선이 과소추정된다
# (최댓값 통계는 표본 수에 민감하다). 병기 전용이라 개수 선택이 판정을 바꾸지 않는다.
NOISE_N_SHUFFLE = 12
NOISE_N_PHASE = 8


# ── [MW0601 500차 4단계 / SOP §3] 구성적 중복 (constructive duplication) ────
#
# 🔴 **선형 상관은 결정론적 파생을 놓친다.** 2026-08-30 실측(n=7,527):
#
#     ofi_imbalance ≡ round(ofi_norm/3, 3)   |r| = 0.9999  → 아래 find_dup_groups 가 잡음
#     ofi_pressure  ≡ sign(ofi_norm)         |r| = 0.4967  → 🔴 놓친다
#     |cvd_divergence| ≡ min(cvd_slope, 1)   |r| = 0.0262  → 🔴 놓친다
#
#   뒤의 둘은 **5,289/5,289 정확 일치하는 항등식**인데 Pearson 으로는 각각 0.50,
#   0.03 이다. 부호 함수·절대값 같은 비선형 파생은 상관이 낮게 나오기 때문이다.
#   이걸 못 잡으면 같은 신호를 독립 신호 여러 개로 세게 되고, 계열 검정의
#   **유효 자유도가 무너진다**(SOP §1 오측정 #9 — 수급 5피처를 5개로 세어
#   판정 미달 p=0.1426 을 자초한 그 사례).
#
# ⚠ **표기 전용 — 판정에 절대 관여하지 않는다**(n_tests 에 안 들어간다).
#   노이즈 하한선·중복 군집과 같은 취급이며 `--no-dup` 으로 함께 꺼진다.
#
# 검사하는 관계 4종 — 전부 "소스 5줄이면 아는 것"을 데이터로 되짚는 것이다:
#   scale  b == k*a  (상수 k, 반올림 허용)   ← ofi_imbalance
#   sign   b == sign(a)                      ← ofi_pressure
#   abs    |b| == |a| 또는 min(|a|, cap)     ← cvd_divergence ~ cvd_slope
#   round  b == round(a, d)
_CONSTRUCT_MIN_PAIRS = 200
_CONSTRUCT_TOL = 1.5e-3      # 반올림 자릿수(3~4자리) 를 흡수하는 허용오차
_CONSTRUCT_PREFILTER_R = 0.90  # a·|a|·sign(a) 중 하나라도 이 이상이면 정밀검사


def _exact_relation(a, b):
    """b 가 a 의 결정론적 파생인가. 관계 이름 또는 None."""
    n = len(a)
    if n < _CONSTRUCT_MIN_PAIRS:
        return None
    tol = _CONSTRUCT_TOL
    # sign — a 가 0 인 행은 반올림 경계라 제외하고 본다(그 비율도 함께 본다)
    nz = np.abs(a) > 1e-12
    if int(nz.sum()) >= _CONSTRUCT_MIN_PAIRS:
        if np.all(np.abs(np.sign(a[nz]) - b[nz]) <= tol):
            return "sign"
    # scale — 중앙값 비율로 k 를 잡고 전 행이 맞는지 확인
    if int(nz.sum()) >= _CONSTRUCT_MIN_PAIRS:
        k = float(np.median(b[nz] / a[nz]))
        if abs(k) > 1e-9 and np.all(np.abs(b - k * a) <= tol + tol * np.abs(a)):
            return "scale(k=%.6g)" % k
    # abs — 크기가 같다(부호만 다름). 상한 클립도 함께 본다.
    aa, ab = np.abs(a), np.abs(b)
    if np.all(np.abs(ab - aa) <= tol):
        return "abs"
    cap = float(np.max(ab))
    if cap > 0 and np.all(np.abs(ab - np.minimum(aa, cap)) <= tol):
        return "abs(cap=%.4g)" % cap
    # round
    for d in (1, 2, 3, 4):
        if np.all(np.abs(np.round(a, d) - b) <= 1e-9):
            return "round(%d)" % d
    return None


def _is_status_flag(name):
    """상태·가용성 플래그인가 — 구성적 중복 검사에서 **대상**으로 제외한다.

    `opt_atm_pcr → opt_chain_available (sign)` 같은 관계는 "값이 있으면 가용
    플래그가 1"이라는 **구조상 당연한** 것이지 정보 중복이 아니다. 걸러내지 않으면
    2026-08-30 실측에서 50쌍이 쏟아져(의미 있는 것은 그중 일부) 경보 피로로
    진짜 중복이 묻힌다 — 0802 계획 Phase A 확정사항 4번이 지적한 그 실패다.
    판정 기준은 `feature_health_report.is_benign_flag` 와 같은 출처를 쓴다.
    """
    try:
        from scripts.feature_health_report import is_benign_flag
        return is_benign_flag(name)
    except Exception:
        return (name.startswith(("is_", "quality_", "opt_available",
                                 "opt_chain_available"))
                or name.endswith(("_ready", "_available", "_measured")))


def find_constructive_dups(names, X):
    """결정론적 파생 쌍을 찾는다 (표기 전용).

    선형 상관(find_dup_groups)이 놓치는 비선형 항등식을 잡는다. 위 주석의
    실측 근거 참조. 반환: [(a, b, 관계이름), ...]
    """
    n = len(names)
    out = []
    # 사전필터 — a · |a| · sign(a) 세 변환 중 하나라도 상관이 높은 쌍만 정밀검사.
    # O(n^2) 정밀검사를 전 쌍에 돌리면 월간 실행이라도 느리다.
    cols = []
    for j in range(n):
        v = X[:, j]
        cols.append((v, np.abs(v), np.sign(v)))
    for i in range(n):
        ai = X[:, i]
        fi = np.isfinite(ai)
        for j in range(n):
            if i == j or _is_status_flag(names[j]):
                continue
            bj = X[:, j]
            m = fi & np.isfinite(bj)
            if int(m.sum()) < _CONSTRUCT_MIN_PAIRS:
                continue
            a, b = ai[m], bj[m]
            if np.std(a) < 1e-12 or np.std(b) < 1e-12:
                continue
            # 사전필터 — a 쪽 변환(원값·절대값·부호)을 b **와 |b| 양쪽**에 대본다.
            # ⚠ |b| 를 빠뜨리면 "크기 → 부호있는 값" 방향의 abs 관계를 놓친다.
            #   실데이터에서는 (cvd_divergence → cvd_slope) 처럼 부호있는 쪽이 a 라
            #   우연히 잡혔지만, a·b 가 뒤집히면 조용히 안 잡힌다(500차 4단계 C3).
            hit = False
            for vb in (b, np.abs(b)):
                if np.std(vb) < 1e-12:
                    continue
                for va in (a, np.abs(a), np.sign(a)):
                    if np.std(va) < 1e-12:
                        continue
                    r = np.corrcoef(va, vb)[0, 1]
                    if np.isfinite(r) and abs(r) >= _CONSTRUCT_PREFILTER_R:
                        hit = True
                        break
                if hit:
                    break
            if not hit:
                continue
            rel = _exact_relation(a, b)
            if rel:
                out.append((names[i], names[j], rel))
    return out


def find_dup_groups(names, X, thr=DUP_R_THRESHOLD, min_pairs=200):
    """|r| >= thr 인 피처를 군집으로 묶는다 (표기 전용).

    L1은 피처별 개별 검정이라 중복이 판정을 왜곡하지는 않는다. 막으려는 것은
    **사람의 오독**이다 — 같은 정보가 여러 이름으로 상위에 늘어서면 신호 다양성이
    과대 표시된다(2026-08-24 §14-7: 수급 5종이 h=1~30 상위를 독점).
    """
    n = len(names)
    parent = list(range(n))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for i in range(n):
        a = X[:, i]
        fa = np.isfinite(a)
        for j in range(i + 1, n):
            b = X[:, j]
            m = fa & np.isfinite(b)
            if int(m.sum()) < min_pairs:
                continue
            aa, bb = a[m], b[m]
            if aa.std() <= 0 or bb.std() <= 0:
                continue
            r = float(np.corrcoef(aa, bb)[0, 1])
            if np.isfinite(r) and abs(r) >= thr:
                union(i, j)

    buckets = defaultdict(list)
    for i in range(n):
        buckets[find(i)].append(names[i])
    return sorted((sorted(g) for g in buckets.values() if len(g) > 1),
                  key=lambda g: (-len(g), g[0]))


def build_noise_matrix(names, X, seed):
    """실피처를 템플릿으로 노이즈 대조 계열을 만든다 (별도 행렬 — bonf_t 무영향)."""
    try:
        from scripts.noise_benchmark import make_noise_features
    except Exception as e:
        print("[노이즈] 생성 불가(%s) — 하한선 병기를 건너뛴다" % e)
        return [], None
    cols = OrderedDict((nm, X[:, j].astype(np.float64)) for j, nm in enumerate(names))
    nz = make_noise_features(cols, seed,
                             n_shuffle=NOISE_N_SHUFFLE, n_phase=NOISE_N_PHASE)
    if not nz:
        return [], None
    nz_names = list(nz.keys())
    return nz_names, np.column_stack([nz[k] for k in nz_names])


def main():
    utf8_console()          # cp949 콘솔에서 비ASCII 출력이 죽는 것 방지 (455차 패턴)
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=120)
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--no-noise", action="store_true",
                    help="노이즈 하한선 병기를 끈다 (기본: 켬)")
    ap.add_argument("--no-dup", action="store_true",
                    help="중복 군집 표기를 끈다 (기본: 켬)")
    args = ap.parse_args()

    # 라이브 DB를 대량 읽는다 — 장중이면 CB⑤를 유발할 수 있어 차단한다(456차 F8).
    guard_intraday("core_feature_discovery")

    feats, closes, dates = load(args.days)
    print("raw_features %d행, %d거래일 (%s ~ %s)" % (len(feats), len(dates), dates[0], dates[-1]))
    names, X, ts_list = build_matrix(feats)

    n_tests = len(names) * len(HORIZONS)
    # 양측 t 임계 ~= Bonferroni α=0.05
    #
    # ⚠ [2026-08-25] 아래 노이즈 하한선·중복 군집은 **이 n_tests에 절대 들어가지 않는다.**
    #    노이즈 컬럼을 실피처와 같은 행렬에 넣으면 len(names)가 늘어 bonf_t가 올라가고,
    #    그 순간 "참고 정보 추가"가 **판정 기준 강화**로 바뀐다(사전등록 위반).
    #    그래서 노이즈는 별도 행렬로 따로 analyze 하고 결과만 병기한다.
    bonf_t = 3.0 + 0.55 * math.log(max(n_tests, 2))
    print("다중비교: 검정 %d회 -> Bonferroni 근사 |t| 임계 ~= %.2f" % (n_tests, bonf_t))

    # ── 중복·선형종속 군집 (표기 전용) ──────────────────────────
    # 왜: L1은 피처별 개별 검정이라 중복이 판정을 직접 왜곡하지는 않는다. 문제는
    # **리포트를 읽는 사람**이다 — 2026-08-24 §14-7에서 수급 5종(|r|>=0.99)이 h=1~30
    # 전 구간 상위를 차지해 "서로 다른 다섯 신호"로 읽혔으나 실은 같은 정보 하나였다.
    # ⚠ 다중비교 임계 완화 목적이 아니다 — 축약해도 임계는 6.435→6.402로 0.033만 내려간다.
    dup_groups = [] if args.no_dup else find_dup_groups(names, X)
    if dup_groups:
        print()
        print("[중복] |r|>=%.2f 군집 %d개 — 같은 정보가 여러 이름으로 세어지고 있다"
              % (DUP_R_THRESHOLD, len(dup_groups)))
        for g in dup_groups:
            print("   · %s" % " ~ ".join(g))
        print("   (표기 전용 — 판정·임계에 반영하지 않는다. 처분은 주간회의 안건)")
    elif not args.no_dup:
        print()
        print("[중복] |r|>=%.2f 군집 없음" % DUP_R_THRESHOLD)

    # ── 구성적 중복 (결정론적 파생) — [500차 4단계 / SOP §3] ─────
    # 위 선형 상관이 **놓치는** 항등식을 잡는다. 실측 근거:
    #   ofi_pressure ≡ sign(ofi_norm)        |r|=0.4967  ← 위에서 못 잡음
    #   |cvd_divergence| ≡ min(cvd_slope,1)  |r|=0.0262  ← 위에서 못 잡음
    # 둘 다 5,289/5,289 정확 일치하는 항등식이다.
    if not args.no_dup:
        # 탈락분 포함 전수 — 사전필터가 부호형 중복을 숨긴다(위 주석 참조)
        _an = LAST_SCREENING_REPORT.get("all_names") or names
        _aX = LAST_SCREENING_REPORT.get("all_X")
        cons = find_constructive_dups(_an, _aX if _aX is not None else X)
        print()
        if cons:
            print("[구성적중복] 결정론적 파생 %d쌍 — 상관이 낮아도 **같은 정보**다"
                  % len(cons))
            for a, b, rel in sorted(cons):
                print("   · %s → %s  (%s)" % (a, b, rel))
            print("   (표기 전용 — 판정·임계에 반영하지 않는다. 다만 계열 검정에서 "
                  "이들을 독립 신호로 세면 유효 자유도가 무너진다: SOP §1 오측정 #9)")
        else:
            print("[구성적중복] 결정론적 파생 없음")

    # ── CORE 우선 시계(D형) 스크린 — [500차 4단계 / SOP §2] ──────
    # 왜 CORE 를 **먼저** 보나: `cvd` 는 SOP §2 의 사전등록 임계(같은 hh:mm 날짜간
    # sd / 전체 sd < 0.05)로 **D형(시계)**이었는데(실측 0.020) 6개월간 아무도
    # 안 쟀다. CORE 는 체크리스트 게이트라 오염되면 전 호라이즌에 번지는데,
    # 전수 스크린 결과 안에 묻히면 눈에 안 띈다. 그래서 맨 앞에 따로 낸다.
    # ⚠ 표기 전용 — 등급·판정에 관여하지 않는다(feature_health_report 와 같은 원칙).
    try:
        from scripts.feature_health_report import (
            temporal_profile_series, SHAPE_DET_RATIO,
        )
        from config.constants import CORE_FEATURES as _CORE
        _watch = list(_CORE) + ["cvd_divergence", "cvd_slope", "cvd"]
        _days = [t[:10] for t in ts_list]
        _mins = [int(t[11:13]) * 60 + int(t[14:16]) for t in ts_list]
        _idx = {nm: k for k, nm in enumerate(LAST_SCREENING_REPORT["all_names"])}
        print()
        print("[CORE 시계] 같은 hh:mm 날짜간 sd / 전체 sd — %.2f 미만이면 D형(시계)"
              % SHAPE_DET_RATIO)
        _AX = LAST_SCREENING_REPORT["all_X"]
        for nm in _watch:
            if nm not in _idx:
                continue
            v = _AX[:, _idx[nm]]
            ok = np.isfinite(v)
            if int(ok.sum()) < MIN_DAY_ROWS:
                continue
            prof = temporal_profile_series(
                list(v[ok]), [d for d, o in zip(_days, ok) if o],
                [m for m, o in zip(_mins, ok) if o])
            dr = prof.get("det_ratio")
            tag = ""
            if dr is not None and dr < SHAPE_DET_RATIO:
                tag = "  🔴 D형 — 이 피처에 IC·수명 지표를 매기면 '시각'을 잰다"
            role = "CORE" if nm in _CORE else "관찰"
            print("   %-6s %-20s det_ratio=%s%s"
                  % (role, nm, ("%.3f" % dr) if dr is not None else "—", tag))
        print("   (표기 전용. 정본 분류·처분은 SOP §2 — 26주 재검증에서 한다)")
    except Exception as _e:
        print()
        print("[CORE 시계] 스킵 (%s) — 계측 실패이지 '이상 없음'이 아니다" % _e)

    # ── 노이즈 하한선 (병기 전용) ───────────────────────────────
    # 455차 N3 방법론. L1'(`ic_probe_pending_features.py`)은 이미 이 하한선을 쓰는데
    # 현역 전수인 L1에는 없어 **신규 후보만 시험받는 비대칭**이었다(2026-08-25 확인).
    # 여기서는 하한선을 **표시만** 한다 — 통과 조건에 넣는 것은 기준 강화라 주간회의 안건.
    noise_floor_by_h = {}
    if not args.no_noise:
        seed = int(dates[-1].replace("-", "")) if dates else 20260101
        nz_names, NZ = build_noise_matrix(names, X, seed)
        if nz_names:
            from scripts.noise_benchmark import noise_floor
            print()
            print("[노이즈] 하한선용 대조 계열 %d개 생성 (seed=%d) — "
                  "실피처와 **별도로** 검정한다(bonf_t 무영향)" % (len(nz_names), seed))
            for h in HORIZONS:
                nres, _nd = analyze(nz_names, NZ, ts_list, closes, h)
                fl, fnm = noise_floor(nres, name_key="name", stat_key="ic_t")
                noise_floor_by_h[h] = (fl, fnm)
                print("   h=%-3d 노이즈 최고 |IC_t| = %.2f (%s)"
                      % (h, fl, fnm or "—"))
            print("   (병기 전용 — 통과 판정에 넣지 않는다. 조건화는 주간회의 안건)")

    results = {}
    for h in HORIZONS:
        res, nd = analyze(names, X, ts_list, closes, h)
        results[h] = res
        grp = {5: "단기(1m·3m·5m)", 15: "중기(10m·15m)", 30: "장기(30m)"}[h]
        print()
        print("=" * 104)
        print("h=%d분  %s   유효일수 %d" % (h, grp, nd))
        print("=" * 104)

        print("  [기준선] 현행 CORE 및 실소비값")
        print("  %-26s %8s %8s %8s %8s %7s %s" % ("feature", "IC", "IC_t", "hit", "hit_t", "안정", "역할"))
        base = dict(INCUMBENT); base.update(INCUMBENT_EXTRA)
        for r in res:
            if r["name"] in base:
                print("  %-26s %8.4f %8.2f %8.4f %8.2f %7s %s"
                      % (r["name"], r["ic"], r["ic_t"], r["hit"], r["hit_t"],
                         "O" if r["stable"] else "-", base[r["name"]]))

        nf, nf_name = noise_floor_by_h.get(h, (float("nan"), None))
        print()
        hdr = "  [후보] |IC_t| 상위 %d — Bonferroni 통과(|t|>%.2f)는 ★" % (args.top, bonf_t)
        if np.isfinite(nf):
            hdr += " / 노이즈 하한(%.2f) 미만은 ▽" % nf
        print(hdr)
        print("  %-26s %8s %8s %8s %8s %7s %8s %8s %s" %
              ("feature", "IC", "IC_t", "hit", "hit_t", "안정", "IC전반", "IC후반", "noise"))
        ranked = sorted([r for r in res if np.isfinite(r["ic_t"])],
                        key=lambda r: -abs(r["ic_t"]))
        for r in ranked[:args.top]:
            star = "★" if abs(r["ic_t"]) > bonf_t else " "
            mark = "*" if r["name"] in base else " "
            # ▽ = 이 피처의 |IC_t|가 노이즈 최고치보다 낮다는 **표시**일 뿐이다.
            # 통과/탈락 판정(★·종합)은 위 bonf_t와 stable로만 결정된다.
            nmark = ""
            if np.isfinite(nf):
                nmark = "▽" if abs(r["ic_t"]) < nf else " "
            print(" %s%s%-25s %8.4f %8.2f %8.4f %8.2f %7s %8.4f %8.4f %s"
                  % (star, mark, r["name"], r["ic"], r["ic_t"], r["hit"], r["hit_t"],
                     "O" if r["stable"] else "-", r["ic_h1"], r["ic_h2"], nmark))
        if np.isfinite(nf):
            below = [r for r in ranked if abs(r["ic_t"]) < nf]
            print("  ▽ 노이즈 하한(%.2f, %s) 미만 %d/%d개 — 참고용 표시이며 판정과 무관"
                  % (nf, nf_name or "—", len(below), len(ranked)))

    # 종합: 전 호라이즌에서 안정적으로 유의한 피처
    print()
    print("=" * 104)
    print("종합 — Bonferroni 통과 ∧ 전·후반 부호 일치 (호라이즌별)")
    print("=" * 104)
    for h in HORIZONS:
        win = [r for r in results[h]
               if np.isfinite(r["ic_t"]) and abs(r["ic_t"]) > bonf_t and r["stable"]]
        win.sort(key=lambda r: -abs(r["ic_t"]))
        print("  h=%-3d 통과 %d개: %s" % (
            h, len(win), ", ".join("%s(IC=%+.3f,t=%.1f)" % (r["name"], r["ic"], r["ic_t"])
                                   for r in win[:12]) or "없음"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
