# -*- coding: utf-8 -*-
"""BRKC 재생 — 그날 08:50/09:30 구조맥점, 가격 범위, 맥점 종가 교차(전 방향·R1 방향) 이벤트를 출력.
읽기 전용(DB 쓰기 없음). 장 마감 후 실행.
사용: conda run -n py37_32 python brk_replay.py 2026-10-13 ..."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))  # repo 루트
sys.path.insert(0, ROOT); os.chdir(ROOT)
from config.settings import PREMARKET_LEVELS_DB, RAW_DATA_DB, WEEKLY_OPTION_FLOW_DB
from strategy.shindong import daily_report as DR, engine as E, spec as S
flow = WEEKLY_OPTION_FLOW_DB if os.path.isabs(WEEKLY_OPTION_FLOW_DB) else os.path.join(ROOT, WEEKLY_OPTION_FLOW_DB)
for day in sys.argv[1:]:
    o = DR.load_day(day, RAW_DATA_DB, flow, PREMARKET_LEVELS_DB)
    L, d = o["L"], o["d"]
    bias = o["results"]["SHADOW_BRKC"]["decision"]["bias"]
    s0 = L["0850"]["S"]; s9 = L.get("0930", {}).get("S", [])
    idx = [k for k in d.idx if k in d.c and "09:00" <= k <= S.FLOW_LAST_ENTRY]
    cs = [d.c[k] for k in idx]
    print("=====", day, "bias", bias, "product", o["product"])
    print(" 0850 S n=%d" % len(s0), [round(x, 2) for x in s0])
    print(" 0930 S n=%d" % len(s9), [round(x, 2) for x in s9])
    print(" first close %s %.2f  range %.2f~%.2f  last %.2f" % (idx[0], cs[0], min(cs), max(cs), cs[-1]))
    allS = sorted(set(s0 + s9))
    print(" levels inside day close-range:", [round(x,2) for x in allS if min(cs) <= x <= max(cs)])
    # all crossings, both directions, ignoring busy
    prev = None; ev = []
    for k in idx:
        _, lv = E.levels_at(L, k); c = d.c[k]
        if prev is not None:
            for x in lv:
                sd = -1 if (prev >= x > c) else (1 if (prev <= x < c) else 0)
                if sd: ev.append((k, sd, round(x, 2), round(prev, 2), round(c, 2)))
        prev = c
    print(" crossings(all) n=%d  bias-dir n=%d" % (len(ev), sum(1 for e in ev if e[1] == bias)))
    for e in ev[:12]: print("   ", e)
    # 09:00 open vs 08:59 premarket close (gap)
    pre = [k for k in d.idx if k < "09:00" and k in d.c]
    print(" pre-09 last close:", (pre[-1], d.c[pre[-1]]) if pre else None)
    print(" BRKC trades:", [(t["entry_ts"], t["side"], t.get("touch_level")) for t in o["results"]["SHADOW_BRKC"]["trades"]])
