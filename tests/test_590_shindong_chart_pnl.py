# -*- coding: utf-8 -*-
"""[MW0602 590차] 1분봉 차트·손익 추이 패널 — GP(GB·GS) → 신동 교체.

사용자 지시(2026-09-24)
  1. 1분봉 차트에서 GB·GS 거래를 제거하고 신동 거래를 올린다.
  2. 손익 추이 패널에 미륵·신동 손익 추이를 각각 볼 수 있는 버튼 — 요율은 크레온.

고정하는 불변식
  A. 크레온 재환산이 엔진 손익식과 **원 단위로** 같다(규격 DB 값은 건드리지 않는다).
  B. 차트 행: 철회 제외 · 다리(1차·최종) 최대 2개 · 보유 중 표시.
  C. 패널: 신동 모드는 신동 행만, 브로커 net 을 **타지 않는다** / 미륵 모드는 종전 그대로
     (부분 선택일 브로커 net 금지 — 557차 test_7 이관).
  D. 배너 평문 · 3상태(미배선/조회 실패/정상).
  E. 배선: GP 흔적이 패널·캔버스에서 사라졌고, 신동 그리기가 점선·클램프를 유지한다.
  F. offscreen 스모크 — 실제로 그려 본다(paint 경로 예외 = 프로세스 사망, CLAUDE.md 557차).

실행: C:\\Users\\pc1\\anaconda3\\python.exe -m pytest tests/test_590_shindong_chart_pnl.py
"""
import io
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

os.environ["MIREUK_TEST_MODE"] = "1"
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402

from strategy.shindong import engine, spec, store  # noqa: E402
from strategy.shindong import display  # noqa: E402

_SRC = io.open(os.path.join(_ROOT, "dashboard", "main_dashboard.py"), encoding="utf-8").read()
CREON = 0.000019


def _trade(side=1, e=1100.0, x1=1104.0, x2=1109.0, status="CLOSED",
           day="2026-09-28", e_ts="09:05", t1="09:40", t2="10:30", rule="R2"):
    """shindong_trades 한 행 모양. 다리 net 은 **규격(CYBOS) 요율** 로 계산한다 — DB 와 같다."""
    p1, n1 = engine.leg_net(side, e, x1, False)
    p2, n2 = engine.leg_net(side, e, x2, True)
    row = {"trade_date": day, "variant": "MAIN", "trade_key": "%s|%s|%+d" % (rule, e_ts, side),
           "rule": rule, "side": side, "product": "wk_mon",
           "entry_ts": "%s %s:00" % (day, e_ts), "entry_px": e,
           "stop_init": e - 3, "stop_now": e - 3, "t1": x1, "t2": x2,
           "touch_level": None, "touch_ts": None, "status": status,
           "leg1_exit_ts": "%s %s:00" % (day, t1), "leg1_exit_px": x1, "leg1_reason": "T1",
           "leg1_pts": p1, "leg1_net": n1,
           "leg2_exit_ts": "%s %s:00" % (day, t2), "leg2_exit_px": x2, "leg2_reason": "TIME",
           "leg2_pts": p2, "leg2_net": n2, "net_krw": n1 + n2}
    if status == "OPEN":
        for k in ("leg2_exit_ts", "leg2_exit_px", "leg2_reason", "leg2_pts", "leg2_net"):
            row[k] = None
        row["net_krw"] = n1
    return row


# ── A. 크레온 재환산 ──────────────────────────────────────────────

def test_a1_creon_rate_is_fixed_creon_not_detected():
    assert display.creon_rate() == pytest.approx(CREON)
    assert spec.COMMISSION_RATE != CREON      # 규격은 CYBOS — 재환산이 실제로 일을 한다


@pytest.mark.parametrize("side,e,x,mkt", [(1, 1100.0, 1104.5, False), (-1, 1130.5, 1110.5, True),
                                          (1, 1100.0, 1097.0, True)])
