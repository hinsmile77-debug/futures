# -*- coding: utf-8 -*-
"""[MW0602 616차 / 거래주체분리] 미륵 · 신동 · 피터 — 계좌에서 실거래하는 주체는 하나.

사용자 결정(2026-10-12): 신동 = V2(FLOWC) · FLAT 이면 장중 언제든 전환 · 전날 선택 유지 ·
신동 2계약 2레그 · 미륵 섀도 1단계(기록 + 장후 가상 손익) · 신동 손익은 CREON 요율.
계획: docs/거래주체분리/거래주체분리_구현계획_MW0602-20261012.md
"""
import datetime
import io
import json
import os
import sqlite3
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from strategy.runtime import trade_principal as TP   # noqa: E402

# 브랜치 판별 — dev 에는 신동 V2(FLOWC, families.py)와 그 실행기가 있고, v9-dev 에는 없다
#   (v9-dev 신동은 R2/R3 레그 분할 규격이라 실집행 미지원 · PRINCIPAL_SHINDONG_ENABLED=False).
HAS_FLOWC = os.path.exists(os.path.join(ROOT, 'strategy', 'shindong', 'families.py'))


@pytest.fixture
def tp_tmp(tmp_path, monkeypatch):
    monkeypatch.setattr(TP, 'STATE_PATH', str(tmp_path / 'trade_principal.json'))
    monkeypatch.setattr(TP, 'LOG_PATH', str(tmp_path / 'trade_principal_log.jsonl'))
    monkeypatch.setattr(TP, 'DAY_ROOT', str(tmp_path / 'principal'))
    # 파일 기준 동작을 본다 — Sindong-V4 는 PRINCIPAL_LOCK="SHINDONG" 이라 고정을 풀어 둔다(고정은 test_renewal_principal_lock).
    from config import settings as _s
    monkeypatch.setattr(_s, 'PRINCIPAL_LOCK', None, raising=False)
    return tmp_path


# ── A. 상태 모듈 ───────────────────────────────────────────────

def test_default_is_mireuk_but_marked_unmeasured(tp_tmp):
    st = TP.load()
    assert st['principal'] == 'MIREUK' and st['measured'] is False   # 기본값을 선택값처럼 보이지 않게


def test_save_persists_and_carries_over(tp_tmp):
    TP.save('SHINDONG', reason='test', now=datetime.datetime(2026, 10, 12, 10, 0))
    st = TP.load()
    assert st['principal'] == 'SHINDONG' and st['measured'] is True
    # 다음 날에도 유지 — 파일에 날짜 관문이 없다(사용자 결정: 전날 선택 유지)
    assert TP.current() == 'SHINDONG'
    TP.save('PETER', reason='test2')
    log = [json.loads(l) for l in io.open(TP.LOG_PATH, encoding='utf-8')]
    assert [r['principal'] for r in log] == ['SHINDONG', 'PETER']
    assert log[1]['prev'] == 'SHINDONG'
    with pytest.raises(ValueError):
        TP.save('NOBODY')


def test_broken_file_falls_back(tp_tmp):
    io.open(TP.STATE_PATH, 'w', encoding='utf-8').write(u'{broken')
    assert TP.load()['principal'] == 'MIREUK' and TP.load()['measured'] is False


def test_can_switch_only_when_flat_and_no_pending():
    assert TP.can_switch('FLAT', False) == (True, 'ok')
    assert TP.can_switch('LONG', False)[0] is False
    assert TP.can_switch('FLAT', True)[0] is False


def test_source_gate_mapping():
    assert TP.is_live_source('SYSTEM_AUTO', 'MIREUK')
    assert not TP.is_live_source('SYSTEM_AUTO', 'SHINDONG')
    assert TP.is_live_source('SHINDONG', 'SHINDONG') and not TP.is_live_source('SHINDONG', 'PETER')
    assert TP.is_live_source('PETER2', 'PETER') and not TP.is_live_source('PETER2', 'MIREUK')
    # 운영·복구 출처는 주체와 무관하게 통과(실계좌와 엔진 상태가 갈라지면 안 된다)
    for src in ('OPERATOR_MANUAL', 'BROKER_SYNC_RECOVERY', 'GHOST_PENDING_MISS', 'OPERATOR_RESTORE'):
        for p in TP.PRINCIPALS:
            assert TP.is_live_source(src, p), (src, p)


