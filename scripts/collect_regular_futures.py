# -*- coding: utf-8 -*-
# scripts/collect_regular_futures.py — 정규 연결선물(10100) 풀세션 1분봉 EOD 수집기
"""미륵이는 **미니 당월물**을 **15:09까지만** 수집한다(15:10 강제청산 원칙의 부산물).
연구·검증에는 두 가지가 더 필요하다.

  (A) 15:10~15:45 — 종가 단일가 포함. L0(종가 임계) 계열 가설이 여기서 갈린다.
  (B) 정규 근월물 스케일 — 미니 당월물은 롤마다 만기 격차만큼 값이 튄다.
      실측: 만기 같으면 −0.01p, 1개월 차 +2.1~2.5p, 2개월 차 +4.4p (2026-09-11 확인)

`CpSysDib.FutOptChart` 로 **`10100` 코스피200 연결선물**(매일 411봉, 08:46~15:45)을 받아
**독립 DB** `data/db/regular_candles.db` 에 적재한다.

안전 규약
---------
  · 읽기 전용 시세 TR 만 호출한다. 주문·계좌 TR 을 부르지 않는다.
  · `raw_data.db` / `predictions.db` 등 **기존 DB 를 열지 않는다**(456차 규약).
  · 자기 DB 에만 INSERT OR REPLACE 로 적재 — 몇 번 돌려도 결과가 같다(멱등).
  · Cybos 요청 제한(15초 60건)을 `GetLimitRemainCount` 로 자동 대기한다.

실행 (py37_32 32-bit · Cybos Plus 로그인)
------------------------------------------
    python scripts/collect_regular_futures.py            # [기본] 전 기간 — 서버가 주는 만큼 전부
    python scripts/collect_regular_futures.py --today    # 최근 영업일 1일 (매일 운영용)
    python scripts/collect_regular_futures.py --days 60
    python scripts/collect_regular_futures.py --from 20260803 --to 20260911
    python scripts/collect_regular_futures.py --status   # 적재 현황·무결성만 (Cybos 불필요)

전 기간 모드
------------
오늘부터 5일씩 과거로 훑으며, **연속 3청크가 비면** 서버 보유 한계로 보고 멈춘다.
이미 완전히 적재된 청크는 건너뛴다(최근 7일은 항상 다시 받는다) — 재실행이 빠르고 멱등이다.
미니 근월물은 소멸 코드를 조회할 수 없으므로 **최근 45일만** 함께 받는다(스프레드 산출용).
"""
from __future__ import print_function

import argparse
import csv
import datetime as _dt
import os
import platform
import sqlite3
import sys
import threading
import time

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(_ROOT, "data", "db", "regular_candles.db")
CSV_DIR = os.path.join(_ROOT, "data", "regular_1m")
LOG_DIR = os.path.join(_ROOT, "logs")

REGULAR_CODE = "10100"                       # 코스피200 연결 (= 정규 근월물)
FIELDS_EXT = [0, 1, 2, 3, 4, 5, 8, 27, 10, 11]
FIELDS_BASE = [0, 1, 2, 3, 4, 5, 8, 27]
NAMES_EXT = ["date", "time", "open", "high", "low", "close", "volume", "oi", "cum_sell", "cum_buy"]
NAMES_BASE = NAMES_EXT[:8]

