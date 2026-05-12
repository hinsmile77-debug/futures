# features/technical/cvd_exhaustion.py — CVD 탈진 강도 계산기
"""
CvdExhaustionCalculator: CVD 탈진 강도 0.0~1.0 반환.

feature_builder.py 에서 호출:
    result = self.cvd_exhaustion.compute(cvd_raw, cvd_slope, volume)
    features["cvd_exhaustion"] = result["exhaustion"]

탈진 조건 (3가지 동시 충족 시 exhaustion > 0):
  ① cvd < cvd_20min_low   (CVD 20분 신저점 갱신)
  ② cvd_accel > 0         (CVD 2차 미분 양전환)
  ③ volume > avg_vol × 1.8 (거래량 급증)
"""
from collections import deque
from typing import Dict


class CvdExhaustionCalculator(object):
    """CVD 탈진 강도 계산기 (피처 빌더용)"""

    CVD_WIN    = 20
    VOL_MULT   = 1.8
    VOL_WIN    = 20

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
            {"exhaustion": 0.0~1.0, "exhaustion_signal": 0 or 1}
        """
        self._cvd_buf.append(float(cvd_raw))
        self._vol_buf.append(float(volume))

        exhaustion = 0.0

        if len(self._cvd_buf) >= self.CVD_WIN and len(self._vol_buf) >= 5:
            cvd_list     = list(self._cvd_buf)
            cvd_20min_low = min(cvd_list[:-1])

            # ① 신저점
            cond1 = cvd_raw < cvd_20min_low

            # ② 낙폭 둔화
            prev_slope   = self._slope_prev if self._slope_prev is not None else cvd_slope
            cvd_accel    = float(cvd_slope) - prev_slope
            cond2        = cvd_accel > 0

            # ③ 거래량 급증
            avg_vol = sum(self._vol_buf) / len(self._vol_buf)
            cond3   = avg_vol > 0 and volume > avg_vol * self.VOL_MULT

            if cond1 and cond2 and cond3:
                exhaustion = min(volume / (avg_vol * 3.0), 1.0) if avg_vol > 0 else 0.5

        self._slope_prev = float(cvd_slope)

        return {
            "exhaustion":        round(exhaustion, 4),
            "exhaustion_signal": 1 if exhaustion > 0 else 0,
        }

    def reset_daily(self):
        self._cvd_buf.clear()
        self._vol_buf.clear()
        self._slope_prev = None
