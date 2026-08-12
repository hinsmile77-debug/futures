# tests/test_458_guard_clean_tail.py
"""[MW0601 458차] 품질 가드 P1-A/P1-B/P1-C + P2-C 계측 회귀 테스트.

배경(`docs/정기점검/매일점검/MW0601-20260812-이상점3건-딥다이브.md`):
456차 전환조건 ①("오염 0봉 EOD 5거래일 연속")은 **원리적으로 달성 불가**였다 —
장중 재학습이 매일 pkl을 덮어써 cutoff를 당일 12:00 근방으로 밀어올리므로
5거래일 폭 홀드아웃의 91%가 항상 오염된다(2026-08-12 실측 1850봉 중 1691봉).
그 결과 EOD 모델 교체 6/6이 무검증 통과(ghost_bypass)하고 있었다.

P1-A는 오염일에도 살아남는 유일한 공정 표본(현행 cutoff 이후 꼬리)을 계측한다.
**판정 경로는 무변경** — 이 테스트들이 그 불변식을 지킨다.
"""

import inspect
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from learning.batch_retrainer import BatchRetrainer  # noqa: E402


# ── P1-A 반환 계약 ───────────────────────────────────────────────────────────

def test_fair_holdout_returns_five_tuple():
    """`_measure_fair_holdout`의 모든 return이 5-튜플이어야 한다.

    호출부가 5개로 언패킹하므로 하나라도 4-튜플이면 그 경로에서 ValueError로
    EOD 재학습이 죽는다. 조기 반환 경로가 6개나 되므로 소스 전수 검사한다.
    """
    import ast
    import textwrap
    src = textwrap.dedent(inspect.getsource(BatchRetrainer._measure_fair_holdout))
    fn = ast.parse(src).body[0]
    returns = [n for n in ast.walk(fn) if isinstance(n, ast.Return)]
    assert returns, "return 문을 찾지 못했다"
    for r in returns:
        assert isinstance(r.value, ast.Tuple), \
            "line %d: 튜플이 아닌 return" % r.lineno
        assert len(r.value.elts) == 5, \
            "line %d: %d-튜플 (5여야 한다)" % (r.lineno, len(r.value.elts))


def test_contaminated_path_still_returns_none_old_acc():
    """[456차 F6 불변식] 오염 시 old_acc=None — P1-A가 판정을 열지 않았는가.

    P1-A는 **관측만** 추가한다. 이 계약이 깨지면 오염된 비교가 판정에 쓰인다.
    """
    src = inspect.getsource(BatchRetrainer._measure_fair_holdout)
    assert "return new_acc, None, H, (" in src, \
        "오염 시 old_acc=None 반환 계약이 깨졌다 — 판정이 그대로 나간다"


def test_clean_tail_helper_exists_and_is_side_effect_free():
    """꼬리 대조 헬퍼가 존재하고 예외를 삼키는가(계측이 학습을 막으면 안 된다)."""
    assert hasattr(BatchRetrainer, "_clean_tail_matched")
    src = inspect.getsource(BatchRetrainer._clean_tail_matched)
    assert "except Exception" in src, "계측 실패가 학습을 중단시킬 수 있다"


# ── P1-A 산출 로직 ───────────────────────────────────────────────────────────

class _FakeBR(object):
    """`_clean_tail_matched`만 떼어 쓰기 위한 최소 객체."""

    def __init__(self, cutoff, ts_list):
        self._cutoff = cutoff
        self._train_row_ts = ts_list

    def _load_model_meta(self, horizon_key):
        return {"train_cutoff_ts": self._cutoff}

    _clean_tail_matched = BatchRetrainer._clean_tail_matched


