# -*- coding: utf-8 -*-
"""[MW0601 454차 / ATB] 퍼지드 CV + ATB v2 라벨링 + DSR/PBO 회귀 테스트.

무엇을 잠그는가:
  T1  _leak_overlap_count — 퍼지 없는 TimeSeriesSplit에서 누출이 실제로 검출되고
      (가드가 살아 있음), 꼬리 h_min행 퍼지 후 정확히 0이 된다.
  T2  _run_cv_folds 스모크 — 퍼지 적용 상태로 정상 완주 + cv_acc 산출.
  T3  세션 클립 — 수직 배리어가 15:10(절대원칙 §1)을 넘지 않는다.
  T4  동시터치 보수 처리 — 같은 봉에서 TP·SL 동시 터치 시 손절(DOWN) 우선.
  T5  min_edge — 익절폭 < 왕복비용 이벤트가 실제로 폐기된다.
  T6  고유성/수익귀속 가중치 — 완전 중복=0.5, 완전 독립=1.0, 큰 움직임에 큰 배점.
  T7  purged_event_splits — leakage_selftest_events 전 폴드 overlap 0.
  T8  DSR — n_trials 증가 시 단조 하락(시도 수 벌점이 실제로 작동).
  T9  PBO — 순수 노이즈 → 높음(과적합 검출), 지배 전략 존재 → 낮음.
  T10 WFA dsr_advisory — 판정(passed) 무영향으로 병기되고 필수 키가 존재.

실행: python tests/test_454_purged_cv_atb.py   (COM/브로커/DB 불필요)
"""
import datetime
import os
import sys

import numpy as np

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), "..")))

# Windows 콘솔(cp949)에서 em-dash 등 특수문자 출력 크래시 방지
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

FAILURES = []


def check(name, cond):
    status = "PASS" if cond else "FAIL"
    print("[%s] %s" % (status, name))
    if not cond:
        FAILURES.append(name)


# ── T1/T2: 퍼지드 CV ─────────────────────────────────────────────


def test_1_leak_overlap_count():
    from sklearn.model_selection import TimeSeriesSplit
    from learning.batch_retrainer import _leak_overlap_count

    h_min = 30
    n = 1000
    tscv = TimeSeriesSplit(n_splits=3)
    X = np.zeros((n, 2))
    for train_idx, val_idx in tscv.split(X):
        raw = _leak_overlap_count(train_idx, val_idx, h_min)
        check("T1: 퍼지 전 누출 검출 (fold overlap=%d > 0)" % raw, raw > 0)
        check("T1: 퍼지 전 누출량 = h_min (경계 %d행)" % h_min, raw == h_min)
        purged = train_idx[:-h_min]
        check("T1: 꼬리 %d행 퍼지 후 overlap=0" % h_min,
              _leak_overlap_count(purged, val_idx, h_min) == 0)
    check("T1: h_min=0이면 항상 0 (1m 등가 아님 — 1m은 h_min=1)",
          _leak_overlap_count(np.arange(10), np.arange(10, 20), 0) == 0)
    check("T1: 빈 train → 0",
          _leak_overlap_count(np.array([]), np.arange(5), 5) == 0)


def test_2_run_cv_folds_smoke():
    from sklearn.tree import DecisionTreeClassifier
    from learning.batch_retrainer import BatchRetrainer

    rng = np.random.default_rng(42)
    n = 900
    X = rng.normal(size=(n, 4)).astype(np.float32)
    y = rng.choice([-1, 0, 1], size=n)

    cv_accs, val_idx = BatchRetrainer._run_cv_folds(
        None, X, y, None, None, "30m", True,
        lambda: DecisionTreeClassifier(max_depth=2, random_state=0),
    )
    check("T2: 퍼지 적용 _run_cv_folds 정상 완주 (folds=%d)" % len(cv_accs),
          len(cv_accs) == 3)
    check("T2: val 인덱스 수집 유지 (incumbent 재채점 경로 보존)",
          len(val_idx) > 0)


# ── T3~T7: ATB 라벨링 ────────────────────────────────────────────


def _make_candles(day, prices, start_hh=9, start_mm=0):
    """분 간격 합성 분봉. prices[i] → close, high=close+0.5, low=close-0.5 기본."""
    out = []
    t0 = datetime.datetime(2026, 8, day, start_hh, start_mm, 0)
    for i, p in enumerate(prices):
        ts = (t0 + datetime.timedelta(minutes=i)).strftime("%Y-%m-%d %H:%M:%S")
        out.append({"ts": ts, "high": p + 0.5, "low": p - 0.5, "close": p})
    return out


