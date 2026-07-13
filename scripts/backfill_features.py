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

사용법:
  python scripts/backfill_features.py             # 전체 소급
  python scripts/backfill_features.py --dry-run   # 건수만 확인
  python scripts/backfill_features.py --from 2026-01-01  # 특정 날짜 이후만
  python scripts/backfill_features.py --update-features --from 2026-04-28
      # 317차 hurst 재보정 반영 — 기존 raw_features 행을 새 공식으로 재계산해 UPDATE

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

# 현재 raw_features에서 사용 중인 키 목록 (318차: hurst_ready 추가, 실제 116개 —
# 기존 "99개" 주석은 2026-06-01 이후 드리프트된 값이라 실측치로 정정)
# 계산 가능한 것 외에는 모두 0.0
FEATURE_KEYS_ALL = [
    "above_vwap", "atr", "atr_ratio", "avg_volume",
    "bear_exhaustion", "bear_exhaustion_signal", "bear_reversal_signal",
    "bull_exhaustion", "bull_exhaustion_signal", "bull_reversal_signal",
    "cancel_add_ratio", "cvd", "cvd_direction", "cvd_divergence",
    "cvd_exhaustion", "cvd_exhaustion_signal", "cvd_monotone_ratio", "cvd_slope",
    "feature_degraded", "feature_quality_score", "feature_recoverable_errors",
    "foreign_call_net", "foreign_futures_net", "foreign_put_net",
    "foreign_retail_divergence",
    "hurst", "hurst_ready", "imbalance_slope", "institution_futures_net",
    "macro_event_flag", "macro_krw_chg", "macro_nasdaq_chg",
    "macro_quality_age_sec", "macro_quality_available",
    "macro_quality_fallback_used", "macro_quality_source_code",
    "macro_quality_stale", "macro_risk_off", "macro_risk_on",
    "macro_sp500_chg", "macro_us10y_chg", "macro_vix", "macro_vix_abs",
    "microprice", "microprice_bias", "microprice_depth_bias", "microprice_slope",
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
    "vwap", "vwap_position",
    # 방향성 고도화 피처 (P2 — 2026-06-01 추가)
    "time_sin", "time_cos", "is_open_volatile", "is_close_volatile",
    "ret_1m", "ret_5m", "ret_15m",
    "ema_cross", "bb_position",
    "cvd_delta_norm",
    "poc_distance", "in_value_area", "va_bandwidth", "poc_above",
    # 개선 3 잔여 방향성 피처 (2026-06-01 추가)
    "volume_acceleration", "vwap_momentum", "prev_day_same_hour_ret",
]


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
    하루치 캔들 리스트 → raw_features 삽입용 (ts, features_json) 리스트 반환

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
        feat["vwap"]          = float(vwap_res["vwap"])
        feat["vwap_position"] = float(vwap_res["position"])
        feat["above_vwap"]    = 1.0 if vwap_res["above_vwap"] else 0.0
        feat["cvd_direction"] = cvd_dir
        feat["cvd_slope"]     = cvd_slope
        feat["avg_volume"]    = round(avg_vol, 2)
        feat["hurst"]         = hurst
        feat["hurst_ready"]   = hurst_ready
        feat["feature_quality_score"] = 0.3  # 소급 데이터 마커

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

        rows.append((ts, json.dumps(feat)))

    return rows


def load_all_dates(conn) -> list:
    """raw_features에 이미 있는 날짜 목록 반환 (update-features용)"""
    c = conn.cursor()
    return sorted(
        r[0] for r in c.execute(
            "SELECT DISTINCT substr(ts,1,10) FROM raw_features ORDER BY 1"
        ).fetchall()
    )


def run(dry_run: bool = False, from_date: str = None, update_features: bool = False):
    """
    update_features=True : 기존 raw_features 행의 features JSON을 새 피처로 갱신 (UPDATE).
    update_features=False: raw_features에 없는 날짜만 INSERT (기본 소급).
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

    if dry_run:
        logger.info("[DRY-RUN] 실제 %s 없이 종료", mode_label)
        conn.close()
        return

    if not target_dates:
        logger.info("처리할 날짜 없음 — 완료")
        conn.close()
        return

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
            # 기존 행의 features JSON을 새 피처로 통째 교체
            c.executemany(
                "UPDATE raw_features SET features=?, created_at=? WHERE ts=?",
                [(feat_json, now_str, ts) for ts, feat_json in rows],
            )
        else:
            c.executemany(
                "INSERT OR IGNORE INTO raw_features (ts, features, created_at) VALUES (?,?,?)",
                [(ts, feat_json, now_str) for ts, feat_json in rows],
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
                        help="기존 raw_features 행의 피처 JSON을 신규 피처로 갱신 (UPDATE)")
    args = parser.parse_args()

    run(dry_run=args.dry_run, from_date=args.from_date,
        update_features=args.update_features)
