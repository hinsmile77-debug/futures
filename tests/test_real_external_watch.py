# -*- coding: utf-8 -*-
"""[MW0602 2026-10-13] 실서버 외부 포지션 = 감시 전용.

사건: 실거래 첫 기동(14:07:31)에서 실계좌 수동 포지션 LONG 2 @938.27 을 startup sync 가
넘겨받아 4~6초 만에 실매도 2건(주문 862·863)이 나갔다.
규칙: 실서버 · 엔진 FLAT · pending 없음 · 최근 자기 주문 없음 → 넘겨받지 않고 감시만.
main.py 는 무거워 import 하지 않고 판정 함수만 떼어 실행한다(test_616 관례).
"""
import ast
import datetime
import io
import os
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(ROOT, "main.py")
FNS = ("_ts_is_real_server", "_ts_should_watch_external", "_ts_start_external_watch",
       "_ts_clear_external_watch", "_ts_log_external_watch_skip",
       "_ts_push_external_exit_target", "_ts_operator_exit_external")


def _src():
    with io.open(MAIN, encoding="utf-8") as f:
        return f.read()


class _Log(object):
    def __init__(self):
        self.lines = []

    def system(self, msg, level="INFO"):
        self.lines.append((level, msg))

    def trade(self, msg):
        self.lines.append(("TRADE", msg))

    def critical(self, msg, *a):
        self.lines.append(("CRITICAL", msg))


def _load(settings=None):
    tree = ast.parse(_src())
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in FNS]
    assert len(nodes) == len(FNS)
    status = []
    ns = {
        "datetime": datetime,
        "runtime_settings": settings or types.SimpleNamespace(
            REAL_EXTERNAL_POSITION_WATCH_ONLY=True, EXTERNAL_ADOPT_OWN_ORDER_GRACE_SEC=120),
        "log_manager": _Log(),
        "logger": _Log(),
        "_ts_set_broker_sync_status": lambda self, v, r, b: status.append((v, r, b)),
    }
    exec(compile(ast.Module(body=nodes, type_ignores=[]), MAIN, "exec"), ns)
    ns["_status"] = status
    return ns


class _Broker(object):
    def __init__(self, gubun):
        self.gubun = gubun

    def get_login_info(self, key):
        return self.gubun


class _Dash(object):
    def __init__(self):
        self.targets = []

    def set_external_exit_target(self, side, qty):
        self.targets.append((side, qty))


def _self(gubun="0", pending=False, last_order_sec_ago=None):
    s = types.SimpleNamespace(
        broker=_Broker(gubun),
        dashboard=_Dash(),
        _external_watch=None,
        _external_watch_skip_logged_at=None,
        _external_manual_exit_at=None,
        _last_pipeline_price=941.0,
        _last_own_order_at=(None if last_order_sec_ago is None else
                            datetime.datetime.now() - datetime.timedelta(seconds=last_order_sec_ago)),
    )
    s._has_pending_order = lambda: pending
    return s


def test_real_flat_no_pending_is_external():
    ns = _load()
    assert ns["_ts_should_watch_external"](_self("0"), "FLAT") is True


def test_mock_server_keeps_old_adoption():
    ns = _load()
    assert ns["_ts_should_watch_external"](_self("1"), "FLAT") is False


def test_engine_holding_or_pending_is_own():
    ns = _load()
    assert ns["_ts_should_watch_external"](_self("0"), "LONG 2계약 @ 938.27") is False
    assert ns["_ts_should_watch_external"](_self("0", pending=True), "FLAT") is False


def test_recent_own_order_is_own_residual():
    ns = _load()
    assert ns["_ts_should_watch_external"](_self("0", last_order_sec_ago=30), "FLAT") is False
    assert ns["_ts_should_watch_external"](_self("0", last_order_sec_ago=300), "FLAT") is True


def test_unknown_server_counts_as_real():
    ns = _load()
    assert ns["_ts_should_watch_external"](_self(""), "FLAT") is True


def test_switch_off_restores_old_behaviour():
    ns = _load(types.SimpleNamespace(REAL_EXTERNAL_POSITION_WATCH_ONLY=False,
                                     EXTERNAL_ADOPT_OWN_ORDER_GRACE_SEC=120))
    assert ns["_ts_should_watch_external"](_self("0"), "FLAT") is False


