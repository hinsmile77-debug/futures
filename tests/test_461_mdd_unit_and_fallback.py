# -*- coding: utf-8 -*-
"""461차 / F-7 — Live MDD 분모 정합 + 거래0건 WR/PF 폴백 가시화.

## 무엇을 잡는가

**같은 이름(`mdd_pct`)이 두 곳에서 다른 분모를 썼다.**

    backtest/performance_metrics.py : mdd_krw / 자본        ← WFA 기준(15%)
    config/strategy_registry.py     : mdd_krw / 누적PnL peak ← Live

이름이 같으니 `_compute_verdict()`가 아무 의심 없이 뺐다. 2026-08-13 실측으로
Live 20일 MDD가 **215.4%**(peak 대비)로 나와 WFA 14.2%에서 빼니 mdd_delta=+2.012,
NORMAL 상한 +0.03을 200배 넘겨 `UNDERPERFORM` → *"🔄 교체 후보 탐색 — param_optimizer
+ WFA 즉시 예약"* 권고가 나왔다. 같은 날짜를 자본 대비로 다시 재면 **3.33%**,
mdd_delta = **-0.109**로 오히려 개선 쪽이다.

계측 4원칙 ① 단위 명시가 정확히 겨냥하는 사고 유형이다.

또 하나: 거래 0건인 날 `win_rate=0.0` · `profit_factor=1.00`이 저장돼 리포트에
`WR=0.0% PF=1.00`으로 찍혔다. "승률 0%"와 "표본 없음"은 다른 사실인데 같은 숫자가
됐다 — 계측 4원칙 ② 미측정≠0 · ④ 폴백 가시화.

## 이 테스트가 고정하는 계약

1. `get_rolling_metrics()`는 두 MDD를 **다른 이름으로** 낸다. `mdd_pct`는
   `mdd_pct_of_peak`의 별칭(하위호환)이며 판정에 쓰이지 않는다.
2. `_compute_verdict()`는 **자본 대비**만 본다. peak 대비 값을 넣어도 판정이
   흔들리지 않아야 한다.
3. 자본 기준을 못 구하면 peak 대비로 대신 판정하지 않고 `INSUFFICIENT`.
4. `record_live_snapshot()`는 거래 0건이면 WR/PF를 **NULL**로 저장하고
   `metrics_measured=0`을 남긴다.
5. 롤링(20일)이 스냅샷(당일)의 WR/PF를 **덮지 않는다** — 덮으면 미측정이
   20일 값으로 위장된다.
"""

import os
import sqlite3
import tempfile
import shutil

import pytest

from config.strategy_registry import (
    StrategyRegistry,
    _merge_rolling,
    _target_capital_krw,
    VERDICT_INSUFFICIENT,
    VERDICT_UNDERPERFORM,
    VERDICT_NORMAL,
    VERDICT_OUTPERFORM,
)


@pytest.fixture
def reg():
    d = tempfile.mkdtemp(prefix="t461_")
    r = StrategyRegistry(db_path=os.path.join(d, "reg.db"))
    yield r
    shutil.rmtree(d, ignore_errors=True)


def _seed_version(r, ver="vT", wfa=None):
    r.register_version(
        version=ver,
        changed_params={},
        wfa_metrics=wfa or {"sharpe": 1.42, "mdd_pct": 0.142,
                            "win_rate": 0.54, "profit_factor": 1.3},
        note="t461",
    )
    return ver


# ─────────────────────────────────────────────────────────────────────────
# 1) 두 MDD가 이름으로 구분되는가
# ─────────────────────────────────────────────────────────────────────────
def _seed_daily_pnl(reg, ver, pnls, start_day=1):
    """일자별 daily_pnl 스냅샷을 직접 심는다.

    record_live_snapshot()은 오늘 날짜로 UPSERT하므로 여러 날을 만들 수 없다.
    """
    with reg._conn() as con:
        for i, pnl in enumerate(pnls):
            con.execute(
                "INSERT INTO strategy_live_snapshots "
                "(version, snapshot_date, daily_pnl, total_trades) VALUES (?,?,?,?)",
                (ver, "2026-08-%02d" % (start_day + i), float(pnl), 3),
            )
        con.commit()


