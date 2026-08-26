# -*- coding: utf-8 -*-
"""[MW0602 500차] F-3 회귀 — 런처 GUARD 가 **무엇을 죽였는지** 남긴다.

**무엇이 문제였나.** `launcher_guard` 가 9거래일 연속 발화 중인데(0826 이상점 `1-2`,
2026-08-27 발화 시 사전등록 규칙에 따라 P1 승격) 로그에는
`[GUARD] 기존 프로세스 종료 완료` 한 줄뿐이라 **대상이 무엇이었는지 알 수 없었다.**
두 가설 — ⓐ 전일 세션의 잔존 `MainThread` · ⓑ `main.py` 문자열 매칭이 재학습
서브프로세스를 오탐 — 은 **PID·시작시각 한 줄이면 갈린다.**

CLAUDE.md 「계측 4원칙 ③ 탈락 가시화」가 이 형태다: 필터가 무엇을 걸러냈는지
개수·대상을 남겨야 한다.

여기서 고정하는 불변식:

① **탐지 프로브가 종료 명령 *앞*에 있다** — 죽은 뒤에는 `create_time` 을 못 읽는다.
② **GUARD 동작 무변경** — 기존 `p.terminate()` 한 줄은 글자 하나 안 바뀐다.
   프로브가 실패해도(`2>NUL`) 다음 줄의 종료는 그대로 돈다. 이중 실행 방지는
   살아 있어야 한다(F-3 계획의 🔴 항).
③ **PID·시작시각·커맨드라인 세 축이 다 있다** — 하나라도 빠지면 ⓐ/ⓑ 가 안 갈린다.
④ **대상 0건도 기록한다** — "감지와 종료 사이에 사라졌다"와 "안 찍혔다"는 다르다
   (계측 4원칙 ②).
⑤ **프로브 명령줄은 순수 ASCII** — 이 배치 파일들은 UTF-8 로 저장돼 있는데 cmd 는
   CP949 로 파싱한다(byte passthrough). ECHO 리터럴은 그래서 통하지만 **명령 인자**
   안의 비ASCII 는 위험하다. 파일 인코딩·개행도 함께 고정한다.

실행:
    py37_32\\python.exe tests/test_500_guard_kill_target_log.py
"""
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAILURES = []

# 두 런처 모두 대상이다. MW0602 가 실제로 쓰는 것은 한글판이며(launcher 로그의
# `[GUARD] 기존 main.py 프로세스 체크` 가 그 증거), CREON 판은 ASCII 사본이다.
# 한쪽만 고치면 조용히 갈라진다.
#
# ⚠ `start_mireuk_CREON.bat` 은 **`.gitignore:108` 대상**(PC 로컬 런처)이라 다른 PC·
#   새 클론에는 없다. 없는 파일을 단언하면 그 환경에서 테스트가 무조건 깨진다 →
#   **존재하는 것만** 검사하되, 하나도 없으면 그것은 그것대로 실패로 본다
#   (조용히 0건 통과하면 계측이 죽은 줄 모른다 — 계측 4원칙 ②).
_CANDIDATES = ("start_mireuk.bat", "start_mireuk_CREON.bat")
LAUNCHERS = tuple(n for n in _CANDIDATES
                  if os.path.exists(os.path.join(_ROOT, n)))

TERMINATE_MARK = "p.terminate() for p in psutil.process_iter"
PROBE_MARK = "kill-target"


def _raw(name):
    return io.open(os.path.join(_ROOT, name), "rb").read()


def _text(name):
    return _raw(name).decode("utf-8")


def _lines(name):
    return _text(name).split("\r\n")


def _probe_line(name):
    hit = [l for l in _lines(name) if PROBE_MARK in l and l.startswith('"!PY32!"')]
    assert len(hit) == 1, "%s: 프로브 명령줄이 %d개" % (name, len(hit))
    return hit[0]


def test_at_least_one_launcher_is_present():
    """검사 대상이 0개면 아래 전부가 공허하게 통과한다 — 그 상태를 실패로 만든다."""
    assert LAUNCHERS, (
        "런처 배치를 하나도 못 찾았다 — 후보 %r. 이름이 바뀌었으면 "
        "`_CANDIDATES` 를 갱신하라(26주 WFA 「고착 지표 감시목록」과 같은 취지)."
        % (_CANDIDATES,))


