# collection/macro/micro_regime.py — 미시 레짐 분류기 ⭐v6.5
"""
매분 ADX·ATR 기반 미시 레짐 실시간 분류

기존 매크로 레짐(1일 1회): RISK_ON / NEUTRAL / RISK_OFF
신규 미시 레짐(매분):      추세장 / 횡보장 / 급변장 / 혼합

v6.5 분류 기준 (ADX·ATR):
  ADX > 25, ATR < 평균 1.5배 → "추세장"  → 추세추종 우위
  ADX < 20, ATR < 평균        → "횡보장"  → 역추세 (개인 역발상)
  ATR > 평균 2배              → "급변장"  → 거래 중단/사이즈 축소
  나머지                      → "혼합"    → 표준 앙상블

Hurst와의 시너지 (hurst_exponent.py 참조):
  ADX > 25 AND H > 0.55 → 강한 추세 (+15% 부스트)
  ADX > 25 AND H < 0.45 → 가짜 추세 (진입 차단)

기대 효과: 정확도 +4~7%
"""
import numpy as np
from collections import deque
from typing import Optional
import logging

logger = logging.getLogger("SYSTEM")

# 레짐 상수
REGIME_TREND      = "추세장"
REGIME_RANGE      = "횡보장"
REGIME_VOLATILE   = "급변장"
REGIME_MIXED      = "혼합"
REGIME_EXHAUSTION = "탈진"   # 방안 D: CVD 탈진 + OFI 급반전 + VWAP 이탈

# 탈진 레짐 전략 파라미터
REGIME_EXHAUSTION_PARAMS = {
    "strategy_mode":  "mean_reversion",
    "min_confidence":  0.56,
    "size_mult":       0.70,
    "entry_direction": "TOWARD_VWAP",
    "hurst_override":  True,   # H < 0.45 차단 무효화
}


