# -*- coding: utf-8 -*-
"""[MW0601 565차 / 풀타임 수집 Phase 3] 장후 차트 TR(`CpSysDib.FutOptChart`)로 `session_bars` 대사·보충.

왜 이 경로인가 (2026-09-14 실측)
--------------------------------
· 실시간 봉은 공식 차트와 **정확히 일치**한다(09-11 08:46·15:33·15:34 봉 OHLCV 전부 동일).
· 차트는 실시간이 못 잡는 두 봉을 준다 — **개장 체결**(09-11 시가 1076.06·653계약 vs 실시간
  1072.72·330계약)과 **15:45 마감 체결**(라벨 `1545`, 단독 봉). 즉 프로세스 수명을 15:46까지
  늘리는 Phase 2 없이도 마감 체결이 회수된다 → Phase 2 폐기, Phase 3 채택.
· 재기동·동결로 빠진 봉(09-10 14:40)도 다음날 메워진다.

원천 규약 (실측으로 확정)
-------------------------
· 봉 라벨은 **종료 시각**이다: `846` = 08:45:00~08:46:00 = 우리 ts `08:45`. 따라서 ts = 라벨 − 1분.
· `1545` 행 하나가 마감 단일가 체결이다(15:36~15:44 행은 없다) → ts `15:45`, CLOSE_FILL.
· 만기가 지난 코드는 조회가 거부된다(`종목코드가 잘못되었습니다`) — **8월 소급 불가**.
  만기일 당일의 만기 월물도 다음날엔 없다. 그 날은 건너뛰고 로그로 남긴다.
· 기간 조회('1')는 한 페이지 2,499행이고 `Continue` 로 이어진다(10거래일 = 2페이지 실측).
· 가격은 float32 로 와서(1076.06005859375) 2자리로 반올림한다(틱 0.02).

절대원칙 §4: BlockRequest 는 COM 콜백 밖(스케줄러 틱)에서만 부른다. `_run_block_request`
와 같은 STA 워커 + 메인 펌프 구조를 쓰되 `Continue` 페이지를 같은 객체로 이어 받는다.
"""
from __future__ import annotations

import datetime
import logging
import threading
import time
from typing import Dict, List, Optional, Tuple

from utils.time_utils import (
    classify_session, get_monthly_expiry_date, is_expiry_day, is_trading_day,
    SESSION_CLOSE_FILL,
)

logger = logging.getLogger(__name__)
sys_log = logging.getLogger("SYSTEM")

try:  # pragma: no cover - 32bit 런타임 전용
    import pythoncom
    from win32com.client import Dispatch
except ImportError:  # pragma: no cover
    pythoncom = None
    Dispatch = None

FUTOPT_CHART_PROGID = "CpSysDib.FutOptChart"
CHART_FIELDS = [0, 1, 2, 3, 4, 5, 8, 27]   # 날짜·시간·O·H·L·C·거래량·미결제
SOURCE_CHART = "chart_backfill"
CLOSE_FILL_LABEL = 1545


def mini_code_for_date(d: datetime.date) -> str:
    """그 날짜에 **근월물이었던** 미니선물 코드. 만기일 당일까지는 그 달 월물.

    규칙 `A05 + 연도 끝자리 + 월(hex)` — `api_connector.get_nearest_mini_futures_code` 와 동일.
    """
    y, m = d.year, d.month
    if d > get_monthly_expiry_date(y, m):
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return "A05{0}{1}".format(str(y)[-1], format(m, "X"))


def prev_trading_day(d: datetime.date) -> datetime.date:
    p = d - datetime.timedelta(days=1)
    while not is_trading_day(datetime.datetime.combine(p, datetime.time(10, 0))):
        p -= datetime.timedelta(days=1)
    return p


