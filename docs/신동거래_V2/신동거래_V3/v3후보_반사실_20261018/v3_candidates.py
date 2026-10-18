# -*- coding: utf-8 -*-
"""v3 후보 규칙 · 섀도 후보 일괄 반사실. 읽기 전용(DB 쓰기 없음).

공통 청산: 재난 손절 0.6×ATR14 · 트레일 6/4 · 익절 12 · 15:05 · 하루 3회(엔진 규격 그대로).
신호원
  FLOWC  : 개인 콜−풋 09:00 대비 ±300 역추종(spec.FLOWC_K)
  R60    : 개인 콜−풋 최근 60분 변화 ±150 역추종(spec.FLOWR_*) — FLOWR60 과 같다
  LEAD   : CP·FX 중 최근 60분 가격 추종 상관이 높은 쪽의 60분 변화(lead_reentry_cf.Monitor, C_MIN 0.3)
라우팅
  first  : 첫 거래 = FLOWC, 2번째부터 = after 신호       (사용자 제안 「혼합 규칙」)
  clock  : 10:00 전 = FLOWC, 10:00 부터 = after 신호       (거래 순번 대신 시각으로 나눔)
  only   : 하루 전부 after 신호                          (FLOWR60 단독 등)
  flowc  : 하루 전부 FLOWC                               (현행 v2.2)
손절 뒤: halt(당일 중단) · same(손절 방향만 당일 금지) · cont(계속)
가드  : FLOWC 진입에 v2.2 R1 반대 재진입 금지(기록 그대로 = 10/15~ · 'all' = 전 기간)
"""
import os, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "추종지표재진입_반사실_20261017"))
sys.argv = [sys.argv[0]] + [a for a in sys.argv[1:]]
GUARD_MODE = "all" if "--guard-all" in sys.argv else "rec"
sys.argv = [sys.argv[0]]
import lead_reentry_cf as M
from strategy.shindong import families as F, spec as S, daily_report as DR


def run(d, L, bias, day, route, after, slp, guard_r60=False):
    fsig, _ = F._flow_signal(d, d.sp, S.FLOWC_K, -1)
    if fsig is None:
        return None
    asig = None
    if after == "R60":
        r = F._roll_signal(d.sp, S.FLOWR_WIN_MIN, S.FLOWR_K, -1)
        asig = lambda k: r(k)
    elif after == "LEAD":
        mon = M.Monitor(d, 60)
        asig = lambda k: mon(k)[0]
    g = GUARD_MODE == "all" or day >= M.V22_FROM
    cat = F._cat_stop_pts(L)
    trades, busy, halted, blocked, ctr_n = [], None, False, 0, 0
    for k in d.idx:
        if k < "09:00" or k not in d.c or (busy is not None and k <= busy):
            continue
        if halted or k > S.FLOW_LAST_ENTRY or len(trades) >= S.FLOW_MAX_TRADES:
            continue
        if route == "flowc":
            use = "FLOWC"
        elif route == "only":
            use = "AFT"
        elif route == "first":
            use = "FLOWC" if not trades else "AFT"
        else:
            use = "FLOWC" if k < "10:00" else "AFT"
        side = fsig(k) if use == "FLOWC" else asig(k)
        if not side or side == blocked:
            continue
        ctr = bool(bias) and side == -bias
        if ctr and ctr_n >= S.FLOW_R1_CTR_MAX and (g if use == "FLOWC" else (guard_r60 and g)):
            continue
        t = M.trade(d, side, k, cat, use)
        trades.append(t); busy = t["x"] or "99:99"
        if ctr:
            ctr_n += 1
        if t["why"] == "SL":
            if slp == "halt":
                halted = True
            elif slp == "same":
                blocked = side
    return trades


def summ(daily, trs):
    xs = list(daily.values())
    w = [t["net"] for t in trs if t["net"] > 0]; l = [t["net"] for t in trs if t["net"] <= 0]
    c = p = m = 0.0
    for x in xs:
        c += x; p = max(p, c); m = min(m, c - p)
    return dict(tot=sum(xs), n=len(trs), wr=len(w) / max(1, len(trs)), pf=(sum(w) / -sum(l)) if sum(l) < 0 else 99,
                worst=min(xs), mdd=m, sl=sum(t["why"] == "SL" for t in trs), pos=sum(x > 0 for x in xs))


