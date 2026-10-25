"""[MW0602 Sindong-V4 / 2026-10-25] 재기동 로그 정리 7건 회귀 테스트.

계기: 커밋 f5c2a21 뒤 start_Sindong.bat 재기동 로그(launcher_20261025_115242).

  E1  런처 REM 주석에 비ASCII 0줄 — 승격 콘솔(CP949)에서 CHCP 65001 뒤 바이트 정렬이 어긋나
      `'하므로' is not recognized` · `'�' is not recognized` 가 났다(구버전 재현 2건 → 0건).
  E2  폴더 선택 대기 2초(신동 작업 폴더 고정).
  E3  StrategyPanel 파라미터 히트맵 표의 스타일시트가 파싱된다(종전 `}}` 로 시트 전체 폐기).
  E4  휴장일 기동은 [BarGap] 기동 결손 줄을 내지 않는다(docstring 「거래일이 아니면 None」).
  E5  [Capital] 은 log_manager.system 한 번만 — logger.* 동시 호출 중복 금지.
  E6  shap_tracker import 가 shap 을 끌어오지 않는다(지연 import, 기동 ≈1초).
  E7  차트 「데이터 없음」 문구가 두부(Glyph missing) 없이 그려진다.
"""
import datetime
import inspect
import io
import os
import re
import subprocess
import sys
import warnings

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
_BAT = os.path.join(_ROOT, "start_Sindong.bat")


def _bat_lines():
    with io.open(_BAT, encoding="utf-8", newline="") as fh:
        return fh.read().split("\r\n")


def test_E1_no_non_ascii_rem_in_launcher():
    bad = [(i, l) for i, l in enumerate(_bat_lines(), 1)
           if l.strip().upper().startswith("REM") and re.search(r"[^\x00-\x7f]", l)]
    assert not bad, bad[:5]


def test_E2_folder_prompt_waits_two_seconds():
    lines = [l for l in _bat_lines() if l.startswith("CHOICE /C 123 ")]
    assert len(lines) == 1 and "/T 2 /D 1" in lines[0]


def test_E3_param_heatmap_stylesheet_parses():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PyQt5 import QtCore
    from PyQt5.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    msgs = []
    prev = QtCore.qInstallMessageHandler(lambda mode, ctx, msg: msgs.append(msg))
    try:
        from dashboard.strategy_dashboard_tab import _ParamHeatmap
        w = _ParamHeatmap()
        qss = w._tbl.styleSheet()
        assert qss.count("{") == qss.count("}"), qss
        w.show()
        app.processEvents()
    finally:
        QtCore.qInstallMessageHandler(prev)
    assert not [m for m in msgs if "Could not parse stylesheet" in m], msgs


def test_E4_bar_gap_silent_on_non_trading_day(tmp_path):
    from utils.bar_gap import startup_line
    db = str(tmp_path / "raw.db")
    import sqlite3
    sqlite3.connect(db).execute("CREATE TABLE raw_candles (ts TEXT)").connection.commit()
    assert startup_line(db, datetime.datetime(2026, 10, 25, 11, 52, 0)) is None   # 일요일
    assert startup_line(db, datetime.datetime(2026, 10, 26, 9, 30, 0)) is not None  # 월요일


def test_E5_capital_profile_logged_once():
    src = io.open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()
    i = src.index("    def _log_capital_profile(self) -> None:")
    body = src[i:src.index("\n    def ", i + 10)]
    assert "log_manager.system(msg)" in body
    for dup in ("logger.info(msg)", "logger.critical(full)", "logger.warning(full)", "logger.info(full)"):
        assert dup not in body, dup


def test_E6_shap_tracker_import_does_not_load_shap():
    code = ("import sys; sys.path.insert(0, %r); import learning.shap.shap_tracker as t; "
            "print('shap' in sys.modules, t._SHAP_OK)" % _ROOT)
    out = subprocess.check_output([sys.executable, "-c", code], cwd=_ROOT).decode().strip().splitlines()[-1]
    assert out == "False None", out


def test_E7_no_data_text_has_no_tofu():
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from dashboard.panels.mid_status_row import draw_no_data
    fig = Figure()
    FigureCanvasAgg(fig)
    ax = fig.add_subplot(111)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        draw_no_data(ax, "#8b949e", 11)
        fig.canvas.draw()
    assert not [x for x in w if "Glyph" in str(x.message)], [str(x.message) for x in w][:3]
