"""[MW0601 701차] 연구용 장후 사본 — 원천 DB 의 핵심 테이블을 삭제 없는 아카이브로 떠 둔다.

왜 필요한가
-----------
`ensemble_decisions`(predictions.db)는 분 단위 국면 라벨(`micro_regime`)·사이징 계보·
캠페인 원자재를 담는 유일한 원천이다. 그런데 predictions.db 는 gitignore 대상이고
백업은 7일치뿐이며, `scripts/monthly_cleanup.py --allow-db-prune` 이 켜지면 190일
이전 행이 지워진다. 가격움직임 패턴 연구(docs/가격움직임패턴연구/)는 수백 거래일
단위 표본이 필요하므로, 원천 정리 정책과 무관하게 **지워지지 않는 사본**이 필요하다.
(2026-10-21 실측: `regime_history` 30일 정리는 캐시만 지우고, 같은 라벨이
`ensemble_decisions.micro_regime` 에 2026-05-08부터 남아 있다 — 6,902/6,902분 일치.)

동작 규칙 — 사본은 원천을 「따라가되 잃지 않는다」
--------------------------------------------------
1. 마감된 날짜만 다룬다: 오늘 이전 날짜 + (15:35 이후라면) 오늘.
2. 사본에 없는 날짜 → 복사(`added`).
3. 원천 행 수 > 사본 행 수인 날짜 → 그 날만 다시 복사(`refreshed`, 늦게 들어온 행 반영).
4. 원천 행 수 < 사본 행 수, 또는 원천에서 사라진 날짜 → **사본을 건드리지 않는다**
   (`kept`). 원천 정리·중복 제거로 줄어든 것이며, 사본은 지우지 않는 것이 존재 이유다.
5. 원천에 새 컬럼이 생기면 사본 테이블에 `ALTER TABLE ADD COLUMN` 으로 따라 붙인다.
6. 복사한 날짜는 즉시 날짜별 행 수를 대조한다. 불일치 시 rc=1.
7. 실행마다 `snapshot_runs` 에 무엇을 몇 건 옮겼는지 남긴다(계측 4원칙 ③).

장중(08:45–15:35)에는 `guard_intraday` 로 rc=2 종료한다 — 첫 실행은 원천 전량을 읽는다.

사용:
    python scripts/research_snapshot.py            # 증분 사본
    python scripts/research_snapshot.py --status   # 사본 현황만 출력(쓰기 없음)
"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.dll_bootstrap import ensure_conda_dll_path   # 448차 — numpy 미사용이나 진입점 규약
ensure_conda_dll_path()

import argparse
import datetime
import json
import sqlite3

from utils.analysis_db import guard_intraday

DB_DIR = os.path.join(_ROOT, "data", "db")
ARCHIVE_DB = os.path.join(_ROOT, "data", "research", "research_archive.db")

# 사본 대상: 테이블명 → (원천 DB 파일, 날짜를 뽑을 ts 컬럼)
TABLES = {
    "ensemble_decisions": ("predictions.db", "ts"),
}

SESSION_CLOSE = datetime.time(15, 35)


def _closed_cutoff(now=None):
    """이 날짜 '미만'이 마감된 날짜다. 15:35 이후면 오늘도 포함."""
    now = now or datetime.datetime.now()
    d = now.date()
    if now.time() >= SESSION_CLOSE:
        d = d + datetime.timedelta(days=1)
    return d.isoformat()


def _ro_uri(path):
    return "file:%s?mode=ro" % path.replace("\\", "/").replace("?", "%3f").replace("#", "%23")


def _ensure_meta(con):
    con.execute("""
        CREATE TABLE IF NOT EXISTS snapshot_runs (
            run_ts      TEXT NOT NULL,
            tbl         TEXT NOT NULL,
            src_db      TEXT NOT NULL,
            src_days    INTEGER,
            dst_days    INTEGER,
            added       INTEGER,
            refreshed   INTEGER,
            kept        INTEGER,
            rows_copied INTEGER,
            new_columns TEXT,
            detail      TEXT
        )""")


def _sync_schema(con, tbl):
    """사본 테이블을 원천 스키마에 맞춘다. 추가된 컬럼명 목록을 반환."""
    src_cols = con.execute("PRAGMA src.table_info(%s)" % tbl).fetchall()
    if not src_cols:
        raise RuntimeError("원천에 테이블 없음: %s" % tbl)
    exists = con.execute(
        "SELECT 1 FROM main.sqlite_master WHERE type='table' AND name=?", (tbl,)).fetchone()
    if not exists:
        # 제약은 옮기지 않는다(원천 id 를 그대로 보존하고 싶어서 PK 만 유지)
        defs = []
        for _cid, name, ctype, _nn, _dflt, pk in src_cols:
            d = '"%s" %s' % (name, ctype or "")
            if pk == 1 and len([c for c in src_cols if c[5]]) == 1:
                d += " PRIMARY KEY"
            defs.append(d)
        con.execute('CREATE TABLE main."%s" (%s)' % (tbl, ", ".join(defs)))
        return None          # 신규 생성 — 「추가된 컬럼」과 구분한다
    dst_names = {r[1] for r in con.execute('PRAGMA main.table_info("%s")' % tbl)}
    added = []
    for _cid, name, ctype, *_ in src_cols:
        if name not in dst_names:
            con.execute('ALTER TABLE main."%s" ADD COLUMN "%s" %s' % (tbl, name, ctype or ""))
            added.append(name)
    return added


def _day_counts(con, schema, tbl, ts_col, cutoff):
    return dict(con.execute(
        'SELECT substr("%s",1,10) d, COUNT(*) FROM %s."%s" WHERE "%s" < ? GROUP BY d'
        % (ts_col, schema, tbl, ts_col), (cutoff,)).fetchall())


def snapshot_table(con, tbl, src_db, ts_col, cutoff, run_ts):
    new_cols = _sync_schema(con, tbl)
    ts_idx = "ix_%s_%s" % (tbl, ts_col)
    con.execute('CREATE INDEX IF NOT EXISTS main."%s" ON "%s"("%s")' % (ts_idx, tbl, ts_col))

    src = _day_counts(con, "src", tbl, ts_col, cutoff)
    dst = _day_counts(con, "main", tbl, ts_col, cutoff)
    cols = [r[1] for r in con.execute("PRAGMA src.table_info(%s)" % tbl)]
    col_sql = ", ".join('"%s"' % c for c in cols)

    added, refreshed, kept_less, kept_gone = [], [], [], []
    for d, n in sorted(src.items()):
        m = dst.get(d, 0)
        if m == 0:
            added.append(d)
        elif n > m:
            refreshed.append(d)
        elif n < m:
            kept_less.append((d, n, m))
    kept_gone = sorted(d for d in dst if d not in src)

    rows = 0
    mismatch = []
    for d in added + refreshed:
        nxt = (datetime.date.fromisoformat(d) + datetime.timedelta(days=1)).isoformat()
        con.execute("SAVEPOINT day")
        con.execute('DELETE FROM main."%s" WHERE "%s" >= ? AND "%s" < ?' % (tbl, ts_col, ts_col), (d, nxt))
        con.execute(
            'INSERT INTO main."%s" (%s) SELECT %s FROM src."%s" WHERE "%s" >= ? AND "%s" < ?'
            % (tbl, col_sql, col_sql, tbl, ts_col, ts_col), (d, nxt))
        got = con.execute('SELECT COUNT(*) FROM main."%s" WHERE "%s" >= ? AND "%s" < ?'
                          % (tbl, ts_col, ts_col), (d, nxt)).fetchone()[0]
        if got != src[d]:
            con.execute("ROLLBACK TO day")
            mismatch.append((d, src[d], got))
        else:
            rows += got
        con.execute("RELEASE day")
    con.commit()

    dst_days = con.execute('SELECT COUNT(DISTINCT substr("%s",1,10)) FROM main."%s"'
                           % (ts_col, tbl)).fetchone()[0]
    detail = {
        "kept_src_fewer": kept_less[:50], "kept_src_fewer_n": len(kept_less),
        "kept_src_gone": kept_gone[:50], "kept_src_gone_n": len(kept_gone),
        "mismatch": mismatch, "cutoff": cutoff, "created": new_cols is None,
    }
    con.execute("INSERT INTO snapshot_runs VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (run_ts, tbl, src_db, len(src), dst_days, len(added), len(refreshed),
                 len(kept_less) + len(kept_gone), rows, ",".join(new_cols or []) or None,
                 json.dumps(detail, ensure_ascii=False)))
    con.commit()
    print("[ResearchSnapshot] %s ← %s | 원천 %d일 · 사본 %d일 | 신규 %d일 · 갱신 %d일 · "
          "보존(원천감소 %d · 원천소실 %d) | 복사 %d행%s"
          % (tbl, src_db, len(src), dst_days, len(added), len(refreshed),
             len(kept_less), len(kept_gone), rows,
             " | 사본 테이블 신규 생성" if new_cols is None else
             ((" | 새 컬럼 %d개: %s" % (len(new_cols), ", ".join(new_cols))) if new_cols else "")))
    if kept_less:
        print("  ⚠ 원천 행 수가 사본보다 적은 날 %d일 — 사본 유지(예: %s)"
              % (len(kept_less), kept_less[:3]))
    if mismatch:
        print("  ✖ 복사 후 행 수 불일치 %d일 — 그 날은 롤백: %s" % (len(mismatch), mismatch[:5]))
    return not mismatch


def status(archive=ARCHIVE_DB):
    if not os.path.exists(archive):
        print("[ResearchSnapshot] 사본 없음:", archive)
        return 0
    con = sqlite3.connect(_ro_uri(archive), uri=True)
    for tbl, (_db, ts_col) in TABLES.items():
        r = con.execute('SELECT COUNT(*), COUNT(DISTINCT substr("%s",1,10)), MIN("%s"), MAX("%s") FROM "%s"'
                        % (ts_col, ts_col, ts_col, tbl)).fetchone()
        print("[ResearchSnapshot] %s: %d행 · %d일 · %s ~ %s" % ((tbl,) + tuple(r)))
    last = con.execute("SELECT run_ts, tbl, added, refreshed, kept, rows_copied FROM snapshot_runs "
                       "ORDER BY rowid DESC LIMIT 3").fetchall()
    for x in last:
        print("  최근 실행:", x)
    print("  크기: %.1f MB" % (os.path.getsize(archive) / 1e6))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--archive", default=ARCHIVE_DB)
    args = ap.parse_args(argv)
    if args.status:
        return status(args.archive)

    guard_intraday("research_snapshot")
    os.makedirs(os.path.dirname(args.archive), exist_ok=True)
    run_ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cutoff = _closed_cutoff()
    ok = True
    for tbl, (src_db, ts_col) in TABLES.items():
        src_path = os.path.join(DB_DIR, src_db)
        if not os.path.exists(src_path):
            print("[ResearchSnapshot] 원천 없음 — 스킵:", src_path)
            ok = False
            continue
        # ATTACH 에 mode=ro URI 를 쓰려면 이 커넥션도 URI 모드로 열어야 한다
        con = sqlite3.connect("file:%s" % args.archive.replace("\\", "/"), uri=True, timeout=30)
        try:
            _ensure_meta(con)
            con.execute("ATTACH DATABASE ? AS src", (_ro_uri(src_path),))
            ok = snapshot_table(con, tbl, src_db, ts_col, cutoff, run_ts) and ok
        finally:
            con.close()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
