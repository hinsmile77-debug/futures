# -*- coding: utf-8 -*-
"""[MW0601 2026-10-13] CREON 실거래 전환 — 사용자 결정 운영값 고정.

  목표자본(사이징) 5천만원 유지 · 실운영금 1,500만원(손실 한도 분모) ·
  신동 1계약 · 피터2 1계약 · CB② 3 · CREON 편도 수수료 0.0019%.
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
    assert ST.LIVE_OPERATING_CAPITAL_KRW == 15_000_000
    assert ST.MAX_CONTRACTS == 1
    assert ST.SHINDONG_LIVE_QTY == 1
    assert ST.PETER2_QTY == 1
    assert ST.CB_CONSEC_STOP_LIMIT == 3
    assert K.BROKER_CHANNEL_SPECS["CREON"]["one_way_commission_rate"] == 0.000019


def test_sizing_uses_target_but_loss_limit_uses_operating():
    bal = 15_000_000
    assert CAP.sizing_capital(bal) == 50_000_000
    assert CAP.risk_capital(bal) == 15_000_000
    assert CAP.daily_loss_limit_krw(bal) == 15_000_000 * ST.DAILY_LOSS_LIMIT_PCT
    # 30만원 손실 = 실운영금 2% → 한도 도달 (사이징 자본 기준이면 0.6% 로 과소평가됐다)
    assert abs(CAP.daily_loss_ratio(300_000, bal) - 0.02) < 1e-12


def test_operating_capital_unset_falls_back(monkeypatch):
    monkeypatch.setattr(CAP, "LIVE_OPERATING_CAPITAL_KRW", 0)
    assert CAP.risk_capital(0) == CAP.sizing_capital(0)


def test_consistency_real_server_is_info_when_operating_set():
    msgs = CAP.check_consistency(actual_balance=15_000_000, is_simulation=False)
    levels = {lv for lv, _ in msgs}
    assert "CRITICAL" not in levels
    assert any(lv == "INFO" and "실운영금" in m for lv, m in msgs)


def test_consistency_real_server_critical_without_operating(monkeypatch):
    monkeypatch.setattr(CAP, "LIVE_OPERATING_CAPITAL_KRW", 0)
    msgs = CAP.check_consistency(actual_balance=15_000_000, is_simulation=False)
    assert any(lv == "CRITICAL" for lv, _ in msgs)
