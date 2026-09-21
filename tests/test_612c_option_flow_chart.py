# tests/test_612c_option_flow_chart.py
"""[MW0601 612차 후속3] 「투자자 포지션 매트릭스」 → 개인 옵션 6종 증감 시계열.

사용자 지시(2026-09-21):
  ① 바이어스 미터 2행(개인/외인 방향 풋·콜) 삭제
  ② 「선물 투자자 수급」을 맨 위로
  ③ 매트릭스를 개인 (월)위클리·(목)위클리·먼스리 콜/풋 6종의
     08:45~15:35 「시초 대비 계약수 증감」으로 리모델링
  · 기준점 = 당일 첫 바  · 역발상/다이버전스 2칸 = 완전 제거

왜 매트릭스를 통째로 바꿨나 — 611차가 개인의 주무대를 잘못 보고 있었음을
실측으로 보였다. 종전 8칸은 전부 `CpSvrNew7221` 의 **금액 축 월물** 콜/풋인데,
개인의 옵션 거래는 **위클리에 집중**돼 있다(2026-09-21 실측 월위클리 콜 +9,656
vs 먼스리 콜 −244, 약 40배).
"""
from __future__ import annotations

import os

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CHART = os.path.join(_ROOT, "dashboard", "panels", "option_flow_delta_chart.py")
_FLOW = os.path.join(_ROOT, "collection", "cybos", "weekly_option_flow.py")
_DASH = os.path.join(_ROOT, "dashboard", "main_dashboard.py")
_MAIN = os.path.join(_ROOT, "main.py")