def test_a2_rerate_equals_engine_formula_at_creon(monkeypatch, side, e, x, mkt):
    _pts, net_spec = engine.leg_net(side, e, x, mkt)
    monkeypatch.setattr(spec, "COMMISSION_RATE", CREON)
    _pts2, net_creon = engine.leg_net(side, e, x, mkt)
    monkeypatch.undo()
    got = display.leg_net_at_rate(net_spec, e, x, CREON)
    assert got == pytest.approx(net_creon, abs=1e-6)
    assert got > net_spec                     # 크레온이 싸다 → 순손익이 오른다


def test_a3_open_leg_stays_none():
    assert display.leg_net_at_rate(None, 1100.0, 1101.0, CREON) is None


# ── B. 차트 행 ───────────────────────────────────────────────────

def test_b1_chart_rows_shape():
    closed = _trade()
    held = _trade(side=-1, status="OPEN", e_ts="11:00", t1="11:20")
    gone = dict(_trade(e_ts="13:00"), status="RETRACTED")
    rows = display.chart_rows([closed, held, gone])
    assert len(rows) == 2, "철회(RETRACTED)가 차트에 올라왔다"
    c, h = rows
    assert c["direction_txt"] == "LONG" and h["direction_txt"] == "SHORT"
    assert [x["leg"] for x in c["exits"]] == [1, 2] and c["open"] is False
    assert [x["leg"] for x in h["exits"]] == [1] and h["open"] is True
    assert c["exits"][1]["pts"] == pytest.approx(9.0)


# ── C. 패널 행 · 계산 ────────────────────────────────────────────

def test_c1_pnl_rows_closed_only_and_creon():
    t = _trade()
    rows = display.pnl_rows([t, _trade(status="OPEN", e_ts="11:00")], rate=CREON)
    assert len(rows) == 1, "보유 중 거래가 손익에 들어갔다"
    r = rows[0]
    assert r["entry_ts"] == "2026-09-28 10:30:00"         # 마지막 다리 청산 시각
    assert r["pnl_pts"] == pytest.approx(4.0 + 9.0)
    want = (display.leg_net_at_rate(t["leg1_net"], 1100.0, 1104.0, CREON)
            + display.leg_net_at_rate(t["leg2_net"], 1100.0, 1109.0, CREON))
    assert r["pnl_krw"] == round(want, 0)
    assert r["pnl_krw"] > t["net_krw"]                     # DB(규격) 값보다 크다 = 재환산됨


class _CB(object):
    def __init__(self, c=True):
        self._c = bool(c)

    def isChecked(self):
        return self._c


class _Banner(object):
    text = ""

    def setText(self, t):
        self.text = t

    def setStyleSheet(self, s):
        pass


class FakePanel(object):
    """`PnlHistoryPanel` 의 계산 메서드를 실물에서 **바인딩**해 쓰는 껍데기(복제 아님)."""

    def __init__(self, rows, broker, sd_rows, mode, fwd=True, rev=True,
                 wired=True, loaded=True, sd_open=0):
        from dashboard.main_dashboard import PnlHistoryPanel as _P
        self.MODE_MIREUK, self.MODE_SHINDONG = _P.MODE_MIREUK, _P.MODE_SHINDONG
        self._rows, self._broker_pnl, self._sd_rows = rows, dict(broker), sd_rows
        self._mode = mode
        self._cb_forward, self._cb_reverse = _CB(fwd), _CB(rev)
        self._sd_wired, self._sd_loaded, self._sd_open_n = wired, loaded, sd_open
        self._mode_banner = _Banner()
        self._day_total_n = {}
        for _r in rows:
            self._day_total_n[_r["entry_ts"][:10]] = self._day_total_n.get(_r["entry_ts"][:10], 0) + 1
        for _n in ("_sd_mode", "_active_rows", "_group", "_stats", "_daily_bucket",
                   "_effective_day_krw", "_day_is_whole", "_effective_day_pt",
                   "_group_effective_krw", "_group_effective_pt", "_mdd", "_mdd_daily",
                   "_update_mode_banner", "_virtual_mark"):
            setattr(self, _n, getattr(_P, _n).__get__(self, FakePanel))


