# -*- coding: utf-8 -*-
"""[MW0601 554차] 테스트가 운영 포지션 상태파일을 오염시키지 못한다 + 복원 가드.

2026-09-10 사고 (재발 시 이 파일이 먼저 깨진다)
------------------------------------------------
08:02:01, `tests/test_493_exit_stage_all_builders.py:_opened()` 가
`PositionTracker.open_position(price=1040.0, quantity=2, atr=1.5)` 를 부르면서
`_save_state()` 로 **운영** `data/position_state.json` 을 덮어썼다.

  · 08:40:41 기동 → `[Position] 이전 포지션 복원: LONG 2계약 @ 1040.0 (손절=1037.75)`
  · 08:45:21 프리장 첫 틱 `1109.60` → tp1(1041.50) 을 69pt 초과 → TP1·TP2 연속 발동
  · **실제 매도 2계약 체결**, 허구 이익 `+6,921,594원` 기록. 계좌 실보유는 없었다.

저장값이 테스트 파라미터와 정확히 일치한 것이 출처를 특정했다 —
`stop=1040−1.5×1.5=1037.75`, `tp1=1040+1.5×1.0=1041.50`.

방어는 **세 겹**이고 이 파일이 셋 다 고정한다:
  ① `tests/conftest.py` autouse fixture — `_STATE_FILE` 을 tmp 로 격리
  ② `_save_state()` — 테스트 모드인데 목적지가 운영 경로면 저장 생략
  ③ `load_state(reference_price=…)` — 참조가 대비 괴리 초과면 복원 거부

실행:
    conda run -n py37_32 python -m pytest tests/test_554_position_state_isolation.py -v
"""
import datetime
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# `python tests/test_554_...py` 직접 실행 대비 2줄 (conftest 관례, 422차)
from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

import pytest  # noqa: E402

import strategy.position.position_tracker as PT  # noqa: E402
from config.constants import POSITION_LONG  # noqa: E402
from config.settings import POSITION_RESTORE_MAX_DEVIATION_PCT  # noqa: E402

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MAIN_SRC = io.open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()

# 사고 당시의 실제 값 — 숫자를 그대로 박아둔다(재현이 곧 회귀 검사다).
_ACCIDENT_ENTRY = 1040.0
_ACCIDENT_TICK = 1109.60


def _tracker():
    return PT.PositionTracker(pt_value=50_000)


def _opened_like_the_accident():
    """사고를 일으킨 그 호출 그대로."""
    pt = _tracker()
    pt.open_position(direction=POSITION_LONG, price=_ACCIDENT_ENTRY, quantity=2,
                     atr=1.5, grade="A", regime="NEUTRAL")
    return pt


# ── ① conftest 격리 ────────────────────────────────────────────────────────
def test_conftest_isolates_state_file():
    """pytest 실행 중에는 `_STATE_FILE` 이 운영 경로가 아니다."""
    assert PT._STATE_FILE != PT._PROD_STATE_FILE, (
        "conftest 의 `_isolate_position_state` fixture 가 걷혔다 — "
        "이 상태로 `open_position()` 을 부르는 테스트가 하나라도 있으면 "
        "2026-09-10 사고가 그대로 재현된다")


def test_open_position_does_not_touch_production_file():
    """🔴 핵심 불변식 — 사고를 낸 그 호출이 운영 파일을 건드리지 않는다."""
    prod = PT._PROD_STATE_FILE
    before = os.path.getmtime(prod) if os.path.exists(prod) else None
    _opened_like_the_accident()
    after = os.path.getmtime(prod) if os.path.exists(prod) else None
    assert before == after, (
        "운영 상태파일이 변경됐다(%s → %s) — 격리가 뚫렸다" % (before, after))


# ── ② _save_state 프로덕션 가드 ────────────────────────────────────────────
def test_save_state_refuses_production_path_in_test_mode(monkeypatch, tmp_path):
    """conftest 가 없는 경로(직접 실행 등)에서도 운영 파일에는 못 쓴다."""
    sentinel = tmp_path / "prod_like.json"
    # `_STATE_FILE` 과 `_PROD_STATE_FILE` 을 같게 만들어 "운영 경로" 상황을 재현한다.
    monkeypatch.setattr(PT, "_STATE_FILE", str(sentinel), raising=False)
    monkeypatch.setattr(PT, "_PROD_STATE_FILE", str(sentinel), raising=False)
    monkeypatch.setattr(PT, "_TEST_SAVE_BLOCK_LOGGED", False, raising=False)
    _opened_like_the_accident()
    assert not sentinel.exists(), "테스트 모드인데 운영 경로에 저장됐다"


