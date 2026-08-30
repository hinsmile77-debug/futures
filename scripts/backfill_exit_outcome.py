# -*- coding: utf-8 -*-
"""exit_outcome 소급 채움 — 2026-08-14 이전 구간(215행).

## 왜

468차 G-3이 청산 라벨을 트리거/결과 2축으로 분리하면서 `exit_trigger`/`exit_outcome`을
신설했으나, 기록은 **2026-08-14부터**다. 그 이전 구간은 두 컬럼이 NULL이라
"손실6일 vs 대조군" 같은 2축 집계가 8월 전체를 덮지 못한다(2026-08-30 조사에서
08-03·08-05·08-10·08-11이 통째로 빠졌다).

## 무엇을 채우고 무엇을 안 채우는가

- **`exit_outcome`은 채운다.** 라이브 기록 구간 전수(143행)에서 `exit_outcome`이
  `gross_pnl_krw` 부호와 **100% 일치**한다(양→'이익', 그 외→'손실'). 즉 결과 축은
  파생값이며 소급 복원이 결정적이다. 스크립트가 실행 전에 이 규칙을 재검증하고,
  한 행이라도 어긋나면 중단한다.

- 🔴 **`exit_trigger`는 채우지 않는다.** `exit_reason`만으로 복원되지 않는다:

      하드스톱(틱) + 이익  → 보호트레일 49
      하드스톱(틱) + 손실  → 하드스톱 29 / 보호트레일 3   ← 갈린다(오류율 9.4%)
      하드스톱     + 손실  → 라이브 사례 0건              ← 매핑 근거 자체가 없다

  추정으로 채우면 계측 4원칙 ②("미측정 ≠ 0")를 정면으로 어긴다. 트리거 축은
  2026-08-14 이후 구간에서만 집계할 것.

## 계측 4원칙 ④ (폴백 가시화)

소급분과 라이브 기록분을 구분할 수 있어야 한다. `exit_outcome_source` 컬럼을
추가해 `'live'` / `'backfill_20260830'`으로 표시한다. **이 컬럼 없이 exit_outcome을
집계하지 말 것** — 소급분은 트리거 축이 비어 있어 성격이 다르다.

## 사용

    python scripts/backfill_exit_outcome.py --dry-run   # 변경 없이 계획만 출력
    python scripts/backfill_exit_outcome.py             # 실제 반영 (백업 자동 생성)

롤백: 생성된 `data/db/trades.db.bak_<타임스탬프>_pre_outcome_backfill` 로 되돌린다.
반드시 장 종료 후(또는 미실행 시)에 돌릴 것.

근거: 2026-08-30 조사, `dev_memory/DECISION_LOG.md` 참조.
"""
import argparse
import os
import shutil
import sqlite3
import sys
import time

DB = os.path.join("data", "db", "trades.db")
TAG = "backfill_20260830"


def outcome_expr():
    """라이브 구간에서 검증된 결과 축 파생 규칙."""
    return "CASE WHEN gross_pnl_krw > 0 THEN '이익' ELSE '손실' END"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=DB)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(args.db):
        sys.exit("DB 없음: %s" % args.db)

    con = sqlite3.connect(args.db)
    con.isolation_level = None
    cur = con.cursor()

    # ── 1) 사전 검증: 라이브 기록이 규칙과 어긋나면 중단 ──────────────────────
    live = cur.execute(
        "SELECT COUNT(*) FROM trades WHERE exit_outcome IS NOT NULL"
    ).fetchone()[0]
    mismatch = cur.execute(
        "SELECT COUNT(*) FROM trades WHERE exit_outcome IS NOT NULL "
        "AND exit_outcome <> (%s)" % outcome_expr()
    ).fetchone()[0]
    print("사전검증: 라이브 기록 %d행 중 규칙 불일치 %d행" % (live, mismatch))
    if live == 0:
        sys.exit("라이브 표본이 없어 규칙을 검증할 수 없다 — 중단")
    if mismatch:
        sys.exit(
            "규칙 불일치 %d행 — exit_outcome이 gross 부호의 파생값이 아니다. "
            "소급 규칙을 재설계할 것." % mismatch
        )

    todo = cur.execute(
        "SELECT COUNT(*) FROM trades WHERE exit_outcome IS NULL "
        "AND gross_pnl_krw IS NOT NULL"
    ).fetchone()[0]
    skip = cur.execute(
        "SELECT COUNT(*) FROM trades WHERE exit_outcome IS NULL "
        "AND gross_pnl_krw IS NULL"
    ).fetchone()[0]
    print("소급 대상 %d행 (gross NULL이라 제외되는 행 %d)" % (todo, skip))

    if args.dry_run:
        print("\n[dry-run] 변경 없음. 소급 시 분포:")
        for row in cur.execute(
            "SELECT (%s) AS oc, COUNT(*) FROM trades "
            "WHERE exit_outcome IS NULL AND gross_pnl_krw IS NOT NULL "
            "GROUP BY 1" % outcome_expr()
        ):
            print("  %-4s %d행" % row)
        return

    # ── 2) 백업 ────────────────────────────────────────────────────────────────
    bak = "%s.bak_%s_pre_outcome_backfill" % (args.db, time.strftime("%Y%m%d_%H%M%S"))
    shutil.copy2(args.db, bak)
    print("백업 생성: %s" % bak)

    # ── 3) 출처 컬럼 + 기존 라이브 행 태깅 ──────────────────────────────────────
    cols = [r[1] for r in cur.execute("PRAGMA table_info(trades)")]
    if "exit_outcome_source" not in cols:
        cur.execute("ALTER TABLE trades ADD COLUMN exit_outcome_source TEXT")
        print("컬럼 추가: exit_outcome_source")
    cur.execute(
        "UPDATE trades SET exit_outcome_source='live' "
        "WHERE exit_outcome IS NOT NULL AND exit_outcome_source IS NULL"
    )
    print("라이브 행 태깅: %d행" % cur.execute("SELECT changes()").fetchone()[0])

    # ── 4) 소급 채움 ───────────────────────────────────────────────────────────
    cur.execute("BEGIN")
    cur.execute(
        "UPDATE trades SET exit_outcome = (%s), exit_outcome_source = ? "
        "WHERE exit_outcome IS NULL AND gross_pnl_krw IS NOT NULL" % outcome_expr(),
        (TAG,),
    )
    n = cur.execute("SELECT changes()").fetchone()[0]
    cur.execute("COMMIT")
    print("소급 채움: %d행" % n)

    # ── 5) 사후 검증 ───────────────────────────────────────────────────────────
    print("\n사후 검증")
    for row in cur.execute(
        "SELECT COALESCE(exit_outcome_source,'(NULL)'), COALESCE(exit_outcome,'(NULL)'), "
        "COUNT(*) FROM trades GROUP BY 1,2 ORDER BY 1,2"
    ):
        print("  %-20s %-4s %4d" % row)
    still = cur.execute(
        "SELECT COUNT(*) FROM trades WHERE exit_trigger IS NULL"
    ).fetchone()[0]
    viol = cur.execute(
        "SELECT COUNT(*) FROM trades WHERE exit_outcome IS NOT NULL "
        "AND exit_outcome <> (%s)" % outcome_expr()
    ).fetchone()[0]
    print("  exit_trigger 미채움(의도적): %d행" % still)
    print("  규칙 위반: %d행" % viol)
    con.close()


if __name__ == "__main__":
    main()
