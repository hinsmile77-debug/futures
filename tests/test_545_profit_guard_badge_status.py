# -*- coding: utf-8 -*-
"""[MW0601 545차] ProfitGuard 배지 상태 API 회귀 가드.

계기 — 2026-09-08. `_TierGate`에만 `is_halted`가 없어
`ProfitGuard.get_l2_halt_info()`·`status_dict()`가 **작성된 날(28차 `47721d6`,
2026-05-14)부터 호출될 때마다 AttributeError로 죽었다.** 호출부가
`logger.debug`(main.py)·`except: pass`(dashboard)로 삼켜 어떤 로그파일에도
남지 않았고, L2 배지는 약 4개월간 초기 텍스트 "L2 —"(=정상)에 굳어 있었다.
그날 09:21 Tier4가 실제로 래치돼 시스템 진입이 0건이 된 순간에도 화면은
정상을 표시했다 — 계측 4원칙 ④(폴백이 정상값처럼 보인다)의 UI판이다.

고정하는 사실:
① 게이트 4종의 `is_halted` **인터페이스가 일치**한다(하나만 빠지면 즉시 실패).
② `get_l2_halt_info()`·`status_dict()`가 인자 유무와 무관하게 예외 없이 dict.
③ `guard_status()`가 L1~L4를 모두 싣고, **구속 레이어**를
   `is_entry_allowed()`와 **같은 우선순위**(L1→L2→L3→L4)로 고른다.
④ `guard_status()`는 **읽기 전용**이다 — 조회가 래치를 만들지 않는다.
   (래치는 매분 `is_entry_allowed()`가 만드는 것이 유일한 경로여야 한다.)
⑤ **미측정과 0을 구분**한다 — `daily_pnl_krw=None`이면 `measured=False`이고
   숫자를 지어내지 않는다(계측 4원칙 ②).
⑥ 2026-09-08 실제 운영값(전 티어 500,000원) 재현 — 그날의 래치가 재현된다.
"""
import datetime
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategy.profit_guard import (  # noqa: E402
    ProfitGuard, ProfitGuardConfig, _TierGate, _TrailingGuard, _ProfitCB,
)

# 2026-09-08 MW0601 라이브 운영값(data/profit_guard_prefs.json 실측).
# 5단계가 **전부 500,000원**이라 50만원을 넘는 순간 Tier4(중단)로 직행한다.
LIVE_0908_TIERS = [
    (0, 0.6, None),
    (500_000, 0.6, None),
    (500_000, 1.0, None),
    (500_000, 1.2, None),
    (500_000, 1.5, 0),
]


def _guard(**cfg_kw):
    cfg = ProfitGuardConfig()
    for k, v in cfg_kw.items():
        setattr(cfg, k, v)
    return ProfitGuard(cfg)


# ── ① 인터페이스 일치 ───────────────────────────────────────────────
@pytest.mark.parametrize("cls", [_TierGate, _TrailingGuard, _ProfitCB])
def test_all_gates_expose_is_halted(cls):
    """게이트 3종 모두 `is_halted`를 노출한다.

    `_TierGate`만 빠져 있었던 것이 2026-09-08 결함의 전부다.
    """
    inst = cls()
    assert hasattr(inst, "is_halted"), "%s 에 is_halted 없음" % cls.__name__
    assert inst.is_halted is False


def test_tier_gate_is_halted_tracks_latch():
    g = _TierGate()
    cfg = ProfitGuardConfig()
    cfg.profit_tiers = LIVE_0908_TIERS
    assert g.is_halted is False
    blocked, tier, _reason = g.check(513_967, 1.0, cfg)
    assert blocked and tier == 4
    assert g.is_halted is True
    assert g.halt_threshold == 500_000
    g.reset()
    assert g.is_halted is False


# ── ② 구 API 무예외 ─────────────────────────────────────────────────
def test_legacy_apis_do_not_raise():
    g = _guard(profit_tiers=LIVE_0908_TIERS)
    for info in (g.get_l2_halt_info(), g.get_l2_halt_info(0.0)):
        assert set(info) == {"is_halted", "halt_threshold", "halt_tier"}
        assert info["is_halted"] is False
    st = g.status_dict(0.0)
    assert st["tier_halted"] is False
    assert st["trail_halted"] is False
    assert st["pcb_halted"] is False


