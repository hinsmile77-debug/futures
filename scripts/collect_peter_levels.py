# -*- coding: utf-8 -*-
# scripts/collect_peter_levels.py — 피터리 역설계 검증용 풀세션 1분봉 수집기 (Cybos Plus)
"""미륵이 raw_candles 가 15:09 에서 끊기고 **미니 당월물만** 담고 있어서
피터리 검증에 두 구멍이 있다:

  (A) 15:10~15:45 구간이 없다 → 8/3 "990 위에서 끝났다", 8/4 "15:14 1000 청산" 검증 불가
  (B) 정규 근월물 시세가 없다 → 그의 레벨이 미니 기준인지 정규 기준인지 확정 불가

이 스크립트는 `CpSysDib.FutOptChart` 로 **지정 종목·지정 기간의 1분봉 전체**를 받아
CSV 로 떨어뜨린다. 읽기 전용 TR 만 쓰고 주문·계좌 TR 은 호출하지 않으며,
미륵이 DB 를 열지도 않는다(456차 규약).

실행 (py37_32 32-bit · Cybos Plus 로그인 · 관리자 권한 권장):
    python scripts/collect_peter_levels.py --list
        → 현재 조회 가능한 선물 코드·종목명 전량 출력 (정규/미니 구분용)

    python scripts/collect_peter_levels.py --auto
        → 피터리 검증에 필요한 날짜를 후보 코드 전부로 시도 (권장 첫 실행)

    python scripts/collect_peter_levels.py --fetch A0568:20260803-20260804 --fetch A0569:20260904-20260904
        → 명시 수집

출력: <OUT_DIR>/<코드>_<시작>_<종료>_1m.csv  +  collect_summary.txt
"""
from __future__ import print_function

import argparse
import csv
import os
import platform
import sys
import threading
import time

OUT_DIR_DEFAULT = r"C:\Users\82108\PycharmProjects\Sindong\가격레벨\cybos_collect"

# FutOptChart 필드: 0=날짜 1=시간 2=시가 3=고가 4=저가 5=종가 8=거래량 27=미결제약정
FIELDS_BASE = [0, 1, 2, 3, 4, 5, 8, 27]
FIELDS_EXT = FIELDS_BASE + [10, 11]          # 누적매도/누적매수 (분·틱 한정)
NAMES_BASE = ["date", "time", "open", "high", "low", "close", "volume", "oi"]
NAMES_EXT = NAMES_BASE + ["cum_sell", "cum_buy"]

# 피터리 검증에 필요한 (설명, 시작일, 종료일)
TARGETS = [
    ("8/3-8/4 장막판 검증", "20260803", "20260804"),
    ("9/4 레벨 검증", "20260904", "20260904"),
    ("9/11 레벨 검증", "20260911", "20260911"),
]

_LOG = []


def P(msg):
    print(msg)
    sys.stdout.flush()
    _LOG.append(msg)


# ───────────────────────── COM BlockRequest (STA + 메시지펌프) ─────────────────────────
def block_request(progid, input_pairs, reader, timeout_sec=60):
    """api_connector._run_block_request 와 같은 규칙: Dispatch~읽기를 한 워커 스레드에서.

    메인 스레드는 PumpWaitingMessages 로 대기한다(없으면 Cybos 가 데드락).
    """
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


def wait_request_quota():
    """Cybos 요청 제한(15초 60건)에 걸리면 남은 시간만큼 쉰다."""
    try:
        import win32com.client as win32
        cyb = win32.Dispatch("CpUtil.CpCybos")
        remain = int(cyb.GetLimitRemainCount(1))      # 1 = 시세 요청
        if remain <= 1:
            ms = int(cyb.LimitRequestRemainTime)
            P("      [quota] 남은요청=%d → %.1f초 대기" % (remain, ms / 1000.0))
            time.sleep(ms / 1000.0 + 0.3)
    except Exception:
        time.sleep(0.25)


# ───────────────────────── 종목코드 열거 ─────────────────────────
def list_codes():
    import win32com.client as win32
    out = []
    for progid in ("CpUtil.CpFutureCode", "CpUtil.CpKFutureCode"):
        try:
            o = win32.Dispatch(progid)
            n = int(o.GetCount())
        except Exception as e:
            P("  [%s] 사용 불가: %r" % (progid, e))
            continue
        P("  [%s] %d 종목" % (progid, n))
        for i in range(n):
            try:
                code = str(o.GetData(0, i))
                name = str(o.GetData(1, i))
            except Exception:
                continue
            out.append((progid, code, name))
            P("      %-10s %s" % (code, name))
    return out


# ───────────────────────── 분봉 수집 ─────────────────────────
def fetch_minutes(code, start_ymd, end_ymd):
    """기간 요청으로 1분봉 전량. (rows, colnames) 반환. 실패 시 (None, err)."""
    last_err = ""
    for fields, names in ((FIELDS_EXT, NAMES_EXT), (FIELDS_BASE, NAMES_BASE)):
        def _reader(obj, _f=fields):
            n = int(obj.GetHeaderValue(3))
            rows = []
            for i in range(n):
                rows.append([obj.GetDataValue(c, i) for c in range(len(_f))])
            return rows

        # 0=코드 1=요청구분('1'기간/'2'개수) 2=종료일 3=시작일 5=필드 6=차트구분('m') 7=주기 8=갭보정
        inputs = [(0, code), (1, ord("1")), (2, int(end_ymd)), (3, int(start_ymd)),
                  (5, fields), (6, ord("m")), (7, 1), (8, ord("0"))]
        wait_request_quota()
        try:
            ret, status, msg, data = block_request("CpSysDib.FutOptChart", inputs, _reader)
        except Exception as e:
            last_err = "예외 %r" % (e,)
            continue
        if ret not in (0, None) or status != 0 or not data:
            last_err = "ret=%s status=%s msg=%s rows=%s" % (ret, status, msg, len(data or []))
            continue
        rows = sorted(data, key=lambda r: (int(r[0]), int(r[1])))
        return rows, names
    return None, last_err


