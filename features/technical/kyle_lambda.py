# features/technical/kyle_lambda.py — Kyle's Lambda (가격충격계수, Kyle 1985) ⭐320차
"""
Kyle's Lambda — 순매수 흐름(signed order flow) 단위당 가격이 얼마나 움직이는지 측정하는
시장 유동성 지표. λ가 클수록 시장이 얇아(유동성 부족) 작은 주문에도 가격이 크게 움직임.

CVD/OFI가 "매수/매도 중 어느 쪽이 우세한가"(방향)를 보는 지표라면, kyle_lambda는
"그 방향 압력이 가격을 얼마나 밀어올리는가"(유동성/가격충격)라는 별도 차원을 잡는다.

계산: 최근 N개 분봉의 (분당 가격변화, 분당 순매수량) 쌍에 대한 단순회귀 기울기.

  Δprice_i = λ * net_volume_i + ε
  λ = Σ((x_i - x̄)(y_i - ȳ)) / Σ((x_i - x̄)²)     (x=net_volume, y=Δprice)

틱 단위 체결 데이터가 아니라 분봉 단위(close·buy_vol·sell_vol)만으로 계산 — VPIN처럼
브로커 레이어의 틱 콜백 배선이 필요 없어 회귀 위험이 낮다.
"""
from collections import deque
from typing import Optional

import numpy as np


class KyleLambdaCalculator:
    """분봉 단위 Kyle's Lambda 실시간 계산기"""

    def __init__(self, window: int = 20):
        self.window = window
        self._min_samples = max(5, window // 4)
        self._net_vol_buf: deque = deque(maxlen=window)
        self._dprice_buf: deque = deque(maxlen=window)
        self._prev_close: Optional[float] = None

    def update(self, close: float, buy_vol: float, sell_vol: float) -> dict:
        """
        분봉 확정마다 호출.

        Returns:
            {kyle_lambda, ready} — 표본 부족 시 kyle_lambda=0.0, ready=False
        """
        if self._prev_close is None or close <= 0:
            self._prev_close = close if close > 0 else self._prev_close
            return {"kyle_lambda": 0.0, "ready": False}

        d_price = close - self._prev_close
        net_vol = float(buy_vol) - float(sell_vol)
        self._prev_close = close

        self._dprice_buf.append(d_price)
        self._net_vol_buf.append(net_vol)

        if len(self._net_vol_buf) < self._min_samples:
            return {"kyle_lambda": 0.0, "ready": False}

        x = np.array(self._net_vol_buf, dtype=float)
        y = np.array(self._dprice_buf, dtype=float)
        x_dev = x - x.mean()
        denom = float(np.dot(x_dev, x_dev))
        if denom < 1e-9:
            return {"kyle_lambda": 0.0, "ready": True}

        lam = float(np.dot(x_dev, y - y.mean()) / denom)
        return {"kyle_lambda": lam, "ready": True}

    def reset_daily(self) -> None:
        self._net_vol_buf.clear()
        self._dprice_buf.clear()
        self._prev_close = None


if __name__ == "__main__":
    import random
    random.seed(7)

    calc = KyleLambdaCalculator(window=20)
    price = 390.0

    # 얇은 시장 시나리오: 작은 순매수량에도 가격이 크게 반응 (λ 큼)
    for i in range(25):
        net = random.uniform(-50, 50)
        price += net * 0.01 + random.gauss(0, 0.02)
        buy = max(net, 0) + 100
        sell = max(-net, 0) + 100
        r = calc.update(close=price, buy_vol=buy, sell_vol=sell)
        if i % 5 == 0:
            print(f"[{i:02d}] price={price:.2f} kyle_lambda={r['kyle_lambda']:+.5f} ready={r['ready']}")
