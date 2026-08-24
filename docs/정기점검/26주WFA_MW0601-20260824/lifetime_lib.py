# -*- coding: utf-8 -*-
"""[MW0601] 수명분석 공통 기반 — 하루 단위 정렬 · NaN-aware ACF · tau 추정.

lifetime.py 초판의 두 약점을 고친다:

1. **세그먼트 손실** — 초판은 '연속 1분 구간'으로 쪼갠 뒤 `max_lag+30`(=120분) 미만
   세그먼트를 통째로 버렸다. 일내 구멍 55건 때문에 31거래일이 67세그먼트로 쪼개져
   하루가 여러 조각이 됐다. 여기서는 **하루를 09:00~15:30 분 격자에 정렬**하고
   구멍을 NaN으로 두며, ACF는 **lag마다 유효쌍만** 써서 계산한다. 조각을 버리지 않는다.

2. **tau 이산화·절단** — 초판은 1/e 교차 lag를 정수로 돌려주고, 도달 못 하면 상한값
   (90)을 값처럼 기록했다. 여기서는 선형보간으로 **연속값**을 주고, 미도달은
   `censored=True`로 **표기**한다 — 절단을 값으로 위장하지 않는다(계측 4원칙 ②).
"""
from __future__ import print_function

import math
from collections import defaultdict
from datetime import datetime

import numpy as np

GRID_START = 9 * 60          # 09:00
GRID_END = 15 * 60 + 30      # 15:30
GRID_N = GRID_END - GRID_START
MAX_LAG = 90
MIN_PAIRS = 30               # lag별 최소 유효쌍
MIN_DAY_OBS = 60             # 하루 최소 유효 관측


def to_daily_grid(ts_list):
    """ts 목록 -> (날짜목록, 행인덱스->(일번호, 격자위치)) 매핑.

    Returns:
        days: 정렬된 날짜 문자열 목록
        di:   각 행의 일 번호 (len == len(ts_list))
        gi:   각 행의 격자 위치 (09:00 기준 분). 격자 밖이면 -1
    """
    days_set = sorted({t[:10] for t in ts_list})
    dmap = {d: i for i, d in enumerate(days_set)}
    di = np.empty(len(ts_list), dtype=np.int32)
    gi = np.empty(len(ts_list), dtype=np.int32)
    for i, t in enumerate(ts_list):
        dt = datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
        di[i] = dmap[t[:10]]
        m = dt.hour * 60 + dt.minute
        gi[i] = (m - GRID_START) if GRID_START <= m < GRID_END else -1
    return days_set, di, gi


def column_to_matrix(col, di, gi, n_days):
    """피처 1열 -> (n_days, GRID_N) 행렬. 빈 칸은 NaN."""
    M = np.full((n_days, GRID_N), np.nan, dtype=np.float64)
    ok = gi >= 0
    M[di[ok], gi[ok]] = col[ok]
    return M


def detrend_day(v):
    """하루 계열에서 선형추세 제거 (유효점만으로 적합). NaN 위치는 보존."""
    ok = np.isfinite(v)
    if ok.sum() < 10:
        return v.copy()
    x = np.arange(v.size, dtype=np.float64)[ok]
    y = v[ok]
    n = x.size
    sx, sy = x.sum(), y.sum()
    sxx, sxy = float(np.dot(x, x)), float(np.dot(x, y))
    den = n * sxx - sx * sx
    out = v.copy()
    if den <= 0:
        return out
    b = (n * sxy - sx * sy) / den
    a = (sy - b * sx) / n
    out[ok] = y - (a + b * x)   # x는 이미 ok로 걸러진 유효 위치 배열이다
    return out


def trend_r2(v):
    """하루 계열의 선형추세 설명력 R^2 (누적/비정상 판정용)."""
    ok = np.isfinite(v)
    if ok.sum() < 10:
        return float("nan")
    y = v[ok]
    if y.std() <= 0:
        return float("nan")
    r = detrend_day(v)[ok]
    ss_tot = float(np.dot(y - y.mean(), y - y.mean()))
    if ss_tot <= 0:
        return float("nan")
    return 1.0 - float(np.dot(r, r)) / ss_tot


