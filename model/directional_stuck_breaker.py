# model/directional_stuck_breaker.py — 앙상블 방향 고착 감쇠기
"""
DirectionalStuckBreaker

발동 조건 (3개 AND):
  1. NEUTRAL 레짐
  2. 앙상블 최종 방향이 동일 방향으로 ACTIVATE_STREAK(8)회 이상 연속
  3. CB③ 30분 정확도(acc30m) < ACC30M_THRESHOLD(38%)

발동 시 효과:
  고착 방향 score에서 deflate분을 빼고 flat_score에 더함.
  streak 8회 → 2.5% 감쇠, 10회 → 7.5%, 12회 → 12.5%, 14회+ → 15%(상한).
  확률 합 = 1.0 유지 보장 (감쇠분을 flat으로 이동).

TrendPersistenceGate 억제:
  TrendGate가 같은 방향으로 활성 상태이면 StuckBreaker 억제.
  (실제 추세 신호가 있다면 고착이 아닐 수 있음)

리셋:
  direction == FLAT 시 streak 즉시 0 리셋 (모델이 스스로 방향을 포기한 경우).

설계 원칙:
  - HorizonDecorrelator 가중치 직접 수정 금지 (15분 재계산 시 덮어씌워짐)
  - 출력 확률을 직접 조정하여 등급 강등 유도
  - A→B, B→C, C→X 순차 강등 → 자동진입 불가 또는 관망
"""
import logging
from config.constants import DIRECTION_UP, DIRECTION_DOWN, DIRECTION_FLAT

logger = logging.getLogger("SIGNAL")

_ACTIVATE_STREAK   = 8      # 발동 최소 연속 횟수
_DEFLATE_PER_STEP  = 0.025  # 발동 후 1스텝(1회)당 추가 감쇠율
_MAX_DEFLATE       = 0.15   # 감쇠 상한 (15%)
_ACC30M_THRESHOLD  = 0.38   # 30분 정확도가 이 값 미만일 때만 발동


class DirectionalStuckBreaker:
    """
    매분 EnsembleDecision.compute() 내에서 호출.
    AdaptiveEnsembleGater 이후, 최종 방향 결정 이전에 삽입.
    """

    def __init__(self):
        self._streak:    int = 0
        self._stuck_dir: int = 0   # +1(UP) or -1(DOWN)

    # ── 매분 호출 ────────────────────────────────────────────────────
    def update_and_apply(
        self,
        direction: int,
        up_score: float,
        down_score: float,
        flat_score: float,
        regime: str,
        acc30m: float = 0.5,
        trend_gate_up_active: bool = False,
        trend_gate_dn_active: bool = False,
    ):
        """
        방향 고착 감지 후 확률 조정.

        Returns:
            (up_score, down_score, flat_score, streak, active)
            확률 합 = 1.0 유지 보장
        """
        # ── streak 갱신 ──────────────────────────────────────────────
        if direction == DIRECTION_FLAT:
            # 모델이 스스로 방향을 포기 → 즉시 리셋
            if self._streak > 0:
                logger.debug(
                    "[StuckBreaker] FLAT 전환 → streak %d→0 리셋",
                    self._streak,
                )
            self._streak    = 0
            self._stuck_dir = 0
        elif direction == self._stuck_dir:
            self._streak += 1
        else:
            # 방향 전환 (UP↔DOWN) → streak 1로 초기화
            self._streak    = 1
            self._stuck_dir = direction

        # ── 발동 조건 (3개 AND) ───────────────────────────────────────
        # 조건 1: NEUTRAL 레짐
        cond_regime = (regime == "NEUTRAL")
        # 조건 2: streak 기준 이상
        cond_streak = (self._streak >= _ACTIVATE_STREAK)
        # 조건 3: acc30m 기준 미만 (실제로 틀리고 있다는 증거)
        cond_acc    = (acc30m < _ACC30M_THRESHOLD)

        if cond_streak and cond_regime and cond_acc and self._streak == _ACTIVATE_STREAK:
            logger.warning(
                "[StuckBreaker] 방향 고착 발동 dir=%+d streak=%d "
                "acc30m=%.1f%% regime=%s",
                self._stuck_dir, self._streak, acc30m * 100, regime,
            )

        active = cond_regime and cond_streak and cond_acc
        if not active:
            return up_score, down_score, flat_score, self._streak, False

        # ── TrendGate 억제: TrendGate가 같은 방향으로 활성이면 억제 ──
        if self._stuck_dir == DIRECTION_UP   and trend_gate_up_active:
            logger.debug(
                "[StuckBreaker] TrendGate UP active → UP 고착 감쇠 억제 "
                "(streak=%d)", self._streak,
            )
            return up_score, down_score, flat_score, self._streak, False

        if self._stuck_dir == DIRECTION_DOWN and trend_gate_dn_active:
            logger.debug(
                "[StuckBreaker] TrendGate DN active → DN 고착 감쇠 억제 "
                "(streak=%d)", self._streak,
            )
            return up_score, down_score, flat_score, self._streak, False

        # ── 감쇠율 계산 ──────────────────────────────────────────────
        extra   = self._streak - _ACTIVATE_STREAK        # 0, 1, 2, ...
        deflate = min(_DEFLATE_PER_STEP * (extra + 1), _MAX_DEFLATE)

        if self._stuck_dir == DIRECTION_UP:
            moved      = up_score * deflate
            up_score   = up_score - moved
            flat_score = flat_score + moved
            logger.info(
                "[StuckBreaker] UP 고착 감쇠 streak=%d deflate=%.1f%% "
                "up -%.4f flat +%.4f",
                self._streak, deflate * 100, moved, moved,
            )
        else:
            moved       = down_score * deflate
            down_score  = down_score - moved
            flat_score  = flat_score + moved
            logger.info(
                "[StuckBreaker] DN 고착 감쇠 streak=%d deflate=%.1f%% "
                "dn -%.4f flat +%.4f",
                self._streak, deflate * 100, moved, moved,
            )

        return up_score, down_score, flat_score, self._streak, True

    # ── 일간 리셋 ───────────────────────────────────────────────────
    def reset_daily(self):
        self._streak    = 0
        self._stuck_dir = 0
        logger.debug("[StuckBreaker] 일간 리셋")

    # ── 진단 ────────────────────────────────────────────────────────
    def status_dict(self) -> dict:
        return {
            "streak":    self._streak,
            "stuck_dir": self._stuck_dir,
            "active":    self._streak >= _ACTIVATE_STREAK,
        }
