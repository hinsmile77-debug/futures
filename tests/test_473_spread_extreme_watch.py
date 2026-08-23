# -*- coding: utf-8 -*-
"""[MW0601 473차 / F-8 Phase A] 극단 스프레드 채널 — 판정 규율 회귀 테스트.

무엇을 지키는가
---------------
이 채널의 위험은 계산 오류가 아니라 **사후적합**이다. 사전등록 임계(20틱)에서
표본이 6건뿐이라 INSUFFICIENT가 나오는데, 옆 버킷(8~12틱 n=36)에는 표본이 있고
평균이 음수다. 문턱을 낮추거나 컷을 옮기면 "유의한" 결과를 만들 수 있다 —
그것이 313차 원칙 ④가 금지하는 바로 그 행동이고, 458차 D6도
*"min_days·min_bars를 낮추지 말 것 — 사전등록 위반이다"* 로 같은 경고를 남겼다.

그래서 세 가지를 못박는다.

1. **합격선은 settings에서만 온다** — 코드에 리터럴로 박히면 조용히 바뀐다.
2. **표본 미달이면 판정하지 않는다** — INSUFFICIENT는 실패가 아니라 결론이다.
3. **진단 버킷은 판정에 관여하지 않는다** — 버킷 표는 "표본이 어디 있는지"를
   보여줄 뿐이며, 거기서 좋아 보이는 컷으로 갈아타면 안 된다.

실행:
    pytest tests/test_473_spread_extreme_watch.py
"""
import inspect
import io as _io
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

os.environ["MIREUK_TEST_MODE"] = "1"

from scripts import spread_extreme_watch as SEW  # noqa: E402

_KEYS = ("block_ticks", "min_samples", "min_days", "pnl_gap_krw",
         "alpha", "drop_worst_days", "min_valid_ticks",
         "spread_source", "data_start", "entry_source")


# ── 1. 사전등록 ─────────────────────────────────────────────────────────────

def test_channel_is_preregistered_in_settings():
    """합격선 10종이 settings에 있어야 한다 — 하나라도 없으면 코드가 폴백을 쓴다."""
    from config.settings import VALIDATION_CAMPAIGN
    cfg = VALIDATION_CAMPAIGN.get("spread_extreme_watch")
    assert cfg, "spread_extreme_watch 채널이 사전등록돼 있지 않다"
    missing = [k for k in _KEYS if k not in cfg]
    assert not missing, "사전등록 키 누락: %s" % missing


def test_threshold_matches_the_flag_it_judges():
    """심사 임계가 실제 게이트 상수와 같아야 한다 — 다르면 딴 것을 재는 것이다."""
    from config.settings import (VALIDATION_CAMPAIGN,
                                 TOXICITY_SEVERE_SPREAD_BLOCK_TICKS)
    cfg = VALIDATION_CAMPAIGN["spread_extreme_watch"]
    assert float(cfg["block_ticks"]) == float(TOXICITY_SEVERE_SPREAD_BLOCK_TICKS), (
        "채널 임계(%s)와 TOXICITY_SEVERE_SPREAD_BLOCK_TICKS(%s)가 다르다"
        % (cfg["block_ticks"], TOXICITY_SEVERE_SPREAD_BLOCK_TICKS))


def test_no_hardcoded_thresholds_in_compute():
    """`compute()`가 임계를 settings에서 읽는가 — 리터럴로 박히면 조용히 바뀐다.

    폴백 기본값(`cfg.get(key, 20.0)`)까지 금지하지는 않는다. 규율은 "settings가
    정본"이지 "리터럴이 한 글자도 없어야 한다"가 아니다 — 후자를 강제하면
    폴백 자체를 없애게 되고, 키가 빠졌을 때 KeyError로 죽는다.
    """
    src = inspect.getsource(SEW.compute)
    for key in ("block_ticks", "min_samples", "min_days",
                "pnl_gap_krw", "alpha", "drop_worst_days"):
        assert 'cfg.get("%s"' % key in src, (
            "%s 를 settings에서 읽지 않는다 — 하드코딩 의심" % key)


# ── 2. 표본 미달이면 판정하지 않는다 ────────────────────────────────────────

def test_insufficient_is_a_verdict_not_a_crash():
    """실 DB로 돌려도 예외 없이 판정 문자열이 나온다."""
    res = SEW.compute()
    if not res.get("available"):
        pytest.skip("DB 미가용 — 이 PC에서는 검증 불가: %s" % res.get("reason"))
    assert res["verdict"] in ("BLOCK_JUSTIFIED", "BLOCK_UNJUSTIFIED", "INSUFFICIENT")
    assert res.get("reason"), "판정에 사유가 없다"


