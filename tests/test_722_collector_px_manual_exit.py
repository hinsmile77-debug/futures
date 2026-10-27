# -*- coding: utf-8 -*-
"""[MW0601 722차 / 장후 자동조치 — 2026-10-27 G-7·G-8] 신동 점검 수집기 2건 — 회귀 고정.

· G-7 — 케이스 표 재생 1차/최종 가격이 `897.4499558212302` 처럼 원시 부동소수로 찍혔다 → 2자리 표기.
        값은 바꾸지 않고 표기만(O-704: 반올림이 숫자를 바꾸면 안 된다).
· G-8 — 14:37 대시보드 수동 전량청산(-155,035원 기회비용)이 로그를 직접 읽어야만 보였다 →
        수집기 §4 에 「수동 개입 N건 · 사유 미기록」 줄 + 자동 적신호.

수정 범위는 **점검 수집기(리포트 도구)뿐**이다 — 매매 코드는 한 줄도 안 바뀐다.
"""
from __future__ import annotations

import importlib.util
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SD_PATH = os.path.join(ROOT, ".claude", "skills", "shindong-daily-check", "scripts",
                       "collect_shindong_evidence.py")


@pytest.fixture(scope="module")
def sd():
    if not os.path.exists(SD_PATH):
        pytest.skip("수집기 본체 없음 — 스킬 미설치 환경")
    spec = importlib.util.spec_from_file_location("_collect_shindong_evidence_722", SD_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ── G-7 ──────────────────────────────────────────────────────────────────────
def test_g7_px_rounds_raw_float(sd):
    assert sd.px(897.4499558212302) == "897.45"
    assert sd.px(895.28) == "895.28"
    assert sd.px("884.12") == "884.12"


def test_g7_px_unmeasured_is_dash_not_zero(sd):
    assert sd.px(None) == "-"
    assert sd.px("") == "-"
    assert sd.px(0) == "0.00"                 # 0 은 측정값 — 「-」로 숨기지 않는다


def test_g7_px_display_only(sd):
    # 반올림 뒤 값이 원값과 0.005 이내 — 표시만 바뀐다(O-704)
    v = 897.4499558212302
    assert abs(float(sd.px(v)) - v) <= 0.005


# ── G-8 (logs/20261027_TRADE.log 원문 그대로) ─────────────────────────────────
T = "2026-10-27 %s [INFO] TRADE: "
LOGS = {"20261027_TRADE.log": [
    T % "14:30:57" + "[ShindongExec] 진입 R3 SHORT 2계약 @882.80(규칙가 884.12) — R3|14:29|-1",
    T % "14:37:01" + "[주문요청] 수동 전량청산 SHORT 2계약 @ 881.70 체결대기",
    T % "14:37:02" + "[Position] 체결청산 SHORT @ 881.8 | PnL=+1.00pt (+48,323원) | 수동 전량청산",
]}


def test_g8_manual_counts_order_and_position(sd):
    sd_pos = [dict(src="SHINDONG", entry_ts="2026-10-27 14:30:57", reasons=["수동 전량청산"]),
              dict(src="SHINDONG", entry_ts="2026-10-27 13:15:30", reasons=["하드스톱(틱)"])]
    hits, pos = sd.manual_interventions(LOGS, sd_pos, [])
    assert len(hits) == 1 and "수동 전량청산" in hits[0][1]
    assert pos == [("SHINDONG", "2026-10-27 14:30:57", ["수동 전량청산"])]


def test_g8_dedup_same_line_in_two_files(sd):
    logs = dict(LOGS)
    logs["20261027_SYSTEM.log"] = [LOGS["20261027_TRADE.log"][1]]
    hits, _ = sd.manual_interventions(logs)
    assert len(hits) == 1


def test_g8_no_manual_is_zero(sd):
    hits, pos = sd.manual_interventions({"x.log": [LOGS["20261027_TRADE.log"][0]]}, None, None)
    assert hits == [] and pos == []


def test_g8_not_triggered_by_manual_entry_warnings(sd):
    # 수동 「진입」 거부 알림은 청산이 아니다 — 주문요청 줄만 센다
    logs = {"x.log": ["2026-10-27 09:00:00 [WARNING] SYSTEM: 수동 진입 불가: 이미 포지션 보유 중"]}
    assert sd.manual_interventions(logs)[0] == []


def test_collector_is_report_only():
    # 수집기는 매매 코드를 import 하지 않는다
    with open(SD_PATH, encoding="utf-8") as f:
        src = f.read()
    for bad in ("import main", "from main", "strategy.shindong", "collection.cybos", "win32com"):
        assert bad not in src, bad
