# -*- coding: utf-8 -*-
"""[MW0601 698차] 피터2 단독 수집 추적 — 사전등록 판정 고정.

2026-10-20 MW0602 수집기 중지(사용자 결정) 효과를 `sole_collect_tracker.py` 가 판정한다.
합성 로그로 판정 분기(IMPROVED / STILL_SHARED / NOT_LIMIT / IN_PROGRESS)와
「미측정 ≠ 0」(계측 4원칙 ②)을 고정한다. 기준값이 바뀌면 이 테스트가 깨진다.
"""
import datetime as D
import importlib.util
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'peter2_live'))
import latency_report as LR          # noqa: E402
import sole_collect_tracker as T     # noqa: E402

EVAL = ['2026-10-20', '2026-10-21', '2026-10-22', '2026-10-23', '2026-10-26']


def _write_day(root, date, per_req_drop, lat_sec, n_tweets=8, n429=0):
    """한도 창 4개(15분)마다 우리 요청 10줄. 우리 요청 사이 rem 감소폭 = per_req_drop."""
    ymd = date.replace('-', '')
    os.makedirs(os.path.join(root, 'logs'), exist_ok=True)
    lines = []
    base = D.datetime.strptime(date + ' 09:00:20', '%Y-%m-%d %H:%M:%S')
    for w in range(4):
        start = base + D.timedelta(minutes=15 * w)
        reset = (start + D.timedelta(minutes=15)).strftime('%H:%M:%S')
        rem = 49
        for i in range(10):
            t = (start + D.timedelta(seconds=80 * i)).strftime('%H:%M:%S')
            st = '429' if (w == 0 and i >= 10 - n429) else '200'
            lines.append('%s RATE SearchTimeline st=%s rem=%d/50 reset=%s phase=load n=1'
                         % (t, st, max(rem, 0), reset))
            rem -= per_req_drop
    with io.open(os.path.join(root, 'logs', 'peter2_receiver_%s.log' % ymd), 'w',
                 encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    raw = os.path.join(root, 'data', 'peter_feed', '_raw')
    os.makedirs(raw, exist_ok=True)
    with io.open(os.path.join(raw, '%s.jsonl' % date), 'w', encoding='utf-8') as f:
        for k in range(n_tweets):
            posted_kst = D.datetime.strptime(date + ' 10:00:00', '%Y-%m-%d %H:%M:%S') \
                + D.timedelta(minutes=20 * k)
            dt_utc = (posted_kst - D.timedelta(hours=9)).strftime('%Y-%m-%dT%H:%M:%S.000Z')
            seen = (posted_kst + D.timedelta(seconds=lat_sec)).strftime('%Y-%m-%dT%H:%M:%S')
            f.write(json.dumps({'src': 'live', 'dt': dt_utc, 'seen_at': seen, 'text': 'x'}) + '\n')


def _setup(tmp_path, monkeypatch, drop, lat, days=EVAL):
    root = str(tmp_path)
    monkeypatch.setattr(LR, 'ROOT', root)
    _write_day(root, '2026-10-19', 4, 240, n429=3)       # 기준선: 공유 소비
    for d in days:
        _write_day(root, d, drop, lat)
    return root


def test_window_external_own_only_is_zero():
    rates = [{'op': 'SearchTimeline', 'reset': '09:15:00', 't': '09:0%d:00' % i,
              'rem': str(49 - i), 'st': '200'} for i in range(6)]
    w = T.window_external(rates)
    assert len(w) == 1 and w[0]['external'] == 0 and w[0]['counted']


def test_window_external_shared_counts_extra():
    rates = [{'op': 'SearchTimeline', 'reset': '09:15:00', 't': '09:0%d:00' % i,
              'rem': str(49 - 3 * i), 'st': '200'} for i in range(6)]
    assert T.window_external(rates)[0]['external'] == 10     # 15 감소 − 5


def test_improved(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch, drop=1, lat=40)
    r = T.build('2026-10-26')
    assert r['final'] == 'IMPROVED'
    assert r['sole_days'] == 5 and r['pooled_n'] == 40
    assert r['baseline']['sole_pass'] is False


def test_still_shared(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch, drop=4, lat=40)
    assert T.build('2026-10-26')['final'] == 'STILL_SHARED'


def test_not_limit(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch, drop=1, lat=200)
    assert T.build('2026-10-26')['final'] == 'NOT_LIMIT'


def test_in_progress_and_weekend_skipped(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch, drop=1, lat=40, days=EVAL[:2])
    r = T.build('2026-10-24')
    assert r['final'] == 'IN_PROGRESS'
    assert [s['date'] for s in r['days']] == EVAL[:2]
    assert '2026-10-24' not in r['missing_weekdays']       # 토요일은 휴장 취급 아님
    assert '2026-10-22' in r['missing_weekdays']


def test_no_rate_is_unmeasured_not_pass(tmp_path, monkeypatch):
    monkeypatch.setattr(LR, 'ROOT', str(tmp_path))
    s = T.day_stats('2026-10-20')
    assert s['measured'] is False
    assert s['sole_pass'] is None and s['n429_pass'] is None


def test_preregistered_constants_fixed():
    assert (T.START_DATE, T.EVAL_DAYS, T.EXTERNAL_MEDIAN_MAX, T.N429_MAX,
            T.POOLED_MIN_N, T.DAYS_PASS_MIN) == ('2026-10-20', 5, 3, 1, 30, 4)
    assert LR.P90_LIMIT_SEC == 90


def test_collect_evidence_section_wired():
    p = os.path.join(ROOT, '.claude', 'skills', 'mireuk-daily-check', 'scripts',
                     'collect_evidence.py')
    spec = importlib.util.spec_from_file_location('_ce698', p)
    ce = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ce)
    out = []
    ce.peter2_sole_collect_section(ROOT, D.date(2026, 10, 20), out)
    assert out[0].startswith('### 9-e.')
    assert any('최종' in x or '미측정' in x for x in out)
    out2 = []
    ce.peter2_sole_collect_section('Z:/no/such/root', D.date(2026, 10, 20), out2)
    assert any('미측정' in x for x in out2)
