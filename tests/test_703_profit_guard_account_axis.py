# -*- coding: utf-8 -*-
"""[MW0601 703차 / F-701-A · MW0602 이식] ProfitGuard 계좌 축(주체 3종 실현 net 합) — 회귀 가드.

[MW0602 이식] v9-dev `87ee17c` 원본에서 dev 차이만 고쳤다:
  · dev 에는 556차 G-4 레그 원장(`_sys_daily_legs_detail`·`system_leg_details`)이 없다 →
    E 의 포지션 net 원천은 `_pg_pos_net_by_ets`(entry_ts → 판정 축 레그 net 합).
  · H 의 레그 원장 복원 단언 → `_pg_pos_net_by_ets` 복원 단언.

계기 — 2026-10-21 신동이 실거래 주체가 된 첫날, 신동 포지션 2연패(11:33 −196,412 ·
11:38 −81,408원)로 11:38:57 `L4-ProfitCB` 가 발동했는데 **신동은 그 뒤 5포지션을 더
거래했다.** 원인 두 가지:
  ① 신동·피터2 실거래 관문에 ProfitGuard 호출이 없었다.
  ② 판정(L1–L3)은 SYSTEM_AUTO 한정 누적기, L4 카운터는 계좌 전체 포지션 손익 — 축 불일치.
사용자 결정(2026-10-22): 「계좌 전체 = 주체 3종의 실현 net 합」.

고정하는 사실:
  A. 판정 축 화이트리스트 = 거래주체 3종(trade_principal.SOURCE_PRINCIPAL 키와 같은 집합).
     수동·복구·유령은 **여전히 제외**(546차 유지). 시스템 성과 축(SYSTEM_SOURCES)은 무변경.
  B. `size_mult=None`(등급 없는 주체)은 L2 최소배수·L3 품질 요건을 생략한다 — 금액·횟수·
     연패 조건은 그대로 건다.
  C. L1 피크는 청산 시점(`on_trade_close`)에도 갱신된다.
  D. 신동·피터2 관문이 같은 인스턴스·같은 축으로 막힌다(10-21 재현).
  E. L4 카운터는 판정 축 출처만, **포지션 단위 실현 net**(같은 entry_ts 레그 합)으로 센다.
  F. L3 오후 진입 횟수가 실제로 센다(703차 전엔 on_entry 호출부 0곳 — 죽은 카운터).
  G. 미륵이 가상 주체면 계좌 래치가 미륵 가상 진입을 막지 않는다(기본값).
  H. 세션 복원이 같은 화이트리스트로 누적기를 되살린다.
  I. 703차 결정 임계값으로 10-21 실거래 흐름이 끊기지 않는다(현행값은 10:12 에 끊긴다).
"""
import datetime
import inspect
import os
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

import main  # noqa: E402
import config.settings as S  # noqa: E402
from strategy.profit_guard import ProfitGuard, ProfitGuardConfig, _PNL_SRC_LABEL  # noqa: E402
from strategy.runtime import trade_principal as P  # noqa: E402
from utils.db_utils import sum_today_system_net_krw  # noqa: E402


# ── 설정값: 2026-10-22 이전 운영값 / 703차 결정값 ────────────────────────────
def _cfg_pre703():
    c = ProfitGuardConfig()
    c.trail_activation_krw, c.trail_ratio = 300_000, 0.10
    c.profit_tiers = [(0, 0.6, None), (500_000, 0.6, None), (500_000, 1.0, None),
                      (500_000, 1.2, None), (500_000, 1.5, 0)]
    c.afternoon_cutoff_hour, c.afternoon_min_pnl_krw, c.afternoon_max_trades = 13, 300_000, 2
    c.profit_cb_min_pnl_krw, c.profit_cb_consec_loss = 300_000, 2
    return c


def _cfg_703():
    c = ProfitGuardConfig()
    c.trail_activation_krw, c.trail_ratio = 1_500_000, 0.35
    c.profit_tiers = [(0, 0.6, None), (4_000_000, 0.6, None), (4_000_000, 1.0, None),
                      (4_000_000, 1.2, None), (4_000_000, 1.5, 0)]
    c.afternoon_cutoff_hour, c.afternoon_min_pnl_krw, c.afternoon_max_trades = 13, 2_000_000, 2
    c.profit_cb_min_pnl_krw, c.profit_cb_consec_loss = 1_000_000, 3
    return c


T = lambda h, m: datetime.datetime(2026, 10, 21, h, m)  # noqa: E731


