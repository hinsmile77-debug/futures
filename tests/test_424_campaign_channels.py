"""[MW0602 424차 후속] 캠페인 신설 3채널([35]~[37]) + 리포트 생성 크래시 회귀.

────────────────────────────────────────────────────────────────────────────
왜 "리포트가 죽는 클래스"를 통째로 검사하는가
────────────────────────────────────────────────────────────────────────────
`generate_validation_campaign_report.py`는 **한 주에 세 번** 생성 자체가 죽었다.
셋 다 원인이 다르지만 발현 조건이 같다 — `campaign_due()`가 **금요일에만** 돌아서
평일에는 아무도 모른다.

  1. `[33]` `"BH FDR 10%"` 미이스케이프 → TypeError   (421차 후속10 → 422차 후속 수정)
  2. `[30]` `_row_is_live()` **정의 없이 호출** → NameError (419차 도입 → 424차 후속 수정)
  3. `[36]/[37]` `%+,.0f` → ValueError                (424차 후속 자작, 즉시 수정)

3번은 %-포매팅이 콤마 플래그를 지원하지 않아서다(`format()`/f-string 전용).
1·3번은 문자열, 2번은 이름 해석 — 그래서 아래 두 가지를 **파일 전체에 대해** 검사한다.

  (A) 모듈 내부 헬퍼(`_foo`)를 호출하는데 정의가 없는 곳이 있는가  → 2번 클래스
  (B) `%`-포맷 문자열에 콤마 플래그가 남아 있는가                  → 3번 클래스

이 두 검사는 채널이 늘어날수록 가치가 커진다. 깨지면 **금요일에 리포트가 안 나온다**.

────────────────────────────────────────────────────────────────────────────
채널 판정 로직
────────────────────────────────────────────────────────────────────────────
[35]~[37]은 전부 **일자단위 부호검정**(313차)으로 판정한다. 포지션 단위 z검정을
쓰지 않는 이유는 같은 날 진입들이 같은 레짐·같은 모델 스냅샷을 공유해 독립
관측치가 아니기 때문이다(372차가 PSI 재보정에서 실측).

특히 [37]은 그 규율 자체가 존재 이유다 — 0804 실측에서 포지션 누적
-1,455,546원과 일자단위 p=0.4531이 정면으로 갈렸다. 아래 테스트는 그 **정확한
수치를 고정**한다. 판정식이 바뀌면 여기서 깨져야 한다.

실행: python tests/test_424_campaign_channels.py   (COM/브로커 불필요)
"""
import ast
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["MIREUK_TEST_MODE"] = "1"  # [422차] 프로덕션 로그·Slack 오염 차단

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_REPORT_PY = os.path.join(_ROOT, "scripts", "generate_validation_campaign_report.py")

FAILURES = []


def check(name, cond):
    print("[%s] %s" % ("OK" if cond else "FAIL", name))
    if not cond:
        FAILURES.append(name)


# ══════════════ (A) 미정의 모듈 헬퍼 호출 — [30] NameError 클래스 ══════════════

def test_no_undefined_module_helpers():
    """`_foo(...)` 호출인데 모듈에 `def _foo`도 `_foo =`도 없는 경우를 찾는다.

    419차가 `_row_is_live()`를 호출만 하고 정의하지 않아 리포트 전체가 죽었다.
    호출부가 try/except 밖이면 NameError는 build_report()를 통째로 무너뜨린다.
    """
    tree = ast.parse(io.open(_REPORT_PY, encoding="utf-8").read())
    defined = set(dir(__builtins__)) if isinstance(__builtins__, type(sys)) else set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defined.add(node.name)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            defined.add(node.id)
        elif isinstance(node, ast.arg):
            defined.add(node.arg)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for a in node.names:
                defined.add((a.asname or a.name).split(".")[0])
    missing = set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id.startswith("_")
                and node.func.id not in defined):
            missing.add(node.func.id)
    check("모듈 private 헬퍼 호출이 전부 정의돼 있다 (%s)" % (sorted(missing) or "없음"),
          not missing)


# ══════════ (B) %-포맷 콤마 플래그 — [36]/[37] ValueError 클래스 ══════════