def test_3_session_clip():
    from model.atb_labeling import effective_horizon_minutes

    check("T3: 14:50 + 30m → 20분으로 클립",
          effective_horizon_minutes("2026-08-07 14:50:00", 30) == 20)
    check("T3: 14:30 + 30m → 클립 없음(30)",
          effective_horizon_minutes("2026-08-07 14:30:00", 30) == 30)
    check("T3: 15:09 + 30m → 1분",
          effective_horizon_minutes("2026-08-07 15:09:00", 30) == 1)
    check("T3: 15:10 정각 → 0 (라벨 불가)",
          effective_horizon_minutes("2026-08-07 15:10:00", 30) <= 0)
    check("T3: 15:11 → 음수 (라벨 불가)",
          effective_horizon_minutes("2026-08-07 15:11:00", 30) < 0)


def test_4_conservative_same_bar():
    from model.atb_labeling import build_atb_labels
    from config.constants import DIRECTION_DOWN

    # 평탄한 가격 후 큰 하락 이벤트 → CUSUM 발동 지점 뒤에 TP/SL 동시 터치 봉 배치
    prices = [400.0] * 60 + [396.0] + [396.0] * 5
    candles = _make_candles(7, prices)
    # 동시터치 봉: 이벤트 직후 봉의 고가/저가를 극단으로
    candles[62]["high"] = 430.0
    candles[62]["low"] = 370.0
    res = build_atb_labels(candles, h_min=5, cusum_k=1.0, stop_mult=1.5,
                           tp_mult=3.0, min_edge_pt=0.0)
    same_bar = [lb for lb in res["labels"]
                if lb["touch_minute"] is not None and lb["ts"] == candles[61]["ts"]]
    if not same_bar:
        # CUSUM 이벤트 위치가 다를 수 있으므로 동시터치 라벨을 전수 검색
        same_bar = [lb for lb in res["labels"]
                    if lb["t1_ts"] == candles[62]["ts"]]
    check("T4: 동시터치 봉 라벨 존재", len(same_bar) > 0)
    check("T4: 동시터치 → 손절(DOWN) 우선",
          all(lb["label"] == DIRECTION_DOWN for lb in same_bar))


def test_5_min_edge():
    from model.atb_labeling import build_atb_labels

    # 저변동(ATR 작음) 시장 — min_edge를 크게 주면 전부 폐기돼야 한다
    rng = np.random.default_rng(1)
    prices = 400.0 + np.cumsum(rng.normal(0, 0.05, size=500))
    candles = _make_candles(7, list(prices))
    res = build_atb_labels(candles, h_min=5, cusum_k=1.0, stop_mult=1.5,
                           tp_mult=3.0, min_edge_pt=50.0)
    check("T5: min_edge 폐기 발생 (dropped=%d)"
          % res["stats"]["n_dropped_edge"], res["stats"]["n_dropped_edge"] > 0)
    check("T5: 폐기된 이벤트는 라벨에 없음", len(res["labels"]) == 0)


def test_6_uniqueness_and_attribution():
    from model.atb_labeling import (
        average_uniqueness, return_attribution_weights,
    )

    # 완전 중복 라벨 2개 → 고유성 0.5 / 완전 분리 → 1.0
    dup = [{"i0": 0, "i1": 9}, {"i0": 0, "i1": 9}]
    u = average_uniqueness(20, dup)
    check("T6: 완전 중복 2개 → 고유성 0.5", np.allclose(u, 0.5))
    sep = [{"i0": 0, "i1": 4}, {"i0": 10, "i1": 14}]
    u2 = average_uniqueness(20, sep)
    check("T6: 완전 분리 → 고유성 1.0", np.allclose(u2, 1.0))

    # 수익귀속 — 크게 움직인 구간의 라벨이 더 큰 배점
    closes = [100.0] * 5 + [100.0, 101.0, 102.0, 103.0, 104.0] + [104.0] * 10
    labels = [{"i0": 1, "i1": 3},   # 무변동 구간
              {"i0": 5, "i1": 9}]   # 급등 구간
    w = return_attribution_weights(closes, labels)
    check("T6: 급등 구간 배점 > 무변동 구간 배점", w[1] > w[0])


