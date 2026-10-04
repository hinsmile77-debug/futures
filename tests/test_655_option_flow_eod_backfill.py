# -*- coding: utf-8 -*-
"""[MW0601 655차] 옵션 흐름(7222) 장 마감 재수집이 **조용히 실패하지 않게** 하는 장치들의 회귀 가드.

사건 (2026-10-04 발견)
---------------------
· 라이브 수집은 수급 타이머에 얹혀 `is_market_open()`(15:35)에서 막히고 15:40 `daily_close`
  에서 멈춘다 → 매일 **15:34 행이 덜 찬 채 굳고 15:35 – 16:07 행이 없다.**
  HTS [7222] 실측 2026-10-02 (월)위클리 콜 개인: 최종 −96(16:07) vs DB −226(15:34).
· 그 구간을 메우는 예약작업 `Mireuk_OptionFlowBackfill_1605` 는 2026-09-21 등록 이래
  **8거래일 전부 실패**(LastTaskResult=2). MW0601 Cybos 는 비승격인데 작업은 Highest 라
  COM 이 미접속 DibServer 를 띄웠다. 예약작업은 출력을 남기지 않았고 결과를 보는 눈도 없었다.
· 덤으로 `--date` 가 저장 라벨만 바꿔 **지난 날짜를 오늘 값으로 덮어쓸 수 있는** 경로가 있었다.

이 파일이 고정하는 것
--------------------
A. 신선도 검사 — 마감 구간 미확보·행 없음을 잡고, 오늘·수집 이전·현물을 기준에서 빼고,
   못 읽으면 「결손 0」이 아니라 미측정이라 말한다.
B. 백필 — 다른 날짜 거부, 미접속 시 권한 수준 진단, 마감 구간 판정(만기일 포함), 실행 로그.
C. 예약작업 등록 — 실행주체를 BROKER 로 정하고, 기본 시각이 16:07 행 뒤다.
D. EOD 체인 배선 — 재학습 try 앞에 [OptionFlowFresh] 가 있다.

실행:
    conda run -n py37_32 python -m pytest tests/test_655_option_flow_eod_backfill.py -v
"""
import datetime as dt
import os
import sqlite3
import sys
import types

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
os.environ["MIREUK_TEST_MODE"] = "1"

from scripts import option_flow_freshness as fresh  # noqa: E402

_PS1 = os.path.join(_ROOT, "scripts", "option_flow_backfill_task.ps1")
_BAT = os.path.join(_ROOT, "TASK_OPTION_BACKFILL_INSTALL.bat")
_EOD = os.path.join(_ROOT, "retrain_eod.py")
_BACKFILL = os.path.join(_ROOT, "scripts", "backfill_option_flow.py")


def _src(p):
    with open(p, "r", encoding="utf-8-sig") as f:
        return f.read()


# ── 픽스처: 임시 raw_data.db / option_flow.db ─────────────────────────────
def _mk_raw(path, days, bars=30):
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE raw_candles (ts TEXT PRIMARY KEY, close REAL)")
    for d in days:
        for i in range(bars):
            con.execute("INSERT INTO raw_candles VALUES (?, 1.0)", ("%s 09:%02d:00" % (d, i), ))
    con.commit(); con.close()


def _mk_flow(path, rows):
    """rows: [(trade_date, bar_time, product)]"""
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE option_investor_flow (trade_date TEXT, bar_time TEXT, product TEXT,"
                " market_code TEXT, investor TEXT, sell_qty INT, buy_qty INT, net_qty INT, net_amt INT,"
                " collected_at TEXT, PRIMARY KEY (trade_date, bar_time, product, investor))")
    for d, t, p in rows:
        con.execute("INSERT INTO option_investor_flow VALUES (?,?,?,'x','individual',0,0,0,0,'-')", (d, t, p))
    con.commit(); con.close()


@pytest.fixture
def dbs(tmp_path):
    return str(tmp_path / "raw.db"), str(tmp_path / "flow.db")


NOW = dt.datetime(2026, 10, 6, 15, 50)      # 화요일 EOD 체인 시각


# ── A. 신선도 검사 ────────────────────────────────────────────────────────
def test_close_reached_is_ok(dbs):
    raw, flow = dbs
    _mk_raw(raw, ["2026-10-02"])
    _mk_flow(flow, [("2026-10-02", "16:07", "wk_mon_call")])
    r = fresh.check(days=10, flow_db=flow, raw_db=raw, now=NOW)
    assert r["status"] == "ok", r["line"]
    assert r["line"].startswith("[OptionFlowFresh] 마감 구간 확보")