# ── ③ 구속 레이어 우선순위 ─────────────────────────────────────────
def test_binding_layer_matches_is_entry_allowed_order():
    """L1과 L2가 동시에 래치돼 있으면 `is_entry_allowed`는 L1을 돌려준다.

    배지의 구속 표기도 같은 순서여야 화면과 로그가 어긋나지 않는다.
    2026-09-08이 정확히 이 상태였다 — 09:21 L2 래치 → 09:40 L1 래치.
    """
    g = _guard(profit_tiers=LIVE_0908_TIERS,
               trail_activation_krw=300_000, trail_ratio=0.10)
    now = datetime.datetime(2026, 9, 8, 9, 21)
    # 09:21 — L2 Tier4 래치
    ok, why = g.is_entry_allowed(513_967, 1.0, now, pnl_source="broker_net_est")
    assert not ok and why.startswith("[L2-Tier4]")
    st = g.guard_status(513_967, 1.0, now)
    assert st["halted"] is True
    assert st["halt_layer"] == "L2" and st["halt_label"] == "L2-Tier4"
    assert st["layers"]["L2"]["state"] == "halt"

    # 09:40 — 피크에서 10% 하락 → L1 도 래치. 이후 구속 표기는 L1 로 넘어간다.
    g._trail.peak_pnl = 684_928
    ok, why = g.is_entry_allowed(524_940, 1.0,
                                 datetime.datetime(2026, 9, 8, 9, 40),
                                 pnl_source="broker_net_est")
    assert not ok and why.startswith("[L1-Trail]")
    st = g.guard_status(524_940, 1.0, datetime.datetime(2026, 9, 8, 9, 40))
    assert st["halt_layer"] == "L1" and st["halt_label"] == "L1-Trail"
    assert st["layers"]["L1"]["state"] == "halt"
    assert st["layers"]["L2"]["state"] == "halt"   # L2 래치도 계속 보인다


def test_l4_binding_when_only_pcb_halted():
    g = _guard(profit_cb_min_pnl_krw=300_000, profit_cb_consec_loss=2)
    now = datetime.datetime(2026, 9, 8, 10, 0)
    g.on_trade_close(-50_000, 400_000)
    g.on_trade_close(-50_000, 400_000)
    st = g.guard_status(400_000, 1.0, now)
    assert st["halted"] is True
    assert st["halt_layer"] == "L4" and st["halt_label"] == "L4-ProfitCB"
    assert st["layers"]["L4"]["state"] == "halt"


def test_l3_is_block_not_halt():
    """L3는 래치가 아니다 — `blocking`이지 `halted`가 아니다.

    래치(회복 불가)와 조건부 차단을 같은 색으로 그리면 운영자가
    "다음 분에 풀릴 수 있는가"를 화면에서 판단할 수 없다.
    """
    g = _guard(afternoon_enabled=True, afternoon_cutoff_hour=13,
               afternoon_min_pnl_krw=300_000, afternoon_max_trades=2)
    g._arisk._afternoon_count = 2
    st = g.guard_status(400_000, 1.0, datetime.datetime(2026, 9, 8, 13, 30))
    assert st["blocking"] is True
    assert st["halted"] is False
    assert st["halt_layer"] == "L3"
    assert st["layers"]["L3"]["state"] == "block"


# ── ④ 읽기 전용 ────────────────────────────────────────────────────
def test_guard_status_never_latches():
    """조회가 래치를 만들면 "누가 언제 멈췄나"의 출처가 흐려진다."""
    g = _guard(profit_tiers=LIVE_0908_TIERS,
               trail_activation_krw=300_000, trail_ratio=0.10)
    before = g.to_state_dict()
    for _ in range(3):
        g.guard_status(9_999_999, 0.1, datetime.datetime(2026, 9, 8, 14, 0))
    assert g.to_state_dict() == before
    assert g._tier.is_halted is False
    assert g._trail.is_halted is False


# ── ⑤ 미측정 ≠ 0 ───────────────────────────────────────────────────
def test_unmeasured_is_not_zero():
    g = _guard(profit_tiers=LIVE_0908_TIERS)
    st = g.guard_status(None, None, datetime.datetime(2026, 9, 8, 14, 0))
    assert st["measured"] is False
    assert st["daily_pnl_krw"] is None
    assert st["tier"] is None
    assert st["layers"]["L2"]["state"] == "unmeasured"
    assert st["layers"]["L3"]["state"] == "unmeasured"
    # 미측정이라고 해서 "차단 중"으로 위장하지 않는다.
    assert st["halted"] is False and st["blocking"] is False


