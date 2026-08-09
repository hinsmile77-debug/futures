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


def derive_bar_flow(volume, high, low, close, buy_vol=None, sell_vol=None):
    # type: (float, float, float, float, object, object) -> tuple
    """1분봉의 매수/매도 귀속량을 낸다. 실측 우선, 없으면 바 기하학 프록시.

    반환: `(buy, sell, used_proxy)` — `buy + sell == volume` 을 항상 만족한다.

    [MW0601 452차 / QDQ Phase 1] 종전에는 `"buy_vol": 0, "sell_vol": 0` 하드코딩이었다.
    `feedback_no_schema_fallback_in_collection`(451차)의 재발 #2이며, 원천이 실제로
    값을 갖고 있는데도(2026-06-08 이후 raw_candles에 실측 존재) 조회조차 하지 않았다.

    프록시 공식은 `features/feature_builder.py:190-192` ·
    `scripts/exhaustion_restore_replay.py:157-159`와 **동일**하다 — 재구성 도구마다
    다른 근사를 쓰면 산출물이 서로 대조 불가능해진다.

    ⚠ N분봉 집계 후 한 번 계산하지 않고 **1분봉마다** 계산해 합산한다.
      라이브(`bar_aggregator`가 분당 귀속을 합산)와 같은 의미가 되게 하기 위함이다.
    """
    if buy_vol is not None and sell_vol is not None:
        return float(buy_vol), float(sell_vol), False
    vol = float(volume or 0.0)
    rng = max(float(high or 0.0) - float(low or 0.0), 1e-9)
    buy = vol * max(float(close or 0.0) - float(low or 0.0), 0.0) / rng
    sell = vol - buy          # 합이 volume과 정확히 일치하도록 잔차로 낸다
    return buy, sell, True


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
                # [452차 Phase 1] buy_vol/sell_vol 추가 조회 — 종전에는 조회조차 하지
                # 않고 0을 하드코딩했다(재발 #2).
                "SELECT ts, open, high, low, close, volume, bid1, ask1, "
                "buy_vol, sell_vol "
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

        proxy_bars = 0
        for row in candle_rows:
            # [452차 Phase 1] 실측 우선, NULL이면 바 기하학 프록시.
            # ⚠ 이 스크립트의 로컬 `override_horizon_features()`(위)는 현재
            #   buy_vol/sell_vol을 **소비하지 않는다** — 그래서 종전 0 하드코딩이
            #   산출물을 직접 틀리게 만든 적은 없다. 그래도 고치는 이유:
            #   ① 거짓값을 만들어 두면 나중에 소비처가 생겼을 때 조용히 틀린다
            #     (라이브 경로 `feature_builder.override_horizon_features()`는 이 값으로
            #      N분봉 cvd_direction을 재계산한다 — 두 함수를 정렬할 때 바로 밟는다)
            #   ② 451차 규칙(원천이 주는 값을 0으로 위장 금지)의 재발 #2를 남겨두지 않는다
            _buy, _sell, _used_proxy = derive_bar_flow(
                volume=row["volume"], high=row["high"], low=row["low"],
                close=row["close"],
                buy_vol=row["buy_vol"], sell_vol=row["sell_vol"],
            )
            proxy_bars += 1 if _used_proxy else 0
            bar = {
                "ts":       row["ts"],
                "open":     float(row["open"]   or 0.0),
                "high":     float(row["high"]   or 0.0),
                "low":      float(row["low"]    or 0.0),
                "close":    float(row["close"]  or 0.0),
                "volume":   int(row["volume"]   or 0),
                "bid1":     float(row["bid1"]   or 0.0) if row["bid1"] else 0.0,
                "ask1":     float(row["ask1"]   or 0.0) if row["ask1"] else 0.0,
                "buy_vol":  _buy,
                "sell_vol": _sell,
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
        # [452차 Phase 1] 실측 없이 기하 프록시로 채운 1분봉 비율 — 이 값이 높으면
        # 그 구간의 흐름 파생 피처는 "추정"이지 "관측"이 아니다.
        logger.info("[%dm] 매수/매도 귀속: 실측 %d봉 / 기하 프록시 %d봉 (%.1f%%)",
                    h_min, len(candle_rows) - proxy_bars, proxy_bars,
                    100.0 * proxy_bars / max(len(candle_rows), 1))

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
