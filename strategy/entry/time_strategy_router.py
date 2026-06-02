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

from config.settings import (
    TIME_ZONES,
    MC_PERCENTILE, MC_ABS_FLOOR, MC_ABS_CEIL, MC_STEP_LIMIT,
)
from utils.time_utils import now_kst, days_to_monthly_expiry, is_fomc_day

logger = logging.getLogger("SIGNAL")


def _restore_mc_from_history() -> None:
    """
    기동 시 mc_history.db의 가장 최근 값으로 _ZONE_PARAMS를 복원.
    재기동 시 마다 코드 초기값으로 리셋되는 문제 해결.
    """
    try:
        import os, sqlite3
        from config.settings import DB_DIR
        db = os.path.join(DB_DIR, "mc_history.db")
        if not os.path.exists(db):
            return
        conn = sqlite3.connect(db, timeout=5)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT zone, new_mc FROM mc_history "
            "WHERE id IN (SELECT MAX(id) FROM mc_history GROUP BY zone)"
        ).fetchall()
        conn.close()
        base_mcs = []
        for r in rows:
            zone = r["zone"]
            if zone in _ZONE_PARAMS:
                old = _ZONE_PARAMS[zone]["min_confidence"]
                _ZONE_PARAMS[zone]["min_confidence"] = float(r["new_mc"])
                logger.info("[DynMC] 기동 복원: %s  %.3f → %.3f", zone, old, r["new_mc"])
                base_mcs.append(float(r.get("base_mc") or r["new_mc"]))

        # REGIME_MIN_CONFIDENCE 복원 (앙상블 내부 min_conf 동기화)
        if base_mcs:
            base = min(base_mcs)   # 가장 낮은 base_mc 기준
            from config import settings as _s
            _rmc = getattr(_s, "REGIME_MIN_CONFIDENCE", {})
            for _regime in ("RISK_ON", "NEUTRAL"):
                old_r = _rmc.get(_regime, 0.52)
                new_r = round(max(base, MC_ABS_FLOOR), 3)
                if abs(new_r - old_r) >= 0.005:
                    _rmc[_regime] = new_r
                    logger.info("[DynMC] 기동 복원 REGIME_MIN_CONF %s %.3f → %.3f",
                                _regime, old_r, new_r)
    except Exception as exc:
        logger.debug("[DynMC] 기동 복원 실패 (무시): %s", exc)


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
        "min_confidence":  0.60,      # 0.63→0.60: 초기 운영 기간 한시적 완화
        "size_mult":       0.8,        # 사이즈 보수적
        "strategy_mode":  "trend_follow",
        "allow_new_entry": True,
        "desc":            "개장 변동성 — 추세추종, 신뢰도↑",
    },
    "STABLE_TREND": {
        "min_confidence":  0.54,   # 0.58→0.54: 초기 운영 기간 한시적 완화
        "size_mult":       1.0,
        "strategy_mode":  "standard",
        "allow_new_entry": True,
        "desc":            "안정 추세 — 표준 앙상블",
    },
    "LUNCH_RECOVERY": {
        "min_confidence":  0.57,   # 0.60→0.57: 초기 운영 기간 한시적 완화
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

# 모듈 로드 시 mc_history.db에서 마지막 mc 복원 (재기동 시 리셋 방지)
_restore_mc_from_history()


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


# ── 시간대별 mc 배율 (base_mc 에 곱해 시간대 특성 반영) ──────────
_ZONE_MC_MULT: Dict[str, float] = {
    "GAP_OPEN":       1.05,
    "OPEN_VOLATILE":  1.02,
    "STABLE_TREND":   1.00,
    "LUNCH_RECOVERY": 0.99,
    "CLOSE_VOLATILE": 1.01,
    "EXIT_ONLY":      1.00,
    "OTHER":          1.02,
}


def update_dynamic_mc(
    conf_list: list,
    trigger: str,
    record: bool = True,
) -> Optional[float]:
    """
    최근 conf 분포를 기반으로 _ZONE_PARAMS min_confidence를 동적 갱신.

    Args:
        conf_list: 측정 기간의 앙상블 confidence 리스트
        trigger:   'RETRAIN' | 'DAILY_WARMUP'
        record:    mc_history.db에 이력 저장 여부

    Returns:
        적용된 base_mc (None = 샘플 부족으로 갱신 안 함)
    """
    if len(conf_list) < 30:
        logger.warning("[DynMC] 샘플 부족 (%d < 30) — mc 갱신 스킵", len(conf_list))
        return None

    sorted_c = sorted(conf_list)
    idx_p65  = int(len(sorted_c) * MC_PERCENTILE / 100)
    conf_p65 = sorted_c[idx_p65]
    conf_avg = sum(conf_list) / len(conf_list)

    # base_mc: p65 기준, 절대 상하한 적용
    base_mc = max(MC_ABS_FLOOR, min(MC_ABS_CEIL, conf_p65))

    # 이전 STABLE_TREND mc와 비교해 변화폭 clamp
    prev_stable = _ZONE_PARAMS["STABLE_TREND"]["min_confidence"]
    delta = base_mc - prev_stable
    if abs(delta) > MC_STEP_LIMIT:
        base_mc = prev_stable + (MC_STEP_LIMIT if delta > 0 else -MC_STEP_LIMIT)
        logger.info(
            "[DynMC] step clamp 적용: p65=%.3f → base=%.3f (prev=%.3f delta=%.3f)",
            conf_p65, base_mc, prev_stable, delta,
        )

    zone_changes = {}
    for zone, params in _ZONE_PARAMS.items():
        if zone in ("EXIT_ONLY", "OTHER"):
            continue
        mult    = _ZONE_MC_MULT.get(zone, 1.00)
        old_mc  = params["min_confidence"]
        new_mc  = round(max(MC_ABS_FLOOR, min(MC_ABS_CEIL, base_mc * mult)), 3)
        if abs(new_mc - old_mc) >= 0.005:   # 0.5%p 미만 변화는 무시
            zone_changes[zone] = (old_mc, new_mc)
            params["min_confidence"] = new_mc

    # REGIME_MIN_CONFIDENCE도 base_mc와 동기화
    # 앙상블 내부의 레짐별 min_conf가 _ZONE_PARAMS보다 높으면 진입 불가
    try:
        from config import settings as _s
        _rmc = getattr(_s, "REGIME_MIN_CONFIDENCE", {})
        for _regime in ("RISK_ON", "NEUTRAL"):
            _old_rmc = _rmc.get(_regime, base_mc)
            _new_rmc = round(max(base_mc, MC_ABS_FLOOR), 3)
            if abs(_new_rmc - _old_rmc) >= 0.005:
                _rmc[_regime] = _new_rmc
                logger.info("[DynMC] REGIME_MIN_CONF %s %.3f→%.3f", _regime, _old_rmc, _new_rmc)
        # RISK_OFF는 항상 base_mc+0.10 이상 유지 (보수 유지)
        _rmc["RISK_OFF"] = round(min(0.75, max(base_mc + 0.10, _rmc.get("RISK_OFF", 0.65))), 3)
    except Exception as _rmc_e:
        logger.debug("[DynMC] REGIME_MIN_CONF 갱신 실패: %s", _rmc_e)

    if zone_changes:
        import datetime as _dt
        ts = _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(
            "[DynMC] mc 갱신 trigger=%s base=%.3f  %s",
            trigger, base_mc,
            " | ".join("%s %.3f→%.3f" % (z, o, n) for z, (o, n) in zone_changes.items()),
        )
        if record:
            try:
                from model.mc_history_db import insert_mc_change
                insert_mc_change(
                    ts=ts, trigger=trigger, base_mc=base_mc,
                    zone_changes=zone_changes,
                    conf_avg=round(conf_avg, 4),
                    conf_p65=round(conf_p65, 4),
                    n_samples=len(conf_list),
                )
            except Exception as _e:
                logger.debug("[DynMC] 이력 저장 실패: %s", _e)
    else:
        logger.debug("[DynMC] mc 변화 없음 (base=%.3f prev=%.3f)", base_mc, prev_stable)

    return base_mc


def get_zone_min_confidence(zone: str) -> float:
    """시간대 코드 → 최소 신뢰도 반환 (main.py에서 레짐 기준과 max 비교용)"""
    return _ZONE_PARAMS.get(zone, _ZONE_PARAMS["OTHER"])["min_confidence"]


def get_horizon_min_confs(zone: str) -> dict:
    """
    시간대 코드 → 호라이즌별 min_conf 딕셔너리 반환 (P4 2D 표).

    GAP_OPEN / EXIT_ONLY / OTHER 등 표에 없는 시간대 → STABLE_TREND 기준 fallback.
    반환값 예시: {"1m": 0.57, "3m": 0.58, ..., "30m": 0.62}
    """
    from config.settings import MIN_CONF_TABLE
    _fallback = MIN_CONF_TABLE.get("STABLE_TREND", {})
    return MIN_CONF_TABLE.get(zone, _fallback)


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
