# -*- coding: utf-8 -*-
"""[MW0602 486차 F-1 / 488차 계획 B] 수집기 휴장일 판정 + 거래일 문맥 불변식.

무엇을 막는가
-------------
0823(일요일)에 `--phase post` 를 돌리자 §11 자동 적신호에 **7건**이 올라왔고
**전부 "오늘이 휴장일"이라는 한 가지 사실의 파생**이었다(실제 결함 0건). 그중 하나는
*"15:10 청산 경로가 아무 흔적도 남기지 않았다 — 절대원칙 1 확인 필요"* 였다.
사람이 매번 알아채야 하고, 익숙해지면 **진짜 경고가 섞여도 넘기게 된다.**

반대편 사고도 있다 — 484차가 `logs/20260817_SYSTEM.log`(공휴일 기동)를 근거로 08-17을
거래일로 세어 "8거래일"이라 썼다. 둘 다 *"파일의 존재/부재를 곧바로 원인으로 읽었다"* 는
같은 형태이고, 그 교훈은 문서에만 있고 도구에는 없었다.

이 파일이 고정하는 불변식
------------------------
① 주말 · 공휴일 · 거래일 3케이스 판정
② 판정식이 `scripts/campaign_steps.py` 와 **같다**(새 판정식을 만들지 않았다)
③ 강등 목록이 **6종으로 고정**돼 있고, 휴장일에도 유효한 사실은 강등되지 않는다
④ 직전 거래일 역탐색이 연휴를 건너뛴다

실행:
    python tests/test_486_collector_holiday.py
"""
import os
import sys
from datetime import date

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, ".claude", "skills", "mireuk-daily-check", "scripts"))

import collect_evidence as CE


def test_weekend_is_not_trading_day():
    """① 주말 — 공휴일표 없이도 걸러진다(폴백이 성립하는 근거)."""
    ok, why = CE.is_trading_day(_ROOT, date(2026, 8, 23))     # 일요일
    assert ok is False and "주말" in why, (ok, why)
    ok2, why2 = CE.is_trading_day(_ROOT, date(2026, 8, 22))   # 토요일
    assert ok2 is False and "주말" in why2, (ok2, why2)


def test_krx_holiday_is_not_trading_day():
    """② 공휴일 — 2026-08-17(광복절 대체공휴일).

    484차가 이 날을 거래일로 세어 "8거래일"이라 썼다. 그날 `logs/20260817_SYSTEM.log`
    가 존재하는데(휴장일에도 프로세스는 뜬다) 파일 존재를 거래일로 읽었기 때문이다.
    """
    ok, why = CE.is_trading_day(_ROOT, date(2026, 8, 17))
    assert ok is False and "공휴일" in why, (ok, why)


def test_normal_weekday_is_trading_day():
    """③ 평일 — 08-21(금)은 거래일이다. 과잉 억제 방향의 오판을 잡는다."""
    ok, why = CE.is_trading_day(_ROOT, date(2026, 8, 21))
    assert ok is True and why == "거래일", (ok, why)


def test_same_formula_as_campaign_steps():
    """④ 새 판정식을 만들지 않았다 — `campaign_steps.py` 와 결과가 일치한다.

    판정식이 둘이 되면 어느 쪽이 옳은지 다투게 된다. repo 에 이미 있는 헬퍼를 쓴다는
    것이 486차 F-1 의 설계 전제였고, 그 전제를 여기서 실제로 대조한다.
    """
    from config.krx_holidays import is_krx_holiday
    for d in (date(2026, 8, 17), date(2026, 8, 21), date(2026, 8, 23),
              date(2026, 9, 25), date(2026, 12, 25), date(2026, 8, 24)):
        expect = not (d.weekday() >= 5 or is_krx_holiday(d))   # campaign_steps.py:40-41
        got, why = CE.is_trading_day(_ROOT, d)
        assert got == expect, "%s: 수집기=%s(%s) vs campaign_steps=%s" % (d, got, why, expect)


