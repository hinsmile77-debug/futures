# -*- coding: utf-8 -*-
"""option_flow 결손 구간 백필 — CpSvrNew7222 type 3 페이징.

[MW0601 611차 후속 / 2026-09-21]

왜 필요한가
-----------
라이브 수집기(`collection/cybos/weekly_option_flow.py`)는 매분 **최근 18행**만
받는다. 그래서 프로세스가 늦게 뜨거나 중간에 재기동하면 그 이전 구간이 비어 있다.
실제로 2026-09-21 재기동 직후 DB 의 봉 범위가 `11:42~12:26` 이었다 — 오전이 통째로
없었다.

7222 는 `SetInputValue(3, HHMM)` 으로 **그 시각 직전** 18행을 준다. 그걸 뒤로
밀면서 반복하면 하루 전체가 메워진다. 이 스크립트가 그 일을 한다.

⚠ 한 페이지가 덮는 시간은 상품마다 다르다 — 옵션은 1분 간격이라 18분,
  현물은 1~2분 불규칙이라 26분쯤이다. 그래서 **가장 촘촘한 쪽(18분)** 에 맞춰
  페이지 간격을 잡는다. 넉넉하게 겹치는 것은 문제가 없다(upsert 라 중복은 덮어쓴다).

요청량
------
7상품 x 3주체 x N페이지. 09:00~15:35 전 구간이면 N=22 라 약 460요청이다.
7222 는 **type1(시세) 한도**(15초당 60건)를 쓰고 라이브와 공유하므로,
기본 `--sleep 0.3`(15초당 50건)으로 여유를 둔다.

사용:
    conda run -n py37_32 python scripts/backfill_option_flow.py              # 09:00~현재
    conda run -n py37_32 python scripts/backfill_option_flow.py --from 09:00 --to 11:45
    conda run -n py37_32 python scripts/backfill_option_flow.py --dry-run
    (32-bit 필수)

장중에도 돌 수 있게 열어두되 가드는 건다 — 결손은 보통 장중에 발견되고,
백필은 라이브 DB 가 아니라 별도 option_flow.db 를 쓴다.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.dll_bootstrap import ensure_conda_dll_path   # noqa: E402

ensure_conda_dll_path()

import argparse      # noqa: E402
import datetime      # noqa: E402
import sqlite3       # noqa: E402
import time          # noqa: E402

from utils.analysis_db import guard_intraday, utf8_console   # noqa: E402
from collection.cybos.weekly_option_flow import (       # noqa: E402
    WeeklyOptionFlow, PRODUCTS, INVESTORS,
)

# ── [MW0601 2026-10-04] 장후 재수집이 8거래일 조용히 실패한 사고의 대책 ──────────
#
# 예약작업 `Mireuk_OptionFlowBackfill_1605` 는 2026-09-21 등록 이래 **하루도 성공하지
# 않았다**(LastTaskResult=2, DB 의 15:35 이후 행 0건). 그런데 아무도 몰랐다 —
# 예약작업은 stdout 을 어디에도 남기지 않기 때문이다. 그래서:
#   ① 실행마다 `logs/<YYYYMMDD>_OPTION_BACKFILL.log` 에 같은 내용을 남긴다
#      (인코딩 명시 — 예약작업은 PYTHONUTF8 을 못 세운다, 595차 교훈)
#   ② 미접속 실패에 **권한 수준 진단**을 붙인다(그날의 실제 원인)
#   ③ 끝난 뒤 **마감 구간을 확보했는지** 보고, 못 했으면 종료코드 3 으로 드러낸다
#      — 「적재는 됐다」와 「목적을 달성했다」는 다른 값이다(계측 4원칙 ⑤)
#
# 종료코드: 0 정상 · 2 Cybos 미접속/다른 날짜 지정 거부 · 3 적재했으나 마감 구간 미확보
EXIT_NOT_CONNECTED = 2
EXIT_NO_CLOSE = 3
# 마감 기준은 신선도 검사와 **한 곳**에서 정의한다(만기일 조기마감 포함). 두 곳에
# 따로 두면 한쪽만 고쳐져 「백필은 성공, 검사는 결손」 같은 엇갈림이 생긴다.
from scripts.option_flow_freshness import CLOSE_OK, _close_ok_for   # noqa: E402


class _Tee(object):
    """stdout 을 콘솔과 로그 파일 양쪽에 쓴다. 파일 쪽 실패가 본 작업을 막지 않는다."""

    def __init__(self, stream, fh):
        self._s, self._f = stream, fh

    def write(self, data):
        try:
            self._s.write(data)
        except Exception:
            pass
        try:
            self._f.write(data)
            self._f.flush()
        except Exception:
            pass

    def flush(self):
        for x in (self._s, self._f):
            try:
                x.flush()
            except Exception:
                pass


def _open_run_log():
    """`logs/<YYYYMMDD>_OPTION_BACKFILL.log` 를 append 로 연다. 실패하면 None."""
    try:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        d = os.path.join(root, "logs")
        os.makedirs(d, exist_ok=True)
        path = os.path.join(d, "%s_OPTION_BACKFILL.log" % datetime.date.today().strftime("%Y%m%d"))
        fh = open(path, "a", encoding="utf-8")
        fh.write("\n===== %s pid=%d argv=%s =====\n"
                 % (datetime.datetime.now().isoformat(timespec="seconds"), os.getpid(), " ".join(sys.argv[1:])))
        return fh
    except Exception:
        return None


def _is_elevated():
    """이 프로세스가 관리자(승격)로 도는가. 판정 불가면 None(미측정 ≠ False)."""
    try:
        import ctypes
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return None


def _is_holiday(now):
    """KRX 휴장일(주말·공휴일)이면 True. 판정 불가면 False — 모르면 돌려 본다(실패는 로그에 남는다)."""
    try:
        from utils.time_utils import is_trading_day
        return not is_trading_day(now)
    except Exception:
        return False


def _latest_option_bar(db, day):
    """그날 옵션 상품의 최신 봉 'HH:MM'. 없거나 못 읽으면 None."""
    try:
        con = sqlite3.connect(db)
        row = con.execute(
            "SELECT MAX(bar_time) FROM option_investor_flow WHERE trade_date=? "
            "AND product != 'kospi_spot'", (day,)).fetchone()
        con.close()
        return row[0] if row else None
    except Exception:
        return None

# 한 페이지가 덮는 분 — 옵션(1분 간격 x 18행)이 가장 촘촘하다.
PAGE_SPAN_MIN = 18

# 🔴 요청 한도는 **라이브와 공유한다.** 7222 는 type1(시세) 한도(15초당 60건)를 쓰고,
#   한 페이지가 7상품 x 3주체 = 21요청을 거의 즉시(각 5~7ms) 쏜다. 페이지 사이
#   sleep 만으로는 15초 창에 수백 건이 몰릴 수 있다 — 그러면 내가 한도를 다 써서
#   **미륵이의 수급 수집(7221·8111)이 실패한다.** 매 페이지 전에 잔여 한도를 보고
#   부족하면 원천이 알려주는 시간만큼 기다린다.
QUOTA_TYPE_QUOTE = 1        # CpCybos.GetLimitRemainCount(1) = 시세 요청
QUOTA_MIN_REMAIN = 25       # 한 페이지(21) + 라이브 몫 여유


def wait_for_quota(verbose: bool = False) -> None:
    """잔여 시세요청 한도가 QUOTA_MIN_REMAIN 이상이 될 때까지 기다린다."""
    try:
        from win32com.client import Dispatch
        cyb = Dispatch("CpUtil.CpCybos")
    except Exception:
        time.sleep(1.0)      # 조회 못 하면 보수적으로 쉰다
        return
    waited = 0.0
    while True:
        try:
            remain = int(cyb.GetLimitRemainCount(QUOTA_TYPE_QUOTE))
        except Exception:
            return
        if remain >= QUOTA_MIN_REMAIN:
            if verbose and waited:
                print("      한도 회복 대기 %.1fs (잔여 %d)" % (waited, remain))
            return
        try:
            ms = int(cyb.LimitRequestRemainTime)
        except Exception:
            ms = 1000
        nap = max(ms / 1000.0, 0.3)
        time.sleep(nap)
        waited += nap
        if waited > 60:      # 이상 상황 — 무한 대기하지 않는다
            print("      ⚠ 한도 회복이 60초를 넘겼다 (잔여 %d) — 계속 진행" % remain)
            return


def require_cybos_connection():
    """Cybos 접속 상태를 먼저 확인한다 — 미연결이면 기다리지 않고 끊는다.

    🔴 `wait_for_quota` 는 잔여 한도가 모자라면 기다린다. 그런데 **미연결일 때도
       `GetLimitRemainCount` 는 0 을 준다** — 원천이 「미측정」과 「소진」을 같은
       값으로 표현한다(계측 4원칙 ②: 미측정 != 0). 그대로 두면 페이지마다 60초
       상한을 다 쓰고, 15페이지면 15분을 조용히 버린 뒤 `순증 0행` 만 남는다.
       접속은 한도와 달리 **기다린다고 회복되지 않으므로** 여기서 끊는다.

    실측 근거(MW0602 2026-09-21): 비승격 실행이 10분 30초 동안 DB 행 증가 0.
    Cybos Plus(coStarter)가 승격으로 돌아 UIPI 가 막은 것이었고, 비승격 프로세스는
    자기 DibServer 를 새로 띄워 `U-CYBOS가 서버에 접속되어 있지 않습니다` 로 전량
    실패했다. 미륵이 런처가 스스로 UAC 승격하는 이유와 같다.

    Returns:
        "" 이면 정상. 아니면 사람이 읽을 사유 문자열.
    """
    try:
        from win32com.client import Dispatch
        cyb = Dispatch("CpUtil.CpCybos")
        connected = int(cyb.IsConnect)
    except Exception as exc:
        return "CpCybos COM 을 열지 못했다: %s" % exc
    if not connected:
        elev = _is_elevated()
        return ("Cybos Plus 에 접속돼 있지 않다 (IsConnect=0).\n"
                "    - 이 프로세스 승격(관리자) = %s\n"
                "    - Cybos Plus 가 로그인돼 있는지 확인할 것\n"
                "    - **Cybos 와 이 프로세스의 권한 수준이 같아야 한다.** 다르면 COM 이\n"
                "      기존 Cybos 에 붙지 못하고 미접속 DibServer 를 새로 띄워 전량 실패한다.\n"
                "        · Cybos 승격(CREON·MW0602)  → 예약작업 -RunLevel Highest\n"
                "        · Cybos 비승격(CYBOS·MW0601) → 예약작업 -RunLevel Limited\n"
                "      (2026-09-21 – 10-02 MW0601: Highest 로 등록돼 8거래일 전부 이 사유로 실패)"
                % ({True: "예", False: "아니오", None: "판정 불가"}[elev]))
    return ""


def _hhmm(t: datetime.time) -> int:
    return t.hour * 100 + t.minute


def _parse_hhmm(s: str) -> datetime.time:
    h, m = s.split(":")
    return datetime.time(int(h), int(m))


def build_pages(t_from: datetime.time, t_to: datetime.time):
    """[t_from, t_to] 를 덮는 type 3 시각 목록 (뒤에서 앞으로)."""
    start = t_from.hour * 60 + t_from.minute
    end = t_to.hour * 60 + t_to.minute
    pages = []
    cur = end + 1                      # type3 는 '직전' 을 주므로 +1
    while cur > start:
        pages.append((cur // 60) * 100 + (cur % 60))
        cur -= PAGE_SPAN_MIN
    return pages


def main() -> int:
    ap = argparse.ArgumentParser(description="option_flow 결손 백필")
    ap.add_argument("--from", dest="t_from", default="09:00", help="시작 HH:MM (기본 09:00)")
    ap.add_argument("--to", dest="t_to", default="", help="끝 HH:MM (기본: 현재)")
    ap.add_argument("--date", default="",
                    help="거래일 YYYY-MM-DD (기본: 오늘). ⚠ 오늘만 허용 — 7222 는 당일 데이터만 준다")
    ap.add_argument("--sleep", type=float, default=0.3, help="요청 간 대기(초)")
    ap.add_argument("--dry-run", action="store_true", help="페이지만 계산하고 끝낸다")
    ap.add_argument("--db", default="data/db/option_flow.db")
    args = ap.parse_args()

    # 콘솔 인코딩 가드 + 실행 로그 — 예약작업은 stdout 을 남기지 않는다(파일 위 주석).
    utf8_console()
    _log_fh = None if args.dry_run else _open_run_log()
    if _log_fh is not None:
        sys.stdout = _Tee(sys.stdout, _log_fh)

    today = datetime.date.today().isoformat()
    # 🔴 [2026-10-04] 다른 날짜는 거부한다. 7222 에는 **날짜 입력이 없어** 항상 오늘
    #   데이터를 돌려준다. 그런데 `--date` 는 저장 라벨만 바꾸므로, 10/6 에
    #   `--date 2026-10-02` 로 돌리면 **10/6 데이터가 10/2 이름으로 덮어써진다**
    #   — 지난 기록을 조용히 오염시키는 경로였다(실행된 적은 없다).
    if args.date and args.date != today:
        print("중단 — --date %s 는 오늘(%s)이 아니다. CpSvrNew7222 는 당일 데이터만 주므로 "
              "지난 날짜는 복구할 수 없다. 다른 날짜로 저장하면 그날 기록을 오늘 값으로 덮어쓴다."
              % (args.date, today))
        return EXIT_NOT_CONNECTED

    # 휴장일은 Cybos 를 부르기 전에 끝낸다. 예약작업은 월–금 매일 돌므로, 막지 않으면
    # 휴장일마다 「미접속(2)」이 찍혀 **진짜 실패와 섞인다**(2026-10-05 대체공휴일이 첫 사례).
    # COM 을 부르지 않는 것 자체도 목적이다 — 미로그인 상태에서 부르면 빈 DibServer 가 뜬다.
    if _is_holiday(datetime.datetime.now()):
        print("건너뜀 — %s 는 KRX 휴장일이다(7222 에 그날 데이터가 없다)." % today)
        return 0

    if not args.dry_run:
        guard_intraday("backfill_option_flow")

    t_from = _parse_hhmm(args.t_from)
    t_to = _parse_hhmm(args.t_to) if args.t_to else datetime.datetime.now().time()
    day = today
    pages = build_pages(t_from, t_to)
    n_req = len(pages) * len(PRODUCTS) * len(INVESTORS)

    print("백필 %s  %02d:%02d~%02d:%02d" % (day, t_from.hour, t_from.minute,
                                            t_to.hour, t_to.minute))
    # 한도(15초당 60건)가 실질 하한을 정한다 — sleep 보다 이쪽이 크다.
    eta_quota = n_req / 60.0 * 15.0
    print("  페이지 %d개 (간격 %d분) x 상품 %d x 주체 %d = **%d 요청**"
          % (len(pages), PAGE_SPAN_MIN, len(PRODUCTS), len(INVESTORS), n_req))
    print("  예상 %.0f초 (요청한도 15초/60건 기준. sleep 기준은 %.0f초)"
          % (max(eta_quota, n_req * args.sleep), n_req * args.sleep))
    print("  type3 시각: %s%s" % (pages[:6], " …" if len(pages) > 6 else ""))
    if args.dry_run:
        return 0

    # 🔴 한도 대기 루프에 들어가기 전에 접속부터 확인한다 — 위 함수 주석 참조.
    _conn_err = require_cybos_connection()
    if _conn_err:
        print("  중단 — %s" % _conn_err)
        return EXIT_NOT_CONNECTED

    # 사전 상태
    def _span():
        try:
            con = sqlite3.connect(args.db)
            row = con.execute(
                "SELECT COUNT(*), MIN(bar_time), MAX(bar_time) "
                "FROM option_investor_flow WHERE trade_date=?", (day,)).fetchone()
            con.close()
            return row
        except Exception:
            return (0, None, None)

    before = _span()
    print("  전: %d행  %s~%s" % before)

    flow = WeeklyOptionFlow(args.db)
    t0 = time.time()
    total = 0
    errs = []
    # 페이지를 바깥 루프로 돌면 같은 COM 객체로 상품·주체를 연속 조회한다.
    for i, pg in enumerate(pages, 1):
        wait_for_quota(verbose=True)          # 라이브 몫을 남기고 진행
        r = flow.fetch_and_store(trade_date=day, pages=(pg,))
        total += r["stored"]
        errs.extend(r["errors"])
        if i % 5 == 0 or i == len(pages):
            print("    %2d/%d 페이지 (t3=%04d) 누적 %d행" % (i, len(pages), pg, total))
        time.sleep(args.sleep)

    after = _span()
    print("  후: %d행  %s~%s" % after)
    print("  소요 %.0f초 · upsert %d건 · 순증 %d행%s"
          % (time.time() - t0, total, after[0] - before[0],
             (" · 오류 %d건" % len(errs)) if errs else ""))
    for e in errs[:3]:
        print("    오류: %s" % e)

    # 결손 점검 — 메웠다고 선언하기 전에 실제로 메워졌는지 본다.
    try:
        con = sqlite3.connect(args.db)
        print("\n  상품별 봉 개수(개인 기준):")
        for p, n, mn, mx in con.execute(
            "SELECT product, COUNT(*), MIN(bar_time), MAX(bar_time) "
            "FROM option_investor_flow WHERE trade_date=? AND investor='individual' "
            "GROUP BY product ORDER BY product", (day,)):
            print("    %-12s %4d봉  %s~%s" % (p, n, mn, mx))
        con.close()
    except Exception as exc:                      # noqa: BLE001
        print("  점검 조회 실패: %s" % exc)

    # 목적 달성 확인 — 장 마감 후 실행이면 마감 구간(종가 단일가 15:35–15:45)이
    # 들어왔어야 한다. 장중 결손 메우기 용도(15:40 이전 실행)면 판정하지 않는다.
    verdict, line = close_check(args.db, day, t_to.strftime("%H:%M"))
    if line:
        print("\n  " + line)
    return EXIT_NO_CLOSE if verdict is False else 0


def close_check(db, day, t_to_hm):
    """장 마감 후 실행이면 마감 구간을 확보했는지 본다.

    Returns: (verdict, line) — verdict 는 True(확보)·False(미확보)·None(판정 대상 아님:
    장중 결손 메우기 용도라 마감 전에 끝난 실행). None 을 True 로 뭉개지 않는다.
    """
    close_ok = _close_ok_for(day)
    if t_to_hm < max(close_ok, CLOSE_OK):
        return None, ""
    last = _latest_option_bar(db, day)
    if last is not None and last >= close_ok:
        return True, "[OptionFlowBackfill] 마감 구간 확보 — 옵션 최신봉 %s (기준 %s)" % (last, close_ok)
    return False, ("[OptionFlowBackfill] ⚠ 마감 구간 미확보 — 옵션 최신봉 %s (기준 %s 이후)"
                   % (last or "없음", close_ok))


if __name__ == "__main__":
    sys.exit(main())
