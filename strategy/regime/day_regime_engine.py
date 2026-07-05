# strategy/regime/day_regime_engine.py — L1 데이 레짐 엔진 (섀도우 전용)
"""
v1 설계안(`mireuki_v9_최종설계안_2026-07-03.md`)이 말하는 "L1 데이 레짐 엔진(신규)"은
기존 레짐분류기 3개를 재구현하는 게 아니라 통합하는 애그리게이터다:

  - `collection.macro.micro_regime.MicroRegimeClassifier` — 1분 ADX/ATR 5분류(방향 없음)
  - `collection.macro.intraday_tactical_regime.IntradayTacticalRegime` — 장중 방어 레짐
  - `features["hurst"]` — 이미 계산되는 허스트 지수
  - 시가이격(day_ret), opt_gex_bn/opt_chain_pcr(옵션체인, 이미 병합됨), 첫 30분 모멘텀

출력은 TREND_UP/TREND_DN/RANGE/CHAOS + confidence + 히스테리시스.

**섀도우 전용** — main.py 호출부는 결과를 로그·entry_gate_json에만 기록한다.
L2(레짐조건부 프로파일) 분기는 이 엔진의 백테스트 검증(`scripts/generate_day_regime_backtest_report.py`)
완료 후 별도 세션에서 연결한다(`mireuki_v9_구현계획_v3_2026-07-05.md` §3).
"""
from collections import deque
from typing import Dict, Optional

TREND_UP = "TREND_UP"
TREND_DN = "TREND_DN"
RANGE    = "RANGE"
CHAOS    = "CHAOS"

# MicroRegimeClassifier 출력 문자열(collection/macro/micro_regime.py)과의 매핑
_MICRO_TREND    = "추세장"
_MICRO_RANGE    = "횡보장"
_MICRO_VOLATILE = "급변장"

# 히스테리시스 — 새 레짐 후보가 이 분(分) 이상 연속 관측돼야 실제 전환.
# MicroRegimeClassifier의 regime_duration 패턴 참고 — 매분 뒤집힘 방지.
_MIN_DWELL_MINUTES = 3

# Hurst 임계값 — CORE.md·기존 checklist.py의 HURST_RANGE_THRESHOLD 계열과 정합되는 수준
_HURST_TREND_MIN = 0.55
_HURST_RANGE_MAX = 0.45

_FIRST_MOMENTUM_WINDOW = 30  # 첫 N분 모멘텀 고정 관측 창


