import os, sys, datetime as dt
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")))
from config import settings as ST
from strategy.shindong import runner, engine as E, spec as S
DAYS=["2026-09-21","2026-09-22","2026-09-23","2026-09-28","2026-09-29"]
def load(day):
    from strategy.shindong.calendar import select_flow_product
    p,_,_=select_flow_product(dt.date.fromisoformat(day))
    c,f,lv=runner.load_inputs(day,p,ST.RAW_DATA_DB,ST.WEEKLY_OPTION_FLOW_DB,ST.PREMARKET_LEVELS_DB)
    return p,c,f,lv
for day in DAYS:
    p,c,f,lv=load(day)
    L=E.prepare_levels(lv); d=E.DayFrame(c,f)
    k0=max([k for k in d.c if k<="09:00"] or [min(d.c)]); kl=d.idx[-1]
    print("\n=====",day,p,"bars",len(c),"last",kl,"open09",d.c.get(k0),"last",d.c[kl],
          "hi",max(d.h.values()),"lo",min(d.l.values()))
    print(" 0850 S:",L["0850"]["S"], "dist",L["0850"].get("dist_low"),L["0850"].get("dist_high"),"80",L["0850"].get("low80_lo"),L["0850"].get("high80_hi"))
    if "0930" in L: print(" 0930 S:",L["0930"]["S"])
    sp=d.sp; 
    print(" sp 08:59",sp.get("08:59"),"09:00",sp.get("09:00"), " sp@10/11/12/13/14:", [round(sp.get(x,float('nan'))) for x in ["10:00","11:00","12:00","13:00","14:00","15:00"] if x in sp])
    for v in S.VARIANTS:
        r=E.run_day(d,L,v); dec=r["decision"]
        tot=sum(E.trade_net(t) for t in r["trades"])
        print(" [%s] bias=%s pm_sp=%s r2=%s %s | n=%d net=%+.0f"%(v,dec["bias"],dec["pm_sp"],dec["r2"],dec["r2_ts"],len(r["trades"]),tot/1e4))
        if v!="MAIN": continue
        for t in r["trades"]:
            e=t["entry_px"]; s=t["side"]; t0=t["entry_ts"]
            ex=t["exit_ts"] or kl
            seg=[k for k in d.idx if t0<k<=ex]
            mfe=max([s*((d.h[k] if s>0 else d.l[k])-e) for k in seg] or [0])
            mae=max([-s*((d.l[k] if s>0 else d.h[k])-e) for k in seg] or [0])
            # after exit 60m MFE
            seg2=[k for k in d.idx if t0<k<=E._plus_min(t0,60)]
            mfe60=max([s*((d.h[k] if s>0 else d.l[k])-e) for k in seg2] or [0])
            risk=s*(e-t["stop_init"])
            d1=s*(t["t1"]-e) if t["t1"] else None
            base=d.sp.get("09:00"); flowdir=(-1 if (base is not None and d.sp.get(t0,base)-base>0) else 1)
            pxdir=1 if e>d.c[k0] else -1
            legs=" ".join("%s@%s %s"%(g.get("reason"),g.get("ts"),round(g.get("px",0),2)) for g in t["legs"] if not g["open"])
            print("   %s %s %s e=%.2f lvl=%s touch=%s risk=%.2f t1d=%s t2=%s mfe=%.2f mae=%.2f mfe60=%.2f flow=%+d px=%+d | %s | %+.1f만"%(
              t["rule"],t0,"B" if s>0 else "S",e,t.get("touch_level"),t.get("touch_ts"),risk,
              None if d1 is None else round(d1,2), t["t2"], mfe,mae,mfe60,flowdir,pxdir,legs,E.trade_net(t)/1e4))
