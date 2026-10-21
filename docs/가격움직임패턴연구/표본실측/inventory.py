"""보유 표본 조사 — 장전 전용(guard_intraday), 읽기전용."""
import sys, time, csv, json
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import _paths  # 저장소 경로·PC별 출력 폴더 (README.md)
from utils.analysis_db import guard_intraday, connect_ro
guard_intraday("sample_inventory")
t0 = time.time()

def q(con, sql):
    return con.execute(sql).fetchall()

def dump(name, header, rows):
    with open(_paths.out("inventory_%s.csv" % name), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)

raw = connect_ro(_paths.db("raw_data.db"))
for t in ["raw_candles", "session_bars", "raw_investor_futures", "raw_program_trade",
          "raw_features", "regime_history", "triple_barrier_labels", "exchange_cb_halts"]:
    print("sample", t, q(raw, "select * from %s order by rowid limit 1" % t)[0][:4] if q(raw, "select 1 from %s limit 1" % t) else "EMPTY")

# 1) raw_candles 일별
rc = q(raw, """select substr(ts,1,10) d, count(*), min(substr(ts,12,5)), max(substr(ts,12,5)),
               sum(case when substr(ts,12,5) between '09:00' and '15:08' then 1 else 0 end),
               sum(coalesce(bar_recovered,0)), sum(case when anchor_buy is not null then 1 else 0 end)
               from raw_candles group by d order by d""")
dump("raw_candles", ["date", "bars", "first", "last", "bars_0900_1508", "recovered", "anchor_rows"], rc)
print("raw_candles days", len(rc), "elapsed", round(time.time() - t0, 1))

# 2) session_bars
sb = q(raw, "select substr(ts,1,10) d, session, count(*) from session_bars group by d, session order by d")
dump("session_bars", ["date", "session", "bars"], sb)

# 3) investor futures by src
inv = q(raw, "select substr(ts,1,10) d, src, count(*) from raw_investor_futures group by d, src order by d")
dump("investor_futures", ["date", "src", "rows"], inv)

# 4) program trade
pt = q(raw, "select substr(ts,1,10) d, market, count(*) from raw_program_trade group by d, market order by d")
dump("program_trade", ["date", "market", "rows"], pt)

# 5) raw_features, regime_history
rf = q(raw, "select substr(ts,1,10) d, count(*) from raw_features group by d order by d")
dump("raw_features", ["date", "rows"], rf)
rh = q(raw, "select substr(ts,1,10) d, count(*) from regime_history group by d order by d")
dump("regime_history", ["date", "rows"], rh)
try:
    tb = q(raw, "select count(*) from triple_barrier_labels")
    print("triple_barrier_labels rows", tb)
except Exception as e:
    print("tbl err", e)
print("cb_halts", q(raw, "select * from exchange_cb_halts"))
raw.close()

# 6) regular_candles
reg = connect_ro(_paths.db("regular_candles.db"))
print("meta", q(reg, "select * from meta"))
rg = q(reg, "select code, trade_date, count(*), min(ts), max(ts) from regular_candles group by code, trade_date order by trade_date")
dump("regular_candles", ["code", "trade_date", "bars", "min_ts", "max_ts"], rg)
print("roll_days", q(reg, "select count(*), min(trade_date), max(trade_date) from roll_days"))
print("cb_halts", q(reg, "select * from cb_halts"))
reg.close()

# 7) option flow
of = connect_ro(_paths.db("option_flow.db"))
ofr = q(of, "select trade_date, product, count(*), min(bar_time), max(bar_time) from option_investor_flow group by trade_date, product order by trade_date")
dump("option_flow", ["date", "product", "rows", "min_bar", "max_bar"], ofr)
of.close()

# 8) option book
ob = connect_ro(_paths.db("option_book.db"))
obr = q(ob, "select substr(ts,1,10) d, book, count(*) from option_book_snap group by d, book order by d")
dump("option_book", ["date", "book", "snaps"], obr)
ob.close()
print("done", round(time.time() - t0, 1), "s")
