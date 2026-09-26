# -*- coding: utf-8 -*-
"""GP 검정 A 공용 라이브러리 (2026-09-10, MW0601).

원천: raw_candles (2025-08-19~2026-09-09). 장 마감 후/개장 전 스냅샷만 읽는다.
비용/포인트가치: settings.py gp_rule_cost 정본 (미니 50,000원/pt, CYBOS/CREON 분리).
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))

PT_VALUE = 50_000.0                 # MINI_FUTURES_PT_VALUE
COST = {"CYBOS": 0.246018, "CREON": 0.079900, "DOC": 0.15}   # 왕복 pt
GP_PERIOD = 20
SESS_LO, SESS_HI = "09:00", "15:35"


def _gp(close: np.ndarray, n: int = GP_PERIOD):
    """세션 내 GB/GS. 첫 n-1 봉 NaN."""
    s = pd.Series(close)
    lo = s.rolling(n, min_periods=n).min()
    hi = s.rolling(n, min_periods=n).max()
    return ((s - lo) / s * 200.0).values, ((hi - s) / s * 200.0).values


def build_panel(min_bars: int = 300) -> dict:
    """세션별 dict. 분 그리드로 재색인(ffill)해 봉 인덱스 == 경과 분 을 보장."""
    c = pd.read_pickle(os.path.join(HERE, "candles.pkl"))
    c["dt"] = pd.to_datetime(c["ts"])
    c["session"] = c["dt"].dt.strftime("%Y-%m-%d")
    c["hhmm"] = c["dt"].dt.strftime("%H:%M")
    c = c[(c["hhmm"] >= SESS_LO) & (c["hhmm"] <= SESS_HI)]
    c = c.sort_values("dt").drop_duplicates("dt")
    out, synth_n, tot_n = {}, 0, 0
    for s, g in c.groupby("session"):
        if len(g) < min_bars:
            continue
        g = g.set_index("dt")
        grid = pd.date_range(g.index[0], g.index[-1], freq="1min")
        real = g.reindex(grid)
        syn = real["close"].isna().values
        real[["open", "high", "low", "close"]] = real[["open", "high", "low", "close"]].ffill()
        real["volume"] = real["volume"].fillna(0.0)
        cl = real["close"].astype(float).values
        hi_ = real["high"].astype(float).values
        lo_ = real["low"].astype(float).values
        gb, gs = _gp(cl, GP_PERIOD)
        pc = np.r_[np.nan, cl[:-1]]
        tr = np.nanmax(np.c_[hi_ - lo_, np.abs(hi_ - pc), np.abs(lo_ - pc)], axis=1)
        atr = pd.Series(tr).rolling(14, min_periods=14).mean().values
        ma20 = pd.Series(cl).rolling(20, min_periods=20).mean().values
        ma60 = pd.Series(cl).rolling(60, min_periods=60).mean().values
        out[s] = dict(hhmm=np.array([t.strftime("%H:%M") for t in grid]),
                      close=cl, gb=gb, gs=gs, atr=atr, ma20=ma20, ma60=ma60,
                      synth=syn, n=len(cl))
        synth_n += int(syn.sum()); tot_n += len(cl)
    return out, dict(sessions=len(out), bars=tot_n, synth=synth_n,
                     synth_pct=100.0 * synth_n / max(tot_n, 1))


# ── 신호 생성 ────────────────────────────────────────────────────────────
def cross_up(x: np.ndarray, lvl: float) -> np.ndarray:
    """코드 정본 정의: prev < lvl and cur >= lvl (settings.py 553차 고정)."""
    p = np.r_[np.nan, x[:-1]]
    return (p < lvl) & (x >= lvl)


def squeeze_recent(gb, gs, lookback=10, thr=0.5, spread=0.5):
    """압축(GB<=thr & GS<=thr & |GB-GS|<=spread)이 최근 lookback 봉 안에 있었는가."""
    z = (gb <= thr) & (gs <= thr) & (np.abs(gb - gs) <= spread)
    z = np.nan_to_num(z, nan=False).astype(bool)
    out = np.zeros(len(z), bool)
    run = 0
    for i in range(len(z)):
        if z[i]:
            run = lookback
        out[i] = run > 0
        if run > 0:
            run -= 1
    return out


def gen_entries(panel, side, *, lvl=0.5, opp_max=None, need_squeeze=False,
                regime=None, t_lo="09:20", t_hi="14:50", once_per_day=False,
                hold=90, nonoverlap=True, atr_min=None):
    """진입 리스트 [(session, i0)] 생성. i0 = 신호 봉 인덱스(진입은 i0+1)."""
    ent = []
    for s in sorted(panel):
        d = panel[s]
        trig_line = d["gb"] if side > 0 else d["gs"]
        opp_line = d["gs"] if side > 0 else d["gb"]
        sig = cross_up(trig_line, lvl)
        ok = sig & (d["hhmm"] >= t_lo) & (d["hhmm"] <= t_hi)
        ok &= ~d["synth"]
        if opp_max is not None:
            ok &= (opp_line <= opp_max)
        if need_squeeze:
            ok &= squeeze_recent(d["gb"], d["gs"])
        if regime == "down":
            ok &= (d["ma20"] < d["ma60"])
        elif regime == "up":
            ok &= (d["ma20"] > d["ma60"])
        if atr_min is not None:
            ok &= (d["atr"] >= atr_min)
        ok &= np.isfinite(d["atr"])
        idx = np.flatnonzero(ok)
        busy_until, cnt = -1, 0
        for i in idx:
            if i + 1 >= d["n"]:
                continue
            if nonoverlap and i <= busy_until:
                continue
            if once_per_day and cnt >= 1:
                break
            ent.append((s, int(i)))
            busy_until = i + hold
            cnt += 1
    return ent


# ── 손익 (시간청산 + 15:05 강제) ─────────────────────────────────────────
def time_exit_pnl(panel, entries, side, hold, cost):
    """일별 손익 시계열(pt) + 거래별 손익."""
    per_trade = []
    for s, i0 in entries:
        d = panel[s]
        e = i0 + 1
        if e >= d["n"]:
            continue
        x = min(e + hold, d["n"] - 1)
        force = np.flatnonzero(d["hhmm"] >= "15:05")
        if len(force):
            x = min(x, int(force[0]))
        pnl = side * (d["close"][x] - d["close"][e]) - cost
        per_trade.append((s, i0, e, x, pnl))
    df = pd.DataFrame(per_trade, columns=["session", "i0", "ent", "ext", "pnl"])
    days = pd.Index(sorted(panel))
    daily = df.groupby("session")["pnl"].sum().reindex(days).fillna(0.0)
    return daily, df


def tstat(x):
    x = np.asarray(x, float)
    sd = x.std(ddof=1)
    return x.mean() / (sd / np.sqrt(len(x))) if sd > 0 else np.nan
