# -*- coding: utf-8 -*-
"""피처 건강도 리포트 — 죽은 피처(상수·영값 고착) 상시 감시.

왜 필요한가: 소진 6종·macro_nasdaq_chg 등이 **2개월 넘게 값이 전부 0인 채로**
방치됐고, 아무도 알아채지 못했다(Phase 0에서 발견). 원인은 제각각이었지만 공통점은
"조용히 죽어도 아무 신호가 없었다"는 것이다. 이 스크립트는 그 부류의 결함이 다시
장기 방치되지 않도록 zero-rate·상수화·점질량을 일괄 점검한다.

판정 등급:
  DEAD     — 전 구간 동일값(분산 0). 사실상 죽은 피처.
  CRITICAL — zero-rate ≥ 95% 또는 최빈값 비중 ≥ 95%. 거의 정보 없음.
  WARN     — zero-rate ≥ 80% 또는 최빈값 비중 ≥ 80%. 점질량 의심.
  OK       — 그 외.

별도 축 — PHANTOM(유령):
  DEAD/CRITICAL이면서 **가용성 게이트가 켜져 있는** 피처. "수집 실패라 0"이 아니라
  "수집 성공이라 보고하면서 0"이라는 모순이며, 원천에 없는 필드를 스키마 폴백이
  채워낸 경우가 전형이다(451차 program_* 사고). 아래 gate_for() 주석 참조.

읽기 전용 — raw_data.db(raw_features)만 SELECT 한다.

실행:
  python scripts/feature_health_report.py                 # 최근 20거래일
  python scripts/feature_health_report.py --days 60 --all # 전 피처 출력
  python scripts/feature_health_report.py --json out.json # 기계판독용
"""
from __future__ import print_function

import argparse
import json
import os
import sqlite3
import sys
from collections import Counter, defaultdict

# [MW0601 410차] Windows 기본 콘솔(cp949)에서 리포트 본문의 '—'(U+2014) 출력이
# UnicodeEncodeError로 죽어 이 도구를 수동 실행할 수 없던 결함 수정. 리다이렉트
# 없이도 돌아가야 한다 — 다른 리포트 스크립트들과 동일한 가드.
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DB = os.path.join(_ROOT, "data", "db", "raw_data.db")

DEAD_LEVEL = "DEAD"
CRIT_LEVEL = "CRITICAL"
WARN_LEVEL = "WARN"
OK_LEVEL = "OK"

CRIT_RATE = 0.95
WARN_RATE = 0.80
MIN_SAMPLES = 200

# ── 시간축 프로파일 (2026-08-25 신설) ────────────────────────────────
# 위 CRIT/WARN은 **값의 분포**만 본다. 아래 셋은 **시간 구조**를 본다 — 두 축은
# 겹치지 않는다(실측 교차표: L0 OK인데 시간축 부적격 27개 / 역방향 0개).
#
# ⚠ 이 임계는 `docs/Spec for feature/피처_재검증_및_호라이즌배정_원칙.md` §2와 같은
#    값이다. 한쪽만 바꾸면 주간 리포트와 26주 재검증이 다른 판정을 낸다 — 바꿀 때는
#    반드시 두 곳을 함께 고칠 것(임계 복사 사고 방지, 이 파일 58행 주석과 같은 취지).
# ⚠ 여기서 산출하는 `shape`는 **참고 표기이며 판정 등급(level)에 영향을 주지 않는다.**
#    등급 체계를 바꾸면 기존 리포트 시계열과 불연속이 생긴다(461차 mdd_pct 교훈).
ACF_MIN_OBS = 60          # 거래일별 최소 관측 (하루 390분 중)
SHAPE_TIE_CONST = 0.95    # 동률(delta=0) 이상이면 상수형 — 하루 종일 값이 안 변한다
SHAPE_GAP_STEP = 5.0      # 값 변화 간격 중앙값(분) 이상이면 계단형 — 원천 갱신 주기
SHAPE_ACF1_INTEG = 0.99   # lag-1 자기상관 이상이면 누적/비정상형
SHAPE_DET_RATIO = 0.05    # 같은 hh:mm 날짜간 변동/전체 변동 미만이면 결정론형(시계)
DET_MIN_DAYS = 5          # 결정론 판정 시 시각 슬롯당 최소 거래일

