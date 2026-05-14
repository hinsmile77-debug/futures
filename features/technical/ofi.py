# features/technical/ofi.py — Order Flow Imbalance ★ CORE-3
"""
OFI (Order Flow Imbalance)

호가창의 매수/매도 압력 불균형을 측정.
1~3분 방향을 가장 강하게 선행하는 지표.

계산 (Cont et al. 2014):
  e_t = ΔBid_Qty  if Bid_Price >= prev_Bid_Price else 0
      - ΔAsk_Qty  if Ask_Price <= prev_Ask_Price else 0

  OFI = Σ(e_t) 누적
  OFI_norm = OFI / total_volume  (정규화)
"""
import numpy as np
from collections import deque


class OFICalculator:
    """실시간 OFI (Order Flow Imbalance) 계산기"""

    WINDOW = 5  # 분봉 집계 창

    def __init__(self, window: int = 5):
        self.window = window
        self._ofi_buf  = deque(maxlen=window)
        self._vol_buf  = deque(maxlen=window)

        self._prev_bid_price = None
        self._prev_ask_price = None
        self._prev_bid_qty   = None
        self._prev_ask_qty   = None

        self._minute_ofi = 0.0
        self._minute_vol = 0.0

    def update_hoga(
        self,
        bid_price: float, bid_qty: int,
        ask_price: float, ask_qty: int,
    ) -> None:
        """
        호가 변경 이벤트 처리 (틱 단위)

        Args:
            bid_price, bid_qty: 매수 1호가 / 수량
            ask_price, ask_qty: 매도 1호가 / 수량
        """
        if self._prev_bid_price is None:
            self._prev_bid_price = bid_price
            self._prev_ask_price = ask_price
            self._prev_bid_qty   = bid_qty
            self._prev_ask_qty   = ask_qty
            return

        e = 0.0

        # 매수호가 변화
        if bid_price >= self._prev_bid_price:
            e += (bid_qty - self._prev_bid_qty)
        # else: 매수호가 하락 → 기여 없음

        # 매도호가 변화
        if ask_price <= self._prev_ask_price:
            e -= (ask_qty - self._prev_ask_qty)
        # else: 매도호가 상승 → 기여 없음

        self._minute_ofi += e
        self._minute_vol += (bid_qty + ask_qty) / 2.0

        self._prev_bid_price = bid_price
        self._prev_ask_price = ask_price
        self._prev_bid_qty   = bid_qty
        self._prev_ask_qty   = ask_qty

    def flush_minute(self) -> dict:
        """
        1분봉 마감 시 OFI 집계 후 버퍼 저장

        Returns:
            {ofi_raw, ofi_norm, ofi_ma, pressure, imbalance_ratio}
        """
        self._ofi_buf.append(self._minute_ofi)
        self._vol_buf.append(max(self._minute_vol, 1.0))

        result = self.compute()

        # 분 초기화
        self._minute_ofi = 0.0
        self._minute_vol = 0.0
        # 분봉 경계에서 _prev_* 리셋: 틱 없는 분봉 이후 첫 틱이
        # 이전 분의 stale 호가 대비 잘못된 delta를 누적하는 것을 방지한다.
        self._prev_bid_price = None
        self._prev_ask_price = None
        self._prev_bid_qty   = None
        self._prev_ask_qty   = None

        return result

    def compute(self) -> dict:
        """버퍼 기반 OFI 지표 계산"""
        if not self._ofi_buf:
            return {
                "ofi_raw":        0.0,
                "ofi_norm":       0.0,
                "ofi_ma":         0.0,
                "pressure":       0,
                "imbalance_ratio": 0.0,
            }

        ofi_raw = self._ofi_buf[-1]
        avg_vol = np.mean(list(self._vol_buf)) if self._vol_buf else 1.0

        # 정규화 OFI
        ofi_norm = ofi_raw / (avg_vol + 1e-9)
        ofi_norm = float(np.clip(ofi_norm, -3.0, 3.0))

        # 이동평균 OFI
        ofi_ma = float(np.mean(list(self._ofi_buf)))

        # 압력 방향: +1(매수)/−1(매도)/0
        pressure = 1 if ofi_raw > 0 else (-1 if ofi_raw < 0 else 0)

        # 불균형 비율 (0 ~ 1.0, 높을수록 강한 방향성)
        imbalance_ratio = min(abs(ofi_norm) / 3.0, 1.0)

        return {
            "ofi_raw":         round(ofi_raw, 2),
            "ofi_norm":        round(ofi_norm, 4),     # CORE 피처값
            "ofi_ma":          round(ofi_ma, 2),
            "pressure":        pressure,
            "imbalance_ratio": round(imbalance_ratio, 3),
        }

    def reset_daily(self):
        self._ofi_buf.clear()
        self._vol_buf.clear()
        self._minute_ofi = 0.0
        self._minute_vol = 0.0
        self._prev_bid_price = None
        self._prev_ask_price = None
        self._prev_bid_qty   = None
        self._prev_ask_qty   = None