# 🔴 [559차 P0-1] 위 두 이름은 **틀렸다. 이름을 믿지 말 것.**
# ---------------------------------------------------------------------------
# 컬럼명은 그대로 두되(223,872행이 이미 적재됐고 이름을 바꾸면 과거 산출물이 어긋난다),
# 실제 의미는 아래가 정본이다. 질의는 뷰 `regular_flow_1m` 을 쓰는 것이 안전하다.
#
#   | 저장 컬럼   | TR 필드 | **실측 의미**                    | 상태 |
#   |------------|--------|---------------------------------|------|
#   | `cum_sell` | 10     | **누적 체결매수** (매도가 아니다) | ✅ 검증됨 |
#   | `cum_buy`  | 11     | **미상** — 하루 종일 오르내린다   | ⛔ 쓰지 말 것 |
#
# 근거(2026-09-13 실측, `scripts/regular_flow_field_verify.py` 로 재현):
#   · A056A(미니 당월물) 2026-09-11 — 필드10 **분봉 증분**이 미륵이 실시간 앵커
#     `raw_candles.anchor_buy`(FutureCurOnly 헤더 23 = 누적체결매수)와 **383/383 정확 일치**.
#     같은 날 `volume − 증분` 이 `anchor_sell` 과도 **383/383 일치**.
#   · 10100 연결선물 2024-07-04~2026-09-11 **533거래일** — 필드10 일중 비단조 스텝 **0건**,
#     일말 필드10/거래량 = 0.507~0.517(매월). 누적 체결매수의 프로파일이다.
#   · 필드11 은 같은 날 A056A 220회·10100 199회 **하락**했다. 누적량일 수 없다.
#
# ⚠ 08-10~09-10 구간에서 앵커와 안 맞는 것은 필드 의미 문제가 아니다 —
#   그 기간 A056A 는 **차월물**(일 거래량 3~6,304계약)이라 미륵이가 다른 종목을 보고 있었다.
#
# ⚠ 검증 표본은 아직 **1거래일(383봉)** 이다. 병행 거래일이 쌓이는 대로
#   `regular_flow_field_verify.py` 로 누적 확인할 것.
FIELD10_SEMANTICS = "cum_buy_verified_20260913"   # meta 에 기록되는 세대 문자열
FIELD11_SEMANTICS = "unknown_do_not_use"
CHUNK_DAYS = 4                               # 한 번의 TR 로 요청할 최대 달력일수
# ↑ FutOptChart 기간요청은 응답이 약 2000행에서 잘리며 **오래된 쪽부터** 버려진다.
#   5일(=2055행) 요청 시 가장 오래된 날의 앞 56분이 사라졌다(2026-09-07 등 22일 실측).
#   4일(=1644행)이면 한도 안쪽이라 안전하다. 1일 요청(411행)은 절대 잘리지 않는다.
# ── 시각 정렬 ────────────────────────────────────────────────────────────────
# 사이보스 FutOptChart 분봉의 시각 라벨은 미륵이 실시간 봉보다 **1분 늦다**.
#   · 증거 1: 같은 개장(08:45)인데 미륵이 raw_candles 첫 봉은 08:45, 차트는 08:46
#   · 증거 2: 1분 수익률 상관 — lag=-1 에서 0.976~0.996, lag=0 에서 -0.10~+0.07 (5일 전수)
#   · 증거 3: 피터리 8/4 트윗 6건이 lag=-1 에서만 "사건 후 0~3분"으로 일관된다
# 그래서 **저장할 때 1분 당겨** 미륵이와 같은 축에 놓는다. 조인이 자동으로 맞는다.
TS_SHIFT_MIN = 1                             # 라벨 → 실제. 0 으로 두면 원본 라벨 그대로
SESSION_OPEN = "08:45"                       # 보정 후 정상일의 첫 봉 (보정 전 08:46)
# 한국거래소 지연 개장일 — 결함이 아니다. (첫 봉, 마지막 봉) 조합으로 식별한다.
#   수능일      : 세션 전체가 1시간 뒤로 밀린다 → 09:46~16:45, 봉 수는 정상(411)
#   1월 2일 개장일: 개장만 1시간 늦고 마감은 그대로 → 09:46~15:45, 60봉 짧다(351)
LATE_OPEN_SESSIONS = {("09:45", "16:44"), ("09:45", "15:44")}   # 보정 후 기준
MAX_BACK_DAYS = 800                          # 전 기간 모드의 최대 소급 한도(안전장치)
STOP_AFTER_EMPTY = 3                         # 연속 빈 청크 N개면 서버 보유 한계로 보고 중단
ALWAYS_REFETCH_DAYS = 7                      # 최근 N일은 이미 있어도 항상 다시 받는다
MINI_BACK_DAYS = 45                          # 미니 근월물 소급 한도(소멸 월물은 조회 불가)

_LOG = []


def P(msg):
    line = "%s %s" % (_dt.datetime.now().strftime("%H:%M:%S"), msg)
    print(line)
    sys.stdout.flush()
    _LOG.append(line)


# ───────────────────────── COM ─────────────────────────
def block_request(progid, input_pairs, reader, timeout_sec=60):
    """Dispatch~데이터읽기를 한 워커 스레드에서(STA), 메인은 메시지 펌프로 대기."""
    import pythoncom
    import win32com.client as win32
    res = {"ret": None, "status": None, "msg": "", "data": None, "exc": None}
    done = threading.Event()

    def _worker():
        try:
            pythoncom.CoInitialize()
        except Exception:
            pass
        try:
            obj = win32.Dispatch(progid)
            for idx, val in input_pairs:
                obj.SetInputValue(idx, val)
            res["ret"] = obj.BlockRequest()
            try:
                res["status"] = int(obj.GetDibStatus())
                res["msg"] = str(obj.GetDibMsg1())
            except Exception:
                pass
            res["data"] = reader(obj) if reader else None
        except Exception as e:
            res["exc"] = e
        finally:
            try:
                pythoncom.CoUninitialize()
            except Exception:
                pass
            done.set()

    t = threading.Thread(target=_worker)
    t.daemon = True
    t.start()
    t0 = time.time()
    while not done.is_set():
        pythoncom.PumpWaitingMessages()
        time.sleep(0.01)
        if time.time() - t0 > timeout_sec:
            raise RuntimeError("BlockRequest timeout: %s" % progid)
    if res["exc"] is not None:
        raise res["exc"]
    return res["ret"], res["status"], res["msg"], res["data"]


