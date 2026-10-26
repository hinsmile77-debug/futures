import sys, os, json, statistics as st
sys.path.insert(0, os.environ["SCR"]); from causal_engine import *
D=json.load(open(os.environ["SCR"]+"/causal_full.json",encoding="utf-8"))["days"]
V=("SHADOW_V2","V2_F2","MAIN","MAIN_F2","SHADOW_E2F2","SHADOW_X4NF","SHADOW_X4NFA","SHADOW_ATRS")
out={}
for v in V:
    out[v]={}
    for d0 in D:
        c,f,l=inputs(d0); tr=[x for x in run_day_c(E.DayFrame(c,f),E.prepare_levels(l),v)["trades"] if x["status"]=="CLOSED"]
        out[v][d0]=dict(net=sum(E.trade_net(x) for x in tr)/1e4,n=len(tr),win=sum(1 for x in tr if E.trade_net(x)>0),
            tr=sum(1 for x in tr if any(g.get("reason")=="TR" for g in x["legs"])),sl=sum(1 for x in tr if all(g.get("reason")=="SL" for g in x["legs"])),
            trades=[dict(rule=x["rule"],stop=abs(x["entry_px"]-x["stop_init"]),l1=x["legs"][0]["net"],l2=x["legs"][1]["net"]) for x in tr])
json.dump(dict(days=D,res=out),open(os.environ["SCR"]+"/causal_2x2.json","w",encoding="utf-8"),ensure_ascii=False)
def mdd(xs):
    c=p=m=0
    for x in xs: c+=x;p=max(p,c);m=min(m,c-p)
    return m
for win,f in (("22일",lambda d:True),("전반",lambda d:d<="2026-10-07"),("후반",lambda d:d>"2026-10-07"),("v2창13일",lambda d:"2026-09-30"<=d<="2026-10-20"),("v3 4일",lambda d:d>="2026-10-21")):
    s={v:sum(out[v][d]["net"] for d in D if f(d)) for v in out}
    print("%-7s V2 %+7.1f | V2+F2 %+7.1f | MAIN %+7.1f | MAIN+F2 %+7.1f || TR44 효과: F2없이 %+6.1f · F2위에서 %+6.1f | F2 효과: 트레일없이 %+6.1f · 트레일위에서 %+6.1f"%(win,s["SHADOW_V2"],s["V2_F2"],s["MAIN"],s["MAIN_F2"],
      s["MAIN"]-s["SHADOW_V2"],s["MAIN_F2"]-s["V2_F2"],s["V2_F2"]-s["SHADOW_V2"],s["MAIN_F2"]-s["MAIN"]))
for v in V:
    xs=[out[v][d]["net"] for d in D]; n=sum(out[v][d]["n"] for d in D)
    print("%-13s 22일 %+7.1f 최악 %+6.1f MDD %+6.1f 효율 %5.2f | 거래 %d 승률 %.0f%% 트레일청산 %d 전손절 %d"%(v,sum(xs),min(xs),mdd(xs),st.mean(xs)/st.stdev(xs),n,100*sum(out[v][d]["win"] for d in D)/n,sum(out[v][d]["tr"] for d in D),sum(out[v][d]["sl"] for d in D)))
print("일별 MAIN+F2:"," ".join("%s %+.1f"%(d[5:],out["MAIN_F2"][d]["net"]) for d in D))
