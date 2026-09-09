# -*- coding: utf-8 -*-
"""[MW0601 552차 후속] 「5단은 이미 소비되고 있었다」와 Phase 3-0 중복 축약 가드.

이 파일이 고정하는 사실
-----------------------
552차 초판 계획서는 두 가지를 잘못 적었고, 그 둘이 Phase 3 설계를 왜곡했다:

  (A) 「2~5단은 hoga_log.debug 한 줄로 흘러가 버려졌다」
      -> 틀렸다. `_handle_hoga` 는 `_on_hoga` 에 **5단 스냅샷 전량**을 넘기고,
         `FeatureBuilder.update_hoga` 가 그것을 `MLOFICalculator(levels=5)` ·
         `MicropriceCalculator(max_levels=5)` 로 흘린다. 5단은 **이미 라이브
         피처로 소비되고 있었다.** 버려진 것은 원값의 **영속화**뿐이다.

  (B) 「오더북 파생은 전부 1단 기반」
      -> 틀렸다. 1단 기반은 `ofi_*`·`queue_*` 뿐이다.

그 결과 초판 Phase 3 이 신규 축으로 등록한
`book_net_ratio = (bid_tot-ask_tot)/(bid_tot+ask_tot)` 은 이미 라이브인
`microprice_depth_bias` 와 **정의가 같고 가중만 다르다**(균등 vs 1/(i+1)).
`config/constants.py` 의 321·326차 주석이 **같은 이유로 `lob_imbalance` 를 이미
기각**했다 — 이 파일은 그 판단이 다시 잊히지 않게 못을 박는다.

⚠ 여기서 검증하는 것은 **중복 여부(정제)** 이지 알파가 아니다.
"""
from __future__ import print_function

import io
import os
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ── (A) 5단이 실제로 소비된다 ────────────────────────────────────────────────
def test_microprice_consumes_levels_2_to_5():
    """1단이 완전 대칭이어도 2~5단 비대칭이 depth_bias 에 나타난다.

    이게 0 이 나오면 5단이 소비되지 않는 것이고, 552차 초판의 「버려졌다」가
    맞는 말이 된다. 실제로는 나타난다.
    """
    from features.technical.microprice import MicropriceCalculator
    mp = MicropriceCalculator(max_levels=5)
    # 1단 잔량은 좌우 동일(50/50) — 2~5단만 매수 우위
    out = mp.update_hoga(
        bid_prices=[100.0, 99.0, 98.0, 97.0, 96.0],
        bid_qtys=[50, 400, 400, 400, 400],
        ask_prices=[101.0, 102.0, 103.0, 104.0, 105.0],
        ask_qtys=[50, 10, 10, 10, 10],
    )
    assert out is not None
    # 틱 반환은 `depth_bias_tick`, 분 플러시는 `depth_bias` — 둘 다 같은 5단 가중값이다.
    assert out.get("depth_bias_tick", 0.0) > 0.5, (
        "2~5단 비대칭이 depth_bias 에 반영되지 않았다 — 5단 소비가 끊긴 것이다: %r" % out)
    flushed = mp.flush_minute()
    assert flushed.get("depth_bias", 0.0) > 0.5, (
        "분 플러시 키 `depth_bias` 에도 5단이 실려야 한다: %r" % flushed)


def test_mlofi_and_microprice_default_to_five_levels():
    """계산기 기본 단수가 5다 — 「1단 기반」이라는 서술을 막는다."""
    from features.technical.mlofi import MLOFICalculator
    from features.technical.microprice import MicropriceCalculator
    assert MLOFICalculator().levels == 5
    assert MicropriceCalculator().max_levels == 5


