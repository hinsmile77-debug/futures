"""[MW0601 488차] [35] 유령 하드스톱 — "모집단 소멸" 서술이 갈래를 타는지 고정한다.

────────────────────────────────────────────────────────────────────────────
무엇이 고장나 있었나
────────────────────────────────────────────────────────────────────────────
439차(MW0602)가 `MAX_CONTRACTS` 10→3 배포 **직후 2거래일**(08-06 0건 / 08-07 1건)을
근거로 *"`qty>=2` 진입이 사라져 유령 청산 모집단이 소멸했다"* 고 판단하고, 그 문장을
리포트 생성기에 **무조건 렌더되는 프로즈**로 박았다. 같은 세션이 P3에서 이미
*"사라진 게 아니라 급감"* 으로 자체 정정했으나 그 정정은 `structural_block` 분기에만
들어갔다.

MW0601(v9-dev)에서는 그 전제가 처음부터 성립하지 않았다 — 2026-08-21 실측 기준
주판정 표본이 **12건 / 5거래일**이고 전부 `tp1_breakeven_qty2`(qty 2~3) 경로다.
그 결과 리포트 [35] 절 안에서 *"모집단이 소멸했다(0건)"* 바로 아래에
*"유령 청산 12건"* 이 찍히는 **정면 모순**이 매주 생산됐다.

같은 가정이 **세 곳**에 박혀 있었다:
    (a) 리포트 [35] 도입 프로즈          — 무조건 렌더
    (b) 리포트 [35-M] 미러 도입 문장     — "431차 이후 사라졌으므로" 무조건 단정
    (c) `tests/test_439_phantom_mirror.py` — 주판정 0건 전제, **2건 FAIL 방치**

(c)가 특히 나쁘다 — 회귀 테스트가 결함을 잡는 대신 결함과 함께 틀려 있었다.

────────────────────────────────────────────────────────────────────────────
488차가 고정하는 불변식
────────────────────────────────────────────────────────────────────────────
    (1) 주판정 n>0  → "488차 정정"(모집단 생존) 렌더, "소멸했다" **미출현**
    (2) 주판정 n==0 → 기존 439차 문구 그대로 (하위호환 — 다른 갈래는 여전히 참일 수 있다)
    (3) [35-M] 도입 문장도 같은 갈래를 탄다
    (4) drop-max 산술 항등식: sum_drop_max == delta_pt_sum - drop_max_delta
    (5) 부호 역전 플래그가 실제 부호 변화와 일치
    (6) drop-max 는 **합격선이 아니다** — verdict 어휘를 바꾸지 않는다(§9-4)

⚠ 이 테스트는 판정 기준을 만들지 않는다. 사전등록 관문은 일자단위 부호검정 그대로다.
"""

import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["MIREUK_TEST_MODE"] = "1"  # [422차] 프로덕션 로그·Slack 오염 차단

from scripts.generate_validation_campaign_report import (  # noqa: E402
    eval_phantom_stop_edge,
)

FAILURES = []
GEN = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "scripts", "generate_validation_campaign_report.py")


def check(name, cond):
    print("[%s] %s" % ("OK" if cond else "FAIL", name))
    if not cond:
        FAILURES.append(name)


def _render_35(pse):
    """[35] 렌더 구간만 잘라 실행한다 — 실 DB·전체 리포트 없이 분기만 본다.

    앵커가 움직이면 즉시 예외로 드러난다(조용한 통과 금지).
    """
    src = io.open(GEN, encoding="utf-8").read().split("\n")
    try:
        start = next(i for i, l in enumerate(src)
                     if "[35]~[37] MW0602 424차 후속 신설 3채널 상세" in l)
        end = next(i for i, l in enumerate(src)
                   if l.strip() == '_mir = pse.get("mirror") or {}')
    except StopIteration:
        raise AssertionError(
            "렌더 구간 앵커를 못 찾았다 — [35] 절 구조가 바뀌었으면 이 테스트를 "
            "함께 갱신할 것(앵커: '[35]~[37] ... 3채널 상세' / '_mir = pse.get(\"mirror\")')")
    block = "\n".join(l[4:] if l.startswith("    ") else l
                      for l in src[start:end])
    ns = {"L": [], "pse": pse}
    exec(block, ns)
    return "\n".join(ns["L"])


def _render_35m(pse):
    """[35-M] 미러 도입 문장 갈래만 확인한다."""
    src = io.open(GEN, encoding="utf-8").read().split("\n")
    try:
        start = next(i for i, l in enumerate(src)
                     if "488차] 이 도입부도" in l)
        end = next(i for i, l in enumerate(src)
                   if "**같은 \u0394를 `live_suppressed=1`" in l)
    except StopIteration:
        raise AssertionError("[35-M] 도입부 앵커를 못 찾았다 — 구조 변경 시 갱신할 것")
    block = "\n".join(l[8:] if l.startswith("        ") else l
                      for l in src[start:end + 1])
    ns = {"L": [], "pse": pse}
    exec(block, ns)
    return "\n".join(ns["L"])


