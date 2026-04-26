# backtest/performance_metrics.py — 성과 지표 계산
"""
Walk-Forward 및 백테스트 성과 지표:
  - Sharpe Ratio (연간화, 하루 평균 6회 거래 기준)
  - Maximum Drawdown (MDD)
  - 승률 (Win Rate)
  - Profit Factor
  - Calmar Ratio

Phase 2 실전 진입 기준:
  Sharpe ≥ 1.5 / MDD ≤ 15% / 승률 ≥ 53%
"""
import numpy as np
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

TRADING_DAYS_YEAR   = 250
AVG_TRADES_PER_DAY  = 6     # 연간화 환산 기준


class PerformanceMetrics:
    """성과 지표 계산기."""

    def __init__(self, risk_free_rate: float = 0.035):
        """
        Args:
            risk_free_rate: 연간 무위험 이자율 (기본 3.5%, 한국 단기채 기준)
        """
        self.risk_free_rate = risk_free_rate

    def compute(
        self,
        trades: List[dict],
        equity_curve: Optional[List[float]] = None,
    ) -> dict:
        """
        전체 성과 지표 계산.

        Args:
            trades: [{"pnl_krw": float, "win": bool (선택)}, ...]
                    "win" 없으면 pnl_krw > 0 을 win으로 판단
            equity_curve: 자산 곡선 (선택, 없으면 trades에서 생성)

        Returns:
            total_trades, win_trades, loss_trades, win_rate,
            sharpe, mdd_krw, mdd_pct, profit_factor, calmar,
            total_pnl_krw, avg_win_krw, avg_loss_krw,
            pass_sharpe, pass_mdd, pass_winrate
        """
        if not trades:
            return self._empty()

        pnl_list = [t["pnl_krw"] for t in trades]
        wins   = [t for t in trades if t.get("win", t["pnl_krw"] > 0)]
        losses = [t for t in trades if not t.get("win", t["pnl_krw"] > 0)]

        n_total = len(trades)
        n_win   = len(wins)
        n_loss  = len(losses)

        win_rate = n_win / n_total

        avg_win  = float(np.mean([t["pnl_krw"] for t in wins]))  if wins   else 0.0
        avg_loss = float(np.mean([t["pnl_krw"] for t in losses])) if losses else 0.0

        gross_profit = sum(t["pnl_krw"] for t in wins)
        gross_loss   = abs(sum(t["pnl_krw"] for t in losses))
        profit_factor = gross_profit / max(gross_loss, 1)

        if equity_curve is None:
            equity_curve = list(np.cumsum([0.0] + pnl_list))

        sharpe          = self._sharpe(pnl_list)
        mdd_krw, mdd_pct = self._max_drawdown(equity_curve)

        total_return   = sum(pnl_list)
        # 연간 수익 추정: 일 거래수 기준 연간화
        trades_per_year = TRADING_DAYS_YEAR * AVG_TRADES_PER_DAY
        annual_return   = total_return * (trades_per_year / max(n_total, 1))
        calmar          = annual_return / max(abs(mdd_krw), 1)

        return {
            "total_trades":   n_total,
            "win_trades":     n_win,
            "loss_trades":    n_loss,
            "win_rate":       round(win_rate, 4),
            "sharpe":         round(sharpe, 3),
            "mdd_krw":        round(mdd_krw),
            "mdd_pct":        round(mdd_pct, 4),
            "profit_factor":  round(profit_factor, 3),
            "calmar":         round(calmar, 3),
            "total_pnl_krw":  round(total_return),
            "avg_win_krw":    round(avg_win),
            "avg_loss_krw":   round(avg_loss),
            "pass_sharpe":    sharpe   >= 1.5,
            "pass_mdd":       abs(mdd_pct) <= 0.15,
            "pass_winrate":   win_rate >= 0.53,
        }

    def check_phase2_criteria(self, metrics: dict) -> dict:
        """
        Phase 2 실전 진입 기준 충족 여부.

        기준: Sharpe ≥ 1.5 / MDD ≤ 15% / 승률 ≥ 53%
        세 가지 모두 충족해야 실전 진입 가능.
        """
        pass_all = (
            metrics["pass_sharpe"] and
            metrics["pass_mdd"]    and
            metrics["pass_winrate"]
        )
        return {
            "pass_all":     pass_all,
            "pass_sharpe":  metrics["pass_sharpe"],
            "pass_mdd":     metrics["pass_mdd"],
            "pass_winrate": metrics["pass_winrate"],
            "verdict":      "실전 진입 가능" if pass_all else "추가 개선 필요",
        }

    # ── 내부 계산 ──────────────────────────────────────────────

    def _sharpe(self, pnl_list: List[float]) -> float:
        """연간화 Sharpe Ratio."""
        if len(pnl_list) < 2:
            return 0.0
        arr = np.array(pnl_list, dtype=float)
        mu  = arr.mean()
        std = arr.std()
        if std == 0:
            return 0.0
        daily_rf    = self.risk_free_rate / TRADING_DAYS_YEAR
        per_trade_rf = daily_rf / AVG_TRADES_PER_DAY
        sharpe_per_trade = (mu - per_trade_rf) / std
        # 연간화: sqrt(거래 횟수/연)
        annual_factor = np.sqrt(TRADING_DAYS_YEAR * AVG_TRADES_PER_DAY)
        return float(sharpe_per_trade * annual_factor)

    @staticmethod
    def _max_drawdown(equity_curve: List[float]):
        """최대 낙폭 (원화 절대값, 비율)."""
        arr  = np.array(equity_curve, dtype=float)
        peak = np.maximum.accumulate(arr)
        dd   = arr - peak
        mdd_krw = float(dd.min())

        peak_max  = float(peak.max())
        initial   = abs(arr[0]) if arr[0] != 0 else 1.0
        base      = max(peak_max, initial)
        mdd_pct   = mdd_krw / base if base > 0 else 0.0

        return mdd_krw, mdd_pct

    @staticmethod
    def _empty() -> dict:
        return {
            "total_trades": 0, "win_trades": 0, "loss_trades": 0,
            "win_rate": 0.0, "sharpe": 0.0,
            "mdd_krw": 0, "mdd_pct": 0.0,
            "profit_factor": 0.0, "calmar": 0.0,
            "total_pnl_krw": 0, "avg_win_krw": 0, "avg_loss_krw": 0,
            "pass_sharpe": False, "pass_mdd": True, "pass_winrate": False,
        }
