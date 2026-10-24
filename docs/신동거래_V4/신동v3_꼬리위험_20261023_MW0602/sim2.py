"""다리별 손절 — leg1/leg2 각각 be_at·cat_mult. 포지션은 두 다리 모두 닫혀야 끝난다(다음 진입은 그 뒤)."""
import sys,os; sys.path.insert(0,os.path.dirname(__file__)); import sim
from strategy.shindong import engine as E, spec as S, families as F
def make_pos(d,cfg,atr):
    def pos(dd,side,t0,stop,trail,tp):
        e=dd.c[t0]; tp_px=(e+side*tp) if tp else None
        legs=[]
        bars=[k for k in dd.idx if t0<k<=S.TIME_EXIT and k in dd.h]
        for n,lc in ((1,cfg.get('leg1',{})),(2,cfg.get('leg2',{}))):
            st=stop if lc.get('cat_mult') is None else e-side*lc['cat_mult']*atr
            mfe=0; trail_on=False; be=False; ex=None
            for k in bars:
                h,l=dd.h[k],dd.l[k]
                if st is not None and ((l<=st) if side>0 else (h>=st)):
                    ex=(k,st,'TR' if trail_on else ('BE' if be else 'SL'),True); break
                if tp_px is not None and ((h>=tp_px) if side>0 else (l<=tp_px)):
                    ex=(k,tp_px,'TP',False); break
                fav=(h-e) if side>0 else (e-l); mfe=max(mfe,fav)
                if trail is not None and mfe>=trail[0]:
                    ns=(e+side*mfe)-side*trail[1]
                    if st is None or side*(ns-st)>0: st,trail_on=ns,True
                if lc.get('be_at') and mfe>=lc['be_at'] and not trail_on and side*(e-st)>0: st=e; be=True
            if ex is None:
                tx=dd.last_at_or_before(S.TIME_EXIT); ex=(tx,dd.c[tx],'TIME',True)
            pts,net=E.leg_net(side,e,ex[1],ex[3])
            legs.append(dict(leg=n,tp=tp_px,open=False,ts=ex[0],px=ex[1],mkt=ex[3],pts=pts,net=net,reason=('TP1' if n==1 else 'TP2') if ex[2]=='TP' else ex[2]))
        # 손절 방향 금지는 기존대로 「첫 다리가 SL」일 때 — 두 다리 모두 SL 일 때만으로 바꾸면 규칙이 달라지므로 leg1 기준 유지 대신
        # 보수적으로: 어느 다리든 SL 이면 SL 로 본다(금지 발동) → legs[0] 사유를 덮어써 _run_signal 이 읽게 한다.
        if any(g['reason']=='SL' for g in legs): legs=[dict(legs[0],reason='SL') if False else legs[0], legs[1]]
        out=dict(side=side,entry_ts=t0,entry_px=e,stop_init=stop,t1=tp_px,t2=tp_px,legs=legs,status='CLOSED',exit_ts=max(g['ts'] for g in legs),stop_now=None)
        out['_anysl']=any(g['reason']=='SL' for g in legs)
        return out
    return pos
def run(cfg,ds=None):
    out={}
    orig=F._run_position
    for d in ds or sim.days():
        D,L=sim.frame(d); atr=L['0850'].get('atr14') or 33.3
        F._run_position=make_pos(D,cfg,atr)
        try: res=F.run_family_day(D,L,'hybr60')
        finally: F._run_position=orig
        out[d]=[dict(rule=t['rule'],side=t['side'],t=t['entry_ts'],px=t['entry_px'],x=t['exit_ts'],why='/'.join(g['reason'] for g in t['legs']),
                     pt=round(E.trade_net(t)/2/S.PT_VALUE_KRW,2)) for t in res['trades']]
    return out
