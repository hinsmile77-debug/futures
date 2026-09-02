# -*- coding: utf-8 -*-
"""[MW0601 478차 후속 / FZ-1] 메인 이벤트 루프 동결 워치독.

## 왜 이 파일이 Qt를 import 하지 않는가

2026-08-19 13:41:21, 메인(Qt) 스레드가 `_qt_app.exec_()` **아래 네이티브 코드**에서
1코어 100% 스핀에 빠졌다. faulthandler 30초 덤프의 동결 전 구간에서 메인 스택은
`main.py:12666 in run`(= `exec_()`) 단독이었고 **파이썬 콜백 프레임이 하나도 없었다** —
즉 어떤 파이썬 핸들러의 무한루프가 아니라 이벤트 루프 자체가 반환하지 않는 상태였다.
그 결과 QTimer 기반 장치가 전부 동시에 죽었다:

    매분 파이프라인(STEP 1~9)  ·  15:10 강제청산(STEP 8, 절대원칙 §1)
    453차 D2 SchedForceExit 안전망  ·  CB⑤  ·  대시보드 파이프라인 워치독
    15:40 daily_close → _schedule_shutdown → _auto_shutdown  (그래서 종료도 안 됐다)

453차 D2 docstring의 *"완전 피드 스톨이 와도 이 30s QTimer는 돈다"* 는 전제는
**QTimer인 한 거짓**이다. 감시자는 이벤트 루프 밖에 있어야 하므로 이 모듈은
`threading.Thread`(daemon)만 쓰고 PyQt5·COM·로깅 프레임워크에 의존하지 않는다.

## 왜 로거 대신 파일에 직접 쓰는가

동결 시 로깅 시스템 자체가 메인 스레드 의존 경로(대시보드 append, Qt 시그널)를
포함할 수 있다. 발화 기록은 **반드시 남아야 하는 마지막 증언**이므로
`crash_fault.log`에 순수 `open(..., "a")`로 append하고 즉시 flush+fsync 한다.
faulthandler가 같은 파일에 fd로 쓰지만 둘 다 append 모드라 안전하다(30초 간격).

## 왜 복구가 아니라 `os._exit()` 인가

메인 스레드가 네이티브 코드 안에서 반환하지 않는 상태는 파이썬 레벨에서 되살릴
방법이 없다(`KeyboardInterrupt` 주입도 바이트코드 경계에서만 전달된다).
남은 선택지는 "동결 지속"과 "재기동"뿐이고, 재기동은 런처
(`start_mireuk.bat` RESTART_LOOP)와 `session_recovery_service.restore_on_startup`이
포지션·카운터를 복원하므로 **모든 시나리오에서 동결 지속보다 낫다** — 특히 포지션
보유 중이면 STEP 8 청산 감시가 부활한다.

`sys.exit()`이 아니라 `os._exit()`인 이유: 전자는 예외를 던져 메인 스레드가
처리해야 하는데 그 메인이 죽어 있다. atexit·flush도 기대할 수 없으므로 기록을
먼저 남기고 즉시 프로세스를 끊는다.

## [MW0601 480차 / G-1] 하트비트를 파일로도 내보낸다 — 진실원천은 하나다

동결 당일 `data/session_state.json`의 mtime은 **16:08**이었다. 라이브 프로세스는
13:41에 멈췄는데 EOD 재학습이 같은 파일을 쓰는 바람에 그 파일만 보면 정상으로
보였다 — **여러 프로세스가 쓰는 상태파일은 생존 판정에 쓸 수 없다.**

그래서 이 워치독이 `heartbeat_path`에 매 검사마다 작은 JSON을 쓴다. 쓰는 주체는
라이브 프로세스 **하나뿐**이므로 밖에서 mtime·`beat_age_sec`만 봐도 생존을 판정할
수 있다. `scripts/force_flat_guard.py`(F-2)가 이 파일을 읽는다.

⚠ **하트비트를 새로 만들지 않는다.** `_main_beat`(FZ-1)와 **같은 값**을 파일로
   내보낼 뿐이다 — 별도 하트비트를 두면 진실원천이 둘이 되어, 어느 쪽이 맞는지
   판정하는 세 번째 장치가 필요해진다.
⚠ 계측 4원칙 ②: 하트비트가 아직 없으면 `beat_age_sec`는 **0이 아니라 `null`**이다.
   "미측정"과 "방금 갱신됨"은 정반대 사실이다.
"""
from __future__ import annotations