# ── B. 신동 실집행 판단 ─────────────────────────────────────────

from strategy.shindong import live_exec as LX   # noqa: E402


def _t(key, entry_ts, status='OPEN', side=1, source='live', **kw):
    d = {'trade_key': key, 'entry_ts': entry_ts, 'status': status, 'side': side, 'source': source,
         'entry_px': 1000.0, 'stop_init': 980.0, 'stop_now': 980.0, 't1': 1012.0}
    d.update(kw)
    return d


def test_pick_fresh_entry_only():
    now = datetime.datetime(2026, 10, 12, 10, 3, 20)
    fresh = _t('FLOW|10:02|1', '2026-10-12 10:02:00')        # 봉 끝 10:03 → 0.3분
    old = _t('FLOW|09:40|1', '2026-10-12 09:40:00')
    back = _t('FLOW|10:02b', '2026-10-12 10:02:00', source='backfill')
    pick, stale = LX.pick_new_entry([old, fresh, back], {}, now, 2)
    assert pick['trade_key'] == 'FLOW|10:02|1'
    assert [t['trade_key'] for t in stale] == ['FLOW|09:40|1']
    pick2, _ = LX.pick_new_entry([fresh], {'FLOW|10:02|1': {}}, now, 2)   # 이미 집행
    assert pick2 is None


def test_manage_trail_mirror_time_retract():
    now = datetime.datetime(2026, 10, 12, 11, 0)
    rec = {'side': 1, 'stop': 980.0}
    assert LX.manage(rec, _t('k', 'x', stop_now=1002.0), now) == [('set_stop', 1002.0)]
    assert LX.manage(rec, _t('k', 'x', stop_now=975.0), now) == []          # 불리하게는 안 움직인다
    short = {'side': -1, 'stop': 1020.0}
    assert LX.manage(short, _t('k', 'x', side=-1, stop_now=1010.0), now) == [('set_stop', 1010.0)]
    assert LX.manage(rec, _t('k', 'x', status='CLOSED', leg1_reason='TR'), now) == [('exit', '신동미러:TR')]
    assert LX.manage(rec, None, now) == [('retracted',)]                      # 청산 사유 아님
    assert LX.manage(dict(rec, retracted=True), None, now) == []
    assert LX.manage(rec, _t('k', 'x'), datetime.datetime(2026, 10, 12, 15, 5)) == [('exit', '신동시간청산')]


@pytest.mark.skipif(not HAS_FLOWC, reason='v9-dev — 신동 V2(FLOWC) 없음')
def test_flowc_two_legs_close_together():
    """2계약 2레그 = 일괄 청산의 근거 — FLOWC 의 두 레그는 같은 청산가·같은 시각이다."""
    from strategy.shindong import families as F
    src = io.open(F.__file__, encoding='utf-8').read()
    body = src[src.index('def _run_position'):src.index('def _run_signal')]
    assert '"t1": tp_px, "t2": tp_px' in body
    assert 'for n in (1, 2):' in body and 'E.leg_net(side, e, exit_px, mkt)' in body


# ── C. 외부 손절·목표 일반화 ────────────────────────────────────

def _tracker(tmp_path, monkeypatch):
    import strategy.position.position_tracker as T
    monkeypatch.setattr(T, '_STATE_FILE', str(tmp_path / 'ps.json'))
    return T.PositionTracker()


def test_tracker_ext_levels_for_shindong(tmp_path, monkeypatch):
    p = _tracker(tmp_path, monkeypatch)
    p.entry_source = 'SHINDONG'
    p.set_external_levels(stop=981.0, target=1012.0, src='shindong')
    p.open_position('LONG', 1000.0, 2, 3.0)
    assert p.is_external() and p.is_external_of('SHINDONG') and not p.is_external_of('PETER2')
    assert p.stop_price == 981.0
    assert p.is_ext_target_hit(1012.0) and not p.is_ext_target_hit(1011.9)
    r = p.close_position(1012.0, '신동익절')
    assert r['pos_entry_src'] == 'SHINDONG'


