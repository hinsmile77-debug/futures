# learning/self_learning/drift_adjuster.py
"""
SGD 학습률 드리프트 조정기

5일 롤링 정확도 추이를 보고 SGD의 alpha(학습률)를 자동 조정한다.
- 정확도 하락 추세 → alpha 상향 (더 빠르게 적응)
- 정확도 안정/상향 → alpha 하향 (과적합 방지)

⚠ [MW0602 492차 F-7] 액션은 넷이 아니라 **다섯**이다 —
  `DRIFT_UP` / **`DRIFT_UP_SATURATED`**(상한 포화, 무연산) / `RECOVERY_DOWN` /
  `HOLD` / `SKIP_LOW_SAMPLE`. 소비부(대시보드 라벨 등)를 정확 일치로 비교하지 말 것.

파일:
  data/drift_adjuster_state.json — 이력·alpha 상태 저장
"""
import json
import logging
import datetime
import os
from collections import deque
from typing import Dict, Optional

logger = logging.getLogger("LEARNING")

_DEFAULT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "drift_adjuster_state.json"
)

# SGD alpha 기본값·범위
ALPHA_DEFAULT = 0.001
ALPHA_MIN     = 0.0001
ALPHA_MAX     = 0.01

# 정확도 하락으로 판단하는 임계치
DRIFT_THRESHOLD       = 0.50   # 이 정확도 이하가 N일 연속이면 드리프트 감지
DRIFT_DAYS_REQUIRED   = 3      # 연속 N일 하락 시 alpha 상향
RECOVERY_THRESHOLD    = 0.58   # 이 정확도 이상이 N일 연속이면 회복 판단
RECOVERY_DAYS_REQUIRED = 2     # 연속 N일 회복 시 alpha 하향

# alpha 조정 배율
ALPHA_UP_FACTOR   = 1.5   # 드리프트 시 1.5배 상향
ALPHA_DOWN_FACTOR = 0.8   # 회복 시 0.8배 하향 (천천히)

# 롤링 이력 유지 기간
HISTORY_DAYS = 10

# 당일 정확도 산출에 쓰인 유효 표본이 이 값 미만이면 이력 반영·alpha 조정을 스킵한다.
# 표본이 3~4건뿐이면 1/3=33%, 1/2=50% 같은 극단값이 그대로 alpha를 흔들어
# drift 오판(연속 하락으로 오인)을 유발한다. contrarian_mode._ACC30M_MIN_SAMPLES=15와
# 동일 기준(1건 오답으로 오발동 방지) 적용.
MIN_SAMPLES_REQUIRED = 15


