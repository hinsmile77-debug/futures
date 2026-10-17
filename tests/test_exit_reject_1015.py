# -*- coding: utf-8 -*-
"""[MW0602 2026-10-17] 10/15 실계좌 청산 거부 113분 재발 방지 ①~⑥ — 회귀 테스트.

사고: 10/15 하한가 → 가격제한폭 2단계 확대 → 실시간 가격제한 해제 중 **시장가가 0707로 접수 후
거부**. 시스템 청산은 전부 시장가였고, 체결통보 `거부`를 「아직 체결 전」으로 읽어 미결을 318초씩
붙잡았다(6분 주기 20회, 경보 0건). 지정가 수동 주문은 같은 시간 체결됐다.
근거: docs/정기점검/매일점검/MW0602-20261015-청산거부113분-딥다이브.md

지키는 불변식
  ① 접수 후 거부는 종결 — 청산이면 미결 즉시 해제 + 거부 훅(백오프·첫 거부 경보)
  ② 청산 거부가 한 번 나면 그날 청산은 체결 가능한 지정가(상대 최우선 ± n틱). 평소는 시장가
     · 지정가 미체결 n초 → 취소 요청(1회) · **취소확인 전에는 미결을 풀지 않는다**
  ③ 첫 거부에 Slack(CRITICAL) + 대시보드 깜박임 · 해소 시 회복 알림 + 띠 해제
  ④ 거부 시 주문 조회 덤프 예약(설정으로 끌 수 있다)
  ⑤ 에피소드가 열려 있으면 미륵·신동·피터 신규 실주문 차단
  ⑥ 진입 접수 후 거부 → 낙관적 포지션 즉시 FLAT(유령 포지션 방지)
주문은 나가지 않는다(브로커 스텁).
"""
import datetime
import inspect
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

import main  # noqa: E402


# ── 스텁 ────────────────────────────────────────────────────────────────────

class _Broker(object):
    def __init__(self):
        self.market, self.limit, self.cancel = [], [], []

    def send_market_order(self, **kw):
        self.market.append(kw)
        return 0

    def send_limit_order(self, **kw):
        self.limit.append(kw)
        return {"ret": 0, "order_no": "L%d" % len(self.limit)}

    def cancel_order(self, **kw):
        self.cancel.append(kw)
        return 0

    def get_last_order_error(self):
        return {}


class _Pos(object):
    def __init__(self, status="SHORT", qty=1, entry=869.70, optimistic=False):
        self.status, self.quantity, self.entry_price = status, qty, entry
        self._optimistic = optimistic

    def _reset_position(self):
        self.status, self.quantity, self.entry_price, self._optimistic = "FLAT", 0, 0.0, False


class _RD(object):
    _last_bid1 = 862.90
    _last_ask1 = 863.00


class _Dash(object):
    def __init__(self):
        self.calls = []

    def set_exit_reject_alert(self, active, text=""):
        self.calls.append((bool(active), text))


class _Self(object):
    """TradingSystem 대역 — 이번 경로가 만지는 속성만(main.__init__ 과 같은 초기값)."""

    def __init__(self, pos=None):
        self.broker = _Broker()
        self.position = pos or _Pos()
        self.realtime_data = _RD()
        self.dashboard = _Dash()
        self._futures_code = "A056B"
        self._pending_order = None
        self._pending_limit_is_active = False
        self._exit_reject_streak = 0
        self._exit_reject_kind = ""
        self._exit_reject_last_at = None
        self._exit_reject_alerted = False
        self._exit_retry_block_until = None
        self._broker_closable_qty = None
        self._broker_closable_qty_at = None
        self._exit_limit_mode_reason = None
        self._exit_reject_episode_at = None
        self.cleared = 0

    def _get_active_account_no(self):
        return "00000000"

    def _peter2_last_price(self):
        return 863.18

    def _clear_pending_order(self):
        self.cleared += 1
        self._pending_order = None

    def pend(self, kind="EXIT_FULL", direction="SHORT", qty=1, reason="하드스톱(틱)", order_no="549"):
        self._pending_order = {"kind": kind, "direction": direction, "qty": qty, "filled_qty": 0,
                               "reason": reason, "order_no": order_no,
                               "created_at": datetime.datetime.now()}
        return self._pending_order


class _Spy(object):
    def __init__(self):
        self.trade, self.system = [], []

    def __enter__(self):
        self._orig = (main.log_manager.trade, main.log_manager.system)
        main.log_manager.trade = lambda m, *a, **k: self.trade.append(str(m))
        main.log_manager.system = lambda m, lv="INFO", *a, **k: self.system.append((str(lv), str(m)))
        return self

    def __exit__(self, *a):
        main.log_manager.trade, main.log_manager.system = self._orig


