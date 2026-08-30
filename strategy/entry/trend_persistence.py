# strategy/entry/trend_persistence.py — 추세 지속성 게이트
"""
TrendPersistenceGate (UP·DOWN 양방향)

UP 모드:
  above_vwap=1 AND (CVD 동조 OR ret_5m>0) 이 STREAK_ACTIVATE분 이상 연속 →
  UP 방향 진입 한정으로 min_conf를 TREND_MIN_CONF 로 완화.

DOWN 모드:
  above_vwap=0 AND (CVD 동조 OR ret_5m<0) 이 STREAK_ACTIVATE분 이상 연속 →
  DOWN 방향 진입 한정으로 min_conf를 TREND_MIN_CONF 로 완화.

목적: 롱/숏 원웨이 추세장에서 GBM conf 부족으로 진입 0건이 되는
      구조적 문제를 장중 실시간 추세 감지로 보완.

리셋 조건:
  - 조건 불충족 STREAK_FAIL_RESET분 연속 → streak 리셋 (느린 취소)
  - UP:   cvd_delta_norm 5바 평균 <= CVD_HARD_BREAK_DN → 즉시 리셋 (매도압 급반전)
  - DOWN: cvd_delta_norm 5바 평균 >= CVD_HARD_BREAK_UP → 즉시 리셋 (숏스퀴즈)
          DOWN 을 UP 보다 민감하게 두는 이유(원 설계 계승): 하락 중 CVD 급반등
          (숏스퀴즈)은 상승 중 CVD 급반락보다 훨씬 빠르고 파괴적.

🔴 [MW0601 500차] 이 게이트는 **min_conf 를 완화**한다. 그래서 "즉시 리셋"은
   기능이 아니라 **안전장치**다 — 완화를 취소하는 쪽이다. 구 구현은 단위 300배
   불일치로 **배포 이래 한 번도 발동할 수 없었고**, 6개월간 어떤 계측에도 안 걸렸다.
   완화는 살고 취소만 죽어 있던 상태다. 상세는 아래 상수 주석 참조.

가격 구조 보강 (PriceStructureBoost):
  recent_bars 를 받아 HH-HL(연속 고점·저점 상승) 또는 LH-LL(연속 고점·저점 하락)
  구조를 감지. streak >= STREAK_ACTIVATE_PRICE_BOOST 이고 가격 구조가 같은 방향이면
  min_conf 를 TREND_MIN_CONF_PRICE_BOOST 까지 추가 완화.
  OFI 또는 CVD 중 하나는 같은 방향이어야 부스트를 인정한다(과진입 방지).
"""
import logging
from collections import deque
from typing import Dict, List, Optional

logger = logging.getLogger("SIGNAL")

# ── 파라미터 ────────────────────────────────────────────────────────────
_STREAK_ACTIVATE         = 10    # 발동 최소 연속 분
_STREAK_FAIL_RESET       = 3     # 조건 불충족 연속 N분 → streak 리셋
_TREND_MIN_CONF          = 0.44  # 추세 지속 시 min_conf 하한 (UP·DOWN 공용)

