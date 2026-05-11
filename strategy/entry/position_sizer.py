# strategy/entry/position_sizer.py — 켈리 포지션 사이즈 계산
"""
설계 명세 8-4:
  최종 수량 = 기본리스크 × 신뢰도배수 × 레짐배수 / (ATR × 1.5 × 250,000)

  기본 리스크: 계좌의 1%
  신뢰도 배수: 0.6 ~ 1.5
  레짐 배수:   RISK_ON=1.0 / NEUTRAL=0.8 / RISK_OFF=0.5
"""
import logging
from typing import Optional

from config.settings import (
    ACCOUNT_BASE_RISK, ATR_STOP_MULT, REGIME_SIZE_MULT, MAX_CONTRACTS,
)

logger = logging.getLogger("TRADE")

# 신뢰도 → 배수 매핑
CONFIDENCE_MULT_TABLE = [
    (0.70, 1.5),
    (0.65, 1.2),
    (0.60, 1.0),
    (0.58, 0.8),
    (0.00, 0.6),
]


def _confidence_mult(confidence: float) -> float:
    for threshold, mult in CONFIDENCE_MULT_TABLE:
        if confidence >= threshold:
            return mult
    return 0.6


class PositionSizer:
    """켈리 기반 포지션 사이즈 계산기"""

    def __init__(self, account_balance: float = 0):
        self.account_balance = account_balance

    def set_account_balance(self, account_balance: Optional[float]) -> None:
        try:
            balance = float(account_balance or 0.0)
        except Exception:
            return
        if balance > 0:
            self.account_balance = balance

    def compute(
        self,
        confidence: float,
        atr: float,
        regime: str = "NEUTRAL",
        grade_mult: float = 1.0,
        adaptive_kelly_mult: float = 1.0,
        account_balance: Optional[float] = None,
    ) -> dict:
        """
        포지션 사이즈 계산

        Args:
            confidence:          앙상블 신뢰도
            atr:                 현재 ATR
            regime:              매크로 레짐
            grade_mult:          진입 등급 배수 (A=1.5, B=1.0, C=0.6)
            adaptive_kelly_mult: 적응형 켈리 배수
            account_balance:     계좌 잔고 (None이면 self.account_balance 사용)

        Returns:
            {quantity, base_risk, conf_mult, regime_mult, kelly_mult, stop_distance}
        """
        balance = self.account_balance if account_balance is None else account_balance
        if balance <= 0:
            return {
                "quantity": 1,
                "base_risk": 0,
                "conf_mult": 1.0,
                "regime_mult": 1.0,
                "kelly_mult": 1.0,
                "stop_distance": atr * ATR_STOP_MULT,
                "note": "계좌 잔고 미설정 — 기본 1계약",
            }

        base_risk       = balance * ACCOUNT_BASE_RISK
        conf_mult       = _confidence_mult(confidence)
        regime_mult     = REGIME_SIZE_MULT.get(regime, 0.8)
        stop_distance   = atr * ATR_STOP_MULT

        # 선물 1틱 = 250,000원, stop_distance는 포인트 기준
        tick_value = 250_000  # 0.05pt × 5,000,000 / 계약
        stop_risk  = stop_distance * tick_value * 20  # 20틱/pt 환산

        if stop_risk <= 0:
            quantity = 1
        else:
            raw_qty = (base_risk * conf_mult * regime_mult * grade_mult
                       * adaptive_kelly_mult) / stop_risk
            quantity = max(1, min(int(raw_qty), MAX_CONTRACTS))

        logger.info(
            f"[Sizer] 잔고={balance:,.0f} 기본리스크={base_risk:,.0f} "
            f"신뢰도배수={conf_mult} 레짐배수={regime_mult} "
            f"→ {quantity}계약"
        )

        return {
            "quantity":      quantity,
            "base_risk":     round(base_risk, 0),
            "conf_mult":     conf_mult,
            "regime_mult":   regime_mult,
            "kelly_mult":    adaptive_kelly_mult,
            "stop_distance": round(stop_distance, 4),
        }