# ── ① 프로브가 종료 명령 앞에 있다 ────────────────────────────────────────────
def test_probe_precedes_terminate():
    for name in LAUNCHERS:
        lines = _lines(name)
        probe = [i for i, l in enumerate(lines)
                 if PROBE_MARK in l and l.startswith('"!PY32!"')]
        kill = [i for i, l in enumerate(lines) if TERMINATE_MARK in l]
        assert len(probe) == 1 and len(kill) == 1, \
            "%s: probe=%r kill=%r" % (name, probe, kill)
        assert probe[0] < kill[0], \
            "%s: 프로브가 종료 뒤에 있다 — 죽은 프로세스의 시작시각은 읽을 수 없다" % name


# ── ② GUARD 동작 무변경 ───────────────────────────────────────────────────────
def test_terminate_command_is_untouched():
    """기존 종료 한 줄은 문자열 동등해야 한다 — 이중 실행 방지가 회귀하면 안 된다."""
    expected = ('"!PY32!" -c "import psutil, os; [p.terminate() for p in '
                "psutil.process_iter(['pid','name','cmdline']) if 'python' in "
                "(p.info.get('name') or '').lower() and any('main.py' in (c or '') "
                "for c in (p.info.get('cmdline') or [])) and p.pid != os.getpid()]\" 2>NUL")
    for name in LAUNCHERS:
        hit = [l for l in _lines(name) if TERMINATE_MARK in l]
        assert hit == [expected], "%s: 종료 명령이 바뀌었다\n%r" % (name, hit)


def test_probe_failure_cannot_block_termination():
    """프로브는 stderr 를 삼키고, 그 결과로 분기하지 않는다."""
    for name in LAUNCHERS:
        probe = _probe_line(name)
        assert probe.rstrip().endswith("2>NUL"), name
        lines = _lines(name)
        i = lines.index(probe)
        # 프로브 바로 뒤가 ERRORLEVEL 분기이면 실패 시 종료를 건너뛸 수 있다.
        nxt = lines[i + 1].strip().upper()
        assert not nxt.startswith("IF ") or "ERRORLEVEL" not in nxt, \
            "%s: 프로브 결과로 분기한다 — GUARD 동작이 프로브에 종속된다" % name


# ── ③ 세 축이 다 있다 ─────────────────────────────────────────────────────────
def test_probe_records_pid_start_and_cmdline():
    for name in LAUNCHERS:
        probe = _probe_line(name)
        for token in ("PID={}", "started={}", "cmd={}",
                      "create_time", "p.pid", "isoformat"):
            assert token in probe, "%s: 프로브에 %r 이 없다" % (name, token)


def test_probe_writes_to_the_launcher_log():
    """콘솔에만 찍으면 다음 날 아무것도 안 남는다 — `_BLOG` 에 append 해야 한다."""
    for name in LAUNCHERS:
        probe = _probe_line(name)
        assert "os.environ.get('_BLOG')" in probe, name
        assert "'a'" in probe and "encoding='utf-8'" in probe, name


# ── ④ 0건도 기록한다 ──────────────────────────────────────────────────────────
def test_empty_target_is_still_recorded():
    """`count=` 는 무조건 한 줄 나간다 — 0건과 "안 찍힘"을 같게 만들지 않는다."""
    for name in LAUNCHERS:
        probe = _probe_line(name)
        assert "kill-target count={} probe=ok" in probe, \
            "%s: 무조건 나가는 count 줄이 없다 (계측 4원칙 ②)" % name


