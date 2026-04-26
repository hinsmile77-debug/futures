# collection/macro/macro_fetcher.py — 매크로 지표 수집
"""
글로벌 매크로 지표 실시간 수집

수집 항목:
  S&P 500 선물 변동률 (sp500_futures_chg)
  나스닥 선물 변동률 (nasdaq_futures_chg)
  VIX 공포 지수     (vix)
  USD/KRW 환율 변동 (usd_krw_chg)
  미국 10년 금리 변동 (us10y_chg)
  이벤트 플래그     (event_flag: FOMC/CPI 등)

수집 방법:
  1. 국내 API: 네이버 금융 (환율·VIX)
  2. 해외 API: yfinance (^GSPC, ^VIX, DX-Y.NYB)
     → Python 3.7 32-bit에서 yfinance 설치 가능 여부 확인 필요
  3. fallback: 캐시 값 유지 (최대 5분)

Python 3.7 32-bit 호환
"""
import logging
import datetime
import threading
from typing import Optional, Dict

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

# 캐시 유효 시간 (초)
CACHE_TTL_SEC = 300   # 5분


class MacroFetcher:
    """
    글로벌 매크로 지표 수집기

    사용:
        macro = MacroFetcher()
        macro.start()                 # 백그라운드 수집 시작
        feats = macro.get_features()  # 최신 피처 반환
    """

    FETCH_INTERVAL_SEC = 180   # 3분마다 갱신

    # 경제 이벤트 캘린더 (YYYYMMDD 형식)
    # 실제 운영 시 별도 파일/API로 관리
    EVENT_DATES: Dict[str, str] = {
        # "20260501": "FOMC",
        # "20260612": "CPI",
    }

    def __init__(self, api_key_fred: str = ""):
        self._fred_key = api_key_fred

        # 캐시
        self._cache: Dict[str, float] = {}
        self._cache_time: Optional[datetime.datetime] = None

        # 이전 값 (변동률 계산용)
        self._prev: Dict[str, float] = {}

        # 백그라운드 스레드
        self._thread: Optional[threading.Thread] = None
        self._stop   = threading.Event()

        self.fetch_count = 0
        self.last_error  = ""

    # ── 시작 / 정지 ───────────────────────────────────────────────
    def start(self):
        if not _REQUESTS_OK and not _YFINANCE_OK:
            logger.warning("[Macro] requests/yfinance 미설치 — 더미 모드")
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        logger.info("[Macro] 수집 시작")

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
                logger.debug(f"[Macro] 수집 오류: {e}")
            self._stop.wait(timeout=self.FETCH_INTERVAL_SEC)

    # ── 수집 ─────────────────────────────────────────────────────
    def _fetch_all(self):
        data = {}

        if _YFINANCE_OK:
            data.update(self._fetch_yfinance())
        if _REQUESTS_OK:
            data.update(self._fetch_naver_fx())

        if not data:
            data = self._dummy_values()

        # 변동률 계산
        result = {}
        for key in ("sp500", "nasdaq", "vix", "usd_krw", "us10y"):
            curr = data.get(key, 0.0)
            prev = self._prev.get(key, curr)
            if prev and prev != 0:
                result[f"{key}_chg"] = round((curr - prev) / abs(prev), 6)
            else:
                result[f"{key}_chg"] = 0.0
            self._prev[key] = curr

        # VIX 절대값도 보관
        result["vix"] = round(data.get("vix", 20.0), 2)

        # 이벤트 플래그
        result["event_flag"] = self._check_event_flag()

        self._cache      = result
        self._cache_time = datetime.datetime.now()
        self.fetch_count += 1
        logger.debug(f"[Macro] 갱신 | VIX={result['vix']:.1f} KRW={result.get('usd_krw_chg', 0):.4f}")

    def _fetch_yfinance(self) -> dict:
        """yfinance로 글로벌 지수 수집"""
        try:
            tickers = _yf.download(
                "^GSPC ^IXIC ^VIX DX-Y.NYB ^TNX",
                period="2d", interval="1m",
                progress=False, auto_adjust=True
            )
            result = {}
            for sym, key in [("^GSPC", "sp500"), ("^IXIC", "nasdaq"),
                              ("^VIX", "vix"), ("DX-Y.NYB", "usd_dxy"),
                              ("^TNX", "us10y")]:
                try:
                    close = tickers["Close"][sym].dropna()
                    if len(close):
                        result[key] = float(close.iloc[-1])
                except Exception:
                    pass
            return result
        except Exception as e:
            logger.debug(f"[Macro] yfinance 오류: {e}")
            return {}

    def _fetch_naver_fx(self) -> dict:
        """네이버 금융 환율 수집 (USD/KRW)"""
        if not _REQUESTS_OK:
            return {}
        try:
            url  = "https://finance.naver.com/marketindex/exchangeDetail.naver?marketindexCd=FX_USDKRW"
            resp = _req.get(url, timeout=5,
                            headers={"User-Agent": "Mozilla/5.0"})
            # 간단 텍스트 파싱
            import re
            m = re.search(r'"basePrice"\s*:\s*"([\d,.]+)"', resp.text)
            if m:
                krw = float(m.group(1).replace(",", ""))
                return {"usd_krw": krw}
        except Exception:
            pass
        return {}

    def _dummy_values(self) -> dict:
        """더미 값 반환 (API 불가 시)"""
        return {
            "sp500":   5500.0,
            "nasdaq":  18000.0,
            "vix":     20.0,
            "usd_krw": 1380.0,
            "us10y":   4.5,
        }

    def _check_event_flag(self) -> float:
        """오늘이 이벤트 날짜인지 확인 — 1.0이면 이벤트 당일"""
        today = datetime.date.today().strftime("%Y%m%d")
        return 1.0 if today in self.EVENT_DATES else 0.0

    # ── 피처 반환 ─────────────────────────────────────────────────
    def get_features(self) -> Dict[str, float]:
        """
        최신 매크로 피처 반환 (캐시 5분 이내)

        Returns:
            constants.py MACRO_FEATURES 형식의 딕셔너리
        """
        # 캐시 신선도 확인
        if self._cache_time:
            age = (datetime.datetime.now() - self._cache_time).total_seconds()
            if age > CACHE_TTL_SEC:
                logger.debug(f"[Macro] 캐시 만료 ({age:.0f}초)")

        if self._cache:
            return dict(self._cache)

        # 캐시 없으면 즉시 수집
        self._fetch_all()
        return dict(self._cache) if self._cache else self._empty_features()

    def manual_fetch(self):
        """수동 즉시 갱신"""
        self._fetch_all()

    @staticmethod
    def _empty_features() -> Dict[str, float]:
        return {
            "sp500_futures_chg":  0.0,
            "nasdaq_futures_chg": 0.0,
            "vix":                20.0,
            "usd_krw_chg":        0.0,
            "us10y_chg":          0.0,
            "event_flag":         0.0,
        }

    def get_stats(self) -> dict:
        return {
            "fetch_count":  self.fetch_count,
            "cache_age":    round((datetime.datetime.now() - self._cache_time).total_seconds(), 0)
                            if self._cache_time else -1,
            "last_error":   self.last_error,
            "yfinance":     _YFINANCE_OK,
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    macro = MacroFetcher()
    macro.manual_fetch()
    print(macro.get_features())
    print(macro.get_stats())
