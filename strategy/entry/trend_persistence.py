# strategy/entry/trend_persistence.py — 추세 지속성 게이트
"""
TrendPersistenceGate

above_vwap=1 AND cvd_direction=1 이 STREAK_ACTIVATE분 이상 연속되면
UP 방향 진입 한정으로 min_conf를 TREND_MIN_CONF 로 완화.

목적: 롱 원웨이 추세장(오늘 같은 날)에서 GBM conf 부족으로 진입 0건이 되는
      구조적 문제를 장중 실시간 추세 감지로 보완.

리셋 조건:
  - above_vwap=0 또는 cvd_direction=-1 이 STREAK_FAIL_RESET분 연속 → 리셋
  - cvd_slope < CVD_SLOPE_HARD_BREAK → 즉시 리셋 (CVD 급반전)
"""
import logging

logger = logging.getLogger("SIGNAL")

# ── 파라미터 ───────────────────────────────────────────────────────────
_STREAK_ACTIVATE    = 10     # 발동 최소 연속 분
_STREAK_FAIL_RESET  = 3      # 조건 불충족 연속 N분 → streak 리셋
_TREND_MIN_CONF     = 0.44   # 추세 지속 시 UP 방향 min_conf 하한
_CVD_SLOPE_HARD_BREAK = -300 # CVD slope 이 이하 → 즉시 리셋 (급반전 감지)


class TrendPersistenceGate:
    """
    장중 추세 지속성 게이트.

    매분 update(features) 호출 → active 여부와 streak 반환.
    active=True 이면 호출부(main.py)에서 UP 방향 actual_min_conf를
    min(actual_min_conf, TREND_MIN_CONF)으로 완화.
    """

    def __init__(self):
        self._streak: int      = 0   # 조건 연속 충족 분 수
        self._fail_streak: int = 0   # 조건 불충족 연속 분 수
        self._active: bool     = False
        self._peak_streak: int = 0   # 당일 최대 streak (진단용)

    # ── 매분 호출 ─────────────────────────────────────────────────────
    def update(self, features: dict) -> dict:
        """
        Args:
            features: feature_builder가 반환한 피처 dict

        Returns:
            {
              "active":            bool   — 추세 지속 모드 여부
              "streak":            int    — 현재 연속 분 수
              "min_conf_override": float | None — active 시 min_conf 하한
            }
        """
        above_vwap    = int(features.get("above_vwap", 0) or 0)
        cvd_direction = int(features.get("cvd_direction", 0) or 0)
        cvd_slope     = float(features.get("cvd_slope", 0.0) or 0.0)

        cond_ok    = (above_vwap == 1 and cvd_direction == 1)
        hard_break = (cvd_slope < _CVD_SLOPE_HARD_BREAK)

        if hard_break:
            # CVD 급반전 → 즉시 리셋
            if self._streak > 0:
                logger.debug(
                    "[TrendGate] 즉시 리셋 (cvd_slope=%.0f) streak %d→0",
                    cvd_slope, self._streak,
                )
            self._streak      = 0
            self._fail_streak = 0
        elif cond_ok:
            self._streak     += 1
            self._fail_streak = 0
            self._peak_streak = max(self._peak_streak, self._streak)
        else:
            self._fail_streak += 1
            if self._fail_streak >= _STREAK_FAIL_RESET:
                if self._streak > 0:
                    logger.debug(
                        "[TrendGate] streak 리셋 (fail=%d) %d→0",
                        self._fail_streak, self._streak,
                    )
                self._streak      = 0
                self._fail_streak = 0

        prev_active   = self._active
        self._active  = (self._streak >= _STREAK_ACTIVATE)

        if self._active and not prev_active:
            logger.info(
                "[TrendGate] 추세 지속 모드 ON (streak=%d) "
                "— UP 방향 min_conf %.2f 완화",
                self._streak, _TREND_MIN_CONF,
            )
        elif not self._active and prev_active:
            logger.info("[TrendGate] 추세 지속 모드 OFF (streak=%d)", self._streak)

        return {
            "active":            self._active,
            "streak":            self._streak,
            "min_conf_override": _TREND_MIN_CONF if self._active else None,
        }

    # ── 일간 리셋 ─────────────────────────────────────────────────────
    def reset_daily(self):
        self._streak      = 0
        self._fail_streak = 0
        self._active      = False
        self._peak_streak = 0
        logger.debug("[TrendGate] 일간 리셋")

    # ── 진단 ──────────────────────────────────────────────────────────
    def status_dict(self) -> dict:
        return {
            "active":       self._active,
            "streak":       self._streak,
            "peak_streak":  self._peak_streak,
        }
