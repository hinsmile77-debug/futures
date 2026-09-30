# -*- coding: utf-8 -*-
"""9/30 하루 최적 진입·청산 탐색 — 5개 규칙 계열 × 격자.  python <this> [YYYY-MM-DD]
출력: 같은 폴더 grid_<date>.json (계열별 전 조합 손익 · 약 17MB — 커밋하지 말 것)."""
import itertools, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from load import load
from sim import simulate, total

DAY = sys.argv[1] if len(sys.argv) > 1 else "2026-09-30"

STOPS = [None, 3, 5, 8, 12, 20]
TRAILS = [None] + [(a, b) for a in (4, 6, 8, 12) for b in (2, 3, 4, 6, 8) if b <= a]
TPS = [None, 8, 12, 16, 20, 25]


def r1_bias(d):
    k = d.last_at_or_before("08:59")
    sp = d.sp.get(k) if k else None
    if sp is None:
        return None
    return -1 if sp >= 50 else (1 if sp <= -50 else 0)


def exits():
    for s, tr, tp in itertools.product(STOPS, TRAILS, TPS):
        if s is None and tr is None:
            continue                      # 손절 없는 무방비 조합은 뺀다
        yield s, tr, tp


def fam_A(d, bias):
    """방향 고정(R1) · 시각 T 진입 · 1회."""
    if not bias:
        return
    times = [k for k in d.idx if "09:00" <= k <= "11:30" and k[-1] in "05"]
    for T in times:
        sig = (lambda T: lambda k, st: bias if k == T else 0)(T)
        for s, tr, tp in exits():
            yield dict(T=T, stop=s, trail=tr, tp=tp), simulate(d, sig, stop=s, trail=tr, tp=tp, max_trades=1)


def fam_B(d, bias):
    """개장 범위(OR) 돌파. filt: none | r1."""
    for N, filt, mt, stopmode in itertools.product((5, 10, 15, 30, 45, 60), ("none", "r1"), (1, 3), ("or", 5, 8, 12)):
        if filt == "r1" and not bias:
            continue
        ks = [k for k in d.idx if "09:00" <= k and k in d.c][:N]
        if len(ks) < N:
            continue
        hi, lo, end = max(d.h[k] for k in ks), min(d.l[k] for k in ks), ks[-1]

        def sig(k, st, hi=hi, lo=lo, end=end, filt=filt):
            if k <= end:
                return 0
            c = d.c[k]
            sd = -1 if c < lo else (1 if c > hi else 0)
            if filt == "r1" and sd != bias:
                return 0
            return sd
        sfn = (lambda k, side, e, hi=hi, lo=lo: hi if side < 0 else lo) if stopmode == "or" else None
        for _s, tr, tp in exits():
            if _s is not None:
                continue                   # 손절은 stopmode 가 정한다
            yield (dict(N=N, filt=filt, max_trades=mt, stop=stopmode, trail=tr, tp=tp),
                   simulate(d, sig, stop=None if stopmode == "or" else stopmode, stop_fn=sfn,
                            trail=tr, tp=tp, max_trades=mt))


def fam_C(d, bias):
    """개인 위클리 콜−풋 누적(09:00 기준 변화)의 역방향 — 콜 순매수↑ → 매도."""
    k0 = d.last_at_or_before("09:00")
    sp0 = d.sp.get(k0) if k0 else None
    if sp0 is None:
        return
    for K, mt, flip_exit in itertools.product((100, 150, 200, 300, 400, 600, 800), (1, 3), (False, True)):
        def sig(k, st, K=K):
            v = d.sp.get(k)
            if v is None:
                return 0
            dv = v - sp0
            return -1 if dv >= K else (1 if dv <= -K else 0)

        def xs(k, side, st, K=K):
            v = d.sp.get(k)
            return v is not None and side * (v - sp0) >= K     # 흐름이 반대편 문턱을 넘으면 청산
        for s, tr, tp in exits():
            yield (dict(K=K, max_trades=mt, flip_exit=flip_exit, stop=s, trail=tr, tp=tp),
                   simulate(d, sig, stop=s, trail=tr, tp=tp, max_trades=mt,
                            exit_sig=xs if flip_exit else None))


