# -*- coding: utf-8 -*-
import json, sqlite3, datetime as dt, collections, sys
S=sys.argv[1]
A=json.load(open(S+"/dir_0601.json",encoding="utf-8")); B=json.load(open(S+"/dir_0602.json",encoding="utf-8"))
con=sqlite3.connect("file:C:/Users/82108/PycharmProjects/futures/data/db/raw_data.db?mode=ro",uri=True)
def bars(d):
    n=(dt.date.fromisoformat(d)+dt.timedelta(days=1)).isoformat()
    return {str(r[0])[11:16]:r[1] for r in con.execute("select ts,close from raw_candles where ts>=? and ts<? order by ts",(d,n))}
def at(c,t):
    ks=[k for k in c if k<=t]; return c[max(ks)] if ks else None
def plus(t,m): return (dt.datetime.strptime(t,"%H:%M")+dt.timedelta(minutes=m)).strftime("%H:%M")
rows=[]
for d in sorted(A):
    c=bars(d); o9=at(c,"09:00"); c15=at(c,"15:05"); day=(1 if c15>o9 else -1) if o9 and c15 and c15!=o9 else 0
    for src,obj,vs in (("0601",A,("MAIN","SHADOW_V2")),("0602",B,("MAIN","SHADOW_FLOWR60"))):
        bias=obj[d]["bias"]
        for v in vs:
            for i,t in enumerate(obj[d][v]):
                e=t["e"]; px=t["px"]
                h={}
                for m in (10,30):
                    p=at(c,min(plus(e,m),"15:05")); h[m]=None if p is None or p==px else t["side"]*(p-px)>0
                h["eod"]=None if c15 is None or c15==px else t["side"]*(c15-px)>0
                rows.append(dict(src=src,v=v,d=d,i=i,rule=t["rule"],side=t["side"],e=e,day=day,bias=bias,
                                 trend=(t["side"]==day) if day else None,r1=(t["side"]==bias) if bias else None,
                                 h10=h[10],h30=h[30],heod=h["eod"],win=t["net"]>0,net=t["net"]))
    rows.append(dict(src="day",d=d,day=day,bias=A[d]["bias"],b2=B[d]["bias"]))
json.dump(rows,open(S+"/dir_rows.json","w",encoding="utf-8"),ensure_ascii=False)
def rate(xs,k):
    m=[x[k] for x in xs if x.get(k) is not None]; return ("%3.0f%% (%d/%d)"%(100*sum(m)/len(m),sum(m),len(m))) if m else "-"
def show(lab,xs):
    print("%-34s n=%3d | 10분 %s | 30분 %s | 15:05 %s | 일방향순응 %s | R1일치 %s | 손익승 %s | 합 %+.0f"%(lab,len(xs),rate(xs,"h10"),rate(xs,"h30"),rate(xs,"heod"),rate(xs,"trend"),rate(xs,"r1"),rate(xs,"win"),sum(x["net"] for x in xs)))
T=[r for r in rows if r["src"]!="day"]
for win,f in (("18일",lambda r:True),("13일 09-30~",lambda r:r["d"]>="2026-09-30")):
    print("=====",win)
    for src,v,nm in (("0601","MAIN","신동2 MAIN(v3=TR44)"),("0601","SHADOW_V2","신동2 V2(구MAIN)"),("0602","MAIN","신동 MAIN(HYBR60)"),("0602","SHADOW_FLOWR60","신동 FLOWR60")):
        xs=[r for r in T if r["src"]==src and r["v"]==v and f(r)]; show(nm,xs)
        for rule in sorted({r["rule"] for r in xs}):
            show("   └ %s"%rule,[r for r in xs if r["rule"]==rule])
        show("   └ 첫 거래",[r for r in xs if r["i"]==0]); show("   └ 2번째 이후",[r for r in xs if r["i"]>0])
D=[r for r in rows if r["src"]=="day"]
for win,f in (("18일",lambda r:True),("13일",lambda r:r["d"]>="2026-09-30")):
    ds=[r for r in D if f(r)]; m=[r for r in ds if r["bias"] and r["day"]]
    print(win,"R1 장전방향 적중(09:00→15:05) %d/%d · 하락일 %d 상승일 %d"%(sum(1 for r in m if r["bias"]==r["day"]),len(m),sum(1 for r in ds if r["day"]<0),sum(1 for r in ds if r["day"]>0)))
