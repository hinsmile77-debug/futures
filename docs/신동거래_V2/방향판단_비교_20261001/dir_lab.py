# -*- coding: utf-8 -*-
"""방향 판단 방법 비교 — (1) 콜−풋(v2.1) (2) 풋 증감 (3) 풋 + 다른 지표(외인선물·외인옵션·가격).
청산은 v2.1 그대로(재난 손절 0.6ATR·전면 중단 · 트레일 6/4 · 익절 12 · 3회 · 15:05) — **방향 판단만** 바꾼다.
7일(9/21~10/1) · 당일 하루씩만 읽는다. 저장소 루트에서 실행.
평가: 표본 안 최적 · 계열 전체 분포 · LODO(하루를 빼고 나머지 6일로 고른 설정을 그 하루에 적용 — 7번 합)."""
import os, sys, sqlite3, datetime as dt, itertools, statistics as st, json
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, ROOT)
from strategy.shindong import engine as E, runner, spec as S
from strategy.shindong.calendar import select_flow_product
from config.settings import RAW_DATA_DB, PREMARKET_LEVELS_DB, WEEKLY_OPTION_FLOW_DB
DAYS = ["2026-09-21", "2026-09-22", "2026-09-23", "2026-09-28", "2026-09-29", "2026-09-30", "2026-10-01"]
FLOW = WEEKLY_OPTION_FLOW_DB if os.path.isabs(WEEKLY_OPTION_FLOW_DB) else os.path.join(ROOT, WEEKLY_OPTION_FLOW_DB)


def load(day):
    prod, _, _ = select_flow_product(dt.date.fromisoformat(day))
    c, f, lv = runner.load_inputs(day, prod, RAW_DATA_DB, FLOW, PREMARKET_LEVELS_DB)
    D = E.DayFrame(c, f, fx=runner.load_fx(day, RAW_DATA_DB))
    L = E.prepare_levels(lv)
    fo = {}
    con = sqlite3.connect("file:%s?mode=ro" % FLOW.replace("\\", "/"), uri=True)
    for bt, p, na in con.execute("select bar_time,product,net_amt from option_investor_flow where trade_date=? and investor='foreign' "
                                 "and product in (?,?)", (day, prod + "_call", prod + "_put")):
        if na is not None:
            fo.setdefault(bt, [None, None])[0 if p.endswith("_call") else 1] = float(na)
    con.close()
    fsp, lc, lp = {}, None, None
    for k in D.idx:
        if k in fo:
            lc = fo[k][0] if fo[k][0] is not None else lc
            lp = fo[k][1] if fo[k][1] is not None else lp
        if lc is not None and lp is not None:
            fsp[k] = lc - lp
    ser = {"sp": D.sp, "call": D.call, "put": D.put, "fx": D.fx, "fsp": fsp, "px": D.c}
    idx = [k for k in D.idx if "09:00" <= k <= S.TIME_EXIT and k in D.c]
    pos = {k: i for i, k in enumerate(idx)}
    return dict(D=D, L=L, ser=ser, idx=idx, pos=pos)


def delta(P, src, k, mode, win):
    s = P["ser"][src]
    v = s.get(k)
    if v is None:
        return None
    if mode == "level":
        b = s.get("09:00")
        if b is None:
            ks = [x for x in P["idx"] if x in s]
            if not ks or k < ks[0]:
                return None
            b = s[ks[0]]
        return v - b
    i = P["pos"].get(k)
    if i is None or i - win < 0:
        return None
    r = s.get(P["idx"][i - win])
    return None if r is None else v - r


