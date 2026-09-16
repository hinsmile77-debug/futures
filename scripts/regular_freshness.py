# -*- coding: utf-8 -*-
# scripts/regular_freshness.py — 정규 연결선물(10100) 적재 신선도 검사 (EOD 체인용)
"""수집이 멈춘 것을 **그날 안에** 알아채기 위한 검사.

왜 있는가 (2026-09-17 / MW0601 595차)
--------------------------------------
`regular_candles.db` 는 2026-09-11 하루 저녁의 손 백필 이후 **엿새간 갱신이 멈춰**
있었고, 그 사흘(09-14·15·16) 동안 **어떤 로그·경보도 울리지 않았다.**
EOD 체인은 매일 `LastTaskResult=0` 으로 성공했고, 「정규 10100 미수집」 문구는
대시보드의 피터 오프셋 경로에만 있어 **사람이 그 화면을 열어야** 보였다.
FP-CRITICAL(PSI 2개월 죽은 게이트)·TOX(한 달 죽은 섀도)와 같은 계열이다.

무엇을 재는가 — 휴장 달력을 새로 만들지 않는다
-----------------------------------------------
**미륵이 자신을 기준선으로 쓴다.**

    결손 = {raw_candles 에 봉이 있는 거래일} − {regular_candles(10100) 거래일}

미륵이가 돌지 않은 날(휴장·정전·PC 꺼짐)은 애초에 기준에서 빠지므로
`config/krx_holidays.py` 를 따로 참조할 필요가 없고 오탐도 없다.
「거래일이었는가」를 가장 잘 아는 것은 그날 실제로 봉을 담은 쪽이다.

규약
----
⚠ 456차(장중 라이브 DB 분석 금지)에 걸리지 않는다 — **EOD(15:50 이후) 전용**이며
  최근 `days` 일만 본다. 468MB 전수 스캔이 아니다. 두 DB 모두 `mode=ro` 로 연다.

⚠ 계측 4원칙 ②: 「DB 가 없다·못 읽었다」와 「결손 0」은 **다른 값**이다.
  전자는 `status="unmeasured"` 이며 결코 0 으로 표현하지 않는다.

⚠ 계측 4원칙 ③: 결손 목록을 자를 때는 **잔여 개수를 명시**한다(`… 외 N개`).

단독 실행
---------
    python scripts/regular_freshness.py            # 종료코드 0=정상 1=결손 2=미측정
    python scripts/regular_freshness.py --days 30
"""
from __future__ import print_function

import argparse
import datetime as _dt
import os
import sqlite3
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG_DB = os.path.join(_ROOT, "data", "db", "regular_candles.db")
RAW_DB = os.path.join(_ROOT, "data", "db", "raw_data.db")

REGULAR_CODE = "10100"
DEFAULT_DAYS = 10        # 기준선 창(달력일). EOD 매일 도므로 짧아도 된다
MIN_BARS = 10            # 이보다 적은 봉만 있는 날은 기준선에서 뺀다(세션 파편)
MAX_LIST = 10            # 로그 한 줄에 나열할 결손 일자 상한


def _ro(path):
    """읽기전용 연결 — 남의 DB 에 `-journal` 을 남기지 않는다(09-16 실측 사고)."""
    return sqlite3.connect("file:%s?mode=ro" % path.replace("\\", "/"),
                           uri=True, timeout=5.0)


def format_line(res):
    """`[RegularFresh] …` 한 줄. 상태별로 **문구 자체가 다르다** — 등급만 다르고
    문구가 같으면 로그를 훑는 사람이 구분하지 못한다."""
    if res["status"] == "unmeasured":
        return ("[RegularFresh] 미측정 — %s. 「결손 없음」이 아니다(계측 4원칙 ②)"
                % res["reason"])
    latest = res["latest"] or "없음"
    if res["status"] == "ok":
        return ("[RegularFresh] 최신 %s · 기준 %d거래일(최근 %d일) · 결손 0일"
                % (latest, res["n_ref"], res["days"]))
    miss = res["missing_days"]
    shown = ", ".join(miss[:MAX_LIST])
    more = "" if len(miss) <= MAX_LIST else " 외 %d개" % (len(miss) - MAX_LIST)
    return ("[RegularFresh] 결손 %d일 — %s%s | 최신 %s · 기준 %d거래일. "
            "복구: python scripts/collect_regular_futures.py --from %s --to %s"
            % (len(miss), shown, more, latest, res["n_ref"],
               miss[0].replace("-", ""), miss[-1].replace("-", "")))


