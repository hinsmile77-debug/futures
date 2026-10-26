import sys, os, json, statistics as st, sqlite3
sys.argv=[sys.argv[0],"2026-09-21","","x.json"]
code=open(r"%s/causal_r3.py"%os.environ["SCR"],encoding="utf-8").read().split("out={}")[0]
code=code.replace('src=(src[:a]+R3_CAUSAL+src[b:]).replace("def run_day(","def run_day_c(",1)',
 'src=(src[:a]+R3_CAUSAL+src[b:]).replace("def run_day(","def run_day_c(",1).replace(\'e2 = f2 = variant == "SHADOW_E2F2"\',\'e2 = variant == "SHADOW_E2F2"; f2 = variant in ("SHADOW_E2F2", "MAIN_F2")\').replace(\'elif variant in ("MAIN", "SHADOW_ATRS"):\',\'elif variant in ("MAIN", "SHADOW_ATRS", "MAIN_F2"):\')')
exec(code)
D="2026-09-21,2026-09-22,2026-09-23,2026-09-28,2026-09-29,2026-09-30,2026-10-01,2026-10-02,2026-10-06,2026-10-07,2026-10-08,2026-10-12,2026-10-13,2026-10-14,2026-10-15,2026-10-16,2026-10-19,2026-10-20,2026-10-21,2026-10-22,2026-10-23,2026-10-26".split(",")
V=["MAIN","MAIN_F2","SHADOW_V2","SHADOW_E2F2","SHADOW_X4NF","SHADOW_X4NFA","SHADOW_ATRS"]
out={"days":D,"causal":{},"current_main":{},"trades":{}}
for d0 in D:
    c,f,l=inputs(d0); L=E.prepare_levels(l); d=E.DayFrame(c,f)
    out["current_main"][d0]=sum(E.trade_net(x) for x in E.run_day(d,L,"MAIN")["trades"] if x["status"]=="CLOSED")/1e4
    for v in V:
        tr=[x for x in run_day_c(d,L,v)["trades"] if x["status"]=="CLOSED"]
        out["causal"].setdefault(v,{})[d0]=sum(E.trade_net(x) for x in tr)/1e4
        if v in ("MAIN","MAIN_F2"):
            out["trades"].setdefault(v,{})[d0]=[dict(rule=x["rule"],stop=abs(x["entry_px"]-x["stop_init"]),l1=x["legs"][0]["net"],l2=x["legs"][1]["net"],e=x["entry_ts"]) for x in tr]
json.dump(out,open(os.environ["SCR"]+"/causal_full.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print("ok")