if __name__ == "__main__":
    data, shadow = {}, collections.defaultdict(dict)
    for day in M.PRE + M.EVAL:
        o = DR.load_day(day, M.RAW_DATA_DB, M.FLOW, M.PREMARKET_LEVELS_DB)
        if not (o.get("ok") and o["d"].sp and o["d"].fx):
            continue
        data[day] = (o["d"], o["L"], F._r1_bias(o["d"])[1])
        for v in ("SHADOW_FLOWF", "SHADOW_BRKC", "SHADOW_V1", "SHADOW_V1X4"):
            shadow[v][day] = sum(sum(g.get("net") or 0 for g in t["legs"]) for t in o["results"][v]["trades"]
                                 if t["status"] == "CLOSED")
    C = [("현행 v2.2 (FLOWC·halt)", "flowc", None, "halt"),
         ("v2.2 + 손절방향금지", "flowc", None, "same"),
         ("FLOWR60 단독 (halt)", "only", "R60", "halt"),
         ("FLOWR60 단독 + same", "only", "R60", "same"),
         ("혼합 first·R60·halt", "first", "R60", "halt"),
         ("혼합 first·R60·same", "first", "R60", "same"),
         ("혼합 first·R60·cont", "first", "R60", "cont"),
         ("시각 clock·R60·halt", "clock", "R60", "halt"),
         ("시각 clock·R60·same", "clock", "R60", "same"),
         ("시각 clock·R60·cont", "clock", "R60", "cont"),
         ("혼합 first·LEAD·cont", "first", "LEAD", "cont"),
         ("혼합 first·LEAD·same", "first", "LEAD", "same"),
         ("LEAD 단독 (halt)", "only", "LEAD", "halt")]
    print("가드 %s | 평가 10일 · 사전 %d일(%s)" % (GUARD_MODE, len([x for x in M.PRE if x in data]), ",".join(x[5:] for x in M.PRE if x in data)))
    print("%-24s %8s %4s %5s %5s %7s %7s %3s %4s || %8s %7s || v2.1구간 v2.2구간" % ("규칙", "평가", "n", "승률", "PF", "최악일", "MDD", "SL", "흑자", "사전", "최악일"))
    daily_all = {}
    for name, route, after, slp in C:
        out = {}
        for part, days in (("E", M.EVAL), ("P", M.PRE)):
            dl, trs = {}, []
            for day in days:
                if day not in data:
                    continue
                t = run(*data[day], day, route, after, slp) or []
                dl[day] = sum(x["net"] for x in t); trs += t
            out[part] = (summ(dl, trs), dl)
        e, p = out["E"][0], out["P"][0]
        daily_all[name] = dict(out["E"][1], **out["P"][1])
        v21 = sum(v for k, v in out["E"][1].items() if k < M.V22_FROM); v22 = sum(v for k, v in out["E"][1].items() if k >= M.V22_FROM)
        print("%-24s %8.1f %4d %4.0f%% %5.2f %7.1f %7.1f %3d %4d || %8.1f %7.1f || %7.1f %7.1f" % (
            name, e["tot"] / 1e4, e["n"], e["wr"] * 100, e["pf"], e["worst"] / 1e4, e["mdd"] / 1e4, e["sl"], e["pos"],
            p["tot"] / 1e4, p["worst"] / 1e4, v21 / 1e4, v22 / 1e4))
    for v in shadow:
        e = [shadow[v][d] for d in M.EVAL if d in shadow[v]]; p = [shadow[v][d] for d in M.PRE if d in shadow[v]]
        print("%-24s %8.1f %4s %5s %5s %7.1f %7s %3s %4d || %8.1f %7.1f" % ("(섀도) " + v.replace("SHADOW_", ""), sum(e) / 1e4, "", "", "", min(e) / 1e4, "", "", sum(x > 0 for x in e), sum(p) / 1e4, min(p) / 1e4))
        daily_all["(섀도) " + v.replace("SHADOW_", "")] = shadow[v]
    names = list(daily_all)
    print("\n[일별(만)]")
    for i, n in enumerate(names):
        print("  %2d %s" % (i, n))
    print("  day   " + " ".join("%6d" % i for i in range(len(names))))
    for day in M.PRE + M.EVAL:
        if day in data:
            print("  %s " % day[5:] + " ".join("%6.0f" % (daily_all[n].get(day, float("nan")) / 1e4) for n in names))
    # 상관(평가 10일) — 섀도 다양성
    import math
    def corr(a, b):
        ma, mb = sum(a) / len(a), sum(b) / len(b)
        va = math.sqrt(sum((x - ma) ** 2 for x in a)); vb = math.sqrt(sum((y - mb) ** 2 for y in b))
        return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (va * vb) if va and vb else float("nan")
    base = "혼합 first·R60·cont"
    print("\n[%s 대비 일손익 상관 · 16일]" % base)
    days16 = [x for x in M.PRE + M.EVAL if x in data]
    for n in names:
        print("  %-24s %+.2f" % (n, corr([daily_all[base].get(x, 0) for x in days16], [daily_all[n].get(x, 0) for x in days16])))
