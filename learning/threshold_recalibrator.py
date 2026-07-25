# learning/threshold_recalibrator.py — Phase A 롤링 임계값 재보정 모니터
"""
매주 금요일 15:40 daily_close() 내부에서 호출.

동작:
  1. raw_candles 전체로 호라이즌별 수익률 분포 재산출
  2. 33/67 분위수 기반 새 대칭 임계값 산출
  3. 현재 BASE로 FLAT 비율 계산 → 목표(34%) 대비 drift 측정
  4. 경보 수준 판단 및 threshold_monitor.db 저장

경보 트리거:
  WATCHLIST : |FLAT drift| >= 6%p  (목표 34% 에서 ±6%p 이상 이탈)
  UPDATE    : |threshold δ| >= 15%  (현재 BASE 대비 재산출값 ±15% 이상 변화)

UPDATE 경보 시 settings.HORIZON_THRESHOLDS_BASE 를 자동 교체하지 않음.
  → 사용자 확인 후 수동 반영 (임계값은 레이블 체계 전체에 영향)
  → 로그/DB에 권고값 기록하여 검토 근거 제공
"""
import datetime
import logging
import sqlite3
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("LEARNING")

FLAT_TARGET = 34.0        # 목표 FLAT 비율 (%)
FLAT_ALARM  = 6.0         # FLAT drift 경보 임계 (±%p)
DELTA_ALARM = 15.0        # threshold 변화율 경보 (±%)
ATR_RATIO_LO = 0.05       # ATR ratio 정상 하한
ATR_RATIO_HI = 0.15       # ATR ratio 정상 상한


