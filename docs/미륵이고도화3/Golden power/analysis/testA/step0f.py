# -*- coding: utf-8 -*-
"""원문서 +432.5pt / 587거래 / 211일 재현 시도 — 변형 스캔."""
import sys, os, itertools
sys.path.insert(0,'C:/Users/82108/PycharmProjects/futures')
from utils.dll_bootstrap import ensure_conda_dll_path
ensure_conda_dll_path()
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try: sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception: pass
import numpy as np, pandas as pd, pickle
from gpa_lib import *
from gpa_lib import _gp

c = pd.read_pickle(os.path.join(os.path.dirname(os.path.abspath(__file__)),'candles.pkl'))
c['dt']=pd.to_datetime(c['ts']); c['session']=c['dt'].dt.strftime('%Y-%m-%d')
c['hhmm']=c['dt'].dt.strftime('%H:%M')
c=c[(c['hhmm']>='09:00')&(c['hhmm']<='15:35')].sort_values('dt').drop_duplicates('dt')

def run(period, reset, side, lvl, hold, t_lo, t_hi, start, entry_px, cost=0.15):
    tot=0.0; n=0; days=set()
    if reset:
        groups = [(s,g) for s,g in c.groupby('session') if len(g)>=300 and s>=start]
    else:
        cc = c[c['session']>=start]
        gb_all, gs_all = _gp(cc['close'].astype(float).values, period)
        cc = cc.assign(gb=gb_all, gs=gs_all)
        groups = [(s,g) for s,g in cc.groupby('session') if len(g)>=300]
    for s,g in groups:
        cl=g['close'].astype(float).values; op=g['open'].astype(float).values
        hh=g['hhmm'].values
        if reset: gb,gs=_gp(cl,period)
        else: gb,gs=g['gb'].values,g['gs'].values
        line = gb if side>0 else gs
        sig = cross_up(line, lvl) & (hh>=t_lo) & (hh<=t_hi)
        force=np.flatnonzero(hh>='15:05'); fx=int(force[0]) if len(force) else len(cl)-1
        busy=-1
        for i in np.flatnonzero(sig):
            if i<=busy or i+1>=len(cl): continue
            e=i+1; x=min(e+hold, fx, len(cl)-1)
            if x<=e: continue
            pe = op[e] if entry_px=='open' else cl[e]
            tot += side*(cl[x]-pe)-cost; n+=1; busy=e+hold; days.add(s)
    return tot,n,len(days)

start_all='2025-08-19'
print('%-58s %9s %6s %5s'%('variant','tot','n','days'))
for period in (20,25):
  for reset in (True,False):
    for entry_px in ('close','open'):
      t,n,dd=run(period,reset,+1,0.5,90,'09:20','14:50',start_all,entry_px)
      print('%-58s %+9.1f %6d %5d'%('LONG p=%d reset=%s px=%s'%(period,reset,entry_px),t,n,dd))
print()
for lvl in (0.3,0.5,0.8,1.0,1.5):
    t,n,dd=run(20,True,+1,lvl,90,'09:20','14:50',start_all,'close')
    print('LONG lvl=%.1f  %+9.1f n=%d'%(lvl,t,n))
print()
for st in ('2025-08-19','2025-10-31','2026-01-02','2026-03-02','2026-05-15','2026-06-01'):
    t,n,dd=run(20,True,+1,0.5,90,'09:20','14:50',st,'close')
    print('LONG start=%s %+9.1f n=%d days=%d'%(st,t,n,dd))
print()
# 숏방향 GS돌파 (롱 라벨 오해 가능성) / GB돌파를 숏으로
for side,line_desc in ((-1,'GS cross-up -> SHORT'),):
    t,n,dd=run(20,True,side,0.5,90,'09:20','14:50',start_all,'close')
    print('%s 90분 %+9.1f n=%d'%(line_desc,t,n))
t,n,dd=run(20,True,+1,0.5,90,'09:20','14:50',start_all,'close',cost=0.0)
print('LONG 무비용 %+9.1f n=%d'%(t,n))
