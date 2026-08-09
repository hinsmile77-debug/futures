# learning/validation_stats.py — 선택편향 방어 통계 (DSR·PBO)
"""
[MW0601 454차 / ATB-C1] Deflated Sharpe Ratio + PBO — 스펙
(docs/Spec for feature/ML Model Labeling/Validation · PY) 이식.

무엇을 막는가: "여러 번 시도해 제일 좋은 것을 골랐다"는 사실 자체가 만드는
점수 부풀림(선택 편향). Purged CV(시간 누출)·고유성 가중치(표본 중복)와 독립인
세 번째 누출 경로다.

  - expected_max_sharpe(n, var): 실력 0이어도 n번 시도하면 우연히 나오는 최대 샤프
  - deflated_sharpe_ratio: 관측 샤프가 그 문턱을 넘는다고 말할 수 있는 확률
      (왜도·첨도 벌점 포함). 통과 기준 DSR ≥ 0.95.
  - probability_of_backtest_overfitting: IS 1등이 OOS에서 중앙값 이하일 확률(CSCV).
      PBO < 0.2 견고 / > 0.5 → 선택 과정 자체가 과적합, 결과 전체 폐기.

배선(454차 기준 — 전부 advisory, 판정문 무변경):
  - backtest/walk_forward.py: WFA 결과에 dsr_advisory 병기 (Phase 5 조건 ③ 정식
    편입 여부는 실측 후 사용자 결정)
  - challenger/promotion_manager.py: evaluate_selection_bias() — 수동 승격 검토
    자료. 자동 승격 금지 원칙(CLAUDE.md)은 그대로다.

n_trials는 정직하게 셀 것 — 실패한 시도를 빼고 세면 DSR은 무의미해진다(스펙 §2.4).
py37_32 호환(scipy 1.5.4 norm만 사용).

참고: Bailey & Lopez de Prado, "The Deflated Sharpe Ratio" (2014)
      Bailey et al., "The Probability of Backtest Overfitting" (2015)
"""
import itertools
import math
from typing import Dict, List, Optional, Sequence

import numpy as np

__all__ = [
    "sharpe_ratio",
    "max_drawdown",
    "expected_max_sharpe",
    "deflated_sharpe_ratio",
    "probability_of_backtest_overfitting",
]

_EULER_GAMMA = 0.5772156649015329


def sharpe_ratio(returns, periods_per_year=252):
    # type: (Sequence[float], int) -> float
    """연율화 샤프. 표본 2개 미만 또는 분산 0이면 0.0."""
    r = np.asarray([x for x in returns if x is not None and np.isfinite(x)],
                   dtype=float)
    if len(r) < 2:
        return 0.0
    sd = r.std(ddof=1)
    if sd == 0:
        return 0.0
    return float(r.mean() / sd * math.sqrt(periods_per_year))


def max_drawdown(returns):
    # type: (Sequence[float]) -> float
    """수익률 시계열의 최대 낙폭 (음수, 비율)."""
    r = np.nan_to_num(np.asarray(returns, dtype=float))
    eq = np.cumprod(1.0 + r)
    peak = np.maximum.accumulate(eq)
    return float((eq / peak - 1.0).min()) if len(eq) else 0.0


def expected_max_sharpe(n_trials, var_sharpe):
    # type: (int, float) -> float
    """n번 시도했을 때 실력 0이어도 우연히 나오는 최대 (주기당) 샤프의 기댓값."""
    from scipy.stats import norm
    if n_trials < 2 or var_sharpe <= 0:
        return 0.0
    a = (1.0 - _EULER_GAMMA) * norm.ppf(1.0 - 1.0 / n_trials)
    b = _EULER_GAMMA * norm.ppf(1.0 - 1.0 / (n_trials * math.e))
    return float(math.sqrt(var_sharpe) * (a + b))