def _mrow(ts, krw, pts=1.0, rev=0):
    return {"entry_ts": ts, "pnl_pts": pts, "pnl_krw": float(krw), "forward_pnl_pts": pts,
            "forward_pnl_krw": float(krw), "quantity": 1, "reverse_entry_enabled": rev}


_M = [_mrow("2026-09-28 10:00:00", 100_000), _mrow("2026-09-28 11:00:00", -30_000, rev=1)]
_B = {"2026-09-28": 62_000}


def test_c2_shindong_mode_uses_only_shindong_and_never_broker():
    sd = display.pnl_rows([_trade()], rate=CREON)
    p = FakePanel(_M, _B, sd, "shindong")
    assert p._active_rows() == sd
    b = p._daily_bucket(p._active_rows())["2026-09-28"]
    assert p._effective_day_krw("2026-09-28", b) == sd[0]["pnl_krw"]
    assert p._effective_day_krw("2026-09-28", b) != 62_000, "신동이 미륵 브로커 net 을 탔다"
    assert p._virtual_mark() == "🟣 "


def test_c3_mireuk_mode_unchanged_and_partial_day_blocks_broker():
    """557차 test_7 이관 — 부분 선택일에 브로커 전량 net 을 쓰면 빠진 거래 손익이 섞인다."""
    sd = display.pnl_rows([_trade()], rate=CREON)
    whole = FakePanel(_M, _B, sd, "mireuk")
    assert whole._virtual_mark() == ""
    bw = whole._daily_bucket(whole._active_rows())["2026-09-28"]
    assert whole._effective_day_krw("2026-09-28", bw) == 62_000
    part = FakePanel(_M, _B, sd, "mireuk", rev=False)
    bp = part._daily_bucket(part._active_rows())["2026-09-28"]
    assert part._effective_day_krw("2026-09-28", bp) == 100_000


# ── D. 배너 ──────────────────────────────────────────────────────

def test_d1_banner_states_plain_text():
    sd = display.pnl_rows([_trade()], rate=CREON)
    cases = {
        "unwired": FakePanel(_M, _B, [], "shindong", wired=False),
        "failed": FakePanel(_M, _B, [], "shindong", loaded=False),
        "never": FakePanel(_M, _B, [], "shindong", loaded=None, wired=None),
        "ok": FakePanel(_M, _B, sd, "shindong", sd_open=2),
        "mireuk": FakePanel(_M, _B, sd, "mireuk"),
    }
    for p in cases.values():
        p._update_mode_banner()
        assert "**" not in p._mode_banner.text        # QLabel 은 평문
    assert "미배선" in cases["unwired"]._mode_banner.text
    assert "조회 실패" in cases["failed"]._mode_banner.text
    assert "조회 전" in cases["never"]._mode_banner.text
    t = cases["ok"]._mode_banner.text
    assert "크레온" in t and "0.0019%" in t and "보유 중 2건" in t
    assert "실전 전환 기준 ①" in t
    assert "미륵" in cases["mireuk"]._mode_banner.text


# ── E. 배선 ──────────────────────────────────────────────────────

def _cls_body(name, nxt):
    return _SRC[_SRC.index("class %s(" % name):_SRC.index("class %s(" % nxt)]


def test_e1_gp_is_gone_from_panel_and_chart_paths():
    panel = _cls_body("PnlHistoryPanel", "LogPanel")
    assert "_gp_" not in panel and "GP(가상)\")" not in panel
    assert "fetch_gp_shadow" not in _SRC, "GP 섀도 조회가 대시보드에 남아 있다"
    assert "set_gp_trades" not in _SRC and "_draw_gp_markers" not in _SRC
    # 패널은 trades 를 신동 원천으로 쓰지 않는다
    body = panel[panel.index("def _load_shindong"):]
    body = body[:body.index("\n    def ", 10)]
    assert "shindong" in body and "fetch_pnl_history" not in body and "TRADES_DB" not in body


