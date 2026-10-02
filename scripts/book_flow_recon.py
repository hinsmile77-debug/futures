# -*- coding: utf-8 -*-
"""[MW0601 654차] `book_flow_bars` 일별 대사 — 호가 흐름 분해 섀도가 헛돌지 않는가.

무엇을 보는가 (계측 4원칙 ⑤ — 모든 축을 건다)
--------------------------------------------
1. **적재율** — 같은 날 `session_bars`(source='rt') 봉 중 흐름 행이 있는 비율.
   흐름 행이 0 이면 배선이 죽은 것이다(552차 초판 `raw_candles` 영구 NULL 과 같은 계열).
2. **항등식** — `ask_exec + bid_exec + unmatched == trade_qty` 위반 행 수. 0 이어야 한다.
3. **체결 커버리지** — Σtrade_qty / Σvolume. 1 을 넘으면 체결 이중 계상이다.
   봉 경계 근사 때문에 행 단위로는 어긋날 수 있으나 일 합계는 1 근처여야 한다.
4. **미귀속 비율** — Σunmatched / Σtrade_qty. 크면 「관측 가능」 판정이나 체결 순서
   근사가 깨진 것이다.
5. **건수 가용률** — Σcnt_pairs / Σpairs. 0 이면 원천이 건수를 안 준다(경고 로그 확인).
6. 참고: 일 합계 취소 하한·체결 (매도/매수).

판정은 하지 않는다 — 섀도 10거래일 뒤 첫 질문(매도벽 소멸 시 체결 vs 취소 비중)을
던지기 전에 **원천이 정상인지**만 확인한다.

🔴 장중 금지(456차) — `guard_intraday` 로 rc=2 종료.

실행
    python scripts/book_flow_recon.py                 # 최근 10거래일
    python scripts/book_flow_recon.py --days 30
종료코드: 0 정상 · 1 이상 발견(적재 0 · 항등식 위반 · 커버리지 > 1.05) · 2 장중 차단
"""
from __future__ import print_function

import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.dll_bootstrap import ensure_conda_dll_path  # noqa: E402

ensure_conda_dll_path()

import argparse  # noqa: E402

from utils.analysis_db import guard_intraday, connect_ro  # noqa: E402

CHANNEL = "book_flow_recon"
COVERAGE_MAX = 1.05   # 사전등록 — 일 합계 체결 커버리지 상한


def run(db_path, days):
    con = connect_ro(db_path)
    try:
        has = con.execute("SELECT 1 FROM sqlite_master WHERE type='table' "
                          "AND name='book_flow_bars'").fetchone()
        if not has:
            print("book_flow_bars 테이블 없음 — 654차 코드가 아직 기동되지 않았다.")
            return 1
        _first = con.execute("SELECT MIN(ts) FROM book_flow_bars").fetchone()[0]
        if _first is None:
            # 배포 직후 첫 장중 전 — 이상이 아니다. 비어 있는 것을 숨기지도 않는다.
            print("book_flow_bars 0행 — 654차 코드로 장중을 아직 한 번도 돌지 않았다. "
                  "첫 거래일 장후에 다시 실행할 것.")
            return 0
        print("첫 흐름 행: %s (그 이전 날짜의 0행은 정상)\n" % _first)
        day_rows = con.execute(
            "SELECT DISTINCT substr(ts,1,10) d FROM session_bars WHERE source='rt' "
            "ORDER BY d DESC LIMIT ?", (days,)).fetchall()
        days_list = sorted(r[0] for r in day_rows)
        bad = False
        print("| 날짜 | rt봉 | 흐름행 | 적재율 | 항등식위반 | 체결커버 | 미귀속 | 건수가용 | "
              "매도 체결/취소LB | 매수 체결/취소LB |")
        print("|---|---|---|---|---|---|---|---|---|---|")
        for d in days_list:
            n_rt = con.execute("SELECT COUNT(*) FROM session_bars WHERE source='rt' "
                               "AND substr(ts,1,10)=?", (d,)).fetchone()[0]
            r = con.execute(
                """SELECT COUNT(*), SUM(pairs), SUM(cnt_pairs), SUM(trade_qty),
                          SUM(exec_unmatched_qty),
                          SUM(ask_exec_qty), SUM(ask_cancel_qty_lb),
                          SUM(bid_exec_qty), SUM(bid_cancel_qty_lb),
                          SUM(CASE WHEN pairs>0 AND
                              ask_exec_qty+bid_exec_qty+exec_unmatched_qty != trade_qty
                              THEN 1 ELSE 0 END)
                   FROM book_flow_bars WHERE substr(ts,1,10)=?""", (d,)).fetchone()
            n_bf, pairs, cpairs, trade, unm, ae, ac, be, bc, viol = r
            vol = con.execute(
                """SELECT SUM(s.volume) FROM session_bars s JOIN book_flow_bars b
                   ON s.ts=b.ts WHERE substr(s.ts,1,10)=?""", (d,)).fetchone()[0]
            if not n_bf:
                if n_rt and d >= _first[:10]:
                    print("| %s | %d | 0 | — | — | — | — | — | — | — |" % (d, n_rt))
                continue    # 654차 이전 날짜는 행이 없는 게 정상
            cov = (float(trade or 0) / vol) if vol else None
            unm_r = (float(unm or 0) / trade) if trade else None
            cnt_r = (float(cpairs or 0) / pairs) if pairs else None
            if viol or (cov is not None and cov > COVERAGE_MAX):
                bad = True

            def _pct(x):
                return "—" if x is None else "%.1f%%" % (100.0 * x)
            print("| %s | %d | %d | %s | %d | %s | %s | %s | %s/%s | %s/%s |" % (
                d, n_rt, n_bf, _pct(float(n_bf) / n_rt if n_rt else None), viol or 0,
                _pct(cov), _pct(unm_r), _pct(cnt_r), ae, ac, be, bc))
        recent = [d for d in days_list[-1:]]
        if recent:
            n_last = con.execute("SELECT COUNT(*) FROM book_flow_bars WHERE substr(ts,1,10)=?",
                                 (recent[0],)).fetchone()[0]
            if n_last == 0:
                print("\n⚠ 최근 거래일(%s)에 흐름 행 0 — 배선/기동 확인 필요" % recent[0])
                bad = True
        return 1 if bad else 0
    finally:
        con.close()


def main():

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--days", type=int, default=10)
    ap.add_argument("--db", default=None)
    a = ap.parse_args()
    guard_intraday(CHANNEL)
    from config.settings import RAW_DATA_DB
    sys.exit(run(a.db or RAW_DATA_DB, a.days))


if __name__ == "__main__":
    main()
