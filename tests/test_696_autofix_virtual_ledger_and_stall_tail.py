# -*- coding: utf-8 -*-
"""[MW0601 696차 / 장후 자동조치] E-2 · F-X1 회귀 고정.

E-2 — 점검 수집기가 가상 장부 진입을 「가상」으로 분리한다.
    2026-10-15 TRADE 로그: 신동 가상 2건(09:41:59 · 09:48:59)·미륵 가상 1건(11:32:00)이
    같은 초에 `[Position] 진입` 을 남겼다. 미륵 건은 `horizon=3m` 까지 붙어 「엔진」으로
    세어졌고, 3원 대사가 「1=1≠4」 불일치처럼 보였다. 15:40 EOD 집계(신동 +599,680원 ·
    미륵 +22,290원)와 가상청산 로그 합이 일치해야 한다.

F-X1 — X 버튼 종료 로그에 직전 메인 스레드 정지를 동반 기록한다.
    2026-10-15 12:12:04 정지 7,750ms → 12:14:13 사용자 종료. 인과를 로그로 가를 수 없어
    O-i2 가 판정 보류로 남았다. 간격 129초라 60초 창이었으면 흔적이 안 남았다.

둘 다 계측·도구 변경이다 — 매매 경로(진입·청산·주문)는 한 줄도 바뀌지 않는다(§4).
"""
from __future__ import annotations

import importlib.util
import io
import os
import re
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

COLLECTOR = os.path.join(ROOT, ".claude", "skills", "mireuk-daily-check",
                         "scripts", "collect_evidence.py")


