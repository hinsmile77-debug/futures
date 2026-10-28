# -*- coding: utf-8 -*-
"""[MW0601 725차 후속10] 신동2 2026-10-28 검토 3건 — 08:45 시가 두 값 · 대기 계획 manage 표기 · 15:12 질문 종결.

고정하는 것
-----------
A. 장중 08:45 시가 — raw_candles 첫 틱 시가(905.34)를 08:50 맥점의 차트 개장가(904.68)로 덮는다. 보정값이 없으면 「보정 전」 꼬리표.
B. manage 대상 — 보유(position) / 미체결 대기(pending) 를 기록에 남기고, 둘 다 없으면 거부. 문서가 「시장가」로 찍지 않는다.
C. 러너 — 프롬프트에 HEADLESS 고지 · close 회차 마감 note 사후 검사 · 질문 종결 경고 · 파일 ASCII 유지.
D. 사다리 — manage 표기가 대상을 구분한다.

실행: conda run -n py37_32 python -m pytest tests/test_725g_shindong2_open_manage_headless.py -v
"""
import datetime as dt
import os
import sqlite3
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))
sys.path.insert(0, os.path.join(_ROOT, "tools", "maekjeom_ladder"))
import ladder_data as L  # noqa: E402
import shindong2_live as M  # noqa: E402

DAY = "2026-10-28"


