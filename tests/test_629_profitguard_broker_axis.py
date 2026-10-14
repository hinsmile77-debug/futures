# -*- coding: utf-8 -*-
"""[MW0602 629차] ProfitGuard broker 추정 — 실계좌(net 축)에서 수수료 이중 차감 금지.

CpTd6197 금일매매손익(idx6)은 모의=수수료 전 / 실계좌=수수료 후(2026-10-14 MW0602 실측).
종전 코드는 축과 무관하게 `idx6 − 엔진 수수료` 로 net 을 추정해, 실계좌에서는 수수료가
두 번 빠졌다(`[ProfitGuard][DebugPnL] broker=` 표시값 · PROFIT_GUARD_SYSTEM_ONLY_PNL=False 면 판정값).
"""
import ast
import io
import os
import re

_MAIN = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py")


def _src():
    return io.open(_MAIN, encoding="utf-8").read()


def test_축_상태는_init에서_명시_초기화된다():
    assert re.search(r"self\._broker_pnl_axis_seen: Optional\[str\] = None", _src())


def test_net축이면_수수료를_다시_빼지_않는다():
    s = _src()
    i = s.index('_daily_pnl_source = "broker_net_est"')
    window = s[i - 900:i]
    assert 'if self._broker_pnl_axis_seen == "net":' in window
    assert '_broker_daily_pnl_now = float(_cached_realized)\n' in window


def test_축_판별은_예탁현금_축과_대조한다():
    s = _src()
    assert "_ax_fn(self._last_balance_realized_krw, _ax_nxt - _ax_dep" in s
    assert "[PnL] 브로커 금일매매손익 축 판별" in s


def test_main_구문():
    ast.parse(_src())
