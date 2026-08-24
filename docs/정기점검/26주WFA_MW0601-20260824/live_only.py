# -*- coding: utf-8 -*-
"""[MW0601 490차 후속3] 순수 라이브 행만으로 L1·L2 재실행 — 490차 후속2 A-1의 조사판.

기존 스크립트는 **수정하지 않는다**(사전등록 판정 경로 무영향). load()만 날짜 필터
버전으로 갈아끼우고 build_matrix/analyze/evaluate는 그대로 재사용한다.

'순수 라이브 일' 정의 = 그날 raw_features 행이 **전부** 라이브인 날.
마커는 418차 정본과 동일: json_extract(features,'$.feature_quality_score') IS NOT 0.3.
혼재일을 행 단위로 걸러내지 않는 이유: L2 simulate_feature가 rows[k+h]로 **인덱스**
기반 청산을 하므로, 하루 안에 구멍이 생기면 'h분 뒤'가 실제로는 더 먼 시각이 되어
손익이 왜곡된다. 실측상 혼재 16일 중 15일은 라이브가 1~5%뿐이라 버려도 손실이 없다.
"""
from __future__ import print_function
import io, json, os, sqlite3, sys, math
import numpy as np

_ROOT = r"C:\Users\82108\PycharmProjects\futures"
sys.path.insert(0, _ROOT)
sys.stdout.reconfigure(encoding="utf-8")

from utils.dll_bootstrap import ensure_conda_dll_path
ensure_conda_dll_path()

from config.settings import FUTURES_COMMISSION_RATE, TICK_SIZE, VALIDATION_CAMPAIGN
from scripts.core_feature_discovery import build_matrix, analyze, HORIZONS, tstat
from scripts.horizon_signal_tradability import evaluate, roundtrip_cost_pt, LEGACY_COST_PT

RAW = os.path.join(_ROOT, "data", "db", "raw_data.db")
PT_VALUE = 50000.0          # 미니선물 1pt = 50,000원
LIVE_SQL = "json_extract(features,'$.feature_quality_score') IS NOT 0.3"


def load_live():
    con = sqlite3.connect(RAW); cur = con.cursor()
    cur.execute("SELECT substr(ts,1,10) d, COUNT(*) n, "
                "SUM(CASE WHEN " + LIVE_SQL + " THEN 1 ELSE 0 END) live "
                "FROM raw_features WHERE ts>='2026-02-10' GROUP BY d ORDER BY d")
    rows = cur.fetchall()
    dates = [d for d, n, l in rows if n == l]
    ds = set(dates)
    lo = dates[0]
    cur.execute("SELECT ts, close FROM raw_candles WHERE ts >= ? ORDER BY ts", (lo,))
    closes = {ts: float(c) for ts, c in cur.fetchall() if c is not None and ts[:10] in ds}
    cur.execute("SELECT ts, features FROM raw_features WHERE ts >= ? ORDER BY ts", (lo,))
    feats = []
    for ts, fj in cur.fetchall():
        if ts[:10] not in ds or ts not in closes:
            continue
        try:
            feats.append((ts, json.loads(fj)))
        except Exception:
            continue
    con.close()
    return feats, closes, dates


def _ser(o):
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        v = float(o)
        return None if math.isnan(v) else v
    raise TypeError(repr(type(o)))


