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
    CB_CONSEC_STOP_LIMIT, CB_CONSEC_STOP_WINDOW_SEC, CB_ACCURACY_MIN_30M,
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
        # ⚠ `_consec_stops` 는 `_stop_events` 에서 **파생**된다(직접 증가시키지 말 것).
        #   [MW0601 489차] 종전에는 이 정수만 있었고 시간창도, 포지션 단위 중복
        #   제거도 없었다 — settings `CB_CONSEC_STOP_WINDOW_SEC` 주석 참조.
        self._consec_stops: int = 0
        self._stop_events: deque = deque()   # (timestamp, position_key|None)

        # 트리거 ③ 30분 정확도 버퍼
        self._accuracy_buf: deque = deque(maxlen=30)  # 매분 정확도

        # 트리거 ④ ATR 비율
        self._atr_buf: deque = deque(maxlen=30)

        # 트리거 ⑤ 최근 API 지연
        self._last_latency: float = 0.0

        # ── [MW0601 482차 / G-1·G-2] CB③ 가용성 계측 ────────────────
        # acc30m 버퍼가 CB_ACC30M_MIN_SAMPLES 에 도달해야 CB③이 **판정 자체를**
        # 할 수 있다. 그런데 종전에는 그 사실이 어디에도 안 남아, 2026-08-20에
        # `acc30m < 0.28` 이 236분(64.0%)인데 HALT 0회인 것을 로그만으로 화해시킬
        # 수 없었다("표본이 없어 판정을 안 한 것"인지 "판정했는데 통과한 것"인지).
        # 스케일러 재적합이 버퍼를 리셋하면 표본이 되감기므로, 재적합 빈도가
        # CB③ 가용시간을 얼마나 깎는지도 함께 센다(482차 G-2).
        self._cb3_resets_today: int = 0          # 실제 리셋된 횟수(스킵 제외)
        self._cb3_samples_dropped_today: int = 0  # 리셋으로 버린 표본 수

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

        # GBM 재학습 중 CB⑤ 임계 완화 플래그
        # 재학습 스레드가 sklearn GIL을 간헐적으로 보유해 S2가 ~5s 블로킹되는 정상 현상.
        # True 동안 PAUSE 기준을 CB_PIPE_PAUSE_MS × 2 로 완화해 오발동 방지.
        self._gbm_retrain_active: bool = False

        # HALT 원인 코드 — 선택적 해제 판단용
        # "cb2": 연속 손절 (전략 실패 → 당일 해제 불가)
        # "cb3": 30분 정확도 저하 (데이터 품질 문제 → ConstOut 회복 시 해제 가능)
        self._halt_cause: str = ""

        # [225차 P2] reset_acc30m_buffer() 후 쿨다운 — 재적합 직후 CB③ 재트리거 방어.
        # 버퍼 리셋 직후 샘플이 충분히 쌓이기 전(≤15샘플) 연속 오답으로 즉시 재HALT되는 문제.
        self._cb3_reset_cooldown_samples: int = 0

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

    @property
    def cb3_samples(self) -> int:
        """[MW0601 482차 / G-1] 현재 acc30m 버퍼에 쌓인 표본 수."""
        return len(self._accuracy_buf)

    @property
    def cb3_ready(self) -> bool:
        """[MW0601 482차 / G-1] CB③이 지금 **판정 가능한** 상태인가.

        `record_accuracy()` 의 평가 분기는 `len(buf) >= CB_ACC30M_MIN_SAMPLES` 를
        전제한다. 그 아래면 acc30m 값이 존재해도 CB③은 아무 판정도 하지 않는다.

        ⚠ 리셋 쿨다운(`_cb3_reset_cooldown_samples`, 15)은 여기 반영하지 않는다 —
          쿨다운 상한 15 < 최소표본 30 이라 표본 조건이 충족되면 쿨다운은 이미
          풀려 있다. 두 상수의 대소가 바뀌면 이 전제가 깨지므로 함께 볼 것.
        ⚠ Contrarian/EKS ACTIVE 구간은 누적은 하되 발동만 스킵하는데, 그 상태는
          CB 가 들고 있지 않아(호출부 인자) 여기서 알 수 없다. 이 값은 **버퍼 축**
          가용성이다.
        """
        return len(self._accuracy_buf) >= CB_ACC30M_MIN_SAMPLES

    @property
    def cb3_acc30m(self):
        """[MW0601 490차 / F-G] 현재 acc30m 값. 표본이 없으면 **None**(미측정).

        ⚠ `status_dict()["accuracy_30m"]` 은 빈 버퍼에서 `0/1 = 0.0` 을 돌려주므로
          「무정보」와 「정확도 0%」가 같은 값이 된다 — 그래서 그쪽 대신 이 프로퍼티를
          판정 계측에 쓴다(계측 4원칙 ②·④. `recent_accuracy()` 가 빈 버퍼에 조용히
          0.5 를 돌려주던 457차 사고와 같은 계열).

        🔴 읽기 전용이다 — **HALT 경로는 손대지 않는다**(CB③ 재상정 금지 사안).
        """
        if not self._accuracy_buf:
            return None
        return sum(self._accuracy_buf) / len(self._accuracy_buf)

    @property
    def cb3_would_halt(self) -> bool:
        """[MW0601 490차 / F-G] 지금 CB③ **발동 조건이 성립하는가**(HALT 여부가 아니다).

        `cb3_ready`(판정 가능한가) 와 다른 질문이다 — 482차 G-1 은 가용 분수만 셌고
        「가용한데 임계 미달인 분수」는 아무 데도 남지 않았다. 2026-08-24 실측:
        그 조건이 **30분 성립**했고 그 창에서 2포지션 -128,195원이 났는데, 그 사실이
        운영 로그 어디에도 없었다(`[DBG-CB]` DEBUG 채널 한 줄에만 있었고
        `[CB③ 비활성]` 은 `logger.debug` × `LOG_LEVEL=INFO` 라 0건 출력).

        ⚠ 이 값은 **판정에 관여하지 않는다.** CB③ 자동진입 차단은
          `CB3_P4_GRADE_BLOCK_ENABLED=False` 한시예외로 비활성이며(절대원칙 §2),
          이 프로퍼티는 그 예외를 되돌리자는 제안이 아니라 **되돌릴지 판단할 근거를
          만드는 계측**이다.
        """
        if not self.cb3_ready:
            return False
        acc = self.cb3_acc30m
        return acc is not None and acc < CB_ACCURACY_MIN_30M

    @property
    def cb3_availability(self) -> dict:
        """[MW0601 482차 / G-1·G-2] 가용성 스냅샷 — EOD 집계용."""
        return {
            "samples":         len(self._accuracy_buf),
            "min_samples":     CB_ACC30M_MIN_SAMPLES,
            "ready":           len(self._accuracy_buf) >= CB_ACC30M_MIN_SAMPLES,
            "resets_today":    self._cb3_resets_today,
            "samples_dropped": self._cb3_samples_dropped_today,
            # [MW0601 490차 / F-G] 값 자체 — None 이면 표본 없음(미측정).
            "acc30m":          self.cb3_acc30m,
            "would_halt":      self.cb3_would_halt,
            "threshold":       CB_ACCURACY_MIN_30M,
        }

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
    def _prune_stop_events(self, now: datetime.datetime) -> None:
        """시간창(CB_CONSEC_STOP_WINDOW_SEC) 밖 손절 사건을 버린다."""
        cutoff = now - datetime.timedelta(seconds=CB_CONSEC_STOP_WINDOW_SEC)
        while self._stop_events and self._stop_events[0][0] < cutoff:
            self._stop_events.popleft()
        self._consec_stops = len(self._stop_events)

    def record_stop_loss(self, position_key: Optional[str] = None):
        """손절 1건 기록 — **포지션 단위**, 시간창 안에서만 센다.

        [MW0601 489차 / A-1 스테이지1] 절대원칙 ②의 문구(*"5분 내 손절 3연속"*)에
        계측을 맞춘다. 두 가지가 없었다:

          ① **시간창** — 종전엔 승리 레그로만 리셋돼, 하루 종일 흩어진 손절도
             "연속"으로 쌓였다.
          ② **포지션 단위** — 호출부가 청산 **레그** 단위 4곳이라 한 포지션의
             계단식 손절(부분청산 → 최종청산)이 2카운트를 만들었다.
             계측 4원칙 ①(단위 명시)의 CB② 판이다.

        Args:
            position_key: 포지션 식별자(권장: `result["entry_ts"]`). 같은 키의
                추가 레그는 **새 사건으로 세지 않는다**. `None`이면 중복 제거를
                할 수 없으므로 레그마다 별도 사건이 된다(구버전 호환 경로) —
                그 경우 어떤 호출부인지 로그에 남겨 폴백을 가시화한다(원칙 ④).
        """
        now = now_kst()
        self._prune_stop_events(now)

        if position_key is None:
            logger.warning(
                "[CB] 손절 기록에 position_key 가 없다 — 레그 단위로 센다"
                "(중복 카운트 가능, 계측 4원칙 ①·④)")
        elif any(k == position_key for _, k in self._stop_events):
            # 같은 포지션의 추가 청산 레그 — 사건이 아니다.
            logger.info(
                "[CB] 같은 포지션의 추가 손절 레그 — 카운트하지 않는다 "
                "(key=%s, 현재 %d회)", position_key, self._consec_stops)
            return

        self._stop_events.append((now, position_key))
        self._consec_stops = len(self._stop_events)
        logger.warning(
            "[CB] 연속 손절 %d회 (%d초 창, 포지션 단위)",
            self._consec_stops, CB_CONSEC_STOP_WINDOW_SEC)
        if self._consec_stops >= CB_CONSEC_STOP_LIMIT:
            self._trigger_halt(
                "연속 손절 %d회/%d초 — 당일 정지"
                % (self._consec_stops, CB_CONSEC_STOP_WINDOW_SEC), cause="cb2")

    def record_win(self):
        self._stop_events.clear()
        self._consec_stops = 0   # 수익 시 카운터 초기화

    # ── 트리거 ③ 정확도 저하 (30분 호라이즌 전용) ───────────────
    def record_accuracy(self, correct: bool, confidence: float = 1.0,
                        contrarian_active: bool = False,
                        eks_active: bool = False):
        """
        Args:
            correct:            예측 적중 여부
            confidence:         예측 신뢰도 (과신·중간신뢰도 오류 감지에 사용)
            contrarian_active:  Contrarian 모드 활성 여부.
                                True이면 accuracy_buf 누적 및 CB③ 경고를 스킵.
            eks_active:         EKS(Early Kill Switch) 활성 여부.
                                True이면 누적·P4 갱신은 유지하되 HALT/경고 발동만 스킵.
                                (EKS = 이미 당일 관망 → CB③ 중복 당일 정지 불필요)
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

        if contrarian_active or eks_active:
            return  # HALT/경고 발동만 스킵, 누적은 이미 위에서 완료

        # [225차 P2] 버퍼 리셋 후 쿨다운 중 — CB③ warn 누적 억제
        # 재적합 직후 샘플 부족 시 즉시 재HALT 방지 (쿨다운=15샘플)
        if self._cb3_reset_cooldown_samples > 0:
            if len(self._accuracy_buf) <= self._cb3_reset_cooldown_samples:
                return  # 쿨다운 기간 — HALT/경고 발동 억제
            else:
                self._cb3_reset_cooldown_samples = 0  # 쿨다운 해제

        # CB③ acc30m HALT 트리거 — 비활성화(2026-06-25) → 30m 퇴역 확정(296차, 2026-07-06)
        # 250차 시점 사유: need_add 피처 미탑재로 CV acc=0.2796, CB③ 오발동 반복.
        # 296차 확정 사유: 피처 8개 탑재(292차) 후 EOD full_cv 결과도 acc=0.3052로
        #   재활성화 기준 미달 — 30m은 앙상블·CB③ 모두에서 영구 제외로 최종 결정.
        #   _accuracy_buf 누적·P4 stage 추적·DriftRetrain은 모니터링용으로 계속 유지.
        if len(self._accuracy_buf) >= CB_ACC30M_MIN_SAMPLES:
            acc = sum(self._accuracy_buf) / len(self._accuracy_buf)
            _n_samples = len(self._accuracy_buf)
            effective_min = (
                CB_ACCURACY_MIN_30M_STRICT
                if (self._high_conf_wrong_streak >= CB_HIGH_CONF_WRONG_LIMIT
                    or self._mid_conf_wrong_streak >= CB_MID_CONF_WRONG_LIMIT)
                else CB_ACCURACY_MIN_30M
            )
            if acc < effective_min:
                # HALT/경고 발동 없음 — 로그만 기록
                logger.debug(
                    "[CB③ 비활성] acc30m=%.1f%% < %.0f%% n=%d (30m 피처 미탑재 기간 중 발동 억제)",
                    acc * 100, effective_min * 100, _n_samples,
                )
            else:
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

    def set_gbm_retrain_active(self, active: bool) -> None:
        """GBM 재학습 시작/완료 시 호출 — CB⑤ PAUSE 임계 일시 완화."""
        self._gbm_retrain_active = active

    # ── 트리거 ⑤ 파이프라인 처리시간 (Cybos CB⑤ 대체) ──────────
    def record_pipe_latency(self, pipe_ms: float):
        """매분 파이프라인 처리시간 감시.

        Cybos Plus는 COM 콜백 기반으로 네트워크 RTT 측정 불가.
        파이프라인 실행시간(run_minute_pipeline 경과)을 CB⑤ 대체 지표로 사용.

        > CB_PIPE_WARN_MS (1초) : WARNING 로그
        > CB_PIPE_PAUSE_MS (5초): 5분 진입 정지 + Slack 알림

        예외1: 09:00~09:10 장 시작 직후는 EarlyWarmup·GBM PreRetrain이 겹쳐 느림.
               이 구간은 9000ms로 완화.
        예외2: 장중 GBM 재학습 실행 중(_gbm_retrain_active=True)은 파이프라인이
               구조적으로 3~5초대까지 느려진다. CB_PIPE_PAUSE_MS × 2로 완화.
               [402차 후속7 주석 정정] 종전 주석은 원인을 "sklearn GIL 간헐 보유"로
               설명했으나, 재학습은 main.py:_start_gbm_retrain_subprocess()가 띄우는
               64비트 **독립 subprocess**라 GIL을 공유하지 않는다. 실제 원인은
               20000행 × 6호라이즌 학습(~35초)이 코어를 점유하는 CPU 경합이다.
               완화 조치 자체는 그대로 타당하며 값도 변경하지 않는다.
               (2026-07-30 실측: 재학습 직후 분 파이프라인 3116~4385ms)
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
        if _open_burst:
            _pause_threshold = 9_000
        elif getattr(self, "_gbm_retrain_active", False):
            _pause_threshold = CB_PIPE_PAUSE_MS * 2   # GBM GIL 완화: 5000→10000ms
        else:
            _pause_threshold = CB_PIPE_PAUSE_MS

        # P5: PAUSE 발동 원인 진단을 위해 retrain_active·임계값·완화사유를 로그에 포함
        _retrain_tag = (
            " [GBM재학습중→임계×2]" if getattr(self, "_gbm_retrain_active", False)
            else (" [장시작버스트→임계9s]" if _open_burst else "")
        )
        if pipe_ms >= _pause_threshold:
            if self._state not in (CB_STATE_PAUSED, CB_STATE_HALTED):
                notify_circuit_breaker(
                    f"파이프라인 {pipe_ms:.0f}ms 지연",
                    "5분 진입 정지",
                )
            self._trigger_pause(
                5,
                f"파이프라인 {pipe_ms:.0f}ms — 처리 지연{_retrain_tag} (임계={_pause_threshold:.0f}ms)"
            )
        elif pipe_ms >= CB_PIPE_WARN_MS:
            _open_tag = " [장시작 버스트]" if _open_burst else ""
            msg = (
                f"[CB⑤] 파이프라인 {pipe_ms:.0f}ms 경고 "
                f"(기준 {CB_PIPE_WARN_MS:.0f}ms){_open_tag}{_retrain_tag}"
            )
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

    def _trigger_halt(self, reason: str, cause: str = ""):
        # HALTED 상태에서는 재발동 금지 (중복 슬랙 전송 방지)
        if self._state == CB_STATE_HALTED:
            return
        self._halt_cause = cause
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

    def reset_acc30m_buffer(self) -> bool:
        """스케일러 재적합 완료 후 acc30m 버퍼 초기화.

        ConstOut 재적합 완료 시점 이전 예측은 노후 스케일러 기반 → 신뢰 불가.
        CB③ 경고 카운터도 리셋해 새 스케일러 기준에서 재카운트한다.

        [277차] ConstOut 재적합이 ~30분 쿨다운마다 반복 발생하는 구간에서는
        이 함수도 같은 주기로 호출되는데, 기존엔 호출될 때마다 무조건 clear()해
        버퍼가 CB_ACC30M_MIN_SAMPLES(30)에 도달하기 전에 계속 리셋되는 "영구 기아"
        상태가 됐다(P4 단계 추적·HALT 판정 모두 30표본 미만이면 평가 자체가 안 됨).
        아직 최소 표본도 못 채운 상태면 리셋을 건너뛰고 기존 표본을 유지한다 —
        deque(maxlen=30)이 오래된 표본을 자연스럽게 밀어내므로 몇 차례 재적합에
        걸쳐 표본이 섞이는 정도의 사소한 대가로 기아 상태를 막는다.

        Returns:
            True  = 실제로 리셋됨
            False = 표본 부족으로 리셋 스킵(기존 표본 유지)
        """
        if len(self._accuracy_buf) < CB_ACC30M_MIN_SAMPLES:
            msg = (
                f"[CB③] acc30m 버퍼 리셋 스킵 — 기존 표본 {len(self._accuracy_buf)}건"
                f" < 최소 {CB_ACC30M_MIN_SAMPLES}건 (기아 방지, 표본 누적 계속)"
            )
            logger.info(msg)
            log_manager.system(msg, "INFO")
            return False
        # [MW0601 482차 / G-2] 재적합이 CB③ 표본을 얼마나 되감는가 — 리셋 **전에** 센다.
        _dropped = len(self._accuracy_buf)
        self._cb3_resets_today += 1
        self._cb3_samples_dropped_today += _dropped
        self._accuracy_buf.clear()
        self._acc30m_stage = "NORMAL"
        self._cb3_warn_count = 0
        # [225차 P2] 리셋 직후 샘플 부족 구간에서 즉시 재HALT 방어
        # 15샘플 이상 누적 전까지 CB③ warn_count 누적 억제
        self._cb3_reset_cooldown_samples = 15
        msg = ("[CB③] acc30m 버퍼 리셋 (스케일러 재적합 완료 — 이전 예측 무효화, "
               "쿨다운=15샘플) | 버린 표본 %d건 · 당일 누적 리셋 %d회/표본손실 %d건"
               % (_dropped, self._cb3_resets_today, self._cb3_samples_dropped_today))
        logger.info(msg)
        log_manager.system(msg, "INFO")
        return True

    def lift_cb3_halt(self) -> bool:
        """CB③(정확도 저하)로 발동된 HALT를 원인 해소 후 해제.

        GBM 재학습 완료 시점에 ConstOut이 회복됐다고 판단하고 호출한다.

        해제 조건:
          - state == HALTED
          - _halt_cause == "cb3"  (CB②·기타 원인 HALT는 해제 불가)
          - daily_halt_count < CB_DAILY_HALT_FULL_BLOCK  (3회 이상이면 완전 관망 유지)

        반환값: True = HALT 해제됨 / False = 조건 미충족으로 해제 안 됨
        """
        if self._state != CB_STATE_HALTED:
            return False
        if self._halt_cause != "cb3":
            msg = (
                f"[CB③] HALT 해제 불가 — 원인이 CB③ 아님 (cause={self._halt_cause!r})"
            )
            logger.warning(msg)
            log_manager.system(msg, "WARNING")
            return False
        if self._daily_halt_count >= CB_DAILY_HALT_FULL_BLOCK:
            msg = (
                f"[CB③] HALT 해제 불가 — 당일 HALT {self._daily_halt_count}회 "
                f"(≥{CB_DAILY_HALT_FULL_BLOCK}) → 완전 관망 정책 유지"
            )
            logger.warning(msg)
            log_manager.system(msg, "WARNING")
            return False
        self._state = CB_STATE_NORMAL
        self._halt_cause = ""
        self._cb3_ok_streak = 0
        size_note = f"×{self.restart_size_mult:.1f}" if self.restart_size_mult < 1.0 else "풀사이즈"
        msg = (
            f"[CB③] ConstOut 회복 — HALT 해제 (당일 HALT {self._daily_halt_count}회, "
            f"진입 사이즈 {size_note})"
        )
        logger.info(msg)
        log_manager.system(msg, "INFO")
        notify_circuit_breaker(
            "ConstOut 회복 후 CB③ HALT 해제",
            f"거래 재개 (진입 사이즈 {size_note})",
        )
        return True

    def reset_daily(self):
        """장 시작 시 일간 리셋"""
        self._state = CB_STATE_NORMAL
        self._pause_until = None
        self._signal_history.clear()
        self._stop_events.clear()
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
        self._halt_cause = ""
        self._cb3_reset_cooldown_samples = 0   # [225차 P2]
        self._cb3_resets_today = 0             # [MW0601 482차 / G-2]
        self._cb3_samples_dropped_today = 0
        logger.info("[CB] 일간 리셋 완료")
        log_manager.system("[CB] 일간 리셋 완료", "INFO")

    def status_dict(self) -> dict:
        brier_avg = (sum(self._brier_buf) / len(self._brier_buf)
                     if self._brier_buf else 0.0)
        return {
            "state":                   self.state,
            "pause_until":             self._pause_until.strftime("%H:%M:%S") if self._pause_until else None,
            "consec_stops":            self._consec_stops,
            # [MW0601 489차] 카운트 단위를 값과 함께 노출한다(계측 4원칙 ①) —
            # "3회"가 레그 3개인지 포지션 3개인지 대시보드에서 구분되게.
            "consec_stop_window_sec":  CB_CONSEC_STOP_WINDOW_SEC,
            "consec_stop_unit":        "position",
            "consec_stop_limit":       CB_CONSEC_STOP_LIMIT,
            "last_latency":            self._last_latency,
            # ⚠ [MW0601 482차 / F-1] 분모의 max(len,1) 때문에 **빈 버퍼가 조용히
            #   0.0** 을 돌려준다. "표본 없음"과 "적중 0%"가 같은 값이 되는 계측
            #   4원칙 ②·④ 위반이다. 하위호환 때문에 반환 타입은 float 로 두고,
            #   대신 `accuracy_30m_measured` 를 **반드시 함께** 소비할 것
            #   (원칙 ②가 명시한 `*_measured` 동반 형태).
            "accuracy_30m":            round(sum(self._accuracy_buf) / max(len(self._accuracy_buf), 1), 3),
            "accuracy_30m_measured":   bool(self._accuracy_buf),
            "cb3_warn_count":          self._cb3_warn_count,
            "cb3_samples":             len(self._accuracy_buf),
            "cb3_min_samples":         CB_ACC30M_MIN_SAMPLES,
            "cb3_ready":               len(self._accuracy_buf) >= CB_ACC30M_MIN_SAMPLES,
            "cb3_resets_today":        self._cb3_resets_today,
            "cb3_samples_dropped":     self._cb3_samples_dropped_today,
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
            # [MW0601 489차] 정수만 저장하면 재기동 후 **시간창을 복원할 수 없다**
            # (언제 난 손절인지 모르니 영원히 안 만료된다). 사건 목록을 함께 남긴다.
            "stop_events":            [[t.isoformat(), k]
                                       for t, k in self._stop_events],
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
        # [MW0601 489차] 사건 목록이 있으면 그것이 정본이다 — 복원 직후 프루닝하면
        # 재기동 사이에 창이 지난 손절은 자동으로 만료된다. 구버전 상태(목록 없음)는
        # 정수만 복원하되 **타임스탬프를 모르므로** 창을 적용할 수 없다 —
        # 그 사실을 로그로 남긴다(계측 4원칙 ④).
        _ev = d.get("stop_events")
        self._stop_events.clear()
        if isinstance(_ev, (list, tuple)):
            for item in _ev:
                try:
                    _t = datetime.datetime.fromisoformat(str(item[0]))
                except Exception:
                    continue
                self._stop_events.append((_t, item[1] if len(item) > 1 else None))
            self._prune_stop_events(now_kst())
        else:
            self._consec_stops = int(d.get("consec_stops", 0) or 0)
            if self._consec_stops:
                logger.warning(
                    "[CB] 구버전 상태 복원 — stop_events 없음. consec_stops=%d 를 "
                    "그대로 쓰되 시간창은 적용되지 않는다(다음 손절/승리에 재동기화)",
                    self._consec_stops)
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
