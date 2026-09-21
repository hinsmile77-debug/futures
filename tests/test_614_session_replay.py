# -*- coding: utf-8 -*-
"""[MW0601 614차] 세션 재생 — 장후 복기 / 장중 복원 회귀 가드.

기동 시 당일(또는 최근 거래일) 데이터를 DB 에서 패널로 되살린다. 표시 경로만
건드리고 수집 게이트(`is_market_open`)는 그대로 둔다.

여기서 고정하는 것:
  1. 🔴 **라이브가 이긴다** — 라이브가 이미 갱신한 패널은 재생이 덮지 않는다
  2. 재생 자신의 주입은 「라이브」로 세지 않는다(배지 자멸 방지)
  3. 장중 복원은 배지를 달지 않고, 장후 복기만 단다
  4. 라이브가 돌아오면 배지가 내려간다
  5. **마지막 행이 아니라 마지막 「유효」 행**을 쓴다 (0 을 되살리지 않는다)
  6. 원천이 없으면 패널을 건드리지 않는다 (빈 dict ≠ 0)
  7. 표시 계층만 — position·investor_data·CB 를 쓰지 않는다
  8. 전수 스캔을 만들지 않는다 (456차 CB⑤ 자가유발)
"""
import io
import json
import os
import sqlite3
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SVC = os.path.join(_ROOT, "strategy", "runtime", "session_replay_service.py")
_DASH = os.path.join(_ROOT, "dashboard", "main_dashboard.py")
_MAIN = os.path.join(_ROOT, "main.py")


def _src(p):
    return io.open(p, encoding="utf-8").read()


class _FakeDash(object):
    """어댑터의 재생 계약만 흉내 낸 최소 스텁."""

    def __init__(self):
        self.calls = []
        self.badge = None
        self.badge_tip = ""
        self._live = set()
        self._injecting = False

    # 재생 계약
    def replay_should_inject(self, key):
        return key not in self._live

    def replay_begin(self):
        self._injecting = True

    def replay_end(self):
        self._injecting = False

    def set_replay_badge(self, text, tip=""):
        self.badge = text
        self.badge_tip = tip

    def mark_live(self, key):
        self._live.add(key)
        if not self._injecting and self.badge:
            self.badge = ""

    # 주입 대상 — 전부 mark_live 를 타는 실제 구조를 흉내 낸다
    def _rec(self, key, *a):
        self.mark_live(key)
        self.calls.append(key)

    def update_price(self, *a, **k):               self._rec("price", *a)
    def update_prediction(self, *a, **k):          self._rec("prediction", *a)
    def update_rv_iv_spread(self, *a, **k):        self._rec("rv_iv", *a)
    def update_option_chain(self, *a, **k):        self._rec("option_chain", *a)
    def update_option_flow_delta(self, *a, **k):   self._rec("option_flow", *a)
    def update_futures_flow_delta(self, *a, **k):  self._rec("futures_flow", *a)


class _Sys(object):
    def __init__(self, dash):
        self.dashboard = dash


def _svc():
    from strategy.runtime.session_replay_service import SessionReplayService
    return SessionReplayService()


def _payload(*keys):
    """주입기가 받는 실제 모양으로 만든다 — price 는 float, prediction 은 (preds, conf)."""
    shape = {"price": 1105.0, "prediction": ({"1분": {}}, 0.5)}
    return dict((k, (shape.get(k, {"x": 1}), "15:00")) for k in keys)


def _drain(qapp, n=60):
    import time
    for _ in range(n):
        qapp.processEvents()
        time.sleep(0.01)


@pytest.fixture(scope="module")
def qapp():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PyQt5.QtWidgets import QApplication
    return QApplication.instance() or QApplication([])


# ── 1. 라이브 우선 ────────────────────────────────────────────────────────

def test_1_live_wins_replay_never_overwrites(qapp):
    """🔴 장중 재기동에서 재생이 늦게 도착하면 더 새로운 값을 덮는다.

    화면이 조용히 과거로 되돌아가고 예외는 나지 않는다 — 이 테스트가 그것을 막는다.
    """
    dash = _FakeDash()
    dash.mark_live("price")          # 라이브가 먼저 도착
    dash.mark_live("rv_iv")
    svc = _svc()
    svc.STEP_GAP_MS = 0
    svc._apply(_Sys(dash), "intraday", "2026-09-21",
               _payload("price", "rv_iv", "option_flow"))
    _drain(qapp)
    assert "price" not in dash.calls, "라이브 값을 재생이 덮었다"
    assert "rv_iv" not in dash.calls, "라이브 값을 재생이 덮었다"
    assert "option_flow" in dash.calls, "라이브가 안 온 패널은 되살려야 한다"


