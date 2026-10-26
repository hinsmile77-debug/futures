import sys, os, statistics as st, datetime as dt
sys.argv=[sys.argv[0],"2026-09-21","","x.json"]
exec(open(r"%s/causal_r3.py"%os.environ["SCR"],encoding="utf-8").read().split("out={}")[0])
D="2026-09-21,2026-09-22,2026-09-23,2026-09-28,2026-09-29,2026-09-30,2026-10-01,2026-10-02,2026-10-06,2026-10-07,2026-10-08,2026-10-12,2026-10-13,2026-10-14,2026-10-15,2026-10-16,2026-10-19,2026-10-20,2026-10-21,2026-10-22,2026-10-23,2026-10-26".split(",")
V=["MAIN","SHADOW_V2","SHADOW_E2F2","SHADOW_X4NF","SHADOW_X4NFA","SHADOW_ATRS"]
FR={d0:inputs(d0) for d0 in D}
def mdd(xs):
    c=p=m=0
    for x in xs: c+=x;p=max(p,c);m=min(m,c-p)
    return m
for win,f in (("22일",lambda d:True),("v2창13일(09-30~10-20)",lambda d:"2026-09-30"<=d<="2026-10-20"),("v3 4일",lambda d:d>="2026-10-21")):
    print("==",win)
    for v in V:
        r={}
        for nm,fn in (("현행",E.run_day),("인과",run_day_c)):
            xs=[]
            for d0 in D:
                if not f(d0): continue
                c,ff,l=FR[d0]; res=fn(E.DayFrame(c,ff),E.prepare_levels(l),v)
                xs.append(sum(E.trade_net(x) for x in res["trades"] if x["status"]=="CLOSED")/1e4)
            r[nm]=xs
        a,b=r["현행"],r["인과"]
        print("  %-13s 현행 %+7.1f 최악 %+6.1f | 인과 %+7.1f 최악 %+6.1f MDD %+6.1f 효율 %s"%(v,sum(a),min(a),sum(b),min(b),mdd(b),("%.2f"%(st.mean(b)/st.stdev(b))) if len(b)>1 else "-"))
