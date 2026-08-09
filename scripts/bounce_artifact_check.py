# -*- coding: utf-8 -*-
"""[MW0601 455차 / N5] bid-ask bounce 아티팩트 1회성 검증 — 단기 CORE IC의 항등식 성분 추정.

가설(검토보고 §3-N5): 1분 봉 종가는 마지막 체결이 매수/매도 어느 호가에 맞았는지에 따라
최소 1틱 진동한다(bid-ask bounce). CVD·OFI 같은 마이크로구조 피처는 이 진동과 기계적으로
상관되므로(매수 체결 몰림 → 종가가 ask에 찍힘), **1m~5m에서 관측되는 IC의 일부는 알파가
아니라 정의상의 항등식**일 수 있다. CVD·OFI는 단기 CORE라 해석 오류의 파급이 크다.

방법: 동일 피처에 대해 타겟 3벌의 일자단위 IC를 대조(방법론은 core_feature_discovery와 동일).
  ① close  : close[t] → close[t+h]           (현행 — bounce 포함)
  ② open   : open[t+1] → open[t+1+h]          (다음봉 시가 진입 — bounce 제거)
  ③ mid    : (bid1+ask1)/2 기준, 커버리지 80% 이상일 때만 (bounce 제거의 정석)
bounce 성분 ≈ IC_close − IC_open (호라이즌이 짧을수록 커야 가설과 정합).

효력: **CORE 교체 근거 아님**(절대원칙 §3 — CORE 강등은 사용자 승인 사안). 결과는
"단기 IC 해석 시 할인율" 문서화 + 향후 단기 피처 ADD 판정 시 다음봉 시가 IC 병기 여부
결정의 입력. 1회성 실행 후 DECISION_LOG에 기록한다.

읽기 전용: raw_data.db만 읽는다. py37_32 호환·numpy 전용. 실행: py310_64 오프라인 권장.
"""
from __future__ import print_function

import argparse
import io
import json
import math
import os
import sqlite3
import sys
from collections import defaultdict

import numpy as np

_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# [448차 패턴] BLAS DLL 경로 보장 — 반드시 numpy 첫 사용 전. conda 미활성 직접 실행 시
# MKL 지연로드가 0xC06D007F로 프로세스를 즉사시킨다 (455차 재확인: np.polyfit).
from utils.dll_bootstrap import ensure_conda_dll_path  # noqa: E402
ensure_conda_dll_path()

def _utf8_console():
    """cp949 콘솔 인코딩 가드 — CLI 실행 시에만 (import 시 래핑하면 중첩 래퍼로 출력 유실)."""
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from config.settings import RAW_DATA_DB  # noqa: E402
from scripts.core_feature_discovery import rankdata, corr, tstat, MIN_DAY_ROWS  # noqa: E402

HORIZONS = [1, 3, 5]
DEFAULT_FEATURES = ["cvd_divergence", "cvd_delta_norm", "cvd_slope",
                    "ofi_norm", "vwap_position", "microprice_bias"]
MID_COVERAGE_MIN = 0.80


def load(days, feature_names):
    con = sqlite3.connect(RAW_DATA_DB)
    cur = con.cursor()
    cur.execute("SELECT DISTINCT substr(ts,1,10) d FROM raw_features ORDER BY d DESC LIMIT ?",
                (days,))
    dates = sorted(r[0] for r in cur.fetchall())
    cur.execute("SELECT ts, open, close, bid1, ask1 FROM raw_candles "
                "WHERE substr(ts,1,10) >= ? ORDER BY ts", (dates[0],))
    candles = {}
    for ts, o, c, b, a in cur.fetchall():
        if c is None:
            continue
        mid = 0.5 * (float(b) + float(a)) if (b is not None and a is not None
                                              and b > 0 and a > 0) else float("nan")
        candles[ts] = (float(o) if o is not None else float("nan"), float(c), mid)
    cur.execute("SELECT ts, features FROM raw_features WHERE substr(ts,1,10) >= ? ORDER BY ts",
                (dates[0],))
    import json as _json
    feats = []
    for ts, fj in cur.fetchall():
        if ts not in candles:
            continue
        try:
            d = _json.loads(fj)
        except Exception:
            continue
        feats.append((ts, [float(d[k]) if isinstance(d.get(k), (int, float))
                           and not isinstance(d.get(k), bool) else float("nan")
                           for k in feature_names]))
    con.close()
    return feats, candles, dates


