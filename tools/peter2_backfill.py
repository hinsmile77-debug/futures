# -*- coding: utf-8 -*-
"""[MW0601 677차] 피터2 백필 빌드 — 실거래 개시 이전 손익을 손익추이에 올릴 재료를 만든다.

원천
    A  peter_levels.db · peter_paste(raw_tr · 그날 실측 offset)   — 1분봉 차트 「거래피터」 확정본
    B  tools/peter2_replay.py · replay_day()                       — 라이브와 같은 cfg 로 재생
    거래일 = raw_data.db · raw_candles 에 분봉이 있는 날, [첫 피터 사료일, PETER2_BACKFILL_UNTIL)
출력
    data/db/peter2_backfill.db (전량 교체) → main.py `_refresh_pnl_history()` 가 읽어 패널에 넘긴다.

읽기 전용(원천 DB) · 장중 실행 금지(456차 — raw_data.db 스캔).

실행
    python tools/peter2_backfill.py                       빌드 + 요약
    python tools/peter2_backfill.py --dry-run             저장하지 않고 요약만
    python tools/peter2_backfill.py --mark-unmeasured 2026-09-28 2026-09-29 --reason "사료 미입력"
                                                          미측정 장부에 적고 다시 빌드
"""
import argparse
import datetime
import os
import sqlite3
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (_ROOT, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from config import settings                      # noqa: E402
from config.constants import (                   # noqa: E402
    MINI_FUTURES_PT_VALUE, PETER2_ENTRY_SOURCE)
from strategy.peter2 import backfill as bf       # noqa: E402
from strategy.peter2 import store                # noqa: E402

RAW_DB = os.path.join(settings.DB_DIR, 'raw_data.db')
TRADES_DB = os.path.join(settings.DB_DIR, 'trades.db')


def _ro(path):
    return sqlite3.connect('file:%s?mode=ro' % path.replace('\\', '/'), uri=True)


def live_cfg():
    """main.py `_peter2_init()` 과 같은 cfg — B 가 라이브 규칙으로 돌게 한다."""
    g = lambda k, d: getattr(settings, k, d)   # noqa: E731
    return {
        'chase': float(g('PETER2_CHASE_MAX_PT', 1.0)),
        'tol': float(g('PETER2_OFFSET_TOL_PT', 0.2)),
        'arm_expire_min': int(g('PETER2_ARM_EXPIRE_MIN', 10)),
        'arm_max_dist': float(g('PETER2_ARM_MAX_DIST_PT', 8.0)),
        'plausible': float(g('PETER2_PLAUSIBLE_DIST_PT', 40.0)),
        'default_stop': float(g('PETER2_DEFAULT_STOP_PT', 4.0)),
        'stop_cap': float(g('PETER2_STOP_CAP_PT', 8.0)),
        'daily_stop_limit': int(g('PETER2_DAILY_STOP_LIMIT', 0) or 0),
        'daily_max_entries': int(g('PETER2_DAILY_MAX_ENTRIES', 6)),
        'last_entry_hm': bf.NEW_ENTRY_CUTOFF_HM,
    }


def load_pastes():
    con = _ro(store.PETER_DB)
    try:
        return {r[0]: (r[1], r[2] or '') for r in con.execute(
            'SELECT date, offset, raw_tr FROM peter_paste ORDER BY date')}
    finally:
        con.close()


def trading_days(start, until):
    con = _ro(RAW_DB)
    try:
        return [r[0] for r in con.execute(
            'SELECT DISTINCT substr(ts,1,10) FROM raw_candles WHERE ts>=? AND ts<? ORDER BY 1',
            (start + ' 00:00:00', until + ' 00:00:00'))]
    finally:
        con.close()


def load_bars(date):
    con = _ro(RAW_DB)
    try:
        return con.execute('SELECT ts, open, high, low, close FROM raw_candles '
                           'WHERE ts>=? AND ts<? ORDER BY ts',
                           (date + ' 09:00:00', date + ' 15:11:00')).fetchall()
    finally:
        con.close()


def live_peter2_days(until):
    """trades 에 PETER2 실거래가 있는 날 — 백필하면 이중계상이다."""
    if not os.path.exists(TRADES_DB):
        return set()
    con = _ro(TRADES_DB)
    try:
        return {r[0] for r in con.execute(
            'SELECT DISTINCT substr(COALESCE(exit_ts, entry_ts),1,10) FROM trades '
            'WHERE entry_source=? AND COALESCE(exit_ts, entry_ts) < ?',
            (PETER2_ENTRY_SOURCE, until + ' 00:00:00'))}
    finally:
        con.close()


def run_b(date, latency):
    """(status, trades). B 는 비교 열이라 실패해도 빌드를 멈추지 않는다 — 사유를 남긴다."""
    if not os.path.exists(store.raw_path(date)):
        return 'NO_RAW', []
    try:
        import peter2_replay
        res = peter2_replay.replay_day(date, latency, cfg=live_cfg())
    except Exception as e:                  # noqa: BLE001
        return 'ERROR:%s' % e, []
    if 'skip' in res:
        return ('NO_BARS' if res['skip'] == 'no_bars' else 'NO_OFFSET'), []
    return 'OK', bf.b_trades_from_replay(date, res, MINI_FUTURES_PT_VALUE)


def build(latency=20, until=None):
    until = until or settings.PETER2_BACKFILL_UNTIL
    pastes = load_pastes()
    if not pastes:
        raise SystemExit('peter_paste 가 비었다 — 백필 원천 없음')
    start = min(pastes)
    unmeasured = bf.read_unmeasured(settings.PETER2_BACKFILL_UNMEASURED)
    live = live_peter2_days(until)
    trades, days, warn = [], [], []
    for d in trading_days(start, until):
        has = d in pastes
        off, raw_tr = pastes.get(d, (None, ''))
        a = []
        if has and d not in live and d not in unmeasured:
            a, notes = bf.build_a_day(d, raw_tr, off, load_bars(d), MINI_FUTURES_PT_VALUE)
            warn += ['%s %s' % (d, n) for n in notes]
        st = bf.classify_day(has, a, d in unmeasured, d in live)
        if st == bf.ST_LIVE:
            b_st, b = 'SKIP', []
        else:
            b_st, b = run_b(d, latency)
        trades += a + b
        a_ok = st in (bf.ST_TRADED, bf.ST_NO_TRADE)
        days.append({
            'trade_date': d, 'status': st,
            'a_n': len(a) if a_ok else None,
            'a_pts': round(sum(t['pnl_pts'] for t in a), 2) if a_ok else None,
            'b_status': b_st,
            'b_n': len(b) if b_st == 'OK' else None,
            'b_pts': round(sum(t['pnl_pts'] for t in b), 2) if b_st == 'OK' else None,
            'offset': off,
            'note': unmeasured.get(d) if st == bf.ST_UNMEASURED else None,
        })
    meta = {'built_at': datetime.datetime.now().isoformat(timespec='seconds'),
            'until': until, 'start': start, 'latency_sec': latency,
            'pt_value': MINI_FUTURES_PT_VALUE}
    return trades, days, meta, warn


def summary(trades, days, meta, warn):
    from collections import Counter
    st = Counter(d['status'] for d in days)
    print('피터2 백필 %s – %s(배타) · 거래일 %d' % (meta['start'], meta['until'], len(days)))
    print('  상태: ' + ' · '.join('%s %d' % kv for kv in sorted(st.items())))
    for src in (bf.SRC_A, bf.SRC_B):
        xs = [t for t in trades if t['src'] == src]
        print('  %s %d건 · %+.2fpt · gross %s원 · 15:10 재측정 %d건' % (
            src, len(xs), sum(t['pnl_pts'] for t in xs),
            format(sum(t['gross_krw'] for t in xs), '+,.0f'), sum(t['clipped'] for t in xs)))
    unres = [d['trade_date'] for d in days if d['status'] == bf.ST_UNRESOLVED]
    if unres:
        print('  ⚠ 미판정(사료·장부 없음) %d일: %s' % (len(unres), ', '.join(unres)))
        print('    → 미측정으로 적으려면: --mark-unmeasured %s --reason "..."' % ' '.join(unres))
    b_miss = [d['trade_date'] for d in days if d['b_status'] not in ('OK', 'SKIP')]
    if b_miss:
        print('  B 미측정 %d일: %s' % (len(b_miss), ', '.join(
            '%s(%s)' % (d['trade_date'], d['b_status']) for d in days if d['trade_date'] in b_miss)))
    for w in warn:
        print('  · ' + w)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--latency', type=int, default=20, help='B 재생 지연(초)')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--mark-unmeasured', nargs='+', metavar='DATE')
    ap.add_argument('--reason', default='')
    a = ap.parse_args()
    if a.mark_unmeasured:
        new = bf.mark_unmeasured(settings.PETER2_BACKFILL_UNMEASURED, a.mark_unmeasured, a.reason)
        print('미측정 장부 +%d: %s → %s' % (len(new), ', '.join(new) or '(이미 있음)',
                                          settings.PETER2_BACKFILL_UNMEASURED))
    try:
        from utils.analysis_db import guard_intraday
        guard_intraday('peter2_backfill')
    except ImportError:
        pass
    trades, days, meta, warn = build(a.latency)
    summary(trades, days, meta, warn)
    if a.dry_run:
        print('(dry-run — 저장 안 함)')
        return
    bf.save(settings.PETER2_BACKFILL_DB, trades, days, meta)
    print('저장 → %s' % settings.PETER2_BACKFILL_DB)


if __name__ == '__main__':
    main()
