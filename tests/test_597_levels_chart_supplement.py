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