class DayRegimeEngine:
    """기존 레짐분류기 3개 + Hurst + 시가이격 + 옵션체인 + 첫30분 모멘텀 통합 애그리게이터."""

    def __init__(self):
        self._current_regime = RANGE
        self._candidate_regime: Optional[str] = None
        self._candidate_streak = 0
        self._regime_duration = 0

        self._first_mom_buf: deque = deque(maxlen=_FIRST_MOMENTUM_WINDOW)
        self._first_mom_frozen: Optional[float] = None
        self._calls_since_reset = 0

    def update(
        self,
        *,
        micro_regime: str,
        adx: float,
        atr_ratio: float,
        hurst: float,
        day_ret: float,
        ret_1m: float,
        opt_gex_bn: float = 0.0,
        opt_chain_pcr: float = 0.0,
        intraday_tactical_regime: str = "NORMAL",
    ) -> Dict:
        # 첫 30분 모멘텀 — 세션 시작 후 30콜(분) 누적 후 값 고정(그 이후는 갱신 안 함)
        self._calls_since_reset += 1
        if self._first_mom_frozen is None:
            self._first_mom_buf.append(ret_1m)
            if self._calls_since_reset >= _FIRST_MOMENTUM_WINDOW:
                self._first_mom_frozen = sum(self._first_mom_buf)
        first_30m_momentum = (
            self._first_mom_frozen
            if self._first_mom_frozen is not None
            else sum(self._first_mom_buf)
        )

        candidate, base_confidence, factors = self._classify(
            micro_regime=micro_regime,
            adx=adx,
            atr_ratio=atr_ratio,
            hurst=hurst,
            day_ret=day_ret,
            first_30m_momentum=first_30m_momentum,
            intraday_tactical_regime=intraday_tactical_regime,
        )

        # opt_gex_bn/opt_chain_pcr — 방향 판정에는 관여하지 않고 confidence 보정만.
        # 음의 감마(딜러 숏감마) → 변동성 증폭 경향 → TREND/CHAOS 확신 소폭 상향.
        # 양의 감마(딜러 롱감마) → 가격 억제 경향 → RANGE 확신 소폭 상향.
        gex_adj = 0.0
        if candidate in (TREND_UP, TREND_DN, CHAOS) and opt_gex_bn < 0:
            gex_adj = min(0.05, abs(opt_gex_bn) * 1e-3)
        elif candidate == RANGE and opt_gex_bn > 0:
            gex_adj = min(0.05, opt_gex_bn * 1e-3)
        # PCR 극단값이 후보 방향과 결이 같으면 소폭 가산(풋 우위=하방 압력, 콜 우위=상방 압력)
        pcr_adj = 0.0
        if candidate == TREND_DN and opt_chain_pcr > 1.2:
            pcr_adj = 0.03
        elif candidate == TREND_UP and 0.0 < opt_chain_pcr < 0.8:
            pcr_adj = 0.03

        confidence = max(0.0, min(1.0, base_confidence + gex_adj + pcr_adj))
        factors["opt_gex_bn"] = round(opt_gex_bn, 4)
        factors["opt_chain_pcr"] = round(opt_chain_pcr, 4)
        factors["first_30m_momentum"] = round(first_30m_momentum, 5)

        # 히스테리시스 — 후보가 현재 레짐과 다르면 연속 관측 카운트, 충분히 지속돼야 전환
        final_regime = self._apply_hysteresis(candidate)

        return {
            "regime":          final_regime,
            "candidate":       candidate,
            "confidence":      round(confidence, 4),
            "regime_duration": self._regime_duration,
            "factors":         factors,
        }

    def _classify(
        self,
        *,
        micro_regime: str,
        adx: float,
        atr_ratio: float,
        hurst: float,
        day_ret: float,
        first_30m_momentum: float,
        intraday_tactical_regime: str,
    ):
        factors = {
            "micro_regime": micro_regime,
            "adx":          round(adx, 2),
            "atr_ratio":    round(atr_ratio, 3),
            "hurst":        round(hurst, 3),
            "day_ret":      round(day_ret, 5),
        }

        # Layer2 CRASH는 방향 신뢰 불가 상태 — 최우선 CHAOS 오버라이드
        if intraday_tactical_regime == "CRASH":
            factors["override"] = "layer2_crash"
            return CHAOS, 0.90, factors

        if micro_regime == _MICRO_VOLATILE:
            return CHAOS, 0.70, factors

        if micro_regime == _MICRO_TREND and hurst >= _HURST_TREND_MIN:
            # 방향 판정: 시가이격 우선, 부호가 애매하면(초반) 첫30분 모멘텀으로 보완
            direction_signal = day_ret if abs(day_ret) > 1e-6 else first_30m_momentum
            if direction_signal >= 0:
                conf = 0.55 + min(0.25, adx / 200.0)
                return TREND_UP, conf, factors
            else:
                conf = 0.55 + min(0.25, adx / 200.0)
                return TREND_DN, conf, factors

        if micro_regime == _MICRO_RANGE and hurst < _HURST_RANGE_MAX:
            return RANGE, 0.60, factors

        # 혼합/탈진 또는 hurst가 중립 구간 — 방향성 확신 없음, RANGE로 보수 처리
        return RANGE, 0.45, factors

    def _apply_hysteresis(self, candidate: str) -> str:
        if candidate == self._current_regime:
            self._candidate_regime = None
            self._candidate_streak = 0
            self._regime_duration += 1
            return self._current_regime

        # CHAOS는 리스크 오버라이드 성격(Layer2 CRASH·급변장) — 지연 없이 즉시 전환.
        # IntradayTacticalRegime의 CRASH 판정 자체가 히스테리시스 없이 즉시 발동하는 것과 정합.
        if candidate == CHAOS:
            self._current_regime = CHAOS
            self._candidate_regime = None
            self._candidate_streak = 0
            self._regime_duration = 1
            return CHAOS

        if candidate == self._candidate_regime:
            self._candidate_streak += 1
        else:
            self._candidate_regime = candidate
            self._candidate_streak = 1

        if self._candidate_streak >= _MIN_DWELL_MINUTES:
            self._current_regime = candidate
            self._candidate_regime = None
            self._candidate_streak = 0
            self._regime_duration = 1
        return self._current_regime

    def reset_daily(self) -> None:
        self._current_regime = RANGE
        self._candidate_regime = None
        self._candidate_streak = 0
        self._regime_duration = 0
        self._first_mom_buf.clear()
        self._first_mom_frozen = None
        self._calls_since_reset = 0

    @property
    def current_regime(self) -> str:
        return self._current_regime
