# -*- coding: utf-8 -*-
"""[MW0601 622차] 메인 펌프 재진입 가드 회귀 테스트.

2026-09-23 13:38:05 동결 — `_run_block_request` 의 PumpWaitingMessages 안에서 Qt 타이머가
재진입해 3중첩(현물지수 → 수급 직접 BlockRequest → 롤오버) 뒤 네이티브 스핀에 갇혔다.
고정하는 것:
  1. 메인 스레드 대기 중에는 main_pump_busy() 가 True, 끝나면 False (예외 경로 포함)
  2. 중첩 진입은 계측된다(nested_enter)
  3. _probe_investor_tr 가 더 이상 메인 스레드에서 직접 BlockRequest 하지 않는다
  4. main.py 의 세 폴링 경로가 가드를 탄다 · 현물지수 타이머 위상 분리
"""
import os
import re
import threading

import collection.cybos.api_connector as ac

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class _FakeObj(object):
    def __init__(self, fail=False):
        self.calls_thread = None
        self.fail = fail
        self.inputs = []

    def SetInputValue(self, i, v):
        self.inputs.append((i, v))

    def BlockRequest(self):
        self.calls_thread = threading.current_thread()
        if self.fail:
            raise RuntimeError("boom")
        return 0

    def GetDibStatus(self):
        return 0

    def GetDibMsg1(self):
        return ""

    def GetHeaderValue(self, i):
        if i >= 3:
            raise IndexError(i)
        return "h%d" % i

    def GetDataValue(self, fi, ri):
        return "%d_%d" % (fi, ri) if ri < 2 else ""


def test_busy_only_while_main_waits(monkeypatch):
    obj = _FakeObj()
    monkeypatch.setattr(ac, "Dispatch", lambda progid: obj)
    seen = {}

    def reader(o):
        seen["busy"] = ac.main_pump_busy()
        return 1

    assert not ac.main_pump_busy()
    ret, status, msg, data = ac._run_block_request("X.Y", [(0, 1)], reader)
    assert data == 1 and seen["busy"] is True
    assert not ac.main_pump_busy()
    assert obj.calls_thread is not threading.main_thread()


def test_depth_restored_on_exception(monkeypatch):
    monkeypatch.setattr(ac, "Dispatch", lambda progid: _FakeObj(fail=True))
    try:
        ac._run_block_request("X.Y", [])
    except RuntimeError:
        pass
    assert not ac.main_pump_busy()


def test_nested_enter_counted(monkeypatch):
    monkeypatch.setattr(ac, "Dispatch", lambda progid: _FakeObj())
    before = ac.MAIN_PUMP_STATS["nested_enter"]
    monkeypatch.setattr(ac, "_MAIN_PUMP_DEPTH", 1)
    ac._run_block_request("X.Y", [])
    assert ac.MAIN_PUMP_STATS["nested_enter"] == before + 1
    assert ac._MAIN_PUMP_DEPTH == 1


def test_probe_runs_off_main_thread(monkeypatch):
    obj = _FakeObj()
    monkeypatch.setattr(ac, "Dispatch", lambda progid: obj)
    api = object.__new__(ac.CybosAPI)
    out = api._probe_investor_tr("CpSysDib.FakeProbe622", [(0, ord("1"))])
    assert out is not None
    assert obj.calls_thread is not threading.main_thread()
    assert out["headers"][0] == "h0"
    assert len(out["rows"]) == 2
    # 첫 호출(덤프) 뒤 두 번째 호출은 상시 폭(15열)으로 읽는다
    out2 = api._probe_investor_tr("CpSysDib.FakeProbe622", [(0, ord("1"))])
    assert max(out2["rows"][0].keys()) == 14


def test_probe_has_no_direct_blockrequest():
    src = open(os.path.join(ROOT, "collection", "cybos", "api_connector.py"),
               encoding="utf-8").read()
    body = src.split("def _probe_investor_tr(", 1)[1].split("\n    def ", 1)[0]
    # docstring·주석이 사고 경위를 인용하므로, 호출 형태(`= obj.BlockRequest()`)만 본다
    assert not re.search(r"=\s*obj\.BlockRequest\(\)", body)
    assert "_run_block_request(" in body


def test_main_wires_guard_and_stagger():
    src = open(os.path.join(ROOT, "main.py"), encoding="utf-8").read()
    for key in ('"investor"', '"kospi200_index"', '"rollover"'):
        assert "_defer_if_pump_busy(%s" % key in src, key
    assert re.search(r"singleShot\(30_000, lambda: self\._kospi200_index_timer\.start\(\)\)", src)
    assert "self._kospi200_index_timer.start()\n" not in src.replace(
        "lambda: self._kospi200_index_timer.start())", "")
