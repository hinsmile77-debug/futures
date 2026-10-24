# -*- coding: utf-8 -*-
"""[MW0602 657차] V4 구현 재현 검증 — 공식 엔진 `families.run_family_day(.., "v4")` vs 반사실 `v4_compare.json`.

읽기 전용(DB 미기록). 저장소 루트에서:  python "docs/신동거래_V4/V4구현_재현검증_20261024/verify_v4_engine.py"
비교: 날짜별 거래 손익(pt, 1계약 환산) 목록 · 합계(가상 2계약 원). V3(hybr60) 도 함께 대조해 무변경을 확인한다.
반사실 sim6 는 TIME 청산을 항상 15:05 로 계산하므로 공식 엔진도 하루 전체(horizon 없음)로 돌린다.
"""
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while not os.path.isdir(os.path.join(ROOT, "strategy")):
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, ROOT)
os.chdir(ROOT)
from strategy.shindong import engine as E, families as F, runner, spec as S   # noqa: E402
from strategy.shindong.calendar import select_flow_product                    # noqa: E402

DB = "data/db/"
REF = json.load(open(os.path.join(HERE, "..", "V22_V3_반사실_20261024", "v4_compare.json"), encoding="utf-8"))


def frame(d):
    prod, _, _ = select_flow_product(dt.date.fromisoformat(d))
    cd, fl, lr = runner.load_inputs(d, prod, DB + "raw_data.db", DB + "option_flow.db", DB + "premarket_levels.db")
    fx = runner.load_fx(d, DB + "raw_data.db")
    return E.DayFrame(cd, fl, fx=fx), E.prepare_levels(lr)


tot = {"V3": [0.0, 0.0], "V4": [0.0, 0.0]}
mism = 0
for d in sorted(REF["V4"]):
    D, L = frame(d)
    for lab, fam in (("V3", "hybr60"), ("V4", "v4")):
        r = F.run_family_day(D, L, fam)
        got = [E.trade_net(t) / 2 / S.PT_VALUE_KRW for t in r["trades"] if t["status"] == "CLOSED"]
        ref = REF[lab][d]
        # 반사실 V4 열은 sim6.run 이 pt 를 소수 2자리로 반올림해 저장했다 → V4 허용오차 = 반올림 폭(0.005). V3 는 원값.
        tol = 0.005 + 1e-9 if lab == "V4" else 1e-6
        ok = len(got) == len(ref) and all(abs(a - b) <= tol for a, b in zip(got, ref))
        tot[lab][0] += sum(got) * 2 * S.PT_VALUE_KRW
        tot[lab][1] += sum(ref) * 2 * S.PT_VALUE_KRW
        if not ok:
            mism += 1
            print("X %s %s  공식 %s\n            반사실 %s" % (d, lab, [round(x, 2) for x in got], [round(x, 2) for x in ref]))
            for t in r["trades"]:
                print("     %s %s %+d → %s %s cut=%s be=%s" % (t["rule"], t["entry_ts"], t["side"], t["exit_ts"],
                                                         t["legs"][0].get("reason"), t.get("cut"), t.get("be_armed")))
        if lab == "V4":
            info = [n for n in r["decision"]["notes"] if n.startswith("[v4]")]
            print("  %s V4 %+7.2fpt  %s" % (d, sum(got), " / ".join(info)))
for lab, (a, b) in tot.items():
    print("%s 합계(가상 2계약) 공식 %s원 · 반사실 %s원 · 차 %s" % (lab, format(a, ",.0f"), format(b, ",.0f"), format(a - b, ",.0f")))
print("불일치 %d건" % mism)
