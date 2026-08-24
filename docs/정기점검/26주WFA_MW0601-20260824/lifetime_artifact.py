# -*- coding: utf-8 -*-
"""[MW0601] 결정적 검정 — "수명이 길수록 IC t가 크다"가 진짜인가 아티팩트인가.

[통제3]에서 tau 장기 그룹의 평균|t|가 2.2로 단·중기(0.8~1.4)보다 뚜렷이 높았다.
두 해석이 가능하다:

  해석 A (실재)  기억이 긴 피처가 실제로 방향 정보를 더 많이 담는다.
  해석 B (아티팩트)  자기상관이 강한 계열은 일자별 IC가 안정적으로 나와
                   일자간 분산이 작아지고, t = mean/(sd/sqrt(n))의 분모가 줄어
                   **예측력과 무관하게** t가 부풀려진다.

판정법: 위상 무작위 널은 자기상관(=tau)을 보존하면서 예측력만 파괴한다.
        널에서도 tau vs |t| 양의 관계가 재현되면 **해석 B 확정**이다.

추가로 프로파일의 '형태'와 '수준'을 분리한다 — 호라이즌 배정 근거는 형태에만 있다.
"""
from __future__ import print_function
import io
import json
import math
import os
import sys

import numpy as np

_ROOT = r"C:\Users\82108\PycharmProjects\futures"
sys.path.insert(0, _ROOT)
sys.stdout.reconfigure(encoding="utf-8")
from utils.dll_bootstrap import ensure_conda_dll_path

ensure_conda_dll_path()
from scripts.core_feature_discovery import build_matrix, analyze
from scripts.noise_benchmark import phase_randomize

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from live_only import load_live
from lifetime import segments, acf_halflife

IC_HZ = [1, 3, 5, 10, 15, 30]
CLOCK = {"time_cos", "time_sin"}


def spearman(a, b):
    from scipy.stats import rankdata
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 4:
        return float("nan"), 0
    ra, rb = rankdata(a[ok]), rankdata(b[ok])
    ra, rb = ra - ra.mean(), rb - rb.mean()
    d = math.sqrt(float(np.dot(ra, ra)) * float(np.dot(rb, rb)))
    return (float(np.dot(ra, rb)) / d if d > 0 else float("nan")), int(ok.sum())


def perm_p(a, b, rho, n_perm=10000, seed=20260824):
    rng = np.random.RandomState(seed)
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = np.isfinite(a) & np.isfinite(b)
    a, b = a[ok], b[ok]
    if a.size < 4 or not np.isfinite(rho):
        return float("nan")
    cnt = 0
    for _ in range(n_perm):
        r, _n = spearman(a, rng.permutation(b))
        if np.isfinite(r) and abs(r) >= abs(rho) - 1e-12:
            cnt += 1
    return (cnt + 1.0) / (n_perm + 1.0)


