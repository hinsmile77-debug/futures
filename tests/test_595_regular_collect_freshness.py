# -*- coding: utf-8 -*-
"""[MW0601 595차] 정규 10100 수집이 **조용히 멈추지 않게** 하는 장치들의 회귀 가드.

사건
----
`regular_candles.db` 는 2026-09-11 하루 저녁의 손 백필 이후 **엿새간 갱신이 멈췄다**.
09-14·15·16 사흘 내내 EOD 는 매일 `LastTaskResult=0` 으로 성공했고 **어떤 경보도
울리지 않았다.** 트리거가 사람 손뿐이었고(배치 헤더가 스스로 "더블클릭"이라 적었다),
결손을 보는 눈이 어디에도 없었다.

그리고 복구하려고 python.exe 를 직접 돌리자 **두 번째 결함**이 드러났다 —
스크립트가 기본 인코딩을 UTF-8 이라 가정하는데, 그건 `.bat` 이 `PYTHONUTF8=1` 을
세워 줄 때만 참이었다. 그 차이로
  · `_flush()` 의 로그 쓰기가 터져 **그 실행의 로그가 통째로 사라졌고**
  · `mini_near_code()` 의 `UnicodeDecodeError` 가 `except: pass` 에 먹혀
    **「미니 코드를 못 찾음」으로 위장**돼 미니 수집이 조용히 빠졌다.

이 파일은 그 **지문**을 고정한다.

실행:
    conda run -n py37_32 python -m pytest tests/test_595_regular_collect_freshness.py -v
"""
import datetime as dt
import io
import os
import re
import sqlite3
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

os.environ["MIREUK_TEST_MODE"] = "1"

from scripts.regular_freshness import check  # noqa: E402

_SRC_COLLECT = os.path.join(_ROOT, "scripts", "collect_regular_futures.py")
_SRC_TASK_PS1 = os.path.join(_ROOT, "scripts", "regular_collect_task.ps1")
_SRC_BAT = os.path.join(_ROOT, "COLLECT_REGULAR_EOD.bat")
_SRC_EOD = os.path.join(_ROOT, "retrain_eod.py")


def _read(p):
    return io.open(p, encoding="utf-8-sig").read()


