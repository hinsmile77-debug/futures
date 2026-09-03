# -*- coding: utf-8 -*-
"""[MW0601 529차] 스윙 위치 피처 — 계산·워밍업·기록 전용 규율 회귀 테스트.

배경: 2026-09-03 C1~C4가 60분 레그 끝(스윙 극단에서 6.6~10 ATR 달린 뒤, 극단 0.6~1.3 ATR 안쪽)의
순방향 진입이었는데, 기존 연장폭 피처는 "N분 전 종가 한 점" 대비라 V자 되돌림 뒤에는 0 근방으로
나왔다(C1: ext_60m 0.28 vs 스윙 대비 7.1). 이 피처는 창 안의 실제 최고/최저 대비 거리와 극단 이후
경과 봉 수를 남긴다. **기록 전용** — 진입·사이징 소비자가 없어야 한다.

못박는 것
1. 순수 함수 산식(거리·경과 봉·ready) 2. 워밍업은 0으로 위장하지 않고 ready=False 3. 동률 극단은
최근 것 기준 4. 클립 5. 소비자 0곳(checklist·sizer·main 진입 경로에 키 참조 없음) 6. (DB 있으면)
2026-09-03 C1~C4 재현값이 528차 조사 수치와 일치.

실행: pytest tests/test_529_swing_features.py
"""
import os
import re
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
os.environ.setdefault("MIREUK_TEST_MODE", "1")

from features.feature_builder import compute_swing_features  # noqa: E402
from config import settings  # noqa: E402

KEYS = ("swing_high_60m", "swing_low_60m", "dist_to_high_60m_atr", "dist_to_low_60m_atr",
        "bars_since_high_60m", "bars_since_low_60m", "swing_ready_60m")


def test_basic_geometry():
    highs = [100 + i * 0.1 for i in range(60)]          # 단조 상승, 최고가 = 마지막 봉
    lows = [99.5 + i * 0.1 for i in range(60)]
    f = compute_swing_features(highs, lows, close=105.0, atr=0.5, lookbacks=(60,))
    for k in KEYS:
        assert k in f, k
    assert f["swing_ready_60m"] is True
    assert f["swing_high_60m"] == highs[-1] and f["swing_low_60m"] == lows[0]
    assert f["bars_since_high_60m"] == 0 and f["bars_since_low_60m"] == 59
    assert abs(f["dist_to_high_60m_atr"] - max(highs[-1] - 105.0, 0) / 0.5) < 1e-9
    assert abs(f["dist_to_low_60m_atr"] - (105.0 - lows[0]) / 0.5) < 1e-9


def test_warmup_is_flagged_not_zeroed():
    f = compute_swing_features([100.5, 101.0], [99.5, 100.2], close=100.8, atr=0.5, lookbacks=(60,))
    assert f["swing_ready_60m"] is False
    assert f["swing_high_60m"] == 101.0 and f["swing_low_60m"] == 99.5   # 부분 창으로는 계산된다
    e = compute_swing_features([], [], close=100.0, atr=0.5, lookbacks=(60,))
    assert e["swing_ready_60m"] is False and e["dist_to_high_60m_atr"] == 0.0


def test_atr_zero_means_not_ready():
    f = compute_swing_features([1.0] * 60, [0.5] * 60, close=0.8, atr=0.0, lookbacks=(60,))
    assert f["swing_ready_60m"] is False and f["dist_to_low_60m_atr"] == 0.0


def test_tie_uses_most_recent_extreme_and_clip():
    highs = [10.0] * 30 + [9.0] * 29 + [10.0]     # 최고가 동률 — 마지막 봉이 최근
    lows = [1.0] + [5.0] * 59
    f = compute_swing_features(highs, lows, close=9.5, atr=0.01, lookbacks=(60,), clip_atr=20.0)
    assert f["bars_since_high_60m"] == 0
    assert f["bars_since_low_60m"] == 59
    assert f["dist_to_low_60m_atr"] == 20.0          # (9.5-1)/0.01 = 850 → 클립


def test_settings_and_multiple_lookbacks():
    assert settings.SWING_FEATURE_LOOKBACKS_MIN and 60 in settings.SWING_FEATURE_LOOKBACKS_MIN
    f = compute_swing_features([1.0] * 70, [0.5] * 70, 0.9, 0.1, lookbacks=(20, 60))
    assert "swing_ready_20m" in f and "swing_ready_60m" in f


def test_record_only_no_consumers():
    """진입·사이징 경로가 이 키를 읽지 않는다 — 판정 전 소비 금지(사전등록 원칙)."""
    pat = re.compile(r"dist_to_(high|low)_\d+m_atr|bars_since_(high|low)_\d+m|swing_(high|low)_\d+m")
    for rel in ("main.py", "strategy/entry/checklist.py", "strategy/entry/position_sizer.py",
                "strategy/entry/dynamic_sizing.py", "strategy/entry/meta_gate.py"):
        p = os.path.join(_ROOT, rel)
        if not os.path.exists(p):
            continue
        src = open(p, encoding="utf-8", errors="ignore").read()
        assert not pat.search(src), "%s 가 스윙 피처를 소비한다 — 채널 판정 전 금지" % rel


def test_replay_20260903_matches_investigation():
    """2026-09-03 C1~C4 재현(정본 60봉 창): C1 run 7.07/dist 0.55 · C2 9.50/1.34 · C3 6.41/0.92 · C4 8.04/0.92.

    528차 조사 문서의 10.0/6.6은 61봉 창(현재 봉 + 60)으로 잰 값 — 창 경계 1봉 차이일 뿐 결론 불변."""
    import sqlite3
    raw = os.path.join(_ROOT, "data", "db", "raw_data.db")
    if not os.path.exists(raw):
        try:
            import pytest
            pytest.skip("라이브 DB 없음")
        except ImportError:
            return
    con = sqlite3.connect("file:%s?mode=ro" % raw.replace("\\", "/"), uri=True)
    rows = [(r[0][11:16], r[1], r[2], r[3], r[4]) for r in con.execute(
        "select ts,open,high,low,close from raw_candles where ts between '2026-09-03 08:45' and '2026-09-03 11:05' order by ts")]
    con.close()
    if len(rows) < 100:
        return
    idx = {r[0]: i for i, r in enumerate(rows)}

    def atr14(i):
        trs = [max(rows[k][2] - rows[k][3], abs(rows[k][2] - rows[k - 1][4]), abs(rows[k][3] - rows[k - 1][4]))
               for k in range(max(1, i - 13), i + 1)]
        return sum(trs) / len(trs)

    expect = {"10:02": (1, 7.07, 0.55), "10:23": (1, 9.50, 1.34), "10:32": (1, 6.41, 0.92), "11:01": (-1, 8.04, 0.92)}
    for t, (d, run_e, dist_e) in expect.items():
        i = idx[t]
        f = compute_swing_features([r[2] for r in rows[:i + 1]], [r[3] for r in rows[:i + 1]], rows[i][4], atr14(i), (60,))
        run = f["dist_to_low_60m_atr"] if d == 1 else f["dist_to_high_60m_atr"]
        dist = f["dist_to_high_60m_atr"] if d == 1 else f["dist_to_low_60m_atr"]
        assert abs(run - run_e) <= 0.05, (t, run, run_e)
        assert abs(dist - dist_e) <= 0.05, (t, dist, dist_e)
        assert f["swing_ready_60m"] is True


if __name__ == "__main__":
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn(); print("PASS", name)
            except AssertionError as e:
                fails += 1; print("FAIL", name, e)
    sys.exit(1 if fails else 0)