def test_stuck_at_1534_is_flagged(dbs):
    """사고의 지문 — 최신봉 15:34 에서 멈춘 날."""
    raw, flow = dbs
    _mk_raw(raw, ["2026-10-01", "2026-10-02"])
    _mk_flow(flow, [("2026-10-01", "15:34", "mon_call"), ("2026-10-02", "16:07", "mon_put")])
    r = fresh.check(days=10, flow_db=flow, raw_db=raw, now=NOW)
    assert r["status"] == "missing"
    assert r["bad"] == [("2026-10-01", "최신봉 15:34")]
    assert "복구 불가" in r["line"]                 # 헛수고 방지 — 7222 는 당일만 준다


def test_day_without_rows_is_flagged(dbs):
    raw, flow = dbs
    _mk_raw(raw, ["2026-10-01", "2026-10-02"])
    _mk_flow(flow, [("2026-10-02", "15:45", "mon_call")])
    r = fresh.check(days=10, flow_db=flow, raw_db=raw, now=NOW)
    assert r["bad"] == [("2026-10-01", "행 없음")]


def test_spot_rows_do_not_count_as_close(dbs):
    """kospi_spot 은 1–2분 불규칙 — 그 늦은 행이 옵션 마감 확보로 위장하면 안 된다."""
    raw, flow = dbs
    _mk_raw(raw, ["2026-10-02"])
    _mk_flow(flow, [("2026-10-02", "15:34", "mon_call"), ("2026-10-02", "16:00", "kospi_spot")])
    r = fresh.check(days=10, flow_db=flow, raw_db=raw, now=NOW)
    assert r["bad"] == [("2026-10-02", "최신봉 15:34")]


def test_today_excluded_before_settle_and_included_after(dbs):
    raw, flow = dbs
    _mk_raw(raw, ["2026-10-06"])
    _mk_flow(flow, [("2026-10-06", "15:34", "mon_call")])
    early = fresh.check(days=10, flow_db=flow, raw_db=raw, now=dt.datetime(2026, 10, 6, 15, 50))
    late = fresh.check(days=10, flow_db=flow, raw_db=raw, now=dt.datetime(2026, 10, 6, 17, 0))
    assert early["status"] == "unmeasured"           # 오늘만 있는데 빼면 기준선이 빈다 — 0 이 아니다
    assert late["status"] == "missing" and late["bad"] == [("2026-10-06", "최신봉 15:34")]


def test_days_before_collection_start_are_not_gaps(dbs):
    raw, flow = dbs
    _mk_raw(raw, ["2026-09-18", "2026-09-21"])
    _mk_flow(flow, [("2026-09-21", "15:45", "mon_call")])
    r = fresh.check(days=30, flow_db=flow, raw_db=raw, now=dt.datetime(2026, 9, 22, 16, 50))
    assert r["status"] == "ok" and r["n_ref"] == 1    # 9/18 은 「수집 이전」이지 결손이 아니다


def test_expiry_day_uses_early_close(dbs):
    """2026-10-08 은 10월물 만기일(15:20 조기 마감) — 평일 기준으로 보면 거짓 경보가 난다."""
    raw, flow = dbs
    assert fresh._close_ok_for("2026-10-08") == fresh.CLOSE_OK_EXPIRY
    assert fresh._close_ok_for("2026-10-07") == fresh.CLOSE_OK
    _mk_raw(raw, ["2026-10-07", "2026-10-08"])
    _mk_flow(flow, [("2026-10-07", "15:25", "mon_call"), ("2026-10-08", "15:25", "mon_call")])
    r = fresh.check(days=10, flow_db=flow, raw_db=raw, now=dt.datetime(2026, 10, 9, 15, 50))
    assert r["bad"] == [("2026-10-07", "최신봉 15:25")]


def test_unreadable_is_unmeasured_not_zero(dbs, tmp_path):
    raw, flow = dbs
    _mk_raw(raw, ["2026-10-02"])
    r = fresh.check(days=10, flow_db=str(tmp_path / "nope.db"), raw_db=raw, now=NOW)
    assert r["status"] == "unmeasured" and "결손 없음」이 아니다" in r["line"]


# ── B. 백필 스크립트 ──────────────────────────────────────────────────────
@pytest.fixture
def bf(monkeypatch):
    pytest.importorskip("win32com")             # py37_32 에서 돈다(import 시 collection.cybos 를 읽는다)
    import scripts.backfill_option_flow as m
    return m


def test_other_date_is_refused_and_writes_nothing(bf, monkeypatch, tmp_path):
    db = str(tmp_path / "flow.db")
    monkeypatch.setattr(sys, "argv", ["backfill", "--date", "2000-01-03", "--db", db, "--dry-run"])
    assert bf.main() == bf.EXIT_NOT_CONNECTED
    assert not os.path.exists(db)               # 라벨만 바꿔 덮어쓰는 경로가 닫혀 있다


