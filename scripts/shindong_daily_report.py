# -*- coding: utf-8 -*-
"""[MW0601 632차 후속] 신동 일일 리포트 — 장후 수동 재생성 · 백필용.

라이브에서는 `main.py:daily_close` 가 장후 1회 자동으로 만든다(`SHINDONG_DAILY_REPORT_ENABLED`).
이 스크립트는 같은 함수(`strategy/shindong/daily_report.build`)를 부른다.

사용:
    python scripts/shindong_daily_report.py                 # 오늘
    python scripts/shindong_daily_report.py 2026-09-28
    python scripts/shindong_daily_report.py --from 2026-09-21 --to 2026-09-28
⚠ 장중(08:45–15:35)에는 돌리지 말 것 — 가격·흐름이 끝나지 않았고 raw_data.db 를 읽는다(456차 규약).
"""
import argparse
import datetime as _dt
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from config.settings import (PREMARKET_LEVELS_DB, RAW_DATA_DB, SHINDONG_DAILY_REPORT_DIR,  # noqa: E402
                             SHINDONG_DB, WEEKLY_OPTION_FLOW_DB)
from strategy.shindong import daily_report  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("dates", nargs="*")
    ap.add_argument("--from", dest="date_from")
    ap.add_argument("--to", dest="date_to")
    ap.add_argument("--out", default=SHINDONG_DAILY_REPORT_DIR)
    a = ap.parse_args(argv)
    if a.date_from and a.date_to:
        d0, d1 = _dt.date.fromisoformat(a.date_from), _dt.date.fromisoformat(a.date_to)
        days = []
        while d0 <= d1:
            if d0.weekday() < 5:
                days.append(d0.isoformat())
            d0 += _dt.timedelta(days=1)
    else:
        days = a.dates or [_dt.date.today().isoformat()]
    flow = WEEKLY_OPTION_FLOW_DB if os.path.isabs(WEEKLY_OPTION_FLOW_DB) else os.path.join(ROOT, WEEKLY_OPTION_FLOW_DB)
    for d in days:
        r = daily_report.build(d, RAW_DATA_DB, flow, PREMARKET_LEVELS_DB, SHINDONG_DB, out_dir=a.out)
        if not r["ok"]:
            print("%s  건너뜀 — %s (파일 안 만듦)" % (d, r.get("why", "")))
            continue
        s = r["sums"]
        print("%s  %s  | %s" % (d, r.get("md_path"), " · ".join(
            "%s %+.1f만" % (v.replace("SHADOW_", ""), s[v]["net"] / 1e4) for v in s)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