# 이미 원인이 규명돼 별도 관리 중인 피처 — 리포트에는 남기되 사유를 병기한다.
KNOWN = {
    "program_institution_net_krw": "원천 TR(CpSvr8111) 미제공 — 451차 폐기 집행. 과거 행 잔재",
    "program_individual_net_krw":  "원천 TR(CpSvr8111) 미제공 — 451차 폐기 집행. 과거 행 잔재",
    "program_foreign_net_krw":     "전체 프로그램 순매수 오라벨 — 451차 폐기 집행. 과거 행 잔재",
    "macro_event_flag":            "EVENT_DATES 빈 dict — 캘린더 미입력(Phase 0 §2-3)",
    "bear_exhaustion":             "394차 섀도 복구 중 — EXHAUSTION_RESTORE_MODE 참조",
    "bull_exhaustion":             "394차 섀도 복구 중 — EXHAUSTION_RESTORE_MODE 참조",
    "bear_exhaustion_signal":      "394차 섀도 복구 중",
    "bull_exhaustion_signal":      "394차 섀도 복구 중",
    "cvd_exhaustion":              "bear_exhaustion 별칭(deprecated)",
    "cvd_exhaustion_signal":       "bear_exhaustion_signal 별칭(deprecated)",
    "cvd":                         "CVD 포화(+1.0 고착) — buy_vol 편향 파생, 미해결 등록",
    "cvd_direction":               "CVD 포화 파생 — 미해결 등록",
    # [451차 Phase 0-4] PHANTOM 검출기가 잡은 신규 1건 — **수집 결함 아님**으로 종결.
    # opt_gex_bn(연속값)과 부호 불일치 0건, sign=0 행은 전부 opt_chain_available=0(미수집).
    # KOSPI200 감마 노출이 구조적으로 음수라 -1이 97.2%인 것이며 계측은 정상이다.
    # 다만 피처로서는 사실상 상수(+1이 07-15·07-23 단 2일, 그 뒤 11거래일 무변화)이고
    # opt_gex_bn의 순수 부호 함수라 정보가 중복이다. 학습 영향은 현재 0(active_features 미포함).
    "opt_gex_sign":                "시장구조(감마 음수 고착) — 계측 정상, 정보 중복. 451차 종결",
}

# 상태·품질 플래그는 "거의 항상 같은 값"이 오히려 정상이다(예: quality_*_available=1,
# is_monthly_witching=0). 이들까지 경보로 올리면 경보 피로로 진짜 이상이 묻히므로
# 별도 분류한다 — 표에는 그대로 나오되 "신규 이상" 목록에서는 제외한다.
_BENIGN_PREFIX = ("quality_", "macro_quality_", "opt_available", "opt_chain_available",
                  "is_", "hurst_ready", "basis_ready", "vkospi_ready",
                  "rv_iv_spread_ready", "feature_degraded", "entry_ok")

# [MW0601 500차 2단계] `*_measured` — 계측 4원칙 ②의 동반 플래그.
# "미측정 ≠ 0"을 구분하려고 새로 다는 플래그인데, 정상 운영에서는 거의 항상 1이라
# 등록하지 않으면 **신설하자마자 CRITICAL 로 뜬다**. 폴백을 드러내려고 만든 장치가
# 경보 피로를 만들어 진짜 이상을 묻는 셈이 되므로 상태플래그로 분류한다.
# ⚠ 등급 표에는 그대로 나온다 — 값이 갑자기 0 쪽으로 쏠리면 워밍업이 길어졌다는
#   뜻이므로 거기서 읽으면 된다.
_BENIGN_SUFFIX = ("_measured",)


def is_benign_flag(name):
    return name.startswith(_BENIGN_PREFIX) or name.endswith(_BENIGN_SUFFIX)


