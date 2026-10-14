# -*- coding: utf-8 -*-
"""MAIN(FLOWC) R1 역방향 패턴 손실 방어 반사실 + 보완 변형 일별 대조. 읽기 전용(DB 쓰기 없음).

패턴(10/07 · 10/14): R1(장전 콜−풋) 방향과 **반대**로 FLOWC 신호 → 첫 거래 이익 → 청산 직후
같은 방향 재진입 → MFE 2pt 안팎 → 재난 손절(≈17pt).

규칙 변형은 공식 엔진 함수(`families._run_position` · `_cat_stop_pts` · `_flow_signal`)로 돌린다.
청산·트레일·익절·재난손절·당일중단은 현행 그대로이고, **진입 허용 조건과 손절 폭만** 바꾼다.
손익은 엔진 규격(2계약 · CYBOS 요율 · 1틱)이다.

사용: conda run -n py37_32 python r1_guard_cf.py
"""
import os, sys, datetime as dt, statistics as st, collections, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, ROOT); os.chdir(ROOT)
from config.settings import PREMARKET_LEVELS_DB, RAW_DATA_DB, WEEKLY_OPTION_FLOW_DB
from strategy.shindong import daily_report as DR, families as F, spec as S, engine as E

FLOW = WEEKLY_OPTION_FLOW_DB if os.path.isabs(WEEKLY_OPTION_FLOW_DB) else os.path.join(ROOT, WEEKLY_OPTION_FLOW_DB)
DAYS = ["2026-09-21", "2026-09-22", "2026-09-23", "2026-09-24", "2026-09-25", "2026-09-29", "2026-09-30",
        "2026-10-01", "2026-10-02", "2026-10-06", "2026-10-07", "2026-10-08", "2026-10-12", "2026-10-13",
        "2026-10-14"]


def run_rule(d, L, bias, mode=None, ctr_stop_atr=None, cat_atr=None):
    """mode:
       None          현행
       'block_all'   R1 반대 방향 진입 전부 금지
       'block_re'    R1 반대 방향은 그날 **첫 1건만** 허용(그 뒤 같은 쪽 재진입 금지)
       'halt_ctr'    R1 반대 거래가 한 번이라도 끝나면(승패 무관) 그날 신규 진입 전면 중단
     ctr_stop_atr: R1 반대 방향 거래만 손절 폭을 이 ATR 배수로(None=현행)
     cat_atr: 전 거래 재난 손절 폭(None=현행 0.6)"""
    sig, _why = F._flow_signal(d, d.sp, S.FLOWC_K, -1)
    if sig is None:
        return None
    atr = L["0850"].get("atr14")
    base_cat = F._cat_stop_pts(L)
    trades, busy, halted, ctr_n = [], None, False, 0
    for k in d.idx:
        if k < "09:00" or k not in d.c:
            continue
        if busy is not None and k <= busy:
            sig(k); continue
        if halted or k > S.FLOW_LAST_ENTRY or len(trades) >= S.FLOW_MAX_TRADES:
            sig(k); continue
        side = sig(k)
        if not side:
            continue
        ctr = bool(bias) and side == -bias
        if ctr and mode == "block_all":
            continue
        if ctr and mode == "block_re" and ctr_n >= 1:
            continue
        cat = base_cat if cat_atr is None else cat_atr * atr
        if ctr and ctr_stop_atr is not None:
            cat = ctr_stop_atr * atr
        e = d.c[k]
        tr = F._run_position(d, side, k, e - side * cat, S.FLOW_TRAIL, S.FLOW_TP)
        net = sum(g.get("net") or 0 for g in tr["legs"])
        why = tr["legs"][0].get("reason")
        trades.append(dict(t=k, side=side, ctr=ctr, e=e, why=why, pts=tr["legs"][0].get("pts") or 0, net=net,
                           x=tr["exit_ts"]))
        busy = tr["exit_ts"] or "99:99"
        if ctr:
            ctr_n += 1
        if why == "SL" and S.FLOW_CAT_STOP_HALT_DAY:
            halted = True
        if ctr and mode == "halt_ctr":
            halted = True
    return trades


RULES = [("현행(BASE)", dict()),
         ("R1반대 전면금지", dict(mode="block_all")),
         ("R1반대 첫1건만", dict(mode="block_re")),
         ("R1반대 1건 뒤 당일중단", dict(mode="halt_ctr")),
         ("R1반대 손절 0.3ATR", dict(ctr_stop_atr=0.3)),
         ("R1반대 손절 0.4ATR", dict(ctr_stop_atr=0.4)),
         ("R1반대 첫1건만+손절0.4", dict(mode="block_re", ctr_stop_atr=0.4)),
         ("전체 손절 0.5ATR(참고)", dict(cat_atr=0.5)),
         ("R1반대 첫1건만+전체0.5", dict(mode="block_re", cat_atr=0.5))]

SHADOWS = ["SHADOW_BRKC", "SHADOW_FLOWR60", "SHADOW_FLOWF", "SHADOW_V1X4", "SHADOW_V1"]


def mdd(xs):
    c = p = m = 0.0
    for x in xs:
        c += x; p = max(p, c); m = min(m, c - p)
    return m


