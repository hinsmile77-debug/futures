# -*- coding: utf-8 -*-
"""[MW0601 668차] 피터2 — 피터리 트윗 실시간 추종 회귀 가드.

고정하는 것
    A. 해석기 — 실측 문형(2026-08-03 ~ 10-07 `_raw`)이 정해진 사실로 읽힌다.
       특히 **진입으로 읽으면 안 되는 것**(결산·인용·보고서·계획·다른 상품)이 진입이 아니다.
    B. 상태기계 — 10-07 실제 트윗 순서를 재생하면 그의 거래줄이 손으로 쓴 `_tr.txt` 와 글자까지 같고,
       추종 의도가 진입 3 · 손절가 2 · 청산가 2 · 미러청산 1 순으로 나온다.
    C. 트래커 — PETER2 포지션은 외부 손절이 ATR·TP·손절계단·트레일링을 덮고,
       **비-PETER2 포지션에는 남은 외부 손절이 붙지 않는다**.
    D. 출처 — PETER2 는 external 로 분류된다(system 이 아니다 — 전환기준 ① 판정에서 빠진다).
    E. 배선 — main.py 가 `entry_source=PETER2` 로 진입하고, 폴링 슬롯이 예외를 가드한다.

실행
    conda run -n py37_32 python -m pytest tests/test_668_peter2.py -q
"""
import datetime
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from strategy.peter2.parse import parse_tweet          # noqa: E402
from strategy.peter2.follower import Peter2Follower    # noqa: E402


def _facts(t):
    return [(f['type'], f.get('level'), f.get('side') or f.get('kind') or f.get('ctx'))
            for f in parse_tweet(t)['facts']]


# ── A. 해석기 ──────────────────────────────────────────────────
def test_entry_breakdown_with_stop():
    assert _facts('1096 하방 돌파시 매도. 손절가 1100') == [
        ('entry', 1096.0, 'S'), ('stop', 1100.0, 'entry')]
    f = parse_tweet('1087.5 하방돌파시 매도. 손절가 1091')['facts'][0]
    assert f['level'] == 1087.5 and f['mode'] == 'brk_dn'


def test_entry_variants():
    assert _facts('1094매수 1088 손절') == [('entry', 1094.0, 'L'), ('stop', 1088.0, 'entry')]
    f = parse_tweet('1035-36에서 매수. 손절 1033')['facts'][0]
    assert (f['lo'], f['hi'], f['mode']) == (1035.0, 1036.0, 'limit')
    f = parse_tweet('1045나 46에서 그냥 매수')['facts'][0]
    assert (f['lo'], f['hi']) == (1045.0, 1046.0)
    assert parse_tweet('1050까지 내려오면 매수. 손절가 1047')['facts'][0]['mode'] == 'limit'
    assert parse_tweet('1105 돌파시 매수. 손절가 1100')['facts'][0]['mode'] == 'brk_up'


def test_fill_and_management():
    assert _facts('1096 매도 체결.') == [('fill', 1096.0, 'S')]
    assert _facts('1010체결됨. 1030 청산가.') == [('fill', 1010.0, None), ('target', 1030.0, None)]
    assert _facts('손절가 1111로 변경.') == [('stop', 1111.0, 'set')]
    assert _facts('손절가 다시 변경 1113') == [('stop', 1113.0, 'set')]
    assert _facts('1024 청산가로 변경.') == [('target', 1024.0, None)]
    assert _facts('1056 청산으로 변경.') == [('target', 1056.0, None)]
    assert _facts('청산은 1097에서. 오늘은 짧게') == [('target', 1097.0, None)]
    assert ('target', 1082.0, None) in _facts('두탕째니까 그냥 1082에 청산하자.')
    assert _facts('만약 995 이탈하면 청산해~~~') == [('tighten', 995.0, None)]
    assert _facts('만약 여기서 밀리면 985에 수익실현') == [('tighten', 985.0, None)]