def wait_quota():
    try:
        import win32com.client as win32
        cyb = win32.Dispatch("CpUtil.CpCybos")
        if int(cyb.GetLimitRemainCount(1)) <= 1:
            ms = int(cyb.LimitRequestRemainTime)
            P("    [quota] %.1f초 대기" % (ms / 1000.0))
            time.sleep(ms / 1000.0 + 0.3)
    except Exception:
        time.sleep(0.25)


def mini_near_code():
    """미니 근월물 코드. CpFutureCode 에 없으므로 ui_prefs 를 우선 본다."""
    try:
        import json
        with open(os.path.join(_ROOT, "data", "ui_prefs.json")) as f:
            raw = str(json.load(f).get("symbol_code", "")).strip()
        if len(raw) == 8 and raw.endswith("000"):
            return raw[:-3]
        if raw:
            return raw
    except Exception:
        pass
    return ""


# ───────────────────────── DB ─────────────────────────
DDL = """
CREATE TABLE IF NOT EXISTS regular_candles (
    code      TEXT NOT NULL,
    ts        TEXT NOT NULL,          -- 'YYYY-MM-DD HH:MM:00'
    trade_date TEXT NOT NULL,
    open  REAL, high REAL, low REAL, close REAL,
    volume INTEGER, oi INTEGER, cum_sell INTEGER, cum_buy INTEGER,
    src   TEXT DEFAULT 'FutOptChart',
    loaded_at TEXT,
    PRIMARY KEY (code, ts)
);
CREATE INDEX IF NOT EXISTS ix_reg_date ON regular_candles(code, trade_date);
CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT);

-- [559차 P0-1] 이름이 틀린 컬럼을 우회하는 질의용 뷰.
-- 필드11(`cum_buy` 컬럼)은 의미 미상이라 **의도적으로 뺐다** — 뷰만 쓰면 오용이 불가능하다.
CREATE VIEW IF NOT EXISTS regular_flow_1m AS
SELECT code, ts, trade_date, open, high, low, close, volume, oi,
       cum_sell AS cum_buy_verified   -- ← 필드10. 누적 "체결매수" 다(실측 383/383).
  FROM regular_candles;
"""


def open_db():
    d = os.path.dirname(DB_PATH)
    if not os.path.isdir(d):
        os.makedirs(d)
    con = sqlite3.connect(DB_PATH)
    con.executescript(DDL)
    # [559차 P0-1] 필드 의미를 DB 안에 남긴다 — 코드를 안 읽고 DB만 여는 세션이 있다.
    con.execute("INSERT OR REPLACE INTO meta VALUES ('field10_semantics',?)", (FIELD10_SEMANTICS,))
    con.execute("INSERT OR REPLACE INTO meta VALUES ('field11_semantics',?)", (FIELD11_SEMANTICS,))
    con.execute("INSERT OR REPLACE INTO meta VALUES ('column_label_warning',"
                "'cum_sell 컬럼=필드10=누적체결매수 / cum_buy 컬럼=필드11=미상. 뷰 regular_flow_1m 사용 권장')")
    con.commit()
    return con


