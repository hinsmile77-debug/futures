# -*- coding: utf-8 -*-
import sys, os, warnings
warnings.filterwarnings('ignore')
sys.path.insert(0,'C:/Users/82108/PycharmProjects/futures')
from utils.dll_bootstrap import ensure_conda_dll_path
ensure_conda_dll_path()
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try: sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception: pass
import numpy as np, pandas as pd
import core
H=os.path.dirname(os.path.abspath(__file__))
D=pd.read_pickle(os.path.join(H,'D.pkl'))
BASE=np.isfinite(D['atr'])&~D['synth']
def cu(col,lvl):
    o=np.zeros(len(D),bool)
    for s,g in D.groupby('s'): o[g.index.values]=core.cross_up(g[col].values,lvl)
    return o
GB05,GS05,GB08=cu('gb',0.5),cu('gs',0.5),cu('gb',0.8)
days=np.array(sorted(D['s'].unique()))
start={s:int(g.index[0]) for s,g in D.groupby('s')}; nbar={s:len(g) for s,g in D.groupby('s')}
cl=D['close'].values; ses=D['s'].values; ii=D['i'].values; hhv=D['hhmm'].values
def bt(rows,side,hold,cost,gs_exit=None):
    rec={}; nt=0
    for ridx in rows:
        s=ses[ridx]; i=int(ii[ridx]); e=i+1; n=nbar[s]
        if e>=n-1: continue
        x=min(e+hold,n-1)
        hh=hhv[start[s]:start[s]+n]; f=np.flatnonzero(hh>='15:05')
        if len(f): x=min(x,int(f[0]))
        if gs_exit is not None:
            g=D['gs'].values[start[s]:start[s]+n]
            k=np.flatnonzero(g[e:x+1]>=gs_exit)
            if len(k): x=e+int(k[0])
        if x<=e: continue
        rec[s]=rec.get(s,0.0)+side*(cl[start[s]+x]-cl[start[s]+e])-cost; nt+=1
    d=pd.Series(rec).reindex(days).fillna(0.0)
    t=d.mean()/(d.std(ddof=1)/np.sqrt(len(d)))
    eq=d.cumsum(); mdd=float((np.maximum.accumulate(eq)-eq).max())
    return d.sum(),t,mdd,nt,int((d>0).sum())
print('=== 원문서 규칙 재현 (내 독립 구현, 252거래일 2025-08-19~2026-09-09) ===')
rowsL=core.select(D,BASE&GB05&(D['hhmm']>='09:20')&(D['hhmm']<='14:50'),hold_block=90)
for ctag,cst in (('원문서가정 0.15',0.15),('CYBOS 0.246018',0.246018),('CREON 0.0799',0.0799)):
    print('  롱 %-18s 총 %+8.1fpt t=%+5.2f MDD %6.1f n=%d 승일 %d'%((ctag,)+bt(rowsL,+1,90,cst)))
print('  원문서 주장: +432.5pt t=2.91 MDD 83.4 n=587 (211일)')
rowsS=core.select(D,BASE&GS05&(D['gb']<=0.10)&D['sq10']&(D['ma20']<D['ma60'])&(D['hhmm']>='09:20')&(D['hhmm']<='14:50'),hold_block=60,once_per_day=True)
for ctag,cst in (('원문서가정 0.15',0.15),('CYBOS 0.246018',0.246018),('CREON 0.0799',0.0799)):
    print('  숏 %-18s 총 %+8.1fpt t=%+5.2f MDD %6.1f n=%d 승일 %d'%((ctag,)+bt(rowsS,-1,60,cst,gs_exit=1.2)))
print('  원문서 주장: +75.1pt t=2.02 MDD 21.7 n=149 (211일)')
print()
print('=== 최적조건 (GB0.8 · 09:20-10:00 · 10분) 대비 ===')
r2=core.select(D,BASE&GB08&(D['hhmm']>='09:20')&(D['hhmm']<'10:00'),hold_block=10)
for ctag,cst in (('CYBOS',0.246018),('CREON',0.0799)):
    tot,t,mdd,nt,wd=bt(r2,+1,10,cst)
    print('  %-6s 총 %+8.1fpt t=%+5.2f MDD %5.1f n=%d | 원화(미니1계약) %+.0f원 | 칼마 %.2f'%(
        ctag,tot,t,mdd,nt,tot*50000,tot/max(mdd,1e-9)))
r3=core.select(D,BASE&GB08&(D['hhmm']>='09:20')&(D['hhmm']<'09:40'),hold_block=10)
for ctag,cst in (('CYBOS',0.246018),('CREON',0.0799)):
    tot,t,mdd,nt,wd=bt(r3,+1,10,cst)
    print('  09:40컷 %-6s 총 %+8.1fpt t=%+5.2f MDD %5.1f n=%d | 원화 %+.0f원 | 칼마 %.2f'%(
        ctag,tot,t,mdd,nt,tot*50000,tot/max(mdd,1e-9)))
