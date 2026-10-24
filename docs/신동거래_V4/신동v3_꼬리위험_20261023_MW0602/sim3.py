"""새 기준선 = v3 + 양다리 본전이동@3 + 본전청산 상한 제외(방향 금지 없음).
그 위에 유형② 대책: struct 손절 / 콜풋 반전 청산(본전 전) / 진입 확인 / (수량은 사후 원화 환산)."""
import sys,os,sqlite3; sys.path.insert(0,os.path.dirname(__file__)); import sim
from strategy.shindong import engine as E, spec as S, families as F
BE_AT=3.0
orig_rs=F._run_signal
def prevday(d):
    c=sqlite3.connect('data/db/raw_data.db')
    r=c.execute("select substr(ts,1,10) from raw_candles where ts<? order by ts desc limit 1",(d,)).fetchone()
    if not r: return None,None
    hl=c.execute("select max(high),min(low) from raw_candles where ts>=? and ts<?",(r[0],d)).fetchone(); return hl
PREV={}
def make_pos(d,L,cfg,atr,day):
    cum,_=F._flow_signal(d,d.sp,S.FLOWC_K,-1)
    r60=F._roll_signal(d.sp,S.FLOWR_WIN_MIN,S.FLOWR_K,-1)
    if day not in PREV: PREV[day]=prevday(day)
    ph,pl=PREV[day]
    def struct_stop(side,t0,e,cat):
        """역행 쪽 가장 가까운 레벨 + 버퍼. 후보: 장전 구조맥점 S · 진입 시점까지 장중 고/저 · 전일 고/저"""
        cands=[]
        src=cfg.get('struct')
        if src in ('lv','both','all'):
            _,lv=E.levels_at(L,t0); cands+=lv
        if src in ('ext','both','all'):
            ks=[k for k in d.idx if '09:00'<=k<=t0 and k in d.h]
            if ks: cands.append(max(d.h[k] for k in ks) if side<0 else min(d.l[k] for k in ks))
        if src=='all' and ph is not None: cands+=[ph,pl]
        md=cfg.get('min_dist',2.0)
        adv=[x for x in cands if x is not None and side*(e-x)>=md]   # 역행 쪽(매도면 위), 최소거리 이상
        if not adv: return cat, False
        lvl=max(adv) if side>0 else min(adv)
        st=lvl-side*cfg.get('buf',S.LV_STOP_BUF)
        if side*(e-st)>side*(e-cat): return cat, False   # 재난손절보다 멀면 재난손절
        return st, True
    def pos(dd,side,t0,stop,trail,tp):
        e=dd.c[t0]; tp_px=(e+side*tp) if tp else None
        cat=stop; st0=stop; used=False
        if cfg.get('struct'): st0,used=struct_stop(side,t0,e,cat)
        bars=[k for k in dd.idx if t0<k<=S.TIME_EXIT and k in dd.h]
        rule_sig = cum if t0<'10:00' else r60
        st=st0; mfe=0; mae=0; trail_on=False; be=False; ex=None; mae_t=None
        for k in bars:
            h,l=dd.h[k],dd.l[k]
            if cfg.get('struct_close') and used and not be and not trail_on:
                # 종가 돌파 확인형: 레벨 손절은 종가 기준, 재난손절은 장중 기준
                if (l<=cat) if side>0 else (h>=cat): ex=(k,cat,'SL',True); break
                if (dd.c[k]<=st) if side>0 else (dd.c[k]>=st): ex=(k,dd.c[k],'LVSL',True); break
            elif st is not None and ((l<=st) if side>0 else (h>=st)):
                ex=(k,st,'TR' if trail_on else ('BE' if be else ('LVSL' if used else 'SL')),True); break
            if tp_px is not None and ((h>=tp_px) if side>0 else (l<=tp_px)):
                ex=(k,tp_px,'TP',False); break
            fav=(h-e) if side>0 else (e-l); adv=(e-l) if side>0 else (h-e)
            mfe=max(mfe,fav); mae=max(mae,adv)
            if not be and not trail_on and cfg.get('rev'):
                s=rule_sig(k) if rule_sig else 0
                if cfg['rev']=='opp' and s==-side: ex=(k,dd.c[k],'REV',True); break
                if cfg['rev']=='opp_adv' and s==-side and mae>=cfg.get('rev_mae',3): ex=(k,dd.c[k],'REV',True); break
            if not be and not trail_on and cfg.get('mae_cut') and mae>=cfg['mae_cut']*atr and mfe<BE_AT:
                ex=(k,dd.c[k],'MAEX',True); break
            if trail is not None and mfe>=trail[0]:
                ns=(e+side*mfe)-side*trail[1]
                if st is None or side*(ns-st)>0: st,trail_on=ns,True
            if mfe>=BE_AT and not trail_on and side*(e-st)>0: st=e; be=True
        if ex is None:
            tx=dd.last_at_or_before(S.TIME_EXIT); ex=(tx,dd.c[tx],'TIME',True)
        legs=[]
        for n in (1,2):
            pts,net=E.leg_net(side,e,ex[1],ex[3])
            legs.append(dict(leg=n,tp=tp_px,open=False,ts=ex[0],px=ex[1],mkt=ex[3],pts=pts,net=net,
                             reason=('TP1' if n==1 else 'TP2') if ex[2]=='TP' else ('SL' if ex[2] in ('LVSL','REV','MAEX') and cfg.get('ban_cut',True) else ex[2])))
        return dict(side=side,entry_ts=t0,entry_px=e,stop_init=st0,t1=tp_px,t2=tp_px,legs=legs,status='CLOSED',exit_ts=ex[0],
                    stop_now=st,_be=(ex[2]=='BE'),_why=ex[2],_mfe=mfe,_mae=mae,_stopd=round(abs(e-st0),1),_used=used)
    return pos
