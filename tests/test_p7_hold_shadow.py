# -*- coding: utf-8 -*-
"""[사전등록 P7] 홀딩 섀도 — 회귀 테스트.

근거: `Peter/피터유튭/피터리_결합모델_P5P6_20260920.md` §9 ·
      `docs/사전등록/P7_홀딩섀도_20260920.md`

지키려는 불변식은 다섯이다.

  ① **롱에는 적용하지 않는다** — 실측에서 상승일 −2.1p / 하락일 −4.7p 로 양 국면 모두 음수.
     이 테스트가 깨지면 누군가 롱을 켠 것이다.
  ② **진 거래는 손대지 않는다** — 추가 위험 0 이 이 규칙의 존재 이유다.
  ③ **잔량 스톱은 본전이다** — 잔량 손익의 하한이 0 이어야 한다.
  ④ **목표는 다음 구조레벨이다** — 임의 배수(W×k)로 바꾸면 안 된다(v2 에서 기각됐다).
  ⑤ **관측 전용** — 매매 경로가 이 모듈을 읽지 않고, 쓰기는 전용 DB 한 곳뿐이다.

Python 3.7.13 32-bit(py37_32)에서 돌아야 한다 — 3.8+ 문법을 쓰면 런타임에서 죽는다.
"""

import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts import p7_hold_shadow_eod as P7  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ─────────────────────────────────────────── ④ 목표 = 다음 구조레벨
def test_next_level_long_picks_nearest_above():
    lv = [1030.0, 1040.0, 1050.0, 1060.0]
    assert P7.next_level(lv, 1042.0, 1) == 1050.0


def test_next_level_short_picks_nearest_below():
    lv = [1030.0, 1040.0, 1050.0, 1060.0]
    assert P7.next_level(lv, 1042.0, -1) == 1040.0


def test_next_level_returns_none_at_edge():
    lv = [1030.0, 1040.0]
    assert P7.next_level(lv, 1050.0, 1) is None
    assert P7.next_level(lv, 1020.0, -1) is None


# ─────────────────────────────────────────── ③ 잔량 스톱은 본전
def _bars(seq, start="10:00"):
    """(hhmm, high, low, close) 목록을 (고,저,종) 3튜플 나열로 만든다."""
    hh, mm = int(start[:2]), int(start[3:])
    out = []
    for hi, lo, cl in seq:
        out.append(("%02d:%02d" % (hh, mm), hi, lo, cl))
        mm += 1
        if mm == 60:
            hh, mm = hh + 1, 0
    return out


def test_hold_breakeven_stop_caps_loss_at_zero_short():
    # 숏 진입 1050, 가격이 되올라 1050 을 건드린다 → 본전 0
    bars = _bars([(1048, 1046, 1047), (1051, 1047, 1050)])
    pnl, outcome = P7.simulate_hold(bars, 1050.0, -1, "10:00", 1040.0)
    assert outcome == "BREAKEVEN"
    assert pnl == 0.0


def test_hold_breakeven_stop_caps_loss_at_zero_long():
    bars = _bars([(1052, 1051, 1051), (1053, 1049, 1050)])
    pnl, outcome = P7.simulate_hold(bars, 1050.0, 1, "10:00", 1060.0)
    assert outcome == "BREAKEVEN"
    assert pnl == 0.0


def test_hold_target_hit_short():
    bars = _bars([(1048, 1046, 1047), (1044, 1039, 1040)])
    pnl, outcome = P7.simulate_hold(bars, 1050.0, -1, "10:00", 1040.0)
    assert outcome == "TARGET"
    assert pnl == pytest.approx(10.0)


def test_hold_pnl_never_below_zero_unless_time_exit():
    """본전 스톱이 걸린 이상, TARGET/BREAKEVEN 결말의 손익은 음수가 될 수 없다."""
    cases = [
        ([(1048, 1046, 1047), (1051, 1047, 1050)], -1, 1040.0),
        ([(1048, 1046, 1047), (1044, 1039, 1040)], -1, 1040.0),
        ([(1052, 1051, 1051), (1053, 1049, 1050)], 1, 1060.0),
    ]
    for seq, side, tgt in cases:
        pnl, outcome = P7.simulate_hold(_bars(seq), 1050.0, side, "10:00", tgt)
        if outcome in ("TARGET", "BREAKEVEN"):
            assert pnl >= 0.0, (seq, side, outcome, pnl)


# ─────────────────────────────────────────── ①② 적용 대상 규칙
def test_long_is_always_excluded():
    """롱은 어떤 경우에도 적용 대상이 아니다 — 소스에 그 분기가 살아 있어야 한다."""
    src = open(os.path.join(ROOT, "scripts", "p7_hold_shadow_eod.py"),
               encoding="utf-8").read()
    assert 'row["skip_reason"] = "LONG_EXCLUDED"' in src
    assert re.search(r"if\s+side\s*==\s*1\s*:", src)


def test_loser_is_excluded():
    src = open(os.path.join(ROOT, "scripts", "p7_hold_shadow_eod.py"),
               encoding="utf-8").read()
    assert '"NOT_A_WINNER"' in src
    assert re.search(r'elif\s+e\["act"\]\s*<=\s*0\s*:', src)


def test_fraction_is_half():
    assert P7.FRAC == 0.5


# ─────────────────────────────────────────── ⑤ 관측 전용
def test_writes_only_to_dedicated_db():
    """쓰기 대상이 p7_shadow.db 하나뿐이어야 한다."""
    src = open(os.path.join(ROOT, "scripts", "p7_hold_shadow_eod.py"),
               encoding="utf-8").read()
    # 쓰기 연결은 save() 안의 한 줄뿐
    writes = re.findall(r"sqlite3\.connect\((?!\"file:)", src)
    assert len(writes) == 1, "쓰기 연결이 늘었다: %d" % len(writes)
    assert "sqlite3.connect(SHADOW_DB" in src
    # 원본 DB 는 전부 read-only
    for db in ("RAW_DATA_DB", "TRADES_DB", "PREMARKET_DB"):
        assert ("_ro(%s)" % db) in src, db


def test_trading_path_does_not_import_this_module():
    """main.py / config / 주문 경로가 이 모듈을 읽으면 안 된다."""
    hits = []
    for base in ("main.py", "config", "core", "execution", "strategy"):
        p = os.path.join(ROOT, base)
        files = []
        if os.path.isfile(p):
            files = [p]
        elif os.path.isdir(p):
            for dirpath, _, names in os.walk(p):
                files += [os.path.join(dirpath, n) for n in names if n.endswith(".py")]
        for f in files:
            try:
                txt = open(f, encoding="utf-8", errors="ignore").read()
            except OSError:
                continue
            if "p7_hold_shadow" in txt:
                hits.append(f)
    assert not hits, "매매 경로가 P7 섀도를 참조한다: %s" % hits


def test_intraday_guard_is_wired():
    src = open(os.path.join(ROOT, "scripts", "p7_hold_shadow_eod.py"),
               encoding="utf-8").read()
    assert "guard_intraday(" in src
