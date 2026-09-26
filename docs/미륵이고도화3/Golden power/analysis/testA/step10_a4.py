# -*- coding: utf-8 -*-
"""A-4 판정표 — ER z 명시 + 일봉 국면 기반 하락구간 부분표본."""
import sys, os, warnings
warnings.filterwarnings('ignore')
sys.path.insert(0,'C:/Users/82108/PycharmProjects/futures')
from utils.dll_bootstrap import ensure_conda_dll_path
ensure_conda_dll_path()
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try: sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception: pass
import numpy as np, pandas as pd
import core, testa, finals
finals.TS=(5,10,15,20,30,60,90,180)
H=os.path.dirname(os.path.abspath(__file__))
D=pd.read_pickle(os.path.join(H,'D.pkl')); FWD=np.load(os.path.join(H,'FWD.npy'))
ctx=testa.Ctx(D,FWD)
BASE=np.isfinite(D['atr'])&~D['synth']
def cu(col,lvl):
    o=np.zeros(len(D),bool)
    for s,g in D.groupby('s'): o[g.index.values]=core.cross_up(g[col].values,lvl)
    return o
GB05,GB08=cu('gb',0.5),cu('gb',0.8); GS05=cu('gs',0.5)
# ── 일봉 국면 (전일까지만 사용 — 미래참조 없음) ──
dayc=pd.Series({s:g['close'].values[-1] for s,g in D.groupby('s')}).sort_index()
d5=dayc.rolling(5).mean().shift(1); d20=dayc.rolling(20).mean().shift(1)
reg=pd.Series(np.where(d5<d20,'down',np.where(d5>d20,'up','na')),index=dayc.index)
reg[d5.isna()|d20.isna()]='na'
rmap=D['s'].map(reg).values
print('일봉국면 분포: %s'%pd.Series(rmap).value_counts().to_dict())

CAND={
 'L 원문서 GB0.5 09:20-14:50 (h90)':(+1,BASE&GB05&(D['hhmm']>='09:20')&(D['hhmm']<='14:50'),90,False),
 'L 최적 GB0.8 09:20-10:00':       (+1,BASE&GB08&(D['hhmm']>='09:20')&(D['hhmm']<'10:00'),90,False),
 'L 최적 GB0.8 09:20-09:40':       (+1,BASE&GB08&(D['hhmm']>='09:20')&(D['hhmm']<'09:40'),90,False),
 'L      GB0.5 09:20-10:00':       (+1,BASE&GB05&(D['hhmm']>='09:20')&(D['hhmm']<'10:00'),90,False),
 'S 원문서 규칙':                   (-1,BASE&GS05&(D['gb']<=0.10)&D['sq10']&(D['ma20']<D['ma60'])&(D['hhmm']>='09:20')&(D['hhmm']<='14:50'),60,True),
 'S 순수 GS0.5 돌파':               (-1,BASE&GS05&(D['hhmm']>='09:20')&(D['hhmm']<='14:50'),60,False),
}
print('\n=== A-4 판정표 (사전등록 문턱: ER≥1.15 且 ERz≥2.0 / Δ zmax≥2.0) ===')
print('%-34s %5s %4s | %-22s | %-22s | %s'%('후보','N','일','최적지평(ER최대)','ER@90(원문서지평)','zmaxΔ'))
res={}
for k,(side,m,hb,oc) in CAND.items():
    r=core.select(D,m,hold_block=hb,once_per_day=oc)
    o=finals.deep(ctx,r,side,n_rep=2000,seed=131); res[k]=o
    best=max((t for t in finals.TS if t<=90), key=lambda t:(o['er%d'%t] if o['er%d'%t]==o['er%d'%t] else -9))
    print('%-34s %5d %4d | t=%3d ER %.3f z%+.2f%s | ER %.3f z%+.2f%s | %.2f@%3d p=%.4f%s'%(
        k,o['N'],o['days'],best,o['er%d'%best],o['erz%d'%best],
        '✅' if (o['er%d'%best]>=1.15 and o['erz%d'%best]>=2.0) else '❌',
        o['er90'],o['erz90'],'✅' if (o['er90']>=1.15 and o['erz90']>=2.0) else '❌',
        o['zmax'],o['zmax_t'],o['p_zmax'],'✅' if o['zmax']>=2.0 else '❌'))

print('\n=== A-4 ③ 하락구간 부분표본 — 일봉 국면(전일까지 정보만) ===')
for k in ('L 원문서 GB0.5 09:20-14:50 (h90)','L 최적 GB0.8 09:20-10:00'):
    side,m,hb,oc=CAND[k]
    for rg in ('down','up'):
        r=core.select(D,m&(rmap==rg),hold_block=hb,once_per_day=oc)
        if len(r)<30: print('%-34s %-5s n=%d 표본부족'%(k,rg,len(r))); continue
        o=finals.deep(ctx,r,side,n_rep=1500,seed=137)
        print('%-34s %-5s N=%3d | Δ10 %+.3f(z%+.2f) Δ15 %+.3f(z%+.2f) | ER15 %.3f 대조 %.3f p=%.4f  → Δ>0 %s'%(
            k,rg,o['N'],o['d10'],o['z10'],o['d15'],o['z15'],o['er15'],o['erc15'],o['erp15'],
            '✅' if o['d15']>0 else '❌'))