def test_external_sources_constant():
    from config.constants import EXTERNAL_ENTRY_SOURCES, SHINDONG_ENTRY_SOURCE
    from config.settings import PROFIT_GUARD_SYSTEM_SOURCES
    assert set(EXTERNAL_ENTRY_SOURCES) == {'PETER2', 'SHINDONG'}
    assert SHINDONG_ENTRY_SOURCE not in PROFIT_GUARD_SYSTEM_SOURCES   # 「시스템 거래」에서 빠진다


# ── D. 미륵 섀도 장후 가상 손익 ─────────────────────────────────

from strategy.runtime import mireuk_shadow_eval as MSE   # noqa: E402


def _bars(seq, start='10:01'):
    h, m = int(start[:2]), int(start[3:])
    out = []
    for hi, lo, c in seq:
        out.append(('%02d:%02d' % (h, m), hi, lo, c))
        m += 1
        if m == 60:
            h, m = h + 1, 0
    return out


def test_shadow_eval_stop_tp_time_overlap():
    e = lambda ts, d='LONG', atr=2.0: {'ts': '2026-10-12T%s:00' % ts, 'direction': d, 'price': 1000.0,
                                       'qty': 1, 'atr': atr, 'entry_horizon': '1m', 'extra_stop_mult': 1.0}
    tp_mult = {'1m': 0.3}
    # 10:00 매수 → 손절 997 · 목표 1000.6. 10:01 봉 고가 1000.7 → tp1
    bars = _bars([(1000.7, 999.5, 1000.5), (1001, 1000, 1000.8)], '10:01')
    r = MSE.simulate([e('10:00')], bars, 1.5, tp_mult, 1.0, 0.000019, 50000)[0]
    assert r['reason'] == 'tp1' and r['exit_px'] == 1000.6
    assert r['net_krw'] == round(0.6 * 50000 - (1000 + 1000.6) * 50000 * 0.000019)
    # 같은 봉에서 둘 다 닿으면 손절(보수적)
    bars2 = _bars([(1001.0, 996.0, 999.0)], '10:01')
    assert MSE.simulate([e('10:00')], bars2, 1.5, tp_mult, 1.0, 0.0, 50000)[0]['reason'] == 'stop'
    # 아무것도 안 닿으면 15:10 직전 봉 종가
    bars3 = _bars([(1000.3, 999.8, 1000.1)] * 3, '15:08')
    r3 = MSE.simulate([e('15:07')], bars3, 1.5, tp_mult, 1.0, 0.0, 50000)[0]
    assert r3['reason'] == 'time' and r3['exit_hm'] == '15:09'
    # 가상 보유 중 들어온 섀도 진입은 overlap(단일 포지션)
    bars4 = _bars([(1000.2, 999.9, 1000.0)] * 5, '10:01')
    rs = MSE.simulate([e('10:00'), e('10:02')], bars4 + _bars([(1000.7, 1000, 1000.6)], '10:06'),
                      1.5, tp_mult, 1.0, 0.0, 50000)
    assert rs[0]['reason'] == 'tp1' and rs[1]['reason'] == 'overlap' and rs[1]['net_krw'] is None


# ── E. 화면 집계 ───────────────────────────────────────────────

from strategy.runtime import principal_views as PV   # noqa: E402


def _trades_db(path, rows):
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE trades (entry_ts TEXT, exit_ts TEXT, direction TEXT, entry_price REAL, "
                "exit_price REAL, quantity INTEGER, pnl_krw REAL, gross_pnl_krw REAL, net_pnl_krw REAL, "
                "exit_reason TEXT, entry_source TEXT)")
    con.executemany("INSERT INTO trades VALUES (?,?,?,?,?,?,?,?,?,?,?)", rows)
    con.commit()
    con.close()


