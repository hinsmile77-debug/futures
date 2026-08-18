# -*- coding: utf-8 -*-
"""[MW0601 477차 후속 / 476차 F-1·F-5] DriftAdjuster 포화 가시화 + PSI 매분 영속.

F-1: alpha가 상한/하한 포화 상태에서 "0.01000→0.01000" 같은 형식적 조정문 대신
     SATURATED_MAX/MIN 액션과 연속일수를 남긴다(계측 4원칙 ④).
F-5: ensemble_decisions INSERT 2경로의 컬럼/플레이스홀더/파라미터 수 일치와
     fp_psi/fp_level 배선을 고정한다(컬럼 하나 추가할 때마다 3곳이 어긋나는 사고 방지).
"""
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from learning.self_learning.drift_adjuster import (
    DriftAdjuster, ALPHA_MAX, ALPHA_MIN, ALPHA_DEFAULT,
)


def _adj(tmp_path):
    return DriftAdjuster(path=os.path.join(str(tmp_path), "drift_state.json"))


# ── F-1: 포화 가시화 ─────────────────────────────────────────────


def test_saturated_max_action_and_streak(tmp_path):
    adj = _adj(tmp_path)
    adj._alpha = ALPHA_MAX
    r1 = adj.record_accuracy(0.20, n_samples=100)   # 이력 1일 — HOLD
    r2 = adj.record_accuracy(0.25, n_samples=100)   # 이력 2일 — HOLD
    r3 = adj.record_accuracy(0.15, n_samples=100)   # 3일 연속 <0.50 — 포화
    r4 = adj.record_accuracy(0.30, n_samples=100)
    assert r1["action"] == "HOLD" and r2["action"] == "HOLD"
    assert r3["action"] == "SATURATED_MAX"
    assert r4["action"] == "SATURATED_MAX"
    assert adj.get_alpha() == ALPHA_MAX             # 값은 불변 — 표기만 진실해진다
    st = adj.get_status()
    assert st["saturated"] is True
    assert st["saturated_days"] == 2


def test_saturated_min_on_recovery_side(tmp_path):
    adj = _adj(tmp_path)
    adj._alpha = ALPHA_MIN
    adj.record_accuracy(0.60, n_samples=100)        # 이력 1일 — HOLD
    r2 = adj.record_accuracy(0.65, n_samples=100)   # 2일 연속 >=0.58 — 포화
    assert r2["action"] == "SATURATED_MIN"
    assert adj.get_alpha() == ALPHA_MIN
    assert adj.get_status()["saturated_days"] == 1


def test_normal_drift_up_not_saturated(tmp_path):
    adj = _adj(tmp_path)
    assert adj.get_alpha() == ALPHA_DEFAULT
    adj.record_accuracy(0.20, n_samples=100)
    adj.record_accuracy(0.20, n_samples=100)
    r3 = adj.record_accuracy(0.20, n_samples=100)
    assert r3["action"] == "DRIFT_UP"               # 0.001→0.0015, 포화 아님
    assert adj.get_alpha() == pytest.approx(ALPHA_DEFAULT * 1.5)
    assert adj.get_status()["saturated_days"] == 0
    assert adj.get_status()["saturated"] is False


def test_hold_resets_streak(tmp_path):
    adj = _adj(tmp_path)
    adj._alpha = ALPHA_MAX
    adj.record_accuracy(0.20, n_samples=100)
    adj.record_accuracy(0.20, n_samples=100)
    adj.record_accuracy(0.20, n_samples=100)        # SATURATED_MAX (streak 1)
    r = adj.record_accuracy(0.55, n_samples=100)    # 하락 연속 끊김·회복 미달 — HOLD
    assert r["action"] == "HOLD"
    assert adj.get_status()["saturated_days"] == 0


def test_skip_low_sample_keeps_streak(tmp_path):
    """표본부족 스킵은 판정이 없던 날 — 포화 연속일수를 건드리지 않는다."""
    adj = _adj(tmp_path)
    adj._alpha = ALPHA_MAX
    adj.record_accuracy(0.20, n_samples=100)
    adj.record_accuracy(0.20, n_samples=100)
    adj.record_accuracy(0.20, n_samples=100)        # streak 1
    adj.record_accuracy(0.20, n_samples=3)          # SKIP_LOW_SAMPLE
    assert adj.get_status()["saturated_days"] == 1


