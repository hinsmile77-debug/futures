# -*- coding: utf-8 -*-
"""[MW0601 624차] 동결 감시자 강제 종료를 「무흔적 크래시」로 읽지 않는다.

2026-09-23 장후 리포트 이상점 1-9·1-10 은 PID 11272(12:37:22 기동)를
「`[CLEAN EXIT]` 조차 없는 완전 무흔적 크래시」로 올렸다. 실제로는
`utils/freeze_watchdog.py` 가 13:41:38 동결을 판정해 `os._exit(43)` 으로 스스로
끝낸 것이었고, 그 판정 블록이 `logs/crash_fault.log` 에 그대로 있었다.
`os._exit` 는 atexit 를 건너뛰므로 `[CLEAN EXIT]` 가 없는 것이 **설계**다.

이 테스트가 거는 것:
  · 감시자 블록이 직전 `[START]` PID 에 귀속되는가 (블록 안에 PID 가 없다)
  · 그 PID 판정이 「하드킬/무흔적」이 아니라 「동결 감시자 강제 종료」인가
  · 감시자 블록이 **없는** 무기록 종료는 여전히 「하드킬/무흔적」으로 남는가
    (새 분류가 진짜 미상 종료를 삼키면 안 된다 — PID 22160 이 그 경우다)
  · 다른 날의 감시자 블록이 오늘 PID 에 새지 않는가
"""

from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.wer_crash import (  # noqa: E402
    crash_fault_events,
    launcher_processes,
    reconcile,
    wer_app_faults,
)

# 2026-09-23 실측 형태(줄여서). 11272 = 감시자 종료, 22160 = 기록 없는 종료, 5964 = 정상.
_CRASH_FAULT = (
    "[START] 2026-09-22T09:00:00  PID=11111  Python 3.7.13 32bit  RSS=164MB\n"
    "\n================================================================\n"
    "[FreezeWatchdog] CRITICAL 메인 이벤트 루프 동결 판정 — 하드 종료\n"
    "  시각      : 2026-09-22T09:10:00\n"
    "  조치      : os._exit(43)\n"
    "================================================================\n"
    "[START] 2026-09-23T12:37:22  PID=11272  Python 3.7.13 32bit  RSS=164MB\n"
    "  File \"C:\\futures\\main.py\", line 20643 in <module>\n"
    "[TS] 2026-09-23T13:41:38 beat_age=212s watching=True strikes=1\n"
    "\n================================================================\n"
    "[FreezeWatchdog] CRITICAL 메인 이벤트 루프 동결 판정 — 하드 종료\n"
    "  시각      : 2026-09-23T13:41:38\n"
    "  하트비트  : 212s 경과 (임계 180s × 2회 연속)\n"
    "  조치      : os._exit(43) — 런처 RESTART_LOOP가 재기동\n"
    "================================================================\n"
    "\n================================================================\n"
    "[START] 2026-09-23T13:41:58  PID=22160  Python 3.7.13 32bit  RSS=164MB\n"
    "[TS] 2026-09-23T13:51:44 beat_age=1s watching=True strikes=0\n"
    "\n================================================================\n"
    "[START] 2026-09-23T13:52:16  PID=5964  Python 3.7.13 32bit  RSS=164MB\n"
    "[CLEAN EXIT] 2026-09-23T14:18:55  PID=5964\n"
)


def _launcher_line(t, pid):
    return ("2026-09-23 %s [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\\crash_fault.log"
            " PID=%d | 행감지=30s all_threads=True\n" % (t, pid))


@pytest.fixture
def fake_root(tmp_path):
    d = tmp_path / "logs" / "Mireuk_batch"
    d.mkdir(parents=True)
    (d / "launcher_20260923_084001_1592.log").write_text(
        _launcher_line("12:37:25", 11272)
        + _launcher_line("13:42:01", 22160)
        + _launcher_line("13:52:19", 5964),
        encoding="utf-8")
    (tmp_path / "logs" / "crash_fault.log").write_text(_CRASH_FAULT, encoding="utf-8")
    return str(tmp_path)


def test_watchdog_block_attributed_to_preceding_start(fake_root):
    r = crash_fault_events(fake_root, "2026-09-23")
    assert r["by_pid"][11272]["watchdog_exit"] == "13:41:38"
    assert r["by_pid"][11272]["clean_exit"] is None
    assert r["by_pid"][22160]["watchdog_exit"] is None
    assert r["by_pid"][5964]["watchdog_exit"] is None


def test_other_day_watchdog_does_not_leak(fake_root):
    r = crash_fault_events(fake_root, "2026-09-23")
    assert 11111 not in r["by_pid"]
    r22 = crash_fault_events(fake_root, "2026-09-22")
    assert r22["by_pid"][11111]["watchdog_exit"] == "09:10:00"


def test_watchdog_exit_is_not_called_traceless(fake_root):
    lau = launcher_processes(fake_root, "20260923")
    fau = crash_fault_events(fake_root, "2026-09-23")
    wer = wer_app_faults("2026-09-23", _runner=lambda d: "###OK###\n")
    rows = dict((r["pid"], r) for r in reconcile(lau, wer, fau)["rows"])

    assert "동결 감시자 강제 종료" in rows[11272]["verdict"]
    assert "무흔적" not in rows[11272]["verdict"]
    assert rows[11272]["watchdog_exit"] == "13:41:38"

    # 🔴 감시자 블록이 없는 무기록 종료는 여전히 미상으로 남아야 한다.
    assert "하드킬/무흔적" in rows[22160]["verdict"]
    assert "정상 종료 기록을 남김" in rows[5964]["verdict"]


def test_watchdog_verdict_survives_unmeasured_wer(fake_root):
    """감시자 블록은 프로세스 자신의 기록이라 WER 과 독립이다. 단 미측정은 밝힌다."""
    lau = launcher_processes(fake_root, "20260923")
    fau = crash_fault_events(fake_root, "2026-09-23")
    wer = wer_app_faults("2026-09-23", _runner=lambda d: "")
    rows = dict((r["pid"], r) for r in reconcile(lau, wer, fau)["rows"])
    assert "동결 감시자 강제 종료" in rows[11272]["verdict"]
    assert "WER 미측정" in rows[11272]["verdict"]
    # 나머지는 종전대로 판정불가.
    assert "판정불가" in rows[22160]["verdict"]


def test_malformed_watchdog_block_is_not_guessed(tmp_path):
    """시각 줄이 없으면 추측으로 채우지 않는다 — 다음 행 시각을 감시자 시각으로 오인 금지."""
    (tmp_path / "logs").mkdir()
    (tmp_path / "logs" / "crash_fault.log").write_text(
        "[START] 2026-09-23T12:00:00  PID=1  Python\n"
        "[FreezeWatchdog] CRITICAL 동결\n"
        "  (형식 변경)\n  (형식 변경)\n  (형식 변경)\n  (형식 변경)\n"
        "[TS] 2026-09-23T12:30:00 beat_age=0s\n",
        encoding="utf-8")
    r = crash_fault_events(str(tmp_path), "2026-09-23")
    assert r["by_pid"][1]["watchdog_exit"] is None


def test_collector_renders_watchdog_column():
    src = open(os.path.join(ROOT, ".claude", "skills", "mireuk-daily-check",
                            "scripts", "collect_evidence.py"), encoding="utf-8").read()
    assert "감시자 종료" in src and 'r.get("watchdog_exit")' in src
