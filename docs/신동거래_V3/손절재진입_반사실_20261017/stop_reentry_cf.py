# -*- coding: utf-8 -*-
"""MAIN(FLOWC) 손절 정책 개선안 반사실 — 손절 폭 × 손절 뒤 재진입 규칙. 읽기 전용(DB 쓰기 없음).

현행: 재난 손절 = 진입가 ∓ 0.6×ATR14 · 손절 발동 시 당일 신규 진입 중단.
개선안(사용자 제안 2026-10-17):
  ① 손절 폭 = 고정 pt(3pt 등) 또는 시뮬 최적 손익비
  ② 손절 뒤 최초 진입 조건이 다시 오면 재진입(당일 중단 해제)
  ③ 재진입 시점 후보 — 아래 REENTRY 참조

공식 엔진 함수(`families._run_position` · `_flow_signal` · `_r1_bias` · `_cat_stop_pts`)로 돌린다.
청산(트레일 6/4 · 익절 12pt · 15:05 시간 청산)·손익 규격(2계약 · CYBOS 요율 · 1틱)은 현행 그대로다.
진입은 신호 봉 **종가**, 청산 검사는 다음 봉부터(엔진과 같다 — 미래 참조 없음).
v2.2 R1 반대 재진입 금지는 「기록 그대로」(10/15~ 켬)가 기본이고 --guard all/off 로 바꿀 수 있다.

사용: conda run -n py37_32 python stop_reentry_cf.py
"""
import os, sys, collections, itertools
ROOT = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(ROOT, "strategy")):   # 폴더를 옮겨도 깨지지 않게 위로 찾는다
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, ROOT); os.chdir(ROOT)
from config.settings import PREMARKET_LEVELS_DB, RAW_DATA_DB, WEEKLY_OPTION_FLOW_DB
from strategy.shindong import daily_report as DR, families as F, spec as S, engine as E

FLOW = WEEKLY_OPTION_FLOW_DB if os.path.isabs(WEEKLY_OPTION_FLOW_DB) else os.path.join(ROOT, WEEKLY_OPTION_FLOW_DB)
EVAL = ["2026-10-01", "2026-10-02", "2026-10-06", "2026-10-07", "2026-10-08", "2026-10-12", "2026-10-13",
        "2026-10-14", "2026-10-15", "2026-10-16"]
HOLD = ["2026-09-21", "2026-09-22", "2026-09-23", "2026-09-24", "2026-09-25", "2026-09-29", "2026-09-30"]
V22_FROM = "2026-10-15"

# 재진입 규칙(손절 SL 뒤에만 적용. 트레일·익절 청산 뒤는 현행처럼 신호가 켜져 있으면 바로 진입)
#   halt     현행 — 손절 뒤 당일 신규 진입 중단
#   same     손절 난 방향만 당일 금지 — 반대 방향 신호는 진입(엔진 halt_mode="same" 과 같은 규칙)
#   sig      신호가 아직 켜져 있으면 다음 봉 즉시 재진입
#   rearm    되돌림 뒤 재도래 — 신호가 한 번 꺼졌다가(0 또는 반대) 같은 방향으로 다시 켜지면
#   stoplvl  손절 지점 복귀 — 같은 방향 신호 + 종가가 손절가 안쪽으로 되돌아오면
#   half     중간 지점 복귀 — 같은 방향 신호 + 종가가 손절가와 직전 진입가의 중간까지 되돌아오면
#   entrylvl 최초 진입 지점 복귀 — 같은 방향 신호 + 종가가 직전 진입가 이상 유리해지면
#   cool10   10분 대기 — 같은 방향 신호 + 손절 뒤 10분 경과
REENTRY = ["halt", "same", "sig", "rearm", "stoplvl", "half", "entrylvl", "cool10"]
STOPS = [("0.6ATR(현행)", ("atr", 0.6)), ("0.4ATR", ("atr", 0.4)), ("0.3ATR", ("atr", 0.3)),
         ("0.2ATR", ("atr", 0.2)), ("0.1ATR", ("atr", 0.1))] + \
        [("%gpt" % p, ("pt", p)) for p in (2, 3, 4, 5, 6, 8, 10, 12, 15)]
CAPS = [3, 6]


def stop_pts(L, spec):
    kind, v = spec
    if kind == "pt":
        return v
    atr = L["0850"].get("atr14")
    return v * atr if isinstance(atr, (int, float)) and atr > 0 else S.FLOW_CAT_STOP_FALLBACK_PT


