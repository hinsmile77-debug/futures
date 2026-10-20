# -*- coding: utf-8 -*-
import sys, os, json
WT, dates, out_p, variants = sys.argv[1], sys.argv[2].split(","), sys.argv[3], sys.argv[4].split(",")
sys.path.insert(0, WT)
DB=r"C:\Users\82108\PycharmProjects\futures\data\db"
from strategy.shindong import runner
P=[os.path.join(DB,x) for x in ("raw_data.db","option_flow.db","premarket_levels.db")]
out={}
for d in dates:
    r=runner.compute(d,*P,live=False); row={"bias":r["results"]["MAIN"]["decision"].get("bias")}
    for v in variants:
        row[v]=[dict(rule=t["rule"],side=t["side"],e=str(t["entry_ts"])[-5:],px=t["entry_px"],lv=t.get("touch_level"),stop=t.get("stop_init"),t1=t.get("t1"),t2=t.get("t2"),
                     x=t.get("exit_ts"),why="/".join(g.get("reason") or "" for g in t["legs"]),
                     net=sum(g.get("net",0.0) for g in t["legs"] if not g.get("open",True))/1e4) for t in r["results"][v]["trades"]]
    out[d]=row
json.dump(out,open(out_p,"w",encoding="utf-8"),ensure_ascii=False); print("ok",len(out))
