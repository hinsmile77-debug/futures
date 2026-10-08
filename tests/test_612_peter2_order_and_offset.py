# -*- coding: utf-8 -*-
"""612차 — 피터2 수집→반영 흐름 3건 회귀 가드 (2026-10-08 장후 점검에서 나온 것들).

① **묶음이 시간 역순으로 처리됐다.** X 검색(`f=live`)은 최신글이 위라, 수집이 끊겼다
   돌아오면 follower 가 새 글 → 옛 글 순으로 상태기계를 돌린다. 실측(2026-10-08 13:26,
   16건 일괄 도착): `13:02 체결 ARM` → `13:00 지시`가 replaced_by 로 덮고 →
   `12:38 손절`이 peter_exited 로 **1시간 전 손절이 방금 지시를 죽였다.**
② **늦게 온 체결트윗의 역산 오프셋이 숫자로 찍혔다.** `price - level` 은 *지금* 가격
   기준이라 트윗이 늦으면 오프셋이 아니다. -15.52 로 보였으나 그 시각 실측은 -5.76 —
   **사용 중이던 -5.40 이 정확했다.**
③ **본문 없는 트윗을 전부 'empty' 로 뭉갰다.** 이미지뿐인 글과 진짜 빈 글이 같은 모양이면
   이미지로 온 매매 지시가 조용히 사라진다.

①은 「낡은 지시로 진입」이 아니라 「새 지시를 놓침」이다 — 대기 만료가 트윗 시각 기준
(`+10분`)이라 진입 쪽은 막혀 있다. 그래도 지연이 몇 분이면 만료가 안 걸려 역전만 남는다.
"""
import datetime
import io
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from strategy.peter2 import store as p2store          # noqa: E402
from strategy.peter2.follower import Peter2Follower   # noqa: E402

_D = '2026-10-08'


def _tw(hm_utc, text, tid, kind=None):
    """UTC 시각(HH:MM)으로 트윗 1건. KST = UTC + 9."""
    r = {'id': tid, 'dt': '%sT%s:00.000Z' % (_D, hm_utc), 'text': text}
    if kind:
        r['kind'] = kind
    return r


def _engine(price):
    return {'status': 'FLAT', 'source': None, 'pending': False,
            'price': price, 'stop': None, 'target': None}


def _mk(now_hm='13:30'):
    fw = Peter2Follower(_D, -5.4, 'prev_day:2026-10-07', True,
                        cfg={'arm_expire_min': 10, 'arm_max_dist': 8.0})
    now = datetime.datetime.strptime('%s %s' % (_D, now_hm), '%Y-%m-%d %H:%M')
    return fw, now


class TestOrdering(unittest.TestCase):

    def test_1_by_time_sorts_ascending(self):
        rows = [_tw('04:02', 'c', '3'), _tw('04:00', 'b', '2'), _tw('03:38', 'a', '1')]
        self.assertEqual(['1', '2', '3'], [r['id'] for r in p2store.by_time(rows)])

    def test_2_rows_without_dt_go_last(self):
        """순서를 모르는 줄을 맨 앞에 두면 상태기계가 그것부터 먹는다."""
        rows = [{'id': 'x'}, _tw('04:00', 'b', '2')]
        self.assertEqual(['2', 'x'], [r['id'] for r in p2store.by_time(rows)])

    def test_3_both_ingest_paths_sort(self):
        """main.py 의 재생·장중 두 경로 모두 정렬해서 먹여야 한다."""
        src = io.open(os.path.join(_ROOT, 'main.py'), encoding='utf-8').read()
        self.assertIn('peter2_store.by_time(tail.read_new())', src,
                      '재기동 복원 경로가 정렬하지 않는다')
        self.assertIn('peter2_store.by_time(self._peter2_tail.read_new())', src,
                      '장중 수집 경로가 정렬하지 않는다')
        self.assertNotIn('new_rows = self._peter2_tail.read_new()', src,
                         '정렬하지 않는 옛 경로가 남아 있다')

    def test_4_stale_exit_no_longer_kills_fresh_entry(self):
        """2026-10-08 실측 시퀀스. 시간순으로 먹이면 13:00 지시가 살아남아야 한다."""
        batch = [_tw('04:02', '1056 매수체결', 'T1302'),          # 13:02 KST
                 _tw('04:00', '1056 상방돌파시 매수. 손절 1052', 'T1300'),
                 _tw('03:38', '1060 손절', 'T1238')]              # 12:38 KST — 가장 낡음
        fw, now = _mk()
        for tw in p2store.by_time(batch):
            fw.ingest(tw, _engine(1051.0), now)
        kinds = [e['kind'] for e in fw.events]
        self.assertIn('ARM', kinds, '지시가 한 번도 대기에 오르지 않았다')
        self.assertNotIn('DISARM', kinds,
                         '낡은 손절이 새 지시를 죽였다 — 역순 처리가 되살아났다')

    def test_5_reverse_order_reproduces_the_bug(self):
        """가드가 헛돌지 않는지 — 역순으로 먹이면 그때 그 증상이 재현돼야 한다."""
        batch = [_tw('04:02', '1056 매수체결', 'T1302'),
                 _tw('04:00', '1056 상방돌파시 매수. 손절 1052', 'T1300'),
                 _tw('03:38', '1060 손절', 'T1238')]
        fw, now = _mk()
        for tw in batch:                      # 정렬하지 않고 수신 순서 그대로
            fw.ingest(tw, _engine(1051.0), now)
        whys = [e.get('why') for e in fw.events if e['kind'] == 'DISARM']
        self.assertIn('peter_exited', whys,
                      '역순인데도 증상이 안 나온다 — 이 테스트가 무의미해졌다')


