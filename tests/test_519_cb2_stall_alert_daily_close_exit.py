# -*- coding: utf-8 -*-
"""[MW0601 519차 / 사용자 지시] CB② 복원 · 정지 경보 · 마감 잔여 청산.

세 항목 모두 **사용자가 직접 지시**해 구현했다 — 자동조치가 C등급 선을 넘은 것이
아니다(`tests/test_514_postmarket_autofix.py` 의 토글 표도 함께 갱신했다).

- **CB②** `CB_CONSEC_STOP_LIMIT` 9999 → **3**. 재검토 기한 2026-08-29 초과 5일.
  선행조건(489차 시간창·포지션 단위 계측)은 이미 끝나 있었다.
- **정지 경보** `[MainStall]` ALERT(≥15초)를 대시보드 「2 경보」 탭으로. 종전에는
  모듈 로거로만 나가 **파일에만** 남았다.
- **F-1** `daily_close()` 진입 시 잔여 포지션을 상한 안에서 시장가 청산.
  514차의 탐지를 집행으로 승격. 절대원칙 §1의 마지막 집행자.
"""
from __future__ import annotations

import ast
import os
import re
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

_DASH = os.path.join(_ROOT, "dashboard", "main_dashboard.py")


def _read(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read()


@pytest.fixture(scope="module")
def main_src():
    return _read(os.path.join(_ROOT, "main.py"))


@pytest.fixture(scope="module")
def dash_src():
    return _read(_DASH)


# ═══════════════════════════════════════════════════════════════════════════
# §1. CB② 복원
# ═══════════════════════════════════════════════════════════════════════════

def test_cb2_limit_restored_to_three():
    from config.settings import CB_CONSEC_STOP_LIMIT
    assert CB_CONSEC_STOP_LIMIT == 3


def test_cb2_limit_inside_allowed_band():
    """허용 범위는 2~3 — 9999(유예)로 되돌아가면 실패한다."""
    from config.settings import CB_CONSEC_STOP_LIMIT
    assert 2 <= CB_CONSEC_STOP_LIMIT <= 3


def test_cb2_window_unchanged():
    """복원은 **한도만** 바꿨다 — 창은 절대원칙 ② 문구 그대로 300초."""
    from config.settings import CB_CONSEC_STOP_WINDOW_SEC
    assert CB_CONSEC_STOP_WINDOW_SEC == 300


def test_cb2_prerequisite_measurement_still_wired(main_src):
    """489차 계측이 살아 있어야 복원이 안전하다.

    시간창·포지션 중복제거가 없으면 한도 3에서 **포지션 하나의 계단식 손절만으로**
    당일 정지가 성립한다 — 절대원칙 ②가 뜻한 바가 아니다.
    """
    tree = ast.parse(main_src)
    calls = [n for n in ast.walk(tree)
             if isinstance(n, ast.Call)
             and getattr(n.func, "attr", None) == "record_stop_loss"]
    assert len(calls) == 4, "record_stop_loss 호출부가 4곳이 아니다: %d" % len(calls)
    bare = [c for c in calls if not c.args and not c.keywords]
    assert not bare, "포지션 키 없이 부르는 곳이 있다 — 레그 단위 폴백으로 샌다"


def test_cb2_halts_at_three_distinct_positions():
    """서로 다른 3포지션이 창 안에 들면 실제로 HALT 한다(운영값 그대로)."""
    from config.constants import CB_STATE_HALTED
    from safety.circuit_breaker import CircuitBreaker
    cb = CircuitBreaker(emergency_exit_callback=lambda *a, **k: None)
    cb.record_stop_loss("p1")
    cb.record_stop_loss("p2")
    assert cb.state != CB_STATE_HALTED, "2회에 멈추면 안 된다(한도 3)"
    cb.record_stop_loss("p3")
    assert cb.state == CB_STATE_HALTED, "3회에 HALT 하지 않는다 — 복원이 무력하다"


def test_cb2_same_position_legs_do_not_halt():
    """같은 포지션의 계단식 청산 레그로는 정지하지 않는다 — 복원의 안전 전제."""
    from config.constants import CB_STATE_HALTED
    from safety.circuit_breaker import CircuitBreaker
    cb = CircuitBreaker(emergency_exit_callback=lambda *a, **k: None)
    for _ in range(6):
        cb.record_stop_loss("2026-09-02 08:45:10")
    assert cb.state != CB_STATE_HALTED
    assert cb.status_dict()["consec_stops"] == 1


def test_cb2_phase5_gate_reports_restored_but_not_met():
    """전환기준 ⑤는 **값 복원만으로 충족되지 않는다**(발동 1회 확인이 남았다)."""
    from strategy.ops import phase5_gate_status as G
    import config.settings as st
    state, msg = G._chk_cb2(st)
    assert state == G.UNMEASURED, "값이 3인데 게이트가 %s 다" % state
    assert "복원" in msg


def test_cb2_expectations_moved_everywhere():
    """기대값 9999가 남아 있으면 점검이 정상을 이상으로 판정한다."""
    collector = _read(os.path.join(
        _ROOT, ".claude", "skills", "mireuk-daily-check",
        "scripts", "collect_evidence.py"))
    assert '{"name": "CB_CONSEC_STOP_LIMIT", "expect": "3"' in collector

    autofix = _read(os.path.join(_ROOT, "tests", "test_514_postmarket_autofix.py"))
    assert '("CB_CONSEC_STOP_LIMIT", 3)' in autofix
    assert '("CB_CONSEC_STOP_LIMIT", 9999)' not in autofix


# ═══════════════════════════════════════════════════════════════════════════
# §2. 메인 스레드 정지 → 「2 경보」 탭
# ═══════════════════════════════════════════════════════════════════════════

def test_stall_alert_routed_to_alert_tab(dash_src):
    """ALERT 밴드가 log_panel 로 간다 — 파일 로거만으로는 화면에 안 뜬다."""
    assert "[MainStall] 🔴 미륵이 화면·판단이" in dash_src
    idx = dash_src.index("[MainStall] 🔴 미륵이 화면·판단이")
    head = dash_src[idx - 1200:idx]
    assert 'self.log_panel.append(' in head
    assert '"all", "ERROR"' in head, "ERROR 태그가 아니면 「2 경보」 탭 라우팅을 못 탄다"


def test_stall_alert_gated_on_alert_band_only(dash_src):
    """WARN(5~15초)은 올리지 않는다 — 올리면 경보 탭이 잡음으로 덮인다."""
    idx = dash_src.index("[MW0601 519차 / 사용자 지시] ALERT 밴드")
    block = dash_src[idx:idx + 4200]
    assert "if _gap_ms >= _MT_ALERT_MS:" in block
    assert "_MT_WARN_MS" not in block.split("self.log_panel.append")[0], (
        "WARN 밴드가 경보 탭 조건에 섞였다"
    )


def test_stall_alert_threshold_unchanged():
    """임계 자체는 바꾸지 않았다 — 재보정은 26주 WFA 항목이다."""
    from config.settings import (
        MAIN_THREAD_STALL_ALERT_MS, MAIN_THREAD_STALL_WARN_MS,
        MAIN_THREAD_STALL_DETECT_MS,
    )
    assert MAIN_THREAD_STALL_ALERT_MS == 15_000
    assert MAIN_THREAD_STALL_WARN_MS == 5_000
    assert MAIN_THREAD_STALL_DETECT_MS == 2_000


def test_stall_alert_has_daily_cap_and_says_when_capped(dash_src):
    """상한이 있고, 상한에 닿았다는 사실을 남긴다(계측 4원칙 ③ 탈락 가시화)."""
    from config.settings import MAIN_THREAD_STALL_ALERT_TAB_DAILY_MAX as CAP
    assert CAP > 0
    assert "_MT_ALERT_TAB_DAILY_MAX" in dash_src
    assert "일일 상한" in dash_src


def test_stall_alert_state_explicitly_initialised(dash_src):
    """`getattr(self, "_x", 기본값)` 으로 런타임 상태를 읽지 않는다(계측 4원칙 ④)."""
    assert 'self._stall_alert_day = ""' in dash_src
    assert "self._stall_alert_count = 0" in dash_src
    assert 'getattr(self, "_stall_alert_day"' not in dash_src
    assert 'getattr(self, "_stall_alert_count"' not in dash_src


def test_stall_alert_never_breaks_the_timer(dash_src):
    """계측이 1초 타이머를 죽이면 안 된다 — 전 구간 try 로 감쌌다."""
    idx = dash_src.index("if _gap_ms >= _MT_ALERT_MS:")
    block = dash_src[idx:idx + 3000]
    assert "try:" in block and "except Exception" in block


def test_stall_alert_does_not_trade(dash_src):
    """경보 블록에 매매 호출이 없다."""
    idx = dash_src.index("if _gap_ms >= _MT_ALERT_MS:")
    block = dash_src[idx:idx + 3000]
    for bad in ("send_market_order", "_execute_entry", "force_exit",
                "_set_pending_order", "close_position"):
        assert bad not in block, "정지 경보가 매매를 호출한다(%s)" % bad


# ═══════════════════════════════════════════════════════════════════════════
# §3. F-1 — 마감 진입 시 잔여 포지션 청산
# ═══════════════════════════════════════════════════════════════════════════

def test_f1_settings_present_and_bounded():
    from config.settings import (
        DAILY_CLOSE_FORCE_EXIT_ENABLED as EN,
        DAILY_CLOSE_FORCE_EXIT_MAX_ATTEMPTS as N,
        DAILY_CLOSE_FORCE_EXIT_TIMEOUT_SEC as T,
        DAILY_CLOSE_FORCE_EXIT_SETTLE_SEC as S,
        MAIN_THREAD_STALL_ALERT_MS as ALERT_MS,
    )
    assert EN is True
    assert 1 <= N <= 5, "시도 상한이 없거나 과하다"
    assert 0 < T, "벽시계 시한이 없다 — 마감이 인질이 된다"
    assert T * 1000 < ALERT_MS, (
        "청산 시한(%.1fs)이 MainStall ALERT(%.1fs) 이상이다 — "
        "안전장치가 자기 때문에 정지 경보를 울린다" % (T, ALERT_MS / 1000.0)
    )
    assert 0 < S < T


def test_f1_wired_into_daily_close(main_src):
    """`daily_close()` 안에서 호출된다 — 함수만 만들어두고 안 부르면 죽은 코드다."""
    start = main_src.index("    def daily_close(self):")
    end = main_src.index("\n    def ", start + 10)
    body = main_src[start:end]
    assert body.count("_ts_daily_close_force_exit(self,") == 2, (
        "미측정 경로와 잔여 경로 **둘 다**에서 불러야 한다"
    )
    assert "DAILY_CLOSE_FORCE_EXIT_ENABLED" in body, "킬스위치를 안 본다"


def test_f1_attempts_even_when_engine_state_unmeasured(main_src):
    """엔진 상태를 못 읽어도 시도한다 — 브로커가 권위 축이다(계측 4원칙 ②·⑤)."""
    start = main_src.index("    def daily_close(self):")
    end = main_src.index("\n    def ", start + 10)
    body = main_src[start:end]
    um = body.index("if not _rp_measured:")
    nxt = body.index("elif _rp_status", um)
    assert "_ts_daily_close_force_exit(self," in body[um:nxt], (
        "미측정 분기가 청산을 시도하지 않는다 — 「못 읽었다」는 「없다」가 아니다"
    )


def test_f1_loop_is_bounded_by_both_attempts_and_clock(main_src):
    start = main_src.index("def _ts_daily_close_force_exit(")
    end = main_src.index("\ndef ", start + 10)
    body = main_src[start:end]
    assert 'while out["attempts"] < max_attempts:' in body, "시도 상한 루프가 아니다"
    assert "time.monotonic() - t0 >= timeout" in body, "벽시계 시한이 없다"
    assert body.count("time.sleep(") >= 1
    # 시한을 넘길 sleep 은 하지 않는다
    assert "time.monotonic() - t0 + settle < timeout" in body


def test_f1_never_raises_out_of_daily_close(main_src):
    """마감을 죽이면 EOD 재학습·P8·세션 저장이 통째로 날아간다."""
    start = main_src.index("def _ts_daily_close_force_exit(")
    end = main_src.index("\ndef ", start + 10)
    body = main_src[start:end]
    assert "raise" not in body, "청산 실패를 예외로 던지면 마감이 멈춘다"

    probe_s = main_src.index("def _ts_broker_residual_qty(")
    probe_e = main_src.index("\ndef ", probe_s + 10)
    probe = main_src[probe_s:probe_e]
    assert "except Exception" in probe, "잔고 TR 예외가 마감을 죽인다"


def test_f1_failure_is_reported_as_failure(main_src):
    """실패를 성공처럼 적지 않는다 — 무엇을 모르는지도 함께 적는다."""
    start = main_src.index("def _ts_daily_close_force_exit(")
    end = main_src.index("\ndef ", start + 10)
    body = main_src[start:end]
    assert "잔여 포지션을 닫지 못했다" in body
    assert "미측정" in body, "「잔량 0」과 「측정 실패」를 같은 문구로 만들면 안 된다"
    assert "직접 정리할 것" in body


def _called_names(main_src, fn_name):
    """`fn_name` 안에서 **실제로 호출되는** 이름 집합 (주석·docstring 제외).

    문자열 검색으로 보면 docstring 이 설명하려고 적어둔 함수명까지 「호출」로
    잡힌다 — 규약을 설명한 문장이 규약 위반으로 판정되면 안 된다
    (`test_514` 의 Slack 검사가 같은 이유로 호출 형태를 본다).
    """
    tree = ast.parse(main_src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == fn_name:
            out = set()
            for n in ast.walk(node):
                if isinstance(n, ast.Call):
                    f = n.func
                    out.add(getattr(f, "id", None) or getattr(f, "attr", None))
            return out
    raise AssertionError("함수를 찾지 못했다: %s" % fn_name)


def test_f1_probe_is_read_only(main_src):
    """프로브는 읽기 전용 — 주문을 내지 않는다."""
    called = _called_names(main_src, "_ts_broker_residual_qty")
    for bad in ("send_market_order", "_send_broker_exit_order",
                "_ts_broker_direct_force_exit", "_set_pending_order"):
        assert bad not in called, "잔량 프로브가 주문을 낸다(%s)" % bad
    assert "request_futures_balance" in called, "잔고를 읽지 않는다"


def test_f1_probe_distinguishes_flat_from_unmeasured(main_src):
    """(0, None, False)와 (0, None, True)를 구분한다 — 계측 4원칙 ②."""
    start = main_src.index("def _ts_broker_residual_qty(")
    end = main_src.index("\ndef ", start + 10)
    body = main_src[start:end]
    assert "return 0, None, False" in body, "미측정 반환이 없다"
    assert "return 0, None, True" in body, "진짜 FLAT 반환이 없다"


def test_f1_probe_parses_same_keys_as_force_exit(main_src):
    """프로브와 청산 함수의 **행 해석 키가 같다** — 드리프트하면 서로 다른 답을 낸다."""
    def keys(fn_name):
        s = main_src.index("def %s(" % fn_name)
        e = main_src.index("\ndef ", s + 10)
        return set(re.findall(r'row\.get\("([^"]+)"\)', main_src[s:e]))
    assert keys("_ts_broker_residual_qty") == keys("_ts_broker_direct_force_exit"), (
        "잔량 파싱 키가 어긋났다 — 「청산했다는데 프로브는 잔량이 있다」가 생긴다"
    )


def test_f1_reuses_existing_exit_path(main_src):
    """새 주문 경로를 만들지 않았다 — 검증된 `_ts_broker_direct_force_exit` 재사용."""
    called = _called_names(main_src, "_ts_daily_close_force_exit")
    assert "_ts_broker_direct_force_exit" in called
    assert "send_market_order" not in called, "주문을 직접 보내면 거부 처리·로그가 갈린다"


def test_f1_no_double_exit_with_external_guard():
    """외부 가드가 주문을 낼 수 있으면 15:39와 15:40이 같은 잔량에 두 번 주문한다."""
    from config.settings import FORCE_FLAT_GUARD_ORDER_ENABLED
    assert FORCE_FLAT_GUARD_ORDER_ENABLED is False, (
        "외부 FLAT 가드의 주문 권한이 켜졌다 — F-1과 함께 재검토해야 한다"
    )


def test_f1_absolute_principle_1_documented(main_src):
    start = main_src.index("def _ts_daily_close_force_exit(")
    end = main_src.index("\ndef ", start + 10)
    assert "절대원칙 §1" in main_src[start:end]


# ═══════════════════════════════════════════════════════════════════════════
# §4. 전체 — 문서와 코드가 어긋나지 않는다
# ═══════════════════════════════════════════════════════════════════════════

def test_claude_md_records_cb2_restoration():
    """CLAUDE.md 가 9999를 현재 상태로 말하고 있으면 다음 세션이 오판한다."""
    md = _read(os.path.join(_ROOT, "CLAUDE.md"))
    assert "CB② 모의투자 한정 예외는 해제됐다" in md
    assert "`CB_CONSEC_STOP_LIMIT = 3`" in md


def test_invariants_reference_updated():
    inv = _read(os.path.join(
        _ROOT, ".claude", "skills", "mireuk-daily-check",
        "references", "invariants.md"))
    assert "| `CB_CONSEC_STOP_LIMIT` | **`3`** |" in inv
