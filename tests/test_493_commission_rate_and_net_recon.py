# -*- coding: utf-8 -*-
"""[MW0601 493차 / F-1~F-5] 수수료율 세대 분리 · net 축 대사 · 판정 원천.

왜 필요한가
-----------
2026-05-11 브로커를 키움 → Cybos로 바꾸면서 `FUTURES_COMMISSION_RATE`가 키움
값(편도 0.0015%)으로 남았다. 실제는 0.00981% — **6.54배**다. 엔진 net 손익이
6개월간 낙관 편향됐고, 실전 전환 기준 ①의 4주 창(2026-07-28~08-25) 통산 판정이
**+1,087,364원(양수) → −414,198원(음수)** 으로 뒤집힐 규모였다.

**왜 안 잡혔나가 핵심이다.** 477차 EOD 대사는 CpTd6197 실현손익이 gross라서
`broker gross vs engine gross`만 비교했다 — 수수료는 엔진 가정이 그대로 net이
되어 어떤 대조도 받지 않는 사각지대였다(계측 4원칙 ④). 정답지(예탁현금·
익일가예탁현금)는 매분 수신·기록되고 있었는데 아무도 안 봤다.

이 테스트가 고정하는 불변식:
① 라이브 요율은 실측값이고, 구 요율은 **별도 상수**로만 존재한다(소급 판별용).
② 비용모델 요율은 라이브와 **분리**돼 있다 — 핀 해제는 주간회의 승인 사항이라
   상수 하나 바꿔서 캠페인 verdict가 조용히 이동하면 안 된다(461차 mdd_pct 유형).
③ `normalize_trade_pnl`은 **어떤 요율로 계산했는지 행에 남긴다**(계측 4원칙 ④).
④ net 축 대사가 gross 일치·net 불일치를 실제로 잡아낸다 — 이 결함의 지문이다.
⑤ 판정 원천은 브로커 net 우선이고, 폴백은 **플래그로 드러난다**(4원칙 ②).
⑥ 비용모델 소비처가 라이브 요율을 직접 import하지 않는다(핀 누수 방지).
"""
import io
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings  # noqa: E402
from utils import db_utils  # noqa: E402


BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ✅ [2026-08-26 후속8 → 495차 후속 체리픽] **CYBOS 채널 고시로 확정.**
#   대신증권 CYBOS 사이버 트레이딩 「KOSPI200 선물 거래금액에 관계없이 0.0098104%」
#   (사용자 확인). 후속5의 39거래일 역산치 0.0098103% 와 5자리 일치 — 독립 확인.
#   (역산 근거: 약정대금 447.3억원, R²=1.000000, 최대 잔차 13.9원, 고정비 ≈0.
#    전체 45일 중 6일은 오염일 제외. `--verify` 로 언제든 재현된다.)
#
# 🔴 **요율은 「로그인 채널」이 정한다** — 495차가 찾아낸 축이다.
#   CYBOS 사이버(이 PC=MW0601) 0.0098104% / CREON 트레이딩(MW0602) 0.0019%,
#   **5.16배 차이**. 두 PC의 역산이 각자의 고시와 일치했다.
#   ⇒ 아래는 **이 PC에서 감지될 채널(CYBOS)의 값**을 고정한다. 채널 감지·매핑
#     자체는 `tests/test_495_broker_channel_rate.py` 가 검증한다.
MEASURED_ONE_WAY_RATE = 0.000098104


# ── ① 요율 세대 분리 ────────────────────────────────────────────────────────
def test_live_rate_is_measured_not_kiwoom_legacy():
    """라이브 요율이 실측값이어야 한다. 구 키움 값으로 되돌아가면 실패한다."""
    assert settings.FUTURES_COMMISSION_RATE == pytest.approx(MEASURED_ONE_WAY_RATE, rel=1e-9), (
        "라이브 수수료율이 공식 고시(0.0098104%)와 다르다. 되돌렸다면 브로커 net 대사가 "
        "매일 MISMATCH를 낸다 — scripts/commission_rate_recon.py --verify 로 확인할 것"
    )


