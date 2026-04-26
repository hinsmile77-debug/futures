# strategy/entry/vol_targeting.py — 변동성 표적화 (Volatility Targeting)
"""
포지션 사이즈를 실현 변동성에 역비례하게 조정.
목표: 포트폴리오 변동성을 항상 일정 수준(target_vol)으로 유지.

Risk Parity / AQR 방식:
  size = (target_vol / realized_vol) × base_size

  변동성 높을 때 → 사이즈 축소 (MDD 방어)
  변동성 낮을 때 → 사이즈 확대 (Sharpe 개선)

KOSPI200 선물 기준:
  1분봉 ATR을 일간 변동성으로 환산 (×√390 ≈ KOSPI 거래 분)
  목표 일간 변동성 기본: 2% (조정 가능)

기대 효과: Sharpe +0.4
"""
import numpy as np
from collections import deque
from typing import Optional


TRADING_MINUTES_PER_DAY = 390   # KOSPI 정규 거래 시간 분


class VolatilityTargeter:
    """
    실현 변동성 기반 포지션 사이즈 조정기

    1분봉 ATR → 일간 변동성 환산 → 목표 변동성 대비 사이즈 결정
    """

    def __init__(
        self,
        target_vol_daily: float = 0.02,   # 목표 일간 변동성 (2%)
        vol_window:       int   = 20,     # 실현 변동성 계산 창 (분)
        max_mult:         float = 1.5,    # 최대 사이즈 배율
        min_mult:         float = 0.2,    # 최소 사이즈 배율 (급변장 방어)
    ):
        """
        Args:
            target_vol_daily: 목표 일간 변동성 (소수점, 0.02 = 2%)
            vol_window:       실현 변동성 계산 분봉 수
            max_mult:         사이즈 상한 배율
            min_mult:         사이즈 하한 배율
        """
        self.target_vol  = target_vol_daily
        self.vol_window  = vol_window
        self.max_mult    = max_mult
        self.min_mult    = min_mult

        self._returns_buf = deque(maxlen=vol_window)
        self._prev_close: Optional[float] = None

        # 최근 변동성 히스토리
        self._vol_history = deque(maxlen=100)

    def push_1m_close(self, close: float) -> Optional[dict]:
        """
        1분봉 종가 입력 → 사이즈 배율 계산

        Args:
            close: 1분봉 종가

        Returns:
            {realized_vol_daily, size_multiplier, regime_vol} or None (데이터 부족)
        """
        if self._prev_close is not None:
            ret = (close - self._prev_close) / (self._prev_close + 1e-9)
            self._returns_buf.append(ret)

        self._prev_close = close

        if len(self._returns_buf) < max(5, self.vol_window // 2):
            return None

        return self._compute()

    def _compute(self) -> dict:
        """실현 변동성 → 사이즈 배율 계산"""
        rets = np.array(list(self._returns_buf))

        # 1분봉 실현 변동성 → 일간 변동성 환산
        vol_1m       = float(np.std(rets))
        vol_daily    = vol_1m * np.sqrt(TRADING_MINUTES_PER_DAY)

        self._vol_history.append(vol_daily)

        # 사이즈 배율: target / realized (역비례)
        if vol_daily < 1e-6:
            mult = self.max_mult
        else:
            mult = self.target_vol / vol_daily

        mult = float(np.clip(mult, self.min_mult, self.max_mult))

        # 변동성 레짐 분류
        vol_avg = float(np.mean(list(self._vol_history))) if len(self._vol_history) >= 5 else vol_daily
        if vol_daily > vol_avg * 2.0:
            vol_regime = "급변장"
        elif vol_daily > vol_avg * 1.3:
            vol_regime = "고변동"
        elif vol_daily < vol_avg * 0.7:
            vol_regime = "저변동"
        else:
            vol_regime = "보통"

        return {
            "realized_vol_1m":    round(vol_1m * 100, 4),    # %
            "realized_vol_daily": round(vol_daily * 100, 4),  # %
            "target_vol_daily":   round(self.target_vol * 100, 2),
            "size_multiplier":    round(mult, 3),              # CORE 출력
            "vol_regime":         vol_regime,
        }

    def get_size_multiplier(self) -> float:
        """
        최근 계산된 사이즈 배율 반환 (즉시 접근용)
        데이터 부족 시 1.0 (기본) 반환
        """
        if not self._vol_history:
            return 1.0
        vol = list(self._vol_history)[-1]
        mult = self.target_vol / (vol + 1e-9)
        return float(np.clip(mult, self.min_mult, self.max_mult))

    def reset_daily(self):
        self._returns_buf.clear()
        self._prev_close = None
        # vol_history는 일간 지속 유지 (변동성 이력 필요)


if __name__ == "__main__":
    import random
    random.seed(42)

    vt = VolatilityTargeter(target_vol_daily=0.02)
    price = 390.0

    print("=== 저변동 구간 (사이즈 확대) ===")
    for i in range(25):
        price += random.gauss(0, 0.05)   # 소폭 변동
        r = vt.push_1m_close(price)
        if r:
            print(f"[{i+1:02d}분] 일간변동성={r['realized_vol_daily']:.3f}%, "
                  f"배율={r['size_multiplier']:.3f}, 레짐={r['vol_regime']}")

    print("\n=== 급변 구간 (사이즈 축소) ===")
    for i in range(10):
        price += random.gauss(0, 1.5)   # 대폭 변동
        r = vt.push_1m_close(price)
        if r:
            print(f"[{i+26:02d}분] 일간변동성={r['realized_vol_daily']:.3f}%, "
                  f"배율={r['size_multiplier']:.3f}, 레짐={r['vol_regime']}")
