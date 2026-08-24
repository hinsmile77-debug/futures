# -*- coding: utf-8 -*-
"""[MW0601 490차 / F-L] `daily_close()` 에서 도달 가능한 코드는 Qt 위젯을 직접 만지지 않는다.

## 무엇을 잡는가

`daily_close()` 는 **백그라운드 스레드**(`_run_daily_close`, `main.py`)에서 돈다.
거기서 도달 가능한 어떤 메서드가 `self.dashboard.<무엇이든>` 을 직접 호출하면
GUI 스레드 밖에서 Qt 위젯을 조작하는 것이고, PyQt 에서 그것은 정의되지 않은
동작이다. 이 저장소에서 실제로 **두 번** 사고가 났다:

  · 2026-07-08 (304차 후속) — `daily_close → update_strategy_ops →
    set_fingerprint_level → refresh` 스택에서 access violation → 런처 AUTO-RESTART
    → `daily_close` 재실행이 반복되는 **크래시 루프**.
  · 2026-08-24 (490차 / 이상점 1-12, P0) — 396차 `33e0e60` 이 `daily_close()` 에
    `_poll_gbm_retrain_subprocess()` 를 심었고, 그 폴링이 `_on_gbm_retrain_done()`
    → `self.dashboard.set_model_status(...)` 까지 같은 스레드에서 실행해
    **GIL 을 쥔 채 반환하지 않는 데드락**이 됐다. 15:40:20 이후 매분 파이프라인 ·
    30 초 스케줄러 · CB · FZ-1 워치독이 전부 함께 멈췄고(프로세스는 살아 있어
    런처도 재기동하지 않았다) 마감 절차 12 종이 미실행으로 끝났다.

두 사고 사이 간격은 47 일이고 **원인 함수는 같은 계열**이다. 사람이 매번 기억해서
막을 수 있는 종류가 아니므로 정적 불변식으로 고정한다
(`test_457_fallback_visibility.py` 가 `getattr` 폴백을 고정하는 것과 같은 방식).

## 규약

워커 스레드에서 도달 가능한 지점의 대시보드 갱신은 **반드시** 아래 둘 중 하나로 한다:

    self._dashboard_call(lambda: self.dashboard.foo(...))          # 490차 F-L
    _daily_close_ui_sig.request.emit(lambda: self.dashboard.foo())  # 304차 후속

둘 다 QueuedConnection 으로 메인 이벤트 루프에 넘긴다. 이 테스트는 **감싸지 않은**
`self.dashboard.` 접근만 실패로 본다.

## 한계 (일부러 좁게 잡았다)

`self.<메서드>()` 호출만 따라간다 — 다른 객체를 경유한 간접 GUI 접근(`self.x.y.
dashboard`)이나 `getattr` 동적 호출은 못 본다. 실제 사고 둘 다 이 좁은 축에서
났으므로 그 축을 확실히 막는 쪽을 택했다. 넓히려면 검출기를 키우기 전에
"넓혔더니 무엇이 새로 걸리는가"를 먼저 확인할 것.
"""
import ast
import io
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

_MAIN = os.path.join(_ROOT, "main.py")

#: 워커 스레드가 진입하는 지점. 여기서부터 호출 그래프를 따라간다.
_ROOTS = ("daily_close",)

#: 메인 스레드로 넘기는 통로. 이 호출의 **인자**로 들어간 코드는 검사 면제다.
_DISPATCHERS = ("_dashboard_call", "emit")


def _src():
    return io.open(_MAIN, encoding="utf-8").read()


def _methods(tree):
    """main.py 최상위 클래스들의 메서드 이름 → FunctionDef."""
    out = {}
    for cls in [n for n in tree.body if isinstance(n, ast.ClassDef)]:
        for fn in cls.body:
            if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                out.setdefault(fn.name, fn)
    return out


def _is_dispatcher_call(node):
    if not isinstance(node, ast.Call):
        return False
    f = node.func
    if isinstance(f, ast.Attribute) and f.attr in _DISPATCHERS:
        return True
    return False


