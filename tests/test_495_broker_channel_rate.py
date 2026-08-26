# -*- coding: utf-8 -*-
"""[MW0602 495차 후속] 브로커 로그인 채널별 수수료율 — 감지·매핑·파생 검증.

배경: 대신증권은 로그인 매체별로 수수료를 고시한다 — CREON 트레이딩 0.0019% /
CYBOS(사이버) 0.0098104%. 493차 체리픽이 CYBOS 값을 하드코딩해 들여오자 이 PC
(CREON)에서 5.16배 과대가 됐다(495차). 재발 방지: 값은 상수가 아니라
`config/constants.py:BROKER_CHANNEL_SPECS[감지된 채널]`에서 파생된다.

실행: pytest tests/test_495_broker_channel_rate.py
      python tests/test_495_broker_channel_rate.py   (단독 실행도 가능)

🔴 [MW0601 494차 후속 체리픽 / 2026-08-26] **원본은 `t1_`~`t6_` 이름이라 pytest 가
   수집하지 못했다** — 전체 스위트에서 한 번도 돌지 않는 「죽은 테스트」가 된다.
   이 저장소가 반복해서 당한 실패(FP-CRITICAL 죽은 게이트 2개월, TOX 죽은 섀도
   1개월)와 같은 형태라 `test_` 로 바꿔 수집되게 했다. 단독 실행 경로는 유지한다.

⚠ **이 브랜치(v9-dev = MW0601)는 CYBOS 채널이다.** dev(MW0602)는 CREON 이고,
   두 브랜치의 폴백 채널이 서로 다르다(각자 자기 PC 채널로 떨어져야 5.16배
   오차를 피한다). 그래서 아래 테스트는 **특정 채널을 단정하지 않고** 「감지된
   채널과 파생값이 일치하는가」만 본다 — 양쪽 브랜치에서 그대로 통과한다.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FAILURES = []


def check(name, fn):
    try:
        fn()
        print("PASS %s" % name)
    except AssertionError as e:
        FAILURES.append(name)
        print("FAIL %s: %s" % (name, e))


def test_spec_table_pins_both_official_rates():
    """채널→요율 매핑이 양 채널 고시값을 정확히 담는다 (2026-08-26 사용자 확인)."""
    from config.constants import BROKER_CHANNEL_SPECS as SPECS
    assert set(SPECS) == {"CREON", "CYBOS"}, "채널 집합이 바뀌었다: %s" % sorted(SPECS)
    assert abs(SPECS["CREON"]["one_way_commission_rate"] - 0.000019) < 1e-12, \
        "CREON 고시 0.0019%%가 아니다"
    assert abs(SPECS["CYBOS"]["one_way_commission_rate"] - 0.000098104) < 1e-12, \
        "CYBOS 고시 0.0098104%%가 아니다"
    for ch, spec in SPECS.items():
        assert spec["fee_source"], "%s 출처 표기가 없다 — 다음 브로커 전환 때 또 못 갱신한다" % ch
        assert len(spec["effective_from"]) == 10, "%s 전환일 형식 이상" % ch


def test_settings_rate_derives_from_detected_channel():
    """settings 요율·전환일·출처가 감지 채널의 스펙에서 파생된다 — 하드코딩 회귀 방지."""
    from config import settings as S
    from config.constants import BROKER_CHANNEL_SPECS as SPECS
    assert S.BROKER_CHANNEL in SPECS, "감지 채널이 스펙에 없다: %r" % S.BROKER_CHANNEL
    spec = SPECS[S.BROKER_CHANNEL]
    assert S.FUTURES_COMMISSION_RATE == spec["one_way_commission_rate"]
    assert S.FUTURES_COMMISSION_RATE_EFFECTIVE_FROM == spec["effective_from"]
    assert S.BROKER_FEE_SOURCE == spec["fee_source"]


def test_detection_source_is_visible():
    """계측 4원칙 ④ — 감지 근거(source)가 항상 드러난다. 폴백도 이름으로 남는다."""
    from config import settings as S
    assert S.BROKER_CHANNEL_SOURCE, "감지 근거가 비어 있다"
    assert (S.BROKER_CHANNEL_SOURCE in ("env", "fallback")
            or S.BROKER_CHANNEL_SOURCE.startswith("starter_log:")), \
        "알 수 없는 감지 근거: %r" % S.BROKER_CHANNEL_SOURCE


def test_env_override_roundtrip():
    """환경변수 강제가 동작하고, 지우면 원복된다 (기계 독립적 검증)."""
    from config.constants import detect_broker_channel
    old = os.environ.pop("MIREUK_BROKER_CHANNEL", None)
    try:
        os.environ["MIREUK_BROKER_CHANNEL"] = "CYBOS"
        ch, src = detect_broker_channel()
        assert (ch, src) == ("CYBOS", "env"), "env 강제 무시됨: %r" % ((ch, src),)
        os.environ["MIREUK_BROKER_CHANNEL"] = "잘못된값"
        ch2, src2 = detect_broker_channel()
        assert src2 != "env", "무효한 env 값이 채널로 채택됐다"
    finally:
        os.environ.pop("MIREUK_BROKER_CHANNEL", None)
        if old is not None:
            os.environ["MIREUK_BROKER_CHANNEL"] = old


def test_downstream_consumers_follow_settings():
    """비용 소비처가 settings 단일 원천을 따른다 — 채널이 바뀌면 함께 바뀐다."""
    from config import settings as S
    import backtest.transaction_cost as T
    assert T.BROKERAGE_RATE_DEFAULT == S.FUTURES_COMMISSION_RATE
    from utils.db_utils import normalize_trade_pnl
    m = normalize_trade_pnl(entry_price=1040.0, quantity=1, pnl_pts=0.0,
                            pt_value=50000)
    assert abs(m["commission_rate_used"] - S.FUTURES_COMMISSION_RATE) < 1e-12


def test_legacy_generation_survives():
    """세대 판별용 LEGACY 상수는 채널과 무관하게 보존된다."""
    from config import settings as S
    assert abs(S.FUTURES_COMMISSION_RATE_LEGACY_KIWOOM - 0.000015) < 1e-12
    assert S.FUTURES_COMMISSION_RATE != S.FUTURES_COMMISSION_RATE_LEGACY_KIWOOM


def main():
    check("T1 채널별 고시 요율 매핑", test_spec_table_pins_both_official_rates)
    check("T2 settings 파생", test_settings_rate_derives_from_detected_channel)
    check("T3 감지 근거 가시화", test_detection_source_is_visible)
    check("T4 env 강제 왕복", test_env_override_roundtrip)
    check("T5 소비처 단일 원천", test_downstream_consumers_follow_settings)
    check("T6 LEGACY 세대 보존", test_legacy_generation_survives)
    if FAILURES:
        print("FAILED: %s" % ", ".join(FAILURES))
        sys.exit(1)
    print("ALL PASS (6/6)")


if __name__ == "__main__":
    main()


# ── [MW0601 v9-dev 고유] 이 브랜치가 CYBOS 로 떨어지는가 ────────────────────
def test_v9dev_fallback_is_cybos_not_creon():
    """🔴 이 브랜치의 폴백은 **CYBOS** 여야 한다 — dev(CREON)와 의도적으로 다르다.

    폴백을 틀리면 요율이 5.16배 어긋난다. 이 PC(MW0601)는 CYBOS 로그인이므로
    감지 실패 시에도 CYBOS 로 떨어져야 한다. dev 브랜치를 그대로 체리픽하면
    CREON 폴백이 따라와 **1/5.16** 이 되므로 여기서 고정한다.
    """
    import io
    import os
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src = io.open(os.path.join(root, "config", "settings.py"), encoding="utf-8").read()
    i = src.index("BROKER_CHANNEL, BROKER_CHANNEL_SOURCE = detect_broker_channel()")
    block = src[i: i + 1600]
    assert 'BROKER_CHANNEL = "CYBOS"' in block, (
        "v9-dev 폴백이 CYBOS 가 아니다 — dev(CREON) 값이 따라 들어왔는가?")
    assert "CYBOS 폴백 적용" in block, "폴백이 쓰였을 때 stderr 경고가 없다(계측 4원칙 ④)"


def test_dual_starter_hazard_is_documented():
    """이 PC에 **두 스타터가 다 설치돼 있다**는 사실이 코드에 남아 있는가.

    감지는 mtime 최신을 쓰므로 **누군가 CREON 을 열면 그날부터 채널이 뒤집힌다.**
    실측(2026-08-26): CREON 2026-07-09 / Daishin(CYBOS) 2026-08-26.
    이 위험이 주석에 없으면 다음 사람이 "감지되니 안전하다"고 읽는다.
    """
    import io
    import os
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src = io.open(os.path.join(root, "config", "settings.py"), encoding="utf-8").read()
    assert "MIREUK_BROKER_CHANNEL=CYBOS" in src, "환경변수 고정 권고가 없다"
    assert "둘 다 설치" in src, "이중 설치 위험 기록이 없다"


def test_rate_is_not_hardcoded_anymore():
    """요율이 리터럴로 되돌아가지 않았는가 — 495차 재발 방지의 본체."""
    import ast
    import io
    import os
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tree = ast.parse(io.open(os.path.join(root, "config", "settings.py"),
                             encoding="utf-8").read())
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        names = [t.id for t in node.targets if isinstance(t, ast.Name)]
        if "FUTURES_COMMISSION_RATE" not in names:
            continue
        assert not isinstance(node.value, (ast.Num, ast.Constant)), (
            "FUTURES_COMMISSION_RATE 가 다시 리터럴로 박혔다(%s행) — "
            "채널 스펙에서 파생해야 한다" % node.lineno)
