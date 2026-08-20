# -*- coding: utf-8 -*-
"""[MW0601 482차 / F-4] 점검 수집기 포지션 조립기 — 계측 4원칙 ① 회귀 방지.

## 무엇을 잡는가

`collect_evidence.py` §5가 **레그(청산 행)** 를 **포지션** 으로 조립하지 못하고
`[Position] 체결청산` 만 세던 회귀. 2026-08-20 실측 사고:

    수집기 §5 종전 : 청산 4건 · 승 1 (25%) · -230,004원
    DB 포지션 단위 : 4포지션 2승 2패(50.0%) · -348,018원
    차이 -118,014원 = 은닉된 부분청산 레그(손절1차 조기축소 2 + TP1 부분청산 1)

당일 순손실의 33.9%가 다이제스트에서 사라졌고 승률은 절반으로 찍혔다. 그 다이제스트로
점검 리포트를 쓰면 손익을 34% 과소, 승률을 25%p 과소 보고한다.

417차가 사이징 통계 4종을 무효화한 것과 **같은 오류를 점검 도구가 반복**한 건이라,
등식 하나를 테스트로 고정해 다시 조용히 깨지지 않게 한다:

    Σ레그 원 = Σ포지션 net · `[청산 완료]` 건수 = 조립된 포지션 건수
"""
import io
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_COLLECTOR = os.path.join(
    _ROOT, ".claude", "skills", "mireuk-daily-check", "scripts", "collect_evidence.py")


def _load():
    """수집기를 모듈로 적재. 패키지가 아니라 경로가 밑줄로 시작해 import 가 안 된다."""
    if not os.path.exists(_COLLECTOR):
        pytest.skip("수집기 스크립트 없음: %s" % _COLLECTOR)
    src = io.open(_COLLECTOR, encoding="utf-8").read()
    ns = {"__name__": "_collect_evidence_under_test", "__file__": _COLLECTOR}
    exec(compile(src, _COLLECTOR, "exec"), ns)
    return ns


# 2026-08-20 실거래 로그 원문(logs/20260820_TRADE.log)에서 그대로 따온 표본.
_LOG_2026_08_20 = u"""\
2026-08-20 10:55:00 [INFO] TRADE: [Position] 진입 LONG 3계약 @ 1085.54 | 손절=1082.83 1차=1086.44(×0.50) 2차=1088.25 horizon=3m hurst=neutral
2026-08-20 10:55:17 [INFO] TRADE: [Position] 체결부분청산 1계약 @ 1084.22 | 잔여=2계약 | PnL=-1.20pt (-61,628원) | 손절1차 조기축소
2026-08-20 10:55:17 [INFO] TRADE: [Position] 체결부분청산 1계약 @ 1084.24 | 잔여=1계약 | PnL=-1.18pt (-60,628원) | 손절1차 조기축소
2026-08-20 10:55:17 [INFO] TRADE: [손절1차 조기축소] 2계약 @ 1084.23 PnL=-1.19pt (-122,256원) 잔여=1계약
2026-08-20 10:56:05 [INFO] TRADE: [Position] 체결청산 LONG @ 1082.5 | PnL=-2.92pt (-147,628원) | 하드스톱(틱)
2026-08-20 10:56:05 [INFO] TRADE: [청산 완료] PnL=-2.92pt (-147,628원)
2026-08-20 13:20:00 [INFO] TRADE: [Position] 진입 LONG 2계약 @ 1088.98 | 손절=1087.18 1차=1089.34(×0.30) 2차=1090.78 horizon=1m hurst=neutral
2026-08-20 13:20:30 [INFO] TRADE: [Position] 체결부분청산 1계약 @ 1088.18 | 잔여=1계약 | PnL=-0.87pt (-45,134원) | 손절1차 조기축소
2026-08-20 13:20:30 [INFO] TRADE: [손절1차 조기축소] 1계약 @ 1088.18 PnL=-0.87pt (-45,134원) 잔여=1계약
2026-08-20 13:22:51 [INFO] TRADE: [Position] 체결청산 LONG @ 1087.04 | PnL=-2.01pt (-102,134원) | 하드스톱(틱)
2026-08-20 13:22:51 [INFO] TRADE: [청산 완료] PnL=-2.01pt (-102,134원)
2026-08-20 13:41:01 [INFO] TRADE: [Position] 진입 LONG 2계약 @ 1082.64 | 손절=1080.16 1차=1083.47(×0.60) 2차=1085.12 horizon=3m hurst=trend
2026-08-20 13:43:04 [INFO] TRADE: [Position] 체결부분청산 1계약 @ 1083.72 | 잔여=1계약 | PnL=+1.02pt (+49,376원) | TP1 부분청산 33%
2026-08-20 13:43:04 [INFO] TRADE: [TP1 부분청산] 1계약 @ 1083.72 PnL=+1.02pt (+49,376원) 잔여=1계약
2026-08-20 13:43:58 [INFO] TRADE: [Position] 체결청산 LONG @ 1082.68 | PnL=-0.02pt (-2,624원) | 하드스톱(틱)
2026-08-20 13:43:58 [INFO] TRADE: [청산 완료] PnL=-0.02pt (-2,624원)
2026-08-20 13:57:01 [INFO] TRADE: [Position] 진입 LONG 1계약 @ 1078.52 | 손절=1075.94 1차=1079.38(×0.60) 2차=1081.10 horizon=3m hurst=trend
2026-08-20 14:01:35 [INFO] TRADE: [Position] 체결청산 LONG @ 1078.92 | PnL=+0.48pt (+22,382원) | 하드스톱(틱)
2026-08-20 14:01:35 [INFO] TRADE: [청산 완료] PnL=+0.48pt (+22,382원)
"""