def test_prev_trading_day_skips_holidays():
    """⑤ 직전 거래일 역탐색 — 주말·연휴를 건너뛴다."""
    # 08-23(일) 직전 거래일은 08-21(금) — 08-22(토)를 건너뛴다
    assert CE.prev_trading_day(_ROOT, date(2026, 8, 23)) == date(2026, 8, 21)
    # 08-18(화) 직전은 08-14(금) — 08-15(토)·16(일)·17(대체공휴일) 3일을 건너뛴다
    assert CE.prev_trading_day(_ROOT, date(2026, 8, 18)) == date(2026, 8, 14)


def test_suppression_list_size_is_locked():
    """⑥ 🔴 강등 목록 6종 고정 — **과잉 억제가 이 fix 의 최대 위험**이다.

    휴장 플래그가 잘못 서거나 목록이 늘면, 진짜 결함이 있는 거래일에 적신호가 통째로
    사라진다. 목록을 늘리려면 이 테스트를 함께 고쳐야 하고 그때 재검토가 강제된다.
    """
    assert len(CE.HOLIDAY_SUPPRESS) == 6, CE.HOLIDAY_SUPPRESS


def test_suppression_never_hides_facts_valid_on_holidays():
    """⑦ 휴장일에도 유효한 사실은 강등하지 않는다.

    미커밋 변경 · PC명 태그 위반 · 설정 불변식 `불일치` — 이 셋은 거래 여부와 무관하다.
    "휴장이니 조용히" 하고 덮으면 F-1 이 만든 것은 안전장치가 아니라 눈가리개다.
    """
    keep, sup = CE.split_holiday_flags([
        "미커밋 변경 12건",
        "PC명 태그 누락 커밋 3건 — 멀티PC 컨벤션 위반",
        "설정 불변식 `FP_CRITICAL_GRADE_BLOCK_ENABLED` = `True` (기대 `False`)",
        "차단 게이트 `X_BLOCK_ENABLED` = False 인데 **근거 미기록**",
        "완료 마커 **`daily_close_done`** 없음 — 15:40 일일 마감 완료 마커",
    ])
    assert len(sup) == 1, sup
    assert len(keep) == 4, keep
    for must in ("미커밋", "PC명 태그", "설정 불변식", "차단 게이트"):
        assert any(must in k for k in keep), "%s 가 강등됐다 — 휴장일에도 유효한 사실이다" % must


def test_trading_day_flags_are_untouched():
    """⑧ 거래일에는 **한 건도 강등되지 않는다** — 회귀 방지의 핵심.

    `build()` 는 `is_td` 가 참이면 `split_holiday_flags()` 를 아예 부르지 않지만,
    함수 단위로도 이 성질이 성립하는지 본다(호출부가 바뀌어도 의미가 남게).
    """
    flags = ["당일 날짜 토큰 파일 0개", "**진입 0건** — 차단 0건."]
    keep, sup = CE.split_holiday_flags(flags)
    assert len(sup) == 2 and len(keep) == 0, (keep, sup)   # 함수는 무조건 가른다
    # → 그러므로 "거래일에 강등이 없다"는 성질은 **호출 조건**이 지킨다.
    #   그 조건을 소스에서 직접 확인한다(라인 번호는 박지 않는다).
    import io as _io
    src = _io.open(os.path.join(
        _ROOT, ".claude", "skills", "mireuk-daily-check", "scripts",
        "collect_evidence.py"), encoding="utf-8").read()
    assert "if not is_td:\n        flags, suppressed = split_holiday_flags(flags)" in src, (
        "강등 호출이 `if not is_td:` 가드 밖으로 나갔다 — 거래일 적신호가 사라질 수 있다")


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    _fails = 0
    for _name, _fn in sorted(globals().items()):
        if not _name.startswith("test_") or not callable(_fn):
            continue
        try:
            _fn()
            print("PASS %s" % _name)
        except AssertionError as _e:
            _fails += 1
            print("FAIL %s\n  %s" % (_name, _e))
    print("-" * 60)
    print("%s (%d fail)" % ("ALL PASS" if not _fails else "FAILED", _fails))
    sys.exit(1 if _fails else 0)
