# -*- coding: utf-8 -*-
"""9/30 입력 로더 — 저장소 루트에서 실행. 읽기 전용."""
import os, sys, datetime as _dt
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, ROOT)
from config.settings import PREMARKET_LEVELS_DB, RAW_DATA_DB, WEEKLY_OPTION_FLOW_DB
from strategy.shindong import runner as RN, engine as E
from strategy.shindong.calendar import select_flow_product

FLOW = WEEKLY_OPTION_FLOW_DB if os.path.isabs(WEEKLY_OPTION_FLOW_DB) else os.path.join(ROOT, WEEKLY_OPTION_FLOW_DB)

def load(day):
    product, _, _ = select_flow_product(_dt.date.fromisoformat(day))
    c, f, lv = RN.load_inputs(day, product, RAW_DATA_DB, FLOW, PREMARKET_LEVELS_DB)
    if not c or "0850" not in lv:
        return None
    L = E.prepare_levels(lv)
    return E.DayFrame(c, f), L, product