# ── 유령(PHANTOM) 피처 검출 ──────────────────────────────────────────────
#
# 왜 등급만으로는 부족한가 — 2026-08-09(451차) 사고:
#   `program_individual_net_krw` / `program_institution_net_krw`는 원천 TR
#   (`Dscbo1.CpSvr8111`)에 아예 없는 필드인데, 소비 계층의 `.get(key, 0)` 스키마
#   폴백이 상수 0을 매분 emit하면서 **동시에**
#   `quality_investor_program_supported = 1`을 보고했다. 바깥에서 보면
#   "수집 성공 + 값 0"이라 조용한 장세와 구분되지 않아 2개월 넘게 방치됐다.
#
# 이 표의 DEAD/CRITICAL 등급만으로는 그 둘을 못 가른다. 진짜 신호는 **모순**이다:
#   "가용하다고 보고하는 게이트가 켜져 있는데 정작 값이 상수다."
# 그 조합을 PHANTOM으로 따로 뽑아 KNOWN 등재 이전에 자동으로 드러낸다.
#
# 반대로 게이트가 꺼져 있는데 값이 0인 것은 **정직한 미수집**이다(예: 2026-08-04
# `opt_available=0` + `opt_pcr_*=0`). 그건 여기서 경보하지 않는다 — 원인이 이미
# 게이트에 정확히 표시돼 있기 때문이다.
_GATE_EXACT = {
    "foreign_futures_net":         "quality_investor_futures_supported",
    "retail_futures_net":          "quality_investor_futures_supported",
    "institution_futures_net":     "quality_investor_futures_supported",
    "foreign_retail_divergence":   "quality_investor_futures_supported",
    "foreign_call_net":            "quality_investor_option_supported",
    "foreign_put_net":             "quality_investor_option_supported",
}
# ⚠ 옵션은 게이트가 둘이고 출처가 다르다 — 섞으면 오검출한다.
#   `opt_pcr_*`  ← PCRStore(투자자 콜/풋 순매수)      게이트 `opt_available`
#   그 외 opt_*  ← OptionChainSnapshot(옵션체인 OI)  게이트 `opt_chain_available`
_GATE_PREFIX = (
    ("program_",     "quality_investor_program_supported"),
    ("opt_pcr_",     "opt_available"),
    ("opt_",         "opt_chain_available"),
    ("macro_",       "quality_macro_available"),
)

# 게이트가 이 비율 이상 켜져 있었으면 "가용하다고 보고했다"로 본다.
GATE_ON_MIN = 0.50


def gate_for(name):
    """이 피처의 가용성을 주장하는 품질 플래그 이름 (없으면 None)."""
    if name in _GATE_EXACT:
        return _GATE_EXACT[name]
    for prefix, gate in _GATE_PREFIX:
        if name.startswith(prefix):
            return gate
    return None


def gate_on_rate(rows, feature, gate):
    """`feature`가 존재하는 행에 한정해, 게이트가 켜져(≥0.5) 있던 비중.

    공존 행이 MIN_SAMPLES 미만이면 판정하지 않는다(None) — 소표본에서 우연히
    맞아떨어진 모순으로 경보를 내면 이 검출기 자체가 신뢰를 잃는다.
    """
    paired = [r[gate] for r in rows if feature in r and gate in r]
    if len(paired) < MIN_SAMPLES:
        return None
    return sum(1 for x in paired if x >= 0.5) / float(len(paired))


