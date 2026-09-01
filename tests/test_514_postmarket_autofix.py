# -*- coding: utf-8 -*-
"""[MW0601 514차] 2026-09-01 장후 자동조치 3건의 불변식.

무엇을 고정하는가
-----------------
2026-09-01 은 **원인불명 외부 진입 38건 / -1,630,766원**으로 끝났고, 그중 마지막
1건(15:34:46 매수 3계약)이 **청산 시도 한 번 없이 밤을 넘겼다**(이상점 1-6,
절대원칙 §1 오버나이트 금지 위반).

세 겹이 동시에 조용했다 — 그 조용함을 각각 하나씩 깬다:

  F-A (Fix P1-3)  15:40 `daily_close()` 가 잔여 포지션을 **보지도 않고** 지나갔다
  F-B (고도화①)   15:12 FLAT 가드는 15:34 에 생긴 위험을 **구조적으로** 볼 수 없었다
  F-C (고도화②)   외부 진입 38건이 TRADE 로그에만 있고 **경보 채널에는 0건**이었다

🔴 **셋 다 「알림 전용」이다 — 이 파일이 지키는 가장 중요한 불변식이 그것이다.**
주문·청산 실행 경로를 바꾸는 것은 Fix P0-2 이고 주간회의 승인 대상이다. 자동조치가
그 선을 넘지 않았음을 코드로 못박는다(§5 「라이브 반영 0」 불변식).
"""
import ast
import datetime
import os
import re
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

_MAIN = os.path.join(_ROOT, "main.py")
_GUARD = os.path.join(_ROOT, "scripts", "force_flat_guard.py")


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def _func_src(path, name):
    """모듈에서 함수/메서드 하나의 소스만 떼어낸다(전역 grep 오탐 방지).

    ⚠ `end_lineno` 를 쓰지 않는다 — **Python 3.7 에는 없다**(3.8 신설). 런타임이
      py37_32(Cybos COM 필수)이므로 들여쓰기로 끝을 찾는다.
    """
    lines = _read(path).splitlines()
    for node in ast.walk(ast.parse(_read(path))):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name != name:
            continue
        start = node.lineno - 1
        indent = len(lines[start]) - len(lines[start].lstrip())
        end = len(lines)
        for i in range(start + 1, len(lines)):
            stripped = lines[i].strip()
            if not stripped:
                continue
            if len(lines[i]) - len(lines[i].lstrip()) <= indent:
                end = i
                break
        return "\n".join(lines[start:end])
    raise AssertionError("함수를 찾지 못했다: %s:%s" % (path, name))


# ══════════════════════════════════════════════════════════════════════════
# F-A — daily_close() 진입부 잔여 포지션 경보 (Fix P1-3)
# ══════════════════════════════════════════════════════════════════════════

def test_fa_daily_close_checks_residual_position():
    """마감이 잔여 포지션을 **본다**. 2026-09-01 에는 보지도 않고 지나갔다."""
    src = _func_src(_MAIN, "daily_close")
    assert "[DailyCloseResidual]" in src, (
        "daily_close() 가 잔여 포지션을 확인하지 않는다 — 이상점 1-6 재발 경로"
    )
    assert "self.position.status" in src


def test_fa_residual_check_runs_before_stats():
    """확인은 마감 통계·리셋 **앞**이다.

    뒤에 두면 리셋이 이미 상태를 지운 뒤라 아무것도 못 본다
    (계측 4원칙 ④ — 「리셋 전에 스냅샷을 잡아라」와 같은 함정).
    """
    src = _func_src(_MAIN, "daily_close")
    assert src.index("[DailyCloseResidual]") < src.index("self.position.daily_stats()")


def test_fa_distinguishes_unmeasured_from_flat():
    """상태를 못 읽으면 「FLAT」이 아니라 **미측정**이다 (계측 4원칙 ②)."""
    src = _func_src(_MAIN, "daily_close")
    seg = src[src.index("[DailyCloseResidual]"):]
    assert "미측정" in seg, "읽기 실패를 FLAT 과 같은 문구로 만들면 안 된다"
    assert "FLAT 확인이 아니다" in seg


