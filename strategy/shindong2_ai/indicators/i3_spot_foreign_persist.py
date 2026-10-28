# -*- coding: utf-8 -*-
"""I3 — 현물(KOSPI) 외인 누계 부호의 **지속성**: 개장 이후 upto 까지 누계 부호가 현재 부호와 같았던 분의 비율 × 현재 부호. [−1, +1].

원천: `option_flow.db` `option_investor_flow`(7222, product='kospi_spot', investor='foreign', **net_amt** 백만원). 미륵이가 1분마다 수집.
[v2 · 2026-10-28 MW0602 670차 후속3 · F3] v1 은 net_qty(주식 수)였다 — 종목마다 가격이 달라 수량 부호가 방향을 말하지 않는다
  (9/21–10/28 외인 장중 행 32% 부호 갈림). 금액은 정규장 보도와 일치. 데드존 DEAD_AMT = 9,350백만 — |누계| 가 이보다 작으면
  부호 없음(개장 직후 0 근처 흔들림만 거른다 · PIT 복기 S1 과 같은 값, 손익 미참조). 9/21–10/28 은 v2 정의를 탐색할 때 본 날이라
  판정 표본에서 뺀다(prereg.since).
근거: L2·L7·L22 — AI 레슨이 반복해서 「현물 외인 수준이 대장」이라 했는데(10/7·10/8·10/20) 그것을 정의된 숫자로 잰 적이 없다.
MAIN 은 이 축을 보지 않는다 → 상대와 **다른 입력**이라 반대일의 근거가 될 수 있다.
"""
from __future__ import annotations

import os
import sqlite3
from typing import List, Optional, Tuple

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
FLOW_DB = os.environ.get("SHINDONG2_FLOW_DB") or os.path.join(ROOT, "data", "db", "option_flow.db")

META = dict(id="I3", title="현물 외인 누계 부호 지속", source="내부: option_investor_flow kospi_spot foreign (7222) · 레슨 L2/L7/L22 의 「대장」 축",
            hypothesis="현물 외인 누계가 개장 내내 한 부호면 그 방향이 종가까지 간다(순추종). 부호가 뒤집힌 날은 0 근처 — 관망 근거",
            inputs=["option_investor_flow"], unit="비율×부호", sign="follow", version="I3-2026-10-28-v2(금액)",
            prereg=dict(min_days=20, hit_min=0.55, p_max=0.05, since="2026-10-29"))
DEAD_AMT = 9350      # 백만원 — 위 v2 주석


def series(day: str, upto_hm: Optional[str], db: str = FLOW_DB) -> List[Tuple[str, float]]:
    if not os.path.exists(db):
        return []
    con = sqlite3.connect("file:%s?mode=ro" % db.replace("\\", "/"), uri=True, timeout=5.0)
    try:
        rows = con.execute("SELECT bar_time, net_amt FROM option_investor_flow WHERE trade_date=? AND product='kospi_spot' AND investor='foreign'"
                           " AND net_amt IS NOT NULL AND bar_time>='09:00' AND bar_time<=? ORDER BY bar_time",
                           (day, upto_hm or "23:59")).fetchall()
    except sqlite3.OperationalError:
        return []
    finally:
        con.close()
    return [(str(t)[:5], float(v)) for t, v in rows]


def compute_from(ser: List[Tuple[str, float]], upto_hm: Optional[str], min_n: int = 10, dead: float = 0) -> Optional[float]:
    """순수 함수. 표본 min_n 미만이면 None(소표본 노이즈 — 미측정). |값| < dead 인 분은 부호 없음(분자에서 빠지고 분모에는 남는다)."""
    pts = [(t, v) for t, v in ser if upto_hm is None or t <= upto_hm]
    if len(pts) < min_n:
        return None
    cur = pts[-1][1]
    if cur == 0 or abs(cur) < dead:
        return 0.0
    sgn = 1 if cur > 0 else -1
    same = sum(1 for _t, v in pts if (v > 0) == (cur > 0) and v != 0 and abs(v) >= dead)
    return round(sgn * same / len(pts), 2)


def compute(day: str, upto_hm: Optional[str]) -> Optional[float]:
    return compute_from(series(day, upto_hm), upto_hm, dead=DEAD_AMT)
