# -*- coding: utf-8 -*-
"""[MW0601 707차 / 사용자 결정 2026-10-23] 실전 자본 3층 — 관측 · 정책 · 통제.

  정책  위험자본 = min(LIVE_OPERATING_CAPITAL_KRW, 당일 시가 예탁금). 미측정이면 정책값.
  통제  신동 실주문 = min(SHINDONG_LIVE_QTY, 진입관리탭 최대허용수량). 증거금 부족이면 기각.
  PG    원화 임계 배율 = max(1, 선택 주체 실주문 수량 ÷ PROFIT_GUARD_QTY_BASE).
  모니터 우측패널 「3 주문/체결」 탭 한 줄.
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


# ── A. 정책층 ──────────────────────────────────────────────────────────
def test_risk_capital_is_min_of_policy_and_deposit():
    pol = ST.LIVE_OPERATING_CAPITAL_KRW
    assert CAP.risk_capital(0, deposit_krw=None) == pol           # 미측정 → 정책값(종전 동작)
    assert CAP.risk_capital(0, deposit_krw=0) == pol              # 0 은 「0원」이 아니라 미측정
    assert CAP.risk_capital(0, deposit_krw=pol * 3) == pol        # 위로는 정책값을 넘지 않는다
    assert CAP.risk_capital(0, deposit_krw=pol / 2) == pol / 2    # 아래로는 따라 내려간다
    assert CAP.daily_loss_limit_krw(0, deposit_krw=pol / 2) == pol / 2 * ST.DAILY_LOSS_LIMIT_PCT
    assert abs(CAP.daily_loss_ratio(pol / 2 * 0.02, 0, deposit_krw=pol / 2) - 0.02) < 1e-12


def test_risk_max_qty_and_pg_scale():
    # 1,500만 × 15% ÷ 90만 = 2.5 → 2
    assert CAP.risk_max_qty(15_000_000) == 2
    assert CAP.risk_max_qty(0) is None
    assert [CAP.profit_guard_krw_scale(q) for q in (1, 2, 3, 4, 5)] == [1.0, 1.0, 1.5, 2.0, 2.5]
    assert CAP.profit_guard_krw_scale(0) == 1.0


def test_planned_and_entry_qty():
    """[707차 후속] 계획 = min(최대허용, 장시작 가능) · 진입 = min(계획, 지금 가능) · 0 이면 기각."""
    P, E = CAP.shindong_planned_qty, CAP.shindong_entry_qty
    assert P(3, day_start_margin_qty=5, configured_qty=2) == 3      # 충분하면 늘린다 — 최대허용까지
    assert P(3, day_start_margin_qty=2, configured_qty=3) == 2      # 부족하면 준다
    assert P(3, day_start_margin_qty=None, configured_qty=2) == 2   # 장시작 미측정 → SHINDONG_LIVE_QTY 폴백
    assert P(1, day_start_margin_qty=5, configured_qty=3) == 1      # 최대허용수량이 상한
    assert P(3, day_start_margin_qty=0, configured_qty=3) == 0      # 증거금 없음
    assert E(3, 2) == 2 and E(3, 5) == 3 and E(3, None) == 3 and E(3, 0) == 0


def test_capital_state_levels():
    kw = dict(policy_krw=34_000_000, deposit_krw=34_000_000, price=858.06, pt_value=50_000,
              configured_qty=3, ui_max_qty=3)
    ok = CAP.capital_state(margin_qty=3, day_start_margin_qty=3, **kw)
    assert ok['level'] == 'OK' and ok['planned_qty'] == 3 and ok['effective_qty'] == 3
    assert ok['risk_capital_krw'] == 34_000_000 and ok['risk_max_qty'] == 5
    shrink = CAP.capital_state(margin_qty=2, day_start_margin_qty=3, **kw)
    assert shrink['level'] == 'OK' and shrink['effective_qty'] == 2          # 줄여서 진입(기각 아님)
    assert any('축소 3→2' in r for r in shrink['reasons'])
    blk = CAP.capital_state(margin_qty=0, day_start_margin_qty=3, **kw)
    assert blk['level'] == 'BLOCK' and blk['effective_qty'] == 0
    grow = CAP.capital_state(margin_qty=5, day_start_margin_qty=5,
                             **dict(kw, configured_qty=2))
    assert grow['effective_qty'] == 3 and any('확대 2→3' in r for r in grow['reasons'])
    warn = CAP.capital_state(policy_krw=15_000_000, deposit_krw=15_000_000, price=858.06, pt_value=50_000,
                             margin_qty=3, day_start_margin_qty=3, configured_qty=3, ui_max_qty=3)
    assert warn['level'] == 'WARN' and warn['risk_max_qty'] == 2
    unk = CAP.capital_state(policy_krw=15_000_000, deposit_krw=None, price=None, pt_value=50_000,
                            margin_qty=None, configured_qty=2, ui_max_qty=2)
    assert unk['deposit_measured'] is False and unk['margin_qty'] is None
    assert unk['day_start_margin_qty'] is None and unk['effective_qty'] == 2
    line = CAP.format_capital_state(unk)
    assert '미측정' in line and '0만' not in line.split('위험자본')[0]   # 미측정을 0 으로 쓰지 않는다


def test_margin_estimate_is_reference_only():
    m1 = CAP.margin_per_contract_est(858.06, 50_000)
    assert abs(m1 - 858.06 * 50_000 * ST.FUTURES_MARGIN_RATE_INITIAL) < 1e-6
    st = CAP.capital_state(policy_krw=15_000_000, deposit_krw=34_000_000, price=858.06,
                           pt_value=50_000, margin_qty=None, configured_qty=2, ui_max_qty=2)
    assert st['margin_qty_est'] == 3 and st['margin_qty'] is None
    assert st['level'] != 'BLOCK'        # 추정치로는 막지 않는다 — 판정은 브로커 CpTd6722


# ── B. ProfitGuard 배율 ────────────────────────────────────────────────
def test_profit_guard_scale_roundtrip():
    from strategy.profit_guard import ProfitGuard
    pg = ProfitGuard()
    base_trail = pg.cfg.trail_activation_krw
    base_tiers = list(pg.cfg.profit_tiers)
    base_ratio, base_n = pg.cfg.trail_ratio, pg.cfg.afternoon_max_trades
    assert pg.set_krw_scale(1.0) is False                         # 2계약 이하 — 종전과 같다
    assert pg.set_krw_scale(1.5) is True
    assert pg.cfg.trail_activation_krw == base_trail * 1.5
    assert [t[0] for t in pg.cfg.profit_tiers] == [t[0] * 1.5 for t in base_tiers]
    assert [t[1:] for t in pg.cfg.profit_tiers] == [t[1:] for t in base_tiers]
    assert pg.cfg.trail_ratio == base_ratio and pg.cfg.afternoon_max_trades == base_n
    # 4,000,000 은 ×1.5 에서 중단 아님, 6,000,000 에서 중단
    ok, _ = pg.is_entry_allowed(4_100_000, None)
    assert ok
    pg.set_krw_scale(1.0)
    assert pg.cfg.trail_activation_krw == base_trail and list(pg.cfg.profit_tiers) == base_tiers


def test_profit_guard_scale_keeps_latch():
    from strategy.profit_guard import ProfitGuard
    pg = ProfitGuard()
    ok, _ = pg.is_entry_allowed(4_100_000, None)                  # ×1 → L2 Tier4 래치
    assert not ok
    pg.set_krw_scale(2.0)
    ok, _ = pg.is_entry_allowed(4_100_000, None)
    assert not ok                                                  # 배율이 래치를 풀지 않는다


# ── C. main 배선 ──────────────────────────────────────────────────────
def test_shindong_entry_qty_follows_margin():
    src = _src('main.py')
    step = _func(src, '_shindong_exec_step')
    i_cap = step.index('_capital_monitor_refresh(force_margin=True)')
    i_qty = step.index('qty = _capital_sd_entry_qty(_planned, _cap["margin_qty"])')
    i_rej = step.index('if qty <= 0:')
    i_exe = step.index('self._execute_entry(')
    assert i_cap < i_qty < i_rej < i_exe                               # 조회 → 수량 → 0 기각 → 주문
    helper = _func(src, '_shindong_live_qty')
    assert '_capital_sd_planned_qty(' in helper and 'self._max_entry_qty' in helper
    assert '_cap_day_start_qty(' in helper and 'SHINDONG_LIVE_QTY' in helper
    # 장시작 값은 파일로 승계(재기동 생존) · 덮어쓰지 않음
    rec = _func(src, '_cap_day_start_record')
    assert 'principal_mod.write_json(' in rec
    assert rec.index('if self._cap_day_start_qty(day) is not None:') < rec.index('principal_mod.write_json(')
    assert 'principal_mod.read_json(' in _func(src, '_cap_day_start_qty')
    # 가상 집행·재기동 복원도 같은 계획 수량
    assert 'qty = max(1, self._shindong_live_qty())' in src
    assert 'rec["leg1_done"] = int(pos.quantity or 0) < self._shindong_live_qty()' in src


def test_pg_scale_synced_before_every_entry_judgement():
    src = _src('main.py')
    for m in re.finditer(r'self\.profit_guard\.is_entry_allowed\(', src):
        head = src[max(0, m.start() - 1500):m.start()]
        assert 'self._pg_sync_scale()' in head, src[m.start() - 200:m.start()]


def test_daily_loss_ratio_and_alert_use_deposit():
    src = _src('main.py')
    assert src.count('deposit_krw=self._broker_dep_base_today)') == 3
    assert 'cap = min(cap, float(self._broker_dep_base_today))' in src


def test_logs_unified_to_trade_layer():
    """[사용자 지시 2026-10-23] 신동 수량·증거금·잔고 로그는 「3 주문/체결」 탭(TRADE 계층)으로 일원화."""
    src = _src('main.py')
    for name in ('_cap_day_start_qty', '_cap_day_start_record', '_capital_monitor_refresh'):
        body = _func(src, name)
        assert 'log_manager.system(' not in body and 'logger.info(' not in body \
            and 'logger.warning(' not in body, name
        assert 'log_manager.trade(' in body, name
    step = _func(src, '_shindong_exec_step')
    for tag in ('증거금 기준 축소', '주문가능수량 미측정 — 계획 수량', '자본 모니터 계산 실패'):
        i = step.index(tag)
        assert 'log_manager.trade(' in step[max(0, i - 120):i], tag
    i = step.index('_why = "margin(가능 %s · 계획 %d)"')
    assert 'log_manager.trade(' in step[i:i + 200]
    for m in re.finditer(r'원화 임계 배율 동기화 실패', src):
        assert 'log_manager.trade(' in src[max(0, m.start() - 80):m.start()]
    tick = _func(src, '_scheduler_tick')
    i = tick.index('[Capital] 모니터 갱신 실패')
    assert 'log_manager.trade(' in tick[max(0, i - 80):i]
    pg = _src('strategy/profit_guard.py')
    body = pg[pg.index('def set_krw_scale('):pg.index('def is_entry_allowed(')]
    assert 'log_manager.trade(' in body and 'log_manager.system(' not in body


def test_monitor_wired_to_scheduler_and_order_tab():
    src = _src('main.py')
    tick = _func(src, '_scheduler_tick')
    assert 'self._capital_monitor_refresh(now)' in tick
    d = _src('dashboard/main_dashboard.py')
    assert d.count('def update_capital_monitor(') == 2              # 로그 패널 + 어댑터
    assert 'self._capital_lbl = QLabel(' in d
    for a in ('self._cap_margin_qty = None', 'self._cap_margin_ts = 0.0', 'self._cap_last_key = None',
              'self._cap_day_start = None'):
        assert a in src                                            # __init__ 명시 초기화(계측 4원칙 ④)
