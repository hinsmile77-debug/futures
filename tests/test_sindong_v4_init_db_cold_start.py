"""[MW0602 Sindong-V4 / 2026-10-25] init_all_dbs 콜드 기동 회귀 테스트.

계기: 08:40 예약 기동의 `[FaultHandler] 활성화 → [System] DB 초기화 완료` 구간이 17~62초(로그 104회).
원인은 `_migrate_predictions_db` 의 확률 컬럼 백필 UPDATE — WHERE 컬럼에 인덱스가 없어 매 기동
predictions 전체(661MB)를 훑었다(warm 0.55s / cold 9.2s 재현). 컬럼을 방금 추가했을 때만 백필한다.

  C1  확률 컬럼이 없던 구 DB → 컬럼 추가 + 기존 행 백필(마이그레이션 본래 목적 유지).
  C2  컬럼이 이미 있으면 UPDATE 를 실행하지 않는다(전체 스캔 금지).
"""
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import utils.db_utils as d  # noqa: E402


def _old_db(path):
    c = sqlite3.connect(path)
    c.execute("CREATE TABLE predictions (id INTEGER PRIMARY KEY, ts TEXT, horizon TEXT, "
              "direction INTEGER, confidence REAL)")
    c.execute("INSERT INTO predictions (ts, horizon, direction, confidence) VALUES "
              "('2026-04-28 09:00:00', '1m', 1, 0.6)")
    c.commit()
    c.close()


def test_C1_old_schema_gets_columns_and_backfill(tmp_path, monkeypatch):
    db = str(tmp_path / "p.db")
    _old_db(db)
    monkeypatch.setattr(d, "PREDICTIONS_DB", db)
    d._migrate_predictions_db()
    c = sqlite3.connect(db)
    up, dn, fl = c.execute("SELECT up_prob, down_prob, flat_prob FROM predictions").fetchone()
    assert abs(up - 0.6) < 1e-9 and abs(dn - 0.2) < 1e-9 and abs(fl - 0.2) < 1e-9


def test_C2_existing_columns_skip_full_scan_update(tmp_path, monkeypatch):
    db = str(tmp_path / "p.db")
    _old_db(db)
    monkeypatch.setattr(d, "PREDICTIONS_DB", db)
    d._migrate_predictions_db()                     # 1차: 컬럼 추가 + 백필
    seen = []
    orig = d.get_conn

    class _Spy(object):
        def __init__(self, conn):
            self._c = conn

        def execute(self, sql, *a):
            seen.append(" ".join(sql.split()))
            return self._c.execute(sql, *a)

    from contextlib import contextmanager

    @contextmanager
    def _spy_conn(path, timeout=10.0):
        with orig(path, timeout) as conn:
            yield _Spy(conn)

    monkeypatch.setattr(d, "get_conn", _spy_conn)
    d._migrate_predictions_db()                     # 2차: 컬럼이 이미 있다
    assert not any(s.startswith("UPDATE predictions") for s in seen), seen
