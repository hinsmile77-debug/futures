# scripts/restore_raw_features_from_backup.py — 백필 UPDATE로 덮인 라이브 행 복원
"""
[418차] 2026-07-13 `backfill_features.py --update-features` 전체 실행이 라이브 수집
행을 덮어쓴 사고의 부분 복구용.

## 사고 요약

MW0601에서 `--from` 없는 `--update-features`가 실행돼 `ts <= 2026-07-13`인 정규장
행 전체의 features JSON이 통째로 교체됐다. 백필은 OHLCV 파생만 계산할 수 있으므로
실제 수집됐던 호가·수급·옵션·매크로 값이 0.0으로 소실됐다 —
**2026-06-02 ~ 07-13, 29거래일 10,448행**.
근거·전체 수치: `dev_memory/DECISION_LOG.md` 2026-08-02 MW0601 418차.

## 이 스크립트가 하는 일

백업본에 **라이브 상태로 남아 있는 행**을 찾아 현재 DB의 **손상된 행**에 되돌린다.
MW0601 기준 `raw_data.db.bak_20260608_151648`에서 1,446행(06-02·06-04·06-05·06-08)이
복구 가능하다. 06-09 ~ 07-13(9,002행)은 백업 시점 이후라 **복구 불가**다.

## 안전 설계

- **기본이 dry-run**이다. 실제 쓰기는 `--apply` 명시가 필요하다.
- 쓰기 전 대상 DB를 자동 백업한다(`--no-backup`으로 생략 가능).
- **손상된 행에만 쓴다.** 현재 행이 라이브(quality != 0.3)면 건너뛴다 — 이미 정상인
  행을 오래된 백업으로 되돌리는 역행을 막는다.
- ts가 양쪽에 다 있는 행만 대상이다. INSERT는 하지 않는다.

## 사용법

    python scripts/restore_raw_features_from_backup.py --backup data/db/raw_data.db.bak_20260608_151648
    python scripts/restore_raw_features_from_backup.py --backup <경로> --apply

Python 3.7 32-bit 호환
"""
import argparse
import datetime
import json
import logging
import os
import shutil
import sqlite3
import sys
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config.settings import RAW_DATA_DB

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# backfill_features.py와 같은 마커 정의를 쓴다 (import로 단일 출처 유지).
from scripts.backfill_features import BACKFILL_QUALITY_MARKER


def _quality(features_json):
    """features JSON에서 feature_quality_score 추출. 파싱 실패 시 None."""
    try:
        return json.loads(features_json).get("feature_quality_score")
    except Exception:
        return None


def collect_candidates(backup_path, main_path, from_date=None, to_date=None):
    """
    복구 대상 산출.

    반환: (candidates, stats)
      candidates = [(ts, features_json, created_at), ...]  실제로 되돌릴 행
      stats      = 날짜별 집계 dict
    """
    bak = sqlite3.connect(backup_path)
    main = sqlite3.connect(main_path)

    # 현재 DB 상태를 ts -> quality 로 적재 (손상 여부 판정용)
    cur_quality = {}
    for ts, fj in main.execute("SELECT ts, features FROM raw_features"):
        cur_quality[ts] = _quality(fj)

    candidates = []
    stats = defaultdict(lambda: {
        "backup_live": 0,    # 백업본에 라이브로 있는 행
        "restorable": 0,     # 그중 현재 손상돼 있어 되돌릴 행
        "already_ok": 0,     # 현재도 라이브 — 건드리지 않음
        "missing": 0,        # 현재 DB에 ts 없음 — INSERT 안 함
    })

    for ts, fj, ca in bak.execute(
        "SELECT ts, features, created_at FROM raw_features ORDER BY ts"
    ):
        day = ts[:10]
        if from_date and day < from_date:
            continue
        if to_date and day > to_date:
            continue
        if _quality(fj) == BACKFILL_QUALITY_MARKER:
            continue                       # 백업본에서도 백필 행 — 복구할 것이 없다
        s = stats[day]
        s["backup_live"] += 1
        if ts not in cur_quality:
            s["missing"] += 1
            continue
        if cur_quality[ts] != BACKFILL_QUALITY_MARKER:
            s["already_ok"] += 1           # 현재 정상 — 역행 방지
            continue
        s["restorable"] += 1
        candidates.append((ts, fj, ca))

    bak.close()
    main.close()
    return candidates, dict(stats)


