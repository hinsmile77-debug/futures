# -*- coding: utf-8 -*-
"""[MW0601 553차 / Phase 1] GP 숏 국면필터 이동평균(`ma20`/`ma60`) 배선 불변식.

무엇을 배선했나
---------------
사전등록 채널 `gp_rule_short_watch` 의 **필수** 국면 필터 「MA20 < MA60」.
이 필터를 빼면 숏 규칙이 −186.7pt(t=−2.71)로 뒤집힌다 — 선택이 아니라 규칙의 일부다.

🔴 왜 변형이 둘인가
-------------------
세션 리셋(`*_sess`)과 연속(`*_cont`) 중 어느 쪽이 규칙의 정본인지 **확정할 수 없다**.
  · 규칙의 **출처**는 사이보스 차트이고 HTS 이동평균은 날짜를 넘어 **연속**이다.
  · 규칙을 만든 **백테스트**는 세션 groupby 안에서 계산했을 가능성이 높다
    (`analysis/rules_backtest.py:81` 이 전부 그 형태). 211거래일 최종 스크립트가
    repo 에 없다.
한쪽을 조용히 고르면 그 선택이 60거래일 관측 결과에 그대로 섞인다. 그래서 둘 다 낸다.

🔴 그런데 차이는 「값」이 아니라 「가용성」이었다 — Phase 1 실측
--------------------------------------------------------------
9거래일 리플레이(2026-07-09 ~ 09-09) **동시측정 2,770분 전수에서 판정 불일치 0건.**
우연이 아니라 **구조**다: 둘 다 준비된 뒤에는 두 버퍼의 마지막 `slow` 봉이 **같은 봉**이라
값이 같을 수밖에 없다.
  ⇒ `ma_regime_agree` 는 「어느 쪽이 맞는가」를 **못 가른다**. 구조적으로 1.0 이어야 하는
    불변식이며, 0 이 나오면 버퍼 정렬이 깨졌다는 뜻으로만 유효하다.
    (이걸 판단 근거로 뒀다면 FP-CRITICAL PSI=0.0 계열의 **죽은 지표**가 될 뻔했다.)
  ⇒ 선택을 가르는 것은 **`ma_cont_only`** 다: 세션 리셋은 09:00+`slow`봉(=10:00)이 돼야
    준비되는데 숏 진입창은 **09:20** 부터다. 실측 **하루 39~43분**(진입창 331분의 약 12%)이
    「cont 는 답을 주는데 sess 는 못 주는」 구간이고 **그게 차이의 전부**다.

이 파일이 고정하는 것
---------------------
1. 순수 함수의 산술이 맞다(단순이동평균 · 부호 판정).
2. 워밍업이 **미측정**으로 나간다 — 「하락 아님(0)」으로 위장하지 않는다(계측 4원칙 ②).
3. 🔴 `ma_regime_agree` 가 판별력이 없다는 사실 자체를 고정한다(§2-b) — 다음 세션이
   그걸 근거로 사양을 고르지 않도록.
4. `reset_daily()` 가 연속 버퍼를 지우지 않는다(지우면 두 변형이 완전히 같아진다).
5. 라이브 경로에 **numpy 가 없다**(537차 BLAS delay-load 즉사 계열 차단).
6. 🔴 **소비자가 없다** — 진입·사이징·체크리스트 어디도 이 키를 읽지 않는다.
   GP_CROSS(540차)와 같은 규율이며, Phase 3 이전에는 매매 정책 무변경이어야 한다.
7. 사전등록(`ma_fast`/`ma_slow`)과 상수(`MA_REGIME_FAST/SLOW`)가 함께 움직인다.

실행:
    conda run -n py37_32 python -m pytest tests/test_553_ma_regime_features.py -v
"""
import ast
import io
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

os.environ["MIREUK_TEST_MODE"] = "1"

import pytest  # noqa: E402

from config.settings import (  # noqa: E402
    MA_REGIME_FAST, MA_REGIME_SLOW, VALIDATION_CAMPAIGN,
)
from features.feature_builder import compute_ma_regime_features  # noqa: E402
from utils.db_utils import fetch_prior_regular_closes  # noqa: E402

_SHORT = VALIDATION_CAMPAIGN["gp_rule_short_watch"]
_FB = os.path.join(_ROOT, "features", "feature_builder.py")

_F = "ma%d" % MA_REGIME_FAST
_S = "ma%d" % MA_REGIME_SLOW


def _read(path):
    with io.open(path, encoding="utf-8") as fh:
        return fh.read()


def _flat(n, v=100.0):
    return [v] * n


# ── 1. 산술 ──────────────────────────────────────────────────────────────────

