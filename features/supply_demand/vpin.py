# features/supply_demand/vpin.py — VPIN (Volume-Synchronized Probability of Informed Trading) ⭐v7.0
"""
VPIN = |매수 거래량 - 매도 거래량| / 총 거래량  (volume bucket 기준)

2010 Flash Crash를 사전에 유일하게 감지한 지표 (Easley et al. 2012).
VPIN이 높을수록 정보거래자(큰 손)가 활발히 참여 중 → 큰 움직임 임박.

v7.0 Gemini 제안:
  VPIN > 0.7 → 큰 움직임 임박 (방향 불문)
  VPIN > 0.9 (90%ile 도달) → 자동 진입 필수 조건으로 설정

계산 방법:
  1. Volume Bucket: 총 거래량 / 50 크기로 버킷 분할
  2. 각 버킷에서 매수/매도량 추정 (틱 규칙 기반)
  3. VPIN = 최근 50버킷 |V_buy - V_sell| 이동평균 / 버킷 크기

기대 효과: 자동 진입 정확도 +5%
"""
import numpy as np
from collections import deque
from typing import Optional


class VPINCalculator:
    """VPIN 실시간 계산기"""

    BUCKET_COUNT = 50   # 이동 평균 버킷 수 (논문 표준)

    def __init__(self, bucket_size: int = 1000):
        """
        Args:
            bucket_size: 버킷 1개당 목표 거래량 (계약 수)
                        KOSPI200 선물: 일평균 거래량 / 50 권장 (~500~2000)
        """
        self.bucket_size = bucket_size

        # 현재 버킷 누적
        self._bucket_vol_buy  = 0.0
        self._bucket_vol_sell = 0.0
        self._bucket_vol_tot  = 0.0

        # 완성된 버킷 버퍼 (최근 50개)
        self._bucket_buf = deque(maxlen=self.BUCKET_COUNT)

        # 히스토리 (90%ile 계산용)
        self._vpin_history = deque(maxlen=500)

        # 이전 틱 가격 (틱 규칙용)
        self._prev_price: Optional[float] = None

    def update_tick(self, price: float, volume: float) -> Optional[dict]:
        """
        체결 틱 업데이트

        Args:
            price:  체결가
            volume: 체결량 (계약 수)

        Returns:
            버킷 완성 시 VPIN 결과, 아니면 None
        """
        # 틱 규칙: 가격 상승 → 매수, 하락 → 매도, 동일 → 이전과 동일
        if self._prev_price is None:
            direction = 1
        elif price > self._prev_price:
            direction = 1
        elif price < self._prev_price:
            direction = -1
        else:
            direction = getattr(self, '_last_direction', 1)

        self._last_direction = direction
        self._prev_price     = price

        # 버킷에 거래량 누적
        if direction == 1:
            self._bucket_vol_buy  += volume
        else:
            self._bucket_vol_sell += volume
        self._bucket_vol_tot += volume

        # 버킷 완성 체크
        if self._bucket_vol_tot >= self.bucket_size:
            return self._complete_bucket()

        return None

    def _complete_bucket(self) -> dict:
        """버킷 완성 → VPIN 계산"""
        imbalance = abs(self._bucket_vol_buy - self._bucket_vol_sell)
        self._bucket_buf.append(imbalance)

        # VPIN
        if len(self._bucket_buf) >= 10:
            vpin = float(np.mean(list(self._bucket_buf))) / (self.bucket_size + 1e-9)
            vpin = float(np.clip(vpin, 0.0, 1.0))
        else:
            vpin = 0.0

        self._vpin_history.append(vpin)

        # 90%ile 계산 (충분한 샘플이 있을 때)
        vpin_90pct = float(np.percentile(list(self._vpin_history), 90)) if len(self._vpin_history) >= 20 else 0.5

        # 신호 분류
        if vpin >= 0.9 or (len(self._vpin_history) >= 20 and vpin >= vpin_90pct):
            signal_level = "EXTREME"   # 진입 필수 조건 (v7.0)
            alert        = True
        elif vpin >= 0.7:
            signal_level = "HIGH"      # 큰 움직임 임박
            alert        = True
        elif vpin >= 0.5:
            signal_level = "MODERATE"
            alert        = False
        else:
            signal_level = "LOW"
            alert        = False

        # 버킷 초기화
        self._bucket_vol_buy  = 0.0
        self._bucket_vol_sell = 0.0
        self._bucket_vol_tot  = 0.0

        return {
            "vpin":          round(vpin, 4),           # CORE 피처값
            "vpin_90pct":    round(vpin_90pct, 4),
            "signal_level":  signal_level,
            "alert":         alert,
            "bucket_count":  len(self._bucket_buf),
        }

    def get_current_vpin(self) -> float:
        """가장 최근 VPIN 값 반환 (버킷 미완성 시에도)"""
        if not self._vpin_history:
            return 0.0
        return float(self._vpin_history[-1])

    def reset_daily(self):
        self._bucket_vol_buy  = 0.0
        self._bucket_vol_sell = 0.0
        self._bucket_vol_tot  = 0.0
        self._bucket_buf.clear()
        self._vpin_history.clear()
        self._prev_price      = None


if __name__ == "__main__":
    import random
    random.seed(42)

    calc = VPINCalculator(bucket_size=500)
    price = 390.0
    results = []

    # 정보거래 급증 시나리오: 한 방향으로 연속 체결
    for i in range(200):
        if i < 100:
            # 초반: 랜덤 (낮은 VPIN)
            price += random.gauss(0, 0.1)
            vol    = random.randint(5, 20)
        else:
            # 후반: 매수 편향 (높은 VPIN)
            price += abs(random.gauss(0.05, 0.05))
            vol    = random.randint(30, 100)

        r = calc.update_tick(price=price, volume=vol)
        if r:
            results.append(r)
            print(f"[버킷 {len(results)}] VPIN={r['vpin']:.4f} | {r['signal_level']} | alert={r['alert']}")
