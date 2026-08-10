# -*- coding: utf-8 -*-
"""456차 Wave 3 — F6 학습 컷오프 메타데이터 + F7 판정 소스 게이트.

배경: `dev_memory/DECISION_LOG.md` 456차 Wave 3,
      `docs/정기점검/매일점검/0810_Fix_고도화_통합구현계획_MW0601.md` Wave 3.

핵심 불변식
  ① 사이드카가 "현행 pkl이 무엇인지"를 기록한다 (intraday면 cv_acc=None)
  ② 홀드아웃이 현행 학습구간과 겹치면 **판정하지 않는다**
  ③ "모름"은 "깨끗함"이 아니라 **오염으로 취급**한다
  ④ 판정 소스 전환은 config 플래그로만 — 기본값은 기존 동작(acc_txt)
"""
import json
import os
import sys

import numpy as np
import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from learning.batch_retrainer import BatchRetrainer   # noqa: E402


@pytest.fixture
def br(tmp_path):
    return BatchRetrainer(model_dir=str(tmp_path / "m"), scaler_dir=str(tmp_path / "s"))


def _ts(i):
    """합성 타임스탬프 — 분 단위 증가."""
    return "2026-08-%02d %02d:%02d:00" % (1 + i // 1440, (i // 60) % 24, i % 60)


# ── F6-① 사이드카 ────────────────────────────────────────────────────────────

def test_sidecar_records_eod_model(br):
    br._train_row_ts = [_ts(i) for i in range(1000)]
    br._save_model_meta("3m", 0.4321, ["a", "b"])
    m = br._load_model_meta("3m")
    assert m["source"] == "eod"
    assert m["cv_acc"] == pytest.approx(0.4321)
    assert m["train_rows"] == 1000
    assert m["train_cutoff_ts"] == _ts(999)
    assert m["n_features"] == 2


def test_sidecar_intraday_has_no_cv_acc(br):
    """intraday는 CV를 안 돈다 — 성적 '미상'을 0이나 낡은 값으로 위장하지 않는다."""
    br._train_row_ts = [_ts(i) for i in range(500)]
    br._save_model_meta("3m", float("nan"), ["a"])
    m = br._load_model_meta("3m")
    assert m["source"] == "intraday"
    assert m["cv_acc"] is None


def test_sidecar_absent_returns_empty(br):
    assert br._load_model_meta("nope") == {}


def test_sidecar_corrupt_is_not_fatal(br):
    p = br._meta_path("3m")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write("{ this is not json")
    assert br._load_model_meta("3m") == {}


# ── F6-② 오염 검출 ───────────────────────────────────────────────────────────

def test_contamination_full_overlap(br):
    """현행이 전 구간을 학습했으면 홀드아웃 전부가 오염이다.

    프로덕션 실측 재현: intraday 학습창 4,800봉 ⊃ 홀드아웃 1,850봉 → 100%.
    """
    br._train_row_ts = [_ts(i) for i in range(5000)]
    br._save_model_meta("3m", float("nan"), ["a"])     # cutoff = 마지막 봉
    n, note = br._holdout_contamination("3m", 1850)
    assert n == 1850
    assert "100%" in note


def test_contamination_clean(br):
    """현행 cutoff가 홀드아웃 시작 이전이면 깨끗하다."""
    br._train_row_ts = [_ts(i) for i in range(5000)]
    br._save_model_meta("3m", 0.44, ["a"])
    p = br._meta_path("3m")
    meta = json.load(open(p, encoding="utf-8"))
    meta["train_cutoff_ts"] = br._train_row_ts[-1851]   # 홀드아웃 직전 봉
    json.dump(meta, open(p, "w", encoding="utf-8"))
    n, note = br._holdout_contamination("3m", 1850)
    assert n == 0 and note == "깨끗함"


def test_contamination_partial(br):
    br._train_row_ts = [_ts(i) for i in range(5000)]
    br._save_model_meta("3m", 0.44, ["a"])
    p = br._meta_path("3m")
    meta = json.load(open(p, encoding="utf-8"))
    meta["train_cutoff_ts"] = br._train_row_ts[-1000]   # 홀드아웃 중간
    json.dump(meta, open(p, "w", encoding="utf-8"))
    n, _ = br._holdout_contamination("3m", 1850)
    assert n == 851, "겹친 봉만 정확히 세야 한다"


def test_unknown_cutoff_is_treated_as_contaminated(br):
    """사이드카 없음(구버전 pkl) → -1. '모름'을 '깨끗함'으로 읽으면 가드가 무력화된다."""
    br._train_row_ts = [_ts(i) for i in range(5000)]
    n, note = br._holdout_contamination("3m", 1850)
    assert n == -1 and "미상" in note


def test_unknown_row_ts_is_treated_as_contaminated(br):
    """외부 주입 X 경로는 행↔ts 정렬 보장 불가 → -1."""
    br._train_row_ts = [_ts(i) for i in range(5000)]
    br._save_model_meta("3m", 0.44, ["a"])
    br._train_row_ts = None
    n, note = br._holdout_contamination("3m", 1850)
    assert n == -1 and "미상" in note


# ── F6-③ 판정 보류 연동 ──────────────────────────────────────────────────────

def test_fair_holdout_withholds_verdict_when_contaminated():
    """오염이면 `_measure_fair_holdout`이 **old_acc 자리에 None**을 반환하는가.

    종전에는 격차를 "하한"이라 적어두고 그대로 판정을 냈고, 그 6거래일치가 전부
    100% 오염이었다(432차가 6일간 판정을 못 낸 이유).

    `_measure_fair_holdout`은 실제 모델 학습을 수반해 단위테스트로 돌리기엔 무겁다.
    여기서는 **반환 계약**만 소스로 확인한다 — 실경로는 26주 실데이터 E2E로 검증했다
    (DECISION_LOG 456차 Wave 3: 홀드아웃 08-03 11:48~08-10 14:38, 오염 1850/1850).
    """
    import inspect
    src = inspect.getsource(BatchRetrainer._measure_fair_holdout)
    assert "_holdout_contamination" in src, "오염 검사가 호출되지 않는다"
    # 오염 시 두 번째 원소(old_acc)가 None이어야 판정 분기가 막힌다
    assert "return new_acc, None, H, (" in src, \
        "오염 시 old_acc=None 반환 계약이 깨졌다 — 판정이 그대로 나간다"


# ── F7-④ 판정 소스 게이트 ────────────────────────────────────────────────────

def test_verdict_source_default_is_unchanged_behavior():
    """기본값이 acc_txt여야 한다 — 이번 배포는 판정을 바꾸지 않는다.

    guard_fair 전환은 '오염 0봉 5거래일 누적 + 주간회의 승인' 후 별도 커밋.
    """
    from config.settings import EOD_GUARD_VERDICT_SOURCE
    assert EOD_GUARD_VERDICT_SOURCE == "acc_txt"


def test_verdict_source_accepts_only_known_values():
    from config.settings import EOD_GUARD_VERDICT_SOURCE
    assert EOD_GUARD_VERDICT_SOURCE in ("acc_txt", "guard_fair")


def test_guard_shadow_log_has_new_columns():
    """전환 조건('깨끗한 5거래일')을 SQL로 셀 수 있어야 한다."""
    import sqlite3
    from config.settings import TRADES_DB
    con = sqlite3.connect(TRADES_DB)
    cols = {r[1] for r in con.execute("PRAGMA table_info(guard_shadow_log)")}
    con.close()
    for c in ("fair_contaminated_bars", "incumbent_source",
              "incumbent_cutoff_ts", "verdict_source"):
        assert c in cols, "guard_shadow_log에 %s 컬럼 없음 (마이그레이션 미적용)" % c


def test_save_model_writes_sidecar(br, tmp_path):
    """_save_model 경로에서 사이드카가 실제로 생성되는가 (배관 연결 확인)."""
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.preprocessing import StandardScaler
    X = np.random.RandomState(0).randn(60, 3)
    y = np.array([0, 1, 2] * 20)
    mdl = HistGradientBoostingClassifier(max_iter=5).fit(X, y)
    sc = StandardScaler().fit(X)
    br._train_row_ts = [_ts(i) for i in range(60)]
    br._save_model("3m", mdl, sc, 0.4567, ["f0", "f1", "f2"])
    assert os.path.exists(br._meta_path("3m"))
    m = br._load_model_meta("3m")
    assert m["cv_acc"] == pytest.approx(0.4567)
    assert m["train_cutoff_ts"] == _ts(59)
