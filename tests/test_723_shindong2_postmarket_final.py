# -*- coding: utf-8 -*-
"""[MW0601 723차] 장후 실행은 「확정」으로 읽는다 — 15:07 절단 회귀 가드.

사건: `ladder_data.is_live()` 가 08:40–16:15 를 장중으로 봐서, 15:55 신동2 장후 실행이
raw_candles(15:08 끝) − 덜 찬 봉 = 15:07 에서 하루를 자르고 외인 선물 경로도 15:07 에서 잘랐다.
7221 은 15:34, 정규봉은 15:44 까지 적재돼 있었다(10-12–10-27 매 거래일 · 10-15·10-19 외인 부호 반전).

고정하는 것
-----------
A. 15:15 이후 정규봉이 적재됐으면 시각과 무관하게 확정(live=False) — 만기일(15:20 마감)도 포함.
B. 정규봉이 없으면 종전대로 장중 — 장중 판정 자체는 바뀌지 않는다.
C. 장중 시각에는 정규봉 DB 를 보지 않는다(15:15 전 — 456차 무게).
D. 장 마감 뒤 완결 봉에서 잘라 읽었으면 원천 경고가 뜬다(계측 4원칙 ④).

실행:
    conda run -n py37_32 python -m pytest tests/test_723_shindong2_postmarket_final.py -v
"""
import datetime as dt
import json
import os
import sqlite3
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "maekjeom_ladder"))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))
import ladder_data as L  # noqa: E402
import shindong2_live as M  # noqa: E402

DAY = "2026-10-27"          # 화요일 · 거래일


def _regular(tmp_path, last_hm):
    con = sqlite3.connect(str(tmp_path / "regular_candles.db"))
    con.execute("CREATE TABLE regular_candles (code TEXT, ts TEXT, trade_date TEXT, open REAL, high REAL,"
                " low REAL, close REAL, PRIMARY KEY (code, ts))")
    if last_hm:
        for hm in ("15:00", last_hm):
            con.execute("INSERT INTO regular_candles VALUES ('A056B',?,?,1,2,0.5,1.5)", ("%s %s:00" % (DAY, hm), DAY))
    con.commit(); con.close()


def _now(hm):
    return dt.datetime.strptime("%s %s" % (DAY, hm), "%Y-%m-%d %H:%M")


def _setup(tmp_path, monkeypatch, last_hm):
    monkeypatch.setattr(L, "DB", str(tmp_path))
    L._final_days.clear()
    _regular(tmp_path, last_hm)


def test_postmarket_with_regular_loaded_is_final(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch, "15:44")
    assert L.is_live(DAY, _now("15:55")) is False            # 사건의 지문 — 종전엔 True


def test_expiry_day_close_1520_is_final(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch, "15:19")
    assert L.is_live(DAY, _now("15:40")) is False


def test_postmarket_without_regular_stays_live(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch, None)
    assert L.is_live(DAY, _now("15:55")) is True              # 적재 전이면 종전 동작(경고는 build_day 가 띄운다)


def test_intraday_never_reads_regular(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch, "15:44")
    called = []
    monkeypatch.setattr(L, "regular_final", lambda d: called.append(d) or True)
    assert L.is_live(DAY, _now("14:00")) is True and called == []


def _raw(tmp_path, rows):
    d = tmp_path / "data" / "db"
    d.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(d / "raw_data.db"))
    con.execute("CREATE TABLE raw_investor_futures (ts TEXT PRIMARY KEY, fields TEXT, src TEXT)")
    for hm, f in rows:
        con.execute("INSERT INTO raw_investor_futures VALUES (?,?, 'live')",
                    ("%s %s:00" % (DAY, hm), json.dumps(dict(foreign_net_qty=f, institution_net_qty=-f))))
    con.commit(); con.close()


def test_truncated_foreign_after_close_warns(tmp_path, monkeypatch):
    monkeypatch.setattr(M, "ROOT", str(tmp_path))
    _raw(tmp_path, [("15:00", 2700), ("15:07", 2810), ("15:34", 1258)])
    fp = M._foreign_profile(DAY, "15:07")
    assert fp["fut_path"][-1]["foreign"] == 2810 and fp["db_last"] == "15:34"
    st = dict(date=DAY, live=True, last_bar="15:07", foreign=fp, flow={}, rival={"present": True}, prev={"date": "2026-10-26"})
    w = M.source_warnings(st, _now("15:55"))
    assert any("마감 누계 미반영" in x for x in w)
    assert not any("마감 누계 미반영" in x for x in M.source_warnings(st, _now("14:00")))   # 장중엔 정상


def test_final_mode_reads_close_cumulative(tmp_path, monkeypatch):
    monkeypatch.setattr(M, "ROOT", str(tmp_path))
    _raw(tmp_path, [("15:07", 2810), ("15:34", 1258)])
    fp = M._foreign_profile(DAY, None)
    assert fp["fut_path"][-1]["foreign"] == 1258                # 10-27 실측 마감 — 15:07 의 절반 이하
    st = dict(date=DAY, live=False, last_bar="15:44", foreign=fp, flow={}, rival={"present": True}, prev={"date": "2026-10-26"})
    assert not any("마감 누계 미반영" in x for x in M.source_warnings(st, _now("15:55")))


# ── E. 레슨 개정 이력 (723차 L19 재검토) ──────────────────────────────────
def test_lesson_revision_is_logged_without_status_change(tmp_path, monkeypatch):
    import shindong2_learn as LN
    monkeypatch.setattr(LN, "LEARN_DIR", str(tmp_path / "learn"))
    now = dt.datetime(2026, 10, 27, 18, 30)
    LN.lesson_add("L90", "외인 롱 확정 추세일", "규칙", trigger="조건", now=now, axis="진입")
    LN.lesson_set("L90", title="외인 장중 롱 우위 — 장중 한정", trigger="개장 롱", rule="규칙2", why="15:07 절단 정정", now=now)
    l = LN._find(LN.load_lessons(), "L90")
    assert l["title"].endswith("장중 한정") and l["trigger"] == "개장 롱" and l["status"] == "후보"
    assert l["history"][-1]["why"].startswith("개정(title·rule·trigger)")
    n = len(l["history"])
    LN.lesson_set("L90", rule="규칙2", now=now)                       # 같은 값 → 이력 늘지 않는다
    assert len(LN._find(LN.load_lessons(), "L90")["history"]) == n
