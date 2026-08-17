# -*- coding: utf-8 -*-
"""[MW0601 474차 / D9-B] 진입 라우팅 밴드 채널 — 판정 규율 회귀 테스트.

무엇을 지키는가
---------------
이 채널의 위험은 계산 오류가 아니라 **사후적합**이다. 채널을 만든 계기 자체가
"여러 경계 후보 중 눈에 띄는 하나"(4.4-6.0, 승률 38.1%)였고, 그걸 그대로 결론으로
쓰면 313차 원칙 ④ 위반이다. 실제로 첫 실행에서 **일자단위 부호검정 p=1.0000**
(감시밴드 우세 8일 / 열위 9일)이 나와 신호단위 인상이 소멸했다 — 372차가 겪은
"신호단위 유의 → 일자단위 소멸"의 재현이다.

그래서 다음을 못박는다.

1. **합격선은 settings에서만 온다** — 코드에 리터럴이 박히면 조용히 바뀐다.
2. **밴드 경계도 settings에서만 온다** — 데이터를 본 뒤 경계를 옮기면 사전등록 무효.
3. **`focus_band` 불일치는 큰 소리로 실패한다** — 조용히 표본 0이 되면
   "안 쌓였다"와 "이름이 안 맞는다"가 같은 출력으로 보인다(계측 4원칙 ②의 문자열판).
4. **py3.7 포매팅** — `"%,.0f" % v`는 런타임에서 ValueError다. 이런 줄은 표본이
   문턱을 넘은 뒤에야 실행되므로 몇 달 뒤에 처음 터진다(473차 `math.comb` 동형).

실행:
    pytest tests/test_474_entry_band_watch.py
"""
import inspect
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

os.environ["MIREUK_TEST_MODE"] = "1"

from scripts import entry_band_watch as EBW  # noqa: E402

_KEYS = ("band_edges", "focus_band", "min_samples", "min_days", "pnl_gap_krw",
         "win_rate_gap_pp", "alpha", "drop_worst_days", "entry_source", "data_start")


# ── 1. 사전등록 ─────────────────────────────────────────────────────────────

def test_channel_is_preregistered():
    from config.settings import VALIDATION_CAMPAIGN
    cfg = VALIDATION_CAMPAIGN.get("entry_band_watch")
    assert cfg, "entry_band_watch 채널이 사전등록돼 있지 않다"
    missing = [k for k in _KEYS if k not in cfg]
    assert not missing, "사전등록 키 누락: %s" % missing


def test_band_edges_contain_the_live_router_boundaries():
    """감시 경계가 실제 라우터 경계를 포함해야 같은 것을 잰다."""
    from config.settings import (VALIDATION_CAMPAIGN, ENTRY_HORIZON_LOW_BLOCK,
                                 ENTRY_HORIZON_B1, ENTRY_HORIZON_B2)
    edges = [float(x) for x in VALIDATION_CAMPAIGN["entry_band_watch"]["band_edges"]]
    for name, v in (("LOW_BLOCK", ENTRY_HORIZON_LOW_BLOCK),
                    ("B1", ENTRY_HORIZON_B1), ("B2", ENTRY_HORIZON_B2)):
        assert any(abs(e - float(v)) < 1e-9 for e in edges), (
            "라우터 경계 %s=%s 가 band_edges %s에 없다 — 채널이 라우터와 다른 컷을 잰다"
            % (name, v, edges))


def test_no_hardcoded_thresholds():
    src = inspect.getsource(EBW.compute)
    for key in ("band_edges", "focus_band", "min_samples", "min_days",
                "pnl_gap_krw", "win_rate_gap_pp", "alpha", "drop_worst_days"):
        assert 'cfg.get("%s"' % key in src, "%s 를 settings에서 읽지 않는다" % key


# ── 2. focus_band 해석 — 조용한 실패 금지 ───────────────────────────────────

def test_focus_band_normalizes_float_notation():
    """`4.4-6.0`(설정 표기)과 `4.4-6`(`%g` 표기)이 같은 밴드로 해석돼야 한다.

    이 정규화가 없으면 감시밴드 표본이 **0**으로 잡히고 INSUFFICIENT가 뜬다 —
    실제로 첫 구현에서 그렇게 됐다.
    """
    edges = [0.8, 3.2, 4.4, 6.0]
    assert EBW.resolve_focus("4.4-6.0", edges) == "4.4-6"
    assert EBW.resolve_focus("4.4-6", edges) == "4.4-6"
    assert EBW.resolve_focus(">=6.0", edges) == ">=6"