# ── ⑥ 🔴 500차에 발견한 결함 — 기존 GUARD 두 줄은 지금 **죽어 있다** ─────────
#
# `SETLOCAL ENABLEDELAYEDEXPANSION` 아래에서 cmd 는 `!` 를 변수 구분자로 먹는다.
# 그래서 명령줄의 `p.pid != os.getpid()` 가 **`p.pid = os.getpid()`** 로 바뀌어
# 파이썬이 `SyntaxError` 로 죽고 **종료코드 1** 을 돌려준다. 실측(2026-08-26):
#
#     "!PY32!" -c "... and p.pid != os.getpid()]; ..."
#     SyntaxError: invalid syntax
#     RC=1
#
# 귀결이 둘이다.
#   ⓐ **탐지**: `IF !ERRORLEVEL! EQU 0 GOTO :guard_no_existing` 이 절대 성립하지 않아
#      GUARD 는 **매일 "기존 프로세스 감지"** 로 분기한다 → `launcher_guard` 9거래일
#      연속 발화(0826 이상점 `1-2`)의 유력한 설명이며, 제안돼 있던 두 가설
#      (ⓐ 잔존 스레드 / ⓑ 프로세스 오탐) **어느 쪽도 아니다.**
#   ⓑ **종료**: 같은 결함이 종료 한 줄에도 있어 **아무 프로세스도 죽이지 않는다.**
#      `[GUARD] 기존 프로세스 종료 완료` 는 사실이 아니다.
#
# 🔴 **여기서 고치지 않는다.** 0826 리포트 F-3 이 *"GUARD 동작 자체는 바꾸지 않는다"*
#    라고 못박았고, 고치면 내일 08:40 부터 런처가 **실제로** 프로세스를 죽이기
#    시작한다 — 라이브 런처의 동작 변경이라 사용자 판단 사항이다.
#    `dev_memory/NEXT_TODO.md` 500차 항목으로 등록했다.
#
# 아래는 **결함 잠금(known-defect lock)** 이다. 누군가 고치면 이 테스트가 깨지고,
# 그때 NEXT_TODO 항목을 닫으라는 신호가 된다. 침묵하는 결함으로 두지 않는다.
def test_legacy_guard_lines_still_carry_the_bang_defect():
    for name in LAUNCHERS:
        legacy = [l for l in _lines(name)
                  if l.startswith('"!PY32!"') and "os.getpid()" in l
                  and PROBE_MARK not in l]
        assert len(legacy) == 2, "%s: 기존 GUARD 명령이 2줄이 아니다 (%d)" % (name, len(legacy))
        for l in legacy:
            assert "!=" in l, (
                "%s: `!=` 가 사라졌다 — 결함이 고쳐졌다면 NEXT_TODO 500차 "
                "「GUARD 명령 `!=` 결함」 항목을 닫고 이 테스트를 지워라.\n%s" % (name, l))


# ── ⑤ 인코딩·개행 규약 ────────────────────────────────────────────────────────
def test_probe_line_is_pure_ascii():
    for name in LAUNCHERS:
        probe = _probe_line(name)
        try:
            probe.encode("ascii")
        except UnicodeEncodeError as e:
            raise AssertionError("%s: 프로브 명령줄에 비ASCII 문자 — %s" % (name, e))


def test_launcher_encoding_and_eol_preserved():
    for name in LAUNCHERS:
        raw = _raw(name)
        raw.decode("utf-8")                      # UTF-8 로 읽혀야 한다
        assert not raw.startswith(b"\xef\xbb\xbf"), "%s: BOM 이 생겼다" % name
        bare_lf = raw.count(b"\n") - raw.count(b"\r\n")
        assert bare_lf == 0, "%s: bare LF %d개 — cmd 가 마지막 줄을 삼킬 수 있다" % (name, bare_lf)


def test_probe_has_no_cmd_metacharacters():
    """`%`·`!`·파이프류가 들어가면 cmd 파서가 조용히 다른 명령을 만든다."""
    for name in LAUNCHERS:
        body = _probe_line(name)[len('"!PY32!" '):]
        for ch in ("%", "!", "^", "|", "&", "<"):
            assert ch not in body, "%s: 프로브에 cmd 메타문자 %r" % (name, ch)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    for fn in (test_at_least_one_launcher_is_present,
               test_probe_precedes_terminate,
               test_terminate_command_is_untouched,
               test_probe_failure_cannot_block_termination,
               test_probe_records_pid_start_and_cmdline,
               test_probe_writes_to_the_launcher_log,
               test_empty_target_is_still_recorded,
               test_legacy_guard_lines_still_carry_the_bang_defect,
               test_probe_line_is_pure_ascii,
               test_launcher_encoding_and_eol_preserved,
               test_probe_has_no_cmd_metacharacters):
        try:
            fn()
            print("[ok]   %s" % fn.__name__)
        except Exception as e:
            print("[FAIL] %s: %r" % (fn.__name__, e))
            FAILURES.append(fn.__name__)
    print("-" * 60)
    print("전부 통과" if not FAILURES else "실패 %d건: %s" % (len(FAILURES), FAILURES))
    sys.exit(1 if FAILURES else 0)