def test_handle_hoga_forwards_five_level_snapshot():
    """`_handle_hoga` 가 `_on_hoga` 콜백에 5단 스냅샷을 넘긴다."""
    from collection.cybos.realtime_data import CybosRealtimeData

    class _Hoga(object):
        def __init__(self):
            self._v = {}
            for i, k in enumerate((2, 3, 4, 5, 6)):
                self._v[k] = 101.0 + i
            for i, k in enumerate((7, 8, 9, 10, 11)):
                self._v[k] = 10 * (i + 1)
            for i, k in enumerate((19, 20, 21, 22, 23)):
                self._v[k] = 100.0 - i
            for i, k in enumerate((24, 25, 26, 27, 28)):
                self._v[k] = 11 * (i + 1)

        def GetHeaderValue(self, i):
            return self._v.get(i, 0)

    seen = {}

    def _cb(bid1, ask1, bid_qty, ask_qty, snapshot=None):
        seen["snap"] = snapshot

    rt = CybosRealtimeData.__new__(CybosRealtimeData)
    rt._last_bid1 = rt._last_ask1 = 0.0
    rt._last_bid_qty = rt._last_ask_qty = 0
    rt._book_oneside_count = 0
    rt._last_hoga_snapshot = {}
    rt._hoga_event_count = 0
    rt._rt_code = "T"
    rt._current_bar = None
    rt._on_hoga = _cb
    rt._handle_hoga(_Hoga())

    snap = seen.get("snap")
    assert snap, "스냅샷이 콜백에 전달되지 않았다 — 5단 소비 경로가 끊겼다"
    for k in ("bid_prices", "ask_prices", "bid_qtys", "ask_qtys"):
        assert len(snap[k]) == 5, "%s 가 5단이 아니다: %r" % (k, snap[k])


def test_constants_records_the_lob_duplication_precedent():
    """321·326차의 중복 기각 근거가 지워지지 않았는지 확인한다.

    이 주석이 사라지면 다음 세션이 `microprice_depth_bias` 와 같은 양을 또
    신규 축으로 등록한다 — 552차 초판이 정확히 그렇게 했다.
    """
    src = io.open(os.path.join(_ROOT, "config", "constants.py"),
                  encoding="utf-8").read()
    assert "microprice_depth_bias" in src
    assert "lob_imbalance" in src, "326차 중복 기각 근거 주석이 사라졌다"


# ── (B) Phase 3-0 판정기 ─────────────────────────────────────────────────────
def _mod():
    import importlib
    sys.path.insert(0, os.path.join(_ROOT, "scripts"))
    return importlib.import_module("book_depth_duplication_check")


def test_prereg_thresholds_are_fixed_and_ordered():
    """사전등록 임계가 상수로 고정돼 있고 순서가 맞다(458차 D6 — 문턱 사후조정 금지)."""
    m = _mod()
    assert 0.0 < m.PARTIAL_THRESHOLD < m.DUP_THRESHOLD <= 1.0
    assert m.MIN_DAYS >= 20


def _pairs(days, fn):
    out = []
    for d in range(days):
        for b in range(5):
            x = (d * 5 + b) / 100.0 - 0.5
            out.append(("2026-06-%02d 09:%02d:00" % (d % 28 + 1, b), x, fn(x)))
    return out


def test_verdict_duplicate_when_monotone_reweighting():
    """단조 재가중(가중만 다른 같은 축)은 DUPLICATE 로 잡힌다."""
    m = _mod()
    r = m.judge(_pairs(30, lambda x: 0.7 * x))
    assert r["verdict"] == "DUPLICATE", r
    assert abs(r["rho_daily"]) >= m.DUP_THRESHOLD


def test_verdict_independent_when_unrelated():
    """무관한 축이면 INDEPENDENT."""
    import random
    m = _mod()
    random.seed(552)
    pairs = [("2026-06-%02d 09:%02d:00" % (d % 28 + 1, b),
              random.uniform(-1, 1), random.uniform(-1, 1))
             for d in range(40) for b in range(20)]
    r = m.judge(pairs)
    assert r["verdict"] in ("INDEPENDENT", "INSUFFICIENT"), r
    if r["verdict"] == "INDEPENDENT":
        assert abs(r["rho_daily"]) < m.PARTIAL_THRESHOLD


