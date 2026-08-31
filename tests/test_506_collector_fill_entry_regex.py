# -*- coding: utf-8 -*-
"""[MW0601 507차 후속 / F-8] 수집기 진입 정규식 — 두 형식 · 보정 배제 · 출처 칸.

**이 사고의 지문을 회귀로 박는다.**

2026-08-31 점검리포트 헤드라인이 「포지션 0건 · 진입 0건」으로 나갔다. 그날 계좌에서는
36건이 체결됐고 20포지션이 만들어졌다 사라졌다. 수집기가 `[체결진입]` 한 형식만 잡는
정규식을 쓰는데, 실제 로그는 `[Position] 체결진입` 형식이었기 때문이다.

실측(TRADE 로그 건수):
    08-27 `[체결진입]`=1 · `[Position] 체결진입`=9 · `[체결진입보정]`=1
    08-28 0 / 24 / 0
    08-31 0 / 36 / 0
즉 **최근 사흘은 전량 미매칭**이었고, 08-27은 두 형식이 섞여 있어 넓히기만 하면
이중 계상이 난다.
"""
from __future__ import annotations

import importlib.util
import os
import re

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLLECTOR = os.path.join(ROOT, ".claude", "skills", "mireuk-daily-check",
                         "scripts", "collect_evidence.py")