def main():
    feats, closes, dates = load_live()
    print("=" * 100)
    print("순수 라이브 전용 재검증 — %d거래일 (%s ~ %s) · raw_features %d행"
          % (len(dates), dates[0], dates[-1], len(feats)))
    print("=" * 100)
    names, X, ts_list = build_matrix(feats)

    # ── L1 ──────────────────────────────────────────────────────────
    n_tests = len(names) * len(HORIZONS)
    bonf_t = 3.0 + 0.55 * math.log(max(n_tests, 2))
    print("\n다중비교: 검정 %d회 -> Bonferroni 근사 |t| 임계 ~= %.2f" % (n_tests, bonf_t))
    l1 = {}
    for h in HORIZONS:
        res, nd = analyze(names, X, ts_list, closes, h)
        l1[h] = {r["name"]: r for r in res}
        win = [r for r in res if np.isfinite(r["ic_t"]) and abs(r["ic_t"]) > bonf_t and r["stable"]]
        win.sort(key=lambda r: -abs(r["ic_t"]))
        print("  h=%-3d 유효일 %-3d  Bonferroni∧안정 통과 %d개: %s"
              % (h, nd, len(win),
                 ", ".join("%s(IC=%+.3f,t=%.1f)" % (r["name"], r["ic"], r["ic_t"]) for r in win[:12]) or "없음"))
        top = sorted([r for r in res if np.isfinite(r["ic_t"])], key=lambda r: -abs(r["ic_t"]))[:12]
        print("     |t|상위: " + ", ".join("%s(%.1f,n=%d)" % (r["name"], r["ic_t"], r["n_days"]) for r in top))

    # ── L2 ──────────────────────────────────────────────────────────
    horizons = [1, 3, 5, 10, 15, 30]
    avg_price = float(np.mean([closes[t] for t in ts_list if t in closes]))
    cost = roundtrip_cost_pt(avg_price)
    print("\n왕복비용(정본) %.4fpt = %.0f원/계약 | 평균가 %.2f | 1pt=%.0f원"
          % (cost, cost * PT_VALUE, avg_price, PT_VALUE))
    res, days = evaluate(names, X, ts_list, closes, horizons, cost)

    out = []
    for (nm, h), r in res.items():
        for tag, sgn in (("plus", 1), ("minus", -1)):
            s = r[tag]
            if s["t"] is None:
                continue
            out.append(dict(nm=nm, h=h, sgn=sgn, net=s["net_per_day"], t=s["t"],
                            h1=s["net_h1"], h2=s["net_h2"], ntr=r["n_trades"],
                            leg=s["net_per_day_legacy_cost"]))
    passed = [c for c in out
              if c["net"] > 0 and abs(c["t"]) >= 2.0
              and c["h1"] is not None and c["h1"] > 0 and c["h2"] > 0]
    print("\n" + "=" * 100)
    print("L2 손익 — 사전등록 합격선(net/일>0 ∧ |t|>=2 ∧ 전·후반 모두 양수)")
    print("=" * 100)
    print("전체 %d셀 | net>0 %d (%.1f%%) | +|t|>=2 %d | +전후반양수 %d | **합격 %d**"
          % (len(out), len([c for c in out if c["net"] > 0]),
             100.0 * len([c for c in out if c["net"] > 0]) / len(out),
             len([c for c in out if c["net"] > 0 and abs(c["t"]) >= 2]),
             len([c for c in out if c["net"] > 0 and c["h1"] is not None and c["h1"] > 0 and c["h2"] > 0]),
             len(passed)))
    if passed:
        print("\n%-26s %3s %4s %10s %10s %7s %9s %9s %6s"
              % ("feature", "h", "방향", "net/일(pt)", "net/일(원)", "t", "전반", "후반", "거래"))
        for c in sorted(passed, key=lambda c: -c["net"]):
            print("%-26s %3d %+4d %10.4f %10.0f %7.2f %9.4f %9.4f %6d"
                  % (c["nm"], c["h"], c["sgn"], c["net"], c["net"] * PT_VALUE, c["t"], c["h1"], c["h2"], c["ntr"]))

    print("\n=== 호라이즌별 손익 요약 ===")
    print("%3s %6s %9s %12s %12s %9s" % ("h", "셀수", "net>0비율", "net중앙값(pt)", "net중앙값(원)", "거래/일"))
    import statistics
    for h in horizons:
        g = [c for c in out if c["h"] == h]
        if not g:
            continue
        med = statistics.median(c["net"] for c in g)
        print("%3d %6d %8.1f%% %12.3f %12.0f %9.1f"
              % (h, len(g), 100.0 * len([c for c in g if c["net"] > 0]) / len(g),
                 med, med * PT_VALUE, statistics.median(c["ntr"] for c in g) / float(len(days))))

    print("\n=== net/일 상위 15 (합격 여부 무관) ===")
    print("%-26s %3s %4s %10s %10s %7s %9s %9s %6s"
          % ("feature", "h", "방향", "net/일(pt)", "net/일(원)", "t", "전반", "후반", "거래"))
    for c in sorted(out, key=lambda c: -c["net"])[:15]:
        print("%-26s %3d %+4d %10.4f %10.0f %7.2f %9.4f %9.4f %6d"
              % (c["nm"], c["h"], c["sgn"], c["net"], c["net"] * PT_VALUE, c["t"],
                 c["h1"] if c["h1"] is not None else float("nan"),
                 c["h2"] if c["h2"] is not None else float("nan"), c["ntr"]))

    json.dump({"days": len(days), "window": [days[0], days[-1]], "cost_pt": cost,
               "pt_value": PT_VALUE, "n_features": len(names),
               "cells": out, "l1": {str(h): {k: {kk: (None if isinstance(vv, float) and math.isnan(vv) else vv)
                                                 for kk, vv in v.items()} for k, v in l1[h].items()} for h in l1}},
              io.open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, default=_ser)
    print("\nJSON: %s" % sys.argv[1])
    return 0


if __name__ == "__main__":
    sys.exit(main())
