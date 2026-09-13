# -*- coding: utf-8 -*-
"""[MW0602 564차 / `O-77`] 표준 스트림 재바인딩 · 임포트 시점 종료 — 전수 가드.

무엇을 막는가
-------------
**A. `sys.stdout` 을 버려서 캡처 파일을 닫는 패턴.**

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, ...)   # 🔴 금지

버려진 원래 `TextIOWrapper` 는 GC 될 때 소멸자가 **하부 buffer 를 닫는다.**
pytest 아래에서 그 buffer 는 캡처 파일이라, 이후 출력이
`ValueError: I/O operation on closed file` 로 죽는다. 명시적 `close()` 가
없으니 grep 으로 안 잡히고, 파괴 시점이 GC 에 달려 있어 **조합·순서에 따라
나타났다 사라진다** — 그래서 「파일 하나씩은 통과하는데 전체는 죽는」 상태로
남아 있었다(`O-77`).

올바른 방법은 **제자리 변경**이다. 버려지는 래퍼가 생기지 않는다:

    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

⚠ 「py37 에는 `reconfigure` 가 없다」는 주석이 6개 파일에 복제돼 있었는데
   **사실이 아니다.** `reconfigure` 는 Python 3.7 에 추가됐고 이 저장소의
   런타임 py37_32(3.7.13)에도 있다. 잘못된 전제 하나가 우회책을 퍼뜨렸다.

**면제** — 원본을 *인자로 받아 보관하는* 래퍼는 고아를 만들지 않으므로 허용한다
(`scripts/cybos_autologin.py` 의 `_TeeStream(sys.stdout, ...)`). 판정 기준은
"`sys.std*.buffer` 를 인자로 넘기는가"이지 "재대입하는가"가 아니다.

**B. 모듈 최상위 `sys.exit()` — 수집 전체를 중단시킨다.**

`def test_` 없이 최상위에서 검사 본문을 돌리고 `sys.exit()` 하는 스크립트형
파일이 `tests/` 에 있으면, pytest 가 임포트하는 순간 `SystemExit` 로
**수집이 `Interrupted`** 된다. 한 파일이 나머지 전부를 죽인다.

그런 파일은 `tests/conftest.py` 의 `collect_ignore` 에 **명시적으로** 올린다.
이 검사는 그 목록을 되읽어 대조하므로, 누군가 목록에서 빼면서 파일을 안 고치면
여기서 깨진다 — *우연한 누락*이 다시 생기지 않는다.

⚠ 손으로 관리하는 면제 목록을 두지 않는다(537차 규약: 강제 대상은 자동 식별).
"""
from __future__ import print_function

import ast
import io
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# conftest 는 pytest 경로만 덮는다 — 직접 실행 대비 두 겹 방어(conftest 규약).
from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

# 🔴 이 파일은 `sys.stdout` 을 다시 묶지 않는다 — 그것이 이 검사의 주제다.

_SCAN_DIRS = ("tests", "scripts")


def _py_files():
    for d in _SCAN_DIRS:
        base = os.path.join(_ROOT, d)
        if not os.path.isdir(base):
            continue
        for fn in sorted(os.listdir(base)):
            if fn.endswith(".py"):
                yield "%s/%s" % (d, fn), os.path.join(base, fn)


def _parse(path):
    # 검사 대상 파일의 잘못된 이스케이프 시퀀스 경고가 이 가드의 출력으로
    # 섞이지 않게 한다 — 그건 그 파일의 문제이지 이 검사의 결과가 아니다.
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        warnings.simplefilter("ignore", SyntaxWarning)
        return ast.parse(io.open(path, encoding="utf-8").read())


def _is_std_attr(node):
    """`sys.stdout` / `sys.stderr` 인가."""
    return (isinstance(node, ast.Attribute) and node.attr in ("stdout", "stderr")
            and isinstance(node.value, ast.Name) and node.value.id == "sys")


def _is_std_buffer(node):
    """`sys.stdout.buffer` / `sys.stderr.buffer` 인가."""
    return (isinstance(node, ast.Attribute) and node.attr == "buffer"
            and _is_std_attr(node.value))


def _orphaning_rebinds(tree):
    """`sys.std* = <call>(... sys.std*.buffer ...)` 을 **범위 무관**으로 찾는다.

    함수 안이라고 안전하지 않다 — 테스트가 그 함수를 부르면 똑같이 터진다
    (564차 실측: `random_entry_control._utf8_stdout()` 을 `test_428` 이 적재).
    """
    hits = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not any(_is_std_attr(t) for t in node.targets):
            continue
        val = node.value
        if not isinstance(val, ast.Call):
            continue
        args = list(val.args) + [kw.value for kw in val.keywords]
        if any(_is_std_buffer(a) for a in args):
            hits.append(node.lineno)
    return hits