# ── [MW0601 500차 / D-1] CVD 급반전 하드브레이크 재설계 ──────────────────
# 🔴 구 상수는 **배포 이래 한 번도 발동할 수 없었다**:
#     _CVD_SLOPE_HARD_BREAK_DN = -300 / _UP = +200
#     vs 실측 `cvd_slope` 범위 **[0.0000, 0.9743]** (n=7,527, 2026-07-31~08-28)
#   Phase 3-A 가 `cvd_slope` 를 계약수 → 정규화값[-1,1] 으로 바꾸면서
#   (`feature_builder.py:208`) 임계를 함께 옮기지 않았다. 단위 300배 불일치이고,
#   에러도 경보도 없이 조용히 죽었다(계측 4원칙 ① 위반).
#   완화(min_conf → 0.44/0.38)는 살고 **즉시 취소만** 죽어 있었다.
#
# 임계만 -0.3 식으로 바꾸면 안 된다 — `cvd_slope` 는 buy_vol 편향으로 **음수가
# 0건**이라 `up_hbreak` 는 여전히 도달 불가다(500-A). 판정 근거 자체를 건강한
# `cvd_delta_norm`(= Close Location Value, 실측 음수 49.1%)으로 옮긴다.
#
# **단일 바가 아니라 5바 롤링 평균**을 쓴다. 원 설계가 10바 누적(cvd_slope)이었고,
# 단일 바 CLV 는 |0.90| 에서도 **8% 발화**해(close==high/low 가 흔하다) streak 자체를
# 무력화한다. 5바 평균 실측: p1 -0.614 / p50 +0.011 / p99 +0.687.
#
# 임계는 **발화율**로 잡았다 — 원 주석의 설계 의도("하락 중 CVD 급반등=숏스퀴즈는
# 상승 중 급반락보다 훨씬 빠르고 파괴적")를 DOWN 이 약 2.8배 자주 끊기는 것으로 옮긴다:
#     UP 리셋  rolling5 <= -0.60  → 1.21%
#     DOWN 리셋 rolling5 >= +0.55 → 3.37%
# streak 활성률 영향(시뮬 n=7,527): 21.4% → **21.3%** (-0.1%p). 죽은 안전장치만
# 복구하고 진입량은 건드리지 않는다.
#
# ⚠ `HARD_BREAK_SPEC` 은 **기계판독용 선언**이다. 테스트
# `tests/test_500_cvd_ofi_live_defects.py` T1 이 이 선언을 읽어 "임계가 그 피처의
# 실측 범위 안에 있는가 + 발화율이 0.1~10% 인가"를 매번 검증한다 — 정규화가 또
# 바뀌면 그 테스트가 깨져서 알려준다. 임계를 바꿀 때는 여기만 고치면 된다.
_HARD_BREAK_WINDOW       = 5     # 롤링 평균 창(분)
_CVD_HARD_BREAK_DN       = -0.60  # UP streak:   매도압 급반전 → 즉시 리셋
_CVD_HARD_BREAK_UP       = +0.55  # DOWN streak: 매수압 급반전(숏스퀴즈) → 즉시 리셋

HARD_BREAK_SPEC = {
    "up_reset": {"feature": "cvd_delta_norm", "window": _HARD_BREAK_WINDOW,
                 "op": "<=", "threshold": _CVD_HARD_BREAK_DN},
    "dn_reset": {"feature": "cvd_delta_norm", "window": _HARD_BREAK_WINDOW,
                 "op": ">=", "threshold": _CVD_HARD_BREAK_UP},
}

# ── [MW0601 500차 / D-2] 조건 A(CVD 동조)는 **정책 동결** ────────────────
# `cvd_direction` 은 {0.0, 0.5} 2값 고착(최빈 99.5%)인데 읽는 쪽이 `int()` 로
# 절단해 **영구 0** 이었다 → `cvd_direction == 1` / `== -1` 이 한 번도 참이 안 됐고,
# 조건 A 는 사실상 꺼져 있었다. up_cond 는 `above_vwap==1 and ret_5m>0` 만으로,
# PriceStructureBoost 의 `cvd_ok` 는 영구 False 로 돌아왔다.
#
# 🔴 **이 버그를 "고치면" 정책이 바뀐다 — 그래서 값만 고치고 게이트는 동결한다.**
#   시뮬(n=7,527, streak>=10 활성률): 현재 **21.4%** → 조건 A 부활 시 **53.1%**.
#   min_conf 를 0.44(부스트 0.38)까지 내리는 게이트가 2.5배로 늘어난다.
#   시스템의 현행 진입 표본·손익은 "조건 A 꺼짐" 상태로 축적된 것이라, 근거 없이
#   켜면 전환기준 ①의 판정 기반이 통째로 흔들린다(⑧ SIZING_TARGET_CAPITAL_ENABLED
#   단독 해제 금지와 같은 취지).
#
# 그래서 이 플래그는 **False 로 신설**한다 — 끈 적이 없으므로 `git log -S` 로
# "끈 커밋"을 찾으면 안 나온다(TOX-SEVERE-SPREAD 와 같은 형태).
# 켜는 조건: 아래 섀도(`*_shadow`)로 축적된 활성 구간의 실현손익이 현행 대비
# 나쁘지 않음을 확인한 뒤 주간회의 승인.
_TREND_CVD_COND_ENABLED  = False

# 가격 구조 보강 파라미터
_TREND_MIN_CONF_PRICE_BOOST  = 0.38  # HH-HL/LH-LL 확인 시 추가 완화 하한
_STREAK_ACTIVATE_PRICE_BOOST = 5     # 부스트 적용 최소 streak (STREAK_ACTIVATE 미만도 허용)
_PRICE_STRUCT_N              = 5     # 고점·저점 비교 봉 수


