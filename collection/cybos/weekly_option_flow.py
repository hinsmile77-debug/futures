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
        # 성공 로그 — 매분 INFO 는 하루 390줄이라 과하고, DEBUG 만 쓰면
        # DATA 로그에 DEBUG 가 기록되지 않아(실측 0건) **돌고 있는지 자체를 못 본다.**
        # 그래서 하루 첫 성공 1회 + 이후 주기적으로만 INFO 를 남긴다.
        # 계측 4원칙 ②의 취지 — "미측정"과 "정상"을 로그에서 구분할 수 있어야 한다.
        self._last_info_ts: Optional[float] = None
        self._info_every_sec: float = 1800.0     # 30분
        self._logged_first_today: Optional[str] = None   # YYYY-MM-DD

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
            now_mono = time.time()
            first_today = (self._logged_first_today != today)
            due = (self._last_info_ts is None
                   or (now_mono - self._last_info_ts) >= self._info_every_sec)
            if first_today or due:
                self._logged_first_today = today
                self._last_info_ts = now_mono
                # 무엇을 몇 개 담았는지까지 남긴다 — "일치"만 찍으면 범위를
                # 오해한다(계측 4원칙 ⑤).
                logger.info(
                    "[OptionFlow] stored=%d rows elapsed=%.0fms "
                    "상품=%d 주체=%d 최신봉=%s%s",
                    stored, elapsed, len(self.products), len(self.investors),
                    max((r[1] for r in rows), default="-"),
                    " (오늘 첫 수집)" if first_today else "",
                )
            else:
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

    # ── 대시보드 — 개인 옵션 시초 대비 증감 (612차 후속3) ──────────────────
    #
    # 「투자자 포지션 매트릭스」가 이 값을 시계열로 그린다.
    #
    # 🔴 **원천 `net_qty` 는 일중 누적 순매수다**(`SetInputValue(2, ord('1'))` = 누적).
    #    그래서 첫 바가 0 이 아니다 — 2026-09-21 실측 08:56 에 (월)위클리 콜이
    #    이미 +2,091 이었다(프리장 단일가 결과가 실려 있다).
    #    ⇒ 「시초 대비 증감」은 **그날 첫 관측을 0 으로 놓은 차분**이다.
    #      사용자 결정(2026-09-21): 기준 = 당일 첫 바.
    #
    # ⚠ 결측을 0 으로 메우지 않는다 — 실측상 `wk_thu_call` 은 오늘 319바로
    #   다른 상품(352바)보다 33바 적다. 없는 분은 점을 찍지 않는다(계측 4원칙 ②).
    DASHBOARD_PRODUCTS: Tuple[Tuple[str, str], ...] = (
        ("wk_mon_call", "(월)위클리 콜"),
        ("wk_mon_put",  "(월)위클리 풋"),
        ("wk_thu_call", "(목)위클리 콜"),
        ("wk_thu_put",  "(목)위클리 풋"),
        ("mon_call",    "먼스리 콜"),
        ("mon_put",     "먼스리 풋"),
    )
    # 세션 창 — 지시받은 표시 범위. 기준 바는 이 창 안의 첫 관측이다.
    SESSION_START = "08:45"
    SESSION_END   = "15:35"

    def get_individual_session_delta(
        self, trade_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """개인 옵션 6종의 **시초 대비 누적 증감(계약)** 시계열.

        한 번의 인덱스 조회로 6상품 전량을 읽는다(하루 약 2,100행 · 실측 수 ms).
        호출은 수급 QTimer 경로에서 분당 1회 — **GUI 스레드에서 DB 를 열지 않는다.**

        Returns:
            {
              "trade_date": "YYYY-MM-DD",
              "last_time":  "HH:MM" | None,
              "products": {
                 key: {"label", "baseline", "baseline_time", "value",
                       "delta", "last_time", "n", "series": [(HH:MM, delta), ...],
                       # [626차] 금액 계열 — 원천에 금액이 있을 때만(없으면 키 자체가 없다)
                       "unit_amt", "baseline_amt", "baseline_time_amt", "value_amt",
                       "delta_amt", "last_time_amt", "series_amt"}
              },
            }
            수집 전이면 `products` 안이 비어 있다 — **빈 dict 와 0 을 구분한다.**
        """
        today = trade_date or datetime.date.today().isoformat()
        keys = [k for k, _ in self.DASHBOARD_PRODUCTS]
        labels = dict(self.DASHBOARD_PRODUCTS)
        out: Dict[str, Any] = {
            "trade_date": today, "last_time": None, "products": {},
        }
        try:
            con = self._conn()
            cur = con.execute(
                "SELECT product,bar_time,net_qty,net_amt FROM option_investor_flow "
                "WHERE trade_date=? AND investor='individual' "
                "  AND bar_time>=? AND bar_time<=? "
                "  AND product IN (%s) "
                "ORDER BY product, bar_time" % ",".join("?" * len(keys)),
                tuple([today, self.SESSION_START, self.SESSION_END] + keys),
            )
            raw = cur.fetchall()
            con.close()
        except Exception as exc:                                # noqa: BLE001
            logger.warning("[OptionFlow] 대시보드 조회 실패: %s", exc)
            return out

        by_prod: Dict[str, List[Tuple[str, int]]] = {}
        # [626차] 금액(백만원) 계열도 같이 싣는다 — 차트의 계약수/금액 토글용.
        #   계약수와 **따로** 모은다: 한쪽만 NULL 인 행이 있을 수 있고, 그 분을
        #   다른 쪽 때문에 버리거나 0 으로 메우면 안 된다(계측 4원칙 ②).
        by_prod_amt: Dict[str, List[Tuple[str, int]]] = {}
        for product, bar_time, net_qty, net_amt in raw:
            if net_qty is not None:
                by_prod.setdefault(product, []).append((bar_time, int(net_qty)))
            if net_amt is not None:
                by_prod_amt.setdefault(product, []).append((bar_time, int(net_amt)))

        last_times = []
        for key in keys:
            pts = by_prod.get(key) or []
            if not pts:
                continue        # 아직 안 옴 — 항목 자체를 만들지 않는다
            base_t, base_v = pts[0]
            series = [(t, v - base_v) for t, v in pts]
            last_t, last_v = pts[-1]
            last_times.append(last_t)
            out["products"][key] = {
                "label":         labels[key],
                # [613차] 단위를 payload 에 싣는다 — 같은 차트에 선물 수급
                # 4행(계약·백만원)이 합류해 **화면의 축이 섞였다.** 단위는
                # 섹션이 아니라 행마다 박혀야 한다(계측 4원칙 ①).
                "unit":          "계약",
                "baseline":      base_v,
                "baseline_time": base_t,
                "value":         last_v,
                "delta":         last_v - base_v,
                "last_time":     last_t,
                "n":             len(pts),
                "series":        series,
            }
            # [626차] 금액 계열 — 시초 기준은 **금액 계열 자신의 첫 관측**이다.
            #   계약수 첫 분과 다를 수 있다. 없으면 키를 만들지 않는다(없음 ≠ 0).
            apts = by_prod_amt.get(key) or []
            if apts:
                abase_t, abase_v = apts[0]
                alast_t, alast_v = apts[-1]
                out["products"][key].update({
                    "unit_amt":          "백만원",
                    "baseline_amt":      abase_v,
                    "baseline_time_amt": abase_t,
                    "value_amt":         alast_v,
                    "delta_amt":         alast_v - abase_v,
                    "last_time_amt":     alast_t,
                    "series_amt":        [(t, v - abase_v) for t, v in apts],
                })
        out["last_time"] = max(last_times) if last_times else None
        return out
