# strategy/entry/trend_persistence.py — 추세 지속성 게이트
"""
TrendPersistenceGate (UP·DOWN 양방향)

UP 모드:
  above_vwap=1 AND cvd_direction=1 이 STREAK_ACTIVATE분 이상 연속 →
  UP 방향 진입 한정으로 min_conf를 TREND_MIN_CONF 로 완화.

DOWN 모드:
  above_vwap=0 AND cvd_direction=-1 이 STREAK_ACTIVATE분 이상 연속 →
  DOWN 방향 진입 한정으로 min_conf를 TREND_MIN_CONF 로 완화.

목적: 롱/숏 원웨이 추세장에서 GBM conf 부족으로 진입 0건이 되는
      구조적 문제를 장중 실시간 추세 감지로 보완.

리셋 조건:
  - 조건 불충족 STREAK_FAIL_RESET분 연속 → streak 리셋
  - UP:   cvd_slope < CVD_SLOPE_HARD_BREAK_DN (-300) → 즉시 리셋 (CVD 급하락)
  - DOWN: cvd_slope > CVD_SLOPE_HARD_BREAK_UP (+200) → 즉시 리셋 (숏스퀴즈)
          DOWN hard_break를 UP보다 민감(-300 vs +200)하게 설정한 이유:
          하락 중 CVD 급반등(숏스퀴즈)은 상승 중 CVD 급반락보다 훨씬 빠르고 파괴적.

가격 구조 보강 (PriceStructureBoost):
  recent_bars 를 받아 HH-HL(연속 고점·저점 상승) 또는 LH-LL(연속 고점·저점 하락)
  구조를 감지. streak >= STREAK_ACTIVATE_PRICE_BOOST 이고 가격 구조가 같은 방향이면
  min_conf 를 TREND_MIN_CONF_PRICE_BOOST 까지 추가 완화.
  OFI 또는 CVD 중 하나는 같은 방향이어야 부스트를 인정한다(과진입 방지).
"""
import logging
from typing import Dict, List, Optional

logger = logging.getLogger("SIGNAL")

# ── 파라미터 ────────────────────────────────────────────────────────────
_STREAK_ACTIVATE         = 10    # 발동 최소 연속 분
_STREAK_FAIL_RESET       = 3     # 조건 불충족 연속 N분 → streak 리셋
_TREND_MIN_CONF          = 0.44  # 추세 지속 시 min_conf 하한 (UP·DOWN 공용)
_CVD_SLOPE_HARD_BREAK_DN = -300  # UP streak:   CVD 하방 급반전 → 즉시 리셋
_CVD_SLOPE_HARD_BREAK_UP = +200  # DOWN streak: CVD 상방 급반전(숏스퀴즈) → 즉시 리셋

# 가격 구조 보강 파라미터
_TREND_MIN_CONF_PRICE_BOOST  = 0.38  # HH-HL/LH-LL 확인 시 추가 완화 하한
_STREAK_ACTIVATE_PRICE_BOOST = 5     # 부스트 적용 최소 streak (STREAK_ACTIVATE 미만도 허용)
_PRICE_STRUCT_N              = 5     # 고점·저점 비교 봉 수


def _price_structure(bars: List[Dict], n: int = _PRICE_STRUCT_N) -> int:
    """최근 n봉의 고점·저점 구조를 판정한다.

    Args:
        bars: [{"high": float, "low": float}, ...] 최신 순서로 오른쪽 끝이 가장 최근봉

    Returns:
        +1  HH-HL (연속 고점·저점 모두 상승 → 상승 구조)
        -1  LH-LL (연속 고점·저점 모두 하락 → 하락 구조)
         0  판정 불가
    """
    if len(bars) < n:
        return 0
    recent = bars[-n:]
    highs = [b.get("high", 0.0) or 0.0 for b in recent]
    lows  = [b.get("low",  0.0) or 0.0 for b in recent]
    hh = all(highs[i] > highs[i - 1] for i in range(1, n))
    hl = all(lows[i]  > lows[i - 1]  for i in range(1, n))
    lh = all(highs[i] < highs[i - 1] for i in range(1, n))
    ll = all(lows[i]  < lows[i - 1]  for i in range(1, n))
    if hh and hl:
        return +1
    if lh and ll:
        return -1
    return 0


def _step_streak(streak, fail_streak, cond_ok, hard_break, label):
    """단방향 streak 1스텝 업데이트. (new_streak, new_fail_streak) 반환."""
    if hard_break:
        if streak > 0:
            logger.debug("[TrendGate][%s] 즉시 리셋 streak %d→0", label, streak)
        return 0, 0
    if cond_ok:
        return streak + 1, 0
    new_fail = fail_streak + 1
    if new_fail >= _STREAK_FAIL_RESET:
        if streak > 0:
            logger.debug(
                "[TrendGate][%s] streak 리셋 (fail=%d) %d→0", label, new_fail, streak
            )
        return 0, 0
    return streak, new_fail


