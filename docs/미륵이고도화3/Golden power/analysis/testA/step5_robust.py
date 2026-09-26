# -*- coding: utf-8 -*-
"""고원성(레벨 미세스윕) · 하락국면 부분표본(A-4 ③) · 분할검증."""
import sys, os, time
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
WIN=(D['hhmm']>='09:20')&(D['hhmm']<='14:50')&np.isfinite(D['atr'])&~D['synth']

def cu(col,lvl):
    o=np.zeros(len(D),bool)
    for s,g in D.groupby('s'):
        o[g.index.values]=core.cross_up(g[col].values,lvl)
    return o

print('=== ① 레벨 미세스윕 (고원인가 스파이크인가) — LONG, GB 상향돌파 ===')
print('%6s %5s %4s %7s %8s %7s %8s %7s'%('lvl','N','days','ER15','p','ER30','p','ER60'))
sweep={}
for lvl in (0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.6):
    m=WIN & cu('gb',lvl)
    r=core.select(D,m,hold_block=90)
    o=finals.deep(ctx,r,+1,n_rep=800,seed=23)
    sweep[lvl]=o
    print('%6.1f %5d %4d %7.3f %8.4f %7.3f %8.4f %7.3f'%(lvl,o['N'],o['days'],o['er15'],o['erp15'],o['er30'],o['erp30'],o['er60']))

print('\n=== ② A-4 ③ 하락국면 부분표본 (MA20<MA60) ===')
for tag,lvl in (('레벨0.5',0.5),('레벨1.2',1.2)):
    for rg,mm in (('전체',None),('하락 MA20<MA60',D['ma20']<D['ma60']),('상승 MA20>MA60',D['ma20']>D['ma60'])):
        m=WIN & cu('gb',lvl)
        if mm is not None: m=m&mm
        r=core.select(D,m,hold_block=90)
        if len(r)<40: continue
        o=finals.deep(ctx,r,+1,n_rep=800,seed=29)
        print('%-8s %-16s N=%4d | Δ15 %+.3f(z%+.2f) Δ30 %+.3f(z%+.2f) | ER30 %.3f 대조 %.3f p=%.4f'%(
            tag,rg,o['N'],o['d15'],o['z15'],o['d30'],o['z30'],o['er30'],o['erc30'],o['erp30']))

print('\n=== ③ 분할검증 (전반 60% 학습 / 후반 40% 검증) ===')
days=np.array(sorted(D['s'].unique())); cut=days[int(len(days)*0.6)]
print('   경계 %s  전반 %d일 / 후반 %d일'%(cut,(days<cut).sum(),(days>=cut).sum()))
CAND={'L 레벨0.5':(+1,WIN&cu('gb',0.5),90,False),
      'L 레벨1.2':(+1,WIN&cu('gb',1.2),90,False),
      'S 원문서규칙':(-1,WIN&cu('gs',0.5)&(D['gb']<=0.10)&D['sq10']&(D['ma20']<D['ma60']),60,True)}
for k,(side,m,hb,oncep) in CAND.items():
    for part,sel in (('전반',D['s']<cut),('후반',D['s']>=cut)):
        r=core.select(D,m&sel,hold_block=hb,once_per_day=oncep)
        if len(r)<30: print('%-12s %s n=%d 표본부족'%(k,part,len(r))); continue
        o=finals.deep(ctx,r,side,n_rep=800,seed=37)
        print('%-12s %-3s N=%4d d=%3d | ER15 %.3f(p%.3f) ER30 %.3f(p%.3f) ER60 %.3f(p%.3f) zmax %.2f p%.3f'%(
            k,part,o['N'],o['days'],o['er15'],o['erp15'],o['er30'],o['erp30'],o['er60'],o['erp60'],o['zmax'],o['p_zmax']))
