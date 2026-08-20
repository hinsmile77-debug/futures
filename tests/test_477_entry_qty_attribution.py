"""[MW0602 477차 후속 / F-1] `ensemble_decisions` 진입수량 귀속 분리 회귀 테스트.

────────────────────────────────────────────────────────────────────────────
배경 (상세: docs/정기점검/매일점검/MW0602-20260820-점검리포트.md §1p 1-1)
────────────────────────────────────────────────────────────────────────────
`ensemble_decisions.entry_qty`는 **실제 진입 계약수가 아니다** — 증거금 캡
이전의 산출 수량(_qty_display)이다. [MarginCap] 발생일에는 실체결(_qty_auto)
보다 1계약 크게 남는다(0820 전수 대사: 140포지션 중 6건, 전부 그런 날).
461차 mdd_pct 사고와 같은 "같은 이름이 다른 것을 센다" 유형이며, 실전 전환
기준 ⑧ 해제 시 [28] sizing_inversion_watch의 입력이 이 오차를 그대로 받는다.

수정은 **새 축 신설**이다 — `entry_qty` 의미를 바꾸면 2026-08-20을 경계로
같은 컬럼의 시계열이 불연속이 된다(계측 4원칙 ①).

지키는 불변식:
  T1  main.py가 `entry_qty_final = int(_qty_auto)`를 저장하고,
      `entry_qty = int(_qty_display)`는 종전 그대로다(기존 축 무변경).
  T2  qty_display != qty_auto 인 스냅샷에서 DB의 `entry_qty_final == qty_auto`,
      `entry_qty == qty_display` — 두 축이 실제로 갈린다.
  T3  키 부재(구버전 호출부)는 NULL — 0이 아니다(계측 4원칙 ②).
  T4  컬럼 부재 구세대 DB에서 마이그레이션 후 INSERT 성공 + 컬럼 수 == 플레이스홀더 수.

실행: python tests/test_477_entry_qty_attribution.py   (COM/브로커 불필요)
"""

import inspect
import os
import re
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

FAILURES = []


def check(name, cond):
    print("[%s] %s" % ("OK" if cond else "FAIL", name))
    if not cond:
        FAILURES.append(name)


def test_t1_main_wiring():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(root, "main.py"), encoding="utf-8") as fh:
        src = fh.read()
    check("T1: entry_qty_final = _qty_auto (증거금 캡 이후) 저장",
          'decision["entry_qty_final"]    = int(_qty_auto)' in src)
    check("T1: entry_qty = _qty_display (산출 수량) - 기존 축 무변경",
          'decision["entry_qty"]          = int(_qty_display)' in src)
    # 캡핑 주석의 전제(“_qty_display는 그대로, _qty_auto만 캡핑”)가 살아 있는지
    check("T1: 증거금 캡은 _qty_auto에만 적용 (_ts_margin_capped_qty)",
          "_qty_auto = _ts_margin_capped_qty(" in src)


def test_t2_t3_db_roundtrip():
    import utils.db_utils as dbu
    import learning.prediction_buffer as pb

    tmp = tempfile.mkdtemp(prefix="qdq_477f1_")
    db_path = os.path.join(tmp, "predictions.db")
    _o_dbu, _o_pb = dbu.PREDICTIONS_DB, pb.PREDICTIONS_DB
    try:
        dbu.PREDICTIONS_DB = pb.PREDICTIONS_DB = db_path
        dbu.init_predictions_db()

        con = sqlite3.connect(db_path)
        cols = {r[1] for r in con.execute("PRAGMA table_info(ensemble_decisions)")}
        check("T2: entry_qty_final 컬럼 생성", "entry_qty_final" in cols)

        buf = pb.PredictionBuffer()
        base = dict(sigma_at_t=0.0, horizon_proba={}, features_clean={},
                    regime="NEUTRAL", micro_regime="NORMAL")
        # 2026-08-20 10:49 실측 케이스: 산출 3계약 → 증거금상한 2계약 체결
        buf.save_step9_batch(ts="2026-08-20 10:49:00",
                             decision={"entry_qty": 3, "entry_qty_final": 2}, **base)
        # 캡 미발동 분 — 두 축이 같은 값
        buf.save_step9_batch(ts="2026-08-20 10:50:00",
                             decision={"entry_qty": 1, "entry_qty_final": 1}, **base)
        # 구버전 호출부(키 부재) — NULL이어야 한다
        buf.save_step9_batch(ts="2026-08-20 10:51:00",
                             decision={"entry_qty": 2}, **base)

        got = {r[0]: (r[1], r[2]) for r in con.execute(
            "SELECT ts, entry_qty, entry_qty_final FROM ensemble_decisions")}
        con.close()
        check("T2: 3행 저장", len(got) == 3)
        check("T2: 캡 발동 분 - entry_qty=3(산출) vs entry_qty_final=2(실체결)",
              got["2026-08-20 10:49:00"] == (3, 2))
        check("T2: 캡 미발동 분 - 두 축 일치",
              got["2026-08-20 10:50:00"] == (1, 1))
        check("T3: 키 부재(구버전) → entry_qty_final NULL (0이 아니다)",
              got["2026-08-20 10:51:00"] == (2, None))
    finally:
        dbu.PREDICTIONS_DB, pb.PREDICTIONS_DB = _o_dbu, _o_pb


