# -*- coding: utf-8 -*-
"""[MW0601] 수명 x 호라이즌 교차검정 — "수명으로 호라이즌을 나눌 수 있는가"에 답한다.

lifetime.py가 낸 수명(tau / L_raw / L_chg)을, 같은 라이브 창에서 계산한
호라이즌별 IC(h)와 교차한다.

핵심 가설 H:
  "수명이 긴 피처는 긴 호라이즌에서 예측력이 최대다"
  -> Spearman(수명, argmax_h |IC(h)|) > 0 이고 유의해야 한다.
  이것이 성립하지 않으면 수명 기반 호라이즌 배정은 근거가 없다.

보조 검정:
  · 정합성 tau >= h — 피처의 기억이 h분보다 짧으면 그 피처는 h 시점에 이미 정보 소멸.
  · 널 대비 수명 — 실측 런이 shuffle/phase 널을 넘는가(455차 N3).
  · 순열검정 — argmax_h 는 IC가 무의미하면 노이즈다. 실제 상관이 우연 범위인지 본다.
"""
from __future__ import print_function
import io
import json
import math
import os
import sys
from collections import defaultdict, OrderedDict

import numpy as np

_ROOT = r"C:\Users\82108\PycharmProjects\futures"
sys.path.insert(0, _ROOT)
sys.stdout.reconfigure(encoding="utf-8")
from utils.dll_bootstrap import ensure_conda_dll_path

ensure_conda_dll_path()
from scripts.core_feature_discovery import build_matrix, analyze, tstat

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from live_only import load_live

IC_HZ = [1, 3, 5, 10, 15, 30]
BUCKET_ORDER = ["09:00-09:30", "09:30-10:30", "10:30-11:30",
                "11:30-13:00", "13:00-14:00", "14:00-15:10"]
CORE = ["cvd_divergence", "vwap_position", "ofi_norm", "opt_chain_pcr",
        "cvd_delta_norm", "vwap_momentum"]


def spearman(a, b):
    from scipy.stats import rankdata
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 6:
        return float("nan"), 0
    ra, rb = rankdata(a[ok]), rankdata(b[ok])
    ra, rb = ra - ra.mean(), rb - rb.mean()
    d = math.sqrt(float(np.dot(ra, ra)) * float(np.dot(rb, rb)))
    return (float(np.dot(ra, rb)) / d if d > 0 else float("nan")), int(ok.sum())


