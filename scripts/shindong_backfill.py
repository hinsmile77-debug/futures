# -*- coding: utf-8 -*-
"""[MW0601 626차] 신동 가상거래 백필 — 지난 날짜를 규격대로 재생해 `shindong.db` 에 넣는다.

복기(1분봉 차트 날짜 선택)에서 과거 신동 거래를 보려면 기록이 있어야 한다.
라이브와 **같은 엔진·같은 규격**으로 계산하고 `source='backfill'` 로 표시한다.

⚠ 백필 행은 `detected_at` 이 없다 — 실시간으로 알아챘는지는 모른다(미측정 ≠ 0).
  채점(`shindong_scorecard.py`)은 사전등록 채점 시작일(9/28) 이전을 표본에 넣지 않으므로
  9/21–9/23 백필은 **복기 전용**이다.

사용:
    python scripts/shindong_backfill.py 2026-09-21 2026-09-22 2026-09-23
    python scripts/shindong_backfill.py --from 2026-09-21 --to 2026-09-23
"""
import argparse
import datetime as _dt
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from config.settings import (PREMARKET_LEVELS_DB, RAW_DATA_DB, SHINDONG_DB,  # noqa: E402
                             WEEKLY_OPTION_FLOW_DB)
from strategy.shindong import engine, runner  # noqa: E402


def _dates(args):
    if args.dates:
        return list(args.dates)
    d0 = _dt.date.fromisoformat(args.date_from)
    d1 = _dt.date.fromisoformat(args.date_to)
    out = []
    while d0 <= d1:
        if d0.weekday() < 5:
            out.append(d0.isoformat())
        d0 += _dt.timedelta(days=1)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("dates", nargs="*")
    ap.add_argument("--from", dest="date_from")
    ap.add_argument("--to", dest="date_to")
    args = ap.parse_args(argv)
    if not args.dates and not (args.date_from and args.date_to):
        ap.error("날짜를 주거나 --from/--to 를 줄 것")
    today = _dt.date.today().isoformat()
    flow_db = WEEKLY_OPTION_FLOW_DB if os.path.isabs(WEEKLY_OPTION_FLOW_DB) \
        else os.path.join(ROOT, WEEKLY_OPTION_FLOW_DB)
    for d in _dates(args):
        if d == today:
            # 오늘은 라이브 실행기의 몫이다 — 백필로 덮으면 detected_at 이 사라진다.
            print("%s  건너뜀 — 오늘은 라이브 기록 대상" % d)
            continue
        p = runner.run_and_store(d, RAW_DATA_DB, flow_db, PREMARKET_LEVELS_DB, SHINDONG_DB,
                                 live=False)
        dec = p["decision"]
        net = sum(float(t.get("net_krw") or 0.0) for t in p["trades"])
        print("%s  %-6s 장전 %s → %s · R2 %s%s · 거래 %d건 · 순 %s원%s" % (
            d, p["product"],
            ("%+.0f" % dec["pm_sp"]) if dec.get("pm_sp") is not None else "미수집",
            {-1: "하방", 0: "보류", 1: "상방"}.get(dec.get("bias"), "?"),
            dec.get("r2") or "-", (" " + dec["r2_ts"]) if dec.get("r2_ts") else "",
            len(p["trades"]), format(net, "+,.0f"),
            (" · " + " / ".join(dec["notes"])) if dec.get("notes") else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
