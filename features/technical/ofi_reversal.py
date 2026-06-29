# features/technical/ofi_reversal.py — OFI 반전 속도 계산기
"""
OfiReversalCalculator: OFI 반전 속도 + 0.8σ 임계값 계산.

feature_builder.py 에서 호출:
    result = self.ofi_reversal.compute(ofi_raw, avg_volume)
    features["ofi_reversal_speed"]   = result["reversal_speed"]
    features["bull_reversal_signal"] = result["bull_reversal_signal"]

bull_reversal_signal: 매도 우세 → 매수 우세 급반전 (LONG 방향 이벤트)
bear_reversal_signal: 삭제됨 (일평균 10봉/일 희소 이진 신호 — 260617)
"""
import math
from collections import deque
from typing import Dict, Optional


class OfiReversalCalculator(object):
    """OFI 반전 속도 계산기 (피처 빌더용)"""

    SIGMA_WIN     = 20     # 롤링 σ 계산 윈도우
    SIGMA_MULT    = 0.8    # 0.8σ 임계값
    COOLDOWN_BARS = 5      # 발동 후 최소 쿨다운 (분봉)

    def __init__(self):
        self._ofi_buf       = deque(maxlen=self.SIGMA_WIN + 5)
        self._speed_buf     = deque(maxlen=self.SIGMA_WIN)
        self._prev_ofi      = None   # type: Optional[float]
        self._bull_cooldown = 0      # 잔여 쿨다운 봉수

    def compute(self, ofi_raw, avg_volume):
        # type: (float, float) -> Dict[str, float]
        """
        Args:
            ofi_raw:    현재 분봉 OFI raw 값
            avg_volume: 평균 거래량 (정규화용)

        Returns:
            {"reversal_speed": float, "speed_sigma": float,
             "signal": 0/1, "ofi_avg_3m": float}
        """
        ofi_raw    = float(ofi_raw)
        avg_volume = float(avg_volume) or 1.0

        self._ofi_buf.append(ofi_raw)

        prev     = self._prev_ofi if self._prev_ofi is not None else ofi_raw
        speed    = (ofi_raw - prev) / (avg_volume + 1e-9)
        self._speed_buf.append(speed)
        self._prev_ofi = ofi_raw

        ofi_list = list(self._ofi_buf)
        speed_sigma = self._sigma(list(self._speed_buf))

        # 직전 3분 평균 (자신 제외)
        ofi_avg_3m = 0.0
        if len(ofi_list) >= 4:
            ofi_avg_3m = sum(ofi_list[-4:-1]) / 3.0

        threshold  = self._sigma(ofi_list) * self.SIGMA_MULT
        speed_cond = abs(speed) > speed_sigma * self.SIGMA_MULT

        # 쿨다운 카운터 소진
        if self._bull_cooldown > 0:
            self._bull_cooldown -= 1

        # warmup 미완료(σ 불안정) 또는 쿨다운 중이면 신호 억제
        warmup_done = len(self._ofi_buf) >= self.SIGMA_WIN

        bull_reversal_signal = 0
        if warmup_done and self._bull_cooldown == 0:
            # bull_reversal: 매도 우세 → 매수 우세 급반전 (LONG 방향 이벤트)
            if ofi_avg_3m < -threshold and ofi_raw > 0 and speed_cond:
                bull_reversal_signal = 1
                self._bull_cooldown  = self.COOLDOWN_BARS

        return {
            "reversal_speed":       round(speed, 8),
            "speed_sigma":          round(speed_sigma, 8),
            "bull_reversal_signal": bull_reversal_signal,
            "ofi_avg_3m":           round(ofi_avg_3m, 2),
        }

    @staticmethod
    def _sigma(buf):
        if len(buf) < 3:
            return 1e-9
        n   = len(buf)
        avg = sum(buf) / n
        var = sum((x - avg) ** 2 for x in buf) / n
        return math.sqrt(var) if var > 0 else 1e-9

    def reset_daily(self):
        self._ofi_buf.clear()
        self._speed_buf.clear()
        self._prev_ofi      = None
        self._bull_cooldown = 0
