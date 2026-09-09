# -*- coding: utf-8 -*-
"""[MW0602 538차 후속 / 1-3] EOD DB pruning 실패 진단 로그 — 회귀 테스트.

────────────────────────────────────────────────────────────────────────────
배경 (상세: 0907 리포트 1-3 · dev_memory/NEXT_TODO.md `1-3` · `O-58`)
────────────────────────────────────────────────────────────────────────────
`prune_raw_data_db()` 가 2026-08-31·09-07 두 번 연속 `database table is locked`
로 실패했다(507차 사전등록 "2주 연속이면 P1 승격" 조건 충족). 그런데 그 실패
로그로는 **어느 테이블에서 멈췄는지조차** 알 수 없었다:

  ① `_prune_once` 가 진행 기록 `_detail` 을 **성공 경로에서만** 반환해, 예외가
     나는 순간 부분 진행이 통째로 사라진다.
  ② 그래서 `대상=` 은 늘 폴백 상수 `_tables` 를 찍었고, 그 상수는 533차가 추가한
     `session_bars` 가 빠진 **낡은 목록**이었다. 아무것도 측정하지 않았는데
     "측정된 대상"처럼 보인다 — 계측 4원칙 ④ 위반.

🔴 이 Fix 는 **기록만** 늘린다. 재시도 횟수·`timeout=15`·반환값 계약·로그 태그
   `[Retrain]`/`[GBM]` 전부 **무변경**이다(492차 F-8 계약을 그대로 승계).
   원인을 고치지 않는다 — **볼 수 있는 것만** 늘렸다("계측 먼저, 그다음 배선").

지키는 불변식:
  T1  실패해도 진행 기록이 남는다 — 어느 테이블에서 멈췄는지 `대상=` 에 보인다.
  T2  실패 시 반환은 **0**(492차 F-8 계약 승계) — 커밋 안 된 행을 세지 않는다.
  T3  진단 1줄이 나온다 — 락종류 · 마지막단계 · 점유 증거(스레드/커넥션/WAL/journal).
  T4  🔴 폴백이 데이터로 위장하지 않는다 — 진행이 없으면 `(진행 없음)` 이지,
      낡은 테이블 목록이 아니다. **이 검사가 깨지는 날이 ②가 되살아난 날이다.**
  T5  🔴 [552차] **성공 경로** — 삭제 행수를 반환하고 `checkpoint:ok` 까지 간다.
  T6  🔴 [552차] 소스 불변식 — `wal_checkpoint` 가 `_prune_once` **밖**에 있다.
  T9  🔴 [552차] 커밋 후 체크포인트가 실패해도 삭제 행수를 0으로 되돌리지 않는다.
  T7  락종류 분류 문구 — SQLITE_LOCKED 는 busy_timeout 이 **듣지 않는다**는
      사실을 로그가 직접 말한다.
  T8  재현 4/4 — journal 모드(delete/wal)도, 지울 행의 유무도 무관하다.

────────────────────────────────────────────────────────────────────────────
🔴 진단을 붙이자마자 원인이 드러났다 (2026-09-07, 이 테스트가 잡아냈다)
────────────────────────────────────────────────────────────────────────────
리포트 1-3 의 가설은 *"매주 월요일 15:40 에 다른 커넥션/스레드가 물고 있을
가능성"* 이었다. **그 가설은 틀렸다.** 외부 점유가 하나도 없는 깨끗한 임시 DB
에서도 같은 `database table is locked` 가 재현된다(T5) — 원인은
`PRAGMA wal_checkpoint(PASSIVE)` 를 **앞선 DELETE 들이 아직 커밋되지 않은**
쓰기 트랜잭션 안에서 호출하는 것이다. 그래서 `timeout=15` 도 1초 뒤 재시도도
처음부터 듣지 않는 레버였다.

로그 실측도 일치한다 — 기록이 남은 **4회 전부(2026-08-10·08-24·08-31·09-07)
실패**이며 성공한 적이 없다. 즉 `prune_raw_data_db()` 는 도입 이래 한 번도
실제로 정리한 적이 없는 **죽은 유지보수 경로**다(FP-CRITICAL 죽은 게이트 ·
TOX 죽은 섀도와 같은 계열). 0824 의 `3,810행 삭제` 는 492차가 이미 지적한
거짓 성공이다.

🔴 **[MW0602 552차] 2026-09-09 사용자 승인으로 반영됐다.** 체크포인트를 커밋·
  close **이후 별도 커넥션**으로 옮겼다(`_checkpoint()`). 그래서 T5/T6 는
  실패 고정에서 **성공 경로 불변식으로 교체**됐고, 커밋 후 체크포인트가
  실패해도 삭제 행수를 0으로 되돌리지 않는다는 T9 가 추가됐다.
  반영 전 실 DB 복사본 검증: `12,954행 삭제` · `checkpoint:ok` ·
  `integrity_check ok` · cutoff 이전 잔존 0 (라이브 DB 미접촉).
  ⚠ T8 은 그대로 둔다 — 그것은 우리 코드가 아니라 **SQLite 자체의 성질**
  (쓰기 트랜잭션 안에서는 체크포인트가 막힌다)을 고정하며, 그 성질이 바로
  체크포인트를 `_prune_once` 안으로 되돌리면 안 되는 이유다.

⚠ 실 DB 격리: 전부 임시 경로 전용이다. `config.settings.RAW_DATA_DB` 를 임시
  파일로 갈아끼운 뒤 원복한다 — 라이브 `data/db/raw_data.db` 를 절대 건드리지
  않는다([[feedback_isolate_stateful_verification]]).

실행: python tests/test_538_prune_lock_diagnostics.py   (COM/브로커 불필요)
"""

