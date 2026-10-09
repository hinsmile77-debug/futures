# -*- coding: utf-8 -*-
"""[MW0601 677차] 피터2 백필 — 실거래 개시(10/12) 이전 손익을 손익추이·손익추이2 에 올린다.

사용자 지시(2026-10-09)
    · 10/12 이전 손익추이는 1분봉 차트 「거래피터」(원천 A)로 산출해 올린다.
    · 재생(원천 B)은 비교 열로 함께 넣는다.
    · [dev 이식] dev 에는 손익추이2 탭이 없다 — 손익추이 「피터2백필」 체크박스, 채널 요율.
    · 기록 없는 날은 사용자가 「미측정」으로 적는다.

고정하는 것
    1. A 환산 규칙 — pt 는 그의 가격 차, 15:10 이후 청산은 15:10 가격으로 재측정,
       14:50 이후 진입 제외, 못 맞춘 줄은 버리지 않는다.
    2. 일자 상태 — LIVE > UNMEASURED > 사료 유무. 「미판정」을 0건으로 세지 않는다.
    3. 패널 — 백필은 **가상**: 미륵 화면의 값(브로커 net 포함)이 백필 유무와 무관하게 같다.
       감지 채널 요율로 수수료를 뗀다. 순방향·역방향과 배타 · 피터2(실거래)와는 공존.
    4. 정규식 사본이 대시보드 원본과 같다(Qt 를 끌어오지 않으려고 사본을 뒀다).

실행:
    conda run -n py37_32 python -m pytest tests/test_677_peter2_backfill.py -q
"""
import os
import re
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

os.environ["MIREUK_TEST_MODE"] = "1"
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402
from PyQt5.QtWidgets import QApplication  # noqa: E402

from config.constants import BROKER_CHANNEL_SPECS  # noqa: E402
from config.settings import FUTURES_COMMISSION_RATE as LIVE_RATE  # noqa: E402
from strategy.peter2 import backfill as bf  # noqa: E402

_APP = QApplication.instance() or QApplication(sys.argv)
CREON_RATE = BROKER_CHANNEL_SPECS["CREON"]["one_way_commission_rate"]
PT = 50_000
D = "2026-10-08"


def _src(rel):
    with open(os.path.join(_ROOT, rel), encoding="utf-8") as f:
        return f.read()


def _bars(last_hm="15:08", close=1052.42):
    """09:00 – last_hm 1분봉. 마지막 봉 종가만 의미 있다."""
    out = []
    h, m = 9, 0
    while "%02d:%02d" % (h, m) <= last_hm:
        hm = "%02d:%02d" % (h, m)
        out.append(("%s %s:00" % (D, hm), 1050.0, 1051.0, 1049.0,
                    close if hm == last_hm else 1050.0))
        m += 1
        if m == 60:
            h, m = h + 1, 0
    return out


# ── 1. A 환산 ───────────────────────────────────────────────────────────
def test_regex_copy_matches_dashboard():
    s = _src("dashboard/main_dashboard.py")
    i = s.index("\n_PT_TRADE = re.compile(")
    stmt = s[i + 1:s.index("\n\n", i)]
    ns = {"re": re}
    exec(stmt, ns)
    assert ns["_PT_TRADE"].pattern == bf.TRADE_RE.pattern, "백필 정규식 사본이 대시보드 원본과 갈렸다"


def test_parse_single_digit_hour_and_errors_kept():
    tr, err = bf.parse_tr("9:39 L 1050 / 10:17 X 1047 손절\n헛줄\n")
    assert tr[0]["entry_hm"] == "09:39" and tr[0]["exit_hm"] == "10:17"
    assert err == ["헛줄"], "못 맞춘 줄을 버리면 안 된다(원칙 ③)"


def test_normal_trade_pts_independent_of_offset():
    a, _ = bf.build_a_day(D, "09:26 L 1072 / 09:56 X 1068 손절", -4.88, _bars(), PT)
    t = a[0]
    assert t["pnl_pts"] == pytest.approx(-4.0) and t["clipped"] == 0
    assert t["gross_krw"] == pytest.approx(-200_000)
    assert t["notional_krw"] == pytest.approx((1072 - 4.88) * PT)
    assert t["entry_px"] == pytest.approx(1067.12)


def test_exit_after_1510_is_remeasured_at_force_exit():
    """10/8 실측 형태 — 그는 15:22 손절, 피터2 는 15:10 강제청산(마지막 봉 15:08 종가)."""
    a, _ = bf.build_a_day(D, "13:02 L 1056 / 15:22 X 1052 손절", -4.88, _bars("15:08", 1052.42), PT)
    t = a[0]
    assert t["clipped"] == 1 and t["exit_ts"] == D + " 15:10:00"
    assert t["exit_reason"] == "15:10 강제청산"
    assert t["pnl_pts"] == pytest.approx(1052.42 - (1056 - 4.88))
    assert "15:08 종가" in t["note"]


def test_force_exit_prefers_1510_bar_open():
    bars = _bars("15:12")
    px, src = bf.force_exit_price(bars)
    assert px == 1050.0 and src.startswith("15:10")


