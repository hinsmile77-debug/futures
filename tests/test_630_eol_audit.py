# -*- coding: utf-8 -*-
"""[MW0601 630차] `scripts/eol_audit.py` — 진단은 안 바꾸고, 교정은 줄끝만 바꾼다.

MW0602 가 이 도구로 같은 교정을 한다(`docs/MW0602_적용가이드_git줄끝잠금_20260924.md`).
"""
import os
import subprocess
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))

import eol_audit as E  # noqa: E402


def _git(repo, *a):
    subprocess.check_call(["git", "-C", repo] + list(a), stdout=subprocess.DEVNULL)


@pytest.fixture
def repo(tmpdir):
    r = str(tmpdir)
    _git(r, "init", "-q")
    with open(os.path.join(_ROOT, ".gitattributes"), "rb") as f:
        ga = f.read()
    files = {".gitattributes": ga, "t.bat": b"@echo off\r\ngoto :A\r\n:A\r\n",
             "m.py": b"a\r\nb\r\n", "k.ps1": u'Write-Host "한글"\r\n'.encode("utf-8")}
    for n, b in files.items():
        with open(os.path.join(r, n), "wb") as f:
            f.write(b)
    _git(r, "add", "-A")
    _git(r, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "init")
    # 에이전트가 LF 로 다시 쓴 배치, 덧붙이기로 섞인 파이썬
    with open(os.path.join(r, "t.bat"), "wb") as f:
        f.write(b"@echo off\ngoto :A\n:A\n")
    with open(os.path.join(r, "m.py"), "ab") as f:
        f.write(b"c\n")
    return r


def test_scan_finds_all_three(repo):
    r = E.scan(repo)
    assert r["bat_lf"] == ["t.bat"]
    assert r["mixed"] == ["m.py"]
    assert r["ps1_nobom"] == ["k.ps1"]
    assert r["mount_noise"] == 0, "규칙이 있으면 마운트 관점 잡음은 0"


def test_diagnosis_changes_nothing(repo):
    before = open(os.path.join(repo, "t.bat"), "rb").read()
    E.main(["--repo", repo])
    assert open(os.path.join(repo, "t.bat"), "rb").read() == before


def test_fix_changes_line_endings_only(repo, monkeypatch, capsys):
    monkeypatch.setattr(E, "running_scripts", lambda r: [])
    assert E.main(["--repo", repo, "--fix"]) == 2, "BOM 은 --fix 로 안 고친다 — 남은 문제가 보고돼야 한다"
    assert open(os.path.join(repo, "t.bat"), "rb").read() == b"@echo off\r\ngoto :A\r\n:A\r\n"
    assert open(os.path.join(repo, "m.py"), "rb").read() == b"a\nb\nc\n"
    staged = subprocess.check_output(["git", "-C", repo, "diff", "--cached", "--name-only"])
    assert staged == b"", "교정은 내용 변경을 스테이징하지 않는다"
    capsys.readouterr()


def test_fix_refuses_when_script_running(repo, monkeypatch, capsys):
    monkeypatch.setattr(E, "running_scripts", lambda r: ["123 cmd /c t.bat"])
    assert E.main(["--repo", repo, "--fix"]) == 1
    assert b"\r\n" not in open(os.path.join(repo, "t.bat"), "rb").read()
    capsys.readouterr()


def test_fix_refuses_when_unmeasured(repo, monkeypatch, capsys):
    """실행 중 스크립트를 못 세면 0 으로 간주하지 않는다(계측 4원칙 ②)."""
    monkeypatch.setattr(E, "running_scripts", lambda r: None)
    assert E.main(["--repo", repo, "--fix"]) == 1
    capsys.readouterr()


def test_fix_bom(repo, capsys):
    E.main(["--repo", repo, "--fix-bom"])
    assert open(os.path.join(repo, "k.ps1"), "rb").read().startswith(b"\xef\xbb\xbf")
    capsys.readouterr()
