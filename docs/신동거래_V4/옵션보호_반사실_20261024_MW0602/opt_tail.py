# -*- coding: utf-8 -*-
"""재난손절 도달 뒤 동결 — 장기 1분봉 꼬리 스트레스. 읽기 전용(DB 미기록).

regular_candles code 10100(KOSPI200 선물 연속, 2024-07~) 의 정규장 분봉으로 가상 진입을 깐다:
  매 거래일 09:30·10:00·…·14:30, 매수·매도 양쪽, 재난손절 = 진입가 ∓ 0.6×ATR14(일봉 TR 14일 평균, 직전일까지)
재난손절에 닿으면 그 분부터 동결 — 청산은 동결이 풀리는 분의 종가:
  F113  113분 뒤(10/15 실측 청산 거부 지속) 또는 15:05 중 이른 쪽
  FEOD  15:05
비교(pt → ATR 배수):
  naked   선물 단독
  put     월물 보호옵션(K = 재난손절, 잔존 18영업일) — IV = ATR/F/1.596×√252 (Parkinson; 10/21 검산 47.5% vs VKOSPI 48.6%),
          동결 해제 시점 IV 는 진입 IV 와 같다고 둔다(급락 시 IV 상승 = 보호 쪽 유리를 뺀 보수 가정). 호가 0.15×2.
  cut     같은 델타만큼 수량 축소 (1 − |δ진입|)
"""
import os, sys, math, sqlite3
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while not os.path.isdir(os.path.join(ROOT, "data")):
    ROOT = os.path.dirname(ROOT)
os.chdir(ROOT)


