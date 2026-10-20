# -*- coding: utf-8 -*-
"""[MW0602 641차] 미니 근월물 롤 — regular_candles 소비처가 `code='A056A'` 를 하드코딩해 2026-10-08 만기 뒤
「정규봉 적재가 멈춘 것처럼」 보였던 결함의 회귀 가드. 딥다이브: docs/맥점x옵션사다리개선/09_정규봉적재중단_딥다이브_MW0602-20261020.md
"""
import os
import re
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "tools", "maekjeom_ladder"))

import ladder_data as LD  # noqa: E402


def _db():
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE regular_candles(code TEXT, ts TEXT, trade_date TEXT, open REAL, high REAL, low REAL, close REAL, volume REAL)")
    rows = []
    for d, codes in (("2026-10-07", ("A056A", "A056B")), ("2026-10-08", ("A056A", "A056B")), ("2026-10-12", ("A056B",)),
                     ("2026-11-12", ("A056B", "A056C")), ("2026-12-10", ("A056C", "A0571"))):
        for c in codes:
            rows.append((c, d + " 09:00:00", d, 1.0, 1.0, 1.0, 1.0, 10.0 if c == "A056A" else 99.0))   # 거래량은 원월물이 크게 — 거래량으로 고르면 틀린다
    con.executemany("INSERT INTO regular_candles VALUES(?,?,?,?,?,?,?,?)", rows)
    con.execute("INSERT INTO regular_candles VALUES('10100','2026-10-12 09:00:00','2026-10-12',1,1,1,1,1)")
    return con


def test_1_front_month_is_nearest_expiry_not_max_volume():
    con = _db()
    assert LD.mini_code_for(con, "2026-10-08") == "A056A"      # 만기일 당일까지 미륵이는 A056A(실측 종가 오차 0.000)
    assert LD.mini_code_for(con, "2026-10-12") == "A056B"
    assert LD.mini_code_for(con, "2026-12-10") == "A056C"      # 연도 넘김(A0571) 앞
    assert LD.mini_code_for(con, "2026-10-09") is None          # 미측정 ≠ 0


def test_2_expiry_and_continuing_contract_for_prev_day():
    assert str(LD.mini_expiry("A056A")) == "2026-10-08" and str(LD.mini_expiry("A056B")) == "2026-11-12"
    assert str(LD.mini_expiry("A0571")) == "2027-01-14" and LD.mini_expiry("XX") is None
    con = _db()
    assert LD.mini_code_continuing(con, "2026-10-08", "2026-10-12") == "A056B"   # 롤 다음 날 — 오늘도 살아 있는 월물
    assert LD.mini_code_continuing(con, "2026-10-07", "2026-10-08") == "A056A"
    assert LD.mini_code_continuing(con, "2026-11-12", "2026-11-13") == "A056C"


def test_3_no_hardcoded_mini_code_in_consumers():
    """조회문에 A056A 리터럴이 다시 들어오면 실패 — 다음 롤(11/12 A056B→C)에서 같은 결함이 재발한다."""
    pat = re.compile(r"(?<!`)code\s*=\s*'A05[0-9][0-9A-C]'|\(\s*MINI_CODE\s*,")       # 백틱 안 설명 문구는 제외
    for rel in ("tools/maekjeom_ladder/ladder_data.py", "scripts/shindong2_live.py", "scripts/foreign_flow_pit_review.py",
                "scripts/shindong2_research.py"):
        src = open(os.path.join(ROOT, rel), encoding="utf-8").read()
        hits = [l for l in src.splitlines() if pat.search(l) and not l.strip().startswith("#")]
        assert not hits, (rel, hits)
