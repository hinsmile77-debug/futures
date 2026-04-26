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

from config.constants import CORE_FEATURES, DYNAMIC_FEATURES_POOL
from config.settings import (
    SHAP_COOLDOWN_DAYS, SHAP_MAX_REPLACE_DAILY,
    SHAP_RANK_IMPROVE_MIN, SHAP_MIN_DATA_POINTS, SHAP_DB,
)

logger = logging.getLogger("SHAP")


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

        self._load_history()

    # ── SHAP 계산 ─────────────────────────────────────────────────
    def update(self, model, X: np.ndarray, sample_size: int = 500):
        """
        모델과 최근 데이터로 SHAP 중요도 계산 후 히스토리 추가

        Args:
            model:       학습된 GBM 모델 (sklearn)
            X:           최근 N개 분봉 피처 행렬
            sample_size: SHAP 계산 샘플 수 (속도 제어)
        """
        if len(X) < SHAP_MIN_DATA_POINTS:
            logger.debug(f"[SHAP] 데이터 부족 ({len(X)} < {SHAP_MIN_DATA_POINTS})")
            return

        # 샘플링
        idx = np.random.choice(len(X), min(sample_size, len(X)), replace=False)
        X_s = X[idx]

        importance = self._calc_importance(model, X_s)
        if importance is None:
            return

        self._current_importance = importance
        self._history.append({
            "week":       datetime.date.today().isocalendar()[:2],  # (year, week)
            "importance": importance.tolist(),
            "n_samples":  len(X_s),
            "timestamp":  datetime.datetime.now().isoformat(),
        })
        self._save_history()
        logger.info(f"[SHAP] 중요도 갱신 완료 (n={len(X_s)})")

    def _calc_importance(self, model, X: np.ndarray) -> Optional[np.ndarray]:
        """SHAP TreeExplainer → fallback to feature_importances_"""
        if _SHAP_OK:
            try:
                explainer  = _shap.TreeExplainer(model)
                shap_vals  = explainer.shap_values(X)
                # 분류: shap_values[1] = positive class
                if isinstance(shap_vals, list):
                    shap_vals = shap_vals[1]
                return np.abs(shap_vals).mean(axis=0)
            except Exception as e:
                logger.debug(f"[SHAP] TreeExplainer 오류: {e}")

        # fallback
        if hasattr(model, "feature_importances_"):
            return model.feature_importances_

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

        # 교체 후보 필터링 (CORE 제외, 최하위 5개)
        bottom5 = [e for e in reversed(rank_table) if not e["is_core"]][:5]
        candidates = []
        for feat in bottom5:
            if feat["feature"] in declining:
                replacement = self._suggest_replacement(feat["feature"])
                candidates.append({
                    "feature":     feat["feature"],
                    "rank":        feat["rank"],
                    "importance":  feat["importance"],
                    "replacement": replacement,
                    "reason":      "하락 트렌드 + 최하위",
                })

        # 교체 허용 여부
        replace_allowed = self._check_replace_allowed()

        report = {
            "rank_table":      rank_table[:15],  # 상위 15개만
            "core_ranks":      core_ranks,
            "declining":       declining,
            "candidates":      candidates,
            "replace_allowed": replace_allowed,
            "note":            "⚠️ 교체는 반드시 인간 검토 후 수동 적용",
        }

        logger.info(
            f"[SHAP] 주간 심사 완료 | "
            f"하락피처={len(declining)}개 | 교체후보={len(candidates)}개 | "
            f"CORE안전={'✅' if len(core_ranks) == 3 else '⚠️'}"
        )
        return report

    def _find_declining_features(self) -> List[str]:
        """최근 4주 중요도 순위가 지속 하락한 피처"""
        if len(self._history) < 4:
            return []

        recent4 = list(self._history)[-4:]
        declining = []

        for i, fname in enumerate(self.feature_names):
            if fname in CORE_FEATURES:
                continue
            ranks = []
            for h in recent4:
                imp   = np.array(h["importance"])
                order = np.argsort(-imp)
                rank  = int(np.where(order == i)[0][0]) + 1
                ranks.append(rank)

            # 4주 연속 순위 하락
            if all(ranks[j] < ranks[j + 1] for j in range(len(ranks) - 1)):
                declining.append(fname)

        return declining

    def _suggest_replacement(self, current_feat: str) -> Optional[str]:
        """현재 피처의 교체 후보 반환 (DYNAMIC_FEATURES_POOL에서)"""
        used = set(self.feature_names)
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
            for h in data.get("history", []):
                self._history.append(h)
            self._replace_log = data.get("replace_log", [])
            lr = data.get("last_replace")
            if lr:
                self._last_replace = datetime.date.fromisoformat(lr)
            if self._history:
                self._current_importance = np.array(self._history[-1]["importance"])
        except Exception as e:
            logger.debug(f"[SHAP] 로드 오류: {e}")

    def get_current_ranking(self) -> List[dict]:
        if self._current_importance is None:
            return []
        idx = np.argsort(-self._current_importance)
        return [
            {"rank": i+1, "feature": self.feature_names[idx[i]],
             "importance": round(float(self._current_importance[idx[i]]), 6)}
            for i in range(len(idx))
        ]


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
