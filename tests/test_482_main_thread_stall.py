# -*- coding: utf-8 -*-
"""[MW0601 482차 / F-3] 메인 스레드 정지 계측 — 무관측 구간 회귀 방지.

## 왜 이 계측이 있는가

CB⑤(`CB_PIPE_PAUSE_MS`=5,000ms)와 FZ-1 워치독(`FREEZE_WATCHDOG_STALL_SEC`=180초)
사이에 **주인이 없다.** 두 장치는 서로 다른 것을 재는데 그 사실이 계측에 안 드러났다:

    CB⑤        : 파이프라인 경과시간 = `[PipePerf] total`(S0~S8)
    _tick_header: 메인 스레드 전체 정지시간(Qt 타이머가 못 돈 시간)

2026-08-20 실측 — 5초 초과 정지 4건 전량이 CB⑤ 사정권 밖이었다:

    12:38:05  5,297ms  vs PipePerf   404ms  → 잔차 4,893ms (92%)
    12:40:08  8,375ms  vs PipePerf 2,838ms  → 잔차 5,537ms (66%)
    13:16:04  5,141ms  vs PipePerf 3,183ms  → 잔차 1,958ms (38%)
    13:54:04  5,047ms  vs PipePerf 2,615ms  → 잔차 2,432ms (48%)

2026-08-19 동결(480차)이 정확히 "프로세스는 살아 있는데 메인 스레드가 멈춤"이었고,
그날 실손해가 0이었던 것도 우연히 FLAT이었기 때문이다.

## 이 테스트가 지키는 것

1. 임계 3종의 대소 관계 (DETECT < WARN < ALERT < FZ-1)
2. **차단 플래그를 만들지 않는다** — 소비자 없는 `*_BLOCK_ENABLED = False` 는
   TOX-SEVERE-SPREAD 와 같은 "켜진 적 없는 게이트"를 하나 더 만든다.
3. 로그 앞머리 문구 불변 — 점검 수집기 `block_ms` 패턴과 §11 적신호가 걸려 있다.
4. 상태 속성 명시 초기화 (계측 4원칙 ④ — getattr 폴백 금지)
5. `notify_pipeline_ran()` 시그니처 불변 (453차·471차가 지키는 불변식)
"""
import io
import os
import re
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

_DASH = os.path.join(_ROOT, "dashboard", "main_dashboard.py")


def _dash_src():
    return io.open(_DASH, encoding="utf-8").read()


# --------------------------------------------------------------- 임계 상수
def test_threshold_ordering():
    import config.settings as _st
    from config.settings import (
        MAIN_THREAD_STALL_DETECT_MS, MAIN_THREAD_STALL_WARN_MS,
        MAIN_THREAD_STALL_ALERT_MS, CB_PIPE_PAUSE_MS,
    )
    assert MAIN_THREAD_STALL_DETECT_MS < MAIN_THREAD_STALL_WARN_MS
    assert MAIN_THREAD_STALL_WARN_MS < MAIN_THREAD_STALL_ALERT_MS
    # 🔴 [MW0602 체리픽 조정] 원본은 `ALERT < FREEZE_WATCHDOG_STALL_SEC*1000` 도
    #   요구한다(ALERT 는 FZ-1 하드 종료 **이전에** 울려야 의미가 있다는 취지).
    #   **이 브랜치에는 FZ-1 동결 워치독이 없다**(MW0601 478차 후속 미이관) — 그래서
    #   상수를 무조건 import 하면 ImportError 로 죽는다. 조건부로 검사하되, FZ-1 이
    #   나중에 이관되면 **자동으로 그 불변식이 살아나게** 둔다.
    #   ⚠ 지금은 CB⑤ 위로 아무 상위 장치가 없다 = 이 계측이 그 구간의 유일한 눈이다.
    _fz = getattr(_st, "FREEZE_WATCHDOG_STALL_SEC", None)
    if _fz is not None:
        assert MAIN_THREAD_STALL_ALERT_MS < float(_fz) * 1000
    # WARN 은 CB⑤ 임계와 같은 수를 쓰되 **재는 대상이 다르다**. 값이 같다고 같은
    # 것을 재는 것이 아니라는 점이 이 항목의 요지다(계측 4원칙 ①).
    assert MAIN_THREAD_STALL_WARN_MS == CB_PIPE_PAUSE_MS