# ── A. 화이트리스트 ─────────────────────────────────────────────────────────
def test_A_judge_sources_are_the_three_principals():
    assert S.PROFIT_GUARD_ACCOUNT_AXIS is True
    assert set(S.PROFIT_GUARD_ACCOUNT_SOURCES) == set(P.SOURCE_PRINCIPAL), \
        "판정 축 = 거래주체 3종. 주체가 늘면 여기와 trade_principal 을 같이 고칠 것"
    assert tuple(S.PROFIT_GUARD_JUDGE_SOURCES) == tuple(S.PROFIT_GUARD_ACCOUNT_SOURCES)
    for bad in ("OPERATOR_MANUAL", "GHOST_PENDING_MISS", "BROKER_SYNC_RECOVERY",
                "OPERATOR_RESTORE", "PHANTOM_STATE_ARTIFACT", None):
        assert bad not in S.PROFIT_GUARD_JUDGE_SOURCES, bad
    # 시스템 성과 축은 손대지 않는다(손익 추이 패널·db_utils 기본값이 같이 쓴다)
    assert tuple(S.PROFIT_GUARD_SYSTEM_SOURCES) == ("SYSTEM_AUTO",)
    assert S.PROFIT_GUARD_BLOCK_VIRTUAL_PRINCIPAL is False
    assert "account_principals" in _PNL_SRC_LABEL


def test_A_aggregator_with_judge_sources():
    rows = [{"entry_source": "SYSTEM_AUTO", "pnl_krw": 100_000},
            {"entry_source": "SHINDONG", "pnl_krw": 1_038_595},
            {"entry_source": "PETER2", "pnl_krw": -50_000},
            {"entry_source": "OPERATOR_MANUAL", "pnl_krw": 513_967},
            {"entry_source": None, "pnl_krw": 7}]
    r = sum_today_system_net_krw(rows, sources=S.PROFIT_GUARD_JUDGE_SOURCES)
    assert r["net_krw"] == 1_088_595 and r["legs"] == 3
    assert r["other_net_krw"] == 513_974 and r["other_legs"] == 2 and r["unknown_legs"] == 1


# ── B. 등급 없는 주체 ───────────────────────────────────────────────────────
def test_B_none_size_mult_skips_quality_only():
    c = ProfitGuardConfig()          # 코드 기본값: Tier1 100만 → min 1.0, Tier2 200만 → 1.2 …
    g = ProfitGuard(c)
    ok, why = g.is_entry_allowed(2_500_000, 1.0, T(10, 0))
    assert not ok and "L2" in why, "미륵 1.0 은 Tier2(1.2) 품질 요건에 막힌다"
    g = ProfitGuard(c)
    ok, why = g.is_entry_allowed(2_500_000, None, T(10, 0))
    assert ok, "등급 없는 주체는 품질 요건을 생략한다: %s" % why
    g = ProfitGuard(c)
    ok, why = g.is_entry_allowed(4_100_000, None, T(10, 0))
    assert not ok and "L2-Tier4" in why, "금액 중단 래치는 그대로 걸린다"


def test_B_none_size_mult_l3_count_still_applies():
    c = _cfg_703()
    g = ProfitGuard(c)
    ok, _ = g.is_entry_allowed(2_100_000, 1.0, T(13, 30))
    assert not ok, "미륵 1.0 < 1.25 는 오후 품질 요건에 막힌다(종전 동작)"
    g = ProfitGuard(c)
    assert g.is_entry_allowed(2_100_000, None, T(13, 30))[0]
    g.on_entry(T(13, 30))
    assert g.is_entry_allowed(2_100_000, None, T(13, 45))[0]
    g.on_entry(T(13, 45))
    ok, why = g.is_entry_allowed(2_100_000, None, T(14, 0))
    assert not ok and "L3" in why and "2/2" in why


# ── C. L1 피크의 청산 시점 갱신 ─────────────────────────────────────────────
def test_C_trail_peak_updated_on_close():
    g = ProfitGuard(_cfg_703())
    g.on_trade_close(+2_000_000, 2_000_000)      # 피크 200만 (그 사이 진입 판정 없음)
    g.on_trade_close(-800_000, 1_200_000)        # 200만 × 0.65 = 130만 아래 → 래치
    ok, why = g.is_entry_allowed(1_200_000, None, T(11, 0))
    assert not ok and "L1" in why


# ── D. 관문 배선 + 10-21 재현 ───────────────────────────────────────────────
def _gate_stub(guard, sys_net, axis=True):
    s = types.SimpleNamespace(profit_guard=guard, _sys_daily_net_krw=sys_net)
    return s


def test_D_gates_wired():
    assert 'self._pg_principal_entry_block("신동")' in inspect.getsource(
        main.TradingSystem._shindong_entry_block_reason)
    assert 'self._pg_principal_entry_block("피터2")' in inspect.getsource(
        main.TradingSystem._peter2_execute)
    # 가상 경로에는 걸지 않는다(돈이 걸리지 않는다)
    assert "_pg_principal_entry_block" not in inspect.getsource(
        main.TradingSystem._peter2_execute_virtual)


