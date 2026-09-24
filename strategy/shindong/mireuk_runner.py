# -*- coding: utf-8 -*-
"""[MW0601 629차] 신동 조건부 러너 섀도 — 미륵이 진입 × 신동 방향 × 신동 최종목표.

무엇을 재나
-----------
미륵이 시스템 진입 포지션마다 다음을 **가상으로** 다시 계산해 실제와 나란히 적는다.

  조건  : 진입 방향 == 그날 신동 R1 장전 방향(08:59 확정 — 진입 전에 알 수 있다)
  그리고 : 실제로 TP1 이 체결됐다
  그러면 : TP1 레그는 **실제 체결 그대로** 두고, TP1 이후에 나간 나머지 레그만
           「본전 스톱 + 신동 최종목표(T2) 지정가 + 15:05 시간 청산」으로 바꾼다.
  아니면 : 실제와 같다(차이 0). 사유를 남긴다.

[629차 후속] **진입 필터 B** 도 같은 행에 기록한다 — 청산은 미륵이 그대로, 진입만 거른다.
  B : 미륵이 진입 시각에 신동(MAIN)이 **같은 방향으로 보유 중**일 때만 진입(「방향 + 유지 상태」).
      통과 못 한 포지션은 「진입 안 함」= 0원. 시뮬이 없으므로 편향도 없다.
  C : 09:00 이후 콜−풋 흐름 추세 방향 — **기록만** 한다(판정 없음, 다중비교 방지).

왜 이 모양인가 — 2026-09-24 반사실(`docs/신동거래/반사실_신동규칙의_미륵이적용_CREON_20260924.md`)
  · 신동 청산을 통째로 입히면 이익이 추세일 3일에 몰리고 나머지 날은 손해였다.
  · TP1 뒤 잔량만 러너로 돌리면 현행 구간에서 차이 +13만(P≤0 = 0.49) — 조건 없이는 무효.
  · 남은 가설은 하나다: **추세일을 미리 가려내는 신호가 흐름(R1)인가.** 흐름 원천이
    3거래일뿐이라 표본으로만 풀린다. 이 섀도가 그 표본을 쌓는다.

🔴 **주문을 내지 않는다**(절대원칙 §6). `trades.db` 는 읽기만 하고, 결과는 `shindong.db`
   의 `shindong_mireuk_runner` 에만 쓴다(브로커 대사·전환기준 ① 오염 방지 — store.py 와 같은 이유).
🔴 값은 사전등록 고정값이다 — 바꾸면 `RUNNER_VERSION` 을 올리고 채점을 처음부터 다시 센다
   (`docs/신동거래/조건부러너_섀도_사전등록_20260924.md` §5).
"""
import datetime as _dt
import os
import sqlite3
from typing import Any, Dict, List, Optional

from strategy.shindong import engine as E
from strategy.shindong import spec as S

# ── 사전등록 고정값 ─────────────────────────────────────────────────────
RUNNER_VERSION = "SDR-2026-09-24-v1"
# 사용자 지시(2026-09-24): 반사실·섀도 손익은 **CREON 요율**로 산출한다.
#   (신동 본 규격 spec.COMMISSION_RATE 는 CYBOS — 두 PC 비교용 통일. 이 섀도는 별개 축이다.)
COMMISSION_RATE = 0.000019          # constants.BROKER_CHANNEL_SPECS["CREON"] 편도
PT_VALUE_KRW = S.PT_VALUE_KRW
SLIP_TICK = S.SLIP_TICK             # 본전·시간 청산(시장가) 1틱, 지정가 목표 0
TIME_EXIT = S.TIME_EXIT             # 15:05

SCORING_START = "2026-09-28"        # 신동 채점 시작과 같다
JUDGE_AFTER_FLOW_DAYS = 20          # 흐름이 측정된 거래일 20일이 차면 판정
MIN_APPLIED = 10                    # 러너가 실제로 적용된 포지션이 이보다 적으면 판정 불가
EXCLUDE_TOP_DAYS = 3                # 이번 반사실의 핵심 교훈 — 상위 3일 빼고도 버티는가
WORST_DAY_TOL_RATIO = 0.5           # 최악일 악화 허용 = |실제 최악일| × 0.5
WORST_DAY_TOL_MIN_KRW = 100000      #   … 단 최소 10만 원(실제 최악일이 작을 때)

