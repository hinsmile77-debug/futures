# -*- coding: utf-8 -*-
"""[MW0601 639차] 신동 규격 v2 개정 — 1차 목표가 진입가 뒤에 놓이는 결함.

재현(2026-09-29 라이브 MAIN R3 매수 4건)
-------------------------------------
| 진입 | 진입가 | 1차 | 진입가 대비 |
|---|---|---|---|
| 10:37 | 1091.22 | 1091.50 | +0.28 |
| 10:43 | 1091.90 | 1091.50 | **−0.40** |
| 10:59 | 1091.04 | 1091.50 | +0.46 |
| 11:19 | 1091.84 | 1091.50 | **−0.34** |

원인(v1 `engine.targets`): 최종 목표 후보 = 08:50 가장 먼 구조맥점(1092)을 「진입 방향에 있는가」
(`side*(x−e) > 0`)로만 걸렀다. −0.5 버퍼를 뺀 1091.50 은 진입가 뒤인데, 1차(1098.36)보다 가까워
**맞바꿈**이 이것을 1차 자리에 넣었다 — 1차 최소거리(`T1_MIN_DIST` 2pt)가 우회됐다.

무엇을 고정하나
---------------
A. 개정 절차 — 버전 · 채점 재시작일 · v1 이력.
B. 재현 — v1(`targets_v1`)은 결함을 그대로 재현하고, v2(`targets`)는 두 목표가 모두 최소거리 밖.
C. 불변식 — 임의 맥점·진입가에서 v2 목표는 진입가 **너머** `T1_MIN_DIST − TP_BUF` 이상, 1차가 최종보다 멀지 않다.
D. 결함이 없던 경우는 v1 과 같다(개정 범위 = 결함 경로뿐).
E. 조건부 러너 섀도(별도 사전등록)는 v1 목표에 고정된다.
F. 채점표 — 다른 규격 버전 행은 표본에서 빠지고 개수가 적힌다.

실행:
    conda run -n py37_32 python -m pytest tests/test_639_shindong_v2_target_inversion.py -q
"""
import inspect
import os
import random
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import pytest  # noqa: E402

from strategy.shindong import engine, spec  # noqa: E402


# ── A ────────────────────────────────────────────────────────────────────
def test_amendment_registered():
    assert spec.SPEC_VERSION == "SD-2026-09-29-v2"
    assert spec.SPEC_VERSION_PREV == "SD-2026-09-24-v1"
    assert spec.V1_SCORING == ("2026-09-28", "2026-09-29")
    # 채점은 새 버전 첫날부터 다시 센다(사전등록 §6-3) — R3 중단 판정 10거래일도 재시작
    assert spec.SCORING_START == "2026-09-30"
    assert spec.X4NF_SCORING_START == "2026-09-30"
    assert spec.LATE_SHADOW_START == {"SHADOW_X4NF": "2026-09-30", "SHADOW_TR44": "2026-09-30",
                                      "SHADOW_X4NFA": "2026-09-30"}   # 598차 체리픽 섀도
    # 값은 하나도 바뀌지 않았다 — 바뀐 것은 판정 동작(최종 후보 최소거리)이다
    assert (spec.T1_MIN_DIST, spec.TP_BUF) == (2.0, 0.5)


def test_amendment_documented():
    doc = os.path.join(_ROOT, "docs", "신동거래", "신동_개정_v2_1차목표역전_20260929.md")
    assert os.path.exists(doc)
    pre = open(os.path.join(_ROOT, "docs", "신동거래", "신동_사전등록_20260924.md"), encoding="utf-8").read()
    assert "SD-2026-09-29-v2" in pre                      # §6-1 개정 이력에 올라갔다


