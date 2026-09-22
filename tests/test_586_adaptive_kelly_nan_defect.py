# -*- coding: utf-8 -*-
"""[MW0602 586차 후속] 본전(0.00pt) 청산 1건이 사이징 계산 전체를 NaN 으로 만든다.

2026-09-22 에 무슨 일이 있었나
------------------------------
10:27:41 에 TP1 보호스톱이 **정확히 진입가**(1127.54)에서 걸려 `pnl_pts=0.0` 인
레그가 하나 생겼다. 그 뒤 13:30:01~14:46:01 사이 **16회**, 매분 파이프라인이
`ValueError: cannot convert float NaN to integer` 로 죽었고, 그때마다
`자동진입 OFF + 15분 쿨다운` 이 함께 걸려 **약 68분간 신규 진입이 잠겼다**.

    AdaptiveKelly.record(win=False, pnl_pts=0.0)
        -> {"win": False, "profit": 0.0, "loss": 0.0}      # loss 가 0 이다
    compute_fraction()
        avg_loss = mean([0.0]) = 0.0                        # `if losses else` 가드를 통과한다
        b        = avg_profit / 0.0   = inf                 # numpy 는 예외를 내지 않는다
        kelly_f  = (p*(b+1)-1) / inf  = inf/inf = nan
        if kelly_f <= 0:  ...                               # nan <= 0 은 False -> 방어 못 함
        multiplier = nan
    PositionSizer.compute(adaptive_kelly_mult=nan)
        int(nan)  ->  ValueError

🔴 리포트 §1-5 의 하위 주장 한 줄을 정정한다 — 재인용 금지
-------------------------------------------------------
0922 리포트는 촉발 경로를 *"승/패 판정은 KRW 부호, 크기는 pt 기준 — 여기서
판정 기준과 크기 기준이 어긋난다"* 로 적었다. **그렇지 않다.** `main.py` 의
`kelly.record()` 호출부 4곳은 **전부 `if pnl > 0:` (pnl = pnl_pts) 으로 분기**하며
KRW 는 보지 않는다(`test_2` 가 이 사실을 고정한다).

차이가 중요한 이유는 **결함 표면의 크기**다. KRW 기준이라면 "pt 는 벌었는데
수수료로 마이너스" 인 레그까지 손실=0 패배가 되어 표면이 넓어진다(실측 6건).
실제로는 pt 기준이므로 `win=False` <=> `pnl_pts <= 0` 이고, `loss == 0.0` 은
**`pnl_pts` 가 정확히 0.0 일 때뿐**이다 — `trades.db` 전수 502레그 중 4건
(2026-07-22 · 08-31 · 09-11 · 09-22). 드물지만 재발성이고, 그 4건 전부
`하드스톱(틱)` 이다. KRW 쪽을 고치러 가면 헛다리를 짚는다.

이 파일이 하는 일 — 그리고 하지 않는 일
--------------------------------------
**프로덕션 코드를 고치지 않는다.** F-586-1(1차·2차 방어)은 `strategy/entry/`
= 수량 확정 경로라 장후 자동조치의 C등급(사용자 검토 필수)이다. 이 파일은
그 전에 **결함을 재현 가능한 형태로 못 박아** 두는 계측 전용 가드다.

    test_1  씨앗   : 본전 레그가 "손실 0 인 패배" 로 기록된다
    test_2  경로   : 승/패 분기는 pnl_pts 기준이다 (KRW 아님)
    test_3  결함   : compute_fraction() 이 nan 을 낸다            [xfail]
    test_4  전파   : 그 nan 이 PositionSizer 에서 크래시로 터진다  [xfail]
    test_5  대조군 : 정상 표본은 지금도 유한하다 (수정 후에도 유지되어야 한다)

🔴 **test_3 · test_4 가 XPASS 로 뜨면 그것은 실패가 아니라 신호다** —
F-586-1 이 적용됐다는 뜻이다. 그때 `@pytest.mark.xfail` 마커를 지워 평범한
정상 검증으로 바꿔라. 마커를 지우기 전까지 이 파일은 스위트를 붉게 만들지
않는다(비-strict xfail).

실행:
    python -m pytest tests/test_586_adaptive_kelly_nan_defect.py
"""
import io
import math
import os
import re
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from strategy.entry.adaptive_kelly import AdaptiveKelly          # noqa: E402
from strategy.entry.position_sizer import PositionSizer          # noqa: E402


# 2026-09-22 의 최근 성적 창을 그대로 재현한다. 임계(n>=5)를 넘겨야 실제 켈리
# 분기로 들어가므로 승 4 + "본전 패배" 1 = 5건이 최소 재현 표본이다.
_TODAY_SHAPE = [(True, 0.58), (True, 0.76), (True, 0.88), (True, 1.34), (False, 0.0)]


def _kelly_from(records):
    k = AdaptiveKelly()
    for win, pts in records:
        k.record(win=win, pnl_pts=pts)
    return k


def test_1_breakeven_leg_is_recorded_as_zero_loss_defeat():
    """씨앗 — 본전 레그는 '손실 크기가 0 인 패배' 로 들어간다.

    여기가 결함의 입구다. `record()` 는 win 플래그와 loss 크기를 **따로**
    만드는데(`abs(min(pnl_pts, 0))`), pnl_pts 가 정확히 0 이면 패배로 분류되면서
    크기는 0 이 된다. 이 불변식은 F-586-1(compute_fraction 쪽 수정) 뒤에도
    그대로여야 한다 — 고치는 지점은 여기가 아니다.
    """
    k = _kelly_from([(False, 0.0)])
    rec = k.trade_results[-1]
    assert rec["win"] is False
    assert rec["loss"] == 0.0, "본전 레그의 loss 가 0 이 아니면 이 결함의 전제가 바뀐 것이다"
    assert rec["profit"] == 0.0

    # 대조 — 진짜 손실은 크기를 갖는다
    k2 = _kelly_from([(False, -1.25)])
    assert k2.trade_results[-1]["loss"] == 1.25


