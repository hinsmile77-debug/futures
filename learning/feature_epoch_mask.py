# -*- coding: utf-8 -*-
"""[MW0601 559차 / P1-6 · P1'-1] 학습 표본의 **세대·측정 여부** 마스크.

두 가지 서로 다른 「이 행을 학습에 써도 되는가」를 한곳에서 답한다.

1. **세대(epoch)** — 피처의 정의가 바뀐 경계 이전 행.
   `cvd_*` 는 체결 방향 분류가 바뀌면(`CVD_FLOW_SOURCE_MODE`) 그 이전 행과 **다른 양**이
   된다. 섞어서 학습하면 train/serve skew 다. 섀도 계측 개시일(`CVD_SHADOW_EPOCH`,
   2026-08-10) 이전에는 올바른 값이 아예 없으므로 백필도 불가하다.

2. **측정 여부(measured)** — 값은 있는데 관측이 아닌 행.
   수급 3종은 프리장·조회실패 때 이월 폴백 0.0 이 실린다. 스케일러가 그 0 을 분포로
   학습하면 실측값이 이상치로 밀린다(481차 F-1). `<key>_measured` 플래그로 가른다.

🔴 **기본은 관측 전용이다.**
`report_*` 함수는 항상 호출해도 안전하다 — 세지만 바꾸지 않는다. 실제 제외는
`config/settings.py` 의 두 플래그가 True 일 때만 일어나며, 둘 다 기본 False 다.

    FEATURE_EPOCH_MASK_ENABLED                  = False   # 1번
    INVESTOR_UNMEASURED_SCALER_EXCLUDE_ENABLED  = False   # 2번

⚠ 1번을 켜면 학습 표본이 급감한다(26주 창 → 섀도 개시 이후만). 그 손실이 편향 학습보다
  나은지는 **Phase 3 승인 사항**이며, 판단 근거는 `report_epoch_loss()` 가 매 EOD 로그에
  남기는 실측 비율이다. 지금 그 숫자를 쌓는 것이 이 모듈의 첫 임무다.
"""
from __future__ import print_function

import logging

logger = logging.getLogger(__name__)

# 세대 경계를 갖는 피처군. 값은 (설정키, 기본 경계일).
# `cvd_*` 는 **전환 모드가 legacy 가 아닐 때만** 경계가 생긴다 — legacy 로 계속 가면
# 과거 전 구간이 일관되게 편향돼 있어 세대 분리가 오히려 표본만 깎는다.
_CVD_PREFIXES = ("cvd", "cvd_norm", "cvd_slope", "cvd_direction", "cvd_divergence",
                 "cvd_delta_norm", "cvd_exhaustion", "cvd_monotone_ratio",
                 "cvd_slope_norm", "kyle_lambda", "vpin")

INVESTOR_MEASURED_PAIRS = (
    ("foreign_futures_net", "foreign_futures_net_measured"),
    ("retail_futures_net", "retail_futures_net_measured"),
    ("institution_futures_net", "institution_futures_net_measured"),
)


def _settings():
    try:
        from config import settings as _s
        return _s
    except Exception:                                   # 테스트 격리 실행
        return None


def cvd_flow_mode():
    s = _settings()
    return str(getattr(s, "CVD_FLOW_SOURCE_MODE", "legacy") or "legacy").lower()


def cvd_shadow_epoch():
    s = _settings()
    return str(getattr(s, "CVD_SHADOW_EPOCH", "2026-08-10") or "2026-08-10")


def epoch_gated_features(feature_names, mode=None):
    """세대 경계가 걸리는 피처명 목록. legacy 모드면 **빈 목록**이다."""
    mode = mode or cvd_flow_mode()
    if mode == "legacy":
        return []
    return [f for f in feature_names
            if any(f == p or f.startswith(p + "_") for p in _CVD_PREFIXES)]


def epoch_row_mask(ts_list, epoch=None):
    """경계일 **이상**인 행만 True. ts 는 'YYYY-MM-DD...' 로 시작하면 된다."""
    epoch = epoch or cvd_shadow_epoch()
    return [str(t)[:10] >= epoch for t in ts_list]


