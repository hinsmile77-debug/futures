# strategy/entry/staged_entry.py — 분할 진입 관리 ⭐v6.5
"""
등급별 분할 진입 전략

등급별 진입 방식:
  A급 (체크리스트 6개↑): 100% 즉시 진입
  B급 (4~5개):            50% → 1분 후 가격 확인 → 추가 50%
  C급 (2~3개):            50% → 손절 도달 시 추가 진입 안 함
  X급 (0~1개):            진입 금지

Stage 상태 머신:
  IDLE → STAGE1 (1차 진입) → STAGE2 (2차 진입) → FULL (완료)
  IDLE → FULL (A급 즉시 100%)
  IDLE → STAGE1 → CANCELLED (C급 손절/조건 미충족)
"""
import datetime
import logging
from typing import Optional, Dict

from config.constants import DIRECTION_UP, DIRECTION_DOWN, POSITION_LONG, POSITION_SHORT

logger = logging.getLogger("TRADE")

# ── 진입 상태 ────────────────────────────────────────────────────
STATE_IDLE       = "IDLE"
STATE_STAGE1     = "STAGE1"      # 1차 진입 완료 대기
STATE_STAGE2     = "STAGE2"      # 2차 진입 완료 대기
STATE_FULL       = "FULL"        # 전량 진입 완료
STATE_CANCELLED  = "CANCELLED"   # 2차 취소

# B급 2차 진입 대기 시간 (분)
B_GRADE_WAIT_MIN = 1


