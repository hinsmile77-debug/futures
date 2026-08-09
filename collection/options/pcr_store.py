# collection/options/pcr_store.py
"""
PCR (Put/Call Ratio) 저장소

CybosInvestorData.get_features()에서 외인 콜/풋 순매수를 받아
PCR과 추세를 계산한다.

- PCR > 1 : 풋 우세 → 하락 헤지 증가 → 약세 신호
- PCR < 1 : 콜 우세 → 상승 베팅 → 강세 신호
- PCR 극단값 역발상: PCR > 1.5는 과도한 공포 → 반등 가능성

데이터 가용성 주의:
  CybosInvestorData._option_flow_supported == True 일 때만 유효 데이터.
  미지원 시 PCR=1.0(중립) 반환.
"""
import logging
from collections import deque
from typing import Dict, Optional

logger = logging.getLogger("OPTIONS")

# 롤링 윈도우 (분봉 단위)
PCR_WINDOW = 20

# PCR 해석 임계치
PCR_BEARISH_THRESHOLD         = 1.2   # 이 이상: 풋 우세 (약세)
PCR_BULLISH_THRESHOLD         = 0.8   # 이 이하: 콜 우세 (강세)
PCR_EXTREME_THRESHOLD         = 1.5   # 이 이상: 풋 과잉 (역발상 반등 신호) — bearish extreme
PCR_EXTREME_BULLISH_THRESHOLD = 0.67  # 이 이하: 콜 과잉 (역발상 매도 신호) — bullish extreme (= 1/1.5)

# 저활동 방어: max(|call|,|put|)가 이 미만이면 양쪽 모두 미미한 장초반 노이즈 → 스킵
# [2026-08-09 재설계] 구 가드 PCR_MIN_CALL_ABS=1000(63차)은 계약수 스케일 가정이었으나
# CpSvrNew7221 옵션 순매수는 입력 ord('1')=금액 단위이고, '순매수'는 방향 균형일에
# 하루 종일 수백 수준에 머물 수 있어(2026-08-04 |call| max=798, 08-07 p95=904)
# 절대 임계 1000이 그런 날 opt_pcr_* 8종을 전면 사망시켰다(08-04 0%, 08-07 0.8% 가용).
# 62일(2026-05-11~08-07) DATA 로그 재생 실측: 신 가드 가용률 99.8% (구 81.5%),
# 63차 원버그 케이스(call=0·put≠0, 33행)는 아래 call_abs==0 스킵이 전부 방어.
PCR_MIN_ACTIVITY_ABS = 100

# PCR 극단값 상한 — 콜≈0 상태에서 생성되는 수억 단위 PCR 방어
PCR_MAX = 4.0


