# -*- coding: utf-8 -*-
"""[MW0601 455차] 다중 호라이즌 피처 평가 P1~P6 회귀 테스트.

무엇을 잠그는가:
  T1  L4 two-proportion z — 손계산 대조 + 대칭성.
  T2  L4 analyze — 판정 어휘(INSUFFICIENT/ANTI_CALIBRATION/NO_SKILL/OK)와
      JSON 계약 키(acc_low/n_low/acc_high/n_high/z/p/verdict), 버킷 합 = 전체.
  T3  L2 비용 산식 — generate_validation_campaign_report._roundtrip_cost_pt(정본)와 동일.
  T4  L2 RunningMedian — numpy median과 일치(past-only 구조 자체가 미래참조 차단).
  T5  L2 미래참조 부재 — 마지막 봉 피처값을 바꿔도 그 앞 거래 결과 불변.
  T6  L2 비중복 — 거래 간격이 항상 h 이상.
  T7  N1 — E[z|top5%]≈2.063, norm_ppf(0.975)≈1.96, IC*(h) ∝ 1/√h.
  T8  N3 — 시드 재현성 / 셔플 분포 보존 / phase 길이·NaN 위치 보존 / noise_floor.
  T9  N2 classify — 단조감쇠/봉우리/부호반전/무정보 4유형 + fit_tau가 정확한 τ 복원.
  T10 N2 analyze_curves — 합성 "완전 1분 신호"가 peak_h=1·양의 IC로 잡힌다.
  T11 N5 — 합성 bounce(종가에만 인공 진동)가 IC_close에서만 잡히고 IC_open≈0.

실행: python tests/test_455_multi_hz_feature_eval.py   (DB/브로커 불필요, 읽기 전용)
"""
import math
import os
import sys
from collections import OrderedDict

import numpy as np

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), "..")))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

FAILURES = []
N_CHECKS = [0]


def check(name, cond):
    N_CHECKS[0] += 1
    status = "PASS" if cond else "FAIL"
    print("[%s] %s" % (status, name))
    if not cond:
        FAILURES.append(name)


# ── T1/T2: L4 ──────────────────────────────────────────────────────────────────
import scripts.horizon_conf_stratified_test as l4

z, p = l4.two_prop_z(50, 100, 60, 100)  # 0.50 vs 0.60
# 손계산: pool=0.55, se=sqrt(0.55*0.45*(2/100))=0.070356..., z=0.10/0.070356=1.4213
check("T1a z 손계산 대조 (0.50 vs 0.60, n=100/100)", abs(z - 1.4213) < 0.001)
check("T1b p 양측 (≈0.1553)", abs(p - 0.1553) < 0.002)
z2, _ = l4.two_prop_z(60, 100, 50, 100)
check("T1c 대칭성 z(a,b) = -z(b,a)", abs(z + z2) < 1e-12)

# 합성 rows: (date, horizon, direction, confidence, actual)
rows = []
dates = ["2026-08-%02d" % d for d in range(1, 13)]  # 12일 (min_days=10 충족)
rng = np.random.RandomState(7)
for d in dates:
    for _ in range(30):  # 저conf: acc 60%
        hit = rng.rand() < 0.60
        rows.append((d, "5m", 1, 0.50, 1 if hit else -1))
    for _ in range(20):  # 고conf: acc 30% (역보정) — n_high 12*20=240 >= 100
        hit = rng.rand() < 0.30
        rows.append((d, "5m", 1, 0.60, 1 if hit else -1))
    for _ in range(3):   # 3m: 고conf 표본 부족 → INSUFFICIENT
        rows.append((d, "3m", 1, 0.60, 1))
res, alpha_adj = l4.analyze(rows, dates)
r5 = res["5m"]
check("T2a 5m 역보정 검출", r5["verdict"] == "ANTI_CALIBRATION" and r5["z"] < 0)
check("T2b 계약 키 존재", all(k in r5 for k in
                              ("acc_low", "n_low", "acc_high", "n_high", "z", "p", "verdict")))
check("T2c 버킷 합 = 전체", sum(b["n"] for b in r5["buckets"]) == r5["n_low"] + r5["n_high"])
check("T2d 3m INSUFFICIENT (n_high<100)", res["3m"]["verdict"] == "INSUFFICIENT")
check("T2e Bonferroni 보정 (α/호라이즌수)", abs(alpha_adj - l4.ALPHA / len(l4.HORIZONS)) < 1e-12)

# ── T3~T6: L2 ─────────────────────────────────────────────────────────────────
import scripts.horizon_signal_tradability as l2

try:
    from scripts.generate_validation_campaign_report import _roundtrip_cost_pt as canon
    same = all(abs(l2.roundtrip_cost_pt(p_) - canon(p_)) < 1e-12
               for p_ in (300.0, 415.0, 1037.0, 1300.0))
    check("T3 비용 산식 = 캠페인 정본", same)
