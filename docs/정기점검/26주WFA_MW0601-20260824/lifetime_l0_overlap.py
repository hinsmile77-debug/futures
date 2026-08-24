# -*- coding: utf-8 -*-
"""[MW0601] L0 건강도 판정 vs 재검증 유형분류 — 두 체계가 같은 것을 잡는가.

배경: `docs/Spec for feature/피처셋_주기점검_자동리포트_구현계획_2026-08-02.md`가 정의하고
`scripts/feature_health_report.py`가 구현한 **L0 건강도**는
   zero-rate >= 95% OR 최빈값비중 >= 95% -> CRITICAL
   zero-rate >= 80% OR 최빈값비중 >= 80% -> WARN
이다. 2026-08-24 재검증이 도입한 **유형 분류**(D/B/C/S/I/N)와 겹치는지 실측한다.

핵심 질문 셋:
  Q1 L0가 CRITICAL/WARN으로 잡는 것과 유형분류가 부적격으로 내리는 것이 같은 집합인가?
  Q2 L0는 통과하는데 유형분류가 내리는 피처가 있나? (있다면 유형분류가 메우는 공백)
  Q3 유형분류는 통과하는데 L0가 잡는 피처가 있나? (있다면 L0가 메우는 공백)

주의 — 두 지표는 **다른 통계량**이다:
  L0 최빈값비중 = 값 분포에서 최빈값이 차지하는 비율   (값이 한 곳에 몰렸나)
  분류 동률(tie) = 증분 delta=0 의 비율                (값이 안 변하나)
날마다 값은 다르지만 하루 안에서는 안 변하는 계열(일봉 매크로)은 tie는 99%인데
최빈값비중은 낮을 수 있다.
"""
from __future__ import print_function

import io
import json
import os
import sys
from collections import Counter, defaultdict

import numpy as np

_ROOT = r"C:\Users\82108\PycharmProjects\futures"
sys.path.insert(0, _ROOT)
sys.stdout.reconfigure(encoding="utf-8")
from utils.dll_bootstrap import ensure_conda_dll_path

ensure_conda_dll_path()
from scripts.core_feature_discovery import build_matrix

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from live_only import load_live

CRIT_RATE = 0.95   # feature_health_report.py:53
WARN_RATE = 0.80   # feature_health_report.py:54
POINTMASS_DROP = 0.50   # 재검증 §9-1


def l0_level(v):
    """feature_health_report.py 판정 재현 (zero-rate / 최빈값비중)."""
    f = v[np.isfinite(v)]
    if f.size < 10:
        return "N/A", 0.0, 0.0
    if f.std() == 0:
        return "DEAD", 1.0, 1.0
    zero = float(np.mean(f == 0.0))
    vals, cts = np.unique(f, return_counts=True)
    mode_rate = float(cts.max() / f.size)
    if zero >= CRIT_RATE or mode_rate >= CRIT_RATE:
        return "CRITICAL", zero, mode_rate
    if zero >= WARN_RATE or mode_rate >= WARN_RATE:
        return "WARN", zero, mode_rate
    return "OK", zero, mode_rate


