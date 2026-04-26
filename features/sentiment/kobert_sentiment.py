# features/sentiment/kobert_sentiment.py — 한국어 감성 분석기
"""
뉴스 헤드라인 감성 분석 (긍정/부정/중립)

Python 3.7 32-bit 호환 전략:
  Tier 1: KoBERT via Hugging Face API (인터넷 접속 시)
  Tier 2: 금융 특화 한국어 키워드 사전 (오프라인 fallback)

키워드 사전 설계:
  KOSPI·선물 특화 용어 수록
  강도 가중치 (-2 ~ +2)
  부정 처리 ("~않", "~못", "~없" 선행 시 극성 반전)

출력:
  score:     -1.0 (매우 부정) ~ +1.0 (매우 긍정)
  label:     "POSITIVE" / "NEGATIVE" / "NEUTRAL"
  confidence: 0.0 ~ 1.0
"""
import re
import logging
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger("SENTIMENT")

# ── Hugging Face API 선택적 import ───────────────────────────────
try:
    import requests as _req
    _REQUESTS_OK = True
except ImportError:
    _REQUESTS_OK = False

# ── 금융 특화 한국어 키워드 사전 ─────────────────────────────────
# 형식: {키워드: 가중치}  (+: 긍정, -: 부정)
_POSITIVE_WORDS = {
    # 강한 긍정 (+2)
    "급등": 2.0, "폭등": 2.0, "신고가": 2.0, "대형호재": 2.0,
    "강세": 1.8, "대량매수": 1.8, "순매수": 1.8,
    # 보통 긍정 (+1)
    "상승": 1.0, "반등": 1.0, "회복": 1.0, "호조": 1.0,
    "매수": 1.0, "긍정적": 1.0, "개선": 1.0, "증가": 0.8,
    "안정": 0.7, "호실적": 1.2, "돌파": 1.2, "랠리": 1.5,
    "외인매수": 1.5, "기관매수": 1.5, "역대최고": 2.0,
    # 약한 긍정 (+0.5)
    "소폭상승": 0.5, "강보합": 0.5, "선방": 0.5,
}

_NEGATIVE_WORDS = {
    # 강한 부정 (-2)
    "급락": -2.0, "폭락": -2.0, "신저가": -2.0, "패닉": -2.0,
    "대폭락": -2.0, "붕괴": -2.0, "충격": -1.8,
    "공황": -2.0, "위기": -1.5,
    # 보통 부정 (-1)
    "하락": -1.0, "약세": -1.2, "순매도": -1.0, "매도": -1.0,
    "부진": -1.0, "감소": -0.8, "악재": -1.5, "리스크": -0.8,
    "불안": -1.0, "우려": -0.8, "경고": -1.2, "침체": -1.5,
    "외인매도": -1.5, "기관매도": -1.5, "투매": -2.0,
    # 약한 부정 (-0.5)
    "소폭하락": -0.5, "약보합": -0.5, "저조": -0.5,
}

# 문맥 수정어 (선행 부정 처리)
_NEGATION_PATTERNS = ["않", "못", "없", "아니", "부정", "반락"]

# 강화 수정어
_INTENSIFIERS = {"매우": 1.5, "급": 1.8, "대폭": 1.8, "극": 2.0, "초": 1.5}