def _analyze(fn):
    """한 함수를 본다 → (감싸지 않은 dashboard 접근 줄번호들, 호출하는 self 메서드 이름들)."""
    # ① 디스패처 인자로 넘어간 서브트리 = 면제 영역
    exempt_nodes = set()
    exempt_names = set()
    for node in ast.walk(fn):
        if _is_dispatcher_call(node):
            for arg in node.args:
                if isinstance(arg, ast.Name):
                    exempt_names.add(arg.id)          # 이름으로 넘긴 중첩 함수
                for sub in ast.walk(arg):
                    exempt_nodes.add(id(sub))
    # 이름으로 넘긴 중첩 def 의 본문도 면제 영역이다(그 함수는 메인에서 돈다).
    for node in ast.walk(fn):
        if isinstance(node, ast.FunctionDef) and node.name in exempt_names:
            for sub in ast.walk(node):
                exempt_nodes.add(id(sub))

    bad, calls = [], set()
    for node in ast.walk(fn):
        if id(node) in exempt_nodes:
            continue
        # self.dashboard.<attr>
        if (isinstance(node, ast.Attribute)
                and isinstance(node.value, ast.Attribute)
                and node.value.attr == "dashboard"
                and isinstance(node.value.value, ast.Name)
                and node.value.value.id == "self"):
            bad.append((node.lineno, node.attr))
        # self.<method>(...)
        if (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "self"):
            calls.add(node.func.attr)
    return bad, calls


def _reachable(methods, roots):
    seen, stack = set(), list(roots)
    while stack:
        name = stack.pop()
        if name in seen or name not in methods:
            continue
        seen.add(name)
        _, calls = _analyze(methods[name])
        stack.extend(calls)
    return seen


def test_daily_close_경로에_직접_GUI_호출이_없다():
    tree = ast.parse(_src())
    methods = _methods(tree)
    for r in _ROOTS:
        assert r in methods, "main.py 에 %s() 가 없다 — 이름이 바뀌었으면 이 검사도 갱신할 것" % r

    offenders = []
    for name in sorted(_reachable(methods, _ROOTS)):
        bad, _ = _analyze(methods[name])
        for lineno, attr in bad:
            offenders.append("main.py:%d  %s() → self.dashboard.%s" % (lineno, name, attr))

    assert not offenders, (
        "daily_close() 백그라운드 스레드에서 도달 가능한 지점이 Qt 위젯을 직접 만진다 "
        "(490차 F-L 회귀). `self._dashboard_call(lambda: ...)` 로 감쌀 것:\n  "
        + "\n  ".join(offenders)
    )


def test_디스패처_헬퍼가_존재하고_스레드를_판정한다():
    """`_dashboard_call` 이 있어야 위 검사가 의미를 갖는다.

    그리고 그것이 **판정 없이 무조건 emit** 하면 안 된다 — 메인 스레드에서
    호출되는 정상 경로(파이프라인 S0-A)까지 큐로 밀려 모델 상태 표시가
    한 박자 늦고, 더 나쁘게는 `daily_close()` 대기 해제 순서가 흔들린다.
    """
    tree = ast.parse(_src())
    methods = _methods(tree)
    assert "_dashboard_call" in methods, "_dashboard_call() 헬퍼가 사라졌다 (F-L 회귀)"
    body = ast.dump(methods["_dashboard_call"])
    assert "currentThread" in body, "_dashboard_call 이 스레드 판정을 하지 않는다"
    assert "emit" in body, "_dashboard_call 이 메인 스레드로 위임하지 않는다"


def test_on_gbm_retrain_done_docstring이_스레드_사실을_적는다():
    """docstring 이 '메인 스레드에서 실행'으로 되돌아가면 다음 사람이 같은 함정에 빠진다."""
    tree = ast.parse(_src())
    doc = ast.get_docstring(_methods(tree)["_on_gbm_retrain_done"]) or ""
    assert "메인 스레드에서 실행" not in doc.splitlines()[0], (
        "_on_gbm_retrain_done docstring 이 다시 '메인 스레드에서 실행'이라고 단정한다 — "
        "396차 이후 그것은 참이 아니다"
    )
    assert "_dashboard_call" in doc, (
        "docstring 이 대시보드 접근 규약(_dashboard_call 경유)을 적고 있지 않다"
    )
