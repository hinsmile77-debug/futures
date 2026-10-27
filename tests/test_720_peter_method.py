# -*- coding: utf-8 -*-
"""[MW0601 2026-10-27] 신동2AI 「피터의 방법」 — 관점 해석 · P층 · 상자 · 신선도 · 피터판단 · 격리 불변식.

근거: docs/미륵이고도화3/피터2/피터_870-850_장초판단근거_딥다이브_MW0601-20261026.md
      docs/미륵이고도화3/피터2/신동2AI_피터방법섹션_구현계획_MW0601-20261027.md
DB 없이 합성 봉으로 돈다(라이브 DB 무관).
"""
import datetime
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from strategy.peter2.view import parse_view, to_mini          # noqa: E402
from strategy.peter2.parse import parse_tweet                   # noqa: E402
from strategy.shindong2_ai import levels_p as P, box as B       # noqa: E402

BOX_TWEET = "오늘은 870 850 싸움. 두 라인 밖으로 벗어나면 가속도 붙음. 매매는 870 아래서 풋만."
# 사전등록은 PC 별 파일이다 — 이 테스트는 MW0601 원본(PM-2026-10-27-v1)으로 고정한다(이식 PC 에서도 같은 결과).
os.environ["PMETHOD_PREREG"] = os.path.join(ROOT, "docs", "미륵이고도화3", "피터2", "피터방법_사전등록_MW0601.json")


# ── 관점 해석 ─────────────────────────────────────────────────────────────
def test_view_box_and_bias_1026():
    v = parse_view(BOX_TWEET)
    assert v["kind"] == "box" and v["box"] == [850.0, 870.0]
    assert v["bias"] == "short" and v["bias_level"] == 870.0 and v["bias_rel"] == "below"


def test_view_other_kinds():
    assert parse_view("875 895 싸움")["box"] == [875.0, 895.0]
    assert parse_view("1105 밑에서 풋")["kind"] == "bias"
    assert parse_view("만약 오늘 종가가 875 이하에서 끝난다면 추가 하방")["kind"] == "cond_close"
    assert parse_view("만약 1050 밑으로 빠지면 기회 함 더 줄거 같으니 대기")["kind"] == "wait"
    assert parse_view("오늘 맥점은 1035. 여기 위에서 버티면")["kind"] == "pivot"
    assert parse_view("오늘은 870 850 싸움이라고 했는데 하루종일 이 안에서 놀았습니다")["kind"] == "recap"
    # 가격이 아닌 숫자 · 남의 「매도만」은 관점이 아니다(10-27 오분류 정정)
    assert parse_view("책 800페이지 넘어버림")["kind"] == "none"
    assert parse_view("풋 1495배 터짐")["kind"] == "none"
    assert parse_view("오늘은 금욜 이상의 기계매도만 안 들어오면 됨")["bias"] is None


def test_view_to_mini_unmeasured_offset():
    v = parse_view(BOX_TWEET)
    assert to_mini(v, None) is None                       # 미측정 — 0 으로 메우지 않는다
    assert to_mini(v, -0.2)["box"] == [849.8, 869.8]


# ── PETER 실거래 격리 ─────────────────────────────────────────────────────
def test_box_tweet_is_not_a_trade():
    """관점 트윗이 주문 해석기에서 매매 사실로 읽히면 실주문이 나간다 — 그대로 facts=[] 여야 한다."""
    r = parse_tweet(BOX_TWEET)
    assert not r.get("ignore") and r["facts"] == []


def test_follower_records_view_without_intent():
    from strategy.peter2.follower import Peter2Follower
    from strategy.peter2.store import event_md
    f = Peter2Follower("2026-10-26", -0.1)
    eng = dict(status="FLAT", source=None, pending=False, price=860.0)
    tw = dict(id="1", dt="2026-10-26T00:09:09.000Z", text=BOX_TWEET)
    intents = f.ingest(tw, eng, datetime.datetime(2026, 10, 26, 9, 10))
    assert intents == []
    ev = [e for e in f.events if e["kind"] in ("VIEW", "NOFACT")]
    assert len(ev) == 1 and ev[0]["kind"] == "VIEW" and ev[0]["box"] == [850.0, 870.0]
    assert "상자 850.00–870.00" in event_md(ev[0])


def test_follower_nofact_not_silent():
    from strategy.peter2.follower import Peter2Follower
    f = Peter2Follower("2026-10-26", -0.1)
    eng = dict(status="FLAT", source=None, pending=False, price=860.0)
    f.ingest(dict(id="2", dt="2026-10-25T23:40:57.000Z", text="장중에 중요 맥점이 보이면 알려드리겠습니다"),
             eng, datetime.datetime(2026, 10, 26, 8, 41))
    assert [e["kind"] for e in f.events] == ["NOFACT"]   # 10-26 08:40 처럼 흔적 없이 사라지지 않는다


