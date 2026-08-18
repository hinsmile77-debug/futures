# scripts/position_mfe_shadow.py
"""[MW0601 477차 후속3 / 476차 G-1] 포지션별 MFE/MAE 소급 계측 — 읽기 전용.

무엇을 묻는가
--------------
0818 실측: 진입 7건 전부 방향 적중·전부 SHORT였고 장중 레인지가 73.1pt(5일평균
32.3pt)인 추세일이었는데, 포지션당 평균 보유가 **1.4분**이고 실현은 계약당
**6.85pt**였다. 같은 진입 시점의 +10분 최대유리폭 합은 **43.2pt** —
realized/MFE10 = **0.158**. "청산이 잘했다"와 "청산이 상승분을 절단했다"가
같은 규칙의 양면인지를 재는 축이 지금까지 없었다.

왜 라이브 코드를 안 건드리는가
------------------------------
필요한 입력이 전부 이미 저장돼 있다 — `trades`(entry_ts·direction·entry_price·
entry_qty·pnl_pts) + `raw_candles`(high/low). [25] tp1_protect_offset_shadow와
같은 설계이며 **과거 표본에 소급 적용**된다(신설 즉시 판정 가능, 라이브 회귀 0).

무엇을 결론으로 삼을 수 있나 / 없나
-----------------------------------
- ⚠ **MFE는 사후 최적값이라 도달 불가능한 상한이다.** 비율의 절대수준으로
  "얼마를 놓쳤다"고 말할 수 없다 — **레짐별 상대 비교**로만 읽는다.
  (완벽한 청산이라도 MFE를 100% 취할 수 없다: 스톱 없이 최고점에 파는 것과 같다)
- 사전등록 기준은 `config/settings.py: VALIDATION_CAMPAIGN["position_mfe_shadow"]`에
  관측 전 고정돼 있다. 관측 후 문턱을 바꾸지 말 것(§9).
- 313차 원칙: min_days 미달이면 판정하지 않는다. 0818 하루(n=7·overlap 심각)로는
  어떤 임계도 바꾸지 않는다.

실행:
    python scripts/position_mfe_shadow.py [--since 2026-06-01] [--json]
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from config.settings import TRADES_DB, RAW_DATA_DB, VALIDATION_CAMPAIGN  # noqa: E402

_CR = VALIDATION_CAMPAIGN.get("position_mfe_shadow", {}) or {}
_HORIZONS_MIN = tuple(_CR.get("horizons_min", (5, 10, 20)))
_TREND_MULT = float(_CR.get("trend_day_range_mult", 1.5))
_TREND_LOOKBACK = int(_CR.get("trend_day_lookback", 5))
_RATIO_MAX = float(_CR.get("realized_over_mfe10_median_max", 0.35))


def _conn(p):
    c = sqlite3.connect(p, timeout=15)
    c.row_factory = sqlite3.Row
    return c


def _load_positions(since: str):
    """포지션 단위(entry_ts) 집계 — 레그 단위 금지(계측 4원칙 ①, 417차)."""
    with _conn(TRADES_DB) as c:
        return [dict(r) for r in c.execute(
            """SELECT entry_ts,
                      MAX(direction)   AS direction,
                      MAX(entry_price) AS entry_price,
                      MAX(COALESCE(entry_qty, quantity, 1)) AS entry_qty,
                      SUM(pnl_pts)     AS realized_pts,
                      MAX(exit_ts)     AS last_exit_ts,
                      MAX(entry_horizon) AS entry_horizon,
                      MAX(hurst_bucket)  AS hurst_bucket
                 FROM trades
                WHERE entry_ts >= ? AND entry_ts IS NOT NULL
                GROUP BY entry_ts ORDER BY entry_ts""", (since,))]


def _load_candles(since: str):
    with _conn(RAW_DATA_DB) as c:
        rows = c.execute(
            "SELECT ts, high, low FROM raw_candles WHERE ts >= ? ORDER BY ts",
            (since,)).fetchall()
    return [(r["ts"], float(r["high"]), float(r["low"])) for r in rows]


def _daily_range(bars):
    """{날짜: 그날 레인지 pt} — 추세일 판정용."""
    agg = {}
    for ts, hi, lo in bars:
        d = ts[:10]
        cur = agg.get(d)
        if cur is None:
            agg[d] = [hi, lo]
        else:
            if hi > cur[0]:
                cur[0] = hi
            if lo < cur[1]:
                cur[1] = lo
    return {d: (v[0] - v[1]) for d, v in agg.items()}


def compute(since: str = "2026-06-01") -> dict:
    bars = _load_candles(since)
    if not bars:
        return {"verdict": "INSUFFICIENT", "reason": "raw_candles 없음", "n": 0}
    idx = {t: i for i, (t, _, _) in enumerate(bars)}
    day_range = _daily_range(bars)
    days_sorted = sorted(day_range)

    positions = _load_positions(since)
    rows, skipped = [], 0
    for p in positions:
        ets = p["entry_ts"] or ""
        # entry_ts는 초 해상도, raw_candles는 분 — 분으로 절삭해 맞춘다
        key = ets[:16] + ":00"
        i0 = idx.get(key)
        if i0 is None:
            skipped += 1
            continue
        ep = float(p["entry_price"] or 0.0)
        if ep <= 0:
            skipped += 1
            continue
        is_long = str(p["direction"] or "").upper() == "LONG"
        sgn = 1.0 if is_long else -1.0
        qty = int(p["entry_qty"] or 1) or 1
        # 계약당 실현 — 포지션 합 pnl_pts는 레그별 pt의 합이므로 계약수로 나눈다
        realized_per_ct = float(p["realized_pts"] or 0.0) / qty

        rec = {
            "entry_ts": ets,
            "direction": "LONG" if is_long else "SHORT",
            "entry_qty": qty,
            "entry_horizon": p["entry_horizon"],
            "hurst_bucket": p["hurst_bucket"],
            "realized_per_ct": round(realized_per_ct, 4),
        }
        for h in _HORIZONS_MIN:
            seg = bars[i0: i0 + h + 1]
            if not seg:
                continue
            # SHORT는 low가 유리, LONG은 high가 유리
            best = max((ep - lo) if not is_long else (hi - ep) for _, hi, lo in seg)
            worst = max((hi - ep) if not is_long else (ep - lo) for _, hi, lo in seg)
            rec["mfe%d" % h] = round(best, 4)
            rec["mae%d" % h] = round(worst, 4)
        d = ets[:10]
        rec["day_range_pt"] = round(day_range.get(d, 0.0), 4)
        # 추세일 = 그날 레인지 >= 직전 N거래일 평균 × mult (당일 제외 — 사전 정보만)
        prior = [day_range[x] for x in days_sorted if x < d][-_TREND_LOOKBACK:]
        base = (sum(prior) / len(prior)) if prior else 0.0
        rec["day_range_base_pt"] = round(base, 4)
        rec["is_trend_day"] = bool(base > 0 and rec["day_range_pt"] >= base * _TREND_MULT)
        rows.append(rec)

    out = {
        "n": len(rows), "n_skipped": skipped,
        "days": len({r["entry_ts"][:10] for r in rows}),
        "rows": rows,
    }
    _ratios = [r["realized_per_ct"] / r["mfe10"]
               for r in rows if r.get("mfe10") and r["mfe10"] > 0]
    _tr = [r for r in rows if r["is_trend_day"]]
    _tr_ratios = [r["realized_per_ct"] / r["mfe10"]
                  for r in _tr if r.get("mfe10") and r["mfe10"] > 0]
    out["n_trend_day"] = len(_tr)

    def _median(xs):
        if not xs:
            return None
        s = sorted(xs)
        m = len(s) // 2
        return s[m] if len(s) % 2 else (s[m - 1] + s[m]) / 2.0

    out["realized_over_mfe10_median"] = (
        round(_median(_ratios), 4) if _ratios else None)
    out["realized_over_mfe10_median_trend"] = (
        round(_median(_tr_ratios), 4) if _tr_ratios else None)

    # ── 사전등록 판정(§9, 관측 전 고정) ────────────────────────────────────
    _min_n = int(_CR.get("min_samples", 30))
    _min_d = int(_CR.get("min_days", 15))
    if len(_tr) < _min_n or out["days"] < _min_d:
        out["verdict"] = "INSUFFICIENT"
        out["reason"] = ("추세일 표본 %d/%d · 거래일 %d/%d — 판정 보류(313차)"
                         % (len(_tr), _min_n, out["days"], _min_d))
        return out
    _m = out["realized_over_mfe10_median_trend"]
    out["verdict"] = "FAIL" if (_m is not None and _m < _RATIO_MAX) else "PASS"
    if out["verdict"] == "FAIL":
        out["recommendation"] = (
            "추세일 realized/MFE10 중앙값 %.3f < %.2f — TP1 배수"
            "(ATR_HORIZON_TP1_MULT)·보호전환 폭 재설계를 주간회의 안건으로 "
            "올릴 것. ⚠ MFE는 도달 불가능한 상한이므로 이 비율의 절대수준이 "
            "아니라 레짐 간 상대차로 논의할 것 (§9 사전등록 — 자동 변경 금지)"
            % (_m, _RATIO_MAX))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2026-06-01")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    res = compute(a.since)
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return
    print("[position_mfe_shadow] since=%s" % a.since)
    print("  포지션 %d건 (스킵 %d) / %d거래일 / 추세일 진입 %d건"
          % (res.get("n", 0), res.get("n_skipped", 0),
             res.get("days", 0), res.get("n_trend_day", 0)))
    print("  realized/MFE10 중앙값: 전체 %s / 추세일 %s"
          % (res.get("realized_over_mfe10_median"),
             res.get("realized_over_mfe10_median_trend")))
    print("  판정: %s%s" % (res.get("verdict"),
                          " — " + res["reason"] if res.get("reason") else ""))
    if res.get("recommendation"):
        print("  권고: %s" % res["recommendation"])
    print("  ⚠ MFE는 사후 최적 상한 — 절대수준이 아니라 레짐별 상대 비교로만 읽을 것")


if __name__ == "__main__":
    main()
