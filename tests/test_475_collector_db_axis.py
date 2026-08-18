# -*- coding: utf-8 -*-
"""tests/test_475_collector_db_axis.py
    — [MW0602 475차 후속] 수집기 DB 읽기 계층 회귀 (장후 G-1 · G-2)

────────────────────────────────────────────────────────────────────────────
무엇을 지키는가
────────────────────────────────────────────────────────────────────────────
이 수집기가 DB 를 읽는 **첫 경로**다. 두 고도화가 같은 선행조건을 공유한다:

  G-1 비용 축   — 로그에는 수수료가 없다. 청산 줄 `PnL=+0.34pt (+15,301원)` 의
                 pt 는 gross, 원은 **net** 이라 순액만 보면 "방향은 맞혔는데
                 비용에 졌다"와 "방향을 틀렸다"가 같은 숫자로 보인다.
                 2026-08-18 실측: gross +8,000 / 수수료 33,084 / net -25,084.
  G-2 binding_gate — `ensemble_decisions.sizing_trace` 는 로그에 없다.
                 431차가 곱셈 체인을 min() 합성으로 바꾼 뒤 "무엇이 실제로 사이즈를
                 구속했는가"가 관측 대상이 됐는데 §12 감시 목록에 없었다.

불변식:
  (1) DB 가 없으면 `None` — 빈 리스트가 아니다. 0과 미측정을 구분한다(계측 4원칙 ②)
  (2) 0바이트 유령 DB(`data/db/ensemble_decisions.db`)를 열어도 조용히 0을 만들지 않는다
  (3) `trade_costs` 는 **진입 시각(HH:MM)** 으로 묶는다 — §5 포지션표와 같은 단위
      (470차 S3: 레그로 세면 없는 인과가 만들어진다)
  (4) DB 지표는 로그 지표와 **같은 판정 규칙**(`stuck_verdict`)을 쓴다
  (5) DB 접근 실패는 `무기록` + "미측정" 문구 — 압력 0으로 읽히면 안 된다
"""
from __future__ import print_function

import os
import shutil
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    ".claude", "skills", "mireuk-daily-check", "scripts"))

import collect_evidence as ce                                        # noqa: E402

_fails = []


def check(label, cond):
    print("%s %s" % ("[OK]  " if cond else "[FAIL]", label))
    if not cond:
        _fails.append(label)


def _make_trades_db(root, rows):
    d = os.path.join(root, "data", "db")
    os.makedirs(d)
    con = sqlite3.connect(os.path.join(d, "trades.db"))
    con.execute("create table trades (entry_ts text, exit_ts text, "
                "gross_pnl_krw real, commission_krw real, net_pnl_krw real)")
    con.executemany("insert into trades values (?,?,?,?,?)", rows)
    con.commit()
    con.close()


def _make_ens_db(root, rows):
    """rows: [(ts, sizing_trace_json)]"""
    d = os.path.join(root, "data", "db")
    if not os.path.isdir(d):
        os.makedirs(d)
    con = sqlite3.connect(os.path.join(d, "predictions.db"))
    con.execute("create table ensemble_decisions (ts text, sizing_trace text)")
    con.executemany("insert into ensemble_decisions values (?,?)", rows)
    con.commit()
    con.close()


