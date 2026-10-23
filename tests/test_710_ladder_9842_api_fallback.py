# -*- coding: utf-8 -*-
"""[MW0601 710차] 사다리 9842 ← API 수집본(strike_investor.db) 폴백 · 장후 스냅샷 대사 오탐 회귀 가드.

고정하는 것
-----------
A. 기간 보유 — 파일·DB 중 늦은 날짜, 같은 날이면 DB(16:25 · 종가 단일가 뒤). 콜·풋 한쪽만이면 쓰지 않는다.
B. 당일 순매수 — 마감본 파일 > (최신 시점 파일 vs DB 최신 측정 분 중 늦은 쪽).
C. 재구성 — 「바뀐 행만」을 이어 붙이고, 건너뛴 분(SKIP_QUOTA)은 칸을 만들지 않으며,
   전체 저장(full=1)이 콜·풋 둘 다 있기 전에는 미측정(None)이다.
D. 금액 단위 시점 파일과는 섞지 않는다(화면이 증감을 못 그린다).
E. DB 가 없으면(미러 PC) 종전 동작 그대로.
F. 장후 스냅샷 — HTS _P 가 15:46 이전 저장이면 대사 불일치를 rc 에 넣지 않는다(2026-10-22 rc=1 오탐).

실행: conda run -n py37_32 python -m pytest tests/test_710_ladder_9842_api_fallback.py -v
"""
import datetime
import json
import os
import sqlite3
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "maekjeom_ladder"))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))
import ladder_data as L  # noqa: E402

from collection.cybos.strike_investor_flow import _SCHEMA  # noqa: E402

_HEAD = ["기관계", "금융투자", "외국인", "개인", "현재가", "행사가", "현재가", "개인", "외국인", "금융투자", "기관계"]


def _xls(path, rows):
    tr = lambda cells: "<tr>%s</tr>" % "".join("<td>%s</td>" % c for c in cells)
    path.write_bytes(("<table>%s</table>" % "".join([tr(_HEAD)] + [tr(r) for r in rows])).encode("euc-kr"))


def _row9(k, v):
    return [str(v)] * 4 + ["9.1", k, "8.0"] + [str(v)] * 4


def _q(frn):
    """외국인 frn, 개인 −frn (합 0)."""
    q = [0] * 12
    q[0], q[1] = -frn, frn
    return q


@pytest.fixture
def env(tmp_path, monkeypatch):
    d = tmp_path / "hts"
    d.mkdir()
    db = tmp_path / "strike_investor.db"
    con = sqlite3.connect(str(db))
    for s in _SCHEMA:
        con.execute(s)
    con.commit()
    monkeypatch.setattr(L, "DOCS_9842", str(d))
    monkeypatch.setattr(L, "STRIKE_DB", str(db))
    L._db9842_cache.clear()
    L._9842_cache.clear()
    return d, con


def _hold(con, day, frn_c, frn_p=None, sides=("C", "P")):
    for cp in sides:
        f = frn_c if cp == "C" else (frn_p if frn_p is not None else frn_c)
        con.execute("INSERT INTO strike_investor_hold VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (day, cp, "1", cp + "1100", 1100.0, "2611", json.dumps(_q(f)), "[]", "[]", "[]",
                     -f, f, 0, "x"))
    con.commit()


def _flow(con, day, hm, cp, frn, full=0, ok=1, strike=1100.0, code=None, write_row=True):
    if write_row:
        con.execute("INSERT INTO strike_investor_flow VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (day, hm, cp, "1", code or (cp + "1100"), strike, "2611", json.dumps(_q(frn)),
                     "[]", "[]", "[]", -frn, frn, 0, "x"))
    con.execute("INSERT OR REPLACE INTO strike_investor_flow_status "
                "(trade_date,snap_hm,cp,month,ok,full) VALUES (?,?,?,?,?,?)", (day, hm, cp, "1", ok, full))
    con.commit()


