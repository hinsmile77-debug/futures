import datetime
import logging
from collections import deque
from typing import Dict, Optional

from utils.time_utils import now_kst

from config.constants import DIRECTION_FLAT
from learning.meta_confidence import MetaConfidenceLearner

logger = logging.getLogger("SIGNAL")

# Checklist(앙상블) 등급별 MetaConf 블렌딩 파라미터
# 설계 원칙:
#   A: 구조적 조건이 강함 → 메타 불확실성에 덜 의존해도 됨 → ens 가중치 ↑, 임계 ↓
#   B: 중간
#   C/X: 현행 유지 (엄격)
#
# 검증 케이스 — grade=A, confidence=0.62, meta_conf=0.25(floor), min_conf=0.65:
#   blended(A) = 0.75×0.62 + 0.25×0.25 = 0.528  >  reduce_thr(A)=0.423  → reduce ✓
#   blended(C) = 0.60×0.62 + 0.40×0.25 = 0.472  <  reduce_thr(C)=0.488  → skip  ✗ (기존 차단)
_GRADE_CFG: Dict[str, Dict] = {
    "A": dict(
        ens_w=0.75,  meta_w=0.25,
        take_add=0.10, take_floor=0.50, take_ceil=0.67,
        reduce_mult=0.65, reduce_base=0.33,
    ),
    "B": dict(
        ens_w=0.65,  meta_w=0.35,
        take_add=0.12, take_floor=0.51, take_ceil=0.68,
        reduce_mult=0.70, reduce_base=0.34,
    ),
    "C": dict(
        ens_w=0.60,  meta_w=0.40,
        take_add=0.14, take_floor=0.52, take_ceil=0.70,
        reduce_mult=0.75, reduce_base=0.36,
    ),
}
# X: 앙상블 자체가 X 등급 → 체크리스트가 최종 차단. MetaGate는 C 기준 유지
_GRADE_CFG["X"] = _GRADE_CFG["C"]


