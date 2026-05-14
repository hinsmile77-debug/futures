# strategy/entry/time_strategy_router.py — 시간대별 전략 라우터 ⭐v6.5
"""
장 중 시간대를 6구간으로 분류하고 구간별 전략 파라미터 반환

시간대 구간:
  GAP_OPEN       09:00~09:05 — 시초가 급변, 고신뢰·소규모 진입만 허용
  OPEN_VOLATILE  09:05~10:30 — 변동성 高, 추세추종, 신뢰도 기준 상향
  STABLE_TREND   10:30~11:50 — 안정 추세, 표준 앙상블
  LUNCH_RECOVERY 13:00~14:00 — 외인 재진입 감지, 신호 가중
  CLOSE_VOLATILE 14:00~15:00 — 마감 변동성, 추세 가속/청산
  EXIT_ONLY      15:00~15:10 — 신규 진입 금지
  OTHER          그 외 (점심 공백 등)

출력 파라미터:
  min_confidence  — 최소 신뢰도 (높을수록 까다로운 진입)
  size_mult       — 사이즈 배율
  strategy_mode   — "trend_follow" | "standard" | "foreign_watch" | "close_accel"
  allow_new_entry — 신규 진입 허용 여부
"""
import datetime
import logging
from typing import Dict, Optional

from config.settings import TIME_ZONES
from utils.time_utils import now_kst, days_to_monthly_expiry, is_fomc_day

logger = logging.getLogger("SIGNAL")

# ── 시간대별 파라미터 ─────────────────────────────────────────────
_ZONE_PARAMS: Dict[str, dict] = {
    "GAP_OPEN": {
        "min_confidence":  0.67,      # 시초가 급변 → 고신뢰 신호만 허용
        "size_mult":       0.5,        # 슬리피지·갭 리스크 대비 소규모
        "strategy_mode":  "trend_follow",
        "allow_new_entry": True,
        "desc":            "시초가 급변 — 고신뢰·소규모 진입만 허용",
    },
    "OPEN_VOLATILE": {
        "min_confidence":  0.63,      # 신뢰도 기준 상향 (변동성 큰 구간)
        "size_mult":       0.8,        # 사이즈 보수적
        "strategy_mode":  "trend_follow",
        "allow_new_entry": True,
        "desc":            "개장 변동성 — 추세추종, 신뢰도↑",
    },
    "STABLE_TREND": {
        "min_confidence":  0.58,
        "size_mult":       1.0,
        "strategy_mode":  "standard",
        "allow_new_entry": True,
        "desc":            "안정 추세 — 표준 앙상블",
    },
    "LUNCH_RECOVERY": {
        "min_confidence":  0.60,
        "size_mult":       0.9,
        "strategy_mode":  "foreign_watch",   # 외인 재진입 감지 우선
        "allow_new_entry": True,
        "desc":            "점심 후 외인 재진입 — 외인 신호 가중",
    },
    "CLOSE_VOLATILE": {
        "min_confidence":  0.62,
        "size_mult":       0.7,        # 마감 리스크 → 사이즈 축소
        "strategy_mode":  "close_accel",
        "allow_new_entry": True,
        "desc":            "마감 변동성 — 추세 가속/청산 구간",
    },
    "EXIT_ONLY": {
        "min_confidence":  1.0,        # 사실상 진입 불가
        "size_mult":       0.0,
        "strategy_mode":  "exit_only",
        "allow_new_entry": False,
        "desc":            "신규 진입 금지 — 청산만 허용",
    },
    "OTHER": {
        "min_confidence":  0.65,
        "size_mult":       0.5,
        "strategy_mode":  "standard",
        "allow_new_entry": False,       # 점심·장 전후 구간 진입 금지
        "desc":            "기타 구간 — 진입 금지",
    },
}


def _to_time(hhmm: str) -> datetime.time:
    h, m = map(int, hhmm.split(":"))
    return datetime.time(h, m)


# 미리 파싱된 시간대 경계
_ZONE_BOUNDS = {
    zone_key: (_to_time(start), _to_time(end))
    for zone_key, (start, end) in TIME_ZONES.items()
}


