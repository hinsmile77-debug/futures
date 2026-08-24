# -*- coding: utf-8 -*-
"""[MW0601 490차 / F-K] MetaGate 무정보 폴백을 로그·DB 양쪽에서 가른다.

## 왜 필요한가 (2026-08-24 이상점 1-11)

`JointGateBlock` 차단 로그의 `meta=0.50` 이 **실측 0.50 인지 무정보 폴백인지**
로그만으로 구분되지 않았다. 그날 차단 9건 중 8건이 그 값이었고, 폴백임을
확정하려면 같은 분 `[MetaGate]` 로그와 교차대조해야 했다 — 계측 4원칙 ④가
금지하는 형태(폴백이 정상값처럼 보인다)다.

`meta_size_raw`(422차) 만으로는 부족하다. 그 컬럼은 **값**이고 이것은 **그 값이
지워졌는가**다. raw 가 NULL 인 경로(MetaGate FLAT early-return)와 raw 가 0.0 인
경로가 따로 있어 값만으로는 역산되지 않는다.

## 🔴 무엇을 바꾸지 않았는가

**임계·합성 방식은 무변경이다.** `JOINT_GATE_META_FALLBACK_NEUTRAL` 도 그대로
False 다. 431차가 이미 검토하고 거부한 변경이고(폴백을 1.0으로 바꾸면
`1.0×0.70=0.70` 이 되어 게이트가 조용히 무력화된다), 캠페인 [7]이 이 게이트에
PASS(차단이 손실을 회피) 판정을 냈다. 이 fix 는 **표기와 컬럼만** 늘린다.
"""
import ast
import io
import os
import sqlite3
import sys
import tempfile

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

_MAIN = io.open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()
_PB = io.open(os.path.join(_ROOT, "learning", "prediction_buffer.py"),
              encoding="utf-8").read()


# ── 로그 표기 ─────────────────────────────────────────────────────────────

def test_차단_로그에_fallback_표기가_붙는다():
    assert '_fb_tag = "<fallback>" if _meta_size_fb else ""' in _MAIN, (
        "JointGateBlock 차단 로그에 폴백 표기가 없다 (490차 F-K 회귀)"
    )
    # signal · trade · entry_block_reason 세 곳 모두에 붙어야 한다 —
    # 로그와 DB 가 서로 다른 사실을 말하면 사후 대조에서 어느 쪽도 못 믿는다.
    assert _MAIN.count("{_fb_tag}") >= 3, (
        "폴백 표기가 signal/trade/entry_block_reason 셋 중 일부에만 붙었다"
    )


def test_mn_tag로_대체하지_않았다():
    """`_mn_tag` 는 **중립화가 적용됐을 때만** 붙는다.
    `JOINT_GATE_META_FALLBACK_NEUTRAL` 이 기본 False 라 라이브에서는 항상 빈
    문자열이므로, 그것으로 폴백을 표기했다고 착각하면 안 된다."""
    from config.settings import JOINT_GATE_META_FALLBACK_NEUTRAL
    assert JOINT_GATE_META_FALLBACK_NEUTRAL is False, (
        "이 fix 는 중립화 플래그를 켜지 않는다 — 431차 확정 결정 · 캠페인 [7] PASS 게이트"
    )
    assert "_fb_tag" in _MAIN and "_mn_tag" in _MAIN, "두 표기는 서로 다른 사실이다"


def test_임계와_합성식은_무변경():
    """🔴 431차 확정 결정 — 재론 금지 사안이다."""
    assert "_joint_mult = _meta_size_eff * _tox_size" in _MAIN
    assert "and _joint_mult < 0.50" in _MAIN


# ── DB 컬럼 ───────────────────────────────────────────────────────────────

