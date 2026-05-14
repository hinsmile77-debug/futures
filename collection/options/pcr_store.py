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
PCR_BEARISH_THRESHOLD  = 1.2   # 이 이상: 풋 우세 (약세)
PCR_BULLISH_THRESHOLD  = 0.8   # 이 이하: 콜 우세 (강세)
PCR_EXTREME_THRESHOLD  = 1.5   # 이 이상: 과공포 (역발상 반등 신호)


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

        self._available = True
        self._call_buf.append(call_net)
        self._put_buf.append(put_net)

        # 양수 기준 PCR: |put| / |call|
        call_abs = abs(call_net)
        put_abs  = abs(put_net)
        pcr = put_abs / (call_abs + 1e-6)
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
            pcr_current    — 현재 PCR (1.0=중립)
            pcr_ma         — 롤링 평균 PCR
            pcr_bearish    — 1.0 if PCR ≥ BEARISH_THRESHOLD
            pcr_bullish    — 1.0 if PCR ≤ BULLISH_THRESHOLD
            pcr_extreme    — 1.0 if PCR ≥ EXTREME_THRESHOLD (역발상 신호)
            pcr_slope      — PCR 추세 (최근 - 이전 평균)
            pcr_available  — 1.0 if 실데이터, 0.0 if 추정
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

        return {
            "pcr_current":   round(pcr, 4),
            "pcr_ma":        round(ma, 4),
            "pcr_bearish":   1.0 if pcr >= PCR_BEARISH_THRESHOLD  else 0.0,
            "pcr_bullish":   1.0 if pcr <= PCR_BULLISH_THRESHOLD  else 0.0,
            "pcr_extreme":   1.0 if pcr >= PCR_EXTREME_THRESHOLD  else 0.0,
            "pcr_slope":     round(slope, 4),
            "pcr_available": 1.0,
        }

    @staticmethod
    def _neutral() -> Dict[str, float]:
        return {
            "pcr_current":   1.0,
            "pcr_ma":        1.0,
            "pcr_bearish":   0.0,
            "pcr_bullish":   0.0,
            "pcr_extreme":   0.0,
            "pcr_slope":     0.0,
            "pcr_available": 0.0,
        }

    def reset_daily(self) -> None:
        self._pcr_buf.clear()
        self._call_buf.clear()
        self._put_buf.clear()
        self._available = False
        self._last_pcr  = None