# [629차 후속] 진입 필터 B 판정 — 러너와 같은 창·같은 ①②③, 최소 표본만 「제외된 포지션」 수
FILTER_VERSION = "SDF-2026-09-24-v1"
FILTER_MIN_EXCLUDED = 10            # 필터가 걸러낸 포지션이 이보다 적으면 판정 불가

SYSTEM_SOURCE = "SYSTEM_AUTO"       # 성과 축의 유일한 구성원(constants.ENTRY_SOURCE_REGISTRY)

_SCHEMA = """CREATE TABLE IF NOT EXISTS shindong_mireuk_runner (
    trade_date      TEXT NOT NULL,
    entry_ts        TEXT NOT NULL,          -- 미륵이 진입 시각(trades.entry_ts)
    side            INTEGER NOT NULL,       -- +1 매수 / -1 매도
    entry_px        REAL NOT NULL,
    qty             INTEGER NOT NULL,       -- 포지션 전체 계약수(레그 합)
    sd_pm_sp        REAL,                   -- 08:59 콜−풋 금액. NULL = 흐름 미수집
    sd_bias         INTEGER,                -- -1/0/+1. NULL = 미측정(계측 4원칙 ②)
    sd_r2           TEXT,                   -- 기술용(판정 무관) — CONFIRMED 등
    cond_met        INTEGER,                -- 1 조건 충족 / 0 불충족 / NULL 미측정
    applied         INTEGER NOT NULL,       -- 1 = 러너로 바뀐 레그가 있다
    skip_reason     TEXT,                   -- applied=0 인 이유
    tp1_exit_ts     TEXT,
    runner_start    TEXT,                   -- 러너 시뮬 시작 분(HH:MM)
    runner_qty      INTEGER,                -- 러너로 바꾼 계약수
    t2              REAL,                   -- 신동 최종목표(지정가). NULL = 목표 없음 → 15:05
    runner_exit_ts  TEXT,
    runner_exit_px  REAL,
    runner_reason   TEXT,                   -- TP2 | BE | TIME
    act_net_krw     REAL NOT NULL,          -- 실제 (CREON 재산정)
    shadow_net_krw  REAL NOT NULL,          -- 섀도 (CREON)
    diff_krw        REAL NOT NULL,          -- shadow − act
    sd_hold_side    INTEGER,                -- 진입 시각 신동 MAIN 보유 방향. 0 = 무포지션, NULL = 흐름 없음
    flow_trend      INTEGER,                -- 09:00 이후 콜−풋 추세(-1 하방/+1 상방). NULL = 미측정 · 기록 전용
    filt_b_pass     INTEGER,                -- 1 통과 / 0 제외 / NULL 미측정
    filt_b_net_krw  REAL,                   -- 필터 B 적용 손익(통과 = 실제, 제외 = 0). NULL = 미측정
    commission_rate REAL NOT NULL,
    runner_version  TEXT NOT NULL,
    source          TEXT NOT NULL,          -- eod | backfill
    updated_at      TEXT NOT NULL,
    PRIMARY KEY (trade_date, entry_ts, side)
)"""


def connect(db_path: str) -> sqlite3.Connection:
    d = os.path.dirname(db_path)
    if d:
        os.makedirs(d, exist_ok=True)
    con = sqlite3.connect(db_path, timeout=5.0)
    con.row_factory = sqlite3.Row
    con.execute(_SCHEMA)
    # 629차 첫 배포 테이블(필터 컬럼 없음)에 컬럼을 더한다 — 기존 행은 NULL(미측정)로 남는다
    have = {r[1] for r in con.execute("PRAGMA table_info(shindong_mireuk_runner)")}
    for col, typ in _ADDED_COLS:
        if col not in have:
            con.execute("ALTER TABLE shindong_mireuk_runner ADD COLUMN %s %s" % (col, typ))
    return con


_ADDED_COLS = (("sd_hold_side", "INTEGER"), ("flow_trend", "INTEGER"),
               ("filt_b_pass", "INTEGER"), ("filt_b_net_krw", "REAL"))


def _ro(path: str) -> sqlite3.Connection:
    con = sqlite3.connect("file:%s?mode=ro" % path.replace("\\", "/"), uri=True, timeout=5.0)
    con.row_factory = sqlite3.Row
    return con