def report_epoch_loss(ts_list, feature_names, tag=""):
    """세대 분리를 켰을 때 **잃게 될 행 비율**을 재서 로그로 남긴다(변경 없음).

    Returns: dict — 판정에 쓰지 말 것. 관측치다.
    """
    mode = cvd_flow_mode()
    gated = epoch_gated_features(feature_names, mode)
    keep = epoch_row_mask(ts_list)
    n = len(ts_list)
    kept = sum(1 for k in keep if k)
    rep = {"mode": mode, "epoch": cvd_shadow_epoch(), "gated_features": len(gated),
           "rows": n, "rows_after_epoch": kept,
           "loss_ratio": round(1.0 - (kept / float(n or 1)), 4)}
    logger.info(
        "[FeatureEpoch]%s mode=%s epoch=%s 세대경계 피처 %d개 · 경계이후 %d/%d행"
        " (분리 시 손실 %.1f%%) — 관측만, 적용 안 함",
        (" " + tag) if tag else "", rep["mode"], rep["epoch"], rep["gated_features"],
        kept, n, rep["loss_ratio"] * 100.0)
    return rep


def report_unmeasured(feature_dicts, tag=""):
    """수급 3종의 **미측정 행 수**를 센다(변경 없음).

    `<key>_measured` 키가 아예 없는 행은 `unknown` 으로 따로 센다 — 559차 이전 행이다.
    「미측정 0건」과 「플래그 자체가 없음」을 같은 칸에 넣지 않는다(계측 4원칙 ②).
    """
    rep = {}
    for key, flag in INVESTOR_MEASURED_PAIRS:
        unknown = sum(1 for d in feature_dicts if flag not in d)
        unmeas = sum(1 for d in feature_dicts
                     if flag in d and not float(d.get(flag) or 0.0))
        rep[key] = {"rows": len(feature_dicts), "unmeasured": unmeas, "flag_absent": unknown}
    logger.info(
        "[InvestorMeasured]%s %s",
        (" " + tag) if tag else "",
        " · ".join("%s 미측정 %d / 플래그없음 %d"
                   % (k.replace("_futures_net", ""), v["unmeasured"], v["flag_absent"])
                   for k, v in rep.items()))
    return rep


def apply_epoch_window(ts_list, feature_names, enabled=None):
    """세대 분리를 **실제로** 적용할 때 남길 행 인덱스.

    Returns: (kept_index_list, applied_bool). 비활성이면 전 행을 그대로 돌려준다.
    """
    if enabled is None:
        s = _settings()
        enabled = bool(getattr(s, "FEATURE_EPOCH_MASK_ENABLED", False))
    if not enabled or not epoch_gated_features(feature_names):
        return list(range(len(ts_list))), False
    keep = epoch_row_mask(ts_list)
    idx = [i for i, k in enumerate(keep) if k]
    logger.warning(
        "[FeatureEpoch] 세대 분리 **적용** — %d행 → %d행. 표본이 줄어든 것은 결함이 아니다.",
        len(ts_list), len(idx))
    return idx, True


def unmeasured_scaler_rows(feature_dicts, enabled=None):
    """스케일러 fit 에서 뺄 행 인덱스(수급 미측정). 비활성이면 빈 목록."""
    if enabled is None:
        s = _settings()
        enabled = bool(getattr(s, "INVESTOR_UNMEASURED_SCALER_EXCLUDE_ENABLED", False))
    if not enabled:
        return []
    drop = []
    for i, d in enumerate(feature_dicts):
        for _key, flag in INVESTOR_MEASURED_PAIRS:
            if flag in d and not float(d.get(flag) or 0.0):
                drop.append(i)
                break
    if drop:
        logger.warning("[ScalerRefresh] 수급 미측정 제외 %d행 (전체 %d)",
                       len(drop), len(feature_dicts))
    return drop

# ── [MW0601 559차 / P1'-3] 418차 백필 오염행 제외 ────────────────────────────
# 2026-07-13 에 `backfill_features.py --update-features` 가 `--from` 없이 실행돼
# 라이브 25거래일(9,002행)의 features JSON 이 통째로 0.0 으로 덮였다. 그 행들은
# OHLCV 파생만 실값이고 호가·수급·옵션·매크로가 전부 0.0 이라, 학습에 넣으면
# **"값 없음"이 아니라 "0 이라는 잘못된 정보"** 를 가르친다.
#
# 418차 결정 1 = 「복구 불가 25거래일은 raw_features 소비처에서 제외한다」.
# 🔴 그런데 559차 실측상 그 제외는 **섀도 TB 폴백 한 곳에만** 걸려 있었다.
#    26주 창을 쓰는 Phase 1 학습 로더와 분위 회귀 폴백은 그대로 먹고 있었다
#    (오염 구간이 26주 창 안에 있다). 계측 4원칙 ⑤ — 대사는 모든 축을 걸어라.
BACKFILL_QUALITY_MARKER = 0.3


