# safety/circuit_breaker.py — 5종 트리거 비상 정지
"""
Circuit Breaker (설계 명세 A2):

발동 조건 5종:
  ① 1분 내 신호 5번 이상 반전      → 15분 진입 정지
  ② 5분 내 손절 3번 연속           → 당일 시스템 정지
  ③ 30분 정확도 이동평균 < 35%     → 당일 시스템 정지
  ④ 변동성 ATR 평균의 3배 초과     → 5분 진입 정지
  ⑤ API 응답 지연 5초 초과        → 전 포지션 즉시 청산

2010 Flash Crash 이후 모든 헤지펀드 의무 도입.
"""
import datetime
import logging
import statistics
from collections import deque
from typing import Callable, Optional

from utils.time_utils import now_kst

from config.settings import (
    CB_SIGNAL_FLIP_LIMIT, CB_SIGNAL_FLIP_PAUSE,
    CB_CONSEC_STOP_LIMIT, CB_ACCURACY_MIN_30M,
    CB_ATR_MULT_LIMIT, CB_API_LATENCY_LIMIT, CB_API_LATENCY_PAUSE,
    CB_HIGH_CONF_WRONG_LIMIT, CB_HIGH_CONF_THRESHOLD, CB_ACCURACY_MIN_30M_STRICT,
    CB_MID_CONF_WRONG_LIMIT, CB_MID_CONF_LO, CB_MID_CONF_HI,
    CB_BRIER_WINDOW, CB_BRIER_WARN, CB_BRIER_PENALTY,
    CB_DAILY_HALT_HALF_SIZE, CB_DAILY_HALT_FULL_BLOCK,
    CB_CB3_WARN_RESET_MARGIN, CB_CB3_WARN_RESET_OK_STREAK,
    CB_PIPE_WARN_MS, CB_PIPE_PAUSE_MS,
    CB_ACC_WATCH_MIN, CB_ACC_RESTRICTED_MIN,   # [P4] 4단계 구간 경계값
    CB_ACC30M_MIN_SAMPLES,                     # CB③ 발동 최솟 유효 샘플 수
)
from config.constants import CB_STATE_NORMAL, CB_STATE_PAUSED, CB_STATE_HALTED
from utils.notify import notify_circuit_breaker
from logging_system.log_manager import log_manager

logger = logging.getLogger("SYSTEM")