def test_sample_gate_precedes_statistics():
    """표본 관문이 통계보다 먼저다 — 미달인데 p값이 나오면 안 된다.

    미달 상태에서 통계를 계산해 두면, 다음 세션이 그 숫자를 보고 문턱을 내리고
    싶어진다. 아예 계산하지 않는 것이 규율이다.
    """
    res = SEW.compute()
    if not res.get("available"):
        pytest.skip("DB 미가용")
    if res["verdict"] == "INSUFFICIENT":
        assert res.get("sign_test_p") is None, (
            "표본 미달인데 부호검정을 계산했다 — 문턱 인하 유혹을 만든다")
        assert res.get("day_mean_diff_krw") is None


def test_sample_gates_use_registered_values():
    """미달 사유 문자열이 사전등록 값을 그대로 인용하는가(문턱 몰래 변경 탐지)."""
    from config.settings import VALIDATION_CAMPAIGN
    cfg = VALIDATION_CAMPAIGN["spread_extreme_watch"]
    res = SEW.compute()
    if not res.get("available") or res["verdict"] != "INSUFFICIENT":
        pytest.skip("현재 INSUFFICIENT가 아님 — 이 검사는 해당 없음")
    reason = res["reason"]
    assert (str(cfg["min_samples"]) in reason) or (str(cfg["min_days"]) in reason), (
        "미달 사유가 사전등록 값을 인용하지 않는다: %s" % reason)


# ── 3. 진단은 판정에 관여하지 않는다 (313차 원칙 ④) ─────────────────────────

def test_verdict_does_not_read_diagnostic_buckets():
    """판정이 진단 버킷을 읽으면 사후적합 경로가 열린다.

    판정에 쓰이는 분할은 사전등록된 `block_ticks` 하나에서 파생된 hi/lo 뿐이어야
    한다. `compute()`가 `_DIAG_EDGES`를 참조하는 순간 "표본이 많은 컷"으로
    갈아탈 수 있게 된다.
    """
    src = inspect.getsource(SEW.compute)
    assert "_DIAG_EDGES" not in src, (
        "compute()가 진단 버킷 경계를 참조한다 — 판정과 진단이 섞였다")
    # `buckets`는 결과 dict에 담기기만 하고(1회) 판정 분기에서 읽히지 않아야 한다.
    assert src.count('res["buckets"]') == 1, (
        "compute()가 buckets를 두 번 이상 만진다 — 판정 오염 의심")


def test_diag_edges_include_the_registered_threshold():
    """진단 버킷이 사전등록 임계를 경계로 포함해야 표가 판정과 정합한다."""
    from config.settings import VALIDATION_CAMPAIGN
    thr = float(VALIDATION_CAMPAIGN["spread_extreme_watch"]["block_ticks"])
    assert thr in SEW._DIAG_EDGES, (
        "진단 경계 %s에 사전등록 임계 %s가 없다 — 표와 판정이 다른 컷을 말한다"
        % (list(SEW._DIAG_EDGES), thr))


def test_bucket_order_is_numeric():
    """`>=20`이 `12-20` 앞에 오면 운영자가 구간을 오독한다."""
    pos = [{"spread": s, "pnl_per_contract": 0.0, "day": "2026-08-17"}
           for s in (1.0, 9.0, 15.0, 30.0)]
    names = [b["bucket"] for b in SEW._buckets(pos)]
    assert names == ["<8", "8-12", "12-20", ">=20"], names


# ── 4. 계측 4원칙 ───────────────────────────────────────────────────────────

def test_zero_spread_is_excluded_not_counted_as_low():
    """호가 결측 폴백(0.0)을 대조군에 넣으면 "스프레드 0"으로 위장된다(원칙 ②)."""
    from config.settings import VALIDATION_CAMPAIGN
    cfg = VALIDATION_CAMPAIGN["spread_extreme_watch"]
    assert float(cfg["min_valid_ticks"]) > 0.0, (
        "min_valid_ticks가 0 이하면 호가 결측이 대조군에 섞인다")
    src = inspect.getsource(SEW.compute)
    assert "invalid_spread" in src, "결측 제외 카운터가 없다 — 탈락이 안 보인다(원칙 ③)"


