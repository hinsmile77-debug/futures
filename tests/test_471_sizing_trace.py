"""[MW0601 471차 후속6 / G-1] 사이징 계보 구조체(`sizing_trace`) 회귀 테스트.

────────────────────────────────────────────────────────────────────────────
배경 (상세: docs/정기점검/매일점검/MW0601-20260814-점검리포트-post.md §3 G-1)
────────────────────────────────────────────────────────────────────────────
F-3이 `[SizerMatch]` 문자열을 고쳤지만 문자열은 게이트가 하나 늘 때마다 같은
오귀속이 재발한다(2026-08-14 P1-2: 실제 원인 hurst가 목록에 아예 없었다).
실전 전환 기준 ⑧의 근거 채널 [28]이 읽는 값이므로 근거 무결성 문제다.
부수 효과가 하나 더 있다 — 지금까지 "사이저가 몇 계약을 내놓았는가"는 DB에 없어
[28]의 `structural_reason`이 **417차에 하드코딩된 수치**를 매주 재인용해 왔다.

지키는 불변식:
  T1  사이저가 돈 분만 구조체가 남는다. 안 돈 분은 **NULL**(0이 아니다 — 계측 4원칙 ②).
  T2  수량 계보 4단(사이저원본→안전군→표시→최종)과 품질군 전량·argmin이 들어 있다.
  T3  🔴 `round(qty_sizer_raw × quality_min) == qty_display` 항등 — 431차 min() 합성.
  T4  DB 왕복 + 압력 집계(`_sizer_pressure_from_trace`)가 실측을 낸다.
  T5  압력 집계는 **판정에 관여하지 않는다**(합격선 불변, §9).

실행: python tests/test_471_sizing_trace.py   (COM/브로커 불필요)
"""

import inspect
import json
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


# 2026-08-14 11:48:00 실측 진입을 그대로 구조체로 옮긴 것
_TRACE_ENTRY = {
    "qty_sizer_raw": 3, "qty_safety_base": 3, "qty_display": 2, "qty_auto": 2,
    "quality_mults": {"meta": 1.0, "hurst": 0.5},
    "binding_gate": "hurst", "quality_min": 0.5,
    "meta_size_raw": 0.5, "meta_size_sizing": 1.0,
    "tox_size": 1.0, "exec_size": 1.0,
    "kelly_mult": 0.6, "kelly_advised_skip": 0,
    "max_contracts": 3, "max_entry_qty": 3, "entry_executed": 1,
}
_TRACE_BLOCKED = dict(_TRACE_ENTRY, qty_sizer_raw=4, qty_display=1, qty_auto=1,
                      quality_mults={"meta": 0.5, "tox": 0.7, "hurst": 0.5},
                      binding_gate="meta", quality_min=0.5, entry_executed=0)


def test_t3_compose_identity():
    import main
    got = main._compose_quality_qty(_TRACE_ENTRY["qty_safety_base"],
                                    _TRACE_ENTRY["quality_mults"])
    check("T3: round(3 × 0.50) = 2 — 구조체의 qty_display와 일치",
          got == _TRACE_ENTRY["qty_display"])
    check("T3: binding_gate == 품질군 argmin",
          min(_TRACE_ENTRY["quality_mults"],
              key=lambda k: _TRACE_ENTRY["quality_mults"][k])
          == _TRACE_ENTRY["binding_gate"])


def test_t1_t2_main_wiring():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(root, "main.py"), encoding="utf-8") as fh:
        src = fh.read()
    check("T1: 사이저 미실행 분은 None(=NULL)", 'decision["sizing_trace"] = None' in src)
    check("T1: 사이저 실행 여부를 _qty_sizer_raw 존재로 판정",
          '_sz_raw = locals().get("_qty_sizer_raw")' in src)
    i = src.find('decision["sizing_trace"] = {')
    check("T2: 구조체 생성부 존재", i > 0)
    blk = src[i:i + 2200]
    for key in ("qty_sizer_raw", "qty_safety_base", "qty_display", "qty_auto",
                "quality_mults", "binding_gate", "quality_min",
                "meta_size_raw", "meta_size_sizing", "tox_size", "exec_size",
                "kelly_mult", "max_contracts", "max_entry_qty", "entry_executed"):
        check("T2: 키 `%s` 포함" % key, '"%s"' % key in blk)


