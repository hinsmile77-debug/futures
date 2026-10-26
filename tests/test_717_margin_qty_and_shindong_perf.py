# -*- coding: utf-8 -*-
"""[MW0601 717차 후속 — 사용자 승인 2026-10-26] F-1 증거금 조회 · F-3/G-4 신동 경로 계측 — 회귀 고정.

F-1: CpTd6722 시장가 조회에 단가(idx2)를 넣으면 브로커가 `msg=11298` 로 거부한다(10-13 이래 성공 0회).
     + 0계약 판독이 예탁금 추정(2계약 이상)과 모순되면 미측정으로 강등(오판독이 신동 진입을 전부 막지 않게).
F-3/G-4: 「정규 재생 대조 60초 미갱신」 134회(10-26) 원인 판정용 소요시간·정규 대조 간격 계측 — 관찰 전용.
"""
from __future__ import annotations

import datetime as dt
import os
import re
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


# ── F-1 : 입력 목록 ───────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def ac():
    import collection.cybos.api_connector as m
    return m


def _connector(ac):
    c = ac.CybosAPI.__new__(ac.CybosAPI)
    c._ensure_trade_init = lambda: None
    c.margin_qty_fail_count = 0
    c._margin_qty_ok_day = ""
    return c


def test_f1_market_query_sends_no_price(ac, monkeypatch):
    seen = {}

    def fake(progid, input_pairs, data_reader=None, timeout_sec=None):
        seen["pairs"] = list(input_pairs)
        return 0, 0, "", {"sell_new_qty": 4, "buy_new_qty": 5}

    monkeypatch.setattr(ac, "_run_block_request", fake)
    c = _connector(ac)
    out = c.request_order_available_qty("12345", "A056B", 857.5)
    idx = [i for i, _ in seen["pairs"]]
    assert 2 not in idx, "시장가 조회에 단가(idx2)를 넣으면 msg=11298 로 거부된다"
    assert dict(seen["pairs"])[3] == ac.ORDER_HOGA_MARKET
    assert out == {"sell_new_qty": 4, "buy_new_qty": 5}
    assert c.margin_qty_fail_count == 0
    assert c._margin_qty_ok_day != ""            # 당일 첫 성공 원값 로그 1회


def test_f1_failure_still_counted(ac, monkeypatch):
    monkeypatch.setattr(ac, "_run_block_request",
                        lambda **k: (0, -1, "11298 …", None))
    c = _connector(ac)
    assert c.request_order_available_qty("12345", "A056B", 857.5) is None
    assert c.margin_qty_fail_count == 1


# ── F-1 : 0 판독 의심 가드 ─────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def mainmod():
    import main  # noqa: E402  (~5s)
    return main


class _Broker:
    def __init__(self, info):
        self.info = info

    def get_order_available_qty(self, a, c, p):
        return self.info


def _sys(mainmod, info, dep):
    s = mainmod.TradingSystem.__new__(mainmod.TradingSystem)
    s._get_active_account_no = lambda: "12345"
    s._futures_code = "A056B"
    s.broker = _Broker(info)
    s._broker_dep_base_today = dep
    s._pt_value = 50000.0
    return s


def test_f1_real_quantity_passes(mainmod):
    s = _sys(mainmod, {"buy_new_qty": 5, "sell_new_qty": 4}, 30_000_000)
    assert mainmod.TradingSystem._cap_query_margin_qty(s, 857.0) == 4


def test_f1_zero_contradicting_deposit_is_unmeasured(mainmod):
    s = _sys(mainmod, {"buy_new_qty": 0, "sell_new_qty": 0}, 300_000_000)
    assert mainmod.TradingSystem._cap_query_margin_qty(s, 857.0) is None


def test_f1_zero_with_small_deposit_is_real_zero(mainmod):
    s = _sys(mainmod, {"buy_new_qty": 0, "sell_new_qty": 0}, 1_000)
    assert mainmod.TradingSystem._cap_query_margin_qty(s, 857.0) == 0


def test_f1_guard_never_raises_quantity(mainmod):
    """가드는 0 → None 강등 한 방향뿐이다 — 추정치로 수량을 만들어 내지 않는다."""
    src = open(os.path.join(ROOT, "main.py"), encoding="utf-8").read()
    i = src.index("def _cap_query_margin_qty")
    body = src[i:src.index("def _capital_monitor_refresh")]
    assert "return _est" not in body and "return None" in body


# ── F-3 / G-4 : 계측 ─────────────────────────────────────────────────────────
def test_perf_monitor_summary_and_race_signature():
    from strategy.shindong.perf_monitor import ShindongPerf
    p = ShindongPerf(summary_every_sec=600)
    t0 = dt.datetime(2026, 10, 26, 12, 50, 0)
    for i in range(5):
        now = t0 + dt.timedelta(seconds=60.3 * i)
        p.record_ms("flow", 120 + i, now)
        p.record_ms("replay", 300, now)
        p.mark_regular_sync(now)
    p.mark_fallback(t0)
    snap = p.snapshot()
    assert snap["sync_gaps_near60"] == 4 and snap["fallback_n"] == 1
    line = p.format_summary(t0 + dt.timedelta(minutes=5))
    assert line.startswith("[ShindongPerf]")
    assert "exec 미측정" in line and "reconcile 미측정" in line      # 표본 없음 ≠ 0ms
    assert "59–62초 4/4" in line and "대체 대조 1회" in line
    assert "~" not in line


def test_perf_monitor_day_rollover():
    from strategy.shindong.perf_monitor import ShindongPerf
    p = ShindongPerf()
    p.record_ms("flow", 10, dt.datetime(2026, 10, 26, 15, 0))
    p.mark_fallback(dt.datetime(2026, 10, 26, 15, 0))
    p.record_ms("flow", 20, dt.datetime(2026, 10, 27, 9, 5))
    s = p.snapshot()
    assert s["ms"]["flow"] == [20.0] and s["fallback_n"] == 0


def test_perf_is_observation_only():
    """계측 모듈은 주문·수량·손절을 건드리지 않는다(라이브 반영 0)."""
    src = open(os.path.join(ROOT, "strategy", "shindong", "perf_monitor.py"), encoding="utf-8").read()
    for bad in ("_execute_entry", "set_stop", "send_order", "position", "settings"):
        assert bad not in src.replace("positions", "")


def test_gap_log_keeps_collector_prefix():
    """수집기 정규식 `정규 재생 대조 \\d+초 미갱신` 이 계속 잡혀야 한다(문두 형식 유지)."""
    src = open(os.path.join(ROOT, "main.py"), encoding="utf-8").read()
    assert '"%.0f초 미갱신(옵션흐름 수집 미성공)"' in src
    assert "수급 타이머 다음 발화까지" in src
    sample = "[ShindongExec] 정규 재생 대조 60초 미갱신(옵션흐름 수집 미성공) — 직전 재생 결과(DB 9건)로 보유 포지션 대조 | 경과 60.1초"
    assert re.search(r"\[ShindongExec\] 정규 재생 대조 \d+초 미갱신", sample)
