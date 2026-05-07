# config/strategy_registry.py — 전략 버전 레지스트리
"""
전략 버전 이력을 SQLite에 영속 저장하고 조회하는 레지스트리.

목적:
  - 파라미터 교체·승격·롤백 이력 완전 보존
  - 각 버전의 Backtest / WFA / Sim / Live 성과 단계별 추적
  - 기대값 대비 실전 성과 자동 판정 (OUTPERFORM / NORMAL / UNDERPERFORM)
  - 대시보드 🧭 전략 운용현황 탭의 데이터 공급원

DB 테이블:
  strategy_versions       — 전략 버전 메타
  strategy_stage_results  — 단계별 성과 (BT/WFA/SIM/LIVE)
  strategy_param_changes  — 파라미터 변경 명세
  strategy_live_snapshots — 일별 실전 성과 스냅샷
  strategy_regime_matrix  — 레짐×시간대 기대값 매트릭스

사용 예:
  reg = StrategyRegistry()
  reg.register_version("v1.3", changed_params, wfa_metrics, note="월간 최적화")
  reg.record_live_snapshot("v1.3", live_metrics)
  current = reg.get_current_version()
  verdict = reg.get_verdict("v1.3")
"""
from __future__ import annotations

import json
import logging
import math
import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ── 경로 설정 ─────────────────────────────────────────────────────────────
_HERE     = os.path.dirname(os.path.abspath(__file__))
_DB_ROOT  = os.path.join(os.path.dirname(_HERE), "data", "db")
REGISTRY_DB = os.path.join(_DB_ROOT, "strategy_registry.db")


# ── 판정 상수 ─────────────────────────────────────────────────────────────
VERDICT_OUTPERFORM   = "OUTPERFORM"    # 기대값 상회
VERDICT_NORMAL       = "NORMAL"        # 기대값 부합
VERDICT_UNDERPERFORM = "UNDERPERFORM"  # 기대값 하회
VERDICT_INSUFFICIENT = "INSUFFICIENT"  # 데이터 부족 (< 5 거래일)

# 판정 임계값: WFA 기준 대비 Live 비교
# OUTPERFORM: sharpe_delta >= +0.15 AND mdd_delta <= -0.01
# NORMAL    : sharpe_delta >= -0.20 AND mdd_delta <= +0.03
# else      : UNDERPERFORM
_OUTPERFORM_SHARPE_DELTA = 0.15
_NORMAL_SHARPE_DELTA     = -0.20
_OUTPERFORM_MDD_DELTA    = -0.01   # MDD 개선 (음수가 개선)
_NORMAL_MDD_DELTA        = 0.03    # MDD 최대 악화 허용


