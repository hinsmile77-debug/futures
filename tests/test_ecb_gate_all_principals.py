# -*- coding: utf-8 -*-
"""[MW0602 2026-10-17 / CB 조사 C1] 거래소 CB 중단·해제 후 관망을 **모든 주체**에 건다.

종전: `_ecb_observation_until` 은 미륵 진입 경로(`_final_entry_ok`)에서만 봤다. 신동·피터2 게이트는
CB 를 몰랐다 — 10/15 13:13:25 피터 가상진입이 관망 시간(~13:18) 안에 일어났다.
근거: docs/정기점검/매일점검/MW0602-20261015-청산거부113분-딥다이브.md §6.

지키는 불변식
  · CB 중단(재개 대기) 중 · 관망 중이면 차단 사유, 관망이 끝났으면 None
  · 미륵(기존) · 신동 실집행 · 피터2 실집행 · 신동 가상 · 피터2 가상 — 다섯 경로 모두 배선
  · 관망 만료 처리(배지 리셋)는 미륵 경로가 맡는다 — 공통 판정은 상태를 바꾸지 않는다
"""
import datetime
import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

import main  # noqa: E402


class _S(object):
    def __init__(self):
        # main.TradingSystem.__init__ 과 같은 초기값
        self._exchange_cb_mode = False
        self._exchange_cb_start = None
        self._ecb_observation_until = None


def test_block_reasons():
    s = _S()
    assert main._ts_exchange_cb_entry_block(s) is None

    s._exchange_cb_mode = True
    s._exchange_cb_start = datetime.datetime(2026, 10, 15, 12, 42)
    r = main._ts_exchange_cb_entry_block(s)
    assert r and "CB 중단" in r and "12:42" in r

    s._exchange_cb_mode = False
    s._ecb_observation_until = datetime.datetime.now() + datetime.timedelta(minutes=5)
    r = main._ts_exchange_cb_entry_block(s)
    assert r and "관망" in r

    s._ecb_observation_until = datetime.datetime.now() - datetime.timedelta(seconds=1)
    assert main._ts_exchange_cb_entry_block(s) is None, "관망이 끝나면 통과"
    assert s._ecb_observation_until is not None, "공통 판정은 상태를 바꾸지 않는다(만료 처리는 미륵 경로)"


def test_wired_to_all_principals():
    assert "_ts_exchange_cb_entry_block(self)" in inspect.getsource(
        main.TradingSystem._shindong_entry_block_reason), "신동 실집행"
    assert "_ts_exchange_cb_entry_block(self)" in inspect.getsource(
        main.TradingSystem._peter2_execute), "피터2 실집행"
    assert "_ts_exchange_cb_entry_block(self)" in inspect.getsource(
        main.TradingSystem._peter2_execute_virtual), "피터2 가상"
    src = inspect.getsource(main)
    assert 'why = _ts_exchange_cb_entry_block(self) + "(가상)"' in src, "신동 가상"
    assert "and _ecb_observation_ok" in src, "미륵(기존 관망 차단) 유지"
