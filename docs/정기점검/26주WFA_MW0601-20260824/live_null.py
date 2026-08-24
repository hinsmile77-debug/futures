# -*- coding: utf-8 -*-
"""[MW0601 490차 후속3] 순수 라이브 L2 합격 9셀에 대한 두 가지 통제.

통제 A — 노이즈 하한선(455차 N3 방법론, 규모만 확대):
  실피처 86개 각각의 **위상 무작위화 쌍둥이**를 만들어 같은 L2 검정에 태운다.
  위상 무작위화는 진폭 스펙트럼(=자기상관 구조)을 보존하고 위상만 파괴하므로,
  "자기상관이 강한 계열이 우연히 만들어내는 손익"의 분포를 그대로 준다.
  노이즈가 몇 셀 합격하는지가 곧 **우연 합격 기대치**다.

통제 B — 방향 드리프트:
  이 창(2026-06~08)에 시장이 한쪽으로 흘렀다면, 그 방향과 상관된 아무 피처나
  "돈을 번다". 항상 LONG / 항상 SHORT(같은 비중복 규칙)의 손익을 기준선으로 낸다.
"""
from __future__ import print_function
import io, json, os, sys, math
import numpy as np
from collections import OrderedDict, defaultdict

_ROOT = r"C:\Users\82108\PycharmProjects\futures"
sys.path.insert(0, _ROOT)
sys.stdout.reconfigure(encoding="utf-8")
from utils.dll_bootstrap import ensure_conda_dll_path
ensure_conda_dll_path()

from scripts.core_feature_discovery import build_matrix, tstat
from scripts.horizon_signal_tradability import evaluate, roundtrip_cost_pt
from scripts.noise_benchmark import phase_randomize, shuffle_column
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from live_only import load_live, PT_VALUE

HZ = [1, 3, 5, 10, 15, 30]


def cells_of(res):
    out = []
    for (nm, h), r in res.items():
        for tag, sgn in (("plus", 1), ("minus", -1)):
            s = r[tag]
            if s["t"] is None:
                continue
            out.append(dict(nm=nm, h=h, sgn=sgn, net=s["net_per_day"], t=s["t"],
                            h1=s["net_h1"], h2=s["net_h2"], ntr=r["n_trades"]))
    return out


def passed(cells):
    return [c for c in cells if c["net"] > 0 and abs(c["t"]) >= 2.0
            and c["h1"] is not None and c["h1"] > 0 and c["h2"] > 0]


