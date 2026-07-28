# -*- coding: utf-8 -*-
"""CORE 피처 발굴 스크리닝 — 전 피처의 방향 예측력을 동일 잣대로 평가 (읽기 전용).

목적: CLAUDE.md 절대원칙 §3의 CORE 피처(체크리스트 게이트)를 교체·보강할 후보를
전수 스크리닝으로 찾는다. 현행 CORE도 **같은 잣대로 함께 평가**해 비교 가능하게 한다.

방법론 — Phase 0/372차 교훈을 그대로 반영:
  · 신호단위 풀링이 아니라 **일자단위 독립관측**으로 유의성 판정
    (풀링하면 하루 수백 개 상관된 분봉이 표본수를 부풀려 t가 과대평가된다)
  · **다중비교 보정** — 피처 수 × 호라이즌 수만큼 검정하므로 Bonferroni 적용
  · **전·후반 분할 안정성** — 우연한 구간 적합을 걸러낸다
  · 미래참조 없음 — 시각 t의 피처 vs t→t+h 수익률, 일중으로만(오버나이트 제외)

지표:
  IC      — 일자별 Spearman(feature_t, fwd_ret) → 일자평균과 t
  hit     — sign(feature 중심화) == sign(fwd_ret) 적중률 → 일자평균과 t (게이트 형태의 유용성)

실행:
  python scripts/core_feature_discovery.py                  # 최근 120거래일, h=5/15/30
  python scripts/core_feature_discovery.py --days 60 --top 30
"""
from __future__ import print_function

import argparse
import json
import math
import os
import sqlite3
import sys
from collections import defaultdict

import numpy as np

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DB = os.path.join(_ROOT, "data", "db", "raw_data.db")

# CLAUDE.md 절대원칙 §3 현행 CORE (비교 기준선)
INCUMBENT = {
    "cvd_divergence": "단기 CORE",
    "vwap_position":  "단·중기 CORE",
    "ofi_norm":       "단기 CORE",
    "opt_chain_pcr":  "장기 CORE",
}
# 체크리스트가 실제로 소비하는 값(파라미터명은 cvd_direction이나 실제는 cvd_delta_norm)
INCUMBENT_EXTRA = {"cvd_delta_norm": "단기 CORE 실소비값"}

HORIZONS = [5, 15, 30]      # 단기/중기/장기 대표
MIN_DAY_ROWS = 60           # 하루 최소 유효 분봉
MIN_DAYS = 20
MIN_COVERAGE = 0.80         # 피처 결측 허용 하한
MIN_DISTINCT = 20           # 상수·이진 플래그 제외


def load(days):
    con = sqlite3.connect(RAW_DB)
    cur = con.cursor()
    cur.execute("SELECT DISTINCT substr(ts,1,10) d FROM raw_candles ORDER BY d DESC LIMIT ?", (days,))
    dates = sorted(r[0] for r in cur.fetchall())
    lo = dates[0]
    cur.execute("SELECT ts, close FROM raw_candles WHERE substr(ts,1,10) >= ? ORDER BY ts", (lo,))
    closes = {ts: float(c) for ts, c in cur.fetchall() if c is not None}
    cur.execute("SELECT ts, features FROM raw_features WHERE substr(ts,1,10) >= ? ORDER BY ts", (lo,))
    feats = []
    for ts, fj in cur.fetchall():
        if ts not in closes:
            continue
        try:
            feats.append((ts, json.loads(fj)))
        except Exception:
            continue
    con.close()
    return feats, closes, dates


def build_matrix(feats):
    """공통 수치 피처만 추려 (이름목록, 값행렬, ts목록) 반환."""
    cnt = defaultdict(int)
    for _, f in feats:
        for k, v in f.items():
            if isinstance(v, bool):
                continue
            if isinstance(v, (int, float)) and not (isinstance(v, float) and math.isnan(v)):
                cnt[k] += 1
    n = len(feats)
    names = sorted(k for k, c in cnt.items() if c >= n * MIN_COVERAGE)
    X = np.full((n, len(names)), np.nan, dtype=np.float64)
    idx = {k: j for j, k in enumerate(names)}
    ts_list = []
    for i, (ts, f) in enumerate(feats):
        ts_list.append(ts)
        for k, v in f.items():
            j = idx.get(k)
            if j is None:
                continue
            if isinstance(v, bool):
                continue
            if isinstance(v, (int, float)):
                X[i, j] = float(v)
    # 상수·저해상도(이진 플래그 등) 제외
    keep = []
    for j, k in enumerate(names):
        col = X[:, j]
        col = col[~np.isnan(col)]
        if col.size < n * MIN_COVERAGE:
            continue
        if np.unique(col).size < MIN_DISTINCT:
            continue
        keep.append(j)
    return [names[j] for j in keep], X[:, keep], ts_list


