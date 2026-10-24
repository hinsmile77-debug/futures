# -*- coding: utf-8 -*-
"""본전·트레일 스톱 재확인·재시도 흐름 손익 비교. 읽기 전용."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim6                                                   # noqa: E402
OOS = "2026-10-19"
def summ(o):
    dd = {d: sum(t["pt"] for t in v) for d, v in o.items()}
    return sum(dd.values()), min(dd.values()), sum(v for d, v in dd.items() if d >= OOS), sum(len(v) for v in o.values())
print("| 흐름 | 달아난 체결 가정 | 21일 합계 pt | 최악일 | 10/19~ | 거래 | 달아난 봉 발생 | 재시도 체결 · 취소 |")
print("|---|---|---|---|---|---|---|---|")
res = {}
for lab, cfg in (("현행 시장가", {"stopx": ("mkt", "stop")}), ("현행 시장가", {"stopx": ("mkt", "mid")}), ("현행 시장가", {"stopx": ("mkt", "close")}),
                 ("재확인·재시도 1pt", {"stopx": ("retry", 1.0)}), ("재확인·재시도 0.5pt", {"stopx": ("retry", 0.5), "band": 0.5}),
                 ("재확인·재시도 2pt", {"stopx": ("retry", 2.0), "band": 2.0}), ("종가 확인형", {"stopx": ("close",)})):
    sim6.EV.clear(); o = sim6.run(cfg); tot, wd, oos, n = summ(o)
    ran = [e for e in sim6.EV if e[2] == "ran"]; rf = sum(e[2] == "retry_fill" for e in sim6.EV); rc = sum(e[2] == "retry_cancel" for e in sim6.EV)
    note = {"stop": "스톱가(낙관)", "mid": "스톱–종가 중간", "close": "종가(비관)"}.get(cfg["stopx"][1] if cfg["stopx"][0] == "mkt" else "", "-")
    print("| %s | %s | %+.1f | %.1f | %+.1f | %d | %d다리 | %d · %d |" % (lab, note, tot, wd, oos, n, len(ran), rf, rc))
    res[(lab, note)] = (o, list(sim6.EV))
print("\n[달아난 봉 사건 — 현행(종가 가정) 기준] 날짜 · 다리 · 시각 · 종가가 스톱 밖으로 벗어난 pt")
for e in res[("현행 시장가", "종가(비관)")][1]:
    if e[2] == "ran": print("  ", e[0][5:], e[1], e[3], e[4])
print("\n[재시도 1pt 사건]")
for e in res[("재확인·재시도 1pt", "-")][1]: print("  ", e[0][5:], e[1:])
a, b = res[("현행 시장가", "스톱가(낙관)")][0], res[("재확인·재시도 1pt", "-")][0]
print("\n[재시도 1pt 가 현행(스톱가) 과 달라진 날]")
for d in a:
    if [(t["t"], t["pt"]) for t in a[d]] != [(t["t"], t["pt"]) for t in b[d]]:
        print("  %s 현행 %+.1f %s\n        재시도 %+.1f %s" % (d[5:], sum(t["pt"] for t in a[d]), [(t["t"], t["why"], t["pt"]) for t in a[d]],
              sum(t["pt"] for t in b[d]), [(t["t"], t["why"], t["pt"]) for t in b[d]]))
