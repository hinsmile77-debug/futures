# -*- coding: utf-8 -*-
"""[MW0601 477차 후속6 / GR-1] ProfitGuard 래치 기회비용 스크립트 검증.

고정하는 사실:
① 로그 파싱 — L1 래치(피크·보호선)와 차단 분이 각각 TRADE/SIGNAL 로그에서 나온다.
② 깔때기 — 차단분 중 **진입 자격**이 살아 있고 **entry_block_reason이 ProfitGuard**인
   분만 binding이다. 다른 게이트가 선행한 분은 래치를 풀어도 진입이 없다.
③ entry_mode별 허용 등급을 따른다(auto면 C는 자격 미달).
④ 클러스터 — 30분 이내 연속 분은 **한 자리**로 묶인다(313차 ② overlap).
⑤ verdict는 항상 NOT_JUDGED — 판정문 재등록(GR-2)이 승인되기 전까지 임계와
   비교하지 않는다(§9 사전등록).
"""
import json
import os
import sqlite3
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import scripts.profit_guard_latch_watch as pgw


LATCH_LINE = ("2026-08-18 13:19:59 [WARNING] TRADE: [ProfitGuard-L1] 트레일링 발동 — "
              "피크 +927,000원 대비 20% 하락 (현재 +685,000원 < 보호선 +741,600원)\n")


def _block_line(hhmm, layer="L1-Trail"):
    return ("2026-08-18 %s:59 [INFO] SIGNAL: [ProfitGuard] 진입 차단 [%s] 사유\n"
            % (hhmm, layer))


@pytest.fixture
def env(tmp_path, monkeypatch):
    logs = tmp_path / "logs"
    logs.mkdir()
    (logs / "20260818_TRADE.log").write_text(LATCH_LINE, encoding="utf-8")
    monkeypatch.setattr(pgw, "LOG_DIR", str(logs))

    pdb = str(tmp_path / "p.db")
    rdb = str(tmp_path / "r.db")
    con = sqlite3.connect(pdb)
    con.execute("""CREATE TABLE ensemble_decisions (
        ts TEXT, direction INTEGER, grade TEXT, confidence REAL, min_conf REAL,
        entry_mode TEXT, entry_block_reason TEXT, entry_block_axes TEXT,
        entry_executed INTEGER, features TEXT)""")
    con.commit(); con.close()
    con = sqlite3.connect(rdb)
    con.execute("CREATE TABLE raw_candles (ts TEXT, high REAL, low REAL, close REAL)")
    # 하락 추세 — SHORT 반사실이 이익 방향
    for h in range(13, 16):
        for m in range(0, 60):
            t = "2026-08-18 %02d:%02d:00" % (h, m)
            base = 350.0 - (h - 13) * 3.0 - m * 0.05
            con.execute("INSERT INTO raw_candles VALUES (?,?,?,?)",
                        (t, base + 0.4, base - 0.4, base))
    con.commit(); con.close()
    monkeypatch.setattr(pgw, "PREDICTIONS_DB", pdb)
    monkeypatch.setattr(pgw, "RAW_DATA_DB", rdb)
    return {"logs": logs, "pdb": pdb, "rdb": rdb}


def _add_row(pdb, hhmm, grade="C", conf=0.40, mc=0.36, reason="[차단] ProfitGuard 진입 차단",
             mode="manual", direction=-1, atr=1.8):
    con = sqlite3.connect(pdb)
    con.execute("INSERT INTO ensemble_decisions VALUES (?,?,?,?,?,?,?,?,?,?)",
                ("2026-08-18 %s:59" % hhmm, direction, grade, conf, mc, mode,
                 reason, None, 0, json.dumps({"atr": atr})))
    con.commit(); con.close()


def _write_blocks(logs, hhmms):
    (logs / "20260818_SIGNAL.log").write_text(
        "".join(_block_line(h) for h in hhmms), encoding="utf-8")


# ── ① 로그 파싱 ──────────────────────────────────────────────────


def test_latch_parsing(env):
    _write_blocks(env["logs"], ["13:30"])
    latches, blocks = pgw.scan_logs("2026-06-01")
    assert "2026-08-18" in latches
    lt = latches["2026-08-18"]
    assert lt["peak_krw"] == 927000.0
    assert lt["current_krw"] == 685000.0
    assert lt["floor_krw"] == 741600.0
    assert lt["ratio_pct"] == 20
    assert "2026-08-18 13:30" in blocks["2026-08-18"]


