# -*- coding: utf-8 -*-
"""[MW0601 2026-10-13 거래주체별 규칙 점검 🔴] 브로커 동기화가 외부 주체(피터·신동) 출처를 지우지 않는다.

종전: 동기화 4곳이 무조건 `BROKER_SYNC_RECOVERY` 대입 → `_apply_ext_levels` 가 ext_stop/target 폐기
→ 피터·신동 포지션에 미륵 TP1~3·손절계단·트레일링이 붙고 피터 지시·신동 레그 관리가 멈췄다.
main.py 는 import 비용이 커서 소스에서 헬퍼만 떼어 검사한다(test_631 과 같은 방식).
"""
import io
import os
import types

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SRC = io.open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()

PETER, SHIN = "PETER2_FOLLOW", "SHINDONG"


def _helper():
    seg = _SRC[_SRC.index("def _ts_sync_source_label"):_SRC.index("def _ts_sync_from_balance_payload")]
    logs = []
    ns = {"EXTERNAL_ENTRY_SOURCES": frozenset([PETER, SHIN]),
          "log_manager": types.SimpleNamespace(system=lambda *a, **k: logs.append(a))}
    exec(seg, ns)
    return ns["_ts_sync_source_label"], logs


def _self(status, src, pending=None, label=None):
    # label: 주문 전 setter 가 트래커에 미러링한 출처(FLAT 이어도 position.entry_source 에 남는다)
    return types.SimpleNamespace(
        position=types.SimpleNamespace(status=status, entry_source=label if label is not None else src),
        _pending_order=pending)


def test_preserves_same_side_external():
    f, logs = _helper()
    assert f(_self("LONG", PETER), "LONG") == PETER
    assert f(_self("SHORT", SHIN), "SHORT") == SHIN
    assert logs, "보존 사실을 로그로 남겨야 한다(계측 4원칙 ④)"


def test_opposite_side_or_mireuk_gets_recovery_label():
    f, _ = _helper()
    assert f(_self("LONG", PETER), "SHORT") == "BROKER_SYNC_RECOVERY"
    assert f(_self("LONG", "SYSTEM_AUTO"), "LONG") == "BROKER_SYNC_RECOVERY"
    assert f(_self("FLAT", None, label="SYSTEM_AUTO"), "LONG") == "BROKER_SYNC_RECOVERY"


def test_flat_with_external_entry_pending_preserved():
    f, _ = _helper()
    s = _self("FLAT", None, pending={"kind": "ENTRY", "direction": "LONG"}, label=PETER)
    assert f(s, "LONG") == PETER
    s2 = _self("FLAT", None, pending={"kind": "ENTRY", "direction": "SHORT"}, label=PETER)
    assert f(s2, "LONG") == "BROKER_SYNC_RECOVERY"


def test_all_four_sync_sites_use_helper():
    assert '_entry_source = "BROKER_SYNC_RECOVERY"' not in _SRC
    assert _SRC.count("self._entry_source = _ts_sync_source_label(self, ") == 4