# ── B ────────────────────────────────────────────────────────────────────
def _levels_0929():
    """2026-09-29 08:50 구조맥점 + 09:30 이후 1차 후보(거리맥점 끝 1098.855)를 최소로 재구성."""
    lv = {"0850": {"struct_up": "[]", "struct_down": "[]",
                   "dist_low": 1074.33, "dist_high": 1098.855,
                   "low80_lo": 1061.4241, "high80_hi": 1101.3725}}
    L = engine.prepare_levels(lv)
    L["0850"]["S"] = [1071.0, 1074.0, 1080.0, 1088.0, 1090.0, 1092.0]
    return L


@pytest.mark.parametrize("e", [1091.22, 1091.90, 1091.04, 1091.84])
def test_v1_reproduces_inversion(e):
    t1, t2 = engine.targets_v1(_levels_0929(), "10:40", 1, e)
    assert t1 == pytest.approx(1091.5)                   # 라이브 기록과 같은 1차
    assert t1 - e < spec.T1_MIN_DIST - spec.TP_BUF       # 최소거리 위반(음수 포함)


@pytest.mark.parametrize("e", [1091.22, 1091.90, 1091.04, 1091.84])
def test_v2_fixes_inversion(e):
    t1, t2 = engine.targets(_levels_0929(), "10:40", 1, e)
    # 1092 는 2pt 안이라 최종 후보에서 빠지고 → 80% 거리맥점 끝 1101.37 − 0.5
    assert (t1, t2) == (pytest.approx(1098.355), pytest.approx(1100.8725))
    assert t1 - e >= spec.T1_MIN_DIST - spec.TP_BUF


def test_v2_mirror_short():
    L = _levels_0929()
    L["0850"]["dist_low"] = 1070.0
    L["0850"]["low80_lo"] = 1066.0
    # 매도 1071.4: 아래쪽 가장 먼 구조맥점 1071 은 0.4pt — v1 은 1071.5(진입가 **위**)를 1차로 쓴다
    v1 = engine.targets_v1(L, "10:40", -1, 1071.4)
    assert v1[0] == pytest.approx(1071.5)
    t1, t2 = engine.targets(L, "10:40", -1, 1071.4)
    assert (t1, t2) == (pytest.approx(1066.5), pytest.approx(1066.5))   # 1차 후보 1070 은 1.4pt → 없음 → 최종이 1차


def test_v2_no_target_when_nothing_far_enough():
    L = _levels_0929()
    L["0850"]["dist_high"] = 1092.5
    L["0850"]["high80_hi"] = 1093.0
    assert engine.targets(L, "10:40", 1, 1091.9) == (None, None)       # 목표 없음 — 가짜 목표를 만들지 않는다


# ── C ────────────────────────────────────────────────────────────────────
def test_v2_invariants_random():
    rnd = random.Random(639)
    lim = spec.T1_MIN_DIST - spec.TP_BUF
    for _ in range(3000):
        base = 1000.0 + rnd.uniform(-50, 50)
        lv = {"0850": {"struct_up": "[]", "struct_down": "[]",
                       "dist_low": base - rnd.uniform(0, 15), "dist_high": base + rnd.uniform(0, 15),
                       "low80_lo": base - rnd.uniform(0, 25), "high80_hi": base + rnd.uniform(0, 25)}}
        L = engine.prepare_levels(lv)
        L["0850"]["S"] = sorted(round(base + rnd.uniform(-20, 20)) for _ in range(rnd.randint(0, 8)))
        side = rnd.choice((1, -1))
        e = round(base + rnd.uniform(-5, 5), 2)
        t1, t2 = engine.targets(L, "10:00", side, e)
        for x in (t1, t2):
            assert x is None or side * (x - e) >= lim - 1e-9, (side, e, t1, t2, L["0850"]["S"])
        if t1 is not None and t2 is not None:
            assert side * (t2 - t1) >= -1e-9                  # 1차가 최종보다 멀지 않다
        assert t1 is not None or t2 is None                  # 1차가 없으면 최종도 없다(최종이 1차로 올라간다)


