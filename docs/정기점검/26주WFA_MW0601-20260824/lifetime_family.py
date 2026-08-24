# -*- coding: utf-8 -*-
"""[MW0601] 계열별 호라이즌 프로파일 — 수명이 아니라 '무엇을 재는 피처인가'로 갈리는가.

lifetime_core.py에서 나온 관찰:
   CORE 6종(vwap/cvd/ofi 계열)은 **전부 h=30에서 최강**인데,
   수급 피처(foreign_futures_net 등)는 h=1~5에서 최강이고 h=30에서 약해진다.

수명(tau)으로는 호라이즌이 갈리지 않았다(형태 상관 p=0.43). 그렇다면 갈리는 축은
'얼마나 오래 기억하는가'가 아니라 '무엇을 재는가'일 수 있다. 이걸 검정한다.

주의 — 이 분석은 사후 관찰에서 출발했다(사전등록 아님). 따라서:
  · 계열 정의는 피처명 규칙으로 **기계적으로** 하고 임의 조정하지 않는다.
  · 계열 간 프로파일 차이는 순열검정(계열 라벨 셔플)으로 유의성을 잰다.
  · 결론은 '가설 생성'까지다. 확정은 다음 26주 창의 사전등록 재현이 필요하다.
"""
from __future__ import print_function
import io
import json
import math
import re
import sys

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")

IC_HZ = [1, 3, 5, 10, 15, 30]
CLOCK = {"time_cos", "time_sin"}

FAMILY = [
    ("수급(투자자)", r"^(foreign|institution|retail|individual|program|quality_investor)"),
    ("옵션", r"^(opt_|vkospi|rv_iv)"),
    ("매크로", r"^macro_"),
    ("기술(가격/거래량)", r"^(vwap|cvd|ema|atr|realized_vol|avg_volume|volume_|ret_|price_|"
                    r"hurst|va_|poc|value_area|bb_|rsi|macd|momentum)"),
    ("미시구조", r"^(ofi|spread|queue|vpin|microprice|toxicity|depth|imbalance|tick)"),
]


def fam_of(nm):
    for lab, pat in FAMILY:
        if re.match(pat, nm):
            return lab
    return "기타"


def spearman(a, b):
    from scipy.stats import rankdata
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 3:
        return float("nan")
    ra, rb = rankdata(a[ok]), rankdata(b[ok])
    ra, rb = ra - ra.mean(), rb - rb.mean()
    d = math.sqrt(float(np.dot(ra, ra)) * float(np.dot(rb, rb)))
    return float(np.dot(ra, rb)) / d if d > 0 else float("nan")


