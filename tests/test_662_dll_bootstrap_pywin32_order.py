# -*- coding: utf-8 -*-
"""[MW0601 662차] dll_bootstrap 이 pywin32 를 깨지 않는다.

무엇을 막는가
-------------
py37_32 에는 pywin32 가 두 벌 있다 — pip 판(`Lib\\site-packages\\pywin32_system32`,
실제 `win32api.pyd` 와 짝)과 conda 302 판(`Library\\bin`). `ensure_conda_dll_path()` 가
`Library\\bin` 을 pip 판보다 앞에 넣자 옛 `pywintypes37.dll` 이 먼저 걸려
`import win32api` 가 「지정된 프로시저를 찾을 수 없습니다」로 죽었다.

conda 활성화 상태에서는 재현되지 않는다(부트스트랩이 아무것도 안 한다). 맨손 실행 —
예약작업 `Mireuk_OptionFlowBackfill_1605` — 에서만 터졌고, 655차 리허설은 일요일이라
COM 을 열기 전에 휴장일로 끝나 이걸 못 잡았다. 2026-10-06 첫 평일 실행이 실패해
옵션 흐름 마감 구간(15:35–16:07)을 잃을 뻔했다(수동 복구).

실행: conda run -n py37_32 python -m pytest tests/test_662_dll_bootstrap_pywin32_order.py -v
"""
import os
import subprocess
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import utils.dll_bootstrap as B  # noqa: E402

_win = pytest.mark.skipif(os.name != "nt", reason="Windows 전용")


def _fake_env(tmp_path, monkeypatch, path):
    root = tmp_path / "py37_32"
    (root / "Library" / "bin").mkdir(parents=True)
    (root / "Lib" / "site-packages" / "pywin32_system32").mkdir(parents=True)
    monkeypatch.setattr(B.sys, "executable", str(root / "python.exe"))
    monkeypatch.setenv("PATH", path.format(root=str(root)))
    return root


def _parts():
    return [p.rstrip("\\").lower() for p in os.environ["PATH"].split(os.pathsep) if p]


@_win
def test_library_bin_goes_after_own_pywin32_system32(tmp_path, monkeypatch):
    root = _fake_env(tmp_path, monkeypatch,
                     r"{root}\lib\site-packages\pywin32_system32;C:\other;C:\Windows")
    added = B.ensure_conda_dll_path()
    p = _parts()
    lib = str(root / "Library" / "bin").lower()
    pyw = str(root / "Lib" / "site-packages" / "pywin32_system32").lower()
    assert added and p.index(pyw) < p.index(lib) < p.index(r"c:\other"), p


@_win
def test_prepends_when_no_pywin32_on_path(tmp_path, monkeypatch):
    """pywin32_system32 가 PATH 에 없으면 종전대로 맨 앞(448차 MKL 대책 유지)."""
    root = _fake_env(tmp_path, monkeypatch, r"C:\other;C:\Windows")
    B.ensure_conda_dll_path()
    assert _parts()[0] == str(root / "Library" / "bin").lower()


@_win
def test_other_envs_pywin32_does_not_count(tmp_path, monkeypatch):
    """다른 env 의 pywin32_system32 뒤로 밀리면 안 된다 — 같은 env 것만 기준."""
    root = _fake_env(tmp_path, monkeypatch,
                     r"C:\x\envs\other\Lib\site-packages\pywin32_system32;C:\Windows")
    B.ensure_conda_dll_path()
    assert _parts()[0] == str(root / "Library" / "bin").lower()


@_win
def test_idempotent(tmp_path, monkeypatch):
    _fake_env(tmp_path, monkeypatch, r"{root}\Lib\site-packages\pywin32_system32;C:\Windows")
    B.ensure_conda_dll_path()
    first = os.environ["PATH"]
    assert B.ensure_conda_dll_path() == [] and os.environ["PATH"] == first


@_win
def test_bare_interpreter_can_import_win32api_after_bootstrap():
    """예약작업과 같은 조건 — 맨손 python.exe + 최소 PATH 에서 부트스트랩 후 win32api.

    py37_32 가 아니거나 pywin32 가 없으면 건너뛴다(py310_64 등에서 돌릴 때).
    """
    if sys.version_info[:2] != (3, 7):
        pytest.skip("py37_32 전용 — 두 벌 pywin32 조합은 이 env 에만 있다")
    try:
        import win32api  # noqa: F401
    except ImportError:
        pytest.skip("pywin32 없음")
    sysroot = os.environ.get("SystemRoot", r"C:\Windows")
    env = {k: v for k, v in os.environ.items() if k.upper() not in ("PATH", "CONDA_PREFIX", "CONDA_DEFAULT_ENV")}
    env["PATH"] = os.pathsep.join([os.path.join(sysroot, "System32"), sysroot])
    code = ("import sys; sys.path.insert(0, %r)\n"
            "from utils.dll_bootstrap import ensure_conda_dll_path; ensure_conda_dll_path()\n"
            "import win32api, pythoncom, win32com.client; print('OK')" % _ROOT)
    p = subprocess.run([sys.executable, "-c", code], env=env, cwd=_ROOT,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
    out = (p.stdout + p.stderr).decode("utf-8", "replace") + p.stderr.decode("cp949", "replace")
    assert p.returncode == 0 and b"OK" in p.stdout, out
