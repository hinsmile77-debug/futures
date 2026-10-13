# -*- coding: utf-8 -*-
"""[MW0602 거래주체분리 2단계] 가상 장부 — 실주문이 안 나가는 주체의 실시간 가상 포지션.

사용자 결정(2026-10-14)
    · 실서버 자동주문 잠금(RealTradingLock)에 막힌 진입도 섀도 · 가상으로 남긴다(①).
    · 가상 손절은 CB② 에서 제외, 가상 거래는 켈리 · 앙상블 학습에서 격리.
    · 미륵 · 신동 · 피터 모두 가상이면 같은 장부로 처리.
"""
import ast
import datetime
import io
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from strategy.runtime import trade_principal as TP   # noqa: E402
from strategy.runtime import virtual_book as VB      # noqa: E402
import strategy.position.position_tracker as PT      # noqa: E402

D = '2026-10-14'
PT_VALUE = 50000.0


@pytest.fixture
def tp_tmp(tmp_path, monkeypatch):
    monkeypatch.setattr(TP, 'DAY_ROOT', str(tmp_path / 'principal'))
    # 🔴 실계좌 상태 파일 — 가상 장부가 이것을 건드리면 안 된다
    monkeypatch.setattr(PT, '_STATE_FILE', str(tmp_path / 'position_state.json'))
    return tmp_path


def _t(hm, sec=0):
    h, m = map(int, hm.split(':'))
    return datetime.datetime(2026, 10, 14, h, m, sec)


def _bar(hm, close, high=None, low=None):
    return {'ts': _t(hm), 'close': close, 'high': close if high is None else high,
            'low': close if low is None else low}


def _vb():
    return VB.VirtualBook(D, PT_VALUE)


# ── A. 격리 ────────────────────────────────────────────────────

def test_virtual_tracker_never_touches_live_state_file(tp_tmp):
    vb = _vb()
    ok, _ = vb.open(TP.MIREUK, 'LONG', 1000.0, 2, 2.0, _t('10:00', 30), 'principal')
    assert ok
    vb.on_bar(_bar('10:01', 1000.5), 2.0, _t('10:02'))
    vb.close_all(1001.0, 'x', _t('10:03'))
    assert not os.path.exists(str(tp_tmp / 'position_state.json'))
    assert os.path.exists(os.path.join(TP.DAY_ROOT, D, VB.LEGS_NAME))


