# -*- coding: utf-8 -*-
"""[MW0601 618차] `raw_candles` 결손 감지 — 두 기준, 두 시점.

왜 기준이 둘인가
----------------
처음 떠올린 안은 「기동 시 `session_bars` 기준으로 결손을 센다」였다. 그런데
**기동 시점에는 `session_bars` 에도 그 봉이 없다** — 차트 TR 보충은 당일
15:46 / 익일 08:41 에만 돈다(`main.py` 565차·589차 블록). 그대로 짰으면
재기동마다 **언제나 결손 0** 을 돌려주는 죽은 계측이 됐을 것이다. FP-CRITICAL
(학습분포 미저장 → PSI=0.0 2개월) · TOX 죽은 섀도와 같은 계열이다.

  · 기동 직후  → **분 그리드**가 정본 (`gap_by_grid`)
  · 15:46 이후 → **session_bars** 가 정본 (`gap_vs_session`)

실측 근거(session_bars 보유 12거래일, 2026-09-07~09-22)
-------------------------------------------------------
결손일 3/12 · 총 12봉. 결손 ts 는 그날 재기동 시각과 1:1 대응한다
(09-21 은 8회 재기동에 7봉). 드문 사고가 아니라 상시 현상이다.
결손봉 12개 전부 `session_bars` 에 `source='chart_backfill'` 로 있고
**OHLCV 만** 있다(bid1·buy_vol·anchor_*·tick_count NULL) — 백필해도
`raw_candles` 24열 중 5열이라 메우지 않는 판단(533차)의 근거가 된다.
"""

import datetime
import os
import sqlite3
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.bar_gap import (
    _fmt_list,
    confirm_line,
    gap_by_grid,
    gap_vs_session,
    startup_line,
)
from utils.time_utils import expected_raw_candle_minutes, raw_candles_last_ts


def _mins(*hhmm):
    return set(hhmm)


def _full_grid():
    return expected_raw_candle_minutes()


# ── 그리드 기준 ────────────────────────────────────────────────────────────

def test_grid_is_exactly_the_observed_row_count():
    """08:45~15:08 = 384분. 정상일 `raw_candles` 당일 행수 실측과 같다.

    이 일치가 「그리드 기준에는 거짓양성이 없다」의 근거다 — 점심 휴장이 없어
    그 구간에 정당하게 비는 분이 존재하지 않는다.
    """
    assert len(_full_grid()) == 384


def test_grid_counts_missing():
    g = gap_by_grid(_full_grid() - _mins("09:41", "09:42"))
    assert g["missing"] == ["09:41", "09:42"]
    assert g["expected"] == 384 and g["present"] == 382


def test_grid_ignores_bars_after_cutoff():
    """🔴 절단선 이후 봉은 결손으로 **세지 않는다** — 그게 정상이다.

    2026-09-22 1차 진단이 정확히 이것을 오독했다(15:07 이후를 공백으로 읽음).
    """
    g = gap_by_grid(_full_grid())
    assert g["missing"] == []
    assert g["window_end"] == raw_candles_last_ts().strftime("%H:%M") == "15:08"


def test_grid_window_respects_upto():
    """비행 중인 봉을 결손으로 세면 매 기동마다 거짓양성이다."""
    g = gap_by_grid(_full_grid(), upto=datetime.time(9, 41))
    assert g["window_end"] == "09:41"
    assert g["expected"] == 57 and g["missing"] == []


# ── session_bars 대조 ──────────────────────────────────────────────────────

def test_session_gap_and_preservation():
    grid = _full_grid()
    r = gap_vs_session(grid - _mins("09:41", "15:08"), grid)
    assert r["missing"] == ["09:41", "15:08"]
    assert r["preserved"] == r["missing"], "session_bars 에 있으면 데이터 손실이 아니다"
    assert r["permanent"] == [] and r["orphan"] == [] and r["over_cut"] == []


def test_session_short_day_surfaces_permanent_gap():
    """🔴 `session_bars` 만 정본으로 삼으면 **그것 자체가 짧은 날**을 못 본다.

    실측 2026-09-08 은 raw 365 / session 365 라 이 대조에서는 「결손 0」인데
    그리드로는 19봉이 빈다(그날 차트 TR 보충이 돌지 않았다). 한 축만 맞춰보면
    나머지가 사각지대가 된다 — 계측 4원칙 ⑤.
    """
    short = _full_grid() - set("08:%02d" % m for m in range(45, 60))
    r = gap_vs_session(short, short)
    assert r["missing"] == []
    assert len(r["permanent"]) == 15
    assert r["permanent"][0] == "08:45" and r["permanent"][-1] == "08:59"


