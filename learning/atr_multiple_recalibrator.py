# learning/atr_multiple_recalibrator.py — ATR배수 임계값 3종 발동률 드리프트 모니터
"""
[신설] 매주 daily_close() 내부에서 호출 (ThresholdRecalibrator/EntryHorizonRecalibrator와
동일 훅 — 금요일 + 최근 실행 후 7일 이상 경과 시에만).

대상 4개(config.settings.ATR_MULTIPLE_RECAL_TARGETS): CHASE_FILTER_ATR_THRESHOLD/
_MEANREV, COUNTERTREND_ATR_THRESHOLD, REGIME_EXHAUSTION_EXT_ATR_THRESHOLD.
전부 price_extension_atr(10분)/price_extension_atr_60m(60분) 연장폭 비율에 대한
정적 배수 임계값인데, 그중 둘(COUNTERTREND/REGIME_EXHAUSTION)은 코드 주석에 이미
"보정 데이터 없어 CHASE_FILTER와 동일값 채택"/"초기값, 표본 축적 후 재보정 검토"라고
명시돼 있다 — entry_horizon(374차)이 겪었던 "설계 당시 가정과 실측 분포가 어긋나
조용히 죽어있는 임계값" 패턴이 재발할 위험이 같은 계열로 존재한다.

다만 ThresholdRecalibrator·EntryHorizonRecalibrator와 달리 이 4개는 "N등분" 같은
명확한 목표 비율이 없는 희귀사건(연장추격/역추세) 트리거라, 33/67 percentile로
"권장 재산출값"을 제안하는 방식이 부적절하다(그 자체가 근거 없는 새 숫자를 만드는
꼴). 대신 "지금 이 임계값이면 최근 실측 데이터에서 얼마나 자주 발동하는가"(발동률)를
매주 기록해, 발동률이 직전 기록 대비 크게 바뀌면 경보만 낸다 — 자동 반영 없음, 사람이
재검토(§9 사전등록 원칙과 동일).
"""
import datetime
import json
import logging
import sqlite3
from typing import Dict, List, Optional

logger = logging.getLogger("LEARNING")