class ThresholdRecalibrator:
    """Phase A 롤링 임계값 재보정 모니터."""

    # [P4] 재보정 참조 윈도우 — 거래일 수
    # 2026-07-03 확인: raw_candles 전체(11개월) 평균으로 재보정하면 최근 레짐(변동성 확대)이
    # 희석되어 recalc값이 오히려 현재 base보다 작게 나옴(반대 방향 UPDATE 경보, 6/12~6/26 3주
    # 연속). HORIZON_THRESHOLDS 수동 재보정(2026-07-03, 21거래일)과 동일 윈도우로 통일해
    # "최근 레짐 기준"이라는 재보정 취지에 맞춘다.
    LOOKBACK_TRADING_DAYS = 21
    # [376차] 주 1회, 휴장 등으로 특정 금요일 세션이 없었던 경우를 대비해
    # "마지막 실행 후 7일 이상 경과 시"로 재트리거 (atr_ceiling/entry_horizon
    # _recalibrator와 동일 패턴). 종전엔 "정확히 금요일"에만 run()을 호출해
    # 그 금요일 daily_close 자체가 안 돌면 해당 주가 통째로 누락됐다(07-17 공백).
    RUN_INTERVAL_CAL_DAYS = 7

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            from config.settings import DB_DIR
            import os
            db_path = os.path.join(DB_DIR, "threshold_monitor.db")
        self.db_path = db_path
        self._init_db()

    # ── 실행 간격 게이트 ─────────────────────────────────────────
    def _last_run_date(self) -> Optional[str]:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT MAX(date) FROM threshold_log").fetchone()
        return row[0] if row and row[0] else None

    def should_run(self, today: str) -> bool:
        last = self._last_run_date()
        if last is None:
            return True
        elapsed = (
            datetime.date.fromisoformat(today) - datetime.date.fromisoformat(last)
        ).days
        return elapsed >= self.RUN_INTERVAL_CAL_DAYS

    def run_if_due(self, today: Optional[str] = None) -> Dict[str, dict]:
        """간격 조건을 만족할 때만 run() 실행. 아니면 {}(스킵)."""
        if today is None:
            today = datetime.date.today().isoformat()
        if not self.should_run(today):
            logger.debug("[ThresholdRecal] 재실행 간격 미도달 — 스킵")
            return {}
        return self.run(today)

    # ── DB 초기화 ────────────────────────────────────────────────
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS threshold_log (
                    date            TEXT,
                    horizon         TEXT,
                    current_base    REAL,
                    recalc_sym      REAL,
                    recalc_down     REAL,
                    recalc_up       REAL,
                    flat_actual     REAL,
                    flat_target     REAL DEFAULT 34.0,
                    flat_drift      REAL,
                    threshold_delta REAL,
                    atr_p50         REAL,
                    atr_ratio       REAL,
                    alert_level     TEXT,
                    n_bars          INTEGER,
                    PRIMARY KEY (date, horizon)
                )
            """)
            conn.commit()

    # ── 메인 실행 ────────────────────────────────────────────────
    def run(self, today: Optional[str] = None) -> Dict[str, dict]:
        """
        호라이즌별 재보정 실행 후 결과 반환.

        Returns:
            {horizon: {"alert": "CLEAR"|"WATCHLIST"|"UPDATE", ...}}
        """
        from config.settings import (
            HORIZONS, HORIZON_THRESHOLDS_BASE, RAW_DATA_DB,
        )
        if today is None:
            today = datetime.date.today().isoformat()

        try:
            rets_by_horizon, atr_p50, price_avg = self._load_returns(RAW_DATA_DB, HORIZONS)
        except Exception as exc:
            logger.warning("[ThresholdRecal] 데이터 로드 실패: %s", exc)
            return {}

        results = {}
        rows = []

        for h, rets in rets_by_horizon.items():
            n = len(rets)
            if n < 100:
                logger.info("[ThresholdRecal] %s: 샘플 부족 (%d < 100), 건너뜀", h, n)
                continue

            current_base = HORIZON_THRESHOLDS_BASE.get(h, 0.0003)

            # 33/67 분위수
            sorted_rets = sorted(rets)
            p33 = sorted_rets[int(n * 0.33)]
            p67 = sorted_rets[int(n * 0.67)]
            recalc_down = p33
            recalc_up   = p67
            recalc_sym  = (abs(p33) + p67) / 2.0  # 대칭 단순화

            # FLAT 비율 (현재 BASE 기준)
            flat_cnt    = sum(1 for r in rets if -current_base <= r / 100.0 <= current_base)
            flat_actual = flat_cnt / n * 100.0
            flat_drift  = flat_actual - FLAT_TARGET

            # threshold delta (현재 BASE 대비 재산출 대칭값)
            if current_base > 0:
                delta_pct = (recalc_sym - current_base * 100.0) / (current_base * 100.0) * 100.0
            else:
                delta_pct = 0.0

            # ATR ratio (threshold / ATR_p50_ratio)
            atr_ratio = None
            if atr_p50 and price_avg and price_avg > 0 and atr_p50 > 0:
                atr_vol_ratio = atr_p50 / price_avg  # 무차원 변동성
                atr_ratio = round(current_base / atr_vol_ratio, 4) if atr_vol_ratio > 0 else None

            # 경보 수준
            alert = "CLEAR"
            if abs(flat_drift) >= FLAT_ALARM:
                alert = "WATCHLIST"
            if abs(delta_pct) >= DELTA_ALARM:
                alert = "UPDATE"

            # ATR ratio 이상 경고
            if atr_ratio is not None:
                if not (ATR_RATIO_LO <= atr_ratio <= ATR_RATIO_HI):
                    if alert == "CLEAR":
                        alert = "WATCHLIST"

            result = {
                "current_base":     round(current_base * 100.0, 5),
                "recalc_sym":       round(recalc_sym, 5),
                "recalc_down":      round(recalc_down, 5),
                "recalc_up":        round(recalc_up, 5),
                "flat_actual":      round(flat_actual, 1),
                "flat_drift":       round(flat_drift, 1),
                "threshold_delta":  round(delta_pct, 1),
                "atr_p50":          round(atr_p50, 3) if atr_p50 else None,
                "atr_ratio":        atr_ratio,
                "alert":            alert,
                "n_bars":           n,
            }
            results[h] = result
            rows.append((today, h, result))

        self._save(rows)
        self._log_summary(results, today)
        return results

    # ── 데이터 로드 ──────────────────────────────────────────────
    def _load_returns(
        self,
        raw_db: str,
        horizons: Dict[str, int],
    ) -> Tuple[Dict[str, List[float]], Optional[float], Optional[float]]:
        """
        raw_candles 최근 LOOKBACK_TRADING_DAYS 거래일에서 연속 1분봉 수익률 계산 후
        호라이즌별 리샘플링. [P4] 전체 이력 대신 최근 레짐만 반영 — 오래된 저변동성
        구간이 섞이면 recalc 임계값이 현재 변동성보다 작게 나와 반대 방향으로
        오판(threshold 축소 권고)할 수 있다.

        Returns:
            rets_by_horizon : {"1m": [ret%,...], "5m": [...], ...}
            atr_p50         : ATR 중앙값 (pt)
            price_avg       : 평균 close 가격
        """
        import json as _json

        with sqlite3.connect(raw_db, timeout=10) as conn:
            day_rows = conn.execute(
                "SELECT DISTINCT substr(ts,1,10) d FROM raw_candles ORDER BY d DESC "
                "LIMIT ?",
                (self.LOOKBACK_TRADING_DAYS,),
            ).fetchall()
            since = min(r[0] for r in day_rows) if day_rows else "1970-01-01"
            candle_rows = conn.execute(
                "SELECT ts, close FROM raw_candles WHERE ts >= ? ORDER BY ts",
                (since + " 00:00:00",),
            ).fetchall()
            feat_rows = conn.execute(
                "SELECT features FROM raw_features WHERE ts >= ? ORDER BY ts",
                (since + " 00:00:00",),
            ).fetchall()

        if len(candle_rows) < 200:
            raise ValueError(f"raw_candles 부족: {len(candle_rows)}")

        # 1분봉 연속 수익률 (갭 제거)
        closes = [(r[0], float(r[1])) for r in candle_rows]
        returns_1m = []
        price_sum = 0.0
        for i in range(1, len(closes)):
            t0, c0 = closes[i - 1]
            t1, c1 = closes[i]
            dt0 = datetime.datetime.strptime(t0, "%Y-%m-%d %H:%M:%S")
            dt1 = datetime.datetime.strptime(t1, "%Y-%m-%d %H:%M:%S")
            if (dt1 - dt0).total_seconds() == 60:
                returns_1m.append((t1, (c1 - c0) / c0 * 100.0))
                price_sum += c1
        price_avg = price_sum / len(returns_1m) if returns_1m else None

        # 호라이즌별 수익률: h분봉 → h분 간격 연속 봉 수익률
        ts_map = {r[0]: float(r[1]) for r in candle_rows}
        rets_by_horizon: Dict[str, List[float]] = {}
        for h_name, h_min in horizons.items():
            rets = []
            td = datetime.timedelta(minutes=h_min)
            seen_ts = sorted(ts_map.keys())
            for i in range(len(seen_ts)):
                t0 = seen_ts[i]
                t1 = (
                    datetime.datetime.strptime(t0, "%Y-%m-%d %H:%M:%S") + td
                ).strftime("%Y-%m-%d %H:%M:%S")
                c0 = ts_map.get(t0)
                c1 = ts_map.get(t1)
                if c0 and c1 and c0 > 0:
                    ret = (c1 - c0) / c0 * 100.0
                    if abs(ret) <= 5.0:   # 이상치(갭·데이터오류) 제거
                        rets.append(ret)
            rets_by_horizon[h_name] = rets

        # ATR 중앙값
        atrs = []
        for r in feat_rows:
            try:
                d = _json.loads(r[0])
                a = float(d.get("atr", 0))
                if a > 0:
                    atrs.append(a)
            except Exception:
                pass
        atrs.sort()
        atr_p50 = atrs[len(atrs) // 2] if atrs else None

        return rets_by_horizon, atr_p50, price_avg

    # ── DB 저장 ──────────────────────────────────────────────────
    def _save(self, rows: list):
        if not rows:
            return
        with sqlite3.connect(self.db_path) as conn:
            for today, h, r in rows:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO threshold_log
                    (date, horizon, current_base, recalc_sym, recalc_down, recalc_up,
                     flat_actual, flat_target, flat_drift, threshold_delta,
                     atr_p50, atr_ratio, alert_level, n_bars)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """,
                    (
                        today, h,
                        r["current_base"], r["recalc_sym"],
                        r["recalc_down"],  r["recalc_up"],
                        r["flat_actual"],  FLAT_TARGET,
                        r["flat_drift"],   r["threshold_delta"],
                        r["atr_p50"],      r["atr_ratio"],
                        r["alert"],        r["n_bars"],
                    ),
                )
            conn.commit()

    # ── 로그 출력 ────────────────────────────────────────────────
    def _log_summary(self, results: dict, today: str):
        if not results:
            return
        lines = [f"[ThresholdRecal] {today} 재보정 결과"]
        for h in ["1m", "3m", "5m", "10m", "15m", "30m"]:
            r = results.get(h)
            if not r:
                continue
            tag = ""
            if r["alert"] == "UPDATE":
                tag = " *** UPDATE 권고"
            elif r["alert"] == "WATCHLIST":
                tag = " * WATCHLIST"
            lines.append(
                f"  {h:4s} base={r['current_base']:.4f}%  "
                f"recalc={r['recalc_sym']:.4f}%  "
                f"delta={r['threshold_delta']:+.1f}%  "
                f"FLAT={r['flat_actual']:.1f}%(drift={r['flat_drift']:+.1f}%p)  "
                f"ATR_ratio={r['atr_ratio']}  "
                f"[{r['alert']}]{tag}"
            )
        logger.info("\n".join(lines))

    # ── 최근 이력 조회 ───────────────────────────────────────────
    def recent_log(self, n_weeks: int = 4) -> List[dict]:
        """최근 n_weeks 주 기록 조회 (대시보드·검토용)."""
        cutoff = (
            datetime.date.today() - datetime.timedelta(weeks=n_weeks)
        ).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM threshold_log WHERE date >= ? ORDER BY date DESC, horizon",
                (cutoff,),
            ).fetchall()
        cols = [
            "date", "horizon", "current_base", "recalc_sym",
            "recalc_down", "recalc_up", "flat_actual", "flat_target",
            "flat_drift", "threshold_delta", "atr_p50", "atr_ratio",
            "alert_level", "n_bars",
        ]
        return [dict(zip(cols, r)) for r in rows]
