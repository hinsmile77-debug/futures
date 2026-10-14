# -*- coding: utf-8 -*-
"""[MW0602 626차] 점검 수집기 §5 — 실거래와 가상 장부를 섞지 않는다.

2026-10-14 장중 다이제스트가 「미청산 4건 + 진입 없는 청산 1건」을 찍었다. 실제는
실거래 1청산·1보유 + 가상 장부 5건 전부 청산이었다. 원인 둘:
  ① 가상 진입도 같은 초에 `[Position] 진입 …` 을 찍는데, 가상 청산은 `체결청산` 이 아니라
     실포지션 표에서 영원히 `_미청산_` 이 됐다.
  ② 신동 진입 줄에는 `horizon=`/`hurst=` 꼬리가 없어 `entry` 정규식에 안 걸렸다(621차 F-2).
"""
import importlib.util
import os
import re

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PATH = os.path.join(_ROOT, ".claude", "skills", "mireuk-daily-check", "scripts", "collect_evidence.py")
_spec = importlib.util.spec_from_file_location("collect_evidence_626", _PATH)
ce = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ce)

_LINES = [
    ("09:09:06", "[Position] 진입 LONG 1계약 @ 961.86 | 손절=944.34 1차=10961.86(×1.00) 2차=10961.86"),
    ("09:37:13", "[Position] 체결청산 LONG @ 966.62 | PnL=+5.08pt (+252,173원) | 하드스톱(틱) [TP1미도달]"),
    ("09:54:00", "[Position] 진입 SHORT 1계약 @ 958.14 | 손절=961.63 1차=956.98(×0.60) 2차=954.65 horizon=3m hurst=trend"),
    ("09:54:00", "[Virtual] 미륵 가상진입 SHORT 1계약 @958.14 손절 961.63 (principal)"),
    ("09:57:00", "[Position] 청산 SHORT @ 957.655 | PnL=+0.49pt (+22,430원) 수수료=1,820원 | 가상:하드스톱"),
    ("09:57:00", "[Virtual] 미륵 가상청산 SHORT 1계약 @957.65 가상:하드스톱 | +0.48pt +22,430원 (포지션 종료)"),
]


def _patterns():
    for name in dir(ce):
        v = getattr(ce, name)
        if isinstance(v, dict) and "day_summary_patterns" in v:
            return v["day_summary_patterns"]
    raise AssertionError("기본 설정에서 day_summary_patterns 를 못 찾았다")


def _merged():
    pats = {k: re.compile(p) for k, p in _patterns().items()}
    merged = {}
    for hhmm, line in _LINES:
        for k, rx in pats.items():
            m = rx.search(line)
            if m:
                d = dict(m.groupdict())
                d["hhmm"] = hhmm
                merged.setdefault(k, []).append(d)
    return merged


def test_신동_진입은_horizon_꼬리_없이도_실진입이다():
    en = ce._real_entries(_merged())
    assert [e["hhmm"] for e in en] == ["09:09:06"]


def test_가상_진입은_실포지션에서_빠지고_미청산이_생기지_않는다():
    m = _merged()
    positions, orphans = ce.group_positions(ce._real_entries(m), m.get("partial_exit", []), m.get("exit", []))
    assert len(positions) == 1 and positions[0]["closed"]
    assert orphans == []


def test_가상_장부는_주체별로_진입과_청산이_묶인다():
    m = _merged()
    vpos, vorph = ce.group_virtual(m["virtual_entry"], m["virtual_exit"])
    assert len(vpos) == 1 and vpos[0]["who"] == "미륵" and vpos[0]["exit"]["won"] == "+22,430"
    assert vorph == []
