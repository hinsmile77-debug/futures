# -*- coding: utf-8 -*-
"""[2026-10-20 MW0602] 피터2 실시간 수집 On/Off — 정지 시 장후 사료 흐름으로 전환.

스위치 한 쌍:
    정지      PETER2_COLLECT_MODE="eod"  · PETER2_FOLLOW_MODE="off"
    되돌리기  PETER2_COLLECT_MODE="live" · PETER2_FOLLOW_MODE="live" (+ Chrome 확장 재활성)

고정하는 것
    1. eod ⇒ follow off (피드 없는 추종 = 켜진 척하는 게이트)
    2. 수신기는 eod 에서 포트를 열지 않고 끝난다
    3. 거래주체 「피터」 는 수집·추종이 꺼져 있으면 고를 수 없다
    4. 백필 장후 재생 구간 경계 — [UNTIL, STOP) 제외 · [STOP, 재개일|내일) 포함 · origin 표기
    5. peter2_eod — 이 PC live 0건이면 지연·삭제는 「미측정」
    6. peter_pull 자체 확정이 정지 중 장후 재생 원장을 돈다
"""
import io
import os
import sqlite3
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from strategy.peter2 import backfill as bf                       # noqa: E402
from strategy.peter2.store import peter_principal_block_reason   # noqa: E402


def _src(rel):
    return io.open(os.path.join(ROOT, rel), encoding='utf-8').read()


# ── 1. 설정 ─────────────────────────────────────────────────────────
def test_eod_implies_follow_off():
    import config.settings as s
    assert s.PETER2_COLLECT_MODE in ('live', 'eod')
    if s.PETER2_COLLECT_MODE == 'eod':
        assert s.PETER2_FOLLOW_MODE == 'off', \
            '실시간 수집이 꺼졌는데 추종이 켜져 있다 — 매 신호가 collector_stale 로 기각된다'


def test_stop_date_after_backfill_until():
    import config.settings as s
    assert s.PETER2_COLLECT_STOP_DATE >= s.PETER2_BACKFILL_UNTIL
    r = s.PETER2_COLLECT_RESUME_DATE
    assert r is None or r > s.PETER2_COLLECT_STOP_DATE


# ── 2. 수신기 ───────────────────────────────────────────────────────
def test_receiver_exits_without_binding_when_eod():
    src = _src('tools/peter2_live/receiver.py')
    main = src[src.index('def main():'):]
    # 비활성 분기가 포트 바인딩(_Server) **앞**에 있어야 한다
    assert main.index("mode != 'live'") < main.index('_Server((')
    assert 'DISABLED COLLECT_MODE' in main


def test_receiver_disabled_run(tmp_path):
    """실제로 띄워 본다 — eod 면 즉시 0 으로 끝나야 한다(상주하면 timeout)."""
    import config.settings as s
    if s.PETER2_COLLECT_MODE == 'live':
        return                                   # 정지 상태에서만 의미가 있다
    p = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'peter2_live', 'receiver.py')],
                       cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
    assert p.returncode == 0
    assert b'disabled' in p.stdout


# ── 3. 거래주체 ─────────────────────────────────────────────────────
def test_peter_principal_block_reason():
    assert peter_principal_block_reason('live', 'live') is None
    assert peter_principal_block_reason('shadow', 'live') is None
    assert 'COLLECT_MODE=eod' in peter_principal_block_reason('off', 'eod')
    assert 'COLLECT_MODE=eod' in peter_principal_block_reason('live', 'eod')
    assert 'FOLLOW_MODE=off' in peter_principal_block_reason('off', 'live')


def test_engine_rejects_peter_principal_switch():
    m = _src('main.py')
    body = m[m.index('    def _on_principal_change_requested'):]
    body = body[:body.index('\n    def ')]
    assert 'peter_principal_block_reason' in body
    # 차단 판정이 저장(principal_mod.save) 보다 먼저다
    assert body.index('peter_principal_block_reason') < body.index('principal_mod.save(')


# ── 4. 백필 구간 ────────────────────────────────────────────────────
def test_eod_window():
    assert bf.eod_window(None, None, '2026-10-20') is None
    assert bf.eod_window('2026-10-20', None, '2026-10-20') == ('2026-10-20', '2026-10-21')
    assert bf.eod_window('2026-10-20', None, '2026-10-23') == ('2026-10-20', '2026-10-24')
    # 재개일이 있으면 그날(배타)까지
    assert bf.eod_window('2026-10-20', '2026-10-22', '2026-10-30') == ('2026-10-20', '2026-10-22')
    # 정지일 이전에 돌리면 구간이 없다
    assert bf.eod_window('2026-10-20', None, '2026-10-18') is None