def test_positions_are_merged_not_legs():
    """레그 단위 집계 금지(원칙 ①) — entry_ts 병합과 sum 수량."""
    src = inspect.getsource(SEW._merged_positions)
    assert "entry_qty" in src, "entry_qty 우선 사용이 없다(417차 ②)"
    assert 'm["qty"] +=' in src, "수량이 sum이 아니다 — max는 417차에 반증됐다"


def test_unmatched_positions_are_reported():
    """매칭 실패를 조용히 버리지 않는다(원칙 ③ — 탈락 가시화)."""
    res = SEW.compute()
    if not res.get("available"):
        pytest.skip("DB 미가용")
    assert "unmatched_positions" in res
    assert "invalid_spread_positions" in res


# ── 5. 통계 ─────────────────────────────────────────────────────────────────

def test_sign_test_basic():
    p, pos, neg = SEW._sign_test_p([1, 1, 1, 1, 1, 1])
    assert pos == 6 and neg == 0
    assert p is not None and p < 0.05
    p2, _, _ = SEW._sign_test_p([1, -1, 1, -1])
    assert p2 == 1.0
    p3, pos3, neg3 = SEW._sign_test_p([0, 0])
    assert p3 is None and pos3 == 0 and neg3 == 0


def test_accrual_eta_is_reported_when_short():
    """표본 미달이면 **언제 채워지는지**를 반드시 말한다.

    F-8이 한 달 넘게 멈춰 있던 이유가 "쌓이면 본다"를 검증하지 않은 것이다.
    ETA가 없으면 같은 상태가 반복된다.
    """
    res = SEW.compute()
    if not res.get("available") or res["verdict"] != "INSUFFICIENT":
        pytest.skip("현재 INSUFFICIENT가 아님")
    acc = res.get("accrual") or {}
    assert acc.get("trading_days_observed", 0) > 0

    # [MW0602 488차 후속2] 요구를 **정밀화**했다 — 약화가 아니다.
    #   종전: `eta_trading_days is not None`
    #   현재: **숫자 또는 산출 불가 사유 중 하나는 반드시 있다**
    # 이유: 적립 속도가 **0.000건/거래일**이 되면(=처리군 진입 0건) ETA 는 수학적으로
    # 산출 불가다. 그때 숫자를 내라고 요구하면 코드가 **문턱을 낮추거나 값을 지어내는**
    # 쪽으로 밀린다 — 458차 D6(사전등록 위반)이 그렇게 생겼다. 이 채널이 지켜야 할 것은
    # "숫자를 낸다"가 아니라 **"침묵하지 않는다"** 이므로 그것을 그대로 단언한다.
    # 2026-08-23 실측이 정확히 그 상태다: 66거래일 · 처리군 0건 · 진입 스프레드 최댓값
    # 19.0002(임계 20 미만) → `eta_status="적립없음"`.
    assert acc.get("eta_status") in ("추정가능", "적립없음", "도달"), (
        "적립 상태를 말하지 않는다: %r" % (acc.get("eta_status"),))
    if acc.get("eta_trading_days") is None:
        assert acc.get("eta_reason"), (
            "ETA 를 못 내면서 **이유도 말하지 않는다** — 이것이 F-8 을 한 달 넘게 "
            "멈춰 있게 한 침묵이다")
        assert "문턱을 낮춰" in acc["eta_reason"], (
            "산출 불가 사유에 문턱 인하 금지 경고가 없다(458차 D6 재발 방지)")

    # 사람이 읽는 출력도 침묵하지 않아야 한다 — 값이 dict 에만 있고 리포트에 없으면
    # 계측이 죽은 것과 같다(이 프로젝트의 단골 실패: 471차 F-2 하트비트·311차 섀도).
    # 상세 출력은 `main()` 안에 있어 함수로 떼어 부를 수 없으므로 **소스로 확인**한다:
    # 적립 절의 출력 조건이 `eta_trading_days` 가 아니라 `trading_days_observed` 여야
    # 한다(전자면 ETA 산출 불가일 때 절 전체가 사라진다 — 종전 결함).
    src = _io.open(os.path.join(_ROOT, "scripts", "spread_extreme_watch.py"),
                   encoding="utf-8").read()
    blk = src[src.index('acc = res.get("accrual")'):]
    blk = blk[:blk.index("column_crosscheck")]
    assert 'if acc.get("trading_days_observed")' in blk, (
        "적립 절이 ETA 유무로 갈린다 — ETA 를 못 낼 때 통째로 사라진다")
    assert 'eta_reason' in blk, "산출 불가 사유를 출력하지 않는다"