def upsert(con, code, rows, names):
    now = _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    idx = dict((n, i) for i, n in enumerate(names))
    payload = []
    for r in rows:
        ymd = str(int(r[idx["date"]]))
        hm = int(r[idx["time"]])
        t0 = _dt.datetime(int(ymd[0:4]), int(ymd[4:6]), int(ymd[6:8]), hm // 100, hm % 100) \
            - _dt.timedelta(minutes=TS_SHIFT_MIN)
        ts = t0.strftime("%Y-%m-%d %H:%M:00")
        payload.append((
            code, ts, t0.strftime("%Y-%m-%d"),
            float(r[idx["open"]]), float(r[idx["high"]]), float(r[idx["low"]]), float(r[idx["close"]]),
            int(r[idx["volume"]]), int(r[idx["oi"]]),
            int(r[idx["cum_sell"]]) if "cum_sell" in idx else None,
            int(r[idx["cum_buy"]]) if "cum_buy" in idx else None,
            "FutOptChart", now))
    con.executemany(
        "INSERT OR REPLACE INTO regular_candles"
        "(code,ts,trade_date,open,high,low,close,volume,oi,cum_sell,cum_buy,src,loaded_at)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", payload)
    con.commit()
    return len(payload)


# ───────────────────────── 수집 ─────────────────────────
def fetch(code, start_ymd, end_ymd):
    last = ""
    for fields, names in ((FIELDS_EXT, NAMES_EXT), (FIELDS_BASE, NAMES_BASE)):
        def _reader(obj, _f=fields):
            n = int(obj.GetHeaderValue(3))
            return [[obj.GetDataValue(c, i) for c in range(len(_f))] for i in range(n)]
        inputs = [(0, code), (1, ord("1")), (2, int(end_ymd)), (3, int(start_ymd)),
                  (5, fields), (6, ord("m")), (7, 1), (8, ord("0"))]
        wait_quota()
        try:
            ret, status, msg, data = block_request("CpSysDib.FutOptChart", inputs, _reader)
        except Exception as e:
            last = "예외 %r" % (e,)
            continue
        if ret not in (0, None) or status != 0 or not data:
            last = "ret=%s status=%s msg=%s rows=%s" % (ret, status, msg, len(data or []))
            continue
        return sorted(data, key=lambda r: (int(r[0]), int(r[1]))), names
    return None, last


def daterange_chunks(start, end, step_days):
    s = _dt.datetime.strptime(start, "%Y%m%d").date()
    e = _dt.datetime.strptime(end, "%Y%m%d").date()
    while s <= e:
        z = min(s + _dt.timedelta(days=step_days - 1), e)
        yield s.strftime("%Y%m%d"), z.strftime("%Y%m%d")
        s = z + _dt.timedelta(days=1)


def loaded_days(con, code):
    return set(r[0] for r in con.execute(
        "SELECT DISTINCT trade_date FROM regular_candles WHERE code=?", (code,)))


def chunk_is_covered(con, code, s_ymd, e_ymd, have):
    """청크의 모든 '평일'이 이미 적재돼 있으면 True (휴장일은 알 수 없으므로 평일만 따진다)."""
    d = _dt.datetime.strptime(s_ymd, "%Y%m%d").date()
    end = _dt.datetime.strptime(e_ymd, "%Y%m%d").date()
    weekdays = []
    while d <= end:
        if d.weekday() < 5:
            weekdays.append(d.strftime("%Y-%m-%d"))
        d += _dt.timedelta(days=1)
    if not weekdays:
        return True
    return all(w in have for w in weekdays)


def backward_chunks(start_date, max_days, step):
    """오늘(start_date)부터 과거로 step일씩. (시작, 종료) YYYYMMDD 를 최신 청크부터 내놓는다."""
    end = start_date
    walked = 0
    while walked < max_days:
        s = end - _dt.timedelta(days=step - 1)
        yield s.strftime("%Y%m%d"), end.strftime("%Y%m%d")
        walked += step
        end = s - _dt.timedelta(days=1)


def collect_range(con, code, chunks, csv_flag, stop_after_empty=0, skip_covered=False,
                  fresh_cutoff=None):
    have = loaded_days(con, code) if skip_covered else set()
    total = 0
    empties = 0
    for s, e in chunks:
        if skip_covered and (fresh_cutoff is None or e < fresh_cutoff) \
                and chunk_is_covered(con, code, s, e, have):
            P("  %s  %s~%s  건너뜀(적재 완료)" % (code, s, e))
            continue
        P("  %s  %s~%s" % (code, s, e))
        rows, info = fetch(code, s, e)
        if rows is None:
            P("    수집 없음: %s" % info)
            empties += 1
            if stop_after_empty and empties >= stop_after_empty:
                P("  [중단] 연속 %d청크 비어 있음 — 서버 보유 한계로 판단" % empties)
                break
            continue
        empties = 0
        n = upsert(con, code, rows, info)
        total += n
        days = sorted(set(int(r[0]) for r in rows))
        P("    %d행 / %d일 (%s~%s)" % (n, len(days), days[0], days[-1]))
        if csv_flag:
            _write_csv(code, s, e, rows, info)
    return total


def _write_csv(code, s, e, rows, names):
    if not os.path.isdir(CSV_DIR):
        os.makedirs(CSV_DIR)
    p = os.path.join(CSV_DIR, "%s_%s_%s_1m.csv" % (code, s, e))
    f = open(p, "w")
    try:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(names)
        for r in rows:
            w.writerow(r)
    finally:
        f.close()
    P("    CSV: %s" % p)


def report(con, code, limit=15):
    tot = con.execute("SELECT COUNT(*), COUNT(DISTINCT trade_date), MIN(trade_date), MAX(trade_date)"
                      " FROM regular_candles WHERE code=?", (code,)).fetchone()
    P("  [%s] 총 %s행 / %s거래일 / %s ~ %s" % (code, tot[0], tot[1], tot[2], tot[3]))
    cur = con.execute(
        "SELECT trade_date, COUNT(*), MIN(ts), MAX(ts), MAX(high), MIN(low),"
        " SUM(CASE WHEN substr(ts,12,5) >= '15:10' THEN 1 ELSE 0 END)"
        " FROM regular_candles WHERE code=? GROUP BY trade_date ORDER BY trade_date DESC LIMIT ?",
        (code, limit))
    P("    일자         봉수  범위            고가      저가   15:10이후")
    for d, n, t0, t1, hi, lo, aft in cur.fetchall():
        f0, f1 = t0[11:16], t1[11:16]
        if is_late_open(f0, f1):
            flag = "   (지연개장)"
        elif n >= 400 and aft >= 20:
            flag = ""
        elif f0 != SESSION_OPEN:
            flag = "   <-- 앞절단" if n >= 400 * 0.6 else "   (희소)"
        else:
            flag = "   <-- 결손"
        P("    %s %5d  %s~%s %9.2f %9.2f %6d%s" % (d, n, t0[11:16], t1[11:16], hi, lo, aft, flag))


def day_first_bar(con, code):
    return dict(con.execute(
        "SELECT trade_date, MIN(substr(ts,12,5)) FROM regular_candles WHERE code=? GROUP BY trade_date", (code,)))


def is_late_open(t0, t1):
    """지연 개장(수능일·1월 2일 개장일)인가 — 결함이 아니다."""
    return (t0, t1) in LATE_OPEN_SESSIONS


def truncated_days(con, code, full_bars=411):
    """앞절단된 날 — 재수집 대상.
    제외: 지연 개장일(수능·1월2일), 그리고 체결 자체가 드문 날(원월물 구간).
    희소일은 첫 봉이 늦는 게 정상이며 재수집해도 같은 결과가 나온다."""
    rows = con.execute(
        "SELECT trade_date, COUNT(*), MIN(substr(ts,12,5)), MAX(substr(ts,12,5))"
        " FROM regular_candles WHERE code=? GROUP BY trade_date", (code,)).fetchall()
    return sorted(d for d, n, t0, t1 in rows
                  if t0 != SESSION_OPEN and not is_late_open(t0, t1) and n >= full_bars * 0.6)


def _flow_semantics_check(con, code):
    """[559차 P0-1] 필드10 = 누적 체결매수 라는 라벨이 아직 유효한가.

    누적 체결매수라면 **일중 단조증가**여야 한다(체결은 취소되지 않는다). 이 검사가
    깨지면 원천의 필드 배치가 바뀐 것이므로 `FIELD10_SEMANTICS` 부터 다시 재야 한다.

    필드11(`cum_buy` 컬럼)은 의미 미상이고 실측상 원래 비단조다 — **이상이 아니라
    현상 기록**이므로 개수만 찍고 판정하지 않는다(계측 4원칙 3: 탈락 가시화).
    """
    def _nonmono(col):
        return con.execute(
            "SELECT COUNT(*) FROM (SELECT %s v, LAG(%s) OVER"
            " (PARTITION BY trade_date ORDER BY ts) p"
            " FROM regular_candles WHERE code=?) WHERE p IS NOT NULL AND v < p" % (col, col),
            (code,)).fetchone()[0]
    try:
        n10, n11 = _nonmono("cum_sell"), _nonmono("cum_buy")
    except sqlite3.OperationalError as e:      # 윈도우 함수 미지원 sqlite
        P("    [필드의미] 검사 생략 (%s)" % e)
        return
    tag = "OK" if n10 == 0 else "🔴 라벨 재확인 필요"
    P("    [필드의미] 필드10(cum_sell 컬럼) 일중 비단조 %d건 — %s"
      "  ← 이 컬럼은 누적 **체결매수** 다(559차 실측)" % (n10, tag))
    P("               필드11(cum_buy 컬럼) 비단조 %d건 — 의미 미상, 판정 대상 아님. 쓰지 말 것" % n11)


def integrity(con, code, full_bars=411):
    P("  [무결성] %s" % code)
    q = con.execute(
        "SELECT SUM(high<low OR high<open OR high<close OR low>open OR low>close),"
        " SUM(close IS NULL), SUM(oi IS NULL OR oi=0), SUM(cum_sell IS NULL)"
        " FROM regular_candles WHERE code=?", (code,)).fetchone()
    P("    OHLC 모순 %s | close 결측 %s | oi 0/결측 %s | cum_sell 결측 %s" % q)
    _flow_semantics_check(con, code)

    rows = con.execute(
        "SELECT trade_date, COUNT(*), MIN(substr(ts,12,5)), MAX(substr(ts,12,5))"
        " FROM regular_candles WHERE code=? GROUP BY trade_date ORDER BY trade_date", (code,)).fetchall()
    late = [r for r in rows if r[2] != SESSION_OPEN and is_late_open(r[2], r[3])]
    rest = [r for r in rows if r[2] != SESSION_OPEN and not is_late_open(r[2], r[3])]
    trunc = [r for r in rest if r[1] >= full_bars * 0.6]
    thin = [r for r in rest if r[1] < full_bars * 0.6]
    midgap = [r for r in rows if r[2] == SESSION_OPEN and r[1] < full_bars]
    if thin:
        P("    희소 %d일  ← 결함 아님. 근월물이 아니던 기간이라 첫 체결이 늦다" % len(thin))
    if late:
        P("    지연개장 %d일  ← 결함 아님(수능일·1월2일 개장일): %s" % (
            len(late), ", ".join("%s(%d봉/%s~%s)" % r for r in late[:8])))
    P("    앞절단(첫 봉 %s 아님) %d일  ← 청크 응답 절단. `--repair` 로 1일씩 재수집" % (SESSION_OPEN, len(trunc)))
    if trunc:
        P("      " + ", ".join("%s(%d봉/%s)" % (d, n, t0) for d, n, t0, _ in trunc[:14])
          + (" …" if len(trunc) > 14 else ""))
    # 근월물이 아닌 기간의 원월물은 체결 자체가 드물어 결손이 정상이다 —
    # 세션의 60% 이상이 차 있는 날만 "구멍"으로 본다.
    dense = [r for r in midgap if r[1] >= full_bars * 0.6]
    sparse = len(midgap) - len(dense)
    P("    장중결손 %d일 (그중 조밀 %d일) ← 결함 아님. 서킷브레이커·매매정지 추정(재수집해도 동일)"
      % (len(midgap), len(dense)))
    if sparse:
        P("      희소 %d일은 해당 종목이 근월물이 아니던 기간 — 무체결 분봉으로 정상" % sparse)
    for d, n, t0, t1 in dense[:14]:
        gap = _gap_windows(con, code, d, full_bars)
        if len(gap) > 110:
            gap = gap[:110] + " …"
        rng = con.execute("SELECT 100.0*(MAX(high)-MIN(low))/MIN(low) FROM regular_candles"
                          " WHERE code=? AND trade_date=?", (code, d)).fetchone()[0]
        P("      %s %d봉  결손 %s  일중변동 %.2f%%" % (d, n, gap, rng or 0.0))

    have = [r[0] for r in rows]
    if len(have) >= 2:
        hs = set(have)
        d = _dt.datetime.strptime(have[0], "%Y-%m-%d").date()
        end = _dt.datetime.strptime(have[-1], "%Y-%m-%d").date()
        miss = []
        while d <= end:
            if d.weekday() < 5 and d.strftime("%Y-%m-%d") not in hs:
                miss.append(d.strftime("%m/%d"))
            d += _dt.timedelta(days=1)
        P("    구간 내 빠진 평일 %d개%s" % (len(miss), (" (공휴일 추정): " + ", ".join(miss[:20])) if miss else ""))


def _gap_windows(con, code, day, full_bars):
    """기준일(최신 정상일)의 시각표와 비교해 빠진 구간을 문자열로."""
    ref = [r[0] for r in con.execute(
        "SELECT substr(ts,12,5) FROM regular_candles WHERE code=? AND trade_date="
        "(SELECT trade_date FROM regular_candles WHERE code=? GROUP BY trade_date"
        " HAVING COUNT(*)>=? ORDER BY trade_date DESC LIMIT 1) ORDER BY ts", (code, code, full_bars))]
    got = set(r[0] for r in con.execute(
        "SELECT substr(ts,12,5) FROM regular_candles WHERE code=? AND trade_date=?", (code, day)))
    miss = [t for t in ref if t not in got]
    if not miss:
        return "-"
    runs, s, p = [], None, None
    for t in miss:
        if s is None:
            s = p = t
            continue
        if ref.index(t) == ref.index(p) + 1:
            p = t
        else:
            runs.append((s, p)); s = p = t
    runs.append((s, p))
    return ", ".join("%s~%s(%d분)" % (a, b, ref.index(b) - ref.index(a) + 1) for a, b in runs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--today", action="store_true", help="최근 영업일 1일만 (매일 운영용)")
    ap.add_argument("--days", type=int, default=0, help="오늘부터 N 달력일 백필")
    ap.add_argument("--from", dest="dfrom", default="", help="YYYYMMDD")
    ap.add_argument("--to", dest="dto", default="", help="YYYYMMDD")
    ap.add_argument("--max-back", type=int, default=MAX_BACK_DAYS, help="전 기간 모드 소급 한도(일)")
    ap.add_argument("--no-mini", action="store_true", help="미니 근월물 수집 생략")
    ap.add_argument("--mini-days", type=int, default=MINI_BACK_DAYS, help="미니 소급 한도(일)")
    ap.add_argument("--force", action="store_true", help="이미 적재된 청크도 다시 받는다")
    ap.add_argument("--csv", action="store_true", help="CSV 도 data/regular_1m/ 에 저장")
    ap.add_argument("--migrate-ts", action="store_true",
                    help="기존 적재분의 시각 라벨을 1분 당겨 미륵이와 정렬(1회용, 중복 실행 방지됨)")
    ap.add_argument("--repair", action="store_true",
                    help="앞절단된 날만 1일 단위로 재수집(1일 요청은 절대 잘리지 않는다)")
    ap.add_argument("--status", action="store_true", help="적재 현황·무결성만 출력 (Cybos 불필요)")
    a = ap.parse_args()

    con = open_db()
    if a.migrate_ts:
        cur = con.execute("SELECT v FROM meta WHERE k='ts_convention'").fetchone()
        if cur and cur[0] == "mireuk_aligned":
            P("[건너뜀] 이미 정렬됨(ts_convention=mireuk_aligned)")
        else:
            n = con.execute("SELECT COUNT(*) FROM regular_candles").fetchone()[0]
            con.execute("UPDATE regular_candles SET"
                        " ts = strftime('%Y-%m-%d %H:%M:00', datetime(ts, ?)),"
                        " trade_date = strftime('%Y-%m-%d', datetime(ts, ?))",
                        ("-%d minutes" % TS_SHIFT_MIN, "-%d minutes" % TS_SHIFT_MIN))
            con.execute("INSERT OR REPLACE INTO meta VALUES ('ts_convention','mireuk_aligned')")
            con.commit()
            P("[DONE] %d행 시각 %d분 당김 → 미륵이 raw_candles 와 같은 축" % (n, TS_SHIFT_MIN))
        _mark_labels(con)
        for c in [r[0] for r in con.execute("SELECT DISTINCT code FROM regular_candles")]:
            report(con, c); integrity(con, c)
        con.close(); _flush(); return 0
    if a.status:
        for c in [r[0] for r in con.execute("SELECT DISTINCT code FROM regular_candles")] or [REGULAR_CODE]:
            report(con, c, 30)
            integrity(con, c)
        _flush()
        return 0

    if platform.architecture()[0] != "32bit":
        P("[중단] 32-bit Python(py37_32)에서 실행할 것 — Cybos COM 요구사항")
        return 2
    try:
        import win32com.client as win32
    except ImportError:
        P("[중단] pywin32(32-bit) 없음")
        return 2
    if not win32.Dispatch("CpUtil.CpCybos").IsConnect:
        P("[중단] Cybos Plus 미연결(IsConnect=0). 로그인 후 실행할 것.")
        return 1

    if a.repair:
        total = 0
        for code in [r[0] for r in con.execute("SELECT DISTINCT code FROM regular_candles")]:
            bad = truncated_days(con, code)
            if not bad:
                P("  [%s] 앞절단 없음" % code)
                continue
            P("  [%s] 앞절단 %d일 — 1일씩 재수집" % (code, len(bad)))
            for day in bad:
                ymd = day.replace("-", "")
                before = con.execute("SELECT COUNT(*), MIN(substr(ts,12,5)) FROM regular_candles"
                                     " WHERE code=? AND trade_date=?", (code, day)).fetchone()
                rows, info = fetch(code, ymd, ymd)
                if rows is None:
                    P("    %s  실패: %s" % (day, info))
                    continue
                total += upsert(con, code, rows, info)
                after = con.execute("SELECT COUNT(*), MIN(substr(ts,12,5)) FROM regular_candles"
                                    " WHERE code=? AND trade_date=?", (code, day)).fetchone()
                P("    %s  %d봉(%s) → %d봉(%s)%s" % (day, before[0], before[1], after[0], after[1],
                                                    "  OK" if after[1] == SESSION_OPEN else "  <-- 여전히 늦은 개장(실제일 수 있음)"))
        P("[DONE] 보수 %d행" % total)
        for c in [r[0] for r in con.execute("SELECT DISTINCT code FROM regular_candles")]:
            report(con, c)
            integrity(con, c)
        con.close()
        _flush()
        return 0

    today = _dt.date.today()
    # 15:45 이전이면 당일 봉이 미완성이므로 전일을 기준으로 삼는다
    base = today if _dt.datetime.now().time() >= _dt.time(15, 46) else today - _dt.timedelta(days=1)
    fresh_cutoff = (base - _dt.timedelta(days=ALWAYS_REFETCH_DAYS)).strftime("%Y%m%d")

    mode = "전기간"
    if a.dfrom or a.dto:
        mode, start, end = "지정기간", (a.dfrom or a.dto), (a.dto or a.dfrom)
    elif a.days > 0:
        mode = "최근%d일" % a.days
        start = (base - _dt.timedelta(days=a.days - 1)).strftime("%Y%m%d")
        end = base.strftime("%Y%m%d")
    elif a.today:
        mode, start, end = "당일", base.strftime("%Y%m%d"), base.strftime("%Y%m%d")

    P("[OK] Cybos 연결 | 모드=%s | DB=%s" % (mode, DB_PATH))
    total = 0
    if mode == "전기간":
        P("  정규 %s — 오늘부터 최대 %d일 소급, 연속 %d청크 비면 중단%s" % (
            REGULAR_CODE, a.max_back, STOP_AFTER_EMPTY, "" if a.force else ", 적재 완료분은 건너뜀"))
        total += collect_range(con, REGULAR_CODE,
                               backward_chunks(base, a.max_back, CHUNK_DAYS), a.csv,
                               stop_after_empty=STOP_AFTER_EMPTY,
                               skip_covered=not a.force, fresh_cutoff=fresh_cutoff)
    else:
        total += collect_range(con, REGULAR_CODE, list(daterange_chunks(start, end, CHUNK_DAYS)),
                               a.csv, skip_covered=not a.force, fresh_cutoff=fresh_cutoff)

    if not a.no_mini:
        mc = mini_near_code()
        if not mc:
            P("[WARN] 미니 근월물 코드를 찾지 못함 — 정규만 수집")
        else:
            if mode == "전기간":
                ms = (base - _dt.timedelta(days=a.mini_days - 1)).strftime("%Y%m%d")
                me = base.strftime("%Y%m%d")
            else:
                ms, me = start, end
            P("  미니 %s (%s~%s) — 소멸 월물은 조회 불가하므로 최근분만" % (mc, ms, me))
            total += collect_range(con, mc, list(daterange_chunks(ms, me, CHUNK_DAYS)), a.csv,
                                   skip_covered=not a.force, fresh_cutoff=fresh_cutoff)

    P("[DONE] 이번 실행 %d행 적재" % total)
    _mark_labels(con)
    for c in [r[0] for r in con.execute("SELECT DISTINCT code FROM regular_candles")]:
        report(con, c)
        integrity(con, c)
    con.close()
    _flush()
    return 0


def _mark_labels(con):
    """롤 당일·거래정지 라벨 재계산 — 같은 프로세스 안에서 직접 부른다.
    배치의 조건문/ERRORLEVEL 에 맡기면 실패가 조용히 묻힌다(2026-09-11 3회 실측)."""
    try:
        con.commit()
        import importlib.util
        mp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mark_roll_and_halts.py")
        spec = importlib.util.spec_from_file_location("mark_roll_and_halts", mp)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        P("[MARK] 롤 당일 / 거래정지 라벨 갱신...")
        mod.run(DB_PATH, mod.RAW_DB, quiet=True)   # raw 경로는 mark 모듈의 상수를 쓴다
    except Exception as e:
        P("[WARN] 라벨 갱신 실패: %r — roll_days/cb_halts 가 옛 값으로 남습니다" % (e,))


def _flush():
    try:
        if not os.path.isdir(LOG_DIR):
            os.makedirs(LOG_DIR)
        p = os.path.join(LOG_DIR, "%s_REGULAR_COLLECT.log" % _dt.date.today().strftime("%Y%m%d"))
        f = open(p, "a")
        try:
            f.write("\n".join(_LOG) + "\n")
        finally:
            f.close()
        print("[로그] %s" % p)
    except Exception as e:
        print("[로그 실패] %r" % e)


if __name__ == "__main__":
    sys.exit(main())
