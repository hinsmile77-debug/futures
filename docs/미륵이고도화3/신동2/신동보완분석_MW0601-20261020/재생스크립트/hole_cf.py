# -*- coding: utf-8 -*-
"""10-23 구멍 대책 반사실 — engine.run_day 사본에 갈고리를 걸어 MAIN(v3) 재생. 읽기 전용."""
import sys, os, json, inspect, statistics as st
ROOT=r"C:\Users\82108\PycharmProjects\futures"; sys.path.insert(0, ROOT)
from strategy.shindong import engine as E, runner, spec as S
src=inspect.getsource(E.run_day)
a='''                t1, t2 = targets(L, conf, bias, e)
                tr = run_trade(d, bias, conf, ex, t1, t2, e2=e2)
                tr.update(rule="R2", touch_level=None)
                trades.append(tr)
                busy = tr["exit_ts"] or "99:99"'''
b='''                t1, t2 = targets(L, conf, bias, e)
                if not HOOK["r2_skip"](d, L, conf, bias, e, ex):
                    tr = run_trade(d, bias, conf, ex, t1, t2, e2=e2, trail=HOOK["r2_trail"])
                    tr.update(rule="R2", touch_level=None)
                    trades.append(tr)
                    busy = tr["exit_ts"] or "99:99"'''
assert src.count(a)==1; src=src.replace(a,b)
a2='''        t1, t2 = (targets_x4 if x4nf else targets)(L, ent, side, e)'''
b2='''        if HOOK["r3_skip"](d, L, ent, side, e, stop, trades):
            continue
        t1, t2 = (targets_x4 if x4nf else targets)(L, ent, side, e)'''
assert src.count(a2)==1; src=src.replace(a2,b2).replace("def run_day(","def run_day_h(",1)
ns=E.__dict__; HOOK={}; ns["HOOK"]=HOOK; exec(src, ns); run_day_h=ns["run_day_h"]
DB=os.path.join(ROOT,"data","db"); P=[os.path.join(DB,x) for x in ("raw_data.db","option_flow.db","premarket_levels.db")]
from strategy.shindong.calendar import select_flow_product
import datetime as dt
DAYS="2026-09-21,2026-09-22,2026-09-23,2026-09-28,2026-09-29,2026-09-30,2026-10-01,2026-10-02,2026-10-06,2026-10-07,2026-10-08,2026-10-12,2026-10-13,2026-10-14,2026-10-15,2026-10-16,2026-10-19,2026-10-20,2026-10-21,2026-10-22,2026-10-23".split(",")
FR={}
for d0 in DAYS:
    prod=select_flow_product(dt.date.fromisoformat(d0))[0]
    c,f,l=runner.load_inputs(d0,prod,*P); FR[d0]=(E.DayFrame(c,f),E.prepare_levels(l))
def closed_before(trades,t): return [x for x in trades if x["exit_ts"] and x["exit_ts"]<=t]
def net(x): return E.trade_net(x)
def atr(L): a=(L.get("0850") or {}).get("atr14"); return float(a) if a else None
NO=lambda *a,**k: False
CASES={
 "기준(현행 MAIN)": dict(),
 "A R2 트레일 4/4": dict(r2_trail=(4.0,4.0)),
 "A' R2 트레일 6/4": dict(r2_trail=(6.0,4.0)),
 "B R2 손절>0.25ATR 이면 생략": dict(r2_skip=lambda d,L,t,s,e,ex: atr(L) is not None and abs(e-ex)>0.25*atr(L)),
 "C R2 끄기": dict(r2_skip=lambda *a: True),
 "D 2연속 손절 뒤 30분 쉼": dict(r3_skip=lambda d,L,t,s,e,stp,tr: (lambda cb: len(cb)>=2 and net(cb[-1])<0 and net(cb[-2])<0 and (dt.datetime.strptime(t,"%H:%M")-dt.datetime.strptime(cb[-1]["exit_ts"],"%H:%M")).seconds<1800)(closed_before(tr,t))),
 "E R3 09:00 이후 가격 방향만": dict(r3_skip=lambda d,L,t,s,e,stp,tr: "09:00" in d.c and s*(e-d.c["09:00"])<0),
 "F 일손실 -150만 뒤 중단": dict(r3_skip=lambda d,L,t,s,e,stp,tr: sum(net(x) for x in closed_before(tr,t))<=-1.5e6),
 "A+D": dict(r2_trail=(4.0,4.0), r3_skip=None),
}
CASES["A+D"]["r3_skip"]=CASES["D 2연속 손절 뒤 30분 쉼"]["r3_skip"]
out={}
for name,cfg in CASES.items():
    HOOK.clear(); HOOK.update(r2_skip=NO, r3_skip=NO, r2_trail=None); HOOK.update({k:v for k,v in cfg.items() if v is not None})
    rows={}
    for d0 in DAYS:
        d,L=FR[d0]; res=run_day_h(d,L,"MAIN")
        cl=[x for x in res["trades"] if x["status"]=="CLOSED"]
        rows[d0]=dict(net=sum(net(x) for x in cl)/1e4, r2=sum(net(x) for x in cl if x["rule"]=="R2")/1e4, n=len(cl))
    out[name]=rows
    xs=[rows[d]["net"] for d in DAYS]; v3=[rows[d]["net"] for d in DAYS if d>="2026-10-21"]; v13=[rows[d]["net"] for d in DAYS if "2026-09-30"<=d<="2026-10-20"]
    print("%-28s 21일 %+7.1f 최악 %+6.1f m/sd %.2f | v2창13일 %+7.1f | v3 3일 %+6.1f | 10-23 %+6.1f | 10-21 %+6.1f"%(name,sum(xs),min(xs),st.mean(xs)/st.stdev(xs),sum(v13),sum(v3),rows["2026-10-23"]["net"],rows["2026-10-21"]["net"]))
json.dump(out,open(sys.argv[1],"w",encoding="utf-8"),ensure_ascii=False,indent=1)
