# -*- coding: utf-8 -*-
"""[MW0601 493차 후속5 / F-Y] `%` 서식 문자열 안의 콤마 플래그 금지 — 정적 불변식.

왜 필요한가 (실제 사고, 2026-08-24·25 이틀 연속)
------------------------------------------------
`main.py:daily_close()`의 계측 로그 한 줄이 이렇게 쓰여 있었다:

    "... · 손익 %+,.0f원" % (..., float(pnl), ...)

`,`(천단위 구분) 은 **`str.format`/f-string 문법이지 `%` 연산자 문법이 아니다.**
파이썬은 이것을 `ValueError: unsupported format character ','` 로 거절하고,
그 예외가 `daily_close()` **전체를 끊었다** — 뒤에 있던

  · `[DBQueue] EOD 플러시`   (버퍼된 기록을 파일로 밀어넣기)
  · `[WAL] 체크포인트`        (DB 정돈)
  · 일일 전략 리포트 생성

가 **이틀 연속 실행되지 않았다.** 조건이 맞아야 나는 문제가 아니라 **매일 반드시**
나는 문제였다(그 로그 줄은 마감 때마다 무조건 렌더링된다).

**기존 테스트가 왜 못 잡았나** — `tests/test_490_cb3_would_halt.py`는 카운터 누산만
검사하고 **그 문자열을 실제로 렌더링하지 않았다.** 값이 맞는지만 보고 「출력되는가」는
보지 않은 것이다. 그래서 이 파일은 두 방향으로 막는다:

  ① 이 파일 — **정적 불변식**: 저장소 전체에서 `%` 서식 + 콤마 조합을 금지한다.
  ② `tests/test_493_daily_close_format.py` — **렌더링**: 그 줄을 실제로 찍어 본다.

f-string과 `.format()`은 콤마가 정상 문법이므로 **건드리지 않는다** — 이 검사는
`<문자열> % <값>` 형태(`ast.BinOp` / `ast.Mod`)만 본다.
"""
import ast
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: `%` 변환지정자에 콤마 플래그가 붙은 형태. `%+,.0f` · `%,d` 등.
#: `%%` (리터럴 퍼센트) 나 f-string 의 `{x:+,.0f}` 는 걸리지 않는다.
_PCT_COMMA = re.compile(r"%[-+ #0]*,[0-9.]*[diouxXeEfFgGrs]")

#: 검사 대상 — 라이브 경로와 그 계측. 테스트·문서는 제외한다.
_SCAN_DIRS = ("", "utils", "config", "model", "learning", "scripts",
              "dashboard", "strategy", "features", "collection", "backtest")


def _iter_py_files():
    for rel in _SCAN_DIRS:
        base = os.path.join(ROOT, rel) if rel else ROOT
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames
                           if d not in (".git", "__pycache__", "tests", "docs",
                                        "data", "logs", "model_backup", ".venv")]
            for name in filenames:
                if name.endswith(".py"):
                    yield os.path.join(dirpath, name)
            if not rel:
                break          # 루트는 재귀하지 않는다(하위는 _SCAN_DIRS가 담당)


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


def _literal_of(node):
    """`%` 좌변이 문자열 리터럴(또는 인접/`+` 연결)이면 합쳐서 돌려준다."""
    parts = []

    def walk(n):
        v = _str_value(n)
        if v is not None:
            parts.append(v)
        elif isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add):
            walk(n.left)
            walk(n.right)

    walk(node)
    return "".join(parts)


def _scan_source(src):
    """소스 문자열에서 위반 (lineno, 지정자) 목록. 파일 스캐너와 같은 경로를 쓴다."""
    out = []
    for node in ast.walk(ast.parse(src)):
        if not (isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod)):
            continue
        text = _literal_of(node.left)
        m = _PCT_COMMA.search(text) if text else None
        if m:
            out.append((node.lineno, m.group(0)))
    return out


