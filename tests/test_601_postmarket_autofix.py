# -*- coding: utf-8 -*-
"""[MW0601 601차 후속] 장후 자동조치 3건(F-3·F-15·F-6)의 회귀 고정.

세 건 모두 **판정에 관여하지 않는 계측·문구 수정**이다. 매매 판단·주문·청산
경로는 건드리지 않았고, 이 파일도 그 사실을 함께 고정한다.

무엇을 고쳤나
-------------
* **F-3** `main.py` 접속끊김 로그가 브로커를 `키움`으로 하드코딩하고 있었다.
  2026-05-11 Cybos 전환 뒤로도 남아 있던 잔재라, Cybos가 끊겨도 로그는 키움이
  끊겼다고 적었다. 바로 다음 줄의 `notify_connection_lost()`는 이미
  `getattr(self.broker, "name", ...)`를 쓰고 있어 **같은 사건을 두 이름으로**
  기록하는 상태였다.
* **F-15** 런처가 정상 종료에도 `일시적 크래시`라고 적었다. 실행시간 통계를
  찍는 지점이 정상종료 플래그를 읽는 지점보다 **위에 있었기 때문**이다.
  ⚠ 고칠 때 줄을 옮기지 않았다 — 재시작 판단 경로(`GOTO :restart_done`)를
  건드리지 않으려고, 위쪽에 **읽기 전용 peek**(삭제하지 않음)만 넣었다.
  권위 있는 read+delete는 아래 그대로다. 그 불변식을 여기서 고정한다.
* **F-6** 점검 수집기가 `logs/mainstall_traceback_<date>.log 참조`라는 **파일명
  언급** 줄을 `Traceback` 출현으로 세어 §11에 「크래시/메모리 계열」 적신호를
  띄웠다. 진짜 트레이스백은 계속 잡아야 하므로 제외는 **파일명 접두사로 좁게**
  잡았고, 이 파일이 그 양쪽을 다 시험한다.

실행:
    conda run -n py37_32 python -m pytest tests/test_601_postmarket_autofix.py
"""
import io
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

os.environ["MIREUK_TEST_MODE"] = "1"

import pytest  # noqa: E402

_MAIN_PY = os.path.join(_ROOT, "main.py")
_LAUNCHER = os.path.join(_ROOT, "start_mireuk.bat")
_COLLECTOR = os.path.join(
    _ROOT, ".claude", "skills", "mireuk-daily-check", "scripts", "collect_evidence.py"
)


def _read(path):
    with io.open(path, encoding="utf-8", newline="") as fh:
        return fh.read()


# ------------------------------------------------------------------ F-3
class TestF3BrokerNameInDisconnectLog(object):
    """접속끊김 로그는 실제 브로커명을 따라가야 한다."""

    def test_no_hardcoded_kiwoom_in_disconnect_log(self):
        src = _read(_MAIN_PY)
        assert u'"[System] 키움 연결 끊김' not in src, (
            u"접속끊김 로그에 브로커명 '키움'이 "
            u"다시 하드코딩됐다 (F-3 회귀)"
        )

    def test_disconnect_log_uses_broker_name(self):
        src = _read(_MAIN_PY)
        assert u'"[System] %s 연결 끊김' in src, (
            u"접속끊김 로그가 브로커명 서식을 "
            u"쓰지 않는다"
        )

    def test_same_event_logged_and_notified_with_one_name(self):
        u"""로그와 알림이 **같은 원천**에서 브로커명을 가져와야 한다.

        F-3 이전에는 알림만 `getattr(...)`를 쓰고 로그는 하드코딩이라, 한 사건이
        두 이름으로 남았다. 그 비대칭이 되살아나면 여기서 깨진다.
        """
        src = _read(_MAIN_PY)
        idx = src.find(u'"[System] %s 연결 끊김')
        assert idx > 0
        window = src[idx:idx + 400]
        assert window.count(u'getattr(self.broker, "name"') >= 2, (
            u"로그와 알림이 같은 원천에서 "
            u"브로커명을 가져오지 않는다"
        )


