# scripts/monthly_cleanup.py
# 월 1회 정기 클린업 — 로그·DB 오래된 데이터 정리
#
# ══════════════════════════════════════════════════════════════════════════════
# [MW0601 476차] 보관정책 재설계 — 이 스크립트는 **한 번도 실행된 적이 없다.**
# ══════════════════════════════════════════════════════════════════════════════
# 2026-08-18 실측: `logs/`에 2026-05-02~08-18 **87 거래일 / 6.4GB**가 그대로 있다.
# 즉 구 `LOG_KEEP_DAYS=30`이 집행됐다면 남아 있을 수 없는 상태다. 그런데
# `dev_memory/NEXT_TODO.md`에는 `[NEXT 2026-07-01] monthly_cleanup.py 첫 실행 —
# python scripts/monthly_cleanup.py --apply`가 **미완료 항목으로 두 번** 걸려 있다.
#
# 🔴 그 상태로 `--apply`를 돌렸다면 다음이 **영구 소실**됐다(2026-08-18 실측):
#
#     ensemble_decisions   9,800행 / 24,501행 (40.0%)   ← 검증 캠페인 시계열 원자재
#     predictions         53,186행 / 101,628행 (52.3%)
#     meta_labels         53,115행 / 99,632행 (53.3%)
#     logs/               57 거래일분 ≈ 4~5GB
#
# `data/db/predictions.db`는 **gitignore 대상**이고 DB 백업은 7일치뿐이다 —
# 되돌릴 경로가 없다. 그리고 `scripts/generate_validation_campaign_report.py`가
# `PREDICTIONS_DB`를 직접 읽는다(:347 등). `ensemble_decisions`에는 471차 후속6의
# `sizing_trace`, 473차 F-8의 `spread_ticks`/`spread_extreme_shadow`가 실려 있고,
# 그 F-8 채널은 `min_samples` 도달 ETA가 **약 7.1개월(149 거래일)**이다.
# 60일 컷은 그 표본을 매달 절반씩 잘라내 **판정을 영원히 불가능하게 만든다.**
#
# ── 그래서 바꾼 것 ────────────────────────────────────────────────────────────
#   1. DB 행 삭제(shap/predictions)는 **기본 비활성**이다. `--allow-db-prune`을
#      명시해야만 후보로 올라간다. "정리"의 기본값이 관측 파괴여서는 안 된다.
#   2. 켜더라도 보관 하한 `_MIN_KEEP_DAYS_DB = 190`(26주 WFA 182일 + 여유)을
#      강제한다. 그보다 짧은 값은 무시하고 190으로 올린다.
#   3. 로그는 **mtime이 아니라 파일명의 날짜**로 판정한다(복사·백업 복원이
#      mtime을 바꿔도 그게 어느 날 로그인지는 안 바뀐다).
#   4. 지운 파일명을 **전부 인쇄**한다. 조용한 정리는 사고가 나도 아무도 모른다.
#   5. 개별 삭제 실패는 경고만 내고 넘어간다.
#   6. 보호 패턴(`crash_fault*` 등 자체 로테이션 대상, `*.json` 산출물)은
#      **살릴 것이 정규식에 안 걸리게** 짰다.
#
# ── 보관 기간의 근거 (2026-08-18 실측, 마흐디 수치를 복사하지 않았다) ─────────
#   · 일일 점검 문서 24편의 소급 인용 거리: 중앙값 7일 · **최대 꼬리 182일**
#     (182일 = 26주 = Walk-Forward 재검증 주기와 같은 스케일이다. 우연이 아니다)
#   · 증거 다이제스트는 원본 로그가 있어야 재생성된다 → **로그 보관이 증거의
#     재생성 가능성을 결정한다.** 둘을 따로 정할 수 없다.
#   · `docs/정기점검` 산출물 전체는 100파일 **3.4MB**뿐이다 — 용량 문제가 아니며
#     전부 git 추적이라 지워도 용량이 안 줄고 grep 대상만 잃는다.
#   → `LOG_KEEP_DAYS = 190`. 현재 보유 87일은 **한 건도 삭제되지 않는다.**
#
# ⚠ 로그 6.4GB의 91%는 `*_HOGA.log`(29MB/일)와 `*_SYSTEM.log`(39MB/일)다.
#   채널별 차등 보관이 합리적으로 보이지만 **HOGA의 소급 인용 거리를 재지 않았다** —
#   측정 없는 차등은 이 파일이 이미 한 번 저지른 실수(근거 없는 30일)의 반복이다.
#   차등 보관은 주간회의 안건으로 남긴다.
#
# 대상:
#   [1] logs/          : LOG_KEEP_DAYS(190)일 이전 로그 파일 삭제 — 파일명 날짜 기준
#   [2] shap.db        : SHAP_KEEP_DAYS 이전 shap_scores 행 삭제 (--allow-db-prune 필요)
#   [3] predictions.db : PRED_KEEP_DAYS 이전 predictions/ensemble_decisions 삭제
#                        (--allow-db-prune 필요)
#   [4] DB 백업 파일   : BACKUP_KEEP_DAYS(7)일 이전 삭제
#
# 사용법:
#   python scripts/monthly_cleanup.py                      # dry-run (변경 없음)
#   python scripts/monthly_cleanup.py --apply              # 로그·백업만 실제 삭제
#   python scripts/monthly_cleanup.py --apply --allow-db-prune   # DB 행까지
#
# ⚠ **장중에 돌리지 말 것.** 라이브 프로세스가 같은 DB를 쓰고, DB 전수 스캔이
#   파이프라인 지연을 유발해 CB⑤를 자가유발한 전례가 있다(2026-08-10, CLAUDE.md).
#
import os
import re
import sys
import sqlite3
import datetime
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from config.settings import LOG_DIR, DB_DIR, SHAP_DB, PREDICTIONS_DB