def test_no_comma_flag_in_percent_format():
    """`"... %+,.0f" % x` 형태가 저장소에 존재하면 실패한다.

    실패하면 그 줄은 **호출되는 순간 ValueError로 죽는다.** 계측 로그에서 이런 일이
    나면 그 로그만 사라지는 것이 아니라, 예외 경계가 없는 한 **호출한 함수가 통째로
    끊긴다**(daily_close가 실제로 그렇게 죽었다).

    고치는 법: 값을 먼저 문자열로 만들고 `%s`로 넘긴다 —
        `txt = format(v, "+,.0f")` 또는 `txt = f"{v:+,.0f}"`  →  `"... %s원" % txt`
    """
    offenders = []
    for path in _iter_py_files():
        try:
            src = io.open(path, encoding="utf-8").read()
            ast.parse(src)      # 파싱 불가 파일은 아래 except로 걸러진다
        except (IOError, OSError, SyntaxError, UnicodeDecodeError):
            continue
        for lineno, spec in _scan_source(src):
            offenders.append("%s:%d  %s"
                             % (os.path.relpath(path, ROOT), lineno, spec))
    assert not offenders, (
        "`%%` 서식 문자열에 콤마 플래그가 있다 — 호출 시 ValueError로 죽는다.\n"
        "값을 먼저 문자열로 만들고 %%s 로 넘길 것:\n  " + "\n  ".join(offenders))


def test_the_regex_actually_catches_the_2026_08_24_bug():
    """검사기 자신의 회귀 — 실제 사고 문자열을 잡는지 확인한다.

    이 테스트가 없으면 정규식이 망가져도 위 테스트가 **공허하게 통과**한다.
    """
    broken = " · 그 창 진입 %d포지션 · 손익 %+,.0f원"
    assert _PCT_COMMA.search(broken), "실제 사고 문자열을 못 잡으면 검사기가 죽은 것이다"
    # 고친 형태와 f-string·format 은 걸리지 않아야 한다(오탐 0).
    assert not _PCT_COMMA.search(" · 손익 %s원")
    assert not _PCT_COMMA.search("{v:+,.0f}")
    assert not _PCT_COMMA.search("진행률 100%% 완료")


def test_percent_operator_would_have_raised():
    """`%` 연산자가 콤마를 정말로 거절하는지 — 전제 자체를 고정한다."""
    import pytest
    with pytest.raises(ValueError):
        _ = "손익 %+,.0f원" % (1234.0,)
    # 고친 형태는 정상이다.
    assert "손익 %s원" % format(1234.0, "+,.0f") == "손익 +1,234원"


def test_scanner_is_not_vacuously_passing():
    """🔴 검사기가 **실제로 문자열을 찾고 있는지** — 공허한 통과 방지.

    py3.7은 문자열 리터럴을 `ast.Str`로, py3.8+는 `ast.Constant`로 만든다.
    한쪽만 처리하면 스캐너가 아무것도 못 찾아 "위반 0건"이 되는데, 그것은
    통과가 아니라 검사를 안 한 것이다. 개발 중 실제로 이 상태였다.

    두 방향으로 확인한다:
      ① 합성 소스의 위반을 잡는가 (검출력)
      ② 실제 저장소에서 `%` 서식을 **하나라도** 파싱했는가 (스캔이 돌긴 했는가)
    """
    bad = 'x = "손익 %+,.0f원" % (v,)'
    assert _scan_source(bad), "합성 위반을 못 잡는다 — 스캐너가 죽었다"

    good = 'x = "손익 %s원" % (txt,)'
    assert not _scan_source(good), "정상 형태를 위반으로 잡는다 — 오탐"

    # 저장소에서 `%` 서식 문자열을 실제로 몇 개나 봤는가.
    seen = 0
    for path in _iter_py_files():
        try:
            tree = ast.parse(io.open(path, encoding="utf-8").read())
        except Exception:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
                if _literal_of(node.left):
                    seen += 1
    assert seen > 50, (
        "저장소에서 %% 서식 문자열을 %d개밖에 못 봤다 — 리터럴 추출이 깨졌을 가능성. "
        "위 '위반 0건'을 믿지 말 것" % seen)
