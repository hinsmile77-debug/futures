# -*- coding: utf-8 -*-
"""[MW0601] **피처별** tau 검정 — 개별 피처의 수명을 산출하고 유의한 것을 발굴한다.

§14 초판과의 차이 — 초판은 **풀링**이었다:
   초판  관측단위 = 피처. 82개 피처를 점으로 놓고 Spearman(tau, 최적h)를 봤다.
         답한 질문은 "수명이라는 축이 호라이즌 배정에 쓸 만한가"였다.
   여기  관측단위 = **(피처, 거래일)**. 피처마다 31일 표본으로 tau를 추정하고,
         그 tau가 널 대비 유의한지를 **피처별로** 검정한다.

## 전제 — 분류를 통과한 것만 다룬다

`lifetime_taxonomy.py`가 가려낸 **적격(N) 56개**만 대상이다. 상수형·누적형·계단형·
결정론형에 tau를 재면 '기억'이 아니라 다른 양(갱신주기·추세기울기·격자)을 재게 된다.

## 널은 shuffle이어야 한다

`phase_randomize`는 진폭스펙트럼을 보존한다 = ACF 보존 = **tau 보존**이다.
tau의 널로 쓰면 tau_null ≈ tau_real이 되어 아무것도 판정하지 못한다.
여기서는 **하루 안에서 값 위치를 섞는다** — 분포·결측패턴은 보존하고 자기상관만 파괴.

## 팻테일 대응

적격 피처 중 초과첨도가 8682(`queue_refill_rate`)·2710(`ofi_reversal_speed`)에
이르는 것이 있다. 피어슨 ACF는 극단값 몇 개에 지배되므로 세 버전을 병기한다:
   raw   원계열
   wins  하루별 1%/99% winsorize   <- **주 추정치**
   rank  하루별 순위 변환(Spearman 자기상관) — 가장 강건

셋이 크게 갈리면 그 tau는 분포 꼬리가 만든 것이다.
"""
from __future__ import print_function

import io
import json
import math
import os
import sys
import time

import numpy as np

_ROOT = r"C:\Users\82108\PycharmProjects\futures"
sys.path.insert(0, _ROOT)
sys.stdout.reconfigure(encoding="utf-8")
from utils.dll_bootstrap import ensure_conda_dll_path

ensure_conda_dll_path()
from scripts.core_feature_discovery import build_matrix

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from live_only import load_live
from lifetime_lib import (MAX_LAG, MIN_DAY_OBS, column_to_matrix, to_daily_grid,
                          day_tau, shuffle_day, tstat, bh_fdr)

N_NULL = 15
IC_HZ = [1, 3, 5, 10, 15, 30]
T975_30 = 2.042   # t(0.975, df=30)


def winsorize_day(v, p=0.01):
    out = v.copy()
    ok = np.isfinite(v)
    if ok.sum() < 20:
        return out
    lo, hi = np.percentile(v[ok], [p * 100, (1 - p) * 100])
    out[ok] = np.clip(v[ok], lo, hi)
    return out


def rank_day(v):
    from scipy.stats import rankdata
    out = np.full_like(v, np.nan)
    ok = np.isfinite(v)
    if ok.sum() < 20:
        return out
    out[ok] = rankdata(v[ok])
    return out


def summarize(taus, cens):
    """일자별 tau 목록 -> (평균, sd, CI반폭, 유효일, 절단일)."""
    a = np.array([t for t, c in zip(taus, cens) if np.isfinite(t) and not c])
    n_c = int(sum(1 for c in cens if c))
    if a.size < 3:
        return dict(mean=float("nan"), sd=float("nan"), ci=float("nan"),
                    n=int(a.size), n_cens=n_c, med=float("nan"))
    sd = float(a.std(ddof=1))
    return dict(mean=float(a.mean()), sd=sd,
                ci=float(T975_30 * sd / math.sqrt(a.size)),
                n=int(a.size), n_cens=n_c, med=float(np.median(a)))


