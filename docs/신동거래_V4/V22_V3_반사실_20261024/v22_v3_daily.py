# -*- coding: utf-8 -*-
"""9/21 이후 일별 — 라이브 적용현황(기록 · 실거래) vs V2.2 반사실 vs V3 반사실. 읽기 전용(DB 미기록).

반사실 = 공식 엔진 `families.run_family_day` 를 그날 봉·흐름·맥점으로 다시 돌린 값
  V2.2 = family "flowc"(= SHADOW_V22) · V3 = family "hybr60"(= MAIN v3) · 참고 V2.1 = flowc 에서 R1 가드 끔
손익 = 엔진 규격(가상 2계약 · CYBOS 요율 · 1틱). pt 는 계약당(net ÷ 5만 ÷ 2).
기록 = shindong.db MAIN(그날 라이브 버전) · SHADOW_V22(10/19~) · 실거래 = trades.db entry_source='SHINDONG'.
"""
import json
import os
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while not os.path.isdir(os.path.join(ROOT, "strategy")):
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, ROOT)
os.chdir(ROOT)
from config.settings import PREMARKET_LEVELS_DB, RAW_DATA_DB, WEEKLY_OPTION_FLOW_DB, SHINDONG_DB   # noqa: E402
from strategy.shindong import daily_report as DR, engine as E, families as F, spec as S          # noqa: E402

FLOW = WEEKLY_OPTION_FLOW_DB if os.path.isabs(WEEKLY_OPTION_FLOW_DB) else os.path.join(ROOT, WEEKLY_OPTION_FLOW_DB)
PTV = S.PT_VALUE_KRW
VER = {"SD-2026-09-24-v1": "v1", "SD-2026-09-30-v2.1": "v2.1", "SD-2026-10-15-v2.2": "v2.2", "SD-2026-10-19-v3": "v3"}
RS = {"TP1": "익절", "TP2": "익절", "TR": "트레일", "SL": "손절", "TIME": "시간", "BE": "본전"}


def ro(p):
    return sqlite3.connect("file:%s?mode=ro" % p.replace("\\", "/"), uri=True)


sd = ro(SHINDONG_DB)
rec = {}
for v in ("MAIN", "SHADOW_V22"):
    for day, sv, net, n in sd.execute(
            "select t.trade_date, d.spec_version, sum(t.net_krw), count(*) from shindong_trades t join shindong_day d "
            "on d.trade_date=t.trade_date and d.variant=t.variant where t.variant=? and t.status='CLOSED' group by 1,2", (v,)):
        rec[(v, day)] = (VER.get(sv, sv), net or 0.0, n)
    for day, sv in sd.execute("select trade_date, spec_version from shindong_day where variant=?", (v,)):
        rec.setdefault((v, day), (VER.get(sv, sv), 0.0, 0))
td = ro(os.path.join(ROOT, "data", "db", "trades.db"))
real = {}
for day, net, n, q in td.execute("select substr(entry_ts,1,10), sum(net_pnl_krw), count(*), group_concat(entry_qty) from trades "
                                 "where entry_source='SHINDONG' group by 1"):
    real[day] = (net or 0.0, n, q)

days = sorted({k[1] for k in rec if k[0] == "MAIN" and k[1] >= "2026-09-21"})


def replay(o, fam, guard=True):
    old = S.FLOW_R1_CTR_REENTRY_BLOCK
    S.FLOW_R1_CTR_REENTRY_BLOCK = guard
    try:
        r = F.run_family_day(o["d"], o["L"], fam)
    finally:
        S.FLOW_R1_CTR_REENTRY_BLOCK = old
    trs = [t for t in r["trades"] if t["status"] == "CLOSED"]
    return dict(net=sum(E.trade_net(t) for t in trs), n=len(trs), win=sum(E.trade_net(t) > 0 for t in trs),
                tr=[(t["entry_ts"], "매수" if t["side"] > 0 else "매도", t.get("rule"), RS.get(t["legs"][0].get("reason"), t["legs"][0].get("reason")),
                     round(E.trade_net(t) / 2 / PTV, 2)) for t in trs], notes=r["decision"].get("notes", []))


rows = []
for day in days:
    o = DR.load_day(day, RAW_DATA_DB, FLOW, PREMARKET_LEVELS_DB)
    if not o.get("ok"):
        continue
    d = o["d"]
    k0 = min(k for k in d.idx if k >= "09:00" and k in d.c)
    act = d.c[d.last_at_or_before(S.TIME_EXIT)] - d.c[k0]
    r22, r3, r21 = replay(o, "flowc", True), replay(o, "hybr60"), replay(o, "flowc", False)
    rows.append(dict(day=day, act=act, bias=F._r1_bias(d)[1], live=rec.get(("MAIN", day)), sh22=rec.get(("SHADOW_V22", day)),
                     real=real.get(day), v22=r22, v3=r3, v21=r21))

