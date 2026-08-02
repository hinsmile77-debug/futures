# learning/shap/shap_tracker.py — SHAP 피처 중요도 추적 및 심사
"""
주간 SHAP 피처 심사 — 중요도 하락 피처 감지 및 교체 추천

운영 원칙:
  - CORE 피처 3개 (CVD·VWAP·OFI) 절대 교체 불가
  - 중요도 하락 피처 → DYNAMIC_FEATURES_POOL에서 대체 후보 추천
  - 하루 최대 1개 교체, 교체 후 3일간 재교체 금지
  - 인간 검토 필수 (자동 교체 금지)

SHAP 계산:
  TreeExplainer (GBM 전용, 빠름)
  shap 패키지 없으면 feature_importances_ 로 대체
"""
import os
import logging
import datetime
import json
from typing import Dict, List, Optional, Tuple
from collections import deque

import numpy as np

try:
    import shap as _shap
    _SHAP_OK = True
except ImportError:
    _SHAP_OK = False

try:
    from sklearn.inspection import permutation_importance as _permutation_importance
    _PERM_IMP_OK = True
except ImportError:
    _PERM_IMP_OK = False

from config.constants import CORE_FEATURES, DYNAMIC_FEATURES_POOL
from config.settings import (
    SHAP_COOLDOWN_DAYS, SHAP_MAX_REPLACE_DAILY,
    SHAP_RANK_IMPROVE_MIN, SHAP_MIN_DATA_POINTS, SHAP_DB,
)

# SHAP 전용 로거: LEARNING 레이어 파일 핸들러 없이 독립 실행되는 문제를 방지하기 위해
# LEARNING 로거를 사용한다. shap 패키지 오류가 LEARNING.log에 기록된다.
logger = logging.getLogger("LEARNING")


def _permutation_importance_fallback(
    model, X: np.ndarray, y: np.ndarray, n_features: int,
) -> Optional[np.ndarray]:
    """[311차 후속9] HistGradientBoostingClassifier 전용 중요도 계산.

    TreeExplainer(shap 0.41: 다중클래스 미지원)와 estimators_/feature_importances_
    (HistGradientBoostingClassifier엔 둘 다 없음 — sklearn이 히스토그램 기반 부스팅에서
    이 속성들을 의도적으로 미제공)가 전부 실패하는 모델 타입에서 유일하게 동작하는 경로.
    라벨(y) 필요 — 검증 완료된 (X, actual) 쌍이 있을 때만 호출할 것.
    """
    if not _PERM_IMP_OK or y is None or len(y) != len(X):
        return None
    if len(np.unique(y)) < 2:
        return None
    # [337차] X 열 수가 모델이 실제로 학습된 입력 차원과 다르면 permutation_importance가
    # 내부적으로 model.predict(X)를 호출하다 ValueError로 실패한다 — 레지스트리(다음
    # 재학습 계획)와 배포된 모델의 피처셋이 어긋났을 때 발생(동적피처 탭 장시간 미갱신의
    # 원인이었던 패턴). 조용히 매분 재시도하는 대신 원인을 명확히 남긴다.
    _model_n_in = getattr(model, "n_features_in_", None)
    if _model_n_in is not None and X.shape[1] != _model_n_in:
        logger.warning(
            "[SHAP] permutation_importance 스킵: X 피처 수(%d) != 모델 학습 피처 수(%d) "
            "— 레지스트리/배포 모델 피처셋 불일치 의심",
            X.shape[1], _model_n_in,
        )
        return None
    try:
        result = _permutation_importance(
            model, X, y, n_repeats=5, random_state=42, n_jobs=1,
        )
        imp = np.clip(result.importances_mean, 0.0, None)
        if len(imp) != n_features:
            return None
        return imp
    except Exception as e:
        logger.warning("[SHAP] permutation_importance 실패: %s", e)
        return None