class DriftAdjuster:
    """
    일일 정확도 추이로 SGD alpha를 동적 조정한다.

    사용 (daily_close() 내부):
        drift_adjuster.record_accuracy(today_accuracy)
        new_alpha = drift_adjuster.get_alpha()
        online_learner.set_alpha(new_alpha)   # SGD 학습률 갱신
    """

    def __init__(self, path: str = _DEFAULT_PATH):
        self._path  = os.path.abspath(path)
        self._alpha: float = ALPHA_DEFAULT
        # 일별 전체 정확도 이력 (최근 HISTORY_DAYS일)
        self._acc_history: deque = deque(maxlen=HISTORY_DAYS)
        # 마지막 record_accuracy() 판정 (대시보드 표시용, 재기동해도 유지되도록 영속화)
        self._last_action: str = "HOLD"
        self._load()

    # ── 15:40 마감 시 호출 ─────────────────────────────────────
    def record_accuracy(self, accuracy: float, n_samples: Optional[int] = None) -> Dict:
        """
        당일 전체 정확도를 기록하고 alpha를 갱신한다.

        Args:
            accuracy: 당일 전체 예측 정확도 (0.0~1.0)
            n_samples: 이 정확도 산출에 쓰인 당일 유효 표본 수 (전 호라이즌 합산).
                       MIN_SAMPLES_REQUIRED 미만이면 극단값이 alpha·이력에 반영되지
                       않도록 이번 기록을 스킵한다 (None이면 가드 미적용, 호환용).

        Returns:
            {"alpha": float, "action": str, "history": list}
        """
        if n_samples is not None and n_samples < MIN_SAMPLES_REQUIRED:
            logger.info(
                "[DriftAdjuster] 표본 부족(n=%d < %d) — acc=%.1f%% 반영 스킵, alpha=%.5f 유지",
                n_samples, MIN_SAMPLES_REQUIRED, accuracy * 100, self._alpha,
            )
            self._last_action = "SKIP_LOW_SAMPLE"
            self._save()
            return {
                "alpha":   self._alpha,
                "action":  "SKIP_LOW_SAMPLE",
                "history": list(self._acc_history),
            }

        self._acc_history.append(round(accuracy, 4))
        action = self._adjust_alpha()
        self._last_action = action
        self._save()

        # [MW0602 492차 F-7 ④] 원천·표본 병기 — 0824 의 `acc=0.0%` 가 **진짜 0%**인지
        # **미측정 0**인지 이 줄만으로 구분되지 않았다(계측 4원칙 ②, 0824 1-13 ⚠②).
        # n 은 호출부가 넘긴 당일 유효 표본 수, src 는 그 값을 만든 함수다.
        logger.info(
            "[DriftAdjuster] acc=%.1f%% n=%s src=online_learner.recent_accuracy "
            "→ alpha=%.5f (%s) | 이력=%s",
            accuracy * 100,
            ("NA" if n_samples is None else n_samples),
            self._alpha, action,
            [f"{a:.0%}" for a in list(self._acc_history)[-5:]],
        )
        return {
            "alpha":   self._alpha,
            "action":  action,
            "history": list(self._acc_history),
        }

    def get_alpha(self) -> float:
        """현재 권장 SGD alpha 반환"""
        return self._alpha

    def get_status(self) -> Dict:
        """대시보드 조회용 — 현재 alpha·마지막 판정 액션·10일 정확도 이력 스냅샷"""
        return {
            "alpha":   self._alpha,
            "action":  self._last_action,
            "history": list(self._acc_history),
        }

    def reset(self) -> None:
        """alpha를 기본값으로 초기화 (수동 개입 시)"""
        self._alpha = ALPHA_DEFAULT
        self._acc_history.clear()
        self._last_action = "HOLD"
        self._save()
        logger.info("[DriftAdjuster] 수동 초기화 — alpha=%.5f", self._alpha)

    # ── 내부 로직 ──────────────────────────────────────────────
    def _adjust_alpha(self) -> str:
        hist = list(self._acc_history)
        n    = len(hist)

        if n >= DRIFT_DAYS_REQUIRED:
            recent_drift = hist[-DRIFT_DAYS_REQUIRED:]
            if all(a < DRIFT_THRESHOLD for a in recent_drift):
                old = self._alpha
                self._alpha = min(self._alpha * ALPHA_UP_FACTOR, ALPHA_MAX)
                # ── [MW0602 492차 F-7 ①②] 상한 포화를 「올렸다」와 가른다 ───────────
                # `ALPHA_MAX` 에 이미 붙어 있으면 min() 이 같은 값을 돌려주므로 이
                # 분기는 **아무것도 하지 않는다.** 그런데 종전에는 그런 날도
                # `WARNING` + "alpha 0.01000→0.01000" 을 찍어 **매일 대응하고 있는
                # 것처럼** 보였다(0824 1-13: 최근 9일 중 6일이 그랬다).
                # 🔴 `ALPHA_MAX`·`ALPHA_UP_FACTOR`·`DRIFT_THRESHOLD` 는 **무변경**이다.
                #    임계를 관측값에서 역산하지 않는다(사전등록 ④). 계측만 가른다.
                if self._alpha == old:
                    logger.info(
                        "[DriftAdjuster] %d일 연속 정확도 %.0f%% 미만 → "
                        "alpha %.5f→%.5f (상한 포화 — 무연산, ALPHA_MAX=%.5f)",
                        DRIFT_DAYS_REQUIRED, DRIFT_THRESHOLD * 100,
                        old, self._alpha, ALPHA_MAX,
                    )
                    return "DRIFT_UP_SATURATED"
                logger.warning(
                    "[DriftAdjuster] %d일 연속 정확도 %.0f%% 미만 → alpha %.5f→%.5f",
                    DRIFT_DAYS_REQUIRED, DRIFT_THRESHOLD * 100, old, self._alpha,
                )
                return "DRIFT_UP"

        if n >= RECOVERY_DAYS_REQUIRED:
            recent_rec = hist[-RECOVERY_DAYS_REQUIRED:]
            if all(a >= RECOVERY_THRESHOLD for a in recent_rec):
                old = self._alpha
                self._alpha = max(self._alpha * ALPHA_DOWN_FACTOR, ALPHA_MIN)
                logger.info(
                    "[DriftAdjuster] %d일 연속 회복 %.0f%% 이상 → alpha %.5f→%.5f",
                    RECOVERY_DAYS_REQUIRED, RECOVERY_THRESHOLD * 100, old, self._alpha,
                )
                return "RECOVERY_DOWN"

        return "HOLD"

    # ── 영속성 ───────────────────────────────────────────────
    def _save(self) -> None:
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        state = {
            "updated":     datetime.datetime.now().isoformat(),
            "alpha":       self._alpha,
            "acc_history": list(self._acc_history),
            "last_action": self._last_action,
        }
        try:
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning("[DriftAdjuster] 저장 실패: %s", e)

    def _load(self) -> None:
        if not os.path.exists(self._path):
            return
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                state = json.load(f)
            self._alpha       = float(state.get("alpha", ALPHA_DEFAULT))
            self._acc_history = deque(
                state.get("acc_history", []), maxlen=HISTORY_DAYS
            )
            self._last_action = str(state.get("last_action", "HOLD"))
            logger.info(
                "[DriftAdjuster] 로드: alpha=%.5f, 이력 %d일, 마지막 액션=%s",
                self._alpha, len(self._acc_history), self._last_action,
            )
        except Exception as e:
            logger.warning("[DriftAdjuster] 로드 실패 (기본값 사용): %s", e)
