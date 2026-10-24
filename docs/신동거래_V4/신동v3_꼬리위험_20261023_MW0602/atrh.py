import sqlite3
c=sqlite3.connect('data/db/premarket_levels.db')
rows=c.execute("select date,round(atr14,1),round(0.6*atr14,1),round(0.6*atr14*50000/1e4) from premarket_levels where stage='0850' and date>='2026-09-01' order by date").fetchall()
for r in rows: print(r)
