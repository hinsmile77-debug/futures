# -*- coding: utf-8 -*-
"""[MW0602 657차] V4 실거래에 걸리는 계좌 안전장치(CB② · ProfitGuard) 상호작용 — 21일 재생. 읽기 전용.

엔진 채점(가상 2계약)은 이 장치들을 모른다. 실거래는 안다 — 그 차이를 잰다.
  CB②  : 청산 포지션 pnl ≤ 0 (본전청산 포함) 3연속 → 당일 신규 진입 정지 (`circuit_breaker.record_stop_loss`)
  PG    : 실제 임계는 `data/profit_guard_prefs.json`(645차 사용자 결정 — L1 150만/35% · Tier4 400만 ·
          L3 13시 이후 누적 ≥ 200만이면 오후 최대 2건 · L4 누적 ≥ 100만에서 3연속 손실)에서 읽는다.
          L4 는 누적이 문턱 아래로 내려가면 연패 카운터를 0 으로 되돌린다(`profit_guard._ProfitCB`).
수량 = 실주문 X% 규칙(min(3, floor(3,000만×7% ÷ (0.6×ATR×5만))), 최소 1). 손익 = 엔진 pt × 수량 × 5만(CYBOS 요율 근사).
⚠ 근사다 — 실거래는 체결가·요율(CREON)·철회 신호가 다르다. 규모를 보려는 계측이다.
사용: 저장소 루트에서 python "docs/신동거래_V4/V4구현_재현검증_20261024/guard_interaction.py"
"""
import datetime as dt
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while not os.path.isdir(os.path.join(ROOT, "strategy")):
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, ROOT)
os.chdir(ROOT)
from config import capital as C                                               # noqa: E402
from strategy.shindong import engine as E, families as F, runner, spec as S   # noqa: E402
from strategy.shindong.calendar import select_flow_product                    # noqa: E402
import json                                                                   # noqa: E402

DB = "data/db/"
DAYS = sorted(json.load(open(os.path.join(HERE, "..", "V22_V3_반사실_20261024", "v4_compare.json"), encoding="utf-8"))["V4"])


def day_trades(d, fam):
    prod, _, _ = select_flow_product(dt.date.fromisoformat(d))
    cd, fl, lr = runner.load_inputs(d, prod, DB + "raw_data.db", DB + "option_flow.db", DB + "premarket_levels.db")
    D, L = E.DayFrame(cd, fl, fx=runner.load_fx(d, DB + "raw_data.db")), E.prepare_levels(lr)
    atr = L["0850"]["atr14"]
    q = min(3, C.shindong_risk_qty(atr) or 1)
    out = [(t["entry_ts"], t["exit_ts"], E.trade_net(t) / 2 / S.PT_VALUE_KRW * q * S.PT_VALUE_KRW)
           for t in F.run_family_day(D, L, fam)["trades"] if t["status"] == "CLOSED"]
    return out, q


PG = json.load(open("data/profit_guard_prefs.json", encoding="utf-8"))["config"]
from config.settings import CB_CONSEC_STOP_LIMIT                              # noqa: E402
TIER_HALT = min(t[0] for t in PG["profit_tiers"] if t[2] == 0)


def apply_guards(trs, cb2=True, pg=True):
    cum = peak = 0.0
    consec0 = 0          # CB② — pnl ≤ 0 연속
    pg_consec = 0        # L4 — 손실 연속
    aft = 0
    kept, why = [], None
    for ent, ex, krw in trs:
        if why:
            break
        if pg and int(ent[:2]) >= PG["afternoon_cutoff_hour"] and cum >= PG["afternoon_min_pnl_krw"]:
            if aft >= PG["afternoon_max_trades"]:
                why = "PG L3(오후 %d건) %s" % (PG["afternoon_max_trades"], ent)
                break
        if pg and int(ent[:2]) >= PG["afternoon_cutoff_hour"]:
            aft += 1
        kept.append(krw)
        cum += krw
        peak = max(peak, cum)
        consec0 = consec0 + 1 if krw <= 0 else 0
        if cum < PG["profit_cb_min_pnl_krw"]:
            pg_consec = 0
        else:
            pg_consec = pg_consec + 1 if krw < 0 else 0
        if cb2 and consec0 >= CB_CONSEC_STOP_LIMIT:
            why = "CB② %s" % ex
        elif pg and peak >= PG["trail_activation_krw"] and cum <= peak * (1 - PG["trail_ratio"]):
            why = "PG L1 %s" % ex
        elif pg and cum >= TIER_HALT:
            why = "PG Tier4 %s" % ex
        elif pg and pg_consec >= PG["profit_cb_consec_loss"]:
            why = "PG L4 %s" % ex
    return sum(kept), len(kept), why


tot = {}
print("| 날짜 | 수량 | 규칙 | 엔진(가드 없음) | CB②만 | CB②+PG | 멈춘 이유 |")
print("|---|---|---|---|---|---|---|")
for fam in ("hybr60", "v4"):
    t0 = t1 = t2 = 0.0
    for d in DAYS:
        trs, q = day_trades(d, fam)
        raw = sum(x[2] for x in trs)
        a, _, wa = apply_guards(trs, cb2=True, pg=False)
        b, _, wb = apply_guards(trs, cb2=True, pg=True)
        t0, t1, t2 = t0 + raw, t1 + a, t2 + b
        if wa or wb:
            print("| %s | %d | %s | %+.1f만 | %+.1f만 | %+.1f만 | %s |" % (d[5:], q, "V3" if fam == "hybr60" else "V4",
                                                                  raw / 1e4, a / 1e4, b / 1e4, wb or wa))
    tot[fam] = (t0, t1, t2)
print()
for fam, (a, b, c) in tot.items():
    print("%s 21일 합계: 가드 없음 %+.1f만 · CB②만 %+.1f만 · CB②+PG %+.1f만" % ("V3" if fam == "hybr60" else "V4",
                                                                          a / 1e4, b / 1e4, c / 1e4))
