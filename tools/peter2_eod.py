# -*- coding: utf-8 -*-
"""피터2 장후 정리 — 그날의 「피터 지시 · 실추종 · 섀도」를 한 장으로 확정한다.

하는 일
    1. 그의 거래줄 `_tr` 을 트윗만으로 만든다(시각은 트윗 시각뿐 — 지어내지 않는다).
       `data/peter_feed/<날짜>_tr.draft.txt` 는 항상 쓰고, `_tr.txt` 가 없을 때만 그것으로 채운다
       (사람이 손본 `_tr.txt` 는 덮지 않는다 — 차이가 나면 리포트에 적는다).
    2. 삭제된 트윗 — 장중(`src=live`)에 봤는데 장후 캡처(`<날짜>.eod_ids.json`)에 없는 id.
    3. 실추종 — trades.db `entry_source='PETER2'` 포지션(레그 합산, 포지션 단위 — 계측 4원칙 ①).
    4. 섀도 — `tools/peter2_replay.py` 와 같은 규칙으로 1분봉 재생(지연 20초 가정).
    5. 수신 지연 — 트윗 게시 시각 vs 수신기 기록 시각(`seen_at`, live 만).
    6. 해석·집행 이벤트 — `data/peter2_live/<날짜>/signals.jsonl` 집계(기각 사유 포함).
    → docs/미륵이고도화3/피터2/일일/피터2_일일_<PC>_<YYYYMMDD>.md

읽기 전용(사료 텍스트 파일 쓰기 제외). 주문 없음. 장중 실행 금지 — 라이브 DB 를 읽는다.

실행
    python tools/peter2_eod.py                 # 오늘
    python tools/peter2_eod.py --date 2026-10-08
"""
import argparse
import datetime
import io
import json
import os
import sqlite3
import sys
from collections import Counter

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (_ROOT, os.path.join(_ROOT, 'tools')):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from strategy.peter2 import store                       # noqa: E402
from strategy.peter2.follower import Peter2Follower     # noqa: E402

FEED_DIR = os.path.join(_ROOT, 'data', 'peter_feed')
TRADES_DB = os.path.join(_ROOT, 'data', 'db', 'trades.db')
OUT_DIR = os.path.join(store.DOC_DIR, '일일')


def _tweets(date):
    p = store.raw_path(date)
    rows = []
    if os.path.exists(p):
        with io.open(p, encoding='utf-8') as f:
            for ln in f:
                ln = ln.strip()
                if ln:
                    try:
                        rows.append(json.loads(ln))
                    except ValueError:
                        pass
    rows.sort(key=lambda r: r.get('dt') or '')
    return rows


def peter_tr(date, rows):
    """트윗만으로 그의 거래줄(피터가). 가격 없이 돈다 — 그의 상태기계만 쓴다."""
    fw = Peter2Follower(date, None, 'eod', False)
    eng = {'status': 'FLAT', 'source': None, 'pending': False, 'price': None}
    for r in rows:
        fw.ingest(r, eng, datetime.datetime.now(), replay=True)
    return fw.peter_tr_text(), fw.peter_trades, fw.peter


def follow_trades(date):
    """trades.db PETER2 — 포지션 단위로 묶는다(entry_ts 가 포지션 키)."""
    if not os.path.exists(TRADES_DB):
        return None
    con = sqlite3.connect('file:%s?mode=ro' % TRADES_DB.replace('\\', '/'), uri=True)
    con.row_factory = sqlite3.Row
    try:
        rows = con.execute("SELECT entry_ts, exit_ts, direction, entry_price, exit_price, quantity, "
                           "pnl_pts, pnl_krw, exit_reason FROM trades WHERE entry_source='PETER2' "
                           "AND substr(entry_ts,1,10)=? ORDER BY entry_ts, exit_ts", (date,)).fetchall()
    finally:
        con.close()
    pos = {}
    for r in rows:
        k = r['entry_ts']
        p = pos.setdefault(k, {'entry_ts': k, 'direction': r['direction'], 'entry': r['entry_price'],
                               'exit_ts': r['exit_ts'], 'exit': r['exit_price'], 'pnl_pts': 0.0,
                               'pnl_krw': 0.0, 'reason': r['exit_reason'], 'legs': 0})
        p['pnl_pts'] += float(r['pnl_pts'] or 0) * int(r['quantity'] or 1)
        p['pnl_krw'] += float(r['pnl_krw'] or 0)
        p['exit_ts'], p['exit'], p['reason'] = r['exit_ts'], r['exit_price'], r['exit_reason']
        p['legs'] += 1
    return list(pos.values())


