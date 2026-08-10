# -*- coding: utf-8 -*-
"""[MW0601 455차 / 07-30 실행계획 1단계 L2] 신호 거래성 하네스 — 394차 방법론 코드화.

배경: "IC가 유의해도 비용 차감 후 돈이 안 되면 못 쓴다"(189/189 전멸, 394차 —
`docs/미륵이고도화3/방향신호_발굴계획_2026-07-27.md` §1-2). 그 거래성 검정이 문서에만
남아 있어 스크립트로 고정한다(07-30 실행계획 §2-5). **새 방법론을 발명하지 않는다.**

방법론(§1-2 원문 그대로):
  · 신호: 피처의 **당일 러닝 중앙값 대비 상/하** 이진 게이트 — 시점 t까지의 당일 값만
    사용(미래참조 없음)
  · 거래: **비중복** — 체결 후 h분간 신규 진입 금지. 진입 close[t] → 청산 close[t+h]
    (당일 내만 — 오버나이트 제외, 절대원칙 §1)
  · 비용: 왕복비용(pt) 차감 — **캠페인 정본 산식**(generate_validation_campaign_report.
    _roundtrip_cost_pt와 동일: 2×price×수수료율 + 2×슬리피지틱×TICK_SIZE)
  · 집계: 거래 pnl을 **일자 단위 합산 → 일평균 ± t**(372차 — 신호단위 풀링 금지).
    거래가 없는 날은 0으로 포함(전략의 일 단위 손익 관점). 전·후반 분할 병기.

⚠ 비용 가정 두 벌 병기 (검토보고 §3-N1 / 구현계획 §0-3):
  394차 문서의 0.133pt는 슬리피지를 일반선물 틱(0.05) 기준으로 잡은 구 가정이고,
  캠페인 정본 산식은 미니선물 틱(0.02)으로 ~0.07pt다. 어느 쪽을 판정 기준으로 삼을지는
  주간회의 결정 사항 — 그때까지 **둘 다 출력**해 조용한 기준 변경을 막는다.

⚠ 방향(orientation) 주의: +1(피처↑→LONG)·-1 두 방향의 순손익을 모두 출력한다.
  더 좋은 쪽을 고르는 것은 in-sample 선택이므로, 후보 심사에서는 **사전에 예상 부호를
  명세에 적고 그 방향만** 읽을 것(피처_발굴_표준절차 Phase 0 — 예상 부호 명시 요건).

읽기 전용: raw_data.db만 읽는다. 실행: py310_64 오프라인/후보 심사 시. py37_32 호환 문법.
"""
from __future__ import print_function

import argparse
import bisect
import io
import json
import math
import os
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

from config.settings import FUTURES_COMMISSION_RATE, TICK_SIZE, VALIDATION_CAMPAIGN  # noqa: E402
from scripts.core_feature_discovery import load, build_matrix, tstat  # noqa: E402

LEGACY_COST_PT = 0.133  # 394차 문서 가정(일반선물 틱 0.05 기준) — 병기 전용, 정본 아님


def roundtrip_cost_pt(avg_price):
    """왕복 비용(pt) — generate_validation_campaign_report._roundtrip_cost_pt와 동일 산식."""
    slip = float(VALIDATION_CAMPAIGN.get("slippage_ticks_per_side", 1.0))
    return 2.0 * avg_price * FUTURES_COMMISSION_RATE + 2.0 * slip * TICK_SIZE


