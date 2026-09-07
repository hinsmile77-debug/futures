# -*- coding: utf-8 -*-
"""[MW0601 537차] BLAS 즉사 회귀 고정.

무엇을 막는가
-------------
conda 활성화 없이 실행되는 진입점이 `ensure_conda_dll_path()` 를 빠뜨리면, 그 프로세스는
BLAS 를 밟는 순간 **stderr 한 줄 없이 즉사**한다(`0xC06D007F` STATUS_DELAY_LOAD_FAILED).
예외가 아니라 프로세스 종료라 `try/except` 로 못 잡고, 로그도 안 남는다.

448차가 `utils/dll_bootstrap.py` 로 고쳤으나 **`retrain_intraday.py` 가 그 호출을
빠뜨린 채 6개월 가까이 방치**됐다(537차 발견). 지금 사고가 없었던 것은 장중 경량
재학습이 HistGBM/RobustScaler 만 써서 BLAS 를 안 밟았기 때문이다 — 상관·회귀·
`scipy.stats` 가 한 줄 들어오면 재학습이 죽고 모델 미교체 → CB③ HALT 로 간다.

근거: docs/정기점검/매일점검/MW0601-20260907-BLAS즉사-딥다이브.md
"""
from __future__ import print_function

import ast
import os
import subprocess
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.dll_bootstrap import child_env_for, ensure_conda_dll_path  # noqa: E402


# ── 1. 감사기가 결손을 보고하지 않는다 (전체 회귀 가드) ──────────────────────
def test_audit_reports_no_gap():
    """`scripts/audit_dll_bootstrap.py --fail-on-gap` 이 통과해야 한다.

    새 진입점이 타 env 인터프리터로 spawn 되거나 맨손 실행을 안내하면서
    부트스트랩을 빠뜨리면 여기서 깨진다.
    """
    p = subprocess.run(
        [sys.executable, os.path.join(_ROOT, "scripts", "audit_dll_bootstrap.py"),
         "--fail-on-gap"],
        cwd=_ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=300,
    )
    out = p.stdout.decode("utf-8", "replace")
    assert p.returncode == 0, "부트스트랩 결손 발생:\n%s" % out


# ── 2. 라이브 경로 개별 고정 ────────────────────────────────────────────────
# 감사기가 언젠가 판정 로직을 바꿔도 이 두 파일만은 반드시 지켜지도록 못 박는다.
_MUST_HAVE = ("retrain_intraday.py", "retrain_eod.py")


@pytest.mark.parametrize("rel", _MUST_HAVE)
def test_retrain_entrypoints_call_bootstrap(rel):
    path = os.path.join(_ROOT, rel)
    with open(path, "r", encoding="utf-8") as f:
        src = f.read()
    tree = ast.parse(src, filename=path)

    call_line = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            nm = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
            if nm == "ensure_conda_dll_path":
                call_line = node.lineno if call_line is None else min(call_line,
                                                                     node.lineno)
    assert call_line is not None, (
        "%s 가 ensure_conda_dll_path() 를 부르지 않는다 — "
        "이 파일은 conda 활성화 없이 실행되므로 BLAS 를 밟으면 즉사한다." % rel)

    # 수치 라이브러리를 **직접** import 한다면 그보다 앞서야 한다.
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = ([a.name for a in node.names] if isinstance(node, ast.Import)
                     else ([node.module] if node.module else []))
            for nm in names:
                if nm and nm.split(".")[0] in ("numpy", "scipy", "sklearn", "pandas"):
                    assert call_line < node.lineno, (
                        "%s: 부트스트랩(line %d)이 %s import(line %d)보다 뒤다 — "
                        "import 는 성공하고 첫 BLAS 호출에서 죽는다."
                        % (rel, call_line, nm, node.lineno))


# ── 3. main.py 가 자식에게 env 를 넘긴다 ────────────────────────────────────
def test_main_passes_child_env_to_retrain_subprocess():
    """`Popen([PYTHON_64_EXEC, ...])` 호출에 `env=` 가 붙어 있어야 한다.

    자식은 기본적으로 py37_32 환경을 상속하는데 두 env 의 MKL 은 파일명이 달라
    (`mkl_rt.1.dll` vs `mkl_rt.3.dll`) 상속된 PATH 로는 찾을 수 없다.
    """
    with open(os.path.join(_ROOT, "main.py"), "r", encoding="utf-8") as f:
        src = f.read()
    tree = ast.parse(src)
    lines = src.splitlines()

    found = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if getattr(node.func, "attr", None) != "Popen":
            continue
        seg = "\n".join(lines[node.lineno - 1:(getattr(node, "end_lineno", None)
                                               or node.lineno) + 1])
        if "PYTHON_64_EXEC" not in seg:
            continue
        found = True
        assert any(kw.arg == "env" for kw in node.keywords), (
            "main.py 의 py310_64 재학습 Popen 에 env= 가 없다 — "
            "자식이 py37_32 PATH 를 상속해 BLAS 즉사 위험.")
    assert found, "main.py 에서 PYTHON_64_EXEC Popen 호출을 찾지 못했다(리팩터링?)"


# ── 4. child_env_for 계약 ───────────────────────────────────────────────────
def test_child_env_for_is_a_full_copy_not_a_fragment():
    """`Popen(env=)` 는 환경을 **대체**한다 — 부분 딕셔너리를 넘기면 나머지가 사라진다."""
    base = {"FOO": "bar", "PATH": r"C:\somewhere"}
    env = child_env_for(sys.executable, base_env=base)
    assert env["FOO"] == "bar", "기존 환경변수가 보존돼야 한다"
    assert "PATH" in env
    assert env is not base, "원본을 제자리 수정하면 안 된다(호출부 부작용)"


@pytest.mark.skipif(os.name != "nt", reason="Windows 전용 경로 규칙")
def test_child_env_for_prepends_target_env_dirs():
    """대상 인터프리터의 env 디렉터리가 PATH **앞**에 붙어야 한다."""
    exe = sys.executable
    root = os.path.dirname(os.path.abspath(exe))
    base = {"PATH": r"C:\unrelated"}
    env = child_env_for(exe, base_env=base)
    parts = [p.rstrip("\\").lower() for p in env["PATH"].split(os.pathsep) if p]
    assert root.rstrip("\\").lower() in parts, "env 루트가 PATH 에 없다"
    libbin = os.path.join(root, "Library", "bin")
    if os.path.isdir(libbin):
        assert parts.index(libbin.rstrip("\\").lower()) < parts.index("c:\\unrelated"), (
            "Library\\bin 이 기존 PATH 보다 앞에 와야 한다 — 뒤면 부모 env 의 "
            "동명 DLL 이 먼저 걸린다")


def test_child_env_for_survives_bad_input():
    """빈 executable 등 이상 입력에서도 예외 없이 기반 환경을 돌려준다.

    main.py 는 실패 시 env=None 폴백을 갖지만, 애초에 던지지 않는 것이 낫다.
    """
    base = {"PATH": "x"}
    assert child_env_for("", base_env=base)["PATH"] == "x"
    assert child_env_for(None, base_env=base)["PATH"] == "x"


# ── 5. 부트스트랩 자체가 멱등이다 ───────────────────────────────────────────
def test_ensure_conda_dll_path_is_idempotent():
    ensure_conda_dll_path()
    assert ensure_conda_dll_path() == [], "두 번째 호출은 아무것도 추가하지 않아야 한다"
