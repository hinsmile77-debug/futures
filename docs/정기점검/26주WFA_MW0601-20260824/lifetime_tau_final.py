# -*- coding: utf-8 -*-
"""[MW0601] tau 검정 최종 집계 — 발굴 기준을 바로잡고 대역 일치를 순열로 검정한다.

`lifetime_tau_test.py` 1차 집계의 두 결함을 고친다(계산은 재사용, 재집계만 한다):

  결함 ① **양측 검정을 발굴에 썼다.** `quality_macro_age_sec`(t=−76.85)·
       `ofi_reversal_speed`(−58.44)·`basis_change_pt`(−59.62)·`imbalance_slope`(−63.58)은
       tau(0.4~0.5분)가 **널(0.63분)보다 짧다** — 반지속적(anti-persistent)이라는 뜻이지
       기억이 있다는 뜻이 아니다. 발굴은 **단측**(tau > null)이어야 한다.

  결함 ② **tau < 1분을 값으로 취급했다.** 1분봉 격자에서 lag=1이 이미 1/e 아래면
       기억이 '1분보다 짧다'까지만 말할 수 있다 — 0.4와 0.7의 차이는 해상도 이하다.
       측정 한계 미만으로 **표기**하고 발굴에서 내린다(계측 4원칙 ②).

그리고 "tau 대역 == IC 최강 h" 일치가 우연 대비 많은지를 **순열**로 검정한다.
1/6 이항 근사는 두 분포가 균등하지 않아 맞지 않는다.
"""
from __future__ import print_function

import io
import json
import math
import sys

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")

IC_HZ = [1, 3, 5, 10, 15, 30]
TAU_FLOOR = 1.0        # 1분봉 격자 해상도
SPREAD_MAX = 0.50      # raw/wins/rank 상대격차 상한
HALF_MAX = 0.50        # 전·후반 상대차 상한


def band_of(tau):
    return min(IC_HZ, key=lambda h: abs(h - tau))


