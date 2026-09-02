# -*- coding: utf-8 -*-
"""[MW0601 518차 / 장후 자동조치] F-3 · G-1 · G-4 회귀 고정.

세 항목 모두 **라벨·문구·리포트 축**만 바꾼다. 주문·수량·게이트·청산 트리거는
한 줄도 바뀌지 않으며, 아래 §4가 그 사실을 코드로 고정한다.

- **F-3** `_entry_source` 세션 고착 — `BROKER_SYNC_RECOVERY` 등으로 한 번 바뀌면
  세션이 끝날 때까지 `SYSTEM_AUTO` 로 돌아오지 않아, 그 뒤의 정상 자동진입이
  전부 남의 이름으로 기록됐다(2026-09-02 09:41→10:19 실측).
- **G-1** 재기동 시 브로커 잔량 이상 경보 — 훅은 **이미 있었다**(함정①). 결손은
  문구였다: 첫 단어가 "완료"라 경보 탭에서 성공 통지로 읽혔다.
- **G-4** 이월 포지션 손익이 다이제스트 헤드라인에서 통째로 빠졌다
  (2026-09-02 −5,299,668원이 `귀속 실패 레그 N행` 한 마디로만 남았다).
"""
from __future__ import annotations

import os
import re
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

_COLLECTOR = os.path.join(
    _ROOT, ".claude", "skills", "mireuk-daily-check", "scripts", "collect_evidence.py"
)


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


@pytest.fixture(scope="module")
def main_src():
    return _read(os.path.join(_ROOT, "main.py"))


# ─────────────────────────────────────────────────────────────────────────────
# §1. F-3 — `_entry_source` 가 진입 퍼널에서 SYSTEM_AUTO 로 복귀한다
# ─────────────────────────────────────────────────────────────────────────────

def test_f3_execute_entry_restores_system_auto(main_src):
    """진입 퍼널 `_ts_execute_entry` 안에 SYSTEM_AUTO 복귀 할당이 있다.

    이 할당이 사라지면 2026-09-02 결함(세션 고착)이 그대로 재발한다.
    """
    start = main_src.index("def _ts_execute_entry(")
    end = main_src.index("\ndef ", start + 10)
    body = main_src[start:end]
    assert re.search(r'self\._entry_source\s*=\s*"SYSTEM_AUTO"', body), (
        "_ts_execute_entry() 안에서 _entry_source 를 SYSTEM_AUTO 로 되돌리지 않는다 — "
        "복구 이벤트(BROKER_SYNC_RECOVERY 등) 뒤의 정상 자동진입이 오귀속된다"
    )


def test_f3_assignment_sits_after_all_early_return_gates(main_src):
    """복귀 할당은 **조기 반환 게이트 전부 뒤**, 그리고 **주문 전송 앞**이어야 한다.

    - 게이트보다 앞에 두면: 차단된 진입 시도가 라벨을 되돌려, 그때 들고 있던
      외부/복구 포지션의 청산이 `SYSTEM_AUTO` 로 **오귀속**된다.
    - 주문 전송보다 뒤에 두면: `BlockRequest()` 가 COM 이벤트를 pump 하는 동안
      Chejan 체결 콜백이 먼저 도착하는 경로가 **낡은 라벨**을 읽는다.
    """
    start = main_src.index("def _ts_execute_entry(")
    end = main_src.index("\ndef ", start + 10)
    body = main_src[start:end]

    pos_assign = body.index('self._entry_source = "SYSTEM_AUTO"')
    pos_send = body.index("self._send_broker_entry_order(")
    pos_pending = body.index('self._set_pending_order(')

    # 조기 반환 게이트들 — 전부 할당보다 앞에 있어야 한다.
    for gate in (
        "_server_matched",
        "_account_mismatch_block",
        "_broker_sync_block_new_entries",
        "if cooldown_active:",
        "self._has_pending_order()",
    ):
        assert body.index(gate) < pos_assign, (
            "조기 반환 게이트 %r 가 SYSTEM_AUTO 할당보다 뒤에 있다 — "
            "차단된 시도가 라벨을 되돌려 보유 포지션을 오귀속한다" % gate
        )

    assert pos_assign < pos_pending < pos_send, (
        "SYSTEM_AUTO 할당은 _set_pending_order()·_send_broker_entry_order() 앞이어야 한다 "
        "(Chejan 선행 체결 레이스가 낡은 라벨을 읽는다)"
    )


