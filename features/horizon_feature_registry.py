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


# ── [MW0601 458차 / P2-C] 만성 제외 추적 ─────────────────────────────────────
# 계측 4원칙 ③(탈락 가시화)의 시간축 확장. 457차 C6이 "몇 개가 빠졌는지"를 정직하게
# 만들었다면, 여기는 "얼마나 오래 빠져 있었는지"를 드러낸다.
#
# 왜 필요한가: 292차("need_add 8개 방치 발견")·411차("pkl 표기 11건 전부 need_add로
# 정정")·458차가 **같은 제외를 세 번 독립적으로 발견**했다. 매번 그날 처음 생긴
# 일처럼 보였기 때문이다. 실측하면 opt_chain_pcr은 수집이 시작된 2026-07-15부터
# 한 번도 학습에 들어간 적이 없다.
#
# 상태 파일은 data/(gitignore 대상)에 둔다 — PC별 런타임 산출물이므로 커밋하지
# 않는다(feedback_git_commit_scope). 파일이 없으면 "오늘 처음 관측"으로 시작하며,
# 그 경우 일수를 단정하지 않고 `최초관측`으로 표기한다(미측정 ≠ 0 — 계측 4원칙 ②).
_CHRONIC_PATH = os.path.normpath(os.path.join(
    os.path.dirname(__file__), "..", "data", "feature_exclusion_state.json",
))
_CHRONIC_CACHE: Optional[Dict] = None


def _chronic_suffix(horizon: str, missing: List[str]) -> str:
    """제외 피처의 '연속 제외 거래일수' 요약 문자열 (실패 시 빈 문자열).

    로그 보조 계측이므로 어떤 예외도 호출부로 전파하지 않는다 — 이 함수가
    학습을 막는 일은 없어야 한다.
    """
    global _CHRONIC_CACHE
    try:
        import datetime as _dt
        today = _dt.date.today().isoformat()
        if _CHRONIC_CACHE is None:
            try:
                with open(_CHRONIC_PATH, encoding="utf-8") as f:
                    _CHRONIC_CACHE = json.load(f)
            except (IOError, OSError, ValueError):
                _CHRONIC_CACHE = {}
        state = _CHRONIC_CACHE.setdefault(horizon, {})
        spans = []
        for name in missing:
            rec = state.get(name)
            if not isinstance(rec, dict) or "first_seen" not in rec:
                state[name] = {"first_seen": today, "last_seen": today, "days": 1}
                spans.append((name, None))
                continue
            if rec.get("last_seen") != today:
                rec["days"] = int(rec.get("days", 1)) + 1
                rec["last_seen"] = today
            spans.append((name, int(rec.get("days", 1))))
        # 다시 가용해진 피처는 상태에서 제거 — 연속성이 끊기면 일수도 끊긴다.
        for gone in [k for k in state if k not in set(missing)]:
            state.pop(gone, None)
        try:
            os.makedirs(os.path.dirname(_CHRONIC_PATH), exist_ok=True)
            with open(_CHRONIC_PATH, "w", encoding="utf-8") as f:
                json.dump(_CHRONIC_CACHE, f, ensure_ascii=False, indent=1)
        except (IOError, OSError):
            pass  # 기록 못 해도 로그는 남긴다
        known = [(n, d) for n, d in spans if d is not None]
        if not known:
            return " | 만성도: 최초관측(기준일 %s)" % today
        worst = max(known, key=lambda x: x[1])
        if worst[1] < 2:
            return " | 만성도: 최초관측(기준일 %s)" % today
        return " | 만성도: 최장 %s %d거래일째 제외" % (worst[0], worst[1])
    except Exception:
        return ""


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
        # [MW0601 457차 / C6] 종전 `missing[:5]`는 절단 표식이 없어 "7개 미가용"이라
        # 적어놓고 5개만 보여줬다(2026-08-11 30m 실측). 운영자가 "7개 = 나열된 5개"로
        # 오독하고, 하필 30m은 opt_chain_pcr(절대원칙 §3 장기 CORE)의 지위를 F9로
        # 심사 중인 호라이즌이라 은닉된 2개가 판단을 직접 왜곡한다.
        # → 계측 3원칙 G3-A③ "탈락 가시화": 전량 출력하고, 길면 잔여 개수를 명시한다.
        _shown = missing if len(missing) <= 12 else missing[:12]
        _tail  = "" if len(missing) <= 12 else " 외 %d개" % (len(missing) - 12)
        # [MW0601 458차 / P2-C] 만성 여부 병기. 292차·411차·458차가 **같은 제외를
        # 세 번 독립적으로 "발견"** 했다 — 매번 하루짜리 이벤트처럼 보였기 때문이다.
        # 실제로는 opt_chain_pcr이 수집 시작(2026-07-15) 이래 계속 제외돼 있었다.
        # 원인은 수집 실패가 아니라 feature_names.pkl 97개 동결(batch_retrainer.py
        # use_feat_names)이며, 푸는 절차는 P2-B로 별도 등록됐다.
        logger.info(
            "[FeatureReg] %s: %d개 피처 미가용 (need_add) → 제외: %s%s%s",
            horizon, len(missing), _shown, _tail,
            _chronic_suffix(horizon, missing),
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
