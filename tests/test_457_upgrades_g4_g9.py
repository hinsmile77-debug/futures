# -*- coding: utf-8 -*-
"""457차 고도화 G4~G9 회귀 테스트.

배경: `docs/정기점검/매일점검/MW0601-20260811-점검리포트.md` §3.

    G4 direction_bias_watch  방향 편향 상시 감시 채널 (캠페인 [50])
    G5 모델 건강도 지표       ConstOut/WeightCollapse 일별 집계 + 앙상블 유효 가동률
    G6 (A3로 흡수 — 별도 구현 없음. 흡수 사실만 고정한다)
    G7 router_health_shadow  라우터 × 모델 건강도 (섀도 전용, 정책 무변경)
    G8 (tests/test_457_fallback_visibility.py 에서 별도 검증)
    G9 HealthPolicy 원인 태그 (관측 전용, 분기 보류)
"""
import json
import os
import re
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


# ── G5: 앙상블 유효 가동률 ─────────────────────────────────────────────────

def test_uptime_none_when_unmeasured():
    """계측 4원칙 ② — "측정 안 함"을 0%로 위장하지 않는다."""
    from model.scaler_monitor_db import compute_ensemble_uptime as u
    assert u(None) is None
    assert u({}) is None
    assert u({"pipeline_minutes": 0}) is None, (
        "분모 0에서 0.0을 돌려주면 '가동률 0%'와 '미측정'이 구분되지 않는다")


def test_uptime_matches_0811_observation():
    """2026-08-11 실측 재현 — 370분 중 ConstOut 13분·붕괴 82분 → 74.3%."""
    from model.scaler_monitor_db import compute_ensemble_uptime as u
    got = u({"pipeline_minutes": 370, "const_out_minutes": 13,
             "weight_collapse_minutes": 82})
    assert abs(got - 0.7432) < 0.001, got


def test_uptime_clamped_when_multi_horizon_overlap():
    """const_out_minutes는 **분·호라이즌** 합이라 분모를 넘을 수 있다 → 0.0 클램프."""
    from model.scaler_monitor_db import compute_ensemble_uptime as u
    assert u({"pipeline_minutes": 10, "const_out_minutes": 50}) == 0.0


def test_scaler_daily_has_health_columns():
    """마이그레이션이 실제로 컬럼을 붙이는가 (기존 DB 무손실)."""
    import sqlite3
    from config.settings import SCALER_MONITOR_DB
    from model.scaler_monitor_db import init_db, _HEALTH_COLS
    init_db()
    with sqlite3.connect(SCALER_MONITOR_DB, timeout=5) as c:
        cols = {r[1] for r in c.execute("PRAGMA table_info(scaler_daily)").fetchall()}
    missing = [n for n, _ in _HEALTH_COLS if n not in cols]
    assert not missing, "scaler_daily 건강도 컬럼 누락: %s" % missing


def test_health_snapshot_read_before_reset():
    """C5와 같은 함정 방지 — daily_close가 스냅샷을 **리셋 전에** 읽는가.

    소스 순서를 본다: insert_daily(health=...) 호출이
    _reset_model_health_counters() 보다 앞서야 한다.
    """
    src = open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()
    # [MW0601 482차] 인자 유무와 무관하게 잡는다. 종전에는 호출 전문
    # `health=self._model_health_snapshot()` 을 문자열로 찾아, 482차가 `cb3_avail=`
    # 인자를 추가하자 **불변식은 그대로인데 테스트만** 깨졌다. 여기서 지킬 것은
    # 호출 형태가 아니라 **순서**다.
    i_snap = src.find("health=self._model_health_snapshot(")
    i_reset = src.find("self._reset_model_health_counters()")
    assert i_snap != -1 and i_reset != -1, "G5 배선이 사라졌다"
    assert i_snap < i_reset, (
        "리셋이 스냅샷보다 먼저다 — 457차 C5(8거래일 연속 죽은 값)와 같은 사고가 난다")


def test_const_out_counted_before_cooldown_gate():
    """쿨다운에 막혀 재적합이 안 도는 분에도 제외 시간은 흘러간다.

    계측이 재적합 트리거 **앞**에 있어야 지속시간이 과소 집계되지 않는다.
    """
    src = open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()
    i_count = src.find("self._mh_pipeline_minutes += 1")
    i_gate = src.find("if _const_hz and not self._scaler_refresh_running")
    assert i_count != -1 and i_gate != -1, "G5 계측 지점이 사라졌다"
    assert i_count < i_gate, "계측이 쿨다운 분기 뒤에 있으면 제외 시간이 과소 집계된다"


# ── G4: 방향 편향 상시 감시 채널 ───────────────────────────────────────────

def test_g4_channel_conforms_to_safe_channel_contract():
    """generate_validation_campaign_report._safe_channel 규약 — compute/summarize."""
    import scripts.direction_bias_watch as m
    assert hasattr(m, "compute") and hasattr(m, "summarize")
    out = m.summarize(m.compute("2026-07-05"))
    assert "verdict" in out and "reason" in out
    assert out["verdict"] in (
        "ALERT_BIAS", "PASS", "INSUFFICIENT"), out["verdict"]


def test_g4_verdicts_render_not_as_insufficient():
    """ALERT_BIAS가 판정 맵에 없으면 조용히 INSUFFICIENT로 렌더돼 경보가 사라진다."""
    import scripts.generate_validation_campaign_report as R
    assert "ALERT_BIAS" in R._fmt_verdict("ALERT_BIAS")
    assert "BACKFILL_ADVISORY" in R._fmt_verdict("BACKFILL_ADVISORY")
    assert R._fmt_verdict("ALERT_BIAS") != R._fmt_verdict("__unknown__")


