# -*- coding: utf-8 -*-
"""tests/test_475_conffloor_sample_and_verdict_source.py
    — [MW0602 475차 후속] 죽은 계측 2종 회귀

────────────────────────────────────────────────────────────────────────────
무엇을 지키는가
────────────────────────────────────────────────────────────────────────────
같은 실패가 **두 곳에서 동시에** 확인됐다 — "무조건 상태 샘플"이라 주장하는 계측이
실제로는 한쪽 값만 찍고 있었다.

(A) `[ConfFloorGuard] state=` — 2026-08-18 실측 **80건 전부 `ZONE_BLACKOUT`**,
    진입 허용 290분 **0건**. 원인은 emit 위치가 아니라 **calibrator 오참조**다.
    470차 L2 가 `self.calibrator`(= main.py:464 가 주입하는 MultiHorizonCalibrator)를
    봤는데, 그 클래스는 `is_fitted` 가 property 가 아니라 **method**(horizon 인자
    필요)라 `not _cal.is_fitted` 가 항상 False 이고, `output_max` 는 **아예 없다.**
    → 매분 `AttributeError` → `logger.debug` 로 삼켜짐 → 로그 0건.
    (py37_32 런타임 실측: `AttributeError 'MultiHorizonCalibrator' object has no
     attribute 'output_max'`)

(B) 수집기 §12 `전략판정` — 원천이 `_WARN`/`_SYSTEM` 로그 배너였는데, 그 배너는
    main.py 가 `if _action in (ROLLBACK_REVIEW, REPLACE_CANDIDATE)` 일 때만 찍는
    **조건부 로그**다. 표본이 UNDERPERFORM 으로 100% 고착되는 것이 구조적으로 보장된다
    (수집기 자신의 §12 머리말이 금지한 패턴). 2026-08-18 실측: 로그 원천은
    `UNDERPERFORM×7` 🔴 고착, 같은 날 실제 판정은 `INSUFFICIENT`.

불변식:
  (1) 진입 허용 존에서 상태 샘플이 **찍힌다** (0건이면 계측이 죽은 것)
  (2) `self.calibrator` 가 무엇이든 ConfFloorGuard 는 `ensemble_calibrator` 를 본다
  (3) 상태 샘플 예외는 `logger.debug` 로 삼키지 않는다 (승격 유지)
  (4) §12 `전략판정` 원천은 **무조건 생성되는** 일일 리포트 파일이다
  (5) INSUFFICIENT 사유가 "데이터 부족"으로 뭉뚱그려지지 않는다 (470차 R1 이후 실제
      다수 원인은 일수 부족이 아니라 seed 기준선)
"""
from __future__ import print_function

import io as _io
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("MIREUK_TEST_MODE", "1")

_fails = []


def check(label, cond):
    print("%s %s" % ("[OK]  " if cond else "[FAIL]", label))
    if not cond:
        _fails.append(label)


def _read(rel):
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), rel)
    return _io.open(p, encoding="utf-8").read()


class _Capture(logging.Handler):
    """로그 문자열만 모으는 최소 핸들러 (pytest 미의존 — 이 repo 테스트는 단독 실행)."""

    def __init__(self):
        logging.Handler.__init__(self)
        self.lines = []

    def emit(self, record):
        try:
            self.lines.append(record.getMessage())
        except Exception:
            self.lines.append(str(record.msg))


# ══════════════════════════════════════════════════════════════════
# (A) ConfFloorGuard 상태 샘플
# ══════════════════════════════════════════════════════════════════
def test_conf_floor_sample_emits_in_entry_zone():
    from model.ensemble_decision import EnsembleDecision
    import model.ensemble_decision as _ed

    ed = EnsembleDecision()
    # 470차 L2 가 잘못 참조하던 객체를 그대로 재현한다 —
    # 이 자리에 무엇이 들어와도 상태 샘플은 살아 있어야 한다.
    ed.calibrator = object()

    cap = _Capture()
    _prev_level = _ed.logger.level
    _ed.logger.addHandler(cap)
    _ed.logger.setLevel(logging.INFO)   # 상태 샘플은 INFO — 루트 기본(WARNING)이면 삼켜진다
    try:
        ed._conf_floor_sample_minute = None
        ed._sample_conf_floor_state(0.384, True)          # 진입 허용 존 · 미fit
        n_allowed = len([l for l in cap.lines if "state=" in l])

        ed._conf_floor_sample_minute = None
        ed.ensemble_calibrator._fitted = True
        ed.ensemble_calibrator._last_out_max = 0.3835     # 하한 미달 재현(0818 09:22)
        ed._sample_conf_floor_state(0.384, True)

        ed._conf_floor_sample_minute = None
        ed._sample_conf_floor_state(1.01, False)          # 진입 금지 존
    finally:
        _ed.logger.removeHandler(cap)
        _ed.logger.setLevel(_prev_level)

    states = [l.split("state=")[1].split(" ")[0]
              for l in cap.lines if "state=" in l]
    check("(1) 진입 허용 존에서 상태 샘플이 찍힌다 (0818 결함: 0건)", n_allowed >= 1)
    check("(1) 세 호출 모두 샘플을 남긴다", len(states) == 3)
    check("(1) 값이 한 값에 고착하지 않는다 — %s" % ",".join(states),
          len(set(states)) >= 2)
    check("(1) 허용 존 미fit = RAW", states[0] == "RAW")
    check("(1) 출력상한 < 필요 = BLOCKED", states[1] == "BLOCKED")
    check("(1) 금지 존 = ZONE_BLACKOUT", states[2] == "ZONE_BLACKOUT")


