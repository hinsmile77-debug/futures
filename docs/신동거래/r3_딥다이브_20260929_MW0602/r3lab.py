# [MW0602 2026-09-29] MW0601 r3_딥다이브_20260928/r3lab.py 사본 - ROOT 상대경로화 + 09:00 봉 결손 폴백(open0·day_hi/lo) 2곳만 수정
# -*- coding: utf-8 -*-
"""R3 연구 하네스 — 신동 엔진(targets/run_trade/levels_at)을 그대로 쓰고,
반전 확인 신호(signal)와 진입 필터(policy)만 갈아끼워 하루를 재생한다.

signal:
  flow      : 개인 위클리 콜−풋 금액 반전 ≥50 (신동 원 규칙, 4일)
  px{X}     : 터치 이후 극값에서 종가가 X pt 반대로 되돌림 (가격 대리, 74일)
  fx{Q}     : 외국인 선물 순매수 수량이 터치 이후 극값에서 Q 계약 반대로 (55일)
policy: 진입 후보(피처 dict) → True 면 진입. 거절하면 busy 가 안 걸리므로 뒤 후보가 살아난다.
"""
import json, os, sqlite3, sys, datetime as dt
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, ROOT)
from strategy.shindong import engine as E, spec as S
from strategy.shindong.calendar import select_flow_product

RAW = ROOT + r"\data\db\raw_data.db"
LV = ROOT + r"\data\db\premarket_levels.db"
FL = ROOT + r"\data\db\option_flow.db"
PR = ROOT + r"\data\db\predictions.db"


def ro(p):
    c = sqlite3.connect("file:%s?mode=ro" % p.replace("\\", "/"), uri=True)
    c.row_factory = sqlite3.Row
    return c


def dates():
    c = ro(LV)
    ds = [r[0] for r in c.execute("select distinct date from premarket_levels where stage='0850' order by date")]
    return ds


_cache = {}


def load_day(d):
    if d in _cache:
        return _cache[d]
    nxt = (dt.date.fromisoformat(d) + dt.timedelta(days=1)).isoformat()
    c = ro(RAW)
    candles, vol = {}, {}
    for r in c.execute("select ts,open,high,low,close,volume from raw_candles where ts>=? and ts<? order by ts", (d, nxt)):
        k = r["ts"][11:16]
        candles[k] = (r["open"], r["high"], r["low"], r["close"])
        vol[k] = r["volume"] or 0
    fx = {}
    for r in c.execute("select ts,fields from raw_investor_futures where ts>=? and ts<? order by ts", (d, nxt)):
        try:
            f = json.loads(r["fields"])
            fx[r["ts"][11:16]] = (f.get("foreign_net_qty"), f.get("institution_net_qty"), f.get("retail_net_qty"))
        except Exception:
            pass
    c.close()
    product, _, _ = select_flow_product(dt.date.fromisoformat(d))
    flow = {}
    c = ro(FL)
    for r in c.execute("select bar_time,product,net_amt from option_investor_flow where trade_date=? and investor='individual' and product in (?,?)",
                       (d, product + "_call", product + "_put")):
        s = flow.setdefault(r["bar_time"], [None, None])
        if r["net_amt"] is not None:
            s[0 if r["product"].endswith("_call") else 1] = float(r["net_amt"])
    c.close()
    c = ro(LV)
    lv = {r["stage"]: dict(r) for r in c.execute("select * from premarket_levels where date=?", (d,))}
    c.close()
    # 미륵이 앙상블 방향(분 단위)
    mk = {}
    try:
        c = ro(PR)
        for r in c.execute("select ts,direction,confidence,weight_collapsed from ensemble_decisions where ts>=? and ts<? order by ts", (d, nxt)):
            mk[r["ts"][11:16]] = (r["direction"], r["confidence"], r["weight_collapsed"])
        c.close()
    except Exception:
        pass
    out = None
    if candles and "0850" in lv:
        L = E.prepare_levels(lv)
        D = E.DayFrame(candles, {k: tuple(v) for k, v in flow.items()})
        # 누적 VWAP (09:00~)
        vw, pv, vv = {}, 0.0, 0.0
        for k in D.idx:
            if k >= "09:00" and k in vol:
                tp = (D.h[k] + D.l[k] + D.c[k]) / 3.0
                pv += tp * vol[k]; vv += vol[k]
            vw[k] = pv / vv if vv else None
        # fx 이어붙이기
        fxd, last = {}, None
        for k in D.idx:
            if k in fx and fx[k][0] is not None:
                last = fx[k]
            if last:
                fxd[k] = last
        out = dict(D=D, L=L, vw=vw, fx=fxd, mk=mk, has_flow=bool(D.sp), atr=lv["0850"].get("atr14"))
    _cache[d] = out
    return out


