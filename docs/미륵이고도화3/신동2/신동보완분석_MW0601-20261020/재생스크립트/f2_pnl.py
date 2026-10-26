# -*- coding: utf-8 -*-
import sys, os, json, re, inspect, statistics as st
sys.path.insert(0, os.environ["SCR"])
import causal_engine as CE
from causal_engine import E, S, inputs
import f2_filters as FF
src=inspect.getsource(E.run_day)
a=src.index("    # R3\n"); b=src.index('    return {"decision": dec, "trades": trades}')
R3=CE.R3_CAUSAL
old='''        if f2:
            if t not in d.sp:
                return None
            base = d.sp.get(S.CONF_BASE)
            trend = -1 if (base is not None and d.sp[t] - base > 0) else 1
            if side != trend:
                return None
'''
assert R3.count(old)==1
new='''        if HOOK["filt"] is not None:
            v = HOOK["filt"](t)
            if v == 0 and HOOK["neutral"] == "block":
                return None
            if v != 0 and side != v:
                return None
'''
src=src[:a]+R3.replace(old,new)+src[b:]
src=CE.sub1(src,"def run_day(","def run_day_h(")
ns=E.__dict__; HOOK={"filt":None,"neutral":"pass"}; ns["HOOK"]=HOOK; exec(src,ns); run_day_h=ns["run_day_h"]
D=json.load(open(os.environ["SCR"]+"/causal_full.json",encoding="utf-8"))["days"]
FR={}
for d0 in D:
    c,f,l=inputs(d0); FR[d0]=(E.DayFrame(c,f),E.prepare_levels(l))
def mdd(xs):
    c=p=m=0
    for x in xs: c+=x;p=max(p,c);m=min(m,c-p)
    return m
names=list(FF.build(FR[D[0]][0]).keys())
res={}
print("%-34s %-5s %-6s | %8s %7s %7s %5s | %7s %7s | %7s"%("필터","중립","바탕","22일","최악","MDD","효율","전반","후반","v3 4일"))
for base in ("SHADOW_V2","MAIN"):
    for nm in [None]+names:
        for neu in (("pass","block") if nm and nm!=names[0] else ("pass",)):
            xs=[]
            for d0 in D:
                d,L=FR[d0]
                HOOK["filt"]=FF.build(d)[nm] if nm else None; HOOK["neutral"]=neu
                xs.append(sum(E.trade_net(x) for x in run_day_h(d,L,base)["trades"] if x["status"]=="CLOSED")/1e4)
            h1=sum(x for x,d0 in zip(xs,D) if d0<="2026-10-07"); h2=sum(x for x,d0 in zip(xs,D) if d0>"2026-10-07"); v3=sum(x for x,d0 in zip(xs,D) if d0>="2026-10-21")
            key="%s|%s|%s"%(base,nm or "필터 없음",neu); res[key]=xs
            print("%-34s %-5s %-6s | %+8.1f %+7.1f %+7.1f %5.2f | %+7.1f %+7.1f | %+7.1f"%((nm or "필터 없음")[:34],neu if nm else "-", "V2" if base=="SHADOW_V2" else "MAIN",sum(xs),min(xs),mdd(xs),st.mean(xs)/st.stdev(xs),h1,h2,v3))
json.dump(dict(days=D,res=res),open(os.environ["SCR"]+"/f2_pnl.json","w",encoding="utf-8"),ensure_ascii=False)
