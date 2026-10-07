# -*- coding: utf-8 -*-
"""피터2 재생 — 보관된 트윗(`_raw`)과 미니 1분봉으로 「그날 실시간 추종했다면」을 다시 돈다.

무엇에 쓰나
    1) 해석기·상태기계 회귀 확인(코드를 고친 뒤 과거 날짜가 그대로 나오는가)
    2) 장후 복기의 「섀도」 열 — 실추종과 같은 규칙을 지연·체결 가정만 고정해 돌린다
    3) 사전등록 근거 — 지연을 바꿔 가며 추종 효율이 얼마나 깎이는지

가정(정직하게 적는다 — 실측이 아니다)
    · 트윗은 게시 시각 + `--latency`초(기본 20초)에 받는다.
    · 봉 하나를 네 점으로 걷는다: 시가 → (양봉이면 저가→고가, 음봉이면 고가→저가) → 종가,
      각 15초 간격. 봉 안의 실제 순서는 모른다.
    · 진입·청산은 그 점의 가격에 체결된다(슬리피지 0). 손절·목표는 그 가격에 정확히 체결된다.
    · 오프셋은 라이브와 같게 **직전 실측일** 값을 쓴다.
    ⚠ 미륵이 자동매매와의 충돌(미륵이 보유 중 건너뜀)은 재현하지 않는다 — 피터2 단독이다.

읽기 전용. 장중 실행 금지(456차) — 라이브 DB 를 스캔한다.

실행
    python tools/peter2_replay.py 2026-10-07
    python tools/peter2_replay.py 2026-08-03 2026-10-07 --latency 30
"""
import argparse
import datetime
import io
import json
import os
import sqlite3
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from strategy.peter2 import store                     # noqa: E402
from strategy.peter2.follower import Peter2Follower   # noqa: E402

RAW_DB = os.path.join(_ROOT, 'data', 'db', 'raw_data.db')


def load_bars(date):
    con = sqlite3.connect('file:%s?mode=ro' % RAW_DB.replace('\\', '/'), uri=True)
    try:
        rows = con.execute("SELECT ts, open, high, low, close FROM raw_candles "
                           "WHERE ts >= ? AND ts < ? ORDER BY ts",
                           ('%s 09:00:00' % date, '%s 15:11:00' % date)).fetchall()
    finally:
        con.close()
    return rows


def load_tweets(date):
    p = store.raw_path(date)
    if not os.path.exists(p):
        return []
    out = []
    with io.open(p, encoding='utf-8') as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                try:
                    out.append(json.loads(ln))
                except ValueError:
                    pass
    out.sort(key=lambda r: r.get('dt') or '')
    return out


def path_points(bars):
    """(datetime, price) 열."""
    pts = []
    for ts, o, h, l, c in bars:
        t0 = datetime.datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')
        mid = (l, h) if c >= o else (h, l)
        for i, p in enumerate((o, mid[0], mid[1], c)):
            pts.append((t0 + datetime.timedelta(seconds=15 * i), float(p)))
    return pts