def test_entry_after_cutoff_excluded():
    a, notes = bf.build_a_day(D, "14:55 S 1060 / 15:05 X 1055 익절", -4.0, _bars(), PT)
    assert a == [] and any("신규진입 마감" in n for n in notes)


def test_open_trade_closed_at_1510():
    a, _ = bf.build_a_day(D, "14:00 S 1060 / - 보유", -4.0, _bars("15:08", 1050.0), PT)
    assert a[0]["clipped"] == 1 and a[0]["pnl_pts"] == pytest.approx(1056.0 - 1050.0)


def test_late_exit_without_offset_keeps_his_exit_and_says_so():
    a, _ = bf.build_a_day(D, "13:00 L 1056 / 15:22 X 1060 익절", None, _bars(), PT)
    assert a[0]["clipped"] == 0 and a[0]["pnl_pts"] == pytest.approx(4.0)
    assert "재측정 불가" in a[0]["note"], "폴백을 썼으면 그 사실을 남긴다(원칙 ④)"


# ── 2. 일자 상태 · 장부 ────────────────────────────────────────────────
def test_classify_priority():
    assert bf.classify_day(True, [1], True, True) == bf.ST_LIVE
    assert bf.classify_day(True, [1], True, False) == bf.ST_UNMEASURED
    assert bf.classify_day(False, [], False, False) == bf.ST_UNRESOLVED
    assert bf.classify_day(True, [], False, False) == bf.ST_NO_TRADE
    assert bf.classify_day(True, [1], False, False) == bf.ST_TRADED


def test_unmeasured_ledger_roundtrip(tmp_path):
    p = str(tmp_path / "sub" / "_unmeasured.txt")
    assert bf.read_unmeasured(p) == {}
    assert bf.mark_unmeasured(p, ["2026-09-28", "2026-09-29"], "사료 없음") == \
        ["2026-09-28", "2026-09-29"]
    assert bf.mark_unmeasured(p, ["2026-09-28"], "x") == [], "같은 날을 두 번 적지 않는다"
    assert bf.read_unmeasured(p) == {"2026-09-28": "사료 없음", "2026-09-29": "사료 없음"}
    with pytest.raises(ValueError):
        bf.mark_unmeasured(p, ["9/30"], "")


def test_save_load_roundtrip_and_unwired(tmp_path):
    db = str(tmp_path / "bf.db")
    assert bf.load_for_pnl(db) is None, "DB 없음 = 미배선(None) — 빈 묶음과 다르다"
    a, _ = bf.build_a_day(D, "09:26 L 1072 / 09:56 X 1068 손절", -4.88, _bars(), PT)
    day = {"trade_date": D, "status": bf.ST_TRADED, "a_n": 1, "a_pts": -4.0, "b_status": "OK",
           "b_n": 0, "b_pts": 0.0, "offset": -4.88, "note": None}
    bf.save(db, a, [day], {"until": "2026-10-12"})
    import datetime as _dt
    got = bf.load_for_pnl(db, today=_dt.date(2026, 10, 9))
    assert len(got["a"]) == 1 and got["b"] == [] and got["meta"]["until"] == "2026-10-12"


def test_tool_skips_days_with_live_peter2_trades():
    s = _src("tools/peter2_backfill.py")
    assert "live_peter2_days" in s and "PETER2_ENTRY_SOURCE" in s


# ── 3. 패널 (dev 구조 — [미륵]/[신동] 모드 · 「피터2」·「피터2백필」 체크박스) ──────────
from dashboard.main_dashboard import PnlHistoryPanel  # noqa: E402

_DAY = "2026-10-07"


def _trade(src="SYSTEM_AUTO", net=100_000.0, day=_DAY):
    ts = day + " 10:00:00"
    return {"entry_ts": ts, "exit_ts": ts, "pnl_pts": 2.0, "pnl_krw": net,
            "forward_pnl_pts": 2.0, "forward_pnl_krw": net, "quantity": 1,
            "reverse_entry_enabled": 0, "entry_source": src}


def _bf_db(tmp_path, b_status="OK"):
    db = str(tmp_path / "bf.db")
    a = [{"src": "A", "trade_date": _DAY, "seq": 1, "side": "LONG",
          "entry_ts": _DAY + " 09:05:00", "exit_ts": _DAY + " 09:16:00",
          "entry_px": 1000.0, "exit_px": 1004.0, "pnl_pts": 4.0, "qty": 1,
          "gross_krw": 200_000.0, "notional_krw": 1_000.0 * PT, "exit_reason": "익절",
          "clipped": 0, "note": ""}]
    b = [dict(a[0], src="B", pnl_pts=3.0, gross_krw=150_000.0)]
    days = [{"trade_date": _DAY, "status": "TRADED", "a_n": 1, "a_pts": 4.0,
             "b_status": b_status, "b_n": 1, "b_pts": 3.0, "offset": -5.0, "note": None},
            {"trade_date": "2026-09-29", "status": "UNMEASURED", "a_n": None, "a_pts": None,
             "b_status": "NO_RAW", "b_n": None, "b_pts": None, "offset": None, "note": "x"}]
    bf.save(db, a + (b if b_status == "OK" else []), days, {"until": "2026-10-12"})
    return db


