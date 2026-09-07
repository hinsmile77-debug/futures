# -*- coding: utf-8 -*-
"""[MW0601 540차] GOLDEN POWER 교차 피처 — 산식·워밍업·기록전용 규율 회귀 테스트.

배경 (2026-09-07)
-----------------
사용자 관찰: 「GB 가 0.5 를 상향 돌파하고 GS 는 0 에 수렴하는 순간 진입하면 수익 청산
확률이 높다」. 실측상 관찰은 사실이다(TP 선도달 75.6% vs 무작위 73.2%, p=0.044).
그러나 그 격자(스톱1.5ATR·TP0.5ATR)의 **손익분기 승률이 정확히 75.0%**라 초과분은
+0.6%p 뿐이고, 청산 격자 19개 전수에서 net 흑자는 0개였다. 상대 ATR ≥16bp 로 좁혔을 때만
흑자(n=116, 건당 +6,513원)였고 **그것은 사후 발견**이다.

⇒ 그래서 이 피처는 **기록 전용**이다. 사전등록 채널 `gp_cross_highvol_watch`(좁은 교차)와
   `gp_cross_any_watch`(순수 교차 — 대조)가 전향으로 판정할 때까지 매매 정책은 무변경이다.

이 파일이 못박는 것
-------------------
1. 산식 — 사이보스 GOLDEN POWER 복원식 그대로 (1.0 = 이격 0.5%)
2. 교차 판정 — 전봉 GP 를 **버퍼에서 재계산**한다(상태 미보유). 재기동해도 어긋나지 않는다
3. 워밍업 — 0 으로 위장하지 않고 `gp_ready_20=False` (계측 4원칙 ②·④)
4. `atr_bp` — 미측정과 0 을 구분한다(`atr_bp_measured`)
5. **소비자 0곳** — 진입·사이징·체크리스트가 이 키를 읽지 않는다
6. 채널 사전등록 컷이 상수와 어긋나지 않는다

실행: pytest tests/test_540_gp_cross_features.py
"""
import os
import re
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
os.environ.setdefault("MIREUK_TEST_MODE", "1")

import pytest  # noqa: E402

from features.feature_builder import compute_gp_cross_features  # noqa: E402
from config import settings  # noqa: E402

P = 20
KEYS = ("gp_buy_20", "gp_sell_20", "gp_cross_up_20", "gp_cross_dn_20",
        "gp_cross_tight_20", "gp_ready_20", "atr_bp", "atr_bp_measured")


# ───────────────────────── 1. 산식 ─────────────────────────
def test_formula_matches_cybos_restoration():
    """GB = (종가−최저종가)/종가×200 · GS = (최고종가−종가)/종가×200."""
    closes = [100.0] * 19 + [101.0]
    f = compute_gp_cross_features(closes, atr=1.0, period=P)
    # 최저 100, 최고 101, 종가 101
    assert f["gp_buy_20"] == pytest.approx((101.0 - 100.0) / 101.0 * 200.0)
    assert f["gp_sell_20"] == pytest.approx(0.0)


def test_unit_is_half_percent():
    """1.0 = 이격 0.5%."""
    c = 100.0 / (1.0 - 0.005)          # 최저종가 대비 정확히 0.5% 위
    f = compute_gp_cross_features([100.0] * 19 + [c], atr=1.0, period=P)
    assert f["gp_buy_20"] == pytest.approx(1.0, abs=1e-9)


def test_lower_bound_is_zero_and_no_upper_bound():
    """하한 0(신저/신고 종가), 상한 없음."""
    f_lo = compute_gp_cross_features([100.0] * 19 + [99.0], atr=1.0, period=P)
    assert f_lo["gp_buy_20"] == 0.0            # 당봉이 신저 종가
    assert f_lo["gp_sell_20"] > 0
    f_hi = compute_gp_cross_features([100.0] * 19 + [110.0], atr=1.0, period=P)
    assert f_hi["gp_buy_20"] > 1.0             # 1.0 초과 가능