def test_no_comma_flag_in_percent_format():
    """`%+,.0f` / `%,d` 같은 콤마 플래그는 %-포매팅에서 ValueError다.

    천단위 구분이 필요하면 `_fmt_krw()` 또는 `format(v, ',')`를 쓸 것.
    """
    import re
    # **실제 포맷 연산자(`"..." % x`)의 좌변만** 검사한다. 소스 전체를 정규식으로
    # 훑으면 주석·독스트링에 적힌 설명 문구까지 잡혀(예: `_fmt_krw`가 바로 이
    # 함정을 경고하는 독스트링) 영원히 빨간불이 된다 — 잡아야 할 것만 잡는다.
    pat = re.compile(r"%[-+ #0]*,[0-9.]*[diouxXeEfFgGs]")
    tree = ast.parse(io.open(_REPORT_PY, encoding="utf-8").read())
    bad = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod)):
            continue
        left = node.left
        val = getattr(left, "s", None)
        if val is None and isinstance(left, ast.Constant):
            val = left.value
        if isinstance(val, str):
            bad += [(node.lineno, f) for f in pat.findall(val)]
    # ⚠ 이 검사 문구 자체에 `%-` 를 쓰면 안 된다 — 파이썬이 `%-포`를 포맷 스펙으로
    #   읽어 ValueError를 낸다(이 테스트를 처음 짤 때 실제로 걸렸다).
    check("퍼센트 포맷 연산자에 콤마 플래그가 없다 (%s)" % (bad or "없음"), not bad)


# ══════════════════════ 헬퍼 단위 검증 ══════════════════════

def _load_report_module():
    import importlib
    sys.path.insert(0, os.path.join(_ROOT, "scripts"))
    return importlib.import_module("generate_validation_campaign_report")


def test_sign_test_p():
    m = _load_report_module()
    # 0804 [37] 실측: 짝지은 7일 중 mean-revert 우세 2일
    check("부호검정 k=2,n=7 → p=0.4531 (0804 [37] 실측 고정)",
          abs(m._sign_test_p(2, 7) - 0.453125) < 1e-9)
    check("부호검정 k=0,n=5 → p=0.0625", abs(m._sign_test_p(0, 5) - 0.0625) < 1e-9)
    check("부호검정 k=5,n=10 → p=1.0 (완전 무작위)",
          abs(m._sign_test_p(5, 10) - 1.0) < 1e-9)
    check("부호검정 n=0 → p=1.0 (0나눗셈 방어)", m._sign_test_p(0, 0) == 1.0)


def test_paired_day_summary_reproduces_0804():
    """0804 [37] 딥다이브 수치를 그대로 재현해야 한다.

    일자별 (mean-revert 평균 − 그 외 평균) pt, 양쪽이 다 있는 7거래일:
      07-15 +5.38 / 07-16 -3.27 / 07-20 +1.76 / 07-21 -3.83
      07-22 -2.93 / 07-28 -2.99 / 08-04 -5.53
    """
    m = _load_report_module()
    diffs = [5.38, -3.27, 1.76, -3.83, -2.93, -2.99, -5.53]
    out = m._paired_day_summary(diffs, 0.05)
    check("짝지은 거래일 7일", out["paired_days"] == 7)
    check("MR 우세 2일", out["days_positive"] == 2)
    check("평균차 ≈ -1.63pt (실측 -1.6288)", abs(out["mean_diff"] + 1.63) < 0.02)
    check("부호검정 p=0.4531", abs(out["sign_p"] - 0.4531) < 1e-4)
    check("t ≈ -1.13 (실측 -1.133)", abs(out["t_stat"] + 1.13) < 0.03)
    check("유의하지 않다 → 조치 금지 판정", out["significant"] is False)


def test_paired_day_summary_edge():
    m = _load_report_module()
    check("빈 입력이 죽지 않는다", m._paired_day_summary([], 0.05)["paired_days"] == 0)
    one = m._paired_day_summary([1.0], 0.05)
    check("1일짜리는 t를 내지 않는다(313차 단일일 판정 금지)",
          "t_stat" not in one)
    same = m._paired_day_summary([2.0, 2.0, 2.0], 0.05)
    check("분산 0이어도 죽지 않는다", "sign_p" in same)


def test_fmt_krw():
    m = _load_report_module()
    check("_fmt_krw 양수에 부호+콤마", m._fmt_krw(587344) == "+587,344")
    check("_fmt_krw 음수", m._fmt_krw(-1455546) == "-1,455,546")
    check("_fmt_krw 실수 반올림", m._fmt_krw(-26943.4) == "-26,943")
    check("_fmt_krw None 방어", m._fmt_krw(None) == "—")