def fam_D(d, bias, L):
    """구조맥점 이탈(돌파 추종) — 종가가 맥점을 새로 넘으면 그 방향. 손절 = 맥점 ∓ b."""
    from strategy.shindong import engine as E
    for filt, b, mt in itertools.product(("none", "r1"), (1, 2, 3, 5), (1, 3, 5)):
        if filt == "r1" and not bias:
            continue

        def sig(k, st, filt=filt):
            _, lv = E.levels_at(L, k)
            prev = st.get("prev")
            c = d.c[k]
            st["prev"] = c
            if prev is None:
                return 0
            for x in lv:
                sd = -1 if (prev >= x > c) else (1 if (prev <= x < c) else 0)
                if sd and (filt == "none" or sd == bias):
                    st["lvl"] = x
                    return sd
            return 0
        for _s, tr, tp in exits():
            if _s is not None:
                continue
            st = {}

            def sig2(k, _st, sig=sig, st=st):
                return sig(k, st)

            def sfn2(k, side, e, st=st, b=b):
                return st["lvl"] + b if side < 0 else st["lvl"] - b
            yield (dict(filt=filt, b=b, max_trades=mt, trail=tr, tp=tp),
                   simulate(d, sig2, stop_fn=sfn2, trail=tr, tp=tp, max_trades=mt))


def ema(vals, n):
    a, out, m = 2.0 / (n + 1), [], None
    for v in vals:
        m = v if m is None else m + a * (v - m)
        out.append(m)
    return out


def fam_E(d, bias):
    """EMA 교차 추세 — 교차 시 그 방향 진입, 반대 교차 시 청산(또는 손절·트레일)."""
    ks = [k for k in d.idx if k in d.c]
    cl = [d.c[k] for k in ks]
    for (f, s_), filt, mt in itertools.product(((5, 20), (10, 30), (20, 60), (5, 60)), ("none", "r1"), (1, 3, 99)):
        if filt == "r1" and not bias:
            continue
        ef, es = ema(cl, f), ema(cl, s_)
        rel = {k: (1 if ef[i] > es[i] else -1) for i, k in enumerate(ks) if i >= s_}
        prevk = {k: ks[i - 1] for i, k in enumerate(ks) if i}

        def sig(k, st, filt=filt):
            r, p = rel.get(k), rel.get(prevk.get(k))
            if r is None or p is None or r == p:
                return 0
            return r if (filt == "none" or r == bias) else 0

        def xs(k, side, st):
            r = rel.get(k)
            return r is not None and r != side
        for s, tr, tp in exits():
            yield (dict(ema=(f, s_), filt=filt, max_trades=mt, stop=s, trail=tr, tp=tp),
                   simulate(d, sig, stop=s, trail=tr, tp=tp, max_trades=mt, exit_sig=xs))


def run(day):
    x = load(day)
    if x is None:
        return None
    d, L, _ = x
    bias = r1_bias(d)
    out = {"day": day, "bias": bias, "fam": {}}
    for name, gen in (("A", fam_A(d, bias)), ("B", fam_B(d, bias)), ("C", fam_C(d, bias)),
                      ("D", fam_D(d, bias, L)), ("E", fam_E(d, bias))):
        rows = []
        for p, trs in gen:
            rows.append(dict(p=p, net=total(trs), n=len(trs), w=sum(t["net"] > 0 for t in trs),
                             trades=[[t["side"], t["et"], round(t["e"], 2), t["xt"], round(t["x"], 2), t["why"], round(t["net"])] for t in trs]))
        out["fam"][name] = rows
    return out


if __name__ == "__main__":
    r = run(DAY)
    json.dump(r, open(os.path.join(HERE, "grid_%s.json" % DAY.replace("-", "")), "w", encoding="utf-8"),
              ensure_ascii=False, default=str)
    for f, rows in r["fam"].items():
        rows.sort(key=lambda z: -z["net"])
        print(f, len(rows), "best %+.1f만" % (rows[0]["net"] / 1e4) if rows else "-")
        for z in rows[:3]:
            print("   %+.1f만 n=%d w=%d %s %s" % (z["net"] / 1e4, z["n"], z["w"], z["p"], z["trades"]))
