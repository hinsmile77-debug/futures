# -*- coding: utf-8 -*-
"""[MW0602 2026-10-24 / 집행 장치 A4] 청산 재송신 직전 브로커 잔고 강제 재조회.

고정하는 불변식
  · 재송신일 때만 조회한다(거부 에피소드 열림 · 지정가 미체결 취소 뒤). 평소 첫 청산은 조회 0회
  · 판정 원천은 `잔고수량` — `청산가능`(closable) 0 오독에 속지 않는다
  · 판정 5종: SEND_AS_IS · SEND_REDUCED · SKIP_FLAT · SKIP_OPPOSITE · SEND_FALLBACK(미측정)
  · shadow 는 기록만 — 송신 수량·횟수가 종전과 같다
  · live 는 판정대로 — 축소 송신 · 생략(-96, 거부로 세지 않음) · SKIP_FLAT 이면 브로커 동기화
  · 15:18 브로커 직접청산(balance_checked=True)은 재조회하지 않는다
  · 조회 예외·판정 예외는 송신을 막지 않는다
"""
import datetime
import io
import json
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

import main  # noqa: E402


def _row(side="매도", qty="2", closable="2", code="A056B"):
    return {"종목코드": code, "매매구분": side, "구분": side, "잔고수량": qty, "청산가능": closable}


class _Broker(object):
    def __init__(self, result):
        self.result = result
        self.queries = 0
        self.sent = []

    def request_futures_balance(self, account_no):
        self.queries += 1
        if isinstance(self.result, Exception):
            raise self.result
        return self.result

    def send_market_order(self, **kw):
        self.sent.append(kw)
        return 0


class _Pos(object):
    def __init__(self, status="SHORT", qty=2):
        self.status, self.quantity, self.entry_source = status, qty, "SHINDONG"


class _Me(object):
    _normalize_broker_code = main.TradingSystem._normalize_broker_code

    def __init__(self, result, status="SHORT", qty=2, episode=True):
        self.position = _Pos(status, qty)
        self.broker = _Broker(result)
        self._exit_reject_episode_at = datetime.datetime(2026, 10, 26, 10, 0) if episode else None
        self._exit_resend_since = None
        self._exit_limit_mode_reason = None
        self._pending_order = None
        self.synced = 0

    def _sync_position_from_broker(self):
        self.synced += 1


@pytest.fixture
def jsonl(tmp_path, monkeypatch):
    p = str(tmp_path / "exit_resend_balance_shadow.jsonl")
    monkeypatch.setattr(main, "_RESEND_BALANCE_JSONL", p)
    return p


def _rows(p):
    if not os.path.exists(p):
        return []
    return [json.loads(x) for x in io.open(p, encoding="utf-8") if x.strip()]


def _send(me, qty=2, side="BUY", **kw):
    return main._ts_send_exit_order_core(me, account_no="123", code="A056B", side=side, qty=qty,
                                         rqname="청산", screen_no="1001", **kw)


# ── 순수 판정 ──────────────────────────────────────────────────────────────

@pytest.mark.parametrize("held,order,action,qty", [
    ({"measured": True, "status": "SHORT", "qty": 2}, 2, "SEND_AS_IS", 2),
    ({"measured": True, "status": "SHORT", "qty": 3}, 2, "SEND_AS_IS", 2),
    ({"measured": True, "status": "SHORT", "qty": 1}, 2, "SEND_REDUCED", 1),
    ({"measured": True, "status": "FLAT", "qty": 0}, 2, "SKIP_FLAT", 0),
    ({"measured": True, "status": "LONG", "qty": 2}, 2, "SKIP_OPPOSITE", 0),
    ({"measured": False, "status": None, "qty": None, "why": "x"}, 2, "SEND_FALLBACK", 2),
])
def test_1_판정(held, order, action, qty):
    v = main._ts_resend_balance_verdict("SHORT", 2, order, held)
    assert (v["action"], v["qty"]) == (action, qty), v


def test_2_해석은_잔고수량을_쓰고_청산가능_0에_속지_않는다():
    me = _Me(None)
    h = main._ts_broker_holding(me, {"nonempty_rows": [_row(qty="2", closable="0")]}, "A056B")
    assert h == {"measured": True, "status": "SHORT", "qty": 2, "why": h["why"]}
    assert main._ts_broker_holding(me, None, "A056B")["measured"] is False
    h0 = main._ts_broker_holding(me, {"nonempty_rows": [_row(code="A101W")]}, "A056B")
    assert h0["measured"] is True and h0["qty"] == 0 and h0["status"] == "FLAT"
    assert main._ts_broker_holding(me, {"rows": []}, "056B")["qty"] == 0
    bad = main._ts_broker_holding(me, {"rows": [_row(qty="두개")]}, "A056B")
    assert bad["measured"] is False


# ── 언제 조회하나 ──────────────────────────────────────────────────────────

