"""[MW0601 471차 후속4 / F-9] `entry_mode` 폴백 가시화 회귀 테스트.

────────────────────────────────────────────────────────────────────────────
배경 (상세: docs/정기점검/매일점검/MW0601-20260814-점검리포트-post.md P2 1-5)
────────────────────────────────────────────────────────────────────────────
종전 `main.py`는 대시보드 조회가 실패하면 `except Exception: entry_mode = "manual"`
한 줄로 **조용히** 떨어졌다. 하필 `manual`은 A·B·C **전 등급을 허용하는 가장 넓은
모드**이고(`{"auto":["A"], "hybrid":["A","B"], "manual":["A","B","C"]}`),
**정상 설정값도 `manual`**이라(실측 2026-07-01~: manual 11,590행 / hybrid 35행)
사후 분석에서 폴백분과 정상분을 구분할 방법이 아예 없었다.
즉 대시보드 예외 한 번이 허용 등급을 `["A"]`에서 `["A","B","C"]`로 조용히 넓혀도
아무 흔적이 남지 않는다 — 계측 4원칙 ④(폴백 가시화)의 정면 위반.

지키는 불변식:
  T1  정상 조회는 대시보드 값을 그대로 쓰고 폴백 사유가 비어 있다.
  T2  예외·대시보드 부재는 `manual`로 떨어지되 **사유를 원인별로 구분해** 돌려준다.
  T3  🔴 로그는 **상태가 바뀔 때만** — 매분 찍으면 하루 370줄이라 로그가 죽는다.
      폴백→정상 복구도 1회 남는다.
  T4  `ensemble_decisions.entry_mode_fallback`에 매 행 저장되고, 키 없는 호출부는
      NULL(미측정)로 남는다 — 0(정상 조회)과 구분한다(계측 4원칙 ②).
  T5  파이프라인이 이 헬퍼를 쓰고, 종전 인라인 폴백은 잔존하지 않는다.

실행: python tests/test_471_entry_mode_fallback.py   (COM/브로커 불필요)
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

import main  # noqa: E402

FAILURES = []


def check(name, cond):
    print("[%s] %s" % ("OK" if cond else "FAIL", name))
    if not cond:
        FAILURES.append(name)


class _StubDash(object):
    def __init__(self, mode="hybrid", raise_exc=None):
        self._mode = mode
        self._raise = raise_exc

    def get_entry_mode(self):
        if self._raise is not None:
            raise self._raise
        return self._mode


class _StubSelf(object):
    """TradingSystem 대역 — `_read_entry_mode`가 만지는 속성만 갖는다."""

    def __init__(self, dashboard=None):
        self.dashboard = dashboard
        self._entry_mode_fallback_last = None     # __init__ 명시 초기화 대역


class _LogRecorder(object):
    def __init__(self):
        self.lines = []

    def signal(self, msg, level="INFO"):
        self.lines.append((level, msg))

    def system(self, msg, level="INFO"):
        self.lines.append((level, msg))

    def trade(self, msg, *a, **k):
        pass


def _with_recorded_log(fn):
    orig = main.log_manager
    rec = _LogRecorder()
    main.log_manager = rec
    try:
        fn(rec)
    finally:
        main.log_manager = orig


_read = main.TradingSystem._read_entry_mode


def test_t1_normal_read():
    def body(rec):
        stub = _StubSelf(_StubDash("hybrid"))
        mode, reason = _read(stub)
        check("T1: 대시보드 값 그대로", mode == "hybrid")
        check("T1: 폴백 사유 없음", reason == "")
        check("T1: 정상 조회는 로그를 남기지 않는다(첫 호출 포함)", len(rec.lines) == 0)
    _with_recorded_log(body)


def test_t2_fallback_causes_are_distinguished():
    def body(rec):
        stub = _StubSelf(_StubDash(raise_exc=RuntimeError("widget deleted")))
        mode, reason = _read(stub)
        check("T2: 예외 → manual 폴백", mode == "manual")
        check("T2: 예외 사유에 예외형·메시지 포함",
              "조회 예외" in reason and "RuntimeError" in reason
              and "widget deleted" in reason)

        stub2 = _StubSelf(None)          # 대시보드 미생성
        mode2, reason2 = _read(stub2)
        check("T2: 대시보드 부재 → manual 폴백", mode2 == "manual")
        check("T2: 부재는 예외와 **다른 사유**로 구분", reason2 == "대시보드 없음")
        check("T2: 두 사유가 서로 다르다(원인 혼동 방지)", reason != reason2)
    _with_recorded_log(body)


def test_t3_logs_only_on_state_change():
    def body(rec):
        stub = _StubSelf(_StubDash(raise_exc=RuntimeError("boom")))
        for _ in range(5):               # 5분 연속 폴백
            _read(stub)
        warns = [m for lv, m in rec.lines if lv == "WARNING"]
        check("T3: 5회 연속 폴백 → WARNING 1건만 (로그 폭주 방지)", len(warns) == 1)
        check("T3: WARNING에 넓어진 허용 등급 명시",
              warns and "['A', 'B', 'C']" in warns[0])

        # 대시보드가 살아나면 복구를 1회 남긴다
        stub.dashboard = _StubDash("auto")
        mode, reason = _read(stub)
        check("T3: 복구 후 정상 조회값", mode == "auto" and reason == "")
        recov = [m for lv, m in rec.lines if "정상 조회 복구" in m]
        check("T3: 복구 로그 1건 + 직전 사유 병기",
              len(recov) == 1 and "boom" in recov[0])

        # 복구 이후 반복 호출은 조용하다
        _n = len(rec.lines)
        for _ in range(3):
            _read(stub)
        check("T3: 복구 후 반복 호출은 무로그", len(rec.lines) == _n)
    _with_recorded_log(body)


def test_t4_db_column_roundtrip():
    import utils.db_utils as dbu
    import learning.prediction_buffer as pb

    tmp = tempfile.mkdtemp(prefix="qdq_471f9_")
    db_path = os.path.join(tmp, "predictions.db")
    _orig_dbu, _orig_pb = dbu.PREDICTIONS_DB, pb.PREDICTIONS_DB
    try:
        dbu.PREDICTIONS_DB = db_path
        pb.PREDICTIONS_DB = db_path
        dbu.init_predictions_db()

        con = sqlite3.connect(db_path)
        cols = {r[1] for r in con.execute("PRAGMA table_info(ensemble_decisions)")}
        check("T4: entry_mode_fallback 컬럼 생성", "entry_mode_fallback" in cols)

        buf = pb.PredictionBuffer()
        base = dict(ts=None, sigma_at_t=0.0, horizon_proba={}, features_clean={},
                    regime="NEUTRAL", micro_regime="NORMAL")
        # 폴백 발생분 — 값은 정상분과 똑같이 manual이다(그래서 플래그가 필요하다)
        base.update(ts="2026-08-14 09:39:00")
        buf.save_step9_batch(decision={"entry_mode": "manual",
                                       "entry_mode_fallback": True}, **base)
        base.update(ts="2026-08-14 09:40:00")
        buf.save_step9_batch(decision={"entry_mode": "manual",
                                       "entry_mode_fallback": False}, **base)
        base.update(ts="2026-08-14 09:41:00")
        buf.save_step9_batch(decision={"entry_mode": "manual"}, **base)   # 구버전 호출부

        rows = {r[0]: r for r in con.execute(
            "SELECT ts, entry_mode, entry_mode_fallback FROM ensemble_decisions")}
        check("T4: 3행 저장", len(rows) == 3)
        check("T4: 폴백분 = 1", rows["2026-08-14 09:39:00"][2] == 1)
        check("T4: 정상분 = 0", rows["2026-08-14 09:40:00"][2] == 0)
        check("T4: 키 없는 호출부 = NULL (0과 구분 — 미측정)",
              rows["2026-08-14 09:41:00"][2] is None)
        check("T4: 🔴 entry_mode 값만으로는 구분 불가 — 셋 다 'manual'",
              {r[1] for r in rows.values()} == {"manual"})
        con.close()
    finally:
        dbu.PREDICTIONS_DB, pb.PREDICTIONS_DB = _orig_dbu, _orig_pb


def test_t5_pipeline_uses_helper():
    src = inspect.getsource(main.TradingSystem.run_minute_pipeline)
    check("T5: 파이프라인이 헬퍼를 쓴다",
          "entry_mode, _entry_mode_fallback_reason = self._read_entry_mode()" in src)
    check("T5: decision에 플래그 전달", 'decision["entry_mode_fallback"]' in src)
    # 🔴 종전 인라인 폴백(로그 없는 조용한 흡수)이 되살아나면 실패한다
    check("T5: 인라인 `except Exception: entry_mode = \"manual\"` 잔존 0",
          not re.search(r"except\s+Exception\s*:\s*\n\s*entry_mode\s*=", src))

    # INSERT arity 재확인 (컬럼 1개 추가)
    import learning.prediction_buffer as pb
    psrc = inspect.getsource(pb.PredictionBuffer.save_step9_batch)
    i = psrc.find("INSERT OR IGNORE INTO ensemble_decisions")
    stmt = psrc[i:psrc.find('"""', i + 10)]
    body = stmt[stmt.find("(") + 1:stmt.rfind(") VALUES")]
    n_cols = len([c for c in re.split(r"[,\s]+", body) if c])
    n_ph = stmt[stmt.rfind("VALUES"):].count("?")
    check("T5: 컬럼 수 == 플레이스홀더 수 (%d)" % n_cols, n_cols == n_ph)
    check("T5: 신규 컬럼 포함", "entry_mode_fallback" in body)


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
