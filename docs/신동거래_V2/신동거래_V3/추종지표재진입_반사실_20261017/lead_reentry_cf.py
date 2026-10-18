# -*- coding: utf-8 -*-
"""MAIN(FLOWC) 「추종 지표 재진입」 개선안 반사실. 읽기 전용(DB 쓰기 없음).

제안(사용자 2026-10-17):
  최초 진입 뒤(손절 또는 관망 중) 시장 국면을 상시 감시한다 — 가격이 **개인 콜−풋**과 **외국인 선물** 중
  어느 쪽을 따라가는지 추적하고, 그 「주도 지표」로 방향을 정해 진입 시점이 오면 재진입한다.
  추적 기간은 30·60분 중 WFA 로 고른다. 재진입 뒤 청산·손절은 기존 규칙.

결과 보기 전 고정한 규격(사전 고정 — 결과를 보고 바꾸지 않는다)
  정렬 시계열  CP = −(콜−풋)(FLOWC 가 역추종이므로) · FX = +외국인 선물 순매수 누적
  추종 점수    최근 W 분(k−W ~ k, k−W ≥ 09:00) 가격 종가와 정렬 시계열의 피어슨 상관(수준). --diff 면 1분 변화 상관
  주도 지표    점수가 더 높은 쪽. 둘 다 C_MIN(0.3) 미만이면 주도 없음(관망)
  방향·시점    주도 지표의 W 분 변화 ≥ +K → 매수 / ≤ −K → 매도. 그 봉 종가 진입.
               K: CP 150(spec.FLOWR_K) · FX 400(= 150 × FLOWF_K/FLOWC_K ≈ 2.67, 구조값)
  감시 시작    mode "sl"  = 재난 손절 뒤에만(그 외 청산 뒤는 현행처럼 FLOWC 계속) — 당일 중단 대신 감시
               mode "any" = 첫 거래가 끝나면(사유 무관) 이후 진입은 전부 감시 신호로
  청산         현행 그대로(재난 손절 0.6×ATR14 · 트레일 6/4 · 익절 12 · 15:05). 하루 3회 상한 유지.
               감시 진입의 재난 손절도 그날 신규 진입을 멈추지 않는다(감시가 계속된다) — 3회 상한이 막는다.
  v2.2 가드    FLOWC 진입에만 기록 그대로(10/15~). 감시 진입은 새 규칙이라 가드 밖(--guard-all 이면 감시에도 적용).
  WFA          평가일 t 마다 t 이전 「두 지표가 모두 있는 날」 전부로 W∈{30,60} 의 **감시 단독 전략**
               (09:00+W 부터 감시 신호만으로 거래, 같은 청산·3회 상한·재난 손절 시 당일 중단) 순손익을 비교해 큰 쪽.

사용: py37_32 python lead_reentry_cf.py [--diff] [--guard-all] [--cmin 0.3]
"""
import os, sys, math, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
sys.path.insert(0, ROOT); os.chdir(ROOT)
from config.settings import PREMARKET_LEVELS_DB, RAW_DATA_DB, WEEKLY_OPTION_FLOW_DB
from strategy.shindong import daily_report as DR, families as F, spec as S, engine as E

FLOW = WEEKLY_OPTION_FLOW_DB if os.path.isabs(WEEKLY_OPTION_FLOW_DB) else os.path.join(ROOT, WEEKLY_OPTION_FLOW_DB)
PRE = ["2026-09-21", "2026-09-22", "2026-09-23", "2026-09-28", "2026-09-29", "2026-09-30"]
EVAL = ["2026-10-01", "2026-10-02", "2026-10-06", "2026-10-07", "2026-10-08", "2026-10-12", "2026-10-13",
        "2026-10-14", "2026-10-15", "2026-10-16"]