def replay_day(date, latency=20, offset=None, cfg=None, verbose=False):
    bars = load_bars(date)
    tweets = load_tweets(date)
    if not bars:
        return {'date': date, 'skip': 'no_bars'}
    off, src, safe = store.load_offset(date)
    if offset is not None:
        off, src, safe = offset, 'arg', True
    if off is None:
        return {'date': date, 'skip': 'no_offset(%s)' % src}
    fw = Peter2Follower(date, off, src, True, cfg=cfg)   # 재생은 만기 가드를 끈다(규칙 검증이 목적)
    q = []
    for t in tweets:
        tt = store.tweet_kst(t.get('dt'))
        if tt is not None and tt.date().isoformat() == date:
            q.append((tt + datetime.timedelta(seconds=latency), t))
    pos = None
    trades = []
    log = []

    def eng(price):
        return {'status': ('LONG' if pos and pos['side'] == 'LONG' else
                           'SHORT' if pos else 'FLAT'),
                'source': 'PETER2' if pos else None, 'pending': False, 'price': price,
                'stop': pos['stop'] if pos else None, 'target': pos['target'] if pos else None}

    def close(now, px, why):
        nonlocal pos
        pnl = (px - pos['entry']) if pos['side'] == 'LONG' else (pos['entry'] - px)
        trades.append(dict(pos, exit=px, exit_t=now.strftime('%H:%M:%S'), why=why,
                           pnl=round(pnl, 2)))
        fw.on_peter2_closed(pnl, now)
        pos = None

    def apply(intents, now, px):
        nonlocal pos
        for it in intents:
            if it['type'] == 'ENTER' and pos is None:
                pos = {'side': it['side'], 'entry': px, 'stop': it['stop'], 'target': it['target'],
                       'entry_t': now.strftime('%H:%M:%S'), 'sig': it['sig'],
                       'stop_src': it.get('stop_src')}
                fw.mark_entered()
                log.append('%s ENTER %s @%.2f stop %.2f tgt %s  (%s)' % (
                    now.strftime('%H:%M:%S'), it['side'], px, it['stop'], it['target'], it['why']))
            elif it['type'] == 'SET_STOP' and pos:
                pos['stop'] = it['stop']
                log.append('%s SET_STOP %.2f (%s)' % (now.strftime('%H:%M:%S'), it['stop'], it['why']))
            elif it['type'] == 'SET_TARGET' and pos:
                pos['target'] = it['target']
                log.append('%s SET_TARGET %.2f' % (now.strftime('%H:%M:%S'), it['target']))
            elif it['type'] == 'EXIT' and pos:
                log.append('%s EXIT %s @%.2f' % (now.strftime('%H:%M:%S'), it['reason'], px))
                close(now, px, it['reason'])

    qi = 0
    for now, px in path_points(bars):
        while qi < len(q) and q[qi][0] <= now:
            apply(fw.ingest(q[qi][1], eng(px), q[qi][0]), now, px)
            qi += 1
        if pos:
            if (pos['side'] == 'LONG' and px <= pos['stop']) or (pos['side'] == 'SHORT' and px >= pos['stop']):
                log.append('%s STOP @%.2f' % (now.strftime('%H:%M:%S'), pos['stop']))
                close(now, pos['stop'], '피터2손절')
            elif pos['target'] is not None and (
                    (pos['side'] == 'LONG' and px >= pos['target']) or
                    (pos['side'] == 'SHORT' and px <= pos['target'])):
                log.append('%s TARGET @%.2f' % (now.strftime('%H:%M:%S'), pos['target']))
                close(now, pos['target'], '피터2청산가')
        apply(fw.on_price(eng(px), now), now, px)
        if pos and now.strftime('%H:%M') >= '15:10':
            close(now, px, '15:10 강제청산')
        for e in fw.events:
            if e['kind'] in ('ARM', 'REJECT', 'EXPIRE', 'DISARM', 'HALT', 'CONFIRM'):
                log.append('%s %s %s' % (e['hm'], e['kind'],
                                         {k: v for k, v in e.items() if k not in ('kind', 'hm')}))
        fw.events = []
    if pos:
        close(now, px, '종료')
    peter_pts = 0.0
    for x in fw.peter_trades:
        if x['exit'] is not None:
            peter_pts += (x['exit'] - x['entry']) if x['side'] == 'L' else (x['entry'] - x['exit'])
    res = {'date': date, 'offset': off, 'trades': trades,
           'follow_pts': round(sum(t['pnl'] for t in trades), 2),
           'peter_pts': round(peter_pts, 2), 'peter_tr': fw.peter_tr_text(), 'log': log}
    if verbose:
        print('===== %s  offset %+.2f (%s)' % (date, off, src))
        for l in log:
            print('  ' + l)
        print('  -- 피터 거래줄(피터가) --')
        for l in res['peter_tr'].splitlines():
            print('    ' + l)
        print('  피터 %+.2fpt · 추종 %+.2fpt (%d건)' % (res['peter_pts'], res['follow_pts'], len(trades)))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('start')
    ap.add_argument('end', nargs='?')
    ap.add_argument('--latency', type=int, default=20)
    ap.add_argument('-q', '--quiet', action='store_true')
    a = ap.parse_args()
    try:
        from utils.analysis_db import guard_intraday
        guard_intraday('peter2_replay')
    except ImportError:
        pass
    d0 = datetime.date.fromisoformat(a.start)
    d1 = datetime.date.fromisoformat(a.end) if a.end else d0
    tot_p = tot_f = 0.0
    n = 0
    rows = []
    d = d0
    while d <= d1:
        if d.weekday() < 5 and os.path.exists(store.raw_path(d.isoformat())):
            r = replay_day(d.isoformat(), a.latency, verbose=not a.quiet)
            if 'skip' not in r:
                tot_p += r['peter_pts']
                tot_f += r['follow_pts']
                n += len(r['trades'])
                rows.append(r)
        d += datetime.timedelta(days=1)
    print('\n일자 | 피터pt | 추종pt | 추종건수')
    for r in rows:
        print('%s | %+6.2f | %+6.2f | %d' % (r['date'], r['peter_pts'], r['follow_pts'], len(r['trades'])))
    print('합계  피터 %+.2fpt · 추종 %+.2fpt · 추종 %d건 · 효율 %s' % (
        tot_p, tot_f, n, ('%.2f' % (tot_f / tot_p)) if tot_p else 'n/a'))


if __name__ == '__main__':
    main()
