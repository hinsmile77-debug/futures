# strategy/entry/position_sizer.py — 켈리 포지션 사이즈 계산
"""
설계 명세 8-4:
  최종 수량 = 기본리스크 × 신뢰도배수 × 레짐배수 / (ATR × 1.5 × pt_value)

  기본 리스크: 계좌의 1%
  신뢰도 배수: 0.6 ~ 1.5
  레짐 배수:   RISK_ON=1.0 / NEUTRAL=0.8 / RISK_OFF=0.5
  미니선물:    켈리 산출값이 3 미만이면 3으로 올림 (최소 3계약)
"""
import logging
from typing import Optional

from config.constants import FUTURES_PT_VALUE, MINI_FUTURES_PT_VALUE
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


MINI_MIN_CONTRACTS = 3   # 미니선물 최소 진입 계약 수


class PositionSizer:
    """켈리 기반 포지션 사이즈 계산기"""

    def __init__(self, account_balance: float = 0, pt_value: float = FUTURES_PT_VALUE):
        self.account_balance = account_balance
        self._pt_value = float(pt_value)

    def set_pt_value(self, pt_value: float) -> None:
        self._pt_value = float(pt_value)

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
        core_health_mult: float = 1.0,
        brier_mult: float = 1.0,
        restart_mult: float = 1.0,
        dna_mult: float = 1.0,
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
            core_health_mult:    [5순위] CORE 건강 배수 (0.0/0.5/1.0)
            brier_mult:          [2순위] Brier 과신 패널티 배수 (0.5/1.0)
            restart_mult:        [3순위] 재시작 루프 브레이커 배수 (0.0/0.5/1.0)
            dna_mult:            [4순위] 장초반 DNA 조심 배수 (0.25/1.0)

        Returns:
            {quantity, base_risk, conf_mult, regime_mult, kelly_mult, stop_distance,
             core_health_mult, safety_note}
        """
        balance = self.account_balance if account_balance is None else account_balance

        # [5순위] CORE 건강 0점이면 진입 자체를 차단 (0계약 반환)
        if core_health_mult <= 0.0:
            logger.warning("[Sizer] CORE Health 점수 < 70 — 진입 차단 (0계약)")
            return {
                "quantity": 0,
                "base_risk": 0,
                "conf_mult": 0.0,
                "regime_mult": 0.0,
                "kelly_mult": 0.0,
                "stop_distance": atr * ATR_STOP_MULT,
                "core_health_mult": 0.0,
                "safety_note": "CORE Health 진입 차단",
            }

        # [3순위] 재시작 루프 완전 차단
        if restart_mult <= 0.0:
            logger.warning("[Sizer] 재시작 루프 브레이커 — 완전 관망 (0계약)")
            return {
                "quantity": 0,
                "base_risk": 0,
                "conf_mult": 0.0,
                "regime_mult": 0.0,
                "kelly_mult": 0.0,
                "stop_distance": atr * ATR_STOP_MULT,
                "core_health_mult": core_health_mult,
                "safety_note": "재시작 루프 브레이커 차단",
            }

        if balance <= 0:
            return {
                "quantity": 1,
                "base_risk": 0,
                "conf_mult": 1.0,
                "regime_mult": 1.0,
                "kelly_mult": 1.0,
                "stop_distance": atr * ATR_STOP_MULT,
                "core_health_mult": core_health_mult,
                "safety_note": "계좌 잔고 미설정 — 기본 1계약",
            }

        base_risk       = balance * ACCOUNT_BASE_RISK
        conf_mult       = _confidence_mult(confidence)
        regime_mult     = REGIME_SIZE_MULT.get(regime, 0.8)
        stop_distance   = atr * ATR_STOP_MULT

        stop_risk = stop_distance * self._pt_value

        is_mini = (self._pt_value <= MINI_FUTURES_PT_VALUE)
        min_qty = MINI_MIN_CONTRACTS if is_mini else 1

        safety_mults = core_health_mult * brier_mult * restart_mult * dna_mult
        safety_parts = []
        if core_health_mult < 1.0:
            safety_parts.append(f"CoreHealth×{core_health_mult}")
        if brier_mult < 1.0:
            safety_parts.append(f"Brier×{brier_mult}")
        if restart_mult < 1.0:
            safety_parts.append(f"Restart×{restart_mult}")
        if dna_mult < 1.0:
            safety_parts.append(f"DNA×{dna_mult}")
        safety_note = " ".join(safety_parts) if safety_parts else "정상"

        if stop_risk <= 0:
            quantity = min_qty
        else:
            raw_qty = (base_risk * conf_mult * regime_mult * grade_mult
                       * adaptive_kelly_mult * safety_mults) / stop_risk
            quantity = max(min_qty, min(int(raw_qty), MAX_CONTRACTS))

        logger.info(
            "[Sizer] %s선물 잔고=%s 기본리스크=%s 신뢰도배수=%s 레짐배수=%s "
            "안전배수=%.2f(%s) → %d계약 (최소=%d)",
            "미니" if is_mini else "일반",
            f"{balance:,.0f}", f"{base_risk:,.0f}",
            conf_mult, regime_mult,
            safety_mults, safety_note,
            quantity, min_qty,
        )

        return {
            "quantity":          quantity,
            "base_risk":         round(base_risk, 0),
            "conf_mult":         conf_mult,
            "regime_mult":       regime_mult,
            "kelly_mult":        adaptive_kelly_mult,
            "stop_distance":     round(stop_distance, 4),
            "core_health_mult":  core_health_mult,
            "safety_note":       safety_note,
        }

    def calc_size(
        self,
        balance: float,
        price: float,
        atr: float,
        size_mult: float = 1.0,
        regime: str = "NEUTRAL",
        confidence: float = 0.5,
    ) -> int:
        """entry_manager 호출용 래퍼 — 계약 수(int)만 반환."""
        result = self.compute(
            confidence=confidence,
            atr=atr,
            regime=regime,
            grade_mult=size_mult,
            account_balance=balance,
        )
        return result["quantity"]
