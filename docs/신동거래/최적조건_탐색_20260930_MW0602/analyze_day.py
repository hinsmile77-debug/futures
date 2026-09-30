# -*- coding: utf-8 -*-
"""grid_20260930.json 분석 — 계열별 분포·파라미터 주변 효과."""
import json, os, statistics as stt, collections, sys
HERE = os.path.dirname(os.path.abspath(__file__))
r = json.load(open(os.path.join(HERE, "grid_20260930.json"), encoding="utf-8"))
M = 1e4
for f, rows in r["fam"].items():
    nets = sorted(z["net"] for z in rows)
    q = lambda p: nets[int(p * (len(nets) - 1))] / M
    print("== %s  n=%d  max %+.1f  p90 %+.1f  p75 %+.1f  med %+.1f  p25 %+.1f  min %+.1f  >0 %.0f%%" % (
        f, len(nets), nets[-1] / M, q(.9), q(.75), q(.5), q(.25), nets[0] / M, 100 * sum(x > 0 for x in nets) / len(nets)))
    keys = rows[0]["p"].keys()
    for k in keys:
        g = collections.defaultdict(list)
        for z in rows:
            g[str(z["p"][k])].append(z["net"])
        if len(g) > 1:
            print("   %-10s " % k + " | ".join("%s: med %+.0f max %+.0f" % (v, stt.median(x) / M, max(x) / M) for v, x in sorted(g.items())))
