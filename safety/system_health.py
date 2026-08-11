# safety/system_health.py — 시스템 건강 점수 (SHS) + Early Kill Switch
"""
SHS = 100
  - restart_count × 8         (최대 -40점)
  - z_warn_count  × 2.5       (최대 -25점)  ← model.last_z_warn_count 사용
  - (1 - core_pass_rate) × 25 (최대 -25점, [459차 F2] CORE 미측정 분은 감점 0)
  - max(0, s2_latency_sec - 1) × 5  (최대 -10점 cap)

SHS < 60 → 슬랙 경고 + 대시보드 배지 주황 (5점 하락마다 재알림)

[459차 F2 명문화] SHS `entry_blocked`는 **표시 전용**이다 — 전수 확인 결과
사용처는 대시보드 배지 색상뿐이며 어떤 진입도 막지 않는다(실제 차단은 EKS
kill_switch_active만). 감점계수 4종(8/2.5/25/5)이 전부 미캘리브레이션이라
게이트로 승격하면 상시 차단 위험 — 승격하려면 F2 수정 후 라이브 SHS 분포를
수 주 관찰해 임계를 재캘리브레이션할 것(주간회의 안건).

[459차 F2] CORE 통과율 미측정 분리: 체크리스트는 신호가 있고 FLAT인 분에만
돈다. 종전에는 그 외 분(관망·포지션 보유)에 통과율 0.0이 들어가 매분 -25점
전액 감점됐다(측정 안 함 ≠ 전부 탈락). update_core_pass(None)이 미측정을
뜻하며, 미측정 상태의 감점은 0이다. → SHS 분포가 종전보다 위로 이동한다
(과거 시계열과 불연속 — DECISION_LOG 459차 참조).

Early Kill Switch (09:05 1회 평가):
  조건: GAP_OPEN(09:00~09:05) 구간 최대 conf < (GAP_OPEN zone min_conf - EKS_TRIGGER_MARGIN)
        AND CORE 통과율 0%
  → 일시 관망 (수동 진입은 대시보드에서 별도 허용 / 이슈 해소 시 자동 재개)

  273차: 임계 바로 아래(예: conf_max=36.4% vs mc=36.9%, 0.5%p 차)에서도 발동해
  하루 관망으로 이어지는 사례 확인 → EKS_TRIGGER_MARGIN(기본 2%p)만큼 발동 임계를
  낮춰 근소한 미달은 발동시키지 않는 히스테리시스 적용. 회복(해제) 조건은 미변경
  — "확실히 나쁠 때만 켜지고, 회복은 기존 기준 그대로"가 목표.

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

ENTRY_BLOCK_THRESHOLD       = 60.0   # SHS 이 미만이면 경고 배지·슬랙 알림 (표시 전용 — 차단 아님)
EKS_CONF_THRESHOLD          = 0.45   # GAP_OPEN zone mc 미전달 시 fallback (실제 기준은 DynMC)
EKS_MIN_BARS                = 3      # EKS 판정 최솟 GAP_OPEN 봉 수
                                     # ERR-FATAL 등으로 데이터 부족 시 섣부른 당일 관망 방지
EKS_TRIGGER_MARGIN          = 0.02   # 273차: 발동 히스테리시스 — conf_max < (mc - 마진) 이어야 발동
                                     # (mc 바로 아래 근소 미달로 당일 관망 처리되는 것 방지)
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
        self._core_pass_rate: float = 1.0  # 0.0 ~ 1.0 (마지막 측정값 — 표시용 유지)
        self._core_pass_measured: bool = False  # [459차 F2] 이번 분 체크리스트 측정 여부
        self._s2_latency_sec: float = 0.0
        self._shs: float = 100.0
        self._last_alerted_shs: float = 101.0  # 아직 블록 임계 미달 적 없음

        # GAP_OPEN 구간 수집 (EKS 판정)
        self._gap_open_conf_max:             float = 0.0
        self._gap_open_core_pass_count:      int   = 0
        self._gap_open_core_measured_count:  int   = 0   # [459차 F2] CORE를 실제로 잰 봉 수
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

    def update_core_pass(self, pass_rate: "float | None") -> None:
        """[459차 F2] pass_rate=None → 이번 분은 체크리스트 미실행(관망·포지션
        보유·워밍업) = 미측정. 감점 0으로 재계산하되 마지막 측정값은 표시용으로
        유지한다. float가 오면 종전대로 측정값 갱신."""
        if pass_rate is None:
            self._core_pass_measured = False
        else:
            self._core_pass_rate = max(0.0, min(1.0, float(pass_rate)))
            self._core_pass_measured = True
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
        core_measured: bool = True,
    ) -> None:
        """GAP_OPEN 구간(09:00~09:05) 분봉 1건 기록. EKS 판정에 사용.

        pipeline_delayed=True: 파이프라인 지연으로 conf 신뢰 불가 → bar_count만 올림.
        horizon_policy_blocked=True: HORIZON_TIME_POLICY=[] 로 예측 차단(정상 cold-start) →
            conf=0.0이 설계적 원인이므로 conf_max 산입 제외 + policy_blocked 카운트.
        core_measured=False: [459차 F2] 체크리스트 미실행 봉(관망·보유·워밍업) —
            CORE "전부 탈락"이 아니라 미측정이다. **발동 조건은 종전 그대로**
            (core_pass_count == 0) 두고 분모만 계측한다 — EKS는 안전장치라
            라이브 발동 특성을 근거 없이 바꾸지 않는다. 로그의
            `core_pass=x/y봉(측정 z봉)`에서 z가 지속적으로 0에 가까우면
            "CORE 조건이 사실상 상시 참"이라는 뜻이므로, 그때 표본을 근거로
            발동 조건 재설계를 결정할 것(NEXT_TODO 459차).
        """
        self._gap_open_bar_count += 1
        if pipeline_delayed:
            self._gap_open_delayed_count += 1
        elif horizon_policy_blocked:
            # 설계적 차단(cold-start) — conf=0.0이 정상이므로 conf_max 미반영
            self._gap_open_policy_blocked_count += 1
        else:
            self._gap_open_conf_max = max(self._gap_open_conf_max, float(conf))
        if core_measured:
            self._gap_open_core_measured_count += 1
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

        # 273차: 히스테리시스 — mc 바로 아래 근소 미달로는 발동하지 않도록
        # 발동선을 EKS_TRIGGER_MARGIN만큼 낮춰 잡는다 (회복 조건은 미변경).
        _eks_trigger_mc = max(0.0, gap_open_mc - EKS_TRIGGER_MARGIN)

        if (
            self._gap_open_conf_max < _eks_trigger_mc
            and self._gap_open_core_pass_count == 0
            and not _is_cold_start
        ):
            self._eks_active = True
            logger.warning(
                "[SHS-EKS] Early Kill Switch 발동 "
                "conf_max=%.1f%% < 발동선=%.1f%%(mc=%.1f%%-margin%.1f%%p) "
                "core_pass=0/%d봉(측정 %d봉) "
                "→ 일시 관망 (09:20부터 30분 간격 자동 회복 평가, 마감 11:30)",
                self._gap_open_conf_max * 100,
                _eks_trigger_mc * 100,
                gap_open_mc * 100,
                EKS_TRIGGER_MARGIN * 100,
                self._gap_open_bar_count,
                self._gap_open_core_measured_count,
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
        elif (
            self._gap_open_conf_max < gap_open_mc
            and self._gap_open_core_pass_count == 0
        ):
            # 마진 내 근소 미달 — 발동은 안 하되 근접 상황을 가시화 (조용히 넘기지 않음)
            logger.warning(
                "[SHS-EKS] EKS 미발동 — 마진 내 근소 미달 "
                "conf_max=%.1f%% mc=%.1f%% (발동선=%.1f%%, margin=%.1f%%p) "
                "core_pass=0/%d봉(측정 %d봉)",
                self._gap_open_conf_max * 100,
                gap_open_mc * 100,
                _eks_trigger_mc * 100,
                EKS_TRIGGER_MARGIN * 100,
                self._gap_open_bar_count,
                self._gap_open_core_measured_count,
            )
        else:
            logger.info(
                "[SHS-EKS] EKS 미발동. conf_max=%.1f%% mc=%.1f%% core_pass=%d/%d봉(측정 %d봉)",
                self._gap_open_conf_max * 100,
                gap_open_mc * 100,
                self._gap_open_core_pass_count,
                self._gap_open_bar_count,
                self._gap_open_core_measured_count,
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
        """⚠ [459차 F2] 이름과 달리 **표시 전용**이다 — 어떤 진입도 막지 않는다.
        유일한 소비처는 대시보드 SHS 배지 색상(main.py → update_shs_badge).
        실제 진입 차단은 EKS kill_switch_active / CB / EntryPolicy 경로만.
        게이트로 승격하려면 모듈 docstring의 캘리브레이션 조건을 먼저 볼 것."""
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
            "core_pass_measured": self._core_pass_measured,   # [459차 F2] False면 위 값은 과거 측정값
            "s2_latency_sec":    round(self._s2_latency_sec, 3),
            "gap_open_conf_max":      round(self._gap_open_conf_max, 3),
            "gap_open_bars":          self._gap_open_bar_count,
            "gap_open_core_measured": self._gap_open_core_measured_count,  # [459차 F2]
            "gap_open_policy_blocked": self._gap_open_policy_blocked_count,
        }

    # ── 일일 리셋 ────────────────────────────────────────────────

    def reset_daily(self) -> None:
        """15:40 일일 마감 시 GAP_OPEN·EKS 상태 초기화.
        restart_count·z_warn_count는 세션 전체 누적이므로 유지."""
        self._gap_open_conf_max             = 0.0
        self._gap_open_core_pass_count      = 0
        self._gap_open_core_measured_count  = 0   # [459차 F2]
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
        # [459차 F2] CORE 통과율은 측정된 분에만 감점 — 미측정(관망·보유 분)에
        # 0.0을 넣어 매분 -25점 전액 감점되던 결함 수정.
        if self._core_pass_measured:
            score -= (1.0 - self._core_pass_rate) * 25.0
        score -= min(10.0, max(0.0, self._s2_latency_sec - 1.0) * 5.0)
        self._shs = max(0.0, min(100.0, score))
