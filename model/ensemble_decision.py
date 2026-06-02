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
    REGIME_MIN_CONFIDENCE, ENTRY_GRADE, COHERENCE_GATE_MIN,
)
from config.constants import DIRECTION_UP, DIRECTION_DOWN, DIRECTION_FLAT
from model.ensemble_gater import AdaptiveEnsembleGater
from model.directional_stuck_breaker import DirectionalStuckBreaker
from learning.calibration import PredictionCalibrator

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


class HorizonF1AdaptiveWeight:
    """
    호라이즌별 최근 F1(정확도 EMA)을 추적하여 앙상블 가중치를 동적으로 조정.

    F1 낮은 호라이즌 → 가중치 급감 (f1²에 비례).
    HorizonDecorrelator 가중치에 곱셈 적용 → 최종 가중치로 정규화.

    Args:
        decay:     EMA 감쇠 계수 (0.95 = 최근 ~20회 반영)
        f1_floor:  최소 가중치 보호 하한 (0.30 미만 → 0.30으로 고정)
        min_obs:   이 관찰 수 이상 쌓여야 동적 조정 활성 (초기 충분 데이터 보호)
    """

    def __init__(self, decay: float = 0.95, f1_floor: float = 0.30, min_obs: int = 30):
        self._f1_ema  = {h: 0.40 for h in HORIZONS}   # 초기 추정값
        self._obs     = {h: 0 for h in HORIZONS}
        self._decay   = decay
        self._floor   = f1_floor
        self._min_obs = min_obs

    def update(self, horizon: str, predicted: int, actual: int) -> None:
        """STEP 1 검증 결과 반영 — 예측 방향이 FLAT(0)이면 스킵."""
        if predicted == 0:
            return
        correct = 1.0 if predicted == actual else 0.0
        self._f1_ema[horizon] = (
            self._decay * self._f1_ema[horizon]
            + (1.0 - self._decay) * correct
        )
        self._obs[horizon] += 1

    def apply(self, base_weights: Dict[str, float]) -> Dict[str, float]:
        """base_weights(HorizonDecorrelator 출력)에 F1 배율을 곱하고 재정규화."""
        adjusted = {}
        for h, w in base_weights.items():
            if self._obs.get(h, 0) >= self._min_obs:
                f1 = max(self._floor, self._f1_ema.get(h, 0.40))
                adjusted[h] = w * (f1 ** 2)
            else:
                adjusted[h] = w   # 관찰 부족 시 원래 가중치 유지
        total = sum(adjusted.values())
        if total <= 0:
            return dict(base_weights)
        return {h: v / total for h, v in adjusted.items()}

    def get_f1_status(self) -> Dict[str, float]:
        return {h: round(self._f1_ema[h], 3) for h in HORIZONS}