def test_7_purged_event_splits():
    from model.atb_labeling import purged_event_splits, leakage_selftest_events

    rng = np.random.default_rng(2)
    # 비등간격 이벤트 + 구간 겹침이 있는 라벨 시뮬레이션
    i0s = np.sort(rng.choice(np.arange(0, 2000), size=120, replace=False))
    labels = [{"i0": int(i), "i1": int(i + rng.integers(1, 30))} for i in i0s]
    rows = leakage_selftest_events(labels, n_splits=3)
    check("T7: 폴드 3개 생성", len(rows) == 3)
    check("T7: 전 폴드 overlap=0 (%s)"
          % [r["overlap_count"] for r in rows], all(r["ok"] for r in rows))
    for tr, va in purged_event_splits(labels, n_splits=3):
        check("T7: train·val 교집합 없음",
              len(set(tr.tolist()) & set(va.tolist())) == 0)
        break


# ── T8~T9: DSR / PBO ─────────────────────────────────────────────


def test_8_dsr_monotonic_in_trials():
    from learning.validation_stats import deflated_sharpe_ratio

    rng = np.random.default_rng(3)
    ret = list(rng.normal(0.002, 0.01, size=104))  # 약한 양의 엣지, 2년 주간
    d1 = deflated_sharpe_ratio(ret, n_trials=1, periods_per_year=52)
    d100 = deflated_sharpe_ratio(ret, n_trials=100, periods_per_year=52,
                                 var_sharpe=0.02)
    check("T8: DSR ∈ [0,1] (n=1: %.3f)" % d1["dsr"], 0.0 <= d1["dsr"] <= 1.0)
    check("T8: 시도 수 벌점 — n_trials=100이 n=1보다 낮음 (%.3f < %.3f)"
          % (d100["dsr"], d1["dsr"]), d100["dsr"] < d1["dsr"])
    check("T8: sr_threshold 양수 (n=100)", d100["sr_threshold"] > 0)
    d_short = deflated_sharpe_ratio([0.01, 0.02], n_trials=1)
    check("T8: 표본 3개 미만 → dsr=0·pass=False",
          d_short["dsr"] == 0.0 and d_short["pass"] is False)


def test_9_pbo():
    from learning.validation_stats import probability_of_backtest_overfitting

    rng = np.random.default_rng(4)
    # 순수 노이즈 10전략 → 선택 과정이 과적합 (PBO 높음)
    noise = rng.normal(0, 1, size=(240, 10))
    p_noise = probability_of_backtest_overfitting(noise, n_splits=12)
    check("T9: 노이즈 PBO 높음 (%.2f > 0.2)" % p_noise["pbo"],
          p_noise["pbo"] > 0.2)
    # 지배 전략(높은 평균·낮은 분산) 존재 → PBO 낮음
    skill = rng.normal(0, 1, size=(240, 10))
    skill[:, 0] = rng.normal(1.0, 0.1, size=240)
    p_skill = probability_of_backtest_overfitting(skill, n_splits=12)
    check("T9: 지배 전략 PBO 낮음 (%.2f < 0.2)" % p_skill["pbo"],
          p_skill["pbo"] < 0.2)
    err = probability_of_backtest_overfitting(np.zeros((10, 1)), n_splits=12)
    check("T9: 전략 1개 → 판정불가 error", "error" in err)


def test_10_wfa_dsr_advisory():
    from backtest.walk_forward import WalkForwardValidator

    rng = np.random.default_rng(5)
    weekly = []
    for _ in range(30):
        week = [{"pnl_krw": float(rng.normal(50000, 150000)), "win": bool(rng.random() < 0.55)}
                for _ in range(rng.integers(3, 8))]
        weekly.append(week)
    v = WalkForwardValidator()
    r = v.run(weekly, n_trials=5)
    check("T10: dsr_advisory 병기됨", "dsr_advisory" in r)
    adv = r["dsr_advisory"]
    ok_keys = ("error" in adv) or all(
        k in adv for k in ("dsr", "sharpe", "sr_threshold", "n_trials"))
    check("T10: advisory 필수 키 존재 (%s)" % sorted(adv.keys()), ok_keys)
    check("T10: passed 판정은 criteria_check에서만 나옴 (advisory 무영향)",
          r["passed"] == r["criteria_check"]["pass_all"])


if __name__ == "__main__":
    _fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in _fns:
        try:
            fn()
        except Exception as e:
            import traceback
            traceback.print_exc()
            FAILURES.append("%s: %r" % (fn.__name__, e))
            print("[FAIL] %s: %r" % (fn.__name__, e))
    print("-" * 60)
    if FAILURES:
        print("실패 %d건: %s" % (len(FAILURES), FAILURES))
        sys.exit(1)
    print("전부 통과")