# ── ② 깔때기: 다른 게이트가 선행하면 binding이 아니다 ───────────────


def test_binding_excludes_other_gate_reason(env):
    _write_blocks(env["logs"], ["13:30", "13:31"])
    _add_row(env["pdb"], "13:30", reason="[차단] ProfitGuard 진입 차단")
    _add_row(env["pdb"], "13:31", reason="[차단] 등급X — 미통과 항목: 2_confidence")
    res = pgw.compute("2026-06-01")
    d = res["days"][0]
    assert d["funnel"]["entry_qualified"] == 2   # 둘 다 자격은 살아 있다
    assert d["funnel"]["binding"] == 1           # PG가 1등 사유인 것만
    assert d["binding_rows"][0]["ts"].endswith("13:30:59")


def test_unqualified_conf_excluded(env):
    _write_blocks(env["logs"], ["13:30"])
    _add_row(env["pdb"], "13:30", conf=0.30, mc=0.36)   # conf < min_conf
    res = pgw.compute("2026-06-01")
    d = res["days"][0]
    assert d["funnel"]["entry_qualified"] == 0
    assert d["funnel"]["binding"] == 0


def test_minutes_before_latch_ignored(env):
    _write_blocks(env["logs"], ["13:10", "13:30"])
    _add_row(env["pdb"], "13:10")
    _add_row(env["pdb"], "13:30")
    res = pgw.compute("2026-06-01")
    d = res["days"][0]
    assert d["funnel"]["after_latch_minutes"] == 1   # 13:19 래치 이후만
    assert d["funnel"]["binding"] == 1


# ── ③ entry_mode별 허용 등급 ───────────────────────────────────────


def test_entry_mode_auto_rejects_c_grade(env):
    _write_blocks(env["logs"], ["13:30"])
    _add_row(env["pdb"], "13:30", grade="C", mode="auto")   # auto는 A만 허용
    res = pgw.compute("2026-06-01")
    assert res["days"][0]["funnel"]["entry_qualified"] == 0


def test_entry_mode_manual_accepts_c_grade(env):
    _write_blocks(env["logs"], ["13:30"])
    _add_row(env["pdb"], "13:30", grade="C", mode="manual")
    res = pgw.compute("2026-06-01")
    assert res["days"][0]["funnel"]["entry_qualified"] == 1


# ── ④ 클러스터(overlap) ────────────────────────────────────────────


def test_cluster_groups_within_window(env):
    mins = ["13:25", "13:26", "13:40", "14:30"]   # 앞 3개는 30분 내, 마지막은 별도
    _write_blocks(env["logs"], mins)
    for m in mins:
        _add_row(env["pdb"], m)
    res = pgw.compute("2026-06-01")
    d = res["days"][0]
    assert d["funnel"]["binding"] == 4
    assert d["overlap_clusters"] == 2
    assert [c["n_minutes"] for c in d["clusters"]] == [3, 1]
    assert d["clusters"][0]["start"] == "13:25"


def test_cluster_first_minute_reported(env):
    _write_blocks(env["logs"], ["13:25", "13:26"])
    for m in ("13:25", "13:26"):
        _add_row(env["pdb"], m)
    d = pgw.compute("2026-06-01")["days"][0]
    c = d["clusters"][0]
    assert c["net_pts_first"] == d["binding_rows"][0]["net_pts"]
    assert c["net_pts_sum"] == pytest.approx(
        sum(b["net_pts"] for b in d["binding_rows"]), abs=1e-6)


# ── ⑤ 판정 금지 ────────────────────────────────────────────────────


def test_verdict_never_judged(env):
    _write_blocks(env["logs"], ["13:30"])
    _add_row(env["pdb"], "13:30")
    res = pgw.compute("2026-06-01")
    assert res["verdict"] == "NOT_JUDGED"
    assert "주간회의 승인" in res["verdict_note"]
    md = pgw.render_md(res)
    assert "NOT_JUDGED" in md
    # 임계·합격선 문구가 새어 들어오지 않았는지
    assert "PASS" not in md and "FAIL" not in md


def test_render_includes_funnel_columns(env):
    _write_blocks(env["logs"], ["13:30"])
    _add_row(env["pdb"], "13:30")
    md = pgw.render_md(pgw.compute("2026-06-01"))
    assert "깔때기" in md and "binding" in md
    assert "313차" in md          # overlap 경고가 빠지지 않았는지
