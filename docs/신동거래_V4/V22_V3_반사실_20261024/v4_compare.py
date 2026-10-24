# -*- coding: utf-8 -*-
"""9/21~10/23 V2.2 · V3 · V4 반사실 수익 비교. 읽기 전용(DB 미기록).
V2.2 = family flowc · V3 = family hybr60 (공식 엔진) · V4 = V3 + 본전이동@3 · 본전청산 상한 제외 · 본전 뒤 방향 금지 없음 ·
       첫 FLOW 역행컷 0.4×ATR(손절 취급) · R60 누적일관성 필터 (`docs/신동거래_V4/.../sim6.py` 시장가 청산).
손익 ① 엔진 가상 2계약 ② 실주문 수량 규칙 = min(3, 증거금 가능(자본 3,000만), floor(3,000만×7% ÷ (0.6×ATR14×5만))), 최소 1."""
import os, sys, io, json, contextlib
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while not os.path.isdir(os.path.join(ROOT, "strategy")):
    ROOT = os.path.dirname(ROOT)
DD = os.path.join(HERE, "..", "수익최대화_딥다이브_20261023_MW0602")   # 같은 docs/신동거래_V4 안
sys.path.insert(0, ROOT); sys.path.insert(0, DD)
os.chdir(ROOT)
import sim6                                                   # noqa: E402
with contextlib.redirect_stdout(io.StringIO()):
    import qty_sim as Q                                       # noqa: E402  계약당 증거금 추정
from strategy.shindong import families as F, engine as E, spec as S   # noqa: E402
PTV, CAP, X, MAXQ = 50_000, 30_000_000, 0.07, 3
v4 = sim6.run({"stopx": ("mkt", "stop")})
days = sorted(v4)
pt = {"V2.2": {}, "V3": {}, "V4": {}}
info = {}
for d in days:
    Dd, L = sim6.sim4.sim.frame(d)
    for lab, fam in (("V2.2", "flowc"), ("V3", "hybr60")):
        r = F.run_family_day(Dd, L, fam)
        pt[lab][d] = [E.trade_net(t) / 2 / PTV for t in r["trades"] if t["status"] == "CLOSED"]
    pt["V4"][d] = [t["pt"] for t in v4[d]]
    atr = L["0850"].get("atr14") or 33.3
    mg = Q.day_px(Dd) * PTV * Q.RATE
    q = max(1, min(MAXQ, int(CAP // mg), int(CAP * X // (0.6 * atr * PTV))))
    k0 = min(k for k in Dd.idx if k >= "09:00" and k in Dd.c)
    info[d] = dict(q=q, atr=atr, act=Dd.c[Dd.last_at_or_before(S.TIME_EXIT)] - Dd.c[k0], bias=F._r1_bias(Dd)[1])
m = lambda x: format(x / 1e4, "+,.1f")
print("## 일별 — 엔진 가상 2계약(만원) · [실주문 수량 규칙 원화(만원)]")
print("| 날짜 | 시장 | R1 | ATR14 | 실주문 수량 | V2.2 | V3 | **V4** | V4−V3 | V2.2 실수량 | V3 실수량 | **V4 실수량** |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|")
for d in days:
    s = {k: sum(pt[k][d]) for k in pt}
    q = info[d]["q"]
    print("| %s | %+.1f | %s | %.1f | %d | %s | %s | **%s** | %s | %s | %s | **%s** |" % (
        d[5:], info[d]["act"], {1: "상방", -1: "하방", 0: "보류"}[info[d]["bias"]], info[d]["atr"], q,
        m(s["V2.2"] * 2 * PTV), m(s["V3"] * 2 * PTV), m(s["V4"] * 2 * PTV), m((s["V4"] - s["V3"]) * 2 * PTV),
        m(s["V2.2"] * q * PTV), m(s["V3"] * q * PTV), m(s["V4"] * q * PTV)))


def summ(lab, sel, mult):
    ds = [d for d in days if sel(d)]
    xs = [sum(pt[lab][d]) * mult(d) * PTV for d in ds]
    trs = [x for d in ds for x in pt[lab][d]]
    c = p = dd = 0.0
    for x in xs:
        c += x; p = max(p, c); dd = max(dd, p - c)
    wt = min((x * mult(d) * PTV for d in ds for x in pt[lab][d]), default=0)
    return dict(tot=sum(xs), n=len(trs), w=sum(x > 0 for x in trs), worst=min(xs), mdd=dd, wt=wt, pos=sum(x > 0 for x in xs), nd=len(ds))


SEL = (("전체 9/21~10/23", lambda d: True), ("v3 설계 표본(~10/16)", lambda d: d <= "2026-10-16"), ("v3 라이브(10/19~)", lambda d: d >= "2026-10-19"))
for head, mult in (("엔진 가상 2계약", lambda d: 2), ("실주문 수량 규칙(자본 3,000만 · X 7% · 증거금 연동)", lambda d: info[d]["q"])):
    print("\n## 구간 합계 — %s" % head)
    print("| 구간 | 규칙 | 합계 | 자본 대비 | 승/거래 | 이익일 | 최악일 | 최악 거래 | MDD |")
    print("|---|---|---|---|---|---|---|---|---|")
    for sl, sel in SEL:
        for lab in ("V2.2", "V3", "V4"):
            r = summ(lab, sel, mult)
            print("| %s | %s | %s만 | %+.1f%% | %d/%d | %d/%d | %s만 | %s만 | %s만 |" % (
                sl, lab, m(r["tot"]), r["tot"] / CAP * 100, r["w"], r["n"], r["pos"], r["nd"], m(r["worst"]), m(r["wt"]), m(-r["mdd"])))
json.dump({k: {d: v for d, v in pt[k].items()} for k in pt}, open(os.path.join(HERE, "v4_compare.json"), "w"), indent=1)