def test_simple_moving_average_arithmetic():
    buf = list(range(1, MA_REGIME_SLOW + 1))          # 1..60
    out = compute_ma_regime_features(buf, buf, MA_REGIME_FAST, MA_REGIME_SLOW)
    exp_fast = sum(buf[-MA_REGIME_FAST:]) / float(MA_REGIME_FAST)
    exp_slow = sum(buf) / float(MA_REGIME_SLOW)
    assert out["%s_sess" % _F] == pytest.approx(exp_fast)
    assert out["%s_sess" % _S] == pytest.approx(exp_slow)


def test_regime_down_flag_is_ma_fast_below_ma_slow():
    """상승 계열이면 fast>slow → down=0, 하락 계열이면 down=1."""
    up = list(range(1, MA_REGIME_SLOW + 1))
    dn = list(range(MA_REGIME_SLOW, 0, -1))
    assert compute_ma_regime_features(up, up)["ma_regime_down_sess"] == 0.0
    assert compute_ma_regime_features(dn, dn)["ma_regime_down_sess"] == 1.0


def test_equal_mas_are_not_down():
    """fast == slow 는 「하락」이 아니다 — 엄격 부등호(<)여야 한다."""
    flat = _flat(MA_REGIME_SLOW)
    assert compute_ma_regime_features(flat, flat)["ma_regime_down_sess"] == 0.0


def test_two_variants_are_computed_independently():
    up = list(range(1, MA_REGIME_SLOW + 1))
    dn = list(range(MA_REGIME_SLOW, 0, -1))
    out = compute_ma_regime_features(up, dn)
    assert out["ma_regime_down_sess"] == 0.0
    assert out["ma_regime_down_cont"] == 1.0
    assert out["ma_regime_agree"] == 0.0
    assert out["ma_agree_measured"] is True


# ── 2. 워밍업은 미측정이다 (계측 4원칙 ②) ──────────────────────────────────

@pytest.mark.parametrize("n", [0, 1, MA_REGIME_FAST, MA_REGIME_SLOW - 1])
def test_warmup_is_unmeasured_not_zero(n):
    out = compute_ma_regime_features(_flat(n), _flat(n))
    assert out["ma_sess_ready"] is False
    assert out["ma_cont_ready"] is False
    # 🔴 값이 0.0 인 것 자체는 괜찮다 — **ready=False 가 그것을 「미측정」으로 표시**한다.
    #   소비자는 반드시 ready 를 먼저 봐야 한다.
    assert out["ma_regime_down_sess"] == 0.0
    assert out["ma_agree_measured"] is False


def test_agree_is_unmeasured_when_only_one_side_ready():
    """한쪽만 준비됐을 때 「일치」라고 말하면 안 된다."""
    out = compute_ma_regime_features(_flat(MA_REGIME_SLOW), _flat(3))
    assert out["ma_sess_ready"] is True
    assert out["ma_cont_ready"] is False
    assert out["ma_agree_measured"] is False
    assert out["ma_regime_agree"] == 0.0


def test_exactly_slow_bars_is_ready():
    """경계 — 정확히 slow 봉이면 준비 완료다(off-by-one 고정)."""
    assert compute_ma_regime_features(
        _flat(MA_REGIME_SLOW), _flat(MA_REGIME_SLOW))["ma_sess_ready"] is True
    assert compute_ma_regime_features(
        _flat(MA_REGIME_SLOW - 1), _flat(MA_REGIME_SLOW - 1))["ma_sess_ready"] is False


def test_key_set_is_stable():
    """키 집합이 바뀌면 사전등록·리포트가 조용히 어긋난다."""
    out = compute_ma_regime_features(_flat(MA_REGIME_SLOW), _flat(MA_REGIME_SLOW))
    assert set(out) == {
        "%s_sess" % _F, "%s_sess" % _S, "ma_sess_ready", "ma_regime_down_sess",
        "%s_cont" % _F, "%s_cont" % _S, "ma_cont_ready", "ma_regime_down_cont",
        "ma_regime_agree", "ma_agree_measured", "ma_cont_only",
    }


# ── 2-b. 🔴 실제 선택 축은 `ma_cont_only` 다 ────────────────────────────────
#
# Phase 1 리플레이 실측(9거래일 · 동시측정 2,770분)에서 두 변형의 판정 **불일치 0건**.
# 우연이 아니라 구조다 — 둘 다 준비된 뒤에는 두 버퍼의 마지막 slow 봉이 같은 봉이다.
# 그래서 `ma_regime_agree` 는 「어느 쪽이 맞는가」를 못 가른다. 차이는 **가용성**이고
# 그것을 재는 키가 `ma_cont_only` 다. 아래 두 테스트가 그 사실을 고정한다.