def _mk_raw(path, days, bars=400):
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE raw_candles (ts TEXT PRIMARY KEY, close REAL)")
    for d in days:
        for i in range(bars):
            con.execute("INSERT INTO raw_candles VALUES (?, 1.0)",
                        ("%s %02d:%02d:00" % (d, 9 + i // 60, i % 60),))
    con.commit()
    con.close()


def _mk_reg(path, days, code="10100"):
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE regular_candles (code TEXT, ts TEXT, trade_date TEXT,"
                " PRIMARY KEY (code, ts))")
    for d in days:
        con.execute("INSERT INTO regular_candles VALUES (?, ?, ?)",
                    (code, d + " 09:00:00", d))
    con.commit()
    con.close()


def _recent(n_from, n_to):
    """오늘에서 n_from 일 전 ~ n_to 일 전 (오름차순 날짜 문자열)."""
    today = dt.date.today()
    return [(today - dt.timedelta(days=i)).isoformat()
            for i in range(n_from, n_to - 1, -1)]


# ── 1) 결손 일자를 정확히 집어낸다 ────────────────────────────────────────
def test_1_missing_days_detected(tmp_path):
    days = _recent(5, 1)                      # 5일치 기준선
    raw = str(tmp_path / "raw.db")
    reg = str(tmp_path / "reg.db")
    _mk_raw(raw, days)
    _mk_reg(reg, days[:2])                    # 정규는 앞 2일만 적재됨

    res = check(days=10, reg_db=reg, raw_db=raw)
    assert res["status"] == "missing"
    assert res["missing_days"] == days[2:]
    assert res["latest"] == days[1]
    assert res["n_ref"] == 5
    # 복구 명령이 로그 한 줄에 들어 있어야 한다 — 사람이 바로 칠 수 있게
    assert "collect_regular_futures.py --from" in res["line"]


def test_1b_no_missing_when_complete(tmp_path):
    days = _recent(3, 1)
    raw = str(tmp_path / "raw.db")
    reg = str(tmp_path / "reg.db")
    _mk_raw(raw, days)
    _mk_reg(reg, days)

    res = check(days=10, reg_db=reg, raw_db=raw)
    assert res["status"] == "ok"
    assert res["missing_days"] == []
    assert "결손 0일" in res["line"]


def test_1c_short_session_excluded_from_reference(tmp_path):
    """봉이 min_bars 미만인 날은 기준선에서 뺀다 — 세션 파편으로 오탐하지 않는다."""
    full = _recent(2, 2)[0]
    frag = _recent(1, 1)[0]
    raw = str(tmp_path / "raw.db")
    reg = str(tmp_path / "reg.db")
    _mk_raw(raw, [full], bars=400)
    con = sqlite3.connect(raw)                # 파편 3봉짜리 하루를 덧붙인다
    for i in range(3):
        con.execute("INSERT INTO raw_candles VALUES (?, 1.0)",
                    ("%s 09:0%d:00" % (frag, i),))
    con.commit()
    con.close()
    _mk_reg(reg, [full])

    res = check(days=10, reg_db=reg, raw_db=raw, min_bars=10)
    assert res["status"] == "ok", res["line"]
    assert frag not in res["missing_days"]


# ── 2) 미측정 ≠ 결손 0 (계측 4원칙 ②) ────────────────────────────────────
def test_2_missing_db_is_unmeasured(tmp_path):
    raw = str(tmp_path / "raw.db")
    _mk_raw(raw, _recent(1, 1))
    res = check(days=10, reg_db=str(tmp_path / "no_such.db"), raw_db=raw)
    assert res["status"] == "unmeasured"
    assert res["missing_days"] == []           # 「0건」을 흉내내지 않는다
    assert "결손 0" not in res["line"]         # 정상과 같은 문구가 되면 안 된다
    assert "미측정" in res["line"]


def test_2b_empty_reference_is_unmeasured(tmp_path):
    """기준선이 비면 「결손 0」이 아니라 **잴 수 없음**이다."""
    raw = str(tmp_path / "raw.db")
    reg = str(tmp_path / "reg.db")
    _mk_raw(raw, ["2000-01-03"])               # 창 밖 — 기준선이 빈다
    _mk_reg(reg, ["2000-01-03"])
    res = check(days=10, reg_db=reg, raw_db=raw)
    assert res["status"] == "unmeasured"
    assert "결손 0" not in res["line"]


def test_2c_broken_db_is_unmeasured(tmp_path):
    """테이블이 없어도 예외를 밖으로 내지 않고 unmeasured 로 떨어진다."""
    raw = str(tmp_path / "raw.db")
    reg = str(tmp_path / "reg.db")
    _mk_raw(raw, _recent(1, 1))
    sqlite3.connect(reg).close()               # 빈 DB — regular_candles 테이블 없음
    res = check(days=10, reg_db=reg, raw_db=raw)
    assert res["status"] == "unmeasured"
    assert "조회 실패" in res["reason"]


# ── 3) 인코딩 지문 — 런처에 의존하지 않는다 ──────────────────────────────
def test_3_collector_declares_encoding():
    src = _read(_SRC_COLLECT)
    # 로그 쓰기: cp949 로 열면 '—'·'←' 한 글자에 그 실행의 로그가 통째로 사라진다
    assert 'io.open(p, "a", encoding="utf-8")' in src
    # ui_prefs.json 읽기: cp949 로 열면 UnicodeDecodeError → 미니 수집이 조용히 빠진다
    assert 'io.open(p, encoding="utf-8")' in src
    # 인코딩 없는 맨 open() 으로 ui_prefs 를 여는 옛 형태가 되살아나면 실패시킨다
    assert 'with open(os.path.join(_ROOT, "data", "ui_prefs.json"))' not in src
    # 실패를 삼키지 않는다 (계측 4원칙 ④)
    assert "ui_prefs.json 읽기 실패" in src


def test_3b_console_print_is_guarded():
    """스케줄러로 띄우면 stdout 이 cp949 파이프다 — 한 글자에 프로세스가 죽으면 안 된다."""
    src = _read(_SRC_COLLECT)
    i = src.index("def P(msg):")
    body = src[i:i + 900]
    assert "UnicodeEncodeError" in body
    assert "backslashreplace" in body


def test_3c_freshness_cli_print_is_guarded():
    """🔴 **음성 대조가 잡아낸 자기 결함.**

    감시 모듈이 고치려던 결함과 **같은 계열의 버그를 자기 안에 갖고 있었다** —
    파이프로 리디렉션하면 stdout 이 cp949 가 돼 `—` 한 글자에 `print` 가 터졌고,
    그때 종료코드가 **1** 이라 「결손 있음」과 구별되지 않았다.
    감시 장치가 자기 입을 닫으면 감시가 아니다.
    """
    src = _read(os.path.join(_ROOT, "scripts", "regular_freshness.py"))
    assert "def _safe_print" in src
    assert "backslashreplace" in src
    assert '_safe_print(res["line"])' in src, "CLI 가 맨 print 로 되돌아가면 안 된다"


# ── 4) 예약작업은 .bat 이 아니라 python.exe 를 등록한다 ──────────────────
def test_4_task_registers_python_not_bat():
    ps = _read(_SRC_TASK_PS1)
    body = ps.split("#>")[-1]                  # 헤더 주석을 뺀 본문
    assert "New-ScheduledTaskAction -Execute " in body
    assert "collect_regular_futures.py" in body
    assert "py37_32" in body                   # Cybos COM 은 32-bit 전용
    assert "--days" in body
    # 🔴 배치를 등록하면 끝의 PAUSE 가 무인 실행을 영구 대기시킨다
    assert "COLLECT_REGULAR_EOD.bat" not in body, "본문에서 .bat 을 등록하면 안 된다"


def test_4b_the_bat_still_has_the_pause_trap():
    """위 단언의 **이유**를 고정한다 — PAUSE 가 사라지면 이 테스트가 먼저 알려준다."""
    bat = _read(_SRC_BAT)
    assert "PAUSE" in bat.upper()


def test_4c_task_time_is_after_1546():
    """수집기는 now >= 15:46 이어야 당일을 base 로 잡는다."""
    ps = _read(_SRC_TASK_PS1)
    assert "15:52" in ps
    assert "15:46" in ps                       # 이른 시각 경고 가드가 살아 있을 것


def test_4d_runlevel_is_a_parameter_not_a_hardcoded_literal():
    """🔴 [MW0602 2026-09-17] 무결성 수준은 **PC 마다 다르다** — 값을 박으면 깨진다.

    595차 원본은 `-RunLevel Limited` 를 하드코딩했고 주석에 그 이유까지 적었다
    (「Cybos Plus 작업과 같은 무결성 수준이어야 COM 이 붙는다」). 원칙은 맞지만
    **가정한 값이 이 PC 에서 틀렸다** — MW0602 는 CREON 이 승격 실행이라
    `Limited` 로 등록하면 붙지 않는다:

        LastTaskResult=1 · 로그 파일조차 미생성
        직접 재현 → "[중단] Cybos Plus 미연결(IsConnect=0)"

    비승격 클라이언트가 기존 세션에 붙지 못하고 **로그인 안 된 새
    DibServer(`-Embedding`)** 를 띄우기 때문이다(실측: COM 호출 시각에 PID 신규
    생성, 그 프로세스만 CommandLine 이 읽힌다 = 하위 무결성).
    `Highest` 로 바꾸자 같은 리허설이 `LastTaskResult=0` 으로 통과했다.

    ⚠ 이 테스트가 깨지면 **체리픽이 이 수정을 덮은 것**이다.
      되돌리기 전에 그 PC 의 CREON 승격 여부를 먼저 실측할 것.
    """
    body = _read(_SRC_TASK_PS1).split("#>")[-1]
    assert "$RunLevel" in body, "-RunLevel 파라미터가 사라졌다"
    assert "-LogonType Interactive -RunLevel $RunLevel" in body,         "principal 이 파라미터를 쓰지 않는다"
    assert "-LogonType Interactive -RunLevel Limited" not in body,         "무결성 수준을 다시 박으면 안 된다"


def test_4e_highest_registration_has_an_elevation_precheck():
    """승격 없이 Highest 를 등록하면 `Access is denied` 만 나온다 — 원인을 말하지 않는다.

    그 오류를 그대로 만나면 **무엇을 고쳐야 하는지 알 수 없다.** 실제로
    2026-09-17 에 그렇게 한 번 막혔다. 그래서 등록 **전**에 잡고
    두 갈래 해법(관리자로 재실행 / -RunLevel Limited)을 같이 안내한다.
    """
    body = _read(_SRC_TASK_PS1).split("#>")[-1]
    i_check = body.find("IsInRole")
    # ⚠ 그냥 find 하면 해제 경로의 `Unregister-ScheduledTask` 에 먼저 걸려
    #   항상 실패한다(test_5 와 같은 계열의 함정). 줄 머리로 고정한다.
    m = re.search(r"^Register-ScheduledTask", body, re.M)
    assert m is not None, "등록 호출을 찾지 못했다"
    i_reg = m.start()
    assert i_check > 0, "승격 사전점검이 없다"
    assert i_reg > 0
    assert i_check < i_reg, "사전점검은 등록보다 **앞**이어야 한다"


# ── 5) EOD 체인 배선 — 재학습보다 **앞**에서 본다 ────────────────────────
def test_5_eod_calls_freshness_before_retrain():
    src = _read(_SRC_EOD)
    # ⚠ `from learning.batch_retrainer import BatchRetrainer` 는 이 파일에 **2곳**이다
    #   (헬퍼 `p8_scaler_refit()` / `main()` 의 재학습 블록). 그냥 find 하면
    #   헬퍼 쪽을 집어 항상 실패한다 — **main() 안에서** 찾는다.
    i_main = src.find("def main():")
    assert i_main > 0
    src = src[i_main:]
    i_fresh = src.find("from scripts.regular_freshness import")
    i_retrain = src.find("from learning.batch_retrainer import BatchRetrainer")
    assert i_fresh > 0, "EOD 체인에 [RegularFresh] 배선이 없다"
    assert i_retrain > 0
    assert i_fresh < i_retrain, "재학습이 실패해도 신선도 판정은 남아야 한다"
    # 결손이면 INFO 가 아니라 WARNING 으로 나가야 한다
    seg = src[i_fresh:i_fresh + 700]
    assert "log.warning" in seg and "log.info" in seg