class StagedEntryManager:
    """
    분할 진입 상태 관리

    외부에서 매 분봉마다 update()를 호출하면
    현재 상태에 따라 진입 지시를 반환합니다.

    사용:
        sem = StagedEntryManager()
        instr = sem.request_entry(grade="B", direction=1, price=380.0,
                                  base_qty=3, atr=0.5)
        # instr: {action: "ENTER_STAGE1", qty: 1, ...}

        # 다음 분봉
        instr = sem.update(current_price=380.2, current_time=now)
        # instr: {action: "ENTER_STAGE2", qty: 1, ...} or None
    """

    def __init__(self):
        self.state         = STATE_IDLE
        self.grade         = ""
        self.direction     = 0
        self.base_qty      = 0
        self.stage1_qty    = 0
        self.stage2_qty    = 0
        self.stage1_price  = 0.0
        self.stage1_time:  Optional[datetime.datetime] = None
        self.stop_price    = 0.0
        self._atr          = 0.0

        self._history: list = []

    # ── 진입 요청 ─────────────────────────────────────────────────
    def request_entry(
        self,
        grade:      str,
        direction:  int,    # DIRECTION_UP=+1 / DIRECTION_DOWN=-1
        price:      float,
        base_qty:   int,    # 최종 목표 계약 수
        atr:        float,
        stop_price: float = 0.0,
    ) -> Optional[Dict]:
        """
        진입 요청 처리

        Returns:
            진입 지시 딕셔너리 또는 None (X급)
            {action, qty, direction_str, grade, note}
        """
        if self.state not in (STATE_IDLE, STATE_CANCELLED, STATE_FULL):
            logger.warning(f"[StagedEntry] 이미 진입 진행 중 (state={self.state}) — 무시")
            return None

        if grade == "X":
            logger.info("[StagedEntry] X급 — 진입 금지")
            return None

        self.grade      = grade
        self.direction  = direction
        self.base_qty   = max(base_qty, 1)
        self._atr       = atr
        self.stop_price = stop_price if stop_price else self._calc_stop(price, atr, direction)
        dir_str         = POSITION_LONG if direction > 0 else POSITION_SHORT

        if grade == "A":
            # 100% 즉시 진입
            self.stage1_qty   = self.base_qty
            self.stage2_qty   = 0
            self.stage1_price = price
            self.stage1_time  = datetime.datetime.now()
            self.state        = STATE_FULL
            instr = {
                "action":        "ENTER_FULL",
                "qty":           self.stage1_qty,
                "direction_str": dir_str,
                "grade":         "A",
                "note":          "A급 100% 즉시",
            }

        elif grade == "B":
            # 50% 진입 → 1분 후 추가
            self.stage1_qty   = max(1, self.base_qty // 2)
            self.stage2_qty   = self.base_qty - self.stage1_qty
            self.stage1_price = price
            self.stage1_time  = datetime.datetime.now()
            self.state        = STATE_STAGE1
            instr = {
                "action":        "ENTER_STAGE1",
                "qty":           self.stage1_qty,
                "direction_str": dir_str,
                "grade":         "B",
                "note":          f"B급 1차 {self.stage1_qty}계약 (1분 후 {self.stage2_qty}계약 추가 대기)",
            }

        else:  # C급
            # 50% 진입 → 손절 도달 시 추가 안 함
            self.stage1_qty   = max(1, self.base_qty // 2)
            self.stage2_qty   = 0   # C급은 2차 없음
            self.stage1_price = price
            self.stage1_time  = datetime.datetime.now()
            self.state        = STATE_STAGE1
            instr = {
                "action":        "ENTER_STAGE1",
                "qty":           self.stage1_qty,
                "direction_str": dir_str,
                "grade":         "C",
                "note":          f"C급 50% {self.stage1_qty}계약 (2차 없음)",
            }

        logger.info(f"[StagedEntry] {instr['note']}")
        self._history.append({**instr, "price": price, "time": datetime.datetime.now()})
        return instr

    # ── 분봉 업데이트 ─────────────────────────────────────────────
    def update(
        self,
        current_price: float,
        current_time:  Optional[datetime.datetime] = None,
    ) -> Optional[Dict]:
        """
        매 분봉마다 호출 — 상태에 따라 추가 진입/취소 지시 반환

        Returns:
            진입 지시 딕셔너리 or None (아직 대기 중 or 완료)
        """
        if current_time is None:
            current_time = datetime.datetime.now()

        if self.state != STATE_STAGE1:
            return None

        dir_str = POSITION_LONG if self.direction > 0 else POSITION_SHORT

        if self.grade == "B":
            elapsed_min = (current_time - self.stage1_time).total_seconds() / 60.0
            if elapsed_min < B_GRADE_WAIT_MIN:
                return None  # 아직 1분 미경과

            # 1분 경과 — 가격 확인 후 추가 진입
            price_ok = self._check_continuation(current_price)
            if price_ok and self.stage2_qty > 0:
                self.state = STATE_FULL
                instr = {
                    "action":        "ENTER_STAGE2",
                    "qty":           self.stage2_qty,
                    "direction_str": dir_str,
                    "grade":         "B",
                    "note":          f"B급 2차 추가 {self.stage2_qty}계약 (가격 확인 OK)",
                }
                logger.info(f"[StagedEntry] {instr['note']}")
                self._history.append({**instr, "price": current_price, "time": current_time})
                return instr
            else:
                self.state = STATE_CANCELLED
                reason = "가격 역행" if not price_ok else "수량 없음"
                logger.info(f"[StagedEntry] B급 2차 취소 ({reason})")
                return None

        # C급은 update에서 아무것도 하지 않음 (1차만으로 종결)
        if self.grade == "C":
            self.state = STATE_FULL   # 상태 완료 처리 (1차가 전부)
            return None

        return None

    def _check_continuation(self, current_price: float) -> bool:
        """
        B급 2차 진입 전 가격 확인

        진입 방향으로 가격이 유지/개선되었는지 확인
        (손절 가격 이하면 취소)
        """
        if self.stop_price and self.direction > 0 and current_price <= self.stop_price:
            return False
        if self.stop_price and self.direction < 0 and current_price >= self.stop_price:
            return False
        # 방향 확인: 1차 진입가에서 반대 방향으로 0.5ATR 이상 이동 시 취소
        move = (current_price - self.stage1_price) * self.direction
        if move < -self._atr * 0.5:
            return False
        return True

    def _calc_stop(self, price: float, atr: float, direction: int) -> float:
        from config.settings import ATR_STOP_MULT
        return price - direction * atr * ATR_STOP_MULT

    # ── 초기화 ───────────────────────────────────────────────────
    def reset(self):
        self.state        = STATE_IDLE
        self.grade        = ""
        self.direction    = 0
        self.base_qty     = 0
        self.stage1_qty   = 0
        self.stage2_qty   = 0
        self.stage1_price = 0.0
        self.stage1_time  = None
        self.stop_price   = 0.0
        self._atr         = 0.0

    @property
    def is_idle(self) -> bool:
        return self.state in (STATE_IDLE, STATE_FULL, STATE_CANCELLED)

    @property
    def pending_stage2(self) -> bool:
        return self.state == STATE_STAGE1 and self.grade == "B"

    def get_history(self) -> list:
        return self._history


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sem = StagedEntryManager()

    print("=== A급 테스트 ===")
    i = sem.request_entry("A", DIRECTION_UP, 380.0, 4, atr=0.5)
    print(f"결과: {i}")

    sem.reset()
    print("\n=== B급 테스트 ===")
    i = sem.request_entry("B", DIRECTION_UP, 380.0, 4, atr=0.5)
    print(f"1차: {i}")
    # 1분 경과 시뮬레이션
    sem.stage1_time = datetime.datetime.now() - datetime.timedelta(minutes=2)
    i2 = sem.update(380.2)
    print(f"2차: {i2}")

    sem.reset()
    print("\n=== C급 테스트 ===")
    i = sem.request_entry("C", DIRECTION_DOWN, 380.0, 4, atr=0.5)
    print(f"1차: {i}")
    i2 = sem.update(379.8)
    print(f"업데이트: {i2}")
