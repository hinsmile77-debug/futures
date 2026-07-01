# safety/system_health.py — 시스템 건강 점수 (SHS) + Early Kill Switch
"""
SHS = 100
  - restart_count × 8         (최대 -40점)
  - z_warn_count  × 2.5       (최대 -25점)  ← model.last_z_warn_count 사용
  - (1 - core_pass_rate) × 25 (최대 -25점)
  - max(0, s2_latency_sec - 1) × 5  (최대 -10점 cap)

SHS < 60 → 진입 차단 + 슬랙 경고 (5점 하락마다 재알림)

Early Kill Switch (09:05 1회 평가):
  조건: GAP_OPEN(09:00~09:05) 구간 최대 conf < GAP_OPEN zone min_conf  AND  CORE 통과율 0%
  → 일시 관망 (수동 진입은 대시보드에서 별도 허용 / 이슈 해소 시 자동 재개)

EKS 동적 해제:
  간격: 30분마다 재평가 (09:20, 09:50, 10:20, 11:00, 11:30)
  해제 조건 (3가지 모두 충족):
    ① 스케일러 age < 1h  (갱신된 스케일러 사용 중)
    ② 최근 10봉 중 conf ≥ current_mc 봉 수 ≥ 3  (DynMC 기준, 0.42 floor 제거)
    ③ z경고 피처 수 < 15  (장 시작 직후 극단 z 스파이크 고려, 5→15 완화)
  마감: 11:30 이후 재평가 없음 (거래 시간 부족)
"""
import datetime
import logging

logger = logging.getLogger("SYSTEM")

ENTRY_BLOCK_THRESHOLD       = 60.0   # SHS 이 이하면 진입 차단
EKS_CONF_THRESHOLD          = 0.45   # GAP_OPEN zone mc 미전달 시 fallback (실제 기준은 DynMC)
EKS_MIN_BARS                = 3      # EKS 판정 최솟 GAP_OPEN 봉 수
                                     # ERR-FATAL 등으로 데이터 부족 시 섣부른 당일 관망 방지
ALERT_DELTA                 = 5.0    # 이 이상 추가 하락 시 슬랙 재알림

