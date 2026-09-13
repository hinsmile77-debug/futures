# -*- coding: utf-8 -*-
"""[MW0601 500차 4단계] 구성적 중복 검출 + CORE 우선 시계 스크린 — SOP §3 B-5 / §2 A-6.

────────────────────────────────────────────────────────────────────────────
왜 필요한가 — 선형 상관은 결정론적 파생을 놓친다
────────────────────────────────────────────────────────────────────────────
`core_feature_discovery.find_dup_groups()` 는 Pearson |r| >= 0.99 로 중복을 묶는다.
그런데 2026-08-30 실측(n=7,527):

    ofi_imbalance ≡ round(ofi_norm/3, 3)   |r| = 0.9999  → 잡힌다
    ofi_pressure  ≡ sign(ofi_norm)         |r| = 0.4967  → 🔴 놓친다
    |cvd_divergence| ≡ min(cvd_slope, 1)   |r| = 0.0262  → 🔴 놓친다

뒤의 둘은 **5,289/5,289 정확 일치하는 항등식**이다. 부호·절대값 같은 비선형 파생은
상관이 낮게 나오지만 정보는 완전히 같다. 이걸 독립 신호로 세면 계열 검정의
**유효 자유도가 무너진다**(SOP §1 오측정 #9 — 수급 5피처를 5개로 세어 판정 미달
p=0.1426 을 자초한 사례).

  C1  scale 관계를 잡는다 (b = k*a)
  C2  sign 관계를 잡는다  ← 상관 0.50 이라 기존 방식이 못 잡던 것
  C3  abs 관계를 잡는다   ← 상관 0.03
  C4  무관한 계열을 중복으로 오탐하지 않는다
  C5  상태·가용성 플래그는 대상에서 제외된다 (경보 피로 방지)
  C6  검사가 **사전필터 탈락분까지** 본다 (부호형 중복이 사는 곳)
  C7  CORE 우선 시계 스크린이 배선돼 있고 건강 대조군을 함께 낸다

실행: python tests/test_500_constructive_dup.py   (COM/브로커·DB 불필요)
            또는 pytest tests/test_500_constructive_dup.py

🔴 [MW0602 564차 후속3 / `O-77-C` 1단계] **스크립트형 → pytest 전환.**

검사 문구와 조건은 **원문 그대로**다. 블록을 함수로 감싸 그룹별 테스트에서 부르고,
공유 setup(합성 데이터·소스 읽기)은 **지연 생성**으로 바꿔 임포트 부작용을 없앴다
— 모듈 최상위에 계산을 남기면 `O-77` 2차층(수집 중 중단)이 재발한다.

직접 실행 경로는 그대로다(파일 하단 러너). py37_32 에 pytest 가 없어 그것이
유일한 수동 확인 수단이다.
"""

import io
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

# ⚠ `utf8_console()` 은 import 시점에 부르지 않는다 — 그 함수 docstring 의 지시.

import scripts.core_feature_discovery as D  # noqa: E402

FAILURES = []


def check(name, cond, detail=""):
    print("[%s] %s%s" % ("OK" if cond else "FAIL", name,
                         ("\n         → %s" % detail) if detail and not cond else ""))
    if not cond:
        FAILURES.append(name)
    return cond


def _assert_group(fn):
    """블록을 실행하고 **그 안에서 난 실패만** 모아 단언한다."""
    before = len(FAILURES)
    fn()
    new = FAILURES[before:]
    assert not new, "실패 %d건 — %s" % (len(new), " / ".join(new))


# ── 공유 setup — 지연 생성 (임포트 시점에 돌리지 않는다) ──────────────

pairs = None
X = None
_SRC_CACHE = {}


def _data():
    """합성 데이터와 검출 결과를 한 번만 만든다. 원본 모듈 최상위 블록 그대로."""
    global pairs, X
    if pairs is not None:
        return
    rng = np.random.RandomState(500)
    n = 1200
    base = rng.normal(0, 0.05, n)                 # ofi_norm 유사
    mag = np.abs(rng.normal(0, 0.3, n))           # cvd_slope 유사 (음수 없음)
    sgn = np.where(rng.rand(n) < 0.5, -1.0, 1.0)  # 독립 부호

    names = ["base", "base_scaled", "base_sign", "mag", "mag_signed",
             "unrelated", "opt_chain_available"]
    X = np.column_stack([
        base,
        np.round(base / 3.0, 3),                  # scale  (ofi_imbalance 관계)
        np.sign(base),                            # sign   (ofi_pressure 관계)
        mag,
        sgn * mag,                                # abs    (cvd_divergence 관계)
        rng.normal(0, 1, n),                      # 무관
        (np.abs(base) > 1e-12).astype(float),     # 가용성 플래그
    ])

    pairs = {(a, b): rel for a, b, rel in D.find_constructive_dups(names, X)}


def _src():
    """`core_feature_discovery.py` 원문 — C6·C7 이 정적으로 검사한다."""
    if "src" not in _SRC_CACHE:
        src = io.open(os.path.join(ROOT, "scripts", "core_feature_discovery.py"),
                      encoding="utf-8").read()
        _SRC_CACHE["src"] = src
    return _SRC_CACHE["src"]


def has(a, b, kind):
    rel = pairs.get((a, b))
    return rel is not None and rel.startswith(kind)


# ── C1~C3b — 구성적 관계 검출 ──────────────────────────────────

