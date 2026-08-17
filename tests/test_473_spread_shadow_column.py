# -*- coding: utf-8 -*-
"""[MW0601 473차 / F-8 Phase B] 스프레드 섀도 컬럼 배선 회귀 테스트.

무엇을 지키는가
---------------
`ToxicityGate.evaluate()`는 밴드(block/reduce/pass)와 무관하게 항상
`signals = {spread_ticks, cancel_stress, flow_stress, spread_extreme_shadow}`
를 반환하는데, **소비처가 코드베이스 전체에 0곳**이었다. 2026-07-12 도입 이래
한 달 넘게 계산만 되고 버려진 값이고, 그래서 실전 전환 기준 ⑨의 복원 판단
근거를 만들 수 없었다 — FP-CRITICAL이 "학습분포 저장 함수가 프로덕션에서
호출된 적이 없어 2개월간 PSI=0.0 고정"이던 것과 **같은 결함 패턴**이다.

이 파일은 그 배선이 살아 있는지, 그리고 **미측정을 0으로 위장하지 않는지**를
못박는다.

⚠ 배선했다고 데이터가 생기는 것이 아니다
-----------------------------------------
471차 후속6의 `sizing_trace`가 바로 그 교훈이다 — 같은 패턴으로 배선했는데
2026-08-17 현재 **적재 0행**이다(장 마감 후 배포라 다음 거래일이 첫 시험).
배선 테스트가 통과하는 것과 라이브에 값이 들어오는 것은 다른 문제이며,
후자는 배포 당일 EOD에 `SELECT COUNT(spread_ticks)`로 확인해야 한다
(`dev_memory/NEXT_TODO.md` 473차 게이트).

실행:
    pytest tests/test_473_spread_shadow_column.py
"""
import os
import sqlite3
import sys
import tempfile

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

os.environ["MIREUK_TEST_MODE"] = "1"

_COLS = ("spread_ticks", "spread_extreme_shadow")


def _fresh_db():
    import utils.db_utils as dbu
    import learning.prediction_buffer as pb
    tmp = tempfile.mkdtemp(prefix="t473_f8_")
    path = os.path.join(tmp, "predictions.db")
    old = (dbu.PREDICTIONS_DB, pb.PREDICTIONS_DB)
    dbu.PREDICTIONS_DB = pb.PREDICTIONS_DB = path
    dbu.init_predictions_db()
    return path, old, dbu, pb


def _restore(old, dbu, pb):
    dbu.PREDICTIONS_DB, pb.PREDICTIONS_DB = old


def test_columns_are_created_by_migration():
    """마이그레이션이 두 컬럼을 만든다 — `additions` 딕트 한 줄씩이 전부."""
    path, old, dbu, pb = _fresh_db()
    try:
        con = sqlite3.connect(path)
        cols = {r[1] for r in con.execute("PRAGMA table_info(ensemble_decisions)")}
        con.close()
        for c in _COLS:
            assert c in cols, "%s 컬럼이 생성되지 않았다" % c
    finally:
        _restore(old, dbu, pb)


def test_roundtrip_and_unmeasured_stays_null():
    """정상값은 그대로, **키가 없으면 NULL** — 0으로 뭉개지 않는다(계측 4원칙 ②).

    `spread_ticks = 0.0`은 호가 결측 폴백일 수도 있다
    (`features/feature_builder.py:516`). 거기에 "게이트가 안 돌았다"까지 0으로
    합치면 세 상태가 한 값에 겹쳐 사후 분리가 불가능해진다.
    """
    path, old, dbu, pb = _fresh_db()
    try:
        buf = pb.PredictionBuffer()
        base = dict(sigma_at_t=0.0, horizon_proba={}, features_clean={},
                    regime="NEUTRAL", micro_regime="NORMAL")

        # ① 극단 스프레드 — 섀도 True
        buf.save_step9_batch(ts="2026-08-17 09:01:00", decision={
            "toxicity_gate": {"action": "reduce", "signals": {
                "spread_ticks": 31.5, "spread_extreme_shadow": True}}}, **base)
        # ② 평상 스프레드 — 섀도 False
        buf.save_step9_batch(ts="2026-08-17 09:02:00", decision={
            "toxicity_gate": {"action": "pass", "signals": {
                "spread_ticks": 6.0, "spread_extreme_shadow": False}}}, **base)
        # ③ 스프레드 0.0 (호가 결측 폴백) — 값은 남기되 섀도는 False
        buf.save_step9_batch(ts="2026-08-17 09:03:00", decision={
            "toxicity_gate": {"action": "pass", "signals": {
                "spread_ticks": 0.0, "spread_extreme_shadow": False}}}, **base)
        # ④ 게이트가 아예 안 돎 — 미측정
        buf.save_step9_batch(ts="2026-08-17 09:04:00", decision={}, **base)
        # ⑤ 게이트는 돌았으나 signals 없음(구버전) — 미측정
        buf.save_step9_batch(ts="2026-08-17 09:05:00", decision={
            "toxicity_gate": {"action": "pass"}}, **base)

        con = sqlite3.connect(path)
        got = {r[0]: (r[1], r[2]) for r in con.execute(
            "SELECT ts, spread_ticks, spread_extreme_shadow FROM ensemble_decisions")}
        con.close()

        assert len(got) == 5, "5행이 저장되지 않았다: %d" % len(got)
        assert got["2026-08-17 09:01:00"] == (31.5, 1)
        assert got["2026-08-17 09:02:00"] == (6.0, 0)
        # 0.0은 유효값으로 남는다 — falsy 승격 금지
        assert got["2026-08-17 09:03:00"] == (0.0, 0), (
            "spread_ticks=0.0이 NULL로 승격됐다 — 0.0은 유효값이다")
        assert got["2026-08-17 09:04:00"] == (None, None), (
            "게이트 미실행 분이 0으로 채워졌다 — 미측정 ≠ 0")
        assert got["2026-08-17 09:05:00"] == (None, None), (
            "signals 부재 분이 0으로 채워졌다 — 미측정 ≠ 0")
    finally:
        _restore(old, dbu, pb)


