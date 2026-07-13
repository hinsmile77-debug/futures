# scripts/hurst_nmin_search.py
"""
[317차 Phase 1 재검토] N=90 채택 전, "진짜 n_min"을 촘촘한 스윕으로 확인.

배경: `scripts/hurst_grid_search.py`(1차 그리드)는 N∈{60,90,120,150} 4개 지점만 봤다.
사용자가 backfill 재실행 여부를 논의하기 전에 다음을 먼저 확립하자고 제안:

  max_lag는 두 조건을 동시에 만족해야 한다 —
    (a) 비율 상한: max_lag <= n/10 (편향 억제)
    (b) 절대 하한: max_lag >= LAG_FLOOR (8~10, 회귀점이 너무 적으면 추정 자체가 불안정)

  n이 작으면 (a)(b)가 서로 충돌한다 — n/10 < LAG_FLOOR인 구간에서는 하한이 강제로
  이기면서 실제 비율이 1/10보다 훨씬 나빠진다(예: n=60, floor=8 → max_lag=8, 실비율=0.133).
  n이 커져서 n/10 >= LAG_FLOOR를 만족하는 지점부터 비로소 두 조건이 동시에 성립한다.
  이 지점 부근에서 bias·std가 "안정 구간"에 들어오는지 촘촘한 시뮬레이션으로 직접 확인해
  n_min을 실증적으로 정한다 — N=90을 그대로 쓸지, 더 조정할지는 이 결과로 재논의한다.

읽기 전용 진단 — config/settings.py를 자동 변경하지 않는다.

실행 (py37_32 — py310_64는 np.corrcoef 크래시, 317차 Phase 1에서 확인):
    python scripts/hurst_nmin_search.py
    python scripts/hurst_nmin_search.py --sims 1000 --step 5
"""
import argparse
import csv
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from scripts.hurst_grid_search import (
    calibrate_from_raw_candles, FbmGenerator, est_current, run_cell,
)

LAG_FLOORS = [8, 10]  # 사용자 지정 절대 하한 범위(8~10) 양끝 비교
RATIO = 1 / 10.0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--days", type=int, default=10, help="캘리브레이션 거래일 수 (기본 10)")
    parser.add_argument("--sims", type=int, default=1000, help="n당 시뮬레이션 횟수 (기본 1000)")
    parser.add_argument("--step", type=int, default=5, help="n 스윕 간격 (기본 5)")
    parser.add_argument("--n-min", type=int, default=20, help="스윕 시작 n (기본 20)")
    parser.add_argument("--n-max", type=int, default=150, help="스윕 종료 n (기본 150)")
    parser.add_argument("--out", type=str, default=None,
                         help="n별 mean_H_0.3/0.5/0.7 CSV 저장 경로(선형보정 테이블 구축용, 선택)")
    args = parser.parse_args()

    print("=" * 78)
    print("[Hurst n_min Search] N=90 채택 전 재검토 — 촘촘한 n 스윕 + 이중조건 max_lag")
    print("=" * 78)

    calib = calibrate_from_raw_candles(args.days)
    print(f"\n[캘리브레이션] 최근 {calib['n_days']}거래일: ret_std={calib['ret_std']:.4f}pt\n")

    fbm_gen = FbmGenerator(sigma=calib["ret_std"])
    rng = np.random.default_rng(42)
    n_values = list(range(args.n_min, args.n_max + 1, args.step))

    csv_rows = []
    for floor in LAG_FLOORS:
        print(f"\n{'='*78}")
        print(f"[LAG_FLOOR = {floor}]  max_lag = max({floor}, round(n/10)), 상한 제약: max_lag <= n/10")
        print(f"{'='*78}")
        print(f"{'n':>5s} {'max_lag':>8s} {'실비율(lag/n)':>13s} {'ratio제약충족':>12s} "
              f"{'mean_H(0.3)':>11s} {'mean_H(0.5)':>11s} {'mean_H(0.7)':>11s} "
              f"{'bias(H=0.5)':>12s} {'std(H=0.5)':>11s} {'분리력':>8s}")
        print("-" * 78)

        rows = []
        for n in n_values:
            max_lag = max(floor, round(n * RATIO))
            if max_lag * 2 > n:
                continue  # 운영 코드 워밍업 제약(len>=max_lag*2) 위반 — 계산 자체 불가
            ratio_actual = max_lag / n
            ratio_ok = ratio_actual <= RATIO + 1e-9

            ests = {}
            for h_true in (0.3, 0.5, 0.7):
                ests[h_true] = run_cell(est_current, fbm_gen, n, max_lag, h_true, args.sims, rng)
            m03 = float(np.mean(ests[0.3]))
            m05 = float(np.mean(ests[0.5]))
            m07 = float(np.mean(ests[0.7]))
            bias = m05 - 0.5
            std = float(np.std(ests[0.5]))
            pooled = max((np.std(ests[0.3]) + np.std(ests[0.7])) / 2.0, 1e-6)
            sep = (m07 - m03) / pooled

            rows.append((n, max_lag, ratio_actual, ratio_ok, bias, std, sep))
            if floor == 8:  # 운영 워밍업 스케줄이 쓰는 floor만 CSV로 저장
                csv_rows.append({
                    "n": n, "max_lag": max_lag, "mean_H_0.3": round(m03, 4),
                    "mean_H_0.5": round(m05, 4), "mean_H_0.7": round(m07, 4),
                    "bias_0.5": round(bias, 4), "std_0.5": round(std, 4),
                })
            flag = "OK" if ratio_ok else "하한강제"
            print(f"{n:>5d} {max_lag:>8d} {ratio_actual:>13.3f} {flag:>12s} "
                  f"{m03:>11.3f} {m05:>11.3f} {m07:>11.3f} "
                  f"{bias:>+12.3f} {std:>11.3f} {sep:>8.2f}")

        # 안정 구간 탐지: ratio 제약이 처음 충족되는 n + |bias| < 0.05가 이후 계속 유지되는 첫 n
        first_ratio_ok = next((n for n, ml, ra, ok, b, s, sp in rows if ok), None)
        stable_n = None
        for i in range(len(rows)):
            n_i, _, _, _, bias_i, _, _ = rows[i]
            remainder_biases = [abs(r[4]) for r in rows[i:]]
            if abs(bias_i) < 0.05 and all(rb < 0.06 for rb in remainder_biases):
                stable_n = n_i
                break

        print(f"\n  → ratio(<=1/10) 제약이 처음 충족되는 n = {first_ratio_ok}"
              f"(= LAG_FLOOR({floor}) x 10 근방)")
        print(f"  → |bias|<0.05가 이후 계속 유지되는 첫 n(안정 구간 진입점) = {stable_n}")

    if args.out and csv_rows:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
            writer.writeheader()
            writer.writerows(csv_rows)
        print(f"\n[저장] LAG_FLOOR=8 계열 n별 mean_H(0.3/0.5/0.7) → {out_path}")

    print("\n읽기 전용 진단 스크립트 — config/settings.py는 자동 변경되지 않음.")
    print("이 결과로 N=90 유지/조정 여부를 재논의할 것.")


if __name__ == "__main__":
    main()
