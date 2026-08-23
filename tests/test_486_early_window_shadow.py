# -*- coding: utf-8 -*-
"""[MW0602 486차] 채널 [55] `early_window_gate_shadow` 불변식.

이 테스트가 지키는 것은 **판정값이 아니라 판정의 전제**다. 판정값은 표본이 늘면
바뀌어야 정상이고, 전제가 조용히 바뀌는 것이 이 프로젝트가 반복해서 데인 실패다
(292·303·371·468차 — 안전장치가 한쪽 값에 붙박여 죽어 있는데 매번 사람이 뒤늦게 발견).

고정하는 불변식 5종
-------------------
1. **코드-설정 일치** — 채널이 보는 창(09:20~09:29)과 차단 마커('조건부구간')가
   `main.py` 실제 분기와 같은가. 하나라도 어긋나면 채널이 조용히 `무기록`이 된다.
2. **사전등록 불변** — 합격선 6종이 존재하고 기존 채널에서 가져온 값 그대로인가
   (313차 ④ — 사후에 문턱을 움직이지 않는다).
3. **판정 어휘 등록** — `_fmt_verdict()` 에 BLOCK_JUSTIFIED/BLOCK_UNJUSTIFIED 가
   등록돼 있는가. 빠뜨리면 판정이 조용히 INSUFFICIENT 로 표시된다(그 함수 주석의 경고).
4. **`_safe_channel` 규약** — compute/summarize 를 노출하는가.
5. **채널 번호 예약** — [54]를 쓰지 않는가(F-9 const_out 재배정용 예약).
"""
from __future__ import annotations

import os
import re
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config.settings import VALIDATION_CAMPAIGN  # noqa: E402

CFG = VALIDATION_CAMPAIGN.get("early_window_gate_shadow")


def _read(rel):
    with open(os.path.join(_ROOT, rel), encoding="utf-8", errors="replace") as f:
        return f.read()


# ── 1. 코드-설정 일치 ────────────────────────────────────────────────────
def test_window_matches_main_branch():
    """창 경계가 main.py 분기와 같은가.

    main.py 는 `_now_hm < "0920"` / `elif _now_hm < "0930"` 으로 자른다.
    설정은 포함 경계(09:20~09:29)로 적으므로 end+1분 == 0930 이어야 한다.
    """
    src = _read("main.py")
    assert '_now_hm < "0920"' in src, "main.py 09:20 경계가 사라졌다 — 채널 창 재확인 필요"
    assert '_now_hm < "0930"' in src, "main.py 09:30 경계가 사라졌다 — 채널 창 재확인 필요"
    assert CFG["window_start_hm"] == "09:20"
    assert CFG["window_end_hm"] == "09:29"


def test_block_marker_matches_main():
    """차단 마커 문자열이 main.py 가 실제로 쓰는 값과 같은가.

    이 문자열이 바뀌면 채널은 예외 없이 조용히 0건이 된다 — 468차 G-2 가 등록한
    `무기록` 실패 형태 그대로다.
    """
    src = _read("main.py")
    marker = CFG["block_reason"]
    pat = r'checklist_reason"\]\s*=\s*"%s"' % re.escape(marker)
    assert re.search(pat, src), (
        "main.py 에 checklist_reason='%s' 대입이 없다 — 마커가 바뀌었으면 "
        "config/settings.py:early_window_gate_shadow.block_reason 도 함께 갱신할 것" % marker
    )


# ── 2. 사전등록 불변 ─────────────────────────────────────────────────────
def test_prereg_criteria_present_and_borrowed():
    """합격선이 전부 있고, 값이 기존 채널에서 가져온 그대로인가(새 숫자 금지)."""
    assert CFG is not None, "채널이 VALIDATION_CAMPAIGN 에서 사라졌다"
    # spread_extreme_watch 와 같은 값이어야 한다
    sew = VALIDATION_CAMPAIGN["spread_extreme_watch"]
    assert CFG["min_samples"] == sew["min_samples"] == 20
    assert CFG["min_days"] == sew["min_days"] == 6
    assert CFG["alpha"] == sew["alpha"] == 0.05
    assert CFG["drop_worst_days"] == sew["drop_worst_days"] == 1
    # hurst_gate_shadow / open_gap_shadow 와 같은 값이어야 한다
    assert CFG["cf_window_min"] == VALIDATION_CAMPAIGN["hurst_gate_shadow"]["cf_window_min"] == 30
    assert CFG["cf_window_min"] == VALIDATION_CAMPAIGN["open_gap_shadow"]["cf_window_min"]
    assert CFG["cost_mult"] == 2.0
    # σ 층화 경계는 창 안이어야 한다
    assert CFG["window_start_hm"] < CFG["sigma_split_hm"] <= CFG["window_end_hm"]


def test_data_start_not_before_marker_exists():
    """data_start 가 마커 최초 출현일보다 앞서면 미측정 구간이 분모에 섞인다."""
    assert CFG["data_start"] >= "2026-06-23", (
        "data_start 를 앞당기면 마커가 없던 구간이 분모에 들어간다(계측 4원칙 ②)"
    )


