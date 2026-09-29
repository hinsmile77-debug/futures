import sys, collections
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")))
import r3lab as R
ALL=[d for d in R.dates() if R.load_day(d)]
A=lambda f: f["side"]*(f["e"]-f["L0"])>0
LL=lambda f: f["lvl_losses"]==0                 # 손실 난 맥점 당일 재진입 금지
CD=lambda f: f["since_loss"] is None or f["since_loss"]>=20  # 손실 후 20분 쿨다운
P=[("X4NF",{}),("X4NF+A",dict(policy=A)),("X4NF+LL",dict(policy=LL)),("X4NF+CD20",dict(policy=CD)),("X4NF+A+LL",dict(policy=lambda f:A(f) and LL(f)))]
for x in (0.5,1.0,1.5):
  for name,kw in P:
    m=collections.defaultdict(float); n=w=0; wrong=0
    for d in ALL:
        v=R.run_r3(d,'px',x=x,x4nf=True,**kw)
        m[d[:7]]+=sum(t['net'] for t in v); n+=len(v); w+=sum(t['net']>0 for t in v)
    print("px%.1f %-10s n=%d 승률%.0f%% 합%+.0f"%(x,name,n,100*w/n,sum(m.values())/1e4),{k[5:]:round(v/1e4) for k,v in m.items()})
# 깨진맥점 진입의 성과(X4NF, 필터 없이 수집)
for x in (0.5,1.0,1.5):
    g=collections.defaultdict(list)
    for d in ALL:
        for t in R.run_r3(d,'px',x=x,x4nf=True):
            g[A(t)].append(t['net'])
    print("px%.1f 맥점 올바른편 n=%d 평균%+.1f만 승률%.0f%% | 깨진편 n=%d 평균%+.1f만 승률%.0f%%"%(x,len(g[True]),sum(g[True])/len(g[True])/1e4,100*sum(v>0 for v in g[True])/len(g[True]),len(g[False]),sum(g[False])/max(1,len(g[False]))/1e4,100*sum(v>0 for v in g[False])/max(1,len(g[False]))))
