# -*- coding: utf-8 -*-
"""[MW0601 594차] ① <예고>가 피터맥점으로 가는가  ② 오프셋을 데이터로 재는가.

① 예고
    <1049 청산가>처럼 **앞으로 어디서 끊겠다**고 미리 말한 줄은 진입이 없다.
    종전에는 그 이유로 미분류(못읽음)로 셌는데, 선은 그려지고 있었다 -
    화면은 그리고 숫자는 <[!]못읽음>이라 **둘이 어긋났다.** 트윗 원문을 모으는
    목적이 그의 매매행태 추적이므로 예고도 그가 한 말이고 피터맥점에 속한다.
    [!] 다만 **이전 지시에 붙이지 않는다** - 무엇을 대체하는지 판단하지 않는
      원칙(588차)은 그대로다.

② 오프셋
    피터는 언제나 **정규 코스피200 선물(10100)**, 나는 **미니 당월물**이고 그
    종목은 롤마다 바뀐다. `offset = median(내 계약 종가 - 정규 종가)` 로 재며,
    실측 대조에서 사용자가 손으로 넣어온 값과 일치했다(09-04 -0.01 · 09-11 -4.47).
    [!] 못 재면 **0.0 이 아니라 None** 이어야 한다 - <못 쟀다>와 <0 이다>가
      같은 모양이면 화면이 조용히 틀린 가격을 그린다(계측 4원칙 ②).

실행:
    conda run -n py37_32 python -m pytest tests/test_594_peter_aux_and_offset.py -v
"""
import os
import sqlite3
import sys
from datetime import datetime, timedelta

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

os.environ["MIREUK_TEST_MODE"] = "1"
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtGui import QPixmap  # noqa: E402
from PyQt5.QtWidgets import QApplication  # noqa: E402

from dashboard.main_dashboard import (  # noqa: E402
    MinuteChartCanvas, parse_peter_orders, peter_offset_measure)

_APP = QApplication.instance() or QApplication(sys.argv)

_DAY = "2026-09-16"
_BASE = datetime(2026, 9, 16, 9, 0, 0)


def _ts(i):
    return (_BASE + timedelta(minutes=i)).strftime("%Y-%m-%d %H:%M:00")


def _candles(n=40, price=350.0):
    return [{"ts": _ts(i), "open": price, "high": price + 0.3,
             "low": price - 0.3, "close": price + (i % 5) * 0.1, "volume": 100}
            for i in range(n)]


# ── ① 예고 ──────────────────────────────────────────────────────────────────

_TWEETS = """1039 돌파시 매수 손절가 1036
9:00 AM · Sep 16, 2026

1049 청산가
9:15 AM · Sep 16, 2026

1049 청산체결.
9:32 AM · Sep 16, 2026

우리 개미들 화이팅
9:45 AM · Sep 16, 2026
"""


def test_target_only_line_becomes_aux_not_unknown():
    """실측 재현 - 09-16 <1049 청산가>."""
    od, rs, ax, uk = parse_peter_orders(_TWEETS, -4.00, _DAY)
    assert len(od) == 1 and od[0]["kind"] == "entry_brk"
    assert len(ax) == 1, "<1049 청산가>가 예고로 안 잡힌다."
    assert ax[0]["hm"] == "09:15"
    kinds = [m["kind"] for m in ax[0]["marks"]]
    assert "target" in kinds
    assert ax[0]["marks"][0]["level_adj"] == 1045.0, "오프셋이 예고에 안 먹었다."
    assert len(rs) == 1, "<청산체결>은 결과다 - 예고로 새면 안 된다."
    assert not any("1049 청산가" in x["raw"] for x in uk), (
        "예고가 아직도 미분류에 남아 있다 - 상태줄이 <못읽음>으로 거짓말한다.")


def test_plain_chatter_is_still_unknown():
    """대조군 - 숫자 없는 잡담이 예고로 승격되면 예고 자체가 무의미해진다."""
    od, rs, ax, uk = parse_peter_orders(
        "우리 개미들 화이팅\n9:45 AM · Sep 16, 2026\n", -4.00, _DAY)
    assert ax == [] and len(uk) == 1


def test_entry_line_is_never_downgraded_to_aux():
    """진입이 있으면 지시다. 손절이 함께 있다고 예고로 내려가면 깃발이 사라진다."""
    od, rs, ax, uk = parse_peter_orders(
        "1039 돌파시 매수 손절가 1036\n9:00 AM · Sep 16, 2026\n", -4.00, _DAY)
    assert len(od) == 1 and ax == []


def test_aux_belongs_to_the_peter_level_layer():
    """예고는 <피터맥점> 소속 - <거래피터>로 새지 않는다(593차 불변식)."""
    c = MinuteChartCanvas()
    c.resize(900, 500)
    c.reset_session(_candles(), [])
    _od, _rs, _ax, _uk = parse_peter_orders(_TWEETS, -1049.0 + 350.5, _DAY)
    c.set_peter([], [], _od, _ax)

    def _render(lv, tp):
        c.set_overlay("peter_lv", lv)
        c.set_overlay("trade_peter", tp)
        pm = QPixmap(c.size())
        c.render(pm)

    _render(True, True)
    assert c._peter_aux_labels, "피터맥점을 켰는데 예고 칩이 없다."
    _render(False, True)
    assert c._peter_aux_labels == [], "피터맥점을 껐는데 예고 칩이 남았다."


# ── ② 오프셋 ────────────────────────────────────────────────────────────────