DRY_RUN = "--apply" not in sys.argv
ALLOW_DB_PRUNE = "--allow-db-prune" in sys.argv

# [476차] 30 → 190. 근거는 파일 머리말 참조(소급 인용 꼬리 182일 = 26주 WFA).
LOG_KEEP_DAYS    = 190
SHAP_KEEP_DAYS   = 190
PRED_KEEP_DAYS   = 190
BACKUP_KEEP_DAYS = 7

# DB 행 삭제의 보관 하한 — 이보다 짧은 값은 무시하고 이 값으로 올린다.
# 26주 Walk-Forward(182일) 창을 자르는 정리는 어떤 사유로도 허용하지 않는다.
_MIN_KEEP_DAYS_DB = 190

# 로그 삭제에서 **구조적으로 제외**되는 것들.
# "지울 것의 패턴"이 아니라 "살릴 것이 대상 정규식에 안 걸리게" 짜는 쪽이 안전하다.
#   · crash_fault*      : CRASH_LOG_ROTATE_MB 자체 로테이션이 관리한다(436차)
#   · *.json            : discovery_results_* 등 산출물이지 로그가 아니다
#   · 날짜가 없는 파일  : creon_launch.log 등 세션 단발 로그 — 날짜 판정이 불가능하므로
#                         "모르면 지우지 않는다"
_LOG_PROTECT_RE = re.compile(r"^(crash_fault|crash_init|crash_test)", re.I)
# 파일명 어디든 YYYYMMDD 가 있으면 그 날짜를 쓴다(20260818_SYSTEM.log,
# retrain_eod_20260818.log, launcher_20260818_084001_2415.log 모두 매칭).
_LOG_DATE_RE = re.compile(r"(20\d{2})(0[1-9]|1[0-2])([0-3]\d)")

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


def log_file_date(name):
    """파일명에서 날짜를 뽑는다. 없으면 None(→ 삭제 대상이 아니다).

    [476차 / 지침 §4-3] **mtime을 쓰지 않는다.** 파일을 복사하거나 백업에서
    되돌리면 mtime은 바뀌지만 그게 어느 날 로그인지는 바뀌지 않는다.
    """
    m = _LOG_DATE_RE.search(name)
    if not m:
        return None
    try:
        return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def _remove(path, label):
    """개별 삭제 — 실패는 경고만. 정리가 본업(다음 달 재시도)을 죽이면 안 된다."""
    try:
        os.remove(path)
        return True
    except OSError as e:
        print("  [경고] %s 삭제 실패(무해, 다음 달 재시도): %s — %s"
              % (label, os.path.basename(path), e))
        return False