def analyze(feats, candles, feature_names, horizon):
    """타겟 3벌의 일자단위 IC. 반환 {name: {"close": (ic,t,nd), "open": ..., "mid": ...}}."""
    by_day = defaultdict(list)
    for i, (ts, _) in enumerate(feats):
        by_day[ts[:10]].append(i)
    days = sorted(by_day)
    nf = len(feature_names)
    acc = {nm: {"close": [], "open": [], "mid": []} for nm in feature_names}
    mid_cov_total = mid_cov_ok = 0

    for d in days:
        rows = by_day[d]
        if len(rows) < MIN_DAY_ROWS + horizon + 1:
            continue
        ts_arr = [feats[i][0] for i in rows]
        opens = np.array([candles[t][0] for t in ts_arr])
        closes = np.array([candles[t][1] for t in ts_arr])
        mids = np.array([candles[t][2] for t in ts_arr])
        mid_cov_total += len(rows)
        mid_cov_ok += int(np.isfinite(mids).sum())
        m = len(rows) - horizon - 1
        if m < MIN_DAY_ROWS:
            continue
        # ① close[t] → close[t+h]
        fwd_close = closes[horizon:horizon + m] - closes[:m]
        # ② open[t+1] → open[t+1+h] (다음봉 시가 진입)
        fwd_open = opens[1 + horizon:1 + horizon + m] - opens[1:1 + m]
        # ③ mid[t] → mid[t+h]
        fwd_mid = mids[horizon:horizon + m] - mids[:m]
        X = np.array([feats[i][1] for i in rows[:m]], dtype=np.float64)
        for j, nm in enumerate(feature_names):
            col = X[:, j]
            for tag, fwd in (("close", fwd_close), ("open", fwd_open), ("mid", fwd_mid)):
                ok = ~np.isnan(col) & np.isfinite(fwd)
                if ok.sum() < MIN_DAY_ROWS or np.unique(col[ok]).size < 3:
                    acc[nm][tag].append(float("nan"))
                    continue
                acc[nm][tag].append(corr(rankdata(col[ok]), rankdata(fwd[ok])))

    mid_cov = mid_cov_ok / float(mid_cov_total) if mid_cov_total else 0.0
    out = {}
    for nm in feature_names:
        out[nm] = {}
        for tag in ("close", "open", "mid"):
            v = np.array(acc[nm][tag], dtype=np.float64)
            t, nd = tstat(list(v))
            vv = v[~np.isnan(v)]
            out[nm][tag] = {"ic": float(vv.mean()) if vv.size else float("nan"),
                            "t": t, "n_days": nd}
    return out, mid_cov


def main():
    ap = argparse.ArgumentParser(description="bid-ask bounce 아티팩트 검증 (1회성, 읽기 전용)")
    ap.add_argument("--days", type=int, default=60)
    ap.add_argument("--features", default=",".join(DEFAULT_FEATURES))
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    feature_names = [s.strip() for s in args.features.split(",") if s.strip()]
    feats, candles, dates = load(args.days, feature_names)
    print("표본 %d행, %d거래일 (%s ~ %s) | 대상 피처 %d개"
          % (len(feats), len(dates), dates[0], dates[-1], len(feature_names)))
    print()

    all_res = {}
    for h in HORIZONS:
        res, mid_cov = analyze(feats, candles, feature_names, h)
        all_res[h] = res
        mid_note = ("" if mid_cov >= MID_COVERAGE_MIN
                    else " (커버리지 %.0f%% < %.0f%% — mid 열 무효)"
                    % (mid_cov * 100, MID_COVERAGE_MIN))
        print("=" * 96)
        print("h=%d분 — 일자단위 IC (부호 유지) | mid 커버리지 %.1f%%%s"
              % (h, mid_cov * 100, mid_note))
        print("%-22s %10s %8s %10s %8s %10s %8s %12s"
              % ("feature", "IC_close", "t", "IC_open", "t", "IC_mid", "t",
                 "bounce성분"))
        for nm in feature_names:
            r = res[nm]
            ic_c, ic_o = r["close"]["ic"], r["open"]["ic"]
            bounce = (ic_c - ic_o) if (not math.isnan(ic_c) and not math.isnan(ic_o)) \
                else float("nan")
            def _f(x, fmt="%+.4f"):
                return fmt % x if isinstance(x, float) and not math.isnan(x) else "-"
            mid_ic = r["mid"]["ic"] if mid_cov >= MID_COVERAGE_MIN else float("nan")
            mid_t = r["mid"]["t"] if mid_cov >= MID_COVERAGE_MIN else float("nan")
            print("%-22s %10s %8s %10s %8s %10s %8s %12s"
                  % (nm, _f(ic_c), _f(r["close"]["t"], "%.2f"),
                     _f(ic_o), _f(r["open"]["t"], "%.2f"),
                     _f(mid_ic), _f(mid_t, "%.2f"), _f(bounce)))
        print()

    print("읽는 법: bounce성분(IC_close−IC_open)이 h가 짧을수록 크면 가설 정합 —")
    print(" 그만큼이 '체결가 정의가 만든 상관'이며 다음봉 시가 실행으로는 잡을 수 없는 부분.")
    print(" ※ CORE 교체 근거 아님(절대원칙 §3) — 단기 IC 해석 할인율 문서화용 1회성 계측.")

    if args.json:
        payload = {"window": [dates[0], dates[-1]], "days": len(dates),
                   "features": feature_names,
                   "results": {str(h): all_res[h] for h in HORIZONS}}
        with io.open(args.json, "w", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False, indent=2))
        print("JSON: %s" % args.json)
    return 0


if __name__ == "__main__":
    _utf8_console()
    sys.exit(main())
