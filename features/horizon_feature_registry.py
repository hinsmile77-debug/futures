# features/horizon_feature_registry.py
"""
호라이즌별 피처셋 레지스트리.

horizon_feature_sets.json을 읽어 각 호라이즌에 사용할 피처명 목록을 반환한다.
Phase C: batch_retrainer(학습 시 X 슬라이싱) + multi_horizon_model(추론 시 슬라이싱) 에서 사용.

backward compat: JSON 미존재 또는 horizon 미등록 시 None 반환 → 호출부에서 전체 피처셋 fallback.
"""

import json
import logging
import os
from typing import Dict, List, Optional, Set

logger = logging.getLogger("FEAT_REG")

_JSON_PATH = os.path.join(
    os.path.dirname(__file__),
    "..", "featureset by horizon", "horizon_feature_sets.json",
)
_JSON_PATH = os.path.normpath(_JSON_PATH)

_HORIZONS = ["1m", "3m", "5m", "10m", "15m", "30m"]

# 모듈 로드 시 캐시 — 런타임 중 파일 변경 반영은 reload_registry() 호출
_REGISTRY: Optional[Dict] = None


def _load_json() -> Optional[Dict]:
    global _REGISTRY
    if not os.path.exists(_JSON_PATH):
        logger.warning("[FeatureReg] JSON 미존재: %s — 단일 피처셋 fallback", _JSON_PATH)
        return None
    try:
        with open(_JSON_PATH, encoding="utf-8") as f:
            data = json.load(f)
        _REGISTRY = data
        logger.debug("[FeatureReg] JSON 로드 완료 (%s)", _JSON_PATH)
        return data
    except Exception as e:
        logger.warning("[FeatureReg] JSON 파싱 오류: %s — 단일 피처셋 fallback", e)
        return None


def _registry() -> Optional[Dict]:
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = _load_json()
    return _REGISTRY


def reload_registry() -> bool:
    """JSON 재로드 (런타임 갱신용). 성공 시 True."""
    global _REGISTRY
    _REGISTRY = None
    result = _load_json()
    return result is not None


# ──────────────────────────────────────────────────────────────
# 공개 API
# ──────────────────────────────────────────────────────────────

def get_feature_set(horizon: str, include_pending: bool = False) -> Optional[List[str]]:
    """horizon에 대한 include 피처 목록 반환.

    Args:
        horizon:         "1m" / "3m" / "5m" / "10m" / "15m" / "30m"
        include_pending: True면 include_pending_validation 항목도 포함

    Returns:
        피처명 리스트 (중복 없음, 순서 보존).
        JSON 미존재 또는 horizon 미등록 시 None (호출부 fallback 처리).
    """
    reg = _registry()
    if reg is None or horizon not in reg:
        return None

    cfg = reg[horizon]
    names: List[str] = []
    seen: Set[str] = set()

    for entry in cfg.get("include", []):
        n = entry.get("name")
        if n and n not in seen:
            names.append(n)
            seen.add(n)

    if include_pending:
        for entry in cfg.get("include_pending_validation", []):
            n = entry.get("name")
            if n and n not in seen:
                names.append(n)
                seen.add(n)

    return names if names else None


def get_available_feature_set(
    horizon: str,
    all_feature_names: List[str],
    include_pending: bool = False,
) -> Optional[List[str]]:
    """horizon 피처셋에서 all_feature_names에 실제 존재하는 것만 반환.

    학습 시 X에 없는 'need_add' 피처를 자동으로 걸러낸다.
    반환값이 None이거나 2개 미만이면 호출부에서 전체 피처셋 fallback.
    """
    desired = get_feature_set(horizon, include_pending=include_pending)
    if desired is None:
        return None

    available_set = set(all_feature_names)
    selected = [f for f in desired if f in available_set]

    if len(selected) < 2:
        logger.warning(
            "[FeatureReg] %s: 가용 피처 %d개 (요구 %d개) — 전체 피처셋 fallback",
            horizon, len(selected), len(desired),
        )
        return None

    missing = [f for f in desired if f not in available_set]
    if missing:
        logger.info(
            "[FeatureReg] %s: %d개 피처 미가용 (need_add) → 제외: %s",
            horizon, len(missing), missing[:5],
        )

    return selected


def get_exclude_set(horizon: str) -> Set[str]:
    """horizon에서 명시적으로 제거할 피처 집합."""
    reg = _registry()
    if reg is None or horizon not in reg:
        return set()
    return {e["name"] for e in reg[horizon].get("exclude", [])}


def get_all_needed_features() -> List[str]:
    """전체 호라이즌 include 피처의 합집합 (중복 제거, 순서 보존).

    전체 학습 X에 포함되어야 할 피처 후보 목록.
    """
    reg = _registry()
    if reg is None:
        return []
    seen: Set[str] = set()
    result: List[str] = []
    for h in _HORIZONS:
        cfg = reg.get(h, {})
        for key in ("include", "include_pending_validation"):
            for entry in cfg.get(key, []):
                n = entry.get("name")
                if n and n not in seen:
                    result.append(n)
                    seen.add(n)
    return result


def get_need_add_features() -> List[str]:
    """pkl_status='need_add'인 피처 목록 (전체 호라이즌 합집합).

    Phase C 진행 상황 확인용.
    """
    reg = _registry()
    if reg is None:
        return []
    seen: Set[str] = set()
    result: List[str] = []
    for h in _HORIZONS:
        cfg = reg.get(h, {})
        for entry in cfg.get("include", []):
            if entry.get("pkl") == "need_add":
                n = entry.get("name")
                if n and n not in seen:
                    result.append(n)
                    seen.add(n)
    return result


def get_registry_info() -> Dict:
    """레지스트리 요약 정보 (로깅/디버깅용)."""
    reg = _registry()
    if reg is None:
        return {"loaded": False}
    info = {"loaded": True, "horizons": {}}
    for h in _HORIZONS:
        cfg = reg.get(h, {})
        inc = cfg.get("include", [])
        pend = cfg.get("include_pending_validation", [])
        in_pkl = sum(1 for e in inc if e.get("pkl") == "in_pkl")
        need_add = sum(1 for e in inc if e.get("pkl") == "need_add")
        info["horizons"][h] = {
            "include": len(inc),
            "in_pkl": in_pkl,
            "need_add": need_add,
            "pending": len(pend),
            "current_acc": cfg.get("current_acc"),
            "target_acc": cfg.get("target_acc"),
        }
    return info
