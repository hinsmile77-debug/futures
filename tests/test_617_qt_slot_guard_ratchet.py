# -*- coding: utf-8 -*-
"""[MW0601 617차] Qt 슬롯 무가드 **래칫** — 늘어나지만 않게 막는다.

왜 "전부 고치기"가 아니라 래칫인가
----------------------------------
2026-09-22 09:41:56 사고의 기전은 **PyQt5 가 슬롯에서 새어나온 예외를
`qFatal()` 로 처리한다**는 것이다. 그러니 원칙적으로 모든 슬롯이 가드돼야
한다. 그런데 무가드 슬롯 중 셋은 `main.py:TradingSystem` 의 **엔진 슬롯**이다
(`_on_main_heartbeat`·`_effect_report_timer_tick`·`_check_limit_entry_timeout`).

    표시 슬롯은 삼켜도 된다 — 화면이 비는 것뿐이다.
    엔진 슬롯을 삼키면 **주문·청산 실패가 조용히 사라진다.**

즉 일괄 try/except 는 이 사고의 교훈(= 조용히 그럴듯한 값)을 그대로 재생산한다.
그래서 이 테스트는 **판정하지 않고 고정만 한다** — 지금 있는 무가드는 기준선으로
두고, **새로 생기는 것만** 막는다. 기준선을 줄이는 것은 슬롯별로 "삼켜도 되는가"를
판단한 뒤의 일이며, 그 판단은 주간회의 몫이다.

이 테스트가 깨지면
------------------
① 새 무가드 슬롯을 추가했거나 ② 기준선의 슬롯을 고쳤다.
②면 아래 목록에서 그 줄을 **지워라**(래칫은 한 방향으로만 돈다).

    python scripts/audit_qtimer_slot_guards.py --show all

실행:
    conda run -n py37_32 python -m pytest tests/test_617_qt_slot_guard_ratchet.py -q
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (ROOT, os.path.join(ROOT, "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import audit_qtimer_slot_guards as audit


#: 2026-09-22 617차 시점의 무가드 슬롯. **늘리지 말 것.**
#:   · `main.py::TradingSystem.*` 3건은 엔진 슬롯이라 의도적으로 남겼다(위 설명).
#:   · 나머지는 표시 슬롯이며, 손대는 김에 하나씩 가드하고 이 목록에서 지우면 된다.
BASELINE = {
    "dashboard/main_dashboard.py::DivergencePanel.self._render_age_chip",
    "dashboard/main_dashboard.py::EntryPanel.self._on_blink_tick",
    "dashboard/main_dashboard.py::EntryPanel.self._on_entry_blink_tick",
    "dashboard/main_dashboard.py::EntryPanel.self._on_trend_blink_tick",
    "dashboard/main_dashboard.py::EntryPanel.self._update_mode_desc",
    "dashboard/main_dashboard.py::LogPanel.self._tick_status",
    "dashboard/main_dashboard.py::MireukDashboard.self._blink_phase5_gate",
    "dashboard/main_dashboard.py::MireukDashboard.self._blink_profit_guard",
    "dashboard/main_dashboard.py::MireukDashboard.self._refresh_cycle_badge",
    "dashboard/main_dashboard.py::UiAutoTabController.self._tick_manual_override",
    "dashboard/panels/atr_multiple_monitor_panel.py::ATRMultipleMonitorPanel.self.refresh",
    "dashboard/panels/entry_horizon_monitor_panel.py::EntryHorizonMonitorPanel.self.refresh",
    "dashboard/panels/regime_panel.py::RegimePanel.self._refresh",
    "dashboard/panels/scaler_monitor_panel.py::ScalerMonitorPanel.self.refresh",
    "dashboard/panels/threshold_monitor_panel.py::ThresholdMonitorPanel.self.refresh",
    "main.py::TradingSystem.self._check_limit_entry_timeout",
    "main.py::TradingSystem.self._effect_report_timer_tick",
    "main.py::TradingSystem.self._on_main_heartbeat",
}


def _unguarded():
    rows = []
    for p in sorted(set(audit._iter_py(audit.TARGETS))):
        r, err = audit.scan_file(p, False)
        assert err is None, "%s 파싱 실패 — %s" % (p, err)
        rows.extend(r)
    assert rows, "timeout.connect 를 하나도 못 찾았다 — 감사기가 망가진 것이다"
    return {"%s::%s.%s" % (r["file"], r["cls"], r["target"])
            for r in rows if r["state"] == audit.UNGUARDED}


def test_no_new_unguarded_slot():
    """새 무가드 슬롯이 생기면 실패한다."""
    new = _unguarded() - BASELINE
    assert not new, (
        "새 무가드 QTimer 슬롯 %d건 — 예외가 새면 PyQt5 가 프로세스를 죽인다: %s"
        % (len(new), " / ".join(sorted(new)))
    )


def test_baseline_has_no_stale_entry():
    """고쳐 놓고 목록에서 안 지운 항목을 잡는다 — 래칫은 한 방향으로만 돈다."""
    stale = BASELINE - _unguarded()
    assert not stale, (
        "이미 가드된 슬롯이 기준선에 남아 있다. BASELINE 에서 지워라: %s"
        % " / ".join(sorted(stale))
    )


def test_chart_slots_are_guarded():
    """617차가 실제로 고친 두 화면은 기준선에 있으면 안 된다."""
    un = _unguarded()
    for key in ("dashboard/panels/direction_indicator_dialog.py",
                "dashboard/panels/candle_chart_dialog.py"):
        offenders = [k for k in un if k.startswith(key)]
        assert not offenders, (
            "%s 의 슬롯이 다시 무가드다 — 2026-09-22 사고 경로다: %s"
            % (key, offenders)
        )
