# -*- coding: utf-8 -*-
"""[MW0601 677차] 피터2 백필 — 실거래 개시(10/12) 이전 손익을 손익추이·손익추이2 에 올린다.

사용자 지시(2026-10-09)
    · 10/12 이전 손익추이는 1분봉 차트 「거래피터」(원천 A)로 산출해 올린다.
    · 재생(원천 B)은 비교 열로 함께 넣는다.
    · 손익추이2(CREON 요율 반사실)에도 넣는다 — 실거래는 CREON 예정.
    · 기록 없는 날은 사용자가 「미측정」으로 적는다.

고정하는 것
    1. A 환산 규칙 — pt 는 그의 가격 차, 15:10 이후 청산은 15:10 가격으로 재측정,
       14:50 이후 진입 제외, 못 맞춘 줄은 버리지 않는다.
    2. 일자 상태 — LIVE > UNMEASURED > 사료 유무. 「미판정」을 0건으로 세지 않는다.
    3. 패널 — 백필은 **가상**: 실거래 화면의 값(브로커 net 포함)이 백필 유무와 무관하게 같다.
       탭마다 자기 요율로 수수료를 뗀다. 실거래 출처와 배타 · 피터2(실거래)와는 공존.
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


# ── 3. 패널 ────────────────────────────────────────────────────────────
from dashboard.main_dashboard import PnlHistoryPanel  # noqa: E402


class _Row(dict):
    def keys(self):
        return list(super(_Row, self).keys())


def _trade(day="2026-10-07", src="SYSTEM_AUTO", net=100_000.0):
    ts = day + " 10:00:00"
    return _Row({"entry_ts": ts, "exit_ts": ts, "pnl_pts": 2.0, "pnl_krw": net,
                 "forward_pnl_pts": 2.0, "forward_pnl_krw": net, "quantity": 1,
                 "reverse_entry_enabled": 0, "gross_pnl_krw": net, "commission_krw": 0.0,
                 "commission_rate_used": LIVE_RATE, "entry_source": src,
                 "exit_reason": "TP1", "direction": "LONG", "grade": "A"})


def _bf_payload(b_status="OK"):
    a = [{"src": "A", "trade_date": "2026-10-07", "seq": 1, "side": "LONG",
          "entry_ts": "2026-10-07 09:05:00", "exit_ts": "2026-10-07 09:16:00",
          "pnl_pts": 4.0, "qty": 1, "gross_krw": 200_000.0, "notional_krw": 1_000.0 * PT,
          "exit_reason": "익절", "clipped": 0}]
    b = [{"src": "B", "trade_date": "2026-10-07", "seq": 1, "side": "LONG",
          "entry_ts": "2026-10-07 09:05:20", "exit_ts": "2026-10-07 09:16:20",
          "pnl_pts": 3.0, "qty": 1, "gross_krw": 150_000.0, "notional_krw": 1_000.0 * PT}]
    days = [{"trade_date": "2026-10-07", "status": "TRADED", "b_status": b_status},
            {"trade_date": "2026-09-29", "status": "UNMEASURED", "b_status": "NO_RAW"}]
    return {"a": a, "b": b if b_status == "OK" else [], "days": days,
            "meta": {"until": "2026-10-12", "latency_sec": 20}}


def _set(p, keys):
    for k, cb in p._cb_origin.items():
        cb.blockSignals(True)
        cb.setChecked(k in keys)
        cb.blockSignals(False)
    p._cb_forward.setChecked(True)
    p._cb_reverse.setChecked(True)
    p._rebuild_tables()


def _panel(mode="live", bfp="default"):
    p = PnlHistoryPanel(rate_mode=mode)
    p.refresh([_trade()], bf=_bf_payload() if bfp == "default" else bfp)
    return p


def _day(p, day="2026-10-07"):
    rows = p._daily_bucket(p._active_rows()).get(day, [])
    return p._effective_day_krw(day, rows)


def test_origin_keys_and_labels():
    assert PnlHistoryPanel._ORIGIN_KEYS == ("auto", "manual", "unknown", "pt2", "pt2bf", "sd")
    tip = PnlHistoryPanel._ORIGIN_TIP["pt2bf"]
    assert "가상" in tip and "전환기준" in tip


@pytest.mark.parametrize("mode,rate", [("live", LIVE_RATE), ("creon", CREON_RATE)])
def test_bf_net_uses_each_tab_rate(mode, rate):
    p = _panel(mode)
    _set(p, {"pt2", "pt2bf"})
    assert _day(p) == pytest.approx(200_000.0 - 1_000.0 * PT * rate * 2)


def test_creon_tab_bf_is_cheaper_than_live():
    live, cf = _panel("live"), _panel("creon")
    _set(live, {"pt2bf"})
    _set(cf, {"pt2bf"})
    assert _day(cf) > _day(live)


@pytest.mark.parametrize("mode", ["live", "creon"])
def test_real_view_unchanged_by_backfill(mode):
    """🔴 백필은 가상 — 실거래 화면 값(브로커 net 경로 포함)이 백필 유무와 무관해야 한다."""
    with_bf, without = _panel(mode), _panel(mode, bfp=None)
    for p in (with_bf, without):
        p._broker_pnl = {"2026-10-07": 777_777.0}
        p._broker_gross = {"2026-10-07": 800_000.0}
        p._broker_comm = {"2026-10-07": 20_000.0}
        _set(p, {"auto", "manual", "unknown", "pt2"})
    assert not any(r.get("is_bf") for r in with_bf._active_rows())
    assert _day(with_bf) == pytest.approx(_day(without))
    assert with_bf._day_total_legs == without._day_total_legs, "가상이 완전성 분모에 끼었다"


def test_bf_exclusive_with_real_but_coexists_with_pt2():
    p = _panel()
    _set(p, {"auto", "manual", "unknown", "pt2"})
    p._cb_origin["pt2bf"].setChecked(True)            # 사용자가 백필을 켠다
    assert not any(p._cb_origin[k].isChecked() for k in ("auto", "manual", "unknown", "sd"))
    assert p._cb_origin["pt2"].isChecked(), "피터2(실거래)는 백필과 함께 남는다"
    p._cb_origin["auto"].setChecked(True)             # 사용자가 자동을 켠다
    assert not p._cb_origin["pt2bf"].isChecked()
    _set(p, {"auto", "pt2bf"})                        # 저장값·전파로 섞여 들어와도
    assert p._active_origins() == {"pt2bf"}


def test_b_column_only_in_bf_view_and_dash_when_unmeasured():
    p = _panel()
    col = p.tbl_daily.columnCount() - 1
    _set(p, {"auto", "manual", "unknown", "pt2"})
    assert p.tbl_daily.isColumnHidden(col)
    _set(p, {"pt2", "pt2bf"})
    assert not p.tbl_daily.isColumnHidden(col)
    txt = p.tbl_daily.item(0, col).text()
    assert txt.endswith("(1)") and txt.startswith("+")
    q = _panel(bfp=_bf_payload(b_status="NO_RAW"))
    _set(q, {"pt2bf"})
    assert q.tbl_daily.item(0, col).text() == "—", "B 미측정은 0원이 아니라 「—」"


def test_banner_unwired_and_counts():
    p = _panel(bfp=None)
    _set(p, {"pt2bf"})
    assert "미배선" in p._bf_banner.text()
    q = _panel("creon")
    _set(q, {"pt2bf"})
    t = q._bf_banner.text()
    assert "CREON" in t and "미측정 1일" in t and "전환기준" in t


def test_wiring_main_and_logpanel():
    s = _src("main.py")
    assert "load_for_pnl(runtime_settings.PETER2_BACKFILL_DB" in s
    assert "sd_wired=_sd_wired, bf=_bf)" in s
    d = _src("dashboard/main_dashboard.py")
    assert "self.pnl_history_cf.refresh(rows, bf=bf)" in d, "손익추이2 에도 백필을 넘긴다"