def _src(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ── 데이터 계층 ───────────────────────────────────────────────────────────

def test_1_dashboard_products_are_the_six_requested():
    from collection.cybos.weekly_option_flow import WeeklyOptionFlow

    keys = [k for k, _ in WeeklyOptionFlow.DASHBOARD_PRODUCTS]
    assert keys == ["wk_mon_call", "wk_mon_put", "wk_thu_call", "wk_thu_put",
                    "mon_call", "mon_put"], "지시받은 6종·순서와 다르다"


def test_2_session_window_matches_instruction():
    from collection.cybos.weekly_option_flow import WeeklyOptionFlow

    assert WeeklyOptionFlow.SESSION_START == "08:45"
    assert WeeklyOptionFlow.SESSION_END == "15:35"


def test_3_delta_is_measured_from_first_bar_of_day(tmp_path):
    """기준점 = 당일 첫 바 (사용자 결정).

    원천 `net_qty` 는 **일중 누적**이라 첫 바가 0 이 아니다 — 실측 2026-09-21
    08:56 에 (월)위클리 콜이 이미 +2,091 이었다(프리장 단일가). 그 몫을 빼야
    「시초 대비 증감」이 된다.
    """
    import sqlite3

    from collection.cybos.weekly_option_flow import WeeklyOptionFlow

    db = str(tmp_path / "of.db")
    f = WeeklyOptionFlow(db)
    con = f._conn()
    rows = [("2026-09-21", t, "wk_mon_call", "?", "individual", 0, 0, q, 0, "x")
            for t, q in (("08:56", 2091), ("09:30", 3000), ("14:47", 11264))]
    con.executemany(
        "INSERT INTO option_investor_flow VALUES (?,?,?,?,?,?,?,?,?,?)", rows)
    con.commit(); con.close()

    d = f.get_individual_session_delta("2026-09-21")
    p = d["products"]["wk_mon_call"]
    assert p["baseline"] == 2091 and p["baseline_time"] == "08:56"
    assert p["value"] == 11264
    assert p["delta"] == 11264 - 2091 == 9173
    assert p["series"][0] == ("08:56", 0), "첫 바는 0 이어야 한다"
    assert p["series"][-1] == ("14:47", 9173)


def test_4_unseen_product_is_absent_not_zero(tmp_path):
    """수집 전 상품은 0 이 아니라 **없어야** 한다 (계측 4원칙 ②)."""
    from collection.cybos.weekly_option_flow import WeeklyOptionFlow

    f = WeeklyOptionFlow(str(tmp_path / "of.db"))
    con = f._conn()
    con.execute("INSERT INTO option_investor_flow VALUES "
                "('2026-09-21','09:00','mon_put','F','individual',0,0,5,0,'x')")
    con.commit(); con.close()
    d = f.get_individual_session_delta("2026-09-21")
    assert set(d["products"]) == {"mon_put"}
    assert "wk_mon_call" not in d["products"], "미수집 상품이 0 으로 만들어졌다"


def test_5_out_of_window_bars_excluded(tmp_path):
    from collection.cybos.weekly_option_flow import WeeklyOptionFlow

    f = WeeklyOptionFlow(str(tmp_path / "of.db"))
    con = f._conn()
    con.executemany(
        "INSERT INTO option_investor_flow VALUES (?,?,?,?,?,?,?,?,?,?)",
        [("2026-09-21", t, "mon_call", "E", "individual", 0, 0, q, 0, "x")
         for t, q in (("08:30", 111), ("09:00", 200), ("16:10", 999))])
    con.commit(); con.close()
    d = f.get_individual_session_delta("2026-09-21")
    times = [t for t, _v in d["products"]["mon_call"]["series"]]
    assert times == ["09:00"], "08:45~15:35 밖의 바가 섞였다: %s" % times


def test_6_empty_db_returns_empty_not_zeros(tmp_path):
    from collection.cybos.weekly_option_flow import WeeklyOptionFlow

    d = WeeklyOptionFlow(str(tmp_path / "of.db")).get_individual_session_delta()
    assert d["products"] == {} and d["last_time"] is None


# ── 위젯 ──────────────────────────────────────────────────────────────────

def test_7_row_order_matches_instruction():
    from dashboard.panels.option_flow_delta_chart import _ROWS

    assert [k for k, _ in _ROWS] == [
        "wk_mon_call", "wk_mon_put", "wk_thu_call", "wk_thu_put",
        "mon_call", "mon_put"]


def test_8_default_scale_is_per_row_not_shared():
    """🔴 공통 스케일을 기본으로 두면 6행 중 4행이 0px 로 뭉개진다.

    2026-09-21 실측 행 최댓값: 월위클콜 9,656 · 월위클풋 12,135 vs
    목위클콜 198 · 목위클풋 1,041 · 먼스리콜 244 · 먼스리풋 248.
    half=17px 기준 각각 13·17·**0·1·0·0** px — 지시("시계열로 잘 파악")를 못 지킨다.
    """
    from dashboard.panels.option_flow_delta_chart import _Plot

    assert _Plot._shared is False if hasattr(_Plot, "_shared") else True
    src = _src(_CHART)
    assert "self._shared = False" in src, "기본이 공통 스케일로 되돌아갔다"
    assert "self._chk_shared.setChecked(False)" in src


def test_9_per_row_axis_is_labelled():
    """행마다 눈금이 다르므로 그 사실을 화면에 박아야 한다."""
    src = _src(_CHART)
    assert "축 ±%s" in src, "행별 축 표기가 없다 — 행 간 높이 비교 오독을 부른다"


def test_10_nonzero_never_rounds_to_invisible():
    """"값이 0" 과 "너무 작아 안 보임"은 화면에서 구분돼야 한다."""
    src = _src(_CHART)
    assert "if v and px == 0:" in src, "작은 값이 반올림으로 사라진다"


def test_11_qty_format_is_valid():
    """`"%+,d" % v` 는 ValueError 다 — 구현 중 이것 때문에 1행만 그려졌다."""
    from dashboard.panels.option_flow_delta_chart import _fmt_qty

    assert _fmt_qty(9173) == "+9,173"
    assert _fmt_qty(-1004) == "-1,004"
    assert _fmt_qty(0) == "0"


def test_12_paint_failure_is_logged_not_swallowed():
    """paint 예외를 debug 로 삼키면 화면을 눈으로 보기 전엔 모른다(계측 4원칙 ④)."""
    src = _src(_CHART)
    body = src.split("def paintEvent", 1)[1].split("def _paint", 1)[0]
    assert "logger.warning" in body, "paint 실패가 WARNING 으로 남지 않는다"
    assert "logger.debug" not in body


def test_13_chart_renders_all_six_rows_without_exception():
    """실 데이터 형태로 6행 전량이 예외 없이 그려지는지 — 오프스크린 렌더."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    try:
        from PyQt5.QtGui import QPixmap
        from PyQt5.QtWidgets import QApplication
    except Exception:                                    # pragma: no cover
        pytest.skip("PyQt5 없음")
    app = QApplication.instance() or QApplication([])

    from dashboard.panels import option_flow_delta_chart as M

    payload = {"trade_date": "2026-09-21", "last_time": "14:47", "products": {}}
    # 실측과 같은 규모차(월위클리 수천 vs 먼스리 수백)를 재현한다.
    for key, label, peak in (("wk_mon_call", "(월)위클리 콜", 9656),
                             ("wk_mon_put", "(월)위클리 풋", 12135),
                             ("wk_thu_call", "(목)위클리 콜", -198),
                             ("wk_thu_put", "(목)위클리 풋", -1041),
                             ("mon_call", "먼스리 콜", -244),
                             ("mon_put", "먼스리 풋", 248)):
        ser = [("%02d:%02d" % (9 + i // 60, i % 60), int(peak * i / 300.0))
               for i in range(300)]
        payload["products"][key] = {
            "label": label, "baseline": 0, "baseline_time": "08:56",
            "value": peak, "delta": peak, "last_time": "14:47",
            "n": len(ser), "series": ser,
        }

    errs = []
    orig = M._Plot._paint

    def spy(self):
        try:
            orig(self)
        except Exception as exc:                          # pragma: no cover
            errs.append(exc)
            raise
    M._Plot._paint = spy
    try:
        w = M.OptionFlowDeltaChart()
        w.update_flow(payload)
        w.resize(560, 290)
        w.render(QPixmap(w.size()))
        assert not errs, "paint 예외: %s" % errs[0]
        # 공통 스케일 토글도 예외 없이 동작해야 한다
        w._chk_shared.setChecked(True)
        w.render(QPixmap(w.size()))
        assert not errs, "공통 스케일 paint 예외: %s" % errs[0]
    finally:
        M._Plot._paint = orig


# ── 배선 ──────────────────────────────────────────────────────────────────

def test_14_main_pushes_delta_every_minute():
    body = _src(_MAIN).split("def _fetch_weekly_option_flow", 1)[1][:3000]
    assert "update_option_flow_delta" in body, (
        "배선이 없다 — 수집만 하고 화면에 안 오면 죽은 위젯이다"
    )
    assert "get_individual_session_delta" in body


def test_15_gui_thread_does_not_open_the_db():
    """조회는 수급 QTimer 경로가 한다 — 패널이 DB 를 열면 paint 가 막힌다."""
    # 모듈 docstring 의 원천 표기(`option_flow.db:option_investor_flow`)와 주석은
    # 설명이므로 제외하고, `import` 이후의 코드 줄만 본다.
    src = _src(_CHART)
    body = src.split("from __future__ import annotations", 1)[1]
    code_only = "\n".join(
        ln for ln in body.splitlines() if not ln.lstrip().startswith("#"))
    for bad in ("sqlite3", "option_flow.db", "_conn(", "execute("):
        assert bad not in code_only, "차트 위젯이 DB 에 직접 접근한다: %s" % bad


def test_16_futures_section_precedes_the_chart():
    """「선물 투자자 수급」이 맨 위 (사용자 지시 ②)."""
    src = _src(_DASH)
    i_fut = src.index('mk_label("선물 투자자 수급"')
    i_chart = src.index("self.option_flow_chart = OptionFlowDeltaChart()")
    i_zone = src.index('mk_label("옵션 투자자 순매수 비중')
    assert i_fut < i_chart < i_zone, "패널 섹션 순서가 지시와 다르다"
