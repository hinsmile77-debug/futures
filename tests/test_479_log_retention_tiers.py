# -*- coding: utf-8 -*-
"""[MW0601 479차] 로그 채널별 차등 보관 — 불변식 테스트.

test_476과 같은 원칙: 지키는 것은 「정리가 돈다」가 아니라
**「지우면 안 되는 것을 안 지운다」** 이다. 핵심 불변식 3개:

  1. Tier A(TRADE·SIGNAL·PROBE — 원본 .log를 소급 glob하는 소비 스크립트가
     있는 채널)는 절대 압축 후보에 오르지 않는다. 그리고 scripts/ 안에
     Tier B 채널을 와일드카드 glob으로 소급 소비하는 코드가 새로 생기면
     이 테스트가 깨져 계층 재분류를 강제한다.
  2. Tier B 채널 원본은 삭제 단계([1b])가 절대 지우지 않는다 — 압축이
     실패한 파일을 삭제 단계가 먼저 집어삼키면 영구 소실이다.
  3. HOGA 압축본은 190일 컷([1c])에서 면제된다 — 원시 5호가 잔량의 유일한
     영구 기록(raw_data.db에 호가 테이블 없음). 면제 해제는 주간회의 결정.

실행:
    python -m pytest tests/test_479_log_retention_tiers.py -q
"""
from __future__ import annotations

import datetime
import os
import re
import runpy
import sys
import zipfile

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BODY = os.path.join(ROOT, "scripts", "monthly_cleanup.py")


@pytest.fixture(scope="module")
def mc():
    """monthly_cleanup 본체를 모듈로 적재한다. main()은 __main__ 가드 뒤라
    적재만으로는 아무것도 지우지 않는다."""
    ns = runpy.run_path(BODY, run_name="_mc_under_test")
    return ns


@pytest.fixture(scope="module")
def cs():
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    from scripts import campaign_steps
    return campaign_steps


TODAY = datetime.date(2026, 8, 19)


# ── 1. 채널 파싱 ──────────────────────────────────────────────────────────────

def test_log_channel_parsing(mc):
    fn = mc["log_channel"]
    assert fn("20260818_SYSTEM.log") == (datetime.date(2026, 8, 18), "SYSTEM")
    # 회전본도 같은 채널로
    assert fn("20260515_SYSTEM.log.2026-05-15") == (datetime.date(2026, 5, 15), "SYSTEM")
    assert fn("20260610_CATCH_UP_EOD.log")[1] == "CATCH_UP_EOD"
    # 채널 로그가 아닌 것들
    assert fn("retrain_eod_20260818.log") == (None, None)
    assert fn("retrain_intraday_20260818_101112.log") == (None, None)
    assert fn("creon_launch.log") == (None, None)
    assert fn("202605_SYSTEM.zip") == (None, None)
    # 존재하지 않는 날짜
    assert fn("20260231_SYSTEM.log") == (None, None)


# ── 2. 계층 정의 불변식 ──────────────────────────────────────────────────────

def test_tier_sets_disjoint(mc):
    raw = mc["_RAW_KEEP_CHANNELS"]
    comp = mc["_COMPRESS_CHANNELS"]
    assert not (raw & comp), "한 채널이 두 계층에 동시에 속할 수 없다"
    # 소급 소비자가 실측된 3채널은 반드시 Tier A다 (2026-08-19 전수조사)
    assert {"TRADE", "SIGNAL", "PROBE"} <= raw
    # HOGA 면제는 압축 채널에만 의미가 있다
    assert mc["_ARCHIVE_DELETE_EXEMPT"] <= comp


# 예외 허용 목록 — 그 스크립트의 소비 창이 LOG_COMPRESS_DAYS(30일) 안의
# **후행 창**임을 확인했을 때만 등록한다. 값은 근거(없으면 등록 금지).
_RETRO_GLOB_EXEMPT = {
    # dev(MW0602) 전용 진단 도구. 전 기간 glob 뒤 [-args.days:] 슬라이스 —
    # 기본 3일·통상 ≤5일 후행 창이라 원본이 항상 남아 있다(30일 유예 안).
    # ⚠ --days 를 25 이상으로 쓰려면 압축본 대응을 먼저 넣을 것.
    "pipeperf_step_decomposition.py":
        "[MW0602 468차 G-4] 최근 N거래일 후행 창(기본 3) — 압축 유예 안",
}


