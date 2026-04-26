# backtest/slippage_simulator.py — 현실적 슬리피지 모델
"""
슬리피지 조정 인자:
  base_slip × ATR계수 × 레짐계수 × 시간대계수 × 만기계수 × 주문크기계수
  + LatencySync 연동 (지연 시 슬리피지 가중)

KOSPI200 선물 기준 기본 슬리피지: 0.5틱 (1틱 = 0.05pt)
"""
import datetime
import logging
from typing import Optional

from config.constants import FUTURES_TICK_SIZE, FUTURES_MULTIPLIER

logger = logging.getLogger(__name__)

# 기본 슬리피지 0.5틱
BASE_SLIP_TICKS = 0.5


class SlippageSimulator:
    """
    현실적 슬리피지 계산기.

    단방향(편도) 슬리피지 포인트 반환.
    왕복은 estimate_round_trip() 사용.
    """

    def get_slippage(
        self,
        atr: float,
        atr_mean: float,
        regime: str = "NEUTRAL",
        trade_time: Optional[datetime.time] = None,
        days_to_expiry: int = 5,
        order_qty: int = 1,
        latency_ms: float = 0.0,
    ) -> dict:
        """
        단방향 슬리피지 계산.

        Args:
            atr:            현재 ATR (pt)
            atr_mean:       평균 ATR (pt)
            regime:         레짐 ("RISK_ON" | "NEUTRAL" | "RISK_OFF")
            trade_time:     체결 시각
            days_to_expiry: 만기까지 남은 영업일
            order_qty:      주문 수량 (계약)
            latency_ms:     API 지연 (ms) — LatencySync 연동

        Returns:
            slip_pts:  슬리피지 포인트
            slip_krw:  슬리피지 원화 (1계약 기준)
            factors:   각 계수 상세
        """
        base = BASE_SLIP_TICKS * FUTURES_TICK_SIZE   # 0.025pt

        atr_factor     = self._atr_factor(atr, atr_mean)
        regime_factor  = self._regime_factor(regime)
        time_factor    = self._time_factor(trade_time)
        expiry_factor  = self._expiry_factor(days_to_expiry)
        size_factor    = self._size_factor(order_qty)
        latency_factor = self._latency_factor(latency_ms)

        slip_pts = (base
                    * atr_factor
                    * regime_factor
                    * time_factor
                    * expiry_factor
                    * size_factor
                    * latency_factor)

        slip_krw = slip_pts * FUTURES_MULTIPLIER

        return {
            "slip_pts": round(slip_pts, 4),
            "slip_krw": round(slip_krw),
            "factors": {
                "base_pts":  round(base, 4),
                "atr":       round(atr_factor, 3),
                "regime":    round(regime_factor, 3),
                "time":      round(time_factor, 3),
                "expiry":    round(expiry_factor, 3),
                "size":      round(size_factor, 3),
                "latency":   round(latency_factor, 3),
            },
        }

    def estimate_round_trip(
        self,
        atr: float,
        atr_mean: float,
        **kwargs,
    ) -> dict:
        """왕복 슬리피지 (진입 + 청산, 같은 조건 가정)."""
        single = self.get_slippage(atr, atr_mean, **kwargs)
        return {
            "slip_pts": round(single["slip_pts"] * 2, 4),
            "slip_krw": single["slip_krw"] * 2,
            "factors":  single["factors"],
        }

    # ── 각 계수 계산 ───────────────────────────────────────────

    @staticmethod
    def _atr_factor(atr: float, atr_mean: float) -> float:
        """ATR 계수: 변동성 비율에 비례, 0.5~3.0 클립."""
        if atr_mean <= 0:
            return 1.0
        ratio = atr / atr_mean
        return float(min(max(ratio, 0.5), 3.0))

    @staticmethod
    def _regime_factor(regime: str) -> float:
        """레짐 계수: RISK_OFF 시 슬리피지 증가."""
        return {"RISK_ON": 0.9, "NEUTRAL": 1.0, "RISK_OFF": 1.5}.get(regime, 1.0)

    @staticmethod
    def _time_factor(t: Optional[datetime.time]) -> float:
        """시간대별 유동성 계수."""
        if t is None:
            return 1.0
        total_min = t.hour * 60 + t.minute
        if 540 <= total_min < 550:   # 09:00~09:10 시초 급변
            return 2.0
        if 550 <= total_min < 570:   # 09:10~09:30 변동성 고조
            return 1.5
        if 900 <= total_min <= 910:  # 15:00~15:10 마감 변동
            return 1.8
        if 710 <= total_min < 780:   # 11:50~13:00 점심 유동성 저하
            return 1.3
        return 1.0

    @staticmethod
    def _expiry_factor(days: int) -> float:
        """만기 근접도 계수."""
        if days <= 1:
            return 2.0
        if days <= 2:
            return 1.5
        if days <= 5:
            return 1.2
        return 1.0

    @staticmethod
    def _size_factor(qty: int) -> float:
        """주문 크기 계수: 5계약 초과 시 5% 가중."""
        return 1.0 + max(qty - 5, 0) * 0.05

    @staticmethod
    def _latency_factor(latency_ms: float) -> float:
        """
        API 지연 기반 슬리피지 계수 (v7.0 Latency Watcher 연동).

        1000ms 이상 → 3배 (신호 차단 구간과 일치)
        300ms 이상  → 1.5배 (슬리피지 가중치 ×1.5)
        """
        if latency_ms >= 1000:
            return 3.0
        if latency_ms >= 300:
            return 1.5
        return 1.0
