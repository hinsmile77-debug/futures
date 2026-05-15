# collection/macro/macro_fetcher.py
"""
Global macro feature fetcher.

Returns raw values used by the regime classifier and the macro feature
transformer. This module must stay lightweight and safe to call during
startup because it runs before the live minute pipeline is fully active.
"""

import contextlib
import datetime
import io
import logging
import threading
from typing import Dict, Optional

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
YF_RETRY_COOLDOWN_SEC = 900


class MacroFetcher:
    FETCH_INTERVAL_SEC = 180

    EVENT_DATES: Dict[str, str] = {
        # "20260501": "FOMC",
        # "20260612": "CPI",
    }

    def __init__(self, api_key_fred: str = ""):
        self._fred_key = api_key_fred
        self._cache: Dict[str, float] = {}
        self._cache_time: Optional[datetime.datetime] = None
        self._prev: Dict[str, float] = {}
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self._fetch_lock = threading.Lock()
        self._last_yf_fail_time: Optional[datetime.datetime] = None
        self._last_source: str = "uninitialized"
        self._last_fallback_used: bool = False
        self.fetch_count = 0
        self.last_error = ""

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

    def _fetch_all(self):
        with self._fetch_lock:
            data: Dict[str, float] = {}
            source_parts = []

            if _YFINANCE_OK:
                yf = self._fetch_yfinance()
                if yf:
                    data.update(yf)
                    source_parts.append("yfinance")
            if _REQUESTS_OK:
                naver = self._fetch_naver_fx()
                if naver:
                    data.update(naver)
                    source_parts.append("naver_fx")

            fallback_used = False
            if not data:
                data = self._dummy_values()
                source_parts = ["dummy_fallback"]
                fallback_used = True

            result: Dict[str, float] = {}
            for key in ("sp500", "nasdaq", "vix", "usd_krw", "us10y"):
                curr = data.get(key, 0.0)
                prev = self._prev.get(key, curr)
                if prev and prev != 0:
                    result["%s_chg" % key] = round((curr - prev) / abs(prev), 6)
                else:
                    result["%s_chg" % key] = 0.0
                self._prev[key] = curr

            result["vix"] = round(data.get("vix", 20.0), 2)
            result["event_flag"] = self._check_event_flag()
            result["macro_quality_available"] = 1.0
            result["macro_quality_stale"] = 0.0
            result["macro_quality_age_sec"] = 0.0
            result["macro_quality_fallback_used"] = 1.0 if fallback_used else 0.0
            result["macro_quality_source_code"] = self._source_code("+".join(source_parts))

            self._cache = result
            self._cache_time = datetime.datetime.now()
            self._last_source = "+".join(source_parts)
            self._last_fallback_used = fallback_used
            self.fetch_count += 1
            logger.debug(
                "[Macro] refreshed | VIX=%.1f KRW=%+.4f",
                result["vix"],
                result.get("usd_krw_chg", 0.0),
            )

    def _fetch_yfinance(self) -> Dict[str, float]:
        now = datetime.datetime.now()
        if self._last_yf_fail_time:
            elapsed = (now - self._last_yf_fail_time).total_seconds()
            if elapsed < YF_RETRY_COOLDOWN_SEC:
                logger.debug(
                    "[Macro] yfinance cooldown active (%.0fs remaining)",
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

    def _fetch_naver_fx(self) -> Dict[str, float]:
        if not _REQUESTS_OK:
            return {}
        try:
            url = "https://finance.naver.com/marketindex/exchangeDetail.naver?marketindexCd=FX_USDKRW"
            resp = _req.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
            import re

            m = re.search(r'"basePrice"\s*:\s*"([\d,.]+)"', resp.text)
            if m:
                krw = float(m.group(1).replace(",", ""))
                return {"usd_krw": krw}
        except Exception:
            pass
        return {}

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

    @staticmethod
    def _empty_features() -> Dict[str, float]:
        return {
            "sp500_chg": 0.0,
            "nasdaq_chg": 0.0,
            "vix": 20.0,
            "usd_krw_chg": 0.0,
            "us10y_chg": 0.0,
            "event_flag": 0.0,
            "macro_quality_available": 0.0,
            "macro_quality_stale": 1.0,
            "macro_quality_age_sec": float(CACHE_TTL_SEC),
            "macro_quality_fallback_used": 1.0,
            "macro_quality_source_code": 0.0,
        }

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

    @staticmethod
    def _source_code(source: str) -> float:
        src = str(source or "").lower()
        if "dummy" in src:
            return 0.0
        if "yfinance" in src and "naver" in src:
            return 3.0
        if "yfinance" in src:
            return 2.0
        if "naver" in src:
            return 1.0
        return 0.0


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    macro = MacroFetcher()
    macro.manual_fetch()
    print(macro.get_features())
    print(macro.get_stats())
