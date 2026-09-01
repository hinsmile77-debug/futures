# -*- coding: utf-8 -*-
"""[MW0601 513차] 동결 센티넬이 「스스로 종료한 세션」을 동결로 읽지 않는다.

왜 필요한가 (2026-09-01 실측 — 팝업까지 떴다)
----------------------------------------------
15:40:11 마감 완료 → 15:40:26 자동 종료로 **완전히 정상**인 날인데, 15:45:28 에
CRITICAL 팝업이 떴고 16:30 까지 매분 CRITICAL 이 쌓였다. 08-25·08-26·08-27·08-31
도 모두 같은 모양이다(**매일 45회**, 08-28 은 93회).

498차 F-10 이 이 사건을 막으려고 `daily_close_done` 축을 붙였는데, 실전에서는
**한 번도 성립한 적이 없다.** 두 축이 각각 다른 이유로 빗나갔다:

  · `_exit_normally`   — 런처가 읽은 직후 **지운다**(`start_mireuk.bat:597~598`).
                         센티넬이 볼 시점에는 항상 없다 → 영구 「미측정」.
  · `daily_close_done` — 마커는 15:40:11 인데, 마감 뒤 **15초의 종료 로그**
                         (`자동 종료 실행`)가 15:40:26 에 남는다. F-10 은 마커가
                         **가장 최근** 신호보다 뒤여야 한다고 봤으므로 15초 차이로
                         매번 실패한다. 임계나 표본의 문제가 아니라 **기준 선택**이
                         구조적으로 성립 불가였다.

이 회귀는 「감시자가 양치기 소년이 되는」 형태라 특히 나쁘다 — 경보 피로가 쌓이면
2026-08-19 13:41 의 **진짜 동결**이 같은 문구에 묻힌다.

조치(ⓑ): `main.py:_write_exit_normally_flag()` 가 `_exit_normally` 와 **함께**
런처가 지우지 않는 날짜본 `data/shutdown_normal_<date>.txt` 를 쓴다. 이 마커는
**종료 시점**을 담으므로(마감 완료 시점이 아니라) 정상 종료의 증거가 된다.

🔴 **이 파일의 가장 중요한 테스트는 여전히 「08-19형을 잡는가」다.**
완화가 그 시나리오를 삼키면 안전장치를 없앤 것이 된다.

고정하는 불변식:
① 2026-09-01 재현(마커 302s · 신호 309/309/302s) → EXITED, CRITICAL 아님
② 08-19형(마커 없음 + 플래그 없음 + 전 신호 정체) → FROZEN   ← 미탐 금지
③ 오전 정상 종료 → 재기동 → 오후 동결: 마커가 신호들보다 **먼저**라 FROZEN
④ 종료 마커 축은 `max`(가장 오래된 정체 신호) 기준이다 — `min` 이면 F-10 재발
⑤ CRITICAL 판정문에는 종료 마커 축의 상태가 **반드시** 한 줄 남는다(계측 4원칙 ②·③)
⑥ 마커는 날짜 스코프 — 어제 것이 오늘 판정에 끼어들지 않는다
⑦ `main.py` 가 그 마커를 실제로 쓴다(입력이 없으면 판정 개선은 무의미하다)
⑧ 하드 종료 승격(`FREEZE_SENTINEL_KILL_ENABLED`)은 여전히 건드리지 않는다
"""
import datetime
import inspect
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import scripts.freeze_sentinel as fs  # noqa: E402
from scripts.freeze_sentinel import (  # noqa: E402
    judge, shutdown_marker_age, RC_FROZEN, RC_NOT_APPLICABLE,
    SIG_HEARTBEAT, SIG_TS, SIG_SYSLOG,
)

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STALL = 300.0

#: 2026-09-01 15:45:28 실측 — 팝업을 띄운 바로 그 판정 입력.
#:   heartbeat/[TS] 15:40:19 · SYSTEM.log 15:40:26 · 종료 마커 15:40:26
DAY_20260901 = {SIG_HEARTBEAT: 309.0, SIG_TS: 309.0, SIG_SYSLOG: 302.0}
SHUTDOWN_20260901 = 302.0


