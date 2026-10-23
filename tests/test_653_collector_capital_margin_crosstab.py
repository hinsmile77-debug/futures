# -*- coding: utf-8 -*-
"""[MW0602 653차 후속 / 1023 G-1 · G-2·G-3] 수집기 — `[Capital]` 위험 기준 초과 적신호 +
증거금 상태 × 계좌 보유 구간 교차표.

무엇을 막는가
-------------
2026-10-23 장후 점검이 O-649(신동 보유가 미륵 증거금을 묶는가)를 판정하려고
`[MarginCap] state=` 31줄과 `[ShindongLive]`·`[Position]` 줄을 손으로 시각 대조했다
(BLOCK 29 · OK 2 — OK 두 번이 정확히 신동 플랫 2분). 같은 날 장전은 `[Capital]` 의
「위험 기준 초과」를 원본 TRADE 로그를 열어서야 봤다. 둘 다 관측 전용 계측이다.

이 파일이 고정하는 불변식
------------------------
① 1023 실측 로그 줄이 새 패턴에 그대로 잡힌다
② 보유 구간 끝 = `체결청산` 시각(늦게 찍히는 `종료 확인` 이 아니다) — 13:03:59 는 FLAT
③ 신동 귀속은 진입 ±60초 + 같은 방향일 때만
④ state 없는 구형식 `[MarginCap]` 줄은 교차표에 들어가지 않는다(축소 중복 계수 방지)
⑤ 위험 기준 초과가 없으면 적신호 없음 / 있으면 전환 횟수·최대 초과를 적는다
⑥ 관측 전용 — 수집기는 매매 코드(main·strategy·config.capital)를 import 하지 않는다

실행:
    python -m pytest tests/test_653_collector_capital_margin_crosstab.py
"""
import os
import re
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
_SCRIPTS = os.path.join(_ROOT, ".claude", "skills", "mireuk-daily-check", "scripts")
sys.path.insert(0, _SCRIPTS)

import collect_evidence as CE

PATS = CE.DEFAULT_CONFIG["day_summary_patterns"]


def _hit(key, line, hhmm):
    m = re.search(PATS[key], line)
    assert m, "%s 패턴이 줄을 못 잡았다: %s" % (key, line)
    d = dict(m.groupdict())
    d["hhmm"] = hhmm
    return d


def test_1_patterns_match_1023_lines():
    sd = _hit("shindong_entry", "[ShindongLive] 진입 SHORT 3계약 @826.70(규격 826.70 09:07) "
              "손절 854.15 목표 814.7 — FLOW|09:07|-1", "09:08:03")
    assert sd["dir"] == "SHORT" and sd["qty"] == "3"
    cw = _hit("capital_warn", "[Capital] 예탁금 3,400만 · 위험자본 1,500만(정책) | 가능수량 지금 3 · "
              "장시작 3 · 위험최대 2 | 신동 실주문 3(최대허용 3 · 폴백 2) ⚠ | 장시작 증거금 기준 확대 2→3 · "
              "위험 기준 초과(실주문 3 > 위험최대 2)", "08:45:33")
    assert (cw["eff"], cw["rmax"]) == ("3", "2")
    # 종료 확인 줄은 진입 패턴에 걸리면 안 된다
    assert not re.search(PATS["shindong_entry"], "[ShindongLive] FLOW|09:07|-1 종료 확인(CLOSED)")
    # 위험 기준 초과가 없는 정상 줄은 안 잡힌다
    assert not re.search(PATS["capital_warn"], "[Capital] 장시작 가능수량 3계약 고정 (08:45:33)")


