# -*- coding: utf-8 -*-
"""[MW0601 555차 후속] 손익 추이 「출처」축 — 화이트리스트 불변식.

🔴 이 축이 틀리는 방향은 언제나 **낙관**이었다
------------------------------------------------
종전 `_assign_origins()` 는 「알려진 manual 이 아니면 auto」였다(블랙리스트).
블랙리스트는 빠뜨리면 시스템 성과 쪽으로 틀린다.

2026-09-10 실측이 정확히 그 형태다:

  · 08:02 pytest 가 운영 `position_state.json` 에 심은 LONG 2계약 @1040.0 을
    08:40 기동이 복원 → 08:45 프리장 첫 틱 1109.60 에 TP1/TP2 발동
    → 허구 이익 **+6,921,594원** (`trades` id=572,573)
  · 554차가 `entry_source` 를 `SYSTEM_AUTO` → `PHANTOM_STATE_ARTIFACT` 로 정정.
    그러나 그 라벨은 **저장소 코드 어디에도 없다**(grep 0건, dev_memory 문서만).
  · 554차는 ProfitGuard 화이트리스트(`PROFIT_GUARD_SYSTEM_SOURCES`)만 보고 정정했고,
    블랙리스트인 이 패널은 그 라벨을 그대로 `auto` 로 읽었다.
  · 결과: 「자동」 필터에 허구 692만원이 잡히고, 실제 브로커 수익 +463,281원
    (`BROKER_SYNC_RECOVERY` = manual)은 빠진다 — **정확히 반대로 나온다.**

그래서 화이트리스트로 뒤집었다. 이 파일이 그 불변식을 고정한다.

실행:
    conda run -n py37_32 python -m pytest tests/test_555_origin_axis_whitelist.py -v
"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

os.environ["MIREUK_TEST_MODE"] = "1"
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402
from PyQt5.QtWidgets import QApplication  # noqa: E402

from config.settings import PROFIT_GUARD_SYSTEM_SOURCES  # noqa: E402
from dashboard.main_dashboard import PnlHistoryPanel  # noqa: E402

_APP = QApplication.instance() or QApplication(sys.argv)

_TS = "2026-09-10 08:02:01"


def _row(src, reason=u"TP2(전량)", ts=_TS):
    return {"entry_ts": ts, "entry_source": src, "exit_reason": reason,
            "pos_key": ts, "origin": "unknown"}


def _origins(rows):
    p = PnlHistoryPanel()
    p._rows = list(rows)
    p._assign_origins()
    return p, [r["origin"] for r in rows]


# ── ① 유령 라벨은 auto 가 아니다 — 이 사고의 지문 ──────────────────────────────
def test_phantom_label_is_not_auto():
    p, out = _origins([_row("PHANTOM_STATE_ARTIFACT", u"TP1 부분청산 33%"),
                       _row("PHANTOM_STATE_ARTIFACT", u"TP2(전량)")])
    assert out == ["unknown", "unknown"], (
        "유령 포지션이 「자동」으로 집계된다 — 허구 692만원이 시스템 성과가 된다")
    assert "PHANTOM_STATE_ARTIFACT" in p._unrecognized_sources


# ── ② 모르는 라벨은 전부 unknown 으로 떨어진다(라벨 이름과 무관) ───────────────
@pytest.mark.parametrize("src", [
    "SOME_FUTURE_SOURCE", "TEST_ARTIFACT", "", "X" * 40,
])
def test_unknown_labels_never_promote_to_auto(src):
    """「모르면 시스템 공로로 치지 않는다」 — 이 축의 보수적 방향."""
    _p, out = _origins([_row(src or None)])
    assert out == ["unknown"], src


# ── ③ 화이트리스트에 있는 것만 auto ─────────────────────────────────────────
def test_whitelisted_source_is_auto():
    for src in PROFIT_GUARD_SYSTEM_SOURCES:
        _p, out = _origins([_row(src, u"하드스톱(틱)")])
        assert out == ["auto"], src


# ── ④ 종전 동작 보존 — manual 판정 3경로는 그대로다 ─────────────────────────
def test_manual_paths_unchanged():
    for src in PnlHistoryPanel._MANUAL_SOURCES:
        _p, out = _origins([_row(src)])
        assert out == ["manual"], src
    # 진입은 시스템인데 사람이 뺀 포지션
    _p, out = _origins([_row(PROFIT_GUARD_SYSTEM_SOURCES[0], u"수동청산(UI)")])
    assert out == ["manual"]
    # entry_source NULL — 미측정
    _p, out = _origins([_row(None)])
    assert out == ["unknown"]


# ── ⑤ 포지션 단위 전파는 그대로 — 한 레그라도 사람 흔적이면 포지션 전체 manual ──
def test_position_level_propagation_survives():
    rows = [_row(PROFIT_GUARD_SYSTEM_SOURCES[0], u"TP1 부분청산 33%"),
            _row(PROFIT_GUARD_SYSTEM_SOURCES[0], u"수동청산(UI)")]
    _p, out = _origins(rows)
    assert out == ["manual", "manual"], "레그 단위로 쪼개지면 계측 4원칙 ① 위반"


# ── ⑥ 정본은 하나다 — 리터럴 사본을 만들면 두 화면이 갈린다 ─────────────────
def test_auto_sources_derive_from_single_definition():
    assert PnlHistoryPanel._AUTO_SOURCES == frozenset(PROFIT_GUARD_SYSTEM_SOURCES), (
        "패널의 「자동」 정의가 ProfitGuard 판정축과 갈렸다 —"
        " 495차 요율 하드코딩과 같은 형태의 사고가 된다")
    src = open(os.path.join(_ROOT, "dashboard", "main_dashboard.py"),
               encoding="utf-8").read()
    assert '_AUTO_SOURCES = frozenset(_AUTO_ENTRY_SOURCES)' in src, (
        "화이트리스트를 리터럴로 베끼지 말 것 — 정본에서 파생해야 한다")


# ── ⑦ 미분류 라벨은 드러난다 — 조용히 삼키지 않는다(계측 4원칙 ③) ──────────
def test_unrecognized_sources_are_surfaced():
    p, _out = _origins([_row("MYSTERY_A"), _row("MYSTERY_B", ts=_TS[:-1] + "2")])
    assert p._unrecognized_sources == {"MYSTERY_A", "MYSTERY_B"}
    tip = p._cb_origin["unknown"].toolTip()
    assert "MYSTERY_A" in tip and "MYSTERY_B" in tip, (
        "미분류 라벨이 툴팁에 드러나지 않는다 — 운영자가 알 방법이 없다")


def test_unrecognized_resets_between_refreshes():
    """이전 조회의 라벨이 남으면 「지금도 있다」로 오독된다(계측 4원칙 ④)."""
    p = PnlHistoryPanel()
    p._rows = [_row("MYSTERY_A")]
    p._assign_origins()
    assert p._unrecognized_sources == {"MYSTERY_A"}
    p._rows = [_row(PROFIT_GUARD_SYSTEM_SOURCES[0])]
    p._assign_origins()
    assert p._unrecognized_sources == set()


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
