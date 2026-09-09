# -*- coding: utf-8 -*-
"""[MW0601 553차 Phase 2] challenger 가상손익의 **비용 세대 정규화**.

무엇을 고치나
-------------
`challenger_trades.pnl_pt` 는 2026-09-10 이전까지 두 가지가 **다 틀린** 공식으로
계산됐다:

  · 편도 수수료율 **`1.5e-05`** 하드코딩 — 493차가 규명한 **키움 잔재**이며
    이 PC(CYBOS) 실제 `9.8104e-05` 의 **1/6.54**
  · **슬리피지 축 없음** — 수수료만 뺐다

참조가 1,050 기준 왕복비용이 **0.0315pt → 0.246018pt (7.8배)** 로 바뀐다.

왜 「행마다 표기」로 끝내지 않고 다시 계산하나
---------------------------------------------
🔴 세대를 섞은 채 두면 `cum_pnl_pt` 같은 집계가 **두 공식의 합**이 된다.
   그건 493차가 지적한 「조용히 그럴듯한 값」 그 자체다.
   가상손익은 `(direction, entry_price, exit_price)` 의 **결정론적 함수**이고
   관측값이 아니다 — 다시 계산해도 잃는 정보가 없다. 그래서 전 행을 현행 모델로
   맞추고, 어떤 모델로 계산했는지를 3열(`commission_rate_used`·`slip_ticks_per_side`·
   `broker_channel`)에 남긴다(계측 4원칙 ④).

⚠ `challenger_daily_metrics` / `challenger_regime_metrics` 는 **통째로 재구축**한다.
  `_compute_and_save_daily()` 의 누적식이 `MAX(cum_pnl_pt) + 오늘분` 이라 날짜별로
  다시 돌리면 **이중 계상**된다. 지우고 날짜 순서대로 한 번에 쌓는 것이 유일하게
  안전한 방법이다.

사용법
------
    python scripts/challenger_cost_normalize.py            # 읽기 전용 진단
    python scripts/challenger_cost_normalize.py --apply    # 실제 반영

⚠ 장중(08:45~15:35) 실행 금지 — 456차. `--apply` 전에 DB 를 백업할 것.
"""
from __future__ import print_function

import argparse
import os
import shutil
import sqlite3
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("MIREUK_TEST_MODE", "1")

from utils.dll_bootstrap import ensure_conda_dll_path  # noqa: E402
ensure_conda_dll_path()

from challenger.challenger_cost import (  # noqa: E402
    LEGACY_KIWOOM_RATE, calc_pnl_pt, cost_context,
)
from config.settings import CHALLENGER_DB  # noqa: E402
from utils.analysis_db import guard_intraday  # noqa: E402


def _conn(path):
    c = sqlite3.connect(path, timeout=30)
    c.row_factory = sqlite3.Row
    return c


def _legacy_pnl(direction, entry, exit_price):
    """구 공식 재현 — 진단에서 「원래 값과 맞는가」를 확인하는 용도."""
    raw = (float(exit_price) - float(entry)) * int(direction)
    commission = (float(entry) + float(exit_price)) * LEGACY_KIWOOM_RATE * 2
    return round(raw - commission, 4)


def diagnose(path, ctx):
    con = _conn(path)
    rows = con.execute(
        "SELECT id, challenger_id, direction, entry_price, exit_price, pnl_pt, "
        "       commission_rate_used "
        "FROM challenger_trades WHERE exit_ts IS NOT NULL ORDER BY id"
    ).fetchall()
    legacy, current, mismatch = [], [], []
    delta_sum = 0.0
    for r in rows:
        new = calc_pnl_pt(r["direction"], r["entry_price"], r["exit_price"], ctx)
        old = r["pnl_pt"]
        if r["commission_rate_used"] is None:
            legacy.append(r["id"])
            if old is not None:
                recon = _legacy_pnl(r["direction"], r["entry_price"], r["exit_price"])
                if abs(recon - float(old)) > 1e-6:
                    mismatch.append((r["id"], float(old), recon))
        else:
            current.append(r["id"])
        if old is not None:
            delta_sum += new - float(old)
    con.close()
    return {
        "n_closed": len(rows), "legacy": legacy, "current": current,
        "mismatch": mismatch, "delta_sum": delta_sum,
    }


def normalize_trades(path, ctx):
    con = _conn(path)
    rows = con.execute(
        "SELECT id, direction, entry_price, exit_price "
        "FROM challenger_trades WHERE exit_ts IS NOT NULL"
    ).fetchall()
    n = 0
    for r in rows:
        pnl = calc_pnl_pt(r["direction"], r["entry_price"], r["exit_price"], ctx)
        con.execute(
            "UPDATE challenger_trades SET pnl_pt=?, commission_rate_used=?, "
            "       slip_ticks_per_side=?, broker_channel=? WHERE id=?",
            (pnl, ctx["one_way_rate"], ctx["slip_ticks_per_side"],
             ctx["broker_channel"], r["id"]),
        )
        n += 1
    con.commit()
    con.close()
    return n


def _mdd(pnls):
    eq = peak = mdd = 0.0
    for p in pnls:
        eq += p
        peak = max(peak, eq)
        mdd = min(mdd, eq - peak)
    return round(mdd, 2)


def _sharpe(pnls):
    if len(pnls) < 3:
        return 0.0
    n = len(pnls)
    avg = sum(pnls) / n
    var = sum((p - avg) ** 2 for p in pnls) / n
    return round(avg / ((var ** 0.5) or 1e-9) * (252 ** 0.5), 2)


