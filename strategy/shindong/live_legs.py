# -*- coding: utf-8 -*-
"""[MW0601 685차 / 거래주체분리 v9] 신동 MAIN(SD-2026-09-29-v2) 실집행 — 레그 분할 판단(순수 함수).

dev 의 `live_exec.manage` 는 FLOWC(두 레그 동시 청산) 전제라 v9 규격에 맞지 않는다. v9 신동은
`engine.run_trade(e2=False)` 그대로 **1차 목표에서 1계약 청산 → 공통 손절을 본전으로 → 최종 목표**다.
이 파일은 그 규격을 실포지션에 옮기는 법만 정한다. 주문·입출력은 main 이 한다.

누가 무엇을 보나
    손절      포지션 트래커의 외부 손절(`ext_stop` → `stop_price`) — 틱 단위 하드스톱이 집행한다.
    1차·최종  여기 `poll()` — main 의 2초 폴링이 현재가로 부른다(지정가 대기 주문은 내지 않는다).
    재생 대조 `sync()` — 매분 재생 결과와 맞춘다. 2초 폴링이 놓친 꼬리(봉 고저만 닿은 값)를
              재생이 잡았으면 따라 청산하고, 재생의 손절(본전 이동)이 유리하면 따라 조인다.
    시간청산  `spec.TIME_EXIT`(15:05) — 규격 그대로. 15:10 강제청산은 main 이 별도로 지킨다.
    철회      RETRACTED 는 청산 사유가 아니다(dev 와 같다) — 마지막 손절·목표로 계속 관리한다.

집행 기록 rec (data/principal/<날짜>/shindong_exec.json 에 영속 — 재기동 생존)
    {trade_key, rule, side(+1/-1), entry_px(규칙가), stop, t1, t2, leg1_done, retracted, done}
"""
from strategy.shindong import spec as S

EPS = 1e-9


def make_rec(trade):
    """재생 거래 행(`store.load_trades`) → 집행 기록."""
    stop = trade.get('stop_now')
    if stop is None:
        stop = trade.get('stop_init')
    return {
        'trade_key': trade['trade_key'], 'rule': trade.get('rule'),
        'side': int(trade['side']), 'entry_px': float(trade['entry_px']),
        'stop': None if stop is None else round(float(stop), 2),
        't1': None if trade.get('t1') is None else float(trade['t1']),
        't2': None if trade.get('t2') is None else float(trade['t2']),
        'leg1_done': False, 'retracted': False, 'done': False,
    }


def _hit(side, price, level):
    if level is None or price is None:
        return False
    return price >= level - EPS if side > 0 else price <= level + EPS


def _single_leg(rec):
    """1차와 최종이 같은 값이면(엔진이 t1=None → t1=t2 로 채운 경우) 두 레그가 한 번에 닫힌다."""
    t1, t2 = rec.get('t1'), rec.get('t2')
    return t2 is None or (t1 is not None and abs(t1 - t2) < EPS)


def entry_check(rec, price):
    """진입 직전 점검 → None(진입 가능) 또는 사유 문자열.

    재생이 진입을 알아챈 시각은 진입봉이 끝난 뒤다. 그 사이 가격이 손절을 이미 넘었거나
    1차 목표를 이미 지났으면 규격대로 매매할 수 없으므로 들어가지 않는다.
    """
    side = rec['side']
    if price is None:
        return 'no_price'
    if rec.get('stop') is None:
        return 'no_stop'
    if side * (price - rec['stop']) <= 0:
        return 'stop_breached(%.2f vs %.2f)' % (price, rec['stop'])
    if _hit(side, price, rec.get('t1')):
        return 'target_passed(%.2f vs t1 %.2f)' % (price, rec['t1'])
    return None


def poll(rec, price, now):
    """2초 폴링 → 행동 목록. ('exit_all', 사유) · ('exit_leg1', 사유)."""
    if rec.get('done'):
        return []
    if now.strftime('%H:%M') >= S.TIME_EXIT:
        return [('exit_all', '신동시간청산')]
    side = rec['side']
    if not rec.get('leg1_done'):
        if _hit(side, price, rec.get('t1')):
            if _single_leg(rec) or _hit(side, price, rec.get('t2')):
                return [('exit_all', '신동1차·최종')]
            return [('exit_leg1', '신동1차')]
        return []
    if _hit(side, price, rec.get('t2')):
        return [('exit_all', '신동최종')]
    return []


def after_leg1(rec):
    """1차 청산 주문을 낸 뒤 — 공통 손절을 본전(규칙 진입가)으로. 이미 더 유리하면 그대로."""
    rec['leg1_done'] = True
    be = round(rec['entry_px'], 2)
    if rec.get('stop') is None or rec['side'] * (be - rec['stop']) > EPS:
        rec['stop'] = be
        return be
    return None


def sync(rec, trade, now):
    """매분 재생 결과와 맞춘다 → 행동 목록.

    ('retracted',) · ('exit_all', 사유) · ('exit_leg1', 사유) · ('set_stop', 가격)
    """
    if rec.get('done'):
        return []
    if now.strftime('%H:%M') >= S.TIME_EXIT:
        return [('exit_all', '신동시간청산')]
    if trade is None or trade.get('status') == 'RETRACTED':
        return [] if rec.get('retracted') else [('retracted',)]
    if trade.get('status') == 'CLOSED':
        why = trade.get('leg2_reason') or trade.get('leg1_reason') or 'CLOSED'
        return [('exit_all', '신동미러:%s' % why)]
    out = []
    if not rec.get('leg1_done') and trade.get('leg1_reason') == 'TP1':
        out.append(('exit_leg1', '신동미러:TP1'))
    ns = trade.get('stop_now')
    if ns is not None:
        ns = round(float(ns), 2)
        cur = rec.get('stop')
        if cur is None or rec['side'] * (ns - cur) > EPS:
            out.append(('set_stop', ns))
    return out