def corr(a, b):
    ma, mb = st.mean(a), st.mean(b)
    va = math.sqrt(sum((x - ma) ** 2 for x in a)); vb = math.sqrt(sum((y - mb) ** 2 for y in b))
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (va * vb) if va and vb else float("nan")


if __name__ == "__main__":
    days, bias_of, rule_daily, rule_tr, sh_daily, main_tr = [], {}, collections.defaultdict(dict), collections.defaultdict(list), collections.defaultdict(dict), {}
    for day in DAYS:
        o = DR.load_day(day, RAW_DATA_DB, FLOW, PREMARKET_LEVELS_DB)
        if not o.get("ok"):
            print("skip", day, o.get("why")); continue
        d, L = o["d"], o["L"]
        _sp, bias = F._r1_bias(d)
        base = run_rule(d, L, bias)
        if base is None:
            print("skip", day, "no flow"); continue
        days.append(day); bias_of[day] = bias
        for name, kw in RULES:
            t = run_rule(d, L, bias, **kw)
            rule_daily[name][day] = sum(x["net"] for x in t)
            rule_tr[name] += [dict(x, day=day) for x in t]
        main_tr[day] = base
        for v in SHADOWS:
            r = o["results"].get(v)
            sh_daily[v][day] = sum(sum(g.get("net") or 0 for g in t["legs"]) for t in (r or {}).get("trades", []))
    # 공식 MAIN 재현 대조
    print("days", len(days), days[0], "~", days[-1])
    print("\n[MAIN 거래 — R1 반대(ctr) 표시]")
    for day in days:
        print(" ", day, "bias", bias_of[day], [(x["t"], x["side"], "CTR" if x["ctr"] else "", x["why"], round(x["pts"], 1), round(x["net"] / 1e4, 1)) for x in main_tr[day]])
    ctr = [x for x in rule_tr["현행(BASE)"] if x["ctr"]]
    ali = [x for x in rule_tr["현행(BASE)"] if not x["ctr"]]
    print("\nR1 반대 거래 n=%d 합 %.1f만 (승 %d) / R1 일치·보류 n=%d 합 %.1f만 (승 %d)" % (
        len(ctr), sum(x["net"] for x in ctr) / 1e4, sum(x["net"] > 0 for x in ctr),
        len(ali), sum(x["net"] for x in ali) / 1e4, sum(x["net"] > 0 for x in ali)))
    print("\n[규칙 변형] 총손익 · IS(9/21~9/30) · OOS(10/01~) · 최악일 · MDD · 재난손절 · 거래")
    for name, _ in RULES:
        xs = [rule_daily[name][d] for d in days]
        is_ = sum(rule_daily[name][d] for d in days if d < "2026-10-01")
        oos = sum(rule_daily[name][d] for d in days if d >= "2026-10-01")
        sl = sum(1 for x in rule_tr[name] if x["why"] == "SL")
        print("  %-24s %7.1f만  IS %7.1f  OOS %7.1f  최악일 %7.1f  MDD %7.1f  SL %d  n %d" % (
            name, sum(xs) / 1e4, is_ / 1e4, oos / 1e4, min(xs) / 1e4, mdd(xs) / 1e4, sl, len(rule_tr[name])))
    # 패턴일 정의: MAIN 의 R1 반대 거래가 SL 로 끝난 날
    pat = sorted(set(x["day"] for x in rule_tr["현행(BASE)"] if x["ctr"] and x["why"] == "SL"))
    lossd = [d for d in days if rule_daily["현행(BASE)"][d] < 0]
    print("\n패턴일:", pat, "| MAIN 손실일:", lossd)
    m = [rule_daily["현행(BASE)"][d] for d in days]
    print("\n[보완 변형] 총손익 · 최악일 · MAIN상관 · 패턴일 합 · MAIN손실일 합 · MAIN+변형 최악일 · MAIN+변형 MDD")
    for v in SHADOWS:
        xs = [sh_daily[v][d] for d in days]
        comb = [a + b for a, b in zip(m, xs)]
        print("  %-15s %7.1f만  최악일 %7.1f  상관 %+.2f  패턴일 %+7.1f  손실일 %+7.1f  합산최악 %7.1f  합산MDD %7.1f" % (
            v, sum(xs) / 1e4, min(xs) / 1e4, corr(m, xs), sum(sh_daily[v][d] for d in pat) / 1e4,
            sum(sh_daily[v][d] for d in lossd) / 1e4, min(comb) / 1e4, mdd(comb) / 1e4))
    print("  MAIN 단독       %7.1f만  최악일 %7.1f  MDD %7.1f" % (sum(m) / 1e4, min(m) / 1e4, mdd(m) / 1e4))
    print("\n[일별] day bias MAIN " + " ".join(v.replace("SHADOW_", "") for v in SHADOWS))
    for d in days:
        print("  %s %+d %7.1f " % (d, bias_of[d], rule_daily["현행(BASE)"][d] / 1e4) + " ".join("%7.1f" % (sh_daily[v][d] / 1e4) for v in SHADOWS))
