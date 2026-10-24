"""v3 MAIN(hybr60) 재생 + 꼬리위험 대안 — 읽기 전용. 엔진 함수 재사용, _run_position 만 감싼다."""
import sys,os,sqlite3,json,datetime as dt
sys.path.insert(0,os.getcwd())
from strategy.shindong import runner, engine as E, spec as S, families as F
from strategy.shindong.calendar import select_flow_product
DB='data/db/'
ORIG=F._run_position
def days():
    c=sqlite3.connect(DB+'option_flow.db'); c2=sqlite3.connect(DB+'premarket_levels.db')
    lv=set(r[0] for r in c2.execute("select distinct date from premarket_levels where stage='0850'"))
    return [r[0] for r in c.execute("select distinct trade_date from option_investor_flow where investor='individual' order by 1") if r[0] in lv]
CACHE={}
def frame(d):
    if d not in CACHE:
        prod,_,_=select_flow_product(dt.date.fromisoformat(d))
        cd,fl,lr=runner.load_inputs(d,prod,DB+'raw_data.db',DB+'option_flow.db',DB+'premarket_levels.db')
        fx=runner.load_fx(d,DB+'raw_data.db')
        CACHE[d]=(E.DayFrame(cd,fl,fx=fx),E.prepare_levels(lr))
    return CACHE[d]

CFG={}
def make_pos(d):
    """옵션: cat_mult(재난손절 ATR배수 덮어쓰기) · ts_min/ts_mfe(시간손절: ts_min분 안에 MFE<ts_mfe면 청산)
       be_at(MFE≥be_at → 손절을 진입가로) · rev(보유 중 반대 신호 → 청산: 'r60'|'cum'|'both')"""
    cum,_=F._flow_signal(d,d.sp,S.FLOWC_K,-1)
    r60=F._roll_signal(d.sp,S.FLOWR_WIN_MIN,S.FLOWR_K,-1)
    def pos(dd,side,t0,stop,trail,tp):
        c=CFG
        e=dd.c[t0]
        if c.get('cat_mult') is not None and stop is not None:
            atr=CFG['_atr']; stop=e-side*c['cat_mult']*atr
        if c.get('cat_cap') is not None and stop is not None:
            stop=e-side*min(abs(e-stop),c['cat_cap'])
        tp_px=(e+side*tp) if tp else None
        st=stop; mfe=0.0; mae=0.0; trail_on=False; ex=None
        bars=[k for k in dd.idx if t0<k<=S.TIME_EXIT and k in dd.h]
        t0m=int(t0[:2])*60+int(t0[3:])
        for k in bars:
            h,l=dd.h[k],dd.l[k]
            if st is not None and ((l<=st) if side>0 else (h>=st)):
                ex=(k,st,'TR' if trail_on else ('BE' if CFG.get('_be') else 'SL'),True); break
            if tp_px is not None and ((h>=tp_px) if side>0 else (l<=tp_px)):
                ex=(k,tp_px,'TP',False); break
            fav=(h-e) if side>0 else (e-l); adv=(e-l) if side>0 else (h-e)
            mfe=max(mfe,fav); mae=max(mae,adv)
            km=int(k[:2])*60+int(k[3:])
            # 봉 종가 기준 판단 → 그 봉 종가 청산(신호봉 종가 진입과 같은 관례)
            if c.get('rev'):
                s1=r60(k) if c['rev'] in ('r60','both') else 0
                s2=cum(k) if (cum and c['rev'] in ('cum','both')) else 0
                if (s1==-side or s2==-side) and not trail_on:
                    ex=(k,dd.c[k],'REV',True); break
            if c.get('ts_min') and not trail_on and km-t0m>=c['ts_min'] and mfe<c.get('ts_mfe',S.FLOW_TRAIL[0]):
                ex=(k,dd.c[k],'TS',True); break
            if trail is not None and mfe>=trail[0]:
                ns=(e+side*mfe)-side*trail[1]
                if st is None or side*(ns-st)>0: st,trail_on=ns,True
            if c.get('be_at') and mfe>=c['be_at'] and not trail_on:
                if st is None or side*(e-st)>0: st=e; CFG['_be']=True
        CFG['_be']=False
        if ex is None:
            tx=dd.last_at_or_before(S.TIME_EXIT); ex=(tx,dd.c[tx],'TIME',True)
        legs=[]
        for n in (1,2):
            pts,net=E.leg_net(side,e,ex[1],ex[3])
            legs.append(dict(leg=n,tp=tp_px,open=False,ts=ex[0],px=ex[1],mkt=ex[3],pts=pts,net=net,reason=('TP1' if n==1 else 'TP2') if ex[2]=='TP' else ex[2]))
        return dict(side=side,entry_ts=t0,entry_px=e,stop_init=stop,t1=tp_px,t2=tp_px,legs=legs,status='CLOSED',exit_ts=ex[0],stop_now=st,mfe=mfe,mae=mae)
    return pos

