# collection/macro/regime_strategy_map.py — 레짐별 전략 매핑 ⭐v6.5
"""
매크로 레짐 × 미시 레짐 조합에 따라 전략 파라미터를 동적으로 매핑.

v6.5 핵심:
  단순 파라미터 조정이 아니라 전략 자체를 교체하는 수준의 분리.

매핑 테이블 (macro × micro):
  ┌──────────┬──────────────┬──────────────┬──────────────┬──────────────┐
  │          │   추세장     │   횡보장     │   급변장     │    혼합      │
  ├──────────┼──────────────┼──────────────┼──────────────┼──────────────┤
  │ RISK_ON  │ 추세추종(강) │ 역추세(보통) │ 방어적 축소  │ 표준 앙상블  │
  │ NEUTRAL  │ 추세추종(보) │ 역추세(약)   │ 거래 중단    │ 표준 앙상블  │
  │ RISK_OFF │ 추세추종(약) │ 역추세 금지  │ 강제 청산    │ 방어적       │
  └──────────┴──────────────┴──────────────┴──────────────┴──────────────┘
"""
from typing import Dict, Optional


# 전략 모드 상수
MODE_TREND_STRONG    = "추세추종_강"
MODE_TREND_NORMAL    = "추세추종_보통"
MODE_TREND_WEAK      = "추세추종_약"
MODE_COUNTER_NORMAL  = "역추세_보통"
MODE_COUNTER_WEAK    = "역추세_약"
MODE_STANDARD        = "표준앙상블"
MODE_DEFENSIVE       = "방어적"
MODE_REDUCE          = "사이즈_축소"
MODE_HALT            = "거래중단"
MODE_FORCE_EXIT      = "강제청산"


# 전략 파라미터 프로파일
# 각 모드별: {entry_threshold, size_mult, stop_mult, target_mult, max_hold_minutes}
STRATEGY_PROFILES: Dict[str, dict] = {
    MODE_TREND_STRONG: {
        "entry_threshold":  0.60,   # 낮은 진입 기준 (공격적)
        "size_multiplier":  1.3,
        "stop_multiplier":  1.2,    # 스탑 여유 (추세 지속 허용)
        "target_multiplier":1.5,
        "max_hold_minutes": 10,
        "description":      "RISK_ON × 추세장 — 공격적 추세추종",
    },
    MODE_TREND_NORMAL: {
        "entry_threshold":  0.62,
        "size_multiplier":  1.0,
        "stop_multiplier":  1.0,
        "target_multiplier":1.2,
        "max_hold_minutes": 7,
        "description":      "NEUTRAL × 추세장 — 표준 추세추종",
    },
    MODE_TREND_WEAK: {
        "entry_threshold":  0.65,   # 높은 진입 기준 (방어적)
        "size_multiplier":  0.7,
        "stop_multiplier":  0.8,    # 스탑 좁힘
        "target_multiplier":1.0,
        "max_hold_minutes": 5,
        "description":      "RISK_OFF × 추세장 — 방어적 추세추종",
    },
    MODE_COUNTER_NORMAL: {
        "entry_threshold":  0.63,
        "size_multiplier":  0.8,
        "stop_multiplier":  0.8,
        "target_multiplier":0.8,    # 역추세는 목표 작게
        "max_hold_minutes": 3,
        "description":      "RISK_ON × 횡보장 — 보통 역추세",
    },
    MODE_COUNTER_WEAK: {
        "entry_threshold":  0.68,
        "size_multiplier":  0.5,
        "stop_multiplier":  0.7,
        "target_multiplier":0.6,
        "max_hold_minutes": 2,
        "description":      "NEUTRAL × 횡보장 — 약한 역추세",
    },
    MODE_STANDARD: {
        "entry_threshold":  0.62,
        "size_multiplier":  1.0,
        "stop_multiplier":  1.0,
        "target_multiplier":1.0,
        "max_hold_minutes": 5,
        "description":      "표준 앙상블 모드",
    },
    MODE_DEFENSIVE: {
        "entry_threshold":  0.70,
        "size_multiplier":  0.5,
        "stop_multiplier":  0.7,
        "target_multiplier":0.8,
        "max_hold_minutes": 3,
        "description":      "방어적 모드 — 사이즈 축소, 기준 상향",
    },
    MODE_REDUCE: {
        "entry_threshold":  0.72,
        "size_multiplier":  0.3,
        "stop_multiplier":  0.6,
        "target_multiplier":0.7,
        "max_hold_minutes": 2,
        "description":      "급변장 — 사이즈 대폭 축소",
    },
    MODE_HALT: {
        "entry_threshold":  1.0,    # 사실상 진입 불가
        "size_multiplier":  0.0,
        "stop_multiplier":  0.5,
        "target_multiplier":0.5,
        "max_hold_minutes": 0,
        "description":      "거래 중단 — 신규 진입 금지",
    },
    MODE_FORCE_EXIT: {
        "entry_threshold":  1.0,
        "size_multiplier":  0.0,
        "stop_multiplier":  0.0,
        "target_multiplier":0.0,
        "max_hold_minutes": 0,
        "description":      "강제 청산 — 전 포지션 청산",
    },
}