# ───────────────────────── 2. 교차 ─────────────────────────
def test_cross_up_fires_only_on_transition():
    """0.5 를 아래에서 위로 통과한 **그 봉에만** 1."""
    base = [100.0] * 20
    below = 100.0 / (1.0 - 0.001)      # GB ≈ 0.2 — 임계 아래
    above = 100.0 / (1.0 - 0.004)      # GB ≈ 0.8 — 임계 위
    f1 = compute_gp_cross_features(base + [below], atr=1.0, period=P)
    assert f1["gp_cross_up_20"] == 0.0
    f2 = compute_gp_cross_features(base + [below, above], atr=1.0, period=P)
    assert f2["gp_cross_up_20"] == 1.0         # 교차 발생
    f3 = compute_gp_cross_features(base + [below, above, above], atr=1.0, period=P)
    assert f3["gp_cross_up_20"] == 0.0         # 상태 연장 — 재발화 금지


def test_cross_is_stateless_recomputed_from_buffer():
    """전봉 GP 를 상태로 들지 않는다 — 같은 버퍼면 같은 답(재기동 안전)."""
    buf = [100.0] * 20 + [100.0 / (1.0 - 0.001), 100.0 / (1.0 - 0.004)]
    a = compute_gp_cross_features(buf, atr=1.0, period=P)
    b = compute_gp_cross_features(list(buf), atr=1.0, period=P)
    assert a == b
    assert a["gp_cross_up_20"] == 1.0


def test_tight_requires_opposite_side_near_zero():
    """`gp_cross_tight` 는 교차 + 반대편 ≤ eps 일 때만 1."""
    base = [100.0] * 20
    below, above = 100.0 / (1.0 - 0.001), 100.0 / (1.0 - 0.004)
    f = compute_gp_cross_features(base + [below, above], atr=1.0, period=P, eps=0.05)
    # 단조 상승이라 당봉이 신고 종가 → GS = 0 → tight
    assert f["gp_sell_20"] == pytest.approx(0.0)
    assert f["gp_cross_tight_20"] == 1.0
    # eps 를 음수로 두면 어떤 반대편 값도 통과하지 못한다
    f2 = compute_gp_cross_features(base + [below, above], atr=1.0, period=P, eps=-1.0)
    assert f2["gp_cross_up_20"] == 1.0 and f2["gp_cross_tight_20"] == 0.0


def test_cross_down_is_symmetric():
    base = [100.0] * 20
    up = 100.0 / (1.0 + 0.001)
    dn = 100.0 / (1.0 + 0.004)
    f = compute_gp_cross_features(base + [up, dn], atr=1.0, period=P)
    assert f["gp_cross_dn_20"] == 1.0 and f["gp_cross_up_20"] == 0.0


# ───────────────────── 3. 워밍업 · 미측정 ─────────────────────
def test_warmup_is_not_disguised_as_zero():
    """period 미만이면 ready=False. 0 을 값으로 위장하지 않는다(계측 4원칙 ②)."""
    f = compute_gp_cross_features([100.0] * 5, atr=1.0, period=P)
    assert f["gp_ready_20"] is False
    for k in KEYS:
        assert k in f
    # period 는 채웠지만 교차 판정용 전봉이 없는 경계
    f2 = compute_gp_cross_features([100.0] * P, atr=1.0, period=P)
    assert f2["gp_ready_20"] is False
    f3 = compute_gp_cross_features([100.0] * (P + 1), atr=1.0, period=P)
    assert f3["gp_ready_20"] is True


def test_atr_bp_distinguishes_unmeasured_from_zero():
    f = compute_gp_cross_features([100.0] * 21, atr=None, period=P)
    assert f["atr_bp_measured"] is False and f["atr_bp"] == 0.0
    f2 = compute_gp_cross_features([100.0] * 21, atr=0.16, period=P)
    assert f2["atr_bp_measured"] is True
    assert f2["atr_bp"] == pytest.approx(0.16 / 100.0 * 10000.0)   # = 16 bp


