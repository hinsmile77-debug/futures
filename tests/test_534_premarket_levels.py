# -*- coding: utf-8 -*-
"""[MW0601 534차] 당일 맥점 예측 — 거리 모델·구조 모델 회귀 테스트.

근거: `docs/미륵이고도화3/당일맥점예측_거리모델_구조모델_구현가이드_2026-09-06.md`.

지키려는 불변식은 넷이다.

  ① **규칙이 문서와 같다** — M1/P1 수식, 경로 하한, 구간 분위, R̂ 하한·상한,
     매물대 봉우리·갭 변·병합·선택 컷.
  ② **지어내지 않는다** — 훈련 세션 30 미만 / 08:45 시가 결손 / 09:30 봉 부족이면
     값 대신 **미산출 + 사유**가 남는다(계측 4원칙 ②·③).
  ③ **굳히기** — 같은 (date, stage) 두 번째 저장은 무시된다(가이드 §4).
  ④ **관측 전용** — 진입·청산·사이징 코드가 맥점 모듈을 읽지 않는다(가이드 §11-1).
     이 테스트가 깨지면 누군가 맥점을 판단에 연결한 것이다.

Python 3.7.13 32-bit(py37_32)에서 돌아야 한다 — 3.8+ 문법을 쓰면 런타임에서 죽는다.
"""

import datetime
import io
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from features.levels import premarket_levels as PL
from features.levels import levels_store as LS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ────────────────────────────────────────────── 합성 봉 헬퍼