def test_3_재송신이_아니면_조회하지_않는다(jsonl, monkeypatch):
    monkeypatch.setattr(main, "EXIT_RESEND_BALANCE_MODE", "shadow")
    me = _Me({"rows": [_row()]}, episode=False)
    assert _send(me) == 0
    assert me.broker.queries == 0 and len(me.broker.sent) == 1 and _rows(jsonl) == []


def test_4_지정가_미체결취소_뒤는_재송신이다(jsonl, monkeypatch):
    monkeypatch.setattr(main, "EXIT_RESEND_BALANCE_MODE", "shadow")
    me = _Me({"rows": [_row()]}, episode=False)
    me._exit_resend_since = datetime.datetime(2026, 10, 26, 10, 1)
    _send(me)
    assert me.broker.queries == 1
    r = _rows(jsonl)
    assert len(r) == 1 and r[0]["limit_cancel_resend"] is True and r[0]["episode_open"] is False


def test_5_off_모드와_직접청산은_조회하지_않는다(jsonl, monkeypatch):
    monkeypatch.setattr(main, "EXIT_RESEND_BALANCE_MODE", "off")
    me = _Me({"rows": [_row()]})
    _send(me)
    monkeypatch.setattr(main, "EXIT_RESEND_BALANCE_MODE", "live")
    _send(me, balance_checked=True)
    assert me.broker.queries == 0 and len(me.broker.sent) == 2


# ── shadow: 주문 무변경 ────────────────────────────────────────────────────

@pytest.mark.parametrize("result,action", [
    ({"rows": [_row(qty="1")]}, "SEND_REDUCED"),
    ({"rows": []}, "SKIP_FLAT"),
    ({"rows": [_row(side="매수")]}, "SKIP_OPPOSITE"),
    (None, "SEND_FALLBACK"),
    (RuntimeError("COM"), "SEND_FALLBACK"),
])
def test_6_섀도는_기록만_하고_주문은_종전과_같다(jsonl, monkeypatch, result, action):
    monkeypatch.setattr(main, "EXIT_RESEND_BALANCE_MODE", "shadow")
    me = _Me(result)
    assert _send(me) == 0
    assert [s["qty"] for s in me.broker.sent] == [2] and me.synced == 0
    r = _rows(jsonl)
    assert len(r) == 1 and r[0]["action"] == action and r[0]["applied"] is False
    assert r[0]["engine_status"] == "SHORT" and r[0]["order_qty"] == 2 and r[0]["side"] == "BUY"


# ── live: 판정대로 ────────────────────────────────────────────────────────

def test_7_live_축소_송신(jsonl, monkeypatch):
    monkeypatch.setattr(main, "EXIT_RESEND_BALANCE_MODE", "live")
    me = _Me({"rows": [_row(qty="1")]})
    assert _send(me) == 0
    assert [s["qty"] for s in me.broker.sent] == [1]
    assert _rows(jsonl)[0]["applied"] is True


def test_8_live_실보유0이면_생략하고_동기화(jsonl, monkeypatch):
    monkeypatch.setattr(main, "EXIT_RESEND_BALANCE_MODE", "live")
    me = _Me({"rows": []})
    assert _send(me) == main.EXIT_RET_BALANCE_SKIP
    assert me.broker.sent == [] and me.synced == 1


def test_9_live_반대방향이면_생략_동기화없음(jsonl, monkeypatch):
    monkeypatch.setattr(main, "EXIT_RESEND_BALANCE_MODE", "live")
    me = _Me({"rows": [_row(side="매수")]})
    assert _send(me) == main.EXIT_RET_BALANCE_SKIP
    assert me.broker.sent == [] and me.synced == 0


def test_10_live_미측정이면_종전대로_송신(jsonl, monkeypatch):
    monkeypatch.setattr(main, "EXIT_RESEND_BALANCE_MODE", "live")
    me = _Me(None)
    assert _send(me) == 0 and [s["qty"] for s in me.broker.sent] == [2]


def test_11_생략은_거부로_세지_않는다(monkeypatch):
    me = _Me(None)
    me._exit_reject_streak = 0
    me._exit_reject_last_at = None
    main._ts_on_exit_order_reject(me, kind="하드스톱", direction="SHORT", qty=2,
                                  ret=main.EXIT_RET_BALANCE_SKIP)
    assert me._exit_reject_streak == 0


def test_12_판정_예외는_송신을_막지_않는다(jsonl, monkeypatch):
    monkeypatch.setattr(main, "EXIT_RESEND_BALANCE_MODE", "live")
    monkeypatch.setattr(main, "_ts_resend_balance_verdict", lambda *a, **k: 1 / 0)
    me = _Me({"rows": []})
    assert _send(me) == 0 and [s["qty"] for s in me.broker.sent] == [2]


def test_13_FLAT_이면_재송신_표시를_지운다():
    me = _Me(None, status="FLAT", qty=0, episode=False)
    me._exit_resend_since = datetime.datetime(2026, 10, 26, 10, 1)
    assert main._ts_is_exit_resend(me) is False and me._exit_resend_since is None


def test_14_기본값은_섀도():
    from config import settings as st
    assert st.EXIT_RESEND_BALANCE_MODE == "shadow"
