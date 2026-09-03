# -*- coding: utf-8 -*-
"""[MW0601 526차 / F-A] 급변장 라벨 ↔ 데이터이상 게이트 분리 — 동작 불변 회귀 테스트.

배경
----
`MicroRegimeClassifier`의 급변장 판정 ③ 조건(스케일러 |z|>4 피처 ≥3)이 실측상 급변장
전환의 82%(정규 파이프라인 207건 중 169건, scaler_monitor.db 대조)를 만들었고 그 분의
변동성은 평상시였다. 526차는 라벨(`regime`)을 변동성 ①②로만 정하고 ③을
`data_anomaly`로 분리했다. **차단은 종전과 동일**해야 한다 — main.py RegimeOverride
지점에서 `regime==급변장 or data_anomaly`로 막는다.

이 테스트가 못박는 것
--------------------
1. 불변식: `regime_legacy == 급변장  ⇔  (regime == 급변장 or data_anomaly)` — 무작위
   격자 전수. 이것이 "막히는 분 집합이 같다"의 수학적 근거다.
2. 2026-09-03 14:08(진짜 급변, ADX 79.8 · ratio 1.27 · z=1) → 급변장 / atr125_adx / anomaly False.
3. 2026-06-18 10:44형(ratio 1.00 · ADX 15 · z=3) → 급변장 아님 / anomaly True / legacy 급변장.
4. `zwarn_gate_blocks`: block·reduce(배선 전)=차단, off=통과. 기본값 settings는 "block".
5. `push_1m_candle` 결과에 새 키 4종이 항상 있다(_empty 경로 포함) — 소비자가 KeyError 없이 읽는다.
6. `_classify`(구 API)는 종전 의미(③ 포함)를 유지한다 — 스크립트 하위호환.

실행:
    pytest tests/test_526_micro_regime_split.py
    python tests/test_526_micro_regime_split.py
"""
import os
import random
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
os.environ.setdefault("MIREUK_TEST_MODE", "1")

from collection.macro.micro_regime import (  # noqa: E402
    MicroRegimeClassifier, REGIME_VOLATILE, REGIME_MIXED,
)
from config.strategy_params import zwarn_gate_blocks  # noqa: E402

_NEW_KEYS = ("regime_source", "data_anomaly", "z_warn_count", "regime_legacy")


def test_invariant_legacy_equals_regime_or_anomaly():
    """종전 라벨 == 급변장 ⇔ (새 라벨 == 급변장 or data_anomaly). 격자 2,000점."""
    clf = MicroRegimeClassifier()
    rng = random.Random(526)
    for _ in range(2000):
        adx = rng.uniform(0, 100)
        ratio = rng.uniform(0.5, 2.5)
        z = rng.choice([0, 1, 2, 3, 4, 10])
        bear = rng.choice([0.0, 0.0, 1.0])
        bull = rng.choice([0.0, 0.0, 1.0])
        vwap = rng.uniform(-3, 3)
        regime, src, anomaly = clf._classify_split(adx, 1.0, 1.0, ratio, bear, bull, vwap, z)
        legacy = clf._classify(adx, 1.0, 1.0, ratio, bear, bull, vwap, z)
        assert (legacy == REGIME_VOLATILE) == ((regime == REGIME_VOLATILE) or anomaly), (
            adx, ratio, z, regime, src, anomaly, legacy)
        assert anomaly == (z >= clf.Z_WARN_ANOMALY_MIN)
        if regime == REGIME_VOLATILE:
            assert src in (clf.SOURCE_ATR15, clf.SOURCE_ATR125_ADX)
        else:
            assert src == clf.SOURCE_NONE


def test_case_20260903_1408_true_volatile():
    clf = MicroRegimeClassifier()
    regime, src, anomaly = clf._classify_split(79.8, 1.0, 1.0, 1.27, z_warn_count=1)
    assert regime == REGIME_VOLATILE
    assert src == clf.SOURCE_ATR125_ADX
    assert anomaly is False


def test_case_20260618_1044_zwarn_only():
    clf = MicroRegimeClassifier()
    regime, src, anomaly = clf._classify_split(15.0, 1.0, 1.0, 1.00, z_warn_count=3)
    assert regime != REGIME_VOLATILE
    assert src == clf.SOURCE_NONE
    assert anomaly is True
    # 구 API는 종전 의미(급변장)를 유지한다
    assert clf._classify(15.0, 1.0, 1.0, 1.00, z_warn_count=3) == REGIME_VOLATILE


