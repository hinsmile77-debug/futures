# -*- coding: utf-8 -*-
"""DivergencePanel 전량 파서 v2 — 월별 아카이브 ZIP 포함.

v1(parse_logs.py) 대비 두 가지를 고친다.
  (1) logs/*_DATA.log 만 훑어 월별 아카이브 logs/YYYYMM_DATA.zip 을 통째로 놓쳤다.
  (2) 정규식이 program(arb= nonarb=) 신형식만 받아, 2026-08-04 이전 구형식
      program(fi= rt= inst=) 라인을 전부 탈락시켰다.
결과: 개인 콜/풋 표본이 23일 → 실측 가용일 전량으로 확대된다.
"""
import sys, os, re, glob, zipfile
import pandas as pd

ROOT = 'C:/Users/82108/PycharmProjects/futures'
if not os.path.isdir(ROOT):                     # Cowork 리눅스 VM 마운트 경로 대체
    ROOT = os.path.expanduser('~/mnt/futures')
LOGS = os.path.join(ROOT, 'logs')
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(os.path.dirname(HERE), 'GP_test')   # [MW0601 631차] pkl/npy 캐시 — 커밋 제외(GP_test/.gitignore)
os.makedirs(CACHE, exist_ok=True)

# 공통 앞부분 + program 블록은 신/구 형식 모두 허용
PAT = re.compile(
    r'^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) \[INFO\] DATA: \[DivergencePanel\]'
    r'.*?status=(\w+)'
    r'.*?futures\(fi=([+-]?\d+) rt=([+-]?\d+) inst=([+-]?\d+)\)'
    r'.*?call\(fi=([+-]?\d+) rt=([+-]?\d+)\)'
    r'.*?put\(fi=([+-]?\d+) rt=([+-]?\d+)\)'
    r'(?:.*?program\((?:arb=([+-]?\d+) nonarb=([+-]?\d+)|fi=([+-]?\d+) rt=([+-]?\d+) inst=([+-]?\d+)))?'
)

COLS = ['ts', 'status', 'fi_fut', 'rt_fut', 'inst_fut',
        'fi_call', 'rt_call', 'fi_put', 'rt_put', 'arb', 'nonarb', 'prog_fi']


def _scan(lines, src, rows):
    for line in lines:
        m = PAT.match(line)
        if not m:
            continue
        g = m.groups()
        arb    = int(g[9])  if g[9]  is not None else None
        nonarb = int(g[10]) if g[10] is not None else None
        progfi = int(g[11]) if g[11] is not None else None   # 구형식 program(fi=) = 비차익 대용
        rows.append([g[0], g[1]] + [int(x) for x in g[2:9]] + [arb, nonarb, progfi, src])


def main():
    rows = []
    for f in sorted(glob.glob(os.path.join(LOGS, '*_DATA.log'))):
        with open(f, encoding='cp949', errors='ignore') as fh:
            _scan(fh, 'loose', rows)
    for zf in sorted(glob.glob(os.path.join(LOGS, '*_DATA.zip'))):
        z = zipfile.ZipFile(zf)
        for n in sorted(z.namelist()):
            _scan(z.read(n).decode('cp949', 'replace').splitlines(), 'zip:' + os.path.basename(zf), rows)

    L = pd.DataFrame(rows, columns=COLS + ['src'])
    L['dt'] = pd.to_datetime(L.ts).dt.floor('min')
    # 같은 분이 loose/zip 양쪽에 있으면 loose(원본) 우선
    L['_pri'] = (L.src == 'loose').astype(int)
    L = (L.sort_values(['dt', '_pri'])
           .drop_duplicates('dt', keep='last')
           .set_index('dt').drop(columns=['ts', '_pri']))
    L.to_pickle(os.path.join(CACHE, 'divpanel_full.pkl'))

    # ── 커버리지 리포트 ────────────────────────────────────────────
    d = L.copy()
    d['day'] = d.index.normalize()
    live = (d[['rt_call', 'rt_put', 'rt_fut']].abs().sum(axis=1) > 0)
    g = d.assign(live=live).groupby('day').agg(
        rows=('status', 'size'),
        live=('live', 'sum'),
        ok=('status', lambda s: (s != 'unavailable').sum()),
        src=('src', lambda s: s.iloc[-1]),
    )
    usable = g[g.live >= 60]
    print('divpanel_full  rows=%d  %s ~ %s  days=%d' % (len(L), L.index.min(), L.index.max(), g.shape[0]))
    print('가용일(분당 live ≥60분): %d일  %s ~ %s'
          % (len(usable), usable.index.min().date(), usable.index.max().date()))
    print()
    print('월별 가용일수:')
    print(usable.groupby(usable.index.to_period('M')).size().to_string())
    print()
    print('가용일 목록(일자, live분, 출처):')
    for day, r in usable.iterrows():
        print('  %s  live=%4d / rows=%4d  %s' % (day.date(), r.live, r.rows, r.src))


if __name__ == '__main__':
    main()
