# -*- coding: utf-8 -*-
"""[MW0601 2026-10-26] 갭 분기 운영안 반사실 (읽기 전용, 장후 전용). py310_64.

안: 08:45 시가 갭 < 0 → SHADOW_F2 + 갭 반대 방향(매수) R3 스킵 / 갭 > 0 → MAIN(F2X).
엔진 원본은 건드리지 않는다 — 소스 사본에 「R3 방향 금지」 한 줄을 끼워 별도 모듈로 실행한다
(치환 1회 검사 — 2026-10-26 MAIN+F2 치환 무음 실패 교훈).
"""
import sys, os, json, sqlite3, types, datetime as dt
ROOT = r"C:\Users\82108\PycharmProjects\futures"; sys.path.insert(0, ROOT)
from utils.dll_bootstrap import ensure_conda_dll_path
ensure_conda_dll_path()
from utils.analysis_db import guard_intraday
guard_intraday("gap_switch_sim")
import numpy as np
from strategy.shindong import engine as E0, runner
from strategy.shindong.calendar import select_flow_product

src = open(E0.__file__, encoding="utf-8").read()
a = "            if side != trend:\n                continue\n"
b = a + "        if R3_BAN_SIDE and side == R3_BAN_SIDE:\n            continue\n"
assert src.count(a) == 1
src = src.replace(a, b)
a2 = "        if f2x_dir is not None:\n            # [v4"
assert src.count(a2) == 1
# F2 가 꺼진 변형(MAIN)에서도 금지가 걸리도록 F2X 앞에 한 번 더(F2 변형은 위에서 이미 걸러져 중복 무해)
src = src.replace(a2, "        if R3_BAN_SIDE and side == R3_BAN_SIDE:\n            continue\n" + a2)
E = types.ModuleType("engine_gapsw"); E.__dict__["R3_BAN_SIDE"] = 0
exec(compile(src, "engine_gapsw", "exec"), E.__dict__)

DB = os.path.join(ROOT, "data", "db"); P = [os.path.join(DB, x) for x in ("raw_data.db", "option_flow.db", "premarket_levels.db")]
D = json.load(open(os.path.join(os.path.dirname(__file__), "..", "데이터", "F2_F2X_전후_거래_22일.json"), encoding="utf-8"))["days"]

con = sqlite3.connect("file:" + os.path.join(DB, "regular_candles.db") + "?mode=ro", uri=True)
def gap(d0):
    o = con.execute("select open from regular_candles where code='10100' and trade_date=? order by ts limit 1", (d0,)).fetchone()[0]
    pc = con.execute("select close from regular_candles where code='10100' and trade_date<? order by ts desc limit 1", (d0,)).fetchone()[0]
    return (o / pc - 1) * 100

def net(d, L, v, ban=0):
    E.__dict__["R3_BAN_SIDE"] = ban
    r = E.run_day(d, L, v)
    E.__dict__["R3_BAN_SIDE"] = 0
    return sum(E.trade_net(x) for x in r["trades"] if x["status"] == "CLOSED") / 1e4, len(r["trades"])

rows = []
for d0 in D:
    prod = select_flow_product(dt.date.fromisoformat(d0))[0]
    c, f, l = runner.load_inputs(d0, prod, *P)
    L = E.prepare_levels(l); d = E.DayFrame(c, f)
    g = gap(d0)
    r = dict(d=d0, gap=g,
             MAIN=net(d, L, "MAIN")[0], F2=net(d, L, "SHADOW_F2")[0], V3=net(d, L, "SHADOW_V3")[0],
             F2_noBuy=net(d, L, "SHADOW_F2", ban=1)[0], MAIN_noBuy=net(d, L, "MAIN", ban=1)[0],
             F2_noSell=net(d, L, "SHADOW_F2", ban=-1)[0], MAIN_noSell=net(d, L, "MAIN", ban=-1)[0])
    rows.append(r)

