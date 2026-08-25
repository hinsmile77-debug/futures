# -*- coding: utf-8 -*-
"""[MW0601 493차 후속5 / F-V] 유령 하드스톱 가드를 진입 경로 전부에서 켠다.

왜 필요한가 (실제 손실, 2026-08-25 11:25:01)
--------------------------------------------
진입 1036.00 / 손절 1033.75 인 LONG 2계약이 **진입 1초 만에** 청산됐다.
청산 근거가 된 값은 **직전 봉(11:24)의 저가 1033.48** 이다 — 그 봉은 포지션이
열리기 **전에** 형성됐다. 즉 존재하지도 않던 포지션의 손절선을 과거 봉에 소급
적용한 「유령 하드스톱」이다. 실현손실 **-24,108원**.

423차가 이미 이 설계 의도를 명시했다(`position_tracker.py` `_recalculate_levels`
주석: *"진입 분봉의 고저가는 진입 이전 구간을 포함하므로, 그 봉의 봉중 판정 역시
유령이다"*). 그래서 `open_position()`은 `_mark_stop_tightened("entry")`로 가드를
켠다. 그런데 **Chejan 선행 체결 레이스**로 `apply_entry_fill()`이 FLAT에서 직접
포지션을 여는 경로에는 **그 한 줄이 없었다.** 새 정책이 아니라 누락의 복원이다.

**왜 3주간 무증상이었나** — 가드는 `stop_updated_at is None`이면 **조용히 통과**하고
그 사실이 어디에도 남지 않았다(계측 4원칙 ④). 그래서 ③(우회 경고)을 함께 넣는다.

이 파일이 고정하는 불변식:
① 진입 3경로 전부가 `_mark_stop_tightened`를 호출한다 (AST 정적 검사 — 새 경로가
   생기면 깨져서 갱신을 강제한다).
② `apply_entry_fill()` FLAT 분기 실행 후 `stop_updated_at is not None`.
③ 2026-08-25 11:25 케이스 재현 — 수정 전 청산 / 수정 후 미청산.
④ **다음 봉의 진짜 손절은 여전히 잡는다** (가드가 손절을 없애는 것이 아니다).
⑤ 가드가 꺼진 채 판정이 나가면 `[PhantomStopGuard]` 경고가 뜬다.
"""
import ast
import datetime
import io
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.constants import POSITION_FLAT, POSITION_LONG  # noqa: E402
from strategy.position.position_tracker import PositionTracker  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PT_SRC = os.path.join(ROOT, "strategy", "position", "position_tracker.py")

# 2026-08-25 11:25:01 실측 상수 (logs/20260825_TRADE.log)
ENTRY_PX = 1036.00
STOP_PX = 1033.75
PREV_BAR_LOW = 1033.48          # 11:24 봉 저가 — 진입 **이전**에 형성됐다
ENTRY_TIME = datetime.datetime(2026, 8, 25, 11, 25, 1)
PREV_BAR_START = datetime.datetime(2026, 8, 25, 11, 24, 0)
NEXT_BAR_START = datetime.datetime(2026, 8, 25, 11, 26, 0)
# ATR — 진입가 - ATR*1.5 = 1033.75 가 되도록 역산(ATR_STOP_MULT=1.5 기준)
ATR = (ENTRY_PX - STOP_PX) / 1.5


def _fresh_tracker(tmp_path=None):
    """새 트래커. 상태 파일을 스크래치로 돌려 라이브 `data/position_state.json`을
    건드리지 않는다(테스트가 운영 상태를 덮으면 안 된다)."""
    pt = PositionTracker(pt_value=50_000)
    return pt


def _open_via_fill(pt, pin_time=True):
    """레이스 경로 — `[Position] 진입` 없이 체결만으로 FLAT에서 여는 경로.

    ⚠ `pin_time` — `_mark_stop_tightened()`는 `filled_at`이 아니라 **벽시계
    `now_kst()`** 를 찍는다. 라이브에서는 체결 직후 호출이라 둘이 사실상 같지만,
    과거 시각을 재현하는 테스트에서는 `stop_updated_at`이 「지금」이 되어 **모든**
    과거 봉에 대해 가드가 걸린다(그러면 ④ 진짜 손절 테스트가 거짓 통과한다).
    그래서 시나리오 테스트는 진입 시각으로 정규화한다.
    ※ 정규화 대상은 **테스트의 시계**이지 프로덕션 동작이 아니다.
    """
    assert pt.status == POSITION_FLAT
    pt.apply_entry_fill(
        direction=POSITION_LONG, price=ENTRY_PX, quantity=2,
        atr=ATR, filled_at=ENTRY_TIME, grade="A", regime="NEUTRAL",
    )
    if pin_time and pt.stop_updated_at is not None:
        pt.stop_updated_at = ENTRY_TIME
    return pt