def test_t4_db_roundtrip_and_pressure():
    import utils.db_utils as dbu
    import learning.prediction_buffer as pb
    import scripts.generate_validation_campaign_report as rep

    tmp = tempfile.mkdtemp(prefix="qdq_471g1_")
    db_path = os.path.join(tmp, "predictions.db")
    _o_dbu, _o_pb, _o_rep = dbu.PREDICTIONS_DB, pb.PREDICTIONS_DB, rep.PREDICTIONS_DB
    try:
        dbu.PREDICTIONS_DB = pb.PREDICTIONS_DB = rep.PREDICTIONS_DB = db_path
        dbu.init_predictions_db()

        con = sqlite3.connect(db_path)
        cols = {r[1] for r in con.execute("PRAGMA table_info(ensemble_decisions)")}
        check("T4: sizing_trace 컬럼 생성", "sizing_trace" in cols)

        buf = pb.PredictionBuffer()
        base = dict(sigma_at_t=0.0, horizon_proba={}, features_clean={},
                    regime="NEUTRAL", micro_regime="NORMAL")
        buf.save_step9_batch(ts="2026-08-14 11:47:00",
                             decision={"sizing_trace": _TRACE_ENTRY}, **base)
        buf.save_step9_batch(ts="2026-08-14 11:50:00",
                             decision={"sizing_trace": _TRACE_BLOCKED}, **base)
        buf.save_step9_batch(ts="2026-08-14 11:51:00",
                             decision={"sizing_trace": None}, **base)   # 사이저 미실행
        buf.save_step9_batch(ts="2026-08-14 11:52:00", decision={}, **base)  # 구버전

        got = {r[0]: r[1] for r in con.execute(
            "SELECT ts, sizing_trace FROM ensemble_decisions")}
        check("T4: 4행 저장", len(got) == 4)
        check("T1: 사이저 미실행 분 → NULL", got["2026-08-14 11:51:00"] is None)
        check("T1: 구버전 호출부 → NULL", got["2026-08-14 11:52:00"] is None)
        rt = json.loads(got["2026-08-14 11:47:00"])
        check("T2: 왕복 무손실", rt == _TRACE_ENTRY)
        check("T2: 한글/유니코드 이스케이프 없이 저장(ensure_ascii=False)",
              "\\u" not in got["2026-08-14 11:47:00"])
        con.close()

        sp = rep._sizer_pressure_from_trace(since="2026-08-01 00:00:00")
        check("T4: 압력 집계 가용", sp.get("available") is True)
        check("T4: 사이저 실행 2회 집계 (NULL 2행 제외)", sp.get("n_sizer_runs") == 2)
        check("T4: 3계약+ 출력 2회 · 100.0%",
              sp.get("n_sizer_ge3") == 2 and sp.get("pct_sizer_ge3") == 100.0)
        check("T4: 3계약+ **체결**은 0건 (눌려서 2·1계약으로 체결)",
              sp.get("entered_qty_ge3") == 0 and sp.get("n_entered") == 1)
        check("T4: binding 게이트 빈도 집계",
              sp.get("binding_gate_hist") == {"hurst": 1, "meta": 1})
        check("T4: 실측 기준일 표기(미측정 구간과 혼동 방지)",
              sp.get("since_effective") == "2026-08-14")

        # 컬럼이 없는 구세대 DB에서는 "미가용"을 명시한다(하드코딩 수치 오독 방지)
        con = sqlite3.connect(db_path)
        con.execute("ALTER TABLE ensemble_decisions RENAME TO _ed_bak")
        con.execute("CREATE TABLE ensemble_decisions (ts TEXT)")
        con.commit(); con.close()
        sp2 = rep._sizer_pressure_from_trace(since="2026-08-01 00:00:00")
        check("T4: 컬럼 없는 PC → available=False + 사유 명시",
              sp2.get("available") is False and "sizing_trace" in sp2.get("reason", ""))
    finally:
        dbu.PREDICTIONS_DB, pb.PREDICTIONS_DB, rep.PREDICTIONS_DB = _o_dbu, _o_pb, _o_rep


def test_t5_pressure_does_not_touch_verdict():
    import scripts.generate_validation_campaign_report as rep

    src = inspect.getsource(rep.eval_sizing_inversion_watch)
    check("T5: 압력 집계를 [28]에 부착", 'out["sizer_pressure"]' in src)
    # 🔴 판정 경로가 압력 값을 읽으면 사전등록 합격선이 오염된다(§9)
    # 부착은 1회뿐이고(쓰기만), 판정 구간(gap_krw 산출 이후)에서는 읽지 않는다.
    # 판정이 이 관측치를 읽으면 사전등록 합격선이 오염된다(§9).
    check("T5: sizer_pressure 부착은 1회(쓰기만)",
          src.count('out["sizer_pressure"]') == 1)
    _verdict_part = src[src.find('out["gap_krw"]'):]
    check("T5: 판정 구간이 sizer_pressure를 읽지 않는다",
          "sizer_pressure" not in _verdict_part)
    check("T5: verdict 산출은 gap_krw 기준 그대로",
          'out["verdict"] = "FAIL" if out["gap_krw"] >= gap else "PASS"' in src)

    # INSERT arity 재확인
    import learning.prediction_buffer as pb
    psrc = inspect.getsource(pb.PredictionBuffer.save_step9_batch)
    i = psrc.find("INSERT OR IGNORE INTO ensemble_decisions")
    stmt = psrc[i:psrc.find('"""', i + 10)]
    body = stmt[stmt.find("(") + 1:stmt.rfind(") VALUES")]
    n_cols = len([c for c in re.split(r"[,\s]+", body) if c])
    n_ph = stmt[stmt.rfind("VALUES"):].count("?")
    check("T5: 컬럼 수 == 플레이스홀더 수 (%d)" % n_cols, n_cols == n_ph)


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
