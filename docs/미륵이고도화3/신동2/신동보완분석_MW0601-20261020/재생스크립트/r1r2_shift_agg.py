# -*- coding: utf-8 -*-
import json, sys, random
from collections import defaultdict
rows = json.load(open(sys.argv[1], encoding="utf-8"))
g = defaultdict(list)
for r in rows:
    g[(r["T"], r["S"])].append(r)

def sign(x): return 0 if not x else (1 if x > 0 else -1)

print("== R1 방향 적중 (T별 — S와 무관) ==")
print("T      결정일 적중(09:00→15:05) 적중(결정시점→15:05)  보류")
seenT = {}
for (T, Sx), rs in sorted(g.items()):
    if T in seenT: continue
    seenT[T] = 1
    dec = [r for r in rs if r["bias"]]
    h1 = [sign(r["mv_fix"]) == r["bias"] for r in dec if r["mv_fix"]]
    h2 = [sign(r["mv_dec"]) == r["bias"] for r in dec if r["mv_dec"]]
    pts = sum(r["bias"] * (r["mv_dec"] or 0) for r in dec)
    print("%s  %2d   %2d/%2d=%4.0f%%   %2d/%2d=%4.0f%%  방향pt합 %+7.1f  보류 %d"
          % (T, len(dec), sum(h1), len(h1), 100*sum(h1)/max(1,len(h1)), sum(h2), len(h2),
             100*sum(h2)/max(1,len(h2)), pts, len(rs)-len(dec)))

print()
print("== R2 확정·손익 (가상 2계약, 만원) — 행 T / 열 S ==")
res = {}
for (T, Sx), rs in sorted(g.items()):
    r2 = [r for r in rs if r["r2_n"]]
    net = sum(r["r2_net"] for r in rs) / 1e4
    win = sum(1 for r in r2 if r["r2_net"] > 0)
    worst = min([r["r2_net"] for r in r2] or [0]) / 1e4
    tot = sum(r["r2_net"] + r["r3_net"] for r in rs) / 1e4
    daily = [ (r["r2_net"] + r["r3_net"]) / 1e4 for r in rs]
    res[(T, Sx)] = dict(n=len(r2), win=win, net=net, worst=worst, tot=tot, dworst=min(daily),
                        r2days={r["day"]: r["r2_net"]/1e4 for r in rs})
Ts = sorted({k[0] for k in g}); Ss = sorted({k[1] for k in g})
for lab, key, fmt in (("R2 거래수(승)", None, None), ("R2 순손익", "net", "%+8.1f"),
                      ("R2 최악거래", "worst", "%+8.1f"), ("MAIN 전체(R2+R3) 순손익", "tot", "%+8.1f"),
                      ("MAIN 최악일", "dworst", "%+8.1f")):
    print("--", lab)
    print("T\\S    " + "  ".join("%8s" % s for s in Ss))
    for T in Ts:
        if key is None:
            print(T + "  " + "  ".join("%8s" % ("%d(%d)" % (res[(T,s)]["n"], res[(T,s)]["win"])) for s in Ss))
        else:
            print(T + "  " + "  ".join(fmt % res[(T,s)][key] for s in Ss))

# 부트스트랩: 최선 R2 조합이 현행(08:59/09:01) 대비 앞설 확률
base = res[("08:59", "09:01")]
best = max(res.items(), key=lambda kv: kv[1]["net"])
print()
print("현행 08:59/09:01 R2 %+.1f만 · 최선 %s/%s R2 %+.1f만" % (base["net"], best[0][0], best[0][1], best[1]["net"]))
days = sorted(base["r2days"])
random.seed(1)
B = 4000; wins = 0
# 그리드 전체 최대치의 부트스트랩(선택 편향 포함): 매 재표본에서 최선 조합 순손익 − 현행
excess = []
for _ in range(B):
    smp = [random.choice(days) for _ in days]
    b = sum(base["r2days"][d] for d in smp)
    m = max(sum(v["r2days"][d] for d in smp) for v in res.values())
    bb = sum(best[1]["r2days"][d] for d in smp)
    wins += bb > b
    excess.append(m - b)
excess.sort()
print("부트스트랩 %d회: 최선조합 > 현행 %.0f%% · (그리드최대−현행) 중앙 %+.1f만 · 90%% 구간 %+.1f–%+.1f"
      % (B, 100*wins/B, excess[B//2], excess[int(B*.05)], excess[int(B*.95)]))

print()
print("== 일별 R2 (현행 vs 최선) ==")
for d in days:
    rb = [r for r in g[("08:59","09:01")] if r["day"]==d][0]
    rx = [r for r in g[best[0]] if r["day"]==d][0]
    print(d, "현행 bias%+d %s %s %+7.1f | 최선 bias%+d %s %s %+7.1f" % (
        rb["bias"] or 0, rb["r2"], rb["r2_ts"], rb["r2_net"]/1e4,
        rx["bias"] or 0, rx["r2"], rx["r2_ts"], rx["r2_net"]/1e4))
json.dump({"%s|%s" % k: {kk: vv for kk, vv in v.items() if kk != "r2days"} for k, v in res.items()},
          open(sys.argv[1].replace(".json", "_agg.json"), "w"), ensure_ascii=False)
