# collection/macro/macro_fetcher.py
"""
Global macro feature fetcher.

Returns raw values used by the regime classifier and the macro feature
transformer. This module must stay lightweight and safe to call during
startup because it runs before the live minute pipeline is fully active.

수집 우선순위 (2026-06 기준 yfinance 429 rate-limit 대응):
  VIX     : Cboe CDN → yfinance fallback
  S&P 500 : Yahoo v8 daily (1d interval — 429 없음) → yfinance fallback
  US10Y   : Treasury XML → Yahoo v8 daily fallback
  USD/KRW : Naver (regex) → frankfurter.app → yfinance fallback
"""

import contextlib
import datetime
import io
import json
import logging
import re
import threading
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("MACRO")

try:
    import requests as _req
    _REQUESTS_OK = True
except ImportError:
    _REQUESTS_OK = False

try:
    import yfinance as _yf
    _YFINANCE_OK = True
except ImportError:
    _YFINANCE_OK = False


CACHE_TTL_SEC = 300
YF_RETRY_COOLDOWN_SEC = 180

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


class MacroFetcher:
    FETCH_INTERVAL_SEC = 180

    EVENT_DATES: Dict[str, str] = {
        # "20260701": "FOMC",
    }

    def __init__(self, api_key_fred: str = ""):
        self._fred_key = api_key_fred
        self._cache: Dict[str, float] = {}
        self._cache_time: Optional[datetime.datetime] = None
        self._first_fetch_done: bool = False
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self._fetch_lock = threading.Lock()
        self._last_yf_fail_time: Optional[datetime.datetime] = None
        self._last_source: str = "uninitialized"
        self._last_fallback_used: bool = False
        self._last_good_vix: Optional[float] = None
        self.fetch_count = 0
        self.last_error = ""

    # ------------------------------------------------------------------
    # lifecycle
    # ------------------------------------------------------------------

    def start(self):
        if not _REQUESTS_OK and not _YFINANCE_OK:
            logger.warning("[Macro] requests/yfinance unavailable; using fallback values")
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        logger.info("[Macro] fetch thread started")

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5)

    def _loop(self):
        while not self._stop.is_set():
            try:
                self._fetch_all()
            except Exception as e:
                self.last_error = str(e)
                logger.debug("[Macro] fetch error: %s", e)
            self._stop.wait(timeout=self.FETCH_INTERVAL_SEC)

    # ------------------------------------------------------------------
    # main fetch
    # ------------------------------------------------------------------

    def _fetch_all(self):
        with self._fetch_lock:
            raw: Dict[str, float] = {}   # key → (curr, prev) or just curr
            raw_prev: Dict[str, float] = {}
            source_parts: List[str] = []

            # --- 1. VIX: Cboe CDN (가장 신뢰할 수 있는 VIX 소스) ---
            if _REQUESTS_OK:
                cboe = self._fetch_cboe_vix()
                if cboe:
                    raw.update(cboe)
                    source_parts.append("cboe")

            # --- 2. S&P500 + (US10Y 보조): Yahoo v8 daily ---
            if _REQUESTS_OK:
                yh = self._fetch_yahoo_daily()
                if yh:
                    raw.update(yh)
                    source_parts.append("yahoo_daily")

            # --- 3. US10Y: Treasury XML (공식 소스, 더 신뢰) ---
            if _REQUESTS_OK:
                tr = self._fetch_treasury_us10y()
                if tr:
                    raw.update(tr)   # Treasury가 Yahoo daily보다 우선
                    if "treasury" not in source_parts:
                        source_parts.append("treasury")

            # --- 4. USD/KRW: Naver (current) + frankfurter (전일 비교용) ---
            if _REQUESTS_OK:
                naver = self._fetch_naver_fx()
                # frankfurter: 전일 값(_prev_usd_krw) 포함이 목적 — Naver 성공 여부와 무관하게 호출
                frank = self._fetch_frankfurter_krw()
                if naver:
                    raw.update(naver)
                    source_parts.append("naver_fx")
                    # 전일 KRW는 frankfurter에서 보완
                    if frank and "_prev_usd_krw" in frank:
                        raw["_prev_usd_krw"] = frank["_prev_usd_krw"]
                elif frank:
                    raw.update(frank)
                    source_parts.append("frankfurter")

            # --- 5. yfinance fallback (rate-limit 해제 시 자동 복귀) ---
            if _YFINANCE_OK and not raw:
                yf = self._fetch_yfinance()
                if yf:
                    raw.update(yf)
                    source_parts.append("yfinance")
                    if "vix" in yf:
                        self._last_good_vix = float(yf["vix"])

            # --- fallback: dummy ---
            fallback_used = False
            if not raw:
                fallback_vix = self._last_good_vix if self._last_good_vix is not None else 20.0
                raw = self._dummy_values()
                raw["vix"] = fallback_vix
                source_parts = [
                    "prev_vix_fallback" if self._last_good_vix is not None else "dummy_fallback"
                ]
                fallback_used = True
                logger.warning(
                    "[Macro] 수집 실패 — fallback vix=%.1f src=%s",
                    fallback_vix, source_parts[0],
                )

            # VIX 캐시 갱신
            if "vix" in raw and not fallback_used:
                self._last_good_vix = float(raw["vix"])

            # --- chg 계산 ---
            result: Dict[str, float] = {}
            for key in ("sp500", "nasdaq", "vix", "usd_krw", "us10y"):
                curr = raw.get(key, 0.0)
                # _prev_key: _fetch_* 가 함께 반환한 전일 값
                prev_from_hist = raw.get("_prev_" + key)

                if not self._first_fetch_done:
                    result["%s_chg" % key] = 0.0
                elif prev_from_hist is not None and prev_from_hist != 0:
                    # 역사적 전일 값 사용 (더 정확한 daily change)
                    result["%s_chg" % key] = round(
                        (curr - prev_from_hist) / abs(prev_from_hist), 6
                    )
                else:
                    result["%s_chg" % key] = 0.0

            result["vix"] = round(raw.get("vix", 20.0), 2)
            result["event_flag"] = self._check_event_flag()
            result["macro_quality_available"] = 1.0
            result["macro_quality_stale"] = 0.0
            result["macro_quality_age_sec"] = 0.0
            result["macro_quality_fallback_used"] = 1.0 if fallback_used else 0.0
            result["macro_quality_source_code"] = self._source_code("+".join(source_parts))
            result["macro_first_fetch_seed_only"] = 0.0 if self._first_fetch_done else 1.0

            if not self._first_fetch_done:
                self._first_fetch_done = True
                logger.info("[Macro] 첫 fetch 완료 src=%s VIX=%.1f",
                            "+".join(source_parts), result["vix"])

            self._cache = result
            self._cache_time = datetime.datetime.now()
            self._last_source = "+".join(source_parts)
            self._last_fallback_used = fallback_used
            self.fetch_count += 1

            if not fallback_used:
                logger.debug(
                    "[Macro] 갱신 | VIX=%.2f SP500chg=%+.4f US10Y=%.3f KRW=%.1f src=%s",
                    result["vix"],
                    result.get("sp500_chg", 0.0),
                    result.get("us10y_chg", 0.0) + raw.get("us10y", 0.0),
                    raw.get("usd_krw", 0.0),
                    "+".join(source_parts),
                )

    # ------------------------------------------------------------------
    # 개별 수집 메서드
    # ------------------------------------------------------------------

    def _fetch_cboe_vix(self) -> Dict[str, float]:
        """Cboe CDN — VIX 일봉 CSV (공식 소스, 매일 갱신)."""
        try:
            url = "https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv"
            r = _req.get(url, headers=_HEADERS, timeout=10)
            if r.status_code != 200:
                return {}
            lines = r.text.strip().splitlines()
            # CSV: DATE,OPEN,HIGH,LOW,CLOSE
            if len(lines) < 3:
                return {}
            last_row = lines[-1].split(",")
            prev_row = lines[-2].split(",")
            curr_vix = float(last_row[4])
            prev_vix = float(prev_row[4])
            return {"vix": curr_vix, "_prev_vix": prev_vix}
        except Exception as e:
            logger.debug("[Macro] Cboe VIX error: %s", e)
            return {}

    def _fetch_yahoo_daily(self) -> Dict[str, float]:
        """Yahoo v8 chart API — 일봉 (1d interval은 crumb 불필요, 429 없음).

        S&P500, US10Y(^TNX) 수집. range=5d로 2일치 close 확보.
        """
        result: Dict[str, float] = {}
        targets = [
            ("^GSPC", "sp500"),
            ("^TNX",  "us10y"),
        ]
        for sym, key in targets:
            try:
                url = (
                    "https://query1.finance.yahoo.com/v8/finance/chart/"
                    "{}?range=5d&interval=1d".format(sym)
                )
                r = _req.get(url, headers=_HEADERS, timeout=8)
                if r.status_code != 200:
                    continue
                d = json.loads(r.text)
                closes = d["chart"]["result"][0]["indicators"]["quote"][0]["close"]
                closes = [c for c in closes if c is not None]
                if len(closes) >= 2:
                    result[key] = float(closes[-1])
                    result["_prev_" + key] = float(closes[-2])
                elif len(closes) == 1:
                    result[key] = float(closes[-1])
            except Exception as e:
                logger.debug("[Macro] Yahoo daily %s error: %s", sym, e)
        return result

    def _fetch_treasury_us10y(self) -> Dict[str, float]:
        """US Treasury XML — 10년 국채금리 (공식 소스).

        당월 데이터가 없으면 전월로 자동 fallback.
        태그 형식: <d:BC_10YEAR m:type="Edm.Double">4.48</d:BC_10YEAR>
        """
        today = datetime.date.today()
        months_to_try = [
            today.strftime("%Y%m"),
            (today.replace(day=1) - datetime.timedelta(days=1)).strftime("%Y%m"),
        ]
        for ym in months_to_try:
            try:
                url = (
                    "https://home.treasury.gov/resource-center/data-chart-center"
                    "/interest-rates/pages/xml?data=daily_treasury_yield_curve"
                    "&field_tdr_date_value_month={}".format(ym)
                )
                r = _req.get(url, headers=_HEADERS, timeout=10)
                if r.status_code != 200:
                    continue
                vals = re.findall(r"<d:BC_10YEAR[^>]*>([\d.]+)</d:BC_10YEAR>", r.text)
                if len(vals) >= 2:
                    return {
                        "us10y": float(vals[-1]),
                        "_prev_us10y": float(vals[-2]),
                    }
                elif len(vals) == 1:
                    return {"us10y": float(vals[-1])}
            except Exception as e:
                logger.debug("[Macro] Treasury US10Y error: %s", e)
        return {}

    def _fetch_naver_fx(self) -> Dict[str, float]:
        """Naver 환율 — USD/KRW."""
        try:
            url = "https://finance.naver.com/marketindex/exchangeDetail.naver?marketindexCd=FX_USDKRW"
            r = _req.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
            # 패턴 예: <td>1,514.10<img
            m = re.search(r"<td>([\d,]+\.\d{2})<img", r.text)
            if m:
                krw = float(m.group(1).replace(",", ""))
                return {"usd_krw": krw}
        except Exception as e:
            logger.debug("[Macro] Naver FX error: %s", e)
        return {}

    def _fetch_frankfurter_krw(self) -> Dict[str, float]:
        """frankfurter.app — USD/KRW 전일 대비 일봉 변화 (무료).

        latest 날짜 D와 그 전일 D-1을 함께 조회해 daily chg 계산.
        """
        try:
            # 최신 날짜 확인
            r = _req.get("https://api.frankfurter.app/latest?from=USD&to=KRW",
                         headers=_HEADERS, timeout=8)
            if r.status_code != 200:
                return {}
            d = json.loads(r.text)
            curr_krw = d.get("rates", {}).get("KRW")
            curr_date = d.get("date")
            if not curr_krw or not curr_date:
                return {}

            # 전일 데이터 조회 (D-1)
            prev_date = (
                datetime.datetime.strptime(curr_date, "%Y-%m-%d")
                - datetime.timedelta(days=3)  # 주말 포함 여유
            ).strftime("%Y-%m-%d")
            r2 = _req.get(
                "https://api.frankfurter.app/{}..{}?from=USD&to=KRW".format(
                    prev_date, curr_date
                ),
                headers=_HEADERS, timeout=8,
            )
            prev_krw = None
            if r2.status_code == 200:
                d2 = json.loads(r2.text)
                # rates: {"2026-06-10": {"KRW": 1518.0}, "2026-06-12": {"KRW": 1520.21}}
                dates_sorted = sorted(d2.get("rates", {}).keys())
                if len(dates_sorted) >= 2:
                    prev_krw = d2["rates"][dates_sorted[-2]].get("KRW")

            result = {"usd_krw": float(curr_krw)}
            if prev_krw:
                result["_prev_usd_krw"] = float(prev_krw)
            return result
        except Exception as e:
            logger.debug("[Macro] frankfurter KRW error: %s", e)
        return {}

    def _fetch_yfinance(self) -> Dict[str, float]:
        """yfinance — rate-limit 해제 시 자동 복귀 fallback."""
        now = datetime.datetime.now()
        if self._last_yf_fail_time:
            elapsed = (now - self._last_yf_fail_time).total_seconds()
            if elapsed < YF_RETRY_COOLDOWN_SEC:
                logger.debug(
                    "[Macro] yfinance cooldown (%.0fs remaining)",
                    YF_RETRY_COOLDOWN_SEC - elapsed,
                )
                return {}
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                tickers = _yf.download(
                    "^GSPC ^IXIC ^VIX DX-Y.NYB ^TNX",
                    period="2d",
                    interval="1m",
                    progress=False,
                    auto_adjust=True,
                    threads=False,
                )
            result: Dict[str, float] = {}
            for sym, key in [
                ("^GSPC", "sp500"),
                ("^IXIC", "nasdaq"),
                ("^VIX", "vix"),
                ("DX-Y.NYB", "usd_dxy"),
                ("^TNX", "us10y"),
            ]:
                try:
                    close = tickers["Close"][sym].dropna()
                    if len(close):
                        result[key] = float(close.iloc[-1])
                except Exception:
                    pass
            if not result:
                self._last_yf_fail_time = now
            return result
        except Exception as e:
            self._last_yf_fail_time = now
            logger.debug("[Macro] yfinance error: %s", e)
            return {}

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    def get_features(self) -> Dict[str, float]:
        now = datetime.datetime.now()
        age = -1.0
        if self._cache_time:
            age = (now - self._cache_time).total_seconds()
            if age > CACHE_TTL_SEC:
                logger.debug("[Macro] cache expired (%.0fs)", age)

        if self._cache:
            result = dict(self._cache)
            is_stale = bool(age > CACHE_TTL_SEC) if age >= 0 else False
            result["macro_quality_age_sec"] = float(max(age, 0.0))
            result["macro_quality_stale"] = 1.0 if is_stale else 0.0
            result["macro_quality_available"] = 1.0
            result["macro_quality_fallback_used"] = 1.0 if self._last_fallback_used else 0.0
            result["macro_quality_source_code"] = self._source_code(self._last_source)
            return result

        self._fetch_all()
        if self._cache:
            result = dict(self._cache)
            result["macro_quality_age_sec"] = 0.0
            result["macro_quality_stale"] = 0.0
            result["macro_quality_available"] = 1.0
            result["macro_quality_fallback_used"] = 1.0 if self._last_fallback_used else 0.0
            result["macro_quality_source_code"] = self._source_code(self._last_source)
            return result
        return self._empty_features()

    def manual_fetch(self):
        self._fetch_all()

    def get_stats(self) -> Dict[str, float]:
        cache_age = (
            round((datetime.datetime.now() - self._cache_time).total_seconds(), 0)
            if self._cache_time
            else -1
        )
        return {
            "fetch_count": self.fetch_count,
            "cache_age": cache_age,
            "quality_stale": 1.0 if (cache_age >= 0 and cache_age > CACHE_TTL_SEC) else 0.0,
            "quality_available": 1.0 if bool(self._cache) else 0.0,
            "quality_fallback_used": 1.0 if self._last_fallback_used else 0.0,
            "quality_source_code": float(self._source_code(self._last_source)),
            "last_error": self.last_error,
            "yfinance": _YFINANCE_OK,
        }

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    def _dummy_values(self) -> Dict[str, float]:
        return {
            "sp500": 5500.0,
            "nasdaq": 18000.0,
            "vix": 20.0,
            "usd_krw": 1380.0,
            "us10y": 4.5,
        }

    def _check_event_flag(self) -> float:
        today = datetime.date.today().strftime("%Y%m%d")
        return 1.0 if today in self.EVENT_DATES else 0.0

    @staticmethod
    def _empty_features() -> Dict[str, float]:
        return {
            "sp500_chg": 0.0,
            "nasdaq_chg": 0.0,
            "vix": 20.0,
            "vix_chg": 0.0,
            "usd_krw_chg": 0.0,
            "us10y_chg": 0.0,
            "event_flag": 0.0,
            "macro_quality_available": 0.0,
            "macro_quality_stale": 1.0,
            "macro_quality_age_sec": float(CACHE_TTL_SEC),
            "macro_quality_fallback_used": 1.0,
            "macro_quality_source_code": 0.0,
        }

    @staticmethod
    def _source_code(source: str) -> float:
        src = str(source or "").lower()
        if "dummy" in src:
            return 0.0
        # 새 소스 코드: cboe/treasury/yahoo_daily 사용 시 최고 품질
        if "cboe" in src or "treasury" in src or "yahoo_daily" in src:
            return 4.0
        if "yfinance" in src and "naver" in src:
            return 3.0
        if "yfinance" in src:
            return 2.0
        if "naver" in src or "frankfurter" in src:
            return 1.0
        return 0.0


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(name)s %(message)s")
    macro = MacroFetcher()
    macro.manual_fetch()
    print("\n=== FEATURES ===")
    for k, v in sorted(macro.get_features().items()):
        print("  {:40s} = {}".format(k, v))
    print("\n=== STATS ===")
    for k, v in macro.get_stats().items():
        print("  {:30s} = {}".format(k, v))
