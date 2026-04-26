# backtest/walk_forward.py — Walk-Forward 검증
"""
Walk-Forward 검증 (슬라이딩 윈도우):
  학습 창: 8주 (TRAIN_WEEKS)
  검증 창: 1주 (TEST_WEEKS)
  최소 26주 데이터 필요 (MIN_WEEKS)

  반복 예시 (26주 데이터):
    창1: 학습W1~W8 / 검증W9
    창2: 학습W2~W9 / 검증W10
    ...
    창18: 학습W18~W25 / 검증W26

  평균 Sharpe ≥ 1.5, 평균 MDD ≤ 15%, 평균 승률 ≥ 53% 모두 통과해야 실전 진입.
"""
import logging
from typing import List
import numpy as np

from backtest.performance_metrics import PerformanceMetrics

logger = logging.getLogger(__name__)

TRAIN_WEEKS = 8
TEST_WEEKS  = 1
MIN_WEEKS   = 26


class WalkForwardValidator:
    """
    Walk-Forward 검증기.

    입력 형식:
      weekly_trades: [
        [{"pnl_krw": float, "win": bool}, ...],   # 1주차 거래 목록
        [...],                                       # 2주차
        ...
      ]
    """

    def __init__(
        self,
        train_weeks: int = TRAIN_WEEKS,
        test_weeks:  int = TEST_WEEKS,
    ):
        self.train_weeks  = train_weeks
        self.test_weeks   = test_weeks
        self.metrics_calc = PerformanceMetrics()

    def run(self, weekly_trades: List[List[dict]]) -> dict:
        """
        Walk-Forward 검증 실행.

        Returns:
            passed:         최종 통과 여부
            total_windows:  검증 창 수
            windows:        창별 상세 성과
            avg_metrics:    평균 성과 지표
            criteria_check: Phase 2 기준 충족 여부
        """
        n_weeks = len(weekly_trades)
        if n_weeks < MIN_WEEKS:
            logger.warning(
                "[WalkForward] 데이터 부족: %d주 < %d주 (최소 필요)",
                n_weeks, MIN_WEEKS,
            )
            return {
                "passed":  False,
                "reason":  f"데이터 부족 ({n_weeks}/{MIN_WEEKS}주)",
                "windows": [],
            }

        windows = []
        start   = 0
        idx     = 0

        while start + self.train_weeks + self.test_weeks <= n_weeks:
            train_end = start + self.train_weeks
            test_end  = train_end + self.test_weeks

            # 검증 구간 거래 취합
            test_trades = []
            for week in weekly_trades[train_end:test_end]:
                test_trades.extend(week)

            if test_trades:
                metrics = self.metrics_calc.compute(test_trades)
                windows.append({
                    "window":      idx + 1,
                    "train_range": "W%d~W%d" % (start + 1, train_end),
                    "test_range":  "W%d~W%d" % (train_end + 1, test_end),
                    "metrics":     metrics,
                })
                idx += 1

            start += self.test_weeks

        if not windows:
            return {"passed": False, "reason": "검증 창 없음", "windows": []}

        avg_metrics = self._average_metrics(windows)
        criteria    = self.metrics_calc.check_phase2_criteria(avg_metrics)

        logger.info(
            "[WalkForward] %d개 창 검증 완료 | Sharpe=%.2f MDD=%.1f%% 승률=%.1f%%",
            len(windows),
            avg_metrics["sharpe"],
            abs(avg_metrics["mdd_pct"]) * 100,
            avg_metrics["win_rate"] * 100,
        )

        return {
            "passed":         criteria["pass_all"],
            "total_windows":  len(windows),
            "windows":        windows,
            "avg_metrics":    avg_metrics,
            "criteria_check": criteria,
        }

    def summary_report(self, result: dict) -> str:
        """콘솔 출력용 요약 텍스트."""
        if not result.get("windows"):
            return "[WalkForward] %s" % result.get("reason", "실패")

        avg  = result["avg_metrics"]
        crit = result["criteria_check"]
        mark = lambda ok: "✓" if ok else "✗"

        lines = [
            "=" * 54,
            "  Walk-Forward 검증 결과  (%d개 창)" % result["total_windows"],
            "=" * 54,
            "  평균 Sharpe: %5.2f  %s  (기준 ≥ 1.5)" % (
                avg["sharpe"], mark(avg["pass_sharpe"])),
            "  평균 MDD:    %5.1f%%  %s  (기준 ≤ 15%%)" % (
                abs(avg["mdd_pct"]) * 100, mark(avg["pass_mdd"])),
            "  평균 승률:   %5.1f%%  %s  (기준 ≥ 53%%)" % (
                avg["win_rate"] * 100, mark(avg["pass_winrate"])),
            "  총 거래:     %d회" % avg["total_trades"],
            "  총 손익:     %s원" % "{:,}".format(avg["total_pnl_krw"]),
            "-" * 54,
            "  최종 판정: %s" % crit["verdict"],
            "=" * 54,
        ]
        return "\n".join(lines)

    # ── 내부 헬퍼 ─────────────────────────────────────────────

    def _average_metrics(self, windows: List[dict]) -> dict:
        """창별 평균 성과 계산."""
        metric_keys = ["sharpe", "mdd_pct", "win_rate", "profit_factor", "total_pnl_krw"]
        avg = {}
        for k in metric_keys:
            vals = [w["metrics"].get(k, 0.0) for w in windows]
            avg[k] = round(float(np.mean(vals)), 4)

        avg["total_trades"] = sum(w["metrics"].get("total_trades", 0) for w in windows)
        avg["win_trades"]   = sum(w["metrics"].get("win_trades",   0) for w in windows)
        avg["loss_trades"]  = avg["total_trades"] - avg["win_trades"]

        # 평균값 기준 기준 통과 여부
        avg["pass_sharpe"]  = avg["sharpe"]          >= 1.5
        avg["pass_mdd"]     = abs(avg["mdd_pct"])    <= 0.15
        avg["pass_winrate"] = avg["win_rate"]         >= 0.53

        return avg