def test_e2_sd_drawing_keeps_dotted_span_and_label_clamp():
    body = _SRC[_SRC.index("    def _draw_sd_markers"):]
    body = body[:body.index("    def _draw_sd_label")]
    assert "Qt.DotLine" in body and "Qt.DashDotLine" in body
    assert body.index("drawLine") < body.index("_draw_sd_shape("), "점선을 마커 뒤에 그린다"
    lab = _SRC[_SRC.index("    def _draw_sd_label"):]
    lab = lab[:lab.index("\n    def ", 10)]
    assert "plot.right()" in lab and "fontMetrics().width" in lab
    # 토글이 있다 — 「거래미륵」이 신동을 끄지 않는다
    assert '("trade_sd",     "거래신동"' in _SRC
    assert 'if self._ov.get("trade_sd", True):' in _SRC


# ── F. offscreen 스모크 — 실제로 그린다 ───────────────────────────

@pytest.fixture
def qt_app():
    from PyQt5.QtWidgets import QApplication
    return QApplication.instance() or QApplication(sys.argv)


def test_f1_chart_paints_shindong_markers(qt_app):
    from dashboard.main_dashboard import MinuteChartCanvas
    c = MinuteChartCanvas()
    c.resize(900, 500)
    candles = []
    px = 1100.0
    for i in range(90):
        hh, mm = divmod(9 * 60 + i, 60)
        candles.append({"ts": "2026-09-28 %02d:%02d:00" % (hh, mm), "open": px,
                        "high": px + 1, "low": px - 1, "close": px + 0.3, "volume": 10})
        px += 0.1
    c.reset_session(candles, [], exit_markers=[])
    c.set_sd_trades(display.chart_rows([
        _trade(t1="09:40", t2="10:10"),
        _trade(side=-1, status="OPEN", e_ts="10:15", t1="10:20")]))
    assert len(c._sd_trades) == 2
    img = c.grab()                             # paintEvent 를 태운다 — 예외면 여기서 죽는다
    assert not img.isNull()
    c.set_overlay("trade_sd", False)
    assert not c.grab().isNull()


def test_f2_panel_switches_mode_offscreen(qt_app, tmp_path, monkeypatch):
    """실제 위젯으로 전환해 본다. DB·ui_prefs 는 tmp 로 격리한다(실운영 파일 오염 금지)."""
    import config.settings as cs
    import dashboard.main_dashboard as md
    db = str(tmp_path / "shindong.db")
    t = _trade(day=__import__("datetime").date.today().isoformat())
    con = store.connect(db)
    cols = ("trade_date,variant,trade_key,rule,side,product,entry_ts,entry_px,stop_init,stop_now,"
            "t1,t2,touch_level,touch_ts,status,leg1_exit_ts,leg1_exit_px,leg1_reason,leg1_pts,"
            "leg1_net,leg2_exit_ts,leg2_exit_px,leg2_reason,leg2_pts,leg2_net,net_krw").split(",")
    with con:
        con.execute("INSERT INTO shindong_trades(%s,updated_at) VALUES(%s,'x')"
                    % (",".join(cols), ",".join("?" * len(cols))), [t[k] for k in cols])
    con.close()
    monkeypatch.setattr(cs, "SHINDONG_DB", db)
    monkeypatch.setattr(md, "DATA_DIR", str(tmp_path))
    p = md.PnlHistoryPanel()
    p.refresh([])
    assert p._mode == p.MODE_MIREUK                        # 기본은 미륵
    assert p._sd_loaded is True and len(p._sd_rows) == 1
    p._btn_shindong.setChecked(True)
    assert p._mode == p.MODE_SHINDONG
    assert p.tbl_daily.rowCount() == 1
    assert "🟣" in p._sum["total"].text()
    assert p._cb_forward.isHidden()
    assert os.path.exists(str(tmp_path / "ui_prefs.json"))   # 저장은 tmp 로만 갔다
    p._btn_mireuk.setChecked(True)
    assert p._mode == p.MODE_MIREUK and p.tbl_daily.rowCount() == 0
