# -*- coding: utf-8 -*-
"""핵심 후보 일별·거래 내역 (가드 = 기록 그대로)."""
import sys
sys.argv = [sys.argv[0]]
import stop_reentry_cf as M
for lab, days in (("평가", M.EVAL), ("보류", M.HOLD)):
    data = M.load(days)
    keys = [("atr", 0.6, "halt", 3), ("atr", 0.6, "same", 3), ("atr", 0.4, "same", 3), ("pt", 3, "halt", 3), ("pt", 3, "rearm", 6)]
    print("\n[%s] 일별(만): " % lab + " | ".join("%s%g/%s/%d" % k for k in keys))
    allt = {k: [] for k in keys}
    for day, (d, L, bias, _a) in data.items():
        row = []
        for k in keys:
            t = M.run(d, L, bias, day >= M.V22_FROM, (k[0], k[1]), k[2], k[3]) or []
            row.append(sum(x["net"] for x in t) / 1e4)
            allt[k] += [dict(x, day=day) for x in t]
        print("  %s %+d " % (day[5:], bias) + " ".join("%8.1f" % v for v in row))
    if lab == "평가":
        for k in keys[1:3]:
            print("\n  [거래] %s%g/%s/%d" % k)
            for t in allt[k]:
                print("   %s %s→%s %+d %-4s %+6.2fpt %+7.1f만" % (t["day"][5:], t["t"], t["x"], t["side"], t["why"], t["pts"], t["net"] / 1e4))
