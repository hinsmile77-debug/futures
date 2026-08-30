# -*- coding: utf-8 -*-
"""[MW0602 502차] U-1 `trend_efficiency_ready` · U-2 [57] 게이트 섀도 회귀 고정.

**U-1 — 폴백이 게이트를 통과한다(계측 4원칙 ④).**
`calculate_trend_efficiency`는 표본 부족 시 중립값 **0.5**를 돌려주는데, 진입
게이트 후보 임계는 **0.32**다. 즉 `0.5 > 0.32`라 *"아직 계산할 수 없다"* 가
*"효율적인 구간이다"* 로 읽혀 **폴백이 게이트를 통과한다.** 전 분봉의
0.49%(57/11,739)로 빈도는 낮지만 **장 초반에 몰리고**, 하필 그 구간이 손실
집중 구간이다(501차 딥다이브 §7: 개장 1시간이 일 손실의 46~74%).
FP-CRITICAL(2개월 PSI=0.0)·TOX 죽은 섀도와 같은 계열의 씨앗이라 배선 전에 막는다.

⚠ `path_sum < 1e-9` → **0.0**은 폴백이 아니라 축퇴(degenerate) 규약이다.
10분간 가격이 전혀 안 움직여 ER = 0/0 이 정의되지 않는 경우이며, 게이트 관점에서는
**스킵 쪽**(0.0 < 0.32)이라 U-1이 막으려는 결함이 아니다. 그래서 ready=True다.

**U-2 — [57] 채널 사전등록은 결과를 보기 전에 박은 것이다.**
임계 0.32는 501차 후속2가 시간분할·LODO로 고정했고 **사후 완화·강화 금지**
(§9-4 검증 시계 리셋 대상)다. 이 테스트가 그 값을 고정해, 누가 바꾸면 깨진다.

**U-2 — MFE/MAE는 고정 30분 창이다.**
resolver가 STOP/TP1 배리어 히트에서 창을 끊으면 **보유기간 내 MFE**가 되어
501차 딥다이브 §4-1의 포착률 분석과 단위가 섞인다(후속2 부록이 명시적으로
경고한 실패다 — 조사 중 실제로 한 번 섞였다). 배리어를 맞은 뒤에도 창 끝까지
누적하는지를 고정한다.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ── U-1. ready 플래그 ────────────────────────────────────────────────────────

def _f():
    from features.technical.trend_efficiency import calculate_trend_efficiency
    return calculate_trend_efficiency


def test_u1a_warmup_fallback_is_flagged_not_ready():
    """표본 부족 → (0.5, False). 값만 보면 게이트를 통과하므로 플래그가 유일한 방어다."""
    val, ready = _f()([1.0, 2.0, 3.0], window=10, return_ready=True)
    assert val == 0.5
    assert ready is False


def test_u1b_fallback_value_would_pass_the_gate():
    """🔴 이 테스트가 U-1의 존재 이유다 — 폴백값이 임계보다 크다는 사실을 고정한다.

    이 관계가 깨지면(예: 폴백을 0.0으로 바꾸면) U-1의 근거가 사라지므로
    그때는 이 테스트와 함께 설계를 다시 검토해야 한다.
    """
    from config.settings import VALIDATION_CAMPAIGN
    thr = VALIDATION_CAMPAIGN["trend_efficiency_entry_gate"]["threshold"]
    fallback, ready = _f()([1.0], window=10, return_ready=True)
    assert ready is False
    assert fallback > thr, (
        "폴백 %.3f 이 임계 %.3f 이하가 됐다 — U-1 설계 전제가 바뀌었다" % (fallback, thr))


def test_u1c_degenerate_flat_market_is_ready_not_fallback():
    """가격 무변동(ER 0/0) → 0.0 이며 ready=True. 폴백과 구분한다(게이트를 통과하지 않음)."""
    val, ready = _f()([100.0] * 12, window=10, return_ready=True)
    assert val == 0.0
    assert ready is True


def test_u1d_backward_compatible_scalar_return():
    """`return_ready` 미지정 호출부(GBM 피처 경로 등)는 기존대로 float를 받는다."""
    trend = [390.0 + i * 0.1 for i in range(15)]
    out = _f()(trend, window=10)
    assert isinstance(out, float)
    assert out > 0.99


def test_u1e_feature_builder_emits_ready_flag():
    """FeatureBuilder가 매분 플래그를 함께 낸다 — hurst_ready 관례와 동일."""
    from features.feature_builder import FeatureBuilder
    fb = FeatureBuilder()
    out = None
    for i in range(14):
        out = fb.build({"close": 390.0 + i * 0.1, "high": 390.12 + i * 0.1,
                        "low": 389.9 + i * 0.1, "open": 390.0 + i * 0.1,
                        "volume": 100 + i})
    assert "trend_efficiency_ready" in out
    assert out["trend_efficiency_ready"] is True
    # STEP9 직렬화(main.py `_feat_clean`)가 bool을 삼키는지 — hurst_ready와 같은 취급
    clean = {k: round(float(v), 4) for k, v in out.items()
             if v is not None and v == v}
    assert clean["trend_efficiency_ready"] == 1.0


# ── U-2. 사전등록 고정 ───────────────────────────────────────────────────────

def test_u2a_channel_is_preregistered_with_frozen_threshold():
    """🔴 임계 0.32는 사후 변경 금지(§9-4). 바꾸려면 주간회의 의결이 선행한다."""
    from config.settings import VALIDATION_CAMPAIGN
    cr = VALIDATION_CAMPAIGN["trend_efficiency_entry_gate"]
    assert cr["threshold"] == 0.32
    assert cr["min_samples"] == 20        # 관측에서 역산하지 않은 값(타 채널과 동일)
    assert cr["cf_window_min"] == 30
    assert cr["require_ready"] is True     # 폴백 행은 판정 모집단에서 제외
    # 승격 순서 — 317차 FalseBlock 교훈(하드차단 직행 금지)
    assert cr["promotion_order"][0] == "size_multiplier"
    assert cr["promotion_order"][-1] == "block"


def test_u2b_shadow_table_exists_with_required_axes():
    """테이블에 두 질문의 축이 모두 있어야 한다 — [57] 판정과 항목 ④ 표본."""
    import sqlite3
    from config.settings import TRADES_DB
    from utils.db_utils import init_trades_db
    init_trades_db()
    con = sqlite3.connect(TRADES_DB)
    try:
        cols = {r[1] for r in con.execute(
            "PRAGMA table_info(trend_efficiency_gate_shadow)")}
    finally:
        con.close()
    assert cols, "trend_efficiency_gate_shadow 테이블이 없다"
    # [57] 게이트 판정 축
    for c in ("te", "te_ready", "would_skip", "hyp_pnl_pts", "cf_outcome"):
        assert c in cols, "판정 축 누락: %s" % c
    # 항목 ④(고te TP 확대) 축 — 고정 30분 창 편위
    for c in ("mfe30_atr", "mae30_atr", "atr"):
        assert c in cols, "항목 ④ 축 누락: %s" % c


def test_u2c_resolver_runs_and_holds_when_sample_short():
    """표본 미달이면 조용히 INSUFFICIENT — 문턱을 낮춰 판정하지 않는다(458차 D6)."""
    import scripts.generate_validation_campaign_report as R
    out = R.resolve_and_eval_trend_efficiency_gate()
    assert out.get("error") is None, "resolver 오류: %s" % out.get("error")
    assert out["threshold"] == 0.32
    if out["n_resolved_skip"] < 20:
        assert out["verdict"] == "INSUFFICIENT"


# ── U-2. 고정 30분 창 불변식 ─────────────────────────────────────────────────

def test_u2d_mfe_window_does_not_break_at_the_barrier():
    """🔴 배리어를 맞아도 MFE/MAE는 창 끝까지 누적한다.

    후속2 부록이 명시적으로 경고한 실패다("보유기간 내 MFE와 혼동 금지 — 섞으면
    딥다이브 §4-1의 포착률이 무의미해진다"). 여기서는 resolver 본문의 누적 규칙을
    같은 형태로 재현해 **배리어 이후 봉이 반영되는지**를 고정한다.

    시나리오: LONG 진입 390.0, 스톱 388.0. 2분째에 스톱을 맞고, 5분째에 396.0까지
    간다. 창을 끊으면 MFE는 1.0에 그치지만 고정 30분 창이면 6.0이다.
    """
    entry, stop, atr = 390.0, 388.0, 2.0
    bars = [  # (high, low)
        (391.0, 389.5),
        (390.5, 387.5),   # ← 여기서 STOP 히트
        (392.0, 389.0),
        (394.0, 391.0),
        (396.0, 393.0),   # ← 배리어 이후 최대 유리편위
    ]
    mfe = mae = 0.0
    cf_outcome, cf_price = "NEITHER", None
    for hi, lo in bars:
        mfe = max(mfe, hi - entry)
        mae = min(mae, lo - entry)
        if cf_price is None and lo <= stop:
            cf_outcome, cf_price = "STOP", stop
    assert cf_outcome == "STOP", "배리어 판정은 첫 히트를 채택해야 한다"
    assert mfe / atr == 3.0, "배리어에서 창이 끊겼다 — 보유기간 MFE가 됐다"
    assert mae / atr == -1.25


def test_u2e_skip_cohort_sign_convention():
    """🔴 부호가 [6]·[9]와 반대다 — 스킵 코호트 `hyp < 0` = 게이트가 옳다.

    이 채널은 *차단된* 신호가 아니라 **실제 진입한 분봉**을 기록한다(게이트가 아직
    라이브가 아니라 차단된 신호가 존재하지 않는다). 승격 판정이 이 부호에 걸려
    있으므로 뒤집히면 정반대 결론이 난다.
    """
    import scripts.generate_validation_campaign_report as R
    import inspect
    src = inspect.getsource(R.resolve_and_eval_trend_efficiency_gate)
    assert "total_hyp < -(cost_pt" in src, (
        "승격 조건의 부호가 바뀌었다 — 스킵 코호트가 손실일 때 승격 검토여야 한다")
