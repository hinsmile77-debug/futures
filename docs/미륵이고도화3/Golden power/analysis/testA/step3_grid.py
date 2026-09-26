# -*- coding: utf-8 -*-
"""검정 A 격자 — GP 진입조건 1축씩. 청산 무관 지표로만 순위."""
import sys, os, time, json
sys.path.insert(0,'C:/Users/82108/PycharmProjects/futures')
from utils.dll_bootstrap import ensure_conda_dll_path
ensure_conda_dll_path()
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try: sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception: pass
import numpy as np, pandas as pd
import core, testa
H=os.path.dirname(os.path.abspath(__file__))
D=pd.read_pickle(os.path.join(H,'D.pkl')); FWD=np.load(os.path.join(H,'FWD.npy'))
ctx=testa.Ctx(D,FWD)
WIN=(D['hhmm']>='09:20')&(D['hhmm']<='14:50')&np.isfinite(D['atr'])&~D['synth']
atr_med=D.loc[WIN,'atr'].median()
print('[grid] ATR 중앙 %.3f'%atr_med)

def build_cands(side):
    """side=+1 롱(GB 돌파) / -1 숏(GS 돌파)"""
    trig = 'gb' if side>0 else 'gs'
    opp  = 'gs' if side>0 else 'gb'
    C=[]
    def add(name, m, hold=90):
        C.append((name, m, hold))
    for lvl in (0.3,0.5,0.8,1.0,1.2,1.5,2.0):
        add('레벨 %.1f'%lvl, WIN & D['cu_%s_%.1f'%(trig,lvl)])
    base = WIN & D['cu_%s_0.5'%trig]
    for o in (0.5,0.2,0.1):
        add('레벨0.5 + 반대≤%.1f'%o, base & (D[opp]<=o))
    add('레벨0.5 + 압축10봉', base & D['sq10'])
    add('레벨0.5 + 하락국면(MA20<MA60)', base & (D['ma20']<D['ma60']))
    add('레벨0.5 + 상승국면(MA20>MA60)', base & (D['ma20']>D['ma60']))
    add('레벨0.5 + 오전 09:20-11:00', base & (D['hhmm']<='11:00'))
    add('레벨0.5 + 오후 11:00-14:50', base & (D['hhmm']>'11:00'))
    add('레벨0.5 + 고ATR(≥중앙)', base & (D['atr']>=atr_med))
    add('레벨0.5 + 저ATR(<중앙)', base & (D['atr']<atr_med))
    return C

rows_all={}
res=[]
t0=time.time()
for side,dtag in ((+1,'LONG'),(-1,'SHORT')):
    for name,m,hold in build_cands(side):
        r=core.select(D,m,hold_block=hold)
        if len(r)<40: 
            print('  skip %s %s n=%d'%(dtag,name,len(r))); continue
        mm=testa.measure(ctx,r,side,n_rep=300,seed=11)
        rows_all[(dtag,name)]=r
        res.append(dict(dir=dtag,cond=name,N=mm['N'],days=mm['days'],
                        er15=mm['er15'],erz15=mm['erz15'],er30=mm['er30'],erz30=mm['erz30'],
                        er60=mm['er60'],erz60=mm['erz60'],er90=mm['er90'],erz90=mm['erz90'],
                        d30=mm['d30'],z30=mm['z30'],zmax=mm['zmax'],zmax_t=mm['zmax_t'],
                        mfe90=mm['mfe90_med'],mae90=mm['mae90_med'],tstar=mm['tstar_med']))
R=pd.DataFrame(res)
R.to_pickle(os.path.join(H,'grid.pkl'))
pd.set_option('display.width',250)
for dtag in ('LONG','SHORT'):
    g=R[R['dir']==dtag].sort_values('er30',ascending=False)
    print('\n===== %s  (검정 A · 청산무관 · n_rep=300) ====='%dtag)
    print('%-32s %5s %4s %7s %6s %7s %6s %7s %6s %6s %5s'%(
        'condition','N','days','ER15','z','ER30','z','ER60','z','zmaxΔ','@t'))
    for _,x in g.iterrows():
        print('%-32s %5d %4d %7.3f %+6.2f %7.3f %+6.2f %7.3f %+6.2f %6.2f %5d'%(
            x['cond'],x['N'],x['days'],x['er15'],x['erz15'],x['er30'],x['erz30'],
            x['er60'],x['erz60'],x['zmax'],x['zmax_t']))
print('\n%.1fs  후보 %d개'%(time.time()-t0,len(R)))