def test_no_script_retro_globs_compressed_channels(mc):
    """scripts/ 안에 Tier B 채널을 **와일드카드 glob**으로 소급 소비하는 코드가
    생기면 실패한다 — 그 채널은 30일 뒤 zip이 되므로 그 스크립트는 조용히
    표본을 잃는다. 당일 로그를 쓰는 생산자(aggregate_and_backfill.py 등,
    와일드카드 없음)는 걸리지 않고, 30일 안 후행 창만 읽는 스크립트는
    _RETRO_GLOB_EXEMPT에 근거와 함께 등록한다."""
    comp = mc["_COMPRESS_CHANNELS"]
    pat = re.compile(r"\*[^\"']*_(%s)\.log" % "|".join(sorted(comp)))
    offenders = []
    scripts_dir = os.path.join(ROOT, "scripts")
    for name in os.listdir(scripts_dir):
        if not name.endswith(".py") or name == "monthly_cleanup.py":
            continue
        if name in _RETRO_GLOB_EXEMPT:
            continue
        path = os.path.join(scripts_dir, name)
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f, 1):
                if pat.search(line):
                    offenders.append("%s:%d: %s" % (name, i, line.strip()))
    assert not offenders, (
        "Tier B(압축) 채널을 와일드카드로 소급 소비하는 스크립트 발견 — "
        "해당 채널을 _RAW_KEEP_CHANNELS로 옮기거나 스크립트를 압축본 대응으로 "
        "고칠 것:\n" + "\n".join(offenders))


# ── 3. 압축 후보 선정 ────────────────────────────────────────────────────────

def test_compress_candidates_selection(mc):
    fn = mc["compress_candidates"]
    names = [
        "20260501_SYSTEM.log",                # 대상 (110일 전)
        "20260501_SYSTEM.log.2026-05-01",     # 회전본도 같은 번들
        "20260615_HOGA.log",                  # 대상
        "20260810_SYSTEM.log",                # 9일 전 — 어리다
        "20260719_SYSTEM.log",                # 31일 전 — 대상 (경계 밖)
        "20260720_SYSTEM.log",                # 정확히 30일 — 보존 (경계)
        "20260501_TRADE.log",                 # Tier A — 절대 안 걸린다
        "20260501_SIGNAL.log",                # Tier A
        "retrain_eod_20260501.log",           # 비채널 — 안 걸린다
        "202605_SYSTEM.zip",                  # 이미 압축본
        "creon_launch.log",                   # 날짜 없음
        "crash_fault.log",
    ]
    groups = fn(names, TODAY)
    assert set(groups) == {("202605", "SYSTEM"), ("202606", "HOGA"),
                           ("202607", "SYSTEM")}
    assert groups[("202605", "SYSTEM")] == [
        "20260501_SYSTEM.log", "20260501_SYSTEM.log.2026-05-01"]
    assert groups[("202607", "SYSTEM")] == ["20260719_SYSTEM.log"]


# ── 4. 원본 삭제 단계의 처분 ─────────────────────────────────────────────────

def test_original_delete_target(mc):
    fn = mc["original_delete_target"]
    cut = datetime.date(2026, 2, 10)   # 190일 컷 실측값과 같은 스케일
    assert fn("crash_fault.log", cut) == "protect"
    assert fn("discovery_results_20250101_120000.json", cut) == "protect"
    assert fn("creon_launch.log", cut) == "nodate"
    # 🔴 핵심 불변식 2: Tier B 원본은 아무리 오래돼도 [1b]가 지우지 않는다
    assert fn("20250101_SYSTEM.log", cut) == "compress_channel"
    assert fn("20250101_HOGA.log", cut) == "compress_channel"
    assert fn("20250101_SYSTEM.log.2025-01-01", cut) == "compress_channel"
    # 압축본은 [1c] 소관
    assert fn("202501_SYSTEM.zip", cut) == "archive"
    # Tier A·비채널 날짜 파일은 기존 190일 컷 그대로
    assert fn("20250101_TRADE.log", cut) == "delete"
    assert fn("retrain_eod_20250101.log", cut) == "delete"
    assert fn("20260818_TRADE.log", cut) == "keep"


# ── 5. 압축본 삭제 단계 ──────────────────────────────────────────────────────

def test_archive_delete_candidates(mc):
    fn = mc["archive_delete_candidates"]
    cut = datetime.date(2026, 2, 10)
    names = [
        "202601_SYSTEM.zip",   # 말일 2026-01-31 < 컷 → 삭제
        "202512_SYSTEM.zip",   # 12월 분기 처리 → 삭제
        "202602_SYSTEM.zip",   # 말일 2026-02-28 ≥ 컷 → 보존 (달 일부가 창에 걸침)
        "202601_HOGA.zip",     # 🔴 핵심 불변식 3: HOGA 면제
        "202608_MICRO.zip",    # 최근 → 보존
        "foo.zip",             # 형식 불일치 → 무시
    ]
    assert fn(names, cut) == ["202512_SYSTEM.zip", "202601_SYSTEM.zip"]


def test_zip_names_invisible_to_date_regex(mc):
    """월 zip 이름(YYYYMM 6자리)이 기존 8자리 날짜 정규식에 오인 매칭되면
    [1b]가 zip을 '날짜 있는 파일'로 오판한다 — 구조적으로 불가능해야 한다."""
    date_re = mc["_LOG_DATE_RE"]
    for n in ("202605_SYSTEM.zip", "202612_HOGA.zip", "202501_MICRO.zip"):
        assert date_re.search(n) is None, n


