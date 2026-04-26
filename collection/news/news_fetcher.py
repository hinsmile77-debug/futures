# collection/news/news_fetcher.py — 뉴스 헤드라인 수집기
"""
한국경제·매일경제 등 금융 뉴스 헤드라인 수집

수집 방법:
  1. RSS 피드 파싱 (requests + xml, 가장 안정적)
  2. Naver 금융 뉴스 API (대체)

수집 주기:
  장 중 5~10분 간격 (과도한 요청 방지)
  배경 스레드로 운영

Python 3.7 32-bit 호환
"""
import time
import logging
import hashlib
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import deque

try:
    import requests
    _REQUESTS_OK = True
except ImportError:
    _REQUESTS_OK = False

try:
    import xml.etree.ElementTree as ET
    _XML_OK = True
except ImportError:
    _XML_OK = False

logger = logging.getLogger("NEWS")

# ── RSS 소스 정의 ─────────────────────────────────────────────────
RSS_SOURCES = {
    "hankyung_economy": {
        "url":  "https://www.hankyung.com/feed/economy",
        "name": "한국경제",
    },
    "hankyung_finance": {
        "url":  "https://www.hankyung.com/feed/finance",
        "name": "한국경제-금융",
    },
    "mk_stock": {
        "url":  "https://www.mk.co.kr/rss/30200030/",
        "name": "매일경제-증권",
    },
    "mk_economy": {
        "url":  "https://www.mk.co.kr/rss/30100041/",
        "name": "매일경제-경제",
    },
    "yonhap_economy": {
        "url":  "https://www.yna.co.kr/rss/economy.xml",
        "name": "연합뉴스-경제",
    },
}

# KOSPI 관련 키워드 필터 (불관련 뉴스 제거)
KOSPI_KEYWORDS = [
    "코스피", "KOSPI", "선물", "외인", "외국인", "기관",
    "금리", "환율", "달러", "원화", "미국", "중국",
    "인플레이션", "긴축", "매수", "매도", "상승", "하락",
    "반등", "급락", "장세", "주가", "증시",
]


class NewsItem:
    """뉴스 아이템 단위"""
    __slots__ = ["id", "source", "title", "published_at", "url", "is_kospi_related"]

    def __init__(
        self,
        source:      str,
        title:       str,
        published_at: datetime,
        url:         str = "",
    ):
        self.source           = source
        self.title            = title
        self.published_at     = published_at
        self.url              = url
        self.id               = hashlib.md5(f"{source}{title}".encode("utf-8")).hexdigest()[:12]
        self.is_kospi_related = self._check_relevance()

    def _check_relevance(self) -> bool:
        return any(kw in self.title for kw in KOSPI_KEYWORDS)

    def to_dict(self) -> dict:
        return {
            "id":               self.id,
            "source":           self.source,
            "title":            self.title,
            "published_at":     self.published_at.strftime("%Y-%m-%d %H:%M"),
            "url":              self.url,
            "is_kospi_related": self.is_kospi_related,
        }

    def __repr__(self):
        return f"[{self.source}] {self.published_at.strftime('%H:%M')} {self.title[:50]}"


