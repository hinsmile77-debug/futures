# -*- coding: utf-8 -*-
"""MAIN 리모델 후보의 6일 손익 — 같은 하네스·같은 비용. R2 와 겹치는 후보는 R2 청산 뒤부터 진입(포지션 배타)."""
import os, sys, json
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from load import load
from sim import simulate, total
from grid import r1_bias
from strategy.shindong import engine as E
FD=["2026-09-21","2026-09-22","2026-09-23","2026-09-28","2026-09-29","2026-09-30"]
M=1e4
FLOWC=dict(K=300,mt=3,stop=None,trail=(6,4),tp=12)
BRK=dict(b=2,mt=5,trail=(6,3),tp=8)         # 둥근 값(9/30 최적 4/3 → 6/3)
def flowc_sig(d):
    k0=d.last_at_or_before("09:00"); base=d.sp.get(k0)
    def sig(k,st):
        v=d.sp.get(k)
        if v is None or base is None: return 0
        dv=v-base
        return -1 if dv>=FLOWC["K"] else (1 if dv<=-FLOWC["K"] else 0)
    return sig
def brk_sig(d,L,bias):
    def sig(k,st):
        _,lv=E.levels_at(L,k); prev=st.get("prev"); c=d.c[k]; st["prev"]=c
        if prev is None or not bias: return 0
        for x in lv:
            sd=-1 if (prev>=x>c) else (1 if (prev<=x<c) else 0)
            if sd and sd==bias: st["lvl"]=x; return sd
        return 0
    st={}
    return (lambda k,_s: sig(k,st)), (lambda k,side,e: st["lvl"]+BRK["b"] if side<0 else st["lvl"]-BRK["b"])
rows=[]
for day in FD:
    d,L,_=load(day); bias=r1_bias(d)
    res=E.run_day(d,L,"MAIN"); r2=[t for t in res["trades"] if t["rule"]=="R2"]
    r2net=sum(E.trade_net(t) for t in r2); r2exit=r2[0]["exit_ts"] if r2 else None
    r3main=sum(E.trade_net(t) for t in res["trades"] if t["rule"]=="R3")
    r3x4=sum(E.trade_net(t) for t in E.run_day(d,L,"SHADOW_X4NF")["trades"] if t["rule"]=="R3")
    r3x4a=sum(E.trade_net(t) for t in E.run_day(d,L,"SHADOW_X4NFA")["trades"] if t["rule"]=="R3")
    fc=total(simulate(d,flowc_sig(d),stop=None,trail=FLOWC["trail"],tp=FLOWC["tp"],max_trades=FLOWC["mt"]))
    fc_after=total(simulate(d,flowc_sig(d),stop=None,trail=FLOWC["trail"],tp=FLOWC["tp"],max_trades=FLOWC["mt"],start=E._plus_min(r2exit,1) if r2exit else "09:00"))
    if bias:
        s,sf=brk_sig(d,L,bias); bk=total(simulate(d,s,stop_fn=sf,trail=BRK["trail"],tp=BRK["tp"],max_trades=BRK["mt"]))
        s,sf=brk_sig(d,L,bias); bk_after=total(simulate(d,s,stop_fn=sf,trail=BRK["trail"],tp=BRK["tp"],max_trades=BRK["mt"],start=E._plus_min(r2exit,1) if r2exit else "09:00"))
    else: bk=bk_after=0.0
    rows.append(dict(day=day,bias=bias,R2=r2net,R3=r3main,X4=r3x4,X4A=r3x4a,FC=fc,FCa=fc_after,BK=bk,BKa=bk_after))
C={
 "v1 현행 MAIN (R2+R3)":lambda r:r["R2"]+r["R3"],
 "R2 단독":lambda r:r["R2"],
 "R2 + X4NF":lambda r:r["R2"]+r["X4"],
 "R2 + X4NFA":lambda r:r["R2"]+r["X4A"],
 "R2 + FLOWC(R2 뒤)":lambda r:r["R2"]+r["FCa"],
 "FLOWC 단독":lambda r:r["FC"],
 "R2 + BRK(R2 뒤) · 보류일 FLOWC":lambda r:(r["R2"]+r["BKa"]) if r["bias"] else r["FC"],
 "BRK(방향일) · FLOWC(보류일)":lambda r:r["BK"] if r["bias"] else r["FC"],
 "BRK + FLOWC(방향일 동시) · 보류일 FLOWC":lambda r:(r["BK"]+r["FC"]) if r["bias"] else r["FC"],
}
print("%-36s"%"후보"+"".join("%9s"%d[5:] for d in FD)+"%10s %8s %8s"%("합","최악일","흑자일"))
for name,f in C.items():
    v=[f(r)/M for r in rows]
    print("%-36s"%name+"".join("%+9.1f"%x for x in v)+"%+10.1f %+8.1f %5d/6"%(sum(v),min(v),sum(x>0 for x in v)))
print("\n구성요소(만원):")
for r in rows: print(r["day"],r["bias"],{k:round(v/M,1) for k,v in r.items() if k not in("day","bias")})
