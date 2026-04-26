# research_bot/evaluators/alpha_evaluator.py — 알파 평가기
"""
AlphaEvaluator: 유전자 하나를 역사적 데이터로 평가.

평가 파이프라인:
  1. 피처 행렬 조립 (feature_ids + params 기반)
  2. 신호 생성 (logic_type 적용)
  3. 수익률 레이블 계산 (hold_bars 후 종가 변화)
  4. IS IC 계산 (Spearman 상관)
  5. IS Sharpe 계산
  6. Walk-Forward OOS 검증 (마지막 20% 구간)
  7. 종합 점수 = compute_fitness()

최소 통과 기준 (PASS):
  IC   ≥ 0.02
  Sharpe ≥ 0.8  (실전 기준보다 낮춤 — 후보 단계)
  n_samples ≥ 300
  OOS Sharpe > 0  (수익 유지)
"""
import logging
import numpy as np
from typing import List, Dict, Optional, Tuple

from research_bot.alpha_gene import AlphaGene, compute_fitness

logger = logging.getLogger(__name__)

# ── 통과 기준 ──────────────────────────────────────────────────────
MIN_IC        = 0.02
MIN_SHARPE    = 0.8
MIN_SAMPLES   = 300
MIN_OOS_SHP   = 0.0    # OOS 음수면 탈락
OOS_RATIO     = 0.20   # 마지막 20%를 OOS로 사용


