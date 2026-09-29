import sys, collections
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")))
import r3lab as R, trail as T
ALL=[d for d in R.dates() if R.load_day(d) and d<="2026-09-28"]
for x in (1.0,):
  for g in [(999,0),(4,1),(4,3),(4,4),(3,1)]:
    fn=None if g[0]==999 else T.make(g[0],g[1],"keep")
    m=collections.defaultdict(float); n=0; big=[]
    for d in ALL:
        v=R.run_r3(d,'px',start_busy='09:29',x=x,trade_fn=fn)
        s=sum(t['net'] for t in v); m[d[:7]]+=s; n+=len(v); big.append((s,d))
    big.sort()
    print(g,n,"합%+.0f"%(sum(m.values())/1e4),{k:round(v/1e4) for k,v in m.items()},"최악",[(d[5:],round(s/1e4)) for s,d in big[:3]])
