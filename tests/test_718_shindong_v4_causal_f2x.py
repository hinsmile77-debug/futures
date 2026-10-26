# -*- coding: utf-8 -*-
"""[MW0601 718차] 신동 규격 v4 — R3 인과 선택 · MAIN R3 F2X 방향 필터 · F2X 수량(2.0% · 버퍼 0.5 · 하한 4pt).

  A. 규격·설정 값 고정(사용자 결정 2026-10-26)
  B. F2X 방향 — 수급·가격 추세가 일치할 때만 방향, 아니면 0(필터 없음)
  C. 인과 선택 — 먼저 터치했어도 나중에 확인된 신호는 그사이 확인된 신호의 자리를 빼앗지 않는다
  D. 수량 공식 — 하한 4pt · 손절 ≤ 5.5pt 는 2계약, 넘으면 1계약
  E. 배선 — main 의 위험 수량이 하한을 넘긴다
  F. (MW0601 DB) v3 창 4일 재현값 · 분 단위 라이브 흉내 철회 0건
"""
import datetime as _dt
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest  # noqa: E402

import config.capital as CAP  # noqa: E402
import config.settings as ST  # noqa: E402
from strategy.shindong import engine, spec  # noqa: E402


# ── A ─────────────────────────────────────────────────────────────────
def test_spec_v4_registered():
    assert spec.SPEC_VERSION == "SD-2026-10-27-v4"
    assert spec.SPEC_VERSION_PREV == spec.V3_SPEC_VERSION == "SD-2026-10-21-v3"
    assert spec.SCORING_START == "2026-10-27" and spec.V3_SCORING_START == "2026-10-21"
    assert spec.VARIANTS[:2] == ("MAIN", "SHADOW_V3")
    assert (spec.F2X_SP_BAND, spec.F2X_EMA_FAST, spec.F2X_EMA_SLOW) == (50, 20, 60)
    assert spec.MAIN_TRAIL == (4.0, 4.0)                  # 트레일은 v3 그대로
    assert spec.LATE_SHADOW_START["SHADOW_V3"] == spec.SCORING_START


def test_sizing_settings():
    assert ST.SHINDONG_STOP_RISK_QTY_ENABLED is True
    assert (ST.SHINDONG_STOP_RISK_PCT, ST.SHINDONG_STOP_RISK_BUF_PTS, ST.SHINDONG_STOP_RISK_FLOOR_PTS) == \
        (0.020, 0.5, 4.0)
    assert ST.SHINDONG_STOP_RISK_FLOOR_PTS == spec.TR44_ACT   # 새 값이 아니라 트레일 발동폭 재사용


# ── B ─────────────────────────────────────────────────────────────────
def _df(n=90, price_step=-0.1, sp_step=2.0):
    """09:00 부터 n 분. 가격은 price_step 씩, 콜−풋은 sp_step 씩 움직인다."""
    candles, flow = {}, {}
    t0 = _dt.datetime(2026, 1, 1, 9, 0)
    for i in range(n):
        k = (t0 + _dt.timedelta(minutes=i)).strftime("%H:%M")
        p = 1000.0 + price_step * i
        candles[k] = (p, p + 0.2, p - 0.2, p)
        flow[k] = (100.0 + sp_step * i, 100.0)
    return engine.DayFrame(candles, flow)


def test_f2x_agree_sell():
    d = _df(price_step=-0.1, sp_step=2.0)          # 가격 하락 · 콜 쏠림(역추종 매도) → 일치
    v = engine.f2x_direction(d)
    assert v["09:10"] == 0                         # Δ = 20 ≤ 50 — 수급 판정 없음
    assert v["10:00"] == -1                        # Δ = 120 > 50 · EMA20 < EMA60


def test_f2x_disagree_is_neutral():
    d = _df(price_step=+0.1, sp_step=2.0)          # 가격 상승 · 수급은 매도 — 불일치
    assert engine.f2x_direction(d)["10:00"] == 0


def test_f2x_agree_buy():
    d = _df(price_step=+0.1, sp_step=-2.0)
    assert engine.f2x_direction(d)["10:00"] == 1