def _load():
    if not os.path.exists(COLLECTOR):
        pytest.skip("수집기 본체 없음 — 스킬 미설치 환경")
    spec = importlib.util.spec_from_file_location("_collect_evidence_696", COLLECTOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    return _load()


@pytest.fixture(scope="module")
def pats(mod):
    p = mod.DEFAULT_CONFIG["day_summary_patterns"]
    return {k: re.compile(p[k]) for k in ("entry", "peter2_entry", "fill_entry", "exit",
                                          "virtual_entry", "virtual_exit")}


def _rec(pat, line):
    m = pat.search(line)
    assert m is not None, "미매칭: %s" % line
    d = dict(m.groupdict())
    d["_raw"] = line
    d["hhmm"] = line[11:16]
    return d


# ── 실제 로그 원문 (logs/20261015_TRADE.log 에서 그대로) ──────────────────────
T = "2026-10-15 %s [INFO] TRADE: "
POS_V1 = T % "09:41:59" + ("[Position] 진입 LONG 1계약 @ 875.74 | 손절=873.50 "
                           "1차=10875.74(×1.00) 2차=10875.74")
VIN_1 = T % "09:41:59" + "[Virtual] 신동 가상진입 LONG 1계약 @875.74 손절 873.50 목표 950.50 (principal)"
VOUT_1 = T % "09:43:00" + ("[Virtual] 신동 가상청산 LONG 1계약 @873.50 가상:하드스톱 | "
                           "-2.24pt -113,664원 (포지션 종료)")
POS_V2 = T % "09:48:59" + ("[Position] 진입 SHORT 1계약 @ 871.56 | 손절=876.50 "
                           "1차=-9128.44(×1.00) 2차=-9128.44")
VIN_2 = T % "09:48:59" + "[Virtual] 신동 가상진입 SHORT 1계약 @871.56 손절 876.50 목표 847.20 (principal)"
VOUT_2 = T % "14:28:23" + ("[Virtual] 신동 가상청산 SHORT 1계약 @857.26 가상:신동미러:TP1 | "
                           "+14.30pt +713,344원 (포지션 종료)")
POS_V3 = T % "11:32:00" + ("[Position] 진입 SHORT 1계약 @ 862.76 | 손절=865.20 1차=861.95(×0.42) "
                           "2차=860.32 horizon=3m hurst=mean-revert")
VIN_3 = T % "11:32:00" + "[Virtual] 미륵 가상진입 SHORT 1계약 @862.76 손절 865.20 (principal)"
VOUT_3 = T % "11:34:00" + ("[Virtual] 미륵 가상청산 SHORT 1계약 @862.28 가상:하드스톱 | "
                           "+0.48pt +22,290원 (포지션 종료)")
# 피터2 실거래(같은 날 09:05:49 진입 → 09:16:39 청산)
P2 = T % "09:05:49" + "[Peter2] 진입 SHORT 1계약 @892.6 손절 896 목표 -"
POS_P2 = T % "09:05:49" + "[Position] 진입 SHORT 1계약 @ 892.6 | 손절=896.00 1차=-9107.4(×1.00) 2차=-9107.4"
FILL_P2 = T % "09:05:49" + "[체결진입] SHORT 1계약 @ 892.6 | 평균=892.6 보유=1계약"
EXIT_P2 = T % "09:16:39" + ("[Position] 체결청산 SHORT @ 879.32 | PnL=+13.28pt (+662,304원) | "
                            "피터2미러(청산)")


def _day(pats):
    return {
        "entry": [_rec(pats["entry"], x) for x in (POS_P2, POS_V1, POS_V2, POS_V3)],
        "peter2_entry": [_rec(pats["peter2_entry"], P2)],
        "fill_entry": [_rec(pats["fill_entry"], FILL_P2)],
        "exit": [_rec(pats["exit"], EXIT_P2)],
        "virtual_entry": [_rec(pats["virtual_entry"], x) for x in (VIN_1, VIN_2, VIN_3)],
        "virtual_exit": [_rec(pats["virtual_exit"], x) for x in (VOUT_1, VOUT_3, VOUT_2)],
    }


# ─────────────────────────────────────────────────────────────────────────────
# §1. E-2 — 가상 장부 분리
# ─────────────────────────────────────────────────────────────────────────────

def test_1a_virtual_patterns_do_not_double_count(pats):
    r = _rec(pats["virtual_exit"], VOUT_2)
    assert r["who"] == "신동" and r["dir"] == "SHORT" and r["won"] == "+713,344"
    # 가상진입 줄이 `[Position] 진입` 정규식에 걸리면 이중 계상된다.
    assert pats["entry"].search(VIN_1) is None
    assert pats["virtual_entry"].search(VOUT_1) is None


def test_1b_counts_10_15(mod, pats):
    """10-15 지문: 진입 4 = 피터2 1 + 가상 3 · 엔진 0 (종전엔 엔진 1로 셌다)."""
    assert mod.count_entry_sources(_day(pats)) == {"엔진": 0, "피터2": 1, "가상": 3, "추정": 0}


def test_1c_virtual_beats_horizon(mod, pats):
    """`horizon=3m` 이 붙은 미륵 가상도 「엔진」이 아니다."""
    d = _day(pats)
    r = _rec(pats["entry"], POS_V3)
    assert mod.entry_source_of(r, mod._peter2_secs(d), mod._virtual_secs(d)) == "가상"
    # 가상 표식이 없으면 종전대로 엔진
    assert mod.entry_source_of(r, [], []) == "엔진"


def test_1d_virtual_pnl_matches_eod(mod, pats):
    """가상청산 합이 15:40 EOD 집계와 같다 — 신동 +599,680 · 미륵 +22,290."""
    positions, orphans = mod.assemble_positions(_day(pats))
    v = [q for q in positions if mod.is_virtual_position(q)]
    assert len(v) == 3 and all(q["closed"] for q in v)
    by = {}
    for q in v:
        by[q["who"]] = by.get(q["who"], 0) + q["net_won"]
    assert by == {"신동": 599680, "미륵": 22290}
    real = [q for q in positions if not mod.is_virtual_position(q)]
    assert len(real) == 1 and real[0]["src"] == "피터2" and real[0]["net_won"] == 662304
    assert not orphans


def test_1e_virtual_does_not_capture_real_legs(mod, pats):
    """가상 진입 뒤의 실체결 청산이 가상 포지션에 붙지 않는다(종전 조립기 결함)."""
    fill = T % "09:50:00" + "[체결진입] LONG 1계약 @ 870.0 | 평균=870.0 보유=1계약"
    ext = T % "09:55:00" + ("[Position] 체결청산 LONG @ 871.0 | PnL=+1.00pt (+50,000원) | "
                            "하드스톱(틱)")
    d = {"entry": [_rec(pats["entry"], POS_V2)],
         "virtual_entry": [_rec(pats["virtual_entry"], VIN_2)],
         "fill_entry": [_rec(pats["fill_entry"], fill)],
         "exit": [_rec(pats["exit"], ext)]}
    positions, _ = mod.assemble_positions(d)
    real = [q for q in positions if not mod.is_virtual_position(q)]
    virt = [q for q in positions if mod.is_virtual_position(q)]
    assert len(real) == 1 and real[0]["net_won"] == 50000 and real[0]["closed"]
    assert len(virt) == 1 and virt[0]["legs"] == [] and not virt[0]["closed"]


def test_1f_unmatched_virtual_exit_is_visible(mod, pats):
    """짝 없는 가상청산은 버리지 않는다(계측 4원칙 ③)."""
    positions, _ = mod.assemble_positions({"virtual_exit": [_rec(pats["virtual_exit"], VOUT_2)]})
    assert len(positions) == 1 and positions[0]["inferred"] and positions[0]["net_won"] == 713344


def _render(mod, merged):
    class _Dg(object):
        hits = merged
        banner = []
    out = []
    mod.day_summary([_Dg()], mod.DEFAULT_CONFIG, out)
    return "\n".join(out)


def test_1g_render_separates_headline(mod, pats):
    txt = _render(mod, _day(pats))
    assert "포지션 1건 · 승 1" in txt                    # 헤드라인 = 실계좌만
    assert "가상 장부 3건(청산 3 · 합계 +621,970원)" in txt
    assert "그중 가상(`[Virtual] … 가상진입` 동반)" in txt


# ─────────────────────────────────────────────────────────────────────────────
# §2. F-X1 — 종료 로그의 직전 정지 꼬리
# ─────────────────────────────────────────────────────────────────────────────

from utils.exit_flags import format_recent_stall, write_exit_flags  # noqa: E402


def test_2a_none_is_not_zero():
    assert format_recent_stall(None, None, 100.0) == "recent_stall=none"


def test_2b_10_15_case_129s_outside_60_inside_300():
    tail = format_recent_stall(7750.0, 1000.0, 1129.0)
    assert tail == "recent_stall_ms=7750 stall_age_s=129.0 within_window=True(300s)"
    assert "within_window=False" in format_recent_stall(7750.0, 1000.0, 1129.0, window_s=60)


def test_2c_never_raises():
    assert format_recent_stall("x", 1.0, 2.0).startswith("recent_stall=unknown")


def test_2d_extra_appended_prefix_unchanged(tmp_path):
    (tmp_path / "data").mkdir()
    got = []
    write_exit_flags("user_restart", keep_alive=True, root=str(tmp_path),
                     log_fn=lambda m, lv: got.append(m),
                     extra="recent_stall_ms=7750 stall_age_s=129.0 within_window=True(300s)")
    assert got == ["[Shutdown] intent=user_restart keep_alive=True files=0 "
                   "recent_stall_ms=7750 stall_age_s=129.0 within_window=True(300s)"]
    # 수집기 의도 파서(앞머리 정규식)가 그대로 읽는다
    assert re.search(r"\[Shutdown\] intent=(\w+)", got[0]).group(1) == "user_restart"


def test_2e_no_extra_is_byte_identical(tmp_path):
    """daily_close·auto_shutdown 경로(extra 없음)는 종전 문자열 그대로다."""
    (tmp_path / "data").mkdir()
    got = []
    write_exit_flags("daily_close", root=str(tmp_path), log_fn=lambda m, lv: got.append(m))
    assert got == ["[Shutdown] intent=daily_close keep_alive=False files=2"]


def _dash_src():
    return io.open(os.path.join(ROOT, "dashboard", "main_dashboard.py"),
                   encoding="utf-8").read()


def test_2f_dashboard_wiring():
    src = _dash_src()
    # 명시 초기화 — getattr 폴백 금지(계측 4원칙 ④)
    assert "self._last_stall_ms = None" in src and "self._last_stall_mono = None" in src
    assert 'getattr(self, "_last_stall' not in src
    ce = src.split('"종료 방법을 선택하세요."')[1].split("\n    def ")[0]
    calls = [ln for ln in ce.splitlines() if "_wef(" in ln]
    assert len(calls) == 2
    assert ce.count("extra=_stall_tail") == 2


# ─────────────────────────────────────────────────────────────────────────────
# §3. 「라이브 반영 0」 — 매매 경로에 닿지 않는다
# ─────────────────────────────────────────────────────────────────────────────

def test_3a_collector_is_report_only():
    src = io.open(COLLECTOR, encoding="utf-8").read()
    for forbidden in ("from strategy", "import strategy", "from main import",
                      "send_market_order", "_execute_entry", "close_position"):
        assert forbidden not in src, "수집기가 매매 경로에 닿는다: %s" % forbidden


def test_3b_stall_record_is_write_only_state():
    """대시보드의 `_last_stall_*` 는 종료 로그 꼬리 외에 아무 데서도 읽지 않는다."""
    src = _dash_src()
    reads = [ln for ln in src.splitlines()
             if "self._last_stall_ms" in ln and "self._last_stall_ms =" not in ln]
    assert len(reads) == 1 and "_frs(" in reads[0], reads