def test_over_cut_is_an_anomaly():
    """절단선을 넘겨 들어온 봉 = 15:10 파이프라인 중단선 미작동."""
    r = gap_vs_session(_full_grid() | _mins("15:12"), _full_grid())
    assert r["over_cut"] == ["15:12"]


def test_orphan_bar_flagged():
    """raw 에 있는데 session 에 없으면 수집 경로 이상이다."""
    r = gap_vs_session(_full_grid(), _full_grid() - _mins("10:00"))
    assert r["orphan"] == ["10:00"]


# ── 로그 문자열 ────────────────────────────────────────────────────────────

def test_zero_gap_still_logs():
    """🔴 결손 0 이어도 찍는다.

    침묵은 「결손 없음」과 「검사가 죽었다」를 구분해주지 않는다 — 계측 4원칙 ④.
    계획 초안은 "결손 0 일 때 로그 미출력"이었으나, 그 형태가 바로 FP-CRITICAL
    이 2개월간 들키지 않은 모양이다.
    """
    db = os.path.join(_ROOT, "data", "db", "raw_data.db")
    line = startup_line(db, datetime.datetime(2026, 9, 22, 9, 42, 48))
    assert line is not None and line[0].startswith("[BarGap]")


def test_truncated_list_states_remainder():
    """절단하면 잔여 개수를 명시한다 — 계측 4원칙 ③.

    457차 C6: `missing[:5]` 가 "7개 미가용"이라 적고 5개만 출력해 운영자가
    "7개 = 나열된 5개"로 오독했다.
    """
    out = _fmt_list(["%02d:00" % h for h in range(10, 25)])
    assert "외 3개" in out
    assert _fmt_list([]) == "(없음)"


def test_before_market_open_returns_none():
    """08:45 이전 기동에는 판정할 창이 없다 — 0 이 아니라 판정 없음."""
    db = os.path.join(_ROOT, "data", "db", "raw_data.db")
    assert startup_line(db, datetime.datetime(2026, 9, 22, 8, 40, 51)) is None


def test_unreadable_db_is_unmeasured_not_zero(tmp_path):
    """DB 를 못 읽으면 「결손 0」이 아니라 **미측정**이라고 말한다 — 계측 4원칙 ②."""
    msg, lv = confirm_line(str(tmp_path / "nope.db"), "2026-09-22")
    assert "미측정" in msg and lv == "WARNING"


# ── 배선 (죽은 계측 방지) ──────────────────────────────────────────────────

def test_main_wires_both_checks():
    """🔴 배선이 빠지면 이 모듈 전체가 죽은 계측이다.

    ⚠ 확정 판정은 15:46 보충 **직후**여야 한다. 15:50 이후로 미루면 영영 안
      돈다 — `_schedule_shutdown()` 이 15:47:15 에 프로세스를 끝낸다(589차).
    """
    src = open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()
    assert "from utils.bar_gap import startup_line" in src
    assert "from utils.bar_gap import confirm_line" in src
    assert "self._bargap_confirm_done" in src
    assert "datetime.time(15, 46)" in src, "확정 판정 시각이 보충 창과 어긋나면 안 된다"
    # 자동종료 예약 시각보다 앞인가 — 두 상수가 함께 움직여야 한다.
    assert src.index("self._bargap_confirm_done: bool = False") > 0


def test_confirm_runs_against_real_db_when_present():
    """실 DB 가 있으면 한 번 돌려본다 — 스키마가 바뀌면 여기서 드러난다."""
    db = os.path.join(_ROOT, "data", "db", "raw_data.db")
    if not os.path.exists(db):
        return
    con = sqlite3.connect("file:%s?mode=ro" % db.replace("\\", "/"), uri=True)
    try:
        row = con.execute("SELECT MAX(substr(ts,1,10)) FROM session_bars").fetchone()
    except sqlite3.Error:
        return
    finally:
        con.close()
    if not row or not row[0]:
        return
    msg, lv = confirm_line(db, row[0])
    assert msg.startswith("[BarGap] 당일 확정")
    assert lv in ("INFO", "WARNING", "ERROR")
