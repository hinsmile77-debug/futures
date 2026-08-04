import datetime
import logging
from collections import deque
from typing import Dict, Optional

from utils.time_utils import now_kst

from config.constants import DIRECTION_FLAT
from learning.meta_confidence import MetaConfidenceLearner
from learning.meta_label_classifier import get_entry_quality_scorer
from learning.quantile_regressor import get_quantile_scorer

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
# [240차] take_floor/take_ceil/reduce_base 전면 하향 — blended_conf 실측 분포 반영
# 변경 근거 (최근 10일 데이터):
#   blended_conf 평균=0.38, P75=0.42, P90=0.46, P95=0.49, 최대=0.63
#   기존 take_floor(0.50~0.52) → 달성 가능 최대값이 P90~P95 수준이어서 사실상 차단
#   CONF_HIGH=0.37 변경으로 meta_conf가 0.0↔1.0 쌍봉 분포로 전환되면
#   좋은 신호에서 blended_C ≈ 0.60×0.37 + 0.40×0.80 = 0.54 → take_ceil=0.57 달성 가능
_GRADE_CFG: Dict[str, Dict] = {
    "A": dict(
        ens_w=0.75,  meta_w=0.25,
        take_add=0.08, take_floor=0.43, take_ceil=0.55,  # floor 0.50→0.43, ceil 0.67→0.55
        reduce_mult=0.65, reduce_base=0.27,               # base 0.33→0.27
    ),
    "B": dict(
        ens_w=0.65,  meta_w=0.35,
        take_add=0.09, take_floor=0.44, take_ceil=0.56,  # floor 0.51→0.44, ceil 0.68→0.56
        reduce_mult=0.70, reduce_base=0.28,               # base 0.34→0.28
    ),
    "C": dict(
        ens_w=0.60,  meta_w=0.40,
        take_add=0.10, take_floor=0.45, take_ceil=0.57,  # floor 0.52→0.45, ceil 0.70→0.57
        reduce_mult=0.75, reduce_base=0.30,               # base 0.36→0.30
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
        # [260704 감사 P1] meta_labels 기반 진입품질 분류기 — 섀도우 신호 전용.
        # action/size_multiplier에는 영향 없음. 학습: scripts/train_meta_label_classifier.py
        self._eq_scorer = get_entry_quality_scorer()
        # [260704 감사 P2] 분위 회귀(q10/q50/q90) — 섀도우 신호 전용.
        # 사이징/TP 거리 미반영. 학습: scripts/train_quantile_regressor.py
        self._q_scorer = get_quantile_scorer()

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
        horizon: str = "1m",                # [260704 감사 P1] entry_quality_prob 섀도우 스코어링용
        context: str = "live",              # [316차] "live"=STEP6 실거래 게이팅, "verify"=STEP2
                                             # 검증루프 카운터팩추얼 재평가 — skip 로그 태그 구분용
                                             # (SIGNAL.log grep 시 두 모집단이 섞여 집계되는 문제 방지)
    ) -> Dict:
        if now is None:
            now = now_kst()
        features = features or {}

        # [260704 감사 P1] meta_labels 기반 진입품질(수익확률) 섀도우 스코어 — 로깅 전용,
        # action/size_multiplier 결정에는 관여하지 않는다.
        entry_quality_prob = self._eq_scorer.score(horizon, features)
        # [260704 감사 P2] 분위 회귀(q10/q50/q90) 섀도우 스코어 — 로깅 전용.
        quantile_estimate = self._q_scorer.score(horizon, features)
        # [260705 검증 캠페인] 스코어링에 쓴 호라이즌을 결과에 보존 —
        # 주간 리포트가 meta_labels(ts×horizon)와 조인할 때 필요 (§3-2·§3-3).
        if quantile_estimate is not None:
            quantile_estimate = dict(quantile_estimate)
            quantile_estimate["horizon"] = horizon

        if direction == DIRECTION_FLAT:
            return {
                "action": "skip",
                "meta_confidence": 0.0,
                "entry_quality_prob": entry_quality_prob,
                "quantile_estimate": quantile_estimate,
                "scoring_horizon": horizon,   # [260705 검증 캠페인] meta_labels 조인 키
                "size_multiplier": 0.0,
                "size_multiplier_sizing": 0.0,   # [431차] 조기반환 경로도 키 일관성 유지
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
        # [MW0601 420차] 아래 두 값은 **계측 전용** — 판정에 쓰지 않는다.
        # size_multiplier는 predict_confidence 리턴 시점에 _make_result()가 raw conf로
        # 이미 확정한 값이라, 바로 아래 과소보완 floor(0.45)가 meta_conf만 올리고
        # size_multiplier는 건드리지 않는다. 즉 액션 경로와 사이즈 경로가 서로 다른
        # conf를 쓴다. joint_gate_shadow가 그 어긋남을 사후에 분리할 수 있도록
        # floor **이전** 값을 여기서 붙잡아 둔다(419차 발견 ④ 후속).
        _meta_conf_raw = meta_conf
        _size_mult_raw = learned.get("size_multiplier")

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

        # [MW0601 431차, 2026-08-05] `size_mult_sizing` 분리 — 사이징 경로 전용.
        #
        # **문제**: reduce 밴드의 `learned["size_multiplier"] or 0.5` 폴백은
        # `_make_result()`가 conf<0.5에서 size_mult=0.0(falsy)을 내보내기 때문에 발동한다.
        # 즉 "모델이 사이즈 의견을 못 냈다"를 **하드코딩 상수 0.5 축소**로 번역한다.
        # 라이브 실측(2026-07-16~08-04): reduce 밴드 1,498건 중 **714건(47.6%)이 정확히
        # 0.50** — MetaGate 축소의 절반이 모델 정보가 아니라 이 상수다.
        #
        # **왜 size_multiplier를 그대로 두는가**: 이 값은 사이징 말고 **JointGateBlock의
        # 라이브 차단 기준**(main.py `_meta_size × _tox_size < 0.50`)에도 쓰인다.
        # 최빈 조합이 정확히 `0.50 × 0.70 = 0.35`라, 폴백을 1.0으로 바꾸면
        # `1.0 × 0.70 = 0.70`이 되어 **JointGateBlock 상당수가 조용히 무력화된다**.
        # 그 게이트는 캠페인 [7]에서 PASS(누적 hyp -13.16pt, n=116 — 차단이 손실을 회피)
        # 판정을 받은 검증된 차단이므로 건드리지 않는다.
        #
        # → 따라서 **키를 나눈다**. `size_multiplier`(차단 기준, 종전 그대로) /
        #   `size_multiplier_sizing`(사이징 전용, 무정보 폴백이면 중립 1.0).
        #   소비처: main.py `_meta_size_sizing`만 후자를 읽는다.
        # 근거: dev_memory/DECISION_LOG.md 431차.
        if blended_conf >= take_thr:
            action    = "take"
            size_mult = max(0.9, min(1.25, learned["size_multiplier"]))
            size_mult_sizing = size_mult
            reason    = "meta_take"
        elif blended_conf >= reduce_thr:
            action    = "reduce"
            size_mult = max(0.35, min(0.75, learned["size_multiplier"] or 0.5))
            # 폴백이 발동했으면(모델이 사이즈 의견 없음) 사이징은 중립 — 상수로 깎지 않는다.
            size_mult_sizing = 1.0 if not _size_mult_raw else size_mult
            reason    = "meta_reduce"
        else:
            action    = "skip"
            size_mult = 0.0
            size_mult_sizing = 0.0   # skip은 차단이라 사이징 경로도 0 (동치)
            reason    = "meta_skip"
            _tag = "LIVE" if context == "live" else "VERIFY"
            _log_fn = logger.info if context == "live" else logger.debug
            _log_fn(
                "[MetaGate][%s] skip: blended=%.3f reduce_thr=%.3f take_thr=%.3f "
                "(grade=%s min_conf=%.3f ens=%.3f meta_raw=%.3f ens_w=%.2f)",
                _tag, blended_conf, reduce_thr, take_thr,
                checklist_grade, min_conf, float(confidence), meta_conf, cfg["ens_w"],
            )

        # P3: 방향 버퍼 갱신 (action 무관하게 모든 evaluate 호출 기록)
        self._direction_buf.append(direction)

        return {
            "action":              action,
            "meta_confidence":     round(blended_conf, 4),
            "entry_quality_prob":  entry_quality_prob,
            "quantile_estimate":   quantile_estimate,
            "scoring_horizon":     horizon,   # [260705 검증 캠페인] meta_labels 조인 키
            "size_multiplier":     round(size_mult, 4),
            # [MW0601 431차] 사이징 전용 배수 — **JointGateBlock은 위 size_multiplier를
            # 계속 쓴다**(차단 기준 무변경). 두 값은 reduce 밴드에서 모델이 사이즈 의견을
            # 못 냈을 때만 갈린다(그때 이 값이 1.0 = 중립). 위 분기 주석 참조.
            "size_multiplier_sizing": round(size_mult_sizing, 4),
            "reason":              reason,
            "source":              learned["model_source"],
            "meta_features":       meta_features,
            "raw_meta_confidence": round(meta_conf, 4),
            # [MW0601 420차] 계측 전용 3종 — 소비처는 joint_gate_shadow 기록뿐이고
            # 사이징·판정 어느 경로도 읽지 않는다(추가해도 라이브 동작 불변).
            # `raw_meta_confidence`는 floor **이후** 값이라(위 과소보완 블록이
            # meta_conf를 덮어씀) floor 이전 값과 이름이 겹치지 않게 _pre_floor로 둔다.
            "meta_confidence_pre_floor": round(_meta_conf_raw, 4),
            "size_multiplier_raw":       (round(float(_size_mult_raw), 4)
                                          if _size_mult_raw is not None else None),
            # reduce 밴드에서 `learned["size_multiplier"] or 0.5`가 발동했는지.
            # take/skip 밴드는 그 표현식을 타지 않으므로 정의상 False.
            "size_multiplier_fallback":  bool(action == "reduce" and not _size_mult_raw),
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
