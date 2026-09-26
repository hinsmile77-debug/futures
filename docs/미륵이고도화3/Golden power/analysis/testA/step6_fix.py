# -*- coding: utf-8 -*-
"""②재실행(MA-ready 통제) + 시간대 프로파일 + 경제성(비용 대비)."""
import sys, os
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
MAOK=np.isfinite(D['ma60'])&np.isfinite(D['ma20'])
def cu(col,lvl):
    o=np.zeros(len(D),bool)
    for s,g in D.groupby('s'): o[g.index.values]=core.cross_up(g[col].values,lvl)
    return o
print('MA60 가용 시각 최소: %s (WIN 내 %d/%d 봉)'%(D.loc[WIN&MAOK,'hhmm'].min(), (WIN&MAOK).sum(), WIN.sum()))
print('\n=== ②재실행 — 세 행 모두 MA-ready 봉으로 통제 ===')
for tag,lvl in (('레벨0.5',0.5),('레벨1.2',1.2)):
    for rg,mm in (('전체(MAready)',MAOK),('하락 MA20<MA60',MAOK&(D['ma20']<D['ma60'])),
                  ('상승 MA20>MA60',MAOK&(D['ma20']>D['ma60']))):
        r=core.select(D,WIN&cu('gb',lvl)&mm,hold_block=90)
        if len(r)<40: continue
        o=finals.deep(ctx,r,+1,n_rep=1000,seed=43)
        print('%-8s %-16s N=%4d | Δ15 %+.3f(z%+.2f) Δ30 %+.3f(z%+.2f) | ER15 %.3f p=%.4f | ER30 %.3f 대조 %.3f p=%.4f'%(
            tag,rg,o['N'],o['d15'],o['z15'],o['d30'],o['z30'],o['er15'],o['erp15'],o['er30'],o['erc30'],o['erp30']))

print('\n=== 시간대 프로파일 (LONG 레벨0.5, 1시간 구간) ===')
for lo,hi in (('09:20','10:00'),('10:00','11:00'),('11:00','12:00'),('12:00','13:00'),('13:00','14:00'),('14:00','14:50')):
    r=core.select(D,WIN&cu('gb',0.5)&(D['hhmm']>=lo)&(D['hhmm']<hi),hold_block=90)
    if len(r)<30: print('%s-%s n=%d 표본부족'%(lo,hi,len(r))); continue
    o=finals.deep(ctx,r,+1,n_rep=800,seed=47)
    print('%s-%s N=%3d | 실측15 %+.3f 대조 %+.3f Δ %+.3f z%+.2f | ER15 %.3f p=%.4f'%(
        lo,hi,o['N'],o['real'][14],o['ctrl'][14],o['d15'],o['z15'],o['er15'],o['erp15']))

print('\n=== 경제성 — 실측 평균 전방수익(pt) vs 왕복비용 ===')
COST={'CYBOS':0.246018,'CREON':0.079900,'원문서가정':0.15}
CAND={'L 레벨0.5':(+1,WIN&cu('gb',0.5),90,False),
      'L 레벨1.2':(+1,WIN&cu('gb',1.2),90,False),
      'S 원문서규칙':(-1,WIN&cu('gs',0.5)&(D['gb']<=0.10)&core.cross_up.__self__ if False else WIN&cu('gs',0.5)&(D['gb']<=0.10)&D['sq10']&(D['ma20']<D['ma60']),60,True)}
for k,(side,m,hb,oncep) in CAND.items():
    r=core.select(D,m,hold_block=hb,once_per_day=oncep)
    o=finals.deep(ctx,r,side,n_rep=1000,seed=53)
    print('\n%s  N=%d  ATR중앙 %.2f'%(k,o['N'],o['atr_med']))
    print('   t    실측평균   대조평균     Δ      z   | 순손익(CYBOS) (CREON)')
    for t in (5,10,15,20,30,45,60,90,180):
        rr=o['real'][t-1]; cc=o['ctrl'][t-1]
        print('%4d  %+8.3f %+9.3f %+7.3f %+6.2f | %+9.3f %+9.3f'%(
            t,rr,cc,rr-cc,(rr-cc)/max(1e-9,abs(rr-cc))*0 + o['z'][t-1],rr-COST['CYBOS'],rr-COST['CREON']))
    print('   t*분위(25/50/75/90) %s  반납중앙 30분 %.2f / 90분 %.2f'%(
        np.round(o['tstar_q'],0), o['giveback30'], o['giveback90']))
    print('   MFE30중앙 %+.2f MAE30중앙 %+.2f | MFE90중앙 %+.2f MAE90중앙 %+.2f'%(
        o['mfe_med30'],o['mae_med30'],o['mfe_med90'],o['mae_med90']))
