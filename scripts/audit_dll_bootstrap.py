# -*- coding: utf-8 -*-
"""[MW0601 537차] dll_bootstrap 적용 커버리지 감사 — BLAS 즉사 사각지대 찾기.

무엇을 묻는가
-------------
`utils/dll_bootstrap.py:ensure_conda_dll_path()`(448차)는 conda 활성화 없이 호출된
python.exe 에서 MKL delay-load 실패(`0xC06D007F`, **stderr 무출력 즉사**)를 막는다.
그 호출은 **진입점마다 수동으로** 들어가야 하므로 빠뜨리면 조용히 사각지대가 된다 —
실제로 `retrain_intraday.py` 가 448차 이후 줄곧 빠져 있었다.

강제 대상을 어떻게 고르나 — **손으로 관리하는 목록을 쓰지 않는다**
------------------------------------------------------------------
목록을 손으로 들면 갱신을 또 잊는다(같은 실패의 반복). 저장소에서 **증거**를 찾는다.

  (a) `.bat` 의 python 실행 줄이 그 스크립트를 부른다
  (b) 저장소 코드가 **타 env 인터프리터**로 그 스크립트를 spawn 한다
      🔴 `sys.executable` spawn 은 제외한다 — 같은 env 라 이 사고가 성립하지 않는다.
         위험한 것은 `PYTHON_64_EXEC` 처럼 **다른 env** 의 python.exe 를 부를 때뿐이다.
  (c) 파일 자신이 `py310_64\\python.exe ...` 같은 **맨손 실행**을 안내한다

수치 라이브러리 사용은 **전이(transitive)로 본다**
--------------------------------------------------
🔴 `retrain_intraday.py` 는 numpy 를 **직접 import 하지 않는다**(`learning.batch_retrainer`
경유). 직접 import 만 보면 이 파일이 감사에서 통째로 빠진다 — 초판이 실제로 그랬다.
그래서 저장소 내 모듈 그래프를 따라 전이 폐포를 계산한다.

판정
----
    NEEDS_FIX  강제 대상인데 부트스트랩 호출이 없다              → rc=1 (--fail-on-gap)
    LATE       호출이 numpy import **뒤**다 (늦으면 소용없다)     → rc=1
    OK         호출이 numpy import 앞에 있다 (또는 직접 import 없음)
    INFO       수치 라이브러리를 쓰지만 강제 대상은 아니다

⚠ 이 스크립트 자체는 numpy 를 쓰지 않는다(AST 정적 분석) — 어떤 환경에서도 돈다.

실행:
    python scripts/audit_dll_bootstrap.py
    python scripts/audit_dll_bootstrap.py --show-info
    python scripts/audit_dll_bootstrap.py --fail-on-gap    # CI/테스트용
"""
from __future__ import print_function

import argparse
import ast
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:                                   # py37 등 reconfigure 미지원
    pass

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NUMERIC = ("numpy", "scipy", "sklearn", "pandas")
BOOTSTRAP = "ensure_conda_dll_path"
SKIP_DIRS = (".git", "__pycache__", ".venv", "node_modules", "backup", ".idea")

_FOREIGN_PY = re.compile(r"PYTHON_\d+_EXEC|python\.exe", re.I)
_SPAWN = re.compile(r"Popen|subprocess\.run|check_call|check_output")
_BARE_RUN = re.compile(r"py3\d+_\d+[\\/]python\.exe", re.I)
_PYFILE = re.compile(r"([\w\-]+\.py)")

# 🔴 main.py 는 런처(start_mireuk.bat:188)가 conda activate py37_32 후 띄우고,
#    py37_32 에는 이 사고 이력이 없다. 강제하지 않고 권고로만 표기한다.
ADVISORY_ONLY = ("main.py",)
# 부트스트랩 모듈 자신 — selftest 가 numpy 를 쓰는 것은 설계상 정상.
EXCLUDE = ("utils/dll_bootstrap.py",)