def _panel(monkeypatch, db, trades=None):
    import config.settings as _s
    monkeypatch.setattr(_s, "PETER2_BACKFILL_DB", db)
    # load_for_pnl 의 90일 창이 테스트 날짜를 자르지 않게 한다
    _orig = bf.load_for_pnl
    monkeypatch.setattr(bf, "load_for_pnl", lambda p, limit_days=90: _orig(p, limit_days=3650))
    p = PnlHistoryPanel()
    p._btn_mireuk.setChecked(True)
    p.refresh(trades if trades is not None else [_trade()])
    return p


def _set(p, fwd, rev, p2, p2bf):
    for cb, v in ((p._cb_forward, fwd), (p._cb_reverse, rev),
                  (p._cb_peter2, p2), (p._cb_p2bf, p2bf)):
        cb.blockSignals(True)
        cb.setChecked(v)
        cb.blockSignals(False)
    p._rebuild_all()


def _day(p, day=_DAY):
    rows = p._daily_bucket(p._active_rows()).get(day, [])
    return p._effective_day_krw(day, rows)


def test_bf_view_net_uses_channel_rate(monkeypatch, tmp_path):
    p = _panel(monkeypatch, _bf_db(tmp_path))
    _set(p, False, False, True, True)
    assert _day(p) == pytest.approx(200_000.0 - 1_000.0 * PT * LIVE_RATE * 2)
    assert all(r.get("is_bf") for r in p._active_rows())


def test_real_view_unchanged_by_backfill(monkeypatch, tmp_path):
    """🔴 백필은 가상 — 미륵 화면 값(브로커 net 포함)이 백필 유무와 무관해야 한다."""
    with_bf = _panel(monkeypatch, _bf_db(tmp_path))
    without = _panel(monkeypatch, str(tmp_path / "none.db"))
    for p in (with_bf, without):
        p._broker_pnl = {_DAY: 777_777.0}
        _set(p, True, True, True, False)
    assert _day(with_bf) == pytest.approx(_day(without)) == pytest.approx(777_777.0)
    assert with_bf._day_total_n == without._day_total_n, "가상이 완전성 분모에 끼었다"


def test_bf_exclusive_with_forward_reverse(monkeypatch, tmp_path):
    p = _panel(monkeypatch, _bf_db(tmp_path))
    _set(p, True, True, True, False)
    p._cb_p2bf.setChecked(True)                     # 사용자가 백필을 켠다
    assert not p._cb_forward.isChecked() and not p._cb_reverse.isChecked()
    assert p._cb_peter2.isChecked(), "피터2(실거래)는 백필과 함께 남는다"
    p._cb_forward.setChecked(True)                  # 사용자가 순방향을 켠다
    assert not p._cb_p2bf.isChecked()


def test_peter2_button_brings_backfill(monkeypatch, tmp_path):
    p = _panel(monkeypatch, _bf_db(tmp_path))
    p.set_peter2_only(True)
    assert p._cb_p2bf.isChecked() and p.is_peter2_only()
    p.set_peter2_only(False)
    assert not p._cb_p2bf.isChecked() and p._cb_forward.isChecked()


def test_b_column_only_in_bf_view_and_dash_when_unmeasured(monkeypatch, tmp_path):
    p = _panel(monkeypatch, _bf_db(tmp_path))
    col = p.tbl_daily.columnCount() - 1
    _set(p, True, True, True, False)
    assert p.tbl_daily.isColumnHidden(col)
    _set(p, False, False, True, True)
    assert not p.tbl_daily.isColumnHidden(col)
    txt = p.tbl_daily.item(0, col).text()
    assert txt.startswith("+") and txt.endswith("(1)")
    sub = tmp_path / "x"
    sub.mkdir()
    q = _panel(monkeypatch, _bf_db(sub, b_status="NO_RAW"))
    _set(q, False, False, True, True)
    assert q.tbl_daily.item(0, col).text() == "—", "B 미측정은 0원이 아니라 「—」"


def test_banner_unwired_and_counts(monkeypatch, tmp_path):
    p = _panel(monkeypatch, str(tmp_path / "none.db"))
    _set(p, False, False, True, True)
    assert "미배선" in p._mode_banner.text()
    q = _panel(monkeypatch, _bf_db(tmp_path))
    _set(q, False, False, True, True)
    t = q._mode_banner.text()
    assert "미측정 1일" in t and "전환 기준" in t and "B 재생 1건" in t


def test_shindong_mode_hides_backfill(monkeypatch, tmp_path):
    p = _panel(monkeypatch, _bf_db(tmp_path))
    _set(p, False, False, True, True)
    p._btn_shindong.setChecked(True)
    assert not p._bf_on() and not any(r.get("is_bf") for r in p._active_rows())
    assert p.tbl_daily.isColumnHidden(p.tbl_daily.columnCount() - 1)