def test_v2_x4_inherits_fix():
    # X4NF 는 targets 를 부른다 — 역전된 1차가 「현행이 더 가깝다」로 살아남지 않는다
    for e in (1091.22, 1091.90, 1091.04, 1091.84):
        x1, _ = engine.targets_x4(_levels_0929(), "10:40", 1, e)
        assert x1 - e >= spec.T1_MIN_DIST - spec.TP_BUF


# ── D ────────────────────────────────────────────────────────────────────
def test_v2_equals_v1_when_far_level_is_far():
    rnd = random.Random(6391)
    same = 0
    for _ in range(3000):
        base = 1000.0 + rnd.uniform(-50, 50)
        lv = {"0850": {"struct_up": "[]", "struct_down": "[]",
                       "dist_low": base - rnd.uniform(0, 15), "dist_high": base + rnd.uniform(0, 15),
                       "low80_lo": base - rnd.uniform(0, 25), "high80_hi": base + rnd.uniform(0, 25)}}
        L = engine.prepare_levels(lv)
        L["0850"]["S"] = sorted(round(base + rnd.uniform(-20, 20)) for _ in range(rnd.randint(0, 8)))
        side = rnd.choice((1, -1))
        e = round(base + rnd.uniform(-5, 5), 2)
        far = [x for x in L["0850"]["S"] if side * (x - e) > 0]
        fb = L["0850"]["low80_lo"] if side < 0 else L["0850"]["high80_hi"]
        # 결함 경로 밖: 최종 후보(가장 먼 구조맥점, 없으면 80% 끝)가 2pt 이상 떨어져 있다
        cand = (min(far) if side < 0 else max(far)) if far else fb
        if side * (cand - e) >= spec.T1_MIN_DIST:
            assert engine.targets(L, "10:00", side, e) == engine.targets_v1(L, "10:00", side, e)
            same += 1
    assert same > 1000


# ── E ────────────────────────────────────────────────────────────────────
def test_runner_shadow_pinned_to_v1():
    from strategy.shindong import mireuk_runner as R
    src = inspect.getsource(R)
    assert "E.targets_v1(" in src
    assert "E.targets(" not in src
    assert R.RUNNER_VERSION == "SDR-2026-09-24-v1"         # 러너 사전등록은 그대로


# ── F ────────────────────────────────────────────────────────────────────
def test_scorecard_excludes_other_version(tmp_path):
    import importlib.util
    sp = importlib.util.spec_from_file_location(
        "shindong_scorecard", os.path.join(_ROOT, "scripts", "shindong_scorecard.py"))
    sc = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(sc)
    from strategy.shindong import store
    db = str(tmp_path / "sd.db")
    tr = {"side": 1, "entry_ts": "10:43", "entry_px": 1091.9, "stop_init": 1088.5,
          "t1": 1098.355, "t2": 1100.8725, "status": "CLOSED", "exit_ts": "11:00", "stop_now": 1088.5,
          "rule": "R3", "touch_level": 1090.0, "touch_ts": "10:42",
          "legs": [{"leg": 1, "open": False, "ts": "11:00", "px": 1088.5, "reason": "SL",
                    "pts": -3.4, "net": -170000.0},
                   {"leg": 2, "open": False, "ts": "11:00", "px": 1088.5, "reason": "SL",
                    "pts": -3.4, "net": -170000.0}]}
    res = {"decision": {"pm_sp": 34.0, "bias": 0, "r2": None, "r2_ts": None, "notes": []}, "trades": [tr]}
    store.save_day(db, "2026-09-30", "MAIN", "wk_thu", "", res, "15:08", spec.SPEC_VERSION_PREV,
                   source="backfill")     # 재기동 전 옛 프로세스가 남긴 행이라 치자
    store.save_day(db, "2026-10-01", "MAIN", "wk_thu", "", res, "15:08", spec.SPEC_VERSION,
                   source="backfill")
    txt = sc.build(db, spec.SCORING_START)
    assert "다른 규격 버전 행 **1건**(SD-2026-09-24-v1) — 표본 제외" in txt
    assert "판정 기록 거래일: **1일**" in txt
