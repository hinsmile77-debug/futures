# -*- coding: utf-8 -*-
"""[MW0601 493차 후속8] 미니선물 계약 사양이 P&L 전 경로에 반영됐는가.

왜 필요한가
-----------
미륵이가 매매하는 종목은 **미니선물 A0569 (승수 50,000 · 틱 0.02pt)** 다.
그런데 손익을 만드는 코드 여러 곳이 **정규선물 250,000** 을 쓰고 있었다:

  · `strategy/shadow_evaluator.py`  — `_FUTURES_MULTIPLIER = 250_000` **하드코딩**
  · `backtest/transaction_cost.py`  — `FUTURES_MULTIPLIER` + 키움 세대 요율 모델
  · `backtest/slippage_simulator.py`— `FUTURES_MULTIPLIER`
  · `utils/db_utils.py`             — 해석 실패 시 **조용히** 250,000 폴백

⇒ 그 경로들의 손익·비용은 **5배 과대**였다. 라이브 주문 경로가 아니라 실손해는
  없었지만 섀도 전략 비교·백테스트 비용이 그 위에 있었다.

⇒ 이 결함은 개발 중에도 재현됐다 — `scripts/commission_rate_recon.py` 초판이
  `FUTURES_PT_VALUE` 를 써서 약정대금이 정확히 5배가 되고 요율이 1/5로 나왔다.
  **같은 실수가 세 번째다.** 그래서 테스트로 고정한다.

고정하는 불변식:
① 수수료율은 **브로커 공식 고시값**이고 출처가 설정에 기록돼 있다.
② 승수의 원천은 **하나**다 — 종목코드(`get_contract_spec`). 설정이 승수를 재정의하지 않는다.
③ 손익·비용을 만드는 모듈이 **정규선물 승수를 직접 import 하지 않는다.**
④ 폴백이 쓰이면 **드러난다**(조용한 5배 오차 금지).
"""
import io
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings as S  # noqa: E402
from config.constants import (  # noqa: E402
    FUTURES_PT_VALUE, MINI_FUTURES_PT_VALUE, get_contract_spec,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: ✅ [MW0602 495차 후속] 대신증권 **CREON 트레이딩** 고시 (2026-08-26 사용자 확인).
#: KOSPI200/미니 선물 0.0019% — 33거래일 역산(0.0018999%, R²=1.000000)과 일치.
#: MW0601(CYBOS 사이버 트레이딩)은 0.0098104% — 요율은 **로그인 채널**이 정한다.
#: 채널 감지·매핑은 tests/test_495_broker_channel_rate.py가 검증한다.
OFFICIAL_ONE_WAY_RATE = 0.000019


# ── ① 요율 (MW0602 실측) ────────────────────────────────────────────────────
def test_commission_rate_is_the_published_rate():
    assert S.FUTURES_COMMISSION_RATE == pytest.approx(OFFICIAL_ONE_WAY_RATE, rel=1e-12)


def test_measured_and_published_agree():
    """33거래일 역산치(0.0018999%)와 채택 상수가 일치하는가 — 독립 확인의 기록.

    둘이 어긋나면 어느 한쪽이 낡은 것이다. 0.01% 이내면 같은 값으로 본다.
    """
    measured = 0.000018999
    assert abs(S.FUTURES_COMMISSION_RATE / measured - 1.0) < 1e-4


def test_fee_source_is_recorded():
    """요율만 있고 **출처가 없으면** 다음 브로커 전환 때 또 못 갱신한다."""
    assert getattr(S, "BROKER_FEE_SOURCE", ""), "수수료 출처 표기가 없다"
    assert re.match(r"^\d{4}-\d{2}-\d{2}$", getattr(S, "BROKER_FEE_VERIFIED_ON", "")), \
        "확인 날짜가 없다 — 언제 기준 값인지 알 수 없다"


def test_margin_rates_present_but_advisory():
    """증거금률은 참고치로만 둔다 — 주문 차단에 쓰면 브로커 판정과 이중이 된다."""
    assert S.FUTURES_MARGIN_RATE_INITIAL == pytest.approx(0.21)
    assert S.FUTURES_MARGIN_RATE_MAINTENANCE == pytest.approx(0.14)
    assert S.FUTURES_MARGIN_RATE_TOTAL_RISK_SIM == pytest.approx(0.0375)
    assert S.FUTURES_MARGIN_RATE_MAINTENANCE < S.FUTURES_MARGIN_RATE_INITIAL


def test_session_spec_matches_krx():
    assert S.MARKET_SESSION_SPEC["regular_open"] == "08:30"
    assert S.MARKET_SESSION_SPEC["regular_close"] == "15:45"
    assert S.MARKET_SESSION_SPEC["final_trading_day_close"] == "15:20"


# ── ② 승수 단일 원천 ────────────────────────────────────────────────────────
def test_active_contract_is_mini():
    spec = S.active_contract_spec()
    assert spec is not None, "ui_prefs.json 에서 활성 종목을 못 읽는다"
    assert spec["pt_value"] == MINI_FUTURES_PT_VALUE == 50_000
    assert spec["tick_size"] == pytest.approx(0.02)
    assert spec["label"] == "미니선물"


def test_settings_does_not_redefine_multiplier():
    """설정이 승수를 또 정의하면 **원천이 둘**이 되어 어긋날 때 판별 불가다."""
    src = io.open(os.path.join(ROOT, "config", "settings.py"), encoding="utf-8").read()
    code = "\n".join(ln.split("#", 1)[0] for ln in src.splitlines())
    assert not re.search(r"^\s*(FUTURES_)?PT_VALUE\s*=", code, re.M), \
        "settings.py 가 승수를 재정의한다 — constants.get_contract_spec() 이 단일 원천이다"


def test_tick_size_is_mini():
    assert S.TICK_SIZE == pytest.approx(0.02), "TICK_SIZE 가 정규선물(0.05)로 되돌아갔다"


def test_contract_spec_routing():
    assert get_contract_spec("A0569000")["pt_value"] == 50_000
    assert get_contract_spec("A01N3000")["pt_value"] == 250_000


# ── ③ 손익 모듈이 정규선물 승수를 직접 쓰지 않는가 ──────────────────────────
#: 손익·비용을 만드는 모듈. 여기서 250,000 을 쓰면 미니 손익이 5배가 된다.
_PNL_MODULES = [
    "strategy/shadow_evaluator.py",
    "backtest/transaction_cost.py",
    "backtest/slippage_simulator.py",
]


def _code_of(rel):
    """주석을 걷어낸 소스(문자열 검사용)."""
    src = io.open(os.path.join(ROOT, rel), encoding="utf-8").read()
    return "\n".join(ln.split("#", 1)[0] for ln in src.splitlines())


def _identifiers_used(rel):
    """모듈이 **실제로 참조하는** 이름 집합 — AST 기준.

    ⚠ 텍스트 검색으로 하면 **독스트링의 설명 문구까지 잡는다**(개발 중 실제로
    밟았다). "왜 이 상수를 쓰면 안 되는가"를 적은 문장이 위반으로 판정되면
    문서를 지우게 되는데, 그건 정확히 반대 방향이다.
    """
    import ast
    tree = ast.parse(io.open(os.path.join(ROOT, rel), encoding="utf-8").read())
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for a in node.names:
                names.add(a.name)
    return names


def _numeric_literals(rel):
    """모듈이 실제 계산에 쓰는 숫자 리터럴 — 독스트링 숫자는 잡히지 않는다."""
    import ast
    tree = ast.parse(io.open(os.path.join(ROOT, rel), encoding="utf-8").read())
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Num):
            out.append(node.n)
        elif isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            out.append(node.value)
    return out