# ─────────────────────────────────────────────────────────────────────────
class StrategyRegistry:
    """
    전략 버전 이력 관리 및 성과 판정 레지스트리.

    Thread-safety: 단일 프로세스 (PyQt5 메인 스레드) 전용.
    """

    def __init__(self, db_path: str = REGISTRY_DB):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._db = db_path
        self._init_db()
        logger.info("[StrategyRegistry] DB: %s", db_path)

    # ─── DB 초기화 ───────────────────────────────────────────────────────
    def _init_db(self) -> None:
        with self._conn() as con:
            cur = con.cursor()
            cur.executescript("""
            CREATE TABLE IF NOT EXISTS strategy_versions (
                version         TEXT PRIMARY KEY,
                activated_at    TEXT NOT NULL,
                deactivated_at  TEXT,
                previous_version TEXT,
                is_current      INTEGER DEFAULT 0,
                note            TEXT,
                created_at      TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS strategy_stage_results (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                version     TEXT NOT NULL,
                stage       TEXT NOT NULL,   -- BACKTEST / WFA / SIM / LIVE
                evaluated_at TEXT NOT NULL,
                sharpe      REAL,
                mdd_pct     REAL,
                win_rate    REAL,
                profit_factor REAL,
                calmar      REAL,
                total_trades INTEGER,
                raw_json    TEXT,
                FOREIGN KEY(version) REFERENCES strategy_versions(version)
            );

            CREATE TABLE IF NOT EXISTS strategy_param_changes (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                version     TEXT NOT NULL,
                param_name  TEXT NOT NULL,
                val_from    TEXT,
                val_to      TEXT,
                FOREIGN KEY(version) REFERENCES strategy_versions(version)
            );

            CREATE TABLE IF NOT EXISTS strategy_live_snapshots (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                version     TEXT NOT NULL,
                snapshot_date TEXT NOT NULL,
                sharpe      REAL,
                mdd_pct     REAL,
                win_rate    REAL,
                profit_factor REAL,
                calmar      REAL,
                total_trades INTEGER,
                daily_pnl   REAL,
                regime      TEXT,
                raw_json    TEXT,
                FOREIGN KEY(version) REFERENCES strategy_versions(version)
            );

            CREATE TABLE IF NOT EXISTS strategy_regime_matrix (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                version      TEXT NOT NULL,
                snapshot_date TEXT NOT NULL,
                regime       TEXT NOT NULL,  -- RISK_ON / NEUTRAL / RISK_OFF
                time_slot    TEXT NOT NULL,  -- OPEN_VOL / STABLE_TREND / LUNCH / CLOSE_VOL
                trade_count  INTEGER,
                win_rate     REAL,
                avg_pnl      REAL,
                expectancy   REAL,
                FOREIGN KEY(version) REFERENCES strategy_versions(version)
            );

            CREATE TABLE IF NOT EXISTS strategy_events (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                version     TEXT,             -- NULL 허용 (시스템 이벤트)
                event_type  TEXT NOT NULL,    -- VERSION_REGISTERED / SHADOW_START / HOTSWAP_APPROVED / HOTSWAP_DENIED / ROLLBACK / REPLACE_CANDIDATE / WATCH
                event_at    TEXT NOT NULL,
                message     TEXT,
                note        TEXT
            );
            """)
            con.commit()

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db)

    # ─── 버전 등록 ───────────────────────────────────────────────────────
    def register_version(
        self,
        version:        str,
        changed_params: Dict[str, Dict[str, Any]],
        wfa_metrics:    Dict[str, Any],
        note:           str = "",
        bt_metrics:     Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        새 전략 버전 등록. 현재 버전 비활성화 후 신규 버전을 활성화.

        Args:
            version:        버전 문자열 (예: "v1.3")
            changed_params: {"entry_conf_neutral": {"from": 0.58, "to": 0.60}, ...}
            wfa_metrics:    WFA 결과 {"sharpe": 1.63, "mdd_pct": 0.125, ...}
            note:           변경 사유
            bt_metrics:     백테스트 결과 (선택)
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._conn() as con:
            cur = con.cursor()

            # 현재 버전 조회
            cur.execute("SELECT version FROM strategy_versions WHERE is_current=1")
            row = cur.fetchone()
            prev_ver = row[0] if row else None

            # 직전 버전 비활성화
            if prev_ver:
                cur.execute(
                    "UPDATE strategy_versions SET is_current=0, deactivated_at=? WHERE version=?",
                    (now, prev_ver),
                )

            # 신규 버전 등록
            cur.execute(
                """INSERT OR REPLACE INTO strategy_versions
                   (version, activated_at, previous_version, is_current, note, created_at)
                   VALUES (?,?,?,1,?,?)""",
                (version, now, prev_ver, note, now),
            )

            # 파라미터 변경 기록
            for pname, delta in changed_params.items():
                cur.execute(
                    """INSERT INTO strategy_param_changes
                       (version, param_name, val_from, val_to)
                       VALUES (?,?,?,?)""",
                    (version, pname,
                     str(delta.get("from", "")), str(delta.get("to", ""))),
                )

            # WFA 결과 기록
            self._insert_stage_result(cur, version, "WFA", now, wfa_metrics)

            # 백테스트 결과 기록 (있으면)
            if bt_metrics:
                self._insert_stage_result(cur, version, "BACKTEST", now, bt_metrics)

            con.commit()

        logger.info(
            "[Registry] 버전 등록: %s (이전: %s) | WFA Sharpe=%.2f MDD=%.1f%%",
            version, prev_ver or "-",
            wfa_metrics.get("sharpe", 0),
            abs(wfa_metrics.get("mdd_pct", 0)) * 100,
        )
        self.log_event(
            event_type = "VERSION_REGISTERED",
            message    = "WFA Sharpe=%.2f MDD=%.1f%% %s" % (
                wfa_metrics.get("sharpe", 0),
                abs(wfa_metrics.get("mdd_pct", 0)) * 100,
                note or "",
            ),
            version = version,
        )

    # ─── 운영 이벤트 로그 ────────────────────────────────────────────────────
    def log_event(
        self,
        event_type: str,
        message:    str = "",
        note:       str = "",
        version:    Optional[str] = None,
    ) -> None:
        """
        전략 운영 이벤트를 strategy_events 테이블에 기록.

        Args:
            event_type : VERSION_REGISTERED / SHADOW_START / HOTSWAP_APPROVED /
                         HOTSWAP_DENIED / ROLLBACK / REPLACE_CANDIDATE / WATCH
            message    : 이벤트 설명
            note       : 추가 메모 (사유·리스크 등)
            version    : 연관 전략 버전 (없으면 None)
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with self._conn() as con:
                con.execute(
                    "INSERT INTO strategy_events (version, event_type, event_at, message, note)"
                    " VALUES (?,?,?,?,?)",
                    (version, event_type, now, message, note),
                )
                con.commit()
        except Exception as e:
            logger.warning("[Registry] log_event 실패: %s", e)

    def get_event_log(
        self,
        version: Optional[str] = None,
        limit:   int = 50,
    ) -> List[Dict[str, Any]]:
        """
        이벤트 로그 조회 (최신 순).

        Args:
            version : 특정 버전 필터 (None=전체)
            limit   : 최대 반환 행 수

        Returns:
            [{"id", "version", "event_type", "event_at", "message", "note"}, ...]
        """
        try:
            with self._conn() as con:
                con.row_factory = sqlite3.Row
                cur = con.cursor()
                if version:
                    cur.execute(
                        "SELECT * FROM strategy_events WHERE version=?"
                        " ORDER BY id DESC LIMIT ?",
                        (version, limit),
                    )
                else:
                    cur.execute(
                        "SELECT * FROM strategy_events ORDER BY id DESC LIMIT ?",
                        (limit,),
                    )
                return [dict(r) for r in cur.fetchall()]
        except Exception as e:
            logger.warning("[Registry] get_event_log 실패: %s", e)
            return []

    def record_stage_result(
        self,
        version:  str,
        stage:    str,
        metrics:  Dict[str, Any],
    ) -> None:
        """
        단계별 성과 기록 (BACKTEST / WFA / SIM / LIVE).

        Args:
            version: 버전 문자열
            stage:   "BACKTEST" | "WFA" | "SIM" | "LIVE"
            metrics: 성과 딕셔너리
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._conn() as con:
            cur = con.cursor()
            self._insert_stage_result(cur, version, stage, now, metrics)
            con.commit()

    def record_live_snapshot(
        self,
        version:  str,
        metrics:  Dict[str, Any],
        regime:   str = "",
    ) -> None:
        """
        일별 실전 성과 스냅샷 저장.

        Args:
            version: 활성 전략 버전
            metrics: 성과 딕셔너리 (sharpe, mdd_pct, win_rate, profit_factor, ...)
            regime:  당일 주요 레짐 (선택)
        """
        today = datetime.now().strftime("%Y-%m-%d")
        with self._conn() as con:
            cur = con.cursor()
            # UPSERT: 당일 같은 버전 중복 방지
            cur.execute(
                "DELETE FROM strategy_live_snapshots WHERE version=? AND snapshot_date=?",
                (version, today),
            )
            cur.execute(
                """INSERT INTO strategy_live_snapshots
                   (version, snapshot_date, sharpe, mdd_pct, win_rate,
                    profit_factor, calmar, total_trades, daily_pnl, regime, raw_json)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    version, today,
                    metrics.get("sharpe"),
                    metrics.get("mdd_pct"),
                    metrics.get("win_rate"),
                    metrics.get("profit_factor"),
                    metrics.get("calmar"),
                    metrics.get("total_trades"),
                    metrics.get("daily_pnl"),
                    regime,
                    json.dumps(metrics, ensure_ascii=False),
                ),
            )
            con.commit()

    def record_regime_matrix(
        self,
        version:     str,
        matrix_rows: List[Dict[str, Any]],
    ) -> None:
        """
        레짐×시간대 기대값 매트릭스 저장.

        Args:
            matrix_rows: [
              {"regime": "NEUTRAL", "time_slot": "STABLE_TREND",
               "trade_count": 12, "win_rate": 0.58, "avg_pnl": 3200, "expectancy": 1856},
              ...
            ]
        """
        today = datetime.now().strftime("%Y-%m-%d")
        with self._conn() as con:
            cur = con.cursor()
            # 당일 기존 레코드 삭제 후 재입력
            cur.execute(
                "DELETE FROM strategy_regime_matrix WHERE version=? AND snapshot_date=?",
                (version, today),
            )
            for row in matrix_rows:
                cur.execute(
                    """INSERT INTO strategy_regime_matrix
                       (version, snapshot_date, regime, time_slot,
                        trade_count, win_rate, avg_pnl, expectancy)
                       VALUES (?,?,?,?,?,?,?,?)""",
                    (
                        version, today,
                        row.get("regime", ""),
                        row.get("time_slot", ""),
                        row.get("trade_count", 0),
                        row.get("win_rate", 0.0),
                        row.get("avg_pnl", 0.0),
                        row.get("expectancy", 0.0),
                    ),
                )
            con.commit()

    # ─── 조회 ────────────────────────────────────────────────────────────
    def get_current_version(self) -> Optional[Dict[str, Any]]:
        """현재 활성 버전 전체 정보 조회."""
        with self._conn() as con:
            cur = con.cursor()
            cur.execute(
                "SELECT version, activated_at, previous_version, note "
                "FROM strategy_versions WHERE is_current=1"
            )
            row = cur.fetchone()
            if not row:
                return None
            ver, activated_at, prev_ver, note = row

            stages   = self._get_stage_results(cur, ver)
            params   = self._get_param_changes(cur, ver)
            live_snap = self._get_latest_live_snapshot(cur, ver)
            live_days = self._get_live_days(cur, ver)

        # 롤링 지표 자동 계산 — daily_pnl 누적에서 실 Sharpe/MDD 채우기
        # (단일 스냅샷에는 sharpe가 없으므로 롤링 계산으로 대체)
        rolling = self.get_rolling_metrics(ver, days=20)
        if rolling:
            if live_snap is None:
                live_snap = rolling
            elif live_snap.get("sharpe") is None:
                # 롤링 지표로 누락 필드 보완 (existing 값 우선)
                for k, v in rolling.items():
                    if live_snap.get(k) is None:
                        live_snap[k] = v

        verdict = self._compute_verdict(stages, live_snap)

        return {
                "version":          ver,
                "activated_at":     activated_at,
                "previous_version": prev_ver,
                "note":             note,
                "stages":           stages,
                "changed_params":   params,
                "live_snapshot":    live_snap,
                "verdict":          verdict,
                "live_days":        live_days,
            }

    def get_version(self, version: str) -> Optional[Dict[str, Any]]:
        """특정 버전 정보 조회."""
        with self._conn() as con:
            cur = con.cursor()
            cur.execute(
                "SELECT version, activated_at, deactivated_at, previous_version, note "
                "FROM strategy_versions WHERE version=?",
                (version,),
            )
            row = cur.fetchone()
            if not row:
                return None
            ver, activated_at, deactivated_at, prev_ver, note = row
            stages    = self._get_stage_results(cur, ver)
            params    = self._get_param_changes(cur, ver)
            live_snap = self._get_latest_live_snapshot(cur, ver)
            live_days = self._get_live_days(cur, ver)

        rolling = self.get_rolling_metrics(ver, days=20)
        if rolling:
            if live_snap is None:
                live_snap = rolling
            elif live_snap.get("sharpe") is None:
                for k, v in rolling.items():
                    if live_snap.get(k) is None:
                        live_snap[k] = v

        verdict = self._compute_verdict(stages, live_snap)
        return {
                "version":          ver,
                "activated_at":     activated_at,
                "deactivated_at":   deactivated_at,
                "previous_version": prev_ver,
                "note":             note,
                "stages":           stages,
                "changed_params":   params,
                "live_snapshot":    live_snap,
                "verdict":          verdict,
                "live_days":        live_days,
            }

    def get_all_versions(self) -> List[Dict[str, Any]]:
        """모든 버전 목록 (최신순 정렬)."""
        with self._conn() as con:
            cur = con.cursor()
            cur.execute(
                "SELECT version FROM strategy_versions ORDER BY activated_at DESC"
            )
            versions = [row[0] for row in cur.fetchall()]

        result = []
        for ver in versions:
            info = self.get_version(ver)
            if info:
                result.append(info)
        return result

    def get_live_history(
        self, version: str, days: int = 30
    ) -> List[Dict[str, Any]]:
        """특정 버전의 일별 실전 성과 이력 (최신 N일)."""
        with self._conn() as con:
            cur = con.cursor()
            cur.execute(
                """SELECT snapshot_date, sharpe, mdd_pct, win_rate,
                          profit_factor, calmar, total_trades, daily_pnl, regime
                   FROM strategy_live_snapshots
                   WHERE version=?
                   ORDER BY snapshot_date DESC LIMIT ?""",
                (version, days),
            )
            rows = cur.fetchall()
        return [
            {
                "date": r[0], "sharpe": r[1], "mdd_pct": r[2],
                "win_rate": r[3], "profit_factor": r[4], "calmar": r[5],
                "total_trades": r[6], "daily_pnl": r[7], "regime": r[8],
            }
            for r in rows
        ]

    def get_regime_matrix(self, version: str) -> List[Dict[str, Any]]:
        """최신 레짐×시간대 기대값 매트릭스 조회."""
        with self._conn() as con:
            cur = con.cursor()
            cur.execute(
                """SELECT regime, time_slot, trade_count, win_rate, avg_pnl, expectancy
                   FROM strategy_regime_matrix
                   WHERE version=?
                   ORDER BY snapshot_date DESC""",
                (version,),
            )
            rows = cur.fetchall()
        seen = set()
        result = []
        for r in rows:
            key = (r[0], r[1])
            if key not in seen:
                seen.add(key)
                result.append({
                    "regime": r[0], "time_slot": r[1],
                    "trade_count": r[2], "win_rate": r[3],
                    "avg_pnl": r[4], "expectancy": r[5],
                })
        return result

    def get_verdict(self, version: str) -> str:
        """특정 버전의 기대값 대비 판정."""
        info = self.get_version(version)
        if not info:
            return VERDICT_INSUFFICIENT
        return info["verdict"]

    def get_rolling_metrics(self, version: str, days: int = 20) -> Dict[str, Any]:
        """
        최근 N일 daily_pnl 스냅샷에서 롤링 Sharpe·MDD·WR·PF 계산.
        scipy 없이 순수 Python으로 구현 (3.7 32-bit 호환).

        Returns:
            {
              sharpe, mdd_pct, win_rate, profit_factor, total_trades,
              days, daily_pnl_list (chronological), mean_pnl, std_pnl, cum_pnl
            }
            데이터 부족 시 빈 dict 반환.
        """
        history = self.get_live_history(version, days)
        if not history:
            return {}

        # get_live_history는 DESC 반환 → 시간순 역전
        chron = list(reversed(history))
        pnls  = [r["daily_pnl"] for r in chron if r.get("daily_pnl") is not None]

        if len(pnls) < 2:
            return {"days": len(pnls), "daily_pnl_list": pnls}

        n        = len(pnls)
        mean_pnl = sum(pnls) / n
        var      = sum((x - mean_pnl) ** 2 for x in pnls) / max(n - 1, 1)
        std_pnl  = math.sqrt(var) if var > 0 else 1.0

        # 연율화 Sharpe (risk-free = 0, 일별 KRW PnL 기준)
        sharpe = mean_pnl / std_pnl * math.sqrt(252)

        # 누적 PnL 기반 MDD
        cum = 0.0
        peak = 0.0
        mdd_krw = 0.0
        for p in pnls:
            cum  += p
            if cum > peak:
                peak = cum
            dd = peak - cum
            if dd > mdd_krw:
                mdd_krw = dd
        mdd_pct = mdd_krw / abs(peak) if abs(peak) > 0 else 0.0

        # 승률 · Profit Factor
        wins       = sum(1 for p in pnls if p > 0)
        win_rate   = wins / n
        gross_win  = sum(p for p in pnls if p > 0)
        gross_loss = sum(abs(p) for p in pnls if p < 0)
        pf = (gross_win / gross_loss
              if gross_loss > 0
              else (999.0 if gross_win > 0 else 1.0))

        total_trades = sum(r.get("total_trades") or 0 for r in chron)

        return {
            "sharpe":         round(sharpe, 3),
            "mdd_pct":        round(mdd_pct, 4),
            "win_rate":       round(win_rate, 4),
            "profit_factor":  round(pf, 3),
            "total_trades":   total_trades,
            "days":           n,
            "daily_pnl_list": pnls,
            "mean_pnl":       round(mean_pnl, 0),
            "std_pnl":        round(std_pnl, 0),
            "cum_pnl":        round(sum(pnls), 0),
        }

    def compare_versions(
        self, ver_a: str, ver_b: str
    ) -> Dict[str, Any]:
        """
        두 버전 성과 비교 (delta 계산).
        ver_a = 이전, ver_b = 현재 기준
        """
        a = self.get_version(ver_a)
        b = self.get_version(ver_b)
        if not a or not b:
            return {}

        def _live_or_wfa(info: Dict[str, Any]) -> Dict[str, Any]:
            live = info.get("live_snapshot") or {}
            if live.get("sharpe") is not None:
                return live
            stages = info.get("stages", {})
            return stages.get("WFA") or stages.get("BACKTEST") or {}

        ma = _live_or_wfa(a)
        mb = _live_or_wfa(b)

        def _delta(key: str, scale: float = 1.0) -> Optional[float]:
            va = ma.get(key)
            vb = mb.get(key)
            if va is None or vb is None:
                return None
            return round((vb - va) * scale, 4)

        return {
            "version_from":      ver_a,
            "version_to":        ver_b,
            "sharpe_delta":      _delta("sharpe"),
            "mdd_pct_delta":     _delta("mdd_pct"),
            "win_rate_delta":    _delta("win_rate"),
            "pf_delta":          _delta("profit_factor"),
            "calmar_delta":      _delta("calmar"),
            "changed_params_to": b.get("changed_params", []),
        }

    # ─── 내부 헬퍼 ───────────────────────────────────────────────────────
    def _insert_stage_result(
        self,
        cur:     sqlite3.Cursor,
        version: str,
        stage:   str,
        now:     str,
        metrics: Dict[str, Any],
    ) -> None:
        cur.execute(
            """INSERT INTO strategy_stage_results
               (version, stage, evaluated_at, sharpe, mdd_pct, win_rate,
                profit_factor, calmar, total_trades, raw_json)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (
                version, stage, now,
                metrics.get("sharpe"),
                metrics.get("mdd_pct"),
                metrics.get("win_rate"),
                metrics.get("profit_factor"),
                metrics.get("calmar"),
                metrics.get("total_trades"),
                json.dumps(metrics, ensure_ascii=False),
            ),
        )

    def _get_stage_results(
        self, cur: sqlite3.Cursor, version: str
    ) -> Dict[str, Dict[str, Any]]:
        cur.execute(
            """SELECT stage, sharpe, mdd_pct, win_rate, profit_factor, calmar, total_trades
               FROM strategy_stage_results WHERE version=? ORDER BY id""",
            (version,),
        )
        rows = cur.fetchall()
        result = {}
        for r in rows:
            stage = r[0]
            # 같은 stage 중 마지막 값 사용 (덮어쓰기)
            result[stage] = {
                "sharpe": r[1], "mdd_pct": r[2], "win_rate": r[3],
                "profit_factor": r[4], "calmar": r[5], "total_trades": r[6],
            }
        return result

    def _get_param_changes(
        self, cur: sqlite3.Cursor, version: str
    ) -> List[Dict[str, Any]]:
        cur.execute(
            "SELECT param_name, val_from, val_to FROM strategy_param_changes WHERE version=?",
            (version,),
        )
        return [
            {"param": r[0], "from": r[1], "to": r[2]}
            for r in cur.fetchall()
        ]

    def _get_latest_live_snapshot(
        self, cur: sqlite3.Cursor, version: str
    ) -> Optional[Dict[str, Any]]:
        cur.execute(
            """SELECT sharpe, mdd_pct, win_rate, profit_factor, calmar,
                      total_trades, daily_pnl, snapshot_date
               FROM strategy_live_snapshots WHERE version=?
               ORDER BY snapshot_date DESC LIMIT 1""",
            (version,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return {
            "sharpe": row[0], "mdd_pct": row[1], "win_rate": row[2],
            "profit_factor": row[3], "calmar": row[4],
            "total_trades": row[5], "daily_pnl": row[6],
            "snapshot_date": row[7],
        }

    def _get_live_days(self, cur: sqlite3.Cursor, version: str) -> int:
        cur.execute(
            "SELECT COUNT(DISTINCT snapshot_date) FROM strategy_live_snapshots WHERE version=?",
            (version,),
        )
        row = cur.fetchone()
        return row[0] if row else 0

    def _compute_verdict(
        self,
        stages:    Dict[str, Dict[str, Any]],
        live_snap: Optional[Dict[str, Any]],
    ) -> str:
        """
        WFA 기준 대비 Live 성과 비교 판정.
        Live 데이터 5일 미만이면 INSUFFICIENT.
        """
        if not live_snap:
            return VERDICT_INSUFFICIENT

        # 롤링 계산 일수가 5일 미만이면 판정 보류
        if live_snap.get("days", 999) < 5:
            return VERDICT_INSUFFICIENT

        wfa = stages.get("WFA", {})
        if not wfa:
            return VERDICT_INSUFFICIENT

        live_sharpe = live_snap.get("sharpe")
        wfa_sharpe  = wfa.get("sharpe")
        live_mdd    = live_snap.get("mdd_pct")
        wfa_mdd     = wfa.get("mdd_pct")

        if live_sharpe is None or wfa_sharpe is None:
            return VERDICT_INSUFFICIENT

        sharpe_delta = live_sharpe - wfa_sharpe
        mdd_delta    = (abs(live_mdd or 0) - abs(wfa_mdd or 0))

        if (sharpe_delta >= _OUTPERFORM_SHARPE_DELTA
                and mdd_delta <= _OUTPERFORM_MDD_DELTA):
            return VERDICT_OUTPERFORM
        elif (sharpe_delta >= _NORMAL_SHARPE_DELTA
              and mdd_delta <= _NORMAL_MDD_DELTA):
            return VERDICT_NORMAL
        else:
            return VERDICT_UNDERPERFORM


# ─────────────────────────────────────────────────────────────────────────
# 전역 싱글턴 (main.py 및 대시보드에서 공유)
# ─────────────────────────────────────────────────────────────────────────
_registry: Optional[StrategyRegistry] = None


def get_registry() -> StrategyRegistry:
    """전역 StrategyRegistry 싱글턴 반환."""
    global _registry
    if _registry is None:
        _registry = StrategyRegistry()
    return _registry
