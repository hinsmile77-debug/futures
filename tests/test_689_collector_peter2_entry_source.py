# -*- coding: utf-8 -*-
"""[MW0601 689차 / 장후 자동조치] F-5 확장 · G-6 — 수집기 진입 출처 회귀 고정.

**이 사고의 지문을 회귀로 박는다.**

2026-10-13 피터2 보조 로직이 6건 진입·6건 하드스톱(-1,040,578원). TRADE 로그에는
6건 전부 `[Position] 진입` 이 남았지만 `horizon=`·`hurst=` 접미사가 없었다
(`entry_horizon=None` → position_tracker 가 꼬리를 안 붙인다). 수집기 entry 정규식이
그 접미사를 필수로 요구해 6/6 미매칭 → 요약이 전부 「(추정귀속)」.
게다가 「엔진 0건인데 체결 N건」 적신호는 외부동기화 표식이 있을 때만 떠서 침묵했다.

수정 범위는 **점검 수집기(리포트 도구)뿐**이다 — 매매 코드는 한 줄도 안 바뀐다(§4).
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
    spec = importlib.util.spec_from_file_location("_collect_evidence_689", COLLECTOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    return _load()


@pytest.fixture(scope="module")
def pats(mod):
    p = mod.DEFAULT_CONFIG["day_summary_patterns"]
    return {k: re.compile(p[k]) for k in ("entry", "peter2_entry", "fill_entry", "exit")}


# ── 실제 로그 원문 (logs/20261013_TRADE.log 에서 그대로) ──────────────────────
P2_LINE = ("2026-10-13 09:01:10 [INFO] TRADE: [Peter2] 진입 LONG 1계약 @973.04 손절 968.80 "
           "목표 - — limit LONG 지시 975(미니 972.8) 현재 973.04")
POS_P2 = ("2026-10-13 09:01:10 [INFO] TRADE: [Position] 진입 LONG 1계약 @ 973.04 | "
          "손절=968.80 1차=10973.04(×1.00) 2차=10973.04")
FILL_P2 = ("2026-10-13 09:01:10 [INFO] TRADE: [체결진입] LONG 1계약 @ 973.36 | "
           "평균=973.36 보유=1계약")
EXIT_P2 = ("2026-10-13 09:05:20 [INFO] TRADE: [Position] 체결청산 LONG @ 968.74 | "
           "PnL=-4.62pt (-240,549원) | 하드스톱(틱)")
# 엔진 진입 형식(두 꼬리 모두 / horizon 만)
POS_ENG = ("2026-08-31 09:28:00 [INFO] TRADE: [Position] 진입 SHORT 1계약 @ 1047.00 | "
           "손절=1050.00 1차=1045.0(×0.50) 2차=1043.0 horizon=1m hurst=mid")
POS_ENG_NOHURST = ("2026-08-31 10:12:00 [INFO] TRADE: [Position] 진입 LONG 2계약 @ 1050.00 | "
                   "손절=1047.00 1차=1051.0(×0.30) 2차=1052.0 horizon=3m")


def _rec(pat, line):
    m = pat.search(line)
    assert m is not None, "미매칭: %s" % line
    d = {k: v for k, v in m.groupdict().items()}
    d["_raw"] = line
    d["hhmm"] = line[11:16]
    return d


# ─────────────────────────────────────────────────────────────────────────────
# §1. F-5 확장 — 접미사는 선택이다
# ─────────────────────────────────────────────────────────────────────────────

def test_1a_peter2_position_line_now_matches(pats):
    """접미사 없는 `[Position] 진입` 이 매칭된다 — 10-13 결손의 원인."""
    r = _rec(pats["entry"], POS_P2)
    assert r["dir"] == "LONG" and r["qty"] == "1" and r["px"] == "973.04"
    assert r["hz"] is None and r["hurst"] is None


def test_1b_engine_line_still_captures_suffixes(pats):
    """종전 형식 회귀 — 엔진 진입의 horizon·hurst 를 계속 뽑는다."""
    r = _rec(pats["entry"], POS_ENG)
    assert r["hz"] == "1m" and r["hurst"] == "mid"


def test_1c_horizon_without_hurst_matches(pats):
    """`_regime_mult` 가 없어 hurst= 가 빠진 엔진 줄도 잡는다(종전엔 이것도 놓쳤다)."""
    r = _rec(pats["entry"], POS_ENG_NOHURST)
    assert r["hz"] == "3m" and r["hurst"] is None


def test_1d_peter2_marker_pattern(pats):
    r = _rec(pats["peter2_entry"], P2_LINE)
    assert r["dir"] == "LONG" and r["qty"] == "1"
    # `[Position] 진입` 정규식이 `[Peter2] 진입` 을 잡으면 이중 계상된다.
    assert pats["entry"].search(P2_LINE) is None


# ─────────────────────────────────────────────────────────────────────────────
# §2. 출처 판정 — 엔진 / 피터2 / 추정
# ─────────────────────────────────────────────────────────────────────────────

def test_2a_peter2_position_is_not_engine_and_not_inferred(mod, pats):
    """10-13 지문: 피터2 자리는 「피터2」로 열리고 「(추정귀속)」이 아니다."""
    merged = {
        "entry": [_rec(pats["entry"], POS_P2)],
        "peter2_entry": [_rec(pats["peter2_entry"], P2_LINE)],
        "fill_entry": [_rec(pats["fill_entry"], FILL_P2)],
        "exit": [_rec(pats["exit"], EXIT_P2)],
    }
    positions, orphans = mod.assemble_positions(merged)
    assert len(positions) == 1 and not orphans
    q = positions[0]
    assert q["src"] == "피터2"
    assert q["inferred"] is False
    assert q["closed"] and q["net_won"] == -240549
    assert mod.count_entry_sources(merged) == {"엔진": 0, "피터2": 1, "추정": 0}


def test_2b_engine_entry_stays_engine(mod, pats):
    merged = {"entry": [_rec(pats["entry"], POS_ENG)]}
    positions, _ = mod.assemble_positions(merged)
    assert positions[0]["src"] == "엔진"


def test_2c_no_marker_no_horizon_is_unmeasured(mod, pats):
    """표식도 horizon 도 없으면 「추정」 — 「엔진 아님」이 아니라 미측정(4원칙 ②)."""
    merged = {"entry": [_rec(pats["entry"], POS_P2)]}
    positions, _ = mod.assemble_positions(merged)
    assert positions[0]["src"] == "추정"


def test_2d_pairing_tolerance_is_narrow(mod, pats):
    """피터2 표식이 3초 이상 떨어지면 짝짓지 않는다 — 엔진 자리를 오귀속하지 않게."""
    far = P2_LINE.replace("09:01:10", "09:01:14")
    merged = {"entry": [_rec(pats["entry"], POS_ENG.replace("2026-08-31 09:28:00",
                                                           "2026-10-13 09:01:10"))],
              "peter2_entry": [_rec(pats["peter2_entry"], far)]}
    assert mod.count_entry_sources(merged)["엔진"] == 1


# ─────────────────────────────────────────────────────────────────────────────
# §3. G-6 — 적신호가 외부동기화 없이도 뜬다
# ─────────────────────────────────────────────────────────────────────────────

def _render(mod, merged):
    class _Dg(object):
        hits = merged
        banner = []
    out = []
    mod.day_summary([_Dg()], mod.DEFAULT_CONFIG, out)
    return "\n".join(out)


def test_3a_red_flag_fires_without_external_sync(mod, pats):
    """10-13: 외부 0 · 엔진 0 · 체결 1(피터2) → 적신호가 떠야 한다(종전엔 침묵)."""
    merged = {
        "entry": [_rec(pats["entry"], POS_P2)],
        "peter2_entry": [_rec(pats["peter2_entry"], P2_LINE)],
        "fill_entry": [_rec(pats["fill_entry"], FILL_P2)],
        "exit": [_rec(pats["exit"], EXIT_P2)],
    }
    txt = _render(mod, merged)
    assert "엔진 진입 0건인데 계좌 체결 1건" in txt
    assert "피터2 1" in txt
    assert "(추정귀속)" not in txt


def test_3b_red_flag_silent_when_engine_entered(mod, pats):
    fill = FILL_P2.replace("LONG", "SHORT")
    merged = {"entry": [_rec(pats["entry"], POS_ENG.replace("2026-08-31 09:28:00",
                                                           "2026-10-13 09:01:10"))],
              "fill_entry": [_rec(pats["fill_entry"], fill)]}
    assert "엔진 진입 0건인데" not in _render(mod, merged)


def test_3c_old_condition_is_gone(mod):
    src = open(COLLECTOR, encoding="utf-8").read()
    assert "if _ext and not en:" not in src, "종전 적신호 조건(외부동기화 한정)이 남아 있다"
    assert 'if _fi_kept and _en_engine == 0:' in src


# ─────────────────────────────────────────────────────────────────────────────
# §4. 「라이브 반영 0」 — 수집기는 매매 코드를 import·호출하지 않는다
# ─────────────────────────────────────────────────────────────────────────────

def test_4_collector_is_report_only():
    src = open(COLLECTOR, encoding="utf-8").read()
    for forbidden in ("from strategy", "import strategy", "from main import",
                      "send_market_order", "_execute_entry", "close_position"):
        assert forbidden not in src, "수집기가 매매 경로에 닿는다: %s" % forbidden
    import py_compile
    py_compile.compile(COLLECTOR, doraise=True)