def test_principal_summary_is_position_unit(tmp_path):
    db = str(tmp_path / 't.db')
    D = '2026-10-12'
    _trades_db(db, [
        # SHINDONG 1포지션 2레그
        (D + ' 10:00:00', D + ' 10:20:00', 'LONG', 1000, 1012, 1, 600000, 600000, 598000, 'TP', 'SHINDONG'),
        (D + ' 10:00:00', D + ' 10:20:00', 'LONG', 1000, 1012, 1, 600000, 600000, 598000, 'TP', 'SHINDONG'),
        # 같은 날 섞인 수동 거래
        (D + ' 11:00:00', D + ' 11:05:00', 'SHORT', 1010, 1011, 1, -50000, -50000, -52000, 'SL', 'OPERATOR_MANUAL'),
        # 전날 미륵
        ('2026-10-08 10:00:00', '2026-10-08 10:10:00', 'LONG', 990, 991, 1, 50000, 50000, 48000, 'TP1', 'SYSTEM_AUTO'),
    ])
    s = PV.principal_summary(db, D, 'SHINDONG')
    assert s['n'] == 1 and s['net'] == 1196000 and s['others'] == {'OPERATOR_MANUAL': -52000}
    assert PV.prev_trade_date(db, D) == '2026-10-08'
    assert PV.principal_summary(db, '2026-10-08', 'MIREUK')['net'] == 48000
    rows = PV.live_rows(db, D, 'SHINDONG')
    assert len(rows) == 1 and rows[0]['qty'] == 2 and rows[0]['pnl'] == 1196000


def test_status_rows_shadow_for_unselected(tmp_path, tp_tmp, monkeypatch):
    db = str(tmp_path / 't.db')
    _trades_db(db, [])
    D = '2026-10-12'
    TP.append_shadow(D, 'mireuk_shadow.jsonl', {'ts': D + 'T10:05:00', 'direction': 'SHORT',
                                                'price': 1005.0, 'qty': 1, 'grade': 'B'})
    monkeypatch.setattr(PV, 'shindong_shadow_rows', lambda db, d: [
        {'time': '09:40', 'who': '신동', 'kind': '섀도', 'side': '매수', 'qty': 2}])
    monkeypatch.setattr(PV, 'peter_shadow_rows', lambda d: [])
    rows = PV.status_rows(db, 'x.db', D, 'PETER')
    assert [(r['who'], r['kind']) for r in rows] == [('신동', '섀도'), ('미륵', '섀도')]
    rows2 = PV.status_rows(db, 'x.db', D, 'MIREUK')     # 선택 주체 자신은 섀도로 안 나온다
    assert all(r['who'] != '미륵' for r in rows2)


# ── F. main · 대시보드 배선 ─────────────────────────────────────

def _src(rel):
    return io.open(os.path.join(ROOT, rel), encoding='utf-8').read()


def test_main_gate_is_first_and_exits_untouched():
    s = _src('main.py')
    fn = s[s.index('def _ts_execute_entry('):]
    fn = fn[:fn.index('\ndef ')]
    g = fn.index('principal_mod.is_live_source(entry_source, _principal)')
    assert g < fn.index('is_entry_paused()') < fn.index('_send_broker_entry_order')
    # 청산 주문 함수는 거래주체를 보지 않는다
    ex = s[s.index('    def _send_broker_exit_order'):]
    ex = ex[:ex.index('\n    def ')]
    assert 'principal' not in ex


def test_manual_entry_passes_operator_source():
    s = _src('main.py')
    assert 'self._execute_entry(direction, price, qty, atr, grade, entry_source="OPERATOR_MANUAL")' in s


def test_peter_live_only_when_selected():
    s = _src('main.py')
    tick = s[s.index('    def _peter2_tick_body(self)'):s.index('    def _peter2_update_button')]
    assert 'if mode == "live" and self._principal_state["principal"] != principal_mod.PETER:' in tick
    d = _src('dashboard/main_dashboard.py')
    if '    def _peter2_mode()' in d:                  # dev 만 패널 배너가 실효 모드를 읽는다
        pm = d[d.index('    def _peter2_mode()'):]
        pm = pm[:pm.index('\n    def ')]
        assert '_tp.current() != _tp.PETER' in pm


