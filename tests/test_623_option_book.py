# -*- coding: utf-8 -*-
"""[MW0601 623차] 옵션 만기북(먼스리·목위클리·월위클리) — 순수 로직 불변식.

    conda run -n py37_32 python -m pytest tests/test_623_option_book.py -q
"""
import datetime as dt
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from collection.options import option_book as ob

# 2026-09-23 실제 KIS 마스터 행(발췌)
_MASTER = "\n".join([
    "1|A01612|KR4A016C0004|F 202612| |00000.00|1|2001|KOSPI200",
    "5|B01610A48|KR4B016AA487|C 202610 1,120.0|3|01120.00| |2001|KOSPI200",
    "6|C01610A48|KR4C016AA486|P 202610 1,120.0|2|01120.00| |2001|KOSPI200",
    "5|B01611A48|KR4B016BA485|C 202611 1,120.0|3|01120.00| |2001|KOSPI200",
    "L|B09FEWA49|KR4B09FEA490|위클리C 2609W4 1,120.0|3|01120.00| |2001|KOSPI200",
    "M|C09FEWA49|KR4C09FEA499|위클리P 2609W4 1,120.0|3|01120.00| |2001|KOSPI200",
    "L|B09FFWA49|KR4B09FFA497|위클리C 2610W1 1,120.0|3|01120.00| |2001|KOSPI200",
    "L|B09FE937|KR4B09FE9377|위클리C 2609W4   937.5|2|00937.50| |2001|KOSPI200",
    "N|BAFBZWA49|KR4BAFBZA490|위클리M C 2609W4 1,120.0|3|01120.00| |2001|KOSPI200",
    "D|B05610A48|KR4B056AA480|미니C 202610 1,120.0|3|01120.00| |2001|KOSPI200",
    "J|B06610A48|KR4B066AA488|C 202610 1,120.0|3|01120.00| |1001|KOSDAQ150",
])


def test_cybos_code_is_std_code_slice():
    # 먼스리 4,602/4,602 전수 일치로 확정한 규칙 (2026-09-23)
    assert ob.cybos_code("KR4B016AA487") == "B016AA48"
    assert ob.cybos_code("KR4B09FEA490") == "B09FEA49"   # 목위클 — OptionMst 조회 실측 성공
    assert ob.cybos_code("KR4BAFBZA490") == "BAFBZA49"   # 월위클 — 〃


def test_parse_keeps_only_three_kospi200_books():
    rows = ob.parse_master_text(_MASTER)
    assert {r["book"] for r in rows} == {"monthly", "weekly_thu", "weekly_mon"}
    assert all(r["code"][:3] in ("B01", "C01", "B09", "C09", "BAF") for r in rows)  # 미니·코스닥 제외
    m = [r for r in rows if r["book"] == "monthly"]
    assert {r["label"] for r in m} == {"2610", "2611"}    # CpOptionCode ym 과 같은 꼴
    w = [r for r in rows if r["code"] == "B09FE937"][0]
    assert w["strike"] == 937.5 and w["cp"] == "C" and w["label"] == "2609W4"


def test_nominal_expiry():
    assert ob.nominal_expiry("monthly", "2610") == dt.date(2026, 10, 8)      # 둘째 목
    assert ob.nominal_expiry("weekly_thu", "2609W4") == dt.date(2026, 9, 24)  # 넷째 목
    assert ob.nominal_expiry("weekly_thu", "2610W1") == dt.date(2026, 10, 1)
    assert ob.nominal_expiry("weekly_mon", "2609W4") == dt.date(2026, 9, 28)  # 넷째 월
    assert ob.nominal_expiry("weekly_mon", "junk") is None


def test_select_nearest_skips_nominally_expired():
    rows = ob.parse_master_text(_MASTER)
    lab, sel = ob.select_nearest(rows, "weekly_thu", dt.date(2026, 9, 23))
    assert lab == "2609W4" and len(sel) == 3
    lab, _ = ob.select_nearest(rows, "weekly_thu", dt.date(2026, 9, 28))   # 낡은 마스터 폴백 상황
    assert lab == "2610W1"
    assert ob.select_nearest(rows, "weekly_mon", dt.date(2026, 12, 1)) == (None, [])


def _snap(cp, k, oi, g, err=None):
    d = {"cp": cp, "strike": k, "oi": oi, "gamma": g, "code": "x"}
    if err:
        d["error"] = err
    return d


def test_compute_book_walls_and_totals():
    spot = 1120.0
    snaps = [_snap("C", 1120, 100, 0.01), _snap("C", 1130, 300, 0.008),
             _snap("P", 1110, 200, 0.009), _snap("P", 1100, 50, 0.005),
             _snap("C", 1140, 0, 0.0, err="dib_status=1")]
    s, strikes = ob.compute_book(snaps, spot)
    u = ob.OPTION_MULTIPLIER * spot / ob.GEX_BN
    assert abs(s["call_gex_bn"] - (100 * .01 + 300 * .008) * u) < 1e-9
    assert abs(s["put_gex_bn"] - (200 * .009 + 50 * .005) * u) < 1e-9
    assert abs(s["gex_bn"] - (s["call_gex_bn"] - s["put_gex_bn"])) < 1e-12
    assert s["call_wall"] == 1130 and s["put_wall"] == 1110
    assert s["n_target"] == 5 and s["n_valid"] == 4          # 탈락 가시화
    assert [r["strike"] for r in strikes] == [1100, 1110, 1120, 1130, 1140]
    assert strikes[-1]["call_gex_bn"] is None                 # 실패 행은 None (0 아님)