class AlphaEvaluator:
    """유전자 → 역사 데이터로 평가 → 점수 갱신."""

    def __init__(self, risk_free_rate: float = 0.035):
        self.rf = risk_free_rate
        self._trades_per_year = 250 * 6   # 연간 거래 횟수 (하루 6회)

    # ── 메인 평가 ─────────────────────────────────────────────────
    def evaluate(
        self,
        gene: AlphaGene,
        candles: List[dict],
        feature_matrix: Optional[Dict[str, List[float]]] = None,
    ) -> bool:
        """
        Args:
            gene           : 평가할 유전자
            candles        : [{"close": float, "high": float, ...}, ...]  시간 순
            feature_matrix : {feature_id: [값 리스트]} 사전 계산된 피처 (없으면 candles에서 추출)

        Returns:
            True  = PASS (후보 승격 가능)
            False = FAIL
        """
        if len(candles) < MIN_SAMPLES + gene.hold_bars + 10:
            logger.debug("Gene %s: 데이터 부족 (%d봉)", gene.gene_id, len(candles))
            return False

        # 1. 피처 행렬 조립
        X, labels = self._build_signal_and_labels(gene, candles, feature_matrix)
        if X is None or len(X) < MIN_SAMPLES:
            return False

        n        = len(X)
        oos_n    = max(int(n * OOS_RATIO), 50)
        is_n     = n - oos_n

        X_is  = X[:is_n];  y_is  = labels[:is_n]
        X_oos = X[is_n:];  y_oos = labels[is_n:]

        # 2. IS 평가
        ic_is     = self._spearman_ic(X_is, y_is)
        sharpe_is = self._signal_sharpe(X_is, y_is)
        wr_is     = self._win_rate(X_is, y_is)

        # 3. OOS 평가
        ic_oos     = self._spearman_ic(X_oos, y_oos)
        sharpe_oos = self._signal_sharpe(X_oos, y_oos)

        # 4. 결과 갱신
        gene.ic        = round(ic_is, 4)
        gene.sharpe    = round(sharpe_is, 3)
        gene.win_rate  = round(wr_is, 4)
        gene.n_samples = is_n
        gene.oos_ic    = round(ic_oos, 4)
        gene.oos_sharpe = round(sharpe_oos, 3)
        gene.score     = compute_fitness(gene)

        # 5. 통과 판정
        passed = (
            ic_is     >= MIN_IC     and
            sharpe_is >= MIN_SHARPE and
            is_n      >= MIN_SAMPLES and
            sharpe_oos >= MIN_OOS_SHP
        )

        logger.info(
            "Gene %s eval: IC=%.3f Sharpe=%.2f WR=%.2f n=%d OOS_SHP=%.2f → %s",
            gene.gene_id, ic_is, sharpe_is, wr_is, is_n, sharpe_oos,
            "PASS" if passed else "FAIL",
        )
        return passed

    # ── 신호 생성 ─────────────────────────────────────────────────
    def _build_signal_and_labels(
        self,
        gene: AlphaGene,
        candles: List[dict],
        feature_matrix: Optional[Dict[str, List[float]]],
    ) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """신호 벡터 X 와 레이블 y 를 반환."""
        try:
            closes = np.array([c["close"] for c in candles], dtype=float)
            n      = len(closes)
            h      = gene.hold_bars

            # 레이블: h봉 후 수익률
            labels = np.zeros(n - h)
            for i in range(n - h):
                labels[i] = (closes[i + h] - closes[i]) / closes[i]

            # 피처 조립
            feat_arrays = []
            for fid in gene.feature_ids:
                if feature_matrix and fid in feature_matrix:
                    arr = np.array(feature_matrix[fid], dtype=float)
                else:
                    arr = self._extract_builtin_feature(fid, candles, gene.params)

                if arr is None or len(arr) < n:
                    continue
                feat_arrays.append(arr[:n])

            if not feat_arrays:
                return None, None

            # 신호 생성 (logic_type)
            X_raw = np.column_stack(feat_arrays)  # (n, n_feat)
            signal = self._apply_logic(gene.logic_type, X_raw)[:n - h]

            # NaN 제거
            mask = np.isfinite(signal) & np.isfinite(labels)
            return signal[mask], labels[mask]

        except Exception as e:
            logger.debug("Gene %s signal build error: %s", gene.gene_id, e)
            return None, None

    def _apply_logic(self, logic_type: str, X: np.ndarray) -> np.ndarray:
        """피처 행렬 → 스칼라 신호."""
        if X.ndim == 1:
            return X

        if logic_type == "momentum":
            # 피처 평균의 부호가 신호
            return X.mean(axis=1)

        elif logic_type == "mean_reversion":
            # 음수 반전
            return -X.mean(axis=1)

        elif logic_type == "breakout":
            # 첫 번째 피처가 롤링 상위/하위 10%인지
            f0  = X[:, 0]
            n   = len(f0)
            w   = 20
            sig = np.zeros(n)
            for i in range(w, n):
                window = f0[i - w:i]
                p90    = np.percentile(window, 90)
                p10    = np.percentile(window, 10)
                if f0[i] > p90:
                    sig[i] = 1.0
                elif f0[i] < p10:
                    sig[i] = -1.0
            return sig

        elif logic_type == "composite":
            # 피처 가중 합 (균등 가중)
            w = np.ones(X.shape[1]) / X.shape[1]
            return X @ w

        elif logic_type == "rank":
            # 피처별 순위 z-score 평균
            from scipy.stats import rankdata
            ranked = np.column_stack([
                (rankdata(X[:, j]) - X.shape[0] / 2) / X.shape[0]
                for j in range(X.shape[1])
            ])
            return ranked.mean(axis=1)

        return X.mean(axis=1)

    # ── 내장 피처 추출 (feature_matrix 없을 때 fallback) ─────────
    def _extract_builtin_feature(
        self,
        fid: str,
        candles: List[dict],
        params: dict,
    ) -> Optional[np.ndarray]:
        """candles dict에서 간단한 기술적 피처 계산."""
        n      = len(candles)
        closes = np.array([c.get("close", 0) for c in candles], dtype=float)
        vols   = np.array([c.get("volume", 0) for c in candles], dtype=float)

        if fid == "cvd":
            # 간이 CVD: 종가 상승이면 +거래량, 하락이면 -거래량
            direction = np.sign(np.diff(closes, prepend=closes[0]))
            raw = np.cumsum(direction * vols)
            return (raw - np.mean(raw)) / (np.std(raw) + 1e-9)

        elif fid == "vwap_dev":
            # 종가와 단순 VWAP 편차
            window = params.get("vwap_window", 20)
            vwap   = np.array([
                np.average(closes[max(0, i-window):i+1],
                           weights=vols[max(0, i-window):i+1] + 1e-9)
                for i in range(n)
            ])
            dev = (closes - vwap) / (vwap + 1e-9)
            return dev

        elif fid == "ofi":
            # 간이 OFI: 호가 데이터 없으므로 거래량 변화로 근사
            return np.diff(vols, prepend=vols[0]) / (vols + 1e-9)

        elif fid == "atr_norm":
            window = params.get("atr_window", 14)
            highs  = np.array([c.get("high", c["close"]) for c in candles], dtype=float)
            lows   = np.array([c.get("low", c["close"]) for c in candles], dtype=float)
            tr     = np.maximum(highs - lows, np.abs(highs - np.roll(closes, 1)))
            atr    = np.array([tr[max(0, i-window+1):i+1].mean() for i in range(n)])
            return atr / (closes + 1e-9)

        elif fid == "mtf_5m_trend":
            window = 5
            return np.array([
                (closes[i] - closes[max(0, i-window)]) / (closes[max(0, i-window)] + 1e-9)
                for i in range(n)
            ])

        elif fid == "mtf_15m_trend":
            window = 15
            return np.array([
                (closes[i] - closes[max(0, i-window)]) / (closes[max(0, i-window)] + 1e-9)
                for i in range(n)
            ])

        else:
            # 알 수 없는 피처 — 0 벡터 반환 (사실상 무의미)
            return np.zeros(n)

    # ── 통계 지표 ─────────────────────────────────────────────────
    @staticmethod
    def _spearman_ic(X: np.ndarray, y: np.ndarray) -> float:
        """Spearman 순위 상관 (IC)."""
        if len(X) < 10:
            return 0.0
        try:
            from scipy.stats import spearmanr
            r, _ = spearmanr(X, y)
            return float(r) if np.isfinite(r) else 0.0
        except Exception:
            # scipy 없을 때 Pearson fallback
            try:
                r = np.corrcoef(X, y)[0, 1]
                return float(r) if np.isfinite(r) else 0.0
            except Exception:
                return 0.0

    def _signal_sharpe(self, signal: np.ndarray, returns: np.ndarray) -> float:
        """신호 방향 * 수익률 기반 Sharpe."""
        if len(signal) < 10:
            return 0.0
        sig_norm  = np.sign(signal)
        strat_ret = sig_norm * returns

        mu  = strat_ret.mean()
        std = strat_ret.std()
        if std < 1e-9:
            return 0.0

        rf_per_trade = self.rf / self._trades_per_year
        sharpe       = (mu - rf_per_trade) / std * np.sqrt(self._trades_per_year)
        return float(sharpe) if np.isfinite(sharpe) else 0.0

    @staticmethod
    def _win_rate(signal: np.ndarray, returns: np.ndarray) -> float:
        """신호 방향과 수익 방향 일치율."""
        if len(signal) == 0:
            return 0.0
        sig_norm = np.sign(signal)
        wins     = np.sum((sig_norm > 0) & (returns > 0)) + np.sum((sig_norm < 0) & (returns < 0))
        valid    = np.sum(sig_norm != 0)
        return float(wins / valid) if valid > 0 else 0.0
