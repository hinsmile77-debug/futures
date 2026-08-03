# -*- coding: utf-8 -*-
"""[MW0602 423차] 백필 행 노출도 스캐너 — 오프라인 재생·재보정 경로 공통 점검.

## 왜 만들었나

`scripts/backfill_features.py`는 결측일을 소급 생성하면서 **호가·수급·옵션·매크로를
전부 0.0으로 채우고** 그 행에 `feature_quality_score = 0.3` 마커를 박는다
(backfill_features.py:341). 가격에서 유도되는 피처(atr·hurst·time_* 등)는 정상이지만
미시구조 피처는 전부 상수 0.0이다.

2026-08-03에 이 행들이 RegimeFingerprint PSI를 7거래일 연속 100% CRITICAL로
고착시킨 것이 확인됐다(학습 모집단의 62%가 백필 → `ofi_norm` 0.0 점질량 63.3%,
라이브는 1.6%). 371차가 균등폭→분위수 비닝으로 재설계했는데도 안 풀린 이유가
비닝이 아니라 **모집단**이었다.

같은 뿌리를 공유하는 소비자가 더 있는지 확인하려고 만든 **읽기 전용 계측 도구**다.

## 무엇을 하지 않는가

**일괄 제외를 처방하지 않는다.** 백필 행은 균질하게 나쁘지 않다 —
가격계 피처는 유효하므로 GBM 학습 표본으로서의 가치가 있다. 어떤 소비자가 어떤
피처를 쓰는지에 따라 판단이 달라지므로, 이 스크립트는 **노출도만 재고** 결론은
사람이 내린다("계측 먼저, 그다음 배선").

실행: python scripts/scan_backfill_exposure.py
      python scripts/scan_backfill_exposure.py --days 180
"""
import argparse
import io
import json
import os
import sqlite3
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BACKFILL_MARKER = 0.3