import datetime
import json
import os
import threading
import time

_FAULT_LOG_DEFAULT = os.path.join("logs", "crash_fault.log")


def _parse_hhmm(text):
    """'15:45' → datetime.time. 형식이 깨지면 None(=구간 제한 없음)."""
    try:
        hh, mm = str(text).split(":")
        return datetime.time(int(hh), int(mm))
    except Exception:
        return None


def in_window(now_time, window):
    """현재 시각이 감시 구간 안인가.

    window가 None이거나 파싱 불가면 **항상 True**(구간 제한 없음)를 돌려준다 —
    설정 오타 때문에 감시가 조용히 꺼지는 쪽이 더 위험하다(계측 4원칙 ④).
    """
    if not window:
        return True
    try:
        start = _parse_hhmm(window[0])
        end = _parse_hhmm(window[1])
    except Exception:
        return True
    if start is None or end is None:
        return True
    return start <= now_time <= end


def evaluate(beat_age_sec, stall_sec, strikes_so_far, strikes_needed, watching):
    """스트라이크 판정 — **순수 함수**(테스트 대상).

    Args:
        beat_age_sec:   마지막 하트비트 이후 경과 초. None이면 아직 첫 하트비트 전.
        stall_sec:      이 값을 넘으면 1스트라이크
        strikes_so_far: 직전까지 누적 스트라이크
        strikes_needed: 발화에 필요한 연속 스트라이크
        watching:       감시 구간 안이며 활성 상태인가

    Returns:
        (new_strikes, should_fire)

    설계 노트:
      · 감시 구간 밖이면 스트라이크를 **0으로 리셋**한다. 구간 경계를 걸친 누적이
        다음 날 첫 검사에서 오발화하는 것을 막는다.
      · 하트비트가 갱신되면 즉시 0으로 리셋한다 — "연속" 조건의 정의 그 자체다.
      · beat_age가 None(하트비트 미시작)이면 판정하지 않는다. 기동 중 Qt 루프
        진입 전 구간을 동결로 오인하지 않기 위함(계측 4원칙 ② 미측정 ≠ 0).
    """
    if not watching or beat_age_sec is None:
        return 0, False
    if beat_age_sec <= stall_sec:
        return 0, False
    new_strikes = int(strikes_so_far) + 1
    return new_strikes, new_strikes >= int(strikes_needed)


