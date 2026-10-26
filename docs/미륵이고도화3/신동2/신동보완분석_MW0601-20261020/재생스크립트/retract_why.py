# -*- coding: utf-8 -*-
import sys, os, sqlite3, datetime as dt, statistics as st
ROOT=r"C:\Users\82108\PycharmProjects\futures"; sys.path.insert(0, ROOT)
from strategy.shindong import runner, engine as E, spec as S
from strategy.shindong.calendar import select_flow_product
DB=os.path.join(ROOT,"data","db"); P=[os.path.join(DB,x) for x in ("raw_data.db","option_flow.db","premarket_levels.db")]
s=sqlite3.connect("file:%s?mode=ro"%os.path.join(DB,"shindong.db").replace("\\","/"),uri=True); s.row_factory=sqlite3.Row
rows=[dict(r) for r in s.execute("select * from shindong_trades where variant='MAIN' and source='live' and rule='R3' and status in ('RETRACTED','CLOSED') order by trade_date,entry_ts")]
FR={}
def frame(d):
    if d not in FR:
        prod=select_flow_product(dt.date.fromisoformat(d))[0]; c,f,l=runner.load_inputs(d,prod,*P)
        FR[d]=(E.DayFrame(c,f),E.prepare_levels(l))
    return FR[d]
def hm(x): return str(x)[11:16] if len(str(x))>5 else str(x)
out=[]
for r in rows:
    d,L=frame(r["trade_date"]); t=hm(r["touch_ts"]); ent=hm(r["entry_ts"]); side=r["side"]; L0=r["touch_level"]
    seg=[d.sp[k] for k in d.between(t,ent) if k in d.sp]
    rev=None
    if seg and ent in d.sp:
        rev=(d.sp[ent]-min(seg)) if side<0 else (max(seg)-d.sp[ent])
    h,l,c=d.h.get(t),d.l.get(t),d.c.get(t)
    touch=None
    if h is not None:
        touch=(L0-S.TOUCH_NEAR<=h<=L0+S.TOUCH_FAR and c<L0) if side<0 else (L0-S.TOUCH_FAR<=l<=L0+S.TOUCH_NEAR and c>L0)
    # 다른 어느 분이든 창 안에서 문턱을 넘었는가(최종 데이터)
    endw=min(S.NEW_ENTRY_END,(dt.datetime.strptime(t,"%H:%M")+dt.timedelta(minutes=S.REV_WIN_MIN)).strftime("%H:%M"))
    first=None
    for u in d.between(t,endw):
        sg=[d.sp[k] for k in d.between(t,u) if k in d.sp]
        if not sg or u not in d.sp: continue
        v=(d.sp[u]-min(sg)) if side<0 else (max(sg)-d.sp[u])
        if v>=S.REV_MIN: first=(u,v); break
    det=str(r["detected_at"])[11:19]; upd=str(r["updated_at"])[11:19]
    out.append(dict(d=r["trade_date"],st=r["status"],side=side,touch=t,ent=ent,rev=rev,touch_ok=touch,first=first,det=det,upd=upd))
ret=[o for o in out if o["st"]=="RETRACTED"]; cl=[o for o in out if o["st"]=="CLOSED"]
print("== 철회 %d건 (최종 데이터로 재검사)"%len(ret))
for o in ret:
    print(" %s %s 터치 %s 진입 %s | 최종 반전 %s (문턱 50) | 터치 유효 %s | 창 안 첫 충족 %s | 탐지 %s → 철회 기록 %s"%(o["d"][5:],"매도" if o["side"]<0 else "매수",o["touch"],o["ent"],("%.0f"%o["rev"]) if o["rev"] is not None else "-",o["touch_ok"],o["first"],o["det"],o["upd"]))
m=[o["rev"] for o in cl if o["rev"] is not None]
print("== 유지된(CLOSED) R3 %d건의 최종 반전 여유: 중앙 %.0f · 50–59 %d건 · 60–79 %d건 · ≥80 %d건 · <50 %d건"%(len(m),st.median(m),sum(50<=x<60 for x in m),sum(60<=x<80 for x in m),sum(x>=80 for x in m),sum(x<50 for x in m)))

print("\n== 최종 재생에서 철회 신호를 덮은 것")
for o in ret:
    d0=o["d"]; r=runner.compute(d0,*P)
    tr=[x for x in r["results"]["MAIN"]["trades"]]
    cover=[x for x in tr if x["entry_ts"]<=o["touch"]<= (x["exit_ts"] or "99:99") or (x["entry_ts"]<o["ent"] and (x["exit_ts"] or "99:99")>=o["touch"])]
    prev=[x for x in tr if x["entry_ts"]<o["touch"]]
    pv=prev[-1] if prev else None
    print(" %s %s %s→%s | 직전 거래 %s | 덮은 거래 %s"%(d0[5:],"매도" if o["side"]<0 else "매수",o["touch"],o["ent"],
        ("%s %s 진입 %s 청산 %s(%s)"%(pv["rule"],"매수" if pv["side"]>0 else "매도",pv["entry_ts"],pv["exit_ts"],"/".join(g.get("reason") or "" for g in pv["legs"]))) if pv else "-",
        "; ".join("%s %s %s→%s"%(x["rule"],"매수" if x["side"]>0 else "매도",x["entry_ts"],x["exit_ts"]) for x in cover) or "없음"))

print("\n== 가설 검증: 「먼저 터치 · 나중 확인」 신호가 자리를 소급 점유했는가")
hit=0
for o in ret:
    r=runner.compute(o["d"],*P)
    pre=[x for x in r["results"]["MAIN"]["trades"] if x["rule"]=="R3" and x.get("touch_ts") and x["touch_ts"]<o["touch"] and x["entry_ts"]>o["ent"]]
    ok=bool(pre); hit+=ok
    x=pre[0] if pre else None
    print(" %s %s 터치 %s 확인·진입 %s ← %s"%(o["d"][5:],"매도" if o["side"]<0 else "매수",o["touch"],o["ent"],
        ("점유: %s 터치 %s → 확인·진입 %s(%d분 뒤) · 청산 %s"%("매수" if x["side"]>0 else "매도",x["touch_ts"],x["entry_ts"],
         (dt.datetime.strptime(x["entry_ts"],"%H:%M")-dt.datetime.strptime(x["touch_ts"],"%H:%M")).seconds//60,x["exit_ts"])) if x else "해당 없음"))
print("가설 일치 %d/%d"%(hit,len(ret)))