def entry_filter_wrap(d,L):
    """진입 필터: CFG['chase'] = 09:00 종가 대비 신호 방향으로 이미 X×ATR 이상 움직였으면 첫 FLOWC 진입 생략"""
    pass

def run(cfg,ds=None):
    global CFG
    out={}
    for d in ds or days():
        D,L=frame(d)
        CFG=dict(cfg); CFG['_atr']=L['0850'].get('atr14') or 33.3
        F._run_position=make_pos(D)
        if cfg.get('chase') is not None or cfg.get('gapdir'):
            base=D.c.get('09:00')
            o=D.c.get('08:45') if False else None
            orig_sig=F._flow_signal
            def fsig(dd,series,k,sign,_o=orig_sig):
                sig,b=_o(dd,series,k,sign)
                if sig is None: return sig,b
                state={'n':0}
                def s2(t):
                    v=sig(t)
                    if v and series is dd.sp and k==S.FLOWC_K and base is not None and cfg.get('chase') is not None:
                        mv=(dd.c[t]-base)*v   # 신호 방향으로 이미 간 거리(+면 추격)
                        if mv>=cfg['chase']*CFG['_atr']: return 0
                    return v
                return s2,b
            F._flow_signal=fsig
        try:
            res=F.run_family_day(D,L,'hybr60')
        finally:
            F._run_position=ORIG
            if cfg.get('chase') is not None: F._flow_signal=orig_sig
        out[d]=[dict(rule=t['rule'],side=t['side'],t=t['entry_ts'],px=t['entry_px'],x=t['exit_ts'],why=t['legs'][0]['reason'],
                     pt=round(E.trade_net(t)/2/S.PT_VALUE_KRW,2),mfe=round(t.get('mfe',0),2),mae=round(t.get('mae',0),2)) for t in res['trades']]
    return out

def summ(out,label):
    daily={d:sum(t['pt'] for t in v) for d,v in out.items()}
    tr=[t for v in out.values() for t in v]
    cum=pk=mdd=0
    for d in sorted(daily): cum+=daily[d]; pk=max(pk,cum); mdd=max(mdd,pk-cum)
    oos=sum(v for d,v in daily.items() if d>='2026-10-19')
    w=[t['pt'] for t in tr if t['pt']>0]; l=[t['pt'] for t in tr if t['pt']<=0]
    return dict(label=label,n=len(tr),sum=round(sum(daily.values()),1),oos=round(oos,1),worst_day=round(min(daily.values()),1),
                worst_tr=round(min(t['pt'] for t in tr),1),n_le_m10=sum(t['pt']<=-10 for t in tr),mdd=round(mdd,1),
                win=round(100*len(w)/len(tr)),pf=round(sum(w)/abs(sum(l)),2) if l and sum(l) else None,
                d1023=round(daily.get('2026-10-23',0),1))
if __name__=='__main__':
    base=run({})
    json.dump(base,open(sys.argv[1],'w',encoding='utf-8'),ensure_ascii=False,indent=0)
    print(summ(base,'v3 기준'))
    for d,v in base.items(): print(d, round(sum(t['pt'] for t in v),2), [(t['rule'],t['side'],t['t'],t['x'],t['why'],t['pt'],'mfe',t['mfe'],'mae',t['mae']) for t in v])
