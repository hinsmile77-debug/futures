# learning/atr_ceiling_recalibrator.py — ATR 게이트 상/하한 재보정 모니터
"""
매 1~2주(금요일 EOD, run_if_due()가 내부적으로 재실행 간격을 관리)
daily_close() 내부에서 호출.

배경(303차): ATR 진입 게이트의 정적 하한(ATR_MAX_ENTRY)·적응형 상한의 절대
캡(ATR_ADAPTIVE_MAX_CEILING)은 273차에 수동으로 캘리브레이션된 값이다.
장기(1~2주) 롤링으로 캡 자체를 완전 자동화하면 변동성 "상승 초입"에 과거 낮은
레벨에 발목 잡혀 오히려 차단율이 커지는 역효과가 시뮬레이션으로 확인됐다
(dev_memory 07-08 딥다이브 참고). 그렇다고 정적값을 영구 방치하면 273차가
풀려던 "시대 뒤처짐" 문제가 재발한다.

절충: 자동으로 값을 바꾸지 않고, 최근 N거래일(만기 전후 제외) ATR 분포로
"제안값"만 산출해 DB에 기록 + Slack 알림을 보낸다. 실제 반영은 사용자가
config/settings.py를 검토 후 수동으로 수정한다 — 알파 리서치 봇 자동 통합
금지(CLAUDE.md 절대원칙 §6)와 동일한 "제안 → 사람 승인" 원칙.

동작:
  1. raw_features 최근 LOOKBACK_TRADING_DAYS 거래일 로드 (만기 D-2~D+1 제외 —
     그 구간은 ATR_EXPIRY_CEILING_MULT 캘린더 예외가 별도로 처리하므로 일반
     재보정 통계에 섞이면 만기 스파이크가 이중으로 반영됨)
  2. 일별 ATR 평균의 중앙값 → suggested_floor (ATR_MAX_ENTRY 제안)
  3. 전체 분봉 ATR의 p95 → suggested_ceiling (ATR_ADAPTIVE_MAX_CEILING 제안)
  4. 현재 설정값 대비 변화율로 CLEAR/WATCHLIST/UPDATE 경보 판정
  5. atr_ceiling_monitor.db 저장 + WATCHLIST 이상이면 Slack 알림
"""
import datetime
import logging
import sqlite3
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("LEARNING")

FLOOR_DELTA_WATCHLIST   = 15.0   # 제안 floor 변화율 ±%p — 관찰 등록
FLOOR_DELTA_UPDATE      = 30.0   # 제안 floor 변화율 ±%p — 재조정 권고
CEILING_DELTA_WATCHLIST = 15.0
CEILING_DELTA_UPDATE    = 30.0

MIN_TRADING_DAYS = 5   # 만기 제외 후 이 미만이면 표본 부족으로 보류