class TrendPersistenceGate:
    """
    장중 추세 지속성 게이트 (UP·DOWN 양방향).

    매분 update(features) 호출.
    active=True 이면 호출부(main.py)에서 해당 방향 actual_min_conf를
    min(actual_min_conf, TREND_MIN_CONF)으로 완화.
    """

    def __init__(self):
        self._up_streak:      int  = 0
        self._up_fail_streak: int  = 0
        self._up_active:      bool = False
        self._up_peak:        int  = 0

        self._dn_streak:      int  = 0
        self._dn_fail_streak: int  = 0
        self._dn_active:      bool = False
        self._dn_peak:        int  = 0

    # ── 매분 호출 ──────────────────────────────────────────────────────
    def update(self, features: dict, recent_bars: Optional[List[Dict]] = None) -> dict:
        """
        Args:
            features:    feature_builder가 반환한 피처 dict
            recent_bars: 최근 N봉 OHLC 리스트 [{"high":, "low":, ...}, ...]
                         None 이면 가격 구조 보강 비활성

        Returns:
            {
              "up_active":         bool   — UP 추세 지속 모드 여부
              "up_streak":         int    — UP 현재 연속 분
              "dn_active":         bool   — DN 추세 지속 모드 여부
              "dn_streak":         int    — DN 현재 연속 분
              "min_conf_override": float  — 활성 방향에 적용할 min_conf 하한
              "price_structure":   int    — +1/0/-1 (가격 구조 판정)
              "price_boost_active":bool   — 가격 구조 부스트 적용 여부
            }
        """
        above_vwap    = int(features.get("above_vwap", 0) or 0)
        cvd_direction = int(features.get("cvd_direction", 0) or 0)
        cvd_slope     = float(features.get("cvd_slope", 0.0) or 0.0)

        # ── UP streak ───────────────────────────────────────────────────
        up_cond   = (above_vwap == 1 and cvd_direction == 1)
        up_hbreak = (cvd_slope < _CVD_SLOPE_HARD_BREAK_DN)
        self._up_streak, self._up_fail_streak = _step_streak(
            self._up_streak, self._up_fail_streak, up_cond, up_hbreak, "UP"
        )
        self._up_peak  = max(self._up_peak, self._up_streak)
        prev_up        = self._up_active
        self._up_active = (self._up_streak >= _STREAK_ACTIVATE)

        if self._up_active and not prev_up:
            logger.info(
                "[TrendGate] UP 추세 지속 모드 ON (streak=%d) "
                "— UP min_conf %.2f 완화",
                self._up_streak, _TREND_MIN_CONF,
            )
        elif not self._up_active and prev_up:
            logger.info("[TrendGate] UP 추세 지속 모드 OFF (streak=%d)", self._up_streak)

        # ── DOWN streak ─────────────────────────────────────────────────
        dn_cond   = (above_vwap == 0 and cvd_direction == -1)
        dn_hbreak = (cvd_slope > _CVD_SLOPE_HARD_BREAK_UP)   # 숏스퀴즈 감지
        self._dn_streak, self._dn_fail_streak = _step_streak(
            self._dn_streak, self._dn_fail_streak, dn_cond, dn_hbreak, "DN"
        )
        self._dn_peak  = max(self._dn_peak, self._dn_streak)
        prev_dn        = self._dn_active
        self._dn_active = (self._dn_streak >= _STREAK_ACTIVATE)

        if self._dn_active and not prev_dn:
            logger.info(
                "[TrendGate] DN 추세 지속 모드 ON (streak=%d) "
                "— DN min_conf %.2f 완화",
                self._dn_streak, _TREND_MIN_CONF,
            )
        elif not self._dn_active and prev_dn:
            logger.info("[TrendGate] DN 추세 지속 모드 OFF (streak=%d)", self._dn_streak)

        # ── 가격 구조 보강 (PriceStructureBoost) ────────────────────────
        ps = _price_structure(recent_bars) if recent_bars else 0
        price_boost = False
        min_conf_override = _TREND_MIN_CONF

        if ps != 0:
            active_streak = self._up_streak if ps == 1 else self._dn_streak
            ofi_ok  = int(features.get("ofi_pressure",  0) or 0) == ps
            cvd_ok  = cvd_direction == ps
            if (active_streak >= _STREAK_ACTIVATE_PRICE_BOOST
                    and (ofi_ok or cvd_ok)):
                min_conf_override = _TREND_MIN_CONF_PRICE_BOOST
                price_boost = True
                if not getattr(self, "_last_price_boost", False):
                    logger.info(
                        "[TrendGate] 가격구조 부스트 ON (%s) streak=%d "
                        "ofi=%s cvd=%s → min_conf %.2f→%.2f",
                        "HH-HL" if ps == 1 else "LH-LL",
                        active_streak, ofi_ok, cvd_ok,
                        _TREND_MIN_CONF, _TREND_MIN_CONF_PRICE_BOOST,
                    )
            elif getattr(self, "_last_price_boost", False):
                logger.info(
                    "[TrendGate] 가격구조 부스트 OFF (ps=%+d streak=%d ofi=%s cvd=%s)",
                    ps, active_streak, ofi_ok, cvd_ok,
                )
        elif getattr(self, "_last_price_boost", False):
            logger.info("[TrendGate] 가격구조 부스트 OFF (ps=0)")
        self._last_price_boost = price_boost

        return {
            "up_active":          self._up_active,
            "up_streak":          self._up_streak,
            "dn_active":          self._dn_active,
            "dn_streak":          self._dn_streak,
            "min_conf_override":  min_conf_override,
            "price_structure":    ps,
            "price_boost_active": price_boost,
        }

    # ── 일간 리셋 ──────────────────────────────────────────────────────
    def reset_daily(self):
        self._up_streak = self._up_fail_streak = 0
        self._up_active = False
        self._up_peak   = 0
        self._dn_streak = self._dn_fail_streak = 0
        self._dn_active = False
        self._dn_peak   = 0
        self._last_price_boost = False
        logger.debug("[TrendGate] 일간 리셋")

    # ── 진단 ───────────────────────────────────────────────────────────
    def status_dict(self) -> dict:
        return {
            "up_active":  self._up_active,
            "up_streak":  self._up_streak,
            "up_peak":    self._up_peak,
            "dn_active":  self._dn_active,
            "dn_streak":  self._dn_streak,
            "dn_peak":    self._dn_peak,
        }
