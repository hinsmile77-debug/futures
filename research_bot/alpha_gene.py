# research_bot/alpha_gene.py — 알파 유전자 표현형
"""
AlphaGene: 하나의 알파 신호를 완전히 기술하는 데이터 구조.

유전자 구성:
  feature_ids   : 사용할 피처 ID 목록 (최소 1개, 최대 5개)
  params        : 피처별 파라미터 dict (window, period 등)
  logic_type    : 신호 생성 방식
  direction     : 방향성 (1=롱, -1=숏, 0=양방향)
  hold_bars     : 홀딩 기간 (분봉 기준, 1~15)
  entry_threshold / exit_threshold : 진입·청산 임계값
  score         : 종합 적합도 점수 (평가 후 갱신)
  status        : candidate → active → retired
"""
import uuid
import json
import time
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# ── 사용 가능한 피처 ID 목록 (feature_builder와 동기화) ────────────
AVAILABLE_FEATURES = [
    # CORE (절대 교체 불가)
    "cvd", "vwap_dev", "ofi",
    # 미시구조
    "microprice", "lob_imbalance", "queue_exhaust", "cancel_ratio",
    # 멀티 타임프레임
    "mtf_5m_trend", "mtf_15m_trend", "htf_pivot_dist", "round_number_dist",
    # 수급
    "vpin", "herding_signal",
    # 변동성
    "atr_norm", "hurst",
    # 감성
    "news_sentiment", "news_shock",
    # 매크로
    "sp500_ret", "usd_krw_ret", "vix_level",
    # 옵션
    "put_call_ratio", "gex_norm",
    # 수급 (투자자)
    "foreigner_net", "inst_net",
]

# CORE 피처 (절대 교체 불가)
CORE_FEATURES = ["cvd", "vwap_dev", "ofi"]

# ── 로직 타입 ──────────────────────────────────────────────────────
LOGIC_TYPES = [
    "momentum",        # 피처 평균 방향으로 진입
    "mean_reversion",  # 피처 극단값에서 역방향
    "breakout",        # 임계값 돌파
    "composite",       # 가중 합산
    "rank",            # 피처 순위 기반
]


