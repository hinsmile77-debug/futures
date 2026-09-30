# -*- coding: utf-8 -*-
"""개인 콜/풋 매수·매도 1분 증분 — 횡보 창 안/밖 비교(6일). 저장소 루트에서 실행."""
import sqlite3, collections, statistics as st
W={"2026-09-28":("10:28","15:05"),"2026-09-29":("11:54","14:16"),"2026-09-30":("11:43","15:05")}
PROD={"2026-09-28":"wk_mon","2026-09-29":"wk_thu","2026-09-30":"wk_thu","2026-09-21":"wk_mon","2026-09-22":"wk_thu","2026-09-23":"wk_thu"}
c=sqlite3.connect("data/db/option_flow.db"); r=sqlite3.connect("data/db/raw_data.db")
def series(d):
    out=collections.defaultdict(dict)
    for bt,prod,inv,sq,bq,nq,na in c.execute("select bar_time,product,investor,sell_qty,buy_qty,net_qty,net_amt from option_investor_flow where trade_date=? and product in (?,?) order by bar_time",(d,PROD[d]+"_call",PROD[d]+"_put")):
        out[bt][(inv,"call" if prod.endswith("call") else "put")]=(sq,bq,nq,na)
    return out
def closes(d): return {ts[11:16]:x for ts,x in r.execute("select ts,close from raw_candles where ts like ?",(d+"%",))}
def stats(v): return (st.mean(v), st.pstdev(v)) if len(v)>1 else (v[0] if v else 0,0)
ALL=collections.defaultdict(lambda: collections.defaultdict(list))
for d in sorted(PROD):
    S=series(d); C=closes(d); ks=sorted(k for k in S if "09:01"<=k<="15:05"); a,b=W.get(d,(None,None))
    def delta(k1,k2,key,i): return S[k2][key][i]-S[k1][key][i] if key in S[k1] and key in S[k2] else None
    feats=collections.defaultdict(lambda: collections.defaultdict(list))
    for k1,k2 in zip(ks,ks[1:]):
        lab="창안" if (a and a<=k2<=b) else "창밖"
        ic,ip=("individual","call"),("individual","put")
        cb,cs,pb,ps=delta(k1,k2,ic,1),delta(k1,k2,ic,0),delta(k1,k2,ip,1),delta(k1,k2,ip,0)
        cn,pn=delta(k1,k2,ic,3),delta(k1,k2,ip,3)
        if None in (cb,cs,pb,ps,cn,pn): continue
        F={"콜매수":cb,"콜매도":cs,"풋매수":pb,"풋매도":ps,"콜순액":cn,"풋순액":pn,"콜-풋":cn-pn,
           "총회전":cb+cs+pb+ps,"콜회전":cb+cs,"풋회전":pb+ps,"|콜순|+|풋순|":abs(cn)+abs(pn),
           "콜풋 동방향":1 if cn*pn>0 else 0,"콜매수-콜매도":cb-cs,"풋매수-풋매도":pb-ps,
           "콜순/콜회전":(cn/(cb+cs)) if cb+cs else 0}
        fc,fp=delta(k1,k2,("foreign","call"),3),delta(k1,k2,("foreign","put"),3)
        if fc is not None and fp is not None: F["외국인 콜-풋"]=fc-fp
        if k2 in C and k1 in C: F["|가격변화|"]=abs(C[k2]-C[k1])
        for f,v in F.items(): feats[lab][f].append(v); ALL[lab if a else "창밖(비대상일)"][f].append(v)
    if not a: continue
    print("== %s %s  창 %s~%s"%(d,PROD[d],a,b))
    for f in feats["창밖"]:
        mi,si=stats(feats["창안"][f]); mo,so=stats(feats["창밖"][f])
        print("   %-16s 창안 %+8.1f (sd %6.1f, n=%d) | 창밖 %+8.1f (sd %6.1f, n=%d)  비 %.2f"%(f,mi,si,len(feats["창안"][f]),mo,so,len(feats["창밖"][f]),(mi/mo) if mo else 0))
print("== 3일 합산 + 비대상 3일(9/21~23)")
for f in ALL["창밖"]:
    print("   %-16s 창안 %+8.1f | 창밖 %+8.1f | 비대상일 %+8.1f"%(f,st.mean(ALL["창안"][f]),st.mean(ALL["창밖"][f]),st.mean(ALL["창밖(비대상일)"][f]) if ALL["창밖(비대상일)"].get(f) else 0))
