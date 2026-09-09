# -*- coding: utf-8 -*-
"""[MW0601 552-11] 진입 출처가 **세션 재시작을 넘어서** 살아 있는가.

사건
----
2026-08-28 15:20:36 에 **외부(수동) 주문**이 체결됐다 — TRADE 로그는 같은 초에
`[체결동기화] 외부진입 SHORT` 를 3번 찍었고, 주문번호 3639 는 14:31:12 에
`상태=접수` 로 들어왔으며 엔진의 `[주문요청]` 이 **없다**(엔진 자기 주문인 TP1 4025
에는 있다). `main.py` 는 그 체결에 `GHOST_PENDING_MISS` 를 정상 태깅했다.

그런데 **15:29:55 에 세션이 재시작**됐고(`[Position] 이전 포지션 복원: SHORT 4계약`),
15:30 청산 3레그가 `trades.entry_source='SYSTEM_AUTO'` 로 기록됐다.

    `_entry_source` 는 프로세스 인스턴스 상태
    `trades` 행은 **청산 시점**에 기록
    ⇒ 진입과 청산 사이에 세션이 바뀌면 `__init__` 기본값이 그대로 남는다

**포지션은 복원되는데 그것을 해석할 출처는 복원되지 않았다.**
552-10(브로커 net 기준점이 재시작으로 소실)과 정확히 같은 계열이다.

크기: 3레그 / 1포지션 / net **+656,935원**. 하필 **낙관** 방향이고,
545/546차 「판정 손익을 시스템 자동매매 한정으로」 축에 외부진입 손익이 섞인다.

⚠ 518차 F-3 은 **반대 방향**(비-AUTO 라벨 고착 → 정상 자동진입이
`BROKER_SYNC_RECOVERY` 로 기록)만 고쳤다. 이 방향은 남아 있었다.
"""
from __future__ import print_function

import datetime
import io
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _tracker(monkeypatch):
    """격리된 상태파일을 쓰는 PositionTracker."""
    import strategy.position.position_tracker as PT
    tmp = tempfile.mkdtemp()
    monkeypatch.setattr(PT, "_STATE_FILE", os.path.join(tmp, "position_state.json"),
                        raising=False)
    return PT


# ── ① 포지션 속성으로서의 entry_source ──────────────────────────────────────
def test_entry_source_defaults_to_none_not_system_auto(monkeypatch):
    """초기값은 None(미측정)이다 — `"SYSTEM_AUTO"` 로 채우면 위장이 된다(계측 4원칙 ②)."""
    PT = _tracker(monkeypatch)
    p = PT.PositionTracker(pt_value=50000)
    assert p.entry_source is None


def test_entry_source_survives_save_and_load(monkeypatch):
    """저장 → (재시작) → 복원에서 출처가 살아남는다."""
    PT = _tracker(monkeypatch)
    p = PT.PositionTracker(pt_value=50000)
    p.apply_entry_fill(direction="SHORT", price=1071.92, quantity=4, atr=3.0,
                       grade="MANUAL", regime="NEUTRAL")
    p.entry_source = "GHOST_PENDING_MISS"
    p._save_state()

    q = PT.PositionTracker(pt_value=50000)          # 새 프로세스
    assert q.load_state() is True
    assert q.entry_source == "GHOST_PENDING_MISS", (
        "재시작이 진입 출처를 지웠다 — 2026-08-28 오귀속 경로")


def test_missing_key_in_old_state_file_is_none(monkeypatch):
    """구버전 상태파일(키 없음)은 None 이다 — `"SYSTEM_AUTO"` 로 추정하지 않는다."""
    PT = _tracker(monkeypatch)
    p = PT.PositionTracker(pt_value=50000)
    p.apply_entry_fill(direction="LONG", price=1000.0, quantity=1, atr=3.0,
                       grade="A", regime="NEUTRAL")
    p.entry_source = "OPERATOR_MANUAL"
    p._save_state()
    with io.open(PT._STATE_FILE, encoding="utf-8") as f:
        st = json.load(f)
    st.pop("entry_source")
    with io.open(PT._STATE_FILE, "w", encoding="utf-8") as f:
        f.write(json.dumps(st, ensure_ascii=False))

    q = PT.PositionTracker(pt_value=50000)
    assert q.load_state() is True
    assert q.entry_source is None


