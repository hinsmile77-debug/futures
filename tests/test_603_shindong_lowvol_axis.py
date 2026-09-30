# -*- coding: utf-8 -*-
"""[MW0602 603차] 채점표 「R3 분리」 저변동(횡보 예보) 진입 축 — 기록만, 판정 아님.

근거: docs/신동거래/신동_횡보구간_방어전략_딥다이브_MW0602-20260930.md §3·§5-3.
"""
import importlib.util
import json
import os
import sqlite3
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from strategy.shindong import spec  # noqa: E402


def _scorecard():
    sp = importlib.util.spec_from_file_location(
        "shindong_scorecard", os.path.join(_ROOT, "scripts", "shindong_scorecard.py"))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def _dbs(tmp_path, rv_by_min, bars, atr14):
    """raw_features(realized_vol_ann) · raw_candles(high/low) · premarket_levels(atr14) 최소 스키마."""
    raw = str(tmp_path / "raw.db")
    con = sqlite3.connect(raw)
    con.execute("CREATE TABLE raw_candles (ts TEXT, open REAL, high REAL, low REAL, close REAL)")
    con.execute("CREATE TABLE raw_features (ts TEXT, features TEXT)")
    for hm, (h, l) in bars.items():
        con.execute("INSERT INTO raw_candles VALUES (?,?,?,?,?)", ("2026-09-30 %s:00" % hm, h, h, l, l))
    for hm, rv in rv_by_min.items():
        con.execute("INSERT INTO raw_features VALUES (?,?)",
                    ("2026-09-30 %s:00" % hm, json.dumps({"realized_vol_ann": rv})))
    con.commit()
    con.close()
    lv = str(tmp_path / "levels.db")
    con = sqlite3.connect(lv)
    con.execute("CREATE TABLE premarket_levels (date TEXT, stage TEXT, atr14 REAL)")
    if atr14 is not None:
        con.execute("INSERT INTO premarket_levels VALUES (?,?,?)", ("2026-09-30", "0850", atr14))
    con.commit()
    con.close()
    return raw, lv


def _t(rule="R3", ent="10:30", **kw):
    d = {"variant": "MAIN", "trade_date": "2026-09-30", "rule": rule, "side": -1, "status": "CLOSED",
         "entry_ts": "2026-09-30 %s:00" % ent, "entry_px": 1090.0, "touch_level": 1092.0, "net_krw": 1000.0}
    d.update(kw)
    return d


def test_lowvol_by_realized_vol(tmp_path):
    sc = _scorecard()
    # 범위는 넓고(0.5×ATR14) rv 만 문턱 아래 → True
    bars = {"%02d:%02d" % (9 + (i + 31) // 60, (i + 31) % 60): (1100.0 + (i % 2) * 15.0, 1100.0) for i in range(60)}
    raw, lv = _dbs(tmp_path, {"10:30": spec.LOWVOL_RV_MAX - 0.01}, bars, atr14=30.0)
    ctx = sc._lowvol_ctx(raw, lv)
    assert sc._is_lowvol(_t(), ctx) is True
    for c in ctx:
        c.close()


def test_lowvol_by_range_only_and_false(tmp_path):
    sc = _scorecard()
    # rv 는 문턱 위, 60분 범위 6pt ≤ 0.30×30 = 9pt → True
    bars = {"%02d:%02d" % (9 + (i + 31) // 60, (i + 31) % 60): (1103.0, 1097.0) for i in range(60)}
    raw, lv = _dbs(tmp_path, {"10:30": spec.LOWVOL_RV_MAX + 5.0}, bars, atr14=30.0)
    ctx = sc._lowvol_ctx(raw, lv)
    assert sc._is_lowvol(_t(), ctx) is True
    for c in ctx:
        c.close()
    # 둘 다 아님 → False (범위 20pt > 9pt · rv 문턱 위)
    bars2 = {k: (1110.0, 1090.0) for k in bars}
    (tmp_path / "b").mkdir()
    raw2, lv2 = _dbs(tmp_path / "b", {"10:30": spec.LOWVOL_RV_MAX + 5.0}, bars2, atr14=30.0)
    ctx = sc._lowvol_ctx(raw2, lv2)
    assert sc._is_lowvol(_t(), ctx) is False
    for c in ctx:
        c.close()


def test_lowvol_unmeasured_is_none(tmp_path):
    """미측정 ≠ 정상 변동(계측 4원칙 ②) — 원천이 없으면 None."""
    sc = _scorecard()
    assert sc._is_lowvol(_t(), (None, None)) is None
    assert sc._is_lowvol(_t(), None) is None
    # 피처 없음 + ATR14 없음(범위를 ATR 로 못 재) → None
    bars = {"10:%02d" % i for i in range(10, 31)}
    raw, lv = _dbs(tmp_path, {}, {k: (1100.0, 1099.0) for k in bars}, atr14=None)
    ctx = sc._lowvol_ctx(raw, lv)
    assert sc._is_lowvol(_t(), ctx) is None
    # R2 · entry_ts 없음 → None
    assert sc._is_lowvol(_t(rule="R2"), ctx) is None
    assert sc._is_lowvol(_t(entry_ts=None), ctx) is None
    for c in ctx:
        c.close()


def test_split_section_renders_lowvol_rows(tmp_path):
    sc = _scorecard()
    days = [{"variant": "MAIN", "trade_date": "2026-09-30", "bias": -1, "r2_status": "CONFIRMED"}]
    bars = {"%02d:%02d" % (9 + (i + 31) // 60, (i + 31) % 60): (1103.0, 1097.0) for i in range(120)}
    raw, lv = _dbs(tmp_path, {"10:30": 10.0, "11:20": 40.0}, bars, atr14=30.0)
    ctx = sc._lowvol_ctx(raw, lv)
    live = [_t(ent="10:30", net_krw=+300000.0),                        # rv 10 → 저변동
            _t(ent="11:20", net_krw=-100000.0, entry_px=1095.0)]         # rv 40 · 범위 6pt ≤ 9pt → 저변동(범위)
    out = "\n".join(sc._r3_split_section(live, days, ctx))
    for c in ctx:
        c.close()
    assert "저변동 진입" in out
    assert "| 2 | 1 | 50% | +200,000 |" in out          # 저변동 2건
    assert "| 정상 변동 진입 | 0 | 0 | - | +0 | - |" in out
    assert "변동성 미측정" not in out
    assert "게이트가 아니다" in out                        # 판정 아님 문구
    # ctx 없이 부르면 전부 미측정으로 표시(0 으로 위장하지 않는다)
    out2 = "\n".join(sc._r3_split_section(live, days, None))
    assert "| 변동성 미측정(피처·봉·ATR14 없음) | 2 |" in out2


def test_spec_constants_registered():
    """상수가 바뀌면 문서·주석을 함께 갱신해야 한다 — 실측 하위 1/3 값을 고정한다."""
    assert spec.LOWVOL_RV_MAX == 24.29
    assert spec.LOWVOL_RANGE60_ATR_MULT == 0.30
    assert spec.LOWVOL_RANGE_BARS == 60
