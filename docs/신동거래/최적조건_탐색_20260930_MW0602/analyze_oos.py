# -*- coding: utf-8 -*-
"""표본 밖 점검 — 9/30 최적 조합이 다른 날에도 버는가 · 전 기간 최적은 무엇인가."""
import json, os, collections, statistics as stt
HERE = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(os.path.join(HERE, "grid_all.json"), encoding="utf-8"))
T = "2026-09-30"
M = 1e4
days = sorted(G)
flow_days = [d for d in days if G[d]["bias"] is not None]
print("거래일 %d (흐름 있는 날 %d: %s)" % (len(days), len(flow_days), flow_days))


def table(fam):
    t = collections.defaultdict(dict)
    for d in days:
        for p, net, n in G[d]["fam"].get(fam, []):
            t[p][d] = (net, n)
    return t


def show(fam, p, t, label):
    v = t[p]
    others = [v[d][0] for d in v if d != T]
    pos = sum(x > 0 for x in others)
    h = [d for d in v if d != T]
    half = len(h) // 2
    print("  [%s] %s" % (label, p))
    print("      9/30 %+.1f만 | 다른 %d일 합 %+.1f만 · 일평균 %+.1f · 흑자일 %d/%d · 최악 %+.1f · 전반 %+.1f / 후반 %+.1f" % (
        v.get(T, (0,))[0] / M, len(others), sum(others) / M, (stt.mean(others) / M) if others else 0, pos, len(others),
        (min(others) / M) if others else 0, sum(v[d][0] for d in h[:half]) / M, sum(v[d][0] for d in h[half:]) / M))


for fam in "ABCDE":
    t = table(fam)
    if not t:
        continue
    print("\n== 계열 %s  조합 %d" % (fam, len(t)))
    full = [p for p in t if T in t[p]]
    best930 = max(full, key=lambda p: t[p][T][0])
    show(fam, best930, t, "9/30 최적")
    # 9/30 상위 1% 조합 묶음의 다른 날 성과 분포
    top = sorted(full, key=lambda p: -t[p][T][0])[:max(1, len(full) // 100)]
    o = [sum(t[p][d][0] for d in t[p] if d != T) for p in top]
    print("      9/30 상위1%% %d조합 → 다른 날 합: 중앙 %+.1f만 · 흑자 조합 %d/%d" % (len(top), stt.median(o) / M, sum(x > 0 for x in o), len(o)))
    # 전 기간(같은 날 집합을 다 가진 조합만) 최적
    for scope, ds in (("전 기간", days), ("흐름 7일", flow_days)):
        cand = [p for p in t if all(d in t[p] for d in ds)]
        if not cand:
            continue
        bp = max(cand, key=lambda p: sum(t[p][d][0] for d in ds))
        s = [t[bp][d][0] for d in ds]
        # 반분 교차: 전반 최적 → 후반 성과
        h = len(ds) // 2
        b1 = max(cand, key=lambda p: sum(t[p][d][0] for d in ds[:h]))
        b2 = max(cand, key=lambda p: sum(t[p][d][0] for d in ds[h:]))
        print("  [%s 최적 · %d일] %s\n      합 %+.1f만 · 일평균 %+.1f · 흑자일 %d/%d · 최악일 %+.1f · 9/30 %+.1f\n"
              "      반분 교차: 전반최적→후반 %+.1f만 (후반최적 %+.1f) · 후반최적→전반 %+.1f만 (전반최적 %+.1f)" % (
                  scope, len(ds), bp, sum(s) / M, stt.mean(s) / M, sum(x > 0 for x in s), len(s), min(s) / M,
                  t[bp].get(T, (0,))[0] / M,
                  sum(t[b1][d][0] for d in ds[h:]) / M, sum(t[b2][d][0] for d in ds[h:]) / M,
                  sum(t[b2][d][0] for d in ds[:h]) / M, sum(t[b1][d][0] for d in ds[:h]) / M))
