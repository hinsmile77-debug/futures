# -*- coding: utf-8 -*-
"""[MW0601 613차] 선물 수급 4종 시계열 — 원천 보존 · 조회 · 표시 회귀 가드.

613차는 「선물 투자자 수급」 6카드를 걷어내고 그중 4종을 개인 옵션 6종과 같은
증감 시계열로 옮겼다(사용자 지시 2026-09-21). 그 과정에서 **없던 원천 보존이
새로 생겼다** — 외인 선물 순매수 원값은 그때까지 어디에도 남지 않았다.

여기서 고정하는 것:
  1. `save_investor_futures_raw` 가 빈 dict 를 저장하지 않는다 (451차 규약)
  2. `get_futures_raw_fields` 가 **미측정 키를 만들지 않는다**
  3. provider 가 첫 바 기준 차분을 내고, 결측을 0 으로 잇지 않는다
  4. provider 가 빈 DB 에서 `{}` 를 준다 (0 이 아니다)
  5. 로그압축 역변환이 왕복 무손실이다
  6. 백필이 **실측(live) 행을 덮지 않는다**
  7. 배선 — 저장이 OI 동기화 뒤에, push 가 저장 뒤에 있다
  8. 차트가 두 payload 를 **따로** 들고 있다 (한쪽 실패가 다른 쪽을 안 지운다)
"""
import io
import json
import math
import os
import sqlite3
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MAIN = os.path.join(_ROOT, "main.py")
_CHART = os.path.join(_ROOT, "dashboard", "panels", "option_flow_delta_chart.py")
_DASH = os.path.join(_ROOT, "dashboard", "main_dashboard.py")


_QAPP = None    # QApplication 을 붙들어 두는 자리(아래 주석 참조)


def _src(path):
    return io.open(path, encoding="utf-8").read()


def _mk_db(tmp_path, investor_rows=(), program_rows=(), candle_rows=()):
    """provider 가 읽는 3테이블만 갖춘 최소 DB."""
    p = str(tmp_path / "raw.db")
    con = sqlite3.connect(p)
    con.execute("CREATE TABLE raw_investor_futures (ts TEXT PRIMARY KEY, "
                "fields TEXT, src TEXT)")
    con.execute("CREATE TABLE raw_program_trade (ts TEXT, market TEXT, "
                "fields TEXT, PRIMARY KEY (ts, market))")
    con.execute("CREATE TABLE raw_candles (ts TEXT PRIMARY KEY, oi INTEGER)")
    con.executemany("INSERT INTO raw_investor_futures VALUES (?,?,?)",
                    investor_rows)
    con.executemany("INSERT INTO raw_program_trade VALUES (?,?,?)", program_rows)
    con.executemany("INSERT INTO raw_candles VALUES (?,?)", candle_rows)
    con.commit()
    con.close()
    return p


# ── 1. 원천 보존 ──────────────────────────────────────────────────────────

def test_1_empty_fields_are_not_saved(tmp_path, monkeypatch):
    """🔴 빈 dict 를 저장하면 「그 시각엔 수급이 0이었다」로 오독된다(451차)."""
    import utils.db_utils as du

    calls = []
    monkeypatch.setattr(du, "execute", lambda *a, **k: calls.append(a))
    assert du.save_investor_futures_raw("2026-09-21 09:02:00", {}) is False
    assert calls == [], "빈 행이 저장됐다"
    assert du.save_investor_futures_raw(
        "2026-09-21 09:02:00", {"foreign_net_qty": 1}) is True
    assert len(calls) == 1


def test_2_unmeasured_keys_are_not_fabricated():
    """🔴 `_futures` 는 이월 폴백이라 항상 값이 있다 — 그대로 덤프하면
    「받은 적 없는 0」이 실측 0 으로 굳는다(계측 4원칙 ②)."""
    from collection.cybos.investor_data import CybosInvestorData

    inv = CybosInvestorData(None)
    # 아무것도 안 받은 상태 — 값은 0 으로 채워져 있지만 측정된 적은 없다.
    assert inv.get_futures_raw_fields() == {}

    inv._futures_supported = True
    inv._futures_seen.add("foreign")
    inv._futures["foreign"] = 4953
    inv._open_interest = 62585
    out = inv.get_futures_raw_fields()
    assert out["foreign_net_qty"] == 4953
    assert out["open_interest"] == 62585
    # 금액 축은 따로 센다 — 계약만 왔으면 금액 키를 만들지 않는다(612차 후속2).
    assert "foreign_amt_mn" not in out
    # 안 받은 투자자의 키도 없다.
    assert "retail_net_qty" not in out