def iter_py(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn.endswith(".py"):
                yield os.path.join(dirpath, fn)


def read(path):
    for enc in ("utf-8", "cp949", "latin-1"):
        try:
            with open(path, "r", encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, LookupError):
            continue
    return ""


def _parse(path):
    src = read(path)
    if not src:
        return None, ""
    try:
        return ast.parse(src, filename=path), src
    except (SyntaxError, ValueError):
        return None, src


# ── 증거 수집 ────────────────────────────────────────────────────────────────
def collect_spawn_evidence(root):
    """타 env 인터프리터로 spawn 되는 스크립트 basename 집합."""
    named = set()

    # (a) .bat 의 python 실행 줄
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if not fn.lower().endswith(".bat"):
                continue
            for line in read(os.path.join(dirpath, fn)).splitlines():
                if "python" not in line.lower():
                    continue
                for m in _PYFILE.finditer(line):
                    named.add(m.group(1).lower())

    # (b) 타 env 인터프리터 spawn — **함수 단위**로 좁힌다.
    #     한 파일에 sys.executable spawn 과 타 env spawn 이 섞여 있을 수 있으므로
    #     (main.py 가 실제로 그렇다) 파일 전체에서 .py 이름을 긁으면 오탐이 난다.
    for p in iter_py(root):
        tree, src = _parse(p)
        if tree is None:
            continue
        lines = src.splitlines()
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            lo = node.lineno - 1
            hi = getattr(node, "end_lineno", None) or (lo + 200)
            seg = "\n".join(lines[lo:hi])
            if not _SPAWN.search(seg) or not _FOREIGN_PY.search(seg):
                continue
            for m in _PYFILE.finditer(seg):
                named.add(m.group(1).lower())
    return named


def module_numeric_map(root):
    """저장소 모듈별 (직접 numeric import 여부, 프로젝트 내부 import 목록)."""
    direct, edges, path_of = {}, {}, {}
    for p in iter_py(root):
        tree, _ = _parse(p)
        if tree is None:
            continue
        rel = os.path.relpath(p, root).replace("\\", "/")
        mod = rel[:-3].replace("/", ".")
        if mod.endswith(".__init__"):
            mod = mod[:-9]
        path_of[mod] = rel
        d, es = False, set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = ([a.name for a in node.names] if isinstance(node, ast.Import)
                         else ([node.module] if node.module else []))
                for nm in names:
                    if not nm:
                        continue
                    top = nm.split(".")[0]
                    if top in NUMERIC:
                        d = True
                    else:
                        es.add(nm)
        direct[mod], edges[mod] = d, es
    return direct, edges, path_of


def transitively_numeric(mod, direct, edges, cache=None, seen=None):
    """모듈이 (전이적으로) 수치 라이브러리를 끌어오는가."""
    cache = {} if cache is None else cache
    if mod in cache:
        return cache[mod]
    seen = set() if seen is None else seen
    if mod in seen or mod not in direct:
        return False
    seen.add(mod)
    if direct[mod]:
        cache[mod] = True
        return True
    for e in edges.get(mod, ()):
        # `learning.batch_retrainer` / `learning` 양쪽 표기를 모두 시도
        for cand in (e, e.rsplit(".", 1)[0] if "." in e else None):
            if cand and cand in direct and transitively_numeric(cand, direct, edges,
                                                                cache, seen):
                cache[mod] = True
                return True
    cache[mod] = False
    return False


def analyze(path, root, spawned, direct, edges, cache):
    tree, src = _parse(path)
    if tree is None:
        return None
    rel = os.path.relpath(path, root).replace("\\", "/")
    if rel in EXCLUDE:
        return None

    is_entry = False
    numeric_line = None
    bootstrap_line = None
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            t = node.test
            if (isinstance(t, ast.Compare) and isinstance(t.left, ast.Name)
                    and t.left.id == "__name__"):
                is_entry = True
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = ([a.name for a in node.names] if isinstance(node, ast.Import)
                     else ([node.module] if node.module else []))
            for nm in names:
                if nm and nm.split(".")[0] in NUMERIC:
                    if numeric_line is None or node.lineno < numeric_line:
                        numeric_line = node.lineno
        if isinstance(node, ast.Call):
            fn = node.func
            nm = getattr(fn, "id", None) or getattr(fn, "attr", None)
            if nm == BOOTSTRAP:
                if bootstrap_line is None or node.lineno < bootstrap_line:
                    bootstrap_line = node.lineno
    if not is_entry:
        return None

    mod = rel[:-3].replace("/", ".")
    uses_numeric = (numeric_line is not None
                    or transitively_numeric(mod, direct, edges, cache))
    if not uses_numeric:
        return None

    base = os.path.basename(path).lower()
    reasons = []
    if base in spawned:
        reasons.append("타env spawn/bat")
    if _BARE_RUN.search(src):
        reasons.append("맨손실행 안내")
    if numeric_line is None:
        reasons.append("전이 numeric")

    if bootstrap_line is None:
        v = "NEEDS_FIX"
    elif numeric_line is not None and bootstrap_line > numeric_line:
        v = "LATE"
    else:
        v = "OK"
    enforced = any(r in ("타env spawn/bat", "맨손실행 안내") for r in reasons)
    if not enforced and v != "OK":
        v = "INFO"
    return {"verdict": v, "numeric": numeric_line, "bootstrap": bootstrap_line,
            "reasons": reasons, "path": rel}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fail-on-gap", action="store_true")
    ap.add_argument("--show-info", action="store_true")
    ap.add_argument("--root", default=_ROOT)
    a = ap.parse_args()

    spawned = collect_spawn_evidence(a.root)
    direct, edges, _ = module_numeric_map(a.root)
    cache = {}

    rows = []
    for p in iter_py(a.root):
        r = analyze(p, a.root, spawned, direct, edges, cache)
        if r:
            rows.append(r)

    order = {"NEEDS_FIX": 0, "LATE": 1, "OK": 2, "INFO": 3}
    rows.sort(key=lambda x: (order[x["verdict"]], x["path"]))
    counts = {}
    for r in rows:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1

    print("=" * 82)
    print(" dll_bootstrap 커버리지 감사")
    print("=" * 82)
    print("  강제 근거: .bat python 줄 / 타env 인터프리터 spawn / 맨손실행 안내")
    print("  (sys.executable spawn 은 같은 env 라 제외 · numeric 은 전이로 판정)")
    for k in ("NEEDS_FIX", "LATE", "OK", "INFO"):
        print("  %-10s %d" % (k, counts.get(k, 0)))
    print()

    gap = 0
    for r in rows:
        v = r["verdict"]
        if v == "INFO" and not a.show_info:
            continue
        advisory = os.path.basename(r["path"]) in ADVISORY_ONLY
        if v in ("NEEDS_FIX", "LATE") and not advisory:
            gap += 1
        tag = "(권고)" if advisory else ""
        why = ("  ← %s" % ", ".join(r["reasons"])) if r["reasons"] else ""
        print("  [%-9s]%s %-46s numeric@%-5s bootstrap@%-5s%s"
              % (v, tag, r["path"], r["numeric"], r["bootstrap"], why))

    print()
    print("판정: %s" % ("결손 %d건" % gap if gap else "강제 대상 결손 없음"))
    return 1 if (a.fail_on_gap and gap) else 0


if __name__ == "__main__":
    sys.exit(main())
