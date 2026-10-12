# -*- coding: utf-8 -*-
"""[MW0602 615차 후속2] 피터2 오프셋 장중 자동 실측.

2026-10-12(10/8 만기 다음 첫날): 직전 실측 −4.88(safe=False)로 하루 종일 진입 0건.
그날 실제 「미니 − 정규 10100」은 08:50부터 −2.0~−2.3. 장 초반 차트 TR 로 잴 수 있었다.
사용자 결정(2026-10-12): 평일에도 당일 자동 실측이 직전일 값보다 우선한다.
"""
import io
import json
import os
import sqlite3
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from strategy.peter2 import offset_live as OL   # noqa: E402
from strategy.peter2 import store               # noqa: E402

YMD = 20261012


def _rows(pairs, ymd=YMD):
    return [{'date': ymd, 'time': t, 'close': c} for t, c in pairs]


def _labels(start, n):
    out, h, m = [], start // 100, start % 100
    for _ in range(n):
        out.append(h * 100 + m)
        m += 1
        if m == 60:
            h, m = h + 1, 0
    return out


def _pair(labels, offs, base=1037.0):
    reg = _rows([(l, base + i * 0.1) for i, l in enumerate(labels)])
    mini = _rows([(l, base + i * 0.1 + o) for i, (l, o) in enumerate(zip(labels, offs))])
    return mini, reg


# ── 순수 함수 ──────────────────────────────────────────────────

def test_stable_open_is_safe():
    labs = _labels(846, 10)                                   # 08:46~08:55
    mini, reg = _pair(labs, [-2.2, -2.18, -2.22, -2.2, -2.21, -2.19, -2.2, -2.2, -2.23, -2.2])
    m = OL.measure(mini, reg, YMD, 855)
    assert m['value'] == pytest.approx(-2.2, abs=0.02)
    assert m['n'] == 10 and m['safe'] is True and m['reason'] == 'ok'
    assert (m['first'], m['last']) == ('08:46', '08:55')


def test_forming_bar_excluded():
    """라벨 = 봉 종료 시각. 지금 시각을 넘는 라벨은 형성 중이라 쓰지 않는다."""
    labs = _labels(846, 10)
    mini, reg = _pair(labs, [-2.2] * 9 + [-9.0])               # 08:55 봉만 튐
    m = OL.measure(mini, reg, YMD, 854)
    assert m['n'] == 9 and m['value'] == -2.2


def test_too_few_minutes_not_safe():
    labs = _labels(846, 5)
    mini, reg = _pair(labs, [-2.2] * 5)
    m = OL.measure(mini, reg, YMD, 850)
    assert m['value'] == -2.2 and m['safe'] is False and '표본 부족' in m['reason']


def test_drifting_window_not_safe():
    """만기일(10-08) 개장처럼 5분 슬롯 사이가 0.3pt 넘게 벌어지면 safe 가 아니다."""
    labs = _labels(846, 10)
    mini, reg = _pair(labs, [-5.3] * 4 + [-4.8] * 6)          # 08:46~49 / 08:50~55
    m = OL.measure(mini, reg, YMD, 855)
    assert m['spread'] == pytest.approx(0.5, abs=0.01)
    assert m['safe'] is False and '불안정' in m['reason']


def test_lookback_tracks_intraday_drift():
    """최근 30분으로 잰다 — 오전 값에 붙박이지 않는다(596차 일중 드리프트)."""
    labs = _labels(900, 90)
    mini, reg = _pair(labs, [-4.0] * 60 + [-3.6] * 30)
    m = OL.measure(mini, reg, YMD, 1030)
    assert m['value'] == -3.6 and m['n'] == 30
    assert m['full'] == -4.0 and m['n_full'] == 90           # 전일정 중앙값은 함께 보고


def test_other_date_and_missing_inputs():
    labs = _labels(846, 10)
    mini, reg = _pair(labs, [-2.2] * 10)
    old = _rows([(l, 1.0) for l in labs], ymd=20261008)
    assert OL.measure(old, reg, YMD, 900)['reason'] == '미니 분봉 없음'
    assert OL.measure(mini, [], YMD, 900)['reason'] == '정규 10100 분봉 없음'
    assert OL.measure(mini, reg, YMD, 845)['reason'] == '짝지어진 완성봉 없음'


def test_real_20261012_open_window():
    """실데이터 — 10-12 08:46~08:55 를 차트 라벨 규약으로 재구성해 −2.0~−2.3 이 나오는지.

    raw_candles·regular_candles 의 ts 는 봉 **시작** 시각이라 +1분 해 종료 라벨로 바꾼다.
    DB 가 없는 PC 에서는 건너뛴다.
    """
    rc = os.path.join(ROOT, 'data', 'db', 'regular_candles.db')
    rd = os.path.join(ROOT, 'data', 'db', 'raw_data.db')
    if not (os.path.exists(rc) and os.path.exists(rd)):
        pytest.skip('DB 없음')

    def lab(ts):
        h, m = int(ts[11:13]), int(ts[14:16]) + 1
        if m == 60:
            h, m = h + 1, 0
        return h * 100 + m

    def q(path, sql, *a):
        con = sqlite3.connect('file:%s?mode=ro' % path.replace('\\', '/'), uri=True)
        try:
            return con.execute(sql, a).fetchall()
        finally:
            con.close()

    reg = q(rc, "SELECT ts, close FROM regular_candles WHERE code='10100' AND trade_date='2026-10-12'")
    mini = q(rd, "SELECT ts, close FROM raw_candles WHERE ts LIKE '2026-10-12%'")
    if not reg or not mini:
        pytest.skip('2026-10-12 데이터 없음')
    m = OL.measure(_rows([(lab(t), c) for t, c in mini]), _rows([(lab(t), c) for t, c in reg]),
                   YMD, 855)
    assert -2.4 <= m['value'] <= -1.8, m
    assert m['safe'] is True, m


