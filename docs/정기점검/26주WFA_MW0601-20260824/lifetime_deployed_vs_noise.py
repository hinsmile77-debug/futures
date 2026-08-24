# -*- coding: utf-8 -*-
"""[MW0601] 배포 피처셋 vs 노이즈 하한선 — 모델이 실제로 쓰는 피처가 노이즈를 넘는가.

사용자 질문(2026-08-25): "h=5 하한 미달 69개를 제외한 피처를 호라이즌 피처셋으로
사용하고 있는지 확인해."

배포의 진실은 `model/horizons/feature_names_{hz}.pkl`이다(337차·394차 교훈 —
`horizon_feature_sets.json`이나 `shap_feature_registry.json`으로 판단하면 오판한다).

L1 호라이즌 그룹 매핑(core_feature_discovery.main의 grp와 동일):
    h=5  -> 단기 1m·3m·5m   /  h=15 -> 중기 10m·15m  /  h=30 -> 장기 30m

⚠ 읽기 전용. 노이즈 하한선은 **판정 기준이 아니다**(현재 L1에서도 병기 표시만 한다).
"""
from __future__ import print_function

import io
import json
import os
import pickle
import sys

import numpy as np

_ROOT = r"C:\Users\82108\PycharmProjects\futures"
sys.path.insert(0, _ROOT)
sys.stdout.reconfigure(encoding="utf-8")
from utils.dll_bootstrap import ensure_conda_dll_path

ensure_conda_dll_path()
from scripts.core_feature_discovery import (load, build_matrix, analyze,
                                            build_noise_matrix, HORIZONS)
from scripts.noise_benchmark import noise_floor

HORIZON_DIR = os.path.join(_ROOT, "model", "horizons")
HZ_OF_H = {5: ["1m", "3m", "5m"], 15: ["10m", "15m"], 30: ["30m"]}
DAYS = 40


def load_deployed(hzs):
    out = {}
    for hz in hzs:
        p = os.path.join(HORIZON_DIR, "feature_names_%s.pkl" % hz)
        if not os.path.exists(p):
            out[hz] = None
            continue
        try:
            with open(p, "rb") as f:
                out[hz] = [str(x) for x in pickle.load(f)]
        except Exception as e:
            print("[경고] %s 로드 실패: %s" % (hz, e))
            out[hz] = None
    return out


