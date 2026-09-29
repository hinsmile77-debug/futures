import sys
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")))
import r3lab as R, trail as T
from strategy.shindong import engine as E
ALL=[d for d in R.dates() if R.load_day(d) and d<="2026-09-28"]
def eng(D,side,ent,stop,t1,t2): return E.run_trade(D,side,ent,stop,t1,t2,trail=(4.0,4.0))
f601=T.make(4,4,"keep")
for name,fn in [("base",None),("trail.py 4/4",f601),("engine TR44",eng)]:
    n=0;tot=0;diffs=[]
    for d in ALL:
        tr=R.run_r3(d,signal="px",x=1.0,trade_fn=fn)
        n+=len(tr); tot+=sum(t["net"] for t in tr)
    print(name,len(ALL),n,round(tot/1e4))
# per-trade compare same entries
d="2026-09-29"