except Exception as e:  # 정본 모듈 import 실패 시 명시적으로 FAIL
    check("T3 비용 산식 = 캠페인 정본 (import 실패: %s)" % e, False)

rm = l2.RunningMedian()
vals = [3.0, 1.0, 4.0, 1.0, 5.0, 9.0, 2.0]
oks = True
for i, v in enumerate(vals):
    rm.push(v)
    oks = oks and abs(rm.median() - float(np.median(vals[:i + 1]))) < 1e-12
check("T4 RunningMedian = numpy median (past-only)", oks)

# 합성 1일: 10봉, h=2
day_rows = {"2026-08-03": list(range(10))}
closes_by_i = {i: 100.0 + i for i in range(10)}  # 단조 상승
col = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], dtype=np.float64)  # 항상 중앙값 이상
g1, t1 = l2.simulate_feature(day_rows, col, closes_by_i, 2)
col2 = col.copy()
col2[9] = -999.0  # 마지막 봉만 변경 — 거래 불가 위치(k+h>=len)
g2, t2 = l2.simulate_feature(day_rows, col2, closes_by_i, 2)
check("T5 미래참조 부재 — 마지막 봉 변경이 결과 불변", g1 == g2 and t1 == t2)
# T6 비중복: h=2, 첫 신호는 k=1(중앙값 초과)부터 — 간격 2 확인 (거래수로 검증)
# k=1 진입→k=3, k=3→k=5, k=5→k=7, k=7→k=9 : 4건 (k=9는 k+h>=len 불가)
check("T6 비중복 간격 (10봉 h=2 → 4건)", t1["2026-08-03"] == 4)

# ── T7: N1 ────────────────────────────────────────────────────────────────────
import scripts.ic_cost_hurdle_table as n1

check("T7a E[z|top5%] ≈ 2.063", abs(n1.ez_top(0.05) - 2.0627) < 0.005)
check("T7b norm_ppf(0.975) ≈ 1.95996", abs(n1.norm_ppf(0.975) - 1.95996) < 1e-4)
c_, ez = 0.07, n1.ez_top(0.05)
ic1 = c_ / (ez * 1.0 * math.sqrt(1))
ic4 = c_ / (ez * 1.0 * math.sqrt(4))
check("T7c IC*(h) ∝ 1/√h (h 4배 → 문턱 절반)", abs(ic1 / ic4 - 2.0) < 1e-9)

# ── T8: N3 ────────────────────────────────────────────────────────────────────
from scripts.noise_benchmark import (make_noise_features, noise_floor,
                                     shuffle_column, phase_randomize, is_noise_name)

base = np.sin(np.arange(300) * 0.1) + np.arange(300) * 0.01
base[5] = np.nan
cols = OrderedDict([("feat_a", base), ("feat_b", base * -2.0 + 1.0)])
nz1 = make_noise_features(cols, seed=20260809)
nz2 = make_noise_features(cols, seed=20260809)
nz3 = make_noise_features(cols, seed=20260810)
check("T8a 시드 재현성 (같은 시드 → 동일)",
      all(np.array_equal(nz1[k], nz2[k], equal_nan=True) for k in nz1))
check("T8b 다른 시드 → 다름",
      any(not np.array_equal(nz1[k], nz3[k], equal_nan=True) for k in nz1))
sh = shuffle_column(base, np.random.RandomState(1))
check("T8c 셔플 분포 보존 (정렬 동일 + NaN 위치 보존)",
      np.allclose(np.sort(sh[~np.isnan(sh)]), np.sort(base[~np.isnan(base)]))
      and np.isnan(sh[5]))
ph = phase_randomize(base, np.random.RandomState(2))
check("T8d phase 길이·NaN 위치 보존", ph.size == base.size and np.isnan(ph[5])
      and np.isfinite(ph[~np.isnan(base)]).all())
fl, fn = noise_floor([{"name": "noise_shuf1_x", "ic_t": 1.5},
                      {"name": "noise_phase1_y", "ic_t": -2.5},
                      {"name": "real", "ic_t": 9.9}], stat_key="ic_t")
check("T8e noise_floor는 노이즈 중 max|t| (실피처 무시)", abs(fl - 2.5) < 1e-12
      and fn == "noise_phase1_y" and is_noise_name(fn))

# ── T9/T10: N2 ────────────────────────────────────────────────────────────────
import scripts.ic_decay_catalog as n2

GRID = [1, 3, 5, 10, 15, 30]


def mk_curve(ics, ts):
    return {h: {"ic": ics[i], "t": ts[i], "n_days": 30, "ic_norm": ics[i], "t_norm": ts[i]}
            for i, h in enumerate(GRID)}


