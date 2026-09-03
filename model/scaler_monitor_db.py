# model/scaler_monitor_db.py
# 섹션 8: 스케일러 상태 모니터 DB — scaler_monitor.db
#
# 테이블:
#   scaler_events — 분봉 단위 호라이즌별 실시간 이벤트
#   scaler_daily  — 일별 EOD 집계
import json
import os
import sqlite3
import logging
from typing import List, Optional

from config.settings import SCALER_MONITOR_DB

logger = logging.getLogger("SIGNAL")

_DDL = """
CREATE TABLE IF NOT EXISTS scaler_events (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    ts             TEXT NOT NULL,
    date           TEXT NOT NULL,
    horizon        TEXT NOT NULL,
    fitted_at      TEXT,
    age_minutes    REAL,
    max_z          REAL,
    max_z_feature  TEXT,
    extreme_count  INTEGER DEFAULT 0,
    extreme_count_adj INTEGER,
    raw_value      REAL,
    pre_value      REAL,
    scaler_mean    REAL,
    scaler_std     REAL,
    refresh_type   TEXT,
    refresh_reason TEXT
);
CREATE INDEX IF NOT EXISTS idx_se_date ON scaler_events(date, ts);

CREATE TABLE IF NOT EXISTS scaler_daily (
    date             TEXT PRIMARY KEY,
    max_age_minutes  REAL,
    total_extreme    INTEGER,
    top_extreme_feat TEXT,
    refresh_count    INTEGER,
    refresh_types    TEXT,
    grade_x_minutes  INTEGER,
    cb3_triggered    INTEGER DEFAULT 0,
    note             TEXT
);
"""