def test_row_is_live():
    """424차 후속이 복구한 헬퍼 — 백필 행을 걸러야 한다."""
    m = _load_report_module()
    check("백필 마커(0.3) → 라이브 아님",
          m._row_is_live('{"feature_quality_score": 0.3}') is False)
    check("정상 품질점수(0.94) → 라이브",
          m._row_is_live('{"feature_quality_score": 0.94}') is True)
    check("마커 키 없음 → 라이브(백필 도입 이전 스키마)",
          m._row_is_live('{"ofi_norm": 0.1}') is True)
    check("dict 직접 전달도 허용", m._row_is_live({"feature_quality_score": 0.3}) is False)
    check("깨진 JSON → False(집계에서 조용히 제외)", m._row_is_live("{not json") is False)
    check("None → False", m._row_is_live(None) is False)
    # float32 왕복값도 마커로 잡아야 한다 — 424차 P0-A와 같은 관례(1e-6)
    import struct
    f32 = struct.unpack("f", struct.pack("f", 0.3))[0]
    check("float32 왕복 0.3도 마커로 인식 (424차 P0-A 관례 일치)",
          m._row_is_live({"feature_quality_score": f32}) is False)


# ══════════════════════ 채널 사전등록 · 스모크 ══════════════════════

def test_channels_registered():
    from config.settings import VALIDATION_CAMPAIGN as VC
    for key, need in (
        ("phantom_stop_edge", ("min_samples", "min_days", "alpha", "effective_date")),
        ("grade_x_promotion", ("min_samples_per_bucket", "min_days", "alpha")),
        ("hurst_meanrevert_drag", ("min_samples", "min_paired_days", "alpha")),
    ):
        ch = VC.get(key)
        check("[%s] 사전등록됨" % key, isinstance(ch, dict))
        if isinstance(ch, dict):
            miss = [k for k in need if k not in ch]
            check("[%s] 필수 임계 전부 존재 (%s)" % (key, miss or "없음"), not miss)
    # 313차 — 단일일 판정 금지가 임계에 실제로 박혀 있는가
    check("[35] min_days >= 5", VC["phantom_stop_edge"]["min_days"] >= 5)
    check("[36] min_days >= 5", VC["grade_x_promotion"]["min_days"] >= 5)
    check("[37] min_paired_days >= 5",
          VC["hurst_meanrevert_drag"]["min_paired_days"] >= 5)


def test_verdict_vocabulary():
    m = _load_report_module()
    for v in ("SUPPORTS_HYP", "REJECTS_HYP"):
        check("판정 어휘 %s가 렌더된다" % v, v in m._fmt_verdict(v))
    check("미등록 어휘는 INSUFFICIENT로 폴백",
          "INSUFFICIENT" in m._fmt_verdict("NONSENSE"))


def test_evals_smoke():
    """실 DB로 3채널이 예외 없이 dict를 돌려주는가 (읽기 전용)."""
    m = _load_report_module()
    for name, fn in (("[35]", m.eval_phantom_stop_edge),
                     ("[36]", m.eval_grade_x_promotion),
                     ("[37]", m.eval_hurst_meanrevert_drag)):
        try:
            out = fn()
            ok = isinstance(out, dict) and "verdict" in out
        except Exception as e:
            ok = False
            print("       예외: %r" % (e,))
        check("%s eval이 verdict를 담은 dict를 반환한다" % name, ok)


def test_hurst_channel_matches_manual_analysis():
    """[37]이 0804 수동 분석과 같은 수를 내는가 — 판정식 표류 감지."""
    m = _load_report_module()
    out = m.eval_hurst_meanrevert_drag()
    if out.get("no_data") or not out.get("paired_days"):
        check("[37] 표본 없음 — 대조 생략(비교 불가)", True)
        return
    check("[37] 짝지은 거래일 7일 (0804 실측)", out.get("paired_days") == 7)
    check("[37] 부호검정 p=0.4531 (0804 실측)",
          abs(out.get("sign_p", 0) - 0.4531) < 1e-4)
    check("[37] 미유의 → PASS (누적 -145만원에도 조치 금지)",
          out.get("verdict") == "PASS")
    check("[37] [29]와 모집단 공유 사실이 metrics에 남는다",
          out.get("shares_population_with", "").startswith("[29]"))


if __name__ == "__main__":
    print("=" * 72)
    print("[MW0602 424차 후속] 캠페인 3채널 + 리포트 생성 크래시 회귀 테스트")
    print("=" * 72)
    for fn in (
        test_no_undefined_module_helpers,
        test_no_comma_flag_in_percent_format,
        test_sign_test_p,
        test_paired_day_summary_reproduces_0804,
        test_paired_day_summary_edge,
        test_fmt_krw,
        test_row_is_live,
        test_channels_registered,
        test_verdict_vocabulary,
        test_evals_smoke,
        test_hurst_channel_matches_manual_analysis,
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
