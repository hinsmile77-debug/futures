# -*- coding: utf-8 -*-
"""유형①·② 수익 최적화 격자 — 기준선(v3+BE3+상한제외) 대비. 읽기 전용."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim4                                                   # noqa: E402
import sim3                                                   # noqa: E402  선행 기준선 대조용

A_END, B_START, OOS = "2026-10-08", "2026-10-12", "2026-10-19"


def daily(o):
    return {d: sum(t["pt"] for t in v) for d, v in o.items()}


def mdd(xs):
    c = p = m = 0.0
    for x in xs:
        c += x; p = max(p, c); m = max(m, p - c)
    return m


B = sim4.run({})
BD = daily(B)
ref = sum(daily(sim3.run({})).values())
print("기준선 대조: sim4 %.2f · sim3 %.2f · 일수 %d (%s ~ %s)" % (sum(BD.values()), ref, len(BD), min(BD), max(BD)))
print("\n| 안 | 거래 | 합계 pt | Δ | 전반Δ | 후반Δ | 10/19~Δ | 최악일 | MDD | 개선일/악화일 | 발동 |")
print("|---|---|---|---|---|---|---|---|---|---|---|")


def show(lab, cfg):
    o = sim4.run(cfg)
    od = daily(o)
    tr = [t for v in o.values() for t in v]
    dlt = {d: od[d] - BD[d] for d in BD}
    a = sum(v for d, v in dlt.items() if d <= A_END)
    b = sum(v for d, v in dlt.items() if d >= B_START)
    oo = sum(v for d, v in dlt.items() if d >= OOS)
    up = sum(1 for v in dlt.values() if v > 0.05); dn = sum(1 for v in dlt.values() if v < -0.05)
    print("| %s | %d | %+.1f | %+.1f | %+.1f | %+.1f | %+.1f | %.1f | %.1f | %d/%d | %s |" % (
        lab, len(tr), sum(od.values()), sum(od.values()) - sum(BD.values()), a, b, oo,
        min(od.values()), mdd([od[d] for d in sorted(od)]), up, dn, cfg.get("_note", "")))
    return o


show("기준(v3+BE3+상한제외)", {})
# ── 유형① · 이익 잠금 ───────────────────────────────────────────────
for lk in (0.5, 1.0, 1.5):
    show("①잠금 MFE3→+%.1f" % lk, {"be_lock": lk})
show("①사다리 3→0 · 4.5→+1.5", {"ladder": [(4.5, 1.5)]})
show("①사다리 3→0 · 4.5→+2", {"ladder": [(4.5, 2.0)]})
show("①사다리 3→+0.5 · 4.5→+1.5", {"be_lock": 0.5, "ladder": [(4.5, 1.5)]})
# ── 트레일·익절(최대화) ─────────────────────────────────────────────
for act in (5.0, 6.0, 7.0, 8.0):
    for dist in (3.0, 4.0, 5.0):
        if (act, dist) != (6.0, 4.0):
            show("트레일 %g/%g" % (act, dist), {"trail": (act, dist)})
for tp in (10.0, 15.0, 18.0, None):
    show("익절 %s" % ("없음" if tp is None else "%g" % tp), {"tp": tp})
for tp1 in (4.0, 6.0, 8.0):
    show("부분익절 1다리 +%g" % tp1, {"tp1": tp1})
# ── 유형② · 진입 ───────────────────────────────────────────────────
for k in (1.0, 2.0, 3.0):
    for n in (5, 10):
        show("②눌림지정가 %gpt·%d분" % (k, n), {"pull": (k, n)})
show("②R60 누적일관성 필터", {"agree": True})
show("②HYBL 주도지표로 2·3번째", {"family": "hybl"})
show("②HYBL + 누적일관성", {"family": "hybl", "agree": True})
