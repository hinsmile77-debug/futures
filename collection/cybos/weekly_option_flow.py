# -*- coding: utf-8 -*-
"""위클리/먼스리 옵션 · KOSPI 현물의 분단위 투자자별 순매수 수집 (CpSvrNew7222).

[MW0601 2026-09-21 신설]

왜 필요한가
-----------
미륵이가 쓰던 `CpSvrNew7221`(ri=3 옵션콜 / ri=4 옵션풋)은 **정규 월물**이고
단위가 **금액**이며, 피처로 나가는 것은 **외국인**뿐이다(`foreign_call_net` /
`foreign_put_net`). 그런데 2026-09-21 실측상 개인의 옵션 거래는 **위클리에
집중**돼 있다 — 계약수 기준 (월)위클리 5,575 vs 먼스리 273, **20.4배**.
즉 종전 경로는 개인 흐름의 주무대를 구조적으로 못 본다.

시장코드 — 2026-09-21 라이브 실측 확정
--------------------------------------
키움 화면 캡처(같은 날 오전)를 정답지로 앵커 대조해 확정했다. 값이 어긋난 행은
하나도 없었다(일부 4/5 는 그 시각 행이 Cybos 응답에 아예 없어서지 불일치가 아니다).

    '&' ord=38  (월)위클리 풋   5/5     '?' ord=63  (월)위클리 콜   5/5
    'R' ord=82  (목)위클리 풋   5/5     'Q' ord=81  (목)위클리 콜   4/5
    'F' ord=70  먼스리 풋       5/5     'E' ord=69  먼스리 콜       5/5
    'B' ord=66  KOSPI 현물     4/5

🔴 **(월)위클리는 공식 명세 A~Z 밖의 특수문자다.** 명세(cybosplus.github.io,
   2014-07-18 스냅샷)에는 위클리가 아예 없고, A~Z · a~z · 0~9 를 전부 훑어도
   나오지 않았다. ord 33~255 확장 스캔에서야 나왔다.
   ⇒ 새 상품군을 찾을 때 **A~Z 로 범위를 한정하지 말 것.**

한 번의 조회가 주는 것
----------------------
`GetHeaderValue(0)` = 행 수이고 실측 **18행**이다. 옵션은 1분 간격이라 18분치,
현물은 1~2분 불규칙이라 26분쯤 된다. `SetInputValue(3, HHMM)` 을 주면 **그 시각
직전** 18행을 준다(페이징).

**매 호출마다 받은 18행을 전부 upsert 한다.** 그래서 프로세스가 재시작해도
최근 18분이 자동으로 메워진다 — 552-10 의 "재시작이 상태를 지운다" 계열 결함을
설계로 막는다.

비용
----
첫 Dispatch 만 ~1,100ms 이고 이후 요청은 **5~7ms** 다(2026-09-21 실측). 그래서
COM 객체를 인스턴스에 캐시한다. 7상품 × 3주체 = 21요청이 약 150ms 다.
⚠ 7222 는 **type1(시세) 한도**를 쓴다 — 15초당 60건. 21요청은 그 안이지만
  라이브(7221·8111)와 공유하므로 여유를 남긴다.

⚠ 이 모듈은 **COM 콜백 체인 밖**(QTimer 경로)에서만 호출할 것.
  절대원칙 §4 — 콜백 안에서 dynamicCall/emit 금지.
"""
from __future__ import annotations

import datetime
import logging
import os
import sqlite3
import time
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("DATA")

# ── 수집 대상 ────────────────────────────────────────────────────────────
# (시장코드, 상품키, 라벨). 상품키가 DB·피처의 정체성이다 — 코드는 표기층일 뿐이므로
# 인용·조인은 항상 상품키로 한다(캠페인 채널 번호 교훈과 같은 원칙).
PRODUCTS: Tuple[Tuple[str, str, str], ...] = (
    ("&", "wk_mon_put",  "(월)위클리 풋"),
    ("?", "wk_mon_call", "(월)위클리 콜"),
    ("R", "wk_thu_put",  "(목)위클리 풋"),
    ("Q", "wk_thu_call", "(목)위클리 콜"),
    ("F", "mon_put",     "먼스리 풋"),
    ("E", "mon_call",    "먼스리 콜"),
    ("B", "kospi_spot",  "KOSPI 현물"),
)
# 투자자 구분 — 명세 type 1. 0=전체 1=개인 2=외국인 3=기관계 4=금융투자 …
INVESTORS: Tuple[Tuple[int, str], ...] = (
    (1, "individual"),
    (2, "foreign"),
    (3, "institution"),
)

