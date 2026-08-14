"""[MW0601 471차 F-4] 차단사유 정합 — 동시 성립 축 전량 + 선제차단 플래그 회귀 테스트.

────────────────────────────────────────────────────────────────────────────
배경 (상세: docs/정기점검/매일점검/MW0601-20260814-점검리포트-post.md "확인 필요")
────────────────────────────────────────────────────────────────────────────
2026-08-14 Degraded 선제차단 4건 중 09:39·11:24는 로그가 `Degraded 선제차단`이라
찍었는데 DB(`ensemble_decisions.entry_block_reason`)에 남은 최종 사유는 `등급X`였다.
STEP7의 차단사유가 **elif 체인의 1등 하나**뿐이라 동시 성립한 다른 축이 통째로
사라지기 때문이다. 두 계측이 같은 분봉에 다른 이름을 붙이면 사후 분석이 갈린다.

지키는 불변식:
  T1  `entry_block_axes` 컬럼과 `health_preblock` 컬럼이 스키마에 존재한다.
  T2  두 값이 실제로 저장되고 되읽힌다(세미콜론 구분 / 0·1).
  T3  🔴 키가 없는 호출부는 **NULL**로 남는다 — 미측정과 "축 없음"을 구분한다
      (계측 4원칙 ②: `.get(key, 0)` 폴백이 상수를 정상 수집으로 위장하는 것 금지).
  T4  `entry_block_reason`(1등 사유)은 **무변경**이다 — 부분문자열 분류기 3곳의
      집계를 조용히 재정의하지 않는다(461차 mdd_pct 유형 불연속 방지).
  T5  INSERT 컬럼 수 == 플레이스홀더 수 == 튜플 길이.

실행: python tests/test_471_block_axes.py   (COM/브로커 불필요)
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


_TS_A = "2026-08-14 09:39:00"     # 로그=Degraded 선제차단 / DB=등급X 였던 분
_TS_B = "2026-08-14 10:39:00"     # 둘 다 Degraded 였던 분
_TS_C = "2026-08-14 11:24:00"     # 구버전 호출부 대역(키 없음)


def _save(pb_mod, ts, decision):
    pb_mod.PredictionBuffer().save_step9_batch(
        ts=ts, sigma_at_t=0.0, horizon_proba={}, features_clean={},
        regime="NEUTRAL", micro_regime="NORMAL", decision=decision,
    )


def test_schema_and_roundtrip():
    import utils.db_utils as dbu
    import learning.prediction_buffer as pb

    tmp = tempfile.mkdtemp(prefix="qdq_471_")
    db_path = os.path.join(tmp, "predictions.db")
    _orig_dbu, _orig_pb = dbu.PREDICTIONS_DB, pb.PREDICTIONS_DB
    try:
        dbu.PREDICTIONS_DB = db_path
        pb.PREDICTIONS_DB = db_path
        dbu.init_predictions_db()

        con = sqlite3.connect(db_path)
        cols = {r[1] for r in con.execute("PRAGMA table_info(ensemble_decisions)")}
        check("T1: entry_block_axes 컬럼 생성", "entry_block_axes" in cols)
        check("T1: health_preblock 컬럼 생성", "health_preblock" in cols)

        # 09:39 재현 — 1등 사유는 등급X인데 선제차단도 동시 성립
        _save(pb, _TS_A, {
            "direction": -1, "confidence": 0.343,
            "entry_block_reason": "[차단] 등급X — 미통과 항목: 2_confidence",
            "entry_block_axes": "grade_x;qty_zero;health_preblock",
            "health_preblock": True,
        })
        # 10:39 재현 — Degraded가 1등
        _save(pb, _TS_B, {
            "direction": 1, "confidence": 0.361,
            "entry_block_reason": "[차단] 자동진입 Degraded 최소신뢰도 62.0% 미달",
            "entry_block_axes": "degraded_conf;health_preblock",
            "health_preblock": True,
        })
        # 구버전 호출부 — 두 키 자체가 없다
        _save(pb, _TS_C, {
            "direction": -1, "confidence": 0.362,
            "entry_block_reason": "[차단] 등급X — 미통과 항목: 2_confidence",
        })

        rows = {r[0]: r for r in con.execute(
            "SELECT ts, entry_block_reason, entry_block_axes, health_preblock "
            "FROM ensemble_decisions")}
        check("T2: 3행 저장", len(rows) == 3)

        a = rows[_TS_A]
        check("T2: 동시 성립 축 전량 저장(세미콜론 구분)",
              a[2] == "grade_x;qty_zero;health_preblock")
        check("T2: 선제차단 플래그 1", a[3] == 1)
        # 🔴 이것이 F-4가 푸는 문제 — 1등 사유만 보면 선제차단이 사라진다
        check("T2: 1등 사유는 등급X인데 축 목록에는 health_preblock이 살아 있다",
              "등급X" in a[1] and "health_preblock" in a[2])

        b = rows[_TS_B]
        check("T2: Degraded가 1등인 분도 축 목록 일치",
              b[2] == "degraded_conf;health_preblock" and b[3] == 1)

        c = rows[_TS_C]
        check("T3: 키 없는 호출부 → axes NULL (빈 문자열 아님)", c[2] is None)
        check("T3: 키 없는 호출부 → health_preblock NULL (0 아님)", c[3] is None)

        check("T4: entry_block_reason 무변경 — 1등 사유 그대로",
              c[1] == "[차단] 등급X — 미통과 항목: 2_confidence")
        # 분류기가 종전과 같은 라벨을 낸다 (일일 퍼널 시계열 연속성)
        label = dbu._categorize_block_reason(a[1], "")
        check("T4: _categorize_block_reason 라벨 불변(체크리스트항목미달)",
              label == "체크리스트항목미달")
        con.close()
    finally:
        dbu.PREDICTIONS_DB, pb.PREDICTIONS_DB = _orig_dbu, _orig_pb


def test_insert_arity():
    import learning.prediction_buffer as pb

    src = inspect.getsource(pb.PredictionBuffer.save_step9_batch)
    i = src.find("INSERT OR IGNORE INTO ensemble_decisions")
    stmt = src[i:src.find('"""', i + 10)]
    body = stmt[stmt.find("(") + 1:stmt.rfind(") VALUES")]
    n_cols = len([c for c in re.split(r"[,\s]+", body) if c and not c.startswith("--")])
    n_ph = stmt[stmt.rfind("VALUES"):].count("?")
    check("T5: 컬럼 수 == 플레이스홀더 수 (%d)" % n_cols, n_cols == n_ph)
    check("T5: 신규 2컬럼 포함", "entry_block_axes" in body and "health_preblock" in body)


def test_main_writes_axes():
    """main.py가 축 목록을 실제로 산출·전달하는지 소스 수준 확인."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(root, "main.py"), encoding="utf-8") as fh:
        src = fh.read()
    check("T6: 축 목록 산출부 존재", '_entry_block_axes = ";".join(_block_axes)' in src)
    check("T6: decision에 전달", 'decision["entry_block_axes"]' in src)
    check("T6: 선제차단 플래그 전달", 'decision["health_preblock"]' in src)
    check("T6: lookahead 발화 시 플래그 True",
          "self._health_preblock_fired = True" in src)
    check("T6: 매 호출 리셋(직전 분 값이 새는 것 방지)",
          "self._health_preblock_fired = False" in src)


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
