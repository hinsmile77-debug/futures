# -*- coding: utf-8 -*-
"""[MW0602 658차 · 사용자 결정 2026-10-24] 신동 V4 본전청산은 CB② 연속 손절에 세지 않는다.

지키는 불변식
  · 손절이 규칙 진입가로 올라오면(본전이동) 외부 손절 출처 = `shindong_be`, 그 위(트레일)는 `shindong_trail`
  · 청산 결과에 손절 출처 스냅샷(`pos_ext_stop_src`)이 실린다 — 리셋 전에
  · 본전청산 판정 = 출처 SHINDONG 이고 (손절 출처 shindong_be 또는 사유 「신동미러:BE」)
  · 본전청산이면 CB② 카운터를 올리지도 초기화하지도 않는다(중립) · 미륵·피터·신동 재난손절은 종전대로 센다
근거: docs/신동거래_V4/신동_사전등록_V4_20261024.md §7 · 21일 재생 10/23 CB② 10:09 정지(본전청산 3연속).
"""
import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

import main  # noqa: E402
from config.constants import PETER2_ENTRY_SOURCE, SHINDONG_ENTRY_SOURCE  # noqa: E402


def test_be_stop_detection():
    rec = {"rule_px": 1100.0}
    assert main._shindong_is_be_stop(rec, 1100.0) is True
    assert main._shindong_is_be_stop(rec, 1102.5) is False          # 트레일
    assert main._shindong_is_be_stop({}, 1100.0) is False            # 규칙가 미기록 — 보수적으로 아님


def test_be_exit_classification():
    sd = SHINDONG_ENTRY_SOURCE
    assert main._shindong_be_exit({"pos_entry_src": sd, "pos_ext_stop_src": "shindong_be", "exit_reason": "하드스톱(틱)"})
    assert main._shindong_be_exit({"pos_entry_src": sd, "pos_ext_stop_src": "shindong", "exit_reason": "신동미러:BE"})
    assert not main._shindong_be_exit({"pos_entry_src": sd, "pos_ext_stop_src": "shindong", "exit_reason": "신동미러:SL"})
    assert not main._shindong_be_exit({"pos_entry_src": sd, "pos_ext_stop_src": "shindong_trail", "exit_reason": "x"})
    # 다른 주체는 항상 아님 — 같은 문자열이 와도
    assert not main._shindong_be_exit({"pos_entry_src": PETER2_ENTRY_SOURCE, "pos_ext_stop_src": "shindong_be"})
    assert not main._shindong_be_exit({"pos_entry_src": "SYSTEM_AUTO", "exit_reason": "신동미러:BE"})


class _CB(object):
    def __init__(self):
        self.calls = []

    def record_win(self):
        self.calls.append("win")

    def record_stop_loss(self):
        self.calls.append("stop")

    def status_dict(self):
        return {"consec_stops": 2}


def _cb2_branch(result):
    """`_post_exit` 의 CB 분기만 떼어 실행한다(소스에서 추출 — 분기 구조가 바뀌면 이 테스트가 깨진다)."""
    src = inspect.getsource(main.TradingSystem._post_exit)
    assert "elif not _shindong_be_exit(result):" in src
    cb = _CB()
    pnl = result["pnl_pts"]
    if pnl > 0:
        cb.record_win()
    elif not main._shindong_be_exit(result):
        cb.record_stop_loss()
    return cb.calls


def test_post_exit_branch_order():
    src = inspect.getsource(main.TradingSystem._post_exit)
    i_win, i_be, i_stop = (src.index("self.circuit_breaker.record_win()"), src.index("elif not _shindong_be_exit(result):"),
                           src.index("self.circuit_breaker.record_stop_loss()"))
    assert i_win < i_be < i_stop
    assert "CB② 연속 손절 카운트 제외" in src[i_stop:]                 # 본전청산은 else(중립) — 로그만
    sd = SHINDONG_ENTRY_SOURCE
    assert _cb2_branch({"pnl_pts": -0.2, "pos_entry_src": sd, "pos_ext_stop_src": "shindong_be"}) == []
    assert _cb2_branch({"pnl_pts": -16.1, "pos_entry_src": sd, "pos_ext_stop_src": "shindong", "exit_reason": "신동미러:SL"}) == ["stop"]
    assert _cb2_branch({"pnl_pts": -0.2, "pos_entry_src": "SYSTEM_AUTO"}) == ["stop"]
    assert _cb2_branch({"pnl_pts": 0.3, "pos_entry_src": sd, "pos_ext_stop_src": "shindong_be"}) == ["win"]


def test_exec_step_labels_be_stop_and_tracker_snapshots_src():
    src = inspect.getsource(main.TradingSystem._shindong_exec_step)
    assert 'src="shindong_be" if _be else "shindong_trail"' in src
    tsrc = open(os.path.join(os.path.dirname(main.__file__), "strategy", "position", "position_tracker.py"),
                encoding="utf-8").read()
    assert tsrc.count('"pos_ext_stop_src": self.ext_stop_src') == 3   # 청산 결과 3곳 모두


def test_tracker_result_carries_ext_stop_src(tmp_path, monkeypatch):
    """실제 PositionTracker 로 신동 포지션을 열고 본전 손절 출처를 건 뒤 청산 — 결과에 출처가 실린다."""
    from strategy.position import position_tracker as PT
    pos = PT.PositionTracker()
    monkeypatch.setattr(pos, "_save_state", lambda *a, **k: None)
    pos.open_position("SHORT", 1100.0, 1, 30.0, grade="S")
    pos.entry_source = SHINDONG_ENTRY_SOURCE       # main 은 진입 출처를 체결 경로에서 이렇게 붙인다
    pos.set_external_levels(stop=1100.0, src="shindong_be")
    r = pos.close_position(1100.1, "하드스톱(틱)")
    assert r.get("pos_ext_stop_src") == "shindong_be"
    assert main._shindong_be_exit(r)
