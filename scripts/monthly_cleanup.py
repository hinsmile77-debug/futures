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
# ══════════════════════════════════════════════════════════════════════════════
# [MW0601 479차] 채널별 차등 보관 + 압축 단계 (2026-08-19)
# ══════════════════════════════════════════════════════════════════════════════
# 476차가 "HOGA 소급 인용 거리를 재기 전에는 차등하지 않는다"로 남긴 미결
# (보관정책_MW0601-20260818.md §6-1)을 실측으로 닫았다. 근거 전문은
# `docs/정기점검/보관정책_로그차등_MW0601-20260819.md`. 요지:
#
#   · 점검 문서의 로그 파일 인용 558건 전수조사 — 과거분(≥1일)은 WARN 1건(1일)
#     뿐이고 나머지는 전부 **당일 인용**이다. 182일 소급 꼬리는 과거 문서·DB를
#     되짚은 것이지 과거 **로그 파일**을 여는 것이 아니었다.
#   · 원본 `.log`를 소급으로 glob 재집계하는 스크립트는 **TRADE·SIGNAL·PROBE**
#     3채널뿐이다(exit_expectancy_map · checklist_ev_regression ·
#     early_trail_exit_counterfactual · profit_guard_latch_watch ·
#     generate_validation_campaign_report → TRADE / profit_guard_latch_watch ·
#     p4_cvd_ofi_demotion_analysis → SIGNAL / analyze_gross_pcr_offline → PROBE).
#     세 채널 합계 39MB — 원본 190일 유지에 부담이 없다.
#   · 용량의 96%는 SYSTEM(3.8GB, 5~6월 일 220MB 버그 유산 — 수정돼 현재 0.7MB/일)
#     + HOGA(2.4GB, 현재도 일 41MB)다. 두 채널 다 소급 소비자가 **0**이다.
#   · 단 **HOGA 로그는 원시 5호가 잔량의 유일한 영구 기록**이다 — raw_data.db에
#     호가 테이블이 없다(파생값 ofi_norm·spread_ticks만 DB에 있다). 삭제가 아니라
#     **압축**이 정답이다. 실측 압축률: HOGA 8% · SYSTEM 2%.
#
# 3계층:
#   Tier A (원본 190일 유지) : TRADE·SIGNAL·PROBE — 소비 스크립트가 원본 .log를
#                              직접 glob한다. 압축하면 그 스크립트들이 조용히
#                              표본을 잃는다(계측 4원칙 ②의 파일판).
#   Tier B (30일 후 월 zip)  : SYSTEM·HOGA·MICRO·DATA·DEBUG·WARN·LEARNING·
#                              HEALTH·BACKFILL — 당일 소비뿐. 압축본은 190일
#                              컷 대상, 단 HOGA 압축본은 삭제 면제(아래).
#   Tier C (기존 보호 유지)  : crash_fault*(자체 로테이션) · 날짜 없는 단발 로그
#                              ("모르면 지우지 않는다") · *.json 산출물.
#
# ⚠ HOGA 압축본 삭제 면제(_ARCHIVE_DELETE_EXEMPT)는 **주간회의 결정 전까지의
#   보수 기본값**이다 — CORE 피처 잔여 이슈(cvd_divergence·ofi_norm 점질량,
#   CLAUDE.md §3)의 조사가 원시 호가 재생을 요구할 수 있고, 압축 HOGA는
#   ~3.3MB/일이라 무기한 보관 부담이 없다. 면제 해제는 주간회의 안건.
#
# 대상:
#   [1a] logs/         : Tier B 채널 LOG_COMPRESS_DAYS(30)일 이전 → 월 단위 zip
#   [1b] logs/         : LOG_KEEP_DAYS(190)일 이전 원본 삭제 — 파일명 날짜 기준
#                        (Tier B 채널 원본은 구조적으로 제외 — 수명은 압축본이 관리)
#   [1c] logs/         : 월 zip 중 그 달 말일이 190일 이전인 것 삭제 (HOGA 면제)
#   [2] shap.db        : SHAP_KEEP_DAYS 이전 shap_scores 행 삭제 (--allow-db-prune 필요)
#   [3] predictions.db : PRED_KEEP_DAYS 이전 predictions/ensemble_decisions 삭제
#                        (--allow-db-prune 필요)
#   [4] DB 백업 파일   : BACKUP_KEEP_DAYS(7)일 이전 삭제
#
# 사용법:
#   python scripts/monthly_cleanup.py                      # dry-run (변경 없음)
#   python scripts/monthly_cleanup.py --apply              # 로그 압축·삭제 + 백업 정리
#   python scripts/monthly_cleanup.py --apply --allow-db-prune   # DB 행까지
#
# 발화 지점: scripts/campaign_steps.py(EOD 체인 공용 모듈)가 매월 첫 캠페인
# 실행일(금요일 EOD)에 `--apply`로 1회 호출한다(마커: data/monthly_cleanup_last_run.txt,
# gitignore 대상 — PC별 로컬 상태). 보관정책 §4-6 원칙: 국면 점검이 아니라
# "하루의 끝이 확정된" EOD 체인 한 곳에만 건다. 따라서 「N일 보관」은 엄밀히
# 「N일 이상 보관」이다.
#
# ⚠ **장중에 돌리지 말 것.** 라이브 프로세스가 같은 DB를 쓰고, DB 전수 스캔이
#   파이프라인 지연을 유발해 CB⑤를 자가유발한 전례가 있다(2026-08-10, CLAUDE.md).
#   → [479차] main()이 utils.analysis_db.guard_intraday()로 스스로 차단한다(rc=2).
#     정규 EOD(15:45)는 장 마감 후라 걸리지 않는다.
#
import os
import re
import sys
import datetime
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# [476차] 30 → 190. 근거는 파일 머리말 참조(소급 인용 꼬리 182일 = 26주 WFA).
LOG_KEEP_DAYS    = 190
SHAP_KEEP_DAYS   = 190
PRED_KEEP_DAYS   = 190
BACKUP_KEEP_DAYS = 7

