"""GOLDEN POWER 활용안 검증 하니스.

두 모드로 나뉜다.

  explore  구조 확인용. 여러 후보를 훑어보되 채택 근거로 쓰지 않는다.
           다중검정 보정 후 살아남는 게 있는지만 본다.
  confirm  판정용. 사전등록서(preregistration.json)에 적힌 단 하나의 가설을
           홀드아웃에서 한 번만 평가한다. 재실행 금지.

미륵이 VALIDATION_CAMPAIGN 원칙(데이터 확인 전 min_samples/합격선 고정)에
맞추기 위한 분리다. explore 결과로 confirm 가설을 정하는 것은 허용되지만,
그 경우 홀드아웃은 explore에 쓰인 구간과 겹치면 안 된다.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from scipy import stats

from golden_power import GP_FEATURE_COLS, golden_power_features

# ---------------------------------------------------------------- 데이터 계약


@dataclass
class Panel:
    """검증에 필요한 최소 데이터.

    df 인덱스는 tz-naive DatetimeIndex(1분봉), 시간 오름차순, 중복 없음.
    필수 컬럼:
        close     종가
        session   거래일 (date). 세션 리셋과 purge 경계에 쓰인다.
    선택 컬럼 (있으면 결합 후보로 자동 편입):
        ofi_norm, cvd_div, vpin, opt_gex_bn, vkospi, ...
    """

    df: pd.DataFrame
    confirm_cols: list[str] = field(default_factory=list)

    def __post_init__(self):
        d = self.df
        missing = {"close", "session"} - set(d.columns)
        if missing:
            raise ValueError(f"필수 컬럼 누락: {sorted(missing)}")
        if not d.index.is_monotonic_increasing:
            raise ValueError("인덱스가 시간 오름차순이 아닙니다")
        if d.index.has_duplicates:
            raise ValueError("인덱스에 중복이 있습니다")


# ---------------------------------------------------------------- 전방 수익률


def forward_returns(
    close: pd.Series, session: pd.Series, horizons: list[int]
) -> pd.DataFrame:
    """h분 후 로그수익률. 세션 경계를 넘지 않는다(당일청산 원칙 반영)."""
    out = {}
    logc = np.log(close)
    for h in horizons:
        fwd = logc.shift(-h) - logc
        same = session.shift(-h) == session
        out[f"fwd_{h}m"] = fwd.where(same)
    return pd.DataFrame(out, index=close.index)


# ---------------------------------------------------------- purged 워크포워드


def purged_folds(
    session: pd.Series, n_folds: int = 5, embargo_days: int = 1
) -> list[tuple[np.ndarray, np.ndarray]]:
    """거래일 단위 시계열 분할. 테스트 앞뒤로 embargo_days를 학습에서 제거한다.

    1분봉을 무작위 분할하면 인접 봉이 학습/테스트에 나뉘어 누수가 생긴다.
    거래일 블록 + 엠바고가 최소 방어선이다.
    """
    days = np.array(sorted(session.unique()))
    if len(days) < n_folds * (1 + 2 * embargo_days):
        raise ValueError(
            f"거래일 {len(days)}일로는 {n_folds}겹 분할이 불가합니다"
        )
    blocks = np.array_split(days, n_folds)
    folds = []
    for te_days in blocks:
        lo, hi = te_days[0], te_days[-1]
        lo_i, hi_i = int(np.where(days == lo)[0][0]), int(np.where(days == hi)[0][0])
        banned = set(days[max(0, lo_i - embargo_days) : hi_i + embargo_days + 1])
        tr_days = np.array([d for d in days if d not in banned])
        folds.append(
            (
                np.where(session.isin(tr_days))[0],
                np.where(session.isin(te_days))[0],
            )
        )
    return folds


# ------------------------------------------------------------------- 지표 계산


def spearman_ic(x: pd.Series, y: pd.Series) -> tuple[float, int]:
    m = x.notna() & y.notna()
    n = int(m.sum())
    if n < 30:
        return np.nan, n
    return float(stats.spearmanr(x[m], y[m]).statistic), n


def fold_ic(
    feat: pd.Series, fwd: pd.Series, session: pd.Series, folds
) -> dict:
    """폴드별 IC와 그 안정성. 평균 IC가 커도 폴드 간 부호가 뒤집히면 무의미하다."""
    ics = []
    for _, te in folds:
        ic, n = spearman_ic(feat.iloc[te], fwd.iloc[te])
        if not np.isnan(ic):
            ics.append(ic)
    if len(ics) < 2:
        return {"ic_mean": np.nan, "ic_std": np.nan, "ic_t": np.nan, "sign_agree": np.nan}
    ics = np.array(ics)
    t = ics.mean() / (ics.std(ddof=1) / np.sqrt(len(ics))) if ics.std(ddof=1) > 0 else np.nan
    return {
        "ic_mean": float(ics.mean()),
        "ic_std": float(ics.std(ddof=1)),
        "ic_t": float(t) if t == t else np.nan,
        "sign_agree": float(np.mean(np.sign(ics) == np.sign(ics.mean()))),
        "n_folds": len(ics),
    }


def event_study(
    events: pd.Series,
    fwd: pd.Series,
    confirm: pd.Series | None = None,
    confirm_q: float = 0.7,
) -> dict:
    """돌파 이벤트의 사후 수익률. confirm을 주면 확증/비확증으로 쪼갠다.

    A안(돌파 x 오더플로 확증)의 핵심 검정. 돌파 단독으로는 의미가 없고
    확증 여부로 갈리는지를 본다. 갈리지 않으면 A안은 기각.
    """
    ev = events.fillna(0).astype(bool)
    base = fwd[~ev & fwd.notna()]
    res = {"n_events": int((ev & fwd.notna()).sum())}
    if res["n_events"] < 30:
        res["note"] = "표본 부족"
        return res

    hit = fwd[ev & fwd.notna()]
    res["evt_mean"] = float(hit.mean())
    res["base_mean"] = float(base.mean())
    res["evt_minus_base"] = res["evt_mean"] - res["base_mean"]
    res["evt_t"] = float(stats.ttest_ind(hit, base, equal_var=False).statistic)

    if confirm is not None:
        thr = confirm[ev].quantile(confirm_q)
        strong = ev & (confirm >= thr) & fwd.notna()
        weak = ev & (confirm < thr) & fwd.notna()
        if strong.sum() >= 20 and weak.sum() >= 20:
            a, b = fwd[strong], fwd[weak]
            res["n_confirmed"] = int(strong.sum())
            res["n_unconfirmed"] = int(weak.sum())
            res["confirmed_mean"] = float(a.mean())
            res["unconfirmed_mean"] = float(b.mean())
            res["spread"] = float(a.mean() - b.mean())
            res["spread_t"] = float(stats.ttest_ind(a, b, equal_var=False).statistic)
    return res


def bh_fdr(pvals: np.ndarray, alpha: float = 0.10) -> np.ndarray:
    """Benjamini-Hochberg. explore 모드에서 다중검정 보정용."""
    p = np.asarray(pvals, dtype=float)
    ok = ~np.isnan(p)
    out = np.zeros_like(p, dtype=bool)
    idx = np.where(ok)[0]
    if len(idx) == 0:
        return out
    order = idx[np.argsort(p[idx])]
    m = len(order)
    thresh = alpha * np.arange(1, m + 1) / m
    passed = p[order] <= thresh
    if passed.any():
        k = np.max(np.where(passed)[0])
        out[order[: k + 1]] = True
    return out


# ------------------------------------------------------------------- 실행 모드


def explore(
    panel: Panel,
    horizons: list[int] = (5, 15, 30),
    period: int = 25,
    n_folds: int = 5,
    alpha: float = 0.10,
) -> pd.DataFrame:
    """구조 확인. 채택 근거로 쓰지 말 것."""
    d = panel.df
    gp = golden_power_features(d["close"], period=period, session=d["session"])
    X = pd.concat([d, gp], axis=1)
    fwd = forward_returns(d["close"], d["session"], list(horizons))
    folds = purged_folds(d["session"], n_folds=n_folds)

    rows = []
    for h in horizons:
        y = fwd[f"fwd_{h}m"]
        for c in GP_FEATURE_COLS:
            if c in ("gp_break_lo", "gp_break_hi"):
                continue
            r = fold_ic(X[c], y, d["session"], folds)
            r.update(feature=c, horizon=h, kind="solo")
            rows.append(r)
        # 상호작용: gp_squeeze로 레짐을 쪼갠 뒤 확증피처의 IC가 달라지는가
        for c in panel.confirm_cols:
            if c not in X.columns:
                continue
            for regime, mask in (
                ("squeeze", X["gp_squeeze"] == 1),
                ("expand", X["gp_squeeze"] == 0),
            ):
                r = fold_ic(X[c].where(mask), y, d["session"], folds)
                r.update(feature=f"{c}|{regime}", horizon=h, kind="interaction")
                rows.append(r)

    res = pd.DataFrame(rows)
    # ic_t -> 양측 p. 폴드 수가 적으므로 t분포.
    dfree = res.get("n_folds", pd.Series(n_folds, index=res.index)).fillna(n_folds) - 1
    res["p"] = 2 * stats.t.sf(res["ic_t"].abs(), dfree)
    res["fdr_pass"] = bh_fdr(res["p"].to_numpy(), alpha=alpha)
    return res.sort_values("p").reset_index(drop=True)


def confirm_run(panel: Panel, prereg_path: str) -> dict:
    """사전등록된 단일 가설을 홀드아웃에서 한 번만 평가한다."""
    with open(prereg_path, encoding="utf-8") as f:
        pre = json.load(f)

    d = panel.df
    hold = d[d["session"].astype(str) >= pre["holdout_start"]]
    if hold["session"].nunique() < pre["min_sessions"]:
        return {
            "verdict": "PENDING",
            "reason": f"홀드아웃 {hold['session'].nunique()}일 < 사전등록 {pre['min_sessions']}일",
        }

    gp = golden_power_features(
        hold["close"], period=pre.get("period", 25), session=hold["session"]
    )
    X = pd.concat([hold, gp], axis=1)
    y = forward_returns(hold["close"], hold["session"], [pre["horizon"]])[
        f"fwd_{pre['horizon']}m"
    ]

    spec = pre["hypothesis"]
    if spec["type"] == "ic":
        ic, n = spearman_ic(X[spec["feature"]], y)
        stat, crit = abs(ic), pre["pass_threshold"]
    elif spec["type"] == "event_spread":
        r = event_study(
            X[spec["event"]], y, X[spec["confirm"]], spec.get("confirm_q", 0.7)
        )
        n = r.get("n_events", 0)
        stat, crit = r.get("spread", np.nan), pre["pass_threshold"]
    else:
        raise ValueError(f"알 수 없는 가설 유형: {spec['type']}")

    if n < pre["min_samples"]:
        return {"verdict": "PENDING", "reason": f"표본 {n} < {pre['min_samples']}"}
    return {
        "verdict": "PASS" if stat >= crit else "FAIL",
        "stat": stat,
        "threshold": crit,
        "n": n,
        "prereg": pre,
    }
