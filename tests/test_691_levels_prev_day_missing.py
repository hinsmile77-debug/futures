# -*- coding: utf-8 -*-
"""[MW0601 691차 → dev 이식] 08:50 맥점 — 전일 이력 경고.

dev 에는 MW0602 2026-10-15(`8775ddf`)가 이미 「전일 세션 품질 제외」·「이력 캐시 낡음」
경보 띠(깜박임)를 갖고 있다. 이 이식은 그 둘이 **침묵할 때만** 두 가지를 더한다.
  · 「전일 이력 없음」 — 직전 KRX 거래일(달력)이 이력에 없음(raw_candles 에도 없어
    두 프로브가 못 잡는 경우). 같은 경보 띠로 깜박인다.
  · 「전일 부분 결손」 — 전일은 있으나 08:45–15:08 분봉 일부가 빠짐. 08:50 메타 줄에
    깜박이지 않는 주황으로 표시.

`raw_candles` 프로브는 빈 임시 DB 로 격리한다(실 DB 를 읽지 않는다).
Python 3.7.13 32-bit(py37_32)에서 돌아야 한다.
"""

import datetime
import os
import sqlite3
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from features.levels import premarket_levels as PL
from features.levels import levels_store as LS


def _day_bars(seed, base=300.0):
    out = []
    for i in range(384):
        m = 525 + i
        amp = 1.0 + i / 60.0
        c = round(base + (amp if (i + seed) % 3 else -amp), 2)
        out.append(PL.Bar(t="%02d:%02d" % (m // 60, m % 60),
                          o=c, h=round(c + 0.3, 2), l=round(c - 0.3, 2), c=c, v=10))
    return out


def _trading_days_before(target, n):
    from utils.time_utils import is_trading_day
    d = datetime.date(*[int(x) for x in target.split("-")])
    out = []
    while len(out) < n:
        d -= datetime.timedelta(days=1)
        if is_trading_day(d):
            out.append(d.isoformat())
    return sorted(out)


def _history(target, n=70, drop_last=0):
    days = _trading_days_before(target, n)
    if drop_last:
        days = days[:-drop_last]
    summaries, bars_by_day = [], {}
    for i, d in enumerate(days):
        b = _day_bars(i, 300.0 + i * 0.1)
        summaries.append(PL.summarize_session(d, b))
        if i >= len(days) - (PL.LOOKBACK + 1):
            bars_by_day[d] = b
    PL.fill_derived(summaries)
    return summaries, bars_by_day, days


def _raw_db(tmp_path):
    """빈 raw_candles — 「품질 제외」·「캐시 낡음」 프로브가 아무것도 못 찾게 한다."""
    p = str(tmp_path / "raw691.db")
    con = sqlite3.connect(p)
    con.execute("CREATE TABLE IF NOT EXISTS raw_candles (ts TEXT PRIMARY KEY, open REAL,"
                " high REAL, low REAL, close REAL, volume INTEGER)")
    con.commit()
    con.close()
    return p


def _cache(tmp_path, summaries, bars_by_day, excluded=None):
    p = str(tmp_path / "hist.json")
    LS.save_history_cache(dict(
        updated_at="2026-10-14 15:50:00", path_grid=getattr(PL, "PATH_GRID_ID", None),
        last_date=summaries[-1].d,
        summaries=[PL.summary_to_dict(s) for s in summaries],
        bars=dict((d, [PL.bar_to_dict(b) for b in bs]) for d, bs in bars_by_day.items()),
        excluded=excluded or {}), p)
    return p


def _tmp_db(tmp_path, monkeypatch):
    from config import settings
    from utils import db_utils
    db = str(tmp_path / "pml691.db")
    monkeypatch.setattr(settings, "PREMARKET_LEVELS_DB", db, raising=False)
    monkeypatch.setattr(db_utils, "PREMARKET_LEVELS_DB", db, raising=False)
    db_utils.init_premarket_levels_db()
    return db_utils


def _today_candles(day, until_min=8 * 60 + 50):
    y, m, d = [int(x) for x in day.split("-")]
    out = []
    for b in _day_bars(99):
        hh, mm = int(b.t[:2]), int(b.t[3:])
        if hh * 60 + mm > until_min:
            break
        out.append(dict(ts=datetime.datetime(y, m, d, hh, mm),
                        open=b.o, high=b.h, low=b.l, close=b.c, volume=b.v))
    return out


def _drop(bars, times):
    return [b for b in bars if b.t not in set(times)]


# ────────────────────────────────────────────── 판정 함수

def test_expected_prev_skips_weekend():
    assert LS.expected_prev_trading_day("2026-09-21") == "2026-09-18"


def test_missing_warning_rules():
    assert LS.prev_day_missing_warning("2026-10-14", "2026-10-15") is None
    assert LS.prev_day_missing_warning("2026-09-18", "2026-09-21") is None
    assert LS.prev_day_missing_warning(None, "2026-10-15") is None
    w = LS.prev_day_missing_warning("2026-10-13", "2026-10-15")
    assert w.startswith(LS.PREV_DAY_MISSING_MARK) and "2026-10-14" in w


def test_partial_warning_lists_runs_and_open_contamination():
    w = LS.prev_day_partial_warning(
        "2026-10-14", _drop(_day_bars(1), ["08:45", "08:46", "08:47", "10:52"]))
    assert w.startswith(LS.PREV_DAY_PARTIAL_MARK)
    assert "380/384봉" in w and "08:45–08:47, 10:52" in w
    assert "시가가 08:48 봉 기준" in w


def test_partial_warning_none_when_complete_or_unmeasured():
    assert LS.prev_day_partial_warning("2026-10-14", _day_bars(1)) is None
    assert LS.prev_day_partial_warning("2026-10-14", None) is None


# ────────────────────────────────────────────── 산출 경로 (MW0602 경보와의 관계)

def test_missing_flagged_when_probes_silent(tmp_path):
    ss, bb, _ = _history("2026-10-15", drop_last=1)
    p = LS.prepare_params(ss, bb, "2026-10-15", db_path=_raw_db(tmp_path))
    assert p["prev_day_missing"] is True
    assert any(w.startswith(LS.PREV_DAY_MISSING_MARK) for w in p["warnings"])


def test_partial_flagged_when_prev_present(tmp_path):
    ss, bb, days = _history("2026-10-15")
    bb[days[-1]] = _drop(bb[days[-1]], ["08:45", "08:46"])
    p = LS.prepare_params(ss, bb, "2026-10-15", db_path=_raw_db(tmp_path))
    assert p["prev_day_partial"] is True and p["prev_day_missing"] is False


def test_quiet_when_complete(tmp_path):
    ss, bb, _ = _history("2026-10-15")
    p = LS.prepare_params(ss, bb, "2026-10-15", db_path=_raw_db(tmp_path))
    assert not p["prev_day_missing"] and not p["prev_day_partial"]


def test_no_duplicate_when_mw0602_alert_fires(tmp_path, monkeypatch):
    """「전일 세션 품질 제외」가 뜨면 같은 사실을 「전일 이력 없음」으로 또 내지 않는다."""
    ss, bb, _ = _history("2026-10-15", drop_last=1)
    monkeypatch.setattr(LS, "latest_session_before", lambda *a, **k: "2026-10-14")
    p = LS.prepare_params(ss, bb, "2026-10-15", excluded={"2026-10-14": "봉 275개(<300)"})
    ws = p["warnings"]
    assert any(w.startswith(LS.PREV_EXCLUDED_MARK) for w in ws)
    assert not any(w.startswith(LS.PREV_DAY_MISSING_MARK) for w in ws)


# ────────────────────────────────────────────── 화면

_APP = []   # ⚠ QApplication 을 모듈 수준에서 붙잡는다 — 지역 변수면 GC 가 거둬 위젯이 죽는다


def _panel():
    pytest.importorskip("PyQt5")
    from PyQt5.QtWidgets import QApplication
    if not _APP:
        _APP.append(QApplication.instance() or QApplication([]))
    from dashboard.main_dashboard import EntryPanel
    return EntryPanel()


def test_missing_mark_blinks_in_alert_band(tmp_path, monkeypatch):
    _tmp_db(tmp_path, monkeypatch)
    ss, bb, _ = _history("2026-10-15", drop_last=1)
    row = LS.ensure_stage("0850", now=datetime.datetime(2026, 10, 15, 8, 50),
                          today_candles=_today_candles("2026-10-15"),
                          db_path=_raw_db(tmp_path), cache_path=_cache(tmp_path, ss, bb))
    panel = _panel()
    panel.update_premarket_levels({"0850": row})
    assert panel._levels_alert_timer.isActive()
    assert LS.PREV_DAY_MISSING_MARK in panel._levels_alert_lbl.text()
    s0 = panel._levels_alert_lbl.styleSheet()
    panel._on_levels_alert_tick()
    assert panel._levels_alert_lbl.styleSheet() != s0
    del panel


def test_partial_is_orange_static_and_restores_tooltip(tmp_path, monkeypatch):
    _tmp_db(tmp_path, monkeypatch)
    ss, bb, days = _history("2026-10-15")
    bb[days[-1]] = _drop(bb[days[-1]], ["08:45", "08:46"])
    row = LS.ensure_stage("0850", now=datetime.datetime(2026, 10, 15, 8, 50),
                          today_candles=_today_candles("2026-10-15"),
                          db_path=_raw_db(tmp_path), cache_path=_cache(tmp_path, ss, bb))
    panel = _panel()
    meta = panel._levels_dist_labels["0850"][0]
    tip0 = meta.toolTip()
    panel.update_premarket_levels({"0850": row})
    assert not panel._levels_alert_timer.isActive()        # 깜박이지 않는다
    assert meta.text().startswith("△ 전일 부분 결손")
    assert "08:45–08:46" in meta.toolTip()
    panel.update_premarket_levels({"0850": row})
    assert meta.text().count("전일 부분 결손") == 1
    ok = dict(row)
    ok["warnings"] = [w for w in row["warnings"]
                      if not w.startswith(LS.PREV_DAY_PARTIAL_MARK)]
    panel.update_premarket_levels({"0850": ok})
    assert not meta.text().startswith("△") and meta.toolTip() == tip0
    del panel
