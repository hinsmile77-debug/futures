"""[MW0602 460차] 공용 헬퍼 `_spearman` 동률 처리 회귀.

────────────────────────────────────────────────────────────────────────────
왜 이 테스트가 필요한가
────────────────────────────────────────────────────────────────────────────
종전 구현은 `np.argsort(np.argsort(x))`로 **서수순위**를 만들어 동률을 배열 위치
순서로 임의 분리했다. 두 축의 행 순서는 같은 쿼리 결과라 항상 동일하므로, 동률군
내부 순위가 양쪽 다 "시간 순서"를 대리하게 되고 그 공유된 위치 성분이 상관으로
읽힌다(부호는 항상 +). y가 전부 같은 값이면 y 순위가 정확히 0..n-1이 되어
분산이 0이 아니게 되므로 `sy < 1e-12` 가드도 통과해버렸다.

    _spearman([1,2,1,2,1,2], [0.3]*6)  →  구 +0.7143  /  정정 nan

이 버그는 2개월 넘게 살아 있었다. 아무 테스트도 이 헬퍼를 직접 부르지 않았고,
실제로 잡힌 것은 신규 채널의 **"관계 없는 합성데이터"** 가드 테스트가 SUPPORTS를
내면서였다. 그래서 여기서 헬퍼 자체를 고정한다.

동시에 **사본 2벌**을 함께 검사한다 — `scripts/atb_v2_build_and_eval.py`가 리포트의
구현을 복사하면서 "동일"을 표방하고 IC 게이트도 [1]과 같은 임계
(`ic_delta_min=0.03` / `ic_abs_min=0.05`)를 쓴다. 한 벌만 고쳐지면 두 채널의
IC 방법론이 조용히 갈라진다.

기준값은 `scipy.stats.spearmanr`다(런타임 py37_32에서는 MKL 지연로드 크래시 때문에
쓸 수 없어 자체 구현을 두는 것이지, 정의가 달라야 할 이유는 없다). scipy가 없으면
그 대조만 건너뛰고 나머지는 검사한다.

실행: <py310_64>\python.exe tests/test_460_spearman_ties.py   (COM/브로커 불필요)
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["MIREUK_TEST_MODE"] = "1"  # [422차] 프로덕션 로그·Slack 오염 차단

FAILURES = []


def check(name, cond):
    print("[%s] %s" % ("OK" if cond else "FAIL", name))
    if not cond:
        FAILURES.append(name)


def _load_impls():
    """검사 대상 사본 2벌. atb_v2는 별건 선재 결함으로 import가 막힐 수 있다."""
    from scripts.generate_validation_campaign_report import _spearman as sp_rep
    impls = [("리포트", sp_rep)]
    try:
        from scripts.atb_v2_build_and_eval import _spearman as sp_atb
        impls.append(("atb_v2", sp_atb))
    except Exception as e:
        # 454차부터 `learning.batch_retrainer._shadow_tb_row_is_live` 부재로 import가
        # 깨져 있다(그 스크립트는 EOD 미연결 수동 전용이라 발현되지 않았다).
        # 헬퍼만이라도 검사하기 위해 소스에서 함수 2개만 떼어 실행한다.
        print("  [note] atb_v2 모듈 import 불가(%s) → 소스에서 헬퍼만 추출" % e)
        src = _extract_helpers(os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "scripts", "atb_v2_build_and_eval.py"))
        ns = {"np": np}
        exec(compile(src, "atb_v2_helpers", "exec"), ns)
        if "_spearman" in ns:
            impls.append(("atb_v2(추출)", ns["_spearman"]))
        else:
            check("atb_v2에서 _spearman/_rankdata를 추출할 수 있다", False)
    return impls


def _extract_helpers(path):
    """`_rankdata`/`_spearman` 두 함수의 소스만 잘라낸다 (ast 기반, import 회피)."""
    import ast
    import io
    text = io.open(path, encoding="utf-8").read()
    lines = text.splitlines(True)
    tree = ast.parse(text)
    out = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in ("_rankdata", "_spearman"):
            out.append("".join(lines[node.lineno - 1:node.end_lineno]))
    return "\n\n".join(out)


# ══════════════════════ 1) 원 버그 케이스 ══════════════════════

def test_constant_axis_returns_nan():
    """y가 전부 같은 값이면 상관은 정의되지 않는다 — 구현은 +0.7143을 냈다."""
    for tag, sp in _load_impls():
        v = sp([1, 2, 1, 2, 1, 2], [0.3] * 6)
        check("%s: y 상수 → nan (구 +0.7143)" % tag, np.isnan(v))
        v2 = sp([2.0] * 40, list(np.linspace(0, 1, 40)))
        check("%s: x 상수 → nan" % tag, np.isnan(v2))


def test_tie_group_order_is_irrelevant():
    """동률군 안의 **배열 순서**가 결과를 바꾸면 안 된다.

    구 구현은 x=[1,1,1,2,2,2,3,3,3]과 무관한 y에 대해 +0.30을 냈다 — y가 동률군
    내부 위치와만 맞물린 순수 인공물이다.
    """
    x = [1, 1, 1, 2, 2, 2, 3, 3, 3]
    y = [1, 5, 9, 2, 6, 7, 3, 4, 8]
    for tag, sp in _load_impls():
        check("%s: 동률군 내부 배열순서는 상관에 기여하지 않는다 (구 +0.30)" % tag,
              abs(sp(x, y)) < 1e-12)


def test_no_positional_bias_under_independence():
    """양축 동률 + 동률군이 시간에 뭉친 경우 — 구 구현의 계통편향이 가장 큰 조건.

    독립 데이터(참값 rho=0)인데 구 구현은 평균 +0.11을 냈다(n=60 몬테카를로).
    여기서는 결정적 시드로 200회만 돌려 **평균 편향이 0 근방**임을 고정한다.
    """
    sp = _load_impls()[0][1]
    n = 60
    vals = []
    for t in range(200):
        r = np.random.RandomState(13000 + t)
        x = np.concatenate([np.full(n // 2, 3.0), np.full(n - n // 2, 1.0)])
        y = (r.rand(n) < 0.5).astype(float)
        v = sp(x, y)
        if not np.isnan(v):
            vals.append(v)
    mean = float(np.mean(vals))
    check("독립 데이터 평균 rho |%.4f| < 0.02 (구 구현 +0.11)" % mean, abs(mean) < 0.02)


# ══════════════════════ 2) 정의 자체 ══════════════════════

def test_matches_scipy():
    try:
        from scipy.stats import spearmanr
    except Exception as e:
        print("  [skip] scipy 없음(%s) — 런타임 py37_32에서는 정상" % e)
        return
    r = np.random.RandomState(20260810)
    cases = [
        ("연속 × 연속", r.randn(200), r.randn(200)),
        ("수량(1~3) × 승패플래그", r.randint(1, 4, 80).astype(float),
         (r.rand(80) < 0.5).astype(float)),
        ("pass_count × pnl(60%가 정확히 0)", r.randint(0, 5, 120).astype(float),
         np.where(r.rand(120) < 0.6, 0.0, r.randn(120))),
        ("동률 포함 단조", np.array([1., 1, 2, 2, 3, 3]), np.array([5., 5, 7, 7, 9, 9])),
    ]
    for tag, sp in _load_impls():
        for name, x, y in cases:
            with np.errstate(all="ignore"):
                ref = float(spearmanr(x, y).correlation)
            check("%s: scipy와 일치 — %s" % (tag, name), abs(sp(x, y) - ref) < 1e-9)


def test_monotone_and_guards():
    for tag, sp in _load_impls():
        check("%s: 완전 단조 = +1" % tag,
              abs(sp([1., 2, 3, 4, 5], [10., 20, 30, 40, 50]) - 1.0) < 1e-12)
        check("%s: 완전 역단조 = -1" % tag,
              abs(sp([1., 2, 3, 4, 5], [50., 40, 30, 20, 10]) + 1.0) < 1e-12)
        check("%s: 표본 3 미만 → nan" % tag, np.isnan(sp([1., 2], [3., 4])))
        check("%s: 길이 불일치 → nan" % tag, np.isnan(sp([1., 2, 3], [3., 4])))


def test_two_copies_agree():
    """사본 2벌이 같은 값을 낸다 — 한 벌만 고쳐지는 사고를 막는다."""
    impls = _load_impls()
    if len(impls) < 2:
        check("사본 2벌을 모두 로드했다", False)
        return
    r = np.random.RandomState(4242)
    for i in range(30):
        x = r.randint(0, 4, 50).astype(float)
        y = np.where(r.rand(50) < 0.4, 0.0, r.randn(50))
        a, b = impls[0][1](x, y), impls[1][1](x, y)
        same = (np.isnan(a) and np.isnan(b)) or abs(a - b) < 1e-12
        if not same:
            check("사본 2벌 값 일치 (case %d: %.6f vs %.6f)" % (i, a, b), False)
            return
    check("사본 2벌 값 일치 (동률 다수 난수 30케이스)", True)


def test_no_ordinal_rank_pattern_remains():
    """소스에 `argsort(argsort(...))` **호출**이 되살아나지 않았는지 — 재발 방지.

    docstring이 이 패턴을 설명 목적으로 인용하므로 문자열 검색이 아니라 AST로 본다.
    """
    import ast
    import io

    def _is_argsort(node):
        return (isinstance(node, ast.Call)
                and ((isinstance(node.func, ast.Attribute) and node.func.attr == "argsort")
                     or (isinstance(node.func, ast.Name) and node.func.id == "argsort")))

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    hits = []
    for rel in ("scripts/generate_validation_campaign_report.py",
                "scripts/atb_v2_build_and_eval.py"):
        tree = ast.parse(io.open(os.path.join(root, rel), encoding="utf-8").read())
        for node in ast.walk(tree):
            if _is_argsort(node) and node.args and _is_argsort(node.args[0]):
                hits.append("%s:%d" % (rel, node.lineno))
    check("서수순위 패턴 미잔존 (%s)" % (hits or "없음"), not hits)


if __name__ == "__main__":
    print("=" * 72)
    print("[MW0602 460차] 공용 헬퍼 _spearman 동률 처리 회귀 테스트")
    print("=" * 72)
    for fn in (
        test_constant_axis_returns_nan,
        test_tie_group_order_is_irrelevant,
        test_no_positional_bias_under_independence,
        test_matches_scipy,
        test_monotone_and_guards,
        test_two_copies_agree,
        test_no_ordinal_rank_pattern_remains,
    ):
        print("\n-- %s" % fn.__name__)
        fn()
    print("\n" + "=" * 72)
    if FAILURES:
        print("실패 %d건:" % len(FAILURES))
        for f in FAILURES:
            print("  - %s" % f)
        sys.exit(1)
    print("전부 통과")
