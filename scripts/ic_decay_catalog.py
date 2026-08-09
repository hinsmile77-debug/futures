# -*- coding: utf-8 -*-
"""[MW0601 455차 / N2] IC 감쇠 곡선 전 격자 카탈로그 — 피처별 (peak_h, τ, 유형) 사전.

기존 `core_feature_discovery.py`(h=5/15/30 3점 스냅샷)와의 차이:
  · 전 격자 h ∈ {1,3,5,10,15,30} — 감쇠 "곡선"을 그린다 (부호 유지, 절댓값 금지)
  · 요약 통계: peak_h · 지수 피팅 τ(반감기 τ·ln2) · R² · 유형 분류
  · 유형 5종: 단조감쇠(peak=h1) / 봉우리(peak 내부) / **증가형**(peak=격자 끝 — 진짜
    피크는 격자 밖, 일 단위 공변동 의심 → L2 함정 경고와 함께 읽기) / **부호반전**
    (반대 부호 두 h가 |t|≥2) / 무정보(전 h Bonferroni 미달)
  · **부호반전형은 진입 후보가 아니라 "청산/역추세 후보"로 별도 섹션 출력** — 되돌림
    알파는 청산 축([41] 계열)·챌린저 계층의 입력이다(검토보고 §5-B)
  · 변동성 정규화 병행 열 — 일중 U자형 변동성 왜곡 감지(원시 타겟 정의는 무변경)
  · 노이즈 벤치마크 5종 상시 포함(N3) + 하한선
  · 회전율 프록시 — 일중 lag-1 자기상관 ρ₁ → turnover ≈ √(2(1−ρ₁))

방법론은 core_feature_discovery와 동일(일자단위 독립관측·Bonferroni·split-half —
함수 재사용). 사전등록 값은 `config/settings.py:VALIDATION_CAMPAIGN["ic_decay_catalog"]`
— 기존 3점 채널과 별개 가족이므로 판정을 섞지 않는다.

⚠ advisory 전용: 어떤 산출도 채택/탈락 효력이 없다. ADD/DROP 제안은 Phase C 월간
리포트 + L3 배터리 + 사람 승인 경로로만(§6 자동 통합 금지).

읽기 전용: raw_data.db만 읽는다. 출력: stdout + data/ic_decay/ic_decay_catalog_YYYYMMDD.{json,md}
(런타임 산출물 — 커밋 금지). 실행: 월간 수동(py310_64 권장) → Phase C 편입 예정.
"""
from __future__ import print_function

import argparse
import datetime
import io
import json
import math
import os
import sys
from collections import OrderedDict, defaultdict

import numpy as np

_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# [448차 패턴] BLAS DLL 경로 보장 — 반드시 numpy 첫 사용 전. conda 미활성 직접 실행 시
# MKL 지연로드가 0xC06D007F로 프로세스를 즉사시킨다 (455차 재확인: np.polyfit).
from utils.dll_bootstrap import ensure_conda_dll_path  # noqa: E402
ensure_conda_dll_path()

def _utf8_console():
    """cp949 콘솔 인코딩 가드 — CLI 실행 시에만 (import 시 래핑하면 중첩 래퍼로 출력 유실)."""
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from config.settings import VALIDATION_CAMPAIGN  # noqa: E402
from scripts.core_feature_discovery import (  # noqa: E402
    load, build_matrix, rankdata, corr, tstat, MIN_DAY_ROWS,
)
from scripts.noise_benchmark import make_noise_features, is_noise_name  # noqa: E402

_CFG = VALIDATION_CAMPAIGN.get("ic_decay_catalog", {})
GRID = list(_CFG.get("grid", [1, 3, 5, 10, 15, 30]))
ALPHA = float(_CFG.get("alpha", 0.05))
SIG_T_PAIR = float(_CFG.get("sig_t_pair", 2.0))
MIN_DAYS = int(_CFG.get("min_days", 20))
TAU_MIN_POINTS = int(_CFG.get("tau_min_points", 3))
N_SHUFFLE = int(_CFG.get("noise_shuffle", 3))
N_PHASE = int(_CFG.get("noise_phase", 2))

EWMA_LAMBDA = 0.94  # 당일 past-only 1분 변동성 EWMA (RiskMetrics 관행값)
OUT_DIR = os.path.join(_ROOT, "data", "ic_decay")


def day_sigma1_pastonly(closes_arr):
    """당일 past-only EWMA 1분 변동성. 반환 배열[i] = i 시점까지 정보만 사용한 σ₁ 추정.

    워밍업 10봉 미만은 NaN — 개장 직후는 정규화 타겟에서 자연 제외된다.
    """
    n = closes_arr.size
    out = np.full(n, np.nan)
    if n < 3:
        return out
    d = np.diff(closes_arr)
    var = None
    for i in range(1, n):
        x2 = d[i - 1] * d[i - 1]
        var = x2 if var is None else EWMA_LAMBDA * var + (1.0 - EWMA_LAMBDA) * x2
        if i >= 10 and var > 0:
            out[i] = math.sqrt(var)
    return out


