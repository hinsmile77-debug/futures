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
"""
import logging

logger = logging.getLogger("SIGNAL")

# ── 파라미터 ────────────────────────────────────────────────────────────
_STREAK_ACTIVATE         = 10    # 발동 최소 연속 분
_STREAK_FAIL_RESET       = 3     # 조건 불충족 연속 N분 → streak 리셋
_TREND_MIN_CONF          = 0.44  # 추세 지속 시 min_conf 하한 (UP·DOWN 공용)
_CVD_SLOPE_HARD_BREAK_DN = -300  # UP streak:   CVD 하방 급반전 → 즉시 리셋
_CVD_SLOPE_HARD_BREAK_UP = +200  # DOWN streak: CVD 상방 급반전(숏스퀴즈) → 즉시 리셋


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
    def update(self, features: dict) -> dict:
        """
        Args:
            features: feature_builder가 반환한 피처 dict

        Returns:
            {
              "up_active":         bool   — UP 추세 지속 모드 여부
              "up_streak":         int    — UP 현재 연속 분
              "dn_active":         bool   — DN 추세 지속 모드 여부
              "dn_streak":         int    — DN 현재 연속 분
              "min_conf_override": float  — 활성 방향에 적용할 min_conf 하한
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

        return {
            "up_active":         self._up_active,
            "up_streak":         self._up_streak,
            "dn_active":         self._dn_active,
            "dn_streak":         self._dn_streak,
            "min_conf_override": _TREND_MIN_CONF,
        }

    # ── 일간 리셋 ──────────────────────────────────────────────────────
    def reset_daily(self):
        self._up_streak = self._up_fail_streak = 0
        self._up_active = False
        self._up_peak   = 0
        self._dn_streak = self._dn_fail_streak = 0
        self._dn_active = False
        self._dn_peak   = 0
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