# [MW0601 457차 / G5] 모델 건강도 컬럼 — ConstOut을 "사건"이 아니라 "지표"로.
#
# 왜: 2026-08-11에 3m이 **하루 6회** 상수 출력으로 앙상블에서 제외됐다 되돌아왔는데,
# 그 사실이 `daily_stats`에도 `scaler_daily`에도 남지 않았다. 경고 로그만 흘러가고
# 추세가 축적되지 않으니 "어제보다 나빠졌는가"를 물을 수 없었다.
# 같은 날 WeightCollapse도 370분 중 **82분(22%)** 였는데 역시 일별 기록이 없다.
#
# 신규 DB를 만들지 않는다 — 관리 포인트가 늘면 CB②·FP-CRITICAL처럼 "재검토하기로
# 했는데 안 함" 상태가 된다(317차 사용자 원칙). 기존 일별 집계에 컬럼만 붙인다.
#
# 파생 지표 **앙상블 유효 가동률** = 1 − (ConstOut 제외 분 + WeightCollapse 분) / 총 분
#   2026-08-11 추정 70%대. 이 값이 26주 WFA 재검증 시 모델 안정성 추이의 입력이 된다.
_HEALTH_COLS = [
    # 분모 — 그날 파이프라인이 실제로 돈 분(minute) 수
    ("pipeline_minutes",        "INTEGER DEFAULT 0"),
    # ConstOut: 전이 횟수(사건) / 제외된 분·호라이즌 합(지속시간)
    ("const_out_events",        "INTEGER DEFAULT 0"),
    ("const_out_minutes",       "INTEGER DEFAULT 0"),
    ("const_out_by_horizon",    "TEXT"),          # JSON {hz: {events, minutes}}
    # 앙상블 가중 붕괴 — conf 0.85 고정 "판단 불가" 분
    ("weight_collapse_minutes", "INTEGER DEFAULT 0"),
    # 장중 GBM 재학습 완료 횟수 (ConstOut 연쇄의 하류 지표)
    ("intraday_retrain_count",  "INTEGER DEFAULT 0"),
    # 파생 — 0.0~1.0. NULL이면 "미측정"이지 "0"이 아니다(계측 4원칙 ②)
    ("ensemble_uptime",         "REAL"),
    # ── [MW0601 482차 / G-1·G-2] CB③ 가용성 ──────────────────────────────
    # 절대원칙 §2의 CB③이 하루 중 실제로 "판정 가능"했던 분 수. 분모는 위
    # pipeline_minutes 다. 2026-08-20에 acc30m < 0.28 이 236분(64.0%)인데 HALT
    # 0회였고, 그 분들이 "표본 부족이라 판정을 안 한 것"인지 "판정했는데 통과한
    # 것"인지 사후 재구성이 불가능했다 — 전환기준 ⑥(CB③ 기준 호라이즌 교체)을
    # 논의하려면 임계 이전에 **판정 입력이 존재했는가**를 먼저 알아야 한다.
    #
    # ⚠ DEFAULT 를 주지 않는다. `ALTER TABLE ADD COLUMN ... DEFAULT 0` 은 기존
    #   행에도 0을 채워 넣어 "측정한 적 없는 51거래일"이 "ready 0분"으로 위장된다
    #   (계측 4원칙 ②). NULL 로 남겨 미측정임을 보존한다.
    ("cb3_ready_minutes",       "INTEGER"),
    # 스케일러 재적합이 acc30m 버퍼를 되감은 횟수와 그때 버린 표본 수.
    # 재적합이 잦을수록 CB③은 표본을 못 채우고, 표본을 못 채우면 판정이 안 된다 —
    # 두 계측이 서로를 침식하는 관계를 처음 수치화한다(482차 G-2).
    ("cb3_buffer_resets",       "INTEGER"),
    ("cb3_samples_dropped",     "INTEGER"),
    # ── [MW0601 493차 후속5 / F-AB] CB③ **조건 성립** 축 ──────────────────
    # 위 `cb3_ready_minutes` 는 「판정 **가능**했던 분」이고, 이쪽은 「임계 미달이라
    # HALT **조건이 실제로 성립**했던 분」이다. 둘은 다른 질문이다 —
    # 전환기준 ⑥(CB③ 기준 호라이즌 교체)을 논의하려면 후자가 있어야
    # "차단을 켰다면 무엇을 잃었겠는가"를 답할 수 있다.
    #
    # 490차 F-G 가 이 세 카운터를 만들었지만 **로그로만 나갔다.** 그 로그 줄이
    # 2026-08-24·25 이틀 연속 서식 오류로 죽으면서(F-Y) 값이 통째로 사라졌고,
    # 오늘 값(69분)은 이 점검이 DEBUG 로그에서 손으로 복원해야 했다.
    # 🔴 **로그는 사람이 읽고 DB는 시계열이 읽는다** — 둘 다 있어야 한다.
    #
    # ⚠ DEFAULT 를 주지 않는 이유는 위 `cb3_ready_minutes` 와 같다 — 기존 행은
    #   NULL(**미측정**)이며 0(「사건이 없었다」)과 구분된다(계측 4원칙 ②).
    ("cb3_would_halt_minutes",  "INTEGER"),
    ("cb3_would_halt_entries",  "INTEGER"),
    ("cb3_would_halt_pnl_krw",  "REAL"),
]


def init_db() -> None:
    """DB 파일 생성 + 스키마 초기화 (멱등). 기존 DB에 신규 컬럼 자동 마이그레이션."""
    os.makedirs(os.path.dirname(SCALER_MONITOR_DB), exist_ok=True)
    with sqlite3.connect(SCALER_MONITOR_DB, timeout=10) as c:
        c.executescript(_DDL)
        existing = {r[1] for r in c.execute("PRAGMA table_info(scaler_events)").fetchall()}
        for col, typedef in [
            ("raw_value",   "REAL"),
            ("pre_value",   "REAL"),
            ("scaler_mean", "REAL"),
            ("scaler_std",  "REAL"),
            # [MW0601 526차 / F-C] 모니터 전용 보정 극단 피처 수(quality_* 제외·항등 그룹 dedupe).
            # DEFAULT 없음 — 기존 행은 NULL = 미측정(계측 4원칙 ②). 게이트 입력은 여전히
            # `extreme_count`(보정 전)다 — 두 값을 병기해 채널 P5-13 판정 뒤 처분한다.
            ("extreme_count_adj", "INTEGER"),
        ]:
            if col not in existing:
                c.execute("ALTER TABLE scaler_events ADD COLUMN %s %s" % (col, typedef))
        # [MW0601 457차 / G5] 모델 건강도 컬럼 마이그레이션 (기존 DB 무손실)
        _daily_cols = {r[1] for r in c.execute("PRAGMA table_info(scaler_daily)").fetchall()}
        for col, typedef in _HEALTH_COLS:
            if col not in _daily_cols:
                c.execute("ALTER TABLE scaler_daily ADD COLUMN %s %s" % (col, typedef))
        c.commit()


