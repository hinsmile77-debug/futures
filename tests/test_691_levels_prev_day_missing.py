# -*- coding: utf-8 -*-
"""[MW0601 691차] 08:50 맥점 — 전 거래일 이력 없이 산출되면 경고하고 깜박인다.

전일 세션이 수집 결손(<300봉)으로 품질 제외되거나 EOD 캐시 갱신이 빠지면,
`prepare_params` 는 **조용히 그 전 세션**을 「전일」로 삼는다(ATR·갭·구조 후보가
하루 밀린다). 그 사실을 행 warnings 맨 앞에 `PREV_DAY_MISSING_MARK` 로 남기고,
대시보드 08:50 메타 줄이 그 머리말을 보면 깜박인다.

Python 3.7.13 32-bit(py37_32)에서 돌아야 한다.
"""

import datetime
import os
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
    """target 직전 거래일까지 n세션 — drop_last 개를 뒤에서 뺀다(전일 결손 재현)."""
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


def _cache(tmp_path, summaries, bars_by_day, excluded=None):
    p = str(tmp_path / "hist.json")
    LS.save_history_cache(dict(
        updated_at="2026-10-14 15:50:00", path_grid=PL.PATH_GRID_ID,
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


# ────────────────────────────────────────────── 판정 함수

def test_expected_prev_skips_weekend():
    assert LS.expected_prev_trading_day("2026-09-21") == "2026-09-18"   # 월 → 금


def test_no_warning_when_prev_day_present():
    assert LS.prev_day_missing_warning("2026-10-14", "2026-10-15") is None


def test_no_warning_across_weekend():
    assert LS.prev_day_missing_warning("2026-09-18", "2026-09-21") is None


def test_warning_names_missing_day_and_reason():
    w = LS.prev_day_missing_warning("2026-10-13", "2026-10-15",
                                    {"2026-10-14": "봉 296개(<300)"})
    assert w.startswith(LS.PREV_DAY_MISSING_MARK)
    assert "2026-10-14" in w and "2026-10-13" in w and "봉 296개" in w


def test_warning_without_excluded_reason_says_unknown_source():
    w = LS.prev_day_missing_warning("2026-10-13", "2026-10-15")
    assert w.startswith(LS.PREV_DAY_MISSING_MARK) and "EOD" in w


def test_no_warning_when_history_empty():
    assert LS.prev_day_missing_warning(None, "2026-10-15") is None


# ────────────────────────────────────────────── 산출 경로

def test_prepare_params_flags_missing_prev_first():
    ss, bb, _ = _history("2026-10-15", drop_last=1)
    p = LS.prepare_params(ss, bb, "2026-10-15", excluded={"2026-10-14": "봉 296개(<300)"})
    assert p["prev_day_missing"] is True
    assert p["warnings"][0].startswith(LS.PREV_DAY_MISSING_MARK)


def test_prepare_params_quiet_when_prev_present():
    ss, bb, _ = _history("2026-10-15")
    p = LS.prepare_params(ss, bb, "2026-10-15")
    assert p["prev_day_missing"] is False
    assert not any(w.startswith(LS.PREV_DAY_MISSING_MARK) for w in p["warnings"])


def test_frozen_0850_row_carries_mark(tmp_path, monkeypatch):
    db_utils = _tmp_db(tmp_path, monkeypatch)
    ss, bb, _ = _history("2026-10-15", drop_last=1)
    cp = _cache(tmp_path, ss, bb, excluded={"2026-10-14": "봉 296개(<300)"})
    row = LS.ensure_stage("0850", now=datetime.datetime(2026, 10, 15, 8, 50),
                          today_candles=_today_candles("2026-10-15"), cache_path=cp)
    assert row is not None and row["distance"] is not None   # 산출은 그대로 한다
    assert row["warnings"][0].startswith(LS.PREV_DAY_MISSING_MARK)
    assert "봉 296개" in row["warnings"][0]
    # DB 되읽기 경로에서도 살아 있다
    again = db_utils.fetch_premarket_levels("2026-10-15")["0850"]
    assert again["warnings"][0].startswith(LS.PREV_DAY_MISSING_MARK)


# ────────────────────────────────────────────── 화면

def test_entry_panel_blinks_only_with_mark(tmp_path, monkeypatch):
    pytest.importorskip("PyQt5")
    from PyQt5.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    assert app is not None
    from dashboard.main_dashboard import EntryPanel

    _tmp_db(tmp_path, monkeypatch)
    ss, bb, _ = _history("2026-10-15", drop_last=1)
    cp = _cache(tmp_path, ss, bb, excluded={"2026-10-14": "봉 296개(<300)"})
    row = LS.ensure_stage("0850", now=datetime.datetime(2026, 10, 15, 8, 50),
                          today_candles=_today_candles("2026-10-15"), cache_path=cp)

    panel = EntryPanel()
    panel.update_premarket_levels({"0850": row})
    meta = panel._levels_dist_labels["0850"][0]
    assert panel._levels_prev_blink_timer.isActive()
    assert meta.text().startswith("⚠ 전일 이력 없음")
    assert "2026-10-14" in meta.toolTip()
    s0 = meta.styleSheet()
    panel._on_levels_prev_blink_tick()
    assert meta.styleSheet() != s0                     # 실제로 번갈아 바뀐다
    # 반복 갱신해도 머리말이 겹치지 않는다
    panel.update_premarket_levels({"0850": row})
    assert meta.text().count("전일 이력 없음") == 1

    # 정상 행으로 바뀌면 멈춘다
    ok = dict(row)
    ok["warnings"] = [w for w in row["warnings"]
                      if not w.startswith(LS.PREV_DAY_MISSING_MARK)]
    panel.update_premarket_levels({"0850": ok})
    assert not panel._levels_prev_blink_timer.isActive()
    assert not meta.text().startswith("⚠")
    del panel


# ────────────────────────────────────────────── 전일 부분 결손 (주황 고정)

def _drop(bars, times):
    return [b for b in bars if b.t not in set(times)]


def test_partial_warning_lists_runs_and_open_contamination():
    bars = _drop(_day_bars(1), ["08:45", "08:46", "08:47", "10:52"])
    w = LS.prev_day_partial_warning("2026-10-14", bars)
    assert w.startswith(LS.PREV_DAY_PARTIAL_MARK)
    assert "380/384봉" in w and "결손 4봉" in w
    assert "08:45–08:47, 10:52" in w           # 범위는 대시(물결표 금지)
    assert "시가가 08:48 봉 기준" in w


def test_partial_warning_none_when_complete_or_unmeasured():
    assert LS.prev_day_partial_warning("2026-10-14", _day_bars(1)) is None
    assert LS.prev_day_partial_warning("2026-10-14", None) is None   # 미측정 ≠ 결손 0


def test_partial_warning_without_open_gap_has_no_open_note():
    w = LS.prev_day_partial_warning("2026-10-14", _drop(_day_bars(1), ["11:22"]))
    assert "11:22" in w and "시가" not in w


def test_prepare_params_flags_partial_prev():
    ss, bb, days = _history("2026-10-15")
    bb[days[-1]] = _drop(bb[days[-1]], ["08:45", "08:46"])
    p = LS.prepare_params(ss, bb, "2026-10-15")
    assert p["prev_day_partial"] is True and p["prev_day_missing"] is False
    assert any(w.startswith(LS.PREV_DAY_PARTIAL_MARK) for w in p["warnings"])


def test_missing_takes_precedence_over_partial():
    ss, bb, days = _history("2026-10-15", drop_last=1)
    bb[days[-1]] = _drop(bb[days[-1]], ["08:45"])
    p = LS.prepare_params(ss, bb, "2026-10-15")
    assert p["prev_day_missing"] is True and p["prev_day_partial"] is False


def test_entry_panel_partial_is_orange_and_not_blinking(tmp_path, monkeypatch):
    pytest.importorskip("PyQt5")
    from PyQt5.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    assert app is not None
    from dashboard.main_dashboard import EntryPanel

    _tmp_db(tmp_path, monkeypatch)
    ss, bb, days = _history("2026-10-15")
    bb[days[-1]] = _drop(bb[days[-1]], ["08:45", "08:46"])
    cp = _cache(tmp_path, ss, bb)
    row = LS.ensure_stage("0850", now=datetime.datetime(2026, 10, 15, 8, 50),
                          today_candles=_today_candles("2026-10-15"), cache_path=cp)

    panel = EntryPanel()
    meta = panel._levels_dist_labels["0850"][0]
    tip0 = meta.toolTip()
    panel.update_premarket_levels({"0850": row})
    assert not panel._levels_prev_blink_timer.isActive()
    assert meta.text().startswith("△ 전일 부분 결손")
    assert "08:45–08:46" in meta.toolTip()
    panel.update_premarket_levels({"0850": row})
    assert meta.text().count("전일 부분 결손") == 1

    ok = dict(row)
    ok["warnings"] = [w for w in row["warnings"]
                      if not w.startswith(LS.PREV_DAY_PARTIAL_MARK)]
    panel.update_premarket_levels({"0850": ok})
    assert not meta.text().startswith("△")
    assert meta.toolTip() == tip0               # 원래 설명 툴팁 복원
    del panel