def acf_nan(v, max_lag=MAX_LAG, min_pairs=MIN_PAIRS):
    """NaN-aware 표본 자기상관. lag마다 유효쌍만으로 정규화.

    lag별 자체 표준화를 쓴다 — 결측이 흩어져 있을 때 공통 분모(lag0 분산)를
    쓰는 것보다 안정적이다.
    """
    out = np.full(max_lag + 1, np.nan)
    ok0 = np.isfinite(v)
    if ok0.sum() < MIN_DAY_OBS:
        return out
    out[0] = 1.0
    for k in range(1, max_lag + 1):
        a, b = v[:-k], v[k:]
        m = np.isfinite(a) & np.isfinite(b)
        n = int(m.sum())
        if n < min_pairs:
            break
        aa, bb = a[m], b[m]
        aa = aa - aa.mean()
        bb = bb - bb.mean()
        da = float(np.dot(aa, aa))
        db = float(np.dot(bb, bb))
        if da <= 0 or db <= 0:
            break
        out[k] = float(np.dot(aa, bb)) / math.sqrt(da * db)
    return out


def tau_from_acf(acf, thr=1.0 / math.e):
    """ACF -> 1/e 교차 반감기. 선형보간한 **연속값**.

    Returns:
        (tau, censored)  censored=True면 max_lag 안에서 thr 아래로 안 내려갔다는 뜻.
        tau는 그 경우 max_lag(관측 상한)를 담지만 **값으로 쓰면 안 된다**.
    """
    n = acf.size - 1
    prev = 1.0
    for k in range(1, n + 1):
        r = acf[k]
        if not np.isfinite(r):
            return float(k - 1), True      # 데이터가 끊긴 지점 — 미도달 취급
        if r < thr:
            if prev <= r:
                return float(k), False
            frac = (prev - thr) / (prev - r)
            return float(k - 1) + max(0.0, min(1.0, frac)), False
        prev = r
    return float(n), True


def day_tau(v, max_lag=MAX_LAG, detrend=False):
    """하루 계열 -> (tau, censored). 표본 미달이면 (nan, True)."""
    if detrend:
        v = detrend_day(v)
    if np.isfinite(v).sum() < MIN_DAY_OBS:
        return float("nan"), True
    a = acf_nan(v, max_lag)
    if not np.isfinite(a[1]):
        return float("nan"), True
    return tau_from_acf(a)


def variance_ratio(v, k=10):
    """분산비 VR(k) = Var(x_{t+k}-x_t) / (k * Var(x_{t+1}-x_t)).

    랜덤워크 ~1 · 추세/누적 >1 · 평균회귀 <1.
    """
    ok = np.isfinite(v)
    if ok.sum() < 60:
        return float("nan")
    d1 = np.diff(v)
    d1 = d1[np.isfinite(d1)]
    dk = v[k:] - v[:-k]
    dk = dk[np.isfinite(dk)]
    if d1.size < 20 or dk.size < 20:
        return float("nan")
    v1, vk = d1.var(), dk.var()
    if v1 <= 0:
        return float("nan")
    return float(vk / (k * v1))


def shuffle_day(v, rng):
    """하루 안에서만 유효값 위치를 섞는다 — 자기상관 파괴, 분포·결측패턴 보존."""
    out = v.copy()
    ok = np.isfinite(v)
    if ok.sum() < 2:
        return out
    vals = v[ok]
    out[ok] = rng.permutation(vals)
    return out


def daily_matrices(names, X, ts_list):
    """전 피처를 (n_days, GRID_N) 행렬 dict로. 메모리 주의 — 필요한 것만 뽑아 쓸 것."""
    days, di, gi = to_daily_grid(ts_list)
    return days, di, gi


def tstat(v):
    v = np.asarray([x for x in v if np.isfinite(x)], dtype=np.float64)
    if v.size < 3:
        return float("nan"), 0
    sd = v.std(ddof=1)
    if sd == 0:
        return float("nan"), v.size
    return float(v.mean() / (sd / math.sqrt(v.size))), int(v.size)


def bh_fdr(pvals, q=0.05):
    """Benjamini-Hochberg — 유의 판정 불린 배열과 임계 p 반환."""
    p = np.asarray(pvals, dtype=np.float64)
    ok = np.isfinite(p)
    idx = np.where(ok)[0]
    if idx.size == 0:
        return np.zeros(p.size, dtype=bool), float("nan")
    order = idx[np.argsort(p[idx])]
    m = order.size
    thr = 0.0
    for i, j in enumerate(order, start=1):
        if p[j] <= q * i / m:
            thr = p[j]
    sig = np.zeros(p.size, dtype=bool)
    if thr > 0:
        sig[ok] = p[ok] <= thr
    return sig, thr
