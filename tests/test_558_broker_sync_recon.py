# -*- coding: utf-8 -*-
"""[MW0601 558차 후속 / G-3(556-6 이월)] 재기동 시 엔진↔브로커 대사 결과 원장.

무엇을 고정하는가
------------------
2026-09-10 사고는 **재기동이라는 우연한 계기**가 없었으면 15:10 강제청산까지,
어쩌면 그 뒤까지도 몰랐을 수 있다. 불일치 자체는 518차부터 ERROR 로 찍혀 왔지만
(`[BrokerSync] 재기동해 보니 계좌에 포지션이 남아 있다`), **로그는 세어지지
않는다** — "이번 달에 몇 번이나 어긋났는가"는 매번 사람이 로그를 뒤져야 했다.

G-3 원문이 요구한 것은 *"몇 번 재기동했고 **그중** 몇 번 불일치가 있었는지"* 다.
따라서 이 원장은 **MISMATCH 만 적지 않는다** — 분자만 남으면 비율이 안 나온다
(계측 4원칙 ⑤ — 대사는 모든 축을 걸어라).

그리고 「일치」와 「대조 못 함」을 섞지 않는다. 모의서버 blank rows·매칭 잔고행
없음·응답 해석 실패는 대조가 **성립하지 않은** 경우이며, 이것을 MATCH 로 적으면
"오늘 이상 없음"으로 위장된다 — FP-CRITICAL 이 PSI=0.0 으로 2개월을 조용히
보낸 것과 같은 계열이다(계측 4원칙 ②).

이 원장은 **판정에 관여하지 않는다.** 아래 「라이브 반영 0」 절이 그것을 고정한다.
"""
from __future__ import print_function

import io
import os
import re
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MAIN = os.path.join(_ROOT, "main.py")


def _tmp_db(monkeypatch):
    import utils.db_utils as D
    tmp = tempfile.mkdtemp()
    path = os.path.join(tmp, "trades.db")
    monkeypatch.setattr(D, "TRADES_DB", path, raising=False)
    D.init_broker_sync_recon_db()
    return D, path


def _rows(path):
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    try:
        return con.execute(
            "SELECT * FROM broker_sync_recon ORDER BY id").fetchall()
    finally:
        con.close()


# ── G3-1. 스키마 ───────────────────────────────────────────────────────────
def test_table_and_columns_exist(monkeypatch):
    D, path = _tmp_db(monkeypatch)
    con = sqlite3.connect(path)
    try:
        cols = set(r[1] for r in con.execute(
            "PRAGMA table_info(broker_sync_recon)").fetchall())
    finally:
        con.close()
    for c in ("ts", "trade_date", "outcome", "reconciled_measured",
              "before_state", "after_state", "direction",
              "broker_qty_per_position", "broker_avg_price",
              "detail", "pc_id", "session_pid"):
        assert c in cols, c
    # 계측 4원칙 ① — 수량 컬럼은 단위를 이름에 박는다(레그가 아니라 포지션).
    assert "broker_qty" not in cols, "단위 없는 이름을 쓰지 말 것"

    # 재호출이 안전해야 한다(init_all_dbs 는 매 기동 호출된다)
    D.init_broker_sync_recon_db()


# ── G3-2. 세 결과가 구분돼 적힌다 ──────────────────────────────────────────
def test_outcomes_are_distinct(monkeypatch):
    D, path = _tmp_db(monkeypatch)
    D.record_broker_sync_recon("MATCH", "synced", before_state="FLAT",
                               after_state="FLAT", reconciled_measured=True,
                               broker_qty_per_position=0)
    D.record_broker_sync_recon("MISMATCH", "synced", before_state="FLAT",
                               after_state="SHORT", reconciled_measured=True,
                               broker_qty_per_position=2,
                               broker_avg_price=421.5)
    D.record_broker_sync_recon("UNVERIFIED", "mock_blank_rows_keep_position",
                               before_state="LONG", after_state="LONG")

    rs = _rows(path)
    assert [r["outcome"] for r in rs] == ["MATCH", "MISMATCH", "UNVERIFIED"]

    # 방향은 대조가 성립한 행에만 붙는다 — UNVERIFIED 에 방향을 적으면
    # "LONG->LONG 이었다"를 관측하지 않은 채 주장하는 꼴이 된다.
    assert rs[0]["direction"] == "FLAT->FLAT"
    assert rs[1]["direction"] == "FLAT->SHORT"
    assert rs[2]["direction"] is None

    # 계측 4원칙 ② — 대조 여부가 같은 행에 플래그로 남는다.
    assert rs[0]["reconciled_measured"] == 1
    assert rs[1]["reconciled_measured"] == 1
    assert rs[2]["reconciled_measured"] == 0

    # 미측정은 0 이 아니라 NULL 이다.
    assert rs[1]["broker_avg_price"] == 421.5
    assert rs[2]["broker_qty_per_position"] is None
    assert rs[2]["broker_avg_price"] is None


