# backtest/transaction_cost.py — KOSPI200 선물 거래 비용 정밀 계산
"""
KOSPI200 선물 거래 비용 구성:
  ① KRX 거래소 수수료: 계약당 약 720원 (단방향)
  ② 증권사 위탁 수수료: 계약금액 × 0.015bp (협의 기본값)
  ③ 거래세: 없음 (주식선물·ETF 아닌 KOSPI200 지수선물)

FUTURES_MULTIPLIER = 500,000원/pt
예: 지수 400pt → 계약금액 2억원
  KRX 수수료:      720원
  증권사 수수료:   2억 × 0.00015 = 30,000원
  왕복 합계:       (720 + 30,000) × 2 ≒ 61,440원
"""
import logging
from config.constants import FUTURES_MULTIPLIER

logger = logging.getLogger(__name__)

KRX_FEE_PER_CONTRACT   = 720        # 원/계약, 단방향
BROKERAGE_RATE_DEFAULT = 0.00015    # 계약금액 대비 (0.015bp)


class TransactionCost:
    """
    거래 비용 계산기.

    단방향 기준으로 계산하며, 왕복은 calc_round_trip() 사용.
    """

    def __init__(
        self,
        brokerage_rate: float = BROKERAGE_RATE_DEFAULT,
        krx_fee: float = KRX_FEE_PER_CONTRACT,
    ):
        self.brokerage_rate = brokerage_rate
        self.krx_fee        = krx_fee

    def calc_one_way(self, price: float, qty: int = 1) -> dict:
        """
        단방향(편도) 거래 비용 계산.

        Args:
            price: 체결 가격 (pt)
            qty:   계약 수

        Returns:
            total_krw, krx_fee, brokerage_fee, tax, contract_value
        """
        contract_value   = price * FUTURES_MULTIPLIER * qty
        krx_total        = self.krx_fee * qty
        brokerage_total  = contract_value * self.brokerage_rate
        tax              = 0.0   # 선물 거래세 없음

        return {
            "total_krw":      round(krx_total + brokerage_total + tax),
            "krx_fee":        round(krx_total),
            "brokerage_fee":  round(brokerage_total),
            "tax":            0,
            "contract_value": round(contract_value),
        }

    def calc_round_trip(self, price: float, qty: int = 1) -> dict:
        """왕복 거래 비용 (진입 + 청산)."""
        one = self.calc_one_way(price, qty)
        return {
            "total_krw":      one["total_krw"] * 2,
            "krx_fee":        one["krx_fee"] * 2,
            "brokerage_fee":  one["brokerage_fee"] * 2,
            "tax":            0,
            "contract_value": one["contract_value"],
        }

    def cost_in_points(self, price: float, qty: int = 1) -> float:
        """
        왕복 비용을 pt 단위로 환산.

        PnL 계산 시 차감용:
          실현 PnL(pt) - cost_in_points() = 순 PnL(pt)
        """
        rt = self.calc_round_trip(price, qty)
        cost_per_contract = rt["total_krw"] / qty
        return round(cost_per_contract / FUTURES_MULTIPLIER, 4)

    def effective_slippage_pts(
        self,
        price: float,
        slip_pts: float,
        qty: int = 1,
    ) -> float:
        """
        슬리피지 + 수수료 합산 순비용 (pt).

        슬리피지 시뮬레이터와 조합하여 사용.
        """
        return round(slip_pts + self.cost_in_points(price, qty), 4)
