# scripts/hurst_stability_check.py
"""
[317차 Phase 3] Hurst N/max_lag 후보의 안정성 체크 — 실전 데이터 기반.

Phase 2(`scripts/hurst_oos_validation.py`)에서 N=90(FalseBlock 최저)과 N=150
(FalsePass 최저) 사이 트레이드오프가 확인됐고, 사용자가 이 안정성 체크 결과까지
보고 최종 선택하기로 함(317차). 두 가지를 확인한다:

  1) N/max_lag를 ±10~20% 흔들어도 순위·지표가 크게 안 뒤집히는지(과적합 조합 배제)
  2) 고변동(폭락 등) vs 저변동 구간에서 N=90 vs N=150의 우열이 뒤집히는지

읽기 전용 진단 — config/settings.py를 자동 변경하지 않는다.

실행 (py37_32 — py310_64는 np.corrcoef 크래시, 317차 Phase 1에서 확인):
    python scripts/hurst_stability_check.py --days 60
"""
import argparse
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
from collection.macro.micro_regime import MicroRegimeClassifier, REGIME_TREND, REGIME_RANGE

# N=90 계열 ±10~20%, N=150 계열 ±10~20% — max_lag는 각 그리드 1위 비율(약 N/10) 유지
CANDIDATES: List[Tuple[int, int, str]] = [
    (60,  20, "N=60(현재 운영값)"),
    (72,   8, "N=90 -20%"),
    (81,   9, "N=90 -10%"),
    (90,   9, "N=90 (Phase2 채택 후보)"),
    (99,  10, "N=90 +10%"),
    (108, 11, "N=90 +20%"),
    (120, 12, "N=150 -20%"),
    (135, 14, "N=150 -10%"),
    (150, 15, "N=150 (Phase2 채택 후보)"),
    (165, 17, "N=150 +10%"),
    (180, 18, "N=150 +20%"),
]


def load_trading_days(days: int) -> List[str]:
    conn = sqlite3.connect(RAW_DATA_DB, timeout=10)
    cur = conn.cursor()
    cur.execute(
        "SELECT DISTINCT substr(ts,1,10) FROM raw_candles ORDER BY substr(ts,1,10) DESC LIMIT ?",
        (days,),
    )
    result = sorted(r[0] for r in cur.fetchall())
    conn.close()
    return result


def load_day_bars(day: str) -> List[Tuple[str, float, float, float]]:
    conn = sqlite3.connect(RAW_DATA_DB, timeout=10)
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


def day_volatility(bars: List[Tuple[str, float, float, float]]) -> float:
    closes = np.array([b[3] for b in bars if b[3]], dtype=float)
    if len(closes) < 10:
        return 0.0
    return float(np.std(np.diff(closes)))


