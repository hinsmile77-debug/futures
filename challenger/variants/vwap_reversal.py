# challenger/variants/vwap_reversal.py — 방안 C: VWAP 밴드 반전 모드
"""
VWAP 2σ 이탈 후 탈진 상태 = 역추세 매수 신호.

조건:
  vwap_position < -1.5  (VWAP 하방 1.5σ 초과)
  cvd_exhaustion > 0    (CVD 탈진 감지)
  close < vwap          (VWAP 아래에 있음)

entry_mode = "MEAN_REVERSION" 태깅
"""
from typing import Dict, Any

from challenger.variants.base_challenger import BaseChallenger, ChallengerSignal


class VwapReversalChallenger(BaseChallenger):
    challenger_id = "C_VWAP_REVERSAL"
    name_kr       = "VWAP 반전모드"

    VWAP_BAND_THRESHOLD  = -1.5   # σ 이탈 임계값
    CVD_EXHAUSTION_MIN   = 0.0    # cvd_exhaustion 최소값 (존재만 해도 OK)

    def generate_signal(self, features, context):
        # type: (Dict[str, Any], Dict[str, Any]) -> ChallengerSignal
        ts             = context.get("ts", "")
        vwap_position  = float(features.get("vwap_position", 0.0) or 0.0)
        cvd_exhaustion = float(features.get("cvd_exhaustion", 0.0) or 0.0)
        close_price    = float(context.get("candle", {}).get("close", 0) or 0)
        vwap_val       = float(features.get("vwap", close_price) or close_price)

        direction  = 0
        confidence = 0.0
        grade      = "X"
        meta       = {}

        # 매수 역추세 조건
        cond_vwap = vwap_position < self.VWAP_BAND_THRESHOLD
        cond_cvd  = cvd_exhaustion >= self.CVD_EXHAUSTION_MIN
        cond_pos  = close_price < vwap_val  # 아직 VWAP 아래

        if cond_vwap and cond_cvd and cond_pos:
            # 이탈 깊이에 비례한 신뢰도 (최대 0.72)
            depth      = abs(vwap_position) - 1.5   # 1.5σ 초과분
            confidence = min(0.55 + depth * 0.05 + cvd_exhaustion * 0.05, 0.72)
            direction  = 1
            grade      = self._grade_from_confidence(confidence)
            meta = {
                "vwap_position":  round(vwap_position, 3),
                "cvd_exhaustion": round(cvd_exhaustion, 3),
                "entry_mode":     "MEAN_REVERSION",
                "close":          close_price,
                "vwap":           round(vwap_val, 2),
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
