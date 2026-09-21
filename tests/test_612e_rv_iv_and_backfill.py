# tests/test_612e_rv_iv_and_backfill.py
"""[MW0601 612차 후속6] RV-IV 카드 정정 + GEX 소급 정정 검증.

## RV-IV — 부호로 「과대/과소평가」를 읽으면 안 된다

종전 색 규칙은 `spread > 0 → 초록(시장이 변동성 과소평가)` 이었다. 그런데
2026-09-01~09-21 `raw_features` 실측에서 **ready 표본 5,433건 중 양수가 193건
(3.55%)** 이고, 일별 중앙값이 −18.8 ~ −29.6 으로 **양수인 날이 하루도 없다**
(RV 중앙 13~26 vs IV 중앙 39~50).

시장 신호가 아니라 **기간축 불일치의 산물**이다 —
RV 는 1분봉 30개(=30분) 실현변동성이고 IV(VKOSPI)는 30일 내재변동성이다.
⇒ 절대 부호 색을 걷어내고 **그날 자기 분포 대비**로 칠한다(감마 배지와 같은 처방).
"""
from __future__ import annotations

import os

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DASH = os.path.join(_ROOT, "dashboard", "main_dashboard.py")
_BF = os.path.join(_ROOT, "scripts", "gex_scale_backfill_612.py")


def _src(p):
    with open(p, "r", encoding="utf-8") as f:
        return f.read()


# ── RV-IV ─────────────────────────────────────────────────────────────────

def test_1_absolute_sign_coloring_is_gone():
    body = _src(_DASH).split("def update_rv_iv", 1)[1].split("\n    def ", 1)[0]
    assert "C['green'] if spread > 0" not in body, (
        "절대 부호 색이 되살아났다 — 실측상 양수가 3.55% 뿐이라 항상 빨강이 된다"
    )
    assert "_rviv_day_spreads" in body, "당일 분포 기준이 없다"


def test_2_card_labels_state_the_horizon_mismatch():
    src = _src(_DASH)
    assert "30분·연율화 %" in src, "RV 의 기간(30분)이 화면에 없다"
    assert "30일·KRX 지수" in src, "IV 의 기간(30일)이 화면에 없다"
    assert "기간축 다름 — 상시 음수" in src, (
        "스프레드가 상시 음수라는 사실이 화면에 없다 — 부호를 신호로 오독한다"
    )


def test_3_day_buffer_is_explicitly_initialised():
    """계측 4원칙 ④ — 런타임 상태를 기본값 폴백으로 읽지 않는다."""
    from dashboard.main_dashboard import DivergencePanel

    assert hasattr(DivergencePanel, "_rviv_day")
    assert hasattr(DivergencePanel, "_rviv_day_spreads")
    body = _src(_DASH).split("def update_rv_iv", 1)[1].split("\n    def ", 1)[0]
    assert "self._rviv_day != _today" in body, "거래일이 바뀌어도 버퍼가 안 비워진다"


def test_4_relative_rule_separates_widen_from_narrow():
    """산식 재현 — 같은 음수라도 그날 중앙값 대비로 갈려야 한다."""
    def color(spread, day):
        if len(day) < 10:
            return "muted"
        med = sorted(day)[len(day) // 2]
        return "green" if spread > med else ("red" if spread < med else "muted")

    day = [-31.2, -30.1, -29.8, -29.5, -28.9, -30.4, -29.1, -28.2, -30.9, -29.6]
    assert color(-22.0, day) == "green", "좁혀졌는데 빨강"
    assert color(-35.0, day) == "red", "벌어졌는데 초록"
    # 표본 부족이면 색을 칠하지 않는다
    assert color(-30.0, day[:5]) == "muted"
    # ⚠ 절대 부호로는 둘이 구분되지 않는다 — 그게 이 정정의 이유다
    assert (-22.0 < 0) and (-35.0 < 0)


# ── GEX 소급 정정 ─────────────────────────────────────────────────────────

def test_5_backfill_marker_uses_the_real_schema():
    """`strategy_events` 는 (version,event_type,event_at,message,note) 다.

    처음엔 `ts/detail` 로 짐작해 썼다가 `--apply` 에서 **마커만 조용히 실패**했다
    (정정 자체는 성공). 스키마를 짐작하지 말 것 — 마커 없는 불연속이 461차 사고다.
    """
    src = _src(_BF)
    assert "INSERT INTO strategy_events(version, event_type, event_at, message, note)" in src
    assert "ts, event_type, detail" not in src


def test_6_backfill_cutoff_is_the_measured_transition():
    """컷오프는 짐작이 아니라 실측 전환점이어야 한다 (GEX 291.32B → 3.19B)."""
    src = _src(_BF)
    assert 'FIX_DEPLOYED_AT = "2026-09-21 14:32:00"' in src
    assert "14:31:18" in src, "전환점 근거가 주석에 없다"


def test_7_backfill_touches_only_the_gex_key():
    import importlib.util

    spec = importlib.util.spec_from_file_location("_bf612e", _BF)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    assert m.KEY == "opt_gex_bn" and m.FACTOR == 100.0
    row = {"opt_gex_bn": 291.32, "opt_gex_sign": 1.0, "opt_chain_pcr": 0.368}
    fixed = dict(row)
    fixed[m.KEY] = round(float(fixed[m.KEY]) / m.FACTOR, 6)
    assert abs(fixed["opt_gex_bn"] - 2.9132) < 1e-9
    assert fixed["opt_gex_sign"] == 1.0 and fixed["opt_chain_pcr"] == 0.368
