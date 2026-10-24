# -*- coding: utf-8 -*-
"""슬립 1pt 지정가 청산 + 「반드시 청산」 재시도 3종 vs 현행 시장가. 읽기 전용."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim6                                                   # noqa: E402
OOS = "2026-10-19"
def summ(o):
    dd = {d: sum(t["pt"] for t in v) for d, v in o.items()}
    return sum(dd.values()), min(dd.values()), sum(v for d, v in dd.items() if d >= OOS), dd
rows = [("현행 시장가 · 체결=스톱가(낙관)", {"stopx": ("mkt", "stop")}),
        ("현행 시장가 · 체결=스톱–종가 중간", {"stopx": ("mkt", "mid")}),
        ("현행 시장가 · 체결=종가(비관)", {"stopx": ("mkt", "close")}),
        ("(앞 시험) 1pt 지정가 고정 · 회복 대기", {"stopx": ("retry", 1.0)}),
        ("① 1pt 추격 지정가(매분 직전종가∓1)", {"stopx": ("chase", 1.0)}),
        ("② 단계 상향 1→2→4pt→가격제한폭", {"stopx": ("escalate",)}),
        ("③ 1pt 지정가 1회 → 다음 분 시가 시장가", {"stopx": ("mkt1",)})]
print("| 흐름 | 21일 합계 pt | 최악일 | 10/19~ | 미체결 다리 | 재시도 체결까지 분(최대) | 10/23 |")
print("|---|---|---|---|---|---|---|")
for lab, cfg in rows:
    sim6.EV.clear(); o = sim6.run(cfg); tot, wd, oos, dd = summ(o)
    ran = sum(1 for e in sim6.EV if e[2] == "ran")
    fills = [e for e in sim6.EV if e[2] == "retry_fill"]
    mx = max((e[4] for e in fills if len(e) > 4), default=0)
    print("| %s | %+.1f | %.1f | %+.1f | %d | %s | %+.1f |" % (lab, tot, wd, oos, ran, mx if fills else "-", dd["2026-10-23"]))
