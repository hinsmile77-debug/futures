# -*- coding: utf-8 -*-
"""[MW0601 559차 / P1-1] `cvd_norm` **정규화 포화**의 원인 분해와 대안 실측.

무엇을 재는가
-------------
452차 발견 B 는 `cvd == 1.0` 이 분봉의 98.6~98.8% 라는 것이었고, 원인이 둘이라고
적었다.

  ① 체결 방향 분류 편향 → 누적 CVD 가 단조증가
  ② `features/technical/cvd.py:compute()` 의 정규화가 **현재값을 분모에 포함**

      cvd_abs_max = max(abs(v) for v in cvds)     # cvds 는 최근 10봉 창
      cvd_norm    = cumulative_cvd / cvd_abs_max

  단조증가면 창 안의 최댓값이 곧 현재값이라 몫이 **항상 1.0** 이 된다.

🔴 **①만 고치면 ②가 남는다.** QDQ 계획서 Phase 3-2 가 「동시 수정」을 요구하는 이유가
이것이고, 이 스크립트는 그 요구를 **숫자로** 뒷받침한다 — 흐름 원천(legacy/섀도/앵커)
× 정규화 방식(4종) 의 격자에서 포화율이 어떻게 움직이는지 본다.

정규화 후보
-----------
  V0 current  : 현행 — 창 최댓값(현재값 포함)
  V1 exclude  : 분모에서 **현재 봉을 뺀다** (창의 직전까지 최댓값)
  V2 sigma    : 중심화 CVD ÷ (k × delta 표준편차) — 수준이 아니라 **놀람의 크기**
  V3 range    : 창의 (최대−최소) 로 나눈다 — 단조증가여도 1.0 에 붙지 않는다

⚠ 이것은 **알파 판정이 아니다.** 손익도 IC 도 보지 않는다. 「포화가 풀리는가」만 본다.
   어느 대안을 채택할지는 Phase 3 승인 사항이며, 여기 숫자는 그 입력이다.

실행
----
    python scripts/cvd_saturation_probe.py
    python scripts/cvd_saturation_probe.py --json
    python scripts/cvd_saturation_probe.py --from 2026-08-10

⚠ 장 마감 후 전용(456차). 종료코드 0 고정(판정기가 아니다) · 2 = 장중 차단.
"""
from __future__ import print_function

import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.dll_bootstrap import ensure_conda_dll_path  # noqa: E402

ensure_conda_dll_path()

import argparse  # noqa: E402
import json as _json  # noqa: E402
from collections import OrderedDict, deque  # noqa: E402

import numpy as np  # noqa: E402

from utils.analysis_db import guard_intraday, connect_ro  # noqa: E402

CHANNEL = "cvd_saturation_probe"
RAW_DB = os.path.join(_ROOT, "data", "db", "raw_data.db")

WINDOW = 10          # features/technical/cvd.py 의 기본 창과 같아야 한다
SIGMA_K = 3.0        # V2 의 k — 3σ 를 ±1 로 본다
SAT_EPS = 1e-3       # |cvd_norm| >= 1 - eps 이면 포화로 센다

FLOWS = ("legacy", "shadow", "anchor")
VARIANTS = ("V0_current", "V1_exclude_self", "V2_sigma", "V3_range")


def _rows(con, since):
    q = ("SELECT ts, close, buy_vol, sell_vol, buy_vol_flag, sell_vol_flag,"
         " anchor_buy, anchor_sell FROM raw_candles WHERE ts >= ? ORDER BY ts")
    return con.execute(q, (since,)).fetchall()


def _pair(row, flow):
    """흐름 원천별 (buy, sell). 그 봉에 없으면 None — 폴백하지 않는다."""
    if flow == "legacy":
        b, s = row[2], row[3]
    elif flow == "shadow":
        b, s = row[4], row[5]
    else:
        b, s = row[6], row[7]
    return None if (b is None or s is None) else (float(b), float(s))


