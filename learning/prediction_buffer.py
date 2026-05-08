# learning/prediction_buffer.py — 예측·실제결과 버퍼 (SQLite)
"""
매분 예측값을 저장하고, N분 후 실제 결과로 검증합니다.
자가학습의 핵심 인프라.

흐름:
  T분: 예측 저장 (direction, confidence, features)
  T+N분: 실제 종가 확인 → actual 업데이트 → 정확도 계산
"""
import json
import datetime
import logging
import math
from typing import Dict, List, Optional, Tuple

from config.settings import HORIZONS, HORIZON_THRESHOLDS, PREDICTIONS_DB
from config.constants import DIRECTION_UP, DIRECTION_DOWN, DIRECTION_FLAT
from learning.meta_labeling import compact_feature_json, derive_meta_label
from model.target_builder import build_single_target
from utils.db_utils import execute, fetchall, fetchone, get_candle_close

logger = logging.getLogger("LEARNING")


class PredictionBuffer:
    """예측 저장 + 실시간 검증 버퍼"""

    def save_ensemble_decision(
        self,
        *,
        ts: str,
        regime: str,
        micro_regime: str,
        decision: Dict,
        features: Optional[Dict] = None,
    ):
        gate = decision.get("gating") or {}
        execute(
            PREDICTIONS_DB,
            """
            INSERT INTO ensemble_decisions (
                ts, regime, micro_regime, direction, confidence,
                up_score, down_score, flat_score,
                grade, auto_entry, regime_ok, min_conf,
                gate_reason, gate_strength, gate_delta, gate_blocked,
                gate_signals, detail, features,
                meta_action, meta_confidence, meta_size_mult, meta_reason,
                toxicity_action, toxicity_score, toxicity_score_ma, toxicity_size_mult, toxicity_reason
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ts,
                regime,
                micro_regime,
                int(decision.get("direction", 0)),
                float(decision.get("confidence", 0.0) or 0.0),
                float(decision.get("up_score", 0.0) or 0.0),
                float(decision.get("down_score", 0.0) or 0.0),
                float(decision.get("flat_score", 0.0) or 0.0),
                str(decision.get("grade", "")),
                int(bool(decision.get("auto_entry", False))),
                int(bool(decision.get("regime_ok", False))),
                float(decision.get("min_conf", 0.0) or 0.0),
                str(gate.get("reason", "")),
                float(gate.get("gate_strength", 0.0) or 0.0),
                float(gate.get("delta", 0.0) or 0.0),
                int(bool(gate.get("blocked", False))),
                json.dumps(gate.get("signals", {}), ensure_ascii=False),
                json.dumps(decision.get("detail", {}), ensure_ascii=False),
                json.dumps(features or {}, ensure_ascii=False),
                str((decision.get("meta_gate") or {}).get("action", "")),
                float((decision.get("meta_gate") or {}).get("meta_confidence", 0.0) or 0.0),
                float((decision.get("meta_gate") or {}).get("size_multiplier", 0.0) or 0.0),
                str((decision.get("meta_gate") or {}).get("reason", "")),
                str((decision.get("toxicity_gate") or {}).get("action", "")),
                float((decision.get("toxicity_gate") or {}).get("score", 0.0) or 0.0),
                float((decision.get("toxicity_gate") or {}).get("score_ma", 0.0) or 0.0),
                float((decision.get("toxicity_gate") or {}).get("size_multiplier", 0.0) or 0.0),
                str((decision.get("toxicity_gate") or {}).get("reason", "")),
            ),
        )

    def save_prediction(
        self,
        ts: str,
        horizon: str,
        direction: int,
        confidence: float,
        up_prob: Optional[float] = None,
        down_prob: Optional[float] = None,
        flat_prob: Optional[float] = None,
        features: Optional[Dict] = None,
    ):
        """예측 저장"""
        try:
            confidence = float(confidence)
        except (TypeError, ValueError):
            confidence = 1 / 3
        if not math.isfinite(confidence):
            confidence = 1 / 3

        def _safe_prob(value, fallback):
            try:
                value = float(value)
            except (TypeError, ValueError):
                value = fallback
            if not math.isfinite(value):
                value = fallback
            return min(max(value, 0.0), 1.0)

        if up_prob is None or down_prob is None or flat_prob is None:
            side = max(0.0, 1.0 - confidence) / 2.0
            if direction == DIRECTION_UP:
                up_prob, down_prob, flat_prob = confidence, side, side
            elif direction == DIRECTION_DOWN:
                up_prob, down_prob, flat_prob = side, confidence, side
            else:
                up_prob, down_prob, flat_prob = side, side, confidence

        up_prob = _safe_prob(up_prob, 1 / 3)
        down_prob = _safe_prob(down_prob, 1 / 3)
        flat_prob = _safe_prob(flat_prob, 1 / 3)

        feat_json = json.dumps(features, ensure_ascii=False) if features else "{}"
        execute(
            PREDICTIONS_DB,
            """INSERT INTO predictions
               (ts, horizon, direction, confidence, up_prob, down_prob, flat_prob, features)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (ts, horizon, direction, confidence, up_prob, down_prob, flat_prob, feat_json),
        )

    def verify_and_update(
        self,
        current_ts: str,
        current_price: float,
    ) -> List[Dict]:
        """
        현재 시각 기준으로 검증 가능한 과거 예측을 찾아 actual 업데이트

        Args:
            current_ts:    현재 분봉 타임스탬프 (YYYY-MM-DD HH:MM:SS)
            current_price: 현재 봉 종가

        Returns:
            검증된 예측 결과 리스트
        """
        verified = []

        for horizon, h_min in HORIZONS.items():
            threshold = HORIZON_THRESHOLDS.get(horizon, 0.0003)

            # T-h분 시각 계산
            current_dt = datetime.datetime.strptime(current_ts, "%Y-%m-%d %H:%M:%S")
            target_dt  = current_dt - datetime.timedelta(minutes=h_min)
            target_ts  = target_dt.strftime("%Y-%m-%d %H:%M:%S")

            # 아직 actual이 없는 예측 조회
            row = fetchone(
                PREDICTIONS_DB,
                """SELECT id, direction, confidence, up_prob, down_prob, flat_prob, features
                   FROM predictions
                   WHERE ts = ? AND horizon = ? AND actual IS NULL""",
                (target_ts, horizon),
            )
            if row is None:
                continue

            pred_id  = row["id"]
            pred_dir = row["direction"]

            # 실제 방향: target_ts 종가 → current_ts 종가
            target_close = get_candle_close(target_ts)
            if target_close is None:
                # raw_candles 미적재 구간 — 건너뜀 (placeholder 방지)
                continue

            actual  = build_single_target(target_close, current_price, threshold)
            correct = int(actual == pred_dir)
            execute(
                PREDICTIONS_DB,
                "UPDATE predictions SET actual = ?, correct = ? WHERE id = ?",
                (actual, correct, pred_id),
            )

            try:
                feat_dict = json.loads(row["features"]) if row["features"] else {}
            except (ValueError, TypeError):
                feat_dict = {}

            meta = derive_meta_label(
                predicted=pred_dir,
                actual=actual,
                confidence=float(row["confidence"] or 0.0),
                target_close=float(target_close),
                future_close=float(current_price),
                threshold_ratio=float(threshold),
            )
            execute(
                PREDICTIONS_DB,
                """
                INSERT INTO meta_labels (
                    ts, horizon, predicted, actual, confidence,
                    up_prob, down_prob, flat_prob,
                    target_close, future_close, realized_move, threshold_move,
                    meta_action, meta_score, features
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    target_ts,
                    horizon,
                    int(pred_dir),
                    int(actual),
                    float(row["confidence"] or 0.0),
                    row["up_prob"],
                    row["down_prob"],
                    row["flat_prob"],
                    float(target_close),
                    float(current_price),
                    float(meta["realized_move"]),
                    float(meta["threshold_move"]),
                    meta["meta_action"],
                    float(meta["meta_score"]),
                    compact_feature_json(feat_dict),
                ),
            )

            verified.append({
                "id":         pred_id,
                "ts":         target_ts,   # 예측이 만들어진 시각 (CB③ 세션 필터용)
                "horizon":    horizon,
                "predicted":  pred_dir,
                "actual":     actual,
                "correct":    bool(correct),
                "confidence": row["confidence"],
                "up_prob":    row["up_prob"],
                "down_prob":  row["down_prob"],
                "flat_prob":  row["flat_prob"],
                "features":   feat_dict,
                "meta_label": meta["meta_action"],
                "meta_score": meta["meta_score"],
            })
            logger.debug(
                f"[Buffer] {horizon} 검증: pred={pred_dir} actual={actual} "
                f"({'✓' if correct else '✗'}) "
                f"target_close={target_close:.2f}→current={current_price:.2f}"
            )

        return verified

    def recent_accuracy(self, horizon: str, last_n: int = 50) -> float:
        """최근 N회 정확도"""
        rows = fetchall(
            PREDICTIONS_DB,
            """SELECT correct FROM predictions
               WHERE horizon = ? AND actual IS NOT NULL
               ORDER BY id DESC LIMIT ?""",
            (horizon, last_n),
        )
        if not rows:
            return 0.5
        return sum(r["correct"] for r in rows) / len(rows)

    def get_unverified_count(self) -> int:
        row = fetchone(
            PREDICTIONS_DB,
            "SELECT COUNT(*) AS cnt FROM predictions WHERE actual IS NULL",
        )
        return row["cnt"] if row else 0
