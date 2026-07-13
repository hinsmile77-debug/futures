# scripts/hurst_grid_search.py
"""
[317차 Phase 1] Hurst 지수 추정 파라미터·알고리즘 그리드서치 (합성데이터 기반).

배경: `features/technical/hurst_exponent.py::calculate_hurst()`를 실거래 파라미터
(n=60, max_lag=20)로 실측 raw_candles에 재현·몬테카를로 검증한 결과, 정답을 아는
순수 랜덤워크(이론 H=0.5)조차 평균 H≈0.33~0.36으로 읽히는 소표본 하향 편향을 확인
(`dev_memory/NEXT_TODO.md` 317차 항목). 이 스크립트는 "체중계가 정말 정확한지"를
표준 추(정답을 아는 합성 시계열)로 검증하는 2단계 작업이다.

검증 축:
  1) 창 길이 N × max_lag 비율 그리드
  2) 추정 알고리즘 3종 비교
     - current : calculate_hurst() 그대로 (variance-scaling, 운영 중인 실제 코드)
     - rs      : 고전 Rescaled Range (Mandelbrot-Wallis, 비중첩 서브윈도우 평균)
     - dfa1    : Detrended Fluctuation Analysis order-1 (추세에 강건하다고 알려짐)
  3) 테스트 케이스 H_true = 0.3(회귀형) / 0.5(랜덤워크) / 0.7(추세형) fGn/fBm 각 N_SIMS회
  4) (그리드 상위 후보만) 실측 캘리브레이션 드리프트를 얹어도 편향이 안 커지는지 확인
     — R/S는 추세에 상방 편향된다는 것이 알려진 약점이라 이 체크가 algo 선택에 중요.

읽기 전용 진단 — 어떤 설정값도 자동으로 바꾸지 않는다. 결과는 사람이 보고 Phase 1
채택 조합을 `config/settings.py`(HURST_WINDOW_N/HURST_MAX_LAG)에 수동 반영한다.

실행 (py310_64 권장 — 순수 numpy 연산이라 py37_32에서도 동작은 하지만, 그리드가
커서(수만~수십만 회 시뮬레이션) OOM/속도 이슈를 피하려면 py310_64 사용 원칙 유지):
    conda activate py310_64
    python scripts/hurst_grid_search.py                      # 기본 그리드, 1000 sims
    python scripts/hurst_grid_search.py --quick               # 스모크 테스트(작은 그리드/sims)
    python scripts/hurst_grid_search.py --sims 300 --days 10
    python scripts/hurst_grid_search.py --out data/daily_reports/hurst_grid_20260713.csv
"""
import argparse
import csv
import datetime
import sqlite3
import sys
import time
from pathlib import Path
from typing import Callable, Dict, List, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from config.settings import RAW_DATA_DB
from features.technical.hurst_exponent import calculate_hurst

RNG_SEED = 42


# ─────────────────────────────────────────────────────────────────
# 0. 실측 잡음 캘리브레이션 — raw_candles 최근 N거래일에서 1분 수익률 std / lag-1 자기상관 추출
# ─────────────────────────────────────────────────────────────────

def calibrate_from_raw_candles(days: int, db_path: str = RAW_DATA_DB) -> Dict[str, float]:
    conn = sqlite3.connect(db_path, timeout=10)
    cur = conn.cursor()
    cur.execute(
        "SELECT DISTINCT substr(ts, 1, 10) FROM raw_candles ORDER BY substr(ts, 1, 10) DESC LIMIT ?",
        (days,),
    )
    day_list = [r[0] for r in cur.fetchall()]

    stds, ac1s, drifts = [], [], []
    for day in day_list:
        cur.execute(
            "SELECT close FROM raw_candles WHERE ts LIKE ? ORDER BY ts", (day + "%",)
        )
        closes = np.array([r[0] for r in cur.fetchall()], dtype=float)
        if len(closes) < 60:
            continue
        rets = np.diff(closes)
        stds.append(float(np.std(rets)))
        if len(rets) > 2:
            ac1 = float(np.corrcoef(rets[:-1], rets[1:])[0, 1])
            if np.isfinite(ac1):
                ac1s.append(ac1)
        drifts.append(float((closes[-1] - closes[0]) / len(closes)))
    conn.close()

    if not stds:
        raise RuntimeError(f"raw_candles에서 최근 {days}일 데이터를 찾지 못함 — DB 경로/기간 확인")

    result = {
        "ret_std":       float(np.median(stds)),
        "lag1_autocorr": float(np.median(ac1s)) if ac1s else 0.0,
        "drift_per_bar": float(np.median(np.abs(drifts))),
        "n_days":        len(stds),
    }
    return result


