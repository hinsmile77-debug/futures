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
from scipy import stats
import core, testa, finals
H=os.path.dirname(os.path.abspath(__file__))
D=pd.read_pickle(os.path.join(H,'D.pkl')); FWD=np.load(os.path.join(H,'FWD.npy'))
BASE=np.isfinite(D['atr'])&~D['synth']
def cu(col,lvl):
    o=np.zeros(len(D),bool)
    for s,g in D.groupby('s'): o[g.index.values]=core.cross_up(g[col].values,lvl)
    return o
GB08=cu('gb',0.8); GB05=cu('gb',0.5)
days=np.array(sorted(D['s'].unique()))
start={s:int(g.index[0]) for s,g in D.groupby('s')}; nbar={s:len(g) for s,g in D.groupby('s')}
cl=D['close'].values; ses=D['s'].values; ii=D['i'].values; hhv=D['hhmm'].values
def bt(rows,hold,cost):
    rec={}
    for ridx in rows:
        s=ses[ridx]; i=int(ii[ridx]); e=i+1; n=nbar[s]
        if e>=n-1: continue
        x=min(e+hold,n-1)
        hh=hhv[start[s]:start[s]+n]; f=np.flatnonzero(hh>='15:05')
        if len(f): x=min(x,int(f[0]))
        if x<=e: continue
        rec[s]=rec.get(s,0.0)+(cl[start[s]+x]-cl[start[s]+e])-cost
    return pd.Series(rec).reindex(days).fillna(0.0), pd.Series(rec)
for tag,lv,hi,hold in (('09:20-09:40 GB0.8 h10',GB08,'09:40',10),
                       ('09:20-10:00 GB0.8 h10',GB08,'10:00',10),
                       ('09:20-10:00 GB0.5 h15',GB05,'10:00',15)):
    m=BASE&lv&(D['hhmm']>='09:20')&(D['hhmm']<hi)
    rows=core.select(D,m,hold_block=hold)
    for ctag,cst in (('CYBOS',0.246018),('CREON',0.0799)):
        d,dd=bt(rows,hold,cst)
        t=d.mean()/(d.std(ddof=1)/np.sqrt(len(d)))
        top3=dd.sort_values(ascending=False).head(3).sum()
        d2=d.copy(); d2[dd.sort_values(ascending=False).head(3).index]=0.0
        t2=d2.mean()/(d2.std(ddof=1)/np.sqrt(len(d2)))
        pos=(dd>0).sum(); tot_d=len(dd)
        sg=stats.binomtest(int(pos),int(tot_d),0.5).pvalue
        print('%-24s %-6s 총 %+7.1f t=%+5.2f | 최선3일 %+6.1f(%.0f%%) 제거후 %+7.1f t=%+5.2f | 승일 %d/%d p=%.3f'%(
            tag,ctag,d.sum(),t,top3,100*top3/max(d.sum(),1e-9),d2.sum(),t2,pos,tot_d,sg))
    m2=BASE&lv&(D['hhmm']>='09:20')&(D['hhmm']<hi)
    d,_=bt(core.select(D,m2,hold_block=hold),hold,0.246018)
    mo=d.groupby(pd.to_datetime(d.index).strftime('%Y-%m')).sum()
    print('   월별(CYBOS): %s'%(' '.join('%s:%+.0f'%(k[-2:],v) for k,v in mo.items())))
    print('   월 양수 %d/%d'%((mo>0).sum(),len(mo)))
    print()
