# -*- coding: utf-8 -*-
"""먼스리 옵션 **행사가 × 투자자 12주체** 보유계약 분단위 수집 (CpSvr9842) — [MW0601 704차]

HTS [9842] 「투자 주체별 종목 비교(추정)」의 API 판이다. 지금까지 `data/db/option_hts/`
에 사람이 내보내던 `YYMMDD_D/_P.xls` 를 자동으로 받는다.

2026-10-22 실측으로 확정된 것 (근거 `docs/미륵이고도화3/옵션_행사가별_투자자포지션_수집가능성_MW0601-20261002.md` §7)
---------------------------------------------------------------------------------------
- 🔴 **실계좌 로그인에서만 된다.** 모의 로그인(`ServerType=1`)은 「계좌등급으로는 CCpSvr9842 …
  제한」으로 클라이언트 `InputCheck` 단계에서 막힌다. 모의계정에서는 쓰지 않는다(사용자 결정).
  ⇒ 차단 응답을 받으면 **그날은 더 부르지 않는다**(로그인은 장중에 바뀌지 않는다).
     행은 쓰지 않고 상태 테이블에만 남긴다 — 미측정을 0 으로 쓰지 않는다(계측 4원칙 ②).
- 기간 모드 vs HTS `_P` **전 칸 일치**(콜·풋 각 1,372/1,372) — API = 화면 같은 원천.
- **위클리 미지원** — 월물 입력은 '1' 최근월 · '2' 차근월뿐('3' 은 서버가 거절).
- 🔴 **명세의 「연속조회 없음」은 틀렸다** — 차근월이 `71102 조회가 계속됩니다` 로 2쪽 온다.
- 🔴 **인덱스 2 기관계 = Σ인덱스 3–10 소계.** 12칸을 그냥 더하면 기관이 이중계상된다.
  기관계를 뺀 합은 행마다 정확히 0 이다(상대 거래) — 매 수집에서 대사한다.
- 금액 `amt` 단위 = 십만원 · 매도 보유 = 음수 · 응답 순서 = 행사가 오름차순.
- 🔴 **행사가를 코드 문자열에서 뽑지 말 것.** 1000 이상 행사가 코드는 상장 순서다
  (`BA01, BA07, BA02 …`). `CpOptionCode`(먼스리 전용, 필드 4)로 해석한다.

저장 — 「바뀐 행만」 + 재구성 규칙
-----------------------------------
당일 모드 보유계약은 그날 0 에서 시작하는 누적이다. 전 행사가(343) × 콜·풋을 매분
쓰면 하루 26만 행이 되는데 대부분 그대로다. 그래서:

1. 프로세스가 그날 **처음 찍는 스냅샷은 전 행 저장**(`full=1`) — 재기동 뒤에도 재구성이 맞는다.
2. 이후에는 **값이 바뀐 코드만** 저장한다.
3. 시각 t 의 값 = 그 코드의 `snap_hm <= t` 최신 행. 행이 없으면 0.
   단 **그 시각 이전에 `ok=1` 상태 행이 하나도 없으면 미측정**이다 — `snapshot_at()` 이 None.

⚠ 이 모듈은 **COM 콜백 체인 밖**(QTimer 경로)에서만 호출할 것 — 절대원칙 §4.
⚠ 피처·게이트에 배선하지 않는다 — 수집·장후 분석 전용(알파 자동통합 금지 취지).
"""
from __future__ import annotations

import datetime
import json
import logging
import os
import sqlite3
import time
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("DATA")

_PROGID = "CpSysDib.CpSvr9842"

# 명세 투자자 인덱스(배열 칸). 인덱스 2 기관계는 3–10 의 소계다.
INVESTORS: Tuple[str, ...] = (
    "개인", "외국인", "기관계", "증권", "보험", "투신", "은행", "종금", "기금", "국가",
    "선물회사", "기타법인",
)
IDX_IND, IDX_FOR, IDX_INS = 0, 1, 2
_INS_PARTS = slice(3, 11)

# (콜풋 키, 시장 입력값)
SIDES: Tuple[Tuple[str, str], ...] = (("C", "2"), ("P", "3"))

# 연속조회 상한 — 실측 최대 2쪽(차근월 567행). 넘으면 절단을 상태에 남긴다.
MAX_PAGES = 6

# 등급 차단 문구의 고정부 — 이 문구면 그날 재시도하지 않는다.
_BLOCK_MARK = "계좌등급"