def N(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def b76(F, K, s, T, cp):
    if T <= 0:
        return max(0.0, (F - K) if cp == "C" else (K - F))
    sd = s * math.sqrt(T); d1 = (math.log(F / K) + 0.5 * sd * sd) / sd; d2 = d1 - sd
    return F * N(d1) - K * N(d2) if cp == "C" else K * N(-d2) - F * N(-d1)


def dlt(F, K, s, T, cp):
    sd = s * math.sqrt(T); d1 = (math.log(F / K) + 0.5 * sd * sd) / sd
    return N(d1) if cp == "C" else N(d1) - 1


c = sqlite3.connect("file:data/db/regular_candles.db?mode=ro", uri=True)
rolls = {r[0] for r in c.execute("select trade_date from roll_days")}
bars = {}
for ts, o, h, l, cl in c.execute("select ts, open, high, low, close from regular_candles where code='10100' "
                                 "and substr(ts,12,5) between '09:00' and '15:05' order by ts"):
    bars.setdefault(ts[:10], []).append((ts[11:16], h, l, cl))
days = sorted(bars)
tr, atr = [], {}
pc = None
for d in days:
    hs = [b[1] for b in bars[d]]; ls = [b[2] for b in bars[d]]
    H, L = max(hs), min(ls)
    if len(tr) >= 14:
        atr[d] = sum(tr[-14:]) / 14
    t = H - L if (pc is None or d in rolls) else max(H - L, abs(H - pc), abs(L - pc))
    tr.append(t); pc = bars[d][-1][3]

T0 = 18 / 252.0
ENTRY = ["%02d:%02d" % (h, m) for h in range(9, 15) for m in (0, 30) if "09:30" <= "%02d:%02d" % (h, m) <= "14:30"]
ev = []
n_entry = 0
for d in days:
    if d not in atr or len(bars[d]) < 300:
        continue
    A = atr[d]; bs = bars[d]; ix = {b[0]: i for i, b in enumerate(bs)}
    for t in ENTRY:
        if t not in ix:
            continue
        i0 = ix[t]; e = bs[i0][3]
        iv = A / e / 1.596 * math.sqrt(252)
        for side in (1, -1):
            n_entry += 1
            stop = e - side * 0.6 * A
            cp = "P" if side > 0 else "C"
            K = round(stop / 2.5) * 2.5
            v0 = b76(e, K, iv, T0, cp); d0 = abs(dlt(e, K, iv, T0, cp))
            hit = None
            for j in range(i0 + 1, len(bs)):
                if (bs[j][2] <= stop) if side > 0 else (bs[j][1] >= stop):
                    hit = j; break
            if hit is None:
                continue
            res = {}
            for lab, n in (("F113", 113), ("FEOD", 10 ** 6)):
                j1 = min(hit + n, len(bs) - 1)
                x = bs[j1][3]
                # 동결 구간 최악 평가
                worst = min(side * ((bs[k][2] if side > 0 else bs[k][1]) - e) for k in range(hit, j1 + 1))
                Tm = T0 - (j1 - i0) / 405.0 / 252
                fut = side * (x - e)
                opt = b76(x, K, iv, Tm, cp) - v0 - 0.30
                res[lab] = dict(naked=fut / A, put=(fut + opt) / A, cut=fut * (1 - d0) / A, worst=worst / A)
            ev.append(dict(d=d, t=t, side=side, A=A, d0=d0, prem=v0 / A, **res))


def q(xs, p):
    xs = sorted(xs); return xs[min(len(xs) - 1, int(p * len(xs)))]


out = []
P = out.append
P("# 재난손절 도달 뒤 동결 — 장기 꼬리 (%s ~ %s · %d거래일)" % (min(atr), max(atr), len(atr)))
P("가상 진입 %d건 중 재난손절 도달 %d건 (%.1f%%) · 진입 |δ| 중앙 %.2f · 프리미엄 중앙 %.2f×ATR" % (
    n_entry, len(ev), 100.0 * len(ev) / n_entry, q([x["d0"] for x in ev], .5), q([x["prem"] for x in ev], .5)))
for lab, name in (("F113", "113분 동결"), ("FEOD", "15:05 까지 동결")):
    P("\n## %s — 동결 해제 시 손익 (×ATR, 진입가 기준. 재난손절 정상 집행 = −0.60)" % name)
    P("| 분위 | 선물 단독 | 보호옵션 | 같은 델타 수량축소 | 동결 중 최악 평가(단독) |")
    P("|---|---|---|---|---|")
    for pp, nm in ((.5, "중앙"), (.1, "하위 10%"), (.05, "하위 5%"), (.01, "하위 1%"), (0.0, "최악")):
        P("| %s | %.2f | %.2f | %.2f | %.2f |" % (nm, q([x[lab]["naked"] for x in ev], pp), q([x[lab]["put"] for x in ev], pp),
                                                q([x[lab]["cut"] for x in ev], pp), q([x[lab]["worst"] for x in ev], pp)))
    over = [x for x in ev if x[lab]["naked"] < -1.2]
    P("- 단독 손실이 재난손절의 2배(−1.2×ATR)를 넘은 경우: %d건 (%.2f%%) · %d일" % (len(over), 100.0 * len(over) / len(ev), len({x["d"] for x in over})))
    win = [x for x in ev if x[lab]["put"] > x[lab]["cut"]]
    P("- 보호옵션이 수량축소보다 나은 경우: %d건 (%.1f%%) — 평균 차이 %+.3f×ATR (전체 평균 %+.3f×ATR)" % (
        len(win), 100.0 * len(win) / len(ev), sum(x[lab]["put"] - x[lab]["cut"] for x in win) / max(1, len(win)),
        sum(x[lab]["put"] - x[lab]["cut"] for x in ev) / len(ev)))
    P("- 기대값(재난손절 도달 사건 1건당): 단독 %+.3f · 보호 %+.3f · 수량축소 %+.3f ×ATR" % (
        sum(x[lab]["naked"] for x in ev) / len(ev), sum(x[lab]["put"] for x in ev) / len(ev), sum(x[lab]["cut"] for x in ev) / len(ev)))
    worst = sorted(ev, key=lambda x: x[lab]["naked"])[:6]
    P("- 최악 6건: " + " · ".join("%s %s %s 단독 %.2f / 보호 %.2f / 축소 %.2f" % (
        x["d"], x["t"], "매수" if x["side"] > 0 else "매도", x[lab]["naked"], x[lab]["put"], x[lab]["cut"]) for x in worst))
open(os.path.join(HERE, "out_opt_tail.txt"), "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(out))