# ── A. 기간 보유 ─────────────────────────────────────────────────────────
def test_hold_db_only(env):
    d, con = env
    _hold(con, "2026-10-22", 40, 7)
    h = L.hts9842("2026-10-23")
    assert h["hold"]["1100.0"]["c_for"] == 40.0 and h["hold"]["1100.0"]["p_for"] == 7.0
    assert h["hold_unit"] == "contract" and h["hold_date"] == "2026-10-22"
    assert "strike_investor.db" in h["hold_src"] and "기간 보유" in h["hold_src"]


def test_hold_same_date_prefers_db(env):
    """2026-10-22: 15:44:57 저장 파일은 종가 단일가가 빠졌다 — 같은 날짜면 DB."""
    d, con = env
    _xls(d / "261022_P.xls", [_row9("1100", 39)])
    _hold(con, "2026-10-22", 40)
    assert L.hts9842("2026-10-23")["hold"]["1100.0"]["c_for"] == 40.0


def test_hold_later_file_wins(env):
    d, con = env
    _hold(con, "2026-10-21", 40)
    _xls(d / "261022_P.xls", [_row9("1100", 39)])
    h = L.hts9842("2026-10-23")
    assert h["hold"]["1100.0"]["c_for"] == 39.0 and h["hold_src"].startswith("261022_P.xls")
    assert h["hold_date"] == "2026-10-22"


def test_hold_half_side_is_ignored(env):
    d, con = env
    _hold(con, "2026-10-22", 40, sides=("C",))
    assert L.hts9842("2026-10-23")["hold_src"] is None


# ── B·C. 당일 순매수 재구성 ──────────────────────────────────────────────
def _day_flow(con, day="2026-10-23"):
    for cp in "CP":
        _flow(con, day, "09:03", cp, 1, full=1)
    _flow(con, day, "09:10", "C", 5)                       # 콜만 바뀜 — 풋은 상태만
    _flow(con, day, "09:10", "P", 0, write_row=False)
    for cp in "CP":                                        # 한도 부족 — 칸을 만들지 않는다
        _flow(con, day, "09:12", cp, 0, ok=0, write_row=False)
    _flow(con, day, "09:31", "P", 9)
    _flow(con, day, "09:31", "C", 0, write_row=False)


def test_flow_reconstruct_and_snaps(env):
    d, con = env
    _day_flow(con)
    h = L.hts9842("2026-10-23")
    assert [s["hm"] for s in h["flow_snaps"]] == ["09:10", "09:31"]       # 이름표 = 실제 수집 분
    assert h["flow_snaps"][0]["rows"]["1100.0"] == {"c_ind": -5.0, "c_for": 5.0, "c_ins": 0.0,
                                                    "p_ind": -1.0, "p_for": 1.0, "p_ins": 0.0}   # _SNAP_KEYS 만
    assert h["flow"]["1100.0"]["c_for"] == 5.0 and h["flow"]["1100.0"]["p_for"] == 9.0   # 콜은 이어 받는다
    assert h["flow_unit"] == "contract" and "09:31 수집" in h["flow_src"]


def test_flow_unmeasured_without_both_full(env):
    d, con = env
    _flow(con, "2026-10-23", "09:03", "C", 1, full=1)
    _flow(con, "2026-10-23", "09:04", "P", 1, full=0)      # 풋 전체 저장이 없다 — 미측정
    h = L.hts9842("2026-10-23")
    assert h["flow"] == {} and h["flow_snaps"] == [] and h["flow_src"] is None


def test_flow_unmapped_strike_is_excluded_and_counted(env):
    d, con = env
    for cp in "CP":
        _flow(con, "2026-10-23", "09:03", cp, 1, full=1)
    _flow(con, "2026-10-23", "09:03", "C", 4, full=1, strike=None, code="CBA99")
    h = L.hts9842("2026-10-23")
    assert set(h["flow"]) == {"1100.0"} and "미매핑 1행" in h["flow_src"]


