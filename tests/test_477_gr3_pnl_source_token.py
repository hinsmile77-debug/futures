# -*- coding: utf-8 -*-
"""[MW0601 477차 후속7 / GR-3] ProfitGuard 차단 로그의 일일손익 원천 토큰.

왜 필요한가
-----------
ProfitGuard가 보는 `daily_pnl_krw`는 호출부(main.py)에서 **broker(gross)** 캐시와
**engine(net)** 폴백을 오간다(2026-08-18 실측 차이 23,332원). 비율 판정은 내부
일관적이라 오작동은 아니지만 `trail_activation_krw`가 절대 원화라 폴백 여부로
발동 시점이 달라지는데, 그 원천이 차단 로그에 남지 않아 사후 복원이 불가능했다.
main.py의 `[DebugPnL]` 줄은 **등급이 이미 X면 찍히지 않아** 커버리지가 23%뿐이다.

고정하는 사실:
① 모든 차단 줄에 `| src=` 토큰이 붙는다(레이어 무관).
② broker → `broker(gross)`, engine → `engine(net)`로 **단위가 이름에 박힌다**.
③ 호출부가 원천을 안 주면 `미상` — 0이나 임의 기본값으로 채우지 않는다(4원칙 ②·④).
④ `_block_log` 튜플 arity는 3 그대로다(대시보드가 `for ts, layer, reason` 언팩).
⑤ GR-1 스크립트가 그 토큰을 집계하고, 토큰 없는 과거 로그는 **미측정**으로 남긴다.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import strategy.profit_guard as pg
import scripts.profit_guard_latch_watch as pgw


@pytest.fixture
def cap(monkeypatch):
    lines = []
    monkeypatch.setattr(pg.log_manager, "signal", lambda m: lines.append(m))
    monkeypatch.setattr(pg.log_manager, "system", lambda m, lv="INFO": None)
    return lines


def _guard_halted():
    """L1이 이미 래치된 가드 — is_entry_allowed가 곧바로 L1 차단으로 간다."""
    g = pg.ProfitGuard()
    g._trail.is_halted = True
    g._trail._halt_reason = "테스트 래치"
    return g


def test_block_log_has_broker_gross_token(cap):
    g = _guard_halted()
    allowed, _ = g.is_entry_allowed(500000.0, 1.0, pnl_source="broker")
    assert allowed is False
    blocked = [l for l in cap if "진입 차단" in l]
    assert len(blocked) == 1
    assert "| src=broker(gross)" in blocked[0]


def test_block_log_has_engine_net_token(cap):
    g = _guard_halted()
    g.is_entry_allowed(500000.0, 1.0, pnl_source="engine")
    assert "| src=engine(net)" in [l for l in cap if "진입 차단" in l][0]


def test_missing_source_is_unknown_not_defaulted(cap):
    """호출부가 원천을 안 주면 '미상' — engine으로 가정하지 않는다(4원칙 ②)."""
    g = _guard_halted()
    g.is_entry_allowed(500000.0, 1.0)          # pnl_source 미지정
    line = [l for l in cap if "진입 차단" in l][0]
    assert "| src=미상" in line
    assert "engine" not in line and "broker" not in line


def test_unknown_label_passes_through(cap):
    g = _guard_halted()
    g.is_entry_allowed(500000.0, 1.0, pnl_source="mock_src")
    assert "| src=mock_src" in [l for l in cap if "진입 차단" in l][0]


def test_source_updated_per_call(cap):
    g = _guard_halted()
    g.is_entry_allowed(500000.0, 1.0, pnl_source="broker")
    g.is_entry_allowed(500000.0, 1.0, pnl_source="engine")
    blocked = [l for l in cap if "진입 차단" in l]
    assert "broker(gross)" in blocked[0] and "engine(net)" in blocked[1]


def test_block_log_tuple_arity_unchanged(cap):
    """대시보드가 `for ts, layer, reason in block_log`로 언팩한다 — 3튜플 유지."""
    g = _guard_halted()
    g.is_entry_allowed(500000.0, 1.0, pnl_source="broker")
    assert len(g._block_log) == 1
    ts, layer, reason = g._block_log[0]      # 언팩 실패하면 대시보드가 깨진다
    assert layer.startswith("L1")


def test_reason_string_has_no_token(cap):
    """반환 reason은 종전 형식 그대로 — grade_x_source 문자열에 토큰이 새지 않는다."""
    g = _guard_halted()
    _, reason = g.is_entry_allowed(500000.0, 1.0, pnl_source="broker")
    assert reason.startswith("[L1")
    assert "src=" not in reason


# ── ⑤ GR-1 스크립트 연결 ──────────────────────────────────────────


def test_gr1_parses_src_token(tmp_path, monkeypatch):
    logs = tmp_path / "logs"
    logs.mkdir()
    (logs / "20260818_TRADE.log").write_text(
        "2026-08-18 13:19:59 [WARNING] TRADE: [ProfitGuard-L1] 트레일링 발동 — "
        "피크 +927,000원 대비 20% 하락 (현재 +685,000원 < 보호선 +741,600원)\n",
        encoding="utf-8")
    (logs / "20260818_SIGNAL.log").write_text(
        "2026-08-18 13:30:59 [INFO] SIGNAL: [ProfitGuard] 진입 차단 [L1-Trail] 사유 | src=broker(gross)\n"
        "2026-08-18 13:31:59 [INFO] SIGNAL: [ProfitGuard] 진입 차단 [L1-Trail] 사유 | src=broker(gross)\n"
        "2026-08-18 13:32:59 [INFO] SIGNAL: [ProfitGuard] 진입 차단 [L1-Trail] 사유 | src=engine(net)\n",
        encoding="utf-8")
    monkeypatch.setattr(pgw, "LOG_DIR", str(logs))
    _, blocks, srcs = pgw.scan_logs("2026-06-01")
    assert len(blocks["2026-08-18"]) == 3
    assert srcs["2026-08-18"] == {"broker(gross)": 2, "engine(net)": 1}


def test_gr1_legacy_log_without_token_is_unmeasured(tmp_path, monkeypatch):
    """토큰 이전 로그는 빈 dict — 'engine이었다'로 추정하지 않는다."""
    logs = tmp_path / "logs"
    logs.mkdir()
    (logs / "20260630_TRADE.log").write_text(
        "2026-06-30 09:51:54 [WARNING] TRADE: [ProfitGuard-L1] 트레일링 발동 — "
        "피크 +2,082,000원 대비 20% 하락 (현재 +723,000원 < 보호선 +1,665,600원)\n",
        encoding="utf-8")
    (logs / "20260630_SIGNAL.log").write_text(
        "2026-06-30 10:00:59 [INFO] SIGNAL: [ProfitGuard] 진입 차단 [L1-Trail] 사유\n",
        encoding="utf-8")
    monkeypatch.setattr(pgw, "LOG_DIR", str(logs))
    _, blocks, srcs = pgw.scan_logs("2026-06-01")
    assert "2026-06-30" in blocks
    assert srcs.get("2026-06-30", {}) == {}