class MetaGate:
    """
    Meta-labeling execution gate.

    The current prototype blends ensemble confidence with a context-aware
    confidence learner and converts that into take / reduce / skip.
    """

    def __init__(self):
        self.learner = MetaConfidenceLearner()
        self._collapse_warn_streak = 0  # meta_conf 과소 연속 횟수
        self._direction_buf = deque(maxlen=30)  # P3: 방향 편향 감지 (최근 30예측)

    def _bias_penalty(self, direction: int) -> float:
        """P3: 최근 30예측에서 동일 방향 비율 >70% 시 패널티 반환.
        70%→0.02, 100%→0.05 선형 스케일. 버퍼 15개 미만이면 0.
        """
        if len(self._direction_buf) < 15:
            return 0.0
        same = sum(1 for d in self._direction_buf if d == direction)
        ratio = same / len(self._direction_buf)
        if ratio <= 0.70:
            return 0.0
        return round(min((ratio - 0.70) / 0.30 * 0.05, 0.05), 4)

    def evaluate(
        self,
        *,
        direction: int,
        confidence: float,
        regime: str,
        micro_regime: str,
        features: Optional[Dict],
        now: Optional[datetime.datetime] = None,
        recent_accuracy: float = 0.5,
        min_conf: float = 0.57,
        horizon_agreement: float = 0.5,   # 6개 호라이즌 중 앙상블 방향 일치 비율
        checklist_grade: str = "C",        # 앙상블 등급(A/B/C/X) — STEP 6 grade 변수 전달
        trend_gate_active: bool = False,   # ② TrendGate ON → 편향패널티 비활성화
        time_zone: str = "",               # ③ STABLE_TREND/LUNCH_RECOVERY → reduce_thr 완화
    ) -> Dict:
        if now is None:
            now = now_kst()
        features = features or {}

        if direction == DIRECTION_FLAT:
            return {
                "action": "skip",
                "meta_confidence": 0.0,
                "size_multiplier": 0.0,
                "reason": "flat_signal",
                "source": "rule",
            }

        # mlofi_norm / cancel_add_ratio 는 EnsembleGater가 이미 처리 → 중복 패널티 방지
        meta_features = self.learner.build_meta_features(
            regime=micro_regime,
            hurst=float(features.get("hurst", 0.5) or 0.5),
            atr_ratio=float(features.get("atr_ratio", 1.0) or 1.0),
            hour_minute=now.hour * 100 + now.minute,
            recent_accuracy=float(recent_accuracy),
            signal_strength=float(confidence),
            horizon_agreement=float(horizon_agreement),
        )
        learned = self.learner.predict_confidence(meta_features)
        meta_conf = float(learned["confidence_score"])

        # meta_conf 과소 보완: meta_conf<0.20 시 rule-based 하한 + 절대 하한 0.45 적용
        # LR은 SGD 붕괴 없음 — 초기 cold-start(레짐별 30봉 미만) 또는 클래스 단조성 구간에서만 발생
        # → 절대 하한 0.45: LR 미학습 레짐에서 중립(0.5 수준) 보장, 불필요한 skip 억제
        # 이전 0.25 → 0.45: 6/11 분석에서 cold-start skip이 12시 이후 진입 전면 차단 원인으로 확인
        if meta_conf < 0.20:
            self._collapse_warn_streak += 1
            _rb_conf = max(self.learner._rule_based_confidence(meta_features), 0.45)
            if _rb_conf > meta_conf:
                logger.info(
                    "[MetaGate] meta_conf 과소 보완: raw=%.3f → floor=%.3f (연속%d회)",
                    meta_conf, _rb_conf, self._collapse_warn_streak,
                )
                meta_conf = _rb_conf
                learned["model_source"] = "규칙기반(과소보완)"
            if self._collapse_warn_streak >= 5:
                # LR은 cold reset 불필요 — 다음 30분 배치 재학습 시 자동 복구
                logger.warning(
                    "[MetaGate] meta_conf 5회 연속 과소 → 다음 배치 재학습 대기 (streak=%d)",
                    self._collapse_warn_streak,
                )
                self._collapse_warn_streak = 0
        else:
            self._collapse_warn_streak = 0

        # 등급별 블렌딩 가중치·임계값 적용
        cfg = _GRADE_CFG.get(checklist_grade, _GRADE_CFG["C"])

        blended_conf = float(confidence) * cfg["ens_w"] + meta_conf * cfg["meta_w"]

        # P3: 방향 편향 패널티 (최근 30봉 동일 방향 >70% 시 신뢰도 소폭 하향)
        # ② TrendGate active 구간(STABLE_TREND 추세 지속)에서는 편향패널티 비활성화
        #    실제 추세를 "편향"으로 오인해 매 분봉 0.005~0.006씩 blended 감소하는 문제 해소
        bias_pen = 0.0 if trend_gate_active else self._bias_penalty(direction)
        if bias_pen > 0:
            logger.info(
                "[MetaGate] 편향패널티: dir=%d buf=%d pen=%.3f blended %.3f→%.3f",
                direction, len(self._direction_buf), bias_pen,
                blended_conf, max(0.0, blended_conf - bias_pen),
            )
            blended_conf = max(0.0, blended_conf - bias_pen)

        take_thr   = max(cfg["take_floor"],
                         min(cfg["take_ceil"], min_conf + cfg["take_add"]))
        reduce_thr = max(cfg["reduce_base"], min_conf * cfg["reduce_mult"])

        # ③ STABLE_TREND/LUNCH_RECOVERY 시간대 reduce_thr 완화
        #    점심 추세 구간에서 blended=0.39~0.43이 0.427에 근소 미달하는 문제 해소
        #    0.04p 하향 → 12:33 기준 blended=0.42 > 0.387 → reduce 통과
        _trend_zones = ("STABLE_TREND", "LUNCH_RECOVERY")
        if time_zone in _trend_zones:
            _original_reduce_thr = reduce_thr
            reduce_thr = max(reduce_thr - 0.04, 0.36)
            if abs(reduce_thr - _original_reduce_thr) > 1e-4:
                logger.debug(
                    "[MetaGate] reduce_thr 완화: %.3f→%.3f (zone=%s)",
                    _original_reduce_thr, reduce_thr, time_zone,
                )

        if blended_conf >= take_thr:
            action    = "take"
            size_mult = max(0.9, min(1.25, learned["size_multiplier"]))
            reason    = "meta_take"
        elif blended_conf >= reduce_thr:
            action    = "reduce"
            size_mult = max(0.35, min(0.75, learned["size_multiplier"] or 0.5))
            reason    = "meta_reduce"
        else:
            action    = "skip"
            size_mult = 0.0
            reason    = "meta_skip"
            logger.info(
                "[MetaGate] skip: blended=%.3f reduce_thr=%.3f take_thr=%.3f "
                "(grade=%s min_conf=%.3f ens=%.3f meta_raw=%.3f ens_w=%.2f)",
                blended_conf, reduce_thr, take_thr,
                checklist_grade, min_conf, float(confidence), meta_conf, cfg["ens_w"],
            )

        # P3: 방향 버퍼 갱신 (action 무관하게 모든 evaluate 호출 기록)
        self._direction_buf.append(direction)

        return {
            "action":              action,
            "meta_confidence":     round(blended_conf, 4),
            "size_multiplier":     round(size_mult, 4),
            "reason":              reason,
            "source":              learned["model_source"],
            "meta_features":       meta_features,
            "raw_meta_confidence": round(meta_conf, 4),
            "regime":              regime,
            "micro_regime":        micro_regime,
            "checklist_grade":     checklist_grade,
        }

    def record_outcome(
        self,
        meta_features,
        correct: bool,
        confidence: float = 0.5,
    ) -> None:
        try:
            self.learner.record_outcome(meta_features, correct, confidence)
        except Exception as exc:
            logger.debug("[MetaGate] record_outcome fallback: %s", exc)