# ─────────────────────────────────────────────────────────────────
# 1. 합성 시계열 생성 — fGn(fractional Gaussian noise) 공분산 Cholesky 방식
# ─────────────────────────────────────────────────────────────────

def _fgn_covariance(n: int, H: float, sigma: float) -> np.ndarray:
    """정상(stationary) fGn 자기공분산 행렬 (Toeplitz).
    gamma(k) = 0.5*sigma^2*(|k+1|^2H - 2|k|^2H + |k-1|^2H)
    """
    k = np.arange(n, dtype=float)
    gamma = 0.5 * sigma ** 2 * (
        np.abs(k + 1) ** (2 * H) - 2 * np.abs(k) ** (2 * H) + np.abs(k - 1) ** (2 * H)
    )
    # Toeplitz 행렬 구성
    idx = np.abs(np.subtract.outer(np.arange(n), np.arange(n)))
    return gamma[idx]


class FbmGenerator:
    """(n, H) 쌍마다 Cholesky 분해를 1회만 계산해 재사용 — 그리드서치 반복 호출 최적화."""

    def __init__(self, sigma: float):
        self.sigma = sigma
        self._chol_cache: Dict[Tuple[int, float], np.ndarray] = {}

    def _chol(self, n: int, H: float) -> np.ndarray:
        key = (n, round(H, 4))
        if key not in self._chol_cache:
            if abs(H - 0.5) < 1e-9:
                # H=0.5는 iid 가우시안 — Cholesky 불필요(공분산이 대각행렬)
                self._chol_cache[key] = None
            else:
                cov = _fgn_covariance(n, H, self.sigma)
                # 수치안정성 위해 작은 jitter 추가
                cov += np.eye(n) * 1e-8 * self.sigma ** 2
                self._chol_cache[key] = np.linalg.cholesky(cov)
        return self._chol_cache[key]

    def generate_price_path(
        self, n: int, H: float, rng: np.random.Generator, drift_per_bar: float = 0.0
    ) -> np.ndarray:
        L = self._chol(n, H)
        z = rng.standard_normal(n)
        fgn = z * self.sigma if L is None else L @ z
        fbm_increments = fgn
        prices = 1200.0 + np.cumsum(fbm_increments) + drift_per_bar * np.arange(n)
        return prices


# ─────────────────────────────────────────────────────────────────
# 2. 추정 알고리즘 3종
# ─────────────────────────────────────────────────────────────────

def est_current(prices: np.ndarray, max_lag: int) -> float:
    """운영 중인 calculate_hurst() 그대로 — variance-scaling 회귀."""
    return calculate_hurst(prices, max_lag=max_lag)