def test_t4_migration_and_arity():
    import utils.db_utils as dbu
    import learning.prediction_buffer as pb

    tmp = tempfile.mkdtemp(prefix="qdq_477f1_mig_")
    db_path = os.path.join(tmp, "predictions.db")
    _o_dbu, _o_pb = dbu.PREDICTIONS_DB, pb.PREDICTIONS_DB
    try:
        dbu.PREDICTIONS_DB = pb.PREDICTIONS_DB = db_path
        dbu.init_predictions_db()
        # 구세대 DB 재현: 컬럼을 뺀 사본으로 갈아끼운다
        con = sqlite3.connect(db_path)
        con.execute("ALTER TABLE ensemble_decisions RENAME TO _ed_new")
        cols = [r[1] for r in con.execute("PRAGMA table_info(_ed_new)")
                if r[1] != "entry_qty_final"]
        con.execute("CREATE TABLE ensemble_decisions AS SELECT %s FROM _ed_new WHERE 0"
                    % ", ".join(cols))
        con.execute("DROP TABLE _ed_new")
        con.commit(); con.close()

        # 마이그레이션이 컬럼을 되살리는가
        dbu._migrate_ensemble_decisions_db()
        con = sqlite3.connect(db_path)
        cols2 = {r[1] for r in con.execute("PRAGMA table_info(ensemble_decisions)")}
        check("T4: 컬럼 부재 DB → 마이그레이션 후 entry_qty_final 존재",
              "entry_qty_final" in cols2)

        buf = pb.PredictionBuffer()
        buf.save_step9_batch(ts="2026-08-20 10:49:00",
                             decision={"entry_qty": 3, "entry_qty_final": 2},
                             sigma_at_t=0.0, horizon_proba={}, features_clean={},
                             regime="NEUTRAL", micro_regime="NORMAL")
        row = con.execute("SELECT entry_qty, entry_qty_final FROM ensemble_decisions"
                          ).fetchone()
        con.close()
        check("T4: 마이그레이션 직후 INSERT 성공", row == (3, 2))

        # INSERT arity — 컬럼 수 == 플레이스홀더 수 (471차 T5와 같은 검사)
        psrc = inspect.getsource(pb.PredictionBuffer.save_step9_batch)
        i = psrc.find("INSERT OR IGNORE INTO ensemble_decisions")
        stmt = psrc[i:psrc.find('"""', i + 10)]
        body = stmt[stmt.find("(") + 1:stmt.rfind(") VALUES")]
        n_cols = len([c for c in re.split(r"[,\s]+", body) if c])
        n_ph = stmt[stmt.rfind("VALUES"):].count("?")
        check("T4: 컬럼 수 == 플레이스홀더 수 (%d)" % n_cols, n_cols == n_ph)
    finally:
        dbu.PREDICTIONS_DB, pb.PREDICTIONS_DB = _o_dbu, _o_pb


if __name__ == "__main__":
    _fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in _fns:
        try:
            fn()
        except Exception as e:
            FAILURES.append("%s: %r" % (fn.__name__, e))
            print("[FAIL] %s: %r" % (fn.__name__, e))
    print("-" * 60)
    if FAILURES:
        print("실패 %d건: %s" % (len(FAILURES), FAILURES))
        sys.exit(1)
    print("전부 통과")
