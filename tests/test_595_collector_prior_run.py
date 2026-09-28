# -*- coding: utf-8 -*-
"""[MW0602 595차 후속 / G-1] 수집기 「같은 국면 선행 실행」 감지 불변식.

무엇을 막는가
-------------
2026-09-28 08:55:19 / 08:57:12 — 중복 등록된 예약 두 벌이 2분 간격으로 같은 "장전"
점검을 시작했다(592차 최초 발견). 수집기는 기존 다이제스트를 `_HHMM` 로 rename 하며
**stderr 에만** 경고했고 다이제스트(§2·§11)에는 아무것도 남지 않아, 매 점검이 예약
목록을 손으로 확인해야 했다.

이 파일이 고정하는 불변식
------------------------
① 선행 실행 없음 → measured=True · flags 0
② 기존본 + `_HHMM` 보존본 → 개수·파일명이 적신호에 실린다
③ 다른 국면·다른 날짜·다른 PC 파일은 세지 않는다
④ 폴더 읽기 실패 / phase=all → measured=False (「없음」으로 위장하지 않는다)
⑤ build() 가 §2 에 블록을 찍고 §11 에 적신호를 올린다(배선 확인)

실행:
    python -m pytest tests/test_595_collector_prior_run.py -q
"""
import io
import os
import shutil
import sys
import tempfile
from datetime import date

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, ".claude", "skills", "mireuk-daily-check", "scripts"))

import collect_evidence as CE

_DAY = date(2026, 9, 28)


def _mk(d, name):
    with io.open(os.path.join(d, name), "w", encoding="utf-8") as f:
        f.write(u"x")


def _tmp():
    return tempfile.mkdtemp(prefix="t595_")


def test_1_no_prior_run():
    d = _tmp()
    try:
        st = CE.prior_run_state(d, "MW0602", _DAY, "pre", CE.now_kst())
        assert st["measured"] is True
        assert st["prior"] == [] and st["flags"] == []
        assert "첫 수집" in st["lines"][0]
    finally:
        shutil.rmtree(d)


def test_2_prior_and_preserved_copies_are_flagged():
    d = _tmp()
    try:
        _mk(d, "evidence_MW0602-20260928_pre.md")
        _mk(d, "evidence_MW0602-20260928_pre_0855.md")
        _mk(d, "evidence_MW0602-20260928_pre_0855-1.md")
        st = CE.prior_run_state(d, "MW0602", _DAY, "pre", CE.now_kst())
        assert st["measured"] is True
        assert len(st["prior"]) == 3, st["prior"]
        assert len(st["flags"]) == 1
        f = st["flags"][0]
        assert "이미 3회" in f and "병행 세션" in f
        assert "evidence_MW0602-20260928_pre_0855.md" in f
    finally:
        shutil.rmtree(d)


def test_3_other_phase_day_pc_not_counted():
    d = _tmp()
    try:
        _mk(d, "evidence_MW0602-20260928_intra.md")
        _mk(d, "evidence_MW0602-20260927_pre.md")
        _mk(d, "evidence_MW0601-20260928_pre.md")
        _mk(d, "evidence_MW0602-20260928_pre.md.bak")
        _mk(d, "MW0602-20260928-점검리포트.md")
        st = CE.prior_run_state(d, "MW0602", _DAY, "pre", CE.now_kst())
        assert st["measured"] is True and st["prior"] == [] and st["flags"] == []
    finally:
        shutil.rmtree(d)


def test_4_unmeasured_is_not_none():
    st = CE.prior_run_state(os.path.join(_tmp(), "no_such_dir"), "MW0602", _DAY, "pre",
                            CE.now_kst())
    assert st["measured"] is False and st["flags"] == []
    assert "미측정" in st["lines"][0]
    st2 = CE.prior_run_state(_tmp(), "MW0602", _DAY, "all", CE.now_kst())
    assert st2["measured"] is False and "미측정" in st2["lines"][0]


def test_5_truncation_shows_remainder():
    d = _tmp()
    try:
        _mk(d, "evidence_MW0602-20260928_post.md")
        for hh in ("1500", "1510", "1520", "1530", "1540", "1550"):
            _mk(d, "evidence_MW0602-20260928_post_%s.md" % hh)
        st = CE.prior_run_state(d, "MW0602", _DAY, "post", CE.now_kst())
        assert len(st["prior"]) == 7
        assert "외 2개" in st["flags"][0]           # 계측 4원칙 ③
    finally:
        shutil.rmtree(d)


def test_6_wired_into_build_section2_and_section11():
    """⑤ 배선 — 소스 수준 확인(build() 전체 실행은 로그·DB 에 의존해 무겁다)."""
    src = io.open(CE.__file__, encoding="utf-8").read()
    body = src[src.index("def build("):]
    i_sec2 = body.index('A("## 2. 코드·커밋 상태")')
    i_call = body.index("prior_run_state(")
    i_sec3 = body.index('A("## 3. 설정 불변식')
    assert i_sec2 < i_call < i_sec3, "§2 안에서 호출돼야 한다"
    i_sec11 = body.index('A("## 11. 자동 적신호')
    assert body.index("flags.extend(_prior_flags", i_sec11) > i_sec11, "§11 로 승격돼야 한다"


if __name__ == "__main__":
    for k, v in sorted(globals().items()):
        if k.startswith("test_") and callable(v):
            v()
            print("ok", k)