_SCHEMA = (
    """
    CREATE TABLE IF NOT EXISTS strike_investor_flow (
        trade_date   TEXT NOT NULL,   -- YYYY-MM-DD
        snap_hm      TEXT NOT NULL,   -- HH:MM (호출 분)
        cp           TEXT NOT NULL,   -- 'C' | 'P'
        month        TEXT NOT NULL,   -- '1' 최근월 | '2' 차근월
        code         TEXT NOT NULL,   -- Cybos 종목코드 (표기층)
        strike       REAL,            -- CpOptionCode 해석. 미매핑이면 NULL (상태 unmapped 로 셈)
        ym           TEXT,            -- 월물 'YYMM'
        qty          TEXT NOT NULL,   -- JSON 12칸 보유계약(당일 누적). 칸 = INVESTORS 인덱스
        avg_px       TEXT NOT NULL,   -- JSON 12칸 평균단가
        amt          TEXT NOT NULL,   -- JSON 12칸 보유금액(십만원)
        pnl          TEXT NOT NULL,   -- JSON 12칸 실현손익
        ind_qty      INTEGER,         -- 조회 편의: 개인
        for_qty      INTEGER,         -- 조회 편의: 외국인
        ins_qty      INTEGER,         -- 조회 편의: 기관계(소계)
        collected_at TEXT NOT NULL,
        PRIMARY KEY (trade_date, snap_hm, cp, month, code)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS strike_investor_flow_status (
        trade_date   TEXT NOT NULL,
        snap_hm      TEXT NOT NULL,
        cp           TEXT NOT NULL,
        month        TEXT NOT NULL,
        ok           INTEGER NOT NULL,  -- 1 = 전 행 수신 · 0 = 실패/차단/생략(행 없음 ≠ 0)
        full         INTEGER,           -- 1 = 전 행 저장 스냅샷(재구성 기준점)
        rows_total   INTEGER,
        rows_stored  INTEGER,
        pages        INTEGER,
        unmapped     INTEGER,           -- CpOptionCode 로 행사가를 못 찾은 코드 수
        inv_bad      INTEGER,           -- 주체 대사 위반 행 수(기관계 제외 합 ≠ 0 또는 기관계 ≠ Σ3–10)
        k_min        REAL,
        k_max        REAL,
        limit_remain INTEGER,
        elapsed_ms   REAL,
        msg          TEXT,
        PRIMARY KEY (trade_date, snap_hm, cp, month)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS strike_investor_hold (
        trade_date   TEXT NOT NULL,   -- 기간 모드 종료일 (HTS _P 파일 날짜)
        cp           TEXT NOT NULL,
        month        TEXT NOT NULL,
        code         TEXT NOT NULL,
        strike       REAL,
        ym           TEXT,
        qty          TEXT NOT NULL,
        avg_px       TEXT NOT NULL,
        amt          TEXT NOT NULL,
        pnl          TEXT NOT NULL,
        ind_qty      INTEGER,
        for_qty      INTEGER,
        ins_qty      INTEGER,
        collected_at TEXT NOT NULL,
        PRIMARY KEY (trade_date, cp, month, code)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_sif_code ON strike_investor_flow(trade_date, cp, month, code, snap_hm)",
)


class BlockedError(RuntimeError):
    """계좌등급 차단 — 모의 로그인. 그날 재시도하지 않는다."""


def _arr(v: Any) -> List[Any]:
    try:
        return [x for x in v]
    except TypeError:
        return [v]


def _rnd(xs: List[Any]) -> List[float]:
    # float32 원값(0.6499999761…)을 그대로 쓰면 「바뀐 행」 비교가 흔들리지는 않지만 용량만 늘어난다.
    return [round(float(x), 4) for x in xs]


def inv_check(qty: List[int]) -> bool:
    """주체 대사 — 기관계 = Σ(3–10) 그리고 기관계를 뺀 합 = 0. 2026-10-22 전 행 성립."""
    if len(qty) != len(INVESTORS):
        return False
    return qty[IDX_INS] == sum(qty[_INS_PARTS]) and sum(qty) - qty[IDX_INS] == 0


class StrikeInvestorFlow:
    """CpSvr9842 수집기.

    사용:
        sif = StrikeInvestorFlow(db_path)
        sif.fetch_and_store()            # 매분 1회, QTimer 경로에서 (당일 모드)
        sif.fetch_period("20261021")     # 장후 1회, 기간 모드 = HTS _P
    """

    def __init__(self, db_path: str, months: Tuple[str, ...] = ("1",),
                 quota_reserve: int = 25):
        self.db_path = db_path
        self.months = tuple(months)
        self.quota_reserve = int(quota_reserve)
        self._obj = None                       # COM 캐시
        self._cy = None
        self._master: Dict[str, Tuple[str, str, float]] = {}
        self._master_day: Optional[str] = None
        self._schema_ready = False
        # 「바뀐 행만」 비교 기준 — {(cp, month, code): 값 튜플}. 날짜가 바뀌면 비운다.
        self._last: Dict[Tuple[str, str, str], Tuple] = {}
        self._last_day: Optional[str] = None
        self._full_done: Dict[Tuple[str, str], bool] = {}
        # 차단 — 그날은 더 부르지 않는다. None = 차단 아님.
        self.blocked_day: Optional[str] = None
        self.blocked_msg: str = ""
        # 미측정과 0 구분 (계측 4원칙 ②·④)
        self.last_ok: Optional[bool] = None
        self.last_stored: int = 0
        self.last_elapsed_ms: float = 0.0
        self.last_error: str = ""
        self._fail_streak = 0
        self._last_info_ts: Optional[float] = None
        self._info_every_sec = 1800.0
        self._logged_first_today: Optional[str] = None

    # ── COM ──────────────────────────────────────────────────────────────
    def _get_obj(self):
        if self._obj is None:
            from win32com.client import Dispatch
            self._obj = Dispatch(_PROGID)
        return self._obj

    def _get_cybos(self):
        if self._cy is None:
            from win32com.client import Dispatch
            self._cy = Dispatch("CpUtil.CpCybos")
        return self._cy

    def _limit_remain(self) -> Optional[int]:
        try:
            return int(self._get_cybos().GetLimitRemainCount(1))
        except Exception:
            return None                     # 모르면 None — 0 으로 두지 않는다

    def _load_master(self, today: str, force: bool = False) -> None:
        """CpOptionCode(서버 요청 아님) → {code: (cp, ym, strike)}. 하루 1회 + 미매핑 시 1회 재적재."""
        if self._master and self._master_day == today and not force:
            return
        from win32com.client import Dispatch
        obj = Dispatch("CpUtil.CpOptionCode")
        m: Dict[str, Tuple[str, str, float]] = {}
        for i in range(int(obj.GetCount())):
            try:
                m[str(obj.GetData(0, i)).strip()] = (
                    str(obj.GetData(2, i)).strip().upper(),
                    str(obj.GetData(3, i)).strip(),
                    float(obj.GetData(4, i)),
                )
            except Exception:
                continue
        self._master = m
        self._master_day = today

    def _query(self, market: str, month: str, period: str = "1",
               end: Optional[int] = None) -> Tuple[List[Dict[str, Any]], int, bool]:
        """한 (시장, 월물) 조회 — 연속조회까지. 반환 (행, 쪽수, 절단여부).

        실패는 예외로 올린다(0행과 구분). 등급 차단은 BlockedError.
        """
        obj = self._get_obj()
        obj.SetInputValue(0, ord(market))
        obj.SetInputValue(1, ord(month))
        obj.SetInputValue(2, ord(period))
        if end is not None:
            obj.SetInputValue(3, int(end))
        rows: List[Dict[str, Any]] = []
        pages = 0
        truncated = False
        while True:
            try:
                obj.BlockRequest()
            except Exception as exc:          # 등급 차단은 InputCheck 예외로 온다
                if _BLOCK_MARK in str(exc):
                    raise BlockedError(str(exc))
                raise
            status = int(obj.GetDibStatus())
            if status != 0:
                msg = str(obj.GetDibMsg1() or "").strip()
                if _BLOCK_MARK in msg:
                    raise BlockedError(msg)
                raise RuntimeError("9842 status=%s msg=%s" % (status, msg))
            pages += 1
            for i in range(int(obj.GetHeaderValue(0))):
                rows.append({
                    "code": str(obj.GetDataValue(0, i)).strip(),
                    "qty": [int(x) for x in _arr(obj.GetDataValue(1, i))],
                    "avg": _rnd(_arr(obj.GetDataValue(2, i))),
                    "amt": _rnd(_arr(obj.GetDataValue(3, i))),
                    "pnl": _rnd(_arr(obj.GetDataValue(4, i))),
                })
            if not obj.Continue:
                break
            if pages >= MAX_PAGES:
                truncated = True
                break
        return rows, pages, truncated

    # ── DB ───────────────────────────────────────────────────────────────
    def _conn(self) -> sqlite3.Connection:
        d = os.path.dirname(self.db_path)
        if d:
            os.makedirs(d, exist_ok=True)
        con = sqlite3.connect(self.db_path, timeout=5.0)
        con.execute("PRAGMA journal_mode=WAL")
        if not self._schema_ready:
            for s in _SCHEMA:
                con.execute(s)
            con.commit()
            self._schema_ready = True
        return con

    def _row_values(self, r: Dict[str, Any], cp_expect: str
                    ) -> Tuple[Optional[float], Optional[str], bool]:
        m = self._master.get(r["code"])
        if m is None or not m[0].startswith(cp_expect):
            return None, None, False
        return m[2], m[1], True

    # ── 당일 모드 (매분) ──────────────────────────────────────────────────
    def fetch_and_store(self, now: Optional[datetime.datetime] = None) -> Dict[str, Any]:
        now = now or datetime.datetime.now()
        today = now.date().isoformat()
        snap_hm = now.strftime("%H:%M")
        now_iso = now.isoformat(timespec="seconds")
        if self.blocked_day == today:
            return {"ok": False, "skipped": "blocked", "stored": 0}
        if self._last_day != today:
            self._last, self._full_done, self._last_day = {}, {}, today

        t0 = time.perf_counter()
        status_rows: List[Tuple] = []
        data_rows: List[Tuple] = []
        errors: List[str] = []

        remain = self._limit_remain()
        need = len(SIDES) * len(self.months)
        if remain is not None and remain < self.quota_reserve + need:
            # 라이브와 한도를 나눠 쓴다 — 기다리지 않고 이 분을 건너뛴다(사유를 남긴다).
            for cp, _m in SIDES:
                for month in self.months:
                    status_rows.append((today, snap_hm, cp, month, 0, None, None, None, None,
                                        None, None, None, None, remain, 0.0,
                                        "SKIP_QUOTA remain=%s" % remain))
            self._write(status_rows, [])
            self.last_ok = False
            self.last_error = "SKIP_QUOTA"
            return {"ok": False, "skipped": "quota", "stored": 0}

        try:
            self._load_master(today)
        except Exception as exc:                                # noqa: BLE001
            errors.append("master: %s" % exc)

        for cp, market in SIDES:
            for month in self.months:
                ts = time.perf_counter()
                try:
                    got, pages, truncated = self._query(market, month)
                except BlockedError as exc:
                    self.blocked_day, self.blocked_msg = today, str(exc)
                    status_rows.append((today, snap_hm, cp, month, 0, None, None, None, None,
                                        None, None, None, None, remain, 0.0,
                                        "BLOCKED %s" % str(exc)[:200]))
                    logger.warning(
                        "[StrikeInvestor] 계좌등급 차단 — 실계좌 로그인 전용이다. "
                        "오늘(%s) 더 호출하지 않는다: %s", today, str(exc)[:160])
                    self._write(status_rows, [])
                    self.last_ok = False
                    self.last_error = "BLOCKED"
                    return {"ok": False, "skipped": "blocked", "stored": 0}
                except Exception as exc:                        # noqa: BLE001
                    errors.append("%s/%s: %s" % (cp, month, exc))
                    status_rows.append((today, snap_hm, cp, month, 0, None, None, None, None,
                                        None, None, None, None, remain,
                                        (time.perf_counter() - ts) * 1000.0,
                                        "ERROR %s" % str(exc)[:200]))
                    continue

                # 미매핑이 있으면 마스터를 한 번 다시 받는다(월물 롤오버 직후 대비).
                if got and any(r["code"] not in self._master for r in got):
                    try:
                        self._load_master(today, force=True)
                    except Exception:
                        pass
                full = not self._full_done.get((cp, month), False)
                unmapped = inv_bad = stored = 0
                ks: List[float] = []
                for r in got:
                    strike, ym, ok_map = self._row_values(r, cp)
                    if not ok_map:
                        unmapped += 1
                    else:
                        ks.append(strike)
                    if not inv_check(r["qty"]):
                        inv_bad += 1
                    key = (cp, month, r["code"])
                    val = (tuple(r["qty"]), tuple(r["avg"]), tuple(r["amt"]), tuple(r["pnl"]))
                    if not full and self._last.get(key) == val:
                        continue
                    # 첫 관측이 전부 0 이고 전체 저장 회차가 아니면 쓸 것이 없다(재구성상 0).
                    if (not full and key not in self._last
                            and not any(r["qty"]) and not any(r["pnl"])):
                        self._last[key] = val
                        continue
                    self._last[key] = val
                    q = r["qty"]
                    data_rows.append((
                        today, snap_hm, cp, month, r["code"], strike, ym,
                        json.dumps(q), json.dumps(r["avg"]), json.dumps(r["amt"]),
                        json.dumps(r["pnl"]),
                        q[IDX_IND] if len(q) > IDX_IND else None,
                        q[IDX_FOR] if len(q) > IDX_FOR else None,
                        q[IDX_INS] if len(q) > IDX_INS else None,
                        now_iso,
                    ))
                    stored += 1
                msg = "truncated(pages>=%d)" % MAX_PAGES if truncated else ""
                status_rows.append((
                    today, snap_hm, cp, month, 0 if truncated else 1, 1 if full else 0,
                    len(got), stored, pages, unmapped, inv_bad,
                    min(ks) if ks else None, max(ks) if ks else None, remain,
                    (time.perf_counter() - ts) * 1000.0, msg,
                ))
                if not truncated:
                    self._full_done[(cp, month)] = True
                if truncated:
                    errors.append("%s/%s: 연속조회 절단" % (cp, month))
                if unmapped:
                    errors.append("%s/%s: 행사가 미매핑 %d" % (cp, month, unmapped))
                if inv_bad:
                    errors.append("%s/%s: 주체 대사 위반 %d행" % (cp, month, inv_bad))

        werr = self._write(status_rows, data_rows)
        if werr:
            errors.append(werr)
            # DB 에 못 썼으면 「바뀐 행만」 기준이 DB 와 어긋난다 — 다음 회차를 전체 저장으로.
            self._full_done = {}
        elapsed = (time.perf_counter() - t0) * 1000.0
        ok = not errors
        self.last_ok, self.last_stored, self.last_elapsed_ms = ok, len(data_rows), elapsed
        self.last_error = "; ".join(errors[:3])
        self._fail_streak = 0 if ok else self._fail_streak + 1
        if errors and (self._fail_streak == 1 or self._fail_streak % 10 == 0):
            logger.warning("[StrikeInvestor] 부분/전체 실패 streak=%d stored=%d elapsed=%.0fms — %s%s",
                           self._fail_streak, len(data_rows), elapsed, self.last_error,
                           (" 외 %d건" % (len(errors) - 3)) if len(errors) > 3 else "")
        elif ok:
            now_mono = time.time()
            first_today = self._logged_first_today != today
            if first_today or self._last_info_ts is None or \
                    (now_mono - self._last_info_ts) >= self._info_every_sec:
                self._logged_first_today, self._last_info_ts = today, now_mono
                done = [s for s in status_rows if s[4] == 1]
                logger.info(
                    "[StrikeInvestor] stored=%d rows elapsed=%.0fms 요청=%d(콜풋×월물 %s) "
                    "수신=%d행 쪽=%d 주체대사 위반=0 미매핑=0%s",
                    len(data_rows), elapsed, len(done), ",".join(self.months),
                    sum(s[6] or 0 for s in done), sum(s[8] or 0 for s in done),
                    " (오늘 첫 수집 — 전체 저장)" if first_today else "")
        return {"ok": ok, "stored": len(data_rows), "elapsed_ms": elapsed,
                "errors": errors, "fail_streak": self._fail_streak}

    def _write(self, status_rows: List[Tuple], data_rows: List[Tuple]) -> str:
        if not status_rows and not data_rows:
            return ""
        try:
            con = self._conn()
            with con:
                if data_rows:
                    con.executemany(
                        "INSERT OR REPLACE INTO strike_investor_flow "
                        "(trade_date,snap_hm,cp,month,code,strike,ym,qty,avg_px,amt,pnl,"
                        " ind_qty,for_qty,ins_qty,collected_at) "
                        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", data_rows)
                if status_rows:
                    con.executemany(
                        "INSERT OR REPLACE INTO strike_investor_flow_status "
                        "(trade_date,snap_hm,cp,month,ok,full,rows_total,rows_stored,pages,"
                        " unmapped,inv_bad,k_min,k_max,limit_remain,elapsed_ms,msg) "
                        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", status_rows)
            con.close()
            return ""
        except Exception as exc:                                # noqa: BLE001
            return "db: %s" % exc

    # ── 기간 모드 (장후 · HTS _P 대응) ──────────────────────────────────────
    def fetch_period(self, end_yyyymmdd: str, months: Optional[Tuple[str, ...]] = None
                     ) -> Dict[str, Any]:
        """종료일 기준 기간 보유계약을 `strike_investor_hold` 에 전 행 저장한다.

        반환: {cp/month: {"ok", "rows", "pages", "unmapped", "inv_bad", "msg"}}.
        차단이면 BlockedError 를 그대로 올린다(호출 측 스크립트가 판단).
        """
        trade_date = "%s-%s-%s" % (end_yyyymmdd[:4], end_yyyymmdd[4:6], end_yyyymmdd[6:8])
        now_iso = datetime.datetime.now().isoformat(timespec="seconds")
        self._load_master(datetime.date.today().isoformat())
        out: Dict[str, Any] = {}
        rows_db: List[Tuple] = []
        for cp, market in SIDES:
            for month in (months or self.months):
                key = "%s/%s" % (cp, month)
                try:
                    got, pages, truncated = self._query(market, month, period="2",
                                                        end=int(end_yyyymmdd))
                except BlockedError:
                    raise
                except Exception as exc:                        # noqa: BLE001
                    out[key] = {"ok": False, "rows": None, "msg": str(exc)}
                    continue
                unmapped = inv_bad = 0
                for r in got:
                    strike, ym, ok_map = self._row_values(r, cp)
                    unmapped += 0 if ok_map else 1
                    inv_bad += 0 if inv_check(r["qty"]) else 1
                    q = r["qty"]
                    rows_db.append((trade_date, cp, month, r["code"], strike, ym,
                                    json.dumps(q), json.dumps(r["avg"]), json.dumps(r["amt"]),
                                    json.dumps(r["pnl"]), q[IDX_IND], q[IDX_FOR], q[IDX_INS],
                                    now_iso))
                out[key] = {"ok": not truncated, "rows": len(got), "pages": pages,
                            "unmapped": unmapped, "inv_bad": inv_bad,
                            "msg": "truncated" if truncated else ""}
        if rows_db:
            con = self._conn()
            with con:
                con.executemany(
                    "INSERT OR REPLACE INTO strike_investor_hold "
                    "(trade_date,cp,month,code,strike,ym,qty,avg_px,amt,pnl,"
                    " ind_qty,for_qty,ins_qty,collected_at) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rows_db)
            con.close()
        return out

    # ── 재구성 (장후 분석·대시보드용) ──────────────────────────────────────
    def snapshot_at(self, trade_date: str, hm: str, cp: str = "C", month: str = "1"
                    ) -> Optional[Dict[float, Dict[str, Any]]]:
        """시각 hm 의 행사가별 당일 보유계약. 그 시각 이전 `ok=1` 수집이 없으면 None(미측정).

        반환 {strike: {"code", "qty"[12], "amt"[12], "snap_hm"}} — 행 없는 행사가는 0(생략).
        """
        con = self._conn()
        try:
            n_ok = con.execute(
                "SELECT COUNT(*) FROM strike_investor_flow_status "
                "WHERE trade_date=? AND cp=? AND month=? AND ok=1 AND full=1 AND snap_hm<=?",
                (trade_date, cp, month, hm)).fetchone()[0]
            if not n_ok:
                return None
            rows = con.execute(
                "SELECT f.code, f.strike, f.qty, f.amt, f.snap_hm FROM strike_investor_flow f "
                "JOIN (SELECT code, MAX(snap_hm) AS mh FROM strike_investor_flow "
                "      WHERE trade_date=? AND cp=? AND month=? AND snap_hm<=? GROUP BY code) g "
                "  ON f.code=g.code AND f.snap_hm=g.mh "
                "WHERE f.trade_date=? AND f.cp=? AND f.month=?",
                (trade_date, cp, month, hm, trade_date, cp, month)).fetchall()
        finally:
            con.close()
        out: Dict[float, Dict[str, Any]] = {}
        for code, strike, qty, amt, sh in rows:
            if strike is None:
                continue
            out[float(strike)] = {"code": code, "qty": json.loads(qty),
                                  "amt": json.loads(amt), "snap_hm": sh}
        return out