def _bars(open_, high, low, close, n=384, start_min=525):
    """08:45(525분)부터 n개. 첫 봉이 시가, 마지막 봉이 종가, 중간에 고·저를 심는다."""
    out = []
    for i in range(n):
        m = start_min + i
        t = "%02d:%02d" % (m // 60, m % 60)
        if i == 0:
            o, h, l, c = open_, open_, open_, open_
        elif i == n // 3:
            o = h = l = c = high
        elif i == 2 * n // 3:
            o = h = l = c = low
        elif i == n - 1:
            o = h = l = c = close
        else:
            o = h = l = c = open_
        out.append(PL.Bar(t=t, o=o, h=h, l=l, c=c, v=10))
    return out


def _summaries(n, base=300.0, rng=10.0):
    """ATR·경로가 채워진 합성 세션 n개.

    범위를 세션마다 흔든다(±30%) — 전부 같은 폭이면 잔차가 0이 돼 구간이 폭 0이
    되고, R̂ 스케일이 폭을 넓히는지조차 시험할 수 없다.
    """
    ss = []
    for i in range(n):
        o = base + i * 0.1
        r = rng * (1.0 + 0.3 * ((i * 7) % 11 - 5) / 5.0)
        u = r * (1.0 + 0.2 * ((i * 5) % 7 - 3) / 3.0)
        s = PL.SessionSummary(d=(datetime.date(2026, 1, 1)
                                 + datetime.timedelta(days=i)).isoformat(),
                              o=o, h=o + u, l=o - r, c=o + (u - r) / 2.0,
                              hp_t=u * 0.4, lp_t=r * 0.4, cp_t=(u - r) * 0.1)
        ss.append(s)
    PL.fill_derived(ss)
    return ss


# ────────────────────────────────────────────── ① 거리 모델 규칙

def test_atr_uses_only_prior_sessions():
    """ATR14 는 **그 세션 이전** 14세션의 TR 평균이다 — 당일을 포함하면 미래 누설."""
    ss = _summaries(20)
    assert PL.atr_of(ss, 0) is None          # 앞이 없으면 낼 수 없다
    assert PL.atr_of(ss, 4) is None          # 5세션 미만이면 None
    assert PL.atr_of(ss, 20) == pytest.approx(PL.atr_of(ss[:20], 20))


def test_stage1_point_estimate_is_open_plus_median_times_atr():
    ss = _summaries(60)
    p1 = PL.fit_stage1(ss)
    # 앞 세션은 직전 5세션이 없어 ATR 을 못 내고 훈련 표본에서 빠진다 — 정상
    assert p1 is not None and p1["n"] == len([x for x in ss if x.atr])
    o, atr = 400.0, 12.0
    d = PL.distance_stage1(p1, o, atr)
    assert d["high"] == pytest.approx(o + p1["med_u"] * atr)
    assert d["low"] == pytest.approx(o - p1["med_d"] * atr)
    # 구간은 항상 (하한, 상한) 순 — 저점 쪽은 부호가 뒤집혀도 정렬돼야 한다
    for k in ("high50", "high80", "low50", "low80"):
        assert d[k][0] <= d[k][1], k
    # 80% 구간은 50% 구간을 감싼다
    assert d["high80"][0] <= d["high50"][0] and d["high50"][1] <= d["high80"][1]
    assert d["low80"][0] <= d["low50"][0] and d["low50"][1] <= d["low80"][1]


def test_stage1_returns_none_below_min_train_sessions():
    """훈련 세션 30 미만이면 **내지 않는다**(가이드 §11-4) — 0 이나 근사치가 아니다."""
    # ATR 이 있는 세션만 센다 — 앞 5세션은 ATR 이 없어 빠진다
    assert PL.fit_stage1(_summaries(PL.MIN_TRAIN_SESSIONS + 4)) is None
    assert PL.fit_stage1(_summaries(PL.MIN_TRAIN_SESSIONS + 5)) is not None


def test_stage2_path_floor_never_predicts_below_realized():
    """09:30 예측은 이미 난 고·저보다 낮을 수 없다(경로 하한)."""
    ss = _summaries(80)
    p2 = PL.fit_stage2(ss, len(ss))
    assert p2 is not None
    o, atr = 400.0, 12.0
    # 09:30까지 이미 3ATR 이나 벌어진 극단 경로 — 회귀 예측치를 반드시 넘는다
    d = PL.distance_stage2(p2, o, atr, 0.0, 20.0, (3.0, 3.0, 0.0))
    assert d["high"] >= d["so_far_high"] - 1e-9
    assert d["low"] <= d["so_far_low"] + 1e-9
    # 회귀가 경로보다 낮게 부를 때 하한이 **실제로** 물리는지 — 계수를 0으로 눌러 확인
    flat = dict(p2, bu=[0.0] * len(p2["bu"]), bd=[0.0] * len(p2["bd"]))
    d2 = PL.distance_stage2(flat, o, atr, 0.0, 20.0, (3.0, 2.0, 0.0))
    assert d2["high"] == pytest.approx(o + 3.0 * atr)   # 예측 0 → 경로 3.0 채택
    assert d2["low"] == pytest.approx(o - 2.0 * atr)


def test_lad_fit_matches_median_regression_on_clean_line():
    import numpy as np
    X = np.array([[1.0, float(i)] for i in range(40)])
    y = X @ np.array([2.0, 0.5])
    beta = PL.lad_fit(X, y)
    assert beta[0] == pytest.approx(2.0, abs=1e-3)
    assert beta[1] == pytest.approx(0.5, abs=1e-3)


def test_rhat_scale_is_clipped_to_floor_and_cap():
    """하한 0.85 채택(가이드 §5-3) — 하한 1.0은 폭이 9~11% 넓어져 '넓혀서 맞춘 것'이 된다."""
    import math
    params = dict(beta=[1.0], med_r=1.0, n=60)   # R̂ = exp(x)
    assert PL.rhat_scale(params, [math.log(0.01)]) == pytest.approx(PL.RHAT_FLOOR)
    assert PL.rhat_scale(params, [math.log(100.0)]) == pytest.approx(PL.RHAT_CAP)
    assert PL.rhat_scale(params, [0.0]) == pytest.approx(1.0)
    assert PL.rhat_scale(None, [0.0]) is None          # 파라미터 없으면 None
    assert PL.rhat_scale(params, None) is None
    assert PL.rhat_scale(params, [0.0, 0.0]) is None   # 차원 불일치도 None


def test_rhat_scale_widens_bands_but_keeps_point_estimate():
    ss = _summaries(60)
    p1 = PL.fit_stage1(ss)
    plain = PL.distance_stage1(p1, 400.0, 12.0)
    scaled = PL.distance_stage1(p1, 400.0, 12.0, 1.5)
    assert scaled["high"] == pytest.approx(plain["high"])   # 점추정은 안 움직인다
    w_plain = plain["high80"][1] - plain["high80"][0]
    w_scaled = scaled["high80"][1] - scaled["high80"][0]
    assert w_scaled > w_plain
    # 스케일 전 원구간이 raw 로 함께 남는다 — 장후 채점이 두 구간을 나란히 센다(§5-2)
    assert scaled["raw"]["high80"] == pytest.approx(plain["high80"])
    assert plain["raw"] is None


# ────────────────────────────────────────────── ② 구조 모델 규칙

def test_volume_profile_peak_uses_dwell_time_not_volume():
    """매물대는 **머문 시간**으로 잰다 — 거래량이 몰린 봉이 봉우리를 만들면 안 된다."""
    # 300 에 오래 머물고(120분), 350 에 한 봉만 있으나 거래량이 1만 배
    bars = ([PL.Bar(t="09:%02d" % i, o=300.0, h=300.2, l=299.8, c=300.0, v=1)
             for i in range(60)]
            + [PL.Bar(t="10:%02d" % i, o=300.0, h=300.2, l=299.8, c=300.0, v=1)
               for i in range(60)]
            + [PL.Bar(t="11:00", o=350.0, h=350.0, l=350.0, c=350.0, v=1000000)])
    cands = PL.structural_candidates([("2026-09-01", bars)])
    peaks = [k for k, v in cands.items() if any(t.startswith("매물대") for t in v)]
    assert 300 in peaks
    assert 350 not in peaks


def test_gap_edges_detected_between_non_overlapping_sessions():
    a = [PL.Bar(t="09:00", o=300.0, h=310.0, l=295.0, c=305.0, v=1)]
    b = [PL.Bar(t="09:00", o=320.0, h=330.0, l=315.0, c=325.0, v=1)]   # 315 > 310
    cands = PL.structural_candidates([("2026-09-01", a), ("2026-09-02", b)])
    tags = [t for v in cands.values() for t in v]
    assert any(t.startswith("갭하변") for t in tags)
    assert any(t.startswith("갭상변") for t in tags)


def test_candidates_merge_within_merge_pt():
    """1.5pt 안의 후보는 한 레벨로 합쳐지고 근거 목록 길이가 '합류'가 된다."""
    prev = [PL.Bar(t="09:00", o=300.0, h=301.0, l=300.0, c=300.5, v=100)]
    cands = PL.structural_candidates([("2026-09-01", prev)])
    # 전일고 301 · 전일저 300 · VWAP 300.5 → 1.5pt 안이라 한 레벨로 병합
    assert len(cands) == 1
    assert len(list(cands.values())[0]) >= 3


def test_select_nearest_excludes_plus_minus_one_point_around_ref():
    merged = {295: ["a"], 299: ["b"], 300: ["c"], 301: ["d"], 305: ["e"], 310: ["f"]}
    ups, dns = PL.select_nearest(merged, 300.0)
    assert 300 not in ups and 300 not in dns
    assert 301 not in ups and 299 not in dns      # ±1pt 안은 어느 쪽도 아니다
    assert ups == [305, 310]
    assert dns == [295]


def test_opening_range_added_only_at_stage2():
    merged = {200: ["x"]}
    early = [PL.Bar(t="09:00", o=300.0, h=310.0, l=290.0, c=305.0, v=1)]
    out = PL.with_opening_range(merged, early, "09:30")
    tags = [t for v in out.values() for t in v]
    assert any(t.startswith("OR고") for t in tags)
    assert any(t.startswith("OR저") for t in tags)
    assert merged == {200: ["x"]}                 # 원본을 건드리지 않는다


def test_quarterly_expiry_window_flagged():
    # 2026-09 둘째 목요일 = 09-10
    assert PL.is_quarterly_expiry_window(datetime.date(2026, 9, 10), [])
    assert PL.is_quarterly_expiry_window(datetime.date(2026, 9, 11), ["2026-09-10"])
    assert not PL.is_quarterly_expiry_window(datetime.date(2026, 9, 4),
                                             ["2026-09-01", "2026-09-02"])


# ────────────────────────────────────────────── ② 지어내지 않는다

def _params(n=80):
    ss = _summaries(n)
    prev = ss[-1]
    return dict(prev=prev, atr=ss[-1].atr or 10.0, atr5=PL.atr_of(ss, len(ss), 5),
                p1=PL.fit_stage1(ss[-PL.TRAIN_SESSIONS:]), p2=PL.fit_stage2(ss, len(ss)),
                rhat1=PL.fit_rhat(ss, len(ss), False), rhat2=PL.fit_rhat(ss, len(ss), True),
                candidates={295: ["a"], 305: ["b"]}, warnings=[])


def test_stage_not_computed_when_open_bar_missing():
    """08:45 시가가 결손된 세션은 **미산출**이다 — 09:00 시가를 시가인 척 쓰지 않는다."""
    p = _params()
    late = [PL.Bar(t="09:%02d" % i, o=300.0, h=301.0, l=299.0, c=300.0, v=1)
            for i in range(0, 40)]
    for stage in ("0850", "0930"):
        res = LS.compute_stage(stage, "2026-09-07", late, p)
        assert res["out"] is None
        assert "미산출" in res["note"]


def test_stage0930_not_computed_with_too_few_bars():
    p = _params()
    few = [PL.Bar(t="08:%02d" % (45 + i), o=300.0, h=301.0, l=299.0, c=300.0, v=1)
           for i in range(3)]
    res = LS.compute_stage("0930", "2026-09-07", few, p)
    assert res["out"] is None and "봉" in res["note"]
    # 08:50 단계는 08:45 봉 하나면 낼 수 있다
    assert LS.compute_stage("0850", "2026-09-07", few, p)["out"] is not None


def test_distance_is_none_when_params_missing_but_structure_still_returned():
    """거리 모델 파라미터가 없어도 구조 후보는 낸다 — 반대로 값을 지어내지는 않는다."""
    p = _params()
    p["p1"] = None
    bars = _bars(300.0, 310.0, 290.0, 305.0, n=10)
    res = LS.compute_stage("0850", "2026-09-07", bars, p)
    assert res["out"]["distance"] is None
    assert res["out"]["structure"]["up"] or res["out"]["structure"]["down"]


def test_bars_from_candles_accepts_datetime_ts():
    """🔴 `candle["ts"]` 는 **datetime 객체**다 — 문자열로 가정하면 봉이 전부 사라진다.

    첫 판이 정확히 이 함정에 빠졌다: `ts[11:16]` 이 TypeError 를 내고 `except: pass`
    가 삼켜, 메모리 버퍼가 **항상 비어** 매일 DB 폴백으로만 돌 뻔했다. 조용히 도는
    폴백은 계측 4원칙 ④가 가장 경계하는 형태다.
    """
    base = datetime.datetime(2026, 9, 7, 8, 45)
    candles = [dict(ts=base + datetime.timedelta(minutes=i), open=300.0, high=301.0,
                    low=299.0, close=300.5, volume=10) for i in range(50)]
    bars = LS.bars_from_candles(candles, until="09:30")
    assert len(bars) == 46            # 08:45~09:30
    assert bars[0].t == "08:45" and bars[-1].t == "09:30"
    # 문자열 ts 도 그대로 받는다(DB 경로 호환)
    str_bars = LS.bars_from_candles([dict(ts="2026-09-07 08:45:00", open=1.0, high=1.0,
                                          low=1.0, close=1.0, volume=1)])
    assert str_bars and str_bars[0].t == "08:45"
    # OHLC 가 없는 봉은 지어내지 않고 버린다
    assert LS.bars_from_candles([dict(ts=base)]) == []


def test_main_buffer_uses_strftime_not_slice():
    """main.py 버퍼도 같은 함정을 피해야 한다 — 소스로 고정한다."""
    src = io.open(os.path.join(ROOT, "main.py"), encoding="utf-8").read()
    i = src.index("맥점 산출용 당일 봉 버퍼")
    block = src[i:i + 800]
    assert 'strftime("%H:%M")' in block
    assert "self._levels_day_bars.append" in block


# ────────────────────────────────────────────── ③ 굳히기 + DB

def test_freeze_second_save_is_ignored(tmp_path, monkeypatch):
    from config import settings
    from utils import db_utils

    db = str(tmp_path / "pml.db")
    monkeypatch.setattr(settings, "PREMARKET_LEVELS_DB", db, raising=False)
    monkeypatch.setattr(db_utils, "PREMARKET_LEVELS_DB", db, raising=False)
    db_utils.init_premarket_levels_db()

    p = _params()
    bars = _bars(300.0, 310.0, 290.0, 305.0, n=60)
    out = LS.compute_stage("0850", "2026-09-07", bars, p)["out"]
    assert db_utils.save_premarket_levels("2026-09-07", "0850", "08:50:01", out) is True

    tampered = dict(out)
    tampered["distance"] = dict(out["distance"])
    tampered["distance"]["high"] = 9999.0
    assert db_utils.save_premarket_levels("2026-09-07", "0850", "09:00:00",
                                          tampered) is False
    row = db_utils.fetch_premarket_levels("2026-09-07")["0850"]
    assert row["computed_at"] == "08:50:01"
    assert row["distance"]["high"] == pytest.approx(out["distance"]["high"])


def test_unmeasured_row_keeps_reason_and_null_values(tmp_path, monkeypatch):
    """미산출 행은 NULL + 사유다 — 0 으로 채워 '정상 산출'로 위장하지 않는다."""
    from config import settings
    from utils import db_utils

    db = str(tmp_path / "pml2.db")
    monkeypatch.setattr(settings, "PREMARKET_LEVELS_DB", db, raising=False)
    monkeypatch.setattr(db_utils, "PREMARKET_LEVELS_DB", db, raising=False)
    db_utils.init_premarket_levels_db()
    db_utils.save_premarket_levels("2026-09-07", "0930", "09:30:02", None,
                                   note="봉 부족 — 미산출", bars=2)
    row = db_utils.fetch_premarket_levels("2026-09-07")["0930"]
    assert row["distance"] is None
    assert row["ref"] is None
    assert "미산출" in row["note"]


def test_roundtrip_db_row_preserves_bands(tmp_path, monkeypatch):
    from config import settings
    from utils import db_utils

    db = str(tmp_path / "pml3.db")
    monkeypatch.setattr(settings, "PREMARKET_LEVELS_DB", db, raising=False)
    monkeypatch.setattr(db_utils, "PREMARKET_LEVELS_DB", db, raising=False)
    db_utils.init_premarket_levels_db()
    p = _params()
    bars = _bars(300.0, 310.0, 290.0, 305.0, n=60)
    out = LS.compute_stage("0850", "2026-09-07", bars, p)["out"]
    db_utils.save_premarket_levels("2026-09-07", "0850", "08:50:01", out)
    row = db_utils.fetch_premarket_levels("2026-09-07")["0850"]
    for k in ("high50", "high80", "low50", "low80"):
        assert row["distance"][k] == pytest.approx(out["distance"][k])
    assert row["structure"]["up"] == [list(x) for x in out["structure"]["up"]]


# ────────────────────────────────────────────── ④ 관측 전용 불변식

_DECISION_FILES = [
    "strategy/entry/checklist.py",
    "model/ensemble_decision.py",
    "strategy/position_sizer.py",
    "strategy/risk/toxicity_gate.py",
]


def test_levels_never_read_by_decision_paths():
    """🔴 진입·청산·사이징 코드가 맥점을 읽으면 안 된다(가이드 §11-1).

    마흐디 이력 반사실 검증에서 이 레벨로 진입을 막으면 손익이 나빠졌다
    (335건 −2.6M~−5.7M원). 관측·기록만 한다.
    """
    pat = re.compile(r"premarket_levels|levels_store|features\.levels")
    for rel in _DECISION_FILES:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            continue
        src = io.open(path, encoding="utf-8").read()
        assert not pat.search(src), "%s 가 맥점 모듈을 참조한다 — 관측 전용 위반" % rel


def test_main_hooks_are_wired_and_isolated():
    """main.py 훅이 살아 있고, 산출 결과가 판단으로 새지 않는다."""
    src = io.open(os.path.join(ROOT, "main.py"), encoding="utf-8").read()
    assert "self._premarket_levels_0850_done" in src
    assert "self._premarket_levels_0930_done" in src
    assert "_compute_premarket_levels" in src
    # 산출 메서드는 아무것도 돌려주지 않는다 — 반환값을 판단에 쓸 수 없게.
    assert "def _compute_premarket_levels(self, stage: str) -> None:" in src


def test_pure_module_is_python37_compatible():
    """py37_32 런타임 — 왈러스(3.8+)·`X | None`(3.10+)·`slots=True`(3.10+) 금지(§6-1).

    문자열 검색으로 재지 않는다 — 두 모듈의 문서 문자열이 이 금지 목록을 **설명**하고
    있어서 자기 문서에 걸린다(첫 판이 실제로 그렇게 걸렸다). AST 로 잰다:
      · `ast.parse` 가 통과하면 이 인터프리터의 문법으로 파싱된다는 뜻이고,
        py37_32 에서 이 테스트를 돌리는 것 자체가 3.8+ 문법 부재의 증거다.
      · `@dataclass(slots=...)` 는 데코레이터 AST 에서 직접 찾는다.
    """
    import ast
    for rel in ("features/levels/premarket_levels.py", "features/levels/levels_store.py"):
        src = io.open(os.path.join(ROOT, rel), encoding="utf-8").read()
        tree = ast.parse(src)          # 3.8+ 문법이면 py37 에서 여기서 터진다
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            for dec in node.decorator_list:
                if isinstance(dec, ast.Call):
                    for kw in dec.keywords:
                        assert kw.arg != "slots", "%s: %s 에 dataclass slots" % (rel, node.name)
        # PEP 604 유니온은 3.7 에서 파싱은 되지만(BinOp) 런타임 평가에서 터진다
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr) \
                    and isinstance(getattr(node, "right", None), ast.NameConstant) \
                    and node.right.value is None:
                raise AssertionError("%s 에 PEP 604 유니온(`X | None`)" % rel)


