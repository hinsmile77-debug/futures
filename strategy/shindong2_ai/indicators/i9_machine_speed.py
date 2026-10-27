# -*- coding: utf-8 -*-
"""I9 — 「기계 속도」: 프로그램 비차익 **위탁** 순매수의 최근 10분 변화(억원/10분). 값 > 0 이면 이후 상승(추종) 가설.

피터리의 「기계매수·매도」를 계량화한 것이다(`docs/미륵이고도화3/피터2/피터_기계매수_정체_딥다이브_MW0601-20261027.md`).
10-27 실측: 외인 현물 ↔ 비차익 위탁 10분 Δ 상관 0.882 · 11:00–11:10 매수→매도 전환이 선물 고점(10:46)·외인 현물 정점(10:51)과 겹쳤다.
사전등록: `docs/미륵이고도화3/피터2/기계속도_사전등록_MW0601.json` (KS-2026-10-27-v1) — 정의·문턱은 거기가 정본이다.

원천: `raw_data.db raw_program_trade`(CpSvr8111 거래소 · 일중 누계 · 백만원) idx35 = 비차익 순매수 위탁금액.
  ⚠ idx17 은 서버 결함 — 쓰지 않는다. 시장 전체 합계이지 투자자별이 아니다(「위탁 = 외국인 바스켓」은 추론).
🔴 456차 — 하루치 ts 범위 조회 한 번(PK). 🔴 미측정은 None — 행이 없거나 2분 넘게 묵었으면 None.
"""
from __future__ import annotations

import json
import os
import sqlite3
from typing import Dict, Optional

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DB = os.path.join(ROOT, "data", "db", "raw_data.db")
FIELD_NA_CUST, FIELD_NA_BUY, FIELD_NA_SELL, FIELD_ARB = "35", "31", "25", "19"
FIRST, LAST = "09:02", "15:10"
STALE_MIN = 2

META = dict(id="I9", title="기계 속도(비차익 위탁 순매수 10분 변화)",
            source="내부: raw_program_trade idx35 (CpSvr8111) — docs/미륵이고도화3/피터2/피터_기계매수_정체_딥다이브_MW0601-20261027.md",
            hypothesis="피터의 기계매수(외국인 비차익 바스켓)가 들어오는 속도가 +면 이후 상승, -면 하락(사전등록 KS-2026-10-27-v1 H-K1)",
            inputs=["raw_program_trade"], unit="억원/10분", sign="follow",
            prereg=dict(min_days=20, hit_min=0.55, p_max=0.05))


def _hm(t):
    return int(t[:2]) * 60 + int(t[3:5])


def load_series(day: str, upto_hm: Optional[str] = None, db: str = DB) -> Dict[str, dict]:
    """{HH:MM: {na, buy, sell, arb}} — 일중 누계(백만원). upto 이하만(미래 참조 금지)."""
    if not os.path.exists(db):
        return {}
    hi = upto_hm or LAST
    con = sqlite3.connect("file:%s?mode=ro" % db.replace("\\", "/"), uri=True, timeout=5.0)
    try:
        rows = con.execute("SELECT ts, fields FROM raw_program_trade WHERE market='1' AND ts>=? AND ts<=? ORDER BY ts",
                           ("%s %s:00" % (day, FIRST), "%s %s:59" % (day, hi))).fetchall()
    finally:
        con.close()
    out = {}
    for ts, f in rows:
        try:
            j = json.loads(f)
        except ValueError:
            continue
        out[ts[11:16]] = dict(na=j.get(FIELD_NA_CUST), buy=j.get(FIELD_NA_BUY), sell=j.get(FIELD_NA_SELL), arb=j.get(FIELD_ARB))
    return out


def value_at(series: Dict[str, dict], t: str, key: str = "na", stale: int = STALE_MIN) -> Optional[float]:
    """t 이하 마지막 값. 그 행이 t 보다 stale 분 넘게 이르면 None(미측정)."""
    ks = [k for k in series if k <= t and series[k].get(key) is not None]
    if not ks:
        return None
    k = max(ks)
    if _hm(t) - _hm(k) > stale:
        return None
    return float(series[k][key])


def speed(series: Dict[str, dict], t: str, key: str = "na", window: int = 10) -> Optional[float]:
    """(값(t) − 값(t − window)) / 100 [억원]. 어느 한쪽이 미측정이면 None."""
    if _hm(t) - window < _hm(FIRST) or t > LAST:
        return None
    t0 = "%02d:%02d" % divmod(_hm(t) - window, 60)
    a, b = value_at(series, t, key), value_at(series, t0, key)
    if a is None or b is None:
        return None
    return round((a - b) / 100.0, 1)


def compute(day: str, upto_hm: Optional[str]) -> Optional[float]:
    t = min(upto_hm or LAST, LAST)
    return speed(load_series(day, t), t)