def analyze_curves(names, X, ts_list, closes, grid):
    """피처×h별 일자단위 IC(원시/정규화) + 피처별 ρ₁. 반환 (curves, rho1_med, n_days).

    curves[name][h] = {"ic","t","n_days","ic_norm","t_norm"} (부호 유지).
    """
    by_day = defaultdict(list)
    for i, ts in enumerate(ts_list):
        by_day[ts[:10]].append(i)
    days = sorted(by_day)
    nf = len(names)
    ic_days = {h: [[] for _ in range(nf)] for h in grid}
    icn_days = {h: [[] for _ in range(nf)] for h in grid}
    rho1_days = [[] for _ in range(nf)]
    n_used_days = 0

    for d in days:
        rows = by_day[d]
        if len(rows) < MIN_DAY_ROWS + max(grid):
            continue
        n_used_days += 1
        closes_arr = np.array([closes[ts_list[i]] for i in rows], dtype=np.float64)
        sig1 = day_sigma1_pastonly(closes_arr)
        sub = X[np.array(rows), :]

        # 피처 lag-1 자기상관 (당일)
        for j in range(nf):
            col = sub[:, j]
            a, b = col[:-1], col[1:]
            ok = ~(np.isnan(a) | np.isnan(b))
            if ok.sum() >= 30:
                r = corr(a[ok], b[ok])
                if not math.isnan(r):
                    rho1_days[j].append(r)

        for h in grid:
            m = len(rows) - h
            fwd = closes_arr[h:] - closes_arr[:-h]          # 당일 내 전방 h분 (pt)
            sigh = sig1[:m] * math.sqrt(h)                   # past-only 정규화 분모
            fwd_norm = np.where(np.isfinite(sigh) & (sigh > 0), fwd / sigh, np.nan)
            fr_rank = rankdata(fwd)
            for j in range(nf):
                col = sub[:m, j]
                ok = ~np.isnan(col)
                if ok.sum() < MIN_DAY_ROWS or np.unique(col[ok]).size < 3:
                    ic_days[h][j].append(float("nan"))
                    icn_days[h][j].append(float("nan"))
                    continue
                c_rank = rankdata(col[ok])
                ic_days[h][j].append(corr(c_rank, fr_rank[ok]))
                okn = ok & np.isfinite(fwd_norm)
                if okn.sum() >= MIN_DAY_ROWS:
                    icn_days[h][j].append(
                        corr(rankdata(col[okn]), rankdata(fwd_norm[okn])))
                else:
                    icn_days[h][j].append(float("nan"))

    curves = OrderedDict()
    for j, nm in enumerate(names):
        curves[nm] = {}
        for h in grid:
            ic = np.array(ic_days[h][j], dtype=np.float64)
            icn = np.array(icn_days[h][j], dtype=np.float64)
            t, nd = tstat(list(ic))
            tn, _ = tstat(list(icn))
            v = ic[~np.isnan(ic)]
            vn = icn[~np.isnan(icn)]
            curves[nm][h] = {
                "ic": float(v.mean()) if v.size else float("nan"),
                "t": t, "n_days": nd,
                "ic_norm": float(vn.mean()) if vn.size else float("nan"),
                "t_norm": tn,
            }
    rho1_med = {}
    for j, nm in enumerate(names):
        v = rho1_days[j]
        rho1_med[nm] = float(np.median(v)) if v else float("nan")
    return curves, rho1_med, n_used_days


def fit_tau(curve, grid, peak_h):
    """peak 이후 동부호 구간에 ln|IC| = ln IC0 − h/τ 최소자승. 반환 (tau, half_life, r2)."""
    peak_sign = np.sign(curve[peak_h]["ic"])
    hs, ys = [], []
    for h in grid:
        if h < peak_h:
            continue
        ic = curve[h]["ic"]
        if math.isnan(ic) or np.sign(ic) != peak_sign or abs(ic) <= 0:
            continue
        hs.append(float(h))
        ys.append(math.log(abs(ic)))
    if len(hs) < TAU_MIN_POINTS:
        return None, None, None
    hs_a, ys_a = np.array(hs), np.array(ys)
    slope, intercept = np.polyfit(hs_a, ys_a, 1)
    pred = slope * hs_a + intercept
    ss_res = float(((ys_a - pred) ** 2).sum())
    ss_tot = float(((ys_a - ys_a.mean()) ** 2).sum())
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    if slope >= 0:
        return None, None, r2  # 감쇠 아님 (증가/평탄)
    tau = -1.0 / slope
    return tau, tau * math.log(2.0), r2


