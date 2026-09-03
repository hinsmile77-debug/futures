# challenger/challenger_registry.py — 도전자 등록 및 챔피언 관리
"""
ChallengerRegistry: 도전자 인스턴스 풀 + 레짐별 챔피언 포인터 관리.

레짐 전문가 풀 (REGIME_POOLS):
  추세장 / 횡보장 / 혼합  → CHAMPION_BASELINE  (기존 앙상블)
  급변장                  → []  진입 금지
  탈진                    → [A_CVD, C_VWAP, D_EXHAUSTION]  전문가 풀

레짐 챔피언 (실거래 권한):
  _regime_champions[regime] = 해당 레짐에서 현재 실거래를 담당하는 challenger_id
  탈진 레짐은 최초에 None → 전문가 풀 내 성과 1위가 자동으로 Shadow 1위가 되고
  사용자 수동 승인 후 실거래 챔피언이 됨.

🔴 [MW0602 526차 후속8] 탈진 풀은 **순환 잠금** 상태다 (2026-09-03 조사보고 §9).
  승격에 필요한 것은 `REGIME_SPECIALIST_CRITERIA.min_regime_trades = 50`(레짐 내 거래 수)
  인데, 레짐 거래가 생기려면 ⓐ 미시레짐 「탈진」이 켜져야 하고 → ⓑ 켜져도
  `main.py` RegimeChampGate 가 champion=None 을 이유로 진입을 막는다 → ⓒ 챔피언이
  되려면 다시 레짐 거래 50건이 필요하다.
  실측: `A_CVD_EXHAUSTION`·`D_EXHAUSTION_REGIME` 은 27,463분 전부 direction=0
  (입력 `bear/bull_exhaustion` 이 상수 0.0) · `challenger_regime_metrics` 0행 ·
  `champion_history` 0행. 소진 피처를 live 로 돌려도 탈진 레짐 발생률이
  0.45분/일이라 50건은 **수년** 스케일이다.
  ⇒ 유지 비용은 0이므로 그대로 둔다. 승격 기준 재정의(레짐 분 → 섀도 거래)는
    **정책 변경**이라 `EXHAUSTION_RESTORE_MODE` live 안건에 묶는다.
"""
import logging
from typing import Dict, List, Optional

from challenger.variants.base_challenger import BaseChallenger

logger = logging.getLogger("CHALLENGER")

CHAMPION_BASELINE_ID = "CHAMPION_BASELINE"

# 레짐별 전문가 풀 정의
REGIME_POOLS = {
    "추세장": [CHAMPION_BASELINE_ID],
    "횡보장": [CHAMPION_BASELINE_ID],
    "혼합":   [CHAMPION_BASELINE_ID],
    "급변장": [],   # 진입 금지
    "탈진":   ["A_CVD_EXHAUSTION", "C_VWAP_REVERSAL", "D_EXHAUSTION_REGIME"],
}

# 레짐별 초기 챔피언 (실거래 담당)
_DEFAULT_REGIME_CHAMPIONS = {
    "추세장": CHAMPION_BASELINE_ID,
    "횡보장": CHAMPION_BASELINE_ID,
    "혼합":   CHAMPION_BASELINE_ID,
    "급변장": None,
    "탈진":   None,   # 전문가 관찰 후 수동 승격 전까지 실거래 없음
}