def test_exit_reports():
    assert _facts('1100 손절.') == [('exit', 1100.0, 'stop')]
    assert _facts('1083 청산체결.\n\n6P 수익 - 5P 손실.') == [('exit', 1083.0, 'take')]
    assert _facts('1081 청산완료. 오늘 한방에 40P 수익') == [('exit', 1081.0, 'take')]
    # 진입 앞 문장의 손절 보고는 청산으로 남는다(09-14 실측)
    assert _facts('1047 손절.\n\n1049 돌파시 매수.  손절 1046') == [
        ('exit', 1047.0, 'stop'), ('entry', 1049.0, 'L'), ('stop', 1046.0, 'entry')]


def test_not_orders():
    """진입으로 읽으면 실제 주문이 나간다 — 이것들은 진입이 아니어야 한다."""
    no_entry = [
        '972 또는 974 매도. 손절가 980 = 6-8P 손실',                       # 결산
        "벌레같은 놈. 내용이 이거임. '1110 갈거니까 매도할거면 거기서'",       # 인용
        '[피터리 - 8월 선물매매 내역] 8/4 +46P 1077 손절가 1100',           # 보고서
        '1130 밑으로 떨어지면 확인하고 매수 들어갈 예정이니 대기',              # 계획
        '1110은 간다고 생각하고 거기서 꺽이는거 보고 매도 진입',               # 생각
        '매도 안되었으면 1087에서 매도 가능.',                               # 가능
        '코스닥150 1550 매도 사인',                                         # 다른 상품
        '965 매수분 995 목표가. 여기서 정리.',                               # 보유분
        '가령 어제 오후장에 974 매수를 외친건.',                              # 회고
    ]
    for t in no_entry:
        assert not any(f['type'] == 'entry' for f in parse_tweet(t)['facts']), t
    assert parse_tweet('코스닥 150 인버스 매수')['ignore'] == 'other_product'
    assert ('cancel', None, None) in _facts('1062 손절. 매수하면 안됨.')


# ── B. 상태기계 ────────────────────────────────────────────────
# 2026-10-07 실제 트윗(UTC). 손으로 쓴 _tr.txt:
#   09:05 S 1096 / 09:16 X 1100 손절
#   09:35 S 1106 / 10:24 X 1096 수익
#   14:30 S 1087.5 / 15:07 X 1082 수익
T1007 = [
    ('2026-10-07T00:05:08', '1096 하방 돌파시 매도. 손절가 1100'),
    ('2026-10-07T00:05:29', '1096 매도 체결.'),
    ('2026-10-07T00:16:08', '1100 손절.'),
    ('2026-10-07T00:35:14', '1106 하방돌파시 매도로 수정. 손절가 1109'),
    ('2026-10-07T00:35:26', '1106 매도체결.'),
    ('2026-10-07T00:38:01', '손절가 1111로 변경.'),
    ('2026-10-07T00:46:37', '오늘 코스피 고점 거의 다 왔습니다.\n\n손절가 다시 변경 1113'),
    ('2026-10-07T01:00:00', '청산가 1096. 오늘 아래 막아놔서 빠져도 많이 안 빠집니다.'),
    ('2026-10-07T01:24:00', '1096 청산체결.\n\n10p 수익 + 4p 손실 = 6p 수익.'),
    ('2026-10-07T05:30:10', '1087.5 하방돌파시 매도. 손절가 1091'),
    ('2026-10-07T05:30:30', '1087.5 매도체결.'),
    ('2026-10-07T05:31:00', '매도 안되었으면 1087에서 매도 가능.'),
    ('2026-10-07T05:32:00', '늦어도 1087에 모두 매도 체결. 손절가 1091'),
    ('2026-10-07T06:05:00', '두탕째니까 그냥 1082에 청산하자. \n\n청산가 1082로 변경'),
    ('2026-10-07T06:07:00', '1082 청산체결!\n\n5p추가수익.'),
]


def _tw(i, dt, text):
    return {'id': 'T%02d' % i, 'dt': dt + '.000Z', 'text': text}


def test_peter_tr_matches_handwritten():
    fw = Peter2Follower('2026-10-07', None, 'test', False)
    eng = {'status': 'FLAT', 'source': None, 'pending': False, 'price': None}
    for i, (dt, tx) in enumerate(T1007):
        fw.ingest(_tw(i, dt, tx), eng, datetime.datetime(2026, 10, 7, 16, 0), replay=True)
    assert fw.peter_tr_text().splitlines() == [
        '09:05 S 1096 / 09:16 X 1100 손절',
        '09:35 S 1106 / 10:24 X 1096 수익',
        '14:30 S 1087.5 / 15:07 X 1082 수익',
    ]