def test_pnl_source_token_is_carried():
    """차단 판정에 쓴 손익 원천이 배지까지 전달된다(계측 4원칙 ①)."""
    g = _guard(profit_tiers=LIVE_0908_TIERS)
    g.is_entry_allowed(0.0, 1.0, datetime.datetime(2026, 9, 8, 10, 0),
                       pnl_source="broker_net_est")
    assert g.guard_status(0.0, 1.0)["pnl_source"] == "broker_net_est"
    # 호출부가 안 주면 None(미측정) — 임의 기본값으로 채우지 않는다.
    g2 = _guard()
    assert g2.guard_status(0.0, 1.0)["pnl_source"] is None


# ── ⑥ 모든 레이어 키가 항상 존재 ───────────────────────────────────
def test_all_four_layers_always_present():
    g = _guard()
    for args in ((None, None), (0.0, 1.0), (5_000_000, 0.1)):
        st = g.guard_status(args[0], args[1], datetime.datetime(2026, 9, 8, 14, 0))
        assert set(st["layers"]) == {"L1", "L2", "L3", "L4"}
        for k, d in st["layers"].items():
            assert d["name"] == k
            assert d["title"]
            assert d["state"] in ("idle", "armed", "block", "halt", "unmeasured")
            assert d["detail"]


def test_reset_daily_clears_all_layers():
    g = _guard(profit_tiers=LIVE_0908_TIERS,
               trail_activation_krw=300_000, trail_ratio=0.10)
    g.is_entry_allowed(513_967, 1.0, datetime.datetime(2026, 9, 8, 9, 21))
    assert g.guard_status(513_967, 1.0)["halted"] is True
    g.reset_daily()
    st = g.guard_status(0.0, 1.0, datetime.datetime(2026, 9, 9, 9, 5))
    assert st["halted"] is False and st["blocking"] is False
    assert all(d["state"] == "idle" for d in st["layers"].values())


# ── ⑦ 배지 렌더러 (Qt 위젯 없이 가짜 라벨로 로직만 검증) ──────────
#
# QApplication 없이 클래스의 메서드만 빌려 쓴다. 실제 화면을 띄우지 않으므로
# CI/헤드리스에서도 돈다. 여기서 고정하는 것은 **색과 깜빡임의 의미**다 —
# 종전 배지의 결함이 "정상"과 "갱신 실패"가 같은 회색이었다는 점이므로,
# 그 구분이 회귀하면 즉시 깨져야 한다.
_dash = pytest.importorskip("dashboard.main_dashboard")


class _FakeLbl(object):
    def __init__(self):
        self.text = ""
        self.css = ""
        self.tip = ""

    def setText(self, t):
        self.text = t

    def setStyleSheet(self, c):
        self.css = c

    def setToolTip(self, t):
        self.tip = t


class _StubWin(object):
    _M = _dash.MireukDashboard
    _PG_STATE_STYLE = _M._PG_STATE_STYLE
    _PG_STATE_MARK = _M._PG_STATE_MARK
    _PG_RANK = _M._PG_RANK
    _PG_SRC_LABEL = _M._PG_SRC_LABEL   # [546차] 손익 원천 라벨
    render_profit_guard = _M.render_profit_guard
    _pg_tooltip = _M._pg_tooltip
    _apply_pg_main_style = _M._apply_pg_main_style
    _apply_pg_chip_style = _M._apply_pg_chip_style
    _blink_profit_guard = _M._blink_profit_guard

    def __init__(self):
        self.lbl_l2_halt = _FakeLbl()
        self._pg_box = _FakeLbl()
        self.lbl_pg_layers = dict((k, _FakeLbl()) for k in ("L1", "L2", "L3", "L4"))
        self._pg_blink_on = True
        self._pg_blink_active = False
        self._pg_blink_chip = ""
        self._pg_color = _dash.C['bg3']
        self._pg_fg = _dash.C['text2']
        self._pg_chip_color = _dash.C['bg3']


def _bg(css):
    import re
    m = re.search(r"background:(#[0-9A-Fa-f]{6})", css)
    return m.group(1) if m else ""


