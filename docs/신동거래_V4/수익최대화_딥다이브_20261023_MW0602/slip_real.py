# -*- coding: utf-8 -*-
"""실거래 신동 체결 vs 엔진 규칙가 — 진입·청산 슬리피지 실측(청산 사유별). 읽기 전용.
엔진 규칙가 = shindong.db MAIN 행(그날 라이브 버전) · 실체결 = trades.db entry_source='SHINDONG' 평균가.
슬리피지(pt) = 불리한 방향 + (매수 진입은 체결 − 규칙, 매도 진입은 규칙 − 체결 · 청산은 반대)."""
import sqlite3, datetime as dt, json, os, statistics as st
sd = sqlite3.connect("file:data/db/shindong.db?mode=ro", uri=True); sd.row_factory = sqlite3.Row
td = sqlite3.connect("file:data/db/trades.db?mode=ro", uri=True); td.row_factory = sqlite3.Row
rows = []
for r in td.execute("select * from trades where entry_source='SHINDONG' order by entry_ts"):
    day = r["entry_ts"][:10]; side = 1 if r["direction"] == "LONG" else -1
    sent = dt.datetime.strptime(r["entry_ts"][:19], "%Y-%m-%d %H:%M:%S")
    best = None
    for e in sd.execute("select * from shindong_trades where trade_date=? and variant='MAIN' and status='CLOSED'", (day,)):
        et = dt.datetime.strptime(day + " " + str(e["entry_ts"])[11:16], "%Y-%m-%d %H:%M")
        gap = (sent - et).total_seconds()
        if int(e["side"]) == side and 0 <= gap <= 180 and (best is None or gap < best[0]):
            best = (gap, e)
    if not best:
        rows.append(dict(day=day, side=side, miss=True)); continue
    e = best[1]
    ent_slip = side * (r["entry_price"] - e["entry_px"])
    ex_slip = side * (e["leg1_exit_px"] - r["exit_price"])
    rows.append(dict(day=day, t=r["entry_ts"][11:16], side=side, qty=r["entry_qty"], why=e["leg1_reason"], rule_e=e["entry_px"],
                     fill_e=r["entry_price"], ent=ent_slip, rule_x=e["leg1_exit_px"], fill_x=r["exit_price"], ex=ex_slip,
                     rule_xt=str(e["leg1_exit_ts"])[11:16] if e["leg1_exit_ts"] else None, fill_xt=r["exit_ts"][11:16]))
print("| 날짜 | 진입 | 방향 | 수량 | 엔진 청산사유 | 진입 규칙→체결 | 진입 슬립 | 청산 규칙→체결 | 청산 슬립 | 청산 시각 규칙/체결 |")
print("|---|---|---|---|---|---|---|---|---|---|")
for x in rows:
    if x.get("miss"):
        print("| %s | ? | %s | | 엔진 행 매칭 실패 | | | | | |" % (x["day"][5:], x["side"])); continue
    print("| %s | %s | %s | %s | %s | %.2f→%.2f | %+.2f | %.2f→%.2f | %+.2f | %s / %s |" % (
        x["day"][5:], x["t"], "매수" if x["side"] > 0 else "매도", x["qty"], x["why"], x["rule_e"], x["fill_e"], x["ent"],
        x["rule_x"], x["fill_x"], x["ex"], x["rule_xt"], x["fill_xt"]))
ok = [x for x in rows if not x.get("miss")]
print("\n청산 슬립(+ = 불리) 사유별:")
for w in sorted(set(x["why"] for x in ok)):
    xs = [x["ex"] for x in ok if x["why"] == w]
    print("  %-5s n=%d 평균 %+.2f 중앙 %+.2f 최악 %+.2f" % (w, len(xs), st.mean(xs), st.median(xs), max(xs)))
stop = [x["ex"] for x in ok if x["why"] in ("TR", "SL")]
print("  스톱형(TR+SL) n=%d 평균 %+.2f 중앙 %+.2f 최악 %+.2f · 1pt 초과 %d건" % (len(stop), st.mean(stop), st.median(stop), max(stop), sum(s > 1 for s in stop)))
print("진입 슬립 n=%d 평균 %+.2f 중앙 %+.2f 최악 %+.2f" % (len(ok), st.mean(x["ent"] for x in ok), st.median(x["ent"] for x in ok), max(x["ent"] for x in ok)))
