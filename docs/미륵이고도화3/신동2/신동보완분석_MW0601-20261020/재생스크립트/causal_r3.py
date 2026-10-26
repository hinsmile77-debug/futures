# -*- coding: utf-8 -*-
"""R3 신호 선택을 「확인(진입) 시각 우선」으로 바꾼 인과 엔진 사본 — 철회 메커니즘 검증·반사실. 읽기 전용."""
import sys, os, json, inspect, sqlite3, datetime as dt, statistics as st
ROOT=r"C:\Users\82108\PycharmProjects\futures"; sys.path.insert(0, ROOT)
from strategy.shindong import engine as E, runner, spec as S
from strategy.shindong.calendar import select_flow_product
src=inspect.getsource(E.run_day)
a=src.index("    # R3\n"); b=src.index('    return {"decision": dec, "trades": trades}')
R3_CAUSAL='''    # R3 — [인과판] 확인(진입) 시각이 가장 이른 신호가 자리를 갖는다
    def _cand(t):
        if t not in d.c:
            return None
        _, lv = levels_at(L, t)
        h, l, c = d.h[t], d.l[t], d.c[t]
        sig = None
        for L0 in lv:
            if L0 - S.TOUCH_NEAR <= h <= L0 + S.TOUCH_FAR and c < L0:
                sig = (-1, L0); break
            if L0 - S.TOUCH_FAR <= l <= L0 + S.TOUCH_NEAR and c > L0:
                sig = (1, L0); break
        if not sig:
            return None
        side, L0 = sig
        if x4nf and lvl_side.get(L0, side) != side:
            return None
        if f2:
            if t not in d.sp:
                return None
            base = d.sp.get(S.CONF_BASE)
            trend = -1 if (base is not None and d.sp[t] - base > 0) else 1
            if side != trend:
                return None
        endw = min(S.NEW_ENTRY_END, _plus_min(t, S.REV_WIN_MIN))
        ent = None
        for u in d.between(t, endw):
            seg = [d.sp[k] for k in d.between(t, u) if k in d.sp]
            if not seg or u not in d.sp:
                continue
            if side < 0 and d.sp[u] - min(seg) >= S.REV_MIN:
                ent = u; break
            if side > 0 and max(seg) - d.sp[u] >= S.REV_MIN:
                ent = u; break
        if not ent:
            return None
        e = d.c[ent]
        if broken_guard and side * (e - L0) <= 0:
            return None
        span = d.between(t, ent)
        stop = (max(L0 + S.LV_STOP_BUF, max(d.h[k] for k in span) + S.EXT_STOP_BUF) if side < 0
                else min(L0 - S.LV_STOP_BUF, min(d.l[k] for k in span) - S.EXT_STOP_BUF))
        if side * (e - stop) <= 0:
            return None
        if atrs and atr14 is not None:
            wide = e - side * S.R3_ATR_STOP_K * atr14
            if side * (stop - wide) > 0:
                stop = wide
        return (ent, t, side, L0, e, stop)
    mins = [k for k in d.idx if S.R3_START <= k <= S.NEW_ENTRY_END]
    while True:
        cands = [x for x in (_cand(t) for t in mins if t > busy) if x is not None]
        if not cands:
            break
        ent, t, side, L0, e, stop = min(cands, key=lambda x: (x[0], x[1]))
        t1, t2 = (targets_x4 if x4nf else targets)(L, ent, side, e)
        tr = run_trade(d, side, ent, stop, t1, t2, e2=e2, trail=tr44)
        tr.update(rule="R3", touch_level=L0, touch_ts=t)
        trades.append(tr)
        lvl_side[L0] = side
        busy = tr["exit_ts"] or "99:99"
'''
src=(src[:a]+R3_CAUSAL+src[b:]).replace("def run_day(","def run_day_c(",1)
ns=E.__dict__; exec(src, ns); run_day_c=ns["run_day_c"]
DB=os.path.join(ROOT,"data","db"); P=[os.path.join(DB,x) for x in ("raw_data.db","option_flow.db","premarket_levels.db")]
DAYS=sys.argv[1].split(",")
def inputs(d0):
    prod=select_flow_product(dt.date.fromisoformat(d0))[0]; return runner.load_inputs(d0,prod,*P)
def live_sim(fn,d0,c,f,l,variant="MAIN"):
    """분 단위 라이브 흉내: 각 horizon 에서 재생 → 처음 보인 거래(진입분·방향)를 모으고 마지막에 사라진 것 = 철회."""
    L=E.prepare_levels(l); seen={}; mins=sorted(set(c)|set(f)); mins=[m for m in mins if "09:30"<=m<="15:08"]
    last=set()
    for h in mins:
        d=E.DayFrame(c,f,horizon=h); res=fn(d,L,variant)
        keys={(x["rule"],x["entry_ts"],x["side"]) for x in res["trades"]}
        for k in keys: seen.setdefault(k,h)
        last=keys
    return seen,last
out={}
for d0 in DAYS:
    c,f,l=inputs(d0); L=E.prepare_levels(l); d=E.DayFrame(c,f)
    rows={}
    for nm,fn in (("현행",E.run_day),("인과",run_day_c)):
        res=fn(d,L,"MAIN"); cl=[x for x in res["trades"] if x["status"]=="CLOSED"]
        rows[nm]=dict(net=sum(E.trade_net(x) for x in cl)/1e4,n=len(cl),ent=[(x["entry_ts"],x["side"]) for x in cl if x["rule"]=="R3"],
                      l1=sum(x["legs"][0]["net"] for x in cl)/1e4)
    if len(sys.argv)>2 and d0 in sys.argv[2].split(","):
        for nm,fn in (("현행",E.run_day),("인과",run_day_c)):
            seen,last=live_sim(fn,d0,c,f,l)
            rows[nm]["retract"]=sorted("%s%s"%(k[1],"+" if k[2]>0 else "-") for k in seen if k not in last)
    out[d0]=rows
    print(d0[5:],"현행 %+7.1f(%d) | 인과 %+7.1f(%d) | 차 %+6.1f"%(rows["현행"]["net"],rows["현행"]["n"],rows["인과"]["net"],rows["인과"]["n"],rows["인과"]["net"]-rows["현행"]["net"]),
          (" | 분단위 철회 현행 %s · 인과 %s"%(rows["현행"].get("retract"),rows["인과"].get("retract"))) if "retract" in rows["현행"] else "")
json.dump(out,open(sys.argv[3] if len(sys.argv)>3 else "causal_out.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
xs=[out[d]["현행"]["net"] for d in DAYS]; ys=[out[d]["인과"]["net"] for d in DAYS]
print("합 현행 %+.1f (효율 %.2f) · 인과 %+.1f (효율 %.2f) · 최악 %+.1f / %+.1f"%(sum(xs),st.mean(xs)/st.stdev(xs),sum(ys),st.mean(ys)/st.stdev(ys),min(xs),min(ys)))
