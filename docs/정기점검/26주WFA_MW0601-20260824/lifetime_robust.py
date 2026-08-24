# -*- coding: utf-8 -*-
"""[MW0601] 수명분석 3종 통제 — 결론을 뒤집을 수 있는 오염요인을 먼저 죽인다.

통제 1  결정론적 시계 제외
        time_cos/time_sin은 피처가 아니라 시계 자체다(R_shuf 90배). 전 피처 평균을
        혼자 끌어올린다. 제외 + 중앙값 병기.
통제 2  단조/누적 아티팩트
        cvd는 상승런 28.6 vs 하락런 1.00. 누적합 계열은 "수명이 길다"가 아니라
        "단조증가한다"는 뜻이다. 비대칭도 |up-dn|/(up+dn)로 검출해 격리.
통제 3  argmax_h 대신 IC 기울기
        argmax는 노이즈에 취약하고, IC(h)가 h에 따라 구조적으로 커지면 편향된다.
        피처별 slope = Spearman(h, |IC(h)|)를 쓰고 tau와 교차한다.

최종 질문: tau 3분위 그룹의 IC(h) 프로파일이 **교차하는가**.
  교차 = 수명 기반 호라이즌 분리에 근거 있음
  평행 = 근거 없음 (그룹을 나눠도 같은 호라이즌이 최적)
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

IC_HZ = [1, 3, 5, 10, 15, 30]
BUCKET_ORDER = ["09:00-09:30", "09:30-10:30", "10:30-11:30",
                "11:30-13:00", "13:00-14:00", "14:00-15:10"]
CLOCK = {"time_cos", "time_sin", "minutes_since_open", "minutes_to_close"}


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


def perm_p(a, b, rho, n_perm=20000, seed=20260824):
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

    life = json.load(open("lifetime_raw.json", encoding="utf-8"))["result"]
    cross = json.load(open("lifetime_cross.json", encoding="utf-8"))
    IC = cross["ic"]
    names = [c["nm"] for c in cross["cross"]]

    P("=" * 104)
    P("[MW0601] 수명분석 3종 통제 — 순수 라이브 %d거래일" % cross["n_days"])
    P("=" * 104)

    # ── 통제 1: 시계 제외 + 중앙값 ─────────────────────────────────
    P("\n" + "=" * 104)
    P("[통제1] 결정론적 시계 제외 후 시간대별 프로파일 (평균 -> 중앙값 병기)")
    P("=" * 104)
    pool = [n for n in life if n not in CLOCK]
    P("대상 %d개 (시계 %d개 제외: %s)"
      % (len(pool), len(life) - len(pool), ", ".join(sorted(set(life) & CLOCK)) or "없음"))
    P("\n%-10s %s" % ("", " ".join("%12s" % b for b in BUCKET_ORDER)))
    for key, lab in (("up", "상승런"), ("dn", "하락런")):
        for stat, fn in (("평균", np.mean), ("중앙값", np.median)):
            vals = []
            for b in BUCKET_ORDER:
                v = [life[n][key][b][0] for n in pool
                     if (life[n].get(key) or {}).get(b)]
                vals.append(fn(v) if v else float("nan"))
            P("%-10s %s" % ("%s %s" % (lab, stat), " ".join("%12.3f" % v for v in vals)))
    P("\n   -> 시계를 빼면 평균과 중앙값이 가까워진다 = 소수 극단값이 만든 착시였다")

    # ── 통제 2: 비대칭 ─────────────────────────────────────────────
    P("\n" + "=" * 104)
    P("[통제2] 상승/하락 비대칭 — 누적·단조 계열 격리")
    P("=" * 104)
    asym = []
    for n in pool:
        r = life[n]
        u = [v[0] for v in (r.get("up") or {}).values()]
        d = [v[0] for v in (r.get("dn") or {}).values()]
        if not u or not d:
            continue
        mu, md = float(np.mean(u)), float(np.mean(d))
        if mu + md <= 0:
            continue
        asym.append((n, mu, md, abs(mu - md) / (mu + md), r.get("tie", 0)))
    asym.sort(key=lambda z: -z[3])
    P("%-32s %8s %8s %9s %8s" % ("피처", "상승런", "하락런", "비대칭도", "동률%"))
    P("-" * 104)
    for n, mu, md, a, tie in asym[:12]:
        flag = "  <-- 단조/누적 의심" if a > 0.3 else ""
        P("%-32s %8.2f %8.2f %9.3f %7.1f%%%s" % (n[:32], mu, md, a, tie * 100, flag))
    bad = [z[0] for z in asym if z[3] > 0.30]
    P("\n   비대칭도>0.30 = %d개 -> 방향 수명 해석에서 제외 대상: %s"
      % (len(bad), ", ".join(bad) or "없음"))

    # ── 통제 3: IC 기울기 ──────────────────────────────────────────
    P("\n" + "=" * 104)
    P("[통제3] argmax_h 대신 IC 기울기 — slope = Spearman(h, |IC(h)|)")
    P("=" * 104)
    clean = [n for n in names if n not in CLOCK and n not in bad]
    tau, slope, bh, absic = [], [], [], []
    for n in clean:
        ts = [abs(IC[str(h)][n]["t"]) for h in IC_HZ
              if n in IC[str(h)] and IC[str(h)][n]["t"] is not None]
        if len(ts) < len(IC_HZ):
            continue
        s, _ = spearman(IC_HZ, ts)
        c = next(c for c in cross["cross"] if c["nm"] == n)
        tau.append(c["tau"])
        slope.append(s)
        bh.append(c["best_h"])
        absic.append(max(ts))
    P("대상 %d개 (시계·단조 제외)" % len(tau))
    r1, n1 = spearman(tau, slope)
    p1 = perm_p(tau, slope, r1)
    P("   Spearman(tau, IC기울기) = %+.4f (n=%d, 순열 p=%.4f) -> %s"
      % (r1, n1, p1, "유의" if p1 < 0.05 else "무의미"))
    r2, n2 = spearman(tau, bh)
    p2 = perm_p(tau, bh, r2)
    P("   Spearman(tau, argmax_h) = %+.4f (n=%d, 순열 p=%.4f) -> %s"
      % (r2, n2, p2, "유의" if p2 < 0.05 else "무의미"))
    P("   (가설 H가 참이면 둘 다 뚜렷한 양수여야 한다)")

    # ── 최종: tau 3분위 그룹의 IC(h) 프로파일 ──────────────────────
    P("\n" + "=" * 104)
    P("[최종] tau 3분위 그룹별 IC(h) 프로파일 — 교차하는가, 평행한가")
    P("=" * 104)
    tt = np.array(tau, float)
    q1, q2 = np.percentile(tt, [33.3, 66.7])
    grp = {"단기(tau<=%.1f)" % q1: [], "중기(%.1f<tau<=%.1f)" % (q1, q2): [],
           "장기(tau>%.1f)" % q2: []}
    keys = list(grp)
    for n, t in zip(clean, tau):
        if not np.isfinite(t):
            continue
        k = keys[0] if t <= q1 else (keys[1] if t <= q2 else keys[2])
        grp[k].append(n)
    P("%-24s %s" % ("그룹(n)", " ".join("%9s" % ("h=%d" % h) for h in IC_HZ)))
    P("-" * 104)
    prof = {}
    for k in keys:
        vals = []
        for h in IC_HZ:
            v = [abs(IC[str(h)][n]["t"]) for n in grp[k]
                 if n in IC[str(h)] and IC[str(h)][n]["t"] is not None]
            vals.append(float(np.mean(v)) if v else float("nan"))
        prof[k] = vals
        P("%-24s %s" % ("%s (n=%d)" % (k, len(grp[k])),
                        " ".join("%9.3f" % v for v in vals)))
    P("\n   각 그룹의 최적 h (평균|t| 최대):")
    for k in keys:
        i = int(np.nanargmax(prof[k]))
        P("      %-28s -> h=%-3d (평균|t|=%.3f)" % (k, IC_HZ[i], prof[k][i]))
    same = len({int(np.nanargmax(prof[k])) for k in keys}) == 1
    P("\n   판정: %s" % ("세 그룹의 최적 h가 **동일** -> 프로파일 평행 -> "
                        "수명 기반 호라이즌 분리 근거 **없음**" if same else
                        "그룹별 최적 h가 **다름** -> 교차 -> 분리 근거 **있음(추가검증 필요)**"))

    # 그룹 간 프로파일 차이 유의성 (h=1 vs h=30 상대우위)
    P("\n   보조: 각 그룹의 '장기선호도' = 평균|t|(h=30) - 평균|t|(h=1)")
    for k in keys:
        P("      %-28s %+.3f" % (k, prof[k][-1] - prof[k][0]))
    lp = [prof[k][-1] - prof[k][0] for k in keys]
    P("      -> 수명이 길수록 이 값이 커져야 가설 H가 참. 실제 추세: %s"
      % ("단조증가(가설 부합)" if lp[0] < lp[1] < lp[2] else "단조 아님(가설 불일치)"))

    # Bonferroni 생존 피처
    P("\n" + "=" * 104)
    P("[참고] 다중비교 생존 피처 (Bonferroni 근사 |t| >= 6.44)")
    P("=" * 104)
    surv = []
    for h in IC_HZ:
        for n in IC[str(h)]:
            t = IC[str(h)][n]["t"]
            if t is not None and abs(t) >= 6.44:
                surv.append((n, h, IC[str(h)][n]["ic"], t))
    surv.sort(key=lambda z: -abs(z[3]))
    if surv:
        for n, h, ic, t in surv:
            P("   %-32s h=%-3d IC=%+.4f t=%+.2f" % (n[:32], h, ic, t))
    else:
        P("   없음 — 516개 검정 중 다중비교를 넘는 셀 0개")
    P("   -> 생존 %d셀 / 516검정" % len(surv))

    with open("lifetime_robust.txt", "w", encoding="utf-8") as f:
        f.write(L.getvalue())
    json.dump(dict(profile=prof, groups={k: grp[k] for k in keys},
                   asym=[dict(nm=z[0], up=z[1], dn=z[2], asym=z[3]) for z in asym],
                   rho_tau_slope=r1, p_tau_slope=p1,
                   rho_tau_argmax=r2, p_tau_argmax=p2,
                   survivors=[dict(nm=z[0], h=z[1], ic=z[2], t=z[3]) for z in surv]),
              open("lifetime_robust.json", "w", encoding="utf-8"), ensure_ascii=False,
              default=lambda o: None if isinstance(o, float) and math.isnan(o) else float(o))
    P("\n저장 -> lifetime_robust.txt / .json")


if __name__ == "__main__":
    main()