@pytest.mark.parametrize("rel", _PNL_MODULES)
def test_pnl_modules_do_not_hardcode_regular_multiplier(rel):
    """🔴 `250_000` / `250000` 리터럴이 손익 계산에 박혀 있으면 실패한다."""
    hits = [v for v in _numeric_literals(rel) if v == 250_000]
    assert not hits, (
        "%s 의 **코드**에 정규선물 승수 250,000 이 박혀 있다(%d개) — 미니 손익이 "
        "5배가 된다. config.settings.active_contract_spec() 을 쓸 것" % (rel, len(hits)))


@pytest.mark.parametrize("rel", _PNL_MODULES)
def test_pnl_modules_do_not_import_regular_multiplier(rel):
    used = _identifiers_used(rel)
    assert "FUTURES_MULTIPLIER" not in used, (
        "%s 가 FUTURES_MULTIPLIER(정규선물 250,000)를 실제로 참조한다" % rel)
    assert "FUTURES_PT_VALUE" not in used, (
        "%s 가 FUTURES_PT_VALUE(정규선물)를 실제로 참조한다 — 활성 계약으로 해석할 것" % rel)


def test_shadow_evaluator_resolves_to_mini():
    import strategy.shadow_evaluator as SE
    assert SE._FUTURES_MULTIPLIER == pytest.approx(50_000.0), (
        "섀도 평가기 승수가 미니가 아니다 — 섀도 손익이 5배 과대였던 그 결함")