def test_saturated_days_persisted_across_reload(tmp_path):
    p = os.path.join(str(tmp_path), "drift_state.json")
    adj = DriftAdjuster(path=p)
    adj._alpha = ALPHA_MAX
    adj.record_accuracy(0.20, n_samples=100)
    adj.record_accuracy(0.20, n_samples=100)
    adj.record_accuracy(0.20, n_samples=100)        # streak 1, _save() 호출됨
    adj2 = DriftAdjuster(path=p)
    assert adj2.get_status()["saturated_days"] == 1
    assert adj2.get_status()["action"] == "SATURATED_MAX"


def test_legacy_state_without_key_defaults_zero(tmp_path):
    import json
    p = os.path.join(str(tmp_path), "drift_state.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump({"alpha": 0.01, "acc_history": [0.2], "last_action": "DRIFT_UP"}, f)
    adj = DriftAdjuster(path=p)
    assert adj.get_status()["saturated_days"] == 0


# ── F-5: INSERT 배선 정합 ─────────────────────────────────────────


class _FakeCursor(object):
    def __init__(self, sink):
        self._sink = sink

    def execute(self, sql, params=()):
        self._sink.append((sql, params))

    def executemany(self, sql, rows):
        for r in rows:
            self._sink.append((sql, r))


class _FakeConnCtx(object):
    def __init__(self, sink):
        self._sink = sink

    def __enter__(self):
        return _FakeCursor(self._sink)

    def __exit__(self, *a):
        return False


def _decision_stub():
    return {
        "direction": -1, "confidence": 0.4, "grade": "A",
        "fp_psi": 0.008, "fp_level": 0,
    }


def test_step9_batch_placeholders_match_params(monkeypatch):
    import learning.prediction_buffer as pb
    calls = []
    monkeypatch.setattr(pb, "get_conn", lambda *a, **k: _FakeConnCtx(calls))
    buf = pb.PredictionBuffer()
    buf.save_step9_batch(
        ts="2026-08-18 10:00:00", sigma_at_t=0.12,
        horizon_proba={"1m": {"direction": 1, "confidence": 0.4}},
        features_clean={"f": 1.0}, regime="NEUTRAL", micro_regime="calm",
        decision=_decision_stub(),
    )
    ens = [c for c in calls if "ensemble_decisions" in c[0]]
    assert len(ens) == 1
    sql, params = ens[0]
    assert sql.count("?") == len(params), (
        "플레이스홀더 %d개 != 파라미터 %d개" % (sql.count("?"), len(params)))
    assert "fp_psi" in sql and "fp_level" in sql
    cols = sql.split("(", 1)[1].split(") VALUES")[0]
    n_cols = len([c for c in cols.split(",") if c.strip()])
    assert n_cols == len(params), (
        "컬럼 %d개 != 파라미터 %d개" % (n_cols, len(params)))
    # fp 값이 실제로 실렸는지 — 마지막 두 파라미터
    assert params[-2] == pytest.approx(0.008)
    assert params[-1] == 0


def test_step9_batch_fp_none_becomes_null(monkeypatch):
    import learning.prediction_buffer as pb
    calls = []
    monkeypatch.setattr(pb, "get_conn", lambda *a, **k: _FakeConnCtx(calls))
    buf = pb.PredictionBuffer()
    d = _decision_stub()
    d["fp_psi"] = d["fp_level"] = None     # update_live 예외 분 — NULL(미측정)
    buf.save_step9_batch(
        ts="2026-08-18 10:01:00", sigma_at_t=0.12, horizon_proba={},
        features_clean={}, regime="NEUTRAL", micro_regime="calm", decision=d,
    )
    sql, params = [c for c in calls if "ensemble_decisions" in c[0]][0]
    assert params[-2] is None and params[-1] is None


def test_fallback_save_ensemble_decision_placeholders(monkeypatch):
    import learning.prediction_buffer as pb
    calls = []
    monkeypatch.setattr(pb, "execute", lambda db, sql, params=(): calls.append((sql, params)))
    buf = pb.PredictionBuffer()
    buf.save_ensemble_decision(
        ts="2026-08-18 10:02:00", regime="NEUTRAL", micro_regime="calm",
        decision=_decision_stub(), features={"f": 1.0},
    )
    sql, params = calls[0]
    assert sql.count("?") == len(params)
    assert "fp_psi" in sql and "fp_level" in sql
    assert params[-2] == pytest.approx(0.008) and params[-1] == 0