def test_3_unit_is_in_the_key_name():
    """계측 4원칙 ① — 단위는 이름에 박는다."""
    from collection.cybos.investor_data import CybosInvestorData

    inv = CybosInvestorData(None)
    inv._futures_supported = True
    inv._futures_seen.update(("foreign", "individual"))
    inv._futures_amt_seen.add("foreign")
    inv._futures["foreign"] = 10
    inv._futures_amt["foreign"] = 2780
    out = inv.get_futures_raw_fields()
    assert "foreign_net_qty" in out and "foreign_amt_mn" in out
    for k in out:
        assert k.endswith(("_qty", "_mn")) or k == "open_interest", k


# ── 2. 조회 provider ──────────────────────────────────────────────────────

def test_4_empty_db_yields_empty_products(tmp_path):
    """수집 전에는 `{}` 다 — 0 이 아니다."""
    from collection.cybos.futures_flow_series import get_futures_session_delta

    d = get_futures_session_delta("2026-09-21", _mk_db(tmp_path))
    assert d["products"] == {} and d["last_time"] is None


def test_5_delta_is_from_first_bar(tmp_path):
    """네 행 모두 당일 첫 바를 0 으로 놓은 차분이다(사용자 결정)."""
    from collection.cybos.futures_flow_series import get_futures_session_delta

    db = _mk_db(
        tmp_path,
        investor_rows=[
            ("2026-09-21 09:02:00", json.dumps({"foreign_net_qty": -100}), "live"),
            ("2026-09-21 09:03:00", json.dumps({"foreign_net_qty": 400}), "live"),
        ],
        program_rows=[
            ("2026-09-21 09:02:00", "1", json.dumps({"19": -11038, "37": -32922})),
            ("2026-09-21 09:03:00", "1", json.dumps({"19": 1000, "37": 2000})),
        ],
        candle_rows=[("2026-09-21 08:45:00", 59840),
                     ("2026-09-21 08:46:00", 59900)],
    )
    d = get_futures_session_delta("2026-09-21", db)["products"]
    assert d["fut_fi"]["series"] == [("09:02", 0), ("09:03", 500)]
    assert d["fut_fi"]["delta"] == 500
    assert d["fut_fi"]["value"] == 400, "누계(카드가 보여주던 값)도 함께 실린다"
    assert d["prog_arb"]["delta"] == 1000 - (-11038)
    assert d["open_int"]["baseline_time"] == "08:45"
    assert d["open_int"]["delta"] == 60


def test_6_missing_minutes_are_not_bridged_with_zero(tmp_path):
    """결측 분에는 점을 찍지 않는다 — 0 으로 잇지 않는다(계측 4원칙 ②)."""
    from collection.cybos.futures_flow_series import get_futures_session_delta

    db = _mk_db(tmp_path, investor_rows=[
        ("2026-09-21 09:02:00", json.dumps({"foreign_net_qty": 0}), "live"),
        ("2026-09-21 09:10:00", json.dumps({"foreign_net_qty": 7}), "live"),
    ])
    s = get_futures_session_delta("2026-09-21", db)["products"]["fut_fi"]["series"]
    assert [t for t, _ in s] == ["09:02", "09:10"], "빈 분이 채워졌다"


def test_7_oi_zero_is_treated_as_missing(tmp_path):
    """`raw_candles.oi = 0` 은 미수신이다 — 실측 0계약이 아니다."""
    from collection.cybos.futures_flow_series import get_futures_session_delta

    db = _mk_db(tmp_path, candle_rows=[("2026-09-21 08:45:00", 0),
                                       ("2026-09-21 08:46:00", 59900)])
    d = get_futures_session_delta("2026-09-21", db)["products"]
    assert d["open_int"]["baseline_time"] == "08:46"


