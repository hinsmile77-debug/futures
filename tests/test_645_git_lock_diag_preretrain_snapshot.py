# -*- coding: utf-8 -*-
"""[MW0601 645차 / 장후 자동조치] F-4 · G-1 · G-2 회귀 고정.

셋 다 **점검 도구**만 바꾼다. 매매 경로(주문·수량·게이트·청산)는 한 줄도 바뀌지 않는다.

- **F-4** `scripts/git_lock_diag.py` 가 락의 주인(ORPHAN/HELD/…)을 진단한다
  (판정 정본 `git_lock_guard.py` 는 fuoption 사본과 바이트 일치라 손대지 않는다). 2026-09-30 하루 3회 재현(STALE 2 · 자연소멸 1)을 한 원인으로 설명할 수
  없어서다. 🔴 **판정(stale·verdict)은 진단 유무와 무관해야 한다** — §1이 고정한다.
- **G-1** 수집기 §9 에 「PreRetrain 우회 확인」 한 줄. 종전엔 SYSTEM.log 수동 grep.
- **G-2** `scripts/git_snapshot.py` — 브랜치·HEAD·상태를 git 호출 1회로.
"""
from __future__ import annotations

import datetime
import importlib.util
import io
import os
import subprocess
import sys
import time

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCRIPTS = os.path.join(_ROOT, "scripts")
for _p in (_ROOT, _SCRIPTS):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import git_lock_guard as G  # noqa: E402
import git_snapshot as S  # noqa: E402
import git_lock_diag as D  # noqa: E402

_COLLECTOR = os.path.join(_ROOT, ".claude", "skills", "mireuk-daily-check",
                          "scripts", "collect_evidence.py")


