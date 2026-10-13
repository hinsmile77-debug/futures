# -*- coding: utf-8 -*-
"""[MW0602 2026-10-13] 실거래 자동주문 잠금 — REAL_TRADING_ARMED.

실서버 세션에서 자동 진입(엔진·신동·피터2)은 REAL_TRADING_ARMED=True **와**
CB② 복원(CB_CONSEC_STOP_LIMIT ∈ REAL_TRADING_CB2_ALLOWED) 둘 다일 때만 나간다.
main.py 는 무거워 import 하지 않고, 판정 함수 소스만 떼어 실행한다(test_616 관례).
"""
import ast
import io
import os
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(ROOT, "main.py")
SETTINGS = os.path.join(ROOT, "config", "settings.py")


def _src():
    with io.open(MAIN, encoding="utf-8") as f:
        return f.read()


def _load_fn(settings_ns):
    s = _src()
    tree = ast.parse(s)
    nodes = [n for n in tree.body
             if (isinstance(n, ast.FunctionDef) and n.name == "_ts_real_trading_block_reason")
             or (isinstance(n, ast.Assign)
                 and any(getattr(t, "id", "") == "REAL_TRADING_UNLOCKED_SOURCES" for t in n.targets))]
    assert len(nodes) == 2
    mod = ast.Module(body=nodes, type_ignores=[])
    ns = {"runtime_settings": settings_ns}
    exec(compile(mod, MAIN, "exec"), ns)
    return ns["_ts_real_trading_block_reason"]


class _Broker(object):
    def __init__(self, gubun=None, raise_=False):
        self.gubun, self.raise_ = gubun, raise_

    def get_login_info(self, key):
        assert key == "GetServerGubun"
        if self.raise_:
            raise RuntimeError("com")
        return self.gubun


def _self(gubun=None, raise_=False):
    return types.SimpleNamespace(broker=_Broker(gubun, raise_))


def _settings(armed, cb2):
    return types.SimpleNamespace(REAL_TRADING_ARMED=armed, CB_CONSEC_STOP_LIMIT=cb2,
                                 REAL_TRADING_CB2_ALLOWED=(2, 3))


def test_mock_server_never_blocks():
    fn = _load_fn(_settings(False, 9999))
    for src in ("SYSTEM_AUTO", "SHINDONG", "PETER2"):
        assert fn(_self("1"), src) is None


def test_real_server_blocks_auto_when_not_armed():
    fn = _load_fn(_settings(False, 3))
    for src in ("SYSTEM_AUTO", "SHINDONG_FLOWC", "PETER2"):
        assert "REAL_TRADING_ARMED" in fn(_self("0"), src)


def test_real_server_armed_but_cb2_not_restored_blocks():
    fn = _load_fn(_settings(True, 9999))
    assert "CB②" in fn(_self("0"), "SYSTEM_AUTO")


def test_real_server_armed_and_cb2_restored_passes():
    for cb2 in (2, 3):
        fn = _load_fn(_settings(True, cb2))
        assert fn(_self("0"), "SYSTEM_AUTO") is None


def test_unknown_server_counts_as_real():
    fn = _load_fn(_settings(False, 3))
    assert fn(_self(""), "SYSTEM_AUTO")
    assert fn(_self(raise_=True), "SYSTEM_AUTO")


def test_manual_entry_is_not_locked():
    fn = _load_fn(_settings(False, 9999))
    assert fn(_self("0"), "OPERATOR_MANUAL") is None


def test_gate_is_wired_before_broker_order():
    s = _src()
    body = s[s.index("def _ts_execute_entry("):]
    gate = body.index("_ts_real_trading_block_reason(self, entry_source)")
    order = body.index("self._send_broker_entry_order(")
    assert gate < order
    # 진입 주문 송신은 _ts_execute_entry 한 곳뿐이어야 잠금을 우회할 수 없다
    assert s.count("self._send_broker_entry_order(") == 1


def test_settings_armed_only_with_cb2_restored():
    """[MW0602 2026-10-13 사용자 결정] ARMED=True 로 전환 — 단 CB② 복원과 함께여야 실효가 있다."""
    with io.open(SETTINGS, encoding="utf-8") as f:
        t = f.read()
    assert "\nREAL_TRADING_ARMED = True" in t
    assert "\nREAL_TRADING_CB2_ALLOWED = (2, 3)" in t
    import config.settings as S
    assert S.CB_CONSEC_STOP_LIMIT in S.REAL_TRADING_CB2_ALLOWED