def test_holiday_skips_before_touching_cybos(bf, monkeypatch, tmp_path):
    """휴장일에 COM 을 부르면 빈 DibServer 가 뜨고 「미접속(2)」이 진짜 실패와 섞인다."""
    called = []
    monkeypatch.setattr(bf, "require_cybos_connection", lambda: called.append(1) or "x")
    monkeypatch.setattr(bf, "_is_holiday", lambda now: True)
    monkeypatch.setattr(bf, "_open_run_log", lambda: None)          # 운영 logs/ 를 건드리지 않는다
    monkeypatch.setattr(sys, "argv", ["backfill", "--db", str(tmp_path / "flow.db")])
    assert bf.main() == 0
    assert called == []
    from utils.time_utils import is_trading_day
    assert not is_trading_day(dt.datetime(2026, 10, 5, 16, 20))   # 개천절 대체공휴일 — 달력이 안다


def test_not_connected_message_names_integrity_mismatch(bf, monkeypatch):
    fake = types.ModuleType("win32com.client")
    fake.Dispatch = lambda progid: types.SimpleNamespace(IsConnect=0)
    monkeypatch.setitem(sys.modules, "win32com.client", fake)
    msg = bf.require_cybos_connection()
    assert "IsConnect=0" in msg
    assert "승격" in msg and "RunLevel Limited" in msg and "RunLevel Highest" in msg


def test_close_check_verdicts(bf, tmp_path):
    db = str(tmp_path / "flow.db")
    _mk_flow(db, [("2026-10-02", "15:34", "mon_call"), ("2026-10-02", "16:00", "kospi_spot"),
                  ("2026-10-08", "15:25", "mon_call")])
    assert bf.close_check(db, "2026-10-02", "16:20")[0] is False      # 현물 행에 속지 않는다
    assert bf.close_check(db, "2026-10-02", "11:45")[0] is None       # 장중 메우기 — 판정 대상 아님
    assert bf.close_check(db, "2026-10-08", "16:20")[0] is True       # 만기일 15:20 기준
    _mk_flow(str(tmp_path / "ok.db"), [("2026-10-02", "16:07", "wk_mon_call")])
    assert bf.close_check(str(tmp_path / "ok.db"), "2026-10-02", "16:20")[0] is True


def test_run_log_is_written_with_explicit_encoding():
    """예약작업은 PYTHONUTF8 을 못 세운다 — 인코딩을 명시하지 않으면 로그가 통째로 사라진다(595차)."""
    s = _src(_BACKFILL)
    assert "_OPTION_BACKFILL.log" in s
    assert 'open(path, "a", encoding="utf-8")' in s
    assert "sys.stdout = _Tee(" in s


def test_close_threshold_has_single_source():
    s = _src(_BACKFILL)
    assert "from scripts.option_flow_freshness import CLOSE_OK, _close_ok_for" in s
    assert 'CLOSE_OK = "15:40"' not in s        # 두 곳에 두면 한쪽만 고쳐진다


# ── C. 예약작업 등록 ──────────────────────────────────────────────────────
def test_task_runlevel_follows_broker():
    s = _src(_PS1)
    assert "[string]$RunLevel   = ''" in s       # 기본값이 Highest 면 MW0601 사고가 되풀이된다
    assert "$Broker -eq 'cybos'" in s and "$RunLevel = 'Limited'" in s
    assert "$Broker -eq 'creon'" in s and "$RunLevel = 'Highest'" in s
    assert "추측으로 등록하지 않는다" in s


def test_task_default_time_is_after_last_7222_row():
    import re
    s = _src(_PS1)
    m = re.search(r"\[string\]\$Time\s*=\s*'(\d{1,2}):(\d{2})'", s)
    assert m, "기본 시각 선언을 못 찾음"
    assert (int(m.group(1)), int(m.group(2))) >= (16, 10), "7222 최종 행(16:07 실측)보다 뒤여야 한다"
    assert "[string]$From       = '08:46'" in s


def test_installer_bat_stays_pure_ascii():
    with open(_BAT, "rb") as f:
        b = f.read()
    assert not b.startswith(b"\xef\xbb\xbf"), ".bat 에 BOM 금지(603차)"
    assert all(c < 128 for c in b), ".bat 은 순수 ASCII(cmd 바이트 오프셋 추적)"


# ── D. EOD 체인 배선 ──────────────────────────────────────────────────────
def test_eod_chain_checks_option_flow_before_retrain():
    s = _src(_EOD)
    i_fresh = s.find("from scripts.option_flow_freshness import check")
    i_reg = s.find("from scripts.regular_freshness import check")
    i_retrain = s.find("t_start = time.perf_counter()")
    assert -1 not in (i_fresh, i_reg, i_retrain)
    assert i_reg < i_fresh < i_retrain, "재학습이 죽어도 판정은 남아야 한다 — 재학습 try 앞"
    assert "[OptionFlowFresh] 검사 실패 — 미측정이다" in s
