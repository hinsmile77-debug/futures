# -*- coding: utf-8 -*-
# scripts/session_bars_chart_backfill.py — FutOptChart 분봉으로 session_bars 대사·보충 (장후 전용)
"""[MW0601 565차 / 풀타임 수집 Phase 3] 수동 실행판. 메인은 매 거래일 08:41 에 전 거래일을
자동 보충하지만, 여러 날을 한 번에 메우거나 대사만 보고 싶을 때 이걸 쓴다.

    conda run -n py37_32 python scripts/session_bars_chart_backfill.py --from 2026-09-07 --to 2026-09-14
    conda run -n py37_32 python scripts/session_bars_chart_backfill.py --date 2026-09-11 --dry-run
    conda run -n py37_32 python scripts/session_bars_chart_backfill.py --date 2026-09-11 --code A056A

py37_32 · Cybos Plus 로그인 · 장 마감 후(`guard_intraday`). 코드는 날짜별 근월물을 자동
유도한다(`mini_code_for_date`). **만기가 지난 월물은 조회가 거부된다** — 2026-09-10 이전 날짜는
A0569 가 필요한데 이미 없다(2026-09-14 실측). 그 구간은 `scripts/session_bars_from_logs.py`.
"""
from __future__ import annotations

import argparse
import datetime
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.analysis_db import guard_intraday  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default="")
    ap.add_argument("--from", dest="d_from", default="")
    ap.add_argument("--to", dest="d_to", default="")
    ap.add_argument("--code", default="", help="강제 코드(기본: 날짜별 근월물 자동)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    guard_intraday("session_bars_chart_backfill")

    import win32com.client as win32
    if not win32.Dispatch("CpUtil.CpCybos").IsConnect:
        print("[중단] Cybos Plus 미연결")
        return 1
    from collection.cybos.chart_backfill import backfill_day, mini_code_for_date
    from utils.db_utils import init_raw_data_db
    init_raw_data_db()

    if a.date:
        d0 = d1 = datetime.date.fromisoformat(a.date)
    elif a.d_from and a.d_to:
        d0, d1 = datetime.date.fromisoformat(a.d_from), datetime.date.fromisoformat(a.d_to)
    else:
        print("[중단] --date 또는 --from/--to")
        return 1

    rc = 0
    d = d0
    while d <= d1:
        code = a.code or mini_code_for_date(d)
        st = backfill_day(d, code=code, dry_run=a.dry_run)
        if st is None:
            print("%s code=%s 건너뜀/실패 (비거래일·만기월물·조회거부 — SYSTEM 로그 참조)" % (d, code))
        else:
            print("%s code=%s chart=%d existing=%d inserted=%d mismatch=%d%s" % (
                d, code, st["chart"], st["existing"], st["inserted"], st["mismatch"],
                " (dry-run)" if a.dry_run else ""))
            for ts, bad, src in st["mismatch_ts"]:
                print("   불일치 ts=%s cols=%s existing_source=%s" % (ts, bad, src))
            if st["mismatch"]:
                rc = 1
        d += datetime.timedelta(days=1)
    return rc


if __name__ == "__main__":
    sys.exit(main())
