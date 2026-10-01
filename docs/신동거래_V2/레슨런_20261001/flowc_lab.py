# -*- coding: utf-8 -*-
"""FLOWC 방어 변형 실험 — 7일(9/21~10/1). 저장소 루트에서 실행. 읽기 전용(그날 하루씩만 읽는다).
변형: 재난 손절 폭(ATR 배수) · 당일 중단 방식(all/same/none) · 흐름 반전 청산(flip_exit).
기본값(cat 0.6 · halt all · flip off)은 `strategy/shindong/families.py` MAIN 과 같아야 한다(자기 검증)."""
import os, sys, datetime as dt
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, ROOT)
from strategy.shindong import engine as E, runner, spec as S, families
from strategy.shindong.calendar import select_flow_product
from config.settings import RAW_DATA_DB, PREMARKET_LEVELS_DB, WEEKLY_OPTION_FLOW_DB
DAYS = ["2026-09-21", "2026-09-22", "2026-09-23", "2026-09-28", "2026-09-29", "2026-09-30", "2026-10-01"]


def load(day):
    prod, _, _ = select_flow_product(dt.date.fromisoformat(day))
    c, f, lv = runner.load_inputs(day, prod, RAW_DATA_DB, WEEKLY_OPTION_FLOW_DB, PREMARKET_LEVELS_DB)
    return E.DayFrame(c, f), E.prepare_levels(lv)


def lab(D, L, cat_atr=0.6, halt="all", flip_exit=False, trail=(6.0, 4.0), tp=12.0, K=300, mt=3, be_at=None):
    """be_at: 유리하게 이만큼 가면 손절을 본전으로(트레일 발동 전 보호). None=없음."""
    base_k = "09:00" if "09:00" in D.sp else next((k for k in sorted(D.sp) if k > "09:00"), None)
    if base_k is None:
        return []
    base = D.sp[base_k]
    atr = L["0850"].get("atr14") or (20.0 / 0.6)
    cat = cat_atr * atr

    def sig(k):
        v = D.sp.get(k)
        if v is None or k < base_k:
            return 0
        dv = v - base
        return -1 if dv >= K else (1 if dv <= -K else 0)
    trades, pos, block, halted = [], None, 0, False
    ks = [k for k in D.idx if "09:00" <= k <= S.TIME_EXIT and k in D.c]
    for k in ks:
        if pos is not None:
            side, e = pos["side"], pos["e"]
            h, l = D.h[k], D.l[k]
            st = pos["stop"]
            x = why = None
            if (l <= st) if side > 0 else (h >= st):
                x, why, mkt = st, ("TR" if pos["tr"] else ("BE" if pos["be"] else "SL")), True
            elif (h >= pos["tp"]) if side > 0 else (l <= pos["tp"]):
                x, why, mkt = pos["tp"], "TP", False
            elif flip_exit and sig(k) == -side:
                x, why, mkt = D.c[k], "FLIP", True
            elif k >= S.TIME_EXIT:
                x, why, mkt = D.c[k], "TIME", True
            if x is not None:
                trades.append(dict(side=side, et=pos["t"], e=e, xt=k, x=x, why=why, net=2 * E.leg_net(side, e, x, mkt)[1]))
                if why == "SL":
                    if halt == "all":
                        halted = True
                    elif halt == "same":
                        block = side
                pos = None
                continue
            fav = (h - e) if side > 0 else (e - l)
            pos["mfe"] = max(pos["mfe"], fav)
            if be_at is not None and pos["mfe"] >= be_at and side * (e - pos["stop"]) > 0 and not pos["tr"]:
                pos["stop"], pos["be"] = e, True
            if pos["mfe"] >= trail[0]:
                ns = (e + side * pos["mfe"]) - side * trail[1]
                if side * (ns - pos["stop"]) > 0:
                    pos["stop"], pos["tr"] = ns, True
            continue
        if halted or k > S.FLOW_LAST_ENTRY or len(trades) >= mt:
            continue
        side = sig(k)
        if side and side != block:
            e = D.c[k]
            pos = dict(side=side, e=e, t=k, stop=e - side * cat, tp=e + side * tp, mfe=0.0, tr=False, be=False)
    return trades


VARS = [
    ("v2.1 현행 (0.6ATR · 전면 중단)", dict()),
    ("v2.0 손절 없음", dict(cat_atr=99.0)),
    ("A 동방향만 중단", dict(halt="same")),
    ("B 중단 없음", dict(halt="none")),
    ("C 흐름 반전 청산", dict(flip_exit=True)),
    ("D 반전 청산 + 동방향만 중단", dict(flip_exit=True, halt="same")),
    ("E 0.4ATR · 동방향만 중단", dict(cat_atr=0.4, halt="same")),
    ("F 0.3ATR · 동방향만 중단", dict(cat_atr=0.3, halt="same")),
    ("G 0.3ATR · 전면 중단", dict(cat_atr=0.3)),
    ("H 본전 이동(+5pt) ", dict(be_at=5.0)),
    ("I 본전(+5) + 반전 청산 + 동방향 중단", dict(be_at=5.0, flip_exit=True, halt="same")),
    ("J 트레일 5/4", dict(trail=(5.0, 4.0))),
]
if __name__ == "__main__":
    data = {d: load(d) for d in DAYS}
    # 자기 검증: 기본값 == 엔진 MAIN
    for d, (D, L) in data.items():
        v1 = E.run_day(D, L, "SHADOW_V1")
        eng = sum(E.trade_net(t) for t in families.run_family_day(D, L, "flowc", v1_decision=v1["decision"])["trades"] if t["status"] == "CLOSED")
        mine = sum(t["net"] for t in lab(D, L))
        assert abs(eng - mine) < 1, (d, eng, mine)
    print("%-36s" % "변형" + "".join("%8s" % d[5:] for d in DAYS) + "%9s %8s %6s" % ("7일 합", "최악일", "흑자일"))
    for name, kw in VARS:
        v = [sum(t["net"] for t in lab(*data[d], **kw)) / 1e4 for d in DAYS]
        print("%-36s" % name + "".join("%+8.1f" % x for x in v) + "%+9.1f %+8.1f %4d/7" % (sum(v), min(v), sum(x > 0 for x in v)))
    print("\n10/1 거래(변형 D):", [(t["et"], t["side"], t["xt"], t["why"], round(t["net"] / 1e4, 1)) for t in lab(*data["2026-10-01"], flip_exit=True, halt="same")])
    print("9/29 거래(변형 D):", [(t["et"], t["side"], t["xt"], t["why"], round(t["net"] / 1e4, 1)) for t in lab(*data["2026-09-29"], flip_exit=True, halt="same")])
