# -*- coding: utf-8 -*-
"""[MW0601 683차] 신동2 확률 시나리오 학습 사이클 + 외인 동향 보고 규약.

고정하는 것
-----------
A. 명세 — 합 100 · 5% 단위 · 2개 이상 · 키 중복 금지 · 되돌림 「이후」는 목표에서 무효 반대쪽.
B. 결말 — 추세형(목표 선착 = 실현) · 무효 선착 · 같은 봉 무효 우선 · 되돌림형(목표 뒤 이후) · 미결/진행.
C. 채점 — brier · 균등 기준 · BSS · 기본 시나리오 적중. 장중(잠정)에 결말 안 난 세트는 점수를 매기지 않는다.
D. 보정 — 표본 5 미만은 말하지 않는다 · 과신/과소 15%p.
E. 배선 — record 가 시나리오를 저장 · CLI 는 장전·장중·익일 live 기록에 --scenarios 필수 ·
   evaluate_day 가 시나리오를 채점 · trend 가 BSS ≤ 0 이면 딥다이브.
F. 스킬 — 사이클(예측결과·반성·레슨·학습·다음 예측) · 외인 동향 규약 · 시나리오 규약 문구.

실행: conda run -n py37_32 python -m pytest tests/test_683_shindong2_scenario_cycle.py -v
"""
import datetime as dt
import io
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))
import shindong2_live as M  # noqa: E402
import shindong2_learn as LN  # noqa: E402
import shindong2_scenario as SC  # noqa: E402

SPEC = "A|반등 후 저항|45|105|108|101 ; B|하락 재개|35|95|103 ; C|랠리|20|108|99"


