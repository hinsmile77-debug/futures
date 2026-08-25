# -*- coding: utf-8 -*-
"""[MW0601 493차 후속5 / F-P] 메인 스레드 정지 시점의 스택을 남긴다.

왜 필요한가 (2026-08-25 실측)
-----------------------------
감시 공백이 **구조적**이다:

    2초  `[MainStall]` 검출 하한
    5초  WARN 밴드
    30초 `[FaultHandler] 행감지` — 여기부터 스택이 남는다
    180초 FZ-1 워치독

즉 **5초~30초 구간에는 아무 스택도 안 남는다.** 그런데 실측 정지는 그 구간에
몰려 있다 — 2026-08-25 하루에 **28건**, 5초 초과 7건, 최대 **21,781ms**.
482차 F-3 섀도가 2주째 "몇 번 멈췄다"만 세고 **"무엇이 멈추게 했는지"** 는
못 남기고 있었다. 스택이 없으면 관찰이 끝나도 원인을 고를 수 없다.

⚠ `faulthandler.dump_traceback()` 은 **GIL을 쥐고 쓴다** — 폭주하면 계측 자체가
새 지연원이 된다. 그래서 레이트리밋이 fix의 일부이고, 이 파일이 그것을 고정한다.
안전장치가 새 사고를 만드는 것이 여기서 가장 피해야 할 결과다.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["MIREUK_TEST_MODE"] = "1"
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from dashboard.main_dashboard import (  # noqa: E402
    should_dump_stall_traceback, dump_stall_traceback,
)
from config import settings  # noqa: E402

KW = dict(enabled=True, min_ms=5_000, min_interval=60.0, daily_max=20)


# ── 임계 ────────────────────────────────────────────────────────────────────
def test_below_threshold_is_not_a_suppression():
    """임계 미만은 **대상 밖**이지 억제가 아니다 — 사유 로그를 남기지 않는다."""
    do, why = should_dump_stall_traceback(2_500, 100.0, None, 0, **KW)
    assert do is False
    assert why is None, "임계 미만마다 '생략' 로그가 뜨면 그것이 새 노이즈다"


def test_at_and_above_threshold_dumps():
    for ms in (5_000, 8_625, 21_781):
        do, why = should_dump_stall_traceback(ms, 100.0, None, 0, **KW)
        assert do is True, "%dms 에서 스택을 안 남긴다" % ms
        assert why is None


def test_threshold_covers_the_2026_08_25_gap():
    """실측 최장 정지(21,781ms)와 최초 관측(8,625ms)이 둘 다 대상인가.

    그리고 30초 `[FaultHandler]` 가 이미 덮는 구간과 **겹쳐도 무해**하다 —
    중복 기록이 미기록보다 낫다.
    """
    assert should_dump_stall_traceback(8_625, 1.0, None, 0, **KW)[0] is True
    assert should_dump_stall_traceback(21_781, 1.0, None, 0, **KW)[0] is True


# ── 레이트리밋 ──────────────────────────────────────────────────────────────
def test_rate_limited_within_interval():
    """분당 1회 — `dump_traceback` 이 GIL을 쥐므로 폭주를 막는다."""
    do, why = should_dump_stall_traceback(9_000, now_mono=130.0,
                                          last_mono=100.0, today_count=1, **KW)
    assert do is False
    assert why and "레이트리밋" in why, "억제 사유가 없으면 나중에 이유를 못 찾는다"


def test_allowed_after_interval():
    do, why = should_dump_stall_traceback(9_000, now_mono=161.0,
                                          last_mono=100.0, today_count=1, **KW)
    assert do is True and why is None


def test_daily_cap_enforced_with_reason():
    do, why = should_dump_stall_traceback(9_000, 10_000.0, None, 20, **KW)
    assert do is False
    assert why and "일일 상한" in why


def test_daily_cap_boundary():
    """19회째는 통과, 20회째부터 차단(상한이 '이미 20회 찍었다'를 뜻한다)."""
    assert should_dump_stall_traceback(9_000, 1e6, None, 19, **KW)[0] is True
    assert should_dump_stall_traceback(9_000, 1e6, None, 20, **KW)[0] is False


def test_disabled_switch_is_honored_and_visible():
    do, why = should_dump_stall_traceback(9_000, 1.0, None, 0,
                                          enabled=False, min_ms=5_000,
                                          min_interval=60.0, daily_max=20)
    assert do is False
    assert why == "비활성", "꺼둔 것도 로그에 드러나야 한다(죽은 계측 방지)"


# ── 실제 덤프 ───────────────────────────────────────────────────────────────
def test_dump_writes_file_with_header(tmp_path):
    ok = dump_stall_traceback(str(tmp_path), "20260825", 8_625.0, since_pipe_s=0.3)
    assert ok is True
    path = tmp_path / "logs" / "mainstall_traceback_20260825.log"
    assert path.exists()
    body = path.read_text(encoding="ascii", errors="replace")
    assert "[MainStall]" in body
    assert "stall_ms=8625" in body
    assert "since_pipe_s=0.3" in body
    assert "Thread" in body or "File " in body, "스택 본문이 없다 — 헤더만 찍혔다"


def test_dump_appends_not_truncates(tmp_path):
    """append 여야 한다 — 두 번째 정지가 첫 번째 스택을 지우면 안 된다."""
    dump_stall_traceback(str(tmp_path), "20260825", 6_000.0)
    dump_stall_traceback(str(tmp_path), "20260825", 7_000.0)
    body = (tmp_path / "logs" / "mainstall_traceback_20260825.log").read_text(
        encoding="ascii", errors="replace")
    assert body.count("[MainStall]") == 2


def test_unmeasured_pipe_elapsed_is_na(tmp_path):
    """`since_pipe_s=None` 은 **NA**로 남는다 — 0.0으로 위장하지 않는다(4원칙 ②)."""
    dump_stall_traceback(str(tmp_path), "20260825", 6_000.0, since_pipe_s=None)
    body = (tmp_path / "logs" / "mainstall_traceback_20260825.log").read_text(
        encoding="ascii", errors="replace")
    assert "since_pipe_s=NA" in body


def test_dump_never_raises(tmp_path):
    """계측 실패가 1초 타이머를 죽이면 안 된다 — 예외 대신 False."""
    bad = str(tmp_path / "nope" / "\x00invalid")
    assert dump_stall_traceback(bad, "20260825", 6_000.0) is False


# ── 설정 ────────────────────────────────────────────────────────────────────
def test_settings_defaults_are_sane():
    assert settings.MAIN_STALL_TRACEBACK_MIN_MS >= settings.MAIN_THREAD_STALL_WARN_MS, (
        "스냅샷 임계가 WARN 밴드보다 낮으면 2초짜리 정지마다 GIL을 잡는다")
    assert settings.MAIN_STALL_TRACEBACK_MIN_INTERVAL_SEC >= 30.0
    assert 1 <= settings.MAIN_STALL_TRACEBACK_DAILY_MAX <= 200
