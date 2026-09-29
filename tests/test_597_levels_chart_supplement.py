# -*- coding: utf-8 -*-
"""[MW0602 597차] 맥점 산출 — 08:45 시가 결손 시 차트 TR 보충.

2026-09-29: preflight 실패로 09:01 에 늦게 기동 → 08:45~09:00 봉이 버퍼·DB 어디에도
없어 거리·구조 모델이 둘 다 「08:45 시가 결손 — 미산출」로 굳었다.
"""
import io
import os

from features.levels import levels_store as LS
from features.levels import premarket_levels as PL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _row(label, o):
    return {"date": 20260929, "time": label, "open": o, "high": o + 1, "low": o - 1,
            "close": o, "volume": 1, "oi": 0}


def test_chart_rows_use_end_label_minus_one_and_drop_close_fill():
    bars = LS.bars_from_chart_rows(
        [_row(846, 100.0), _row(902, 101.0), _row(1545, 1.0)], "2026-09-29")
    assert [b.t for b in bars] == ["08:45", "09:01"]


def test_supplement_fills_only_missing_minutes_and_keeps_live_bars():
    sup = [PL.Bar("08:45", 100, 101, 99, 100), PL.Bar("09:01", 555, 555, 555, 555)]
    live = [PL.Bar("09:01", 1, 1, 1, 1)]
    bars, n = LS.supplement_bars(live, sup, until="09:30")
    assert n == 1
    assert [b.t for b in bars] == ["08:45", "09:01"]
    assert bars[1].o == 1                      # 실시간 봉 우선


def test_supplement_is_noop_when_0845_present_or_no_supplement():
    live = [PL.Bar("08:45", 1, 1, 1, 1)]
    assert LS.supplement_bars(live, [PL.Bar("08:46", 2, 2, 2, 2)])[1] == 0
    assert LS.supplement_bars([PL.Bar("09:01", 1, 1, 1, 1)], [])[1] == 0


def test_supplement_respects_cut():
    sup = [PL.Bar("08:45", 1, 1, 1, 1), PL.Bar("09:40", 2, 2, 2, 2)]
    bars, n = LS.supplement_bars([], sup, until="08:45")
    assert n == 1 and [b.t for b in bars] == ["08:45"]


def test_main_defers_stage_until_chart_supplement_tried():
    """보충 시도 전 산출하면 미산출 행이 굳는다 — 미룸 가드와 틱 보충이 살아 있어야 한다."""
    src = io.open(os.path.join(ROOT, "main.py"), encoding="utf-8").read()
    i = src.index("def _compute_premarket_levels(")
    head = src[i:i + 2500]
    assert "not self._levels_have_0845() and not self._levels_chart_supp_done" in head
    assert "supplement=self._levels_chart_bars" in src
    # BlockRequest 는 스케줄러 틱에서만(§4) — 봉 확정 콜백에 두지 않는다
    j = src.index("def _scheduler_tick(")
    k = src.index("\n    def ", j + 10)
    assert "request_futopt_minute_bars" in src[j:k]
    c = src.index("def _on_candle_closed(")
    ce = src.index("\n    def ", c + 10)
    assert "request_futopt_minute_bars" not in src[c:ce]


def test_v9_ensure_stage_records_supplement_with_bars_source_and_extra(tmp_path, monkeypatch):
    """[v9-dev 체리픽 적응] v9-dev 의 ensure_stage 는 `bars_source`·`extra`(구독지연)를 함께 기록한다.

    597차 보충이 그 위에 얹혀도 ① 원천 문자열에 `+chart(N봉)` 가 붙고 ② 보충 머리말이
    note/warnings 에 남아야 한다 — 병합에서 새로 생긴 경로다.
    (이력 캐시가 없는 이 경로에서 extra 를 저장하지 않는 것은 v9-dev 원래 동작이다 — 건드리지 않는다.)
    """
    import datetime
    import sqlite3
    from config import settings
    from utils import db_utils

    db = str(tmp_path / "lv.db")
    monkeypatch.setattr(db_utils, "PREMARKET_LEVELS_DB", db, raising=False)
    monkeypatch.setattr(settings, "PREMARKET_LEVELS_DB", db, raising=False)
    db_utils.init_premarket_levels_db()
    raw = str(tmp_path / "raw.db")
    con = sqlite3.connect(raw)
    con.execute("CREATE TABLE raw_candles (ts TEXT PRIMARY KEY, open REAL, high REAL,"
                " low REAL, close REAL, volume INTEGER)")
    con.commit()
    con.close()
    late = [dict(ts=datetime.datetime(2026, 9, 29, 9, 1), open=300.0, high=301.0,
                 low=299.0, close=300.5, volume=9)]
    sup = [PL.Bar("08:45", 299.0, 300.0, 298.0, 299.5)]
    row = LS.ensure_stage("0850", now=datetime.datetime(2026, 9, 29, 9, 2), today_candles=late,
                          db_path=raw, cache_path=str(tmp_path / "hist.json"),
                          extra=dict(subscribe_lag_sec=960.0), supplement=sup)
    assert "+chart(1봉)" in str(row["bars_source"])
    text = " ".join([str(row.get("note") or "")] + list(row.get("warnings") or []))
    assert LS.CHART_SUPPLEMENT_MARK in text