def test_legacy_rate_kept_separately_for_generation_lookup():
    """구 요율은 지우지 말고 **별도 상수로** 남긴다.

    과거 trades 행의 commission_krw가 이 값으로 계산돼 있어, 소급 재계산과
    "이 net은 어느 세대인가" 판별에 필요하다. 상수를 덮어썼다면 그 정보가 사라진다.
    """
    assert settings.FUTURES_COMMISSION_RATE_LEGACY_KIWOOM == pytest.approx(0.000015)
    assert settings.FUTURES_COMMISSION_RATE != settings.FUTURES_COMMISSION_RATE_LEGACY_KIWOOM
    assert re.match(r"^\d{4}-\d{2}-\d{2}$", settings.FUTURES_COMMISSION_RATE_EFFECTIVE_FROM), (
        "불연속 경계 날짜가 있어야 앞뒤 시계열을 섞어 비교하는 사고를 막을 수 있다"
    )


# ── ② 비용모델 핀 분리 ──────────────────────────────────────────────────────
def test_cost_model_rate_is_separate_symbol():
    """비용모델 요율은 라이브와 **다른 이름**이어야 한다.

    같은 상수를 공유하면 라이브 재보정이 사전등록 채널의 측정값을 조용히
    재정의한다(합격선은 그대로인데 verdict가 뒤집힌다).
    """
    assert hasattr(settings, "COST_MODEL_COMMISSION_RATE")
    assert hasattr(settings, "COST_MODEL_COMMISSION_RATE_PINNED")


def test_pinned_flag_agrees_with_actual_value():
    """핀 플래그와 실제 값이 어긋나면 배너가 거짓말을 한다.

    PINNED=True인데 값이 라이브와 같으면 "과소 6.54배" 경고가 헛돈다.
    PINNED=False인데 값이 다르면 승인 없이 핀이 유지된 채 경고만 사라진다.
    """
    same = (settings.COST_MODEL_COMMISSION_RATE
            == pytest.approx(settings.FUTURES_COMMISSION_RATE, rel=1e-9))
    if settings.COST_MODEL_COMMISSION_RATE_PINNED:
        assert not same, "PINNED=True인데 라이브와 같다 — 핀 해제했으면 플래그도 False로"
    else:
        assert same, "PINNED=False인데 라이브와 다르다 — 승인 없는 핀 유지"


#: 비용차감 판정을 내는 채널들. 여기 있는 파일의 **비용 계산식**은 반드시
#: 핀된 요율을 써야 한다. (표시·배너 목적의 참조는 허용 — 오히려 권장이다.)
_COST_CONSUMERS = [
    "scripts/atb_v2_build_and_eval.py",
    "scripts/cost_edge_shadow.py",
    "scripts/generate_validation_campaign_report.py",
    "scripts/horizon_signal_tradability.py",
    "scripts/profit_guard_latch_watch.py",
    "scripts/tp1_protect_offset_shadow.py",
]

#: 산술에 쓰였는가 — 요율 좌우에 곱셈이 붙은 형태만 비용 계산으로 본다.
#: 배너의 `% (..., FUTURES_COMMISSION_RATE))` 같은 포맷 인자는 걸리지 않는다.
_ARITHMETIC_USE = re.compile(
    r"(\*\s*FUTURES_COMMISSION_RATE\b|\bFUTURES_COMMISSION_RATE\s*\*)")


def _code_lines(path):
    """주석을 걷어낸 코드 줄. 설명문에 이름이 나오는 것은 정상이라 제외한다."""
    src = io.open(path, encoding="utf-8").read()
    return [ln.split("#", 1)[0] for ln in src.splitlines()]


