import sys, os, time, sqlite3
sys.path.insert(0, 'C:/Users/82108/PycharmProjects/futures')
from utils.dll_bootstrap import ensure_conda_dll_path
ensure_conda_dll_path()
import pandas as pd
t0 = time.time()
raw = 'C:/Users/82108/PycharmProjects/futures/data/db/raw_data.db'
con = sqlite3.connect('file:' + raw + '?mode=ro', uri=True)
c = pd.read_sql_query('SELECT ts,open,high,low,close,volume,bar_recovered FROM raw_candles ORDER BY ts', con)
con.close()
print('rows', len(c), c['ts'].iloc[0], c['ts'].iloc[-1], '%.1fs' % (time.time() - t0))
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'candles.pkl')
c.to_pickle(out)
print('saved', out)
