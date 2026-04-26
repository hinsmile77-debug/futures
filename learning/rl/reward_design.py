# learning/rl/reward_design.py — 보상 함수 설계
"""
트레이딩 RL 보상 함수

설계 원칙:
  Reward = PnL(원화) - 거래비용 - 리스크 페널티 - MDD 페널티 + 불필요 거래 페널티

PnL 스케일: 원화 → 표준화 (initial_balance 기준)

리스크 페널티:
  - 포지션이 클수록 패널티 (분산 제어)
  - 미실현 손실이 클수록 패널티

MDD 패널티:
  - peak 대비 현재 잔고 낙폭이 클수록 강한 패널티 (비선형)

행동 패널티:
  - 동일 방향 과도 매매 시 소량 패널티
"""
import numpy as np
from typing import Optional


class RewardDesign:
    """정적 메서드 모음 — 인스턴스 불필요"""

    # 보상 스케일 (원화 1만원 = 1.0)
    REWARD_SCALE = 10_000.0

    # 무의미한 반복 매매 패널티
    CHURN_PENALTY = 0.02

    @staticmethod
    def compute(
        pnl:             float,    # 실현 손익 (원화)
        commission:      float,    # 수수료 (원화)
        position:        int,      # 현재 포지션 계약 수
        unrealized_pnl:  float,    # 미실현 손익 (원화)
        balance:         float,    # 현재 잔고 (원화)
        peak_balance:    float,    # 최고 잔고 (원화)
        action:          int,      # 실행한 행동
        risk_penalty_wt: float = 0.1,
        drawdown_penalty: float = 0.5,
    ) -> float:
        """
        보상 계산

        Returns:
            reward (float): 표준화된 보상 값
        """
        scale = RewardDesign.REWARD_SCALE

        # 1. 기본 PnL 보상 (수수료 차감)
        net_pnl = (pnl - commission) / scale

        # 2. 미실현 손실 페널티 (보유 중 손실에 부분 패널티)
        if unrealized_pnl < 0:
            unrealized_penalty = risk_penalty_wt * abs(unrealized_pnl) / scale
        else:
            # 미실현 이익은 소량만 반영 (과도한 보유 억제)
            unrealized_penalty = -0.02 * unrealized_pnl / scale

        # 3. 포지션 크기 페널티 (큰 포지션 = 리스크 높음)
        position_penalty = risk_penalty_wt * 0.01 * abs(position)

        # 4. MDD 페널티 (비선형 — MDD가 커질수록 급격히 증가)
        if peak_balance > 0:
            mdd_ratio = (peak_balance - balance) / peak_balance
            # 5% 이상 낙폭부터 페널티 시작, 비선형 증가
            if mdd_ratio > 0.05:
                mdd_pen = drawdown_penalty * (mdd_ratio ** 2) * 10.0
            else:
                mdd_pen = 0.0
        else:
            mdd_pen = 0.0

        # 5. 불필요 HOLD 패널티 (포지션 없이 HOLD → 기회비용)
        # ACTION_HOLD = 0
        if action == 0 and position == 0:
            hold_penalty = 0.001   # 아주 작게 — 과도하게 적용하면 과매매 유도
        else:
            hold_penalty = 0.0

        reward = net_pnl - unrealized_penalty - position_penalty - mdd_pen - hold_penalty
        return float(np.clip(reward, -10.0, 10.0))

    @staticmethod
    def compute_shaped(
        pnl:         float,
        commission:  float,
        position:    int,
        next_close:  float,
        prev_close:  float,
        max_long:    int = 5,
    ) -> float:
        """
        Reward Shaping — 방향 예측 보너스 포함

        포지션 방향이 다음 분 가격 방향과 일치하면 보너스
        (희소 보상 문제 완화)
        """
        scale    = RewardDesign.REWARD_SCALE
        net_pnl  = (pnl - commission) / scale

        # 방향 보너스
        price_chg = next_close - prev_close
        if position > 0 and price_chg > 0:
            direction_bonus = 0.1 * (position / max_long)
        elif position < 0 and price_chg < 0:
            direction_bonus = 0.1 * (abs(position) / max_long)
        else:
            direction_bonus = -0.05  # 반대 방향

        return float(np.clip(net_pnl + direction_bonus, -10.0, 10.0))


if __name__ == "__main__":
    # 수익 실현 케이스
    r = RewardDesign.compute(
        pnl=100_000, commission=5_000,
        position=2, unrealized_pnl=0,
        balance=50_100_000, peak_balance=50_100_000,
        action=5,  # EXIT
    )
    print(f"[수익 청산] reward = {r:.4f}")

    # MDD 큰 케이스
    r2 = RewardDesign.compute(
        pnl=-50_000, commission=5_000,
        position=0, unrealized_pnl=0,
        balance=47_000_000, peak_balance=50_000_000,  # MDD 6%
        action=5,
    )
    print(f"[MDD 6%]   reward = {r2:.4f}")