def test_cost_formulas_do_not_use_live_rate():
    """[핀 누수 방지] 비용차감 채널의 **계산식**이 라이브 요율을 쓰면 안 된다.

    하나라도 라이브를 쓰면 그 채널만 새 비용으로 판정돼 리포트 안에서 기준이
    섞인다 — 배너는 "핀됨"이라 말하는데 일부 수치는 아닌 상태가 된다.

    ⚠ import·배너 표시는 막지 않는다. 리포트는 오히려 라이브 요율을 읽어
      "실제 대비 몇 배 과소인지"를 매주 찍어야 한다(핀을 조용히 두지 않기 위함).
    """
    offenders = []
    for rel in _COST_CONSUMERS:
        path = os.path.join(BASE, rel)
        if not os.path.exists(path):
            continue
        for i, ln in enumerate(_code_lines(path), 1):
            if _ARITHMETIC_USE.search(ln):
                offenders.append("%s:%d" % (rel, i))
    assert not offenders, (
        "비용 계산식이 라이브 요율을 쓴다 — COST_MODEL_COMMISSION_RATE로 바꿀 것: %s"
        % offenders)


def test_cost_formulas_actually_use_pinned_rate():
    """반대 방향 — 계산식이 핀된 요율을 **쓰고는 있는지**.

    위 테스트만 있으면 상수를 통째로 지워도 통과한다(공허한 참).
    """
    missing = []
    for rel in _COST_CONSUMERS:
        path = os.path.join(BASE, rel)
        if not os.path.exists(path):
            continue
        code = "\n".join(_code_lines(path))
        if not re.search(r"(\*\s*COST_MODEL_COMMISSION_RATE\b"
                         r"|\bCOST_MODEL_COMMISSION_RATE\s*\*)", code):
            missing.append(rel)
    assert not missing, "핀된 요율을 쓰는 비용 계산식이 사라졌다: %s" % missing


def test_report_banner_surfaces_the_pin():
    """핀 상태를 매주 리포트가 **말해야** 한다.

    말없는 핀은 이 시스템이 반복해서 당한 실패다(FP-CRITICAL 죽은 게이트,
    TOX 죽은 섀도). 배너가 없으면 읽는 사람이 "실제 비용으로 판정됐다"고 오해한다.
    """
    path = os.path.join(BASE, "scripts/generate_validation_campaign_report.py")
    src = io.open(path, encoding="utf-8").read()
    assert "COST_MODEL_COMMISSION_RATE_PINNED" in src
    assert "commission_rate_recon.py --impact" in src, (
        "배너가 영향 확인 경로를 안내해야 한다"
    )


# ── ③ 요율을 행에 남긴다 ────────────────────────────────────────────────────
def test_normalize_records_rate_used():
    m = db_utils.normalize_trade_pnl(entry_price=1040.0, quantity=1,
                                     pnl_pts=1.0, pt_value=50000)
    assert "commission_rate_used" in m, "어떤 가정으로 계산했는지 행에 남아야 한다"
    assert m["commission_rate_used"] == pytest.approx(settings.FUTURES_COMMISSION_RATE)


def test_normalize_honors_explicit_rate_for_historical_rows():
    """과거 행은 **그 행이 쓴 요율로** 재계산돼야 한다.

    라이브 요율로 덮으면 formula_version을 올리는 순간 과거 전 구간의 수수료가
    조용히 신 요율로 바뀐다 — 소급 정정은 명시 도구의 일이지 기동 부수효과가
    아니다.
    """
    legacy = db_utils.normalize_trade_pnl(
        entry_price=1040.0, quantity=1, pnl_pts=1.0, pt_value=50000,
        commission_rate=settings.FUTURES_COMMISSION_RATE_LEGACY_KIWOOM)
    live = db_utils.normalize_trade_pnl(
        entry_price=1040.0, quantity=1, pnl_pts=1.0, pt_value=50000)
    assert legacy["commission_rate_used"] == pytest.approx(
        settings.FUTURES_COMMISSION_RATE_LEGACY_KIWOOM)
    assert legacy["commission_krw"] < live["commission_krw"]
    # 6.54배 관계가 수수료에도 그대로 반영돼야 한다.
    assert live["commission_krw"] / legacy["commission_krw"] == pytest.approx(6.54, abs=0.05)


def test_trades_table_has_rate_column():
    """행별 요율 컬럼이 실제 스키마에 있어야 한다(마이그레이션 회귀 방지)."""
    import sqlite3
    db_utils.init_all() if hasattr(db_utils, "init_all") else None
    con = sqlite3.connect(settings.TRADES_DB)
    try:
        cols = {r[1] for r in con.execute("PRAGMA table_info(trades)")}
    finally:
        con.close()
    if not cols:
        pytest.skip("trades 테이블 미생성 환경")
    assert "commission_rate_used" in cols