_PROGID = "CpSysDib.CpSvrNew7222"
_SCHEMA = """
CREATE TABLE IF NOT EXISTS option_investor_flow (
    trade_date   TEXT    NOT NULL,   -- YYYY-MM-DD
    bar_time     TEXT    NOT NULL,   -- HH:MM (원천이 준 시각)
    product      TEXT    NOT NULL,   -- PRODUCTS 의 상품키
    market_code  TEXT    NOT NULL,   -- 원천 시장코드 (표기층)
    investor     TEXT    NOT NULL,   -- individual|foreign|institution
    sell_qty     INTEGER,
    buy_qty      INTEGER,
    net_qty      INTEGER,            -- 순매수 수량(계약). 현물은 주식 수
    net_amt      INTEGER,            -- 순매수 금액(백만원). 화면 억원의 100배
    collected_at TEXT    NOT NULL,
    PRIMARY KEY (trade_date, bar_time, product, investor)
)
"""
_INDEX = (
    "CREATE INDEX IF NOT EXISTS idx_oif_date_product "
    "ON option_investor_flow(trade_date, product)",
)


def _safe_int(v: Any) -> int:
    try:
        return int(str(v).strip().replace(",", ""))
    except Exception:
        return 0


def _hhmm_to_text(v: int) -> str:
    """원천 시각(HHMM 또는 HHMMSS)을 'HH:MM' 으로."""
    if v > 10000:
        v //= 100
    return "%02d:%02d" % (v // 100, v % 100)


class WeeklyOptionFlow:
    """CpSvrNew7222 수집기.

    사용:
        flow = WeeklyOptionFlow(db_path)
        flow.fetch_and_store()      # 매분 1회, QTimer 경로에서
    """

    def __init__(self, db_path: str, products=PRODUCTS, investors=INVESTORS):
        self.db_path = db_path
        self.products = tuple(products)
        self.investors = tuple(investors)
        self._obj = None                    # COM 객체 캐시 (첫 Dispatch 1.1초 회피)
        self._schema_ready = False
        # 미측정과 0 을 구분하기 위한 상태 (계측 4원칙 ②·④)
        self.last_ok: Optional[bool] = None
        self.last_rows: int = 0
        self.last_elapsed_ms: float = 0.0
        self.last_error: str = ""
        self._fail_streak = 0

    # ── COM ──────────────────────────────────────────────────────────────
    def _get_obj(self):
        if self._obj is None:
            from win32com.client import Dispatch
            self._obj = Dispatch(_PROGID)
        return self._obj

    def _query(self, market_code: str, investor: int,
               t3: Optional[int] = None) -> List[Dict[str, Any]]:
        """한 (상품, 투자자) 조합을 조회해 행 목록을 반환한다.

        반환 실패와 '데이터 0행'을 구분한다 — 실패는 예외로 올린다.
        """
        obj = self._get_obj()
        obj.SetInputValue(0, ord(market_code))
        obj.SetInputValue(1, investor)
        obj.SetInputValue(2, ord("1"))      # 누적
        obj.SetInputValue(4, ord("1"))      # 계약(옵션만 적용. 금액은 어차피 별도 필드)
        if t3 is not None:
            obj.SetInputValue(3, t3)
        obj.BlockRequest()
        status = _safe_int(obj.GetDibStatus())
        if status != 0:
            raise RuntimeError("7222 status=%s msg=%s"
                               % (status, str(obj.GetDibMsg1() or "").strip()))
        cnt = _safe_int(obj.GetHeaderValue(0))
        out: List[Dict[str, Any]] = []
        for i in range(cnt):
            out.append({
                "t":        _safe_int(obj.GetDataValue(0, i)),
                "sell_qty": _safe_int(obj.GetDataValue(1, i)),
                "buy_qty":  _safe_int(obj.GetDataValue(3, i)),
                "net_qty":  _safe_int(obj.GetDataValue(5, i)),
                "net_amt":  _safe_int(obj.GetDataValue(6, i)),
            })
        return out

    # ── DB ───────────────────────────────────────────────────────────────
    def _conn(self) -> sqlite3.Connection:
        d = os.path.dirname(self.db_path)
        if d:
            os.makedirs(d, exist_ok=True)
        con = sqlite3.connect(self.db_path, timeout=5.0)
        con.execute("PRAGMA journal_mode=WAL")
        if not self._schema_ready:
            con.execute(_SCHEMA)
            for ix in _INDEX:
                con.execute(ix)
            con.commit()
            self._schema_ready = True
        return con

    # ── 수집 ─────────────────────────────────────────────────────────────
    def fetch_and_store(self, trade_date: Optional[str] = None,
                        pages: Tuple[Optional[int], ...] = (None,)) -> Dict[str, Any]:
        """전 상품 × 전 투자자를 조회해 upsert 한다.

        pages: type 3 시각 목록. 기본 (None,) 이면 최근 18행.
               장 마감 후 하루 전체를 메우려면 여러 시각을 넘긴다.
        반환: 요약 dict (로그·대시보드용).
        """
        t0 = time.perf_counter()
        today = trade_date or datetime.date.today().isoformat()
        now_iso = datetime.datetime.now().isoformat(timespec="seconds")
        rows: List[Tuple] = []
        errors: List[str] = []

        for market_code, product, label in self.products:
            for inv_code, inv_name in self.investors:
                for pg in pages:
                    try:
                        got = self._query(market_code, inv_code, pg)
                    except Exception as exc:                    # noqa: BLE001
                        errors.append("%s/%s: %s" % (product, inv_name, exc))
                        continue
                    for r in got:
                        rows.append((
                            today, _hhmm_to_text(r["t"]), product, market_code,
                            inv_name, r["sell_qty"], r["buy_qty"],
                            r["net_qty"], r["net_amt"], now_iso,
                        ))

        stored = 0
        if rows:
            try:
                con = self._conn()
                with con:
                    con.executemany(
                        "INSERT INTO option_investor_flow "
                        "(trade_date,bar_time,product,market_code,investor,"
                        " sell_qty,buy_qty,net_qty,net_amt,collected_at) "
                        "VALUES (?,?,?,?,?,?,?,?,?,?) "
                        "ON CONFLICT(trade_date,bar_time,product,investor) DO UPDATE SET "
                        " sell_qty=excluded.sell_qty, buy_qty=excluded.buy_qty,"
                        " net_qty=excluded.net_qty, net_amt=excluded.net_amt,"
                        " collected_at=excluded.collected_at",
                        rows,
                    )
                stored = len(rows)
                con.close()
            except Exception as exc:                            # noqa: BLE001
                errors.append("db: %s" % exc)

        elapsed = (time.perf_counter() - t0) * 1000.0
        ok = bool(stored) and not errors
        self.last_ok = ok
        self.last_rows = stored
        self.last_elapsed_ms = elapsed
        self.last_error = "; ".join(errors[:3])
        self._fail_streak = 0 if ok else self._fail_streak + 1

        # 실패를 조용히 넘기지 않는다 (계측 4원칙 ③·④).
        # 다만 매분 반복이므로 연속 실패 1회째와 이후 10회마다만 WARNING.
        if errors and (self._fail_streak == 1 or self._fail_streak % 10 == 0):
            logger.warning(
                "[OptionFlow] 부분/전체 실패 streak=%d stored=%d elapsed=%.0fms — %s%s",
                self._fail_streak, stored, elapsed, self.last_error,
                (" 외 %d건" % (len(errors) - 3)) if len(errors) > 3 else "",
            )
        elif ok:
            logger.debug("[OptionFlow] stored=%d elapsed=%.0fms", stored, elapsed)
        return {
            "ok": ok, "stored": stored, "elapsed_ms": elapsed,
            "errors": errors, "fail_streak": self._fail_streak,
        }

    # ── 조회 헬퍼 (피처/대시보드용) ────────────────────────────────────────
    def latest(self, product: str, investor: str = "individual",
               trade_date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """그 상품·주체의 가장 최근 행. 없으면 None (0 을 돌려주지 않는다)."""
        today = trade_date or datetime.date.today().isoformat()
        try:
            con = self._conn()
            cur = con.execute(
                "SELECT bar_time,sell_qty,buy_qty,net_qty,net_amt "
                "FROM option_investor_flow "
                "WHERE trade_date=? AND product=? AND investor=? "
                "ORDER BY bar_time DESC LIMIT 1",
                (today, product, investor),
            )
            row = cur.fetchone()
            con.close()
        except Exception:
            return None
        if not row:
            return None
        return {"bar_time": row[0], "sell_qty": row[1], "buy_qty": row[2],
                "net_qty": row[3], "net_amt": row[4]}
