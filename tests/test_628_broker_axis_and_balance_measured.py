# -*- coding: utf-8 -*-
"""[MW0602 628차] 실계좌 브로커 손익 축 · 잔고 미측정 표기.

2026-10-14 실계좌(783293269) 첫 브로커 판독에서 두 개의 낡은 전제가 드러났다.

① CpTd6197 「금일매매손익」(idx6)이 **수수료 후(net)** 였다 — 모의는 수수료 전(gross).
   idx6 −650,647 = 익일가예탁 − 예탁 −650,647. 엔진 gross −647,000 · 수수료 3,661.
   그대로 gross 로 대조해 `[BrokerPnl] gross 불일치 −3,647원` 거짓 경보가 났고,
   `fetch_broker_net` 은 브로커 수수료를 `idx6 − net = 0원` 으로 계산했다.
② 잔고 조회가 종일 실패하는 동안 사이저 생성자 기본값 1억이 「실제잔고」로 찍혀
   `[Capital]` CRITICAL · 괴리 +566.7% 경고를 냈다(계측 4원칙 ②).
"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.db_utils import broker_pnl_axis  # noqa: E402
import config.capital as cap  # noqa: E402
from strategy.entry.position_sizer import PositionSizer  # noqa: E402


# ── ① 축 판별 ─────────────────────────────────────────────────────────
def test_실계좌_idx6이_net과_같으면_net축():
    assert broker_pnl_axis(-650647.0, -650647.0, 3661.0) == "net"


def test_모의계좌_idx6이_수수료만큼_다르면_gross축():
    # 2026-10-13 모의 실측: idx6 2,709,000 · 브로커 net 2,698,196 · 엔진 수수료 28,778
    assert broker_pnl_axis(2709000.0, 2698196.0, 28778.0) == "gross"


def test_거래없는날은_판별불가_None():
    assert broker_pnl_axis(0.0, 0.0, 0.0) is None
    assert broker_pnl_axis(None, -1.0, 10.0) is None
    assert broker_pnl_axis(-1.0, None, 10.0) is None


def test_net축이면_브로커_수수료는_0이_아니라_미측정(monkeypatch):
    import utils.db_utils as du
    row = {"pnl_krw": -650647.0, "broker_net_krw": -650647.0, "deposit_cash_krw": 15383556.0,
           "next_day_deposit_cash_krw": 14732909.0, "commission_krw": 3661.0, "pnl_net_krw": -650661.0,
           "broker_net_source": None, "deposit_snapshot_ts": None}
    monkeypatch.setattr(du, "fetchone", lambda *a, **k: row)
    b = du.fetch_broker_net("2026-10-14")
    assert b["pnl_axis"] == "net" and b["gross_krw"] is None and b["commission_krw"] is None
    r = du.reconcile_daily_net("2026-10-14", -647000.0, 3661.0, -650661.0)
    assert r["status"] == "OK" and r["residual"] == -14.0
    assert r["broker_commission"] is None and r["commission_ratio"] is None


def test_gross축은_종전대로_브로커_수수료를_잰다(monkeypatch):
    import utils.db_utils as du
    row = {"pnl_krw": 2709000.0, "broker_net_krw": 2698196.0, "deposit_cash_krw": 29760446.0,
           "next_day_deposit_cash_krw": 32458642.0, "commission_krw": 28778.0, "pnl_net_krw": 2740222.0,
           "broker_net_source": None, "deposit_snapshot_ts": None}
    monkeypatch.setattr(du, "fetchone", lambda *a, **k: row)
    b = du.fetch_broker_net("2026-10-13")
    assert b["pnl_axis"] == "gross" and b["commission_krw"] == 10804.0


# ── ② 잔고 미측정 ──────────────────────────────────────────────────────
def test_사이저는_생성자_잔고를_미측정으로_본다():
    s = PositionSizer(account_balance=100_000_000)
    assert s.balance_measured is False
    s.set_account_balance(0)          # 빈 응답은 측정이 아니다
    assert s.balance_measured is False
    s.set_account_balance(14_732_909)
    assert s.balance_measured is True and s.account_balance == 14_732_909


def test_미측정이면_괴리경고를_내지_않고_미측정을_알린다():
    out = cap.check_consistency(actual_balance=100_000_000, is_simulation=False,
                                balance_measured=False)
    texts = " ".join(t for _, t in out)
    assert "미측정" in texts
    assert "기준자본(" not in texts                  # 기본값으로 괴리 경고(②)를 내지 않는다
    assert "100,000,000원)와 무관하게" not in texts   # 기본값을 「실제 잔고」로 쓰지 않는다


def test_측정됐으면_종전과_같다():
    # v9-dev: 실운영금(operating_capital)이 설정돼 있으면 ①은 INFO, ②는 실운영금과 대조한다.
    out = cap.check_consistency(actual_balance=100_000_000, is_simulation=False)
    texts = " ".join(t for _, t in out)
    assert "100,000,000원" in texts and "미측정" not in texts
    if cap.SIZING_TARGET_CAPITAL_ENABLED:
        assert "괴리" in texts


def test_net축_잔차_분해는_미측정으로_빠진다():
    import utils.db_utils as du
    rec = {"residual": -14.0, "engine_commission": 3661.0, "broker_commission": None,
           "engine_gross": -647000.0, "broker_gross": None, "commission_ratio": None,
           "engine_net": -650661.0, "broker_net": -650647.0, "tolerance": 5000.0}
    d = du.decompose_net_residual(rec, True)
    assert d["comm_axis"] is None and d["gross_axis"] is None and d["dominant"] is None
    txt = du.format_net_recon_mismatch(rec, True)
    assert "미측정" in txt


def test_프로파일_한줄도_미측정을_표기한다():
    p = cap.capital_profile(100_000_000, balance_measured=False)
    assert p["gap_pct"] is None
    line = cap.format_profile(p)
    assert "실제잔고=미측정(기본값 100,000,000원)" in line and "괴리=미측정" in line
