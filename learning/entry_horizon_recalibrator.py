# learning/entry_horizon_recalibrator.py — entry_horizon(1m/3m/5m TP1 배수) 경계값 재보정 모니터
"""
[375차 신설] 매주 금요일 15:40 daily_close() 내부에서 호출 (ThresholdRecalibrator와 동일 훅).

select_entry_horizon()(model/ensemble_decision.py)은 ATR/1m임계값 비율
(threshold_feasibility)을 3구간(1m/3m/5m)으로 나눠 TP1 목표폭(ATR×0.3/0.5/0.7)을
정하는데, 경계값(374차 재보정 기준 3.5/4.0)이 정적 상수라 시장 변동성 체제가
다시 바뀌면 한쪽 버킷에 고착될 수 있다 — 374차가 발견한 원 버그(경계값 0.8/1.5/
2.5가 실제 분포와 어긋나 61건 실거래 전부 "5m"로만 분류됨)와 동일한 재발 위험.

동작:
  1. raw_features(atr) + raw_candles(close) 최근 LOOKBACK_TRADING_DAYS 거래일로
     threshold_feasibility를 최신 HORIZON_THRESHOLDS["1m"] 기준으로 재계산
     (저장된 과거 threshold_feasibility 값이 아니라 항상 "지금" 설정 기준으로
     재산출 — HORIZON_THRESHOLDS 자체가 ThresholdRecalibrator로 바뀔 수 있어서)
  2. 33/67 분위수로 새 경계값(b1/b2) 후보 산출
  3. 현재 경계값(model.ensemble_decision.ENTRY_HORIZON_B1/B2) 적용 시 각
     버킷(1m/3m/5m) 실제 비중을 직접 계산 — "고착"은 델타%보다 이 비중으로
     더 직접 드러남(374차는 5m=99.0%로 확정)
  4. 경보 수준 판단 및 threshold_monitor.db:entry_horizon_log 저장

경보 트리거:
  WATCHLIST : 어느 한 버킷 비중이 [13%, 54%] 밖 (이상적 33%에서 크게 벗어남)
              또는 |경계값 δ| >= 15%
  UPDATE    : 어느 한 버킷 비중이 [3%, 74%] 밖 (374차 발견 당시 5m=99% 수준의
              고착 재발 조짐) 또는 |경계값 δ| >= 30%

UPDATE/WATCHLIST 경보 시 ENTRY_HORIZON_B1/B2를 자동 교체하지 않음 — 사용자
확인 후 수동 반영(ThresholdRecalibrator와 동일 원칙: "경계값은 모든 진입의
TP1 폭에 영향을 준다").

주 1회(금요일)만 실행하되, 휴장일 등으로 특정 금요일에 세션 자체가 없었던
경우를 대비해 "마지막 실행 후 7일 이상 경과 시"로 재트리거
(atr_ceiling_recalibrator와 동일 패턴) — 374차 원인 규명 중 threshold_monitor.db
가 정확히 이 이유(0717 휴장으로 그 주 금요일 세션 자체가 없었음)로 한 주
누락된 걸 확인, 재발 방지 차원에서 처음부터 이 패턴으로 설계.
"""
import datetime
import json
import logging
import sqlite3
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("LEARNING")

DELTA_ALARM_WATCH   = 15.0   # 경계값 변화율 WATCHLIST 임계 (%)
DELTA_ALARM_UPDATE  = 30.0   # 경계값 변화율 UPDATE 임계 (%)
BUCKET_TARGET       = 33.3   # 버킷당 이상적 비중 (%, 3등분)
BUCKET_WATCH_LO     = 13.0   # WATCHLIST 하한 (%)
BUCKET_WATCH_HI     = 54.0   # WATCHLIST 상한 (%)
BUCKET_UPDATE_LO    = 3.0    # UPDATE 하한 (%) — 이보다 작으면 그 버킷이 거의 죽은 것
BUCKET_UPDATE_HI    = 74.0   # UPDATE 상한 (%) — 이보다 크면 다른 버킷이 거의 죽은 것


