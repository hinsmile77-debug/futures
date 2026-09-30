# -*- coding: utf-8 -*-
"""「매일 재최적화 → 다음날 적용」 루프 자체를 과거에 돌려 본다(전진 검증).
입력: grid_all.json(grid_all.py 산출 · scratchpad).  python loop_wf.py <grid_all.json 경로>
정책: daily(매일 재선택) · hyst(10% 이상 나아야 교체) · top20(상위 20 조합 평균 = 분산 투자) ·
      rank(일별 순위 합으로 선택 — 큰 하루에 덜 휘둘림) · weekly(5거래일마다 재선택) · roll20(최근 20일 창)."""
import json, sys, collections, statistics as stt
G = json.load(open(sys.argv[1], encoding="utf-8"))
M = 1e4
days = sorted(G)


def table(fam, filt=None):
    t = collections.defaultdict(dict)
    for d in days:
        for p, net, n in G[d]["fam"].get(fam, []):
            if filt and json.loads(p).get("filt") != filt:
                continue
            t[p][d] = net
    return t


def stats(seq):
    cum = peak = mdd = 0.0
    for x in seq:
        cum += x
        peak = max(peak, cum)
        mdd = min(mdd, cum - peak)
    return cum, sum(x > 0 for x in seq), len(seq), min(seq) if seq else 0, mdd


def run(fam, filt=None, min_train=10, label=None):
    t = table(fam, filt)
    ds = [d for d in days if any(d in t[p] for p in t)]
    cand = [p for p in t if all(d in t[p] for d in ds)]
    if len(ds) <= min_train or not cand:
        return
    test = ds[min_train:]
    res = collections.OrderedDict()
    inc = None; inc_score = None
    rank_cache = {}
    week_p = None
    for pol in ("daily", "hyst", "top20", "rank", "weekly", "roll20"):
        seq = []; switches = 0; cur = None
        for i, d in enumerate(test):
            tr = ds[:min_train + i]
            if pol == "roll20":
                tr = tr[-20:]
            if pol == "rank":
                sc = collections.defaultdict(float)
                for dd in tr:
                    order = sorted(cand, key=lambda p: t[p][dd])
                    for r, p in enumerate(order):
                        sc[p] += r / len(cand)
                best = max(cand, key=lambda p: sc[p])
                seq.append(t[best][d]); switches += (best != cur); cur = best; continue
            score = {p: sum(t[p][dd] for dd in tr) for p in cand}
            best = max(cand, key=lambda p: score[p])
            if pol == "top20":
                top = sorted(cand, key=lambda p: -score[p])[:20]
                seq.append(stt.mean(t[p][d] for p in top)); continue
            if pol == "hyst":
                if cur is None or score[best] > max(score[cur], 0) * 1.10 + 1e-9:
                    cur = best
                best = cur
            if pol == "weekly":
                if i % 5 == 0 or cur is None:
                    cur = best
                best = cur
            seq.append(t[best][d]); switches += (best != cur) if pol == "daily" else 0
            if pol == "daily":
                cur = best
        res[pol] = (stats(seq), switches)
    # 기준선: 사후 최적 고정(오라클) · 무작위 조합 중앙
    oracle = max(cand, key=lambda p: sum(t[p][d] for d in test))
    orc = stats([t[oracle][d] for d in test])
    rnd = stt.median(sum(t[p][d] for d in test) for p in cand)
    print("\n== %s  훈련 최소 %d일 · 시험 %d일(%s~%s) · 조합 %d" % (label or fam, min_train, len(test), test[0], test[-1], len(cand)))
    print("   %-8s %10s %8s %9s %10s %6s" % ("정책", "합(만)", "흑자일", "최악일", "MDD", "교체"))
    for pol, ((cum, w, n, worst, mdd), sw) in res.items():
        print("   %-8s %+10.1f %5d/%-3d %+9.1f %+10.1f %6s" % (pol, cum / M, w, n, worst / M, mdd / M, sw if pol in ("daily", "hyst", "rank") else "-"))
    print("   %-8s %+10.1f %5d/%-3d %+9.1f %+10.1f   (사후 최적 고정 — 도달 불가 상한)" % ("oracle", orc[0] / M, orc[1], orc[2], orc[3] / M, orc[4] / M))
    print("   %-8s %+10.1f   (무작위 조합 중앙값)" % ("random", rnd / M))


for fam in "BDE":
    run(fam, min_train=10)
run("D", filt="none", min_train=10, label="D(필터 없음)")
print("\n########## 흐름 6일(개인 콜−풋) — 훈련 최소 2일")
for fam, filt in (("C", None), ("D", "r1"), ("A", None), ("B", "r1")):
    run(fam, filt=filt, min_train=2, label="%s%s" % (fam, "(" + filt + ")" if filt else ""))
