# -*- coding: utf-8 -*-
"""[MW0602 570차 후속] 증거지도가 인용한 **로그 문구가 아직 살아 있는가**.

무엇을 막는 장치인가
--------------------
`.claude/skills/mireuk-daily-check/references/evidence_map.md` 는 점검 세션이
로그를 읽는 기준표다. 그 표가 인용한 문자열이 프로덕션에서 바뀌면, 표는
**틀렸다고 말해주지 않고 조용히 낡는다** — 468차 G-2 가 "감시 대상 목록 자체가
낡는 것은 일일 점검이 못 잡는다"고 등록한 것과 같은 실패 경로다.

2026-09-15 에 두 건이 한꺼번에 드러났다.

1. **「예약」을 「실행」으로 읽었다** — `[WarmupRetrain] … 즉시 재학습 예약` 은
   그 자리에서 돌지 않고 08:55 `[PreRetrain]` 에서 소비된다. 장전 점검이 예약
   줄만 보고 재학습 누락을 의심해 `main.py` 를 직접 재추적했다.
2. **「동결」과 「종료」를 못 갈랐다** — 장후 리포트 1-9 가 15:27~15:33 하트비트
   공백을 "6분 38초 완전 동결"로 적었으나, `crash_fault.log` 는 그 구간 앞에
   `[CLEAN EXIT] … PID=13544` 를 남기고 있었다. 프로세스가 **없었던** 것이다
   (런처: `[AUTO-RESTART] 15:10 이후 종료 -- 재시작 안 함`). 설계된 동작이다.

이 파일이 하는 일
-----------------
**로그 문구가 옳은지 판정하지 않는다.** 두 곳이 함께 움직이도록 묶을 뿐이다 —
한쪽만 바뀌면 깨져서 나머지 갱신을 강제한다.

    main.py 의 로그 문자열
        ↕
    evidence_map.md 의 해당 절

깨지면 "고쳐야 할 버그"가 아니라 **"증거지도를 갱신하라"** 는 신호다.

실행:
    pytest tests/test_570_evidence_map_log_string_sync.py
"""
import io
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import pytest  # noqa: E402

_MAIN = os.path.join(_ROOT, "main.py")
_EVMAP = os.path.join(
    _ROOT, ".claude", "skills", "mireuk-daily-check", "references", "evidence_map.md"
)

#: 증거지도가 인용한 문자열. 바꾸려면 evidence_map.md 의 해당 절도 함께 고칠 것.
_WARMUP_SCHEDULE = u"[WarmupRetrain] 세션 재시작 감지"
_PRERETRAIN_SKIP = u"[PreRetrain] 08:55 사전 재학습 스킵"

#: 「동결」과 「프로세스 부재」를 가르는 유일한 증거(`logs/crash_fault.log`).
_LIFECYCLE_MARKERS = (u"[START] ", u"[CLEAN EXIT] ")

#: evidence_map.md 에 실려 있어야 하는 절 제목의 특징 문구.
_EVMAP_SECTIONS = (
    u"「예약」 로그를",
    u"「동결」과 「종료」를",
)


def _read(path):
    with io.open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


@pytest.fixture(scope="module")
def main_src():
    return _read(_MAIN)


@pytest.fixture(scope="module")
def evmap():
    if not os.path.exists(_EVMAP):
        pytest.skip("evidence_map.md 없음 (스킬 미설치 체크아웃)")
    return _read(_EVMAP)


# ── 1. 「예약 → 소비」 두 줄이 모두 프로덕션에 있는가 ────────────────────

def test_1_warmup_schedule_line_exists(main_src):
    """예약 줄이 사라지면 증거지도의 「예약 != 실행」 설명이 근거를 잃는다."""
    assert _WARMUP_SCHEDULE in main_src, (
        u"main.py 에서 %r 를 찾지 못했다 — 로그 문구가 바뀌었으면 "
        u"evidence_map.md 의 「예약」 절도 함께 갱신할 것." % _WARMUP_SCHEDULE
    )


def test_2_preretrain_skip_line_exists(main_src):
    """소비(스킵) 줄 — 예약과 짝을 이루는 쪽."""
    assert _PRERETRAIN_SKIP in main_src, (
        u"main.py 에서 %r 를 찾지 못했다 — evidence_map.md 의 「예약」 절을 "
        u"함께 갱신할 것." % _PRERETRAIN_SKIP
    )


# ── 2. 생명주기 마커 — 「동결/종료」를 가르는 유일한 증거 ────────────────

def test_3_lifecycle_markers_exist(main_src):
    """`[START]` / `[CLEAN EXIT]` 가 없으면 동결과 프로세스 부재를 못 가른다.

    이 둘이 사라지면 2026-09-15 의 오진(부재를 동결로 읽음)이 **다시 가능해진다.**
    """
    missing = [m for m in _LIFECYCLE_MARKERS if m not in main_src]
    assert not missing, (
        u"main.py 가 %s 마커를 더는 쓰지 않는다 — evidence_map.md "
        u"「동결과 종료를 구분하는 법」 절이 무효가 된다." % u", ".join(repr(m) for m in missing)
    )


