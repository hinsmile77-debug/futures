# -*- coding: utf-8 -*-
"""당일 맥점 예측 — **과거 날짜 재현 산출·채점** (가이드 §9 Phase 0 검증 / 표본 적립).

[MW0601 534차] `raw_candles` 이력으로 임의 날짜의 08:50 / 09:30 단계를 그날 시점의
정보만으로 재현해 `premarket_levels` 에 굳히고, 실제 고·저로 채점한다.

라이브 산출(`levels_store.ensure_stage`)과 **같은 함수**를 쓴다 — 다른 코드로 재현하면
재현된 것이 무엇인지 알 수 없다. 다른 점은 이력 출처뿐이다(캐시 대신 DB 전 구간, 그
날짜 **이전** 세션만).

⚠ 굳히기는 여기서도 유효하다 — 이미 있는 (date, stage) 행은 건드리지 않는다.
  다시 계산하려면 `--force` (그 행을 지우고 재산출).

실행:
    python scripts/premarket_levels_backfill.py --days 20          # 최근 20거래일
    python scripts/premarket_levels_backfill.py --date 2026-09-04
    python scripts/premarket_levels_backfill.py --days 60 --force
"""

from __future__ import annotations

import argparse
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.analysis_db import guard_intraday
from utils import db_utils
from config.settings import PREMARKET_LEVELS_DB
from features.levels import levels_store as LS
from features.levels import premarket_levels as PL


def backfill(dates, sessions, force=False, quiet=False):
    summaries = [PL.summarize_session(d, bars) for d, bars in sessions]
    PL.fill_derived(summaries)
    bars_by_day = dict(sessions)
    n_new = 0
    for target in dates:
        params = LS.prepare_params(summaries, bars_by_day, target)
        if params is None:
            print("[%s] 이력 부족 — 건너뜀" % target)
            continue
        today_bars = bars_by_day.get(target)
        if not today_bars:
            print("[%s] 당일 봉 없음(품질 제외일 가능) — 건너뜀" % target)
            continue
        if force:
            db_utils.execute(PREMARKET_LEVELS_DB,
                             "DELETE FROM premarket_levels WHERE date = ?", (target,))
        for stage in ("0850", "0930"):
            res = LS.compute_stage(stage, target, today_bars, params)
            # computed_at 은 재현본임을 드러낸다 — 라이브 산출 시각과 헷갈리면 안 된다
            new = db_utils.save_premarket_levels(
                target, stage, "backfill", res["out"], note=res["note"],
                warnings=params.get("warnings"), bars=res["bars"])
            n_new += int(new)
            if not quiet and new and res["out"]:
                for line in LS.format_log_lines(res["out"]):
                    print("  " + line)
            elif not quiet and new:
                print("  [LEVELS %s:%s] 미산출 — %s" % (stage[:2], stage[2:], res["note"]))
        sc = LS.score_day(target)
        if not quiet:
            if sc.get("error"):
                print("[%s] 채점 보류 — %s" % (target, sc["error"]))
            else:
                print("[%s] 실제 고 %.2f 저 %.2f (봉 %d)"
                      % (target, sc["actual_high"], sc["actual_low"], sc["bars"]))
    return n_new


def print_cumulative(days=60):
    agg = LS.cumulative_scores(days)
    if not agg:
        print("누적 채점 없음")
        return
    print("")
    print("| 단계 | n(일) | 거리 MAE pt | 50% | 80%(R̂) | 80% 원구간 | 구조 ±0.5% |")
    print("|---|---|---|---|---|---|---|")
    for stage in sorted(agg):
        a = agg[stage]
        mae = "%.1f" % a["mae"] if a["mae"] is not None else "—"
        c50 = "%.0f%%" % (a["in50"] / a["n"] * 100) if a["n"] else "—"
        c80 = "%.0f%%" % (a["in80"] / a["n"] * 100) if a["n"] else "—"
        craw = "%.0f%%" % (a["in80raw"] / a["nraw"] * 100) if a["nraw"] else "—"
        sh = "%.0f%%" % (a["s_hit"] / a["s_n"] * 100) if a["s_n"] else "—"
        print("| %s:%s | %d | %s | %s | %s | %s | %s |"
              % (stage[:2], stage[2:], a["n"] // 2, mae, c50, c80, craw, sh))
    print("")
    print("> 기대치(144세션 검증): 08:50 MAE 14.2 · 80% 78%(R̂ 83%) / "
          "09:30 MAE 11.0 · 80% 74%(R̂ 81%). 구조 ±0.5% 는 무작위와 같은 ~47% 가 정상 —"
          " 그보다 유의하게 높지 않다고 해서 결함이 아니다(가이드 §8).")


def main(argv=None):
    ap = argparse.ArgumentParser(description="맥점 과거 재현 산출·채점")
    ap.add_argument("--date", action="append", default=[], help="YYYY-MM-DD (반복 가능)")
    ap.add_argument("--days", type=int, default=0, help="최근 N거래일")
    ap.add_argument("--force", action="store_true", help="이미 굳힌 행을 지우고 재산출")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    guard_intraday("premarket_levels_backfill")
    db_utils.init_premarket_levels_db()
    sessions, excluded = LS.load_sessions()
    if not sessions:
        print("이력 없음 — raw_candles 확인")
        return 1
    all_days = [d for d, _ in sessions]
    dates = list(a.date)
    if a.days:
        dates = all_days[-a.days:]
    if not dates:
        dates = all_days[-1:]
    print("이력 %d세션 (%s ~ %s) · 재현 대상 %d일"
          % (len(sessions), all_days[0], all_days[-1], len(dates)))
    n_new = backfill(dates, sessions, force=a.force, quiet=a.quiet)
    print("새로 굳힌 단계 %d개" % n_new)
    print_cumulative(max(a.days, 60))
    return 0


if __name__ == "__main__":
    sys.exit(main())
