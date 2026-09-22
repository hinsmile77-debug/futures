# -*- coding: utf-8 -*-
"""[MW0601 617차] Qt 슬롯 무가드 전수 스캔 — "표시가 엔진을 죽이는" 경로 찾기.

왜 이 도구가 있나
-----------------
2026-09-22 09:41:56, 대시보드 캔들차트의 `ax.axhline` 한 줄이
`LinAlgError: Singular matrix` 를 던져 **미륵이가 통째로 죽었다**(다운 31초,
분봉 2개 결손). 실손해가 0이었던 것은 그날 우연히 FLAT 이었기 때문이다.

치명화의 기전은 차트가 아니라 **슬롯**이다:

    PyQt5(5.15.10)는 C++ 에서 호출된 파이썬 코드(= 슬롯) 안의 미처리 예외를
    `qFatal()` 로 처리한다 → 프로세스 abort.
    `sys.excepthook` 을 깔아도 못 막는다(호출된 뒤 그대로 죽는다).

즉 **슬롯 안에서 잡는 것이 유일하게 확실한 방어**다. 이 스크립트는 그 방어가
없는 슬롯을 전수로 찾는다. 457차 `test_457_fallback_visibility.py`(폴백 자동
검출)와 같은 취지 — 손 목록이 아니라 기계가 찾는다.

무엇을 "가드됨" 으로 보나
-------------------------
함수 본문(독스트링 제외)이 **통째로 하나의 try 로 감싸여** 있고, 그 except 가
`Exception`(또는 bare)을 잡는 경우만 가드로 센다. 본문 일부만 감싼 것은
`부분가드` 로 따로 센다 — 감싸지 않은 줄에서 죽으면 결과는 같기 때문이다.

⚠ **한계 — 읽을 때 주의할 것**
  · `lambda` 로 연결된 슬롯은 본문을 따라가지 않는다(`람다` 로 분류).
  · 다른 객체의 메서드(`self._panel.refresh`)는 정의를 찾지 못하면 `미해결`.
  · 가드가 있다고 안전한 것은 아니다 — `except: pass` 는 죽지는 않지만
    실패를 **숨긴다**(계측 4원칙 ④). 이 도구는 생존만 본다.

실행:
    python scripts/audit_qtimer_slot_guards.py                # 타이머 슬롯
    python scripts/audit_qtimer_slot_guards.py --all-signals  # 모든 시그널
    python scripts/audit_qtimer_slot_guards.py --fail-on-gap  # 무가드면 rc=2
"""
from __future__ import print_function

import argparse
import ast
import io
import os
import sys

try:                                    # cp949 콘솔에서 한글·기호 깨짐 방지
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: 스캔 대상 — GUI 스레드에서 도는 코드
TARGETS = ["dashboard", "main.py"]

GUARDED, PARTIAL, UNGUARDED, LAMBDA, UNRESOLVED = (
    "가드됨", "부분가드", "무가드", "람다", "미해결")


def _iter_py(paths):
    for p in paths:
        full = os.path.join(ROOT, p)
        if os.path.isfile(full):
            yield full
        for base, _dirs, files in os.walk(full):
            if "__pycache__" in base:
                continue
            for f in files:
                if f.endswith(".py"):
                    yield os.path.join(base, f)


def _strip_docstring(body):
    if (body and isinstance(body[0], ast.Expr)
            and isinstance(getattr(body[0], "value", None), ast.Str)):
        return body[1:]
    return body


def _catches_everything(handler):
    """`except Exception:` / `except:` / `except (A, Exception):` 인가."""
    t = handler.type
    if t is None:                                   # bare except
        return True
    names = []
    if isinstance(t, ast.Tuple):
        names = [getattr(e, "id", getattr(e, "attr", "")) for e in t.elts]
    else:
        names = [getattr(t, "id", getattr(t, "attr", ""))]
    return any(n in ("Exception", "BaseException") for n in names)


def _guard_state(func):
    """함수 하나의 가드 상태."""
    body = _strip_docstring(func.body)
    if not body:
        return GUARDED                              # 빈 몸통 — 죽을 일이 없다
    if len(body) == 1 and isinstance(body[0], ast.Try):
        if any(_catches_everything(h) for h in body[0].handlers):
            return GUARDED
        return PARTIAL
    for node in ast.walk(func):
        if isinstance(node, ast.Try):
            return PARTIAL
    return UNGUARDED