def check(days=DEFAULT_DAYS, reg_db=None, raw_db=None,
          code=REGULAR_CODE, min_bars=MIN_BARS):
    """Returns:
        dict(status, latest, missing_days, n_ref, days, since, reason, line)
        status ∈ {"ok", "missing", "unmeasured"}
    """
    reg_db = reg_db or REG_DB
    raw_db = raw_db or RAW_DB
    days = int(days)
    since = (_dt.date.today() - _dt.timedelta(days=days)).isoformat()
    res = {"status": "unmeasured", "latest": None, "missing_days": [],
           "n_ref": 0, "days": days, "since": since, "reason": "", "line": ""}

    for label, p in (("regular_candles.db", reg_db), ("raw_data.db", raw_db)):
        if not os.path.exists(p):
            res["reason"] = "%s 없음 (%s)" % (label, p)
            res["line"] = format_line(res)
            return res

    try:
        con = _ro(raw_db)
        try:
            ref = set(r[0] for r in con.execute(
                "SELECT substr(ts,1,10) AS d FROM raw_candles"
                " WHERE ts >= ? GROUP BY d HAVING COUNT(*) >= ?",
                (since + " 00:00:00", int(min_bars))))
        finally:
            con.close()

        con = _ro(reg_db)
        try:
            have = set(r[0] for r in con.execute(
                "SELECT DISTINCT trade_date FROM regular_candles"
                " WHERE code = ? AND trade_date >= ?", (code, since)))
            row = con.execute(
                "SELECT MAX(trade_date) FROM regular_candles WHERE code = ?",
                (code,)).fetchone()
            res["latest"] = row[0] if row else None
        finally:
            con.close()
    except Exception as e:                       # 테이블 부재·락 — 값을 지어내지 않는다
        res["reason"] = "조회 실패: %r" % (e,)
        res["line"] = format_line(res)
        return res

    res["n_ref"] = len(ref)
    if not ref:
        # 기준선이 비면 「결손 0」이 아니라 **잴 수 없음**이다.
        res["reason"] = ("기준선 없음 — 최근 %d일 raw_candles 에 %d봉 이상인 거래일이 "
                         "하나도 없다" % (days, min_bars))
        res["line"] = format_line(res)
        return res

    res["missing_days"] = sorted(ref - have)
    res["status"] = "ok" if not res["missing_days"] else "missing"
    res["line"] = format_line(res)
    return res


def _safe_print(line):
    """🔴 [595차 음성대조 산물] 콘솔 인코딩에 죽지 않는다.

    이 모듈은 고치려던 결함과 **같은 계열의 버그를 자기 안에 가지고 있었다** —
    파이프로 리디렉션하면 stdout 이 cp949 가 돼 `—` 한 글자에 터졌고,
    그 때 종료코드가 **1** 이라 「결손 있음」과 구별되지 않았다.
    감시 장치가 자기 입을 닫으면 감시가 아니다.
    """
    try:
        print(line)
    except (UnicodeEncodeError, ValueError, OSError):
        try:
            print(line.encode("ascii", "backslashreplace").decode("ascii"))
        except Exception:
            pass                     # 찍지 못해도 종료코드는 살려 보낸다


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=DEFAULT_DAYS)
    ap.add_argument("--reg-db", default=None)
    ap.add_argument("--raw-db", default=None)
    a = ap.parse_args()
    res = check(days=a.days, reg_db=a.reg_db, raw_db=a.raw_db)
    _safe_print(res["line"])
    return {"ok": 0, "missing": 1, "unmeasured": 2}[res["status"]]


if __name__ == "__main__":
    sys.exit(main())
