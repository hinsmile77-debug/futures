# -*- coding: utf-8 -*-
"""[MW0601 653차 / 652 F-1] 점검 수집기 §2 「락 자가점검」 ↔ 「git 호출 기록」 일치.

2026-10-02 장전·장중·장후 세 번, 같은 §2 안에서 자가점검은 「이 수집 실행은 락을
만들지 않았다」, 바로 아래 호출 기록은 「`git diff --numstat` 구간에 락이 생겼다」로
갈렸다. 원인: `lk = git_index_lock(root)` 가 `git_change_profile()`(git diff) **앞**에
있어 그 뒤에 생긴 락을 못 봤다.

거는 것:
  · 호출 구간에 락이 생긴 기록이 있으면 자가점검이 「만들지 않았다」라고 쓰지 않는다
  · 생겼다가 사라진 경우도 「만들지 않았다」가 아니다
  · run_git 밖에서 생긴 락은 종전 문구(다른 git 명령 의심)를 유지한다
  · 시작 스냅샷·현재 상태 미측정은 미측정으로 적힌다 (계측 4원칙 ②)
  · build() 에서 git_change_profile 이 인덱스락 조회보다 먼저 돈다 (순서 고정)
"""

from __future__ import annotations

import importlib.util
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_COLLECTOR = os.path.join(ROOT, ".claude", "skills", "mireuk-daily-check",
                          "scripts", "collect_evidence.py")
_SKILL = os.path.join(ROOT, ".claude", "skills", "mireuk-daily-check", "SKILL.md")

_NOT_MADE = "이 수집 실행은 락을 만들지 않았다"


def _load():
    spec = importlib.util.spec_from_file_location("collect_evidence_653", _COLLECTOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _rec(cmd, outcome, before, after):
    return {"cmd": cmd, "outcome": outcome, "elapsed_s": 25.0,
            "lock_before": before, "lock_after": after}


def test_born_in_trace_and_still_present_is_flagged():
    """2026-10-02 실측 지문 — diff 타임아웃 구간에 생겨 지금도 남아 있다."""
    ce = _load()
    tr = [_rec("git status --porcelain", "ok", False, False),
          _rec("git diff --numstat", "timeout", False, True)]
    line = ce.lock_selfcheck_line(False, True, trace=tr)
    assert _NOT_MADE not in line
    assert "git diff --numstat" in line
    assert "인과 미확정" in line
    assert "🔴" in line


def test_born_in_trace_then_gone_is_not_reported_as_clean():
    ce = _load()
    tr = [_rec("git diff --numstat", "timeout", False, True)]
    line = ce.lock_selfcheck_line(False, False, trace=tr)
    assert _NOT_MADE not in line
    assert "지금은 없다" in line


def test_stale_lk_snapshot_cannot_contradict_trace():
    """조회 순서가 다시 어긋나 lock_now=False 가 들어와도 호출 기록과 상충하지 않는다."""
    ce = _load()
    tr = [_rec("git diff --numstat", "timeout", False, True)]
    trace_txt = "\n".join(ce.git_call_trace_lines(trace=tr))
    line = ce.lock_selfcheck_line(False, False, trace=tr)
    assert "이 호출 구간에 락이 생겼다" in trace_txt
    assert _NOT_MADE not in line


def test_lock_outside_run_git_keeps_other_command_hint():
    ce = _load()
    tr = [_rec("git status", "ok", False, False)]
    line = ce.lock_selfcheck_line(False, True, trace=tr)
    assert "다른 git 명령" in line
    assert "남겼다" in line


def test_clean_run_says_not_made():
    ce = _load()
    tr = [_rec("git status", "ok", False, False)]
    assert _NOT_MADE in ce.lock_selfcheck_line(False, False, trace=tr)


def test_pre_existing_lock_not_blamed():
    ce = _load()
    tr = [_rec("git status", "ok", True, True)]
    line = ce.lock_selfcheck_line(True, True, trace=tr)
    assert "시작 시점부터 있던" in line
    assert "회수했다" in ce.lock_selfcheck_line(True, False, trace=tr)


def test_unmeasured_states():
    ce = _load()
    assert "미측정" in ce.lock_selfcheck_line(None, True, trace=[])
    line = ce.lock_selfcheck_line(False, None, trace=[])
    assert "미측정" in line and _NOT_MADE not in line


def test_build_orders_change_profile_before_lock_lookup():
    src = open(_COLLECTOR, encoding="utf-8").read()
    i_chg = src.index("_chg = git_change_profile(root)")
    i_lk = src.index("lk = git_index_lock(root)")
    assert i_chg < i_lk
    assert src.count("_chg = git_change_profile(root)") == 1
    assert "A(lock_selfcheck_line(_LOCK_AT_START, lk.get(\"present\")))" in src


def test_skill_since_example_pins_kst():
    """652 G-1 — 병행 세션 확인 예시 명령에 시간대가 박혀 있다."""
    src = open(_SKILL, encoding="utf-8").read()
    assert '00:00:00 +0900"' in src
