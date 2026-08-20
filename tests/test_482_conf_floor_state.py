# -*- coding: utf-8 -*-
"""[MW0601 482차 / G-3] ConfFloorGuard 도달가능성 3상태 — 가짜 시계열 방지.

## 왜 3상태인가

0820 리포트 3절 G-3은 "진입후보 분 집계에서 `ConfFloorGuard` 발동 구간을 분리
카운트하라"고 제안했다. 그런데 **그 위에 바로 카운터를 얹으면 안 된다.**

`_conf_floor_reachable` 은 상태 전이 시에만 로그를 남기는 래치인데, 세 개의 early
return 경로에서 **상태를 갱신하지 않고** 빠져나간다:

    zone_allows_entry=False   진입 금지 시간대(설계된 블랙아웃)
    not _cal.is_fitted        보정기 미fit — 403차 축퇴 가드 이후 상시
    _out_max is None          출력범위 미확정

그래서 한 번 False 로 떨어진 뒤 보정기가 미fit 이 되면 복구 로그 없이 False 로
**고착**한다. 2026-08-20 실측이 정확히 그 모습이다:

    09:06:00  "자동진입 하한 도달 불가" WARNING 1건
    (복구 로그 0건)
    10:55~13:57  conf 0.368~0.397 (> min_conf 0.366~0.370) 로 정상 진입 4건

즉 그날은 도달불가가 지속된 것이 아니라 **판정을 멈춘 것**이다. 이 래치 위에
"도달불가 분"을 세면 CLAUDE.md 계측 4원칙 ④의 `_verified_today` 가짜 평선
(대시보드 추이가 8일치 가짜 평선이던 사고)과 똑같은 시계열이 만들어진다.

따라서 카운트 이전에 "재지 않음"을 1급 상태로 만든다.
"""
import io
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

_SRC = os.path.join(_ROOT, "model", "ensemble_decision.py")


class _Cal(object):
    """보정기 스텁 — is_fitted / output_max / output_span 만 본다."""

    def __init__(self, fitted=True, out_max=0.40, span=0.05):
        self.is_fitted = fitted
        self.output_max = out_max
        self.output_span = span


def _guard(fitted=True, out_max=0.40):
    """`_check_conf_floor_consistency` 만 떼어 쓰기 위한 최소 인스턴스."""
    from model.ensemble_decision import EnsembleDecision
    obj = EnsembleDecision.__new__(EnsembleDecision)
    obj._conf_floor_reachable = None
    obj.conf_floor_state = "unmeasured:init"
    obj.ensemble_calibrator = _Cal(fitted=fitted, out_max=out_max)
    return obj


def test_initial_state_is_unmeasured_not_reachable():
    g = _guard()
    assert g.conf_floor_state.startswith("unmeasured:"), \
        "초기값이 reachable/unreachable 이면 '재지 않음'이 사라진다"


def test_reachable_and_unreachable_are_distinguished():
    from config.settings import ENS_CONF_FLOOR_FOR_AUTO
    need = max(float(ENS_CONF_FLOOR_FOR_AUTO), 0.37)

    g = _guard(out_max=need + 0.05)
    g._check_conf_floor_consistency(0.37, zone_allows_entry=True)
    assert g.conf_floor_state == "reachable"

    g2 = _guard(out_max=need - 0.05)
    g2._check_conf_floor_consistency(0.37, zone_allows_entry=True)
    assert g2.conf_floor_state == "unreachable"


def test_zone_blackout_is_unmeasured_not_unreachable():
    """설계된 진입 블랙아웃은 결함이 아니다 — 도달불가로 세면 안 된다."""
    g = _guard()
    g._check_conf_floor_consistency(0.65, zone_allows_entry=False)
    assert g.conf_floor_state == "unmeasured:zone_blackout"


def test_unfitted_calibrator_does_not_latch_stale_verdict():
    """이 테스트가 0820 고착 사고 그 자체다.

    도달불가로 떨어진 뒤 보정기가 미fit 이 되면, 종전 코드는 상태를 그대로 두고
    빠져나가 래치가 False 로 굳었다. 3상태에서는 "재지 않음"으로 바뀌어야 한다.
    """
    from config.settings import ENS_CONF_FLOOR_FOR_AUTO
    need = max(float(ENS_CONF_FLOOR_FOR_AUTO), 0.379)

    g = _guard(out_max=need - 0.03)
    g._check_conf_floor_consistency(0.379, zone_allows_entry=True)
    assert g.conf_floor_state == "unreachable"

    # 보정기가 꺼진다(403차 축퇴 가드) — 이후 매분 이 경로를 탄다
    g.ensemble_calibrator.is_fitted = False
    g._check_conf_floor_consistency(0.370, zone_allows_entry=True)
    assert g.conf_floor_state == "unmeasured:calibrator_unfitted", \
        "미fit 구간이 직전 '도달불가'로 고착하면 가짜 시계열이 만들어진다"

    # 래치 자체는 유지된다(로그 억제 목적) — 3상태와 역할이 다르다
    assert g._conf_floor_reachable is False


def test_missing_output_max_is_unmeasured():
    g = _guard(out_max=None)
    g._check_conf_floor_consistency(0.37, zone_allows_entry=True)
    assert g.conf_floor_state == "unmeasured:no_output_max"


def test_every_return_path_sets_a_state():
    """early return 이 하나라도 상태를 안 정하면 그 분은 직전 값으로 오염된다."""
    src = io.open(_SRC, encoding="utf-8").read()
    i = src.find("def _check_conf_floor_consistency")
    j = src.find("\n    def ", i + 10)
    body = src[i:j]
    n_return = body.count("return")
    n_set = body.count("self.conf_floor_state = ")
    assert n_set >= n_return, (
        "return %d개 vs 상태 설정 %d개 — 상태를 안 정하고 빠지는 경로가 있다"
        % (n_return, n_set))


def test_main_counts_three_buckets_with_shared_denominator():
    """3상태 카운터가 모델 건강도와 같은 자리(같은 분모)에서 세어져야 한다."""
    src = io.open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()
    for attr in ("_mh_cfg_reachable_min", "_mh_cfg_unreachable_min",
                 "_mh_cfg_unmeasured_min"):
        assert ("self.%s: int = 0" % attr) in src, "%s 명시 초기화 없음" % attr
        assert ("self.%s += 1" % attr) in src, "%s 를 세지 않는다" % attr
        assert ("self.%s = 0" % attr) in src, "%s 일일 리셋 없음" % attr
    # 분모 공유 — CB③ ready 카운트 바로 옆이어야 한다
    i_cb3 = src.find("self._mh_cb3_ready_minutes += 1")
    i_cfg = src.find("_cfg_state = self.ensemble.conf_floor_state")
    assert 0 < i_cb3 < i_cfg < i_cb3 + 600, \
        "3상태 카운트가 건강도 계측 자리에서 떨어지면 분모가 달라진다"


def test_mc_gap_alert_reports_all_three():
    """경보에 '재지 않음'이 빠지면 앞의 두 수치를 해석할 수 없다(원칙 ②)."""
    src = io.open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()
    assert "도달가능 %d분 · 도달불가 %d분 · 재지않음 %d분" in src
    # 세 경로(하한미달·평균미달·정상) 전부에 붙어야 한다
    assert src.count("{_cfg_txt}") == 2      # f-string 경보 2곳
    assert src.count("_cfg_txt,") >= 1       # logger.info 정상 경로
