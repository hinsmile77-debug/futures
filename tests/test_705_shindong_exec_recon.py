# -*- coding: utf-8 -*-
"""[MW0601 705차] 신동 실거래 대사 — 리포트 재생 MAIN 과 실거래가 갈리는 이유를 리포트가 직접 보인다.

2026-10-22 사고: 리포트 MAIN +259.9만 vs 실거래 +112.7만(브로커 net 일치). 리포트에 실거래가 한 줄도
없어 「패널과 안 맞는다」로만 드러났다. 원인은 ① 진입 뒤 재생에서 철회된 신호(실거래만 3건 −30.0만)
② 늦음·보유 중으로 못 친 재생 신호(재생만 3건 +120.1만). ②의 보유 중 2건은 로그조차 없었다.
"""
import io
import os
import sqlite3

from strategy.shindong import exec_recon as XR

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _mkdb(tmp_path, legs, broker=None, other=()):
    p = str(tmp_path / "trades.db")
    con = sqlite3.connect(p)
    con.execute("CREATE TABLE trades (entry_ts TEXT, exit_ts TEXT, direction TEXT, quantity INT, "
                "entry_price REAL, exit_price REAL, pnl_krw REAL, net_pnl_krw REAL, exit_reason TEXT, "
                "entry_source TEXT)")
    con.execute("CREATE TABLE daily_broker_pnl (date TEXT, broker_net_krw REAL, broker_net_source TEXT)")
    for l in legs:
        con.execute("INSERT INTO trades VALUES (?,?,?,?,?,?,?,?,?,?)", l + ("SHINDONG",))
    for l in other:
        con.execute("INSERT INTO trades VALUES (?,?,?,?,?,?,?,?,?,?)", l + ("MIREUK",))
    if broker is not None:
        con.execute("INSERT INTO daily_broker_pnl VALUES ('2026-10-22', ?, 'live')", (broker,))
    con.commit()
    con.close()
    return p


D = "2026-10-22 "
LEGS = [
    # 철회됐지만 집행 — 2계약 한 번에 손절
    (D + "09:33:05", D + "09:41:20", "SHORT", 2, 881.93, 885.74, -384351.0, -384351.0, "하드스톱(틱)"),
    # 일치 — 1+1 분할(포지션 하나)
    (D + "10:13:05", D + "10:38:42", "SHORT", 1, 882.15, 874.52, 379824.0, 379824.0, "신동1차"),
    (D + "10:13:05", D + "10:45:14", "SHORT", 1, 882.15, 874.84, 363824.0, 363824.0, "하드스톱(틱)"),
    # 집행 기록 없는 실거래(수동 등)
    (D + "14:00:00", D + "14:10:00", "LONG", 2, 860.0, 861.0, 10000.0, 10000.0, "수동"),
]
EVENTS = [
    {"kind": "ENTER", "trade_key": "R3|09:32|-1", "side": -1, "entered_at": "2026-10-22T09:33:05"},
    {"kind": "RETRACTED", "trade_key": "R3|09:32|-1"},
    {"kind": "SKIP_STALE", "trade_key": "R3|09:37|+1"},
    {"kind": "ENTER", "trade_key": "R3|10:12|-1", "side": -1, "entered_at": "2026-10-22T10:13:05"},
    {"kind": "SKIP_HOLDING", "trade_key": "R3|13:25|+1", "holding": "R3|13:21|-1"},
    {"kind": "REJECT", "trade_key": "R3|13:40|-1", "why": "ProfitGuard [L4]"},
]
MAIN = [
    {"key": "R3|09:37|+1", "side": 1, "entry_ts": "09:37", "entry_px": 882.30, "net": 951000.0},
    {"key": "R3|10:12|-1", "side": -1, "entry_ts": "10:12", "entry_px": 882.22, "net": 737000.0},
    {"key": "R3|13:25|+1", "side": 1, "entry_ts": "13:25", "entry_px": 860.90, "net": -291000.0},
    {"key": "R3|13:40|-1", "side": -1, "entry_ts": "13:40", "entry_px": 860.00, "net": 1000.0},
    {"key": "R3|13:51|-1", "side": -1, "entry_ts": "13:51", "entry_px": 860.42, "net": 541000.0},
]


def test_real_positions_group_legs_by_position(tmp_path):
    pos = XR.real_positions(_mkdb(tmp_path, LEGS), "2026-10-22")
    assert len(pos) == 3                                    # 레그 4 → 포지션 3 (계측 4원칙 ①)
    p = [x for x in pos if x["entry_ts"].endswith("10:13:05")][0]
    assert p["qty"] == 2 and abs(p["net"] - 743648.0) < 1e-6 and len(p["legs"]) == 2


