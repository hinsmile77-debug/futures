# -*- coding: utf-8 -*-
"""[MW0601 2026-10-16] 장후 정리(사다리 + CREON API 세션) — scripts/eod_session_cleanup.ps1.

밤을 넘긴 API 세션이 좀비가 되어 다음 날 08:35 에 DibServer·coStarter 크래시를 일으켰다
(09-24 ~ 10-16 6회). 연결이 살아 있을 때의 PlusDisconnect() 만 CpStart 를 내린다.
2026-10-16 16:39 실측: RESULT=DISCONNECTED cpstart [20564] -> [] · 사다리 서버·콘솔 종료.
"""
import io
import os
import re

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PS1 = os.path.join(_ROOT, "scripts", "eod_session_cleanup.ps1")
_PY = os.path.join(_ROOT, "scripts", "broker_session_cleanup.py")


def _ps1():
    return io.open(_PS1, "rb").read()


def test_ps1_is_pure_ascii():
    """PowerShell 5.1 은 BOM 없는 파일을 ANSI 로 읽는다 — 사다리 스크립트와 같은 규약."""
    assert all(b < 128 for b in _ps1())


def test_runs_after_last_com_task():
    src = _ps1().decode("ascii")
    assert re.search(r"\[string\]\$At = '16:30'", src)
    # 실측 가장 늦은 COM 작업(OptionFlowBackfill 16:20 → 16:23:09) 뒤여야 한다
    assert "backfill_option_flow" in src and "collect_regular_futures" in src


def test_never_touches_a_running_mireuk_session():
    src = _ps1().decode("ascii").split("#>", 1)[1]   # 머리 주석 제외 — 코드 순서만 본다
    i_gate = src.index("main\\.py")
    assert i_gate < src.index("stop ladder server") < src.index("broker_session_cleanup.py")
    assert "-> skip" in src


def test_does_not_touch_hts_and_runs_elevated():
    src = _ps1().decode("ascii")
    assert "coMain" not in src.split("#>")[1], "HTS(coMain)는 사람 도구 — 건드리지 않는다"
    assert "-RunLevel Highest" in src
    assert "StartWhenAvailable" not in src.split("#>")[1].replace("No StartWhenAvailable", "")


def test_broker_helper_uses_plus_disconnect_and_reports_state():
    src = io.open(_PY, encoding="utf-8").read()
    assert "PlusDisconnect()" in src
    for state in ("NO_SESSION", "DISCONNECTED", "ZOMBIE_LEFT", "STILL_ALIVE", "PROBE_FAIL"):
        assert state in src
