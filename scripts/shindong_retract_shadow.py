# -*- coding: utf-8 -*-
"""[MW0601 708차] 신동 철회 섀도 소급·누적 — 「철회 시 본전 이상이면 청산 → 새 신호 수용」 계측.

읽기 전용. 날짜마다 `data/principal/<날짜>/shindong_exec.jsonl`(집행 이벤트) ·
`trades.db`(신동 실거래) · `shindong.db`(재생 MAIN) · SYSTEM 로그(708차 이전 철회 가격)를 읽어
`strategy/shindong/retract_shadow.evaluate()` 로 BE·ALL 섀도 Δ 를 낸다.

    python scripts/shindong_retract_shadow.py                 # 집행 기록이 있는 모든 날
    python scripts/shindong_retract_shadow.py --date 2026-10-22
    python scripts/shindong_retract_shadow.py --be-pts 0.5     # 본전 기준을 바꿔 민감도 확인

⚠ 장중에는 돌리지 않는다(`guard_intraday`) — 라이브 DB 읽기.
"""
import argparse
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.analysis_db import guard_intraday  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", action="append", help="YYYY-MM-DD (반복 가능). 생략 시 전부")
    ap.add_argument("--be-pts", type=float, default=None, help="본전 기준(pt). 생략 시 설정값")
    args = ap.parse_args(argv)
    guard_intraday("shindong_retract_shadow")

    from config import settings as st
    from strategy.runtime import trade_principal as TP
    from strategy.shindong import exec_recon as XR, retract_shadow as RS

    be = args.be_pts if args.be_pts is not None else float(getattr(st, "SHINDONG_RETRACT_SHADOW_BE_PTS", 0.0))
    age = float(getattr(st, "SHINDONG_LIVE_MAX_AGE_MIN", 2))
    trades_db = os.path.join(st.DB_DIR, "trades.db")
    log_dir = os.path.join(_ROOT, "logs")
    dates = args.date or sorted(d for d in os.listdir(TP.DAY_ROOT)
                                if os.path.exists(os.path.join(TP.DAY_ROOT, d, "shindong_exec.jsonl")))
    tot = {"n": 0, "be": 0, "dbe": 0.0, "dall": 0.0, "un": 0}
    for d in dates:
        ev = TP.read_jsonl(d, "shindong_exec.jsonl")
        rp = RS.replay_from_db(st.SHINDONG_DB, d)
        rs = RS.evaluate(d, rp or [], XR.real_positions(trades_db, d), ev,
                         logp=RS.log_prices(d, log_dir), costs=RS.position_costs(trades_db, d),
                         max_age_min=age, be_pts=be)
        if rs is None or not rs["items"]:
            continue
        print("\n## %s" % d)
        print("\n".join(RS.section(rs)))
        tot["n"] += rs["n"]
        tot["be"] += rs["n_be_exit"]
        tot["dbe"] += rs["delta_be"]
        tot["dall"] += rs["delta_all"]
        tot["un"] += rs["n_unmeasured"]
    print("\n## 누적 — 측정 %d건 · BE 청산 %d건 · Δ BE %+.0f원 · Δ ALL %+.0f원 · 미측정 %d건 (be_pts=%+.2f)"
          % (tot["n"], tot["be"], tot["dbe"], tot["dall"], tot["un"], be))
    return 0


if __name__ == "__main__":
    sys.exit(main())