def test_D_1021_shindong_blocked_after_l4():
    """10-21: 당일 +155.9만 상태에서 신동 2연패 → 종전 임계(30만·2연패)면 L4 래치,
    이제 신동 관문도 같은 래치에 막힌다."""
    g = ProfitGuard(_cfg_pre703())
    g.on_trade_close(-196_412, 1_641_378)
    g.on_trade_close(-81_408, 1_559_970)
    assert g._pcb.is_halted, "신동 2연패가 L4 를 켠다(10-21 11:38:57 과 같다)"
    why = main.TradingSystem._pg_principal_entry_block(_gate_stub(g, 1_559_970), "신동")
    # 종전 운영값에선 L2 50만 래치가 판정 순서상 먼저 보고된다 — 요점은 「신동이 막힌다」
    assert why.startswith("ProfitGuard") and ("L2" in why or "L4" in why), why


def test_D_1021_new_thresholds_do_not_cut_the_day():
    """703차 결정값: 같은 날 2연패는 L4(3연패) 미만 — 신동 진입 통과."""
    g = ProfitGuard(_cfg_703())
    for pnl, day in ((1_038_595, 1_038_595), (602_620, 1_641_215), (196_575, 1_837_790),
                     (-196_412, 1_641_378), (-81_408, 1_559_970)):
        g.on_trade_close(pnl, day)
    assert main.TradingSystem._pg_principal_entry_block(_gate_stub(g, 1_559_970), "신동") == ""
    g.on_trade_close(-100_000, 1_459_970)        # 3연패 → L4
    why = main.TradingSystem._pg_principal_entry_block(_gate_stub(g, 1_459_970), "신동")
    assert "L4" in why


def test_D_axis_flag_off_restores_old_gate(monkeypatch):
    g = ProfitGuard(_cfg_pre703())
    g.on_trade_close(-1, 2_000_000)
    g.on_trade_close(-1, 2_000_000)
    monkeypatch.setattr(main, "PROFIT_GUARD_ACCOUNT_AXIS", False)
    assert main.TradingSystem._pg_principal_entry_block(_gate_stub(g, 2_000_000), "신동") == ""


def test_D_gate_fails_closed_on_error():
    class _Boom(object):
        def is_entry_allowed(self, *a, **k):
            raise RuntimeError("boom")
    why = main.TradingSystem._pg_principal_entry_block(_gate_stub(_Boom(), 0.0), "피터2")
    assert why == "ProfitGuard(판정실패)"


# ── E. L4 카운터 축 ─────────────────────────────────────────────────────────
def _close_stub(guard, sys_net, legs):
    # [MW0602] dev 원천 — entry_ts → 판정 축 레그 net 합 (`_record_trade_result` 가 채운다)
    acc = {}
    for d in legs:
        acc[d["entry_ts"]] = acc.get(d["entry_ts"], 0.0) + float(d["net_krw"])
    return types.SimpleNamespace(profit_guard=guard, _sys_daily_net_krw=sys_net,
                                 _pg_pos_net_by_ets=acc)


def test_E_counter_uses_position_net_and_judge_axis():
    c = _cfg_pre703()                                     # 30만 이상 · 2연패
    g = ProfitGuard(c)
    ets = "2026-10-21 11:30:13"
    legs = [{"entry_ts": ets, "entry_source": "SHINDONG", "net_krw": -97_706},
            {"entry_ts": ets, "entry_source": "SHINDONG", "net_krw": -98_706}]
    s = _close_stub(g, 1_641_378, legs)
    main.TradingSystem._pg_on_position_closed(
        s, {"pos_entry_src": "SHINDONG", "entry_ts": ets, "pnl_krw": -98_706})
    assert g._pcb.consec_loss == 1
    assert ets not in s._pg_pos_net_by_ets, "청산된 포지션 누적은 pop 된다"
    # 수동 청산은 카운터를 올리지도 리셋하지도 않는다
    main.TradingSystem._pg_on_position_closed(
        s, {"pos_entry_src": "OPERATOR_MANUAL", "entry_ts": "x", "pnl_krw": +500_000})
    assert g._pcb.consec_loss == 1


def test_E_tp1_then_small_stop_is_a_win_at_position_level():
    """종전엔 마지막 주문 손익(−)으로 셌다 — TP1 이익 뒤 본전 근처 손절이 「손실」이었다."""
    g = ProfitGuard(_cfg_pre703())
    g._pcb._consec_loss = 1
    ets = "2026-10-21 10:17:13"
    legs = [{"entry_ts": ets, "entry_source": "SHINDONG", "net_krw": +160_810},
            {"entry_ts": ets, "entry_source": "SHINDONG", "net_krw": -20_000}]
    main.TradingSystem._pg_on_position_closed(
        _close_stub(g, 1_000_000, legs),
        {"pos_entry_src": "SHINDONG", "entry_ts": ets, "pnl_krw": -20_000})
    assert g._pcb.consec_loss == 0 and not g._pcb.is_halted