def insert_events_batch(rows: List[dict]) -> None:
    """호라이즌별 분봉 이벤트 일괄 INSERT.

    rows: list of dicts — keys:
        ts, date, horizon, fitted_at, age_minutes,
        max_z, max_z_feature, extreme_count,
        raw_value, pre_value, scaler_mean, scaler_std
    """
    if not rows:
        return
    try:
        with sqlite3.connect(SCALER_MONITOR_DB, timeout=5) as c:
            c.execute("PRAGMA journal_mode=WAL")  # WAL: 배경 스레드 write와 EXCLUSIVE lock 경합 해소
            c.executemany(
                """INSERT INTO scaler_events
                   (ts, date, horizon, fitted_at, age_minutes,
                    max_z, max_z_feature, extreme_count, extreme_count_adj,
                    raw_value, pre_value, scaler_mean, scaler_std)
                   VALUES
                   (:ts, :date, :horizon, :fitted_at, :age_minutes,
                    :max_z, :max_z_feature, :extreme_count, :extreme_count_adj,
                    :raw_value, :pre_value, :scaler_mean, :scaler_std)""",
                # [526차 / F-C] 구버전 행(키 부재)은 NULL = 미측정
                [dict(r, extreme_count_adj=r.get("extreme_count_adj")) for r in rows],
            )
            c.commit()
    except Exception as _e:
        logger.debug("[ScalerMonitorDB] insert_events_batch 실패: %s", _e)


def update_event_refresh(ts: str, refresh_type: str, refresh_reason: str) -> None:
    """해당 ts 의 모든 호라이즌 행에 refresh 정보 UPDATE.

    Phase B 트리거 스레드가 refit 완료 후 호출.
    """
    try:
        with sqlite3.connect(SCALER_MONITOR_DB, timeout=5) as c:
            c.execute("PRAGMA journal_mode=WAL")
            c.execute(
                "UPDATE scaler_events SET refresh_type=?, refresh_reason=? WHERE ts=?",
                (refresh_type, refresh_reason, ts),
            )
            c.commit()
    except Exception as _e:
        logger.debug("[ScalerMonitorDB] update_event_refresh 실패: %s", _e)


