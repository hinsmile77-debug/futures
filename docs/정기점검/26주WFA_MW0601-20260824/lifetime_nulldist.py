# -*- coding: utf-8 -*-
"""[MW0601] 널 분포 — lifetime_artifact.py의 널 1회 실현을 분포로 확장.

artifact 검정은 위상무작위 널을 **한 번만** 실현해 rho(tau_null, |t|_null) = -0.3228
(순열 p=0.0031)을 얻었다. 그 p값은 '이 한 실현 안에서 짝을 섞었을 때'의 값이라
널 자체의 실현 변동은 반영하지 못한다. 널을 N회 반복해 분포를 만들고,
실측값이 그 분포의 어디에 있는지로 판정한다.

두 가지를 본다:
  (a) rho(tau, 평균|t|)   실측 +0.1078 이 널 분포의 몇 분위인가
  (b) 평균|t| 수준        실측 1.361 이 널 분포(1회 0.830)를 넘는가
"""
from __future__ import print_function
import io
import json
import math
import os
import sys
import time

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
N_REP = 15


def spearman(a, b):
    from scipy.stats import rankdata
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 4:
        return float("nan")
    ra, rb = rankdata(a[ok]), rankdata(b[ok])
    ra, rb = ra - ra.mean(), rb - rb.mean()
    d = math.sqrt(float(np.dot(ra, ra)) * float(np.dot(rb, rb)))
    return float(np.dot(ra, rb)) / d if d > 0 else float("nan")


def main():
    L = io.StringIO()

    def P(*a):
        s = " ".join(str(x) for x in a)
        print(s, flush=True)
        L.write(s + "\n")

    cross = json.load(open("lifetime_cross.json", encoding="utf-8"))
    IC = cross["ic"]
    robust = json.load(open("lifetime_robust.json", encoding="utf-8"))
    art = json.load(open("lifetime_artifact.json", encoding="utf-8"))
    bad = {z["nm"] for z in robust["asym"] if z["asym"] and z["asym"] > 0.30}

    feats, closes, dates = load_live()
    names, X, ts_list = build_matrix(feats, verbose=False)
    segs, tt = segments(ts_list)
    idx = [i for i, nm in enumerate(names) if nm not in CLOCK and nm not in bad]

    P("=" * 104)
    P("[MW0601] 널 분포 검정 — %d회 반복 · 순수 라이브 %d거래일" % (N_REP, len(dates)))
    P("=" * 104)
    P("실측 기준값: rho(tau, 평균|t|) = %+.4f · 평균|t| = %.3f"
      % (art["rho_tau_level"], art["real_mean_absT"]))
    P("널 1회 실현(artifact): rho = %+.4f · 평균|t| = %.3f\n"
      % (art["rho_null_level"], art["null_mean_absT"]))

    rng = np.random.RandomState(90824)
    rhos, lvls, maxts = [], [], []
    t0 = time.time()
    for rep in range(N_REP):
        NZ = np.full((X.shape[0], len(idx)), np.nan)
        nz_names = []
        for k, j in enumerate(idx):
            NZ[:, k] = phase_randomize(X[:, j].astype(np.float64), rng)
            nz_names.append("nz%d_%s" % (rep, names[j]))
        tau_n = [acf_halflife(NZ[:, k], segs)[0] for k in range(len(idx))]
        icn = {}
        for h in IC_HZ:
            res, _nd = analyze(nz_names, NZ, ts_list, closes, h)
            icn[h] = {r["name"]: r["ic_t"] for r in res}
        lvl = []
        for nm in nz_names:
            ts = [abs(icn[h].get(nm, float("nan"))) for h in IC_HZ]
            ts = [x for x in ts if np.isfinite(x)]
            lvl.append(float(np.mean(ts)) if len(ts) == len(IC_HZ) else float("nan"))
        rhos.append(spearman(tau_n, lvl))
        lvls.append(float(np.nanmean(lvl)))
        maxts.append(float(np.nanmax(lvl)))
        P("   rep %2d/%d  rho=%+.4f  평균|t|=%.3f  최대|t|=%.2f  (%.0fs)"
          % (rep + 1, N_REP, rhos[-1], lvls[-1], maxts[-1], time.time() - t0))

    rhos = np.array([r for r in rhos if np.isfinite(r)])
    lvls = np.array(lvls)
    P("\n" + "=" * 104)
    P("[결과]")
    P("=" * 104)
    P("(a) rho(tau, 평균|t|) 널 분포: 평균 %+.4f · sd %.4f · 범위 [%+.4f, %+.4f]"
      % (rhos.mean(), rhos.std(ddof=1), rhos.min(), rhos.max()))
    real_rho = art["rho_tau_level"]
    above = int((rhos >= real_rho).sum())
    p_two = 2.0 * min(above + 1, len(rhos) - above + 1) / (len(rhos) + 1.0)
    P("    실측 %+.4f 는 널 %d개 중 %d개보다 크다 -> 양측 p ~ %.3f"
      % (real_rho, len(rhos), len(rhos) - above, min(p_two, 1.0)))
    P("    -> %s" % ("널 분포 밖 = 수명-예측력 수준 관계가 실재"
                     if min(p_two, 1.0) < 0.05 else
                     "널 분포 안 = 실측 관계는 우연 범위. 수명은 예측력 수준과 무관"))
    P("    ※ 널 rho 평균이 0이 아니면 그 자체가 자기상관의 구조적 편향이다.")

    P("\n(b) 평균|t| 수준: 널 평균 %.3f (sd %.3f, 범위 %.3f~%.3f) vs 실측 %.3f"
      % (lvls.mean(), lvls.std(ddof=1), lvls.min(), lvls.max(), art["real_mean_absT"]))
    z = (art["real_mean_absT"] - lvls.mean()) / lvls.std(ddof=1) if lvls.std(ddof=1) > 0 else float("nan")
    P("    z = %+.2f · 실측이 널 %d개 전부보다 %s"
      % (z, len(lvls), "크다" if art["real_mean_absT"] > lvls.max() else "크지 않다"))
    P("    -> %s" % ("피처 집합 전체에 널을 넘는 방향 정보가 있다(수명과는 별개)"
                     if art["real_mean_absT"] > lvls.max() else
                     "피처 집합 전체가 널과 구분되지 않는다"))

    json.dump(dict(n_rep=int(len(rhos)), rho_null=[float(x) for x in rhos],
                   lvl_null=[float(x) for x in lvls],
                   real_rho=real_rho, real_lvl=art["real_mean_absT"],
                   p_rho=float(min(p_two, 1.0)), z_level=float(z)),
              open("lifetime_nulldist.json", "w", encoding="utf-8"), ensure_ascii=False)
    with open("lifetime_nulldist.txt", "w", encoding="utf-8") as f:
        f.write(L.getvalue())
    P("\n저장 -> lifetime_nulldist.txt / .json")


if __name__ == "__main__":
    main()
