# -*- coding: utf-8 -*-
"""자본 3,000만 · BE3A · 증거금 연동 — 위험 최소·이익 최대 X 탐색. 읽기 전용.
위험 4축: ① 설계상 최악 거래(수량×0.6×ATR) ② 보유 중 최대 역행 노출(MAE×수량)
         ③ 본전이동 미작동 스트레스(같은 수량을 v3 거래에 적용한 최악일) ④ 부트스트랩 월(21일 복원추출 1만회)."""
import os, sys, io, contextlib, random, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
with contextlib.redirect_stdout(io.StringIO()):
    import qty_sim as Q                                             # noqa: E402
import sim4                                                         # noqa: E402
from collections import Counter
DEP, PTV, MAXQ, TARGET = 30_000_000, 50_000, 3, 10_000_000
BE3A = sim4.run({"agree": True})
V3 = Q.res["v3 현행"]
plan = {}
for d in Q.plan:
    Dd, L = Q.sim.frame(d)
    plan[d] = dict(m=int(DEP // (Q.day_px(Dd) * PTV * Q.RATE)), atr=Q.plan[d]["atr"])
DAYS = sorted(plan)


def qty(X):
    return {d: max(1, min(MAXQ, p["m"], int(DEP * X // (0.6 * p["atr"] * PTV)))) for d, p in plan.items()}


def daily(o, qd, slip=0.0, scale=1.0):
    out = {}
    for d in DAYS:
        s = 0.0
        for t in o[d]:
            pt = t["pt"] - (slip if "BE" in t.get("why", "") else 0.0)
            s += (pt * scale if pt > 0 else pt) * qd[d] * PTV
        out[d] = s
    return out


def mdd(xs):
    c = p = m = 0.0
    for x in xs:
        c += x; p = max(p, c); m = max(m, p - c)
    return m


def boot(dl, n=10000, seed=7):
    rnd = random.Random(seed); v = list(dl.values()); ms = sorted(sum(rnd.choice(v) for _ in range(21)) for _ in range(n))
    return dict(p_loss=sum(x < 0 for x in ms) / n, p5=ms[int(.05 * n)], med=ms[n // 2], p_tgt=sum(x >= TARGET for x in ms) / n)


rows = []
for X in [x / 100 for x in range(2, 16)] + [None]:
    qd = qty(X) if X else {d: max(1, min(MAXQ, plan[d]["m"])) for d in DAYS}
    base, hc, st3 = daily(BE3A, qd), daily(BE3A, qd, 1.0, 0.5), daily(V3, qd)
    tot = sum(base.values())
    design = max(qd[d] * 0.6 * plan[d]["atr"] * PTV for d in DAYS)
    expo = max(t["mae"] * qd[d] * PTV for d in DAYS for t in BE3A[d])
    sd = st.pstdev(list(base.values()))
    b1, b2 = boot(base), boot(hc)
    rows.append(dict(X=X, qd=qd, tot=tot, hc=sum(hc.values()), design=design, expo=expo, stress=min(st3.values()),
                     mdd=mdd([base[d] for d in DAYS]), sharpe=(st.mean(base.values()) / sd * 21 ** .5) if sd else 0, b1=b1, b2=b2))
m = lambda x: format(x / 1e4, "+,.0f") + "만"
print("## 자본 3,000만 · BE3A · 수량 = min(3, 증거금, X%) (최소 1)")
print("| X | 수량 분포 | 21일 합계 | 설계상 최악 거래 | 최대 보유역행 | 스트레스 최악일(BE 미작동) | 합계 ÷ 설계최악 | 월 샤프 | 표본 부트: 손실월 · 하위5% · 목표확률 | 보수(×0.5+슬립1): 합계 · 손실월 · 하위5% · 목표확률 |")
print("|---|---|---|---|---|---|---|---|---|---|")
for r in rows:
    lab = "증거금만" if r["X"] is None else "%d%%" % round(r["X"] * 100)
    print("| %s | %s | %s | %s (%.1f%%) | %s | %s (%.1f%%) | %.1f | %.1f | %.1f%% · %s · %.0f%% | %s · %.1f%% · %s · %.0f%% |" % (
        lab, dict(sorted(Counter(r["qd"].values()).items())), m(r["tot"]), m(-r["design"]), r["design"] / DEP * 100,
        m(-r["expo"]), m(r["stress"]), -r["stress"] / DEP * 100, r["tot"] / r["design"], r["sharpe"],
        r["b1"]["p_loss"] * 100, m(r["b1"]["p5"]), r["b1"]["p_tgt"] * 100,
        m(r["hc"]), r["b2"]["p_loss"] * 100, m(r["b2"]["p5"]), r["b2"]["p_tgt"] * 100))