# ── ① 2026-09-01 회귀 ───────────────────────────────────────────────────────
def test_20260901_normal_shutdown_is_not_critical():
    """정상 종료한 세션을 동결로 읽지 않는다 — 이 값들이 실제 팝업을 냈다."""
    v = judge(DAY_20260901, stall_sec=STALL, exit_flag_age=None,
              close_done_age=317.0, shutdown_age=SHUTDOWN_20260901)
    assert v["level"] != "CRITICAL"
    assert v["state"] == "EXITED"
    assert v["rc"] == RC_NOT_APPLICABLE
    assert any("shutdown_normal" in d for d in v["details"]), \
        "무엇을 근거로 강등했는지 판정문에 남아야 한다(계측 4원칙 ⑤)"


def test_20260901_without_marker_reproduces_the_false_alarm():
    """조치 전 상태 — 같은 신호인데 마커가 없으면 CRITICAL 이 그대로 나온다.

    이 대비가 「무엇이 문제였는지」를 고정한다: 판정 논리가 아니라 **증거 결손**.
    """
    v = judge(DAY_20260901, stall_sec=STALL, exit_flag_age=None,
              close_done_age=317.0, shutdown_age=None)
    assert v["level"] == "CRITICAL"


def test_close_done_axis_alone_cannot_save_the_day():
    """🔴 F-10 이 실전에서 성립 못 한 이유를 고정한다.

    마감 마커(317s)는 가장 최근 신호(302s)보다 **먼저**라 강등 조건을 못 넘는다.
    이 테스트가 깨지면 F-10 기준이 바뀐 것이므로 이 파일의 전제를 다시 볼 것.
    """
    v = judge(DAY_20260901, stall_sec=STALL, close_done_age=317.0)
    assert v["level"] == "CRITICAL"


# ── ② 🔴 08-19형 동결 — 미탐 금지 ───────────────────────────────────────────
def test_2026_08_19_freeze_still_detected():
    """🔴 **가장 중요한 테스트.**

    13:41 동결은 프로세스가 **살아 있는** 채로 멈춘 것이라 종료 마커가 없다.
    세 마커 축이 모두 미측정이어도 동결 판정은 유지돼야 한다.
    """
    v = judge({SIG_HEARTBEAT: 900.0, SIG_TS: 900.0, SIG_SYSLOG: 880.0},
              stall_sec=STALL, exit_flag_age=None, close_done_age=None,
              shutdown_age=None)
    assert v["level"] == "CRITICAL"
    assert v["state"] == "FROZEN"
    assert v["rc"] == RC_FROZEN


# ── ③ 오전 종료 → 재기동 → 오후 동결 ────────────────────────────────────────
def test_stale_marker_from_earlier_session_does_not_mask_freeze():
    """존재만으로 판정하지 않는다.

    09:30 에 한 번 정상 종료(마커 기록)하고 재기동한 세션이 13:41 에 얼어붙으면,
    마커는 정체 신호들보다 **먼저**다 → 동결 유지.
    """
    v = judge({SIG_HEARTBEAT: 900.0, SIG_TS: 900.0, SIG_SYSLOG: 880.0},
              stall_sec=STALL, shutdown_age=15000.0)
    assert v["level"] == "CRITICAL"
    assert v["state"] == "FROZEN"
    assert any("shutdown_normal" in d and "먼저" in d for d in v["details"]), \
        "왜 강등하지 않았는지가 판정문에 남아야 한다"


# ── ④ 기준은 max(가장 오래된 정체 신호)다 ───────────────────────────────────
def test_marker_axis_uses_oldest_stale_signal_not_newest():
    """마커가 **가장 오래된** 신호보다만 뒤면 강등이다.

    `min`(가장 최근 신호) 기준으로 되돌리면 종료 직후 로그 한 줄에 매번 걸려
    F-10 과 같은 「성립 불가 조건」이 된다 — 2026-09-01 이 정확히 그 형태였다.
    """
    ages = {SIG_HEARTBEAT: 400.0, SIG_TS: 400.0, SIG_SYSLOG: 310.0}
    # 마커(350s)는 가장 오래된 신호(400s)보다 뒤 · 가장 최근 신호(310s)보다는 먼저.
    v = judge(ages, stall_sec=STALL, shutdown_age=350.0)
    assert v["state"] == "EXITED", "min 기준으로 되돌아가면 여기서 깨진다"


