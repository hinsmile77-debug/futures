# scripts/hurst_oos_validation.py
"""
[317차 Phase 2] Hurst 후보 파라미터의 실전 아웃오브샘플(OOS) 검증.

Phase 1(`scripts/hurst_grid_search.py`, 합성데이터)에서 algo=current(기존 variance-scaling
공식 그대로) 유지 + N∈{90,120,150}이 N=60(현재 운영값)보다 편향·분리력 모두 우월함을 확인했다.
이 스크립트는 "그럼 실제 KOSPI200 데이터에서도 그런가"를 라벨링된 실전 구간으로 검증한다.

라벨(정답) 소스: `MicroRegimeClassifier`(ADX/ATR 기반, `collection/macro/micro_regime.py`)의
추세장/횡보장 판정. Hurst와 입력을 전혀 공유하지 않아(ADX·ATR vs 가격 시계열) 순환성이 없다.

검증 질문: 각 (N, max_lag) 후보에서, MicroRegimeClassifier가 "추세장"이라고 확정한 분봉을
Hurst 게이트가 잘못 "횡보(<0.45)"로 오판해 차단하는 비율은 얼마인가 — 이게 이번 딥다이브의
핵심 문제(316차: grade=C 신호의 63%가 Hurst 오탐으로 차단)에 가장 직접적으로 대응하는 지표다.

읽기 전용 진단 — config/settings.py를 자동 변경하지 않는다.

실행 (py37_32 권장 — py310_64는 np.corrcoef 크래시 있음, 317차 Phase 1에서 확인):
    python scripts/hurst_oos_validation.py                 # 기본 60거래일
    python scripts/hurst_oos_validation.py --days 120
    python scripts/hurst_oos_validation.py --out data/daily_reports/hurst_oos_20260713.csv
"""
import argparse
import csv
import sqlite3
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from config.settings import RAW_DATA_DB, HURST_TREND_THRESHOLD, HURST_RANGE_THRESHOLD
from features.technical.hurst_exponent import calculate_hurst
from collection.macro.micro_regime import (
    MicroRegimeClassifier, REGIME_TREND, REGIME_RANGE,
)

# Phase 1 그리드서치 상위 후보(algo=current 고정, 317차 결론) + 현재 운영값(비교 기준선)
CANDIDATES: List[Tuple[int, int, str]] = [
    (60,  20, "current(운영값)"),
    (90,   9, "N=90 1위"),
    (120, 12, "N=120 1위"),
    (150, 15, "N=150 1위(그리드 전체 1위)"),
]


def load_trading_days(days: int, db_path: str = RAW_DATA_DB) -> List[str]:
    conn = sqlite3.connect(db_path, timeout=10)
    cur = conn.cursor()
    cur.execute(
        "SELECT DISTINCT substr(ts,1,10) FROM raw_candles ORDER BY substr(ts,1,10) DESC LIMIT ?",
        (days,),
    )
    day_list = [r[0] for r in cur.fetchall()]
    conn.close()
    return sorted(day_list)


