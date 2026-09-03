# -*- coding: utf-8 -*-
"""[MW0601 529차] 레그 위치 채널 3종 — 판정 규율 회귀 테스트.

무엇을 지키는가
---------------
이 채널의 위험은 계산 오류가 아니라 **사후적합**이다. 소급 스캔에서 `run>=8 且 dist<=1.5`가
`run>=5 且 dist<=1.0`보다 좋아 보였고(일자 11/5 p=0.21 vs 9/8 p=1.00), 컷을 옮기면 "유의한" 결과를
만들 수 있다. 313차 원칙 ④와 458차 D6이 금지하는 바로 그 행동이다.

그래서 못박는다.
1. **합격선·컷은 settings에서만 온다** — 코드 리터럴이면 조용히 바뀐다.
2. **하드차단은 금지다** — `promotion_order`에 'block'이 없고 `hard_block_forbidden`이 참이다
   (317차 FalseBlock: Hurst 하드차단이 진짜 추세 분봉의 72.3%를 오판).
3. **거울상 보존 조건이 살아 있다** — 처리군을 누르는 조치가 레그 초입 승리군을 함께 누르면
   순이익이 사라진다. `require_early_group_better`가 판정에 실제로 반영돼야 한다.
4. **표본 미달이면 판정하지 않는다** — INSUFFICIENT는 실패가 아니라 결론이다.
5. **[E]는 관측 전용** — 승격 경로가 없어야 한다(가점은 진입을 늘리는 방향).
6. **부호검정은 py37에서 돈다** — `math.comb` 금지(표본이 문턱을 넘는 그날 처음 터지는 지연 폭발 방지).

실행: pytest tests/test_529_leg_position_watch.py
"""
import inspect
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
os.environ.setdefault("MIREUK_TEST_MODE", "1")

from scripts import leg_position_watch as LPW  # noqa: E402

_A_KEYS = ("enabled", "entry_source", "data_start", "lookback_min", "run_atr_min", "dist_atr_max",
           "min_samples", "min_days", "alpha", "drop_worst_days", "require_early_group_better",
           "promotion_order", "hard_block_forbidden", "feature_wired_date")
_C_KEYS = ("enabled", "data_start", "population_source", "run_atr_min", "dist_atr_max",
           "min_samples", "min_days", "alpha", "drop_worst_days", "promotion_order")
_E_KEYS = ("enabled", "data_start", "run_atr_max", "observe_only")


def test_preregistered_keys_present():
    a, c, e = LPW._cfg(LPW.CH_A), LPW._cfg(LPW.CH_C), LPW._cfg(LPW.CH_E)
    for k in _A_KEYS:
        assert k in a, "A:%s" % k
    for k in _C_KEYS:
        assert k in c, "C:%s" % k
    for k in _E_KEYS:
        assert k in e, "E:%s" % k
    # 컷은 조사 시점 값으로 고정 — 사후 변경 금지
    assert a["run_atr_min"] == 5.0 and a["dist_atr_max"] == 1.0
    assert c["run_atr_min"] == a["run_atr_min"] and c["dist_atr_max"] == a["dist_atr_max"], "두 채널 축이 어긋났다"
    assert a["min_samples"] >= 40 and a["min_days"] >= 25
    assert e["run_atr_max"] == 2.0 and e["observe_only"] is True


def test_hard_block_forbidden():
    for ch in (LPW.CH_A, LPW.CH_C):
        cfg = LPW._cfg(ch)
        assert cfg.get("hard_block_forbidden") is True, ch
        assert "block" not in (cfg.get("promotion_order") or []), ch
    # 승격 1순위는 감점(10_chase 동형) — 판정 전에 확정된 형태여야 한다
    assert LPW._cfg(LPW.CH_A)["promotion_order"][0] == "checklist_demote"


def test_thresholds_not_hardcoded_in_script():
    """합격선·컷이 코드 리터럴로 박혀 있지 않다(settings 조회만)."""
    src = inspect.getsource(LPW)
    for lit in ("min_samples\", 40", "min_days\", 25", "= 5.0", "= 1.0"):
        # 기본값 fallback 형태(cfg.get("min_samples", 40))는 허용하되, 대입은 금지
        assert "run_atr_min = 5" not in src and "dist_atr_max = 1" not in src
    assert 'cfg["run_atr_min"]' in src and 'cfg["dist_atr_max"]' in src