def _c1_c3():
    _data()
    check("C1 scale 관계를 잡는다 (base → base_scaled)",
          has("base", "base_scaled", "scale"),
          "검출: %r" % pairs.get(("base", "base_scaled")))
    check("C2 sign 관계를 잡는다 (base → base_sign)  ← |r|≈0.50 이라 기존 방식이 놓치던 것",
          has("base", "base_sign", "sign"),
          "검출: %r" % pairs.get(("base", "base_sign")))
    check("C3 abs 관계를 잡는다 (mag → mag_signed)  ← |r|≈0.03",
          has("mag", "mag_signed", "abs"),
          "검출: %r" % pairs.get(("mag", "mag_signed")))
    _r = abs(np.corrcoef(X[:, 3], X[:, 4])[0, 1])
    check("C3b 그 쌍의 Pearson |r|=%.4f 은 실제로 DUP 임계(%.2f) 미만이다"
          % (_r, D.DUP_R_THRESHOLD), _r < D.DUP_R_THRESHOLD,
          "합성 데이터가 실제 상황을 재현하지 못하고 있다")


def test_C1_C3_constructive_relations_detected():
    """scale·sign·abs 관계를 잡는가 — 선형 상관이 놓치는 결정론적 파생."""
    _assert_group(_c1_c3)


# ── C4~C5b — 오탐·상태플래그 제외 ──────────────────────────────

def _c4_c5():
    _data()
    check("C4 무관 계열을 오탐하지 않는다",
          not any(a == "unrelated" or b == "unrelated" for a, b in pairs),
          "오탐: %s" % [p for p in pairs if "unrelated" in p])
    check("C5 상태·가용성 플래그는 대상에서 제외된다",
          not any(b == "opt_chain_available" for a, b in pairs),
          "가용성 플래그를 대상에 넣으면 실측 50쌍이 쏟아져 진짜 중복이 묻힌다")
    check("C5b 플래그 판정이 feature_health_report 와 같은 출처를 쓴다",
          D._is_status_flag("opt_chain_available") and D._is_status_flag("cvd_measured")
          and not D._is_status_flag("ofi_norm"))


def test_C4_C5_no_false_positives_and_flags_excluded():
    """무관 계열을 오탐하지 않고 상태·가용성 플래그는 대상에서 빠지는가."""
    _assert_group(_c4_c5)


# C6 — 사전필터 탈락분까지 검사하는가 (정적 검사)

def _c6():
    src = _src()
    check("C6 구성적 중복 검사가 사전필터 탈락분(all_names/all_X)까지 본다",
          '"all_names"' in src and '"all_X"' in src
          and 'LAST_SCREENING_REPORT.get("all_names")' in src,
          "MIN_DISTINCT=20 이 떨어뜨리는 저해상도 피처가 부호형 중복이 사는 곳이다 "
          "— ofi_pressure(고유값 3)가 그 예")


def test_C6_prefilter_dropouts_are_included():
    """사전필터 탈락분(all_names/all_X)까지 보는가 — 부호형 중복이 사는 곳."""
    _assert_group(_c6)


# C7 — CORE 우선 시계 스크린

def _c7():
    src = _src()
    check("C7a CORE 우선 시계 스크린이 배선돼 있다",
          "[CORE 시계]" in src and "temporal_profile_series" in src,
          "CORE 는 오염되면 전 호라이즌에 번지는데 전수 결과에 묻히면 안 보인다(SOP A-6)")
    # 🔴 [MW0602 체리픽 조정] 원본은 `from config.constants import CORE_FEATURES` 를
    #   문자열로 확인한다. 이 브랜치에서 그 상수는 **레거시**(468차 F-3 보호축)라,
    #   그대로면 A-6 스크린이 실집행이 아닌 레거시 이름을 본다. 실집행 정의
    #   (`CORE_FEATURES_BY_GROUP["short"]`) 직독을 요구하도록 바꾼다.
    check("C7b[MW0602] 실집행 CORE 정의를 직접 읽는다 — 레거시 상수가 아니라",
          "CORE_FEATURES_BY_GROUP" in src
          and "from config.constants import CORE_FEATURES" not in src,
          "2026-08-30까지 문서(cvd_divergence)와 실집행(cvd_delta_norm)이 달랐다. "
          "이 브랜치는 constants 를 레거시로 남기므로 settings 를 직독해야 한다")
    check("C7c 건강 대조군을 함께 낸다",
          "cvd_divergence" in src and "cvd_slope" in src and '"cvd"' in src,
          "절대값만으로는 '0.55 가 나쁜가'를 판단할 수 없다(SOP A-6-3)")
    check("C7d 계측 실패를 '이상 없음'으로 넘기지 않는다",
          "계측 실패이지 '이상 없음'이 아니다" in src)


def test_C7_core_temporal_screen_wired():
    """CORE 우선 시계 스크린 배선 + 건강 대조군 + 계측 실패 구분."""
    _assert_group(_c7)


if __name__ == "__main__":
    from utils.analysis_db import utf8_console

    utf8_console()
    fns = [(n, f) for n, f in sorted(globals().items())
           if n.startswith("test_") and callable(f)]
    ok = fail = 0
    for name, fn in fns:
        try:
            fn()
            print("  PASS %s" % name)
            ok += 1
        except Exception as e:
            print("  FAIL %s -> %s: %s" % (name, type(e).__name__, e))
            fail += 1
    print("")
    print("%d passed, %d failed (of %d)" % (ok, fail, len(fns)))
    sys.exit(1 if fail else 0)