def test_2_replay_does_not_count_itself_as_live(qapp):
    """재생 주입도 같은 update_* 를 탄다 — 구분하지 않으면 배지가 자멸한다."""
    dash = _FakeDash()
    svc = _svc()
    svc.STEP_GAP_MS = 0
    svc._apply(_Sys(dash), "post_market", "2026-09-21", _payload("price"))
    _drain(qapp)
    assert dash.badge, "재생이 스스로를 라이브로 세어 배지를 지웠다"
    assert "복기" in dash.badge


# ── 2. 배지 ───────────────────────────────────────────────────────────────

def test_3_intraday_restore_has_no_badge(qapp):
    """장중 복원은 배지를 달지 않는다 — 라이브가 곧 덮는다.

    거기에 배지가 남으면 반대 방향의 같은 사고다(살아 있는 값이 죽은 값처럼 보인다).
    """
    dash = _FakeDash()
    svc = _svc()
    svc.STEP_GAP_MS = 0
    svc._apply(_Sys(dash), "intraday", "2026-09-21", _payload("price"))
    _drain(qapp)
    assert not dash.badge


def test_4_post_market_badge_names_every_source_time(qapp):
    """⚠ 단일 「스냅샷 시각」이 없다 — 원천마다 끝난 시각이 다르다."""
    dash = _FakeDash()
    svc = _svc()
    svc.STEP_GAP_MS = 0
    pay = {"price": (1.0, "15:08"), "futures_flow": ({}, "15:34")}
    svc._apply(_Sys(dash), "post_market", "2026-09-21", pay)
    _drain(qapp)
    assert "15:08" in dash.badge_tip and "15:34" in dash.badge_tip, (
        "원천별 마지막 시각을 하나로 뭉뚱그렸다")


def test_5_live_return_clears_badge(qapp):
    """장이 열려 라이브가 들어오면 복기 배지는 사라져야 한다."""
    from dashboard.main_dashboard import DashboardAdapter

    d = DashboardAdapter()
    d.set_replay_badge("■ 복기 · 2026-09-21", "t")
    assert d._replay_badge_on is True
    d.update_price(1105.0, 0.0)          # 라이브
    assert d._replay_badge_on is False


# ── 3. 「마지막 유효 행」 ─────────────────────────────────────────────────

def test_6_picks_last_valid_row_not_last_row(tmp_path):
    """🔴 마지막 행이 재기동 직후면 0 이다 — 그걸 되살리면 안 한 것보다 나쁘다.

    실측 2026-09-21: 15:02~15:08 6행이 `opt_chain_available=0` 이고
    마지막 유효 행은 15:00 이었다.
    """
    p = str(tmp_path / "raw.db")
    con = sqlite3.connect(p)
    con.execute("CREATE TABLE raw_features (ts TEXT PRIMARY KEY, features TEXT)")
    con.execute("CREATE TABLE raw_candles (ts TEXT PRIMARY KEY, close REAL)")
    good = json.dumps({"opt_chain_available": 1.0, "opt_chain_pcr": 0.42,
                       "rv_iv_spread_ready": 1.0})
    dead = json.dumps({"opt_chain_available": 0.0, "opt_chain_pcr": 0.0,
                       "rv_iv_spread_ready": 0.0})
    con.executemany("INSERT INTO raw_features VALUES (?,?)", [
        ("2026-09-21 15:00:00", good),
        ("2026-09-21 15:02:00", dead),
        ("2026-09-21 15:08:00", dead),
    ])
    con.execute("INSERT INTO raw_candles VALUES ('2026-09-21 15:08:00', 1105.0)")
    con.commit(); con.close()

    import strategy.runtime.session_replay_service as m
    old_raw, old_pred = m._RAW_DB, m._PRED_DB
    m._RAW_DB, m._PRED_DB = p, p
    try:
        out = _svc()._collect("2026-09-21")
    finally:
        m._RAW_DB, m._PRED_DB = old_raw, old_pred

    assert out["option_chain"][1] == "15:00", "죽은 마지막 행을 되살렸다"
    assert out["option_chain"][0]["opt_chain_pcr"] == 0.42
    assert out["rv_iv"][1] == "15:00"


