# -*- coding: utf-8 -*-
"""[MW0601 477차 / DD-1] ModelLive DB 승격(G-3) 계산부 검증.

0818 딥다이브가 확정한 두 계측 사실을 회귀 고정한다:
① 10m/15m 예측은 :x9/:x0 연속 2분 쌍으로 생성돼 명목 n의 절반이 유효표본이다
   — n_eff는 "겹치지 않는 h분 창의 그리디 최대 개수"로 이를 보정해야 한다.
② 미측정 ≠ 0 (계측 4원칙 ②) — 표본 없으면 acc/sigma_avg는 None이어야 한다.
"""
import os
import sys
import sqlite3
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_utils import summarize_live_prediction_rows, save_model_live_daily


def _row(ts, direction, actual, correct, sigma=None):
    return {"ts": ts, "direction": direction, "actual": actual,
            "correct": correct, "sigma_at_t": sigma}


def test_pair_sampling_collapses_to_half_for_10m():
    """0818 실측 패턴 그대로 — :x9/:x0 쌍 6행은 유효표본 3이어야 한다."""
    rows = [
        _row("2026-08-18 11:09:00", -1, 0, 0),
        _row("2026-08-18 11:10:00", -1, 0, 0),
        _row("2026-08-18 11:19:00", 0, -1, 0),
        _row("2026-08-18 11:20:00", 0, -1, 0),
        _row("2026-08-18 11:29:00", -1, -1, 1),
        _row("2026-08-18 11:30:00", -1, -1, 1),
    ]
    out = summarize_live_prediction_rows(rows, h_min=10)
    assert out["n"] == 6
    assert out["n_eff"] == 3   # 11:09 → 11:19 → 11:29 (각 채택 후 10분 봉쇄)
    assert out["acc"] == pytest.approx(2.0 / 6.0)


def test_1m_horizon_every_minute_is_independent():
    """1m은 매분이 독립 창 — n_eff == n (쌍 보정이 과잉 축약하면 안 된다)."""
    rows = [_row("2026-08-18 10:0%d:00" % i, 1, 1, 1) for i in range(5)]
    out = summarize_live_prediction_rows(rows, h_min=1)
    assert out["n"] == 5
    assert out["n_eff"] == 5


def test_crosstab_keys_and_counts():
    rows = [
        _row("2026-08-18 09:00:00", -1, 0, 0),
        _row("2026-08-18 09:20:00", -1, 0, 0),
        _row("2026-08-18 09:40:00", 1, -1, 0),
        _row("2026-08-18 10:00:00", 0, 0, 1),
    ]
    out = summarize_live_prediction_rows(rows, h_min=10)
    assert out["hit_dir"] == {"p-1_a+0": 2, "p+1_a-1": 1, "p+0_a+0": 1}


def test_unscored_rows_excluded_from_acc_but_sigma_uses_all():
    """correct IS NULL 행은 acc/n/n_eff에서 제외되지만 σ 평균에는 들어간다
    (σ는 그날 라벨 밴드의 상태이지 채점 여부와 무관하다)."""
    rows = [
        _row("2026-08-18 09:00:00", -1, -1, 1, sigma=0.10),
        _row("2026-08-18 09:30:00", 1, None, None, sigma=0.20),
    ]
    out = summarize_live_prediction_rows(rows, h_min=10)
    assert out["n"] == 1
    assert out["n_eff"] == 1
    assert out["acc"] == 1.0
    assert out["sigma_avg"] == pytest.approx(0.15)


def test_empty_rows_return_none_not_zero():
    """미측정 ≠ 0 — 표본이 없으면 acc/sigma_avg는 None이다 (계측 4원칙 ②)."""
    out = summarize_live_prediction_rows([], h_min=10)
    assert out["acc"] is None
    assert out["sigma_avg"] is None
    assert out["n"] == 0
    assert out["n_eff"] == 0
    assert out["hit_dir"] == {}


def test_save_model_live_daily_upsert_and_readback():
    """(date, horizon) PK — 같은 날 재실행 시 행이 늘지 않고 덮어써야 한다."""
    tmp = tempfile.mktemp(suffix=".db")
    try:
        save_model_live_daily(
            "2026-08-18", "10m", live_acc=0.2083, live_n=72,
            cv_acc=0.4596, oos_acc=0.3589, n_eff=36,
            hit_dir_json='{"p-1_a-1": 9}', sigma_avg=0.129,
            clean_old_acc=0.2434, db_path=tmp,
        )
        # 재실행(값 갱신) — INSERT OR REPLACE
        save_model_live_daily(
            "2026-08-18", "10m", live_acc=0.21, live_n=72,
            db_path=tmp,
        )
        con = sqlite3.connect(tmp)
        con.row_factory = sqlite3.Row
        rows = con.execute("SELECT * FROM model_live_daily").fetchall()
        con.close()
        assert len(rows) == 1
        r = rows[0]
        assert r["date"] == "2026-08-18"
        assert r["horizon"] == "10m"
        assert r["live_acc"] == pytest.approx(0.21)
        # 두 번째 저장에서 생략된 컬럼은 NULL — "미측정"으로 남는다
        assert r["cv_acc"] is None
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def test_save_two_horizons_two_rows():
    tmp = tempfile.mktemp(suffix=".db")
    try:
        save_model_live_daily("2026-08-18", "10m", 0.2083, 72, db_path=tmp)
        save_model_live_daily("2026-08-18", "15m", 0.2128, 47, db_path=tmp)
        con = sqlite3.connect(tmp)
        n = con.execute("SELECT COUNT(*) FROM model_live_daily").fetchone()[0]
        con.close()
        assert n == 2
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
