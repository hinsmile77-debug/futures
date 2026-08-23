# -*- coding: utf-8 -*-
"""[MW0601 483차 / P1-A] `daily_close()` — 리셋 뒤에 당일 카운터를 읽지 마라.

## 무엇을 잡는가

`daily_close()` 안에서 `self._reset_model_health_counters()` **뒤에** `self._mh_*`
당일 카운터를 읽는 구문. 그 지점의 값은 항상 0이므로 예외 없이 조용히 0을 찍는다.

실제 사고(2026-08-21 이상점 1-9):

    11667  self._reset_model_health_counters()      # 카운터 0으로
    ...
    11718  _cfg_txt = " | ConfFloorGuard 도달가능 %d분 · 도달불가 %d분 · 재지않음 %d분" \
                      % (self._mh_cfg_reachable_min, ...)

15:40 「mc-conf 괴리」 경보의 ConfFloorGuard 3칸이 매일 `0분 · 0분 · 0분` 으로
찍혔다. 482차 G-3이 만든 그 계측은 「진입 기회 부족」 경보가 오탐인지 정탐인지를
가르는 **유일한 판별자**인데, 결함이 예외를 내지 않아 며칠 두면
`_verified_today` 와 같은 **가짜 평선**이 된다(CLAUDE.md 계측 4원칙 ④).

## 왜 `test_457_fallback_visibility.py` 로는 못 잡는가

457차 검사는 "읽히지만 **할당이 없는** 속성"을 본다. 여기 세 속성은 매분 정상적으로
`+= 1` 되고 리셋에서도 할당된다 — 457차 기준으로는 완전무결하다. 죽는 것은 값이
아니라 **읽는 시점**이다. 이 테스트가 그 축(시간 순서)의 일반 검출기다.

## 규약

당일 카운터는 리셋 **전에** `_model_health_snapshot()` 으로 스냅샷을 잡고, 이후
소비자는 그 dict 를 읽는다(`_ccf_today` · `_cb3_avail_eod` 와 같은 관례).
"""
import ast
import io
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

_MAIN = os.path.join(_ROOT, "main.py")

#: (리셋 메서드, 그 리셋이 0으로 되돌리는 속성 접두사)
#: 새 일일 리셋을 만들면 여기에 등록할 것 — 등록해야 이 검사가 지켜준다.
_RESET_PAIRS = [
    ("_reset_model_health_counters", "_mh_"),
]


def _daily_close_node():
    tree = ast.parse(io.open(_MAIN, encoding="utf-8").read())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "daily_close":
            return node
    pytest.fail("main.py 에 daily_close() 가 없다 — 이름이 바뀌었으면 이 검사도 갱신할 것")


def _self_attr(node):
    """`self.X` 형태면 X, 아니면 None."""
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) \
            and node.value.id == "self":
        return node.attr
    return None


@pytest.mark.parametrize("reset_name,prefix", _RESET_PAIRS)
def test_no_counter_read_after_reset(reset_name, prefix):
    fn = _daily_close_node()

    reset_lines = [
        n.lineno for n in ast.walk(fn)
        if isinstance(n, ast.Call) and _self_attr(n.func) == reset_name
    ]
    assert reset_lines, (
        "daily_close() 가 %s() 를 부르지 않는다 — 리셋을 옮겼다면 이 검사도 옮길 것"
        % reset_name)
    reset_line = min(reset_lines)

    late = sorted({
        (n.lineno, n.attr) for n in ast.walk(fn)
        if isinstance(n, ast.Attribute)
        and isinstance(n.ctx, ast.Load)
        and (_self_attr(n) or "").startswith(prefix)
        and n.lineno > reset_line
    })
    assert not late, (
        "daily_close(): %s() (line %d) **뒤에서** 당일 카운터를 읽는다 → 항상 0이다.\n"
        "  %s\n"
        "리셋 전에 `_model_health_snapshot()` 으로 스냅샷을 잡아 그 dict 를 읽을 것 "
        "(CLAUDE.md 계측 4원칙 ④)."
        % (reset_name, reset_line,
           "\n  ".join("line %d: self.%s" % (ln, a) for ln, a in late)))


def test_snapshot_is_taken_before_reset():
    """스냅샷 호출이 리셋보다 **앞**이어야 한다 — 순서가 뒤집히면 위 검사가 무력해진다."""
    fn = _daily_close_node()
    snap = [n.lineno for n in ast.walk(fn)
            if isinstance(n, ast.Call) and _self_attr(n.func) == "_model_health_snapshot"]
    reset = [n.lineno for n in ast.walk(fn)
             if isinstance(n, ast.Call) and _self_attr(n.func) == "_reset_model_health_counters"]
    assert snap, "daily_close() 가 _model_health_snapshot() 을 부르지 않는다"
    assert reset, "daily_close() 가 _reset_model_health_counters() 를 부르지 않는다"
    assert max(snap) < min(reset), (
        "스냅샷(line %s)이 리셋(line %s)보다 뒤다 — 457차 C5 와 같은 죽은 값이 기록된다"
        % (snap, reset))


def test_snapshot_carries_conf_floor_three_states():
    """3상태가 스냅샷 dict 에 실려야 소비자가 리셋과 무관해진다."""
    tree = ast.parse(io.open(_MAIN, encoding="utf-8").read())
    fn = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_model_health_snapshot":
            fn = node
    assert fn is not None, "_model_health_snapshot() 이 없다"

    keys = set()
    for node in ast.walk(fn):
        if isinstance(node, ast.Dict):
            for k in node.keys:
                if isinstance(k, ast.Str):
                    keys.add(k.s)
    for want in ("cfg_reachable_min", "cfg_unreachable_min", "cfg_unmeasured_min"):
        assert want in keys, "스냅샷에 %s 가 없다 — 경보가 리셋된 값을 읽게 된다" % want
    # 482차 G-1 의 CB③ 3키도 같은 자리에 남아 있어야 한다(같은 규약)
    assert "cb3_ready_minutes" in keys


def test_alert_reads_snapshot_not_live_attrs():
    """15:40 경보 문자열이 `self._mh_cfg_*` 대신 스냅샷을 읽는지 — 원 사고 지점."""
    src = io.open(_MAIN, encoding="utf-8").read()
    i = src.find("ConfFloorGuard 도달가능")
    assert i > 0, "경보 문구가 사라졌다 — 문구를 바꿨다면 이 검사도 갱신할 것"
    block = src[i:i + 500]
    assert "self._mh_cfg_" not in block, \
        "경보가 리셋된 라이브 속성을 직접 읽는다 (매일 0분 · 0분 · 0분)"
    assert "cfg_reachable_min" in block, "경보가 스냅샷 키를 읽지 않는다"


def test_snapshot_keys_are_log_only_no_db_column():
    """DB 스키마를 늘리지 않는다 — `scaler_daily` 컬럼 증설은 회귀 위험이 크다."""
    src = io.open(os.path.join(_ROOT, "model", "scaler_monitor_db.py"),
                  encoding="utf-8").read()
    for k in ("cfg_reachable_min", "cfg_unreachable_min", "cfg_unmeasured_min"):
        assert k not in src, (
            "%s 가 scaler_monitor_db 로 새어 들어갔다 — P1-A 는 로그 전용이다" % k)
