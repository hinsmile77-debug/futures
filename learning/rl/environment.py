# learning/rl/environment.py — 트레이딩 강화학습 환경
"""
KOSPI 200 선물 1분봉 트레이딩을 위한 RL 환경

State  : 시장 피처 + 포지션 상태 + 미실현 손익
Action : HOLD(0) / BUY_FULL(1) / BUY_HALF(2) / SELL_FULL(3) / SELL_HALF(4) / EXIT(5)
Reward : 다음 1분 PnL - 거래 비용 - 리스크 페널티

Python 3.7 32-bit 호환 (numpy only, no torch required)
"""
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("RL_ENV")

# ── 행동 정의 ──────────────────────────────────────────────────────
ACTION_HOLD      = 0
ACTION_BUY_FULL  = 1
ACTION_BUY_HALF  = 2
ACTION_SELL_FULL = 3
ACTION_SELL_HALF = 4
ACTION_EXIT      = 5
N_ACTIONS        = 6

ACTION_NAMES = {
    ACTION_HOLD:      "HOLD",
    ACTION_BUY_FULL:  "BUY_FULL",
    ACTION_BUY_HALF:  "BUY_HALF",
    ACTION_SELL_FULL: "SELL_FULL",
    ACTION_SELL_HALF: "SELL_HALF",
    ACTION_EXIT:      "EXIT",
}

# 상태 벡터 크기 (피처 수 — reward_design.py와 동기화)
STATE_DIM = 18