def test_build_spans_two_windows(monkeypatch):
    sys.path.insert(0, os.path.join(ROOT, 'tools'))
    import peter2_backfill as T
    import config.settings as s
    monkeypatch.setattr(s, 'PETER2_BACKFILL_UNTIL', '2026-10-12')
    monkeypatch.setattr(s, 'PETER2_COLLECT_STOP_DATE', '2026-10-20')
    monkeypatch.setattr(s, 'PETER2_COLLECT_RESUME_DATE', None)
    monkeypatch.setattr(s, 'PETER2_COLLECT_MODE', 'eod')
    cal = ['2026-10-08', '2026-10-09', '2026-10-12', '2026-10-13', '2026-10-19',
           '2026-10-20', '2026-10-21']
    monkeypatch.setattr(T, 'trading_days', lambda a, b: [d for d in cal if a <= d < b])
    monkeypatch.setattr(T, 'load_pastes', lambda: {d: (-1.0, '') for d in cal})
    monkeypatch.setattr(T, 'live_peter2_days', lambda until: set())
    monkeypatch.setattr(T, 'load_bars', lambda d: [])
    monkeypatch.setattr(T, 'run_b', lambda d, lat: ('NO_RAW', []))
    monkeypatch.setattr(bf, 'read_unmeasured', lambda p: {})
    _, days, meta, _ = T.build(today='2026-10-21')
    got = {d['trade_date']: d['origin'] for d in days}
    assert got == {'2026-10-08': bf.ORIGIN_PRE_LIVE, '2026-10-09': bf.ORIGIN_PRE_LIVE,
                   '2026-10-20': bf.ORIGIN_EOD_REPLAY, '2026-10-21': bf.ORIGIN_EOD_REPLAY}, \
        '[UNTIL, STOP) 는 실시간 가상장부 구간 — 백필에 들어오면 이중계상이다'
    assert meta['eod_from'] == '2026-10-20' and meta['eod_until'] == '2026-10-22'


def test_build_warns_when_live_without_resume(monkeypatch):
    sys.path.insert(0, os.path.join(ROOT, 'tools'))
    import peter2_backfill as T
    import config.settings as s
    monkeypatch.setattr(s, 'PETER2_BACKFILL_UNTIL', '2026-10-12')
    monkeypatch.setattr(s, 'PETER2_COLLECT_STOP_DATE', '2026-10-20')
    monkeypatch.setattr(s, 'PETER2_COLLECT_RESUME_DATE', None)
    monkeypatch.setattr(s, 'PETER2_COLLECT_MODE', 'live')
    monkeypatch.setattr(T, 'trading_days', lambda a, b: [])
    monkeypatch.setattr(T, 'load_pastes', lambda: {'2026-10-01': (0.0, '')})
    monkeypatch.setattr(T, 'live_peter2_days', lambda until: set())
    monkeypatch.setattr(bf, 'read_unmeasured', lambda p: {})
    _, _, _, warn = T.build(today='2026-10-25')
    assert any('RESUME_DATE' in w for w in warn)


def test_origin_column_migrates_old_db(tmp_path):
    db = str(tmp_path / 'old.db')
    con = sqlite3.connect(db)
    old_ddl = bf.DDL.replace('origin', 'x_unused')     # 열 없는 구판 스키마
    con.executescript(old_ddl)
    con.close()
    day = {'trade_date': '2026-10-20', 'status': bf.ST_NO_TRADE, 'a_n': 0, 'a_pts': 0.0,
           'b_status': 'NO_RAW', 'b_n': None, 'b_pts': None, 'offset': -1.0, 'note': None,
           'origin': bf.ORIGIN_EOD_REPLAY}
    bf.save(db, [], [day], {'until': '2026-10-12'})
    import datetime as _dt
    got = bf.load_for_pnl(db, today=_dt.date(2026, 10, 21))
    assert got['days'][0]['origin'] == bf.ORIGIN_EOD_REPLAY


# ── 5. peter2_eod ───────────────────────────────────────────────────
def test_peter2_eod_marks_unmeasured_without_live():
    s = _src('tools/peter2_eod.py')
    assert "res['live_unmeasured']" in s
    i = s.index("if res['n_live'] == 0:")
    assert "res['deleted'] = None" in s[i:i + 200], 'live 0건인 날 삭제 0건으로 적으면 미측정이 0 으로 둔갑한다'


# ── 6. peter_pull ───────────────────────────────────────────────────
def test_peter_pull_runs_eod_replay_ledger():
    s = _src('tools/peter_pull.py')
    sb = s[s.index('def _self_build():'):s.index('def _eod_replay_ledger():')]
    assert '_eod_replay_ledger()' in sb
    # 오늘 원본이 없어도 원장은 돈다 — return 으로 빠지지 않는다
    import re
    assert not re.search(r'(?m)^\s+return\b', sb.split('"""')[-1])
    led = s[s.index('def _eod_replay_ledger():'):]
    assert 'peter2_backfill.py' in led and "mode == 'live'" in led
