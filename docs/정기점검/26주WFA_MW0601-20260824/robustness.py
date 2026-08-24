# -*- coding: utf-8 -*-
"""[MW0601 491차 후속2] 피처셋 검증 배터리의 3대 통계 취약점 실측.

① 팻테일 — 극단일 1~2개가 L1의 IC t / L2의 손익 t를 얼마나 지배하는가 (잭나이프)
② 동률(tie) — rank 동률·중앙값 동률이 어디서 몇 개나 조용히 탈락하는가
③ 점질량 — 최빈값 질량이 유효표본·거래수·IC를 얼마나 갉아먹는가

읽기 전용. 기존 스크립트 무수정 — load/build_matrix/analyze 재사용.
"""
from __future__ import print_function
import io, json, math, os, sys
import numpy as np
from collections import defaultdict, Counter

_ROOT = r"C:\Users\82108\PycharmProjects\futures"
sys.path.insert(0, _ROOT)
sys.stdout.reconfigure(encoding="utf-8")
from utils.dll_bootstrap import ensure_conda_dll_path
ensure_conda_dll_path()

from scripts.core_feature_discovery import (
    load, build_matrix, rankdata, corr, tstat, MIN_DAY_ROWS,
)
from scripts.horizon_signal_tradability import roundtrip_cost_pt, RunningMedian
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from live_only import load_live, PT_VALUE


def excess_kurtosis(v):
    v = np.asarray([x for x in v if np.isfinite(x)], dtype=np.float64)
    if v.size < 4:
        return float("nan")
    m, s = v.mean(), v.std(ddof=1)
    if s == 0:
        return float("nan")
    return float((((v - m) / s) ** 4).mean() - 3.0)


def jack_t(daily):
    """일별 값에서 '가장 영향 큰 하루'를 뺀 뒤의 t (양방향 각각 시도해 최악을 취함)."""
    v = np.asarray([x for x in daily if np.isfinite(x)], dtype=np.float64)
    if v.size < 4:
        return float("nan"), float("nan"), -1
    t0, _ = tstat(list(v))
    worst_t, worst_i = t0, -1
    for i in range(v.size):
        w = np.delete(v, i)
        ti, _ = tstat(list(w))
        if not math.isnan(ti) and abs(ti) < abs(worst_t):
            worst_t, worst_i = ti, i
    return t0, worst_t, worst_i


def sim_with_ties(day_rows, col, cl, h):
    """L2 시뮬 + 동률로 신호가 안 난 봉 수를 함께 센다."""
    daily, ties, sigs, skipped_nan = {}, 0, 0, 0
    for d, rows in day_rows.items():
        rm = RunningMedian(); g = 0.0; k_allowed = 0
        for k, i in enumerate(rows):
            v = col[i]
            if math.isnan(v):
                skipped_nan += 1
                continue
            rm.push(v)
            if k < k_allowed:
                continue
            if k + h >= len(rows):
                continue
            med = rm.median()
            if v > med:
                s = 1.0
            elif v < med:
                s = -1.0
            else:
                ties += 1          # ← 조용히 버려지는 봉
                continue
            sigs += 1
            g += s * (cl[rows[k + h]] - cl[rows[k]])
            k_allowed = k + h
        daily[d] = g
    return daily, ties, sigs, skipped_nan