def deflated_sharpe_ratio(
    returns,               # type: Sequence[float]
    n_trials,              # type: int
    var_sharpe=None,       # type: Optional[float]
    periods_per_year=252,  # type: int
    sharpe_trials=None,    # type: Optional[Sequence[float]]
):
    # type: (...) -> Dict
    """Deflated Sharpe Ratio.

    returns       : 주기 수익률 시계열 (주간이면 periods_per_year=52)
    n_trials      : 실제 시도한 전략/파라미터 조합 수 — **정직하게 셀 것**
    sharpe_trials : 시도들의 연율화 샤프 배열 (주면 var_sharpe를 여기서 추정)

    Returns: {"sharpe", "sr_threshold", "dsr", "n_obs", "skew", "kurtosis", "pass"}
             (sharpe·sr_threshold는 연율화 값, pass 기준 DSR >= 0.95)
    """
    from scipy.stats import norm
    r = np.asarray([x for x in returns if x is not None and np.isfinite(x)],
                   dtype=float)
    T = len(r)
    if T < 3:
        return {"sharpe": 0.0, "sr_threshold": float("nan"), "dsr": 0.0,
                "n_obs": T, "skew": 0.0, "kurtosis": 3.0, "pass": False}

    sr_ann = sharpe_ratio(r, periods_per_year)
    sr = sr_ann / math.sqrt(periods_per_year)  # 주기당 샤프

    m = r.mean()
    sd = r.std(ddof=1)
    if sd == 0:
        return {"sharpe": 0.0, "sr_threshold": float("nan"), "dsr": 0.0,
                "n_obs": T, "skew": 0.0, "kurtosis": 3.0, "pass": False}
    z3 = ((r - m) ** 3).mean() / sd ** 3
    z4 = ((r - m) ** 4).mean() / sd ** 4  # 비초과 첨도 (정규=3)
    skew = float(z3)
    kurt = float(z4)

    if var_sharpe is None:
        if sharpe_trials is not None and len(sharpe_trials) > 1:
            per = np.asarray(sharpe_trials, dtype=float) / math.sqrt(periods_per_year)
            var_sharpe = float(np.var(per, ddof=1))
        else:
            var_sharpe = (1.0 + 0.5 * sr ** 2) / T

    sr0 = expected_max_sharpe(int(n_trials), var_sharpe)
    denom = math.sqrt(max(1e-12, 1.0 - skew * sr + (kurt - 1.0) / 4.0 * sr ** 2))
    z = (sr - sr0) * math.sqrt(T - 1) / denom
    dsr = float(norm.cdf(z))
    return {
        "sharpe": round(sr_ann, 4),
        "sr_threshold": round(float(sr0 * math.sqrt(periods_per_year)), 4),
        "dsr": round(dsr, 4),
        "n_obs": T,
        "skew": round(skew, 4),
        "kurtosis": round(kurt, 4),
        "pass": bool(dsr >= 0.95),
    }


def probability_of_backtest_overfitting(returns_matrix, n_splits=12):
    # type: (np.ndarray, int) -> Dict
    """PBO (CSCV) — "인샘플 1등이 아웃샘플에서 중앙값 이하일 확률".

    returns_matrix : (T, N) — 열=시도한 전략/파라미터, 행=시점 수익률.
                     NaN이 있는 행은 통째로 제외한다.

    Returns: {"pbo", "median_oos_percentile", "n_combinations", "pass"}
             표본/전략 부족 시 {"error": ...}
    """
    R = np.asarray(returns_matrix, dtype=float)
    if R.ndim != 2:
        return {"error": "returns_matrix는 2차원이어야 함"}
    R = R[~np.isnan(R).any(axis=1)]
    T, N = R.shape
    if N < 2:
        return {"error": "전략 2개 이상 필요 (N=%d)" % N}
    if n_splits % 2 == 1:
        n_splits += 1
    if T < n_splits * 2:
        return {"error": "시점 부족 (T=%d < %d)" % (T, n_splits * 2)}

    blocks = np.array_split(np.arange(T), n_splits)
    half = n_splits // 2

    def _sr(mat):
        mu = mat.mean(axis=0)
        sd = mat.std(axis=0, ddof=1)
        with np.errstate(divide="ignore", invalid="ignore"):
            out = np.where(sd > 0, mu / sd, np.nan)
        return out

    logits = []
    oos_pct = []
    for combo in itertools.combinations(range(n_splits), half):
        is_idx = np.concatenate([blocks[b] for b in combo])
        os_idx = np.concatenate([blocks[b] for b in range(n_splits)
                                 if b not in combo])
        is_sr = _sr(R[is_idx])
        os_sr = _sr(R[os_idx])
        if np.isnan(is_sr).all() or np.isnan(os_sr).all():
            continue
        best = int(np.nanargmax(is_sr))
        # OOS 순위 백분위 (1=최고). NaN은 최하위 취급.
        os_vals = np.where(np.isnan(os_sr), -np.inf, os_sr)
        rank = float((os_vals <= os_vals[best]).sum())  # 1..N
        w = rank / (N + 1.0)
        w = min(max(w, 1e-6), 1.0 - 1e-6)
        logits.append(math.log(w / (1.0 - w)))
        oos_pct.append(w)

    if not logits:
        return {"error": "유효 조합 없음"}
    logits_arr = np.asarray(logits)
    pbo = float((logits_arr <= 0).mean())
    return {
        "pbo": round(pbo, 4),
        "median_oos_percentile": round(float(np.median(oos_pct)), 4),
        "n_combinations": len(logits),
        "pass": bool(pbo < 0.2),
    }
