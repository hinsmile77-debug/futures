# -*- coding: utf-8 -*-
"""[MW0601 667차 / G-2] 증거 수집기 — 장중 수집 시 분모를 「수집 시각까지」로 줄인다.

2026-09-14·09-29·10-07 장중 점검이 매번 같은 거짓 적신호를 손으로 정정했다:
12:27 수집인데 분모를 09:00~15:10 으로 고정해 「커버리지 56.1%」「12:28~15:10
연속 163분 기록 없음」「영구 결손 162봉」이 떴다 — 전부 아직 오지 않은 미래다.

고정하는 것:
  · 장전·장중 + 오늘 + 영업일일 때만 끊는다 (장후·과거 날짜는 전 구간 — 진짜 결손을 가리지 않도록)
  · 커버리지 분모가 수집 분까지로 줄어든다
  · 분봉은 ts ≤ 수집분 − 2 만 「있어야 할 봉」으로 센다
  · 배선 — 표·적신호·raw_candles 절이 모두 같은 컷을 쓴다
"""
import datetime
import importlib.util
import io
import os

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PATH = os.path.join(_ROOT, ".claude", "skills", "mireuk-daily-check", "scripts",
                     "collect_evidence.py")


def _mod():
    spec = importlib.util.spec_from_file_location("_ce667", _PATH)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


_NOW = datetime.datetime(2026, 10, 7, 12, 27, 30)
_DAY = _NOW.date()


def test_live_cutoff_only_for_live_phases_today():
    m = _mod()
    f = m.live_cutoff_min
    assert f("intra", _DAY, False, now=_NOW) == 12 * 60 + 27
    assert f("pre", _DAY, False, now=_NOW) == 12 * 60 + 27
    # 장후·전체는 하루가 끝났다 — 끊지 않는다
    assert f("post", _DAY, False, now=_NOW) is None
    assert f("all", _DAY, False, now=_NOW) is None
    # 과거 날짜를 장중 국면으로 다시 돌려도 끊지 않는다
    assert f("intra", datetime.date(2026, 10, 6), False, now=_NOW) is None
    # 휴장일은 끊을 분모 자체가 없다
    assert f("intra", _DAY, True, now=_NOW) is None


class _Dg(object):
    """minute_coverage 만 빌려 쓰는 최소 대역."""


def _digest(m, minutes):
    dg = _Dg()
    dg.cfg = {"minute_loop_window": ["09:00", "15:10"]}
    dg.records = [{"minutes": x} for x in minutes]
    return m.LogDigest.minute_coverage.__get__(dg)


def test_coverage_denominator_shrinks_to_cutoff():
    m = _mod()
    # 09:00~12:27 매분 기록 (208분)
    cov = _digest(m, range(9 * 60, 12 * 60 + 28))
    have, total, missing = cov()               # 종전 동작 — 고정 분모
    assert (have, total) == (208, 371) and len(missing) == 163
    have, total, missing = cov(12 * 60 + 27)   # 장중 컷
    assert (have, total, missing) == (208, 208, [])


def test_coverage_cutoff_still_shows_real_gap():
    m = _mod()
    mins = [x for x in range(9 * 60, 12 * 60 + 28) if not (10 * 60 <= x < 10 * 60 + 5)]
    have, total, missing = _digest(m, mins)(12 * 60 + 27)
    assert total == 208 and missing == list(range(600, 605))


def test_coverage_cutoff_before_open():
    m = _mod()
    assert _digest(m, [])(8 * 60 + 50) == (0, 0, [])


def test_split_due_bars():
    m = _mod()
    ts = ["12:20", "12:25", "12:26", "12:27", "15:08"]
    due, later = m.split_due_bars(ts, 12 * 60 + 27)
    assert due == ["12:20", "12:25"]
    assert later == ["12:26", "12:27", "15:08"]
    # 장후(None)는 전부 확정 대상 — 종전 동작
    assert m.split_due_bars(ts, None) == (ts, [])


def test_wiring_uses_same_cutoff():
    src = io.open(_PATH, encoding="utf-8").read()
    assert src.count("dg.minute_coverage(_cov_upto)") == 2      # 표 + 적신호
    assert "_cov_upto = live_cutoff_min(phase, day, _closed)" in src
    assert "bar_gap_section(root, cfg, day, L, upto_min=_cov_upto)" in src
    # 뺀 분·봉을 숨기지 않는다(계측 4원칙 ③)
    assert "**미도래**라 제외" in src
    assert "미도래 **%d봉**" in src