def test_follow_intents_sequence():
    """가격을 지시가 근처로 두고 순서대로 넣으면 의도열이 그의 행동을 따라간다."""
    off = -5.5
    fw = Peter2Follower('2026-10-07', off, 'test', True)
    pos = {'status': 'FLAT', 'source': None}
    seq = []

    def eng(px):
        e = {'status': pos['status'], 'source': pos['source'], 'pending': False, 'price': px,
             'stop': pos.get('stop'), 'target': pos.get('target')}
        return e

    def run(intents):
        for it in intents:
            seq.append(it['type'])
            if it['type'] == 'ENTER':
                pos.update(status=it['side'], source='PETER2', stop=it['stop'], target=it['target'])
                fw.mark_entered()
            elif it['type'] == 'SET_STOP':
                pos['stop'] = it['stop']
            elif it['type'] == 'SET_TARGET':
                pos['target'] = it['target']
            elif it['type'] == 'EXIT':
                pos.update(status='FLAT', source=None, stop=None, target=None)

    for i, (dt, tx) in enumerate(T1007):
        t = datetime.datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S') + datetime.timedelta(hours=9, seconds=20)
        lv = re.findall(r'\d{4}(?:\.\d)?', tx)
        px = (float(lv[0]) + off) if lv else 1090.0
        run(fw.ingest(_tw(i, dt, tx), eng(px), t))
        run(fw.on_price(eng(px - 0.1 if pos['status'] == 'FLAT' else px), t))
    assert seq.count('ENTER') == 3, seq
    assert seq[:2] == ['ENTER', 'EXIT']                   # 1096 매도 → 1100 손절 미러
    assert seq.count('SET_STOP') >= 2 and seq.count('SET_TARGET') >= 2
    assert fw.consumed and fw.entries == 3


def test_engine_busy_skips():
    """미륵이가 들고 있으면 피터 신호는 건너뛴다(사용자 결정 — 권고안)."""
    fw = Peter2Follower('2026-10-07', -5.5, 'test', True)
    t = datetime.datetime(2026, 10, 7, 9, 5, 30)
    fw.ingest(_tw(0, *T1007[0]), {'status': 'FLAT', 'source': None, 'price': 1090.6}, t)
    out = fw.on_price({'status': 'LONG', 'source': 'SYSTEM_AUTO', 'pending': False,
                       'price': 1090.4}, t)
    assert out == [] and fw.armed is None
    assert any(e['kind'] == 'DISARM' and 'engine_busy' in e['why'] for e in fw.events)


def test_offset_unsafe_blocks_entry():
    fw = Peter2Follower('2026-10-12', -5.4, 'prev_day:2026-10-07', False)
    t = datetime.datetime(2026, 10, 12, 9, 5, 30)
    fw.ingest({'id': 'X', 'dt': '2026-10-12T00:05:08.000Z', 'text': '1096 하방 돌파시 매도. 손절가 1100'},
              {'status': 'FLAT', 'price': 1090.6}, t)
    assert fw.on_price({'status': 'FLAT', 'pending': False, 'price': 1090.4}, t) == []


def test_daily_stop_limit_off_by_default():
    """[2026-10-07 사용자 결정] 손절 n회 당일 정지는 해제 — 손실이 몇 번이어도 멈추지 않는다."""
    from config.settings import PETER2_DAILY_STOP_LIMIT
    assert PETER2_DAILY_STOP_LIMIT == 0
    fw = Peter2Follower('2026-10-07', -5.5, 'test', True,
                        cfg={'daily_stop_limit': PETER2_DAILY_STOP_LIMIT})
    now = datetime.datetime(2026, 10, 7, 10, 0)
    for _ in range(5):
        fw.on_peter2_closed(-4.0, now)
    assert fw.halted is None and fw.losses == 5