def test_rolling_exposes_both_mdd_denominators(reg):
    ver = _seed_version(reg)
    # peak가 작고 낙폭이 큰 곡선 — peak 대비는 100%를 넘고 자본 대비는 작다
    _seed_daily_pnl(reg, ver, [100_000, -400_000, 50_000, -200_000, 30_000])

    m = reg.get_rolling_metrics(ver, days=20)
    assert m, "롤링 지표가 비었다"

    # 별칭 계약: mdd_pct == mdd_pct_of_peak (하위호환)
    assert m["mdd_pct"] == m["mdd_pct_of_peak"]

    # 분모가 실제로 다르다
    cap = _target_capital_krw()
    assert cap > 0
    assert m["mdd_pct_of_capital"] == pytest.approx(m["mdd_krw"] / cap, rel=1e-3)
    assert m["mdd_pct_of_peak"] == pytest.approx(m["mdd_krw"] / 100_000)

    # 낙폭 55만원: peak(10만원) 대비 550% / 자본(5천만원) 대비 1.1%
    # — 같은 사실을 두 분모로 재면 500배 차이가 난다는 것이 F-7의 요점이다
    assert m["mdd_pct_of_peak"] > 5.0
    assert m["mdd_pct_of_capital"] < 0.02


# ─────────────────────────────────────────────────────────────────────────
# 2) 판정은 자본 대비만 본다
# ─────────────────────────────────────────────────────────────────────────
def test_verdict_uses_capital_denominator_not_peak(reg):
    """2026-08-13 실측 재현: peak 2.1535 / capital 0.0333 / WFA 0.142."""
    stages = {"WFA": {"sharpe": 1.42, "mdd_pct": 0.142}}
    live = {
        "days": 20,
        "sharpe": 1.40,                 # sharpe_delta = -0.02 → NORMAL 통과
        "mdd_pct": 2.1535,              # peak 대비 (판정에 쓰이면 안 된다)
        "mdd_pct_of_peak": 2.1535,
        "mdd_pct_of_capital": 0.0333,   # 자본 대비
    }
    v = reg._compute_verdict(stages, live)
    # 자본 대비면 mdd_delta = 0.0333-0.142 = -0.109 ≤ -0.01 이고
    # sharpe_delta -0.02 는 OUTPERFORM 하한(+0.15) 미달 → NORMAL
    assert v == VERDICT_NORMAL, "자본 대비로 판정하지 않았다"

    # peak 값을 아무리 키워도 판정이 흔들리면 안 된다
    live_worse = dict(live, mdd_pct=99.0, mdd_pct_of_peak=99.0)
    assert reg._compute_verdict(stages, live_worse) == v


def test_verdict_holds_when_capital_mdd_missing(reg):
    """자본 기준을 못 구하면 peak로 대체 판정하지 않고 보류한다."""
    stages = {"WFA": {"sharpe": 1.42, "mdd_pct": 0.142}}
    live = {"days": 20, "sharpe": 1.40, "mdd_pct": 0.01,
            "mdd_pct_of_capital": None}
    assert reg._compute_verdict(stages, live) == VERDICT_INSUFFICIENT


def test_verdict_still_fails_on_sharpe_alone(reg):
    """MDD를 고쳐도 Sharpe가 미달이면 UNDERPERFORM이 유지된다.

    2026-08-13 실측이 정확히 이 경우였다(Live Sh=0.57 vs WFA 1.42,
    sharpe_delta=-0.848). F-7은 MDD 축의 계측 결함만 없앤 것이지
    판정을 좋게 만드는 변경이 아니다.
    """
    stages = {"WFA": {"sharpe": 1.42, "mdd_pct": 0.142}}
    live = {"days": 20, "sharpe": 0.57, "mdd_pct_of_capital": 0.0333}
    assert reg._compute_verdict(stages, live) == VERDICT_UNDERPERFORM


