# -*- coding: utf-8 -*-
"""검정 A 엔진 — 전방행렬 사전계산 + 매칭 대조군.

설계: 전 봉의 전방경로를 한 번만 만들어두고(FWD), 모든 진입후보/대조군은
행 선택으로만 처리한다. 대조군 1000회 재표집이 초 단위로 끝난다.
"""
from __future__ import annotations
import os, pickle
import numpy as np, pandas as pd

H_FWD = 180
GP_N = 20
HERE = os.path.dirname(os.path.abspath(__file__))

# 오염 세션 — 1분 |수익률|>2% 봉을 포함하거나 세션 진폭이 비정상
BAD_SESSIONS = {"2026-05-13"}          # 48봉이 ~1930 (정상대 ~1180). 진폭 764pt


def _gp(close, n=GP_N):
    s = pd.Series(close)
    lo = s.rolling(n, min_periods=n).min()
    hi = s.rolling(n, min_periods=n).max()
    return ((s - lo) / s * 200.0).values, ((hi - s) / s * 200.0).values


def build(min_bars=300, h=H_FWD, verbose=True):
    c = pd.read_pickle(os.path.join(HERE, "candles.pkl"))
    c["dt"] = pd.to_datetime(c["ts"])
    c["s"] = c["dt"].dt.strftime("%Y-%m-%d")
    c["hhmm"] = c["dt"].dt.strftime("%H:%M")
    c = c[(c["hhmm"] >= "09:00") & (c["hhmm"] <= "15:35")]
    c = c.sort_values("dt").drop_duplicates("dt")

    S, F = [], []
    dropped = []
    for s, g in c.groupby("s"):
        if s in BAD_SESSIONS:
            dropped.append((s, "오염")); continue
        if len(g) < min_bars:
            dropped.append((s, "봉부족 %d" % len(g))); continue
        g = g.set_index("dt")
        grid = pd.date_range(g.index[0], g.index[-1], freq="1min")
        r = g.reindex(grid)
        syn = r["close"].isna().values
        r[["open", "high", "low", "close"]] = r[["open", "high", "low", "close"]].ffill()
        cl = r["close"].astype(float).values
        hi_ = r["high"].astype(float).values
        lo_ = r["low"].astype(float).values
        n = len(cl)
        gb, gs = _gp(cl)
        pc = np.r_[np.nan, cl[:-1]]
        tr = np.nanmax(np.c_[hi_ - lo_, np.abs(hi_ - pc), np.abs(lo_ - pc)], axis=1)
        atr = pd.Series(tr).rolling(14, min_periods=14).mean().values
        ma20 = pd.Series(cl).rolling(20, min_periods=20).mean().values
        ma60 = pd.Series(cl).rolling(60, min_periods=60).mean().values
        # 전방행렬: 신호봉 i -> 진입 close[i+1], 경로 close[i+2 .. i+1+h]
        fwd = np.full((n, h), np.nan, np.float32)
        for t in range(h):
            j = np.arange(n) + 2 + t
            ok = j < n
            fwd[ok, t] = cl[j[ok]] - cl[np.arange(n)[ok] + 1]
        S.append(pd.DataFrame(dict(
            s=s, i=np.arange(n), hhmm=[t.strftime("%H:%M") for t in grid],
            close=cl, gb=gb, gs=gs, atr=atr, ma20=ma20, ma60=ma60, synth=syn)))
        F.append(fwd)
    D = pd.concat(S, ignore_index=True)
    FWD = np.vstack(F)
    if verbose:
        print("[build] 세션 %d  봉 %d  제외 %d일" % (D["s"].nunique(), len(D), len(dropped)))
        print("[build] 제외: %s" % ", ".join("%s(%s)" % x for x in dropped[:8]))
    return D, FWD


# ── 진입 마스크 ──────────────────────────────────────────────────────────
def cross_up(x, lvl):
    p = np.r_[np.nan, x[:-1]]
    return (p < lvl) & (x >= lvl)


def add_signals(D):
    """세션 경계를 지키며 교차/압축 플래그 생성."""
    out = {k: np.zeros(len(D), bool) for k in
           ["cu_gb", "cu_gs", "sq10"]}
    lv_cols = {}
    for lvl in (0.3, 0.5, 0.8, 1.0, 1.2, 1.5, 2.0):
        lv_cols["cu_gb_%.1f" % lvl] = np.zeros(len(D), bool)
        lv_cols["cu_gs_%.1f" % lvl] = np.zeros(len(D), bool)
    for s, g in D.groupby("s"):
        idx = g.index.values
        gb, gs = g["gb"].values, g["gs"].values
        out["cu_gb"][idx] = cross_up(gb, 0.5)
        out["cu_gs"][idx] = cross_up(gs, 0.5)
        for lvl in (0.3, 0.5, 0.8, 1.0, 1.2, 1.5, 2.0):
            lv_cols["cu_gb_%.1f" % lvl][idx] = cross_up(gb, lvl)
            lv_cols["cu_gs_%.1f" % lvl][idx] = cross_up(gs, lvl)
        z = np.nan_to_num((gb <= 0.5) & (gs <= 0.5) & (np.abs(gb - gs) <= 0.5), nan=False)
        run, o = 0, np.zeros(len(z), bool)
        for k in range(len(z)):
            if z[k]:
                run = 10
            o[k] = run > 0
            if run > 0:
                run -= 1
        out["sq10"][idx] = o
    for k, v in out.items():
        D[k] = v
    for k, v in lv_cols.items():
        D[k] = v
    return D


def select(D, mask, hold_block=90, once_per_day=False):
    """비중첩 진입 행 인덱스."""
    rows = []
    dd = D.loc[mask]
    for s, g in dd.groupby("s"):
        busy, cnt = -1, 0
        for ridx, i in zip(g.index.values, g["i"].values):
            if i <= busy:
                continue
            if once_per_day and cnt >= 1:
                break
            rows.append(ridx); busy = i + hold_block; cnt += 1
    return np.array(rows, int)


# ── 검정 A 지표 ──────────────────────────────────────────────────────────
def fwd_of(FWD, rows, side):
    return (FWD[rows] * side).astype(np.float64)


def edge_ratio(fw, atr0, t):
    a = fw[:, :t]
    mfe = np.nanmax(a, axis=1) / atr0
    mae = -np.nanmin(a, axis=1) / atr0
    ok = np.isfinite(mfe) & np.isfinite(mae)
    m1, m2 = np.nanmean(mfe[ok]), np.nanmean(mae[ok])
    return m1 / m2 if m2 > 0 else np.nan


def control_rows(D, rows, rng, n_rep, pool_mask):
    """날짜·횟수·시간대 분포 보존 무작위 대조군. 행 인덱스 배열 리스트 반환."""
    per_date = D.loc[rows].groupby("s").size()
    pool = D.loc[pool_mask]
    by_date = {s: g.index.values for s, g in pool.groupby("s")}
    # 시간대 분포 보존: 실제 진입의 hhmm 분포에서 뽑아 그 날 가장 가까운 봉을 쓴다
    tod = D.loc[rows, "i"].values
    reps = []
    for _ in range(n_rep):
        pick = []
        for s, cnt in per_date.items():
            cand = by_date.get(s)
            if cand is None or len(cand) == 0:
                continue
            ci = D.loc[cand, "i"].values
            want = rng.choice(tod, size=cnt, replace=False if cnt <= len(tod) else True)
            sel = cand[np.abs(ci[None, :] - want[:, None]).argmin(axis=1)]
            pick.append(np.unique(sel))
        reps.append(np.concatenate(pick) if pick else np.array([], int))
    return reps
