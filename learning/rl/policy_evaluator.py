# learning/rl/policy_evaluator.py — 정책 평가기
"""
학습된 PPO 정책을 백테스트 데이터로 평가

평가 지표:
  - 총 수익률, Sharpe Ratio, MDD
  - 정적 규칙 대비 개선도 (Sharpe +0.4 목표)
  - 행동 분포 (각 액션 비율)
  - 에피소드별 성과 분포

Phase 4 완료 기준: 강화학습 정책이 정적 규칙 대비 Sharpe +0.4 이상
"""
import numpy as np
import logging
from typing import List, Dict, Optional

from learning.rl.environment import TradingEnvironment, N_ACTIONS, STATE_DIM, ACTION_NAMES

logger = logging.getLogger("POLICY_EVAL")


class PolicyEvaluator:
    """
    에이전트 정책 평가 — 백테스트 에피소드 목록으로 평가
    """

    def __init__(
        self,
        env:     TradingEnvironment,
        agent,   # PPOAgent (순환 참조 방지 — 타입 힌트 생략)
        n_eval:  int = 20,   # 평가 에피소드 수
    ):
        self.env    = env
        self.agent  = agent
        self.n_eval = n_eval

        self._eval_history: List[dict] = []

    # ── 단일 에피소드 평가 ────────────────────────────────────────
    def run_episode(
        self,
        candles:  List[dict],
        features: List[np.ndarray],
        greedy:   bool = True,
    ) -> dict:
        """
        단일 에피소드 실행 — 결과 딕셔너리 반환

        Args:
            greedy: True → argmax 행동, False → 샘플링
        """
        self.env.load_episode(candles, features)
        state = self.env.reset()

        rewards    = []
        actions    = []
        done       = False

        while not done:
            if greedy:
                action = self.agent.get_greedy_action(state)
            else:
                action, _ = self.agent.select_action(state)

            state, reward, done, info = self.env.step(action)
            rewards.append(reward)
            actions.append(action)

        summary = self.env.get_episode_summary()
        summary["rewards"] = rewards
        summary["actions"] = actions
        return summary

    # ── 다중 에피소드 배치 평가 ───────────────────────────────────
    def evaluate(
        self,
        episode_data: List[Dict],   # [{"candles": [...], "features": [...]}]
        baseline_sharpe: float = 0.0,
    ) -> dict:
        """
        다중 에피소드 평가 — 종합 지표 반환

        Args:
            episode_data:     평가 에피소드 목록
            baseline_sharpe:  정적 규칙 기준 Sharpe (비교용)

        Returns:
            평가 결과 딕셔너리
        """
        rois:      List[float] = []
        mdds:      List[float] = []
        episodes:  List[dict]  = []
        action_counts = np.zeros(N_ACTIONS, dtype=int)

        for ep in episode_data[:self.n_eval]:
            result = self.run_episode(ep["candles"], ep["features"], greedy=True)
            rois.append(result["roi"])
            mdds.append(result["mdd"])
            episodes.append(result)
            for a in result["actions"]:
                action_counts[a] += 1

        if not rois:
            return {"error": "평가 에피소드 없음"}

        rois_arr = np.array(rois)
        mdds_arr = np.array(mdds)

        # Sharpe (일일 수익률 기준, 연율화)
        mean_roi = float(np.mean(rois_arr))
        std_roi  = float(np.std(rois_arr)) + 1e-8
        sharpe   = mean_roi / std_roi * np.sqrt(252)

        # MDD 통계
        avg_mdd  = float(np.mean(mdds_arr))
        max_mdd  = float(np.max(mdds_arr))

        # 행동 분포
        total_actions = action_counts.sum()
        action_dist   = {
            ACTION_NAMES[i]: int(action_counts[i])
            for i in range(N_ACTIONS)
        }
        action_pct = {
            ACTION_NAMES[i]: round(action_counts[i] / max(total_actions, 1), 3)
            for i in range(N_ACTIONS)
        }

        # 기준 대비 개선도
        sharpe_improvement = sharpe - baseline_sharpe
        phase4_pass = sharpe_improvement >= 0.4

        result = {
            "n_episodes":          len(rois),
            "mean_roi":            round(mean_roi, 4),
            "std_roi":             round(std_roi, 4),
            "sharpe":              round(sharpe, 3),
            "baseline_sharpe":     round(baseline_sharpe, 3),
            "sharpe_improvement":  round(sharpe_improvement, 3),
            "phase4_pass":         phase4_pass,   # Phase 4 완료 기준
            "avg_mdd":             round(avg_mdd, 4),
            "max_mdd":             round(max_mdd, 4),
            "win_rate":            round(float(np.mean(rois_arr > 0)), 3),
            "action_counts":       action_dist,
            "action_pct":          action_pct,
        }

        self._eval_history.append(result)
        self._log_result(result)
        return result

    def _log_result(self, result: dict):
        logger.info(
            f"[EVAL] 에피소드={result['n_episodes']} "
            f"Sharpe={result['sharpe']:.3f} "
            f"(기준 {result['baseline_sharpe']:.3f}, 개선 +{result['sharpe_improvement']:.3f}) "
            f"MDD={result['avg_mdd']:.2%} "
            f"Phase4_PASS={result['phase4_pass']}"
        )

    # ── 정적 규칙 기준선 계산 ─────────────────────────────────────
    def compute_baseline(
        self,
        episode_data: List[Dict],
        rule_func=None,
    ) -> float:
        """
        정적 규칙(rule_func) 기반 Sharpe 계산

        Args:
            rule_func: (state) → action (None이면 HOLD 0 반환)

        Returns:
            baseline Sharpe
        """
        if rule_func is None:
            rule_func = lambda s: 0  # HOLD만

        rois = []
        for ep in episode_data[:self.n_eval]:
            self.env.load_episode(ep["candles"], ep["features"])
            state = self.env.reset()
            done  = False
            while not done:
                action       = rule_func(state)
                state, _, done, _ = self.env.step(action)
            summary = self.env.get_episode_summary()
            rois.append(summary["roi"])

        if not rois:
            return 0.0

        arr    = np.array(rois)
        sharpe = float(np.mean(arr)) / (float(np.std(arr)) + 1e-8) * np.sqrt(252)
        logger.info(f"[EVAL] 기준선 Sharpe = {sharpe:.3f}")
        return round(sharpe, 3)

    def get_history(self) -> List[dict]:
        return self._eval_history


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from learning.rl.ppo_agent import PPOAgent

    env   = TradingEnvironment(max_steps=30)
    agent = PPOAgent(batch_size=64)

    # 더미 에피소드 데이터
    def make_ep():
        n = 30
        return {
            "candles":  [{"close": 380.0 + np.random.randn() * 0.3} for _ in range(n)],
            "features": [np.random.randn(STATE_DIM - 4).astype(np.float32) for _ in range(n)],
        }

    episodes = [make_ep() for _ in range(5)]

    evaluator = PolicyEvaluator(env, agent, n_eval=5)
    baseline  = evaluator.compute_baseline(episodes)
    result    = evaluator.evaluate(episodes, baseline_sharpe=baseline)
    print(result)