def test_entry_source_resets_on_flat(monkeypatch):
    """포지션이 닫히면 출처도 리셋된다 — 다음 포지션에 새지 않는다."""
    PT = _tracker(monkeypatch)
    p = PT.PositionTracker(pt_value=50000)
    p.apply_entry_fill(direction="LONG", price=1000.0, quantity=1, atr=3.0,
                       grade="A", regime="NEUTRAL")
    p.entry_source = "GHOST_PENDING_MISS"
    p.close_position(exit_price=1001.0, reason="TP1(전량)")
    assert p.status == PT.POSITION_FLAT
    assert p.entry_source is None, "이전 포지션의 출처가 남았다"


# ── ② main 쪽 배선 (소스 고정) ───────────────────────────────────────────────
def _main_src():
    return io.open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()


def test_setter_mirrors_into_position():
    """`_entry_source` setter 가 포지션에 미러링하는지 소스로 고정한다.

    할당 7곳을 하나하나 고치는 대신 setter 한 곳으로 모은 이유는, 한 곳이라도
    빠뜨리면 **그 경로만 조용히 옛 동작**으로 남기 때문이다.
    """
    src = _main_src()
    assert "@_entry_source.setter" in src, "setter 미러링이 사라졌다"
    assert "self.position.entry_source = value" in src
    assert '_entry_source_val = "SYSTEM_AUTO"' in src, (
        "클래스 기본값이 없으면 읽기가 AttributeError 로 깨질 수 있다")


def test_init_inherits_restored_source():
    """`__init__` 이 복원된 포지션의 출처를 승계하는지 고정한다.

    🔴 순서가 급소다 — `load_state()` 는 `__init__` 앞쪽(재시작 복원 블록)에서
    끝나고 `_entry_source` 초기화는 그보다 **뒤**에 있다. 그 자리에서 무조건
    `"SYSTEM_AUTO"` 를 넣으면 방금 복원한 출처를 덮어쓴다 — 그것이 오귀속의
    마지막 한 걸음이었다.
    """
    src = _main_src()
    assert "_restored_src = self.position.entry_source" in src
    assert 'self._entry_source = _restored_src or "SYSTEM_AUTO"' in src
    assert "[EntrySource]" in src, "승계 사실을 로그로 남겨야 한다(계측 4원칙 ④)"
    # 순서 불변식: 복원 블록이 승계보다 앞에 있어야 한다
    assert src.index("if self.position.load_state():") < src.index("_restored_src ="), (
        "load_state() 가 출처 승계보다 뒤에 있으면 승계가 항상 None 이 된다")


def test_no_getattr_fallback_on_read():
    """읽기부의 `getattr(..., "SYSTEM_AUTO")` 폴백이 없어야 한다(계측 4원칙 ④)."""
    src = _main_src()
    assert 'getattr(self, "_entry_source", "SYSTEM_AUTO")' not in src
    assert "_entry_src_this_leg = self._entry_source" in src


def test_detector_query_shape():
    """오귀속 검출기의 정의를 고정한다 — 자동진입 불가 구간의 SYSTEM_AUTO.

    이 검출기가 2026-08-28 3레그를 유일하게 집어냈다. 정의가 바뀌면 다음 세션이
    같은 사건을 못 찾는다.
    """
    from config.settings import FORCE_EXIT_TIME
    hh, mm = str(FORCE_EXIT_TIME).split(":")[:2]
    assert (int(hh), int(mm)) == (15, 10), (
        "강제청산 시각이 바뀌었다 — 검출기 경계(15:10)를 함께 갱신할 것")