class TimeStrategyRouter:
    """
    분봉 시각 → 시간대 분류 → 전략 파라미터 반환

    사용:
        router = TimeStrategyRouter()
        params = router.route(now_kst())
        if not params["allow_new_entry"]:
            return  # 신규 진입 금지
        min_conf = params["min_confidence"]
    """

    def __init__(self):
        self._last_zone: Optional[str] = None

    def get_zone(self, dt: Optional[datetime.datetime] = None) -> str:
        """
        현재 시각의 시간대 코드 반환

        Returns:
            "OPEN_VOLATILE" | "STABLE_TREND" | "LUNCH_RECOVERY" |
            "CLOSE_VOLATILE" | "EXIT_ONLY" | "OTHER"
        """
        if dt is None:
            dt = now_kst()
        t = dt.time()

        for zone_key, (start, end) in _ZONE_BOUNDS.items():
            if start <= t < end:
                return zone_key

        return "OTHER"

    def route(self, dt: Optional[datetime.datetime] = None) -> dict:
        """
        현재 시각의 전략 파라미터 반환

        Returns:
            {zone, min_confidence, size_mult, strategy_mode,
             allow_new_entry, desc}
        """
        zone   = self.get_zone(dt)
        params = dict(_ZONE_PARAMS[zone])
        params["zone"] = zone

        if zone != self._last_zone:
            logger.info(f"[TimeRouter] 시간대 전환 → {zone}: {params['desc']}")
            self._last_zone = zone

        return params

    def apply_regime_override(self, params: dict, macro_regime: str) -> dict:
        """
        매크로 레짐에 따른 파라미터 보정

        RISK_OFF → 신뢰도 기준 추가 상향, 사이즈 축소
        RISK_ON  → 신뢰도 기준 소폭 완화
        """
        params = dict(params)   # 원본 보호

        if macro_regime == "RISK_OFF":
            params["min_confidence"] = min(params["min_confidence"] + 0.05, 0.90)
            params["size_mult"]      = params["size_mult"] * 0.7
        elif macro_regime == "RISK_ON":
            params["min_confidence"] = max(params["min_confidence"] - 0.02, 0.50)
            params["size_mult"]      = params["size_mult"] * 1.1

        params["_regime_override"] = macro_regime
        return params

    def apply_micro_regime_override(self, params: dict, micro_regime: str) -> dict:
        """
        미시 레짐에 따른 파라미터 보정

        추세장 → 추세추종 강화
        횡보장 → 신뢰도 상향 + 사이즈 축소
        급변장 → 진입 차단
        """
        params = dict(params)

        if micro_regime == "추세장":
            if params["strategy_mode"] == "standard":
                params["strategy_mode"] = "trend_follow"
            params["size_mult"] = params["size_mult"] * 1.1

        elif micro_regime == "횡보장":
            params["min_confidence"] = min(params["min_confidence"] + 0.04, 0.90)
            params["size_mult"]      = params["size_mult"] * 0.8

        elif micro_regime == "급변장":
            params["allow_new_entry"] = False
            params["size_mult"]       = 0.0

        params["_micro_regime"] = micro_regime
        return params

    def apply_expiry_override(self, params: dict, dt: Optional[datetime.datetime] = None) -> dict:
        """
        월물 만기일 접근 시 리스크 파라미터 보정

        만기 당일  → 신뢰도 기준 +5%, 사이즈 ×0.6 (롤오버 변동·유동성 왜곡)
        만기 전날  → 신뢰도 기준 +2%, 사이즈 ×0.8 (사전 포지션 조정 영향)
        그 외       → 변경 없음
        """
        d2e = days_to_monthly_expiry(dt.date() if dt else None)
        if d2e == 0:
            params = dict(params)
            params["min_confidence"] = min(params["min_confidence"] + 0.05, 0.90)
            params["size_mult"]      = params["size_mult"] * 0.6
            params["_expiry_override"] = "EXPIRY_DAY"
            logger.info("[TimeRouter] 월물 만기 당일 — 신뢰도↑ 사이즈×0.6")
        elif d2e == 1:
            params = dict(params)
            params["min_confidence"] = min(params["min_confidence"] + 0.02, 0.90)
            params["size_mult"]      = params["size_mult"] * 0.8
            params["_expiry_override"] = "PRE_EXPIRY"
            logger.info("[TimeRouter] 월물 만기 전날 — 신뢰도↑ 사이즈×0.8")
        return params

    def apply_fomc_override(self, params: dict, dt: Optional[datetime.datetime] = None) -> dict:
        """
        FOMC 발표 당일(한국 기준) 리스크 파라미터 보정

        FOMC 당일 → 신뢰도 기준 +5%, 사이즈 ×0.7 (글로벌 변동성 급등 대비)
        """
        if is_fomc_day(dt):
            params = dict(params)
            params["min_confidence"] = min(params["min_confidence"] + 0.05, 0.90)
            params["size_mult"]      = params["size_mult"] * 0.7
            params["_fomc_override"] = True
            logger.info("[TimeRouter] FOMC 발표일 — 신뢰도↑ 사이즈×0.7")
        return params


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    router = TimeStrategyRouter()

    test_times = [
        datetime.datetime(2026, 4, 26, 9, 15),
        datetime.datetime(2026, 4, 26, 10, 45),
        datetime.datetime(2026, 4, 26, 13, 20),
        datetime.datetime(2026, 4, 26, 14, 30),
        datetime.datetime(2026, 4, 26, 15, 5),
        datetime.datetime(2026, 4, 26, 12, 0),
    ]

    for t in test_times:
        p = router.route(t)
        print(f"  {t.strftime('%H:%M')} → [{p['zone']:<16}] conf≥{p['min_confidence']:.2f} "
              f"size×{p['size_mult']:.1f} entry={p['allow_new_entry']} | {p['desc']}")
