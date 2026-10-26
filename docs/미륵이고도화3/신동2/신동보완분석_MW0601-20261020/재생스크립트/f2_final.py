# -*- coding: utf-8 -*-
import sys, os, json, statistics as st, sqlite3
sys.path.insert(0, os.environ["SCR"])
exec(open(os.path.join(os.environ["SCR"],"f2_pnl.py"),encoding="utf-8").read().split("D=json.load")[0])   # run_day_h · HOOK · FF
D=json.load(open(os.environ["SCR"]+"/causal_full.json",encoding="utf-8"))["days"]
FR={}
for d0 in D:
    c,f,l=inputs(d0); FR[d0]=(E.DayFrame(c,f),E.prepare_levels(l))
F2N="F2(현행: 09:00 대비 >0, 0→매수)"; F2X="조합: F2±50 ∧ 가격 EMA20−60"
SER={"현행재생 MAIN":("cur","MAIN",None),"인과 MAIN":("h","MAIN",None),"①SHADOW_F2":("h","SHADOW_V2",F2N),"②SHADOW_F2X":("h","MAIN",F2X)}
out={}
for nm,(eng,base,filt) in SER.items():
    out[nm]={}
    for d0 in D:
        d,L=FR[d0]
        if eng=="cur": res=E.run_day(d,L,base)
        else:
            HOOK["filt"]=FF.build(d)[filt] if filt else None; HOOK["neutral"]="pass"; res=run_day_h(d,L,base)
        tr=[x for x in res["trades"] if x["status"]=="CLOSED"]
        out[nm][d0]=[dict(rule=x["rule"],side=x["side"],e=x["entry_ts"],stop=abs(x["entry_px"]-x["stop_init"]),l1=x["legs"][0]["net"],l2=x["legs"][1]["net"],
                          why="/".join(g.get("reason") or "" for g in x["legs"])) for x in tr]
json.dump(dict(days=D,trades=out),open(os.environ["SCR"]+"/f2_final.json","w",encoding="utf-8"),ensure_ascii=False)
print("ok")
