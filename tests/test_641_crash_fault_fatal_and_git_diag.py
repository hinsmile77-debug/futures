# -*- coding: utf-8 -*-
"""[MW0601 641차 / 637-2 · 638-1] 점검 수집기의 사각지대 두 개를 막는다.

637-2 — `logs/crash_fault.log` 는 파일명에 날짜가 없어 수집기 §1 당일 인벤토리에
  안 잡힌다. 종전 파서(`crash_fault_events`)는 `[START]`/`[CLEAN EXIT]` 만 봐서,
  프로세스가 **살아남은** `Windows fatal exception` 은 어느 축에도 걸리지 않았다.
  실측: 2026-09-28 부팅 구간 access violation 4건이 그날 장전 리포트에 0회 등장.

638-1 — 2026-09-29 12:27 장중 수집에서 `git diff` 가 실패하고 인덱스락이 남았는데,
  다이제스트에는 「git diff 실패」만 적혀 어느 명령이 왜 죽었는지 몰랐다.
  → 실패 명령·rc·stderr 를 남기고, `GIT_OPTIONAL_LOCKS=0` 을 자식에 상속시킨다.

거는 것:
  · fatal 이 그날 PID 에 귀속되고, 다른 날 PID 로 새지 않는가
  · 시각은 직전 표식(`[START]`/`[TS]`) — 하한으로만 쓰는가
  · 기존 키(start·clean_exit·watchdog_exit)와 판정이 그대로인가 (회귀)
  · 수집기가 fatal 을 렌더링하고 §11 에 올리는가
  · run_git 이 환경변수를 넘기고, 실패 시 git_change_profile 이 사유를 남기는가
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.wer_crash import crash_fault_events  # noqa: E402

_COLLECTOR = os.path.join(ROOT, ".claude", "skills", "mireuk-daily-check",
                          "scripts", "collect_evidence.py")

# 2026-09-28·09-29 실측 형태(줄여서).
_CRASH_FAULT = (
    "[START] 2026-09-28T08:40:48  PID=19608  Python 3.7.13 32bit  RSS=163MB\n"
    "Windows fatal exception: access violation\n"
    "Thread 0x000051ac (most recent call first):\n"
    "[TS] 2026-09-28T11:33:47 beat_age=1s watching=True strikes=0\n"
    "Windows fatal exception: access violation\n"
    "[CLEAN EXIT] 2026-09-28T15:47:14  PID=19608\n"
    "[START] 2026-09-29T08:40:44  PID=29344  Python 3.7.13 32bit  RSS=163MB\n"
    "Windows fatal exception: access violation\n"
    "  File \"...\\dashboard\\main_dashboard.py\", line 7249 in _build\n"
    "Windows fatal exception: access violation\n"
    "Windows fatal exception: access violation\n"
    "[TS] 2026-09-29T08:41:39 beat_age=0s watching=False strikes=0\n"
    "[CLEAN EXIT] 2026-09-29T15:47:15  PID=29344\n"
)


@pytest.fixture
def fake_root(tmp_path):
    (tmp_path / "logs").mkdir()
    (tmp_path / "logs" / "crash_fault.log").write_text(_CRASH_FAULT, encoding="utf-8")
    return str(tmp_path)


def _load_collector():
    spec = importlib.util.spec_from_file_location("collect_evidence_641", _COLLECTOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ── 637-2 파서 ────────────────────────────────────────────────────────────

def test_fatal_counted_per_day_pid(fake_root):
    r29 = crash_fault_events(fake_root, "2026-09-29")
    assert r29["fatal_total"] == 3
    fat = r29["by_pid"][29344]["fatal"]
    assert [f["kind"] for f in fat] == ["access violation"] * 3
    # 머리줄에 시각이 없다 — 직전 표식이 [START] 08:40:44 이다.
    assert [f["after"] for f in fat] == ["08:40:44"] * 3
    assert 19608 not in r29["by_pid"], "다른 날 PID 가 새면 안 된다"


def test_fatal_after_uses_latest_ts_mark(fake_root):
    r28 = crash_fault_events(fake_root, "2026-09-28")
    assert r28["fatal_total"] == 2
    assert [f["after"] for f in r28["by_pid"][19608]["fatal"]] == ["08:40:48", "11:33:47"]


def test_existing_keys_unchanged(fake_root):
    r = crash_fault_events(fake_root, "2026-09-29")
    rec = r["by_pid"][29344]
    assert rec["start"] == "08:40:44"
    assert rec["clean_exit"] == "15:47:15"
    assert rec["watchdog_exit"] is None
    assert r["covered"] is True and r["measured"] is True


def test_no_day_rows_is_not_zero(fake_root):
    """그날 구간이 없으면 fatal_total=0 이지만 covered=False — 「0건」으로 읽으면 안 된다."""
    r = crash_fault_events(fake_root, "2026-01-01")
    assert r["covered"] is False
    assert r["fatal_total"] == 0


def test_missing_file_is_unmeasured(tmp_path):
    r = crash_fault_events(str(tmp_path), "2026-09-29")
    assert r["measured"] is False
    assert r["fatal_total"] is None, "미측정을 0 으로 위장하면 안 된다(계측 4원칙 ②)"


# ── 637-2 수집기 렌더링 ────────────────────────────────────────────────────

def test_collector_renders_fatal_lines(fake_root):
    ce = _load_collector()
    lines = ce.fatal_exception_lines(crash_fault_events(fake_root, "2026-09-28"))
    txt = "\n".join(lines)
    assert "PID 19608" in txt and "**2건**" in txt
    assert "access violation 2" in txt
    assert "정규장(09:00) 이후 **1건**" in txt   # 11:33:47 이후 1건
    assert "하한" in txt


def test_collector_render_empty_when_unmeasured(tmp_path):
    ce = _load_collector()
    assert ce.fatal_exception_lines(crash_fault_events(str(tmp_path), "2026-09-29")) == []
    assert ce.fatal_exception_lines(None) == []


def test_collector_wires_fatal_into_section_and_flags():
    src = open(_COLLECTOR, encoding="utf-8").read()
    assert "_fau = wer_crash_section(root, cfg, day, L)" in src
    assert "fatal_exception_lines(fau)" in src
    assert 'if _fau and _fau.get("measured") and _fau.get("fatal_total"):' in src


# ── 638-1 git 진단 ────────────────────────────────────────────────────────

def test_run_git_passes_optional_locks_env(monkeypatch):
    ce = _load_collector()
    seen = {}

    class _P(object):
        returncode = 0

        def __init__(self, args, **kw):
            seen["args"] = args
            seen["env"] = kw.get("env")

        def communicate(self, timeout=None):
            return b"ok", b""

        def poll(self):
            return 0

    monkeypatch.setattr(ce.subprocess, "Popen", _P)
    assert ce.run_git(".", ["status"]) == "ok"
    assert seen["args"][:2] == ["git", "--no-optional-locks"]
    assert seen["env"]["GIT_OPTIONAL_LOCKS"] == "0"


def test_git_change_profile_records_fail_reason(monkeypatch):
    ce = _load_collector()

    def fake_run_git(root, args, timeout=25):
        if args[0] == "status":
            return " M a.py"
        return "(git 실패 rc=128) fatal: Unable to create index.lock"

    monkeypatch.setattr(ce, "run_git", fake_run_git)
    out = ce.git_change_profile(".")
    assert out["measured"] is False
    assert out["fail_reason"].startswith("git diff --numstat → (git 실패 rc=128)")
    assert "index.lock" in out["fail_reason"]


def test_git_change_profile_status_fail_reason(monkeypatch):
    ce = _load_collector()
    monkeypatch.setattr(ce, "run_git",
                        lambda root, args, timeout=25: "(git 타임아웃 25s — 자식 종료함) git status")
    out = ce.git_change_profile(".")
    assert out["measured"] is False
    assert out["fail_reason"].startswith("git status --porcelain → (git 타임아웃")


def test_git_change_profile_success_has_no_reason(monkeypatch):
    ce = _load_collector()

    def fake_run_git(root, args, timeout=25):
        if args[0] == "status":
            return " M a.py"
        if args[0] == "config":
            return "true"
        return "1\t1\ta.py"

    monkeypatch.setattr(ce, "run_git", fake_run_git)
    out = ce.git_change_profile(".")
    assert out["measured"] is True and out["fail_reason"] is None