def test_start_blocks_entries_and_clear_unblocks():
    ns = _load()
    s = _self("0")
    ns["_ts_start_external_watch"](s, "LONG", 2, 938.27, "startup_sync")
    assert s._external_watch["qty"] == 2
    assert ns["_status"][-1][2] is True           # block_new_entries
    ns["_ts_clear_external_watch"](s, "qty=0")
    assert s._external_watch is None
    assert ns["_status"][-1][2] is False
    # 대시보드 수동 청산 버튼: 감시 시작에 열리고 해제에 닫힌다
    assert s.dashboard.targets == [("LONG", 2), ("", 0)]


def _operator_ns(watch_qty=2):
    ns = _load()
    calls = []

    def _direct(self, price, reason, operator=False, qty_cap=None):
        calls.append({"operator": operator, "qty_cap": qty_cap, "reason": reason})
        return True
    ns["_ts_broker_direct_force_exit"] = _direct
    s = _self("0")
    s._external_watch = {"side": "LONG", "qty": watch_qty, "avg": 941.78}
    return ns, s, calls


def test_operator_exit_full_sends_all_as_operator():
    """2026-10-13 사건: 외부 포지션에서 「전량 청산」이 아무 일도 안 했다."""
    ns, s, calls = _operator_ns(2)
    ns["_ts_operator_exit_external"](s, 100)
    assert calls == [{"operator": True, "qty_cap": None, "reason": calls[0]["reason"]}]


def test_operator_exit_partial_and_single_contract():
    ns, s, calls = _operator_ns(4)
    ns["_ts_operator_exit_external"](s, 50)
    assert calls[-1]["qty_cap"] == 2
    ns, s, calls = _operator_ns(1)
    ns["_ts_operator_exit_external"](s, 33)
    assert calls[-1]["qty_cap"] is None          # 1계약은 전량


def test_operator_exit_debounces_double_click():
    ns, s, calls = _operator_ns(2)
    ns["_ts_operator_exit_external"](s, 100)
    ns["_ts_operator_exit_external"](s, 100)
    assert len(calls) == 1


def test_manual_exit_routes_external_before_flat_reject():
    s = _src()      # 클래스 메서드라 _body()(모듈 함수용) 대신 들여쓰기 기준으로 자른다
    i = s.index("    def _on_manual_exit_requested(")
    body = s[i:s.index("\n    def ", i + 1)]
    assert body.index("_ts_operator_exit_external(self, percent)") < body.index("포지션이 없어 수동 청산을 무시")


def test_external_fill_not_adopted_as_ghost_entry():
    """외부 포지션 반대매매 체결이 GHOST_PENDING_MISS 진입으로 넘겨받아지면 안 된다."""
    b = _body("_ts_handle_external_fill")
    assert b.index('if self._external_watch and self.position.status == "FLAT":') \
        < b.index('self._entry_source = "GHOST_PENDING_MISS"')


def _body(fn_name):
    s = _src()
    i = s.index("def %s(" % fn_name)
    j = s.index("\ndef ", i + 1)
    return s[i:j]


def test_startup_sync_checks_watch_before_adopting():
    b = _body("_ts_sync_position_from_broker")
    assert b.index("_ts_should_watch_external(self, before)") < b.index("self.position.sync_from_broker(")


def test_balance_chejan_checks_watch_before_adopting():
    b = _body("_ts_sync_from_balance_payload")
    assert b.index("_ts_should_watch_external(self, before)") < b.index("self.position.sync_from_broker(")
    assert b.index("_ts_clear_external_watch(") < b.index("self.position.sync_flat_from_broker()")


def test_broker_direct_exit_refuses_external():
    b = _body("_ts_broker_direct_force_exit")
    # 자동 경로는 막고, 사람 지시(operator=True)만 통과한다
    assert b.index("if self._external_watch and not operator:") < b.index("request_futures_balance(")


def test_integrity_check_quiet_but_blocking():
    b = _body("_ts_check_position_integrity")
    assert "if self._external_watch:\n        return False" in b


def test_manual_restore_hands_over():
    b = _body("_ts_manual_position_restore")
    assert b.index("_ts_clear_external_watch(") < b.index("self.position.sync_from_broker(")
