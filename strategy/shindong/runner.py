# -*- coding: utf-8 -*-
"""신동 실행기 — 원천 DB 3곳을 읽어 엔진을 돌리고 `shindong.db` 에 쓴다.

호출 경로
---------
· 라이브: `main.py:_fetch_weekly_option_flow` — 위클리 흐름 수집 **직후**, 같은 QTimer
  경로에서 분당 1회. 새 타이머를 만들지 않는다(617차 슬롯 래칫). COM 콜백 밖이다(§4).
· 백필·복기: `scripts/shindong_backfill.py`

비용(2026-09-24 실측, 9/21–9/23 분 단위 재생 383회×3일): 1회 평균 약 30ms · 최대 68ms.
하루치 봉 약 380행 + 흐름 약 800행 인덱스 조회 + 재생 2변형.
장중 분석 금지 규약(456차)의 대상은 **전수 스캔**이다 — 여기는 그날 하루만 읽는다.
"""
import datetime as _dt
import logging
import os
import sqlite3
from typing import Any, Dict, List, Optional, Tuple

from strategy.shindong import engine, spec, store
from strategy.shindong.calendar import select_flow_product

logger = logging.getLogger("TRADE")


def _ro(path: str) -> sqlite3.Connection:
    con = sqlite3.connect("file:%s?mode=ro" % path.replace("\\", "/"), uri=True, timeout=5.0)
    con.row_factory = sqlite3.Row
    return con


def load_inputs(trade_date: str, product: str, raw_db: str, flow_db: str, levels_db: str):
    """(candles, flow, levels_rows). 없으면 빈 dict — 0 으로 메우지 않는다."""
    nxt = (_dt.date.fromisoformat(trade_date) + _dt.timedelta(days=1)).isoformat()
    candles: Dict[str, Tuple[float, float, float, float]] = {}
    con = _ro(raw_db)
    try:
        for r in con.execute(
                "SELECT ts,open,high,low,close FROM raw_candles WHERE ts>=? AND ts<? ORDER BY ts",
                (trade_date, nxt)):
            candles[str(r["ts"])[11:16]] = (float(r["open"]), float(r["high"]),
                                           float(r["low"]), float(r["close"]))
    finally:
        con.close()
    flow: Dict[str, List[Optional[float]]] = {}
    if os.path.exists(flow_db):
        con = _ro(flow_db)
        try:
            for r in con.execute(
                    "SELECT bar_time,product,net_amt FROM option_investor_flow "
                    "WHERE trade_date=? AND investor='individual' AND product IN (?,?)",
                    (trade_date, product + "_call", product + "_put")):
                slot = flow.setdefault(r["bar_time"], [None, None])
                if r["net_amt"] is None:
                    continue           # 미측정 — 0 으로 메우지 않는다
                slot[0 if r["product"].endswith("_call") else 1] = float(r["net_amt"])
        finally:
            con.close()
    levels: Dict[str, Dict[str, Any]] = {}
    if os.path.exists(levels_db):
        con = _ro(levels_db)
        try:
            for r in con.execute("SELECT * FROM premarket_levels WHERE date=?", (trade_date,)):
                levels[r["stage"]] = dict(r)
        finally:
            con.close()
    return candles, {k: tuple(v) for k, v in flow.items()}, levels


def compute(trade_date: str, raw_db: str, flow_db: str, levels_db: str,
            now: Optional[_dt.datetime] = None, live: bool = False):
    """변형별 결과. 반환 {"product","product_note","horizon","last_close","results":{variant:res}}."""
    d0 = _dt.date.fromisoformat(trade_date)
    product, _exp, note = select_flow_product(d0)
    candles, flow, lvrows = load_inputs(trade_date, product, raw_db, flow_db, levels_db)
    horizon = None
    if live:
        # 봉·흐름이 **둘 다** 도착한 마지막 분, 그리고 진행 중인 분은 제외한다.
        # 흐름 원천은 진행 중인 분의 부분 누계를 준다(621차 후속 실측 — :02 초 수집).
        now = now or _dt.datetime.now()
        cur = (now - _dt.timedelta(minutes=1)).strftime("%H:%M")
        cands = [cur]
        if candles:
            cands.append(max(candles))
        if flow:
            cands.append(max(flow))
        horizon = min(cands) if candles else None
    out = {"product": product, "product_note": note, "horizon": horizon,
           "last_close": None, "results": {}}
    if not candles or not lvrows or "0850" not in lvrows:
        why = "봉 없음" if not candles else "08:50 맥점 없음"
        for v in spec.VARIANTS:
            out["results"][v] = {"decision": {"notes": [why]}, "trades": []}
        return out
    L = engine.prepare_levels(lvrows)
    d = engine.DayFrame(candles, flow, horizon=horizon)
    if d.idx:
        out["last_close"] = d.c.get(d.idx[-1])
        out["horizon"] = d.idx[-1]
    for v in spec.VARIANTS:
        out["results"][v] = engine.run_day(d, L, v)
    return out


def run_and_store(trade_date: str, raw_db: str, flow_db: str, levels_db: str, sd_db: str,
                  now: Optional[_dt.datetime] = None, live: bool = True) -> Dict[str, Any]:
    """계산 → 저장 → 차트용 MAIN 목록 반환."""
    r = compute(trade_date, raw_db, flow_db, levels_db, now=now, live=live)
    for v, res in r["results"].items():
        store.save_day(sd_db, trade_date, v, r["product"], r["product_note"], res,
                       r["horizon"], spec.SPEC_VERSION,
                       source="live" if live else "backfill",
                       detect_px=r["last_close"], now=now)
    return {"trade_date": trade_date, "product": r["product"],
            "product_note": r["product_note"], "horizon": r["horizon"],
            "decision": r["results"]["MAIN"]["decision"],
            "trades": store.load_trades(sd_db, trade_date, "MAIN")}
