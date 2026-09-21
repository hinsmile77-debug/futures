# -*- coding: utf-8 -*-
"""option_flow 결손 구간 백필 — CpSvrNew7222 type 3 페이징.

[MW0601 611차 후속 / 2026-09-21]

왜 필요한가
-----------
라이브 수집기(`collection/cybos/weekly_option_flow.py`)는 매분 **최근 18행**만
받는다. 그래서 프로세스가 늦게 뜨거나 중간에 재기동하면 그 이전 구간이 비어 있다.
실제로 2026-09-21 재기동 직후 DB 의 봉 범위가 `11:42~12:26` 이었다 — 오전이 통째로
없었다.

7222 는 `SetInputValue(3, HHMM)` 으로 **그 시각 직전** 18행을 준다. 그걸 뒤로
밀면서 반복하면 하루 전체가 메워진다. 이 스크립트가 그 일을 한다.

⚠ 한 페이지가 덮는 시간은 상품마다 다르다 — 옵션은 1분 간격이라 18분,
  현물은 1~2분 불규칙이라 26분쯤이다. 그래서 **가장 촘촘한 쪽(18분)** 에 맞춰
  페이지 간격을 잡는다. 넉넉하게 겹치는 것은 문제가 없다(upsert 라 중복은 덮어쓴다).

요청량
------
7상품 x 3주체 x N페이지. 09:00~15:35 전 구간이면 N=22 라 약 460요청이다.
7222 는 **type1(시세) 한도**(15초당 60건)를 쓰고 라이브와 공유하므로,
기본 `--sleep 0.3`(15초당 50건)으로 여유를 둔다.

사용:
    conda run -n py37_32 python scripts/backfill_option_flow.py              # 09:00~현재
    conda run -n py37_32 python scripts/backfill_option_flow.py --from 09:00 --to 11:45
    conda run -n py37_32 python scripts/backfill_option_flow.py --dry-run
    (32-bit 필수)

장중에도 돌 수 있게 열어두되 가드는 건다 — 결손은 보통 장중에 발견되고,
백필은 라이브 DB 가 아니라 별도 option_flow.db 를 쓴다.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.dll_bootstrap import ensure_conda_dll_path   # noqa: E402

ensure_conda_dll_path()

import argparse      # noqa: E402
import datetime      # noqa: E402
import sqlite3       # noqa: E402
import time          # noqa: E402

from utils.analysis_db import guard_intraday            # noqa: E402
from collection.cybos.weekly_option_flow import (       # noqa: E402
    WeeklyOptionFlow, PRODUCTS, INVESTORS,
)

# 한 페이지가 덮는 분 — 옵션(1분 간격 x 18행)이 가장 촘촘하다.
PAGE_SPAN_MIN = 18

# 🔴 요청 한도는 **라이브와 공유한다.** 7222 는 type1(시세) 한도(15초당 60건)를 쓰고,
#   한 페이지가 7상품 x 3주체 = 21요청을 거의 즉시(각 5~7ms) 쏜다. 페이지 사이
#   sleep 만으로는 15초 창에 수백 건이 몰릴 수 있다 — 그러면 내가 한도를 다 써서
#   **미륵이의 수급 수집(7221·8111)이 실패한다.** 매 페이지 전에 잔여 한도를 보고
#   부족하면 원천이 알려주는 시간만큼 기다린다.
QUOTA_TYPE_QUOTE = 1        # CpCybos.GetLimitRemainCount(1) = 시세 요청
QUOTA_MIN_REMAIN = 25       # 한 페이지(21) + 라이브 몫 여유


def wait_for_quota(verbose: bool = False) -> None:
    """잔여 시세요청 한도가 QUOTA_MIN_REMAIN 이상이 될 때까지 기다린다."""
    try:
        from win32com.client import Dispatch
        cyb = Dispatch("CpUtil.CpCybos")
    except Exception:
        time.sleep(1.0)      # 조회 못 하면 보수적으로 쉰다
        return
    waited = 0.0
    while True:
        try:
            remain = int(cyb.GetLimitRemainCount(QUOTA_TYPE_QUOTE))
        except Exception:
            return
        if remain >= QUOTA_MIN_REMAIN:
            if verbose and waited:
                print("      한도 회복 대기 %.1fs (잔여 %d)" % (waited, remain))
            return
        try:
            ms = int(cyb.LimitRequestRemainTime)
        except Exception:
            ms = 1000
        nap = max(ms / 1000.0, 0.3)
        time.sleep(nap)
        waited += nap
        if waited > 60:      # 이상 상황 — 무한 대기하지 않는다
            print("      ⚠ 한도 회복이 60초를 넘겼다 (잔여 %d) — 계속 진행" % remain)
            return


def _hhmm(t: datetime.time) -> int:
    return t.hour * 100 + t.minute


def _parse_hhmm(s: str) -> datetime.time:
    h, m = s.split(":")
    return datetime.time(int(h), int(m))


def build_pages(t_from: datetime.time, t_to: datetime.time):
    """[t_from, t_to] 를 덮는 type 3 시각 목록 (뒤에서 앞으로)."""
    start = t_from.hour * 60 + t_from.minute
    end = t_to.hour * 60 + t_to.minute
    pages = []
    cur = end + 1                      # type3 는 '직전' 을 주므로 +1
    while cur > start:
        pages.append((cur // 60) * 100 + (cur % 60))
        cur -= PAGE_SPAN_MIN
    return pages


def main() -> int:
    ap = argparse.ArgumentParser(description="option_flow 결손 백필")
    ap.add_argument("--from", dest="t_from", default="09:00", help="시작 HH:MM (기본 09:00)")
    ap.add_argument("--to", dest="t_to", default="", help="끝 HH:MM (기본: 현재)")
    ap.add_argument("--date", default="", help="거래일 YYYY-MM-DD (기본: 오늘)")
    ap.add_argument("--sleep", type=float, default=0.3, help="요청 간 대기(초)")
    ap.add_argument("--dry-run", action="store_true", help="페이지만 계산하고 끝낸다")
    ap.add_argument("--db", default="data/db/option_flow.db")
    args = ap.parse_args()

    if not args.dry_run:
        guard_intraday("backfill_option_flow")

    t_from = _parse_hhmm(args.t_from)
    t_to = _parse_hhmm(args.t_to) if args.t_to else datetime.datetime.now().time()
    day = args.date or datetime.date.today().isoformat()
    pages = build_pages(t_from, t_to)
    n_req = len(pages) * len(PRODUCTS) * len(INVESTORS)

    print("백필 %s  %02d:%02d~%02d:%02d" % (day, t_from.hour, t_from.minute,
                                            t_to.hour, t_to.minute))
    # 한도(15초당 60건)가 실질 하한을 정한다 — sleep 보다 이쪽이 크다.
    eta_quota = n_req / 60.0 * 15.0
    print("  페이지 %d개 (간격 %d분) x 상품 %d x 주체 %d = **%d 요청**"
          % (len(pages), PAGE_SPAN_MIN, len(PRODUCTS), len(INVESTORS), n_req))
    print("  예상 %.0f초 (요청한도 15초/60건 기준. sleep 기준은 %.0f초)"
          % (max(eta_quota, n_req * args.sleep), n_req * args.sleep))
    print("  type3 시각: %s%s" % (pages[:6], " …" if len(pages) > 6 else ""))
    if args.dry_run:
        return 0

    # 사전 상태
    def _span():
        try:
            con = sqlite3.connect(args.db)
            row = con.execute(
                "SELECT COUNT(*), MIN(bar_time), MAX(bar_time) "
                "FROM option_investor_flow WHERE trade_date=?", (day,)).fetchone()
            con.close()
            return row
        except Exception:
            return (0, None, None)

    before = _span()
    print("  전: %d행  %s~%s" % before)

    flow = WeeklyOptionFlow(args.db)
    t0 = time.time()
    total = 0
    errs = []
    # 페이지를 바깥 루프로 돌면 같은 COM 객체로 상품·주체를 연속 조회한다.
    for i, pg in enumerate(pages, 1):
        wait_for_quota(verbose=True)          # 라이브 몫을 남기고 진행
        r = flow.fetch_and_store(trade_date=day, pages=(pg,))
        total += r["stored"]
        errs.extend(r["errors"])
        if i % 5 == 0 or i == len(pages):
            print("    %2d/%d 페이지 (t3=%04d) 누적 %d행" % (i, len(pages), pg, total))
        time.sleep(args.sleep)

    after = _span()
    print("  후: %d행  %s~%s" % after)
    print("  소요 %.0f초 · upsert %d건 · 순증 %d행%s"
          % (time.time() - t0, total, after[0] - before[0],
             (" · 오류 %d건" % len(errs)) if errs else ""))
    for e in errs[:3]:
        print("    오류: %s" % e)

    # 결손 점검 — 메웠다고 선언하기 전에 실제로 메워졌는지 본다.
    try:
        con = sqlite3.connect(args.db)
        print("\n  상품별 봉 개수(개인 기준):")
        for p, n, mn, mx in con.execute(
            "SELECT product, COUNT(*), MIN(bar_time), MAX(bar_time) "
            "FROM option_investor_flow WHERE trade_date=? AND investor='individual' "
            "GROUP BY product ORDER BY product", (day,)):
            print("    %-12s %4d봉  %s~%s" % (p, n, mn, mx))
        con.close()
    except Exception as exc:                      # noqa: BLE001
        print("  점검 조회 실패: %s" % exc)
    return 0


if __name__ == "__main__":
    sys.exit(main())