def aggregate_daily(date_str: str) -> dict:
    """date_str 의 scaler_events 집계 → scaler_daily INSERT 용 dict 반환.

    Returns:
        max_age_minutes, total_extreme, top_extreme_feat,
        refresh_count, refresh_types (JSON list)
    """
    try:
        with sqlite3.connect(SCALER_MONITOR_DB, timeout=5) as c:
            max_age = c.execute(
                "SELECT MAX(age_minutes) FROM scaler_events WHERE date=?",
                (date_str,),
            ).fetchone()[0] or 0.0

            total_extreme = c.execute(
                "SELECT COALESCE(SUM(extreme_count),0) FROM scaler_events WHERE date=?",
                (date_str,),
            ).fetchone()[0]

            top_row = c.execute(
                """SELECT max_z_feature, COUNT(*) AS cnt
                   FROM scaler_events
                   WHERE date=? AND extreme_count > 0
                   GROUP BY max_z_feature
                   ORDER BY cnt DESC LIMIT 1""",
                (date_str,),
            ).fetchone()
            top_feat = top_row[0] if top_row else ""

            refresh_rows = c.execute(
                """SELECT DISTINCT ts, refresh_type
                   FROM scaler_events
                   WHERE date=? AND refresh_type IS NOT NULL""",
                (date_str,),
            ).fetchall()
    except Exception as _e:
        logger.debug("[ScalerMonitorDB] aggregate_daily 실패: %s", _e)
        return {}

    refresh_ts_set = set(r[0] for r in refresh_rows)
    refresh_types  = sorted(set(r[1] for r in refresh_rows if r[1]))
    return {
        "max_age_minutes":  round(float(max_age), 1),
        "total_extreme":    int(total_extreme),
        "top_extreme_feat": top_feat,
        "refresh_count":    len(refresh_ts_set),
        "refresh_types":    json.dumps(refresh_types),
    }


def _int_or_none(v):
    """[MW0601 482차 / G-1] 값이 없으면 0이 아니라 None — 계측 4원칙 ②."""
    return None if v is None else int(v)


def _float_or_none(v):
    """[MW0601 493차 후속5 / F-AB] `_int_or_none` 의 실수판 (원 단위 손익용).

    0.0(「그 창에서 손익이 0이었다」)과 None(「안 쟀다」)은 다른 사실이다.
    """
    return None if v is None else float(v)


def compute_ensemble_uptime(health: Optional[dict]) -> Optional[float]:
    """[MW0601 457차 / G5] 앙상블 유효 가동률 = 1 − (ConstOut 분 + 붕괴 분) / 총 분.

    ⚠ 계측 4원칙 ② — 분모(pipeline_minutes)가 없으면 **0이 아니라 None**을 돌려준다.
      "가동률 0%"와 "측정 안 함"을 같은 값으로 쓰면 추이가 거짓말을 한다.

    ⚠ ConstOut 분은 **분·호라이즌** 합이라 여러 호라이즌이 동시에 죽으면 분모를 넘을
      수 있다. 가동률은 0.0으로 클램프하고, 원자료(const_out_minutes)는 그대로 남긴다.
    """
    if not health:
        return None
    total = int(health.get("pipeline_minutes") or 0)
    if total <= 0:
        return None
    lost = int(health.get("const_out_minutes") or 0) + \
        int(health.get("weight_collapse_minutes") or 0)
    return max(0.0, min(1.0, 1.0 - float(lost) / float(total)))