class SentimentAnalyzer:
    """
    뉴스 헤드라인 감성 분석기

    설계 원칙:
      오프라인에서도 안정적으로 동작하는 키워드 사전 기반
      온라인 시 HuggingFace Inference API로 정밀도 향상
    """

    # HuggingFace Inference API (snunlp/KR-FinBert-SC 한국어 금융 BERT)
    HF_MODEL_ID  = "snunlp/KR-FinBert-SC"
    HF_API_URL   = f"https://api-inference.huggingface.co/models/{HF_MODEL_ID}"
    HF_TIMEOUT   = 5   # 초 (장 중 지연 최소화)

    def __init__(
        self,
        hf_api_token:  Optional[str] = None,
        use_api:       bool          = True,
    ):
        """
        Args:
            hf_api_token: HuggingFace API 토큰 (None이면 API 사용 안 함)
            use_api:      API 사용 여부
        """
        self._hf_token  = hf_api_token
        self._use_api   = use_api and _REQUESTS_OK and hf_api_token is not None
        self._api_ok    = self._use_api   # API 오류 발생 시 False로 전환

        # 결합 사전
        self._lexicon: Dict[str, float] = {}
        self._lexicon.update(_POSITIVE_WORDS)
        self._lexicon.update(_NEGATIVE_WORDS)

        mode = "HuggingFace API + 사전" if self._use_api else "키워드 사전"
        logger.info(f"[Sentiment] 초기화 완료 — 모드: {mode}")

    # ── 공개 API ─────────────────────────────────────────────────
    def analyze(self, text: str) -> dict:
        """
        단일 텍스트 감성 분석

        Returns:
            {score, label, confidence, method}
        """
        if not text or not text.strip():
            return {"score": 0.0, "label": "NEUTRAL", "confidence": 0.0, "method": "empty"}

        # Tier 1: API 시도
        if self._use_api and self._api_ok:
            result = self._analyze_api(text)
            if result is not None:
                return result

        # Tier 2: 키워드 사전
        return self._analyze_lexicon(text)

    def analyze_batch(self, texts: List[str]) -> List[dict]:
        """배치 분석"""
        return [self.analyze(t) for t in texts]

    # ── HuggingFace API ──────────────────────────────────────────
    def _analyze_api(self, text: str) -> Optional[dict]:
        """HuggingFace Inference API 호출"""
        try:
            headers = {"Authorization": f"Bearer {self._hf_token}"}
            payload = {"inputs": text}
            resp    = _req.post(
                self.HF_API_URL, headers=headers, json=payload,
                timeout=self.HF_TIMEOUT
            )
            resp.raise_for_status()
            data = resp.json()

            # KR-FinBert-SC 출력: [[{label, score},...]]
            if isinstance(data, list) and data and isinstance(data[0], list):
                preds = data[0]
            elif isinstance(data, list) and data and isinstance(data[0], dict):
                preds = data
            else:
                return None

            # 레이블 매핑 (모델별 상이)
            label_map = {
                "positive": 1.0, "negative": -1.0, "neutral": 0.0,
                "POSITIVE": 1.0, "NEGATIVE": -1.0, "NEUTRAL": 0.0,
                "긍정": 1.0, "부정": -1.0, "중립": 0.0,
            }

            best = max(preds, key=lambda x: x.get("score", 0))
            raw_label = best.get("label", "NEUTRAL")
            polarity  = label_map.get(raw_label, 0.0)
            conf      = float(best.get("score", 0.5))
            score     = polarity * conf

            return {
                "score":      round(score, 4),
                "label":      self._score_to_label(score),
                "confidence": round(conf, 4),
                "method":     "huggingface_api",
            }
        except Exception as e:
            logger.debug(f"[Sentiment] API 오류 → fallback: {e}")
            self._api_ok = False
            return None

    # ── 키워드 사전 분석 ──────────────────────────────────────────
    def _analyze_lexicon(self, text: str) -> dict:
        """
        키워드 사전 기반 감성 분석

        1. 텍스트에서 키워드 탐색
        2. 부정 선행어 처리
        3. 강화 수정어 처리
        4. 가중 합산 → 정규화
        """
        score       = 0.0
        match_count = 0

        # 강화 수정어 스캔
        intensify = 1.0
        for word, mult in _INTENSIFIERS.items():
            if word in text:
                intensify = max(intensify, mult)

        for keyword, weight in self._lexicon.items():
            if keyword not in text:
                continue

            # 부정 처리: 키워드 앞 5글자 이내 부정어 있으면 극성 반전
            pos = text.find(keyword)
            prefix = text[max(0, pos - 5): pos]
            negated = any(neg in prefix for neg in _NEGATION_PATTERNS)

            w = -weight if negated else weight
            w *= intensify
            score       += w
            match_count += 1

        # 정규화 (-1 ~ +1)
        if match_count > 0:
            norm_score = score / (match_count * 2.0)
            norm_score = max(-1.0, min(1.0, norm_score))
            confidence = min(1.0, match_count * 0.2)
        else:
            norm_score = 0.0
            confidence = 0.0

        return {
            "score":      round(float(norm_score), 4),
            "label":      self._score_to_label(norm_score),
            "confidence": round(confidence, 4),
            "method":     "lexicon",
        }

    @staticmethod
    def _score_to_label(score: float) -> str:
        if score > 0.1:
            return "POSITIVE"
        elif score < -0.1:
            return "NEGATIVE"
        else:
            return "NEUTRAL"

    def get_stats(self) -> dict:
        return {
            "mode":       "api+lexicon" if self._use_api else "lexicon",
            "api_ok":     self._api_ok,
            "lexicon_size": len(self._lexicon),
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    sa = SentimentAnalyzer(hf_api_token=None)  # API 없이 테스트

    tests = [
        "코스피 급등, 외국인 순매수 확대",
        "코스피 급락, 패닉 셀링 확산",
        "코스피 소폭 상승, 보합세",
        "미국 금리 인상 우려로 증시 하락",
        "외인 매수세 유입으로 코스피 반등",
        "부진한 실적에 낙폭 확대",
    ]

    for t in tests:
        r = sa.analyze(t)
        print(f"  [{r['label']:8}] score={r['score']:+.3f} conf={r['confidence']:.2f} | {t}")
