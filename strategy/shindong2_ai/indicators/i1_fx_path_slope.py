# -*- coding: utf-8 -*-
"""I1 — 외국인 선물 순매수 누적의 최근 60분 변화(계약). 순추종 가설.

원천: `raw_data.db` `raw_investor_futures.fields.foreign_net_qty`(7221 정규 K200 선물, 미륵이가 분당 수집).
근거: 683차 외인 동향 블록이 「경로」를 보라고 했고, HYBL 의 FX 축(K=400)이 같은 값을 쓴다 — 상대가 보는 축을 AI 도 같은 정의로 재서
상대와 **같은 입력에서 다른 결론**을 낼 수 있는지 본다.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import sqlite3
from typing import Dict, Optional

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
RAW_DB = os.environ.get("SHINDONG2_RAW_DB") or os.path.join(ROOT, "data", "db", "raw_data.db")
WIN_MIN = 60

META = dict(id="I1", title="외인 선물 60분 변화", source="내부: raw_investor_futures.foreign_net_qty (7221) · HYBL FX 축과 같은 정의",
            hypothesis="최근 60분 외인 선물 순매수가 +면 이후 상승(순추종). 외인 선물은 가격을 1분 뒤따르므로(L1) 신호가 아니라 지속성 가설",
            inputs=["raw_investor_futures"], unit="계약", sign="follow",
            prereg=dict(min_days=20, hit_min=0.55, p_max=0.05))


def series(day: str, upto_hm: Optional[str], db: str = RAW_DB) -> Dict[str, float]:
    """{HH:MM: foreign_net_qty} — upto 이하만. DB 없으면 빈 dict(미측정)."""
    if not os.path.exists(db):
        return {}
    hi = "%s %s:59" % (day, upto_hm) if upto_hm else "%s 23:59:59" % day
    con = sqlite3.connect("file:%s?mode=ro" % db.replace("\\", "/"), uri=True, timeout=5.0)
    try:
        rows = con.execute("SELECT ts, fields FROM raw_investor_futures WHERE ts >= ? AND ts <= ? ORDER BY ts",
                           (day + " 00:00:00", hi)).fetchall()
    except sqlite3.OperationalError:
        return {}
    finally:
        con.close()
    out = {}
    for ts, f in rows:
        try:
            v = json.loads(f).get("foreign_net_qty")
        except (TypeError, ValueError):
            v = None
        if v is not None:
            out[str(ts)[11:16]] = float(v)
    return out


def compute_from(ser: Dict[str, float], upto_hm: Optional[str], win: int = WIN_MIN) -> Optional[float]:
    """순수 함수 — 검증·테스트가 직접 부른다. upto 의 값 − (upto−win) 이전 마지막 값. 창이 09:00 전이면 None."""
    if not ser:
        return None
    keys = sorted(k for k in ser if upto_hm is None or k <= upto_hm)
    if not keys:
        return None
    k = keys[-1]
    t = _dt.datetime.strptime(k, "%H:%M") - _dt.timedelta(minutes=win)
    rk = t.strftime("%H:%M")
    if rk < "09:00":
        return None
    base = [x for x in keys if x <= rk]
    if not base:
        # 7221 첫 수신이 09:00 을 조금 지나는 날이 많다(09:02 앵커). rk 뒤 5분 안의 첫 값은 기준으로 허용 — 그 밖이면 미측정.
        lim = (t + _dt.timedelta(minutes=5)).strftime("%H:%M")
        early = [x for x in keys if rk < x <= lim and x < k]
        if not early:
            return None
        base = [early[0]]
    return round(ser[k] - ser[base[-1]], 0)


def compute(day: str, upto_hm: Optional[str]) -> Optional[float]:
    return compute_from(series(day, upto_hm), upto_hm)
