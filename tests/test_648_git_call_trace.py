# -*- coding: utf-8 -*-
"""[MW0601 648차 후속 / F-3] 점검 수집기 `run_git` 호출 기록.

2026-10-01 장중 수집은 `git diff --numstat` 25초 타임아웃 뒤 `.git/index.lock` 이
남았고, 장후 수집은 같은 타임아웃인데 남지 않았다. §2 는 「이 수집 실행이 락을
남겼다/안 남겼다」만 적어 **어느 호출 구간**에 생겼는지 알 수 없었다.

거는 것:
  · 호출마다 결과·경과·락 전후가 기록되는가 (ok / fail / timeout)
  · 반환 문자열은 종전과 같은가 (동작 무변경)
  · 락이 호출 구간에 생기면 그 호출이 「락 생성 구간」으로 표시되는가
  · 호출 0회는 「0 = 정상」이 아니라 미측정으로 적히는가 (계측 4원칙 ②)
  · 주목 호출이 많으면 잔여 개수를 적는가 (계측 4원칙 ③)
  · §2 에 배선돼 있는가
"""

from __future__ import annotations

import importlib.util
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_COLLECTOR = os.path.join(ROOT, ".claude", "skills", "mireuk-daily-check",
                          "scripts", "collect_evidence.py")


def _load():
    spec = importlib.util.spec_from_file_location("collect_evidence_648", _COLLECTOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _fake_popen(rc=0, timeout=False, make_lock=None):
    class _P(object):
        returncode = rc

        def __init__(self, args, **kw):
            self.calls = 0

        def communicate(self, timeout=None):
            self.calls += 1
            if make_lock:
                open(make_lock, "w").close()
            if timeout_flag[0] and self.calls == 1:
                raise subprocess.TimeoutExpired("git", timeout)
            return b"out", b"err"

        def kill(self):
            pass

        def poll(self):
            return 0

    timeout_flag = [timeout]
    return _P


def _root(tmp_path):
    (tmp_path / ".git").mkdir()
    return str(tmp_path)


def test_ok_call_recorded_and_return_unchanged(tmp_path, monkeypatch):
    ce = _load()
    root = _root(tmp_path)
    monkeypatch.setattr(ce.subprocess, "Popen", _fake_popen())
    assert ce.run_git(root, ["status", "--porcelain"]) == "out"
    r = ce._GIT_CALL_TRACE[-1]
    assert r["cmd"] == "git status --porcelain"
    assert r["outcome"] == "ok"
    assert r["lock_before"] is False and r["lock_after"] is False
    assert r["elapsed_s"] is not None


def test_fail_and_timeout_outcomes(tmp_path, monkeypatch):
    ce = _load()
    root = _root(tmp_path)
    monkeypatch.setattr(ce.subprocess, "Popen", _fake_popen(rc=1))
    assert ce.run_git(root, ["diff"]).startswith("(git 실패 rc=1)")
    monkeypatch.setattr(ce.subprocess, "Popen", _fake_popen(timeout=True))
    assert ce.run_git(root, ["diff", "--numstat"], timeout=25).startswith("(git 타임아웃 25s")
    assert [r["outcome"] for r in ce._GIT_CALL_TRACE] == ["fail", "timeout"]


def test_lock_born_during_call_is_flagged(tmp_path, monkeypatch):
    ce = _load()
    root = _root(tmp_path)
    lock = os.path.join(root, ".git", "index.lock")
    monkeypatch.setattr(ce.subprocess, "Popen", _fake_popen(timeout=True, make_lock=lock))
    ce.run_git(root, ["diff", "--numstat"])
    r = ce._GIT_CALL_TRACE[-1]
    assert r["lock_before"] is False and r["lock_after"] is True
    txt = "\n".join(ce.git_call_trace_lines())
    assert "락 생성 구간 1" in txt
    assert "이 호출 구간에 락이 생겼다" in txt
    assert "인과 미확정" in txt


def test_pre_existing_lock_is_not_born(tmp_path, monkeypatch):
    ce = _load()
    root = _root(tmp_path)
    open(os.path.join(root, ".git", "index.lock"), "w").close()
    monkeypatch.setattr(ce.subprocess, "Popen", _fake_popen())
    ce.run_git(root, ["status"])
    txt = "\n".join(ce.git_call_trace_lines())
    assert "락 생성 구간 0" in txt
    assert "이 호출 구간에" not in txt


def test_empty_trace_is_unmeasured():
    ce = _load()
    txt = "\n".join(ce.git_call_trace_lines(trace=[]))
    assert "미측정" in txt


def test_notable_truncation_states_remainder():
    ce = _load()
    tr = [{"cmd": "git diff %d" % i, "outcome": "timeout", "elapsed_s": 25.0,
           "lock_before": False, "lock_after": False} for i in range(11)]
    lines = ce.git_call_trace_lines(trace=tr, limit=8)
    assert "타임아웃 11" in lines[0]
    assert lines[-1].strip() == "- … 외 3건"


def test_unmeasured_lock_counted():
    ce = _load()
    tr = [{"cmd": "git status", "outcome": "ok", "elapsed_s": 0.1,
           "lock_before": None, "lock_after": None}]
    assert "락 미측정 1" in ce.git_call_trace_lines(trace=tr)[0]


def test_wired_into_section2():
    src = open(_COLLECTOR, encoding="utf-8").read()
    assert "L.extend(git_call_trace_lines())" in src
