# strategy/entry/checklist.py — 9개 진입 전 체크리스트
"""
9개 항목을 평가하여 통과 수와 등급을 결정합니다.

등급 기준:
  A: 6개 이상 → ×1.5 자동 진입
  B: 4~5개   → ×1.0 자동 진입
  C: 2~3개   → ×0.6 자동 진입 (UI 'C 자동' 토글로 ON/OFF)
  X: 1개 이하 → 진입 금지
"""
import logging
from typing import Dict, Tuple

from config.constants import DIRECTION_UP, DIRECTION_DOWN, DIRECTION_FLAT
from config.settings import ENTRY_GRADE, HORIZON_CORE_GROUP, CORE_FEATURES_BY_GROUP, ENS_CONF_FLOOR_FOR_AUTO

logger = logging.getLogger("SIGNAL")


class EntryChecklist:
    """9개 진입 전 체크리스트"""

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
            }

        is_long = direction == DIRECTION_UP
        is_exhaustion_regime = (micro_regime == REGIME_EXHAUSTION)

        checks = {}
        entry_mode = "TREND_FOLLOW"

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
            }

        # 3. VWAP 위치
        # LONG MR: VWAP 하방 1.5σ 초과 + 하락 압력 소진(bear_exhaustion) → 역추세 매수
        # SHORT MR: VWAP 상방 1.5σ 초과 + 상승 압력 소진(bull_exhaustion) → 역추세 매도
        if "3_vwap" in disabled:
            checks["3_vwap"] = True
        elif is_long:
            if vwap_position < -1.5 and bear_exhaustion > 0.0:
                checks["3_vwap"] = True
                entry_mode = "MEAN_REVERSION"
            else:
                checks["3_vwap"] = vwap_position > 0
        else:
            if vwap_position > 1.5 and bull_exhaustion > 0.0:
                checks["3_vwap"] = True
                entry_mode = "MEAN_REVERSION"
            else:
                checks["3_vwap"] = vwap_position < 0

        # 4. CVD / 중기·장기 대체 신호 체크
        # 단기(1m~5m): cvd_delta_norm — price-action 기반 바 단위 방향 (>0=매수압, <0=매도압)
        #   ※ cvd_direction(구 이산 -1/0/+1)에서 교체 (2026-06-25):
        #      Cybos buy_vol 시스템 편향으로 cvd_direction이 +0.5 고착(98.6%)되어
        #      사실상 상수화. cvd_delta_norm은 동일 정보를 price-action으로 올바르게 표현.
        # 중기(10m~15m): macro_vix 방향 — VIX<0.5=저공포=LONG 유리, >0.5=고공포=SHORT 유리
        # 장기(30m): opt_chain_pcr 방향 — PCR<1.0=콜우세=LONG, >1.0=풋우세=SHORT (미가용 시 면제)
        if "4_cvd" in disabled:
            checks["4_cvd"] = True
        elif _core_group == "short":
            checks["4_cvd"] = cvd_direction > 0 if is_long else cvd_direction < 0
        elif _core_group == "mid":
            # macro_vix [0,1] — 낮을수록 위험선호(LONG 유리)
            checks["4_cvd"] = (macro_vix < 0.5) if is_long else (macro_vix > 0.5)
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

        # 7. 직전 봉 (도지=0은 양쪽 모두 불통과)
        if "7_prev_bar" in disabled:
            checks["7_prev_bar"] = True
        elif is_long:
            checks["7_prev_bar"] = prev_bar_direction == 1   # 양봉만
        else:
            checks["7_prev_bar"] = prev_bar_direction == -1  # 음봉만

        # 8. 시간 필터 (금지 구간 외)
        checks["8_time"] = "8_time" in disabled or time_zone not in ("EXIT_ONLY", "OTHER")

        # 9. 리스크 한도 (일일 손실 < 2%)
        checks["9_risk"] = "9_risk" in disabled or daily_loss_pct < 0.02

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
                elif _core_group == "mid":
                    _diag_parts.append(f"macro_vix={macro_vix:.2f} need {'<0.5' if is_long else '>0.5'}")
                else:
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

        # conf < ENS_CONF_FLOOR_FOR_AUTO → A/B 등급이어도 자동진입 차단
        # 체크리스트 구조가 맞아도 앙상블이 33% 미만이면 EV 음수 (5일 실거래 분석 근거)
        # 대시보드에는 원래 등급(A/B)이 표시되어 수동 확인은 가능하다
        if auto_entry and confidence < ENS_CONF_FLOOR_FOR_AUTO:
            auto_entry = False
            logger.info(
                "[Checklist] conf=%.1f%% < floor=%.1f%% → 등급=%s 유지, auto_entry=OFF (수동확인 필요)",
                confidence * 100, ENS_CONF_FLOOR_FOR_AUTO * 100, grade,
            )

        logger.info(
            "[Checklist] 통과 %d/9 → 등급 %s (자동=%s, 배수×%s, 모드=%s, group=%s)",
            pass_count, grade, auto_entry, size_mult, entry_mode, _core_group,
        )

        return {
            "pass_count": pass_count,
            "grade":      grade,
            "checks":     checks,
            "size_mult":  size_mult,
            "auto_entry": auto_entry,
            "entry_mode": entry_mode,
        }
