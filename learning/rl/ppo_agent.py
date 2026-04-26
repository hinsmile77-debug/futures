# learning/rl/ppo_agent.py — PPO 에이전트
"""
Proximal Policy Optimization (PPO) 에이전트

Python 3.7 32-bit 호환:
  - 기본: numpy 기반 선형 정책 (즉시 동작)
  - 선택: PyTorch MLP 정책 (torch 설치 시 자동 활성화)

상태  → 정책 네트워크 → 행동 확률분포 → 샘플링
     → 가치 네트워크 → 상태 가치 추정

PPO Clip Objective:
  L = E[ min(r_t * A_t, clip(r_t, 1-ε, 1+ε) * A_t) ]
  r_t = π_θ(a|s) / π_θ_old(a|s)
"""
import numpy as np
import logging
from typing import List, Tuple, Optional

from learning.rl.environment import (
    TradingEnvironment, N_ACTIONS, STATE_DIM
)

logger = logging.getLogger("PPO")

# ── PyTorch 선택적 import ─────────────────────────────────────────
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    _TORCH_OK = True
except ImportError:
    _TORCH_OK = False

# ── numpy 기반 선형 정책 (torch 없을 때 fallback) ─────────────────

class _LinearPolicy:
    """
    단순 선형 정책 (softmax 출력)
    torch 없이 numpy만으로 동작하는 baseline
    """

    def __init__(self, state_dim: int, n_actions: int, lr: float = 1e-3):
        self.W = np.random.randn(state_dim, n_actions).astype(np.float64) * 0.01
        self.b = np.zeros(n_actions, dtype=np.float64)
        self.lr = lr
        # 가치 함수 파라미터
        self.Wv = np.random.randn(state_dim, 1).astype(np.float64) * 0.01
        self.bv = np.zeros(1, dtype=np.float64)

    def _softmax(self, x: np.ndarray) -> np.ndarray:
        x = x - x.max()
        e = np.exp(x)
        return e / e.sum()

    def get_action_probs(self, state: np.ndarray) -> np.ndarray:
        logits = state @ self.W + self.b
        return self._softmax(logits)

    def get_value(self, state: np.ndarray) -> float:
        return float(state @ self.Wv + self.bv)

    def update(self, states, actions, advantages, returns, old_log_probs,
               clip_eps: float, entropy_coef: float):
        """REINFORCE with baseline (numpy PPO 근사)"""
        total_loss = 0.0
        for s, a, adv, ret, old_lp in zip(states, actions, advantages, returns, old_log_probs):
            probs   = self.get_action_probs(s)
            log_p   = np.log(probs[a] + 1e-8)
            ratio   = np.exp(log_p - old_lp)
            clipped = np.clip(ratio, 1 - clip_eps, 1 + clip_eps)
            policy_loss = -min(ratio * adv, clipped * adv)

            # 정책 그라디언트 (단순화)
            grad_logit     = probs.copy()
            grad_logit[a] -= 1.0
            self.W -= self.lr * np.outer(s, grad_logit * policy_loss)
            self.b -= self.lr * grad_logit * policy_loss

            # 가치 업데이트
            val   = self.get_value(s)
            v_err = val - ret
            self.Wv -= self.lr * s.reshape(-1, 1) * v_err
            self.bv -= self.lr * v_err

            total_loss += policy_loss
        return total_loss / max(len(states), 1)


# ── PyTorch MLP 정책 ──────────────────────────────────────────────
if _TORCH_OK:
    class _MlpActorCritic(nn.Module):
        def __init__(self, state_dim: int, n_actions: int, hidden: int = 128):
            super().__init__()
            self.shared = nn.Sequential(
                nn.Linear(state_dim, hidden),
                nn.Tanh(),
                nn.Linear(hidden, hidden),
                nn.Tanh(),
            )
            self.actor  = nn.Linear(hidden, n_actions)
            self.critic = nn.Linear(hidden, 1)

        def forward(self, x):
            h = self.shared(x)
            return self.actor(h), self.critic(h)

        def get_action_probs(self, state_np: np.ndarray):
            with torch.no_grad():
                x       = torch.FloatTensor(state_np).unsqueeze(0)
                logits, val = self(x)
                probs   = torch.softmax(logits, dim=-1).squeeze(0).numpy()
                value   = val.item()
            return probs, value


# ── PPO 에이전트 본체 ─────────────────────────────────────────────

