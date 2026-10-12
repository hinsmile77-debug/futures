# -*- coding: utf-8 -*-
"""619차 F-3 — 옵션체인 워커 정체 복구(버리고 새로 띄우기) 회귀 가드.

2026-10-07·10-08·10-12 세 번 모두 워커가 COM 호출 안에서 예외 없이 멈췄고
`isRunning()` 스킵만 반복돼 재시작 외 탈출 경로가 없었다.
"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

import main  # noqa: E402
import config.settings as S  # noqa: E402

_abandon = main.TradingSystem._abandon_stalled_option_chain_worker


class _Sig(object):
    def __init__(self):
        self.connected = True

    def disconnect(self):
        if not self.connected:
            raise TypeError("not connected")
        self.connected = False


class _Worker(object):
    def __init__(self):
        self.result_ready = _Sig()
        self.book_ready = _Sig()
        self.terminated = False

    def terminate(self):            # 호출되면 안 된다
        self.terminated = True


class _Snap(object):
    def __init__(self, stall):
        self.stall = stall

    def seconds_since_refresh(self):
        return self.stall


class _Self(object):
    def __init__(self, stall):
        self.option_chain_snap = _Snap(stall)
        self._option_chain_abandoned = []
        self._option_chain_abandon_cap_logged = False
        self._option_chain_worker = object()


def test_short_stall_keeps_skipping():
    s, w = _Self(S.OPTION_CHAIN_WORKER_STALL_SEC - 1), _Worker()
    assert _abandon(s, w) is False
    assert w.result_ready.connected and not s._option_chain_abandoned


def test_long_stall_abandons_without_terminate():
    s, w = _Self(S.OPTION_CHAIN_WORKER_STALL_SEC + 60), _Worker()
    assert _abandon(s, w) is True
    assert s._option_chain_worker is None
    assert s._option_chain_abandoned == [w]           # 참조 보관 — GC 로 프로세스가 죽지 않게
    assert not w.result_ready.connected and not w.book_ready.connected
    assert not w.terminated


def test_cap_stops_abandoning():
    s = _Self(10_000)
    for _ in range(S.OPTION_CHAIN_WORKER_ABANDON_MAX):
        assert _abandon(s, _Worker()) is True
    w = _Worker()
    assert _abandon(s, w) is False
    assert s._option_chain_abandon_cap_logged
    assert w.result_ready.connected
    assert len(s._option_chain_abandoned) == S.OPTION_CHAIN_WORKER_ABANDON_MAX


def test_never_started_is_not_stall():
    assert _abandon(_Self(float("inf")), _Worker()) is False


def test_exception_falls_back_to_skip():
    s = _Self(10_000)
    s.option_chain_snap = None                          # 판정 중 예외
    assert _abandon(s, _Worker()) is False


def test_threshold_leaves_room_for_normal_run():
    # 정상 상한(먼스리 ~16s + 만기북 예산) 보다 크고 폴링 주기(300s) 보다 작아야 한다
    assert S.OPTION_BOOK_BUDGET_SEC + 20 < S.OPTION_CHAIN_WORKER_STALL_SEC < 300


def test_no_terminate_in_poll_path():
    src = open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()
    i = src.find("def _poll_option_chain(")
    j = src.find("def _on_option_chain_done(")
    assert i != -1 and j > i
    assert ".terminate()" not in src[i:j]
    assert "_abandon_stalled_option_chain_worker(_prev)" in src[i:j]