# ── 6. 압축 실행부 왕복 ──────────────────────────────────────────────────────

def _write(d, name, content):
    with open(os.path.join(d, name), "w", encoding="utf-8") as f:
        f.write(content)


def test_compress_roundtrip(mc, tmp_path):
    log_dir = str(tmp_path)
    _write(log_dir, "20260501_SYSTEM.log", "may-1 " * 100)
    _write(log_dir, "20260502_SYSTEM.log", "may-2 " * 100)
    _write(log_dir, "20260601_HOGA.log", "jun-hoga " * 100)
    groups = mc["compress_candidates"](sorted(os.listdir(log_dir)), TODAY)

    # dry-run은 아무것도 바꾸지 않는다
    mc["compress_into_archives"](log_dir, groups, dry_run=True)
    assert sorted(os.listdir(log_dir)) == [
        "20260501_SYSTEM.log", "20260502_SYSTEM.log", "20260601_HOGA.log"]

    # 실적용: zip 생성 + 원본 삭제 + 내용 보존
    mc["compress_into_archives"](log_dir, groups, dry_run=False)
    assert sorted(os.listdir(log_dir)) == ["202605_SYSTEM.zip", "202606_HOGA.zip"]
    with zipfile.ZipFile(os.path.join(log_dir, "202605_SYSTEM.zip")) as zf:
        assert sorted(zf.namelist()) == ["20260501_SYSTEM.log", "20260502_SYSTEM.log"]
        assert zf.read("20260501_SYSTEM.log").decode("utf-8") == "may-1 " * 100

    # 멱등: 원본이 사라진 그룹으로 재실행해도 조용히 지나간다
    mc["compress_into_archives"](log_dir, groups, dry_run=False)
    assert sorted(os.listdir(log_dir)) == ["202605_SYSTEM.zip", "202606_HOGA.zip"]


def test_compress_residue_and_conflict(mc, tmp_path):
    """이전 실행이 '추가 후 삭제 전'에 중단된 잔재(같은 크기)는 원본만 지우고,
    크기가 다른 동명 파일은 **양쪽 다 보존**한다(모르면 지우지 않는다)."""
    log_dir = str(tmp_path)
    _write(log_dir, "20260501_SYSTEM.log", "original " * 50)
    groups = mc["compress_candidates"](sorted(os.listdir(log_dir)), TODAY)
    mc["compress_into_archives"](log_dir, groups, dry_run=False)
    assert os.listdir(log_dir) == ["202605_SYSTEM.zip"]

    # 잔재 시나리오 — 같은 내용으로 원본이 다시 나타남
    _write(log_dir, "20260501_SYSTEM.log", "original " * 50)
    mc["compress_into_archives"](log_dir, groups, dry_run=False)
    assert os.listdir(log_dir) == ["202605_SYSTEM.zip"]

    # 충돌 시나리오 — 크기가 다른 동명 파일: 원본·압축본 모두 생존
    _write(log_dir, "20260501_SYSTEM.log", "DIFFERENT-and-longer " * 80)
    mc["compress_into_archives"](log_dir, groups, dry_run=False)
    assert sorted(os.listdir(log_dir)) == ["202605_SYSTEM.zip", "20260501_SYSTEM.log"] or \
           sorted(os.listdir(log_dir)) == ["20260501_SYSTEM.log", "202605_SYSTEM.zip"]
    with zipfile.ZipFile(os.path.join(log_dir, "202605_SYSTEM.zip")) as zf:
        assert zf.read("20260501_SYSTEM.log").decode("utf-8") == "original " * 50


# ── 7. 발화 지점(마커) ───────────────────────────────────────────────────────

def test_monthly_cleanup_due_marker(cs, tmp_path):
    base = str(tmp_path)
    os.makedirs(os.path.join(base, "data"))

    class _L:
        def warning(self, *a):
            pass

    today = datetime.date(2026, 8, 21)   # 금요일
    # 마커 없음 → due
    assert cs.monthly_cleanup_due(base, today) is True
    # 성공 기록 → 같은 달은 더 안 돈다
    cs._monthly_cleanup_mark_done(base, _L(), today)
    assert cs.monthly_cleanup_due(base, today) is False
    assert cs.monthly_cleanup_due(base, datetime.date(2026, 8, 28)) is False
    # 달이 바뀌면 다시 due
    assert cs.monthly_cleanup_due(base, datetime.date(2026, 9, 4)) is True
    # 마커 파일이 깨져 있어도(빈 파일) due — "모르면 돌린다"(정리는 멱등)
    with open(cs._monthly_cleanup_marker(base), "w") as f:
        f.write("")
    assert cs.monthly_cleanup_due(base, today) is True