def request_futopt_minute_bars(code: str, d_from: datetime.date, d_to: datetime.date,
                               timeout_sec: float = 60.0, max_pages: int = 20) -> List[Dict]:
    """기간 분봉 전량. 행: {date, time, open, high, low, close, volume, oi}. 실패는 예외."""
    if pythoncom is None or Dispatch is None:
        raise RuntimeError("pywin32(32-bit) 없음 — py37_32 에서만 호출 가능")
    out = {"rows": [], "pages": 0, "exc": None, "ret": None, "status": None, "msg": ""}
    done = threading.Event()

    def _worker():
        try:
            pythoncom.CoInitialize()
        except Exception:
            pass
        try:
            obj = Dispatch(FUTOPT_CHART_PROGID)
            for k, v in [(0, code), (1, ord("1")), (2, int(d_to.strftime("%Y%m%d"))),
                         (3, int(d_from.strftime("%Y%m%d"))), (5, CHART_FIELDS),
                         (6, ord("m")), (7, 1), (8, ord("0"))]:
                obj.SetInputValue(k, v)
            for _ in range(max_pages):
                out["ret"] = obj.BlockRequest()
                out["status"] = int(obj.GetDibStatus() or 0)
                out["msg"] = str(obj.GetDibMsg1() or "")
                n = int(obj.GetHeaderValue(3) or 0)
                for i in range(n):
                    out["rows"].append({
                        "date": int(obj.GetDataValue(0, i)),
                        "time": int(obj.GetDataValue(1, i)),
                        "open": round(float(obj.GetDataValue(2, i)), 2),
                        "high": round(float(obj.GetDataValue(3, i)), 2),
                        "low": round(float(obj.GetDataValue(4, i)), 2),
                        "close": round(float(obj.GetDataValue(5, i)), 2),
                        "volume": int(obj.GetDataValue(6, i)),
                        "oi": int(obj.GetDataValue(7, i)),
                    })
                out["pages"] += 1
                if not obj.Continue:
                    break
        except Exception as exc:
            out["exc"] = exc
        finally:
            try:
                pythoncom.CoUninitialize()
            except Exception:
                pass
            done.set()

    threading.Thread(target=_worker, daemon=True, name="FutOptChart").start()
    deadline = time.time() + timeout_sec
    while not done.wait(timeout=0.01):
        if time.time() >= deadline:
            raise TimeoutError("FutOptChart timeout {0}s code={1}".format(timeout_sec, code))
        try:
            pythoncom.PumpWaitingMessages()
        except Exception:
            pass
    if out["exc"] is not None:
        raise out["exc"]
    if out["status"] not in (0, None):
        raise RuntimeError("FutOptChart status={0} msg={1}".format(out["status"], out["msg"]))
    return out["rows"]


def chart_rows_to_bars(rows: List[Dict]) -> List[Tuple[str, str, Dict]]:
    """차트 행 → (ts, session, bar). 라벨은 종료 시각이므로 ts = 라벨 − 1분, `1545` 는 CLOSE_FILL."""
    out = []
    for r in rows:
        d = datetime.datetime.strptime(str(r["date"]), "%Y%m%d").date()
        hh, mm = divmod(int(r["time"]), 100)
        if int(r["time"]) == CLOSE_FILL_LABEL:
            ts = datetime.datetime.combine(d, datetime.time(15, 45))
            session = SESSION_CLOSE_FILL
        else:
            ts = datetime.datetime.combine(d, datetime.time(hh, mm)) - datetime.timedelta(minutes=1)
            session = classify_session(ts, None)
        bar = {
            "ts": ts, "open": r["open"], "high": r["high"], "low": r["low"], "close": r["close"],
            "volume": r["volume"], "oi": r["oi"],
        }
        out.append((ts.strftime("%Y-%m-%d %H:%M:%S"), session, bar))
    out.sort(key=lambda t: t[0])
    return out


