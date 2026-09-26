# -*- coding: utf-8 -*-
import sys, os, re, glob
sys.path.insert(0, 'C:/Users/82108/PycharmProjects/futures')
from utils.dll_bootstrap import ensure_conda_dll_path; ensure_conda_dll_path()
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(os.path.dirname(HERE), 'GP_test')   # [MW0601 631차] pkl/npy 캐시 — 커밋 제외(GP_test/.gitignore)
os.makedirs(CACHE, exist_ok=True)
pat = re.compile(r'^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) \[INFO\] DATA: \[DivergencePanel\].*?futures\(fi=([+-]?\d+) rt=([+-]?\d+) inst=([+-]?\d+)\) call\(fi=([+-]?\d+) rt=([+-]?\d+)\) put\(fi=([+-]?\d+) rt=([+-]?\d+)\).*?program\(arb=([+-]?\d+) nonarb=([+-]?\d+)')
rows = []
for f in sorted(glob.glob('C:/Users/82108/PycharmProjects/futures/logs/*_DATA.log')):
    with open(f, encoding='cp949', errors='ignore') as fh:
        for line in fh:
            m = pat.match(line)
            if m:
                rows.append([m.group(1)] + [int(x) for x in m.groups()[1:]])
L = pd.DataFrame(rows, columns=['ts','fi_fut','rt_fut','inst_fut','fi_call','rt_call','fi_put','rt_put','arb','nonarb'])
L['dt'] = pd.to_datetime(L.ts).dt.floor('min')
L = L.drop_duplicates('dt', keep='last').set_index('dt').drop(columns='ts')
L.to_pickle(os.path.join(CACHE, 'divpanel.pkl'))
print('divpanel', len(L), L.index.min(), L.index.max(), 'days', L.index.normalize().nunique())