# ── C ─────────────────────────────────────────────────────────────────
def _causal_day():
    """맥점 1100 · 1120 두 개.
    09:31 매도 터치(1120) — 반전 확인은 09:39(나중).  09:33 매수 터치(1100) — 09:34 확인(먼저).
    v3(터치 순)는 09:39 매도를 먼저 잡아 09:34 매수 자리를 소급 점유했다. v4 는 09:34 매수를 먼저 잡는다."""
    lv = {"0850": {"struct_up": "[[1120.0, [\"x\"]]]", "struct_down": "[[1100.0, [\"y\"]]]",
                   "dist_low": 1080.0, "dist_high": 1140.0, "low80_lo": 1070.0, "high80_hi": 1150.0}}
    candles, flow = {}, {}
    t0 = _dt.datetime(2026, 1, 1, 9, 0)
    for i in range(0, 60):
        k = (t0 + _dt.timedelta(minutes=i)).strftime("%H:%M")
        candles[k] = (1110.0, 1110.5, 1109.5, 1110.0)
        flow[k] = (0.0, 0.0)
    candles["09:31"] = (1118.0, 1120.5, 1117.0, 1118.0)       # 1120 위꼬리 · 종가 아래 → 매도 터치
    candles["09:33"] = (1102.0, 1103.0, 1099.5, 1101.0)       # 1100 아래꼬리 · 종가 위 → 매수 터치
    for i in range(34, 60):                                    # 09:34 콜−풋 −60(매수 반전) → 그 뒤 유지
        flow["09:%02d" % i] = (0.0, 60.0)
    for i in range(39, 60):                                    # 09:39 다시 +0 → 매도 반전 확인(최저 −60 대비 +60)
        flow["09:%02d" % i] = (0.0, 0.0)
    return engine.DayFrame(candles, flow), engine.prepare_levels(lv)


def test_causal_pick_earliest_confirmation():
    d, L = _causal_day()
    r3 = [t for t in engine.run_day(d, L, "SHADOW_V3")["trades"] if t["rule"] == "R3"]
    assert r3, "합성 하루에서 R3 가 나와야 한다"
    assert (r3[0]["entry_ts"], r3[0]["side"], r3[0]["touch_ts"]) == ("09:34", 1, "09:33")


def test_causal_prefix_stable():
    """분마다 재생해도 한 번 나온 거래가 사라지지 않는다(RETRACTED 없음)."""
    d_full, L = _causal_day()
    seen, last = set(), set()
    for h in d_full.idx:
        dd = engine.DayFrame({k: (d_full.o[k], d_full.h[k], d_full.l[k], d_full.c[k]) for k in d_full.idx},
                             {k: (d_full.call[k], d_full.put[k]) for k in d_full.idx}, horizon=h)
        last = {(t["rule"], t["entry_ts"], t["side"]) for t in engine.run_day(dd, L, "SHADOW_V3")["trades"]}
        seen |= last
    assert seen == last


# ── D ─────────────────────────────────────────────────────────────────
def _q(stop):
    return CAP.shindong_stop_risk_qty(stop, 30_000_000, 50_000)      # 설정 기본값(2.0% · 0.5 · 하한 4)


def test_sizing_formula():
    # 60만 ÷ ((max(손절, 4) + 0.5) × 5만)
    assert _q(1.3) == 2          # 하한 4 → 60 / 22.5 = 2.67 (711차 1.5%·버퍼1 이면 3)
    assert _q(4.0) == 2
    assert _q(5.5) == 2          # 60 / 30.0 = 2.0 — 경계
    assert _q(5.6) == 1          # 60 / 30.5 = 1.97
    assert _q(10.6) == 1
    assert _q(None) is None      # 미측정은 0 이 아니라 None(계측 4원칙 ②)
    assert CAP.shindong_stop_risk_qty(1.3, 30_000_000, 50_000, floor_pts=0.0) == 6   # 하한 끄면 좁은 손절에 더 싣는다(상한 3 은 호출자)