# [479차] Tier B 채널의 압축 유예 — 점검 문서의 로그 인용 최대 거리(1일)의
# 30배 여유. 이보다 어린 파일은 절대 건드리지 않는다.
LOG_COMPRESS_DAYS = 30

# DB 행 삭제의 보관 하한 — 이보다 짧은 값은 무시하고 이 값으로 올린다.
# 26주 Walk-Forward(182일) 창을 자르는 정리는 어떤 사유로도 허용하지 않는다.
_MIN_KEEP_DAYS_DB = 190

# ── [479차] 채널 3계층 (근거: 보관정책_로그차등_MW0601-20260819.md) ──────────
# Tier A — 원본 190일 유지. 소비 스크립트가 원본 .log를 직접 glob하는 채널.
#          여기 넣으면 압축 대상에서 빠진다. **여기서 빼려면 그 소비 스크립트를
#          먼저 압축본 대응으로 고쳐야 한다** (tests/test_479가 불변식으로 고정).
_RAW_KEEP_CHANNELS = frozenset({"TRADE", "SIGNAL", "PROBE"})

# Tier B — 30일 후 월 단위 zip. 당일 소비(점검 증거 수집)뿐인 채널.
_COMPRESS_CHANNELS = frozenset({
    "SYSTEM", "HOGA", "MICRO", "DATA", "DEBUG", "WARN",
    "LEARNING", "HEALTH", "BACKFILL",
})

# 압축본 190일 컷의 면제 채널 — HOGA는 원시 5호가 잔량의 유일한 영구 기록
# (raw_data.db에 호가 테이블 없음). 면제 해제는 주간회의 결정 사항.
_ARCHIVE_DELETE_EXEMPT = frozenset({"HOGA"})