def run(d, L, bias, guard, spec, reentry, cap):
    sig, _ = F._flow_signal(d, d.sp, S.FLOWC_K, -1)
    if sig is None:
        return None
    s = stop_pts(L, spec)
    trades, busy, halted, ctr_n = [], None, False, 0
    pend = None          # 손절 뒤 대기 조건: dict(side, stop, entry, t, off, ext)
    for k in d.idx:
        if k < "09:00" or k not in d.c:
            continue
        side = sig(k)
        c = d.c[k]
        if pend is not None and busy is not None and k > busy:
            if side != pend["side"]:
                pend["off"] = True
        if busy is not None and k <= busy:
            continue
        if halted or k > S.FLOW_LAST_ENTRY or len(trades) >= cap:
            continue
        if not side:
            continue
        ctr = bool(bias) and guard and side == -bias
        if ctr and ctr_n >= S.FLOW_R1_CTR_MAX:
            continue
        if pend is not None and side == pend["side"]:
            if reentry == "same":
                continue
            p = pend
            ok = {"sig": True,
                  "rearm": p["off"],
                  "stoplvl": side * (c - p["stop"]) > 0,          # 손절가 안쪽으로 되돌아옴(매도면 손절가 아래)
                  "half": side * (c - (p["stop"] + p["entry"]) / 2) >= 0,   # 손절가–진입가 중간 지점 복귀
                  "entrylvl": side * (c - p["entry"]) >= 0,       # 직전 진입가 이상 유리(매도면 진입가 이하)
                  "cool10": k >= E._plus_min(p["t"], 10)}[reentry]
            if not ok:
                continue
        tr = F._run_position(d, side, k, c - side * s, S.FLOW_TRAIL, S.FLOW_TP)
        net = sum(g.get("net") or 0 for g in tr["legs"])
        why = tr["legs"][0].get("reason")
        trades.append(dict(t=k, side=side, e=c, why=why, pts=tr["legs"][0].get("pts") or 0, net=net,
                           x=tr["exit_ts"], re=pend is not None and side == pend["side"]))
        busy = tr["exit_ts"] or "99:99"
        if bool(bias) and side == -bias:
            ctr_n += 1
        if pend is not None and not pend.get("keep") and side == pend["side"]:
            pend = None                     # 대기 조건은 그 방향 재진입으로만 소진(반대 방향 거래로는 안 지워진다)
        if why == "SL":
            if reentry == "halt":
                halted = True
            elif reentry == "same":
                pend = dict(side=side, stop=None, entry=c, t=tr["exit_ts"], off=False, ext=None, keep=True)
            else:
                pend = dict(side=side, stop=c - side * s, entry=c, t=tr["exit_ts"], off=False, ext=None)
    return trades


def stats(daily, trs):
    xs = list(daily.values())
    w = [t["net"] for t in trs if t["net"] > 0]
    l = [t["net"] for t in trs if t["net"] <= 0]
    pf = sum(w) / -sum(l) if l and sum(l) < 0 else float("inf")
    c = p = m = 0.0
    for x in xs:
        c += x; p = max(p, c); m = min(m, c - p)
    return dict(tot=sum(xs), n=len(trs), wr=len(w) / len(trs) if trs else 0, aw=sum(w) / len(w) if w else 0,
                al=sum(l) / len(l) if l else 0, pf=pf, worst=min(xs) if xs else 0, mdd=m,
                sl=sum(1 for t in trs if t["why"] == "SL"), re=sum(1 for t in trs if t["re"]),
                pos=sum(1 for x in xs if x > 0))


def load(days):
    out = {}
    for day in days:
        o = DR.load_day(day, RAW_DATA_DB, FLOW, PREMARKET_LEVELS_DB)
        if not o.get("ok"):
            print("skip", day, o.get("why")); continue
        _sp, bias = F._r1_bias(o["d"])
        out[day] = (o["d"], o["L"], bias, o["L"]["0850"].get("atr14"))
    return out


def sweep(data, guard_mode):
    res = {}
    for (sn, spec), rm, cap in itertools.product(STOPS, REENTRY, CAPS):
        daily, trs = {}, []
        for day, (d, L, bias, _atr) in data.items():
            g = {"rec": day >= V22_FROM, "all": True, "off": False}[guard_mode]
            t = run(d, L, bias, g, spec, rm, cap)
            if t is None:
                continue
            daily[day] = sum(x["net"] for x in t)
            trs += [dict(x, day=day) for x in t]
        res[(sn, rm, cap)] = (stats(daily, trs), daily, trs)
    return res


def fmt(st):
    return "%8.1f만 n%3d 승률%3.0f%% 평균승%+6.1f 평균패%+6.1f PF%5.2f 최악일%7.1f MDD%7.1f SL%2d 재진입%2d 흑자일%d" % (
        st["tot"] / 1e4, st["n"], st["wr"] * 100, st["aw"] / 1e4, st["al"] / 1e4, st["pf"], st["worst"] / 1e4,
        st["mdd"] / 1e4, st["sl"], st["re"], st["pos"])