def perm_p(a, b, rho, n_perm=20000, seed=20260824):
    """순열검정 — |rho| 이상이 우연히 나올 확률."""
    rng = np.random.RandomState(seed)
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = np.isfinite(a) & np.isfinite(b)
    a, b = a[ok], b[ok]
    if a.size < 6 or not np.isfinite(rho):
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

    with open("lifetime_raw.json", encoding="utf-8") as f:
        LIFE = json.load(f)
    res_life = LIFE["result"]

    feats, closes, dates = load_live()
    names, X, ts_list = build_matrix(feats, verbose=False)

    P("=" * 104)
    P("[MW0601] 피처 수명 x 호라이즌 교차검정 — 순수 라이브 %d거래일 (%s ~ %s)"
      % (len(dates), dates[0], dates[-1]))
    P("=" * 104)

    # ── 1. 호라이즌별 IC ────────────────────────────────────────────
    P("\n[1] 호라이즌별 IC 계산 (일자단위 독립관측, 오버나이트 제외)")
    IC = {}
    for h in IC_HZ:
        res, nd = analyze(names, X, ts_list, closes, h)
        IC[h] = {r["name"]: r for r in res}
        sig = [r for r in res if np.isfinite(r["ic_t"]) and abs(r["ic_t"]) >= 2.0]
        P("   h=%-3d 유효일 %-3d  |t|>=2 피처 %d개" % (h, nd, len(sig)))
    n_tests = len(names) * len(IC_HZ)
    bonf_t = 3.0 + 0.55 * math.log(max(n_tests, 2))
    P("   다중비교: 검정 %d회 -> Bonferroni 근사 |t| 임계 ~= %.2f" % (n_tests, bonf_t))

    # ── 2. 널 대비 수명 ────────────────────────────────────────────
    P("\n" + "=" * 104)
    P("[2] 널 대비 수명 — 실측 런이 노이즈보다 긴가 (455차 N3)")
    P("=" * 104)
    P("%-32s %6s %7s %7s %7s %7s %7s %6s" %
      ("피처", "동률%", "L_raw", "널shuf", "널phase", "R_shuf", "R_phase", "tau"))
    P("-" * 104)
    rows = []
    for nm in names:
        r = res_life.get(nm)
        if not r:
            continue
        lr = r.get("L_raw")
        ns, npz = r.get("null_shuf"), r.get("null_phase")
        if lr is None or ns in (None, 0) or npz in (None, 0):
            continue
        rows.append(dict(nm=nm, tie=r["tie"], L_raw=lr, L_chg=r.get("L_chg"),
                         tau=r.get("tau"), ns=ns, np_=npz,
                         Rs=lr / ns, Rp=lr / npz,
                         ns_sd=r.get("null_shuf_sd"), np_sd=r.get("null_phase_sd")))
    rows.sort(key=lambda x: -(x["Rs"] if np.isfinite(x["Rs"]) else -9))
    for x in rows[:20]:
        P("%-32s %5.1f%% %7.3f %7.3f %7.3f %7.3f %7.3f %6.1f" %
          (x["nm"][:32], x["tie"] * 100, x["L_raw"], x["ns"], x["np_"],
           x["Rs"], x["Rp"], x["tau"] if x["tau"] else float("nan")))
    P("   ... (하위 생략, 전체 %d개는 lifetime_cross.json)" % len(rows))
    allR = np.array([x["Rs"] for x in rows if np.isfinite(x["Rs"])])
    allRp = np.array([x["Rp"] for x in rows if np.isfinite(x["Rp"])])
    P("\n   R_shuf  중앙값 %.3f | >1.05인 피처 %d/%d"
      % (np.median(allR), int((allR > 1.05).sum()), allR.size))
    P("   R_phase 중앙값 %.3f | >1.05인 피처 %d/%d"
      % (np.median(allRp), int((allRp > 1.05).sum()), allRp.size))
    P("   해석: R_shuf>1 = 시간구조 존재 / R_phase>1 = 선형 자기상관을 넘는 방향지속성")

    # ── 3. 핵심 교차검정 ───────────────────────────────────────────
    P("\n" + "=" * 104)
    P("[3] 핵심 — 수명이 최적 호라이즌을 예측하는가")
    P("=" * 104)
    life_tau, life_chg, life_raw, best_h, best_t, nm_ok = [], [], [], [], [], []
    for nm in names:
        r = res_life.get(nm)
        if not r or r.get("tau") is None:
            continue
        ics = [(h, IC[h].get(nm, {}).get("ic_t", float("nan"))) for h in IC_HZ]
        ics = [(h, t) for h, t in ics if np.isfinite(t)]
        if len(ics) < len(IC_HZ):
            continue
        h_star, t_star = max(ics, key=lambda z: abs(z[1]))
        nm_ok.append(nm)
        life_tau.append(r["tau"])
        life_chg.append(r.get("L_chg") or float("nan"))
        life_raw.append(r.get("L_raw") or float("nan"))
        best_h.append(h_star)
        best_t.append(abs(t_star))
    P("대상 피처 %d개 (수명·IC 모두 산출된 것)" % len(nm_ok))

    for lab, arr in (("tau (ACF반감기)", life_tau), ("L_chg (변화압축런)", life_chg),
                     ("L_raw (분단위런)", life_raw)):
        rho, n = spearman(arr, best_h)
        p = perm_p(arr, best_h, rho)
        P("   Spearman(%-18s , argmax_h|IC|) = %+.4f  (n=%d, 순열 p=%.4f) %s"
          % (lab, rho, n, p, "유의" if np.isfinite(p) and p < 0.05 else "무의미"))

    # 유의한 IC를 가진 피처만
    strong = [i for i, t in enumerate(best_t) if t >= 2.0]
    P("\n   |t|>=2 인 피처만 (n=%d):" % len(strong))
    if len(strong) >= 6:
        for lab, arr in (("tau", life_tau), ("L_chg", life_chg)):
            sub_a = [arr[i] for i in strong]
            sub_b = [best_h[i] for i in strong]
            rho, n = spearman(sub_a, sub_b)
            p = perm_p(sub_a, sub_b, rho)
            P("      Spearman(%-6s, argmax_h) = %+.4f (n=%d, p=%.4f)" % (lab, rho, n, p))
    else:
        P("      표본 부족 — 판정 불가")

    P("\n   argmax_h 분포: " + ", ".join(
        "h=%d:%d개" % (h, best_h.count(h)) for h in IC_HZ))
    P("   (IC가 무정보면 이 분포는 균등에 가깝고 argmax_h 자체가 노이즈다)")

    # ── 4. 정합성 tau >= h ─────────────────────────────────────────
    P("\n" + "=" * 104)
    P("[4] 정합성 — 피처의 기억(tau)이 호라이즌 h보다 긴가")
    P("=" * 104)
    taus = np.array([t for t in life_tau if np.isfinite(t)])
    P("tau 분포: 중앙값 %.1f분 · 25%%=%.1f · 75%%=%.1f · 최대 %.1f (상한 90분)"
      % (np.median(taus), np.percentile(taus, 25), np.percentile(taus, 75), taus.max()))
    for h in IC_HZ:
        n_ok = int((taus >= h).sum())
        P("   h=%-3d : tau>=h 인 피처 %2d/%d (%.0f%%)"
          % (h, n_ok, taus.size, 100.0 * n_ok / taus.size))

    # ── 5. 시간대별 프로파일 ───────────────────────────────────────
    P("\n" + "=" * 104)
    P("[5] 시간대별 수명 프로파일 (분 단위 런, 일자평균)")
    P("=" * 104)
    P("%-32s %s" % ("피처", " ".join("%11s" % b for b in BUCKET_ORDER)))
    P("-" * 104)

    def bucket_row(nm, key):
        r = res_life.get(nm, {})
        d = r.get(key) or {}
        out = []
        for b in BUCKET_ORDER:
            v = d.get(b)
            out.append("%11s" % ("%.2f" % v[0] if v else "-"))
        return " ".join(out)

    shown = [n for n in CORE if n in res_life]
    shown += [x["nm"] for x in rows[:6] if x["nm"] not in shown]
    for nm in shown:
        P("%-32s %s" % (nm[:32] + " ^", bucket_row(nm, "up")))
        P("%-32s %s" % ("  (하락런)", bucket_row(nm, "dn")))

    # 전체 평균 프로파일
    P("\n   [전 피처 평균]")
    for key, lab in (("up", "상승런"), ("dn", "하락런")):
        vals = []
        for b in BUCKET_ORDER:
            v = [res_life[n][key][b][0] for n in names
                 if n in res_life and (res_life[n].get(key) or {}).get(b)]
            vals.append(np.mean(v) if v else float("nan"))
        P("   %-8s %s" % (lab, " ".join("%11.3f" % v for v in vals)))

    # 시간대 차이 유의성 — 개장 vs 나머지, 피처별 일자단위 paired
    P("\n   [개장(09:00-09:30) vs 마감(14:00-15:10) 차이 — 피처별 일자평균 t검정]")
    diffs = []
    for nm in names:
        r = res_life.get(nm)
        if not r:
            continue
        a = (r.get("up_daily") or {}).get("09:00-09:30")
        b = (r.get("up_daily") or {}).get("14:00-15:10")
        if not a or not b or len(a) < 5 or len(b) < 5:
            continue
        m = min(len(a), len(b))
        d = np.array(a[:m]) - np.array(b[:m])
        t, n = tstat(d)
        if np.isfinite(t):
            diffs.append((nm, float(np.mean(d)), t, n))
    diffs.sort(key=lambda z: -abs(z[2]))
    P("   유의(|t|>=2) %d/%d 피처" % (len([d for d in diffs if abs(d[2]) >= 2]), len(diffs)))
    for nm, md, t, n in diffs[:10]:
        P("      %-32s 개장-마감 = %+.3f분  t=%+.2f (n=%d)" % (nm[:32], md, t, n))

    # ── 저장 ───────────────────────────────────────────────────────
    out = dict(
        dates=[dates[0], dates[-1]], n_days=len(dates),
        null_ratio=[dict(nm=x["nm"], tie=x["tie"], L_raw=x["L_raw"], tau=x["tau"],
                         R_shuf=x["Rs"], R_phase=x["Rp"]) for x in rows],
        cross=[dict(nm=n, tau=t, L_chg=c, best_h=h, best_t=bt)
               for n, t, c, h, bt in zip(nm_ok, life_tau, life_chg, best_h, best_t)],
        ic={str(h): {n: dict(ic=IC[h][n]["ic"], t=IC[h][n]["ic_t"])
                     for n in names if n in IC[h]} for h in IC_HZ},
    )
    with open("lifetime_cross.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False,
                  default=lambda o: None if isinstance(o, float) and math.isnan(o) else float(o))
    with open("lifetime_cross.txt", "w", encoding="utf-8") as f:
        f.write(L.getvalue())
    P("\n저장 -> lifetime_cross.json / lifetime_cross.txt")


if __name__ == "__main__":
    main()