def test_no_born_dead_block_gate():
    """차단 플래그를 신설하지 않았는지 — 수집기 §11이 즉시 적신호로 올린다."""
    import config.settings as st
    assert not hasattr(st, "MAIN_THREAD_STALL_BLOCK_ENABLED"), (
        "소비자 없는 차단 게이트를 만들지 마라. 정말 필요하면 소비 코드와 함께 넣고 "
        "config/dailycheck_targets.json 의 documented_disabled_flags 에 등록할 것.")


# ------------------------------------------------------- 로그 포맷 하위호환
#: 새 포맷 실제 출력 예 — 앞머리는 종전과 동일해야 한다.
_NEW_LINE = ("2026-08-20 12:40:08 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 8375ms"
             " — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] |"
             " [MainStall] stall_ms=8375 band=WARN since_pipe_s=5.5")


def _collector_pattern(key):
    src = io.open(os.path.join(
        _ROOT, ".claude", "skills", "mireuk-daily-check", "scripts",
        "collect_evidence.py"), encoding="utf-8").read()
    ns = {"__name__": "_t", "__file__": "x"}
    exec(compile(src, "x", "exec"), ns)
    return re.compile(ns["DEFAULT_CONFIG"]["day_summary_patterns"][key])


def test_collector_block_ms_still_matches_new_format():
    """앞머리를 바꾸면 수집기 §5·§11이 조용히 0건이 된다."""
    m = _collector_pattern("block_ms").search(_NEW_LINE)
    assert m, "block_ms 패턴이 새 포맷을 못 잡는다 — 앞머리 문구가 바뀌었다"
    assert (m.group("ms") or m.group("ms2")) == "8375"


def test_collector_pipe_perf_matches_both_variants():
    """`[PipePerf]` 와 `[PipePerf][DBG]` 둘 다 잡아야 잔차 대조가 성립한다."""
    rx = _collector_pattern("pipe_perf")
    for ln, want in [
        ("2026-08-20 12:40:03 [WARNING] SYSTEM: [PipePerf] total=2838ms | S0=2ms", "2838"),
        ("2026-08-20 12:38:00 [INFO] SYSTEM: [PipePerf][DBG] total=315ms | S0=2ms", "315"),
    ]:
        m = rx.search(ln)
        assert m and m.group("total_ms") == want, ln


def test_log_prefix_literal_unchanged_in_source():
    src = _dash_src()
    assert '"[LiveDBG] _tick_header 간격 %.0fms — 메인 스레드 블로킹 발생 | "' in src, \
        "로그 앞머리 리터럴이 바뀌었다 — 수집기 패턴과 §11 적신호 3곳이 깨진다"


# --------------------------------------------- 계측 4원칙 ④ (폴백 가시화)
def test_state_attributes_are_explicitly_initialised():
    """`getattr(self, "_x", 기본값)` 로 런타임 상태를 읽지 않는다."""
    src = _dash_src()
    # 주석은 제외한다 — 폐지된 형태를 경위 설명으로 코드 옆에 인용해 두었다.
    code = " ".join(ln for ln in src.splitlines()
                    if not ln.lstrip().startswith("#"))
    for attr in ("_tick_header_last_mono", "_pipe_last_done_mono"):
        assert ("self.%s = None" % attr) in src, (
            "%s 명시 초기화가 없다" % attr)
        assert ('getattr(self, "%s"' % attr) not in code, (
            "%s 를 getattr 폴백으로 읽고 있다 (계측 4원칙 4)" % attr)


def test_unmeasured_since_pipe_is_not_zero():
    """파이프라인이 한 번도 안 돈 상태를 `0.0초`로 찍으면 안 된다(원칙 ②)."""
    src = _dash_src()
    assert 'else "NA"' in src, \
        "since_pipe_s 의 미측정 표기(NA)가 사라졌다 — 0.0으로 위장된다"


# ------------------------------------------------------- 453·471차 불변식
def test_notify_pipeline_ran_signature_unchanged():
    src = _dash_src()
    assert "def notify_pipeline_ran(self):" in src, \
        "시그니처를 바꾸면 453차·471차 복구 경로 테스트가 깨진다"
    # 완료 시각 기록은 그 안에서 해야 한다 — 호출부를 건드리지 않기 위한 설계다.
    i = src.find("def notify_pipeline_ran(self):")
    body = src[i:i + 900]
    assert "_pipe_last_done_mono" in body