def test_backtest_cost_uses_published_rate():
    """백테스트 비용이 키움 세대 모델(720원 + 0.015bp)로 되돌아가지 않았는가."""
    import backtest.transaction_cost as T
    assert T._pt_value() == pytest.approx(50_000.0)
    assert T.KRX_FEE_PER_CONTRACT == 0, "고시 요율에 정액 성분이 없음이 실측 확인됐다"
    assert T.BROKERAGE_RATE_DEFAULT == pytest.approx(OFFICIAL_ONE_WAY_RATE)


def test_backtest_slippage_uses_mini():
    import backtest.slippage_simulator as SL
    assert SL._pt_value() == pytest.approx(50_000.0)


# ── ④ 폴백 가시화 ───────────────────────────────────────────────────────────
def test_pt_value_fallback_is_logged(monkeypatch):
    """해석 실패 시 **조용히** 250,000 으로 떨어지지 않는가(계측 4원칙 ④).

    ⚠ `caplog` 를 쓰지 않는다. `SYSTEM` 로거는 다른 테스트(`test_log_isolation`)가
    핸들러·propagate 를 재구성하므로 단독 실행은 통과하고 **전체 실행에서만
    깨진다**(개발 중 실제로 밟았다 — F-V 때와 같은 함정). 로거를 직접 가로채면
    로깅 설정과 무관하게 「경고가 실제로 나갔는가」만 본다.
    """
    import logging
    import utils.db_utils as D

    calls = []
    real_get = logging.getLogger

    class _Spy(object):
        def warning(self, msg, *a, **k):
            calls.append(msg % a if a else msg)

        def __getattr__(self, name):
            return lambda *a, **k: None

    monkeypatch.setattr(
        D.logging, "getLogger",
        lambda name=None: _Spy() if name == "SYSTEM" else real_get(name))
    monkeypatch.setattr(D, "DATA_DIR", os.path.join(ROOT, "no_such_dir_for_test"))
    val = D._get_pt_value_from_prefs()

    assert val == FUTURES_PT_VALUE, "폴백 값 자체는 하위호환으로 유지한다"
    assert any("PtValueFallback" in str(m) for m in calls), (
        "폴백이 쓰였는데 로그가 없다 — 5배 오차가 조용히 흐른다")


def test_shadow_evaluator_fallback_prefers_mini():
    """섀도 평가기는 해석 실패 시에도 **정규선물로 떨어지지 않는다.**

    이 저장소의 두 PC 모두 미니선물이므로, 실패 시 미니가 덜 틀린다.
    """
    src = _code_of("strategy/shadow_evaluator.py")
    assert "MINI_FUTURES_PT_VALUE" in src
    assert "logger.warning" in src, "폴백을 조용히 쓰면 안 된다"


# ── 실제 계산이 맞는가 ──────────────────────────────────────────────────────
def test_round_trip_cost_matches_reality():
    """미니 1계약 @1040pt 왕복 수수료가 MW0602 실측 규모(약 1,980원)인가.

    2026-08-25 MW0602 실측: 7레그 수수료 13,951원 / 약정대금 734백만원
    → 1계약 편도(약정 52백만원)당 약 988원, 왕복 약 1,976원.
    (MW0601 원본은 편도 ≈5,100원 — 계좌별 요율 상이, 파일 상단 주석 참조)
    """
    notional = 1040.0 * 50_000
    one_way = notional * S.FUTURES_COMMISSION_RATE
    assert 950 < one_way < 1_030
    assert 1_900 < one_way * 2 < 2_060
