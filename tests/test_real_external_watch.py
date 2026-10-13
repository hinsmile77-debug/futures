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
       "_ts_clear_external_watch", "_ts_log_external_watch_skip")


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


def _self(gubun="0", pending=False, last_order_sec_ago=None):
    s = types.SimpleNamespace(
        broker=_Broker(gubun),
        _external_watch=None,
        _external_watch_skip_logged_at=None,
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
    assert b.index("if self._external_watch:") < b.index("request_futures_balance(")


def test_integrity_check_quiet_but_blocking():
    b = _body("_ts_check_position_integrity")
    assert "if self._external_watch:\n        return False" in b


def test_manual_restore_hands_over():
    b = _body("_ts_manual_position_restore")
    assert b.index("_ts_clear_external_watch(") < b.index("self.position.sync_from_broker(")