def test_E_hook_moved_after_record():
    src = inspect.getsource(main.TradingSystem._post_exit)
    assert "self.profit_guard.on_trade_close(" not in src, "종전 자리(기록 전)에서 제거"
    assert src.index("self._record_trade_result(result)") < src.index(
        "self._pg_on_position_closed(result)")
    assert "daily_stats()[\"pnl_krw\"]\n        self.profit_guard" not in inspect.getsource(main)


# ── F. L3 진입 카운트 ───────────────────────────────────────────────────────
def test_F_entry_counted_for_principals_only():
    g = ProfitGuard(_cfg_703())
    s = types.SimpleNamespace(profit_guard=g)
    real_now = datetime.datetime

    class _FakeDT(datetime.datetime):
        @classmethod
        def now(cls, tz=None):
            return real_now(2026, 10, 21, 13, 30)
    orig = main.datetime.datetime
    main.datetime.datetime = _FakeDT
    try:
        main._ts_pg_count_entry(s, "SHINDONG")
        main._ts_pg_count_entry(s, "OPERATOR_MANUAL")
        main._ts_pg_count_entry(s, "PETER2")
    finally:
        main.datetime.datetime = orig
    assert g._arisk.afternoon_count == 2


def test_F_count_wired_in_execute_entry():
    src = inspect.getsource(main._ts_execute_entry)
    assert src.count("_ts_pg_count_entry(self, entry_source)") == 2
    # 주문 실패 롤백 뒤에 있어야 한다(실패 진입은 세지 않는다)
    assert src.index("pending 롤백") < src.rindex("_ts_pg_count_entry(self, entry_source)")


# ── G. 가상 주체 ────────────────────────────────────────────────────────────
def test_G_virtual_mireuk_not_blocked_wiring():
    src = inspect.getsource(main)
    assert "if not _pg_allowed and not _pg_virtual_pass and _final_grade not in (\"X\",):" in src
    assert "_ts_is_virtual(self, principal_mod.MIREUK)" in src
    assert "[ProfitGuard][Virtual]" in src


# ── H. 세션 복원 ────────────────────────────────────────────────────────────
def test_H_restore_uses_judge_sources():
    import strategy.runtime.session_recovery_service as R
    src = inspect.getsource(R)
    assert "sum_today_system_net_krw(rows, sources=_PG_SRC)" in src
    assert "system._pg_pos_net_by_ets = _pos_net" in src


def test_E_accumulator_keyed_on_judge_axis():
    """[MW0602] 포지션 net 누적이 판정 축 합계와 **같은 자리·같은 조건**에 있다."""
    src = inspect.getsource(main.TradingSystem._record_trade_result)
    i = src.index("if _entry_src_this_leg in PROFIT_GUARD_JUDGE_SOURCES:")
    j = src.index("else:", i)
    assert "self._pg_pos_net_by_ets[_pg_ets]" in src[i:j]
    assert "PROFIT_GUARD_SYSTEM_SOURCES" not in src


def test_H_panel_filter_uses_judge_sources():
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "dashboard", "panels", "profit_guard_panel.py")
    with open(path, encoding="utf-8") as f:
        src = f.read()
    assert "PROFIT_GUARD_JUDGE_SOURCES as _SRC" in src


# ── I. 703차 임계 — 10-21 실거래 흐름(포지션 순서) ──────────────────────────
LIVE_1021 = [  # (진입시, 진입분, 청산시, 청산분, 포지션 손익) — TRADE 로그 [청산 완료]
    (9, 34, 10, 12, 1_038_595), (10, 17, 10, 42, 602_620), (10, 48, 11, 6, 196_575),
    (11, 30, 11, 33, -196_412), (11, 37, 11, 38, -81_408), (11, 44, 12, 15, 51_590),
    (12, 25, 12, 26, -236_396), (12, 33, 13, 24, 751_609), (13, 28, 14, 11, -208_361),
    (14, 18, 15, 5, 308_628)]


def _replay(cfg):
    g, cum, kept = ProfitGuard(cfg), 0.0, 0.0
    for eh, em, xh, xm, pnl in LIVE_1021:
        if not g.is_entry_allowed(cum, None, T(eh, em))[0]:
            continue
        g.on_entry(T(eh, em))
        cum += pnl
        kept += pnl
        g.on_trade_close(pnl, cum)
    return kept


def test_I_703_thresholds_keep_1021_day():
    assert _replay(_cfg_703()) == sum(x[-1] for x in LIVE_1021)      # +2,227,040
    assert _replay(_cfg_pre703()) == 1_038_595, "종전 운영값은 첫 거래 뒤 L2 50만에 끊긴다"
