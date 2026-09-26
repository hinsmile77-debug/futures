# -*- coding: utf-8 -*-
"""[MW0601 631차] 런처 연결 대기 — F-3(자동로그인 진행 중 대기) · F-3b(연속 유지).

2026-09-26 10:21:59, 자동로그인 재시도가 기존 세션을 죽이는 사이 런처가 IsConnect=1 을
한 번 보고 main.py 를 출발시켰다.
"""
import io
import json
import os
import sys
import types

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))
import check_cybos_account as C  # noqa: E402


def _lock(path, pid, started):
    with io.open(path, "w", encoding="utf-8") as f:
        f.write(u"%s" % json.dumps({"pid": pid, "started": started}))


def test_lock_states(tmp_path):
    p = str(tmp_path / "autologin.lock")
    now = 1000000.0
    assert C.autologin_in_progress(p, now) is False                     # 없음
    _lock(p, os.getpid(), now - 5)
    assert C.autologin_in_progress(p, now) is True                      # 살아 있음
    _lock(p, os.getpid(), now - C.AUTOLOGIN_LOCK_MAX_AGE - 1)
    assert C.autologin_in_progress(p, now) is False                     # 너무 오래됨
    _lock(p, 2 ** 30, now - 5)
    assert C.autologin_in_progress(p, now) is False                     # PID 사망
    with io.open(p, "w", encoding="utf-8") as f:
        f.write(u"{broken")
    assert C.autologin_in_progress(p, now) is False                     # 깨짐


class _Clock(object):
    def __init__(self):
        self.t = 0.0

    def time(self):
        return self.t

    def sleep(self, s):
        self.t += s


def _fake_com(monkeypatch, is_connect):
    cp = types.SimpleNamespace(IsConnect=is_connect)
    client = types.SimpleNamespace(Dispatch=lambda name: cp)
    pkg = types.ModuleType("win32com")
    pkg.client = client
    monkeypatch.setitem(sys.modules, "win32com", pkg)
    monkeypatch.setitem(sys.modules, "win32com.client", client)
    return cp


@pytest.fixture
def clock(monkeypatch):
    c = _Clock()
    monkeypatch.setattr(C.time, "time", c.time)
    monkeypatch.setattr(C.time, "sleep", c.sleep)
    return c


def test_waits_while_autologin_busy(monkeypatch, clock):
    _fake_com(monkeypatch, 1)
    state = {"busy_until": 60.0}
    monkeypatch.setattr(C, "autologin_in_progress", lambda *a, **k: clock.t < state["busy_until"])
    assert C.wait_for_connect(300) == C.EXIT_OK
    assert clock.t >= 60.0 + C.STABLE_SEC, "자동로그인이 끝나기 전에 출발했다"


def test_requires_stable_connection(monkeypatch, clock):
    cp = _fake_com(monkeypatch, 1)
    monkeypatch.setattr(C, "autologin_in_progress", lambda *a, **k: False)
    # 5초 뒤 끊겼다 20초에 재연결 — 연속 유지 창이 리셋돼야 한다
    orig_sleep = clock.sleep

    def sleep(s):
        orig_sleep(s)
        cp.IsConnect = 0 if 5 <= clock.t < 20 else 1
    monkeypatch.setattr(C.time, "sleep", sleep)
    assert C.wait_for_connect(300) == C.EXIT_OK
    assert clock.t >= 20 + C.STABLE_SEC


def test_times_out_if_autologin_never_finishes(monkeypatch, clock):
    _fake_com(monkeypatch, 1)
    monkeypatch.setattr(C, "autologin_in_progress", lambda *a, **k: True)
    assert C.wait_for_connect(60) == C.EXIT_NOT_CONNECTED


def test_autologin_wraps_lock_for_module_callers():
    src = io.open(os.path.join(_ROOT, "scripts", "cybos_autologin.py"), encoding="utf-8").read()
    fn = src[src.index("def autologin():"):src.index('if __name__ == "__main__":')]
    assert "_lock_acquire()" in fn and "_lock_release()" in fn and "finally:" in fn