def _signal_of(call):
    """`x.timeout.connect(f)` → 'timeout'. connect 호출이 아니면 None."""
    fn = call.func
    if not isinstance(fn, ast.Attribute) or fn.attr != "connect":
        return None
    owner = fn.value
    if isinstance(owner, ast.Attribute):
        return owner.attr
    if isinstance(owner, ast.Name):
        return owner.id
    return None


def scan_file(path, all_signals=False):
    try:
        src = io.open(path, encoding="utf-8").read()
        tree = ast.parse(src)
    except Exception as e:                          # noqa: BLE001
        return [], "%s: %s" % (type(e).__name__, e)

    # 클래스별 메서드 표
    methods = {}                                    # (classname, method) -> FunctionDef
    class_of = {}                                   # FunctionDef -> classname
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef,)):
                    methods[(node.name, sub.name)] = sub
                    class_of[sub] = node.name
    # 해당 호출이 어느 클래스 안에 있는지
    owner_class = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for sub in ast.walk(node):
                owner_class[id(sub)] = node.name

    rows = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        sig = _signal_of(node)
        if sig is None:
            continue
        if not all_signals and sig != "timeout":
            continue
        if not node.args:
            continue
        arg = node.args[0]
        cls = owner_class.get(id(node), "")

        if isinstance(arg, ast.Lambda):
            state, target = LAMBDA, "<lambda>"
        elif (isinstance(arg, ast.Attribute)
                and isinstance(arg.value, ast.Name) and arg.value.id == "self"):
            target = "self.%s" % arg.attr
            fn = methods.get((cls, arg.attr))
            state = _guard_state(fn) if fn is not None else UNRESOLVED
        elif isinstance(arg, ast.Name):
            target = arg.id
            fn = methods.get((cls, arg.id))
            state = _guard_state(fn) if fn is not None else UNRESOLVED
        else:
            target = ast.dump(arg)[:40]
            state = UNRESOLVED
        rows.append({
            "file": os.path.relpath(path, ROOT).replace("\\", "/"),
            "line": node.lineno, "signal": sig, "cls": cls,
            "target": target, "state": state,
        })
    return rows, None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--all-signals", action="store_true",
                    help="timeout 외 모든 시그널 connect 포함")
    ap.add_argument("--fail-on-gap", action="store_true",
                    help="무가드가 하나라도 있으면 rc=2")
    ap.add_argument("--show", default="무가드",
                    help="상세 출력할 상태 (쉼표 구분, 'all' 가능)")
    args = ap.parse_args(argv)

    rows, errs = [], []
    for p in sorted(set(_iter_py(TARGETS))):
        r, e = scan_file(p, args.all_signals)
        rows.extend(r)
        if e:
            errs.append("%s — %s" % (p, e))

    counts = {}
    for r in rows:
        counts[r["state"]] = counts.get(r["state"], 0) + 1

    scope = "모든 시그널" if args.all_signals else "QTimer.timeout"
    print("=" * 70)
    print("Qt 슬롯 가드 감사 — 대상: %s | 연결 %d건" % (scope, len(rows)))
    print("=" * 70)
    for k in (UNGUARDED, PARTIAL, GUARDED, LAMBDA, UNRESOLVED):
        print("  %-6s %4d" % (k, counts.get(k, 0)))

    show = set(x.strip() for x in args.show.split(",")) if args.show else set()
    if "all" in show:
        show = {UNGUARDED, PARTIAL, GUARDED, LAMBDA, UNRESOLVED}
    detail = [r for r in rows if r["state"] in show]
    if detail:
        print("\n[상세] %s" % ", ".join(sorted(show)))
        for r in sorted(detail, key=lambda x: (x["file"], x["line"])):
            print("  %-6s %s:%d  %s.%s"
                  % (r["state"], r["file"], r["line"], r["cls"], r["target"]))

    if errs:
        print("\n[파싱 실패]")
        for e in errs:
            print("  " + e)

    print("\n⚠ 무가드 슬롯에서 예외가 나면 PyQt5 가 qFatal() 로 프로세스를 죽인다.")
    print("  (2026-09-22 09:41:56 실사고 — 617차)")

    if args.fail_on_gap and counts.get(UNGUARDED, 0):
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
