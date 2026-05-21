# features/technical/cvd_exhaustion.py — CVD 탈진 강도 계산기 (양방향)
"""
CvdExhaustionCalculator: bear_exhaustion / bull_exhaustion 양방향 반환.

feature_builder.py 에서 호출:
    result = self.cvd_exhaustion_calc.compute(cvd_raw, cvd_slope, volume)
    features["bear_exhaustion"] = result["bear_exhaustion"]
    features["bull_exhaustion"] = result["bull_exhaustion"]

bear_exhaustion (하락 압력 소진 → LONG MR용):
  ① cvd < cvd_20min_low   (CVD 20분 신저점 갱신)
  ② cvd_accel > 0         (낙폭 둔화 — CVD 2차 미분 양전환)
  ③ volume > avg_vol × 1.8 (거래량 급증)

bull_exhaustion (상승 압력 소진 → SHORT MR용):
  ① cvd > cvd_20min_high  (CVD 20분 신고점 갱신)
  ② cvd_accel < 0         (상승폭 둔화 — CVD 2차 미분 음전환)
  ③ volume > avg_vol × 1.8 (거래량 급증)
"""
from collections import deque
from typing import Dict


class CvdExhaustionCalculator(object):
    """CVD 탈진 강도 계산기 — 양방향 (피처 빌더용)"""

    CVD_WIN  = 20
    VOL_MULT = 1.8
    VOL_WIN  = 20

    def __init__(self):
        self._cvd_buf    = deque(maxlen=self.CVD_WIN + 2)
        self._vol_buf    = deque(maxlen=self.VOL_WIN)
        self._slope_prev = None

    def compute(self, cvd_raw, cvd_slope, volume):
        # type: (float, float, float) -> Dict[str, float]
        """
        Args:
            cvd_raw:   현재 누적 CVD
            cvd_slope: CVD 기울기 (현재 - 이전)
            volume:    현재 분봉 거래량

        Returns:
            bear_exhaustion:        0.0~1.0  (하락 압력 소진 — LONG MR용)
            bull_exhaustion:        0.0~1.0  (상승 압력 소진 — SHORT MR용)
            bear_exhaustion_signal: 0 or 1
            bull_exhaustion_signal: 0 or 1
            exhaustion:             bear_exhaustion  (deprecated — 이행기 호환)
            exhaustion_signal:      bear_exhaustion_signal (deprecated — 이행기 호환)
        """
        self._cvd_buf.append(float(cvd_raw))
        self._vol_buf.append(float(volume))

        bear_exhaustion = 0.0
        bull_exhaustion = 0.0

        if len(self._cvd_buf) >= self.CVD_WIN and len(self._vol_buf) >= 5:
            cvd_list   = list(self._cvd_buf)
            avg_vol    = sum(self._vol_buf) / len(self._vol_buf)

            prev_slope = self._slope_prev if self._slope_prev is not None else float(cvd_slope)
            cvd_accel  = float(cvd_slope) - prev_slope
            vol_surge  = avg_vol > 0 and volume > avg_vol * self.VOL_MULT
            exh_val    = min(volume / (avg_vol * 3.0), 1.0) if avg_vol > 0 else 0.5

            # bear_exhaustion: CVD 신저점 + 낙폭 둔화 + 거래량 급증
            if (cvd_raw < min(cvd_list[:-1])
                    and cvd_accel > 0
                    and vol_surge):
                bear_exhaustion = exh_val

            # bull_exhaustion: CVD 신고점 + 상승폭 둔화 + 거래량 급증
            if (cvd_raw > max(cvd_list[:-1])
                    and cvd_accel < 0
                    and vol_surge):
                bull_exhaustion = exh_val

        self._slope_prev = float(cvd_slope)

        return {
            "bear_exhaustion":        round(bear_exhaustion, 4),
            "bull_exhaustion":        round(bull_exhaustion, 4),
            "bear_exhaustion_signal": 1 if bear_exhaustion > 0 else 0,
            "bull_exhaustion_signal": 1 if bull_exhaustion > 0 else 0,
            "exhaustion":             round(bear_exhaustion, 4),        # deprecated
            "exhaustion_signal":      1 if bear_exhaustion > 0 else 0,  # deprecated
        }

    def reset_daily(self):
        self._cvd_buf.clear()
        self._vol_buf.clear()
        self._slope_prev = None