def reconcile_and_insert(bars: List[Tuple[str, str, Dict]], source: str = SOURCE_CHART,
                         dry_run: bool = False, log_prefix: str = "[SessionBackfill]") -> Dict:
    """기존 `session_bars` 와 ts 로 대조 — 있으면 OHLCV 불일치만 세고, 없으면 삽입.

    기존 행은 **덮지 않는다**(실시간 봉이 bid/ask·틱수를 더 갖는다).
    """
    from utils.db_utils import (
        fetch_session_bars_map, insert_session_bar_if_missing, update_session_bar_ohlv_from_chart,
    )
    if not bars:
        return {"chart": 0, "existing": 0, "inserted": 0, "mismatch": 0, "mismatch_ts": [], "open_fixed": 0}
    days = sorted({ts[:10] for ts, _, _ in bars})
    existing = fetch_session_bars_map(days[0], days[-1])
    st = {"chart": len(bars), "existing": 0, "inserted": 0, "mismatch": 0, "mismatch_ts": [], "open_fixed": 0}
    for ts, session, bar in bars:
        ex = existing.get(ts)
        if ex is not None:
            st["existing"] += 1
            bad = [k for k in ("open", "high", "low", "close", "volume")
                   if abs(float(ex[k]) - float(bar[k])) > 1e-6]
            if bad:
                # 08:45 봉: 실시간 구독(08:45:07~)이 개장 단일가 체결을 놓쳐 O·H·V 가 다르다
                # (09-11 실측 시가 1076.06·653계약 vs 1072.72·330계약). 이 봉만 차트 값으로
                # O/H/L/V 를 보정하고 source 를 바꿔 남긴다 — close·bid/ask·틱수는 실시간 유지.
                if (ts[11:16] == "08:45" and source == SOURCE_CHART and ex["source"] == "rt"
                        and not dry_run):
                    update_session_bar_ohlv_from_chart(ts, bar, "rt_chart_open")
                    st["open_fixed"] += 1
                    sys_log.info("%s 08:45 개장 체결 보정 ts=%s rt O=%.2f/V=%s → chart O=%.2f/V=%s",
                                 log_prefix, ts, float(ex["open"]), ex["volume"], bar["open"], bar["volume"])
                    continue
                st["mismatch"] += 1
                if len(st["mismatch_ts"]) < 20:
                    st["mismatch_ts"].append((ts, bad, ex["source"]))
            continue
        if not dry_run:
            if insert_session_bar_if_missing(bar, session, source):
                st["inserted"] += 1
        else:
            st["inserted"] += 1
    sys_log.info(
        "%s %s~%s chart=%d existing=%d inserted=%d open_fixed=%d mismatch=%d%s",
        log_prefix, days[0], days[-1], st["chart"], st["existing"], st["inserted"], st["open_fixed"],
        st["mismatch"], " (dry-run)" if dry_run else "",
    )
    for ts, bad, src in st["mismatch_ts"][:5]:
        sys_log.warning("%s OHLCV 불일치 ts=%s cols=%s existing_source=%s", log_prefix, ts, bad, src)
    return st


def backfill_day(day: datetime.date, code: Optional[str] = None, dry_run: bool = False) -> Optional[Dict]:
    """하루치 보충. 만기일의 만기 월물은 다음날 조회가 거부되므로 건너뛴다(None)."""
    if not is_trading_day(datetime.datetime.combine(day, datetime.time(10, 0))):
        return None
    code = code or mini_code_for_date(day)
    if is_expiry_day(datetime.datetime.combine(day, datetime.time(10, 0))) and day < datetime.date.today():
        sys_log.info("[SessionBackfill] %s 만기일 — 만기 월물 %s 은 사후 조회 불가, 건너뜀", day, code)
        return None
    try:
        rows = request_futopt_minute_bars(code, day, day)
    except Exception as exc:
        sys_log.warning("[SessionBackfill] %s code=%s 차트 조회 실패: %s", day, code, exc)
        return None
    rows = [r for r in rows if str(r["date"]) == day.strftime("%Y%m%d")]
    return reconcile_and_insert(chart_rows_to_bars(rows), dry_run=dry_run)
