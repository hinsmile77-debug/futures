# -*- coding: utf-8 -*-
"""P7 섀도 — 「이긴 숏의 절반을 본전 스톱으로 다음 구조레벨까지 홀딩」 카운터팩추얼 기록.

[사전등록 2026-09-20]  근거: `Peter/피터유튭/피터리_결합모델_P5P6_20260920.md` §9

## 왜 있는가

미륵이는 **보유 중앙 3분**에 나가고, **이긴 거래에서 갈 수 있는 거리(MFE)의 13%만** 먹는다.
2026-06-10~09-14 실측에서 「이긴 거래의 50%를 **본전 스톱**으로 남겨 **다음 구조레벨**까지
홀딩」하면 숏에서 **일평균 +0.624p(1계약)** 개선됐다(51일, 부트스트랩 95%CI [+0.5, +66.8]).

⚠ **그러나 그 표본으로 '숏'이라는 조건을 골랐다 — 전부 in-sample 이다.**
이 스크립트는 **판정하지 않는다. 기록만 한다.** 표본 밖 120거래일이 쌓이면 그때 판정한다.

## 하지 않는 것

* **라이브 매매에 아무 영향을 주지 않는다.** 주문·청산·설정 어디에도 연결돼 있지 않다.
* `trades.db` / `raw_data.db` / `premarket_levels.db` 를 **읽기 전용(mode=ro)** 으로만 연다.
* 쓰기는 **전용 DB `data/db/p7_shadow.db`** 한 곳뿐이다 — 기존 스키마를 건드리지 않는다.
* 장중에는 돌지 않는다(`guard_intraday`) — 2026-08-10 CB⑤ 자가유발 재발 방지.

## 규칙 (사전등록 · 변경 금지)

    적용 대상   방향 = SHORT  ∧  실제 손익 > 0  ∧  진행 방향에 다음 구조레벨이 있음
    잔량 비율   50%
    잔량 스톱   진입가(본전)          → 최악 0p. 추가 위험 없음
    잔량 목표   08:50 구조모델 레벨 중 진행 방향의 다음 값
    시간청산    15:05
    ⛔ 롱에는 적용하지 않는다 — 실측에서 상승일 −2.1p / 하락일 −4.7p 로 양 국면 모두 음수

실행:
    conda run -n py37_32 python scripts/p7_hold_shadow_eod.py              # 오늘
    conda run -n py37_32 python scripts/p7_hold_shadow_eod.py --date 2026-09-12
    conda run -n py37_32 python scripts/p7_hold_shadow_eod.py --backfill 2026-06-10 2026-09-14
    conda run -n py37_32 python scripts/p7_hold_shadow_eod.py --report
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.dll_bootstrap import ensure_conda_dll_path  # noqa: E402  (numpy 보다 먼저)
ensure_conda_dll_path()

import argparse  # noqa: E402
import datetime  # noqa: E402
import json  # noqa: E402
import random  # noqa: E402
import sqlite3  # noqa: E402
import statistics  # noqa: E402

from config.settings import DB_DIR, RAW_DATA_DB, TRADES_DB  # noqa: E402
from utils.analysis_db import guard_intraday  # noqa: E402

PREMARKET_DB = os.path.join(DB_DIR, "premarket_levels.db")
SHADOW_DB = os.path.join(DB_DIR, "p7_shadow.db")

EXIT_T = "15:05"      # 시간청산 — raw_candles 가 15:08 에서 끊긴다
FRAC = 0.5            # 잔량 비율
SESSION_OPEN = "08:45"

SCHEMA = """
CREATE TABLE IF NOT EXISTS p7_hold_shadow (
    trade_date    TEXT NOT NULL,
    entry_ts      TEXT NOT NULL,
    direction     TEXT NOT NULL,
    entry_price   REAL NOT NULL,
    exit_ts       TEXT,
    qty           INTEGER,
    act_pts       REAL,            -- 미륵이 실제 손익(1계약 환산)
    applicable    INTEGER,         -- P7 적용 대상(1) / 아님(0)
    skip_reason   TEXT,            -- 적용 제외 사유
    target_level  REAL,            -- 잔량 목표 = 다음 구조레벨
    hold_pts      REAL,            -- 잔량의 손익
    hold_outcome  TEXT,            -- TARGET / BREAKEVEN / TIME
    shadow_pts    REAL,            -- act*(1-FRAC) + hold*FRAC
    delta_pts     REAL,            -- shadow - act  (= 개선분)
    day_dir       TEXT,            -- UP / DOWN  (사후 진단 전용. 규칙 아님)
    v20           REAL,
    created_at    TEXT,
    PRIMARY KEY (entry_ts, direction, entry_price)
);
"""


# ─────────────────────────────────────────────────────────── 읽기 (read-only)
def _ro(path):
    return sqlite3.connect("file:%s?mode=ro" % path.replace("\\", "/"), uri=True)


def load_bars(date_str):
    """당일 1분봉 — (hhmm, high, low, close). 08:45 이후만."""
    con = _ro(RAW_DATA_DB)
    try:
        rows = con.execute(
            "SELECT ts, high, low, close FROM raw_candles"
            " WHERE substr(ts,1,10)=? AND substr(ts,12,5)>=? ORDER BY ts",
            (date_str, SESSION_OPEN)).fetchall()
    finally:
        con.close()
    return [(r[0][11:16], r[1], r[2], r[3]) for r in rows]


def load_levels(date_str):
    """08:50 구조모델 레벨 집합(정렬)."""
    con = _ro(PREMARKET_DB)
    try:
        row = con.execute(
            "SELECT struct_up, struct_down FROM premarket_levels"
            " WHERE date=? AND stage='0850'", (date_str,)).fetchone()
    finally:
        con.close()
    if not row:
        return []
    out = []
    for js in row:
        if not js:
            continue
        try:
            for item in json.loads(js):
                out.append(round(float(item[0]) * 2) / 2)
        except (ValueError, TypeError, IndexError):
            continue
    return sorted(set(out))


def load_entries(date_str):
    """당일 진입 그룹 — 같은 (entry_ts, direction, entry_price) 는 한 포지션."""
    con = _ro(TRADES_DB)
    try:
        rows = con.execute(
            "SELECT entry_ts, exit_ts, direction, entry_price, quantity, pnl_pts"
            " FROM trades WHERE substr(entry_ts,1,10)=? AND pnl_pts IS NOT NULL"
            " AND substr(entry_ts,12,5)>=? AND substr(entry_ts,12,5)<?"
            " ORDER BY entry_ts", (date_str, SESSION_OPEN, EXIT_T)).fetchall()
    finally:
        con.close()
    grp = {}
    for ets, xts, dr, ep, qty, pnl in rows:
        key = (ets, dr, ep)
        g = grp.get(key)
        if g is None:
            g = {"qty": 0, "pts": 0.0, "last_exit": xts or ets}
            grp[key] = g
        g["qty"] += (qty or 1)
        g["pts"] += (pnl or 0.0)
        if xts and xts > g["last_exit"]:
            g["last_exit"] = xts
    out = []
    for (ets, dr, ep), g in sorted(grp.items()):
        out.append({
            "entry_ts": ets, "direction": dr, "entry_price": ep,
            "exit_ts": g["last_exit"], "qty": g["qty"],
            "act": g["pts"] / max(1, g["qty"]),
        })
    return out


def v20_for(date_str):
    """직전 20거래일 일중범위(고−저) 중앙값. 당일을 포함하지 않는다(look-ahead 없음)."""
    con = _ro(RAW_DATA_DB)
    try:
        rows = con.execute(
            "SELECT substr(ts,1,10) d, MAX(high)-MIN(low) FROM raw_candles"
            " WHERE substr(ts,1,10)<? AND substr(ts,12,5)>=?"
            " GROUP BY d ORDER BY d DESC LIMIT 20", (date_str, SESSION_OPEN)).fetchall()
    finally:
        con.close()
    vals = [r[1] for r in rows if r[1] is not None]
    return statistics.median(vals) if len(vals) >= 10 else None


# ─────────────────────────────────────────────────────────── 규칙 (사전등록)
def next_level(levels, from_price, side):
    """진행 방향의 다음 구조레벨. side: 1=롱 · -1=숏."""
    if side == 1:
        cand = [x for x in levels if x > from_price]
        return min(cand) if cand else None
    cand = [x for x in levels if x < from_price]
    return max(cand) if cand else None


def simulate_hold(bars, entry_price, side, exit_hhmm, target):
    """잔량을 본전 스톱으로 target 까지 홀딩. 반환 (pnl, outcome)."""
    path = [b for b in bars if exit_hhmm <= b[0] <= EXIT_T]
    if len(path) < 2:
        return None, None
    for hhmm, hi, lo, cl in path[1:]:
        if side == 1:
            if lo <= entry_price:
                return 0.0, "BREAKEVEN"
            if hi >= target:
                return target - entry_price, "TARGET"
        else:
            if hi >= entry_price:
                return 0.0, "BREAKEVEN"
            if lo <= target:
                return entry_price - target, "TARGET"
    last = path[-1][3]
    return (last - entry_price) * side, "TIME"


def evaluate_day(date_str):
    """하루치 섀도 행을 만든다. 쓰기는 하지 않는다."""
    bars = load_bars(date_str)
    if len(bars) < 60:
        return []
    levels = load_levels(date_str)
    entries = load_entries(date_str)
    v20 = v20_for(date_str)
    day_dir = "UP" if bars[-1][3] > bars[0][3] else "DOWN"
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    out = []
    for e in entries:
        side = 1 if e["direction"] == "LONG" else -1
        row = {
            "trade_date": date_str, "entry_ts": e["entry_ts"],
            "direction": e["direction"], "entry_price": e["entry_price"],
            "exit_ts": e["exit_ts"], "qty": e["qty"], "act_pts": e["act"],
            "applicable": 0, "skip_reason": None, "target_level": None,
            "hold_pts": None, "hold_outcome": None,
            "shadow_pts": e["act"], "delta_pts": 0.0,
            "day_dir": day_dir, "v20": v20, "created_at": now,
        }
        if side == 1:
            row["skip_reason"] = "LONG_EXCLUDED"
        elif e["act"] <= 0:
            row["skip_reason"] = "NOT_A_WINNER"
        elif not levels:
            row["skip_reason"] = "NO_LEVELS"
        else:
            frm = e["entry_price"] + side * e["act"]
            tgt = next_level(levels, frm, side)
            if tgt is None:
                row["skip_reason"] = "NO_NEXT_LEVEL"
            else:
                hp, outcome = simulate_hold(
                    bars, e["entry_price"], side, e["exit_ts"][11:16], tgt)
                if hp is None:
                    row["skip_reason"] = "NO_PATH_AFTER_EXIT"
                else:
                    shadow = e["act"] * (1 - FRAC) + hp * FRAC
                    row.update(applicable=1, target_level=tgt, hold_pts=hp,
                               hold_outcome=outcome, shadow_pts=shadow,
                               delta_pts=shadow - e["act"])
        out.append(row)
    return out


# ─────────────────────────────────────────────────────────── 쓰기 (전용 DB만)
COLS = ("trade_date", "entry_ts", "direction", "entry_price", "exit_ts", "qty",
        "act_pts", "applicable", "skip_reason", "target_level", "hold_pts",
        "hold_outcome", "shadow_pts", "delta_pts", "day_dir", "v20", "created_at")


def save(rows):
    if not rows:
        return 0
    os.makedirs(DB_DIR, exist_ok=True)
    con = sqlite3.connect(SHADOW_DB, timeout=10.0)
    try:
        con.executescript(SCHEMA)
        con.executemany(
            "INSERT OR REPLACE INTO p7_hold_shadow (%s) VALUES (%s)"
            % (",".join(COLS), ",".join("?" * len(COLS))),
            [tuple(r[c] for c in COLS) for r in rows])
        con.commit()
    finally:
        con.close()
    return len(rows)


# ─────────────────────────────────────────────────────────── 보고 (판정 아님)
def report():
    if not os.path.exists(SHADOW_DB):
        print("[P7] 섀도 DB 없음 — 먼저 적재하라"); return
    con = _ro(SHADOW_DB)
    try:
        rows = con.execute(
            "SELECT trade_date, direction, act_pts, delta_pts, applicable,"
            " hold_outcome, day_dir, skip_reason FROM p7_hold_shadow"
            " ORDER BY trade_date").fetchall()
    finally:
        con.close()
    if not rows:
        print("[P7] 기록 없음"); return

    days = sorted(set(r[0] for r in rows))
    appl = [r for r in rows if r[4] == 1]
    byday = {}
    for r in rows:
        byday[r[0]] = byday.get(r[0], 0.0) + (r[3] or 0.0)
    per = [byday[d] for d in days]

    print("=" * 78)
    print("[P7 섀도 누적]  %s ~ %s  %d거래일 · 진입 %d건 · 적용 %d건"
          % (days[0], days[-1], len(days), len(rows), len(appl)))
    print("  ⚠ 이것은 **기록**이다. 판정은 표본 밖 120거래일이 쌓인 뒤에 한다.")
    print()
    base = sum(r[2] or 0.0 for r in rows)
    delta = sum(r[3] or 0.0 for r in rows)
    print("  기준선(실제)      %+9.1f p" % base)
    print("  P7 섀도           %+9.1f p   (개선 %+.1f p · %+.1f%%)"
          % (base + delta, delta, (delta / base * 100) if base else 0.0))
    print("  일평균 개선       %+9.3f p   (%d일)" % (delta / len(days), len(days)))

    if len(days) >= 10:
        random.seed(20260920)
        sims = []
        for _ in range(3000):
            pick = [random.choice(days) for _ in days]
            sims.append(sum(byday[d] for d in pick))
        sims.sort()
        lo = sims[int(3000 * 0.025)]
        hi = sims[int(3000 * 0.975)]
        p = sum(1 for x in sims if x > 0) / 3000.0
        print("  블록 부트스트랩   95%%CI [%+.1f, %+.1f]  P(>0)=%.3f" % (lo, hi, p))
        need = None
        if per and statistics.mean(per) > 0:
            sd = statistics.pstdev(per) or 1e-9
            need = (1.96 * sd / statistics.mean(per)) ** 2
        print("  합격 필요 표본    %s  (현재 %d일)"
              % (("%.0f일" % need) if need else "산출 불가(개선≤0)", len(days)))

    print()
    print("  [진단 — 규칙 아님] 국면별")
    for dd in ("UP", "DOWN"):
        g = [r for r in rows if r[6] == dd]
        gd = sorted(set(r[0] for r in g))
        if not gd:
            continue
        s = sum(r[3] or 0.0 for r in g)
        print("   %-6s %3d일 · 개선 %+8.1f p · 일평균 %+.3f p" % (dd, len(gd), s, s / len(gd)))
    print()
    print("  [잔량 결말]  " + " · ".join(
        "%s %d" % (k, sum(1 for r in appl if r[5] == k))
        for k in ("TARGET", "BREAKEVEN", "TIME")))
    skips = {}
    for r in rows:
        if r[7]:
            skips[r[7]] = skips.get(r[7], 0) + 1
    if skips:
        print("  [제외 사유]  " + " · ".join(
            "%s %d" % (k, skips[k]) for k in sorted(skips, key=lambda x: -skips[x])))
    print("=" * 78)


# ─────────────────────────────────────────────────────────── 진입점
def main(argv=None):
    ap = argparse.ArgumentParser(description="P7 홀딩 섀도 (기록 전용 · 매매 무관)")
    ap.add_argument("--date", help="YYYY-MM-DD (기본: 오늘)")
    ap.add_argument("--backfill", nargs=2, metavar=("FROM", "TO"))
    ap.add_argument("--report", action="store_true", help="누적 보고만")
    ap.add_argument("--allow-intraday", action="store_true",
                    help="🔴 장중 가드 해제 — 테스트 전용")
    a = ap.parse_args(argv)

    if not a.allow_intraday:
        guard_intraday("p7_hold_shadow_eod.py")

    if a.report:
        report(); return 0

    if a.backfill:
        con = _ro(RAW_DATA_DB)
        try:
            days = [r[0] for r in con.execute(
                "SELECT DISTINCT substr(ts,1,10) d FROM raw_candles"
                " WHERE substr(ts,1,10)>=? AND substr(ts,1,10)<=? ORDER BY d",
                (a.backfill[0], a.backfill[1])).fetchall()]
        finally:
            con.close()
    else:
        days = [a.date or datetime.date.today().strftime("%Y-%m-%d")]

    total = 0
    for d in days:
        rows = evaluate_day(d)
        n = save(rows)
        total += n
        if n:
            ap_n = sum(1 for r in rows if r["applicable"] == 1)
            dl = sum(r["delta_pts"] or 0.0 for r in rows)
            print("[P7] %s  진입 %2d · 적용 %2d · 개선 %+.2f p" % (d, n, ap_n, dl))
    print("[P7] 적재 %d행 → %s" % (total, SHADOW_DB))
    return 0


if __name__ == "__main__":
    sys.exit(main())
