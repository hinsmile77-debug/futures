# -*- coding: utf-8 -*-
"""[MW0602 637차] 점검 수집기 §5 — 1019 장후 리포트 1-6·1-8(F-10).

① 1-6: 브로커 체결 통보가 주문 결과보다 먼저 오면 `[Position] 진입` 없이
   `[Position] 체결진입` 만 찍힌다(2026-10-19 10:01:36). 그 청산이 고아가 됐다.
② F-10: 신동 트레일이 손절가를 진입가 위로 올려 `[TP1미도달]` 하드스톱이 이익으로
   체결된 2건(+2.90pt·+2.10pt)을 「진짜 손절」로 셌다.
"""
import importlib.util
import os
import re

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PATH = os.path.join(_ROOT, ".claude", "skills", "mireuk-daily-check", "scripts", "collect_evidence.py")
_spec = importlib.util.spec_from_file_location("collect_evidence_637", _PATH)
ce = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ce)

# 2026-10-19 TRADE.log 실제 줄(가상 진입 2건 포함)
_LINES = [
    ("09:03:36", "[Position] 진입 LONG 1계약 @ 864.38 | 손절=840.49 1차=10864.38(×1.00) 2차=10864.38"),
    ("09:03:36", "[Position] 체결보정 LONG 1계약 @ 863.72 | 평균=863.72 보유=1계약"),
    ("09:03:36", "[체결진입] LONG 1계약 @ 863.72 | 평균=863.72 보유=1계약"),
    ("09:05:11", "[Position] 진입 SHORT 1계약 @ 865.72 | 손절=866.92 1차=-9134.28(×1.00) 2차=-9134.28"),
    ("09:05:11", "[Virtual] 피터 가상진입 SHORT 1계약 @865.72 손절 866.92 (peter)"),
    ("09:13:30", "[Position] 체결청산 LONG @ 866.62 | PnL=+2.90pt (+143,359원) | 하드스톱(틱) [TP1미도달]"),
    ("10:01:36", "[Position] 체결진입 LONG 1계약 @ 864.32 | 평균=864.32 보유=1계약"),
    ("10:01:36", "[체결진입] LONG 1계약 @ 864.32 | 평균=864.32 보유=1계약"),
    ("10:14:51", "[Position] 체결청산 LONG @ 876.38 | PnL=+12.06pt (+601,358원) | 신동익절"),
    ("10:16:36", "[Position] 진입 LONG 1계약 @ 876.6 | 손절=852.71 1차=10876.60(×1.00) 2차=10876.60"),
    ("10:16:36", "[Position] 체결보정 LONG 1계약 @ 878.66 | 평균=878.66 보유=1계약"),
    ("10:25:29", "[Position] 체결청산 LONG @ 880.76 | PnL=+2.10pt (+103,331원) | 하드스톱(틱) [TP1미도달]"),
]


def _patterns():
    for name in dir(ce):
        v = getattr(ce, name)
        if isinstance(v, dict) and "day_summary_patterns" in v:
            return v["day_summary_patterns"]
    raise AssertionError("기본 설정에서 day_summary_patterns 를 못 찾았다")


def _merged(lines=_LINES):
    pats = {k: re.compile(p) for k, p in _patterns().items()}
    merged = {}
    for hhmm, line in lines:
        for k, rx in pats.items():
            m = rx.search(line)
            if m:
                d = dict(m.groupdict())
                d["hhmm"] = hhmm
                merged.setdefault(k, []).append(d)
    return merged


def _group(m):
    return ce.group_positions(ce._real_entries(m), m.get("partial_exit", []),
                              m.get("exit", []), ce._chejan_opens(m))


def test_1019_실로그는_포지션_3건_고아_0건():
    positions, orphans = _group(_merged())
    assert orphans == []
    assert [p["entry"]["hhmm"] for p in positions] == ["09:03:36", "10:01:36", "10:16:36"]
    assert all(p["closed"] for p in positions)
    assert [p["anchor"] for p in positions] == ["entry", "fill", "entry"]
    assert sum(p["won"] for p in positions) == 143359 + 601358 + 103331