V22_FROM = "2026-10-15"
WINS = (30, 60)
K = {"CP": float(S.FLOWR_K), "FX": float(S.FLOWR_K) * S.FLOWF_K / S.FLOWC_K}
DIFF = "--diff" in sys.argv
GUARD_ALL = "--guard-all" in sys.argv
C_MIN = float(sys.argv[sys.argv.index("--cmin") + 1]) if "--cmin" in sys.argv else 0.3   # -9 = 상관 필터 끔
IND = tuple(sys.argv[sys.argv.index("--ind") + 1].split(",")) if "--ind" in sys.argv else ("CP", "FX")  # 분해용


def pearson(a, b):
    n = len(a)
    if n < 5:
        return None
    ma, mb = sum(a) / n, sum(b) / n
    va = sum((x - ma) ** 2 for x in a); vb = sum((y - mb) ** 2 for y in b)
    if va <= 0 or vb <= 0:
        return None
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / math.sqrt(va * vb)


class Monitor:
    """분 k 에서 (방향, 주도 지표, 점수들) — 미래 참조 없음(k 까지의 값만)."""

    def __init__(self, d, win):
        self.d, self.win = d, win
        self.keys = [k for k in d.idx if k >= S.FLOW_BASE and k in d.c]
        self.pos = {k: i for i, k in enumerate(self.keys)}
        self.ser = {"CP": {k: -d.sp[k] for k in self.keys if k in d.sp},
                    "FX": {k: d.fx[k] for k in self.keys if k in d.fx}}
        self.cache = {}

    def __call__(self, k):
        if k in self.cache:
            return self.cache[k]
        out = (0, None, {})
        i = self.pos.get(k)
        rk = E._plus_min(k, -self.win)
        if i is not None and rk >= S.FLOW_BASE:
            ks = [x for x in self.keys[:i + 1] if x >= rk]
            px = [self.d.c[x] for x in ks]
            sc = {}
            for nm, s in self.ser.items():
                if nm not in IND:
                    continue
                if not all(x in s for x in ks):
                    continue
                xs = [s[x] for x in ks]
                if DIFF:
                    sc[nm] = pearson([b - a for a, b in zip(px, px[1:])], [b - a for a, b in zip(xs, xs[1:])])
                else:
                    sc[nm] = pearson(px, xs)
            cand = [(v if v is not None else -2.0, nm) for nm, v in sc.items() if C_MIN <= -9 or (v is not None and v >= C_MIN)]
            if cand:
                _v, lead = max(cand)
                s = self.ser[lead]
                dv = s[k] - s[ks[0]]
                side = 1 if dv >= K[lead] else (-1 if dv <= -K[lead] else 0)
                out = (side, lead, sc)
            else:
                out = (0, None, sc)
        self.cache[k] = out
        return out


def trade(d, side, k, cat, src, lead=None):
    tr = F._run_position(d, side, k, d.c[k] - side * cat, S.FLOW_TRAIL, S.FLOW_TP)
    return dict(t=k, side=side, e=d.c[k], why=tr["legs"][0].get("reason"), pts=tr["legs"][0].get("pts") or 0,
                net=sum(g.get("net") or 0 for g in tr["legs"]), x=tr["exit_ts"], src=src, lead=lead)