def main():
    L = io.StringIO()

    def P(*a):
        s = " ".join(str(x) for x in a)
        print(s)
        L.write(s + "\n")

    cross = json.load(open("lifetime_cross.json", encoding="utf-8"))
    IC = cross["ic"]
    robust = json.load(open("lifetime_robust.json", encoding="utf-8"))
    bad = {z["nm"] for z in robust["asym"] if z["asym"] and z["asym"] > 0.30}

    feats, closes, dates = load_live()
    names, X, ts_list = build_matrix(feats, verbose=False)
    segs, tt = segments(ts_list)

    P("=" * 104)
    P("[MW0601] 수명-IC 관계의 실재성 검정 — 순수 라이브 %d거래일" % len(dates))
    P("=" * 104)

    # ── 실측: tau vs 예측력 수준 ───────────────────────────────────
    keep = [c for c in cross["cross"]
            if c["nm"] not in CLOCK and c["nm"] not in bad and c["tau"]]
    tau_r = [c["tau"] for c in keep]
    lvl_r, shp_r = [], []
    for c in keep:
        ts = [abs(IC[str(h)][c["nm"]]["t"]) for h in IC_HZ
              if c["nm"] in IC[str(h)] and IC[str(h)][c["nm"]]["t"] is not None]
        lvl_r.append(float(np.mean(ts)) if len(ts) == len(IC_HZ) else float("nan"))
        shp_r.append(spearman(IC_HZ, ts)[0] if len(ts) == len(IC_HZ) else float("nan"))

    P("\n[1] 실측 — tau vs IC t의 '수준'과 '형태'")
    r_lvl, n = spearman(tau_r, lvl_r)
    p_lvl = perm_p(tau_r, lvl_r, r_lvl)
    P("   수준: Spearman(tau, 평균|t|)      = %+.4f (n=%d, p=%.4f) %s"
      % (r_lvl, n, p_lvl, "유의" if p_lvl < 0.05 else "무의미"))
    r_shp, n2 = spearman(tau_r, shp_r)
    p_shp = perm_p(tau_r, shp_r, r_shp)
    P("   형태: Spearman(tau, IC기울기)     = %+.4f (n=%d, p=%.4f) %s"
      % (r_shp, n2, p_shp, "유의" if p_shp < 0.05 else "무의미"))
    P("   -> 호라이즌 배정 근거는 **형태**에만 있다. 수준은 피처 선별 축이다.")

    # ── 널: 같은 관계가 재현되는가 ─────────────────────────────────
    P("\n[2] 위상 무작위 널 — 자기상관 보존 · 예측력 파괴")
    P("    널에서도 같은 양의 관계가 나오면 [1]의 '수준'은 아티팩트다.")
    rng = np.random.RandomState(20260824)
    idx = [i for i, nm in enumerate(names) if nm not in CLOCK and nm not in bad]
    NZ = np.full((X.shape[0], len(idx)), np.nan)
    nz_names = []
    for k, j in enumerate(idx):
        NZ[:, k] = phase_randomize(X[:, j].astype(np.float64), rng)
        nz_names.append("nz_%s" % names[j])

    tau_n = []
    for k in range(len(idx)):
        t, _c = acf_halflife(NZ[:, k], segs)
        tau_n.append(t)

    ic_n = {}
    for h in IC_HZ:
        res, nd = analyze(nz_names, NZ, ts_list, closes, h)
        ic_n[h] = {r["name"]: r for r in res}
    lvl_n, shp_n = [], []
    for nm in nz_names:
        ts = [abs(ic_n[h][nm]["ic_t"]) for h in IC_HZ
              if nm in ic_n[h] and np.isfinite(ic_n[h][nm]["ic_t"])]
        lvl_n.append(float(np.mean(ts)) if len(ts) == len(IC_HZ) else float("nan"))
        shp_n.append(spearman(IC_HZ, ts)[0] if len(ts) == len(IC_HZ) else float("nan"))

    rn_lvl, nn = spearman(tau_n, lvl_n)
    pn_lvl = perm_p(tau_n, lvl_n, rn_lvl)
    P("   널 수준: Spearman(tau_null, 평균|t|_null) = %+.4f (n=%d, p=%.4f) %s"
      % (rn_lvl, nn, pn_lvl, "유의" if pn_lvl < 0.05 else "무의미"))
    P("   널 평균|t| = %.3f (실측 %.3f) | 널 최대|t| = %.2f (실측 %.2f)"
      % (np.nanmean(lvl_n), np.nanmean(lvl_r), np.nanmax(lvl_n), np.nanmax(lvl_r)))

    P("\n   판정:")
    if np.isfinite(rn_lvl) and rn_lvl > 0.2 and pn_lvl < 0.05:
        P("      널에서도 양의 관계가 재현됐다 -> [1]의 '수준' 관계는 **아티팩트**.")
        P("      자기상관이 t를 부풀린 것이지 예측력이 아니다.")
        verdict = "artifact"
    elif np.isfinite(r_lvl) and r_lvl > 0.2 and p_lvl < 0.05:
        P("      널에서는 재현되지 않았다 -> [1]의 '수준' 관계는 **실재**로 보존된다.")
        verdict = "real"
    else:
        P("      실측 관계 자체가 무의미해 판정할 것이 없다.")
        verdict = "none"

    # ── 형태 정규화 프로파일 ───────────────────────────────────────
    P("\n[3] 프로파일 '형태'만 비교 — 각 그룹을 자기 평균으로 정규화")
    P("    수준 차이를 제거하면 형태가 같은가? (같으면 호라이즌 분리 근거 없음)")
    prof = robust["profile"]
    P("   %-26s %s" % ("그룹", " ".join("%8s" % ("h=%d" % h) for h in IC_HZ)))
    shapes = {}
    for k, v in prof.items():
        v = np.array(v, float)
        s = v / np.nanmean(v)
        shapes[k] = s
        P("   %-26s %s" % (k[:26], " ".join("%8.3f" % x for x in s)))
    ks = list(shapes)
    P("\n   형태 간 Spearman 상관 (1.0에 가까울수록 동일한 모양):")
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            r, _n = spearman(shapes[ks[i]], shapes[ks[j]])
            P("      %-22s vs %-22s = %+.3f" % (ks[i][:22], ks[j][:22], r))

    # 그룹별 프로파일 변동폭
    P("\n   각 그룹 프로파일의 변동폭 (max-min, 정규화 후):")
    for k in ks:
        s = shapes[k]
        P("      %-26s %.3f %s" % (k[:26], np.nanmax(s) - np.nanmin(s),
                                   "<- 사실상 평평(argmax 무의미)"
                                   if (np.nanmax(s) - np.nanmin(s)) < 0.15 else ""))

    out = dict(rho_tau_level=r_lvl, p_tau_level=p_lvl,
               rho_tau_shape=r_shp, p_tau_shape=p_shp,
               rho_null_level=rn_lvl, p_null_level=pn_lvl,
               null_mean_absT=float(np.nanmean(lvl_n)),
               real_mean_absT=float(np.nanmean(lvl_r)),
               verdict=verdict,
               shapes={k: [float(x) for x in v] for k, v in shapes.items()})
    json.dump(out, open("lifetime_artifact.json", "w", encoding="utf-8"),
              ensure_ascii=False,
              default=lambda o: None if isinstance(o, float) and math.isnan(o) else float(o))
    with open("lifetime_artifact.txt", "w", encoding="utf-8") as f:
        f.write(L.getvalue())
    P("\n저장 -> lifetime_artifact.txt / .json")


if __name__ == "__main__":
    main()