# ── 입력 ────────────────────────────────────────────────────────────────
def load_positions(trades_db: str, trade_date: str) -> List[Dict[str, Any]]:
    """그날 시스템 진입 포지션(레그 묶음). 청산 안 된 레그가 있으면 `open=True`."""
    nxt = (_dt.date.fromisoformat(trade_date) + _dt.timedelta(days=1)).isoformat()
    con = _ro(trades_db)
    try:
        rows = [dict(r) for r in con.execute(
            "SELECT entry_ts, direction, entry_price, exit_price, quantity, gross_pnl_krw, "
            "exit_ts, exit_reason FROM trades WHERE entry_ts>=? AND entry_ts<? "
            "AND entry_source=? ORDER BY entry_ts, exit_ts", (trade_date, nxt, SYSTEM_SOURCE))]
    finally:
        con.close()
    out: Dict[tuple, Dict[str, Any]] = {}
    for r in rows:
        k = (r["entry_ts"], r["direction"])
        p = out.setdefault(k, {"entry_ts": r["entry_ts"],
                               "side": 1 if r["direction"] == "LONG" else -1,
                               "entry_px": float(r["entry_price"]), "legs": []})
        p["legs"].append(r)
    for p in out.values():
        p["open"] = any(l["exit_ts"] is None or l["exit_price"] is None for l in p["legs"])
    return list(out.values())


# ── 손익 ────────────────────────────────────────────────────────────────
def act_leg_net(leg: Dict[str, Any]) -> float:
    """실제 레그 — 기록된 gross 에서 CREON 요율로 수수료만 다시 뺀다(실체결·실슬리피지 유지)."""
    q = int(leg["quantity"])
    return (float(leg["gross_pnl_krw"] or 0.0)
            - (float(leg["entry_price"]) + float(leg["exit_price"])) * PT_VALUE_KRW
            * COMMISSION_RATE * q)


def sim_leg_net(side: int, e: float, x: float, qty: int, market_exit: bool) -> float:
    return qty * (side * (x - e) * PT_VALUE_KRW
                  - (e + x) * PT_VALUE_KRW * COMMISSION_RATE
                  - (SLIP_TICK * PT_VALUE_KRW if market_exit else 0.0))


def run_runner(d: "E.DayFrame", side: int, e: float, start: str,
               t2: Optional[float]) -> Optional[Dict[str, Any]]:
    """본전 스톱 + t2 지정가 + 15:05. 같은 봉에서 둘 다 닿으면 **본전**(보수적, 신동 규격과 동일).

    봉이 하나도 없으면 None — 시뮬 불가(0 으로 메우지 않는다).
    """
    bars = [k for k in d.idx if start <= k <= TIME_EXIT and k in d.c]
    if not bars:
        return None
    for t in bars:
        if (d.l[t] <= e) if side > 0 else (d.h[t] >= e):
            return {"ts": t, "px": e, "reason": "BE", "mkt": True}
        if t2 is not None and ((d.h[t] >= t2) if side > 0 else (d.l[t] <= t2)):
            return {"ts": t, "px": t2, "reason": "TP2", "mkt": False}
    tx = bars[-1]
    return {"ts": tx, "px": d.c[tx], "reason": "TIME", "mkt": True}


def sd_hold_side_at(sd_trades: List[Dict[str, Any]], hm: str) -> int:
    """미륵이 진입 분 `hm` 에 신동 MAIN 이 들고 있던 방향. 없으면 0.

    신동은 진입봉 **종가**로 들어가므로 진입 분 < hm 이어야 알 수 있다(같은 분 = 미래 참조).
    청산은 봉 안에서 일어나므로 hm 이 청산 분과 같으면 아직 보유 중으로 본다.
    """
    for tr in sd_trades:
        if not (tr["entry_ts"] < hm):
            continue
        ex = tr.get("exit_ts")
        if ex is None or hm <= ex:
            return int(tr["side"])
    return 0


def flow_trend_at(d: Optional["E.DayFrame"], hm: str) -> Optional[int]:
    """09:00 대비 직전 분까지의 콜−풋 변화 부호(+ = 하방 = -1). 흐름 없으면 None."""
    if d is None or S.CONF_BASE not in d.sp:
        return None
    k = d.last_at_or_before(E._plus_min(hm, -1))
    if k is None or k <= S.CONF_BASE or k not in d.sp:
        return None
    return -1 if d.sp[k] - d.sp[S.CONF_BASE] > 0 else 1