def _ts(i):
    return "2026-08-%02d %02d:%02d:00" % (5 + i // 400, 9 + (i % 400) // 60, i % 60)


def test_clean_tail_selects_only_post_cutoff_bars():
    """cutoff 이후 봉만 골라 매치드 대조하는가 — 핵심 산출 검증."""
    import numpy as np
    H = 10
    ts_list = ["2026-08-12 %02d:00:00" % h for h in range(1, 11)]
    # cutoff=05:00 → 06,07,08,09,10시 = 5봉만 깨끗
    br = _FakeBR("2026-08-12 05:00:00", ts_list)
    y_ho = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    # 도전자는 깨끗 구간(뒤 5봉)을 전부 맞히고, 현행은 전부 틀린다
    pred_new = np.array([0, 0, 0, 0, 0, 1, 1, 1, 1, 1])
    pred_old = np.array([1, 1, 1, 1, 1, 0, 0, 0, 0, 0])
    out = br._clean_tail_matched("3m", H, y_ho, pred_new, pred_old)
    assert out["clean_n"] == 5, "깨끗한 꼬리 봉 수가 틀렸다: %r" % out
    assert out["clean_new"] == 1.0, "도전자 채점이 오염 구간을 포함했다"
    assert out["clean_old"] == 0.0, "현행 채점이 오염 구간을 포함했다"


def test_clean_tail_reports_zero_when_cutoff_covers_all():
    """cutoff가 홀드아웃 전체를 덮으면 '0봉'을 명시하고 값은 None이어야 한다.

    계측 4원칙 ②: '표본 없음'을 '적중률 0.0'으로 표현하지 않는다.
    """
    import numpy as np
    ts_list = ["2026-08-12 %02d:00:00" % h for h in range(1, 6)]
    br = _FakeBR("2026-08-12 23:59:00", ts_list)  # 전부 학습됨
    out = br._clean_tail_matched(
        "3m", 5, np.array([1] * 5), np.array([1] * 5), np.array([0] * 5))
    assert out["clean_n"] == 0
    assert out["clean_new"] is None and out["clean_old"] is None, \
        "표본 0인데 0.0을 반환하면 롤링 집계가 오염된다"
    assert "0봉" in out["clean_note"]


def test_clean_tail_unknown_ts_does_not_fabricate():
    """타임스탬프 미상이면 값을 만들어내지 않는다(계측 4원칙 ④ 폴백 가시화)."""
    import numpy as np
    br = _FakeBR("2026-08-12 05:00:00", None)
    out = br._clean_tail_matched(
        "3m", 5, np.array([1] * 5), np.array([1] * 5), np.array([0] * 5))
    assert out["clean_new"] is None and out["clean_n"] == 0
    assert "미상" in out["clean_note"]


# ── P1-B 관찰 계측 ───────────────────────────────────────────────────────────

def test_live_frequential_distinguishes_empty_from_zero():
    """표본 없음은 (None, 0)이어야 한다 — 0.0 적중률과 구분(계측 4원칙 ②)."""
    from utils.db_utils import fetch_live_frequential_acc
    acc, n = fetch_live_frequential_acc("3m", "1999-01-01")
    assert acc is None and n == 0, "빈 표본이 0.0으로 위장됐다: %r" % ((acc, n),)


def test_guard_shadow_accepts_new_columns():
    """save_guard_shadow가 P1-A/P1-B 인자를 받는가 (시그니처 계약)."""
    from utils.db_utils import save_guard_shadow
    params = inspect.signature(save_guard_shadow).parameters
    for p in ("clean_new", "clean_old", "clean_n", "clean_note",
              "live_acc", "live_n"):
        assert p in params, "save_guard_shadow에 %s 인자가 없다" % p
        assert params[p].default is None, "%s 기본값은 None이어야 한다" % p


# ── P1-C 로그 정직성 ─────────────────────────────────────────────────────────

def test_ghost_bypass_message_includes_oos():
    """⑤안 교체 로그가 cv만이 아니라 최신 OOS를 함께 밝히는가.

    2026-08-12 실측 3m: cv=0.4215 vs 최신OOS=0.3000 (−12pp). cv만 보이면
    운영자가 교체를 실제보다 안전하게 인지한다(계측 4원칙 ④).
    """
    src = inspect.getsource(BatchRetrainer._train_horizon)
    assert "최신OOS" in src, "ghost_bypass 판정문에 최신 OOS 병기가 없다"


# ── P2-C 만성 제외 가시화 ────────────────────────────────────────────────────

def test_chronic_suffix_marks_first_observation(tmp_path, monkeypatch):
    """최초 관측은 일수를 단정하지 않는다(미측정 ≠ 1일)."""
    import features.horizon_feature_registry as reg
    monkeypatch.setattr(reg, "_CHRONIC_PATH", str(tmp_path / "s.json"))
    monkeypatch.setattr(reg, "_CHRONIC_CACHE", None)
    s = reg._chronic_suffix("30m", ["opt_chain_pcr"])
    assert "최초관측" in s, s


def test_chronic_suffix_counts_consecutive_days(tmp_path, monkeypatch):
    """이전 기록이 있으면 누적 일수를 드러낸다 — 292차·411차·458차 재발견 방지."""
    import features.horizon_feature_registry as reg
    p = tmp_path / "s.json"
    p.write_text(json.dumps({
        "30m": {"opt_chain_pcr": {"first_seen": "2026-07-15",
                                  "last_seen": "2026-08-11", "days": 21}}
    }), encoding="utf-8")
    monkeypatch.setattr(reg, "_CHRONIC_PATH", str(p))
    monkeypatch.setattr(reg, "_CHRONIC_CACHE", None)
    s = reg._chronic_suffix("30m", ["opt_chain_pcr"])
    assert "22거래일째" in s, s


def test_chronic_suffix_resets_when_feature_returns(tmp_path, monkeypatch):
    """다시 가용해지면 상태에서 빠진다 — 연속성이 끊기면 일수도 끊긴다."""
    import features.horizon_feature_registry as reg
    p = tmp_path / "s.json"
    p.write_text(json.dumps({
        "30m": {"gone_feat": {"first_seen": "2026-07-15",
                              "last_seen": "2026-08-11", "days": 21}}
    }), encoding="utf-8")
    monkeypatch.setattr(reg, "_CHRONIC_PATH", str(p))
    monkeypatch.setattr(reg, "_CHRONIC_CACHE", None)
    reg._chronic_suffix("30m", ["other_feat"])
    saved = json.loads(p.read_text(encoding="utf-8"))
    assert "gone_feat" not in saved.get("30m", {}), "복귀한 피처가 상태에 남았다"


def test_chronic_suffix_never_raises(monkeypatch):
    """계측 실패가 학습 로그 경로를 죽이지 않는다."""
    import features.horizon_feature_registry as reg
    monkeypatch.setattr(reg, "_CHRONIC_PATH", "/nonexistent\x00/bad.json")
    monkeypatch.setattr(reg, "_CHRONIC_CACHE", None)
    assert isinstance(reg._chronic_suffix("30m", ["x"]), str)


# ── 판정 무변경 불변식 ───────────────────────────────────────────────────────

def test_verdict_source_still_acc_txt():
    """458차는 판정 소스를 바꾸지 않는다 — P1-A는 관측 축적 단계다."""
    from config.settings import EOD_GUARD_VERDICT_SOURCE
    assert EOD_GUARD_VERDICT_SOURCE == "acc_txt", \
        "guard_fair 전환은 롤링 표본 누적 + 주간회의 승인 후 별도 커밋이다"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
