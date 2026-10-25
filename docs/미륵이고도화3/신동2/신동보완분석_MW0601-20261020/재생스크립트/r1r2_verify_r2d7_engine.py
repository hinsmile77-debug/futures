# -*- coding: utf-8 -*-
import sys, os, datetime as dt
ROOT = r"C:\Users\82108\PycharmProjects\futures"; sys.path.insert(0, ROOT)
from config.settings import PREMARKET_LEVELS_DB, RAW_DATA_DB, WEEKLY_OPTION_FLOW_DB
from strategy.shindong import engine as E, runner as R
from strategy.shindong.calendar import select_flow_product
F = os.path.join(ROOT, WEEKLY_OPTION_FLOW_DB)
tot = {"MAIN": [0, 0], "SHADOW_R2D7": [0, 0]}
for day in sys.argv[1].split(","):
    p, _, _ = select_flow_product(dt.date.fromisoformat(day))
    c, f, lv = R.load_inputs(day, p, RAW_DATA_DB, F, PREMARKET_LEVELS_DB)
    d, L = E.DayFrame(c, f), E.prepare_levels(lv)
    for v in tot:
        tr = E.run_day(d, L, v)["trades"]
        tot[v][0] += sum(E.trade_net(t) for t in tr if t["rule"] == "R2")
        tot[v][1] += sum(E.trade_net(t) for t in tr)
for v, (a, b) in tot.items():
    print(v, "R2 %+.1f만 total %+.1f만" % (a / 1e4, b / 1e4))
