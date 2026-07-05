"""
장 마감 후 독립 실행 GBM EOD 재학습 스크립트
────────────────────────────────────────────────
사용:
    conda activate py37_32
    python scripts/eod_retrain.py
    python scripts/eod_retrain.py --weeks 10
    python scripts/eod_retrain.py --weeks 10 --no-force

미륵이 종료 상태에서 실행하는 전용 스크립트.
미륵이 실행 중에는 15:40 daily_close()가 자동으로 동일 작업을 실행함.
"""
import sys
import os
import argparse
import datetime
import logging

# ── 프로젝트 루트를 sys.path에 추가 ───────────────────────────
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
            os.path.join(_log_dir, f"{_today}_EOD_RETRAIN.log"),
            encoding="utf-8",
        ),
    ],
)
logger = logging.getLogger("EOD_RETRAIN")


def main():
    parser = argparse.ArgumentParser(description="미륵이 EOD GBM 재학습")
    parser.add_argument(
        "--weeks", type=int, default=10,
        help="학습 기간 (주). 기본 10 — 약 16,000봉 (MIN_TRAIN_BARS=15,000 통과 기준)",
    )
    parser.add_argument(
        "--no-force", dest="force", action="store_false", default=True,
        help="성능 저하 시 교체 금지 (기본: force=True로 강제 교체)",
    )
    parser.add_argument(
        "--phase2", action="store_true", default=False,
        help="Phase 2 경로: raw_features_horizon 테이블(호라이즌별 N분봉 피처)로 재학습",
    )
    # [260705 검증 캠페인] 주간 스텝 — 기본 None = 금요일에만 자동 실행
    parser.add_argument(
        "--campaign", dest="campaign", action="store_true", default=None,
        help="검증 캠페인 주간 스텝 강제 실행 (기본: 금요일 자동)",
    )
    parser.add_argument(
        "--no-campaign", dest="campaign", action="store_false",
        help="검증 캠페인 주간 스텝 실행 안 함",
    )
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("EOD GBM 재학습 시작 | weeks_back=%d | force=%s", args.weeks, args.force)
    logger.info("BASE_DIR: %s", BASE_DIR)
    logger.info("=" * 60)

    # ── 임포트 (py37_32 환경 필요) ─────────────────────────────
    try:
        from learning.batch_retrainer import BatchRetrainer, MIN_TRAIN_BARS, MIN_TRAIN_BARS_PER_HORIZON
    except ImportError as e:
        logger.error("임포트 실패 — py37_32 환경에서 실행했는지 확인: %s", e)
        sys.exit(1)

    if args.phase2:
        logger.info("Phase 2 모드: 호라이즌별 N분봉 피처 사용")
        logger.info("MIN_TRAIN_BARS_PER_HORIZON=%s", MIN_TRAIN_BARS_PER_HORIZON)
    else:
        logger.info("MIN_TRAIN_BARS=%d", MIN_TRAIN_BARS)

    # ── 재학습 실행 ────────────────────────────────────────────
    start_dt = datetime.datetime.now()
    retrainer = BatchRetrainer()
    result = retrainer.retrain_now(
        weeks_back=args.weeks,
        force=args.force,
        use_horizon_features=args.phase2,
    )

    elapsed = (datetime.datetime.now() - start_dt).total_seconds()

    # ── 결과 출력 ──────────────────────────────────────────────
    logger.info("=" * 60)
    if result.get("ok"):
        logger.info(
            "재학습 완료 | 소요=%.1f초 (%.1f분) | 데이터=%d행",
            result.get("elapsed_sec", elapsed),
            result.get("elapsed_sec", elapsed) / 60,
            result.get("data_size", 0),
        )
        horizons = result.get("horizons", {})
        replaced_count = sum(1 for r in horizons.values() if r.get("replaced"))
        logger.info("교체: %d/%d 호라이즌", replaced_count, len(horizons))
        for h in ["1m", "3m", "5m", "10m", "15m", "30m"]:
            r = horizons.get(h, {})
            marker = "OK" if r.get("replaced") else "--"
            logger.info(
                "  [%s] %s  cv_acc=%.4f  old_acc=%.4f",
                marker, h,
                r.get("cv_acc", 0.0),
                r.get("old_acc", 0.0),
            )
    else:
        err = result.get("error", "알 수 없음")
        logger.error("재학습 실패: %s", err)
        if "부족" in str(err):
            logger.error(
                "→ weeks_back을 늘리거나 backfill_features.py를 실행하여 피처 DB를 채우세요."
            )
        # 재학습이 실패해도 캠페인 판정 리포트(읽기 전용)는 실행할 가치가 있다
        if _campaign_due(args.campaign):
            _run_campaign_steps()
        sys.exit(1)

    logger.info("=" * 60)
    logger.info("완료. pkl 저장 위치: %s", os.path.join(BASE_DIR, "model", "horizons"))

    # ── [260705 검증 캠페인] 주간 스텝 (금요일 자동 / --campaign 강제) ─────
    if _campaign_due(args.campaign):
        _run_campaign_steps()


