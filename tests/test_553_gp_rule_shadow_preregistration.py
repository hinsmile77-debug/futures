# -*- coding: utf-8 -*-
"""[MW0601 553차 / Phase 0] GP 규칙 병행운용(섀도) **사전등록의 동결 불변식**.

무엇을 지키는가
---------------
`VALIDATION_CAMPAIGN["gp_rule_long_watch"]` / `["gp_rule_short_watch"]` 는
**데이터를 보기 전에** 고정한 합격선이다(§9 사전등록). 관측 60거래일 동안 값이
바뀌면 그건 판정이 아니라 사후 최적화다 — 458차 D6(문턱을 낮춰 판정)이 같은 계열의
사고였고, 313차 ④가 「컷은 관측 전에 고정, 사후 변경 금지」를 규약으로 세웠다.

이 파일이 하는 일
-----------------
**규칙이 옳은지 판정하지 않는다.** 그건 관측 60거래일 뒤 리포트가 한다.
여기서는 아래가 **함께** 움직이도록 묶는다 — 하나만 바뀌면 깨져서 나머지 갱신을 강제한다.

    config/settings.py:VALIDATION_CAMPAIGN["gp_rule_*"]      (사전등록 합격선·규칙정의)
        ↕
    config/constants.py:BROKER_CHANNEL_SPECS                 (왕복비용의 원천)
        ↕
    config/settings.py:GP_CROSS_PERIOD                       (라이브 피처의 룩백)
        ↕
    docs/…/GP병행운용_구현가능성_검토_MW0601-20260910.md      (근거 문서)

테스트가 깨지면 "고쳐야 할 버그"가 아니라 **"사전등록을 바꾸려는 것이 맞는지
DECISION_LOG 에 사유를 남기고 검증 시계를 리셋하라"** 는 신호다(§9-4).

🔴 왕복비용은 CYBOS·CREON 으로 **분리**한다 [2026-09-10 사용자 지시].
   같은 규칙의 소급 t 가 채널에 따라 갈린다 — 숏은 CYBOS 1.64(미달) / CREON 2.30(통과).
   그래서 `reference` 표가 `BROKER_CHANNEL_SPECS` 에서 실제로 파생되는지 매번 재계산해
   대조한다. 요율이 조용히 바뀌면(493차 사건) 여기서 먼저 걸린다.

실행:
    conda run -n py37_32 python -m pytest tests/test_553_gp_rule_shadow_preregistration.py -v
"""
import io
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

os.environ["MIREUK_TEST_MODE"] = "1"

import pytest  # noqa: E402

from config.constants import (  # noqa: E402
    BROKER_CHANNEL_SPECS, MINI_FUTURES_PT_VALUE, MINI_FUTURES_TICK_SIZE,
)
from config.settings import GP_CROSS_PERIOD, VALIDATION_CAMPAIGN  # noqa: E402

_COST = VALIDATION_CAMPAIGN["gp_rule_cost"]
_LONG = VALIDATION_CAMPAIGN["gp_rule_long_watch"]
_SHORT = VALIDATION_CAMPAIGN["gp_rule_short_watch"]
_MULT = VALIDATION_CAMPAIGN["gp_rule_multiplicity"]

_DOC = os.path.join(
    _ROOT, "docs", "미륵이고도화3", "Golden power",
    "GP병행운용_구현가능성_검토_MW0601-20260910.md",
)

#: 2026-09-10 Phase 0 등록 시점의 합격선. 바꾸려면 DECISION_LOG 기록 + 검증 시계 리셋.
_FROZEN_LONG = {
    "period": 20, "cross_level": 0.5, "entry_delay_bars": 0,
    "hold_minutes": 90, "session_start": "09:20", "session_end": "14:50",
    "force_exit": "15:05", "stop_loss": None, "non_overlap": True,
    "min_samples": 100, "min_days": 40, "unit": "position",
    "alpha": 0.05, "drop_best_days": 3, "observation_days": 60,
}
_FROZEN_SHORT = {
    "period": 20, "cross_level": 0.5, "entry_delay_bars": 0,
    "squeeze_gb_max": 0.5, "squeeze_gs_max": 0.5, "squeeze_spread_max": 0.5,
    "squeeze_valid_bars": 10, "trigger_gb_max": 0.10,
    "regime_filter": "ma20_lt_ma60", "ma_fast": 20, "ma_slow": 60,
    "exit_gs_target": 1.2, "hold_minutes": 60, "force_exit": "15:05",
    "opposite_line_stop": None, "max_per_day": 1,
    "session_start": "09:20", "session_end": "14:50",
    "min_samples": 30, "min_days": 25, "unit": "position",
    "alpha": 0.05, "drop_best_days": 3, "observation_days": 60,
}


def _read(path):
    with io.open(path, encoding="utf-8") as fh:
        return fh.read()


# ── 합격선 동결 ──────────────────────────────────────────────────────────────

@pytest.mark.parametrize("key,expected", sorted(_FROZEN_LONG.items()))
def test_long_channel_is_frozen(key, expected):
    assert _LONG[key] == expected, (
        "GP-R1 사전등록 `%s` 가 %r → %r 로 바뀌었다. 관측 중 변경은 사후 최적화다 "
        "(313차 ④ · 458차 D6). 바꾸려면 DECISION_LOG 기록 + 검증 시계 리셋."
        % (key, expected, _LONG[key]))


