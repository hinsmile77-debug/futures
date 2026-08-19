# -*- coding: utf-8 -*-
"""[MW0601 476차] 점검 산출물 보관정책 — 불변식 테스트.

이 테스트가 지키는 것은 「정리가 돈다」가 아니라 **「지우면 안 되는 것을 안 지운다」** 이다.
보관정책 이식 지침 §5의 5케이스 + 미륵이 전용 멀티PC 케이스를 고정한다.

실행:
    python -m pytest tests/test_476_evidence_retention.py -q
"""
from __future__ import annotations

import datetime
import os
import runpy
import shutil
import sys
import tempfile

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BODY = os.path.join(ROOT, ".claude", "skills", "mireuk-daily-check",
                    "scripts", "collect_evidence.py")


@pytest.fixture(scope="module")
def ce():
    """수집기 본체를 모듈로 적재한다(패키지가 아니라 파일이라 runpy를 쓴다)."""
    if not os.path.exists(BODY):
        pytest.skip("수집기 본체 없음: %s" % BODY)
    ns = runpy.run_path(BODY, run_name="_ce_under_test")
    return ns


@pytest.fixture
def sandbox():
    """실물 디렉터리에 절대 손대지 않는다 — 임시 폴더에 사본을 만든다(지침 §5)."""
    d = tempfile.mkdtemp(prefix="mireuk_476_")
    ev = os.path.join(d, "docs", "정기점검", "매일점검")
    os.makedirs(ev)
    names = [
        # 자동 생성 증거 — 자기 PC (삭제 후보)
        "evidence_MW0601-20260501_pre.md",
        "evidence_MW0601-20260501_intra.md",
        "evidence_MW0601-20260501_post.md",
        "evidence_MW0601-20260814_pre.md",
        "evidence_MW0601-20260814_pre_1622.md",      # 461차 F-6 비덮어쓰기 변형
        "evidence_MW0601-20260818_post.md",
        # 다른 PC — **절대 지우면 안 된다**
        "evidence_MW0602-20260501_post.md",
        "evidence_MW0602-20260814_post.md",
        # 보고서·검토보고·딥다이브 — 삭제 대상이 아니다
        "MW0601-20260501-점검리포트-post.md",
        "MW0601-20260814-점검리포트-post.md",
        "MW0601-20260812-이상점3건-딥다이브.md",
        "0810_Fix_고도화_통합구현계획_MW0601.md",
        "dailycheck_prompt.txt",
    ]
    for n in names:
        with open(os.path.join(ev, n), "w", encoding="utf-8") as f:
            f.write("x")
    yield d, ev, {"evidence_dir": os.path.join("docs", "정기점검", "매일점검")}
    shutil.rmtree(d, ignore_errors=True)


TODAY = datetime.date(2026, 8, 18)


def _names(paths):
    return sorted(os.path.basename(p) for p in paths)


# ── PC 식별자 오버라이드 ─────────────────────────────────────────────────────

def test_pc_override_beats_hostname(ce):
    """`--pc`가 호스트명을 이긴다 — 리눅스 샌드박스 UNKNOWN 방지."""
    set_pc, pc_id = ce["set_pc_override"], ce["pc_id"]
    try:
        set_pc("mw0601")
        pid, host = pc_id()
        assert pid == "MW0601"
        assert "override" in host
    finally:
        set_pc(None)


def test_pc_env_used_when_no_arg(ce, monkeypatch):
    set_pc, pc_id = ce["set_pc_override"], ce["pc_id"]
    set_pc(None)
    monkeypatch.setenv("MIREUK_PC_ID", "MW0602")
    pid, host = pc_id()
    assert pid == "MW0602" and "env" in host


# ── 지침 §5 5케이스 ──────────────────────────────────────────────────────────

def test_case1_keep_zero_deletes_nothing(ce, sandbox):
    """keep_days=0 은 「전부 지워라」가 아니라 킬스위치다."""
    root, ev, cfg = sandbox
    before = os.listdir(ev)
    for keep in (0, -1, None):
        doomed, why = ce["prune_evidence"](root, cfg, "MW0601", keep, TODAY)
        assert doomed == []
        assert "킬스위치" in why
    assert sorted(os.listdir(ev)) == sorted(before)


def test_case2_boundary_only(ce, sandbox):
    """keep_days=N 이면 경계 밖만 지우고 목록을 돌려준다."""
    root, ev, cfg = sandbox
    # 2026-08-18 기준 30일 컷 = 2026-07-19. 05-01 것만 밖이다.
    doomed, _ = ce["prune_evidence"](root, cfg, "MW0601", 30, TODAY, dry_run=True)
    assert _names(doomed) == [
        "evidence_MW0601-20260501_intra.md",
        "evidence_MW0601-20260501_post.md",
        "evidence_MW0601-20260501_pre.md",
    ]
    assert len(os.listdir(ev)) == 13         # dry-run은 아무것도 안 지운다


def test_case3_reports_never_targeted(ce, sandbox):
    """보고서·검토보고·딥다이브·txt 는 keep_days=1 에서도 개수 불변."""
    root, ev, cfg = sandbox
    ce["prune_evidence"](root, cfg, "MW0601", 1, TODAY)
    left = set(os.listdir(ev))
    for n in ("MW0601-20260501-점검리포트-post.md",
              "MW0601-20260814-점검리포트-post.md",
              "MW0601-20260812-이상점3건-딥다이브.md",
              "0810_Fix_고도화_통합구현계획_MW0601.md",
              "dailycheck_prompt.txt"):
        assert n in left, "삭제되면 안 되는 파일이 사라졌다: %s" % n


