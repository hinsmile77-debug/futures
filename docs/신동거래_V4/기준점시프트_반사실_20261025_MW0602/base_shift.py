# -*- coding: utf-8 -*-
"""[MW0602] V4 콜-풋 기준점(FLOW_BASE) 09:00~09:10 시프트 반사실. 읽기 전용(DB 미기록).
저장소 루트에서: conda run -n py37_32 python "docs/신동거래_V4/기준점시프트_반사실_20261025_MW0602/base_shift.py"

mode A = FLOW_BASE 전면(FLOWC 누적 기준 + R60 개시 시각 + 일관성 필터 모두 이동 — 코드상 상수 하나)
mode B = FLOWC 누적 기준만 이동(R60 개시는 09:00 기준 유지)
방향적중 = 진입 방향과 (15:05 종가 − 진입가) 부호 일치. 손익 = engine.trade_net(가상 2계약).
"""
import datetime as dt, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while not os.path.isdir(os.path.join(ROOT, "strategy")):
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, ROOT); os.chdir(ROOT)
from strategy.shindong import engine as E, families as F, runner, spec as S   # noqa: E402
from strategy.shindong.calendar import select_flow_product                    # noqa: E402

DB = "data/db/"
REF = json.load(open("docs/신동거래_V4/V22_V3_반사실_20261024/v4_compare.json", encoding="utf-8"))
DAYS = sorted(REF["V4"])
FR = {}
for d in DAYS:
    prod, _, _ = select_flow_product(dt.date.fromisoformat(d))
    cd, fl, lr = runner.load_inputs(d, prod, DB + "raw_data.db", DB + "option_flow.db", DB + "premarket_levels.db")
    FR[d] = (E.DayFrame(cd, fl, fx=runner.load_fx(d, DB + "raw_data.db")), E.prepare_levels(lr))
orig_fs = F._flow_signal


def run(base, mode):
    if mode == "A":
        S.FLOW_BASE = base; F._flow_signal = orig_fs
    else:
        S.FLOW_BASE = "09:00"

        def fs(*a, **k):
            S.FLOW_BASE = base
            try:
                return orig_fs(*a, **k)
            finally:
                S.FLOW_BASE = "09:00"
        F._flow_signal = fs
    out = {"net": 0.0, "n": 0, "win": 0, "hit": 0, "f_n": 0, "f_hit": 0, "f_win": 0, "f_net": 0.0, "f_t": [], "days": {}}
    for d in DAYS:
        D, L = FR[d]
        r = F.run_family_day(D, L, "v4")
        c15 = D.c[D.last_at_or_before(S.TIME_EXIT)]
        dn = 0.0
        tr = [t for t in r["trades"] if t["status"] == "CLOSED"]
        for i, t in enumerate(tr):
            net = E.trade_net(t); dn += net
            out["n"] += 1; out["win"] += net > 0
            h = (c15 - t["entry_px"]) * t["side"] > 0; out["hit"] += h
            if i == 0 and t["rule"] == F.RULE_FLOW:
                out["f_n"] += 1; out["f_hit"] += h; out["f_win"] += net > 0; out["f_net"] += net
                hh, mm = map(int, t["entry_ts"][-5:].split(":")); out["f_t"].append(hh * 60 + mm)
        out["net"] += dn; out["days"][d] = dn
    S.FLOW_BASE = "09:00"; F._flow_signal = orig_fs
    return out


res = {}
for mode in ("A", "B"):
    print("\n== mode %s ==" % mode)
    print("기준  순손익(만,2계약)  거래  승률   방향적중(→15:05)  첫거래:n 적중 승률 손익(만)  첫진입평균  최악일(만)  플러스일")
    for m in range(0, 11):
        b = "09:%02d" % m
        o = run(b, mode); res["%s_%s" % (mode, b)] = o
        ft = sum(o["f_t"]) / len(o["f_t"]) if o["f_t"] else 0
        print("%s  %10.1f  %4d  %5.1f%%  %6.1f%%   %3d %5.1f%% %5.1f%% %8.1f   %02d:%02d   %8.1f   %d/%d" % (
            b, o["net"] / 1e4, o["n"], 100 * o["win"] / max(o["n"], 1), 100 * o["hit"] / max(o["n"], 1),
            o["f_n"], 100 * o["f_hit"] / max(o["f_n"], 1), 100 * o["f_win"] / max(o["f_n"], 1), o["f_net"] / 1e4,
            ft // 60, ft % 60, min(o["days"].values()) / 1e4, sum(v > 0 for v in o["days"].values()), len(DAYS)))
json.dump({k: {"net": v["net"], "days": v["days"]} for k, v in res.items()},
          open(os.path.join(HERE, "base_shift.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
