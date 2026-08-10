# -*- coding: utf-8 -*-
"""456차 Wave 4 — 사전등록 하위 축 3종.

배경: `docs/정기점검/매일점검/0810_Wave4_사전등록_합격선_제안_MW0601.md` (승인),
      `dev_memory/DECISION_LOG.md` 456차 Wave 4.

핵심 불변식
  ① 합격선은 settings에 **사전등록**돼 있고 코드가 그 값을 읽는다(하드코딩 금지)
  ② 표본 미달이면 판정하지 않는다
  ③ 이상치 제거 후 부호가 뒤집히면 SUPPORTS_HYP를 주지 않는다(372차)
  ④ 계측 컬럼이 존재한다
"""
import math
import os
import sqlite3
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config.settings import VALIDATION_CAMPAIGN as V          # noqa: E402
from scripts import wave4_subaxis as W                        # noqa: E402


# ── 사전등록 값 (승인된 수치) ────────────────────────────────────────────────

def test_approved_thresholds_are_registered():
    """승인된 합격선이 settings에 그대로 있는가 — 사후 변경 방지."""
    a = V["tp1_protect_forgone_mfe"]
    assert a["min_samples"] == 40 and a["min_days"] == 10
    assert a["forgone_pt_threshold"] == 0.5 and a["t_threshold"] == 2.26
    assert a["data_start"] == "2026-08-07"     # arm_ts 신설일(436차)

    b = V["exit_fill_slippage_qty"]
    assert b["min_samples"] == 60 and b["min_samples_qty2p"] == 20
    assert b["min_days"] == 10 and b["outlier_drop_top"] == 2
    assert b["pre_observed"] is True, "정직성 고지 플래그가 꺼져 있다"

    c = V["grade_promotion_passcount"]
    assert c["min_samples"] == 40 and c["min_days"] == 10
    assert c["min_samples_per_bucket"] == 20 and c["t_threshold"] == 2.26


# ── 계측 배관 ────────────────────────────────────────────────────────────────

def test_instrumentation_columns_exist():
    from config.settings import TRADES_DB
    con = sqlite3.connect(TRADES_DB)
    tc = {r[1] for r in con.execute("PRAGMA table_info(trades)")}
    ec = {r[1] for r in con.execute("PRAGMA table_info(exit_fill_slippage)")}
    con.close()
    assert "checklist_pass_count" in tc
    assert "quantity" in ec


def test_position_tracker_carries_pass_count(tmp_path, monkeypatch):
    import strategy.position.position_tracker as m
    monkeypatch.setattr(m, "_STATE_FILE", str(tmp_path / "p.json"))
    pt = m.PositionTracker(pt_value=50_000)
    pt.open_position(direction="SHORT", price=980.0, quantity=1, atr=3.0,
                     grade="A", checklist_pass_count=9)
    assert pt.checklist_pass_count == 9
    r = pt.apply_exit_fill(exit_price=979.0, quantity=1, reason="TP")
    assert r["checklist_pass_count"] == 9, "청산 결과에 실려야 trades에 기록된다"
    assert pt.checklist_pass_count is None, "청산 후 초기화돼야 한다"


def test_pass_count_survives_restart(tmp_path, monkeypatch):
    import strategy.position.position_tracker as m
    monkeypatch.setattr(m, "_STATE_FILE", str(tmp_path / "p.json"))
    pt = m.PositionTracker(pt_value=50_000)
    pt.open_position(direction="LONG", price=980.0, quantity=2, atr=3.0,
                     grade="A", checklist_pass_count=11)
    revived = m.PositionTracker(pt_value=50_000)
    assert revived.load_state() is True
    assert revived.checklist_pass_count == 11


def test_pass_count_none_is_not_zero(tmp_path, monkeypatch):
    """미기록과 '0개 통과'를 구분한다 (G3-A② 미측정 ≠ 0)."""
    import strategy.position.position_tracker as m
    monkeypatch.setattr(m, "_STATE_FILE", str(tmp_path / "p.json"))
    pt = m.PositionTracker(pt_value=50_000)
    pt.open_position(direction="SHORT", price=980.0, quantity=1, atr=3.0)
    assert pt.checklist_pass_count is None


# ── 통계 헬퍼 ────────────────────────────────────────────────────────────────

def test_daily_t_needs_three_days():
    assert math.isnan(W.daily_t([1.0, 2.0])[1])
    m, t, n = W.daily_t([1.0, 1.2, 0.8, 1.1])
    assert n == 4 and t > 0


def test_daily_t_zero_variance_is_nan():
    _, t, _ = W.daily_t([1.0, 1.0, 1.0, 1.0])
    assert math.isnan(t), "분산 0이면 t를 만들지 않는다"


def test_half_sign_agree():
    assert W.half_sign_agree([("d1", 1.0), ("d2", 2.0), ("d3", 1.5), ("d4", 1.1)])
    assert not W.half_sign_agree([("d1", 1.0), ("d2", 2.0), ("d3", -1.5), ("d4", -1.1)])
    assert not W.half_sign_agree([("d1", 1.0)]), "표본 부족은 일치로 치지 않는다"