print("=" * 68)
print("monthly_cleanup.py")
print("  mode    :", "DRY-RUN" if DRY_RUN else "APPLY")
print("  DB 정리 :", "허용(--allow-db-prune)" if ALLOW_DB_PRUNE
      else "**비활성** — 켜려면 --allow-db-prune")
print("  now     :", now.strftime("%Y-%m-%d %H:%M"))
print("=" * 68)

# ── [1] 로그 파일 ──────────────────────────────────────────────
print("\n[1] logs/ --", LOG_KEEP_DAYS, "일 이전 삭제 (파일명 날짜 기준)")
if LOG_KEEP_DAYS < 1:
    # 0을 "전부 지워라"로 읽지 않는다. 킬스위치다.
    print("  [스킵] LOG_KEEP_DAYS < 1 — 킬스위치. 아무것도 지우지 않는다.")
    log_files = []
else:
    log_cut = cutoff_dt(LOG_KEEP_DAYS).date()
    log_files = []
    skipped_nodate = 0
    for f in glob.glob(os.path.join(LOG_DIR, "*")):
        if not os.path.isfile(f):
            continue                      # Mireuk_batch/ 등 하위 디렉터리는 건드리지 않는다
        base = os.path.basename(f)
        if _LOG_PROTECT_RE.match(base) or base.lower().endswith(".json"):
            continue                      # 보호 대상
        d = log_file_date(base)
        if d is None:
            skipped_nodate += 1
            continue                      # 날짜를 모르면 지우지 않는다
        if d < log_cut:
            log_files.append(f)
    log_size_mb = sum(os.path.getsize(f) for f in log_files) / 1024 / 1024
    print("  컷오프:", log_cut.isoformat(),
          " / 대상:", len(log_files), "개 파일,", round(log_size_mb, 1), "MB",
          " / 날짜없어 보존:", skipped_nodate, "개")
    for f in sorted(log_files):
        print("    -", os.path.basename(f))     # 지운 것은 반드시 인쇄한다
    if not DRY_RUN and log_files:
        ok = sum(1 for f in log_files if _remove(f, "로그"))
        print("  ->", ok, "/", len(log_files), "개 삭제 완료")

# ── [2] shap.db ────────────────────────────────────────────────
_shap_keep = max(SHAP_KEEP_DAYS, _MIN_KEEP_DAYS_DB)
print("\n[2] shap.db --", _shap_keep, "일 이전 shap_scores 삭제")
if not ALLOW_DB_PRUNE:
    print("  [스킵] DB 행 삭제 비활성 — --allow-db-prune 을 붙여야 후보가 된다.")
elif os.path.exists(SHAP_DB):
    shap_cut = cutoff_str(_shap_keep)
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
_pred_keep = max(PRED_KEEP_DAYS, _MIN_KEEP_DAYS_DB)
print("\n[3] predictions.db --", _pred_keep, "일 이전 삭제")
print("  ⚠ `ensemble_decisions`는 검증 캠페인의 시계열 원자재다"
      " (generate_validation_campaign_report.py가 직접 읽는다).")
print("    predictions.db는 gitignore 대상이고 백업은 7일치뿐 — 삭제 = 영구 소실.")
if not ALLOW_DB_PRUNE:
    print("  [스킵] DB 행 삭제 비활성 — --allow-db-prune 을 붙여야 후보가 된다.")
elif os.path.exists(PREDICTIONS_DB):
    pred_cut = cutoff_str(_pred_keep)
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
if BACKUP_KEEP_DAYS < 1:
    print("  [스킵] BACKUP_KEEP_DAYS < 1 — 킬스위치.")
    backup_files = []
else:
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
        ok = sum(1 for f in backup_files if _remove(f, "백업"))
        print("  ->", ok, "/", len(backup_files), "개 삭제 완료")

# ── 요약 ───────────────────────────────────────────────────────
print()
if DRY_RUN:
    print("[DRY-RUN] 변경 없음. --apply 로 실제 적용하세요.")
else:
    print("[완료]")
if not ALLOW_DB_PRUNE:
    print("[안내] DB 행 삭제는 비활성입니다. 켜기 전에 "
          "docs/정기점검/보관정책_MW0601-20260818.md 의 근거를 먼저 읽으세요.")