# raw_features를 읽는 오프라인 소비자 목록. 새 소비자가 생기면 여기 추가할 것.
#   name        : 표시용
#   where       : 코드 위치
#   features    : 그 소비자가 실제로 꺼내 쓰는 피처
#   window      : 그 소비자의 **실제 조회 창**. ("rows", N) = 최신 N행,
#                 ("days", N) = 최신 N거래일. 이걸 반영하지 않으면 오탐이 난다 —
#                 최신 N행만 읽는 소비자는 최근 구간이 전부 라이브라 백필 노출이 0인데,
#                 26주 창으로 재면 "노출 77%"라고 잘못 뜬다(초판 스캐너의 실제 오류).
#   verdict     : 백필 혼입이 그 소비자에게 갖는 의미(사람이 판단해 적어둔 값)
CONSUMERS = [
    {
        "name": "RegimeFingerprint 학습분포 (PSI 기준선)",
        "where": "retrain_eod.py:354",
        "features": ["cvd_divergence", "vwap_position", "ofi_norm"],
        "window": ("days", 182),          # GBM 학습 X를 그대로 재사용
        "verdict": "치명 — 423차에 백필 제외 적용함",
    },
    {
        "name": "ATR ceiling 재보정",
        "where": "learning/atr_ceiling_recalibrator.py:197",
        "features": ["atr"],
        "window": ("days", 15),           # LOOKBACK_TRADING_DAYS = 15
        "verdict": "무해 추정 — atr은 가격 유도라 백필도 유효",
    },
    {
        "name": "ATR multiple 재보정",
        "where": "learning/atr_multiple_recalibrator.py:154",
        "features": ["atr", "toxicity_atr_stress"],
        "window": ("days", 15),
        "verdict": "확인 필요 — toxicity_* 는 미시구조 계열",
    },
    {
        "name": "ScalerWarmup (배치 재학습 스케일러)",
        "where": "learning/batch_retrainer.py:1278",
        "features": ["ofi_norm", "cvd_divergence", "spread_ticks",
                     "toxicity_score", "vwap_position"],
        "window": ("rows", 500),          # ORDER BY ts DESC LIMIT lookback_bars
        "verdict": "확인 필요 — 0.0 상수는 scale을 눌러 z-score를 부풀린다",
    },
    {
        "name": "GBM 학습 X (26주 WFA)",
        "where": "learning/batch_retrainer.py:1776",
        "features": ["ofi_norm", "cvd_divergence", "opt_pcr_norm",
                     "foreign_futures_net", "spread_ticks"],
        "window": ("days", 182),
        "verdict": "기등록 이슈 — NEXT_TODO 417차(백필 UPDATE 여부)와 같은 뿌리",
    },
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=182,
                    help="점검 창(일). 기본 182 = 26주 WFA 창")
    ap.add_argument("--db", default=os.path.join("data", "db", "raw_data.db"))
    args = ap.parse_args()

    if not os.path.exists(args.db):
        print("DB 없음: %s" % args.db)
        return 2

    con = sqlite3.connect(args.db)
    days = [r[0] for r in con.execute(
        "SELECT DISTINCT substr(ts,1,10) d FROM raw_features ORDER BY d DESC LIMIT ?",
        (args.days,))]
    if not days:
        print("raw_features 비어 있음")
        return 2
    since = min(days)

    wanted = sorted({f for c in CONSUMERS for f in c["features"]})
    n_bf = n_lv = 0
    # feature -> [백필 0.0수, 백필 총수, 라이브 0.0수, 라이브 총수]
    acc = defaultdict(lambda: [0, 0, 0, 0])
    for (fj,) in con.execute(
            "SELECT features FROM raw_features WHERE ts >= ? ORDER BY ts",
            (since + " 00:00:00",)):
        try:
            d = json.loads(fj)
        except Exception:
            continue
        is_bf = abs(float(d.get("feature_quality_score", 1.0)) - BACKFILL_MARKER) < 1e-9
        if is_bf:
            n_bf += 1
        else:
            n_lv += 1
        for f in wanted:
            v = d.get(f)
            if v is None:
                continue
            z = 1 if abs(float(v)) < 1e-12 else 0
            a = acc[f]
            if is_bf:
                a[0] += z; a[1] += 1
            else:
                a[2] += z; a[3] += 1

    total = n_bf + n_lv
    print("=" * 78)
    print("백필 행 노출도 스캔 — 최근 %d 거래일 (%s ~)" % (len(days), since))
    print("=" * 78)
    print("모집단 %d행 = 백필 %d (%.1f%%) + 라이브 %d (%.1f%%)"
          % (total, n_bf, 100.0 * n_bf / total, n_lv, 100.0 * n_lv / total))
    print()
    # 판정 기준: **백필 행에서 사실상 전부 0.0인가**(≥99%). 라이브와의 격차가 아니라
    # 이것으로 보는 이유 — 격차 기준은 라이브 자체의 0.0 비율이 높은 피처
    # (toxicity_atr_stress: 라이브 53.8%)를 놓친다. 그 피처도 백필에선 100% 0.0이라
    # "백필에서 계산되지 않는다"는 사실은 똑같다.
    DEAD_PCT = 99.0
    print("[피처별 0.0 비율] 백필에서 %.0f%% 이상 0.0이면 그 피처는 백필에서 계산되지 않는다"
          % DEAD_PCT)
    print("%-26s %12s %12s %10s" % ("피처", "백필 0.0%", "라이브 0.0%", "격차"))
    print("-" * 62)
    dead = set()
    for f in wanted:
        a = acc[f]
        if not a[1] or not a[3]:
            print("%-26s %12s %12s %10s" % (f, "-" if not a[1] else "", "-", "표본없음"))
            continue
        pb, pl = 100.0 * a[0] / a[1], 100.0 * a[2] / a[3]
        gap = pb - pl
        if pb >= DEAD_PCT:
            dead.add(f)
        print("%-26s %11.1f%% %11.1f%% %+9.1f%%%s"
              % (f, pb, pl, gap, "  ← 백필에서 죽음" if pb >= DEAD_PCT else ""))

    print()
    print("[소비자별 판정] — 각자의 실제 조회 창에서 백필 비중을 다시 잰다")
    print("-" * 78)
    for c in CONSUMERS:
        kind, n = c["window"]
        if kind == "rows":
            rows = con.execute(
                "SELECT features FROM raw_features ORDER BY ts DESC LIMIT ?", (n,))
            win_desc = "최신 %d행" % n
        else:
            wdays = [r[0] for r in con.execute(
                "SELECT DISTINCT substr(ts,1,10) d FROM raw_features "
                "ORDER BY d DESC LIMIT ?", (n,))]
            wsince = min(wdays) if wdays else "1970-01-01"
            rows = con.execute(
                "SELECT features FROM raw_features WHERE ts >= ? ORDER BY ts",
                (wsince + " 00:00:00",))
            win_desc = "최신 %d거래일 (%s ~)" % (len(wdays), wsince)

        w_bf = w_tot = 0
        for (fj,) in rows:
            try:
                d = json.loads(fj)
            except Exception:
                continue
            w_tot += 1
            if abs(float(d.get("feature_quality_score", 1.0)) - BACKFILL_MARKER) < 1e-9:
                w_bf += 1
        w_pct = (100.0 * w_bf / w_tot) if w_tot else 0.0

        hit = [f for f in c["features"] if f in dead]
        # 노출 = 죽은 피처를 쓰면서 **그 창에 백필이 실제로 들어 있을 때만** 성립한다.
        exposed = bool(hit) and w_pct > 0.0
        print("%s %s" % ("⚠" if exposed else "·", c["name"]))
        print("    위치: %s" % c["where"])
        print("    조회 창: %s → 백필 %d/%d (%.1f%%)" % (win_desc, w_bf, w_tot, w_pct))
        print("    사전판정: %s" % c["verdict"])
        if not hit:
            print("    실측: 사용 피처 중 백필에서 죽은 것 없음 → 무해")
        elif not exposed:
            print("    실측: 죽은 피처 %s 를 쓰지만 **이 창에 백필이 0건** → 무해"
                  % ", ".join(hit))
        else:
            print("    실측: 노출 — 백필에서 죽은 피처 %d개(%s)가 %.1f%% 백필 구간에 섞임"
                  % (len(hit), ", ".join(hit), w_pct))
        print()

    print("=" * 78)
    print("이 스크립트는 판단하지 않는다 — 위 '실측'을 보고 소비자별로 결정할 것.")
    print("백필 행은 가격계 피처(atr·hurst 등)는 유효하므로 일괄 제외가 정답이 아니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