class ChallengerRegistry(object):
    """
    도전자 등록 / 레짐별 챔피언 지정 / 활성 도전자 목록 반환.
    """

    def __init__(self):
        self._challengers = {}        # type: Dict[str, BaseChallenger]

        # 레짐별 챔피언 (실거래 담당자)
        self._regime_champions = dict(_DEFAULT_REGIME_CHAMPIONS)

        # 레짐별 현재 Shadow 1위 (실거래 권한 없음, 표시용)
        self._regime_shadow_rank1 = {}  # type: Dict[str, Optional[str]]

    # ── 도전자 등록/해제 ─────────────────────────────────────────

    def register(self, challenger):
        # type: (BaseChallenger) -> None
        cid = challenger.challenger_id
        if not cid:
            raise ValueError("challenger_id 가 비어 있습니다.")
        self._challengers[cid] = challenger
        logger.info("[Registry] 도전자 등록: %s (%s)", cid, challenger.name_kr)

    def unregister(self, challenger_id):
        # type: (str) -> None
        if challenger_id in self._challengers:
            del self._challengers[challenger_id]
            logger.info("[Registry] 도전자 해제: %s", challenger_id)

    # ── 도전자 목록 조회 ─────────────────────────────────────────

    def active_challengers(self):
        # type: () -> List[BaseChallenger]
        """active=True 인 모든 도전자 (레짐별 챔피언 포함)"""
        return [c for c in self._challengers.values() if c.active]

    def all_challengers(self):
        # type: () -> List[BaseChallenger]
        return list(self._challengers.values())

    def get(self, challenger_id):
        # type: (str) -> Optional[BaseChallenger]
        return self._challengers.get(challenger_id)

    def ids(self):
        # type: () -> List[str]
        return list(self._challengers.keys())

    def set_active(self, challenger_id, active):
        # type: (str, bool) -> None
        c = self._challengers.get(challenger_id)
        if c:
            c.active = active
            logger.info("[Registry] %s active=%s", challenger_id, active)

    # ── 레짐별 챔피언 관리 ───────────────────────────────────────

    def get_regime_champion(self, regime):
        # type: (str) -> Optional[str]
        """레짐의 현재 실거래 챔피언 ID (없으면 None)"""
        return self._regime_champions.get(regime)

    def set_regime_champion(self, regime, challenger_id):
        # type: (str, Optional[str]) -> None
        """레짐 챔피언 설정 (수동 승격 시 호출)"""
        old = self._regime_champions.get(regime)
        self._regime_champions[regime] = challenger_id
        logger.info("[Registry] 레짐 챔피언 변경 [%s]: %s → %s",
                    regime, old, challenger_id)

    def get_regime_pool(self, regime):
        # type: (str) -> List[str]
        """레짐 전문가 풀 ID 목록"""
        return list(REGIME_POOLS.get(regime, []))

    def get_all_regime_champions(self):
        # type: () -> Dict[str, Optional[str]]
        return dict(self._regime_champions)

    # ── 레짐 Shadow 1위 추적 (WARNING 판단용) ────────────────────

    def update_regime_shadow_rank1(self, regime, rank1_id):
        # type: (str, Optional[str]) -> bool
        """
        레짐 Shadow 1위 갱신.

        Returns:
            True = 순위 변경 발생 (WARNING 필요)
        """
        prev = self._regime_shadow_rank1.get(regime)
        self._regime_shadow_rank1[regime] = rank1_id
        changed = (prev is not None) and (prev != rank1_id)
        if changed:
            logger.info("[Registry] 레짐 Shadow 1위 변경 [%s]: %s → %s",
                        regime, prev, rank1_id)
        return changed

    def get_regime_shadow_rank1(self, regime):
        # type: (str) -> Optional[str]
        return self._regime_shadow_rank1.get(regime)

    # ── 하위 호환 (기존 단일 챔피언 API) ─────────────────────────

    def get_champion_id(self):
        # type: () -> str
        """전역 챔피언 ID (레짐 무관, 대부분 CHAMPION_BASELINE)"""
        return self._regime_champions.get("혼합", CHAMPION_BASELINE_ID) or CHAMPION_BASELINE_ID

    def set_champion(self, challenger_id):
        # type: (str) -> None
        """전역 챔피언 설정 (비-탈진 레짐 전체 동시 변경)"""
        for regime in ("추세장", "횡보장", "혼합"):
            self._regime_champions[regime] = challenger_id
        logger.info("[Registry] 전역 챔피언 → %s", challenger_id)