def _load():
    if not os.path.exists(COLLECTOR):
        pytest.skip("수집기 본체 없음 — 스킬 미설치 환경")
    spec = importlib.util.spec_from_file_location("_collect_evidence_f8", COLLECTOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    return _load()


@pytest.fixture(scope="module")
def fill_re(mod):
    pat = mod.DEFAULT_CONFIG["day_summary_patterns"]["fill_entry"]
    return re.compile(pat)


@pytest.fixture(scope="module")
def ext_re(mod):
    pat = mod.DEFAULT_CONFIG["day_summary_patterns"]["ext_entry"]
    return re.compile(pat)


# ── 실제 로그 원문 픽스처 (2026-08-27 · 08-31 TRADE 로그에서 그대로) ─────────
LINE_POS = ("2026-08-31 09:35:05 [INFO] TRADE: [Position] 체결진입 SHORT 1계약 "
            "@ 1051.6 | 평균=1051.55 보유=2계약")
LINE_BRACKET = ("2026-08-27 13:43:22 [INFO] TRADE: [체결진입] SHORT 1계약 "
                "@ 1090.08 | 평균=1089.81 보유=2계약")
LINE_FIXUP = ("2026-08-27 13:43:25 [INFO] TRADE: [체결진입보정] SHORT 2계약 "
              "@ 1089.81 | 평균=1089.81 보유=2계약")
LINE_EXT = ("2026-08-31 09:35:05 [INFO] TRADE: [체결동기화] 외부진입 SHORT 1계약 "
            "@ 1051.6 | 평균=1051.55 보유=2계약")


def test_a_both_forms_match(fill_re):
    """ⓐ 두 형식 모두 잡는다 — 종전에는 `[Position] 체결진입` 이 통째로 빠졌다."""
    m1 = fill_re.search(LINE_POS)
    assert m1 is not None, "`[Position] 체결진입` 미매칭 — 08-31 결손의 원인"
    assert m1.group("dir") == "SHORT"
    assert m1.group("qty") == "1"
    assert m1.group("held") == "2"

    m2 = fill_re.search(LINE_BRACKET)
    assert m2 is not None, "`[체결진입]` 회귀 — 종전 형식이 깨졌다"
    assert m2.group("held") == "2"


def test_b_fixup_line_never_matches(fill_re):
    """ⓑ `[체결진입보정]` 은 **잡히면 안 된다**(F-8의 유일한 실질 위험).

    이미 열린 포지션의 평균가 보정이라 세면 진입이 이중 계상된다.
    """
    assert fill_re.search(LINE_FIXUP) is None, "보정 라인이 진입으로 잡혔다 — 이중 계상"


def test_c_dedup_folds_same_second_duplicate(mod):
    """ⓒ 08-27처럼 두 형식이 같은 체결에 겹치는 날 **접힌다**."""
    same_bracket = ("2026-08-27 13:43:22 [INFO] TRADE: [체결진입] SHORT 1계약 "
                    "@ 1090.08 | 평균=1089.81 보유=2계약")
    same_pos = ("2026-08-27 13:43:22 [INFO] TRADE: [Position] 체결진입 SHORT 1계약 "
                "@ 1090.08 | 평균=1089.81 보유=2계약")
    merged = {"fill_entry": [
        {"_raw": same_bracket, "hhmm": "13:43", "dir": "SHORT", "qty": "1", "held": "2"},
        {"_raw": same_pos, "hhmm": "13:43", "dir": "SHORT", "qty": "1", "held": "2"},
    ]}
    kept, dropped = mod.dedup_fill_entries(merged)
    assert len(kept) == 1, "같은 초·같은 값의 두 형식이 안 접혔다 — 이중 계상"
    assert dropped == 1


def test_d_dedup_keeps_genuine_consecutive_fills(mod):
    """ⓓ 같은 초의 **진짜** 연속 체결은 살아남는다(08-31 09:35:05 실측 2건).

    보유 수량이 1→2→3으로 달라지므로 접기 키가 다르다.
    """
    base = "2026-08-31 09:35:05 [INFO] TRADE: [Position] 체결진입 SHORT 1계약 @ 1051.6"
    merged = {"fill_entry": [
        {"_raw": base, "hhmm": "09:35", "dir": "SHORT", "qty": "1", "held": "2"},
        {"_raw": base, "hhmm": "09:35", "dir": "SHORT", "qty": "1", "held": "3"},
    ]}
    kept, dropped = mod.dedup_fill_entries(merged)
    assert len(kept) == 2
    assert dropped == 0


def test_e_ext_entry_pattern(ext_re):
    """ⓔ 외부진입 표식 — 출처 칸의 근거."""
    m = ext_re.search(LINE_EXT)
    assert m is not None
    assert m.group("dir") == "SHORT"
    assert m.group("held") == "2"


def test_f_position_src_marks_external(mod):
    """ⓕ 같은 초에 외부진입 표식이 있으면 포지션 출처가 「외부」다.

    2026-08-31은 36/36이 외부였는데 요약이 그것을 「엔진 성적」으로 읽히게 냈다(1-14).
    """
    fill = ("2026-08-31 09:28:47 [INFO] TRADE: [Position] 체결진입 SHORT 1계약 "
            "@ 1047.14 | 평균=1047.14 보유=1계약")
    ext = ("2026-08-31 09:28:47 [INFO] TRADE: [체결동기화] 외부진입 SHORT 1계약 "
           "@ 1047.14 | 평균=1047.14 보유=1계약")
    exit_line = ("2026-08-31 09:29:32 [INFO] TRADE: [Position] 체결청산 SHORT @ 1050.66 "
                 "| PnL=-3.52pt (-186,273원) | 하드스톱(틱)")
    merged = {
        "fill_entry": [{"_raw": fill, "hhmm": "09:28", "dir": "SHORT",
                        "qty": "1", "held": "1"}],
        "ext_entry": [{"_raw": ext, "hhmm": "09:28", "dir": "SHORT",
                       "qty": "1", "held": "1"}],
        "exit": [{"_raw": exit_line, "hhmm": "09:29", "dir": "SHORT", "px": "1050.66",
                  "pt": "-3.52", "won": "-186,273", "reason": "하드스톱(틱)"}],
    }
    positions, _ = mod.assemble_positions(merged)
    assert len(positions) == 1
    assert positions[0]["src"] == "외부"
    assert positions[0]["inferred"] is True


def test_g_engine_entry_marks_src_engine(mod):
    """ⓖ `[Position] 진입` 으로 열린 자리는 「엔진」이다."""
    entry = ("2026-08-31 09:28:00 [INFO] TRADE: [Position] 진입 SHORT 1계약 @ 1047.00 "
             "| horizon=1m hurst=0.55")
    merged = {"entry": [{"_raw": entry, "hhmm": "09:28", "dir": "SHORT", "qty": "1",
                         "px": "1047.00", "hz": "1m", "hurst": "0.55"}]}
    positions, _ = mod.assemble_positions(merged)
    assert len(positions) == 1
    assert positions[0]["src"] == "엔진"
