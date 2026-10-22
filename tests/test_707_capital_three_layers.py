# -*- coding: utf-8 -*-
"""[MW0601 707차 → dev 선별 이식 2026-10-23] 실전 자본 3층 — 관측 · 정책 · 통제 (dev 판).

동작을 바꾸는 3가지(SHINDONG_QTY_FROM_MARGIN_ENABLED · RISK_CAPITAL_DEPOSIT_CAP_ENABLED ·
PROFIT_GUARD_QTY_SCALE_ENABLED)는 [2026-10-23 사용자 지시] **켜짐** — v9-dev 와 같다.
이 테스트는 ① 운영값(켜짐) ② 끄면 종전과 같다(롤백 경로) ③ 켜진 규칙 ④ 배선 을 고정한다.
값을 바꾸면 ① 이 깨져 DECISION_LOG 기록을 강제한다.
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import config.capital as CAP          # noqa: E402
import config.settings as ST          # noqa: E402


def _src(rel):
    return io.open(os.path.join(ROOT, rel), encoding='utf-8').read()


def _func(src, name):
    i = src.index('def %s(' % name)
    j = src.find('\n    def ', i + 10)
    return src[i:j if j > 0 else None]


# ── ① 기본 꺼짐 = 종전 동작 ───────────────────────────────────────────
def test_behavior_flags_on():
    """[2026-10-23 사용자 지시] dev 도 v9-dev 와 같이 켠다."""
    assert ST.SHINDONG_QTY_FROM_MARGIN_ENABLED is True
    assert ST.RISK_CAPITAL_DEPOSIT_CAP_ENABLED is True
    assert ST.PROFIT_GUARD_QTY_SCALE_ENABLED is True


def test_risk_capital_unchanged_when_off(monkeypatch):
    """롤백 경로 — 끄면 예탁금을 보지 않는다(종전 동작)."""
    monkeypatch.setattr(CAP, "RISK_CAPITAL_DEPOSIT_CAP_ENABLED", False)
    base = CAP.sizing_capital(0)
    assert CAP.risk_capital(0, deposit_krw=base / 2) == base          # 꺼짐 — 예탁금 무시
    assert CAP.daily_loss_ratio(base * 0.02, 0, deposit_krw=base / 2) == 0.02 or \
        abs(CAP.daily_loss_ratio(base * 0.02, 0, deposit_krw=base / 2) - 0.02) < 1e-12


def test_risk_capital_capped_when_on(monkeypatch):
    monkeypatch.setattr(CAP, "RISK_CAPITAL_DEPOSIT_CAP_ENABLED", True)
    base = CAP.sizing_capital(0)
    assert CAP.risk_capital(0, deposit_krw=base / 2) == base / 2
    assert CAP.risk_capital(0, deposit_krw=base * 3) == base          # 위로는 정책값을 넘지 않는다
    assert CAP.risk_capital(0, deposit_krw=None) == base              # 미측정 → 정책값


# ── ② 켜면 v9-dev 와 같은 규칙 ─────────────────────────────────────────
def test_planned_and_entry_qty():
    P, E = CAP.shindong_planned_qty, CAP.shindong_entry_qty
    assert P(3, day_start_margin_qty=5, configured_qty=2) == 3
    assert P(3, day_start_margin_qty=2, configured_qty=3) == 2
    assert P(3, day_start_margin_qty=None, configured_qty=2) == 2
    assert P(3, day_start_margin_qty=0, configured_qty=3) == 0
    assert E(3, 2) == 2 and E(3, None) == 3 and E(3, 0) == 0
    assert [CAP.profit_guard_krw_scale(q) for q in (1, 2, 3, 4)] == [1.0, 1.0, 1.5, 2.0]


def test_capital_state_off_mode_shows_what_on_would_do():
    st = CAP.capital_state(policy_krw=15_000_000, deposit_krw=27_000_000, price=858.06, pt_value=50_000,
                           margin_qty=2, configured_qty=2, ui_max_qty=3, day_start_margin_qty=3,
                           qty_from_margin=False, deposit_cap=False)
    assert st['effective_qty'] == 2                                    # 꺼짐 — SHINDONG_LIVE_QTY 고정
    assert any('증거금 연동 꺼짐 — 켜면 2계약' in r for r in st['reasons'])
    assert st['risk_capital_krw'] == 15_000_000 and st['risk_capital_src'] == '정책'
    on = CAP.capital_state(policy_krw=15_000_000, deposit_krw=27_000_000, price=858.06, pt_value=50_000,
                           margin_qty=3, configured_qty=2, ui_max_qty=3, day_start_margin_qty=3)
    assert on['effective_qty'] == 3 and any('확대 2→3' in r for r in on['reasons'])
    zero = CAP.capital_state(policy_krw=15_000_000, deposit_krw=27_000_000, price=858.06, pt_value=50_000,
                             margin_qty=0, configured_qty=2, ui_max_qty=3, day_start_margin_qty=3)
    assert zero['level'] == 'BLOCK'
    line = CAP.format_capital_state(st)
    assert '[Capital]' in line and '장시작' in line


def test_profit_guard_scale_roundtrip_and_latch():
    from strategy.profit_guard import ProfitGuard
    pg = ProfitGuard()
    base = (pg.cfg.trail_activation_krw, list(pg.cfg.profit_tiers))
    assert pg.set_krw_scale(1.0) is False
    assert pg.set_krw_scale(1.5) is True and pg.cfg.trail_activation_krw == base[0] * 1.5
    pg.set_krw_scale(1.0)
    assert (pg.cfg.trail_activation_krw, list(pg.cfg.profit_tiers)) == base
    pg2 = ProfitGuard()
    ok, _ = pg2.is_entry_allowed(base[1][-1][0] + 100_000, None)
    assert not ok
    pg2.set_krw_scale(2.0)
    ok, _ = pg2.is_entry_allowed(base[1][-1][0] + 100_000, None)
    assert not ok                                                       # 배율이 래치를 풀지 않는다


# ── ③ 배선 ────────────────────────────────────────────────────────────
def test_entry_qty_gated_by_flag():
    src = _src('main.py')
    step = _func(src, '_shindong_exec_step')
    i_q = step.index('qty = self._shindong_live_qty()')
    i_f = step.index('if bool(getattr(runtime_settings, "SHINDONG_QTY_FROM_MARGIN_ENABLED", False)):', i_q)
    i_c = step.index('_capital_monitor_refresh(force_margin=True)', i_f)
    i_e = step.index('if qty <= 0:', i_c)
    i_x = step.index('self._execute_entry(', i_e)
    assert i_q < i_f < i_c < i_e < i_x
    helper = _func(src, '_shindong_live_qty')
    assert 'SHINDONG_QTY_FROM_MARGIN_ENABLED' in helper and 'return _cfg' in helper
    assert 'qty = max(1, self._shindong_live_qty())' in src             # 가상 집행 같은 수량
    sync = _func(src, '_pg_sync_scale')
    assert 'PROFIT_GUARD_QTY_SCALE_ENABLED' in sync
    for m in re.finditer(r'self\.profit_guard\.is_entry_allowed\(', src):
        assert 'self._pg_sync_scale()' in src[max(0, m.start() - 1500):m.start()]


def test_monitor_and_logs_on_order_tab():
    src = _src('main.py')
    assert 'self._capital_monitor_refresh(now)' in _func(src, '_scheduler_tick')
    assert src.count('deposit_krw=self._broker_dep_base_today)') == 3
    for name in ('_cap_day_start_qty', '_cap_day_start_record', '_capital_monitor_refresh'):
        body = _func(src, name)
        assert 'log_manager.system(' not in body and 'logger.info(' not in body, name
        assert 'log_manager.trade(' in body, name
    d = _src('dashboard/main_dashboard.py')
    assert d.count('def update_capital_monitor(') == 2 and 'self._capital_lbl = QLabel(' in d
    for a in ('self._cap_margin_qty = None', 'self._cap_margin_ts = 0.0', 'self._cap_last_key = None',
              'self._cap_day_start = None'):
        assert a in src
