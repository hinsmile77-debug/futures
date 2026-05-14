# model/ensemble_decision.py — 앙상블 가중합 + 진입 등급 판정
"""
6개 호라이즌 예측을 가중합하여 최종 방향·신뢰도·진입 등급을 결정합니다.

앙상블 가중치 (설계 명세 4-3):
  기본:  1분 10% / 3분 15% / 5분 20% / 10분 20% / 15분 20% / 30분 15%
  상관관계 역수 조정(HorizonDecorrelator):
    - 30분 롤링 창에서 호라이즌 간 실측 상관계수를 추적
    - 상관이 높은 호라이즌의 가중치를 자동으로 낮춰 이중 가중을 완화
    - 데이터 부족 시 ENSEMBLE_WEIGHTS_CORR_ADJ 정적 추정치로 fallback
"""
import logging
import math
from collections import deque
from typing import Dict, Optional, Tuple

from config.settings import (
    ENSEMBLE_WEIGHTS, ENSEMBLE_WEIGHTS_CORR_ADJ, HORIZONS,
    REGIME_MIN_CONFIDENCE, ENTRY_GRADE,
)
from config.constants import DIRECTION_UP, DIRECTION_DOWN, DIRECTION_FLAT
from model.ensemble_gater import AdaptiveEnsembleGater

logger = logging.getLogger("SIGNAL")


class HorizonDecorrelator:
    """
    호라이즌 간 실측 상관계수를 추적하여 앙상블 가중치를 동적으로 조정.

    이중 가중 완화 원리:
      - 매분 각 호라이즌의 prob_up을 60분 롤링 버퍼에 쌓는다.
      - 15분마다 pairwise 상관계수를 계산, 각 호라이즌의 평균 |ρ|를 산출.
      - w_adj[h] = (1 - avg_|ρ|[h]) / Σ(1 - avg_|ρ|) 로 정규화.
      - 샘플이 MIN_SAMPLES 미만이면 ENSEMBLE_WEIGHTS_CORR_ADJ 정적값 사용.
    """

    MIN_SAMPLES  = 30
    UPDATE_EVERY = 15   # 15분마다 재계산
    BUF_SIZE     = 60   # 60분 롤링 창

    def __init__(self):
        self._horizons = list(HORIZONS.keys())
        self._buf = {h: deque(maxlen=self.BUF_SIZE) for h in self._horizons}
        self._weights = dict(ENSEMBLE_WEIGHTS_CORR_ADJ)
        self._ticks   = 0

    def push(self, horizon_proba: Dict[str, Dict]) -> None:
        """매분 예측 결과를 버퍼에 추가하고 필요 시 가중치를 재계산한다."""
        for h in self._horizons:
            p = horizon_proba.get(h, {}).get("up", 0.5)
            self._buf[h].append(float(p))

        self._ticks += 1
        if self._ticks % self.UPDATE_EVERY == 0:
            self._recompute()

    def _recompute(self) -> None:
        min_len = min(len(self._buf[h]) for h in self._horizons)
        if min_len < self.MIN_SAMPLES:
            return

        # 각 호라이즌의 다른 5개 호라이즌과의 평균 |ρ|
        avg_abs_rho: Dict[str, float] = {}
        for h in self._horizons:
            rhos = []
            for other in self._horizons:
                if other == h:
                    continue
                rho = self._pearson(
                    list(self._buf[h])[-min_len:],
                    list(self._buf[other])[-min_len:],
                )
                rhos.append(abs(rho))
            avg_abs_rho[h] = sum(rhos) / len(rhos) if rhos else 0.5

        # w_adj[h] = (1 - avg_|ρ|[h]) / 정규화
        raw   = {h: max(1.0 - avg_abs_rho[h], 0.05) for h in self._horizons}
        total = sum(raw.values())
        if total <= 0:
            return

        self._weights = {h: raw[h] / total for h in self._horizons}
        logger.debug(
            "[Decorr] 가중치 갱신 (샘플=%d) | %s",
            min_len,
            {k: round(v, 3) for k, v in self._weights.items()},
        )

    @staticmethod
    def _pearson(x: list, y: list) -> float:
        n = len(x)
        if n < 2:
            return 0.0
        mx = sum(x) / n
        my = sum(y) / n
        cov = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y)) / n
        sx  = math.sqrt(sum((xi - mx) ** 2 for xi in x) / n)
        sy  = math.sqrt(sum((yi - my) ** 2 for yi in y) / n)
        return cov / (sx * sy) if sx * sy > 1e-9 else 0.0

    @property
    def weights(self) -> Dict[str, float]:
        """현재 유효 가중치 반환 (정규화 보장)."""
        return dict(self._weights)

    def get_status(self) -> Dict:
        min_len = min(len(self._buf[h]) for h in self._horizons)
        return {
            "samples": min_len,
            "adaptive": min_len >= self.MIN_SAMPLES,
            "weights": {k: round(v, 4) for k, v in self._weights.items()},
        }