def _campaign_due(flag):
    """--campaign 명시 > 금요일 자동. None=자동 판단."""
    if flag is not None:
        return bool(flag)
    return datetime.date.today().weekday() == 4  # 금요일


def _run_campaign_steps():
    """[260705 검증 캠페인] 주간 검증 스텝 체인 자동화.

    docs/260705_OFFENSE_READINESS_AUDIT_AND_NEXT_PHASE.md §4-1.
    각 스텝은 서브프로세스로 격리 — 하나가 실패해도 나머지는 계속 실행한다.

    순서가 중요하다:
      1) 게이트 ablation 리포트 (읽기 전용)
      2) 검증 캠페인 판정 리포트 — 반드시 섀도우 TB 재학습 **전에** 실행해야
         이번 주 데이터가 지난주 모델 기준 OOS로 평가된다 (§3-1 OOS 보장:
         리포트가 모델 파일 mtime 이후 ts만 평가하므로, 재학습을 먼저 돌리면
         mtime이 오늘로 갱신돼 평가 표본이 0이 된다)
      3) 섀도우 TB 재학습 (다음 주 평가용 모델 갱신)
      4) 분위 회귀 재학습
      5) 격주(짝수 ISO 주차): MAE/MFE 배리어 적정성 분석
    """
    import subprocess

    steps = [
        ("게이트 ablation 리포트", ["generate_gate_ablation_report.py", "--days", "7"]),
        ("검증 캠페인 판정 리포트", ["generate_validation_campaign_report.py"]),
        ("섀도우 TB 재학습", ["run_shadow_triple_barrier_retrain.py"]),
        ("분위 회귀 재학습", ["train_quantile_regressor.py"]),
    ]
    if datetime.date.today().isocalendar()[1] % 2 == 0:
        steps.append(("MAE/MFE 분석", ["analyze_mae_mfe.py"]))

    script_dir = os.path.dirname(os.path.abspath(__file__))
    logger.info("=" * 60)
    logger.info("[검증 캠페인] 주간 스텝 %d개 실행 (§4-1)", len(steps))
    summary = []
    for name, cmd in steps:
        script_path = os.path.join(script_dir, cmd[0])
        if not os.path.exists(script_path):
            logger.warning("[검증 캠페인] %s — 스크립트 없음: %s", name, script_path)
            summary.append((name, "MISSING"))
            continue
        try:
            proc = subprocess.run(
                [sys.executable, script_path] + cmd[1:],
                cwd=BASE_DIR,
                timeout=1800,  # 스텝당 최대 30분
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            )
            ok = proc.returncode == 0
            tail = (proc.stdout or b"")[-2000:].decode("utf-8", errors="replace")
            logger.info("[검증 캠페인] %s → %s (rc=%d)\n%s",
                        name, "완료" if ok else "실패", proc.returncode, tail)
            summary.append((name, "OK" if ok else "FAIL(rc=%d)" % proc.returncode))
        except subprocess.TimeoutExpired:
            logger.error("[검증 캠페인] %s — 30분 타임아웃", name)
            summary.append((name, "TIMEOUT"))
        except Exception as e:
            logger.error("[검증 캠페인] %s — 실행 오류: %s", name, e)
            summary.append((name, "ERROR"))

    logger.info("[검증 캠페인] 요약: %s",
                " | ".join("%s=%s" % (n, s) for n, s in summary))
    logger.info("판정 리포트: %s",
                os.path.join(BASE_DIR, "data", "validation_campaign_report.md"))
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
