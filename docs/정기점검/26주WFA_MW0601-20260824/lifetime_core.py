# -*- coding: utf-8 -*-
"""[MW0601] 현행 CORE 배정 vs 수명·IC 실측 대조 (읽기 전용 진단).

CLAUDE.md 절대원칙 §3은 CORE를 호라이즌 그룹별로 지정한다:
   단기(1m·3m·5m)  cvd_divergence · vwap_position · ofi_norm
   중기(10m·15m)   vwap_position
   장기(30m)       opt_chain_pcr

이 배정이 라이브 실측(수명 tau · 호라이즌별 IC)과 정합하는지 대조한다.
※ 이 스크립트는 아무것도 바꾸지 않는다. 배정 변경은 주간회의 수동 승인 경로만이다
   (절대원칙 §3 "교체 불가" · §6 자동 통합 금지).
"""
from __future__ import print_function
import io
import json
import math
import sys

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")

IC_HZ = [1, 3, 5, 10, 15, 30]
ASSIGN = {
    "cvd_divergence": "단기(1/3/5m)",
    "cvd_delta_norm": "단기 체크리스트 실소비값",
    "vwap_position": "단기+중기(1/3/5/10/15m)",
    "ofi_norm": "단기(1/3/5m)",
    "opt_chain_pcr": "장기(30m)",
    "vwap_momentum": "(CORE 아님·참고)",
}


def main():
    L = io.StringIO()

    def P(*a):
        s = " ".join(str(x) for x in a)
        print(s)
        L.write(s + "\n")

    life = json.load(open("lifetime_raw.json", encoding="utf-8"))["result"]
    cross = json.load(open("lifetime_cross.json", encoding="utf-8"))
    IC = cross["ic"]

    P("=" * 110)
    P("[MW0601] 현행 CORE 배정 vs 라이브 실측 — 순수 라이브 %d거래일 (%s~%s)"
      % (cross["n_days"], cross["dates"][0], cross["dates"][1]))
    P("=" * 110)
    P("※ 읽기 전용 진단. 절대원칙 §3은 CORE 교체 불가 · §6은 자동 통합 금지.")

    P("\n%-22s %-26s %6s %6s %7s" % ("CORE 피처", "현행 배정", "tau", "동률%", "L_raw")
      + " " + " ".join("%8s" % ("t@%d" % h) for h in IC_HZ))
    P("-" * 110)
    for nm, asg in ASSIGN.items():
        r = life.get(nm)
        if not r:
            P("%-22s %-26s  (수명 미산출 — build_matrix 탈락)" % (nm[:22], asg))
            continue
        ts = []
        for h in IC_HZ:
            v = IC[str(h)].get(nm, {}).get("t")
            ts.append(v if v is not None else float("nan"))
        best = int(np.nanargmax([abs(x) for x in ts])) if any(np.isfinite(ts)) else None
        line = "%-22s %-26s %6.1f %5.1f%% %7.2f " % (
            nm[:22], asg, r.get("tau") or float("nan"), r["tie"] * 100,
            r.get("L_raw") or float("nan"))
        line += " ".join(("%8.2f" % t if np.isfinite(t) else "%8s" % "-") for t in ts)
        if best is not None:
            line += "   <-최강 h=%d" % IC_HZ[best]
        P(line)

    P("\n" + "=" * 110)
    P("[대조 결과]")
    P("=" * 110)

    # vwap_position 상세
    vp = [IC[str(h)].get("vwap_position", {}).get("t") for h in IC_HZ]
    if all(v is not None for v in vp):
        P("\n1) vwap_position — 유일하게 다중비교(|t|>=6.44)를 넘는 피처")
        P("   호라이즌별 |t|: " + " ".join("h=%d:%.2f" % (h, abs(t)) for h, t in zip(IC_HZ, vp)))
        b = int(np.argmax([abs(t) for t in vp]))
        P("   최강 h=%d (t=%+.2f) — 단조 증가: 호라이즌이 길수록 강해진다"
          % (IC_HZ[b], vp[b]))
        ic30 = IC["30"]["vwap_position"]["ic"]
        P("   ⚠ IC 부호가 **음수**(h=30 IC=%+.4f)다. 26주 재검증 §7-1이 지적한"
          % ic30)
        P("     '체크리스트는 양수 방향으로 배선' 문제와 같은 사실이며, 여기서는")
        P("     '중기까지만 배정돼 있는데 실측 최강은 h=30'이라는 점이 추가된다.")

    # opt_chain_pcr
    op = life.get("opt_chain_pcr")
    if op:
        P("\n2) opt_chain_pcr — 장기(30m) CORE")
        P("   동률 %.1f%% · 분단위 런이 전 시간대에서 정확히 1.00 = 방향 수명 측정 불가"
          % (op["tie"] * 100))
        t30 = IC["30"].get("opt_chain_pcr", {}).get("t")
        P("   h=30 IC t = %s" % ("%+.2f" % t30 if t30 is not None else "산출 불가"))
        P("   -> 458차가 확인한 '지정만 존재하는 상태'(모델 미편입·IC 무정보)와 일치.")
        P("      수명 축에서도 판정 근거를 주지 못한다.")

    # 단기 CORE 3종의 수명
    P("\n3) 단기 CORE 3종의 수명 — 단기 배정과 정합하는가")
    for nm in ("cvd_divergence", "vwap_position", "ofi_norm"):
        r = life.get(nm)
        if not r:
            continue
        tau = r.get("tau") or float("nan")
        P("   %-16s tau=%5.1f분  L_raw=%.2f분  -> tau가 %s"
          % (nm, tau, r.get("L_raw") or float("nan"),
             "1~5m 범위와 정합" if tau <= 6 else "단기 범위를 넘음(%d분)" % tau))

    # 전체에서 h별 최강 피처
    P("\n4) 호라이즌별 실측 최강 피처 (참고 — 배정 근거가 아니라 현황)")
    for h in IC_HZ:
        d = IC[str(h)]
        cand = [(n, v["t"]) for n, v in d.items()
                if v.get("t") is not None and n not in ("time_cos", "time_sin")]
        cand.sort(key=lambda z: -abs(z[1]))
        P("   h=%-3d " % h + ", ".join("%s(%+.1f)" % (n[:22], t) for n, t in cand[:4]))

    P("\n" + "=" * 110)
    P("[주의] 위 표는 배정 변경을 제안하지 않는다.")
    P("  · 516개 검정 중 다중비교 생존은 9셀이고 그 대부분이 vwap_position 한 피처다.")
    P("  · L2(비용 차감 거래성) 층에서는 같은 창에서 합격 셀이 0이었다(26주 재검증 §12).")
    P("  · 따라서 이 대조의 용도는 '현행 배정과 실측의 불일치 지점을 기록'하는 데 있다.")
    P("=" * 110)

    with open("lifetime_core.txt", "w", encoding="utf-8") as f:
        f.write(L.getvalue())
    P("\n저장 -> lifetime_core.txt")


if __name__ == "__main__":
    main()
