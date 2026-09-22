# -*- coding: utf-8 -*-
"""[MW0601 618차] 종료 의도 기록 + `raw_candles` 절단선.

발단 — 2026-09-22
-----------------
수동 재시작 2회가 런처 로그에 **둘 다 「일시적 크래시」**로 남았다. 그런데
`crash_fault.log` 는 서로 다른 것을 말하고 있었다:

  · 15:08 `[CLEAN EXIT] PID=27016`      — atexit 까지 돈 정상 종료(X → 재시작)
  · 09:42 CLEAN EXIT **없음**            — atexit 도 못 돈 하드킬

종료 의도는 3종인데 표현 수단이 `_exit_normally` 의 존재/부재 **2상태**였다.
그래서 「정상 종료지만 재시작해야 한다」와 「비정상 종료」가 같은 흔적으로
뭉개졌고, 같은 날 1차 진단이 `raw_candles` 당일 max=15:07 을 **「38분 수집
공백」으로 오독**했다(5거래일 비교로 뒤집혔다).

이 파일이 고정하는 것
---------------------
 ① `write_exit_flags` 의 keep_alive 분기 — 재시작은 **파일을 쓰지 않는다**
 ② 기존 두 호출부(daily_close·auto_shutdown) 회귀 — keep_alive=False 유지
 ③ 대시보드 두 분기가 **모두** 의도를 남긴다(재시작 분기 무흔적 재발 차단)
 ④ 절단선이 **파생값**이다 — 리터럴 "15:08" 을 새로 박으면 깨진다
 ⑤ `settings.FORCE_EXIT_TIME` 과 `time_utils.FORCE_EXIT_AT` 이 어긋나지 않는다
"""

import datetime
import io
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.exit_flags import write_exit_flags
from utils.time_utils import FORCE_EXIT_AT, raw_candles_last_ts


# ── ① keep_alive 분기 ──────────────────────────────────────────────────────

def test_user_restart_writes_no_file(tmp_path):
    """🔴 재시작은 파일을 **하나도** 쓰지 않는다 — 런처가 다시 띄워야 한다.

    ⚠ 「의도 파일을 하나 더 만든다」로 가지 않았다. 런처가 읽지 않는 파일은
      아무도 소비하지 않는 죽은 산출물이 되고(FP-CRITICAL 계열), 런처 배치는
      GOTO/괄호 블록 오염 사고 이력이 있어 라벨 하나 때문에 손댈 곳이 아니다.
      의도는 로그로 전달한다.
    """
    d = tmp_path / "data"
    d.mkdir()
    written = write_exit_flags("user_restart", keep_alive=True, root=str(tmp_path))
    assert written == []
    assert not (d / "_exit_normally").exists()
    assert list(d.iterdir()) == []


@pytest.mark.parametrize("reason", ["daily_close", "auto_shutdown", "user_close"])
def test_normal_exit_writes_both_files(tmp_path, reason):
    """정상 종료 3종은 런처 플래그 + 날짜본 마커(513차 FZ-2) **둘 다** 쓴다."""
    d = tmp_path / "data"
    d.mkdir()
    written = write_exit_flags(reason, keep_alive=False, root=str(tmp_path))
    assert len(written) == 2
    flag = d / "_exit_normally"
    assert flag.exists()
    assert flag.read_text(encoding="utf-8").splitlines()[0] == reason

    marker = d / ("shutdown_normal_%s.txt" % datetime.date.today().strftime("%Y%m%d"))
    assert marker.exists(), "날짜본 마커가 없으면 FZ-2 가 다시 가짜 CRITICAL 을 쏟는다"
    assert marker.read_text(encoding="utf-8").splitlines()[0] == reason


def test_exit_log_line_carries_intent(tmp_path, caplog):
    """사후 점검이 읽는 것은 파일이 아니라 **로그**다 — 의도가 거기 실려야 한다.

    `_exit_normally` 는 런처가 읽은 직후 지우므로(start_mireuk.bat) 점검 시점엔
    항상 없다. 그래서 의도는 로그에 남겨야 한다.
    """
    (tmp_path / "data").mkdir()
    with caplog.at_level("INFO", logger="utils.exit_flags"):
        write_exit_flags("user_restart", keep_alive=True, root=str(tmp_path))
    joined = " ".join(r.getMessage() for r in caplog.records)
    assert "intent=user_restart" in joined
    assert "keep_alive=True" in joined


# ── ② 기존 호출부 회귀 ─────────────────────────────────────────────────────

def test_main_callers_keep_normal_exit_semantics():
    """daily_close·auto_shutdown 이 재시작 의미로 바뀌지 않았는가."""
    src = io.open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()
    assert 'self._write_exit_normally_flag("daily_close")' in src
    assert 'self._write_exit_normally_flag("auto_shutdown")' in src
    body = src.split("def _write_exit_normally_flag")[1].split("\n    def ")[0]
    assert "keep_alive=False" in body, "두 호출부는 종전 그대로 파일을 써야 한다"