def test_2_record_call_sites_branch_on_pnl_pts_not_krw():
    """경로 — main.py 의 승/패 분기는 pnl_pts 기준이다. KRW 가 아니다.

    0922 리포트의 'KRW 부호 기준' 서술을 반증한 지점이며, 결함 표면이
    `pnl_pts == 0.0` 으로 좁다는 근거다. 누가 이 기준을 KRW 로 바꾸면 표면이
    넓어지므로(수수료로 마이너스인 레그까지 손실 0 패배가 된다) 이 테스트가
    깨져서 위 docstring 의 갱신을 강제한다.
    """
    path = os.path.join(_ROOT, "main.py")
    with io.open(path, "r", encoding="utf-8") as fp:
        lines = fp.read().splitlines()

    hits = [i for i, ln in enumerate(lines) if "self.kelly.record(win=False" in ln]
    assert hits, "main.py 에서 kelly.record(win=False ...) 호출부를 찾지 못했다"

    for i in hits:
        # 바로 위 8줄 안에 `pnl > 0` 비교가 있어야 한다(else 가지에 놓인다).
        # 호출부 4곳 중 3곳은 `if pnl > 0:` 이고, `_post_exit` 한 곳만
        # `was_correct = pnl > 0` 으로 한 번 이름을 거친다 — 둘 다 같은 기준이다.
        window = "\n".join(lines[max(0, i - 8):i])
        assert re.search(r"\bpnl\s*>\s*0\b", window), (
            "%s:%d — 승/패 분기가 `pnl > 0` (pnl_pts) 기준이 아니다. "
            "기준이 바뀌었다면 test_586 docstring 의 '결함 표면' 설명을 갱신할 것."
            % (path, i + 1))
        assert not re.search(r"\bpnl_krw\b", window), (
            "%s:%d — 승/패 분기 근처에 pnl_krw 가 등장한다. 기준이 KRW 로 바뀌면 "
            "결함 표면이 넓어지므로(수수료로 마이너스인 레그 포함) docstring 을 갱신할 것."
            % (path, i + 1))

    # pnl 이 pnl_pts 에서 온다는 것도 함께 고정한다.
    assert any('pnl = result["pnl_pts"]' in ln for ln in lines), (
        'main.py 의 pnl 이 result["pnl_pts"] 에서 오지 않는다 — 위 분기의 단위 전제가 깨졌다')


@pytest.mark.xfail(
    reason="F-586-1 미적용 — 손실=0 표본만 있으면 b=inf -> kelly_f=nan. "
           "XPASS 로 뜨면 수정이 적용된 것이니 이 마커를 지울 것.",
    strict=False,
)
def test_3_zero_loss_sample_must_not_yield_nan_multiplier():
    """결함 — 배수는 언제나 [MIN_MULT, MAX_MULT] 안의 유한값이어야 한다."""
    result = _kelly_from(_TODAY_SHAPE).compute_fraction()
    mult = float(result["multiplier"])
    assert math.isfinite(mult), "multiplier=%r (nan/inf)" % (mult,)
    assert AdaptiveKelly.MIN_MULT <= mult <= AdaptiveKelly.MAX_MULT


@pytest.mark.xfail(
    reason="F-586-1 2차 방어 미적용 — int(nan) 이 ValueError 로 터진다. "
           "XPASS 로 뜨면 수정이 적용된 것이니 이 마커를 지울 것.",
    strict=False,
)
def test_4_nan_kelly_mult_must_not_crash_position_sizer():
    """전파 — nan 배수가 들어와도 크래시 대신 안전한 수량으로 폴백해야 한다.

    이것이 13:30~14:46 의 16회 `ValueError: cannot convert float NaN to integer`
    가 터진 바로 그 지점이다(`position_sizer.py` 의 `int(raw_qty)`).
    """
    sizer = PositionSizer(account_balance=50_000_000.0)
    out = sizer.compute(confidence=0.45, atr=3.0, adaptive_kelly_mult=float("nan"))
    assert isinstance(out["quantity"], int)
    assert out["quantity"] >= 1


def test_5_normal_samples_stay_finite_control():
    """대조군 — 손실에 크기가 있는 정상 표본은 지금도 유한하다.

    비공허성 확인이자 회귀 가드다. F-586-1 이 '손실=0' 을 특수 처리하면서
    정상 경로까지 바꿔 버리면 여기서 걸린다.
    """
    cases = {
        "정상 혼합(승3 패2)": [(True, 1.0)] * 3 + [(False, -0.5)] * 2,
        "전패":              [(False, -0.8)] * 6,
        "표본 부족(n<5)":     [(True, 1.0)] * 4,
    }
    for label, records in cases.items():
        mult = float(_kelly_from(records).compute_fraction()["multiplier"])
        assert math.isfinite(mult), "%s -> multiplier=%r" % (label, mult)
        assert AdaptiveKelly.MIN_MULT <= mult <= AdaptiveKelly.MAX_MULT, (
            "%s -> multiplier=%r 가 [%s, %s] 밖이다"
            % (label, mult, AdaptiveKelly.MIN_MULT, AdaptiveKelly.MAX_MULT))
