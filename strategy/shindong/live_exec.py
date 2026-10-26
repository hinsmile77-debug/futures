# -*- coding: utf-8 -*-
"""[MW0602 거래주체분리] 신동 V2(FLOWC) 실집행 판단 — 순수 함수(입출력·주문 없음).

거래주체가 「신동」일 때 main 이 이 판단대로 실주문을 낸다(`main.py:_shindong_exec_step`).
규칙은 신동 엔진(`shindong.db` MAIN 재생)이 정하고, 여기서는 **그 재생을 실포지션에 옮기는 법**만 정한다.

FLOWC MAIN 의 두 레그는 같은 청산가·같은 시각에 닫힌다(`families._run_position` — t1 == t2).
그래서 실집행은 2계약 일괄 진입·일괄 청산이다(사용자 결정 2026-10-12: 2계약 2레그 그대로).

옮기는 법
    진입    재생에 새 OPEN 거래(라이브 탐지)가 생기고 진입봉이 끝난 지 `max_age_min` 분 이내 → 진입.
            더 늦으면 진입하지 않는다(재기동·지연으로 이미 지나간 신호를 쫓지 않는다).
    손절    재생의 `stop_now`(재난 손절 → 트레일)가 유리하게 움직이면 따라 조인다(한 방향).
    목표    `t1`(익절가) — main 의 2초 폴링이 본다.
    청산    재생에서 그 거래가 CLOSED 가 되면 미러 청산. 규격 시간청산(TIME_EXIT 15:05)이면 시장가.
    철회    RETRACTED(재생에서 신호 소멸 — v3 까지는 R3 비인과 선택 탓, 718차 확인)는 **청산 사유가 아니다** — 이미 들고 있는 포지션은
            마지막 손절·목표로 계속 관리한다(재생이 과거를 고쳐 쓴 것이지 시장이 바뀐 게 아니다).
"""
import datetime

from strategy.shindong import spec as S

SIDE_DIR = {1: 'LONG', -1: 'SHORT'}


def bar_end(entry_ts):
    """진입봉(시작 시각 'YYYY-MM-DD HH:MM:00')이 끝난 시각 = 신호가 확정된 시각."""
    t = datetime.datetime.strptime(str(entry_ts)[:16], '%Y-%m-%d %H:%M')
    return t + datetime.timedelta(minutes=1)


def stop_of(t):
    v = t.get('stop_now')
    if v is None:
        v = t.get('stop_init')
    return None if v is None else float(v)


def pick_new_entry(trades, executed, now, max_age_min=2):
    """→ (trade 또는 None, 늦어서 건너뛴 trade 목록).

    후보: MAIN 재생의 OPEN · 라이브 탐지(`source='live'`) · 아직 집행 기록 없음.
    여럿이면 가장 최근 진입봉 하나만(FLOWC 는 한 번에 한 거래다).
    """
    cands = [t for t in (trades or [])
             if t.get('status') == 'OPEN' and t.get('source') == 'live'
             and t.get('trade_key') not in executed]
    stale = []
    pick = None
    for t in sorted(cands, key=lambda x: str(x.get('entry_ts')), reverse=True):
        try:
            age = (now - bar_end(t['entry_ts'])).total_seconds() / 60.0
        except (KeyError, ValueError, TypeError):
            continue
        if pick is None and -0.5 <= age <= max_age_min:
            pick = t
        else:
            stale.append(t)
    return pick, stale


def manage(rec, trade, now, time_exit=None):
    """집행 중 거래 하나 → 행동 목록.

    rec   = 집행 기록 {side(+1/-1), stop, target, retracted?}
    trade = 지금 재생의 같은 거래 행(사라졌으면 None = RETRACTED)
    행동  = ('exit', 사유) · ('set_stop', 가격) · ('retracted',)
    """
    te = time_exit or S.TIME_EXIT
    if now.strftime('%H:%M') >= te:
        return [('exit', '신동시간청산')]
    if trade is None:
        return [] if rec.get('retracted') else [('retracted',)]
    if trade.get('status') == 'CLOSED':
        return [('exit', '신동미러:%s' % (trade.get('leg1_reason') or 'CLOSED'))]
    ns = stop_of(trade)
    cur = rec.get('stop')
    side = int(rec.get('side') or 0)
    if ns is not None and (cur is None or side * (ns - float(cur)) > 1e-9):
        return [('set_stop', round(ns, 2))]
    return []
