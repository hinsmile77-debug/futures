# -*- coding: utf-8 -*-
"""GOLDEN POWER 검증 공용 라이브러리.

SOP(`docs/Spec for feature/피처_재검증_및_호라이즌배정_원칙.md`) 준수 사항
  §2  유형 분류를 IC 계산보다 **먼저** 한다
  §3  중복은 상관 이전에 **소스**에서 찾는다(B-5-1)
  §4  관측단위는 **거래일**이다(C-2) — 분봉 풀링 t는 쓰지 않는다
  §6  해상도·절단·표본손실을 값으로 위장하지 않는다
  §7  NaN 가드 · 다중비교 검정 수 명시
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
SNAP = os.path.join(HERE, "_snapshot")
sys.path.insert(0, os.path.dirname(HERE))          # golden_power.py 임포트용

from golden_power import golden_power, golden_power_features  # noqa: E402

# ── 계약·비용 상수 (config/constants.py · config/settings.py 실측값) ──────────
PT_VALUE = 50_000          # 미니선물 1pt
TICK = 0.02                # 미니선물 호가단위
RATE_LIVE = 0.000098104    # CYBOS 편도 요율 (BROKER_CHANNEL_SPECS["CYBOS"])
RATE_PINNED = 0.000015     # COST_MODEL_COMMISSION_RATE — 캠페인 채널 핀값(구 키움)

GP_FEATS = ["gp_dir", "gp_range", "gp_pos", "gp_break_lo", "gp_break_hi",
            "gp_range_drop", "gp_squeeze"]


def roundtrip_cost_pt(price, rate=RATE_LIVE, slip_ticks=0.0):
    """왕복 비용(포인트). 수수료 = 약정금액 × 요율 × 2(왕복)."""
    return 2.0 * np.asarray(price, dtype=float) * rate + 2.0 * slip_ticks * TICK


# ── 데이터 로딩 ──────────────────────────────────────────────────────────────
def load_panel(period: int = 25, snap_dir: str = SNAP) -> pd.DataFrame:
    """스냅샷 → 분석 패널. 세션 리셋 GP 피처 포함."""
    c = pd.read_pickle(os.path.join(snap_dir, "candles.pkl"))
    f = pd.read_pickle(os.path.join(snap_dir, "feats.pkl"))
    d = c.merge(f, on="ts", how="left")
    d["dt"] = pd.to_datetime(d["ts"])
    d = d.sort_values("dt").drop_duplicates("dt").reset_index(drop=True)
    d["session"] = d["dt"].dt.date.astype(str)
    d["hhmm"] = d["dt"].dt.strftime("%H:%M")
    d = d.set_index("dt")

    gp = golden_power_features(d["close"], period=period, session=d["session"])
    raw = _gp_raw_by_session(d["close"], d["session"], period)
    return pd.concat([d, gp, raw], axis=1)


def _gp_raw_by_session(close: pd.Series, session: pd.Series, period: int) -> pd.DataFrame:
    parts = []
    for _, idx in close.groupby(session).groups.items():
        parts.append(golden_power(close.loc[idx], period))
    return pd.concat(parts).sort_index()


def forward_returns(close: pd.Series, session: pd.Series, horizons) -> pd.DataFrame:
    """h분 후 로그수익률. 세션 경계를 넘지 않는다(절대원칙 §1 당일청산)."""
    out = {}
    logc = np.log(close.astype(float))
    for h in horizons:
        same = session.shift(-h) == session
        out["fwd_%dm" % h] = (logc.shift(-h) - logc).where(same)
    return pd.DataFrame(out, index=close.index)


# ── §4 C-2: 일자단위 IC ──────────────────────────────────────────────────────
def daily_ic(x: pd.Series, y: pd.Series, session: pd.Series, min_n: int = 60) -> pd.Series:
    """거래일마다 Spearman IC 하나. 관측단위 = 거래일."""
    df = pd.DataFrame({"x": x, "y": y, "s": session}).dropna()
    out = {}
    for s, g in df.groupby("s"):
        if len(g) < min_n or g["x"].nunique() < 2 or g["y"].nunique() < 3:
            continue
        out[s] = stats.spearmanr(g["x"], g["y"]).statistic
    return pd.Series(out, dtype=float).dropna()


def ic_verdict(ics: pd.Series, min_days: int = 20) -> dict:
    """일자단위 IC 계열의 유의성. n = 거래일 수."""
    ics = ics.dropna()
    n = len(ics)
    r = {"n_days": n, "ic_mean": np.nan, "ic_sd": np.nan, "t": np.nan,
         "p": np.nan, "pos_ratio": np.nan, "h1_ic": np.nan, "h2_ic": np.nan}
    if n < min_days:
        r["note"] = "표본 미달(%d < %d)" % (n, min_days)
        return r
    r["ic_mean"] = float(ics.mean())
    r["ic_sd"] = float(ics.std(ddof=1))
    if r["ic_sd"] > 0:
        r["t"] = r["ic_mean"] / (r["ic_sd"] / np.sqrt(n))
        r["p"] = float(2 * stats.t.sf(abs(r["t"]), n - 1))
    r["pos_ratio"] = float((ics > 0).mean())
    # §7 F-4 전·후반 안정성 — 날짜순 앞/뒤 절반
    ics_sorted = ics.sort_index()
    half = n // 2
    r["h1_ic"] = float(ics_sorted.iloc[:half].mean())
    r["h2_ic"] = float(ics_sorted.iloc[half:].mean())
    r["stable"] = bool(np.sign(r["h1_ic"]) == np.sign(r["h2_ic"]))
    return r


def partial_daily_ic(x, y, ctrl, session, min_n: int = 60) -> pd.Series:
    """통제변수의 순위효과를 제거한 뒤의 일자단위 IC (Spearman partial).

    "GP가 기존 피처 **위에** 무엇을 더하는가"를 재는 값이다.
    ctrl 은 Series 하나 또는 Series 리스트(다중 통제 — 예: 최근접피처 + 시각).
    """
    ctrls = list(ctrl) if isinstance(ctrl, (list, tuple)) else [ctrl]
    cols = {"x": x, "y": y, "s": session}
    for i, c in enumerate(ctrls):
        cols["c%d" % i] = c
    df = pd.DataFrame(cols).dropna()
    cnames = ["c%d" % i for i in range(len(ctrls))]
    out = {}
    for s, g in df.groupby("s"):
        if len(g) < min_n or g["x"].nunique() < 2:
            continue
        if any(g[c].nunique() < 2 for c in cnames):
            continue
        rx = g["x"].rank().to_numpy(float)
        ry = g["y"].rank().to_numpy(float)
        rc = np.column_stack([np.ones(len(g))] +
                             [g[c].rank().to_numpy(float) for c in cnames])
        ex = rx - rc @ np.linalg.lstsq(rc, rx, rcond=None)[0]
        ey = ry - rc @ np.linalg.lstsq(rc, ry, rcond=None)[0]
        if ex.std() < 1e-12 or ey.std() < 1e-12:
            continue
        out[s] = float(np.corrcoef(ex, ey)[0, 1])
    return pd.Series(out, dtype=float).dropna()


# ── §2 유형 분류 ─────────────────────────────────────────────────────────────
def taxonomy(v: pd.Series, session: pd.Series, hhmm: pd.Series) -> dict:
    """D/B/C/S/I/N 6종 분류. 임계는 SOP §2 표와 동일(사전 고정)."""
    s = v.astype(float)
    m = s.notna()
    r = {"n": int(m.sum()), "n_nan": int((~m).sum())}
    if r["n"] < 100:
        r["shape"] = "표본부족"
        return r
    x = s[m]
    # D — 결정론형(시계): 같은 hh:mm의 날짜간 sd / 전체 sd
    g = pd.DataFrame({"v": x, "t": hhmm[m]}).groupby("t")["v"]
    r["det_ratio"] = float(g.std().mean() / x.std()) if x.std() > 0 else np.nan
    # B — 이진/범주
    r["n_unique"] = int(x.nunique())
    # C — 상수/준상수
    r["tie_rate"] = float(x.value_counts(normalize=True).iloc[0])
    r["daily_uniq"] = float(pd.DataFrame({"v": x, "s": session[m]})
                            .groupby("s")["v"].nunique().mean())
    # S — 계단/저빈도갱신: 값 변화 간격 중앙값
    chg = pd.DataFrame({"v": x, "s": session[m]}).groupby("s")["v"].apply(
        lambda z: z.diff().abs().gt(1e-12).to_numpy())
    gaps = []
    for arr in chg:
        pos = np.flatnonzero(arr)
        if len(pos) >= 2:
            gaps.extend(np.diff(pos).tolist())
    r["upd_gap_med"] = float(np.median(gaps)) if gaps else np.inf
    # I — 누적/비정상: 일중 추세 R² · ACF(1)
    r2s, acfs = [], []
    for _, gg in pd.DataFrame({"v": x, "s": session[m]}).groupby("s"):
        z = gg["v"].to_numpy(float)
        if len(z) < 30 or z.std() < 1e-12:
            continue
        t = np.arange(len(z), dtype=float)
        r2s.append(np.corrcoef(t, z)[0, 1] ** 2)
        acfs.append(np.corrcoef(z[:-1], z[1:])[0, 1])
    r["intraday_r2"] = float(np.nanmean(r2s)) if r2s else np.nan
    r["acf1"] = float(np.nanmean(acfs)) if acfs else np.nan

    shape = "N"
    if r["n_unique"] <= 5:
        shape = "B"                       # 이진/범주 — C보다 먼저 판정한다
    elif r["tie_rate"] >= 0.95 or r["daily_uniq"] <= 3:
        shape = "C"
    elif (r["det_ratio"] == r["det_ratio"]) and r["det_ratio"] < 0.05:
        shape = "D"
    elif r["upd_gap_med"] >= 5:
        shape = "S"
    elif (r["intraday_r2"] >= 0.50) or (r["acf1"] >= 0.99):
        shape = "I"
    r["shape"] = shape
    return r


def hour_profile(v: pd.Series, dt_index) -> pd.Series:
    """시각별 평균 — cvd_divergence 교훈(§2 A-6 주의문). 단조 감소면 시계 오염 의심."""
    return pd.Series(v.astype(float).to_numpy(),
                     index=pd.DatetimeIndex(dt_index).hour).groupby(level=0).mean()


def bonferroni(p, n_tests, alpha=0.05):
    return bool(p == p and p < alpha / max(n_tests, 1))


# ── 529차 스윙 피처 재계산 (replay) ─────────────────────────────────────────
# 라이브 배선이 2026-09-03이라 raw_features 에는 99.2%가 결측이다. 비교하려면
# `features/feature_builder.py:compute_swing_features` 와 **같은 산식**으로 봉에서
# 다시 재는 수밖에 없다 — `scripts/leg_position_watch.py:_replay_swing` 과 같은 방식이며
# 사본이 아니라 원본 봉에서 재계산하는 것이라 오차가 없다.
def replay_swing(d: pd.DataFrame, n: int = 60, atr_win: int = 14,
                 clip_atr: float = 20.0) -> pd.DataFrame:
    parts = []
    for _, g in d.groupby("session"):
        h = g["high"].to_numpy(float)
        l = g["low"].to_numpy(float)
        c = g["close"].to_numpy(float)
        cp = np.r_[c[0], c[:-1]]
        tr = np.maximum(h - l, np.maximum(np.abs(h - cp), np.abs(l - cp)))
        atr = pd.Series(tr, index=g.index).rolling(atr_win, min_periods=atr_win).mean()
        hi = pd.Series(h, index=g.index).rolling(n, min_periods=1).max()
        lo = pd.Series(l, index=g.index).rolling(n, min_periods=1).min()
        a = atr.to_numpy(float)
        ok = a > 1e-6
        dh = np.where(ok, np.clip((hi.to_numpy() - c) / np.where(ok, a, 1.0), 0, clip_atr), np.nan)
        dl = np.where(ok, np.clip((c - lo.to_numpy()) / np.where(ok, a, 1.0), 0, clip_atr), np.nan)
        parts.append(pd.DataFrame({
            "rp_swing_high_%dm" % n: hi, "rp_swing_low_%dm" % n: lo,
            "rp_dist_to_high_%dm_atr" % n: dh, "rp_dist_to_low_%dm_atr" % n: dl,
            "rp_atr%d" % atr_win: atr,
            "rp_swing_ready_%dm" % n: np.arange(len(g)) >= n - 1,
        }, index=g.index))
    return pd.concat(parts).sort_index()


# ── 계측 4원칙 ② — 미측정을 0으로 두지 않는다 ────────────────────────────────
# 추출은 원천이 안 주는 키를 그대로 담았고, 백필 구간의 미시구조 피처는 값이 0이다.
# 그 0을 값으로 쓰면 상관이 희석되고(분모에 무정보 구간이 섞인다) 판정이 뒤틀린다.
# **세션 내내 상수 0인 날**을 그 피처의 미측정으로 보고 NaN 으로 되돌린다.
LIVE_ONLY_FEATURES = [
    "ofi_norm", "ofi_pressure", "mlofi_norm", "vpin", "toxicity_score",
    "spread_ticks", "microprice_bias", "queue_signal", "micro_regime_code",
    "cvd_divergence", "realized_vol_ann", "kyle_lambda", "opt_gex_bn", "vkospi",
    "price_extension_atr", "price_extension_atr_60m", "trend_efficiency",
    "dist_to_high_60m_atr", "dist_to_low_60m_atr", "bars_since_high_60m",
    "bars_since_low_60m", "swing_high_60m", "swing_low_60m",
]
# 백필로도 재계산돼 전 구간 존재하는 피처 (257일 비교에 쓸 수 있는 것)
ALWAYS_AVAILABLE = [
    "atr", "atr_ratio", "bb_position", "vwap_position", "poc_distance",
    "poc_above", "in_value_area", "va_bandwidth", "ema_cross", "hurst",
    "ret_1m", "ret_5m", "ret_15m", "cvd_delta_norm", "cvd_slope",
    "avg_volume", "time_sin", "time_cos",
]


def mask_unmeasured(d: pd.DataFrame, cols=None) -> pd.DataFrame:
    """세션 전체가 상수 0인 피처-날짜를 NaN 으로 되돌린다. 반환: 마스킹 요약."""
    cols = [c for c in (cols or LIVE_ONLY_FEATURES) if c in d.columns]
    rows = []
    for c in cols:
        v = pd.to_numeric(d[c], errors="coerce")
        allzero = (pd.DataFrame({"v": v, "s": d["session"]})
                   .groupby("s")["v"].apply(lambda z: bool(z.fillna(0).eq(0).all())))
        bad = d["session"].map(allzero).fillna(False).to_numpy()
        rows.append({"feature": c, "masked_days": int(allzero.sum()),
                     "total_days": int(len(allzero)),
                     "masked_rows": int(bad.sum())})
        d.loc[bad, c] = np.nan
    return pd.DataFrame(rows)
