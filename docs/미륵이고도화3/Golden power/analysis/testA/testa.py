# -*- coding: utf-8 -*-
"""검정 A 측정기 — Δ(t) · Edge Ratio · 경로분포. 청산 무관."""
from __future__ import annotations
import os
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
TS = (15, 30, 60, 90, 180)


class Ctx:
    def __init__(self, D, FWD):
        self.D = D; self.FWD = FWD
        self.start = {}
        self.nbar = {}
        for s, g in D.groupby("s"):
            self.start[s] = int(g.index[0]); self.nbar[s] = len(g)
        self.i = D["i"].values
        self.atr = D["atr"].values
        self.hhmm = D["hhmm"].values
        self.sess = D["s"].values
        # 대조군 후보 풀: 시간창 안 + ATR 유효 + 전방 여유
        self.pool_ok = ((D["hhmm"].values >= "09:20") & (D["hhmm"].values <= "14:50")
                        & np.isfinite(self.atr) & ~D["synth"].values)
        self._pool_by_date = {}
        for s, g in D.loc[self.pool_ok].groupby("s"):
            self._pool_by_date[s] = g["i"].values

    def control_reps(self, rows, n_rep, rng):
        dates = pd.Series(self.sess[rows]).value_counts()
        tod = self.i[rows]
        reps = []
        per_date_pool = {}
        for s, k in dates.items():
            p = self._pool_by_date.get(s, np.array([], int))
            p = p[np.isin(p, tod)] if False else p
            p = p[p <= self.nbar[s] - 3]
            per_date_pool[s] = p
        # 시간대 분포 보존: 실제 tod 값 중 그 날 유효한 것만 후보로
        tod_u = np.unique(tod)
        for s in list(per_date_pool):
            p = per_date_pool[s]
            q = p[np.isin(p, tod_u)]
            per_date_pool[s] = q if len(q) >= dates[s] else p
        for _ in range(n_rep):
            acc = []
            for s, k in dates.items():
                p = per_date_pool[s]
                if len(p) == 0:
                    continue
                sel = rng.choice(p, size=min(k, len(p)), replace=False)
                acc.append(self.start[s] + sel)
            reps.append(np.concatenate(acc) if acc else np.array([], int))
        return reps


def path_stats(FWD, rows, side, atr0):
    fw = (FWD[rows].astype(np.float64)) * side
    mfe = np.fmax.accumulate(np.where(np.isnan(fw), -np.inf, fw), axis=1)
    mae = np.fmin.accumulate(np.where(np.isnan(fw), np.inf, fw), axis=1)
    mfe[~np.isfinite(mfe)] = np.nan
    mae[~np.isfinite(mae)] = np.nan
    return fw, mfe, mae


def er_from(mfe, mae, atr0, t):
    a = mfe[:, t - 1] / atr0
    b = -mae[:, t - 1] / atr0
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 10:
        return np.nan
    m2 = np.nanmean(b[ok])
    return np.nanmean(a[ok]) / m2 if m2 > 0 else np.nan


def measure(ctx, rows, side, n_rep=500, seed=7, ts=TS):
    """반환: dict(delta_t, z_t, er_t, er_z_t, N, days, 경로분포)"""
    rng = np.random.default_rng(seed)
    FWD = ctx.FWD
    atr0 = ctx.atr[rows]
    fw, mfe, mae = path_stats(FWD, rows, side, atr0)
    real_curve = np.nanmean(fw, axis=0)
    er_real = {t: er_from(mfe, mae, atr0, t) for t in ts}

    reps = ctx.control_reps(rows, n_rep, rng)
    cc = np.full((len(reps), FWD.shape[1]), np.nan)
    ce = {t: np.full(len(reps), np.nan) for t in ts}
    for k, r in enumerate(reps):
        if len(r) < 10:
            continue
        a0 = ctx.atr[r]
        f2, m1, m2 = path_stats(FWD, r, side, a0)
        cc[k] = np.nanmean(f2, axis=0)
        for t in ts:
            ce[t][k] = er_from(m1, m2, a0, t)
    cm, cs = np.nanmean(cc, axis=0), np.nanstd(cc, axis=0)
    delta = real_curve - cm
    z = np.where(cs > 0, delta / cs, np.nan)
    out = dict(N=len(rows), days=len(np.unique(ctx.sess[rows])),
               real=real_curve, ctrl=cm, delta=delta, z=z)
    for t in ts:
        out["d%d" % t] = delta[t - 1]
        out["z%d" % t] = z[t - 1]
        out["er%d" % t] = er_real[t]
        s_ = np.nanstd(ce[t]); m_ = np.nanmean(ce[t])
        out["erc%d" % t] = m_
        out["erz%d" % t] = (er_real[t] - m_) / s_ if s_ > 0 else np.nan
    out["zmax"] = np.nanmax(np.abs(z[:180]))
    out["zmax_t"] = int(np.nanargmax(np.abs(z[:180]))) + 1
    # 경로 분포
    last = min(90, FWD.shape[1])
    out["mfe90_med"] = np.nanmedian(mfe[:, last - 1])
    out["mae90_med"] = np.nanmedian(mae[:, last - 1])
    out["mfe90_p75"] = np.nanpercentile(mfe[:, last - 1], 75)
    out["mae90_p20"] = np.nanpercentile(mae[:, last - 1], 20)
    with np.errstate(invalid="ignore"):
        tstar = np.nanargmax(np.where(np.isnan(fw), -np.inf, fw), axis=1) + 1
    out["tstar_med"] = float(np.nanmedian(tstar))
    out["giveback_med"] = float(np.nanmedian(mfe[:, -1] - fw[:, -1]))
    out["fw90_mean"] = float(np.nanmean(fw[:, last - 1]))
    out["atr_med"] = float(np.nanmedian(atr0))
    return out