def deleted(date, rows):
    p = os.path.join(store.RAW_DIR, '%s.eod_ids.json' % date)
    if not os.path.exists(p):
        return None                                   # 장후 캡처 미실행 — 판정 불가(0건 아님)
    try:
        eod = set(json.load(io.open(p, encoding='utf-8')))
    except Exception:
        return None
    return [r for r in rows if r.get('src') == 'live' and r['id'] not in eod]


def latency(rows):
    out = []
    for r in rows:
        if r.get('src') != 'live':
            continue
        t = store.tweet_kst(r.get('dt'))
        try:
            s = datetime.datetime.fromisoformat((r.get('seen_at') or '')[:19])
        except ValueError:
            continue
        if t is not None:
            out.append((s - t).total_seconds())
    return out


def _med(xs):
    xs = sorted(xs)
    if not xs:
        return None
    n = len(xs)
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2.0


def build(date, write_tr=True, shadow=True):
    rows = _tweets(date)
    res = {'date': date, 'n_tweets': len(rows)}
    tr_txt, ptrades, popen = peter_tr(date, rows)
    res['peter_tr'] = tr_txt
    draft = os.path.join(FEED_DIR, '%s_tr.draft.txt' % date)
    final = os.path.join(FEED_DIR, '%s_tr.txt' % date)
    tr_note = ''
    if write_tr and rows:
        with io.open(draft, 'w', encoding='utf-8') as f:
            f.write(tr_txt + ('\n' if tr_txt else ''))
        if not os.path.exists(final):
            if tr_txt:
                with io.open(final, 'w', encoding='utf-8') as f:
                    f.write(tr_txt + '\n')
                tr_note = '`_tr.txt` 신규 작성(초안 그대로)'
            else:
                tr_note = '거래 0건 — `_tr.txt` 만들지 않음'
        else:
            cur = io.open(final, encoding='utf-8').read().strip()
            tr_note = ('`_tr.txt` 기존본 유지 — 초안과 **같다**' if cur == tr_txt.strip()
                       else '`_tr.txt` 기존본 유지 — 초안과 **다르다**(사람이 손본 것으로 보고 덮지 않음)')
    res['tr_note'] = tr_note
    peter_pts = 0.0
    for x in ptrades:
        if x['exit'] is not None:
            peter_pts += (x['exit'] - x['entry']) if x['side'] == 'L' else (x['entry'] - x['exit'])
    res['peter_pts'] = round(peter_pts, 2)
    res['follow'] = follow_trades(date)
    res['deleted'] = deleted(date, rows)
    lat = latency(rows)
    res['lat_med'] = _med(lat)
    res['lat_max'] = max(lat) if lat else None
    res['lat_n'] = len(lat)
    res['n_live'] = sum(1 for r in rows if r.get('src') == 'live')
    sig = store.read_signals(date)
    res['sig_counts'] = Counter(s.get('kind') for s in sig)
    res['rejects'] = Counter('%s' % (s.get('why') or '?') for s in sig
                             if s.get('kind') in ('REJECT', 'DISARM', 'EXPIRE'))
    res['init'] = next((s for s in sig if s.get('kind') == 'INIT'), None)
    res['shadow'] = None
    if shadow:
        try:
            import peter2_replay as R
            sh = R.replay_day(date, 20)
            if 'skip' not in sh:
                res['shadow'] = sh
        except Exception as e:
            res['shadow_err'] = str(e)
    res['md_path'] = write_md(res)
    return res


def _f(v, fmt='%+.2f'):
    return '—' if v is None else (fmt % v)