def _bars(prices, start="09:00"):
    h, m = map(int, start.split(":"))
    out = []
    for i, (o, hi, lo, c) in enumerate(prices):
        t = h * 60 + m + i
        out.append(["%02d:%02d" % (t // 60, t % 60), o, hi, lo, c])
    return out


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    monkeypatch.setattr(M, "LIVE_DIR", str(tmp_path / "live"))
    monkeypatch.setattr(M, "DOC_DIR", str(tmp_path / "doc"))
    monkeypatch.setattr(LN, "LEARN_DIR", str(tmp_path / "learn"))
    return tmp_path


# ── A ──
def test_parse_spec_valid_and_rejects():
    it = SC.parse_spec(SPEC)
    assert [i["key"] for i in it] == ["A", "B", "C"] and [i["kind"] for i in it] == ["되돌림", "하락", "상승"]
    for bad in ("A|x|50|1|2 ; B|y|45|3|1",          # 합 95
                "A|x|52|1|2 ; B|y|48|3|1",          # 5% 단위 아님
                "A|x|100|1|2",                       # 1개
                "A|x|50|1|2 ; A|y|50|3|1",          # 키 중복
                "A|x|50|105|108|110 ; B|y|50|95|103",  # 이후가 무효 쪽
                "A|x|50|1|1 ; B|y|50|3|1"):         # 목표 = 무효
        with pytest.raises(SystemExit):
            SC.parse_spec(bad)


# ── B ──
def test_resolve_trend_reversal_and_priority():
    it = {i["key"]: i for i in SC.parse_spec(SPEC)}
    pre = [(100, 100.5, 99.5, 100)]
    # 반등 105 도달 → 101 재하락: A 실현 · B 무효(103 선착) · C 미결(108 안 감)
    cs = _bars(pre + [(100, 103, 100, 102.5), (102.5, 105.2, 102, 104.8), (104.8, 105, 100.8, 101)])
    r = {k: SC.resolve(v, cs, "09:01") for k, v in it.items()}
    assert r["A"]["status"] == "실현" and r["A"]["t"] == "09:03" and r["A"]["t_target"] == "09:02"
    assert r["B"]["status"] == "무효" and r["B"]["t"] == "09:01"
    assert r["C"]["status"] == "미결"
    # 같은 봉에 목표·무효 → 무효 우선
    cs2 = _bars(pre + [(100, 108.5, 94, 100)])
    assert SC.resolve(it["C"], cs2, "09:01")["status"] == "무효"
    # 되돌림형 목표만 도달하고 끝 → 진행
    cs3 = _bars(pre + [(100, 105.5, 100, 105)])
    assert SC.resolve(it["A"], cs3, "09:01")["status"] == "진행"
    # 15:10 이후 봉은 보지 않는다
    cs4 = _bars([(100, 100, 100, 100), (100, 120, 100, 120)], start="15:09")
    assert SC.resolve(it["C"], cs4, "15:09")["status"] == "미결"


# ── C ──
def test_score_set_and_live_provisional():
    it = SC.parse_spec(SPEC)
    s = SC.score_set(it, {"A": 1, "B": 0, "C": 0})
    assert s["brier"] == round(((0.45 - 1) ** 2 + 0.35 ** 2 + 0.2 ** 2) / 3, 4)
    assert s["base"] == round(((1 / 3 - 1) ** 2 + 2 * (1 / 3) ** 2) / 3, 4)
    assert s["bss"] > 0 and s["top"] == "A" and s["top_hit"] is True and s["realized"] == ["A"]
    rec = dict(id="x", ts="2026-10-13T09:00:30", phase="intraday", scenarios=dict(items=it))
    cs = _bars([(100, 100.5, 99.5, 100), (100, 103, 100, 102.5)])
    live = SC.evaluate_sets([rec], cs, lambda r: "09:01", final=False)
    assert live[0].get("brier") is None                     # 결말 안 난 시나리오가 있으면 잠정
    fin = SC.evaluate_sets([rec], cs, lambda r: "09:01", final=True)
    assert fin[0]["brier"] is not None and fin[0]["top_hit"] is False   # B 무효 · A/C 미결 → 실현 없음


# ── D ──
def test_calibration_advice():
    pairs = [(70, 0)] * 4 + [(70, 1)]
    cal = SC.calibration(pairs)
    assert cal[0]["bin"] == "65–100%" and cal[0]["rate"] == 20.0
    assert SC.calibration_advice(cal)[0].startswith("과신")
    assert SC.calibration_advice(SC.calibration(pairs[:4])) == []      # n<5 — 말하지 않는다
    assert SC.calibration_advice(SC.calibration([(20, 1)] * 5))[0].startswith("과소")


# ── E ──
def test_record_cli_requires_scenarios_and_stores(sandbox, monkeypatch):
    with pytest.raises(SystemExit) as e:
        M.main(["record", "--date", "2026-10-13", "--phase", "intraday", "--action", "note", "--comment", "유지"])
    assert "--scenarios" in str(e.value)
    M.main(["record", "--date", "2026-10-13", "--phase", "position", "--action", "note", "--comment", "보유"])  # 보유는 면제
    now = dt.datetime(2026, 10, 12, 16, 0, 0)
    rec = M.record("2026-10-13", "overnight", "plan", "매도", 100.0, 103.0, 95.0, "본문", now=now, scenarios=SPEC)
    assert [i["prob"] for i in rec["scenarios"]["items"]] == [45, 35, 20]
    doc = io.open(M._doc_path("2026-10-13"), encoding="utf-8").read()
    assert "채점용 시나리오" in doc and "A 반등 후 저항 45%" in doc
    with pytest.raises(SystemExit):
        M.record("2026-10-13", "intraday", "note", "관망", None, None, None, "x", now=now, scenarios="A|x|60|1|2 ; B|y|30|3|1")


def test_evaluate_day_scores_scenarios_and_trend_flags(sandbox):
    it = SC.parse_spec(SPEC)
    cs = _bars([(100, 100.5, 99.5, 100), (100, 103, 100, 102.5), (102.5, 105.2, 102, 104.8), (104.8, 105, 100.8, 101)])
    log = [dict(id="o", ts="2026-10-12T16:00:00", phase="overnight", action="stand", dir="관망", variant="live",
                scenarios=dict(spec=SPEC, items=it))]
    out = LN.evaluate_day("2026-10-13", bars=cs, log=log, st=dict(prev=dict(close=99.0), sd2=dict(summary={})))
    assert out["scen_summary"]["n"] == 1 and out["scen_summary"]["on_brier"] is not None
    assert "시나리오 예측 채점" in LN.render_eval(out)
    # 3일 연속 BSS<0 이면 딥다이브
    bad = dict(n=1, brier=0.5, bss=-0.4, top_hit=0.0, on_brier=0.5, on_bss=-0.4, on_top_hit=False, pairs=[[80, 0], [20, 1]])
    rows = [dict(date="2026-10-%02d" % d, actual="매도", range=10.0, rules_p=0, fb_hits=[], fb_misses=[], on_live=None, on_legacy=None, pm_live=None, pm_legacy=None, ai_pnl=0, ai_n=0,
                 rules_base=0, lessons=[], feedback=False, scen=bad) for d in (7, 8, 9)]
    win = LN.trend_windows(rows)
    v = LN.trend_verdict(rows, win)
    assert any("BSS" in m and "🔴" in m for m in v["messages"])
    assert "시나리오 확률 판단" in LN.render_trend(rows, win, v)


def test_foreign_flags_and_render():
    fp = dict(t_cut=None, prev=[dict(date="2026-10-08", foreign=-5148), dict(date="2026-10-07", foreign=-2455)],
              fut_path=[dict(t="09:02", foreign=-207, inst=369, retail=-242, oi=32992),
                        dict(t="15:34", foreign=1482, inst=-1452, retail=19, oi=42730)],
              fut_extreme=dict(min_t="10:02", min=-1452, max_t="15:32", max=1515),
              mon_put_foreign=dict(t="15:42", qty=297, amt=-7563))
    L = "\n".join(M._render_foreign(fp))
    assert "| 15:34 | +1482 | -1452 | +19 | 42730 |" in L and "10-07 -2455 · 10-08 -5148" in L


# ── F ──
def test_skill_documents_cycle_and_rules():
    s = io.open(os.path.join(_ROOT, ".claude", "skills", "shindong2", "SKILL.md"), encoding="utf-8").read()
    for w in ("외인 동향 · 시나리오 보고 규약", "--scenarios", "예측결과", "반성", "보정", "BSS", "확률 합", "장 초반 확인 체크리스트"):
        assert w in s, w


def test_scenarios_from_comment_line(sandbox, monkeypatch):
    """명령행 대신 본문 「시나리오명세:」 한 줄 — 예약작업 권한 패턴에 | ; 를 넣지 않는 경로."""
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(("결론 관망\n시나리오명세: " + SPEC + "\n").encode("utf-8"))))
    M.main(["record", "--date", "2026-10-13", "--phase", "intraday", "--action", "note", "--comment-file", "-"])
    rec = M.load_ai_log("2026-10-13")[-1]
    assert [i["key"] for i in rec["scenarios"]["items"]] == ["A", "B", "C"]