class ATRCeilingRecalibrator:
    """ATR 게이트 상/하한 재보정 제안 모니터 (자동 반영 없음, 제안만)."""

    LOOKBACK_TRADING_DAYS  = 15   # 재보정 참조 윈도우 (약 3주 거래일)
    RUN_INTERVAL_CAL_DAYS  = 10   # 마지막 실행 이후 이 이상 지나야 재실행 (약 1~2주)

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            from config.settings import DB_DIR
            import os
            db_path = os.path.join(DB_DIR, "atr_ceiling_monitor.db")
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS atr_ceiling_log (
                    date               TEXT PRIMARY KEY,
                    current_floor      REAL,
                    current_ceiling    REAL,
                    suggested_floor    REAL,
                    suggested_ceiling  REAL,
                    floor_delta_pct    REAL,
                    ceiling_delta_pct  REAL,
                    atr_daily_p50      REAL,
                    atr_bar_p95        REAL,
                    n_days             INTEGER,
                    n_bars             INTEGER,
                    alert_level        TEXT
                )
            """)
            conn.commit()

    # ── 실행 간격 게이트 ─────────────────────────────────────────
    def _last_run_date(self) -> Optional[str]:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT MAX(date) FROM atr_ceiling_log"
            ).fetchone()
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
            logger.debug("[ATRCeilingRecal] 재실행 간격 미도달 — 스킵")
            return None
        return self.run(today)

    # ── 메인 실행 ────────────────────────────────────────────────
    def run(self, today: Optional[str] = None) -> Optional[dict]:
        from config.settings import ATR_MAX_ENTRY, ATR_ADAPTIVE_MAX_CEILING, RAW_DATA_DB

        if today is None:
            today = datetime.date.today().isoformat()

        try:
            daily_means, all_atrs, n_days, n_bars = self._load_atr(RAW_DATA_DB)
        except Exception as exc:
            logger.warning("[ATRCeilingRecal] 데이터 로드 실패: %s", exc)
            return None

        if n_days < MIN_TRADING_DAYS or n_bars < 100:
            logger.info(
                "[ATRCeilingRecal] 만기 제외 후 표본 부족 (%d일/%d봉 < 최소 %d일) — 보류",
                n_days, n_bars, MIN_TRADING_DAYS,
            )
            return None

        daily_means_sorted = sorted(daily_means)
        atr_daily_p50 = daily_means_sorted[len(daily_means_sorted) // 2]

        atrs_sorted = sorted(all_atrs)
        atr_bar_p95 = atrs_sorted[int(len(atrs_sorted) * 0.95)]

        suggested_floor = round(atr_daily_p50 * 2) / 2.0     # 0.5pt 단위 반올림
        suggested_ceiling = round(atr_bar_p95 * 2) / 2.0

        floor_delta_pct = (
            (suggested_floor - ATR_MAX_ENTRY) / ATR_MAX_ENTRY * 100.0
            if ATR_MAX_ENTRY else 0.0
        )
        ceiling_delta_pct = (
            (suggested_ceiling - ATR_ADAPTIVE_MAX_CEILING) / ATR_ADAPTIVE_MAX_CEILING * 100.0
            if ATR_ADAPTIVE_MAX_CEILING else 0.0
        )

        alert = "CLEAR"
        if abs(floor_delta_pct) >= FLOOR_DELTA_WATCHLIST or abs(ceiling_delta_pct) >= CEILING_DELTA_WATCHLIST:
            alert = "WATCHLIST"
        if abs(floor_delta_pct) >= FLOOR_DELTA_UPDATE or abs(ceiling_delta_pct) >= CEILING_DELTA_UPDATE:
            alert = "UPDATE"

        result = {
            "date":               today,
            "current_floor":      ATR_MAX_ENTRY,
            "current_ceiling":    ATR_ADAPTIVE_MAX_CEILING,
            "suggested_floor":    suggested_floor,
            "suggested_ceiling":  suggested_ceiling,
            "floor_delta_pct":    round(floor_delta_pct, 1),
            "ceiling_delta_pct":  round(ceiling_delta_pct, 1),
            "atr_daily_p50":      round(atr_daily_p50, 3),
            "atr_bar_p95":        round(atr_bar_p95, 3),
            "n_days":             n_days,
            "n_bars":             n_bars,
            "alert":              alert,
        }
        self._save(result)
        self._log_summary(result)
        if alert != "CLEAR":
            self._notify(result)
        return result

    # ── 데이터 로드 (만기 D-2~D+1 제외) ───────────────────────────
    def _load_atr(self, raw_db: str) -> Tuple[List[float], List[float], int, int]:
        import json as _json
        from features.technical.expiry import is_near_monthly_expiry
        from config.settings import (
            ATR_EXPIRY_CEILING_DAYS_BEFORE, ATR_EXPIRY_CEILING_DAYS_AFTER,
        )

        with sqlite3.connect(raw_db, timeout=10) as conn:
            day_rows = conn.execute(
                "SELECT DISTINCT substr(ts,1,10) d FROM raw_features ORDER BY d DESC "
                "LIMIT ?",
                (self.LOOKBACK_TRADING_DAYS,),
            ).fetchall()
            days = [r[0] for r in day_rows]
            if not days:
                return [], [], 0, 0

            # 만기 전후 제외 (ATR_EXPIRY_CEILING_MULT 캘린더 예외가 별도로 처리)
            keep_days = [
                d for d in days
                if not is_near_monthly_expiry(
                    datetime.datetime.strptime(d, "%Y-%m-%d"),
                    ATR_EXPIRY_CEILING_DAYS_BEFORE, ATR_EXPIRY_CEILING_DAYS_AFTER,
                )
            ]
            if not keep_days:
                return [], [], 0, 0

            since = min(keep_days)
            feat_rows = conn.execute(
                "SELECT ts, features FROM raw_features WHERE ts >= ? ORDER BY ts",
                (since + " 00:00:00",),
            ).fetchall()

        keep_set = set(keep_days)
        by_day: Dict[str, List[float]] = {}
        for ts, feat in feat_rows:
            day = ts[:10]
            if day not in keep_set:
                continue
            try:
                a = float(_json.loads(feat).get("atr", 0))
            except Exception:
                continue
            if a > 0:
                by_day.setdefault(day, []).append(a)

        all_atrs = [a for vals in by_day.values() for a in vals]
        daily_means = [sum(v) / len(v) for v in by_day.values() if v]
        return daily_means, all_atrs, len(by_day), len(all_atrs)

    # ── 저장/로그/알림 ───────────────────────────────────────────
    def _save(self, r: dict):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO atr_ceiling_log
                (date, current_floor, current_ceiling, suggested_floor, suggested_ceiling,
                 floor_delta_pct, ceiling_delta_pct, atr_daily_p50, atr_bar_p95,
                 n_days, n_bars, alert_level)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    r["date"], r["current_floor"], r["current_ceiling"],
                    r["suggested_floor"], r["suggested_ceiling"],
                    r["floor_delta_pct"], r["ceiling_delta_pct"],
                    r["atr_daily_p50"], r["atr_bar_p95"],
                    r["n_days"], r["n_bars"], r["alert"],
                ),
            )
            conn.commit()

    def _log_summary(self, r: dict):
        tag = ""
        if r["alert"] == "UPDATE":
            tag = " *** UPDATE 권고"
        elif r["alert"] == "WATCHLIST":
            tag = " * WATCHLIST"
        logger.info(
            "[ATRCeilingRecal] %s (만기제외 %d일/%d봉) "
            "floor: 현재=%.1f 제안=%.1f(%+.1f%%)  "
            "ceiling: 현재=%.1f 제안=%.1f(%+.1f%%)  [%s]%s",
            r["date"], r["n_days"], r["n_bars"],
            r["current_floor"], r["suggested_floor"], r["floor_delta_pct"],
            r["current_ceiling"], r["suggested_ceiling"], r["ceiling_delta_pct"],
            r["alert"], tag,
        )

    def _notify(self, r: dict):
        try:
            from utils.notify import notify
            notify(
                f"[ATR게이트 재보정 제안] {r['alert']} — 사람 검토 필요\n"
                f"최근 {r['n_days']}거래일(만기 전후 제외) 기준:\n"
                f"  하한(ATR_MAX_ENTRY): {r['current_floor']}pt → 제안 {r['suggested_floor']}pt "
                f"({r['floor_delta_pct']:+.0f}%)\n"
                f"  상한(ATR_ADAPTIVE_MAX_CEILING): {r['current_ceiling']}pt → 제안 "
                f"{r['suggested_ceiling']}pt ({r['ceiling_delta_pct']:+.0f}%)\n"
                f"자동 반영 안 됨 — config/settings.py 수동 검토 후 반영 여부 결정 "
                f"(atr_ceiling_monitor.db 상세 로그 참조)",
                level="WARNING",
            )
        except Exception as exc:
            logger.debug("[ATRCeilingRecal] Slack 알림 실패(무해): %s", exc)

    # ── 최근 이력 조회 (대시보드·검토용) ───────────────────────────
    def recent_log(self, n_weeks: int = 8) -> List[dict]:
        cutoff = (
            datetime.date.today() - datetime.timedelta(weeks=n_weeks)
        ).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM atr_ceiling_log WHERE date >= ? ORDER BY date DESC",
                (cutoff,),
            ).fetchall()
        cols = [
            "date", "current_floor", "current_ceiling", "suggested_floor",
            "suggested_ceiling", "floor_delta_pct", "ceiling_delta_pct",
            "atr_daily_p50", "atr_bar_p95", "n_days", "n_bars", "alert_level",
        ]
        return [dict(zip(cols, r)) for r in rows]