def rebuild_metrics(path):
    """일별·레짐별 집계를 **지우고 날짜 순서대로 한 번에** 다시 쌓는다."""
    con = _conn(path)
    con.execute("DELETE FROM challenger_daily_metrics")
    con.execute("DELETE FROM challenger_regime_metrics")

    trades = con.execute(
        "SELECT challenger_id, substr(exit_ts,1,10) AS d, pnl_pt, regime "
        "FROM challenger_trades WHERE exit_ts IS NOT NULL AND pnl_pt IS NOT NULL "
        "ORDER BY exit_ts"
    ).fetchall()
    sig = {}
    for r in con.execute(
        "SELECT challenger_id, substr(ts,1,10) AS d, COUNT(*) AS n "
        "FROM challenger_signals GROUP BY challenger_id, d"
    ):
        sig[(r["challenger_id"], r["d"])] = r["n"]

    by_cd = {}
    for t in trades:
        by_cd.setdefault((t["challenger_id"], t["d"]), []).append(float(t["pnl_pt"]))

    cum, cummdd = {}, {}
    n_daily = 0
    for (cid, d) in sorted(by_cd, key=lambda k: (k[1], k[0])):
        pnls = by_cd[(cid, d)]
        wins = sum(1 for p in pnls if p > 0)
        total = sum(pnls)
        cum[cid] = round(cum.get(cid, 0.0) + total, 2)
        cummdd[cid] = min(cummdd.get(cid, 0.0), _mdd(pnls))
        con.execute(
            "INSERT OR REPLACE INTO challenger_daily_metrics "
            "(date, challenger_id, signal_count, trade_count, win_count, win_rate, "
            " total_pnl_pt, mdd_pt, sharpe, cum_pnl_pt, cum_mdd_pt) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            # ⚠ `signal_count` 는 없으면 **NULL** 이다. 0 으로 채우면 「그날 신호를
            #   기록하지 않았다」가 「신호가 0건이었다」로 위장된다(계측 4원칙 ②).
            #   `challenger_signals` 는 활성 도전자에 대해 매분 1행을 남기므로,
            #   거래가 있는데 신호 행이 없다면 그건 0 이 아니라 **미측정**이다.
            (d, cid, sig.get((cid, d)), len(pnls), wins,
             round(wins / len(pnls) * 100, 2), round(total, 2),
             _mdd(pnls), _sharpe(pnls), cum[cid], cummdd[cid]),
        )
        n_daily += 1

    by_cr = {}
    for t in trades:
        by_cr.setdefault((t["challenger_id"], t["regime"] or "혼합"), []).append(
            float(t["pnl_pt"]))
    n_reg = 0
    for (cid, reg), pnls in by_cr.items():
        wins = sum(1 for p in pnls if p > 0)
        con.execute(
            "INSERT OR REPLACE INTO challenger_regime_metrics "
            "(challenger_id, regime, trade_count, win_count, win_rate, "
            " total_pnl_pt, mdd_pt, sharpe) VALUES (?,?,?,?,?,?,?,?)",
            (cid, reg, len(pnls), wins, round(wins / len(pnls) * 100, 2),
             round(sum(pnls), 2), _mdd(pnls), _sharpe(pnls)),
        )
        n_reg += 1

    con.commit()
    con.close()
    return n_daily, n_reg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="실제 반영(기본은 읽기 전용)")
    ap.add_argument("--db", default=CHALLENGER_DB)
    args = ap.parse_args()

    guard_intraday("challenger_cost_normalize")

    if not os.path.exists(args.db):
        print("[정규화] DB 없음: %s" % args.db)
        return 0

    ctx = cost_context()
    print("[정규화] 현행 비용 모델: 채널=%s 편도=%.8f 슬립=%.1f틱/편도 틱=%.2f"
          % (ctx["broker_channel"], ctx["one_way_rate"],
             ctx["slip_ticks_per_side"], ctx["tick_size"]))
    rt = 2 * 1050.0 * ctx["one_way_rate"] + 2 * ctx["slip_ticks_per_side"] * ctx["tick_size"]
    print("        왕복비용 @1050 = %.6fpt (구 모델 %.6fpt, %.1f배)"
          % (rt, 2 * 1050.0 * LEGACY_KIWOOM_RATE, rt / (2 * 1050.0 * LEGACY_KIWOOM_RATE)))

    d = diagnose(args.db, ctx)
    print("[진단] 청산 %d건 — 구세대 %d · 현세대 %d"
          % (d["n_closed"], len(d["legacy"]), len(d["current"])))
    # ⚠ %-포매팅은 콤마 플래그를 지원하지 않는다(424차 리포트 크래시와 같은 결함).
    #   천단위 구분이 필요하면 format()/f-string 을 쓴다.
    print("       재계산 시 pnl_pt 합계 변화: {:+.4f} pt ({:+,.0f} 원 @50,000/pt)".format(
        d["delta_sum"], d["delta_sum"] * 50000))
    if d["mismatch"]:
        print("       ⚠ 구 공식으로도 재현되지 않는 행 %d건: %s"
              % (len(d["mismatch"]), d["mismatch"][:5]))

    if not args.apply:
        print("[정규화] 읽기 전용 — 반영하려면 --apply")
        return 0

    bak = "%s.bak_%s_pre_cost_normalize" % (args.db, datetime.now().strftime("%Y%m%d"))
    if not os.path.exists(bak):
        shutil.copy2(args.db, bak)
        print("[정규화] 백업 생성: %s" % bak)

    n = normalize_trades(args.db, ctx)
    nd, nr = rebuild_metrics(args.db)
    print("[정규화] 완료 — 거래 %d행 재계산 · 일별집계 %d행 · 레짐집계 %d행 재구축"
          % (n, nd, nr))
    print("🔴 `challenger_trades.pnl_pt` 시계열은 2026-09-10 에 불연속이다. "
          "앞뒤 직접 비교 금지 — 세대는 행마다 commission_rate_used 가 명시한다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