ALIVE = {"n": 12, "n_days": 5, "realized_pt_sum": 17.293, "cf_pt_sum": 62.99,
         "delta_pt_sum": -45.697, "delta_pt_avg": -3.8081, "favorable_n": 10,
         "n_unresolved": 0, "paired_days": 5, "days_positive": 3,
         "mean_diff": -1.3629, "sign_p": 1.0,
         "by_path": {"tp1_breakeven_qty2": {"n": 12, "delta_pt_sum": -45.697}},
         "drop_max_ts": "2026-08-18 10:40:58", "drop_max_delta": -52.84,
         "delta_pt_sum_drop_max": 7.143, "drop_max_flips_sign": True,
         "mirror": {"n": 20, "n_days": 8}}

DEAD = {"n": 0, "structural_block": True, "structural_reason": "…모집단 소멸…",
        "verdict": "INSUFFICIENT", "mirror": {"n": 20, "n_days": 8}}


def test_alive_branch_hides_extinction_prose():
    """(1) 주판정 표본이 있으면 '소멸' 서술이 나오면 안 된다."""
    md = _render_35(ALIVE)
    check("(1) '488차 정정'(모집단 생존) 출현", "488차 정정" in md)
    check("(1) '소멸했다' 미출현", "소멸했다" not in md)
    check("(1) 실측 건수/거래일 병기", "**12건 / 5거래일** 실측" in md)
    check("(1) '%%' 이스케이프 잔재 없음", "37%%" not in md and "37%" in md)


def test_dead_branch_keeps_439_prose():
    """(2) 주판정 0건 갈래에서는 439차 문구가 그대로 — 하위호환."""
    md = _render_35(DEAD)
    check("(2) 439차 '소멸했다' 유지", "소멸했다" in md)
    check("(2) '488차 정정' 미출현", "488차 정정" not in md)


def test_mirror_intro_follows_same_branch():
    """(3) [35-M] 도입 문장도 갈래를 탄다."""
    alive = _render_35m(ALIVE)
    dead = _render_35m(DEAD)
    check("(3) n>0 → '431차 이후 사라졌으므로' 미출현",
          "431차 이후 사라졌으므로" not in alive)
    check("(3) n>0 → '겹치지 않는 서브표본' 출현",
          "겹치지 않는 서브표본" in alive)
    check("(3) n==0 → 기존 문장 유지", "431차 이후 사라졌으므로" in dead)


def test_drop_max_rendered_with_sign_flip():
    """(4)(5) drop-max 줄과 부호 역전 표시."""
    md = _render_35(ALIVE)
    check("(4) drop-max 줄 출현", "drop-max(최대기여 1건 제거)" in md)
    check("(5) 부호 역전 표시", "부호 역전" in md)
    check("(4) 판정 읽는 법 고정 문단 출현",
          "delta 합`을 단독 인용하지 말 것" in md)


def test_drop_max_arithmetic_on_live_db():
    """(4)(6) 실 DB — 항등식·부호 플래그·verdict 무변경."""
    out = eval_phantom_stop_edge()
    if out.get("error"):
        check("(4) 실 DB 조회 실패 — 스킵: %s" % out["error"], True)
        return
    if not out.get("n"):
        check("(4) 주판정 0건 — drop-max 미산출이 정상",
              out.get("delta_pt_sum_drop_max") is None)
        return
    got = out["delta_pt_sum_drop_max"]
    want = round(out["delta_pt_sum"] - out["drop_max_delta"], 3)
    check("(4) 항등식 sum_drop_max == delta_sum - drop_max_delta (%s == %s)"
          % (got, want), abs(got - want) < 1e-6)
    check("(5) 부호 역전 플래그가 실제 부호 변화와 일치",
          out["drop_max_flips_sign"]
          == ((out["delta_pt_sum"] < 0) != (got < 0)))
    check("(4) drop_max_delta 는 |Δ| 최대 1건이다",
          abs(out["drop_max_delta"]) >= abs(out["delta_pt_sum"]) / max(out["n"], 1))
    check("(6) drop-max 는 합격선이 아니다 — verdict 어휘 무변경",
          out.get("verdict") in ("INSUFFICIENT", "PASS",
                                 "SUPPORTS_HYP", "REJECTS_HYP"))


if __name__ == "__main__":
    print("=" * 72)
    print("[MW0601 488차] [35] 모집단 생존 갈래 + drop-max 회귀 테스트")
    print("=" * 72)
    for fn in (
        test_alive_branch_hides_extinction_prose,
        test_dead_branch_keeps_439_prose,
        test_mirror_intro_follows_same_branch,
        test_drop_max_rendered_with_sign_flip,
        test_drop_max_arithmetic_on_live_db,
    ):
        print("\n-- %s" % fn.__name__)
        fn()
    print("\n" + "=" * 72)
    if FAILURES:
        print("실패 %d건: %s" % (len(FAILURES), FAILURES))
        sys.exit(1)
    print("전부 통과")