class MicroRegimeClassifier:
    """
    매분 ADX·ATR 기반 미시 레짐 분류기

    Phase 3에서 regime_specific.py, meta_confidence.py 등에 레짐 신호 공급.
    """

    ADX_TREND_THRESHOLD  = 25.0   # ADX > 25 → 추세
    ADX_RANGE_THRESHOLD  = 20.0   # ADX < 20 → 횡보
    ATR_VOLATILE_MULT    = 2.0    # ATR > 평균 2배 → 급변
    ATR_TREND_MULT       = 1.5    # ATR < 평균 1.5배 조건 (추세장 필터)
    ATR_EXHAUSTION_MULT  = 1.5    # 탈진 레짐: ATR 확대 임계값
    VWAP_EXHAUSTION_MIN  = 1.5    # 탈진 레짐: VWAP 이탈 최소 σ

    def __init__(self, atr_window: int = 20, adx_window: int = 14):
        """
        Args:
            atr_window: ATR 이동평균 창 (분봉)
            adx_window: ADX 계산 창 (분봉)
        """
        self.atr_window = atr_window
        self.adx_window = adx_window

        # 가격 데이터 버퍼
        self._high_buf  = deque(maxlen=adx_window + 5)
        self._low_buf   = deque(maxlen=adx_window + 5)
        self._close_buf = deque(maxlen=adx_window + 5)

        # ATR 버퍼
        self._atr_buf   = deque(maxlen=atr_window)

        # 현재 레짐
        self._current_regime   = REGIME_MIXED
        self._regime_duration  = 0   # 현재 레짐 지속 분 수
        self._prev_regime      = REGIME_MIXED

        # 레짐 이력 (전략 매핑용)
        self._regime_history   = deque(maxlen=60)

    def push_1m_candle(self, high, low, close,
                       cvd_exhaustion=0.0, ofi_reversal_speed=0.0,
                       vwap_position=0.0):
        # type: (float, float, float, float, float, float) -> dict
        """
        1분봉 캔들 입력 → 미시 레짐 계산

        Returns:
            {regime, adx, atr, atr_avg, atr_ratio, regime_duration,
             regime_changed, trend_strength}
        """
        self._high_buf.append(high)
        self._low_buf.append(low)
        self._close_buf.append(close)

        if len(self._close_buf) < 5:
            return self._empty()

        # ATR 계산
        atr     = self._compute_atr()
        atr_avg = float(np.mean(list(self._atr_buf))) if len(self._atr_buf) >= 5 else atr
        self._atr_buf.append(atr)
        atr_ratio = atr / (atr_avg + 1e-9)

        # ADX 계산
        adx = self._compute_adx()

        # 레짐 분류 (탈진 레짐 피처 전달)
        new_regime = self._classify(adx, atr, atr_avg, atr_ratio,
                                    cvd_exhaustion, ofi_reversal_speed,
                                    vwap_position)

        # 레짐 변경 감지
        regime_changed = (new_regime != self._current_regime)
        if regime_changed:
            logger.info(f"[MicroRegime] {self._current_regime} → {new_regime} "
                        f"(ADX={adx:.1f}, ATR={atr:.3f}, ratio={atr_ratio:.2f})")
            self._prev_regime     = self._current_regime
            self._current_regime  = new_regime
            self._regime_duration = 1
        else:
            self._regime_duration += 1

        self._regime_history.append(new_regime)

        # 추세 강도 (ADX 기반 0~1)
        trend_strength = float(np.clip((adx - 10) / 40.0, 0.0, 1.0))

        return {
            "regime":          new_regime,
            "adx":             round(adx, 2),
            "atr":             round(atr, 4),
            "atr_avg":         round(atr_avg, 4),
            "atr_ratio":       round(atr_ratio, 3),
            "regime_duration": self._regime_duration,
            "regime_changed":  regime_changed,
            "trend_strength":  round(trend_strength, 3),
            "hurst_override":  new_regime == REGIME_EXHAUSTION,
        }

    def _classify(self, adx, atr, atr_avg, atr_ratio,
                  cvd_exhaustion=0.0, ofi_reversal_speed=0.0, vwap_position=0.0):
        # type: (float, float, float, float, float, float, float) -> str
        """레짐 분류 규칙"""
        # 급변장: ATR 2배 이상 → 최우선 차단
        if atr_ratio >= self.ATR_VOLATILE_MULT:
            return REGIME_VOLATILE

        # 탈진 레짐 (방안 D): 4가지 조건 동시 충족
        exhaustion_conds = (
            atr_ratio >= self.ATR_EXHAUSTION_MULT          # 변동성 확대
            and cvd_exhaustion > 0                          # CVD 탈진
            and abs(ofi_reversal_speed) > 0                 # OFI 급반전 (0 초과면 통과)
            and abs(vwap_position) >= self.VWAP_EXHAUSTION_MIN  # VWAP 밴드 이탈
        )
        if exhaustion_conds:
            return REGIME_EXHAUSTION

        # 추세장: ADX 강세 + ATR 과도하지 않음
        if adx >= self.ADX_TREND_THRESHOLD and atr_ratio < self.ATR_TREND_MULT:
            return REGIME_TREND

        # 횡보장: ADX 약세 + ATR 정상
        if adx < self.ADX_RANGE_THRESHOLD and atr_ratio < 1.3:
            return REGIME_RANGE

        # 나머지: 혼합
        return REGIME_MIXED

    def _compute_atr(self) -> float:
        """1분봉 ATR 계산"""
        highs  = list(self._high_buf)
        lows   = list(self._low_buf)
        closes = list(self._close_buf)

        if len(closes) < 2:
            return 0.0

        tr_list = []
        for i in range(1, len(closes)):
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i-1]),
                abs(lows[i] - closes[i-1]),
            )
            tr_list.append(tr)

        return float(np.mean(tr_list[-14:])) if tr_list else 0.0

    def _compute_adx(self) -> float:
        """
        ADX 계산 (Wilder's Smoothed DI)
        단순화: 선형 기울기 기반 방향 강도 (실제 Wilder ADX보다 가볍고 실시간 적합)
        """
        closes = np.array(list(self._close_buf))
        if len(closes) < self.adx_window:
            return 15.0   # 기본값 (혼합 레짐)

        # 양방향 방향성 측정
        # +DM: 상승 움직임 / -DM: 하락 움직임
        highs = np.array(list(self._high_buf)[-self.adx_window:])
        lows  = np.array(list(self._low_buf)[-self.adx_window:])

        if len(highs) < 2:
            return 15.0

        plus_dm  = np.maximum(highs[1:] - highs[:-1], 0)
        minus_dm = np.maximum(lows[:-1] - lows[1:], 0)

        # 양방향이 모두 양수면 큰 쪽만 취함
        for i in range(len(plus_dm)):
            if plus_dm[i] > 0 and minus_dm[i] > 0:
                if plus_dm[i] >= minus_dm[i]:
                    minus_dm[i] = 0
                else:
                    plus_dm[i] = 0

        # ATR (분모)
        atrs = []
        for i in range(1, min(len(highs), len(lows), len(list(self._close_buf)))):
            tr = max(highs[i] - lows[i],
                     abs(highs[i] - list(self._close_buf)[-self.adx_window+i-1]),
                     abs(lows[i] - list(self._close_buf)[-self.adx_window+i-1]))
            atrs.append(tr)

        atr_sum = sum(atrs) if atrs else 1e-9

        plus_di  = 100 * sum(plus_dm)  / (atr_sum + 1e-9)
        minus_di = 100 * sum(minus_dm) / (atr_sum + 1e-9)

        di_sum  = plus_di + minus_di
        if di_sum < 1e-9:
            return 15.0

        dx  = 100 * abs(plus_di - minus_di) / di_sum
        return float(np.clip(dx, 0, 100))

    def _empty(self) -> dict:
        return {
            "regime":          REGIME_MIXED,
            "adx":             15.0,
            "atr":             0.0,
            "atr_avg":         0.0,
            "atr_ratio":       1.0,
            "regime_duration": 0,
            "regime_changed":  False,
            "trend_strength":  0.0,
        }

    @property
    def current_regime(self) -> str:
        return self._current_regime

    def get_regime_distribution(self) -> dict:
        """최근 60분 레짐 분포"""
        hist = list(self._regime_history)
        if not hist:
            return {}
        from collections import Counter
        cnt = Counter(hist)
        return {r: round(cnt.get(r, 0) / len(hist), 3) for r in REGIMES}

    def reset_daily(self):
        self._high_buf.clear()
        self._low_buf.clear()
        self._close_buf.clear()
        self._atr_buf.clear()
        self._current_regime  = REGIME_MIXED
        self._regime_duration = 0
        self._regime_history.clear()


if __name__ == "__main__":
    import random
    random.seed(42)

    clf = MicroRegimeClassifier()
    price = 390.0

    print("=== 추세 구간 ===")
    for i in range(30):
        price += random.gauss(0.15, 0.1)   # 상승 추세
        h = price + abs(random.gauss(0, 0.05))
        l = price - abs(random.gauss(0, 0.05))
        r = clf.push_1m_candle(high=h, low=l, close=price)
        if r["regime_changed"] or i % 5 == 0:
            print(f"[{i+1:02d}분] 레짐={r['regime']}, ADX={r['adx']:.1f}, "
                  f"ATR비={r['atr_ratio']:.2f}, 지속={r['regime_duration']}분")

    print("\n=== 급변 구간 ===")
    for i in range(10):
        price += random.gauss(0, 3.0)   # 급변
        h = price + abs(random.gauss(0, 1.5))
        l = price - abs(random.gauss(0, 1.5))
        r = clf.push_1m_candle(high=h, low=l, close=price)
        if r["regime_changed"] or i % 3 == 0:
            print(f"[{i+31:02d}분] 레짐={r['regime']}, ATR비={r['atr_ratio']:.2f}")
