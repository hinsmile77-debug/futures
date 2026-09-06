# -*- coding: utf-8 -*-
"""당일 맥점 예측 — **거리 모델 워크포워드 재현 검증** (가이드 §9 Phase 0 완료 기준).

[MW0601 534차] 구현이 옳게 이식됐는지 판정하는 유일한 수단이다. 가이드 §2-4 의 검증
수치(144세션, 2026-01-05~09-04)를 `raw_candles` 로 그대로 재현한다:

    N0 전일 고·저      MAE 30.9pt
    N1 시가±전일범위/2  MAE 15.3pt
    M1 (08:50)         MAE 14.2pt · 50% 47% · 80% 78%  (R̂ 스케일 83%)
    P1 (09:30)         MAE 11.0pt · 50% 44% · 80% 74%  (R̂ 스케일 81%)

**재현되지 않으면 구현이 틀린 것이다**(가이드 §9). 단 마흐디 원 검증은 2026-08-20
이후 세션을 마흐디 자체 봉으로 덮어 계산했으므로 마지막 ~11세션에서 소폭 차이가 날
수 있다 — 판정은 소수점이 아니라 **자릿수·순서**(M1 < N1 < N0, P1 < M1)로 한다.

실행:
    python scripts/premarket_levels_wfa.py
    python scripts/premarket_levels_wfa.py --start 2026-01-05 --end 2026-09-05
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

from utils.analysis_db import guard_intraday
from features.levels import levels_store as LS
from features.levels import premarket_levels as PL


def _inside(v, band):
    return bool(band[0] <= v <= band[1])


def run(start, end, db_path=None):
    sessions, excluded = LS.load_sessions(db_path=db_path)
    summaries = [PL.summarize_session(d, bars) for d, bars in sessions]
    PL.fill_derived(summaries)
    print("이력 %d세션 (%s ~ %s) · 품질 제외 %d세션"
          % (len(summaries), summaries[0].d, summaries[-1].d, len(excluded)))
    if excluded:
        print("  제외: " + ", ".join("%s(%s)" % (k, v) for k, v in sorted(excluded.items())))

    acc = {}
    for key in ("N0", "N1", "M1", "P1"):
        acc[key] = dict(err=[], in50=0, in80=0, in80raw=0, n=0, nraw=0, hit=0)

    for i, s in enumerate(summaries):
        if i < 1 or not (start <= s.d <= end) or not s.atr:
            continue
        past = summaries[:i]
        prev = past[-1]
        atr = s.atr
        atr5 = PL.atr_of(past, i, 5)

        # ── N0: 전일 고·저 그대로 ──
        acc["N0"]["err"] += [prev.h - s.h, prev.l - s.l]
        acc["N0"]["n"] += 2

        # ── N1: 시가 ± 전일범위/2 ──
        half = (prev.h - prev.l) / 2.0
        acc["N1"]["err"] += [(s.o + half) - s.h, (s.o - half) - s.l]
        acc["N1"]["n"] += 2

        # ── M1 (08:50) ──
        p1 = PL.fit_stage1(past[-PL.TRAIN_SESSIONS:])
        if p1:
            today = PL.SessionSummary(d=s.d, o=s.o, h=s.o, l=s.o, c=s.o, atr=atr)
            rhat1 = PL.fit_rhat(past, i, with_path=False)
            xf = PL._x_fixed(today, prev, atr5)
            scale = PL.rhat_scale(rhat1, xf)
            dist = PL.distance_stage1(p1, s.o, atr, scale)
            a = acc["M1"]
            a["err"] += [dist["high"] - s.h, dist["low"] - s.l]
            a["n"] += 2
            a["in50"] += int(_inside(s.h, dist["high50"])) + int(_inside(s.l, dist["low50"]))
            a["in80"] += int(_inside(s.h, dist["high80"])) + int(_inside(s.l, dist["low80"]))
            if dist.get("raw"):
                a["nraw"] += 2
                a["in80raw"] += (int(_inside(s.h, dist["raw"]["high80"]))
                                 + int(_inside(s.l, dist["raw"]["low80"])))

        # ── P1 (09:30) ──
        p2 = PL.fit_stage2(past, i)
        if p2 and s.u_t is not None:
            rhat2 = PL.fit_rhat(past, i, with_path=True)
            today = PL.SessionSummary(d=s.d, o=s.o, h=s.o, l=s.o, c=s.o, atr=atr)
            xf = PL._x_fixed(today, prev, atr5)
            x2 = (xf + [np.log(max(s.u_t + s.d_t, 1e-3)), abs(s.ret_t)]) if xf else None
            scale = PL.rhat_scale(rhat2, x2)
            dist = PL.distance_stage2(p2, s.o, atr, s.o - prev.c, prev.h - prev.l,
                                      (s.u_t, s.d_t, s.ret_t), scale)
            a = acc["P1"]
            a["err"] += [dist["high"] - s.h, dist["low"] - s.l]
            a["n"] += 2
            a["in50"] += int(_inside(s.h, dist["high50"])) + int(_inside(s.l, dist["low50"]))
            a["in80"] += int(_inside(s.h, dist["high80"])) + int(_inside(s.l, dist["low80"]))
            if dist.get("raw"):
                a["nraw"] += 2
                a["in80raw"] += (int(_inside(s.h, dist["raw"]["high80"]))
                                 + int(_inside(s.l, dist["raw"]["low80"])))

    print("")
    print("| 모델 | n(세션) | MAE pt | 50% 구간 | 80% 구간 | 80% 원구간 |")
    print("|---|---|---|---|---|---|")
    expect = {"N0": "30.9", "N1": "15.3", "M1": "14.2", "P1": "11.0"}
    for key in ("N0", "N1", "M1", "P1"):
        a = acc[key]
        if not a["n"]:
            print("| %s | 0 | — | — | — | — |" % key)
            continue
        mae = float(np.mean(np.abs(a["err"])))
        c50 = "%.0f%%" % (a["in50"] / a["n"] * 100) if key in ("M1", "P1") else "—"
        c80 = "%.0f%%" % (a["in80"] / a["n"] * 100) if key in ("M1", "P1") else "—"
        craw = "%.0f%%" % (a["in80raw"] / a["nraw"] * 100) if a["nraw"] else "—"
        print("| %s | %d | %.1f (기대 %s) | %s | %s | %s |"
              % (key, a["n"] // 2, mae, expect[key], c50, c80, craw))
    print("")
    print("> 80% 구간은 R̂ 스케일(하한 0.85) 적용값, 「원구간」은 스케일 전 — "
          "두 열의 차이가 가이드 §5 채택의 손익이다.")
    return acc


def main(argv=None):
    ap = argparse.ArgumentParser(description="맥점 거리 모델 워크포워드 재현 검증")
    ap.add_argument("--start", default="2026-01-05")
    ap.add_argument("--end", default="2026-12-31")
    ap.add_argument("--db", default=None)
    a = ap.parse_args(argv)
    guard_intraday("premarket_levels_wfa")
    run(a.start, a.end, a.db)
    return 0


if __name__ == "__main__":
    sys.exit(main())