def rankdata(a):
    """평균순위(동점 처리) — scipy 없이."""
    order = np.argsort(a, kind="mergesort")
    ranks = np.empty(a.size, dtype=np.float64)
    ranks[order] = np.arange(1, a.size + 1, dtype=np.float64)
    # 동점 평균 처리
    sa = a[order]
    i = 0
    while i < sa.size:
        j = i
        while j + 1 < sa.size and sa[j + 1] == sa[i]:
            j += 1
        if j > i:
            ranks[order[i:j + 1]] = (i + 1 + j + 1) / 2.0
        i = j + 1
    return ranks


def corr(x, y):
    xm, ym = x - x.mean(), y - y.mean()
    dx, dy = math.sqrt(float((xm * xm).sum())), math.sqrt(float((ym * ym).sum()))
    if dx == 0 or dy == 0:
        return float("nan")
    return float((xm * ym).sum() / (dx * dy))


def tstat(v):
    v = np.asarray([x for x in v if not math.isnan(x)], dtype=np.float64)
    if v.size < 3:
        return float("nan"), 0
    sd = v.std(ddof=1)
    if sd == 0:
        return float("nan"), v.size
    return float(v.mean() / (sd / math.sqrt(v.size))), v.size


def analyze(names, X, ts_list, closes, horizon):
    """피처별 (일자평균 IC, IC t, 일자평균 hit, hit t, 유효일수, 전·후반 IC)."""
    by_day = defaultdict(list)
    for i, ts in enumerate(ts_list):
        by_day[ts[:10]].append(i)
    days = sorted(by_day)

    nf = len(names)
    ic_days = [[] for _ in range(nf)]
    hit_days = [[] for _ in range(nf)]
    day_tag = []

    for d in days:
        rows = by_day[d]
        if len(rows) < MIN_DAY_ROWS + horizon:
            continue
        ts_arr = [ts_list[i] for i in rows]
        # 일중 전방 수익률 (오버나이트 제외)
        fwd = np.full(len(rows), np.nan)
        for a in range(len(rows) - horizon):
            t0, t1 = ts_arr[a], ts_arr[a + horizon]
            if t0[:10] != t1[:10]:
                continue
            fwd[a] = closes[t1] - closes[t0]
        valid = ~np.isnan(fwd)
        if valid.sum() < MIN_DAY_ROWS:
            continue
        day_tag.append(d)
        fr = fwd[valid]
        fr_rank = rankdata(fr)
        fr_sign = np.sign(fr)
        sub = X[np.array(rows)[valid], :]
        for j in range(nf):
            col = sub[:, j]
            ok = ~np.isnan(col)
            if ok.sum() < MIN_DAY_ROWS or np.unique(col[ok]).size < 3:
                ic_days[j].append(float("nan")); hit_days[j].append(float("nan")); continue
            c = col[ok]
            ic_days[j].append(corr(rankdata(c), fr_rank[ok]))
            # 게이트 형태: 일중 중앙값 기준 중심화 후 부호 일치율
            cs = np.sign(c - np.median(c))
            m = (cs != 0) & (fr_sign[ok] != 0)
            hit_days[j].append(float((cs[m] == fr_sign[ok][m]).mean()) if m.sum() >= 20 else float("nan"))

    half = len(day_tag) // 2
    out = []
    for j, nm in enumerate(names):
        ic = np.array(ic_days[j], dtype=np.float64)
        ht = np.array(hit_days[j], dtype=np.float64)
        ic_t, nd = tstat(ic)
        hit_t, _ = tstat(ht - 0.5)
        ic_v = ic[~np.isnan(ic)]

        def _half_mean(seg):
            # 전·후반 IC 평균. 유효값이 없으면 nan (np.nanmean의 빈 슬라이스 경고 회피)
            s = seg[~np.isnan(seg)]
            return float(s.mean()) if s.size else float("nan")

        ic1 = _half_mean(ic[:half]) if half > 2 else float("nan")
        ic2 = _half_mean(ic[half:]) if half > 2 else float("nan")
        out.append({
            "name": nm,
            "ic": float(ic_v.mean()) if ic_v.size else float("nan"),
            "ic_t": ic_t, "n_days": nd,
            "hit": float(np.nanmean(ht)) if np.isfinite(ht).any() else float("nan"),
            "hit_t": hit_t,
            "ic_h1": float(ic1), "ic_h2": float(ic2),
            "stable": (np.isfinite(ic1) and np.isfinite(ic2)
                       and np.sign(ic1) == np.sign(ic2) and abs(ic1) > 0.005 and abs(ic2) > 0.005),
        })
    return out, len(day_tag)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=120)
    ap.add_argument("--top", type=int, default=20)
    args = ap.parse_args()

    feats, closes, dates = load(args.days)
    print("raw_features %d행, %d거래일 (%s ~ %s)" % (len(feats), len(dates), dates[0], dates[-1]))
    names, X, ts_list = build_matrix(feats)
    print("스크리닝 대상 피처 %d개 (커버리지 %.0f%%+ · 고유값 %d+ 만)"
          % (len(names), MIN_COVERAGE * 100, MIN_DISTINCT))

    n_tests = len(names) * len(HORIZONS)
    # 양측 t 임계 ≈ Bonferroni α=0.05
    bonf_t = 3.0 + 0.55 * math.log(max(n_tests, 2))
    print("다중비교: 검정 %d회 → Bonferroni 근사 |t| 임계 ≈ %.2f" % (n_tests, bonf_t))

    results = {}
    for h in HORIZONS:
        res, nd = analyze(names, X, ts_list, closes, h)
        results[h] = res
        grp = {5: "단기(1m·3m·5m)", 15: "중기(10m·15m)", 30: "장기(30m)"}[h]
        print()
        print("=" * 104)
        print("h=%d분  %s   유효일수 %d" % (h, grp, nd))
        print("=" * 104)

        print("  [기준선] 현행 CORE 및 실소비값")
        print("  %-26s %8s %8s %8s %8s %7s %s" % ("feature", "IC", "IC_t", "hit", "hit_t", "안정", "역할"))
        base = dict(INCUMBENT); base.update(INCUMBENT_EXTRA)
        for r in res:
            if r["name"] in base:
                print("  %-26s %8.4f %8.2f %8.4f %8.2f %7s %s"
                      % (r["name"], r["ic"], r["ic_t"], r["hit"], r["hit_t"],
                         "O" if r["stable"] else "-", base[r["name"]]))

        print()
        print("  [후보] |IC_t| 상위 %d — Bonferroni 통과(|t|>%.2f)는 ★" % (args.top, bonf_t))
        print("  %-26s %8s %8s %8s %8s %7s %8s %8s" %
              ("feature", "IC", "IC_t", "hit", "hit_t", "안정", "IC전반", "IC후반"))
        ranked = sorted([r for r in res if np.isfinite(r["ic_t"])],
                        key=lambda r: -abs(r["ic_t"]))
        for r in ranked[:args.top]:
            star = "★" if abs(r["ic_t"]) > bonf_t else " "
            mark = "*" if r["name"] in base else " "
            print(" %s%s%-25s %8.4f %8.2f %8.4f %8.2f %7s %8.4f %8.4f"
                  % (star, mark, r["name"], r["ic"], r["ic_t"], r["hit"], r["hit_t"],
                     "O" if r["stable"] else "-", r["ic_h1"], r["ic_h2"]))

    # 종합: 전 호라이즌에서 안정적으로 유의한 피처
    print()
    print("=" * 104)
    print("종합 — Bonferroni 통과 ∧ 전·후반 부호 일치 (호라이즌별)")
    print("=" * 104)
    for h in HORIZONS:
        win = [r for r in results[h]
               if np.isfinite(r["ic_t"]) and abs(r["ic_t"]) > bonf_t and r["stable"]]
        win.sort(key=lambda r: -abs(r["ic_t"]))
        print("  h=%-3d 통과 %d개: %s" % (
            h, len(win), ", ".join("%s(IC=%+.3f,t=%.1f)" % (r["name"], r["ic"], r["ic_t"])
                                   for r in win[:12]) or "없음"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
