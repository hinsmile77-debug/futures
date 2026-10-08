# -*- coding: utf-8 -*-
"""[MW0602 614차 후속2] 사다리 「신동2 해설」 — legacy(기존방식 섀도)가 화면의 실제 계획처럼 보이지 않는다.

발견(2026-10-08 장후 종합점검): 10/12 익일계획을 SKILL 절차대로 live → legacy 순으로 남기자
`/api/day` 의 `sd2ai.latest` 가 **섀도**였다. `ladder_data.shindong2_ai()` 가 `log[-1]` 을 썼기 때문이다
(바로 옆 `_next_plan` 은 거르고 있었다). 차트 계획선(`ladder.html` plans)도 섀도를 그렸다.
672차 테스트는 `ai_latest.json`(파일)만 확인해 이 경로를 못 봤다 — 사다리는 그 파일을 읽지 않는다.

고정하는 것
A. latest 는 마지막 **live** 기록이다(섀도가 더 늦어도).
B. 차트 계획선 필터가 variant 를 거른다 · 기록 목록은 섀도에 표식을 단다(정적 검사).
"""
import datetime as dt
import io
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))
sys.path.insert(0, os.path.join(_ROOT, "tools", "maekjeom_ladder"))
import shindong2_live as M  # noqa: E402
import ladder_data as LD  # noqa: E402


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    monkeypatch.setattr(M, "LIVE_DIR", str(tmp_path / "live"))
    monkeypatch.setattr(M, "DOC_DIR", str(tmp_path / "doc"))
    monkeypatch.setattr(LD, "_sd2_live_mod", lambda: M)
    monkeypatch.setenv("SHINDONG2_LEARN_DIR", str(tmp_path / "learn"))
    return tmp_path


def test_1_latest_is_last_live_even_if_legacy_is_later(sandbox):
    now = dt.datetime(2026, 10, 8, 17, 51, 47)
    M.record("2026-10-12", "overnight", "plan", "매도", 1060.7, 1067.0, 1050.5, "개선", now=now)
    M.record("2026-10-12", "overnight", "plan", "매도", 1061.11, 1067.0, 1050.5, "기존", now=now + dt.timedelta(seconds=2),
             variant="legacy")
    out = LD.shindong2_ai("2026-10-12", [], live=False)
    assert out["latest"]["entry"] == 1060.7 and (out["latest"].get("variant") or "live") == "live"
    assert len(out["log"]) == 2                               # 기록 목록에는 둘 다 남는다(표식으로 구분)


def test_2_latest_none_when_only_legacy(sandbox):
    M.record("2026-10-12", "overnight", "plan", "매도", 1061.11, 1067.0, 1050.5, "기존",
             now=dt.datetime(2026, 10, 8, 17, 51), variant="legacy")
    assert LD.shindong2_ai("2026-10-12", [], live=False)["latest"] is None


def test_3_html_filters_legacy_from_chart_and_tags_log():
    html = io.open(os.path.join(_ROOT, "tools", "maekjeom_ladder", "ladder.html"), encoding="utf-8").read()
    i = html.index("const plans = AI.log.filter(")
    assert "(r.variant || 'live') === 'live'" in html[i:i + 250]
    assert "r.variant === 'legacy' ? ' 〔기존방식 섀도〕'" in html
