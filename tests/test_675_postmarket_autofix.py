# -*- coding: utf-8 -*-
"""[MW0601 675차 후속] 장후 자동조치 — F-1(재진단) · G-1(리포트 append 생존 마커)."""
import importlib.util
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load_marker():
    p = os.path.join(ROOT, "scripts", "report_append_marker.py")
    spec = importlib.util.spec_from_file_location("report_append_marker", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ── F-1: shindong2_run.ps1 ─────────────────────────────────────────────

def _ps1():
    with open(os.path.join(ROOT, "scripts", "shindong2_run.ps1"), "rb") as f:
        return f.read()


def test_f1_ps1_stays_pure_ascii():
    # PowerShell 5.1 이 BOM 없는 파일을 ANSI 로 읽는다 — 비-ASCII 한 글자가 파싱을 깬다
    raw = _ps1()
    raw.decode("ascii")


def test_f1_utf8_env_already_set_for_all_live_calls():
    # 리포트 F-1 이 추가하라던 환경변수는 eb4bad3(10/06)부터 스크립트 전역에 있다
    src = _ps1().decode("ascii")
    assert "$env:PYTHONUTF8 = '1'" in src
    assert "$env:PYTHONIOENCODING = 'utf-8'" in src
    assert "--no-capture-output" in src


def test_f1_designed_rc_annotated():
    src = _ps1().decode("ascii")
    assert "designed rc=" in src
    assert "'gate' -and $code -eq 3" in src
    assert "'poll' -and $code -eq 10" in src


# ── G-1: report_append_marker ──────────────────────────────────────────

def test_g1_no_others_rc0(tmp_path):
    m = _load_marker()
    d = str(tmp_path)
    res = m.acquire(d, "MW0601", "20261009", "pre", "s1")
    assert res["others"] == []
    assert os.path.exists(res["path"])
    assert m.main(["check", "--dir", d, "--pc", "MW0601", "--date", "20261009"]) == 2  # 자기 마커도 check 에선 보인다


def test_g1_parallel_session_detected(tmp_path):
    m = _load_marker()
    d = str(tmp_path)
    m.acquire(d, "MW0601", "20261009", "pre", "s1")
    res = m.acquire(d, "MW0601", "20261009", "intra", "s2")
    assert len(res["others"]) == 1
    assert res["others"][0]["phase"] == "pre"
    rc = m.main(["acquire", "--dir", d, "--pc", "MW0601", "--date", "20261009",
                 "--phase", "post", "--session", "s3"])
    assert rc == 2


def test_g1_release_clears(tmp_path):
    m = _load_marker()
    d = str(tmp_path)
    m.acquire(d, "MW0601", "20261009", "pre", "s1")
    assert m.release(d, "MW0601", "20261009", "pre", "s1") is True
    assert m.scan(d, "MW0601", "20261009")["fresh"] == []
    assert m.release(d, "MW0601", "20261009", "pre", "s1") is False


def test_g1_stale_ignored_and_pruned(tmp_path):
    m = _load_marker()
    d = str(tmp_path)
    old = time.time() - 3 * 3600
    m.acquire(d, "MW0601", "20261009", "pre", "dead", now=old)
    res = m.acquire(d, "MW0601", "20261009", "intra", "s2")
    assert res["others"] == []
    assert res["pruned_stale"] == 1


def test_g1_unreadable_not_disguised(tmp_path):
    # 시각을 못 읽는 마커는 신선으로도 스테일로도 위장하지 않는다(계측 4원칙 ②)
    m = _load_marker()
    d = str(tmp_path)
    with open(os.path.join(d, "MW0601-20261009-pre-x.json"), "w") as f:
        f.write("{broken")
    found = m.scan(d, "MW0601", "20261009")
    assert found["fresh"] == [] and found["stale"] == []
    assert len(found["unreadable"]) == 1


def test_g1_other_date_and_pc_isolated(tmp_path):
    m = _load_marker()
    d = str(tmp_path)
    m.acquire(d, "MW0601", "20261008", "post", "y")
    m.acquire(d, "MW0602", "20261009", "post", "z")
    res = m.acquire(d, "MW0601", "20261009", "pre", "s1")
    assert res["others"] == []


def test_g1_default_dir_is_gitignored_data():
    m = _load_marker()
    rel = os.path.relpath(m.DEFAULT_DIR, ROOT).replace("\\", "/")
    assert rel.startswith("data/")


def test_g1_marker_json_fields(tmp_path):
    m = _load_marker()
    res = m.acquire(str(tmp_path), "MW0601", "20261009", "post", "s9")
    with open(res["path"], encoding="utf-8") as f:
        rec = json.load(f)
    for k in ("pc", "date", "phase", "session", "pid", "started_epoch", "started_at"):
        assert k in rec