class CircuitBreaker:
    """5종 트리거 Circuit Breaker"""

    def __init__(self, emergency_exit_callback: Optional[Callable] = None):
        """
        Args:
            emergency_exit_callback: 즉시 청산이 필요할 때 호출할 함수
        """
        self._state: str = CB_STATE_NORMAL
        self._pause_until: Optional[datetime.datetime] = None
        self._emergency_exit = emergency_exit_callback

        # 트리거 ① 신호 반전 추적 (1분 창)
        self._signal_history: deque = deque()   # (timestamp, direction)
        self._flip_window_sec = 60

        # 트리거 ② 연속 손절 카운터
        self._consec_stops: int = 0

        # 트리거 ③ 30분 정확도 버퍼
        self._accuracy_buf: deque = deque(maxlen=30)  # 매분 정확도

        # 트리거 ④ ATR 비율
        self._atr_buf: deque = deque(maxlen=30)

        # 트리거 ⑤ 최근 API 지연
        self._last_latency: float = 0.0

        # 트리거 ③ 연속 경고 카운터 — 2회 연속 미달 시 HALT
        self._cb3_warn_count: int = 0
        self._cb3_ok_streak:  int = 0  # 연속 정상 분 수 (리셋 조건 강화용)

        # 과신(conf >= CB_HIGH_CONF_THRESHOLD) 오류 연속 카운터
        # 연속 N회 이상이면 CB③ 임계값을 0.35 → 0.50으로 상향 (더 빨리 발동)
        self._high_conf_wrong_streak: int = 0

        # ── [1순위] Mid-Conf Blind Spot Tracker ──────────────────
        # 60~85% 중간신뢰도 구간 연속 오답 — 오늘(5/19) 직접 원인
        # 7회 연속이면 strict 모드 진입 (CB③ 임계값 0.35→0.50)
        self._mid_conf_wrong_streak: int = 0

        # ── [2순위] Brier Score 실시간 추적 ──────────────────────
        # brier_i = (conf_i - actual_i)^2 이동평균으로 과신 탐지
        # 이동평균 > CB_BRIER_WARN  → 경고 로그
        # 이동평균 > CB_BRIER_PENALTY → 사이징 50% 패널티 플래그
        self._brier_buf: deque = deque(maxlen=CB_BRIER_WINDOW)
        self._brier_penalty_active: bool = False

        # ── [3순위] 재시작 루프 브레이커 ─────────────────────────
        # 당일 CB③ HALT 횟수 추적
        # 2회 → 다음 진입 50% 사이즈, 3회 이상 → 완전 관망
        self._daily_halt_count: int = 0

        # ── [P4] acc30m 4단계 구간 추적 ──────────────────────────
        # NORMAL(≥35%) / WATCH(30~35%) / RESTRICTED(28~30%) / HALTED(<28%→기존CB③)
        self._acc30m_stage: str = "NORMAL"

        # ── [P5] 호라이즌별 FL 편향 고착 추적 ────────────────────
        # 15m을 포함한 개별 호라이즌의 FL 편향이 30분 이상 지속 시 CRITICAL 로그 + Slack.
        # 거래 중단(HALT)이 아닌 모델 품질 경보 — 실제 차단은 main.py P2(uniform fallback) 담당.
        self._horizon_fl_bias_streak: dict = {}  # {horizon: 연속 분 수}
        self._horizon_fl_bias_warned: set = set()  # 이미 경보 발송한 호라이즌

    # ── 상태 조회 ──────────────────────────────────────────────
    @property
    def state(self) -> str:
        self._check_pause_expiry()
        return self._state

    def is_entry_allowed(self) -> bool:
        return self.state == CB_STATE_NORMAL

    def high_conf_entry_block(self, conf: float) -> bool:
        """
        고신뢰 연속오답 진입 차단 여부.
        streak >= CB_HIGH_CONF_WRONG_LIMIT AND 현재 conf >= CB_HIGH_CONF_THRESHOLD 이면 True.
        CB_STATE와 독립적으로 동작해 진입 전 사전 차단 역할.
        """
        if self._high_conf_wrong_streak < CB_HIGH_CONF_WRONG_LIMIT:
            return False
        return conf >= CB_HIGH_CONF_THRESHOLD

    @property
    def brier_size_mult(self) -> float:
        """[2순위] Brier Score 패널티 배수. 패널티 발동 시 0.5, 정상 시 1.0."""
        return 0.5 if self._brier_penalty_active else 1.0

    @property
    def restart_size_mult(self) -> float:
        """[3순위] 재시작 루프 브레이커 사이즈 배수.
        당일 HALT 횟수에 따라 감소:  0~1회 → 1.0 / 2회 → 0.5 / 3회 이상 → 0.0 (진입 차단)
        """
        if self._daily_halt_count >= CB_DAILY_HALT_FULL_BLOCK:
            return 0.0
        if self._daily_halt_count >= CB_DAILY_HALT_HALF_SIZE:
            return 0.5
        return 1.0

    def is_restart_blocked(self) -> bool:
        """[3순위] 당일 HALT가 CB_DAILY_HALT_FULL_BLOCK 회 이상이면 재진입 완전 차단."""
        return self._daily_halt_count >= CB_DAILY_HALT_FULL_BLOCK

    @property
    def acc30m_stage(self) -> str:
        """[P4] 현재 acc30m 4단계 구간: NORMAL / WATCH / RESTRICTED."""
        return self._acc30m_stage

    def is_grade_restricted(self) -> bool:
        """[P4] RESTRICTED 구간 여부 — C등급 이하 자동 진입 차단 시 True."""
        return self._acc30m_stage == "RESTRICTED"

    @property
    def mid_conf_wrong_streak(self) -> int:
        """[1순위] 현재 중간신뢰도 연속 오답 횟수."""
        return self._mid_conf_wrong_streak

    @property
    def daily_halt_count(self) -> int:
        """[3순위] 당일 HALT 발생 횟수."""
        return self._daily_halt_count

    def _check_pause_expiry(self):
        if self._state == CB_STATE_PAUSED and self._pause_until:
            if now_kst() >= self._pause_until:
                self._state = CB_STATE_NORMAL
                self._pause_until = None
                logger.info("[CB] 일시 정지 해제 — 정상 복귀")
                log_manager.system("[CB] 일시 정지 해제 — 정상 복귀", "INFO")

    # ── 트리거 ① 신호 반전 ────────────────────────────────────
    def record_signal(self, direction: int):
        now = now_kst()
        self._signal_history.append((now, direction))

        # 1분 이전 제거
        cutoff = now - datetime.timedelta(seconds=self._flip_window_sec)
        while self._signal_history and self._signal_history[0][0] < cutoff:
            self._signal_history.popleft()

        # 반전 횟수 계산
        signals = [d for _, d in self._signal_history]
        flips = sum(1 for i in range(1, len(signals)) if signals[i] != signals[i-1])

        if flips >= CB_SIGNAL_FLIP_LIMIT:
            self._trigger_pause(
                CB_SIGNAL_FLIP_PAUSE,
                f"신호 반전 {flips}회/분",
            )

    # ── 트리거 ② 연속 손절 ────────────────────────────────────
    def record_stop_loss(self):
        self._consec_stops += 1
        logger.warning(f"[CB] 연속 손절 {self._consec_stops}회")
        if self._consec_stops >= CB_CONSEC_STOP_LIMIT:
            self._trigger_halt(f"연속 손절 {self._consec_stops}회 — 당일 정지")

    def record_win(self):
        self._consec_stops = 0   # 수익 시 카운터 초기화

    # ── 트리거 ③ 정확도 저하 (30분 호라이즌 전용) ───────────────
    def record_accuracy(self, correct: bool, confidence: float = 1.0,
                        contrarian_active: bool = False):
        """
        Args:
            correct:            예측 적중 여부
            confidence:         예측 신뢰도 (과신·중간신뢰도 오류 감지에 사용)
            contrarian_active:  Contrarian 모드 활성 여부.
                                True이면 accuracy_buf 누적 및 CB③ 경고를 스킵.
                                Brier·과신·Mid-Conf streak는 항상 집계.
        """
        # ── [2순위] Brier Score 누적 — Contrarian 상태와 무관하게 항상 집계 ──
        actual = 1.0 if correct else 0.0
        brier  = (confidence - actual) ** 2
        self._brier_buf.append(brier)
        if len(self._brier_buf) >= CB_BRIER_WINDOW:
            brier_avg = sum(self._brier_buf) / len(self._brier_buf)
            if brier_avg > CB_BRIER_PENALTY:
                if not self._brier_penalty_active:
                    self._brier_penalty_active = True
                    msg = (
                        f"[Brier] 과신 패널티 발동 | "
                        f"이동평균={brier_avg:.3f} > {CB_BRIER_PENALTY} "
                        f"— 사이징 50% 강제 축소"
                    )
                    logger.warning(msg)
                    log_manager.system(msg, "WARNING")
            elif brier_avg > CB_BRIER_WARN:
                if not self._brier_penalty_active:
                    logger.warning(
                        "[Brier] 과신 경고 | 이동평균=%.3f > %.2f",
                        brier_avg, CB_BRIER_WARN,
                    )
            else:
                self._brier_penalty_active = False

        # ── 과신(conf >= 0.85) 오류 연속 카운터 — 항상 집계 ─────
        if not correct and confidence >= CB_HIGH_CONF_THRESHOLD:
            self._high_conf_wrong_streak += 1
        else:
            self._high_conf_wrong_streak = 0

        # ── [1순위] Mid-Conf Blind Spot Tracker — 항상 집계 ──────
        if not correct and CB_MID_CONF_LO <= confidence < CB_MID_CONF_HI:
            self._mid_conf_wrong_streak += 1
            if self._mid_conf_wrong_streak == CB_MID_CONF_WRONG_LIMIT:
                msg = (
                    f"[Mid-Conf Blind Spot] {CB_MID_CONF_WRONG_LIMIT}연속 오답 "
                    f"(conf {CB_MID_CONF_LO:.0%}~{CB_MID_CONF_HI:.0%}) "
                    f"— CB③ strict 모드 진입"
                )
                logger.warning(msg)
                log_manager.system(msg, "WARNING")
                notify_circuit_breaker(
                    f"Mid-Conf {CB_MID_CONF_WRONG_LIMIT}연속 오답",
                    "CB③ strict 모드 (임계값 35%→42%)",
                )
        else:
            self._mid_conf_wrong_streak = 0

        # ── CB③ 정확도 집계 ───────────────────────────────────────
        # [deadlock 수정] 누적과 발동을 분리:
        #   - accuracy_buf 누적은 Contrarian 상태와 무관하게 항상 수행
        #   - Contrarian ACTIVE 중에는 CB③ HALT/경고 발동만 스킵
        # 수정 전: contrarian_active → return (누적 자체를 막아 acc30m 영구 동결)
        # 수정 후: 누적은 허용 → acc30m이 회복되면 Contrarian이 자연 해제됨
        self._accuracy_buf.append(1.0 if correct else 0.0)

        # [P4] acc30m 4단계 구간 갱신 — Contrarian 상태와 무관하게 항상 추적
        if len(self._accuracy_buf) >= CB_ACC30M_MIN_SAMPLES:
            _acc_now = sum(self._accuracy_buf) / len(self._accuracy_buf)
            _new_stage = (
                "RESTRICTED" if _acc_now < CB_ACC_RESTRICTED_MIN else
                "WATCH"      if _acc_now < CB_ACC_WATCH_MIN      else
                "NORMAL"
            )
            if _new_stage != self._acc30m_stage:
                _msg = (
                    f"[CB③-P4] acc30m 단계 전환: {self._acc30m_stage} → {_new_stage}"
                    f" (acc={_acc_now:.1%})"
                )
                logger.warning(_msg)
                log_manager.system(_msg, "WARNING")
                self._acc30m_stage = _new_stage

        if contrarian_active:
            return  # HALT/경고 발동만 스킵, 누적은 이미 위에서 완료

        if len(self._accuracy_buf) >= CB_ACC30M_MIN_SAMPLES:
            acc = sum(self._accuracy_buf) / len(self._accuracy_buf)
            _n_samples = len(self._accuracy_buf)

            # 과신 또는 중간신뢰도 streak 중 하나라도 임계 초과면 strict 모드
            effective_min = (
                CB_ACCURACY_MIN_30M_STRICT
                if (self._high_conf_wrong_streak >= CB_HIGH_CONF_WRONG_LIMIT
                    or self._mid_conf_wrong_streak >= CB_MID_CONF_WRONG_LIMIT)
                else CB_ACCURACY_MIN_30M
            )

            if acc < effective_min:
                self._cb3_ok_streak = 0
                self._cb3_warn_count += 1
                if self._cb3_warn_count >= 2:
                    streak_note = ""
                    if self._high_conf_wrong_streak >= CB_HIGH_CONF_WRONG_LIMIT:
                        streak_note += f" | 고신뢰 오류 {self._high_conf_wrong_streak}연속"
                    if self._mid_conf_wrong_streak >= CB_MID_CONF_WRONG_LIMIT:
                        streak_note += f" | 중간신뢰도 오류 {self._mid_conf_wrong_streak}연속"
                    self._trigger_halt(
                        f"30분 정확도 {acc:.1%} < {effective_min:.0%} "
                        f"(2회 연속 미달{streak_note}) n={_n_samples}"
                    )
                else:
                    msg = (
                        f"[CB③ 경고 {self._cb3_warn_count}/2] "
                        f"30분 정확도 {acc:.1%} < {effective_min:.0%} "
                        f"n={_n_samples} — 다음 확인 시 당일 정지"
                    )
                    logger.warning(msg)
                    log_manager.system(msg, "WARNING")
                    notify_circuit_breaker(
                        f"30분 정확도 {acc:.1%} 경고 ({self._cb3_warn_count}/2)",
                        "다음 미달 시 당일 정지",
                    )
            else:
                # 리셋 조건: 임계값 + 여유폭 이상으로 연속 N분 정상이어야 카운터 리셋
                reset_margin = CB_CB3_WARN_RESET_MARGIN
                reset_streak = CB_CB3_WARN_RESET_OK_STREAK
                if acc >= effective_min + reset_margin:
                    self._cb3_ok_streak += 1
                    if self._cb3_ok_streak >= reset_streak:
                        self._cb3_warn_count = 0
                        self._cb3_ok_streak = 0
                else:
                    self._cb3_ok_streak = 0

    # ── [P5] 호라이즌별 FL 편향 고착 경보 ───────────────────────
    def record_horizon_fl_bias(self, horizon: str, fl_ratio: float, streak: int):
        """특정 호라이즌의 FL 예측 편향이 고착됐을 때 호출.

        30분 이상 지속이면 CRITICAL 로그 + Slack 경보를 1회 발송한다.
        거래 중단(HALT)은 하지 않음 — 차단은 main.py P2(uniform fallback)가 담당.

        Args:
            horizon:  편향 호라이즌 ('10m', '15m' 등)
            fl_ratio: FL 예측 비율 (0.0~1.0)
            streak:   연속 편향 분 수
        """
        self._horizon_fl_bias_streak[horizon] = streak
        if streak >= 30 and horizon not in self._horizon_fl_bias_warned:
            self._horizon_fl_bias_warned.add(horizon)
            msg = (
                f"[CB-FLBias] {horizon} FL편향 {fl_ratio:.0%} {streak}분 지속 "
                f"— uniform fallback 적용 중. 모델 재학습 또는 다음 장 P8 확인 필요."
            )
            logger.critical(msg)
            log_manager.system(msg, "CRITICAL")
            notify_circuit_breaker(
                f"{horizon} FL편향 {fl_ratio:.0%} {streak}분 고착",
                "uniform fallback 적용 중 — 모델 품질 경보",
            )

    # ── 트리거 ④ ATR 급등 ─────────────────────────────────────
    def record_atr(self, atr_ratio: float):
        self._atr_buf.append(atr_ratio)
        # 즉시 스파이크: 단일 시점 3배 초과
        if atr_ratio >= CB_ATR_MULT_LIMIT:
            self._trigger_pause(5, f"ATR {atr_ratio:.1f}배 급등 (순간)")
            return
        # 지속 급등: 버퍼 중앙값이 임계치의 70% 이상으로 3분 이상 유지
        # 단일 스파이크가 아닌 지속 고변동성 장세에서도 CB를 발동한다.
        if len(self._atr_buf) >= 3:
            med = statistics.median(self._atr_buf)
            if med >= CB_ATR_MULT_LIMIT * 0.7:
                self._trigger_pause(3, f"ATR {med:.1f}배 지속 급등 (중앙값, 버퍼={len(self._atr_buf)})")

    # ── 트리거 ⑤ API 지연 ─────────────────────────────────────
    def record_api_latency(self, latency_sec: float):
        self._last_latency = latency_sec
        if latency_sec >= CB_API_LATENCY_LIMIT:
            # PAUSED·HALTED 상태에서는 슬랙·청산 콜백 중복 호출 방지
            if self._state not in (CB_STATE_PAUSED, CB_STATE_HALTED):
                msg = f"[CB] API 지연 {latency_sec:.1f}초 — 즉시 청산"
                logger.critical(msg)
                log_manager.system(msg, "CRITICAL")
                notify_circuit_breaker(
                    f"API 지연 {latency_sec:.1f}초",
                    "전 포지션 즉시 청산",
                )
                if self._emergency_exit:
                    self._emergency_exit()
            self._trigger_pause(
                CB_API_LATENCY_PAUSE // 60,
                f"API 지연 {latency_sec:.1f}초",
            )

    # ── 트리거 ⑤ 파이프라인 처리시간 (Cybos CB⑤ 대체) ──────────
    def record_pipe_latency(self, pipe_ms: float):
        """매분 파이프라인 처리시간 감시.

        Cybos Plus는 COM 콜백 기반으로 네트워크 RTT 측정 불가.
        파이프라인 실행시간(run_minute_pipeline 경과)을 CB⑤ 대체 지표로 사용.

        > CB_PIPE_WARN_MS (1초) : WARNING 로그
        > CB_PIPE_PAUSE_MS (5초): 5분 진입 정지 + Slack 알림

        예외: 09:00~09:02 장 시작 직후 2분은 EarlyWarmup·ScalerWarmup·GBM PreRetrain
        스레드가 동시에 실행되어 첫 분봉 처리가 구조적으로 느림.
        이 구간은 임계를 9000ms로 완화하고 경고만 발생시킨다.
        """
        # DBG-CB latency 필드 갱신 — status_dict()의 last_latency가 0.0 고착되던 문제 수정
        # record_api_latency가 Cybos에서 호출 안 됨 → pipe_ms를 초 단위로 대입
        self._last_latency = pipe_ms / 1000.0
        _now_t = now_kst().time()
        # 09:00~09:10: EarlyWarmup·ScalerWarmup·GBM PreRetrain·ERR-FATAL 복구가
        # 겹쳐 파이프라인이 구조적으로 느림. 임계를 9000ms로 완화하여 오발동 방지.
        _open_burst = (
            datetime.time(9, 0) <= _now_t < datetime.time(9, 10)
        )
        _pause_threshold = 9_000 if _open_burst else CB_PIPE_PAUSE_MS

        if pipe_ms >= _pause_threshold:
            if self._state not in (CB_STATE_PAUSED, CB_STATE_HALTED):
                notify_circuit_breaker(
                    f"파이프라인 {pipe_ms:.0f}ms 지연",
                    "5분 진입 정지",
                )
            self._trigger_pause(5, f"파이프라인 {pipe_ms:.0f}ms — 처리 지연")
        elif pipe_ms >= CB_PIPE_WARN_MS:
            _open_tag = " [장시작 버스트]" if _open_burst else ""
            msg = f"[CB⑤] 파이프라인 {pipe_ms:.0f}ms 경고 (기준 {CB_PIPE_WARN_MS:.0f}ms){_open_tag}"
            logger.warning(msg)
            log_manager.system(msg, "WARNING")

    # ── 내부 트리거 ────────────────────────────────────────────
    def _trigger_pause(self, minutes: int, reason: str):
        # PAUSED·HALTED 상태에서는 재발동 금지 (중복 슬랙 전송 방지)
        if self._state in (CB_STATE_PAUSED, CB_STATE_HALTED):
            return
        self._state = CB_STATE_PAUSED
        self._pause_until = now_kst() + datetime.timedelta(minutes=minutes)
        msg = f"[CB] {minutes}분 진입 정지 | {reason}"
        logger.warning(msg)
        log_manager.system(msg, "WARNING")
        notify_circuit_breaker(reason, f"{minutes}분 진입 정지")

    def _trigger_halt(self, reason: str):
        # HALTED 상태에서는 재발동 금지 (중복 슬랙 전송 방지)
        if self._state == CB_STATE_HALTED:
            return
        self._state = CB_STATE_HALTED
        self._pause_until = None
        # ── [3순위] 재시작 루프 브레이커 카운터 증가 ─────────────
        self._daily_halt_count += 1
        halt_note = ""
        if self._daily_halt_count >= CB_DAILY_HALT_FULL_BLOCK:
            halt_note = f" | 당일 HALT {self._daily_halt_count}회 → 완전 관망 모드"
        elif self._daily_halt_count >= CB_DAILY_HALT_HALF_SIZE:
            halt_note = f" | 당일 HALT {self._daily_halt_count}회 → 재진입 50% 사이즈"
        msg = f"[CB] 당일 시스템 정지 | {reason}{halt_note}"
        logger.critical(msg)
        log_manager.system(msg, "CRITICAL")
        notify_circuit_breaker(reason, f"당일 시스템 정지{halt_note}")
        # CB② · CB③ 발동 시에도 기존 포지션 즉시 청산
        # (CB⑤는 record_api_latency에서 별도 호출, 여기서는 ②·③ 공통 처리)
        if self._emergency_exit:
            self._emergency_exit()

    def reset_daily(self):
        """장 시작 시 일간 리셋"""
        self._state = CB_STATE_NORMAL
        self._pause_until = None
        self._signal_history.clear()
        self._consec_stops = 0
        self._accuracy_buf.clear()
        self._atr_buf.clear()
        self._cb3_warn_count = 0
        self._high_conf_wrong_streak = 0
        self._mid_conf_wrong_streak = 0
        self._brier_buf.clear()
        self._brier_penalty_active = False
        self._daily_halt_count = 0
        self._acc30m_stage = "NORMAL"   # [P4]
        self._horizon_fl_bias_streak.clear()   # [P5]
        self._horizon_fl_bias_warned.clear()   # [P5]
        logger.info("[CB] 일간 리셋 완료")
        log_manager.system("[CB] 일간 리셋 완료", "INFO")

    def status_dict(self) -> dict:
        brier_avg = (sum(self._brier_buf) / len(self._brier_buf)
                     if self._brier_buf else 0.0)
        return {
            "state":                   self.state,
            "pause_until":             self._pause_until.strftime("%H:%M:%S") if self._pause_until else None,
            "consec_stops":            self._consec_stops,
            "last_latency":            self._last_latency,
            "accuracy_30m":            round(sum(self._accuracy_buf) / max(len(self._accuracy_buf), 1), 3),
            "cb3_warn_count":          self._cb3_warn_count,
            "cb3_samples":             len(self._accuracy_buf),
            "high_conf_wrong_streak":  self._high_conf_wrong_streak,
            "mid_conf_wrong_streak":   self._mid_conf_wrong_streak,
            "brier_avg":               round(brier_avg, 4),
            "brier_penalty_active":    self._brier_penalty_active,
            "daily_halt_count":        self._daily_halt_count,
            "restart_size_mult":       self.restart_size_mult,
            "acc30m_stage":            self._acc30m_stage,   # [P4]
        }

    def to_state_dict(self) -> dict:
        """재시작 영속화용 상태 직렬화 (signal_history·accuracy_buf 제외)."""
        return {
            "state":                  self._state,
            "pause_until":            self._pause_until.isoformat() if self._pause_until else None,
            "consec_stops":           self._consec_stops,
            "cb3_warn_count":         self._cb3_warn_count,
            "high_conf_wrong_streak": self._high_conf_wrong_streak,
            "mid_conf_wrong_streak":  self._mid_conf_wrong_streak,
            "brier_penalty_active":   self._brier_penalty_active,
            "daily_halt_count":       self._daily_halt_count,
        }

    def from_state_dict(self, d: dict) -> None:
        """to_state_dict() 반환값으로 상태 복원."""
        if not d:
            return
        self._state = str(d.get("state", CB_STATE_NORMAL) or CB_STATE_NORMAL)
        pu = d.get("pause_until")
        try:
            self._pause_until = datetime.datetime.fromisoformat(pu) if pu else None
        except Exception:
            self._pause_until = None
        self._consec_stops           = int(d.get("consec_stops", 0) or 0)
        self._cb3_warn_count         = int(d.get("cb3_warn_count", 0) or 0)
        self._high_conf_wrong_streak = int(d.get("high_conf_wrong_streak", 0) or 0)
        self._mid_conf_wrong_streak  = int(d.get("mid_conf_wrong_streak", 0) or 0)
        self._brier_penalty_active   = bool(d.get("brier_penalty_active", False))
        self._daily_halt_count       = int(d.get("daily_halt_count", 0) or 0)
        logger.info(
            "[CB] 상태 복원: state=%s consec_stops=%d cb3_warn=%d "
            "mid_conf_streak=%d daily_halt=%d",
            self._state, self._consec_stops, self._cb3_warn_count,
            self._mid_conf_wrong_streak, self._daily_halt_count,
        )
