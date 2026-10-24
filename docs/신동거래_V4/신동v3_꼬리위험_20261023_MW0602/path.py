import sys,json; sys.path.insert(0,sys.argv[2]); import sim
from strategy.shindong import spec as S
base=json.load(open(sys.argv[1],encoding='utf-8'))
rows=[]
for d,trs in base.items():
    D,L=sim.frame(d); atr=L['0850'].get('atr14')
    base900=D.c.get('09:00')
    for t in trs:
        e=t['px']; s=t['side']; t0=t['t']; m0=int(t0[:2])*60+int(t0[3:])
        mfe=mae=0; t6=None; mae6=None; t3=None
        for k in [k for k in D.idx if t0<k<=t['x']]:
            fav=(D.h[k]-e) if s>0 else (e-D.l[k]); adv=(e-D.l[k]) if s>0 else (D.h[k]-e)
            mae=max(mae,adv)  # 봉 내 순서 모름 — 보수적으로 역행 먼저
            mfe=max(mfe,fav)
            km=int(k[:2])*60+int(k[3:])
            if t3 is None and mfe>=3: t3=km-m0
            if t6 is None and mfe>=6: t6=km-m0; mae6=mae
        chase=None if base900 is None or t['rule']!='FLOW' else round((e-base900)*s,1)
        rows.append((d[5:],t['rule'],'B' if s>0 else 'S',t0,t['pt'],t3,t6,mae6 if t6 is not None else round(mae,1),round(atr,1),chase, round(abs(e-(e-s*0.6*atr)),1)))
print('날짜 규칙 방향 진입 pt | MFE3도달분 MFE6도달분 | 6도달전MAE(미도달=전체MAE) ATR14 FLOW추격(09:00대비 신호방향 기이동) 재난폭')
for r in sorted(rows,key=lambda r:r[4]): print(r)
W=[r for r in rows if r[4]>0]; Lz=[r for r in rows if r[4]<=0.2]
import statistics as st
t6=[r[6] for r in W if r[6] is not None]; m6=[r[7] for r in W if r[6] is not None]
print('승 n',len(W),'MFE6 도달분 max',max(t6),'p90',sorted(t6)[int(.9*len(t6))],'중앙',st.median(t6))
print('승 6도달 전 MAE max',max(m6),'p90',sorted(m6)[int(.9*len(m6))],'중앙',st.median(m6))
print('승 MFE3 도달분 max',max(r[5] for r in W),'중앙',st.median(r[5] for r in W))
print('패/본전 MFE3도달분',[r[5] for r in Lz])
