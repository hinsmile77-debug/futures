# -*- coding: utf-8 -*-
"""신동 기록 — `data/db/shindong.db`.

🔴 **가상거래 전용 DB 다.** `trades.db` 에 섞지 않는다 — 섞으면 브로커 대사·
  전환기준 ①·수수료 재환산이 전부 오염된다(GP 섀도가 `challenger.db` 를 따로 쓴 것과
  같은 이유, 553차 검토문서 §5-4).

테이블
------
shindong_trades : 거래 1건 = 1행. 다리(1차·최종) 결과를 같은 행에 싣는다.
shindong_day    : 날짜 × 변형별 판정 기록(R1 장전 · R2 확정 · 상품 선택 사유).

재생 설계라 매분 같은 거래를 다시 쓴다. 그래서
· `detected_at` 은 **처음 본 시각만** 남긴다 — 규칙가(진입봉 종가)와 실제 알아챈 시각의
  차이가 곧 「실시간으로 가능했는가」다(계측 4원칙 ④).
· 재계산에서 사라진 거래는 지우지 않고 `RETRACTED` 로 남긴다 — 원천 값이 나중에 바뀌어
  신호가 뒤집힌 사실 자체가 기록이다.
"""
import datetime as _dt
import os
import sqlite3
from typing import Any, Dict, List, Optional

_SCHEMA = (
    """CREATE TABLE IF NOT EXISTS shindong_trades (
        trade_date   TEXT NOT NULL,
        variant      TEXT NOT NULL,          -- MAIN | SHADOW_E2F2
        trade_key    TEXT NOT NULL,          -- rule|entry_ts|side
        rule         TEXT NOT NULL,          -- R2 | R3
        side         INTEGER NOT NULL,       -- +1 매수 / -1 매도
        product      TEXT,                   -- wk_mon | wk_thu | mon
        entry_ts     TEXT NOT NULL,          -- YYYY-MM-DD HH:MM:00 (진입봉)
        entry_px     REAL NOT NULL,          -- 규칙가 = 진입봉 종가
        stop_init    REAL,
        stop_now     REAL,
        t1           REAL,
        t2           REAL,
        touch_level  REAL,                   -- R3 만
        touch_ts     TEXT,
        status       TEXT NOT NULL,          -- OPEN | CLOSED | RETRACTED
        leg1_exit_ts TEXT, leg1_exit_px REAL, leg1_reason TEXT, leg1_pts REAL, leg1_net REAL,
        leg2_exit_ts TEXT, leg2_exit_px REAL, leg2_reason TEXT, leg2_pts REAL, leg2_net REAL,
        net_krw      REAL,                   -- 닫힌 다리 합(2계약). 보유 중 다리는 미포함
        detected_at  TEXT,                   -- 처음 기록한 벽시계(라이브). 백필은 NULL
        detect_px    REAL,                   -- 처음 기록 시점의 최신 종가 — 실현가능가
        source       TEXT,                   -- live | backfill
        spec_version TEXT,
        updated_at   TEXT NOT NULL,
        PRIMARY KEY (trade_date, variant, trade_key)
    )""",
    """CREATE TABLE IF NOT EXISTS shindong_day (
        trade_date   TEXT NOT NULL,
        variant      TEXT NOT NULL,
        product      TEXT,
        product_note TEXT,
        pm_sp        REAL,                   -- 08:59 콜−풋 금액(백만원). NULL = 미수집
        bias         INTEGER,                -- -1 하방 / 0 보류 / +1 상방
        r2_status    TEXT,                   -- CONFIRMED | NONE | PENDING | NO_BASE | NULL(편향 없음)
        r2_ts        TEXT,
        horizon      TEXT,                   -- 이번 계산이 본 마지막 분
        notes        TEXT,
        spec_version TEXT,
        updated_at   TEXT NOT NULL,
        PRIMARY KEY (trade_date, variant)
    )""",
)


def connect(db_path: str) -> sqlite3.Connection:
    d = os.path.dirname(db_path)
    if d:
        os.makedirs(d, exist_ok=True)
    con = sqlite3.connect(db_path, timeout=5.0)
    con.row_factory = sqlite3.Row
    for s in _SCHEMA:
        con.execute(s)
    return con


def _leg_cols(g: Dict[str, Any], ts_prefix: str):
    if g.get("open", True):
        return (None, None, None, None, None)
    return (ts_prefix + g["ts"] + ":00", g["px"], g["reason"], g["pts"], g["net"])


