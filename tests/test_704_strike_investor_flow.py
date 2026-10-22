# -*- coding: utf-8 -*-
"""[MW0601 704차] CpSvr9842 행사가 × 투자자 수집기 회귀 가드.

2026-10-22 실측에서 명세와 어긋난 두 가지와 운영 조건을 고정한다:
- 명세 「연속조회 없음」은 틀렸다 — 차근월이 2쪽으로 온다 → 루프를 돈다.
- 인덱스 2 기관계는 Σ(3–10) 소계 — 대사식이 그것을 반영한다.
- 실계좌 전용 — 등급 차단이면 행을 쓰지 않고, 그날 다시 부르지 않는다(미측정 ≠ 0).
- 저장은 「첫 스냅샷 전체 + 이후 바뀐 행만」, 재구성은 「그 시각 이전 최신 행, 없으면 0」.
"""
import datetime
import io
import os
import sqlite3

import pytest

from collection.cybos import strike_investor_flow as sif_mod
from collection.cybos.strike_investor_flow import StrikeInvestorFlow, inv_check

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

Z12 = [0] * 12


def _q(ind=0, frn=0, sec=0, corp=None):
    """기관계(2)=증권(3) 소계, 합 0 이 되게 기타법인(11)으로 맞춘다."""
    q = [0] * 12
    q[0], q[1], q[3] = ind, frn, sec
    q[2] = sec
    q[11] = -(ind + frn + sec) if corp is None else corp
    return q


def _row(code, qty):
    return (code, qty, [0.5] * 12, [1.0] * 12, [0.0] * 12)


class FakeObj(object):
    """CpSvr9842 흉내 — responses[(market, month)] = [page_rows, ...]"""

    def __init__(self, responses, raise_msg=None):
        self.responses = responses
        self.raise_msg = raise_msg
        self.inputs = {}
        self.calls = 0
        self._page = -1
        self._fresh = True

    def SetInputValue(self, i, v):
        self.inputs[i] = v
        self._fresh = True

    def BlockRequest(self):
        self.calls += 1
        if self.raise_msg:
            raise Exception(self.raise_msg)
        self._page = 0 if self._fresh else self._page + 1
        self._fresh = False

    def _pages(self):
        return self.responses[(chr(self.inputs[0]), chr(self.inputs[1]))]

    def GetDibStatus(self):
        return 0

    def GetDibMsg1(self):
        return ""

    def GetHeaderValue(self, i):
        return len(self._pages()[self._page])

    def GetDataValue(self, f, i):
        return self._pages()[self._page][i][f]

    @property
    def Continue(self):
        return self._page + 1 < len(self._pages())


class FakeCy(object):
    def __init__(self, remain=60):
        self.remain = remain

    def GetLimitRemainCount(self, t):
        return self.remain


MASTER = {
    "B016B740": ("C", "2611", 740.0), "B016B742": ("C", "2611", 742.5),
    "B016BA01": ("C", "2611", 1002.5), "C016B740": ("P", "2611", 740.0),
}


def _mk(tmp_path, responses, remain=60, raise_msg=None, months=("1",)):
    s = StrikeInvestorFlow(str(tmp_path / "sif.db"), months=months)
    fake = FakeObj(responses, raise_msg)
    s._fake = fake
    s._obj_factory = lambda: fake
    s._cy = FakeCy(remain)

    def _load(today, force=False):
        s._master, s._master_day = dict(MASTER), today
    s._load_master = _load
    return s


def _status(db):
    con = sqlite3.connect(db)
    r = con.execute("SELECT snap_hm,cp,month,ok,full,rows_total,rows_stored,pages,unmapped,inv_bad,msg "
                    "FROM strike_investor_flow_status ORDER BY snap_hm,cp").fetchall()
    con.close()
    return r


def _count(db):
    con = sqlite3.connect(db)
    n = con.execute("SELECT COUNT(*) FROM strike_investor_flow").fetchone()[0]
    con.close()
    return n


T1 = datetime.datetime(2026, 10, 23, 10, 0, 5)
T2 = datetime.datetime(2026, 10, 23, 10, 1, 5)


def test_inv_check_institution_is_subtotal():
    assert inv_check(_q(ind=6, frn=55))                 # 6 + 55 + 0 + (-61) = 0
    q = _q(ind=1, frn=2, sec=3)
    assert inv_check(q)
    assert sum(q) != 0                                  # 12칸 단순합은 기관 이중계상
    q[2] = 0
    assert not inv_check(q)                             # 소계가 깨지면 위반