# ── 3. 판정 어휘 등록 ────────────────────────────────────────────────────
def test_verdict_vocabulary_registered():
    """`_fmt_verdict()` 에 두 어휘가 등록돼 있는가.

    그 함수 주석이 직접 경고한다 — *"이 표에 없는 verdict는 조용히 INSUFFICIENT로
    표시된다"*. 등록을 빠뜨리면 BLOCK_JUSTIFIED 가 표본 미달처럼 보인다.
    """
    src = _read("scripts/generate_validation_campaign_report.py")
    assert '"BLOCK_JUSTIFIED"' in src
    assert '"BLOCK_UNJUSTIFIED"' in src
    assert "PASS" not in src.split('"BLOCK_JUSTIFIED":')[1].split(",")[0], (
        "차단 정당성 채널에 PASS/FAIL 어휘를 쓰지 말 것(HurstGate FalseBlock 전례)"
    )


# ── 4. _safe_channel 규약 ────────────────────────────────────────────────
def test_safe_channel_contract():
    import importlib
    m = importlib.import_module("scripts.early_window_gate_shadow")
    assert hasattr(m, "compute") and hasattr(m, "summarize")
    out = m.summarize(m.compute("2026-07-05"))
    assert isinstance(out, dict) and "verdict" in out
    assert out["verdict"] in ("BLOCK_JUSTIFIED", "BLOCK_UNJUSTIFIED", "INSUFFICIENT")


def test_report_wires_channel():
    src = _read("scripts/generate_validation_campaign_report.py")
    assert 'scripts.early_window_gate_shadow' in src, "리포트 소비부가 빠졌다"
    assert '"early_window_gate_shadow": ewg' in src, "metrics 키가 빠졌다"


# ── 5. 채널 번호 예약 ────────────────────────────────────────────────────
def test_channel_number_does_not_collide():
    """채널 번호가 유일한가 — [55]는 이 채널, [54]는 F-9 재배정분(ConstOut).

    ↩️ **[MW0602 488차 정정] 종전 단언 `'"[54]"' not in src` 는 뒤집혔다.**
    486차가 이 테스트를 쓸 때 [54]는 F-9(=[51] 중복 해소 시 `const_out_horizon_watch`
    재배정)용 **예약**이었고, 그래서 "아직 아무도 쓰면 안 된다"로 잠갔다.
    그런데 **487차 후속(`f8faa12`)이 F-9 를 집행해 [54]를 그 용도로 배정했다** —
    예약이 **이행된 것**이지 침범당한 것이 아니다. 종전 단언을 그대로 두면
    *"F-9 를 되돌려라"* 로 읽히고, 실제로 이 테스트는 그날 이후 계속 빨간불이었다.

    그래서 묻는 것을 바꾼다 — **"[54]를 쓰지 않았는가"가 아니라 "번호가 겹치지
    않는가"** 다. 그것이 0821 리포트 1-18(=[51] 중복)이 원래 막으려던 것이다.
    """
    src = _read("scripts/generate_validation_campaign_report.py")
    assert '"[55]"' in src, "채널 번호가 [55]가 아니다"
    # [54]는 ConstOut 전용이어야 한다(F-9 이행 결과). 다른 채널이 가져가면 중복이다.
    assert '_safe_channel("scripts.const_out_horizon_watch", "[54]")' in src, (
        "[54]가 ConstOut 에 배정돼 있지 않다 — 487차 F-9(`f8faa12`) 재배정이 사라졌다")
    # 번호 유일성: 요약표 배정 라인에서 같은 번호가 두 번 나오면 안 된다.
    nums = re.findall(r'_safe_(?:eval|channel)\([^)]*?"(\[\d+\])"', src)
    dup = sorted(set(n for n in nums if nums.count(n) > 1))
    assert not dup, "채널 번호 중복 %s — 0821 리포트 1-18 과 같은 형태다" % dup


# ── 부수: 산식 재사용 확인 ───────────────────────────────────────────────
def test_geometry_is_reused_not_reimplemented():
    """청산 기하를 새로 짜지 않고 exit_replay.geometry() 를 재사용하는가.

    라이브와 다른 산식으로 시뮬하면 counterfactual 이 조용히 틀린다
    (471차 G-2 규율 — 새 숫자를 만들지 않는다).
    """
    src = _read("scripts/early_window_gate_shadow.py")
    assert "from scripts.exit_replay import geometry" in src
    # 문서 문자열의 언급은 허용하고 **실제 임포트**만 금지한다.
    code = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("#"))
    for const in ("ATR_STOP_MULT", "ATR_HORIZON_TP1_MULT", "HURST_REGIME_ATR_MULT"):
        assert not re.search(r"^\s+%s,\s*$" % const, code, re.M), (
            "%s 를 직접 임포트하면 exit_replay 와 산식이 갈린다 — geometry() 를 쓸 것"
            % const
        )


def test_posthoc_fields_are_marked():
    """사후탐색 필드에 경고가 붙어 있는가(313차 ④)."""
    import importlib
    m = importlib.import_module("scripts.early_window_gate_shadow")
    out = m.compute()
    if out.get("n_resolved"):
        assert "_posthoc_warning" in out
        assert "사후탐색" in out["_posthoc_warning"]
        # 판정 게이트가 사후탐색 필드를 쓰지 않는지 — 이름으로 확인
        for k in (out.get("gates") or {}):
            assert "atr" not in k.lower(), (
                "ATR 3분위는 사후탐색이다 — 판정 관문에 넣지 말 것(313차 ④)"
            )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
