# features/sentiment/news_features.py — 뉴스 감성 피처 생성기
"""
최근 N분 뉴스 감성 점수를 시계열 피처로 집계

출력 피처:
  sentiment_avg_30m:   최근 30분 가중 평균 감성 점수 (-1 ~ +1)
  sentiment_avg_10m:   최근 10분 가중 평균
  sentiment_trend:     30분 전반부 vs 후반부 추세 (+: 개선, -: 악화)
  sentiment_count_30m: 최근 30분 뉴스 건수
  sentiment_shock:     급격한 부정 뉴스 감지 (0/1)

가중치 설계:
  최신 뉴스에 지수 가중치 (시간 반감기 10분)
  KOSPI 관련 뉴스에 1.5배 가중치

통합 방법:
  매 분봉 pipeline에서 호출
  news_fetcher.get_recent() → 감성 분석 → 피처 벡터
"""
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from collection.news.news_fetcher import NewsItem

logger = logging.getLogger("NEWS_FEAT")

# 시간 반감기 (분) — 최신 뉴스에 더 높은 가중치
TIME_HALF_LIFE_MIN = 10.0

# KOSPI 관련 뉴스 가중치 배율
KOSPI_WEIGHT_MULT  = 1.5

# 감성 충격 임계값 (단기 급락 부정 감지)
SHOCK_THRESHOLD    = -0.5
SHOCK_WINDOW_MIN   = 5


