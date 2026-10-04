# -*- coding: utf-8 -*-
# scripts/option_flow_freshness.py — 옵션 투자자 흐름(7222) 마감 구간 신선도 검사 (EOD 체인용)
"""장후 재수집이 **조용히 실패하는 것**을 다음 날 안에 알아채기 위한 검사.

왜 있는가 (2026-10-04 / MW0601)
-------------------------------
`option_flow.db` 의 라이브 수집은 수급 타이머에 얹혀 있고, 그 타이머는
`is_market_open()`(15:35 마감)에 막힌 뒤 15:40 `daily_close` 에서 멈춘다.
그래서 매일 **15:34 행이 덜 찬 채로 굳고, 15:35 – 16:07 행(종가 단일가·장후
정정)이 통째로 없다.** 실측 2026-10-02 (월)위클리 콜 개인: HTS [7222] 최종 −96
(16:07) vs DB 마지막 −226(15:34).

이 구간을 메우라고 둔 예약작업 `Mireuk_OptionFlowBackfill_1605` 는 2026-09-21
등록 이래 **8거래일 전부 실패**했다(LastTaskResult=2 · DB 의 15:35 이후 행 0건).
원인은 권한 수준 불일치다 — 이 PC 의 Cybos 는 비승격인데 작업이 Highest 로
등록돼 COM 이 새 미접속 DibServer 를 띄웠다. 작업은 출력을 어디에도 남기지
않았고, 결과를 보는 눈도 없었다. 595차 정규선물 수집이 「엿새간 조용히 멈춘」
것과 같은 계열이다 — 그때 만든 `[RegularFresh]` 와 같은 자리에 같은 방식으로 둔다.

무엇을 재는가
-------------
기준선은 **미륵이 자신**이다(`regular_freshness.py` 와 같다):
    기준 거래일 = raw_candles 에 MIN_BARS 봉 이상 있는 날 ∩ 수집 개시일(FLOW_START) 이후

각 기준일의 판정:
    absent    그날 옵션 흐름 행이 하나도 없다
    no_close  행은 있으나 옵션 상품의 최신 봉이 CLOSE_OK 미만 — 마감 구간 미확보

⚠ **오늘은 SETTLE_HM 전이면 기준에서 뺀다.** EOD 체인은 15:50 에 돌고 재수집은
  그 뒤(16:20)에 돈다. 오늘을 넣으면 매일 거짓 경보가 난다. 그래서 이 검사는
  사실상 「어제까지」를 본다 — 하루 늦지만 조용히 멈추는 것은 막는다.

🔴 **지난 날짜는 복구할 수 없다.** 7222 에는 날짜 입력이 없고 당일 데이터만
  준다. 그래서 경보 문구에 복구 명령 대신 「복구 불가」를 적는다(헛수고 방지).

규약
----
· 456차(장중 라이브 DB 분석 금지) — EOD 전용, 최근 `days` 일만 본다. 두 DB 모두 `mode=ro`.
· 계측 4원칙 ②: 「DB 를 못 읽었다」와 「결손 0」은 다른 값이다 → `unmeasured`.
· 계측 4원칙 ③: 목록을 자를 때 잔여 개수를 적는다.

단독 실행
---------
    python scripts/option_flow_freshness.py            # 종료코드 0=정상 1=결손 2=미측정
    python scripts/option_flow_freshness.py --days 20
"""
from __future__ import print_function

import argparse
import datetime as _dt
import os
import sqlite3
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

FLOW_DB = os.path.join(_ROOT, "data", "db", "option_flow.db")
RAW_DB = os.path.join(_ROOT, "data", "db", "raw_data.db")

FLOW_START = "2026-09-21"   # CpSvrNew7222 수집 개시일 — 그 전은 결손이 아니라 「수집 이전」
DEFAULT_DAYS = 10           # 기준선 창(달력일)
MIN_BARS = 10               # 이보다 적은 봉만 있는 날은 기준선에서 뺀다(세션 파편)
CLOSE_OK = "15:40"          # 이 시각 이후 봉이 있어야 「마감 구간 확보」(종가 단일가 15:35–15:45)
CLOSE_OK_EXPIRY = "15:20"   # 월물 만기일 — ⚠ 미검증 보수값. 2026-10-08 실측으로 확정할 것
SETTLE_HM = "16:40"         # 이 시각 전이면 오늘은 기준에서 뺀다(재수집 16:20 + 여유)
MAX_LIST = 10
# 옵션 상품만 본다 — kospi_spot(B)은 1–2분 불규칙이라 마감 판정에 쓰지 않는다
OPTION_PRODUCTS = ("wk_mon_call", "wk_mon_put", "wk_thu_call", "wk_thu_put", "mon_call", "mon_put")


def _ro(path):
    """읽기전용 연결 — 남의 DB 에 `-journal` 을 남기지 않는다(09-16 실측 사고)."""
    return sqlite3.connect("file:%s?mode=ro" % path.replace("\\", "/"), uri=True, timeout=5.0)