def test_verdict_insufficient_below_min_days():
    """표본 미달은 판정하지 않는다 — 문턱을 낮춰 통과시키지 않는다."""
    m = _mod()
    r = m.judge(_pairs(5, lambda x: 0.7 * x))
    assert r["verdict"] == "INSUFFICIENT"
    assert "min_days" in r["reason"]


def test_sign_flip_blocks_verdict():
    """전·후반 부호가 뒤집히면 판정을 보류한다.

    ⚠ 판정 단위가 **거래일**이므로 날짜별로 값이 달라야 한다. 하루 안에서만
    변하고 일평균이 상수면 분산 0 으로 상관이 `None` 이 된다 — 그 자체가
    「분봉 풀링으로 판정하지 않는다」는 설계의 방증이다(372차).
    """
    import datetime
    m = _mod()
    base = datetime.date(2026, 6, 1)
    pairs = []
    for d in range(40):
        day = (base + datetime.timedelta(days=d)).strftime("%Y-%m-%d")
        x = (d - 20) / 40.0                   # 날짜별로 단조 변화
        y = x if d < 20 else -x               # 후반에 부호 반전
        for b in range(5):
            pairs.append(("%s 09:%02d:00" % (day, b), x + b * 1e-6, y + b * 1e-6))
    r = m.judge(pairs)
    assert r["sign_consistent"] is False, r
    assert r["verdict"] == "INSUFFICIENT", r


def test_collect_excludes_unmeasured_depth_bias_zero():
    """`depth_bias == 0.0` 행은 제외한다 — 미측정을 0 으로 섞지 않는다(계측 4원칙 2).

    2026-06 이전 전량 0.0(호가 스트림 부재)을 섞으면 상관이 0 으로 희석돼
    「독립이다」라는 거짓 결론이 나온다.
    """
    import json
    m = _mod()
    tmp = tempfile.mkdtemp()
    db = os.path.join(tmp, "raw.db")
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE raw_candles (ts TEXT PRIMARY KEY, book_bid_tot INTEGER,"
                " book_ask_tot INTEGER, book_snaps INTEGER)")
    con.execute("CREATE TABLE raw_features (ts TEXT PRIMARY KEY, features TEXT)")
    rows = [("2026-09-10 09:00:00", 120, 80, 2, 0.30),    # 유효
            ("2026-09-10 09:01:00", 100, 100, 2, 0.0),    # depth_bias 미측정 -> 제외
            ("2026-09-10 09:02:00", None, None, 0, 0.25)] # book 미수신 -> 제외
    for ts, b, a, n, v in rows:
        con.execute("INSERT INTO raw_candles VALUES (?,?,?,?)", (ts, b, a, n))
        con.execute("INSERT INTO raw_features VALUES (?,?)",
                    (ts, json.dumps({"microprice_depth_bias": v})))
    con.commit()
    con.close()
    pairs, err = m.collect("raw_candles", db_path=db)
    assert err is None, err
    assert len(pairs) == 1 and pairs[0][0] == "2026-09-10 09:00:00", pairs
    assert abs(pairs[0][1] - 0.2) < 1e-9      # (120-80)/200


def test_checker_does_not_look_at_pnl():
    """정제 단계는 손익을 보지 않는다 — 보면 Phase 3 사전등록이 오염된다.

    소스 텍스트 가드다. `trades`/`pnl` 조회가 들어오는 순간 이 스크립트는
    「중복 축약」이 아니라 「알파 탐색」이 되고, 그 뒤의 사전등록은 무효가 된다.
    """
    src = io.open(os.path.join(_ROOT, "scripts", "book_depth_duplication_check.py"),
                  encoding="utf-8").read()
    body = src.split('"""', 2)[-1]            # 모듈 docstring 제외
    for banned in ("FROM trades", "pnl_krw", "predictions.db", "TRADES_DB"):
        assert banned not in body, (
            "중복 축약 판정기가 손익을 참조한다(%s) — 사전등록 오염" % banned)
