# -*- coding: utf-8 -*-
"""[MW0601 552-11] `trades.entry_source` 오귀속 상시 검출기.

무엇을 보는가
-------------
**자동진입이 불가능한 구간에 `entry_source='SYSTEM_AUTO'` 로 기록된 레그.**
절대원칙 §1 에 따라 15:10 이후에는 강제청산만 있고 신규 자동진입이 없다. 그런데
그 구간에 `SYSTEM_AUTO` 진입이 있다면 라벨이 틀린 것이다.

왜 필요한가
-----------
`_entry_source` 는 프로세스 인스턴스 상태였고 `trades` 행은 **청산 시점**에 쓰인다.
진입과 청산 사이에 세션이 바뀌면 `__init__` 기본값 `"SYSTEM_AUTO"` 가 기록된다 —
**포지션은 복원되는데 그것을 해석할 출처는 복원되지 않았다.**

2026-08-28 실측: 15:20:36 외부(수동) 주문 체결(`[체결동기화] 외부진입 SHORT`,
주문번호 3639 — 엔진 `[주문요청]` 없음) → **15:29:55 세션 재시작** → 15:30 청산
3레그가 `SYSTEM_AUTO` 로 기록. net **+656,935원**이 시스템 성과로 계상됐다.
하필 **낙관** 방향이고, 545/546차 「판정 손익을 시스템 자동매매 한정으로」 축이
그만큼 오염된다.

552-11 이 배선을 고쳤지만(포지션 상태 파일에 출처를 실어 재시작을 넘긴다),
**이미 쌓인 행은 그대로다** — 518차 전례에 따라 소급 정정하지 않는다. 그래서
「얼마나 섞여 있는가」를 언제든 다시 셀 수 있어야 한다. 그것이 이 스크립트다.

⚠ **완전한 검출기가 아니다.** 15:10 이전에 진입해 재시작을 겪은 포지션은 여기
걸리지 않는다(그 구간은 정상 자동진입과 구분이 안 된다). 이 값은 **하한**이다 —
계측 4원칙 ③(탈락 가시화)에 따라 그 사실을 출력에 함께 적는다.

실행
----
    python scripts/entry_source_attribution_watch.py
    python scripts/entry_source_attribution_watch.py --json

⚠ 장 마감 후 전용(456차).
"""
from __future__ import print_function

import argparse
import json
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.analysis_db import guard_intraday, connect_ro  # noqa: E402

CHANNEL = "entry_source_attribution_watch"


def _cutoff():
    """자동진입 불가 경계 — 절대원칙 §1 의 강제청산 시각."""
    from config.settings import FORCE_EXIT_TIME
    return str(FORCE_EXIT_TIME)[:5]


def scan(db_path=None):
    if db_path is None:
        from config.settings import TRADES_DB
        db_path = TRADES_DB
    cut = _cutoff()
    con = connect_ro(db_path)
    try:
        rows = con.execute(
            "SELECT entry_ts, exit_ts, quantity, pnl_krw, exit_reason "
            "  FROM trades "
            " WHERE entry_source = 'SYSTEM_AUTO' AND substr(entry_ts,12,5) >= ? "
            " ORDER BY entry_ts", (cut,)).fetchall()
        dist = con.execute(
            "SELECT COALESCE(entry_source,'(NULL)') s, COUNT(*) n "
            "  FROM trades GROUP BY s ORDER BY n DESC").fetchall()
    finally:
        try:
            con.close()
        except Exception:
            pass
    legs = [{"entry_ts": r[0], "exit_ts": r[1], "quantity": r[2],
             "net_krw": float(r[3] or 0), "exit_reason": r[4] or ""} for r in rows]
    return {
        "channel": CHANNEL,
        "cutoff": cut,
        "legs": legs,
        "n_legs": len(legs),
        "n_positions": len(set(l["entry_ts"] for l in legs)),
        "net_krw": sum(l["net_krw"] for l in legs),
        "source_distribution": [{"source": d[0], "n": d[1]} for d in dist],
        "note": ("하한이다 — 15:10 이전 진입 + 재시작 조합은 정상 자동진입과 "
                 "구분되지 않아 여기 걸리지 않는다(계측 4원칙 ③)."),
    }


def main():
    ap = argparse.ArgumentParser(description="entry_source 오귀속 검출 (552-11)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    guard_intraday(CHANNEL)
    res = scan()
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0

    print("=" * 72)
    print("[%s] entry_source 오귀속 — 자동진입 불가 구간(>= %s)의 SYSTEM_AUTO"
          % (CHANNEL, res["cutoff"]))
    print("=" * 72)
    print("entry_source 분포:")
    for d in res["source_distribution"]:
        print("   %-22s %5d" % (d["source"], d["n"]))
    print("-" * 72)
    if not res["legs"]:
        print("✅ 검출 0건 — 이 구간의 SYSTEM_AUTO 라벨 없음")
    else:
        print("🔴 %d레그 / %d포지션 / net %s원"
              % (res["n_legs"], res["n_positions"],
                 "{:+,.0f}".format(res["net_krw"])))
        for l in res["legs"]:
            print("   %s -> %s qty=%d net=%+9.0f  %s"
                  % (l["entry_ts"], l["exit_ts"], l["quantity"], l["net_krw"],
                     l["exit_reason"][:24]))
        print("")
        print("   ⚠ 이 손익은 545/546차 「시스템 자동매매 한정」 판정 축에 섞여 있다.")
        print("     552-11 이 배선을 고쳤으나 **이미 쌓인 행은 그대로다**(518차 전례).")
    print("   %s" % res["note"])
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())