def main():
    L = io.StringIO()

    def P(*a):
        s = " ".join(str(x) for x in a)
        print(s)
        L.write(s + "\n")

    feats, closes, dates = load(DAYS)
    names, X, ts_list = build_matrix(feats, verbose=False)
    seed = int(dates[-1].replace("-", ""))
    nz_names, NZ = build_noise_matrix(names, X, seed)

    all_hz = [h for hs in HZ_OF_H.values() for h in hs]
    deployed = load_deployed(all_hz)

    P("=" * 112)
    P("[MW0601] 배포 피처셋 vs 노이즈 하한선 — %d거래일 (%s ~ %s)"
      % (len(dates), dates[0], dates[-1]))
    P("=" * 112)
    P("배포 진실 = model/horizons/feature_names_{hz}.pkl · 스크리닝 대상 %d피처"
      % len(names))
    P("⚠ 노이즈 하한선은 **판정 기준이 아니다** — 현재 L1도 병기 표시(▽)만 한다.")

    summary = {}
    for h in HORIZONS:
        res, nd = analyze(names, X, ts_list, closes, h)
        t_of = {r["name"]: r["ic_t"] for r in res}
        nres, _ = analyze(nz_names, NZ, ts_list, closes, h)
        fl, fnm = noise_floor(nres, name_key="name", stat_key="ic_t")

        scr = [n for n in names if np.isfinite(t_of.get(n, float("nan")))]
        below_all = [n for n in scr if abs(t_of[n]) < fl]

        P("\n" + "=" * 112)
        P("h=%d  (%s)   노이즈 하한 |IC_t| = %.2f (%s)"
          % (h, " · ".join(HZ_OF_H[h]), fl, fnm or "—"))
        P("=" * 112)
        P("스크리닝 %d개 중 하한 미달 %d개 (%.0f%%) / 초과 %d개"
          % (len(scr), len(below_all), 100.0 * len(below_all) / max(1, len(scr)),
             len(scr) - len(below_all)))

        # 하한 초과 목록 (= "미달 제외하고 남는 것")
        above = sorted([n for n in scr if abs(t_of[n]) >= fl],
                       key=lambda n: -abs(t_of[n]))
        P("\n  [하한 초과 %d개] — 미달분을 제외하면 남는 피처" % len(above))
        for n in above:
            where = [hz for hz in HZ_OF_H[h] if deployed.get(hz) and n in deployed[hz]]
            P("    %-32s |t|=%5.2f   %s"
              % (n[:32], abs(t_of[n]),
                 ("배포: " + ", ".join(where)) if where else "**배포 안 됨**"))

        # 배포 피처 관점
        for hz in HZ_OF_H[h]:
            dep = deployed.get(hz)
            if not dep:
                P("\n  [%s] pkl 없음 — 대조 불가" % hz)
                continue
            rows = []
            for n in dep:
                t = t_of.get(n)
                rows.append((n, t))
            n_scr = [r for r in rows if r[1] is not None and np.isfinite(r[1])]
            n_bel = [r for r in n_scr if abs(r[1]) < fl]
            n_na = [r for r in rows if r not in n_scr]
            P("\n  [%s 배포 %d개] 하한 미달 **%d개** / 초과 %d개 / 미평가 %d개"
              % (hz, len(dep), len(n_bel), len(n_scr) - len(n_bel), len(n_na)))
            for n, t in sorted(rows, key=lambda r: -(abs(r[1]) if r[1] is not None
                                                     and np.isfinite(r[1]) else -1)):
                if t is None or not np.isfinite(t):
                    P("    %-32s     —      (스크리닝 대상 아님)" % n[:32])
                else:
                    P("    %-32s |t|=%5.2f  %s"
                      % (n[:32], abs(t), "▽ 하한 미달" if abs(t) < fl else "초과"))
            summary["%s" % hz] = dict(
                h=h, floor=float(fl), n_deployed=len(dep),
                below=[r[0] for r in n_bel],
                above=[r[0] for r in n_scr if abs(r[1]) >= fl],
                unscreened=[r[0] for r in n_na])

    # ── 총평 ──────────────────────────────────────────────────────
    P("\n" + "=" * 112)
    P("[요약] 호라이즌별 배포 피처의 노이즈 하한선 통과율")
    P("=" * 112)
    P("%-6s %8s %10s %10s %10s %s" %
      ("호라이즌", "배포", "하한초과", "하한미달", "미평가", "하한"))
    P("-" * 112)
    for hz in all_hz:
        s = summary.get(hz)
        if not s:
            continue
        P("%-6s %8d %10d %10d %10d %8.2f"
          % (hz, s["n_deployed"], len(s["above"]), len(s["below"]),
             len(s["unscreened"]), s["floor"]))

    tot_dep = sum(s["n_deployed"] for s in summary.values())
    tot_bel = sum(len(s["below"]) for s in summary.values())
    tot_abv = sum(len(s["above"]) for s in summary.values())
    tot_na = sum(len(s["unscreened"]) for s in summary.values())
    P("-" * 112)
    P("%-6s %8d %10d %10d %10d" % ("합계", tot_dep, tot_abv, tot_bel, tot_na))
    P("\n(중복 계상 있음 — 같은 피처가 여러 호라이즌에 배포될 수 있다)")

    json.dump(summary, open("lifetime_deployed_vs_noise.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    with open("lifetime_deployed_vs_noise.txt", "w", encoding="utf-8") as f:
        f.write(L.getvalue())
    P("\n저장 -> lifetime_deployed_vs_noise.txt / .json")


if __name__ == "__main__":
    main()