@pytest.mark.parametrize("key,expected", sorted(_FROZEN_SHORT.items()))
def test_short_channel_is_frozen(key, expected):
    assert _SHORT[key] == expected, (
        "GP-R2 사전등록 `%s` 가 %r → %r 로 바뀌었다. 관측 중 변경은 사후 최적화다."
        % (key, expected, _SHORT[key]))


# ── 왕복비용: CYBOS·CREON 분리 ───────────────────────────────────────────────

def test_cost_is_split_by_broker_channel():
    """[2026-09-10 사용자 지시] 채널을 합치면 숏 판정이 뒤집힌다."""
    assert _COST["split_by_channel"] is True
    assert _COST["report_both"] is True
    assert _COST["cost_source"] == "BROKER_CHANNEL_SPECS"
    assert set(_COST["reference"]) >= {"CYBOS", "CREON"}


@pytest.mark.parametrize("channel", ["CYBOS", "CREON"])
def test_cost_reference_is_derived_from_broker_specs(channel):
    """참조표가 `BROKER_CHANNEL_SPECS` 에서 실제로 파생되는가.

    🔴 핀값 금지(493차) — 요율이 바뀌었는데 표만 남아 있으면 그 표가 낙관 쪽으로
    거짓말한다. 2026-05-11 브로커 전환 때 정확히 그 일이 6개월간 벌어졌다.
    """
    ref = _COST["reference"][channel]
    live_rate = BROKER_CHANNEL_SPECS[channel]["one_way_commission_rate"]
    assert ref["one_way_rate"] == live_rate, (
        "%s 요율이 %g → %g 로 바뀌었다. `reference` 표와 26주 재검증 항목을 함께 갱신할 것."
        % (channel, ref["one_way_rate"], live_rate))

    price = _COST["reference"]["price_ref"]
    slip_pt = 2.0 * _COST["slip_ticks_per_side"] * MINI_FUTURES_TICK_SIZE
    comm_pt = 2.0 * price * live_rate
    assert abs(comm_pt - ref["comm_pt"]) < 1e-6
    assert abs(comm_pt + slip_pt - ref["roundtrip_pt"]) < 1e-6
    assert abs((comm_pt + slip_pt) * MINI_FUTURES_PT_VALUE - ref["roundtrip_krw"]) < 1.0


def test_point_value_is_mini_not_regular():
    """🔴 원문서가 250,000원/pt 로 환산해 원화를 5배 과대계상했다."""
    assert _COST["pt_value_krw"] == MINI_FUTURES_PT_VALUE == 50_000, (
        "운영 종목은 A0569000 미니선물이다. 250,000 은 정규선물(A01…) 승수다.")


def test_legacy_challenger_rate_is_recorded_as_to_be_replaced():
    """challenger 엔진의 키움 잔재 요율(1.5e-05)이 Phase 2 교체 대상으로 남아 있는가."""
    assert _COST["legacy_rate_to_replace"] == 1.5e-05
    assert _COST["legacy_rate_to_replace"] != \
        BROKER_CHANNEL_SPECS["CYBOS"]["one_way_commission_rate"]


# ── 라이브 피처와의 정합 ─────────────────────────────────────────────────────

@pytest.mark.parametrize("ch", [_LONG, _SHORT])
def test_period_matches_live_feature_lookback(ch):
    """사전등록 룩백이 라이브 피처(`gp_buy_20` 등)와 갈리면 다른 규칙을 재게 된다."""
    assert ch["period"] == GP_CROSS_PERIOD, (
        "사전등록 period=%s 인데 GP_CROSS_PERIOD=%s 다. 한쪽만 바꾸면 안 된다."
        % (ch["period"], GP_CROSS_PERIOD))


def test_triggers_name_live_feature_keys():
    """트리거가 실제로 존재하는 피처 키를 가리키는가(산문 별칭 `gp_bull_20` 금지)."""
    assert _LONG["trigger"] == "gp_cross_up_%d" % GP_CROSS_PERIOD
    assert _SHORT["trigger"] == "gp_cross_dn_%d" % GP_CROSS_PERIOD


# ── 안전 불변식 ──────────────────────────────────────────────────────────────

@pytest.mark.parametrize("ch,name", [(_LONG, "GP-R1"), (_SHORT, "GP-R2")])
def test_force_exit_is_not_later_than_absolute_rule(ch, name):
    """절대원칙 §1 — 15:10 강제청산보다 늦으면 안 된다."""
    assert ch["force_exit"] <= "15:10", "%s 강제청산이 절대원칙 §1을 넘는다" % name
    assert ch["session_end"] < ch["force_exit"]