def test_f3_manual_path_still_overrides_after_call(main_src):
    """수동 진입은 여전히 호출 **뒤에** OPERATOR_MANUAL 로 덮어쓴다.

    F-3 이 퍼널 안에서 SYSTEM_AUTO 를 세우므로, 수동 경로가 그 뒤에 덮어쓰지
    않으면 수동 진입이 시스템 진입으로 둔갑한다.
    """
    call = main_src.index("self._execute_entry(direction, price, qty, atr, grade)")
    tail = main_src[call:call + 400]
    assert 'self._entry_source = "OPERATOR_MANUAL"' in tail, (
        "수동 진입 경로가 _execute_entry() 호출 뒤 OPERATOR_MANUAL 덮어쓰기를 잃었다"
    )


def test_f3_recovery_labels_are_not_removed(main_src):
    """복구·수동 라벨 자체는 그대로 살아 있다 — F-3 은 되돌리기만 추가했다."""
    for label in (
        "BROKER_SYNC_RECOVERY",
        "GHOST_PENDING_MISS",
        "OPERATOR_MANUAL",
        "OPERATOR_RESTORE",
    ):
        assert 'self._entry_source = "%s"' % label in main_src, (
            "%s 라벨 할당이 사라졌다 — F-3 은 라벨을 지우는 수정이 아니다" % label
        )


# ─────────────────────────────────────────────────────────────────────────────
# §2. G-1 — 재기동 시 브로커 잔량 경보가 **읽히는 문구**다
# ─────────────────────────────────────────────────────────────────────────────

def test_g1_startup_sync_emits_actionable_alert(main_src):
    """`[BrokerSync]` 경보가 ERROR 로, 조건부(잔량 있을 때만) 발화한다."""
    assert "[BrokerSync] 🔴 재기동해 보니 계좌에 포지션이 남아 있다" in main_src

    idx = main_src.index("[BrokerSync] 🔴 재기동해 보니")
    head = main_src[idx - 300:idx]
    assert "if before != after and qty > 0:" in head, (
        "경보가 무조건 발화한다 — FLAT 정상 재기동에서도 경보가 떠 경보 탭이 무뎌진다"
    )
    tail = main_src[idx:idx + 700]
    assert '"ERROR"' in tail, "경보 레벨이 ERROR 가 아니다 — 대시보드 「2 경보」 탭 라우팅 조건"


def test_g1_alert_tells_the_reader_what_to_do(main_src):
    """경보는 *무슨 일인지 + 지금 무엇을 할지* 를 담는다(514차 F-C 형식)."""
    idx = main_src.index("[BrokerSync] 🔴 재기동해 보니")
    msg = main_src[idx:idx + 700]
    assert "지금 계좌를 직접 확인할 것" in msg
    assert "미륵이가 이번 세션에 낸 자리가 아니다" in msg


def test_g1_does_not_duplicate_the_existing_hook(main_src):
    """기존 `startup sync 완료` 줄은 **그대로** 살아 있다 — 훅을 갈아치우지 않았다.

    그 줄은 이미 CRITICAL 로 경보 탭까지 이어져 있었다(함정① — 이미 있는 것을
    또 만들지 않는다). G-1 은 그 위에 **읽히는 한 줄**을 더한 것뿐이다.
    """
    assert '[BrokerSync] startup sync 완료: {before} -> {after}' in main_src
    assert main_src.count("[BrokerSync] 🔴 재기동해 보니") == 1, "경보가 중복 배선됐다"


def test_g1_alert_channel_is_still_wired_to_dashboard():
    """SYSTEM 레이어 → 대시보드 경보 탭 배선이 살아 있다(경보의 전제)."""
    main_src_local = _read(os.path.join(_ROOT, "main.py"))
    assert 'log_manager.subscribe(' in main_src_local
    assert 'append_sys_log_tagged' in main_src_local

    dash = _read(os.path.join(_ROOT, "dashboard", "main_dashboard.py"))
    idx = dash.index("def append_sys_log_tagged(")
    body = dash[idx:idx + 600]
    for lvl in ("WARN", "ERROR", "CRITICAL"):
        assert lvl in body, "경보 탭 라우팅에서 %s 가 빠졌다" % lvl


def test_g1_no_slack(main_src):
    """Slack 은 쓰지 않는다 — 사용자 결정(개발단계 직접 모니터링)."""
    idx = main_src.index("[BrokerSync] 🔴 재기동해 보니")
    assert "slack" not in main_src[idx:idx + 700].lower()


# ─────────────────────────────────────────────────────────────────────────────
# §3. G-4 — 이월 포지션 손익이 다이제스트에 드러난다
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def collector_src():
    return _read(_COLLECTOR)


def test_g4_orphan_block_is_rendered(collector_src):
    assert "이월 포지션(전일 이전 진입) 추정" in collector_src
    assert "if orphans:" in collector_src


