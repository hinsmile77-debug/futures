# -*- coding: utf-8 -*-
"""[MW0602 거래주체분리] 미륵 섀도 장후 가상 손익 — 1단계(사용자 결정 2026-10-12).

거래주체가 미륵이 아닌 날, 진입 관문이 막은 미륵 자동진입(`mireuk_shadow.jsonl`)을 그날 1분봉으로
가상 청산해 손익을 낸다. 결과: `data/principal/<날짜>/mireuk_shadow_eval.json`.

⚠ **단순화 규칙이다 — 실제 청산 사다리와 다르다.** 실제는 TP1~TP3 분할·손절계단·트레일링·
   급행 하드스톱이 있다. 여기서는
     손절 = 진입가 ∓ ATR × ATR_STOP_MULT × extra_stop_mult
     목표 = 진입가 ± ATR × ATR_HORIZON_TP1_MULT[호라이즌](없으면 ATR_TP1_MULT) — **전량**
     시간 = FORCE_EXIT_TIME(15:10) 직전 봉 종가
     같은 봉에서 손절·목표가 둘 다 닿으면 손절(보수적)
   진입가 = 관문 시점 가격(실제라면 시장가 체결가). 한 번에 한 포지션 — 가상 보유 중에 들어온
   섀도 진입은 `overlap` 으로 표시하고 손익에서 뺀다(실계좌라면 단일 포지션이라 못 들어갔다).
   요율은 이 PC 감지 요율(MW0602 = CREON).
2단계(실시간 가상 포지션)는 PositionTracker 상태 파일 격리 문제 때문에 미룬다
(`docs/거래주체분리/거래주체분리_구현계획_MW0602-20261012.md` §3-3).
"""
import datetime
import os
import sqlite3

from strategy.runtime import trade_principal as TP

RULE = 'simplified_v1(stop ATR×1.5×extra · TP1 전량 · 15:10)'


def load_bars(raw_db, date):
    """→ [(HH:MM, high, low, close)] 정규장 봉. raw_candles.ts 는 봉 시작 시각."""
    if not os.path.exists(raw_db):
        return []
    con = sqlite3.connect('file:%s?mode=ro' % raw_db.replace('\\', '/'), uri=True, timeout=5.0)
    try:
        rows = con.execute("SELECT ts, high, low, close FROM raw_candles WHERE ts LIKE ? ORDER BY ts",
                           (date + '%',)).fetchall()
    finally:
        con.close()
    return [(str(r[0])[11:16], float(r[1]), float(r[2]), float(r[3])) for r in rows]


def simulate(entries, bars, stop_mult, tp1_mult_by_hz, tp1_default, rate, pt_value,
             force_exit='15:10'):
    """순수 함수 — entries(시간순) × bars → [가상 거래]."""
    out = []
    busy_until = ''
    for e in entries:
        ts = str(e.get('ts') or '')
        hm = ts[11:16]
        side = 1 if e.get('direction') == 'LONG' else -1 if e.get('direction') == 'SHORT' else 0
        rec = {'ts': ts, 'direction': e.get('direction'), 'qty': int(e.get('qty') or 0),
               'entry_px': e.get('price'), 'grade': e.get('grade'), 'entry_horizon': e.get('entry_horizon')}
        try:
            px, atr = float(e.get('price')), float(e.get('atr') or 0.0)
        except (TypeError, ValueError):
            px, atr = None, 0.0
        if not side or px is None or atr <= 0 or rec['qty'] <= 0:
            rec.update(reason='invalid', net_krw=None)
            out.append(rec)
            continue
        if hm < busy_until:
            rec.update(reason='overlap', net_krw=None)
            out.append(rec)
            continue
        stop = px - side * atr * stop_mult * float(e.get('extra_stop_mult') or 1.0)
        tp = px + side * atr * float(tp1_mult_by_hz.get(e.get('entry_horizon'), tp1_default))
        # 관문 시점 분의 봉은 진입 전에 형성된 부분이 섞이므로 다음 봉부터 본다
        exit_hm = exit_px = reason = None
        last = None
        for b_hm, h, l, c in bars:
            if b_hm <= hm:
                continue
            if b_hm >= force_exit:
                break
            last = (b_hm, c)
            if (l <= stop) if side > 0 else (h >= stop):
                exit_hm, exit_px, reason = b_hm, stop, 'stop'
                break
            if (h >= tp) if side > 0 else (l <= tp):
                exit_hm, exit_px, reason = b_hm, tp, 'tp1'
                break
        if exit_hm is None:
            if last is None:
                rec.update(reason='no_bars', net_krw=None)
                out.append(rec)
                continue
            exit_hm, exit_px, reason = last[0], last[1], 'time'
        pts = side * (exit_px - px)
        gross = pts * pt_value * rec['qty']
        fee = (px + exit_px) * pt_value * rate * rec['qty']
        rec.update(stop=round(stop, 2), target=round(tp, 2), exit_hm=exit_hm, exit_px=round(exit_px, 2),
                   reason=reason, pts=round(pts, 2), gross_krw=round(gross), net_krw=round(gross - fee))
        out.append(rec)
        busy_until = exit_hm
    return out


def evaluate(date, raw_db=None, write=True):
    import config.settings as S
    from config.constants import MINI_FUTURES_PT_VALUE
    entries = sorted(TP.read_jsonl(date, 'mireuk_shadow.jsonl'), key=lambda r: str(r.get('ts')))
    bars = load_bars(raw_db or S.RAW_DATA_DB, date)
    trades = simulate(entries, bars, S.ATR_STOP_MULT, dict(S.ATR_HORIZON_TP1_MULT), S.ATR_TP1_MULT,
                      float(S.FUTURES_COMMISSION_RATE), MINI_FUTURES_PT_VALUE,
                      getattr(S, 'FORCE_EXIT_TIME', '15:10'))
    done = [t for t in trades if t.get('net_krw') is not None]
    res = {'date': date, 'rule': RULE, 'rate': float(S.FUTURES_COMMISSION_RATE),
           'n_shadow': len(entries), 'n_eval': len(done),
           'n_skip': {k: sum(1 for t in trades if t.get('reason') == k) for k in ('overlap', 'invalid', 'no_bars')},
           'net_krw': sum(t['net_krw'] for t in done), 'trades': trades,
           'evaluated_at': datetime.datetime.now().isoformat(timespec='seconds')}
    if write and entries:
        TP.write_json(date, 'mireuk_shadow_eval.json', res)
    return res