def make_sig(P, comps, combine="all"):
    """comps: [(src, mode, win, K, orient)]. orient +1 = 계열 증가 → 매수, −1 = 계열 증가 → 매도.
    all: 모든 성분이 같은 방향(문턱 통과) / gate: 첫 성분이 신호, 나머지는 **부호만** 같은 쪽이어야 함."""
    def one(c, k, thr=True):
        src, mode, win, K, orient = c
        dv = delta(P, src, k, mode, win)
        if dv is None:
            return 0
        if thr:
            return orient * (1 if dv >= K else (-1 if dv <= -K else 0))
        return orient * (1 if dv > 0 else (-1 if dv < 0 else 0))

    def sig(k):
        d0 = one(comps[0], k)
        if not d0:
            return 0
        for c in comps[1:]:
            if one(c, k, thr=(combine == "all")) != d0:
                return 0
        return d0
    return sig


def run(P, sig, cat_atr=S.FLOW_CAT_STOP_ATR, trail=S.FLOW_TRAIL, tp=S.FLOW_TP, mt=S.FLOW_MAX_TRADES):
    D, L = P["D"], P["L"]
    cat = cat_atr * (L["0850"].get("atr14") or (S.FLOW_CAT_STOP_FALLBACK_PT / S.FLOW_CAT_STOP_ATR))
    trades, pos, halted = [], None, False
    for k in P["idx"]:
        if pos is not None:
            side, e = pos["side"], pos["e"]
            h, l = D.h[k], D.l[k]
            x = why = None
            if (l <= pos["stop"]) if side > 0 else (h >= pos["stop"]):
                x, why, mkt = pos["stop"], ("TR" if pos["tr"] else "SL"), True
            elif (h >= pos["tp"]) if side > 0 else (l <= pos["tp"]):
                x, why, mkt = pos["tp"], "TP", False
            elif k >= S.TIME_EXIT:
                x, why, mkt = D.c[k], "TIME", True
            if x is not None:
                trades.append(dict(side=side, et=pos["t"], e=e, xt=k, x=x, why=why, net=2 * E.leg_net(side, e, x, mkt)[1]))
                halted = halted or why == "SL"
                pos = None
                continue
            pos["mfe"] = max(pos["mfe"], (h - e) if side > 0 else (e - l))
            if pos["mfe"] >= trail[0]:
                ns = (e + side * pos["mfe"]) - side * trail[1]
                if side * (ns - pos["stop"]) > 0:
                    pos["stop"], pos["tr"] = ns, True
            continue
        if halted or k > S.FLOW_LAST_ENTRY or len(trades) >= mt:
            continue
        side = sig(k)
        if side:
            e = D.c[k]
            pos = dict(side=side, e=e, t=k, stop=e - side * cat, tp=e + side * tp, mfe=0.0, tr=False)
    return trades


def single(src, orients, Ks_level, Ks_roll, wins):
    out = []
    for o in orients:
        for K in Ks_level:
            out.append([(src, "level", 0, K, o)])
        for w, K in itertools.product(wins, Ks_roll):
            out.append([(src, "roll", w, K, o)])
    return out


KL, KR, WN = (50, 100, 150, 200, 300, 400, 600), (50, 100, 150, 200, 300), (15, 30, 60)
FAM = {}
FAM["1 콜-풋(역방향)"] = [(c, "all") for c in single("sp", (-1,), (100, 150, 200, 300, 400, 600, 800), (100, 150, 200, 300, 400), WN)]
FAM["2a 풋 증감(풋 증가=매수)"] = [(c, "all") for c in single("put", (+1,), KL, KR, WN)]
FAM["2b 풋 증감(풋 증가=매도)"] = [(c, "all") for c in single("put", (-1,), KL, KR, WN)]
FAM["참고 콜 증감(콜 증가=매도)"] = [(c, "all") for c in single("call", (-1,), KL, KR, WN)]
PUT = single("put", (+1,), KL, KR, WN)
SEC = {
    "외인선물 부호": ("fx", "level", 0, 0, +1), "외인선물 30분": ("fx", "roll", 30, 0, +1),
    "외인옵션 콜-풋 부호": ("fsp", "level", 0, 0, +1), "가격 09:00 대비": ("px", "level", 0, 0, +1), "가격 30분": ("px", "roll", 30, 0, +1),
}
for name, sec in SEC.items():
    FAM["3 풋 + %s(게이트)" % name] = [(c + [sec], "gate") for c in PUT]
