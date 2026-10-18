# -*- coding: utf-8 -*-
import os, sys, datetime as dt
ROOT = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(ROOT, "strategy")):   # 폴더를 옮겨도 깨지지 않게 위로 찾는다
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, ROOT); os.chdir(ROOT)
from config.settings import PREMARKET_LEVELS_DB, RAW_DATA_DB, WEEKLY_OPTION_FLOW_DB
from strategy.shindong import runner as RN, daily_report as DR
FLOW = WEEKLY_OPTION_FLOW_DB if os.path.isabs(WEEKLY_OPTION_FLOW_DB) else os.path.join(ROOT, WEEKLY_OPTION_FLOW_DB)
d = dt.date(2026, 6, 1)
while d <= dt.date(2026, 10, 16):
    if d.weekday() < 5:
        s = d.isoformat()
        prod, _e, _n = DR.select_flow_product(d)
        c, f, lv = RN.load_inputs(s, prod, RAW_DATA_DB, FLOW, PREMARKET_LEVELS_DB)
        fx = RN.load_fx(s, RAW_DATA_DB)
        if c:
            print(s, "bars", len(c), "flow", len(f), "fx", len(fx), "lv0850", "0850" in lv)
    d += dt.timedelta(days=1)
