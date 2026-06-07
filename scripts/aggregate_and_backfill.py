"""
scripts/aggregate_and_backfill.py — Phase 2 배포 직후 1회 실행
────────────────────────────────────────────────────────────────
기존 raw_candles(72k봉) → N분봉 집계 → raw_features_horizon 생성.

사용:
    conda activate py37_32
    python scripts/aggregate_and_backfill.py
    python scripts/aggregate_and_backfill.py --weeks 10

피처 품질 등급 (부록 D-4 기준):
    A — OHLCV로 정상 계산 (atr, ret_Nm, bar_volume, ema_cross, bb_position 등)
    B — 근사 가능 (spread_ticks, volume_acceleration)
    C — 0으로 채움 (OFI/CVD: tick 데이터 없음)
    → C등급 피처는 장기(10m+) 호라이즌에서 FEATURE_HALFLIFE가 이미 0 처리
"""
import sys
import os
import argparse
import datetime
import logging
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

_today = datetime.datetime.now().strftime("%Y%m%d")
_log_dir = os.path.join(BASE_DIR, "logs")
os.makedirs(_log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            os.path.join(_log_dir, "{}_BACKFILL.log".format(_today)),
            encoding="utf-8",
        ),
    ],
)
logger = logging.getLogger("BACKFILL")

HORIZONS_TO_BACKFILL = [3, 5, 10, 15, 30]

# C등급 피처 — tick 데이터 없어 0으로 채움
C_GRADE_FEATURES = [
    "ofi_norm", "mlofi_norm", "cvd_delta_norm", "cvd_slope",
    "microprice_bias", "queue_directional_depletion",
]


def compute_ohlcv_features(bar, h_min, prev_close=None):
    # type: (dict, int, float) -> dict
    """A·B등급 피처를 OHLCV에서 계산."""
    high  = float(bar.get("high",  0.0) or 0.0)
    low   = float(bar.get("low",   0.0) or 0.0)
    close = float(bar.get("close", 0.0) or 0.0)
    open_ = float(bar.get("open",  close) or close)
    vol   = int(bar.get("volume",  0) or 0)

    feats = {}

    # A등급
    feats["atr"]         = max(high - low, 0.5)
    feats["bar_volume"]  = float(vol)
    feats["ret_{}m".format(h_min)] = (close - open_) / (open_ + 1e-9)
    feats["above_vwap"]  = 0.5   # 집계봉에서는 계산 불가 → 중립
    feats["threshold_feasibility"] = feats["atr"] / (close * 0.0004 + 1e-9)

    # B등급 근사
    bid1 = float(bar.get("bid1") or 0.0)
    ask1 = float(bar.get("ask1") or 0.0)
    feats["spread_ticks"] = max(round((ask1 - bid1) / 0.05), 0) if ask1 > bid1 else 1.0

    # C등급: 0 채움
    for f in C_GRADE_FEATURES:
        feats[f] = 0.0

    return feats


def main():
    parser = argparse.ArgumentParser(description="Phase 2 backfill: raw_candles → raw_features_horizon")
    parser.add_argument("--weeks", type=int, default=10,
                        help="backfill 기간 (주). 기본 10주")
    parser.add_argument("--dry-run", action="store_true", default=False,
                        help="실제 저장 없이 집계 수 출력만")
    args = parser.parse_args()

    from config.settings import RAW_DATA_DB
    from features.bar_aggregator import BarAggregator
    from features.feature_decay import get_horizon_features, BACKFILL_QUALITY

    if not os.path.exists(RAW_DATA_DB):
        logger.error("raw_data.db 없음: %s", RAW_DATA_DB)
        sys.exit(1)

    # DB 스키마 초기화 (raw_features_horizon 테이블 없으면 생성)
    try:
        from utils.db_utils import init_raw_data_db
        init_raw_data_db()
        logger.info("DB 스키마 초기화 완료")
    except Exception as e:
        logger.warning("DB 초기화 오류 (계속 진행): %s", e)

    cutoff = (
        datetime.datetime.now() - datetime.timedelta(weeks=args.weeks)
    ).strftime("%Y-%m-%d %H:%M:%S")

    logger.info("=" * 60)
    logger.info("Phase 2 Backfill 시작 | weeks=%d | cutoff=%s | dry_run=%s",
                args.weeks, cutoff[:10], args.dry_run)
    logger.info("=" * 60)

    # 1분봉 전체 로드
    try:
        with sqlite3.connect(RAW_DATA_DB, timeout=30) as conn:
            conn.row_factory = sqlite3.Row
            candle_rows = conn.execute(
                "SELECT ts, open, high, low, close, volume, bid1, ask1 "
                "FROM raw_candles WHERE ts>=? ORDER BY ts",
                (cutoff,),
            ).fetchall()
    except Exception as e:
        logger.error("raw_candles 로드 실패: %s", e)
        sys.exit(1)

    logger.info("1분봉 로드: %d봉", len(candle_rows))

    total_saved = {h: 0 for h in HORIZONS_TO_BACKFILL}

    for h_min in HORIZONS_TO_BACKFILL:
        logger.info("── %dm 집계 시작 ──", h_min)
        aggregator = BarAggregator()
        count = 0

        for row in candle_rows:
            bar = {
                "ts":     row["ts"],
                "open":   float(row["open"]   or 0.0),
                "high":   float(row["high"]   or 0.0),
                "low":    float(row["low"]    or 0.0),
                "close":  float(row["close"]  or 0.0),
                "volume": int(row["volume"]   or 0),
                "bid1":   float(row["bid1"]   or 0.0) if row["bid1"] else 0.0,
                "ask1":   float(row["ask1"]   or 0.0) if row["ask1"] else 0.0,
                "buy_vol":  0,
                "sell_vol": 0,
            }
            completed = aggregator.push(bar)
            agg_bar = completed.get(h_min)
            if agg_bar is None:
                continue

            # A·B등급 피처 계산
            feats = compute_ohlcv_features(agg_bar, h_min)

            # 반감기 적용 (C등급 피처 장기 호라이즌 자동 감쇠)
            feats = get_horizon_features(feats, "{}m".format(h_min))

            if not args.dry_run:
                try:
                    from utils.db_utils import save_horizon_features
                    save_horizon_features(agg_bar["ts"], "{}m".format(h_min), feats)
                except Exception as e:
                    logger.warning("[%dm] %s 저장 실패: %s", h_min, agg_bar["ts"], e)

            count += 1
            if count % 500 == 0:
                logger.info("  [%dm] %d봉 처리 중...", h_min, count)

        total_saved[h_min] = count
        logger.info("[%dm] 완료: %d봉 %s", h_min, count,
                    "(dry-run)" if args.dry_run else "저장")

    logger.info("=" * 60)
    logger.info("Backfill 완료:")
    for h_min in HORIZONS_TO_BACKFILL:
        logger.info("  %dm: %d봉", h_min, total_saved[h_min])
    logger.info("=" * 60)
    if not args.dry_run:
        logger.info("다음 단계: python scripts/eod_retrain.py --phase2 --weeks 10 --force")


if __name__ == "__main__":
    main()
