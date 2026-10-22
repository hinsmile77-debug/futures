# -*- coding: utf-8 -*-
"""[MW0602 647차 후속 / 장후 자동조치 F-1] 차단 게이트 화이트리스트 정합.

1022 장전 점검 1-2: 645차가 `PROFIT_GUARD_BLOCK_VIRTUAL_PRINCIPAL = False` 를 신설했으나
점검 도구 쪽 목록(`config/dailycheck_targets.json:documented_disabled_flags`)은 별개 파일이라
손이 안 가, 수집기 §11 이 매일 「근거 미기록」 적신호를 반복했다(경보 피로).

이 테스트는 그 지문을 고정한다 — 꺼진 `*BLOCK*` 플래그가 새로 생기면 여기서 깨져
화이트리스트 등록(+근거 문장)을 강제한다. 매매 경로와 무관한 점검 도구 정합 검사다.
"""
import io
import json
import os
import re

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CFG = os.path.join(_ROOT, "config", "dailycheck_targets.json")
_SETTINGS = os.path.join(_ROOT, "config", "settings.py")


def _cfg():
    return json.load(io.open(_CFG, encoding="utf-8"))


def _disabled_block_flags(cfg):
    # 수집기 scan_gate_flags() 와 같은 규칙 — 최상위 `NAME = True|False` 만 센다
    alert = re.compile(cfg.get("gate_flag_alert_pattern", "BLOCK"))
    text = io.open(_SETTINGS, encoding="utf-8").read()
    return sorted(
        m.group(1)
        for m in re.finditer(r"(?m)^([A-Z][A-Z0-9_]*)\s*=\s*(True|False)\b", text)
        if m.group(2) == "False" and alert.search(m.group(1)))


def test_profit_guard_virtual_flag_documented():
    cfg = _cfg()
    assert "PROFIT_GUARD_BLOCK_VIRTUAL_PRINCIPAL" in cfg["documented_disabled_flags"]
    # 목록만 늘리면 '기록됨' 표시가 근거 없이 붙는다 — 근거 문장에도 이름이 있어야 한다
    assert "PROFIT_GUARD_BLOCK_VIRTUAL_PRINCIPAL" in cfg["_documented_설명"]


def test_every_disabled_block_flag_is_documented():
    cfg = _cfg()
    documented = set(cfg["documented_disabled_flags"])
    missing = [n for n in _disabled_block_flags(cfg) if n not in documented]
    assert not missing, (
        "꺼진 차단 플래그가 화이트리스트에 없다: %s — config/dailycheck_targets.json 의 "
        "documented_disabled_flags 와 _documented_설명(근거 위치)에 함께 등록할 것" % missing)


def test_documented_flags_still_exist_in_settings():
    # 사라진 플래그가 목록에 남으면 '기록됨' 이 허공을 가리킨다
    text = io.open(_SETTINGS, encoding="utf-8").read()
    gone = [n for n in _cfg()["documented_disabled_flags"]
            if not re.search(r"(?m)^%s\s*=" % re.escape(n), text)]
    assert not gone, "settings.py 에 없는 플래그가 화이트리스트에 남아 있다: %s" % gone
