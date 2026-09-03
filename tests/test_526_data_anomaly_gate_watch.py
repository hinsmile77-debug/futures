# -*- coding: utf-8 -*-
"""[MW0601 526차 / P5-13] 데이터이상 게이트 채널 — 판정 규율 회귀 테스트.

못박는 것
---------
1. 합격선은 settings에서만 온다(사전등록 키 존재·타입).
2. 수수료는 settings 요율 × 약정금액 × 2 — 상수 하드코딩 금지(493·495차).
3. 시뮬 기하: 손절 우선 · TP1 부분청산 후 보호스톱 · TP2 전량 — 합성 봉으로 고정.
4. 채널 스크립트가 DB 없이도 import 된다(장중 가드는 __main__에서만).

실행: pytest tests/test_526_data_anomaly_gate_watch.py
"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
os.environ.setdefault("MIREUK_TEST_MODE", "1")

from scripts import data_anomaly_gate_watch as DAW  # noqa: E402

_KEYS = ("enabled", "data_start", "reasons", "legacy_proxy", "candidate_filter",
         "nonoverlap_min", "min_samples", "min_days", "alpha", "drop_best_days",
         "require_net_positive", "sim", "pt_value_krw", "promotion_order")


def test_preregistered_keys_present():
    cfg = DAW._cfg()
    for k in _KEYS:
        assert k in cfg, k
    assert cfg["min_samples"] >= 30 and cfg["min_days"] >= 10
    assert cfg["promotion_order"][0] != "off", "하드 해제 직행 금지"


def test_commission_from_settings_rate():
    from config.settings import FUTURES_COMMISSION_RATE
    cfg = DAW._cfg()
    v = DAW._round_trip_commission(1046.0, cfg)
    assert abs(v - 1046.0 * cfg["pt_value_krw"] * FUTURES_COMMISSION_RATE * 2) < 1e-6
    # 2026-09-03 실측 왕복 10,262원/계약(CYBOS 요율) 근방인지 — 브랜치 요율에 따라 다르므로 부호만
    assert v > 0


def _rows(prices):
    # (ts, open, high, low, close) — 1분 간격 합성
    out = []
    for i, (o, h, l, c) in enumerate(prices):
        out.append(("2026-01-01 09:%02d" % i, o, h, l, c))
    return out


def test_simulate_stop_first_and_tp2():
    sim = {"stop_atr": 1.5, "tp1_atr": 0.5, "tp2_atr": 1.5, "tp1_fraction": 1 / 3.0,
           "max_bars": 30, "atr_window": 3}
    # ATR≈1.0 워밍업 3봉 후, 진입봉 시가 100 → 다음 봉에서 손절(98.5)과 TP1(100.5) 동시 → 손절 우선
    rows = _rows([(100, 101, 100, 100.5), (100.5, 101.5, 100.5, 101), (101, 102, 101, 101.5),
                  (100, 100, 100, 100), (100, 100, 100, 100),
                  (100, 101, 98, 99)])
    idx, atr = DAW._prep(rows, 3)
    r = DAW.simulate(rows, idx, atr, "2026-01-01 09:04", 1, sim)
    assert r is not None and r[1] == "STOP" and r[0] < 0
    # TP1 → TP2 경로
    rows2 = _rows([(100, 101, 100, 100.5), (100.5, 101.5, 100.5, 101), (101, 102, 101, 101.5),
                   (100, 100, 100, 100), (100, 100, 100, 100),
                   (100, 100.7, 100, 100.6), (100.6, 102.0, 100.5, 101.9)])
    idx2, atr2 = DAW._prep(rows2, 3)
    r2 = DAW.simulate(rows2, idx2, atr2, "2026-01-01 09:04", 1, sim)
    assert r2 is not None and r2[1] == "TP2" and r2[0] > 0


def test_sign_test_small_sample():
    p, pos, neg = DAW._sign_test_p([1, 1, 1, 1, 1, 1, 1, 1, -1, 1])
    assert pos == 9 and neg == 1 and 0 < p < 0.05
    p2, _, _ = DAW._sign_test_p([1, -1, 1, -1])
    assert p2 == 1.0


if __name__ == "__main__":
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn(); print("PASS", name)
            except AssertionError as e:
                fails += 1; print("FAIL", name, e)
    sys.exit(1 if fails else 0)