def test_marker_older_than_every_signal_is_rejected():
    """경계 — 마커가 가장 오래된 신호와 **같은 나이**면 동결 유지(보수적)."""
    ages = {SIG_HEARTBEAT: 400.0, SIG_TS: 400.0, SIG_SYSLOG: 310.0}
    v = judge(ages, stall_sec=STALL, shutdown_age=400.0)
    assert v["level"] == "CRITICAL"


# ── ⑤ 판정문에 축 상태가 반드시 남는다 ──────────────────────────────────────
def test_critical_always_reports_shutdown_axis():
    """미측정이든 기각이든 **침묵하지 않는다** — 계측 4원칙 ②·③."""
    unmeasured = judge(DAY_20260901, stall_sec=STALL, shutdown_age=None)
    rejected = judge(DAY_20260901, stall_sec=STALL, shutdown_age=9999.0)
    for v in (unmeasured, rejected):
        assert v["level"] == "CRITICAL"
        assert any("shutdown_normal" in d for d in v["details"])


# ── ⑥ 마커 자체 (파일 IO) ───────────────────────────────────────────────────
def test_shutdown_marker_age_none_when_absent(tmp_path):
    assert shutdown_marker_age(str(tmp_path), datetime.datetime.now(),
                               datetime.date(2026, 9, 1)) is None


def test_shutdown_marker_age_measures_marker(tmp_path):
    d = tmp_path / "data"
    d.mkdir()
    (d / "shutdown_normal_20260901.txt").write_text("auto_shutdown\n", encoding="utf-8")
    age = shutdown_marker_age(str(tmp_path), datetime.datetime.now(),
                              datetime.date(2026, 9, 1))
    assert age is not None and 0.0 <= age < 60.0


def test_shutdown_marker_age_is_date_scoped(tmp_path):
    d = tmp_path / "data"
    d.mkdir()
    (d / "shutdown_normal_20260831.txt").write_text("auto_shutdown\n", encoding="utf-8")
    assert shutdown_marker_age(str(tmp_path), datetime.datetime.now(),
                               datetime.date(2026, 9, 1)) is None


# ── ⑦ 입력이 실제로 생산·소비되는가 ─────────────────────────────────────────
def test_main_writes_dated_shutdown_marker():
    """🔴 `main.py` 가 이 마커를 쓰지 않으면 위 판정 개선은 전부 무의미하다.

    ⚠ `_write_exit_normally_flag()` **안**이어야 한다 — 그래야 `_auto_shutdown()`
      경로에서 **종료 시점**으로 갱신된다. 마감 완료 시점(15:40:11)에만 찍히면
      2026-09-01 형이 그대로 재발한다.
    """
    with io.open(os.path.join(_ROOT, "main.py"), encoding="utf-8") as f:
        src = f.read()
    body = src.split("def _write_exit_normally_flag")[1].split("\n    def ")[0]
    assert "shutdown_normal_" in body, \
        "종료 플래그와 같은 함수에서 날짜본 마커를 써야 종료 시점을 담는다"
    assert "_exit_normally" in body, "기존 런처 계약을 깨지 않았는지 함께 고정한다"


def test_both_paths_pass_shutdown_axis():
    """`--once` 진단과 주기 감시가 **같은 입력**을 받는다(498차 입력 결손 재발 방지)."""
    src = inspect.getsource(fs.main)
    assert src.count("shutdown_age=shutdown_marker_age(") == 2


# ── ⑧ 하드 종료 승격은 건드리지 않는다 ──────────────────────────────────────
def test_kill_toggle_untouched():
    """🔴 하드 종료 승격은 주간회의 안건이다 — 이 fix 는 알림 전용을 유지한다."""
    src = inspect.getsource(fs)
    assert "FREEZE_SENTINEL_KILL_ENABLED" in src
    assert "미구현" in src, "하드 종료 미구현 경고가 사라지면 켠 플래그가 동작으로 읽힌다"
    assert "os.kill" not in src and "taskkill" not in src
