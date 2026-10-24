# -*- coding: utf-8 -*-
"""대조 — 개인 콜 단독(콜 ↑ → 매도). 풋 단독이 진 이유가 「풋에 정보가 없다」인지 「콜−풋 차이에 정보가 있다」인지 가른다. 읽기 전용."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import put_dir as P                                             # noqa: E402  (기준·풋 결과 출력 없이 함수만 쓰려면 아래만 본다)
from strategy.shindong import engine as E, families as F, spec as S   # noqa: E402


def day_net_call(day, kc, kr):
    d, L = P.sim.frame(day)
    call = d.call
    def fs(dd, series, k, sign):
        return P.OF(dd, call, kc, -1) if (kc is not None and series is dd.sp) else P.OF(dd, series, k, sign)
    def rsig(series, win, k, sign):
        return P.OR(call, win, kr, -1) if (kr is not None and series is d.sp) else P.OR(series, win, k, sign)
    F._flow_signal, F._roll_signal = fs, rsig
    try:
        r = F.run_family_day(d, L, "hybr60")
    finally:
        F._flow_signal, F._roll_signal = P.OF, P.OR
    return sum(E.trade_net(t) for t in r["trades"] if t["status"] == "CLOSED") / 2 / S.PT_VALUE_KRW


print("\n## 대조: 개인 콜 단독 (A 첫거래=콜 · C 둘다=콜)")
for kc, kr in [(k, None) for k in (100, 150, 200, 300)] + [(k, k // 2) for k in (100, 150, 200, 300)]:
    v = {d: day_net_call(d, kc, kr) for d in P.DAYS}
    a = sum(x for d, x in v.items() if d <= P.A_END); b = sum(x for d, x in v.items() if d >= P.B_START)
    print("  kc=%-4s kr=%-4s %+7.1f (Δ%+6.1f) | 전반 %+6.1f 후반 %+6.1f | 최악일 %6.1f" % (kc, kr, sum(v.values()), sum(v.values()) - P.B0["tot"], a, b, min(v.values())))