# ── ④ net 축 대사 ───────────────────────────────────────────────────────────
class _FakeBroker(object):
    """fetch_broker_net 대역 — DB 없이 대사 로직만 고정한다."""

    def __init__(self, gross, net):
        self.gross, self.net = gross, net

    def __call__(self, date):
        if self.gross is None:
            return None
        return {"gross_krw": self.gross, "net_krw": self.net,
                "commission_krw": self.gross - self.net,
                "deposit_cash_krw": 0.0, "next_day_deposit_cash_krw": 0.0,
                "engine_commission_krw": None, "engine_net_krw": None}


def test_recon_catches_the_exact_2026_08_25_defect(monkeypatch):
    """이 결함의 지문 — **gross는 일치하는데 net만 어긋난다**.

    2026-08-25 실측: gross 39,000 양쪽 동일 / 엔진 net +32,765 vs 브로커 −1,782.
    종전 gross 대사는 "일치"라고 답했다. net 대사는 잡아야 한다.
    """
    monkeypatch.setattr(db_utils, "fetch_broker_net", _FakeBroker(39000.0, -1782.0))
    r = db_utils.reconcile_daily_net("2026-08-25", 39000.0, 6235.0, 32765.0)
    assert r["status"] == "MISMATCH"
    assert r["broker_gross"] == r["engine_gross"], "gross는 일치한다 — 그래서 못 잡았던 것"
    assert r["residual"] == pytest.approx(34547.0)
    assert r["commission_ratio"] == pytest.approx(6.54, abs=0.02), (
        "수수료 배수가 원인을 바로 가리켜야 한다"
    )


def test_recon_passes_under_corrected_rate(monkeypatch):
    """요율을 고치면 같은 날이 OK가 된다 — 대사가 요율에 반응한다는 확인."""
    monkeypatch.setattr(db_utils, "fetch_broker_net", _FakeBroker(39000.0, -1782.0))
    r = db_utils.reconcile_daily_net("2026-08-25", 39000.0, 40782.0, -1782.0)
    assert r["status"] == "OK"
    assert r["residual"] == pytest.approx(0.0, abs=1.0)


def test_recon_distinguishes_missing_from_zero(monkeypatch):
    """브로커 값이 없으면 '차이 0'이 아니라 '측정 불가'다(계측 4원칙 ②)."""
    monkeypatch.setattr(db_utils, "fetch_broker_net", _FakeBroker(None, None))
    r = db_utils.reconcile_daily_net("2026-08-25", 39000.0, 6235.0, 32765.0)
    assert r["status"] == "NO_BROKER"
    assert "residual" not in r, "미측정인데 잔차를 만들어내면 0으로 오독된다"


def test_recon_tolerance_ignores_rounding_noise(monkeypatch):
    """체결가 반올림 수준(실측 최대 1.5원)에는 경보가 뜨지 않아야 한다."""
    monkeypatch.setattr(db_utils, "fetch_broker_net", _FakeBroker(39000.0, -1782.0))
    r = db_utils.reconcile_daily_net("2026-08-25", 39000.0, 40780.0, -1780.0)
    assert r["status"] == "OK"


# ── ⑤ 판정 원천 ─────────────────────────────────────────────────────────────
def test_verdict_source_prefers_broker_and_flags_fallback():
    """실전 전환 기준 ①의 원천은 브로커 net이고, 폴백은 드러나야 한다."""
    rows = db_utils.fetch_daily_net_for_verdict(400)
    if not rows:
        pytest.skip("daily_broker_pnl 표본 없음")
    for date, v in rows.items():
        assert v["source"] in ("broker", "engine")
        assert "net_krw" in v
    # 브로커 실측이 있는 날은 반드시 broker로 잡혀야 한다.
    sample = next((d for d, v in rows.items() if v["source"] == "broker"), None)
    if sample:
        b = db_utils.fetch_broker_net(sample)
        assert b is not None
        assert rows[sample]["net_krw"] == pytest.approx(b["net_krw"])


