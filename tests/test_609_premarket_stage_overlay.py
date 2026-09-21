# -*- coding: utf-8 -*-
"""[MW0601 609차] 장전 레벨 08:50 1차와 09:30 2차를 **함께** 그린다.

증상
----
당일 1분봉 차트에 08:50 구조·거리모델 값이 떠 있다가, 09:30 2차가 올라오면
**08:50 값이 사라졌다.** 그날 아침에 무엇을 보고 매매했는지가 화면에서 지워진다.

원인
----
차트의 조회가 `ORDER BY computed_at DESC LIMIT 1` 이었다 — 최신 한 행만 고른다.
🔴 **DB 에는 두 행이 처음부터 다 있었다**(실측 2026-09-21: 09-15~09-21 매일
  `0850`·`0930` 2행). 없던 데이터가 아니라 **안 읽던 데이터**다 — FP-CRITICAL
  죽은 게이트 · TOX 죽은 섀도와 같은 계열이다(계측 4원칙 ⑤).

가름 규칙 (사용자 결정 2026-09-21)
----------------------------------
**색상 = 모델 / 농도·선모양 = 스테이지.** 색은 모델 정체성이라 건드리지 않는다
(가격모델 청록 · 구조모델 회색 — 584차 「회색은 구조모델 전용」).
  · 09:30 2차 = 진한 색 · 파선(구조) / 실선(가격 점추정)
  · 08:50 1차 = 옅은 색 · 점선

실행: conda run -n py37_32 python -m pytest tests/test_609_premarket_stage_overlay.py
"""
import datetime
import json
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["MIREUK_TEST_MODE"] = "1"
# ⚠ QApplication import/생성보다 **먼저** — 순서가 바뀌면 실제 창을 띄우려다 죽는다.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtCore import QSize          # noqa: E402
from PyQt5.QtGui import QImage, QPainter  # noqa: E402
from PyQt5.QtWidgets import QApplication  # noqa: E402

_APP = None

_DASH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "dashboard", "main_dashboard.py")


def _app():
    global _APP
    if _APP is None:
        _APP = QApplication.instance() or QApplication(sys.argv)
    return _APP


def _canvas():
    _app()
    from dashboard.main_dashboard import MinuteChartCanvas
    return MinuteChartCanvas()


def _src():
    return open(_DASH, encoding="utf-8").read()


def _stage(stage, dist_lo, dist_hi, struct_up, struct_down):
    return {"stage": stage, "dist_low": dist_lo, "dist_high": dist_hi,
            "struct_up": struct_up, "struct_down": struct_down,
            "high50_lo": dist_hi - 1, "high50_hi": dist_hi + 1,
            "low50_lo": dist_lo - 1, "low50_hi": dist_lo + 1,
            "warnings": []}


# 09:30 이 08:50 의 1055.0 을 **그대로 다시** 가리킨다 — 칩 병합이 걸리는 경우.
_S0850 = _stage("0850", 1044.0, 1066.0, [[1063.0, ["갭상변"]]], [[1055.0, ["매물대"]]])
_S0930 = _stage("0930", 1046.0, 1068.0, [[1067.0, ["갭상변"]]], [[1055.0, ["매물대"]]])


def _bars(n, day="2026-09-21"):
    t0 = datetime.datetime(int(day[:4]), int(day[5:7]), int(day[8:10]), 9, 0)
    return [{"ts": (t0 + datetime.timedelta(minutes=i)).strftime("%Y-%m-%d %H:%M:%S"),
             "open": 1056.0, "high": 1057.0, "low": 1055.0, "close": 1056.5,
             "volume": 10} for i in range(n)]


def _render(stages, capture_chips=False):
    """오프스크린 렌더. 칩 텍스트를 가로챌 수 있다."""
    c = _canvas()
    c.resize(1200, 700)
    c._ov["price"] = True
    c._ov["struct"] = True
    c.reset_session(_bars(90), [])
    c.set_full_session_x(True)
    c.set_premarket_levels(stages[-1] if stages else None, stages)

    chips = []
    if capture_chips:
        _orig = c._draw_label_chip

        def _spy(painter, x, y, text, fill, stroke, upward):
            chips.append(text)
            return _orig(painter, x, y, text, fill, stroke, upward)
        c._draw_label_chip = _spy

    img = QImage(QSize(1200, 700), QImage.Format_RGB32)
    p = QPainter(img)
    c.render(p)
    p.end()
    return c, img, chips