EKS_RECOVERY_INTERVAL_MIN   = 30     # 재평가 최소 간격 (분)
EKS_RECOVERY_CONF_WINDOW    = 10     # 회복 판정용 최근 봉 수
EKS_RECOVERY_CONF_MIN_HITS  = 3      # window 내 임계 초과 최소 봉 수
EKS_RECOVERY_DEADLINE       = datetime.time(11, 30)  # 이 시각 이후 재평가 없음


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
        self._gap_open_conf_max:             float = 0.0
        self._gap_open_core_pass_count:      int   = 0
        self._gap_open_bar_count:            int   = 0
        self._gap_open_delayed_count:        int   = 0   # [P2] 파이프라인 지연으로 conf 제외된 봉 수
        self._gap_open_policy_blocked_count: int   = 0   # [P3] HORIZON_TIME_POLICY [] 차단 봉 수

        # EKS 상태
        self._eks_evaluated:          bool  = False
        self._eks_active:             bool  = False
        self._eks_recovery_count:     int   = 0     # 회복 시도 횟수 (로그·진단용)
        self._eks_last_recovery_ts:   "datetime.datetime | None" = None
        self._eks_reason:             str   = ""    # [C2] 발동 원인 (배지 표시용)

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

    def record_gap_open_bar(
        self,
        conf: float,
        core_all_passed: bool,
        pipeline_delayed: bool = False,
        horizon_policy_blocked: bool = False,
    ) -> None:
        """GAP_OPEN 구간(09:00~09:05) 분봉 1건 기록. EKS 판정에 사용.

        pipeline_delayed=True: 파이프라인 지연으로 conf 신뢰 불가 → bar_count만 올림.
        horizon_policy_blocked=True: HORIZON_TIME_POLICY=[] 로 예측 차단(정상 cold-start) →
            conf=0.0이 설계적 원인이므로 conf_max 산입 제외 + policy_blocked 카운트.
        """
        self._gap_open_bar_count += 1
        if pipeline_delayed:
            self._gap_open_delayed_count += 1
        elif horizon_policy_blocked:
            # 설계적 차단(cold-start) — conf=0.0이 정상이므로 conf_max 미반영
            self._gap_open_policy_blocked_count += 1
        else:
            self._gap_open_conf_max = max(self._gap_open_conf_max, float(conf))
        if core_all_passed:
            self._gap_open_core_pass_count += 1

    # ── EKS 판정 ────────────────────────────────────────────────

    def evaluate_early_kill_switch(self, gap_open_mc: float = EKS_CONF_THRESHOLD) -> bool:
        """
        09:05 최초 비-GAP_OPEN 분봉에서 1회 호출.
        gap_open_mc: GAP_OPEN zone DynMC min_conf (main.py에서 전달). 미전달 시 fallback 0.45.
        GAP_OPEN 바가 1개 이상 있을 때만 판정.
        Returns: True if kill switch fired.
        """
        if self._eks_evaluated:
            return self._eks_active

        self._eks_evaluated = True

        if self._gap_open_bar_count < EKS_MIN_BARS:
            import datetime as _dt_mod
            _now_t = _dt_mod.datetime.now().time()
            if _now_t >= _dt_mod.time(9, 15):
                # 09:15 이후 재시작 → GAP_OPEN 봉 수집 기회 없음 → EKS 미발동 확정
                # (판단 근거 없으므로 관망 선언하지 않음)
                logger.info(
                    "[SHS-EKS] 재시작 후 GAP_OPEN 봉 없음 (09:15 이후) — EKS 미발동 확정"
                )
                return False
            # 09:15 이전이면 기존대로 유예 (이후 GAP_OPEN 봉 수집 가능)
            logger.warning(
                "[SHS-EKS] EKS 판정 유예 — GAP_OPEN 봉 부족 "
                "(%d봉 < 최소 %d봉) conf_max=%.1f%%",
                self._gap_open_bar_count,
                EKS_MIN_BARS,
                self._gap_open_conf_max * 100,
            )
            return False

        # cold-start 판별: conf_max==0.0% 이고 모든 봉이 지연·정책차단으로 설명되는 경우
        # [P3] HORIZON_TIME_POLICY=(900,905):[] + 장시작버스트(09:00 delayed=1) 조합 시
        #   delayed=1, policy_blocked=4, bar_count=5 → 5/5 설명됨 → cold-start 정상 판정.
        #   기존 로직(delayed==0 조건)은 장시작버스트 1봉이 delayed_count를 1로 만들어
        #   cold-start 탐지를 무너뜨렸음 (264차 수정).
        _all_bars_accounted = (
            self._gap_open_delayed_count + self._gap_open_policy_blocked_count
            >= self._gap_open_bar_count
        )
        _is_cold_start = (
            self._gap_open_conf_max == 0.0
            and _all_bars_accounted
        )

        if (
            self._gap_open_conf_max < gap_open_mc
            and self._gap_open_core_pass_count == 0
            and not _is_cold_start
        ):
            self._eks_active = True
            logger.warning(
                "[SHS-EKS] Early Kill Switch 발동 "
                "conf_max=%.1f%% < mc=%.1f%% core_pass=0/%d봉 "
                "→ 일시 관망 (09:20부터 30분 간격 자동 회복 평가, 마감 11:30)",
                self._gap_open_conf_max * 100,
                gap_open_mc * 100,
                self._gap_open_bar_count,
            )
        elif _is_cold_start:
            logger.info(
                "[SHS-EKS] EKS 미발동 — cold-start "
                "(conf_max=0%% delayed=%d policy_blocked=%d / %d봉) "
                "HORIZON_TIME_POLICY 차단 또는 active_horizons 초기화 지연으로 판단",
                self._gap_open_delayed_count,
                self._gap_open_policy_blocked_count,
                self._gap_open_bar_count,
            )
        else:
            logger.info(
                "[SHS-EKS] EKS 미발동. conf_max=%.1f%% mc=%.1f%% core_pass=%d/%d봉",
                self._gap_open_conf_max * 100,
                gap_open_mc * 100,
                self._gap_open_core_pass_count,
                self._gap_open_bar_count,
            )
        return self._eks_active

    # ── EKS 회복 ────────────────────────────────────────────────

    def can_attempt_recovery(self, now: "datetime.datetime") -> bool:
        """EKS 회복 시도 가능 여부: 활성·마감·간격 체크.
        main.py 매분 파이프라인에서 호출. True이면 try_eks_recovery 호출."""
        if not self._eks_active:
            return False
        if now.time() >= EKS_RECOVERY_DEADLINE:
            return False
        if self._eks_last_recovery_ts is None:
            _ok = now.time() >= datetime.time(9, 20)
            if _ok:
                logger.info("[SHS-EKS] 회복 평가 시작 (첫 시도) — %s", now.strftime("%H:%M"))
            return _ok
        elapsed_min = (now - self._eks_last_recovery_ts).total_seconds() / 60.0
        _ok = elapsed_min >= EKS_RECOVERY_INTERVAL_MIN
        if _ok:
            logger.info(
                "[SHS-EKS] 회복 평가 시작 (#%d, 경과=%.0f분) — %s",
                self._eks_recovery_count + 1, elapsed_min, now.strftime("%H:%M"),
            )
        return _ok

    def try_eks_recovery(
        self,
        scaler_age_hours: float,
        conf_window: list,      # 최근 EKS_RECOVERY_CONF_WINDOW봉 conf 목록
        current_mc: float = 0.50,
        z_warn_count: int = 0,
    ) -> bool:
        """주기적 EKS 회복 평가. can_attempt_recovery() 확인 후 호출.

        해제 조건 (3가지 모두):
          ① scaler_age < 1h
          ② 최근 window 중 conf ≥ current_mc 봉 수 ≥ EKS_RECOVERY_CONF_MIN_HITS  (DynMC 기준)
          ③ z경고 피처 수 < 15
        Returns True if EKS was deactivated.
        """
        if not self._eks_active:
            return False

        self._eks_recovery_count += 1
        self._eks_last_recovery_ts = datetime.datetime.now()

        _threshold = current_mc
        _hits      = sum(1 for c in conf_window if c >= _threshold)

        _ok_scaler = scaler_age_hours < 1.0
        _ok_conf   = _hits >= EKS_RECOVERY_CONF_MIN_HITS
        # P0-C: 장 시작 직후 극단 z 스파이크(quality_investor 등)로 인한 영구 차단 방지
        # 5 → 15로 완화 (실전 관측치: 장 시작 후 z=22개 지속, 5 기준으로 해제 불가)
        _ok_z      = z_warn_count < 15

        if _ok_scaler and _ok_conf and _ok_z:
            self._eks_active = False
            logger.warning(
                "[SHS-EKS] EKS 자동 해제 (회복 #%d) — "
                "scaler_age=%.1fh conf_hits=%d/%d(임계%.0f%%) z_warn=%d",
                self._eks_recovery_count,
                scaler_age_hours, _hits, len(conf_window),
                _threshold * 100, z_warn_count,
            )
            return True

        # 미해제 원인을 명확히 노출 (INFO→WARNING: 매 30분 시도 결과 가시성 확보)
        _reasons = []
        if not _ok_scaler:
            _reasons.append("scaler_age=%.1fh(≥1h)" % scaler_age_hours)
        if not _ok_conf:
            _reasons.append("conf_hits=%d/%d(필요%d,임계%.0f%%)" % (
                _hits, len(conf_window), EKS_RECOVERY_CONF_MIN_HITS, _threshold * 100))
        if not _ok_z:
            _reasons.append("z_warn=%d(≥15)" % z_warn_count)
        logger.warning(
            "[SHS-EKS] EKS 미해제 (시도 #%d) — 미충족: %s",
            self._eks_recovery_count,
            " | ".join(_reasons) if _reasons else "알 수 없음",
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
            "gap_open_conf_max":      round(self._gap_open_conf_max, 3),
            "gap_open_bars":          self._gap_open_bar_count,
            "gap_open_policy_blocked": self._gap_open_policy_blocked_count,
        }

    # ── 일일 리셋 ────────────────────────────────────────────────

    def reset_daily(self) -> None:
        """15:40 일일 마감 시 GAP_OPEN·EKS 상태 초기화.
        restart_count·z_warn_count는 세션 전체 누적이므로 유지."""
        self._gap_open_conf_max             = 0.0
        self._gap_open_core_pass_count      = 0
        self._gap_open_bar_count            = 0
        self._gap_open_delayed_count        = 0
        self._gap_open_policy_blocked_count = 0
        self._eks_evaluated            = False
        self._eks_active               = False
        self._eks_recovery_count       = 0
        self._eks_last_recovery_ts     = None
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