# ── ① 진입 3경로 전부에 가드가 있는가 (정적 불변식) ─────────────────────────
def _str_value(n):
    """py3.7(`ast.Str`) / py3.8+(`ast.Constant`) 양쪽 지원.

    런타임은 py3.7 32-bit(Cybos COM)다. `ast.Constant`만 보면 문자열을 하나도
    못 찾아 검사가 **공허하게 통과**한다.
    """
    if isinstance(n, ast.Str):
        return n.s
    if isinstance(n, ast.Constant) and isinstance(n.value, str):
        return n.value
    return None


def _funcs_calling_mark_stop_tightened():
    """`_mark_stop_tightened(...)`를 호출하는 함수명 → 인자 문자열 집합."""
    tree = ast.parse(io.open(PT_SRC, encoding="utf-8").read())
    out = {}
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef,)):
            continue
        for node in ast.walk(fn):
            if not isinstance(node, ast.Call):
                continue
            f = node.func
            name = getattr(f, "attr", None) or getattr(f, "id", None)
            if name != "_mark_stop_tightened":
                continue
            arg = _str_value(node.args[0]) if node.args else None
            out.setdefault(fn.name, set()).add(arg)
    return out


def test_all_entry_paths_mark_stop_tightened():
    """진입 경로가 늘어나면 이 테스트가 깨져 갱신을 강제한다.

    474차 `test_473_core_group_reachability.py` · 457차 `test_457_fallback_visibility.py`
    와 같은 관례. **한 경로만 고치면 같은 누락이 남는다**(424차가 3/4 지점만 덮어
    재발한 전례).
    """
    calls = _funcs_calling_mark_stop_tightened()
    assert "open_position" in calls and "entry" in calls["open_position"], (
        "`open_position` 경로의 가드('entry')가 사라졌다 — 423차 설계 의도")
    assert "apply_entry_fill" in calls, (
        "🔴 `apply_entry_fill`에 `_mark_stop_tightened` 호출이 없다 — "
        "레이스 경로가 다시 유령 하드스톱에 노출된다(2026-08-25 -24,108원)")
    paths = calls["apply_entry_fill"]
    assert "entry_fill" in paths, "FLAT 분기(F-V ①)의 가드가 없다"
    assert "entry_fill_correction" in paths, "낙관적 오픈 보정 분기(F-V ①-a)의 가드가 없다"


# ── ② FLAT 분기가 실제로 가드를 켜는가 ──────────────────────────────────────
def test_apply_entry_fill_sets_stop_updated_at():
    # 시각 정규화 없이 **실제 호출 결과**를 본다.
    pt = _open_via_fill(_fresh_tracker(), pin_time=False)
    assert pt.status == POSITION_LONG
    assert pt.stop_updated_at is not None, (
        "레이스 경로 진입 후 stop_updated_at이 None이다 — 가드가 꺼진 채로 열렸다")


def test_optimistic_correction_branch_sets_stop_updated_at():
    """낙관적 오픈 → 체결보정 분기(①-a)도 가드를 켜는가."""
    pt = _fresh_tracker()
    pt.open_position(direction=POSITION_LONG, price=ENTRY_PX, quantity=2,
                     atr=ATR, grade="A", regime="NEUTRAL")
    pt._optimistic = True              # 투기적 오픈 상태 재현(Chejan 보정 대기)
    pt.stop_updated_at = None          # 가드를 일부러 비우고 보정 분기를 태운다
    pt.apply_entry_fill(direction=POSITION_LONG, price=ENTRY_PX + 0.02, quantity=2,
                        atr=ATR, filled_at=ENTRY_TIME)
    assert pt.stop_updated_at is not None, "체결보정 분기에서 가드가 켜지지 않았다"


# ── ③ 2026-08-25 재현 ───────────────────────────────────────────────────────
def test_ghost_hardstop_no_longer_fires_on_prior_bar():
    """🔴 핵심 재현 — 진입 **이전** 봉의 저가로는 청산되지 않아야 한다."""
    pt = _open_via_fill(_fresh_tracker())
    assert pt.stop_price == pytest.approx(STOP_PX, abs=0.01)
    assert PREV_BAR_LOW <= pt.stop_price, "전제: 그 저가는 손절선을 뚫는다"

    hit = pt.is_stop_hit_intrabar(bar_low=PREV_BAR_LOW, bar_high=ENTRY_PX + 1.0,
                                  bar_start=PREV_BAR_START)
    assert hit is False, (
        "진입 이전 봉(11:24)의 저가로 손절이 났다 — 2026-08-25 -24,108원 재발")


def test_guard_off_would_have_fired():
    """가드가 없었다면 청산됐다 — 재현 테스트가 **공허하지 않음**을 보인다."""
    pt = _open_via_fill(_fresh_tracker())
    pt.stop_updated_at = None          # 수정 전 상태 재현
    hit = pt.is_stop_hit_intrabar(bar_low=PREV_BAR_LOW, bar_high=ENTRY_PX + 1.0,
                                  bar_start=PREV_BAR_START)
    assert hit is True, "가드를 꺼도 안 터지면 이 재현 테스트는 아무것도 검증하지 않는다"