def test_continuation_pages_are_merged(tmp_path):
    resp = {("2", "1"): [[_row("B016B740", _q(1, -1))], [_row("B016B742", _q(2, -2))]],
            ("3", "1"): [[_row("C016B740", Z12)]]}
    s = _mk(tmp_path, resp)
    rows, pages, trunc = s._query("2", "1")
    assert pages == 2 and not trunc and [r["code"] for r in rows] == ["B016B740", "B016B742"]


def test_first_snapshot_full_then_changes_only_and_reconstruct(tmp_path):
    resp = {("2", "1"): [[_row("B016B740", _q(1, -1)), _row("B016B742", Z12)]],
            ("3", "1"): [[_row("C016B740", Z12)]]}
    s = _mk(tmp_path, resp)
    r1 = s.fetch_and_store(T1)
    assert r1["ok"] and r1["stored"] == 3                # 첫 스냅샷 = 전 행(0 행 포함)
    # 742 만 바뀐다
    resp[("2", "1")] = [[_row("B016B740", _q(1, -1)), _row("B016B742", _q(5, -5))]]
    r2 = s.fetch_and_store(T2)
    assert r2["ok"] and r2["stored"] == 1
    st = _status(s.db_path)
    assert [x[4] for x in st] == [1, 1, 0, 0]            # full 플래그: 첫 회차만
    snap = s.snapshot_at("2026-10-23", "10:01", "C")
    assert snap[742.5]["qty"][0] == 5 and snap[740.0]["qty"][0] == 1
    snap0 = s.snapshot_at("2026-10-23", "10:00", "C")
    assert snap0[742.5]["qty"][0] == 0                  # 그 시각 값으로 재구성


def test_snapshot_before_any_ok_is_unmeasured(tmp_path):
    resp = {("2", "1"): [[_row("B016B740", Z12)]], ("3", "1"): [[_row("C016B740", Z12)]]}
    s = _mk(tmp_path, resp)
    s.fetch_and_store(T1)
    assert s.snapshot_at("2026-10-23", "09:59", "C") is None   # None ≠ 빈 dict(0)


def test_blocked_writes_no_rows_and_stops_for_the_day(tmp_path):
    msg = "고객님의 계좌등급으로는 CCpSvr9842 시세데이터를 받는 데는 제한이 있습니다"
    s = _mk(tmp_path, {}, raise_msg=msg)
    r = s.fetch_and_store(T1)
    assert r["skipped"] == "blocked" and s.blocked_day == "2026-10-23"
    assert _count(s.db_path) == 0
    st = _status(s.db_path)
    assert st and st[0][3] == 0 and st[0][10].startswith("BLOCKED")
    calls = s._fake.calls
    s.fetch_and_store(T2)
    assert s._fake.calls == calls                        # 그날은 다시 부르지 않는다


def test_quota_skip_records_reason_without_request(tmp_path):
    s = _mk(tmp_path, {}, remain=10)
    r = s.fetch_and_store(T1)
    assert r["skipped"] == "quota" and s._fake.calls == 0
    assert all(x[3] == 0 and x[10].startswith("SKIP_QUOTA") for x in _status(s.db_path))


def test_unmapped_code_is_counted_and_strike_null(tmp_path):
    resp = {("2", "1"): [[_row("B016ZZZZ", _q(1, -1))]], ("3", "1"): [[_row("C016B740", Z12)]]}
    s = _mk(tmp_path, resp)
    r = s.fetch_and_store(T1)
    assert not r["ok"] and any("미매핑" in e for e in r["errors"])
    con = sqlite3.connect(s.db_path)
    k = con.execute("SELECT strike FROM strike_investor_flow WHERE code='B016ZZZZ'").fetchone()[0]
    con.close()
    assert k is None                                    # 문자열에서 행사가를 추측하지 않는다


def test_inv_violation_is_reported(tmp_path):
    bad = _q(1, -1)
    bad[2] = 7                                          # 소계 깨짐
    resp = {("2", "1"): [[_row("B016B740", bad)]], ("3", "1"): [[_row("C016B740", Z12)]]}
    s = _mk(tmp_path, resp)
    r = s.fetch_and_store(T1)
    assert not r["ok"] and any("주체 대사 위반" in e for e in r["errors"])


# ── 설정 · 배선 ───────────────────────────────────────────────────────────