def main():
    L = io.StringIO()

    def P(*a):
        s = " ".join(str(x) for x in a)
        print(s)
        L.write(s + "\n")

    cross = json.load(open("lifetime_cross.json", encoding="utf-8"))
    IC = cross["ic"]
    robust = json.load(open("lifetime_robust.json", encoding="utf-8"))
    life = json.load(open("lifetime_raw.json", encoding="utf-8"))["result"]
    bad = {z["nm"] for z in robust["asym"] if z["asym"] and z["asym"] > 0.30}

    names = [n for n in IC["1"] if n not in CLOCK and n not in bad]
    P("=" * 108)
    P("[MW0601] 계열별 호라이즌 프로파일 — 순수 라이브 %d거래일" % cross["n_days"])
    P("=" * 108)
    P("대상 %d피처 (시계·단조 제외) · 계열은 피처명 규칙으로 기계 분류" % len(names))
    P("⚠ 사후 관찰에서 출발한 가설 생성용 분석이다. 사전등록 검정이 아니다.")

    # 피처별 IC 프로파일
    # [버그수정] None뿐 아니라 NaN도 제외한다. macro_* 4종은 동률 99.7~99.9%라
    # analyze()가 unique<3으로 NaN을 돌려주는데, 이걸 남기면 계열 평균이 NaN이 되고
    # 순열검정의 분산 비교(nan >= obs_var)가 항상 False가 되어 p가 0에 붙는다.
    prof, nan_drop = {}, []
    for n in names:
        ts = [IC[str(h)].get(n, {}).get("t") for h in IC_HZ]
        if any(t is None or not np.isfinite(t) for t in ts):
            nan_drop.append(n)
            continue
        prof[n] = [abs(t) for t in ts]
    if nan_drop:
        P("\n[제외] IC 산출 불가 %d개 (동률 과다로 일자별 순위상관 정의 안 됨):"
          % len(nan_drop))
        for n in nan_drop:
            tie = (life.get(n) or {}).get("tie")
            P("   %-28s 동률 %.1f%%" % (n[:28], (tie or 0) * 100))

    groups = {}
    for n in prof:
        groups.setdefault(fam_of(n), []).append(n)

    P("\n%-20s %4s %s %9s %9s" % ("계열", "n", " ".join("%8s" % ("h=%d" % h) for h in IC_HZ),
                                  "기울기", "최강h"))
    P("-" * 108)
    fam_slope = {}
    rows = []
    for lab in [f[0] for f in FAMILY] + ["기타"]:
        ns = groups.get(lab) or []
        if len(ns) < 3:
            continue
        M = np.array([prof[n] for n in ns], float)
        mu = M.mean(axis=0)
        sl = spearman(IC_HZ, mu)
        fam_slope[lab] = sl
        b = int(np.argmax(mu))
        rows.append((lab, len(ns), mu, sl, IC_HZ[b]))
        P("%-20s %4d %s %9.3f %9d"
          % (lab, len(ns), " ".join("%8.3f" % x for x in mu), sl, IC_HZ[b]))

    # 정규화 형태
    P("\n[형태만 — 각 계열을 자기 평균으로 정규화]")
    P("%-20s %s %9s" % ("계열", " ".join("%8s" % ("h=%d" % h) for h in IC_HZ), "변동폭"))
    P("-" * 108)
    shapes = {}
    for lab, n, mu, sl, bh in rows:
        s = mu / mu.mean()
        shapes[lab] = s
        P("%-20s %s %9.3f" % (lab, " ".join("%8.3f" % x for x in s), s.max() - s.min()))

    # 순열검정 — 계열 라벨을 섞어도 이만한 기울기 분산이 나오는가
    P("\n[순열검정] 계열 라벨을 무작위로 섞어 '계열 간 기울기 분산'을 재현한다")
    labs = [l for l, _n, _m, _s, _b in rows]
    sizes = [n for _l, n, _m, _s, _b in rows]
    obs_slopes = [fam_slope[l] for l in labs]
    if not all(np.isfinite(s) for s in obs_slopes):
        P("   [중단] 계열 기울기에 NaN이 남아 있다 — 순열검정을 하지 않는다.")
        p, obs_var = float("nan"), float("nan")
    else:
        obs_var = float(np.var(obs_slopes))
        allp = [prof[n] for n in prof]
        rng = np.random.RandomState(20260824)
        cnt, N, bad_draw = 0, 20000, 0
        for _ in range(N):
            idx = rng.permutation(len(allp))
            pos, sls = 0, []
            for sz in sizes:
                sub = np.array([allp[i] for i in idx[pos:pos + sz]], float)
                pos += sz
                sls.append(spearman(IC_HZ, sub.mean(axis=0)))
            if not all(np.isfinite(s) for s in sls):
                bad_draw += 1
                continue
            if float(np.var(sls)) >= obs_var - 1e-15:
                cnt += 1
        eff = N - bad_draw
        p = (cnt + 1.0) / (eff + 1.0)
        P("   관측 기울기 분산 = %.4f · 순열 %d회(무효 %d 제외) · p = %.4f -> %s"
          % (obs_var, eff, bad_draw, p,
             "계열 간 차이 유의" if p < 0.05 else "계열 간 차이 무의미"))

    # 계열별 수명
    P("\n[참고] 계열별 수명(tau) 중앙값 — 수명과 계열은 별개 축인가")
    for lab, n, _m, sl, bh in rows:
        tv = [life[x]["tau"] for x in groups[lab]
              if x in life and life[x].get("tau") is not None]
        P("   %-20s n=%2d  tau중앙값 %5.1f분  기울기 %+.3f  최강h=%d"
          % (lab, n, np.median(tv) if tv else float("nan"), sl, bh))

    # 대표 피처
    P("\n[계열별 대표 피처 — |t| 상위 3]")
    for lab, _n, _m, _s, _b in rows:
        ns = sorted(groups[lab], key=lambda x: -max(prof[x]))[:3]
        P("   %-20s %s" % (lab, ", ".join(
            "%s(최강h=%d,|t|=%.1f)" % (x[:24], IC_HZ[int(np.argmax(prof[x]))], max(prof[x]))
            for x in ns)))

    P("\n" + "=" * 108)
    P("[해석 한계]")
    P("  · 사후 관찰 기반이다. 계열 정의를 바꾸면 결과가 달라질 수 있다(연구자 자유도).")
    P("  · 같은 창에서 L2(비용차감 거래성) 합격 셀은 0이었다 — 통계적 분리가 곧")
    P("    수익으로 이어진다는 뜻이 아니다.")
    P("  · 확정하려면 다음 26주 창에서 **사전등록**으로 재현해야 한다.")
    P("=" * 108)

    json.dump(dict(family={l: dict(n=int(n), mean_absT=[float(x) for x in m],
                                   slope=float(s), best_h=int(b))
                           for l, n, m, s, b in rows},
                   shapes={l: [float(x) for x in v] for l, v in shapes.items()},
                   perm_p=float(p), obs_var=obs_var),
              open("lifetime_family.json", "w", encoding="utf-8"), ensure_ascii=False)
    with open("lifetime_family.txt", "w", encoding="utf-8") as f:
        f.write(L.getvalue())
    P("\n저장 -> lifetime_family.txt / .json")


if __name__ == "__main__":
    main()
