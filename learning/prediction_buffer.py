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
import time
from typing import Dict, List, Optional, Tuple

from config.settings import HORIZONS, HORIZON_THRESHOLDS, PREDICTIONS_DB, SIGMA_K
from config.constants import DIRECTION_UP, DIRECTION_DOWN, DIRECTION_FLAT
from learning.meta_labeling import compact_feature_json, derive_meta_label
from model.target_builder import build_single_target
from utils.db_utils import (
    execute, executemany, fetchall, fetchone, get_candle_close, get_conn,
    _lock as _db_write_lock,
)

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
                toxicity_action, toxicity_score, toxicity_score_ma, toxicity_size_mult, toxicity_reason,
                checklist_reason, meta_entry_quality_prob,
                quantile_expected_pt, quantile_uncertainty_pt
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                str(decision.get("checklist_reason", "")),
                (decision.get("meta_gate") or {}).get("entry_quality_prob"),
                ((decision.get("meta_gate") or {}).get("quantile_estimate") or {}).get("expected_pt"),
                ((decision.get("meta_gate") or {}).get("quantile_estimate") or {}).get("uncertainty_pt"),
            ),
        )

    @staticmethod
    def _normalize_probs(
        direction: int, confidence: float,
        up_prob=None, down_prob=None, flat_prob=None,
    ) -> Tuple[float, float, float, float]:
        """확률 정규화 (save_prediction / save_step9_batch 공용)"""
        try:
            confidence = float(confidence)
        except (TypeError, ValueError):
            confidence = 1 / 3
        if not math.isfinite(confidence):
            confidence = 1 / 3

        def _safe(v, fb):
            try:
                v = float(v)
            except (TypeError, ValueError):
                v = fb
            if not math.isfinite(v):
                v = fb
            return min(max(v, 0.0), 1.0)

        if up_prob is None or down_prob is None or flat_prob is None:
            side = max(0.0, 1.0 - confidence) / 2.0
            if direction == DIRECTION_UP:
                up_prob, down_prob, flat_prob = confidence, side, side
            elif direction == DIRECTION_DOWN:
                up_prob, down_prob, flat_prob = side, confidence, side
            else:
                up_prob, down_prob, flat_prob = side, side, confidence

        return (
            confidence,
            _safe(up_prob, 1 / 3),
            _safe(down_prob, 1 / 3),
            _safe(flat_prob, 1 / 3),
        )

    def save_step9_batch(
        self,
        *,
        ts: str,
        sigma_at_t: float,
        horizon_proba: Dict,
        features_clean: Dict,
        regime: str,
        micro_regime: str,
        decision: Dict,
    ) -> None:
        """STEP 9: 전 호라이즌 예측 + 앙상블 결정을 1연결 트랜잭션으로 저장.

        기존 save_prediction×N + save_ensemble_decision 대비 연결 7회 → 1회.
        """
        feat_json = json.dumps(features_clean, ensure_ascii=False) if features_clean else "{}"
        try:
            _sigma = float(sigma_at_t) if sigma_at_t else 0.0
        except (TypeError, ValueError):
            _sigma = 0.0

        pred_rows: List[Tuple] = []
        for h_name, h_res in horizon_proba.items():
            conf, up, dn, fl = self._normalize_probs(
                h_res.get("direction", 0),
                h_res.get("confidence", 1 / 3),
                h_res.get("up"), h_res.get("down"), h_res.get("flat"),
            )
            pred_rows.append((ts, h_name, h_res.get("direction", 0), conf, up, dn, fl, feat_json, _sigma))

        gate = decision.get("gating") or {}
        ens_row: Tuple = (
            ts, regime, micro_regime,
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
            json.dumps(features_clean or {}, ensure_ascii=False),
            str((decision.get("meta_gate") or {}).get("action", "")),
            float((decision.get("meta_gate") or {}).get("meta_confidence", 0.0) or 0.0),
            float((decision.get("meta_gate") or {}).get("size_multiplier", 0.0) or 0.0),
            str((decision.get("meta_gate") or {}).get("reason", "")),
            str((decision.get("toxicity_gate") or {}).get("action", "")),
            float((decision.get("toxicity_gate") or {}).get("score", 0.0) or 0.0),
            float((decision.get("toxicity_gate") or {}).get("score_ma", 0.0) or 0.0),
            float((decision.get("toxicity_gate") or {}).get("size_multiplier", 0.0) or 0.0),
            str((decision.get("toxicity_gate") or {}).get("reason", "")),
            json.dumps(decision.get("entry_gate") or {}, ensure_ascii=False),
            int(bool(decision.get("entry_final_ok", False))),
            int(decision.get("entry_qty", 0) or 0),
            str(decision.get("entry_mode", "")),
            int(bool(decision.get("entry_executed", False))),
            str(decision.get("entry_block_reason", "")),
            str(decision.get("checklist_reason", "")),
            (decision.get("meta_gate") or {}).get("entry_quality_prob"),
            ((decision.get("meta_gate") or {}).get("quantile_estimate") or {}).get("expected_pt"),
            ((decision.get("meta_gate") or {}).get("quantile_estimate") or {}).get("uncertainty_pt"),
        )

        with get_conn(PREDICTIONS_DB, timeout=3.0) as conn:  # 3s fail-fast (기본 10s 대비 CB⑤ 5s 이내 실패)
            if pred_rows:
                conn.executemany(
                    """INSERT INTO predictions
                       (ts, horizon, direction, confidence, up_prob, down_prob, flat_prob,
                        features, sigma_at_t)
                       VALUES (?,?,?,?,?,?,?,?,?)""",
                    pred_rows,
                )
            conn.execute(
                """INSERT INTO ensemble_decisions (
                       ts, regime, micro_regime, direction, confidence,
                       up_score, down_score, flat_score,
                       grade, auto_entry, regime_ok, min_conf,
                       gate_reason, gate_strength, gate_delta, gate_blocked,
                       gate_signals, detail, features,
                       meta_action, meta_confidence, meta_size_mult, meta_reason,
                       toxicity_action, toxicity_score, toxicity_score_ma,
                       toxicity_size_mult, toxicity_reason,
                       entry_gate_json, entry_final_ok, entry_qty, entry_mode,
                       entry_executed, entry_block_reason,
                       checklist_reason, meta_entry_quality_prob,
                       quantile_expected_pt, quantile_uncertainty_pt
                   ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                ens_row,
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
        sigma_at_t: float = 0.0,
    ):
        """예측 단건 저장 (save_step9_batch 미사용 시 fallback)"""
        conf, up, dn, fl = self._normalize_probs(direction, confidence, up_prob, down_prob, flat_prob)
        feat_json = json.dumps(features, ensure_ascii=False) if features else "{}"
        try:
            sigma_at_t = float(sigma_at_t) if sigma_at_t else 0.0
        except (TypeError, ValueError):
            sigma_at_t = 0.0
        execute(
            PREDICTIONS_DB,
            """INSERT INTO predictions
               (ts, horizon, direction, confidence, up_prob, down_prob, flat_prob, features, sigma_at_t)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (ts, horizon, direction, conf, up, dn, fl, feat_json, sigma_at_t),
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
        from config.settings import RAW_DATA_DB
        from utils.db_utils import get_conn

        current_dt = datetime.datetime.strptime(current_ts, "%Y-%m-%d %H:%M:%S")

        # 각 호라이즌의 target_ts 미리 계산
        horizon_targets = {
            h: (current_dt - datetime.timedelta(minutes=m)).strftime("%Y-%m-%d %H:%M:%S")
            for h, m in HORIZONS.items()
        }
        target_tss = list(horizon_targets.values())

        # [P0-Timing] verify_and_update 구간별 소요시간 — PipePerf "S2"(=STEP1 본문)
        # 정체 원인을 raw_fetch/pred_select/pred_update/pred_insert 중 어디인지 확정하기 위함.
        _vt0 = time.perf_counter()

        # ── DB 1: RAW_DATA_DB — 필요한 종가 일괄 조회 (락 불필요: WAL 읽기 전용) ──
        # SQLite WAL 모드는 읽기와 쓰기를 동시 허용하므로 _db_write_lock 없이 안전하게 읽을 수 있다.
        # timeout=3.0: 기본 10s 대신 짧게 fail-fast — 파이프라인 CB⑤ 임계(5000ms) 전에
        # 멈춰서 차라리 이번 분 검증을 스킵하고 다음 분에서 재시도하게 함.
        candle_map: Dict[str, float] = {}
        try:
            placeholders = ",".join("?" * len(target_tss))
            with get_conn(RAW_DATA_DB, timeout=3.0) as raw_conn:
                for r in raw_conn.execute(
                    f"SELECT ts, close FROM raw_candles WHERE ts IN ({placeholders})",
                    target_tss,
                ).fetchall():
                    candle_map[r["ts"]] = float(r["close"])
        except Exception as _raw_e:
            logger.warning("[Buffer] raw_candles 배치 조회 실패, fallback: %s", _raw_e)
            for tts in target_tss:
                v = get_candle_close(tts)
                if v is not None:
                    candle_map[tts] = v

        _vt1 = time.perf_counter()   # raw_fetch 완료

        # ── DB 2: PREDICTIONS_DB — SELECT(락 없음) + UPDATE/INSERT(락 있음) 분리 ──
        # 근본 원인: _db_write_lock을 SELECT에도 걸어두면 _db_write_worker(STEP4 raw_data.db 쓰기)가
        # lock을 점유하는 동안 STEP1 SELECT가 5~12초 대기 → CB⑤ 3회 연속 유발.
        # 수정: SELECT는 WAL 읽기(락 불필요), UPDATE/INSERT만 쓰기 락으로 직렬화.
        verified = []
        update_rows: List[Tuple] = []
        meta_rows: List[Tuple] = []
        _vt_select = _vt_update = _vt_insert = _vt1   # 예외 발생 시에도 길이 일관성 유지

        # ── 2-A: SELECT (락 없음 — WAL 동시 읽기) ──────────────────────────────
        try:
            with get_conn(PREDICTIONS_DB, timeout=3.0) as pred_conn:
                for horizon, target_ts in horizon_targets.items():
                    h_min = HORIZONS[horizon]

                    row = pred_conn.execute(
                        """SELECT id, direction, confidence, up_prob, down_prob, flat_prob,
                                  features, sigma_at_t
                           FROM predictions
                           WHERE ts = ? AND horizon = ? AND actual IS NULL""",
                        (target_ts, horizon),
                    ).fetchone()
                    if row is None:
                        continue

                    target_close = candle_map.get(target_ts)
                    if target_close is None:
                        continue

                    pred_id  = row["id"]
                    pred_dir = row["direction"]

                    _sigma_saved = float(row["sigma_at_t"] or 0.0)
                    if _sigma_saved > 0 and SIGMA_K > 0:
                        threshold = _sigma_saved / 100.0 * SIGMA_K * math.sqrt(h_min)
                    else:
                        threshold = HORIZON_THRESHOLDS.get(horizon, 0.0003)

                    actual  = build_single_target(target_close, current_price, threshold)
                    correct = int(actual == pred_dir)
                    update_rows.append((actual, correct, pred_id))

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
                    meta_rows.append((
                        target_ts, horizon, int(pred_dir), int(actual),
                        float(row["confidence"] or 0.0),
                        row["up_prob"], row["down_prob"], row["flat_prob"],
                        float(target_close), float(current_price),
                        float(meta["realized_move"]), float(meta["threshold_move"]),
                        meta["meta_action"], float(meta["meta_score"]),
                        compact_feature_json(feat_dict),
                    ))
                    verified.append({
                        "id":         pred_id,
                        "ts":         target_ts,
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
                        "[Buffer] %s 검증: pred=%s actual=%s (%s) "
                        "target_close=%.2f→current=%.2f",
                        horizon, pred_dir, actual,
                        "✓" if correct else "✗",
                        target_close, current_price,
                    )

            _vt_select = time.perf_counter()   # 호라이즌별 SELECT 루프 완료
        except Exception as _sel_e:
            logger.warning("[Buffer] verify_and_update SELECT 오류: %s", _sel_e)

        # ── 2-B: UPDATE + INSERT (락 있음 — 쓰기 직렬화) ──────────────────────
        try:
            with _db_write_lock:
                with get_conn(PREDICTIONS_DB, timeout=3.0) as pred_conn:
                    if update_rows:
                        pred_conn.executemany(
                            "UPDATE predictions SET actual = ?, correct = ? WHERE id = ?",
                            update_rows,
                        )
                    _vt_update = time.perf_counter()   # UPDATE executemany 완료
                    if meta_rows:
                        pred_conn.executemany(
                            """INSERT INTO meta_labels (
                                   ts, horizon, predicted, actual, confidence,
                                   up_prob, down_prob, flat_prob,
                                   target_close, future_close, realized_move, threshold_move,
                                   meta_action, meta_score, features
                               ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                            meta_rows,
                        )
                    _vt_insert = time.perf_counter()   # INSERT executemany 완료
        except Exception as _e:
            logger.warning("[Buffer] verify_and_update 배치 오류: %s", _e)

        # [P0-Timing] 300ms 초과 시 구간별 분해 — PipePerf "S2"(=STEP1 본문) 정체 원인 확정용
        _v_total_ms = (time.perf_counter() - _vt0) * 1000
        if _v_total_ms > 300:
            logger.warning(
                "[Buffer-Timing] total=%dms raw_fetch=%dms pred_select=%dms "
                "pred_update=%dms pred_insert=%dms verified=%d",
                _v_total_ms,
                (_vt1 - _vt0) * 1000,
                (_vt_select - _vt1) * 1000,
                (_vt_update - _vt_select) * 1000,
                (_vt_insert - _vt_update) * 1000,
                len(verified),
            )

        return verified

    def recent_accuracy(self, horizon: str, last_n: int = 50,
                        exclude_flat: bool = False,
                        min_conf: float = 0.0,
                        since_ts: str = None,
                        min_samples: int = 0) -> float:
        """최근 N회 정확도.

        exclude_flat: FLAT 예측(predicted=0) 제외 — CB③와 동일 기준
        min_conf:     이 값 이하 confidence 제외 (bootstrap/uniform fallback 차단)
        since_ts:     이 타임스탬프 이후 예측만 집계 (이전 세션 혼입 차단)
        min_samples:  유효 샘플이 이 수 미만이면 0.5 반환 (초기 불안정 방지)
        """
        conds = ["horizon = ?", "actual IS NOT NULL"]
        params = [horizon]
        if exclude_flat:
            conds.append("predicted != 0")
        if min_conf > 0.0:
            conds.append("confidence > ?")
            params.append(min_conf)
        if since_ts:
            conds.append("ts >= ?")
            params.append(since_ts)
        params.append(last_n)

        rows = fetchall(
            PREDICTIONS_DB,
            "SELECT correct FROM predictions"
            " WHERE " + " AND ".join(conds) +
            " ORDER BY id DESC LIMIT ?",
            tuple(params),
        )
        if not rows or len(rows) < min_samples:
            return 0.5
        return sum(r["correct"] for r in rows) / len(rows)

    def get_unverified_count(self) -> int:
        row = fetchone(
            PREDICTIONS_DB,
            "SELECT COUNT(*) AS cnt FROM predictions WHERE actual IS NULL",
        )
        return row["cnt"] if row else 0
