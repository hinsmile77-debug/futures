# -*- coding: utf-8 -*-
"""[MW0602 547차 후속] 브로커 net 체인 진단의 렌더 경로 회귀 고정.

`scripts/broker_net_chain_audit.py` 의 금액 포매터는 `("%+,.0f" % v)` 였다.
printf 계열에는 `,` 천단위 플래그가 없어 **호출되면 무조건 ValueError** 다.

그런데 이 포매터는 **D1 오염이나 D2 불연속이 있을 때만** 호출된다.
「이상 없음」으로 끝나는 날에는 한 줄도 실행되지 않으므로, 이 진단은
*무언가를 찾아낸 바로 그 순간에만 죽는* 계측이었다 — FP-CRITICAL 죽은 게이트,
TOX 죽은 섀도와 같은 계열이다(CLAUDE.md 계측 4원칙 ④).

실제로 2026-09-07 의 D1 오염(기록 -28,948 vs 장중 -164,948, 136,000원 과소)이
이 크래시에 가려 사람 눈에 닿지 않았다.
"""
import io
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCRIPT = os.path.join(_ROOT, "scripts", "broker_net_chain_audit.py")
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


def _load():
    """스크립트를 모듈로 적재한다 (scripts/ 는 패키지가 아니다)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("_bnca_547", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ── T1. 포매터가 살아 있는가 (원 크래시) ────────────────────────────────────
def test_t1_formatter_does_not_raise_on_float():
    """종전 구현은 여기서 ValueError('unsupported format character') 로 죽었다."""
    f = _load()._fmt_krw
    for v in (-164948.0, 29580521.0, 0.0, -0.4, 1e9):
        assert isinstance(f(v), str)


def test_t2_formatter_output_shape():
    """부호 + 천단위 구분. 2026-09-07 실측값을 그대로 고정한다."""
    f = _load()._fmt_krw
    assert f(-164948.0) == "-164,948"
    assert f(-28948.0) == "-28,948"
    assert f(29580521.0) == "+29,580,521"


def test_t3_none_is_not_zero():
    """미측정을 0 으로 위장하지 않는다 (계측 4원칙 ②)."""
    f = _load()._fmt_krw
    assert f(None) == "-"
    assert f(0.0) != f(None)


# ── T4. 재발 방지 — 잘못된 printf 문법이 되돌아오면 실패한다 ────────────────
def test_t4_no_invalid_printf_thousands_flag_in_source():
    """`"%+,.0f" % v` 형태가 되살아나면 실패한다.

    문자열 검색이 아니라 AST 로 **실제 `%` 포맷 연산**만 본다 — 이 결함을
    설명하는 주석·독스트링이 소스에 남아 있어야 하기 때문이다.
    """
    import ast
    src = io.open(_SCRIPT, encoding="utf-8").read()
    offenders = []
    for node in ast.walk(ast.parse(src)):
        if not (isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod)):
            continue
        left = node.left
        val = getattr(left, "s", None)
        if val is None and isinstance(left, ast.Constant):
            val = left.value if isinstance(left.value, str) else None
        if val and ("%+," in val or "%," in val):
            offenders.append((getattr(node, "lineno", "?"), val))
    assert not offenders, "printf 에 없는 천단위 플래그 재도입: %r" % (offenders,)


# ── T5. 렌더 경로가 실제로 끝까지 도는가 ────────────────────────────────────
def test_t5_render_path_completes_with_findings(monkeypatch, capsys):
    """D1·D2·D3 가 **모두 걸리는** 합성 입력으로 사람이 읽는 경로를 끝까지 태운다.

    원 결함은 이 조건에서만 드러났다(발견이 0건이면 포매터가 호출되지 않는다).
    수치는 2026-09-07 실측을 본떴다 — 기록 -28,948 vs 장중 -164,948.
    """
    mod = _load()

    # rows = [(hhmmss, gross, dep, nxt), ...]
    keep = [("100000", -136000.0, 29416220.0, 29251272.0)]   # nxt-dep = -164,948
    drop = [("220215", -136000.0, 29280000.0, 29251052.0)]   # 장후 정산 롤오버

    monkeypatch.setattr(mod, "_iter_log_days", lambda: iter([("20260907", [])]))
    monkeypatch.setattr(mod, "_parse_day", lambda lines: (keep + drop, 1))
    monkeypatch.setattr(mod, "_split_rollover", lambda rows: (keep, drop))
    monkeypatch.setattr(mod, "_db_rows", lambda: {
        # date: (dep, nxt, broker_net, pnl_krw)
        "2026-09-04": (29247153.0, 29416220.0, 169067.0, 181000.0),
        "2026-09-07": (29251292.0, 29222344.0, -28948.0, -136000.0),
    })
    monkeypatch.setattr(mod, "_traded_dates", lambda: {"2026-09-04", "2026-09-07"})
    monkeypatch.setattr(mod, "_guard_present", lambda: True)
    monkeypatch.setattr(sys, "argv", ["broker_net_chain_audit.py"])

    try:
        rc = mod.main()
    except ValueError as e:                      # 원 결함의 정확한 지문
        pytest.fail("렌더 경로가 죽었다 (원 547차 결함 재발): %s" % e)

    out = capsys.readouterr().out
    assert "Traceback" not in out
    assert rc == 1, "오염·불연속·스킵이 다 있는데 종료코드가 1 이 아니다"

    # 세 진단이 전부 사람이 읽는 형태로 렌더됐는가
    assert "1일 오염" in out
    assert "-164,948" in out and "-28,948" in out
    assert "불연속" in out
    assert "+29,416,220" in out
