# strategy/entry/adaptive_kelly.py
# 적응형 켈리 공식 — 시스템 실전 성적 반영 동적 자금 관리
"""
기존 정적 켈리: 신뢰도 기반 고정 배수 (시스템 성적 무관)
적응형 켈리:   최근 20회 실전 승률·손익비로 사이즈 자동 조정

핵심 효과:
  슬럼프 진입 시 자동 사이즈 축소 → 계좌 보호
  승률 회복 시 자동 사이즈 복원 → 수익 극대화
"""
import numpy as np
from collections import deque
import logging

logger = logging.getLogger(__name__)


class AdaptiveKelly:
    """
    적응형 켈리 공식 (최근 N회 실전 성적 반영)

    f* = (p * (b + 1) - 1) / b
      p: 최근 N회 승률
      b: 최근 N회 손익비 (평균 수익 / 평균 손실)

    안전장치:
      - 하프 켈리 (f* / 2)
      - 최대 배율: 1.5 캡핑
      - 최소 배율: 0.1 (완전 중단 방지)
    """

    LOOKBACK    = 20    # 최근 20회
    HALF_KELLY  = 0.5   # 하프 켈리 계수
    MAX_MULT    = 1.5   # 최대 배율 캡
    MIN_MULT    = 0.10  # 최소 배율 (완전 정지 방지)

    def __init__(self):
        self.trade_results = deque(maxlen=self.LOOKBACK)
        # 각 원소: {"win": bool, "profit": float, "loss": float}

    def record(self, win: bool, pnl_pts: float):
        """매매 결과 기록"""
        self.trade_results.append({
            "win":    win,
            "profit": max(pnl_pts, 0),
            "loss":   abs(min(pnl_pts, 0)),
        })
        logger.info(f"[AdaptiveKelly] 기록 ({len(self.trade_results)}/{self.LOOKBACK}) "
                    f"{'WIN' if win else 'LOSS'} {pnl_pts:+.2f}pt")

    def compute_fraction(self) -> dict:
        """
        켈리 비율 계산

        Returns:
            kelly_f:   순수 켈리 비율
            adjusted:  하프 켈리 + 캡핑 적용값
            multiplier: 기본 사이즈 대비 배수
            reason:    결정 이유
        """
        n = len(self.trade_results)
        if n < 5:
            return {
                "kelly_f":    0.5,
                "adjusted":   0.5,
                "multiplier": 0.6,
                "reason":     f"데이터 부족 ({n}/20) — 보수적 적용",
            }

        wins   = [t for t in self.trade_results if t["win"]]
        losses = [t for t in self.trade_results if not t["win"]]

        p = len(wins) / n   # 승률
        avg_profit = (np.mean([w["profit"] for w in wins])
                      if wins else 0.001)
        avg_loss   = (np.mean([l["loss"]  for l in losses])
                      if losses else 0.001)
        b = avg_profit / avg_loss   # 손익비

        # 켈리 공식: f* = (p*(b+1) - 1) / b
        kelly_f = (p * (b + 1) - 1) / b

        # 하프 켈리 적용
        adjusted = kelly_f * self.HALF_KELLY

        # 배율 캡핑
        multiplier = float(np.clip(adjusted / 0.5, self.MIN_MULT, self.MAX_MULT))
        # 기준: 정적 켈리 0.5 → 배수 = adjusted / 0.5

        reason = (
            f"최근{n}회: 승률{p:.0%} 손익비{b:.2f} "
            f"→ Kelly={kelly_f:.2f} 배수={multiplier:.2f}"
        )

        if kelly_f <= 0:
            reason = f"켈리 음수 (승률{p:.0%}) — 최소 배율 적용"
            multiplier = self.MIN_MULT

        logger.info(f"[AdaptiveKelly] {reason}")
        return {
            "kelly_f":    round(kelly_f, 3),
            "adjusted":   round(adjusted, 3),
            "multiplier": round(multiplier, 3),
            "win_rate":   round(p, 3),
            "profit_ratio": round(b, 3),
            "reason":     reason,
        }

    def apply_to_size(self, base_qty: int) -> int:
        """기본 수량에 적응형 켈리 배율 적용"""
        result = self.compute_fraction()
        adjusted = max(1, round(base_qty * result["multiplier"]))
        logger.info(f"[AdaptiveKelly] 수량 조정: {base_qty} → {adjusted}계약")
        return adjusted
