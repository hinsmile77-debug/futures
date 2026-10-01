# -*- coding: utf-8 -*-
"""대조 실험 — roll60(최근 60분 콜-풋 변화)의 효과는 「추세 측정」인가 「개장 1시간 건너뛰기」인가.
(a) level K300 인데 진입을 10:00 이후로만 (b) roll60 (c) roll60 인데 기준 창을 45·90·120분 (d) 풋·콜 단독의 roll60 (e) LODO."""
import os, sys, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dir_lab as X
M = 1e4
data = {d: X.load(d) for d in X.DAYS}


def run_from(P, sig, start):
    def s2(k):
        return sig(k) if k >= start else 0
    return X.run(P, s2)


def row(name, fn):
    v, n = [], 0
    for d in X.DAYS:
        tr = fn(data[d]); v.append(sum(t["net"] for t in tr) / M); n += len(tr)
    print("%-44s" % name + "".join("%+7.0f" % x for x in v) + "%+9.1f %+7.1f %4d/7 %4d" % (sum(v), min(v), sum(x > 0 for x in v), n))
    return v


print("%-44s" % "설정" + "".join("%7s" % d[5:] for d in X.DAYS) + "%9s %7s %6s %4s" % ("7일 합", "최악일", "흑자일", "거래"))
lvl = [("sp", "level", 0, 300, -1)]
row("v2.1 현행 level K300", lambda P: X.run(P, X.make_sig(P, lvl)))
for stt in ("09:30", "10:00", "10:30"):
    row("  level K300 · 진입 %s 이후만" % stt, lambda P, stt=stt: run_from(P, X.make_sig(P, lvl), stt))
for w in (30, 45, 60, 90, 120):
    for K in (150, 300):
        row("콜-풋 최근 %d분 변화 K%d" % (w, K), lambda P, w=w, K=K: X.run(P, X.make_sig(P, [("sp", "roll", w, K, -1)])))
row("콜 최근 60분 K150(콜 증가=매도)", lambda P: X.run(P, X.make_sig(P, [("call", "roll", 60, 150, -1)])))
row("풋 최근 60분 K150(풋 증가=매수)", lambda P: X.run(P, X.make_sig(P, [("put", "roll", 60, 150, +1)])))
row("외인선물 최근 60분 K400(순방향)", lambda P: X.run(P, X.make_sig(P, [("fx", "roll", 60, 400, +1)])))
row("콜-풋 60분 K150 + 외인선물 60분 부호 동의", lambda P: X.run(P, X.make_sig(P, [("sp", "roll", 60, 150, -1), ("fx", "roll", 60, 0, +1)], "gate")))
row("콜-풋 60분 K150 + 풋 60분 부호 동의", lambda P: X.run(P, X.make_sig(P, [("sp", "roll", 60, 150, -1), ("put", "roll", 60, 0, +1)], "gate")))

# LODO — roll 창 {45,60,90} × K {100,150,200,300,400} 15조합 안에서
cfgs = [[("sp", "roll", w, K, -1)] for w in (45, 60, 90) for K in (100, 150, 200, 300, 400)]
tab = [[sum(t["net"] for t in X.run(data[d], X.make_sig(data[d], c))) / M for d in X.DAYS] for c in cfgs]
sums = [sum(v) for v in tab]
lodo = []
for j in range(len(X.DAYS)):
    pick = max(range(len(tab)), key=lambda i: sums[i] - tab[i][j]); lodo.append(tab[pick][j])
print("\n콜-풋 롤링(45·60·90분 × K 5종 = 15조합): 7일 합 최저 %+.1f · 중앙 %+.1f · 최고 %+.1f · 흑자 조합 %d/15 · 최악일 중앙 %+.1f" % (
    min(sums), st.median(sums), max(sums), sum(s > 0 for s in sums), st.median(min(v) for v in tab)))
print("LODO 일별: " + " ".join("%+6.0f" % x for x in lodo) + "  합 %+.1f · 최악일 %+.1f   (현행 계열 LODO +427.3 · 최악일 -181.9)" % (sum(lodo), min(lodo)))
