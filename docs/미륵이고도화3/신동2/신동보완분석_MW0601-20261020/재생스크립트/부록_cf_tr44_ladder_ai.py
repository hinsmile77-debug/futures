# -*- coding: utf-8 -*-
import sys, os, json, sqlite3, datetime as _dt
ROOT=r"C:\Users\82108\PycharmProjects\futures"; sys.path.insert(0, os.path.join(ROOT,"scripts")); sys.path.insert(0, ROOT)
import shindong2_live as SL
_hm, _fmt = SL._hm, SL._fmt

def candles(day):
    con=sqlite3.connect("file:%s?mode=ro"%os.path.join(ROOT,"data","db","raw_data.db").replace("\\","/"),uri=True)
    nxt=(_dt.date.fromisoformat(day)+_dt.timedelta(days=1)).isoformat()
    cs=[(str(r[0])[11:16],float(r[1]),float(r[2]),float(r[3]),float(r[4])) for r in con.execute(
        "SELECT ts,open,high,low,close FROM raw_candles WHERE ts>=? AND ts<? ORDER BY ts",(day,nxt))]
    con.close(); return [c for c in cs if "08:45"<=c[0]]

def sim(day, cs, records, trail=None):
    """SL.simulate_ai 사본 + trail=(act,dist): 진입가 대비 유리 극값 ≥ act → 손절 = 극값 ∓ dist(한 방향, 다음 봉부터)."""
    recs=[]
    for r in records:
        if r.get("backfill") or (r.get("variant") or "live")!="live": continue
        ts=_dt.datetime.fromisoformat(r["ts"])
        eff="08:45" if ts.date().isoformat()<day or ts.strftime("%H:%M")<"08:45" else _fmt(_hm(ts.strftime("%H:%M"))+1)
        recs.append((eff,r))
    recs.sort(key=lambda x:(x[0],x[1]["ts"]))
    bars=[c for c in cs if _hm(c[0])<_hm(SL.FORCE_EXIT)]
    pend=pos=None; trades=[]; j=0
    for c in bars:
        t=c[0]
        while j<len(recs) and _hm(recs[j][0])<=_hm(t):
            eff,r=recs[j]; j+=1
            act=r.get("action","plan"); sgn=1 if r.get("dir")=="매수" else -1 if r.get("dir")=="매도" else 0
            if act=="plan" and sgn:
                if pos is None: pend=dict(sgn=sgn,entry=r.get("entry"),stop=r.get("stop"),target=r.get("target"),rid=r["id"],t=eff)
                elif pos["sgn"]==sgn: pos.update(stop=r.get("stop",pos["stop"]),target=r.get("target",pos["target"]))
            elif act=="manage":
                tg=pos or pend
                if tg is not None:
                    if r.get("stop") is not None: tg["stop"]=r["stop"]
                    if r.get("target") is not None: tg["target"]=r["target"]
            elif act=="exit" and pos is not None: pos["exit_now"]=(r["id"],t)
            elif act in ("stand","exit"): pend=None
        if pos is not None and pos.get("exit_now"):
            px=c[1]; trades.append(dict(pos["tr"],exit_t=t,exit_px=round(px,2),why="재량 청산",pnl=round((px-pos["fill"])*pos["sgn"],2))); pos=None
        if pos is None and pend is not None:
            if _hm(t)>_hm(SL.PLAN_EXPIRE): pend=None
            elif pend["entry"] is None:
                pos=dict(sgn=pend["sgn"],fill=c[1],stop=pend["stop"],target=pend["target"],best=c[1],tstop=None,
                         tr=dict(entry_t=t,side="매수" if pend["sgn"]>0 else "매도",fill=round(c[1],2))); pend=None
            elif c[3]<=pend["entry"]<=c[2]:
                pos=dict(sgn=pend["sgn"],fill=pend["entry"],stop=pend["stop"],target=pend["target"],best=pend["entry"],tstop=None,
                         tr=dict(entry_t=t,side="매수" if pend["sgn"]>0 else "매도",fill=pend["entry"])); pend=None
        if pos is not None:
            s=pos["sgn"]; st=pos["stop"]
            if pos["tstop"] is not None and (st is None or s*(pos["tstop"]-st)>0): st=pos["tstop"]   # 트레일이 더 유리하면 그것
            hs=st is not None and ((c[3]<=st) if s>0 else (c[2]>=st))
            ht=pos["target"] is not None and ((c[2]>=pos["target"]) if s>0 else (c[3]<=pos["target"]))
            if hs or ht:
                px,why=(st,("트레일" if (pos["tstop"] is not None and st==pos["tstop"]) else "손절")) if hs else (pos["target"],"목표 청산")
                trades.append(dict(pos["tr"],exit_t=t,exit_px=px,why=why,pnl=round((px-pos["fill"])*s,2))); pos=None
            elif trail is not None and t != pos["tr"]["entry_t"]:      # 이 봉 극값은 다음 봉부터 · 진입봉 제외(엔진 run_trade 와 같다)
                pos["best"]=max(pos["best"],c[2]) if s>0 else min(pos["best"],c[3])
                if s*(pos["best"]-pos["fill"])>=trail[0]:
                    cand=pos["best"]-s*trail[1]
                    if pos["tstop"] is None or s*(cand-pos["tstop"])>0: pos["tstop"]=cand
    if pos is not None:
        px=bars[-1][4] if bars else pos["fill"]
        trades.append(dict(pos["tr"],exit_t=bars[-1][0],exit_px=round(px,2),why="15:10 강제청산",pnl=round((px-pos["fill"])*pos["sgn"],2)))
    return dict(trades=trades,pnl=round(sum(t["pnl"] for t in trades),2))

out={}
for d in sorted(os.listdir(os.path.join(ROOT,"data","shindong2_live"))):
    if not d.isdigit(): continue
    day="%s-%s-%s"%(d[:4],d[4:6],d[6:]); ev=os.path.join(ROOT,"data","shindong2_live",d,"eval.json")
    if not os.path.exists(ev): continue
    rec=json.load(open(ev,encoding="utf-8")).get("live_ai") or {}
    log=SL.load_ai_log(day); cs=candles(day)
    base=sim(day,cs,log); orig=SL.simulate_ai(day,cs,log)
    t44=sim(day,cs,log,trail=(4.0,4.0)); t64=sim(day,cs,log,trail=(6.0,4.0))
    out[day]=dict(recorded=rec.get("pnl"),orig=orig["pnl"],base=base["pnl"],tr44=t44["pnl"],tr64=t64["pnl"],
                  n=len(base["trades"]),trades44=t44["trades"],trades_base=base["trades"])
    print(day,"기록 %s | 원함수 %s | 사본 %s | TR44 %s | 6/4 %s | n=%d"%(rec.get("pnl"),orig["pnl"],base["pnl"],t44["pnl"],t64["pnl"],len(base["trades"])))
json.dump(out,open(sys.argv[1],"w",encoding="utf-8"),ensure_ascii=False,indent=1)