class RunningMedian(object):
    """당일 러닝 중앙값 — 현재 시점까지의 값만 사용(미래참조 없음)."""

    def __init__(self):
        self._v = []

    def push(self, x):
        bisect.insort(self._v, x)

    def median(self):
        n = len(self._v)
        if n == 0:
            return float("nan")
        if n % 2:
            return self._v[n // 2]
        return 0.5 * (self._v[n // 2 - 1] + self._v[n // 2])


def simulate_feature(day_rows, col, closes_by_i, horizon):
    """단일 (피처, 호라이즌) 거래 시뮬 — 반환 (일자별 gross pnl 합, 거래수).

    day_rows: {date: [행 인덱스 목록(시간순)]}, col: 피처 값 배열(전체 행 기준),
    closes_by_i: 행 인덱스 → close. gross는 orientation +1(피처>중앙값 → LONG) 기준.
    """
    daily_gross = {}
    daily_trades = {}
    for d, rows in day_rows.items():
        rm = RunningMedian()
        gross = 0.0
        n_tr = 0
        next_allowed = 0
        for k, i in enumerate(rows):
            v = col[i]
            if math.isnan(v):
                continue
            rm.push(v)
            if k < next_allowed:
                continue
            if k + horizon >= len(rows):
                continue  # 당일 내 청산 불가 — 세션 경계 절단
            med = rm.median()
            if v > med:
                s = 1.0
            elif v < med:
                s = -1.0
            else:
                continue  # 중앙값 동률 — 신호 없음
            c0 = closes_by_i[rows[k]]
            c1 = closes_by_i[rows[k + horizon]]
            gross += s * (c1 - c0)
            n_tr += 1
            next_allowed = k + horizon  # 비중복
        daily_gross[d] = gross
        daily_trades[d] = n_tr
    return daily_gross, daily_trades


def evaluate(names, X, ts_list, closes, horizons, cost_pt, min_day_rows=60):
    """피처×호라이즌별 거래성 지표. 반환 {(name, h): {...}}."""
    day_rows = defaultdict(list)
    for i, ts in enumerate(ts_list):
        day_rows[ts[:10]].append(i)
    # 표본이 너무 얇은 날 제외(개장 지연·수집 결손일)
    day_rows = {d: r for d, r in day_rows.items() if len(r) >= min_day_rows}
    days = sorted(day_rows)
    closes_by_i = {i: closes[ts] for i, ts in enumerate(ts_list) if ts in closes}

    out = {}
    for j, nm in enumerate(names):
        col = X[:, j]
        for h in horizons:
            dg, dt = simulate_feature(day_rows, col, closes_by_i, h)
            gross = np.array([dg.get(d, 0.0) for d in days], dtype=np.float64)
            ntr = np.array([dt.get(d, 0) for d in days], dtype=np.int64)
            n_total = int(ntr.sum())
            if n_total == 0:
                continue
            cost_daily = ntr * cost_pt
            cost_daily_legacy = ntr * LEGACY_COST_PT
            res = {"n_trades": n_total, "n_days": len(days)}
            for tag, sign in (("plus", 1.0), ("minus", -1.0)):
                net = sign * gross - cost_daily
                net_legacy = sign * gross - cost_daily_legacy
                t, _ = tstat(list(net))
                half = len(days) // 2
                res[tag] = {
                    "net_per_day": float(net.mean()),
                    "t": float(t) if not math.isnan(t) else None,
                    "net_h1": float(net[:half].mean()) if half else None,
                    "net_h2": float(net[half:].mean()) if half else None,
                    "net_per_day_legacy_cost": float(net_legacy.mean()),
                }
            res["gross_per_day_plus"] = float(gross.mean())
            out[(nm, h)] = res
    return out, days


def main():
    ap = argparse.ArgumentParser(description="신호 거래성 하네스 (L2, 읽기 전용)")
    ap.add_argument("--days", type=int, default=120)
    ap.add_argument("--horizons", default="5,15,30",
                    help="쉼표 구분 분 단위 (예: 1,3,5,10,15,30)")
    ap.add_argument("--features", default="",
                    help="쉼표 구분 피처명. 비우면 --all 필요")
    ap.add_argument("--all", action="store_true",
                    help="커버리지 80%%·고유값 20+ 전 피처 스크리닝 (느림)")
    ap.add_argument("--json", default="", help="결과 JSON 출력 경로(선택)")
    args = ap.parse_args()

    # 라이브 DB를 대량 읽는다 — 장중이면 CB⑤를 유발할 수 있어 차단한다(456차 F8).
    from utils.analysis_db import guard_intraday
    guard_intraday("horizon_signal_tradability")

    horizons = [int(x) for x in args.horizons.split(",") if x.strip()]
    feats, closes, dates = load(args.days)
    print("raw_features %d행, %d거래일 (%s ~ %s)" % (len(feats), len(dates), dates[0], dates[-1]))
    names, X, ts_list = build_matrix(feats)
    if args.features:
        want = [s.strip() for s in args.features.split(",") if s.strip()]
        missing = [w for w in want if w not in names]
        if missing:
            print("⚠ 대상에 없음(커버리지/고유값 필터 포함 확인): %s" % ", ".join(missing))
        idx = [names.index(w) for w in want if w in names]
        names = [names[i] for i in idx]
        X = X[:, idx]
    elif not args.all:
        print("--features 또는 --all 지정 필요")
        return 2

    avg_price = float(np.mean([closes[ts] for ts in ts_list if ts in closes]))
    cost = roundtrip_cost_pt(avg_price)
    print("왕복비용(정본 산식, 평균가 %.2f 기준): %.4fpt | 병기(394차 구 가정): %.3fpt"
          % (avg_price, cost, LEGACY_COST_PT))
    print("※ 방향 ± 둘 다 출력 — 더 좋은 쪽 사후 선택은 in-sample. 후보 심사는 예상 부호"
          " 사전 명세 방향만 읽을 것.")

    res, days = evaluate(names, X, ts_list, closes, horizons, cost)
    print()
    hdr = ("%-26s %4s %6s | %+.0f방향: %9s %6s %8s %8s | %+.0f방향: %9s %6s"
           % ("feature", "h", "거래수", 1, "net/일", "t", "전반", "후반", -1, "net/일", "t"))
    print(hdr)
    print("-" * len(hdr))
    for (nm, h) in sorted(res, key=lambda k: (k[1], k[0])):
        r = res[(nm, h)]
        p, m = r["plus"], r["minus"]
        print("%-26s %4d %6d |         %9.4f %6s %8.4f %8.4f |         %9.4f %6s"
              % (nm, h, r["n_trades"],
                 p["net_per_day"], "%.2f" % p["t"] if p["t"] is not None else "-",
                 p["net_h1"] if p["net_h1"] is not None else float("nan"),
                 p["net_h2"] if p["net_h2"] is not None else float("nan"),
                 m["net_per_day"], "%.2f" % m["t"] if m["t"] is not None else "-"))
    print()
    print("합격 참고선(08-02 계획 L2, 관측 전 고정): 일평균 net > 0 이고 t 유의 + 전·후반"
          " 동부호. 구 가정(0.133pt) 열은 JSON에 병기.")

    if args.json:
        payload = {
            "days": len(days), "window": [days[0], days[-1]] if days else None,
            "cost_pt": cost, "cost_pt_legacy": LEGACY_COST_PT, "avg_price": avg_price,
            "results": {"%s@%d" % (nm, h): r for (nm, h), r in res.items()},
        }
        with io.open(args.json, "w", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False, indent=2))
        print("JSON: %s" % args.json)
    return 0


if __name__ == "__main__":
    _utf8_console()
    sys.exit(main())
