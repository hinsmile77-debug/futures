# scripts/qa_strategy_seeder.py — Phase 5 QA 검증 + 더미 데이터 시드
"""
미륵이 전략 레지스트리 시스템의 QA 검증 및 더미 데이터 초기 적재 스크립트.

사용법:
  python scripts/qa_strategy_seeder.py --seed        # 더미 3개 버전 생성
  python scripts/qa_strategy_seeder.py --validate    # 판정 로직 QA
  python scripts/qa_strategy_seeder.py --report      # 현재 상태 리포트 출력
  python scripts/qa_strategy_seeder.py --all         # 전체 실행

검증 항목 (§11-9):
  1. OUTPERFORM / NORMAL / UNDERPERFORM 판정 정확성
  2. active 버전 단독 확인 (중복 없음)
  3. 직전 버전 링크 연속성
  4. stage 결과 누락 시 graceful fallback
  5. KEEP/WATCH/REPLACE_CANDIDATE/ROLLBACK_REVIEW 액션 결정
  6. 교체 직후 / 교체 실패 / 롤백 후보 케이스 QA
"""
from __future__ import annotations

import argparse
import logging
import os
import sys

# 프로젝트 루트를 경로에 추가
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("qa_seeder")

# ─── 더미 시나리오 데이터 ─────────────────────────────────────────────────────
_SEED_SCENARIOS = [
    {
        "version":    "v1.0",
        "note":       "초기 버전 — 시스템 첫 가동",
        "wfa_metrics": {
            "sharpe":        1.42,
            "mdd_pct":       0.142,
            "win_rate":      0.532,
            "profit_factor": 1.21,
        },
        "bt_metrics": {
            "sharpe":        1.65,
            "mdd_pct":       0.118,
            "win_rate":      0.558,
            "profit_factor": 1.38,
        },
        "changed_params": {},
        "live_snapshots": [
            {"win_rate": 0.521, "total_trades": 12, "daily_pnl": -45000,  "profit_factor": 1.05},
            {"win_rate": 0.543, "total_trades": 14, "daily_pnl":  72000,  "profit_factor": 1.28},
            {"win_rate": 0.551, "total_trades": 11, "daily_pnl":  38000,  "profit_factor": 1.19},
            {"win_rate": 0.532, "total_trades": 13, "daily_pnl": -21000,  "profit_factor": 0.97},
            {"win_rate": 0.529, "total_trades": 15, "daily_pnl":  55000,  "profit_factor": 1.22},
        ],
    },
    {
        "version":    "v1.1",
        "note":       "entry_conf_neutral 0.58→0.60, atr_tp2_mult 1.5→2.0",
        "wfa_metrics": {
            "sharpe":        1.63,
            "mdd_pct":       0.125,
            "win_rate":      0.541,
            "profit_factor": 1.31,
        },
        "bt_metrics": {
            "sharpe":        1.88,
            "mdd_pct":       0.112,
            "win_rate":      0.558,
            "profit_factor": 1.42,
        },
        "changed_params": {
            "entry_conf_neutral": {"from": 0.58, "to": 0.60},
            "atr_tp2_mult":       {"from": 1.50, "to": 2.00},
        },
        "live_snapshots": [
            {"win_rate": 0.553, "total_trades": 14, "daily_pnl":  88000,  "profit_factor": 1.35},
            {"win_rate": 0.571, "total_trades": 12, "daily_pnl": 102000,  "profit_factor": 1.48},
            {"win_rate": 0.562, "total_trades": 15, "daily_pnl":  75000,  "profit_factor": 1.39},
            {"win_rate": 0.548, "total_trades": 13, "daily_pnl":  61000,  "profit_factor": 1.28},
            {"win_rate": 0.563, "total_trades": 16, "daily_pnl":  95000,  "profit_factor": 1.41},
        ],
    },
    {
        "version":    "v1.2",
        "note":       "kelly_half_factor 0.50→0.45, hurst_trend_threshold 0.62→0.65",
        "wfa_metrics": {
            "sharpe":        1.78,
            "mdd_pct":       0.108,
            "win_rate":      0.556,
            "profit_factor": 1.44,
        },
        "bt_metrics": {
            "sharpe":        2.01,
            "mdd_pct":       0.095,
            "win_rate":      0.572,
            "profit_factor": 1.55,
        },
        "changed_params": {
            "kelly_half_factor":       {"from": 0.50, "to": 0.45},
            "hurst_trend_threshold":   {"from": 0.62, "to": 0.65},
        },
        "live_snapshots": [
            {"win_rate": 0.569, "total_trades": 13, "daily_pnl": 115000, "profit_factor": 1.52},
            {"win_rate": 0.582, "total_trades": 11, "daily_pnl": 138000, "profit_factor": 1.61},
        ],
    },
]


