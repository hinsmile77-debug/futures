# challenger/variants/exhaustion_regime.py — 방안 D: 탈진 레짐 추가
"""
4가지 동시 조건 충족 시 탈진 레짐 발동 → Hurst H < 0.45 차단 무효화.

발동 조건:
  ① atr > avg_atr × 1.5          (변동성 확대 중)
  ② cvd_exhaustion > 0            (CVD 탈진 감지)
  ③ ofi_reversal_speed > 0.8σ    (OFI 급반전)
  ④ abs(vwap_position) > 1.5     (VWAP 밴드 크게 이탈)

탈진 레짐 파라미터:
  min_confidence  = 0.56
  size_mult       = 0.70
  entry_direction = TOWARD_VWAP (VWAP 방향으로 역추세)
  hurst_override  = True
"""
import math
from collections import deque
from typing import Dict, Any

from challenger.variants.base_challenger import BaseChallenger, ChallengerSignal


class ExhaustionRegimeChallenger(BaseChallenger):
    challenger_id = "D_EXHAUSTION_REGIME"
    name_kr       = "탈진레짐"

    ATR_MULT         = 1.5
    VWAP_BAND_MIN    = 1.5
    MIN_CONFIDENCE   = 0.56
    SIZE_MULT        = 0.70
    OFI_SPEED_WIN    = 20   # OFI 반전 속도 σ 계산 윈도우

    def __init__(self):
        super(ExhaustionRegimeChallenger, self).__init__()
        self._ofi_speed_buf = deque(maxlen=self.OFI_SPEED_WIN)

    def generate_signal(self, features, context):
        # type: (Dict[str, Any], Dict[str, Any]) -> ChallengerSignal
        ts = context.get("ts", "")

        atr         = float(context.get("atr", 1.0) or 1.0)
        avg_atr     = float(features.get("atr_avg", atr) or atr)
        cvd_exh     = float(features.get("cvd_exhaustion", 0.0) or 0.0)
        ofi_speed   = float(features.get("ofi_reversal_speed", 0.0) or 0.0)
        vwap_pos    = float(features.get("vwap_position", 0.0) or 0.0)
        vwap_val    = float(features.get("vwap", 0.0) or 0.0)
        close_price = float(context.get("candle", {}).get("close", 0) or 0)

        self._ofi_speed_buf.append(ofi_speed)
        ofi_sigma = self._compute_sigma(list(self._ofi_speed_buf))

        # 4가지 탈진 레짐 조건
        cond1 = avg_atr > 0 and atr > avg_atr * self.ATR_MULT
        cond2 = cvd_exh > 0
        cond3 = ofi_sigma > 0 and abs(ofi_speed) > ofi_sigma * 0.8
        cond4 = abs(vwap_pos) > self.VWAP_BAND_MIN

        direction  = 0
        confidence = 0.0
        grade      = "X"
        meta       = {}

        if cond1 and cond2 and cond3 and cond4:
            # TOWARD_VWAP: VWAP 방향으로 역추세
            if vwap_pos < 0 and close_price < vwap_val:
                direction = 1   # 롱 (VWAP 위로 회귀)
            elif vwap_pos > 0 and close_price > vwap_val:
                direction = -1  # 숏 (VWAP 아래로 회귀)

            if direction != 0:
                # 4가지 조건 충족도에 따른 신뢰도
                confidence = self.MIN_CONFIDENCE + 0.02 * sum([cond1, cond2, cond3, cond4])
                grade      = self._grade_from_confidence(confidence)
                meta = {
                    "atr":             round(atr, 4),
                    "avg_atr":         round(avg_atr, 4),
                    "cvd_exhaustion":  round(cvd_exh, 3),
                    "ofi_speed":       round(ofi_speed, 6),
                    "ofi_sigma":       round(ofi_sigma, 6),
                    "vwap_position":   round(vwap_pos, 3),
                    "hurst_override":  True,
                    "entry_mode":      "MEAN_REVERSION",
                    "size_mult":       self.SIZE_MULT,
                }

        return ChallengerSignal(
            ts            = ts,
            challenger_id = self.challenger_id,
            direction     = direction,
            confidence    = round(confidence, 4),
            grade         = grade,
            entry_price   = close_price if direction != 0 else None,
            signal_meta   = meta,
        )

    @staticmethod
    def _compute_sigma(buf):
        # type: (list) -> float
        if len(buf) < 3:
            return 1e-9
        n   = len(buf)
        avg = sum(buf) / n
        var = sum((x - avg) ** 2 for x in buf) / n
        return math.sqrt(var) if var > 0 else 1e-9