def run_main(d, L, bias, guard, mode, win):
    """mode None = 현행 MAIN. "sl"/"any" = 추종 지표 재진입."""
    fsig, _ = F._flow_signal(d, d.sp, S.FLOWC_K, -1)
    if fsig is None:
        return None
    mon = Monitor(d, win) if mode else None
    cat = F._cat_stop_pts(L)
    trades, busy, halted, ctr_n, watching = [], None, False, 0, False
    for k in d.idx:
        if k < "09:00" or k not in d.c:
            continue
        if busy is not None and k <= busy:
            continue
        if halted or k > S.FLOW_LAST_ENTRY or len(trades) >= S.FLOW_MAX_TRADES:
            continue
        if watching:
            side, lead, _sc = mon(k)
            if not side:
                continue
            if GUARD_ALL and bias and side == -bias and ctr_n >= S.FLOW_R1_CTR_MAX:
                continue
            t = trade(d, side, k, cat, "MON", lead)
        else:
            side = fsig(k)
            if not side:
                continue
            if guard and bias and side == -bias and ctr_n >= S.FLOW_R1_CTR_MAX:
                continue
            t = trade(d, side, k, cat, "FLOWC")
        trades.append(t)
        busy = t["x"] or "99:99"
        if bias and t["side"] == -bias:
            ctr_n += 1
        if t["why"] == "SL":
            if mode is None:
                halted = S.FLOW_CAT_STOP_HALT_DAY
            else:
                watching = True
        elif mode == "any":
            watching = True
    return trades


def run_lead_only(d, L, win):
    """WFA 목적함수 — 감시 신호만으로 하루 거래(같은 청산 · 3회 · 재난 손절 시 당일 중단)."""
    mon = Monitor(d, win)
    cat = F._cat_stop_pts(L)
    trades, busy = [], None
    for k in d.idx:
        if k < "09:00" or k not in d.c or (busy is not None and k <= busy):
            continue
        if k > S.FLOW_LAST_ENTRY or len(trades) >= S.FLOW_MAX_TRADES:
            break
        side, lead, _ = mon(k)
        if not side:
            continue
        t = trade(d, side, k, cat, "MON", lead)
        trades.append(t)
        busy = t["x"] or "99:99"
        if t["why"] == "SL":
            break
    return trades


def stats(daily, trs):
    xs = list(daily.values())
    w = [t["net"] for t in trs if t["net"] > 0]; l = [t["net"] for t in trs if t["net"] <= 0]
    c = p = m = 0.0
    for x in xs:
        c += x; p = max(p, c); m = min(m, c - p)
    return "%8.1f만 n%2d 승률%3.0f%% 평균승%+6.1f 평균패%+7.1f PF%5.2f 최악일%7.1f MDD%7.1f SL%d" % (
        sum(xs) / 1e4, len(trs), 100 * len(w) / len(trs) if trs else 0, (sum(w) / len(w) if w else 0) / 1e4,
        (sum(l) / len(l) if l else 0) / 1e4, sum(w) / -sum(l) if sum(l) < 0 else float("inf"), min(xs) / 1e4,
        m / 1e4, sum(1 for t in trs if t["why"] == "SL"))