class FreezeWatchdog(object):
    """메인 이벤트 루프 하트비트 감시 스레드.

    Args:
        beat_fn:      () -> float|None. 마지막 하트비트의 time.time() 값.
                      None이면 아직 하트비트가 시작되지 않은 것으로 본다.
        active_fn:    () -> bool. 감시해야 하는 상태인가(거래일 여부·자동종료 완료
                      여부 등 호출부 판단). 예외를 던지면 **감시 계속**(True)으로
                      본다 — 판단 실패로 감시가 꺼지면 안 된다.
        context_fn:   () -> str. 발화 직전 기록할 한 줄 컨텍스트(포지션 상태 등).
                      실패해도 발화를 막지 않는다.
        on_fire:      () -> None. 기본값 None이면 os._exit(exit_code).
                      테스트에서 주입해 종료를 가로챈다.
        heartbeat_path: [480차 G-1] 매 검사마다 생존 JSON을 덮어쓸 경로.
                      None이면 출력하지 않는다(기존 동작). 쓰는 주체는 라이브
                      프로세스 하나뿐이어야 한다 — 여러 프로세스가 쓰는 파일은
                      생존 판정에 쓸 수 없다(모듈 docstring 참조).
    """

    def __init__(
        self,
        beat_fn,
        active_fn=None,
        context_fn=None,
        on_fire=None,
        check_sec=30.0,
        stall_sec=180.0,
        strikes=2,
        exit_code=43,
        window=("09:00", "15:45"),
        fault_log_path=_FAULT_LOG_DEFAULT,
        ts_heartbeat=True,
        heartbeat_path=None,
        name="FreezeWatchdog",
    ):
        self._beat_fn = beat_fn
        self._active_fn = active_fn
        self._context_fn = context_fn
        self._on_fire = on_fire
        self._check_sec = float(check_sec)
        self._stall_sec = float(stall_sec)
        self._strikes_needed = int(strikes)
        self._exit_code = int(exit_code)
        self._window = window
        self._fault_log_path = fault_log_path
        self._ts_heartbeat = bool(ts_heartbeat)
        self._heartbeat_path = heartbeat_path      # [480차 G-1] None이면 미출력
        self._name = name

        self._strikes = 0
        self._stop_evt = threading.Event()
        self._thread = None
        self.fired = False          # 테스트·진단용 — 발화했는가

    # ── 수명주기 ────────────────────────────────────────────────────────

    def start(self):
        if self._thread is not None:
            return
        self._thread = threading.Thread(target=self._run, name=self._name, daemon=True)
        self._thread.start()
        self._write_fault_line(
            "[FreezeWatchdog] START stall=%.0fs strikes=%d check=%.0fs window=%s"
            % (self._stall_sec, self._strikes_needed, self._check_sec, self._window)
        )

    def stop(self):
        self._stop_evt.set()

    # ── 감시 루프 ───────────────────────────────────────────────────────

    def _run(self):
        while not self._stop_evt.wait(self._check_sec):
            try:
                self.check_once()
            except Exception:
                # 감시자가 예외로 죽으면 감시가 조용히 사라진다 — 절대 올리지 않는다.
                try:
                    self._write_fault_line("[FreezeWatchdog] 검사 예외 — 계속 감시")
                except Exception:
                    pass

    def check_once(self, now=None):
        """1회 검사. 반환: 발화했으면 True. (테스트에서 직접 호출한다)"""
        now = now or datetime.datetime.now()
        watching = in_window(now.time(), self._window) and self._is_active()

        beat = None
        try:
            beat = self._beat_fn()
        except Exception:
            beat = None
        # ⚠ `if not beat` 로 쓰지 말 것 — epoch 0.0이 falsy라 "하트비트 없음"과
        #   구분되지 않는다. 그것이 정확히 계측 4원칙 ②가 금지하는 혼동이고,
        #   여기서는 "미측정(판정 보류)"과 "무한히 낡음(발화)"이 정반대 결과다.
        age = None if beat is None else max(0.0, time.time() - float(beat))

        if self._ts_heartbeat:
            self._write_fault_line(
                "[TS] %s beat_age=%s watching=%s strikes=%d"
                % (
                    now.isoformat(timespec="seconds"),
                    "N/A" if age is None else "%.0fs" % age,
                    watching,
                    self._strikes,
                )
            )

        self._write_heartbeat_file(now, beat, age, watching)

        self._strikes, should_fire = evaluate(
            age, self._stall_sec, self._strikes, self._strikes_needed, watching
        )
        if not should_fire:
            return False
        self._fire(now, age)
        return True

    def _is_active(self):
        if self._active_fn is None:
            return True
        try:
            return bool(self._active_fn())
        except Exception:
            return True     # 판단 실패 시 감시를 끄지 않는다

    # ── 발화 ────────────────────────────────────────────────────────────

    def _fire(self, now, age):
        self.fired = True
        ctx = ""
        try:
            if self._context_fn is not None:
                ctx = str(self._context_fn())
        except Exception as exc:
            ctx = "context_fn 실패: %s" % (exc,)

        self._write_fault_line(
            "\n%s\n"
            "[FreezeWatchdog] CRITICAL 메인 이벤트 루프 동결 판정 — 하드 종료\n"
            "  시각      : %s\n"
            "  하트비트  : %s 경과 (임계 %.0fs × %d회 연속)\n"
            "  상태      : %s\n"
            "  조치      : os._exit(%d) — 런처 RESTART_LOOP가 재기동 (15:10 이후면 재기동 없음)\n"
            "  근거      : 2026-08-19 13:41:21 동결 사고 / dev_memory DECISION_LOG 478차 후속\n"
            "%s"
            % (
                "=" * 64,
                now.isoformat(timespec="seconds"),
                "N/A" if age is None else "%.0fs" % age,
                self._stall_sec,
                self._strikes_needed,
                ctx or "(컨텍스트 없음)",
                self._exit_code,
                "=" * 64,
            )
        )

        if self._on_fire is not None:
            # 주입된 콜백(리허설·테스트)은 프로세스를 끊지 않으므로, 감시 루프를
            # 여기서 멈춘다. 안 그러면 매 검사마다 재발화해 로그를 덮는다.
            # 운영 경로(아래 os._exit)는 애초에 돌아오지 않으므로 무관하다.
            self._stop_evt.set()
            self._on_fire()
            return
        os._exit(self._exit_code)

    # ── [480차 G-1] 생존 하트비트 파일 ─────────────────────────────────

    def _write_heartbeat_file(self, now, beat, age, watching):
        """밖에서 읽을 수 있는 생존 신호를 원자적으로 덮어쓴다.

        원자성(tmp → os.replace)이 필요한 이유: 읽는 쪽(`force_flat_guard.py`)이
        15:12에 딱 한 번 읽고 그 결과로 절대원칙 §1 경보를 낼지 정한다. 반쯤 쓰인
        JSON을 읽고 파싱에 실패하면 "프로세스 죽음"으로 오판할 수 있다.

        실패는 삼킨다 — 하트비트를 못 써서 감시자가 죽으면 본말전도다. 대신 파일이
        아예 갱신되지 않는 것 자체가 읽는 쪽에서 "낡음"으로 보이므로 안전측 오류다.
        """
        if not self._heartbeat_path:
            return
        try:
            d = os.path.dirname(self._heartbeat_path)
            if d:
                os.makedirs(d, exist_ok=True)
            payload = {
                "pid": os.getpid(),
                "written_at": now.isoformat(timespec="seconds"),
                "beat_epoch": None if beat is None else float(beat),
                # ⚠ 계측 4원칙 ② — 하트비트 미시작은 0이 아니라 null이다.
                "beat_age_sec": None if age is None else round(float(age), 1),
                "watching": bool(watching),
                "strikes": int(self._strikes),
                "stall_sec": self._stall_sec,
                "strikes_needed": self._strikes_needed,
                "check_sec": self._check_sec,
                "window": list(self._window),
                "fired": bool(self.fired),
            }
            tmp = self._heartbeat_path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False)
                f.flush()
                try:
                    os.fsync(f.fileno())
                except Exception:
                    pass
            os.replace(tmp, self._heartbeat_path)
        except Exception:
            pass

    # ── fault 로그 직접 append ──────────────────────────────────────────

    def _write_fault_line(self, text):
        """로깅 프레임워크를 거치지 않고 파일에 직접 쓴다(모듈 docstring 참조).

        ⚠ **`encoding="utf-8"`을 반드시 명시한다.** py37_32 런타임의
        `locale.getpreferredencoding()`은 `cp949`이고, cp949는 em dash(U+2014 —)를
        인코딩하지 못한다. 기본 인코딩으로 열면 `UnicodeEncodeError`가 나고 아래
        `except`가 그것을 삼켜 **발화 기록이 통째로 사라진다**(개발 중 실측).
        이 함수가 남기는 것은 동결 프로세스의 마지막 증언이므로 유실이 곧 실명이다.
        `errors="replace"`는 앞으로 어떤 문자가 섞여도 기록 자체는 남게 하는 2차
        방어다 — 한 글자를 잃는 것이 한 줄을 잃는 것보다 낫다.
        (faulthandler는 같은 파일에 fd로 ASCII를 직접 쓴다 — append 모드끼리라 안전)
        """
        if not self._fault_log_path:
            return
        try:
            d = os.path.dirname(self._fault_log_path)
            if d:
                os.makedirs(d, exist_ok=True)
            with open(self._fault_log_path, "a", encoding="utf-8", errors="replace") as f:
                f.write(text + "\n")
                f.flush()
                try:
                    os.fsync(f.fileno())
                except Exception:
                    pass
        except Exception:
            pass    # 기록 실패가 감시를 멈추게 하지 않는다