class EnsembleDecision:
    """앙상블 신호 생성 + 진입 등급 판정"""

    def __init__(self):
        self.gater      = AdaptiveEnsembleGater()
        self._decorr    = HorizonDecorrelator()
        self._f1_weight = HorizonF1AdaptiveWeight()
        self._stuck     = DirectionalStuckBreaker()
        self.calibrator = None   # main.py에서 horizon_calibrator 주입 (3m 분포 기반)
        # 앙상블 전용 보정기: 앙상블 conf 분포를 직접 학습 (3m 분포 미스매치 해소)
        # 100건 이상 누적 전: self.calibrator(3m) fallback
        self.ensemble_calibrator = PredictionCalibrator(method="platt")

    def compute(
        self,
        horizon_proba: Dict[str, Dict],
        regime: str = "NEUTRAL",
        features: Optional[Dict[str, float]] = None,
        adaptive_gating: bool = True,
        acc30m: float = 0.5,
        trend_gate_up_active: bool = False,
        trend_gate_dn_active: bool = False,
        time_zone: str = "",
    ) -> Dict:
        """
        Args:
            horizon_proba: MultiHorizonModel.predict_proba() 결과
            regime:        현재 매크로 레짐

        Returns:
            {direction, confidence, up_score, down_score,
             grade, auto_entry, regime_ok, detail}
        """
        # ── 가중합 (상관관계 역수 × F1 적응형 가중치 적용) ──────────
        # HorizonDecorrelator: 이중 가중(double-counting) 완화.
        # HorizonF1AdaptiveWeight: F1 낮은 호라이즌 자동 억제 (f1² 비례).
        cur_weights = self._f1_weight.apply(self._decorr.weights)
        self._decorr.push(horizon_proba)   # 이번 예측을 버퍼에 기록

        # CLOSE_VOLATILE(14:00~15:00) 구간: 단기(1m/3m/5m) FL편향 완화
        # 오후 저변동성 구간에서 단기 호라이즌이 FL에 과대 편향되어 중기 DN 신호를 희석.
        # 단기 가중치를 0.6× 축소 후 재정규화하여 10m/15m의 기여도를 상대적으로 확대.
        if time_zone == "CLOSE_VOLATILE":
            _SHORT = {"1m", "3m", "5m"}
            cur_weights = {
                h: (w * 0.6 if h in _SHORT else w)
                for h, w in cur_weights.items()
            }
            _total = sum(cur_weights.values())
            if _total > 0:
                cur_weights = {h: w / _total for h, w in cur_weights.items()}
            logger.debug(
                "[Ensemble] CLOSE_VOLATILE 단기 0.6× | %s",
                {k: round(v, 3) for k, v in cur_weights.items()},
            )

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

        # ── 방향 고착 감쇠 ───────────────────────────────────
        # 발동: NEUTRAL + 동방향 8회+ + acc30m < 38%
        # 억제: TrendGate가 같은 방향 active → 실제 추세 인정
        up_score, down_score, flat_score, _stuck_streak, _stuck_active = \
            self._stuck.update_and_apply(
                direction, up_score, down_score, flat_score,
                regime=regime,
                acc30m=acc30m,
                trend_gate_up_active=trend_gate_up_active,
                trend_gate_dn_active=trend_gate_dn_active,
            )
        # 감쇠 후 방향·신뢰도 재결정
        if up_score >= down_score and up_score >= flat_score:
            direction  = DIRECTION_UP
            confidence = up_score
        elif down_score > up_score and down_score >= flat_score:
            direction  = DIRECTION_DOWN
            confidence = down_score
        else:
            direction  = DIRECTION_FLAT
            confidence = flat_score

        # ── 호라이즌 합의도 패널티 (불합의 노이즈 필터) ───────────
        # 6개 중 2개 이하 합의: 방향 신호가 노이즈일 가능성 높음 → 진입 억제
        # 보너스 없음: 전 호라이즌 합의도 높아도 편향이면 오히려 7연속 실패 (이상점3 사례)
        if direction != DIRECTION_FLAT:
            _n_agree = sum(
                1 for h_res in horizon_proba.values()
                if h_res.get("direction") == direction
            )
            if _n_agree <= 2:
                confidence = round(confidence * 0.92, 6)
                if direction == DIRECTION_UP:
                    up_score = confidence
                elif direction == DIRECTION_DOWN:
                    down_score = confidence
                logger.debug(
                    "[Ensemble] 합의도 패널티 n_agree=%d/6 conf→%.3f",
                    _n_agree, confidence,
                )

        # ── 코히어런스 게이트 (P3b) ──────────────────────────────
        # FLAT 제외 계산: FLAT 예측 호라이즌은 방향성 없으므로 코히어런스에서 제외
        # (FLAT 포함 시 오늘처럼 5m/10m/15m FLAT 편향 → DN 3/6=0.50 → 과잉 차단)
        _coherence_blocked = False
        if direction != DIRECTION_FLAT:
            # FLAT 예측 호라이즌 제외: 방향성 있는 호라이즌만 대상
            _active_h = [
                h for h in horizon_proba
                if horizon_proba[h] and horizon_proba[h].get("direction") != DIRECTION_FLAT
            ]
            _n_active = len(_active_h)
            if _n_active > 0:
                _n_coherent = sum(
                    1 for h in _active_h
                    if horizon_proba[h].get("direction") == direction
                )
                _coherence_score = _n_coherent / _n_active
                if _coherence_score < COHERENCE_GATE_MIN:
                    _coherence_blocked = True
                    logger.info(
                        "[Ensemble] CoherenceGate 차단 score=%.2f (%d/%d비FLAT) dir=%+d",
                        _coherence_score, _n_coherent, _n_active, direction,
                    )

        # ── Platt 보정 (앙상블 전용 보정기 우선, 미학습 시 3m fallback) ────
        # ensemble_calibrator: 앙상블 conf 분포를 직접 학습 (3m 분포 미스매치 해소)
        # 100건 미만: 3m 보정기 fallback (분포 차이 일부 허용)
        _confidence_raw = confidence
        if direction != DIRECTION_FLAT:
            if self.ensemble_calibrator.is_fitted:
                _cal = self.ensemble_calibrator.calibrate(confidence)
            elif self.calibrator is not None:
                _cal = self.calibrator.calibrate("3m", confidence)
            else:
                _cal = confidence
            confidence = min(max(float(_cal), 0.0), 0.85)
            if direction == DIRECTION_UP:
                up_score = confidence
            elif direction == DIRECTION_DOWN:
                down_score = confidence

        # ── 레짐별 최소 신뢰도 기준 ──────────────────────────
        min_conf  = REGIME_MIN_CONFIDENCE.get(regime, 0.58)
        regime_ok = (confidence >= min_conf) and (direction != DIRECTION_FLAT)

        # ── 진입 등급 (체크리스트 통과 수는 entry_manager에서 계산) ──
        # 코히어런스 게이트 차단 시 최우선 X
        if _coherence_blocked:
            grade = "X"
        elif not regime_ok:
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
            "direction":          direction,
            "confidence":         round(confidence, 4),
            "confidence_raw":     round(_confidence_raw, 4),
            "up_score":           round(up_score, 4),
            "down_score":         round(down_score, 4),
            "flat_score":         round(flat_score, 4),
            "grade":              grade,
            "auto_entry":         auto_entry,
            "regime_ok":          regime_ok,
            "min_conf":           min_conf,
            "coherence_blocked":  _coherence_blocked,
            "detail":             detail,
            "gating":             gating,
            "decorr":             self._decorr.get_status(),
            "stuck":              self._stuck.status_dict(),
            "f1_adaptive":        self._f1_weight.get_f1_status(),
        }

        logger.info(
            f"[Ensemble] dir={direction:+d} conf={confidence:.1%} "
            f"grade={grade} regime={regime}"
        )
        return result

    def record_ensemble_outcome(self, raw_conf: float, correct: bool) -> None:
        """앙상블 보정기에 결과 누적 — STEP 1 검증 시 main.py에서 호출."""
        self.ensemble_calibrator.record(raw_conf, correct)

    def record_horizon_verification(
        self, horizon: str, predicted: int, actual: int
    ) -> None:
        """호라이즌별 F1 EMA 업데이트 — STEP 1 검증 시 main.py에서 호출."""
        self._f1_weight.update(horizon, predicted, actual)

    def reset_daily(self):
        self._stuck.reset_daily()

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
