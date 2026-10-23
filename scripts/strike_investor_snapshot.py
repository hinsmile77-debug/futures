# -*- coding: utf-8 -*-
"""[MW0601 704차] CpSvr9842 기간 보유(= HTS [9842] `_P`) 스냅샷 · 백필 · HTS 대사

장후에 하루 1회 돌리면 그날의 `YYMMDD_P.xls` 수동 저장을 대신한다. 결과는
`strike_investor.db.strike_investor_hold` 에 전 행 저장되고, 같은 날짜의 HTS `_P`
파일이 `data/db/option_hts/` 에 있으면 칸 단위로 대사한다.

🔴 실계좌 로그인 전용 — 모의 로그인이면 차단 문구를 찍고 rc=3 으로 끝난다(아무것도 쓰지 않는다).

사용
  conda run --no-capture-output -n py37_32 python scripts\\strike_investor_snapshot.py            # 오늘
  conda run --no-capture-output -n py37_32 python scripts\\strike_investor_snapshot.py --end 20261021
  conda run --no-capture-output -n py37_32 python scripts\\strike_investor_snapshot.py --from 20260901 --to 20261021
  옵션: --months 1,2  (기본 1)  --no-verify

rc: 0 정상(휴장일 건너뜀 포함) · 1 일부 실패/대사 불일치 · 2 너무 이름 · 3 차단
    [710차] 대사 불일치라도 HTS `_P` 가 그날 15:46 이전에 저장된 파일이면 rc 에 넣지 않는다
    (로그에 「참고」로만 남긴다) — 종가 단일가가 빠진 쪽은 파일이다.

🔴 **오늘 날짜는 15:50 이후에만 받는다**(`--force` 로 무시). 2026-10-22 실측: 15:44:57 에 저장한
   HTS `_P` 와 16:16 API 가 34칸 달랐다 — 15:45 종가 단일가 체결(개인↔외인 15/17 쌍 상쇄)이
   그 사이에 들어왔다. 예약작업 `\\Mireuk\\Mireuk_StrikeInvestorSnapshot` 이 16:25 에 돈다.
로그: logs/YYYYMMDD_STRIKE_SNAPSHOT.log
"""
from __future__ import print_function

import argparse
import datetime
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from utils.dll_bootstrap import ensure_conda_dll_path  # noqa: E402

ensure_conda_dll_path()

try:
    sys.stdout.reconfigure(errors="replace")   # cp949 콘솔
except Exception:
    pass

import json  # noqa: E402

HTS_DIR = os.path.join(ROOT, "data", "db", "option_hts")
# HTS 머리행 이름 → API 투자자 인덱스 (probe_cpsvr9842 와 같은 표)
HTS_NAME_TO_IDX = {"개인": 0, "외국인": 1, "기관계": 2, "금융투자": 3, "투신": 5}