def test_agree_cannot_discriminate_when_buffers_share_the_tail():
    """둘 다 ready 이고 꼬리 slow 봉이 같으면 판정은 **반드시** 일치한다."""
    tail = list(range(1, MA_REGIME_SLOW + 1))
    cont = [999.0] * 40 + tail          # 앞부분이 달라도 꼬리가 같으면 값이 같다
    out = compute_ma_regime_features(tail, cont)
    assert out["ma_agree_measured"] is True
    assert out["ma_regime_agree"] == 1.0
    assert out["%s_sess" % _S] == pytest.approx(out["%s_cont" % _S])
    assert out["ma_cont_only"] == 0.0


def test_cont_only_marks_the_window_where_the_choice_matters():
    """cont 는 답을 주는데 sess 는 못 주는 구간 — 하루 39~43분(실측)."""
    out = compute_ma_regime_features(_flat(10), _flat(MA_REGIME_SLOW))
    assert out["ma_cont_ready"] is True
    assert out["ma_sess_ready"] is False
    assert out["ma_cont_only"] == 1.0
    # 반대로 둘 다 미준비면 선택 축도 미해당이다
    assert compute_ma_regime_features(_flat(3), _flat(3))["ma_cont_only"] == 0.0


# ── 3. 연속 버퍼는 일간 리셋 대상이 아니다 ──────────────────────────────────

def _method_body(src, name):
    """`    def <name>(` 부터 다음 동급 def 까지 잘라낸다.

    ⚠ `ast.get_source_segment` 는 Python 3.8+ 다 — 이 프로젝트 런타임은 **3.7 32-bit**
      이므로 쓸 수 없다(맨 처음 이 테스트가 AttributeError 로 깨진 이유).
    """
    i = src.index("    def %s(" % name)
    j = src.find("\n    def ", i + 1)
    return src[i:] if j < 0 else src[i:j]


def test_reset_daily_clears_session_buffer_but_not_continuous():
    """🔴 연속 버퍼에 clear() 가 추가되면 두 변형이 같아져 계측이 죽는다."""
    body = _method_body(_read(_FB), "reset_daily")
    assert "_close_history.clear()" in body, "세션 버퍼는 계속 리셋돼야 한다(317차)"
    assert "_close_history_cont.clear()" not in body, (
        "연속 MA 버퍼를 reset_daily 에서 지우고 있다 — 그러면 매일 세션 리셋과 같아져 "
        "ma_regime_agree 가 항상 1이 되고 「어느 쪽이 맞는가」가 계측에서 사라진다.")


def test_continuous_buffer_maxlen_covers_slow_window():
    """maxlen 이 slow 보다 작으면 연속 MA 가 영원히 준비되지 않는다."""
    src = _read(_FB)
    assert "self._close_history_cont: deque = deque(maxlen=MA_REGIME_SLOW + 2)" in src


def test_priming_runs_before_append():
    """프라이밍이 append 뒤에 오면 현재 봉이 버퍼에 두 번 들어간다."""
    src = _read(_FB)
    i_prime = src.index("self._prime_ma_cont_buffer(bar)")
    i_append = src.index("self._close_history_cont.append(close)")
    assert i_prime < i_append


# ── 4. 프라이밍 조회의 안전 계약 ────────────────────────────────────────────

def test_prime_query_rejects_bad_input_without_raising():
    assert fetch_prior_regular_closes("", 60) == []
    assert fetch_prior_regular_closes("2026-09-09 10:00:00", 0) == []
    assert fetch_prior_regular_closes("2026-09-09 10:00:00", None) == []


def test_prime_query_is_bounded():
    """상한이 없으면 장중에 전수 스캔이 될 수 있다(456차)."""
    src = _read(os.path.join(_ROOT, "utils", "db_utils.py"))
    i = src.index("def fetch_prior_regular_closes")
    body = src[i:i + 2400]
    assert "min(n, 600)" in body, "limit 상한이 없다"
    assert "ORDER BY ts DESC" in body and "LIMIT ?" in body


def test_prime_query_excludes_pre_and_post_session_bars():
    """프리장·장후 단일가가 섞이면 백테스트 패널과 창이 어긋난다."""
    src = _read(os.path.join(_ROOT, "utils", "db_utils.py"))
    i = src.index("def fetch_prior_regular_closes")
    body = src[i:i + 2400]
    assert "'09:00'" in body and "'15:09'" in body


def test_prime_query_returns_ascending_and_positive():
    rows = fetch_prior_regular_closes("2026-09-09 15:00:00", 30)
    if not rows:
        pytest.skip("raw_candles 에 해당 구간 데이터가 없다(다른 PC/신규 클론)")
    assert all(c > 0 for c in rows)
    assert len(rows) <= 30


# ── 5. numpy 금지 (537차) ───────────────────────────────────────────────────

