# -*- coding: utf-8 -*-
"""신동 목표 함수 v1 vs v2 비교 — 흐름일(엔진 run_day) + 가격 대리(r3lab, R3 만). 읽기 전용."""
import sys, os, random, json
ROOT = r"C:\Users\82108\PycharmProjects\futures"
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "docs", "신동거래", "r3_딥다이브_20260929_MW0602"))
from strategy.shindong import engine as E, spec as S
import r3lab as R

V2 = E.targets
V1 = E.targets_v1


def use(fn):
    E.targets = fn


def closed_net(res):
    return [E.trade_net(t) if "legs" in t else t.get("net_krw") for t in res["trades"]
            if t.get("status") == "CLOSED"]


# ── 1. 흐름일 전 변형 ──────────────────────────────────────────────
ds = R.dates()
flow = []
for d in ds:
    P = R.load_day(d)
    if P and P["has_flow"]:
        flow.append(d)
print("FLOW_DAYS", flow)
rows = {}
for d in flow:
    P = R.load_day(d)
    for tag, fn in (("v1", V1), ("v2", V2)):
        use(fn)
        for v in S.VARIANTS:
            res = E.run_day(P["D"], P["L"], v)
            tr = [t for t in res["trades"] if t.get("status") == "CLOSED"]
            net = sum(E.trade_net(t) for t in tr)
            rows[(d, v, tag)] = (round(net), len(tr), sum(1 for t in tr if E.trade_net(t) > 0))
use(V2)
for d in flow:
    print(d, " | ".join("%s %s→%s" % (v, rows[(d, v, "v1")][0], rows[(d, v, "v2")][0]) for v in S.VARIANTS))
tot = {}
for v in S.VARIANTS:
    tot[v] = (sum(rows[(d, v, "v1")][0] for d in flow), sum(rows[(d, v, "v2")][0] for d in flow))
print("FLOW_TOTAL", tot)

# ── 2. 가격 대리(R3 만) ────────────────────────────────────────────
out = {}
diffs = {}
for x in (0.5, 1.0, 1.5):
    for x4 in (False, True):
        key = "px%.1f%s" % (x, "+X4NF" if x4 else "")
        per = {}
        for tag, fn in (("v1", V1), ("v2", V2)):
            use(fn)
            day = {}
            ntr = win = 0
            for d in ds:
                if R.load_day(d) is None:
                    continue
                tr = R.run_r3(d, signal="px", x=x, x4nf=x4)
                day[d] = sum(t["net"] for t in tr)
                ntr += len(tr); win += sum(1 for t in tr if t["net"] > 0)
            per[tag] = (day, ntr, win)
        use(V2)
        d1, d2 = per["v1"][0], per["v2"][0]
        dd = [d2[d] - d1[d] for d in d1]
        changed = [d for d in d1 if abs(d2[d] - d1[d]) > 0.5]
        # 일 단위 부트스트랩 P(Δ≤0)
        random.seed(7)
        n = len(dd); bs = 0
        for _ in range(5000):
            s = sum(dd[random.randrange(n)] for _ in range(n))
            bs += s <= 0
        half = n // 2
        ks = sorted(d1)
        out[key] = dict(days=n, v1=round(sum(d1.values())), v2=round(sum(d2.values())),
                        v1_trades=per["v1"][1], v2_trades=per["v2"][1],
                        v1_win=per["v1"][2], v2_win=per["v2"][2],
                        changed_days=len(changed),
                        worst_v1=round(min(d1.values())), worst_v2=round(min(d2.values())),
                        h1=round(sum(d2[k] - d1[k] for k in ks[:half])),
                        h2=round(sum(d2[k] - d1[k] for k in ks[half:])),
                        p_le0=round(bs / 5000.0, 3),
                        top_changed=sorted(((round(d2[d] - d1[d]), d) for d in changed))[:3]
                        + sorted(((round(d2[d] - d1[d]), d) for d in changed))[-3:])
        print(key, json.dumps(out[key], ensure_ascii=False))
print("RANGE", ds[0], ds[-1], len(ds))
