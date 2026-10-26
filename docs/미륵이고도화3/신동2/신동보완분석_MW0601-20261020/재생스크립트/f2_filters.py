# -*- coding: utf-8 -*-
"""F2 대안 방향 필터 — 매분 방향 적중률(인과: t 시점까지의 데이터만). 0=중립(필터 미판정)."""
import sys, os, json, datetime as dt, statistics as st
sys.path.insert(0, os.environ["SCR"]); from causal_engine import *
def plus(t,m): return (dt.datetime.strptime(t,"%H:%M")+dt.timedelta(minutes=m)).strftime("%H:%M")
def ema(series, keys, n):
    a=2.0/(n+1); out={}; v=None
    for k in keys:
        if k in series:
            v=series[k] if v is None else v+a*(series[k]-v)
        if v is not None: out[k]=v
    return out
def sgn(x, band=0.0):
    return 0 if x is None or abs(x)<=band else (1 if x>0 else -1)
def build(d):
    keys=d.idx; sp=d.sp; c=d.c
    ems={n:ema(sp,keys,n) for n in (10,30)}; emc={n:ema(c,keys,n) for n in (20,60)}
    b=sp.get("09:00"); o=c.get("09:00")
    def at(series,k): 
        xs=[x for x in keys if x<=k and x in series]; return series[xs[-1]] if xs else None
    F={}
    def f(name,fn): F[name]=fn
    # 수급(콜−풋 역추종: 콜−풋 증가 → 하방 = -1)
    f("F2(현행: 09:00 대비 >0, 0→매수)", lambda t: -1 if (b is not None and sp.get(t) is not None and sp[t]-b>0) else 1)
    for band in (50,100,200):
        f("F2 중립±%d"%band, (lambda band: lambda t: -sgn(None if b is None or t not in sp else sp[t]-b, band))(band))
    for m in (30,60):
        f("수급 %d분 변화(중립±50)"%m, (lambda m: lambda t: -sgn(None if t not in sp or at(sp,plus(t,-m)) is None else sp[t]-at(sp,plus(t,-m)),50))(m))
    f("수급 EMA10−EMA30 기울기", lambda t: -sgn(None if t not in ems[10] or t not in ems[30] else ems[10][t]-ems[30][t], 20))
    f("수급 EMA30 10분 기울기", lambda t: -sgn(None if t not in ems[30] or at(ems[30],plus(t,-10)) is None else ems[30][t]-at(ems[30],plus(t,-10)), 10))
    # 가격 추세
    f("가격 09:00 대비(±1pt)", lambda t: sgn(None if o is None or t not in c else c[t]-o, 1.0))
    f("가격 EMA20 위/아래", lambda t: sgn(None if t not in emc[20] else c[t]-emc[20][t], 0.0))
    f("가격 EMA20−EMA60", lambda t: sgn(None if t not in emc[20] or t not in emc[60] else emc[20][t]-emc[60][t], 0.0))
    f("가격 30분 변화(±2pt)", lambda t: sgn(None if t not in c or at(c,plus(t,-30)) is None else c[t]-at(c,plus(t,-30)), 2.0))
    # 조합
    def agree(a,bf):
        return lambda t: (lambda x,y: x if x==y and x!=0 else 0)(F[a](t),F[bf](t))
    f("조합: F2±50 ∧ 가격 09:00 대비", agree("F2 중립±50","가격 09:00 대비(±1pt)"))
    f("조합: F2±50 ∧ 가격 EMA20−60", agree("F2 중립±50","가격 EMA20−EMA60"))
    f("조합: 수급60분 ∧ 가격 EMA20−60", agree("수급 60분 변화(중립±50)","가격 EMA20−EMA60"))
    # 지속성: F2±50 이 5분 연속 같은 부호
    def persist(t):
        ks=[k for k in keys if k<=t][-5:]
        v=[F["F2 중립±50"](k) for k in ks]
        return v[-1] if len(v)==5 and len(set(v))==1 else 0
    f("F2±50 5분 지속", persist)
    return F
if __name__=="__main__":
    D=json.load(open(os.environ["SCR"]+"/causal_full.json",encoding="utf-8"))["days"]
    agg={}
    for d0 in D:
        c,fl,l=inputs(d0); d=E.DayFrame(c,fl); F=build(d)
        mins=[k for k in d.idx if "09:30"<=k<="14:30" and k in d.c]
        c15=d.c.get(d.last_at_or_before("15:05") or "")
        for name,fn in F.items():
            a=agg.setdefault(name,dict(n=0,cov=0,h30=0,n30=0,heod=0,neod=0,days={}))
            dn=dc=0
            for k in mins:
                v=fn(k); a["n"]+=1
                if v==0: continue
                a["cov"]+=1
                p30=d.c.get(d.last_at_or_before(plus(k,30)) or "")
                if p30 is not None and p30!=d.c[k]: a["n30"]+=1; a["h30"]+=(v*(p30-d.c[k])>0)
                if c15 is not None and c15!=d.c[k]: a["neod"]+=1; a["heod"]+=(v*(c15-d.c[k])>0); dn+=1; dc+=(v*(c15-d.c[k])>0)
            a["days"][d0]=(dc/dn) if dn else None
    print("%-34s %6s %8s %8s %8s"%("필터","판정률","30분적중","마감적중","일별≥55%"))
    for name,a in agg.items():
        good=sum(1 for v in a["days"].values() if v is not None and v>=0.55); nd=sum(1 for v in a["days"].values() if v is not None)
        print("%-34s %5.0f%% %7.1f%% %7.1f%% %4d/%d"%(name,100*a["cov"]/a["n"],100*a["h30"]/max(1,a["n30"]),100*a["heod"]/max(1,a["neod"]),good,nd))