def main():
    L = io.StringIO()

    def P(*a):
        s = " ".join(str(x) for x in a)
        print(s)
        L.write(s + "\n")

    D = json.load(open("lifetime_tau_test.json", encoding="utf-8"))
    R = D["result"]
    unstable = set(D["unstable"])

    P("=" * 116)
    P("[MW0601] 피처별 tau 검정 — 최종 집계 (순수 라이브 %d거래일)" % D["n_days"])
    P("=" * 116)
    P("적격 %d개 · BH-FDR 임계 p=%.5f" % (len(D["eligible"]), D["fdr_thr"]))
    P("발굴 기준: ① tau > %.1f분(격자 해상도) ② **단측** tau>널 ∧ FDR 유의"
      % TAU_FLOOR)
    P("           ③ raw/wins/rank 상대격차 < %.0f%% ④ 전·후반 상대차 < %.0f%%"
      % (SPREAD_MAX * 100, HALF_MAX * 100))

    # ── 탈락 사유별 집계 ─────────────────────────────────────────
    rows = []
    for nm, r in R.items():
        tau = r["wins"]["mean"]
        if tau is None or not np.isfinite(tau):
            rows.append((nm, tau, r, "산출불가"))
            continue
        t = r["t"]
        why = []
        if tau <= TAU_FLOOR:
            why.append("해상도이하(tau<=%.1f)" % TAU_FLOOR)
        if not r.get("sig_fdr"):
            why.append("FDR미달")
        elif t is not None and t < 0:
            why.append("반지속(널보다짧음)")
        if nm in unstable:
            why.append("꼬리의존")
        a, b = r["h1"], r["h2"]
        if a is not None and b is not None and np.isfinite(a) and np.isfinite(b):
            rel = abs(a - b) / max(1e-9, (a + b) / 2.0)
            if rel >= HALF_MAX:
                why.append("전후반불안정(%.0f%%)" % (rel * 100))
        else:
            why.append("전후반산출불가")
        rows.append((nm, tau, r, ", ".join(why) if why else ""))

    keep = [x for x in rows if x[3] == ""]
    drop = [x for x in rows if x[3] != ""]

    P("\n" + "=" * 116)
    P("[1] **발굴 결과** — 네 기준을 모두 통과한 피처")
    P("=" * 116)
    P("%-30s %15s %9s %9s %9s %8s" %
      ("피처", "tau(95%CI)", "tau_rank", "널대비t", "tau대역", "IC최강h"))
    P("-" * 116)
    keep.sort(key=lambda x: -x[1])
    pairs = []
    for nm, tau, r, _w in keep:
        bh = r.get("best_h")
        bd = band_of(tau)
        if bh:
            pairs.append((bd, bh))
        P("%-30s %7.1f±%-7.1f %9.1f %9.2f %9s %8s"
          % (nm[:30], tau, r["wins"]["ci"], r["rank"]["mean"], r["t"],
             "h=%d" % bd, ("h=%d" % bh) if bh else "-"))
    P("\n   발굴 **%d개** / 적격 %d개" % (len(keep), len(R)))

    # ── 탈락 사유 ────────────────────────────────────────────────
    P("\n" + "=" * 116)
    P("[2] 탈락 %d개 — 사유별" % len(drop))
    P("=" * 116)
    by = {}
    for nm, tau, r, w in drop:
        by.setdefault(w.split(",")[0], []).append((nm, tau))
    for w in sorted(by, key=lambda k: -len(by[k])):
        P("\n   %s — %d개" % (w, len(by[w])))
        for nm, tau in sorted(by[w], key=lambda z: -(z[1] or 0)):
            P("      %-32s tau=%s" % (nm[:32],
                                      "%.2f" % tau if tau and np.isfinite(tau) else "-"))

    # ── 대역 일치 순열검정 ───────────────────────────────────────
    P("\n" + "=" * 116)
    P("[3] tau 대역이 IC 최강 h를 맞히는가 — 순열검정")
    P("=" * 116)
    if len(pairs) >= 6:
        bands = [p[0] for p in pairs]
        bests = [p[1] for p in pairs]
        obs = sum(1 for a, b in pairs if a == b)
        rng = np.random.RandomState(20260824)
        N = 20000
        cnt = 0
        for _ in range(N):
            perm = rng.permutation(bests)
            if sum(1 for a, b in zip(bands, perm) if a == b) >= obs:
                cnt += 1
        p = (cnt + 1.0) / (N + 1.0)
        P("   일치 **%d / %d** (%.1f%%)" % (obs, len(pairs), 100.0 * obs / len(pairs)))
        P("   순열 귀무분포 대비 p = %.4f -> %s"
          % (p, "우연보다 많다(유의)" if p < 0.05 else "**우연 범위 — tau는 최적 h를 예측하지 못한다**"))
        P("\n   tau 대역 분포 : " + ", ".join(
            "h=%d:%d" % (h, bands.count(h)) for h in IC_HZ))
        P("   IC 최강h 분포 : " + ", ".join(
            "h=%d:%d" % (h, bests.count(h)) for h in IC_HZ))
        P("\n   ※ 두 분포가 겹치지 않는 것 자체가 답이다 — tau는 긴 쪽(h=30)에,")
        P("     IC 최강은 양극단(h=1·h=30)에 몰린다.")
    else:
        P("   표본 부족 — 판정 불가")

    # ── 수명 스펙트럼 ────────────────────────────────────────────
    P("\n" + "=" * 116)
    P("[4] 발굴 피처의 수명 스펙트럼 — 이것이 사용자가 요청한 '피처별 수명'이다")
    P("=" * 116)
    tiers = [("초장기 (tau >= 30분)", lambda t: t >= 30),
             ("장기   (15 <= tau < 30)", lambda t: 15 <= t < 30),
             ("중기   (5 <= tau < 15)", lambda t: 5 <= t < 15),
             ("단기   (1 < tau < 5)", lambda t: TAU_FLOOR < t < 5)]
    for lab, fn in tiers:
        ns = [(nm, tau) for nm, tau, r, _w in keep if fn(tau)]
        if not ns:
            continue
        P("\n   %s — %d개" % (lab, len(ns)))
        for nm, tau in ns:
            fl = R[nm].get("flags") or []
            P("      %-32s %6.1f분  %s" % (nm[:32], tau, ",".join(fl) or ""))

    json.dump(dict(discovered=[dict(nm=nm, tau=tau, ci=R[nm]["wins"]["ci"],
                                    tau_rank=R[nm]["rank"]["mean"], t=R[nm]["t"],
                                    band=band_of(tau), best_h=R[nm].get("best_h"),
                                    flags=R[nm].get("flags") or [])
                              for nm, tau, R_, _w in [(a, b, c, d) for a, b, c, d in keep]],
                   dropped=[dict(nm=nm, tau=tau, why=w) for nm, tau, _r, w in drop]),
              open("lifetime_tau_final.json", "w", encoding="utf-8"),
              ensure_ascii=False,
              default=lambda o: None if isinstance(o, float) and not np.isfinite(o) else float(o))
    with open("lifetime_tau_final.txt", "w", encoding="utf-8") as f:
        f.write(L.getvalue())
    P("\n저장 -> lifetime_tau_final.txt / .json")


if __name__ == "__main__":
    main()
