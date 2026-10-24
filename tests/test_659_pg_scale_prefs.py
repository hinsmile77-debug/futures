# -*- coding: utf-8 -*-
"""[MW0602 659차] ProfitGuard 원화 임계 배율 × 사용자 임계(prefs) × 신동 V4 ATR 연동 수량.

결함(2026-10-23 08:45 실측): `update_config()` 가 배율 원본(`_krw_base`)을 갱신하지 않아, 배율이 바뀌는 순간
사용자 임계가 「기본값 × 배율」로 덮어써졌다(L1 300만 · L3 150만 · L4 225만 · 중간 등급 경계 부활).
V4 는 ATR 연동 수량으로 장전 ×1.5 → ATR 확정 뒤 ×1.0 전환이 매일 생긴다.

지키는 불변식
  ① 배율은 언제나 **사용자 임계(update_config 로 받은 값)** 에서 다시 계산한다 — ×1.0 으로 돌아오면 prefs 그대로
  ② 횟수·비율(오후 최대 건수 · L4 연패 · L1 비율)은 배율과 무관하다
  ③ update_config 는 받은 객체를 바꾸지 않는다(패널이 그 객체를 곧바로 prefs 파일에 저장한다 — 누적 방지)
  ④ 배율이 걸린 상태에서 설정이 바뀌면 새 설정에 지금 배율이 다시 걸린다
  ⑤ 연쇄: ATR → X% 수량 → 계획 수량 → 배율. ATR > 35 → 1계약 → ×1.0 · ATR ≤ 23.3 → 3계약 → ×1.5
"""
import copy
import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

from config import capital as CAP  # noqa: E402
from strategy.profit_guard import ProfitGuard, ProfitGuardConfig  # noqa: E402


def _prefs_645():
    """data/profit_guard_prefs.json(645차 사용자 결정) 과 같은 값 — 기본값과 일부러 다르다."""
    c = ProfitGuardConfig()
    c.trail_activation_krw = 1_500_000
    c.trail_ratio = 0.35
    c.profit_tiers = [(0, 0.6, None), (4_000_000, 0.6, None), (4_000_000, 1.0, None),
                      (4_000_000, 1.2, None), (4_000_000, 1.5, 0)]
    c.afternoon_min_pnl_krw = 2_000_000
    c.afternoon_max_trades = 2
    c.profit_cb_min_pnl_krw = 1_000_000
    c.profit_cb_consec_loss = 3
    return c


def _krw(pg):
    c = pg.cfg
    return (c.trail_activation_krw, [t[0] for t in c.profit_tiers], c.afternoon_min_pnl_krw, c.profit_cb_min_pnl_krw)


def test_scale_uses_user_prefs_not_defaults():
    pg = ProfitGuard()
    pg.update_config(_prefs_645())
    assert pg.set_krw_scale(1.5, why="신동 3계약") is True
    assert _krw(pg) == (2_250_000, [0, 6_000_000, 6_000_000, 6_000_000, 6_000_000], 3_000_000, 1_500_000)
    # ② 횟수·비율은 그대로
    assert (pg.cfg.afternoon_max_trades, pg.cfg.profit_cb_consec_loss, pg.cfg.trail_ratio) == (2, 3, 0.35)
    # ① ×1.0 복귀 = prefs 그대로(기본값 200만·100만·150만·100/200/300만 경계가 되살아나면 안 된다)
    pg.set_krw_scale(1.0)
    assert _krw(pg) == (1_500_000, [0, 4_000_000, 4_000_000, 4_000_000, 4_000_000], 2_000_000, 1_000_000)


def test_update_config_does_not_mutate_caller_and_reapplies_scale():
    pg = ProfitGuard()
    pg.update_config(_prefs_645())
    pg.set_krw_scale(1.5)
    new = _prefs_645()
    new.trail_activation_krw = 1_800_000
    snap = copy.deepcopy(new.__dict__)
    pg.update_config(new)
    assert new.__dict__ == snap                              # ③ 패널이 저장할 객체는 배율 1 그대로
    assert pg.krw_scale == 1.5 and pg.cfg.trail_activation_krw == 2_700_000   # ④ 새 원본 × 지금 배율
    pg.set_krw_scale(1.0)
    assert pg.cfg.trail_activation_krw == 1_800_000


def test_atr_qty_scale_chain():
    """⑤ 신동 계획 수량(최대허용 3 · 장시작 가능 3 · 폴백 2) × X% → PG 배율."""
    def scale(atr):
        q = CAP.shindong_planned_qty(3, 3, 2, CAP.shindong_risk_qty(atr))
        return q, CAP.profit_guard_krw_scale(q)
    assert scale(45.7) == (1, 1.0)
    assert scale(34.2) == (2, 1.0)
    assert scale(23.0) == (3, 1.5)
    assert scale(None) == (3, 1.5)          # ATR 미확보(재생 전) — 증거금 수량 그대로. 진입은 엔진이 막는다


def test_principal_qty_feeds_scale_through_shindong_live_qty():
    import main
    src = inspect.getsource(main.TradingSystem._principal_live_qty)
    assert "self._shindong_live_qty()" in src
    sync = inspect.getsource(main.TradingSystem._pg_sync_scale)
    assert "_capital_pg_scale(_q)" in sync and "self._principal_live_qty(_p)" in sync
    gate = inspect.getsource(main.TradingSystem._pg_principal_entry_block)
    assert "self._pg_sync_scale()" in gate                   # 신동 진입 직전에도 배율을 맞춘다