def test_missing_db_is_unmeasured_not_zero(tmp_path):
    assert XR.real_positions(str(tmp_path / "none.db"), "2026-10-22") is None
    assert XR.broker_net(str(tmp_path / "none.db"), "2026-10-22") is None


def test_reconcile_classifies_every_case(tmp_path):
    db = _mkdb(tmp_path, LEGS)
    rc = XR.reconcile(MAIN, XR.real_positions(db, "2026-10-22"), EVENTS)
    kinds = {(it["kind"], it["key"]): it for it in rc["items"]}
    assert ("MATCH", "R3|10:12|-1") in kinds
    assert ("EXEC_RETRACTED", "R3|09:32|-1") in kinds
    assert kinds[("EXEC_RETRACTED", "R3|09:32|-1")]["note"] == "철회 이벤트 있음"
    assert ("EXEC_UNKEYED", None) in kinds                 # 짝 없는 실거래도 숨기지 않는다
    assert kinds[("REPLAY_ONLY", "R3|09:37|+1")]["note"] == "늦게 알아챔"
    assert kinds[("REPLAY_ONLY", "R3|13:25|+1")]["note"].startswith("보유 중")
    assert kinds[("REPLAY_ONLY", "R3|13:40|-1")]["note"].startswith("기각")
    assert kinds[("REPLAY_ONLY", "R3|13:51|-1")]["note"].endswith("(미측정)")
    # 합 보존: 실거래 합 = 모든 실거래 포지션 합 · 재생 합 = MAIN 합
    assert abs(rc["real_total"] - (-384351 + 743648 + 10000)) < 1e-6
    assert abs(rc["replay_total"] - sum(r["net"] for r in MAIN)) < 1e-6
    t = rc["totals"]
    assert abs(t["MATCH"]["real"][0] + t["EXEC_RETRACTED"]["real"][0] + t["EXEC_UNKEYED"]["real"][0]
               - rc["real_total"]) < 1e-6
    assert abs(t["MATCH"]["replay"][0] + t["REPLAY_ONLY"]["replay"][0] - rc["replay_total"]) < 1e-6


def test_broker_and_other_sources(tmp_path):
    other = [(D + "11:00:00", D + "11:05:00", "LONG", 1, 870.0, 871.0, 5000.0, 5000.0, "TP1")]
    db = _mkdb(tmp_path, LEGS, broker=374000.0, other=other)
    assert XR.broker_net(db, "2026-10-22")["net"] == 374000.0
    o = XR.other_sources(db, "2026-10-22")
    assert o["legs"] == 1 and o["net"] == 5000.0          # 브로커 net 은 계좌 전체 — 섞인 몫을 드러낸다


def test_cumulative_exec_counts_positions(tmp_path):
    cx = XR.cumulative_exec(_mkdb(tmp_path, LEGS), "2026-10-21", "2026-10-22")
    assert cx["n"] == 3 and cx["days"] == 1 and cx["win"] == 2


# ── 리포트 · main 배선 ────────────────────────────────────────────────────

def _read(p):
    return io.open(os.path.join(ROOT, p), encoding="utf-8").read()


def test_report_section_and_labels():
    from strategy.shindong import daily_report as DR
    assert "실거래 대사" in DR._recon_section(None)[0] or "미측정" in DR._recon_section(None)[0]
    src = _read("strategy/shindong/daily_report.py")
    assert '"재생(장중 기록)" if v in live_vs' in src           # 「라이브」 → 「재생」
    assert "## 2-1. 실거래 대사" in src
    assert "판정 기준 아님" in src                                # C: 참고 행, 사전등록 판정 무변경
    assert 'replace("|", "\\\\|")' in src                      # 표 칸 구분자 이스케이프
    assert "trades_db=TRADES_DB" in _read("scripts/shindong_daily_report.py")
    assert "trades_db=runtime_settings.TRADES_DB" in _read("main.py")


def test_main_logs_skip_holding_without_touching_reject_dedupe():
    src = _read("main.py")
    assert src.count("self._sd_exec_hold_seen = set()") == 2       # __init__ + 날짜 전환 리셋
    body = src[src.index("[MW0601 705차 B]"):]
    body = body[:body.index("            return")]
    assert '"SKIP_HOLDING"' in body and "새 신호 미집행" in body
    assert "self._sd_exec_skipped.add" not in body                # 기각 로그 1회 억제와 분리