def is_live_row(features_json, json_mod=None):
    """features JSON 이 라이브 수집 행이면 True (백필 생성 행이면 False).

    파싱 실패는 True — 어차피 뒤 파싱 루프가 거른다. 여기서 제외 사유를 흐리지 않는다.
    """
    if json_mod is None:
        import json as json_mod
    try:
        return json_mod.loads(features_json).get(
            "feature_quality_score") != BACKFILL_QUALITY_MARKER
    except (ValueError, TypeError):
        return True


def filter_backfill_rows(rows, key="features", json_mod=None, tag=""):
    """(ts, features) 행 목록에서 백필 오염행을 뺀다. **뺀 개수를 반드시 남긴다**.

    `rows` 원소는 sqlite3.Row / dict / 튜플 모두 받는다.
    """
    if json_mod is None:
        import json as json_mod

    def _feat(r):
        try:
            return r[key]
        except (TypeError, KeyError, IndexError):
            return r[1]

    kept = [r for r in rows if is_live_row(_feat(r), json_mod)]
    dropped = len(rows) - len(kept)
    if dropped:
        logger.warning(
            "[BackfillFilter]%s 백필 오염행 %d/%d 제외 (418차 결정 1) — 남은 %d행",
            (" " + tag) if tag else "", dropped, len(rows), len(kept))
    return kept

# ── [MW0601 559차 / P1'-2] 압축 이전 단위 거래일 제외 ────────────────────────
# 418차 복구 때 압축 도입(124차, 2026-06-08) **이전 백업**에서 되살린 4거래일은
# 수급 8키가 **계약수 원단위**로 들어 있다. 라이브 압축값은 |v| <= 2.6 인데 이 행들은
# |v| 최대 5.4e+05 다.
#
# 🔴 이건 「보기 흉한 이상치」가 아니라 **피처를 죽인다.** 실측(2026-09-13,
#    26주 창 · `raw_features_horizon`):
#      · 3m  정상 13,081행 std=0.884  →  4일 487행 섞으면 std=5.0e+04 (**56,760배**)
#      · 15m 정상  2,552행 std=0.883  →  4일  96행 섞으면 std=5.0e+04 (**57,117배**)
#    StandardScaler 가 그 std 로 나누므로 **진짜 라이브 값이 전부 0 근방으로 짓눌린다**.
#    `apply_robust_preprocess` 는 spread_ticks·mlofi_slope 만 clip 하므로 막아주지 않는다.
#
# 그래서 418차 결정 1(「잘못된 값은 제외한다」)과 같은 취급으로 **행 자체를 뺀다**.
# 컬럼만 비우면 `X_hz` 구성이 `.get(f, 0.0)` 이라 0 으로 채워져 같은 함정에 빠진다.
# 4일 / 114거래일이라 표본 비용은 3.5% 다.
INVESTOR_UNIT_MISMATCH_DAYS = frozenset((
    "2026-06-02", "2026-06-04", "2026-06-05", "2026-06-08",
))


def filter_unit_mismatch_rows(rows, ts_getter=None, tag="", enabled=None):
    """압축 이전 단위 거래일 행을 뺀다. 뺀 개수를 반드시 남긴다(계측 4원칙 ③).

    `rows` 원소에서 ts 를 꺼내는 방법이 자료구조마다 달라 `ts_getter` 로 받는다.
    기본은 `r["ts"]` → 실패 시 `r[0]`.
    """
    if enabled is None:
        s = _settings()
        enabled = bool(getattr(s, "INVESTOR_UNIT_MISMATCH_EXCLUDE_ENABLED", True))
    if not enabled:
        return rows

    def _ts(r):
        if ts_getter is not None:
            return ts_getter(r)
        try:
            return r["ts"]
        except (TypeError, KeyError, IndexError):
            return r[0]

    kept = [r for r in rows if str(_ts(r))[:10] not in INVESTOR_UNIT_MISMATCH_DAYS]
    dropped = len(rows) - len(kept)
    if dropped:
        logger.warning(
            "[UnitMismatch]%s 압축 이전 단위 거래일 %d/%d행 제외 (559차 P1'-2) — 남은 %d행."
            " 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다.",
            (" " + tag) if tag else "", dropped, len(rows), len(kept))
    return kept