def _bars(prices, start="09:00"):
    h, m = map(int, start.split(":"))
    out = []
    for i, (o, hi, lo, c) in enumerate(prices):
        t = h * 60 + m + i
        out.append(["%02d:%02d" % (t // 60, t % 60), o, hi, lo, c])
    return out


def _rec(ts, **kw):
    r = dict(id=ts, ts="%sT%s" % (DAY, ts), phase="intraday", action="plan", variant="live")
    r.update(kw)
    return r


def _levels_db(tmp_path, open_price=904.68, bar_ts="08:45"):
    con = sqlite3.connect(str(tmp_path / "premarket_levels.db"))
    con.execute("CREATE TABLE premarket_levels (date TEXT, stage TEXT, open_price REAL, open_bar_ts TEXT)")
    if open_price is not None:
        con.execute("INSERT INTO premarket_levels VALUES (?,?,?,?)", (DAY, "0850", open_price, bar_ts))
    con.commit(); con.close()


# ── A. 08:45 시가 ─────────────────────────────────────────────────────────
def test_live_open_fixed_from_0850_levels(tmp_path, monkeypatch):
    _levels_db(tmp_path)
    monkeypatch.setattr(L, "DB", str(tmp_path))
    rows = [["08:45", 905.34, 905.68, 904.18, 904.18], ["08:46", 904.18, 905.34, 904.10, 904.10]]
    out, tag = L._live_open_fix(DAY, rows)
    assert out[0] == ["08:45", 904.68, 905.68, 904.18, 904.18]          # 10-28 실측 — 종가·나머지 봉 유지
    assert out[1] == rows[1] and rows[0][1] == 905.34                    # 원본(캐시)은 건드리지 않는다
    assert "905.34→904.68" in tag
    out2, _ = L._live_open_fix(DAY, [["08:45", 903.0, 903.5, 903.0, 903.2]])
    assert out2[0][2] == 904.68 and out2[0][3] == 903.0                  # 고가는 개장가를 포함하도록 넓힌다


def test_live_open_unfixed_is_tagged_not_silent(tmp_path, monkeypatch):
    _levels_db(tmp_path, open_price=None)
    monkeypatch.setattr(L, "DB", str(tmp_path))
    rows = [["08:45", 905.34, 905.68, 904.18, 904.18]]
    out, tag = L._live_open_fix(DAY, rows)
    assert out == rows and "보정 전" in tag                               # 계측 4원칙 ④ — 폴백 가시화
    assert L._live_open_fix(DAY, [["08:46", 1, 1, 1, 1]])[1] == ""        # 08:45 봉이 없으면 손대지 않는다


def test_live_open_fix_without_open_bar_ts_column(tmp_path, monkeypatch):
    # Sindong-V4(MW0602) premarket_levels 에는 open_bar_ts 열이 없다 — 「보정 전」으로 떨어지지 말고 표기를 달아 보정한다
    con = sqlite3.connect(str(tmp_path / "premarket_levels.db"))
    con.execute("CREATE TABLE premarket_levels (date TEXT, stage TEXT, open_price REAL)")
    con.execute("INSERT INTO premarket_levels VALUES (?,?,?)", (DAY, "0850", 904.68))
    con.commit(); con.close()
    monkeypatch.setattr(L, "DB", str(tmp_path))
    out, tag = L._live_open_fix(DAY, [["08:45", 905.34, 905.68, 904.18, 904.18]])
    assert out[0][1] == 904.68 and "open_bar_ts 미기록" in tag


def test_candles_live_path_carries_tag(tmp_path, monkeypatch):
    _levels_db(tmp_path)
    monkeypatch.setattr(L, "DB", str(tmp_path))
    monkeypatch.setattr(L, "_candles_live", lambda d: ([["08:45", 905.34, 905.68, 904.18, 904.18]], "raw_candles(live)"))
    rows, src = L.candles(DAY, live=True)
    assert rows[0][1] == 904.68 and src.startswith("raw_candles(live)") and "차트 보정" in src


# ── B. manage 대상 ────────────────────────────────────────────────────────
def test_manage_target_pending_position_none():
    cs = _bars([(940, 947, 939, 946)] * 5, start="12:28")            # 932.9 되돌림 없음 — 10-28 12:30 무렵
    plan = _rec("11:03:57", dir="매수", entry=932.9, stop=929.5, target=946.0)
    assert M.manage_target(DAY, [plan], cs=cs) == ("pending", 932.9)
    mkt = _rec("12:20:00", dir="매수", entry=None, stop=930.0, target=960.0)
    assert M.manage_target(DAY, [mkt], cs=cs)[0] == "position"
    stand = _rec("12:20:00", action="stand", dir="관망")
    assert M.manage_target(DAY, [plan, stand], cs=cs) == ("none", None)
    fresh = _rec("12:32:30", dir="매수", entry=935.0, stop=930.0, target=950.0)   # 효력 12:33 — 아직 봉에 안 닿았다
    assert M.manage_target(DAY, [fresh], cs=cs) == ("pending", 935.0)


def test_record_manage_writes_target_and_label(tmp_path, monkeypatch):
    monkeypatch.setattr(M, "LIVE_DIR", str(tmp_path / "live"))
    monkeypatch.setattr(M, "DOC_DIR", str(tmp_path / "doc"))
    cs = _bars([(940, 947, 939, 946)] * 5, start="12:28")
    monkeypatch.setattr(L, "is_live", lambda d, now=None: False)
    monkeypatch.setattr(L, "candles", lambda d, live: (cs, "test"))
    t0 = dt.datetime(2026, 10, 28, 11, 3, 57)
    M.record(DAY, "intraday", "plan", "매수", 932.9, 929.5, 946.0, "되돌림 대기", now=t0)
    rec = M.record(DAY, "intraday", "manage", "매수", None, 929.5, 950.0, "목표 950", now=dt.datetime(2026, 10, 28, 12, 34, 11))
    assert rec["on"] == "pending" and rec["pending_entry"] == 932.9
    doc = open(M._doc_path(DAY), encoding="utf-8").read().split("## 12:34")[1]
    assert "대기 주문 수정" in doc and "시장가" not in doc


def test_record_manage_without_target_is_refused(tmp_path, monkeypatch):
    monkeypatch.setattr(M, "LIVE_DIR", str(tmp_path / "live"))
    monkeypatch.setattr(M, "DOC_DIR", str(tmp_path / "doc"))
    monkeypatch.setattr(L, "is_live", lambda d, now=None: False)
    monkeypatch.setattr(L, "candles", lambda d, live: (_bars([(940, 941, 939, 940)] * 3, start="12:30"), "test"))
    with pytest.raises(SystemExit):
        M.record(DAY, "intraday", "manage", "매수", None, 929.5, 950.0, "x", now=dt.datetime(2026, 10, 28, 12, 34))
    assert M.load_ai_log(DAY) == []                                     # 거부는 기록을 남기지 않는다


def test_manage_label_legacy_records():
    assert "대상 미기록" in M.manage_label(dict(action="manage"))      # 10-28 이전 기록 — 소급 추정하지 않는다
    assert "보유 관리" in M.manage_label(dict(on="position"))


# ── C. 러너 ───────────────────────────────────────────────────────────────
def test_runner_headless_prompt_and_postchecks():
    raw = open(os.path.join(_ROOT, "scripts", "shindong2_run.ps1"), "rb").read()
    assert all(b < 128 for b in raw)                                    # PS 5.1 — BOM 없는 파일은 ANSI 로 읽힌다
    src = raw.decode("ascii")
    assert src.count("HEADLESS") >= 2 and "Never end with a question" in src
    assert "WARN ended with question" in src and "WARN no wrap-up note after 15:10" in src


# ── D. 사다리 ─────────────────────────────────────────────────────────────
def test_ladder_manage_label_distinguishes_target():
    html = open(os.path.join(_ROOT, "tools", "maekjeom_ladder", "ladder.html"), encoding="utf-8").read()
    assert "function manageLabel(r)" in html and "대기 주문 수정" in html
    assert '<span class="k-sd2ai">갱신</span>' not in html