# ══════════════════════════════════════════════════════════════════
def test_missing_db_is_none_not_empty():
    root = tempfile.mkdtemp(prefix="mireuk_db_")
    try:
        r = ce.db_rows(root, "data/db/nope.db", "select 1")
        check("(1) DB 부재는 None — 빈 리스트가 아니다", r is None)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_ghost_db_does_not_fabricate_zero():
    """0바이트 `ensemble_decisions.db` — 이름만 보고 열면 조용히 빈 결과가 나온다."""
    root = tempfile.mkdtemp(prefix="mireuk_db_")
    try:
        d = os.path.join(root, "data", "db")
        os.makedirs(d)
        open(os.path.join(d, "ensemble_decisions.db"), "wb").close()   # 0바이트
        r = ce.db_rows(root, "data/db/ensemble_decisions.db",
                       "select ts from ensemble_decisions")
        check("(2) 유령 DB 질의는 None (테이블 없음) — 0건으로 위장하지 않는다", r is None)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_trade_costs_groups_by_entry_minute():
    import datetime
    root = tempfile.mkdtemp(prefix="mireuk_db_")
    try:
        # 0818 실측 재현 — 10:08 진입 1건이 레그 2개로 쪼개진다(포지션 단위로 묶여야 한다).
        _make_trades_db(root, [
            ("2026-08-18 09:59:57", "2026-08-18 10:00:16", 17000.0, 1699.0, 15301.0),
            ("2026-08-18 10:08:58", "2026-08-18 10:10:06", -64500.0, 1696.0, -66196.0),
            ("2026-08-18 10:08:58", "2026-08-18 10:10:58", -134500.0, 1696.0, -136196.0),
            ("2026-08-17 10:00:00", "2026-08-17 10:01:00", 999999.0, 1.0, 999998.0),  # 다른 날
        ])
        c = ce.trade_costs(root, datetime.date(2026, 8, 18))
    finally:
        shutil.rmtree(root, ignore_errors=True)
    check("(3) 그날 청산분만 집계 (전날 999,999원 제외) — gross=%s" % c["gross"],
          abs(c["gross"] - (17000 - 64500 - 134500)) < 1)
    check("(3) 레그 수는 레그대로 센다", c["legs"] == 3)
    check("(3) 진입 분(10:08)으로 두 레그가 한 줄에 묶인다",
          c["by_min"]["10:08"][0] == 2 and abs(c["by_min"]["10:08"][3] + 202392) < 1)
    check("(3) 09:59 포지션은 따로", abs(c["by_min"]["09:59"][3] - 15301) < 1)


def test_db_indicator_uses_same_verdict_rules():
    import datetime, json
    root = tempfile.mkdtemp(prefix="mireuk_db_")
    try:
        rows = []
        for d in ("2026-08-12", "2026-08-13", "2026-08-18"):
            for i in range(10):
                rows.append(("%s 10:%02d:00" % (d, i),
                             json.dumps({"binding_gate": "tox"})))
        _make_ens_db(root, rows)
        cfg = {"db_indicators": {
            "lookback_days": 14, "min_samples": 20, "min_days": 3,
            "sources": {"binding_gate": {
                "db": "data/db/predictions.db",
                "sql": "select substr(ts,1,10) d, sizing_trace from ensemble_decisions "
                       " where ts >= ? and ts <= ? || ' 23:59:59' and sizing_trace is not null",
                "json_key": "binding_gate", "why": "테스트"}}}}
        out = ce.scan_db_indicators(root, cfg, datetime.date(2026, 8, 18))
    finally:
        shutil.rmtree(root, ignore_errors=True)
    r = out[0]
    check("(4) 한 값 100%%면 고착 — 로그 지표와 같은 규칙 (%s)" % r["verdict"],
          r["verdict"] == "고착")
    check("(4) 관측일·표본이 DB 기준으로 집계된다", r["days"] == 3 and r["n"] == 30)
    check("(4) 원천이 DB 로 표시된다", r.get("source") == "DB")
    check("(4) 관측률은 재지 않는다 (매분 축이 아니다)", r.get("ratio") is None)


def test_db_failure_is_unmeasured_not_zero():
    import datetime
    root = tempfile.mkdtemp(prefix="mireuk_db_")
    try:
        cfg = {"db_indicators": {"sources": {"binding_gate": {
            "db": "data/db/predictions.db",
            "sql": "select substr(ts,1,10) d, sizing_trace from ensemble_decisions "
                   " where ts >= ? and ts <= ? || ' 23:59:59'",
            "json_key": "binding_gate", "why": "테스트"}}}}
        out = ce.scan_db_indicators(root, cfg, datetime.date(2026, 8, 18))
    finally:
        shutil.rmtree(root, ignore_errors=True)
    r = out[0]
    check("(5) DB 접근 실패는 무기록", r["verdict"] == "무기록")
    check("(5) 사유가 '미측정'을 말한다 — 압력 0으로 읽히면 안 된다",
          "미측정" in r["note"])


if __name__ == "__main__":
    for fn in sorted(
        [v for k, v in list(globals().items()) if k.startswith("test_")],
        key=lambda f: f.__code__.co_firstlineno,
    ):
        print("\n── %s" % fn.__name__)
        fn()
    print("\n" + "=" * 60)
    if _fails:
        print("수집기 DB 계층 회귀 실패 %d건" % len(_fails))
        for f in _fails:
            print("  - %s" % f)
        sys.exit(1)
    print("수집기 DB 계층 회귀 전부 통과")