def _is_main_guard(node):
    """`if __name__ == "__main__":` 인가 — 임포트 시 실행되지 않는다."""
    if not isinstance(node, ast.If):
        return False
    t = node.test
    return (isinstance(t, ast.Compare) and isinstance(t.left, ast.Name)
            and t.left.id == "__name__")


def _module_level_exits(tree):
    """임포트만으로 실행되는 `sys.exit()` / `raise SystemExit` 을 찾는다."""
    hits = []
    skip = (ast.FunctionDef, ast.ClassDef)
    if hasattr(ast, "AsyncFunctionDef"):
        skip = skip + (ast.AsyncFunctionDef,)

    def walk(body):
        for n in body:
            if isinstance(n, skip) or _is_main_guard(n):
                continue
            if isinstance(n, ast.Raise):
                exc = n.exc
                name = None
                if isinstance(exc, ast.Call) and isinstance(exc.func, ast.Name):
                    name = exc.func.id
                elif isinstance(exc, ast.Name):
                    name = exc.id
                if name == "SystemExit":
                    hits.append(n.lineno)
            for sub in ast.iter_child_nodes(n):
                if (isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute)
                        and sub.func.attr == "exit"
                        and isinstance(sub.func.value, ast.Name)
                        and sub.func.value.id == "sys"):
                    hits.append(n.lineno)
            for f in ("body", "orelse", "finalbody"):
                sub = getattr(n, f, None)
                if isinstance(sub, list):
                    walk(sub)
            for h in getattr(n, "handlers", []) or []:
                walk(h.body)

    walk(tree.body)
    return hits


def _collect_ignore():
    """`tests/conftest.py` 의 `collect_ignore` 를 **소스에서** 읽는다.

    import 하지 않는다 — conftest 는 부작용(테스트 모드 설정)이 있고, 이
    검사의 목적은 *선언된 목록*을 보는 것이지 실행 결과가 아니다.
    """
    tree = _parse(os.path.join(_ROOT, "tests", "conftest.py"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "collect_ignore":
                    out = []
                    for e in node.value.elts:
                        out.append(e.value if hasattr(e, "value") else e.s)
                    return out
    return []


def test_1_no_orphaning_stdout_rebind():
    """A — 캡처 파일을 닫는 재바인딩이 tests/ · scripts/ 어디에도 없다."""
    bad = []
    for rel, path in _py_files():
        for ln in _orphaning_rebinds(_parse(path)):
            bad.append("%s:%d" % (rel, ln))
    assert not bad, (
        "`sys.std* = <call>(sys.std*.buffer, ...)` 는 버려진 래퍼가 캡처 파일을 "
        "닫아 전체 스위트를 죽인다(O-77). `sys.stdout.reconfigure(...)` 를 쓸 것: %s" % bad)


def test_2_no_module_level_exit_in_tests():
    """B — 임포트만으로 종료하는 테스트 파일은 collect_ignore 에 올라 있어야 한다."""
    ignored = set(_collect_ignore())
    bad = []
    for rel, path in _py_files():
        fn = os.path.basename(rel)
        if not (rel.startswith("tests/") and fn.startswith("test_")):
            continue
        hits = _module_level_exits(_parse(path))
        if hits and fn not in ignored:
            bad.append("%s:%s" % (rel, hits))
    assert not bad, (
        "모듈 최상위 `sys.exit()` 은 pytest 수집을 통째로 중단시킨다. "
        "__main__ 가드로 감싸거나 conftest 의 collect_ignore 에 올릴 것: %s" % bad)


def test_3_collect_ignore_entries_exist():
    """면제 목록이 낡지 않았는가 — 없는 파일이 남아 있으면 목록을 믿을 수 없다."""
    missing = [f for f in _collect_ignore()
               if not os.path.exists(os.path.join(_ROOT, "tests", f))]
    assert not missing, "collect_ignore 에 존재하지 않는 파일이 있다: %s" % missing


def test_4_reconfigure_exists_on_this_interpreter():
    """전제 검증 — `reconfigure` 가 있어야 A 의 처방이 성립한다.

    py37 에 없다는 주석이 6개 파일에 복제돼 있었다. 그 오해가 다시 굳지 않도록
    인터프리터에 직접 묻는다.
    """
    ok = hasattr(sys.stdout, "reconfigure") or hasattr(sys.__stdout__, "reconfigure")
    assert ok, "이 인터프리터에 sys.stdout.reconfigure 가 없다 — A 의 처방을 재검토할 것"


if __name__ == "__main__":
    import pytest as _pt
    sys.exit(_pt.main([__file__, "-v"]))