def test_fa_checks_both_axes():
    """엔진 포지션 축과 브로커 잔량 축을 **둘 다** 건다 (계측 4원칙 ⑤).

    한 축만 보면 엔진이 FLAT 인데 브로커에 잔량이 남은 형태를 통째로 놓친다.
    """
    src = _func_src(_MAIN, "daily_close")
    seg = src[src.index("[DailyCloseResidual]"):]
    assert "_integrity_broker_qty" in src
    assert "broker_cached" in seg


def test_fa_is_alert_only_no_exit_order():
    """🔴 **경보만 한다 — 청산 주문을 내지 않는다.**

    마감 절차에 자동 청산을 통합하는 것은 Fix P0-2 이고 주문·청산 실행 경로
    변경이라 주간회의 승인 대상이다. 자동조치가 그 선을 넘으면 안 된다.
    """
    src = _func_src(_MAIN, "daily_close")
    start = src.index("[MW0601 514차 / 장후 Fix P1-3]")
    end = src.index("self.position.daily_stats()")
    block = src[start:end]
    forbidden = ["send_order", "_ts_time_exit_pass", "force_exit", "close_position",
                 "SendOrder", "execute_exit", "_exit_position"]
    for token in forbidden:
        assert token not in block, (
            "P1-3 블록이 주문·청산 경로를 호출한다(%s) — 이것은 승인 대기 Fix P0-2 다"
            % token
        )


# ══════════════════════════════════════════════════════════════════════════
# F-B — force_flat_guard 반복 판정 (고도화①)
# ══════════════════════════════════════════════════════════════════════════

def test_fb_extra_times_setting_exists():
    import config.settings as st
    assert isinstance(st.FORCE_FLAT_GUARD_EXTRA_AT, (list, tuple))
    # 15:40 마감 **직전**을 반드시 포함한다 — 2026-09-01 의 15:34:46 을 잡는 축이다.
    assert "15:39" in list(st.FORCE_FLAT_GUARD_EXTRA_AT)


def test_fb_primary_time_unchanged():
    """🔴 `FORCE_FLAT_GUARD_AT` 는 **건드리지 않는다.**

    26주 WFA 재검증 등록 상수다(CLAUDE.md 480차 항목). 값·타입을 바꾸면 그 항목의
    대조 대상이 어긋난다(461차 `mdd_pct` 교훈). 축을 더하기만 한다.
    """
    import config.settings as st
    assert st.FORCE_FLAT_GUARD_AT == "15:12"
    assert isinstance(st.FORCE_FLAT_GUARD_AT, str)


def test_fb_order_path_still_disabled():
    """🔴 반복 판정이 되어도 **주문 권한은 없다.** 1단계 성격 무변경."""
    import config.settings as st
    assert st.FORCE_FLAT_GUARD_ORDER_ENABLED is False


def test_fb_worse_rc_ranks_by_severity_not_number():
    """반복 판정의 종합은 `max(rc)` 가 아니다.

    RC 숫자는 심각도 순이 아니다 — 미청산(3)이 가장 심각한데 비거래일(6)보다
    **작다**. `max` 를 쓰면 미청산이 조용히 묻힌다.
    """
    from scripts.force_flat_guard import (
        _worse_rc, RC_OK, RC_UNCLOSED, RC_PROCESS_DEAD, RC_UNKNOWN,
        RC_NOT_APPLICABLE,
    )
    assert _worse_rc(RC_OK, RC_UNCLOSED) == RC_UNCLOSED
    assert _worse_rc(RC_UNCLOSED, RC_NOT_APPLICABLE) == RC_UNCLOSED   # ← max 였다면 6
    assert _worse_rc(RC_NOT_APPLICABLE, RC_UNCLOSED) == RC_UNCLOSED
    assert _worse_rc(RC_OK, RC_PROCESS_DEAD) == RC_PROCESS_DEAD
    assert _worse_rc(RC_OK, RC_UNKNOWN) == RC_UNKNOWN
    assert _worse_rc(RC_OK, RC_NOT_APPLICABLE) == RC_OK
    assert _worse_rc(RC_UNCLOSED, RC_PROCESS_DEAD) == RC_UNCLOSED


