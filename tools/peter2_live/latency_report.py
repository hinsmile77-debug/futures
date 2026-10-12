# -*- coding: utf-8 -*-
"""[MW0602 615차 후속2] 피터2 수집 지연 리포트 — 읽기 전용.

사전등록 합격선: **트윗 지연 p90 ≤ 90초** (= PETER2_HEARTBEAT_STALE_SEC).
    결과를 보고 문턱을 바꾸지 말 것(§9-4). 미달이면 계획서 B2(전용 X 계정 → 프로필 폴백)로 간다.

입력
    data/peter_feed/_raw/<YYYY-MM-DD>.jsonl   src=live 행의 dt(UTC, 게시) · seen_at(KST, 수신)
    logs/peter2_receiver_<YYYYMMDD>.log       `HH:MM:SS PAGE_ERROR …` 줄
    data/peter2_live/<YYYY-MM-DD>/collector.json  `last_ok` 키 유무 = 후속8 수신기로 돌았나

실행
    python tools/peter2_live/latency_report.py 2026-10-13
    python tools/peter2_live/latency_report.py 2026-10-13 --json
"""
from __future__ import print_function

import argparse
import datetime as D
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P90_LIMIT_SEC = 90
SLOW_SEC = 90
KST = D.timezone(D.timedelta(hours=9))
_ERR_RE = re.compile(r'^(\d\d):(\d\d):(\d\d) PAGE_ERROR')


def _pct(vals, q):
    if not vals:
        return None
    s = sorted(vals)
    k = (len(s) - 1) * q
    lo = int(k)
    hi = min(lo + 1, len(s) - 1)
    return round(s[lo] + (s[hi] - s[lo]) * (k - lo), 1)


def load_tweets(date):
    p = os.path.join(ROOT, 'data', 'peter_feed', '_raw', '%s.jsonl' % date)
    out = []
    if not os.path.exists(p):
        return out
    with io.open(p, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get('src') != 'live' or not r.get('seen_at') or not r.get('dt'):
                continue
            try:
                posted = (D.datetime.fromisoformat(r['dt'].replace('Z', '+00:00'))
                          .astimezone(KST).replace(tzinfo=None))
                seen = D.datetime.fromisoformat(r['seen_at'][:19])
            except ValueError:
                continue
            if posted.date().isoformat() != date:
                continue
            out.append({'posted': posted, 'seen': seen,
                        'lat': int((seen - posted).total_seconds()),
                        'text': (r.get('text') or '').replace('\n', ' ')[:40]})
    out.sort(key=lambda x: x['posted'])
    return out


def load_errors(date):
    p = os.path.join(ROOT, 'logs', 'peter2_receiver_%s.log' % date.replace('-', ''))
    out = []
    if not os.path.exists(p):
        return out, False
    day = D.date.fromisoformat(date)
    with io.open(p, encoding='utf-8', errors='replace') as f:
        for line in f:
            m = _ERR_RE.match(line)
            if m:
                out.append(D.datetime.combine(day, D.time(int(m.group(1)), int(m.group(2)),
                                                          int(m.group(3)))))
    return out, True


def collector_version(date):
    p = os.path.join(ROOT, 'data', 'peter2_live', date, 'collector.json')
    try:
        with io.open(p, encoding='utf-8') as f:
            return 'last_ok' in json.load(f)
    except (OSError, IOError, ValueError):
        return None


def build(date):
    tw = load_tweets(date)
    errs, have_log = load_errors(date)
    lats = [t['lat'] for t in tw]
    win = {}
    for e in errs:
        if D.time(8, 30) <= e.time() <= D.time(15, 45):
            k = '%02d:%02d' % (e.hour, (e.minute // 15) * 15)
            win[k] = win.get(k, 0) + 1
    slow = []
    for t in tw:
        if t['lat'] <= SLOW_SEC:
            continue
        n_err = sum(1 for e in errs if t['posted'] <= e <= t['seen'])
        slow.append({'posted': t['posted'].strftime('%H:%M:%S'), 'lat': t['lat'],
                     'errors_between': n_err, 'text': t['text']})
    p90 = _pct(lats, 0.9)
    verdict = ('INSUFFICIENT' if len(lats) < 10 else
               ('PASS' if p90 <= P90_LIMIT_SEC else 'FAIL'))
    return {'date': date, 'n': len(lats), 'p50': _pct(lats, 0.5), 'p90': p90,
            'max': max(lats) if lats else None, 'p90_limit': P90_LIMIT_SEC,
            'verdict': verdict, 'page_errors': len(errs), 'receiver_log': have_log,
            'collector_has_last_ok': collector_version(date),
            'errors_per_15m': dict(sorted(win.items())), 'slow': slow}


def render(r):
    L = ['# 피터2 수집 지연 — %s' % r['date'], '',
         '| 항목 | 값 |', '|---|---|',
         '| 트윗(live) | %d |' % r['n'],
         '| 지연 p50 / p90 / max (초) | %s / %s / %s |' % (r['p50'], r['p90'], r['max']),
         '| 판정 (p90 ≤ %d초, n≥10) | **%s** |' % (r['p90_limit'], r['verdict']),
         '| PAGE_ERROR | %d%s |' % (r['page_errors'], '' if r['receiver_log'] else ' (수신기 로그 없음)'),
         '| 수신기 last_ok (후속8) | %s |' % {True: '있음', False: '**없음 — 옛 수신기**',
                                           None: '미확인'}[r['collector_has_last_ok']],
         '', '## 15분 창별 PAGE_ERROR', '']
    if r['errors_per_15m']:
        L.append(' · '.join('%s %d' % kv for kv in r['errors_per_15m'].items()))
    else:
        L.append('(없음)')
    L += ['', '## 지연 > %d초 트윗' % SLOW_SEC, '']
    if r['slow']:
        L += ['| 게시 | 지연(초) | 그 사이 PAGE_ERROR | 원문 |', '|---|---|---|---|']
        L += ['| %s | %d | %d | %s |' % (s['posted'], s['lat'], s['errors_between'],
                                         s['text'].replace('|', '/')) for s in r['slow']]
    else:
        L.append('(없음)')
    return '\n'.join(L)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('date', nargs='?', default=D.date.today().isoformat())
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args(argv)
    r = build(a.date)
    txt = json.dumps(r, ensure_ascii=False, indent=1) if a.json else render(r)
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:          # py37 이전
        pass
    print(txt)
    return 0 if r['verdict'] != 'FAIL' else 2


if __name__ == '__main__':
    sys.exit(main())
