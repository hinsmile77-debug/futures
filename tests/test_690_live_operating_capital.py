# -*- coding: utf-8 -*-
"""[MW0601 2026-10-13] CREON 실거래 전환 — 사용자 결정 운영값 고정.

  목표자본(사이징) 5천만원 유지 · 실운영금 3,400만원(손실 한도 분모 — 2026-10-23 707차 1,500만→3,400만) ·
  MAX_CONTRACTS 3(2026-10-23 707차 1→3) · 신동 3계약(2026-10-21 1→2 · 2026-10-23 707차 2→3) · 피터2 1계약 · CB② 3 ·
  CREON 편도 수수료 0.0019%.
값을 바꾸면 이 테스트가 깨져 결정 기록 갱신을 강제한다.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config.settings as ST          # noqa: E402
import config.capital as CAP          # noqa: E402
from config import constants as K     # noqa: E402


def test_user_decided_values():
    assert ST.SIZING_TARGET_CAPITAL_ENABLED is True
    assert ST.SIZING_TARGET_CAPITAL_KRW == 50_000_000
    assert ST.LIVE_OPERATING_CAPITAL_KRW == 30_000_000   # [707차] 3,400만 → [711차] 3,000만(위험자산 기준, 사용자 결정)
    assert ST.MAX_CONTRACTS == 3                         # [707차] 증거금 최대 3(예수금 3,400만 ÷ 약 901만)
    assert ST.MINI_MIN_CONTRACTS == 1                    # 최소 계약수 — 상한과 혼동 금지(2026-10-23 오편집 복원)
    assert ST.SHINDONG_LIVE_QTY == 3                     # [707차] 2 → 3
    assert ST.PETER2_QTY == 1
    assert ST.CB_CONSEC_STOP_LIMIT == 3
    assert K.BROKER_CHANNEL_SPECS["CREON"]["one_way_commission_rate"] == 0.000019


def test_sizing_uses_target_but_loss_limit_uses_operating():
    op = ST.LIVE_OPERATING_CAPITAL_KRW
    assert CAP.sizing_capital(op) == 50_000_000
    assert CAP.risk_capital(op) == op
    assert CAP.daily_loss_limit_krw(op) == op * ST.DAILY_LOSS_LIMIT_PCT
    # 실운영금 2% 손실 → 한도 도달 (사이징 자본 기준이면 과소평가된다)
    assert abs(CAP.daily_loss_ratio(op * 0.02, op) - 0.02) < 1e-12
    # [707차] 예탁금이 정책값보다 적으면 그쪽을 분모로 쓴다
    assert CAP.risk_capital(op, deposit_krw=27_000_000) == 27_000_000


def test_operating_capital_unset_falls_back(monkeypatch):
    monkeypatch.setattr(CAP, "LIVE_OPERATING_CAPITAL_KRW", 0)
    assert CAP.risk_capital(0) == CAP.sizing_capital(0)


def test_consistency_real_server_is_info_when_operating_set():
    msgs = CAP.check_consistency(actual_balance=ST.LIVE_OPERATING_CAPITAL_KRW, is_simulation=False)
    levels = {lv for lv, _ in msgs}
    assert "CRITICAL" not in levels
    assert any(lv == "INFO" and "실운영금" in m for lv, m in msgs)


def test_consistency_real_server_critical_without_operating(monkeypatch):
    monkeypatch.setattr(CAP, "LIVE_OPERATING_CAPITAL_KRW", 0)
    msgs = CAP.check_consistency(actual_balance=ST.LIVE_OPERATING_CAPITAL_KRW, is_simulation=False)
    assert any(lv == "CRITICAL" for lv, _ in msgs)