FAM["3 풋 + 외인선물 문턱(동의)"] = [(c + [("fx", "level", 0, Kf, +1)], "all") for c in PUT for Kf in (200, 400, 800)]
SP = single("sp", (-1,), (100, 150, 200, 300, 400, 600, 800), (100, 150, 200, 300, 400), WN)
FAM["3b 콜-풋 + 외인선물 부호(게이트)"] = [(c + [SEC["외인선물 부호"]], "gate") for c in SP]
FAM["3b 콜-풋 + 가격 30분(게이트)"] = [(c + [SEC["가격 30분"]], "gate") for c in SP]
FAM["참고 외인선물 단독(순방향)"] = [(c, "all") for c in single("fx", (+1,), (200, 400, 800, 1200, 1600), (200, 400, 800), (30, 60))]

if __name__ == "__main__":
    data = {d: load(d) for d in DAYS}
    M = 1e4
    base_cfg = ([("sp", "level", 0, 300, -1)], "all")
    base = [sum(t["net"] for t in run(data[d], make_sig(data[d], *base_cfg))) for d in DAYS]
    print("v2.1 현행 재현:", [round(x / M, 1) for x in base], "합 %+.1f만" % (sum(base) / M))
    assert abs(sum(base) / M - 693.2) < 0.2, sum(base)      # 자기 검증 — 엔진 MAIN 7일 값
    res = {}
    for fam, cfgs in FAM.items():
        tab = []
        for comps, comb in cfgs:
            tr = [run(data[d], make_sig(data[d], comps, comb)) for d in DAYS]
            tab.append((comps, comb, [sum(t["net"] for t in x) for x in tr], [len(x) for x in tr],
                        [(x[0]["side"] if x else 0) for x in tr]))
        res[fam] = tab
    print("\n%-32s %4s %8s %7s %7s %6s %8s | 표본 안 최적 설정 · 일별(만원) · 거래 수" % ("방법(계열)", "조합", "표본안", "최악일", "중앙", "흑자%", "LODO"))
    summary = {}
    for fam, tab in res.items():
        sums = [sum(v) for _, _, v, _, _ in tab]
        bi = max(range(len(tab)), key=lambda i: sums[i])
        lodo, picks = [], []
        for j in range(len(DAYS)):
            pick = max(range(len(tab)), key=lambda i: sums[i] - tab[i][2][j])
            lodo.append(tab[pick][2][j]); picks.append(pick)
        comps, comb, v, n, fs = tab[bi]
        cfg = ["%s/%s%s/K%s/%+d" % (c[0], c[1], c[2] or "", c[3], c[4]) for c in comps]
        summary[fam] = dict(best=sums[bi] / M, worst=min(v) / M, lodo=sum(lodo) / M, lodo_worst=min(lodo) / M, med=st.median(sums) / M,
                            pos=sum(s > 0 for s in sums) / float(len(sums)), cfg=cfg, days=[x / M for x in v],
                            lodo_days=[x / M for x in lodo], n=n, n_cfg=len(tab), distinct_picks=len(set(picks)))
        print("%-32s %4d %+8.1f %+7.1f %+7.1f %5.0f%% %+8.1f | %s · %s · %s" % (
            fam, len(tab), sums[bi] / M, min(v) / M, st.median(sums) / M, 100 * summary[fam]["pos"], sum(lodo) / M,
            cfg, " ".join("%+.0f" % (x / M) for x in v), n))
    print("\nLODO 일별(만원)                   " + " ".join("%6s" % d[5:] for d in DAYS) + "      합   최악일  설정수")
    for fam, s in summary.items():
        print("%-32s %s  %+7.1f %+7.1f  %d" % (fam, " ".join("%+6.0f" % x for x in s["lodo_days"]), s["lodo"], s["lodo_worst"], s["distinct_picks"]))
    json.dump(summary, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "summary.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