def _day_1023():
    entries = [{"hhmm": "09:08:03", "dir": "SHORT", "qty": "3", "px": "826.7"},
               {"hhmm": "13:05:03", "dir": "LONG", "qty": "3", "px": "853.12"}]
    partials = [{"hhmm": "13:03:16", "pt": "-28.31", "won": "-2,833,805"},
                {"hhmm": "14:52:05", "pt": "+3.81", "won": "+189,045"}]
    finals = [{"hhmm": "13:03:16", "pt": "-28.33", "won": "-1,417,903", "dir": "SHORT"},
              {"hhmm": "14:52:05", "pt": "+3.79", "won": "+376,091", "dir": "LONG"}]
    positions, orphans = CE.group_positions(entries, partials, finals)
    assert not orphans and len(positions) == 2
    sd = [{"hhmm": "09:08:03", "dir": "SHORT"}, {"hhmm": "13:05:03", "dir": "LONG"}]
    return positions, sd


def test_2_flat_gap_between_close_and_late_confirm():
    positions, sd = _day_1023()
    mc = [{"hhmm": "10:02:58", "state": "BLOCK"},
          {"hhmm": "13:02:59", "state": "BLOCK"},
          {"hhmm": "13:03:59", "state": "OK"},    # 체결청산 13:03:16 뒤 · 종료 확인 13:04:03 앞
          {"hhmm": "13:04:59", "state": "OK"},
          {"hhmm": "13:05:59", "state": "BLOCK"},
          {"hhmm": "14:55:00", "state": "OK"}]
    xt = CE.margin_holding_crosstab(positions, mc, sd)
    assert xt["신동 보유 중"] == {"OK": 0, "CAP": 0, "BLOCK": 3, "n": 3}
    assert xt["미보유(FLAT)"] == {"OK": 3, "CAP": 0, "BLOCK": 0, "n": 3}
    assert xt["그 밖의 보유 중"]["n"] == 0
    assert xt["_unplaced"] == 0


def test_3_shindong_attach_needs_time_and_direction():
    positions, _ = _day_1023()
    mc = [{"hhmm": "10:00:00", "state": "BLOCK"}]
    # 방향이 다르면 신동이 아니다
    xt = CE.margin_holding_crosstab(positions, mc, [{"hhmm": "09:08:03", "dir": "LONG"}])
    assert xt["그 밖의 보유 중"]["BLOCK"] == 1
    # 60초 밖이면 신동이 아니다
    xt = CE.margin_holding_crosstab(positions, mc, [{"hhmm": "09:09:10", "dir": "SHORT"}])
    assert xt["그 밖의 보유 중"]["BLOCK"] == 1
    xt = CE.margin_holding_crosstab(positions, mc, [{"hhmm": "09:08:50", "dir": "SHORT"}])
    assert xt["신동 보유 중"]["BLOCK"] == 1


def test_4_old_format_and_open_position():
    positions, sd = _day_1023()
    mc = [{"hhmm": "10:00:00", "state": None},        # 구형식 축소 줄 — 세지 않는다
          {"hhmm": "bad", "state": "BLOCK"}]          # 시각 해석 실패 — 드러낸다
    xt = CE.margin_holding_crosstab(positions, mc, sd)
    assert sum(xt[b]["n"] for b in CE.MARGIN_HOLD_BUCKETS) == 0
    assert xt["_unplaced"] == 1
    # 청산 레그가 없는 포지션은 하루 끝까지 보유
    open_pos, _ = CE.group_positions([{"hhmm": "14:00:00", "dir": "LONG"}], [], [])
    xt = CE.margin_holding_crosstab(open_pos, [{"hhmm": "15:30:00", "state": "BLOCK"}], [])
    assert xt["그 밖의 보유 중"]["BLOCK"] == 1


def test_5_capital_warn_flag():
    assert CE.capital_warn_flag([]) is None
    f = CE.capital_warn_flag([{"hhmm": "08:45:33", "eff": "3", "rmax": "2"},
                              {"hhmm": "11:00:00", "eff": "4", "rmax": "2"}])
    assert "2회" in f and "08:45:33" in f and "4계약 > 위험최대 2계약" in f
    assert "차단 아님" in f


def test_6_collector_is_observation_only():
    src = open(os.path.join(_SCRIPTS, "collect_evidence.py"), encoding="utf-8").read()
    for mod in ("main", "strategy", "config.capital", "config.settings"):
        assert not re.search(r"^\s*(?:from|import)\s+%s\b" % re.escape(mod), src, re.M), mod