def classify(curve, grid, bonf_t):
    """유형 판정 (사전등록 규칙 — settings 주석 참조)."""
    valid = [h for h in grid if not math.isnan(curve[h]["t"])]
    if not valid:
        return "무정보", None
    sig = [h for h in valid if abs(curve[h]["t"]) >= bonf_t]
    # 부호반전: |t|>=SIG_T_PAIR인 두 h가 반대 부호
    pair = [h for h in valid if abs(curve[h]["t"]) >= SIG_T_PAIR]
    signs = set(int(np.sign(curve[h]["ic"])) for h in pair if curve[h]["ic"] != 0)
    peak_h = max(valid, key=lambda h: abs(curve[h]["ic"]))
    if len(signs) >= 2:
        return "부호반전", peak_h
    if not sig:
        return "무정보", peak_h
    if peak_h == grid[0]:
        return "단조감쇠", peak_h
    if peak_h == grid[-1]:
        # |IC|가 격자 끝까지 단조 증가 — 진짜 피크는 격자 밖. 수급 계열처럼 "일 단위
        # 공변동"이 원천일 가능성이 높은 형태다(394차: IC 강해도 일중 거래 전환 시 손실).
        # L2 거래성 함정 경고와 함께 읽을 것.
        return "증가형", peak_h
    return "봉우리", peak_h