# ------------------------------------------------------------------ F-15
class TestF15LauncherExitKind(object):
    """런처는 정상 종료를 크래시라고 적지 않는다 — 단, 재시작 경로는 무변경."""

    def test_runtime_log_is_not_hardcoded_crash(self):
        src = _read(_LAUNCHER)
        assert u"-- 일시적 크래시, 카운터 초기화." not in src, (
            u"실행시간 로그가 종료 사유와 무관하게 "
            u"'일시적 크래시'로 고정도다 (F-15 회귀)"
        )
        assert u"-- !_EXIT_KIND!, 카운터 초기화." in src

    def test_peek_precedes_runtime_log(self):
        u"""peek 은 반드시 실행시간 로그 **위**에 있어야 한다 — 순서가 이 결함의 본체였다."""
        src = _read(_LAUNCHER)
        peek = src.find(u'IF EXIST "data\\_exit_normally" SET "_EXIT_KIND=')
        gate = src.find(u"IF !_RUNTIME_MIN! GTR 5 (")
        assert peek > 0, u"peek 분기가 없다"
        assert gate > 0
        assert peek < gate, (
            u"peek 이 실행시간 로그 블록 아래로 "
            u"내려갔다 — 그러면 다시 크래시로 찍힌다"
        )

    def test_peek_does_not_consume_the_flag(self):
        u"""peek 은 **읽기 전용**이다.

        peek 이 파일을 지우면 아래 `IF DEFINED _EXIT_REASON ... GOTO :restart_done`
        이 성립하지 않아 **정상 종료 뒤에도 런처가 재시작**한다. 그 사고를 막는다.
        """
        src = _read(_LAUNCHER)
        peek_line = u'IF EXIST "data\\_exit_normally" SET "_EXIT_KIND='
        idx = src.find(peek_line)
        assert idx > 0
        line_end = src.find(u"\r\n", idx)
        assert u"DEL" not in src[idx:line_end], u"peek 이 플래그를 지운다"

    def test_authoritative_read_and_restart_path_intact(self):
        u"""권위 있는 read+delete 와 재시작 분기는 그대로 남아 있어야 한다."""
        src = _read(_LAUNCHER)
        assert u'IF EXIST "data\\_exit_normally" SET /P "_EXIT_REASON=" < "data\\_exit_normally"' in src
        assert u'IF EXIST "data\\_exit_normally" DEL "data\\_exit_normally" 2>NUL' in src
        assert u"IF DEFINED _EXIT_REASON GOTO :restart_done" in src

    def test_launcher_stays_crlf(self):
        u"""배치 파일은 CRLF 여야 한다 — LF 로 저장되면 Windows 에서 오작동한다."""
        with open(_LAUNCHER, "rb") as fh:
            data = fh.read()
        assert data.count(b"\n") == data.count(b"\r\n"), u"bare LF 가 섮였다"


# ------------------------------------------------------------------ F-6
def _load_collector():
    import importlib.util
    spec = importlib.util.spec_from_file_location("_collect_evidence_601", _COLLECTOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _digest(mod):
    entry = {"rel": "logs/20260917_WARN.log", "size": 0, "mtime": 0,
             "name": "20260917_WARN.log", "ext": ".log"}
    return mod.LogDigest(entry, mod.DEFAULT_CONFIG, "20260917")


class TestF6TracebackFalsePositive(object):
    """파일명 언급은 크래시가 아니다 — 그러나 진짜 트레이스백은 계속 잡는다."""

    def test_config_declares_narrow_exclusion(self):
        mod = _load_collector()
        excl = mod.DEFAULT_CONFIG.get("quote_exclude_by_pattern", {})
        assert excl.get("Traceback") == ["mainstall_traceback_"], (
            u"제외 토큰이 넓어졌거나 사라졌다 — "
            u"넓히면 진짜 트레이스백을 놓친다"
        )

    def test_filename_mention_is_not_counted(self):
        mod = _load_collector()
        dg = _digest(mod)
        dg._ingest(
            u"2026-09-17 13:20:01 | WARNING | [MainStall] 메인 스레드 "
            u"블로킹 7734ms — logs/mainstall_traceback_20260917.log 참조"
        )
        assert "Traceback" not in dg.quoted, (
            u"파일명 언급이 여전히 Traceback 으로 "
            u"집계된다 (F-6 회귀)"
        )

    def test_real_traceback_is_still_caught(self):
        u"""제외가 진짜 크래시까지 삼키면 안 된다 — 이게 이 수정의 유일한 위험이었다."""
        mod = _load_collector()
        dg = _digest(mod)
        dg._ingest(u"2026-09-17 13:20:02 | ERROR | Traceback (most recent call last):")
        assert "Traceback" in dg.quoted
        assert len(dg.quoted["Traceback"]) == 1

    def test_excluded_line_can_still_match_other_patterns(self):
        u"""제외는 `continue` 여야 한다.

        `break` 로 빠지면 그 줄이 **뒤쪽 패턴 전부**에서도 사라진다. 같은 줄에
        「메인 스레드 블로킹」이 함께 있으므로, 그 버킷에는 정상적으로 들어가야 한다.
        """
        mod = _load_collector()
        dg = _digest(mod)
        dg._ingest(
            u"2026-09-17 13:20:01 | WARNING | 메인 스레드 블로킹 "
            u"7734ms — logs/mainstall_traceback_20260917.log 참조"
        )
        assert "Traceback" not in dg.quoted
        assert u"메인 스레드 블로킹" in dg.quoted, (
            u"제외가 break 로 동작해 다른 패턴까지 "
            u"가렸다"
        )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
