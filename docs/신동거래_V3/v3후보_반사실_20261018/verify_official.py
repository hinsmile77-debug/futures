# -*- coding: utf-8 -*-
"""v3 배포 검증 — 공식 경로(daily_report.load_day → runner.run_variant)로 16일 재생해 반사실과 대조."""
import os, sys
ROOT = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(ROOT, "strategy")):   # 폴더를 옮겨도 깨지지 않게 위로 찾는다
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, ROOT); os.chdir(ROOT)
from config.settings import PREMARKET_LEVELS_DB, RAW_DATA_DB, WEEKLY_OPTION_FLOW_DB
from strategy.shindong import daily_report as DR, spec as S, engine as E
FLOW = WEEKLY_OPTION_FLOW_DB if os.path.isabs(WEEKLY_OPTION_FLOW_DB) else os.path.join(ROOT, WEEKLY_OPTION_FLOW_DB)
PRE = ["2026-09-21", "2026-09-22", "2026-09-23", "2026-09-28", "2026-09-29", "2026-09-30"]
EVAL = ["2026-10-01", "2026-10-02", "2026-10-06", "2026-10-07", "2026-10-08", "2026-10-12", "2026-10-13",
        "2026-10-14", "2026-10-15", "2026-10-16"]
# 반사실 기대값(만원) — v3_candidates.py out_guardall.txt · rule12_check.py
EXP = {"MAIN": (986.9, 739.9), "SHADOW_V22": (897.7, 875.1), "SHADOW_V22S": (959.2, 875.1),
       "SHADOW_HYBL": (1017.5, 739.9), "SHADOW_FLOWR60": (736.9, 603.6), "SHADOW_BRKC": (291.2, 631.8)}
print("SPEC", S.SPEC_VERSION, "MAIN_FAMILY", S.MAIN_FAMILY, "VARIANTS", S.VARIANTS)
tot = {v: [0.0, 0.0] for v in S.VARIANTS}
daily = {v: {} for v in S.VARIANTS}
notes = {}
for day in PRE + EVAL:
    o = DR.load_day(day, RAW_DATA_DB, FLOW, PREMARKET_LEVELS_DB)
    if not o.get("ok"):
        print("skip", day); continue
    for v in S.VARIANTS:
        r = o["results"][v]
        net = sum(E.trade_net(t) for t in r["trades"] if t["status"] == "CLOSED")
        tot[v][0 if day in EVAL else 1] += net
        daily[v][day] = net
    notes[day] = [n for n in o["results"]["MAIN"]["decision"]["notes"] if "v3" in n or "손절" in n]
    if day in EVAL or day in PRE:
        print(day[5:], "MAIN", [(t["entry_ts"], t["side"], t.get("rule"), t["legs"][0].get("reason"),
                                round(E.trade_net(t) / 1e4, 1)) for t in o["results"]["MAIN"]["trades"]], notes[day])
bad = 0
print("\n변형 · 공식 평가/사전 · 기대 평가/사전")
for v in S.VARIANTS:
    e, p = tot[v][0] / 1e4, tot[v][1] / 1e4
    ok = abs(e - EXP[v][0]) < 0.11 and abs(p - EXP[v][1]) < 0.11
    bad += not ok
    print("  %-16s %8.1f %8.1f | %8.1f %8.1f %s" % (v, e, p, EXP[v][0], EXP[v][1], "OK" if ok else "❌ 불일치"))
print("\n불일치 변형 %d" % bad)
sys.exit(1 if bad else 0)