class NewsFetcher:
    """
    뉴스 헤드라인 수집 및 캐싱

    사용:
        fetcher = NewsFetcher()
        fetcher.start()          # 백그라운드 수집 시작
        news = fetcher.get_recent(minutes=30)  # 최근 30분 뉴스
        fetcher.stop()
    """

    FETCH_INTERVAL_SEC = 300    # 5분마다 수집
    MAX_CACHE_SIZE     = 500    # 최대 캐시 뉴스 수
    REQUEST_TIMEOUT    = 10     # 요청 타임아웃 (초)

    def __init__(
        self,
        sources:      Optional[List[str]] = None,
        kospi_only:   bool = False,
        fetch_interval: int = FETCH_INTERVAL_SEC,
    ):
        self.sources        = sources or list(RSS_SOURCES.keys())
        self.kospi_only     = kospi_only
        self.fetch_interval = fetch_interval

        # 뉴스 캐시 (NewsItem deque)
        self._cache: deque = deque(maxlen=self.MAX_CACHE_SIZE)
        self._seen_ids: set = set()

        # 백그라운드 스레드
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        # 통계
        self.fetch_count   = 0
        self.total_fetched = 0
        self.last_fetch_time: Optional[datetime] = None
        self.last_error: str = ""

        if not _REQUESTS_OK:
            logger.warning("[News] requests 미설치 — 수집 비활성화")

    # ── 시작 / 정지 ───────────────────────────────────────────────
    def start(self):
        """백그라운드 수집 스레드 시작"""
        if not _REQUESTS_OK:
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._fetch_loop, daemon=True)
        self._thread.start()
        logger.info(f"[News] 수집 시작 (소스={len(self.sources)}개, 주기={self.fetch_interval}초)")

    def stop(self):
        """수집 스레드 정지"""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("[News] 수집 정지")

    def _fetch_loop(self):
        """백그라운드 수집 루프"""
        while not self._stop_event.is_set():
            try:
                self._fetch_all()
            except Exception as e:
                self.last_error = str(e)
                logger.warning(f"[News] 수집 오류: {e}")
            self._stop_event.wait(timeout=self.fetch_interval)

    # ── 수집 로직 ─────────────────────────────────────────────────
    def _fetch_all(self):
        """모든 소스에서 뉴스 수집"""
        count = 0
        for src_key in self.sources:
            if src_key not in RSS_SOURCES:
                continue
            src_info = RSS_SOURCES[src_key]
            items    = self._fetch_rss(src_key, src_info["url"], src_info["name"])
            for item in items:
                if item.id not in self._seen_ids:
                    if not self.kospi_only or item.is_kospi_related:
                        self._cache.append(item)
                        self._seen_ids.add(item.id)
                        count += 1

        self.fetch_count     += 1
        self.total_fetched   += count
        self.last_fetch_time = datetime.now()
        logger.debug(f"[News] 수집 #{self.fetch_count} +{count}건 (누계={self.total_fetched})")

    def _fetch_rss(self, src_key: str, url: str, name: str) -> List[NewsItem]:
        """RSS 피드 파싱"""
        if not _REQUESTS_OK or not _XML_OK:
            return []

        try:
            headers = {"User-Agent": "Mozilla/5.0 (compatible; futures-bot/1.0)"}
            resp    = requests.get(url, headers=headers, timeout=self.REQUEST_TIMEOUT)
            resp.raise_for_status()
            resp.encoding = resp.apparent_encoding or "utf-8"
            return self._parse_rss(resp.text, name)
        except Exception as e:
            logger.debug(f"[News] {src_key} RSS 오류: {e}")
            return []

    def _parse_rss(self, xml_text: str, source_name: str) -> List[NewsItem]:
        """RSS XML 파싱 → NewsItem 목록"""
        items = []
        try:
            root = ET.fromstring(xml_text)
            # 네임스페이스 무시 파싱
            for item in root.iter("item"):
                title_el   = item.find("title")
                pub_el     = item.find("pubDate")
                link_el    = item.find("link")

                if title_el is None or title_el.text is None:
                    continue

                title = title_el.text.strip()
                url   = link_el.text.strip() if link_el is not None and link_el.text else ""
                pub_dt = self._parse_pubdate(pub_el.text if pub_el is not None else "")

                items.append(NewsItem(source=source_name, title=title,
                                      published_at=pub_dt, url=url))
        except ET.ParseError as e:
            logger.debug(f"[News] XML 파싱 오류: {e}")
        return items

    def _parse_pubdate(self, raw: str) -> datetime:
        """RSS 날짜 문자열 파싱"""
        if not raw:
            return datetime.now()
        formats = [
            "%a, %d %b %Y %H:%M:%S %z",
            "%a, %d %b %Y %H:%M:%S %Z",
            "%Y-%m-%dT%H:%M:%S%z",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(raw.strip(), fmt).replace(tzinfo=None)
            except ValueError:
                continue
        return datetime.now()

    # ── 조회 API ──────────────────────────────────────────────────
    def get_recent(
        self,
        minutes:      int  = 30,
        kospi_only:   bool = True,
    ) -> List[NewsItem]:
        """
        최근 N분 이내 뉴스 반환

        Args:
            minutes:    최근 몇 분
            kospi_only: KOSPI 관련 뉴스만

        Returns:
            NewsItem 목록 (최신 순)
        """
        cutoff = datetime.now() - timedelta(minutes=minutes)
        result = [
            item for item in self._cache
            if item.published_at >= cutoff
            and (not kospi_only or item.is_kospi_related)
        ]
        return sorted(result, key=lambda x: x.published_at, reverse=True)

    def get_all_cached(self) -> List[NewsItem]:
        return list(self._cache)

    def manual_fetch(self):
        """수동 즉시 수집 (테스트·디버그용)"""
        self._fetch_all()

    def get_stats(self) -> dict:
        return {
            "cache_size":      len(self._cache),
            "fetch_count":     self.fetch_count,
            "total_fetched":   self.total_fetched,
            "last_fetch":      self.last_fetch_time.strftime("%H:%M:%S") if self.last_fetch_time else "",
            "last_error":      self.last_error,
            "sources":         self.sources,
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    fetcher = NewsFetcher(kospi_only=False)
    fetcher.manual_fetch()
    print(f"수집 통계: {fetcher.get_stats()}")
    recent = fetcher.get_recent(minutes=120, kospi_only=False)
    for n in recent[:5]:
        print(n)