class PCRStore:
    """
    분봉마다 investor_data.get_features()를 받아 PCR 이력을 관리한다.

    사용:
        pcr_store.update(investor_feats)      # 매분 호출
        feats = pcr_store.get_features()      # OptionFeatureCalculator로 전달
    """

    def __init__(self, window: int = PCR_WINDOW):
        self._window = window
        self._pcr_buf:      deque = deque(maxlen=window)
        self._call_buf:     deque = deque(maxlen=window)
        self._put_buf:      deque = deque(maxlen=window)
        self._available = False
        self._last_pcr: Optional[float] = None

    # ── 매분 호출 ──────────────────────────────────────────────
    def update(self, investor_feats: Dict[str, float]) -> None:
        """
        Args:
            investor_feats: CybosInvestorData.get_features() 반환값
                            foreign_call_net, foreign_put_net 키 사용
        """
        call_net = investor_feats.get("foreign_call_net", 0.0)
        put_net  = investor_feats.get("foreign_put_net",  0.0)

        # 두 값이 모두 0이면 미수집 상태 — 중립 처리
        if call_net == 0.0 and put_net == 0.0:
            self._available = False
            return

        call_abs = abs(call_net)
        put_abs  = abs(put_net)

        # ① 장 시작 직후 콜 데이터 미로드 방어(63차 원버그: call=0·put≠0 → PCR 폭주).
        #    진짜 순매수 0과 미로드를 구분할 수 없으므로 스킵한다(실측 0.14%).
        if call_abs == 0:
            self._available = False
            logger.debug(
                "[PCRStore] call_abs=0 → 미로드 스킵 (put_abs=%+.0f)", put_abs,
            )
            return

        # ② 저활동 방어: 콜·풋 모두 미미하면 비율 자체가 노이즈 → 스킵.
        if max(call_abs, put_abs) < PCR_MIN_ACTIVITY_ABS:
            self._available = False
            logger.debug(
                "[PCRStore] max(|call|,|put|)=%.0f < %d → 저활동 스킵",
                max(call_abs, put_abs), PCR_MIN_ACTIVITY_ABS,
            )
            return

        self._available = True
        self._call_buf.append(call_net)
        self._put_buf.append(put_net)

        # 양수 기준 PCR: |put| / |call|, 극단값 상한 PCR_MAX 적용
        pcr = min(put_abs / call_abs, PCR_MAX)
        self._pcr_buf.append(round(pcr, 4))
        self._last_pcr = pcr

        logger.debug(
            "[PCRStore] call_net=%+.0f put_net=%+.0f PCR=%.3f",
            call_net, put_net, pcr,
        )

    def get_features(self) -> Dict[str, float]:
        """
        PCR 기반 피처 반환 (미수집 시 중립 기본값).

        Returns:
            pcr_current         — 현재 PCR (1.0=중립)
            pcr_ma              — 롤링 평균 PCR
            pcr_bearish         — 1.0 if PCR ≥ 1.2 (약세 신호)
            pcr_bullish         — 1.0 if PCR ≤ 0.8 (강세 신호)
            pcr_extreme         — 1.0 if PCR ≥ 1.5 (deprecated — pcr_extreme_bearish 사용)
            pcr_extreme_bearish — 1.0 if PCR ≥ 1.5 (풋 과잉 → 역발상 반등)
            pcr_extreme_bullish — 1.0 if PCR ≤ 0.67 (콜 과잉 → 역발상 매도)
            pcr_extreme_signed  — [-1, +1] 연속 강도 (음수=콜 극단, 양수=풋 극단)
            pcr_slope           — PCR 추세 (최근 - 이전 평균)
            pcr_available       — 1.0 if 실데이터, 0.0 if 추정
        """
        if not self._available or len(self._pcr_buf) == 0:
            return self._neutral()

        buf = list(self._pcr_buf)
        n   = len(buf)
        pcr = buf[-1]
        ma  = sum(buf) / n

        # PCR 추세: 최근 반쪽 평균 - 앞 반쪽 평균
        if n >= 4:
            mid = n // 2
            slope = (sum(buf[mid:]) / (n - mid)) - (sum(buf[:mid]) / mid)
        else:
            slope = 0.0

        # pcr_extreme_signed: 풋 극단이 양수, 콜 극단이 음수 (중립=1.0 기준 대칭)
        pcr_extreme_signed = round(
            max(min((pcr - 1.0) / 0.5, 1.0), -1.0), 4
        )

        return {
            "pcr_current":          round(pcr, 4),
            "pcr_ma":               round(ma, 4),
            "pcr_bearish":          1.0 if pcr >= PCR_BEARISH_THRESHOLD         else 0.0,
            "pcr_bullish":          1.0 if pcr <= PCR_BULLISH_THRESHOLD         else 0.0,
            "pcr_extreme":          1.0 if pcr >= PCR_EXTREME_THRESHOLD         else 0.0,  # deprecated
            "pcr_extreme_bearish":  1.0 if pcr >= PCR_EXTREME_THRESHOLD         else 0.0,
            "pcr_extreme_bullish":  1.0 if pcr <= PCR_EXTREME_BULLISH_THRESHOLD else 0.0,
            "pcr_extreme_signed":   pcr_extreme_signed,
            "pcr_slope":            round(slope, 4),
            "pcr_available":        1.0,
        }

    @staticmethod
    def _neutral() -> Dict[str, float]:
        return {
            "pcr_current":          1.0,
            "pcr_ma":               1.0,
            "pcr_bearish":          0.0,
            "pcr_bullish":          0.0,
            "pcr_extreme":          0.0,  # deprecated
            "pcr_extreme_bearish":  0.0,
            "pcr_extreme_bullish":  0.0,
            "pcr_extreme_signed":   0.0,
            "pcr_slope":            0.0,
            "pcr_available":        0.0,
        }

    def reset_daily(self) -> None:
        self._pcr_buf.clear()
        self._call_buf.clear()
        self._put_buf.clear()
        self._available = False
        self._last_pcr  = None
