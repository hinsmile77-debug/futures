# -*- coding: utf-8 -*-
"""[MW0602 638차 / F-2] CpTd6722 증거금 조회 — 시장가에는 단가를 넣지 않는다.

배경: 2026-10-13 실거래 전환 이래 `[CybosMarginQty] 조회 실패 … msg=11298 시장가/…
주문은 단가를 입력하지 않습니다` 로 성공 0건이었다(모의서버는 단가를 허용했다).
실서버에서 체결되는 시장가 주문(`send_market_order`)은 이미 `(4, 0)` 을 보낸다.

불변식
- 조회 입력 idx 2(주문가격)는 호가유형이 시장가면 **0** 이다 — 호출부가 넘긴 가격과 무관.
- 실패 시 `[MarginCap] state=UNMEASURED` 를 남기되 **수량은 그대로**, `_margin_probe` 는 건드리지 않는다.
"""
import os
import re

import collection.cybos.api_connector as ac

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _api_with_capture(monkeypatch, result):
    seen = {}

    def _fake(progid, input_pairs, data_reader=None, timeout_sec=None, **kw):
        seen["progid"] = progid
        seen["pairs"] = list(input_pairs)
        return result

    monkeypatch.setattr(ac, "_run_block_request", _fake)
    api = ac.CybosAPI.__new__(ac.CybosAPI)
    api._ensure_trade_init = lambda: None
    api.margin_qty_fail_count = 0
    return api, seen


def test_시장가_조회는_단가를_0으로_보낸다(monkeypatch):
    api, seen = _api_with_capture(monkeypatch, (0, 0, "", {"sell_new_qty": 2, "buy_new_qty": 2}))
    out = api.request_order_available_qty("783293269", "A056B", 864.32)
    assert out == {"sell_new_qty": 2, "buy_new_qty": 2}
    pairs = dict(seen["pairs"])
    assert pairs[3] == ac.ORDER_HOGA_MARKET
    assert pairs[2] == 0


def test_시장가_주문과_같은_단가_규약이다():
    """send_market_order 의 단가 입력(idx 4)도 0 — 실서버에서 체결되는 기준선."""
    with open(os.path.join(_ROOT, "collection", "cybos", "api_connector.py"), encoding="utf-8") as f:
        src = f.read()
    body = src.split("def send_market_order(", 1)[1].split("def send_limit_order(", 1)[0]
    assert "(4, 0)," in body and "(6, ORDER_HOGA_MARKET)," in body


def test_조회_실패는_None_이고_실패카운트가_오른다(monkeypatch):
    api, _ = _api_with_capture(monkeypatch, (0, -1, "11298 단가를 입력하지 않습니다", None))
    assert api.request_order_available_qty("783293269", "A056B", 864.32) is None
    assert api.margin_qty_fail_count == 1


def _capped_qty_src():
    with open(os.path.join(_ROOT, "main.py"), encoding="utf-8") as f:
        src = f.read()
    return src.split("def _ts_margin_capped_qty(", 1)[1].split("\ndef ", 1)[0]


def test_실패_경로는_UNMEASURED_샘플만_남기고_수량은_그대로다():
    body = _capped_qty_src()
    head = body.split('key = "buy_new_qty"', 1)[0]      # 조회 성공 전까지 = 실패 경로
    assert head.count("state=UNMEASURED") == 2         # 예외 · None 두 경로
    assert re.search(r"self\._margin_probe\s*=", head) is None   # sizing_trace margin_binding 은 None 유지
    assert head.count("return qty") >= 3               # 계좌없음 · 예외 · None — 수량 무변경


def test_UNMEASURED_줄은_수집기_조회성공_정규식에_안_걸린다():
    """`상한=` 뒤에 숫자가 오면 §5 `margin_cap` 이 조회 성공으로 센다."""
    import importlib.util
    p = os.path.join(_ROOT, ".claude", "skills", "mireuk-daily-check", "scripts", "collect_evidence.py")
    spec = importlib.util.spec_from_file_location("ce_638", p)
    ce = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ce)
    pats = None
    for name in dir(ce):
        v = getattr(ce, name)
        if isinstance(v, dict) and "day_summary_patterns" in v:
            pats = v["day_summary_patterns"]
    line = "[MarginCap] state=UNMEASURED LONG 산출=1 상한=미측정 사유=조회실패"
    assert re.search(pats["margin_cap"], line) is None