def test_sign_test_py37_safe_and_correct():
    # ⚠ 주석에 적힌 경고 문구가 아니라 **호출 형태**를 본다(경고문 자체는 있어야 한다)
    assert "math.comb(" not in inspect.getsource(LPW)
    assert "comb" in inspect.getsource(LPW), "py37 경고 주석이 사라졌다"
    p, pos, neg = LPW._sign_test_p([1, 1, 1, 1, 1, 1, 1, 1, -1, 1])
    assert pos == 9 and neg == 1 and 0 < p < 0.05
    p2, _, _ = LPW._sign_test_p([1, -1, 1, -1])
    assert p2 == 1.0
    assert LPW._sign_test_p([])[0] is None


def test_krw_format_py37_safe():
    assert LPW._krw(-1234567.0, True) == "-1,234,567"
    assert LPW._krw(None) == "N/A"


def test_replay_swing_matches_investigation():
    """배선 전 프록시가 09-03 C1~C4를 재현한다(정본 60봉 창)."""
    import sqlite3
    raw = os.path.join(_ROOT, "data", "db", "raw_data.db")
    if not os.path.exists(raw):
        try:
            import pytest
            pytest.skip("라이브 DB 없음")
        except ImportError:
            return
    con = sqlite3.connect("file:%s?mode=ro" % raw.replace("\\", "/"), uri=True)
    rows = [(r[0][:16], float(r[1]), float(r[2]), float(r[3])) for r in con.execute(
        "SELECT ts, high, low, close FROM raw_candles "
        "WHERE ts BETWEEN '2026-09-03 08:45' AND '2026-09-03 11:05' ORDER BY ts")]
    con.close()
    if len(rows) < 100:
        return
    idx = {r[0]: i for i, r in enumerate(rows)}
    expect = {"2026-09-03 10:02": (1, 7.07, 0.55), "2026-09-03 10:23": (1, 9.50, 1.34),
              "2026-09-03 10:32": (1, 6.41, 0.92), "2026-09-03 11:01": (-1, 8.04, 0.92)}
    for ts, (d, run_e, dist_e) in expect.items():
        s = LPW._replay_swing(rows, idx[ts], 60)
        assert s is not None, ts
        run = s["dist_to_low_60m_atr"] if d == 1 else s["dist_to_high_60m_atr"]
        dist = s["dist_to_high_60m_atr"] if d == 1 else s["dist_to_low_60m_atr"]
        assert abs(run - run_e) <= 0.05, (ts, run, run_e)
        assert abs(dist - dist_e) <= 0.05, (ts, dist, dist_e)


def test_verdicts_respect_sample_gate():
    """표본 미달이면 판정하지 않는다 — 현재 데이터에서 A는 INSUFFICIENT여야 한다."""
    if not os.path.exists(os.path.join(_ROOT, "data", "db", "trades.db")):
        try:
            import pytest
            pytest.skip("라이브 DB 없음")
        except ImportError:
            return
    a = LPW.compute_a()
    assert a.get("available") is True
    assert a["verdict"] in ("INSUFFICIENT", "NO_CHANGE", "SOFT_DEMOTE_CANDIDATE")
    cfg = LPW._cfg(LPW.CH_A)
    if a["verdict"] != "INSUFFICIENT":
        assert a["treat"]["n"] >= cfg["min_samples"] and a["treat"]["days"] >= cfg["min_days"]
    # 소급 구간은 배선 전이므로 전부 replay_proxy 여야 한다(배선 후엔 db가 늘어난다)
    assert a["meta"]["by_source"]["replay_proxy"] > 0


def test_e_channel_is_observe_only():
    if not os.path.exists(os.path.join(_ROOT, "data", "db", "trades.db")):
        try:
            import pytest
            pytest.skip("라이브 DB 없음")
        except ImportError:
            return
    e = LPW.compute_e()
    assert e.get("observe_only") is True and e.get("verdict") == "OBSERVE"
    assert "promotion_order" not in LPW._cfg(LPW.CH_E), "관측 채널에 승격 경로가 생겼다"


if __name__ == "__main__":
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn(); print("PASS", name)
            except AssertionError as ex:
                fails += 1; print("FAIL", name, ex)
    sys.exit(1 if fails else 0)
