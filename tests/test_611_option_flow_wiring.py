# -*- coding: utf-8 -*-
"""[MW0601 611차 후속] 위클리 옵션 수급 수집 배선 회귀 가드.

2026-09-21 실제 사고를 고정한다.

무슨 일이 있었나
----------------
611차가 `main.py:_fetch_weekly_option_flow()` 안에서 설정을
`getattr(settings, ...)` 로 읽었다. 그런데 main.py 의 설정 모듈 별칭은
`runtime_settings` 다(main.py:115 `import config.settings as runtime_settings`).
`settings` 라는 이름은 **존재하지 않는다.**

그 자체보다 **배치**가 더 나빴다. 호출이 이랬다:

    self.investor_data.fetch_all(include_program=True)
    self._save_program_trade_raw(now)
    self._fetch_weekly_option_flow(now)      # <- 여기서 NameError
    rt = getattr(self, "realtime_data", None)   # <- 이하 실행 안 됨
    ...
        self.investor_data._open_interest = oi  # <- 미결제약정 동기화 중단

보조 수집의 오류가 **핵심 로직(OI 동기화)을 막았다.** 재기동 후 4분간
매분 `[ERR-DEGRADED] investor_timer_fetch: name 'settings' is not defined` 가
찍히고 OI 가 갱신되지 않았다.

⚠ NameError 가 함수 안 try 블록 **밖**에 있어서, 수집기 자신의
  `[OptionFlow] 수집기 기동 실패` 경고조차 찍히지 않았다 — 실패가 엉뚱한
  곳(상위 except)에서 다른 이름으로 드러났다.

그래서 여기서 고정하는 것
-------------------------
1. main.py 가 `settings` 라는 이름으로 설정을 읽지 않는다.
2. 보조 수집 호출이 **OI 동기화 뒤**에 온다.
3. 수집기 상태 3종이 `__init__` 에서 명시 초기화된다(계측 4원칙 ④).
4. 수집기의 설정 키가 config/settings.py 에 실재한다.
"""
import io
import os
import re

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(ROOT, "main.py")
SETTINGS = os.path.join(ROOT, "config", "settings.py")


def _read(path):
    return io.open(path, encoding="utf-8").read()


def test_main_does_not_use_bare_settings_name():
    """main.py 에는 `settings` 라는 이름이 없다 — `runtime_settings` 를 쓸 것.

    ⚠ 정규식이 아니라 AST 로 검사한다. 문자열 매칭은 **주석을 잡는다** —
      실제로 main.py:10911 의 주석 `# [396차 정정] settings.ENTRY_GRADE_C_AUTO_EXP …`
      이 오탐으로 걸렸다. 코드와 주석을 구분하지 못하는 가드는 신뢰를 잃는다.
    """
    import ast

    tree = ast.parse(_read(MAIN))
    bad = []
    for node in ast.walk(tree):
        # getattr(settings, ...)
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "getattr" and node.args
                and isinstance(node.args[0], ast.Name)
                and node.args[0].id == "settings"):
            bad.append("main.py:%d getattr(settings, ...)" % node.lineno)
        # settings.FOO
        if (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
                and node.value.id == "settings"):
            bad.append("main.py:%d settings.%s" % (node.lineno, node.attr))
    assert not bad, (
        "main.py 가 정의되지 않은 이름 `settings` 로 설정을 읽는다: %s\n"
        "설정 모듈 별칭은 `runtime_settings` 다(main.py:115). "
        "611차에 이 실수로 NameError 가 나 미결제약정 동기화가 4분간 끊겼다." % bad[:3]
    )


def test_option_flow_called_after_open_interest_sync():
    """보조 수집은 핵심 로직 뒤에서 부른다.

    보조 데이터 수집이 실패해도 OI 동기화 같은 핵심 경로가 살아 있어야 한다.
    """
    src = _read(MAIN)
    i_flow = src.find("self._fetch_weekly_option_flow(now)")
    assert i_flow > 0, "_fetch_weekly_option_flow 호출이 main.py 에 없다"
    i_oi = src.find("self.investor_data._open_interest = oi")
    assert i_oi > 0, "미결제약정 동기화 코드를 찾지 못했다 — 이 테스트의 전제가 바뀌었다"
    assert i_oi < i_flow, (
        "보조 수집(_fetch_weekly_option_flow)이 미결제약정 동기화보다 **앞**에 있다. "
        "거기서 예외가 나면 그 뒤 핵심 로직이 통째로 막힌다 — 611차 사고의 형태다."
    )


