import csv, collections
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import _paths  # 저장소 경로·PC별 출력 폴더 (README.md)

def rd(n): return list(csv.DictReader(open(_paths.out("inventory_%s.csv" % n), encoding="utf-8")))

rc = rd("raw_candles")
FULL = 369  # 09:00-15:08 분 수
def era(d): return "backfill" if d < "2026-04-28" else "live"
print("== raw_candles: days", len(rc), rc[0]["date"], "->", rc[-1]["date"])
by = collections.defaultdict(lambda: collections.Counter())
for r in rc:
    n = int(r["bars_0900_1508"]); e = era(r["date"])
    by[e]["days"] += 1
    by[e]["full>=95%"] += n >= 0.95 * FULL
    by[e]["partial50-95%"] += 0.5 * FULL <= n < 0.95 * FULL
    by[e]["<50%"] += n < 0.5 * FULL
    by[e]["recovered_days"] += int(r["recovered"] or 0) > 0
    by[e]["anchor_days"] += int(r["anchor_rows"] or 0) > 0
for e, c in by.items(): print(" ", e, dict(c))
months = collections.Counter(r["date"][:7] for r in rc)
print("  by month", sorted(months.items()))
short = [(r["date"], r["bars_0900_1508"], r["first"], r["last"]) for r in rc if int(r["bars_0900_1508"]) < 0.95 * FULL]
print("  short days(<95%)", len(short), short[:40])

rg = rd("regular_candles")
codes = collections.defaultdict(list)
for r in rg: codes[r["code"]].append((r["trade_date"], int(r["bars"])))
for c, v in codes.items():
    full = sum(1 for _, b in v if b >= 380)
    print("== regular", c, "days", len(v), v[0][0], "->", v[-1][0], "full(>=380 bars)", full,
          "median bars", sorted(b for _, b in v)[len(v)//2])
    print("   by year", sorted(collections.Counter(d[:4] for d, _ in v).items()))

for name, key in [("session_bars", "session"), ("investor_futures", "src"), ("program_trade", "market"),
                  ("option_flow", "product"), ("option_book", "book")]:
    rows = rd(name)
    days = sorted(set(r["date"] for r in rows))
    cat = collections.defaultdict(set)
    for r in rows: cat[r[key]].add(r["date"])
    print("==", name, "days", len(days), days[0] if days else None, "->", days[-1] if days else None)
    for k, s in sorted(cat.items()):
        s = sorted(s); print("   ", k, len(s), s[0], "->", s[-1])

for name in ["raw_features", "regime_history"]:
    rows = rd(name)
    print("==", name, "days", len(rows), rows[0]["date"], "->", rows[-1]["date"])
