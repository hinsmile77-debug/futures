# -*- coding: utf-8 -*-
"""tests/test_470_verdict_mdd_unit.py — [MW0602 470차 R1] 전략판정 MDD 단위 회귀

────────────────────────────────────────────────────────────────────────────
무엇을 지키는가
────────────────────────────────────────────────────────────────────────────
`전략판정` 배너가 2026-07-31부터 **10거래일 연속** UNDERPERFORM + REPLACE_CANDIDATE
를 발행했고, **손익 부호와 무관**했다(+752,561원인 날도 UNDERPERFORM,
-473,373원인 날은 OUTPERFORM).

뒤집은 것은 Sharpe 가 아니라 **MDD 다리 단독**이었고, 그 두 값은 단위가 달랐다:
  · live  = mdd_krw / **20일 창 누적손익 peak**   (`_compute_live_metrics:601`)
  · WFA   = **자본 대비** MDD (0.142)
08-12 실측 `mdd_pct=1.292`(129%)는 자본 대비로는 **물리적으로 불가능한 값**이다.

⛔ 계산식(`:601`)은 바꾸지 않는다 — 465차 P6-b 가 "WFA 합격선이 이 정의를 쓰므로
   바꾸면 실전 전환 기준 ③이 조용히 이동한다"고 명시했다. **소비 지점만** 고쳤다.

불변식:
  (1) 자본 대비 MDD 는 1.0(=100%)을 넘지 않는다 — 넘으면 단위가 틀린 것이다
  (2) `mdd_krw` 가 없으면 None → INSUFFICIENT (모르는 것을 UNDERPERFORM 으로 단정 금지)
  (3) 자본이 0/미설정이면 None → INSUFFICIENT
  (4) QA seed 기준선이면 INSUFFICIENT (26주 WFA 미수행 상태에서 "기대값 대비" 판정 금지)
  (5) 08-12 실측 재현 — 129% 짜리 peak 기준 값이 판정에 쓰이지 않는다
  (6) 임계 상수는 **무변경** (313차 — 단위 버그 수정이지 기준 완화가 아니다)
"""
from __future__ import print_function

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("MIREUK_TEST_MODE", "1")

from config.strategy_registry import (                                # noqa: E402
    StrategyRegistry, VERDICT_INSUFFICIENT, VERDICT_UNDERPERFORM,
    VERDICT_NORMAL, VERDICT_OUTPERFORM,
)
import config.strategy_registry as SR                                 # noqa: E402

_fails = []


def check(label, cond):
    print("%s %s" % ("[OK]  " if cond else "[FAIL]", label))
    if not cond:
        _fails.append(label)


CAPITAL = 50_000_000.0          # config/settings.py:SIZING_TARGET_CAPITAL_KRW 현행

# 2026-08-12 실측 — peak 기준 mdd_pct 가 1.292(129%)였던 날
LIVE_0812 = {"days": 20, "sharpe": -0.186, "mdd_pct": 1.292,
             "mdd_krw": 1_446_000.0}
# 2026-08-13 실측 — sharpe 는 NORMAL 기준을 통과했는데 mdd 다리가 뒤집었다
LIVE_0813 = {"days": 20, "sharpe": 1.250, "mdd_pct": 0.855,
             "mdd_krw": 957_000.0}

WFA_SEED = {"sharpe": 1.42, "mdd_pct": 0.142,
            "evaluated_at": "2026-05-07 18:37:00"}          # QA seed
WFA_REAL = {"sharpe": 1.42, "mdd_pct": 0.142,
            "evaluated_at": "2026-09-01 10:00:00"}          # 가상의 진짜 WFA


def test_capital_ratio_is_bounded():
    r = StrategyRegistry._live_mdd_vs_capital(LIVE_0812)
    check("(1) 08-12 자본 대비 MDD 가 계산된다", r is not None)
    check("(1) 자본 대비 MDD <= 1.0 (129%% 같은 값이 안 나온다) — 실측 %.4f" % (r or -1),
          r is not None and r <= 1.0)
    check("(1) 값이 mdd_krw/자본 과 일치",
          r is not None and abs(r - LIVE_0812["mdd_krw"] / CAPITAL) < 1e-9)


def test_missing_mdd_krw_returns_none():
    check("(2) mdd_krw 없으면 None",
          StrategyRegistry._live_mdd_vs_capital({"days": 20, "mdd_pct": 1.29}) is None)


