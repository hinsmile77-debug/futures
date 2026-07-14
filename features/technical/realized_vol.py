# features/technical/realized_vol.py — 실현변동성(RV) 연율화 계산 ⭐328차
"""
RV(Realized Volatility) — 최근 N분봉 종가 로그수익률의 표준편차를 연율화한 값.
rv_iv_spread(RV - IV)의 RV 측 입력.

IV(내재변동성) 측은 Cybos OptionMst 개별 종목 IV 필드(HeaderValue 108)가 "추정" 단계로만
문서화돼 있고(dev_memory/CYBOS_OPTION_PROBE_2026-05-13.md, scripts/collect_option_metrics.py의
HV_IV=108 주석 "내재변동성 — 종목별 상이, 추정") 실측 교차검증 로그가 없어 그대로 신뢰하기
위험하다. 대신 main.py가 260704 감사 이후 이미 실시간 폴링·운영해 온 VKOSPI 지수(KRX 공식
KOSPI200 내재변동성 지수, main.py:_last_vkospi → basis_data["vkospi"])를 IV 프록시로
재사용한다 — rv_iv_spread 계산은 feature_builder.py에서 이 RV 값과 vkospi를 뺀다.

연율화: 1분봉 로그수익률 표준편차 × sqrt(거래일당 분봉수 × 연간 거래일수) × 100(%)
"""
from collections import deque
from typing import Optional

import numpy as np

TRADING_MINUTES_PER_DAY = 390   # KOSPI 정규 거래시간 분 (strategy/entry/vol_targeting.py와 동일값)
TRADING_DAYS_PER_YEAR = 252


class RealizedVolCalculator:
    """1분봉 종가 기반 연율화 실현변동성(%) 계산기."""

    def __init__(self, window: int = 30):
        self.window = window
        self._min_samples = max(5, window // 3)
        self._returns_buf: deque = deque(maxlen=window)
        self._prev_close: Optional[float] = None
        self._annualize_factor = float(np.sqrt(TRADING_MINUTES_PER_DAY * TRADING_DAYS_PER_YEAR))

    def update(self, close: float) -> dict:
        """
        분봉 확정마다 호출.

        Returns:
            {realized_vol_ann, ready} — 표본 부족 시 realized_vol_ann=0.0, ready=False
        """
        if close <= 0:
            return {"realized_vol_ann": 0.0, "ready": False}
        if self._prev_close is None or self._prev_close <= 0:
            self._prev_close = close
            return {"realized_vol_ann": 0.0, "ready": False}

        ret = float(np.log(close / self._prev_close))
        self._prev_close = close
        self._returns_buf.append(ret)

        if len(self._returns_buf) < self._min_samples:
            return {"realized_vol_ann": 0.0, "ready": False}

        vol_1m = float(np.std(np.array(self._returns_buf)))
        rv_ann_pct = vol_1m * self._annualize_factor * 100.0
        return {"realized_vol_ann": rv_ann_pct, "ready": True}

    def reset_daily(self) -> None:
        self._returns_buf.clear()
        self._prev_close = None


if __name__ == "__main__":
    import random
    random.seed(11)

    calc = RealizedVolCalculator(window=30)
    price = 390.0

    print("=== 저변동 구간 ===")
    for i in range(35):
        price += random.gauss(0, 0.05)
        r = calc.update(price)
        if i % 5 == 0:
            print(f"[{i:02d}] price={price:.2f} rv_ann={r['realized_vol_ann']:.3f}% ready={r['ready']}")

    print("\n=== 급변 구간 ===")
    for i in range(15):
        price += random.gauss(0, 1.2)
        r = calc.update(price)
        if i % 5 == 0:
            print(f"[{i:02d}] price={price:.2f} rv_ann={r['realized_vol_ann']:.3f}% ready={r['ready']}")