# ── 3. 증거지도에 두 절이 실제로 실려 있는가 ────────────────────────────

def test_4_evidence_map_has_both_sections(evmap):
    """문서 쪽 절반. 절이 지워지면 테스트가 깨져 기록 소실을 막는다."""
    missing = [t for t in _EVMAP_SECTIONS if t not in evmap]
    assert not missing, (
        u"evidence_map.md 에서 %d개 절을 찾지 못했다: %s"
        % (len(missing), u" / ".join(missing))
    )


def test_5_evidence_map_quotes_lifecycle_markers(evmap):
    """증거지도가 판별 근거로 쓰는 마커를 실제로 적고 있는가."""
    missing = [m.strip() for m in _LIFECYCLE_MARKERS if m.strip() not in evmap]
    assert not missing, (
        u"evidence_map.md 에 %s 가 없다 — 「동결과 종료」 절의 판별표가 불완전하다."
        % u", ".join(missing)
    )


# ── 4. `[OptionFlow]` 스로틀 — 「줄이 적다」를 「죽었다」로 읽지 않기 위한 묶음 ──
#
# [MW0602 582차 후속 / G-3B] 2026-09-21 O-83 판정이 INFO 1줄을 보고 그것이 정상인지
# 확인하려고 **코드를 열어 `_info_every_sec` 를 읽어야 했다.** 증거지도에 그 해설을
# 실었으므로, 해설이 인용한 것들이 프로덕션에서 사라지면 여기서 깨져야 한다.
#
# ⚠ 스로틀 값이 옳은지는 판정하지 않는다 — 그 값은 2026-09-21 MW0601 `b35d363` 의
#   의도된 결정이다(매분 INFO 면 하루 390줄). 여기서는 **문서와 코드가 함께
#   움직이는지**만 본다.

_OPTFLOW_SRC = os.path.join(_ROOT, "collection", "cybos", "weekly_option_flow.py")

#: 증거지도 판별표가 인용한 문자열.
_OPTFLOW_OK = u"[OptionFlow] stored=%d rows"
_OPTFLOW_LATEST_BAR = u"최신봉=%s"
_OPTFLOW_FAIL = u"[OptionFlow] 부분/전체 실패 streak=%d"

#: 30분 스로틀 상수 — 증거지도가 이 값을 그대로 적고 있다.
_OPTFLOW_THROTTLE = u"1800.0"

#: 증거지도 쪽 절 제목의 특징 문구.
_EVMAP_OPTFLOW_SECTION = u"INFO 가 하루 한두 줄뿐인 것은"


@pytest.fixture(scope="module")
def optflow_src():
    if not os.path.exists(_OPTFLOW_SRC):
        pytest.skip("weekly_option_flow.py 없음")
    return _read(_OPTFLOW_SRC)


def test_6_optionflow_success_log_shape(optflow_src):
    """성공 INFO 의 두 축(건수·최신봉)이 살아 있는가.

    `최신봉=` 이 사라지면 증거지도 판별표 1행("최신봉이 전진한다")이 근거를 잃고,
    다음 점검이 다시 **DB 파일 mtime** 이라는 간접 증거로 돌아간다.
    """
    missing = [t for t in (_OPTFLOW_OK, _OPTFLOW_LATEST_BAR) if t not in optflow_src]
    assert not missing, (
        u"weekly_option_flow.py 에서 %s 를 찾지 못했다 — evidence_map.md 의 "
        u"「[OptionFlow]」 절도 함께 갱신할 것."
        % u", ".join(repr(m) for m in missing)
    )


def test_7_optionflow_failure_path_is_separate(optflow_src):
    """실패는 성공과 **다른 줄**로 나온다 — 판별표가 그렇게 적고 있다."""
    assert _OPTFLOW_FAIL in optflow_src, (
        u"weekly_option_flow.py 에서 %r 를 찾지 못했다 — 실패 경로가 없어지면 "
        u"판별표의 「INFO·WARNING 둘 다 없다 = 부재」 행이 무의미해진다."
        % _OPTFLOW_FAIL
    )


def test_8_evidence_map_documents_the_throttle(evmap, optflow_src):
    """문서 쪽 절반 — 절이 있고, 코드의 스로틀 값을 그대로 인용하는가."""
    assert _EVMAP_OPTFLOW_SECTION in evmap, (
        u"evidence_map.md 에서 「[OptionFlow] 스로틀」 절을 찾지 못했다."
    )
    assert _OPTFLOW_THROTTLE in optflow_src, (
        u"weekly_option_flow.py 에 %s 가 없다 — 스로틀이 바뀌었다." % _OPTFLOW_THROTTLE
    )
    assert _OPTFLOW_THROTTLE in evmap, (
        u"evidence_map.md 가 스로틀 값 %s 를 적고 있지 않다 — 코드와 문서가 "
        u"어긋났다." % _OPTFLOW_THROTTLE
    )