def test_isolated_path_still_saves_and_restores(monkeypatch, tmp_path):
    """격리된 경로에서는 저장/복원 왕복이 **정상 동작해야** 한다.

    가드가 "테스트면 무조건 저장 안 함"이었다면 왕복 검증 테스트들이 조용히
    공허해진다(통과하지만 아무것도 재지 않는다).
    """
    path = tmp_path / "position_state.json"
    monkeypatch.setattr(PT, "_STATE_FILE", str(path), raising=False)
    _opened_like_the_accident()
    assert path.exists(), "격리 경로 저장까지 막혔다 — 왕복 검증이 불가능해진다"

    restored = _tracker()
    assert restored.load_state(reference_price=_ACCIDENT_ENTRY) is True
    assert restored.entry_price == pytest.approx(_ACCIDENT_ENTRY)
    assert restored.quantity == 2


# ── ③ 복원 가드 ────────────────────────────────────────────────────────────
def _write_state(path, entry_price, saved_at=None):
    pt = _tracker()
    pt.open_position(direction=POSITION_LONG, price=entry_price, quantity=2,
                     atr=1.5, grade="A", regime="NEUTRAL")
    state = json.loads(io.open(str(path), encoding="utf-8").read())
    if saved_at:
        state["saved_at"] = saved_at
    io.open(str(path), "w", encoding="utf-8").write(
        json.dumps(state, ensure_ascii=False))
    return state


def test_restore_rejected_when_entry_price_is_far_from_reference(monkeypatch, tmp_path):
    """🔴 2026-09-10 재현 — 저장 1040.0 vs 실제 1109.60(6.6%) 이면 복원하지 않는다."""
    path = tmp_path / "position_state.json"
    monkeypatch.setattr(PT, "_STATE_FILE", str(path), raising=False)
    _write_state(path, _ACCIDENT_ENTRY)

    pt = _tracker()
    assert pt.load_state(reference_price=_ACCIDENT_TICK) is False, (
        "6.6%% 괴리를 통과시켰다 — 한도 %.1f%%" % POSITION_RESTORE_MAX_DEVIATION_PCT)
    assert pt.status == "FLAT"
    assert not path.exists(), "거부했는데 원본이 남아 있다 — 다음 재기동이 또 복원한다"
    rejected = [p for p in os.listdir(str(tmp_path)) if ".rejected_" in p]
    assert rejected, "증거 파일(.rejected_*)이 없다 — 사후 분석 원본이 사라진다"


def test_restore_allowed_within_threshold(monkeypatch, tmp_path):
    """정상 갭(한도 이내)은 복원한다 — 가드가 진짜 포지션을 버리면 안 된다."""
    path = tmp_path / "position_state.json"
    monkeypatch.setattr(PT, "_STATE_FILE", str(path), raising=False)
    _write_state(path, 1100.0)
    ref = 1100.0 * (1 + (POSITION_RESTORE_MAX_DEVIATION_PCT - 1.0) / 100.0)

    pt = _tracker()
    assert pt.load_state(reference_price=ref) is True
    assert pt.quantity == 2


def test_missing_reference_skips_check_but_is_not_silent(monkeypatch, tmp_path, caplog):
    """참조가가 없으면 **검사하지 않는다** — 단 「미측정」임을 남긴다(계측 4원칙 ②)."""
    path = tmp_path / "position_state.json"
    monkeypatch.setattr(PT, "_STATE_FILE", str(path), raising=False)
    _write_state(path, _ACCIDENT_ENTRY)

    pt = _tracker()
    with caplog.at_level("WARNING", logger="TRADE"):
        assert pt.load_state(reference_price=None) is True
    assert any("PositionRestoreGuard" in r.getMessage() and "미측정" in r.getMessage()
               for r in caplog.records), (
        "참조가 없이 복원했는데 아무 흔적도 남지 않았다 — "
        "「괴리 없음」과 「재지 못함」이 구분되지 않는다")


