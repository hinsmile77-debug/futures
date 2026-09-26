# -*- coding: utf-8 -*-
import sys, os, pickle, time
sys.path.insert(0,'C:/Users/82108/PycharmProjects/futures')
from utils.dll_bootstrap import ensure_conda_dll_path
ensure_conda_dll_path()
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try: sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception: pass
import numpy as np, pandas as pd
import core
t0=time.time()
D, FWD = core.build()
D = core.add_signals(D)
H=os.path.dirname(os.path.abspath(__file__))
D.to_pickle(os.path.join(H,'D.pkl'))
np.save(os.path.join(H,'FWD.npy'), FWD)
print('FWD', FWD.shape, FWD.dtype, '%.1fMB'%(FWD.nbytes/1e6), '%.1fs'%(time.time()-t0))
print('교차수: GB0.5 %d  GS0.5 %d  압축10 %d'%(D['cu_gb'].sum(), D['cu_gs'].sum(), D['sq10'].sum()))
print('ATR 결측 %d / %d'%(D['atr'].isna().sum(), len(D)))
print('세션 %d  %s ~ %s'%(D['s'].nunique(), D['s'].min(), D['s'].max()))