# ── ③ 대시보드 두 분기 ─────────────────────────────────────────────────────

def test_dashboard_records_both_branches():
    """🔴 재시작 분기가 다시 **무흔적**이 되면 여기서 깨진다.

    종전 `closeEvent` 는 완전 종료만 인라인으로 플래그를 썼다. 재시작은
    코드도 로그도 없어, 런처 라벨 말고는 그 종료를 설명하는 것이 없었다.
    """
    src = io.open(os.path.join(_ROOT, "dashboard", "main_dashboard.py"),
                  encoding="utf-8").read()
    # ⚠ `closeEvent` 는 이 파일에 여럿이다(차트 다이얼로그 등). 메인 윈도우의
    #   것만 집어야 한다 — 종료 선택 다이얼로그 문구를 앵커로 쓴다.
    ce = src.split('"종료 방법을 선택하세요."')[1].split("\n    def ")[0]
    assert '"user_close"' in ce and "keep_alive=False" in ce
    assert '"user_restart"' in ce and "keep_alive=True" in ce
    assert "write_exit_flags" in ce


def test_launcher_contract_untouched():
    """런처는 손대지 않는다 — `_exit_normally` 판정부가 그대로여야 한다.

    이 fix 의 안전성 근거가 「런처 무수정」이다. 배치에 손이 가면 이 가드가
    깨져서 그 사실을 드러낸다.
    """
    bat = io.open(os.path.join(_ROOT, "start_mireuk.bat"),
                  encoding="utf-8", errors="replace").read()
    assert 'IF EXIST "data\\_exit_normally" DEL "data\\_exit_normally"' in bat
    assert "_exit_intent" not in bat, \
        "런처를 건드리려면 이 fix 의 위험 평가(로그 축만)를 다시 해야 한다"


# ── ④⑤ 절단선은 파생값 ────────────────────────────────────────────────────

def test_cutoff_is_derived_not_literal():
    """🔴 절단선은 `FORCE_EXIT_AT − 2분` 이다 — 리터럴을 새로 박으면 안 된다.

    봉 ts=T 의 마감 콜백은 T+1분에 도착하고, `run_minute_pipeline` 이
    `is_force_exit_time(now)` 면 **저장 전에** return 한다. ⇒ 마지막 저장 ts 는
    15:10 − 2분 = 15:08.

    461차 `mdd_pct`(분모 두 출처)·500차 CORE 정의(세 출처)와 같은 유형을
    만들지 않기 위해 값이 아니라 **관계**를 고정한다.
    """
    base = datetime.datetime.combine(datetime.date(2000, 1, 1), FORCE_EXIT_AT)
    assert raw_candles_last_ts() == (base - datetime.timedelta(minutes=2)).time()
    assert raw_candles_last_ts() == datetime.time(15, 8)  # 현행 운영값


def test_force_exit_time_single_truth():
    """`settings.FORCE_EXIT_TIME`(문자열)과 `time_utils.FORCE_EXIT_AT` 일치.

    두 곳을 억지로 합치지 않는다 — 어긋나면 **여기서 깨지게** 한다.
    """
    from config.settings import FORCE_EXIT_TIME
    assert FORCE_EXIT_AT.strftime("%H:%M") == FORCE_EXIT_TIME


def test_pipeline_guard_still_uses_the_constant():
    """중단선이 `is_force_exit_time` 을 통해 걸리는가 — 배선이 살아 있는지."""
    src = io.open(os.path.join(_ROOT, "utils", "time_utils.py"), encoding="utf-8").read()
    body = src.split("def is_force_exit_time")[1].split("\ndef ")[0]
    assert "FORCE_EXIT_AT" in body
    assert "datetime.time(15, 10)" not in body, "리터럴이 되살아나면 출처가 둘이 된다"


def test_legacy_shutdown_log_string_preserved(tmp_path, caplog):
    """🔴 레거시 문구를 지우면 **기존 점검이 조용히 깨진다**.

    `dev_memory/NEXT_TODO.md` 는 정상 마감일에 `[Shutdown] 정상 종료 플래그
    기록` 이 「매번 정확히 2회」(daily_close + auto_shutdown) 나오는 것을 건강
    신호로 센다. 618차가 본문을 옮기면서 하마터면 없앨 뻔했다 — 문자열 앵커는
    호출부가 아니라 **로그를 읽는 쪽**에 있어서 리팩터링에 안 걸린다.
    """
    (tmp_path / "data").mkdir()
    with caplog.at_level("INFO", logger="utils.exit_flags"):
        write_exit_flags("daily_close", keep_alive=False, root=str(tmp_path))
    joined = " ".join(r.getMessage() for r in caplog.records)
    assert "[Shutdown] 정상 종료 플래그 기록" in joined
    assert "(daily_close)" in joined
