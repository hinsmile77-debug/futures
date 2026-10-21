import sys
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import _paths  # 저장소 경로·PC별 출력 폴더 (README.md)
from utils.analysis_db import guard_intraday, connect_ro
guard_intraday("sample_inventory_schema")
for db, tabs in [("raw_data.db", ["raw_candles", "session_bars", "raw_investor_futures",
                                  "raw_program_trade", "raw_features", "regime_history"]),
                 ("regular_candles.db", None), ("option_flow.db", None), ("option_book.db", None)]:
    con = connect_ro(_paths.db(db))
    names = [r[0] for r in con.execute("select name from sqlite_master where type='table'")]
    print("==", db, names)
    for t in (tabs or names):
        if t in names:
            cols = [r[1] for r in con.execute("pragma table_info(%s)" % t)]
            idx = [r[1] for r in con.execute("pragma index_list(%s)" % t)]
            print("  ", t, cols[:25], "idx=", idx)
    con.close()
