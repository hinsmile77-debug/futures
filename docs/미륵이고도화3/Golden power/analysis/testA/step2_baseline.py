# -*- coding: utf-8 -*-
import sys, os, time
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
win=(D['hhmm']>='09:20')&(D['hhmm']<='14:50')&np.isfinite(D['atr'])&~D['synth']
t0=time.time()
rowsL=core.select(D, win & D['cu_gb'], hold_block=90)
rowsS=core.select(D, win & D['cu_gs'] & (D['gb']<=0.10) & D['sq10'] & (D['ma20']<D['ma60']),
                  hold_block=60, once_per_day=True)
print('LONG n=%d days=%d | SHORT n=%d days=%d'%(len(rowsL),D.loc[rowsL,'s'].nunique(),
                                                len(rowsS),D.loc[rowsS,'s'].nunique()))
for tag,rows,side in (('LONG(GB0.5돌파)',rowsL,+1),('SHORT(원문서 규칙)',rowsS,-1)):
    m=testa.measure(ctx,rows,side,n_rep=1000)
    print('\n=== %s  N=%d days=%d  ATR중앙 %.2f'%(tag,m['N'],m['days'],m['atr_med']))
    print('  t   Δ(pt)   대조(pt)   z     ER    대조ER   ER_z')
    for t in testa.TS:
        print('%4d %+7.3f %+8.3f %+6.2f %6.3f %7.3f %+6.2f'%(
            t,m['d%d'%t],m['ctrl'][t-1],m['z%d'%t],m['er%d'%t],m['erc%d'%t],m['erz%d'%t]))
    print('  zmax=%.2f @ t=%d | MFE90중앙 %+.2f MAE90중앙 %+.2f t*중앙 %.0f 반납중앙 %.2f'%(
        m['zmax'],m['zmax_t'],m['mfe90_med'],m['mae90_med'],m['tstar_med'],m['giveback_med']))
print('\n%.1fs'%(time.time()-t0))
