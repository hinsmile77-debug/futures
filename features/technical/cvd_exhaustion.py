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

    def __init__(self, detrend=False):
        # type: (bool) -> None
        """
        Args:
            detrend: [394차] True면 누적 CVD 레벨 대신 "레벨 − 최근 CVD_WIN봉 이동평균"
                (오실레이터)에서 신저점/신고점을 판정한다.

                왜 필요한가: Cybos buy_vol에 구조적 매수편향이 있어(분봉 delta 평균
                +57.3, t=93.1 — 최근 60거래일 raw_candles 실측) 일중 누적 CVD가 사실상
                단조 증가한다. 그 결과 원시 레벨 기준 20봉 신저점은 **0.00%**, 신고점은
                55.89%로 완전히 한쪽으로 쏠려 bear_exhaustion이 구조적으로 발화 불가다.
                오실레이터로 바꾸면 신저점 10.26% / 신고점 6.85%로 양방향이 회복된다.

                단 detrend=True의 산출값은 **아직 알파가 검증되지 않았다** — 발화 시점
                사후 10분 수익률이 기대방향 기준 평균 −1.72pt(n=89, t=−1.35)로 음수다.
                그래서 라이브 소비가 아니라 섀도 관측용으로 먼저 배선한다
                (config/settings.py:EXHAUSTION_RESTORE_MODE).
                근거: docs/미륵이고도화2/Phase1_소진복구_2026-07-27.md
        """
        self.detrend     = bool(detrend)
        self._cvd_buf    = deque(maxlen=self.CVD_WIN + 2)
        self._lvl_buf    = deque(maxlen=self.CVD_WIN)   # detrend용 이동평균 원천
        self._vol_buf    = deque(maxlen=self.VOL_WIN)
        self._slope_prev = None

    def compute(self, cvd_raw, cvd_slope, volume):
        # type: (float, float, float) -> Dict[str, float]
        """
        Args:
            cvd_raw:   현재 누적 CVD (detrend=True면 내부에서 오실레이터로 변환)
            cvd_slope: CVD 기울기 (현재 - 이전). detrend=True면 무시하고 오실레이터
                       델타를 대신 사용한다 — 추세제거 전후 기울기 단위가 다르기 때문.
            volume:    현재 분봉 거래량

        Returns:
            bear_exhaustion:        0.0~1.0  (하락 압력 소진 — LONG MR용)
            bull_exhaustion:        0.0~1.0  (상승 압력 소진 — SHORT MR용)
            bear_exhaustion_signal: 0 or 1
            bull_exhaustion_signal: 0 or 1
            exhaustion:             bear_exhaustion  (deprecated — 이행기 호환)
            exhaustion_signal:      bear_exhaustion_signal (deprecated — 이행기 호환)
        """
        if self.detrend:
            self._lvl_buf.append(float(cvd_raw))
            cvd_val = float(cvd_raw) - sum(self._lvl_buf) / len(self._lvl_buf)
        else:
            cvd_val = float(cvd_raw)

        self._cvd_buf.append(cvd_val)
        self._vol_buf.append(float(volume))

        bear_exhaustion = 0.0
        bull_exhaustion = 0.0
        slope_now = float(cvd_slope)

        if len(self._cvd_buf) >= self.CVD_WIN and len(self._vol_buf) >= 5:
            cvd_list   = list(self._cvd_buf)
            avg_vol    = sum(self._vol_buf) / len(self._vol_buf)

            if self.detrend:
                slope_now = cvd_val - cvd_list[-2]
            prev_slope = self._slope_prev if self._slope_prev is not None else slope_now
            cvd_accel  = slope_now - prev_slope
            vol_surge  = avg_vol > 0 and volume > avg_vol * self.VOL_MULT
            exh_val    = min(volume / (avg_vol * 3.0), 1.0) if avg_vol > 0 else 0.5

            # bear_exhaustion: CVD 신저점 + 낙폭 둔화 + 거래량 급증
            if (cvd_val < min(cvd_list[:-1])
                    and cvd_accel > 0
                    and vol_surge):
                bear_exhaustion = exh_val

            # bull_exhaustion: CVD 신고점 + 상승폭 둔화 + 거래량 급증
            if (cvd_val > max(cvd_list[:-1])
                    and cvd_accel < 0
                    and vol_surge):
                bull_exhaustion = exh_val

        self._slope_prev = slope_now

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
        self._lvl_buf.clear()
        self._vol_buf.clear()
        self._slope_prev = None