def mae_profile(data):
    """현행 MAIN 진입(0.6ATR · 당일중단 · 3회)마다 청산 전 최대 역행(MAE)·최대 순행(MFE) — 손절 폭 선택의 근거."""
    rows = []
    for day, (d, L, bias, _atr) in data.items():
        t = run(d, L, bias, day >= V22_FROM, ("atr", 0.6), "halt", 3) or []
        for x in t:
            span = [k for k in d.idx if x["t"] < k <= (x["x"] or S.TIME_EXIT) and k in d.h]
            mae = max([x["side"] * (x["e"] - (d.l[k] if x["side"] > 0 else d.h[k])) for k in span] or [0])
            rows.append((day, x["t"], x["why"], x["net"], mae))
    return rows


if __name__ == "__main__":
    guard = sys.argv[sys.argv.index("--guard") + 1] if "--guard" in sys.argv else "rec"
    ev, ho = load(EVAL), load(HOLD)
    print("평가 %d일 · 보류(9/21~9/30) %d일 · 가드 %s" % (len(ev), len(ho), guard))
    print("ATR14:", {k[5:]: round(v[3], 1) for k, v in ev.items()})
    # 엔진 대조: same 모드 = families.flowc_counterfactual(halt_mode="same") (가드 끔 · 0.6ATR · 3회)
    mism = 0
    for day, (d, L, bias, _a) in ev.items():
        a = [(t["entry_ts"], round(sum(g["net"] for g in t["legs"]))) for t in F.flowc_counterfactual(d, L, 0.6, "same")]
        b = [(t["t"], round(t["net"])) for t in run(d, L, bias, False, ("atr", 0.6), "same", 3)]
        mism += a != b
    print("엔진 대조(same 모드 · 가드 끔): 불일치 %d일" % mism)
    mp = mae_profile(ev)
    print("\n[현행 진입의 MAE(pt) — 이긴 거래 / 진 거래]")
    for lab, f in (("이긴 거래", lambda r: r[3] > 0), ("진 거래", lambda r: r[3] <= 0)):
        xs = sorted(r[4] for r in mp if f(r))
        print("  %-6s n%2d  MAE " % (lab, len(xs)) + " ".join("%.1f" % v for v in xs))
        for th in (2, 3, 4, 5, 8, 12):
            print("     MAE ≥ %2dpt: %d/%d" % (th, sum(v >= th for v in xs), len(xs)))
    R = sweep(ev, guard)
    H = sweep(ho, guard)
    base = R[("0.6ATR(현행)", "halt", 3)]
    print("\n[기준선 재현] 0.6ATR · 당일중단 · 3회:", fmt(base[0]))
    print("  일별:", {k[5:]: round(v / 1e4, 1) for k, v in base[1].items()})
    for cap in CAPS:
        print("\n[손절 폭 × 재진입 — 총손익(만) · 상한 %d회]" % cap)
        print("  %-12s" % "손절" + "".join("%10s" % r for r in REENTRY))
        for sn, _ in STOPS:
            row = []
            for rm in REENTRY:
                key = (sn, rm, cap)
                row.append("%10.1f" % (R[key][0]["tot"] / 1e4))
            print("  %-12s" % sn + "".join(row))
    print("\n[상위 15 — 10일 총손익순 · 9/21~9/30 보류 구간 병기]")
    top = sorted(R.items(), key=lambda kv: -kv[1][0]["tot"])[:15]
    for key, (st, _dl, _t) in top:
        print("  %-12s %-8s cap%d  %s | 보류 %7.1f만 최악일 %6.1f" % (key + (fmt(st),) + (H[key][0]["tot"] / 1e4, H[key][0]["worst"] / 1e4)))
    print("\n[사용자 제안 핵심: 3pt × 재진입 규칙]")
    for rm in REENTRY:
        for cap in CAPS:
            key = ("3pt", rm, cap)
            if key in R:
                print("  3pt %-8s cap%d  %s | 보류 %7.1f만" % (rm, cap, fmt(R[key][0]), H[key][0]["tot"] / 1e4))
    sel = [("0.6ATR(현행)", "halt", 3)] + [k for k, _ in top[:3]] + [("3pt", "rearm", 6), ("3pt", "sig", 6)]
    seen = []
    for k in sel:
        if k in R and k not in seen:
            seen.append(k)
    print("\n[일별 비교(만)] " + " | ".join("%s/%s/%d" % k for k in seen))
    for day in ev:
        print("  %s bias%+d " % (day[5:], ev[day][2]) + " ".join("%8.1f" % (R[k][1].get(day, 0) / 1e4) for k in seen))
    for k in seen[1:]:
        print("\n[거래 내역] %s/%s/%d" % k)
        for t in R[k][2]:
            print("   %s %s %s %+d %-4s %+6.2fpt %+7.1f만 %s" % (t["day"][5:], t["t"], t["x"], t["side"], t["why"], t["pts"],
                                                          t["net"] / 1e4, "재진입" if t["re"] else ""))
