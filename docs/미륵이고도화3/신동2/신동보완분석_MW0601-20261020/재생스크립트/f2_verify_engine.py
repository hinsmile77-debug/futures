# -*- coding: utf-8 -*-
"""[719차] 구현 엔진 SHADOW_F2 22일 재생 = 분석(V2+F2 · f2_final ①SHADOW_F2) 원 단위 대조. 장후 전용 · 읽기 전용."""
import sys, os, json, time, datetime as dt
ROOT = r"C:\Users\82108\PycharmProjects\futures"; sys.path.insert(0, ROOT)
from utils.analysis_db import guard_intraday
guard_intraday("f2_verify_engine")
from strategy.shindong import engine as E, runner, spec as S
from strategy.shindong.calendar import select_flow_product
DB = os.path.join(ROOT, "data", "db"); P = [os.path.join(DB, x) for x in ("raw_data.db", "option_flow.db", "premarket_levels.db")]
ref = json.load(open(sys.argv[1], encoding="utf-8"))
D = ref["days"]; R = ref["trades"]
pairs = (("SHADOW_F2", "①SHADOW_F2"), ("MAIN", "②SHADOW_F2X"), ("SHADOW_V3", "인과 MAIN"))
tot = {v: 0.0 for v, _ in pairs}; bad = 0; tsum = 0.0; nrun = 0
for d0 in D:
    prod = select_flow_product(dt.date.fromisoformat(d0))[0]
    c, f, l = runner.load_inputs(d0, prod, *P)
    L = E.prepare_levels(l); d = E.DayFrame(c, f)
    row = [d0[5:]]
    for v, k in pairs:
        t0 = time.perf_counter(); res = E.run_day(d, L, v); tsum += time.perf_counter() - t0; nrun += 1
        got = sum(E.trade_net(x) for x in res["trades"] if x["status"] == "CLOSED")
        exp = sum(x["l1"] + x["l2"] for x in R[k][d0])
        tot[v] += got; ok = abs(got - exp) < 1; bad += (not ok)
        row.append("%s %+8.1f/%+8.1f%s" % (v, got / 1e4, exp / 1e4, "" if ok else " ✗"))
    print(" | ".join(row))
print("합계", {v: round(x / 1e4, 1) for v, x in tot.items()}, "불일치", bad, "· run_day 평균 %.1fms" % (1000 * tsum / nrun))