@pytest.fixture(autouse=True)
def _no_detail_query(monkeypatch):
    # ④ 은 QTimer 로 브로커 조회를 예약한다 — 단위 테스트에서는 끈다(배선은 소스 검사로 본다).
    monkeypatch.setattr(main, "EXIT_REJECT_DETAIL_QUERY", False)


def _reject_payload(order_no="549"):
    return {"order_no": order_no, "order_status": "거부", "original_order_no": ""}


# ── ① 접수 후 거부 = 종결 ────────────────────────────────────────────────────

def test_async_exit_reject_is_terminal_and_alerts_once():
    s = _Self()
    po = s.pend()
    with _Spy() as spy:
        main._ts_on_async_order_reject(s, _reject_payload(), po, True)
    assert s._pending_order is None and s.cleared == 1, "미결을 318초 붙잡지 않는다"
    assert s._exit_reject_streak == 1 and s._exit_retry_block_until is not None, "거부 훅·백오프"
    assert s._exit_reject_episode_at is not None
    assert s._exit_limit_mode_reason, "② 래치가 걸린다"
    assert any(m.startswith("[주문거부]") for m in spy.trade)
    assert any(m.startswith("[주문실패]") and "접수 후 거부" in m for m in spy.trade), spy.trade
    alerts = [m for lv, m in spy.system if m.startswith("[ExitRejectAlert]")]
    assert len(alerts) == 1, "③ 첫 거부에 경보"
    assert s.dashboard.calls and s.dashboard.calls[-1][0] is True, "③ 대시보드 깜박임"


def test_alert_is_not_repeated_within_episode():
    s = _Self()
    with _Spy() as spy:
        for i in range(5):
            po = s.pend(order_no=str(600 + i))
            main._ts_on_async_order_reject(s, _reject_payload(str(600 + i)), po, True)
    assert len([m for lv, m in spy.system if m.startswith("[ExitRejectAlert]")]) == 1
    assert s._exit_reject_streak == 5


def test_backoff_caps_at_30s():
    assert max(main.EXIT_REJECT_BACKOFF_SEC) == 30.0
    assert main.EXIT_REJECT_WINDOW_SEC >= 600.0, "6분 간격 거부가 매번 첫 거부로 리셋되지 않는다"
    assert main.EXIT_REJECT_ALERT_STREAK == 1


# ── ⑥ 진입 거부 → 유령 포지션 방지 ──────────────────────────────────────────

def test_async_entry_reject_resets_optimistic_position():
    s = _Self(pos=_Pos(status="LONG", qty=1, entry=965.02, optimistic=True))
    po = s.pend(kind="ENTRY", direction="LONG", reason="진입")
    s._pending_limit_is_active = True
    with _Spy() as spy:
        main._ts_on_async_order_reject(s, _reject_payload("404"), po, True)
    assert s.position.status == "FLAT", "낙관적으로 연 포지션을 즉시 되돌린다"
    assert s._pending_order is None and s._pending_limit_is_active is False
    assert s._exit_reject_episode_at is None, "진입 거부는 청산 거부 에피소드가 아니다"
    assert any(m.startswith("[진입거부]") for m in spy.trade)


def test_unmatched_reject_with_open_position_latches_limit():
    s = _Self()
    with _Spy():
        main._ts_on_async_order_reject(s, _reject_payload("777"), None, False)
    assert s._exit_limit_mode_reason, "브로커 직접청산·긴급청산 거부도 래치를 건다"


# ── ② 청산 지정가 ───────────────────────────────────────────────────────────

def test_core_sends_market_on_normal_day():
    s = _Self()
    ret = main._ts_send_exit_order_core(s, account_no="0", code="A056B", side="BUY", qty=1,
                                        rqname="청산", screen_no="1001")
    assert ret == 0 and len(s.broker.market) == 1 and not s.broker.limit, "평소는 종전과 같은 시장가"


def test_core_sends_marketable_limit_after_latch():
    s = _Self()
    s._exit_limit_mode_reason = "테스트"
    po = s.pend(order_no="")
    with _Spy() as spy:
        ret = main._ts_send_exit_order_core(s, account_no="0", code="A056B", side="BUY", qty=1,
                                            rqname="청산", screen_no="1001")
    assert ret == 0 and not s.broker.market and len(s.broker.limit) == 1
    tick = float(main.get_contract_spec("A056B")["tick_size"])
    want = round(round((863.00 + main.EXIT_LIMIT_SLIP_TICKS * tick) / tick) * tick, 2)
    assert s.broker.limit[0]["price"] == want, (s.broker.limit[0]["price"], want)
    assert po["exit_limit"] and po["order_no"] == "L1", "미결에 지정가 표시 · 주문번호"
    assert any(m.startswith("[청산지정가]") for m in spy.trade)

    s2 = _Self()
    s2._exit_limit_mode_reason = "테스트"
    main._ts_send_exit_order_core(s2, account_no="0", code="A056B", side="SELL", qty=1,
                                  rqname="청산", screen_no="1001")
    want2 = round(round((862.90 - main.EXIT_LIMIT_SLIP_TICKS * tick) / tick) * tick, 2)
    assert s2.broker.limit[0]["price"] == want2, "매도 청산은 매수 최우선 − n틱"