def _read(p):
    return io.open(os.path.join(ROOT, p), encoding="utf-8").read()


def test_settings_off_on_dev_and_keys_exist():
    from config import settings
    assert settings.STRIKE_INVESTOR_FLOW_ENABLED is False     # dev: MW0602 프로브 전까지 꺼짐(이식 메모 §3)
    assert settings.STRIKE_INVESTOR_FLOW_MONTHS == ("1",)
    assert settings.STRIKE_INVESTOR_FLOW_DB.endswith("strike_investor.db")
    assert settings.STRIKE_INVESTOR_FLOW_DB != settings.WEEKLY_OPTION_FLOW_DB


def test_main_wiring_after_weekly_flow_and_explicit_init():
    src = _read("main.py")
    for attr in ("self._strike_investor_flow = None", "self._sif_last_ts = None",
                 "self._sif_warned = False"):
        assert attr in src
    i_w = src.index("self._fetch_weekly_option_flow(now)\n")
    i_s = src.index("self._fetch_strike_investor_flow(now)")
    assert i_w < i_s                                    # 보조 수집은 7222 뒤
    body = src[src.index("def _fetch_strike_investor_flow"):]
    body = body[:body.index("\n    def ")]
    assert "runtime_settings" in body and "getattr(settings" not in body


def test_module_never_parses_strike_from_code():
    src = _read("collection/cybos/strike_investor_flow.py")
    assert "CpOptionCode" in src
    assert "code[5:" not in src and "code[-3:" not in src


# ── 704차 후속 첫 실행에서 드러난 결함 (2026-10-22 장후) ──────────────────────

def test_normalize_cp_accepts_korean_labels():
    """CpOptionCode 필드 2 는 '콜'/'풋' 이다 — 'C'/'P' 만 받으면 콜 343행 전부 미매핑."""
    from collection.cybos.strike_investor_flow import normalize_cp
    assert normalize_cp("콜") == "C" and normalize_cp("풋") == "P"
    assert normalize_cp("C") == "C" and normalize_cp("p") == "P"
    assert normalize_cp("") is None


def test_empty_response_is_failure_not_zero(tmp_path):
    """풋이 status=0 · 0행으로 조용히 왔다 — 보유 0 으로 쓰면 안 된다."""
    resp = {("2", "1"): [[_row("B016B740", _q(1, -1))]], ("3", "1"): [[]]}
    s = _mk(tmp_path, resp)
    r = s.fetch_and_store(T1)
    assert not r["ok"] and any("빈 응답" in e for e in r["errors"])
    st = {x[1]: x for x in _status(s.db_path)}
    assert st["P"][3] == 0 and st["P"][10] == "EMPTY"
    assert s.snapshot_at("2026-10-23", "10:00", "P") is None     # 풋은 미측정


def test_new_com_object_per_request():
    """같은 객체 재사용 시 두 번째 조회(풋)가 0행 — 요청마다 새로 만든다."""
    src = _read("collection/cybos/strike_investor_flow.py")
    body = src[src.index("    def _get_obj(self):"):]
    body = body[:body.index("\n    def ")]
    assert "return Dispatch(_PROGID)" in body and "self._obj =" not in body


def test_snapshot_task_waited_by_eod_cleanup():
    """16:30 세션 정리가 스냅샷(COM) 끝까지 기다려야 한다 — 목록에 없으면 세션을 끊는다."""
    if not os.path.exists(os.path.join(ROOT, "scripts/eod_session_cleanup.ps1")):
        pytest.skip("eod_session_cleanup.ps1 은 MW0601 전용 — dev 에 없다")
    src = _read("scripts/eod_session_cleanup.ps1")
    line = [l for l in src.splitlines() if l.startswith("$ComScripts")][0]
    assert "strike_investor_snapshot" in line


def test_task_scripts_are_pure_ascii():
    for p in ("scripts/eod_session_cleanup.ps1", "scripts/strike_investor_snapshot_task.ps1"):
        if not os.path.exists(os.path.join(ROOT, p)):
            continue
        raw = io.open(os.path.join(ROOT, p), "rb").read()
        assert all(b < 0x80 for b in raw), p           # PS 5.1 은 BOM 없는 파일을 ANSI 로 읽는다


def test_snapshot_refuses_today_before_close():
    src = _read("scripts/strike_investor_snapshot.py")
    assert "datetime.time(15, 50)" in src and "is_trading_day" in src
