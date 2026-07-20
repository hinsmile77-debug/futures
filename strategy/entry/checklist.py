# strategy/entry/checklist.py — 11개 진입 전 체크리스트
"""
11개 항목을 평가하여 통과 수와 등급을 결정합니다.

등급 기준(min_pass는 절대 개수 — 10·11번 항목 추가 후에도 그대로, §343차·360차 참조):
  A: 6개 이상 → ×1.5 자동 진입
  B: 4~5개   → ×1.0 자동 진입
  C: 2~3개   → ×0.6 자동 진입 (UI 'C 자동' 토글로 ON/OFF)
  X: 1개 이하 → 진입 금지
"""
import logging
from typing import Dict, Tuple

from config.constants import DIRECTION_UP, DIRECTION_DOWN, DIRECTION_FLAT
from config.settings import (
    ENTRY_GRADE, HORIZON_CORE_GROUP, CORE_FEATURES_BY_GROUP, ENS_CONF_FLOOR_FOR_AUTO,
    MR_EXHAUSTION_MIN, MR_EXHAUSTION_MIN_WEAK, MR_WEAK_SIZE_MULT,
    CHASE_FILTER_ENABLED, CHASE_FILTER_ATR_THRESHOLD, CHASE_FILTER_ATR_THRESHOLD_MEANREV,
    HURST_RANGE_THRESHOLD, HURST_TREND_THRESHOLD,
    COUNTERTREND_CAP_ENABLED, COUNTERTREND_ATR_THRESHOLD, COUNTERTREND_MAX_QTY,
)

logger = logging.getLogger("SIGNAL")


