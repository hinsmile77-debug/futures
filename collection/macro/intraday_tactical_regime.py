# collection/macro/intraday_tactical_regime.py — 장중 전술 레짐 분류기
"""
Layer 2: Intraday Tactical Regime (장중 매분 갱신)

설계: docs/MACRO_REGIME_ENHANCEMENT.md § 4~5
  NORMAL       → Layer 1(Overnight) 레짐 사용
  DAY_RISK_OFF → 신규 롱 금지, 숏만 허용, 사이즈 ×0.5
  CRASH        → 모든 신규 진입 금지 (A등급 숏 추세추종만 예외)

상태 전이:
  NORMAL → DAY_RISK_OFF : 조건 A 또는 B
  NORMAL / DAY_RISK_OFF → CRASH : 조건 A·B·C 중 하나
  CRASH / DAY_RISK_OFF → NORMAL : RECOVERY 조건 3개 모두 충족

Layer 2가 NORMAL 이면 Layer 1 레짐을 그대로 사용.
Layer 2가 DAY_RISK_OFF / CRASH 이면 Layer 2 우선 적용.
"""
import datetime
import logging
from collections import deque
from typing import Optional

logger = logging.getLogger("SYSTEM")

# Layer 2 레짐 상수
INTRADAY_NORMAL       = "NORMAL"
INTRADAY_DAY_RISK_OFF = "DAY_RISK_OFF"
INTRADAY_CRASH        = "CRASH"

# 진입 정책 테이블 (레짐별)
INTRADAY_POLICY = {
    INTRADAY_NORMAL: {
        "allow_long":       True,
        "allow_short":      True,
        "min_conf_adjust":  0.0,    # 기준 신뢰도 보정 (퍼센트p)
        "size_mult":        1.0,
    },
    INTRADAY_DAY_RISK_OFF: {
        "allow_long":       False,
        "allow_short":      True,
        "min_conf_adjust":  5.0,    # +5%p
        "size_mult":        0.5,
    },
    INTRADAY_CRASH: {
        "allow_long":       False,
        "allow_short":      False,  # A등급 숏 추세추종은 호출부에서 별도 허용
        "min_conf_adjust":  12.0,   # +12%p
        "size_mult":        0.3,
    },
}