def collect(days):
    """행 단위 리스트를 반환한다.

    [451차] 이전에는 키별 값 리스트만 모았는데, 그러면 **행 정렬이 깨진다**. 실제로
    `macro_vix_abs` 같은 백필 전용 키는 7,533행 중 710행에만 존재하는데, 게이트
    비중을 전체 7,533행에서 재면 "게이트는 87% 켜졌는데 값은 상수"라는 가짜 모순이
    만들어져 유령으로 오검출된다. 게이트는 반드시 **그 피처가 존재하는 행에서만**
    재야 한다.

    [MW0601 2026-08-25] 반환에 **행별 거래일(day_of)** 을 추가했다. 시간축 지표
    (동률·ACF(1)·변화간격)는 일 경계를 넘어 계산하면 오버나이트 갭이 섞여 무의미해진다.
    이 함수는 이 파일 안에서만 호출되고 `generate_featureset_health_report.py`는 자체
    collect를 따로 갖고 있어, 반환값 확장의 영향 범위는 이 파일로 닫힌다.
    """
    con = sqlite3.connect(RAW_DB)
    cur = con.cursor()
    cur.execute("SELECT DISTINCT substr(ts,1,10) d FROM raw_features ORDER BY d DESC LIMIT ?", (days,))
    dates = sorted(r[0] for r in cur.fetchall())
    if not dates:
        return [], 0, None, None, [], []
    cur.execute("SELECT ts, features FROM raw_features WHERE substr(ts,1,10) >= ? ORDER BY ts",
                (dates[0],))
    rows = []
    day_of = []
    min_of = []
    for ts, fj in cur.fetchall():
        try:
            f = json.loads(fj)
        except Exception:
            continue
        row = {}
        for k, v in f.items():
            if isinstance(v, bool):
                v = 1.0 if v else 0.0
            if isinstance(v, (int, float)):
                row[k] = float(v)
        rows.append(row)
        day_of.append(ts[:10])
        min_of.append(ts[11:16])
    con.close()
    return rows, len(rows), dates[0], dates[-1], day_of, min_of


def series_of(rows, key):
    return [r[key] for r in rows if key in r]


def _median(xs):
    """순수 파이썬 중앙값 (numpy 없이 — 이 스크립트의 의존성 제약)."""
    s = sorted(xs)
    n = len(s)
    if n == 0:
        return None
    m = n // 2
    return float(s[m]) if n % 2 else (s[m - 1] + s[m]) / 2.0


def _acf1(v):
    """lag-1 자기상관 (공통 분모 표본 ACF). 표본 미달·상수면 None."""
    n = len(v)
    if n < ACF_MIN_OBS:
        return None
    mean = sum(v) / float(n)
    a = [x - mean for x in v]
    den = sum(x * x for x in a)
    if den <= 0:
        return None
    num = sum(a[i] * a[i + 1] for i in range(n - 1))
    return num / den


def _change_gap(v):
    """값이 바뀌는 시점 사이 간격(분)의 중앙값. 원천 갱신 주기를 드러낸다."""
    pos = [i for i in range(1, len(v)) if v[i] != v[i - 1]]
    if len(pos) < 3:
        return None
    return _median([pos[i] - pos[i - 1] for i in range(1, len(pos))])


def _sd(xs):
    n = len(xs)
    if n < 2:
        return None
    m = sum(xs) / float(n)
    return (sum((x - m) ** 2 for x in xs) / float(n)) ** 0.5


def _determinism_series(values, mins):
    """같은 시각(hh:mm)의 날짜간 변동 / 전체 변동.

    0에 가까우면 값이 **시각의 함수**라는 뜻이다 — 피처가 아니라 시계(`time_cos` 등).
    이 판정이 없으면 그런 계열이 ACF1이 높다는 이유로 '누적형'으로 오분류된다
    (2026-08-25 첫 실행에서 실제로 그랬다).
    """
    by_slot = defaultdict(list)
    for v, m in zip(values, mins):
        by_slot[m].append(v)
    allv = list(values)
    tot = _sd(allv)
    if not tot or tot <= 0:
        return None
    sds = [_sd(v) for v in by_slot.values() if len(v) >= DET_MIN_DAYS]
    sds = [s for s in sds if s is not None]
    if len(sds) < 30:
        return None
    return (sum(sds) / float(len(sds))) / tot


def temporal_profile(rows, day_of, min_of, key):
    """행 dict 목록용 어댑터 — 계산 본체는 `temporal_profile_series`."""
    v, d, m = [], [], []
    for r, dd, mm in zip(rows, day_of, min_of):
        if key in r:
            v.append(r[key])
            d.append(dd)
            m.append(mm)
    return temporal_profile_series(v, d, m)