# ── ④ 진짜 손절은 여전히 잡는가 ─────────────────────────────────────────────
def test_real_stop_on_next_bar_still_fires():
    """가드는 손절을 **없애는** 것이 아니라 **한 봉 미루는** 것이다.

    다음 봉부터는 정상 판정된다(423차 독스트링이 명시). 이것이 깨지면
    F-V는 안전장치를 없앤 것이 된다.
    """
    pt = _open_via_fill(_fresh_tracker())
    hit = pt.is_stop_hit_intrabar(bar_low=PREV_BAR_LOW, bar_high=ENTRY_PX + 1.0,
                                  bar_start=NEXT_BAR_START)
    assert hit is True, "진입 이후 봉의 진짜 손절을 놓쳤다 — 안전장치가 사라졌다"


def test_close_based_stop_is_untouched():
    """종가 기준 `is_stop_hit()`은 가드와 무관하게 그대로 살아 있다."""
    pt = _open_via_fill(_fresh_tracker())
    assert pt.is_stop_hit(STOP_PX - 0.01) is True
    assert pt.is_stop_hit(ENTRY_PX) is False


# ── ⑤ 우회 가시화 + 섀도 ────────────────────────────────────────────────────
def test_bypass_emits_warning_once(monkeypatch):
    """가드가 꺼진 채 판정이 나가면 경고가 뜬다 — 무증상 3주의 재발 방지.

    ⚠ `caplog` 를 쓰지 않는다. `TRADE` 로거는 다른 테스트(`test_log_isolation`)가
    핸들러·propagate 를 재구성하므로, 단독 실행은 통과하고 **전체 실행에서만
    깨진다**(개발 중 실제로 밟았다). 모듈 로거를 직접 가로채면 로깅 설정과
    무관하게 「경고가 실제로 나갔는가」만 본다.
    """
    import strategy.position.position_tracker as PT

    calls = []
    monkeypatch.setattr(PT.logger, "warning",
                        lambda msg, *a, **k: calls.append(msg % a if a else msg))

    pt = _open_via_fill(_fresh_tracker())
    pt.stop_updated_at = None
    for _ in range(2):
        pt.is_stop_hit_intrabar(bar_low=PREV_BAR_LOW, bar_high=ENTRY_PX + 1.0,
                                bar_start=PREV_BAR_START)
    hits = [m for m in calls if "[PhantomStopGuard]" in str(m)]
    assert len(hits) == 1, "포지션당 1회만 경고해야 한다(로그 폭주 방지), 실제 %d회" % len(hits)
    assert pt._last_intrabar_guard_bypassed is True


def test_add_on_fill_is_deliberately_out_of_scope():
    """🚫 추가진입(증량) 분기에는 가드를 붙이지 않았다 — 명세 범위 밖이다.

    증량도 `_recalculate_levels()` 로 손절선이 움직이므로 같은 논리가 성립하지만,
    0825 리포트가 위험을 저울질한 범위는 **FLAT 분기**다. 손익이 걸린 경로를
    분석 없이 넓히지 않는다(NEXT_TODO U-15로 등록).

    이 테스트는 「그 결정이 유지되고 있는가」를 고정한다 — 나중에 넓히기로
    **결정**하면 이 테스트를 함께 갱신하면 된다(조용히 넓히는 것만 막는다).
    """
    pt = _open_via_fill(_fresh_tracker())
    pt.stop_updated_at = None                  # 증량 직전 상태를 비워둔다
    pt.apply_entry_fill(direction=POSITION_LONG, price=ENTRY_PX + 0.5, quantity=1,
                        atr=ATR, filled_at=ENTRY_TIME)
    assert pt.quantity == 3, "증량이 반영되지 않았다 — 전제가 틀렸다"
    assert pt.stop_updated_at is None, (
        "증량 분기가 가드를 켰다 — 명세 범위(FLAT 분기)를 넘는 확대다. "
        "의도한 변경이면 이 테스트와 NEXT_TODO U-15를 함께 갱신할 것")


def test_entry_after_bar_shadow_is_recorded_but_not_enforced():
    """② 섀도 — 표시는 하되 **라이브 판정에는 관여하지 않는다.**"""
    pt = _open_via_fill(_fresh_tracker())
    pt.stop_updated_at = None                     # ①가드를 비활성화해 ②만 관찰
    hit = pt.is_stop_hit_intrabar(bar_low=PREV_BAR_LOW, bar_high=ENTRY_PX + 1.0,
                                  bar_start=PREV_BAR_START)
    assert pt._last_intrabar_entry_after_bar is True, "진입이 봉보다 뒤인 것을 못 봤다"
    assert hit is True, "섀도가 라이브 판정을 바꿨다 — 승격은 별도 판단 사항이다"


def test_shadow_is_none_when_unmeasurable():
    """`bar_start`가 없으면 섀도는 **None(미측정)** 이다 — False가 아니다.

    계측 4원칙 ②: "측정하지 않았다"와 "측정했더니 아니다"를 같은 값으로 쓰지 않는다.
    """
    pt = _open_via_fill(_fresh_tracker())
    pt.is_stop_hit_intrabar(bar_low=PREV_BAR_LOW, bar_high=ENTRY_PX + 1.0)
    assert pt._last_intrabar_entry_after_bar is None