def _ink(img):
    """배경이 아닌 픽셀 수 — 2px 간격 표본."""
    n = 0
    for y in range(0, img.height()):
        for x in range(0, img.width(), 2):
            if (img.pixel(x, y) & 0xFFFFFF) != 0x0D1117:
                n += 1
    return n


# ── A. 조회가 그날 전부를 가져온다 ────────────────────────────────────────

def test_query_no_longer_takes_only_the_latest():
    """`LIMIT 1` 로 되돌아가면 08:50 이 다시 사라진다.

    ⚠ 소스 **전체**에서 문자열을 찾으면 안 된다 — 주석이 옛 SQL 을 인용하고 있어서
      코드가 고쳐져도 단언이 걸린다(초판이 실제로 그렇게 헛돌았다). 단언은 코드와
      주석을 못 가른다. SQL 리터럴이 실린 줄만 골라서 본다.
    """
    src = _src()
    assert "def _load_premarket_stages" in src
    _sql = [ln.strip() for ln in src.splitlines()
            if "SELECT * FROM premarket_levels" in ln and ln.lstrip().startswith('"')]
    assert _sql, "장전 레벨 조회 SQL 을 못 찾았다 — 표식이 바뀌었다"
    for ln in _sql:
        assert "LIMIT" not in ln.upper(), \
            "최신 한 행만 고르면 08:50 이 09:30 에 덮인다: %s" % ln
        assert "ORDER BY computed_at ASC" in ln, "오래된 것부터 가져와야 한다: %s" % ln


def test_load_stages_returns_all_in_order(tmp_path):
    """DB 에 두 행이 있으면 **두 건 다**, 오래된 것부터."""
    from dashboard.main_dashboard import MinuteChartDialog as MD

    db = str(tmp_path / "premarket_levels.db")
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE premarket_levels (date TEXT, stage TEXT, computed_at TEXT,"
                " dist_high REAL, dist_low REAL, struct_up TEXT, struct_down TEXT,"
                " warnings TEXT)")
    con.execute("INSERT INTO premarket_levels VALUES (?,?,?,?,?,?,?,?)",
                ("2026-09-21", "0930", "09:31:00", 1068.0, 1046.0,
                 json.dumps([[1067.0, ["갭상변"]]]), json.dumps([]), "[]"))
    con.execute("INSERT INTO premarket_levels VALUES (?,?,?,?,?,?,?,?)",
                ("2026-09-21", "0850", "08:50:00", 1066.0, 1044.0,
                 json.dumps([[1063.0, ["갭상변"]]]), json.dumps([]), "[]"))
    con.commit()
    con.close()

    class _Stub(object):
        _PRE_KEYS = MD._PRE_KEYS
    _Stub._load_premarket_stages = MD._load_premarket_stages
    _Stub._load_premarket_levels = MD._load_premarket_levels

    import config.settings as _cs
    _old = _cs.DB_DIR
    try:
        _cs.DB_DIR = str(tmp_path)
        st = _Stub()._load_premarket_stages("2026-09-21")
        assert [s["stage"] for s in st] == ["0850", "0930"], "오래된 것부터여야 한다"
        # 구 계약 — 최신 1건
        assert _Stub()._load_premarket_levels("2026-09-21")["stage"] == "0930"
        # 미조회(None)와 「그날 없음」([])을 가른다 — 계측 4원칙 ②
        assert _Stub()._load_premarket_stages("1999-01-01") == []
        assert _Stub()._load_premarket_levels("1999-01-01") == {}
    finally:
        _cs.DB_DIR = _old


def test_iter_stages_falls_back_to_single():
    """단건만 주입하는 경로(테스트·구버전 호출)가 그대로 돌아야 한다."""
    c = _canvas()
    assert c._iter_pre_stages() == []              # 미조회 — 0 으로 위장하지 않는다
    c.set_premarket_levels(dict(_S0930))
    assert len(c._iter_pre_stages()) == 1
    c.set_premarket_levels(_S0930, [_S0850, _S0930])
    assert [s["stage"] for s in c._iter_pre_stages()] == ["0850", "0930"]


# ── B. 두 스테이지가 실제로 그려진다 ──────────────────────────────────────

