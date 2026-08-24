# -*- coding: utf-8 -*-
"""[MW0601 490차 / F-N] 마감 마커는 둘이다 — `started`(시작) · `done`(완료).

## 무엇을 고정하는가

2026-08-24 15:40:20, 마감 스레드가 Qt 위젯 접근 데드락으로 영구 정지했다
(이상점 1-12). `data/daily_close_done_*.txt` 는 마감 절차의 **거의 마지막**에
기록되므로 영영 오지 않았고, `retrain_eod.py:_wait_for_daily_close()` 는
**20분을 통째로 헛기다린 뒤** 강제 진행했다(16:00:13, 이상점 1-15).

고치는 방법이 하나 있고 그것이 함정이다 — **`done` 마커를 앞으로 옮기면 뜻이
뒤집힌다.** 그 마커는 "마감이 끝났다"이고 EOD 는 그것을 pkl 경합 회피의 근거로
쓴다. 그래서 마커를 **둘로 나눴다**(계측 4원칙 ②·④ — 상태를 값 하나로 뭉개지
않는다):

    started : `_run_daily_close()` 진입 직후  — "절차가 시작됐다"
    done    : `daily_close()` 끝 (위치 무변경) — "절차가 끝났다"

`started` 만 있고 `done` 이 없으면 = 중간에 죽었다.

이 테스트는 다음 세션이 "마커를 앞으로 옮기면 되잖아"로 되돌리는 것을 막는다.
"""
import ast
import io
import os
import re
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

_MAIN = os.path.join(_ROOT, "main.py")
_EOD = os.path.join(_ROOT, "retrain_eod.py")


def _read(p):
    return io.open(p, encoding="utf-8").read()


def _segment(src, node):
    """함수 본문 소스 조각. `ast.get_source_segment` 은 3.8+ 라 여기서 못 쓴다
    (이 저장소 런타임은 py37_32 — CLAUDE.md 운영환경). 자손 노드의 최대 줄번호로
    끝을 잡는다."""
    lines = src.splitlines()
    last = node.lineno
    for sub in ast.walk(node):
        last = max(last, getattr(sub, "lineno", last) or last)
    return chr(10).join(lines[node.lineno - 1:last])


def test_started_마커가_run_daily_close_진입부에_있다():
    """스레드 본문 **앞쪽**이어야 의미가 있다 — 뒤로 밀리면 죽은 마감을 못 가른다."""
    src = _read(_MAIN)
    tree = ast.parse(src)
    target = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_run_daily_close":
            target = node
    assert target is not None, "main.py 에 _run_daily_close() 가 없다 — 이름이 바뀌었으면 이 검사도 갱신할 것"

    seg = _segment(src, target)
    assert "daily_close_started_" in seg, (
        "_run_daily_close() 가 started 마커를 쓰지 않는다 (490차 F-N 회귀)"
    )
    # `self.daily_close()` 호출보다 **먼저** 기록해야 한다.
    i_marker = seg.index("daily_close_started_")
    i_call = seg.index("self.daily_close()")
    assert i_marker < i_call, (
        "started 마커가 daily_close() 호출 뒤에 있다 — 마감이 죽으면 기록되지 않는다"
    )


def test_done_마커는_daily_close_끝에_그대로_있다():
    """`done` 은 '완료'의 뜻이다. 앞으로 옮기면 EOD 의 pkl 경합 회피 근거가 거짓이 된다."""
    src = _read(_MAIN)
    tree = ast.parse(src)
    dc = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "daily_close":
            dc = node
    assert dc is not None
    seg = _segment(src, dc)
    assert "daily_close_done_" in seg, "daily_close() 에서 done 마커가 사라졌다"
    # 함수 후반부(뒤쪽 25%)에 있어야 한다 — 이 검사가 "앞으로 옮기기"를 막는다.
    pos = seg.index("daily_close_done_") / float(len(seg))
    assert pos > 0.75, (
        "done 마커가 daily_close() 앞쪽(%.0f%% 지점)으로 옮겨졌다 — "
        "그 마커의 뜻은 '완료'다. 일찍 알리려면 started 마커를 쓸 것" % (pos * 100)
    )


def test_EOD가_정체를_조기_판정한다():
    src = _read(_EOD)
    assert "daily_close_started_" in src, (
        "retrain_eod.py 가 started 마커를 보지 않는다 — 20분 헛대기가 그대로 남는다"
    )
    assert "_system_log_age_sec" in src, "SYSTEM.log 정체 신호를 보지 않는다"
    # 단일 신호 판정 금지 — 두 신호가 **함께** 성립해야 조기 탈출한다.
    assert re.search(r"_has_started\s+and\s+_log_age is not None\s+and\s+_log_age >=", src), (
        "정체 판정이 두 신호(started 마커 · SYSTEM.log 나이)의 AND 가 아니다. "
        "단일 신호면 느린 마감을 죽은 것으로 오판하거나 미기동일을 정체로 센다"
    )


def test_마커에_stalled_3상태가_남는다():
    """true/false/unmeasured — 480차 F-4 가 세운 폴백 가시화 규약의 연장."""
    src = _read(_EOD)
    assert "daily_close_stalled:" in src, "완료 마커에 stalled 키가 없다"
    assert "unmeasured" in src, (
        "stalled 가 2상태(true/false)뿐이다 — '못 쟀다'가 '정상'으로 뭉개진다 "
        "(계측 4원칙 ②)"
    )
    assert src.count("_dc_note") >= 3, "완료/실패 마커 양쪽 기록을 확인할 수 없다"


def test_wait_함수가_두_값을_돌려준다():
    """반환을 bool 하나로 되돌리면 stalled 정보가 사라진다."""
    tree = ast.parse(_read(_EOD))
    fn = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_wait_for_daily_close":
            fn = node
    assert fn is not None
    returns = [n for n in ast.walk(fn) if isinstance(n, ast.Return)]
    assert returns, "_wait_for_daily_close() 에 return 이 없다"
    for r in returns:
        assert isinstance(r.value, ast.Tuple) and len(r.value.elts) == 2, (
            "_wait_for_daily_close() 가 (ok, stalled) 2-튜플이 아닌 값을 돌려준다 "
            "(490차 F-N 회귀)"
        )