# ── store 우선순위 ─────────────────────────────────────────────

def _prev_db(tmp_path, date, off):
    p = str(tmp_path / 'peter_levels.db')
    con = sqlite3.connect(p)
    con.execute('CREATE TABLE IF NOT EXISTS peter_paste (date TEXT, offset REAL)')
    con.execute('INSERT INTO peter_paste VALUES (?, ?)', (date, off))
    con.commit()
    con.close()
    return p


def test_priority_override_then_live_then_prev(tmp_path, monkeypatch):
    monkeypatch.setattr(store, 'LIVE_DIR', str(tmp_path / 'live'))
    monkeypatch.setattr(store, 'PETER_DB', _prev_db(tmp_path, '2026-10-08', -4.88))
    D = '2026-10-12'
    off, src, safe = store.load_offset(D)                     # 3. 직전일 — 만기를 넘어 unsafe
    assert (off, safe) == (-4.88, False) and src.startswith('prev_day:')

    store.write_offset_live(D, {'value': -2.21, 'safe': False, 'measured_at': '08:50:10'})
    assert store.load_offset(D)[0] == -4.88                   # 자동 실측 unsafe → 직전일로

    store.write_offset_live(D, {'value': -2.2, 'safe': True, 'measured_at': '08:55:10'})
    assert store.load_offset(D) == (-2.2, 'live:08:55:10', True)   # 2. 자동 실측 safe

    ov = tmp_path / 'live' / D / 'offset_override.json'
    ov.write_text(json.dumps({'offset': -2.29, 'src': 'broker_chart'}), encoding='utf-8')
    assert store.load_offset(D) == (-2.29, 'override:broker_chart', True)   # 1. 수동


def test_live_beats_safe_prev_day_on_weekday(tmp_path, monkeypatch):
    """평일(만기 안 넘음) — 직전일도 safe 지만 당일 실측이 이긴다(사용자 결정 2026-10-12)."""
    monkeypatch.setattr(store, 'LIVE_DIR', str(tmp_path / 'live'))
    monkeypatch.setattr(store, 'PETER_DB', _prev_db(tmp_path, '2026-10-12', -2.20))
    D = '2026-10-13'
    assert store.load_offset(D)[2] is True
    store.write_offset_live(D, {'value': -2.55, 'safe': True, 'measured_at': '10:00:00'})
    assert store.load_offset(D)[0] == -2.55


def test_live_file_broken_or_empty_is_none(tmp_path, monkeypatch):
    monkeypatch.setattr(store, 'LIVE_DIR', str(tmp_path))
    D = '2026-10-12'
    assert store.load_offset_live(D) is None
    store.write_offset_live(D, {'value': None, 'safe': False, 'reason': '정규 10100 분봉 없음'})
    assert store.load_offset_live(D) is None                  # 못 잰 것은 값이 아니다(②)
    io.open(store.live_offset_path(D), 'w', encoding='utf-8').write(u'{broken')
    assert store.load_offset_live(D) is None


# ── main 배선 ─────────────────────────────────────────────────

def _src(rel):
    return io.open(os.path.join(ROOT, rel), encoding='utf-8').read()


def test_main_wiring():
    s = _src('main.py')
    for a in ('self._peter2_live_offset_mtime = None', 'self._peter2_offset_next_at = None',
              'self._peter2_offset_date = None'):
        assert a in s, a                                     # __init__ 명시 초기화(계측 4원칙 ④)
    sched = s[s.index('    def _scheduler_tick(self)'):]
    sched = sched[:sched.index('\n    def ')]
    assert 'self._peter2_measure_offset(now)' in sched
    tick = s[s.index('    def _peter2_tick_body(self)'):s.index('    def _peter2_update_button')]
    assert (tick.index('self._peter2_apply_override(date, now)')
            < tick.index('self._peter2_apply_live_offset(date, now)') < tick.index('read_new()'))


def test_measure_never_writes_regular_candles():
    """장중 부분 데이터를 장후 수집기의 정본 DB 에 섞지 않는다(595차 신선도 감시 보호)."""
    s = _src('main.py')
    body = s[s.index('    def _peter2_measure_offset'):s.index('    def _peter2_tick_body')]
    assert 'regular_candles' not in body.replace('regular_candles.db 는', '')
    assert 'write_offset_live' in body and 'request_futopt_minute_bars("10100"' in body
    ap = s[s.index('    def _peter2_apply_live_offset'):s.index('    def _peter2_measure_offset')]
    assert 'peter2_store.load_offset(date)' in ap             # 우선순위는 store 한 곳
    assert 'why="offset_live"' in ap and 'fw.armed = None' in ap


def test_latency_report_threshold_is_preregistered():
    from tools.peter2_live import latency_report as LR
    assert LR.P90_LIMIT_SEC == 90
    import config.settings as S
    assert LR.P90_LIMIT_SEC == S.PETER2_HEARTBEAT_STALE_SEC
