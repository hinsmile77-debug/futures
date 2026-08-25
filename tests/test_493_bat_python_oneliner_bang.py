# -*- coding: utf-8 -*-
"""[MW0601 493차 후속7 / F-U 변경 10] 배치의 `python -c` 한 줄에 맨 느낌표 금지.

## 넉 달간 거짓 경고를 찍은 결함

`start_mireuk.bat` 최상단은 `SETLOCAL EnableDelayedExpansion` 이다. 그 상태에서

    "!PY32!" -c "... and p.pid != os.getpid()]; ..."

를 실행하면 **`cmd.exe` 가 `!=` 의 느낌표를 지연확장 토큰으로 먹는다.** 파이썬에는
`p.pid = os.getpid()` 가 전달되고 `SyntaxError` 로 죽는다.

**파이썬은 예외로 죽어도 exit 1 이다.** 배치는 `IF !ERRORLEVEL! EQU 0` 하나만 보므로
「크래시」와 「N개 발견」이 같은 분기로 간다. 결과:

  · 런처 로그 11개 전수에서 `[GUARD] 기존 main.py 없음` 이 **0번**
  · 전날 정상 종료가 로그로 확인되는 날에도, **주말을 사이에 둔 월요일 아침에도** 감지
  · `terminate()` 줄도 같은 결함 — 한 번도 실행된 적이 없는데 "종료 완료"는 무조건 출력

2026-08-25 재현(`scripts/diag_guard_delayedexp.bat`, 사용자 실행):

    [A] 지연확장 ON   ->  p.pid = os.getpid()   SyntaxError, EXITCODE=1
    [B] 지연확장 OFF  ->  p.pid != os.getpid()  정상 실행, EXITCODE=0

## 이 테스트가 막는 것

가드 프로브는 `scripts/guard_single_instance.py` 로 분리해 근본 해결했다. 그러나
**다른 `-c` 한 줄에 누가 `!=` 를 쓰면 같은 사고가 재발한다.** 여기서 정적으로 막는다.

⚠ 규약은 "`!` 금지"가 아니라 **"맨 `!` 금지"** 다. `^!` 로 이스케이프했거나
지연확장을 끈 파일은 통과한다 — 실제로 쓸 수 있어야 하는 문법이다.

⚠ **더 나은 해법은 파일로 빼는 것이다.** 이스케이프는 다음 사람이 또 밟는다.
이 테스트는 최후 방어선이지 권장 패턴이 아니다.
"""
import io
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: `python -c "..."` 형태의 한 줄. 따옴표 안을 통째로 잡는다.
_DASH_C = re.compile(r'-c\s+"(?P<body>[^"]*(?:""[^"]*)*)"', re.IGNORECASE)
#: 이스케이프되지 않은 느낌표 — 앞이 `^` 가 아닌 `!`.
_BARE_BANG = re.compile(r'(?<!\^)!')


def _bat_files():
    for name in sorted(os.listdir(ROOT)):
        if name.lower().endswith(".bat"):
            yield os.path.join(ROOT, name)


def _read(path):
    raw = io.open(path, "rb").read()
    for enc in ("utf-8", "cp949", "latin-1"):
        try:
            return raw.decode(enc)
        except Exception:
            continue
    return ""


def _has_delayed_expansion(text):
    return re.search(r"EnableDelayedExpansion", text, re.IGNORECASE) is not None


#: 🔴 **F-U 배선은 아직 적용되지 않았다** — 2026-08-26 07:20 판단.
#:
#: 프로브 분리(`scripts/guard_single_instance.py`)와 리허설은 끝났으나, 런처 배치의
#: 재배선은 **되돌렸다.** 이유는 배치 파싱 자체의 위험이다:
#:   · 작업 시점의 `start_mireuk.bat` 는 **LF-only** 줄바꿈이었고(원본 0 CRLF / 644 LF),
#:     cmd.exe 는 `GOTO`/`CALL` 에서 **바이트 오프셋으로 파일을 재탐색**한다. 편집으로
#:     오프셋이 바뀌면 파서가 줄 중간에 착지할 수 있다 — 리허설에서 ASCII 줄이
#:     `'through' is not recognized` 로 쪼개지는 것을 실제로 관측했다.
#:   · 검증을 끝낼 시간이 없었다(08:40 자동기동까지 80분). 런처가 깨지면 개장 시점에
#:     프로세스가 0개가 된다 — 431차에 실제로 5회 연속 기동 실패한 전례가 있다.
#: ⇒ 런처는 HEAD 내용 그대로 되돌렸다(현재 CRLF로 정규화 — 배치 표준이라 더 안전).
#: ⇒ 재적용은 **CRLF 확정 + 전체 런처 리허설**과 함께(`NEXT_TODO.md` U-16).
#:
#: 그동안 아래 두 테스트는 **strict xfail** 이다 — 결함이 살아 있음을 숨기지 않고,
#: 누군가 고치면 xpass 로 **실패**해서 이 주석과 U-16 갱신을 강제한다.
_WIRING_PENDING = pytest.mark.xfail(
    strict=True,
    reason="F-U 런처 배선 미적용 — LF-only 배치 파싱 위험으로 되돌림(U-16). "
           "고치면 이 마크를 제거할 것")


