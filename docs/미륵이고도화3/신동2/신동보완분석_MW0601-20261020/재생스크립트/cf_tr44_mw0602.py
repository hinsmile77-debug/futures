import sys, os, json
WT=sys.argv[1]; sys.path.insert(0, WT); DB=r"C:\Users\82108\PycharmProjects\futures\data\db"
from strategy.shindong import runner, spec
P=[os.path.join(DB,x) for x in ("raw_data.db","option_flow.db","premarket_levels.db")]
V=("MAIN","SHADOW_FLOWR60","SHADOW_V22S","SHADOW_HYBL")
out={}
for trail in ((6.0,4.0),(4.0,4.0)):
    spec.FLOW_TRAIL=trail
    k="%g/%g"%trail; out[k]={}
    for d in sys.argv[2].split(","):
        r=runner.compute(d,*P,live=False); row={}
        for v in V:
            tr=r["results"][v]["trades"]
            nets=[sum(g.get("net",0.0) for g in t["legs"] if not g.get("open",True)) for t in tr]
            row[v]=dict(net=sum(nets)/1e4,n=len(tr),w=sum(1 for x in nets if x>0),
                        tr=sum(1 for t in tr if any(g.get("reason")=="TR" for g in t["legs"])))
        out[k][d]=row
json.dump(out,open(sys.argv[3],"w"),indent=1); print("ok")
