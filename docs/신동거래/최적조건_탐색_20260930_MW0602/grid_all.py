# -*- coding: utf-8 -*-
"""같은 격자를 맥점이 있는 전 거래일에 돌린다(표본 밖 점검).  출력: grid_all.json(약 150MB · 약 12분 — 커밋하지 말 것) {day: {fam: [net,...]}}
조합 순서는 grid.run 과 같다 — 같은 인덱스 = 같은 파라미터(9/30 기준 ps 목록 동봉)."""
import json, os, sqlite3, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import grid
from load import ROOT
from config.settings import PREMARKET_LEVELS_DB

days = [r[0] for r in sqlite3.connect(PREMARKET_LEVELS_DB).execute(
    "select distinct date from premarket_levels where stage='0850' order by date")]
out = {}
for day in days:
    r = grid.run(day)
    if r is None:
        continue
    out[day] = {"bias": r["bias"], "fam": {f: [[json.dumps(z["p"], sort_keys=True), round(z["net"]), z["n"]] for z in rows]
                                           for f, rows in r["fam"].items()}}
    print(day, r["bias"], {f: len(v) for f, v in r["fam"].items()}, flush=True)
json.dump(out, open(os.path.join(HERE, "grid_all.json"), "w", encoding="utf-8"), ensure_ascii=False)
