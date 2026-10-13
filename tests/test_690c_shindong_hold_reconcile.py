# -*- coding: utf-8 -*-
"""[MW0601 2026-10-13] 신동 보유 중 재생 대조·복원을 옵션흐름 수집과 분리했다.

종전: `_run_shindong`(→ `_shindong_exec_step`)이 `_fetch_weekly_option_flow` 의 수집 성공 뒤에만 돌아,
수집이 끊긴 분에는 보유 포지션의 손절 조이기·재생 청산 미러·재기동 복원이 멈췄다.
지금: 2초 슬롯이 60초 넘게 정규 대조가 없으면 DB 의 직전 재생 결과로 보유 분기를 돈다.
"""
import io
import os

_SRC = io.open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py"),
               encoding="utf-8").read()


def _fn(name):
    i = _SRC.index("    def %s(" % name)
    j = _SRC.index("\n    def ", i + 10)
    return _SRC[i:j]


def test_called_from_existing_2s_slot_without_new_timer():
    tick = _fn("_peter2_tick")
    assert "self._shindong_hold_reconcile()" in tick
    # 신동 예외 가둠 블록 안(피터2 와 예외를 섞지 않는다 — 617차 슬롯 규약)
    i = tick.index("self._shindong_target_poll()")
    assert "self._shindong_hold_reconcile()" in tick[i:i + 200]


def test_only_when_holding_shindong_and_uses_persisted_replay():
    f = _fn("_shindong_hold_reconcile")
    assert "is_external_of(SHINDONG_ENTRY_SOURCE)" in f.split("now =")[0], "보유 중이 아니면 즉시 반환"
    assert "_has_pending_order()" in f
    assert "60.0" in f
    assert "load_trades(runtime_settings.SHINDONG_DB, day, \"MAIN\")" in f, \
        "run_and_store 가 돌려주는 것과 같은 DB 재생 결과를 써야 한다"
    assert "self._shindong_exec_step(" in f
    assert "self._sd_exec_last_sync = now" in f
    assert "log_manager.system(" in f, "대체 대조 사용을 드러내야 한다(계측 4원칙 ④)"


def test_regular_path_stamps_last_sync_and_state_initialized():
    run = _fn("_run_shindong")
    i = run.index("self._shindong_exec_step(payload, now)")
    assert "self._sd_exec_last_sync = now" in run[i:i + 120]
    init = _SRC[_SRC.index("self._sd_exec_orphan_warned = False"):][:600]
    assert "self._sd_exec_last_sync = None" in init and "self._sd_hold_gap_logged = False" in init


def test_exec_step_holding_branch_returns_before_new_entry():
    """보유 분기는 신규 진입 전에 반환한다 — 대체 대조가 진입을 일으키지 않는 근거."""
    f = _fn("_shindong_exec_step")
    hold = f.index("if pos.is_external_of(SHINDONG_ENTRY_SOURCE):")
    ret = f.index("return", hold)
    entry = f.index("pick_new_entry")
    assert hold < ret < entry