# ────────────────────────────────────────────── 대시보드 표시

def test_entry_panel_renders_levels():
    """패널이 값·미산출 사유를 모두 그린다 — 미산출을 '——' 로만 두면 안 된다."""
    pytest.importorskip("PyQt5")
    from PyQt5.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    from dashboard.main_dashboard import EntryPanel

    panel = EntryPanel()
    p = _params()
    bars = _bars(300.0, 310.0, 290.0, 305.0, n=60)
    out = LS.compute_stage("0850", "2026-09-07", bars, p)["out"]
    panel.update_premarket_levels({
        "0850": dict(distance=out["distance"], structure=out["structure"],
                     atr=out["atr"], note=None),
        "0930": dict(distance=None, structure=dict(up=[], down=[]),
                     note="09:30 이전 봉 2개(<5) — 미산출"),
    })
    _meta0, _hi0, _lo0 = panel._levels_dist_labels["0850"]
    assert _hi0.text().startswith("고 ") and "50%" in _hi0.text() and "80%" in _hi0.text()
    assert _lo0.text().startswith("저 ") and "50%" in _lo0.text() and "80%" in _lo0.text()
    assert "ATR" in _meta0.text()
    assert "미산출" in panel._levels_dist_labels["0930"][0].text()
    assert panel._levels_struct_labels["0850"][0].text().startswith("▲")
    assert panel._levels_struct_labels["0850"][1].text().startswith("▼")
    # 빈 입력에도 죽지 않는다(장전 대기 상태)
    panel.update_premarket_levels({})
    assert "이후 산출" in panel._levels_dist_labels["0850"][0].text()
    assert panel._levels_dist_labels["0850"][1].text() == "고 ——"
    del panel
