# scripts/backfill_features.py — 과거 캔들 → raw_features 소급 생성
"""
raw_candles에는 2025-08-19부터 데이터가 있지만
raw_features는 미륵이가 처음 기동된 2026-04-28부터만 존재한다.
이 스크립트는 OHLCV 기반으로 계산 가능한 피처를 소급 생성해
raw_features에 INSERT한다.

계산 가능 피처 (OHLCV only):
  atr, atr_ratio           — ATRCalculator
  vwap, vwap_position,
  above_vwap               — VWAPCalculator (일중 누적, 일자 바뀌면 reset)
  cvd_direction            — close > open → +1, 반대 → -1
  cvd_slope                — 최근 5봉 cvd_direction 합산
  avg_volume               — 최근 20봉 volume 이동평균
  hurst, hurst_ready       — calculate_hurst() (317차 3단계 워밍업 스케줄까지 실거래와
                              동일하게 재현, 최근 HURST_WINDOW_N봉 종가 버퍼)

불가 피처 (호가/수급/매크로/옵션 없음):
  ofi_*, microprice_*, mlofi_*, queue_*
  foreign_*, institution_*, retail_*
  macro_*, opt_*, toxicity_*
  → 모두 0.0 으로 채움 (batch_retrainer에서 rec.get(f, 0.0) 처리와 동일)

[317차] hurst 재보정 소급 반영 시 유의사항 — 이 스크립트의 hurst 재계산은 "GBM
재학습용 학습 피처를 새 공식으로 재구성"하는 것이지, "과거에 실제로 나갔던 진입/청산
신호를 다시 쓴다"는 뜻이 아니다. 실거래는 당시 배포돼 있던 파라미터(예: N=60/max_lag=20)
기준으로 이미 확정적으로 발생했고 trades.db·ensemble_decisions.db 등 실거래 기록은
그대로 유지된다. 이 스크립트가 건드리는 건 raw_features(재학습 입력)뿐이다.
  - 콜드스타트/워밍업 재현: 라이브(feature_builder.py)와 동일한 317차 3단계 스케줄
    (n<HURST_WARMUP_COLDSTART_MIN 중립 / 적응형 max_lag / n>=HURST_WINDOW_N 고정)을
    `process_day()`에서 그대로 재현한다 — 이걸 빠뜨리면(예: 항상 고정 max_lag만 사용)
    라이브 파이프라인과 값이 달라져 소급 데이터 자체가 새로운 불일치 원인이 된다.
  - 일자 경계 리셋: `process_day()`가 날짜별로 `close_buf`를 새로 생성하므로
    `feature_builder.reset_daily()` 수정분(317차, `_close_history.clear()` 추가)과
    동등한 효과가 이미 구조적으로 보장된다(전날 데이터가 섞이는 오염 불가) — 별도
    조치 불필요, 최초 설계부터 그렇게 돼 있었음.
  - [318차 수정] `hurst_ready`가 `FEATURE_KEYS_ALL`에 없어 이 스크립트가 재계산하는
    모든 행에서 키 자체가 통째로 빠지는 문제를 발견 — `_Z_WARN_EXEMPT` 등록은 스케일러
    z-경보 노이즈 제거용일 뿐 실제 학습 피처 편입과 무관했음(재조사 결과 GBM
    `feature_names.pkl`·`shap_feature_registry.json` 어디에도 `hurst_ready`가 없었음,
    즉 "0.0 기본값"이 아니라 애초에 학습 후보에도 오른 적이 없었던 상태). `FEATURE_KEYS_ALL`에
    추가하고 `hurst`와 동일한 3단계 워밍업 산식으로 `feat["hurst_ready"]`를 채우도록 수정.
    학습 피처 편입 자체는 `config/constants.py:DYNAMIC_FEATURES_POOL` 등록 + 주간 SHAP
    심사·수동 승인(`main.py:_on_apply_shap_candidate_requested`)을 거쳐야 하며 이 스크립트
    수정만으로 자동 편입되지 않는다.

[418차] `--update-features` 안전장치 3종 — 2026-07-13 사고 재발 방지
  MW0601에서 `--from` 없는 `--update-features` 전체 실행이 라이브 29거래일
  10,448행의 features JSON을 통째로 교체해, 실제 수집됐던 호가·수급·옵션·매크로
  값을 0.0으로 소실시켰다(9,002행 복구 불가). 원래 의도는 hurst 재계산 하나뿐이었다.
  근거: `dev_memory/DECISION_LOG.md` 2026-08-02 MW0601 418차.

  ① 라이브 행 포함일 스캔 — 대상에 라이브 수집 행이 섞이면 날짜별 건수를 출력하고
     **중단**한다. 강행하려면 `--force-overwrite-live` 명시.
  ② 병합 갱신 — UPDATE가 features JSON을 통째 교체하지 않고 `_BACKFILL_COMPUTED_KEYS`
     (백필이 실제로 계산하는 키)만 덮어쓴다. 라이브 수집분은 보존된다.
  ③ 자동 백업 — UPDATE 실행 전 DB 스냅샷을 뜬다(`--no-backup`으로 생략 가능).

사용법:
  python scripts/backfill_features.py             # 전체 소급 (INSERT — 안전)
  python scripts/backfill_features.py --dry-run   # 건수만 확인
  python scripts/backfill_features.py --from 2026-01-01  # 특정 날짜 이후만
  python scripts/backfill_features.py --update-features --from 2026-04-28
      # 317차 hurst 재보정 반영 — 기존 raw_features 행을 새 공식으로 재계산해 병합 UPDATE
      # ※ 라이브 행이 섞인 날이 있으면 중단된다. 목록을 확인한 뒤 판단할 것.

Python 3.7 32-bit 호환
"""
import argparse
import datetime
import json
import logging
import math
import os
import sys
from collections import deque