class IntradayTacticalRegime:
    """
    매분 갱신되는 장중 전술 레짐 분류기.

    주입 인터페이스:
        update(ts_dt, futures_day_ret, open_price, atr_ratio,
               ofi_15m_avg, z_warn_count)
    조회 인터페이스:
        current        → 현재 레짐 문자열
        policy         → 진입 정책 dict
        status_dict()  → 대시보드/로그용 상태 dict
    """

    # DAY_RISK_OFF 발동 임계값 (양방향 — 상승이든 하락이든 급변 시 보수 운영)
    DAY_RISK_OFF_ABS_DAY   = 0.010    # |당일 수익률| ≥ 1.0%
    DAY_RISK_OFF_ABS_DAY2  = 0.008    # |당일 수익률| ≥ 0.8% (15분과 복합)
    DAY_RISK_OFF_ABS_15M   = 0.005    # |15분 수익률| ≥ 0.5%

    # CRASH 발동 임계값 (양방향 — 모델 신뢰 불가 상태)
    CRASH_ABS_DAY_RET      = 0.018    # |당일 수익률| ≥ 1.8%
    CRASH_ABS_30M_RET      = 0.010    # |30분 수익률| ≥ 1.0%
    CRASH_ATR_RATIO        = 1.25     # ATR ratio ≥ 1.25  (중립)
    CRASH_Z_WARN_MIN       = 3        # z극단 ≥ 3  (중립)

    # RECOVERY_NEUTRAL 복귀 임계값
    # bounce(저점 대비 반등) 제거 — 선물 양방향 거래에서 상승 방향 복귀만 요구하면
    # 하락 추세 지속 시 숏 기회를 차단하는 모순 발생 (2026-06-02 설계 수정)
    # 대신: ATR 안정 + z_warn 해소 + OFI 방향 확인으로 복귀
    RECOVERY_ATR_MAX       = 1.2      # ATR ratio < 1.2  (변동성 안정)
    RECOVERY_Z_WARN_MAX    = 3        # z극단 수 < 3 (스케일러 정상화)

    def __init__(self):
        self._regime: str = INTRADAY_NORMAL
        self._prev_regime: str = INTRADAY_NORMAL
        self._regime_since: Optional[datetime.datetime] = None

        # 장중 수익률 추적
        self._open_price: float = 0.0
        self._day_low: float = 0.0
        self._ret_15m_buf: deque = deque(maxlen=15)   # 1분봉 수익률 15개

        # 레짐 이력 (대시보드용, 최근 60분)
        self._history: deque = deque(maxlen=60)       # (ts_str, regime)

        # 마지막 상태 스냅샷 (status_dict 용)
        self._last_factors: dict = {}

    # ── 매분 호출 ────────────────────────────────────────────────

    def update(
        self,
        ts_dt: datetime.datetime,
        futures_day_ret: float,     # 시가 대비 현재 수익률 (소수: -0.012 = -1.2%)
        open_price: float,          # 당일 시가
        close_price: float,         # 현재가
        atr_ratio: float,           # MicroRegime ATR ratio
        ofi_15m_avg: float,         # OFI 15분 이동평균 (양수=매수 우세)
        z_warn_count: int,          # z-score extreme 경고 호라이즌 수
        ret_1m: float = 0.0,        # 직전 1분 수익률
        contrarian_active: bool = False,   # Contrarian ACTIVE 여부
    ) -> str:
        """레짐 갱신 후 새 레짐 반환"""
        if open_price > 0 and self._open_price == 0:
            self._open_price = open_price
            self._day_low    = close_price

        if close_price > 0:
            self._day_low = min(self._day_low, close_price) if self._day_low else close_price
            self._ret_15m_buf.append(ret_1m)

        ret_15m = sum(self._ret_15m_buf)  # 15분 누적 수익률 근사
        ret_30m = sum(list(self._ret_15m_buf)[-30:]) if len(self._ret_15m_buf) >= 10 else 0.0

        # 저점 대비 반등률
        bounce = (
            (close_price - self._day_low) / (abs(self._day_low) + 1e-9)
            if self._day_low else 0.0
        )

        self._last_factors = {
            "day_ret":       round(futures_day_ret, 5),
            "ret_15m":       round(ret_15m, 5),
            "ret_30m":       round(ret_30m, 5),
            "atr_ratio":     round(atr_ratio, 3),
            "ofi_15m_avg":   round(ofi_15m_avg, 4),
            "z_warn_count":  z_warn_count,
            "bounce":        round(bounce, 5),
            "contrarian":    contrarian_active,
        }

        new_regime = self._classify(
            futures_day_ret, ret_15m, ret_30m, atr_ratio,
            ofi_15m_avg, z_warn_count, bounce, contrarian_active,
        )

        if new_regime != self._regime:
            logger.info(
                "[IntradayRegime] %s → %s | day=%.2f%% atr=%.2f z=%d",
                self._regime, new_regime,
                futures_day_ret * 100, atr_ratio, z_warn_count,
            )
            self._prev_regime  = self._regime
            self._regime       = new_regime
            self._regime_since = ts_dt

        self._history.append((ts_dt.strftime("%H:%M"), new_regime))
        return new_regime

    # ── 분류 로직 ────────────────────────────────────────────────

    def _classify(
        self,
        day_ret: float,
        ret_15m: float,
        ret_30m: float,
        atr_ratio: float,
        ofi_15m_avg: float,
        z_warn_count: int,
        bounce: float,
        contrarian_active: bool,
    ) -> str:
        cur = self._regime

        # ─ CRASH 발동 조건 (셋 중 하나) ─────────────────────────
        # 수익률 기반은 abs() 양방향 — 급등이든 급락이든 동일 처리
        crash_a = abs(day_ret) >= self.CRASH_ABS_DAY_RET
        crash_b = abs(ret_30m) >= self.CRASH_ABS_30M_RET and atr_ratio >= self.CRASH_ATR_RATIO
        crash_c = z_warn_count >= self.CRASH_Z_WARN_MIN   # 이미 방향 중립

        if crash_a or crash_b or crash_c:
            return INTRADAY_CRASH

        # ─ DAY_RISK_OFF 발동 조건 (셋 중 하나) ──────────────────
        # 수익률 기반은 abs() 양방향 — 급등이든 급락이든 보수 운영
        dro_a = abs(day_ret) >= self.DAY_RISK_OFF_ABS_DAY
        dro_b = (
            abs(day_ret) >= self.DAY_RISK_OFF_ABS_DAY2
            and abs(ret_15m) >= self.DAY_RISK_OFF_ABS_15M
        )
        # Contrarian ACTIVE → 최소 DAY_RISK_OFF 자동 승격 (방향 중립)
        dro_c = contrarian_active

        if dro_a or dro_b or dro_c:
            return INTRADAY_DAY_RISK_OFF

        # ─ RECOVERY 복귀 조건 (현재 비정상 상태일 때만 평가) ─────
        # 방향 중립 2가지만 사용:
        #   ATR < 1.2       : 변동성 안정 (상승/하락 무관)
        #   z극단 < 3       : 스케일러·모델 정상화 (상승/하락 무관)
        # 제거 이유:
        #   bounce ≥ 0.5%   : 상승 방향 편향 → 하락 추세 시 CRASH 고착
        #   OFI15m > 0      : 매수 방향 편향 → 하락 추세 시 OFI 음수로 고착
        if cur in (INTRADAY_CRASH, INTRADAY_DAY_RISK_OFF):
            recovery = (
                atr_ratio < self.RECOVERY_ATR_MAX
                and z_warn_count < self.RECOVERY_Z_WARN_MAX
            )
            if not recovery:
                return cur   # 복귀 조건 미충족 → 현 레짐 유지

        return INTRADAY_NORMAL

    # ── 조회 인터페이스 ──────────────────────────────────────────

    @property
    def current(self) -> str:
        return self._regime

    @property
    def policy(self) -> dict:
        return INTRADAY_POLICY[self._regime]

    def is_long_allowed(self) -> bool:
        return INTRADAY_POLICY[self._regime]["allow_long"]

    def is_short_allowed(self) -> bool:
        return INTRADAY_POLICY[self._regime]["allow_short"]

    def allow_crash_grade_a_short(self) -> bool:
        """CRASH 상태에서 A등급 숏 추세추종 허용 여부"""
        return self._regime == INTRADAY_CRASH

    def size_mult(self) -> float:
        return INTRADAY_POLICY[self._regime]["size_mult"]

    def min_conf_adjust(self) -> float:
        """신뢰도 최소값 보정 (퍼센트p, 양수=상향)"""
        return INTRADAY_POLICY[self._regime]["min_conf_adjust"]

    def status_dict(self) -> dict:
        since_str = self._regime_since.strftime("%H:%M") if self._regime_since else "--:--"
        return {
            "regime":       self._regime,
            "prev_regime":  self._prev_regime,
            "since":        since_str,
            "policy":       INTRADAY_POLICY[self._regime],
            "factors":      self._last_factors,
            "history":      list(self._history)[-10:],
        }

    def reset_daily(self):
        self._regime       = INTRADAY_NORMAL
        self._prev_regime  = INTRADAY_NORMAL
        self._regime_since = None
        self._open_price   = 0.0
        self._day_low      = 0.0
        self._ret_15m_buf.clear()
        self._history.clear()
        self._last_factors = {}