# ── G3-3. 집계는 분모를 함께 돌려준다 ──────────────────────────────────────
def test_counts_expose_denominator(monkeypatch):
    D, _ = _tmp_db(monkeypatch)
    for _i in range(7):
        D.record_broker_sync_recon("MATCH", "synced", before_state="FLAT",
                                   after_state="FLAT", reconciled_measured=True)
    D.record_broker_sync_recon("MISMATCH", "synced", before_state="FLAT",
                               after_state="SHORT", reconciled_measured=True)
    for _i in range(2):
        D.record_broker_sync_recon("UNVERIFIED", "no_matching_row")

    c = D.broker_sync_recon_counts(days_back=30)
    assert c["attempts"] == 10, c          # 분모가 있어야 비율을 말할 수 있다
    assert c["match"] == 7
    assert c["mismatch"] == 1
    assert c["unverified"] == 2

    # 분모는 **대조가 성립한 건수**(7+1)다. UNVERIFIED 를 분모에 넣으면
    # "대조를 못 한 날"이 비율을 좋아 보이게 만든다.
    assert abs(c["mismatch_rate_of_reconciled"] - (1.0 / 8.0)) < 1e-9


def test_rate_is_none_when_nothing_reconciled(monkeypatch):
    """표본 없음을 0.0 으로 말하지 않는다(계측 4원칙 ②)."""
    D, _ = _tmp_db(monkeypatch)
    c = D.broker_sync_recon_counts(days_back=30)
    assert c["attempts"] == 0
    assert c["mismatch_rate_of_reconciled"] is None, "0.0 이면 '불일치 없음'으로 읽힌다"

    D.record_broker_sync_recon("UNVERIFIED", "balance_tr_none")
    c = D.broker_sync_recon_counts(days_back=30)
    assert c["attempts"] == 1
    assert c["mismatch_rate_of_reconciled"] is None


# ── G3-4. 모르는 값이 집계를 오염시키지 않는다 ─────────────────────────────
def test_unknown_outcome_is_quarantined(monkeypatch):
    D, path = _tmp_db(monkeypatch)
    D.record_broker_sync_recon("WEIRD", "synced", before_state="FLAT",
                               after_state="FLAT", reconciled_measured=True)
    r = _rows(path)[0]
    assert r["outcome"] == "UNVERIFIED"
    assert "unknown_outcome=WEIRD" in (r["detail"] or ""), r["detail"]
    # 조용히 버리지도, MATCH 로 끼워 넣지도 않는다(계측 4원칙 ③).
    assert D.broker_sync_recon_counts()["attempts"] == 1


# ── G3-5. 기록 실패가 예외로 새어나오지 않는다 ─────────────────────────────
def test_record_failure_is_swallowed(monkeypatch):
    import utils.db_utils as D

    def _boom(*a, **k):
        raise sqlite3.OperationalError("database is locked")
    monkeypatch.setattr(D, "execute", _boom, raising=False)
    monkeypatch.setattr(D, "fetchall", _boom, raising=False)

    # 재기동 경로 한복판이다 — 관측이 동기화를 깨뜨리면 안 된다.
    assert D.record_broker_sync_recon("MISMATCH", "synced") is False
    assert D.broker_sync_recon_counts()["attempts"] == 0   # 집계도 죽지 않는다


# ══════════════════════════════════════════════════════════════════════════
# 라이브 반영 0 — 이 계측은 매매 판단을 바꾸지 않는다
# ══════════════════════════════════════════════════════════════════════════

def _main_src():
    with io.open(_MAIN, encoding="utf-8") as f:
        return f.read()


