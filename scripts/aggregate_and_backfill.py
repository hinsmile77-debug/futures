"""
scripts/aggregate_and_backfill.py — Phase 2 배포 직후 1회 실행
────────────────────────────────────────────────────────────────
기존 raw_candles(72k봉) → N분봉 집계 → raw_features_horizon 생성.

★ 피처 구성 방식 (v2 — JOIN 방식):
    N분봉 완성 시각 T에 대해 raw_features 테이블의 1m 피처(105+개)를 base로 사용,
    atr / bar_volume / ret_Nm 만 N분봉 OHLCV 값으로 오버라이드 후 feature_decay 적용.
    → 학습/추론 피처 벡터가 일치 (build_for_horizon 로직과 동일).

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
import json

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


def override_horizon_features(base_feats, bar_n, h_min):
    # type: (dict, dict, int) -> dict
    """
    1m 피처 dict(base_feats)를 base로,
    N분봉 bar_n의 OHLCV 값으로 atr/bar_volume/ret_Nm 오버라이드.
    feature_decay.get_horizon_features 적용 후 반환.
    """
    feats = dict(base_feats)

    high  = float(bar_n.get("high",  0.0) or 0.0)
    low   = float(bar_n.get("low",   0.0) or 0.0)
    close = float(bar_n.get("close", 0.0) or 0.0)
    open_ = float(bar_n.get("open",  close) or close)
    vol   = int(bar_n.get("volume",  0) or 0)

    feats["atr"]         = max(high - low, 0.5)
    feats["bar_volume"]  = float(vol)
    feats["ret_{}m".format(h_min)] = (close - open_) / (open_ + 1e-9)

    from features.feature_decay import get_horizon_features
    return get_horizon_features(feats, "{}m".format(h_min))


def main():
    parser = argparse.ArgumentParser(
        description="Phase 2 backfill: raw_candles+raw_features → raw_features_horizon"
    )
    parser.add_argument("--weeks", type=int, default=10,
                        help="backfill 기간 (주). 기본 10주")
    parser.add_argument("--dry-run", action="store_true", default=False,
                        help="실제 저장 없이 집계 수 출력만")
    parser.add_argument("--clear", action="store_true", default=False,
                        help="기존 raw_features_horizon 데이터 삭제 후 재생성")
    args = parser.parse_args()

    from config.settings import RAW_DATA_DB
    from features.bar_aggregator import BarAggregator

    if not os.path.exists(RAW_DATA_DB):
        logger.error("raw_data.db 없음: %s", RAW_DATA_DB)
        sys.exit(1)

    # DB 스키마 초기화
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
    logger.info("Phase 2 Backfill v2 시작 | weeks=%d | cutoff=%s | dry_run=%s",
                args.weeks, cutoff[:10], args.dry_run)
    logger.info("방식: raw_features JOIN → 105+ 피처 오버라이드")
    logger.info("=" * 60)

    # --clear: 기존 데이터 삭제
    if args.clear and not args.dry_run:
        try:
            with sqlite3.connect(RAW_DATA_DB, timeout=30) as conn:
                conn.execute(
                    "DELETE FROM raw_features_horizon WHERE horizon!=? AND ts>=?",
                    ("1m", cutoff)
                )
                conn.execute(
                    "DELETE FROM raw_features_horizon WHERE horizon=? AND ts>=?",
                    ("1m", cutoff)
                )
                conn.commit()
            logger.info("기존 raw_features_horizon 데이터 삭제 완료 (cutoff=%s)", cutoff[:10])
        except Exception as e:
            logger.warning("기존 데이터 삭제 실패: %s", e)

    # 1분봉 + raw_features 동시 로드
    try:
        with sqlite3.connect(RAW_DATA_DB, timeout=30) as conn:
            conn.row_factory = sqlite3.Row
            candle_rows = conn.execute(
                "SELECT ts, open, high, low, close, volume, bid1, ask1 "
                "FROM raw_candles WHERE ts>=? ORDER BY ts",
                (cutoff,),
            ).fetchall()
            feat_rows = conn.execute(
                "SELECT ts, features FROM raw_features WHERE ts>=? ORDER BY ts",
                (cutoff,),
            ).fetchall()
    except Exception as e:
        logger.error("DB 로드 실패: %s", e)
        sys.exit(1)

    # raw_features → dict (ts → feature_dict)
    feat_map = {}
    for r in feat_rows:
        try:
            fd = json.loads(r["features"])
            if isinstance(fd, dict) and fd:
                feat_map[r["ts"]] = fd
        except (ValueError, TypeError):
            pass

    logger.info("1분봉 로드: %d봉  |  raw_features 로드: %d행  |  매핑: %d행",
                len(candle_rows), len(feat_rows), len(feat_map))

    if len(feat_map) == 0:
        logger.error("raw_features 데이터 없음 — 백필 불가. "
                     "미륵이를 먼저 실행하여 raw_features를 채우세요.")
        sys.exit(1)

    sample_feats = next(iter(feat_map.values()))
    logger.info("피처 수: %d개 (예: %s)", len(sample_feats), list(sample_feats.keys())[:5])

    total_saved = {h: 0 for h in HORIZONS_TO_BACKFILL}
    total_skipped = {h: 0 for h in HORIZONS_TO_BACKFILL}

    for h_min in HORIZONS_TO_BACKFILL:
        logger.info("── %dm 집계 시작 ──", h_min)
        aggregator = BarAggregator()
        count = 0
        skipped = 0

        for row in candle_rows:
            bar = {
                "ts":       row["ts"],
                "open":     float(row["open"]   or 0.0),
                "high":     float(row["high"]   or 0.0),
                "low":      float(row["low"]    or 0.0),
                "close":    float(row["close"]  or 0.0),
                "volume":   int(row["volume"]   or 0),
                "bid1":     float(row["bid1"]   or 0.0) if row["bid1"] else 0.0,
                "ask1":     float(row["ask1"]   or 0.0) if row["ask1"] else 0.0,
                "buy_vol":  0,
                "sell_vol": 0,
            }
            completed = aggregator.push(bar)
            agg_bar = completed.get(h_min)
            if agg_bar is None:
                continue

            # N분봉 완성 시각의 1m 피처를 base로 사용
            ts = agg_bar["ts"]
            base_feats = feat_map.get(ts)
            if base_feats is None:
                # fallback: cutoff 이전 봉이거나 raw_features 누락 — 건너뜀
                skipped += 1
                continue

            # atr/bar_volume/ret_Nm 오버라이드 + feature_decay 적용
            try:
                feats = override_horizon_features(base_feats, agg_bar, h_min)
            except Exception as e:
                logger.debug("[%dm] 피처 오버라이드 오류: %s", h_min, e)
                skipped += 1
                continue

            if not args.dry_run:
                try:
                    from utils.db_utils import save_horizon_features
                    save_horizon_features(ts, "{}m".format(h_min), feats)
                except Exception as e:
                    logger.warning("[%dm] %s 저장 실패: %s", h_min, ts, e)

            count += 1
            if count % 500 == 0:
                logger.info("  [%dm] %d봉 처리 중...", h_min, count)

        total_saved[h_min] = count
        total_skipped[h_min] = skipped
        logger.info("[%dm] 완료: %d봉 저장 / %d봉 건너뜀 %s",
                    h_min, count, skipped, "(dry-run)" if args.dry_run else "")

    logger.info("=" * 60)
    logger.info("Backfill v2 완료:")
    for h_min in HORIZONS_TO_BACKFILL:
        logger.info("  %dm: %d봉 저장 / %d봉 건너뜀", h_min, total_saved[h_min], total_skipped[h_min])
    if not args.dry_run:
        feat_count = len(next(iter(feat_map.values()))) if feat_map else 0
        logger.info("  피처 수: %d개 (전체 1m 피처 기반)", feat_count)
        logger.info("=" * 60)
        logger.info("다음 단계: python scripts/eod_retrain.py --phase2 --weeks 10")


if __name__ == "__main__":
    main()