def main():
    L = io.StringIO()

    def P(*a):
        s = " ".join(str(x) for x in a)
        print(s)
        L.write(s + "\n")

    tax = json.load(open("lifetime_taxonomy.json", encoding="utf-8"))
    rec = tax["record"]
    elig = set(tax["eligible"])
    dropped_clean = set(tax["dropped_clean"])

    feats, closes, dates = load_live()
    names, X, ts_list = build_matrix(feats, verbose=False)

    P("=" * 112)
    P("[MW0601] L0 건강도 vs 재검증 유형분류 — 순수 라이브 %d거래일" % len(dates))
    P("=" * 112)
    P("L0 (feature_health_report.py): zero>=95%% or 최빈>=95%% -> CRITICAL / >=80%% -> WARN")
    P("분류 (재검증 §2·§9-1): D/B/C/S/I 부적격 + 점질량>=50%% 제외")

    rows = []
    for j, nm in enumerate(names):
        lvl, zero, mode = l0_level(X[:, j].astype(np.float64))
        r = rec.get(nm, {})
        kind = r.get("kind", "?")
        tie = r.get("tie") or 0.0
        ok_new = (nm in elig)
        rows.append(dict(nm=nm, l0=lvl, zero=zero, mode=mode, kind=kind,
                         tie=tie, ok_new=ok_new,
                         drop_clean=(nm in dropped_clean)))

    # ── 교차표 ────────────────────────────────────────────────────
    P("\n" + "=" * 112)
    P("[1] 교차표 — L0 등급 x 재검증 적격 여부")
    P("=" * 112)
    ct = defaultdict(lambda: [0, 0])
    for r in rows:
        ct[r["l0"]][0 if r["ok_new"] else 1] += 1
    P("%-12s %14s %14s" % ("L0 등급", "재검증 적격", "재검증 부적격"))
    P("-" * 112)
    for lvl in ("OK", "WARN", "CRITICAL", "DEAD", "N/A"):
        if lvl in ct:
            P("%-12s %14d %14d" % (lvl, ct[lvl][0], ct[lvl][1]))

    # ── Q2: L0 통과인데 분류가 내린 것 ────────────────────────────
    P("\n" + "=" * 112)
    P("[2] **L0는 OK인데 재검증이 부적격으로 내린 피처** — 유형분류가 메우는 공백")
    P("=" * 112)
    gap1 = [r for r in rows if r["l0"] == "OK" and not r["ok_new"]]
    P("%-32s %8s %9s %8s %8s  %s" % ("피처", "L0등급", "최빈비중", "동률", "유형", "사유"))
    P("-" * 112)
    for r in sorted(gap1, key=lambda z: -z["tie"]):
        why = rec.get(r["nm"], {}).get("why", "")
        if r["drop_clean"]:
            why = "점질량 %.0f%% (정제)" % (r["mode"] * 100)
        P("%-32s %8s %8.1f%% %7.1f%% %8s  %s"
          % (r["nm"][:32], r["l0"], r["mode"] * 100, r["tie"] * 100, r["kind"], why[:38]))
    P("\n   -> **%d개**. L0 임계(80%%)를 넘지 않아 건강도상 정상인데, decay 지표를 매기면"
      % len(gap1))
    P("      다른 양을 재게 되는 피처들이다.")

    # ── Q3: 분류 통과인데 L0가 잡은 것 ────────────────────────────
    P("\n" + "=" * 112)
    P("[3] **재검증은 적격인데 L0가 WARN/CRITICAL로 잡은 피처** — L0가 메우는 공백")
    P("=" * 112)
    gap2 = [r for r in rows if r["l0"] in ("WARN", "CRITICAL", "DEAD") and r["ok_new"]]
    if gap2:
        P("%-32s %8s %9s %8s %8s" % ("피처", "L0등급", "최빈비중", "zero%", "유형"))
        P("-" * 112)
        for r in sorted(gap2, key=lambda z: -z["mode"]):
            P("%-32s %8s %8.1f%% %7.1f%% %8s"
              % (r["nm"][:32], r["l0"], r["mode"] * 100, r["zero"] * 100, r["kind"]))
    else:
        P("   없음")
    P("\n   -> **%d개**." % len(gap2))

    # ── 매크로 계열 집중 확인 ──────────────────────────────────────
    P("\n" + "=" * 112)
    P("[4] 두 지표가 다른 것을 잰다는 증거 — 일봉 매크로 계열")
    P("=" * 112)
    P("%-32s %9s %8s %10s %10s" % ("피처", "최빈비중", "동률", "L0 판정", "분류"))
    P("-" * 112)
    for r in rows:
        if r["nm"].startswith("macro_") or r["kind"] in ("C", "S"):
            P("%-32s %8.1f%% %7.1f%% %10s %10s"
              % (r["nm"][:32], r["mode"] * 100, r["tie"] * 100, r["l0"], r["kind"]))
    P("\n   최빈값비중(L0)은 '값이 한 곳에 몰렸나'를, 동률(분류)은 '값이 안 변하나'를 잰다.")
    P("   날마다 값이 다르면 최빈값비중은 낮게 나오지만, 하루 안에서 상수면 동률은 99%다.")

    json.dump(dict(rows=rows, gap_l0ok_newdrop=[r["nm"] for r in gap1],
                   gap_newok_l0flag=[r["nm"] for r in gap2]),
              open("lifetime_l0_overlap.json", "w", encoding="utf-8"),
              ensure_ascii=False, default=float)
    with open("lifetime_l0_overlap.txt", "w", encoding="utf-8") as f:
        f.write(L.getvalue())
    P("\n저장 -> lifetime_l0_overlap.txt / .json")


if __name__ == "__main__":
    main()
