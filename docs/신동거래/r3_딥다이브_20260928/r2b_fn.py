import sys
sys.path.insert(0, r"C:\Users\82108\PycharmProjects\futures")
from strategy.shindong import engine as E
def pt(G):
    def fn(d, side, t0, stop, t1, t2, e2=False):
        e=d.c[t0]; c=e+side*G
        n=lambda t: c if (t is None or side*(t-c)>0) else t
        return E.run_trade(d, side, t0, stop, n(t1), n(t2))
    return fn