# ─── 시드 실행 ────────────────────────────────────────────────────────────────
def run_seed() -> None:
    """더미 전략 버전 3개를 StrategyRegistry에 적재."""
    from config.strategy_registry import get_registry

    reg = get_registry()
    logger.info("=== 더미 데이터 시드 시작 ===")

    for scenario in _SEED_SCENARIOS:
        ver = scenario["version"]
        try:
            reg.register_version(
                version        = ver,
                changed_params = scenario["changed_params"],
                wfa_metrics    = scenario["wfa_metrics"],
                note           = scenario["note"],
                bt_metrics     = scenario["bt_metrics"],
            )
            logger.info("  [SEED] %s 등록 완료", ver)
        except Exception as e:
            logger.warning("  [SEED] %s 등록 실패: %s", ver, e)

        # live snapshot 적재
        for snap in scenario.get("live_snapshots", []):
            try:
                reg.record_live_snapshot(version=ver, metrics=snap)
            except Exception as e:
                logger.warning("  [SEED] %s live snapshot 실패: %s", ver, e)

        logger.info("  [SEED] %s live snapshot %d개 적재", ver, len(scenario.get("live_snapshots", [])))

    logger.info("=== 시드 완료 ===")


# ─── QA 검증 ─────────────────────────────────────────────────────────────────
def run_validate() -> bool:
    """
    전략 레지스트리 시스템 QA 검증.

    Returns:
        True = 전체 통과, False = 1개 이상 실패
    """
    from config.strategy_registry import get_registry, VERDICT_OUTPERFORM, VERDICT_NORMAL, VERDICT_UNDERPERFORM
    from strategy.ops.verdict_engine import compute_action, ACTION_KEEP, ACTION_WATCH, ACTION_REPLACE_CANDIDATE, ACTION_ROLLBACK_REVIEW

    reg    = get_registry()
    passed = 0
    failed = 0

    def _check(label: str, cond: bool, detail: str = "") -> None:
        nonlocal passed, failed
        if cond:
            logger.info("  [PASS] %s %s", label, detail)
            passed += 1
        else:
            logger.error("  [FAIL] %s %s", label, detail)
            failed += 1

    logger.info("=== QA 검증 시작 ===")

    # ── 1. active 버전 단 1개 ─────────────────────────────────────────────
    curr = reg.get_current_version()
    _check("active 버전 존재", curr is not None)
    all_vers = reg.get_all_versions()
    active_count = sum(1 for v in all_vers if v.get("is_current") or (curr and v["version"] == curr.get("version")))
    _check("active 버전 중복 없음", active_count <= 1, "(count=%d)" % active_count)

    # ── 2. 직전 버전 링크 연속성 ─────────────────────────────────────────
    if curr:
        prev_ver = curr.get("previous_version")
        if prev_ver:
            prev_info = reg.get_version(prev_ver)
            _check("직전 버전 링크 유효", prev_info is not None, "(prev=%s)" % prev_ver)
        else:
            _check("최초 버전 (prev 없음)", True)

    # ── 3. stage 누락 시 graceful fallback ───────────────────────────────
    _check("stage 누락 시 UI 안깨짐", curr is not None and "stages" in (curr or {}))

    # ── 4. 판정 로직 검증 (더미 데이터 직접 테스트) ───────────────────────
    _verdicts = [
        # (verdict, drift_lv, days, psi_lv, expected_action)
        (VERDICT_OUTPERFORM,   0, 10, 0, ACTION_KEEP),
        (VERDICT_OUTPERFORM,   1, 10, 0, ACTION_WATCH),
        (VERDICT_NORMAL,       0, 10, 0, ACTION_KEEP),
        (VERDICT_NORMAL,       1, 10, 0, ACTION_WATCH),
        (VERDICT_UNDERPERFORM, 0,  3, 0, ACTION_WATCH),         # 유예 기간
        (VERDICT_UNDERPERFORM, 0, 10, 0, ACTION_REPLACE_CANDIDATE),
        (VERDICT_UNDERPERFORM, 2, 10, 0, ACTION_ROLLBACK_REVIEW),
        (VERDICT_NORMAL,       3, 10, 0, ACTION_ROLLBACK_REVIEW),  # CRITICAL drift
    ]
    for verdict, drift_lv, days, psi_lv, expected in _verdicts:
        action, _ = compute_action(verdict, drift_lv, days, psi_lv)
        _check(
            "판정→액션 %s+Drift%d+%dd" % (verdict[:5], drift_lv, days),
            action == expected,
            "→ %s (expected %s)" % (action, expected),
        )

    # ── 5. 교체 직후 모니터링 케이스 ─────────────────────────────────────
    if curr:
        days_active = curr.get("live_days", 0)
        _check("신규 버전 운용 일수 >= 0", days_active >= 0, "(%d일)" % days_active)

    # ── 6. 롤백 경보 메시지 생성 ─────────────────────────────────────────
    try:
        from strategy.ops.verdict_engine import rollback_alert_message
        msg = rollback_alert_message("v1.2", VERDICT_UNDERPERFORM, 2, ACTION_ROLLBACK_REVIEW, "테스트", -100000)
        _check("롤백 경보 메시지 생성", len(msg) > 20)
    except Exception as e:
        _check("롤백 경보 메시지 생성", False, str(e))

    # ── 7. DailyExporter 리포트 생성 ─────────────────────────────────────
    try:
        from strategy.ops.daily_exporter import DailyExporter
        report = DailyExporter().build_report()
        _check("DailyExporter 리포트 생성", "리포트" in report)
    except Exception as e:
        _check("DailyExporter 리포트 생성", False, str(e))

    # ── 8. RegimeFingerprint 싱글턴 ──────────────────────────────────────
    try:
        from strategy.regime_fingerprint import get_fingerprint
        fp = get_fingerprint()
        _check("RegimeFingerprint 싱글턴", fp is not None)
    except Exception as e:
        _check("RegimeFingerprint 싱글턴", False, str(e))

    # ── 결과 출력 ─────────────────────────────────────────────────────────
    total = passed + failed
    logger.info("=== QA 결과: %d/%d 통과 %s ===", passed, total,
                "✓ PASS" if failed == 0 else "✗ FAIL(%d개)" % failed)
    return failed == 0


