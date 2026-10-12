# -*- coding: utf-8 -*-
"""[MW0602 612차 후속 / F-1008-1] 옵션체인 워커 완료시간 추이 로깅 — 로그 전용.

고정하는 것
  1. 표본 4건 미만이면 평균·배수는 None(미측정 ≠ 정상, 계측 4원칙 ②)
  2. 이동평균은 최근 8건 창
  3. 사전등록 기준값(1.5초 · x5 · 4건 · 8건)이 그대로다 — 관측을 보고 바꾸지 말 것
  4. `_execute` 의 반환값(피처·체인)은 추이 계측과 무관하다 — 판단 무변경
"""
import logging
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

ocw = pytest.importorskip("collection.options.option_chain_worker")


@pytest.fixture(autouse=True)
def _reset_hist():
    with ocw._elapsed_lock:
        del ocw._elapsed_hist[:]
    yield
    with ocw._elapsed_lock:
        del ocw._elapsed_hist[:]


def test_1_unmeasured_below_min_samples():
    for i in range(3):
        n, avg, ratio = ocw._record_elapsed(1500.0)
        assert n == i + 1
        assert avg is None and ratio is None
    assert "미측정(표본 3/4)" in ocw._elapsed_trend_text(n, avg, ratio)


def test_2_moving_average_window_is_8():
    for _ in range(8):
        ocw._record_elapsed(1500.0)
    for _ in range(8):
        n, avg, ratio = ocw._record_elapsed(16300.0)
    assert n == 8
    assert avg == pytest.approx(16300.0)
    assert ratio == pytest.approx(16300.0 / 1500.0)
    assert "x10.9" in ocw._elapsed_trend_text(n, avg, ratio)


def test_3_preregistered_constants_unchanged():
    assert ocw._ELAPSED_NORMAL_MS == 1500.0
    assert ocw._ELAPSED_WARN_RATIO == 5.0
    assert ocw._ELAPSED_MIN_SAMPLES == 4
    assert ocw._ELAPSED_WINDOW == 8


class _FakeMst(object):
    def __init__(self):
        self._code = None

    def SetInputValue(self, idx, code):
        self._code = code

    def BlockRequest(self):
        pass

    def GetDibStatus(self):
        return 0

    def GetHeaderValue(self, idx):
        return 100 if idx == ocw._HV_OI else 0.5


class _Capture(logging.Handler):
    """caplog 대신 SYSTEM 로거에 직접 붙인다 — 다른 테스트가 propagate 를 끄면
    caplog 가 못 받는다(스위트 실행 순서 의존 제거)."""

    def __init__(self):
        logging.Handler.__init__(self, level=logging.DEBUG)
        self.msgs = []

    def emit(self, record):
        self.msgs.append(record.getMessage())


@pytest.fixture
def cap():
    lg = logging.getLogger("SYSTEM")
    h = _Capture()
    old_level, old_disabled = lg.level, lg.disabled
    lg.addHandler(h)
    lg.setLevel(logging.DEBUG)
    lg.disabled = False
    yield h
    lg.removeHandler(h)
    lg.setLevel(old_level)
    lg.disabled = old_disabled


def _run_execute(monkeypatch):
    import types
    fake_client = types.ModuleType("win32com.client")
    fake_client.Dispatch = lambda name: _FakeMst()
    fake_pkg = types.ModuleType("win32com")
    fake_pkg.client = fake_client
    monkeypatch.setitem(sys.modules, "win32com", fake_pkg)
    monkeypatch.setitem(sys.modules, "win32com.client", fake_client)
    monkeypatch.setattr(ocw, "_filter_front_month", lambda chain: chain)
    chain = [
        {"code": "C1", "call_put": "콜", "strike": 1000.0, "ym": "2610"},
        {"code": "P1", "call_put": "풋", "strike": 1000.0, "ym": "2610"},
    ]
    w = ocw.OptionChainWorker.__new__(ocw.OptionChainWorker)
    w._chain_raw = chain
    w._spot = 1000.0
    w._cache_path = ""
    w._atm_window = 30.0
    w._pause_ms = 0
    w._force_reload = False
    w._book_cfg = None
    w._book_ctx = None
    monkeypatch.setattr(ocw.time, "sleep", lambda s: None)
    return w._execute()


def test_4_execute_output_independent_of_trend(monkeypatch, cap):
    feats_cold, chain_cold = _run_execute(monkeypatch)
    # 지연 이력을 미리 채워 WARNING 경로를 태운다 — 반환값은 같아야 한다.
    for _ in range(8):
        ocw._record_elapsed(20000.0)
    feats_hot, chain_hot = _run_execute(monkeypatch)
    assert feats_hot == feats_cold
    assert chain_hot == chain_cold
    msgs = cap.msgs
    assert any("완료시간 지연 추이" in m for m in msgs)
    assert any("[OptionChain][Worker] 완료" in m and "정상치 x" in m for m in msgs)


def test_5_trend_failure_does_not_break_execute(monkeypatch, cap):
    def _boom(ms):
        raise RuntimeError("boom")
    monkeypatch.setattr(ocw, "_record_elapsed", _boom)
    feats, _ = _run_execute(monkeypatch)
    assert feats.get("opt_chain_available") == 1.0
    assert any("계측실패" in m for m in cap.msgs)