def test_fb_extra_times_parser_is_defensive():
    """설정이 비었거나 문자열 하나여도 죽지 않는다 — 감시자가 죽는 것이 가장 나쁘다."""
    import config.settings as st
    from scripts.force_flat_guard import _extra_times
    orig = st.FORCE_FLAT_GUARD_EXTRA_AT
    try:
        st.FORCE_FLAT_GUARD_EXTRA_AT = []
        assert _extra_times() == []          # 빈 값 = 종전 단발 동작
        st.FORCE_FLAT_GUARD_EXTRA_AT = "15:39"
        assert _extra_times() == ["15:39"]   # 문자열 하나도 받는다
        st.FORCE_FLAT_GUARD_EXTRA_AT = ["15:20", " ", "15:30"]
        assert _extra_times() == ["15:20", "15:30"]
    finally:
        st.FORCE_FLAT_GUARD_EXTRA_AT = orig


def test_fb_judge_and_emit_does_not_place_orders():
    """🔴 반복 판정 경로 전체에 주문 호출이 없다."""
    src = _read(_GUARD)
    for token in ["send_order", "SendOrder", "BuyOrder", "SellOrder", "dynamicCall"]:
        assert token not in src, "F-2 가드는 알림 전용이다 — %s 가 있으면 안 된다" % token


def test_fb_judge_logic_unchanged():
    """판정 함수 자체는 손대지 않았다 — 호출 지점만 늘었다.

    2026-09-01 15:12 의 「FLAT · 정상」은 **그 시점의 사실로서 옳았다.**
    고친 것은 판정이 아니라 판정 횟수다.
    """
    from scripts.force_flat_guard import judge, RC_OK, RC_UNCLOSED
    now = datetime.datetime(2026, 9, 1, 15, 12, 0)
    hb = {"written_at": "2026-09-01T15:11:50", "beat_age_sec": 1.0, "pid": 1, "strikes": 0}
    flat = {"status": "FLAT", "quantity": 0, "saved_at": "2026-09-01 15:00:00"}
    assert judge(now, hb, flat, stale_sec=180.0)["rc"] == RC_OK

    # 15:39 — 15:34:46 에 들어온 외부 매수 3계약이 여기서 잡힌다(2026-09-01 재현)
    now = datetime.datetime(2026, 9, 1, 15, 39, 0)
    hb = {"written_at": "2026-09-01T15:38:50", "beat_age_sec": 1.0, "pid": 1, "strikes": 0}
    held = {"status": "LONG", "quantity": 3, "saved_at": "2026-09-01 15:34:46"}
    v = judge(now, hb, held, stale_sec=180.0)
    assert v["rc"] == RC_UNCLOSED and v["level"] == "CRITICAL"


# ══════════════════════════════════════════════════════════════════════════
# F-C — 외부 진입 실시간 경보 (고도화② · P5-신규)
# ══════════════════════════════════════════════════════════════════════════

def test_fc_external_entry_raises_alert():
    """외부 진입이 **경보 채널**에 뜬다. 2026-09-01 에는 TRADE 로그에만 있었다."""
    src = _read(_MAIN)
    assert "[ExternalEntry]" in src
    # ⚠ 주석에도 같은 문구가 있으므로 **실제 로그 호출**(f-string)을 찾는다.
    idx = src.index('f"[체결동기화] 외부진입 {side}')
    tail = src[idx:idx + 3000]
    assert "[ExternalEntry]" in tail, "경보가 외부진입 검출 지점에 붙어 있지 않다"
    assert '"ERROR"' in tail, "경보 레벨이 ERROR 가 아니면 대시보드 경보 탭에 안 뜬다"