def test_limit_price_falls_back_to_last_price_without_quote():
    s = _Self()
    s.realtime_data = None
    p, src = main._ts_exit_limit_price(s, "BUY", "A056B")
    assert p and p > 863.18 and "직전가" in src, "호가가 없으면 직전가 기준이고 그 사실을 남긴다"


# ── 미체결 취소 · 에피소드 해소 ─────────────────────────────────────────────

def test_unfilled_limit_cancels_once_and_keeps_pending():
    s = _Self()
    po = s.pend(order_no="L1")
    po["exit_limit"] = True
    po["exit_limit_sent_at"] = datetime.datetime.now() - datetime.timedelta(
        seconds=main.EXIT_LIMIT_UNFILLED_SEC + 1)
    with _Spy():
        main._ts_check_exit_order_health(s)
        main._ts_check_exit_order_health(s)
    assert len(s.broker.cancel) == 1, "취소는 1회"
    assert s._pending_order is po, "취소확인 전에는 미결을 풀지 않는다(반대 포지션 방지)"


def test_episode_closes_on_flat_and_keeps_latch():
    s = _Self()
    with _Spy() as spy:
        po = s.pend()
        main._ts_on_async_order_reject(s, _reject_payload(), po, True)
        s.position._reset_position()             # HTS 수동 청산 등으로 FLAT
        main._ts_check_exit_order_health(s)
    assert s._exit_reject_episode_at is None and s._exit_reject_streak == 0
    assert s._exit_limit_mode_reason, "그날 래치는 유지(가격제한 확대 상태는 그대로)"
    assert any(m.startswith("[ExitRejectResolved]") for lv, m in spy.system)
    assert s.dashboard.calls[-1][0] is False, "띠 해제"


# ── ⑤ 신규 실주문 차단 ──────────────────────────────────────────────────────

def test_entry_block_while_episode_open():
    s = _Self()
    assert main._ts_exit_reject_entry_block(s) is None
    s._exit_reject_episode_at = datetime.datetime.now()
    assert "청산 거부 미해결" in main._ts_exit_reject_entry_block(s)


def test_entry_block_is_wired_for_all_principals():
    src = inspect.getsource(main)
    assert "and not _ts_exit_reject_entry_block(self)" in src, "미륵 _final_entry_ok"
    assert "_ts_exit_reject_entry_block(self)" in inspect.getsource(main.TradingSystem._shindong_entry_block_reason)
    assert "_ts_exit_reject_entry_block(self)" in inspect.getsource(main.TradingSystem._peter2_execute)


# ── 배선 (소스) ─────────────────────────────────────────────────────────────

def test_all_exit_paths_use_single_sender():
    assert "_ts_send_exit_order_core(" in inspect.getsource(main.TradingSystem._send_broker_exit_order)
    assert "_ts_send_exit_order_core(" in inspect.getsource(main._ts_broker_direct_force_exit)
    assert "_ts_send_exit_order_core(" in inspect.getsource(main._BrokerOrderAdapter)
    assert "owner=self" in inspect.getsource(main), "긴급청산 어댑터가 owner 를 받는다"


def test_chejan_handler_treats_reject_as_terminal_and_waits_cancel_confirm():
    src = inspect.getsource(main._ts_on_chejan_event_cybos_safe)
    i_rej = src.find('status == "거부"')
    i_cxl = src.find('status == "취소확인"')
    i_fin = src.find("if not is_final_fill:")
    assert 0 <= i_rej < i_fin and 0 <= i_cxl < i_fin, "체결 전 분기보다 앞에서 처리"
    assert "_ts_exit_reject_episode_close(self, \"청산 체결\")" in src


def test_health_check_is_on_2s_timer():
    assert "_ts_check_exit_order_health(self)" in inspect.getsource(main.TradingSystem)


# ── ③ 대시보드 (offscreen 실제 렌더) ────────────────────────────────────────

def test_dashboard_exit_alert_blinks_and_clears():
    pytest.importorskip("PyQt5")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PyQt5.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    from dashboard.main_dashboard import EntryPanel
    p = EntryPanel()
    p.set_exit_reject_alert(True, "청산 주문 거부 — SHORT 1계약 미청산")
    assert not p._exit_alert_lbl.isHidden() and p._exit_alert_timer.isActive()
    s1 = p._exit_alert_lbl.styleSheet()
    p._on_exit_alert_tick()
    assert p._exit_alert_lbl.styleSheet() != s1
    p.show()
    app.processEvents()
    p.grab()
    p.set_exit_reject_alert(False)
    assert p._exit_alert_lbl.isHidden() and not p._exit_alert_timer.isActive()
    p.close()