def test_체결선행_앵커가_없으면_종전처럼_고아가_된다():
    """회귀 기준선 — fill_opens 를 안 넘긴 구 호출부의 동작은 그대로다."""
    m = _merged()
    positions, orphans = ce.group_positions(ce._real_entries(m), [], m["exit"])
    assert len(positions) == 2 and len(orphans) == 1


def test_열린_포지션_중의_체결진입은_증량이라_새_포지션을_열지_않는다():
    lines = [
        ("11:00:00", "[Position] 진입 LONG 1계약 @ 900.0 | 손절=890.0 1차=1(×1.00) 2차=1"),
        ("11:00:05", "[Position] 체결진입 LONG 1계약 @ 900.5 | 평균=900.25 보유=2계약"),
        ("11:10:00", "[Position] 체결청산 LONG @ 905.0 | PnL=+4.75pt (+200,000원) | 신동익절"),
    ]
    positions, orphans = _group(_merged(lines))
    assert len(positions) == 1 and orphans == [] and positions[0]["anchor"] == "entry"


def test_가상_진입과_겹치는_체결진입은_실포지션을_열지_않는다():
    lines = [
        ("12:00:00", "[Position] 체결진입 SHORT 1계약 @ 880.0 | 평균=880.00 보유=1계약"),
        ("12:00:00", "[Virtual] 피터 가상진입 SHORT 1계약 @880.0 손절 885 (peter)"),
    ]
    assert ce._chejan_opens(_merged(lines)) == []


def test_TP1미도달_수익권_스톱은_진짜_손절이_아니다():
    assert ce.exit_stop_kind("하드스톱(틱) [TP1미도달]", "+2.90") == "trail_win"
    assert ce.exit_stop_kind("하드스톱(틱) [TP1미도달]", "-3.10") == "stop"
    assert ce.exit_stop_kind("하드스톱(틱) [TP1미도달]", "+0.00") == "stop"   # 본전은 손절 쪽
    assert ce.exit_stop_kind("하드스톱(틱) [TP1보호]", "+1.00") == "protect"
    assert ce.exit_stop_kind("하드스톱(틱)", "+1.00") == "unknown"
    assert ce.exit_stop_kind("신동익절", "+12.06") is None


def test_pt_미측정이면_태그만_본다():
    """계측 4원칙 ② — pt 를 못 읽었다고 수익권으로 추정하지 않는다."""
    assert ce.exit_stop_kind("하드스톱(틱) [TP1미도달]") == "stop"
    assert ce.exit_stop_kind("하드스톱(틱) [TP1미도달]", "?") == "stop"


def _settings_value(name):
    with open(os.path.join(_ROOT, "config", "settings.py"), encoding="utf-8") as f:
        for line in f:
            m = re.match(r"^%s\s*=\s*([^#\s]+)" % re.escape(name), line)
            if m:
                return m.group(1)
    raise AssertionError("settings.py 에 %s 가 없다" % name)


def _invariant(name):
    for name_ in dir(ce):
        v = getattr(ce, name_)
        if isinstance(v, dict) and "invariants" in v:
            for row in v["invariants"]:
                if row["name"] == name:
                    return row
    raise AssertionError("수집기 invariants 에 %s 가 없다" % name)


def test_F1_CB2_기대값은_실거래_전환_후_현행값이다():
    """1019 F-1 — 수집기 기대값이 모의 시절 9999 에 남아 매일 「불일치」 오탐을 냈다.

    설정이 다시 바뀌면 이 테스트가 깨져 수집기·invariants.md 동시 갱신을 강제한다.
    """
    assert _invariant("CB_CONSEC_STOP_LIMIT")["expect"] == _settings_value("CB_CONSEC_STOP_LIMIT") == "3"
    with open(os.path.join(_ROOT, ".claude", "skills", "mireuk-daily-check",
                           "references", "invariants.md"), encoding="utf-8") as f:
        doc = f.read()
    assert "| `CB_CONSEC_STOP_LIMIT` | **`3`**" in doc


def test_1019_실로그_손절계열_분해():
    ex = _merged()["exit"]
    assert ce.exit_stop_counts(ex) == (0, 0, 0)
    assert ce.exit_trail_win_count(ex) == 2