def test_zero_capital_returns_none():
    _orig = SR.StrategyRegistry._live_mdd_vs_capital

    # 자본을 못 읽는 상황을 흉내낸다 — settings 를 건드리지 않고 함수만 감싼다.
    def _no_capital(live_snap):
        import config.settings as _s
        _save = getattr(_s, "SIZING_TARGET_CAPITAL_KRW", None)
        try:
            _s.SIZING_TARGET_CAPITAL_KRW = 0
            try:
                import config.runtime_settings as _rs
                _rs_save = getattr(_rs, "SIZING_TARGET_CAPITAL_KRW", None)
                _rs.SIZING_TARGET_CAPITAL_KRW = 0
            except Exception:
                _rs = None
                _rs_save = None
            return _orig(live_snap)
        finally:
            if _save is not None:
                _s.SIZING_TARGET_CAPITAL_KRW = _save
            if _rs is not None and _rs_save is not None:
                _rs.SIZING_TARGET_CAPITAL_KRW = _rs_save

    check("(3) 자본 0 이면 None", _no_capital(LIVE_0812) is None)


def test_seed_baseline_is_insufficient():
    reg = StrategyRegistry.__new__(StrategyRegistry)     # DB 안 열고 메서드만 쓴다
    check("(4) seed 기준선 판별", StrategyRegistry._is_seed_baseline(WFA_SEED) is True)
    check("(4) 진짜 WFA 는 seed 아님", StrategyRegistry._is_seed_baseline(WFA_REAL) is False)
    check("(4) seed 기준선이면 INSUFFICIENT",
          reg._compute_verdict({"WFA": WFA_SEED}, LIVE_0813) == VERDICT_INSUFFICIENT)
    check("(4) evaluated_at 없으면 INSUFFICIENT",
          reg._compute_verdict({"WFA": {"sharpe": 1.42, "mdd_pct": 0.142}}, LIVE_0813)
          == VERDICT_INSUFFICIENT)


def test_0812_0813_no_longer_driven_by_peak_mdd():
    reg = StrategyRegistry.__new__(StrategyRegistry)
    # 진짜 WFA 기준선을 가정했을 때, mdd 다리가 더 이상 129%로 뒤집지 않는지 본다.
    v13 = reg._compute_verdict({"WFA": WFA_REAL}, LIVE_0813)
    check("(5) 08-13 은 더 이상 UNDERPERFORM 이 아니다 (실제 %s)" % v13,
          v13 in (VERDICT_NORMAL, VERDICT_OUTPERFORM))
    v12 = reg._compute_verdict({"WFA": WFA_REAL}, LIVE_0812)
    # 08-12 는 sharpe 자체가 -0.186 이라 UNDERPERFORM 이 맞다 — 그건 진짜 저성과다.
    check("(5) 08-12 는 Sharpe 가 음수라 UNDERPERFORM 유지 (실제 %s)" % v12,
          v12 == VERDICT_UNDERPERFORM)
    check("(5) 즉 판정이 손익/Sharpe 를 따라간다 — 단위 오류가 아니라",
          v13 != v12)


def test_thresholds_unchanged():
    """313차 — 이번 변경은 단위 버그 수정이지 기준 완화가 아니다.

    아래 4개 값이 바뀌면 그것은 **판정 기준 변경**이고, 사전등록 절차를 거쳐야 한다.
    이 테스트가 그 경계를 지킨다.
    """
    check("(6) _OUTPERFORM_SHARPE_DELTA = 0.15 무변경", SR._OUTPERFORM_SHARPE_DELTA == 0.15)
    check("(6) _NORMAL_SHARPE_DELTA = -0.20 무변경", SR._NORMAL_SHARPE_DELTA == -0.20)
    check("(6) _OUTPERFORM_MDD_DELTA = -0.01 무변경", SR._OUTPERFORM_MDD_DELTA == -0.01)
    check("(6) _NORMAL_MDD_DELTA = 0.03 무변경", SR._NORMAL_MDD_DELTA == 0.03)


if __name__ == "__main__":
    print("=" * 72)
    print("[MW0602 470차 R1] 전략판정 MDD 단위 회귀 테스트")
    print("=" * 72)
    for fn in (test_capital_ratio_is_bounded,
               test_missing_mdd_krw_returns_none,
               test_zero_capital_returns_none,
               test_seed_baseline_is_insufficient,
               test_0812_0813_no_longer_driven_by_peak_mdd,
               test_thresholds_unchanged):
        print("\n-- %s" % fn.__name__)
        fn()
    print("\n" + "=" * 72)
    if _fails:
        print("실패 %d건:" % len(_fails))
        for f in _fails:
            print("  - %s" % f)
        sys.exit(1)
    print("470차 R1 전략판정 MDD 단위 회귀 테스트 전부 통과")
