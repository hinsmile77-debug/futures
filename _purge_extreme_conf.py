"""
개선4: 과거 극단 신뢰도 샘플 격리 스크립트
-----------------------------------------------
CONF_CLIP 도입 이전(2026-06-04 이전) predictions 테이블의 confidence > 0.85 행을
predictions_archive 테이블로 이동 후 원본에서 삭제.

- 직접 DELETE하지 않고 아카이브 후 삭제 (복구 가능)
- ensemble_decisions는 건드리지 않음 (이미 calibration cap 0.85 이하)
- dry_run=True(기본)로 실행하면 삭제 없이 대상 건수만 출력

실행:
    python _purge_extreme_conf.py            # dry-run (안전 확인)
    python _purge_extreme_conf.py --execute  # 실제 격리 실행
"""
import sqlite3
import sys
import os

_DRY_RUN = "--execute" not in sys.argv

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "db", "predictions.db")
CUTOFF_DATE = "2026-06-04"
CONF_THRESHOLD = 0.85

if not os.path.exists(DB_PATH):
    print(f"[ERROR] DB 없음: {DB_PATH}")
    sys.exit(1)

conn = sqlite3.connect(DB_PATH, timeout=10)
conn.row_factory = sqlite3.Row

# 대상 건수 확인
rows = conn.execute(
    "SELECT COUNT(*) AS n, MIN(ts) AS min_ts, MAX(ts) AS max_ts "
    "FROM predictions "
    "WHERE confidence > ? AND ts < ?",
    (CONF_THRESHOLD, CUTOFF_DATE + " 00:00:00"),
).fetchone()

print(f"격리 대상: {rows['n']}건  ({rows['min_ts']} ~ {rows['max_ts']})")
print(f"threshold: confidence > {CONF_THRESHOLD}, ts < {CUTOFF_DATE}")

if _DRY_RUN:
    print("\n[DRY-RUN] 실제 변경 없음. --execute 플래그 추가 시 격리 실행.")
    conn.close()
    sys.exit(0)

if rows["n"] == 0:
    print("[SKIP] 격리 대상 없음.")
    conn.close()
    sys.exit(0)

# predictions_archive 테이블 생성 (없으면)
conn.execute(
    "CREATE TABLE IF NOT EXISTS predictions_archive AS "
    "SELECT * FROM predictions WHERE 0"
)
conn.execute(
    "CREATE INDEX IF NOT EXISTS idx_pa_ts ON predictions_archive (ts)"
)

# 아카이브로 이동
conn.execute(
    "INSERT INTO predictions_archive "
    "SELECT * FROM predictions "
    "WHERE confidence > ? AND ts < ?",
    (CONF_THRESHOLD, CUTOFF_DATE + " 00:00:00"),
)
deleted = conn.execute(
    "DELETE FROM predictions "
    "WHERE confidence > ? AND ts < ?",
    (CONF_THRESHOLD, CUTOFF_DATE + " 00:00:00"),
).rowcount
conn.commit()
conn.close()

# VACUUM은 트랜잭션 밖에서 별도 연결로 실행
conn2 = sqlite3.connect(DB_PATH, timeout=10)
conn2.execute("VACUUM")
conn2.close()

print(f"[DONE] {deleted}건 → predictions_archive로 이동 완료.")
print("복구 필요 시: INSERT INTO predictions SELECT * FROM predictions_archive WHERE ts < ?")
