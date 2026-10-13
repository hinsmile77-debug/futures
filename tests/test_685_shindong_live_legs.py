# -*- coding: utf-8 -*-
"""[MW0601 685차] 신동 실집행 — v9 규격(SD-2026-09-29-v2) 레그 분할.

규격(`engine.run_trade(e2=False)`): 2계약 진입 → 1차 목표에서 1계약 → 공통 손절 본전 → 최종 목표.
손절은 트래커 하드스톱, 1차·최종은 2초 폴링(`live_legs.poll`), 재생 대조는 매분(`live_legs.sync`).
"""
import datetime
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from strategy.shindong import live_legs as LL   # noqa: E402
from strategy.shindong import spec as S         # noqa: E402

T10 = datetime.datetime(2026, 10, 13, 10, 0)


def _trade(side=1, entry=1000.0, stop=995.0, t1=1004.0, t2=1010.0, **kw):
    d = {'trade_key': 'R3|10:00|%+d' % side, 'rule': 'R3', 'side': side, 'entry_px': entry,
         'stop_init': stop, 'stop_now': stop, 't1': t1, 't2': t2, 'status': 'OPEN', 'source': 'live'}
    d.update(kw)
    return d


def _src(rel):
    return io.open(os.path.join(ROOT, rel), encoding='utf-8').read()


# ── A. 순수 판단 ───────────────────────────────────────────────

def test_qty_matches_spec_legs():
    """[2026-10-13 사용자 결정] 실계좌 1계약 — 규격(LEGS=2)과 의도적으로 다르다.
    1계약이면 1차 목표의 exit_leg1 이 부분청산이 아니라 전량청산으로 가야 한다(main 분기 고정)."""
    import config.settings as ST
    assert S.LEGS == 2
    assert ST.SHINDONG_LIVE_QTY == 1
    assert ST.PRINCIPAL_SHINDONG_ENABLED is True
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py"),
               encoding="utf-8").read()
    assert 'leg1 = (kind == "exit_leg1" and qty_all >= 2)' in src


def test_entry_check_long_short():
    r = LL.make_rec(_trade())
    assert LL.entry_check(r, 1000.5) is None
    assert LL.entry_check(r, 995.0).startswith('stop_breached')
    assert LL.entry_check(r, 1004.2).startswith('target_passed')
    assert LL.entry_check(r, None) == 'no_price'
    s = LL.make_rec(_trade(side=-1, stop=1005.0, t1=996.0, t2=990.0))
    assert LL.entry_check(s, 999.0) is None
    assert LL.entry_check(s, 1005.5).startswith('stop_breached')
    assert LL.entry_check(s, 995.9).startswith('target_passed')


def test_leg1_then_breakeven_then_final_long():
    r = LL.make_rec(_trade())
    assert LL.poll(r, 1003.9, T10) == []
    assert LL.poll(r, 1004.0, T10) == [('exit_leg1', '신동1차')]
    assert LL.after_leg1(r) == 1000.0 and r['stop'] == 1000.0 and r['leg1_done']
    assert LL.poll(r, 1006.0, T10) == []            # 1차를 다시 보지 않는다
    assert LL.poll(r, 1010.0, T10) == [('exit_all', '신동최종')]


def test_leg1_then_final_short():
    r = LL.make_rec(_trade(side=-1, stop=1005.0, t1=996.0, t2=990.0))
    assert LL.poll(r, 996.0, T10) == [('exit_leg1', '신동1차')]
    LL.after_leg1(r)
    assert r['stop'] == 1000.0
    assert LL.poll(r, 990.0, T10) == [('exit_all', '신동최종')]


def test_single_leg_when_targets_equal_or_gap_through():
    r = LL.make_rec(_trade(t1=1010.0, t2=1010.0))            # 엔진이 t1=None → t1=t2 로 채운 경우
    assert LL.poll(r, 1010.0, T10) == [('exit_all', '신동1차·최종')]
    r2 = LL.make_rec(_trade(t2=None))
    assert LL.poll(r2, 1004.0, T10) == [('exit_all', '신동1차·최종')]
    r3 = LL.make_rec(_trade())                                # 한 번에 최종까지 뛰었다
    assert LL.poll(r3, 1011.0, T10) == [('exit_all', '신동1차·최종')]


