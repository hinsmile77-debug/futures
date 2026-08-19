# -*- coding: utf-8 -*-
"""[MW0601 480차 / G-2] 로그 종료시각 기준선 — 불변식 테스트.

## 무엇을 지키는가

2026-08-19 동결일, 수집기 §11은 로그 공백을 정확히 짚었다(`13:52~15:10 연속 79분`).
그런데 *"정상일에는 15:40까지 로그가 있다"* 는 **비교 기준선이 리포트에 없어서**,
이상 여부를 사람이 직전 12거래일 로그를 하나씩 열어 확인해야 했다. 그 수작업을
기계가 하게 만든 것이 G-2다.

FZ-6(478차 후속)과 잡는 구간이 다르다 — FZ-6은 *장중 침묵*(지금 멎었다),
G-2는 *장후 조기종료*(오늘 하루가 일찍 끝났다). 둘 다 필요하다.

지키는 불변식:

  ① 종료시각은 **로그 본문의 마지막 타임스탬프**에서 온다(mtime은 폴백이고,
     폴백을 썼으면 그 사실이 출처 문자열에 남는다 — 계측 4원칙 ④)
  ② 기준선은 **오늘 이전** 날짜만 쓴다(자기 자신을 기준으로 삼으면 항상 정상이다)
  ③ 읽을 수 없으면 0분이 아니라 **None**이다(계측 4원칙 ②)
"""
from __future__ import annotations

import datetime
import os
import runpy
import tempfile

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BODY = os.path.join(ROOT, ".claude", "skills", "mireuk-daily-check",
                    "scripts", "collect_evidence.py")


@pytest.fixture(scope="module")
def ce():
    if not os.path.exists(BODY):
        pytest.skip("수집기 본체 없음: %s" % BODY)
    return runpy.run_path(BODY, run_name="_ce_under_test")


@pytest.fixture
def sandbox():
    d = tempfile.mkdtemp(prefix="mireuk_480_")
    os.makedirs(os.path.join(d, "logs"))
    return d


def _write(root, name, last_hhmmss):
    p = os.path.join(root, "logs", name)
    with open(p, "w", encoding="utf-8") as f:
        f.write("2026-08-18 09:00:00 [INFO] SYSTEM: start\n")
        if last_hhmmss:
            f.write("2026-08-18 %s [INFO] SYSTEM: last\n" % last_hhmmss)
    return p


# ── ① 본문 우선 ───────────────────────────────────────────────────────────

def test_종료시각은_본문_마지막_타임스탬프다(ce, sandbox):
    p = _write(sandbox, "20260818_SYSTEM.log", "15:40:38")
    minute, src = ce["log_end_minute"](p)
    assert minute == 15 * 60 + 40
    assert src == "로그 본문"


def test_본문에_시각이_없으면_mtime_폴백이고_그_사실을_남긴다(ce, sandbox):
    p = _write(sandbox, "20260818_SYSTEM.log", None)
    with open(p, "w", encoding="utf-8") as f:
        f.write("시각 없는 줄\n")
    minute, src = ce["log_end_minute"](p)
    assert minute is not None
    assert "폴백" in src, "폴백을 썼는데 출처가 그것을 말하지 않는다 (계측 4원칙 ④)"


def test_읽을_수_없으면_0이_아니라_None이다(ce, sandbox):
    minute, src = ce["log_end_minute"](os.path.join(sandbox, "logs", "없는파일.log"))
    assert minute is None and "실패" in src


# ── ② 기준선 ─────────────────────────────────────────────────────────────

def test_기준선은_오늘_이전_날짜만_쓴다(ce, sandbox):
    _write(sandbox, "20260819_SYSTEM.log", "13:51:22")   # 오늘 — 제외돼야 한다
    for tok in ("20260818", "20260814", "20260813"):
        _write(sandbox, "%s_SYSTEM.log" % tok, "15:40:10")
    rows = ce["prior_log_end_baseline"](sandbox, datetime.date(2026, 8, 19))
    assert [r["date"] for r in rows] == ["20260818", "20260814", "20260813"]
    assert ce["median_minute"](rows) == 15 * 60 + 40


def test_최근_n일만_본다(ce, sandbox):
    for d in range(1, 9):
        _write(sandbox, "202608%02d_SYSTEM.log" % d, "15:40:00")
    rows = ce["prior_log_end_baseline"](sandbox, datetime.date(2026, 8, 19), n=5)
    assert len(rows) == 5
    assert rows[0]["date"] == "20260808"      # 최신부터


def test_로그가_없으면_빈_기준선이다(ce, sandbox):
    assert ce["prior_log_end_baseline"](sandbox, datetime.date(2026, 8, 19)) == []


# ── ③ 08-19 사고 재현 ────────────────────────────────────────────────────

def test_08_19_동결일이_30분_기준을_넘긴다(ce, sandbox):
    """실측 재현: 직전 5거래일 15:40대 vs 당일 13:51 → 델타 −109분."""
    for tok in ("20260818", "20260814", "20260813", "20260812", "20260811"):
        _write(sandbox, "%s_SYSTEM.log" % tok, "15:40:20")
    p = _write(sandbox, "20260819_SYSTEM.log", "13:51:22")
    base = ce["prior_log_end_baseline"](sandbox, datetime.date(2026, 8, 19))
    med = ce["median_minute"](base)
    today = ce["log_end_minute"](p)[0]
    assert today - med <= -30, "동결일이 조기종료 적신호에 걸리지 않는다"
    assert med - today == 109