class ShapTracker:
    """
    SHAP 피처 중요도 추적 및 주간 심사

    사용:
        tracker = ShapTracker(feature_names)
        tracker.update(model, X_recent)    # 매 분봉 or 주간
        report  = tracker.weekly_review()  # 주간 심사
    """

    # 중요도 히스토리 보관 주 수
    HISTORY_WEEKS = 12

    def __init__(self, feature_names: List[str]):
        self.feature_names = feature_names
        self._n_features   = len(feature_names)

        # 주간 중요도 히스토리 (deque of {week, importances})
        self._history: deque = deque(maxlen=self.HISTORY_WEEKS)

        # 교체 이력
        self._replace_log: List[dict] = []
        self._last_replace: Optional[datetime.date] = None

        # 현재 중요도 (최신)
        self._current_importance: Optional[np.ndarray] = None
        # 방향별 중요도: [UP클래스배열, DN클래스배열, FL클래스배열] — per-class 경로에서만 설정
        self._current_importance_by_class: Optional[List[np.ndarray]] = None

        # TreeExplainer 첫 실패 후 False로 설정 → 이후 매분 불필요한 시도 방지
        self._tree_explainer_ok: bool = True

        # 반복 로그 억제: 같은 주 갱신은 DEBUG, 심사 로그는 30분 1회
        self._last_logged_update_week: Optional[tuple] = None
        self._last_review_log_ts: Optional[datetime.datetime] = None
        # [414차 후속] 차원 불일치 경고 스로틀(하루 1회) — 불일치는 재학습 전까지
        # 지속되므로 매분 찍으면 로그가 하루 수백 줄 늘어난다.
        self._last_dim_warn_date: Optional[str] = None

        self._load_history()

    # ── SHAP 계산 ─────────────────────────────────────────────────
    def update(
        self, model, X: np.ndarray, y: Optional[np.ndarray] = None, sample_size: int = 500,
    ) -> bool:
        """
        모델과 최근 데이터로 SHAP 중요도 계산 후 히스토리 추가

        Args:
            model:       학습된 GBM 모델 (sklearn)
            X:           최근 N개 분봉 피처 행렬
            y:           [311차 후속9] X와 짝지어진 검증완료 실제 레이블(있으면
                         permutation_importance fallback 활성화 — HistGradientBoosting
                         Classifier 등 estimators_/feature_importances_ 없는 모델 전용).
                         None이면 기존 동작(TreeExplainer/per-class/global) 그대로.
            sample_size: SHAP 계산 샘플 수 (속도 제어)

        Returns:
            True  — 실제 계산 완료
            False — 데이터 부족·계산 실패로 skip
        """
        if len(X) < SHAP_MIN_DATA_POINTS:
            logger.debug(f"[SHAP] 데이터 부족 ({len(X)} < {SHAP_MIN_DATA_POINTS})")
            return False

        # 샘플링 — y가 있으면 동일 idx로 짝을 유지해야 함
        idx = np.random.choice(len(X), min(sample_size, len(X)), replace=False)
        X_s = X[idx]
        y_s = y[idx] if y is not None and len(y) == len(X) else None

        importance = self._calc_importance(model, X_s, y_s)
        if importance is None:
            return False

        self._current_importance = importance
        current_week = tuple(datetime.date.today().isocalendar()[:2])
        entry = {
            "week":       list(current_week),
            "importance": importance.tolist(),
            "n_samples":  len(X_s),
            "timestamp":  datetime.datetime.now().isoformat(),
        }
        # 같은 주 엔트리는 최신 데이터로 교체 (weekly deduplication)
        # 매분 호출돼도 주별 슬롯 1개만 유지 → 다주 히스토리 보존
        is_new_week = not (self._history and tuple(self._history[-1].get("week", [])) == current_week)
        if not is_new_week:
            self._history.pop()
        self._history.append(entry)
        self._save_history()

        if current_week != self._last_logged_update_week:
            logger.info("[SHAP] 중요도 갱신 완료 (n=%d, week=%s)", len(X_s), current_week)
            self._last_logged_update_week = current_week
        else:
            logger.debug("[SHAP] 중요도 갱신 (n=%d, week=%s)", len(X_s), current_week)
        return True

    def _calc_importance(
        self, model, X: np.ndarray, y: Optional[np.ndarray] = None,
    ) -> Optional[np.ndarray]:
        """중요도 계산 4단계 우선순위:
        1) SHAP TreeExplainer (이진 모델 / shap 미래 버전에서 다중 클래스 지원 시 자동 활성)
        2) per-class 트리 중요도 (GBM 다중 클래스 전용 — 방향별 기여도 max 집계)
        3) global feature_importances_
        4) [311차 후속9] permutation_importance (y 필요) — HistGradientBoostingClassifier
           전용 최종 fallback. 1~3은 이 모델 타입에서 구조적으로 전부 실패한다
           (estimators_/feature_importances_ 속성 자체가 없음, shap 0.41 다중클래스 미지원).
        """
        # ── 0) [414차 후속] 모델 입력 차원 교차검증 (경로 1~4 공통 선행 가드) ──
        # 아래 1~3의 길이 검사는 전부 `self._n_features`(= len(self.feature_names))만
        # 본다. 이름 배열이 모델 차원과 어긋나 있으면 그 검사는 통과하면서 값만 엉뚱한
        # 이름에 붙는다 — 414차 딥다이브에서 2026-06-17~07-10(22거래일) 동안 실제로
        # 그렇게 기록됐다(길이 12/14 중요도가 길이 97/121 이름 배열의 앞 K칸에 얹혀,
        # 모델이 쓰지도 않는 레지스트리 선두 블록 cvd_*/ofi_*이 상위 중요도로 20거래일
        # 연속 기록). 경로 4에는 337차가 같은 취지의 가드를 넣었으나 1~3은 무방비였다.
        # 여기서 한 번에 막는다 — 잘못된 기록을 남기느니 남기지 않는 편이 낫다.
        _n_in = getattr(model, "n_features_in_", None)
        if _n_in is not None and int(_n_in) != self._n_features:
            _today = datetime.date.today().isoformat()
            if self._last_dim_warn_date != _today:
                self._last_dim_warn_date = _today
                logger.warning(
                    "[SHAP] 중요도 계산 스킵: feature_names %d개 != 모델 입력 %d개 — "
                    "이름-값 대응이 어긋나므로 기록하지 않는다(414차). "
                    "ShapTracker 생성 시 실배포 모델의 피처셋을 쓰는지 확인할 것.",
                    self._n_features, int(_n_in),
                )
            return None

        # ── 1) SHAP TreeExplainer ───────────────────────────────────
        # [332차] HistGradientBoostingClassifier(배치 재학습 주 경로 모델)에서
        # shap 0.41 TreeExplainer.shap_values()가 "binary classification" 류의
        # 정상 Python 예외가 아니라 Windows 0xc0000374(STATUS_HEAP_CORRUPTION)
        # 네이티브 크래시로 죽어 try/except가 못 잡고 프로세스 전체가 종료됨
        # (실사고: crash_fault.log). estimators_ 없는 모델(HGB)은 TreeExplainer가
        # 애초에 지원하는 구조가 아니므로 2)와 동일한 hasattr 게이트로 아예 스킵.
        if _SHAP_OK and self._tree_explainer_ok and hasattr(model, "estimators_"):
            try:
                explainer  = _shap.TreeExplainer(model)
                shap_vals  = explainer.shap_values(X)
                # 다중 클래스: list[n_classes] 또는 3D array (shap 버전 의존)
                if isinstance(shap_vals, list):
                    shap_vals = np.mean([np.abs(sv) for sv in shap_vals], axis=0)
                    imp = shap_vals.mean(axis=0)
                elif shap_vals.ndim == 3:
                    imp = np.abs(shap_vals).mean(axis=(0, 2))
                else:
                    imp = np.abs(shap_vals).mean(axis=0)
                # [312차] TreeExplainer는 다른 경로(2/3/4단계)와 달리 길이 검증이
                # 없었음 — X 컬럼수가 self._n_features와 다르면(호출부 버그로 잘못된
                # 폭의 X가 들어온 경우) 길이가 안 맞는 importance가 그대로
                # _current_importance에 저장되고, get_current_ranking()이
                # feature_names로 인덱싱할 때 IndexError로 죽는다.
                if len(imp) != self._n_features:
                    logger.warning(
                        "[SHAP] TreeExplainer 결과 길이 불일치: %d != %d (X.shape=%s) — skip",
                        len(imp), self._n_features, getattr(X, "shape", None),
                    )
                    self._tree_explainer_ok = False
                else:
                    return imp
            except Exception as e:
                _emsg = str(e)
                if "binary classification" in _emsg.lower():
                    # shap 0.41: GBM 다중 클래스 TreeExplainer 미지원 — 알려진 제한, 오류 아님
                    logger.info(
                        "[SHAP] GBM 다중 클래스: TreeExplainer 미지원 (shap %s) "
                        "→ per-class 트리 중요도로 전환 (1회 알림)",
                        _shap.__version__ if _SHAP_OK else "N/A",
                    )
                else:
                    logger.warning("[SHAP] TreeExplainer 실패: %s → per-class fallback", _emsg)
                self._tree_explainer_ok = False

        # ── 2) per-class 트리 중요도 (GBM 다중 클래스 실전 경로) ───
        # GBM 내부: estimators_[i][k] = DecisionTreeRegressor for class k
        # 각 클래스 전용 트리의 feature_importances_ 평균 → max across classes
        # 단순 global 평균 대비: 방향 신호를 가장 강하게 내는 피처를 누락하지 않음
        if (
            hasattr(model, "estimators_")
            and hasattr(model, "n_classes_")
            and int(getattr(model, "n_classes_", 1)) > 1
        ):
            try:
                n_cls    = int(model.n_classes_)
                n_trees  = len(model.estimators_)
                class_imps: List[np.ndarray] = []
                for k in range(n_cls):
                    fi_list = [
                        model.estimators_[i][k].feature_importances_
                        for i in range(n_trees)
                        if hasattr(model.estimators_[i][k], "feature_importances_")
                    ]
                    if fi_list and len(fi_list[0]) == self._n_features:
                        class_imps.append(np.mean(fi_list, axis=0))
                if len(class_imps) == n_cls:
                    imp = np.max(class_imps, axis=0)   # max: 어느 방향에서든 기여하면 포착
                    self._current_importance_by_class = class_imps
                    logger.debug(
                        "[SHAP] per-class 트리 중요도 (n_cls=%d, n_trees=%d)",
                        n_cls, n_trees,
                    )
                    return imp
            except Exception as e:
                logger.debug("[SHAP] per-class 트리 중요도 실패: %s", e)

        # ── 3) global feature_importances_ ─────────────────────────
        if hasattr(model, "feature_importances_"):
            imp = model.feature_importances_
            if len(imp) == self._n_features:
                return imp
            logger.warning(
                "[SHAP] feature_importances_ 길이 불일치: %d != %d",
                len(imp), self._n_features,
            )

        # ── 4) permutation_importance (최종 fallback, y 필요) ──────
        # [311차 후속9] HistGradientBoostingClassifier는 1~3 전부 구조적으로 실패
        # (estimators_/feature_importances_ 없음, shap 0.41 다중클래스 미지원) —
        # y(검증완료 실제 레이블)가 있을 때만 활성화되는 유일한 동작 경로.
        imp = _permutation_importance_fallback(model, X, y, self._n_features)
        if imp is not None:
            logger.debug("[SHAP] permutation_importance 경로 사용 (n=%d)", len(X))
            return imp

        logger.warning(
            "[SHAP] 중요도 계산 불가: SHAP=%s, feature_importances_=%s, "
            "permutation_importance=%s(y=%s)",
            _SHAP_OK, hasattr(model, "feature_importances_"),
            _PERM_IMP_OK, y is not None,
        )
        return None

    # ── 주간 심사 ─────────────────────────────────────────────────
    def weekly_review(self) -> dict:
        """
        주간 SHAP 심사 — 교체 추천 리포트 반환

        Returns:
            {
                rank_table:      현재 중요도 순위표
                declining:       하락 트렌드 피처 목록
                candidates:      교체 후보 (피처명, 추천 대체)
                core_safe:       CORE 피처 안전 여부
                replace_allowed: 교체 허용 여부 (쿨다운·일일 한도 확인)
            }
        """
        if self._current_importance is None:
            return {"error": "SHAP 데이터 없음"}
        if len(self._current_importance) != len(self.feature_names):
            return {"error": "SHAP importance/feature_names 길이 불일치"}

        # 현재 순위표
        rank_idx   = np.argsort(-self._current_importance)
        rank_table = [
            {
                "rank":       i + 1,
                "feature":    self.feature_names[rank_idx[i]],
                "importance": round(float(self._current_importance[rank_idx[i]]), 6),
                "is_core":    self.feature_names[rank_idx[i]] in CORE_FEATURES,
            }
            for i in range(len(rank_idx))
        ]

        # CORE 피처 순위 확인
        core_ranks = {}
        for entry in rank_table:
            if entry["is_core"]:
                core_ranks[entry["feature"]] = entry["rank"]

        # 하락 트렌드 감지 (최근 4주 추세)
        declining = self._find_declining_features()

        # 절대값 기준: 전체 평균의 30% 미만이면 declining 없어도 교체 후보
        mean_imp = float(np.mean(self._current_importance)) if self._current_importance is not None else 0.0
        low_imp_threshold = mean_imp * 0.3

        # 교체 후보 필터링 (CORE 제외, 하위 20%)
        bottom_n = max(5, int(len(rank_table) * 0.20))
        bottom = [e for e in reversed(rank_table) if not e["is_core"]][:bottom_n]
        candidates = []
        seen = set()
        already_suggested: set = set()
        for feat in bottom:
            if feat["feature"] in seen:
                continue
            is_declining = feat["feature"] in declining
            is_low_imp   = float(feat["importance"]) < low_imp_threshold
            if not (is_declining or is_low_imp):
                continue
            if is_declining:
                reason = "하락 트렌드 + 최하위"
            else:
                ratio = float(feat["importance"]) / (mean_imp + 1e-9)
                reason = f"기여도 미달 (avg의 {ratio*100:.0f}%)"
            replacement = self._suggest_replacement(feat["feature"], already_suggested)
            if replacement:
                already_suggested.add(replacement)
            candidates.append({
                "feature":     feat["feature"],
                "rank":        feat["rank"],
                "importance":  feat["importance"],
                "replacement": replacement,
                "reason":      reason,
            })
            seen.add(feat["feature"])
            if len(candidates) >= 3:
                break

        # 교체 허용 여부
        replace_allowed = self._check_replace_allowed()

        # 방향별 상위 피처 (per-class 경로에서만 유효)
        direction_top: dict = {}
        if self._current_importance_by_class is not None:
            _cls_labels = ["UP", "DN", "FL"]
            for k, label in enumerate(_cls_labels[:len(self._current_importance_by_class)]):
                _imp_k = self._current_importance_by_class[k]
                _top_idx = np.argsort(-_imp_k)[:3]
                direction_top[label] = [
                    {"feature": self.feature_names[i], "importance": round(float(_imp_k[i]), 6)}
                    for i in _top_idx
                ]

        report = {
            "rank_table":      rank_table[:15],  # 상위 15개만
            "core_ranks":      core_ranks,
            "declining":       declining,
            "candidates":      candidates,
            "replace_allowed": replace_allowed,
            "direction_top":   direction_top,    # 방향별 상위 3개 (per-class 경로만)
            "note":            "⚠️ 교체는 반드시 인간 검토 후 수동 적용",
        }

        now = datetime.datetime.now()
        _review_interval = datetime.timedelta(minutes=30)
        if (self._last_review_log_ts is None
                or (now - self._last_review_log_ts) >= _review_interval):
            logger.info(
                "[SHAP] 주간 심사 완료 | "
                "하락피처=%d개 | 교체후보=%d개 | CORE안전=%s%s",
                len(declining), len(candidates),
                "✅" if len(core_ranks) == 3 else "⚠️",
                " | 방향별분석=ON" if direction_top else "",
            )
            self._last_review_log_ts = now
        else:
            logger.debug(
                "[SHAP] 주간 심사 (하락=%d, 후보=%d)",
                len(declining), len(candidates),
            )
        return report

    def _find_declining_features(self) -> List[str]:
        """최근 4주(주별 deduplicate) 중요도 순위 하락 피처 감지.

        조건: 4회 중 3회 이상 하락 (기존 4회 연속에서 완화 — 노이즈 1회 허용)
        """
        # 주별 중복 제거: 같은 week는 마지막 엔트리만 사용
        seen_weeks: dict = {}
        for h in self._history:
            w = tuple(h.get("week") or [])
            if w:
                seen_weeks[w] = h
        deduped = sorted(seen_weeks.values(), key=lambda h: h.get("timestamp", ""))

        if len(deduped) < 4:
            return []

        recent4 = [
            h for h in deduped[-4:]
            if len(np.array(h.get("importance") or [])) == self._n_features
        ]
        if len(recent4) < 4:
            return []

        declining = []
        for i, fname in enumerate(self.feature_names):
            if fname in CORE_FEATURES:
                continue
            ranks = []
            for h in recent4:
                imp   = np.array(h["importance"])
                order = np.argsort(-imp)
                matched = np.where(order == i)[0]
                if len(matched) == 0:
                    ranks = []
                    break
                ranks.append(int(matched[0]) + 1)

            # 4회 중 3회 이상 하락 (연속 불요 — 노이즈 1회 허용)
            if len(ranks) == 4:
                drop_count = sum(ranks[j] < ranks[j + 1] for j in range(3))
                if drop_count >= 3:
                    declining.append(fname)

        return declining

    def _suggest_replacement(self, current_feat: str, already_suggested: Optional[set] = None) -> Optional[str]:
        """현재 피처의 교체 후보 반환 (DYNAMIC_FEATURES_POOL에서, 중복 제외)"""
        used = set(self.feature_names)
        if already_suggested:
            used |= already_suggested
        pool = [f for f in DYNAMIC_FEATURES_POOL if f not in used]
        return pool[0] if pool else None

    def _check_replace_allowed(self) -> dict:
        today = datetime.date.today()

        # 쿨다운 확인
        if self._last_replace:
            days_since = (today - self._last_replace).days
            if days_since < SHAP_COOLDOWN_DAYS:
                return {
                    "allowed": False,
                    "reason":  f"쿨다운 중 ({days_since}/{SHAP_COOLDOWN_DAYS}일)",
                }

        # 일일 한도 확인
        today_str = today.isoformat()
        today_count = sum(
            1 for r in self._replace_log
            if r.get("date") == today_str
        )
        if today_count >= SHAP_MAX_REPLACE_DAILY:
            return {
                "allowed": False,
                "reason":  f"일일 한도 초과 ({today_count}/{SHAP_MAX_REPLACE_DAILY})",
            }

        return {"allowed": True, "reason": "교체 가능"}

    def record_replacement(self, old_feat: str, new_feat: str, reason: str = ""):
        """피처 교체 이력 기록 (수동 교체 후 호출)"""
        today = datetime.date.today()
        self._replace_log.append({
            "date":     today.isoformat(),
            "old":      old_feat,
            "new":      new_feat,
            "reason":   reason,
        })
        self._last_replace = today
        logger.info(f"[SHAP] 교체 기록: {old_feat} → {new_feat}")
        self._save_history()

    # ── 영속화 ────────────────────────────────────────────────────
    def _save_history(self):
        try:
            path = SHAP_DB.replace(".db", "_history.json")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            data = {
                "history":     list(self._history),
                "replace_log": self._replace_log,
                "last_replace": self._last_replace.isoformat() if self._last_replace else None,
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.debug(f"[SHAP] 저장 오류: {e}")

    def _load_history(self):
        try:
            path = SHAP_DB.replace(".db", "_history.json")
            if not os.path.exists(path):
                return
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # 주별 dedup: 같은 week는 마지막(최신) 엔트리만 보존
            seen_weeks: dict = {}
            skipped = 0
            for h in data.get("history", []):
                imp = np.array(h.get("importance") or [])
                if len(imp) != self._n_features:
                    skipped += 1
                    continue
                w = tuple(h.get("week") or [])
                if w:
                    seen_weeks[w] = h  # 같은 주 → 뒤에 나온 것(최신)으로 덮음
            if skipped:
                logger.warning(
                    "[SHAP] 히스토리 %d개 항목 길이 불일치로 skip (저장=%d, 현재 n_features=%d)"
                    " — 다음 update() 호출 시 재계산됨",
                    skipped,
                    skipped and len(np.array(data["history"][0].get("importance") or [])),
                    self._n_features,
                )
            for h in sorted(seen_weeks.values(), key=lambda x: x.get("timestamp", "")):
                self._history.append(h)
            self._replace_log = data.get("replace_log", [])
            lr = data.get("last_replace")
            if lr:
                self._last_replace = datetime.date.fromisoformat(lr)
            if self._history:
                self._current_importance = np.array(self._history[-1]["importance"])
            logger.debug(f"[SHAP] 히스토리 로드: {len(self._history)}주차")
        except Exception as e:
            logger.debug(f"[SHAP] 로드 오류: {e}")

    def get_current_ranking(self) -> List[dict]:
        if self._current_importance is None:
            return []
        if len(self._current_importance) != self._n_features:
            logger.warning(
                "[SHAP] _current_importance 길이 불일치: %d != %d — ranking skip",
                len(self._current_importance), self._n_features,
            )
            return []
        idx = np.argsort(-self._current_importance)
        return [
            {"rank": i+1, "feature": self.feature_names[idx[i]],
             "importance": round(float(self._current_importance[idx[i]]), 6)}
            for i in range(len(idx))
        ]

    def get_class_ranking(self, class_labels: Optional[List[str]] = None) -> List[dict]:
        """방향별(UP/DN/FL) 피처 중요도 순위 반환.

        per-class 트리 중요도 경로에서만 유효.
        class_labels: ['UP', 'DN', 'FL'] 등 클래스 이름 (없으면 class_0/1/2 사용).
        Returns list of {feature, class_0_imp, class_1_imp, ..., max_imp, max_class}
        """
        if self._current_importance_by_class is None:
            return []
        n_cls    = len(self._current_importance_by_class)
        labels   = class_labels or ["class_%d" % k for k in range(n_cls)]
        labels   = labels[:n_cls]
        n_feat   = self._n_features
        rows = []
        idx  = np.argsort(-self._current_importance)
        for i in idx:
            row = {
                "rank":      int(i) + 1,
                "feature":   self.feature_names[i],
            }
            imp_vals = [float(self._current_importance_by_class[k][i]) for k in range(n_cls)]
            for k, label in enumerate(labels):
                row[label] = round(imp_vals[k], 6)
            row["max_imp"]   = round(max(imp_vals), 6)
            row["max_class"] = labels[int(np.argmax(imp_vals))]
            rows.append(row)
        return rows

    def get_recent_ranks(self, feature: str, lookback: int = 4) -> List[int]:
        if feature not in self.feature_names:
            return []
        if not self._history:
            return []

        # 주별 dedup 후 최근 lookback개 사용 (매분 중복 제거)
        seen_weeks: dict = {}
        for h in self._history:
            w = tuple(h.get("week") or [])
            if w:
                seen_weeks[w] = h
        deduped = sorted(seen_weeks.values(), key=lambda h: h.get("timestamp", ""))
        recent = deduped[-max(int(lookback), 1):]

        feat_idx = self.feature_names.index(feature)
        ranks = []
        for hist in recent:
            imp = np.array(hist.get("importance") or [])
            if len(imp) != self._n_features:
                continue
            order = np.argsort(-imp)
            found = np.where(order == feat_idx)[0]
            if len(found) == 0:
                continue
            ranks.append(int(found[0]) + 1)
        return ranks

    def get_replace_state(self) -> dict:
        state = dict(self._check_replace_allowed())
        today = datetime.date.today()
        days_since = None
        cooldown_progress = 0
        if self._last_replace:
            days_since = (today - self._last_replace).days
            cooldown_progress = int(
                min(100, max(0, (days_since / max(SHAP_COOLDOWN_DAYS, 1)) * 100))
            )
        state["last_replace"] = self._last_replace.isoformat() if self._last_replace else None
        state["days_since_last"] = days_since
        state["cooldown_progress"] = cooldown_progress
        return state

    def get_replace_log(self, limit: int = 10) -> List[dict]:
        if limit <= 0:
            return []
        return list(self._replace_log)[-int(limit):]


def compute_horizon_importance(
    model, X: np.ndarray, y: np.ndarray, feature_names: List[str],
) -> Optional[Dict[str, float]]:
    """[311차 후속9] 단발성 호라이즌별 중요도 계산 — ShapTracker의 주간 히스토리/
    교체추천 상태(_history, weekly_review 등)와 완전히 분리된 순수 계산 함수.

    현재 ShapTracker는 1m 전용 단일 인스턴스로 대시보드·SHAP 심사·후보교체 로직에
    깊이 얽혀 있어(main.py: _pick_shap_candidate 등), 3m/5m을 같은 인스턴스에
    update() 하면 매분 서로 다른 호라이즌 데이터로 _current_importance/_history를
    덮어써 그 로직들을 오염시킨다. 이 함수는 상태 없이 DB 관측용 스냅샷만 계산해
    save_shap_scores()로 직접 저장하는 용도 — 1m 주간심사 체계와 별개.
    """
    n_features = len(feature_names)
    if n_features == 0 or len(X) == 0:
        return None
    # [414차 후속] 이름 배열이 모델 입력 차원과 어긋나면 계산 자체를 하지 않는다.
    # 아래 zip()은 길이가 다르면 **조용히 짧은 쪽에서 잘려** 값이 엉뚱한 이름에 붙는데,
    # 그게 정확히 06-17~07-10 22거래일 오염의 실패 유형이다(414차).
    _n_in = getattr(model, "n_features_in_", None)
    if _n_in is not None and int(_n_in) != n_features:
        logger.warning(
            "[SHAP] compute_horizon_importance 스킵: feature_names %d개 != "
            "모델 입력 %d개 (414차 이름-값 정렬 가드)", n_features, int(_n_in),
        )
        return None
    imp = _permutation_importance_fallback(model, X, y, n_features)
    if imp is None and hasattr(model, "feature_importances_"):
        fi = model.feature_importances_
        if len(fi) == n_features:
            imp = np.asarray(fi, dtype=float)
    if imp is None:
        return None
    if len(imp) != n_features:
        logger.warning(
            "[SHAP] compute_horizon_importance 스킵: 중요도 %d개 != 이름 %d개",
            len(imp), n_features,
        )
        return None
    return {name: float(val) for name, val in zip(feature_names, imp)}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from config.constants import CORE_FEATURES, DYNAMIC_FEATURES_POOL

    feat_names = CORE_FEATURES + DYNAMIC_FEATURES_POOL[:10]
    tracker    = ShapTracker(feat_names)

    # 더미 중요도 주입
    dummy_imp = np.random.rand(len(feat_names))
    dummy_imp[:3] = [0.5, 0.4, 0.3]  # CORE 높게 설정
    tracker._current_importance = dummy_imp
    tracker._history.append({"week": (2026, 17), "importance": dummy_imp.tolist(),
                              "n_samples": 500, "timestamp": "2026-04-26T09:00:00"})

    report = tracker.weekly_review()
    print(f"상위 5 피처:")
    for r in report["rank_table"][:5]:
        core = "⭐CORE" if r["is_core"] else ""
        print(f"  {r['rank']}위 {r['feature']:<30} {r['importance']:.4f} {core}")
    print(f"교체 후보: {report['candidates']}")
    print(f"교체 허용: {report['replace_allowed']}")
