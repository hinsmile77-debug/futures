# -*- coding: utf-8 -*-
"""[MW0602 657차] 신동 V4 본전청산 실측 슬립 누적 — 사전등록 V4 §3-2 되돌림 조건 판정. 읽기 전용.

조건(결과 보기 전 고정 — `spec.V4_BE_SLIP_REVIEW_PT`·`V4_BE_SLIP_MIN_N`):
  본전청산 실측 슬립 **평균 > 0.8pt** 이고 표본 **20건 이상** → 「BE3 단독 우위가 사라졌다」 → 재검토(자동 조치 없음).
표본 = 채점 시작(`spec.SCORING_START`)부터, 재생 MAIN(v4 규격 행) 중 청산 사유 BE 이고 실거래와 짝지어진(MATCH) 거래.
슬립 = side × (본전가 − 실청산 평균가), + = 불리. 계산은 `exec_recon.be_exit_slips` 와 같다.

사용: python scripts/shindong_v4_be_slip.py [--since YYYY-MM-DD] [--until YYYY-MM-DD]
"""
import argparse
import datetime as _dt
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from config.settings import SHINDONG_DB, TRADES_DB          # noqa: E402
from strategy.shindong import exec_recon as XR, spec as S, store   # noqa: E402


def _main_rows(sd_db, day):
    rows = []
    for t in store.load_trades(sd_db, day, "MAIN"):
        if t.get("spec_version") != S.SPEC_VERSION:
            continue                                 # v4 규격 행만(그 전 규격은 다른 규칙)
        rows.append(dict(key=t["trade_key"], side=int(t["side"]), entry_ts=str(t["entry_ts"])[11:16],
                         entry_px=float(t["entry_px"]), net=t.get("net_krw"),
                         legs=[(t.get("leg1_exit_ts"), t.get("leg1_exit_px"), t.get("leg1_reason")),
                               (t.get("leg2_exit_ts"), t.get("leg2_exit_px"), t.get("leg2_reason"))]))
    return rows


def collect(since, until, sd_db=SHINDONG_DB, trades_db=TRADES_DB):
    from strategy.runtime import trade_principal as TP
    out, unmeasured = [], []
    d = _dt.date.fromisoformat(since)
    end = _dt.date.fromisoformat(until)
    while d <= end:
        day = d.isoformat()
        d += _dt.timedelta(days=1)
        main_rows = _main_rows(sd_db, day)
        if not main_rows:
            continue
        pos = XR.real_positions(trades_db, day)
        if pos is None:
            unmeasured.append(day)
            continue
        ev = TP.read_jsonl(day, "shindong_exec.jsonl") or XR.events_from_exec_json(
            TP.read_json(day, "shindong_exec.json", {}))
        for x in XR.be_exit_slips(XR.reconcile(main_rows, pos, ev)) or []:
            out.append(dict(x, day=day))
    return out, unmeasured


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default=S.SCORING_START)
    ap.add_argument("--until", default=_dt.date.today().isoformat())
    a = ap.parse_args()
    xs, um = collect(a.since, a.until)
    print("신동 V4 본전청산 실측 슬립 (%s ~ %s, 규격 %s)" % (a.since, a.until, S.SPEC_VERSION))
    for x in xs:
        print("  %s %s %s 본전가 %.2f → 실청산 %.2f · 슬립 %+.2fpt" % (
            x["day"], x["key"], "매수" if x["side"] > 0 else "매도", x["be_px"], x["real_exit_px"], x["slip_pt"]))
    if um:
        print("  대사 원천 없음(미측정) %d일: %s" % (len(um), ", ".join(um)))
    n = len(xs)
    if not n:
        print("판정: 대기 — 표본 0건 (필요 %d건)" % S.V4_BE_SLIP_MIN_N)
        return 0
    m = sum(x["slip_pt"] for x in xs) / n
    print("표본 %d건 · 평균 %+.3fpt · 최악 %+.2fpt" % (n, m, max(x["slip_pt"] for x in xs)))
    if n < S.V4_BE_SLIP_MIN_N:
        print("판정: 대기 — %d/%d건" % (n, S.V4_BE_SLIP_MIN_N))
    elif m > S.V4_BE_SLIP_REVIEW_PT:
        print("판정: **재검토** — 평균 %.3f > %.1fpt (사전등록 V4 §3-2. 자동 조치 없음)" % (m, S.V4_BE_SLIP_REVIEW_PT))
    else:
        print("판정: 유지 — 평균 %.3f ≤ %.1fpt" % (m, S.V4_BE_SLIP_REVIEW_PT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
