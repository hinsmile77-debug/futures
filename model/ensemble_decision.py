# model/ensemble_decision.py — 앙상블 가중합 + 진입 등급 판정
"""
6개 호라이즌 예측을 가중합하여 최종 방향·신뢰도·진입 등급을 결정합니다.

앙상블 가중치 (설계 명세 4-3, 최초 기준값 — 이후 실측 기반 재조정 다수):
  기본:  1분 10% / 3분 15% / 5분 20% / 10분 20% / 15분 20% / 30분 15%
  상관관계 역수 조정(HorizonDecorrelator):
    - 30분 롤링 창에서 호라이즌 간 실측 상관계수를 추적
    - 상관이 높은 호라이즌의 가중치를 자동으로 낮춰 이중 가중을 완화
    - 데이터 부족 시 ENSEMBLE_WEIGHTS_CORR_ADJ 정적 추정치로 fallback

30m 퇴역(296차, 2026-07-06): 앙상블 가중합·CascadeCoherence·CoherenceGate 전부에서
영구 제외. predict_proba·GBM/RF 학습·CB③ 모니터링은 계속 유지(연구/재평가용).

1m 퇴역(331차 후속2, 2026-07-14): conf-층화 재검정(311차 후속5~6)에서 1m 방향적중률
47.75%(z=-2.82, 역스킬 확정) + 331차 피처셋 개편 후 purged CV로도 무변화(-0.52%p) 확인,
30m과 동일하게 앙상블 가중합에서 영구 제외. CoherenceGate 분모 제외는 311차가 이미
선행 조치했음(위 30m과 같은 취지, 아래 _bias_overrides 참조). predict_proba·GBM/RF
학습은 계속 유지(연구/재평가용, SGD 블렌딩은 250차부터 이미 제외 — SGD_BLEND_DISABLED_HORIZONS).
"""
import logging
import math
from collections import deque
from typing import Dict, Optional, Tuple