def test_fc_counters_are_initialized_not_getattr_fallback():
    """카운터는 `__init__` 에서 **명시 초기화**한다 (계측 4원칙 ④).

    `getattr(self, "_x", 0)` 으로 읽으면 할당 누락이 조용히 0 으로 위장된다 —
    2026-08-11 에 같은 형태가 하루 4건 나왔다.
    """
    src = _read(_MAIN)
    for name in ("_external_entry_legs_today", "_external_entry_qty_today"):
        assert re.search(r"self\.%s\s*:\s*int\s*=\s*0" % name, src), (
            "%s 가 __init__ 에서 명시 초기화되지 않았다" % name
        )
        assert 'getattr(self, "%s"' % name not in src


def test_fc_zero_is_reported_as_measured():
    """0 을 침묵으로 처리하지 않는다 (계측 4원칙 ②).

    "오늘 외부 진입이 없었다"와 "계측이 죽어 있었다"가 같은 모양이면 안 된다.
    """
    src = _func_src(_MAIN, "daily_close")
    assert "오늘 외부 진입 0건" in src
    assert "실측 — 미측정이 아니다" in src


def test_fc_snapshot_taken_before_reset():
    """리셋 **전에** 값을 읽는다 (계측 4원칙 ④ — `_ccf_today` 관례)."""
    src = _func_src(_MAIN, "daily_close")
    assert src.index("_ee_legs = self._external_entry_legs_today") < \
        src.index("self._external_entry_legs_today = 0")


def test_fc_is_alert_only_no_gate_or_order_change():
    """🔴 **차단하지 않는다. 경보만 한다.**

    이 지점은 이미 체결된 사실을 엔진 상태에 반영하는 동기화 경로다. 여기서
    게이트를 걸거나 주문을 내면 이중 청산·수량 불일치를 만든다.
    """
    src = _read(_MAIN)
    start = src.index("[MW0601 514차 / 장후 고도화② · P5-신규] 외부 진입 **실시간 경보**")
    block = src[start:start + 2200]
    forbidden = ["send_order", "SendOrder", "block", "return False",
                 "size_multiplier", "_exit_position", "close_position"]
    for token in forbidden:
        assert token not in block, (
            "외부진입 경보 블록이 매매 경로를 건드린다(%s) — 알림 전용이어야 한다" % token
        )


def test_fc_no_slack():
    """Slack 은 쓰지 않는다 — 사용자 결정(개발단계 직접 모니터링).

    `scripts/force_flat_guard.py:emit()` 이 같은 이유로 Slack 을 쓰지 않는다.
    """
    src = _read(_MAIN)
    start = src.index("[MW0601 514차 / 장후 고도화② · P5-신규] 외부 진입 **실시간 경보**")
    block = src[start:start + 2200]
    # ⚠ 주석에 "Slack 은 쓰지 않는다"라고 **적혀 있으므로** 낱말이 아니라
    #   **호출 형태**를 본다. 규약을 설명한 문장이 규약 위반으로 잡히면 안 된다.
    for call in ["notify(", "notify_", "_send(", "slack_queue", "enqueue("]:
        assert call not in block, "외부진입 경보가 Slack 경로를 쓴다(%s)" % call


# ══════════════════════════════════════════════════════════════════════════
# 전체 — 자동조치가 넘지 않아야 할 선
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("toggle,expected", [
    ("CB_CONSEC_STOP_LIMIT", 9999),
    ("CB3_P4_GRADE_BLOCK_ENABLED", False),
    ("FP_CRITICAL_GRADE_BLOCK_ENABLED", False),
    ("TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED", False),
    ("MAX_CONTRACTS", 3),
    ("FORCE_FLAT_GUARD_ORDER_ENABLED", False),
])
def test_absolute_principle_toggles_untouched(toggle, expected):
    """🔴 이번 자동조치는 절대원칙·한시예외 토글을 **하나도** 건드리지 않았다.

    전부 C등급(승인 대상)이다. 계측·경보 작업이 조용히 이 선을 넘는 것을 막는다.
    """
    import config.settings as st
    assert getattr(st, toggle) == expected
