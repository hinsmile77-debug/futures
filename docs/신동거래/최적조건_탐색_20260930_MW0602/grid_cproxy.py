# -*- coding: utf-8 -*-
"""흐름 역추종(C) 계열을 **외국인 선물 순매수**(콜−풋의 장중 거울상)로 76일 전진 검증.
신호: 외국인 누적 순매수(09:00 이후 첫 수신값 대비 변화)가 −K 이하 → 매도, +K 이상 → 매수(순방향).
① 5일 겹침: 콜−풋 원본 C vs 대리 C 의 일별 손익 ② 76일 walk-forward(loop_wf 와 같은 정책)."""
import os, sys, json, sqlite3, itertools, collections, statistics as stt
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from load import load, ROOT
from sim import simulate, total
from grid import exits as _ex

RAW = os.path.join(ROOT, "data/db/raw_data.db")
inv = collections.defaultdict(dict)
for ts, f in sqlite3.connect(RAW).execute("select ts,fields from raw_investor_futures order by ts"):
    v = json.loads(f).get("foreign_net_qty")
    if v is not None:
        inv[ts[:10]][ts[11:16]] = v
days = [r[0] for r in sqlite3.connect(os.path.join(ROOT, "data/db/premarket_levels.db")).execute(
    "select distinct date from premarket_levels where stage='0850' order by date")] if os.path.exists(os.path.join(ROOT, "data/db/premarket_levels.db")) else []
if not days:
    from config.settings import PREMARKET_LEVELS_DB
    days = [r[0] for r in sqlite3.connect(PREMARKET_LEVELS_DB).execute("select distinct date from premarket_levels where stage='0850' order by date")]
days = [d for d in days if d in inv]

KS = (200, 400, 800, 1200, 1600, 2400, 3200)
STOPS = [None, 5, 8, 12]; TRAILS = [None, (4, 3), (6, 4), (6, 6), (8, 4), (8, 8), (12, 6)]; TPS = [None, 8, 12, 16, 20]
EX = [(s, tr, tp) for s, tr, tp in itertools.product(STOPS, TRAILS, TPS) if not (s is None and tr is None)]


def run_day(day, mode="foreign"):
    x = load(day)
    if x is None:
        return None
    d = x[0]
    if mode == "foreign":
        fl = inv[day]; ks = sorted(k for k in fl if k >= "09:00")
        if not ks:
            return None
        base = fl[ks[0]]
        def val(k):
            kk = [z for z in ks if z <= k]
            return (fl[kk[-1]] - base) if kk else None
        sgn = +1                       # 순방향(외국인이 팔면 매도)
    else:
        k0 = d.last_at_or_before("09:00"); base = d.sp.get(k0)
        if base is None:
            return None
        val = lambda k: (d.sp[k] - base) if k in d.sp else None
        sgn = -1                       # 역방향(개인이 콜을 사면 매도)
    out = {}
    for K, mt, fe in itertools.product(KS if mode == "foreign" else (100, 150, 200, 300, 400, 600, 800), (1, 3), (False, True)):
        def sig(k, st):
            v = val(k)
            if v is None: return 0
            return sgn * (1 if v >= K else (-1 if v <= -K else 0))
        def xs(k, side, st):
            v = val(k)
            return v is not None and sgn * v * -side >= K   # 반대 문턱
        for s, tr, tp in EX:
            trs = simulate(d, sig, stop=s, trail=tr, tp=tp, max_trades=mt, exit_sig=xs if fe else None)
            out[json.dumps(dict(K=K, mt=mt, fe=fe, stop=s, trail=tr, tp=tp))] = (total(trs), len(trs))
    return out


FD = ["2026-09-22", "2026-09-23", "2026-09-28", "2026-09-29", "2026-09-30"]
M = 1e4
print("① 5일 겹침 — 원본(콜−풋) C vs 대리(외국인 선물) C : 그날 최적 / 전 조합 중앙 / 흑자 비율")
orig = {d: run_day(d, "callput") for d in FD}
prox = {}
res = {}
for d in days:
    r = run_day(d, "foreign")
    if r: res[d] = r
for d in FD:
    o, p = orig[d], res.get(d)
    if not o or not p: continue
    ov, pv = [v[0] for v in o.values()], [v[0] for v in p.values()]
    print("  %s  원본: 최적 %+7.1f 중앙 %+7.1f 흑자 %3.0f%% | 대리: 최적 %+7.1f 중앙 %+7.1f 흑자 %3.0f%%" % (
        d, max(ov) / M, stt.median(ov) / M, 100 * sum(v > 0 for v in ov) / len(ov), max(pv) / M, stt.median(pv) / M, 100 * sum(v > 0 for v in pv) / len(pv)))

print("\n② 대리 C — %d일 walk-forward(훈련 최소 10일)" % len(res))
ds = sorted(res); cand = [p for p in res[ds[0]] if all(p in res[d] for d in ds)]
t = {p: {d: res[d][p][0] for d in ds} for p in cand}
test = ds[10:]
def stats(seq):
    cum = peak = mdd = 0.0
    for x in seq:
        cum += x; peak = max(peak, cum); mdd = min(mdd, cum - peak)
    return cum, sum(x > 0 for x in seq), len(seq), min(seq), mdd
for pol in ("daily", "hyst", "rank", "weekly"):
    seq = []; cur = None; sw = 0
    for i, d in enumerate(test):
        tr = ds[:10 + i]
        if pol == "rank":
            sc = collections.defaultdict(float)
            for dd in tr:
                for r, p in enumerate(sorted(cand, key=lambda p: t[p][dd])): sc[p] += r / len(cand)
        else:
            sc = {p: sum(t[p][dd] for dd in tr) for p in cand}
        best = max(cand, key=lambda p: sc[p])
        if pol == "hyst" and cur is not None and sc[best] <= max(sc[cur], 0) * 1.10: best = cur
        if pol == "weekly" and cur is not None and i % 5: best = cur
        sw += (best != cur); cur = best; seq.append(t[best][d])
    cum, w, n, worst, mdd = stats(seq)
    print("  %-7s 합 %+8.1f만 · 흑자일 %d/%d · 최악일 %+7.1f · MDD %+8.1f · 교체 %d%s" % (pol, cum / M, w, n, worst / M, mdd / M, sw, "" if pol != "daily" else "   ← 요청안"))
orc = max(cand, key=lambda p: sum(t[p][d] for d in test)); s = stats([t[orc][d] for d in test])
print("  oracle  합 %+8.1f만 · 흑자일 %d/%d · 최악일 %+7.1f · MDD %+8.1f  (사후 최적 고정 · 도달 불가)  %s" % (s[0] / M, s[1], s[2], s[3] / M, s[4] / M, orc))
print("  random  합 %+8.1f만 (무작위 조합 중앙값)" % (stt.median(sum(t[p][d] for d in test) for p in cand) / M))
# 전반/후반
h = len(ds) // 2
b1 = max(cand, key=lambda p: sum(t[p][d] for d in ds[:h])); b2 = max(cand, key=lambda p: sum(t[p][d] for d in ds[h:]))
print("  반분 교차: 전반최적→후반 %+.1f만 (후반최적 %+.1f) · 후반최적→전반 %+.1f만 (전반최적 %+.1f)" % (
    sum(t[b1][d] for d in ds[h:]) / M, sum(t[b2][d] for d in ds[h:]) / M, sum(t[b2][d] for d in ds[:h]) / M, sum(t[b1][d] for d in ds[:h]) / M))
