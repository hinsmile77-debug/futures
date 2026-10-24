# -*- coding: utf-8 -*-
"""1차 후보 검증 — 이웃 값 안정성 · 바뀐 거래 · 슬리피지 내성 · 조합 · 유형별 몫. 읽기 전용."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim4                                                   # noqa: E402

A_END, B_START, OOS = "2026-10-08", "2026-10-12", "2026-10-19"


def daily(o):
    return {d: sum(t["pt"] for t in v) for d, v in o.items()}


def mdd(xs):
    c = p = m = 0.0
    for x in xs:
        c += x; p = max(p, c); m = max(m, p - c)
    return m


B = sim4.run({}); BD = daily(B)


def stats(o, slip=0.0):
    """slip: 본전·잠금 청산 1건당 계약당 추가 미끄러짐(pt)."""
    od = {d: sum(t["pt"] - (slip if "BE" in t["why"] else 0) for t in v) for d, v in o.items()}
    return od


def row(lab, cfg, slip=0.0):
    o = sim4.run(cfg)
    od, bd = stats(o, slip), stats(B, slip)
    dl = {d: od[d] - bd[d] for d in bd}
    nbe = sum(1 for v in o.values() for t in v if "BE" in t["why"])
    print("| %s | %d | %+.1f | %+.1f | %+.1f | %+.1f | %+.1f | %.1f | %.1f | %d |" % (
        lab, sum(len(v) for v in o.values()), sum(od.values()), sum(dl.values()),
        sum(v for d, v in dl.items() if d <= A_END), sum(v for d, v in dl.items() if d >= B_START),
        sum(v for d, v in dl.items() if d >= OOS), min(od.values()), mdd([od[d] for d in sorted(od)]), nbe))
    return o


HDR = "| 안 | 거래 | 합계 | Δ | 전반Δ | 후반Δ | 10/19~Δ | 최악일 | MDD | 본전·잠금 청산 |\n|---|---|---|---|---|---|---|---|---|---|"

print("## A. 사다리 이웃 값 (3→본전 고정, 2단 (MFE, 잠금))")
print(HDR)
row("기준", {})
for m in (4.0, 4.5, 5.0):
    for lk in (1.0, 1.5, 2.0, 2.5):
        if lk < m - 1.0:
            row("사다리 %g→+%g" % (m, lk), {"ladder": [(m, lk)]})
row("3단 3→0 · 4→+1 · 5→+2", {"ladder": [(4.0, 1.0), (5.0, 2.0)]})
row("비례 잠금 MFE m → m−3 (3~6)", {"ladder": [(3.5, 0.5), (4.0, 1.0), (4.5, 1.5), (5.0, 2.0), (5.5, 2.5)]})

print("\n## B. 트레일 간격 이웃 (발동 6)")
print(HDR)
for dist in (2.5, 3.0, 3.5, 4.0):
    row("트레일 6/%g" % dist, {"trail": (6.0, dist)})

print("\n## C. 조합")
print(HDR)
L2 = [(4.5, 2.0)]
row("사다리4.5→+2", {"ladder": L2})
row("누적일관성", {"agree": True})
row("사다리4.5→+2 + 누적일관성", {"ladder": L2, "agree": True})
row("사다리4.5→+2 + 누적일관성 + 트레일6/3", {"ladder": L2, "agree": True, "trail": (6.0, 3.0)})
row("비례잠금 + 누적일관성", {"ladder": [(3.5, 0.5), (4.0, 1.0), (4.5, 1.5), (5.0, 2.0), (5.5, 2.5)], "agree": True})

print("\n## D. 슬리피지 내성 — 본전·잠금 청산 1건당 계약당 추가 미끄러짐")
print(HDR)
for s in (0.5, 1.0):
    row("기준 · 슬립%g" % s, {}, s)
    row("사다리4.5→+2 + 누적일관성 · 슬립%g" % s, {"ladder": L2, "agree": True}, s)

print("\n## E. 바뀐 거래 — 누적일관성 필터")
o = sim4.run({"agree": True})
for d in sorted(BD):
    a = [(t["rule"], t["t"], t["side"], t["why"], t["pt"]) for t in B[d]]
    b = [(t["rule"], t["t"], t["side"], t["why"], t["pt"]) for t in o[d]]
    if a != b:
        print("  %s 기준 %s\n         필터 %s" % (d[5:], a, b))

print("\n## F. 바뀐 거래 — 사다리 4.5→+2")
o = sim4.run({"ladder": L2})
for d in sorted(BD):
    a = [(t["t"], t["side"], t["why"], t["pt"], t["mfe"]) for t in B[d]]
    b = [(t["t"], t["side"], t["why"], t["pt"], t["mfe"]) for t in o[d]]
    if a != b:
        print("  %s Δ%+.1f\n     기준 %s\n     사다리 %s" % (d[5:], sum(x[3] for x in b) - sum(x[3] for x in a), a, b))

print("\n## G. 유형별 몫 (거래 단위, pt/계약)")
for lab, oo in (("기준", B), ("사다리4.5→+2+누적일관성", sim4.run({"ladder": L2, "agree": True}))):
    tr = [t for v in oo.values() for t in v]
    t1 = [t for t in tr if 3 <= t["mfe"] < 6 and "TR" not in t["why"] and "TP" not in t["why"]]
    t2 = [t for t in tr if t["mfe"] < 3]
    win = [t for t in tr if t["mfe"] >= 6 or "TP" in t["why"] or "TR" in t["why"]]
    print("  %s: 유형①(MFE 3~6·트레일 미점화) %d건 %+.1f · 유형②(MFE<3) %d건 %+.1f · 트레일·익절 %d건 %+.1f" % (
        lab, len(t1), sum(t["pt"] for t in t1), len(t2), sum(t["pt"] for t in t2), len(win), sum(t["pt"] for t in win)))
