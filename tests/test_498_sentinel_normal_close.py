# -*- coding: utf-8 -*-
"""[MW0601 498차 / F-10] 동결 센티넬이 「정상 마감 뒤 정지」와 「동결」을 구분한다.

왜 필요한가 (2026-08-26 실측 — 이상점 1-11)
--------------------------------------------
15:40:23 에 일일 마감이 **정상 종료**했는데(`data/daily_close_done_20260826.txt`),
15:45 부터 16:17 까지 **33분 연속** CRITICAL 이 나갔다. 로그 종료 시각은 5거래일
중앙값과 델타 +0분으로 정상이었다.

493차 후속5(F-Z)가 `_exit_normally` 축을 붙였지만, 그 플래그는 **프로세스가 실제로
종료할 때** 런처가 쓰는 것이라 「마감은 끝났고 프로세스는 아직 떠 있는」 구간에는
없다. 그래서 미측정 → 동결 판정 유지로 떨어졌다.

🔴 **이 파일의 가장 중요한 테스트는 여전히 「08-19형을 잡는가」다.**
2026-08-19 13:41 동결은 마감 전이라 `daily_close_done` 마커가 **없다**.
이 완화가 그 시나리오를 삼키면 안전장치를 없앤 것이 된다.

고정하는 불변식:
① 마감 마커가 정체 신호보다 **뒤** → NORMAL_CLOSE / INFO (CRITICAL 아님)
② 08-19형(마커 없음 + 플래그 없음 + 전 신호 정체) → FROZEN  ← 미탐 금지
③ 마커가 정체 신호보다 **먼저**면 동결 유지 — 존재만으로 판정하지 않는다
④ NORMAL_CLOSE 는 마커 파일·팝업 대상이 아니다 (emit 이 CRITICAL/UNKNOWN 만 쓴다)
⑤ `_exit_normally`(EXITED)와 `daily_close_done`(NORMAL_CLOSE)은 **다른 상태**다
⑥ `--once` 진단 경로도 두 축을 실제로 넘긴다 — 입력 결손이 가짜 CRITICAL 을 만들었다
"""
import datetime
import inspect
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import scripts.freeze_sentinel as fs  # noqa: E402
from scripts.freeze_sentinel import (  # noqa: E402
    judge, close_done_age, RC_FROZEN, RC_NOT_APPLICABLE,
    SIG_HEARTBEAT, SIG_TS, SIG_SYSLOG,
)

STALL = 300.0
#: 정상 마감 직후 — 3신호가 5분 넘게 멈췄다(2026-08-26 15:45:40 실측 값에 근접).
ALL_STALE = {SIG_HEARTBEAT: 307.0, SIG_TS: 307.0, SIG_SYSLOG: 302.0}


# ── ① 정상 마감 뒤 정지 ─────────────────────────────────────────────────────
def test_normal_close_is_not_critical():
    """2026-08-26 15:45:40 재현 — 마커가 15:40:23, 신호는 그 앞에서 멈췄다."""
    v = judge(ALL_STALE, stall_sec=STALL, exit_flag_age=None, close_done_age=290.0)
    assert v["state"] == "NORMAL_CLOSE"
    assert v["level"] == "INFO"
    assert v["level"] != "CRITICAL"
    assert v["rc"] == RC_NOT_APPLICABLE
    assert any("daily_close_done" in d for d in v["details"]), \
        "무엇을 근거로 강등했는지 판정문에 남아야 한다(계측 4원칙 ⑤)"


# ── ② 🔴 08-19형 동결 — 미탐 금지 ───────────────────────────────────────────
def test_2026_08_19_freeze_still_detected_without_close_marker():
    """🔴 **가장 중요한 테스트.**

    13:41 동결이라 마감이 돌지 않았다 → 마커 없음 → 여전히 CRITICAL 이어야 한다.
    """
    v = judge(ALL_STALE, stall_sec=STALL, exit_flag_age=None, close_done_age=None)
    assert v["state"] == "FROZEN", "08-19형 동결을 놓쳤다 — 완화가 과했다"
    assert v["rc"] == RC_FROZEN
    assert any("daily_close_done" in d and "미측정" in d for d in v["details"]), \
        "마커가 미측정이라는 사실이 판정문에 남아야 한다(계측 4원칙 ②)"


def test_default_arg_keeps_old_behaviour():
    """인자를 안 넘기면 종전과 같다 — 기존 호출부가 조용히 무뎌지지 않는다."""
    v = judge(ALL_STALE, stall_sec=STALL)
    assert v["state"] == "FROZEN"


