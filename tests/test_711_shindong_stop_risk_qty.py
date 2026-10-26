# -*- coding: utf-8 -*-
"""[MW0601 711차] 신동 손절거리 위험 수량 · 위험자본 3,000만 · 복원 1차 판정(선행 수정).

고정하는 것
  A. 사용자 결정 값: 위험자본 3,000만 · X 1.5% · 버퍼 1pt · 켜짐. dev 상수와 이름이 다르다.
  B. 식: floor(자본 × X% ÷ ((손절 + 버퍼) × 1pt)) · 최소 1 · 미측정/꺼짐 None.
  C. 배선: 진입 시점에 계획 수량 ∧ 위험 수량 → 증거금 · 미측정이면 TRADE 경고 · 진입 수량 기록 ·
     가상 장부도 같은 위험 수량.
  D. 선행 수정: 복원(_shindong_adopt)의 1차 판정이 계획 수량이 아니라 트래커 진입 수량과 비교.
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import config.capital as CAP          # noqa: E402
import config.settings as ST          # noqa: E402


def _src(rel):
    return io.open(os.path.join(ROOT, rel), encoding="utf-8").read()


def _func(src, name):
    a = src.index("    def %s(" % name)
    b = re.compile(r"\n    def ").search(src, a + 10)
    return src[a:b.start() if b else len(src)]


# ── A ─────────────────────────────────────────────────────────────────
def test_user_decided_values():
    assert ST.LIVE_OPERATING_CAPITAL_KRW == 30_000_000
    assert ST.SHINDONG_STOP_RISK_QTY_ENABLED is True
    # [718차 / 사용자 결정 2026-10-26] 1.5% · 버퍼 1 → 2.0% · 버퍼 0.5 · 하한 4pt(v4 MAIN F2X 전용) — test_718 이 고정
    assert ST.SHINDONG_STOP_RISK_PCT == 0.020
    assert ST.SHINDONG_STOP_RISK_BUF_PTS == 0.5
    assert ST.SHINDONG_STOP_RISK_FLOOR_PTS == 4.0
    assert not hasattr(ST, "SHINDONG_TRADE_RISK_PCT")   # dev 657차(7% · ATR 분모)와 다른 상수 — 이름 충돌 방지


# ── B ─────────────────────────────────────────────────────────────────
def _q(stop, cap=30_000_000):
    # 711차 공식 그대로(하한 없음) — [718차] 하한 인자가 생겨 0 을 명시한다(기본값은 설정의 4pt)
    return CAP.shindong_stop_risk_qty(stop, cap, 50_000, risk_pct=0.015, buf_pts=1.0, floor_pts=0.0)


def test_formula_examples():
    # 45만 ÷ ((손절+1)×5만)
    assert _q(1.3) == 3          # 45 / 11.5 = 3.9
    assert _q(3.2) == 2          # 45 / 21.0 = 2.1
    assert _q(5.4) == 1          # 45 / 32.0 = 1.4
    assert _q(10.6) == 1         # 45 / 58.0 = 0.78 → 최소 1
    assert _q(0.0) == 9          # 45 / 5 — 상한은 호출자가 건다
    assert _q(3.2, cap=34_000_000) == 2


def test_unmeasured_is_none_not_zero():
    assert _q(None) is None
    assert CAP.shindong_stop_risk_qty(3.0, 0, 50_000, risk_pct=0.015, buf_pts=1.0) is None
    assert CAP.shindong_stop_risk_qty(3.0, 30_000_000, 0, risk_pct=0.015, buf_pts=1.0) is None
    assert CAP.shindong_stop_risk_qty(3.0, 30_000_000, 50_000, risk_pct=0.0, buf_pts=1.0) is None


def test_disabled_is_none(monkeypatch):
    monkeypatch.setattr(CAP, "SHINDONG_STOP_RISK_QTY_ENABLED", False)
    assert _q(3.0) is None


def test_risk_capital_caps_at_policy():
    assert CAP.risk_capital(deposit_krw=34_000_000) == 30_000_000      # 예탁금이 많아도 3,000만
    assert CAP.risk_capital(deposit_krw=25_000_000) == 25_000_000      # 적으면 따라 내려간다


# ── C ─────────────────────────────────────────────────────────────────
def test_exec_step_wiring_order():
    step = _func(_src("main.py"), "_shindong_exec_step")
    i_plan = step.index("_planned = self._shindong_live_qty()")
    i_risk = step.index("_risk_q, _risk_why = self._shindong_risk_qty(rec)")
    i_eff = step.index("_planned_eff = min(_planned, _risk_q) if (_risk_q is not None and _planned > 0) else _planned")
    i_qty = step.index('qty = _capital_sd_entry_qty(_planned_eff, _cap["margin_qty"])')
    i_exe = step.index("self._execute_entry(")
    i_rec = step.index('rec["entry_qty"] = int(qty)')
    assert i_plan < i_risk < i_eff < i_qty < i_exe < i_rec
    # 미측정 경고·축소 기록은 TRADE 계층(707차 로그 일원화)
    for tag in ("— 계획 수량 %d계약 그대로", "위험 기준 축소"):
        i = step.index(tag)
        assert "log_manager.trade(" in step[max(0, i - 120):i], tag


def test_risk_helper_uses_single_capital_source():
    h = _func(_src("main.py"), "_shindong_risk_qty")
    assert "_capital_risk_capital(deposit_krw=self._broker_dep_base_today)" in h
    assert "_capital_sd_stop_risk_qty(stop_pts, cap, self._pt_value" in h
    assert 'abs(float(rec["entry_px"]) - float(rec["stop"]))' in h
    assert '"SHINDONG_STOP_RISK_QTY_ENABLED"' in h and '"위험수량 꺼짐"' in h


def test_virtual_book_mirrors_risk_qty():
    src = _src("main.py")
    v = _func(src, "_shindong_virtual_step")
    assert "_vrq, _vrw = self._shindong_risk_qty(rec)" in v
    assert "qty = max(1, min(qty, _vrq))" in v


# ── D ─────────────────────────────────────────────────────────────────
def test_adopt_compares_entry_qty_not_planned():
    a = _func(_src("main.py"), "_shindong_adopt")
    assert "_eq = int(pos.entry_quantity or 0)" in a
    assert 'rec["leg1_done"] = int(pos.quantity or 0) < _eq' in a
    assert "< self._shindong_live_qty()" not in a                     # 계획 수량 비교 금지
    assert '"planned_fallback"' in a and 'rec["entry_qty_src"]' in a   # 폴백 가시화(④)


def test_adopt_behaviour(monkeypatch):
    """복원 본문을 떼어 돌린다 — 계획 3 · 진입 2 · 보유 2 → 1차 「대기」(예전 로직은 「완료」 오판)."""
    import textwrap
    import types
    src = _src("main.py")
    body = textwrap.dedent(_func(src, "_shindong_adopt"))
    logs = []
    ns = {"log_manager": types.SimpleNamespace(system=lambda m, lv="INFO": logs.append(m))}
    exec(body, ns)
    adopt = ns["_shindong_adopt"]
    trades = [{"trade_key": "R3|10:00|+1", "rule": "R3", "side": 1, "entry_px": 900.0, "stop_init": 897.0,
               "stop_now": 897.0, "t1": 904.0, "t2": 910.0, "status": "OPEN", "entry_ts": "2026-10-26 10:00:00"}]

    def me(qty, entry_qty):
        pos = types.SimpleNamespace(status="LONG", quantity=qty, entry_quantity=entry_qty, stop_price=897.0)
        return types.SimpleNamespace(position=pos, _sd_exec={}, _sd_exec_orphan_warned=False,
                                     _shindong_live_qty=lambda: 3, _sd_exec_save=lambda d: None,
                                     _sd_exec_event=lambda *a, **k: None)
    r = adopt(me(2, 2), trades, "2026-10-26")
    assert r["leg1_done"] is False and r["entry_qty"] == 2 and r["entry_qty_src"] == "tracker"
    r = adopt(me(1, 2), trades, "2026-10-26")
    assert r["leg1_done"] is True
    r = adopt(me(2, 0), trades, "2026-10-26")                         # 트래커 값 없음 → 계획 수량 폴백
    assert r["entry_qty_src"] == "planned_fallback" and r["leg1_done"] is True
    assert "진입수량 출처 planned_fallback" in logs[-1]