def compute_metrics(records: List[Tuple[str, str]]) -> Dict[str, float]:
    trend_recs = [v for t, v in records if t == REGIME_TREND]
    range_recs = [v for t, v in records if t == REGIME_RANGE]
    n_trend, n_range = len(trend_recs), len(range_recs)
    false_block = (sum(1 for v in trend_recs if v == "RANGE") / n_trend) if n_trend else float("nan")
    false_pass = (sum(1 for v in range_recs if v == "TREND") / n_range) if n_range else float("nan")
    return {"false_block": false_block, "false_pass": false_pass, "n_trend": n_trend, "n_range": n_range}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--days", type=int, default=60, help="검증 거래일 수 (기본 60)")
    args = parser.parse_args()

    day_list = load_trading_days(args.days)
    print("=" * 78)
    print("[Hurst Stability Check] 317차 Phase 3 — 파라미터 흔들기 + 고/저변동 구간 분리")
    print("=" * 78)
    print(f"\n대상 거래일: {len(day_list)}일 ({day_list[0]} ~ {day_list[-1]})\n")

    # 일별 변동성(1분 수익률 std) 계산 → 중앙값 기준 고/저변동 분리
    day_bars_cache = {}
    day_vol = {}
    for day in day_list:
        bars = load_day_bars(day)
        if len(bars) < 30:
            continue
        day_bars_cache[day] = bars
        day_vol[day] = day_volatility(bars)

    vol_values = list(day_vol.values())
    vol_median = float(np.median(vol_values))
    high_vol_days = {d for d, v in day_vol.items() if v >= vol_median}
    low_vol_days = {d for d, v in day_vol.items() if v < vol_median}
    print(f"변동성 중앙값(1분 수익률 std) = {vol_median:.3f}pt — "
          f"고변동 {len(high_vol_days)}일 / 저변동 {len(low_vol_days)}일\n")

    # candidate별 (전체 / 고변동 / 저변동) 레코드 수집
    records_all: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
    records_high: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
    records_low: Dict[str, List[Tuple[str, str]]] = defaultdict(list)

    for day, bars in day_bars_cache.items():
        micro_clf = MicroRegimeClassifier()
        close_bufs = {name: deque(maxlen=n) for n, ml, name in CANDIDATES}
        bucket = records_high if day in high_vol_days else records_low

        for ts, high, low, close in bars:
            if not close or close <= 0:
                continue
            high = float(high or close); low = float(low or close); close = float(close)
            regime_res = micro_clf.push_1m_candle(high=high, low=low, close=close)
            true_regime = regime_res["regime"]
            if true_regime not in (REGIME_TREND, REGIME_RANGE):
                for n, max_lag, name in CANDIDATES:
                    close_bufs[name].append(close)
                continue
            for n, max_lag, name in CANDIDATES:
                buf = close_bufs[name]
                buf.append(close)
                if len(buf) < max_lag * 2:
                    continue
                h = calculate_hurst(list(buf), max_lag=max_lag)
                v = verdict(h)
                records_all[name].append((true_regime, v))
                bucket[name].append((true_regime, v))

    # ── 1) 파라미터 흔들기 안정성 ────────────────────────────────────────
    print("[1] 파라미터 ±10~20% 안정성 (전체 기간 기준)\n")
    print(f"{'후보':<28s} {'FalseBlock':>11s} {'FalsePass':>11s} {'표본(추세/횡보)':>16s}")
    print("-" * 70)
    group_results = {}
    for n, max_lag, name in CANDIDATES:
        m = compute_metrics(records_all[name])
        group_results[name] = m
        sample_str = "{}/{}".format(m['n_trend'], m['n_range'])
        print(f"{name:<28s} {m['false_block']*100:>10.1f}% {m['false_pass']*100:>10.1f}% "
              f"{sample_str:>16s}")

    def spread(names):
        vals = [group_results[n]["false_block"] for n in names if not np.isnan(group_results[n]["false_block"])]
        return (max(vals) - min(vals)) if vals else float("nan")

    n90_group = ["N=90 -20%", "N=90 -10%", "N=90 (Phase2 채택 후보)", "N=90 +10%", "N=90 +20%"]
    n150_group = ["N=150 -20%", "N=150 -10%", "N=150 (Phase2 채택 후보)", "N=150 +10%", "N=150 +20%"]
    print(f"\nN=90 계열 FalseBlock 변동폭(최대-최소): {spread(n90_group)*100:.1f}%p")
    print(f"N=150 계열 FalseBlock 변동폭(최대-최소): {spread(n150_group)*100:.1f}%p")
    print("→ 변동폭이 작을수록(대략 5%p 이내) 특정 숫자에만 우연히 맞는 과적합이 아니라는 뜻.")

    # ── 2) 고변동 vs 저변동 구간 분리 ────────────────────────────────────
    print("\n[2] 고변동 vs 저변동 구간 분리 — N=90 vs N=150 우열이 뒤집히는지 확인\n")
    key_names = ["N=60(현재 운영값)", "N=90 (Phase2 채택 후보)", "N=150 (Phase2 채택 후보)"]
    print(f"{'후보':<28s} {'고변동 FalseBlock':>17s} {'저변동 FalseBlock':>17s} "
          f"{'고변동 FalsePass':>16s} {'저변동 FalsePass':>16s}")
    print("-" * 90)
    for name in key_names:
        mh = compute_metrics(records_high[name])
        ml = compute_metrics(records_low[name])
        print(f"{name:<28s} {mh['false_block']*100:>16.1f}% {ml['false_block']*100:>16.1f}% "
              f"{mh['false_pass']*100:>15.1f}% {ml['false_pass']*100:>15.1f}%")

    fb_high_90  = compute_metrics(records_high["N=90 (Phase2 채택 후보)"])["false_block"]
    fb_high_150 = compute_metrics(records_high["N=150 (Phase2 채택 후보)"])["false_block"]
    fb_low_90   = compute_metrics(records_low["N=90 (Phase2 채택 후보)"])["false_block"]
    fb_low_150  = compute_metrics(records_low["N=150 (Phase2 채택 후보)"])["false_block"]
    fp_high_90  = compute_metrics(records_high["N=90 (Phase2 채택 후보)"])["false_pass"]
    fp_high_150 = compute_metrics(records_high["N=150 (Phase2 채택 후보)"])["false_pass"]
    fp_low_90   = compute_metrics(records_low["N=90 (Phase2 채택 후보)"])["false_pass"]
    fp_low_150  = compute_metrics(records_low["N=150 (Phase2 채택 후보)"])["false_pass"]

    print(f"\nFalseBlock: N=90이 더 낮음(추세 포착 유리) — 고변동={fb_high_90 < fb_high_150}, 저변동={fb_low_90 < fb_low_150}")
    print(f"FalsePass : N=150이 더 낮음(MDD 방어 유리) — 고변동={fp_high_150 < fp_high_90}, 저변동={fp_low_150 < fp_low_90}")
    print("→ 둘 다 True/True로 나오면 Phase 2 결론이 변동성 국면과 무관하게 안정적이라는 뜻.")

    print("\n읽기 전용 진단 스크립트 — config/settings.py는 자동 변경되지 않음.")


if __name__ == "__main__":
    main()