#: 포지션 단위 정답 — `data/db/trades.db` 실측과 일치(482차 리포트 §1 1-2 표).
_EXPECTED = [
    {"open": "10:55", "qty": 3, "hz": "3m", "legs": 3, "net": -269884, "pt": -5.30},
    {"open": "13:20", "qty": 2, "hz": "1m", "legs": 2, "net": -147268, "pt": -2.88},
    {"open": "13:41", "qty": 2, "hz": "3m", "legs": 2, "net": +46752,  "pt": +1.00},
    {"open": "13:57", "qty": 1, "hz": "3m", "legs": 1, "net": +22382,  "pt": +0.48},
]


def _merged_from_log(ns):
    """수집기와 같은 정규식으로 로그를 훑어 `merged` 구조를 만든다."""
    import re
    pats = {k: re.compile(v) for k, v in ns["DEFAULT_CONFIG"]["day_summary_patterns"].items()}
    merged = {}
    for line in _LOG_2026_08_20.splitlines():
        for key, rx in pats.items():
            m = rx.search(line)
            if m:
                d = dict(m.groupdict())
                d["hhmm"] = line[11:16]
                d["_raw"] = line
                merged.setdefault(key, []).append(d)
    return merged


def test_positions_match_db_position_units():
    """레그가 아니라 포지션으로 조립되고, 각 포지션 합이 DB 실측과 같아야 한다."""
    ns = _load()
    merged = _merged_from_log(ns)
    positions, orphans = ns["assemble_positions"](merged)

    assert orphans == [], "귀속 실패 레그가 있으면 안 된다: %r" % orphans
    assert len(positions) == 4, "포지션 4건이어야 한다(레그 8행이 아니라)"
    for got, want in zip(positions, _EXPECTED):
        assert got["open_hhmm"] == want["open"]
        assert got["entry_qty"] == want["qty"]
        assert got["hz"] == want["hz"]
        assert len(got["legs"]) == want["legs"]
        assert got["net_won"] == want["net"], "포지션 %s net 불일치" % want["open"]
        assert abs(got["net_pt"] - want["pt"]) < 1e-9, "포지션 %s pt 불일치" % want["open"]
        assert got["closed"] is True


def test_win_rate_is_position_based_not_leg_based():
    """승률 50%(포지션) — 레그로 세면 25%가 나오는 그 사고를 고정한다."""
    ns = _load()
    positions, _ = ns["assemble_positions"](_merged_from_log(ns))
    wins = sum(1 for q in positions if q["net_won"] > 0)
    assert wins == 2, "포지션 단위 승 2건(레그 단위로 세면 1건이 된다)"
    assert sum(q["net_won"] for q in positions) == -348018


def test_integrity_identity_legs_equal_positions():
    """정합성 등식 — Σ레그 원 = Σ포지션 net, `[청산 완료]` 수 = 포지션 수."""
    ns = _load()
    merged = _merged_from_log(ns)
    positions, _ = ns["assemble_positions"](merged)
    leg_sum = (sum(ns["_won"](e) for e in merged.get("exit", []))
               + sum(ns["_won"](e) for e in merged.get("partial_exit", [])))
    assert leg_sum == sum(q["net_won"] for q in positions)
    assert len(merged.get("pos_done", [])) == sum(1 for q in positions if q["closed"])


def test_summary_lines_are_not_double_counted():
    """요약 라인(`[TP1 부분청산]`·`[손절1차 조기축소]`)을 레그로 세면 이중계상이다.

    10:55:17 실측 — 체결 -61,628 + -60,628 = 요약 -122,256. 둘 다 세면 두 배가 된다.
    """
    ns = _load()
    merged = _merged_from_log(ns)
    # 요약 라인은 어떤 패턴에도 잡히지 않아야 한다.
    for key in ("exit", "partial_exit"):
        for rec in merged.get(key, []):
            raw = rec["_raw"]
            assert "[TP1 부분청산]" not in raw, raw
            assert "[손절1차 조기축소]" not in raw, raw
    assert len(merged.get("partial_exit", [])) == 4   # 체결 단위 4건
    assert len(merged.get("exit", [])) == 4


def test_branch_scoped_invariants_are_excluded_here_and_listed():
    """[F-2] v9-dev 에 없는 `dev` 전용 상수는 표에서 빠지고 목록으로 남아야 한다."""
    ns = _load()
    cfg = ns["load_config"](_ROOT)
    spath, rows, oos = ns["check_invariants"](_ROOT, cfg)
    assert spath is not None
    names = set(r["name"] for r in rows)
    branch = ns["current_branch"](_ROOT)
    for inv in cfg["invariants"]:
        scope = inv.get("branches")
        if scope and branch and branch not in scope:
            assert inv["name"] not in names, "%s 는 표에서 빠져야 한다" % inv["name"]
            assert any(o["name"] == inv["name"] for o in oos), \
                "%s 는 제외 목록에 이름이 남아야 한다(계측 4원칙 ③)" % inv["name"]
    # 스코프 지정이 없는 항목은 종전대로 전부 표에 있어야 한다(MW0602 무영향 보장)
    for inv in cfg["invariants"]:
        if not inv.get("branches"):
            assert inv["name"] in names
