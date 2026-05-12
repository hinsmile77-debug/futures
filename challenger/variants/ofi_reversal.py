# challenger/variants/ofi_reversal.py — 방안 B: OFI 반전 속도 감지
"""
OFI 부호 전환 + 전환 속도(가속도)로 신호 선행화.

반전 조건 (3가지 동시):
  ① ofi_avg[t-3:t-1] < -threshold  (직전 3분 매도 압도)
  ② ofi_raw[t] > 0                  (이번 분 매수 전환)
  ③ ofi_raw[t] > |ofi_raw[t-1]| × 0.5  (전환 강도 충분)

발화 예측: 분기점과 동시
"""
import math
from collections import deque
from typing import Dict, Any, Optional

from challenger.variants.base_challenger import BaseChallenger, ChallengerSignal

_SENTINEL = object()


class OfiReversalChallenger(BaseChallenger):
    challenger_id = "B_OFI_REVERSAL"
    name_kr       = "OFI 반전속도"

    SIGMA_WIN    = 20   # 0.8σ 임계값 계산 윈도우
    SIGMA_MULT   = 0.8
    OFI_AVG_WIN  = 3    # 직전 N분 OFI 평균

    def __init__(self):
        super(OfiReversalChallenger, self).__init__()
        self._ofi_buf       = deque(maxlen=self.SIGMA_WIN + 5)
        self._speed_buf     = deque(maxlen=self.SIGMA_WIN)  # 반전 속도 히스토리
        self._prev_ofi_raw  = None   # type: Optional[float]

    def generate_signal(self, features, context):
        # type: (Dict[str, Any], Dict[str, Any]) -> ChallengerSignal
        ts       = context.get("ts", "")
        ofi_raw  = float(features.get("ofi_raw", 0.0) or 0.0)
        avg_vol  = float(features.get("avg_volume", 1.0) or 1.0)

        self._ofi_buf.append(ofi_raw)

        # 반전 속도
        prev = self._prev_ofi_raw if self._prev_ofi_raw is not None else ofi_raw
        ofi_reversal_speed = (ofi_raw - prev) / (avg_vol + 1e-9)
        self._speed_buf.append(ofi_reversal_speed)
        self._prev_ofi_raw = ofi_raw

        direction  = 0
        confidence = 0.0
        grade      = "X"
        meta       = {}

        if len(self._ofi_buf) >= self.OFI_AVG_WIN + 1:
            ofi_list = list(self._ofi_buf)

            # 0.8σ 임계값
            threshold = self._compute_threshold(ofi_list)

            # ① 직전 3분 OFI 평균 < -threshold
            recent_avg = sum(ofi_list[-self.OFI_AVG_WIN-1:-1]) / self.OFI_AVG_WIN
            cond1 = recent_avg < -threshold

            # ② 이번 분 매수 전환
            cond2 = ofi_raw > 0

            # ③ 전환 강도 충분 (직전 절댓값의 50% 이상)
            prev_ofi = ofi_list[-2] if len(ofi_list) >= 2 else 0.0
            cond3    = ofi_raw > abs(prev_ofi) * 0.5

            if cond1 and cond2 and cond3:
                # 반전 속도 상대 강도
                speed_sigma = self._compute_speed_sigma()
                strength    = min(abs(ofi_reversal_speed) / (speed_sigma + 1e-9), 1.0) \
                              if speed_sigma > 0 else 0.5
                direction  = 1
                confidence = 0.55 + strength * 0.10
                grade      = self._grade_from_confidence(confidence)
                meta = {
                    "ofi_raw":            round(ofi_raw, 2),
                    "recent_avg":         round(recent_avg, 2),
                    "threshold":          round(threshold, 2),
                    "ofi_reversal_speed": round(ofi_reversal_speed, 6),
                    "speed_sigma":        round(speed_sigma, 6),
                }

        entry_price = float(context.get("candle", {}).get("close", 0) or 0)
        return ChallengerSignal(
            ts            = ts,
            challenger_id = self.challenger_id,
            direction     = direction,
            confidence    = round(confidence, 4),
            grade         = grade,
            entry_price   = entry_price if direction != 0 else None,
            signal_meta   = meta,
        )

    def _compute_threshold(self, ofi_list):
        # type: (list) -> float
        """0.8σ (20일 표준편차 기반)"""
        if len(ofi_list) < 5:
            return 100.0
        n   = len(ofi_list)
        avg = sum(ofi_list) / n
        var = sum((x - avg) ** 2 for x in ofi_list) / n
        return math.sqrt(var) * self.SIGMA_MULT if var > 0 else 100.0

    def _compute_speed_sigma(self):
        # type: () -> float
        buf = list(self._speed_buf)
        if len(buf) < 3:
            return 1e-9
        n   = len(buf)
        avg = sum(buf) / n
        var = sum((x - avg) ** 2 for x in buf) / n
        return math.sqrt(var) if var > 0 else 1e-9
