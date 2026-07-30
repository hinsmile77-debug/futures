# scripts/tp1_geometry_shadow.py
"""[403차 종합 P1-6] TP1/손절 초기 기하 A/B 카운터팩추얼 — 읽기 전용.

무엇을 묻는가
--------------
현행 청산 기하는 손절:TP1 비율이 호라이즌만으로 결정되고 전 레짐에 상시 적용된다.

    stop = ATR × ATR_STOP_MULT(1.5)       × hurst_mult
    TP1  = ATR × ATR_HORIZON_TP1_MULT[hz] × hurst_mult

hurst_mult가 양쪽에 똑같이 곱해져 비율에서 약분되므로 결과는

    1m 5.00:1    3m 3.00:1    5m 2.14:1

이며 trend/neutral/mean-revert 어느 버킷에서도 동일하다. 이 스크립트는 "다른 기하를
썼다면 실현손익이 어땠을까"를 실제 분봉으로 재생해 비교한다.

왜 라이브 코드를 안 건드리는가
------------------------------
필요한 입력이 전부 이미 저장돼 있다 — trades(진입가·방향·호라이즌·hurst·entry_ts),
ensemble_decisions.features(진입 분봉의 atr), raw_candles(고저가). 진입 경로에 섀도
INSERT를 심을 이유가 없고, 심지 않는 만큼 라이브 회귀 위험이 0이다.

무엇을 결론으로 삼을 수 있나 / 없나
-----------------------------------
- 사전등록 기준은 config/settings.py VALIDATION_CAMPAIGN["tp1_geometry_shadow"]에
  **관측 전에** 고정돼 있다. 여기서 기준을 바꾸지 말 것(§9).
- 313차 원칙: min_days 미달이면 판정하지 않는다. 단일일 결과로 기하를 바꾸지 않는다.
- 스톱 축소안은 노이즈 스톱아웃 증가를 동반하므로 승률·최대손실·표준편차를 함께 본다.
- [12] tp1_trail_shadow가 이미 기각한 "TP1 이후 더 느슨한 트레일링"과는 다른 질문이다
  (그건 트레일 폭, 이건 초기 기하).

한계 (반드시 함께 읽을 것)
--------------------------
- 1분봉 고저가 기준이라 봉 내 도달 순서를 알 수 없다. 스톱·TP가 같은 봉에서 모두
  닿으면 보수적으로 STOP을 먼저 적용한다(캠페인 다른 채널과 동일 관례).
- qty=1 포지션의 현행 TP1은 물리적 부분청산이 아니라 보호스톱 전환이다. 여기서는
  비교 가능성을 위해 모든 변형에서 "TP1 도달 = 그 가격에 전량 청산"으로 단순화한다.
  따라서 현행(current)의 시뮬 손익은 실제 실현손익과 다르며, 변형 간 상대비교로만
  읽어야 한다. 절대값을 실적으로 인용하지 말 것.
- 슬리피지·수수료는 왕복 1회분만 차감한다(캠페인 공통 가정).

사용법
------
    python scripts/tp1_geometry_shadow.py [--since 2026-06-01] [--horizon 5m]
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import (  # noqa: E402
    TRADES_DB, PREDICTIONS_DB, RAW_DATA_DB,
    ATR_STOP_MULT, ATR_TP1_MULT, ATR_HORIZON_TP1_MULT,
    HURST_REGIME_ATR_MULT, HURST_REGIME_ATR_MULT_ENABLED,
    VALIDATION_CAMPAIGN,
)
from config.constants import MINI_FUTURES_PT_VALUE  # noqa: E402

_TS_FMT = "%Y-%m-%d %H:%M:%S"
_CR = VALIDATION_CAMPAIGN.get("tp1_geometry_shadow", {})
_MAX_HOLD_MIN = 45          # 최대 보유 분 (미도달 시 그 시점 종가로 마감)
_COST_PTS = 0.10            # 왕복 비용 가정 (수수료+슬리피지, pt) — 보수적 근사


def _load_candles(since: str):
    hi, lo, cl = {}, {}, {}
    with sqlite3.connect(RAW_DATA_DB) as c:
        for ts, h, l, k in c.execute(
            "SELECT ts, high, low, close FROM raw_candles WHERE ts >= ?", (since,)
        ):
            hi[ts], lo[ts], cl[ts] = h, l, k
    return hi, lo, cl


def _load_atr_map(since: str):
    """진입 분봉의 atr — ensemble_decisions.features(JSON)에서 뽑는다."""
    out = {}
    with sqlite3.connect(PREDICTIONS_DB) as c:
        for ts, feat in c.execute(
            "SELECT ts, features FROM ensemble_decisions WHERE ts >= ? AND features IS NOT NULL",
            (since,),
        ):
            try:
                v = json.loads(feat).get("atr")
            except (ValueError, TypeError):
                continue
            if v:
                out[ts] = float(v)
    return out


def _load_trades(since: str, horizon=None):
    """부분청산 레그를 entry_ts 기준으로 병합해 '진입 1건'으로 만든다."""
    src = _CR.get("entry_source", "SYSTEM_AUTO")
    sql = (
        "SELECT entry_ts, direction, entry_price, entry_horizon, hurst_bucket, "
        "       SUM(COALESCE(net_pnl_krw, pnl_krw)) AS krw, SUM(quantity) AS qty "
        "FROM trades WHERE entry_ts >= ? AND exit_ts IS NOT NULL AND entry_source = ? "
    )
    args = [since, src]
    if horizon:
        sql += "AND entry_horizon = ? "
        args.append(horizon)
    sql += "GROUP BY entry_ts, direction, entry_price ORDER BY entry_ts"
    with sqlite3.connect(TRADES_DB) as c:
        c.row_factory = sqlite3.Row
        return [dict(r) for r in c.execute(sql, args)]


def _geometry(horizon, hurst_bucket, atr, stop_override, tp1_override):
    """현행 산식 그대로. override가 주어지면 그 배수로 대체한다."""
    m = (HURST_REGIME_ATR_MULT.get(hurst_bucket or "", {})
         if HURST_REGIME_ATR_MULT_ENABLED else {})
    stop_mult = ATR_STOP_MULT if stop_override is None else stop_override
    tp1_base = ATR_HORIZON_TP1_MULT.get(horizon, ATR_TP1_MULT)
    tp1_mult = tp1_base if tp1_override is None else tp1_override
    return (atr * stop_mult * m.get("stop", 1.0),
            atr * tp1_mult * m.get("tp1", 1.0))


def _simulate(entry_ts, is_long, entry_px, stop_pts, tp1_pts, hi, lo, cl):
    """분봉 고저가로 STOP/TP1 선후 판정. 동시 도달 시 보수적으로 STOP."""
    base = datetime.datetime.strptime(entry_ts, _TS_FMT).replace(second=0)
    stop_px = entry_px - stop_pts if is_long else entry_px + stop_pts
    tp1_px = entry_px + tp1_pts if is_long else entry_px - tp1_pts
    last = None
    for k in range(1, _MAX_HOLD_MIN + 1):
        mid = base + datetime.timedelta(minutes=k)
        if mid.time() > datetime.time(15, 10):
            break
        key = mid.strftime(_TS_FMT)
        h, l = hi.get(key), lo.get(key)
        if h is None:
            continue
        last = cl.get(key, last)
        hit_stop = (l <= stop_px) if is_long else (h >= stop_px)
        hit_tp = (h >= tp1_px) if is_long else (l <= tp1_px)
        if hit_stop:
            return "STOP", (stop_px - entry_px) if is_long else (entry_px - stop_px)
        if hit_tp:
            return "TP1", (tp1_px - entry_px) if is_long else (entry_px - tp1_px)
    if last is None:
        return None, None
    return "TIMEOUT", (last - entry_px) if is_long else (entry_px - last)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2026-06-01")
    ap.add_argument("--horizon", default=None)
    args = ap.parse_args()

    hi, lo, cl = _load_candles(args.since)
    atr_map = _load_atr_map(args.since)
    trades = _load_trades(args.since, args.horizon)

    variants = _CR.get("variants", {"current": {"stop_mult": None, "tp1_mult": None}})
    res = {name: [] for name in variants}
    days, skipped = set(), 0

    for t in trades:
        ets = t["entry_ts"]
        atr = atr_map.get(ets[:17] + "00") or atr_map.get(ets)
        if not atr:
            skipped += 1
            continue
        is_long = str(t["direction"]).upper() == "LONG"
        px = float(t["entry_price"])
        days.add(ets[:10])
        for name, cfg in variants.items():
            sp, tp = _geometry(t["entry_horizon"], t["hurst_bucket"], atr,
                               cfg.get("stop_mult"), cfg.get("tp1_mult"))
            outcome, pts = _simulate(ets, is_long, px, sp, tp, hi, lo, cl)
            if outcome is None:
                continue
            res[name].append((outcome, pts - _COST_PTS))

    print("=" * 90)
    print("TP1/손절 초기 기하 A/B 카운터팩추얼   기간 %s~   호라이즌 %s"
          % (args.since, args.horizon or "전체"))
    print("사전등록 기준: config/settings.py VALIDATION_CAMPAIGN['tp1_geometry_shadow']")
    print("=" * 90)
    print("진입 %d건 (atr 결측으로 제외 %d건) / 거래일 %d일   왕복비용 가정 %.2fpt"
          % (len(trades) - skipped, skipped, len(days), _COST_PTS))
    print()
    print("%-14s %5s %7s %7s %7s %9s %9s %9s %9s"
          % ("변형", "n", "TP1", "STOP", "만료", "승률", "누적pt", "평균pt", "최대손실"))
    base_total = None
    for name in variants:
        rows = res[name]
        if not rows:
            print("%-14s (표본 없음)" % name)
            continue
        pts = [p for _, p in rows]
        total = sum(pts)
        if name == "current":
            base_total = total
        n_tp = sum(1 for o, _ in rows if o == "TP1")
        n_st = sum(1 for o, _ in rows if o == "STOP")
        n_to = sum(1 for o, _ in rows if o == "TIMEOUT")
        wr = 100.0 * sum(1 for p in pts if p > 0) / len(pts)
        print("%-14s %5d %7d %7d %7d %8.1f%% %+9.2f %+9.3f %+9.2f"
              % (name, len(pts), n_tp, n_st, n_to, wr, total,
                 total / len(pts), min(pts)))

    print()
    if base_total is not None:
        print("현행 대비 차이 (pt / 1계약 환산 원):")
        for name in variants:
            if name == "current" or not res[name]:
                continue
            d = sum(p for _, p in res[name]) - base_total
            print("  %-14s %+8.2f pt   %+12s 원"
                  % (name, d, format(int(d * MINI_FUTURES_PT_VALUE), ",")))

    print()
    n_cur = len(res.get("current", []))
    min_n = int(_CR.get("min_samples", 20))
    min_d = int(_CR.get("min_days", 3))
    if n_cur < min_n or len(days) < min_d:
        print("판정: INSUFFICIENT — n=%d(<%d) 또는 거래일=%d(<%d). "
              "313차 원칙상 결론 내지 않는다." % (n_cur, min_n, len(days), min_d))
    else:
        print("판정 근거는 위 표의 '누적pt'다. 사전등록 기준(PASS=현행 이하 / "
              "FAIL=현행 초과)에 따라 주간회의에서 수동 결정할 것 — 이 스크립트는 "
              "판정을 자동 적용하지 않는다(§9).")
    print()
    print("⚠ current의 절대값은 실제 실현손익이 아니다 — qty=1의 TP1 보호전환을 "
          "'TP1 전량청산'으로 단순화했기 때문. 변형 간 상대비교로만 읽을 것.")


if __name__ == "__main__":
    main()