def _log(msg):
    """화면 + logs/YYYYMMDD_STRIKE_SNAPSHOT.log — 예약작업은 화면이 없다."""
    line = "%s %s" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg)
    print(line)
    try:
        p = os.path.join(ROOT, "logs", "%s_STRIKE_SNAPSHOT.log"
                         % datetime.date.today().strftime("%Y%m%d"))
        with open(p, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def _days(a, b):
    from utils.time_utils import is_trading_day
    d0 = datetime.datetime.strptime(a, "%Y%m%d").date()
    d1 = datetime.datetime.strptime(b, "%Y%m%d").date()
    out = []
    while d0 <= d1:
        if is_trading_day(datetime.datetime.combine(d0, datetime.time(12))):
            out.append(d0.strftime("%Y%m%d"))
        d0 += datetime.timedelta(days=1)
    return out


def _wait_quota(cy, need):
    for _ in range(60):
        if cy.GetLimitRemainCount(1) >= need:
            return
        time.sleep(max(cy.LimitRequestRemainTime, 500) / 1000.0 + 0.2)


def hts_saved_before_close(path, end):
    """[MW0601 710차] HTS 파일이 그날 15:46 이전에 저장됐나 — 그러면 15:45 종가 단일가가 빠져 있다.

    2026-10-22 실측: 15:44:57 저장 `_P` vs 16:25 API 가 34칸 달랐다(rc=1). 틀린 쪽은 파일이다.
    그런 파일과의 불일치를 수집 실패로 세면 진짜 실패와 섞인다. 반환 (bool, 저장시각 문자열).
    """
    mt = datetime.datetime.fromtimestamp(os.path.getmtime(path))
    close = datetime.datetime.combine(datetime.datetime.strptime(end, "%Y%m%d").date(),
                                      datetime.time(15, 46))
    return mt < close, mt.strftime("%Y-%m-%d %H:%M:%S")


def _verify(sif, end, months):
    """같은 날짜 HTS _P 파일과 칸 대사. 반환 (일치, 전체, 불일치 예, 경로) 또는 None(파일 없음)."""
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    from probe_cpsvr9842 import read_hts
    path = os.path.join(HTS_DIR, "%s_P.xls" % end[2:])
    if not os.path.exists(path):
        return None
    hts, unit, _ = read_hts(path)
    field = "qty" if unit == "contract" else "amt"
    td = "%s-%s-%s" % (end[:4], end[4:6], end[6:])
    con = sif._conn()
    rows = con.execute("SELECT cp, strike, %s FROM strike_investor_hold "
                       "WHERE trade_date=? AND month='1'" % ("qty" if field == "qty" else "amt"),
                       (td,)).fetchall()
    con.close()
    api = {(cp, float(k)): json.loads(v) for cp, k, v in rows if k is not None}
    same = n = 0
    bad = []
    for k, cells in hts.items():
        for (cp, idx), hv in cells.items():
            av = api.get((cp, float(k)))
            n += 1
            if av is not None and abs(av[idx] - hv) < (1e-6 if field == "qty" else 0.01):
                same += 1
            else:
                bad.append((cp, k, idx, None if av is None else av[idx], hv))
    return same, n, bad[:5], path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--end", help="YYYYMMDD (기본 오늘)")
    ap.add_argument("--from", dest="d_from")
    ap.add_argument("--to", dest="d_to")
    ap.add_argument("--months", default="1")
    ap.add_argument("--no-verify", action="store_true")
    ap.add_argument("--force", action="store_true", help="오늘 15:50 이전 실행 허용")
    a = ap.parse_args()

    now = datetime.datetime.now()
    today = now.strftime("%Y%m%d")
    if not a.d_from and (a.end or today) == today:
        # 휴장일은 Cybos 를 부르기 전에 끝낸다 — 예약작업이 월–금 매일 돌므로
        # 막지 않으면 휴장일 실패가 진짜 실패와 섞인다(backfill_option_flow.py 와 같은 이유).
        try:
            from utils.time_utils import is_trading_day
            if not is_trading_day(now):
                _log("건너뜀 — %s 는 KRX 휴장일이다." % today)
                return 0
        except Exception:
            pass                                    # 모르면 돌려 본다(실패는 로그에 남는다)
        if now.time() < datetime.time(15, 50) and not a.force:
            _log("거부 — 오늘 기간 보유는 15:50 이후에 받는다(15:45 종가 단일가 반영). --force 로 무시.")
            return 2

    from config import settings
    from collection.cybos.strike_investor_flow import StrikeInvestorFlow, BlockedError
    import win32com.client as wc

    cy = wc.Dispatch("CpUtil.CpCybos")
    _log("connect=%s server_type=%s remain(1)=%s" % (
        cy.IsConnect, cy.ServerType, cy.GetLimitRemainCount(1)))
    if cy.IsConnect != 1:
        _log("Cybos 미연결 — 중단")
        return 1

    if a.d_from:
        days = _days(a.d_from, a.d_to or datetime.date.today().strftime("%Y%m%d"))
    else:
        days = [a.end or datetime.date.today().strftime("%Y%m%d")]
    months = tuple(m.strip() for m in a.months.split(",") if m.strip())
    db = os.path.join(ROOT, getattr(settings, "STRIKE_INVESTOR_FLOW_DB", "data/db/strike_investor.db"))
    sif = StrikeInvestorFlow(db, months=months)

    rc = 0
    for end in days:
        _wait_quota(cy, 10 + 2 * len(months))
        try:
            res = sif.fetch_period(end, months)
        except BlockedError as exc:
            _log("🔴 계좌등급 차단 — 실계좌 로그인 전용: %s" % exc)
            return 3
        line = "%s  " % end + "  ".join(
            "%s rows=%s pages=%s unmapped=%s inv_bad=%s%s" % (
                k, v.get("rows"), v.get("pages"), v.get("unmapped"), v.get("inv_bad"),
                (" ❌ " + v["msg"]) if v.get("msg") else "")
            for k, v in sorted(res.items()))
        if any((not v.get("ok")) or v.get("unmapped") or v.get("inv_bad") for v in res.values()):
            rc = 1
        if not a.no_verify:
            vr = _verify(sif, end, months)
            if vr is None:
                line += "  | HTS _P 없음(대사 생략)"
            else:
                same, n, bad, hpath = vr
                line += "  | HTS 대사 %d/%d칸" % (same, n)
                if same != n:
                    early, saved = hts_saved_before_close(hpath, end)
                    if early:
                        # 파일이 종가 단일가 전에 저장됨 — 대사 기준이 낡았다. 참고로만 남긴다.
                        line += (" 불일치 예 %s (참고 — HTS _P 가 %s 저장, 15:45 종가 단일가 이전이라"
                                 " 대사 기준 아님 · rc 미반영)" % (bad, saved))
                    else:
                        rc = 1
                        line += " 불일치 예 %s" % bad
        _log(line)
    _log("DB: %s rc=%d" % (db, rc))
    return rc


if __name__ == "__main__":
    sys.exit(main())