def test_insert_arity_matches_column_list():
    """컬럼 개수와 `?` 개수가 같은가 — 471차가 50→52로 바꾸며 놓치기 쉬운 지점."""
    import inspect
    import re
    from learning.prediction_buffer import PredictionBuffer

    src = inspect.getsource(PredictionBuffer.save_step9_batch)
    m = re.search(
        r"INSERT OR IGNORE INTO ensemble_decisions \((.*?)\) VALUES \((.*?)\)",
        src, re.S)
    assert m, "INSERT 문을 찾지 못했다"
    cols = [c.strip() for c in m.group(1).replace("\n", " ").split(",") if c.strip()]
    n_q = m.group(2).count("?")
    assert len(cols) == n_q, "컬럼 %d개 vs ? %d개 — arity 불일치" % (len(cols), n_q)
    for c in _COLS:
        assert c in cols, "%s 가 INSERT 컬럼 목록에 없다" % c


def test_no_get_with_zero_default():
    """`.get(key, 0)` 폴백 금지 — 상수 0이 정상 수집으로 위장한다(451차 program_* 전례)."""
    import inspect
    from learning.prediction_buffer import PredictionBuffer

    src = inspect.getsource(PredictionBuffer.save_step9_batch)
    idx = src.find("_tox_signals.get(")
    assert idx > 0, "_tox_signals 바인딩이 없다"
    seg = src[idx:idx + 400]
    for bad in ('.get("spread_ticks", 0', '.get("spread_extreme_shadow", 0',
                '.get("spread_ticks", 0.0'):
        assert bad not in seg, "폴백 0을 쓰고 있다: %s" % bad


def test_gate_still_emits_the_signals_it_promises():
    """ToxicityGate가 세 밴드 모두에서 두 키를 반환하는가 — 배선의 상류."""
    from strategy.risk.toxicity_gate import ToxicityGate

    g = ToxicityGate()
    seen = set()
    for spread in (2.0, 10.0, 50.0):
        out = g.evaluate({"spread_ticks": spread})
        sig = out.get("signals") or {}
        assert "spread_ticks" in sig, "signals에 spread_ticks가 없다"
        assert "spread_extreme_shadow" in sig, "signals에 spread_extreme_shadow가 없다"
        seen.add(out.get("action"))
    assert seen, "게이트가 action을 내지 않았다"


def test_shadow_threshold_follows_settings():
    """섀도 판정 임계가 설정값을 따르는가 — 채널 사전등록과 어긋나면 딴 것을 잰다."""
    from config.settings import TOXICITY_SEVERE_SPREAD_BLOCK_TICKS
    from strategy.risk.toxicity_gate import ToxicityGate

    thr = float(TOXICITY_SEVERE_SPREAD_BLOCK_TICKS)
    g = ToxicityGate(severe_spread_block_ticks=thr)
    below = g.evaluate({"spread_ticks": thr - 0.01})["signals"]["spread_extreme_shadow"]
    at = g.evaluate({"spread_ticks": thr})["signals"]["spread_extreme_shadow"]
    assert not below and at, "섀도 경계가 %s틱에서 갈리지 않는다" % thr