# 레짐 조합 → 전략 모드 매핑 테이블
REGIME_STRATEGY_TABLE: Dict[str, Dict[str, str]] = {
    "RISK_ON": {
        "추세장":  MODE_TREND_STRONG,
        "횡보장":  MODE_COUNTER_NORMAL,
        "급변장":  MODE_REDUCE,
        "혼합":    MODE_STANDARD,
    },
    "NEUTRAL": {
        "추세장":  MODE_TREND_NORMAL,
        "횡보장":  MODE_COUNTER_WEAK,
        "급변장":  MODE_HALT,
        "혼합":    MODE_STANDARD,
    },
    "RISK_OFF": {
        "추세장":  MODE_TREND_WEAK,
        "횡보장":  MODE_DEFENSIVE,     # 역추세 금지 → 방어적
        "급변장":  MODE_FORCE_EXIT,
        "혼합":    MODE_DEFENSIVE,
    },
}


class RegimeStrategyMapper:
    """레짐 조합 → 전략 파라미터 동적 매핑"""

    def __init__(self):
        self._current_mode    = MODE_STANDARD
        self._current_profile = STRATEGY_PROFILES[MODE_STANDARD].copy()

    def get_strategy(
        self,
        macro_regime: str,   # "RISK_ON" / "NEUTRAL" / "RISK_OFF"
        micro_regime: str,   # "추세장" / "횡보장" / "급변장" / "혼합"
    ) -> dict:
        """
        레짐 조합으로 전략 파라미터 결정

        Returns:
            {mode, entry_threshold, size_multiplier, stop_multiplier,
             target_multiplier, max_hold_minutes, description, force_exit}
        """
        macro = macro_regime if macro_regime in REGIME_STRATEGY_TABLE else "NEUTRAL"
        micro = micro_regime if micro_regime in ["추세장", "횡보장", "급변장", "혼합"] else "혼합"

        mode    = REGIME_STRATEGY_TABLE[macro][micro]
        profile = STRATEGY_PROFILES[mode].copy()

        self._current_mode    = mode
        self._current_profile = profile

        return {
            "mode":              mode,
            "entry_threshold":   profile["entry_threshold"],
            "size_multiplier":   profile["size_multiplier"],
            "stop_multiplier":   profile["stop_multiplier"],
            "target_multiplier": profile["target_multiplier"],
            "max_hold_minutes":  profile["max_hold_minutes"],
            "description":       profile["description"],
            "force_exit":        (mode == MODE_FORCE_EXIT),
            "halt_new_entry":    (mode in (MODE_HALT, MODE_FORCE_EXIT)),
        }

    @property
    def current_mode(self) -> str:
        return self._current_mode

    @property
    def current_profile(self) -> dict:
        return self._current_profile.copy()

    def is_entry_allowed(self) -> bool:
        return self._current_profile.get("size_multiplier", 0) > 0

    def is_force_exit(self) -> bool:
        return self._current_mode == MODE_FORCE_EXIT


if __name__ == "__main__":
    mapper = RegimeStrategyMapper()

    test_cases = [
        ("RISK_ON",  "추세장"),
        ("RISK_ON",  "횡보장"),
        ("NEUTRAL",  "급변장"),
        ("RISK_OFF", "급변장"),
        ("RISK_OFF", "횡보장"),
        ("NEUTRAL",  "혼합"),
    ]

    print(f"{'매크로':<10} {'미시':<8} {'모드':<20} {'진입기준':<10} {'사이즈':<8} {'설명'}")
    print("-" * 100)
    for macro, micro in test_cases:
        s = mapper.get_strategy(macro, micro)
        print(f"{macro:<10} {micro:<8} {s['mode']:<20} {s['entry_threshold']:<10} "
              f"{s['size_multiplier']:<8} {s['description']}")