def insert_daily(
    date_str: str,
    stats: dict,
    grade_x_minutes: int = 0,
    cb3_triggered: int = 0,
    note: str = "",
    health: Optional[dict] = None,   # [MW0601 457차 / G5]
) -> None:
    """scaler_daily 일별 집계 INSERT OR REPLACE.

    health: [457차 G5] 모델 건강도 카운터. None이면 해당 컬럼은 NULL/0으로 남는다
            (구버전 호출부 하위호환 — "미측정"을 0으로 위장하지 않는다).
    """
    try:
        _h = health or {}
        _uptime = compute_ensemble_uptime(health)
        with sqlite3.connect(SCALER_MONITOR_DB, timeout=5) as c:
            c.execute(
                """INSERT OR REPLACE INTO scaler_daily
                   (date, max_age_minutes, total_extreme, top_extreme_feat,
                    refresh_count, refresh_types, grade_x_minutes, cb3_triggered, note,
                    pipeline_minutes, const_out_events, const_out_minutes,
                    const_out_by_horizon, weight_collapse_minutes,
                    intraday_retrain_count, ensemble_uptime,
                    cb3_ready_minutes, cb3_buffer_resets, cb3_samples_dropped,
                    cb3_would_halt_minutes, cb3_would_halt_entries,
                    cb3_would_halt_pnl_krw)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    date_str,
                    stats.get("max_age_minutes", 0.0),
                    stats.get("total_extreme", 0),
                    stats.get("top_extreme_feat", ""),
                    stats.get("refresh_count", 0),
                    stats.get("refresh_types", "[]"),
                    grade_x_minutes,
                    cb3_triggered,
                    note,
                    int(_h.get("pipeline_minutes") or 0),
                    int(_h.get("const_out_events") or 0),
                    int(_h.get("const_out_minutes") or 0),
                    json.dumps(_h.get("const_out_by_horizon") or {}, ensure_ascii=False),
                    int(_h.get("weight_collapse_minutes") or 0),
                    int(_h.get("intraday_retrain_count") or 0),
                    _uptime,
                    # [MW0601 482차 / G-1·G-2] health 가 없으면 **NULL**(미측정).
                    # 0 으로 채우면 "CB③이 하루 종일 죽어 있었다"로 읽힌다.
                    _int_or_none(_h.get("cb3_ready_minutes")),
                    _int_or_none(_h.get("cb3_buffer_resets")),
                    _int_or_none(_h.get("cb3_samples_dropped")),
                    # [MW0601 493차 후속5 / F-AB] 조건 성립 축.
                    # `health` 가 없으면 NULL(미측정) — 있으면 **0도 기록한다**
                    # ("조건이 한 번도 성립하지 않았다"는 정보다).
                    _int_or_none(_h.get("cb3_would_halt_minutes")),
                    _int_or_none(_h.get("cb3_would_halt_entries")),
                    _float_or_none(_h.get("cb3_would_halt_pnl_krw")),
                ),
            )
            c.commit()
        logger.info(
            "[ScalerMonitor] EOD 일별 집계 저장 | date=%s age=%.0fm extreme=%d refresh=%d grade_x=%d cb3=%d",
            date_str,
            stats.get("max_age_minutes", 0.0),
            stats.get("total_extreme", 0),
            stats.get("refresh_count", 0),
            grade_x_minutes,
            cb3_triggered,
        )
        # [MW0601 457차 / G5] 건강도는 별도 줄로 — 종전 줄의 포맷을 바꾸면 기존
        # 로그 파서·점검 스크립트가 깨진다.
        if health:
            # [MW0601 482차 / G-1·G-2] CB③ 가용성을 같은 줄에 붙인다 — 종전 필드
            # 순서와 포맷은 그대로 두고 **뒤에만** 덧붙인다(457차 G5의 이유와 동일:
            # 앞을 바꾸면 기존 로그 파서·점검 스크립트가 깨진다).
            _pm = int(_h.get("pipeline_minutes") or 0)
            _rm = _h.get("cb3_ready_minutes")
            if _rm is None:
                _cb3_txt = " | CB③ ready 미측정"
            else:
                _cb3_txt = " | CB③ ready %d분/%d분%s (리셋 %s회, 표본손실 %s건)" % (
                    int(_rm), _pm,
                    (" (%.0f%%)" % (100.0 * int(_rm) / _pm)) if _pm else "",
                    _h.get("cb3_buffer_resets"), _h.get("cb3_samples_dropped"),
                )
            logger.info(
                "[ModelHealth] date=%s 앙상블유효가동률=%s | 파이프라인 %d분 | "
                "ConstOut %d회/%d분%s | WeightCollapse %d분 | 장중재학습 %d회%s",
                date_str,
                ("%.1f%%" % (_uptime * 100.0)) if _uptime is not None else "미측정",
                _pm,
                int(_h.get("const_out_events") or 0),
                int(_h.get("const_out_minutes") or 0),
                (" " + json.dumps(_h.get("const_out_by_horizon") or {},
                                  ensure_ascii=False)) if _h.get("const_out_by_horizon") else "",
                int(_h.get("weight_collapse_minutes") or 0),
                int(_h.get("intraday_retrain_count") or 0),
                _cb3_txt,
            )
    except Exception as _e:
        logger.debug("[ScalerMonitorDB] insert_daily 실패: %s", _e)