# ── E ─────────────────────────────────────────────────────────────────
def test_main_passes_floor():
    src = open(os.path.join(ROOT, "main.py"), encoding="utf-8").read()
    a = src.index("def _shindong_risk_qty(")
    h = src[a:src.index("\n    def ", a + 10)]
    assert '"SHINDONG_STOP_RISK_FLOOR_PTS"' in h
    assert "floor_pts=flo)" in h


# ── F ─────────────────────────────────────────────────────────────────
_DBS = [os.path.join(ROOT, "data", "db", p) for p in ("raw_data.db", "option_flow.db", "premarket_levels.db")]
try:
    from utils.db_utils import pc_id as _pc_id
    _SRC_OK = all(os.path.exists(p) for p in _DBS) and _pc_id() == "MW0601"
except Exception:                         # noqa: BLE001
    _SRC_OK = False


def _load(day):
    from strategy.shindong import runner
    from strategy.shindong.calendar import select_flow_product
    c, f, l = runner.load_inputs(day, select_flow_product(_dt.date.fromisoformat(day))[0], *_DBS)
    return c, f, engine.prepare_levels(l)


@pytest.mark.skipif(not _SRC_OK, reason="기대값은 MW0601 DB 산출")
@pytest.mark.parametrize("day,main,v3", [
    # 분석 f2_final(②SHADOW_F2X · 인과 MAIN)과 원 단위로 같다 — 22일 합 +6,379,xxx / +1,204,xxx
    ("2026-10-21", -45202, 1048260),
    ("2026-10-22", 1564711, 262970),
    ("2026-10-23", -1153000, -1797791),
    ("2026-10-26", -308983, -1533184),
])
def test_replay_v3_window(day, main, v3):
    c, f, L = _load(day)
    d = engine.DayFrame(c, f)
    net = lambda v: round(sum(engine.trade_net(t) for t in engine.run_day(d, L, v)["trades"]
                              if t["status"] == "CLOSED"))
    assert net("MAIN") == pytest.approx(main, abs=2)
    assert net("SHADOW_V3") == pytest.approx(v3, abs=2)


@pytest.mark.skipif(not _SRC_OK, reason="기대값은 MW0601 DB 산출")
@pytest.mark.parametrize("day", ["2026-10-22", "2026-10-26"])
def test_no_live_retraction(day):
    """v3 엔진은 이 두 날 실제로 RETRACTED 를 냈다(철회 메커니즘 문서 §1). v4 는 분 단위로 돌려도 0건이어야 한다."""
    c, f, L = _load(day)
    mins = [m for m in sorted(set(c) | set(f)) if "09:30" <= m <= "15:08"]
    for v in ("MAIN", "SHADOW_V3"):
        seen, last = set(), set()
        for h in mins:
            last = {(t["rule"], t["entry_ts"], t["side"])
                    for t in engine.run_day(engine.DayFrame(c, f, horizon=h), L, v)["trades"]}
            seen |= last
        assert seen == last, (v, sorted(seen - last))


# ── G. 신동2AI 대 MAIN 사전등록 §7 재등록 ─────────────────────────────────
def test_sd2ai_reregistered_for_v4():
    src = open(os.path.join(ROOT, "scripts", "shindong2_rival.py"), encoding="utf-8").read()
    assert '"MW0601": dict(version="SD2AI-MW0601-2026-10-27-v3", scoring_start="2026-10-27")' in src
    assert spec.SCORING_START == "2026-10-27"            # 새 창 개시 = v4 첫 거래일
    doc = open(os.path.join(ROOT, "docs", "맥점x옵션사다리개선", "02_사전등록_AI대MAIN_판정_MW0601-20261020.md"),
               encoding="utf-8").read()
    assert "SD2AI-MW0601-2026-10-27-v3" in doc and spec.SPEC_VERSION in doc
    assert "사료" in doc and "가상 2계약" in doc           # v2 창 종료 · 수량 무관 명시
    sk = open(os.path.join(ROOT, ".claude", "skills", "shindong2", "SKILL.md"), encoding="utf-8").read()
    assert spec.SPEC_VERSION in sk and "TR44·X4NFA)" not in sk   # 상대 설명이 v4 로 갱신됐다