def main():
    ap = argparse.ArgumentParser(description="IC 감쇠 카탈로그 (advisory, 읽기 전용)")
    ap.add_argument("--days", type=int, default=120)
    ap.add_argument("--top", type=int, default=40)
    ap.add_argument("--no-noise", action="store_true")
    args = ap.parse_args()

    feats, closes, dates = load(args.days)
    print("raw_features %d행, %d거래일 (%s ~ %s)" % (len(feats), len(dates), dates[0], dates[-1]))
    names, X, ts_list = build_matrix(feats)
    n_real = len(names)

    if not args.no_noise:
        templates = OrderedDict((nm, X[:, j]) for j, nm in enumerate(names))
        seed = int(dates[-1].replace("-", ""))
        noise = make_noise_features(templates, seed=seed,
                                    n_shuffle=N_SHUFFLE, n_phase=N_PHASE)
        if noise:
            X = np.column_stack([X] + [arr for arr in noise.values()])
            names = names + list(noise.keys())
            print("[N3] 노이즈 벤치마크 %d개 삽입 (seed=%d)" % (len(noise), seed))

    # Bonferroni 가족 = 실피처 × 격자 (노이즈는 가족 밖 — 하한선 전용)
    n_tests = n_real * len(GRID)
    bonf_t = 3.0 + 0.55 * math.log(max(n_tests, 2))
    print("격자 h=%s | 실피처 %d × %d = 검정 %d회 → Bonferroni 근사 |t| 임계 ≈ %.2f"
          % (GRID, n_real, len(GRID), n_tests, bonf_t))

    curves, rho1_med, n_days = analyze_curves(names, X, ts_list, closes, GRID)
    if n_days < MIN_DAYS:
        print("⚠ 유효일수 %d < min_days %d — 표본 미달, 결과는 참고만(313차 원칙)"
              % (n_days, MIN_DAYS))

    catalog = []
    for nm in names:
        curve = curves[nm]
        ctype, peak_h = classify(curve, GRID, bonf_t)
        tau = hl = r2 = None
        if peak_h is not None and not math.isnan(curve[peak_h]["ic"]):
            tau, hl, r2 = fit_tau(curve, GRID, peak_h)
        rho1 = rho1_med.get(nm, float("nan"))
        turnover = math.sqrt(max(0.0, 2.0 * (1.0 - rho1))) if not math.isnan(rho1) else None
        # 시간대의존: peak에서 원시·정규화 부호가 갈리고 둘 다 |t|>=2
        tod_flag = False
        if peak_h is not None:
            c = curve[peak_h]
            if (not math.isnan(c["ic"]) and not math.isnan(c["ic_norm"])
                    and abs(c["t"]) >= 2.0 and abs(c["t_norm"]) >= 2.0
                    and np.sign(c["ic"]) != np.sign(c["ic_norm"])):
                tod_flag = True
        max_abs_t = max((abs(curve[h]["t"]) for h in GRID
                         if not math.isnan(curve[h]["t"])), default=float("nan"))
        catalog.append({
            "name": nm, "type": ctype, "peak_h": peak_h,
            "peak_ic": curve[peak_h]["ic"] if peak_h is not None else None,
            "peak_t": curve[peak_h]["t"] if peak_h is not None else None,
            "max_abs_t": max_abs_t,
            "tau": tau, "half_life": hl, "fit_r2": r2,
            "rho1": None if math.isnan(rho1) else rho1,
            "turnover_proxy": turnover,
            "tod_dependent": tod_flag,
            "curve": {str(h): curve[h] for h in GRID},
            "is_noise": is_noise_name(nm),
        })

    # 노이즈 하한선 (max |t| 기준 — 일자 표본수가 피처마다 같아 t 비교가 공정)
    noise_rows = [c for c in catalog if c["is_noise"]]
    floor_t = max((c["max_abs_t"] for c in noise_rows
                   if not math.isnan(c["max_abs_t"])), default=float("nan"))

    def _fmt(v, fmt="%.3f"):
        return (fmt % v) if isinstance(v, float) and not math.isnan(v) else "-"

    print()
    print("=" * 118)
    print("카탈로그 — |t| 상위 %d (부호 유지 · ★=Bonferroni 통과 · †=노이즈 하한선 이하)"
          % args.top)
    print("=" * 118)
    print("%-28s %-8s %6s %9s %8s %8s %8s %6s %8s %s"
          % ("feature", "유형", "peak_h", "peak_IC", "peak_t", "τ", "반감기", "R²",
             "회전율≈", "IC 곡선 (h=%s)" % ",".join(str(h) for h in GRID)))
    ranked = sorted([c for c in catalog if not c["is_noise"]],
                    key=lambda c: -(c["max_abs_t"] if not math.isnan(c["max_abs_t"]) else -1))
    for c in ranked[:args.top]:
        star = "★" if (c["peak_t"] is not None and not math.isnan(c["peak_t"])
                       and abs(c["peak_t"]) > bonf_t) else " "
        dag = "†" if (not math.isnan(floor_t) and c["max_abs_t"] <= floor_t) else " "
        curve_s = " ".join(_fmt(c["curve"][str(h)]["ic"], "%+.3f") for h in GRID)
        print("%s%s%-26s %-8s %6s %9s %8s %8s %8s %6s %8s %s%s"
              % (star, dag, c["name"], c["type"],
                 c["peak_h"] if c["peak_h"] is not None else "-",
                 _fmt(c["peak_ic"], "%+.4f"), _fmt(c["peak_t"], "%.2f"),
                 _fmt(c["tau"] if c["tau"] is not None else float("nan"), "%.1f"),
                 _fmt(c["half_life"] if c["half_life"] is not None else float("nan"), "%.1f"),
                 _fmt(c["fit_r2"] if c["fit_r2"] is not None else float("nan"), "%.2f"),
                 _fmt(c["turnover_proxy"] if c["turnover_proxy"] is not None
                      else float("nan"), "%.3f"),
                 curve_s, "  ⚠시간대의존" if c["tod_dependent"] else ""))

    print()
    if noise_rows:
        alarm = [c["name"] for c in noise_rows
                 if not math.isnan(c["max_abs_t"]) and c["max_abs_t"] > bonf_t]
        print("[N3] 노이즈 하한선 max|t| = %s (%d개) %s"
              % (_fmt(floor_t, "%.2f"), len(noise_rows),
                 "| ⚠ 노이즈가 Bonferroni 통과: %s — 이 회차 전체 의심" % ", ".join(alarm)
                 if alarm else ""))

    flips = [c for c in ranked if c["type"] == "부호반전"]
    print()
    print("─" * 118)
    print("부호반전형 — **진입 후보 아님.** 청산/역추세 후보로 회부(챌린저 계층 입력,"
          " 검토보고 §3-N2). %d건" % len(flips))
    for c in flips:
        curve_s = " ".join("h%d:%s(t=%s)" % (h, _fmt(c["curve"][str(h)]["ic"], "%+.3f"),
                                             _fmt(c["curve"][str(h)]["t"], "%.1f"))
                           for h in GRID)
        print("  %-28s %s" % (c["name"], curve_s))

    print()
    print("※ advisory — 어떤 산출도 채택/탈락 효력이 없다. ADD/DROP은 Phase C 월간 리포트"
          " + L3 배터리 + 사람 승인 경로로만(§6).")

    # 산출물 저장 (런타임 — 커밋 금지)
    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)
    stamp = datetime.date.today().strftime("%Y%m%d")
    payload = {
        "generated": datetime.date.today().isoformat(),
        "window": [dates[0], dates[-1]], "n_days": n_days,
        "grid": GRID, "bonferroni_t": bonf_t, "n_real_features": n_real,
        "noise_floor_max_abs_t": None if math.isnan(floor_t) else floor_t,
        "catalog": catalog,
    }
    jpath = os.path.join(OUT_DIR, "ic_decay_catalog_%s.json" % stamp)
    with io.open(jpath, "w", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False, indent=1, default=str))
    print("JSON: %s" % jpath)
    return 0


if __name__ == "__main__":
    _utf8_console()
    sys.exit(main())