def test_g4_states_exclusion_and_combined_total(collector_src):
    """세 값을 **전부** 보여준다 — 헤드라인·이월분·합계. 뭉개지 않는다."""
    idx = collector_src.index("이월 포지션(전일 이전 진입) 추정")
    block = collector_src[idx:idx + 2600]
    assert "이 금액은 들어 있지 않다" in block, "헤드라인 미포함 사실을 명시하지 않는다"
    assert "오늘 계좌에서 실제로 오간 돈" in block, "합계 병기가 없다"
    assert "데이터 손실이" in block and "귀속 불가" in block, (
        "「귀속 불가」와 「데이터 손실」을 구분하지 않는다(계측 4원칙 ②)"
    )


def test_g4_points_at_absolute_principle_1(collector_src):
    """이월분 존재는 전일이 FLAT 으로 안 끝났다는 뜻 — 절대원칙 §1 확인을 지시한다."""
    idx = collector_src.index("이월 포지션(전일 이전 진입) 추정")
    assert "15:10 강제청산" in collector_src[idx:idx + 2600]


def test_g4_consistency_line_carries_the_amount(collector_src):
    """정합성 줄이 건수만이 아니라 **금액**을 싣는다 — 경고로만 읽히지 않게."""
    assert "귀속 실패(이월 추정) 레그" in collector_src
    idx = collector_src.index("귀속 실패(이월 추정) 레그")
    assert "헤드라인 합계에 미포함" in collector_src[idx:idx + 400]


def test_g4_headline_total_still_excludes_orphans(collector_src):
    """`tot_won` 정의는 **바뀌지 않았다** — 오늘 엔진 성적이 전일분에 오염되면 안 된다."""
    assert 'tot_won = sum(q["net_won"] for q in closed)' in collector_src


def test_g4_collector_compiles():
    """수집기가 문법적으로 성립한다(py37 대상)."""
    import py_compile
    py_compile.compile(_COLLECTOR, doraise=True)


# ─────────────────────────────────────────────────────────────────────────────
# §4. 「라이브 반영 0」 불변식 — 이 3건은 매매 경로를 바꾸지 않았다
# ─────────────────────────────────────────────────────────────────────────────

def test_invariant_entry_source_is_label_only(main_src):
    """`_entry_source` 는 **DB INSERT 한 곳에서만** 읽힌다.

    조건문·수량·게이트가 이 값을 읽기 시작하면 라벨이 매매 판단으로 승격된 것이다
    — 그 순간 F-3 은 「라벨 수정」이 아니라 매매 정책 변경이 된다.
    """
    reads = [
        ln.strip()
        for ln in main_src.splitlines()
        if "_entry_source" in ln
        and not re.search(r"self\._entry_source\s*=", ln)
        and not ln.strip().startswith("#")
    ]
    # 남는 것은 __init__ 타입선언 1줄 + trades INSERT 의 getattr 1줄뿐이어야 한다.
    assert len(reads) == 2, "예상치 못한 _entry_source 읽기: %r" % (reads,)
    assert any("str" in r and "SYSTEM_AUTO" in r for r in reads), reads
    assert any("getattr(self" in r for r in reads), reads
    for r in reads:
        assert not r.startswith("if "), "라벨이 분기 조건으로 쓰인다: %r" % r


def test_invariant_no_order_or_exit_logic_touched(main_src):
    """진입 퍼널의 게이트·주문 호출 구조가 그대로다 — 추가/삭제 없음."""
    start = main_src.index("def _ts_execute_entry(")
    end = main_src.index("\ndef ", start + 10)
    body = main_src[start:end]

    # 조기 반환 게이트 5종이 전부 살아 있다.
    assert body.count("return") >= 5
    # 주문 전송은 여전히 한 번만 불린다.
    assert body.count("self._send_broker_entry_order(") == 1
    # 이번 수정이 더한 것은 라벨 할당 한 줄뿐이다.
    assert body.count('self._entry_source = "SYSTEM_AUTO"') == 1


def test_invariant_brokersync_alert_does_not_trade(main_src):
    """G-1 경보 블록에 주문·청산 호출이 없다 — 경보만 한다."""
    idx = main_src.index("if before != after and qty > 0:")
    block = main_src[idx:idx + 900]
    for forbidden in (
        "_send_broker_entry_order",
        "send_market_order",
        "_execute_entry",
        "close_position",
        "_set_pending_order",
    ):
        assert forbidden not in block, (
            "G-1 경보 블록이 매매를 호출한다(%s) — 경보 전용이어야 한다" % forbidden
        )
