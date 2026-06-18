"""
scripts/catch_up_eod.py — 미완료 EOD 작업 수동 완료 스크립트
────────────────────────────────────────────────────────────
사용:
    conda activate py37_32
    python scripts/catch_up_eod.py            # 기본: 오늘 날짜 기준
    python scripts/catch_up_eod.py --weeks 26 # 재학습 기간 지정

대상 (daily_close MemoryError 이후 미완료 작업):
  STEP 1. GBM/RF 모델 재학습 (fix 적용: CV fold 20k 상한)
  STEP 2. P8 EOD 스케일러 재적합 (내일 시초 z-score 안정화)
  STEP 3. SQLite WAL 체크포인트 (DB WAL 정리)

생략 (세션 런타임 in-memory 필요 → 내일 장 시작 후 자동 복구):
  - DailyConsolidator  : 장중 누적 데이터가 in-memory — 재구성 불가
  - DriftAdjuster      : OnlineLearner 정확도 필요 — 이전 state 유지됨
  - EnsembleCalibrator : in-memory Platt 파라미터 — 이전 pkl 유지됨
  - MetaConf save      : in-memory 상태 — 다음날 cold-start로 대체

내일 장 시작 흐름:
  08:45  EarlyWarmup (스케일러 노후화 감지 시 자동 재적합)
  08:55  PreRetrain   (_eod_retrain_ok=False 이므로 항상 실행)
         → 이 스크립트를 실행하면 08:55 PreRetrain 시 이미 최신 PKL 상태
"""
import sys
import os
import argparse
import datetime
import logging
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# ── 로그 설정 ─────────────────────────────────────────────────
_today = datetime.datetime.now().strftime("%Y%m%d")
_log_dir = os.path.join(BASE_DIR, "logs")
os.makedirs(_log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            os.path.join(_log_dir, f"{_today}_CATCH_UP_EOD.log"),
            encoding="utf-8",
        ),
    ],
)
logger = logging.getLogger("CATCH_UP_EOD")

# LEARNING 로거도 같은 핸들러에 연결 (batch_retrainer 로그 출력)
logging.getLogger("LEARNING").handlers = logging.getLogger("CATCH_UP_EOD").handlers
logging.getLogger("LEARNING").setLevel(logging.INFO)
logging.getLogger("LEARNING").propagate = False


# ── 유틸 ─────────────────────────────────────────────────────
def _sep(title):
    logger.info("=" * 60)
    logger.info("  %s", title)
    logger.info("=" * 60)


def _ok(msg):
    logger.info("[OK]   %s", msg)


def _skip(msg):
    logger.info("[SKIP] %s", msg)


def _warn(msg):
    logger.warning("[WARN] %s", msg)


def _fail(msg):
    logger.error("[FAIL] %s", msg)


# ═══════════════════════════════════════════════════════════════
# STEP 1: GBM / RF 재학습
# ═══════════════════════════════════════════════════════════════
def step1_gbm_retrain(weeks_back: int, force: bool = True) -> bool:
    _sep("STEP 1: GBM/RF 배치 재학습")

    try:
        from learning.batch_retrainer import BatchRetrainer, MIN_TRAIN_BARS
    except ImportError as e:
        _fail(f"임포트 실패 — py37_32 환경 확인: {e}")
        return False

    logger.info("weeks_back=%d | force=%s | MIN_TRAIN_BARS=%d", weeks_back, force, MIN_TRAIN_BARS)

    start_dt = datetime.datetime.now()
    retrainer = BatchRetrainer()
    result = retrainer.retrain_now(
        weeks_back=weeks_back,
        force=force,
        intraday=False,   # 전체 CV 실행 (fix: fold 상한 20k 적용됨)
    )
    elapsed = (datetime.datetime.now() - start_dt).total_seconds()

    if result.get("ok"):
        horizons = result.get("horizons", {})
        replaced = sum(1 for r in horizons.values() if r.get("replaced"))
        _ok(
            f"완료 | {result.get('elapsed_sec', elapsed):.1f}초 | "
            f"데이터={result.get('data_size', 0):,}행 | "
            f"교체={replaced}/{len(horizons)} 호라이즌"
        )
        for h in ["1m", "3m", "5m", "10m", "15m", "30m"]:
            r = horizons.get(h, {})
            marker = "교체" if r.get("replaced") else "유지"
            cv = r.get("cv_acc")
            old = r.get("old_acc", 0.0)
            logger.info(
                "    %s  %s | cv_acc=%s | old_acc=%.4f",
                h, marker,
                f"{cv:.4f}" if cv is not None else "nan(no-cv)",
                old,
            )
        return True
    else:
        err = result.get("error", "알 수 없음")
        _fail(f"재학습 실패: {err}")
        if "부족" in str(err):
            _fail("→ --weeks를 늘리거나 backfill_features.py를 먼저 실행하세요.")
        return False


