# -*- coding: utf-8 -*-
"""scripts/backfill_stack_gate_shadow.py — stack_gate_shadow 과거 백필 + 리포트

`strategy/stack_gate_shadow.py` 의 상태기를 과거 `raw_candles` 에 그대로 돌려
실제 진입(`trades`)마다 진입 시점 상태를 붙이고 반사실 판정까지 끝낸다.
main.py 훅 없이도 표본이 즉시 쌓인다.

읽기: raw_data.db (mode=ro), trades.db (mode=ro)
쓰기: **기본값 data/db/stack_gate_shadow.db (신규 파일)**
      `--into-trades-db` 를 주면 trades.db 에 직접 쓴다 (승인 필요 — 456차 원칙)

사용:
    python scripts\\backfill_stack_gate_shadow.py
    python scripts\\backfill_stack_gate_shadow.py --report-only
"""
from __future__ import annotations
import argparse, datetime, os, sqlite3, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from strategy.stack_gate_shadow import (          # noqa: E402
    StackGateShadow, DDL, DDL_IDX, INSERT_SQL, UPDATE_SQL, resolve_rows)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DBDIR = os.path.join(ROOT, "data", "db")
RAW = os.path.join(DBDIR, "raw_data.db")
TRD = os.path.join(DBDIR, "trades.db")
OWN = os.path.join(DBDIR, "stack_gate_shadow.db")
ATR_STOP_MULT, ATR_TP1_MULT = 1.5, 3.0   # config/settings.py 기본값과 동일


def ro(p):
    return sqlite3.connect("file:%s?mode=ro" % p.replace("\\", "/"), uri=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--into-trades-db", action="store_true",
                    help="trades.db 에 직접 기록 (기본은 별도 파일)")
    ap.add_argument("--report-only", action="store_true")
    ap.add_argument("--out", default="", help="기록할 DB 경로 직접 지정 (검증·격리용)")
    ap.add_argument("--window", type=int, default=30)
    ap.add_argument("--q", type=float, default=0.5)
    a = ap.parse_args()
    out_db = a.out or (TRD if a.into_trades_db else OWN)

    # ── 1. 분봉 적재 + 상태 재생 ──
    con = ro(RAW)
    bars = con.execute(
        "select ts,open,high,low,close,volume,oi,buy_vol,sell_vol from raw_candles "
        "where ts>='2026-06-01' order by ts").fetchall()
    con.close()
    gate = StackGateShadow(a.window, a.q)
    state_at, bar_map, atr_map = {}, {}, {}
    prev_close, tr = None, []
    for ts, o, h, l, c, v, oi, bv, sv in bars:
        key = ts[:16] + ":00"
        bar_map[key] = {"high": h, "low": l, "close": c}
        rng = (h - l) if prev_close is None else max(h - l, abs(h - prev_close), abs(l - prev_close))
        tr.append(rng); tr[:] = tr[-14:]
        atr_map[key] = sum(tr) / len(tr) if tr else 0.0
        prev_close = c
        state_at[key] = gate.update(ts, bv, sv, v, oi)

    # ── 2. 실제 진입 로드 (포지션 단위) ──
    con = ro(TRD)
    rows = con.execute(
        "select entry_ts, direction, grade, sum(quantity) q, avg(entry_price) p "
        "from trades where entry_ts>='2026-06-01' group by entry_ts, direction").fetchall()
    con.close()

    recs = []
    for ets, dirn, grade, qty, _px in rows:
        key = ets[:16] + ":00"
        st = state_at.get(key)
        bar = bar_map.get(key)
        if bar is None:
            continue
        close = bar["close"]; atr = atr_map.get(key, 0.0)
        dm = 1 if dirn == "LONG" else -1
        s = (st or {}).get("state", "NA")
        recs.append((key, dirn, grade, s,
                     (st or {}).get("aggr_imb"), (st or {}).get("oi_delta"),
                     int(bool((st or {}).get("ready"))),
                     int(StackGateShadow.would_block(s, dirn)),
                     None, float(atr), None, int(qty or 0), float(close),
                     float(close - dm * atr * ATR_STOP_MULT),
                     float(close + dm * atr * ATR_TP1_MULT)))

    if not a.report_only:
        w = sqlite3.connect(out_db)
        w.execute(DDL); w.execute(DDL_IDX)
        w.execute("delete from stack_gate_shadow where ts>='2026-06-01'")
        w.executemany(INSERT_SQL, recs); w.commit()
        pend = [dict(zip(["id", "ts", "direction", "entry_price", "stop_price", "tp1_price", "atr"], r))
                for r in w.execute("select id,ts,direction,entry_price,stop_price,tp1_price,atr "
                                   "from stack_gate_shadow where resolved=0")]
        ups = resolve_rows(bar_map, pend)
        w.executemany(UPDATE_SQL, ups); w.commit()
        n = w.execute("select count(*) from stack_gate_shadow where resolved=1").fetchone()[0]
        print("기록 %d행 / 판정완료 %d행  →  %s" % (len(recs), n, out_db))
        rep = w
    else:
        rep = sqlite3.connect(":memory:"); rep.execute(DDL)
        rep.executemany(INSERT_SQL, recs)

    # ── 3. 리포트 ──
    print("\n[상태 × 방향] 진입 건수")
    q = rep.execute("select state, direction, count(*) from stack_gate_shadow group by 1,2 order by 1,2")
    for s, d, n in q:
        print("   %-11s %-6s %4d" % (s, d, n))
    print("\n[게이트 판정] LONG ∧ BUY_MECH 차단 대상")
    r = rep.execute("select count(*), sum(would_block) from stack_gate_shadow").fetchone()
    print("   전체 %d건 중 %d건 (%.1f%%)" % (r[0], r[1] or 0, 100.0 * (r[1] or 0) / max(r[0], 1)))
    if not a.report_only:
        print("\n[반사실 성적] state × direction — hyp_pnl_pts (+)=진입이 옳았음")
        for s, d, n, m, w_ in rep.execute(
                "select state, direction, count(*), round(avg(hyp_pnl_pts),3), "
                "round(100.0*sum(hyp_pnl_pts>0)/count(*),1) from stack_gate_shadow "
                "where resolved=1 group by 1,2 having count(*)>=5 order by 4"):
            print("   %-11s %-6s n=%3d  평균 %+7.3fpt  승률 %5.1f%%" % (s, d, n, m, w_))
    rep.close()
    print("\n⚠ 이 테이블은 계측 전용이다. 라이브 차단은 표본 120거래일 + 사전등록 통과 뒤에만 검토한다.")


if __name__ == "__main__":
    main()
