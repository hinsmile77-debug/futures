# -*- coding: utf-8 -*-
"""[MW0602 673차 후속] 신동 일일 리포트 헤더 — 재생(2계약 가정) vs 실거래(X%위험 1계약) 차를 리포트가 직접 나눈다.

2026-10-29 사례: 리포트 「한눈에」 MAIN **+132.8만** vs 실현손익 **+50.3만**(브로커 net 502,820).
차 −82.5만의 80% 는 수량(ATR14 49.78 > 35 → X%위험 1계약)이고 나머지는 체결·비용이다. 리포트가
차를 한 덩어리로만 적어 「손익이 안 맞는다」로 읽혔고, 메일 요약(「오늘의 한 줄」만 읽음)에는 실거래가 없었다.

고정하는 것
A. 수량 + 체결·비용 + 신호 구성 = 실거래 − 재생 (정확히)
B. 실거래 줄에 수량 분포·재생 가정 수량·분해가 찍힌다
C. 「오늘의 한 줄」(메일 요약 원천)이 실거래로 시작하고 수량 환산 재생값을 함께 보인다
D. 수량이 재생 가정과 같으면 「수량」 몫·환산 문구를 붙이지 않는다(노이즈 금지)
"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import pytest  # noqa: E402

from strategy.shindong import daily_report as DR, spec as S  # noqa: E402

# 2026-10-29 MW0602 — 실거래(1계약) net · 재생 MAIN(2계약) net
_REAL = [243183, -36796, 187208, 109224]
_REPLAY = [449000, -23000, 512000, 390000]


def _rc(real_qty=1, extra=()):
    items = []
    for i, (a, b) in enumerate(zip(_REAL, _REPLAY)):
        items.append(dict(kind="MATCH", key="K%d" % i,
                          real=dict(qty=real_qty, net=a * real_qty, entry_ts="2026-10-29 10:0%d:00" % i,
                                    side=-1, entry_px=940.0),
                          replay=dict(net=b, entry_ts="10:0%d" % i, side=-1, entry_px=940.0)))
    items.extend(extra)
    real = [it["real"] for it in items if it["real"] is not None]
    rep = [it["replay"] for it in items if it["replay"] is not None]
    return dict(items=items, n_real=len(real), real_total=sum(p["net"] for p in real),
                replay_total=sum(r["net"] for r in rep), broker={"net": 502820, "source": "live"}, other={})


def test_a_split_sums_exactly():
    rc = _rc(extra=[dict(kind="REPLAY_ONLY", key="R", real=None, note="늦게 알아챔",
                         replay=dict(net=100000, entry_ts="11:00", side=1, entry_px=941.0))])
    sp = DR._recon_split(rc)
    assert sp["size"] + sp["exec"] + sp["signal"] == pytest.approx(rc["real_total"] - rc["replay_total"])
    assert sp["size"] == pytest.approx(-664000)          # 재생 132.8만의 절반
    assert sp["exec"] == pytest.approx(502819 - 664000)  # 체결·비용 −16.1만
    assert sp["signal"] == pytest.approx(-100000)
    assert sp["scaled"] == pytest.approx(664000 + 100000)
    assert not sp["same_qty"]


def test_b_headline_shows_qty_and_split():
    rc = _rc()
    h = DR._recon_headline(rc, rc["replay_total"])
    assert "1계약×4" in h and "재생은 %d계약 가정" % S.LEGS in h
    assert "차 -82.5만 = 수량 -66.4만 + 체결·비용 -16.1만" in h
    assert "신호 구성" not in h                           # 짝 없는 거래가 없으면 붙이지 않는다


def test_c_oneliner_leads_with_real_and_reaches_mail():
    from strategy.shindong.report_mail import _summary
    rc = _rc()
    line = "**오늘의 한 줄** — %sMAIN %s(4거래 3승%s)." % (
        DR._recon_oneliner(rc), DR._man(rc["replay_total"]), DR._recon_scaled_note(rc))
    assert line.startswith("**오늘의 한 줄** — 실거래 +50.3만(1계약×4) · 재생 MAIN +132.8만")
    assert "실거래 수량 환산 +66.4만" in line
    s = _summary("## 0. 한눈에\n\n" + line + "\n\n## 1. 차트\n")
    assert "실거래 +50.3만" in s


def test_d_same_qty_no_size_noise():
    rc = _rc(real_qty=S.LEGS)
    h = DR._recon_headline(rc, rc["replay_total"])
    assert "수량 " not in h.split("차 ")[-1] and "체결·비용" in h
    assert DR._recon_scaled_note(rc) == ""
    assert DR._recon_oneliner(None) == "" and DR._recon_scaled_note(None) == ""


# ── [673차 후속3] A·B — 진입 슬립 실측 · 진입봉 종가 표기 ──────────────────────────
from strategy.shindong import exec_recon as XR  # noqa: E402


def _rc_slip():
    # 10/29 R60 매도 3건: 규칙가 944.32/944.52/936.20 · 실체결 945.44/943.32/934.48
    items = []
    for i, (rule, real) in enumerate(((944.32, 945.44), (944.52, 943.32), (936.20, 934.48))):
        items.append(dict(kind="MATCH", key="K%d" % i,
                          real=dict(qty=1, net=0.0, entry_px=real, side=-1, entry_ts="2026-10-29 10:0%d:00" % i),
                          replay=dict(net=0.0, entry_px=rule, side=-1, entry_ts="10:0%d" % i)))
    items.append(dict(kind="REPLAY_ONLY", key="R", real=None,
                      replay=dict(net=0.0, entry_px=900.0, side=1, entry_ts="11:00")))
    return dict(items=items)


def test_e_entry_slip_sign_and_scope():
    sl = XR.entry_slips(_rc_slip())
    assert [round(x["slip_pt"], 2) for x in sl] == [-1.12, 1.20, 1.72]   # + = 불리(매도를 싸게 팜)
    assert XR.entry_slips(None) is None and XR.entry_slips({"items": []}) == []
    st = XR.slip_stats([x["slip_pt"] for x in sl])
    assert st["n"] == 3 and st["worst"] == pytest.approx(1.72) and st["t"] is not None
    assert XR.slip_stats([]) is None                                     # 미측정 ≠ 0


def test_f_entry_slip_line_in_recon_section():
    line = DR._entry_slip_line(_rc_slip(), {"n": 20, "days": 6, "mean": 0.057, "sd": 0.71, "t": 0.36})
    assert "오늘 3건 평균 +0.60pt · 최악 +1.72pt" in line and "합 +9.0만" in line
    assert "누적(2026-10-13~) 20건/6일 평균 +0.057pt · 표준편차 0.71 · t=+0.36" in line
    assert DR._entry_slip_line(_rc_slip(), None).endswith("누적 미측정")
    assert DR._entry_slip_line(None) is None


def test_g_dead_detect_lag_metric_removed():
    src = open(DR.__file__, encoding="utf-8").read()
    assert '"**탐지 지연**' not in src            # 구조적 +0 지표를 다시 그리지 않는다


def test_h_entry_label_is_bar_close():
    assert DR._entry_label("10:16", 936.2, "10:17") == "10:16봉 종가 936.20 (확정 10:17)"
    assert DR._entry_label("10:16", 936.2, "10:19") == "10:16봉 종가 936.20 (확정 10:17 · 탐지 10:19)"
    assert DR._entry_label("10:59", 1.0) == "10:59봉 종가 1.00 (확정 11:00)"


def test_i_collect_recons_walks_days(monkeypatch):
    import types
    fake = types.ModuleType("strategy.runtime.trade_principal")      # 실제 모듈은 PyQt5 를 끌어온다
    fake.read_jsonl = lambda day, name: [{"kind": "ENTER", "trade_key": "K", "side": -1,
                                          "entered_at": day + " 10:17:03"}]
    fake.read_json = lambda day, name, default=None: default
    pkg = types.ModuleType("strategy.runtime")
    pkg.trade_principal = fake
    monkeypatch.setitem(sys.modules, "strategy.runtime", pkg)
    monkeypatch.setitem(sys.modules, "strategy.runtime.trade_principal", fake)
    rows = {"2026-10-28": [dict(key="K", side=-1, entry_ts="10:16", entry_px=936.2, net=0.0, legs=[])],
            "2026-10-29": [dict(key="K", side=-1, entry_ts="10:16", entry_px=936.2, net=0.0, legs=[])]}
    monkeypatch.setattr(XR, "stored_main_rows", lambda sd, day, sv=None: rows.get(day, []))
    monkeypatch.setattr(XR, "real_positions", lambda db, day: None if day == "2026-10-28" else [
        dict(entry_ts=day + " 10:17:03", side=-1, qty=1, entry_px=934.48, net=0.0, legs=[])])
    recons, um = XR.collect_recons("sd", "tr", "2026-10-27", "2026-10-29")
    assert um == ["2026-10-28"] and [d for d, _ in recons] == ["2026-10-29"]
    assert round(XR.entry_slips(recons[0][1])[0]["slip_pt"], 2) == 1.72
