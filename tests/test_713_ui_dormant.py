# -*- coding: utf-8 -*-
"""[MW0601 713차 후속] 휴면 기동 화면 — 2026-10-25 16:55 기동 로그·스크린샷에서 고친 것.

  U1  빈 차트 안내문: 한글 폰트가 있으면 한글+fontname, 없으면 영문(두부 □□ 금지)
  U2  장외(주말·08:45 전·15:35 뒤)는 「포지션 갱신 끊김」 경고 대신 「장외」
  U3  방향 램프: 예측이 없고 미륵 휴면이면 「대기」가 아니라 「미륵 휴면」
  U4  장중 재기동 재학습 판단 블록이 휴면 게이트 안이다(「GBM 장중 재학습중」 표시가 굳지 않게)
"""
import ast
import datetime
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_U1_no_data_text(monkeypatch):
    from dashboard.panels import mid_status_row as M
    monkeypatch.setattr(M, "_ko_font", lambda: "Malgun Gothic")
    kw = M.no_data_text_kwargs()
    assert kw["fontname"] == "Malgun Gothic" and "데이터 없음" in kw["s"]
    monkeypatch.setattr(M, "_ko_font", lambda: "")
    kw = M.no_data_text_kwargs()
    assert "fontname" not in kw and all(ord(c) < 128 for c in kw["s"])
    for rel in ("dashboard/panels/direction_indicator_dialog.py", "dashboard/panels/candle_chart_dialog.py"):
        src = io.open(os.path.join(ROOT, rel), encoding="utf-8").read()
        assert '0.5, 0.5, "데이터 없음' not in src and "no_data_text_kwargs()" in src, rel


def test_U2_market_session():
    from dashboard.panels.mid_status_row import market_session_now as f
    assert not f(datetime.datetime(2026, 10, 25, 10, 0))      # 일요일
    assert not f(datetime.datetime(2026, 10, 26, 8, 30))
    assert f(datetime.datetime(2026, 10, 26, 8, 45))
    assert f(datetime.datetime(2026, 10, 26, 15, 35))
    assert not f(datetime.datetime(2026, 10, 26, 16, 56))
    src = io.open(os.path.join(ROOT, "dashboard/panels/mid_status_row.py"), encoding="utf-8").read()
    assert src.index('pos_state == "stale" and not market_session_now()') < src.index('"포지션 갱신 끊김"')


def test_U3_lamp_dormant_label():
    src = io.open(os.path.join(ROOT, "dashboard/panels/direction_indicator_dialog.py"), encoding="utf-8").read()
    i = src.index("if _mireuk_dormant():")
    assert src.index('"미륵 휴면"', i) < src.index('"대기"', i)


def test_U4_warmup_retrain_decision_gated():
    src = io.open(os.path.join(ROOT, "main.py"), encoding="utf-8").read()
    i = src.index("[WarmupRetrain] 장중 재시작 — GBM 경량 재학습 시작")
    head = src[:i]
    gate = head.rindex("        if self._mireuk_on():")
    assert "_RESTART_RETRAIN_GAP_MIN = 60" in src[gate:i]           # 판단 블록 전체가 게이트 안
    assert src[gate:i].count("\n        _RESTART_RETRAIN_GAP_MIN") == 0  # 8칸 들여쓰기(게이트 밖)로 남지 않았다