bonf_t = 3.5
c_mono = mk_curve([0.10, 0.07, 0.05, 0.03, 0.02, 0.01], [6, 5, 4, 3, 2.5, 2])
c_hump = mk_curve([0.01, 0.03, 0.06, 0.09, 0.06, 0.03], [1, 2.5, 4, 6, 4, 2.5])
c_flip = mk_curve([0.06, 0.03, 0.00, -0.03, -0.05, -0.06], [4, 2.5, 0.1, -2.2, -3.6, -4])
c_none = mk_curve([0.01, -0.01, 0.005, 0.002, -0.003, 0.001], [0.5, -0.6, 0.3, 0.2, -0.2, 0.1])
c_rise = mk_curve([0.01, 0.02, 0.04, 0.07, 0.10, 0.15], [1, 2, 3, 4.5, 5.5, 7])
check("T9a 단조감쇠", n2.classify(c_mono, GRID, bonf_t)[0] == "단조감쇠")
check("T9b 봉우리", n2.classify(c_hump, GRID, bonf_t)[0] == "봉우리")
check("T9c 부호반전", n2.classify(c_flip, GRID, bonf_t)[0] == "부호반전")
check("T9d 무정보", n2.classify(c_none, GRID, bonf_t)[0] == "무정보")
check("T9d2 증가형 (peak=격자 끝)", n2.classify(c_rise, GRID, bonf_t)[0] == "증가형")
# fit_tau: 정확한 지수 IC(h)=0.1·e^(-h/10) → τ=10 복원
tau_true = 10.0
c_exp = mk_curve([0.1 * math.exp(-h / tau_true) for h in GRID], [5] * 6)
tau, hl, r2 = n2.fit_tau(c_exp, GRID, 1)
check("T9e fit_tau τ 복원 (10±0.1, R²>0.999)",
      tau is not None and abs(tau - tau_true) < 0.1 and r2 > 0.999)
check("T9f 반감기 = τ·ln2", hl is not None and abs(hl - tau_true * math.log(2)) < 0.1)

# T10: 합성 25일 × 150봉 — 피처 = 다음 1분 변화 + 약한 노이즈 → peak_h=1
rng = np.random.RandomState(42)
feats_ts, X_rows, closes_map = [], [], {}
for d in range(25):
    date = "2026-07-%02d" % (d + 1)
    px = 400.0 + np.cumsum(rng.randn(151) * 0.1)
    for i in range(150):
        ts = "%s 09:%02d:%02d" % (date, i // 60, i % 60)  # 형식만 맞으면 됨 (일자 그룹핑)
        feats_ts.append(ts)
        closes_map[ts] = float(px[i])
        X_rows.append([float(px[i + 1] - px[i]) + rng.randn() * 0.02])
X_syn = np.array(X_rows, dtype=np.float64)
curves, rho1_med, n_days = n2.analyze_curves(["perfect_1m"], X_syn, feats_ts,
                                             closes_map, [1, 3, 5])
c1 = curves["perfect_1m"]
check("T10a 합성 1분 신호 — h=1 IC 강한 양수", c1[1]["ic"] > 0.5 and c1[1]["t"] > 10)
check("T10b 감쇠 — IC(1) > IC(3) > IC(5) > 0",
      c1[1]["ic"] > c1[3]["ic"] > c1[5]["ic"] > -0.05)
check("T10c 유효일수 = 25", n_days == 25)

# ── T11: N5 ───────────────────────────────────────────────────────────────────
import scripts.bounce_artifact_check as n5

rng = np.random.RandomState(9)
feats_b, candles_b = [], {}
for d in range(20):
    date = "2026-06-%02d" % (d + 1)
    mid = 400.0 + np.cumsum(rng.randn(121) * 0.1)
    s = rng.randn(121)  # "마이크로 피처" — 연속값 순수 노이즈 (이진이면 unique<3 가드에 걸림)
    tick = 0.05
    for i in range(120):
        ts = "%s 10:%02d:%02d" % (date, i // 60, i % 60)
        feats_b.append((ts, [float(s[i])]))
        # 종가에만 bounce: close = mid + tick·sign(s) (피처와 기계적 상관), open·mid는 무오염
        candles_b[ts] = (float(mid[i]), float(mid[i] + tick * np.sign(s[i])), float(mid[i]))
res_b, mid_cov = n5.analyze(feats_b, candles_b, ["noise_micro"], 1)
r = res_b["noise_micro"]
# fwd_close = Δmid + tick(s[t+1]−s[t]) → corr(s[t], fwd_close) < 0 (−tick·s[t] 항) —
# 부호와 무관하게 |IC_close|가 뚜렷하고 IC_open은 0 근방이어야 한다
check("T11a bounce가 IC_close에 잡힘 (|IC|>0.15)", abs(r["close"]["ic"]) > 0.15)
check("T11b IC_open ≈ 0 (무오염 타겟)", abs(r["open"]["ic"]) < 0.05)
check("T11c mid 커버리지 100%", mid_cov > 0.99)
check("T11d IC_mid ≈ 0", abs(r["mid"]["ic"]) < 0.05)

print()
if FAILURES:
    print("FAILED %d/%d: %s" % (len(FAILURES), N_CHECKS[0], ", ".join(FAILURES)))
    sys.exit(1)
print("ALL PASS (%d checks)" % N_CHECKS[0])