def main():
    feats, closes, dates = load_live()
    names, X, ts_list = build_matrix(feats, verbose=False)
    by_day = defaultdict(list)
    for i, t in enumerate(ts_list):
        by_day[t[:10]].append(i)
    day_rows = {d: r for d, r in by_day.items() if len(r) >= MIN_DAY_ROWS}
    days = sorted(day_rows)
    cl = {i: closes[t] for i, t in enumerate(ts_list) if t in closes}
    cost = roundtrip_cost_pt(float(np.mean([closes[t] for t in ts_list if t in closes])))
    print("순수 라이브 %d거래일 · 피처 %d개 · 왕복비용 %.4fpt\n" % (len(days), len(names), cost))

    # ═══ ① 팻테일 ═══════════════════════════════════════════════
    print("=" * 96)
    print("① 팻테일 — 분포 자체")
    print("=" * 96)
    rets = []
    for d, rows in day_rows.items():
        c = [cl[i] for i in rows if i in cl]
        rets.extend(np.diff(c))
    rets = np.asarray(rets)
    print("1분 수익률 n=%d · std=%.4fpt · 초과첨도=%.1f (정규=0)"
          % (rets.size, rets.std(), excess_kurtosis(rets)))
    a = np.abs(rets)
    print("  |수익률| p50=%.3f p99=%.3f p99.9=%.3f **max=%.3f** (max/std=%.1f배)"
          % (np.percentile(a, 50), np.percentile(a, 99), np.percentile(a, 99.9), a.max(), a.max() / rets.std()))
    top1 = np.sort(a)[::-1][:int(a.size * 0.01)]
    print("  상위 1%% 봉이 전체 |이동|의 %.1f%%를 차지" % (100.0 * top1.sum() / a.sum()))
    dmove = np.array([abs(cl[day_rows[d][-1]] - cl[day_rows[d][0]]) for d in days])
    print("  일중 |변동| 최대일 %.1fpt / 중앙 %.1fpt = **%.1f배**\n"
          % (dmove.max(), np.median(dmove), dmove.max() / np.median(dmove)))

    # ①-b L2 손익 t의 잭나이프
    print("① 팻테일 — L2 손익 t가 하루에 얼마나 좌우되나 (라이브 합격 9셀)")
    print("%-26s %3s %4s %8s %8s %9s %10s" % ("feature", "h", "방향", "t", "잭나이프t", "합격유지", "최대일비중"))
    targets = [("toxicity_flow_stress", 30, -1), ("toxicity_queue_stress", 15, -1),
               ("imbalance_slope", 15, 1), ("ofi_norm", 10, 1), ("microprice_slope", 30, 1),
               ("quality_investor_age_sec", 10, -1), ("va_bandwidth", 15, 1),
               ("cvd", 5, 1), ("macro_nasdaq_chg", 5, -1)]
    surv = 0
    tie_stat = {}
    for nm, h, sgn in targets:
        j = names.index(nm)
        dg, ties, sigs, _ = sim_with_ties(day_rows, X[:, j], cl, h)
        ntr = {}
        # 거래수 재계산용: sim 내부와 동일 규칙이므로 신호수=거래수
        net = np.array([sgn * dg[d] for d in days]) - np.array(
            [len([1]) for d in days]) * 0.0   # 비용은 아래에서 일별 거래수로
        # 일별 거래수 재계산
        per_day_tr = []
        for d in days:
            rm = RunningMedian(); n = 0; ka = 0
            rows = day_rows[d]
            for k, i in enumerate(rows):
                v = X[i, j]
                if math.isnan(v):
                    continue
                rm.push(v)
                if k < ka or k + h >= len(rows):
                    continue
                m = rm.median()
                if v == m:
                    continue
                n += 1; ka = k + h
            per_day_tr.append(n)
        net = np.array([sgn * dg[d] for d in days]) - np.array(per_day_tr, dtype=float) * cost
        t0, tj, wi = jack_t(net)
        ok = "유지" if abs(tj) >= 2.0 and net.mean() > 0 else "**탈락**"
        if ok == "유지":
            surv += 1
        share = 100.0 * abs(net[wi]) / np.abs(net).sum() if wi >= 0 else float("nan")
        print("%-26s %3d %+4d %8.2f %8.2f %9s %9.1f%%" % (nm, h, sgn, t0, tj, ok, share))
        tie_stat[nm] = (ties, sigs)
    print("→ 하루만 빼도 합격 유지: **%d / 9셀**\n" % surv)

    # ═══ ② 동률 ════════════════════════════════════════════════
    print("=" * 96)
    print("② 동률(tie) — 어디서 몇 개가 조용히 사라지나")
    print("=" * 96)
    print("[L1] 일별 IC 계산에서 '고유값<3'으로 통째 제외된 날 (nan 처리, 0 아님)")
    print("%-26s %8s %8s %10s" % ("feature", "유효일", "제외일", "최빈값질량"))
    watch = ["ofi_norm", "cvd_divergence", "cvd_delta_norm", "vwap_position",
             "toxicity_flow_stress", "imbalance_slope", "quality_investor_age_sec",
             "opt_chain_pcr", "foreign_futures_net", "macro_nasdaq_chg"]
    pm = {}
    for nm in watch:
        j = names.index(nm)
        ndrop = 0; nok = 0; allv = []
        for d in days:
            colv = X[np.array(day_rows[d]), j]
            okm = ~np.isnan(colv)
            if okm.sum() < MIN_DAY_ROWS or np.unique(colv[okm]).size < 3:
                ndrop += 1
            else:
                nok += 1
            allv.extend(colv[okm].tolist())
        cnt = Counter(allv)
        top, topn = cnt.most_common(1)[0]
        pm[nm] = (top, 100.0 * topn / max(len(allv), 1))
        print("%-26s %8d %8d %9.1f%% (값=%.4g)" % (nm, nok, ndrop, pm[nm][1], top))
    print()
    print("[L1-hit] 게이트 적중률에서 '값==일중중앙값'이라 제외된 봉 (건수 미출력 = 계측4원칙③ 위반)")
    print("[L2]     '값==러닝중앙값'이라 신호가 발생하지 않은 봉")
    print("%-26s %3s %10s %10s %9s" % ("feature", "h", "동률탈락봉", "실제신호", "탈락비율"))
    for nm, h, _ in targets:
        ties, sigs = tie_stat[nm]
        print("%-26s %3d %10d %10d %8.1f%%" % (nm, h, ties, sigs, 100.0 * ties / max(ties + sigs, 1)))
    print()

    # ═══ ③ 점질량 ═══════════════════════════════════════════════
    print("=" * 96)
    print("③ 점질량 — 최빈값 질량이 유효표본·거래·IC를 얼마나 갉아먹나 (전 피처)")
    print("=" * 96)
    rows_all = []
    for j, nm in enumerate(names):
        colv = X[:, j]
        okm = ~np.isnan(colv)
        if okm.sum() < 100:
            continue
        cnt = Counter(colv[okm].tolist())
        top, topn = cnt.most_common(1)[0]
        mass = 100.0 * topn / okm.sum()
        rows_all.append((nm, mass, top, okm.sum()))
    rows_all.sort(key=lambda r: -r[1])
    print("최빈값 질량 상위 15:")
    print("%-30s %10s %12s" % ("feature", "질량", "최빈값"))
    for nm, mass, top, n in rows_all[:15]:
        print("%-30s %9.1f%% %12.4g" % (nm, mass, top))
    bands = [(0, 10), (10, 30), (30, 50), (50, 90), (90, 101)]
    print("\n질량 구간별 피처 수 / 평균 거래수(h=5, 1계약):")
    print("%-14s %8s %14s" % ("질량구간", "피처수", "평균거래수/일"))
    for lo, hi in bands:
        grp = [r for r in rows_all if lo <= r[1] < hi]
        if not grp:
            continue
        trs = []
        for nm, mass, top, n in grp[:40]:
            j = names.index(nm)
            _, ties, sigs, _ = sim_with_ties(day_rows, X[:, j], cl, 5)
            trs.append(sigs / float(len(days)))
        print("%-14s %8d %14.1f" % ("%d~%d%%" % (lo, hi), len(grp), float(np.mean(trs)) if trs else float("nan")))
    json.dump({"point_mass": [{"name": r[0], "mass_pct": r[1], "mode": r[2]} for r in rows_all]},
              io.open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, default=float)
    print("\nJSON: %s" % sys.argv[1])
    return 0


if __name__ == "__main__":
    sys.exit(main())
