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
        "atr_at_entry", "trail_extreme",
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
        self.trail_extreme = None   # 트레일 전용 변형(should_exit 오버라이드)이 갱신하는 고점/저점


class ExitReason(object):
    TP1   = "TP1"
    TP2   = "TP2"
    SL    = "SL"
    TRAIL = "TRAIL"   # 트레일 스톱 청산 (TP1 스킵 변형 전용)
    FORCE = "FORCE"   # 도전자별 강제 청산 시각 도달 (BaseChallenger.FORCE_EXIT_TIME)
    TIME  = "TIME"    # 시간 청산 (EOD 전)
    # ── [MW0601 553차 Phase 2] 미청산 누수 차단 ──────────────────────────────
    # 🔴 파이프라인은 15:10 이후 봉을 처리하지 않는다(main.py `_on_candle_closed` 의
    #   force-exit 분기가 return). 마지막 처리 봉은 15:08 이라 엔진의 15:10 안전망은
    #   **한 번도 발화한 적이 없다.** 그래서 마감 훅에서 남은 포지션을 여기서 닫는다.
    EOD_FORCE = "EOD_FORCE"        # 일 마감 시 그날 마지막 종가로 강제 청산
    # 프로세스가 죽어 인메모리 상태를 잃은 뒤 **다음 기동에서** 발견된 미청산 행.
    # 청산가를 그날 마지막 종가로 **재구성**한 것이므로 관측값이 아니다 — 이름으로 남긴다.
    EOD_FORCE_RECON = "EOD_FORCE_RECON"


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

    # ── [MW0601 553차 Phase 2] 도전자별 강제 청산 시각 ──────────────────────
    # 기본은 종전과 같은 15:10(절대원칙 §1). GP 규칙 도전자는 "15:05" 로 덮어쓴다.
    # ⚠ 실제로는 파이프라인이 15:10 이후 봉을 안 주므로 15:10 은 발화하지 않는다 —
    #   그 경우 마감 훅의 `EOD_FORCE` 가 닫는다.
    FORCE_EXIT_TIME = "15:10"

    # ── [MW0601 553차 Phase 2] 등급 개념이 없는 도전자 ──────────────────────
    # 🔴 엔진 진입 게이트가 `grade in ("A","B")` 로 고정돼 있어, 등급이 없는 규칙
    #   도전자(GP 등)는 통과하려고 `grade="A"` 를 지어내게 된다 — **등급 위장**이며
    #   계측 4원칙 ④ 위반이다. `GRADE_NA = True` 로 선언하면 엔진이 등급 조건을
    #   건너뛰고, 신호는 등급을 "-" 로 정직하게 기록한다.
    GRADE_NA = False

    # ── [MW0601 553차 Phase 3] 일일 진입 상한 ────────────────────────────────
    # None = 상한 없음(종전 동작). GP 숏 규칙은 「당일 최초 1회」라 1 이다.
    # 🔴 엔진이 **DB 기준**으로 센다 — 인메모리 플래그는 재시작이 지운다
    #   (552-10·552-11과 같은 계열).
    MAX_PER_DAY = None

    def __init__(self):
        self.active = True
        self._open_trade = None   # type: Optional[ChallengerTrade]

    def observe(self, features, context):
        # type: (Dict[str, Any], Dict[str, Any]) -> None
        """[553차 Phase 3] 매분, **청산 판정보다 먼저** 현재 봉을 보여준다.

        `should_exit()` 는 가격·ts·atr 만 받으므로 피처를 보는 청산 규칙
        (GP 숏의 「GS ≥ 1.2 도달」)이 이 훅 없이는 **직전 봉** 피처로 판정하게 된다.
        1봉 지연은 청산 규칙을 다른 규칙으로 바꾼다.

        기본은 무동작 — 기존 도전자의 동작은 바뀌지 않는다.
        """
        return None

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
        """포인트 순손익 — 수수료 + 슬리피지 차감.

        🔴 [553차 Phase 2] 자체 공식을 버리고 `challenger_cost` 한 벌로 모았다.
          종전 이 메서드와 엔진의 `_calc_pnl()` 이 **같은 공식을 두 벌** 들고 있었고
          둘 다 편도 요율을 키움 잔재 `1.5e-05` 로 하드코딩(실제의 1/6.54) + 슬리피지
          누락이었다. 값은 채널 스펙에서 파생한다(핀값 금지, 493차).

        ⚠ 반환 단위는 pt 다. 원화는 **미니선물 50,000원/pt** 이며 250,000 이 아니다
          (종전 이 독스트링이 250,000 이라 적고 있었다 — 5배 오독의 씨앗).
        """
        from challenger.challenger_cost import calc_pnl_pt
        return calc_pnl_pt(trade.direction, trade.entry_price, exit_price)

    def _grade_from_confidence(self, confidence):
        # type: (float) -> str
        if confidence >= 0.70:
            return "A"
        if confidence >= 0.60:
            return "B"
        if confidence >= 0.55:
            return "C"
        return "X"