@pytest.mark.parametrize("ch,name", [(_LONG, "GP-R1"), (_SHORT, "GP-R2")])
def test_no_live_order_promotion(ch, name):
    """섀도 전용. 자동 승격 경로가 생기면 절대원칙 §6 위반이다."""
    assert ch["live_order_forbidden"] is True
    assert ch["promotion_order"] == ["record_only", "report_only"], (
        "%s 승격 형태는 판정 전에 확정한다 — 실주문 승격은 주간회의 안건이다." % name)
    assert ch["entry_source"] == "GP_SHADOW", (
        "GP 는 `trades` 테이블의 실거래와 섞이면 안 된다(브로커 대사·전환기준 ① 오염).")


def test_long_rule_is_judged_against_beta_not_total_pnl():
    """🔴 롱은 손익의 59%가 시장 드리프트다 — 총손익으로 판정하면 상승장이 통과시킨다."""
    assert _LONG["require_beat_exposure_matched_control"] is True
    assert _LONG["control_kind"] == "exposure_matched_buy_and_hold"
    assert _LONG["require_alpha_positive"] is True
    assert "alpha_t_min" not in _LONG, (
        "α 유의성은 요구하지 않는다 — 소급 211일에도 t=1.46 이라 60거래일에 t≥1.96 은 "
        "구조적으로 불가능하다. 달성 불가능한 문턱은 사전등록이 아니라 알리바이다.")


def test_long_rule_forbids_the_rejected_filters():
    """원문서 기각 목록 — 압축·수렴 필터를 붙이면 90분 +432 → +131 로 300pt 가 사라진다."""
    assert set(_LONG["forbidden_additions"]) == {
        "squeeze_prefilter", "opposite_line_convergence"}


def test_short_rule_keeps_the_regime_filter_and_its_control():
    """MA20>MA60 구간만 떼면 −186.7pt(t=−2.71). 필터는 선택이 아니다."""
    assert _SHORT["regime_filter"] == "ma20_lt_ma60"
    assert _SHORT["require_beta_nonpositive"] is True
    assert _SHORT["record_no_filter_control"] is True


# ── 다중검정 회계 ────────────────────────────────────────────────────────────

def test_multiplicity_ledger_is_not_reset():
    """원문서 §운용권고 5 — 탐색 카운트는 누적한다."""
    assert _MULT["exploration_tests_prior"] >= 70
    assert _MULT["confirmatory_tests_n"] == 2
    assert _MULT["reset_forbidden"] is True


# ── 표본 도달 가능성 ─────────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "ch,per_day,name",
    [(_LONG, 587.0 / 211.0, "GP-R1"), (_SHORT, 149.0 / 211.0, "GP-R2")],
)
def test_min_samples_is_reachable_within_observation_window(ch, per_day, name):
    """🔴 도달 불가능한 표본선은 사전등록이 아니라 영구 미판정이다.

    TOX-SEVERE-SPREAD 가 `min_samples=20` 에 ETA 7.1개월이라 전환기준 ⑨ 하나가
    전체를 잠갔던 사건(489차 A-2)의 재발 방지다.
    """
    expected = per_day * ch["observation_days"]
    assert ch["min_samples"] <= expected, (
        "%s: 소급 적립속도 %.3f건/일 × %d거래일 = %.0f건인데 min_samples=%d 다 — "
        "관측 창 안에 도달할 수 없다."
        % (name, per_day, ch["observation_days"], expected, ch["min_samples"]))
    assert ch["min_days"] <= ch["observation_days"]


# ── 문서 동기화 ──────────────────────────────────────────────────────────────

def test_rule_doc_and_review_doc_exist():
    """근거 문서가 사라지면 이 사전등록의 해석 근거가 사라진다."""
    assert os.path.exists(_DOC), "검토 보고서가 없다: %s" % _DOC
    for ch in (_LONG, _SHORT):
        assert os.path.exists(os.path.join(_ROOT, ch["rule_doc"])), \
            "규칙 원문서가 없다: %s" % ch["rule_doc"]


def test_review_doc_records_the_channel_split_cost():
    """왕복비용 분리 근거가 문서에 남아 있는가 — 코드만 바뀌고 문서가 못 따라가는 것을 막는다."""
    md = _read(_DOC)
    for channel in ("CYBOS", "CREON"):
        assert channel in md, "검토 문서에 %s 채널 비용 근거가 없다" % channel


# ── 미배선 상태의 명시 ───────────────────────────────────────────────────────

@pytest.mark.parametrize("ch,name", [(_LONG, "GP-R1"), (_SHORT, "GP-R2")])
def test_data_start_is_none_until_wiring(ch, name):
    """Phase 3 배선 전까지 `data_start` 는 None 이어야 한다.

    ⚠ 이 테스트는 **배선하면 깨진다** — 그게 의도다. 깨지면 이 파일에서 해당
    파라미터를 제거하고 `dev_memory/DECISION_LOG.md` 에 실제 개시일을 남길 것.
    날짜를 채우는 것은 기준 변경이 아니다(`data_start_rule` 이 정한 규칙의 적용이다).
    """
    if ch["data_start"] is None:
        assert ch["data_start_rule"], "%s: data_start 가 비었는데 채우는 규칙도 없다" % name
    else:
        assert len(ch["data_start"]) == 10 and ch["data_start"][4] == "-", (
            "%s: data_start 형식이 YYYY-MM-DD 가 아니다" % name)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