def backup_db(db_path):
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = "%s.bak_%s" % (db_path, stamp)
    logger.info("[백업] %s → %s (약 %.0f MB)",
                os.path.basename(db_path), os.path.basename(dst),
                os.path.getsize(db_path) / 1024.0 / 1024.0)
    shutil.copy2(db_path, dst)
    return dst


def main():
    parser = argparse.ArgumentParser(
        description="백업본의 라이브 raw_features 행을 손상된 현재 DB에 복원"
    )
    parser.add_argument("--backup", required=True, metavar="PATH",
                        help="복구원 DB 경로 (예: data/db/raw_data.db.bak_20260608_151648)")
    parser.add_argument("--db", default=RAW_DATA_DB, metavar="PATH",
                        help="복구 대상 DB (기본: config의 RAW_DATA_DB)")
    parser.add_argument("--from", dest="from_date", default=None, metavar="YYYY-MM-DD",
                        help="이 날짜 이후만 복구")
    parser.add_argument("--to", dest="to_date", default=None, metavar="YYYY-MM-DD",
                        help="이 날짜 이전만 복구")
    parser.add_argument("--apply", action="store_true",
                        help="실제 쓰기 (미지정 시 dry-run)")
    parser.add_argument("--no-backup", action="store_true",
                        help="쓰기 전 대상 DB 자동 백업 생략 (권장하지 않음)")
    args = parser.parse_args()

    for p, label in ((args.backup, "백업본"), (args.db, "대상 DB")):
        if not os.path.exists(p):
            logger.error("%s 없음: %s", label, p)
            sys.exit(1)

    logger.info("복구원 : %s", args.backup)
    logger.info("대상   : %s", args.db)

    candidates, stats = collect_candidates(
        args.backup, args.db, args.from_date, args.to_date
    )

    if not stats:
        logger.info("백업본에 라이브 행이 없다 — 복구할 것 없음")
        return

    logger.info("-" * 70)
    logger.info("%-12s %10s %11s %10s %8s", "날짜", "백업라이브", "복구대상", "이미정상", "행없음")
    logger.info("-" * 70)
    tot = defaultdict(int)
    for day in sorted(stats):
        s = stats[day]
        logger.info("%-12s %10d %11d %10d %8d",
                    day, s["backup_live"], s["restorable"], s["already_ok"], s["missing"])
        for k, v in s.items():
            tot[k] += v
    logger.info("-" * 70)
    logger.info("%-12s %10d %11d %10d %8d",
                "합계", tot["backup_live"], tot["restorable"], tot["already_ok"], tot["missing"])

    if not candidates:
        logger.info("복구 대상 0행 — 종료 (현재 DB가 이미 정상이거나 ts 불일치)")
        return

    if not args.apply:
        logger.info("")
        logger.info("[DRY-RUN] 실제 쓰기 없이 종료. 적용하려면 --apply 를 붙일 것.")
        return

    if not args.no_backup:
        backup_db(args.db)

    conn = sqlite3.connect(args.db, timeout=30)
    c = conn.cursor()
    # created_at은 백업본 값을 그대로 되돌린다 — "언제 수집된 행인가"가 손상 판별의
    # 핵심 단서였으므로(418차) 복원 시각으로 덮으면 이력이 또 지워진다.
    c.executemany(
        "UPDATE raw_features SET features=?, created_at=? WHERE ts=?",
        [(fj, ca, ts) for ts, fj, ca in candidates],
    )
    conn.commit()
    conn.close()
    logger.info("=== 복구 완료: %d행 ===", len(candidates))

    # 검증 — 되돌린 행이 실제로 라이브 상태인지 재확인
    conn = sqlite3.connect(args.db)
    still_bad = 0
    for ts, _, _ in candidates:
        row = conn.execute("SELECT features FROM raw_features WHERE ts=?", (ts,)).fetchone()
        if row is None or _quality(row[0]) == BACKFILL_QUALITY_MARKER:
            still_bad += 1
    conn.close()
    if still_bad:
        logger.error("검증 실패 — 여전히 백필 마커인 행 %d개", still_bad)
        sys.exit(3)
    logger.info("검증 통과 — 복구된 %d행 전부 라이브 상태", len(candidates))


if __name__ == "__main__":
    main()
