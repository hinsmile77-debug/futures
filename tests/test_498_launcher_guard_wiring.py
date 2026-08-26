# -*- coding: utf-8 -*-
"""[MW0601 498차 / F-2] 런처 단일 인스턴스 가드가 분리 스크립트로 배선돼 있다.

배경
----
493차 후속7(`35ed037`)이 `scripts/guard_single_instance.py` · 유닛 테스트 · 리허설을
만들었지만 **배치 배선 한 조각은 되돌렸다.** 그래서 2026-08-26에도 런처는 인라인
`python -c` 원라이너를 그대로 썼고, `[GUARD] 기존 프로세스 종료 완료`가 실제로는
아무것도 종료하지 않은 채 찍혔다(허위 로그).

인라인 원라이너의 결함 3종(493차 후속7 분석):
① 종료코드 혼동 — 크래시(exit 1)와 「N개 발견」이 같은 분기로 간다(계측 4원칙 ②)
② `2>NUL` 이 stderr 를 버려 그 크래시가 어디에도 안 남는다
③ 지연확장 `!` 파싱 — `p.pid != os.getpid()` 의 `!` 를 cmd.exe 가 먹는다

고정하는 불변식
---------------
① GUARD 블록이 `scripts\\guard_single_instance.py` 를 **probe·terminate 둘 다** 호출한다
② 인라인 `python -c` 가 GUARD 블록에서 사라졌다 (재도입 시 이 테스트가 깨진다)
③ 종료코드 0/1/3 을 **분리해서** 다룬다 — 특히 rc=3(프로브 실패)에 전용 분기가 있다
④ 「종료 완료」류 문자열이 **무조건** 찍히지 않는다 — rc 확인 뒤에만 나온다
⑤ `2>NUL` 로 가드 호출의 오류 출력을 버리지 않는다
"""
import io
import os
import re
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

_BAT = os.path.join(_ROOT, "start_mireuk.bat")


def _guard_block():
    """GUARD 블록만 떼어 본다 — 파일 전체를 보면 다른 블록의 문자열에 걸린다."""
    if not os.path.exists(_BAT):
        pytest.skip("start_mireuk.bat 없음(이 PC 미배치)")
    src = io.open(_BAT, encoding="utf-8", errors="replace").read()
    i = src.find("[GUARD] 기존 main.py 프로세스 체크")
    if i < 0:
        pytest.fail("GUARD 블록을 찾지 못했다 — 런처 구조가 바뀌었으면 이 테스트를 갱신할 것")
    j = src.find(":guard_done", i)
    return src[i:j if j > 0 else len(src)]


def test_guard_calls_separated_script():
    b = _guard_block()
    assert "guard_single_instance.py" in b, \
        "가드가 분리 스크립트를 부르지 않는다 — 493차 후속7 배선이 또 빠졌다"
    assert "--probe" in b, "탐지 경로가 없다"
    assert "--terminate" in b, "종료 경로가 여전히 인라인이다"


def test_no_inline_python_c_in_guard():
    b = _guard_block()
    assert not re.search(r'"!PY32!"\s+-c\s', b), \
        "GUARD 블록에 인라인 `python -c` 가 되돌아왔다 — `!` 파싱 사고가 재발한다"


def test_probe_failure_has_its_own_branch():
    """🔴 미측정(rc=3)을 「발견」이나 「없음」으로 뭉개지 않는다(계측 4원칙 ②)."""
    b = _guard_block()
    assert re.search(r"_GUARD_RC!?\s*(?:EQU|==)\s*3", b) or "EQU 3" in b, \
        "프로브 실패(rc=3) 전용 분기가 없다 — 크래시가 조용히 흘러간다"
    assert re.search(r"EQU\s+0\s+GOTO\s+:guard_no_existing", b), \
        "rc=0(없음) 분기가 사라졌다"


def test_completion_message_is_conditional():
    """「종료 완료」가 무조건 문자열이면 안 된다 — rc 확인 뒤에만 나온다."""
    b = _guard_block()
    for line in b.splitlines():
        if "종료" in line and ("완료" in line or "확인" in line) and "CALL :L" in line:
            # 그 줄 앞에 rc 분기가 있어야 한다.
            head = b[:b.index(line)]
            assert "_GUARD_RC" in head, \
                "종료 결과 문구가 rc 확인 없이 찍힌다: %s" % line.strip()


def test_guard_stderr_not_discarded():
    b = _guard_block()
    for line in b.splitlines():
        if "guard_single_instance.py" in line:
            assert "2>NUL" not in line, \
                "가드 호출의 오류 출력을 버리면 프로브 실패가 어디에도 안 남는다"


def test_guard_script_exit_codes_are_distinct():
    """스크립트 쪽 계약 — 0/1/3 이 서로 다른 뜻이어야 배치 분기가 성립한다."""
    import scripts.guard_single_instance as g
    assert (g.RC_NONE, g.RC_FOUND, g.RC_PROBE_FAILED) == (0, 1, 3)
    assert len({g.RC_NONE, g.RC_FOUND, g.RC_PROBE_FAILED}) == 3


def test_workdir_scoped_so_other_repos_survive():
    """WORKDIR 밖 프로세스는 종료하지 않는다 — 형제 저장소의 main.py 보호."""
    b = _guard_block()
    assert "--workdir" in b, \
        "workdir 스코프가 없으면 다른 리포의 main.py 까지 죽인다"