def evaluate_position(p: Dict[str, Any], d: Optional["E.DayFrame"], L: Optional[Dict[str, Any]],
                      decision: Optional[Dict[str, Any]],
                      sd_trades: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """포지션 1개 → 기록 1행. 순수 함수.

    sd_trades: 그날 신동 MAIN 거래(엔진 출력). None = 흐름 없음 → 필터 B 미측정.
    """
    side, e = p["side"], p["entry_px"]
    legs = p["legs"]
    act = sum(act_leg_net(l) for l in legs)
    rec = {
        "trade_date": p["entry_ts"][:10], "entry_ts": p["entry_ts"], "side": side,
        "entry_px": e, "qty": sum(int(l["quantity"]) for l in legs),
        "sd_pm_sp": None, "sd_bias": None, "sd_r2": None, "cond_met": None,
        "applied": 0, "skip_reason": None, "tp1_exit_ts": None, "runner_start": None,
        "runner_qty": None, "t2": None, "runner_exit_ts": None, "runner_exit_px": None,
        "runner_reason": None, "act_net_krw": act, "shadow_net_krw": act, "diff_krw": 0.0,
        "sd_hold_side": None, "flow_trend": None, "filt_b_pass": None, "filt_b_net_krw": None,
    }
    # 진입 필터 B · 기록용 C — 러너 조건과 무관하게 모든 포지션에 채운다
    hm = p["entry_ts"][11:16]
    if sd_trades is not None:
        hs = sd_hold_side_at(sd_trades, hm)
        rec["sd_hold_side"] = hs
        rec["filt_b_pass"] = 1 if hs == side else 0
        rec["filt_b_net_krw"] = act if hs == side else 0.0
    rec["flow_trend"] = flow_trend_at(d, hm)

    def skip(why):
        rec["skip_reason"] = why
        return rec

    # 1) 신동 방향 — 흐름 미수집은 「불충족」이 아니라 미측정이다
    if decision is not None:
        rec["sd_pm_sp"] = decision.get("pm_sp")
        rec["sd_r2"] = decision.get("r2")
        if decision.get("pm_sp") is not None:
            rec["sd_bias"] = int(decision.get("bias") or 0)
    if rec["sd_bias"] is None:
        return skip("흐름 미수집(미측정)")
    rec["cond_met"] = 1 if rec["sd_bias"] == side else 0
    if rec["sd_bias"] == 0:
        return skip("신동 방향 보류")
    if not rec["cond_met"]:
        return skip("신동 방향 반대")
    # 2) TP1 실체결
    tp1 = [l for l in legs if l["exit_reason"] and "TP1" in l["exit_reason"]]
    if not tp1:
        return skip("TP1 미도달")
    tp1_ts = min(l["exit_ts"] for l in tp1)
    rec["tp1_exit_ts"] = tp1_ts
    # TP1 이후에 나간 비-TP1 레그만 러너로 바꾼다(그 전에 나간 레그는 실제 그대로)
    rest = [l for l in legs if l not in tp1 and l["exit_ts"] >= tp1_ts]
    if not rest:
        return skip("TP1 뒤 잔량 없음")
    if d is None or L is None:
        return skip("봉 또는 08:50 맥점 없음")
    start = E._plus_min(tp1_ts[11:16], 1)
    if start > TIME_EXIT:
        return skip("TP1 이 15:05 이후")
    _t1, t2 = E.targets(L, p["entry_ts"][11:16], side, e)
    rq = sum(int(l["quantity"]) for l in rest)
    x = run_runner(d, side, e, start, t2)
    if x is None:
        return skip("러너 구간 봉 없음")
    runner_net = sim_leg_net(side, e, x["px"], rq, x["mkt"])
    shadow = act - sum(act_leg_net(l) for l in rest) + runner_net
    rec.update(applied=1, runner_start=start, runner_qty=rq, t2=t2,
               runner_exit_ts=x["ts"], runner_exit_px=x["px"], runner_reason=x["reason"],
               shadow_net_krw=shadow, diff_krw=shadow - act)
    return rec


# ── 하루 실행 · 저장 ────────────────────────────────────────────────────
def run_for_date(trade_date: str, trades_db: str, raw_db: str, flow_db: str, levels_db: str,
                 sd_db: str, source: str = "eod",
                 now: Optional[_dt.datetime] = None) -> Dict[str, Any]:
    """그날 전 포지션을 평가해 저장. 보유 중 포지션은 건너뛴다(개수는 반환값에 남긴다)."""
    from strategy.shindong import runner as _rn
    from strategy.shindong.calendar import select_flow_product

    positions = load_positions(trades_db, trade_date)
    n_open = sum(1 for p in positions if p["open"])
    positions = [p for p in positions if not p["open"]]
    product = select_flow_product(_dt.date.fromisoformat(trade_date))[0]
    candles, flow, lvrows = _rn.load_inputs(trade_date, product, raw_db, flow_db, levels_db)
    d = E.DayFrame(candles, flow) if candles else None
    L = E.prepare_levels(lvrows) if "0850" in lvrows else None
    day_res = E.run_day(d, L, "MAIN") if (d is not None and L is not None) else None
    decision = day_res["decision"] if day_res else None
    sd_trades = None
    if day_res is not None and d.sp:          # 흐름이 없으면 신동 보유 상태는 미측정
        sd_trades = [{"entry_ts": tr["entry_ts"], "exit_ts": tr["exit_ts"], "side": tr["side"]}
                     for tr in day_res["trades"]]
    recs = [evaluate_position(p, d, L, decision, sd_trades) for p in positions]
    save(sd_db, recs, source=source, now=now)
    return {"trade_date": trade_date, "n": len(recs), "n_open_skipped": n_open,
            "applied": sum(r["applied"] for r in recs),
            "act": sum(r["act_net_krw"] for r in recs),
            "shadow": sum(r["shadow_net_krw"] for r in recs),
            # 필터 B: 측정된 행이 하나도 없으면 None(미측정) — 0원과 다르다
            "filt_b": (sum(r["filt_b_net_krw"] for r in recs if r["filt_b_pass"] is not None)
                       if any(r["filt_b_pass"] is not None for r in recs) else None),
            "filt_b_excluded": sum(1 for r in recs if r["filt_b_pass"] == 0),
            "bias": None if decision is None or decision.get("pm_sp") is None
            else decision.get("bias"),
            "records": recs}


def save(sd_db: str, recs: List[Dict[str, Any]], source: str,
         now: Optional[_dt.datetime] = None) -> None:
    if not recs:
        return
    now_s = (now or _dt.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    cols = ["trade_date", "entry_ts", "side", "entry_px", "qty", "sd_pm_sp", "sd_bias", "sd_r2",
            "cond_met", "applied", "skip_reason", "tp1_exit_ts", "runner_start", "runner_qty",
            "t2", "runner_exit_ts", "runner_exit_px", "runner_reason", "act_net_krw",
            "shadow_net_krw", "diff_krw", "sd_hold_side", "flow_trend", "filt_b_pass",
            "filt_b_net_krw"]
    allc = cols + ["commission_rate", "runner_version", "source", "updated_at"]
    upd = ",".join("%s=excluded.%s" % (c, c) for c in allc[3:])
    con = connect(sd_db)
    try:
        with con:
            for r in recs:
                con.execute(
                    "INSERT INTO shindong_mireuk_runner(%s) VALUES(%s) "
                    "ON CONFLICT(trade_date,entry_ts,side) DO UPDATE SET %s"
                    % (",".join(allc), ",".join("?" * len(allc)), upd),
                    [r[c] for c in cols] + [COMMISSION_RATE, RUNNER_VERSION, source, now_s])
    finally:
        con.close()


# ── 사전등록 판정 ───────────────────────────────────────────────────────
def _judge(judged_days: List[str], rows: List[Dict[str, Any]], alt_key: str) -> Dict[str, Any]:
    """일별 (실제, 대안) → ①②③. 대안이 NULL 인 행은 실제로 본다(미측정은 바꾸지 않는다)."""
    by_day: Dict[str, List[float]] = {dd: [0.0, 0.0] for dd in judged_days}
    for r in rows:
        alt = r[alt_key] if r.get(alt_key) is not None else r["act_net_krw"]
        by_day[r["trade_date"]][0] += r["act_net_krw"]
        by_day[r["trade_date"]][1] += alt
    diffs = sorted((v[1] - v[0] for v in by_day.values()), reverse=True)
    tot = sum(diffs)
    ex_top = sum(diffs[EXCLUDE_TOP_DAYS:])
    worst_act = min((v[0] for v in by_day.values()), default=0.0)
    worst_alt = min((v[1] for v in by_day.values()), default=0.0)
    tol = max(WORST_DAY_TOL_RATIO * abs(min(worst_act, 0.0)), WORST_DAY_TOL_MIN_KRW)
    return {"act_krw": sum(v[0] for v in by_day.values()),
            "alt_krw": sum(v[1] for v in by_day.values()),
            "diff_krw": tot, "diff_ex_top_krw": ex_top,
            "worst_day_act": worst_act, "worst_day_alt": worst_alt, "worst_tol": tol,
            "c1_total_pos": tot > 0, "c2_ex_top_nonneg": ex_top >= 0,
            "c3_worst_ok": (worst_act - worst_alt) <= tol}


def _window(sd_db: str, until: Optional[str]):
    """(흐름 측정일 전부, 판정 창 20일, 창 안 기록 행). DB 없음 = None."""
    if not os.path.exists(sd_db):
        return None
    con = connect(sd_db)
    try:
        q_days = ("SELECT trade_date FROM shindong_day WHERE variant='MAIN' AND pm_sp IS NOT NULL "
                  "AND trade_date>=?" + (" AND trade_date<=?" if until else "") +
                  " ORDER BY trade_date")
        args = [SCORING_START] + ([until] if until else [])
        try:
            flow_days = [r[0] for r in con.execute(q_days, args)]
        except sqlite3.OperationalError:
            flow_days = []            # shindong_day 테이블 없음 — 신동 본체 미배선
        rows = [dict(r) for r in con.execute(
            "SELECT * FROM shindong_mireuk_runner WHERE runner_version=? AND trade_date>=?"
            + (" AND trade_date<=?" if until else ""), [RUNNER_VERSION] + args)]
    finally:
        con.close()
    judged = flow_days[:JUDGE_AFTER_FLOW_DAYS]
    scope = set(judged)
    return flow_days, judged, [r for r in rows if r["trade_date"] in scope]


def verdict(sd_db: str, until: Optional[str] = None) -> Dict[str, Any]:
    """러너 판정(사전등록 §3). status ∈ {NO_DB, WAITING, INSUFFICIENT, PASS, FAIL}.

    흐름 측정일 = `shindong_day`(MAIN) 에서 pm_sp 가 NULL 이 아닌 날(채점 시작 이후).
    미륵이 진입이 없던 날도 측정일로 센다(그날 차이 0).
    """
    w = _window(sd_db, until)
    if w is None:
        return {"status": "NO_DB"}
    flow_days, judged, rows = w
    applied = [r for r in rows if r["applied"]]
    j = _judge(judged, rows, "shadow_net_krw")
    out = {"flow_days": len(flow_days), "judged_days": len(judged),
           "positions": len(rows), "applied": len(applied),
           "act_krw": j["act_krw"], "shadow_krw": j["alt_krw"],
           "diff_krw": j["diff_krw"], "diff_ex_top_krw": j["diff_ex_top_krw"],
           "worst_day_act": j["worst_day_act"], "worst_day_shadow": j["worst_day_alt"],
           "worst_tol": j["worst_tol"], "c1_total_pos": j["c1_total_pos"],
           "c2_ex_top_nonneg": j["c2_ex_top_nonneg"], "c3_worst_ok": j["c3_worst_ok"]}
    if len(flow_days) < JUDGE_AFTER_FLOW_DAYS:
        out["status"] = "WAITING"
    elif len(applied) < MIN_APPLIED:
        out["status"] = "INSUFFICIENT"      # 표본 없음 ≠ 합격
    else:
        out["status"] = "PASS" if (out["c1_total_pos"] and out["c2_ex_top_nonneg"]
                                   and out["c3_worst_ok"]) else "FAIL"
    return out


def verdict_filter_b(sd_db: str, until: Optional[str] = None) -> Dict[str, Any]:
    """진입 필터 B 판정(사전등록 §3-2). 창·①②③ 은 러너와 같다.

    최소 표본 = 필터가 **제외한** 포지션 수. 제외가 적으면 필터는 사실상 아무것도 안 한
    것이다 — 그걸 합격으로 부르지 않는다. 미측정 행(filt_b_pass NULL)은 실제 그대로 둔다.
    """
    w = _window(sd_db, until)
    if w is None:
        return {"status": "NO_DB"}
    flow_days, judged, rows = w
    measured = [r for r in rows if r.get("filt_b_pass") is not None]
    out = {"flow_days": len(flow_days), "judged_days": len(judged),
           "positions": len(rows), "measured": len(measured),
           "passed": sum(1 for r in measured if r["filt_b_pass"] == 1),
           "excluded": sum(1 for r in measured if r["filt_b_pass"] == 0)}
    out.update(_judge(judged, rows, "filt_b_net_krw"))
    if len(flow_days) < JUDGE_AFTER_FLOW_DAYS:
        out["status"] = "WAITING"
    elif out["excluded"] < FILTER_MIN_EXCLUDED:
        out["status"] = "INSUFFICIENT"
    else:
        out["status"] = "PASS" if (out["c1_total_pos"] and out["c2_ex_top_nonneg"]
                                   and out["c3_worst_ok"]) else "FAIL"
    return out
