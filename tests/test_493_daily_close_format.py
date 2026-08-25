# -*- coding: utf-8 -*-
"""[MW0601 493차 후속5 / F-Y] `daily_close()` 계측 로그가 **실제로 렌더링되는가**.

왜 필요한가 (실제 사고, 2026-08-24·25 이틀 연속)
------------------------------------------------
`daily_close()`의 `[CB③계측]` 줄이 `%+,.0f` 를 써서 렌더링 시점에
`ValueError: unsupported format character ','` 로 죽었고, **그 예외가 마감 절차
전체를 끊었다.** 뒤에 있던 DB 플러시·WAL 체크포인트·일일 전략 리포트가 이틀
연속 실행되지 않았다.

🔴 **기존 테스트(`tests/test_490_cb3_would_halt.py`)는 이것을 못 잡았다.**
그 테스트는 카운터 누산(`_mh_cb3_would_halt_*` 값이 맞는가)만 검사하고
**그 값으로 문자열을 만들어 보지는 않았다.** 값은 옳았고 출력이 죽은 것이다.

그래서 이 파일은 **렌더링 자체**를 고정한다. `main.py` 전체를 import 하면 COM·Qt가
따라오므로, 소스에서 그 로그 표현식만 뽑아 **같은 값으로 실제 평가**한다.
표현식을 소스에서 뽑기 때문에, 누가 그 줄을 다시 `%+,.0f` 로 되돌리면 여기서 깨진다.

같이 고정하는 것:
· 그 블록이 **개별 try/except 로 감싸여** 있어 마감 절차를 끊지 않는다.
· 그러면서 **예외를 삼키지 않는다**(로그로 남긴다 — 계측 4원칙 ④).
· 손익 확정·마커 기록에는 그 관례를 **적용하지 않았다**(조용히 실패하면 안 된다).
"""
import ast
import io
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN_PY = os.path.join(ROOT, "main.py")

#: 2026-08-25 실측 스냅샷(이 점검이 DEBUG 로그에서 복원한 값) + 음수/큰 값 경계.
_SNAPSHOTS = [
    {"cb3_would_halt_minutes": 69, "cb3_ready_minutes": 74, "pipeline_minutes": 370,
     "cb3_would_halt_entries": 0, "cb3_would_halt_pnl_krw": 0.0},
    {"cb3_would_halt_minutes": 0, "cb3_ready_minutes": 0, "pipeline_minutes": 0,
     "cb3_would_halt_entries": 0, "cb3_would_halt_pnl_krw": 0.0},
    {"cb3_would_halt_minutes": 120, "cb3_ready_minutes": 300, "pipeline_minutes": 370,
     "cb3_would_halt_entries": 3, "cb3_would_halt_pnl_krw": -1234567.89},
    {"cb3_would_halt_minutes": 5, "cb3_ready_minutes": 9, "pipeline_minutes": 370,
     "cb3_would_halt_entries": 1, "cb3_would_halt_pnl_krw": 9876543.21},
]


def _main_src():
    return io.open(MAIN_PY, encoding="utf-8").read()


def _str_value(n):
    """문자열 리터럴 노드의 값. py3.7(`ast.Str`)과 py3.8+(`ast.Constant`) 양쪽 지원.

    🔴 **이 호환이 없으면 검사기가 공허하게 통과한다.** 런타임은 py3.7 32-bit
    (Cybos COM 요구사항)이고 그쪽은 `ast.Constant`가 아니라 `ast.Str`를 쓴다.
    `ast.Constant`만 보면 문자열을 하나도 못 찾아 "위반 0건"이 되는데,
    그것은 통과가 아니라 **검사를 안 한 것**이다(개발 중 실제로 밟았다).
    """
    if isinstance(n, ast.Str):                      # py3.7
        return n.s
    if isinstance(n, ast.Constant) and isinstance(n.value, str):   # py3.8+
        return n.value
    return None


def _find_cb3_log_call(tree):
    """`[CB③계측]` 문자열을 좌변에 가진 `%` 표현식 노드를 찾는다."""
    for node in ast.walk(tree):
        if not (isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod)):
            continue
        parts = []

        def walk(n):
            v = _str_value(n)
            if v is not None:
                parts.append(v)
            elif isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add):
                walk(n.left)
                walk(n.right)

        walk(node.left)
        if "[CB③계측]" in "".join(parts):
            return node, "".join(parts)
    return None, None


def test_cb3_log_line_exists():
    """그 줄이 사라지지 않았는지 — F-AB가 DB 저장을 붙여도 로그는 유지한다."""
    node, fmt = _find_cb3_log_call(ast.parse(_main_src()))
    assert node is not None, (
        "[CB③계측] 로그 줄이 없다. F-Y는 로그를 없애는 fix가 아니다 — "
        "로그는 사람이 읽고 DB(F-AB)는 시계열이 읽는다")
    assert "%s원" in fmt, "손익은 미리 문자열로 만들어 %s로 넘겨야 한다"


@pytest.mark.parametrize("snap", _SNAPSHOTS)
def test_cb3_log_line_renders_without_error(snap):
    """🔴 핵심 — 그 서식 문자열이 실제 값으로 **렌더링된다.**

    종전 `%+,.0f` 였다면 여기서 ValueError로 죽는다.
    """
    _, fmt = _find_cb3_log_call(ast.parse(_main_src()))
    assert fmt is not None
    pnl_txt = format(float(snap.get("cb3_would_halt_pnl_krw") or 0.0), "+,.0f")
    rendered = fmt % (
        int(snap.get("cb3_would_halt_minutes") or 0),
        int(snap.get("cb3_ready_minutes") or 0),
        int(snap.get("pipeline_minutes") or 0),
        int(snap.get("cb3_would_halt_entries") or 0),
        pnl_txt,
        0.28,
    )
    assert "[CB③계측]" in rendered
    assert pnl_txt in rendered, "천단위 구분이 살아 있어야 한다(읽는 사람을 위해)"


def test_cb3_block_is_guarded_but_does_not_swallow():
    """그 블록이 try/except 안에 있고, except가 **로그를 남기는지**.

    감싸기만 하고 `except: pass` 로 두면 계측이 조용히 사라진다 — 이 저장소가
    반복해서 당한 실패(죽은 게이트·죽은 섀도)와 같은 형태가 된다.
    """
    src = _main_src()
    idx = src.index("[CB③계측] 조건성립")
    window = src[max(0, idx - 1200): idx + 1200]
    assert "try:" in window, "[CB③계측] 블록이 try로 감싸여 있지 않다"
    assert re.search(r"except\s+Exception\s+as\s+\w+:", window), \
        "except 절이 예외를 바인딩하지 않는다"
    assert "[CB③계측] 출력 실패" in window, \
        "except가 예외를 삼킨다 — logger.warning으로 남길 것(계측 4원칙 ④)"


def test_pnl_confirmation_blocks_are_not_silently_guarded():
    """🚫 손익 확정·마커 기록에는 「무해」 관례를 적용하지 않았는가.

    F-Y 변경 ③은 "아직 감싸이지 않은 **로그·계측** 블록"을 대상으로 한다.
    `[Daily] 마감 통계`가 조용히 실패하면 그날 손익이 통째로 사라진다.
    """
    src = _main_src()
    idx = src.index("[Daily] 마감 통계")
    window = src[max(0, idx - 400): idx + 400]
    assert "무해" not in window, (
        "손익 확정 블록에 '무해' 예외 처리가 붙었다 — 그 블록은 조용히 실패하면 안 된다")