def main():
    L = io.StringIO()

    def P(*a):
        s = " ".join(str(x) for x in a)
        print(s, flush=True)
        L.write(s + "\n")

    tax = json.load(open("lifetime_taxonomy.json", encoding="utf-8"))
    elig = tax["eligible"]
    flags = tax.get("flags", {})
    try:
        IC = json.load(open("lifetime_cross.json", encoding="utf-8"))["ic"]
    except Exception:
        IC = {}

    feats, closes, dates = load_live()
    names, X, ts_list = build_matrix(feats, verbose=False)
    days, di, gi = to_daily_grid(ts_list)
    nd = len(days)
    name_idx = {n: j for j, n in enumerate(names)}

    P("=" * 118)
    P("[MW0601] 피처별 tau 검정 — 순수 라이브 %d거래일 (%s ~ %s)" % (nd, days[0], days[-1]))
    P("=" * 118)
    P("대상 **적격 %d개**(분류 통과) · 널 = 일내 shuffle %d회 · ACF 최대 lag %d분"
      % (len(elig), N_NULL, MAX_LAG))
    P("관측단위 = (피처, 거래일). 피처마다 %d일 표본으로 tau를 추정한다." % nd)

    rng = np.random.RandomState(20260824)
    res = {}
    t0 = time.time()
    for i, nm in enumerate(elig):
        j = name_idx.get(nm)
        if j is None:
            continue
        M = column_to_matrix(X[:, j].astype(np.float64), di, gi, nd)

        ver = {}
        for tag, fn in (("raw", lambda r: r),
                        ("wins", winsorize_day),
                        ("rank", rank_day)):
            ts, cs = [], []
            for r in M:
                t, c = day_tau(fn(r))
                ts.append(t)
                cs.append(c)
            ver[tag] = dict(summ=summarize(ts, cs), daily=ts, cens=cs)

        # 널 — wins 버전 기준, 일자별 paired
        null_daily = np.full((N_NULL, nd), np.nan)
        for rep in range(N_NULL):
            for d in range(nd):
                t, c = day_tau(shuffle_day(winsorize_day(M[d]), rng))
                null_daily[rep, d] = t if (np.isfinite(t) and not c) else np.nan
        with np.errstate(invalid="ignore"):
            null_mean_day = np.nanmean(null_daily, axis=0)

        real_day = np.array([t if (np.isfinite(t) and not c) else np.nan
                             for t, c in zip(ver["wins"]["daily"], ver["wins"]["cens"])])
        diff = real_day - null_mean_day
        t_stat, n_pair = tstat(diff)
        from scipy import stats as _st
        p = float(2 * (1 - _st.t.cdf(abs(t_stat), n_pair - 1))) if (
            np.isfinite(t_stat) and n_pair > 2) else float("nan")

        # 전·후반 안정성
        half = nd // 2
        h1 = summarize(ver["wins"]["daily"][:half], ver["wins"]["cens"][:half])
        h2 = summarize(ver["wins"]["daily"][half:], ver["wins"]["cens"][half:])

        # 실측 최강 h
        best_h = None
        if IC:
            cand = [(h, IC[str(h)].get(nm, {}).get("t")) for h in IC_HZ]
            cand = [(h, t) for h, t in cand if t is not None and np.isfinite(t)]
            if len(cand) == len(IC_HZ):
                best_h = max(cand, key=lambda z: abs(z[1]))[0]

        res[nm] = dict(
            raw=ver["raw"]["summ"], wins=ver["wins"]["summ"], rank=ver["rank"]["summ"],
            null_mean=float(np.nanmean(null_mean_day)),
            null_sd=float(np.nanstd(null_mean_day)),
            t=float(t_stat), p=p, n_pair=int(n_pair),
            h1=h1["mean"], h2=h2["mean"], best_h=best_h,
            flags=flags.get(nm, []),
            daily_wins=[None if not np.isfinite(x) else float(x) for x in real_day],
        )
        if (i + 1) % 10 == 0:
            P("   ... %d/%d (%.0fs)" % (i + 1, len(elig), time.time() - t0))

    # ── FDR ────────────────────────────────────────────────────────
    keys = [n for n in elig if n in res]
    pv = [res[n]["p"] for n in keys]
    sig, thr = bh_fdr(pv, q=0.05)
    for n, s in zip(keys, sig):
        res[n]["sig_fdr"] = bool(s)

    P("\n" + "=" * 118)
    P("[1] 피처별 tau 검정 결과 — 널(일내 shuffle) 대비 paired t, BH-FDR q<0.05")
    P("=" * 118)
    P("BH-FDR 임계 p = %.5f (검정 %d회)" % (thr, len(keys)))
    P("\n%-30s %14s %8s %8s %9s %7s %6s %5s %s"
      % ("피처", "tau_wins(95%CI)", "tau_rank", "널tau", "t", "q<.05", "전반", "후반", "플래그"))
    P("-" * 118)
    order = sorted(keys, key=lambda n: -(res[n]["wins"]["mean"]
                                         if np.isfinite(res[n]["wins"]["mean"]) else -1))
    for n in order:
        r = res[n]
        w = r["wins"]
        ci = "%6.1f±%-5.1f" % (w["mean"], w["ci"]) if np.isfinite(w["mean"]) else "     -     "
        P("%-30s %14s %8.1f %8.2f %9.2f %7s %6.1f %5.1f %s"
          % (n[:30], ci, r["rank"]["mean"], r["null_mean"], r["t"],
             "**Y**" if r.get("sig_fdr") else "-",
             r["h1"], r["h2"], ",".join(r["flags"]) or "-"))

    n_sig = sum(1 for n in keys if res[n].get("sig_fdr"))
    P("\n   유의(FDR q<0.05) **%d / %d**" % (n_sig, len(keys)))

    # ── 강건성: 세 버전 일치 ───────────────────────────────────────
    P("\n" + "=" * 118)
    P("[2] 팻테일 강건성 — raw / wins / rank 세 추정치가 갈리는 피처")
    P("=" * 118)
    P("%-30s %8s %8s %8s %9s  %s" % ("피처", "raw", "wins", "rank", "최대격차", "판정"))
    P("-" * 118)
    unstable = []
    for n in order:
        r = res[n]
        v = [r["raw"]["mean"], r["wins"]["mean"], r["rank"]["mean"]]
        if not all(np.isfinite(x) for x in v):
            continue
        spread = max(v) - min(v)
        rel = spread / max(1e-9, np.mean(v))
        if rel >= 0.5:
            unstable.append(n)
            P("%-30s %8.1f %8.1f %8.1f %9.1f  상대격차 %.0f%% — 꼬리 의존"
              % (n[:30], v[0], v[1], v[2], spread, rel * 100))
    P("\n   세 버전이 %.0f%% 이상 갈리는 피처 **%d개** — 이들의 tau는 분포 꼬리가 만든 것이다."
      % (50, len(unstable)))

    # ── 안정성 ─────────────────────────────────────────────────────
    P("\n" + "=" * 118)
    P("[3] 전·후반 안정성 — 유의 피처 중 tau가 재현되는가")
    P("=" * 118)
    stable = []
    P("%-30s %8s %8s %9s  %s" % ("피처", "전반", "후반", "상대차", "판정"))
    P("-" * 118)
    for n in order:
        r = res[n]
        if not r.get("sig_fdr"):
            continue
        a, b = r["h1"], r["h2"]
        if not (np.isfinite(a) and np.isfinite(b)):
            continue
        rel = abs(a - b) / max(1e-9, (a + b) / 2.0)
        ok = rel < 0.5
        if ok and n not in unstable:
            stable.append(n)
        P("%-30s %8.1f %8.1f %8.0f%%  %s"
          % (n[:30], a, b, rel * 100,
             "안정" if ok else "불안정(전후반 %.0f%% 차)" % (rel * 100)))

    # ── 최종 발굴 ──────────────────────────────────────────────────
    P("\n" + "=" * 118)
    P("[4] **발굴 결과** — 유의 ∧ 꼬리무관 ∧ 전후반 안정")
    P("=" * 118)
    P("%-30s %14s %8s %10s %10s  %s"
      % ("피처", "tau(95%CI)", "널대비t", "tau대역", "IC최강h", "대역일치"))
    P("-" * 118)
    match = 0
    for n in sorted(stable, key=lambda x: -res[x]["wins"]["mean"]):
        r = res[n]
        w = r["wins"]
        band = min(IC_HZ, key=lambda h: abs(h - w["mean"]))
        bh = r["best_h"]
        hit = (bh is not None and band == bh)
        if hit:
            match += 1
        P("%-30s %6.1f±%-6.1f %8.2f %10s %10s  %s"
          % (n[:30], w["mean"], w["ci"], r["t"], "h=%d" % band,
             ("h=%d" % bh) if bh else "-", "O" if hit else "X"))
    P("\n   발굴 **%d개** · tau 대역과 IC 최강 h가 일치하는 것 **%d/%d**"
      % (len(stable), match, len(stable)))
    if stable:
        P("   (일치가 우연이라면 기대치는 약 %d/6 = %.1f개)"
          % (len(stable), len(stable) / 6.0))

    json.dump(dict(n_days=nd, eligible=elig, fdr_thr=float(thr),
                   result={n: {k: v for k, v in res[n].items() if k != "daily_wins"}
                           for n in res},
                   daily={n: res[n]["daily_wins"] for n in res},
                   unstable=unstable, stable=stable),
              open("lifetime_tau_test.json", "w", encoding="utf-8"),
              ensure_ascii=False,
              default=lambda o: None if isinstance(o, float) and not np.isfinite(o) else float(o))
    with open("lifetime_tau_test.txt", "w", encoding="utf-8") as f:
        f.write(L.getvalue())
    P("\n저장 -> lifetime_tau_test.json / .txt")


if __name__ == "__main__":
    main()