# 로그 삭제에서 **구조적으로 제외**되는 것들.
# "지울 것의 패턴"이 아니라 "살릴 것이 대상 정규식에 안 걸리게" 짜는 쪽이 안전하다.
#   · crash_fault*      : CRASH_LOG_ROTATE_MB 자체 로테이션이 관리한다(436차)
#   · *.json            : discovery_results_* 등 산출물이지 로그가 아니다
#   · 날짜가 없는 파일  : creon_launch.log 등 세션 단발 로그 — 날짜 판정이 불가능하므로
#                         "모르면 지우지 않는다"
_LOG_PROTECT_RE = re.compile(r"^(crash_fault|crash_init|crash_test)", re.I)
# 파일명 어디든 YYYYMMDD 가 있으면 그 날짜를 쓴다(20260818_SYSTEM.log,
# retrain_eod_20260818.log, launcher_20260818_084001_2415.log 모두 매칭).
# ⚠ 월 zip(`202605_SYSTEM.zip`)은 6자리라 **여기 안 걸린다** — [1c]가 따로 다룬다.
_LOG_DATE_RE = re.compile(r"(20\d{2})(0[1-9]|1[0-2])([0-3]\d)")
# 일일 채널 로그: 20260818_SYSTEM.log / 회전본 20260515_SYSTEM.log.2026-05-15
_CHANNEL_RE = re.compile(r"^(\d{8})_([A-Za-z_]+)\.log(\..*)?$")
# 월 압축본: 202605_SYSTEM.zip
_ARCHIVE_RE = re.compile(r"^(\d{6})_([A-Za-z_]+)\.zip$")


def _table_exists(conn, name):
    return conn.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?",
        (name,),
    ).fetchone()[0] > 0


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


def log_channel(name):
    """일일 채널 로그면 (date, channel), 아니면 (None, None).

    회전본(`20260515_SYSTEM.log.2026-05-15`)도 같은 채널로 분류한다.
    `retrain_eod_20260818.log` 등 채널 로그가 아닌 날짜 파일은 (None, None) —
    그쪽은 기존 [1b] 190일 컷만 적용된다.
    """
    m = _CHANNEL_RE.match(name)
    if not m:
        return None, None
    try:
        d = datetime.date(int(name[0:4]), int(name[4:6]), int(name[6:8]))
    except ValueError:
        return None, None
    return d, m.group(2)


def compress_candidates(names, today):
    """[1a] 압축 후보를 {(YYYYMM, 채널): [파일명...]}로 묶는다.

    Tier B(_COMPRESS_CHANNELS) 채널이면서 LOG_COMPRESS_DAYS일 이전인 것만.
    Tier A(_RAW_KEEP_CHANNELS)와 비채널 파일은 **구조적으로** 안 걸린다.
    """
    cut = today - datetime.timedelta(days=LOG_COMPRESS_DAYS)
    groups = {}
    for n in sorted(names):
        d, ch = log_channel(n)
        if d is None or ch not in _COMPRESS_CHANNELS:
            continue
        if d >= cut:
            continue
        groups.setdefault((n[:6], ch), []).append(n)
    return groups


def original_delete_target(name, log_cut):
    """[1b] 원본 파일 하나의 처분. 반환: 'delete' | 'protect' | 'nodate' |
    'compress_channel' | 'archive' | 'keep'.

    Tier B 채널 원본은 여기서 지우지 않는다('compress_channel') — 압축이
    실패한 파일을 삭제 단계가 먼저 집어삼키면 영구 소실이기 때문이다.
    수명 관리는 [1a](압축) → [1c](압축본 컷)가 맡는다.
    """
    if _LOG_PROTECT_RE.match(name) or name.lower().endswith(".json"):
        return "protect"
    if _ARCHIVE_RE.match(name):
        return "archive"                  # [1c] 소관
    _, ch = log_channel(name)
    if ch in _COMPRESS_CHANNELS:
        return "compress_channel"         # [1a]/[1c] 소관
    d = log_file_date(name)
    if d is None:
        return "nodate"
    return "delete" if d < log_cut else "keep"


