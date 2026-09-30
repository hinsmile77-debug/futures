# -*- coding: utf-8 -*-
"""후보 조합의 흐름 6일 일별 손익 + 계열 내 r1 조합 분포."""
import json, os, statistics as stt, collections
HERE = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(os.path.join(HERE, "grid_all.json"), encoding="utf-8"))
FD = ["2026-09-21", "2026-09-22", "2026-09-23", "2026-09-28", "2026-09-29", "2026-09-30"]
MAIN = [-61.7, 163.0, 182.4, 33.0, -103.8, -51.2]
C = {
 "A 9/30최적": ("A", {"T": "09:05", "stop": None, "tp": 20, "trail": [8, 8]}),
 "A 10:00·손절12·트레일12/3": ("A", {"T": "10:00", "stop": 12, "tp": None, "trail": [12, 3]}),
 "C 9/30최적": ("C", {"K": 200, "flip_exit": False, "max_trades": 1, "stop": None, "tp": 20, "trail": [8, 8]}),
 "C 6일최적": ("C", {"K": 300, "flip_exit": False, "max_trades": 3, "stop": None, "tp": 12, "trail": [6, 4]}),
 "D 9/30최적(r1)": ("D", {"b": 2, "filt": "r1", "max_trades": 5, "tp": 8, "trail": [4, 3]}),
 "D 6일최적(none)": ("D", {"b": 2, "filt": "none", "max_trades": 3, "tp": 25, "trail": [8, 6]}),
 "B 6일최적": ("B", {"N": 5, "filt": "none", "max_trades": 3, "stop": 8, "tp": 12, "trail": [4, 3]}),
}
idx = {}
for d in FD:
    for f, rows in G[d]["fam"].items():
        for p, net, n in rows:
            idx[(d, f, p)] = (net, n)
print("%-28s " % "" + " ".join("%9s" % d[5:] for d in FD) + "      합")
print("%-28s " % "현행 MAIN" + " ".join("%+9.1f" % x for x in MAIN) + " %+8.1f" % sum(MAIN))
for name, (f, p) in C.items():
    k = json.dumps(p, sort_keys=True)
    v = [idx.get((d, f, k)) for d in FD]
    print("%-28s " % name + " ".join(("%+6.1f(%d)" % (x[0] / 1e4, x[1])) if x else "        -" for x in v)
          + " %+8.1f" % (sum(x[0] for x in v if x) / 1e4))
# 계열 D r1 전 조합: 9/30 외 방향일 3일 합의 분포
for fam, filt in (("D", "r1"), ("A", None), ("C", None)):
    agg = collections.defaultdict(float); n930 = {}
    for (d, f, p), (net, n) in idx.items():
        if f != fam or (filt and json.loads(p).get("filt") != filt):
            continue
        if d == "2026-09-30":
            n930[p] = net
        else:
            agg[p] += net
    xs = sorted(agg[p] for p in n930)
    print("%s%s 전 조합 %d: 9/30 외 합 중앙 %+.1f만 · 흑자 %.0f%% · p10 %+.1f · p90 %+.1f" % (
        fam, "(" + filt + ")" if filt else "", len(xs), stt.median(xs) / 1e4, 100 * sum(x > 0 for x in xs) / len(xs),
        xs[len(xs) // 10] / 1e4, xs[9 * len(xs) // 10] / 1e4))