class EntryChecklist:
    """11개 진입 전 체크리스트"""

    def evaluate(
        self,
        direction: int,
        confidence: float,
        vwap_position: float,
        cvd_direction: float,
        ofi_pressure: int,
        foreign_call_net: float,
        foreign_put_net: float,
        prev_bar_direction: int,
        time_zone: str,
        daily_loss_pct: float,
        min_confidence: float = 0.58,
        bear_exhaustion: float = 0.0,
        bull_exhaustion: float = 0.0,
        micro_regime: str = "혼합",
        disabled_gates: set = None,
        entry_ok: float = 1.0,
        entry_horizon: str = "1m",
        macro_vix: float = 0.5,
        opt_chain_pcr: float = 0.0,
        ensemble_grade: str = None,
        hurst: float = 0.5,
        price_extension_atr: float = 0.0,
    ) -> Dict:
        """
        Args:
            direction:       앙상블 방향 (+1/-1)
            confidence:      앙상블 신뢰도
            vwap_position:   VWAP 위치 (양수=위, 음수=아래)
            cvd_direction:   cvd_delta_norm (-1~+1, price-action 기반 바 단위 방향)
            ofi_pressure:    OFI 압력 (+1/-1/0)
            foreign_call_net:   외인 콜 순매수
            foreign_put_net:    외인 풋 순매수
            prev_bar_direction: 직전 봉 방향 +1(양봉) / 0(도지) / -1(음봉)
            time_zone:          현재 시간대 코드
            daily_loss_pct:  당일 누적 손실률 (양수=손실)
            min_confidence:  레짐별 최소 신뢰도
            bear_exhaustion: 하락 압력 소진 강도 0.0~1.0 (LONG MR 분기용)
            bull_exhaustion: 상승 압력 소진 강도 0.0~1.0 (SHORT MR 분기용)
            micro_regime:    현재 미시 레짐 (탈진 레짐 시 Hurst 차단 무효화)
            disabled_gates:  UI 체크박스 OFF 항목의 내부 키 집합
                             (예: {"3_vwap", "6_foreign"}) — 해당 항목은 항상 통과 처리
            entry_horizon:   ATR 기반 진입 호라이즌 ("1m"~"30m") — CORE 그룹 결정에 사용
            macro_vix:       VIX 정규화값 [0,1] — 중기/장기 CORE 체크용
            opt_chain_pcr:   PCR 실측값 — 장기 CORE 체크용 (0이면 미가용)
            ensemble_grade:  앙상블 자체 등급(A/B/C/X) — X인데 체크리스트가 A/B로
                             승격시키려는 경우 정렬 강도(pass_count>=7) 추가 요구용
            hurst:           Hurst 지수 [0,1] — 10번 연장추격 필터 임계값 결정용
            price_extension_atr: (현재가-N분전가)/ATR, signed — 양수=상승 연장,
                             음수=하락 연장. 10번 연장추격 필터 입력값

        Returns:
            {pass_count, grade, checks, size_mult, auto_entry, entry_mode}
        """
        from collection.macro.micro_regime import REGIME_EXHAUSTION

        disabled = set(disabled_gates) if disabled_gates else set()

        # 호라이즌 CORE 그룹 결정
        _core_group = HORIZON_CORE_GROUP.get(entry_horizon, "short")
        _core_cfg   = CORE_FEATURES_BY_GROUP.get(_core_group, CORE_FEATURES_BY_GROUP["short"])

        if entry_ok == 0.0:
            logger.debug("[Checklist] entry_ok=0 (독성·품질·스프레드 미달) → 즉시 X등급")
            return {
                "pass_count": 0,
                "grade":      "X",
                "checks":     {"0_entry_ok": False},
                "size_mult":  0,
                "auto_entry": False,
                "entry_mode": "NO_ENTRY",
                "max_qty_override": None,
            }

        # FLAT 신호는 방향 없음 → SHORT로 오분류되어 8/9 통과 후 A등급 AUTO진입이
        # 발생하는 버그를 차단한다. 반드시 즉시 X등급 반환해야 한다.
        if direction == DIRECTION_FLAT:
            logger.debug("[Checklist] FLAT 방향 → 즉시 X등급 (진입 금지)")
            return {
                "pass_count": 0,
                "grade":      "X",
                "checks":     {"1_signal": False},
                "size_mult":  0,
                "auto_entry": False,
                "entry_mode": "NO_ENTRY",
                "max_qty_override": None,
            }

        is_long = direction == DIRECTION_UP
        is_exhaustion_regime = (micro_regime == REGIME_EXHAUSTION)

        checks = {}
        entry_mode = "TREND_FOLLOW"
        _countertrend_cap_triggered = False  # [360차] 11번 항목에서 갱신

        # 1. 앙상블 신호 방향 확인
        checks["1_signal"] = "1_signal" in disabled or direction in (DIRECTION_UP, DIRECTION_DOWN)

        # 2. 최소 신뢰도 (탈진 레짐은 0.56으로 완화)
        min_conf_effective = 0.56 if is_exhaustion_regime else min_confidence
        checks["2_confidence"] = "2_confidence" in disabled or confidence >= min_conf_effective
        if not checks["2_confidence"]:
            logger.warning(
                "[Checklist] 신뢰도 미달 %.1f%% < %.1f%% → 강제 X등급",
                confidence * 100, min_conf_effective * 100,
            )
            return {
                "pass_count":        1,
                "grade":             "X",
                "checks":            checks,
                "size_mult":         0,
                "auto_entry":        False,
                "entry_mode":        entry_mode,
                "conf_check_failed": True,   # [P3] 신뢰도 차단 식별 플래그
                "max_qty_override":  None,
            }

        # 3. VWAP 위치
        # LONG MR: VWAP 하방 1.5σ 초과 + 하락 압력 소진(bear_exhaustion) → 역추세 매수
        # SHORT MR: VWAP 상방 1.5σ 초과 + 상승 압력 소진(bull_exhaustion) → 역추세 매도
        # 273차: 0.70 단일 컷오프 대신 0.60~0.70을 "약한 MR"로 허용(사이즈 축소).
        # Hurst<0.45 횡보 구간에서 MR이 사실상 발동 0회였던 문제 완화용.
        _mr_weak = False
        if "3_vwap" in disabled:
            checks["3_vwap"] = True
        elif is_long:
            # MR LONG: VWAP -1.5σ 초과 하락 + bear_exhaustion 최소강도 이상(≥0.60)
            if vwap_position < -1.5 and bear_exhaustion >= MR_EXHAUSTION_MIN_WEAK:
                checks["3_vwap"] = True
                entry_mode = "MEAN_REVERSION"
                _mr_weak = bear_exhaustion < MR_EXHAUSTION_MIN
            else:
                checks["3_vwap"] = vwap_position > 0
        else:
            # MR SHORT: VWAP +1.5σ 초과 상승 + bull_exhaustion 최소강도 이상(≥0.60)
            if vwap_position > 1.5 and bull_exhaustion >= MR_EXHAUSTION_MIN_WEAK:
                checks["3_vwap"] = True
                entry_mode = "MEAN_REVERSION"
                _mr_weak = bull_exhaustion < MR_EXHAUSTION_MIN
            else:
                checks["3_vwap"] = vwap_position < 0

        # 4. CVD / 중기·장기 대체 신호 체크
        # 단기(1m~5m): cvd_delta_norm — price-action 기반 바 단위 방향 (>0=매수압, <0=매도압)
        #   ※ cvd_direction(구 이산 -1/0/+1)에서 교체 (2026-06-25):
        #      Cybos buy_vol 시스템 편향으로 cvd_direction이 +0.5 고착(98.6%)되어
        #      사실상 상수화. cvd_delta_norm은 동일 정보를 price-action으로 올바르게 표현.
        # 중기(10m~15m): 면제 — CVD·OFI·macro_vix 모두 중기 유의성 없음 (2026-06-25)
        #   macro_vix는 일봉 VIX 상수, SHAP 기여 ≈ 0, 임계 VIX 27.5는 평상시 항상 통과
        # 장기(30m): opt_chain_pcr 방향 — PCR<1.0=콜우세=LONG, >1.0=풋우세=SHORT (미가용 시 면제)
        if "4_cvd" in disabled:
            checks["4_cvd"] = True
        elif _core_group == "short":
            checks["4_cvd"] = cvd_direction > 0 if is_long else cvd_direction < 0
        elif _core_group == "mid":
            checks["4_cvd"] = True  # CVD·OFI·macro_vix 모두 면제
        else:  # long
            if opt_chain_pcr > 0:
                checks["4_cvd"] = (opt_chain_pcr < 1.0) if is_long else (opt_chain_pcr > 1.0)
            else:
                checks["4_cvd"] = True  # PCR 미가용 → 면제

        # 5. OFI / 중기·장기 대체 신호 체크
        # 단기: OFI 압력 — 1~3분 선행 신호
        # 중기/장기: OFI 틱 잡음 → 면제(자동 통과)
        if "5_ofi" in disabled:
            checks["5_ofi"] = True
        elif _core_group == "short":
            checks["5_ofi"] = ofi_pressure > 0 if is_long else ofi_pressure < 0
        else:
            checks["5_ofi"] = True  # 중기·장기: OFI 면제

        # 6. 외인 방향 (콜/풋 순매수 양수 AND 상대우위 — 둘 다 충족해야 통과)
        if "6_foreign" in disabled:
            checks["6_foreign"] = True
        elif is_long:
            checks["6_foreign"] = foreign_call_net > 0 and foreign_call_net > foreign_put_net
        else:
            checks["6_foreign"] = foreign_put_net > 0 and foreign_put_net > foreign_call_net

        # 7. 직전 봉
        # 트렌드 추종: LONG=양봉만, SHORT=음봉만 (도지 불허)
        # MR(평균회귀): 반전 직전 봉이 추세 방향 or 도지여야 정상 → 조건 완화
        #   MR LONG : 하락 탈진 반전 → 직전 봉이 음봉(-1) 또는 도지(0) 허용
        #   MR SHORT: 상승 탈진 반전 → 직전 봉이 양봉(+1) 또는 도지(0) 허용
        if "7_prev_bar" in disabled:
            checks["7_prev_bar"] = True
        elif entry_mode == "MEAN_REVERSION":
            if is_long:
                checks["7_prev_bar"] = prev_bar_direction in (-1, 0)
            else:
                checks["7_prev_bar"] = prev_bar_direction in (0, 1)
        elif is_long:
            checks["7_prev_bar"] = prev_bar_direction == 1   # 양봉만
        else:
            checks["7_prev_bar"] = prev_bar_direction == -1  # 음봉만

        # 8. 시간 필터 (금지 구간 외)
        checks["8_time"] = "8_time" in disabled or time_zone not in ("EXIT_ONLY", "OTHER")

        # 9. 리스크 한도 (일일 손실 < 2%)
        checks["9_risk"] = "9_risk" in disabled or daily_loss_pct < 0.02

        # 10. 연장 추격 필터(anti-chasing, 343차) — 직전 CHASE_FILTER_LOOKBACK_MIN분간
        # 이미 임계 ATR 이상 같은 방향으로 연장된 뒤 순방향(추격) 진입인지 확인.
        # 7/15 진입 딥다이브: 4패 전부가 이 패턴(직전 연장 ≥2ATR 후 순방향 진입)이었음.
        # Hurst 평균회귀(<HURST_RANGE_THRESHOLD) 구간은 반전 리스크가 커 임계값을 더 좁힌다.
        # 하드 차단이 아니라 pass_count 반영만 — 등급이 자연히 낮아진다(4_cvd·5_ofi와 동일).
        if "10_chase" in disabled or not CHASE_FILTER_ENABLED:
            checks["10_chase"] = True
        else:
            _chase_threshold = (
                CHASE_FILTER_ATR_THRESHOLD_MEANREV if hurst < HURST_RANGE_THRESHOLD
                else CHASE_FILTER_ATR_THRESHOLD
            )
            _is_chasing_dir = (price_extension_atr > 0) == is_long
            _chase_triggered = _is_chasing_dir and abs(price_extension_atr) > _chase_threshold
            checks["10_chase"] = not _chase_triggered
            if _chase_triggered:
                logger.info(
                    "[Checklist] 연장추격 감지 — |ext|=%.2fATR > %.2f (hurst=%.3f, dir=%s)"
                    " → pass_count-1",
                    abs(price_extension_atr), _chase_threshold, hurst,
                    "LONG" if is_long else "SHORT",
                )

        # 11. 역추세 진입 필터(anti-countertrend, 360차) — hurst>=HURST_TREND_THRESHOLD
        # (추세 지속 확인) 구간에서 price_extension_atr(10번과 동일 피처) 연장 방향과
        # 반대로 진입하는지 확인. 0720 유일 손실(포지션6, hurst=trend, SHORT 2계약,
        # -523,099원)이 이 패턴 — 추세 지속이 확인된 구간에서 그 추세를 거스르면 지속
        # 추세에 계속 밀릴 위험이 크다. entry_mode=MEAN_REVERSION(3번 VWAP 분기, 의도적
        # 역추세 전략)은 예외 — exhaustion 기반 사이징과 충돌 방지. 10번과 동일하게
        # 하드 차단이 아니라 pass_count만 반영하고, 트리거 시 수량은 이후
        # PositionSizer.compute(max_qty_override=COUNTERTREND_MAX_QTY)로 캡된다.
        if ("11_countertrend" in disabled or not COUNTERTREND_CAP_ENABLED
                or entry_mode == "MEAN_REVERSION"):
            checks["11_countertrend"] = True
        else:
            _is_countertrend_dir = (price_extension_atr > 0) != is_long
            _countertrend_cap_triggered = (
                hurst >= HURST_TREND_THRESHOLD
                and _is_countertrend_dir
                and abs(price_extension_atr) > COUNTERTREND_ATR_THRESHOLD
            )
            checks["11_countertrend"] = not _countertrend_cap_triggered
            if _countertrend_cap_triggered:
                logger.info(
                    "[Checklist] 역추세 진입 감지 — hurst=%.3f ext=%.2fATR(반대) > %.2f dir=%s"
                    " → pass_count-1, 수량 %d계약 캡",
                    hurst, abs(price_extension_atr), COUNTERTREND_ATR_THRESHOLD,
                    "LONG" if is_long else "SHORT", COUNTERTREND_MAX_QTY,
                )

        pass_count = sum(1 for v in checks.values() if v)

        # VWAP 강제 X — 그룹별 적용 여부 결정
        # 단기·중기: 기관 알고리즘 기준선 위반 → 강제 X
        # 장기(30m): above_vwap 이진 대체 사용, 강제 X 해제 → pass_count 반영만
        _vwap_forced_x = _core_cfg.get("vwap_forced_x", True)
        if not checks["3_vwap"]:
            _need = ">0 (LONG)" if is_long else "<0 (SHORT)"
            _diag = (
                f"VWAP pos={vwap_position:+.3f} need {_need}"
                + (f" bear_exh={bear_exhaustion:.2f}" if is_long else f" bull_exh={bull_exhaustion:.2f}")
            )
            if _vwap_forced_x:
                logger.warning(
                    "[Checklist] CORE VWAP ✗ → 강제 X등급 (pass_count=%d, group=%s) | %s",
                    pass_count, _core_group, _diag,
                )
                return {
                    "pass_count": pass_count,
                    "grade":      "X",
                    "checks":     checks,
                    "size_mult":  0,
                    "auto_entry": False,
                    "entry_mode": entry_mode,
                    "max_qty_override": None,
                }
            else:
                logger.info(
                    "[Checklist] CORE VWAP ✗ — 장기 그룹 강제X 해제, pass_count 반영 (pass_count=%d) | %s",
                    pass_count, _diag,
                )

        # 4번(CVD/대체)·5번(OFI/대체) 불일치: pass_count에 반영됨 — 진단 로그만
        if not checks["4_cvd"] or not checks["5_ofi"]:
            _fail_keys = [k for k in ("4_cvd", "5_ofi") if not checks[k]]
            _diag_parts = []
            if not checks["4_cvd"]:
                if _core_group == "short":
                    _need_cvd = ">0" if is_long else "<0"
                    _diag_parts.append(f"cvd_delta_norm={cvd_direction:+.3f} need {_need_cvd}")
                else:  # long (mid는 항상 True이므로 여기 도달 불가)
                    _diag_parts.append(f"opt_chain_pcr={opt_chain_pcr:.3f} need {'<1.0' if is_long else '>1.0'}")
            if not checks["5_ofi"] and _core_group == "short":
                _need_ofi = ">0" if is_long else "<0"
                _diag_parts.append(f"OFI pres={ofi_pressure:+d} need {_need_ofi}")
            logger.info(
                "[Checklist] CORE 4·5 ✗ %s (group=%s) — pass_count-1 적용 (pass_count=%d) | %s",
                _fail_keys, _core_group, pass_count, "  |  ".join(_diag_parts),
            )

        # 등급 결정
        if pass_count >= ENTRY_GRADE["A"]["min_pass"]:
            grade = "A"
        elif pass_count >= ENTRY_GRADE["B"]["min_pass"]:
            grade = "B"
        elif pass_count >= ENTRY_GRADE["C"]["min_pass"]:
            grade = "C"
        else:
            grade = "X"

        size_mult  = ENTRY_GRADE[grade]["size_mult"]
        auto_entry = ENTRY_GRADE[grade]["auto"]

        # [311차] ensemble_grade=X인데 체크리스트가 A/B로 승격 — 정렬강도(pass_count>=7) 요구.
        # 근거: X→A 재구성 backtest(06-15~07-10, n=124)에서 pass=6(A 최저컷)은 +15m 평균
        # -0.50pt(t=-0.31, 승률50%)로 음수인 반면 pass>=7은 +2.57pt(승률61%)로 반전 확인.
        # CoherenceGate/CascadeCoherence가 앙상블을 X로 막은 근거(호라이즌 간 불일치)와
        # 체크리스트의 오더플로 정렬 근거가 충돌할 때, 최소 정렬 수준만 걸러 꼬리위험 완화.
        if ensemble_grade == "X" and grade in ("A", "B") and pass_count < 7:
            logger.info(
                "[Checklist] ensemble=X 승격 차단 — pass_count=%d < 7 (원등급=%s) → X",
                pass_count, grade,
            )
            grade      = "X"
            size_mult  = 0
            auto_entry = False

        # 약한 MR(exhaustion 0.60~0.70) — 정상 진입은 허용하되 사이즈 축소
        if _mr_weak and grade != "X":
            size_mult = round(size_mult * MR_WEAK_SIZE_MULT, 3)
            logger.info(
                "[Checklist] MR 약한탈진(0.60~0.70) → 사이즈×%s 축소 (등급=%s)",
                MR_WEAK_SIZE_MULT, grade,
            )

        # conf < ENS_CONF_FLOOR_FOR_AUTO → A/B 등급이어도 자동진입 차단
        # 체크리스트 구조가 맞아도 앙상블이 33% 미만이면 EV 음수 (5일 실거래 분석 근거)
        # 대시보드에는 원래 등급(A/B)이 표시되어 수동 확인은 가능하다
        if auto_entry and confidence < ENS_CONF_FLOOR_FOR_AUTO:
            auto_entry = False
            logger.info(
                "[Checklist] conf=%.1f%% < floor=%.1f%% → 등급=%s 유지, auto_entry=OFF (수동확인 필요)",
                confidence * 100, ENS_CONF_FLOOR_FOR_AUTO * 100, grade,
            )

        # [360차] 역추세 진입 캡 — 11번 항목에서 트리거된 경우 수량 상한을 반환값에 싣는다.
        # size_mult는 건드리지 않는다(kelly_advised_skip 오염 방지, 상세 근거는
        # position_sizer.py 참조) — PositionSizer.compute()가 별도 파라미터로 적용.
        max_qty_override = COUNTERTREND_MAX_QTY if _countertrend_cap_triggered else None

        logger.info(
            "[Checklist] 통과 %d/11 → 등급 %s (자동=%s, 배수×%s, 모드=%s, group=%s)%s",
            pass_count, grade, auto_entry, size_mult, entry_mode, _core_group,
            f" [역추세캡 {max_qty_override}계약]" if max_qty_override else "",
        )

        return {
            "pass_count": pass_count,
            "grade":      grade,
            "checks":     checks,
            "size_mult":  size_mult,
            "auto_entry": auto_entry,
            "entry_mode": entry_mode,
            "max_qty_override": max_qty_override,
        }
