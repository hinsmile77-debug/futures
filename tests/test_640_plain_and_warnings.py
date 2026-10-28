# -*- coding: utf-8 -*-
"""[MW0602 640차 ⑤] 원천 경고 검출(전일 고착 · 현물 부호 모순 · 7221 지연 · 옵션 결손 · 상대 미측정 · 봉 지연) · 중학생 설명 세 줄 · 패널 띠."""
import datetime as _dt
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "tools", "maekjeom_ladder"))

import shindong2_live as SL  # noqa: E402
import ladder_data as LD  # noqa: E402


def _st(**kw):
    base = dict(date="2026-10-20", live=True, last_bar="10:30", px=856.2, open=888.86, hi=889.9, lo=849.22,
                prev=dict(date="2026-10-19", high=890.24, low=870.0, close=890.24),
                foreign=dict(kospi_spot_foreign=dict(t="10:30", qty=371, amt=2000), fut_path=[dict(t="10:29", foreign=-385)]),
                flow=dict(mon_call=100.0, mon_put=50.0, wk_prod="wk_thu", wk_call=10.0, wk_put=5.0, fut_foreign=-385),
                rival=dict(present=True, signals=dict(present=True)))
    base.update(kw)
    return base


def test_1_clean_state_has_no_warnings():
    assert SL.source_warnings(_st(), now=_dt.datetime(2026, 10, 20, 10, 31)) == []


def test_2_each_defect_is_detected():
    W = SL.source_warnings(_st(prev=dict(date="2026-10-08", high=1, low=0, close=1049.0)))
    assert any("전일 참조 고착" in w and "12일 전" in w for w in W)
    W = SL.source_warnings(_st(foreign=dict(kospi_spot_foreign=dict(t="10:30", qty=371, amt=-137665), fut_path=[dict(t="10:29")])))
    assert any("부호 갈림" in w and "금액" in w for w in W)          # F3(e432cd27) — 방향은 금액 기준 문구
    W = SL.source_warnings(_st(foreign=dict(kospi_spot_foreign=None, fut_path=[dict(t="10:05")])))
    assert any("7221" in w and "25분" in w for w in W)
    W = SL.source_warnings(_st(flow=dict(mon_call=None, mon_put=None, wk_prod="wk_thu", wk_call=None, wk_put=None)))
    assert any("먼스리" in w for w in W) and any("위클리[wk_thu]" in w for w in W)
    W = SL.source_warnings(_st(rival=dict(present=False, why="shindong.db 없음")))
    assert any("상대의 수 미측정" in w for w in W)
    W = SL.source_warnings(_st(rival=dict(present=True, signals=dict(present=False, why="봉 없음"))))
    assert any("상대 신호원 미측정" in w for w in W)
    W = SL.source_warnings(_st(), now=_dt.datetime(2026, 10, 20, 10, 40))
    assert any("완결 봉 10:30" in w and "10분" in w for w in W)
    assert SL.source_warnings(dict(empty=True)) == []


def test_3_plain_lines_from_state_and_bars(tmp_path):
    cs = [("09:00", 888.86, 889.9, 887.0, 888.0), ("09:01", 888.0, 888.5, 849.22, 856.2), ("09:02", 856.2, 857.0, 855.0, 856.5)]
    st = _st()
    st["rival"] = dict(present=True, main=dict(n=3, pnl_pt=19.19, trades=[dict(entry_t="09:07", side_ko="매도")], open=None),
                       signals=dict(present=True, flowc=dict(dv=3007.0, k=300, side="매도")))
    latest = dict(ts="2026-10-20T09:19:00", dir="매도", entry=874.8, stop=881.0, target=862.0, vs_main="disagree", vs_why="현물 외인이 더 강하다",
                  comment="결론: 매도 전환\n둘째 줄")
    p = LD.plain_lines("2026-10-20", cs, True, st, latest, dict(pnl=-5.2))
    assert p["market"].startswith("09:01 현재 856.20 — 시가보다 32.66 아래") and "전날 마감(890.24)보다 낮다" in p["market"] and "385계약 팔았다" in p["market"]
    assert "MAIN(기본 규칙)은 09:07에 매도로 들어가 지금까지 3번 거래해 +19.19pt" in p["rival"] and "콜을 더 샀다" in p["rival"] and "MAIN 은 매도 쪽" in p["rival"]
    assert p["ai"].startswith("AI 는 09:19 기준으로 매도 — 진입 874.8") and "상대와 반대 — 현물 외인이 더 강하다" in p["ai"] and "결론: 매도 전환" in p["ai"] and "-5.20pt" in p["ai"]
    q = LD.plain_lines("2026-10-20", [], False, None, None, None)
    assert q == dict(market=None, rival=None, ai=None)
    r = LD.plain_lines("2026-10-20", cs, False, dict(rival=dict(present=True, main=dict(n=0, pnl_pt=0.0, trades=[], open=None))), None, None)
    assert "아직 거래하지 않았다" in r["rival"] and "포지션 없음" in r["rival"]


def test_4_ladder_ai_panel_carries_warnings_and_plain(tmp_path, monkeypatch):
    M = LD._sd2_live_mod()
    monkeypatch.setattr(M, "LIVE_DIR", str(tmp_path))
    d = tmp_path / "20261020"
    d.mkdir()
    (d / "ai_log.jsonl").write_text(json.dumps(dict(id="a", ts="2026-10-20T09:19:00", date="2026-10-20", phase="intraday", action="plan", dir="매도",
                                                   entry=874.8, stop=881.0, target=862.0, comment="결론", variant="live", lessons=[])) + "\n", encoding="utf-8")
    (d / "state.json").write_text(json.dumps(dict(generated_at="2026-10-20T10:31:00", source_warnings=["전일 참조 고착 — x"], prev=dict(close=890.24), flow={},
                                                 rival=dict(present=False))), encoding="utf-8")
    cs = [("09:00", 888.86, 889.9, 887.0, 888.0), ("09:01", 888.0, 888.5, 849.22, 856.2), ("09:02", 856.2, 857.0, 855.0, 856.5)]
    ai = LD.shindong2_ai("2026-10-20", cs, True)
    assert ai["source_warnings"] == ["전일 참조 고착 — x"] and ai["state_at"] == "2026-10-20T10:31:00"
    assert ai["plain"]["market"] and ai["plain"]["rival"] is None and ai["plain"]["ai"].startswith("AI 는 09:19")
    h = open(os.path.join(ROOT, "tools", "maekjeom_ladder", "ladder.html"), encoding="utf-8").read()
    assert 'class="srcwarn"' in h and 'class="plain"' in h and "AI.source_warnings" in h and "<abbr title=" in h and "지금 시장은" in h