class PPOAgent:
    """
    KOSPI 200 선물 트레이딩 PPO 에이전트

    사용:
        agent = PPOAgent()
        state = env.reset()
        action = agent.select_action(state)
        next_state, reward, done, info = env.step(action)
        agent.record(state, action, reward, done, log_prob)
        if len(agent.buffer) >= agent.batch_size:
            agent.update()
    """

    def __init__(
        self,
        state_dim:    int   = STATE_DIM,
        n_actions:    int   = N_ACTIONS,
        lr:           float = 3e-4,
        gamma:        float = 0.99,    # 할인율
        lam:          float = 0.95,    # GAE lambda
        clip_eps:     float = 0.2,     # PPO clip epsilon
        entropy_coef: float = 0.01,    # 엔트로피 보너스
        n_epochs:     int   = 4,       # 업데이트 epoch 수
        batch_size:   int   = 256,     # 롤아웃 배치 크기
    ):
        self.state_dim    = state_dim
        self.n_actions    = n_actions
        self.gamma        = gamma
        self.lam          = lam
        self.clip_eps     = clip_eps
        self.entropy_coef = entropy_coef
        self.n_epochs     = n_epochs
        self.batch_size   = batch_size

        # 정책 초기화
        if _TORCH_OK:
            self._net       = _MlpActorCritic(state_dim, n_actions)
            self._optimizer = optim.Adam(self._net.parameters(), lr=lr)
            self._backend   = "torch"
            logger.info("[PPO] PyTorch MLP 정책 사용")
        else:
            self._linear    = _LinearPolicy(state_dim, n_actions, lr=lr)
            self._backend   = "numpy"
            logger.info("[PPO] numpy 선형 정책 사용 (torch 미설치)")

        # 롤아웃 버퍼
        self.buffer: List[dict] = []

        # 학습 통계
        self.update_count = 0
        self.total_reward = 0.0
        self.episode_count = 0

    # ── 행동 선택 ────────────────────────────────────────────────
    def select_action(self, state: np.ndarray) -> Tuple[int, float]:
        """
        현재 상태에서 행동 샘플링

        Returns:
            (action, log_prob)
        """
        if self._backend == "torch":
            probs, _val = self._net.get_action_probs(state)
        else:
            probs = self._linear.get_action_probs(state)

        action   = int(np.random.choice(self.n_actions, p=probs))
        log_prob = float(np.log(probs[action] + 1e-8))
        return action, log_prob

    def get_greedy_action(self, state: np.ndarray) -> int:
        """탐욕 행동 (평가용, 샘플링 없음)"""
        if self._backend == "torch":
            probs, _ = self._net.get_action_probs(state)
        else:
            probs = self._linear.get_action_probs(state)
        return int(np.argmax(probs))

    # ── 경험 저장 ────────────────────────────────────────────────
    def record(
        self,
        state:    np.ndarray,
        action:   int,
        reward:   float,
        done:     bool,
        log_prob: float,
    ):
        """롤아웃 버퍼에 경험 추가"""
        self.total_reward += reward
        self.buffer.append({
            "state":    state,
            "action":   action,
            "reward":   reward,
            "done":     float(done),
            "log_prob": log_prob,
        })
        if done:
            self.episode_count += 1

    # ── 정책 업데이트 ─────────────────────────────────────────────
    def update(self) -> Optional[float]:
        """
        PPO 업데이트 — 버퍼가 batch_size 이상 쌓였을 때 호출

        Returns:
            average policy loss (None if buffer insufficient)
        """
        if len(self.buffer) < self.batch_size:
            return None

        states   = np.array([t["state"]    for t in self.buffer], dtype=np.float32)
        actions  = np.array([t["action"]   for t in self.buffer], dtype=np.int64)
        rewards  = np.array([t["reward"]   for t in self.buffer], dtype=np.float32)
        dones    = np.array([t["done"]     for t in self.buffer], dtype=np.float32)
        old_lps  = np.array([t["log_prob"] for t in self.buffer], dtype=np.float32)

        # GAE (Generalized Advantage Estimation)
        values   = self._get_values(states)
        advs, rets = self._compute_gae(rewards, values, dones)

        # 정규화
        advs = (advs - advs.mean()) / (advs.std() + 1e-8)

        if self._backend == "torch":
            loss = self._update_torch(states, actions, advs, rets, old_lps)
        else:
            loss = self._linear.update(states, actions, advs, rets, old_lps,
                                       self.clip_eps, self.entropy_coef)

        self.buffer.clear()
        self.update_count += 1
        logger.info(f"[PPO] 업데이트 #{self.update_count} loss={loss:.4f}")
        return loss

    def _get_values(self, states: np.ndarray) -> np.ndarray:
        if self._backend == "torch":
            with torch.no_grad():
                x = torch.FloatTensor(states)
                _, vals = self._net(x)
                return vals.squeeze(-1).numpy()
        else:
            return np.array([self._linear.get_value(s) for s in states])

    def _compute_gae(
        self,
        rewards: np.ndarray,
        values:  np.ndarray,
        dones:   np.ndarray,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """GAE 어드밴티지 계산"""
        n        = len(rewards)
        advs     = np.zeros(n, dtype=np.float32)
        rets     = np.zeros(n, dtype=np.float32)
        last_adv = 0.0
        last_val = 0.0  # 마지막 스텝 이후 가치

        for t in reversed(range(n)):
            mask     = 1.0 - dones[t]
            delta    = rewards[t] + self.gamma * last_val * mask - values[t]
            last_adv = delta + self.gamma * self.lam * mask * last_adv
            advs[t]  = last_adv
            last_val = values[t]

        rets = advs + values
        return advs, rets

    def _update_torch(
        self,
        states:  np.ndarray,
        actions: np.ndarray,
        advs:    np.ndarray,
        rets:    np.ndarray,
        old_lps: np.ndarray,
    ) -> float:
        if not _TORCH_OK:
            return 0.0

        s_t   = torch.FloatTensor(states)
        a_t   = torch.LongTensor(actions)
        adv_t = torch.FloatTensor(advs)
        ret_t = torch.FloatTensor(rets)
        olp_t = torch.FloatTensor(old_lps)

        total_loss = 0.0
        for _ in range(self.n_epochs):
            logits, vals = self._net(s_t)
            dist         = torch.distributions.Categorical(logits=logits)
            log_probs    = dist.log_prob(a_t)
            entropy      = dist.entropy().mean()

            ratio        = torch.exp(log_probs - olp_t)
            clipped      = torch.clamp(ratio, 1 - self.clip_eps, 1 + self.clip_eps)
            policy_loss  = -torch.min(ratio * adv_t, clipped * adv_t).mean()
            value_loss   = 0.5 * (vals.squeeze(-1) - ret_t).pow(2).mean()

            loss = policy_loss + 0.5 * value_loss - self.entropy_coef * entropy

            self._optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self._net.parameters(), 0.5)
            self._optimizer.step()
            total_loss += loss.item()

        return total_loss / self.n_epochs

    # ── 저장 / 불러오기 ───────────────────────────────────────────
    def save(self, path: str):
        import os, pickle
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if self._backend == "torch":
            torch.save(self._net.state_dict(), path)
        else:
            with open(path, "wb") as f:
                pickle.dump({"W": self._linear.W, "b": self._linear.b,
                             "Wv": self._linear.Wv, "bv": self._linear.bv}, f)
        logger.info(f"[PPO] 정책 저장: {path}")

    def load(self, path: str):
        import pickle
        if self._backend == "torch" and _TORCH_OK:
            self._net.load_state_dict(torch.load(path, map_location="cpu"))
        else:
            with open(path, "rb") as f:
                d = pickle.load(f)
            self._linear.W  = d["W"]
            self._linear.b  = d["b"]
            self._linear.Wv = d["Wv"]
            self._linear.bv = d["bv"]
        logger.info(f"[PPO] 정책 로드: {path}")

    def get_stats(self) -> dict:
        return {
            "backend":        self._backend,
            "update_count":   self.update_count,
            "episode_count":  self.episode_count,
            "buffer_size":    len(self.buffer),
            "avg_reward":     round(self.total_reward / max(self.episode_count, 1), 4),
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agent = PPOAgent(batch_size=32)

    env = TradingEnvironment(max_steps=50)
    import numpy as np
    candles  = [{"close": 380.0 + np.random.randn() * 0.5} for _ in range(50)]
    features = [np.random.randn(STATE_DIM - 4).astype(np.float32) for _ in range(50)]
    env.load_episode(candles, features)

    state = env.reset()
    for _ in range(50):
        action, log_prob = agent.select_action(state)
        next_s, reward, done, info = env.step(action)
        agent.record(state, action, reward, done, log_prob)
        state = next_s
        if done:
            break

    loss = agent.update()
    print(f"loss={loss}, stats={agent.get_stats()}")
