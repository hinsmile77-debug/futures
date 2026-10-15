# -*- coding: utf-8 -*-
"""[MW0601 2026-10-15] 장중 재기동 시 동결 센티넬이 「직전 세션의 정상 종료」를 보고
새 세션 감시를 포기하지 않는다.

실측: 13:43:57·13:58:13 재기동 두 번 모두 센티넬이 무장 0초 만에
「정상 종료 확인 — 감시 종료」를 남기고 빠졌다. 센티넬은 새 main.py 가 신호를 쓰기
**전에** 뜨므로, 그 순간 3신호는 직전 세션 것(전부 정체)이고 직전 세션의 종료 마커가
그보다 뒤라 judge() 가 EXITED 를 낸다. 판정은 옳지만 그대로 return 하면 새 세션은
하루 종일 무감시가 된다(08:48 첫 기동분만 살아 있었다).

규칙: 정상 종료 근거가 **전부 센티넬 무장 이전**이면 직전 세션의 것 → 감시 계속.
무장 이후에 찍힌 근거가 하나라도 있으면 이번 세션의 정상 종료 → 종전대로 감시 종료.
"""
import datetime
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import scripts.freeze_sentinel as fs  # noqa: E402


def _touch(path, when):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write("x")
    ts = time.mktime(when.timetuple())
    os.utime(path, (ts, ts))


def _marker(root, day):
    return os.path.join(root, "data", "shutdown_normal_%s.txt" % day.strftime("%Y%m%d"))


def test_marker_before_arming_is_prior_session(tmp_path):
    root = str(tmp_path)
    now = datetime.datetime(2026, 10, 15, 13, 58, 30)
    armed = now - datetime.timedelta(seconds=17)                      # 13:58:13 무장
    _touch(_marker(root, now.date()), now - datetime.timedelta(minutes=7))   # 13:51 user_close
    assert fs._exit_marker_predates(root, now, armed) is True


def test_marker_after_arming_is_this_session(tmp_path):
    root = str(tmp_path)
    armed = datetime.datetime(2026, 10, 15, 8, 48, 22)
    now = datetime.datetime(2026, 10, 15, 15, 46, 0)
    _touch(_marker(root, now.date()), datetime.datetime(2026, 10, 15, 15, 40, 26))
    assert fs._exit_marker_predates(root, now, armed) is False


def test_any_post_arming_evidence_wins(tmp_path):
    """어제 `_exit_normally` 가 남아 있어도 오늘 무장 뒤 종료 마커가 있으면 이번 세션 종료다."""
    root = str(tmp_path)
    armed = datetime.datetime(2026, 10, 15, 13, 58, 13)
    now = datetime.datetime(2026, 10, 15, 15, 46, 0)
    _touch(os.path.join(root, "data", "_exit_normally"), datetime.datetime(2026, 10, 14, 15, 47, 0))
    _touch(_marker(root, now.date()), datetime.datetime(2026, 10, 15, 15, 40, 26))
    assert fs._exit_marker_predates(root, now, armed) is False


def test_no_evidence_keeps_legacy_behaviour(tmp_path):
    root = str(tmp_path)
    now = datetime.datetime(2026, 10, 15, 14, 0, 0)
    assert fs._exit_marker_predates(root, now, now) is False


def test_loop_consults_prior_exit_before_returning():
    import inspect
    src = inspect.getsource(fs.main)
    i_prior = src.index("_exit_marker_predates(")
    i_return = src.index("정상 종료 확인 — 감시 종료")
    assert i_prior < i_return, "직전 세션 판별이 감시 종료 return 보다 먼저 와야 한다"


def test_resident_sentinel_is_single_instance():
    """[MW0601 2026-10-15] 장중 재기동 시 직전 센티넬이 살아 있으면 새 센티넬은 물러난다."""
    import subprocess
    name = r"Global\Mireuk_FreezeSentinel_test"
    assert fs._acquire_single_instance(name) is True
    code = ("import sys; sys.path.insert(0, %r); import scripts.freeze_sentinel as f; "
            "print(f._acquire_single_instance(%r))" % (
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), name))
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True).stdout.strip()
    assert out.endswith("False")
    import inspect
    src = inspect.getsource(fs.main)
    assert src.index("_acquire_single_instance()") < src.index("log_armed(root, now.date(), window")