import io
import logging
import os
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

import config.settings as S            # noqa: E402
from learning.batch_retrainer import BatchRetrainer  # noqa: E402

FAILURES = []
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# `prune_raw_data_db` 는 `self` 를 쓰지 않는다 — 무거운 __init__ 을 피해 평함수로 부른다.
_PRUNE = BatchRetrainer.__dict__["prune_raw_data_db"]

OLD = "2020-01-01 09:00:00"            # cutoff(52주 전)보다 확실히 오래된 값
NEW = "2099-01-01 09:00:00"            # 남아야 하는 값


def check(name, cond):
    print("[%s] %s" % ("OK" if cond else "FAIL", name))
    if not cond:
        FAILURES.append(name)


def _read(rel):
    return io.open(os.path.join(ROOT, rel), encoding="utf-8").read()


class _Capture(logging.Handler):
    """`learning.batch_retrainer` 로거가 뱉는 줄을 모은다."""

    def __init__(self):
        logging.Handler.__init__(self)
        self.lines = []

    def emit(self, record):
        try:
            self.lines.append(record.getMessage() % record.args
                              if record.args else record.getMessage())
        except Exception:
            self.lines.append(record.getMessage())

    def text(self):
        return "\n".join(self.lines)


def _build_db(path, view_table=None):
    """임시 raw_data.db — `view_table` 로 지정한 이름은 뷰로 만들어 DELETE 를 실패시킨다.

    실패를 만드는 데 뷰를 쓰는 이유: 진짜 락(SQLITE_BUSY)을 걸면 `timeout=15` 를
    2회 기다려 테스트가 30초 넘게 걸린다. 우리가 고정하려는 것은 **락 자체가
    아니라 실패했을 때 무엇이 기록되는가** 이므로, 즉시·결정적으로 실패하는
    `OperationalError` 면 충분하다.
    """
    conn = sqlite3.connect(path)
    for t in ("raw_features", "raw_candles", "raw_features_horizon", "session_bars"):
        if t == view_table:
            continue
        conn.execute("CREATE TABLE %s (ts TEXT, v INTEGER)" % t)
        conn.execute("INSERT INTO %s VALUES (?, 1)" % t, (OLD,))
        conn.execute("INSERT INTO %s VALUES (?, 2)" % t, (NEW,))
    if view_table:
        # 뷰는 DELETE 불가 → OperationalError("cannot modify ... it is a view")
        conn.execute("CREATE TABLE _src (ts TEXT, v INTEGER)")
        conn.execute("INSERT INTO _src VALUES (?, 1)", (OLD,))
        conn.execute("CREATE VIEW %s AS SELECT * FROM _src" % view_table)
    conn.commit()
    conn.close()


