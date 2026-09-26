# -*- coding: utf-8 -*-
"""개장구간 국소성 확정 — 경계 스윕 · 레벨 스윕 · 분할검증 · 숏 대칭확인."""
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
H=os.path.dirname(os.path.abspath(__file__))
D=pd.read_pickle(os.path.join(H,'D.pkl')); FWD=np.load(os.path.join(H,'FWD.npy'))
ctx=testa.Ctx(D,FWD)
BASE=np.isfinite(D['atr'])&~D['synth']
def cu(col,lvl):
    o=np.zeros(len(D),bool)
    for s,g in D.groupby('s'): o[g.index.values]=core.cross_up(g[col].values,lvl)
    return o
CU={}
for c_ in ('gb','gs'):
    for l_ in (0.3,0.5,0.8,1.0,1.2,1.5): CU[(c_,l_)]=cu(c_,l_)

def M(mask,side,hb=90,nrep=1000,seed=61,once=False):
    r=core.select(D,mask,hold_block=hb,once_per_day=once)
    if len(r)<25: return None,len(r)
    return finals.deep(ctx,r,side,n_rep=nrep,seed=seed),len(r)

print('=== ① 종료경계 스윕 (LONG GB0.5, 시작 09:20 고정) ===')
print('%-14s %5s %4s %9s %9s %8s %7s %8s %7s'%('창','N','days','실측15','대조15','Δ15','z','ER15','p'))
for hi in ('09:35','09:45','09:55','10:05','10:20','10:40','11:00','12:00','14:50'):
    o,n=M(BASE&CU[('gb',0.5)]&(D['hhmm']>='09:20')&(D['hhmm']<hi),+1)
    if o is None: print('%-14s n=%d 부족'%(hi,n)); continue
    print('09:20-%-8s %5d %4d %+9.3f %+9.3f %+8.3f %+7.2f %8.3f %7.4f'%(
        hi,o['N'],o['days'],o['real'][14],o['ctrl'][14],o['d15'],o['z15'],o['er15'],o['erp15']))

print('\n=== ② 시작경계 스윕 (종료 10:00 고정) ===')
for lo in ('09:00','09:10','09:20','09:30','09:40'):
    o,n=M(BASE&CU[('gb',0.5)]&(D['hhmm']>=lo)&(D['hhmm']<'10:00'),+1)
    if o is None: print('%s n=%d 부족'%(lo,n)); continue
    print('%s-10:00 N=%3d 실측15 %+.3f 대조 %+.3f Δ %+.3f z%+.2f ER15 %.3f p=%.4f'%(
        lo,o['N'],o['real'][14],o['ctrl'][14],o['d15'],o['z15'],o['er15'],o['erp15']))

print('\n=== ③ 09:20-10:00 안에서 레벨 스윕 ===')
for l_ in (0.3,0.5,0.8,1.0,1.2,1.5):
    o,n=M(BASE&CU[('gb',l_)]&(D['hhmm']>='09:20')&(D['hhmm']<'10:00'),+1)
    if o is None: print('lvl %.1f n=%d 부족'%(l_,n)); continue
    print('lvl %.1f N=%3d 실측15 %+.3f Δ %+.3f z%+.2f | ER15 %.3f p=%.4f ER30 %.3f p=%.4f'%(
        l_,o['N'],o['real'][14],o['d15'],o['z15'],o['er15'],o['erp15'],o['er30'],o['erp30']))

print('\n=== ④ 분할검증 — 09:20-10:00 GB0.5 ===')
days=np.array(sorted(D['s'].unique())); cut=days[int(len(days)*0.6)]
for part,sel in (('전반',D['s']<cut),('후반',D['s']>=cut)):
    o,n=M(BASE&CU[('gb',0.5)]&(D['hhmm']>='09:20')&(D['hhmm']<'10:00')&sel,+1,nrep=1000,seed=67)
    if o is None: print(part,'부족',n); continue
    print('%-3s N=%3d d=%3d 실측15 %+.3f Δ %+.3f z%+.2f | ER15 %.3f p=%.4f | zmaxΔ %.2f@%d p=%.4f'%(
        part,o['N'],o['days'],o['real'][14],o['d15'],o['z15'],o['er15'],o['erp15'],o['zmax'],o['zmax_t'],o['p_zmax']))

print('\n=== ⑤ 숏 대칭 — 09:20-10:00 GS 상향돌파 ===')
for l_ in (0.5,1.0,1.2):
    o,n=M(BASE&CU[('gs',l_)]&(D['hhmm']>='09:20')&(D['hhmm']<'10:00'),-1,hb=60)
    if o is None: print('lvl %.1f n=%d 부족'%(l_,n)); continue
    print('GS lvl %.1f N=%3d 실측15 %+.3f Δ %+.3f z%+.2f | ER15 %.3f p=%.4f ER30 %.3f p=%.4f'%(
        l_,o['N'],o['real'][14],o['d15'],o['z15'],o['er15'],o['erp15'],o['er30'],o['erp30']))

print('\n=== ⑥ 09:20-10:00 GB0.5 경로분포 (검정 B 입력) ===')
o,n=M(BASE&CU[('gb',0.5)]&(D['hhmm']>='09:20')&(D['hhmm']<'10:00'),+1,nrep=1500,seed=71)
print('N=%d ATR중앙 %.2f'%(o['N'],o['atr_med']))
print('   t   실측평균   Δ      z     ER      p   | 순(CYBOS) 순(CREON)')
for t in (5,10,15,20,30,45,60,90):
    ers=o.get('er%d'%t); erp=o.get('erp%d'%t)
    print('%4d %+8.3f %+7.3f %+6.2f %s %s | %+8.3f %+8.3f'%(
        t,o['real'][t-1],o['d%d'%t],o['z'][t-1],
        ('%6.3f'%ers) if ers==ers else '   —  ', ('%7.4f'%erp) if erp==erp else '   —   ',
        o['real'][t-1]-0.246018, o['real'][t-1]-0.079900))
print('t*분위 25/50/75/90 = %s | 반납중앙 30분 %.2f 90분 %.2f'%(np.round(o['tstar_q'],0),o['giveback30'],o['giveback90']))
print('MFE30중앙 %+.2f (p75 %+.2f) MAE30중앙 %+.2f (p20 %+.2f)'%(o['mfe_med30'],o['mfe_p75_30'],o['mae_med30'],o['mae_p20_30']))