# ─────────────────────────────────────────────────────────────────────────
# 3) 거래 0건 → WR/PF는 NULL, 플래그가 남는다
# ─────────────────────────────────────────────────────────────────────────
def test_zero_trades_stores_null_not_fallback(reg):
    ver = _seed_version(reg, "vZ")
    # main.py:daily_close 가 실제로 넘기는 형태 — 0/max(0,1)=0.0, PF 폴백 1.0
    reg.record_live_snapshot(ver, {
        "win_rate": 0.0, "total_trades": 0,
        "daily_pnl": 0.0, "profit_factor": 1.0,
    })
    with reg._conn() as con:
        row = con.execute(
            "SELECT win_rate, profit_factor, total_trades, metrics_measured "
            "FROM strategy_live_snapshots WHERE version=?", (ver,)
        ).fetchone()

    assert row[0] is None, "거래 0건인데 win_rate가 0.0으로 저장됐다"
    assert row[1] is None, "거래 0건인데 profit_factor가 1.0으로 저장됐다"
    assert row[2] == 0
    assert row[3] == 0, "metrics_measured 플래그가 없다"


def test_nonzero_trades_stores_values(reg):
    ver = _seed_version(reg, "vN")
    reg.record_live_snapshot(ver, {
        "win_rate": 0.6, "total_trades": 5,
        "daily_pnl": 120000.0, "profit_factor": 1.8,
    })
    with reg._conn() as con:
        row = con.execute(
            "SELECT win_rate, profit_factor, metrics_measured "
            "FROM strategy_live_snapshots WHERE version=?", (ver,)
        ).fetchone()
    assert row[0] == pytest.approx(0.6)
    assert row[1] == pytest.approx(1.8)
    assert row[2] == 1


# ─────────────────────────────────────────────────────────────────────────
# 4) 롤링이 당일 값을 덮지 않는다
# ─────────────────────────────────────────────────────────────────────────
def test_rolling_never_overwrites_daily_only_keys():
    snap = {"sharpe": None, "win_rate": None, "profit_factor": None,
            "total_trades": 0, "metrics_measured": False}
    rolling = {"sharpe": 1.1, "win_rate": 0.55, "profit_factor": 1.4,
               "total_trades": 88, "mdd_pct_of_capital": 0.03}

    out = _merge_rolling(dict(snap), rolling)

    # 누락된 롤링 전용 지표는 채워진다
    assert out["sharpe"] == 1.1
    assert out["mdd_pct_of_capital"] == 0.03
    # 당일 전용 키는 20일 값으로 덮이지 않는다
    assert out["win_rate"] is None, "당일 WR이 20일 롤링 값으로 덮였다"
    assert out["profit_factor"] is None
    assert out["total_trades"] == 0
    assert out["metrics_measured"] is False


def test_merge_marks_unmeasured_when_no_snapshot():
    """당일 스냅샷이 아예 없으면 롤링을 쓰되 '당일 미측정'으로 표시한다."""
    out = _merge_rolling(None, {"sharpe": 1.1, "win_rate": 0.55})
    assert out["metrics_measured"] is False


# ─────────────────────────────────────────────────────────────────────────
# 5) 리포트 배너가 폴백을 숫자로 찍지 않는다
# ─────────────────────────────────────────────────────────────────────────
def test_banner_prints_unmeasured_instead_of_zero(monkeypatch, tmp_path):
    from strategy.ops.daily_exporter import DailyExporter

    class _FakeReg(object):
        def get_current_version(self):
            return {
                "version": "vB", "live_days": 20, "verdict": "NORMAL",
                "live_snapshot": {
                    "sharpe": 0.57,
                    "mdd_pct": 2.1535,
                    "mdd_pct_of_capital": 0.0333,
                    "win_rate": 0.0, "profit_factor": 1.0,
                    "metrics_measured": False,
                },
            }

        def get_rolling_metrics(self, ver, days=20):
            return {"cum_pnl": 371426.0, "sharpe": 0.57,
                    "mdd_pct_of_peak": 2.1535, "mdd_pct_of_capital": 0.0333}

    import config.strategy_registry as _sr
    monkeypatch.setattr(_sr, "get_registry", lambda: _FakeReg())

    report = DailyExporter(report_dir=str(tmp_path)).build_report()

    assert "WR=미측정(거래0건)" in report, "거래 0건인데 WR이 숫자로 찍혔다"
    assert "PF=미측정" in report
    assert "WR=0.0%" not in report
    # MDD는 자본 대비로, 단위가 라벨에 박혀 있어야 한다
    assert "MDD(자본대비)=3.3%" in report
    assert "MDD=215.4%" not in report, "peak 대비가 단위 표기 없이 찍혔다"