def archive_delete_candidates(names, log_cut):
    """[1c] 삭제할 월 zip 목록. 그 달 **말일**이 컷보다 오래됐을 때만(보수적) —
    달의 일부라도 보관 창에 걸치면 남긴다. HOGA는 면제(머리말 참조)."""
    out = []
    for n in sorted(names):
        m = _ARCHIVE_RE.match(n)
        if not m:
            continue
        if m.group(2) in _ARCHIVE_DELETE_EXEMPT:
            continue
        y, mo = int(n[0:4]), int(n[4:6])
        if not 1 <= mo <= 12:
            continue
        if mo == 12:
            month_end = datetime.date(y, 12, 31)
        else:
            month_end = datetime.date(y, mo + 1, 1) - datetime.timedelta(days=1)
        if month_end < log_cut:
            out.append(n)
    return out


def _remove(path, label):
    """개별 삭제 — 실패는 경고만. 정리가 본업(다음 달 재시도)을 죽이면 안 된다."""
    try:
        os.remove(path)
        return True
    except OSError as e:
        print("  [경고] %s 삭제 실패(무해, 다음 달 재시도): %s — %s"
              % (label, os.path.basename(path), e))
        return False


def compress_into_archives(log_dir, groups, dry_run):
    """[1a] 실행부. 번들마다: zip에 추가 → 재열기 CRC 검증 → 통과 시에만 원본 삭제.

    검증 실패면 원본을 남긴다("모르면 지우지 않는다"). 이전 실행이 '추가 후
    삭제 전'에 중단된 잔재(zip에 같은 이름·같은 크기로 이미 존재)는 원본만
    지운다. 크기가 다르면 손대지 않고 경고만 낸다.
    """
    import zipfile

    total_src_mb = total_zip_mb = 0.0
    for (month, ch), names in sorted(groups.items()):
        zip_name = "%s_%s.zip" % (month, ch)
        zip_path = os.path.join(log_dir, zip_name)
        src_mb = sum(os.path.getsize(os.path.join(log_dir, n))
                     for n in names if os.path.isfile(os.path.join(log_dir, n))) / 1024.0 / 1024.0
        total_src_mb += src_mb
        print("  [%s] %d개 파일 %.1fMB -> %s" % (ch, len(names), src_mb, zip_name))
        for n in names:
            print("    +", n)              # 무엇이 압축되는지 반드시 인쇄한다
        if dry_run:
            continue

        added, dups = [], []
        try:
            with zipfile.ZipFile(zip_path, "a", zipfile.ZIP_DEFLATED,
                                 allowZip64=True) as zf:
                existing = set(zf.namelist())
                for n in names:
                    src = os.path.join(log_dir, n)
                    if not os.path.isfile(src):
                        continue
                    if n in existing:
                        try:
                            same = zf.getinfo(n).file_size == os.path.getsize(src)
                        except KeyError:
                            same = False
                        if same:
                            dups.append(src)   # 이전 실행의 잔재 — 원본만 지운다
                        else:
                            print("  [경고] %s — zip에 다른 크기로 이미 존재. "
                                  "원본·압축본 모두 보존(수동 확인 필요)." % n)
                        continue
                    try:
                        zf.write(src, arcname=n)
                        added.append(src)
                    except OSError as e:
                        print("  [경고] %s 압축 실패(원본 보존): %s" % (n, e))
        except Exception as e:
            print("  [경고] %s 갱신 실패(원본 보존): %s" % (zip_name, e))
            continue

        # 재열기 CRC 전수 검증 — 통과해야만 원본을 지운다.
        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                bad = zf.testzip()
        except Exception as e:
            print("  [경고] %s 검증 실패(원본 보존): %s" % (zip_name, e))
            continue
        if bad is not None:
            print("  [경고] %s CRC 불일치: %s — 원본 보존" % (zip_name, bad))
            continue

        removed = sum(1 for src in added + dups if _remove(src, "압축원본"))
        zip_mb = os.path.getsize(zip_path) / 1024.0 / 1024.0
        total_zip_mb += zip_mb
        print("  -> %s: 신규 %d + 잔재 %d, 원본 %d개 삭제, 압축본 %.1fMB"
              % (zip_name, len(added), len(dups), removed, zip_mb))
    if not dry_run and groups:
        print("  [합계] 원본 %.1fMB -> 압축본 %.1fMB" % (total_src_mb, total_zip_mb))


