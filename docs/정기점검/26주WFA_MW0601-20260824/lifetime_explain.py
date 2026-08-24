# -*- coding: utf-8 -*-
"""[MW0601] tau가 무엇을 재는지 실측 ACF로 보이는 설명용 산출 (읽기 전용).

'피처가 자기 값을 얼마나 오래 기억하는가'를 숫자로 보이기 위해,
발굴 피처 중 수명 대역이 다른 것들의 **실측 자기상관 곡선**을 뽑는다.
"""
from __future__ import print_function

import io
import os
import sys

import numpy as np

_ROOT = r"C:\Users\82108\PycharmProjects\futures"
sys.path.insert(0, _ROOT)
sys.stdout.reconfigure(encoding="utf-8")
from utils.dll_bootstrap import ensure_conda_dll_path

ensure_conda_dll_path()
from scripts.core_feature_discovery import build_matrix

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from live_only import load_live
from lifetime_lib import acf_nan, column_to_matrix, to_daily_grid

SHOW = ["vwap_position", "hurst", "kyle_lambda", "ret_5m", "mlofi_slope"]
LAGS = [1, 2, 3, 5, 10, 15, 20, 30, 45, 60]


def winsorize_day(v, p=0.01):
    out = v.copy()
    ok = np.isfinite(v)
    if ok.sum() < 20:
        return out
    lo, hi = np.percentile(v[ok], [p * 100, (1 - p) * 100])
    out[ok] = np.clip(v[ok], lo, hi)
    return out


def main():
    L = io.StringIO()

    def P(*a):
        s = " ".join(str(x) for x in a)
        print(s)
        L.write(s + "\n")

    feats, closes, dates = load_live()
    names, X, ts_list = build_matrix(feats, verbose=False)
    days, di, gi = to_daily_grid(ts_list)
    nd = len(days)
    idx = {n: j for j, n in enumerate(names)}

    P("=" * 100)
    P("[MW0601] tau 해설 — 실측 자기상관 곡선 (순수 라이브 %d거래일)" % nd)
    P("=" * 100)
    P("ACF(k) = 지금 값과 k분 뒤 값의 상관계수 (거래일별로 계산 후 평균)")
    P("tau = ACF가 1/e = 0.368 아래로 내려가는 시점\n")

    P("%-24s %6s  %s" % ("피처", "tau", " ".join("%6s" % ("k=%d" % k) for k in LAGS)))
    P("-" * 100)
    out = {}
    for nm in SHOW:
        j = idx.get(nm)
        if j is None:
            continue
        M = column_to_matrix(X[:, j].astype(np.float64), di, gi, nd)
        acc = []
        for r in M:
            a = acf_nan(winsorize_day(r), max_lag=max(LAGS))
            if np.isfinite(a[1]):
                acc.append(a)
        if not acc:
            continue
        A = np.nanmean(np.array(acc), axis=0)
        out[nm] = A
        # tau
        tau = None
        prev = 1.0
        for k in range(1, max(LAGS) + 1):
            if not np.isfinite(A[k]):
                break
            if A[k] < 1.0 / np.e:
                tau = (k - 1) + (prev - 1.0 / np.e) / (prev - A[k])
                break
            prev = A[k]
        P("%-24s %6s  %s"
          % (nm[:24], ("%.1f" % tau) if tau else ">60",
             " ".join("%6.3f" % A[k] if np.isfinite(A[k]) else "%6s" % "-" for k in LAGS)))

    P("\n" + "=" * 100)
    P("[해석용] 지금 값이 평균보다 +2.0 (표준편차 단위) 높다고 할 때,")
    P("         k분 뒤 기대값 = ACF(k) x 2.0")
    P("=" * 100)
    P("%-24s %s" % ("피처", " ".join("%7s" % ("%d분뒤" % k) for k in [1, 5, 10, 30, 60])))
    P("-" * 100)
    for nm, A in out.items():
        vals = []
        for k in [1, 5, 10, 30, 60]:
            vals.append("%+7.2f" % (A[k] * 2.0) if np.isfinite(A[k]) else "%7s" % "-")
        P("%-24s %s" % (nm[:24], " ".join(vals)))

    P("\n" + "=" * 100)
    P("[비교] 널(하루 안에서 값을 섞은 것)의 ACF — 기억이 없으면 이렇게 된다")
    P("=" * 100)
    rng = np.random.RandomState(1)
    j = idx["vwap_position"]
    M = column_to_matrix(X[:, j].astype(np.float64), di, gi, nd)
    acc = []
    for r in M:
        v = r.copy()
        ok = np.isfinite(v)
        if ok.sum() < 60:
            continue
        v[ok] = rng.permutation(v[ok])
        a = acf_nan(v, max_lag=max(LAGS))
        if np.isfinite(a[1]):
            acc.append(a)
    A = np.nanmean(np.array(acc), axis=0)
    P("%-24s %6s  %s" % ("vwap_position(섞음)", "0.6",
                         " ".join("%6.3f" % A[k] if np.isfinite(A[k]) else "%6s" % "-"
                                  for k in LAGS)))

    with open("lifetime_explain.txt", "w", encoding="utf-8") as f:
        f.write(L.getvalue())
    P("\n저장 -> lifetime_explain.txt")


if __name__ == "__main__":
    main()