def test_empty_input_is_safe():
    f = compute_gp_cross_features([], atr=1.0, period=P)
    assert f["gp_ready_20"] is False and f["atr_bp_measured"] is False


# ───────────────────── 4. 기록 전용 규율 ─────────────────────
_CONSUMER_FILES = [
    "main.py",
    os.path.join("strategy", "entry", "checklist.py"),
    os.path.join("strategy", "entry", "position_sizer.py"),
    os.path.join("model", "ensemble_decision.py"),
]
_FEATURE_KEYS = ("gp_buy_20", "gp_sell_20", "gp_cross_up_20", "gp_cross_dn_20",
                 "gp_cross_tight_20")


def test_no_consumer_in_entry_or_sizing_path():
    """진입·사이징 경로가 이 키를 읽으면 안 된다 — 승격 전까지 매매정책 무변경."""
    for rel in _CONSUMER_FILES:
        path = os.path.join(_ROOT, rel)
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8", errors="replace") as fh:
            src = fh.read()
        for k in _FEATURE_KEYS:
            assert k not in src, (
                "%s 가 기록 전용 키 %s 를 참조한다. 승격 절차(promotion_order)를 거치지 "
                "않은 소비자다 — settings 의 채널 주석 참조." % (rel, k))


def test_feature_builder_wires_it_once():
    path = os.path.join(_ROOT, "features", "feature_builder.py")
    with open(path, encoding="utf-8", errors="replace") as fh:
        src = fh.read()
    assert src.count("features.update(compute_gp_cross_features(") == 1


# ───────────────────── 5. 채널 사전등록 정합성 ─────────────────────
def test_channels_registered():
    vc = getattr(settings, "VALIDATION_CAMPAIGN", {})
    for name in ("gp_cross_highvol_watch", "gp_cross_any_watch"):
        assert name in vc, "%s 채널이 VALIDATION_CAMPAIGN 에서 사라졌다" % name


def test_channel_cuts_match_constants():
    """채널 컷과 피처 상수가 어긋나면 소급·전향이 다른 신호를 센다."""
    vc = settings.VALIDATION_CAMPAIGN
    for name in ("gp_cross_highvol_watch", "gp_cross_any_watch"):
        ch = vc[name]
        assert ch["period"] == settings.GP_CROSS_PERIOD
        assert ch["cross_level"] == settings.GP_CROSS_LEVEL
        assert ch["tight_eps"] == settings.GP_CROSS_TIGHT_EPS
        assert ch["atr_bp_min"] == 16.0
        assert ch["hard_block_forbidden"] is True
        assert ch["cost_source"] == "BROKER_CHANNEL_SPECS"


def test_two_channels_differ_only_by_tight():
    """대조 설계의 핵심 — 두 채널은 require_tight 하나만 달라야 한다."""
    a = dict(settings.VALIDATION_CAMPAIGN["gp_cross_highvol_watch"])
    b = dict(settings.VALIDATION_CAMPAIGN["gp_cross_any_watch"])
    assert a["require_tight"] is True and b["require_tight"] is False
    for k in ("period", "cross_level", "tight_eps", "atr_bp_min", "sim", "alpha",
              "drop_best_days", "data_start"):
        assert a[k] == b[k], "대조 조건 %s 가 두 채널에서 다르다" % k


def test_control_channel_is_not_a_promotion_candidate():
    b = settings.VALIDATION_CAMPAIGN["gp_cross_any_watch"]
    assert b["promotion_order"] == ["record_only"]
    assert b.get("role") == "control_for_gp_cross_highvol_watch"


def test_prospective_only_start_date():
    """소급으로 이미 충족되면 안 된다 — data_start 가 배선일 이후여야 한다."""
    for name in ("gp_cross_highvol_watch", "gp_cross_any_watch"):
        ch = settings.VALIDATION_CAMPAIGN[name]
        assert ch["data_start"] > ch["feature_wired_date"], name


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
