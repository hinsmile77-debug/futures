# -*- coding: utf-8 -*-
"""[MW0601 493차 후속5 / F-Z] 동결 센티넬이 「정상 종료」와 「동결」을 구분한다.

왜 필요한가 (2026-08-25 실측)
-----------------------------
매일 정상 마감 뒤 15:45~16:30 에 **43회**의 CRITICAL 이 떴고 팝업도 한 번 떴다.
프로세스가 정상 종료해 3신호가 전부 멈춘 것을 「동결」로 읽은 것이다.

가짜 경보 자체보다 그 **누적 효과**가 위험하다 — 이런 것이 쌓이면 **진짜 얼어붙은
날에도 무시하게 된다.** 2026-08-19 에 실제로 동결이 나 15:10 강제청산이 통째로
지나갔고, 그때 포지션이 없었던 것은 설계가 막은 것이 아니라 **운**이었다.

🔴 **이 파일의 가장 중요한 테스트는 「08-19형을 여전히 잡는가」다.**
그날 프로세스는 **살아 있었고** `_exit_normally` 는 **쓰이지 않았다**.
완화가 그 시나리오를 삼키면, 이 fix는 안전장치를 없앤 것이 된다.

고정하는 불변식:
① 정상 종료(플래그가 정체 신호보다 **뒤**)  → EXITED / RC_NOT_APPLICABLE
② 08-19형(플래그 **없음** + 신호 정체)       → FROZEN / RC_FROZEN  ← 미탐 금지
③ 어제 플래그가 남은 경우(플래그가 신호보다 **오래됨**) → FROZEN  ← 존재만으로 판정 금지
④ 하나라도 신선                              → WATCHING
⑤ 전부 미측정                                → UNKNOWN (조용히 OK로 넘기지 않는다)
"""
import datetime
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.freeze_sentinel import (  # noqa: E402
    judge, exit_flag_age, RC_OK, RC_FROZEN, RC_UNKNOWN, RC_NOT_APPLICABLE,
    SIG_HEARTBEAT, SIG_TS, SIG_SYSLOG,
)

STALL = 300.0
#: 정상 마감 직후 — 3신호가 5분 넘게 멈췄다(프로세스가 없으니 당연하다).
ALL_STALE = {SIG_HEARTBEAT: 600.0, SIG_TS: 620.0, SIG_SYSLOG: 610.0}


# ── ① 정상 종료 ─────────────────────────────────────────────────────────────
def test_normal_exit_is_not_frozen():
    """플래그가 **가장 오래된 정체 신호보다 뒤**면 정상 종료다."""
    v = judge(ALL_STALE, stall_sec=STALL, exit_flag_age=580.0)
    assert v["state"] == "EXITED"
    assert v["level"] == "NOT_APPLICABLE"
    assert v["rc"] == RC_NOT_APPLICABLE
    assert "정상 종료" in v["headline"]


# ── ② 🔴 08-19형 동결 — 미탐 금지 ───────────────────────────────────────────
def test_2026_08_19_freeze_still_detected():
    """🔴 **가장 중요한 테스트.**

    2026-08-19 13:41:21 — 메인 스레드가 네이티브 스핀에 빠져 **프로세스는 살아
    있는 채로** 전부 멈췄다. 정상 종료가 아니었으므로 `_exit_normally` 는
    쓰이지 않았다(→ `exit_flag_age is None`).
    이 완화가 그 시나리오를 삼키면 안전장치가 사라진다.
    """
    v = judge(ALL_STALE, stall_sec=STALL, exit_flag_age=None)
    assert v["state"] == "FROZEN", "08-19형 동결을 놓쳤다 — 완화가 과했다"
    assert v["rc"] == RC_FROZEN
    assert any("미측정" in d for d in v["details"]), \
        "플래그가 미측정이라는 사실이 판정문에 남아야 한다(계측 4원칙 ②)"