def _label_kind(L, L0):
    labs = []
    for st in ("0850", "0930"):
        if st in L:
            for x in L[st]["_up"] + L[st]["_dn"]:
                if x[0] == L0:
                    labs += x[1]
    return labs


def run_r3(d, signal="flow", policy=None, start_busy=None, x=1.0, collect=None, tgt_fn=None, trade_fn=None, x4nf=False):
    """R3 만 재생. start_busy: R2 가 점유한 청산 시각(없으면 09:30 전 전부 비움)."""
    P = load_day(d)
    if not P:
        return []
    D, L = P["D"], P["L"]
    busy = start_busy or "09:29"
    trades = []
    lvl_hist = {}      # 맥점별 {touch: n, entries: n, losses: n}
    day_loss = 0
    last_loss = None
    open0 = D.c.get("09:00") or (D.c[min(D.c)] if D.c else None)
    sp0 = D.sp.get("09:00")
    fx0 = (0, 0, 0) if P["fx"] else None  # 당일 누적(개장=0)
    for t in [k for k in D.idx if S.R3_START <= k <= S.NEW_ENTRY_END]:
        if t <= busy or t not in D.c:
            continue
        _, lv = E.levels_at(L, t)
        h, l, c = D.h[t], D.l[t], D.c[t]
        sig = None
        for L0 in lv:
            if L0 - S.TOUCH_NEAR <= h <= L0 + S.TOUCH_FAR and c < L0:
                sig = (-1, L0); break
            if L0 - S.TOUCH_FAR <= l <= L0 + S.TOUCH_NEAR and c > L0:
                sig = (1, L0); break
        if not sig:
            continue
        side, L0 = sig
        hist = lvl_hist.setdefault(L0, {"touch": 0, "entries": 0, "losses": 0, "last_side": 0})
        hist["touch"] += 1
        endw = min(S.NEW_ENTRY_END, E._plus_min(t, S.REV_WIN_MIN))
        ent = None
        for u in D.between(t, endw):
            if signal == "flow":
                seg = [D.sp[k] for k in D.between(t, u) if k in D.sp]
                if not seg or u not in D.sp:
                    continue
                if side < 0 and D.sp[u] - min(seg) >= S.REV_MIN: ent = u; break
                if side > 0 and max(seg) - D.sp[u] >= S.REV_MIN: ent = u; break
            elif signal == "px":
                seg = [D.c[k] for k in D.between(t, u)]
                if side < 0 and max(seg) - D.c[u] >= x: ent = u; break
                if side > 0 and D.c[u] - min(seg) >= x: ent = u; break
            elif signal == "fx":
                seg = [P["fx"][k][0] for k in D.between(t, u) if k in P["fx"]]
                if not seg or u not in P["fx"]:
                    continue
                q = P["fx"][u][0]
                if side < 0 and max(seg) - q >= x: ent = u; break
                if side > 0 and q - min(seg) >= x: ent = u; break
        if not ent:
            continue
        e = D.c[ent]
        span = D.between(t, ent)
        stop = (max(L0 + S.LV_STOP_BUF, max(D.h[k] for k in span) + S.EXT_STOP_BUF) if side < 0
                else min(L0 - S.LV_STOP_BUF, min(D.l[k] for k in span) - S.EXT_STOP_BUF))
        if side * (e - stop) <= 0:
            continue
        t1, t2 = E.targets(L, ent, side, e)
        atr = P["atr"] or 1.0
        z = L["0850"]
        Sall = sorted(set(z["S"] + (L["0930"]["S"] if "0930" in L and ent >= "09:31" else [])))
        vw = P["vw"].get(ent)
        mk = P["mk"].get(ent) or P["mk"].get(t)
        fxn = P["fx"].get(ent); fxb = P["fx"].get(t)
        day_hi = max(D.h[k] for k in D.between("09:00", ent) if k in D.h); day_lo = min(D.l[k] for k in D.between("09:00", ent) if k in D.l)
        m30 = D.c.get("09:30")
        f = dict(
            date=d, touch_ts=t, ent=ent, side=side, L0=L0, e=e, stop=stop, t1=t1, t2=t2,
            risk=abs(e - stop),
            rr=(abs(t1 - e) / abs(e - stop)) if t1 else None,
            has_tgt=t1 is not None,
            trend=(c - open0) if open0 else None,
            trend_align=(side * (e - open0) > 0) if open0 else None,  # 역방향이면 True=추세역행 아님
            trend_atr=abs(e - open0) / atr if open0 else None,
            am_align=(side * (m30 - open0) > 0) if (m30 and open0) else None,
            flow_align=(None if (sp0 is None or ent not in D.sp) else (side == (-1 if D.sp[ent] - sp0 > 0 else 1))),
            fx_align=(None if (fx0 is None or fxn is None) else (side == (1 if fxn[0] - fx0[0] > 0 else -1))),
            fx_day=(None if (fx0 is None or fxn is None) else fxn[0] - fx0[0]),
            vwap_align=(None if vw is None else side * (vw - e) > 0),  # VWAP 쪽으로 되돌림
            vwap_dist_atr=(None if vw is None else (e - vw) / atr),
            touch_n=hist["touch"], entries_n=hist["entries"], lvl_losses=hist["losses"],
            flip=(hist["last_side"] != 0 and hist["last_side"] != side),
            day_losses=day_loss, n_prior=len(trades),
            outside=(e < min(Sall) or e > max(Sall)) if Sall else None,
            range_atr=(day_hi - day_lo) / atr,
            pos_in_range=((e - day_lo) / (day_hi - day_lo)) if day_hi > day_lo else None,
            hour=int(ent[:2]),
            labels="|".join(_label_kind(L, L0)),
            mk_dir=(mk[0] if mk else None), mk_conf=(mk[1] if mk else None),
            mk_align=(None if not mk or mk[0] in (None, 0) else side == (1 if mk[0] > 0 else -1)),
            lat=None,
            since_loss=(None if last_loss is None else (int(ent[:2])*60+int(ent[3:]))-(int(last_loss[:2])*60+int(last_loss[3:]))),
        )
        if policy is not None and not policy(f):
            if collect is not None:
                collect.append(dict(f, taken=False))
            continue
        if tgt_fn is not None:
            t1, t2, stop = tgt_fn(f)
        if x4nf and hist["last_side"] not in (0, side):
            continue
        if x4nf and tgt_fn is None:
            t1, t2 = E.targets_x4(L, ent, side, e)
        tr = (trade_fn or E.run_trade)(D, side, ent, stop, t1, t2)
        if tr["status"] != "CLOSED":
            continue
        net = E.trade_net(tr)
        xs = [k for k in D.idx if ent < k <= (tr["exit_ts"] or "15:05")]
        f["mfe"] = max([side*((D.h[k] if side>0 else D.l[k]) - e) for k in xs] or [0])
        f["mfe30"] = max([side*((D.h[k] if side>0 else D.l[k]) - e) for k in xs if k <= E._plus_min(ent, 30)] or [0])
        f.update(taken=True, net=net, exit_ts=tr["exit_ts"],
                 reasons="/".join(g.get("reason", "") for g in tr["legs"]),
                 pts=sum(g.get("pts", 0) for g in tr["legs"]))
        trades.append(f)
        if collect is not None:
            collect.append(f)
        hist["entries"] += 1
        hist["last_side"] = side
        if net < 0:
            hist["losses"] += 1
            day_loss += 1
            last_loss = tr["exit_ts"]
        busy = tr["exit_ts"] or "99:99"
    return trades


def r2_busy(d):
    """신동 MAIN R2 가 점유한 청산 시각(흐름일만)."""
    P = load_day(d)
    if not P or not P["has_flow"]:
        return None
    res = E.run_day(P["D"], P["L"], "MAIN")
    r2 = [t for t in res["trades"] if t.get("rule") == "R2"]
    return r2[0]["exit_ts"] if r2 else None