def test_module_does_not_reach_cb_kelly_trades():
    """격리는 구조다 — 가상 장부 소스에 CB · 켈리 · trades · _post_exit 경로가 없다."""
    src = io.open(VB.__file__, encoding='utf-8').read()
    code = '\n'.join(l for l in src.splitlines() if not l.strip().startswith('#'))
    tree = ast.parse(src)
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} | \
            {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    for bad in ('circuit_breaker', 'kelly', 'record_stop_loss', 'record_win', '_post_exit',
                '_record_trade_result', 'TRADES_DB', 'execute'):
        assert bad not in names, bad
    assert 'INSERT' not in code


def test_main_dispatch_is_isolated():
    src = io.open(os.path.join(ROOT, 'main.py'), encoding='utf-8').read()
    tree = ast.parse(src)
    fns = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    for name in ('_ts_vbook_dispatch', '_ts_vbook_on_bar', '_ts_vbook_on_price', '_ts_vbook_open'):
        body = ast.get_source_segment(src, fns[name])
        for bad in ('circuit_breaker', 'kelly', '_record_trade_result', '_post_exit', 'TRADES_DB'):
            assert bad not in body, (name, bad)


# ── B. 미륵 청산 사다리 ────────────────────────────────────────

def test_qty2_tp1_partial_then_breakeven_then_tp2(tp_tmp):
    vb = _vb()
    vb.open(TP.MIREUK, 'LONG', 1000.0, 2, 2.0, _t('10:00', 30), 'principal', entry_horizon='5m')
    t = vb.books[TP.MIREUK]
    tp1, tp2 = t.tp1_price, t.tp2_price
    legs = vb.on_bar(_bar('10:01', tp1 - 0.1, high=tp1 + 0.05, low=999.8), 2.0, _t('10:02'))
    assert len(legs) == 1 and not legs[0]['final'] and legs[0]['qty'] == 1
    assert legs[0]['exit_px'] == round(tp1, 2)                     # TP1 가 체결(틱 근사)
    assert t.stop_price == 1000.0                                  # 본전 이동(tp1_breakeven)
    legs = vb.on_bar(_bar('10:02', tp2 + 0.1), 2.0, _t('10:03'))
    assert len(legs) == 1 and legs[0]['final'] and 'TP2' in legs[0]['reason']
    assert vb.is_flat(TP.MIREUK)
    assert legs[0]['pos_pnl_pts'] > 0


def test_qty1_tp1_is_protect_not_exit(tp_tmp):
    vb = _vb()
    vb.open(TP.MIREUK, 'SHORT', 1000.0, 1, 2.0, _t('10:00', 30), 'principal')
    t = vb.books[TP.MIREUK]
    stop0 = t.stop_price
    legs = vb.on_bar(_bar('10:01', t.tp1_price + 0.1, low=t.tp1_price - 0.05), 2.0, _t('10:02'))
    assert legs == [] and t.partial_1_done and t.stop_price < stop0   # 보호전환(손절이 내려옴)
    assert t.quantity == 1


def test_entry_bar_extremes_ignored_but_later_intrabar_stop_hits(tp_tmp):
    vb = _vb()
    vb.open(TP.MIREUK, 'LONG', 1000.0, 1, 2.0, _t('10:00', 30), 'principal')
    stop = vb.books[TP.MIREUK].stop_price
    # 진입 이전에 시작한 10:00 봉의 저가는 무시
    assert vb.on_bar(_bar('10:00', 1000.0, low=stop - 1), 2.0, _t('10:00', 31)) == []
    legs = vb.on_bar(_bar('10:01', 1000.0, low=stop - 1), 2.0, _t('10:02'))
    assert len(legs) == 1 and legs[0]['final'] and '하드스톱' in legs[0]['reason']
    assert legs[0]['exit_px'] == round(max(stop, stop - 1), 2)


def test_loss_tier1_does_not_fake_tp1(tp_tmp):
    vb = _vb()
    vb.open(TP.MIREUK, 'LONG', 1000.0, 2, 2.0, _t('10:00', 30), 'principal')
    t = vb.books[TP.MIREUK]
    lt = t.loss_tier1_price
    legs = vb.on_bar(_bar('10:01', lt - 0.01), 2.0, _t('10:02'))
    assert len(legs) == 1 and '손절1차' in legs[0]['reason'] and legs[0]['qty'] == 1
    assert t.quantity == 1 and t.loss_tier1_done and not t.partial_1_done
    assert t.initial_quantity == 1


def test_mireuk_cooldown_after_virtual_exit(tp_tmp):
    vb = _vb()
    vb.open(TP.MIREUK, 'LONG', 1000.0, 1, 2.0, _t('10:00', 30), 'principal')
    vb.close_all(999.0, 'x', _t('10:05'))                     # 손실 → 3분
    ok, why = vb.open(TP.MIREUK, 'LONG', 1000.0, 1, 2.0, _t('10:06'), 'principal')
    assert not ok and 'cooldown' in why
    ok, _ = vb.open(TP.MIREUK, 'LONG', 1000.0, 1, 2.0, _t('10:08', 1), 'principal')
    assert ok


def test_busy_blocks_second_open(tp_tmp):
    vb = _vb()
    assert vb.open(TP.MIREUK, 'LONG', 1000.0, 1, 2.0, _t('10:00'), 'principal')[0]
    ok, why = vb.open(TP.MIREUK, 'SHORT', 1000.0, 1, 2.0, _t('10:01'), 'principal')
    assert not ok and 'busy' in why
    # 다른 주체는 별개
    assert vb.open(TP.PETER, 'SHORT', 1000.0, 1, 2.0, _t('10:01'), 'principal', ext_stop=1004.0)[0]


# ── C. 외부 주체(피터 · 신동) ──────────────────────────────────

def test_peter_uses_ext_levels_and_no_cooldown(tp_tmp):
    vb = _vb()
    vb.open(TP.PETER, 'LONG', 1000.0, 1, 2.0, _t('10:00', 30), 'principal',
            ext_stop=996.0, ext_target=1006.0, ext_src='peter')
    t = vb.books[TP.PETER]
    assert t.stop_price == 996.0 and t.tp1_price > 5000          # TP1~3 무력화
    assert vb.on_bar(_bar('10:01', 1003.0, high=1004.0), 2.0, _t('10:02')) == []
    vb.set_ext(TP.PETER, stop=999.0, now=_t('10:02'))
    assert t.stop_price == 999.0
    legs = vb.on_bar(_bar('10:02', 1005.0, high=1006.2), 2.0, _t('10:03'))
    assert len(legs) == 1 and legs[0]['exit_px'] == 1006.0 and '외부목표' in legs[0]['reason']
    assert vb.open(TP.PETER, 'LONG', 1000.0, 1, 2.0, _t('10:03', 5), 'principal', ext_stop=996.0)[0]


def test_shindong_mirror_exit(tp_tmp):
    vb = _vb()
    vb.open(TP.SHINDONG, 'SHORT', 1000.0, 1, 2.0, _t('10:00', 30), 'principal',
            ext_stop=1008.0, ext_target=988.0, ext_src='shindong')
    legs = vb.exit(TP.SHINDONG, 995.0, '가상:신동미러:TR', _t('10:10'))
    assert legs[0]['final'] and legs[0]['pnl_pts'] == 5.0 and legs[0]['source'] == 'SHINDONG'
    assert legs[0]['net_krw'] < legs[0]['gross_krw']                # 수수료 차감


def test_ext_target_on_2s_price(tp_tmp):
    vb = _vb()
    vb.open(TP.PETER, 'SHORT', 1000.0, 1, 2.0, _t('10:00', 30), 'principal',
            ext_stop=1004.0, ext_target=995.0)
    legs = vb.on_price(994.9, _t('10:01', 2))
    assert len(legs) == 1 and legs[0]['exit_px'] == 995.0


# ── D. 15:10 · 영속 · 집계 ────────────────────────────────────

def test_force_exit_1510_on_price(tp_tmp):
    vb = _vb()
    vb.open(TP.MIREUK, 'LONG', 1000.0, 1, 2.0, _t('14:50'), 'real_lock')
    vb.open(TP.PETER, 'LONG', 1000.0, 1, 2.0, _t('14:50'), 'principal', ext_stop=996.0)
    assert vb.on_price(1001.0, _t('15:09', 58)) == []
    legs = vb.on_price(1001.0, _t('15:10', 0))
    assert len(legs) == 2 and all('15:10' in r['reason'] for r in legs)
    assert not vb.open(TP.MIREUK, 'LONG', 1000.0, 1, 2.0, _t('15:11'), 'principal')[0]


def test_snapshot_restore_roundtrip(tp_tmp):
    vb = _vb()
    vb.open(TP.MIREUK, 'LONG', 1000.0, 2, 2.0, _t('10:00', 30), 'real_lock', entry_horizon='3m')
    vb.open(TP.PETER, 'SHORT', 1001.0, 1, 2.0, _t('10:00', 40), 'principal', ext_stop=1005.0)
    vb2 = VB.load(D, PT_VALUE)
    for p in (TP.MIREUK, TP.PETER):
        a, b = vb.books[p], vb2.books[p]
        assert (a.status, a.quantity, a.stop_price, a.tp1_price, a.entry_source, a.entry_time) == \
               (b.status, b.quantity, b.stop_price, b.tp1_price, b.entry_source, b.entry_time)
    assert vb2.meta[TP.MIREUK]['origin'] == 'real_lock'


def test_day_positions_and_status_rows(tp_tmp, tmp_path, monkeypatch):
    from strategy.runtime import principal_views as PV
    vb = VB.VirtualBook(D, PT_VALUE)
    vb.open(TP.MIREUK, 'LONG', 1000.0, 2, 2.0, _t('10:00', 30), 'principal')
    t = vb.books[TP.MIREUK]
    vb.on_bar(_bar('10:01', t.tp1_price), 2.0, _t('10:02'))
    vb.close_all(1001.0, '가상:x', _t('10:05'))
    pos = VB.day_positions(D)
    assert len(pos) == 1 and pos[0]['qty'] == 2 and pos[0]['closed']
    TP.append_shadow(D, 'mireuk_shadow.jsonl', {'ts': D + 'T10:00:30', 'direction': 'LONG',
                                                'price': 1000.0, 'qty': 2, 'grade': 'B'})
    monkeypatch.setattr(PV, 'shindong_shadow_rows', lambda db, d: [])
    monkeypatch.setattr(PV, 'peter_shadow_rows', lambda d: [])
    rows = PV.status_rows(str(tmp_path / 'none.db'), 'x.db', D, 'SHINDONG')
    kinds = [(r['who'], r['kind']) for r in rows]
    assert kinds == [('미륵', '가상')]                       # 1단계 섀도 행은 겹쳐 싣지 않는다


# ── E. main 배선 ──────────────────────────────────────────────

def _main():
    return io.open(os.path.join(ROOT, 'main.py'), encoding='utf-8').read()


def test_real_lock_branch_records_shadow_and_virtual():
    s = _main()
    i = s.index('[RealTradingLock] 실서버 자동진입 차단')
    seg = s[i:i + 2500]
    assert 'append_shadow' in seg and '"blocked_by": "real_lock"' in seg
    assert '_ts_vbook_open(self, _owner' in seg and '"real_lock"' in seg


def test_pipeline_uses_mireuk_flat_but_step8_uses_real_position():
    s = _main()
    assert '_mireuk_flat = _ts_mireuk_entry_flat(self)' in s
    i = s.index('# ── STEP 8: 청산 트리거 감시')
    seg = s[i:i + 600]
    assert 'if self.position.status != "FLAT":\n            self._check_exit_triggers' in seg
    assert '_ts_vbook_on_bar(self, bar' in seg


def test_peter_and_shindong_divert_to_virtual():
    s = _main()
    assert 'if mode == "live" and _ts_real_trading_block_reason(self, PETER2_ENTRY_SOURCE):' in s
    assert 'return self._peter2_execute_virtual(it, mode, date, now)' in s
    assert 'self._shindong_virtual_step(trades, by_key, payload, now)' in s
    assert 'and not _ts_real_trading_block_reason(self, SHINDONG_ENTRY_SOURCE)):' in s


def test_exit_qty_partial_then_rest(tp_tmp):
    vb = _vb()
    vb.open(TP.SHINDONG, 'LONG', 1000.0, 2, 2.0, _t('10:00', 30), 'principal',
            ext_stop=996.0, ext_target=1010.0)
    legs = vb.exit_qty(TP.SHINDONG, 1005.0, 1, '가상:신동1차', _t('10:05'))
    assert len(legs) == 1 and not legs[0]['final'] and vb.books[TP.SHINDONG].quantity == 1
    legs = vb.exit_qty(TP.SHINDONG, 1007.0, 5, '가상:신동최종', _t('10:06'))
    assert legs[0]['final'] and vb.is_flat(TP.SHINDONG)
    assert legs[0]['pos_pnl_pts'] == 12.0
