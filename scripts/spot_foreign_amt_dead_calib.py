# -*- coding: utf-8 -*-
"""[MW0602 670차 후속3 · F3] 현물 외인 금액 데드존(PIT S1 · I3) 보정 — 읽기 전용, 장 마감 후 전용.

    conda run --no-capture-output -n py310_64 python scripts/spot_foreign_amt_dead_calib.py

1차(선정): 분위 대응 — 수량 문턱 S1=100(주식 수)의 투표율을 보존하는 금액 문턱(10-10 v2 옵션 개정과 같은 방법, 손익 미참조).
2차(검증 — 선정에 쓰지 않는다): 방향 적중 sign(15:09 종가 − 기준가) 문턱 격자 · 시간 분할 · 일 단위 부트스트랩
   (같은 날 표본은 같은 종가로 채점돼 독립이 아니다 — 표본 단위 p 는 과대).
2026-10-28 초회(9/21–10/28, 25거래일): PIT 9,350 · 장중 9,450 → 채택 9,350.
재검증: 26주 WFA 주기 또는 원천(7222) 변경 시. 문턱을 손익축 최댓값으로 옮기지 말 것(사후탐색).
"""
import math
import os
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import foreign_flow_pit_review as P   # noqa: E402
from utils.analysis_db import guard_intraday   # noqa: E402

guard_intraday("spot_foreign_amt_dead_calib")

con = sqlite3.connect("file:%s?mode=ro" % os.path.join(ROOT, "data", "db", "option_flow.db").replace("\\", "/"), uri=True)
days = [r[0] for r in con.execute("SELECT DISTINCT trade_date FROM option_investor_flow WHERE product='kospi_spot' ORDER BY 1")]
spot = {}
for d in days:
    rows = con.execute("SELECT bar_time, net_qty, net_amt FROM option_investor_flow WHERE trade_date=? AND product='kospi_spot' "
                       "AND investor='foreign' ORDER BY bar_time", (d,)).fetchall()
    spot[d] = ([(t, q) for t, q, a in rows], [(t, a) for t, q, a in rows])


def hm(t):
    h, m = t.split(":")
    return int(h) * 60 + int(m)