def plan(r, th, down, up, flat="MAIN"):
    if r["gap"] <= -th: return r[down]
    if r["gap"] >= th: return r[up]
    return r[flat]

def stat(xs):
    xs = np.array(xs); cum = np.cumsum(xs); dd = (cum - np.maximum.accumulate(np.r_[0, cum])[1:]).min()
    return "%+7.1f | 최악 %+6.1f | MDD %+6.1f | 이긴날 %2d | 효율 %.2f | 최고일 빼면 %+7.1f" % (
        xs.sum(), xs.min(), min(dd, 0), (xs > 0).sum(), xs.sum() / np.abs(xs).sum(), xs.sum() - xs.max())

print("날짜  갭%   MAIN(F2X)  F2  F2-매수R3스킵  V3")
for r in rows:
    print("%s %+5.2f %+7.1f %+7.1f %+7.1f %+7.1f" % (r["d"][5:], r["gap"], r["MAIN"], r["F2"], r["F2_noBuy"], r["V3"]))
cases = [
    ("항상 MAIN(F2X, v4)", lambda r: r["MAIN"]),
    ("항상 F2", lambda r: r["F2"]),
    ("항상 SHADOW_V3(구 MAIN)", lambda r: r["V3"]),
]
for th in (0.0, 0.5):
    cases += [
        ("[안] 갭≤−%.1f: F2+매수R3스킵 / 갭≥+%.1f: MAIN" % (th, th), lambda r, th=th: plan(r, th if th else 1e-9, "F2_noBuy", "MAIN")),
        ("  갭≤−%.1f: F2(스킵 없음) / 그 밖 MAIN" % th, lambda r, th=th: plan(r, th if th else 1e-9, "F2", "MAIN")),
        ("  갭≤−%.1f: MAIN+매수R3스킵 / 그 밖 MAIN" % th, lambda r, th=th: plan(r, th if th else 1e-9, "MAIN_noBuy", "MAIN")),
        ("  대칭: 갭↓ F2+매수스킵 / 갭↑ MAIN+매도스킵" + (" (±%.1f)" % th), lambda r, th=th: plan(r, th if th else 1e-9, "F2_noBuy", "MAIN_noSell")),
    ]
for name, fn in cases:
    print("%-48s %s" % (name, stat([fn(r) for r in rows])))
# 갭하락일만
dn = [r for r in rows if r["gap"] < 0]
print("\n갭하락일 %d일: MAIN %+.1f · F2 %+.1f · F2+매수스킵 %+.1f · MAIN+매수스킵 %+.1f · V3 %+.1f" % (
    len(dn), sum(r["MAIN"] for r in dn), sum(r["F2"] for r in dn), sum(r["F2_noBuy"] for r in dn), sum(r["MAIN_noBuy"] for r in dn), sum(r["V3"] for r in dn)))
up = [r for r in rows if r["gap"] > 0]
print("갭상승일 %d일: MAIN %+.1f · F2 %+.1f · MAIN+매도스킵 %+.1f · V3 %+.1f" % (
    len(up), sum(r["MAIN"] for r in up), sum(r["F2"] for r in up), sum(r["MAIN_noSell"] for r in up), sum(r["V3"] for r in up)))
# 부트스트랩: 안 − 항상 MAIN
rng = np.random.default_rng(0)
diff = np.array([plan(r, 1e-9, "F2_noBuy", "MAIN") - r["MAIN"] for r in rows])
bs = [rng.choice(diff, len(diff)).sum() for _ in range(20000)]
print("안−항상MAIN 차 합 %+.1f · 부트스트랩 P(>0) %.2f · 차 기여 상위 3일 %s" % (
    diff.sum(), np.mean(np.array(bs) > 0), sorted([(round(x, 1), r["d"][5:]) for x, r in zip(diff, rows)], reverse=True)[:3]))
json.dump(rows, open(os.path.join(os.path.dirname(__file__), "..", "데이터", "갭분기_반사실_22일.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