def _price_structure(bars: List[Dict], n: int = _PRICE_STRUCT_N) -> int:
    """최근 n봉의 고점·저점 구조를 판정한다.

    Args:
        bars: [{"high": float, "low": float}, ...] 최신 순서로 오른쪽 끝이 가장 최근봉

    Returns:
        +1  HH-HL (연속 고점·저점 모두 상승 → 상승 구조)
        -1  LH-LL (연속 고점·저점 모두 하락 → 하락 구조)
         0  판정 불가
    """
    if len(bars) < n:
        return 0
    recent = bars[-n:]
    highs = [b.get("high", 0.0) or 0.0 for b in recent]
    lows  = [b.get("low",  0.0) or 0.0 for b in recent]
    hh = all(highs[i] > highs[i - 1] for i in range(1, n))
    hl = all(lows[i]  > lows[i - 1]  for i in range(1, n))
    lh = all(highs[i] < highs[i - 1] for i in range(1, n))
    ll = all(lows[i]  < lows[i - 1]  for i in range(1, n))
    if hh and hl:
        return +1
    if lh and ll:
        return -1
    return 0


def _step_streak(streak, fail_streak, cond_ok, hard_break, label):
    """단방향 streak 1스텝 업데이트. (new_streak, new_fail_streak) 반환."""
    if hard_break:
        if streak > 0:
            logger.debug("[TrendGate][%s] 즉시 리셋 streak %d→0", label, streak)
        return 0, 0
    if cond_ok:
        return streak + 1, 0
    new_fail = fail_streak + 1
    if new_fail >= _STREAK_FAIL_RESET:
        if streak > 0:
            logger.debug(
                "[TrendGate][%s] streak 리셋 (fail=%d) %d→0", label, new_fail, streak
            )
        return 0, 0
    return streak, new_fail


