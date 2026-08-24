# -*- coding: utf-8 -*-
"""[MW0601 410차] 호라이즌별 피처셋 주간 건강 리포트 (Phase A) — 읽기 전용.

근거: `docs/Spec for feature/피처셋_주기점검_자동리포트_구현계획_2026-08-02.md` Phase A.
상위 원칙: `CLAUDE.md` §3(CORE 그룹 교체 불가)·§6(자동 통합 금지),
`docs/Spec for feature/피처_발굴_표준절차.md` Phase 2(건강도 계측)·Phase 1(POOL 등록).

**왜 필요한가**: 검정 도구는 이미 6종이 있는데 전부 수동 실행 전용이라, 소진 6종·
`macro_nasdaq_chg`가 2개월간 값 전부 0인 채 방치된 유형의 사고를 아무도 자동으로
잡지 못한다. 이 리포트는 그 계측을 **주간 EOD 체인에 얹어** 무인화하되, 판단은
사람에게 남긴다.

무엇을 출력하나 (4개 절):
  §1·§2  L0 건강도 — 호라이즌별 **실배포 피처셋** 기준 DEAD/CRITICAL/WARN 집계·상세
  §3     L4 요약 — conf-층화 z-test 결과(별도 스크립트 산출물)를 읽어 요약
  §4     후보 파이프라인 현황판 — POOL/pending 후보의 raw_features 축적 진척
  §5     확정 결정 레지스트리(📌) — 이미 기각/조건부채택한 피처의 재론 차단

설계상 반드시 지킨 것 3가지:
  1) **배포 스펙의 진실은 `model/horizons/feature_names_{hz}.pkl`뿐이다.**
     `horizon_feature_sets.json`(계획 문서)이나 `shap_feature_registry.json`(PC별
     런타임 산출물, 커밋 안 됨)으로 판단하면 오판한다 — 337차·394차·07-30 실행계획
     0장이 전부 같은 함정을 밟았다. 여기서는 pkl을 직접 로드한다.
  2) **읽기 전용.** raw_data.db를 SELECT하고 md/json을 쓰는 것 외에 아무것도 하지
     않는다. 모델·설정·registry·featureset json 어디에도 쓰지 않는다.
  3) **계측이 죽으면 티가 나야 한다.** 데이터 부재·산출물 부재는 조용히 빈칸으로
     넘기지 않고 "⚠ 미배선/미계측"으로 명시한다(`toxicity_block_shadow`가 자기모순
     조건으로 3개월간 0건인 채 방치된 402차 후속3의 교훈).

실행:
  python scripts/generate_featureset_health_report.py
  python scripts/generate_featureset_health_report.py --days 20 --pool-days 60
  python scripts/generate_featureset_health_report.py --out-dir /tmp/x --no-prune
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import pickle
import re
import sqlite3
import subprocess
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# 건강도 판정 기준은 `feature_health_report`가 단일 출처다 — 여기서 재정의하지 않는다.
# (임계값이 두 곳에 복사되면 한쪽만 바뀌어 리포트끼리 다른 판정을 내는 사고가 난다)
from scripts.feature_health_report import (  # noqa: E402
    classify, is_benign_flag, KNOWN,
    DEAD_LEVEL, CRIT_LEVEL, WARN_LEVEL, OK_LEVEL, MIN_SAMPLES,
    temporal_profile_series, SHAPE_GAP_STEP, SHAPE_ACF1_INTEG,
)

RAW_DB = os.path.join(ROOT, "data", "db", "raw_data.db")
HORIZON_DIR = os.path.join(ROOT, "model", "horizons")
FEATURESET_JSON = os.path.join(ROOT, "featureset by horizon",
                               "horizon_feature_sets.json")

REPORT_STEM = "featureset_health"

# 미계측 — pkl에는 있는데 raw_features 창에서 표본이 모자란 경우. 등급 체계 밖의
# 별도 상태다("나쁘다"가 아니라 "잴 수 없다"). 섞으면 원인 진단이 흐려진다.
NA_LEVEL = "미계측"
# raw부재 — 모델 입력인데 raw_features에 키 자체가 없다. 미계측보다 무겁다
# (표본이 적은 게 아니라 계측이 그 피처를 아예 못 보고 있다).
MISSING_LEVEL = "raw부재"

_LEVEL_ORDER = {DEAD_LEVEL: 0, MISSING_LEVEL: 1, CRIT_LEVEL: 2, WARN_LEVEL: 3,
                NA_LEVEL: 4, OK_LEVEL: 5}

# "실이상"으로 셀 등급 — 이 등급이면서 KNOWN(원인 규명 완료)도 상태플래그도 아닌 것만
# 사람이 볼 필요가 있다. WARN을 빼는 이유: 점질량 80%대는 정상 피처에도 흔해
# (`opt_pcr_extreme` 84.6%) 매주 뜨면 경보 피로로 진짜 이상이 묻힌다 —
# `feature_health_report.py`의 "신규 이상" 정의와 동일하게 맞춘다.
_REAL_BAD_LEVELS = (DEAD_LEVEL, CRIT_LEVEL, MISSING_LEVEL)

# 후보가 "검증 가능"해지는 축적 기준 — `core_feature_discovery.MIN_DAYS`와 같아야
# 한다(L1' 월간 스크리닝이 그 값으로 후보를 거르므로, 여기서 "검증가능"이라 해놓고
# 정작 스크리닝에서 표본미달로 튕기면 현황판이 거짓말을 하는 셈이다).
try:
    from scripts.core_feature_discovery import MIN_DAYS as POOL_READY_DAYS
except Exception as _e:  # numpy 미가용 등 — 리포트를 막지는 않는다
    POOL_READY_DAYS = 20
    print("[경고] core_feature_discovery.MIN_DAYS 조회 실패(%s) → 기본 20 사용. "
          "두 값이 어긋나면 §4 '검증가능' 판정이 L1' 스크리닝과 불일치한다." % _e,
          file=sys.stderr)

# §4 발굴 세션 권고 트리거 — 살아있는 후보 재고가 이 미만이면 권고를 찍는다.
# 캘린더가 아니라 재고 기반인 이유: 구현계획 §5-2 — 발굴은 "때가 돼서" 하는 게 아니라
# 검증 파이프라인이 마르면 하는 것이다.
CANDIDATE_STOCK_MIN = 3

# §3 L4 입력 계약 — `horizon_conf_stratified_test.py`(07-30 실행계획 1단계 신설 대상)가
# 여기에 쓰기로 한 경로. 아직 그 스크립트가 없으므로 지금은 항상 "미배선"으로 뜬다.
# 이 경로/스키마는 그 스크립트를 만들 때 반드시 맞출 것(구현계획 Phase A 참조).
L4_JSON = os.path.join(ROOT, "data", "horizon_conf_stratified_latest.json")


# ──────────────────────────────────────────────────────────────
# 수집
# ──────────────────────────────────────────────────────────────

# [418차] 백필 생성 행 마커 (scripts/backfill_features.py:BACKFILL_QUALITY_MARKER와 동일).
BACKFILL_QUALITY_MARKER = 0.3
_LIVE_ONLY_SQL = ("json_extract(features,'$.feature_quality_score') IS NOT "
                  "%r" % BACKFILL_QUALITY_MARKER)


def _trading_dates(cur, n, include_backfill=False):
    """raw_features에 실제 행이 있는 최근 n개 날짜(오름차순).

    [418차] 기본은 **라이브 행이 1개라도 있는 날**만 센다. 백필 전용일을 거래일로
    치면 관찰창이 "N거래일"이라는 이름과 달리 실제 관측이 없는 날을 포함하게 된다 —
    MW0601의 2026-08-02 리포트가 20거래일 창에 백필 7일을 포함해 §2-b에 유령 DEAD
    4건을 띄우고 §4 축적일수를 부풀린 것이 그 결과다.
    """
    if include_backfill:
        cur.execute(
            "SELECT DISTINCT substr(ts,1,10) d FROM raw_features ORDER BY d DESC LIMIT ?",
            (int(n),))
    else:
        cur.execute(
            "SELECT substr(ts,1,10) d FROM raw_features WHERE " + _LIVE_ONLY_SQL +
            " GROUP BY d ORDER BY d DESC LIMIT ?",
            (int(n),))
    return sorted(r[0] for r in cur.fetchall())


def collect(days, pool_days, include_backfill=False):
    """단일 스캔으로 (건강도 표본, 후보 축적 일자)를 함께 모은다.

    전수 스캔(86k행)은 8초 이상 걸리고 데이터가 쌓일수록 선형으로 늘어난다. 두 창 중
    넓은 쪽까지만 읽어 비용을 상한선 안에 묶는다 — 축적 진척은 `POOL_READY_DAYS`
    도달 여부만 보면 되므로 60거래일 창이면 충분하다.

    [418차] 백필 생성 행은 기본적으로 제외한다(`include_backfill=True`로 복원 가능).
    그 행들은 OHLCV 파생만 실값이고 호가·수급·옵션·매크로가 전부 0.0이라, 섞이면
    두 방향으로 리포트를 왜곡한다:
      - §2-b: 백필 전용 키(`bear_reversal_signal`·`macro_vix_abs`·`microprice`·
        `feature_recoverable_errors`)가 "DEAD 100%"로 뜬다 — 죽은 피처가 아니라
        애초에 라이브가 기록하지 않는 퇴역 키다.
      - §4: presence 집계가 "값이 None이 아니면 그날 관측됨"으로 세는데 백필 행은
        `FEATURE_KEYS_ALL` 전 키를 0.0으로 채운다 — 한 번도 실제 수집되지 않은 날이
        축적일로 계상돼 **축적일수가 부풀려진다**(`foreign_futures_net` 60→17일,
        `cvd_direction` 60→32일). 실제보다 검증 준비가 된 것처럼 보인다.
    근거: dev_memory/DECISION_LOG.md 2026-08-02 MW0601 418차.

    반환: (vals, day_presence, meta, stamps)
      vals[key]         = 건강도 창(days)의 float 값 리스트
      day_presence[key] = 후보 창(pool_days)에서 그 키가 나타난 날짜 집합
      stamps[key]       = vals와 **병렬**인 (거래일, 'HH:MM') 목록 — 시간축 프로파일용
    """
    con = sqlite3.connect(RAW_DB, timeout=15)
    cur = con.cursor()
    wide = _trading_dates(cur, max(days, pool_days), include_backfill)
    if not wide:
        con.close()
        return {}, {}, {"rows": 0, "dates": []}, {}
    health_dates = set(wide[-days:]) if days > 0 else set()

    cur.execute("SELECT ts, features FROM raw_features WHERE substr(ts,1,10) >= ?",
                (wide[0],))
    vals = defaultdict(list)
    stamps = defaultdict(list)
    presence = defaultdict(set)
    n_rows = 0
    n_health_rows = 0
    n_bad = 0
    n_backfill = 0
    backfill_days = set()
    for ts, fj in cur.fetchall():
        try:
            f = json.loads(fj)
        except Exception:
            n_bad += 1
            continue
        d = ts[:10]
        if f.get("feature_quality_score") == BACKFILL_QUALITY_MARKER:
            n_backfill += 1
            backfill_days.add(d)
            if not include_backfill:
                continue
        n_rows += 1
        in_health = d in health_dates
        if in_health:
            n_health_rows += 1
        for k, v in f.items():
            if v is None:
                continue        # 값이 없는 키는 "그날 관측됨"으로 치지 않는다
            presence[k].add(d)
            if not in_health:
                continue
            if isinstance(v, bool):
                v = 1.0 if v else 0.0
            if isinstance(v, (int, float)):
                vals[k].append(float(v))
                # [2026-08-25] 시간축 프로파일용 스탬프. 값과 **병렬**로 쌓아야
                # 거래일·시각 대응이 유지된다(451차 "행 정렬이 깨진다"와 같은 이유).
                stamps[k].append((d, ts[11:16]))
    con.close()
    meta = {
        "rows": n_rows, "health_rows": n_health_rows, "bad_rows": n_bad,
        "wide_from": wide[0], "wide_to": wide[-1], "wide_days": len(wide),
        "health_from": min(health_dates) if health_dates else None,
        "health_to": max(health_dates) if health_dates else None,
        "health_days": len(health_dates),
        "backfill_rows": n_backfill,
        "backfill_days": len(backfill_days),
        "include_backfill": bool(include_backfill),
    }
    return dict(vals), dict(presence), meta, dict(stamps)


def health_table(vals):
    """키 → classify() 결과. 표본 미달은 NA_LEVEL로 남긴다(조용히 빼지 않는다)."""
    out = {}
    for k, v in vals.items():
        if len(v) < MIN_SAMPLES:
            out[k] = {"n": len(v), "level": NA_LEVEL, "zero_rate": None,
                      "mode_rate": None, "distinct": None, "mode_value": None}
        else:
            out[k] = classify(v)
    return out


def load_deployed(horizons):
    """호라이즌별 실배포 피처셋 — feature_names_{hz}.pkl 직접 로드.

    joblib이 아니라 표준 pickle로 읽는다. 이 파일들은 문자열 리스트라 numpy 객체가
    없어 pickle로 충분하고, py37_32/py310_64 어디서도 joblib 버전 차이를 타지 않는다.
    (joblib으로 저장돼도 pickle 프로토콜이라 표준 로더로 읽힌다 — 실측 확인)
    """
    out = {}
    for hz in horizons:
        p = os.path.join(HORIZON_DIR, "feature_names_%s.pkl" % hz)
        if not os.path.exists(p):
            out[hz] = {"names": None, "error": "파일 없음", "mtime": None}
            continue
        try:
            with open(p, "rb") as f:
                names = pickle.load(f)
            names = [str(x) for x in names]
            mt = datetime.datetime.fromtimestamp(os.path.getmtime(p))
            out[hz] = {"names": names, "error": None,
                       "mtime": mt.strftime("%Y-%m-%d %H:%M")}
        except Exception as e:
            out[hz] = {"names": None, "error": "로드 실패: %s" % e, "mtime": None}
    return out


def load_candidate_sources():
    """후보 명부 — DYNAMIC_FEATURES_POOL ∪ (호라이즌별 include_pending_validation).

    반환: {name: [출처 라벨, ...]}
    """
    src = defaultdict(list)
    try:
        from config.constants import DYNAMIC_FEATURES_POOL
        for n in DYNAMIC_FEATURES_POOL:
            src[str(n)].append("POOL")
    except Exception as e:
        print("[경고] DYNAMIC_FEATURES_POOL 로드 실패: %s" % e, file=sys.stderr)
    try:
        with open(FEATURESET_JSON, encoding="utf-8") as f:
            js = json.load(f)
        for hz, blk in js.items():
            if hz.startswith("_") or not isinstance(blk, dict):
                continue
            for item in blk.get("include_pending_validation") or []:
                nm = item.get("name") if isinstance(item, dict) else item
                if nm:
                    src[str(nm)].append("pending:%s" % hz)
    except Exception as e:
        print("[경고] horizon_feature_sets.json 로드 실패: %s" % e, file=sys.stderr)
    return dict(src)


def load_l4():
    """conf-층화 검정 산출물(있으면). 없으면 None — 호출부가 '미배선'으로 표시."""
    if not os.path.exists(L4_JSON):
        return None
    try:
        with open(L4_JSON, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"_error": "%s" % e}


def git_hash():
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
            stderr=subprocess.STDOUT, timeout=10)
        return out.decode("utf-8", "replace").strip()
    except Exception:
        return None


def _pc_dir_name():
    """산출물 폴더로 쓸 PC 이름 — 405차 P0-5/408차 규약과 동일(경고 포함)."""
    try:
        from utils.db_utils import pc_id
        raw = pc_id()
    except Exception:
        try:
            import platform as _pf
            host = _pf.node() or ""
            m = re.search(r"(MW\d{4})", host, re.IGNORECASE)
            raw = m.group(1).upper() if m else (host[:32] or "UNKNOWN")
        except Exception:
            raw = "UNKNOWN"
    safe = re.sub(r'[\\/:*?"<>|\s]+', "_", raw).strip("._") or "UNKNOWN"
    if not re.match(r"^MW\d{4}$", safe):
        print("[경고] PC 식별자가 MW#### 형식이 아니다: %r → 산출물 폴더 '%s' 사용. "
              "새 PC라면 호스트명을 확인할 것." % (raw, safe), file=sys.stderr)
    return safe


# ──────────────────────────────────────────────────────────────
# 리포트 조립
# ──────────────────────────────────────────────────────────────

def _fmt_pct(x):
    return "—" if x is None else "%.1f%%" % (100.0 * x)


def _note_for(name):
    if name in KNOWN:
        return KNOWN[name]
    if is_benign_flag(name):
        return "상태플래그(상수 정상)"
    return ""


def build_report(days, pool_days, include_backfill=False):
    warnings = []
    metrics = {}

    from config.settings import (
        HORIZONS, ENSEMBLE_WEIGHTS, HORIZON_CORE_GROUP, CORE_FEATURES_BY_GROUP,
    )
    import config.settings as _settings
    decisions = getattr(_settings, "FEATURE_SET_DECISIONS", None)
    if decisions is None:
        decisions = {}
        warnings.append(
            "`config/settings.py:FEATURE_SET_DECISIONS` 미정의 — 구현계획 Phase B "
            "미구현 상태다. §5가 비어 있는 것은 '결정이 없다'가 아니라 '레지스트리가 "
            "아직 없다'는 뜻이므로, 기각 피처가 §4에 후보로 다시 뜰 수 있다.")

    hz_list = list(HORIZONS.keys())
    vals, presence, meta, stamps = collect(days, pool_days, include_backfill)
    if not vals:
        warnings.append("raw_features에서 표본을 얻지 못했다 — DB 경로/데이터 확인 필요.")
    health = health_table(vals)
    deployed = load_deployed(hz_list)
    sources = load_candidate_sources()      # §2-b·§4가 함께 쓴다(한 번만 읽는다)

    today = datetime.date.today()
    pc = _pc_dir_name()
    gh = git_hash()

    L = []
    L.append("# 호라이즌별 피처셋 주간 건강 리포트 — %s · %s"
             % (pc, today.strftime("%Y-%m-%d")))
    L.append("")
    L.append("> 생성: `scripts/generate_featureset_health_report.py` (읽기 전용)  ")
    L.append("> 근거: `docs/Spec for feature/피처셋_주기점검_자동리포트_구현계획_"
             "2026-08-02.md` Phase A  ")
    L.append("> **이 리포트는 관측과 권고만 출력한다.** 피처셋 변경은 L3(purged CV) "
             "배터리 → 주간회의 수동 승인 → EOD 재학습 경로로만 이뤄진다 "
             "(`CLAUDE.md` §6 자동 통합 금지).")
    L.append("")
    if meta.get("health_from"):
        L.append("- 건강도 관찰창: **%s ~ %s** (%d거래일, %s행)"
                 % (meta["health_from"], meta["health_to"], meta["health_days"],
                    "{:,}".format(meta["health_rows"])))
    if meta.get("wide_from"):
        L.append("- 후보 축적 관찰창: %s ~ %s (%d거래일)"
                 % (meta["wide_from"], meta["wide_to"], meta.get("wide_days", 0)))
        # [418차] 관찰창 안에 백필 생성 행이 있으면 명시한다. 침묵하면 §2-b·§4를
        # 라이브 관측으로 오독하게 된다 — 2026-08-02 MW0601 리포트가 그 상태였다.
        _bf_rows, _bf_days = meta.get("backfill_rows", 0), meta.get("backfill_days", 0)
        if _bf_rows:
            if meta.get("include_backfill"):
                L.append("- 🚨 **관찰창에 백필 생성 행 %s행(%d일)이 포함돼 있다** "
                         "(`--include-backfill`). 이 행들은 호가·수급·옵션·매크로가 "
                         "전부 0.0이라 §2-b의 zero%%와 §4의 축적일수가 모두 왜곡된다. "
                         "판정을 그대로 믿지 말 것."
                         % ("{:,}".format(_bf_rows), _bf_days))
            else:
                L.append("- ℹ 관찰창 범위에서 백필 생성 행 %s행(%d일)을 **제외**했다 "
                         "(418차 기본 동작). 미시구조가 0.0인 소급 행이라 포함하면 "
                         "§2-b·§4가 왜곡된다. 포함하려면 `--include-backfill`."
                         % ("{:,}".format(_bf_rows), _bf_days))
    else:
        L.append("- ⚠ 후보 축적 관찰창: **데이터 없음** — `raw_features`에서 거래일을 "
                 "하나도 찾지 못했다. 아래 표는 전부 신뢰할 수 없다.")
    L.append("- 배포 스펙 출처: `model/horizons/feature_names_{hz}.pkl` **직접 로드** "
             "— `horizon_feature_sets.json`(계획 문서)·`shap_feature_registry.json`"
             "(PC별 런타임 산출물)이 아니다")
    L.append("- 판정 기준: `scripts/feature_health_report.py` 단일 출처 "
             "(DEAD=분산0 / CRITICAL=zero·최빈 95%%+ / WARN=80%%+ / 미계측=표본<%d)"
             % MIN_SAMPLES)
    if gh:
        L.append("- git: `%s`" % gh)
    L.append("")

    metrics["_meta"] = {
        "pc": pc, "date": today.strftime("%Y-%m-%d"), "git": gh,
        "days": days, "pool_days": pool_days,
        "min_samples": MIN_SAMPLES, "pool_ready_days": POOL_READY_DAYS,
        "window": meta,
    }

    # ── §1 호라이즌별 요약 ────────────────────────────────────
    L.append("## 1. 호라이즌별 요약")
    L.append("")
    L.append("| 호라이즌 | 앙상블 | 배포 피처 | OK | WARN | CRITICAL | DEAD | 미계측 "
             "| raw부재 | **실이상** | CORE |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")

    hz_detail = {}
    for hz in hz_list:
        info = deployed.get(hz) or {}
        names = info.get("names")
        w = float(ENSEMBLE_WEIGHTS.get(hz, 0.0))
        wtxt = "퇴역" if w == 0.0 else "%.2f" % w
        if names is None:
            L.append("| %s | %s | ⚠ %s | — | — | — | — | — | — | — | — |"
                     % (hz, wtxt, info.get("error") or "?"))
            warnings.append("%s 배포 피처셋을 읽지 못했다: %s — 이 호라이즌은 이번 주 "
                            "건강도 판정에서 통째로 빠졌다(정상 아님)."
                            % (hz, info.get("error")))
            hz_detail[hz] = None
            continue

        rows = []
        for nm in names:
            h = health.get(nm)
            if h is None:
                rows.append((nm, {"level": MISSING_LEVEL, "n": 0, "zero_rate": None,
                                  "mode_rate": None, "distinct": None}))
            else:
                rows.append((nm, h))
        cnt = Counter(r[1]["level"] for r in rows)
        real_bad = [n for n, h in rows
                    if h["level"] in _REAL_BAD_LEVELS
                    and n not in KNOWN and not is_benign_flag(n)]

        # CORE는 체크리스트 게이트(strategy/entry/checklist.py)라 모델 입력이 아닐 수
        # 있다 — pkl 미포함은 이상이 아니다. 건강도만 별도로 본다.
        grp = HORIZON_CORE_GROUP.get(hz)
        core_names = []
        for k, v in (CORE_FEATURES_BY_GROUP.get(grp) or {}).items():
            if isinstance(v, str):
                core_names.append(v)
        core_bad = [n for n in core_names
                    if (health.get(n) or {}).get("level") in (DEAD_LEVEL, CRIT_LEVEL)]
        core_txt = "⚠ " + ", ".join(core_bad) if core_bad else "OK"

        L.append("| %s | %s | %d | %d | %d | %d | %d | %d | %d | **%d** | %s |"
                 % (hz, wtxt, len(names), cnt[OK_LEVEL], cnt[WARN_LEVEL],
                    cnt[CRIT_LEVEL], cnt[DEAD_LEVEL], cnt[NA_LEVEL],
                    cnt[MISSING_LEVEL], len(real_bad), core_txt))
        hz_detail[hz] = {"rows": rows, "core": core_names, "core_bad": core_bad,
                         "weight": w, "mtime": info.get("mtime"),
                         "real_bad": real_bad}
        metrics.setdefault("horizons", {})[hz] = {
            "weight": w, "n_features": len(names), "pkl_mtime": info.get("mtime"),
            "counts": {k: int(cnt[k]) for k in
                       (OK_LEVEL, WARN_LEVEL, CRIT_LEVEL, DEAD_LEVEL, NA_LEVEL,
                        MISSING_LEVEL)},
            "real_bad": real_bad,
            "core": core_names, "core_bad": core_bad,
            "features": {n: h["level"] for n, h in rows},
        }
    L.append("")
    L.append("> **`실이상`만 보면 된다** — DEAD·CRITICAL·raw부재 중 원인 미규명이고 "
             "상태플래그도 아닌 것의 수. `is_*`/`quality_*`처럼 \"항상 같은 값이 정상\"인 "
             "플래그는 CRITICAL/WARN 열에 잡혀도 실이상이 아니다(경보 피로 방지 — "
             "`feature_health_report.py`의 '신규 이상'과 같은 정의).  ")
    L.append("> `앙상블=퇴역`은 `ENSEMBLE_WEIGHTS`가 0.0인 호라이즌(1m 331차 후속2, "
             "30m 296차) — 방향투표에 쓰이지 않으므로 개선 대상이 아니다.  ")
    L.append("> `raw부재` = 모델 입력인데 `raw_features`에 기록이 없는 피처. 0이 "
             "아니면 계측 자체가 그 피처를 못 보고 있다는 뜻이라 우선 조사 대상이다.  ")
    L.append("> `CORE`는 체크리스트 게이트(`CLAUDE.md` §3)라 모델 입력이 아닐 수 "
             "있다 — pkl 미포함은 이상이 아니므로 건강도만 본다.")
    L.append("")

    # ── §2 호라이즌별 상세 ────────────────────────────────────
    L.append("## 2. 호라이즌별 상세 (정상 아닌 것만)")
    L.append("")
    any_detail = False
    for hz in hz_list:
        d = hz_detail.get(hz)
        if not d:
            continue
        bad = [(n, h) for n, h in d["rows"] if h["level"] != OK_LEVEL]
        bad.sort(key=lambda nh: (_LEVEL_ORDER.get(nh[1]["level"], 9), nh[0]))
        L.append("### %s — 배포 %d개 (pkl %s)"
                 % (hz, len(d["rows"]), d.get("mtime") or "mtime?"))
        L.append("")
        if not bad:
            L.append("전 피처 OK.")
        else:
            any_detail = True
            L.append("| 등급 | 피처 | n | zero% | 최빈비중 | 고유값 | 비고 |")
            L.append("|---|---|---|---|---|---|---|")
            for n, h in bad:
                L.append("| %s | `%s` | %s | %s | %s | %s | %s |"
                         % (h["level"], n, h.get("n", 0),
                            _fmt_pct(h.get("zero_rate")), _fmt_pct(h.get("mode_rate")),
                            h.get("distinct") if h.get("distinct") is not None else "—",
                            _note_for(n)))
        core_line = []
        for n in d["core"]:
            lv = (health.get(n) or {}).get("level", MISSING_LEVEL)
            core_line.append("`%s`=%s" % (n, lv))
        if core_line:
            L.append("")
            L.append("CORE(%s): %s" % (HORIZON_CORE_GROUP.get(hz), " / ".join(core_line)))
        L.append("")

    # 신규 이상 — 원인 미규명 + 상태플래그 아님 (경보 피로 방지)
    unknown_bad = sorted({
        n for hz in hz_list for n in ((hz_detail.get(hz) or {}).get("real_bad") or [])
    })
    L.append("**배포 피처 신규 이상(원인 미규명·상태플래그 제외)**: %s"
             % (", ".join("`%s`" % n for n in unknown_bad) if unknown_bad
                else "없음"))
    metrics["unknown_bad"] = unknown_bad
    if not any_detail:
        L.append("")
        L.append("(모든 배포 피처가 OK — 상세 표 없음)")
    L.append("")

    # ── §2-b 전체 raw 피처 신규 이상 ─────────────────────────
    # 왜 따로 보나: 위 §1·§2는 **배포된 모델 입력만** 본다. 그런데 계측이 죽는 사고는
    # 배포 전 단계에서 더 자주 난다 — 소진 6종이 2개월간 전부 0이었던 것도, 이번
    # 실측에서 `bear_reversal_signal`·`microprice` 등 8종이 DEAD인 것도 전부 배포
    # 피처셋 밖이라 호라이즌 관점 표에는 한 줄도 안 뜬다. 이 절이 없으면 이 리포트는
    # 수동 `feature_health_report.py`보다 **덜 보는** 도구가 된다.
    L.append("### 2-b. 전체 `raw_features` 신규 이상 (배포·후보 밖 포함)")
    L.append("")
    sys_bad = sorted(n for n, h in health.items()
                     if h["level"] in (DEAD_LEVEL, CRIT_LEVEL)
                     and n not in KNOWN and not is_benign_flag(n))
    if sys_bad:
        deployed_by_feature = defaultdict(list)
        for hz in hz_list:
            for n in ((deployed.get(hz) or {}).get("names") or []):
                deployed_by_feature[n].append(hz)
        L.append("| 등급 | 피처 | zero% | 최빈비중 | 소재 |")
        L.append("|---|---|---|---|---|")
        for n in sys_bad:
            h = health[n]
            if deployed_by_feature.get(n):
                where = "배포: %s" % ", ".join(deployed_by_feature[n])
            elif sources.get(n):
                where = "후보: %s" % ", ".join(sources[n])
            else:
                where = "계측만 (배포·후보 아님)"
            L.append("| %s | `%s` | %s | %s | %s |"
                     % (h["level"], n, _fmt_pct(h.get("zero_rate")),
                        _fmt_pct(h.get("mode_rate")), where))
        L.append("")
        L.append("> `계측만`인 피처가 죽어 있어도 지금 당장 모델을 해치지는 않는다. "
                 "다만 **나중에 후보로 승격시킬 때 이미 죽어 있는 상태**라 표준절차 "
                 "Phase 2에서 반드시 걸린다 — 그때 고치는 것보다 지금 아는 편이 싸다.")
    else:
        L.append("없음 — 원인 미규명 DEAD/CRITICAL 피처가 전체 %d개 중 0개."
                 % len(health))
    metrics["system_bad"] = sys_bad
    L.append("")

    # ── §2-c 시간축 형태 이상 ─────────────────────────────────
    # 왜 따로 보나: §1~§2-b는 전부 **값의 분포**(zero·최빈)만 본다. 그래서 "날마다
    # 값은 다른데 하루 안에서는 상수"인 계열을 구조적으로 못 잡는다. 2026-08-25
    # 교차 실측(라이브 31일·86피처): L0 OK인데 시간축 부적격 **27개**, 역방향 **0개** —
    # 즉 시간축 판정은 값 분포 판정의 상위집합이다. `opt_chain_pcr`(30m CORE)은
    # 최빈비중 0.7%로 완전 정상인데 갱신 주기가 10분인 계단형이었다.
    L.append("### 2-c. 시간축 형태 (값 분포로는 안 보이는 것)")
    L.append("")
    shapes = {}
    for n, st in (stamps or {}).items():
        v = vals.get(n) or []
        if len(v) < MIN_SAMPLES or len(st) != len(v):
            continue
        prof = temporal_profile_series(v, [s[0] for s in st], [s[1] for s in st])
        if prof.get("shape"):
            shapes[n] = prof
    # 필터는 §2-b와 같은 원칙 — KNOWN·상태플래그·DEAD는 뺀다(경보 피로 방지).
    shaped = sorted(n for n, p in shapes.items()
                    if n not in KNOWN and not is_benign_flag(n)
                    and (health.get(n) or {}).get("level") != DEAD_LEVEL)
    if shaped:
        deployed_by_feature2 = defaultdict(list)
        for hz in hz_list:
            for n in ((deployed.get(hz) or {}).get("names") or []):
                deployed_by_feature2[n].append(hz)
        L.append("| 형태 | 피처 | 동률% | ACF1 | 변화간격 | 소재 |")
        L.append("|---|---|---|---|---|---|")
        for n in sorted(shaped, key=lambda x: (shapes[x]["shape"], x)):
            p = shapes[n]
            if deployed_by_feature2.get(n):
                where = "**배포: %s**" % ", ".join(deployed_by_feature2[n])
            elif sources.get(n):
                where = "후보: %s" % ", ".join(sources[n])
            else:
                where = "계측만"
            L.append("| %s | `%s` | %s | %s | %s | %s |"
                     % (p["shape"], n,
                        _fmt_pct(p.get("tie_rate")),
                        ("%.4f" % p["acf1"]) if p.get("acf1") is not None else "—",
                        ("%.1f분" % p["change_gap"]) if p.get("change_gap") is not None else "—",
                        where))
        L.append("")
        L.append("> 이 표는 **등급을 바꾸지 않는다.** 값 분포는 정상이므로 §1·§2에서는 "
                 "OK로 뜬다. 다만 이 피처들에 수명·decay·자기상관 지표를 매기면 "
                 "'기억 길이'가 아니라 다른 양(갱신 주기·추세 기울기·상수성)을 재게 된다.")
        L.append("> 판정 기준: 상수형=동률≥95%% · 계단형=변화간격≥%.0f분 · "
                 "누적형=ACF1≥%.2f · 결정론형=시각의 함수. "
                 "정본 분류·처분은 26주 재검증(`docs/Spec for feature/"
                 "피처_재검증_및_호라이즌배정_원칙.md` §2)에서 한다."
                 % (SHAPE_GAP_STEP, SHAPE_ACF1_INTEG))
    else:
        L.append("없음 — 시간축 형태 이상 0개.")
    metrics["shape_flagged"] = {n: shapes[n]["shape"] for n in shaped}
    L.append("")

    # ── §3 L4 conf-층화 ──────────────────────────────────────
    L.append("## 3. L4 — confidence 층화 검정 요약")
    L.append("")
    l4 = load_l4()
    if l4 is None:
        L.append("⚠ **미배선** — `%s`가 없다. 이 절은 "
                 "`scripts/horizon_conf_stratified_test.py`(07-30 실행계획 1단계 "
                 "신설 대상)가 그 경로에 JSON을 쓰면 자동으로 채워진다. "
                 "**빈칸이 '이상 없음'을 뜻하지 않는다.**"
                 % os.path.relpath(L4_JSON, ROOT).replace("\\", "/"))
        metrics["l4"] = {"status": "미배선"}
    elif "_error" in l4:
        L.append("⚠ 산출물 파싱 실패: %s" % l4["_error"])
        metrics["l4"] = {"status": "파싱실패", "error": l4["_error"]}
        warnings.append("L4 산출물 파싱 실패: %s" % l4["_error"])
    else:
        gen = l4.get("generated") or "?"
        L.append("출처: `%s` (생성 %s, 창 %s일)"
                 % (os.path.relpath(L4_JSON, ROOT).replace("\\", "/"),
                    gen, l4.get("days", "?")))
        L.append("")
        L.append("| 호라이즌 | conf<0.55 acc(n) | conf≥0.55 acc(n) | z | p | 판정 |")
        L.append("|---|---|---|---|---|---|")
        for hz, r in sorted((l4.get("horizons") or {}).items()):
            def _f(x, fmt="%.4f"):
                return "—" if x is None else (fmt % x)
            L.append("| %s | %s (%s) | %s (%s) | %s | %s | %s |"
                     % (hz, _f(r.get("acc_low"), "%.3f"), r.get("n_low", "—"),
                        _f(r.get("acc_high"), "%.3f"), r.get("n_high", "—"),
                        _f(r.get("z"), "%.2f"), _f(r.get("p")),
                        r.get("verdict", "—")))
        metrics["l4"] = l4
    L.append("")

    # ── §4 후보 파이프라인 현황판 ─────────────────────────────
    L.append("## 4. 후보 파이프라인 현황판")
    L.append("")
    deployed_all = set()
    for hz in hz_list:
        for n in (deployed.get(hz) or {}).get("names") or []:
            deployed_all.add(n)

    cand_rows = []
    stock = 0
    for name in sorted(sources):
        if name in deployed_all:
            continue                     # 이미 현역 — 후보가 아니다
        ndays = len(presence.get(name) or ())
        dec = decisions.get(name) if isinstance(decisions, dict) else None
        lvl = (health.get(name) or {}).get("level", MISSING_LEVEL)
        if ndays <= 0:
            status = "⚠ 미배선(축적 0)"
        elif ndays >= POOL_READY_DAYS:
            status = "검증가능 (%d일)" % ndays
        else:
            status = "축적중 %d/%d일" % (ndays, POOL_READY_DAYS)

        # 📌는 두 가지로 갈린다. suppress=True는 재론이 끝난 것이라 파이프라인 상태를
        # 덮어쓰고 재고에서 뺀다. suppress=False는 "진행 중인 상태"에 대한 기록이므로
        # 마커만 덧붙이고 재고에는 그대로 남긴다 — 빼면 오히려 추적이 끊긴다.
        if dec and dec.get("suppress"):
            status = "📌 %s" % (dec.get("decision") or "결정됨")
        else:
            if ndays > 0:
                stock += 1
            if dec:
                status = "%s · 📌 %s" % (status, dec.get("decision") or "기록됨")
        cand_rows.append((name, ", ".join(sources[name]), ndays, lvl, status))

    if cand_rows:
        L.append("| 후보 | 출처 | 축적(최근 %d거래일) | 건강 | 상태 |" % pool_days)
        L.append("|---|---|---|---|---|")
        for nm, src, nd, lvl, st in cand_rows:
            L.append("| `%s` | %s | %d일 | %s | %s |" % (nm, src, nd, lvl, st))
    else:
        L.append("(후보 없음 — POOL/pending이 전부 배포 피처셋에 포함돼 있다)")
    L.append("")
    L.append("- **살아있는 재고**: %d건 (축적중+검증가능 — `⚠ 미배선`과 §5에서 "
             "`재고=제외`로 확정된 것은 뺀다)" % stock)
    if stock < CANDIDATE_STOCK_MIN:
        L.append("- 🔍 **발굴 세션 권고** — 재고 %d < %d. `docs/Spec for feature/"
                 "피처_발굴_표준절차.md` Phase 0으로 신규 후보를 확보할 것 "
                 "(구현계획 §5-2 재고 트리거)." % (stock, CANDIDATE_STOCK_MIN))
    else:
        L.append("- 재고 충분 — 발굴 세션 권고 없음 (트리거 기준 %d건)"
                 % CANDIDATE_STOCK_MIN)
    L.append("")
    L.append("> `⚠ 미배선`은 명부에만 있고 계산 모듈이 없거나 배선이 끊겨 "
             "`raw_features`에 값이 전혀 쌓이지 않는 후보다 — 표준절차 Phase 1을 "
             "밟지 않은 상태이므로 검증 단계로 올라갈 수 없다 "
             "(예: `cancel_ratio`는 계좌등급 제한으로 **구현불가 확정**).  ")
    L.append("> `검증가능`은 L1' 월간 스크리닝(`ic_probe_pending_features.py`) 표본 "
             "요건(%d거래일)을 채웠다는 뜻일 뿐, 채택 근거가 아니다." % POOL_READY_DAYS)
    L.append("")
    metrics["candidates"] = [
        {"name": nm, "sources": src, "days": nd, "health": lvl, "status": st}
        for nm, src, nd, lvl, st in cand_rows
    ]
    metrics["candidate_stock"] = stock

    # ── §5 확정 결정 레지스트리 ───────────────────────────────
    L.append("## 5. 확정 결정 레지스트리 (📌)")
    L.append("")
    if decisions:
        L.append("출처: `config/settings.py:FEATURE_SET_DECISIONS` (%d건)" % len(decisions))
        L.append("")
        L.append("| 피처 | 결정 | 일자 | 재고 | 재검토 |")
        L.append("|---|---|---|---|---|")
        for nm in sorted(decisions):
            d = decisions[nm] or {}
            L.append("| `%s` | %s | %s | %s | %s |"
                     % (nm, d.get("decision", "?"), d.get("date", "—"),
                        "제외" if d.get("suppress") else "유지",
                        d.get("re_eval") or "재검정 금지"))
        L.append("")
        # 같은 사유를 공유하는 항목(예: exhaustion 4종)은 묶어서 한 번만 쓴다 —
        # 동일 문단이 네 번 반복되면 읽는 사람이 그 절을 건너뛰게 된다.
        by_note = {}
        for nm in sorted(decisions):
            d = decisions[nm] or {}
            by_note.setdefault(
                (d.get("note", "(사유 미기재)"), d.get("source") or ""), []
            ).append(nm)
        for (note, src), names in sorted(by_note.items(), key=lambda kv: kv[1][0]):
            L.append("- **%s** — %s  "
                     % (", ".join("`%s`" % n for n in names), note))
            L.append("  근거: %s" % (src or "⚠ 근거 미기재"))
        L.append("")
        L.append("> `재고=제외`(suppress)만 §4 살아있는 재고에서 빠진다. `유지`는 마커만 "
                 "붙고 재고에 그대로 남는다 — 보류·조건부채택처럼 **진행 중인 상태**를 "
                 "재고에서 빼면 추적이 끊기기 때문이다.  ")
        L.append("> **판정(매주 재계산)과 결정(사람이 확정)은 별개다** — 리포트가 같은 "
                 "수치를 다시 찍는 것은 미조치가 아니다(`CLAUDE.md` 검증 캠페인 운영 모드).")

        # 이름 오타 검출 — 레지스트리 키가 아무 데도 매칭되지 않으면 그 항목은 조용히
        # 아무 일도 하지 않는다. suppress=True 오타는 "기각했다고 믿었는데 후보로
        # 계속 살아있는" 최악의 실패라 반드시 눈에 띄어야 한다.
        known_names = set(health) | deployed_all | set(sources)
        orphans = sorted(n for n in decisions if n not in known_names)
        if orphans:
            L.append("")
            L.append("⚠ **레지스트리 이름 불일치 %d건** — `%s`. 배포 피처·후보 명부·"
                     "`raw_features` 어디에도 없는 이름이라 이 항목들은 아무 효과가 "
                     "없다. 오타이거나 이미 사라진 피처다."
                     % (len(orphans), "`, `".join(orphans)))
        metrics["decision_orphans"] = orphans
    else:
        L.append("(등록된 확정 결정 없음 — `config/settings.py:FEATURE_SET_DECISIONS`)")
    metrics["decisions"] = decisions
    L.append("")

    # ── 생성 경고 ────────────────────────────────────────────
    if warnings:
        L.append("## ⚠ 생성 경고")
        L.append("")
        for w in warnings:
            L.append("- %s" % w)
        L.append("")
    metrics["warnings"] = warnings

    L.append("---")
    L.append("")
    L.append("> 다음 단계: 이 리포트는 L0(건강)·L4(신뢰도) 관측이다. KEEP/DROP/ADD "
             "제안은 월간 리포트(구현계획 Phase C, L1·L2 필요)가 낸다. 어느 쪽도 "
             "피처셋을 바꾸지 않는다 — 변경은 L3 purged CV 통과 + 주간회의 승인 + "
             "EOD 재학습 반영 후 **pkl 직접 로드로 확인**하는 경로뿐이다.")

    return "\n".join(L), metrics


def main():
    ap = argparse.ArgumentParser(description="호라이즌별 피처셋 주간 건강 리포트")
    ap.add_argument("--days", type=int, default=20,
                    help="건강도 관찰창(거래일). 기본 20 — feature_health_report와 동일")
    ap.add_argument("--pool-days", type=int, default=60,
                    help="후보 축적 관찰창(거래일). 기본 60")
    ap.add_argument("--out-dir", default=None,
                    help="출력 폴더 오버라이드. 기본 docs/정기점검/금요일점검/<PC명>/ "
                         "— 지정 시 FIFO 보관정리는 하지 않는다")
    ap.add_argument("--keep", type=int, default=None,
                    help="FIFO 보관 주차 수. 기본 config/settings.py:"
                         "VALIDATION_REPORT_KEEP_WEEKS. 0 이하면 삭제 안 함")
    ap.add_argument("--no-prune", action="store_true",
                    help="이번 실행에서만 보관정리를 건너뛴다")
    ap.add_argument("--include-backfill", action="store_true",
                    help="[418차] 백필 생성 행(미시구조 0.0)을 관찰창에 포함한다. "
                         "기본은 제외 — 포함하면 §2-b zero%%·§4 축적일수가 왜곡된다.")
    ap.add_argument("--stdout", action="store_true",
                    help="리포트 본문을 콘솔에도 출력")
    args = ap.parse_args()

    if not os.path.exists(RAW_DB):
        print("raw_data.db 없음: %s" % RAW_DB, file=sys.stderr)
        return 1

    keep = args.keep
    if keep is None:
        try:
            from config.settings import VALIDATION_REPORT_KEEP_WEEKS
            keep = VALIDATION_REPORT_KEEP_WEEKS
        except Exception:
            keep = 4

    report_md, metrics = build_report(args.days, args.pool_days,
                                      args.include_backfill)

    pc_name = _pc_dir_name()
    if args.out_dir:
        out_dir = os.path.abspath(args.out_dir)
    else:
        out_dir = os.path.join(ROOT, "docs", "정기점검", "금요일점검", pc_name)
    os.makedirs(out_dir, exist_ok=True)
    stamp = datetime.date.today().strftime("%Y%m%d")
    md_path = os.path.join(out_dir, "%s_report_%s.md" % (REPORT_STEM, stamp))
    json_path = os.path.join(out_dir, "%s_metrics_%s.json" % (REPORT_STEM, stamp))
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report_md)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2, default=str)

    if args.stdout:
        print(report_md)
    # EOD 로그에서 바로 찾아갈 수 있도록 경로와 한 줄 요약을 남긴다(407차 패턴).
    n_bad = len(metrics.get("unknown_bad") or [])
    n_sys = len(metrics.get("system_bad") or [])
    print("저장: %s / %s" % (md_path, json_path))
    print("요약: 배포피처 실이상 %d건 | 전체 raw 신규이상 %d건 | 후보재고 %d건 | L4 %s"
          % (n_bad, n_sys, metrics.get("candidate_stock", 0),
             (metrics.get("l4") or {}).get("status", "연결됨")))

    # 쓰기가 끝난 뒤에만 FIFO — 중간에 죽어도 이번 주 파일은 이미 디스크에 있다.
    if args.out_dir:
        if keep and keep > 0:
            print("보관정리: --out-dir 사용 중이라 건너뜀")
    elif args.no_prune:
        print("보관정리: --no-prune")
    else:
        try:
            from scripts.campaign_report_paths import prune
            removed = prune(pc_name, keep, stem=REPORT_STEM)
            if removed:
                print("보관정리: %d주 초과분 %d개 삭제 — %s"
                      % (keep, len(removed),
                         ", ".join(os.path.basename(p) for p in removed)))
            elif keep and keep > 0:
                print("보관정리: 삭제 대상 없음 (보관 %d주)" % keep)
        except Exception as e:
            print("[경고] 보관정리 실패(무해, 다음 주 재시도): %s" % e, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
