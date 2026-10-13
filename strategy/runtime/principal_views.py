# -*- coding: utf-8 -*-
"""[MW0602 거래주체분리] 거래주체 화면용 집계 — 잔고 카드(주체 실적) · 「거래 현황」 행.

읽기 전용. 미륵이 라이브 DB 는 `mode=ro` 로만 연다.

실적의 단위는 **포지션**이다(계측 4원칙 ①) — trades 는 청산 레그별 행이라 같은 진입(entry_ts)을
묶는다. 순손익은 `net_pnl_krw`(없으면 `pnl_krw` 로 폴백하고 그 사실을 남긴다 — ④).

신동 섀도 손익은 **CREON 요율**로 환산한다(사용자 결정 2026-10-12, `shindong/display.py` 와 같은 식).
"""
import datetime
import os
import sqlite3

from strategy.runtime import trade_principal as TP

SIDE_KO = {'LONG': '매수', 'SHORT': '매도', 1: '매수', -1: '매도'}


def _ro(path):
    con = sqlite3.connect('file:%s?mode=ro' % path.replace('\\', '/'), uri=True, timeout=3.0)
    con.row_factory = sqlite3.Row
    return con


def _positions(rows):
    """레그 행 → 포지션(entry_ts 묶음)."""
    pos = {}
    for r in rows:
        k = (r['entry_ts'], r['entry_source'])
        p = pos.setdefault(k, {'entry_ts': r['entry_ts'], 'source': r['entry_source'],
                               'direction': r['direction'], 'entry': r['entry_price'],
                               'qty': 0, 'net': 0.0, 'gross': 0.0, 'exit': None, 'exit_ts': '',
                               'reason': '', 'net_fallback': False})
        p['qty'] += int(r['quantity'] or 0)
        net = r['net_pnl_krw']
        if net is None:
            net = r['pnl_krw'] or 0.0
            p['net_fallback'] = True
        p['net'] += float(net)
        p['gross'] += float(r['gross_pnl_krw'] if r['gross_pnl_krw'] is not None else (r['pnl_krw'] or 0.0))
        if str(r['exit_ts'] or '') >= p['exit_ts']:
            p['exit_ts'] = str(r['exit_ts'] or '')
            p['exit'] = r['exit_price']
            p['reason'] = r['exit_reason'] or ''
    return sorted(pos.values(), key=lambda x: str(x['entry_ts']))


def day_positions(trades_db, date):
    """그날 청산된 포지션 전부(출처 무관)."""
    if not os.path.exists(trades_db):
        return []
    con = _ro(trades_db)
    try:
        rows = con.execute(
            "SELECT entry_ts, exit_ts, direction, entry_price, exit_price, quantity, pnl_krw, "
            "gross_pnl_krw, net_pnl_krw, exit_reason, entry_source FROM trades "
            "WHERE substr(exit_ts,1,10)=? ORDER BY exit_ts", (date,)).fetchall()
    finally:
        con.close()
    return _positions(rows)


def principal_summary(trades_db, date, principal):
    """→ dict(net, gross, n, fallback, others{출처: net}). 주체 출처의 그날 실적과 섞인 다른 출처."""
    src = TP.PRINCIPAL_SOURCE.get(principal)
    out = {'net': 0.0, 'gross': 0.0, 'n': 0, 'fallback': False, 'others': {}}
    for p in day_positions(trades_db, date):
        if p['source'] == src:
            out['net'] += p['net']
            out['gross'] += p['gross']
            out['n'] += 1
            out['fallback'] = out['fallback'] or p['net_fallback']
        else:
            k = p['source'] or '미상'
            out['others'][k] = out['others'].get(k, 0.0) + p['net']
    return out


def prev_trade_date(trades_db, date):
    """date 이전 마지막 청산일(거래가 있던 날). 없으면 None."""
    if not os.path.exists(trades_db):
        return None
    con = _ro(trades_db)
    try:
        r = con.execute("SELECT max(substr(exit_ts,1,10)) FROM trades WHERE substr(exit_ts,1,10)<?",
                        (date,)).fetchone()
    finally:
        con.close()
    return r[0] if r and r[0] else None


# ── 거래 현황 행 ──────────────────────────────────────────────

def _hm(ts):
    s = str(ts or '')
    return s[11:16] if len(s) >= 16 else s[:5]


def live_rows(trades_db, date, principal, open_pos=None):
    """선택 주체의 오늘 실거래(청산분) + 보유 중 포지션."""
    src = TP.PRINCIPAL_SOURCE.get(principal)
    who = TP.label(principal)
    out = []
    for p in day_positions(trades_db, date):
        if p['source'] != src:
            continue
        out.append({'time': _hm(p['entry_ts']), 'who': who, 'kind': '실거래',
                    'side': SIDE_KO.get(p['direction'], p['direction']), 'qty': p['qty'],
                    'entry': p['entry'], 'exit': p['exit'], 'pnl': round(p['net']),
                    'status': '청산 %s %s' % (_hm(p['exit_ts']), p['reason'])})
    if open_pos and open_pos.get('source') == src:
        out.append({'time': _hm(open_pos.get('entry_ts')), 'who': who, 'kind': '실거래',
                    'side': SIDE_KO.get(open_pos.get('status'), open_pos.get('status')),
                    'qty': open_pos.get('qty'), 'entry': open_pos.get('entry'),
                    'exit': open_pos.get('stop'), 'pnl': open_pos.get('unrealized'),
                    'status': '보유'})
    return out