def _make_regular_db(tmpdir, day, closes):
    os.makedirs(tmpdir, exist_ok=True)
    p = os.path.join(tmpdir, "regular_candles.db")
    con = sqlite3.connect(p)
    con.execute("CREATE TABLE regular_candles (code TEXT, ts TEXT, trade_date TEXT,"
                " open REAL, high REAL, low REAL, close REAL)")
    con.executemany("INSERT INTO regular_candles(code,ts,trade_date,close)"
                    " VALUES('10100',?,?,?)",
                    [(_ts(i), day, v) for i, v in enumerate(closes)])
    con.commit()
    con.close()
    return p


def test_offset_is_my_contract_minus_regular(tmp_path, monkeypatch):
    """부호를 못 박는다 - 미륵이 = 정규 + offset. 내 계약이 4p 낮으면 -4.00."""
    import config.settings as _cfg
    cs = _candles()
    # 정규는 내 계약보다 정확히 4.00 높다
    _make_regular_db(str(tmp_path), _DAY, [c["close"] + 4.00 for c in cs])
    monkeypatch.setattr(_cfg, "DB_DIR", str(tmp_path), raising=False)
    val, n, why, info = peter_offset_measure(_DAY, cs)
    assert why == "" and val == -4.00, (val, n, why)
    assert n == len(cs)
    assert info["full"] == -4.00 and info["n_full"] == len(cs)


def test_offset_returns_none_not_zero_when_unmeasurable(tmp_path, monkeypatch):
    """[!] <못 쟀다>와 <0.00 이다>는 절대 같은 모양이면 안 된다."""
    import config.settings as _cfg
    monkeypatch.setattr(_cfg, "DB_DIR", str(tmp_path), raising=False)
    val, n, why, _ = peter_offset_measure(_DAY, _candles())
    assert val is None and why, "정규 DB 가 없는데 값을 돌려줬다."

    val2, n2, why2, _ = peter_offset_measure(_DAY, [])
    assert val2 is None and "캔들" in why2


def test_offset_refuses_a_thin_overlap(tmp_path, monkeypatch):
    """몇 봉만 겹치면 롤·수집 구멍이다. 그 값으로 그리면 조용히 틀린다."""
    import config.settings as _cfg
    cs = _candles()
    _make_regular_db(str(tmp_path), _DAY, [c["close"] + 4.00 for c in cs[:5]])
    monkeypatch.setattr(_cfg, "DB_DIR", str(tmp_path), raising=False)
    val, n, why, _ = peter_offset_measure(_DAY, cs)
    assert val is None and "적다" in why


def test_offset_uses_the_morning_window_only(tmp_path, monkeypatch):
    """[596차] 오프셋은 하루 안에서 **방향을 갖고** 움직인다 - 오전으로만 잰다.

    실측(09-16): 09:00 -4.01 -> 12:00 -4.63 -> 15:00 -4.40. 전일정 중앙값을 쓰면
    오전 매매가 0.4p 밀린다. 오후 값을 크게 어긋나게 넣어 창이 실제로 닫히는지 본다.
    """
    import config.settings as _cfg
    from dashboard.main_dashboard import PETER_OFFSET_WINDOW
    # 09:00~11:29 는 -4.00, 그 뒤는 -9.00 이 되도록 정규를 만든다
    cs = [{"ts": (_BASE + timedelta(minutes=i)).strftime("%Y-%m-%d %H:%M:00"),
           "open": 350.0, "high": 350.3, "low": 349.7, "close": 350.0, "volume": 1}
          for i in range(360)]                      # 09:00 ~ 14:59
    reg = []
    for c in cs:
        hm = c["ts"][11:16]
        reg.append(c["close"] + (4.00 if PETER_OFFSET_WINDOW[0] <= hm
                                 < PETER_OFFSET_WINDOW[1] else 9.00))
    _make_regular_db(str(tmp_path), _DAY, reg)
    monkeypatch.setattr(_cfg, "DB_DIR", str(tmp_path), raising=False)
    val, n, why, info = peter_offset_measure(_DAY, cs)
    assert val == -4.00, "오전 창 밖의 값이 새어 들어왔다 - %s" % val
    assert n == 150, n
    assert info["full"] == -9.00, "전일정 값이 참고로 함께 나와야 한다(드리프트 은폐 금지)."
    assert info["lo"] == -9.00 and info["hi"] == -4.00, (info["lo"], info["hi"])


def test_dialog_prefers_the_measured_value_over_the_saved_one():
    """[596차] 실측값이 기본값이다 - 저장값이 계속 따라다니면 안 된다.

    다만 **소리 없이 버리지 않는다**: 되돌리기 버튼이 함께 떠야 한다.
    """
    import inspect
    from dashboard.main_dashboard import MinuteChartDialog
    src = inspect.getsource(MinuteChartDialog._open_peter_input)
    i_mv = src.index("if _mv is not None:\n                _sp.setValue(_mv)")
    i_saved = src.index("elif _saved is not None:")
    assert i_mv < i_saved, "저장값이 실측값보다 먼저 들어간다."
    assert "저장 %+.2f 으로" in src, "되돌리기 버튼이 없다 - 손으로 넣은 값이 사라진다."


# ── ③ 거래피터 - 진입·청산 **가격**이 화면에 있다 ───────────────────────────

def test_trade_chip_shows_entry_and_exit_prices():
    """종전 칩은 시각만 있어 <+10.00p>가 어디서 나온 수인지 확인이 안 됐다."""
    import inspect
    src = inspect.getsource(MinuteChartCanvas._draw_peter_labels)
    assert "entry_price" in src and "exit_price" in src, (
        "거래 라벨이 진입·청산 가격을 쓰지 않는다.")