def _close_ok_for(day):
    try:
        from utils.time_utils import is_expiry_day
        if is_expiry_day(_dt.datetime.strptime(day, "%Y-%m-%d")):
            return CLOSE_OK_EXPIRY
    except Exception:
        pass                         # 판정 불가면 평일 기준(더 엄격한 쪽)으로 본다
    return CLOSE_OK


def format_line(res):
    """`[OptionFlowFresh] …` 한 줄. 상태마다 **문구 자체가 다르다**."""
    if res["status"] == "unmeasured":
        return ("[OptionFlowFresh] 미측정 — %s. 「결손 없음」이 아니다(계측 4원칙 ②)" % res["reason"])
    if res["status"] == "ok":
        return ("[OptionFlowFresh] 마감 구간 확보 · 기준 %d거래일(%s 이후, 최근 %d일) · 결손 0일 · 최신 %s"
                % (res["n_ref"], FLOW_START, res["days"], res["latest"] or "없음"))
    bad = res["bad"]
    shown = ", ".join("%s(%s)" % (d, why) for d, why in bad[:MAX_LIST])
    more = "" if len(bad) <= MAX_LIST else " 외 %d개" % (len(bad) - MAX_LIST)
    return ("[OptionFlowFresh] 결손 %d일 — %s%s | 기준 %d거래일. "
            "⚠ 지난 날짜는 복구 불가(7222 는 당일만 준다). "
            "원인 점검: 예약작업 \\Mireuk\\Mireuk_OptionFlowBackfill_1605 의 LastTaskResult · "
            "logs\\<YYYYMMDD>_OPTION_BACKFILL.log"
            % (len(bad), shown, more, res["n_ref"]))


def check(days=DEFAULT_DAYS, flow_db=None, raw_db=None, now=None, min_bars=MIN_BARS):
    """Returns dict(status, bad=[(day, why)], n_ref, latest, days, reason, line).

    status ∈ {"ok", "missing", "unmeasured"}. why ∈ {"행 없음", "최신봉 HH:MM"}.
    """
    flow_db = flow_db or FLOW_DB
    raw_db = raw_db or RAW_DB
    now = now or _dt.datetime.now()
    days = int(days)
    since = max((now.date() - _dt.timedelta(days=days)).isoformat(), FLOW_START)
    today = now.date().isoformat()
    res = {"status": "unmeasured", "bad": [], "n_ref": 0, "latest": None,
           "days": days, "reason": "", "line": ""}

    for label, p in (("option_flow.db", flow_db), ("raw_data.db", raw_db)):
        if not os.path.exists(p):
            res["reason"] = "%s 없음 (%s)" % (label, p)
            res["line"] = format_line(res)
            return res

    try:
        con = _ro(raw_db)
        try:
            ref = sorted(r[0] for r in con.execute(
                "SELECT substr(ts,1,10) AS d FROM raw_candles WHERE ts >= ?"
                " GROUP BY d HAVING COUNT(*) >= ?", (since + " 00:00:00", int(min_bars))))
        finally:
            con.close()
        con = _ro(flow_db)
        try:
            q = ",".join("?" * len(OPTION_PRODUCTS))
            last = dict(con.execute(
                "SELECT trade_date, MAX(bar_time) FROM option_investor_flow"
                " WHERE trade_date >= ? AND product IN (%s) GROUP BY trade_date" % q,
                (since,) + OPTION_PRODUCTS).fetchall())
            row = con.execute("SELECT MAX(trade_date) FROM option_investor_flow").fetchone()
            res["latest"] = row[0] if row else None
        finally:
            con.close()
    except Exception as e:               # 테이블 부재·락 — 값을 지어내지 않는다
        res["reason"] = "조회 실패: %r" % (e,)
        res["line"] = format_line(res)
        return res

    if now.strftime("%H:%M") < SETTLE_HM:
        ref = [d for d in ref if d != today]
    ref = [d for d in ref if d >= FLOW_START]
    res["n_ref"] = len(ref)
    if not ref:
        res["reason"] = "기준선 없음 — %s 이후 raw_candles 에 %d봉 이상인 거래일이 없다" % (since, min_bars)
        res["line"] = format_line(res)
        return res

    for d in ref:
        mx = last.get(d)
        if mx is None:
            res["bad"].append((d, "행 없음"))
        elif mx < _close_ok_for(d):
            res["bad"].append((d, "최신봉 %s" % mx))
    res["status"] = "ok" if not res["bad"] else "missing"
    res["line"] = format_line(res)
    return res


def _safe_print(line):
    """콘솔 인코딩에 죽지 않는다 — 595차 음성대조 교훈(감시 장치가 자기 입을 닫으면 안 된다)."""
    try:
        print(line)
    except (UnicodeEncodeError, ValueError, OSError):
        try:
            print(line.encode("ascii", "backslashreplace").decode("ascii"))
        except Exception:
            pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=DEFAULT_DAYS)
    ap.add_argument("--flow-db", default=None)
    ap.add_argument("--raw-db", default=None)
    a = ap.parse_args()
    res = check(days=a.days, flow_db=a.flow_db, raw_db=a.raw_db)
    _safe_print(res["line"])
    return {"ok": 0, "missing": 1, "unmeasured": 2}[res["status"]]


if __name__ == "__main__":
    sys.exit(main())
