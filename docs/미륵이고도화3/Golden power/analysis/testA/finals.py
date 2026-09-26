# -*- coding: utf-8 -*-
"""정밀 측정 — 순열(대조군) 기반 p값 + max통계 널 + 분할검증."""
import os
import numpy as np, pandas as pd
import testa

TS = (10, 15, 30, 60, 90, 180)

def deep(ctx, rows, side, n_rep=2000, seed=101):
    rng = np.random.default_rng(seed)
    FWD = ctx.FWD
    atr0 = ctx.atr[rows]
    fw, mfe, mae = testa.path_stats(FWD, rows, side, atr0)
    real = np.nanmean(fw, axis=0)
    er_r = {t: testa.er_from(mfe, mae, atr0, t) for t in TS}
    reps = ctx.control_reps(rows, n_rep, rng)
    Hn = FWD.shape[1]
    cc = np.full((len(reps), Hn), np.nan)
    ce = {t: np.full(len(reps), np.nan) for t in TS}
    for k, r in enumerate(reps):
        if len(r) < 10: continue
        a0 = ctx.atr[r]
        f2, m1, m2 = testa.path_stats(FWD, r, side, a0)
        cc[k] = np.nanmean(f2, axis=0)
        for t in TS:
            ce[t][k] = testa.er_from(m1, m2, a0, t)
    cm, cs = np.nanmean(cc, axis=0), np.nanstd(cc, axis=0)
    z = np.where(cs > 0, (real - cm) / cs, np.nan)
    zc = np.where(cs > 0, (cc - cm) / cs, np.nan)          # 대조군 자신의 z곡선
    zmax_real = np.nanmax(np.abs(z[:180]))
    zmax_null = np.nanmax(np.abs(zc[:, :180]), axis=1)
    p_zmax = (1.0 + np.nansum(zmax_null >= zmax_real)) / (1.0 + np.isfinite(zmax_null).sum())
    out = dict(N=len(rows), days=len(np.unique(ctx.sess[rows])),
               zmax=zmax_real, zmax_t=int(np.nanargmax(np.abs(z[:180]))) + 1,
               p_zmax=p_zmax, real=real, ctrl=cm, z=z)
    for t in TS:
        c = ce[t][np.isfinite(ce[t])]
        out['er%d' % t] = er_r[t]
        out['erc%d' % t] = c.mean() if len(c) else np.nan
        out['erz%d' % t] = (er_r[t] - c.mean()) / c.std() if len(c) and c.std() > 0 else np.nan
        out['erp%d' % t] = (1.0 + (c >= er_r[t]).sum()) / (1.0 + len(c))   # 단측
        out['d%d' % t] = real[t - 1] - cm[t - 1]
        out['z%d' % t] = z[t - 1]
    last = 90
    out['mfe_med90'] = np.nanmedian(mfe[:, last-1]); out['mae_med90'] = np.nanmedian(mae[:, last-1])
    out['mfe_med30'] = np.nanmedian(mfe[:, 29]);     out['mae_med30'] = np.nanmedian(mae[:, 29])
    out['mfe_p75_30'] = np.nanpercentile(mfe[:, 29], 75)
    out['mae_p20_30'] = np.nanpercentile(mae[:, 29], 20)
    with np.errstate(invalid='ignore'):
        ts_ = np.nanargmax(np.where(np.isnan(fw), -np.inf, fw), axis=1) + 1
    out['tstar_q'] = np.nanpercentile(ts_, [25, 50, 75, 90])
    out['giveback90'] = float(np.nanmedian(mfe[:, 89] - fw[:, 89]))
    out['giveback30'] = float(np.nanmedian(mfe[:, 29] - fw[:, 29]))
    out['atr_med'] = float(np.nanmedian(atr0))
    return out
