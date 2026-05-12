# challenger/variants/base_challenger.py — 도전자 추상 기반 클래스
"""
ChallengerSignal  : 매분 신호 dataclass
ChallengerTrade   : 가상 거래 dataclass
BaseChallenger    : 모든 도전자 공통 인터페이스
"""
import time
import logging
from abc import ABCMeta, abstractmethod
from typing import Optional, Dict, Any

logger = logging.getLogger("CHALLENGER")


class ChallengerSignal(object):
    """매분 신호 기록"""
    __slots__ = (
        "ts", "challenger_id", "direction",
        "confidence", "grade", "entry_price", "signal_meta",
    )

    def __init__(
        self,
        ts,            # str  'YYYY-MM-DD HH:MM:SS'
        challenger_id, # str
        direction,     # int  +1 / -1 / 0
        confidence,    # float 0.0~1.0
        grade,         # str  'A'/'B'/'C'/'X'
        entry_price,   # float | None
        signal_meta,   # dict  JSON-serializable
    ):
        self.ts           = ts
        self.challenger_id = challenger_id
        self.direction    = direction
        self.confidence   = confidence
        self.grade        = grade
        self.entry_price  = entry_price
        self.signal_meta  = signal_meta or {}


class ChallengerTrade(object):
    """가상 거래 상태 (열림/닫힘)"""
    __slots__ = (
        "trade_id", "challenger_id",
        "entry_ts", "exit_ts",
        "direction", "entry_price", "exit_price",
        "pnl_pt", "exit_reason", "grade",
        "atr_at_entry",
    )

    def __init__(
        self,
        trade_id,      # int | None (DB에서 할당)
        challenger_id, # str
        entry_ts,      # str
        direction,     # int +1/-1
        entry_price,   # float
        grade,         # str
        atr_at_entry,  # float  TP/SL 계산용
    ):
        self.trade_id     = trade_id
        self.challenger_id = challenger_id
        self.entry_ts     = entry_ts
        self.exit_ts      = None
        self.direction    = direction
        self.entry_price  = entry_price
        self.exit_price   = None
        self.pnl_pt       = None
        self.exit_reason  = None
        self.grade        = grade
        self.atr_at_entry = atr_at_entry


class ExitReason(object):
    TP1   = "TP1"
    TP2   = "TP2"
    SL    = "SL"
    FORCE = "FORCE"   # 15:10 강제 청산
    TIME  = "TIME"    # 시간 청산 (EOD 전)


class BaseChallenger(object):
    """
    모든 도전자 공통 인터페이스.

    서브클래스는 generate_signal() 만 구현하면 됨.
    청산 로직(should_exit)은 챔피언과 동일한 ATR TP/SL 방식 공용 사용.
    """
    __metaclass__ = ABCMeta   # Python 2 호환 (py37 ABCMeta)

    challenger_id = ""   # 'A_CVD_EXHAUSTION' 등
    name_kr       = ""   # 'CVD 탈진 감지'

    # ATR 기반 청산 배수 (챔피언과 동일)
    ATR_TP1_MULT = 1.0
    ATR_TP2_MULT = 1.5
    ATR_SL_MULT  = 1.5

    # 수수료: 편도 0.0015% (설계안 기준)
    COMMISSION_RATE = 0.000015

    def __init__(self):
        self.active = True
        self._open_trade = None   # type: Optional[ChallengerTrade]

    @abstractmethod
    def generate_signal(self, features, context):
        # type: (Dict[str, Any], Dict[str, Any]) -> ChallengerSignal
        """
        매분 호출 — 신호 생성.

        Args:
            features: feature_builder 출력 dict
            context:  {candle, atr, regime, ts, ...}

        Returns:
            ChallengerSignal
        """
        raise NotImplementedError

    def should_exit(self, trade, current_price, current_ts, atr=None):
        # type: (ChallengerTrade, float, str, Optional[float]) -> Optional[str]
        """
        열린 가상 포지션 청산 여부 판정.

        Returns:
            ExitReason 문자열 또는 None (계속 보유)
        """
        if trade is None:
            return None

        atr_val = atr if atr else trade.atr_at_entry
        if not atr_val or atr_val <= 0:
            return None

        tp1 = trade.entry_price + trade.direction * self.ATR_TP1_MULT * atr_val
        tp2 = trade.entry_price + trade.direction * self.ATR_TP2_MULT * atr_val
        sl  = trade.entry_price - trade.direction * self.ATR_SL_MULT  * atr_val

        if trade.direction == 1:
            if current_price >= tp2:
                return ExitReason.TP2
            if current_price >= tp1:
                return ExitReason.TP1
            if current_price <= sl:
                return ExitReason.SL
        else:  # direction == -1
            if current_price <= tp2:
                return ExitReason.TP2
            if current_price <= tp1:
                return ExitReason.TP1
            if current_price >= sl:
                return ExitReason.SL

        return None

    def calc_pnl(self, trade, exit_price):
        # type: (ChallengerTrade, float) -> float
        """
        포인트 손익 계산 (수수료 포함).
        KOSPI200 선물 1포인트 = 250,000원 기준이나 여기서는 pt 단위로 반환.
        """
        raw_pnl = (exit_price - trade.entry_price) * trade.direction
        # 편도 수수료 × 2 (진입+청산)
        commission = (trade.entry_price + exit_price) * self.COMMISSION_RATE * 2
        return round(raw_pnl - commission, 4)

    def _grade_from_confidence(self, confidence):
        # type: (float) -> str
        if confidence >= 0.70:
            return "A"
        if confidence >= 0.60:
            return "B"
        if confidence >= 0.55:
            return "C"
        return "X"