def fmt(m):
    return "%02d:%02d" % (m // 60, m % 60)


PIT_T = ["09:05", "09:15", "09:25", "09:35", "09:45", "09:55"]
DAY_T = [fmt(m) for m in range(hm("09:15"), hm("15:00"), 10)]

samples = []    # (day, T, dq, da, px, close1509, fwd30, cum_q, cum_a)
for d in days:
    try:
        S = P.load(d)
    except Exception as e:                                # noqa: BLE001
        print("load fail", d, e)
        continue
    cs = S["cs"]
    if not cs:
        continue
    ref = [c for c in cs if hm(c[0]) < hm("15:10")]
    if not ref or ref[-1][0] < "15:09":
        continue
    close1509 = ref[-1][4]
    qs, am = spot[d]
    for T in sorted(set(PIT_T + DAY_T)):
        before = [c for c in cs if hm(c[0]) < hm(T)]
        if not before:
            continue
        px = before[-1][4]
        fw = [c for c in cs if hm(c[0]) < hm(T) + 30]
        fwd30 = fw[-1][4] if fw else None
        cq, dq = P._d(qs, T)
        ca, da = P._d(am, T)
        samples.append(dict(d=d, T=T, pit=T in PIT_T, dq=dq, da=da, px=px, c=close1509, f30=fwd30, cq=cq, ca=ca))

print("거래일 %d · 표본 %d (PIT %d)" % (len(days), len(samples), sum(s["pit"] for s in samples)))


def quantile_match(sub, label):
    q = [abs(s["dq"]) for s in sub if s["dq"] is not None and s["da"] is not None]
    a = sorted(abs(s["da"]) for s in sub if s["dq"] is not None and s["da"] is not None)
    rate = sum(1 for x in q if x >= 100) / len(q)
    k = int(round((1 - rate) * len(a)))
    k = min(max(k, 0), len(a) - 1)
    raw = a[k]
    print("[%s] 표본 %d · 수량 |Δ|≥100 투표율 %.1f%% → 같은 투표율 금액 문턱 %.0f백만 (50단위 %d) · |Δ금액| 분위 p25 %.0f p50 %.0f p75 %.0f p90 %.0f"
          % (label, len(q), 100 * rate, raw, int(round(raw / 50.0) * 50), a[len(a) // 4], a[len(a) // 2], a[3 * len(a) // 4], a[9 * len(a) // 10]))
    return int(round(raw / 50.0) * 50)


def binom_p(k, n):
    """양측 이항 p(0.5) — 정규 근사 + 연속성 보정."""
    if n == 0:
        return float("nan")
    z = (abs(k - n / 2.0) - 0.5) / math.sqrt(n / 4.0)
    return math.erfc(max(z, 0) / math.sqrt(2))


def hit_table(sub, key, grid, outcome, label, unit):
    print("\n[%s] %s 투표 적중 — 결과축 %s" % (label, key, outcome))
    print("  문턱(%s) |  투표 n  적중률   p   | 앞절반 n 적중 | 뒤절반 n 적중" % unit)
    half = days[len(days) // 2]
    for g in grid:
        rows = []
        for s in sub:
            v = s[key]
            y = s[outcome]
            if v is None or y is None or abs(v) < g or y == s["px"]:
                continue
            rows.append((s["d"], (v > 0) == (y > s["px"])))
        n = len(rows)
        k = sum(h for _, h in rows)
        a = [h for d, h in rows if d < half]
        b = [h for d, h in rows if d >= half]
        print("  %8s | %5d  %5.1f%%  %.3f | %5d %5.1f%% | %5d %5.1f%%" % (
            g, n, 100.0 * k / n if n else float("nan"), binom_p(k, n), len(a), 100.0 * sum(a) / len(a) if a else float("nan"),
            len(b), 100.0 * sum(b) / len(b) if b else float("nan")))


pit = [s for s in samples if s["pit"]]
allt = samples
print("\n== 1차: 분위 대응 (S1) ==")
dead_pit = quantile_match(pit, "PIT 09:05–09:55")
dead_all = quantile_match(allt, "장중 09:15–14:55")

GA = [0, 50, 100, 200, 300, 500, 1000, 2000, 3000, 5000]
GQ = [0, 50, 100, 200, 500, 1000]
print("\n== 2차: 손익축 검증 (선정에 쓰지 않는다) ==")
hit_table(pit, "dq", GQ, "c", "PIT · 수량(현행)", "주식수")
hit_table(pit, "da", GA, "c", "PIT · 금액", "백만")
hit_table(allt, "dq", GQ, "c", "장중 · 수량(현행)", "주식수")
hit_table(allt, "da", GA, "c", "장중 · 금액", "백만")
hit_table(allt, "da", GA, "f30", "장중 · 금액 · 30분 뒤", "백만")

# ── I3: 누계 부호 지속(금액) ──
print("\n== I3 (누계 부호 지속) — upto 시각별 · 데드존 = |누계| < D 면 부호 없음 ==")


def i3(series, upto, D):
    pts = [(t, v) for t, v in series if "09:00" <= t <= upto and v is not None]
    if len(pts) < 10:
        return None
    cur = pts[-1][1]
    if abs(cur) < D:
        return 0.0
    sgn = 1 if cur > 0 else -1
    same = sum(1 for _t, v in pts if abs(v) >= D and (v > 0) == (cur > 0))
    return sgn * same / len(pts)


for upto in ("10:00", "11:00", "13:00"):
    print(" upto %s" % upto)
    for which, idx in (("수량", 0), ("금액", 1)):
        grid = [0] if which == "수량" else [0, 100, 300, 500, 1000, 2000, 3000, 5000]
        for D in grid:
            rows = []
            for d in days:
                ss = [s for s in samples if s["d"] == d]
                if not ss:
                    continue
                v = i3(spot[d][idx], upto, D)
                pxs = [s for s in ss if s["T"] <= upto]
                if v is None or v == 0 or not pxs:
                    continue
                px, c = pxs[-1]["px"], ss[0]["c"]
                if c == px:
                    continue
                rows.append((d, (v > 0) == (c > px), abs(v)))
            n = len(rows)
            k = sum(h for _, h, _ in rows)
            strong = [h for _, h, a in rows if a >= 0.8]
            print("   %s D=%5s  n=%2d 적중 %5.1f%% p=%.2f · |I3|≥0.8 n=%2d 적중 %s" % (
                which, D, n, 100.0 * k / n if n else float("nan"), binom_p(k, n), len(strong),
                ("%.0f%%" % (100.0 * sum(strong) / len(strong))) if strong else "—"))


# ── 보강: 일 단위 군집 검정 · 넓은 격자 ──
print("\n== 보강: 일 단위 군집(같은 날 표본은 같은 종가로 채점 — 독립 아님) ==")
import random
random.seed(7)


def day_cluster(sub, key, g, outcome="c"):
    per = {}
    for s in sub:
        v, y = s[key], s[outcome]
        if v is None or y is None or abs(v) < g or y == s["px"]:
            continue
        per.setdefault(s["d"], []).append((v > 0) == (y > s["px"]))
    ds = sorted(per)
    if not ds:
        return None
    rate = lambda dd: sum(sum(per[d]) for d in dd) / float(sum(len(per[d]) for d in dd))
    obs = rate(ds)
    boots = sorted(rate([random.choice(ds) for _ in ds]) for _ in range(2000))
    return len(ds), sum(len(per[d]) for d in ds), obs, boots[50], boots[1949]


GW = [0, 1000, 3000, 5000, 10000, 20000, 30000, 50000]
for lab, sub in (("PIT", pit), ("장중", allt)):
    print(" [%s] 수량 100(현행): 일 %d · 투표 %d · 적중 %.1f%% · 95%% 일-부트스트랩 [%.1f, %.1f]" % ((lab,) + tuple(
        x * 100 if isinstance(x, float) else x for x in day_cluster(sub, "dq", 100))))
    for g in GW:
        r = day_cluster(sub, "da", g)
        if r:
            print(" [%s] 금액 %6d백만: 일 %2d · 투표 %4d · 적중 %.1f%% · 95%% [%.1f, %.1f]" % (lab, g, r[0], r[1], 100 * r[2], 100 * r[3], 100 * r[4]))


print("\n== 보강2: I3 데드존 D=S1 문턱(9,350) 의 실효 · 개장 초 |누계| 분포 ==")
for upto in ("09:30", "10:00", "11:00"):
    cums = []
    for d in days:
        pts = [v for t, v in spot[d][1] if "09:00" <= t <= upto and v is not None]
        if pts:
            cums.append(abs(pts[-1]))
    cums.sort()
    print(" upto %s: |누계| p10 %.0f · p25 %.0f · p50 %.0f · <9350 인 날 %d/%d" % (
        upto, cums[len(cums) // 10], cums[len(cums) // 4], cums[len(cums) // 2], sum(1 for c in cums if c < 9350), len(cums)))
for upto in ("10:00", "11:00"):
    for D in (9350, 20000):
        rows = []
        for d in days:
            ss = [s for s in samples if s["d"] == d]
            v = i3(spot[d][1], upto, D)
            pxs = [s for s in ss if s["T"] <= upto]
            if v is None or v == 0 or not pxs or ss[0]["c"] == pxs[-1]["px"]:
                continue
            rows.append((ss[0]["c"] > pxs[-1]["px"]) == (v > 0))
        print(" I3 금액 upto %s D=%d: n=%d 적중 %.1f%%" % (upto, D, len(rows), 100.0 * sum(rows) / len(rows)))
