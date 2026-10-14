# -*- coding: utf-8 -*-
"""BRKC 반사실 — 09:30 오프닝 레인지 고·저(OR고/OR저)가 ±1pt 무효대·근접 3개 제한으로 0930 맥점에서
빠진 날, 그 값을 넣었을 때 BRKC 거래가 어떻게 바뀌는가(근처 맥점에 병합돼 이미 있는 OR 은 그대로). 읽기 전용(DB 쓰기 없음). 장 마감 후 실행.
사용: conda run -n py37_32 python brk_cf.py 2026-10-01 2026-10-13 ..."""
import os, sys, copy
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))  # repo 루트
sys.path.insert(0, ROOT); os.chdir(ROOT)
from config.settings import PREMARKET_LEVELS_DB, RAW_DATA_DB, WEEKLY_OPTION_FLOW_DB
from strategy.shindong import daily_report as DR, families as F
flow = WEEKLY_OPTION_FLOW_DB if os.path.isabs(WEEKLY_OPTION_FLOW_DB) else os.path.join(ROOT, WEEKLY_OPTION_FLOW_DB)
tot0 = tot1 = 0
for day in sys.argv[1:]:
    o = DR.load_day(day, RAW_DATA_DB, flow, PREMARKET_LEVELS_DB)
    L, d = o["L"], o["d"]; v1 = o["results"]["SHADOW_V1"]["decision"]
    base = F.run_family_day(d, L, "brkc", v1_decision=v1)
    L2 = copy.deepcopy(L); z = L2.get("0930")
    added = []
    if z and z.get("sofar_low") is not None:
        # 이미 근처 맥점에 병합돼 들어간 OR(태그 "OR저"/"OR고" 존재)은 건드리지 않는다 —
        # 무효대(±1pt)·근접 3개 제한으로 **아예 빠진** 경우만 원값을 추가한다.
        tags = [t for x in z["_up"] + z["_dn"] for t in x[1]]
        for name, x in (("OR저", z["sofar_low"]), ("OR고", z["sofar_high"])):
            if not any(t.startswith(name) for t in tags):
                x = int(round(x))
                z["S"] = sorted(set(z["S"] + [x])); added.append((name, x))
    cf = F.run_family_day(d, L2, "brkc", v1_decision=v1)
    f = lambda r: [(t["entry_ts"], t["side"], round(t["entry_px"],2), t["legs"][0].get("reason"), round(t["legs"][0].get("pts") or 0,2), round(sum(g.get("net") or 0 for g in t["legs"])/1e4,1)) for t in r["trades"]]
    n0 = sum(sum(g.get("net") or 0 for g in t["legs"]) for t in base["trades"]); n1 = sum(sum(g.get("net") or 0 for g in t["legs"]) for t in cf["trades"])
    tot0 += n0; tot1 += n1
    print("=====", day, "added OR levels", added, "base %.1f만 -> cf %.1f만" % (n0/1e4, n1/1e4))
    print("  base", f(base)); print("  cf  ", f(cf))
print("TOTAL base %.1f만 cf %.1f만" % (tot0/1e4, tot1/1e4))