# ── 판정 로직 ────────────────────────────────────────────────────────────────

class _FakeConn:
    def __init__(self, rows): self._rows = rows
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def execute(self, sql, params=()): return self
    def fetchall(self): return self._rows


def _slip_rows(spec):
    """spec=[(date, qty, abs_slip)] → sqlite3.Row 흉내"""
    return [{"ts": "%s 10:00:00" % d, "qty": q, "slippage_pts": -s}
            for d, q, s in spec]


def _spearman(x, y):
    from scripts.generate_validation_campaign_report import _spearman as sp
    return sp(x, y)


def test_slippage_qty_insufficient_when_qty2p_short():
    """qty>=2 병목 — 전체가 차도 qty2p가 모자라면 판정하지 않는다."""
    spec = [("2026-08-%02d" % (3 + i % 8), 1, 0.3) for i in range(80)]
    out = W.eval_exit_fill_slippage_qty(
        lambda db: _FakeConn(_slip_rows(spec)), "x", "2026-07-01", _spearman, V)
    assert out["verdict"] == "INSUFFICIENT"
    assert "qty>=2" in out["reason"]


def test_slippage_qty_reports_pre_observed_flag():
    out = W.eval_exit_fill_slippage_qty(
        lambda db: _FakeConn([]), "x", "2026-07-01", _spearman, V)
    assert out["pre_observed"] is True, "사전관측 고지가 결과에 실려야 한다"


def test_slippage_qty_outlier_guard_blocks_supports():
    """상위 2건이 결론을 만들면 SUPPORTS_HYP를 주지 않는다 (372차)."""
    spec = []
    for i in range(12):                       # 12일 × 6건, qty 1/2 혼재
        d = "2026-08-%02d" % (3 + i)
        for j in range(3):
            spec.append((d, 1, 0.30))
            spec.append((d, 2, 0.30))         # 수량과 무관 = rho 0
    spec.append(("2026-08-03", 2, 99.0))      # 이상치 2건이 관계를 만든다
    spec.append(("2026-08-04", 2, 99.0))
    out = W.eval_exit_fill_slippage_qty(
        lambda db: _FakeConn(_slip_rows(spec)), "x", "2026-07-01", _spearman, V)
    assert out["verdict"] != "SUPPORTS_HYP", \
        "이상치 제거 전 부호만으로 가설을 지지하면 안 된다"


def test_passcount_no_column_is_reported():
    out = W.eval_grade_promotion_passcount(
        lambda extra_cols="": [], lambda c: False, _spearman, V)
    assert out["no_data"] is True and "컬럼 없음" in out["reason"]


def test_passcount_insufficient_reports_distribution():
    """표본 미달이어도 분포는 보여준다 — 도달 가능성 판단 재료."""
    pos = [{"entry_ts": "2026-08-11 10:00:00", "raw_grade": "C",
            "grade": "A", "checklist_pass_count": 9, "pnl": 100.0}]
    out = W.eval_grade_promotion_passcount(
        lambda extra_cols="": pos, lambda c: True, _spearman, V)
    assert out["verdict"] == "INSUFFICIENT"
    assert out["passcount_dist"] == {9: 1}


def test_forgone_mfe_respects_data_start():
    out = W.eval_tp1_protect_forgone_mfe(
        lambda db: _FakeConn([]), "x", "2026-07-01",
        lambda ts, exclude_untradeable=False: ({}, {}, {}), V)
    assert out["verdict"] == "INSUFFICIENT"
    assert "2026-08-07" in out["reason"], "arm_ts 신설일 이전은 소급 불가"


def test_all_three_disabled_switch_works():
    import copy
    cfg = copy.deepcopy(V)
    for k in ("exit_fill_slippage_qty", "grade_promotion_passcount",
              "tp1_protect_forgone_mfe"):
        cfg[k]["enabled"] = False
    assert W.eval_exit_fill_slippage_qty(
        lambda db: _FakeConn([]), "x", "2026-07-01", _spearman, cfg
    )["verdict"] == "DISABLED"
    assert W.eval_grade_promotion_passcount(
        lambda extra_cols="": [], lambda c: True, _spearman, cfg
    )["verdict"] == "DISABLED"
    assert W.eval_tp1_protect_forgone_mfe(
        lambda db: _FakeConn([]), "x", "2026-07-01",
        lambda ts, exclude_untradeable=False: ({}, {}, {}), cfg
    )["verdict"] == "DISABLED"


def test_report_renders_three_rows():
    """리포트 요약표에 3행이 배선됐는가."""
    src = open(os.path.join(_ROOT, "scripts",
                            "generate_validation_campaign_report.py"),
               encoding="utf-8").read()
    for tag in ("[36-P]", "[17-Q]", "[TP1-M]"):
        assert tag in src, "%s 행이 요약표에 없다" % tag
    assert "wave4_subaxis" in src, "하위 축 모듈이 import 되지 않았다"