def test_daily_file_beats_db(env):
    d, con = env
    _day_flow(con)
    _xls(d / "261023_D.xls", [_row9("1100", 77)])
    h = L.hts9842("2026-10-23")
    assert h["flow"]["1100.0"]["c_for"] == 77.0 and h["flow_src"].startswith("261023_D.xls")


def test_later_snapshot_file_beats_db_and_merges(env):
    d, con = env
    _day_flow(con)
    _xls(d / "261023_0945_D.xls", [_row9("1100", 11)])
    h = L.hts9842("2026-10-23")
    assert h["flow"]["1100.0"]["c_for"] == 11.0 and "09:45 시점" in h["flow_src"]
    assert [(s["hm"], s["fn"]) for s in h["flow_snaps"]] == [
        ("09:10", "strike_investor.db"), ("09:31", "strike_investor.db"), ("09:45", "261023_0945_D.xls")]
    _xls(d / "261023_0931_D.xls", [_row9("1100", 3)])      # 같은 분이면 파일
    h = L.hts9842("2026-10-23")
    assert [s["fn"] for s in h["flow_snaps"] if s["hm"] == "09:31"] == ["261023_0931_D.xls"]


def test_cache_invalidates_on_new_minute(env):
    d, con = env
    _day_flow(con)
    assert L.hts9842("2026-10-23")["flow"]["1100.0"]["p_for"] == 9.0
    _flow(con, "2026-10-23", "09:32", "P", 12)
    _flow(con, "2026-10-23", "09:32", "C", 0, write_row=False)
    assert L.hts9842("2026-10-23")["flow"]["1100.0"]["p_for"] == 12.0


# ── D. 단위 ──────────────────────────────────────────────────────────────
def test_amount_snapshot_files_are_not_mixed(env):
    d, con = env
    _day_flow(con)
    _xls(d / "261023_0915_D.xls", [["1.5"] * 4 + ["9.1", "1100", "8.0"] + ["1.5"] * 4])   # 금액
    h = L.hts9842("2026-10-23")
    assert {s["unit"] for s in h["flow_snaps"]} == {"krw_eok"}
    assert any("금액 단위" in e for e in h["flow_snaps_err"])


# ── E. DB 없음 ───────────────────────────────────────────────────────────
def test_no_db_keeps_file_behavior(env, tmp_path, monkeypatch):
    d, con = env
    monkeypatch.setattr(L, "STRIKE_DB", str(tmp_path / "nope.db"))
    _xls(d / "261022_P.xls", [_row9("1100", 39)])
    h = L.hts9842("2026-10-23")
    assert h["hold"]["1100.0"]["c_for"] == 39.0 and h["flow_snaps"] == [] and h["flow_snaps_err"] == []
    assert L.db9842_dates() == set()


# ── F. 장후 스냅샷 대사 ──────────────────────────────────────────────────
def test_snapshot_hts_saved_before_close(tmp_path):
    import strike_investor_snapshot as S
    p = tmp_path / "261022_P.xls"
    p.write_bytes(b"x")
    for hms, early in (((15, 44, 57), True), ((15, 49, 55), False), ((16, 22, 0), False)):
        ts = datetime.datetime(2026, 10, 22, *hms).timestamp()
        os.utime(str(p), (ts, ts))
        assert S.hts_saved_before_close(str(p), "20261022")[0] is early
    ts = datetime.datetime(2026, 10, 23, 9, 0).timestamp()     # 다음 날 저장한 백필 파일
    os.utime(str(p), (ts, ts))
    assert S.hts_saved_before_close(str(p), "20261022")[0] is False


def test_snapshot_rc_ignores_preclose_mismatch():
    """rc=1 은 「파일이 마감 뒤 저장인데도 다를 때」만 — 소스 배선 고정."""
    src = open(os.path.join(_ROOT, "scripts", "strike_investor_snapshot.py"), encoding="utf-8").read()
    body = src[src.index("same, n, bad, hpath = vr"):]
    body = body[:body.index("_log(line)")]
    assert "hts_saved_before_close(hpath, end)" in body
    assert body.index("if early:") < body.index("rc = 1")
