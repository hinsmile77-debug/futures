# -*- coding: utf-8 -*-
"""[MW0601 692차] raw_candles 창 안(08:45–15:08) 결손을 session_bars 로 메운다 — 과거분 1회·수동용.

장후 자동 경로는 `main._post_close_bar_sync()` 가 당일·따라잡기 날짜에 같은 함수를 부른다.
이 스크립트는 그 이전 날짜(배포 전)를 한 번에 맞출 때 쓴다.

    python scripts/raw_candles_fill_from_session_bars.py                 # 미리보기(쓰지 않음)
    python scripts/raw_candles_fill_from_session_bars.py --apply         # 적용
    python scripts/raw_candles_fill_from_session_bars.py --apply --rebuild-levels-cache

⚠ 장중(08:45–15:35) 실행 금지 — `guard_intraday`.
⚠ `--apply` 는 바뀌는 실시간 행(bar_recovered=3 대상)의 **원래 값을 먼저 JSON 으로 남긴다**.
  되돌리기: bar_recovered=2 행 DELETE, =3 행은 그 JSON 값으로 UPDATE.
"""
from __future__ import print_function

import argparse
import datetime
import io
import json
import os
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from utils.dll_bootstrap import ensure_conda_dll_path  # noqa: E402
ensure_conda_dll_path()

from config.settings import RAW_DATA_DB  # noqa: E402


def _preview(con):
    days = [r[0] for r in con.execute(
        "SELECT DISTINCT substr(ts,1,10) FROM session_bars ORDER BY 1")]
    miss = con.execute(
        "SELECT substr(s.ts,1,10), COUNT(*) FROM session_bars s "
        "WHERE substr(s.ts,12,5) BETWEEN '08:45' AND '15:08' "
        "AND NOT EXISTS (SELECT 1 FROM raw_candles r WHERE r.ts=s.ts) GROUP BY 1").fetchall()
    fix = con.execute(
        "SELECT r.ts, r.open, r.high, r.low, r.volume, r.bar_recovered FROM raw_candles r "
        "JOIN session_bars s ON s.ts=r.ts WHERE s.source IN ('rt_chart_open','rt_chart_fix') "
        "AND (abs(r.open-s.open)>1e-6 OR abs(r.high-s.high)>1e-6 OR abs(r.low-s.low)>1e-6 "
        "OR r.volume<>s.volume)").fetchall()
    return days, miss, fix


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--rebuild-levels-cache", action="store_true")
    a = ap.parse_args()
    try:
        from utils.analysis_db import guard_intraday
        guard_intraday("raw_candles_fill_from_session_bars")
    except ImportError:
        pass
    out = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8") if hasattr(sys.stdout, "buffer") else sys.stdout
    con = sqlite3.connect("file:%s?mode=ro" % RAW_DATA_DB.replace("\\", "/"), uri=True)
    days, miss, fix = _preview(con)
    con.close()
    out.write("session_bars %d일 (%s – %s)\n" % (len(days), days[0] if days else "-", days[-1] if days else "-"))
    out.write("삽입 대상(bar_recovered=2): %d봉 — %s\n" % (sum(n for _, n in miss),
                                                       ", ".join("%s %d" % (d, n) for d, n in miss) or "없음"))
    out.write("보정 대상(bar_recovered=3): %d봉\n" % len(fix))
    if not a.apply:
        out.write("(미리보기 — --apply 로 적용)\n")
        out.flush()
        return 0
    bak = os.path.join(os.path.dirname(RAW_DATA_DB),
                       "raw_candles_692_before_fill_%s.json" % datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    with io.open(bak, "w", encoding="utf-8") as f:
        json.dump({"note": "692차 적용 전 raw_candles 원값(보정 대상). 되돌리기: bar_recovered=2 DELETE, "
                           "=3 은 이 값으로 UPDATE", "fixed_rows": [list(r) for r in fix]},
                  f, ensure_ascii=False)
    out.write("백업: %s\n" % bak)
    from utils.db_utils import fill_raw_candles_from_session_bars
    ti = tf = 0
    for d in days:
        r = fill_raw_candles_from_session_bars(d)
        if r["inserted"] or r["fixed"]:
            out.write("  %s 보충 %d(%s) · 보정 %d(%s)\n" % (
                d, r["inserted"], ", ".join(r["inserted_ts"][:8]), r["fixed"], ", ".join(r["fixed_ts"][:8])))
        ti += r["inserted"]
        tf += r["fixed"]
    out.write("합계 보충 %d · 보정 %d\n" % (ti, tf))
    if a.rebuild_levels_cache:
        from features.levels import levels_store as LS
        res = LS.refresh_history_cache(force_full=True)
        out.write("맥점 이력 캐시 전량 재생성: sessions=%s last=%s grid=%s\n"
                  % (res.get("sessions"), res.get("last_date"), res.get("grid_sessions")))
    out.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
