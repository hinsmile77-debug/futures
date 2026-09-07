# -*- coding: utf-8 -*-
"""[MW0601 539차] `ATR_MIN_ENTRY` 26주 WFA 재검증 등재의 **동기화 불변식**.

무엇을 발견했나 (2026-09-07)
----------------------------
`config/settings.py:ATR_MIN_ENTRY = 1.0`(pt)은 **절대 포인트 고정 임계**인데
ATR은 지수 수준에 비례한다. 아무도 값을 바꾸지 않았는데 실효 강도가 월별로
**0.3% ~ 61.6%** 를 오갔다(변동폭 61.2%p). 상한(`ATR_MAX_ENTRY`)은 273차에
적응형으로 바뀌었으나 하한은 2026-05-08 도입 이래 정적인 채 남아 있었다.

이 파일이 하는 일
-----------------
**임계값이 옳은지 판정하지 않는다.** 그건 26주 주기에
`scripts/atr_min_entry_recalibration.py`가 한다. 여기서는 세 가지가 **함께**
움직이도록 묶는다 — 하나만 바뀌면 테스트가 깨져 나머지 갱신을 강제한다.

    config/settings.py:ATR_MIN_ENTRY
        ↕
    CLAUDE.md 「주기적 재검증 항목」의 539차 항목
        ↕
    scripts/atr_min_entry_recalibration.py (판정 도구 + 사전등록 밴드)

CB②·CB③-P4·FP-CRITICAL이 "재검토하기로 했는데 안 함" 상태가 됐던 것과 같은
경로를 막는 장치다. 테스트가 깨지면 "고쳐야 할 버그"가 아니라 **"세 곳을 함께
갱신하라"** 는 신호다.

실행:
    pytest tests/test_539_atr_min_entry_wfa_registration.py
"""
import os
import re
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

os.environ["MIREUK_TEST_MODE"] = "1"

import pytest  # noqa: E402

from config.settings import ATR_MIN_ENTRY, ATR_MAX_ENTRY  # noqa: E402

#: 2026-09-07 539차 등재 시점의 운영값. 바뀌면 CLAUDE.md 항목과
#: `scripts/atr_min_entry_recalibration.py`의 밴드를 **함께** 갱신할 것.
_DECLARED_ATR_MIN_ENTRY = 1.0

_CLAUDE_MD = os.path.join(_ROOT, "CLAUDE.md")
_SCRIPT = os.path.join(_ROOT, "scripts", "atr_min_entry_recalibration.py")


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def test_declared_value_matches_settings():
    """운영값이 바뀌면 여기서 먼저 걸린다 — 문서·스크립트 동반 갱신 신호."""
    assert ATR_MIN_ENTRY == _DECLARED_ATR_MIN_ENTRY, (
        "ATR_MIN_ENTRY가 %s → %s 로 바뀌었다. CLAUDE.md 26주 목록의 539차 항목과 "
        "scripts/atr_min_entry_recalibration.py 의 BLOCK_RATE_BAND 를 함께 갱신하고 "
        "이 상수를 새 값으로 고칠 것. 재보정이라면 strategy_events 에 "
        "METRIC_REDEFINITION 마커도 남길 것(461차 mdd_pct 교훈)."
        % (_DECLARED_ATR_MIN_ENTRY, ATR_MIN_ENTRY))


def test_lower_bound_is_below_upper_bound():
    """하한 < 정적 상한. 뒤집히면 진입이 구조적으로 전면 차단된다."""
    assert 0 < ATR_MIN_ENTRY < ATR_MAX_ENTRY


def test_recalibration_script_exists_and_is_readonly_by_contract():
    """26주 항목은 반드시 재검증 도구를 갖는다 — 없으면 목록이 죽은 문장이 된다."""
    assert os.path.isfile(_SCRIPT), "재검증 스크립트가 없다: %s" % _SCRIPT
    src = _read(_SCRIPT)

    # 장중 DB 전수 스캔 금지 (456차 CB⑤)
    assert "guard_intraday" in src, "장중 실행 가드(guard_intraday)가 빠졌다"
    # BLAS 즉사 방지 (537차) — numpy 계열 import 보다 먼저 불려야 한다
    assert "ensure_conda_dll_path" in src, "DLL 부트스트랩 호출이 빠졌다(537차)"
    # 사전등록 밴드가 코드에 고정돼 있어야 한다 (SOP §11 / 458차 D6)
    assert re.search(r"^BLOCK_RATE_BAND\s*=", src, re.M), "사전등록 밴드 상수가 없다"
    assert re.search(r"^MAX_MONTHLY_SPREAD\s*=", src, re.M), "변동폭 기준 상수가 없다"
    # 읽기 전용 계약 — 설정 파일을 쓰지 않는다
    assert "settings.py" not in src.split('"""', 2)[-1] or "자동 변경하지 않는다" in src


def test_claude_md_registers_the_item():
    """CLAUDE.md 「주기적 재검증 항목」에 실제로 등재돼 있는가."""
    md = _read(_CLAUDE_MD)
    head = "## 주기적 재검증 항목"
    assert head in md, "26주 재검증 절 자체가 사라졌다"
    section = md.split(head, 1)[1]
    # 다음 대제목 전까지가 이 절이다
    section = re.split(r"\n---\n\n## ", section, 1)[0]

    assert "ATR_MIN_ENTRY" in section, (
        "CLAUDE.md 26주 재검증 목록에서 ATR_MIN_ENTRY 항목이 사라졌다. "
        "폐기하려면 이 테스트도 함께 지우고 DECISION_LOG에 사유를 남길 것.")
    assert "atr_min_entry_recalibration.py" in section, (
        "항목이 재검증 스크립트를 가리키지 않는다 — 도구 없는 목록은 지켜지지 않는다")


def test_claude_md_item_quotes_current_value():
    """문서가 인용한 값과 코드의 값이 어긋나면 안 된다 (461차·483차 계열 사고 방지)."""
    md = _read(_CLAUDE_MD)
    idx = md.find("ATR 진입 하한 `ATR_MIN_ENTRY")
    assert idx > 0, "539차 항목 제목을 찾지 못했다"
    head_line = md[idx:idx + 200]
    m = re.search(r"ATR_MIN_ENTRY\s*=\s*([\d.]+)", head_line)
    assert m, "항목 제목에 값이 명시돼 있지 않다"
    assert float(m.group(1)) == ATR_MIN_ENTRY, (
        "CLAUDE.md 항목이 %s 라고 적었는데 코드는 %s 다 — 문서가 코드를 못 따라갔다"
        % (m.group(1), ATR_MIN_ENTRY))


def test_script_imports_the_live_constant_not_a_copy():
    """스크립트가 값을 복사해 두면 상수 변경이 반영되지 않는다."""
    src = _read(_SCRIPT)
    assert re.search(r"from config\.settings import \([^)]*ATR_MIN_ENTRY", src, re.S), (
        "스크립트가 config.settings 에서 ATR_MIN_ENTRY 를 직접 import 해야 한다")
    assert not re.search(r"^ATR_MIN_ENTRY\s*=", src, re.M), (
        "스크립트가 ATR_MIN_ENTRY 를 자체 정의하고 있다 — 사본은 드리프트한다")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