def summarize(code, rows, names):
    by_day = {}
    for r in rows:
        by_day.setdefault(int(r[0]), []).append(r)
    for d in sorted(by_day):
        rs = sorted(by_day[d], key=lambda x: int(x[1]))
        ti = names.index("time")
        times = [int(x[ti]) for x in rs]
        hi = max(float(x[names.index("high")]) for x in rs)
        lo = min(float(x[names.index("low")]) for x in rs)
        o = float(rs[0][names.index("open")])
        c = float(rs[-1][names.index("close")])
        after1510 = [t for t in times if t >= 1510]
        P("      %d  봉%4d  %04d~%04d  O%.2f H%.2f L%.2f C%.2f | 15:10이후 %d봉 %s"
          % (d, len(rs), times[0], times[-1], o, hi, lo, c, len(after1510),
             ("마지막 %04d" % after1510[-1]) if after1510 else "없음"))


def save_csv(out_dir, code, start_ymd, end_ymd, rows, names):
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    path = os.path.join(out_dir, "%s_%s_%s_1m.csv" % (code, start_ymd, end_ymd))
    f = open(path, "w")
    try:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(names)
        for r in rows:
            w.writerow(r)
    finally:
        f.close()
    P("      저장: %s (%d행)" % (path, len(rows)))
    return path


# ───────────────────────── main ─────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true", help="선물 종목코드 전량 출력")
    ap.add_argument("--auto", action="store_true", help="피터리 검증 대상 날짜를 후보 코드 전부로 시도")
    ap.add_argument("--fetch", action="append", default=[], help="CODE:YYYYMMDD-YYYYMMDD (반복 가능)")
    ap.add_argument("--codes", default="", help="--auto 에서 쓸 코드 목록(쉼표). 기본: 자동 열거 + 소멸 후보")
    ap.add_argument("--out", default=OUT_DIR_DEFAULT)
    a = ap.parse_args()

    if platform.architecture()[0] != "32bit":
        P("[중단] 32-bit Python(py37_32)에서 실행할 것 — Cybos COM 요구사항")
        return 2
    try:
        import win32com.client as win32
    except ImportError:
        P("[중단] pywin32(32-bit) 없음")
        return 2
    cyb = win32.Dispatch("CpUtil.CpCybos")
    if not cyb.IsConnect:
        P("[중단] Cybos Plus 미연결(IsConnect=0). 로그인 + 관리자 권한으로 실행할 것.")
        return 1
    P("[OK] Cybos Plus 연결 확인. 출력 폴더: %s" % a.out)

    listed = []
    if a.list or a.auto:
        P("\n=== 선물 종목코드 열거 ===")
        listed = list_codes()

    if a.list and not a.auto and not a.fetch:
        _write_log(a.out)
        return 0

    jobs = []
    for spec in a.fetch:
        try:
            code, rng = spec.split(":", 1)
            s, e = rng.split("-", 1)
            jobs.append((code.strip(), s.strip(), e.strip()))
        except Exception:
            P("[무시] --fetch 형식 오류: %s" % spec)

    if a.auto:
        if a.codes:
            cand = [c.strip() for c in a.codes.split(",") if c.strip()]
        else:
            cand = [c for (_p, c, _n) in listed]
            # 이미 소멸한 월물도 차트 TR 이 받아 주는지 시험한다
            for extra in ("A0568", "A0569", "A056A", "A056B", "A056C"):
                if extra not in cand:
                    cand.append(extra)
        P("\n=== 자동 수집 후보 코드 %d개: %s ===" % (len(cand), ", ".join(cand)))
        for desc, s, e in TARGETS:
            for code in cand:
                jobs.append((code, s, e))

    ok = fail = 0
    seen = set()
    P("\n=== 수집 시작 (%d건) ===" % len(jobs))
    for code, s, e in jobs:
        key = (code, s, e)
        if key in seen:
            continue
        seen.add(key)
        P("  %s  %s~%s" % (code, s, e))
        rows, info = fetch_minutes(code, s, e)
        if rows is None:
            P("      실패: %s" % info)
            fail += 1
            continue
        names = info
        summarize(code, rows, names)
        save_csv(a.out, code, s, e, rows, names)
        ok += 1

    P("\n=== 완료: 성공 %d / 실패 %d ===" % (ok, fail))
    _write_log(a.out)
    return 0


def _write_log(out_dir):
    try:
        if not os.path.isdir(out_dir):
            os.makedirs(out_dir)
        p = os.path.join(out_dir, "collect_summary.txt")
        f = open(p, "w")
        try:
            f.write("\n".join(_LOG) + "\n")
        finally:
            f.close()
        print("[로그] %s" % p)
    except Exception as e:
        print("[로그 저장 실패] %r" % e)


if __name__ == "__main__":
    sys.exit(main())
