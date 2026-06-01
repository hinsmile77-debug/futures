# scripts/cleanup_cancel_add_ratio.py
# Phase D: cancel_add_ratio DB 클린업
#
# 처리 전략:
#   |val| > 10  → DELETE  (극단 이상치, 구버전 raw ratio 오염)
#   3 < |val| <= 10 → UPDATE (clip to ±3.0, 현행 _stable_cancel_add_ratio 기준)
#
# 사용법:
#   python scripts/cleanup_cancel_add_ratio.py           # dry-run (변경 없음)
#   python scripts/cleanup_cancel_add_ratio.py --apply   # 실제 적용
#
import sys
import os
import json
import sqlite3
import datetime
import shutil

# 프로젝트 루트를 sys.path 에 추가
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from config.settings import RAW_DATA_DB

DRY_RUN = "--apply" not in sys.argv
EXTREME_DELETE_THRESHOLD = 10.0   # 이 값 초과 → 행 삭제
CLAMP_THRESHOLD          = 3.0    # 이 값 초과 → ±3.0 클램프
MIN_TRAIN_BARS_TARGET    = 5000   # 복원 목표 (약 2026-05-26 예정)

print("=" * 60)
print("cancel_add_ratio DB 클린업 (Phase D)")
print(f"  대상 DB  : {RAW_DATA_DB}")
print(f"  모드     : {'DRY-RUN (--apply 없음)' if DRY_RUN else '실제 적용'}")
print(f"  삭제 기준: |val| > {EXTREME_DELETE_THRESHOLD}")
print(f"  클램프   : {CLAMP_THRESHOLD} < |val| <= {EXTREME_DELETE_THRESHOLD}  →  ±{CLAMP_THRESHOLD}")
print("=" * 60)

if not os.path.exists(RAW_DATA_DB):
    print(f"[ERR] DB 없음: {RAW_DATA_DB}")
    sys.exit(1)

# ── 1. 현황 조사 ──────────────────────────────────────────────────────────────
with sqlite3.connect(RAW_DATA_DB, timeout=30) as conn:
    total_rows = conn.execute("SELECT COUNT(*) FROM raw_features").fetchone()[0]
    all_rows   = conn.execute(
        "SELECT rowid, ts, features FROM raw_features ORDER BY ts"
    ).fetchall()

cnt_with_key  = 0
rows_delete   = []   # (rowid, ts, val)
rows_clamp    = []   # (rowid, ts, val, clamped)
max_abs       = 0.0

for rowid, ts, feat_json in all_rows:
    try:
        fd = json.loads(feat_json)
    except Exception:
        continue
    v = fd.get("cancel_add_ratio")
    if v is None:
        continue
    v = float(v)
    cnt_with_key += 1
    abs_v = abs(v)
    if abs_v > max_abs:
        max_abs = abs_v
    if abs_v > EXTREME_DELETE_THRESHOLD:
        rows_delete.append((rowid, ts, v))
    elif abs_v > CLAMP_THRESHOLD:
        clamped = max(-CLAMP_THRESHOLD, min(CLAMP_THRESHOLD, v))
        rows_clamp.append((rowid, ts, v, clamped, feat_json, fd))

print(f"\n[조사 결과]")
print(f"  raw_features 총 행수    : {total_rows}")
print(f"  cancel_add_ratio 보유행 : {cnt_with_key}")
print(f"  최대 절대값             : {max_abs:.4f}")
print(f"  삭제 대상 (|v|>{EXTREME_DELETE_THRESHOLD})  : {len(rows_delete)}행")
print(f"  클램프 대상 (|v|>{CLAMP_THRESHOLD})  : {len(rows_clamp)}행")
if rows_delete:
    examples = [(ts, round(v, 2)) for _, ts, v in rows_delete[:5]]
    print(f"  삭제 예시             : {examples}")
if rows_clamp:
    examples = [(ts, round(v, 4), round(cv, 4)) for _, ts, v, cv, _, _ in rows_clamp[:5]]
    print(f"  클램프 예시(원→결과)  : {examples}")

remaining_after = total_rows - len(rows_delete)
print(f"\n  정리 후 예상 행수       : {remaining_after}")
print(f"  MIN_TRAIN_BARS 목표({MIN_TRAIN_BARS_TARGET}) : "
      f"{'충분 OK' if remaining_after >= MIN_TRAIN_BARS_TARGET else f'부족 NG ({remaining_after - MIN_TRAIN_BARS_TARGET}행 부족)'}")

if DRY_RUN:
    print("\n[DRY-RUN] 변경 없음. --apply 옵션으로 실제 적용하세요.")
    sys.exit(0)

# ── 2. 백업 ───────────────────────────────────────────────────────────────────
ts_tag = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
backup_path = RAW_DATA_DB.replace(".db", f"_backup_{ts_tag}.db")
shutil.copy2(RAW_DATA_DB, backup_path)
print(f"\n[백업] {backup_path}")

# ── 3. 실제 적용 ───────────────────────────────────────────────────────────────
with sqlite3.connect(RAW_DATA_DB, timeout=30) as conn:
    conn.execute("PRAGMA journal_mode=WAL")

    # 3-A. 극단 이상치 행 삭제
    if rows_delete:
        delete_rowids = [r[0] for r in rows_delete]
        # sqlite3 placeholders: DELETE rowid IN (?,?,...)
        placeholders = ",".join("?" * len(delete_rowids))
        conn.execute(
            f"DELETE FROM raw_features WHERE rowid IN ({placeholders})",
            delete_rowids,
        )
        print(f"[삭제] {len(rows_delete)}행 삭제 완료")

    # 3-B. 클램프 적용 (JSON 업데이트)
    if rows_clamp:
        updated = 0
        for rowid, ts, orig_v, clamped_v, orig_json, fd in rows_clamp:
            fd["cancel_add_ratio"] = round(float(clamped_v), 6)
            new_json = json.dumps(fd, ensure_ascii=False, separators=(",", ":"))
            conn.execute(
                "UPDATE raw_features SET features=? WHERE rowid=?",
                (new_json, rowid),
            )
            updated += 1
        print(f"[클램프] {updated}행 업데이트 완료")

    conn.commit()

# VACUUM은 트랜잭션 외부에서 별도 연결로 실행
with sqlite3.connect(RAW_DATA_DB, timeout=30) as _vc:
    _vc.execute("VACUUM")

# ── 4. 결과 확인 ─────────────────────────────────────────────────────────────
with sqlite3.connect(RAW_DATA_DB, timeout=30) as conn:
    final_rows = conn.execute("SELECT COUNT(*) FROM raw_features").fetchone()[0]

print(f"\n[완료] 최종 raw_features 행수: {final_rows}")
if final_rows >= MIN_TRAIN_BARS_TARGET:
    print(f"  [OK] MIN_TRAIN_BARS={MIN_TRAIN_BARS_TARGET} 복원 조건 달성!")
    print(f"  [OK] learning/batch_retrainer.py MIN_TRAIN_BARS 를 {MIN_TRAIN_BARS_TARGET}으로 변경하세요.")
else:
    print(f"  [NG] 아직 {final_rows}행 -- {MIN_TRAIN_BARS_TARGET}까지 {MIN_TRAIN_BARS_TARGET - final_rows}행 더 필요")
    print(f"  [NG] MIN_TRAIN_BARS 는 현행 3000 유지 권장")