def test_both_stages_actually_render():
    """「함께 표시」가 코드에만 있고 화면에 없으면 고친 게 아니다."""
    _, img_one, _ = _render([_S0930])
    _, img_two, _ = _render([_S0850, _S0930])
    one, two = _ink(img_one), _ink(img_two)
    assert two > one, "두 스테이지를 넣었는데 잉크가 늘지 않았다 — 안 그려진 것이다"


def test_axis_covers_both_stages():
    """축이 한쪽만 덮으면 08:50 선이 축 밖으로 밀려 캐럿으로만 남는다."""
    c = _canvas()
    c.set_premarket_levels(_S0930, [_S0850, _S0930])
    got = sorted(c._model_axis_levels())
    for v in (1044.0, 1066.0, 1063.0, 1046.0, 1068.0, 1067.0, 1055.0):
        assert v in got, "%s 가 축 계산에서 빠졌다" % v


def test_same_level_in_both_stages_gets_one_merged_chip():
    """같은 가격을 둘 다 가리키면 칩을 두 개 찍지 않는다 — 글자까지 똑같다."""
    _, _, chips = _render([_S0850, _S0930], capture_chips=True)
    _m = [t for t in chips if "1055" in t]
    assert len(_m) == 1, "1055 칩이 %d개다 — 병합되지 않았다: %r" % (len(_m), _m)
    assert "0850" in _m[0] and "0930" in _m[0], \
        "어느 스테이지가 말한 가격인지 칩에 없다: %r" % _m[0]


def test_stage_only_level_keeps_its_own_chip():
    """한쪽 스테이지에만 있는 레벨은 **그 스테이지 이름만** 달고 남아야 한다."""
    _, _, chips = _render([_S0850, _S0930], capture_chips=True)
    _a = [t for t in chips if "1063" in t]
    _b = [t for t in chips if "1067" in t]
    assert len(_a) == 1 and _a[0].startswith("0850"), "08:50 전용 레벨이 사라졌다: %r" % _a
    assert len(_b) == 1 and _b[0].startswith("0930"), "09:30 전용 레벨이 사라졌다: %r" % _b


# ── C. 그리는 순서 — 584차의 그 자리 ──────────────────────────────────────

def test_lines_oldest_first_but_chips_newest_first():
    """선은 오래된 것부터(최신이 위에), 칩은 최신부터(자리를 최신이 먼저 잡는다).

    🔴 칩을 오래된 것부터 찍으면 `_place_chip` 이 08:50 에 자리를 다 주고
      09:30 칩이 **소리 없이 사라진다**. 584차가 겪은 결함과 같은 자리다.
    """
    src = _src()
    i = src.index("def _draw_struct_model")
    blk = src[i:i + 4200]
    assert "for _i, L in enumerate(_stages):" in blk, "선은 오래된 것부터"
    assert 'key=lambda d: (not d["new"], d["lv"])' in blk, "칩은 최신을 포함한 레벨부터"


def test_stage_style_is_density_not_hue():
    """색은 **모델** 정체성이다 — 스테이지로 색을 바꾸면 회색 규칙이 깨진다.

    584차: 「회색은 구조모델 전용」. 스테이지는 농도·선모양으로만 가른다.
    """
    from dashboard.main_dashboard import MinuteChartCanvas as MC
    assert MC.PRICE_MODEL_COLOR == "#39C5CF", "가격모델 색을 바꾸면 안 된다"
    assert MC.STRUCT_MODEL_COLOR == "#C2CCD6", "구조모델 색을 바꾸면 안 된다"
    assert 0.0 < MC.PRE_STAGE_DIM < 1.0, "이전 스테이지가 최신과 같은 농도면 안 갈린다"
    assert 0.0 < MC.PRE_STAGE_BAND_DIM < 1.0
    src = _src()
    assert "Qt.DashLine if _latest else Qt.DotLine" in src, \
        "농도만으로는 색약·저대비 화면에서 안 갈린다 — 선모양도 달라야 한다"


def test_legend_states_the_stage_rule():
    """규칙을 안 적으면 옅은 선을 「흐린 구조모델」로 오독한다."""
    src = _src()
    i = src.index("_LEGEND_SPEC = (")
    blk = src[i:i + 900]
    assert "08:50" in blk and "09:30" in blk, "레전드가 스테이지 규칙을 말하지 않는다"