def test_8_oi_tail_comes_from_investor_table_only_after_candles_stop(tmp_path):
    """분봉은 15:09 에 끝난다 — 그 뒤만 수급 테이블이 이어받는다.

    같은 분을 두 원천으로 두 번 찍으면 관측 시점이 다른 값이 섞인다.
    """
    from collection.cybos.futures_flow_series import get_futures_session_delta

    db = _mk_db(
        tmp_path,
        investor_rows=[
            # 캔들과 겹치는 분 — 쓰이면 안 된다
            ("2026-09-21 15:08:00", json.dumps({"open_interest": 99999}), "live"),
            ("2026-09-21 15:20:00", json.dumps({"open_interest": 62600}), "live"),
        ],
        candle_rows=[("2026-09-21 08:45:00", 61186),
                     ("2026-09-21 15:08:00", 62500)],
    )
    s = get_futures_session_delta("2026-09-21", db)["products"]["open_int"]["series"]
    assert [t for t, _ in s] == ["08:45", "15:08", "15:20"]
    assert s[1][1] == 62500 - 61186, "겹치는 분을 수급 테이블이 덮었다"


def test_9_provider_marks_derived_rows(tmp_path):
    """백필 행은 실측과 구분돼야 한다(계측 4원칙 ②·④)."""
    from collection.cybos.futures_flow_series import get_futures_session_delta

    db = _mk_db(tmp_path, investor_rows=[
        ("2026-09-21 09:02:00", json.dumps({"foreign_net_qty": 1}), "derived"),
        ("2026-09-21 09:03:00", json.dumps({"foreign_net_qty": 2}), "derived"),
    ])
    assert get_futures_session_delta(
        "2026-09-21", db)["products"]["fut_fi"]["src"] == "derived"


# ── 3. 백필 ───────────────────────────────────────────────────────────────

def test_10_log_compression_roundtrip_is_lossless():
    """역변환 정확도 — 실측 대조로 확인된 값들(2026-09-21 15:06 로그)."""
    from scripts.backfill_investor_futures import _inv_log

    for raw in (4953, -146, -4850, 6224, 1, -1, 541664):
        f = math.copysign(math.log1p(abs(raw) / 1000.0), raw)
        assert _inv_log(f) == raw, raw


def test_11_pre_compression_era_is_detected_per_day():
    """🔴 행 단위로 판정하면 원값 시대의 작은 값이 3,000배로 부풀려진다.

    실측: 2026-06-02·04·05·08 4거래일은 압축 전이라 원값이 그대로 있다
    (최대 541,664). 그 값을 역변환하면 expm1 이 넘친다(OverflowError).
    """
    from scripts.backfill_investor_futures import (_COMPRESSED_ABS_MAX,
                                                   _scan_compression_era)

    class _Con(object):
        def __init__(self, rows):
            self._rows = rows

        def execute(self, *a, **k):
            return iter(self._rows)

    rows = [
        ("2026-06-05 09:00:00", json.dumps({"foreign_futures_net": 541664.0})),
        ("2026-06-05 09:01:00", json.dumps({"foreign_futures_net": 3.0})),
        ("2026-09-18 09:00:00", json.dumps({"foreign_futures_net": 1.8})),
    ]
    era = _scan_compression_era(_Con(rows), "", ())
    assert era["2026-06-05"] is False, "원값 시대를 압축으로 오판했다"
    assert era["2026-09-18"] is True
    assert _COMPRESSED_ABS_MAX > 7.0, "현실적 순매수의 압축값 상한보다 커야 한다"


def test_12_backfill_never_overwrites_live_rows():
    """실측(live) 을 파생으로 덮으면 안 된다."""
    src = _src(os.path.join(_ROOT, "scripts", "backfill_investor_futures.py"))
    assert "INSERT OR IGNORE INTO raw_investor_futures" in src, (
        "INSERT OR REPLACE 로 바뀌면 실측 행이 파생으로 덮인다")
    assert "SELECT ts FROM raw_investor_futures" in src, "기존 행 확인이 없다"


