# scripts/monthly_cleanup.py
# 월 1회 정기 클린업 — 로그·DB 오래된 데이터 정리
#
# 대상:
#   [1] logs/          : LOG_KEEP_DAYS(30)일 이전 로그 파일 삭제
#   [2] shap.db        : SHAP_KEEP_DAYS(90)일 이전 shap_scores 행 삭제
#   [3] predictions.db : PRED_KEEP_DAYS(60)일 이전 predictions/ensemble_decisions 삭제
#   [4] DB 백업 파일   : BACKUP_KEEP_DAYS(7)일 이전 삭제
#
# 사용법:
#   python scripts/monthly_cleanup.py           # dry-run (변경 없음)
#   python scripts/monthly_cleanup.py --apply   # 실제 적용
#
import os
import sys
import sqlite3
import datetime
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from config.settings import LOG_DIR, DB_DIR, SHAP_DB, PREDICTIONS_DB

DRY_RUN = "--apply" not in sys.argv

LOG_KEEP_DAYS    = 30
SHAP_KEEP_DAYS   = 90
PRED_KEEP_DAYS   = 60
BACKUP_KEEP_DAYS = 7

now = datetime.datetime.now()


def _table_exists(conn, name):
    return conn.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?",
        (name,),
    ).fetchone()[0] > 0


def cutoff_str(days):
    return (now - datetime.timedelta(days=days)).strftime("%Y-%m-%d")


def cutoff_dt(days):
    return now - datetime.timedelta(days=days)


print("=" * 60)
print("monthly_cleanup.py")
print("  mode :", "DRY-RUN" if DRY_RUN else "APPLY")
print("  now  :", now.strftime("%Y-%m-%d %H:%M"))
print("=" * 60)

# ── [1] 로그 파일 ──────────────────────────────────────────────
print("\n[1] logs/ --", LOG_KEEP_DAYS, "일 이전 삭제")
log_cut = cutoff_dt(LOG_KEEP_DAYS)
log_files = [
    f for f in glob.glob(os.path.join(LOG_DIR, "*"))
    if os.path.isfile(f) and os.path.getmtime(f) < log_cut.timestamp()
]
log_size_mb = sum(os.path.getsize(f) for f in log_files) / 1024 / 1024
print("  대상:", len(log_files), "개 파일,", round(log_size_mb, 1), "MB")
if not DRY_RUN:
    for f in log_files:
        os.remove(f)
    print("  ->", len(log_files), "개 삭제 완료")

# ── [2] shap.db ────────────────────────────────────────────────
print("\n[2] shap.db --", SHAP_KEEP_DAYS, "일 이전 shap_scores 삭제")
shap_cut = cutoff_str(SHAP_KEEP_DAYS)
if os.path.exists(SHAP_DB):
    with sqlite3.connect(SHAP_DB, timeout=10) as c:
        cnt   = c.execute("SELECT COUNT(*) FROM shap_scores WHERE ts < ?", (shap_cut,)).fetchone()[0]
        total = c.execute("SELECT COUNT(*) FROM shap_scores").fetchone()[0]
    print("  현재:", total, "행  /  삭제 대상 (", shap_cut, "이전):", cnt, "행")
    if not DRY_RUN and cnt > 0:
        with sqlite3.connect(SHAP_DB, timeout=10) as c:
            c.execute("DELETE FROM shap_scores WHERE ts < ?", (shap_cut,))
            c.commit()
        with sqlite3.connect(SHAP_DB, timeout=10) as vc:
            vc.execute("VACUUM")
        with sqlite3.connect(SHAP_DB, timeout=10) as c:
            remaining = c.execute("SELECT COUNT(*) FROM shap_scores").fetchone()[0]
        print("  ->", cnt, "행 삭제  /  남은 행수:", remaining)
else:
    print("  shap.db 없음:", SHAP_DB)

# ── [3] predictions.db ─────────────────────────────────────────
print("\n[3] predictions.db --", PRED_KEEP_DAYS, "일 이전 삭제")
pred_cut = cutoff_str(PRED_KEEP_DAYS)
if os.path.exists(PREDICTIONS_DB):
    with sqlite3.connect(PREDICTIONS_DB, timeout=10) as c:
        p_cnt   = c.execute("SELECT COUNT(*) FROM predictions WHERE ts < ?", (pred_cut,)).fetchone()[0]
        p_total = c.execute("SELECT COUNT(*) FROM predictions").fetchone()[0]
        ed_cnt  = c.execute("SELECT COUNT(*) FROM ensemble_decisions WHERE ts < ?", (pred_cut,)).fetchone()[0] \
                  if _table_exists(c, "ensemble_decisions") else 0
        ed_total = c.execute("SELECT COUNT(*) FROM ensemble_decisions").fetchone()[0] \
                   if _table_exists(c, "ensemble_decisions") else 0
        ml_cnt  = c.execute("SELECT COUNT(*) FROM meta_labels WHERE ts < ?", (pred_cut,)).fetchone()[0] \
                  if _table_exists(c, "meta_labels") else 0
        ml_total = c.execute("SELECT COUNT(*) FROM meta_labels").fetchone()[0] \
                   if _table_exists(c, "meta_labels") else 0

    print("  predictions       :", p_total, "행  삭제 대상:", p_cnt)
    print("  ensemble_decisions:", ed_total, "행  삭제 대상:", ed_cnt)
    print("  meta_labels       :", ml_total, "행  삭제 대상:", ml_cnt)

    if not DRY_RUN and (p_cnt + ed_cnt + ml_cnt) > 0:
        with sqlite3.connect(PREDICTIONS_DB, timeout=10) as c:
            c.execute("DELETE FROM predictions WHERE ts < ?", (pred_cut,))
            if _table_exists(c, "ensemble_decisions"):
                c.execute("DELETE FROM ensemble_decisions WHERE ts < ?", (pred_cut,))
            if _table_exists(c, "meta_labels"):
                c.execute("DELETE FROM meta_labels WHERE ts < ?", (pred_cut,))
            c.commit()
        with sqlite3.connect(PREDICTIONS_DB, timeout=10) as vc:
            vc.execute("VACUUM")
        print("  ->", p_cnt + ed_cnt + ml_cnt, "행 삭제 완료")
else:
    print("  predictions.db 없음:", PREDICTIONS_DB)

# ── [4] DB 백업 파일 ───────────────────────────────────────────
print("\n[4] DB 백업 파일 --", BACKUP_KEEP_DAYS, "일 이전 삭제")
backup_cut = cutoff_dt(BACKUP_KEEP_DAYS)
backup_files = [
    f for f in glob.glob(os.path.join(DB_DIR, "*backup*.db"))
    if os.path.isfile(f) and os.path.getmtime(f) < backup_cut.timestamp()
]
backup_size_mb = sum(os.path.getsize(f) for f in backup_files) / 1024 / 1024
print("  대상:", len(backup_files), "개 파일,", round(backup_size_mb, 1), "MB")
for f in backup_files:
    print("    -", os.path.basename(f))
if not DRY_RUN and backup_files:
    for f in backup_files:
        os.remove(f)
    print("  ->", len(backup_files), "개 삭제 완료")

# ── 요약 ───────────────────────────────────────────────────────
print()
if DRY_RUN:
    print("[DRY-RUN] 변경 없음. --apply 로 실제 적용하세요.")
else:
    print("[완료]")