def test_shindong_disabled_on_branch_without_flowc():
    """v9-dev — 신동 실집행을 붙이지 않고, 버튼·전환 처리기가 신동을 거부한다."""
    if HAS_FLOWC:
        pytest.skip('dev — 신동 실행기 있음')
    import config.settings as S
    assert S.PRINCIPAL_SHINDONG_ENABLED is False
    s = _src('main.py')
    assert '_shindong_exec_step' not in s and '_shindong_target_poll' not in s
    ch = s[s.index('    def _on_principal_change_requested'):]
    ch = ch[:ch.index('\n    def ')]
    assert 'PRINCIPAL_SHINDONG_ENABLED' in ch
    assert 'self._principal_disabled' in _src('dashboard/main_dashboard.py')


@pytest.mark.skipif(not HAS_FLOWC, reason='v9-dev — 신동 실행기 없음')
def test_shindong_exec_wired():
    s = _src('main.py')
    run = s[s.index('    def _run_shindong(self'):s.index('    def _sd_exec_load')]
    assert 'self._shindong_exec_step(payload, now)' in run
    step = s[s.index('    def _shindong_exec_step'):s.index('    def _shindong_entry_block_reason')]
    assert 'self._principal_state["principal"] == principal_mod.SHINDONG' in step
    assert 'entry_source=SHINDONG_ENTRY_SOURCE' in step and 'SHINDONG_LIVE_QTY' in step
    tick = s[s.index('    def _peter2_tick(self)'):s.index('    def _peter2_last_price')]
    assert 'self._shindong_target_poll()' in tick and 'self._push_principal_ui()' in tick
    for a in ('self._principal_state = principal_mod.load()', 'self._sd_exec = {}',
              'self._sd_exec_day = None', 'self._principal_prev_cache = None'):
        assert a in s, a                                   # __init__ 명시 초기화(계측 4원칙 ④)
    import config.settings as S
    assert S.SHINDONG_LIVE_QTY == 2      # [MW0602 2026-10-21 사용자 결정] 1 → 2 (10-13 실거래 전환 때 2 → 1)


def test_isolation_and_cooldown_cover_shindong():
    s = _src('main.py')
    # dev 는 부분청산 2곳 + 최종청산 1곳, v9-dev 는 최종청산 1곳(부분청산은 원래 피터2 도 격리 안 함)
    assert s.count('_is_ext = (result.get("pos_entry_src") in EXTERNAL_ENTRY_SOURCES)') == (3 if HAS_FLOWC else 1)
    assert 'and not _is_ext:' in s                         # 앙상블 학습 격리
    assert 'if entry_source in EXTERNAL_ENTRY_SOURCES:\n        cooldown_active = False' in s


def test_dashboard_wiring():
    d = _src('dashboard/main_dashboard.py')
    assert 'sig_principal_change_requested = pyqtSignal(str)' in d
    assert 'self._build_principal_buttons(_commit_row)' in d
    assert 'title_widget=self.account_info_panel.lbl_principal' in d
    assert 'self.trade_status_panel = TradeStatusPanel()' in d
    assert '"총평가": "수익율_표시"' in d
    s = _src('main.py')
    assert 'self.dashboard.sig_principal_change_requested.connect(self._on_principal_change_requested)' in s


def test_no_non_ascii_strftime_in_new_code():
    """557차 규약 — strftime 포맷에 한글을 넣지 않는다(로케일 코덱 ASCII)."""
    import re
    for rel in ('strategy/runtime/trade_principal.py', 'strategy/runtime/principal_views.py',
                'strategy/runtime/mireuk_shadow_eval.py', 'strategy/shindong/live_exec.py'):
        for m in re.finditer(r'strftime\((["\'])(.*?)\1', _src(rel)):
            assert all(ord(ch) < 128 for ch in m.group(2)), (rel, m.group(2))