def test_unresolvable_focus_band_fails_loudly():
    """맞지 않는 focus_band는 표본 미달이 아니라 **판정 불가**로 나와야 한다."""
    edges = [0.8, 3.2, 4.4, 6.0]
    assert EBW.resolve_focus("9.9-99", edges) is None
    assert EBW.resolve_focus("헛소리", edges) is None


def test_band_names_are_ordered_and_cover_all():
    names = EBW.all_band_names([0.8, 3.2, 4.4, 6.0])
    assert names == ["<0.8", "0.8-3.2", "3.2-4.4", "4.4-6", ">=6"], names
    for tf, want in ((0.1, "<0.8"), (1.0, "0.8-3.2"), (4.0, "3.2-4.4"),
                     (5.0, "4.4-6"), (99.0, ">=6")):
        assert EBW.band_of(tf, [0.8, 3.2, 4.4, 6.0])[0] == want, tf


# ── 3. py3.7 포매팅 (지연 폭발 방지) ────────────────────────────────────────

def test_krw_formatter_works_on_py37():
    """`%,.0f`는 py3.7 ValueError — 헬퍼가 대신한다."""
    assert EBW._krw(1234567) == "1,234,567"
    assert EBW._krw(-90251, sign=True) == "-90,251"
    assert EBW._krw(None) == "N/A"
    with pytest.raises(ValueError):
        _ = "%,.0f" % 1234.0     # 이 문법이 왜 금지인지 못박는다


def test_no_percent_comma_format_in_source():
    """소스에 `%`-콤마 포매팅이 남아 있지 않은가(docstring 설명문은 제외)."""
    import re
    src = inspect.getsource(EBW)
    body = "\n".join(l for l in src.splitlines()
                     if "py3.7에서 ValueError" not in l and "이 문법이 왜" not in l)
    bad = [l.strip() for l in body.splitlines()
           if re.search(r'"[^"]*%[-+]?,\.?\d*f', l)]
    assert not bad, "py3.7에서 터지는 %%-콤마 포매팅이 남아 있다: %s" % bad[:3]


# ── 4. 통계 ─────────────────────────────────────────────────────────────────

def test_sign_test_matches_known_values():
    p, pos, neg = EBW._sign_test_p([1] * 6)
    assert pos == 6 and neg == 0 and abs(p - 0.03125) < 1e-9
    p2, _, _ = EBW._sign_test_p([1, -1, 1, -1])
    assert p2 == 1.0
    assert EBW._sign_test_p([0, 0])[0] is None


# ── 5. 실 DB 판정 ───────────────────────────────────────────────────────────

def test_real_run_produces_a_verdict():
    res = EBW.compute()
    if not res.get("available"):
        pytest.skip("DB 미가용: %s" % res.get("reason"))
    assert res["verdict"] in ("BAND_ANOMALY", "BAND_UNIFORM", "INSUFFICIENT")
    assert res.get("reason")
    assert res.get("bands"), "밴드 집계가 비어 있다"


def test_focus_band_actually_has_samples():
    """감시밴드 표본이 0이면 이름 불일치를 의심해야 한다 — 첫 구현의 실패 모드."""
    res = EBW.compute()
    if not res.get("available"):
        pytest.skip("DB 미가용")
    names = [b["band"] for b in res["bands"]]
    assert res["focus_band"] in names, (
        "감시밴드 %s 가 집계 밴드 %s에 없다" % (res["focus_band"], names))


def test_low_power_is_flagged_not_hidden():
    """`BAND_UNIFORM`이 '이상 없음이 입증됐다'로 읽히지 않도록 주석이 붙는가."""
    res = EBW.compute()
    if not res.get("available") or res["verdict"] != "BAND_UNIFORM":
        pytest.skip("현재 BAND_UNIFORM이 아님")
    from config.settings import VALIDATION_CAMPAIGN
    need = int(VALIDATION_CAMPAIGN["entry_band_watch"]["min_samples"])
    if res.get("n_focus", 0) >= 2 * need:
        pytest.skip("표본이 충분해 저검정력 주석 대상이 아님")
    assert res.get("low_power") is True
    assert "검정력" in (res.get("power_note") or "")


def test_verdict_requires_all_preregistered_conditions():
    """BAND_ANOMALY는 손익·승률·유의성·이상치내성을 **모두** 만족해야 한다.

    하나만 커도 발화하면 사후적합 통로가 열린다. 실제 첫 실행이 그 반례다 —
    승률 격차 24.7%p(문턱 15 초과)인데 부호검정 p=1.0000이라 UNIFORM이 나왔다.
    """
    src = inspect.getsource(EBW.compute)
    assert "if worse and big and wr_big and sig and holds:" in src, (
        "판정 조건이 AND 결합이 아니다 — 사후적합 위험")