def temporal_profile_series(values, days, mins):
    """시간축 프로파일 — 거래일별로 계산한 뒤 중앙값으로 합친다.

    L0가 쓰던 zero-rate·최빈값비중은 **값의 분포**만 본다. 그래서 "날마다 값은 다른데
    하루 안에서는 상수"인 계열(일봉 매크로)을 구조적으로 못 잡는다 — 2026-08-25 실측:
    `macro_us10y_chg`는 최빈값비중 13.3%(정상)인데 동률 99.9%(하루 종일 상수)였다.
    같은 이유로 누적형(`foreign_futures_net` ACF1=0.9967)과 계단형(옵션체인 갱신간격
    10분)도 전부 L0를 통과했다. 이 함수가 그 세 공백을 메운다.

    ⚠ **간이 판정이다.** 결측 행을 건너뛰어 압축하므로 격자가 엄밀하지 않고, 추세 R²·
    분산비는 계산하지 않는다(누적형 판정은 ACF(1) 하나로만 한다). 정본은 26주 재검증의
    `docs/Spec for feature/피처_재검증_및_호라이즌배정_원칙.md` §2이며, 여기서는
    **주간 감지**가 목적이다(그 문서 §13 참조 구현 `lifetime_taxonomy.py`).

    Args:
        values/days/mins: 같은 길이의 병렬 리스트 (값, 거래일 'YYYY-MM-DD', 시각 'HH:MM').

    Returns:
        dict(tie_rate, acf1, change_gap, det_ratio, shape) — 산출 불가 항목은 None.
        `shape`는 참고 표기이며 **판정 등급(level)에 영향을 주지 않는다.**
    """
    by_day = defaultdict(list)
    for v, d in zip(values, days):
        by_day[d].append(v)

    ties, acfs, gaps = [], [], []
    for v in by_day.values():
        if len(v) < ACF_MIN_OBS:
            continue
        diffs = [v[i] - v[i - 1] for i in range(1, len(v))]
        if diffs:
            ties.append(sum(1 for x in diffs if x == 0.0) / float(len(diffs)))
        a = _acf1(v)
        if a is not None:
            acfs.append(a)
        g = _change_gap(v)
        if g is not None:
            gaps.append(g)

    tie = _median(ties) if ties else None
    acf1 = _median(acfs) if acfs else None
    gap = _median(gaps) if gaps else None
    det = _determinism_series(values, mins)

    # 우선순위는 재검증 §2와 같다: 결정론 > 상수 > 계단 > 누적.
    shape = ""
    if det is not None and det < SHAPE_DET_RATIO:
        shape = "결정론형"
    elif tie is not None and tie >= SHAPE_TIE_CONST:
        shape = "상수형"
    elif gap is not None and gap >= SHAPE_GAP_STEP:
        shape = "계단형"
    elif acf1 is not None and acf1 >= SHAPE_ACF1_INTEG:
        shape = "누적형"
    return {"tie_rate": tie, "acf1": acf1, "change_gap": gap,
            "det_ratio": det, "shape": shape}