def test_corrupt_zero_entry_price_is_rejected(monkeypatch, tmp_path):
    """진입가 0 은 참조가 유무와 무관하게 거부한다(0 나눗셈 이전에 손상 신호다)."""
    path = tmp_path / "position_state.json"
    monkeypatch.setattr(PT, "_STATE_FILE", str(path), raising=False)
    _write_state(path, _ACCIDENT_ENTRY)
    state = json.loads(io.open(str(path), encoding="utf-8").read())
    state["entry_price"] = 0.0
    io.open(str(path), "w", encoding="utf-8").write(json.dumps(state, ensure_ascii=False))

    assert _tracker().load_state(reference_price=None) is False


def test_yesterday_state_is_still_ignored(monkeypatch, tmp_path):
    """기존 방어(당일 저장분만 복원)를 554차 변경이 깨뜨리지 않았는가."""
    path = tmp_path / "position_state.json"
    monkeypatch.setattr(PT, "_STATE_FILE", str(path), raising=False)
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat()
    _write_state(path, 1100.0, saved_at=yesterday)
    assert _tracker().load_state(reference_price=1100.0) is False


# ── main.py 배선 ───────────────────────────────────────────────────────────
def _func_body(name):
    """`def name(` 부터 다음 메서드 정의 전까지 — 들여쓰기 기반 거친 절단으로 충분하다."""
    start = _MAIN_SRC.index("def %s(" % name)
    nxt = _MAIN_SRC.find("\n    def ", start + 1)
    return _MAIN_SRC[start:nxt if nxt > 0 else len(_MAIN_SRC)]


def test_restore_guard_is_wired_into_startup():
    """복원 호출부가 참조가를 **실제로 넘기는가** — 안 넘기면 가드가 죽는다."""
    assert "load_state(reference_price=_startup_reference_price())" in _MAIN_SRC, (
        "기동 복원이 참조가 없이 `load_state()` 를 부른다 — 괴리 검사가 상시 스킵된다")


def test_unreconciled_exit_warns_but_never_blocks():
    """🔴 미대조 청산은 **경보만** 한다 — 막으면 절대원칙 §1(15:10 강제청산)이 깨진다."""
    body = _func_body("_send_broker_exit_order")
    assert "UnreconciledExit" in body, "미대조 청산 경보가 배선되지 않았다"

    # 경보 `if` 블록만 잘라낸다 — 뒤따르는 511차 백오프(`return EXIT_RET_THROTTLED`)는
    # 기존 동작이라 여기 섞이면 안 된다.
    lines = body.split("\n")
    head = next(i for i, ln in enumerate(lines)
                if "if not self._broker_position_reconciled" in ln)
    indent = len(lines[head]) - len(lines[head].lstrip())
    end = len(lines)
    for i in range(head + 1, len(lines)):
        stripped = lines[i].strip()
        if stripped and (len(lines[i]) - len(lines[i].lstrip())) <= indent:
            end = i
            break
    guard_block = "\n".join(lines[head:end])
    assert "return" not in guard_block, (
        "미대조 경보 블록이 조기 반환한다 — 모의서버는 상시 blank 라 "
        "손절·15:10 강제청산이 **상시** 막힌다(480차: 안전장치가 새 사고를 만든다)")


def test_reconciled_flag_is_a_separate_axis():
    """`_broker_position_reconciled` 는 `_broker_sync_verified` 와 별개 축이어야 한다."""
    assert "self._broker_position_reconciled: bool = False" in _MAIN_SRC, (
        "명시 초기화가 없다 — `getattr(self, ..., False)` 폴백으로 읽히면 "
        "계측 4원칙 ④ 위반이고 test_457_fallback_visibility 가 잡는다")
    assert "position NOT reconciled with broker" in _MAIN_SRC, (
        "모의 blank-rows 경로가 여전히 「검증됨」으로만 기록된다 — "
        "2026-09-10 에 `verified=True` 한 줄이 유령 포지션을 정상으로 보이게 했다")