def test_verdict_net_is_not_broker_gross():
    """판정 원천이 gross로 되돌아가면 실패한다.

    종전 손익 추이 탭은 브로커 **gross**와 엔진 **net**을 섞어 더했다
    (계측 4원칙 ① 단위 혼합). 두 갈래 모두 net이어야 한다.
    """
    nv = db_utils.fetch_daily_net_for_verdict(400)
    gm = db_utils.fetch_broker_daily_pnl_map(400)
    shared = [d for d in nv if d in gm and nv[d]["source"] == "broker"]
    if not shared:
        pytest.skip("대조 표본 없음")
    # 수수료가 0인 날(거래 없음)을 빼면 반드시 달라야 한다.
    traded = [d for d in shared if abs(nv[d].get("commission_krw", 0.0)) > 1.0]
    if not traded:
        pytest.skip("거래일 표본 없음")
    assert any(abs(nv[d]["net_krw"] - gm[d]) > 1.0 for d in traded), (
        "판정 net이 브로커 gross와 같다 — 수수료가 차감되지 않았다"
    )


# ── ⑥ P&L 패널 이중표기 (F-5) ───────────────────────────────────────────────
# ⚠ QApplication 생성보다 **먼저** offscreen을 세운다(test_dashboard_smoke 관례).
os.environ["MIREUK_TEST_MODE"] = "1"
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def _daily_tile(**kw):
    """LogPanel의 '일일 누적' 타일을 갱신하고 (텍스트, 색)을 돌려준다."""
    pytest.importorskip("PyQt5")
    from PyQt5.QtWidgets import QApplication
    from dashboard.main_dashboard import LogPanel
    app = QApplication.instance() or QApplication([])
    assert app is not None
    panel = LogPanel()
    engine = kw.pop("engine")
    panel.update_pnl_metrics(0.0, engine, 0.0,
                             forward_daily_pnl_krw=engine, **kw)
    lbl = panel._pnl_vals["daily"]
    return lbl.text(), lbl.styleSheet()


def test_panel_falls_back_to_single_line_when_broker_missing():
    """브로커 값이 없으면 종전 표시 그대로 — 0을 지어내지 않는다(계측 4원칙 ②)."""
    text, _ = _daily_tile(engine=32765.0)
    assert "브로커" not in text
    assert "실행" in text


def test_panel_shows_both_and_residual():
    """2026-08-25 실제 상황 — 엔진 +32,765 / 브로커 −1,782 / 차 +34,547."""
    text, style = _daily_tile(engine=32765.0, broker_net_krw=-1782.0)
    assert "엔진 +32,765원" in text
    assert "브로커 -1,782원" in text
    assert "+34,547" in text


def test_mismatch_is_distinguishable_from_a_losing_day():
    """🔴 대사 실패 신호가 **손실 색과 달라야** 한다.

    적색을 재사용하면 손실 나는 날에는 대사 실패가 아예 안 보인다(구현 중 실측).
    대사 실패는 손익 부호와 무관한 별개 차원이므로 색·마커 모두 분리한다.
    """
    bad_text, bad_style = _daily_tile(engine=-500000.0, broker_net_krw=-1782.0)
    ok_text, ok_style = _daily_tile(engine=-414198.0, broker_net_krw=-414198.0)
    assert "⚠" in bad_text, "대사 실패는 색맹·흑백에서도 읽히는 마커가 있어야 한다"
    assert "⚠" not in ok_text
    assert bad_style != ok_style, "손실인 두 날의 대사 성패가 같은 색이면 구분 불가"


def test_matching_day_keeps_pnl_color_semantics():
    """대사가 맞으면 색은 손익 의미 그대로다(이익=녹 / 손실=적)."""
    win_text, win_style = _daily_tile(engine=50000.0, broker_net_krw=50000.0)
    loss_text, loss_style = _daily_tile(engine=-50000.0, broker_net_krw=-50000.0)
    assert "⚠" not in win_text and "⚠" not in loss_text
    assert win_style != loss_style