def test_7_no_source_means_panel_untouched(tmp_path):
    """원천이 없으면 키를 만들지 않는다 — 빈 dict 와 0 을 구분한다."""
    p = str(tmp_path / "raw.db")
    con = sqlite3.connect(p)
    con.execute("CREATE TABLE raw_features (ts TEXT PRIMARY KEY, features TEXT)")
    con.execute("CREATE TABLE raw_candles (ts TEXT PRIMARY KEY, close REAL)")
    con.commit(); con.close()

    import strategy.runtime.session_replay_service as m
    old_raw, old_pred = m._RAW_DB, m._PRED_DB
    m._RAW_DB, m._PRED_DB = p, p
    try:
        out = _svc()._collect("2026-09-21")
    finally:
        m._RAW_DB, m._PRED_DB = old_raw, old_pred
    assert "rv_iv" not in out and "option_chain" not in out and "price" not in out


def test_8_apply_with_empty_payload_touches_nothing(qapp):
    dash = _FakeDash()
    svc = _svc(); svc.STEP_GAP_MS = 0
    svc._apply(_Sys(dash), "post_market", "2026-09-21", {})
    _drain(qapp, 10)
    assert dash.calls == [] and not dash.badge


# ── 4. 안전 ───────────────────────────────────────────────────────────────

def test_9_replay_touches_display_layer_only():
    """🔴 재생이 매매 상태를 오염시키면 안 된다."""
    src = _src(_SVC)
    # ⚠ 모듈 docstring 은 "쓰지 않는다"고 **약속하느라** 그 이름들을 인용한다.
    #   주석·docstring 을 걷어내고 **코드만** 본다(613차에서 같은 함정을 밟았다).
    body = src.split('"""', 2)[2] if src.count('"""') >= 2 else src
    code = "\n".join(ln for ln in body.splitlines()
                     if not ln.lstrip().startswith("#"))
    for bad in ("system.position", ".investor_data", "circuit_breaker",
                "place_order", "INSERT ", "UPDATE ", "DELETE "):
        assert bad not in code, "재생이 표시 계층 밖을 건드린다: %s" % bad
    # 읽기는 반드시 read-only 연결로
    assert "mode=ro" in src


def test_10_queries_are_bounded_no_full_scan():
    """장중에도 도는 경로다 — 전수 스캔은 456차 CB⑤ 자가유발이다."""
    src = _src(_SVC)
    from strategy.runtime.session_replay_service import SessionReplayService

    assert SessionReplayService._LOOKBACK <= 200
    assert "LIMIT" in src
    # 날짜 경계 없이 raw_features/raw_candles 를 훑는 질의가 없어야 한다
    for stmt in ("FROM raw_features WHERE", "FROM raw_candles WHERE"):
        assert stmt in src


def test_11_side_path_never_raises():
    """보조 경로가 기동을 흔들면 안 된다(611차 후속이 실증한 배치 원칙)."""
    src = _src(_SVC)
    for fn in ("def schedule", "def _worker", "def _collect"):
        body = src[src.index(fn):]
        body = body[:body.index("\n    def ", 5)]
        assert "except Exception" in body, fn


def test_12_collection_gates_are_not_loosened():
    """🔴 화면을 채우려고 장외 TR 게이트를 풀면 안 된다.

    `is_market_open` 가드 4개는 옳다 — 614차는 표시 경로만 되살린다.
    """
    src = _src(_MAIN)
    for fn, ln in (("_fetch_investor_data", "if not is_market_open(now):"),
                   ("_poll_option_chain", "if not is_market_open(datetime.datetime.now()):"),
                   ("_poll_kospi200_index", "if not is_market_open(datetime.datetime.now()):")):
        body = src[src.index("def %s(" % fn):]
        body = body[:body.index("\n    def ", 5)]
        assert ln in body, "%s 의 장중 가드가 사라졌다" % fn


def test_13_wired_after_restore_on_startup():
    """`restore_on_startup` 이 못 덮는 구간을 메우는 것이므로 그 뒤여야 한다."""
    src = _src(_MAIN)
    i_restore = src.index("self.session_recovery_service.restore_on_startup(self)")
    i_replay = src.index("self.session_replay_service.schedule(self)")
    assert i_restore < i_replay


def test_14_adapter_marks_live_on_every_replayed_panel():
    """재생이 되살리는 패널은 전부 라이브 표식을 남겨야 한다 — 하나라도 빠지면
    그 패널만 라이브가 덮이는 구멍이 된다."""
    src = _src(_DASH)
    for key in ("price", "prediction", "rv_iv", "option_chain",
                "option_flow", "futures_flow", "divergence"):
        assert 'self.mark_live("%s")' % key in src, "mark_live 누락: %s" % key