def test_13_backfill_guards_intraday():
    """라이브 DB 전수 스캔 — 장중이면 CB⑤ 를 부른다(456차)."""
    src = _src(os.path.join(_ROOT, "scripts", "backfill_investor_futures.py"))
    assert "guard_intraday(" in src


# ── 4. 배선 ───────────────────────────────────────────────────────────────

def test_14_save_is_after_oi_sync_and_push_is_after_save():
    """🔴 순서가 의미를 만든다.

    · 저장이 OI 동기화보다 앞이면 그 분의 `open_interest` 가 한 틱 낡는다.
    · push 가 저장보다 앞이면 방금 분이 화면에 안 실린다.
    """
    src = _src(_MAIN)
    i_oi = src.index("self.investor_data._open_interest = oi")
    i_save = src.index("self._save_investor_futures_raw(now)")
    i_push = src.index("self._push_futures_flow_series()")
    assert i_oi < i_save < i_push


def test_15_side_paths_never_raise():
    """보조 경로가 수급 수집을 흔들면 안 된다(611차 후속이 실증)."""
    src = _src(_MAIN)
    for fn in ("_save_investor_futures_raw", "_push_futures_flow_series"):
        body = src[src.index("def %s(" % fn):]
        body = body[:body.index("\n    def ")]
        assert "except Exception" in body, fn
    # 실패를 조용히 삼키지도 않는다(계측 4원칙 ④).
    assert "_investor_raw_err_logged" in src
    assert "_futures_flow_err_logged" in src


def test_16_widget_keeps_two_payloads_separately():
    """한쪽 조회 실패가 다른 쪽 행을 지우면 안 된다."""
    src = _src(_CHART)
    assert "self._fut_payload" in src and "self._payload" in src
    assert "def update_futures_flow" in src
    body = src[src.index("def _merged"):]
    assert "prods.update" in body, "두 payload 를 합치는 경로가 없다"


def test_17_widget_does_not_open_db():
    """GUI 스레드가 DB 를 열면 paint 가 막힌다 — 조회는 타이머 경로가 한다."""
    src = _src(_CHART)
    code = "\n".join(ln for ln in src.splitlines()
                     if not ln.lstrip().startswith("#"))
    # ⚠ docstring 은 그 함수 이름을 **인용**한다(어디서 오는 값인지 적어야 하니까).
    #   그래서 이름이 아니라 **import·연결 자체**를 막는다.
    for bad in ("sqlite3", "raw_data.db", "futures_flow_series import",
                "import futures_flow_series"):
        assert bad not in code, "차트 위젯이 DB 에 직접 접근한다: %s" % bad


def test_18_shared_scale_is_per_group():
    """옵션(계약)과 프로그램(백만원)을 한 눈금에 올리면 그 자체가 오독이다."""
    from dashboard.panels.option_flow_delta_chart import _ALL_ROWS

    groups = dict((k, g) for k, _lab, g in _ALL_ROWS)
    assert groups["wk_mon_call"] == "opt" and groups["prog_arb"] == "fut"
    assert "_group_max" in _src(_CHART)


def test_19_row_order_matches_instruction():
    """사용자 지시 순서 — 옵션 6종 뒤 미결제·외인·차익·비차익."""
    from dashboard.panels.option_flow_delta_chart import _ALL_ROWS, _FUT_ROWS

    assert [k for k, _ in _FUT_ROWS] == [
        "open_int", "fut_fi", "prog_arb", "prog_nonarb"]
    assert [k for k, _lab, _g in _ALL_ROWS][-4:] == [
        "open_int", "fut_fi", "prog_arb", "prog_nonarb"]
    assert len(_ALL_ROWS) == 10


def test_20_removed_cards_are_gone_but_data_keys_remain():
    """🔴 사라진 것은 **화면 표시뿐**이어야 한다.

    개인·기관 선물 순매수는 지시대로 표시에서 빠졌지만, `get_panel_data()` 의
    키는 `div_score`·피처·다른 소비처가 계속 쓴다.
    """
    dash = _src(_DASH)
    for gone in ("fut_fut_fi_val", "fut_prog_arb_val", "fut_open_int_val"):
        assert gone not in dash, "걷어낸 카드 위젯이 남아 있다: %s" % gone
    inv = _src(os.path.join(_ROOT, "collection", "cybos", "investor_data.py"))
    for keep in ("retail_futures_amt_mn", "institution_futures_amt_mn",
                 "program_arb_net", "open_interest"):
        assert '"%s"' % keep in inv, "수집 키가 함께 지워졌다: %s" % keep