@_WIRING_PENDING
def test_no_bare_bang_in_python_oneliners():
    """🔴 지연확장이 켜진 배치의 `python -c` 본문에 맨 `!` 가 있으면 실패한다.

    있으면 그 줄은 **실행 즉시 SyntaxError 로 죽고, 배치는 그것을 성공/발견으로
    오독한다.** 고치는 법은 두 가지, 순서대로 권장:
      ① 그 파이썬을 `scripts/*.py` 파일로 빼서 `cmd.exe` 를 통과시키지 않는다(권장)
      ② 불가피하면 `^!` 로 이스케이프한다
    """
    offenders = []
    for path in _bat_files():
        text = _read(path)
        if not text or not _has_delayed_expansion(text):
            continue
        for i, line in enumerate(text.splitlines(), 1):
            for m in _DASH_C.finditer(line):
                body = m.group("body")
                if _BARE_BANG.search(body):
                    offenders.append("%s:%d  %s"
                                     % (os.path.basename(path), i, body[:80]))
    assert not offenders, (
        "지연확장 배치의 `python -c` 본문에 맨 `!` 가 있다 — 실행 시 SyntaxError 로 "
        "죽고 배치가 그것을 오독한다.\n"
        "  → scripts/*.py 로 빼거나(권장) `^!` 로 이스케이프할 것:\n  "
        + "\n  ".join(offenders))


@_WIRING_PENDING
def test_guard_probe_is_no_longer_an_inline_oneliner():
    """가드 프로브가 **파일로 빠져 있는가** — 이스케이프로 때우지 않았는가.

    `^!` 로만 고치면 규약이 사람의 기억에 의존한다. 파일로 빼면 그 등급의 실수가
    구조적으로 불가능해지고, 유닛 테스트도 붙는다.
    """
    for name in ("start_mireuk.bat", "start_mireuk_CREON.bat"):
        path = os.path.join(ROOT, name)
        if not os.path.exists(path):
            continue
        text = _read(path)
        assert "guard_single_instance.py" in text, (
            "%s 가 분리된 가드 스크립트를 호출하지 않는다" % name)
        assert "psutil.process_iter" not in text, (
            "%s 에 인라인 psutil 프로브가 남아 있다 — 파일로 뺄 것" % name)


@_WIRING_PENDING
def test_probe_failure_has_its_own_branch():
    """🔴 「실패」와 「없음」이 갈리는가 — 이 결함의 핵심 해소.

    rc=3(프로브 실패) 분기가 없으면, 크래시가 다시 「감지됨」이나 「없음」으로
    흘러간다. 어느 쪽이든 조용한 오판이다.
    """
    for name in ("start_mireuk.bat", "start_mireuk_CREON.bat"):
        path = os.path.join(ROOT, name)
        if not os.path.exists(path):
            continue
        text = _read(path)
        assert '"3"' in text or "EQU 3" in text, (
            "%s 에 프로브 실패(rc=3) 분기가 없다" % name)
        assert "_GUARD_RC" in text, "%s 가 종료코드를 변수로 잡지 않는다" % name


@_WIRING_PENDING
def test_probe_output_goes_to_the_log_not_just_console():
    """판정 근거가 **로그에 남는가.**

    종전에는 프로브의 `print` 가 콘솔로만 갔다 — 08:40 자동 기동의 콘솔을 사람이
    보고 있을 리 없고, 실제로 `grep "실행 중 main.py"` 가 로그 11개에서 0건이었다.
    그리고 `2>NUL` 이 traceback 을 통째로 버렸다.
    """
    for name in ("start_mireuk.bat", "start_mireuk_CREON.bat"):
        path = os.path.join(ROOT, name)
        if not os.path.exists(path):
            continue
        text = _read(path)
        idx = text.find("guard_single_instance.py")
        block = text[max(0, idx - 400): idx + 900]
        assert "CALL :L" in block, "%s: 가드 출력이 로그로 안 간다" % name
        assert "2>&1" in block, (
            "%s: stderr 를 버리고 있다 — traceback 이 사라지면 원인을 못 찾는다" % name)