def _replay_day(rows, flow):
    """하루치를 재생해 변형별 cvd_norm 시계열을 낸다. 미측정 봉은 건너뛴다."""
    cvd = 0.0
    cvd_c = 0.0
    dsum, dn = 0.0, 0
    buf = deque(maxlen=WINDOW)
    cbuf = deque(maxlen=WINDOW)
    dbuf = deque(maxlen=60)
    out = dict((v, []) for v in VARIANTS)
    for row in rows:
        pair = _pair(row, flow)
        if pair is None:
            continue
        delta = pair[0] - pair[1]
        cvd += delta
        mean_prev = (dsum / dn) if dn else 0.0
        cvd_c += (delta - mean_prev)
        dn += 1
        dsum += delta
        buf.append(cvd)
        cbuf.append(cvd_c)
        dbuf.append(delta)
        if len(buf) < 3:
            continue
        cvds = list(buf)

        # V0 — 현행
        m0 = max(abs(v) for v in cvds) or 1.0
        out["V0_current"].append(cvd / m0)

        # V1 — 분모에서 현재 봉 제외
        prev = cvds[:-1]
        m1 = (max(abs(v) for v in prev) if prev else 0.0) or 1.0
        out["V1_exclude_self"].append(float(np.clip(cvd / m1, -1.0, 1.0)))

        # V2 — 중심화 CVD ÷ (k σ_delta)
        sd = float(np.std(list(dbuf))) if len(dbuf) >= 3 else 0.0
        m2 = (SIGMA_K * sd) or 1.0
        out["V2_sigma"].append(float(np.clip(cvd_c / m2, -1.0, 1.0)))

        # V3 — 창의 진폭
        m3 = (max(cvds) - min(cvds)) or 1.0
        out["V3_range"].append(float(np.clip((cvd - float(np.mean(cvds))) / m3, -1.0, 1.0)))
    return out


def probe(since):
    con = connect_ro(RAW_DB)
    rows = _rows(con, since)
    by_day = OrderedDict()
    for r in rows:
        by_day.setdefault(r[0][:10], []).append(r)

    res = OrderedDict()
    for flow in FLOWS:
        acc = dict((v, []) for v in VARIANTS)
        days = 0
        for _day, drows in by_day.items():
            rep = _replay_day(drows, flow)
            if not rep["V0_current"]:
                continue
            days += 1
            for v in VARIANTS:
                acc[v].extend(rep[v])
        res[flow] = {"days": days, "bars": len(acc["V0_current"]), "variants": {}}
        for v in VARIANTS:
            a = np.asarray(acc[v], dtype=float)
            if a.size == 0:
                res[flow]["variants"][v] = None
                continue
            res[flow]["variants"][v] = {
                "saturated_ratio": round(float(np.mean(np.abs(a) >= 1.0 - SAT_EPS)), 4),
                "mean": round(float(np.mean(a)), 4),
                "std": round(float(np.std(a)), 4),
                "p10": round(float(np.percentile(a, 10)), 4),
                "p50": round(float(np.percentile(a, 50)), 4),
                "p90": round(float(np.percentile(a, 90)), 4),
                "negative_ratio": round(float(np.mean(a < 0)), 4),
            }
    return res


def main():
    ap = argparse.ArgumentParser(description="cvd_norm 정규화 포화 분해 (559차 P1-1)")
    ap.add_argument("--from", dest="since", default="2026-08-10",
                    help="시작일 (기본: 섀도 계측 개시일)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    guard_intraday(CHANNEL)
    if not os.path.exists(RAW_DB):
        print("[%s] raw_data.db 없음" % CHANNEL)
        return 0

    res = probe(args.since)
    if args.json:
        print(_json.dumps({"channel": CHANNEL, "since": args.since,
                           "window": WINDOW, "sigma_k": SIGMA_K,
                           "result": res}, ensure_ascii=False, indent=2))
        return 0

    print("=" * 78)
    print("[%s] cvd_norm 포화 분해 — 흐름원천 × 정규화 (관측 전용)" % CHANNEL)
    print("=" * 78)
    print("창 %d봉 · σk=%.1f · 포화 판정 |norm| >= %.3f · %s 이후"
          % (WINDOW, SIGMA_K, 1.0 - SAT_EPS, args.since))
    for flow, r in res.items():
        print("-" * 78)
        print("흐름 %-7s  %d거래일 · %d봉" % (flow, r["days"], r["bars"]))
        if not r["bars"]:
            print("   표본 없음 — 그 원천은 이 구간에 계측되지 않았다")
            continue
        print("   %-16s %9s %8s %8s %8s %8s %8s"
              % ("정규화", "포화율", "평균", "표준편차", "p10", "p50", "음수비"))
        for v in VARIANTS:
            d = r["variants"][v]
            if d is None:
                continue
            print("   %-16s %8.1f%% %8.3f %8.3f %8.3f %8.3f %7.1f%%"
                  % (v, d["saturated_ratio"] * 100, d["mean"], d["std"],
                     d["p10"], d["p50"], d["negative_ratio"] * 100))
    print("-" * 78)
    print("읽는 법: 흐름을 legacy→shadow 로 바꿔도 V0 포화율이 안 내려가면 원인 ②가")
    print("         독립으로 살아 있다는 뜻이다 — 방향 분류만 고쳐서는 안 된다.")
    print("⚠ 채택 결정은 Phase 3 승인 사항. 이 표는 손익이 아니라 분포만 본다.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