if __name__ == "__main__":
    data = {}
    for day in PRE + EVAL:
        o = DR.load_day(day, RAW_DATA_DB, FLOW, PREMARKET_LEVELS_DB)
        if not o.get("ok") or not o["d"].sp or not o["d"].fx:
            print("skip", day); continue
        _sp, bias = F._r1_bias(o["d"])
        data[day] = (o["d"], o["L"], bias)
    days = [x for x in PRE + EVAL if x in data]
    if IND == ("CP",) and C_MIN <= -9:
        mism = 0
        for day in days:
            o = DR.load_day(day, RAW_DATA_DB, FLOW, PREMARKET_LEVELS_DB)
            a = [(t["entry_ts"], round(sum(g["net"] for g in t["legs"]))) for t in o["results"]["SHADOW_FLOWR60"]["trades"]]
            b = [(t["t"], round(t["net"])) for t in run_lead_only(data[day][0], data[day][1], 60)]
            mism += a != b
        print("FLOWR60 섀도 대조(CP만 · 필터 끔 · W60 단독): 불일치 %d일" % mism)
    print("지표 %s · 규격: %s 상관 · C_MIN %.2f · K CP %.0f / FX %.0f · 가드 %s" % (
        "+".join(IND), "1분변화" if DIFF else "수준", C_MIN, K["CP"], K["FX"], "감시에도" if GUARD_ALL else "FLOWC만(기록 그대로)"))
    # 0) 주도 지표 분포 — 매분 점수
    print("\n[주도 지표 분포 — 09:00+W ~ 14:50 분 단위]  day  W=30: CP/FX/없음  |  W=60: CP/FX/없음")
    for day in days:
        d = data[day][0]
        row = []
        for w in WINS:
            m = Monitor(d, w)
            cnt = collections.Counter(m(k)[1] for k in m.keys if E._plus_min(k, -w) >= "09:00" and k <= "14:50")
            row.append("%3d/%3d/%3d" % (cnt["CP"], cnt["FX"], cnt[None]))
        print("  %s  %s  |  %s" % (day[5:], row[0], row[1]))
    # 1) 감시 단독 전략(WFA 목적함수) 일별
    lead_net = {w: {} for w in WINS}
    for w in WINS:
        for day in days:
            d, L, _b = data[day]
            lead_net[w][day] = sum(t["net"] for t in run_lead_only(d, L, w))
    print("\n[감시 단독 전략 일별(만)] day  W30  W60")
    for day in days:
        print("  %s %7.1f %7.1f" % (day[5:], lead_net[30][day] / 1e4, lead_net[60][day] / 1e4))
    # 2) WFA 로 평가일별 W 선택
    pick = {}
    for day in EVAL:
        tr = [x for x in days if x < day]
        sc = {w: sum(lead_net[w][x] for x in tr) for w in WINS}
        pick[day] = max(WINS, key=lambda w: (sc[w], -w))
        print("  WFA %s 학습 %d일: W30 %+7.1f  W60 %+7.1f → W%d" % (day[5:], len(tr), sc[30] / 1e4, sc[60] / 1e4, pick[day]))
    # 3) MAIN + 추종 지표 재진입
    cfgs = [("현행 MAIN", None, None)]
    for mode in ("sl", "any"):
        for w in ("WFA", 30, 60):
            cfgs.append(("재진입 %s · W%s" % ({"sl": "손절 뒤", "any": "첫 거래 뒤"}[mode], w), mode, w))
    res = {}
    for name, mode, w in cfgs:
        for part, ds in (("평가", EVAL), ("사전", PRE)):
            daily, trs = {}, []
            for day in ds:
                if day not in data:
                    continue
                d, L, bias = data[day]
                ww = (pick.get(day, 60) if w == "WFA" else w) or 30
                t = run_main(d, L, bias, day >= V22_FROM, mode, ww) or []
                daily[day] = sum(x["net"] for x in t)
                trs += [dict(x, day=day) for x in t]
            res[(name, part)] = (daily, trs)
    print("\n[결과] 평가 10일  ||  사전 6일(9/21~9/30, WFA 선택값 없음 → W60 고정)")
    for name, mode, w in cfgs:
        dl, trs = res[(name, "평가")]
        mon = [t["net"] for t in trs if t["src"] == "MON"]
        dp, tp = res[(name, "사전")]
        print("  %-22s %s | 감시진입 %2d건 %+7.1f만 || 사전 %7.1f만 최악일 %6.1f" % (
            name, stats(dl, trs), len(mon), sum(mon) / 1e4, sum(dp.values()) / 1e4, min(dp.values()) / 1e4))
    print("\n[일별(만)] " + " | ".join(n for n, _m, _w in cfgs))
    for day in EVAL:
        print("  %s %+d " % (day[5:], data[day][2]) + " ".join("%7.1f" % (res[(n, "평가")][0][day] / 1e4) for n, _m, _w in cfgs))
    for name, mode, w in cfgs[1:]:
        print("\n[감시 진입 내역] " + name)
        for t in res[(name, "평가")][1]:
            if t["src"] == "MON":
                print("   %s %s→%s %+d 주도=%s %-4s %+6.2fpt %+7.1f만" % (t["day"][5:], t["t"], t["x"], t["side"], t["lead"],
                                                                   t["why"], t["pts"], t["net"] / 1e4))