def test_21_itm_otm_widgets_are_none_not_zero():
    """ITM·OTM 은 구조적으로 영원히 N/A — 0% 로 그리면 실측처럼 보인다."""
    dash = _src(_DASH)
    assert 'setattr(self, f"oz_{zone}_{inv}", None)' in dash
    # update_data 의 None 가드가 살아 있어야 한다.
    assert "if widget is None:" in dash


def test_22_freshness_chip_keeps_three_levels():
    """「그냥 좀 낡음」과 「멈춤」을 색으로 가른다(612차 후속5)."""
    dash = _src(_DASH)
    assert 'ch.set_age_text(txt, "stop" if age > 600' in dash
    chart = _src(_CHART)
    assert '"stop": _COL["red"]' in chart and '"warn": _COL["orange"]' in chart


def test_23_row_height_is_elastic():
    """아래에서 비운 세로가 차트로 흘러와야 한다(613차 지시)."""
    from dashboard.panels.option_flow_delta_chart import _Plot

    assert _Plot.MIN_ROW_H < _Plot.MAX_ROW_H
    assert "def row_height" in _src(_CHART)
    assert "QSizePolicy.Expanding" in _src(_CHART)


def test_24_row_height_fills_available_space():
    """🔴 [615차] 상한이 낮으면 비운 세로가 차트 아래 **빈칸**으로 남는다.

    614차 라이브 화면 실측(2026-09-21): 가용 세로가 행당 약 103px 인데 상한 64 가
    640px 에서 잘라 아래 약 390px 이 빈 채였다. 아래 블록을 압축해 얻은 세로가
    시인성으로 가지 못하고 그냥 사라진 것이다(613·615차 지시의 정반대).
    """
    import os as _os
    _os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PyQt5.QtWidgets import QApplication
    # ⚠ **반환값을 붙들어야 한다.** `QApplication.instance() or QApplication([])`
    #   처럼 버리면 즉시 GC 돼 프로세스가 통째로 죽는다(실행 중 실제로 죽었다).
    global _QAPP
    _QAPP = QApplication.instance() or QApplication([])
    from dashboard.panels.option_flow_delta_chart import _LAYOUT, _Plot

    pl = _Plot()
    # 실사용 높이에서 행이 그 높이를 **거의 다 쓴다**
    # [621차] 콜↔풋 상대강도 2행(높이 가중 0.6)이 들어와 행 수가 10 → 12 가 됐다.
    #   그래서 행당 높이 하한을 95 → 85(→ 후속3 80) 로, 「다 쓴다」는 실제 배치(row_spans)로 잰다.
    #   불변식(비운 세로가 차트로 온다)은 그대로다.
    pl.setFixedHeight(1030)
    r = pl.row_height()
    top, hh = pl.row_spans(r)[-1]
    # [621차 후속2] 시간 눈금 띠가 행 위로 옮겨가 top 에 이미 포함된다.
    used = top + hh + _Plot.PAD_V
    # [621차 후속3] 먼스리 콜↔풋 행이 더해져 13행 — 행당 높이 85 → 84. 하한을 80 으로.
    #   「비운 세로가 차트로 온다」는 바로 아래 used 단언이 그대로 지킨다.
    assert r >= 80, "행이 가용 세로를 안 쓴다(상한이 다시 낮아졌다): %d" % r
    assert used >= 1030 - 2 * len(_LAYOUT), "아래에 빈칸이 남는다: %d/1030" % used
    assert used <= 1030, "행이 위젯 밖으로 넘친다: %d/1030" % used
    # 작은 창에서는 하한을 지킨다
    pl.setFixedHeight(200)
    assert pl.row_height() == _Plot.MIN_ROW_H