def _run(view_table=None):
    """격리된 임시 DB에서 1회 실행하고 (반환값, 로그전문) 을 돌려준다."""
    tmp = tempfile.mkdtemp(prefix="t538_")
    path = os.path.join(tmp, "raw_data.db")
    _build_db(path, view_table=view_table)

    logger = logging.getLogger("LEARNING")   # batch_retrainer.py:61
    cap = _Capture()
    logger.addHandler(cap)
    prev_level, logger.level = logger.level, logging.INFO
    prev_db = S.RAW_DATA_DB
    S.RAW_DATA_DB = path                      # 함수 안에서 import 하므로 이걸 본다
    try:
        got = _PRUNE(None, keep_weeks=52)
    finally:
        S.RAW_DATA_DB = prev_db               # 🔴 라이브 경로 원복
        logger.removeHandler(cap)
        logger.level = prev_level
    return got, cap.text(), path


# ── 실패 경로 ────────────────────────────────────────────────────────────────

def test_t1_t2_t3_failure_records_progress():
    # raw_candles(2번째 대상)를 뷰로 만들어 "1개는 성공, 2번째에서 실패"를 만든다
    got, log, _ = _run(view_table="raw_candles")

    check("T2: 실패 시 반환 0 (492차 F-8 계약 승계, got=%r)" % got, got == 0)
    check("T1: 성공한 앞 테이블이 기록에 남는다", "raw_features:1" in log)
    check("T1: 멈춘 테이블이 이름으로 지목된다", "raw_candles:" in log)
    check("T1: 실패 사유가 그 테이블 옆에 붙는다", "is a view" in log)

    check("T3: 진단 줄이 나온다", "[Retrain] DB pruning 진단:" in log)
    check("T3: 락종류를 분류한다", "락종류=" in log)
    check("T3: 마지막 단계를 지목한다", "마지막단계=raw_candles:" in log)
    for field in ("스레드=", "열린커넥션=", "wal=", "shm=", "journal="):
        check("T3: 점유 증거 %s" % field, field in log)

    # 뷰 실패는 락이 아니다 — 억지로 LOCKED/BUSY 로 분류하면 안 된다(오분류 금지)
    check("T3: 락이 아닌 실패는 '기타'로 분류", "락종류=기타(OperationalError)" in log)


def test_t4_no_placeholder_masquerading_as_data():
    """🔴 진행이 0인 실패에서 낡은 테이블 목록을 '대상'인 척 찍지 않는다."""
    got, log, _ = _run(view_table="raw_features")   # 첫 대상부터 실패

    check("T4: 반환 0", got == 0)
    check("T4: 진행 없음을 진행 없음이라 쓴다", "(진행 없음)" in log
          or "raw_features:" in log)
    # 종전 폴백 상수는 `session_bars` 가 빠진 낡은 목록이었다 — 다시 나오면 안 된다
    check("T4: 낡은 폴백 목록이 되살아나지 않았다",
          "대상=raw_features,raw_candles,raw_features_horizon " not in log
          and "대상=raw_features,raw_candles,raw_features_horizon\n" not in log)
    src = _read("learning/batch_retrainer.py")
    check("T4: 폴백 상수 자체가 제거됨",
          '_tables = "raw_features,raw_candles,raw_features_horizon"' not in src)


# ── 🔴 근본원인 고정 ─────────────────────────────────────────────────────────