def rs(d,sig,rule,stop_fn,trail,tp,max_trades,**kw):
    if CUR.get('confirm'):
        s0=sig; prev={'k':None,'v':0}
        def sig2(k):
            v=s0(k); pv=prev['v']; pk=prev['k']; prev.update(k=k,v=v)
            if not v or pv!=v or pk is None: return 0
            return v if (d.c[k]-d.c[pk])*v>0 else 0
        sig=sig2
        sa=kw.get('sig_after')
        if sa:
            pr={'k':None,'v':0}
            def sa2(k,_s=sa):
                v=_s(k); pv=pr['v']; pk=pr['k']; pr.update(k=k,v=v)
                if not v or pv!=v or pk is None: return 0
                return v if (d.c[k]-d.c[pk])*v>0 else 0
            kw['sig_after']=sa2
    out=orig_rs(d,sig,rule,stop_fn,trail,tp,max_trades+10,**kw); keep=[]; n=0
    for t in out:
        if n>=max_trades: break
        keep.append(t); n+= 0 if t.get('_be') else 1
    return keep
CUR={}
def run(cfg,ds=None):
    global CUR; CUR=cfg; out={}; orig=F._run_position
    F._run_signal=rs
    for day in ds or sim.days():
        D,L=sim.frame(day); atr=L['0850'].get('atr14') or 33.3
        F._run_position=make_pos(D,L,cfg,atr,day)
        try: res=F.run_family_day(D,L,'hybr60')
        finally: F._run_position=orig
        out[day]=[dict(rule=t['rule'],side=t['side'],t=t['entry_ts'],px=t['entry_px'],x=t['exit_ts'],why=t['_why'],mfe=round(t['_mfe'],1),mae=round(t['_mae'],1),
                       stopd=t['_stopd'],used=t['_used'],atr=round(atr,1),pt=round(E.trade_net(t)/2/S.PT_VALUE_KRW,2)) for t in res['trades']]
    F._run_signal=orig_rs
    return out
