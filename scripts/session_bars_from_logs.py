# -*- coding: utf-8 -*-
# scripts/session_bars_from_logs.py — SYSTEM 로그의 [BAR-CLOSE][CYBOS] 줄로 session_bars 소급 복구
"""[MW0601 565차 / 풀타임 수집 소급] 2026-09-07(533차 배포) **이전** 날짜의 15:09~15:34 봉은
DB 어디에도 없지만, 실시간 수집기는 15:40 까지 살아 있었으므로 **SYSTEM 로그에 매 봉의
OHLCV 가 남아 있다**:

    2026-08-04 15:14:50 [INFO] SYSTEM: [BAR-CLOSE][CYBOS] ts=15:14 O=995.94 H=997.16 L=995.94 C=996.84 V=178

차트 TR 소급은 불가하다(만기 지난 월물 조회 거부 — 2026-09-14 실측). 그래서 로그가 유일한 원천이다.
복구 봉은 `source='log_recovered'` 이며 bid/ask·틱수·미결제는 NULL, **15:45 마감 체결은 없다**
(프로세스가 15:40 에 끝났다). 15:34 봉도 없다(550차 플러시 이전).

    python scripts/session_bars_from_logs.py --from 2026-08-01 --to 2026-09-06 [--dry-run] [--after 15:08]

`--after HH:MM` (기본 15:08): 이 시각보다 뒤 ts 만 넣는다 — 그 이전은 `raw_candles` 가 이미 갖고
있어 중복 적재의 이득이 없다. `--after 00:00` 이면 하루 전체를 넣는다.
장중 실행 금지(`guard_intraday`). 같은 ts 가 이미 있으면 건드리지 않는다.
"""
from __future__ import annotations

import argparse
import datetime
import glob
import os
import re
import sys
import zipfile

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.analysis_db import guard_intraday  # noqa: E402
from utils.time_utils import classify_session  # noqa: E402

SOURCE_LOG = "log_recovered"
_RE = re.compile(
    r"^(\d{4}-\d{2}-\d{2}) \d{2}:\d{2}:\d{2} \[INFO\] SYSTEM: \[BAR-CLOSE\]\[CYBOS\] "
    r"ts=(\d{2}):(\d{2}) O=([\d.]+) H=([\d.]+) L=([\d.]+) C=([\d.]+) V=(\d+)"
)


def iter_log_lines(day: datetime.date):
    """`logs/YYYYMMDD_SYSTEM.log` → 없으면 `logs/YYYYMM_SYSTEM.zip` 안의 같은 이름."""
    name = "%s_SYSTEM.log" % day.strftime("%Y%m%d")
    p = os.path.join(_ROOT, "logs", name)
    if os.path.exists(p):
        with open(p, encoding="utf-8", errors="replace") as f:
            for line in f:
                yield line
        return
    z = os.path.join(_ROOT, "logs", "%s_SYSTEM.zip" % day.strftime("%Y%m"))
    if os.path.exists(z):
        with zipfile.ZipFile(z) as zf:
            if name in zf.namelist():
                with zf.open(name) as fh:
                    for raw in fh:
                        yield raw.decode("utf-8", "replace")


def parse_bars(day: datetime.date, after: datetime.time):
    """첫 출현 우선(중복 BAR-CLOSE 는 stale 진동 — 두 번째는 버린다)."""
    seen, bars = set(), []
    for line in iter_log_lines(day):
        m = _RE.match(line)
        if not m or m.group(1) != day.isoformat():
            continue
        hh, mm = int(m.group(2)), int(m.group(3))
        t = datetime.time(hh, mm)
        if t <= after or (hh, mm) in seen:
            continue
        seen.add((hh, mm))
        ts = datetime.datetime.combine(day, t)
        bars.append((ts.strftime("%Y-%m-%d %H:%M:%S"), classify_session(ts, None), {
            "ts": ts, "open": float(m.group(4)), "high": float(m.group(5)),
            "low": float(m.group(6)), "close": float(m.group(7)), "volume": int(m.group(8)),
        }))
    return bars


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="d_from", required=True)
    ap.add_argument("--to", dest="d_to", required=True)
    ap.add_argument("--after", default="15:08", help="이 시각 이후 ts 만 (기본 15:08 — raw_candles 절단점)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    guard_intraday("session_bars_from_logs")
    from collection.cybos.chart_backfill import reconcile_and_insert
    from utils.db_utils import init_raw_data_db
    init_raw_data_db()

    after = datetime.time(*[int(x) for x in a.after.split(":")[:2]])
    d, d1 = datetime.date.fromisoformat(a.d_from), datetime.date.fromisoformat(a.d_to)
    tot_ins = tot_bars = days = 0
    while d <= d1:
        bars = parse_bars(d, after)
        if bars:
            st = reconcile_and_insert(bars, source=SOURCE_LOG, dry_run=a.dry_run, log_prefix="[SessionLogRecover]")
            days += 1
            tot_bars += len(bars)
            tot_ins += st["inserted"]
            print("%s bars=%d inserted=%d existing=%d mismatch=%d  %s~%s" % (
                d, len(bars), st["inserted"], st["existing"], st["mismatch"], bars[0][0][11:16], bars[-1][0][11:16]))
        d += datetime.timedelta(days=1)
    print("합계: %d일 bars=%d inserted=%d%s" % (days, tot_bars, tot_ins, " (dry-run)" if a.dry_run else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