def test_INSERT_컬럼과_플레이스홀더가_맞는다():
    """컬럼을 늘리면서 `?` 를 안 늘리면 매분 STEP9 저장이 통째로 죽는다."""
    import re
    hits = list(re.finditer(
        r'INSERT OR IGNORE INTO ensemble_decisions \((.*?)\)\s*VALUES \((.*?)\)"""',
        _PB, re.S))
    assert hits, "ensemble_decisions INSERT 문을 못 찾았다"
    m = hits[-1]
    cols = [c.strip() for c in m.group(1).replace(chr(10), " ").split(",") if c.strip()]
    assert "meta_size_fallback" in cols, "INSERT 에 meta_size_fallback 이 없다"
    assert len(cols) == m.group(2).count("?"), (
        "컬럼 %d개 vs 플레이스홀더 %d개 — 불일치" % (len(cols), m.group(2).count("?"))
    )
    tree = ast.parse(_PB)
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and getattr(node.target, "id", "") == "ens_row":
            assert len(node.value.elts) == len(cols), (
                "ens_row %d개 vs 컬럼 %d개 — 불일치" % (len(node.value.elts), len(cols))
            )
            break
    else:
        pytest.fail("ens_row 튜플을 못 찾았다")


@pytest.fixture
def sandbox_db():
    """임시 DB 로 갈아끼우고 **반드시 되돌린다**.

    ⚠ 되돌리지 않으면 같은 프로세스의 뒤이은 테스트가 임시 경로를 쓰게 되고,
      최악에는 라이브 DB 경로를 잃은 채 조용히 통과한다 — 테스트가 스스로
      「조용한 결함」을 만드는 형태다.
    """
    import config.settings as st
    import utils.db_utils as du
    import learning.prediction_buffer as pb
    saved = (st.PREDICTIONS_DB, du.PREDICTIONS_DB, pb.PREDICTIONS_DB)
    tmp = tempfile.mkdtemp()
    db = os.path.join(tmp, "predictions.db")
    st.PREDICTIONS_DB = du.PREDICTIONS_DB = pb.PREDICTIONS_DB = db
    du.init_predictions_db()
    try:
        yield tmp, pb
    finally:
        st.PREDICTIONS_DB, du.PREDICTIONS_DB, pb.PREDICTIONS_DB = saved


def _decision(meta_gate):
    return {
        "direction": 1, "confidence": 0.5, "grade": "C", "auto_entry": False,
        "regime_ok": True, "min_conf": 0.35, "weight_collapsed": False,
        "meta_gate": meta_gate,
        "toxicity_gate": {"signals": {"spread_ticks": 3.0,
                                      "spread_extreme_shadow": False}},
        "fp_psi": None, "fp_level": None, "sizing_trace": None,
    }


def test_폴백이면_1_아니면_0_키가_없으면_NULL(sandbox_db):
    """세 상태다 — 폴백 / 폴백 아님 / **미측정**. 계측 4원칙 ②."""
    tmp, pb = sandbox_db
    buf = pb.PredictionBuffer()
    cases = [
        ("10:00:00", {"action": "reduce", "size_multiplier_fallback": True}, 1),
        ("10:01:00", {"action": "reduce", "size_multiplier_fallback": False}, 0),
        ("10:02:00", {"action": "skip"}, None),          # 키 부재 = 미측정
    ]
    for ts, mg, _ in cases:
        buf.save_step9_batch(ts="2026-08-24 " + ts, sigma_at_t=1.0, horizon_proba={},
                             features_clean={}, regime="NEUTRAL", micro_regime="",
                             decision=_decision(mg))
    con = sqlite3.connect(os.path.join(tmp, "predictions.db"))
    got = dict(con.execute(
        "SELECT ts, meta_size_fallback FROM ensemble_decisions").fetchall())
    con.close()
    for ts, _, want in cases:
        assert got["2026-08-24 " + ts] == want, (
            "%s: %r (기대 %r)" % (ts, got["2026-08-24 " + ts], want)
        )


def test_get_key_0_폴백을_쓰지_않는다():
    """`.get(key, 0)` 로 채우면 「미측정」이 「폴백 아님」으로 위장한다 —
    451차가 `program_*` 3종을 폐기한 것과 같은 결함이다."""
    i = _PB.index("size_multiplier_fallback")
    seg = _PB[max(0, i - 600):i + 200]
    assert '"size_multiplier_fallback", 0' not in seg
    assert ".get(\"size_multiplier_fallback\", 0)" not in seg