def shindong_shadow_rows(shindong_db, date):
    """신동 MAIN 재생(가상) — CREON 요율 순손익.

    `shindong/display.py`(CREON 재환산, dev 590차)가 없는 브랜치(v9-dev)는 저장된 `net_krw`
    (규격 요율)를 그대로 쓴다 — 그 사실을 status 에 「규격요율」로 남긴다(계측 4원칙 ④).
    """
    try:
        from strategy.shindong import store as sd_store
    except Exception:
        return []
    try:
        from strategy.shindong import display as sd_disp
        rate = sd_disp.creon_rate()
    except Exception:
        sd_disp, rate = None, None
    out = []
    for t in sd_store.load_trades(shindong_db, date, 'MAIN'):
        net = None
        if t.get('status') == 'CLOSED':
            if sd_disp is None:
                net = float(t.get('net_krw') or 0.0)
            else:
                net = 0.0
                for i in (1, 2):
                    n = sd_disp.leg_net_at_rate(t.get('leg%d_net' % i), t['entry_px'],
                                                t.get('leg%d_exit_px' % i) or t['entry_px'], rate)
                    net += n or 0.0
        out.append({'time': _hm(t.get('entry_ts')), 'who': '신동', 'kind': '섀도',
                    'side': SIDE_KO.get(t.get('side'), t.get('side')), 'qty': 2,
                    'entry': t.get('entry_px'),
                    'exit': t.get('leg1_exit_px') if t.get('status') == 'CLOSED' else t.get('stop_now'),
                    'pnl': None if net is None else round(net),
                    'status': (('청산 %s' % (t.get('leg1_reason') or ''))
                               + ('' if sd_disp is not None else ' ·규격요율'))
                    if t.get('status') == 'CLOSED' else '보유(가상)'})
    return out


def mireuk_shadow_rows(date):
    """관문이 막은 미륵 자동진입. 장후 가상 손익 파일이 있으면 그 값을 붙인다."""
    ev = TP.read_json(date, 'mireuk_shadow_eval.json', {}) or {}
    by_ts = {e.get('ts'): e for e in (ev.get('trades') or [])}
    out = []
    for r in TP.read_jsonl(date, 'mireuk_shadow.jsonl'):
        e = by_ts.get(r.get('ts')) or {}
        out.append({'time': _hm(r.get('ts', '').replace('T', ' ')), 'who': '미륵', 'kind': '섀도',
                    'side': SIDE_KO.get(r.get('direction'), r.get('direction')), 'qty': r.get('qty'),
                    'entry': r.get('price'), 'exit': e.get('exit_px'),
                    'pnl': e.get('net_krw'),
                    'status': ('가상 %s' % e.get('reason')) if e else ('섀도 등급 %s' % r.get('grade'))})
    return out


def peter_shadow_rows(date):
    """피터2 섀도 진입(SHADOW 이벤트) — 손익은 장후 재생 도구 몫이라 비운다."""
    try:
        from strategy.peter2 import store as p2
        import io
        import json
        p = os.path.join(p2.LIVE_DIR, date, 'signals.jsonl')
        if not os.path.exists(p):
            return []
        out = []
        with io.open(p, encoding='utf-8') as f:
            for line in f:
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                if e.get('kind') != 'SHADOW':
                    continue
                out.append({'time': str(e.get('hm') or ''),        # follower._ev 는 'hm'(HH:MM)
                            'who': '피터', 'kind': '섀도',
                            'side': SIDE_KO.get(e.get('side'), e.get('side')), 'qty': 1,
                            'entry': e.get('price'), 'exit': e.get('stop'), 'pnl': None,
                            'status': '섀도'})
        return out
    except Exception:
        return []


def virtual_rows(date, open_books=None):
    """[거래주체분리 2단계] 가상 장부 — 청산된 가상 포지션 + 보유 중 가상 포지션.

    open_books = {principal: {status, qty, entry, stop, entry_ts, unrealized}} (main 이 넘긴다).
    → (행 목록, 가상 기록이 있는 주체 집합).
    """
    try:
        from strategy.runtime import virtual_book as VB
        poss = VB.day_positions(date)
    except Exception:
        poss = []
    out, who_set = [], set()
    for p in poss:
        who_set.add(p['principal'])
        out.append({'time': _hm(p['entry_ts']), 'who': TP.label(p['principal']), 'kind': '가상',
                    'side': SIDE_KO.get(p['direction'], p['direction']), 'qty': p['qty'],
                    'entry': p['entry'], 'exit': p['exit'], 'pnl': p['net'],
                    'status': ('청산 %s %s' % (_hm(p['exit_ts']), p['reason'])) if p['closed']
                    else ('부분 %s' % p['reason'])})
    for pr, b in (open_books or {}).items():
        who_set.add(pr)
        out.append({'time': _hm(b.get('entry_ts')), 'who': TP.label(pr), 'kind': '가상',
                    'side': SIDE_KO.get(b.get('status'), b.get('status')), 'qty': b.get('qty'),
                    'entry': b.get('entry'), 'exit': b.get('stop'), 'pnl': b.get('unrealized'),
                    'status': '보유(가상)'})
    return out, who_set


def status_rows(trades_db, shindong_db, date, principal, open_pos=None, open_books=None):
    rows = live_rows(trades_db, date, principal, open_pos)
    vrows, vwho = virtual_rows(date, open_books)
    rows += vrows
    # 가상 장부 기록이 있는 주체는 1단계 섀도 행을 겹쳐 싣지 않는다(같은 진입이 두 번 보인다).
    if principal != TP.MIREUK and TP.MIREUK not in vwho:
        rows += mireuk_shadow_rows(date)
    if principal != TP.SHINDONG and TP.SHINDONG not in vwho:
        rows += shindong_shadow_rows(shindong_db, date)
    if principal != TP.PETER and TP.PETER not in vwho:
        rows += peter_shadow_rows(date)
    rows.sort(key=lambda r: (r.get('time') or '', r.get('kind') != '실거래'))
    return rows