def test_render_normal_is_not_blinking():
    w = _StubWin()
    g = _guard(profit_tiers=LIVE_0908_TIERS)
    w.render_profit_guard(g.guard_status(120_000, 1.0, datetime.datetime(2026, 9, 8, 10, 0)))
    assert "정상" in w.lbl_l2_halt.text
    assert "+120,000원" in w.lbl_l2_halt.text
    assert w._pg_blink_active is False
    for k in ("L1", "L2", "L3", "L4"):
        assert _bg(w.lbl_pg_layers[k].css) == _dash.C['bg3']


def test_render_latch_blinks_and_names_the_cause():
    """2026-09-08 09:21 재현 — 얼마 벌어서 · 무엇 때문에 멈췄는지가 라벨에 있다."""
    w = _StubWin()
    g = _guard(profit_tiers=LIVE_0908_TIERS,
               trail_activation_krw=300_000, trail_ratio=0.10)
    now = datetime.datetime(2026, 9, 8, 9, 21)
    g.is_entry_allowed(513_967, 1.0, now, pnl_source="broker_net_est")
    w.render_profit_guard(g.guard_status(513_967, 1.0, now))
    assert "L2-Tier4" in w.lbl_l2_halt.text
    assert "513,967원" in w.lbl_l2_halt.text
    assert _bg(w.lbl_l2_halt.css) == _dash.C['red']
    assert w._pg_blink_active is True and w._pg_blink_chip == "L2"
    assert _bg(w.lbl_pg_layers["L2"].css) == _dash.C['red']
    # 툴팁에 달성률과 해제 조건이 있다.
    assert "달성률 102.8%" in w._pg_box.tip
    assert "reset_daily" in w._pg_box.tip
    # 깜빡임 위상 토글이 실제로 색을 바꾼다.
    w._blink_profit_guard()
    assert _bg(w.lbl_l2_halt.css) != _dash.C['red']
    w._blink_profit_guard()
    assert _bg(w.lbl_l2_halt.css) == _dash.C['red']


def test_render_block_does_not_blink():
    """L3는 조건부 차단 — 색은 주황이되 깜빡이지 않는다(상시 깜빡임 금지)."""
    w = _StubWin()
    g = _guard(afternoon_enabled=True, afternoon_cutoff_hour=13,
               afternoon_min_pnl_krw=300_000, afternoon_max_trades=2)
    g._arisk._afternoon_count = 2
    w.render_profit_guard(g.guard_status(400_000, 1.0, datetime.datetime(2026, 9, 8, 13, 30)))
    assert "L3-Afternoon" in w.lbl_l2_halt.text
    assert _bg(w.lbl_l2_halt.css) == _dash.C['orange']
    assert w._pg_blink_active is False


def test_render_failure_is_visually_distinct_from_normal():
    """🔴 이 사건의 핵심 — '정상'과 '갱신 실패'가 같은 픽셀이면 안 된다."""
    ok = _StubWin()
    ok.render_profit_guard(_guard().guard_status(0.0, 1.0, datetime.datetime(2026, 9, 8, 10, 0)))
    bad = _StubWin()
    bad.render_profit_guard(None)
    assert ok.lbl_l2_halt.text != bad.lbl_l2_halt.text
    assert _bg(ok.lbl_l2_halt.css) != _bg(bad.lbl_l2_halt.css)
    assert "갱신실패" in bad.lbl_l2_halt.text
    assert bad._pg_blink_active is True          # 침묵하지 않는다
    assert ok._pg_blink_active is False


def test_render_unmeasured_does_not_claim_allowed():
    w = _StubWin()
    w.render_profit_guard(_guard().guard_status(None, None,
                                                datetime.datetime(2026, 9, 8, 10, 0)))
    assert "미측정" in w.lbl_l2_halt.text
    assert "진입 허용" not in w._pg_box.tip


def test_legacy_shim_still_renders():
    """구 API로 호출해도 예외 없이 그려지고, 모르는 레이어는 미측정으로 남는다."""
    class _Ad(object):
        update_profit_guard_badge = _dash.DashboardAdapter.update_profit_guard_badge
        update_l2_halt_badge = _dash.DashboardAdapter.update_l2_halt_badge

        def __init__(self, win):
            self._win = win

    w = _StubWin()
    ad = _Ad(w)
    ad.update_l2_halt_badge(True, 4_000_000)
    assert "L2-Tier" in w.lbl_l2_halt.text
    assert w._pg_blink_active is True
    assert "미측정" in w._pg_box.tip