def test_zwarn_gate_modes():
    assert zwarn_gate_blocks("block") is True
    assert zwarn_gate_blocks("reduce") is True     # 배선 전 — 안전 쪽
    assert zwarn_gate_blocks("off") is False
    assert zwarn_gate_blocks(None) is True
    from config import settings
    assert settings.MICRO_REGIME_ZWARN_GATE == "block", "기본값은 block — 채널 판정 전 변경 금지"


def test_push_result_has_new_keys_including_empty_path():
    clf = MicroRegimeClassifier()
    r = clf.push_1m_candle(100.1, 99.9, 100.0)          # 워밍업(_empty) 경로
    for k in _NEW_KEYS:
        assert k in r, k
    assert r["data_anomaly"] is False and r["regime_legacy"] == REGIME_MIXED
    for i in range(30):
        r = clf.push_1m_candle(100.0 + i * 0.02, 99.9 + i * 0.02, 100.0 + i * 0.02,
                               z_warn_count=3)
    for k in _NEW_KEYS:
        assert k in r, k
    assert r["data_anomaly"] is True and r["z_warn_count"] == 3
    assert r["regime_legacy"] == REGIME_VOLATILE
    assert r["regime"] != REGIME_VOLATILE          # 평온 시세 + z경고 → 라벨은 급변장 아님


def test_live_replay_blocked_minutes_unchanged():
    """실봉 재생 — 종전 라벨의 급변장 분 집합 == 신 로직의 차단 분 집합. **동작 불변의 실증.**

    DB가 없는 환경(다른 PC·CI)에서는 skip 한다. 2026-09-03 기준 실측:
    23거래일 8,704분 · 차단 496분 · 불일치 0
    (RegimeOverride 342 = atr15 131 + atr125_adx 211 · DataAnomalyGate 154).
    """
    import collections
    import datetime
    import sqlite3

    raw = os.path.join(_ROOT, "data", "db", "raw_data.db")
    smd = os.path.join(_ROOT, "data", "db", "scaler_monitor.db")
    if not (os.path.exists(raw) and os.path.exists(smd)):
        try:
            import pytest
            pytest.skip("라이브 DB 없음 — 재생 검증 생략")
        except ImportError:
            print("SKIP live replay (no DB)")
            return

    rc = sqlite3.connect("file:%s?mode=ro" % raw.replace("\\", "/"), uri=True)
    sm = sqlite3.connect("file:%s?mode=ro" % smd.replace("\\", "/"), uri=True)
    try:
        K = collections.defaultdict(int)
        for ts, ec in sm.execute(
                "select ts, extreme_count from scaler_events "
                "where extreme_count is not null and ts >= '2026-08-01'"):
            K[ts[:16]] = max(K[ts[:16]], ec or 0)
        days = [r[0] for r in rc.execute(
            "select distinct date(ts) from raw_candles where ts >= '2026-08-01' order by 1")]
        if not days:
            return
        checked = blocked = 0
        for day in days:
            clf = MicroRegimeClassifier()
            for ts, h, l, c in rc.execute(
                    "select ts,high,low,close from raw_candles "
                    "where date(ts)=? and substr(ts,12,5) >= '08:45' order by ts", (day,)):
                m = ts[:16]
                prev = (datetime.datetime.strptime(m, "%Y-%m-%d %H:%M")
                        - datetime.timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M")
                r = clf.push_1m_candle(float(h), float(l), float(c),
                                       z_warn_count=K.get(prev, 0))
                legacy = (r["regime_legacy"] == REGIME_VOLATILE)
                new = (r["regime"] == REGIME_VOLATILE) or r["data_anomaly"]
                assert legacy == new, (ts, r["regime"], r["regime_legacy"], r["data_anomaly"])
                checked += 1
                blocked += int(legacy)
        assert checked > 1000 and blocked > 0, (checked, blocked)
    finally:
        rc.close()
        sm.close()


def test_zero_z_warn_never_anomaly():
    clf = MicroRegimeClassifier()
    for ratio in (0.8, 1.0, 1.24, 1.3, 1.6):
        _, _, anomaly = clf._classify_split(40.0, 1.0, 1.0, ratio, z_warn_count=0)
        assert anomaly is False


if __name__ == "__main__":
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("PASS", name)
            except AssertionError as e:
                fails += 1
                print("FAIL", name, e)
    sys.exit(1 if fails else 0)