class EnsembleDecision:
    """앙상블 신호 생성 + 진입 등급 판정"""

    def __init__(self):
        self.gater    = AdaptiveEnsembleGater()
        self._decorr  = HorizonDecorrelator()

    def compute(
        self,
        horizon_proba: Dict[str, Dict],
        regime: str = "NEUTRAL",
        features: Optional[Dict[str, float]] = None,
        adaptive_gating: bool = True,
    ) -> Dict:
        """
        Args:
            horizon_proba: MultiHorizonModel.predict_proba() 결과
            regime:        현재 매크로 레짐

        Returns:
            {direction, confidence, up_score, down_score,
             grade, auto_entry, regime_ok, detail}
        """
        # ── 가중합 (상관관계 역수 적응형 가중치 적용) ──────────────
        # HorizonDecorrelator: 실측 호라이즌 간 상관관계를 추적하여
        # 이중 가중(double-counting)을 완화. 샘플 부족 시 정적 추정치 사용.
        cur_weights = self._decorr.weights
        self._decorr.push(horizon_proba)   # 이번 예측을 버퍼에 기록

        up_score   = 0.0
        down_score = 0.0
        total_w    = 0.0

        detail = {}
        for h, w in cur_weights.items():
            res = horizon_proba.get(h, {})
            if not res:
                continue
            up_score   += res.get("up",   0.0) * w
            down_score += res.get("down", 0.0) * w
            total_w    += w
            detail[h]  = {
                "direction":  res.get("direction"),
                "confidence": res.get("confidence"),
                "weight":     round(w, 4),
            }

        if total_w > 0:
            up_score   /= total_w
            down_score /= total_w

        flat_score = max(0.0, 1.0 - up_score - down_score)

        # ── 최종 방향·신뢰도 ─────────────────────────────────
        if up_score >= down_score and up_score >= flat_score:
            direction  = DIRECTION_UP
            confidence = up_score
        elif down_score > up_score and down_score >= flat_score:
            direction  = DIRECTION_DOWN
            confidence = down_score
        else:
            direction  = DIRECTION_FLAT
            confidence = flat_score

        gating = {
            "reason": "disabled",
            "blocked": False,
            "delta": 0.0,
            "gate_strength": 0.0,
            "signals": {},
        }
        if adaptive_gating:
            gating = self.gater.apply(
                direction=direction,
                up_score=up_score,
                down_score=down_score,
                flat_score=flat_score,
                confidence=confidence,
                features=features,
            )
            up_score = float(gating["up_score"])
            down_score = float(gating["down_score"])
            flat_score = float(gating["flat_score"])
            if up_score >= down_score and up_score >= flat_score:
                direction  = DIRECTION_UP
                confidence = up_score
            elif down_score > up_score and down_score >= flat_score:
                direction  = DIRECTION_DOWN
                confidence = down_score
            else:
                direction  = DIRECTION_FLAT
                confidence = flat_score

        # ── 레짐별 최소 신뢰도 기준 ──────────────────────────
        min_conf  = REGIME_MIN_CONFIDENCE.get(regime, 0.58)
        regime_ok = (confidence >= min_conf) and (direction != DIRECTION_FLAT)

        # ── 진입 등급 (체크리스트 통과 수는 entry_manager에서 계산) ──
        # 여기선 신뢰도 기반 사전 등급만 판정
        if not regime_ok:
            grade = "X"
        elif confidence >= 0.70:
            grade = "A"
        elif confidence >= 0.60:
            grade = "B"
        elif confidence >= min_conf:
            grade = "C"
        else:
            grade = "X"

        auto_entry = ENTRY_GRADE.get(grade, {}).get("auto", False) and regime_ok

        result = {
            "direction":  direction,
            "confidence": round(confidence, 4),
            "up_score":   round(up_score, 4),
            "down_score": round(down_score, 4),
            "flat_score": round(flat_score, 4),
            "grade":      grade,
            "auto_entry": auto_entry,
            "regime_ok":  regime_ok,
            "min_conf":   min_conf,
            "detail":     detail,
            "gating":     gating,
            "decorr":     self._decorr.get_status(),
        }

        logger.info(
            f"[Ensemble] dir={direction:+d} conf={confidence:.1%} "
            f"grade={grade} regime={regime}"
        )
        return result

    def record_trade_outcome(
        self,
        *,
        was_correct: bool,
        signals: dict,
        direction: int,
    ) -> None:
        """거래 결과를 EnsembleGater 온라인 학습에 반영."""
        self.gater.record_outcome(
            was_correct=was_correct,
            signals=signals,
            direction=direction,
        )