# ─── 리포트 출력 ─────────────────────────────────────────────────────────────
def run_report() -> None:
    """현재 전략 상태 리포트를 출력하고 파일 저장."""
    from strategy.ops.daily_exporter import get_exporter
    exp    = get_exporter()
    report = exp.build_report()
    try:
        print(report)
    except UnicodeEncodeError:
        import sys
        sys.stdout.buffer.write((report + "\n").encode("utf-8", errors="replace"))
    path = exp.save(report)
    logger.info("리포트 저장: %s", path)


# ─── CLI ─────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        description="미륵이 전략 레지스트리 QA + 더미 데이터 시드"
    )
    parser.add_argument("--seed",     action="store_true", help="더미 버전 3개 생성")
    parser.add_argument("--validate", action="store_true", help="판정 로직 QA 실행")
    parser.add_argument("--report",   action="store_true", help="현재 상태 리포트 출력")
    parser.add_argument("--all",      action="store_true", help="seed + validate + report 전체 실행")
    args = parser.parse_args()

    if args.all or args.seed:
        run_seed()

    if args.all or args.validate:
        ok = run_validate()
        if not ok:
            sys.exit(1)

    if args.all or args.report:
        run_report()

    if not any([args.seed, args.validate, args.report, args.all]):
        parser.print_help()


if __name__ == "__main__":
    main()
