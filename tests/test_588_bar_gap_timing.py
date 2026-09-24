# -*- coding: utf-8 -*-
"""[MW0602 588차 후속] 절단선 경계 봉 도착시각 진단 `[BarGapTiming]`.

발단 — 2026-09-23 (이 PC 의 `[BarGap]` 첫 라이브일)
---------------------------------------------------
15:46 `[BarGap]` 이 「절단선 초과 1봉(15:09) — 15:10 파이프라인 중단선 미작동」을
ERROR 로 찍었다. 같은 날 SYSTEM 로그:

  15:09:01 [BAR-CLOSE][CYBOS] ts=15:08
  15:09:59 [BAR-CLOSE][CYBOS] ts=15:09   ← PC 15:10 **이전** 마감 → 가드 통과

봉 롤오버는 브로커 체결시각, force-exit 가드는 PC 시각이다. n=1 이라 결론이
아니므로 **진단 로그만** 붙였다. 이 파일이 고정하는 것:

 ① 경계 봉(15:08·15:09)에만 한 줄, 나머지는 `None`
 ② 2026-09-23 재현 — 15:09 봉이 15:09:59 도착이면 WARNING(경계 역전)
 ③ 정상 도착(15:10:00.x)이면 INFO
 ④ 브로커 오프셋 `None` 은 「미측정」으로 찍는다(0 으로 위장 금지 — 계측 4원칙 ②)
 ⑤ 🔴 라이브 반영 0 — main.py 에서 로그 호출 외에 결과를 읽지 않고, force-exit
    가드·저장 경로 **앞**에 있으며 예외를 밖으로 내지 않는다
"""

import datetime
import io
import os
import re
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.bar_gap import cutoff_timing_line
from utils.time_utils import FORCE_EXIT_AT, raw_candles_last_ts

D = datetime.date(2026, 9, 23)


def _dt(h, m, s=0, us=0):
    return datetime.datetime.combine(D, datetime.time(h, m, s, us))


# ── ① 대상 봉 한정 ─────────────────────────────────────────────────────────

def test_1_only_boundary_bars():
    assert cutoff_timing_line(_dt(15, 7), _dt(15, 8, 1)) is None
    assert cutoff_timing_line(_dt(10, 0), _dt(10, 1, 0)) is None
    assert cutoff_timing_line(_dt(15, 10), _dt(15, 11, 0)) is None
    # 경계 봉은 절단선 파생값에서 나온다 — 리터럴이 아니다
    last = raw_candles_last_ts()
    assert cutoff_timing_line(_dt(last.hour, last.minute), _dt(15, 9, 1)) is not None


def test_1b_non_datetime_ts_is_ignored():
    """ts 가 문자열이면 조용히 None — 진단이 파이프라인을 막으면 안 된다."""
    assert cutoff_timing_line("2026-09-23 15:09:00", _dt(15, 9, 59)) is None
    assert cutoff_timing_line(None, _dt(15, 9, 59)) is None


# ── ② 2026-09-23 재현 ──────────────────────────────────────────────────────

def test_2_reproduces_20260923_boundary_inversion():
    msg, level = cutoff_timing_line(_dt(15, 9), _dt(15, 9, 59, 400000), 0.9)
    assert level == "WARNING"
    assert "ts=15:09" in msg
    assert "가드=통과 (기대 중단)" in msg
    assert "경계 역전" in msg
    assert "-0.600s" in msg
    assert "+0.90s" in msg


# ── ③ 정상 ──────────────────────────────────────────────────────────────────

def test_3_normal_arrivals_are_info():
    msg, level = cutoff_timing_line(_dt(15, 9), _dt(15, 10, 0, 120000), -0.2)
    assert level == "INFO" and "가드=중단 (기대 중단)" in msg and "역전" not in msg
    msg, level = cutoff_timing_line(_dt(15, 8), _dt(15, 9, 1), 0.0)
    assert level == "INFO" and "가드=통과 (기대 통과)" in msg


def test_3b_cutline_bar_arriving_late_is_flagged():
    """절단선 봉(15:08)이 15:10 이후 도착하면 반대 방향 역전 — 이것도 WARNING."""
    msg, level = cutoff_timing_line(_dt(15, 8), _dt(15, 10, 0, 500000), None)
    assert level == "WARNING" and "가드=중단 (기대 통과)" in msg


# ── ④ 미측정 ≠ 0 ────────────────────────────────────────────────────────────

def test_4_none_offset_is_unmeasured_not_zero():
    msg, _ = cutoff_timing_line(_dt(15, 9), _dt(15, 10, 0), None)
    assert "브로커−PC 시계=미측정" in msg
    assert "+0.00s" not in msg


def test_4b_force_exit_at_consistency():
    """가드 판정은 time_utils.FORCE_EXIT_AT 단일 출처와 같아야 한다."""
    assert FORCE_EXIT_AT == datetime.time(15, 10)


# ── ⑤ 라이브 반영 0 (소스 텍스트 불변식) ─────────────────────────────────────

def _on_candle_closed_src():
    with io.open(os.path.join(_ROOT, "main.py"), encoding="utf-8") as f:
        src = f.read()
    start = src.index("    def _on_candle_closed(self, candle: dict) -> None:")
    end = src.index("\n    def ", start + 10)
    return src[start:end]


def test_5_diag_is_before_guards_and_log_only():
    body = _on_candle_closed_src()
    i_diag = body.index("cutoff_timing_line")
    assert i_diag < body.index("if is_pre_market(now):")
    assert i_diag < body.index("if is_force_exit_time(now):")

    # 진단 블록(try … except) 추출
    blk_start = body.rindex("try:", 0, i_diag)
    blk_end = body.index("except Exception as _bgt_e:", i_diag)
    blk = body[blk_start:blk_end]
    # 결과는 로그 호출에만 쓰인다 — return·self 대입·candle 변경 없음
    assert "return" not in blk
    assert not re.search(r"self\.\w+\s*=", blk)
    assert not re.search(r"candle\[[^\]]+\]\s*=", blk)
    assert "log_manager.system(_bgt[0], _bgt[1])" in blk
    # 예외를 밖으로 내지 않는다
    tail = body[blk_end:blk_end + 200]
    assert "raise" not in tail.split("# ──")[0]


def test_5b_guard_logic_untouched():
    """가드 자체는 여전히 PC 시각 판정이다 — 이 커밋은 가드를 바꾸지 않았다."""
    body = _on_candle_closed_src()
    assert "if is_force_exit_time(now):" in body
    assert "_ts_run_force_exit_pass(self, candle)" in body