def test_g4_wired_into_report():
    src = open(os.path.join(_ROOT, "scripts",
                            "generate_validation_campaign_report.py"),
               encoding="utf-8").read()
    assert 'scripts.direction_bias_watch' in src, "[50] 채널이 build_report에 없다"
    assert '"direction_bias_watch": dbw' in src, "metrics에 채널이 안 실린다"
    assert "[50] 방향 편향 상시 감시" in src, "요약표 행이 없다"


def test_g4_reason_always_carries_reversal_note():
    """"뒤집으면 되지 않나"의 자동 반박 — 판정문에 역방향 적중률이 항상 실려야 한다.

    A1 실측: 반전 시 적중률이 오히려 떨어진다(3m 0.347→0.337). 이 문구가 빠지면
    다음 세션이 ALERT_BIAS를 보고 방향 반전을 처방할 위험이 생긴다.
    """
    import scripts.direction_bias_watch as m
    s = m.summarize(m.compute("2026-07-05"))
    if s["verdict"] == "INSUFFICIENT":
        pytest.skip("표본 미달 — 판정문에 역방향 주석이 없는 것이 정상")
    assert "역방향 적중" in s["reason"], s["reason"]


def test_g4_preregistered():
    from config.settings import VALIDATION_CAMPAIGN
    cfg = VALIDATION_CAMPAIGN.get("direction_bias_watch")
    assert cfg, "direction_bias_watch 사전등록이 사라졌다"
    for k in ("min_days", "t_threshold", "alert_min_horizons", "data_start"):
        assert k in cfg, "사전등록 키 누락: %s" % k
    assert cfg["alert_min_horizons"] >= 2, (
        "1개 호라이즌만으로 ALERT를 내면 단일 호라이즌 특이를 '체계적 편향'이라 부르게 된다")


# ── G7: 라우터 건강도 섀도 ─────────────────────────────────────────────────

def test_g7_table_exists():
    import sqlite3
    from config.settings import TRADES_DB
    from utils.db_utils import init_trades_db
    init_trades_db()
    with sqlite3.connect(TRADES_DB, timeout=5) as c:
        cols = {r[1] for r in
                c.execute("PRAGMA table_info(router_health_shadow)").fetchall()}
    for need in ("ts", "chosen_hz", "const_out_hz", "chosen_degraded",
                 "chosen_cv_null", "entry_executed"):
        assert need in cols, "router_health_shadow 컬럼 누락: %s" % need


def test_g7_is_shadow_only_no_policy_change():
    """**정책을 바꾸지 않는다**는 것이 이 항목의 핵심 제약이다.

    라우터 선택(`_entry_horizon = select_entry_horizon(...)`)과 ConstOut 목록 사이에
    어떤 필터링도 없어야 한다. 08-11 대조에서 ConstOut 구간 × 진입 시도 교집합이
    0건이라 효과가 미확인이고, 313차는 효과 미확인 상태의 정책 변경을 금지한다.
    """
    src = open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()
    m = re.search(r"_entry_horizon = select_entry_horizon\(([^)]*)\)", src)
    assert m, "라우터 호출부가 사라졌다"
    assert "const" not in m.group(1).lower(), (
        "라우터 입력에 ConstOut이 섞였다 — G7은 섀도 단계이며 정책 변경은 "
        "router_health_shadow 판정 + 주간회의 승인 이후다")


def test_g7_preregistered():
    from config.settings import VALIDATION_CAMPAIGN
    cfg = VALIDATION_CAMPAIGN.get("router_health_shadow")
    assert cfg, "router_health_shadow 사전등록이 사라졌다"
    assert cfg["degraded_rate_rejects"] < cfg["degraded_rate_supports"], (
        "REJECTS 문턱이 SUPPORTS보다 크면 두 판정이 동시에 성립한다")


# ── G9: 원인 태그는 관측 전용 ──────────────────────────────────────────────

def test_g9_cause_tag_does_not_affect_verdict():
    """원인 태그는 **로그 문자열에만** 쓰여야 한다.

    `_last_pipe_dominant`가 Degraded 판정식(streak/threshold 비교)에 들어가면
    관측이 정책으로 슬쩍 승격된다. 457차는 B1 배포 후 재평가하기로 했다.
    """
    src = open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()
    uses = [ln.strip() for ln in src.splitlines() if "_last_pipe_dominant" in ln]
    assert uses, "G9 배선이 사라졌다"
    for ln in uses:
        if ln.startswith("#") or "self._last_pipe_dominant = " in ln:
            continue
        assert "getattr(self, \"_last_pipe_dominant\"" in ln, (
            "예상 밖 사용처 — 판정식에 섞였는지 확인할 것: %s" % ln)
    # is_degraded 결정 라인에 원인 태그가 들어가 있지 않은지
    i = src.find("is_degraded = True")
    assert i != -1
    window = src[max(0, i - 400):i]
    assert "_last_pipe_dominant" not in window, (
        "Degraded 진입 판단 직전에 원인 태그가 쓰였다 — 관측 전용 제약 위반")


# ── G6: 흡수 사실 고정 ─────────────────────────────────────────────────────

def test_g6_absorbed_into_a3_not_duplicated():
    """G6는 A3(cost_edge_watch)로 흡수됐다 — 별도 채널을 만들지 않는다."""
    from config.settings import VALIDATION_CAMPAIGN
    assert "cost_edge_watch" in VALIDATION_CAMPAIGN
    assert "cost_edge_gate" not in VALIDATION_CAMPAIGN, (
        "G6를 별도 채널로 다시 만들었다 — A3와 중복이고 소급 실측은 "
        "quantile_expected_pt의 예측력을 기각하는 방향이다(rho=0.156, 격차 -2.4%p)")
