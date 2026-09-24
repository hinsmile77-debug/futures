# -*- coding: utf-8 -*-
"""신동이 볼 옵션 상품 — **만기가 가장 가까운 위클리**, 달력으로 정한다.

규칙(사전등록 1번 + 사용자 지시 2026-09-24 5번)
------------------------------------------------
· 후보 만기: 이번 주 월요일 만기 · 이번 주 목요일 만기 · 다음 주 월요일 만기 중
  **오늘 이후(오늘 포함)에서 가장 가까운 것.**
· 목요일 만기가 그달 **먼스리 만기(둘째 목요일)** 이면 그 주에는 목위클리가
  상장되지 않는다 → **먼스리(`mon`)로 대신한다.**
· 휴장 이동
  - 목요일(목위클리·먼스리): **직전 거래일**로 당긴다. 2026-09-24(추석) → 09-23 실측 확인.
  - 월요일(월위클리): **직후 거래일**로 순연한다. [2026-09-24 사용자 확인 — 확정]
    월요일 만기 위클리는 다른 파생상품과 반대로 다음 거래일로 미룬다
    (방증도 일치: 9/23 월위클리 거래량 4,538계약 — 만기일 9/21 은 147,405).
    예: 2026-10-05(개천절 대체공휴일) → 10-06.
    ⚠ 2026-09-28 은 휴장이 **아니다**(대체공휴일 오등록 정정, `config/krx_holidays.py`).

반환 상품키는 `option_flow.db:option_investor_flow.product` 의 접두어다
(`wk_mon` · `wk_thu` · `mon` → `_call`/`_put`).
"""
import datetime as _dt
from typing import Tuple

from config.krx_holidays import is_krx_holiday
from utils.time_utils import get_monthly_expiry_date


def _is_business_day(d: _dt.date) -> bool:
    return d.weekday() < 5 and not is_krx_holiday(d)


def _shift_back(d: _dt.date) -> _dt.date:
    while not _is_business_day(d):
        d -= _dt.timedelta(days=1)
    return d


def _shift_forward(d: _dt.date) -> _dt.date:
    while not _is_business_day(d):
        d += _dt.timedelta(days=1)
    return d


def thursday_expiry(week_monday: _dt.date) -> _dt.date:
    return _shift_back(week_monday + _dt.timedelta(days=3))


def monday_expiry(week_monday: _dt.date) -> _dt.date:
    return _shift_forward(week_monday)


def is_monthly_expiry_week(d: _dt.date) -> bool:
    """d 가 속한 주의 목요일 만기가 먼스리 만기인가."""
    mon = d - _dt.timedelta(days=d.weekday())
    thu = thursday_expiry(mon)
    return thu == get_monthly_expiry_date(thu.year, thu.month)


def select_flow_product(d: _dt.date) -> Tuple[str, _dt.date, str]:
    """(상품 접두어, 그 상품의 만기일, 사유 문구)."""
    mon = d - _dt.timedelta(days=d.weekday())
    cands = []
    m0 = monday_expiry(mon)
    if m0 >= d:
        cands.append((m0, "wk_mon"))
    t0 = thursday_expiry(mon)
    if t0 >= d:
        cands.append((t0, "thu"))
    nxt = mon + _dt.timedelta(days=7)
    cands.append((monday_expiry(nxt), "wk_mon"))
    t1 = thursday_expiry(nxt)
    cands.append((t1, "thu"))
    exp, kind = min(cands, key=lambda x: x[0])
    if kind == "thu":
        if exp == get_monthly_expiry_date(exp.year, exp.month):
            return "mon", exp, "먼스리 만기주 — 목위클리 대신 먼스리 (만기 %s)" % exp.isoformat()
        return "wk_thu", exp, "최근접 만기 목위클리 (만기 %s)" % exp.isoformat()
    return "wk_mon", exp, "최근접 만기 월위클리 (만기 %s)" % exp.isoformat()