def test_collector_state_explicitly_initialized():
    """계측 4원칙 ④ — 런타임 상태를 getattr 폴백으로 읽지 않는다."""
    src = _read(MAIN)
    for attr in ("_weekly_option_flow", "_wof_last_ts", "_wof_warned"):
        assert re.search(r"self\.%s\s*=" % attr, src), (
            "%s 가 __init__ 에서 명시 초기화되지 않았다" % attr
        )


def test_settings_keys_exist():
    """수집기가 읽는 설정 키가 실재한다 — 오타면 조용히 비활성이 된다."""
    src = _read(SETTINGS)
    for key in ("WEEKLY_OPTION_FLOW_ENABLED",
                "WEEKLY_OPTION_FLOW_DB",
                "WEEKLY_OPTION_FLOW_MIN_INTERVAL_SEC",
                "WEEKLY_OPTION_FLOW_START_AFTER",
                "WEEKLY_OPTION_FLOW_PEAK_SKIP"):
        assert re.search(r"^%s\s*=" % key, src, re.M), \
            "config/settings.py 에 %s 가 없다" % key


def test_start_after_is_early_enough_for_first_bar():
    """시작 시각에 여유가 있어야 이른 구간이 잘리지 않는다.

    한 번의 조회는 18행만 준다. 시작이 09:02 면 옵션(1분 간격) 기준 하한이
    08:44 로 딱 맞물려 여유가 없다 — 첫 수집이 조금만 밀려도 이른 구간이 잘린다.
    장 개시 직후 서버 피크는 시작을 미루는 대신 PEAK_SKIP 으로 건너뛴다.

    ⚠ **08:45 는 이 테스트의 관심사가 아니다.** 2026-09-22 실측상 Cybos 의 첫 행은
      08:46 이고(`t3=0846` 은 0행) 어떤 설정으로도 08:45 는 오지 않는다 —
      키움에는 있으므로 브로커 간 차이다. 그걸 미륵이 결손으로 세지 말 것.
    """
    src = _read(SETTINGS)
    m = re.search(r'^WEEKLY_OPTION_FLOW_START_AFTER\s*=\s*"(\d{2}):(\d{2})"', src, re.M)
    assert m, "WEEKLY_OPTION_FLOW_START_AFTER 를 읽지 못했다"
    minutes = int(m.group(1)) * 60 + int(m.group(2))
    # 수급 타이머 첫 호출(08:58)에 걸리도록 그보다 이르게 둔다 — 그래야 첫 수집이
    # 장 개시 전에 한 번 돌아 18행 하한에 여유가 생긴다.
    assert minutes <= 8 * 60 + 58, (
        "START_AFTER 가 %s 다 — 08:58(수급 타이머 첫 호출)보다 늦으면 "
        "첫 수집의 18행 하한이 장 개시 구간과 맞물려 여유가 사라진다." % m.group(0)
    )
    # 피크 구간은 시작 시각이 아니라 스킵으로 처리돼야 한다.
    assert re.search(r"WEEKLY_OPTION_FLOW_PEAK_SKIP", _read(MAIN)), \
        "main.py 가 PEAK_SKIP 을 읽지 않는다 — 피크 회피가 배선되지 않았다"


def test_market_codes_are_the_verified_ones():
    """2026-09-21 앵커 검증으로 확정된 시장코드가 바뀌면 이 테스트가 깨진다.

    ⚠ (월)위클리는 공식 명세 A~Z 밖의 특수문자('&', '?')다. 명세만 보고
      '잘못된 값'으로 오인해 고치는 일을 막는다.
    """
    from collection.cybos.weekly_option_flow import PRODUCTS, INVESTORS

    got = {code: key for code, key, _ in PRODUCTS}
    expect = {
        "&": "wk_mon_put", "?": "wk_mon_call",
        "R": "wk_thu_put", "Q": "wk_thu_call",
        "F": "mon_put", "E": "mon_call", "B": "kospi_spot",
    }
    assert got == expect, (
        "시장코드 매핑이 바뀌었다. 2026-09-21 키움 캡처 정답지 대조로 확정된 값이며 "
        "(월)위클리 '&'·'?' 는 명세 A~Z 밖의 특수문자다 — 명세를 근거로 되돌리지 말 것."
    )
    assert [n for _, n in INVESTORS] == ["individual", "foreign", "institution"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