def test_missing_flag_is_not_read_as_normal_exit():
    """미측정을 「정상 종료」로 읽지 않는다 — ②의 다른 표현."""
    v = judge(ALL_STALE, stall_sec=STALL)          # exit_flag_age 기본값 None
    assert v["state"] == "FROZEN"


# ── ③ 어제 플래그 잔재 ──────────────────────────────────────────────────────
def test_stale_flag_from_previous_session_does_not_suppress():
    """플래그 **존재만으로** 판정하지 않는다.

    런처가 읽고 지우기 전에 죽었거나, 어제 것이 남아 있을 수 있다. 그 경우
    나이가 정체 신호보다 **크다** — 그러면 동결 판정을 유지해야 한다.
    """
    v = judge(ALL_STALE, stall_sec=STALL, exit_flag_age=90000.0)   # 25시간 전
    assert v["state"] == "FROZEN", "어제 플래그가 오늘 동결을 가렸다"
    assert any("이전 세션 잔재" in d for d in v["details"])


def test_boundary_flag_exactly_as_old_as_signal():
    """경계 — 플래그가 정체 신호와 **같은 나이**면 동결 유지(보수적)."""
    v = judge(ALL_STALE, stall_sec=STALL, exit_flag_age=600.0)
    assert v["state"] == "FROZEN"


# ── ④⑤ 나머지 상태 ─────────────────────────────────────────────────────────
def test_fresh_signal_is_watching():
    v = judge({SIG_HEARTBEAT: 10.0, SIG_TS: 620.0, SIG_SYSLOG: 610.0},
              stall_sec=STALL, exit_flag_age=None)
    assert v["state"] == "WATCHING"
    assert v["rc"] == RC_OK


def test_all_unmeasured_is_unknown():
    """전부 미측정이면 조용히 OK로 넘기지 않는다."""
    v = judge({SIG_HEARTBEAT: None, SIG_TS: None, SIG_SYSLOG: None},
              stall_sec=STALL, exit_flag_age=10.0)
    assert v["state"] == "UNKNOWN"
    assert v["rc"] == RC_UNKNOWN


def test_three_states_are_distinct():
    """세 상태가 **서로 다른 문자열**이어야 한다(계측 4원칙 ②).

    종전에는 정상 종료와 동결이 같은 `CRITICAL` 이었다 — 그것이 이 결함의 본체다.
    """
    exited = judge(ALL_STALE, stall_sec=STALL, exit_flag_age=580.0)
    frozen = judge(ALL_STALE, stall_sec=STALL, exit_flag_age=None)
    watching = judge({SIG_HEARTBEAT: 1.0, SIG_TS: 1.0, SIG_SYSLOG: 1.0},
                     stall_sec=STALL)
    states = {exited["state"], frozen["state"], watching["state"]}
    assert states == {"EXITED", "FROZEN", "WATCHING"}
    assert len({exited["level"], frozen["level"]}) == 2, \
        "정상 종료와 동결이 같은 level 문자열이면 구분이 안 된다"


# ── exit_flag_age 자체 ──────────────────────────────────────────────────────
def test_exit_flag_age_returns_none_when_absent(tmp_path):
    """파일이 없으면 **None(미측정)** — 0 이나 큰 수로 위장하지 않는다."""
    assert exit_flag_age(str(tmp_path), datetime.datetime.now()) is None


def test_exit_flag_age_measures_recent_file(tmp_path):
    d = tmp_path / "data"
    d.mkdir()
    (d / "_exit_normally").write_text("daily_close\n", encoding="utf-8")
    age = exit_flag_age(str(tmp_path), datetime.datetime.now())
    assert age is not None
    assert 0.0 <= age < 60.0


def test_exit_flag_age_never_negative(tmp_path):
    """미래 mtime(시계 되돌림 등)에도 음수를 돌려주지 않는다."""
    d = tmp_path / "data"
    d.mkdir()
    f = d / "_exit_normally"
    f.write_text("x\n", encoding="utf-8")
    past = datetime.datetime.now() - datetime.timedelta(hours=1)
    age = exit_flag_age(str(tmp_path), past)
    assert age is not None and age >= 0.0
