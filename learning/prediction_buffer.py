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
from typing import Dict, List, Optional, Tuple

from config.settings import HORIZONS, HORIZON_THRESHOLDS, PREDICTIONS_DB
from config.constants import DIRECTION_UP, DIRECTION_DOWN, DIRECTION_FLAT
from model.target_builder import build_single_target
from utils.db_utils import execute, fetchall, fetchone, get_candle_close

logger = logging.getLogger("LEARNING")


class PredictionBuffer:
    """예측 저장 + 실시간 검증 버퍼"""

    def save_prediction(
        self,
        ts: str,
        horizon: str,
        direction: int,
        confidence: float,
        features: Optional[Dict] = None,
    ):
        """예측 저장"""
        feat_json = json.dumps(features, ensure_ascii=False) if features else "{}"
        execute(
            PREDICTIONS_DB,
            """INSERT INTO predictions
               (ts, horizon, direction, confidence, features)
               VALUES (?, ?, ?, ?, ?)""",
            (ts, horizon, direction, confidence, feat_json),
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
                """SELECT id, direction, confidence, features
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

            verified.append({
                "id":         pred_id,
                "horizon":    horizon,
                "predicted":  pred_dir,
                "actual":     actual,
                "correct":    bool(correct),
                "confidence": row["confidence"],
                "features":   feat_dict,
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