def test_daily_stop_limit_halts():
    fw = Peter2Follower('2026-10-07', -5.5, 'test', True, cfg={'daily_stop_limit': 2})
    now = datetime.datetime(2026, 10, 7, 10, 0)
    fw.on_peter2_closed(-4.0, now)
    assert fw.halted is None
    fw.on_peter2_closed(-3.0, now)
    assert fw.halted and fw.losses == 2


def test_expiry_rule():
    from strategy.peter2.store import last_expiry_before
    assert str(last_expiry_before('2026-10-08')) == '2026-09-10'   # 만기일 당일은 아직 같은 월물
    assert str(last_expiry_before('2026-10-12')) == '2026-10-08'


# ── C. 트래커 ──────────────────────────────────────────────────
def _tracker(tmp_path, monkeypatch):
    import strategy.position.position_tracker as T
    monkeypatch.setattr(T, '_STATE_FILE', str(tmp_path / 'ps.json'))
    return T.PositionTracker()


def test_tracker_external_levels_override(tmp_path, monkeypatch):
    p = _tracker(tmp_path, monkeypatch)
    p.entry_source = 'PETER2'
    p.set_external_levels(stop=1094.48, src='peter')
    p.open_position('SHORT', 1089.84, 1, 2.0)
    assert p.stop_price == 1094.48
    assert not p.is_tp1_hit(1000.0) and not p.is_loss_tier1_hit(1093.0)
    p.update_trailing_stop(1080.0, 2.0)
    assert p.stop_price == 1094.48
    p._recalculate_levels(3.0)
    assert p.stop_price == 1094.48
    p.set_external_levels(target=1085.0)
    assert p.is_ext_target_hit(1085.0) and not p.is_ext_target_hit(1085.5)
    r = p.close_position(1085.0, '피터2청산가')
    assert p.ext_stop is None and p.ext_target is None
    # _post_exit 는 라벨 프로퍼티 대신 이 값으로 피터2를 가른다(518차 불변식)
    assert r['pos_entry_src'] == 'PETER2'


def test_tracker_ext_never_leaks_to_system(tmp_path, monkeypatch):
    p = _tracker(tmp_path, monkeypatch)
    p.set_external_levels(stop=1000.0)          # 실패한 피터2 진입의 잔존값
    p.entry_source = 'SYSTEM_AUTO'
    p.open_position('LONG', 1090.0, 1, 2.0)
    assert p.ext_stop is None and p.stop_price != 1000.0


# ── D. 출처 ────────────────────────────────────────────────────
def test_registry_external():
    from config.constants import (classify_entry_source, entry_source_is_system,
                                  PETER2_ENTRY_SOURCE, EXTERNAL_ENTRY_SOURCES)
    assert classify_entry_source(PETER2_ENTRY_SOURCE) == 'external'
    assert not entry_source_is_system(PETER2_ENTRY_SOURCE)
    assert PETER2_ENTRY_SOURCE in EXTERNAL_ENTRY_SOURCES


# ── E. 배선 ────────────────────────────────────────────────────
def _src(rel):
    return io.open(os.path.join(ROOT, rel), encoding='utf-8').read()


def test_main_wiring():
    s = _src('main.py')
    assert 'entry_source=PETER2_ENTRY_SOURCE' in s
    assert 'self._peter2_timer.timeout.connect(self._peter2_tick)' in s
    body = s[s.index('    def _peter2_tick(self)'):s.index('    def _peter2_engine_state')]
    assert 'try:' in body and 'logger.exception' in body
    # 켈리·앙상블 학습 제외, CB 는 유지
    pe = s[s.index('    def _post_exit(self'):s.index('    def _post_exit(self') + 4000]
    assert 'if not _is_p2:' in pe and 'record_stop_loss' in pe
    # 출처 라벨은 호출부 인자로(기본값 SYSTEM_AUTO 유지)
    assert 'entry_source: str = "SYSTEM_AUTO"' in s and 'self._entry_source = entry_source' in s


def test_dashboard_wiring():
    s = _src('dashboard/main_dashboard.py')
    assert '"pt2": "피터2"' in s
    assert 'def refresh_peter_live' in s and 'def minute_chart_refresh_peter' in s
    assert 'def update_peter2_metrics' in s and 'peter2_live_row' in s
