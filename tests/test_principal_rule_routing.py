# -*- coding: utf-8 -*-
"""[MW0602 2026-10-13] 거래주체별 진입·청산 규칙 라우팅.

미륵은 미륵 규칙, 신동은 신동 규칙, 피터는 피터 규칙으로 청산돼야 한다.
- 외부 주체(신동·피터) 포지션: 손절=주체 지시, TP1~3·손절계단·미륵 트레일링 무력화
- 브로커 동기화가 외부 주체 포지션의 출처를 BROKER_SYNC_RECOVERY 로 덮지 않는다
  (덮이면 _apply_ext_levels 가 주체 손절을 폐기하고 미륵 ATR 규칙이 붙는다)
"""
import ast
import io
import os
import sys
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(ROOT, "main.py")
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def _src():
    with io.open(MAIN, encoding="utf-8") as f:
        return f.read()


def _load_sync_source():
    from config.constants import EXTERNAL_ENTRY_SOURCES
    tree = ast.parse(_src())
    node = [n for n in tree.body
            if isinstance(n, ast.FunctionDef) and n.name == "_ts_broker_sync_source"][0]
    ns = {"EXTERNAL_ENTRY_SOURCES": EXTERNAL_ENTRY_SOURCES}
    exec(compile(ast.Module(body=[node], type_ignores=[]), MAIN, "exec"), ns)
    return ns["_ts_broker_sync_source"]


def _self(status, source, pending=None):
    return types.SimpleNamespace(
        position=types.SimpleNamespace(status=status, entry_source=source),
        _pending_order=pending,
    )


def test_restart_keeps_shindong_and_peter_source():
    fn = _load_sync_source()
    assert fn(_self("SHORT", "SHINDONG"), "SHORT") == "SHINDONG"
    assert fn(_self("LONG", "PETER2"), "LONG") == "PETER2"


def test_stuck_external_entry_keeps_source():
    fn = _load_sync_source()
    s = _self("FLAT", "SHINDONG", {"kind": "ENTRY", "direction": "SHORT"})
    assert fn(s, "SHORT") == "SHINDONG"


def test_mireuk_and_new_adoption_and_opposite_side_are_recovery():
    fn = _load_sync_source()
    assert fn(_self("LONG", "SYSTEM_AUTO"), "LONG") == "BROKER_SYNC_RECOVERY"
    assert fn(_self("FLAT", "SHINDONG"), "LONG") == "BROKER_SYNC_RECOVERY"
    assert fn(_self("SHORT", "SHINDONG"), "LONG") == "BROKER_SYNC_RECOVERY"


def test_no_unconditional_recovery_relabel_left():
    assert 'self._entry_source = "BROKER_SYNC_RECOVERY"' not in _src()
    assert _src().count("self._entry_source = _ts_broker_sync_source(self, ") == 4


def _tracker():
    from strategy.position.position_tracker import PositionTracker
    t = PositionTracker()
    t._save_state = lambda *a, **k: None
    return t


def test_external_position_uses_principal_levels_only():
    t = _tracker()
    for src, stop in (("SHINDONG", 952.0), ("PETER2", 963.0)):
        t.status, t.entry_price, t.quantity, t.entry_source = "SHORT", 959.88, 2, src
        t.stop_price, t.tp1_price = 961.0, 958.0
        t.loss_tier1_price = 960.5
        t.set_external_levels(stop=stop, target=947.88, src=src.lower())
        assert t.stop_price == stop                      # 주체 손절
        assert t.tp1_price > 5000 or t.tp1_price < -5000 # 미륵 TP 무력화(도달 불가)
        assert t.loss_tier1_price == 0.0                 # 미륵 손절계단 무력화
        before = t.stop_price
        t.update_trailing_stop(940.0, 3.0)               # 큰 이익에도
        assert t.stop_price == before                    # 미륵 트레일링 미적용


def test_relabel_to_recovery_would_drop_principal_stop():
    """회귀 의미 고정 — 출처가 BROKER_SYNC_RECOVERY 로 바뀌면 주체 손절이 폐기된다.
    그래서 동기화가 출처를 보존해야 한다(위 테스트들)."""
    t = _tracker()
    t.status, t.entry_price, t.quantity, t.entry_source = "SHORT", 959.88, 2, "SHINDONG"
    t.set_external_levels(stop=952.0, target=947.88, src="shindong")
    t.entry_source = "BROKER_SYNC_RECOVERY"
    t._apply_ext_levels("test")
    assert t.ext_stop is None and t.ext_target is None
