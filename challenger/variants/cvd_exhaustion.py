# challenger/variants/cvd_exhaustion.py — 방안 A: CVD 탈진 감지
"""
CVD가 신저점을 갱신하되, 낙폭 속도가 급감하는 순간 = 매도 에너지 소진.

탈진 조건 (3가지 동시 충족):
  ① cvd < cvd_20min_low           (CVD 20분 신저점 갱신)
  ② cvd_accel > 0                 (CVD 2차 미분 양전환 = 낙폭 둔화)
  ③ volume > avg_vol × 1.8        (거래량 급증 = 매도 클라이맥스)

발화 예측: 분기점 1~2분 전
"""
from collections import deque
from datetime import datetime
from typing import Dict, Any, Optional

from challenger.variants.base_challenger import BaseChallenger, ChallengerSignal


class CvdExhaustionChallenger(BaseChallenger):
    challenger_id = "A_CVD_EXHAUSTION"
    name_kr       = "CVD 탈진 감지"

    CVD_WIN      = 20    # CVD 신저점 윈도우 (분)
    VOL_MULT     = 1.8   # 거래량 급증 배수
    VOL_WIN      = 20    # 평균 거래량 계산 윈도우

    def __init__(self):
        super(CvdExhaustionChallenger, self).__init__()
        self._cvd_buf  = deque(maxlen=self.CVD_WIN + 2)
        self._vol_buf  = deque(maxlen=self.VOL_WIN)
        self._slope_prev = None   # type: Optional[float]

    def generate_signal(self, features, context):
        # type: (Dict[str, Any], Dict[str, Any]) -> ChallengerSignal
        ts     = context.get("ts", "")
        candle = context.get("candle", {})
        volume = float(candle.get("volume", 0) or 0)

        cvd_raw     = features.get("cvd", 0.0) or 0.0
        cvd_slope   = features.get("cvd_slope", 0.0) or 0.0

        self._cvd_buf.append(cvd_raw)
        self._vol_buf.append(volume)

        direction  = 0
        confidence = 0.0
        grade      = "X"
        meta       = {}

        if len(self._cvd_buf) >= self.CVD_WIN and len(self._vol_buf) >= 5:
            cvd_list = list(self._cvd_buf)
            cvd_20min_low = min(cvd_list[:-1])  # 직전 20개 중 최솟값 (현재 제외)

            # ① CVD 신저점 갱신
            cond1 = cvd_raw < cvd_20min_low

            # ② CVD 2차 미분 양전환 (낙폭 둔화)
            cvd_accel = cvd_slope - (self._slope_prev or cvd_slope)
            cond2 = cvd_accel > 0

            # ③ 거래량 급증
            avg_vol = sum(self._vol_buf) / len(self._vol_buf)
            cond3   = avg_vol > 0 and volume > avg_vol * self.VOL_MULT

            if cond1 and cond2 and cond3:
                signal_strength = min(volume / (avg_vol * 3.0), 1.0) if avg_vol > 0 else 0.5
                direction  = 1   # 매도 탈진 → 롱 신호
                confidence = 0.55 + signal_strength * 0.15   # 0.55~0.70
                grade      = self._grade_from_confidence(confidence)
                meta = {
                    "cvd_raw":         round(cvd_raw, 2),
                    "cvd_20min_low":   round(cvd_20min_low, 2),
                    "cvd_accel":       round(cvd_accel, 4),
                    "volume":          volume,
                    "avg_vol":         round(avg_vol, 1),
                    "signal_strength": round(signal_strength, 3),
                }

        self._slope_prev = cvd_slope

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