json.dump([dict(r, v22=dict(r["v22"], notes=None), v3=dict(r["v3"], notes=None), v21=dict(r["v21"], notes=None)) for r in rows],
          open(os.path.join(HERE, "daily.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)

m = lambda x: format(x / 1e4, "+,.1f")
pt = lambda x: "%+.2f" % (x / 2 / PTV)
print("## 재현 대조 — 반사실 vs 같은 규칙의 라이브 기록")
bad = 0
for r in rows:
    lv = r["live"]
    if lv and lv[0] == "v2.2":
        ok = abs(lv[1] - r["v22"]["net"]) < 1; bad += not ok
        print("  %s 라이브 v2.2 %s만 vs V2.2 반사실 %s만 %s" % (r["day"][5:], m(lv[1]), m(r["v22"]["net"]), "OK" if ok else "❌"))
    if lv and lv[0] == "v3":
        ok = abs(lv[1] - r["v3"]["net"]) < 1; bad += not ok
        print("  %s 라이브 v3 %s만 vs V3 반사실 %s만 %s" % (r["day"][5:], m(lv[1]), m(r["v3"]["net"]), "OK" if ok else "❌"))
    if r["sh22"]:
        ok = abs(r["sh22"][1] - r["v22"]["net"]) < 1; bad += not ok
        print("  %s 섀도 V22 기록 %s만 vs V2.2 반사실 %s만 %s" % (r["day"][5:], m(r["sh22"][1]), m(r["v22"]["net"]), "OK" if ok else "❌"))
    if lv and lv[0] == "v2.1":
        ok = abs(lv[1] - r["v21"]["net"]) < 1; bad += not ok
        print("  %s 라이브 v2.1 %s만 vs V2.1 반사실(가드 끔) %s만 %s" % (r["day"][5:], m(lv[1]), m(r["v21"]["net"]), "OK" if ok else "❌"))
print("  불일치 %d건" % bad)

print("\n## 일별 (가상 2계약 · 만원 / 괄호 = pt/계약)")
print("| 날짜 | 시장(09:00→15:05) | R1 | 라이브 버전 | 라이브 기록 | 실거래(체결) | **V2.2 반사실** | **V3 반사실** | V3−V2.2 |")
print("|---|---|---|---|---|---|---|---|---|")
cum22 = cum3 = 0.0
for r in rows:
    lv, rl = r["live"], r["real"]
    print("| %s | %+.1f | %s | %s | %s | %s | %s (%s) %d/%d | %s (%s) %d/%d | %s |" % (
        r["day"][5:], r["act"], {1: "상방", -1: "하방", 0: "보류"}[r["bias"]], lv[0] if lv else "-",
        (m(lv[1]) + "만") if lv else "-", ("%s만 · %d건 · 수량 %s" % (m(rl[0]), rl[1], rl[2])) if rl else "-",
        m(r["v22"]["net"]), pt(r["v22"]["net"]), r["v22"]["win"], r["v22"]["n"],
        m(r["v3"]["net"]), pt(r["v3"]["net"]), r["v3"]["win"], r["v3"]["n"], m(r["v3"]["net"] - r["v22"]["net"])))


def agg(lab, sel):
    rs = [r for r in rows if sel(r["day"])]
    out = [lab, len(rs)]
    for key in ("v22", "v3"):
        xs = [r[key]["net"] for r in rs]
        n = sum(r[key]["n"] for r in rs); w = sum(r[key]["win"] for r in rs)
        c = p = dd = 0.0
        for x in xs:
            c += x; p = max(p, c); dd = max(dd, p - c)
        out += [sum(xs), w, n, min(xs), dd]
    lv = sum(r["live"][1] for r in rs if r["live"]); rl = sum(r["real"][0] for r in rs if r["real"])
    return out + [lv, rl]


print("\n## 구간 합계")
print("| 구간 | 일수 | V2.2 합계 | 승/거래 | 최악일 | MDD | V3 합계 | 승/거래 | 최악일 | MDD | 라이브 기록 합 | 실거래 합 |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|")
for lab, sel in (("전체 9/21~", lambda d: True), ("v1 라이브 구간 9/21~9/30", lambda d: d <= "2026-09-30"),
                 ("v2.1 라이브 10/01~10/14", lambda d: "2026-10-01" <= d <= "2026-10-14"),
                 ("v2.2 라이브 10/15~10/16", lambda d: "2026-10-15" <= d <= "2026-10-16"),
                 ("v3 라이브 10/19~ (v3 표본 밖)", lambda d: d >= "2026-10-19")):
    a = agg(lab, sel)
    print("| %s | %d | %s만 | %d/%d | %s만 | %s만 | %s만 | %d/%d | %s만 | %s만 | %s만 | %s만 |" % (
        a[0], a[1], m(a[2]), a[3], a[4], m(a[5]), m(-a[6]), m(a[7]), a[8], a[9], m(a[10]), m(-a[11]), m(a[12]), m(a[13])))

print("\n## 거래 내역 (진입시각 · 방향 · 규칙 · 청산 · pt/계약)")
for r in rows:
    print("  %s V2.2 %s" % (r["day"][5:], r["v22"]["tr"]))
    print("        V3   %s" % (r["v3"]["tr"],))