def test_t5_t6_success_path_after_fix():
    """🔴 [MW0602 552차 / 1-3 승인 반영] 이제 **성공한다** — 성공 경로를 고정한다.

    538차까지 이 검사는 일부러 **실패를 고정**하고 있었다("이 검사가 깨지는 날이
    근본원인이 고쳐진 날이다"). 2026-09-09 사용자 승인으로 체크포인트를 커밋
    이후 별도 커넥션으로 옮겼고, 그래서 여기를 성공 불변식으로 교체했다.

    실 DB 복사본 검증(2026-09-09): `12,954행 삭제` · `checkpoint:ok` ·
    `integrity_check ok` · cutoff 이전 잔존 0.

    ⚠ 되돌아가는 것을 막는 축은 아래 T6 의 **소스 불변식**이다 — 체크포인트가
      `_prune_once` 안으로 다시 들어가면 그 즉시 깨진다.
    """
    got, log, path = _run(view_table=None)

    # 임시 DB 는 4개 테이블 × OLD 1행 = 4행이 지워져야 한다
    check("T5: 삭제 행수를 반환한다 (got=%r)" % got, got == 4)
    check("T5: 더는 락으로 실패하지 않는다",
          "database table is locked" not in log)
    check("T5: 완료 로그가 나온다", "[Retrain] DB pruning 완료:" in log)
    check("T5: 진단(실패) 줄이 나오지 않는다",
          "[Retrain] DB pruning 진단:" not in log)
    check("T6: 체크포인트가 끝까지 간다", "checkpoint:ok" in log)

    # 실제로 지워졌는가 — 로그가 아니라 DB로 확인한다
    # (계측 4원칙 ⑤: 파생값 말고 구성요소를 직접 건다)
    conn = sqlite3.connect(path)
    rows = sorted(r[0] for r in conn.execute("SELECT ts FROM raw_features"))
    integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
    conn.close()
    check("T5: 오래된 행만 지워지고 최신 행은 남는다", rows == [NEW])
    check("T5: DB 무결성 유지", integrity == "ok")

    # 🔴 T6 소스 불변식 — 체크포인트는 `_prune_once` 밖에 있어야 한다.
    # ⚠ **주석은 빼고 코드 줄만 본다.** `_prune_once` 안에는 "여기에 있던
    #   `PRAGMA wal_checkpoint` 를 뺐다"는 설명 주석이 남아 있고(되돌리지 말라는
    #   경고다), 원문 전체를 그대로 훑으면 그 주석이 코드로 오인돼 잡힌다.
    src = _read("learning/batch_retrainer.py")
    body = src.split("def _prune_once(", 1)[1].split("def _checkpoint(", 1)[0]
    code = "\n".join(ln for ln in body.splitlines()
                     if not ln.lstrip().startswith("#"))
    check("T6: `_prune_once` 코드에 wal_checkpoint 호출이 없다",
          "wal_checkpoint" not in code)
    check("T6: 되돌리지 말라는 경고 주석은 남아 있다", "wal_checkpoint" in body)
    check("T6: 체크포인트 전용 함수가 있다", "def _checkpoint(" in src)
    check("T6: 커밋 후 커넥션을 명시적으로 닫는다", "conn.close()" in src)


def test_t9_post_commit_checkpoint_failure_keeps_count():
    """🔴 커밋 **이후** 체크포인트가 실패해도 삭제 행수를 0으로 되돌리지 않는다.

    492차 F-8 이 막은 것은 「커밋 안 된 수를 성공으로 보고」였다. 그 반대인
    「커밋된 수를 실패로 보고」도 똑같은 오보다(계측 4원칙 ④). 체크포인트는
    WAL 정리일 뿐이라 실패해도 삭제는 유효하다.
    """
    tmp = tempfile.mkdtemp(prefix="t538ck_")
    path = os.path.join(tmp, "raw_data.db")
    _build_db(path)

    real_connect = sqlite3.connect
    state = {"n": 0}

    def _flaky(*a, **k):
        state["n"] += 1
        if state["n"] == 2:            # 1=본 커넥션, 2=체크포인트 전용
            raise sqlite3.OperationalError("database table is locked")
        return real_connect(*a, **k)

    logger = logging.getLogger("LEARNING")
    cap = _Capture()
    logger.addHandler(cap)
    prev_level, logger.level = logger.level, logging.INFO
    prev_db = S.RAW_DATA_DB
    S.RAW_DATA_DB = path
    sqlite3.connect = _flaky
    try:
        got = _PRUNE(None, keep_weeks=52)
    finally:
        sqlite3.connect = real_connect     # 🔴 반드시 원복
        S.RAW_DATA_DB = prev_db
        logger.removeHandler(cap)
        logger.level = prev_level
    log = cap.text()

    check("T9: 커밋된 삭제 행수를 그대로 반환한다 (got=%r)" % got, got == 4)
    check("T9: 완료 로그가 나온다", "[Retrain] DB pruning 완료:" in log)
    check("T9: 체크포인트 실패는 별도 줄로 드러난다",
          "체크포인트 실패" in log and "커밋됨" in log)

    conn = real_connect(path)
    rows = sorted(r[0] for r in conn.execute("SELECT ts FROM raw_features"))
    conn.close()
    check("T9: 삭제는 실제로 커밋돼 있다", rows == [NEW])