# ═══════════════════════════════════════════════════════════════
# STEP 2: P8 EOD 스케일러 재적합
# ═══════════════════════════════════════════════════════════════
def step2_scaler_refit() -> bool:
    _sep("STEP 2: P8 EOD 스케일러 재적합")

    try:
        from learning.batch_retrainer import BatchRetrainer
        from model.multi_horizon_model import MultiHorizonModel
        from config.settings import SCALER_WARMUP_LOOKBACK_BARS, HORIZON_DIR
    except ImportError as e:
        _fail(f"임포트 실패: {e}")
        return False

    retrainer = BatchRetrainer()
    X, feature_names = retrainer.load_features_for_warmup(
        lookback_bars=SCALER_WARMUP_LOOKBACK_BARS
    )

    if X is None or len(X) == 0:
        _warn("스케일러 재적합용 데이터 없음 — raw_data.db 확인")
        return False

    logger.info("피처 로드: n=%d봉 feat=%d", len(X), len(feature_names) if feature_names else 0)

    try:
        model = MultiHorizonModel()
        loaded = model._load_all()
        if loaded:
            logger.info("PKL 로드 완료 (불일치 호라이즌=%d)", len(loaded))

        result = model.refit_scalers_only(
            X,
            feature_names,
            trigger_ts=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            trigger_type="E_EOD",
            trigger_reason="catch_up_eod.py P8 — retrain_eod.py 미실행 시 수동 복구",
        )

        if result.get("ok") is not False:
            _ok(
                f"스케일러 재적합 완료 | n={len(X)}봉 | "
                f"elapsed={result.get('elapsed_sec', 0):.2f}s | "
                f"horizons={result.get('horizons', [])}"
            )
            return True
        else:
            _fail(f"스케일러 재적합 실패: {result.get('error', '알 수 없음')}")
            return False

    except Exception as e:
        _fail(f"스케일러 재적합 예외: {e}")
        import traceback
        traceback.print_exc()
        return False


# ═══════════════════════════════════════════════════════════════
# STEP 3: WAL 체크포인트
# ═══════════════════════════════════════════════════════════════
def step3_wal_checkpoint() -> bool:
    _sep("STEP 3: SQLite WAL 체크포인트")

    try:
        from config.settings import EOD_WAL_CHECKPOINT_DBS
    except ImportError as e:
        _fail(f"임포트 실패: {e}")
        return False

    ok_count = 0
    for db_path in EOD_WAL_CHECKPOINT_DBS:
        if not os.path.exists(db_path):
            _skip(f"{os.path.basename(db_path)} — 파일 없음")
            continue
        try:
            with sqlite3.connect(db_path, timeout=30) as conn:
                conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            _ok(f"{os.path.basename(db_path)}")
            ok_count += 1
        except Exception as e:
            _warn(f"{os.path.basename(db_path)} 체크포인트 실패 (무해): {e}")

    logger.info("WAL 체크포인트: %d/%d DB 처리", ok_count, len(EOD_WAL_CHECKPOINT_DBS))
    return True


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(description="미륵이 EOD catch-up — 미완료 작업 수동 완료")
    parser.add_argument(
        "--weeks", type=int, default=26,
        help="재학습 기간 (주). 기본 26 — EOD 표준값",
    )
    parser.add_argument(
        "--no-force", dest="force", action="store_false", default=True,
        help="GBM 성능 저하 시 교체 금지 (기본: force=True)",
    )
    parser.add_argument(
        "--skip-retrain", action="store_true", default=False,
        help="STEP 1 GBM 재학습 건너뜀 (스케일러+WAL만 실행)",
    )
    parser.add_argument(
        "--skip-scaler", action="store_true", default=False,
        help="STEP 2 스케일러 재적합 건너뜀",
    )
    args = parser.parse_args()

    logger.info("")
    logger.info("┌─────────────────────────────────────────────┐")
    logger.info("│  미륵이 EOD catch-up  %s  │", datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    logger.info("│  대상: GBM재학습 + 스케일러재적합 + WAL      │")
    logger.info("└─────────────────────────────────────────────┘")
    logger.info("")

    results = {}

    # STEP 1
    if args.skip_retrain:
        _skip("STEP 1 GBM 재학습 — --skip-retrain 지정으로 건너뜀")
        results["retrain"] = "SKIP"
    else:
        ok = step1_gbm_retrain(weeks_back=args.weeks, force=args.force)
        results["retrain"] = "OK" if ok else "FAIL"

    # STEP 2 (재학습 성공하거나 skip인 경우만 실행 — 실패 시에도 실행)
    if args.skip_scaler:
        _skip("STEP 2 스케일러 재적합 — --skip-scaler 지정으로 건너뜀")
        results["scaler"] = "SKIP"
    else:
        ok = step2_scaler_refit()
        results["scaler"] = "OK" if ok else "FAIL"

    # STEP 3
    step3_wal_checkpoint()
    results["wal"] = "OK"

    # ── 최종 요약 ─────────────────────────────────────────────
    logger.info("")
    logger.info("=" * 60)
    logger.info("  최종 요약")
    logger.info("=" * 60)
    logger.info("  GBM 재학습   : %s", results["retrain"])
    logger.info("  스케일러 재적합: %s", results["scaler"])
    logger.info("  WAL 체크포인트: %s", results["wal"])
    logger.info("")

    if results["retrain"] == "FAIL":
        logger.error("GBM 재학습 실패 — 내일 08:55 PreRetrain이 자동으로 재시도합니다.")
    else:
        logger.info("PKL 저장 위치: %s", os.path.join(BASE_DIR, "model", "horizons"))

    if results["scaler"] == "FAIL":
        logger.warning("스케일러 재적합 실패 — 내일 08:45 EarlyWarmup이 자동으로 재시도합니다.")

    logger.info("")
    logger.info("내일 장 시작 흐름:")
    logger.info("  08:45  EarlyWarmup (스케일러 노후화 감지 시 자동 재적합)")
    logger.info("  08:55  PreRetrain  (항상 실행 — _eod_retrain_ok 미영속)")
    logger.info("  09:00  장 시작")
    logger.info("")

    # 실패 항목이 있으면 exit code 1
    if "FAIL" in results.values():
        sys.exit(1)


if __name__ == "__main__":
    main()
