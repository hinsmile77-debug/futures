import r3lab as R, random
from strategy.shindong import engine as E

T=lambda v: v is True
def near_struct(f):
    P=R.load_day(f['date']); L=P['L']; _,lv=E.levels_at(L,f['ent'])
    c=[x for x in lv if f['side']*(x-f['e'])>=2.0]
    return (min(c) if f['side']>0 else max(c)) if c else None
def cap(k1,k2=None):
    def fn(f):
        s,e,r=f['side'],f['e'],f['risk']
        t1,t2=f['t1'],f['t2']
        c1=e+s*k1*r
        t1=c1 if (t1 is None or s*(t1-c1)>0) else t1
        if k2:
            c2=e+s*k2*r
            t2=c2 if (t2 is None or s*(t2-c2)>0) else t2
        if t2 is not None and s*(t2-t1)<0: t2=t1
        return t1,t2,f['stop']
    return fn
def struct1(f):
    s,e=f['side'],f['e']; n=near_struct(f)
    t1=f['t1']
    if n is not None:
        n=n-s*0.5
        if t1 is None or s*(t1-n)>0: t1=n
    t2=f['t2'] if f['t2'] is not None else t1
    if t1 is not None and s*(t2-t1)<0: t2=t1
    return t1,t2,f['stop']