def test_shindong_main_does_not_import_peter_method():
    """신동 MAIN 규격 입력(premarket_levels)과 엔진은 P층을 모른다(사전등록 격리)."""
    pat = re.compile(r"levels_p|shindong2_ai\.box|peter2\.view|shindong2_pmethod")
    sd = os.path.join(ROOT, "strategy", "shindong")
    for fn in os.listdir(sd):
        if fn.endswith(".py"):
            with open(os.path.join(sd, fn), encoding="utf-8") as fh:
                assert not pat.search(fh.read()), fn
    with open(os.path.join(ROOT, "features", "levels", "premarket_levels.py"), encoding="utf-8") as fh:
        assert not pat.search(fh.read())
    with open(os.path.join(ROOT, "strategy", "peter2", "parse.py"), encoding="utf-8") as fh:
        assert "view" not in fh.read().split("def parse_tweet")[0].split("import re")[1][:50]


# ── 사전등록 ──────────────────────────────────────────────────────────────
def test_prereg_frozen_fields():
    cfg = P.prereg()
    assert cfg["id"] == "PM-2026-10-27-v1" and cfg["registered_before_backfill"] is True
    assert cfg["box"]["T"] == ["09:10", "09:30"]
    h = cfg["hypotheses"]
    assert h["H-P1"]["pass"] == {"min_n": 30, "min_edge_pp": 10.0, "max_p": 0.05}
    assert h["H-B1"]["pass"] == {"min_n": 40, "min_edge_pp": 10.0, "max_p": 0.05}
    assert h["H-B2"]["pass"] == {"min_n": 15, "max_p": 0.05}