class TestFillOffsetFreshness(unittest.TestCase):

    def test_6_fresh_fill_records_a_number(self):
        fw, now = _mk(now_hm='13:03')
        fw.ingest(_tw('04:02', '1056 매수체결', 'T1302'), _engine(1050.6), now)
        ev = [e for e in fw.events if e['kind'] == 'FILL_OFFSET']
        self.assertEqual(1, len(ev))
        self.assertAlmostEqual(-5.4, ev[0]['implied'], places=2)
        self.assertEqual(-5.4, fw.last_fill_offset)

    def test_7_stale_fill_records_no_number(self):
        """4시간 늦은 체결트윗 — 숫자를 적으면 사람이 오프셋이 틀렸다고 읽는다."""
        fw, now = _mk(now_hm='13:27')      # 트윗 09:26 KST -> 4시간 늦음
        fw.ingest(_tw('00:26', '1072 매수체결.', 'T0926'), _engine(1054.48), now)
        ev = [e for e in fw.events if e['kind'] == 'FILL_OFFSET']
        self.assertEqual(1, len(ev), 'FILL_OFFSET 자체는 남겨야 한다(미측정도 기록이다)')
        self.assertIsNone(ev[0]['implied'], '늦은 트윗에 역산 숫자가 적혔다')
        self.assertGreater(ev[0]['age_sec'], 3600, '지연을 기록하지 않는다')
        self.assertIsNone(fw.last_fill_offset, '쓰레기 값으로 직전 오프셋을 덮어썼다')

    def test_8_prose_does_not_print_a_bogus_number(self):
        line = p2store.event_md({'kind': 'FILL_OFFSET', 'hm': '09:26',
                                 'implied': None, 'used': -5.4, 'age_sec': 14460})
        self.assertIsNotNone(line)
        self.assertIn('역산 못 함', line)
        self.assertIn('241분', line)
        self.assertNotIn('-15', line)


class TestMediaOnly(unittest.TestCase):

    def test_9_media_only_is_not_empty(self):
        fw, now = _mk()
        fw.ingest(_tw('04:54', '', 'M1', kind='media_only'), _engine(1051.0), now)
        ev = [e for e in fw.events if e['kind'] == 'IGNORE']
        self.assertEqual(1, len(ev))
        self.assertEqual('media_only', ev[0]['why'],
                         '이미지 전용 트윗이 「빈 글」로 묻힌다')

    def test_10_truly_empty_stays_empty(self):
        fw, now = _mk()
        fw.ingest(_tw('04:54', '', 'E1'), _engine(1051.0), now)
        ev = [e for e in fw.events if e['kind'] == 'IGNORE']
        self.assertEqual('empty', ev[0]['why'])

    def test_11_kind_survives_the_whole_chain(self):
        """수집기 -> 수신기 -> _raw jsonl 까지 kind 가 살아 있어야 한다."""
        ct = io.open(os.path.join(_ROOT, 'tools', 'peter2_live', 'extension', 'content.js'),
                     encoding='utf-8').read()
        self.assertIn('media_only', ct, '수집기가 이미지 전용을 판별하지 않는다')
        self.assertIn('kind: kind', ct, '수집기가 kind 를 실어 보내지 않는다')
        rc = io.open(os.path.join(_ROOT, 'tools', 'peter2_live', 'receiver.py'),
                     encoding='utf-8').read()
        self.assertIn("'kind'", rc, '수신기가 kind 를 버린다')
        pc = io.open(os.path.join(_ROOT, 'tools', 'peter_capture.py'), encoding='utf-8').read()
        self.assertIn("rec['kind']", pc, '적재 단계에서 kind 가 사라진다')


if __name__ == '__main__':
    unittest.main()
