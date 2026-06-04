# safety/system_health.py — 시스템 건강 점수 (SHS) + Early Kill Switch
"""
SHS = 100
  - restart_count × 8         (최대 -40점)
  - z_warn_count  × 2.5       (최대 -25점)  ← model.last_z_warn_count 사용
  - (1 - core_pass_rate) × 25 (최대 -25점)
  - max(0, s2_latency_sec - 1) × 5  (최대 -10점 cap)

SHS < 60 → 진입 차단 + 슬랙 경고 (5점 하락마다 재알림)

Early Kill Switch (09:05 1회 평가):
  조건: GAP_OPEN(09:00~09:05) 구간 최대 conf < 45%  AND  CORE 통과율 0%
  → 당일 관망 선언 (수동 진입은 대시보드에서 별도 허용)
"""
import logging

logger = logging.getLogger("SYSTEM")

ENTRY_BLOCK_THRESHOLD = 60.0       # SHS 이 이하면 진입 차단
EKS_CONF_THRESHOLD    = 0.45       # GAP_OPEN 최대 conf 기준
ALERT_DELTA           = 5.0        # 이 이상 추가 하락 시 슬랙 재알림


class SystemHealthScore:
    """시스템 건강 점수 + 당일 Early Kill Switch 상태 관리."""

    def __init__(self):
        self._restart_count: int   = 0
        self._z_warn_count:  int   = 0    # model.last_z_warn_count (z>임계 피처 수)
        self._core_pass_rate: float = 1.0  # 0.0 ~ 1.0
        self._s2_latency_sec: float = 0.0
        self._shs: float = 100.0
        self._last_alerted_shs: float = 101.0  # 아직 블록 임계 미달 적 없음

        # GAP_OPEN 구간 수집 (EKS 판정)
        self._gap_open_conf_max:        float = 0.0
        self._gap_open_core_pass_count: int   = 0
        self._gap_open_bar_count:       int   = 0

        # EKS 상태
        self._eks_evaluated:        bool = False
        self._eks_active:           bool = False
        self._eks_recovery_checked: bool = False   # [P3] 09:20 이후 1회 회복 시도 여부
        self._eks_reason:           str  = ""      # [C2] 발동 원인 (배지 표시용)

    # ── 업데이트 ────────────────────────────────────────────────

    def update_restart(self, count: int) -> None:
        self._restart_count = max(0, int(count))
        self._recompute()

    def update_z_warn(self, z_warn_count: int) -> None:
        self._z_warn_count = max(0, int(z_warn_count))
        self._recompute()

    def update_core_pass(self, pass_rate: float) -> None:
        self._core_pass_rate = max(0.0, min(1.0, float(pass_rate)))
        self._recompute()

    def update_s2_latency(self, latency_sec: float) -> None:
        self._s2_latency_sec = max(0.0, float(latency_sec))
        self._recompute()

    # ── GAP_OPEN 기록 ────────────────────────────────────────────

    def record_gap_open_bar(self, conf: float, core_all_passed: bool) -> None:
        """GAP_OPEN 구간(09:00~09:05) 분봉 1건 기록. EKS 판정에 사용."""
        self._gap_open_conf_max = max(self._gap_open_conf_max, float(conf))
        self._gap_open_bar_count += 1
        if core_all_passed:
            self._gap_open_core_pass_count += 1

    # ── EKS 판정 ────────────────────────────────────────────────

    def evaluate_early_kill_switch(self) -> bool:
        """
        09:05 최초 비-GAP_OPEN 분봉에서 1회 호출.
        GAP_OPEN 바가 1개 이상 있을 때만 판정.
        Returns: True if kill switch fired.
        """
        if self._eks_evaluated:
            return self._eks_active

        self._eks_evaluated = True

        if (
            self._gap_open_bar_count > 0
            and self._gap_open_conf_max < EKS_CONF_THRESHOLD
            and self._gap_open_core_pass_count == 0
        ):
            self._eks_active = True
            logger.warning(
                "[SHS-EKS] Early Kill Switch 발동! "
                "conf_max=%.1f%% core_pass=0/%d봉 → 당일 관망 선언",
                self._gap_open_conf_max * 100,
                self._gap_open_bar_count,
            )
        else:
            logger.info(
                "[SHS-EKS] EKS 미발동. conf_max=%.1f%% core_pass=%d/%d봉",
                self._gap_open_conf_max * 100,
                self._gap_open_core_pass_count,
                self._gap_open_bar_count,
            )
        return self._eks_active

    # ── EKS 회복 ────────────────────────────────────────────────

    def try_eks_recovery(
        self, scaler_age_hours: float, recent_conf: float, current_mc: float = 0.50
    ) -> bool:
        """[P3] 09:20 이후 1회 호출 — 스케일러 갱신 + conf 회복 시 EKS 자동 해제.
        해제 임계값: max(current_mc, 0.42) — 오늘처럼 낮은 conf 장에서도 해제 가능.
        Returns True if EKS was deactivated."""
        if self._eks_recovery_checked or not self._eks_active:
            return False
        self._eks_recovery_checked = True
        # 임계값: mc 기준 또는 42% 중 큰 값 (고정 50%보다 현실적)
        _threshold = max(current_mc, 0.42)
        if scaler_age_hours < 1.0 and recent_conf >= _threshold:
            self._eks_active = False
            logger.warning(
                "[SHS-EKS] EKS 자동 해제 — scaler_age=%.1fh conf=%.1f%% (임계=%.1f%%)",
                scaler_age_hours, recent_conf * 100, _threshold * 100,
            )
            return True
        logger.info(
            "[SHS-EKS] EKS 유지 — scaler_age=%.1fh conf=%.1f%% < threshold=%.1f%% (회복 조건 미충족)",
            scaler_age_hours, recent_conf * 100, _threshold * 100,
        )
        return False

    # ── 조회 ────────────────────────────────────────────────────

    @property
    def shs(self) -> float:
        return self._shs

    def is_entry_blocked(self) -> bool:
        return self._shs < ENTRY_BLOCK_THRESHOLD

    @property
    def kill_switch_active(self) -> bool:
        return self._eks_active

    def should_send_alert(self) -> bool:
        """슬랙 알림 발송 여부: 최초 블록 진입 또는 5점 이상 추가 하락 시 True."""
        if self._shs >= ENTRY_BLOCK_THRESHOLD:
            self._last_alerted_shs = self._shs
            return False
        trigger = (self._last_alerted_shs - self._shs) >= ALERT_DELTA
        if trigger:
            self._last_alerted_shs = self._shs
        return trigger

    def to_dict(self) -> dict:
        return {
            "shs":               round(self._shs, 1),
            "entry_blocked":     self.is_entry_blocked(),
            "kill_switch_active": self._eks_active,
            "restart_count":     self._restart_count,
            "z_warn_count":      self._z_warn_count,
            "core_pass_rate":    round(self._core_pass_rate, 2),
            "s2_latency_sec":    round(self._s2_latency_sec, 3),
            "gap_open_conf_max": round(self._gap_open_conf_max, 3),
            "gap_open_bars":     self._gap_open_bar_count,
        }

    # ── 일일 리셋 ────────────────────────────────────────────────

    def reset_daily(self) -> None:
        """15:40 일일 마감 시 GAP_OPEN·EKS 상태 초기화.
        restart_count·z_warn_count는 세션 전체 누적이므로 유지."""
        self._gap_open_conf_max        = 0.0
        self._gap_open_core_pass_count = 0
        self._gap_open_bar_count       = 0
        self._eks_evaluated            = False
        self._eks_active               = False
        self._eks_recovery_checked     = False
        self._eks_reason               = ""
        self._last_alerted_shs         = 101.0
        logger.info("[SHS] 일일 리셋 완료")

    # ── 내부 계산 ────────────────────────────────────────────────

    def _recompute(self) -> None:
        score = 100.0
        score -= min(40.0, self._restart_count * 8.0)
        score -= min(25.0, self._z_warn_count * 2.5)
        score -= (1.0 - self._core_pass_rate) * 25.0
        score -= min(10.0, max(0.0, self._s2_latency_sec - 1.0) * 5.0)
        self._shs = max(0.0, min(100.0, score))