# 프로젝트 루트를 sys.path에 추가
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import sqlite3

from features.technical.atr import ATRCalculator
from features.technical.vwap import VWAPCalculator
from features.technical.volume_profile import VolumeProfileCalculator
from features.technical.hurst_exponent import calculate_hurst
from config.settings import (
    HURST_WINDOW_N, HURST_MAX_LAG,
    HURST_WARMUP_COLDSTART_MIN, HURST_WARMUP_LAG_FLOOR, HURST_WARMUP_LAG_RATIO,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("backfill")

RAW_DATA_DB = os.path.join(BASE_DIR, "data", "db", "raw_data.db")

# 현재 raw_features에서 사용 중인 키 목록 (417차: 라이브 미기록 9종 제거 → 107개.
# 318차 "116개"는 그 시점 실측치이며, hurst_ready 추가분은 그대로 유지)
# 계산 가능한 것 외에는 모두 0.0
#
# ── 동기화 규칙: **라이브가 한 번도 쓰지 않는 키는 넣지 않는다** ──────────────
# 이 목록이 낡으면 양방향으로 사고가 나고, 둘 다 실제로 발생했다.
#   ① 목록에만 있고 라이브에 없는 키 → 백필이 퇴역 피처를 0.0으로 되살린다.
#      `learning/batch_retrainer.py:_load_from_db`가 전 구간 키의 **합집합**으로
#      feat_names를 만들므로(318차), 백필 행이 학습창에 하나라도 들어오면 그 키가
#      상수 0.0 컬럼으로 학습 피처공간에 편입된다. 주간 건강 리포트
#      (`generate_featureset_health_report.py` §2-b)에도 유령 DEAD로 뜬다 —
#      2026-08-02 MW0601×MW0602 대조에서 MW0601에만 있던 §2-b 추가 4건
#      (bear_reversal_signal·macro_vix_abs·microprice·feature_recoverable_errors)이
#      전부 이 경로였음이 확인됐다(MW0602 라이브 구간에는 그 키가 아예 없음).
#   ② 라이브에 있는데 목록에 없는 키 → 백필 날짜에 그 키가 통째로 빠진다
#      (318차 hurst_ready 사고).
#
# ⚠ **②를 "라이브 키를 전부 0.0으로 추가"로 고치지 말 것.** 학습 쪽은 이득이 0이고
#   (위 합집합 + `rec.get(f, 0.0)`이라 키 부재 == 0.0), 건강 리포트 §4는 "키가 있으면
#   그날 관측됨"으로 후보 축적 일수를 세기 때문에 실제로 수집된 적 없는 날이 축적일로
#   잡혀 "20/20일 검증가능"이 거짓 판정이 된다. 라이브에만 있는 키(2026-08-02 기준
#   37종: opt_gex_sign·opt_chain_pcr·vkospi·kyle_lambda·vpin 등)를 편입하려면
#   **백필이 OHLCV로 진짜 계산할 수 있는 것만** 라이브와 동일한 산식으로 추가한다
#   (317차 train/serve skew 원칙 — 산식이 다르면 소급 데이터가 새 불일치 원인이 된다).
#
# 재점검 방법(피처 퇴역 직후·26주 WFA 주기): 최근 라이브 구간의 features JSON 키
#   합집합을 뽑아 이 목록과 대조해 **출현율 0%인 키만** 제거한다. 옵션체인·수급처럼
#   장중 갱신 주기 때문에 84~96%대인 키는 정상이므로 남긴다.
#
# [417차 제거 9종] 2026-06-18~07-31 라이브 10,746행 실측 출현율 전부 0.0%:
#   bear_reversal_signal                     — 191차 삭제(희소 이진 신호)
#   microprice / macro_vix_abs /
#   feature_recoverable_errors               — Phase 2-A~2-C 절대값·상수 피처 제거
#   macro_quality_age_sec / _available /
#   _fallback_used / _stale                  — macro_quality_source_code만 라이브 잔존
#   vwap                                     — 라이브 미기록. 백필만 실값을 써서
#       "백필 날짜에만 비영"인 컬럼이 되므로 오히려 train/serve skew를 만든다
#       (0.0 상수보다 나쁘다). feat["vwap"] 대입도 함께 제거했다.
FEATURE_KEYS_ALL = [
    "above_vwap", "atr", "atr_ratio", "avg_volume",
    "bear_exhaustion", "bear_exhaustion_signal",
    "bull_exhaustion", "bull_exhaustion_signal", "bull_reversal_signal",
    "cancel_add_ratio", "cvd", "cvd_direction", "cvd_divergence",
    "cvd_exhaustion", "cvd_exhaustion_signal", "cvd_monotone_ratio", "cvd_slope",
    "feature_degraded", "feature_quality_score",
    "foreign_call_net", "foreign_futures_net", "foreign_put_net",
    "foreign_retail_divergence",
    "hurst", "hurst_ready", "imbalance_slope", "institution_futures_net",
    "macro_event_flag", "macro_krw_chg", "macro_nasdaq_chg",
    "macro_quality_source_code",
    "macro_risk_off", "macro_risk_on",
    "macro_sp500_chg", "macro_us10y_chg", "macro_vix",
    "microprice_bias", "microprice_depth_bias", "microprice_slope",
    "mlofi_norm", "mlofi_pressure", "mlofi_slope",
    "ofi_imbalance", "ofi_norm", "ofi_pressure", "ofi_reversal_speed",
    "opt_available", "opt_pcr_bearish", "opt_pcr_bullish", "opt_pcr_extreme",
    "opt_pcr_extreme_bearish", "opt_pcr_extreme_bullish",
    "opt_pcr_extreme_signed", "opt_pcr_norm", "opt_pcr_slope_norm",
    "program_arb_net", "program_foreign_net_krw",
    "program_individual_net_krw", "program_institution_net_krw",
    "program_non_arb_net",
    "quality_investor_age_sec", "quality_investor_fetch_count",
    "quality_investor_futures_supported", "quality_investor_option_supported",
    "quality_investor_program_supported", "quality_investor_reason_code",
    "quality_investor_source_code", "quality_investor_stale",
    "quality_investor_supported",
    "quality_macro_age_sec", "quality_macro_available",
    "quality_macro_fallback_used", "quality_macro_stale",
    "quality_option_available", "quality_supply_available",
    "queue_depletion_speed", "queue_momentum", "queue_refill_rate",
    "queue_signal", "queue_signal_ma",
    "retail_futures_net", "spread_ticks",
    "toxicity_atr_stress", "toxicity_cancel_stress", "toxicity_flow_stress",
    "toxicity_queue_stress", "toxicity_regime_code", "toxicity_score",
    "toxicity_score_ma",
    "vwap_position",
    # 방향성 고도화 피처 (P2 — 2026-06-01 추가)
    "time_sin", "time_cos", "is_open_volatile", "is_close_volatile",
    "ret_1m", "ret_5m", "ret_15m",
    "ema_cross", "bb_position",
    "cvd_delta_norm",
    "poc_distance", "in_value_area", "va_bandwidth", "poc_above",
    # 개선 3 잔여 방향성 피처 (2026-06-01 추가)
    "volume_acceleration", "vwap_momentum", "prev_day_same_hour_ret",
]

# [418차] 백필이 **실제로 계산하는** 키 — `process_day()`가 명시적으로 대입하는 것만.
#
# FEATURE_KEYS_ALL과 구분해야 하는 이유가 이 스크립트가 낸 사고의 핵심이다.
# `process_day()`는 `{k: 0.0 for k in FEATURE_KEYS_ALL}`로 전 키를 0.0으로 깔고 시작하며,
# 그중 OHLCV로 계산 가능한 아래 키만 실값으로 채운다. 즉 FEATURE_KEYS_ALL의 나머지는
# "계산 결과 0.0"이 아니라 **"계산할 수단이 없어 0.0"** 이다. 병합 갱신에서 이 구분 없이
# feat 전체를 merge하면 라이브가 실제로 수집한 호가·수급·옵션·매크로 값이 그 0.0에
# 덮여 사라진다 — 2026-07-13 MW0601 사고와 똑같은 결과가 된다.
#
# `feature_quality_score`는 의도적으로 제외한다. 0.3은 "백필 생성 행" 마커이고,
# 라이브 행에 병합 갱신을 걸 때 이걸 덮으면 그 행이 백필 행으로 오인돼 손상 판별
# 자체가 불가능해진다(418차 조사가 이 마커에 전적으로 의존했다).
_BACKFILL_COMPUTED_KEYS = frozenset([
    "atr", "atr_ratio",
    "vwap_position", "above_vwap",
    "cvd_direction", "cvd_slope", "cvd_delta_norm",
    "avg_volume",
    "hurst", "hurst_ready",
    "time_sin", "time_cos", "is_open_volatile", "is_close_volatile",
    "ret_1m", "ret_5m", "ret_15m",
    "ema_cross", "bb_position",
    "poc_distance", "in_value_area", "va_bandwidth", "poc_above",
    "volume_acceleration", "vwap_momentum", "prev_day_same_hour_ret",
])

# 백필 생성 행 마커. 라이브(feature_builder.py:604)는 페널티 차감식이라 정확히 0.3이
# 나오려면 페널티 0.7이 필요한데 실측 0건 — 마커로 신뢰할 수 있다(418차 검증).
BACKFILL_QUALITY_MARKER = 0.3


def load_missing_dates(conn) -> list:
    """raw_candles에는 있지만 raw_features에 없는 날짜 목록 반환 (오름차순)"""
    c = conn.cursor()
    candle_days = set(
        r[0] for r in c.execute(
            "SELECT DISTINCT substr(ts,1,10) FROM raw_candles ORDER BY 1"
        ).fetchall()
    )
    feat_days = set(
        r[0] for r in c.execute(
            "SELECT DISTINCT substr(ts,1,10) FROM raw_features"
        ).fetchall()
    )
    return sorted(candle_days - feat_days)


def process_day(date_str: str, candles: list) -> list:
    """
    하루치 캔들 리스트 → raw_features 삽입용 (ts, features_dict) 리스트 반환

    [418차] 반환 타입이 features_json(str) → features_dict로 바뀌었다. 병합 갱신에서
    호출부가 키 단위로 골라 써야 하기 때문이다. 직렬화는 각 write 지점에서 한다.

    candles: [{'ts', 'open', 'high', 'low', 'close', 'volume'}, ...]  시간순
    """
    atr_calc  = ATRCalculator(period=14)
    vwap_calc = VWAPCalculator()
    vp_calc   = VolumeProfileCalculator(n=60, bins=20)

    close_buf    = deque(maxlen=HURST_WINDOW_N)   # hurst/볼린저/모멘텀용
    cvd_dir_buf  = deque(maxlen=5)    # cvd_slope용
    vol_buf      = deque(maxlen=20)   # avg_volume용
    vol_buf10    = deque(maxlen=10)   # volume_acceleration용
    vwap_buf10   = deque(maxlen=10)   # vwap_momentum용

    # EMA 상태
    ema5  = 0.0
    ema20 = 0.0
    ema_init = False

    rows = []
    for bar in candles:
        o  = float(bar["open"]   or 0)
        h  = float(bar["high"]   or 0)
        l  = float(bar["low"]    or 0)
        c  = float(bar["close"]  or 0)
        v  = float(bar["volume"] or 0)
        ts = bar["ts"]

        if c <= 0:
            continue

        # ── ATR ─────────────────────────────────────────────────
        atr_res = atr_calc.update(h, l, c)

        # ── VWAP ────────────────────────────────────────────────
        vwap_res = vwap_calc.update(h, l, c, v)

        # ── CVD 근사 ─────────────────────────────────────────────
        cvd_dir = 1.0 if c > o else (-1.0 if c < o else 0.0)
        cvd_dir_buf.append(cvd_dir)
        cvd_slope = float(sum(cvd_dir_buf))

        # ── avg_volume ───────────────────────────────────────────
        vol_buf.append(v)
        avg_vol = float(sum(vol_buf) / len(vol_buf)) if vol_buf else 0.0

        # ── Hurst ────────────────────────────────────────────────
        # 317차: feature_builder.py와 동일한 3단계 워밍업 스케줄까지 그대로 재현
        # (콜드스타트만 다르게 처리하면 라이브와 값이 어긋나 소급 데이터가 새로운
        # train/serve 불일치 원인이 됨). close_buf는 날짜마다 process_day() 호출 시
        # 새로 생성되므로(위 함수 시작부) reset_daily() 수정분과 동등하게 이미
        # 일자 경계에서 항상 비어 있다.
        close_buf.append(c)
        _n_buf = len(close_buf)
        if _n_buf < HURST_WARMUP_COLDSTART_MIN:
            hurst = 0.5
            hurst_ready = False
        else:
            if _n_buf < HURST_WINDOW_N:
                _lag_eff = max(HURST_WARMUP_LAG_FLOOR, round(_n_buf * HURST_WARMUP_LAG_RATIO))
            else:
                _lag_eff = HURST_MAX_LAG
            hurst = calculate_hurst(list(close_buf), max_lag=_lag_eff)
            hurst_ready = True

        # ── 시간대 피처 ─────────────────────────────────────────
        try:
            ts_dt  = datetime.datetime.strptime(ts[:19], "%Y-%m-%d %H:%M:%S")
            mkt    = ts_dt.replace(hour=9, minute=0, second=0, microsecond=0)
            mod    = max(0, min(389, int((ts_dt - mkt).total_seconds() / 60)))
            time_sin          = math.sin(2.0 * math.pi * mod / 390.0)
            time_cos          = math.cos(2.0 * math.pi * mod / 390.0)
            is_open_volatile  = 1.0 if mod < 30  else 0.0
            is_close_volatile = 1.0 if mod > 360 else 0.0
        except Exception:
            time_sin = 0.0; time_cos = 1.0
            is_open_volatile = 0.0; is_close_volatile = 0.0

        # ── 가격 모멘텀 ─────────────────────────────────────────
        _ch = list(close_buf)
        _n  = len(_ch)
        ret_1m  = (_ch[-1] - _ch[-2])  / (_ch[-2]  + 1e-9) if _n >= 2  else 0.0
        ret_5m  = (_ch[-1] - _ch[-6])  / (_ch[-6]  + 1e-9) if _n >= 6  else 0.0
        ret_15m = (_ch[-1] - _ch[-16]) / (_ch[-16] + 1e-9) if _n >= 16 else 0.0

        # ── EMA cross ─────────────────────────────────────────
        if not ema_init:
            ema5 = ema20 = c
            ema_init = True
        else:
            ema5  = ema5  * (1.0 - 2.0 / 6.0)  + c * (2.0 / 6.0)
            ema20 = ema20 * (1.0 - 2.0 / 21.0) + c * (2.0 / 21.0)
        ema_cross = 1.0 if ema5 > ema20 else -1.0

        # ── 볼린저 밴드 위치 ──────────────────────────────────
        if _n >= 20:
            _sma20 = sum(_ch[-20:]) / 20.0
            _std20 = math.sqrt(sum((x - _sma20) ** 2 for x in _ch[-20:]) / 20.0)
            bb_position = (c - (_sma20 - 2.0 * _std20)) / (4.0 * _std20 + 1e-9)
        else:
            bb_position = 0.5

        # ── CVD delta 고도화 (Bull/Bear Volume 분해) ─────────
        _rng_hilo   = max(h - l, 1e-9)
        _bull_v     = v * max(c - l, 0.0) / _rng_hilo
        _bear_v     = v * max(h - c, 0.0) / _rng_hilo
        cvd_delta_norm = (_bull_v - _bear_v) / (v + 1e-9)

        # ── Volume Profile ────────────────────────────────────
        vp = vp_calc.update(h, l, c, v)

        # ── 개선 3: 거래량 가속도 ─────────────────────────────
        vol_buf10.append(v)
        _vl10 = list(vol_buf10)
        _nv10 = len(_vl10)
        if _nv10 >= 6:
            _vol_r = sum(_vl10[-3:]) / 3.0
            _vol_p = sum(_vl10[-6:-3]) / 3.0
            volume_acceleration = (_vol_r - _vol_p) / (_vol_p + 1e-9)
        else:
            volume_acceleration = 0.0

        # ── 개선 3: VWAP 이동 속도 ───────────────────────────
        _vwap_now = float(vwap_res["vwap"])
        vwap_buf10.append(_vwap_now)
        _vb10 = list(vwap_buf10)
        vwap_momentum = (c - _vb10[-5]) / (_vb10[-5] + 1e-9) if len(_vb10) >= 5 else 0.0

        # ── 개선 3: 전일 동시간대 수익률 (소급 — 전날 동일봉 찾기) ──
        # 소급 데이터는 일중 단위로 처리되므로 전일 데이터 접근 불가 → 0.0 고정
        prev_day_same_hour_ret = 0.0

        # ── 피처 딕셔너리 구성 ────────────────────────────────────
        feat: dict = {k: 0.0 for k in FEATURE_KEYS_ALL}
        feat["atr"]           = float(atr_res["atr"])
        feat["atr_ratio"]     = float(atr_res["atr_ratio"])
        # feat["vwap"]는 417차에 제거 — 라이브가 vwap 절대값을 기록하지 않아
        # 백필 날짜에만 비영인 컬럼이 됐다(위 FEATURE_KEYS_ALL 주석 참조).
        # vwap_res는 vwap_position/above_vwap/vwap_momentum 계산에 계속 쓴다.
        feat["vwap_position"] = float(vwap_res["position"])
        feat["above_vwap"]    = 1.0 if vwap_res["above_vwap"] else 0.0
        feat["cvd_direction"] = cvd_dir
        feat["cvd_slope"]     = cvd_slope
        feat["avg_volume"]    = round(avg_vol, 2)
        feat["hurst"]         = hurst
        feat["hurst_ready"]   = hurst_ready
        feat["feature_quality_score"] = BACKFILL_QUALITY_MARKER  # 소급 데이터 마커

        feat["time_sin"]          = time_sin
        feat["time_cos"]          = time_cos
        feat["is_open_volatile"]  = is_open_volatile
        feat["is_close_volatile"] = is_close_volatile
        feat["ret_1m"]            = round(ret_1m,  6)
        feat["ret_5m"]            = round(ret_5m,  6)
        feat["ret_15m"]           = round(ret_15m, 6)
        feat["ema_cross"]         = ema_cross
        feat["bb_position"]       = round(bb_position, 6)
        feat["cvd_delta_norm"]    = round(cvd_delta_norm, 6)
        feat["poc_distance"]      = vp["poc_distance"]
        feat["in_value_area"]     = vp["in_value_area"]
        feat["va_bandwidth"]      = vp["va_bandwidth"]
        feat["poc_above"]         = vp["poc_above"]
        feat["volume_acceleration"]      = round(volume_acceleration, 6)
        feat["vwap_momentum"]            = round(vwap_momentum, 6)
        feat["prev_day_same_hour_ret"]   = prev_day_same_hour_ret

        rows.append((ts, feat))

    return rows


def load_all_dates(conn) -> list:
    """raw_features에 이미 있는 날짜 목록 반환 (update-features용)"""
    c = conn.cursor()
    return sorted(
        r[0] for r in c.execute(
            "SELECT DISTINCT substr(ts,1,10) FROM raw_features ORDER BY 1"
        ).fetchall()
    )


def scan_live_days(conn, target_dates) -> dict:
    """
    [418차] 대상 날짜 중 **라이브 수집 행이 섞인 날**을 찾아 반환한다.

    반환: {date_str: (live_cnt, backfill_cnt)}  — 라이브 행이 1개라도 있는 날만.

    라이브/백필 구분은 `feature_quality_score == BACKFILL_QUALITY_MARKER`.
    이 마커에 의존하는 근거는 `_BACKFILL_COMPUTED_KEYS` 주석 참조.
    """
    if not target_dates:
        return {}
    want = set(target_dates)
    out = {}
    c = conn.cursor()
    for ts, fj in c.execute("SELECT ts, features FROM raw_features"):
        day = ts[:10]
        if day not in want:
            continue
        try:
            q = json.loads(fj).get("feature_quality_score")
        except Exception:
            # 파싱 불가 행은 보수적으로 라이브 취급 — 덮어쓰기 판단은 안전측으로.
            q = None
        slot = out.setdefault(day, [0, 0])
        if q == BACKFILL_QUALITY_MARKER:
            slot[1] += 1
        else:
            slot[0] += 1
    return dict((d, tuple(v)) for d, v in out.items() if v[0] > 0)


def backup_db(db_path: str) -> str:
    """[418차] UPDATE 전 원본 DB 스냅샷. 생성 경로 반환."""
    import shutil
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = "%s.bak_%s" % (db_path, stamp)
    logger.info("[백업] %s → %s (약 %.0f MB)",
                os.path.basename(db_path), os.path.basename(dst),
                os.path.getsize(db_path) / 1024.0 / 1024.0)
    shutil.copy2(db_path, dst)
    return dst


def merge_features(existing_json: str, new_feat: dict) -> str:
    """
    [418차] 기존 features JSON에 백필 계산 키만 덮어써 반환 (병합 갱신).

    `_BACKFILL_COMPUTED_KEYS`에 없는 키는 **손대지 않는다** — 라이브가 수집한
    호가·수급·옵션·매크로 값이 백필의 0.0 채움에 덮이는 것을 막는 지점이다.
    기존 JSON이 깨져 있으면 백필 값 전체로 대체한다(그 행은 어차피 못 읽는다).
    """
    try:
        merged = json.loads(existing_json)
        if not isinstance(merged, dict):
            raise ValueError("dict 아님")
    except Exception:
        return json.dumps(dict(new_feat))
    for k in _BACKFILL_COMPUTED_KEYS:
        if k in new_feat:
            merged[k] = new_feat[k]
    return json.dumps(merged)


def run(dry_run: bool = False, from_date: str = None, update_features: bool = False,
        force_overwrite_live: bool = False, no_backup: bool = False):
    """
    update_features=True : 기존 raw_features 행의 features JSON을 갱신 (UPDATE).
                           [418차] **병합 갱신**이다 — 백필이 계산하는 키만 덮어쓰고
                           나머지(라이브 수집분)는 보존한다.
    update_features=False: raw_features에 없는 날짜만 INSERT (기본 소급).

    force_overwrite_live : 라이브 행이 섞인 날에도 UPDATE를 강행 (기본 False → 중단).
    no_backup            : UPDATE 전 DB 자동 백업 생략 (기본 False → 백업).
    """
    if not os.path.exists(RAW_DATA_DB):
        logger.error("raw_data.db 없음: %s", RAW_DATA_DB)
        sys.exit(1)

    conn = sqlite3.connect(RAW_DATA_DB, timeout=30)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    if update_features:
        target_dates = load_all_dates(conn)
    else:
        target_dates = load_missing_dates(conn)

    if from_date:
        target_dates = [d for d in target_dates if d >= from_date]

    mode_label = "UPDATE" if update_features else "INSERT"
    logger.info("[%s] 대상 날짜: %d일 (%s ~ %s)",
                mode_label,
                len(target_dates),
                target_dates[0] if target_dates else "-",
                target_dates[-1] if target_dates else "-")

    # ── [418차] 안전장치 ① 라이브 행 포함일 스캔 ──────────────────
    # 2026-07-13 MW0601에서 `--from` 없는 `--update-features`가 라이브 29거래일
    # 10,448행을 0.0으로 덮어썼다(9,002행 복구 불가). 같은 명령을 다시 밟지 못하게
    # 대상에 라이브 행이 섞이면 기본적으로 멈춘다.
    live_days = {}
    if update_features and target_dates:
        live_days = scan_live_days(conn, target_dates)
        if live_days:
            logger.warning("=" * 68)
            logger.warning("⚠ 대상 %d일 중 %d일에 **라이브 수집 행**이 있다.",
                           len(target_dates), len(live_days))
            for d in sorted(live_days):
                lv, bf = live_days[d]
                logger.warning("    %s  live=%d  backfill=%d", d, lv, bf)
            logger.warning("-" * 68)
            logger.warning("병합 갱신이라 라이브 수집값(호가·수급·옵션·매크로)은 보존되고")
            logger.warning("백필이 계산하는 %d개 키만 덮어쓴다.", len(_BACKFILL_COMPUTED_KEYS))
            logger.warning("그래도 라이브 행을 건드리므로 명시적 동의를 요구한다:")
            logger.warning("    --force-overwrite-live  를 붙여 다시 실행")
            logger.warning("또는 라이브 이전 구간으로 한정:  --from YYYY-MM-DD")
            logger.warning("=" * 68)
            if not force_overwrite_live:
                logger.error("중단 — 라이브 행 포함 (--force-overwrite-live 없음)")
                conn.close()
                sys.exit(2)
            logger.warning("--force-overwrite-live 지정됨 — 진행한다.")

    if dry_run:
        logger.info("[DRY-RUN] 실제 %s 없이 종료", mode_label)
        conn.close()
        return

    if not target_dates:
        logger.info("처리할 날짜 없음 — 완료")
        conn.close()
        return

    # ── [418차] 안전장치 ③ UPDATE 전 자동 백업 ────────────────────
    # 418차 복구가 우연히 남아 있던 2026-06-08 백업본에 전적으로 의존했다
    # (그것도 4일치 1,446행뿐). 다음엔 우연에 기대지 않는다.
    if update_features and not no_backup:
        conn.close()                      # 복사 중 쓰기 없도록 닫고 진행
        backup_db(RAW_DATA_DB)
        conn = sqlite3.connect(RAW_DATA_DB, timeout=30)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

    total_processed = 0
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for i, date_str in enumerate(target_dates, 1):
        candles = c.execute(
            "SELECT ts, open, high, low, close, volume "
            "FROM raw_candles WHERE substr(ts,1,10)=? ORDER BY ts",
            (date_str,),
        ).fetchall()

        if not candles:
            logger.warning("[%d/%d] %s — 캔들 없음, 건너뜀",
                           i, len(target_dates), date_str)
            continue

        rows = process_day(date_str, candles)

        if update_features:
            # [418차] 통째 교체(SET features=?) → **병합 갱신**.
            # 기존 행을 읽어 백필 계산 키만 덮어쓴다. 이 한 줄이 바뀌지 않았다면
            # --force-overwrite-live를 붙이는 순간 2026-07-13 사고가 그대로 재현된다.
            existing = dict(
                (r[0], r[1]) for r in c.execute(
                    "SELECT ts, features FROM raw_features WHERE substr(ts,1,10)=?",
                    (date_str,),
                ).fetchall()
            )
            payload = []
            for ts, feat in rows:
                prev = existing.get(ts)
                if prev is None:
                    continue          # UPDATE 대상 아님 (기존 행 없음)
                payload.append((merge_features(prev, feat), now_str, ts))
            c.executemany(
                "UPDATE raw_features SET features=?, created_at=? WHERE ts=?",
                payload,
            )
            rows = payload            # 진행 로그·누계를 실제 반영 행수 기준으로
        else:
            c.executemany(
                "INSERT OR IGNORE INTO raw_features (ts, features, created_at) VALUES (?,?,?)",
                [(ts, json.dumps(feat), now_str) for ts, feat in rows],
            )
        conn.commit()

        total_processed += len(rows)
        if i % 10 == 0 or i == len(target_dates):
            logger.info("[%d/%d] %s — %d봉 %s (누계 %d)",
                        i, len(target_dates), date_str, len(rows),
                        mode_label, total_processed)

    conn.close()
    logger.info("=== %s 완료: 총 %d행 ===", mode_label, total_processed)

    # 결과 검증
    conn2 = sqlite3.connect(RAW_DATA_DB)
    c2 = conn2.cursor()
    total_feat = c2.execute("SELECT COUNT(*) FROM raw_features").fetchone()[0]
    min_ts = c2.execute("SELECT MIN(ts) FROM raw_features").fetchone()[0]
    max_ts = c2.execute("SELECT MAX(ts) FROM raw_features").fetchone()[0]
    conn2.close()
    logger.info("raw_features 최종: %d행 (%s ~ %s)", total_feat, min_ts, max_ts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="raw_candles → raw_features 소급 생성 / 피처 갱신")
    parser.add_argument("--dry-run", action="store_true",
                        help="실제 INSERT/UPDATE 없이 대상 날짜만 출력")
    parser.add_argument("--from", dest="from_date", default=None,
                        metavar="YYYY-MM-DD",
                        help="이 날짜 이후만 처리 (기본: 전체)")
    parser.add_argument("--update-features", action="store_true",
                        help="기존 raw_features 행의 피처를 갱신 (병합 UPDATE — "
                             "백필 계산 키만 덮어쓰고 라이브 수집분은 보존)")
    parser.add_argument("--force-overwrite-live", action="store_true",
                        help="[418차] 라이브 수집 행이 섞인 날에도 UPDATE 강행. "
                             "미지정 시 해당 날짜 목록을 출력하고 중단한다.")
    parser.add_argument("--no-backup", action="store_true",
                        help="[418차] UPDATE 전 DB 자동 백업 생략 (권장하지 않음)")
    args = parser.parse_args()

    run(dry_run=args.dry_run, from_date=args.from_date,
        update_features=args.update_features,
        force_overwrite_live=args.force_overwrite_live,
        no_backup=args.no_backup)
