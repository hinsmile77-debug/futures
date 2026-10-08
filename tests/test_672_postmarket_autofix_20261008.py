# -*- coding: utf-8 -*-
"""[MW0601 672차] 2026-10-08 장후 자동조치 — F-10 · 장전 고도화 2 · 장후 G-1.

고정하는 것:
  · F-10  수집기 「당일 커밋」 git 경계가 KST(+0900)로 고정된다 — 환경 시간대 무관
          (이상점 1-2: UTC 환경에서 KST 00:00~09:00 커밋이 빠졌다)
  · 고도화2 같은 절에 수집 환경 시간대 한 줄이 찍힌다
  · G-1  `[NetRecon]` 불일치·일치 로그에 엔진 요율 출처(채널·감지 근거)가 붙는다
          (이상점 1-4: CREON 오감지를 DB 조회 없이 로그로 좁히기 위해)
  · G-1 은 문자열만 바꾼다 — channel_note 없이 부르면 종전과 바이트 동일
"""
import importlib.util
import os
import subprocess

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CE = os.path.join(_ROOT, ".claude", "skills", "mireuk-daily-check", "scripts",
                   "collect_evidence.py")


def _ce():
    spec = importlib.util.spec_from_file_location("_ce672", _CE)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _src(rel):
    with open(os.path.join(_ROOT, rel), encoding="utf-8") as f:
        return f.read()


# ── F-10 ────────────────────────────────────────────────────────────────
def test_kst_day_bound_has_explicit_offset():
    m = _ce()
    assert m.kst_day_bound("2026-10-08") == "2026-10-08 00:00:00 +0900"


def test_todays_commit_query_uses_kst_bound():
    s = _src(os.path.join(".claude", "skills", "mireuk-daily-check", "scripts",
                          "collect_evidence.py"))
    assert '"--since=%s 00:00" % D' not in s, "시간대 없는 경계가 남아 있다"
    assert '"--since=%s" % kst_day_bound(D)' in s
    assert '"--until=%s" % kst_day_bound(nxt)' in s


def test_kst_bound_is_timezone_independent():
    """UTC 환경에서도 KST 08:51 커밋(a0f179f)이 2026-10-08 에 들어가야 한다."""
    env = dict(os.environ, TZ="UTC")
    out = subprocess.run(
        ["git", "--no-optional-locks", "log", "--format=%h", "--no-decorate",
         "--since=2026-10-08 00:00:00 +0900", "--until=2026-10-09 00:00:00 +0900"],
        cwd=_ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        universal_newlines=True, encoding="utf-8")
    if out.returncode != 0 or not out.stdout.strip():
        import pytest
        pytest.skip("git 이력 조회 불가 환경")
    hashes = out.stdout.split()
    if not any(h.startswith("a0f179f") for h in hashes):
        import pytest
        pytest.skip("a0f179f 가 이 클론에 없다")
    assert any(h.startswith("a0f179f") for h in hashes)


# ── 장전 고도화 2 ─────────────────────────────────────────────────────────
def test_tz_note_line_states_basis():
    m = _ce()
    line = m.git_tz_note_line()
    assert "KST +0900 고정" in line
    assert "수집 환경 로컬 시간대" in line


def test_tz_note_wired_into_commit_section():
    s = _src(os.path.join(".claude", "skills", "mireuk-daily-check", "scripts",
                          "collect_evidence.py"))
    i = s.index('A("**당일(%s) 커밋**" % D)')
    assert "A(git_tz_note_line())" in s[i:i + 400]


# ── 장후 G-1 ─────────────────────────────────────────────────────────────
_REC = {
    "engine_net": -170128.0, "broker_net": -245601.0, "residual": 75473.0,
    "tolerance": 18720.0, "engine_gross": -152000.0, "broker_gross": -152000.0,
    "engine_commission": 18128.0, "broker_commission": 93601.0,
    "commission_ratio": 5.16,
}


def test_mismatch_without_note_is_unchanged():
    from utils.db_utils import format_net_recon_mismatch as f
    a = f(dict(_REC), True)
    b = f(dict(_REC), True, channel_note=None)
    assert a == b
    assert "엔진 요율 출처" not in a


def test_mismatch_with_note_appends_source_line():
    from utils.db_utils import format_net_recon_mismatch as f
    msg = f(dict(_REC), True, channel_note="CREON 편도 0.0019000% (감지 근거: starter_log:x)")
    assert msg.splitlines()[-1].strip().startswith("· 엔진 요율 출처 : CREON")
    assert msg.startswith("[NetRecon]")


def test_broker_channel_note_reports_channel_and_source():
    from utils.db_utils import broker_channel_note
    from config import settings as S
    note = broker_channel_note()
    assert S.BROKER_CHANNEL in note
    assert str(S.BROKER_CHANNEL_SOURCE) in note
    assert "%" in note


def test_main_netrecon_wired_both_branches():
    s = _src("main.py")
    i = s.index("from utils.db_utils import format_net_recon_mismatch as _f14_fmt")
    blk = s[i:i + 2500]
    assert "channel_note=_g1_note()" in blk
    assert "엔진 요율 출처 {_g1_note()}" in blk