def test_conf_floor_calibrator_is_single_source():
    from model.ensemble_decision import EnsembleDecision
    ed = EnsembleDecision()
    _sentinel = object()
    ed.calibrator = _sentinel
    check("(2) ConfFloorGuard 는 ensemble_calibrator 를 본다",
          ed._resolve_conf_calibrator() is ed.ensemble_calibrator)
    check("(2) self.calibrator(MultiHorizon) 를 보지 않는다",
          ed._resolve_conf_calibrator() is not _sentinel)

    src = _read("model/ensemble_decision.py")
    check("(2) 두 경로가 같은 접근자를 쓴다 (참조 분기 재발 차단)",
          src.count("self._resolve_conf_calibrator()") >= 2)
    check("(3) 상태 샘플 예외를 debug 로 삼키지 않는다",
          "[ConfFloorGuard] 상태 샘플 실패 (무해)" not in src)
    check("(3) 예외 타입을 함께 남긴다",
          "type(_cfs_e).__name__" in src)


# ══════════════════════════════════════════════════════════════════
# (B) 수집기 §12 `전략판정` 원천 + INSUFFICIENT 사유
# ══════════════════════════════════════════════════════════════════
def test_stuck_indicator_source_is_unconditional():
    sys.path.insert(0, os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        ".claude", "skills", "mireuk-daily-check", "scripts"))
    import collect_evidence as ce

    spec = ce.DEFAULT_CONFIG["stuck_indicators"]["patterns"]["전략판정"]
    files = [f.lower() for f in spec["files"]]
    check("(4) 원천이 일일 전략 리포트 파일이다", "strategy_report" in files)
    check("(4) 조건부 로그(_WARN/_SYSTEM)를 원천으로 쓰지 않는다",
          not any(f in ("_warn", "_system") for f in files))

    # 배너가 조건부라는 사실 자체를 고정한다 — main.py 가 무조건 로그로 바뀌면
    # 이 테스트가 깨지고, 그때 원천을 되돌릴지 다시 판단하면 된다.
    main_src = _read("main.py")
    check("(4) 로그 배너는 여전히 조건부다 (원천 교체 근거 유지)",
          "if _action in (ACTION_ROLLBACK_REVIEW, ACTION_REPLACE_CANDIDATE):" in main_src)


def test_insufficient_reason_is_specific():
    from config.strategy_registry import StrategyRegistry, VERDICT_INSUFFICIENT
    from strategy.ops.verdict_engine import compute_action

    reg = StrategyRegistry.__new__(StrategyRegistry)      # DB 접근 없이 순수 판정만
    live = {"days": 20, "sharpe": -0.2, "mdd_krw": 1445833.0}
    why = {}
    v = reg._compute_verdict({"WFA": {"sharpe": 1.42, "mdd_pct": 0.142}}, live, why)
    check("(5) seed 기준선이면 INSUFFICIENT", v == VERDICT_INSUFFICIENT)
    check("(5) 사유에 기준선 문제가 드러난다 — %s" % why.get("reason"),
          "seed" in (why.get("reason") or ""))

    _, reason = compute_action(v, 0, 60, 0, insufficient_reason=why.get("reason"))
    check("(5) 배너 사유가 '데이터 부족 (60일)' 로 뭉뚱그려지지 않는다",
          "데이터 부족" not in reason and "seed" in reason)

    _, legacy = compute_action(v, 0, 60, 0)
    check("(5) 사유를 안 넘기면 종전 문구 유지 (하위호환)",
          "데이터 부족 (60일)" in legacy)

    why2 = {}
    reg._compute_verdict({"WFA": {"sharpe": 1.42, "mdd_pct": 0.142}},
                         {"days": 2}, why2)
    check("(5) 진짜 일수 부족은 일수 부족이라고 말한다 — %s" % why2.get("reason"),
          "5일 미달" in (why2.get("reason") or ""))


if __name__ == "__main__":
    for fn in sorted(
        [v for k, v in list(globals().items()) if k.startswith("test_")],
        key=lambda f: f.__code__.co_firstlineno,
    ):
        print("\n── %s" % fn.__name__)
        fn()
    print("\n" + "=" * 60)
    if _fails:
        print("475차 후속 회귀 테스트 실패 %d건" % len(_fails))
        for f in _fails:
            print("  - %s" % f)
        sys.exit(1)
    print("475차 후속 회귀 테스트 전부 통과")