# ── P층 ───────────────────────────────────────────────────────────────────
def _day(lo, hi, n=20, start="09:00"):
    h0 = int(start[:2]) * 60 + int(start[3:])
    out = []
    for i in range(n):
        t = h0 + i
        px = lo + (hi - lo) * (i % 5) / 4.0
        out.append(["%02d:%02d" % (t // 60, t % 60), px, min(px + 0.5, hi), max(px - 0.5, lo), px])
    out[0][3] = lo
    out[-1][2] = hi
    return out


def test_rebound_cluster_1026_like():
    """10-15 저 848.00 · 10-20 저 850.60 · 10-22 저 852.05 → 반발 3회 군집(≈850)."""
    ext = [("10-15", "L", 848.0), ("10-20", "L", 850.6), ("10-22", "L", 852.05), ("10-21", "L", 875.2),
           ("10-23", "L", 824.65)]
    c = P.cluster_extremes(ext, 2.5, 2)
    assert len(c) == 1 and c[0]["hits"] == 3 and abs(c[0]["price"] - 850.0) <= 0.5


def test_cluster_same_day_counts_once():
    assert P.cluster_extremes([("d1", "H", 900.0), ("d1", "L", 899.0)], 2.5, 2) == []


def test_merge_walls_tags():
    lv = P.merge_walls([dict(price=849.0, kind="반발", label="반발3회")], [dict(price=850.0, label="먼스리풋벽850")], 1.5)
    assert lv[0]["merged"] == ["먼스리풋벽850"] and lv[1]["kind"] == "벽"


# ── 상자 ──────────────────────────────────────────────────────────────────
def test_box_b2_snaps_to_anchor_and_b0_centered():
    cfg = P.prereg()
    bars = [["08:45", 856.0, 862.98, 856.0, 859.14], ["09:00", 855.7, 858.3, 854.46, 854.78],
            ["09:08", 860.86, 868.06, 860.52, 866.88], ["09:09", 866.86, 867.8, 864.52, 865.14],
            ["09:10", 865.1, 866.2, 862.9, 863.6]]
    bx = B.make_boxes(bars, "09:10", [849.0, 850.0, 866.5, 870.0], cfg)
    assert bx["or_lo"] == 854.46 and bx["or_hi"] == 868.06       # 09:10 봉은 OR 에 안 들어간다(미래 참조 금지)
    assert bx["B1"] == [850, 870] and bx["B2"] == [850.0, 870.0]
    w = bx["B2"][1] - bx["B2"][0]
    assert abs((bx["B0"][1] - bx["B0"][0]) - w) < 1e-6 and abs(sum(bx["B0"]) / 2 - 865.14) < 1e-6


def test_box_score_held_and_break():
    cfg = P.prereg()
    bars = [["09:10", 860, 861, 859, 860], ["09:11", 860, 869, 852, 860]]
    assert B.score_box(bars, [850, 870], "09:10", cfg)["held"] is True
    bars.append(["09:12", 860, 873, 860, 872])                   # 종가 872 ≥ 870+1 → 상단 이탈
    bars.append(["09:13", 872, 876, 871, 875])
    s = B.score_box(bars, [850, 870], "09:10", cfg)
    assert s["held"] is False and s["break_side"] == "up" and s["break_t"] == "09:12" and s["ext"] == 4.0


def test_level_reaction_support_revert():
    cfg = P.prereg()
    bars = [["09:00", 860, 860, 858, 858], ["09:01", 858, 858, 850.5, 851], ["09:02", 851, 857, 851, 856]]
    r = B.level_reaction(bars, 850.0, cfg)
    assert r["side"] == "지지" and r["ok"] is True


# ── 신선도 · 피터판단 ─────────────────────────────────────────────────────
def test_freshness_flags_missed_spike(monkeypatch):
    """10-26 09:09 재현: snapshot 완결 봉 09:03(고 863.50) → 기록 시점 09:08 고 868.06."""
    import shindong2_pmethod as PM
    sys.path.insert(0, os.path.join(ROOT, "tools", "maekjeom_ladder"))
    import ladder_data as L
    bars = [["09:0%d" % i, 860, 863.5 if i < 4 else (868.06 if i == 8 else 864), 855, 860] for i in range(10)]
    monkeypatch.setattr(L, "is_live", lambda day, now=None: True)
    monkeypatch.setattr(L, "candles", lambda day, live: (bars, "test"))
    fr = PM.freshness("2026-10-26", dict(last_bar="09:03", hi=863.5, lo=854.46))
    assert fr["rec_bar"] == "09:08" and fr["lag_bars"] == 5 and fr["new_hi"] == 868.06 and fr["stale"] is True
    assert "868.06" in PM.freshness_line(fr)
    fr2 = PM.freshness("2026-10-26", dict(last_bar="09:08", hi=868.06, lo=854.46))
    assert fr2["stale"] is False and PM.freshness_line(fr2) is None


def test_freshness_unmeasured_on_error(monkeypatch):
    import shindong2_pmethod as PM
    sys.path.insert(0, os.path.join(ROOT, "tools", "maekjeom_ladder"))
    import ladder_data as L

    def boom(day, live):
        raise IOError("db")
    monkeypatch.setattr(L, "is_live", lambda day, now=None: True)
    monkeypatch.setattr(L, "candles", boom)
    fr = PM.freshness("2026-10-26", dict(last_bar="09:03", hi=1, lo=0))
    assert fr["rec_bar"] is None and "실패" in fr["why"]        # 미측정 — stale=False 로 위장하지 않는다
    assert PM.freshness_line(fr).startswith("⚪")


def test_vs_peter_line():
    import shindong2_pmethod as PM
    assert PM.parse_vs_peter_line("본문\n피터판단: 반대 | 외인 선물 매수") == ("disagree", "외인 선물 매수")
    assert PM.parse_vs_peter_line("상대판단: 동의 | x") == (None, None)


def test_render_block_marks_shadow_status():
    import shindong2_pmethod as PM
    pl = dict(status=PM.STATUS, px=860.0, walls_n=2, pin=None, views_source=True, views=[],
              levels=[dict(price=850.0, kind="반발", label="반발3회", merged=["먼스리풋벽850"])],
              boxes={"09:10": dict(B1=[850, 870], B2=[850.0, 870.0], B0=[855, 875], or_lo=854.46, or_hi=868.06,
                                    pos=0.5, break_side=None, break_t=None)})
    txt = "\n".join(PM.render(pl))
    assert "섀도" in txt and "B2 850–870" in txt and "합류 먼스리풋벽850" in txt


# ── I9 기계 속도(KS-2026-10-27-v1) ───────────────────────────────────────
def test_i9_speed_and_unmeasured():
    from strategy.shindong2_ai.indicators import i9_machine_speed as K9
    s = {"10:50": dict(na=100000), "11:00": dict(na=119350), "11:10": dict(na=89870)}
    assert K9.speed(s, "11:00") == 193.5                 # (119350 − 100000) / 100
    assert K9.speed(s, "11:10") == -294.8
    assert K9.speed(s, "09:05") is None                  # 첫 바 09:02 + 10분 전 — 미측정
    assert K9.value_at(s, "11:20") is None               # 행이 10분 묵었다 — 0 이 아니라 None
    assert K9.speed({"11:00": dict(na=None)}, "11:10") is None


def test_i9_prereg_frozen():
    with open(os.path.join(ROOT, "docs", "미륵이고도화3", "피터2", "기계속도_사전등록_MW0601.json"), encoding="utf-8") as fh:
        cfg = json.load(fh)
    assert cfg["id"] == "KS-2026-10-27-v1" and cfg["status"].startswith("확정")
    h = cfg["hypotheses"]
    assert h["H-K2"]["X_eok"] == 500 and h["H-K2"]["Y_eok"] == 150
    assert "2026-10-27" in h["H-K1"]["exclude_days"] and h["H-K1"]["primary_at"] == "10:00"