class AlphaGene:
    """알파 신호 하나를 표현하는 유전자."""

    __slots__ = (
        "gene_id", "feature_ids", "params", "logic_type",
        "direction", "hold_bars", "entry_threshold", "exit_threshold",
        "generation", "parent_ids",
        # 평가 결과
        "score", "ic", "sharpe", "win_rate", "n_samples",
        "oos_sharpe", "oos_ic",
        # 생명주기
        "status", "created_at", "promoted_at", "retired_at",
        "consecutive_fails",
    )

    def __init__(
        self,
        feature_ids: List[str],
        params: Optional[Dict[str, Any]] = None,
        logic_type: str = "momentum",
        direction: int = 0,
        hold_bars: int = 3,
        entry_threshold: float = 0.5,
        exit_threshold: float = 0.0,
        generation: int = 0,
        parent_ids: Optional[List[str]] = None,
        gene_id: Optional[str] = None,
    ):
        self.gene_id       = gene_id or str(uuid.uuid4())[:8]
        self.feature_ids   = list(feature_ids)
        self.params        = params or {}
        self.logic_type    = logic_type
        self.direction     = direction      # 1=롱, -1=숏, 0=양방향
        self.hold_bars     = hold_bars
        self.entry_threshold = entry_threshold
        self.exit_threshold  = exit_threshold
        self.generation    = generation
        self.parent_ids    = parent_ids or []

        # 평가 결과 (초기값)
        self.score        = 0.0
        self.ic           = 0.0
        self.sharpe       = 0.0
        self.win_rate     = 0.0
        self.n_samples    = 0
        self.oos_sharpe   = 0.0
        self.oos_ic       = 0.0

        # 생명주기
        self.status            = "candidate"
        self.created_at        = time.time()
        self.promoted_at: Optional[float] = None
        self.retired_at: Optional[float]  = None
        self.consecutive_fails = 0

    # ── 직렬화 ──────────────────────────────────────────────────
    def to_dict(self) -> dict:
        return {
            "gene_id":         self.gene_id,
            "feature_ids":     self.feature_ids,
            "params":          self.params,
            "logic_type":      self.logic_type,
            "direction":       self.direction,
            "hold_bars":       self.hold_bars,
            "entry_threshold": self.entry_threshold,
            "exit_threshold":  self.exit_threshold,
            "generation":      self.generation,
            "parent_ids":      self.parent_ids,
            "score":           self.score,
            "ic":              self.ic,
            "sharpe":          self.sharpe,
            "win_rate":        self.win_rate,
            "n_samples":       self.n_samples,
            "oos_sharpe":      self.oos_sharpe,
            "oos_ic":          self.oos_ic,
            "status":          self.status,
            "created_at":      self.created_at,
            "promoted_at":     self.promoted_at,
            "retired_at":      self.retired_at,
            "consecutive_fails": self.consecutive_fails,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "AlphaGene":
        g = cls(
            feature_ids     = d["feature_ids"],
            params          = d.get("params", {}),
            logic_type      = d.get("logic_type", "momentum"),
            direction       = d.get("direction", 0),
            hold_bars       = d.get("hold_bars", 3),
            entry_threshold = d.get("entry_threshold", 0.5),
            exit_threshold  = d.get("exit_threshold", 0.0),
            generation      = d.get("generation", 0),
            parent_ids      = d.get("parent_ids", []),
            gene_id         = d.get("gene_id"),
        )
        g.score           = d.get("score", 0.0)
        g.ic              = d.get("ic", 0.0)
        g.sharpe          = d.get("sharpe", 0.0)
        g.win_rate        = d.get("win_rate", 0.0)
        g.n_samples       = d.get("n_samples", 0)
        g.oos_sharpe      = d.get("oos_sharpe", 0.0)
        g.oos_ic          = d.get("oos_ic", 0.0)
        g.status          = d.get("status", "candidate")
        g.created_at      = d.get("created_at", time.time())
        g.promoted_at     = d.get("promoted_at")
        g.retired_at      = d.get("retired_at")
        g.consecutive_fails = d.get("consecutive_fails", 0)
        return g

    def __repr__(self) -> str:
        return (
            f"AlphaGene(id={self.gene_id}, "
            f"feats={self.feature_ids}, "
            f"logic={self.logic_type}, "
            f"score={self.score:.3f}, "
            f"status={self.status})"
        )


# ── 적합도 점수 계산 (외부 호출용) ──────────────────────────────────
def compute_fitness(gene: AlphaGene) -> float:
    """
    종합 적합도 점수.
    IC·Sharpe·OOS 일관성을 가중 합산.
    최소 샘플(300) 미충족 시 패널티.
    """
    if gene.n_samples < 300:
        return max(0.0, gene.score * 0.5)  # 샘플 부족 패널티

    # IS (In-Sample) 점수
    ic_score     = min(max(gene.ic, 0.0), 0.1) / 0.1          # 0~1 정규화 (IC 0.1 상한)
    sharpe_score = min(max(gene.sharpe, 0.0), 3.0) / 3.0       # 0~1 정규화 (Sharpe 3 상한)
    wr_score     = max(gene.win_rate - 0.5, 0.0) / 0.2         # 0~1 (승률 50%~70%)

    # OOS 일관성 보너스
    oos_bonus = 0.0
    if gene.oos_sharpe > 0.5 and gene.oos_ic > 0.01:
        oos_bonus = 0.2

    fitness = (
        ic_score     * 0.35 +
        sharpe_score * 0.40 +
        wr_score     * 0.25 +
        oos_bonus
    )
    return round(fitness, 4)
