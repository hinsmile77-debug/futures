"""[MW0602 464차 P5] BiasReset→ConstOut 오탐 차단 + EOD 가드 유령 기준 계측 회귀 테스트.

지키려는 불변식:
  P5-a  BiasReset(uniform fallback) 중인 호라이즌의 출력은 ConstOut 버퍼에 쌓이지
        않는다 — 의도된 상수값은 모델 고장이 아니다. 그러나 BiasReset이 아닌
        **진짜** 상수출력은 종전대로 감지된다(감지기 자체는 살아 있어야 한다).
        킬스위치 OFF 시 종전 동작(오탐 포함) 복원.
  P5-b  EOD 가드 HOLD 판정은 **무변경**(457차 유보·[22] guard_shadow 관할).
        추가된 것은 "유령 기준 HOLD" 경고 로그뿐이다.

실행: python tests/test_464_constout_biasreset.py   (COM/브로커/DB 불필요)
"""
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["MIREUK_TEST_MODE"] = "1"  # [422차] 프로덕션 로그·Slack 오염 차단

try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass

import config.settings as S
from config.settings import HORIZONS
from model.ensemble_decision import EnsembleDecision

FAILURES = []
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def check(name, cond):
    print("[%s] %s" % ("OK" if cond else "FAIL", name))
    if not cond:
        FAILURES.append(name)


def _proba(up, down, flat):
    d = 1 if up >= down and up >= flat else (-1 if down >= up and down >= flat else 0)
    return {"up": up, "down": down, "flat": flat,
            "direction": d, "confidence": max(up, down, flat)}


def _mixed_proba(const_h="3m", n_min=0.42):
    """3m만 상수(균등), 나머지는 매분 달라지는 정상 출력."""
    import random
    rnd = random.Random(n_min * 1000)
    data = {}
    for h in HORIZONS.keys():
        if h == const_h:
            data[h] = _proba(0.3334, 0.3334, 0.3333)
        else:
            u = 0.40 + rnd.random() * 0.2
            data[h] = _proba(u, (1 - u) * 0.6, (1 - u) * 0.4)
    return data


def _run_n(decision, n, const_h="3m", bias_set=None):
    """n분 연속 compute — 마지막 결과의 const_output_horizons 반환."""
    res = None
    for i in range(n):
        res = decision.compute(
            _mixed_proba(const_h, 0.40 + i * 0.01),
            regime="NEUTRAL", adaptive_gating=False,
            bias_override_horizons=bias_set,
        )
    return res


# ══════════════════════════════════════════════════════════════
# P5-a — 오탐 차단
# ══════════════════════════════════════════════════════════════
def test_biasreset_horizon_not_flagged():
    """BiasReset 중인 3m의 균등 출력은 ConstOut으로 잡히면 안 된다."""
    S.CONST_OUT_EXCLUDE_BIAS_RESET = True
    d = EnsembleDecision()
    res = _run_n(d, 7, const_h="3m", bias_set={"3m"})
    check("BiasReset 중 3m은 const_output_horizons에 없음",
          "3m" not in (res.get("const_output_horizons") or []))
    check("BiasReset 중 3m 버퍼가 비어 있음 (해제 후 오염 방지)",
          len(d._hz_conf_hist["3m"]) == 0)


def test_genuine_constout_still_detected():
    """BiasReset이 아닌 진짜 상수출력은 종전대로 감지돼야 한다 — 감지기 생존 확인."""
    S.CONST_OUT_EXCLUDE_BIAS_RESET = True
    d = EnsembleDecision()
    res = _run_n(d, 7, const_h="3m", bias_set=None)   # override 없음 = 진짜 고착
    check("override 없는 3m 상수출력은 여전히 감지",
          "3m" in (res.get("const_output_horizons") or []))


def test_killswitch_restores_old_behavior():
    """킬스위치 OFF → 종전 동작(BiasReset 중에도 감지 = 오탐 포함) 복원."""
    S.CONST_OUT_EXCLUDE_BIAS_RESET = False
    try:
        d = EnsembleDecision()
        res = _run_n(d, 7, const_h="3m", bias_set={"3m"})
        check("킬스위치 OFF면 BiasReset 중에도 감지 (종전 동작)",
              "3m" in (res.get("const_output_horizons") or []))
    finally:
        S.CONST_OUT_EXCLUDE_BIAS_RESET = True
    check("킬스위치 기본값 True", S.CONST_OUT_EXCLUDE_BIAS_RESET is True)


