# -*- coding: utf-8 -*-
"""최종 확정 — 국소창 정밀 · 경로분포 · 경제성 백테스트 · 반기 구조."""
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
finals.TS=(5,10,15,20,30,45,60,90,180)
H=os.path.dirname(os.path.abspath(__file__))
D=pd.read_pickle(os.path.join(H,'D.pkl')); FWD=np.load(os.path.join(H,'FWD.npy'))
ctx=testa.Ctx(D,FWD)
BASE=np.isfinite(D['atr'])&~D['synth']
def cu(col,lvl):
    o=np.zeros(len(D),bool)
    for s,g in D.groupby('s'): o[g.index.values]=core.cross_up(g[col].values,lvl)
    return o
GB05,GB08,GB12=cu('gb',0.5),cu('gb',0.8),cu('gb',1.2)

print('=== ① 09:20-09:40 정밀 (종료경계 후보) ===')
for hi,tag in (('09:40','09:20-09:40'),('10:00','09:20-10:00')):
    for lv,lvn in ((GB05,'0.5'),(GB08,'0.8'),(GB12,'1.2')):
        r=core.select(D,BASE&lv&(D['hhmm']>='09:20')&(D['hhmm']<hi),hold_block=90)
        o=finals.deep(ctx,r,+1,n_rep=1500,seed=83)
        print('%s lvl%s N=%3d d=%3d | Δ10 %+.3f(z%+.2f) Δ15 %+.3f(z%+.2f) Δ30 %+.3f(z%+.2f) | ER15 %.3f p=%.4f | zmax %.2f@%d p=%.4f'%(
            tag,lvn,o['N'],o['days'],o['d10'],o['z10'],o['d15'],o['z15'],o['d30'],o['z30'],
            o['er15'],o['erp15'],o['zmax'],o['zmax_t'],o['p_zmax']))

print('\n=== ② 최종후보 경로분포 (09:20-10:00 · GB 0.8 상향돌파) ===')
r=core.select(D,BASE&GB08&(D['hhmm']>='09:20')&(D['hhmm']<'10:00'),hold_block=90)
o=finals.deep(ctx,r,+1,n_rep=2000,seed=89)
print('N=%d days=%d ATR중앙 %.2f'%(o['N'],o['days'],o['atr_med']))
print('   t   실측평균   대조     Δ      z    ER      ERp   | 순CYBOS  순CREON')
for t in finals.TS:
    print('%4d %+8.3f %+8.3f %+7.3f %+6.2f %6.3f %8.4f | %+8.3f %+8.3f'%(
        t,o['real'][t-1],o['ctrl'][t-1],o['d%d'%t],o['z%d'%t],o['er%d'%t],o['erp%d'%t],
        o['real'][t-1]-0.246018,o['real'][t-1]-0.079900))
print('t*분위 25/50/75/90 = %s | 반납중앙 30분 %.2f 90분 %.2f'%(np.round(o['tstar_q'],0),o['giveback30'],o['giveback90']))
print('MFE30중앙 %+.2f p75 %+.2f | MAE30중앙 %+.2f p20 %+.2f'%(o['mfe_med30'],o['mfe_p75_30'],o['mae_med30'],o['mae_p20_30']))

print('\n=== ③ 경제성 — 단순 시간청산 백테스트 (일자단위 t) ===')
days=np.array(sorted(D['s'].unique())); cut=days[int(len(days)*0.6)]
start={s:int(g.index[0]) for s,g in D.groupby('s')}
nbar={s:len(g) for s,g in D.groupby('s')}
cl=D['close'].values; ses=D['s'].values
def bt(rows,side,hold,cost):
    rec={}
    for ridx in rows:
        s=ses[ridx]; i=int(D['i'].values[ridx]); e=i+1; n=nbar[s]
        if e>=n-1: continue
        x=min(e+hold,n-1)
        hh=D['hhmm'].values[start[s]:start[s]+n]
        f=np.flatnonzero(hh>='15:05')
        if len(f): x=min(x,int(f[0]))
        if x<=e: continue
        p=side*(cl[start[s]+x]-cl[start[s]+e])-cost
        rec[s]=rec.get(s,0.0)+p
    d=pd.Series(rec).reindex(days).fillna(0.0)
    t=d.mean()/(d.std(ddof=1)/np.sqrt(len(d)))
    eq=d.cumsum(); mdd=float((np.maximum.accumulate(eq)-eq).max())
    return d.sum(), t, mdd, int(sum(1 for _ in rec))
CANDS={'09:20-10:00 GB0.5':(GB05,'09:20','10:00'),
       '09:20-10:00 GB0.8':(GB08,'09:20','10:00'),
       '09:20-09:40 GB0.8':(GB08,'09:20','09:40'),
       '09:20-14:50 GB0.5 (원문서)':(GB05,'09:20','14:50')}
for name,(lv,lo,hi) in CANDS.items():
    m=BASE&lv&(D['hhmm']>=lo)&(D['hhmm']<hi if hi!='14:50' else D['hhmm']<='14:50')
    for hold in (10,15,20,30,90):
        rr=core.select(D,m,hold_block=hold)
        line=[]
        for ctag,cst in (('CYBOS',0.246018),('CREON',0.0799)):
            tot,t,mdd,nd=bt(rr,+1,hold,cst)
            line.append('%s %+7.1fpt t=%+5.2f MDD %5.1f'%(ctag,tot,t,mdd))
        print('%-26s hold=%3d n=%4d | %s | %s'%(name,hold,len(rr),line[0],line[1]))
    print()

print('=== ④ 반기 구조 — 왜 후반에만 유의한가 ===')
for part,sel in (('전반',D['s']<cut),('후반',D['s']>=cut)):
    sub=D.loc[BASE&sel&(D['hhmm']>='09:20')&(D['hhmm']<='14:50')]
    print('%s: %s~%s 종가중앙 %.0f  ATR중앙 %.2f  ATR/종가(bp) %.1f  |일중변화|중앙 %.2f'%(
        part,sub['s'].min(),sub['s'].max(),sub['close'].median(),sub['atr'].median(),
        1e4*sub['atr'].median()/sub['close'].median(),
        np.median([abs(D.loc[D['s']==s,'close'].values[-1]-D.loc[D['s']==s,'close'].values[0]) for s in np.unique(sub['s'])])))
    rr=core.select(D,BASE&GB08&sel&(D['hhmm']>='09:20')&(D['hhmm']<'10:00'),hold_block=90)
    oo=finals.deep(ctx,rr,+1,n_rep=1500,seed=97)
    print('     GB0.8 오전 N=%3d 실측15 %+.3f 대조 %+.3f Δ %+.3f z%+.2f ER15 %.3f p=%.4f'%(
        oo['N'],oo['real'][14],oo['ctrl'][14],oo['d15'],oo['z15'],oo['er15'],oo['erp15']))
