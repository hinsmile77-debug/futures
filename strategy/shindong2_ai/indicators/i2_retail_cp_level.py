# -*- coding: utf-8 -*-
"""I2 — 개인 위클리 콜−풋 금액(백만원)의 09:00 대비 변화. 역추종 가설 — **상대(MAIN FLOWC)가 보는 바로 그 값**.

원천: `option_flow.db` `option_investor_flow`(7222, investor='individual', product=만기 최근접 위클리 콜/풋) — `strategy.shindong.runner.load_inputs`
와 같은 경로·같은 단위. MAIN 의 첫 거래 신호(K=300)가 여기서 나온다. AI 가 이 값을 지표로 들고 있어야 상대의 수를 읽고 반대할 수 있다.
"""
from __future__ import annotations

import datetime as _dt
import os
import sys
from typing import Dict, Optional

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
BASE_HM = "09:00"

META = dict(id="I2", title="개인 위클리 콜−풋 09:00 대비", source="내부: option_investor_flow individual 위클리(7222) — MAIN FLOWC 의 입력",
            hypothesis="개인이 콜을 사면(+) 이후 하락(역추종). MAIN 은 ±300 에서 켜진다 — AI 는 문턱 안쪽의 기울기·지속을 본다",
            inputs=["option_investor_flow"], unit="백만원", sign="contra",
            prereg=dict(min_days=20, hit_min=0.55, p_max=0.05))


def compute_from(sp: Dict[str, float], upto_hm: Optional[str], base_hm: str = BASE_HM) -> Optional[float]:
    """순수 함수 — sp = {HH:MM: 콜−풋}. 기준 = base_hm 값(없으면 그 이후 첫 값). upto 이하 마지막 값 − 기준."""
    if not sp:
        return None
    keys = sorted(k for k in sp if upto_hm is None or k <= upto_hm)
    if not keys:
        return None
    base_k = base_hm if base_hm in sp else next((x for x in sorted(sp) if x > base_hm), None)
    if base_k is None or base_k > keys[-1]:
        return None
    return round(sp[keys[-1]] - sp[base_k], 1)


def _frame(day: str, upto_hm: Optional[str]):
    from strategy.shindong import runner, engine
    from strategy.shindong.calendar import select_flow_product
    db = os.path.join(ROOT, "data", "db")
    product, _e, _n = select_flow_product(_dt.date.fromisoformat(day))
    candles, flow, _lv = runner.load_inputs(day, product, os.path.join(db, "raw_data.db"), os.path.join(db, "option_flow.db"),
                                            os.path.join(db, "premarket_levels.db"))
    if not candles:
        return None
    return engine.DayFrame(candles, flow, horizon=upto_hm)


def compute(day: str, upto_hm: Optional[str]) -> Optional[float]:
    d = _frame(day, upto_hm)
    if d is None:
        return None
    return compute_from(dict(d.sp), upto_hm)
