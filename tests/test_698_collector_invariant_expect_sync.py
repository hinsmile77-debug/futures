# -*- coding: utf-8 -*-
"""[MW0601 698차 후속 / 장후 자동조치 F-1] 증거 수집기·점검 체크리스트의 낡은 기대값 동기화.

2026-10-13 사용자 결정(`56cc917`)으로 `MAX_CONTRACTS` 가 3 → 1 이 됐는데 수집기의
기대값이 3 으로 남아, 그날부터 매 점검 §3 표에 「불일치 ⚠」가 떴다. 점검 세션이
매번 「의도값이다, 신규 아님」으로 손으로 정정했다(10-14~10-20). 체크리스트의
`joblib 1.1.1` 표기도 실제 런타임(1.1.0, CLAUDE.md 운영환경 표)과 달랐다.

고정하는 것:
  · 수집기 불변식 `MAX_CONTRACTS` 기대값이 settings.py 실값과 일치한다
  · phases.md 의 joblib 표기가 CLAUDE.md 운영환경 표와 같다
"""
import importlib.util
import io
import os
import re

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SKILL = os.path.join(_ROOT, ".claude", "skills", "mireuk-daily-check")
_PATH = os.path.join(_SKILL, "scripts", "collect_evidence.py")


def _mod():
    spec = importlib.util.spec_from_file_location("_ce698", _PATH)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _read(path):
    with io.open(path, encoding="utf-8") as f:
        return f.read()


def test_max_contracts_expect_matches_settings():
    m = _mod()
    _path, rows, _oos = m.check_invariants(_ROOT, m.DEFAULT_CONFIG)
    row = [r for r in rows if r["name"] == "MAX_CONTRACTS"]
    assert row, "MAX_CONTRACTS 행이 수집기 표에서 빠졌다"
    assert row[0]["verdict"] == "일치", row[0]


def test_phases_joblib_matches_claude_md():
    claude = _read(os.path.join(_ROOT, "CLAUDE.md"))
    m = re.search(r"joblib\s+(\d+\.\d+\.\d+)", claude)
    assert m, "CLAUDE.md 운영환경 표에서 joblib 버전을 못 찾았다"
    phases = _read(os.path.join(_SKILL, "references", "phases.md"))
    found = set(re.findall(r"joblib\s+(\d+\.\d+\.\d+)", phases))
    assert found == {m.group(1)}, (found, m.group(1))