def test_no_targets_only_time_exit():
    r = LL.make_rec(_trade(t1=None, t2=None))
    assert LL.poll(r, 1100.0, T10) == []
    assert LL.poll(r, 1000.0, datetime.datetime(2026, 10, 13, 15, 5)) == [('exit_all', '신동시간청산')]
    assert S.TIME_EXIT == '15:05'


def test_breakeven_never_loosens():
    r = LL.make_rec(_trade())
    r['stop'] = 1001.0                                       # 재생이 이미 더 유리하게 조였다
    assert LL.after_leg1(r) is None and r['stop'] == 1001.0


def test_sync_mirror_and_retract():
    r = LL.make_rec(_trade())
    assert LL.sync(r, _trade(), T10) == []
    assert LL.sync(r, _trade(leg1_reason='TP1', stop_now=1000.0), T10) == \
        [('exit_leg1', '신동미러:TP1'), ('set_stop', 1000.0)]
    assert LL.sync(r, _trade(stop_now=990.0), T10) == []    # 불리하게는 안 움직인다
    assert LL.sync(r, _trade(status='CLOSED', leg1_reason='SL', leg2_reason='SL'), T10) == \
        [('exit_all', '신동미러:SL')]
    assert LL.sync(r, None, T10) == [('retracted',)]          # 철회는 청산 사유가 아니다
    r['retracted'] = True
    assert LL.sync(r, None, T10) == []
    r['done'] = True
    assert LL.sync(r, _trade(status='CLOSED'), T10) == [] and LL.poll(r, 2000.0, T10) == []


def test_matches_engine_semantics():
    """엔진 run_trade(e2=False) — 1차 익절 즉시 공통 손절 본전. 실행기가 같은 규칙인지 고정한다."""
    from strategy.shindong import engine as E
    candles = {'10:00': (1000, 1000, 1000, 1000.0), '10:01': (1000, 1004.5, 999.5, 1003.0),
               '10:02': (1003, 1003, 999.8, 1000.0)}
    d = E.DayFrame(candles, {}, horizon='15:08')
    tr = E.run_trade(d, 1, '10:00', 995.0, 1004.0, 1010.0)
    assert tr['legs'][0]['reason'] == 'TP1' and tr['legs'][1]['reason'] == 'BE'
    r = LL.make_rec(_trade())
    LL.poll(r, 1004.0, T10)
    LL.after_leg1(r)
    assert r['stop'] == tr['legs'][1]['px'] == 1000.0


# ── B. main 배선 ───────────────────────────────────────────────

def test_main_wiring():
    s = _src('main.py')
    run = s[s.index('    def _run_shindong(self'):s.index('    def _sd_exec_load')]
    assert 'self._shindong_exec_step(payload, now)' in run
    step = s[s.index('    def _shindong_exec_step'):s.index('    def _shindong_adopt')]
    assert 'self._principal_state["principal"] != principal_mod.SHINDONG' in step
    assert 'entry_source=SHINDONG_ENTRY_SOURCE' in step and 'SHINDONG_LIVE_QTY' in step
    # 보유 포지션 관리는 주체 판정보다 **앞**이다 — 주체를 바꿔도 들고 있는 신동 포지션은 끝까지 관리
    assert step.index('pos.is_external_of(SHINDONG_ENTRY_SOURCE)') < step.index('principal_mod.SHINDONG')
    tick = s[s.index('    def _peter2_tick(self)'):s.index('    def _peter2_last_price')]
    assert 'self._shindong_target_poll()' in tick and 'self._push_principal_ui()' in tick
    for a in ('self._sd_exec = {}', 'self._sd_exec_day = None', 'self._sd_exec_skipped = set()',
              'self._sd_exec_orphan_warned = False'):
        assert a in s, a                                   # __init__ 명시 초기화(계측 4원칙 ④)
    assert '    def _peter2_last_price(self):' in s        # 616 이식본 _ts_refresh_principal_views 가 부른다
    ap = s[s.index('    def _shindong_apply'):s.index('    def _save_program_trade_raw')]
    assert 'kind="EXIT_MANUAL_PARTIAL"' in ap and 'kind="EXIT_FULL"' in ap
    assert '_ll.after_leg1(rec)' in ap


def test_no_new_qtimer():
    """617차 슬롯 래칫 — 신동 실행은 기존 타이머(수급 1분 · 피터2 2초)에 얹는다."""
    s = _src('main.py')
    blk = s[s.index('    def _sd_exec_load'):s.index('    def _save_program_trade_raw')]
    assert 'QTimer' not in blk
