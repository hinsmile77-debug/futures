# backtest/transaction_cost.py — KOSPI200 선물 거래 비용 정밀 계산
"""
🔴 [MW0601 493차 후속8 / 2026-08-26] **이 모듈은 두 군데가 틀려 있었다.**

이 파일을 import 하는 코드는 저장소 어디에도 없다(테스트 포함) — 그래서 아무 손해도
나지 않았지만, 잘못된 가정이 남아 있으면 다음 사람이 그대로 쓴다. 바로잡는다.

① **승수** — `FUTURES_MULTIPLIER`(정규선물 250,000)를 썼다. 미륵이가 매매하는 종목은
   **미니선물(A0569, 승수 50,000)** 이다. 그대로 쓰면 비용이 **5배 과대**가 된다.
   ⇒ `config/constants.py:get_contract_spec()` 단일 원천으로 교체.

② **수수료 모델** — 「KRX 계약당 720원 + 위탁 0.015bp」는 **키움 세대 가정**이다.
   대신증권 공식 고시(2026-08-26 확인)는 **「거래금액에 관계없이 0.0098104%」** 이며,
   **정액 성분이 없다.** 39거래일 회귀 실측이 그것을 독립 확인했다 —
   레그당 고정비 **+0.08원 ≈ 0**, R²=1.000000(493차 후속5).
   ⇒ 계약당 정액 수수료를 **0 으로** 두고 요율 단일 항으로 계산한다.

계산: 비용 = 약정대금 × FUTURES_COMMISSION_RATE (편도) · 거래세 없음
예: 미니 1계약 @1040pt → 약정대금 5,200만원 → 편도 5,101원 / 왕복 10,202원
"""
import logging
from config.settings import FUTURES_COMMISSION_RATE, active_contract_spec
from config.constants import MINI_FUTURES_PT_VALUE

logger = logging.getLogger(__name__)

# [493차 후속8] 고시 요율에 **정액 성분이 없다**(39거래일 회귀 실측 확인).
# 값을 지우지 않고 0 으로 두는 이유: 브로커가 바뀌어 정액이 생기면 여기에 넣으라는
# 자리 표시다(계측 4원칙 — "없다"와 "안 쟀다"를 구분해 두는 것과 같은 취지).
KRX_FEE_PER_CONTRACT   = 0          # 원/계약 — 현행 브로커는 정액 성분 없음
BROKERAGE_RATE_DEFAULT = FUTURES_COMMISSION_RATE   # 0.0098104% 편도 (공식 고시)


def _pt_value():
    """계약 승수 — 종목코드가 정한다. 정규선물 기본값으로 떨어지지 않는다."""
    spec = active_contract_spec()
    return float(spec["pt_value"]) if (spec and spec.get("pt_value")) else float(MINI_FUTURES_PT_VALUE)


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
        contract_value   = price * _pt_value() * qty
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
        return round(cost_per_contract / _pt_value(), 4)

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
