# -*- coding: utf-8 -*-
"""[MW0601 483차 후속4 / P2-H] 캠페인 스텝이 인쇄 때문에 죽지 않는다.

## 무엇을 막는가

2026-08-21 EOD 검증 캠페인 12스텝 중 「월간 로그 정리」가 **작업을 한 줄도 하기 전에**
죽었다(`rc=1`). `main()` 배너의 em-dash(U+2014)를 **cp949 파이프**에 쓰다 `print` 자체가
`UnicodeEncodeError` 를 던졌기 때문이다. 캠페인 스텝은 금요일 EOD 에만 도는데, 그날이
479차 배선 이후 **첫 자동 실행**이었고 첫 시도에서 실패했다.

    2026-08-21 16:05:54 [검증 캠페인] 월간 로그 정리 → 실패 (rc=1)
      File "scripts/monthly_cleanup.py", line 366, in main
        print("  DB 정리 :", ... "**비활성** — 켜려면 --allow-db-prune")
    UnicodeEncodeError: 'cp949' codec can't encode character '\\u2014'

## 왜 문자열을 고치지 않는가

그 파일에 cp949 로 인코딩 불가능한 문자가 `—` `≈` `═` `⚠` `🔴` **5종 359회** 있다.
한 줄을 고쳐도 다음 `print` 에서 같은 자리에 다시 선다. 고칠 곳은 문자열이 아니라
**스트림 인코딩**이며, 처방은 두 겹이다:

    (1) 자식 스크립트가 자기 stdout/stderr 를 UTF-8 로 재설정한다  (수동 실행 보호)
    (2) 호출부가 PYTHONIOENCODING=utf-8 로 12스텝 전부를 띄운다     (근본 처방)

(2)가 근본인 이유: 2026-08-21 에 나머지 11스텝이 통과한 것은 **그 문자를 안 썼을 뿐**
이고, 출력 문구가 바뀌면 언제든 재발한다. 개별 스크립트를 하나씩 고치는 것은
두더지잡기다.
"""
import ast
import io
import os
import subprocess
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MC = os.path.join(_ROOT, "scripts", "monthly_cleanup.py")
_CS = os.path.join(_ROOT, "scripts", "campaign_steps.py")

#: 이 저장소 스크립트에 실제로 등장하는 cp949 불가 문자들.
_CP949_HOSTILE = ["—", "≈", "═", "⚠", "\U0001f534"]


def _tree(path):
    return ast.parse(io.open(path, encoding="utf-8").read())


def _func(tree, name):
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef) and n.name == name:
            return n
    return None


# ── (1) 자식 쪽 ──────────────────────────────────────────────────────

def test_monthly_cleanup_forces_utf8_before_any_print():
    """재설정이 **첫 print 보다 앞**이어야 한다 — 배너에서 죽은 사고 그 자체다."""
    tree = _tree(_MC)
    main = _func(tree, "main")
    assert main is not None, "monthly_cleanup.main() 이 사라졌다"

    calls = [n.lineno for n in ast.walk(main)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
             and n.func.id == "_force_utf8_stdio"]
    assert calls, "main() 이 _force_utf8_stdio() 를 부르지 않는다"

    prints = [n.lineno for n in ast.walk(main)
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
              and n.func.id == "print"]
    if prints:
        assert min(calls) < min(prints), (
            "첫 print(line %d)가 인코딩 재설정(line %d)보다 앞이다 — "
            "그 사이의 출력은 여전히 cp949 로 나간다" % (min(prints), min(calls)))


def test_force_utf8_survives_missing_reconfigure():
    """`reconfigure` 가 없는 스트림에서도 죽으면 안 된다 — 정리 작업이 인쇄 때문에

    죽는 일이 다시 있어서는 안 되므로, 이 헬퍼는 **어떤 경우에도 예외를 내지 않는다.**
    """
    src = io.open(_MC, encoding="utf-8").read()
    fn = _func(ast.parse(src), "_force_utf8_stdio")
    assert fn is not None
    handlers = [n for n in ast.walk(fn) if isinstance(n, ast.ExceptHandler)]
    assert handlers, "try/except 없이 reconfigure 를 부르면 구형 스트림에서 죽는다"


def test_pipe_with_cp949_does_not_crash():
    """실제 파이프 + cp949 에서 적대적 문자를 인쇄해 본다(기능 검증)."""
    code = (
        "import sys, os; sys.path.insert(0, os.path.join(%r, 'scripts'));"
        "import monthly_cleanup as m; m._force_utf8_stdio();"
        "print(%r)" % (_ROOT, "".join(_CP949_HOSTILE))
    )
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "cp949"          # 최악 조건
    p = subprocess.run([sys.executable, "-c", code], env=env, cwd=_ROOT,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120)
    out = (p.stdout or b"").decode("utf-8", errors="replace")
    assert p.returncode == 0, "cp949 파이프에서 죽었다:\n%s" % out
    assert "—" in out, "em-dash 가 보존되지 않았다 (인코딩이 UTF-8 이 아니다)"


# ── (2) 호출부 ───────────────────────────────────────────────────────

def test_campaign_steps_passes_utf8_env_to_every_step():
    """근본 처방 — 12스텝 **전부**가 UTF-8 로 뜬다."""
    src = io.open(_CS, encoding="utf-8").read()
    assert '"PYTHONIOENCODING"' in src or "'PYTHONIOENCODING'" in src, \
        "호출부가 PYTHONIOENCODING 을 설정하지 않는다"

    tree = ast.parse(src)
    runs = [n for n in ast.walk(tree)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
            and n.func.attr == "run"
            and isinstance(n.func.value, ast.Name) and n.func.value.id == "subprocess"]
    assert runs, "subprocess.run 호출을 찾지 못했다 — 실행 방식이 바뀌었으면 이 검사도 갱신할 것"
    for call in runs:
        kw = {k.arg for k in call.keywords}
        assert "env" in kw, (
            "subprocess.run(line %d)에 env 가 없다 — 그 스텝은 cp949 로 떠서 "
            "출력 문구에 특수문자가 들어오는 순간 죽는다" % call.lineno)


def test_caller_decodes_utf8():
    """자식을 UTF-8 로 띄웠으면 부모도 UTF-8 로 읽어야 짝이 맞는다."""
    src = io.open(_CS, encoding="utf-8").read()
    assert 'decode("utf-8"' in src, "부모가 UTF-8 로 디코드하지 않으면 로그가 깨진다"