def write_md(r):
    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)
    pc = store._pc()
    p = os.path.join(OUT_DIR, '피터2_일일_%s_%s.md' % (pc, r['date'].replace('-', '')))
    L = []
    L.append('# 피터2 일일 복기 — %s (%s)\n' % (r['date'], pc))
    L.append('> 장후 자동 생성(`tools/peter2_eod.py`). 피터가 = 그가 쓴 일반선물 가격, '
             '미니가 = 미륵이 계약 가격. 장중 기록은 `live/피터2_실시간_%s-%s.md`.\n'
             % (pc, r['date'].replace('-', '')))
    fol = r['follow']
    f_pts = sum(x['pnl_pts'] for x in fol) if fol else 0.0
    f_krw = sum(x['pnl_krw'] for x in fol) if fol else 0.0
    sh = r.get('shadow')
    L.append('## 요약\n')
    L.append('| 항목 | 값 |\n|---|---|')
    L.append('| 피터 공개 거래(트윗 기준) | %d건 · **%+.2fpt** |' % (
        len([1 for l in r['peter_tr'].splitlines() if l.strip()]), r['peter_pts']))
    if fol is None:
        L.append('| 실추종(trades.db) | 미측정 — DB 없음 |')
    else:
        L.append('| 실추종(trades.db PETER2) | %d포지션 · **%+.2fpt · %s원** |' % (
            len(fol), f_pts, format(f_krw, '+,.0f')))
    if sh:
        L.append('| 섀도 재생(지연 20초 가정) | %d건 · %+.2fpt |' % (len(sh['trades']), sh['follow_pts']))
    eff = (f_pts / r['peter_pts']) if (fol and r['peter_pts']) else None
    L.append('| 추종 효율(실추종/피터) | %s |' % ('—' if eff is None else '%.2f' % eff))
    L.append('| 트윗 | 전체 %d · 장중 수신(live) %d |' % (r['n_tweets'], r['n_live']))
    L.append('| 수신 지연(게시→기록) | 중앙 %s초 · 최대 %s초 (n=%d) |' % (
        _f(r['lat_med'], '%.0f'), _f(r['lat_max'], '%.0f'), r['lat_n']))
    if r['deleted'] is None:
        L.append('| 삭제 트윗 | 미측정 — 장후 캡처(eod_ids) 없음 |')
    else:
        L.append('| 삭제 트윗 | **%d건** |' % len(r['deleted']))
    ini = r.get('init') or {}
    L.append('| 오프셋 | %s (%s · safe=%s) |' % (ini.get('offset'), ini.get('offset_src'), ini.get('safe')))
    L.append('')
    L.append('## 피터 거래줄(트윗 기준, 피터가)\n')
    L.append('```\n%s\n```' % (r['peter_tr'] or '(거래 없음)'))
    L.append(r['tr_note'] and ('\n' + r['tr_note'] + '\n') or '')
    L.append('## 실추종 포지션(미니가)\n')
    if fol:
        L.append('| 진입 | 방향 | 진입가 | 청산 | 청산가 | pt | 원 | 사유 |\n|---|---|---|---|---|---|---|---|')
        for x in fol:
            L.append('| %s | %s | %.2f | %s | %.2f | %+.2f | %s | %s |' % (
                (x['entry_ts'] or '')[11:19], x['direction'], x['entry'] or 0,
                (x['exit_ts'] or '')[11:19], x['exit'] or 0, x['pnl_pts'],
                format(x['pnl_krw'], '+,.0f'), x['reason']))
    else:
        L.append('(실추종 없음)')
    L.append('')
    if sh:
        L.append('## 섀도 재생(같은 규칙 · 지연 20초 · 봉 4점 경로 가정)\n')
        L.append('```')
        L.extend(sh['log'])
        L.append('```')
        L.append('')
    L.append('## 해석·집행 이벤트\n')
    sc = r['sig_counts']
    L.append(' · '.join('%s %d' % (k, v) for k, v in sorted(sc.items())) or '(이벤트 없음 — 피터2 미기동?)')
    if r['rejects']:
        L.append('\n기각·해제·만료 사유:\n')
        for k, v in r['rejects'].most_common():
            L.append('- %s — %d' % (k, v))
    if r['deleted']:
        L.append('\n## 삭제된 트윗(장중에 봤으나 장후에 없음)\n')
        for x in r['deleted']:
            t = store.tweet_kst(x.get('dt'))
            L.append('- %s 「%s」' % (t.strftime('%H:%M') if t else '--:--',
                                    (x.get('text') or '').replace('\n', ' / ')[:120]))
    L.append('\n## 복기 메모(사람)\n\n- \n')
    with io.open(p, 'w', encoding='utf-8') as f:
        f.write('\n'.join(L))
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--date', default=datetime.date.today().isoformat())
    ap.add_argument('--no-tr', action='store_true', help='_tr 초안/최종 파일을 쓰지 않는다')
    ap.add_argument('--no-shadow', action='store_true')
    a = ap.parse_args()
    try:
        from utils.analysis_db import guard_intraday
        guard_intraday('peter2_eod')
    except ImportError:
        pass
    r = build(a.date, write_tr=not a.no_tr, shadow=not a.no_shadow)
    print('[peter2_eod] %s 트윗 %d · 피터 %+.2fpt · 실추종 %s · %s' % (
        a.date, r['n_tweets'], r['peter_pts'],
        ('%d포지션' % len(r['follow'])) if r['follow'] is not None else '미측정', r['tr_note']))
    print('  -> %s' % os.path.relpath(r['md_path'], _ROOT))


if __name__ == '__main__':
    main()
