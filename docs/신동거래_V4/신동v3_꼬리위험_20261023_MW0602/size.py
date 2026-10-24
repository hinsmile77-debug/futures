import sys,sqlite3,statistics as st; sys.path.insert(0,sys.argv[1]); import sim3, sim
from strategy.shindong import engine as E, spec as S
PTV=50000; CAP=15_000_000
o=sim3.run({})
c=sqlite3.connect('data/db/premarket_levels.db')
atr_hist=dict(c.execute("select date,atr14 from premarket_levels where stage='0850' and atr14 is not null order by date").fetchall())
def atr_ref(d):
    prev=[v for k,v in atr_hist.items() if k<d][-20:]
    return st.median(prev) if len(prev)>=5 else None
def leg2_scalein(d,t):
    """1계약은 기존 그대로. 2번째 계약은 MFE≥3 이 된 봉에 e+3 지정가로 추가, 손절 = 추가가(본전), 트레일·익절·시간은 1계약과 같은 가격."""
    D,L=sim.frame(d); e=t['px']; s=t['side']; e2=e+s*3.0; tp=e+s*S.FLOW_TP
    bars=[k for k in D.idx if t['t']<k<=t['x'] and k in D.h]
    mfe=0; added=None; st2=None
    for k in bars:
        h,l=D.h[k],D.l[k]
        if added is not None and k>added:
            if (l<=st2) if s>0 else (h>=st2): return E.leg_net(s,e2,st2,True)[0]
            if (h>=tp) if s>0 else (l<=tp): return E.leg_net(s,e2,tp,False)[0]
        fav=(h-e) if s>0 else (e-l); mfe=max(mfe,fav)
        if added is None and mfe>=3.0: added=k; st2=e2
        if added is not None and mfe>=S.FLOW_TRAIL[0]:
            ns=(e+s*mfe)-s*S.FLOW_TRAIL[1]
            if s*(ns-st2)>0: st2=ns
    if added is None: return None
    # 1계약과 같은 시점에 닫힌다(시간청산·TP 등) — 그 가격
    x=D.c[t['x']] if t['why'] in ('TIME',) else None
    if x is None:
        # 1계약 청산가 역산: pt(비용포함) 대신 가격 = 마지막 봉 처리 — 보수적으로 st2 사용
        x=st2
    return E.leg_net(s,e2,x,True)[0]
rows=[]
for d,v in o.items():
    ar=atr_ref(d)
    for t in v:
        q_atr=2 if (ar is None or t['atr']<=ar) else (1 if t['atr']>=1.5*ar else 1)
        q_atr=2 if ar is None else max(1,min(2,round(2*ar/t['atr'])))
        l2=leg2_scalein(d,t)
        pt1=t['pt']  # 계약당(비용포함)
        rows.append(dict(d=d,pt=pt1,l2=l2,qa=q_atr,mae=t['mae'],mfe=t['mfe'],atr=t['atr'],ar=ar))
def evals(lab,f):
    day={}; worst_tr=0; risk=0
    for r in rows:
        krw,open_risk=f(r)
        day[r['d']]=day.get(r['d'],0)+krw; worst_tr=min(worst_tr,krw); risk=max(risk,open_risk)
    cum=pk=mdd=0
    for d in sorted(day): cum+=day[d]; pk=max(pk,cum); mdd=max(mdd,pk-cum)
    oos=sum(v for d,v in day.items() if d>='2026-10-19')
    print(f"{lab} | {sum(day.values())/1e4:+,.0f}만 | {sum(day.values())/CAP*100:+.1f}% | {oos/1e4:+,.0f}만 | {min(day.values())/1e4:+,.0f}만 | {worst_tr/1e4:+,.0f}만 | {mdd/1e4:,.0f}만 | {risk/1e4:,.0f}만 ({risk/CAP*100:.1f}%)")
print('수량안 | 합계 | 수익률(1,500만) | 10/19~ | 최악일 | 최악거래 | MDD | 최대 보유역행 노출')
evals('고정 2계약',lambda r:(r['pt']*2*PTV, r['mae']*2*PTV))
evals('고정 1계약',lambda r:(r['pt']*1*PTV, r['mae']*1*PTV))
evals('[1] ATR 정규화 1~2 (2×직전20일 중앙ATR/ATR)',lambda r:(r['pt']*r['qa']*PTV, r['mae']*r['qa']*PTV))
def scale(r,base=1):
    k=r['pt']*base + (r['l2'] if r['l2'] is not None else 0)
    risk=r['mae']*base*PTV if r['mfe']<3 else max(r['mae']*base, 0)*PTV   # 추가 전 역행은 base 계약만
    return k*PTV, risk
evals('[4c] 분할 진입 1+1(유리 3pt에 추가)',scale)
evals('[4c] 분할 + ATR 고변동일 추가 생략',lambda r: scale(r) if r['qa']>=2 else (r['pt']*PTV, r['mae']*PTV))
n2=sum(1 for r in rows if r['l2'] is not None); print('2번째 계약 추가된 거래',n2,'/',len(rows),' 추가분 합(pt)',round(sum(r['l2'] for r in rows if r['l2'] is not None),1))
print('ATR 정규화로 1계약이 된 거래',sum(r['qa']==1 for r in rows),'— 날짜',sorted(set(r['d'][5:] for r in rows if r['qa']==1)))