@pytest.fixture(scope="module")
def collector():
    spec = importlib.util.spec_from_file_location("_collect_evidence_645", _COLLECTOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _lock_repo(tmpdir, age_sec=3600):
    root = str(tmpdir)
    os.makedirs(os.path.join(root, ".git"))
    lock = os.path.join(root, ".git", "index.lock")
    open(lock, "wb").close()
    t = time.time() - age_sec
    os.utime(lock, (t, t))
    return root, t


# ─────────────────────────────────────────────────────────────────────────────
# §1. F-4 — 주인 진단
# ─────────────────────────────────────────────────────────────────────────────
def test_f4_origin_unmeasured_is_not_orphan():
    code, _ = D.classify_lock_origin(1000.0, None)
    assert code == "UNMEASURED"


def test_f4_origin_orphan_when_zero_procs():
    code, _ = D.classify_lock_origin(1000.0, [])
    assert code == "ORPHAN"


def test_f4_origin_held_when_older_proc_alive():
    code, _ = D.classify_lock_origin(1000.0, [{"pid": 1, "started_epoch": 990.0, "cmd": "git diff"}])
    assert code == "HELD"


def test_f4_origin_unrelated_when_all_procs_newer():
    code, _ = D.classify_lock_origin(1000.0, [{"pid": 1, "started_epoch": 1500.0, "cmd": "git log"}])
    assert code == "UNRELATED"


def test_f4_origin_unknown_when_start_unmeasured():
    code, _ = D.classify_lock_origin(1000.0, [{"pid": 1, "started_epoch": None, "cmd": "git"}])
    assert code == "UNKNOWN"


def test_f4_diag_does_not_change_verdict(tmpdir, monkeypatch):
    """진단은 표기일 뿐 — stale·verdict 는 정본 inspect() 와 같아야 한다."""
    root, _ = _lock_repo(tmpdir)
    monkeypatch.setattr(D, "git_process_snapshot", lambda: [])
    a = G.inspect(root, git_procs=0)
    b = D.inspect_with_diag(root, git_procs=0)
    assert (a["stale"], a["verdict"]) == (b["stale"], b["verdict"])
    assert "diag" not in a
    assert b["diag"]["origin"] == "ORPHAN"


def test_f4_no_lock_no_diag(tmpdir):
    root = str(tmpdir)
    os.makedirs(os.path.join(root, ".git"))
    info = D.inspect_with_diag(root)
    assert info["present"] is False and "diag" not in info


def test_f4_recheck_reports_vanished_lock(tmpdir, monkeypatch, capsys):
    root, _ = _lock_repo(tmpdir, age_sec=5)  # 나이 미달 → 판정보류
    monkeypatch.setattr(G, "_git_process_count", lambda: 0)
    monkeypatch.setattr(D, "git_process_snapshot", lambda: [])

    def _sleep(_s):
        os.remove(os.path.join(root, ".git", "index.lock"))
    assert D.main(["--repo", root, "--recheck", "1"], sleep=_sleep) == 0
    assert "자연소멸" in capsys.readouterr().out


def test_f4_recheck_never_waits_on_stale_and_never_deletes(tmpdir, monkeypatch):
    root, _ = _lock_repo(tmpdir, age_sec=3600)
    monkeypatch.setattr(G, "_git_process_count", lambda: 0)
    monkeypatch.setattr(D, "git_process_snapshot", lambda: [])
    called = []
    assert D.main(["--repo", root, "--recheck", "1"], sleep=called.append) == 3
    assert called == []
    assert os.path.exists(os.path.join(root, ".git", "index.lock"))


def test_f4_diag_module_has_no_delete_path():
    src = io.open(os.path.join(_SCRIPTS, "git_lock_diag.py"), encoding="utf-8").read()
    for banned in ("os.remove", "os.unlink", "os.rename", "reclaim(", "shutil"):
        assert banned not in src, banned


def test_f4_collector_attaches_diag():
    src = io.open(_COLLECTOR, encoding="utf-8").read()
    assert "_gld.diagnose_lock(root)" in src
    assert "락 주인 진단" in src


# ─────────────────────────────────────────────────────────────────────────────
# §2. G-1 — PreRetrain 우회 확인
# ─────────────────────────────────────────────────────────────────────────────
_L_BYPASS = ("2026-09-30 08:55:09 [INFO] SYSTEM: [PreRetrain] EOD 마커 파일 직접 확인 "
             "(1일 전: 2026-09-29) → PreRetrain 스킵 (session_state 미기록 보완)")
_L_SKIP = ("2026-09-30 08:55:09 [INFO] SYSTEM: [PreRetrain] 08:55 사전 재학습 스킵 — "
           "1영업일 전(2026-09-29) EOD 재학습 성공 (동일 데이터 중복 불필요) | WarmupRetrain 예약 소진")
_L_FAIL = "2026-09-30 08:55:09 [WARNING] SYSTEM: [PreRetrain] 마커 파일 직접 확인 실패 (무해): x"
_L_RUN = "2026-09-30 08:55:09 [INFO] SYSTEM: [PreRetrain] 08:55 GBM 사전 재학습 시작 — EOD 미완료"


def _run_g1(collector, tmpdir, lines):
    root = str(tmpdir)
    os.makedirs(os.path.join(root, "logs"))
    if lines is not None:
        with io.open(os.path.join(root, "logs", "20260930_SYSTEM.log"), "w", encoding="utf-8") as f:
            f.write("\n".join(["2026-09-30 08:41:08 [INFO] SYSTEM: 무관한 줄"] + lines) + "\n")
    out = []
    collector.preretrain_bypass_lines(root, datetime.date(2026, 9, 30), out)
    return "\n".join(out)


def test_g1_bypass_success(collector, tmpdir):
    txt = _run_g1(collector, tmpdir, [_L_BYPASS, _L_SKIP])
    assert "✅" in txt and "우회 확인 **성공**" in txt


def test_g1_bypass_failure_is_red(collector, tmpdir):
    txt = _run_g1(collector, tmpdir, [_L_FAIL, _L_RUN])
    assert "🔴" in txt


def test_g1_no_log_is_unmeasured(collector, tmpdir):
    txt = _run_g1(collector, tmpdir, None)
    assert "미측정" in txt


def test_g1_run_path(collector, tmpdir):
    txt = _run_g1(collector, tmpdir, [_L_RUN])
    assert "**실행**" in txt


def test_g1_wired_into_state_snapshot(collector):
    src = io.open(_COLLECTOR, encoding="utf-8").read()
    i = src.index("def state_snapshot_section")
    body = src[i:src.index("\ndef ", i + 10)]
    assert "preretrain_bypass_lines(root, day, out)" in body


def test_g1_matches_live_log_wording():
    """main.py 문구가 바뀌면 이 분류가 조용히 죽는다 — 원문과 대조한다."""
    src = io.open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()
    for pat in ("EOD 마커 파일 직접 확인", "마커 파일 직접 확인 실패",
                "EOD 재학습 날짜 복원", "사전 재학습 스킵", "사전 재학습 시작"):
        assert pat in src, pat


# ─────────────────────────────────────────────────────────────────────────────
# §3. G-2 — git 1회 스냅샷
# ─────────────────────────────────────────────────────────────────────────────
_PORCELAIN = "\n".join([
    "# branch.oid 89836e3aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "# branch.head v9-dev",
    "# branch.upstream origin/v9-dev",
    "# branch.ab +2 -1",
    "1 .M N... 100644 100644 100644 abc abc dev_memory/NEXT_TODO.md",
    "2 R. N... 100644 100644 100644 abc abc R100 new name.md\told.md",
    "u UU N... 100644 100644 100644 100644 a b c conflict.py",
    "? dev_memory/_tmp.txt",
])


def test_g2_parse_porcelain():
    s = S.parse_porcelain_v2(_PORCELAIN)
    assert s["branch"] == "v9-dev" and s["head_oid"].startswith("89836e3")
    assert (s["ahead"], s["behind"]) == (2, 1)
    assert (s["changed"], s["untracked"], s["unmerged"]) == (2, 1, 1)
    assert "new name.md" in s["paths"] and "dev_memory/NEXT_TODO.md" in s["paths"]


def test_g2_no_upstream_is_none_not_zero():
    s = S.parse_porcelain_v2("# branch.oid abc\n# branch.head x\n")
    assert s["ahead"] is None and s["behind"] is None


def test_g2_one_git_call_on_real_repo(tmpdir):
    root = str(tmpdir)
    try:
        subprocess.check_call(["git", "init", "-q", root])
    except Exception:
        pytest.skip("git 없음")
    snap = S.snapshot(root)
    assert snap["git_calls"] == 1
    assert snap["measured"] is True
    assert snap["left_lock"] is False


def test_g2_uses_no_optional_locks():
    src = io.open(os.path.join(_SCRIPTS, "git_snapshot.py"), encoding="utf-8").read()
    assert '"--no-optional-locks"' in src and 'GIT_OPTIONAL_LOCKS' in src


# ─────────────────────────────────────────────────────────────────────────────
# §4. 라이브 반영 0 — 매매 모듈이 이 도구들을 import 하지 않는다
# ─────────────────────────────────────────────────────────────────────────────
def test_no_trading_module_imports_tools():
    for rel in ("main.py",):
        src = io.open(os.path.join(_ROOT, rel), encoding="utf-8").read()
        assert "git_snapshot" not in src
        assert "preretrain_bypass" not in src