def main():
    import sqlite3

    from config.settings import LOG_DIR, DB_DIR, SHAP_DB, PREDICTIONS_DB

    dry_run = "--apply" not in sys.argv
    allow_db_prune = "--allow-db-prune" in sys.argv
    now = datetime.datetime.now()

    def cutoff_str(days):
        return (now - datetime.timedelta(days=days)).strftime("%Y-%m-%d")

    def cutoff_dt(days):
        return now - datetime.timedelta(days=days)

    print("=" * 68)
    print("monthly_cleanup.py")
    print("  mode    :", "DRY-RUN" if dry_run else "APPLY")
    print("  DB 정리 :", "허용(--allow-db-prune)" if allow_db_prune
          else "**비활성** — 켜려면 --allow-db-prune")
    print("  now     :", now.strftime("%Y-%m-%d %H:%M"))
    print("=" * 68)

    # ── [0] 장중 가드 ──────────────────────────────────────────────
    # dry-run도 아래 [2]/[3]에서 predictions.db COUNT 전수 스캔을 한다 —
    # 2026-08-10 CB⑤ 자가유발과 같은 유형의 IO다. 장중이면 rc=2로 나간다
    # (campaign_steps가 SKIP(장중차단)으로 집계). 우회: MIREUK_ALLOW_INTRADAY_ANALYSIS=1
    try:
        from utils.analysis_db import guard_intraday
        guard_intraday("monthly_cleanup")
    except ImportError as e:
        print("  [경고] 장중 가드 불가(utils.analysis_db 임포트 실패: %s) — "
              "장중이 아닌지 직접 확인할 것" % e)

    # ── [1a] Tier B 채널 월 단위 압축 (479차 신설) ─────────────────
    print("\n[1a] logs/ -- Tier B 채널", LOG_COMPRESS_DAYS,
          "일 이전 -> 월 zip 압축 (%s)" % ", ".join(sorted(_COMPRESS_CHANNELS)))
    all_names = [os.path.basename(f) for f in glob.glob(os.path.join(LOG_DIR, "*"))
                 if os.path.isfile(f)]   # 하위 디렉터리는 건드리지 않는다
    groups = compress_candidates(all_names, now.date())
    if not groups:
        print("  대상 없음")
    else:
        n_files = sum(len(v) for v in groups.values())
        print("  대상: 번들 %d개 / 파일 %d개" % (len(groups), n_files))
        compress_into_archives(LOG_DIR, groups, dry_run)

    # ── [1b] 원본 로그 삭제 ────────────────────────────────────────
    print("\n[1b] logs/ --", LOG_KEEP_DAYS, "일 이전 원본 삭제 (파일명 날짜 기준)")
    if LOG_KEEP_DAYS < 1:
        # 0을 "전부 지워라"로 읽지 않는다. 킬스위치다.
        print("  [스킵] LOG_KEEP_DAYS < 1 — 킬스위치. 아무것도 지우지 않는다.")
    else:
        log_cut = cutoff_dt(LOG_KEEP_DAYS).date()
        # [1a] 이후 목록을 다시 읽는다(압축으로 지워진 원본 제외).
        names_now = [os.path.basename(f) for f in glob.glob(os.path.join(LOG_DIR, "*"))
                     if os.path.isfile(f)]
        counts = {"protect": 0, "nodate": 0, "compress_channel": 0,
                  "archive": 0, "keep": 0}
        log_files = []
        for n in names_now:
            verdict = original_delete_target(n, log_cut)
            if verdict == "delete":
                log_files.append(os.path.join(LOG_DIR, n))
            else:
                counts[verdict] += 1
        log_size_mb = sum(os.path.getsize(f) for f in log_files) / 1024.0 / 1024.0
        # 탈락 가시화(계측 4원칙 ③): 제외 사유별 개수를 전부 인쇄한다.
        print("  컷오프:", log_cut.isoformat(),
              " / 대상:", len(log_files), "개 파일,", round(log_size_mb, 1), "MB")
        print("  제외: 보호 %d · 날짜없음 %d · 압축채널(수명은 압축본이 관리) %d "
              "· 압축본([1c] 소관) %d · 보관창 내 %d"
              % (counts["protect"], counts["nodate"], counts["compress_channel"],
                 counts["archive"], counts["keep"]))
        for f in sorted(log_files):
            print("    -", os.path.basename(f))     # 지운 것은 반드시 인쇄한다
        if not dry_run and log_files:
            ok = sum(1 for f in log_files if _remove(f, "로그"))
            print("  ->", ok, "/", len(log_files), "개 삭제 완료")

    # ── [1c] 월 압축본 삭제 (479차 신설) ───────────────────────────
    print("\n[1c] logs/ -- 월 zip 중 말일이", LOG_KEEP_DAYS,
          "일 이전인 것 삭제 (HOGA 면제 — 주간회의 결정 전 보수 기본값)")
    if LOG_KEEP_DAYS < 1:
        print("  [스킵] LOG_KEEP_DAYS < 1 — 킬스위치.")
    else:
        log_cut = cutoff_dt(LOG_KEEP_DAYS).date()
        names_now = [os.path.basename(f) for f in glob.glob(os.path.join(LOG_DIR, "*.zip"))
                     if os.path.isfile(f)]
        arch_targets = archive_delete_candidates(names_now, log_cut)
        n_exempt = sum(1 for n in names_now
                       if _ARCHIVE_RE.match(n)
                       and _ARCHIVE_RE.match(n).group(2) in _ARCHIVE_DELETE_EXEMPT)
        print("  대상:", len(arch_targets), "개 / 면제(HOGA):", n_exempt, "개")
        for n in arch_targets:
            print("    -", n)
        if not dry_run and arch_targets:
            ok = sum(1 for n in arch_targets
                     if _remove(os.path.join(LOG_DIR, n), "압축본"))
            print("  ->", ok, "/", len(arch_targets), "개 삭제 완료")

    # ── [2] shap.db ────────────────────────────────────────────────
    _shap_keep = max(SHAP_KEEP_DAYS, _MIN_KEEP_DAYS_DB)
    print("\n[2] shap.db --", _shap_keep, "일 이전 shap_scores 삭제")
    if not allow_db_prune:
        print("  [스킵] DB 행 삭제 비활성 — --allow-db-prune 을 붙여야 후보가 된다.")
    elif os.path.exists(SHAP_DB):
        shap_cut = cutoff_str(_shap_keep)
        with sqlite3.connect(SHAP_DB, timeout=10) as c:
            cnt   = c.execute("SELECT COUNT(*) FROM shap_scores WHERE ts < ?", (shap_cut,)).fetchone()[0]
            total = c.execute("SELECT COUNT(*) FROM shap_scores").fetchone()[0]
        print("  현재:", total, "행  /  삭제 대상 (", shap_cut, "이전):", cnt, "행")
        if not dry_run and cnt > 0:
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
    if not allow_db_prune:
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

        if not dry_run and (p_cnt + ed_cnt + ml_cnt) > 0:
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
    else:
        backup_cut = cutoff_dt(BACKUP_KEEP_DAYS)
        backup_files = [
            f for f in glob.glob(os.path.join(DB_DIR, "*backup*.db"))
            if os.path.isfile(f) and os.path.getmtime(f) < backup_cut.timestamp()
        ]
        backup_size_mb = sum(os.path.getsize(f) for f in backup_files) / 1024.0 / 1024.0
        print("  대상:", len(backup_files), "개 파일,", round(backup_size_mb, 1), "MB")
        for f in backup_files:
            print("    -", os.path.basename(f))
        if not dry_run and backup_files:
            ok = sum(1 for f in backup_files if _remove(f, "백업"))
            print("  ->", ok, "/", len(backup_files), "개 삭제 완료")

    # ── 요약 ───────────────────────────────────────────────────────
    print()
    if dry_run:
        print("[DRY-RUN] 변경 없음. --apply 로 실제 적용하세요.")
    else:
        print("[완료]")
    if not allow_db_prune:
        print("[안내] DB 행 삭제는 비활성입니다. 켜기 전에 "
              "docs/정기점검/보관정책_MW0601-20260818.md 의 근거를 먼저 읽으세요.")


if __name__ == "__main__":
    main()