class NewsFeatureBuilder:
    """
    뉴스 감성 → 트레이딩 피처 변환기

    사용:
        builder = NewsFeatureBuilder(sentiment_analyzer)
        news    = fetcher.get_recent(minutes=30)
        feats   = builder.build(news, now=datetime.now())
    """

    def __init__(self, sentiment_analyzer=None):
        """
        Args:
            sentiment_analyzer: SentimentAnalyzer 인스턴스
                                None이면 NewsItem에 score가 있다고 가정
        """
        self._analyzer = sentiment_analyzer

        # 피처 히스토리 (연속 분봉 피처 저장)
        self._feat_history: List[dict] = []

    # ── 핵심 피처 생성 ────────────────────────────────────────────
    def build(
        self,
        news_items: List,          # List[NewsItem]
        now:        Optional[datetime] = None,
    ) -> dict:
        """
        뉴스 아이템 목록 → 분봉 감성 피처

        Args:
            news_items: 최근 N분 뉴스 목록
            now:        기준 시각 (None → 현재 시각)

        Returns:
            피처 딕셔너리
        """
        if now is None:
            now = datetime.now()

        if not news_items:
            feats = self._empty_features()
            self._feat_history.append(feats)
            return feats

        # 감성 점수 계산 (analyzer 없으면 기존 score 사용)
        scored_items = []
        for item in news_items:
            score = getattr(item, "score", None)
            if score is None and self._analyzer is not None:
                result = self._analyzer.analyze(item.title)
                score  = result["score"]
                conf   = result["confidence"]
            else:
                conf = 0.5
            scored_items.append({
                "title":            item.title,
                "published_at":     item.published_at,
                "score":            score or 0.0,
                "confidence":       conf,
                "is_kospi_related": getattr(item, "is_kospi_related", False),
            })

        # 시간 가중치 계산
        for s in scored_items:
            age_min = max(0.0, (now - s["published_at"]).total_seconds() / 60.0)
            # 지수 감소: weight = exp(-age / half_life)
            s["time_weight"] = float(np.exp(-age_min / TIME_HALF_LIFE_MIN))
            if s["is_kospi_related"]:
                s["time_weight"] *= KOSPI_WEIGHT_MULT

        # ── 30분 피처 ────────────────────────────────────────────
        cutoff_30m = now - timedelta(minutes=30)
        items_30m  = [s for s in scored_items if s["published_at"] >= cutoff_30m]
        avg_30m    = self._weighted_avg([s["score"] for s in items_30m],
                                        [s["time_weight"] for s in items_30m])

        # ── 10분 피처 ────────────────────────────────────────────
        cutoff_10m = now - timedelta(minutes=10)
        items_10m  = [s for s in scored_items if s["published_at"] >= cutoff_10m]
        avg_10m    = self._weighted_avg([s["score"] for s in items_10m],
                                        [s["time_weight"] for s in items_10m])

        # ── 감성 추세 (전반 vs 후반) ─────────────────────────────
        cutoff_20m  = now - timedelta(minutes=20)
        items_early = [s for s in items_30m if s["published_at"] < cutoff_20m]
        items_late  = [s for s in items_30m if s["published_at"] >= cutoff_20m]
        avg_early   = self._weighted_avg([s["score"] for s in items_early],
                                         [s["time_weight"] for s in items_early])
        avg_late    = self._weighted_avg([s["score"] for s in items_late],
                                         [s["time_weight"] for s in items_late])
        trend       = avg_late - avg_early   # +: 개선, -: 악화

        # ── 감성 충격 감지 ────────────────────────────────────────
        cutoff_shock = now - timedelta(minutes=SHOCK_WINDOW_MIN)
        items_shock  = [s for s in scored_items if s["published_at"] >= cutoff_shock]
        shock        = 0
        if items_shock:
            min_score = min(s["score"] for s in items_shock)
            if min_score <= SHOCK_THRESHOLD:
                shock = 1

        # ── 신뢰도 가중 조정 ────────────────────────────────────
        if items_30m:
            avg_conf = float(np.mean([s["confidence"] for s in items_30m]))
            # 신뢰도 낮으면 점수를 0으로 당기기
            avg_30m *= avg_conf
            avg_10m *= avg_conf

        feats = {
            "sentiment_avg_30m":    round(float(avg_30m), 4),
            "sentiment_avg_10m":    round(float(avg_10m), 4),
            "sentiment_trend":      round(float(trend), 4),
            "sentiment_count_30m":  len(items_30m),
            "sentiment_shock":      shock,
            # 추가 정보
            "_titles_sample":       [s["title"][:30] for s in items_30m[:3]],
        }

        self._feat_history.append(feats)
        return feats

    # ── 헬퍼 ─────────────────────────────────────────────────────
    @staticmethod
    def _weighted_avg(scores: list, weights: list) -> float:
        if not scores:
            return 0.0
        w_arr  = np.array(weights, dtype=np.float64)
        s_arr  = np.array(scores, dtype=np.float64)
        total  = w_arr.sum()
        if total < 1e-9:
            return float(np.mean(s_arr))
        return float(np.dot(s_arr, w_arr) / total)

    @staticmethod
    def _empty_features() -> dict:
        return {
            "sentiment_avg_30m":   0.0,
            "sentiment_avg_10m":   0.0,
            "sentiment_trend":     0.0,
            "sentiment_count_30m": 0,
            "sentiment_shock":     0,
            "_titles_sample":      [],
        }

    # ── 피처 벡터 (모델 입력용) ───────────────────────────────────
    @staticmethod
    def to_vector(feats: dict) -> np.ndarray:
        """
        딕셔너리 → numpy 벡터 변환 (5개 피처)

        feature_builder.py에 통합할 때 사용
        """
        return np.array([
            feats.get("sentiment_avg_30m",   0.0),
            feats.get("sentiment_avg_10m",   0.0),
            feats.get("sentiment_trend",     0.0),
            feats.get("sentiment_count_30m", 0.0) / 20.0,  # 정규화
            float(feats.get("sentiment_shock", 0)),
        ], dtype=np.float32)

    # ── 사용 가이드 (main pipeline 통합 예시) ────────────────────
    def get_history(self) -> List[dict]:
        return self._feat_history[-50:]   # 최근 50분


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    from features.sentiment.kobert_sentiment import SentimentAnalyzer

    # 더미 NewsItem 클래스
    class FakeNewsItem:
        def __init__(self, title, minutes_ago, is_kospi=True):
            self.title            = title
            self.published_at     = datetime.now() - timedelta(minutes=minutes_ago)
            self.is_kospi_related = is_kospi

    sa      = SentimentAnalyzer()
    builder = NewsFeatureBuilder(sentiment_analyzer=sa)

    items = [
        FakeNewsItem("코스피 급등 외인 대규모 순매수", 2),
        FakeNewsItem("미국 금리 인상 우려 코스피 하락", 8),
        FakeNewsItem("삼성전자 분기 실적 호조", 15),
        FakeNewsItem("코스피 급락 패닉셀링", 3),
        FakeNewsItem("반도체 섹터 랠리 지속", 25),
    ]

    feats = builder.build(items)
    print("피처:", {k: v for k, v in feats.items() if not k.startswith("_")})
    vec   = NewsFeatureBuilder.to_vector(feats)
    print("벡터:", vec)
