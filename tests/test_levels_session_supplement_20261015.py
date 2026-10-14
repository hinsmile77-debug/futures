# -*- coding: utf-8 -*-
"""[MW0602 2026-10-15] 맥점 이력 — session_bars 보완 · 제외일 재판정 · 과거 세션 보존 · 전일 제외 경보.

계기: 2026-10-13 재기동 공백 109분 → raw_candles 275봉(<300) → 세션 품질 제외 →
10/14 08:50 맥점이 10/12 를 「전일」로 삼았는데 경고가 없었다. 그 109분은 15:46 차트 TR
보충으로 session_bars 에 이미 있었다. 고정하는 불변식:

  ① 보완은 **메모리에서만** — raw_candles 행 수는 변하지 않는다(533차 원칙).
  ② 보완은 raw_candles 하루 정의(08:45~15:08) 안의 **빈 분만** — 실시간 봉 우선.
  ③ session_bars 가 없으면 보완 없이 기존과 같다(미측정 ≠ 0봉 · 크래시 없음).
  ④ 최근 제외일은 데이터가 채워지면 다음 EOD 에 **재편입**되고 제외 목록에서 빠진다.
  ⑤ 전량 재생성은 raw_candles 범위 밖 기존 세션을 **지우지 않는다**(격자 변경 시 paths=None).
  ⑥ 직전 거래일이 제외됐으면 경고가 나오고, main 이 WARNING 으로 올리며, 대시보드가 깜박인다.

py37_32 에서 돈다.
"""

import datetime
import io
import os
import sqlite3
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from features.levels import premarket_levels as PL  # noqa: E402
from features.levels import levels_store as LS  # noqa: E402


DAYS = ["2026-09-%02d" % d for d in (1, 2, 3, 4, 7, 8, 9, 10, 11, 14, 15, 16, 17, 18, 21, 22)]


