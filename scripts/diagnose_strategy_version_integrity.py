# scripts/diagnose_strategy_version_integrity.py — 유령버전 진단+정리
"""
strategy_registry.db의 "현재 버전"(strategy_versions.is_current) 포인터가
실제 실거래 기록 버전(config/strategy_params.py의 PARAM_HISTORY 최신 항목)과
어긋나는지 진단하고, 어긋난 경우 정리한다.

배경 (298차, 2026-07-06): qa_strategy_seeder.py --seed가 한 타임스탬프로 남긴
v1.0/v1.1/v1.2 더미 버전 중 v1.2가 is_current로 남았는데, 실거래 PnL은 계속
v1.0으로 기록되고 있었다. 그 결과 live_days가 seed 당시 1건으로 고정돼 판정
로직이 2달간 실거래 성과를 전혀 보지 못했다. 상세 원인·수정 내역은
dev_memory/DECISION_LOG.md 298차 항목 참고.

data/db/strategy_registry.db는 PC별 로컬 파일(gitignore 대상, 멀티PC 간 동기화
안 됨)이라 이 진단은 각 머신에서 개별 실행해야 한다.

사용법:
  python scripts/diagnose_strategy_version_integrity.py             # 진단만 (읽기 전용)
  python scripts/diagnose_strategy_version_integrity.py --fix        # 확인 후 정리
  python scripts/diagnose_strategy_version_integrity.py --fix --yes  # 확인 없이 정리
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import sqlite3
import sys
from datetime import datetime

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


def _print(msg: str) -> None:
    try:
        print(msg)
    except UnicodeEncodeError:
        sys.stdout.buffer.write((msg + "\n").encode("utf-8", errors="replace"))


def _real_active_version() -> str:
    """main.py가 실제로 live_snapshot을 기록할 때 쓰는 버전."""
    from config.strategy_params import PARAM_HISTORY
    if not PARAM_HISTORY:
        return "v1.0"
    return PARAM_HISTORY[-1]["version"]


def _check_cusum_persistence() -> bool:
    """
    param_drift_detector.py에 디스크 영속화(pickle/json 등) 로직이 있는지
    best-effort 정적 스캔. main.py의 EOD 배선(get_drift_detector().update(...))은
    존재하지만(298차 확인), DriftDetector가 인메모리 싱글턴이라 프로세스가
    재시작되면(이 시스템은 매일 재기동되는 운영 구조로 보임) CUSUM 누적이
    리셋될 수 있다. 영속화 로직이 있으면 True(문제 없음), 없으면 False.
    """
    target = os.path.join(_ROOT, "strategy", "param_drift_detector.py")
    try:
        with open(target, encoding="utf-8") as f:
            src = f.read()
    except OSError:
        return True
    return bool(re.search(r"\bpickle\b|json\.(dump|load)|shelve\.", src))


def _live_days(cur: sqlite3.Cursor, version: str) -> int:
    cur.execute(
        "SELECT COUNT(DISTINCT snapshot_date) FROM strategy_live_snapshots WHERE version=?",
        (version,),
    )
    row = cur.fetchone()
    return row[0] if row else 0


def run(db_path: str, fix: bool, assume_yes: bool) -> int:
    from config.strategy_registry import REGISTRY_DB
    db_path = db_path or REGISTRY_DB

    if not os.path.exists(db_path):
        _print(f"[진단] DB 없음: {db_path}")
        return 1

    real_ver = _real_active_version()
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    cur.execute("SELECT version, activated_at FROM strategy_versions WHERE is_current=1")
    row = cur.fetchone()
    if not row:
        _print("[진단] strategy_versions에 is_current=1인 버전이 없음 — 별도 확인 필요.")
        con.close()
        return 1
    cur_ver, cur_activated = row

    real_days = _live_days(cur, real_ver)
    cur_days = _live_days(cur, cur_ver)

    _print("=" * 60)
    _print("  strategy_registry.db 버전 정합성 진단")
    _print("=" * 60)
    _print(f"  PARAM_HISTORY 최신(실운영) 버전 : {real_ver}  (live_days={real_days})")
    _print(f"  DB is_current 버전            : {cur_ver}  (live_days={cur_days})")

    mismatch = real_ver != cur_ver
    if not mismatch:
        _print("  결과: 일치 — 정상.")
    else:
        _print("  결과: 불일치! is_current가 실운영 버전과 다름 (298차와 동일 패턴 의심)")

    if not _check_cusum_persistence():
        _print("-" * 60)
        _print("  [정보] param_drift_detector.py에 디스크 영속화 로직 없음 —")
        _print("  main.py EOD 배선(get_drift_detector().update(...))은 존재하지만")
        _print("  DriftDetector가 인메모리 싱글턴이라, 매일 재기동되는 운영 구조라면")
        _print("  CUSUM 20거래일 누적이 매일 리셋될 수 있음(298차 확인, 정정판")
        _print("  dev_memory/DECISION_LOG.md 참고).")

    if not mismatch:
        con.close()
        return 0

    if not fix:
        _print("-" * 60)
        _print("  정리하려면 --fix 옵션을 붙여 다시 실행하세요.")
        con.close()
        return 1

    # ── phantom 버전 클러스터: is_current 버전과 등록시각이 같은 버전들 ──
    cur.execute(
        "SELECT version FROM strategy_versions WHERE activated_at=? AND version!=?",
        (cur_activated, real_ver),
    )
    phantom_versions = sorted({r[0] for r in cur.fetchall()} | {cur_ver} - {real_ver})

    _print("-" * 60)
    _print(f"  삭제 대상 phantom 버전(등록시각={cur_activated} 공유): {phantom_versions}")

    # 실버전의 같은 날짜 스냅샷도 seed 오염 가능성이 있으나, 진짜 거래일과
    # 우연히 겹칠 위험이 있어 자동 삭제하지 않고 안내만 한다.
    seed_date = cur_activated.split(" ")[0] if cur_activated else None
    if seed_date:
        cur.execute(
            "SELECT daily_pnl FROM strategy_live_snapshots WHERE version=? AND snapshot_date=?",
            (real_ver, seed_date),
        )
        r = cur.fetchone()
        if r:
            _print(
                f"  [참고] 실버전({real_ver})의 동일 날짜({seed_date}) 스냅샷"
                f" daily_pnl={r[0]} — seed 오염일 수 있으나 자동 삭제 안 함,"
                f" 필요시 직접 확인 후 수동 삭제할 것."
            )

    if not assume_yes:
        ans = input("  위 phantom 버전들을 정리할까요? [y/N] ").strip().lower()
        if ans != "y":
            _print("  취소함.")
            con.close()
            return 1

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}.bak_{ts}"
    con.close()
    shutil.copy2(db_path, backup_path)
    _print(f"  백업 완료: {backup_path}")

    con = sqlite3.connect(db_path)
    cur = con.cursor()
    for pv in phantom_versions:
        cur.execute("DELETE FROM strategy_versions WHERE version=?", (pv,))
        cur.execute("DELETE FROM strategy_param_changes WHERE version=?", (pv,))
        cur.execute("DELETE FROM strategy_stage_results WHERE version=?", (pv,))
        cur.execute("DELETE FROM strategy_live_snapshots WHERE version=?", (pv,))

    cur.execute(
        "UPDATE strategy_versions SET is_current=1, deactivated_at=NULL,"
        " previous_version=NULL WHERE version=?",
        (real_ver,),
    )
    con.commit()

    new_days = _live_days(cur, real_ver)
    _print(f"  정리 완료 — {real_ver} is_current 복원, live_days={new_days}")
    _print("  (strategy_events 이력은 감사 기록으로 보존, 삭제하지 않음)")
    con.close()
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default=None, help="strategy_registry.db 경로 (기본: config 기본값)")
    ap.add_argument("--fix", action="store_true", help="불일치 발견 시 정리 수행")
    ap.add_argument("--yes", action="store_true", help="확인 프롬프트 생략")
    args = ap.parse_args()
    return run(args.db, args.fix, args.yes)


if __name__ == "__main__":
    sys.exit(main())