def test_release_after_override_needs_fresh_window():
    """override 해제 직후엔 새 관찰 창이 다시 5분 차야 감지 — 잔존값 혼합 오탐 방지."""
    S.CONST_OUT_EXCLUDE_BIAS_RESET = True
    d = EnsembleDecision()
    _run_n(d, 6, const_h="3m", bias_set={"3m"})       # override 기간 — 버퍼 빈 상태 유지
    res = _run_n(d, 3, const_h="3m", bias_set=None)   # 해제 — 3분만 지남 (5분 미달)
    check("해제 후 5분 미달이면 아직 미감지",
          "3m" not in (res.get("const_output_horizons") or []))
    res = _run_n(d, 3, const_h="3m", bias_set=None)   # 누적 6분
    check("해제 후 5분 충족되면 (진짜 고착이므로) 감지",
          "3m" in (res.get("const_output_horizons") or []))


def test_other_horizons_unaffected():
    """3m이 BiasReset이어도 다른 호라이즌의 진짜 상수출력 감지는 독립적으로 동작."""
    S.CONST_OUT_EXCLUDE_BIAS_RESET = True
    d = EnsembleDecision()
    # 5m을 상수로, 3m을 override로
    import random
    res = None
    for i in range(7):
        data = {}
        for h in HORIZONS.keys():
            if h == "5m":
                data[h] = _proba(0.3334, 0.3334, 0.3333)
            elif h == "3m":
                data[h] = _proba(0.3334, 0.3334, 0.3333)
            else:
                rnd = random.Random(i * 7 + hash(h) % 100)
                u = 0.40 + rnd.random() * 0.2
                data[h] = _proba(u, (1 - u) * 0.6, (1 - u) * 0.4)
        res = d.compute(data, regime="NEUTRAL", adaptive_gating=False,
                        bias_override_horizons={"3m"})
    flagged = res.get("const_output_horizons") or []
    check("5m(진짜 상수)은 감지", "5m" in flagged)
    check("3m(BiasReset)은 미감지", "3m" not in flagged)


# ══════════════════════════════════════════════════════════════
# P5-b — 유령 기준 계측 (판정 무변경)
# ══════════════════════════════════════════════════════════════
def _read(rel):
    with io.open(os.path.join(BASE, rel), encoding="utf-8") as f:
        return f.read()


def test_guard_verdict_unchanged():
    """가드 판정 함수·호출부는 종전 그대로 — 457차 유보 존중."""
    br = _read("learning/batch_retrainer.py")
    check("evaluate_model_replace 호출부 무변경",
          "evaluate_model_replace(\n                horizon_key, cv_acc, old_acc," in br)
    eg = _read("learning/eod_model_guard.py")
    check("가드 판정식 무변경 (콜드스타트 분기 보존)",
          '"콜드스타트(구모델 없음) — 비교 없이 교체"' in eg)
    check("유보 근거([22] 채널 관할) 주석 명시", "guard_shadow" in br and "457차" in br)


def test_ghost_hold_warning_wired():
    """HOLD 경로에서만, 메타 source=intraday/force일 때만 경고."""
    br = _read("learning/batch_retrainer.py")
    check("유령 기준 경고 로그 존재", "유령 기준 HOLD" in br)
    # HOLD 분기(guard_rejected) 안에 있어야 한다
    hold_block = br.split("guard_rejected = True")[1].split("save_guard_shadow")[0]
    check("경고가 HOLD 분기 내부에 위치", "유령 기준 HOLD" in hold_block)
    check("메타 source 조건부 (intraday/force)",
          '_inc_meta.get("source") in ("intraday", "force")' in hold_block)
    check("예외 격리 (경고 실패가 학습을 깨지 않음)",
          "유령 기준 계측 실패 (무해)" in br)


def test_settings_flag():
    check("CONST_OUT_EXCLUDE_BIAS_RESET 등록 + 기본 True",
          getattr(S, "CONST_OUT_EXCLUDE_BIAS_RESET", None) is True)


if __name__ == "__main__":
    for fn in sorted(
        [v for k, v in list(globals().items()) if k.startswith("test_")],
        key=lambda f: f.__code__.co_firstlineno,
    ):
        print("\n── %s" % fn.__name__)
        fn()
    print("\n" + "=" * 60)
    if FAILURES:
        print("실패 %d건:" % len(FAILURES))
        for f in FAILURES:
            print("  - %s" % f)
        sys.exit(1)
    print("464차 회귀 테스트 전부 통과")
