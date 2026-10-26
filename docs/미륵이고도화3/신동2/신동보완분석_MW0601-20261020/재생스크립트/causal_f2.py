import sys, os, statistics as st
sys.argv=[sys.argv[0],"2026-09-21","","x.json"]
code=open(r"%s/causal_r3.py"%os.environ["SCR"],encoding="utf-8").read().split("out={}")[0]
code=code.replace('src=(src[:a]+R3_CAUSAL+src[b:]).replace("def run_day(","def run_day_c(",1)',
 'src=(src[:a]+R3_CAUSAL+src[b:]).replace("def run_day(","def run_day_c(",1).replace(\'e2 = f2 = variant == "SHADOW_E2F2"\',\'e2 = variant == "SHADOW_E2F2"; f2 = variant in ("SHADOW_E2F2", "MAIN_F2")\').replace(\'elif variant in ("MAIN", "SHADOW_ATRS"):\',\'elif variant in ("MAIN", "SHADOW_ATRS", "MAIN_F2"):\')')
exec(code)
D="2026-09-21,2026-09-22,2026-09-23,2026-09-28,2026-09-29,2026-09-30,2026-10-01,2026-10-02,2026-10-06,2026-10-07,2026-10-08,2026-10-12,2026-10-13,2026-10-14,2026-10-15,2026-10-16,2026-10-19,2026-10-20,2026-10-21,2026-10-22,2026-10-23,2026-10-26".split(",")
FR={d0:inputs(d0) for d0 in D}
def mdd(xs):
    c=p=m=0
    for x in xs: c+=x;p=max(p,c);m=min(m,c-p)
    return m
for v in ("MAIN","MAIN_F2","SHADOW_E2F2"):
    xs={d0:sum(E.trade_net(x) for x in run_day_c(E.DayFrame(FR[d0][0],FR[d0][1]),E.prepare_levels(FR[d0][2]),v)["trades"] if x["status"]=="CLOSED")/1e4 for d0 in D}
    for win,f in (("22일",lambda d:True),("전반 09-21~10-07",lambda d:d<="2026-10-07"),("후반 10-08~10-26",lambda d:d>"2026-10-07"),("v3 4일",lambda d:d>="2026-10-21")):
        a=[xs[d] for d in D if f(d)]
        print("%-12s %-18s 합 %+7.1f 최악 %+6.1f MDD %+6.1f 효율 %.2f"%(v,win,sum(a),min(a),mdd(a),st.mean(a)/st.stdev(a)))