def test_t8_journal_mode_and_rowcount_are_irrelevant():
    """재현 4/4 — journal 모드도, 지울 행이 있는지도 무관하다.

    "월요일에만 뭔가가 물고 있다"는 가설을 배제하는 근거다. 지우려는 행이
    한 건도 없어도 파이썬 sqlite3 는 DML 앞에서 트랜잭션을 열기 때문에
    체크포인트는 똑같이 막힌다.
    """
    for journal in ("delete", "wal"):
        for rows in (True, False):
            tmp = tempfile.mkdtemp(prefix="t538p_")
            path = os.path.join(tmp, "t.db")
            c = sqlite3.connect(path)
            c.execute("PRAGMA journal_mode=%s" % journal)
            c.execute("CREATE TABLE raw_features (ts TEXT)")
            if rows:
                c.execute("INSERT INTO raw_features VALUES (?)", (OLD,))
            c.commit()
            c.close()

            err = None
            try:
                with sqlite3.connect(path, timeout=15) as conn:
                    conn.execute("DELETE FROM raw_features WHERE ts < ?", (NEW,))
                    conn.execute("PRAGMA wal_checkpoint(PASSIVE)")
            except Exception as e:
                err = str(e)
            check("T8: journal=%s 삭제대상=%s → 같은 락 (err=%r)"
                  % (journal, rows, err),
                  err is not None and "table is locked" in err)


# ── 원문 계약 ────────────────────────────────────────────────────────────────

def test_t7_lock_classification_contract():
    """SQLITE_LOCKED 와 SQLITE_BUSY 는 **레버가 다르다** — 로그가 그걸 말해야 한다.

    라이브 실패 문구는 `database table is locked`(SQLITE_LOCKED)이고
    `database is locked`(SQLITE_BUSY)가 아니다. busy_timeout 은 SQLITE_LOCKED 에
    적용되지 않으므로 `timeout=15` 도 1초 뒤 재시도도 **듣지 않는 레버**였다.
    """
    src = _read("learning/batch_retrainer.py")
    check("T7: LOCKED 분기", '"table is locked" in _m' in src)
    check("T7: BUSY 분기", '"database is locked" in _m' in src)
    check("T7: busy_timeout 무효를 로그가 직접 말한다",
          "busy_timeout 무효" in src)
    check("T7: 재시도 횟수 무변경(루프 금지)", "for _attempt in (1, 2):" in src)
    check("T7: 진단은 EOD 를 깨뜨리지 않는다(전체 try 감쌈)",
          "[Retrain] DB pruning 진단 실패" in src)
    check("T7: 미측정을 0으로 쓰지 않는다(계측 4원칙 ②)", "미측정" in src)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    for fn in (test_t1_t2_t3_failure_records_progress,
               test_t4_no_placeholder_masquerading_as_data,
               test_t5_t6_success_path_after_fix,
               test_t9_post_commit_checkpoint_failure_keeps_count,
               test_t7_lock_classification_contract,
               test_t8_journal_mode_and_rowcount_are_irrelevant):
        try:
            fn()
        except Exception as e:
            print("[FAIL] %s: %r" % (fn.__name__, e))
            FAILURES.append(fn.__name__)
    print("-" * 60)
    print("전부 통과" if not FAILURES else "실패 %d건: %s" % (len(FAILURES), FAILURES))
    sys.exit(1 if FAILURES else 0)