class EntryHorizonRecalibrator:
    """entry_horizon(select_entry_horizon) 3-way 경계값 재보정 모니터."""

    LOOKBACK_TRADING_DAYS = 21   # ThresholdRecalibrator와 동일 윈도 통일
    RUN_INTERVAL_CAL_DAYS = 7    # 주 1회, 휴장 금요일 등으로 밀려도 다음 실행일에 자동 보정

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            from config.settings import DB_DIR
            import os
            db_path = os.path.join(DB_DIR, "threshold_monitor.db")
        self.db_path = db_path
        self._init_db()

    # ── DB 초기화 ────────────────────────────────────────────────
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS entry_horizon_log (
                    date            TEXT PRIMARY KEY,
                    current_b1      REAL,
                    current_b2      REAL,
                    recalc_b1       REAL,
                    recalc_b2       REAL,
                    b1_delta_pct    REAL,
                    b2_delta_pct    REAL,
                    bucket_1m_pct   REAL,
                    bucket_3m_pct   REAL,
                    bucket_5m_pct   REAL,
                    alert_level     TEXT,
                    n_samples       INTEGER
                )
            """)
            conn.commit()

    # ── 재실행 간격 관리 (atr_ceiling_recalibrator와 동일 패턴) ────
    def _last_run_date(self) -> Optional[str]:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT MAX(date) FROM entry_horizon_log").fetchone()
        return row[0] if row and row[0] else None

    def should_run(self, today: str) -> bool:
        last = self._last_run_date()
        if last is None:
            return True
        elapsed = (
            datetime.date.fromisoformat(today) - datetime.date.fromisoformat(last)
        ).days
        return elapsed >= self.RUN_INTERVAL_CAL_DAYS

    def run_if_due(self, today: Optional[str] = None) -> Optional[dict]:
        """간격 조건을 만족할 때만 run() 실행. 아니면 None(스킵)."""
        if today is None:
            today = datetime.date.today().isoformat()
        if not self.should_run(today):
            logger.debug("[EntryHorizonRecal] 재실행 간격 미도달 — 스킵")
            return None
        return self.run(today)

    # ── 메인 실행 ────────────────────────────────────────────────
    def run(self, today: Optional[str] = None) -> Optional[dict]:
        from config.settings import RAW_DATA_DB
        from model.ensemble_decision import ENTRY_HORIZON_B1, ENTRY_HORIZON_B2

        if today is None:
            today = datetime.date.today().isoformat()

        try:
            feasibilities = self._load_feasibilities(RAW_DATA_DB)
        except Exception as exc:
            logger.warning("[EntryHorizonRecal] 데이터 로드 실패: %s", exc)
            return None

        n = len(feasibilities)
        if n < 100:
            logger.info("[EntryHorizonRecal] 샘플 부족 (%d < 100) — 건너뜀", n)
            return None

        sorted_f = sorted(feasibilities)
        recalc_b1 = sorted_f[int(n * 0.33)]
        recalc_b2 = sorted_f[int(n * 0.67)]

        def delta_pct(current, recalc):
            if current <= 0:
                return 0.0
            return (recalc - current) / current * 100.0

        b1_delta = delta_pct(ENTRY_HORIZON_B1, recalc_b1)
        b2_delta = delta_pct(ENTRY_HORIZON_B2, recalc_b2)

        # 현재 경계값을 그대로 적용했을 때 실제 버킷 비중 — "고착" 직접 확인
        n_1m = sum(1 for f in feasibilities if f < ENTRY_HORIZON_B1)
        n_3m = sum(1 for f in feasibilities if ENTRY_HORIZON_B1 <= f < ENTRY_HORIZON_B2)
        n_5m = n - n_1m - n_3m
        bucket_1m_pct = n_1m / n * 100.0
        bucket_3m_pct = n_3m / n * 100.0
        bucket_5m_pct = n_5m / n * 100.0

        alert = "CLEAR"
        bucket_pcts = (bucket_1m_pct, bucket_3m_pct, bucket_5m_pct)
        if any(p < BUCKET_WATCH_LO or p > BUCKET_WATCH_HI for p in bucket_pcts):
            alert = "WATCHLIST"
        if max(abs(b1_delta), abs(b2_delta)) >= DELTA_ALARM_WATCH and alert == "CLEAR":
            alert = "WATCHLIST"
        if any(p < BUCKET_UPDATE_LO or p > BUCKET_UPDATE_HI for p in bucket_pcts):
            alert = "UPDATE"
        if max(abs(b1_delta), abs(b2_delta)) >= DELTA_ALARM_UPDATE:
            alert = "UPDATE"

        result = {
            "current_b1": round(ENTRY_HORIZON_B1, 3),
            "current_b2": round(ENTRY_HORIZON_B2, 3),
            "recalc_b1": round(recalc_b1, 3),
            "recalc_b2": round(recalc_b2, 3),
            "b1_delta_pct": round(b1_delta, 1),
            "b2_delta_pct": round(b2_delta, 1),
            "bucket_1m_pct": round(bucket_1m_pct, 1),
            "bucket_3m_pct": round(bucket_3m_pct, 1),
            "bucket_5m_pct": round(bucket_5m_pct, 1),
            "alert": alert,
            "n_samples": n,
        }

        self._save(today, result)
        self._log_summary(result, today)
        return result

    # ── 데이터 로드 ──────────────────────────────────────────────
    def _load_feasibilities(self, raw_db: str) -> List[float]:
        """
        raw_candles(close) + raw_features(atr) 최근 LOOKBACK_TRADING_DAYS 거래일을
        ts로 조인해 threshold_feasibility = atr / (HORIZON_THRESHOLDS["1m"] * close)
        를 "현재" 설정 기준으로 재계산한다. feature_builder.py의 산식과 동일해야
        select_entry_horizon()이 실제로 보는 값과 일치한다.
        """
        from config.settings import HORIZON_THRESHOLDS

        thresh_1m = HORIZON_THRESHOLDS.get("1m", 0.0005)

        with sqlite3.connect(raw_db, timeout=10) as conn:
            day_rows = conn.execute(
                "SELECT DISTINCT substr(ts,1,10) d FROM raw_features ORDER BY d DESC LIMIT ?",
                (self.LOOKBACK_TRADING_DAYS,),
            ).fetchall()
            since = min(r[0] for r in day_rows) if day_rows else "1970-01-01"

            close_rows = conn.execute(
                "SELECT ts, close FROM raw_candles WHERE ts >= ? ORDER BY ts",
                (since + " 00:00:00",),
            ).fetchall()
            feat_rows = conn.execute(
                "SELECT ts, features FROM raw_features WHERE ts >= ? ORDER BY ts",
                (since + " 00:00:00",),
            ).fetchall()

        close_by_ts = {r[0]: float(r[1]) for r in close_rows if r[1]}

        feasibilities = []
        for ts, fj in feat_rows:
            close = close_by_ts.get(ts)
            if not close or close <= 0:
                continue
            try:
                fd = json.loads(fj)
            except Exception:
                continue
            atr = fd.get("atr")
            if atr is None or atr <= 0:
                continue
            thresh_pt = max(thresh_1m * max(close, 1.0), 1e-9)
            feasibilities.append(atr / thresh_pt)

        if len(feasibilities) < 100:
            raise ValueError(f"유효 표본 부족: {len(feasibilities)}")
        return feasibilities

    # ── DB 저장 ──────────────────────────────────────────────────
    def _save(self, today: str, r: dict):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO entry_horizon_log
                (date, current_b1, current_b2, recalc_b1, recalc_b2,
                 b1_delta_pct, b2_delta_pct, bucket_1m_pct, bucket_3m_pct,
                 bucket_5m_pct, alert_level, n_samples)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    today, r["current_b1"], r["current_b2"],
                    r["recalc_b1"], r["recalc_b2"],
                    r["b1_delta_pct"], r["b2_delta_pct"],
                    r["bucket_1m_pct"], r["bucket_3m_pct"], r["bucket_5m_pct"],
                    r["alert"], r["n_samples"],
                ),
            )
            conn.commit()

    # ── 로그 출력 ────────────────────────────────────────────────
    def _log_summary(self, r: dict, today: str):
        tag = ""
        if r["alert"] == "UPDATE":
            tag = " *** UPDATE 권고 (버킷 고착 조짐 또는 경계값 대폭 이탈)"
        elif r["alert"] == "WATCHLIST":
            tag = " * WATCHLIST"
        logger.info(
            "[EntryHorizonRecal] %s  경계=%.2f/%.2f  재계산=%.2f/%.2f  "
            "델타=%+.1f%%/%+.1f%%  버킷비중(1m/3m/5m)=%.1f%%/%.1f%%/%.1f%%  "
            "n=%d  [%s]%s",
            today, r["current_b1"], r["current_b2"], r["recalc_b1"], r["recalc_b2"],
            r["b1_delta_pct"], r["b2_delta_pct"],
            r["bucket_1m_pct"], r["bucket_3m_pct"], r["bucket_5m_pct"],
            r["n_samples"], r["alert"], tag,
        )

    # ── 최근 이력 조회 ───────────────────────────────────────────
    def recent_log(self, n_weeks: int = 4) -> List[dict]:
        """최근 n_weeks 주 기록 조회 (대시보드·검토용)."""
        cutoff = (
            datetime.date.today() - datetime.timedelta(weeks=n_weeks)
        ).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM entry_horizon_log WHERE date >= ? ORDER BY date DESC",
                (cutoff,),
            ).fetchall()
        cols = [
            "date", "current_b1", "current_b2", "recalc_b1", "recalc_b2",
            "b1_delta_pct", "b2_delta_pct", "bucket_1m_pct", "bucket_3m_pct",
            "bucket_5m_pct", "alert_level", "n_samples",
        ]
        return [dict(zip(cols, r)) for r in rows]