def test_pure_function_has_no_numpy():
    """BLAS delay-load 실패는 예외가 아니라 **프로세스 즉사**다. 이 경로에 들이지 않는다.

    ⚠ 문자열 검색으로는 안 된다 — 주석·독스트링에 「numpy 를 쓰지 않는다」라고 적은
      것까지 잡힌다(초판이 그렇게 깨졌다). **AST 로 실제 참조만** 본다.
    """
    tree = ast.parse(_read(_FB))
    fn = next((n for n in ast.walk(tree)
               if isinstance(n, ast.FunctionDef)
               and n.name == "compute_ma_regime_features"), None)
    assert fn is not None, "compute_ma_regime_features 를 찾지 못했다"
    names = {n.id for n in ast.walk(fn) if isinstance(n, ast.Name)}
    assert "np" not in names and "numpy" not in names, (
        "순수 함수가 numpy 를 참조한다 — 537차 BLAS 즉사 계열을 이 경로에 들이지 말 것")
    imports = [n for n in ast.walk(fn) if isinstance(n, (ast.Import, ast.ImportFrom))]
    assert not imports, "함수 안에서 import 하지 않는다"


# ── 6. 🔴 소비자 없음 — 매매 정책 무변경 ────────────────────────────────────

_MA_KEYS = ("ma_regime_down_sess", "ma_regime_down_cont", "ma_sess_ready",
            "ma_cont_ready", "ma_regime_agree", "ma_cont_only",
            "%s_sess" % _F, "%s_cont" % _F)
_FORBIDDEN_DIRS = ("strategy", "model", "learning", "safety")


def test_no_consumer_in_trading_path():
    """진입·사이징·게이트가 이 키를 읽으면 Phase 1이 매매 정책을 바꾼 것이 된다."""
    hits = []
    for d in _FORBIDDEN_DIRS:
        root = os.path.join(_ROOT, d)
        if not os.path.isdir(root):
            continue
        for dirpath, _dirs, files in os.walk(root):
            for fn in files:
                if not fn.endswith(".py"):
                    continue
                fp = os.path.join(dirpath, fn)
                try:
                    txt = _read(fp)
                except Exception:
                    continue
                for k in _MA_KEYS:
                    if k in txt:
                        hits.append("%s: %s" % (os.path.relpath(fp, _ROOT), k))
    assert not hits, "MA 국면 키에 소비자가 생겼다 — 기록 전용이어야 한다:\n" + "\n".join(hits)


def test_main_py_does_not_consume_ma_keys():
    txt = _read(os.path.join(_ROOT, "main.py"))
    hits = [k for k in _MA_KEYS if k in txt]
    assert not hits, "main.py 가 MA 국면 키를 읽는다: %s" % hits


# ── 7. 사전등록 동기화 ──────────────────────────────────────────────────────

def test_preregistration_matches_constants():
    assert _SHORT["ma_fast"] == MA_REGIME_FAST
    assert _SHORT["ma_slow"] == MA_REGIME_SLOW


def test_wiring_date_is_recorded():
    assert _SHORT["feature_wired_date"] == "2026-09-10"


def test_ma_basis_is_decided_as_cont():
    """🔵 [2026-09-10 사용자 결정] `"cont"`(연속) 확정 — 이후 변경 금지.

    Phase 3 도전자가 이 값을 읽어 `ma_regime_down_cont` 를 소비한다. 관측 60거래일
    중에 바꾸면 규칙 자체가 바뀌는 것이라 사전등록이 무효가 된다(313차 ④ · 458차 D6).

    ⚠ 미확인으로 남는 것: 211거래일 백테스트 t=2.02 가 어느 쪽 기준이었는지 —
      최종 스크립트가 repo 에 없다. 전향 표본이 소급과 크게 갈리면 여기를 먼저 의심할 것.
    """
    assert _SHORT["ma_basis"] == "cont", (
        "ma_basis 는 2026-09-10 에 cont 로 확정됐다. 바꾸려면 DECISION_LOG 기록 + "
        "검증 시계 리셋이 필요하다.")
    assert _SHORT["ma_basis_options"] == ["sess", "cont"]


def test_decided_basis_has_a_live_feature_key():
    """확정된 basis 가 실제로 존재하는 키를 가리키는가 — 오타 하나로 Phase 3 가 죽는다."""
    out = compute_ma_regime_features(_flat(MA_REGIME_SLOW), _flat(MA_REGIME_SLOW))
    basis = _SHORT["ma_basis"]
    assert "ma_regime_down_%s" % basis in out
    assert "ma_%s_ready" % basis in out
    # 🔴 근거 키는 `ma_regime_agree` 가 아니다 — 구조적으로 항상 1.0 이라 못 가른다.
    assert _SHORT["ma_basis_evidence_key"] == "ma_cont_only"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
