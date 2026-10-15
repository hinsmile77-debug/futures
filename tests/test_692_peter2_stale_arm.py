# -*- coding: utf-8 -*-
"""[MW0601 2026-10-15] 피터2 — 도착 시점에 이미 만료된 지시는 대기로 열지 않는다.

실측(2026-10-15):
  · 13:12 「859 에서 오늘 손절없이 지금 매수함. / 859 매수체결.」이 X 페이지 수집 중단
    (12:16–14:03) 때문에 14:04 에 도착 → too_far 로 2회 기각.
  · 14:20 재기동 복원(replay)에서 같은 지시가 「대기」로 살아났다가 첫 가격에 EXPIRE.
    복원 때는 가격이 없어 거리 검사를 건너뛰므로, 트윗 10분 안에 재기동하면 실시간에서
    기각됐던 지시가 열릴 수 있었다.
"""
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategy.peter2.follower import Peter2Follower    # noqa: E402

TW = {'id': '2110584639144563038', 'dt': '2026-10-15T04:12:00.000Z',     # 13:12 KST
      'text': '859 에서 오늘 손절없이 지금 매수함.\n\n859 매수체결.'}


def _fw():
    return Peter2Follower('2026-10-15', -2.2, 'test', True)


def _reasons(fw):
    return [e.get('why') for e in fw.events if e.get('kind') == 'REJECT']


def test_replay_after_expiry_does_not_arm():
    fw = _fw()
    fw.ingest(TW, {'status': 'FLAT', 'source': None, 'price': None},
              datetime.datetime(2026, 10, 15, 14, 20, 26), replay=True)
    assert fw.armed is None, "만료된 지시가 재기동 복원에서 대기로 살아났다"


def test_late_live_tweet_is_rejected_as_stale():
    fw = _fw()
    fw.ingest(TW, {'status': 'FLAT', 'source': None, 'price': 866.78},
              datetime.datetime(2026, 10, 15, 14, 4, 7))
    assert fw.armed is None
    assert 'stale' in _reasons(fw) and 'too_far' not in _reasons(fw)


def test_fresh_tweet_still_arms():
    fw = _fw()
    fw.ingest(TW, {'status': 'FLAT', 'source': None, 'price': 857.5},
              datetime.datetime(2026, 10, 15, 13, 12, 30))
    assert fw.armed is not None and fw.armed['sig'] == TW['id']


def test_replay_within_window_still_restores():
    """설계 유지: 아직 유효한 대기 지시는 재기동 복원에서 되살린다."""
    fw = _fw()
    fw.ingest(TW, {'status': 'FLAT', 'source': None, 'price': None},
              datetime.datetime(2026, 10, 15, 13, 15, 0), replay=True)
    assert fw.armed is not None