class ATRMultipleRecalibrator:
    """ATR배수 임계값 3종(4개 타깃) 발동률 드리프트 모니터 (자동 반영 없음)."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            from config.settings import DB_DIR
            import os
            db_path = os.path.join(DB_DIR, "atr_multiple_monitor.db")
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS atr_multiple_log (
                    date              TEXT NOT NULL,
                    target_key        TEXT NOT NULL,
                    threshold         REAL,
                    trigger_rate_pct  REAL,
                    n_samples         INTEGER,
                    prev_trigger_rate_pct REAL,
                    delta_pct_pts     REAL,
                    alert_level       TEXT,
                    PRIMARY KEY (date, target_key)
                )
            """)
            conn.commit()

    # ── 실행 간격 게이트 (entry_horizon_recalibrator와 동일 패턴) ──────
    def _last_run_date(self) -> Optional[str]:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT MAX(date) FROM atr_multiple_log").fetchone()
        return row[0] if row and row[0] else None

    def should_run(self, today: str) -> bool:
        from config.settings import ATR_MULTIPLE_RECAL_RUN_INTERVAL_DAYS
        last = self._last_run_date()
        if last is None:
            return True
        elapsed = (
            datetime.date.fromisoformat(today) - datetime.date.fromisoformat(last)
        ).days
        return elapsed >= ATR_MULTIPLE_RECAL_RUN_INTERVAL_DAYS

    def run_if_due(self, today: Optional[str] = None) -> Optional[Dict[str, dict]]:
        if today is None:
            today = datetime.date.today().isoformat()
        if not self.should_run(today):
            logger.debug("[ATRMultipleRecal] 재실행 간격 미도달 — 스킵")
            return None
        return self.run(today)

    # ── 메인 실행 ────────────────────────────────────────────────
    def run(self, today: Optional[str] = None) -> Dict[str, dict]:
        from config.settings import (
            RAW_DATA_DB, ATR_MULTIPLE_RECAL_TARGETS,
            ATR_MULTIPLE_RECAL_LOOKBACK_DAYS,
            ATR_MULTIPLE_RECAL_DELTA_WATCH, ATR_MULTIPLE_RECAL_DELTA_UPDATE,
        )
        import config.settings as _settings

        if today is None:
            today = datetime.date.today().isoformat()

        try:
            values_by_feature = self._load_features(
                RAW_DATA_DB, ATR_MULTIPLE_RECAL_TARGETS, ATR_MULTIPLE_RECAL_LOOKBACK_DAYS
            )
        except Exception as exc:
            logger.warning("[ATRMultipleRecal] 데이터 로드 실패: %s", exc)
            return {}

        results: Dict[str, dict] = {}
        rows = []
        for key, cfg in ATR_MULTIPLE_RECAL_TARGETS.items():
            feat_vals = values_by_feature.get(cfg["feature"], [])
            n = len(feat_vals)
            if n < 100:
                logger.info("[ATRMultipleRecal] %s: 샘플 부족 (%d < 100) — 건너뜀", key, n)
                continue

            threshold = float(getattr(_settings, cfg["setting"], 0.0))
            n_trigger = sum(1 for v in feat_vals if abs(v) > threshold)
            trigger_rate = n_trigger / n * 100.0

            prev_rate = self._prev_trigger_rate(key, today)
            delta = (trigger_rate - prev_rate) if prev_rate is not None else None

            alert = "CLEAR"
            if delta is not None:
                if abs(delta) >= ATR_MULTIPLE_RECAL_DELTA_UPDATE:
                    alert = "UPDATE"
                elif abs(delta) >= ATR_MULTIPLE_RECAL_DELTA_WATCH:
                    alert = "WATCHLIST"

            result = {
                "label":       cfg["label"],
                "threshold":   threshold,
                "trigger_rate_pct": round(trigger_rate, 2),
                "n_samples":   n,
                "prev_trigger_rate_pct": round(prev_rate, 2) if prev_rate is not None else None,
                "delta_pct_pts": round(delta, 2) if delta is not None else None,
                "alert":       alert,
            }
            results[key] = result
            rows.append((today, key, threshold, result["trigger_rate_pct"], n,
                         result["prev_trigger_rate_pct"], result["delta_pct_pts"], alert))

        self._save(rows)
        self._log_summary(results, today)
        return results

    # ── 데이터 로드 ──────────────────────────────────────────────
    def _load_features(self, raw_db: str, targets: dict, lookback_days: int) -> Dict[str, List[float]]:
        """raw_features 최근 lookback_days 거래일에서 대상 피처들의 값을 로드."""
        feature_names = sorted({cfg["feature"] for cfg in targets.values()})

        with sqlite3.connect(raw_db, timeout=10) as conn:
            day_rows = conn.execute(
                "SELECT DISTINCT substr(ts,1,10) d FROM raw_features ORDER BY d DESC LIMIT ?",
                (lookback_days,),
            ).fetchall()
            since = min(r[0] for r in day_rows) if day_rows else "1970-01-01"
            feat_rows = conn.execute(
                "SELECT features FROM raw_features WHERE ts >= ? ORDER BY ts",
                (since + " 00:00:00",),
            ).fetchall()

        out: Dict[str, List[float]] = {f: [] for f in feature_names}
        for (fj,) in feat_rows:
            try:
                fd = json.loads(fj)
            except Exception:
                continue
            for f in feature_names:
                v = fd.get(f)
                if v is not None:
                    try:
                        out[f].append(float(v))
                    except (TypeError, ValueError):
                        continue
        return out

    def _prev_trigger_rate(self, key: str, today: str) -> Optional[float]:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                """SELECT trigger_rate_pct FROM atr_multiple_log
                   WHERE target_key = ? AND date < ? ORDER BY date DESC LIMIT 1""",
                (key, today),
            ).fetchone()
        return float(row[0]) if row and row[0] is not None else None

    # ── DB 저장 ──────────────────────────────────────────────────
    def _save(self, rows: list):
        if not rows:
            return
        with sqlite3.connect(self.db_path) as conn:
            conn.executemany(
                """
                INSERT OR REPLACE INTO atr_multiple_log
                (date, target_key, threshold, trigger_rate_pct, n_samples,
                 prev_trigger_rate_pct, delta_pct_pts, alert_level)
                VALUES (?,?,?,?,?,?,?,?)
                """,
                rows,
            )
            conn.commit()

    # ── 로그 출력 ────────────────────────────────────────────────
    def _log_summary(self, results: dict, today: str):
        if not results:
            return
        lines = [f"[ATRMultipleRecal] {today} 발동률 드리프트"]
        for key, r in results.items():
            tag = ""
            if r["alert"] == "UPDATE":
                tag = " *** UPDATE 권고 (발동률 급변)"
            elif r["alert"] == "WATCHLIST":
                tag = " * WATCHLIST"
            prev = f"{r['prev_trigger_rate_pct']:.1f}%" if r["prev_trigger_rate_pct"] is not None else "—"
            delta = f"{r['delta_pct_pts']:+.1f}%p" if r["delta_pct_pts"] is not None else "—"
            lines.append(
                f"  {key:18s} threshold={r['threshold']:.2f}  "
                f"발동률={r['trigger_rate_pct']:.1f}%(이전 {prev}, Δ{delta})  "
                f"n={r['n_samples']}  [{r['alert']}]{tag}"
            )
        logger.info("\n".join(lines))

    # ── 최근 이력 조회 (대시보드용) ─────────────────────────────
    def recent_log(self, n_weeks: int = 8) -> List[dict]:
        cutoff = (
            datetime.date.today() - datetime.timedelta(weeks=n_weeks)
        ).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM atr_multiple_log WHERE date >= ? ORDER BY date DESC, target_key",
                (cutoff,),
            ).fetchall()
        cols = [
            "date", "target_key", "threshold", "trigger_rate_pct", "n_samples",
            "prev_trigger_rate_pct", "delta_pct_pts", "alert_level",
        ]
        return [dict(zip(cols, r)) for r in rows]