def est_rs(prices: np.ndarray, max_lag: int) -> float:
    """고전 Rescaled Range(R/S) — 비중첩 서브윈도우 평균 후 log-log 회귀.
    윈도우 크기 s in [max(2, max_lag//6), max_lag] 범위에서, 시계열을 s 단위로
    잘라 각 조각의 R/S를 구하고 평균낸 뒤 s에 대해 회귀한다(Mandelbrot-Wallis 방식).
    """
    n = len(prices)
    rets = np.diff(prices)
    sizes = sorted(set(np.linspace(max(4, max_lag // 3), max_lag, num=6, dtype=int)))
    log_s, log_rs = [], []
    for s in sizes:
        if s < 4 or s > len(rets):
            continue
        n_chunks = len(rets) // s
        if n_chunks < 1:
            continue
        rs_vals = []
        for i in range(n_chunks):
            chunk = rets[i * s:(i + 1) * s]
            mean_c = chunk.mean()
            dev = np.cumsum(chunk - mean_c)
            R = dev.max() - dev.min()
            S = chunk.std()
            if S > 1e-10:
                rs_vals.append(R / S)
        if rs_vals:
            log_s.append(np.log(s))
            log_rs.append(np.log(max(np.mean(rs_vals), 1e-10)))
    if len(log_s) < 2:
        return 0.5
    slope = np.polyfit(log_s, log_rs, 1)[0]
    return float(np.clip(slope, 0.0, 1.0))


def est_dfa1(prices: np.ndarray, max_lag: int) -> float:
    """DFA order-1 — 누적편차를 박스로 나눠 각 박스 선형추세 제거 후 RMS 스케일링.
    비정상성(추세)에 R/S보다 강건하다고 알려진 방법.
    """
    rets = np.diff(prices)
    y = np.cumsum(rets - rets.mean())
    n = len(y)
    sizes = sorted(set(np.linspace(max(4, max_lag // 3), max_lag, num=6, dtype=int)))
    log_s, log_f = [], []
    for s in sizes:
        if s < 4 or s > n:
            continue
        n_boxes = n // s
        if n_boxes < 1:
            continue
        rms_list = []
        for i in range(n_boxes):
            seg = y[i * s:(i + 1) * s]
            x = np.arange(s, dtype=float)
            coeffs = np.polyfit(x, seg, 1)
            trend = np.polyval(coeffs, x)
            resid = seg - trend
            rms_list.append(np.mean(resid ** 2))
        F_s = np.sqrt(np.mean(rms_list))
        if F_s > 1e-10:
            log_s.append(np.log(s))
            log_f.append(np.log(F_s))
    if len(log_s) < 2:
        return 0.5
    slope = np.polyfit(log_s, log_f, 1)[0]
    return float(np.clip(slope, 0.0, 1.0))


ALGORITHMS: Dict[str, Callable[[np.ndarray, int], float]] = {
    "current": est_current,
    "rs":      est_rs,
    "dfa1":    est_dfa1,
}


# ─────────────────────────────────────────────────────────────────
# 3. 그리드서치 본체
# ─────────────────────────────────────────────────────────────────

def run_cell(
    algo_fn: Callable[[np.ndarray, int], float],
    fbm_gen: FbmGenerator,
    n: int,
    max_lag: int,
    h_true: float,
    n_sims: int,
    rng: np.random.Generator,
    drift_per_bar: float = 0.0,
) -> np.ndarray:
    ests = np.empty(n_sims)
    for i in range(n_sims):
        prices = fbm_gen.generate_price_path(n, h_true, rng, drift_per_bar=drift_per_bar)
        ests[i] = algo_fn(prices, max_lag)
    return ests


def score_row(bias_050: float, std_050: float, sep_score: float) -> float:
    """정렬용 종합점수 — 편향·분산 최소화를 분리력보다 우선시(안전장치 성격이므로)."""
    return sep_score - 6.0 * abs(bias_050) - 3.0 * std_050


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--days", type=int, default=10, help="실측 캘리브레이션에 쓸 최근 거래일 수 (기본 10)")
    parser.add_argument("--sims", type=int, default=1000, help="셀당 시뮬레이션 반복 횟수 (기본 1000)")
    parser.add_argument("--quick", action="store_true", help="스모크 테스트용 축소 그리드/sims")
    parser.add_argument("--out", type=str, default=None, help="결과 CSV 저장 경로 (기본: 저장 안 함)")
    parser.add_argument("--top", type=int, default=8, help="콘솔에 출력할 상위 후보 수 (기본 8)")
    args = parser.parse_args()

    print("=" * 70)
    print("[Hurst Grid Search] 317차 Phase 1 — 합성데이터 (N, max_lag) × 알고리즘 검증")
    print("=" * 70)

    calib = calibrate_from_raw_candles(args.days)
    print(f"\n[캘리브레이션] 최근 {calib['n_days']}거래일 실측 (raw_candles):")
    print(f"  1분 수익률 std      = {calib['ret_std']:.4f} pt")
    print(f"  lag-1 자기상관       = {calib['lag1_autocorr']:.4f}")
    print(f"  |평균 분당 드리프트|  = {calib['drift_per_bar']:.4f} pt/min")

    if args.quick:
        n_candidates = [60, 90]
        lag_ratios = [1 / 8]
        algos = ["current", "rs", "dfa1"]
        n_sims = min(args.sims, 50)
    else:
        n_candidates = [60, 90, 120, 150]
        lag_ratios = [1 / 10, 1 / 8, 1 / 6]
        algos = ["current", "rs", "dfa1"]
        n_sims = args.sims

    h_cases = [0.3, 0.5, 0.7]
    fbm_gen = FbmGenerator(sigma=calib["ret_std"])
    rng = np.random.default_rng(RNG_SEED)

    rows = []
    total_cells = len(n_candidates) * len(lag_ratios) * len(algos)
    cell_i = 0
    t0 = time.time()

    for n in n_candidates:
        for ratio in lag_ratios:
            max_lag = max(4, int(n * ratio))
            if max_lag * 2 > n:
                continue  # 운영 코드와 동일한 워밍업 제약(len >= max_lag*2) 위반 조합 제외
            for algo_name in algos:
                algo_fn = ALGORITHMS[algo_name]
                cell_i += 1
                ests_by_h = {}
                for h_true in h_cases:
                    ests_by_h[h_true] = run_cell(algo_fn, fbm_gen, n, max_lag, h_true, n_sims, rng)

                mean_050 = float(np.mean(ests_by_h[0.5]))
                std_050  = float(np.std(ests_by_h[0.5]))
                bias_050 = mean_050 - 0.5
                mean_030 = float(np.mean(ests_by_h[0.3]))
                mean_070 = float(np.mean(ests_by_h[0.7]))
                std_030  = float(np.std(ests_by_h[0.3]))
                std_070  = float(np.std(ests_by_h[0.7]))
                pooled_std = max((std_030 + std_070) / 2.0, 1e-6)
                sep_score = (mean_070 - mean_030) / pooled_std

                rows.append({
                    "n": n, "max_lag": max_lag, "lag_ratio": round(ratio, 4), "algo": algo_name,
                    "mean_H_0.3": round(mean_030, 4), "mean_H_0.5": round(mean_050, 4),
                    "mean_H_0.7": round(mean_070, 4),
                    "bias_0.5": round(bias_050, 4), "std_0.5": round(std_050, 4),
                    "separation_score": round(sep_score, 4),
                    "score": round(score_row(bias_050, std_050, sep_score), 4),
                })
                elapsed = time.time() - t0
                print(f"  [{cell_i}/{total_cells}] n={n:3d} max_lag={max_lag:2d} algo={algo_name:8s} "
                      f"H0.5={mean_050:.3f}(±{std_050:.3f}) bias={bias_050:+.3f} "
                      f"sep={sep_score:.2f}  ({elapsed:.0f}s 경과)")

    rows.sort(key=lambda r: r["score"], reverse=True)

    print(f"\n[결과] 총 {len(rows)}개 그리드 셀, 상위 {args.top}개 (score = 분리력 - 6*|편향| - 3*표준편차):\n")
    header = ["n", "max_lag", "algo", "mean_H_0.3", "mean_H_0.5", "mean_H_0.7", "bias_0.5", "std_0.5", "separation_score", "score"]
    print("  " + " | ".join(f"{h:>12s}" for h in header))
    for r in rows[:args.top]:
        print("  " + " | ".join(f"{str(r[h]):>12s}" for h in header))

    current_row = next((r for r in rows if r["n"] == 60 and r["max_lag"] == 20 and r["algo"] == "current"), None)
    if current_row is None:
        # 정확히 60/20이 그리드에 없으면 가장 가까운 current 셀 참고용으로 별도 계산
        cur_ests = run_cell(est_current, fbm_gen, 60, 20, 0.5, n_sims, rng)
        print(f"\n[참고] 현재 운영값(n=60, max_lag=20, current)의 H=0.5 재확인: "
              f"mean={np.mean(cur_ests):.3f} std={np.std(cur_ests):.3f} "
              f"(dev_memory 317차 몬테카를로와 동일 방향인지 대조용)")
    else:
        print(f"\n[참고] 현재 운영값(n=60, max_lag=20, current) 그리드 내 순위: "
              f"{rows.index(current_row) + 1}/{len(rows)}, score={current_row['score']}")

    print(f"\n[다음 단계] 상위 후보 중 top-3에 대해 실측 드리프트(|{calib['drift_per_bar']:.3f}|pt/min)를 "
          f"얹어도 편향이 커지지 않는지 확인 필요 — 특히 R/S는 추세에 상방 편향된다고 알려져 있어 "
          f"driftless 그리드에서 1등이어도 이 체크에서 탈락할 수 있음.")
    top3 = rows[:3]
    drift = calib["drift_per_bar"]
    for r in top3:
        algo_fn = ALGORITHMS[r["algo"]]
        ests_drift = run_cell(algo_fn, fbm_gen, r["n"], r["max_lag"], 0.5, n_sims, rng, drift_per_bar=drift)
        bias_drift = float(np.mean(ests_drift)) - 0.5
        delta = bias_drift - r["bias_0.5"]
        flag = "  ⚠ 편향 확대" if abs(delta) > 0.03 else "  OK"
        print(f"  n={r['n']} max_lag={r['max_lag']} algo={r['algo']:8s} "
              f"driftless_bias={r['bias_0.5']:+.3f} → with_drift_bias={bias_drift:+.3f} (Δ={delta:+.3f}){flag}")

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        print(f"\n[저장] 전체 그리드 결과 → {out_path}")

    print(f"\n총 소요시간: {time.time() - t0:.0f}s")
    print("읽기 전용 진단 스크립트 — config/settings.py는 자동 변경되지 않음. "
          "채택 조합은 사람이 검토 후 HURST_WINDOW_N/HURST_MAX_LAG에 수동 반영할 것.")


if __name__ == "__main__":
    main()
