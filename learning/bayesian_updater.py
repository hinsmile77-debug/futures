# learning/bayesian_updater.py — 베이지안 사전확률 실시간 업데이터
"""
매 분봉마다 방향 예측 확률을 베이지안 방식으로 업데이트

핵심 아이디어:
  사전 확률 (prior): 모델 앙상블 예측 확률
  우도 (likelihood): 관측된 피처 패턴이 상승/하락에 얼마나 부합하는가
  사후 확률 (posterior): prior × likelihood (정규화)

  → 단순 앙상블 확률 대비 피처 일치도를 추가로 반영
  → 레짐 변화 시 prior를 빠르게 재설정 (망각 인자 적용)

피처 우도 모델:
  각 피처가 상승/하락과 얼마나 일치했는지 누적 학습
  (온라인 나이브 베이즈 근사)
"""
import numpy as np
import logging
from collections import deque
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("BAYESIAN")


class BayesianUpdater:
    """
    방향 예측을 위한 온라인 베이지안 업데이터

    prior → likelihood(피처 관측) → posterior
    posterior가 진입 신호 최종 확률로 사용됨
    """

    # 망각 인자 (레짐 변화 빠른 적응)
    FORGETTING_FACTOR = 0.98

    # 우도 추정 창 (최근 N분 관측)
    LIKELIHOOD_WINDOW = 50

    # 최소 학습 샘플 (이전에는 prior만 사용)
    MIN_SAMPLES = 30

    def __init__(
        self,
        n_features:     int   = 9,    # 입력 피처 수
        prior_strength: float = 2.0,  # 사전 확률 가중치 (높을수록 prior 신뢰)
    ):
        self.n_features     = n_features
        self.prior_strength = prior_strength

        # 피처별 상승/하락 조건부 누적값 (나이브 베이즈용)
        # shape: [n_features, 2] — [:,0]=하락, [:,1]=상승
        self._feat_sum   = np.ones((n_features, 2), dtype=np.float64)  # Laplace smoothing
        self._feat_sq    = np.ones((n_features, 2), dtype=np.float64)  # 분산용
        self._class_cnt  = np.array([1.0, 1.0], dtype=np.float64)      # [하락, 상승]

        # 최근 관측 버퍼
        self._obs_buffer: deque = deque(maxlen=self.LIKELIHOOD_WINDOW)

        # 학습 카운터
        self.sample_count = 0

        # 레짐 상태 (망각 인자 조정용)
        self._last_regime: Optional[str] = None

        # 사후 확률 히스토리
        self._posterior_history: deque = deque(maxlen=200)

    # ── 핵심 업데이트 ─────────────────────────────────────────────
    def update(
        self,
        features:  np.ndarray,  # 현재 피처 벡터 (n_features,)
        label:     int,         # 실제 방향 0=하락, 1=상승
        regime:    str = "",
    ):
        """
        관측 결과로 우도 파라미터 온라인 업데이트

        Args:
            features: 현재 분봉 피처
            label:    실제 방향 (0/1)
            regime:   현재 레짐 문자열 (변화 감지용)
        """
        # 레짐 변화 시 망각 인자 강화
        if regime and regime != self._last_regime and self._last_regime is not None:
            self._apply_forgetting(factor=0.80)  # 레짐 변화 시 빠른 망각
            logger.debug(f"[Bayes] 레짐 변화 {self._last_regime}→{regime} — 히스토리 80% 할인")
        elif self.sample_count > 0:
            self._apply_forgetting(self.FORGETTING_FACTOR)

        self._last_regime = regime

        # 피처 정규화 후 저장
        feat = np.clip(features[:self.n_features], -5.0, 5.0)

        # 우도 파라미터 갱신 (가우시안 나이브 베이즈 근사)
        self._class_cnt[label]      += 1.0
        self._feat_sum[:, label]    += feat
        self._feat_sq[:, label]     += feat ** 2

        self._obs_buffer.append({"features": feat.copy(), "label": label})
        self.sample_count += 1

    def _apply_forgetting(self, factor: float):
        """망각 인자 적용 — 오래된 관측값 할인"""
        self._feat_sum   *= factor
        self._feat_sq    *= factor
        self._class_cnt  *= factor
        # 최소 평활화 유지
        self._class_cnt  = np.maximum(self._class_cnt, 0.5)

    # ── 사후 확률 계산 ────────────────────────────────────────────
    def predict_posterior(
        self,
        prior_prob:   float,       # 앙상블 모델의 상승 확률 (0~1)
        features:     np.ndarray,  # 현재 피처 벡터
    ) -> dict:
        """
        베이지안 사후 확률 계산

        P(상승|피처) ∝ P(상승) × P(피처|상승)

        Args:
            prior_prob: 주 모델(앙상블)의 상승 예측 확률
            features:   현재 피처

        Returns:
            {posterior_up, posterior_down, bayes_boost, source}
        """
        feat = np.clip(features[:self.n_features], -5.0, 5.0)

        if self.sample_count < self.MIN_SAMPLES:
            # 학습 부족 — prior 그대로 반환
            return {
                "posterior_up":   round(prior_prob, 4),
                "posterior_down": round(1.0 - prior_prob, 4),
                "bayes_boost":    0.0,
                "source":         "prior_only",
            }

        # 클래스 사전확률
        total          = self._class_cnt.sum()
        p_class        = self._class_cnt / total  # [P(하락), P(상승)]

        # 가우시안 우도 계산 (각 피처 독립 가정)
        log_like = np.zeros(2, dtype=np.float64)
        for c in range(2):
            n_c   = max(self._class_cnt[c], 1.0)
            mean  = self._feat_sum[:, c] / n_c
            var   = (self._feat_sq[:, c] / n_c) - mean ** 2
            var   = np.maximum(var, 1e-4)  # 최소 분산

            # 로그 우도 (수치 안정성)
            log_like[c] = -0.5 * np.sum(
                np.log(2 * np.pi * var) + (feat - mean) ** 2 / var
            )

        # 사전 확률 가중 (prior_strength로 앙상블 신뢰도 조정)
        prior_log  = np.array([
            np.log(max(1.0 - prior_prob, 1e-8)) * self.prior_strength,
            np.log(max(prior_prob,       1e-8)) * self.prior_strength,
        ])
        log_post   = log_like + prior_log + np.log(p_class + 1e-8)

        # 수치 안정화
        log_post  -= log_post.max()
        post       = np.exp(log_post)
        post       /= post.sum()

        posterior_up   = float(post[1])
        posterior_down = float(post[0])
        bayes_boost    = posterior_up - prior_prob

        result = {
            "posterior_up":   round(posterior_up, 4),
            "posterior_down": round(posterior_down, 4),
            "bayes_boost":    round(bayes_boost, 4),
            "source":         "bayesian",
        }
        self._posterior_history.append(posterior_up)
        return result

    # ── 레짐별 calibration ────────────────────────────────────────
    def get_regime_prior(self, regime: str, base_prior: float) -> float:
        """
        레짐에 따른 사전 확률 조정

        추세장: 방향성 강화
        횡보장: 0.5로 당기기
        급변장: 0.5 (중립)
        """
        if regime == "추세장":
            # 방향성 강화 (사전 확률과 0.5 사이를 확장)
            return float(np.clip(0.5 + (base_prior - 0.5) * 1.3, 0.1, 0.9))
        elif regime == "횡보장":
            return float(np.clip(0.5 + (base_prior - 0.5) * 0.5, 0.3, 0.7))
        elif regime == "급변장":
            return 0.5
        else:
            return base_prior

    # ── 통계 ─────────────────────────────────────────────────────
    def get_stats(self) -> dict:
        recent = list(self._posterior_history)
        return {
            "sample_count":    self.sample_count,
            "class_balance":   {
                "down": round(float(self._class_cnt[0] / max(self._class_cnt.sum(), 1)), 3),
                "up":   round(float(self._class_cnt[1] / max(self._class_cnt.sum(), 1)), 3),
            },
            "avg_posterior":   round(float(np.mean(recent)), 4) if recent else 0.5,
            "last_regime":     self._last_regime or "",
        }

    def reset_daily(self):
        """일일 리셋 (레짐 히스토리 유지, 학습 파라미터 부분 초기화)"""
        self._apply_forgetting(0.5)   # 하루 시작 시 50% 할인
        self._last_regime = None
        logger.info("[Bayes] 일일 리셋 완료")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    bu = BayesianUpdater(n_features=9)

    np.random.seed(42)
    # 시뮬레이션: 추세장에서 상승 우세
    for i in range(60):
        feat  = np.random.randn(9)
        label = 1 if feat[0] + feat[1] > 0 else 0
        bu.update(feat, label, regime="추세장")

    print(f"stats: {bu.get_stats()}")

    feat_test = np.array([0.5, 0.3, -0.1, 0.2, 0.0, 0.1, -0.2, 0.4, 0.1])
    r = bu.predict_posterior(prior_prob=0.60, features=feat_test)
    print(f"posterior: {r}")

    r2 = bu.predict_posterior(prior_prob=0.40, features=-feat_test)
    print(f"반대 방향: {r2}")
