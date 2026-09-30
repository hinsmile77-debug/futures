# -*- coding: utf-8 -*-
"""R1 대리 검증 — 선물 투자자별 순매수(raw_investor_futures) vs 개인 위클리 콜−풋 R1.
① 6일 겹침: 개장 직후 스냅샷 부호 대조 ② 6일 분 단위 누적 변화 상관 ③ 79일: 대리 R1 의 방향 적중률(09:00→15:05, 09:xx→15:05)."""
import os, sys, json, sqlite3, datetime as _dt, math, collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load import load
from grid import r1_bias

RAW = os.path.join(ROOT, "data/db/raw_data.db")
c = sqlite3.connect(RAW)
inv = collections.defaultdict(dict)        # day -> hm -> fields
for ts, f in c.execute("select ts,fields from raw_investor_futures order by ts"):
    inv[ts[:10]][ts[11:16]] = json.loads(f)
days = sorted(inv)
cl = collections.defaultdict(dict)
for ts, x in c.execute("select ts,close from raw_candles where ts>='2026-06-01' order by ts"):
    cl[ts[:10]][ts[11:16]] = x

KEYS = ("retail_net_qty", "foreign_net_qty", "institution_net_qty")
FD = ["2026-09-21", "2026-09-22", "2026-09-23", "2026-09-28", "2026-09-29", "2026-09-30"]


def first_at(day, hm):
    ks = sorted(k for k in inv[day] if k >= hm)
    return (ks[0], inv[day][ks[0]]) if ks else (None, None)


print("① 6일 겹침 — 개장 직후 스냅샷(첫 수신 분) vs 콜−풋 R1")
print("%-10s %6s %8s | %s" % ("날짜", "R1", "콜−풋", "  ".join("%-14s" % k.replace("_net_qty", "") for k in KEYS)) + " | 실제(09:00→15:05)")
r1 = {}
for d in FD:
    x = load(d)
    if not x:
        continue
    dd, L, _ = x
    b = r1_bias(dd); r1[d] = b
    k0 = dd.last_at_or_before("08:59"); sp = dd.sp.get(k0)
    hm, f = first_at(d, "09:00")
    c0, c1 = cl[d].get("09:00"), cl[d].get("15:05")
    act = (1 if c1 > c0 else -1) if c0 and c1 else None
    print("%-10s %6s %+8.0f | %s | %s" % (d, {1: "상방", -1: "하방", 0: "보류", None: "-"}[b], sp or 0,
          "  ".join("%s %+6d" % (hm, f[k]) for k in KEYS) if f else "-", {1: "상승", -1: "하락", None: "-"}[act]))

print("\n② 6일 — 분 단위 누적(09:xx 값) 콜−풋 vs 선물 순매수 상관(피어슨, 그날 안)")
for d in FD:
    x = load(d)
    if not x:
        continue
    dd = x[0]
    row = []
    for k in KEYS:
        xs, ys = [], []
        for hm, f in inv[d].items():
            if hm in dd.sp and "09:00" <= hm <= "15:05":
                xs.append(dd.sp[hm]); ys.append(f[k])
        if len(xs) > 10:
            mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
            sxy = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
            sxx = math.sqrt(sum((a - mx) ** 2 for a in xs) * sum((b - my) ** 2 for b in ys))
            row.append("%s r=%+.2f" % (k.replace("_net_qty", ""), sxy / sxx if sxx else 0))
    print("  %s  n=%d  %s" % (d, len(xs), "  ".join(row)))

print("\n③ %d일 — 대리 R1 적중률. 대리 = 시각 T 첫 수신값의 부호(역방향/순방향), |값| ≥ 문턱이면 방향, 아니면 보류" % len(days))
print("   적중 = 방향 판정 후 T 종가 → 15:05 종가가 그 방향. p = 이항검정(50%) 단측")


def binom_p(k, n):
    from math import factorial as F
    comb = lambda a, b: F(a) // (F(b) * F(a - b))
    return sum(comb(n, i) for i in range(k, n + 1)) / 2 ** n if n else 1.0


for T in ("09:02", "09:05", "09:10", "09:30"):
    for k in KEYS:
        for sign, lab in ((-1, "역방향"), (1, "순방향")):
            line = []
            for th in (0, 50, 100, 200, 300):
                hit = n = 0
                for d in days:
                    hm, f = first_at(d, T)
                    if not f or hm > "09:35" or f.get(k) is None:
                        continue
                    v = f[k]
                    if abs(v) < th or v == 0:
                        continue
                    bias = sign * (1 if v > 0 else -1)
                    c0, c1 = cl[d].get(hm), cl[d].get("15:05")
                    if not c0 or not c1 or c1 == c0:
                        continue
                    n += 1; hit += (bias == (1 if c1 > c0 else -1))
                line.append("th%3d %2d/%2d=%3.0f%% p=%.2f" % (th, hit, n, 100 * hit / n if n else 0, binom_p(hit, n)))
            print("  %s %-11s %s | %s" % (T, k.replace("_net_qty", ""), lab, " | ".join(line)))
# 참고: 콜−풋 R1 자체의 적중(6일)
print("\n참고 — 콜−풋 R1(08:59) 적중: 방향일 %d일 중 %d" % (
    sum(1 for d in r1 if r1[d]), sum(1 for d in r1 if r1[d] and cl[d].get("09:00") and cl[d].get("15:05") and r1[d] == (1 if cl[d]["15:05"] > cl[d]["09:00"] else -1))))