from config.settings import (
    ENSEMBLE_WEIGHTS, ENSEMBLE_WEIGHTS_CORR_ADJ, HORIZONS,
    REGIME_MIN_CONFIDENCE, ENTRY_GRADE, COHERENCE_GATE_MIN,
    CONF_STUCK_BOOST_ENABLED, CONF_STUCK_BOOST_SOURCE, CONF_STUCK_BOOST_TARGET,
    CONF_STUCK_BOOST_MIN_STREAK, CONF_STUCK_BOOST_TRANSFER_RATIO,
    CONF_STUCK_BOOST_TARGET_MIN_ACC,
    ENTRY_HORIZON_LOW_BLOCK, ENTRY_HORIZON_B1, ENTRY_HORIZON_B2,
    WEIGHT_COLLAPSE_HONEST_MODE,
    ENS_CONF_FLOOR_FOR_AUTO,   # [403차 종합 P0-2b] 하한↔보정기 정합성 경보용
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
        # 호라이즌별 마지막 push 틱 (-1 = 미사용)
        # _recompute 에서 "최근 UPDATE_EVERY 틱 내에 실제 push된 것"만 available로 간주
        self._last_push_tick: Dict[str, int] = {h: -1 for h in self._horizons}

    def push(self, horizon_proba: Dict[str, Dict]) -> None:
        """매분 예측 결과를 버퍼에 추가하고 필요 시 가중치를 재계산한다."""
        for h in self._horizons:
            if h not in horizon_proba:
                # 체크박스 OFF 등 비활성 호라이즌 건너뜀
                continue
            prev_tick = self._last_push_tick[h]
            if prev_tick >= 0 and (self._ticks - prev_tick) >= self.UPDATE_EVERY:
                # UPDATE_EVERY(15분) 이상 공백 후 재활성 → 구 데이터로 상관관계 왜곡 방지
                self._buf[h].clear()
                logger.debug("[Decorr] %s 버퍼 클리어 (비활성 %d틱 후 복귀)", h, self._ticks - prev_tick)
            p = horizon_proba[h].get("up", 0.5)
            self._buf[h].append(float(p))
            self._last_push_tick[h] = self._ticks

        self._ticks += 1
        if self._ticks % self.UPDATE_EVERY == 0:
            self._recompute()

    def _recompute(self) -> None:
        # 최근 UPDATE_EVERY 틱 내에 실제 push된 호라이즌만 대상
        # push 공백이 UPDATE_EVERY 이상이면 구 버퍼 데이터 → 시간 불일치 상관관계 배제
        _recent = self._ticks - self.UPDATE_EVERY
        available = [
            h for h in self._horizons
            if len(self._buf[h]) >= self.MIN_SAMPLES
            and self._last_push_tick[h] >= _recent
        ]
        if len(available) < 2:
            return
        min_len = min(len(self._buf[h]) for h in available)

        # 각 호라이즌의 다른 호라이즌과의 평균 |ρ|
        avg_abs_rho: Dict[str, float] = {}
        for h in available:
            rhos = []
            for other in available:
                if other == h:
                    continue
                rho = self._pearson(
                    list(self._buf[h])[-min_len:],
                    list(self._buf[other])[-min_len:],
                )
                rhos.append(abs(rho))
            avg_abs_rho[h] = sum(rhos) / len(rhos) if rhos else 0.5

        # w_adj[h] = (1 - avg_|ρ|[h]) / 정규화 — available 호라이즌만 갱신
        # 비활성 호라이즌의 self._weights는 이전 값 유지
        # (compute() 에서 horizon_proba 부재 시 if not res: continue 로 자동 스킵)
        raw   = {h: max(1.0 - avg_abs_rho[h], 0.05) for h in available}
        total = sum(raw.values())
        if total <= 0:
            return

        for h in available:
            self._weights[h] = raw[h] / total
        logger.debug(
            "[Decorr] 가중치 갱신 (샘플=%d, 활성=%d/%d) | %s",
            min_len, len(available), len(self._horizons),
            {k: round(v, 3) for k, v in self._weights.items() if v > 0},
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
        populated = [len(self._buf[h]) for h in self._horizons if len(self._buf[h]) > 0]
        min_len = min(populated) if populated else 0
        return {
            "samples": min_len,
            "adaptive": len(populated) >= 2 and min_len >= self.MIN_SAMPLES,
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
        """STEP 1 검증 결과 반영 — FL 포함 전 예측 방향을 EMA 업데이트."""
        # 수정: 기존에 predicted==FL(0)이면 스킵했으나, FL만 반복 예측하는 호라이즌의
        # obs가 누적되지 않아 min_obs 미달 → 동적 억제가 영구 비활성되는 버그 수정.
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


# ── Phase 1 유틸리티 함수 ────────────────────────────────────────────────────

def compute_cascade_coherence(horizon_proba):
    # type: (Dict[str, Dict]) -> float
    """15m→…→3m 방향이 흘러내려오는 정렬도를 반환.

    FL 호라이즌 제외 후 방향성 있는 호라이즌만으로 정렬 비율 계산.
    (FL 끼임으로 인한 연속 break 방지 — 오늘 오전처럼 15m/10m=DN, 5m/3m=FL 케이스)
    30m은 퇴역(296차, 2026-07-06)으로 cascade에서 제외 — 구조적 저성능(EOD full_cv
    acc=0.3052, 랜덤 이하) 호라이즌의 노이즈 방향이 정렬도를 깨 정상 진입을 차단하는
    부작용 방지(CoherenceGate와 동일 사유).
    [311차] 1m도 동일 사유로 제외 — 무스킬(방향예측 정확도 45~51%, 기준선과 구분불가)
    호라이즌을 정렬도의 기준점(target)으로 삼고 있었던 게 더 심각한 문제. 3m을 새 기준점으로 사용.
    반환: 0.0(완전 불일치) ~ 1.0(완전 정렬)
    """
    cascade = ["15m", "10m", "5m", "3m"]
    dirs = [
        (horizon_proba.get(h) or {}).get("direction", DIRECTION_FLAT)
        for h in cascade
    ]
    target = dirs[-1]  # 3m 방향 기준
    if target == DIRECTION_FLAT:
        return 0.5    # FLAT → 중립
    directional = [d for d in dirs if d != DIRECTION_FLAT]
    if not directional:
        return 0.5
    aligned = sum(1 for d in directional if d == target)
    return aligned / len(directional)


# [374차/375차] entry_horizon 경계값(ENTRY_HORIZON_LOW_BLOCK/B1/B2)은
# config/settings.py로 이전됨 — HORIZON_THRESHOLDS_BASE 옆 참조(재보정 이력 주석 포함).


def select_entry_horizon(atr, threshold_1m):
    # type: (float, float) -> Optional[str]
    """ATR 레짐 기반 최적 진입 호라이즌 선택.

    기존 threshold_feasibility 피처(atr / threshold_1m) 역활용.
    Returns: "1m" / "3m" / "5m" / None(저변동성 차단)

    라이브 미검증 — dev_memory DECISION_LOG 374차 항목 참조.
    """
    feasibility = atr / (threshold_1m + 1e-9)
    if feasibility < ENTRY_HORIZON_LOW_BLOCK:
        return None       # 저변동성 → 진입 차단
    elif feasibility < ENTRY_HORIZON_B1:
        return "1m"       # 적정 변동성
    elif feasibility < ENTRY_HORIZON_B2:
        return "3m"       # 중간 변동성
    else:
        return "5m"       # 고변동성


class EnsembleDecision:
    """앙상블 신호 생성 + 진입 등급 판정"""

    # 호라이즌 상수 출력 감지 임계값
    # 5분간 direction 동일 + confidence max-min < 0.5%p → GBM 붕괴로 판정
    _CONST_OUT_N     = 5      # 판정 최소 관찰 수 (분)
    _CONST_OUT_RANGE = 0.005  # confidence max-min 허용 범위

    # TrendGate 추세 부스트 (P0-A): 원웨이 추세 감지 시 방향 점수 직접 보정
    # 문제: TrendGate가 min_conf만 낮춰줘서 dir=FLAT이면 완전 무력.
    # 해결: 앙상블 점수 계산 직후 up/down_score를 올려 flat_score를 이기게 함.
    # 6/2 13:55 실증 케이스: up=0.36 → 0.43 > flat=0.42 → dir=+1 확정.
    _TREND_UP_BOOST    = 0.07   # UP streak active 시 up_score 보정량
    _TREND_DN_BOOST    = 0.07   # DN streak active 시 down_score 보정량
    _TREND_SCORE_CAP   = 0.58   # boost 후 점수 상한 (과신 방지 — 0.58 이상은 GBM 실제값 우선)

    # FlatCap (P0-B): 추세 active 중 flat_score 과지배 차단
    # 14:10 케이스: 15m+30m 가중치 합 0.79인데 FLAT/DOWN → flat 0.57 우세
    # → flat을 0.38로 cap 후 재정규화하여 UP/DN 상대 경쟁력 확보.
    _FLAT_CAP_ON_TREND = 0.38   # 추세 중 flat_score 상한

    # ── Grade A 롤링 정확도 가드 ─────────────────────────────────────────────
    # conf ≥ 0.65 예측의 최근 N건 실적이 임계값 미달이면 Grade A를 B로 강등.
    # 근거: conf 0.7+ 실측 정확도 ~29-31% — conf 0.4대 정확도(33%)보다 낮은 역전 현상.
    _HC_GUARD_WINDOW   = 50    # 최근 N건 고신뢰도 예측
    _HC_GUARD_MIN_N    = 20    # 이 수 이상 쌓여야 가드 활성 (초기 cold start 보호)
    _HC_GUARD_CONF_THR = 0.65  # 고신뢰도 판단 기준
    _HC_GUARD_ACC_THR  = 0.42  # 이 정확도 미달 시 Grade A → B 강등

    def __init__(self):
        self.gater      = AdaptiveEnsembleGater()
        self._decorr    = HorizonDecorrelator()
        self._f1_weight = HorizonF1AdaptiveWeight()
        self._stuck     = DirectionalStuckBreaker()
        self.calibrator = None   # main.py에서 horizon_calibrator 주입 (3m 분포 기반)
        # 앙상블 전용 보정기: 앙상블 conf 분포를 직접 학습 (3m 분포 미스매치 해소)
        # 100건 이상 누적 전: self.calibrator(3m) fallback
        self.ensemble_calibrator = PredictionCalibrator(method="platt")
        # 호라이즌 상수 출력 감지 — (direction, confidence) 이력 + 현재 stuck 상태
        self._hz_conf_hist: Dict[str, deque] = {
            h: deque(maxlen=self._CONST_OUT_N) for h in HORIZONS
        }
        self._hz_stuck: Dict[str, bool] = {h: False for h in HORIZONS}
        # ShortHorizonOverride: dir=FLAT 연속 카운터
        self._flat_streak: int = 0
        # FL 조기 감쇠: FL 확률 70%+ 연속 분 카운터 (Phase 1 부록 C-1)
        self._fl_streak: Dict[str, int] = {h: 0 for h in HORIZONS}
        # P4: display용 EMA smoothing (span=20, 실거래 로직 무영향)
        self._conf_ema: Optional[float] = None
        self._CONF_EMA_ALPHA: float = 2.0 / (20 + 1)  # span=20
        # Grade A 롤링 정확도 가드: conf ≥ _HC_GUARD_CONF_THR 예측 결과 버퍼
        self._hc_buf: deque = deque(maxlen=self._HC_GUARD_WINDOW)
        self._hc_grade_a_blocked: bool = False  # 현재 차단 상태 (로그용)
        # [conf(ema) 딥다이브, 개선안1] 실질 가중합 0 붕괴 연속 카운터 — WeightCollapse 계측용
        self._weight_collapse_streak: int = 0
        # [403차 종합 P0-2b] 진입 하한 ↔ 보정기 출력범위 정합성 경보 상태.
        # 마지막으로 경보한 (도달가능여부) 를 기억해 상태가 바뀔 때만 로그를 남긴다.
        self._conf_floor_reachable: Optional[bool] = None

    def _check_conf_floor_consistency(
        self, min_conf: float, zone_allows_entry: bool = True
    ) -> None:
        """[403차 종합 P0-2b] 자동진입 하한이 보정기 출력범위 안에 있는지 점검.

        2026-07-30 두 PC 공통 사고: 보정기가 축퇴해 출력 상한이 0.3012~0.3052로
        내려앉았는데 ENS_CONF_FLOOR_FOR_AUTO는 정적 0.33 그대로였다. 두 값이 서로
        다른 규칙으로 움직이는데(하나는 상수, 하나는 학습결과) 어긋남을 감지하는
        계측이 없어, "어떤 신호도 하한을 넘을 수 없는" 상태가 하루 종일 조용히
        유지됐다. min_conf(동적)까지 셋을 함께 본다.

        판정만 로그로 남긴다 — 임계값을 자동으로 조정하지 않는다(§9 사전등록 원칙).

        [404차 후속4 / P1-E] zone_allows_entry=False 구간은 판정 자체를 건너뛴다.
        PRE_MARKET·EXIT_ONLY·OTHER(점심 공백 11:50~13:00 등)는 min_confidence가
        0.65~1.01로 설정된 **설계된 진입 블랙아웃**이라, 보정기 출력상한(≈0.30~0.37)이
        그 값을 못 넘는 것이 정상이다. 이를 경보하면 "하한↔보정기 스케일 불일치"라는
        이 가드의 진짜 표적과 무관한 오탐이 된다 — 2026-07-31 11:50:57 WARNING이
        정확히 그 사례이며, 403차 NEXT_TODO는 이를 "P1-8 착수 신호"로 잘못 규정했다.
        상태(_conf_floor_reachable)도 갱신하지 않으므로, 블랙아웃 구간 진입/이탈만으로
        생기던 짝지어진 오탐 WARNING·복구 INFO가 둘 다 사라진다.

        범위 주: 14:50 신규진입 컷오프(utils.time_utils.is_new_entry_allowed)는
        여기에 반영하지 않는다 — CLOSE_VOLATILE의 min_conf(0.62)는 실제 진입 임계라
        그 구간의 도달 불가는 진짜 결함 신호다(§9 사전등록 범위 = 시간대 존 축 한정).
        """
        try:
            if not zone_allows_entry:
                logger.debug(
                    "[ConfFloorGuard] 진입 금지 시간대 — 정합성 판정 스킵 (min_conf=%.3f)",
                    float(min_conf or 0.0),
                )
                return
            _cal = self.ensemble_calibrator
            # [461차 P-B] 실효 진입 하한 주입 — 진입 허용 시간대의 min_conf만 넘긴다.
            # (블랙아웃 구간 min_conf는 진입 임계가 아니므로 위 early-return이 막는다.)
            # 미fit 상태에서도 갱신해야 다음 fit이 최신 하한으로 판정할 수 있다.
            _cal.update_effective_floor(min_conf)
            if not _cal.is_fitted:
                return          # 미fit이면 raw가 그대로 나가므로 도달 가능
            _out_max = _cal.output_max
            if _out_max is None:
                return
            _need = max(float(ENS_CONF_FLOOR_FOR_AUTO), float(min_conf or 0.0))
            _reachable = _out_max >= _need
            if _reachable == self._conf_floor_reachable:
                return          # 상태 무변화 — 로그 억제
            self._conf_floor_reachable = _reachable
            if not _reachable:
                logger.warning(
                    "[ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 %.4f < "
                    "필요 %.4f (conf_floor=%.3f, min_conf=%.3f, span=%s). "
                    "이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.",
                    _out_max, _need, float(ENS_CONF_FLOOR_FOR_AUTO), float(min_conf or 0.0),
                    ("%.4f" % _cal.output_span) if _cal.output_span is not None else "N/A",
                )
            else:
                logger.info(
                    "[ConfFloorGuard] 하한 도달 가능 복구 — 출력상한 %.4f ≥ 필요 %.4f",
                    _out_max, _need,
                )
        except Exception as _cfg_e:
            logger.debug("[ConfFloorGuard] 점검 실패 (무해): %s", _cfg_e)

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
        active_horizons: Optional[list] = None,
        zone_mc: float = 0.60,
        bias_override_horizons: Optional[set] = None,
        conf_stuck_streak: Optional[Dict[str, int]] = None,
        target_recent_acc: Optional[float] = None,
        zone_allows_entry: bool = True,
    ) -> Dict:
        """
        Args:
            horizon_proba: MultiHorizonModel.predict_proba() 결과
            regime:        현재 매크로 레짐

        Returns:
            {direction, confidence, up_score, down_score,
             grade, auto_entry, regime_ok, detail}
        """
        # [P0] 빈 예측 입력 차단 — horizon_proba={} 시 flat_score=1.0→conf=100% 방지
        # 근본 원인(predict_proba continue 버그)이 수정됐더라도 다른 경로로
        # horizon_proba={}이 전달될 수 있으므로 진입부에서 즉시 차단한다.
        if not horizon_proba:
            logger.warning("[Ensemble] horizon_proba={} — confidence=0.0 반환 (P0 방어)")
            return {
                "direction": DIRECTION_FLAT,
                "confidence": 0.0,
                "confidence_raw": 0.0,
                "up_score": 0.0,
                "down_score": 0.0,
                "flat_score": 0.0,
                "grade": "X",
                "auto_entry": False,
                "regime_ok": False,
                "min_conf": zone_mc,
                "coherence_blocked": False,
                "cascade_blocked": False,
                "trend_boost_applied": False,
                "detail": {},
                "gating": {},
                "decorr": {},
                "stuck": {},
                "f1_adaptive": {},
                "const_output_horizons": [],
                "active_horizons_blocked": False,
                "30m_filter_blocked": False,
                "conf_stuck_boost_applied": False,
            }

        # ── 가중합 (상관관계 역수 × F1 적응형 가중치 적용) ──────────
        # HorizonDecorrelator: 이중 가중(double-counting) 완화.
        # HorizonF1AdaptiveWeight: F1 낮은 호라이즌 자동 억제 (f1² 비례).
        cur_weights = self._f1_weight.apply(self._decorr.weights)
        self._decorr.push(horizon_proba)   # 이번 예측을 버퍼에 기록

        # 30m 퇴역(296차) — 가중합에서 영구 제외(과거 Q3 "필터 전용" 단계를 지나 완전 퇴역).
        # Decorrelator·F1 추적은 위 push()에서 이미 반영되므로 순서 중요
        _proba_30m = horizon_proba.get("30m")
        _30m_filter_blocked = False
        if _proba_30m is not None and "30m" in cur_weights:
            cur_weights["30m"] = 0.0
            _tw_no30 = sum(cur_weights.values())
            if _tw_no30 > 1e-9:
                cur_weights = {h: w / _tw_no30 for h, w in cur_weights.items()}
            logger.debug(
                "[Ensemble] 30m 필터 전용: dir=%+d conf=%.1f%% (앙상블 가중합 제외)",
                _proba_30m.get("direction", 0),
                _proba_30m.get("confidence", 0.0) * 100,
            )

        # 1m 퇴역(331차 후속2, 2026-07-14) — 30m과 동일 패턴. ENSEMBLE_WEIGHTS를 이미
        # 0.0으로 설정했지만, Decorrelator·F1AdaptiveWeight가 매분 실측 상관계수·F1로
        # 가중치를 동적 재계산하므로(위 self._f1_weight.apply/self._decorr.weights) 설정값
        # 0.0이 그대로 유지된다는 보장이 없다 — 30m 때와 동일한 안전망으로 명시적 강제.
        _proba_1m = horizon_proba.get("1m")
        if _proba_1m is not None and "1m" in cur_weights:
            cur_weights["1m"] = 0.0
            _tw_no1m = sum(cur_weights.values())
            if _tw_no1m > 1e-9:
                cur_weights = {h: w / _tw_no1m for h, w in cur_weights.items()}
            logger.debug(
                "[Ensemble] 1m 필터 전용: dir=%+d conf=%.1f%% (앙상블 가중합 제외)",
                _proba_1m.get("direction", 0),
                _proba_1m.get("confidence", 0.0) * 100,
            )

        # ── 시간대 정책: 비활성 호라이즌 가중치 0 ────────────────────
        # HORIZON_TIME_POLICY 기반 active_horizons가 주어진 경우 적용
        if active_horizons is not None:
            _active_set = set(active_horizons)
            for _h in list(cur_weights.keys()):
                if _h not in _active_set:
                    cur_weights[_h] = 0.0
            _tw = sum(cur_weights.values())
            if _tw <= 1e-9:
                # 활성 호라이즌이 없는 cold-start 구간 → FLAT 즉시 반환
                logger.debug(
                    "[Ensemble] active_horizons=%s 전체 차단 → FLAT 반환", active_horizons
                )
                return {
                    "direction": DIRECTION_FLAT,
                    "confidence": 0.0,
                    "confidence_raw": 0.0,
                    "up_score": 0.0,
                    "down_score": 0.0,
                    "flat_score": 0.0,
                    "grade": "X",
                    "auto_entry": False,
                    "regime_ok": False,
                    "min_conf": zone_mc,
                    "coherence_blocked": False,
                    "cascade_blocked": False,
                    "trend_boost_applied": False,
                    "detail": {},
                    "gating": {},
                    "decorr": {},
                    "stuck": {},
                    "f1_adaptive": {},
                    "const_output_horizons": [],
                    "active_horizons_blocked": True,
                    "30m_filter_blocked": False,
                    "conf_stuck_boost_applied": False,
                }
            cur_weights = {h: w / _tw for h, w in cur_weights.items()}
            logger.debug(
                "[Ensemble] 시간대 정책 active=%s | weights=%s",
                active_horizons,
                {k: round(v, 3) for k, v in cur_weights.items() if v > 0},
            )

        # ── [353차] 확신도 고착 임시 부스트 (P2-b 옵션 c) ────────────────
        # 5m GBM은 5분마다만 갱신되는 구조라(bar_age), SGD 온라인블렌드가 그
        # 공백을 못 메우면(저신뢰 예측은 학습 게이트로 걸러져 SGD 자체가
        # 5m에서 학습 기회가 희소함) 같은 확신도가 3~4분씩 얼어붙는다
        # (2026-07-16 정기점검 P2 딥다이브 — [CONF⚠] 로그 기준 하루 112건
        # 전부 5m에서만 실측). SGD 학습 게이트(0.52)를 건드리면 저신뢰
        # 레이블이 학습에 섞이는 부작용(P2-D가 막으려던 것)이 재발할 수
        # 있어, 그 대신 "이번 순간만" 정체된 호라이즌의 가중치 일부를 항상
        # 정상 갱신되는 호라이즌으로 옮기는 국소·가역적 개입을 택했다 —
        # 학습 파이프라인은 전혀 건드리지 않으며, 소스가 갱신되는 즉시(다음
        # 분) 자동으로 정상 가중치로 복귀한다. 타깃의 최근 정확도가 낮으면
        # (표본 부족으로 판단 불가한 경우는 허용) 부스트를 억제해 "정체된
        # 신호를 다른 노이즈로 대체"하는 상황을 방지한다.
        _stuck_boost_applied = False
        if (
            CONF_STUCK_BOOST_ENABLED
            and conf_stuck_streak
            and conf_stuck_streak.get(CONF_STUCK_BOOST_SOURCE, 0) >= CONF_STUCK_BOOST_MIN_STREAK
            and cur_weights.get(CONF_STUCK_BOOST_SOURCE, 0.0) > 0.0
            and cur_weights.get(CONF_STUCK_BOOST_TARGET, 0.0) > 0.0
            and (
                target_recent_acc is None
                or target_recent_acc >= CONF_STUCK_BOOST_TARGET_MIN_ACC
            )
        ):
            _boost_amt = cur_weights[CONF_STUCK_BOOST_SOURCE] * CONF_STUCK_BOOST_TRANSFER_RATIO
            cur_weights[CONF_STUCK_BOOST_SOURCE] -= _boost_amt
            cur_weights[CONF_STUCK_BOOST_TARGET]  += _boost_amt
            _stuck_boost_applied = True
            logger.debug(
                "[Ensemble] ConfStuckBoost %s(%d분 고착) → %s +%.3f "
                "(target_acc=%s)",
                CONF_STUCK_BOOST_SOURCE,
                conf_stuck_streak.get(CONF_STUCK_BOOST_SOURCE, 0),
                CONF_STUCK_BOOST_TARGET,
                _boost_amt,
                f"{target_recent_acc:.1%}" if target_recent_acc is not None else "N/A(허용)",
            )

        # ── 방향 편향 조기 감쇠: 단일 방향 50%+ 10분 → weight×0.2 ─
        # 127차: FL 전용 → UP/DN/FL 공통 (30m DN 100% 고착 사례 대응)
        # 수정: 70% → 50% — GBM이 FL을 50~55%로 반복 예측할 때 70% 임계로는
        # streak이 전혀 쌓이지 않아 감쇠 미발동. 3m FL 100% 고착 사례(14:28~) 대응.
        _dir_damped = set()
        for _h in list(cur_weights.keys()):
            _hp    = horizon_proba.get(_h) or {}
            _fl_p  = float(_hp.get("flat", 0.0))
            _up_p  = float(_hp.get("up",   0.0))
            _dn_p  = float(_hp.get("down", 0.0))
            _max_p = max(_fl_p, _up_p, _dn_p)
            # FL은 0.43 이상이면 streak 누적 (UP/DN은 기존 0.50 유지)
            # 근거: 3m/5m GBM raw FL≈0.47 → 0.50 임계로는 streak 미누적 → 감쇠 미발동
            #       FL 편향의 임계를 낮춰 10분 지속 시 앙상블 가중치 0.2× 적용
            _fl_dominant = _fl_p == _max_p and _fl_p > 0.43
            _dir_dominant = _fl_p != _max_p and _max_p > 0.50
            if _fl_dominant or _dir_dominant:
                self._fl_streak[_h] = self._fl_streak.get(_h, 0) + 1
            else:
                self._fl_streak[_h] = 0
            _streak = self._fl_streak.get(_h, 0)
            if _streak >= 10 and cur_weights.get(_h, 0) > 0:
                _bname = ("FL" if _fl_p == _max_p else
                          ("UP" if _up_p == _max_p else "DN"))
                cur_weights[_h] *= 0.2
                _dir_damped.add(_h)
                logger.debug(
                    "[EarlyDirDamp] %s %s=%.0f%% %dmin → weight×0.2",
                    _h, _bname, _max_p * 100, _streak,
                )
        if _dir_damped:
            _tw = sum(cur_weights.values())
            if _tw > 1e-9:
                cur_weights = {h: w / _tw for h, w in cur_weights.items()}

        # CLOSE_VOLATILE(14:00~15:00) 구간: 단기(1m/3m/5m) FL편향 완화
        # 오후 저변동성 구간에서 단기 호라이즌이 FL에 과대 편향되어 중기 DN 신호를 희석.
        # 단기 가중치를 0.6× 축소 후 재정규화하여 10m/15m의 기여도를 상대적으로 확대.
        # 예외: TrendGate active 중에는 단기 호라이즌이 추세를 가장 빠르게 감지하므로
        #       축소하지 않는다 — CLOSE_VOLATILE 축소가 오히려 방향 확정을 방해.
        if time_zone == "CLOSE_VOLATILE" and not (trend_gate_up_active or trend_gate_dn_active):
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

        # ── 호라이즌 상수 출력 감지 (GBM 붕괴 보호) ──────────────────
        # 동일 direction + confidence max-min < 0.5%p 가 _CONST_OUT_N 분 지속
        # → 해당 호라이즌을 앙상블에서 임시 제외 후 재정규화.
        # F1AdaptiveWeight(EMA 기반·느림)보다 빠른 응답으로 즉시 피해 최소화.
        _const_stuck: set = set()
        # 비활성 호라이즌은 fallback 상수값으로 ConstOut을 허위 트리거하므로 버퍼 업데이트 제외
        _active_set_co = set(active_horizons) if active_horizons is not None else set(HORIZONS.keys())
        # [MW0602 464차 P5-a] BiasReset(uniform fallback) 호라이즌도 동일 사유로 제외.
        # BiasReset은 main.py STEP5가 편향 고착 호라이즌에 **의도적으로** 균등분포
        # (1/3,1/3,1/3)를 20분간 강제하는 안전장치인데, 그 균등값이 이 버퍼에 쌓이면
        # 정확히 5분 뒤 ConstOut이 "GBM 붕괴"로 오인해 스케일러 재적합 + 장중 GBM
        # 재학습(n=4800, CV 없음, force 교체)을 쏜다. 0811 실측 — 3m ConstOut 3회
        # 전부 BiasReset +5~8분 후였고(09:51→09:57 / 12:01→12:09 / 12:49→12:59),
        # 08-04~08-11 6거래일 대조에서도 3m·5m ConstOut의 대부분이 같은 패턴이다.
        # 이 오탐 하나가 "무검증 장중 모델이 검증된 EOD 모델을 영구 대체"하는 악순환의
        # 방아쇠였다(P5-b·DECISION_LOG 464차 참조). 위 "비활성 호라이즌 제외"와 완전히
        # 같은 취지 — 의도된 상수값은 모델 고장이 아니다.
        # 버퍼는 비운다: 남겨두면 20분 뒤 해제 시 override 이전 잔존값과 새 값이 섞여
        # 관찰 창이 오염된다. 해소 경로(아래 elif)의 clear와 같은 이유다.
        # 킬스위치: CONST_OUT_EXCLUDE_BIAS_RESET=False 로 종전 동작(오탐 포함) 복원.
        from config import settings as _rs_co
        _bias_set_co = (
            set(bias_override_horizons or [])
            if getattr(_rs_co, "CONST_OUT_EXCLUDE_BIAS_RESET", True) else set()
        )
        for _h in list(cur_weights.keys()):
            # [P1, 303차 후속] 30m 퇴역(296차) — 가중치는 이미 0으로 앙상블 투표에서
            # 제외되지만, 이 루프는 active_horizons(시간대 정책)만 걸러 30m을 그대로
            # 순회했음. 그 결과 앙상블에 전혀 기여하지 않는 30m 단독 상수 출력만으로도
            # main.py의 스케일러 재적합 + GBM 재학습 강제 예약(force=True)이 반복
            # 트리거되는 낭비가 있었음 — 위 30m 가중치 제외(352행)와 동일한 취지로
            # 감지 대상에서도 영구 제외.
            # [331차 후속2] 1m 퇴역 — 동일 취지로 감지 대상에서도 영구 제외.
            if _h == "30m" or _h == "1m":
                continue
            _res_h = horizon_proba.get(_h) or {}
            if not _res_h:
                continue
            if _h not in _active_set_co:
                continue
            # [464차 P5-a] BiasReset 중 — 의도된 균등값이므로 감지 대상 아님
            if _h in _bias_set_co:
                self._hz_conf_hist[_h].clear()
                continue
            _c = round(float(_res_h.get("confidence", 0.0)), 3)
            _d = int(_res_h.get("direction", 0))
            self._hz_conf_hist[_h].append((_d, _c))
            _hist = self._hz_conf_hist[_h]
            if len(_hist) >= self._CONST_OUT_N:
                _dirs  = [x[0] for x in _hist]
                _confs = [x[1] for x in _hist]
                if len(set(_dirs)) == 1 and (max(_confs) - min(_confs)) < self._CONST_OUT_RANGE:
                    _const_stuck.add(_h)

        # 전환 시점에만 로그 (매 분봉마다 출력 안 함)
        for _h in list(HORIZONS.keys()):
            _prev_stuck = self._hz_stuck.get(_h, False)
            _now_stuck  = _h in _const_stuck
            if _now_stuck and not _prev_stuck:
                _buf = self._hz_conf_hist[_h]
                _rng = max(x[1] for x in _buf) - min(x[1] for x in _buf)
                logger.warning(
                    "[ConstOut] %s 상수 출력 %d분 감지 (range=%.4f dir=%+d) → 앙상블 제외",
                    _h, self._CONST_OUT_N, _rng, list(_buf)[-1][0],
                )
            elif not _now_stuck and _prev_stuck:
                logger.info("[ConstOut] %s 상수 출력 해소 → 앙상블 복귀", _h)
                self._hz_conf_hist[_h].clear()   # 오염된 버퍼 클리어 후 재관찰 시작
            self._hz_stuck[_h] = _now_stuck
            if _now_stuck:
                cur_weights[_h] = 0.0

        # stuck 호라이즌 제외 후 가중치 재정규화
        _tw = sum(cur_weights.values())
        if _tw > 1e-9:
            cur_weights = {h: w / _tw for h, w in cur_weights.items()}
        else:
            # 전 호라이즌 동시 붕괴(매우 희귀) → 기본 가중치로 fallback
            cur_weights = dict(ENSEMBLE_WEIGHTS)
            logger.warning("[ConstOut] 전 호라이즌 상수 출력 — ENSEMBLE_WEIGHTS fallback")

        up_score   = 0.0
        down_score = 0.0
        flat_score = 0.0   # [Fix1] 직접 가중합 — 1-up-down 계산 시 up/down 반올림→0 → 1.0 팽창 방지
        total_w    = 0.0

        detail = {}
        for h, w in cur_weights.items():
            res = horizon_proba.get(h, {})
            if not res:
                continue
            up_score   += res.get("up",   0.0) * w
            down_score += res.get("down", 0.0) * w
            flat_score += res.get("flat", 0.0) * w
            total_w    += w
            detail[h]  = {
                "direction":  res.get("direction"),
                "confidence": res.get("confidence"),
                "weight":     round(w, 4),
            }

        if total_w > 0:
            up_score   /= total_w
            down_score /= total_w
            flat_score /= total_w

        # [Fix1] 직접 가중합 후 합계 정규화 (개별 호라이즌 반올림 오차 흡수)
        _score_sum = up_score + down_score + flat_score
        if _score_sum > 1e-9 and abs(_score_sum - 1.0) > 1e-4:
            up_score   /= _score_sum
            down_score /= _score_sum
            flat_score /= _score_sum
        # 안전망: 합계가 0인 극단 케이스 (모든 호라이즌 missing)
        # [conf(ema) 딥다이브, 개선안1] 콜드스타트 좁은 활성창(HORIZON_TIME_POLICY)에서
        # 유일한 활성 호라이즌이 Q3 bar_only 정책(HZ_DEPLOY_POLICY)으로 그 분에
        # horizon_proba에서 빠지면 여기로 떨어진다 — cur_weights상 가중치는 있지만
        # 실제 res가 없어 총가중합이 0인 경우. 이 붕괴가 인위적 flat_score=1.0을 만들고
        # 그게 그대로 Platt 보정을 거치면 "확신도 고착"처럼 보이는 게 실측 확인됨
        # (2026-07-28 conf(ema) 딥다이브). 발생 빈도를 계량하기 위해 계측만 추가하고
        # (아래 로그 + weight_collapsed 플래그 → DB 저장), 실제 동작 변경은
        # WEIGHT_COLLAPSE_HONEST_MODE(개선안4)/BAR_ONLY_RELAX_ENABLED(개선안5, 401차부터
        # 상시 적용으로 확장·기본 활성화) 플래그로 별도 게이트한다(이 블록 자체는
        # 동작 무변화 — 계측 전용).
        _weight_collapsed = _score_sum <= 1e-9
        if _weight_collapsed:
            flat_score = 1.0
            self._weight_collapse_streak += 1
            _wc_expected = sorted(h for h, w in cur_weights.items() if w > 1e-9)
            _wc_missing  = sorted(h for h in _wc_expected if not horizon_proba.get(h))
            logger.warning(
                "[WeightCollapse] 실질 가중합 0 (%d연속) — 활성기대=%s 중 미배포=%s "
                "→ flat_score=1.0 안전망 발동 (active_horizons=%s)",
                self._weight_collapse_streak, _wc_expected, _wc_missing, active_horizons,
            )
        else:
            self._weight_collapse_streak = 0

        # ── P0-A: TrendGate 추세 부스트 ─────────────────────────────
        # TrendGate streak(10분+)이 active이면 해당 방향 점수를 직접 올린다.
        # 이 처리가 없으면: dir=FLAT인 동안 TrendGate는 min_conf를 낮춰도
        # direction 확정 자체에는 영향을 못 줘 사실상 무력 (6/2 실증).
        # AdaptiveGater / StuckBreaker 적용 이전에 수행하여 후속 로직 일관성 유지.
        _trend_boost_applied = False
        if trend_gate_up_active:
            _up_before = up_score
            up_score   = min(self._TREND_SCORE_CAP, up_score + self._TREND_UP_BOOST)
            flat_score = max(0.0, 1.0 - up_score - down_score)
            _trend_boost_applied = True
            logger.debug(
                "[TrendBoost] UP streak active: up %.3f→%.3f flat→%.3f",
                _up_before, up_score, flat_score,
            )
        elif trend_gate_dn_active:
            _dn_before = down_score
            down_score = min(self._TREND_SCORE_CAP, down_score + self._TREND_DN_BOOST)
            flat_score = max(0.0, 1.0 - up_score - down_score)
            _trend_boost_applied = True
            logger.debug(
                "[TrendBoost] DN streak active: dn %.3f→%.3f flat→%.3f",
                _dn_before, down_score, flat_score,
            )

        # 개선2: TrendBoost 후 확률 합 정규화
        # flat이 음수가 되어 0에 clamp된 경우 up+down+flat > 1.0 발생 → 명시적 정규화
        if _trend_boost_applied:
            _tw_tb = up_score + down_score + flat_score
            if _tw_tb > 1e-9 and abs(_tw_tb - 1.0) > 1e-6:
                up_score   /= _tw_tb
                down_score /= _tw_tb
                flat_score /= _tw_tb
                logger.debug(
                    "[TrendBoost] sum=%.4f → 정규화 후 up=%.3f dn=%.3f fl=%.3f",
                    _tw_tb, up_score, down_score, flat_score,
                )

        # ── P0-B: FlatCap — 추세 중 flat_score 과지배 차단 ────────────
        # TrendBoost 이후에도 long-horizon FLAT 편향으로 flat이 0.38을 넘으면
        # 상한을 적용하고 재정규화한다.
        # 재정규화: up+dn+flat_capped 합이 1이 되도록 비례 스케일.
        if (trend_gate_up_active or trend_gate_dn_active) and flat_score > self._FLAT_CAP_ON_TREND:
            _flat_before = flat_score
            flat_score   = self._FLAT_CAP_ON_TREND
            _tw_renorm   = up_score + down_score + flat_score
            if _tw_renorm > 1e-9:
                up_score   = up_score   / _tw_renorm
                down_score = down_score / _tw_renorm
                flat_score = flat_score / _tw_renorm
            _trend_boost_applied = True
            logger.debug(
                "[FlatCap] flat %.3f→%.3f (추세 보호) up=%.3f dn=%.3f",
                _flat_before, self._FLAT_CAP_ON_TREND, up_score, down_score,
            )

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

        # ── ShortHorizonOverride: FLAT 고착 시 단기 호라이즌 우선 ──
        # dir=FLAT 5봉+ 연속이고 3m/5m 방향이 일치하면 단기 호라이즌으로 방향 결정.
        # 이유: 15m/30m FLAT 고착이 단기 방향 신호를 묻어버리는 구조 해소.
        # 안전장치: OFI/CVD 중 하나라도 동방향이어야 채택 (피처 기반 검증).
        # [331차 후속2] "1m" 제거 — 1m은 단순 무정보가 아니라 역스킬(z=-2.82, 체계적으로
        # 반대 방향)로 확정됐으므로, 이 override가 OFI/CVD 동의를 조건으로 걸어도 1m
        # 자신의 방향을 그대로 채택하는 것은 이론상 유해할 수 있다(ENSEMBLE_WEIGHTS·
        # ConstOut 감지에서 1m을 퇴역시킨 것과 동일 취지 — 30m 퇴역 선례 적용).
        if direction == DIRECTION_FLAT:
            self._flat_streak += 1
        else:
            self._flat_streak = 0

        _short_override_applied = False
        if direction == DIRECTION_FLAT and self._flat_streak >= 5:
            # 활성 호라이즌 중 가장 짧은 두 개를 단기 쌍으로 선택
            # (3m OFF 시 5m+10m 등 자동 대체). 1m은 역스킬 확정으로 영구 제외(331차 후속2).
            _HZ_SHORT_PREF = ["3m", "5m", "10m", "15m", "30m"]
            _short_pair = [h for h in _HZ_SHORT_PREF if horizon_proba.get(h)][:2]
            if len(_short_pair) >= 2:
                _h1, _h2 = _short_pair
                _s1 = horizon_proba[_h1]
                _s2 = horizon_proba[_h2]
                _d1 = _s1.get("direction", 0)
                _d2 = _s2.get("direction", 0)
                if _d1 != 0 and _d1 == _d2:
                    # OFI 또는 CVD가 같은 방향인지 피처로 검증
                    _ofi  = (features or {}).get("ofi_norm", 0.0)
                    _cvd  = (features or {}).get("cvd_direction", 0.0)
                    _feat_agree = (
                        (_d1 == DIRECTION_UP   and (_ofi > 0 or _cvd > 0)) or
                        (_d1 == DIRECTION_DOWN and (_ofi < 0 or _cvd < 0))
                    )
                    if _feat_agree:
                        _c1 = _s1.get("confidence", 0.0)
                        _c2 = _s2.get("confidence", 0.0)
                        direction  = _d1
                        confidence = (_c1 + _c2) / 2.0
                        # score 삼총사 정규화 — direction 전환 시 up/down/flat 일관성 보장
                        _sho_rem = max(0.0, 1.0 - confidence) / 2.0
                        if direction == DIRECTION_UP:
                            up_score   = confidence
                            down_score = _sho_rem
                            flat_score = _sho_rem
                        else:
                            down_score = confidence
                            up_score   = _sho_rem
                            flat_score = _sho_rem
                        _short_override_applied = True
                        logger.info(
                            "[ShortHorizonOverride] flat streak=%d → %s/%s 방향=%+d "
                            "conf=%.1f%% (ofi=%.2f cvd=%.2f)",
                            self._flat_streak, _h1, _h2, direction,
                            confidence * 100, _ofi, _cvd,
                        )

        # ── 호라이즌 합의도 패널티 (불합의 노이즈 필터) ───────────
        # 6개 중 2개 이하 합의: 방향 신호가 노이즈일 가능성 높음 → 진입 억제
        # 보너스 없음: 전 호라이즌 합의도 높아도 편향이면 오히려 7연속 실패 (이상점3 사례)
        # P0-D 예외: TrendGate active 중에는 패널티 면제.
        #   이유: 추세 초기엔 장기 호라이즌이 FLAT 고착 상태라 n_agree가 낮아도
        #   실제 추세 신호(단기 호라이즌)가 맞는 경우가 많다 — 이미 낮은 conf에
        #   추가 패널티를 주면 방향 확정을 이중으로 방해한다.
        if direction != DIRECTION_FLAT:
            _n_agree = sum(
                1 for h_res in horizon_proba.values()
                if h_res.get("direction") == direction
            )
            _tp_agree_exempt = (
                (trend_gate_up_active and direction == DIRECTION_UP) or
                (trend_gate_dn_active and direction == DIRECTION_DOWN)
            )
            if _n_agree <= 2:
                if _tp_agree_exempt:
                    logger.debug(
                        "[Ensemble] 합의도 패널티 면제 (TrendGate active) n_agree=%d/6",
                        _n_agree,
                    )
                else:
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
        #
        # TrendGate 예외: TrendBoost로 dir이 확정됐어도, 장기 호라이즌 FLAT 고착으로
        # n_coherent/n_active가 낮으면 CoherenceGate가 다시 차단.
        # 추세 초기엔 단기 호라이즌만 방향을 포착하므로 n_active 자체가 1~2 수준.
        # TrendGate(10분+ 연속)가 외부 추세 근거를 제공하므로 CoherenceGate를 완화.
        _coherence_blocked = False
        _tp_coherence_exempt = (
            (trend_gate_up_active and direction == DIRECTION_UP) or
            (trend_gate_dn_active and direction == DIRECTION_DOWN)
        )
        # 시간대별 CoherenceGate 임계값 차등 적용
        # GAP_OPEN: 개장 직후 단기 호라이즌만 방향 포착 → 합의도 기대치 낮춤
        # TrendGate ON(방향 불일치 포함): 추세 초기 장기 FLAT 고착 구간에서 완화
        _trend_gate_any = trend_gate_up_active or trend_gate_dn_active
        if time_zone == "GAP_OPEN":
            _coherence_min = 0.50
        elif _trend_gate_any:
            _coherence_min = 0.50
        else:
            _coherence_min = COHERENCE_GATE_MIN
        if direction != DIRECTION_FLAT:
            # FLAT 예측 호라이즌 제외: 방향성 있는 호라이즌만 대상
            # + BiasReset uniform fallback 적용된 호라이즌도 분모에서 제외
            # 이유: BiasReset이 uniform(=방향0=FLAT처럼 계산)을 적용하면 CoherenceGate
            #   score가 낮아져 원웨이장에서도 차단됨. BiasReset은 편향 모델을 방어하기 위한
            #   것이지 원웨이 감지를 방해하려는 게 아니므로, 해당 호라이즌은 집계 제외.
            # [267차] ConstOut 감지 호라이즌도 분모에서 제외.
            # ConstOut 호라이즌은 가중치=0으로 앙상블 투표에서 이미 제외되지만
            # horizon_proba 딕셔너리에는 잔존해 CoherenceGate 분모에 포함됐음.
            # 30m ConstOut(dir=+1) + 1m SHORT(-1) → score=1/2=0.50 < min=0.60 → 진입 전면 차단.
            # [296차] 30m 퇴역 — 위와 동일한 부작용(구조적 저성능 호라이즌의 노이즈
            # 방향이 분모에 남아 정상 진입을 차단)을 근본적으로 막기 위해 분모에서 영구 제외.
            # [311차] 1m도 동일 사유로 제외 — conf-층화 검증(06-15~07-10)에서 1m 방향예측
            # 정확도 45~51%(기준선 50%와 통계적으로 구분 불가, 무스킬)로 확인됨. 재구성
            # 백테스트 결과 1m 단독/다수 반대표로 인한 오차단이 317건(전체 결정의 6.4%) —
            # CoherenceGate 원 취지(호라이즌 간 진짜 불일치 감지)를 무스킬 호라이즌의
            # 노이즈가 대체하고 있었음.
            _bias_overrides = set(bias_override_horizons or []) | _const_stuck | {"30m", "1m"}
            _active_h = [
                h for h in horizon_proba
                if (horizon_proba[h]
                    and horizon_proba[h].get("direction") != DIRECTION_FLAT
                    and h not in _bias_overrides)
            ]
            _n_active = len(_active_h)
            if _n_active > 0:
                _n_coherent = sum(
                    1 for h in _active_h
                    if horizon_proba[h].get("direction") == direction
                )
                _coherence_score = _n_coherent / _n_active
                if _coherence_score < _coherence_min:
                    if _tp_coherence_exempt:
                        # TrendGate가 외부 추세 근거를 제공 → CoherenceGate 면제
                        logger.debug(
                            "[Ensemble] CoherenceGate 면제 (TrendGate active) "
                            "score=%.2f (%d/%d비FLAT) dir=%+d",
                            _coherence_score, _n_coherent, _n_active, direction,
                        )
                    else:
                        _coherence_blocked = True
                        logger.info(
                            "[Ensemble] CoherenceGate 차단 score=%.2f (%d/%d비FLAT) dir=%+d zone=%s min=%.2f",
                            _coherence_score, _n_coherent, _n_active, direction,
                            time_zone or "OTHER", _coherence_min,
                        )

        # ── 캐스케이드 코히어런스 게이트 (Phase 1-2) ─────────────────
        # CoherenceGate(비율)와 보완: 장기→단기 방향 정렬 순서를 검증
        # 하위 호라이즌만 방향 있고 상위는 FLAT이면 노이즈성 스파이크로 차단
        _cascade_blocked = False
        if direction != DIRECTION_FLAT and not _coherence_blocked:
            _cascade_score = compute_cascade_coherence(horizon_proba)
            if _cascade_score < 0.25:
                _cascade_blocked = True
                _coherence_blocked = True
                logger.info(
                    "[Ensemble] CascadeCoherence 차단 score=%.2f dir=%+d",
                    _cascade_score, direction,
                )

        # ── Platt 보정 — UP/DN/FLAT 전방향 동일 처리 (P1) ────────────────
        # P1: FLAT도 UP/DN과 같은 calibration 경로 통과
        #   → 방향 전환 시 calibration 불연속(conf 급등락) 제거
        # P3 블렌딩(calibration.py)으로 is_fitted 전환 점프 완화
        _confidence_raw = confidence
        # [461차 P-C] 이 분의 conf가 보정 적용값인지 raw 통과값인지 기록한다.
        # 아래 분기 중 실제로 보정 함수를 통과한 경로만 True — 사후 추정
        # (`conf == min(raw, 0.85)`)이 아니라 사실을 남긴다.
        _cal_applied = False
        if _weight_collapsed and WEIGHT_COLLAPSE_HONEST_MODE:
            # [conf(ema) 딥다이브, 개선안4 — 기본 비활성] 실질 신호 0인 붕괴 케이스는
            # 인위적 raw=1.0을 캘리브레이터에 넣지 않고 "판단불가"를 정직하게 confidence=0.0
            # 으로 표시한다. 캘리브레이터 fit 여부와 무관하게 항상 이 분기 우선.
            confidence = 0.0
        elif self.ensemble_calibrator.is_fitted:
            _cal = self.ensemble_calibrator.calibrate(confidence)
            confidence = min(max(float(_cal), 0.0), 0.85)
            _cal_applied = True
        elif self.calibrator is not None:
            _cal = self.calibrator.calibrate("3m", confidence)
            confidence = min(max(float(_cal), 0.0), 0.85)
            # 호라이즌 보정기는 미fit이면 raw를 그대로 돌려준다 — 그 경우는
            # "적용"이 아니다(is_fitted 접근자로 사실 확인, 461차 P-C).
            try:
                _cal_applied = bool(self.calibrator.is_fitted("3m"))
            except Exception:
                _cal_applied = False
        else:
            confidence = min(max(float(confidence), 0.0), 0.85)
        # [conf(ema) 딥다이브, 개선안3] 보정은 direction에 해당하는 스코어 하나만
        # 갱신하고 나머지 두 값은 보정 이전(raw) 값이 그대로 남아 up+down+flat 합이
        # 1이 아니게 되던 버그 수정 — 나머지 두 값을 remainder로 비례 재분배한다.
        if direction == DIRECTION_UP:
            up_score = confidence
            down_score, flat_score = self._fill_remainder(confidence, down_score, flat_score)
        elif direction == DIRECTION_DOWN:
            down_score = confidence
            up_score, flat_score = self._fill_remainder(confidence, up_score, flat_score)
        else:
            flat_score = confidence
            up_score, down_score = self._fill_remainder(confidence, up_score, down_score)

        # ── 레짐별 최소 신뢰도 기준 ──────────────────────────
        # [297차] zone_mc(시간대 DynMC + FQAdj 실시간 조정 반영값)를 1차 기준으로 사용.
        # 종전에는 REGIME_MIN_CONFIDENCE[regime]만 사용해 FQAdj의 완화가 여기 반영되지
        # 않았고, main.py의 max(min_conf, zone_mc)가 완화를 재차 무효화했다(268차 의도
        # 무산 — FQAdj "완화" 로그는 하루 수백 회 찍히지만 실제 컷은 항상 완화 전 값).
        # RISK_OFF만 REGIME_MIN_CONFIDENCE의 추가 강화(+10%p, update_dynamic_mc 참조)를
        # 유지 — zone_mc는 시간대 축이라 레짐 축의 리스크오프 강화를 대체하지 못한다.
        _regime_floor = REGIME_MIN_CONFIDENCE.get(regime, 0.58)
        min_conf  = max(_regime_floor, zone_mc) if regime == "RISK_OFF" else zone_mc
        regime_ok = (confidence >= min_conf) and (direction != DIRECTION_FLAT)

        # [403차 종합 P0-2b] 하한 ↔ 보정기 출력범위 정합성 점검 (상태 변화 시에만 로그)
        # [404차 후속4 / P1-E] 진입 허용 시간대에서만 판정 — 블랙아웃 구간 오탐 억제
        self._check_conf_floor_consistency(min_conf, zone_allows_entry)

        # ── 진입 등급 (체크리스트 통과 수는 entry_manager에서 계산) ──
        # 코히어런스 게이트 차단 시 최우선 X
        if _coherence_blocked:
            grade = "X"
        elif not regime_ok:
            grade = "X"
        elif confidence >= 0.70:
            # Grade A 롤링 정확도 가드: 고신뢰도 예측 실적이 _HC_GUARD_ACC_THR 미달이면 B 강등.
            # conf 0.7+ 실측 acc ~29-31% (conf 0.4대 33%보다 낮음) 역전 현상 대응.
            _hc_n = len(self._hc_buf)
            _hc_acc = (sum(self._hc_buf) / _hc_n) if _hc_n > 0 else 0.0
            _hc_guard_active = _hc_n >= self._HC_GUARD_MIN_N
            _hc_blocked = _hc_guard_active and (_hc_acc < self._HC_GUARD_ACC_THR)
            if _hc_blocked:
                grade = "B"
                if not self._hc_grade_a_blocked:
                    logger.warning(
                        "[HCGuard] Grade A → B 강등: 고신뢰 최근 %d건 acc=%.1f%% < %.0f%%",
                        _hc_n, _hc_acc * 100, self._HC_GUARD_ACC_THR * 100,
                    )
                self._hc_grade_a_blocked = True
            else:
                grade = "A"
                if self._hc_grade_a_blocked and _hc_guard_active:
                    logger.info(
                        "[HCGuard] Grade A 차단 해제: 고신뢰 최근 %d건 acc=%.1f%%",
                        _hc_n, _hc_acc * 100,
                    )
                self._hc_grade_a_blocked = False
        elif confidence >= 0.60:
            grade = "B"
        elif confidence >= min_conf:
            grade = "C"
        else:
            grade = "X"

        auto_entry = ENTRY_GRADE.get(grade, {}).get("auto", False) and regime_ok

        # 30m 역방향 필터 — 비활성화(2026-06-25) → 퇴역 확정(296차, 2026-07-06)
        # 250차 시점 사유: 30m 모델이 need_add 피처(opt_gex_bn·opt_chain_pcr 등) 미탑재
        #   상태로 CV acc=0.2796(랜덤 이하)이며, 필터가 정상 진입을 차단하는 역효과 발생.
        # 296차 확정 사유: need_add 8개 피처 탑재(292차) 후 첫 EOD full_cv 재학습 결과
        #   CV acc=0.3052 — 재활성화 기준(≥0.33~0.38) 여전히 미달, 랜덤보다도 낮음.
        #   "피처 부족" 가설 소진 → 구조적 저성능으로 최종 판단, 재활성화 계획 철회.
        #   아래 플래그는 대시보드/로그 참고용으로만 유지(grade 격하 없음, 기존과 동일).
        if _proba_30m is not None and direction != DIRECTION_FLAT:
            _dir_30m = _proba_30m.get("direction", DIRECTION_FLAT)
            if _dir_30m != DIRECTION_FLAT and _dir_30m != direction:
                _30m_filter_blocked = True  # 플래그만 기록 (grade 격하 없음)
                logger.debug(
                    "[Ensemble] 30m 역방향 감지(필터 비활성): 30m=%+d ens=%+d",
                    _dir_30m, direction,
                )

        # P4: display용 EMA smoothing (span=20) — 실거래 로직(grade·regime_ok)은 비보정 confidence 기준
        if self._conf_ema is None:
            self._conf_ema = confidence
        else:
            self._conf_ema = self._CONF_EMA_ALPHA * confidence + (1.0 - self._CONF_EMA_ALPHA) * self._conf_ema

        result = {
            "direction":          direction,
            "confidence":         round(confidence, 4),
            "confidence_raw":     round(_confidence_raw, 4),
            "confidence_smoothed": round(self._conf_ema, 4),
            "up_score":           round(up_score, 4),
            "down_score":         round(down_score, 4),
            "flat_score":         round(flat_score, 4),
            "grade":              grade,
            "auto_entry":         auto_entry,
            "regime_ok":          regime_ok,
            "min_conf":           min_conf,
            "coherence_blocked":  _coherence_blocked,
            "cascade_blocked":    _cascade_blocked,
            "trend_boost_applied": _trend_boost_applied,
            "detail":             detail,
            "gating":             gating,
            "decorr":                self._decorr.get_status(),
            "stuck":                 self._stuck.status_dict(),
            "f1_adaptive":           self._f1_weight.get_f1_status(),
            "const_output_horizons": sorted(_const_stuck),
            "30m_filter_blocked":    _30m_filter_blocked,
            "conf_stuck_boost_applied": _stuck_boost_applied,
            "weight_collapsed":      _weight_collapsed,
            # [461차 P-C] conf 스케일 판독용 — 1=보정 적용 / 0=raw 통과
            "cal_applied":           _cal_applied,
        }

        logger.info(
            f"[Ensemble] dir={direction:+d} conf={confidence:.1%} "
            f"grade={grade} regime={regime}"
            + (" [30m역방향차단]" if _30m_filter_blocked else "")
            + (" [ConfStuckBoost]" if _stuck_boost_applied else "")
            + (" [WeightCollapse]" if _weight_collapsed else "")
        )
        return result

    @staticmethod
    def _fill_remainder(primary: float, a: float, b: float) -> Tuple[float, float]:
        """[conf(ema) 딥다이브, 개선안3] confidence 보정 후 나머지 두 스코어를

        remainder(1 - primary)로 비례 재분배해 up+down+flat 합=1을 보장한다.
        기존 상대비(a:b)를 유지하며, 둘 다 0이면 remainder를 균등 분배한다.
        """
        remainder = max(0.0, 1.0 - primary)
        total = a + b
        if total > 1e-9:
            return remainder * (a / total), remainder * (b / total)
        return remainder / 2.0, remainder / 2.0

    def record_ensemble_outcome(
        self, raw_conf: float, correct: bool, weight_collapsed: bool = False,
    ) -> None:
        """앙상블 보정기에 결과 누적 — STEP 1 검증 시 main.py에서 호출.

        [461차 P-A] weight_collapsed=True는 그 분의 raw_conf가 모델 출력이 아니라
        WeightCollapse 안전망이 넣은 인위값(flat_score=1.0)이라는 뜻이다. 기본
        False이며, 라이브 학습 표본 구성은 `CAL_COLLAPSE_EXCLUDE_LIVE`가 False인 한
        종전과 동일하다(오염행 포함) — 지금은 clean 섀도 윈도만 따로 쌓는다.
        """
        self.ensemble_calibrator.record(
            raw_conf, correct, is_artifact=bool(weight_collapsed),
        )
        # Grade A 가드용 고신뢰도 버퍼 업데이트 (calibrated conf 기준)
        if raw_conf >= self._HC_GUARD_CONF_THR:
            self._hc_buf.append(1 if correct else 0)

    def record_horizon_verification(
        self, horizon: str, predicted: int, actual: int
    ) -> None:
        """호라이즌별 F1 EMA 업데이트 — STEP 1 검증 시 main.py에서 호출."""
        self._f1_weight.update(horizon, predicted, actual)

    def reset_daily(self):
        self._stuck.reset_daily()
        for h in self._hz_conf_hist:
            self._hz_conf_hist[h].clear()
        self._hz_stuck = {h: False for h in HORIZONS}
        self._flat_streak = 0
        self._fl_streak = {h: 0 for h in HORIZONS}
        self._weight_collapse_streak = 0
        # HCGuard 버퍼는 일일 리셋 안 함 — 누적 데이터가 가드 품질의 핵심
        # (장 사이 하루만 공백이어도 50건 버퍼가 유효하므로 유지)

    def reset_exchange_cb(self) -> None:
        """거래소 CB 해제 후 앙상블 상태 초기화.

        - ConstOut 버퍼: CB 기간 빈 데이터로 상수 출력 오판 방지
        - CascadeCoherence 방향 버퍼: 공백 전 호라이즌 방향 잔존 제거
        - FL streak: CB 공백이 FL 연속으로 오산될 수 있음
        """
        for h in self._hz_conf_hist:
            self._hz_conf_hist[h].clear()
        self._hz_stuck = {h: False for h in HORIZONS}
        self._flat_streak = 0
        self._fl_streak = {h: 0 for h in HORIZONS}
        # StuckBreaker streak도 리셋 — CB 직전 방향 고착이 재개 후 오발동 방지
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