def test_compute_book_all_failed_is_unmeasured_not_zero():
    s, _ = ob.compute_book([_snap("C", 1120, 1, 1, err="x")], 1120.0)
    assert s["gex_bn"] is None and s["call_wall"] is None and s["n_valid"] == 0


def test_monthly_book_equals_existing_feature():
    """먼스리 북 합계 == 기존 `opt_gex_bn` — 같은 단위·같은 모집단이어야 한다."""
    from collection.options.option_chain_worker import _compute_gex
    raw = [{"call_put": "콜", "strike": 1120.0, "oi": 1063, "gamma": 0.0022},
           {"call_put": "풋", "strike": 1120.0, "oi": 155, "gamma": 0.0022},
           {"call_put": "콜", "strike": 1150.0, "oi": 4000, "gamma": 0.0017}]
    gex, _ = _compute_gex(raw, 1120.56)
    snaps = [dict(r, cp="C" if r["call_put"] == "콜" else "P") for r in raw]
    s, _ = ob.compute_book(snaps, 1120.56)
    assert abs(s["gex_bn"] - gex) < 1e-9


def test_save_and_load_roundtrip(tmp_path):
    db = str(tmp_path / "ob.db")
    s, strikes = ob.compute_book([_snap("C", 1120, 100, .01), _snap("P", 1110, 90, .01)], 1120.0)
    s.update(label="2609W4", expiry="2026-09-24", spot=1120.0, master_src="download", elapsed_ms=10)
    ob.save_books(db, "2026-09-23 14:30:00", {"weekly_thu": {"summary": s, "strikes": strikes}})
    ob.save_books(db, "2026-09-23 14:35:00", {"weekly_thu": {"summary": s, "strikes": strikes}})
    got = ob.load_day_snaps(db, "2026-09-23")
    assert list(got) == ["weekly_thu"] and len(got["weekly_thu"]) == 2
    assert got["weekly_thu"][0]["call_wall"] == 1120 and got["weekly_thu"][0]["label"] == "2609W4"
    assert ob.load_day_snaps(db, "2026-09-22") == {}
    assert ob.load_day_snaps(str(tmp_path / "none.db"), "2026-09-23") == {}


# ── 수집 경로 가드 (COM 없이 가짜 객체로) ────────────────────────────────

class _SlowMst(object):
    """BlockRequest 가 느린 상대 — 호출 수를 센다."""
    def __init__(self):
        self.calls = 0

    def SetInputValue(self, i, v):
        pass

    def BlockRequest(self):
        self.calls += 1

    def GetDibStatus(self):
        return 0

    def GetHeaderValue(self, i):
        return 10 if i == 99 else 1.0


class _RichQuota(object):
    """한도가 늘 넉넉하다 — 그래서 `_wait_quota` 는 절대 기다리지 않는다."""
    LimitRequestRemainTime = 0

    def GetLimitRemainCount(self, t):
        return 60


def _master_dir(tmp_path):
    d = tmp_path / "m"
    d.mkdir()
    (d / ob.MASTER_NAME).write_bytes(_MASTER.encode("cp949"))
    (d / (ob.MASTER_NAME + ".date")).write_text(dt.date.today().isoformat())
    return str(d)


def test_budget_applies_even_when_quota_is_plentiful(tmp_path, monkeypatch):
    """예산이 `_wait_quota` 안에서만 검사되면 한도가 넉넉할 때 무시된다(느린 BlockRequest 에 계속 던진다)."""
    from collection.options import option_chain_worker as w
    monkeypatch.setattr(ob, "select_nearest",
                        lambda rows, book, today: ("2609W4", [
                            {"book": book, "cp": "C", "label": "2609W4", "strike": 1120.0, "code": "X"}] * 5))
    mst = _SlowMst()
    out = w.collect_option_books(
        mst, _RichQuota(), 1120.0, [], "2610", "2026-09-23 10:00:00",
        {"db_path": str(tmp_path / "ob.db"), "master_dir": _master_dir(tmp_path),
         "window": 30.0, "reserve": 25, "budget_sec": -1.0})         # 예산 이미 소진
    assert mst.calls == 0
    assert out["books"]["weekly_thu"]["n_valid"] == 0
    assert out["books"]["weekly_thu"]["n_target"] == 5              # 탈락은 행으로 남는다
    assert out["books"]["weekly_thu"]["gex_bn"] is None             # 미측정 ≠ 0


def test_download_failure_backs_off(tmp_path, monkeypatch):
    """다운로드 실패 뒤에는 폴링마다 20초 타임아웃을 다시 물지 않는다(MW0602 는 마흐디 폴백이 없다)."""
    calls = []

    def _boom(*a, **k):
        calls.append(1)
        raise OSError("offline")
    monkeypatch.setattr(ob.urllib.request, "urlopen", _boom)
    monkeypatch.setattr(ob, "_last_dl_fail", None)
    d = str(tmp_path / "empty")
    assert ob.load_master(d, dt.date.today()) == ([], "none")
    assert ob.load_master(d, dt.date.today()) == ([], "none")
    assert len(calls) == 1