def save_day(db_path: str, trade_date: str, variant: str, product: str, product_note: str,
             result: Dict[str, Any], horizon: Optional[str], spec_version: str,
             source: str = "live", detect_px: Optional[float] = None,
             now: Optional[_dt.datetime] = None) -> None:
    now_s = (now or _dt.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    pre = trade_date + " "
    dec = result["decision"]
    con = connect(db_path)
    try:
        with con:
            con.execute(
                """INSERT INTO shindong_day(trade_date,variant,product,product_note,pm_sp,bias,
                       r2_status,r2_ts,horizon,notes,spec_version,updated_at)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(trade_date,variant) DO UPDATE SET
                       product=excluded.product, product_note=excluded.product_note,
                       pm_sp=excluded.pm_sp, bias=excluded.bias, r2_status=excluded.r2_status,
                       r2_ts=excluded.r2_ts, horizon=excluded.horizon, notes=excluded.notes,
                       spec_version=excluded.spec_version, updated_at=excluded.updated_at""",
                (trade_date, variant, product, product_note, dec.get("pm_sp"), dec.get("bias"),
                 dec.get("r2"), dec.get("r2_ts"), horizon, " / ".join(dec.get("notes") or []),
                 spec_version, now_s))
            keys = []
            for tr in result["trades"]:
                key = "%s|%s|%+d" % (tr["rule"], tr["entry_ts"], tr["side"])
                keys.append(key)
                l1 = _leg_cols(tr["legs"][0], pre)
                l2 = _leg_cols(tr["legs"][1], pre)
                net = sum(g.get("net", 0.0) for g in tr["legs"] if not g.get("open", True))
                con.execute(
                    """INSERT INTO shindong_trades(trade_date,variant,trade_key,rule,side,product,
                           entry_ts,entry_px,stop_init,stop_now,t1,t2,touch_level,touch_ts,status,
                           leg1_exit_ts,leg1_exit_px,leg1_reason,leg1_pts,leg1_net,
                           leg2_exit_ts,leg2_exit_px,leg2_reason,leg2_pts,leg2_net,
                           net_krw,detected_at,detect_px,source,spec_version,updated_at)
                       VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                       ON CONFLICT(trade_date,variant,trade_key) DO UPDATE SET
                           stop_now=excluded.stop_now, t1=excluded.t1, t2=excluded.t2,
                           status=excluded.status,
                           leg1_exit_ts=excluded.leg1_exit_ts, leg1_exit_px=excluded.leg1_exit_px,
                           leg1_reason=excluded.leg1_reason, leg1_pts=excluded.leg1_pts,
                           leg1_net=excluded.leg1_net,
                           leg2_exit_ts=excluded.leg2_exit_ts, leg2_exit_px=excluded.leg2_exit_px,
                           leg2_reason=excluded.leg2_reason, leg2_pts=excluded.leg2_pts,
                           leg2_net=excluded.leg2_net, net_krw=excluded.net_krw,
                           spec_version=excluded.spec_version, updated_at=excluded.updated_at""",
                    (trade_date, variant, key, tr["rule"], tr["side"], product,
                     pre + tr["entry_ts"] + ":00", tr["entry_px"], tr["stop_init"], tr["stop_now"],
                     tr["t1"], tr["t2"], tr.get("touch_level"),
                     (pre + tr["touch_ts"] + ":00") if tr.get("touch_ts") else None,
                     tr["status"]) + l1 + l2 +
                    (net,
                     now_s if source == "live" else None,
                     detect_px if source == "live" else None,
                     source, spec_version, now_s))
            # 이번 계산에서 사라진 거래 — 지우지 않고 표시만 한다
            if keys:
                q = ("UPDATE shindong_trades SET status='RETRACTED', updated_at=? "
                     "WHERE trade_date=? AND variant=? AND status!='RETRACTED' "
                     "AND trade_key NOT IN (%s)" % ",".join("?" * len(keys)))
                con.execute(q, [now_s, trade_date, variant] + keys)
            else:
                con.execute("UPDATE shindong_trades SET status='RETRACTED', updated_at=? "
                            "WHERE trade_date=? AND variant=? AND status!='RETRACTED'",
                            (now_s, trade_date, variant))
    finally:
        con.close()


def load_trades(db_path: str, trade_date: str, variant: str = "MAIN",
                include_retracted: bool = False) -> List[Dict[str, Any]]:
    """차트·채점용. DB 가 없으면 빈 목록(「미배선」 판정은 호출자가 `is_wired` 로 한다)."""
    if not os.path.exists(db_path):
        return []
    con = connect(db_path)
    try:
        q = ("SELECT * FROM shindong_trades WHERE trade_date=? AND variant=?"
             + ("" if include_retracted else " AND status!='RETRACTED'")
             + " ORDER BY entry_ts")
        return [dict(r) for r in con.execute(q, (trade_date, variant))]
    finally:
        con.close()


def load_closed_for_pnl(db_path: str, limit_days: int = 90,
                        variant: str = "MAIN") -> List[Dict[str, Any]]:
    """[628차] 손익 추이 패널용 — 최근 N일 **청산 완료** 거래(보유 중·철회 제외).

    DB 가 없으면 빈 목록이다. 「미배선」 판정은 호출자가 파일 존재로 한다(계측 4원칙 ②).
    """
    if not os.path.exists(db_path):
        return []
    since = (_dt.date.today() - _dt.timedelta(days=int(limit_days))).isoformat()
    con = connect(db_path)
    try:
        return [dict(r) for r in con.execute(
            "SELECT * FROM shindong_trades WHERE variant=? AND status='CLOSED' "
            "AND trade_date>=? ORDER BY entry_ts", (variant, since))]
    finally:
        con.close()


def load_day(db_path: str, trade_date: str, variant: str = "MAIN") -> Optional[Dict[str, Any]]:
    if not os.path.exists(db_path):
        return None
    con = connect(db_path)
    try:
        r = con.execute("SELECT * FROM shindong_day WHERE trade_date=? AND variant=?",
                        (trade_date, variant)).fetchone()
        return dict(r) if r else None
    finally:
        con.close()


def covered_dates(db_path: str) -> Optional[set]:
    """판정 기록이 있는 날짜들. DB 없음 = None(원천없음) — 빈 집합(기록없음)과 다르다."""
    if not os.path.exists(db_path):
        return None
    con = connect(db_path)
    try:
        return {r[0] for r in con.execute(
            "SELECT DISTINCT trade_date FROM shindong_day WHERE variant='MAIN'")}
    finally:
        con.close()