def load_day_bars(day: str, db_path: str = RAW_DATA_DB) -> List[Tuple[str, float, float, float]]:
    conn = sqlite3.connect(db_path, timeout=10)
    cur = conn.cursor()
    cur.execute(
        "SELECT ts, high, low, close FROM raw_candles WHERE ts LIKE ? ORDER BY ts",
        (day + "%",),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def verdict(h: float) -> str:
    if h >= HURST_TREND_THRESHOLD:
        return "TREND"
    if h < HURST_RANGE_THRESHOLD:
        return "RANGE"
    return "NEUTRAL"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--days", type=int, default=60, help="검증에 쓸 최근 거래일 수 (기본 60)")
    parser.add_argument("--out", type=str, default=None, help="분봉 단위 상세 결과 CSV 저장 경로 (선택)")
    args = parser.parse_args()

    day_list = load_trading_days(args.days)
    print("=" * 70)
    print("[Hurst OOS Validation] 317차 Phase 2 — MicroRegimeClassifier 라벨 대조")
    print("=" * 70)
    print(f"\n대상 거래일: {len(day_list)}일 ({day_list[0]} ~ {day_list[-1]})\n")

    # candidate별 종가 버퍼 (일별로 reset — Phase 0에서 고친 reset_daily와 동일 원칙)
    per_candidate_records: Dict[str, List[Tuple[str, str]]] = defaultdict(list)  # name -> [(true_regime, hurst_verdict), ...]
    detail_rows = []

    n_bars_total = 0
    for day in day_list:
        bars = load_day_bars(day)
        if len(bars) < 30:
            continue

        micro_clf = MicroRegimeClassifier()
        close_bufs = {name: deque(maxlen=n) for n, ml, name in CANDIDATES}

        for ts, high, low, close in bars:
            if close is None or close <= 0:
                continue
            high = float(high or close)
            low = float(low or close)
            close = float(close)

            regime_res = micro_clf.push_1m_candle(high=high, low=low, close=close)
            true_regime = regime_res["regime"]

            row = {"ts": ts, "true_regime": true_regime}
            for n, max_lag, name in CANDIDATES:
                buf = close_bufs[name]
                buf.append(close)
                if len(buf) < max_lag * 2:
                    h = 0.5  # 콜드스타트 — 라이브와 동일하게 중립 취급, 아래서 카운트 제외
                    is_coldstart = True
                else:
                    h = calculate_hurst(list(buf), max_lag=max_lag)
                    is_coldstart = False
                row[name] = round(h, 4)
                if true_regime in (REGIME_TREND, REGIME_RANGE) and not is_coldstart:
                    per_candidate_records[name].append((true_regime, verdict(h)))

            detail_rows.append(row)
            n_bars_total += 1

    print(f"전체 분봉 수: {n_bars_total}\n")

    print(f"{'후보':<28s} {'추세오판(FalseBlock)':>18s} {'횡보오판(FalsePass)':>18s} "
          f"{'방향정확도':>10s} {'커버리지':>8s} {'표본(추세/횡보)':>16s}")
    print("-" * 105)

    summary_rows = []
    for n, max_lag, name in CANDIDATES:
        recs = per_candidate_records[name]
        trend_recs = [v for t, v in recs if t == REGIME_TREND]
        range_recs = [v for t, v in recs if t == REGIME_RANGE]
        n_trend, n_range = len(trend_recs), len(range_recs)

        # 핵심 지표: 진짜 추세인데 Hurst가 RANGE(<0.45)로 오판 → 게이트가 부당 차단
        false_block = (sum(1 for v in trend_recs if v == "RANGE") / n_trend) if n_trend else float("nan")
        # 진짜 횡보인데 Hurst가 TREND(>=0.55)로 오판 → 게이트가 부당 통과
        false_pass = (sum(1 for v in range_recs if v == "TREND") / n_range) if n_range else float("nan")

        # 방향 정확도: NEUTRAL 제외, TREND/RANGE 둘 중 하나를 찍은 표본 중 맞춘 비율
        directional = [(t, v) for t, v in recs if v != "NEUTRAL"]
        correct = sum(
            1 for t, v in directional
            if (t == REGIME_TREND and v == "TREND") or (t == REGIME_RANGE and v == "RANGE")
        )
        accuracy = correct / len(directional) if directional else float("nan")
        coverage = len(directional) / len(recs) if recs else float("nan")

        summary_rows.append({
            "candidate": name, "n": n, "max_lag": max_lag,
            "false_block_rate": false_block, "false_pass_rate": false_pass,
            "directional_accuracy": accuracy, "coverage": coverage,
            "n_trend": n_trend, "n_range": n_range,
        })
        print(f"{name:<28s} {false_block*100:>16.1f}% {false_pass*100:>17.1f}% "
              f"{accuracy*100:>9.1f}% {coverage*100:>7.1f}% {f'{n_trend}/{n_range}':>16s}")

    print("\n[해석 가이드]")
    print("  - '추세오판(FalseBlock)': ADX/ATR로 확정된 추세장 분봉 중 Hurst<0.45로 잘못 판정된 비율")
    print("    → 이 값이 낮을수록 실제 추세일 때 게이트가 신호를 덜 부당 차단한다는 뜻(가장 중요).")
    print("  - '횡보오판(FalsePass)': 확정된 횡보장 분봉 중 Hurst>=0.55로 잘못 판정된 비율")
    print("    → MDD 방어 관점에서는 낮을수록 좋지만, FalseBlock보다는 우선순위가 낮음.")
    print("  - '커버리지': 전체 표본 중 Hurst가 NEUTRAL(0.45~0.55)이 아니라 뚜렷한 판정을 내린 비율")
    print(f"  - 표본 한계: {len(day_list)}거래일치 — 여러 변동성 국면(폭락일 포함 여부)을 확인하고")
    print("    표본이 특정 레짐에 쏠려있지 않은지 별도로 확인할 것(4단계 안정성 체크와 연결).")

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()))
            writer.writeheader()
            writer.writerows(summary_rows)
        print(f"\n[저장] 후보별 요약 → {out_path}")

    print("\n읽기 전용 진단 스크립트 — config/settings.py는 자동 변경되지 않음.")


if __name__ == "__main__":
    main()
