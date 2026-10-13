# -*- coding: utf-8 -*-
"""[MW0601 2026-10-14] 우측상단 [진입허용][진입정지] — 운영자 진입 일시정지 불변식.

종전 [모의투자][실서버] 「서버 선언」 라디오의 역할을 바꿨다. 고정하는 것:

1. 정지 게이트는 `_ts_execute_entry` 안, 거래주체 관문 뒤 · 주문 전송 앞에 있다.
2. 수동 버튼(OPERATOR_MANUAL)은 통과한다 — 운영자가 직접 누른 주문이다.
3. 🔴 청산 주문 경로는 정지 여부를 보지 않는다 — 정지 중에도 손절·15:10 청산은 나간다.
4. 차단 로그에 「진입 일시정지중」이 찍힌다.
5. 정지 상태는 ui_prefs 에 저장·복원되고, 기동 시 정지 상태면 로그로 알린다.

실행:
    conda run -n py37_32 python -m pytest tests/test_entry_pause_switch.py -q
"""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _src(rel):
    return io.open(os.path.join(ROOT, rel), encoding="utf-8").read()


def _entry_fn(s):
    fn = s[s.index("def _ts_execute_entry("):]
    return fn[:fn.index("\ndef ")]


def test_gate_sits_after_principal_and_before_send():
    fn = _entry_fn(_src("main.py"))
    g_principal = fn.index("principal_mod.is_live_source(entry_source, _principal)")
    g_pause = fn.index("self.dashboard.is_entry_paused()")
    assert g_principal < g_pause < fn.index("_send_broker_entry_order")


def test_manual_button_bypasses_pause():
    fn = _entry_fn(_src("main.py"))
    g_pause = fn.index("self.dashboard.is_entry_paused()")
    head = fn[:g_pause]
    assert 'if entry_source != "OPERATOR_MANUAL":' in head[-1500:]


def test_block_log_says_paused():
    fn = _entry_fn(_src("main.py"))
    assert "[EntryPause] 진입 일시정지중 — 신규 진입 차단" in fn


def test_exit_order_path_ignores_pause():
    s = _src("main.py")
    ex = s[s.index("    def _send_broker_exit_order"):]
    ex = ex[:ex.index("\n    def ")]
    assert "entry_paused" not in ex and "EntryPause" not in ex


def test_server_match_gate_removed_everywhere():
    # 주석의 이력 언급은 허용 — 정의·호출만 없어야 한다.
    for rel in ("main.py", "dashboard/main_dashboard.py"):
        src = _src(rel)
        assert "def is_server_match" not in src, rel
        assert ".is_server_match()" not in src.replace("`is_server_match()`", ""), rel


def test_prefs_persist_and_startup_notice():
    d = _src("dashboard/main_dashboard.py")
    assert '"entry_paused": self.rdo_entry_pause.isChecked()' in d
    assert 'prefs.get("entry_paused", False)' in d
    m = _src("main.py")
    assert "진입 일시정지중 상태로 기동" in m
    assert "self.dashboard.sig_entry_pause_changed.connect(self._on_entry_pause_changed)" in m