class TradingEnvironment:
    """
    KOSPI 200 선물 트레이딩 환경

    백테스트 모드: 과거 데이터로 에피소드 반복
    실시간 모드:  매 분봉 마다 step() 호출

    포지션 단위: 계약 수 (1계약 = 250,000 × index_pt)
    """

    # 계약 1개 기준 변동 단위
    TICK_SIZE    = 0.05   # KOSPI 200 선물 최소 호가
    PT_VALUE     = 250_000  # 1pt = 250,000원

    # 최대 계약
    MAX_LONG  =  5
    MAX_SHORT = -5

    def __init__(
        self,
        max_steps:        int   = 390,   # 하루 최대 분봉 (09:00 ~ 15:30)
        initial_balance:  float = 50_000_000.0,  # 초기 자본
        commission_rate:  float = 0.0000336,     # KRX+증권사 왕복 수수료
        risk_penalty_wt:  float = 0.1,           # 리스크 페널티 가중치
        drawdown_penalty: float = 0.5,           # MDD 패널티 가중치
    ):
        self.max_steps       = max_steps
        self.initial_balance = initial_balance
        self.commission_rate = commission_rate
        self.risk_penalty_wt = risk_penalty_wt
        self.drawdown_penalty = drawdown_penalty

        # 에피소드 데이터 (백테스트 시 외부에서 주입)
        self._candles: List[dict] = []      # 1분봉 OHLCV + 피처 딕셔너리 목록
        self._features: List[np.ndarray] = []  # 전처리된 상태 벡터

        self.reset()

    # ── 에피소드 데이터 설정 ──────────────────────────────────────
    def load_episode(self, candles: List[dict], features: List[np.ndarray]):
        """
        백테스트용 에피소드 데이터 주입

        Args:
            candles:  1분봉 dict 목록 (keys: open/high/low/close/volume/time)
            features: 각 분봉의 상태 벡터 (shape: [N, STATE_DIM])
        """
        self._candles  = candles
        self._features = features
        self.reset()

    # ── 환경 초기화 ───────────────────────────────────────────────
    def reset(self) -> np.ndarray:
        """에피소드 시작 — 초기 상태 반환"""
        self.step_idx         = 0
        self.position         = 0       # 현재 포지션 (계약 수, 음수=숏)
        self.avg_entry_price  = 0.0
        self.balance          = self.initial_balance
        self.peak_balance     = self.initial_balance
        self.unrealized_pnl   = 0.0
        self.realized_pnl     = 0.0
        self.total_commission = 0.0
        self.trade_count      = 0
        self.done             = False
        self._history: List[dict] = []
        return self._get_state()

    # ── 행동 실행 ─────────────────────────────────────────────────
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, dict]:
        """
        한 스텝 진행

        Returns:
            (next_state, reward, done, info)
        """
        if self.done:
            raise RuntimeError("에피소드가 종료된 상태에서 step() 호출")

        candle = self._get_current_candle()
        price  = candle.get("close", 0.0)

        # 행동 실행 및 PnL 계산
        pnl, commission = self._execute_action(action, price)

        # 다음 분봉으로 이동
        self.step_idx += 1
        done = (self.step_idx >= len(self._candles)) or (self.step_idx >= self.max_steps)

        # 마지막 스텝에서 강제 청산
        if done and self.position != 0:
            next_price = self._get_current_candle().get("close", price) if not (self.step_idx >= len(self._candles)) else price
            close_pnl, close_comm = self._close_position(next_price, reason="에피소드종료")
            pnl        += close_pnl
            commission += close_comm

        self.realized_pnl     += pnl
        self.total_commission += commission
        self.balance           = self.initial_balance + self.realized_pnl - self.total_commission

        # 최고 잔고 갱신 (MDD 계산용)
        if self.balance > self.peak_balance:
            self.peak_balance = self.balance

        # 미실현 손익 업데이트
        next_candle   = self._get_current_candle()
        next_price_f  = next_candle.get("close", price)
        self._update_unrealized(next_price_f)

        # 보상 계산 (reward_design.py 참조)
        from learning.rl.reward_design import RewardDesign
        reward = RewardDesign.compute(
            pnl=pnl,
            commission=commission,
            position=self.position,
            unrealized_pnl=self.unrealized_pnl,
            balance=self.balance,
            peak_balance=self.peak_balance,
            action=action,
            risk_penalty_wt=self.risk_penalty_wt,
            drawdown_penalty=self.drawdown_penalty,
        )

        next_state = self._get_state()
        self.done  = done

        info = {
            "pnl":           round(pnl, 0),
            "commission":    round(commission, 0),
            "position":      self.position,
            "balance":       round(self.balance, 0),
            "unrealized":    round(self.unrealized_pnl, 0),
            "action_name":   ACTION_NAMES.get(action, "?"),
        }
        self._history.append({**info, "reward": round(reward, 4), "step": self.step_idx})

        return next_state, reward, done, info

    # ── 행동 실행 내부 ────────────────────────────────────────────
    def _execute_action(self, action: int, price: float) -> Tuple[float, float]:
        """행동에 따른 매매 실행 — (pnl, commission) 반환"""
        pnl        = 0.0
        commission = 0.0

        if action == ACTION_HOLD:
            pass  # 아무 것도 안 함

        elif action == ACTION_BUY_FULL:
            if self.position < 0:
                # 숏 전량 청산 후 롱 진입
                p, c = self._close_position(price, reason="숏→롱")
                pnl += p; commission += c
            target = self.MAX_LONG
            delta  = target - self.position
            if delta > 0:
                c = self._open_position(delta, price, "LONG")
                commission += c

        elif action == ACTION_BUY_HALF:
            if self.position >= 0:
                target = min(self.position + max(1, self.MAX_LONG // 2), self.MAX_LONG)
                delta  = target - self.position
                if delta > 0:
                    c = self._open_position(delta, price, "LONG")
                    commission += c

        elif action == ACTION_SELL_FULL:
            if self.position > 0:
                p, c = self._close_position(price, reason="롱→숏")
                pnl += p; commission += c
            target = self.MAX_SHORT
            delta  = target - self.position
            if delta < 0:
                c = self._open_position(abs(delta), price, "SHORT")
                commission += c

        elif action == ACTION_SELL_HALF:
            if self.position <= 0:
                target = max(self.position - max(1, abs(self.MAX_SHORT) // 2), self.MAX_SHORT)
                delta  = target - self.position
                if delta < 0:
                    c = self._open_position(abs(delta), price, "SHORT")
                    commission += c

        elif action == ACTION_EXIT:
            if self.position != 0:
                p, c = self._close_position(price, reason="EXIT")
                pnl += p; commission += c

        return pnl, commission

    def _open_position(self, contracts: int, price: float, direction: str) -> float:
        """포지션 진입 — 수수료 반환"""
        if direction == "LONG":
            self.position        += contracts
        else:
            self.position        -= contracts

        self.avg_entry_price  = price
        self.trade_count      += 1
        commission = contracts * price * self.PT_VALUE * self.commission_rate
        logger.debug(f"[ENV] {direction} {contracts}계약 @ {price:.2f}, comm={commission:,.0f}")
        return commission

    def _close_position(self, price: float, reason: str = "") -> Tuple[float, float]:
        """전량 청산 — (pnl, commission) 반환"""
        if self.position == 0:
            return 0.0, 0.0

        contracts  = abs(self.position)
        direction  = 1 if self.position > 0 else -1
        pnl        = direction * (price - self.avg_entry_price) * contracts * self.PT_VALUE
        commission = contracts * price * self.PT_VALUE * self.commission_rate

        logger.debug(f"[ENV] 청산({reason}) {contracts}계약 @ {price:.2f}, PnL={pnl:,.0f}")

        self.position        = 0
        self.avg_entry_price = 0.0
        return pnl, commission

    def _update_unrealized(self, current_price: float):
        if self.position == 0 or self.avg_entry_price == 0.0:
            self.unrealized_pnl = 0.0
            return
        direction = 1 if self.position > 0 else -1
        self.unrealized_pnl = direction * (current_price - self.avg_entry_price) * abs(self.position) * self.PT_VALUE

    # ── 상태 벡터 구성 ────────────────────────────────────────────
    def _get_state(self) -> np.ndarray:
        """
        현재 상태 벡터 반환 (shape: [STATE_DIM])

        외부 피처(market features) + 내부 상태(position/pnl) 결합
        """
        # 외부 피처
        if self._features and self.step_idx < len(self._features):
            market_feat = self._features[self.step_idx].copy()
            # STATE_DIM - 4 차원 보장
            n_market = STATE_DIM - 4
            if len(market_feat) >= n_market:
                market_feat = market_feat[:n_market]
            else:
                market_feat = np.pad(market_feat, (0, n_market - len(market_feat)))
        else:
            market_feat = np.zeros(STATE_DIM - 4)

        # 내부 상태 (정규화)
        pos_norm    = self.position / max(self.MAX_LONG, 1)
        pnl_norm    = self.unrealized_pnl / max(self.initial_balance * 0.01, 1.0)
        bal_norm    = (self.balance - self.initial_balance) / max(self.initial_balance * 0.05, 1.0)
        mdd_norm    = (self.peak_balance - self.balance) / max(self.peak_balance * 0.05, 1.0)

        internal = np.array([pos_norm, pnl_norm, bal_norm, mdd_norm], dtype=np.float32)
        state    = np.concatenate([market_feat.astype(np.float32), internal])
        return np.clip(state, -5.0, 5.0)

    def _get_current_candle(self) -> dict:
        if self._candles and self.step_idx < len(self._candles):
            return self._candles[self.step_idx]
        return {"open": 0.0, "high": 0.0, "low": 0.0, "close": 0.0, "volume": 0}

    # ── 에피소드 요약 ─────────────────────────────────────────────
    def get_episode_summary(self) -> dict:
        mdd = (self.peak_balance - self.balance) / max(self.peak_balance, 1.0)
        return {
            "total_steps":     self.step_idx,
            "trade_count":     self.trade_count,
            "realized_pnl":    round(self.realized_pnl, 0),
            "total_commission":round(self.total_commission, 0),
            "final_balance":   round(self.balance, 0),
            "mdd":             round(mdd, 4),
            "roi":             round((self.balance - self.initial_balance) / self.initial_balance, 4),
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    env = TradingEnvironment(max_steps=10)

    # 더미 에피소드
    candles  = [{"close": 380.0 + i * 0.1} for i in range(10)]
    features = [np.random.randn(STATE_DIM - 4).astype(np.float32) for _ in range(10)]
    env.load_episode(candles, features)

    state = env.reset()
    print(f"초기 상태 shape: {state.shape}")
    for t in range(10):
        action = np.random.randint(0, N_ACTIONS)
        s, r, done, info = env.step(action)
        print(f"  step={t+1} action={info['action_name']:<10} reward={r:.4f} pos={info['position']} bal={info['balance']:,.0f}")
        if done:
            break
    print(env.get_episode_summary())
