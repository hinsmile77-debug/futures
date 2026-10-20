# -*- coding: utf-8 -*-
"""[MW0602 640차 ④] 지표 플러그인 계약 · 미래 참조 차단 · 레지스트리(출처 필수 · 검증 없이 장착 불가) · PIT 검증 통계 · 장중 가드."""
import datetime as _dt
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from strategy.shindong2_ai import indicators as IND  # noqa: E402
from strategy.shindong2_ai.indicators import i1_fx_path_slope as I1, i2_retail_cp_level as I2, i3_spot_foreign_persist as I3  # noqa: E402
import shindong2_research as RS  # noqa: E402


def test_1_discover_builtin_plugins_satisfy_contract():
    pl = IND.discover()
    assert pl["__errors__"] == {}
    assert {"I1", "I2", "I3"} <= set(pl)
    for k, mod in pl.items():
        if k == "__errors__":
            continue
        assert all(f in mod.META for f in IND.REQUIRED_META) and mod.META["sign"] in IND.SIGNS and callable(mod.compute)
        assert mod.META["prereg"]["min_days"] >= 20 and mod.META["prereg"]["hit_min"] >= 0.55     # 사전등록 문턱이 느슨해지지 않았나


def test_2_pure_functions_no_future_reference():
    ser = {"%02d:%02d" % (9 + i // 60, i % 60): float(i) for i in range(0, 180)}           # 09:00=0 … 11:59=179 (단조 증가)
    assert I1.compute_from(ser, "10:00") == 60.0 and I1.compute_from(ser, "09:30") is None     # 60분 창이 09:00 전이면 None
    assert I1.compute_from(ser, "11:00") == 60.0                                               # 11:59 값은 보지 않는다
    assert I1.compute_from({}, "10:00") is None
    sp = {"08:55": 50.0, "09:00": 100.0, "09:30": 400.0, "10:00": -200.0}
    assert I2.compute_from(sp, "09:30") == 300.0 and I2.compute_from(sp, "10:00") == -300.0 and I2.compute_from(sp, "08:59") is None
    assert I2.compute_from({"09:05": 10.0, "09:10": 30.0}, "09:10") == 20.0                     # 09:00 결손 → 그 뒤 첫 값이 기준
    s3 = [("09:%02d" % i, -100.0 - i) for i in range(0, 30)] + [("09:%02d" % i, 50.0) for i in range(30, 40)]
    assert I3.compute_from(s3, "09:29") == -1.0                                                 # 30분 내내 음수
    assert I3.compute_from(s3, "09:39") == 0.25                                                 # 뒤집힌 뒤 10/40 만 현재 부호
    assert I3.compute_from(s3[:5], "09:04") is None                                             # 소표본


def test_3_compute_one_lean_follows_sign():
    class M:
        META = dict(id="X", sign="contra", unit="u")

        @staticmethod
        def compute(day, upto):
            return 5.0
    assert IND.compute_one(M, "2026-10-20", "10:00")["lean"] == "매도"
    M.META["sign"] = "follow"
    assert IND.compute_one(M, "2026-10-20", "10:00")["lean"] == "매수"

    class Bad:
        META = dict(id="Y", sign="follow")

        @staticmethod
        def compute(day, upto):
            raise RuntimeError("db")
    r = IND.compute_one(Bad, "2026-10-20", "10:00")
    assert r["value"] is None and "계산 실패" in r["why"]


def test_4_registry_requires_source_and_verification_before_mount(tmp_path, monkeypatch):
    monkeypatch.setattr(RS, "LEARN_DIR", str(tmp_path))
    with pytest.raises(SystemExit):
        RS.add("I9", "t", "", "h")
    r = RS.add("I9", "헤지펀드 베이시스", "https://example.org/paper", "베이시스 확대 → 상승", formula="basis - ma20", inputs=["basis"])
    assert r["status"] == "후보" and r["implemented"] is False and "미구현" in r["history"][0]["why"]
    with pytest.raises(SystemExit):
        RS.set_status("I9", status="장착")                       # 플러그인 없음
    r1 = RS.add("I1", "x", "내부: raw", "h")
    assert r1["implemented"] is True and r1["sign"] == "follow"
    with pytest.raises(SystemExit):
        RS.set_status("I1", status="장착")                       # 검증 PASS 없음
    md = open(os.path.join(str(tmp_path), RS.REG_MD), encoding="utf-8").read()
    assert "| I9 | 후보 |" in md and "미구현" in md
    assert "I9 [후보·미구현]" in RS.registry_text()


def test_5_evaluate_pairs_stats_and_prereg():
    pre = dict(min_days=20, hit_min=0.55, p_max=0.05)
    r = RS.evaluate_pairs([1.0] * 10, [1.0] * 10, "follow", pre)
    assert r["verdict"] == "UNMEASURED" and "10 < 20" in r["why"]
    # 강한 신호: 값 부호 = 이후 수익 부호(약간의 잡음)
    import random
    rng = random.Random(1)
    vals = [rng.uniform(-1, 1) for _ in range(40)]
    fwd = [v * 3 + rng.uniform(-0.5, 0.5) for v in vals]
    r = RS.evaluate_pairs(vals, fwd, "follow", pre, perm=100)
    assert r["verdict"] == "PASS" and r["hit_rate"] >= 0.55 and r["ic"] > 0 and r["p_perm"] < 0.05 and r["noise_95"] < r["ic"]
    # 같은 자료를 contra 로 읽으면 FAIL(부호 반대)
    r2 = RS.evaluate_pairs(vals, fwd, "contra", pre, perm=100)
    assert r2["verdict"] == "FAIL"
    # 무작위: 노이즈 하한선 아래 → FAIL
    vals = [rng.uniform(-1, 1) for _ in range(40)]
    fwd = [rng.uniform(-1, 1) for _ in range(40)]
    r3 = RS.evaluate_pairs(vals, fwd, "follow", pre, perm=100)
    assert r3["verdict"] in ("FAIL",) and r3["n"] == 40
    # 0 값·None 은 제외(미측정 ≠ 0)
    r4 = RS.evaluate_pairs([None, 0.0] + [1.0] * 25, [1.0] * 27, "follow", pre, perm=10)
    assert r4["n"] == 25 and r4["n_all"] == 27


def test_6_guard_intraday_and_binom():
    with pytest.raises(SystemExit):
        RS.guard_intraday(_dt.datetime(2026, 10, 21, 10, 30))
    RS.guard_intraday(_dt.datetime(2026, 10, 21, 16, 0))
    RS.guard_intraday(_dt.datetime(2026, 10, 24, 10, 0))              # 토요일
    RS.guard_intraday(_dt.datetime(2026, 10, 21, 10, 30), force=True)
    assert RS.binom_two_sided(10, 20) == pytest.approx(1.0, abs=0.01)
    assert RS.binom_two_sided(18, 20) < 0.01
    assert RS.spearman([1, 2, 3, 4, 5], [2, 4, 6, 8, 10]) == pytest.approx(1.0)
    assert RS.spearman([1, 2, 3, 4, 5], [5, 4, 3, 2, 1]) == pytest.approx(-1.0)


def test_7_mounted_values_and_headless_scripts():
    assert RS.mounted_values("2026-10-20", "10:00") == [] or isinstance(RS.mounted_values("2026-10-20", "10:00"), list)
    run = open(os.path.join(ROOT, "scripts", "shindong2_run.ps1"), encoding="utf-8").read()
    assert "'research'" in run and "shindong2_research.py:*" in run and "$Phase -ne 'research'" in run
    tasks = open(os.path.join(ROOT, "scripts", "shindong2_tasks.ps1"), encoding="utf-8").read()
    assert "'Research'" in tasks and "Saturday" in tasks