def main():
    feats, closes, dates = load_live()
    names, X, ts_list = build_matrix(feats, verbose=False)
    avg = float(np.mean([closes[t] for t in ts_list if t in closes]))
    cost = roundtrip_cost_pt(avg)
    print("순수 라이브 %d일 · 피처 %d개 · 왕복비용 %.4fpt" % (len(dates), len(names), cost))

    # ── 통제 B: 방향 드리프트 기준선 ────────────────────────────────
    by_day = defaultdict(list)
    for i, t in enumerate(ts_list):
        by_day[t[:10]].append(i)
    day_rows = {d: r for d, r in by_day.items() if len(r) >= 60}
    days = sorted(day_rows)
    cl = {i: closes[t] for i, t in enumerate(ts_list) if t in closes}
    print("\n=== 통제 B — 항상 LONG / 항상 SHORT (같은 비중복 규칙, 비용 차감) ===")
    print("%3s %8s %12s %12s %9s %12s %12s %9s"
          % ("h", "거래/일", "LONG net/일", "LONG(원)", "t", "SHORT net/일", "SHORT(원)", "t"))
    drift = {}
    for h in HZ:
        dg, dn = {}, {}
        for d, rows in day_rows.items():
            g, n, k = 0.0, 0, 0
            while k + h < len(rows):
                g += cl[rows[k + h]] - cl[rows[k]]
                n += 1
                k += h
            dg[d], dn[d] = g, n
        gross = np.array([dg[d] for d in days]); ntr = np.array([dn[d] for d in days])
        lo = gross - ntr * cost
        sh = -gross - ntr * cost
        tl, _ = tstat(list(lo)); ts_, _ = tstat(list(sh))
        drift[h] = dict(long_net=float(lo.mean()), long_t=tl,
                        short_net=float(sh.mean()), short_t=ts_,
                        gross=float(gross.mean()), ntr=float(ntr.mean()))
        print("%3d %8.1f %12.4f %12.0f %9.2f %12.4f %12.0f %9.2f"
              % (h, ntr.mean(), lo.mean(), lo.mean() * PT_VALUE, tl,
                 sh.mean(), sh.mean() * PT_VALUE, ts_))
    print("  (gross = 순수 시장 이동. 일평균 %+.4fpt/일 @h=30 → 이 창의 방향 드리프트)"
          % drift[30]["gross"])

    # ── 통제 A: 위상 무작위 노이즈 쌍둥이 ──────────────────────────
    seed = int(dates[-1].replace("-", ""))
    rng = np.random.RandomState(seed % (2 ** 31 - 1))
    nz_names, nz_cols = [], []
    for j, nm in enumerate(names):
        col = X[:, j]
        if np.isfinite(col).sum() < 30:
            continue
        nz_names.append("noise_phase_%s" % nm)
        nz_cols.append(phase_randomize(col, rng))
    Xn = np.column_stack(nz_cols)
    print("\n=== 통제 A — 위상 무작위 노이즈 %d개 (실피처 %d개의 쌍둥이) ==="
          % (len(nz_names), len(names)))
    res_n = evaluate(nz_names, Xn, ts_list, closes, HZ, cost)[0]
    cn = cells_of(res_n); pn = passed(cn)
    res_r = evaluate(names, X, ts_list, closes, HZ, cost)[0]
    cr = cells_of(res_r); pr = passed(cr)

    print("%-10s %8s %10s %10s %12s %14s"
          % ("표본", "셀수", "net>0", "|t|>=2", "전후반양수", "**합격**"))
    for tag, c, p in (("실피처", cr, pr), ("노이즈", cn, pn)):
        print("%-10s %8d %10d %10d %12d %14d"
              % (tag, len(c), len([x for x in c if x["net"] > 0]),
                 len([x for x in c if x["net"] > 0 and abs(x["t"]) >= 2]),
                 len([x for x in c if x["net"] > 0 and x["h1"] is not None and x["h1"] > 0 and x["h2"] > 0]),
                 len(p)))
    print("\n  노이즈 합격 셀 (=우연히 통과한 가짜):")
    for c in sorted(pn, key=lambda c: -c["net"])[:12]:
        print("    %-34s h=%-3d %+d  net/일 %8.4fpt (%9.0f원)  t=%.2f"
              % (c["nm"], c["h"], c["sgn"], c["net"], c["net"] * PT_VALUE, c["t"]))
    if not pn:
        print("    없음")
    nz_max = max([abs(c["t"]) for c in cn if c["net"] > 0] or [0])
    nz_maxnet = max([c["net"] for c in cn] or [0])
    print("\n  노이즈 하한선: 양수 net 중 최대 |t| = %.2f | 최대 net/일 = %.4fpt (%.0f원)"
          % (nz_max, nz_maxnet, nz_maxnet * PT_VALUE))
    print("  → 실피처 합격 %d셀 중 이 하한선을 넘는 것: %d셀"
          % (len(pr), len([c for c in pr if abs(c["t"]) > nz_max and c["net"] > nz_maxnet])))
    for c in sorted(pr, key=lambda c: -c["net"]):
        mark = "OK " if (abs(c["t"]) > nz_max and c["net"] > nz_maxnet) else "미달"
        print("    [%s] %-26s h=%-3d %+d  net %8.4fpt  t=%.2f" % (mark, c["nm"], c["h"], c["sgn"], c["net"], c["t"]))

    json.dump({"drift": drift, "noise_pass": len(pn), "real_pass": len(pr),
               "noise_max_t": nz_max, "noise_max_net": nz_maxnet,
               "real_passed": pr, "noise_passed": pn},
              io.open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, default=float)
    print("\nJSON: %s" % sys.argv[1])
    return 0


if __name__ == "__main__":
    sys.exit(main())