def classify(v):
    n = len(v)
    zero = sum(1 for x in v if x == 0.0) / float(n)
    c = Counter(round(x, 6) for x in v)
    mode_val, mode_cnt = c.most_common(1)[0]
    mode_rate = mode_cnt / float(n)
    if len(c) == 1:
        level = DEAD_LEVEL
    elif zero >= CRIT_RATE or mode_rate >= CRIT_RATE:
        level = CRIT_LEVEL
    elif zero >= WARN_RATE or mode_rate >= WARN_RATE:
        level = WARN_LEVEL
    else:
        level = OK_LEVEL
    return {
        "n": n, "zero_rate": zero, "mode_value": mode_val,
        "mode_rate": mode_rate, "distinct": len(c), "level": level,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=20)
    ap.add_argument("--all", action="store_true", help="OK 등급도 전부 출력")
    ap.add_argument("--json", default="", help="결과를 JSON으로 저장할 경로")
    args = ap.parse_args()

    if not os.path.exists(RAW_DB):
        print("raw_data.db 없음: %s" % RAW_DB)
        return 1

    data_rows, n_rows, d_from, d_to, day_of, min_of = collect(args.days)
    if not data_rows:
        print("raw_features 데이터 없음")
        return 1

    all_keys = set()
    for r in data_rows:
        all_keys.update(r.keys())

    print("피처 건강도 리포트 — %s ~ %s (%d행, %d개 피처)"
          % (d_from, d_to, n_rows, len(all_keys)))
    print("판정: DEAD=분산0 / CRITICAL=zero·최빈 95%+ / WARN=80%+ / OK=그 외")
    print("형태: 상수형=동률>=95%% / 계단형=변화간격>=%.0f분 / 누적형=ACF1>=%.2f "
          "(참고 표기 — 등급에 영향 없음)" % (SHAPE_GAP_STEP, SHAPE_ACF1_INTEG))

    report = {}
    for k in all_keys:
        v = series_of(data_rows, k)
        if len(v) < MIN_SAMPLES:
            continue
        report[k] = classify(v)
        report[k].update(temporal_profile(data_rows, day_of, min_of, k))

    # 유령 판정 — "가용하다고 보고했는데 값이 상수"인 모순 조합
    for k, r in report.items():
        r["gate"] = None
        r["gate_on_rate"] = None
        r["phantom"] = False
        if is_benign_flag(k) or r["level"] not in (DEAD_LEVEL, CRIT_LEVEL):
            continue
        gate = gate_for(k)
        if not gate or gate == k:
            continue
        rate = gate_on_rate(data_rows, k, gate)
        if rate is None:
            continue
        r["gate"] = gate
        r["gate_on_rate"] = rate
        r["phantom"] = rate >= GATE_ON_MIN

    order = {DEAD_LEVEL: 0, CRIT_LEVEL: 1, WARN_LEVEL: 2, OK_LEVEL: 3}
    rows = sorted(report.items(), key=lambda kv: (order[kv[1]["level"]], -kv[1]["mode_rate"]))

    counts = Counter(r["level"] for r in report.values())
    print()
    print("요약: DEAD=%d  CRITICAL=%d  WARN=%d  OK=%d"
          % (counts[DEAD_LEVEL], counts[CRIT_LEVEL], counts[WARN_LEVEL], counts[OK_LEVEL]))
    print()
    print("  %-9s %-30s %8s %8s %9s %8s %7s %7s  %s"
          % ("등급", "피처", "n", "zero%", "최빈비중", "고유값", "동률%", "형태", "비고"))
    shown = 0
    for k, r in rows:
        if r["level"] == OK_LEVEL and not args.all:
            continue
        shown += 1
        note = KNOWN.get(k) or ("상태플래그(상수 정상)" if is_benign_flag(k) else "")
        if r.get("phantom"):
            note = ("유령? " + note).strip()
        tie = r.get("tie_rate")
        print("  %-9s %-30s %8d %7.1f%% %8.1f%% %8d %6s %7s  %s"
              % (r["level"], k, r["n"], 100.0 * r["zero_rate"], 100.0 * r["mode_rate"],
                 r["distinct"],
                 ("%.0f%%" % (100.0 * tie)) if tie is not None else "-",
                 r.get("shape") or "-", note))
    if not shown:
        print("  (해당 없음 — 모든 피처 OK)")

    # ── 시간축 형태 이상 ────────────────────────────────────────
    # 값의 분포(zero·최빈)로는 정상인데 **시간 구조**가 특이한 피처. 위 표는 OK 등급을
    # 숨기므로 여기서 따로 낸다 — 2026-08-25 실측에서 이 부류 27개가 전부 L0 OK였다
    # (`opt_chain_pcr` 최빈비중 0.7%, `macro_us10y_chg` 13.3% 등).
    # 필터는 위 "신규 이상"과 같은 원칙이다 — KNOWN(원인 규명 완료)·상태플래그
    # (`is_*`/`quality_*`는 상수가 정상)·DEAD(이미 위 표에 나옴)는 뺀다. 이 필터가
    # 없으면 첫 실행처럼 64개가 쏟아져 0802 계획 Phase A 확정사항 4번이 지적한
    # "경보 피로"가 그대로 재발한다.
    shaped = [(k, r) for k, r in rows
              if r.get("shape")
              and r["level"] != DEAD_LEVEL
              and k not in KNOWN
              and not is_benign_flag(k)]
    print()
    if shaped:
        print("시간축 형태 이상 %d개 — 값 분포는 정상이나 decay·수명 지표를 매기면 "
              "다른 양을 잰다" % len(shaped))
        print("  %-30s %8s %7s %8s %9s  %s"
              % ("피처", "형태", "동률%", "ACF1", "변화간격", "비고"))
        for k, r in sorted(shaped, key=lambda kv: (kv[1]["shape"], kv[0])):
            note = KNOWN.get(k) or ("상태플래그(상수 정상)" if is_benign_flag(k) else "")
            if r["level"] != OK_LEVEL:
                note = ("등급 %s / " % r["level"] + note).strip(" /")
            print("  %-30s %8s %6s %8s %8s  %s"
                  % (k, r["shape"],
                     ("%.0f%%" % (100.0 * r["tie_rate"])) if r.get("tie_rate") is not None else "-",
                     ("%.4f" % r["acf1"]) if r.get("acf1") is not None else "-",
                     ("%.1f분" % r["change_gap"]) if r.get("change_gap") is not None else "-",
                     note))
        print("  → 이 목록은 **등급을 바꾸지 않는다.** 정본 분류·처분은 26주 재검증")
        print("    (`docs/Spec for feature/피처_재검증_및_호라이즌배정_원칙.md` §2)에서 한다.")
    else:
        print("시간축 형태 이상 없음")

    unknown_bad = [k for k, r in rows
                   if r["level"] in (DEAD_LEVEL, CRIT_LEVEL)
                   and k not in KNOWN and not is_benign_flag(k)]
    print()
    if unknown_bad:
        print("!! 신규 이상 피처 %d개 — 원인 조사 필요: %s"
              % (len(unknown_bad), ", ".join(unknown_bad)))
    else:
        print("신규 이상 피처 없음 (DEAD/CRITICAL은 전부 원인 규명·관리 중이거나 상태플래그)")

    # ── 유령 피처 ──────────────────────────────────────────────
    phantoms = [(k, r) for k, r in rows if r.get("phantom")]
    print()
    if phantoms:
        new_phantoms = [k for k, _ in phantoms if k not in KNOWN]
        print("🔴 유령 피처 %d개 — '가용' 보고와 상수값이 모순 (신규 %d개)"
              % (len(phantoms), len(new_phantoms)))
        print("   원천이 실제로 그 필드를 주는지 먼저 확인할 것. 스키마 폴백"
              "(.get(key, 0))이 상수를 만들어내고 있을 가능성이 높다.")
        for k, r in phantoms:
            print("   - %-28s %s=%.0f%% 켜짐인데 %s (고유값 %d, 최빈 %.1f%%)%s"
                  % (k, r["gate"], 100.0 * r["gate_on_rate"], r["level"],
                     r["distinct"], 100.0 * r["mode_rate"],
                     "  [기록됨: %s]" % KNOWN[k] if k in KNOWN else ""))
    else:
        print("유령 피처 없음 (가용 보고와 상수값이 모순되는 조합 없음)")

    # ── KNOWN 목록 부패 점검 ────────────────────────────────────
    # 원인이 해소됐는데 KNOWN에 남아 있으면, 그 항목이 앞으로의 진짜 이상을 조용히
    # 삼킨다. 451차처럼 폐기를 집행하면 해당 피처는 표에서 사라지므로 정리 시점을
    # 여기서 알려준다.
    stale_known = [k for k in KNOWN if k not in report]
    # OK만 '해소'로 본다 — WARN은 여전히 점질량 의심 구간이라, 이걸 정리 대상으로
    # 올리면 아직 살아 있는 문제(cvd 포화 등)의 기록을 지우게 된다.
    resolved_known = [k for k in KNOWN
                      if k in report and report[k]["level"] == OK_LEVEL]
    if stale_known or resolved_known:
        print()
        if stale_known:
            print("ℹ KNOWN 정리 가능(데이터에 없음, 폐기·표본미달): %s"
                  % ", ".join(sorted(stale_known)))
        if resolved_known:
            print("ℹ KNOWN 정리 가능(등급 해소됨): %s" % ", ".join(sorted(resolved_known)))

    if args.json:
        with open(args.json, "w") as fp:
            json.dump({"from": d_from, "to": d_to, "rows": n_rows, "features": report},
                      fp, indent=2)
        print("JSON 저장: %s" % args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
