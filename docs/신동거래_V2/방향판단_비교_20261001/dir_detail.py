# -*- coding: utf-8 -*-
"""dir_lab 후속 — (a) MAIN 신호(K300 level)에 게이트만 얹은 깨끗한 대조 (b) 첫 신호의 방향 적중 (c) 3b 계열 상위 설정의 평탄성."""
import os, sys, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dir_lab as X
M = 1e4
data = {d: X.load(d) for d in X.DAYS}
SP300 = ("sp", "level", 0, 300, -1)
CASES = [
    ("v2.1 현행: 콜-풋 level K300", [SP300], "all"),
    ("  + 가격 30분 방향 동의", [SP300, ("px", "roll", 30, 0, +1)], "gate"),
    ("  + 가격 60분 방향 동의", [SP300, ("px", "roll", 60, 0, +1)], "gate"),
    ("  + 가격 09:00 대비 동의", [SP300, ("px", "level", 0, 0, +1)], "gate"),
    ("  + 외인선물 부호 동의", [SP300, ("fx", "level", 0, 0, +1)], "gate"),
    ("  + 외인선물 30분 동의", [SP300, ("fx", "roll", 30, 0, +1)], "gate"),
    ("  + 풋 60분 방향 동의(풋 증가=매수)", [SP300, ("put", "roll", 60, 0, +1)], "gate"),
    ("콜 증감 level K300(콜 증가=매도)", [("call", "level", 0, 300, -1)], "all"),
    ("풋 증감 level K300(풋 증가=매수)", [("put", "level", 0, 300, +1)], "all"),
    ("풋 증감 level K300(풋 증가=매도)", [("put", "level", 0, 300, -1)], "all"),
    ("풋 60분 K300(풋 증가=매수) [2a 최적]", [("put", "roll", 60, 300, +1)], "all"),
    ("풋 15분 K100(풋 증가=매도) [2b 최적]", [("put", "roll", 15, 100, -1)], "all"),
    ("풋 60분 K200 + 외인선물 30분 [3 최적]", [("put", "roll", 60, 200, +1), ("fx", "roll", 30, 0, +1)], "gate"),
    ("콜-풋 60분 K150 + 가격 30분 [3b 최적]", [("sp", "roll", 60, 150, -1), ("px", "roll", 30, 0, +1)], "gate"),
    ("외인선물 60분 K400 [외인 단독 최적]", [("fx", "roll", 60, 400, +1)], "all"),
]
print("%-40s" % "설정" + "".join("%7s" % d[5:] for d in X.DAYS) + "%9s %7s %5s  첫신호 적중" % ("7일 합", "최악일", "거래"))
for name, comps, comb in CASES:
    v, n, hit, tot = [], 0, 0, 0
    for d in X.DAYS:
        P = data[d]
        tr = X.run(P, X.make_sig(P, comps, comb))
        v.append(sum(t["net"] for t in tr) / M); n += len(tr)
        if tr:
            D = P["D"]; c15 = D.c[D.last_at_or_before("15:05")]
            mv = c15 - tr[0]["e"]
            if mv != 0:
                tot += 1; hit += int(tr[0]["side"] * mv > 0)
    print("%-40s" % name + "".join("%+7.0f" % x for x in v) + "%+9.1f %+7.1f %5d  %d/%d" % (sum(v), min(v), n, hit, tot))

# 3b 계열(콜-풋 + 가격 30분 게이트) 전 조합 분포 — 평탄한가
tab = []
for comps, comb in X.FAM["3b 콜-풋 + 가격 30분(게이트)"]:
    v = [sum(t["net"] for t in X.run(data[d], X.make_sig(data[d], comps, comb))) / M for d in X.DAYS]
    tab.append((sum(v), min(v), "%s%s K%s" % (comps[0][1], comps[0][2] or "", comps[0][3]), v))
tab.sort(reverse=True)
print("\n3b 콜-풋 + 가격 30분 게이트 — 전 22조합(7일 합 순)")
for s, w, c, v in tab:
    print("  %-12s 합 %+7.1f 최악일 %+7.1f | %s" % (c, s, w, " ".join("%+5.0f" % x for x in v)))
base = []
for comps, comb in X.FAM["1 콜-풋(역방향)"]:
    v = [sum(t["net"] for t in X.run(data[d], X.make_sig(data[d], comps, comb))) / M for d in X.DAYS]
    base.append((sum(v), min(v), "%s%s K%s" % (comps[0][1], comps[0][2] or "", comps[0][3]), v))
base.sort(reverse=True)
print("\n1 콜-풋 단독 — 전 22조합(7일 합 순)")
for s, w, c, v in base:
    print("  %-12s 합 %+7.1f 최악일 %+7.1f | %s" % (c, s, w, " ".join("%+5.0f" % x for x in v)))
# 같은 신호 설정끼리: 게이트를 얹으면 좋아지나(22쌍)
gate = {c: (s, w) for s, w, c, _ in tab}
plain = {c: (s, w) for s, w, c, _ in base}
better = sum(1 for c in gate if gate[c][0] > plain[c][0]); wbetter = sum(1 for c in gate if gate[c][1] > plain[c][1])
print("\n같은 신호 22쌍: 가격 게이트로 7일 합이 나아진 쌍 %d/22 · 최악일이 나아진 쌍 %d/22 · 합 차이 중앙 %+.1f만" % (
    better, wbetter, st.median(gate[c][0] - plain[c][0] for c in gate)))