def _minutes():
    out = []
    for i in range(384):          # 08:45 ~ 15:08
        m = 525 + i
        out.append("%02d:%02d" % (m // 60, m % 60))
    return out


def _px(day_i, i):
    return round(300.0 + day_i * 0.2 + ((i * 7 + day_i) % 11 - 5) * 0.1, 2)


def _db(tmp_path, with_session=True):
    p = str(tmp_path / "raw.db")
    con = sqlite3.connect(p)
    con.execute("CREATE TABLE raw_candles (ts TEXT PRIMARY KEY, open REAL, high REAL, "
                "low REAL, close REAL, volume INTEGER)")
    if with_session:
        con.execute("CREATE TABLE session_bars (ts TEXT PRIMARY KEY, session TEXT, open REAL, "
                    "high REAL, low REAL, close REAL, volume INTEGER, source TEXT)")
    con.commit()
    con.close()
    return p


def _put(db, table, day_i, d, minutes, extra_15xx=False):
    con = sqlite3.connect(db)
    rows = []
    for i, t in enumerate(_minutes()):
        if t not in minutes:
            continue
        c = _px(day_i, i)
        rows.append(("%s %s:00" % (d, t), c, c + 0.3, c - 0.3, c, 10))
    if extra_15xx:                                 # session_bars 는 15:09~ 도 갖는다
        for t in ("15:09", "15:20", "15:45"):
            rows.append(("%s %s:00" % (d, t), 999.0, 999.0, 999.0, 999.0, 1))
    if table == "raw_candles":
        con.executemany("INSERT INTO raw_candles VALUES (?,?,?,?,?,?)", rows)
    else:
        con.executemany("INSERT INTO session_bars VALUES (?,'REGULAR',?,?,?,?,?,'chart_backfill')",
                        [(r[0],) + r[1:] for r in rows])
    con.commit()
    con.close()


def _count(db, table, d):
    con = sqlite3.connect(db)
    try:
        return con.execute("SELECT COUNT(*) FROM %s WHERE ts LIKE ?" % table, (d + "%",)).fetchone()[0]
    finally:
        con.close()


GAP = set(_minutes()[245:354])        # 109분 결손(≈12:50~14:38)
FULL = set(_minutes())


# ────────────────────────────────────────────── ①②③ load_sessions 보완

def test_supplement_fills_only_missing_grid_minutes_and_keeps_raw(tmp_path):
    db = _db(tmp_path)
    d = "2026-10-13"
    _put(db, "raw_candles", 0, d, FULL - GAP)
    _put(db, "session_bars", 0, d, FULL, extra_15xx=True)
    raw_before = _count(db, "raw_candles", d)

    clean, excluded = LS.load_sessions(since=d, db_path=db)

    assert excluded == {} and len(clean) == 1
    bars = clean[0][1]
    assert len(bars) == 384, "08:45~15:08 만 — 15:09 이후 session_bars 봉은 더하지 않는다"
    assert all(b.t <= "15:08" for b in bars)
    assert [b.t for b in bars] == sorted(b.t for b in bars)
    assert LS.LAST_SESSION_SUPPLEMENT == {d: len(GAP)}
    assert _count(db, "raw_candles", d) == raw_before == 384 - len(GAP), "raw_candles 무변경(533차)"


def test_supplement_prefers_raw_bar_on_same_minute(tmp_path):
    db = _db(tmp_path)
    d = "2026-10-13"
    _put(db, "raw_candles", 0, d, FULL)
    con = sqlite3.connect(db)                    # 같은 분, 다른 값의 session_bars
    con.execute("INSERT INTO session_bars VALUES (?,'REGULAR',1,1,1,1,1,'chart_backfill')",
                (d + " 10:00:00",))
    con.commit()
    con.close()
    clean, _ = LS.load_sessions(since=d, db_path=db)
    b = [x for x in clean[0][1] if x.t == "10:00"][0]
    assert b.c != 1.0 and LS.LAST_SESSION_SUPPLEMENT == {}


def test_without_session_bars_behaves_as_before(tmp_path):
    db = _db(tmp_path, with_session=False)
    d = "2026-10-13"
    _put(db, "raw_candles", 0, d, FULL - GAP)
    clean, excluded = LS.load_sessions(since=d, db_path=db)
    assert clean == [] and d in excluded and "275" in excluded[d]
    assert LS.LAST_SESSION_SUPPLEMENT == {}


def test_supplement_can_be_turned_off(tmp_path):
    db = _db(tmp_path)
    d = "2026-10-13"
    _put(db, "raw_candles", 0, d, FULL - GAP)
    _put(db, "session_bars", 0, d, FULL)
    clean, excluded = LS.load_sessions(since=d, db_path=db, session_supplement=False)
    assert clean == [] and d in excluded


# ────────────────────────────────────────────── ④ 제외일 재판정

def test_recent_excluded_day_is_readmitted_when_data_completes(tmp_path):
    # 결손일이 캐시 last_date **앞**에 묻힌 경우 — 2026-10-13(제외) 뒤 10-14 가 들어와
    # last_date 가 넘어간 실제 상황. 뒤에 있으면 일반 증분이 다시 읽으므로 재판정이 필요 없다.
    db = _db(tmp_path)
    cache = str(tmp_path / "hist.json")
    gap_day = DAYS[-3]
    for i, d in enumerate(DAYS[:-1]):
        _put(db, "raw_candles", i, d, FULL - GAP if d == gap_day else FULL)
    r1 = LS.refresh_history_cache(db_path=db, path=cache)
    assert gap_day in r1["excluded"], "15:46 보충이 없던 날 — 제외된다"
    assert r1["last_date"] == DAYS[-2] > gap_day

    # 익일 08:41 보충이 session_bars 를 채우고, 다음 날 세션이 들어온다
    _put(db, "session_bars", len(DAYS) - 3, gap_day, FULL)
    _put(db, "raw_candles", len(DAYS) - 1, DAYS[-1], FULL)
    r2 = LS.refresh_history_cache(db_path=db, path=cache)

    assert r2["readmitted"] == [gap_day]
    assert r2["supplemented"].get(gap_day) == len(GAP)
    assert DAYS[-1] in r2["added"]
    c = LS.load_history_cache(cache)
    assert gap_day in [s["d"] for s in c["summaries"]]
    assert gap_day not in c["excluded"], "편입된 날은 제외 목록에서 빠진다"
    assert _count(db, "raw_candles", gap_day) == 384 - len(GAP), "raw_candles 무변경"


def test_old_excluded_day_is_not_rechecked(tmp_path):
    db = _db(tmp_path)
    cache = str(tmp_path / "hist.json")
    old = DAYS[0]
    for i, d in enumerate(DAYS):
        _put(db, "raw_candles", i, d, FULL - GAP if d == old else FULL)
    LS.refresh_history_cache(db_path=db, path=cache)
    _put(db, "session_bars", 0, old, FULL)
    r = LS.refresh_history_cache(db_path=db, path=cache)
    assert r["readmitted"] == [], "EXCLUDED_RECHECK_DAYS 밖은 다시 보지 않는다"


# ────────────────────────────────────────────── ⑤ 전량 재생성 보존

def test_force_full_preserves_sessions_outside_raw_retention(tmp_path, monkeypatch):
    db = _db(tmp_path)
    cache = str(tmp_path / "hist.json")
    for i, d in enumerate(DAYS):
        _put(db, "raw_candles", i, d, FULL)
    r0 = LS.refresh_history_cache(db_path=db, path=cache)
    n0 = r0["sessions"]
    con = sqlite3.connect(db)                    # raw_candles 보존 범위가 앞 5일을 잘랐다
    con.execute("DELETE FROM raw_candles WHERE ts < ?", (DAYS[5],))
    con.commit()
    con.close()

    r1 = LS.refresh_history_cache(db_path=db, path=cache, force_full=True)
    assert r1["sessions"] == n0 and r1["preserved"] == 5
    c = LS.load_history_cache(cache)
    s = dict((x["d"], x) for x in c["summaries"])
    assert all(d in s for d in DAYS)
    assert s[DAYS[0]]["paths"], "격자 세대가 같으면 경로를 그대로 둔다"
    assert s[DAYS[6]]["atr"] is not None, "앞 세션이 남아 ATR 이 끊기지 않는다"

    monkeypatch.setattr(PL, "PATH_GRID_ID", "test-grid-changed", raising=False)
    r2 = LS.refresh_history_cache(db_path=db, path=cache)
    assert r2["rebuilt"] and r2["preserved"] == 5
    s = dict((x["d"], x) for x in LS.load_history_cache(cache)["summaries"])
    assert s[DAYS[0]]["paths"] is None, "옛 격자 경로를 새 세대 이름으로 남기지 않는다(미측정)"
    assert s[DAYS[10]]["paths"], "raw 로 다시 만든 세션은 새 격자 경로를 갖는다"


# ────────────────────────────────────────────── ⑥ 전일 제외 경고 · 배선 · 화면

def test_prev_session_excluded_warning(tmp_path):
    db = _db(tmp_path)
    for i, d in enumerate(DAYS[:3]):
        _put(db, "raw_candles", i, d, FULL - GAP if i == 2 else FULL)
    prev = PL.SessionSummary(d=DAYS[1], o=300, h=301, l=299, c=300)
    w = LS.prev_session_excluded_warning(prev, DAYS[3], {DAYS[2]: "봉 275개(<300)"}, db_path=db)
    assert w and w.startswith(LS.PREV_EXCLUDED_MARK) and DAYS[2] in w and DAYS[1] in w
    assert LS.prev_session_excluded_warning(prev, DAYS[3], {}, db_path=db) is None
    prev3 = PL.SessionSummary(d=DAYS[2], o=300, h=301, l=299, c=300)
    assert LS.prev_session_excluded_warning(prev3, DAYS[3], {DAYS[2]: "x"}, db_path=db) is None


def test_main_promotes_prev_excluded_warning():
    src = io.open(os.path.join(ROOT, "main.py"), encoding="utf-8").read()
    blk = src[src.index("def _compute_premarket_levels"):][:6000]
    assert "_LS.PREV_EXCLUDED_MARK" in blk and "_LS.STALE_HISTORY_MARK" in blk


def test_dashboard_alert_blinks_and_hides():
    pytest.importorskip("PyQt5")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PyQt5.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    from dashboard.main_dashboard import EntryPanel

    panel = EntryPanel()
    msg = "%s — 직전 거래일(2026-10-13)이 품질 제외" % LS.PREV_EXCLUDED_MARK
    panel.update_premarket_levels({
        "0850": dict(distance=None, structure=dict(up=[], down=[]), note=None,
                     warnings=[msg, "옵션 OI 원천 없음(설계상 제외)"]),
        "0930": dict(distance=None, structure=dict(up=[], down=[]), note=None, warnings=[msg]),
    })
    lbl = panel._levels_alert_lbl
    assert not lbl.isHidden() and lbl.text().count(LS.PREV_EXCLUDED_MARK) == 1, "중복 없이 1줄"
    assert "옵션 OI" not in lbl.text(), "다른 「주의」는 띄우지 않는다"
    assert panel._levels_alert_timer.isActive()
    s1 = lbl.styleSheet()
    panel._on_levels_alert_tick()
    assert lbl.styleSheet() != s1, "깜박임 — 틱마다 스타일이 바뀐다"
    panel.show()
    app.processEvents()
    panel.grab()                                  # paint 경로를 실제로 태운다(CLAUDE.md)

    panel.update_premarket_levels({"0850": dict(distance=None, structure={}, note=None,
                                                warnings=["옵션 OI 원천 없음(설계상 제외)"])})
    assert lbl.isHidden() and not panel._levels_alert_timer.isActive()
    panel.close()