def test_case4_phase_suffix_recognized(ce, sandbox):
    """국면 접미사·461차 F-6 시각 변형(`_pre_1622`)을 정확히 인식한다."""
    root, ev, cfg = sandbox
    doomed, _ = ce["prune_evidence"](root, cfg, "MW0601", 1, TODAY, dry_run=True)
    names = _names(doomed)
    assert "evidence_MW0601-20260814_pre_1622.md" in names
    assert "evidence_MW0601-20260814_pre.md" in names
    # 오늘 것(20260818)은 keep_days=1 경계 안이라 살아 있어야 한다
    assert "evidence_MW0601-20260818_post.md" not in names


def test_case5_backfill_deletes_less(ce, sandbox):
    """과거 날짜로 돌리면 **덜** 지우는 방향이어야 한다(밀린 실행 안전성)."""
    root, ev, cfg = sandbox
    now_cnt = len(ce["prune_evidence"](root, cfg, "MW0601", 30, TODAY,
                                       dry_run=True)[0])
    past_cnt = len(ce["prune_evidence"](root, cfg, "MW0601", 30,
                                        datetime.date(2026, 6, 1),
                                        dry_run=True)[0])
    assert past_cnt <= now_cnt


# ── 미륵이 전용 — 멀티PC 교차삭제 방지 (마흐디에 없던 함정) ──────────────────

def test_other_pc_files_are_structurally_unmatchable(ce, sandbox):
    """정규식에 PC명이 박혀 있어 다른 PC 파일은 **매칭 자체가 안 된다.**"""
    root, ev, cfg = sandbox
    doomed, _ = ce["prune_evidence"](root, cfg, "MW0601", 1, TODAY, dry_run=True)
    assert not any("MW0602" in os.path.basename(p) for p in doomed)
    ce["prune_evidence"](root, cfg, "MW0601", 1, TODAY)
    left = os.listdir(ev)
    assert "evidence_MW0602-20260501_post.md" in left
    assert "evidence_MW0602-20260814_post.md" in left


def test_unknown_pc_aborts(ce, sandbox):
    """PC를 모르면 무엇이 내 것인지도 모른다 — 지우지 않고 멈춘다."""
    root, ev, cfg = sandbox
    doomed, why = ce["prune_evidence"](root, cfg, "UNKNOWN", 1, TODAY)
    assert doomed == [] and "UNKNOWN" in why
    assert len(os.listdir(ev)) == 13


def test_filename_date_not_mtime(ce, sandbox):
    """mtime을 최신으로 바꿔도 **파일명 날짜**로 판정한다(복사·백업복원 대비)."""
    root, ev, cfg = sandbox
    old = os.path.join(ev, "evidence_MW0601-20260501_post.md")
    os.utime(old, None)                       # mtime = 지금
    doomed, _ = ce["prune_evidence"](root, cfg, "MW0601", 30, TODAY, dry_run=True)
    assert old in doomed, "mtime이 최신이어도 파일명 날짜로 지워져야 한다"


# ── monthly_cleanup 안전장치 ─────────────────────────────────────────────────

def test_monthly_cleanup_db_prune_off_by_default():
    """DB 행 삭제는 기본 비활성이고, 켜도 26주(190일) 하한이 강제된다."""
    src = open(os.path.join(ROOT, "scripts", "monthly_cleanup.py"),
               encoding="utf-8").read()
    # [479차] main() 리팩터링으로 변수가 지역화됐다 — 플래그 메커니즘만 고정한다.
    assert '= "--allow-db-prune" in sys.argv' in src
    assert "_MIN_KEEP_DAYS_DB = 190" in src
    assert "max(PRED_KEEP_DAYS, _MIN_KEEP_DAYS_DB)" in src
    assert "max(SHAP_KEEP_DAYS, _MIN_KEEP_DAYS_DB)" in src
    # 로그 보관은 소급 인용 꼬리(182일=26주)보다 길어야 한다
    ns = {}
    for line in src.splitlines():
        if line.startswith("LOG_KEEP_DAYS"):
            exec(line, ns)
    assert ns["LOG_KEEP_DAYS"] >= 182


def test_monthly_cleanup_uses_filename_date():
    """로그 판정이 mtime이 아니라 파일명 날짜여야 한다(지침 §4-3)."""
    sys.path.insert(0, ROOT)
    src = open(os.path.join(ROOT, "scripts", "monthly_cleanup.py"),
               encoding="utf-8").read()
    assert "def log_file_date(" in src
    # 파일 전체를 import 하면 config.settings 를 끌어와 무겁다 —
    # 정규식과 판정 함수만 잘라 실행한다(슬라이스 경계가 깨지면 이 테스트가 먼저 깨진다).
    seg = src[src.index("_LOG_DATE_RE = "):src.index("def _remove(")]
    ns = {}
    exec("import re, datetime\n" + seg, ns)
    f = ns["log_file_date"]
    assert f("20260818_SYSTEM.log") == datetime.date(2026, 8, 18)
    assert f("retrain_eod_20260818.log") == datetime.date(2026, 8, 18)
    assert f("launcher_20260818_084001_2415.log") == datetime.date(2026, 8, 18)
    assert f("creon_launch.log") is None      # 날짜 없으면 지우지 않는다