# ── ③ 마커가 신호보다 먼저인 경우 ───────────────────────────────────────────
def test_marker_older_than_stall_does_not_suppress():
    """마커 **존재만으로** 판정하지 않는다 — 마감 뒤에도 한참 돌다 얼어붙은 형."""
    v = judge(ALL_STALE, stall_sec=STALL, exit_flag_age=None, close_done_age=9000.0)
    assert v["state"] == "FROZEN", "오래된 마감 마커가 그 뒤의 동결을 가렸다"
    assert any("먼저" in d for d in v["details"])


def test_boundary_marker_exactly_as_old_as_signal():
    """경계 — 마커가 가장 오래된 정체 신호와 **같은 나이**면 동결 유지(보수적)."""
    v = judge(ALL_STALE, stall_sec=STALL, close_done_age=302.0)
    assert v["state"] == "FROZEN"


# ── ⑤ 상태가 서로 구분된다 ──────────────────────────────────────────────────
def test_four_states_are_distinct():
    exited = judge(ALL_STALE, stall_sec=STALL, exit_flag_age=290.0)
    closed = judge(ALL_STALE, stall_sec=STALL, close_done_age=290.0)
    frozen = judge(ALL_STALE, stall_sec=STALL)
    watching = judge({SIG_HEARTBEAT: 1.0, SIG_TS: 1.0, SIG_SYSLOG: 1.0}, stall_sec=STALL)
    states = {exited["state"], closed["state"], frozen["state"], watching["state"]}
    assert states == {"EXITED", "NORMAL_CLOSE", "FROZEN", "WATCHING"}
    assert len({exited["level"], closed["level"], frozen["level"]}) == 3, \
        "세 상태가 같은 level 문자열을 쓰면 구분이 안 된다"


def test_exit_flag_wins_over_close_marker():
    """둘 다 있으면 `_exit_normally`(프로세스 종료 확인)가 더 강한 증거다."""
    v = judge(ALL_STALE, stall_sec=STALL, exit_flag_age=280.0, close_done_age=290.0)
    assert v["state"] == "EXITED"


# ── ④ 마커 파일·팝업 대상이 아니다 ──────────────────────────────────────────
def test_normal_close_writes_no_alert_marker(tmp_path):
    v = judge(ALL_STALE, stall_sec=STALL, close_done_age=290.0)
    day = datetime.date(2026, 8, 26)
    fs.emit(str(tmp_path), day, v, popup=False, manual=False)
    alert = tmp_path / "data" / "freeze_sentinel_alert_20260826.txt"
    assert not alert.exists(), \
        "정상 마감을 경보 마커로 남기면 다음날 장전 인벤토리가 상시 적신호가 된다"
    log = tmp_path / "logs" / "freeze_sentinel_20260826.log"
    assert log.exists(), "강등해도 **기록은 남긴다** — 조용해지는 것과는 다르다"


# ── close_done_age 자체 ─────────────────────────────────────────────────────
def test_close_done_age_none_when_absent(tmp_path):
    assert close_done_age(str(tmp_path), datetime.datetime.now(),
                          datetime.date(2026, 8, 26)) is None


def test_close_done_age_measures_marker(tmp_path):
    d = tmp_path / "data"
    d.mkdir()
    (d / "daily_close_done_20260826.txt").write_text("done\n", encoding="utf-8")
    age = close_done_age(str(tmp_path), datetime.datetime.now(),
                         datetime.date(2026, 8, 26))
    assert age is not None and 0.0 <= age < 60.0


def test_close_done_age_is_date_scoped(tmp_path):
    """어제 마커가 오늘 판정에 끼어들지 않는다(파일명 날짜 스코프)."""
    d = tmp_path / "data"
    d.mkdir()
    (d / "daily_close_done_20260825.txt").write_text("done\n", encoding="utf-8")
    assert close_done_age(str(tmp_path), datetime.datetime.now(),
                          datetime.date(2026, 8, 26)) is None


# ── ⑥ --once 경로 입력 결손 회귀 ────────────────────────────────────────────
def test_once_path_passes_both_axes():
    """`--once` 진단이 두 축을 **실제로** 넘기는지 소스로 고정한다.

    2026-08-26 16:17 수동 실행이 `_exit_normally 미측정`을 찍은 것은 판정 결함이
    아니라 **입력 결손**이었다 — 그 경로가 인자를 아예 안 넘겼다.
    """
    src = inspect.getsource(fs.main)
    once = src.split("if args.once or args.at_time:")[1].split("emit(")[0]
    assert "exit_flag_age=" in once
    assert "close_done_age=" in once


def test_kill_toggle_untouched():
    """🔴 하드 종료 승격은 주간회의 안건이다 — 이 fix 는 그것을 건드리지 않는다."""
    src = inspect.getsource(fs)
    assert "FREEZE_SENTINEL_KILL_ENABLED" in src
    assert "하드 종료는" in src and "미구현" in src
