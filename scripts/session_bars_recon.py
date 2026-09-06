# -*- coding: utf-8 -*-
# scripts/session_bars_recon.py — session_bars ↔ raw_candles 대사 + Phase 1 판정 (장후 전용)
"""[MW0601 533차 / 풀타임 수집 Phase 1 검증] 하루치 `session_bars` 를 세션별로 세고,
`raw_candles` 와 겹치는 ts 에서 OHLCV 를 **모든 축** 대조한다(계측 4원칙 ⑤).

    python scripts/session_bars_recon.py                 # 가장 최근 거래일
    python scripts/session_bars_recon.py --date 2026-09-08

장중이면 456차 규약대로 rc=2 로 종료한다(`utils.analysis_db.guard_intraday`).
읽기전용이며 아무것도 쓰지 않는다.

판정(§6, 첫 5거래일):
  · PRE_MARKET 15 · REGULAR 370(15:09 포함) · POST_FORCE_EXIT 25   ← Phase 1 만으로 도달
  · CLOSE_AUCTION 0~10 · CLOSE_FILL 1                                ← Phase 2 배선 뒤에만
  · raw_candles 교집합에서 OHLCV 불일치 0
  · auction_code 전부 NULL 이면 헤더 28 미수신 — `[CybosRT-AUCTION]` WARNING 확인
"""
from __future__ import annotations

import argparse
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config.settings import RAW_DATA_DB  # noqa: E402
from utils.analysis_db import connect_ro, guard_intraday  # noqa: E402

EXPECT_PHASE1 = {"PRE_MARKET": 15, "REGULAR": 370, "POST_FORCE_EXIT": 25}
EXPECT_PHASE2 = {"CLOSE_FILL": 1}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default="", help="YYYY-MM-DD (기본: session_bars 최신 날짜)")
    args = ap.parse_args()
    guard_intraday("session_bars_recon")

    con = connect_ro(RAW_DATA_DB)
    try:
        has = con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='session_bars'").fetchone()
        if not has:
            print("[중단] session_bars 테이블 없음 — 메인이 533차 코드로 한 번도 기동하지 않았다")
            return 1
        day = args.date or (con.execute("SELECT MAX(substr(ts,1,10)) FROM session_bars").fetchone()[0] or "")
        if not day:
            print("[중단] session_bars 비어 있음")
            return 1
        rows = con.execute(
            "SELECT session, COUNT(*), MIN(ts), MAX(ts), SUM(auction_code IS NULL), SUM(COALESCE(auction_ticks,0)>0), "
            "SUM(source<>'rt') FROM session_bars WHERE substr(ts,1,10)=? GROUP BY session ORDER BY MIN(ts)",
            (day,)).fetchall()
        print("=== %s session_bars ===" % day)
        print("  %-16s %5s  %-19s %-19s %8s %8s %6s" % ("session", "n", "first", "last", "ac_NULL", "ac_hit", "nonRT"))
        counts = {}
        for s, n, a, b, nnull, nhit, nrt in rows:
            counts[s] = n
            print("  %-16s %5d  %-19s %-19s %8d %8d %6d" % (s, n, a, b, nnull or 0, nhit or 0, nrt or 0))

        auc = con.execute(
            "SELECT ts, session, open, close, volume, auction_code, auction_ticks FROM session_bars "
            "WHERE substr(ts,1,10)=? AND COALESCE(auction_code,0)<>0 ORDER BY ts", (day,)).fetchall()
        print("\n단일가 체결 포함 봉(auction_code≠0): %d" % len(auc))
        for r in auc[:12]:
            print("   ", r)

        mism = con.execute(
            "SELECT COUNT(*), SUM(s.open<>r.open), SUM(s.high<>r.high), SUM(s.low<>r.low), "
            "SUM(s.close<>r.close), SUM(s.volume<>r.volume) "
            "FROM session_bars s JOIN raw_candles r ON r.ts=s.ts WHERE substr(s.ts,1,10)=?", (day,)).fetchone()
        n_join = mism[0] or 0
        bad = [int(x or 0) for x in mism[1:]]
        print("\nraw_candles 교집합 %d행 — 불일치 O/H/L/C/V = %s" % (n_join, bad))
        only_raw = con.execute(
            "SELECT COUNT(*) FROM raw_candles r WHERE substr(r.ts,1,10)=? AND NOT EXISTS "
            "(SELECT 1 FROM session_bars s WHERE s.ts=r.ts)", (day,)).fetchone()[0]
        print("raw_candles 에만 있는 봉: %d (0이어야 정상 — 세션 적재가 모든 분기보다 앞이므로)" % only_raw)

        print("\n=== 판정 ===")
        ok = True
        for k, v in EXPECT_PHASE1.items():
            got = counts.get(k, 0)
            flag = "OK " if got == v else "!! "
            ok = ok and got == v
            print("  %s %-16s 기대 %3d 실측 %3d" % (flag, k, v, got))
        for k, v in EXPECT_PHASE2.items():
            got = counts.get(k, 0)
            print("  %s %-16s 기대 %3d 실측 %3d  (Phase 2 배선 전이면 0이 정상)" % ("OK " if got == v else "-- ", k, v, got))
        if sum(bad) or only_raw:
            ok = False
            print("  !! OHLCV 불일치 또는 raw_candles 전용 봉 존재 — 적재 경로 재확인")
        total_null = sum(r[4] or 0 for r in rows)
        total_rows = sum(counts.values())
        if total_rows and total_null == total_rows:
            print("  !! auction_code 전부 NULL — 헤더 28 미수신. 로그 [CybosRT-AUCTION] WARNING 확인")
        print("  Phase 1 %s" % ("PASS" if ok else "FAIL"))
        return 0 if ok else 1
    finally:
        con.close()


if __name__ == "__main__":
    sys.exit(main())