class TrendPersistenceGate:
    """
    장중 추세 지속성 게이트 (UP·DOWN 양방향).

    매분 update(features) 호출.
    active=True 이면 호출부(main.py)에서 해당 방향 actual_min_conf를
    min(actual_min_conf, TREND_MIN_CONF)으로 완화.
    """

    def __init__(self):
        self._up_streak:      int  = 0
        self._up_fail_streak: int  = 0
        self._up_active:      bool = False
        self._up_peak:        int  = 0

        self._dn_streak:      int  = 0
        self._dn_fail_streak: int  = 0
        self._dn_active:      bool = False
        self._dn_peak:        int  = 0

        # [500차 D-1] 하드브레이크용 cvd_delta_norm 롤링 버퍼
        self._cdn_buf: deque = deque(maxlen=_HARD_BREAK_WINDOW)

        # [500차 D-2] 조건 A(CVD 동조) 섀도 — `_TREND_CVD_COND_ENABLED` 를 켰다면
        # 어떻게 됐을지를 같은 streak 규칙으로 나란히 굴린다. 라이브에는 일절
        # 영향이 없고, 켤지 말지를 나중에 **실측으로** 판정하기 위한 근거다.
        # 이게 없으면 이 플래그도 CB② · CB③-P4 처럼 "재검토하기로 했는데 안 함"이
        # 된다(계측 4원칙 ④ — 억제되고 있다는 사실을 남긴다).
        self._up_streak_sh: int = 0
        self._up_fail_sh:   int = 0
        self._dn_streak_sh: int = 0
        self._dn_fail_sh:   int = 0
        self._sh_bars:      int = 0   # 관측 분봉
        self._sh_up_extra:  int = 0   # 섀도만 active 였던 분봉
        self._sh_dn_extra:  int = 0
        self._sh_logged_day: Optional[str] = None

    # ── 매분 호출 ──────────────────────────────────────────────────────
    def update(self, features: dict, recent_bars: Optional[List[Dict]] = None) -> dict:
        """
        Args:
            features:    feature_builder가 반환한 피처 dict
            recent_bars: 최근 N봉 OHLC 리스트 [{"high":, "low":, ...}, ...]
                         None 이면 가격 구조 보강 비활성

        Returns:
            {
              "up_active":         bool   — UP 추세 지속 모드 여부
              "up_streak":         int    — UP 현재 연속 분
              "dn_active":         bool   — DN 추세 지속 모드 여부
              "dn_streak":         int    — DN 현재 연속 분
              "min_conf_override": float  — 활성 방향에 적용할 min_conf 하한
              "price_structure":   int    — +1/0/-1 (가격 구조 판정)
              "price_boost_active":bool   — 가격 구조 부스트 적용 여부
            }
        """
        above_vwap    = int(features.get("above_vwap", 0) or 0)
        # [500차 D-2] `cvd_direction`(2값 고착) 대신 `cvd_delta_norm`(연속 -1~+1,
        # price-action 기반)의 부호를 쓴다. int() 절단 금지 — int(0.5) == 0 이라
        # 값이 있는데 영구 0 이 됐던 것이 이 결함의 정체다.
        cvd_delta = float(features.get("cvd_delta_norm", 0.0) or 0.0)
        cvd_dir_real = 1 if cvd_delta > 0 else (-1 if cvd_delta < 0 else 0)
        # 라이브 게이트에 먹이는 값 — 플래그가 꺼져 있으면 0(조건 A 무효)으로
        # 현행 동작을 그대로 보존한다. 실측값은 아래 섀도가 따로 굴린다.
        cvd_direction = cvd_dir_real if _TREND_CVD_COND_ENABLED else 0
        # [500차 D-1] 하드브레이크 입력 — 5바 롤링 평균(위 상수 주석 참조)
        self._cdn_buf.append(cvd_delta)
        cvd_roll = (sum(self._cdn_buf) / float(len(self._cdn_buf))
                    if len(self._cdn_buf) == _HARD_BREAK_WINDOW else 0.0)
        # ret_5m: 5분 수익률 (양수=가격 상승) — CVD 동조가 DN(-1)이어도 가격이 오르면
        # UP 조건을 충족할 수 있는 대체 기준. 스칼라감쇠·극단 z-score 등으로 CVD 방향이
        # 왜곡될 때 TrendGate가 완전히 마비되는 문제 방지.
        ret_5m = float(features.get("ret_5m", 0.0) or 0.0)

        # ── UP streak ───────────────────────────────────────────────────
        # 조건 A (CVD 확인): above_vwap=1 AND cvd_direction=1 (기존)
        # 조건 B (가격 확인): above_vwap=1 AND ret_5m > 0 (CVD 극단/왜곡 시 대체)
        # 둘 중 하나 충족이면 UP 조건 인정. hard_break는 CVD 급반전만 사용.
        up_cond   = (above_vwap == 1 and (cvd_direction == 1 or ret_5m > 0))
        up_hbreak = (cvd_roll <= _CVD_HARD_BREAK_DN)
        self._up_streak, self._up_fail_streak = _step_streak(
            self._up_streak, self._up_fail_streak, up_cond, up_hbreak, "UP"
        )
        self._up_peak  = max(self._up_peak, self._up_streak)
        prev_up        = self._up_active
        self._up_active = (self._up_streak >= _STREAK_ACTIVATE)

        if self._up_active and not prev_up:
            logger.info(
                "[TrendGate] UP 추세 지속 모드 ON (streak=%d) "
                "— UP min_conf %.2f 완화",
                self._up_streak, _TREND_MIN_CONF,
            )
        elif not self._up_active and prev_up:
            logger.info("[TrendGate] UP 추세 지속 모드 OFF (streak=%d)", self._up_streak)

        # ── DOWN streak ─────────────────────────────────────────────────
        # DN 조건도 대칭 완화: above_vwap=0 AND (cvd_direction=-1 OR ret_5m < 0)
        dn_cond   = (above_vwap == 0 and (cvd_direction == -1 or ret_5m < 0))
        dn_hbreak = (cvd_roll >= _CVD_HARD_BREAK_UP)   # 숏스퀴즈 감지
        self._dn_streak, self._dn_fail_streak = _step_streak(
            self._dn_streak, self._dn_fail_streak, dn_cond, dn_hbreak, "DN"
        )
        self._dn_peak  = max(self._dn_peak, self._dn_streak)
        prev_dn        = self._dn_active
        self._dn_active = (self._dn_streak >= _STREAK_ACTIVATE)

        if self._dn_active and not prev_dn:
            logger.info(
                "[TrendGate] DN 추세 지속 모드 ON (streak=%d) "
                "— DN min_conf %.2f 완화",
                self._dn_streak, _TREND_MIN_CONF,
            )
        elif not self._dn_active and prev_dn:
            logger.info("[TrendGate] DN 추세 지속 모드 OFF (streak=%d)", self._dn_streak)

        # ── 가격 구조 보강 (PriceStructureBoost) ────────────────────────
        ps = _price_structure(recent_bars) if recent_bars else 0
        price_boost = False
        min_conf_override = _TREND_MIN_CONF

        if ps != 0:
            active_streak = self._up_streak if ps == 1 else self._dn_streak
            ofi_ok  = int(features.get("ofi_pressure",  0) or 0) == ps
            cvd_ok  = cvd_direction == ps
            if (active_streak >= _STREAK_ACTIVATE_PRICE_BOOST
                    and (ofi_ok or cvd_ok)):
                min_conf_override = _TREND_MIN_CONF_PRICE_BOOST
                price_boost = True
                if not getattr(self, "_last_price_boost", False):
                    logger.info(
                        "[TrendGate] 가격구조 부스트 ON (%s) streak=%d "
                        "ofi=%s cvd=%s → min_conf %.2f→%.2f",
                        "HH-HL" if ps == 1 else "LH-LL",
                        active_streak, ofi_ok, cvd_ok,
                        _TREND_MIN_CONF, _TREND_MIN_CONF_PRICE_BOOST,
                    )
            elif getattr(self, "_last_price_boost", False):
                logger.info(
                    "[TrendGate] 가격구조 부스트 OFF (ps=%+d streak=%d ofi=%s cvd=%s)",
                    ps, active_streak, ofi_ok, cvd_ok,
                )
        elif getattr(self, "_last_price_boost", False):
            logger.info("[TrendGate] 가격구조 부스트 OFF (ps=0)")
        self._last_price_boost = price_boost

        # ── [500차 D-2] 조건 A 섀도 — 라이브에 영향 없음 ────────────────
        # 플래그를 켰다면 어떻게 됐을지를 같은 규칙으로 굴려 "섀도만 active"였던
        # 분봉 수를 센다. 이 숫자가 켜기/두기 판단의 실측 근거가 된다.
        up_cond_sh = (above_vwap == 1 and (cvd_dir_real == 1 or ret_5m > 0))
        dn_cond_sh = (above_vwap == 0 and (cvd_dir_real == -1 or ret_5m < 0))
        self._up_streak_sh, self._up_fail_sh = _step_streak(
            self._up_streak_sh, self._up_fail_sh, up_cond_sh, up_hbreak, "UP-sh")
        self._dn_streak_sh, self._dn_fail_sh = _step_streak(
            self._dn_streak_sh, self._dn_fail_sh, dn_cond_sh, dn_hbreak, "DN-sh")
        up_active_sh = self._up_streak_sh >= _STREAK_ACTIVATE
        dn_active_sh = self._dn_streak_sh >= _STREAK_ACTIVATE
        self._sh_bars += 1
        if up_active_sh and not self._up_active:
            self._sh_up_extra += 1
        if dn_active_sh and not self._dn_active:
            self._sh_dn_extra += 1

        return {
            "up_active":          self._up_active,
            "up_streak":          self._up_streak,
            "dn_active":          self._dn_active,
            "dn_streak":          self._dn_streak,
            "min_conf_override":  min_conf_override,
            "price_structure":    ps,
            "price_boost_active": price_boost,
            # 섀도(관측 전용) — 소비처가 없어도 계측 4원칙 ④에 따라 노출한다.
            "cvd_cond_enabled":   _TREND_CVD_COND_ENABLED,
            "up_active_shadow":   up_active_sh,
            "dn_active_shadow":   dn_active_sh,
            "cvd_roll5":          round(cvd_roll, 4),
            "hard_break":         ("UP" if up_hbreak else
                                   ("DN" if dn_hbreak else "")),
        }

    # ── 일간 리셋 ──────────────────────────────────────────────────────
    def reset_daily(self):
        self._up_streak = self._up_fail_streak = 0
        self._up_active = False
        self._up_peak   = 0
        self._dn_streak = self._dn_fail_streak = 0
        self._dn_active = False
        self._dn_peak   = 0
        self._last_price_boost = False
        self._cdn_buf.clear()
        # [500차 D-2] 섀도 누적치는 **리셋 전에 남긴다** — 리셋과 저장이 같은
        # 함수에 있으면 기록이 항상 0이 된다(계측 4원칙 ④ `_ccf_today` 관례).
        if self._sh_bars:
            logger.info(
                "[TrendGate][섀도] 조건A(CVD 동조) enabled=%s — 관측 %d분 중 "
                "섀도만 활성 UP %d분(%.1f%%) / DN %d분(%.1f%%). "
                "켜면 이만큼 min_conf 완화가 늘어난다.",
                _TREND_CVD_COND_ENABLED, self._sh_bars,
                self._sh_up_extra, 100.0 * self._sh_up_extra / self._sh_bars,
                self._sh_dn_extra, 100.0 * self._sh_dn_extra / self._sh_bars,
            )
        self._up_streak_sh = self._up_fail_sh = 0
        self._dn_streak_sh = self._dn_fail_sh = 0
        self._sh_bars = self._sh_up_extra = self._sh_dn_extra = 0
        logger.debug("[TrendGate] 일간 리셋")

    # ── 진단 ───────────────────────────────────────────────────────────
    def status_dict(self) -> dict:
        return {
            "up_active":  self._up_active,
            "up_streak":  self._up_streak,
            "up_peak":    self._up_peak,
            "dn_active":  self._dn_active,
            "dn_streak":  self._dn_streak,
            "dn_peak":    self._dn_peak,
        }
