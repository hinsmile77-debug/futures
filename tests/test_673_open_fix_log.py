# -*- coding: utf-8 -*-
"""[MW0602 673차 후속 / F-SD-6] 사다리 08:45 시가 보정 — 성공 사례도 관측 가능한 1줄을 남긴다.

2026-10-29 장후 점검 P2-1: `candles()` 의 출처 꼬리표(「08:45 시가 차트 보정 …」)는 화면 src 문자열에만 있고,
보정이 실제 적용된 날을 확인하려면 함수를 직접 불러야 했다. → 날짜 폴더 `open_fix.log` 에 상태마다 1줄.

고정하는 것
-----------
1. 상태 3종(적용 · 차이없음 · 보정전) 각각 1줄, 같은 상태는 한 번만(프로세스·파일 양쪽 중복 방지).
2. 동작 무변경 — 봉·꼬리표는 기록 유무와 무관하게 같다. 기록 실패는 삼킨다.
3. 장후 재생(live=False) 경로는 기록하지 않는다 — 지난 날짜 폴더를 만들지 않는다.

실행: C:\\Users\\pc1\\anaconda3\\python.exe -m pytest tests/test_673_open_fix_log.py -v
"""
import os
import sqlite3
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "maekjeom_ladder"))
import ladder_data as L  # noqa: E402

DAY = "2026-10-29"
BAR = ["08:45", 905.34, 905.68, 904.18, 904.18]


def _setup(tmp_path, monkeypatch, open_price):
    con = sqlite3.connect(str(tmp_path / "premarket_levels.db"))
    con.execute("CREATE TABLE premarket_levels (date TEXT, stage TEXT, open_price REAL, open_bar_ts TEXT)")
    if open_price is not None:
        con.execute("INSERT INTO premarket_levels VALUES (?,?,?,?)", (DAY, "0850", open_price, "08:45"))
    con.commit(); con.close()
    monkeypatch.setattr(L, "DB", str(tmp_path))
    monkeypatch.setattr(L, "OPEN_FIX_LOG_DIR", str(tmp_path / "live"))
    monkeypatch.setattr(L, "_open_fix_seen", set())
    monkeypatch.setattr(L, "_candles_live", lambda d: ([list(BAR)], "raw_candles(live)"))
    return tmp_path / "live" / "20261029" / "open_fix.log"


def _lines(p):
    return p.read_text(encoding="utf-8").splitlines() if p.exists() else []


def test_applied_is_logged_once(tmp_path, monkeypatch):
    p = _setup(tmp_path, monkeypatch, 904.68)
    rows, src = L.candles(DAY, live=True)
    L.candles(DAY, live=True)
    ln = _lines(p)
    assert len(ln) == 1 and "[OpenFix]" in ln[0] and "상태=적용" in ln[0] and "905.34→904.68" in ln[0]
    assert rows[0][1] == 904.68 and "차트 보정" in src                     # 반환값은 종전과 같다


def test_no_diff_and_pending_are_logged(tmp_path, monkeypatch):
    p = _setup(tmp_path, monkeypatch, 905.34)                             # 10-29 실측처럼 차이 0
    L.candles(DAY, live=True)
    assert "상태=차이없음" in _lines(p)[0]
    (tmp_path / "b").mkdir()
    q = _setup(tmp_path / "b", monkeypatch, None)                         # 08:50 맥점 전 — 보정값 없음
    L.candles(DAY, live=True)
    assert "상태=보정전" in _lines(q)[0]


def test_state_transition_and_cross_process_dedupe(tmp_path, monkeypatch):
    p = _setup(tmp_path, monkeypatch, 904.68)
    p.parent.mkdir(parents=True)
    p.write_text("08:46:01 [OpenFix] day=2026-10-29 상태=보정전 08:45시가=905.34 · 08:45 시가 보정 전(실시간 첫 틱)\n",
                 encoding="utf-8")
    L.candles(DAY, live=True)                                             # 다른 프로세스가 남긴 「보정전」 뒤 적용 전이
    assert [("상태=보정전" in x, "상태=적용" in x) for x in _lines(p)] == [(True, False), (False, True)]
    monkeypatch.setattr(L, "_open_fix_seen", set())                       # 새 프로세스 — 파일을 보고 다시 쓰지 않는다
    L.candles(DAY, live=True)
    assert len(_lines(p)) == 2


def test_replay_path_does_not_log(tmp_path, monkeypatch):
    p = _setup(tmp_path, monkeypatch, 904.68)
    monkeypatch.setattr(L, "_candles_regular", lambda d: ([], None))      # 정규봉 없음 → 라이브 경로로 떨어져도
    L.candles(DAY, live=False)
    assert not p.parent.exists()


def test_no_0845_bar_is_not_a_state(tmp_path, monkeypatch):
    p = _setup(tmp_path, monkeypatch, 904.68)
    monkeypatch.setattr(L, "_candles_live", lambda d: ([["08:46", 1, 1, 1, 1]], "raw_candles(live)"))
    L.candles(DAY, live=True)
    assert not p.exists()


def test_log_failure_does_not_change_candles(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch, 904.68)
    blocker = tmp_path / "file_not_dir"
    blocker.write_text("x")
    monkeypatch.setattr(L, "OPEN_FIX_LOG_DIR", str(blocker))              # makedirs 실패 유도
    rows, src = L.candles(DAY, live=True)
    assert rows[0][1] == 904.68 and "차트 보정" in src