def test_recorder_return_value_is_never_consumed():
    """호출부가 반환값으로 분기하면 계측이 매매 경로가 된다.

    `_ts_record_broker_sync_recon(...)` 은 **반드시 단독 표현식 문장**이어야 한다 —
    `if`/`while`/대입/`return`/`and`/`or` 의 피연산자로 쓰이면 안 된다.
    """
    bad = []
    for i, line in enumerate(_main_src().splitlines(), 1):
        s = line.strip()
        if "_ts_record_broker_sync_recon(" not in s:
            continue
        if s.startswith("#") or s.startswith("def ") or s.startswith("from "):
            continue
        if s.startswith("_ts_record_broker_sync_recon("):
            continue          # 단독 호출 — 정상
        bad.append((i, s))
    assert not bad, "반환값을 소비하는 호출부: %s" % (bad,)


def test_recorder_wrapper_swallows_everything(monkeypatch):
    """래퍼는 어떤 예외도 밖으로 내보내지 않고 None 을 돌려준다."""
    src = _main_src()
    m = re.search(
        r"def _ts_record_broker_sync_recon\(outcome, detail, \*\*kw\):\n"
        r"(?:.*\n)*?(?=\n\ndef )", src)
    assert m, "래퍼 함수를 찾지 못했다 — 이름이 바뀌었으면 이 테스트를 갱신할 것"
    body = m.group(0)
    assert "try:" in body and "except Exception" in body, body
    assert "return" not in body, "반환값을 만들면 소비될 여지가 생긴다"

    class _L(object):
        @staticmethod
        def debug(*a, **k):
            return None

    def _throw(*a, **k):
        raise RuntimeError("db down")

    import utils.db_utils as D
    monkeypatch.setattr(D, "record_broker_sync_recon", _throw, raising=False)

    ns = {"logger": _L}
    exec(compile(body, "<wrapper>", "exec"), ns)
    assert ns["_ts_record_broker_sync_recon"]("MATCH", "synced") is None


def test_all_terminating_branches_are_instrumented():
    """대사 원장의 값은 **빠짐없이 적히는 것**에 달려 있다.

    한 분기라도 빠지면 그 경우가 조용히 분모에서 사라져, 남은 비율이
    실제보다 좋아 보인다(계측 4원칙 ⑤).
    """
    src = _main_src()
    start = src.index("def _ts_sync_position_from_broker(self) -> None:")
    end = src.index("def _ts_sync_from_balance_payload(self, payload: dict)")
    body = src[start:end]

    for detail in ("missing_account_or_code", "balance_tr_none",
                   "mock_blank_rows_keep_position", "blank_as_flat",
                   "no_matching_row", "parse_failure", "synced"):
        assert '"%s"' % detail in body, "미계측 분기: %s" % detail

    # 종결 경로 = 이른 return 7개 + 끝까지 떨어지는 정상 종결 1개 = 8개.
    # 그중 계측 대상이 아닌 것은 **장외 스킵** 하나뿐이다(대사를 시도조차 안 했다).
    #   ⇒ 계측 호출 수 == return 수 - 1(장외 스킵) + 1(정상 종결) == return 수
    n_ret = len(re.findall(r"^\s+return\s*$", body, re.M))
    n_rec = body.count("_ts_record_broker_sync_recon(")
    assert n_rec == n_ret, (
        "return %d개 vs 계측 %d개 — 분기가 늘었는데 계측이 안 따라왔다"
        % (n_ret, n_rec))


def test_recon_ledger_is_not_read_by_decision_paths():
    """진입·청산·사이징·게이트가 이 원장을 읽지 않는다."""
    hits = []
    for sub in ("strategy", "model"):
        base = os.path.join(_ROOT, sub)
        for dirpath, _dirs, files in os.walk(base):
            for fn in files:
                if not fn.endswith(".py"):
                    continue
                p = os.path.join(dirpath, fn)
                with io.open(p, encoding="utf-8", errors="ignore") as f:
                    t = f.read()
                if ("broker_sync_recon" in t
                        or "_ts_record_broker_sync_recon" in t):
                    hits.append(os.path.relpath(p, _ROOT))
    assert not hits, "판단 경로가 관측 원장을 참조한다: %s" % (hits,)


def test_registered_in_init_all_dbs():
    import utils.db_utils as D
    path = D.__file__
    if path.endswith(".pyc"):
        path = path[:-1]
    with io.open(path, encoding="utf-8") as f:
        t = f.read()
    block = t[t.index("def init_all_dbs():"):]
    assert "init_broker_sync_recon_db()" in block[:800], \
        "init_all_dbs 에 등록되지 않으면 라이브에서 테이블이 안 생긴다"
