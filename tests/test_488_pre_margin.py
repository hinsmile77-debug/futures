# -*- coding: utf-8 -*-
"""[MW0602 488차 계획 A] 장전 발화 마진 불변식.

무엇을 재는가
-------------
`발화 마진 = 09:00:00 − 다이제스트 생성시각`. 예약 점검이 개장에 얼마나 붙어서
발화했는지다. 0821 O-10 이 이 값을 **예측 47초 vs 실측 12초**(4배 차)로 마주쳤는데,
아무도 매일 보고 있지 않아 단발 관측으로 판정할 뻔했다. 반대편에서는 0819 장전 점검이
**09:07**(개장 7분 후)에 돌아 장전/장중 표본이 한 파일에 섞였다.

이 파일이 고정하는 불변식
------------------------
① 양수(개장 전) · 음수(개장 후) · 소급 실행 3케이스의 반환 계약
② `MARGIN_WARN_SEC`(30초) · `MARGIN_WARN_STREAK`(2일)이 **사전등록 값 그대로**
   — 313차 ④(결과를 보고 문턱을 움직이지 않는다)를 코드로 잠근다
③ 연속 판정 규칙: 소급본(미측정)은 정상으로도 위반으로도 세지 않는다
④ 이력 파서가 다이제스트 생성 줄의 **고정 형식**을 실제로 읽어낸다

실행:
    python tests/test_488_pre_margin.py
"""
import io
import os
import sys
import tempfile
from datetime import date, datetime

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, ".claude", "skills", "mireuk-daily-check", "scripts"))

import collect_evidence as CE


def test_margin_positive_before_open():
    """① 개장 전 실행 — 마진은 양수이고 초 단위로 정확하다."""
    d = date(2026, 8, 24)
    got, kind = CE._fire_margin(d, datetime(2026, 8, 24, 8, 59, 48))
    assert kind == "live", kind
    assert got == 12, got                      # 0821 실측과 같은 값
    assert "+12초" in CE.fmt_margin(got), CE.fmt_margin(got)


def test_margin_negative_after_open():
    """② 개장 후 실행 — 음수로 나오고 표기가 「개장 후」임을 밝힌다.

    0819 사고(09:07 실행)를 그대로 재현한다. 절댓값만 보고 「7분 여유」로 읽으면 안 된다.
    """
    d = date(2026, 8, 24)
    got, kind = CE._fire_margin(d, datetime(2026, 8, 24, 9, 7, 0))
    assert kind == "live", kind
    assert got == -420, got
    txt = CE.fmt_margin(got)
    assert "개장 7분 0초 후" in txt, txt
    assert txt.startswith("−"), txt


def test_margin_backfill_is_not_measured():
    """③ 소급 실행 — 마진을 **재지 않는다**.

    0823 이상점 1-2(예약작업 재실행으로 일요일에 08-21분이 다시 돌았다)에서 나오는
    「마진」은 발화 품질이 아니라 재실행 시각일 뿐이다. 추이에 섞으면 판정이 오염된다.
    """
    got, kind = CE._fire_margin(date(2026, 8, 21), datetime(2026, 8, 23, 15, 2, 0))
    assert kind == "backfill", kind
    assert got is None, got
    assert CE.fmt_margin(None) == "—"


def test_prereg_thresholds_are_frozen():
    """④ 사전등록 임계 고정 — 결과를 보고 문턱을 움직이지 않는다(313차 ④).

    이 값을 바꾸려면 이 테스트를 함께 고쳐야 하고, 그 순간 왜 바꾸는지 근거를 남기게 된다.
    """
    assert CE.MARGIN_WARN_SEC == 30, CE.MARGIN_WARN_SEC
    assert CE.MARGIN_WARN_STREAK == 2, CE.MARGIN_WARN_STREAK
    assert CE.MARGIN_ANCHOR == "09:00:00", CE.MARGIN_ANCHOR


def test_streak_flag_rules():
    """⑤ 연속 판정 — 임계 이상이면 침묵, 연속 2일이면 적신호, 소급본은 중립."""
    # 여유 있는 마진 → 적신호 없음
    assert CE.margin_streak_flag(120, [("20260821", 100)]) is None
    # 오늘만 미달, 어제는 정상 → 아직 아니다(연속 1일)
    assert CE.margin_streak_flag(12, [("20260821", 100)]) is None
    # 이틀 연속 미달 → 적신호
    msg = CE.margin_streak_flag(12, [("20260821", 20)])
    assert msg and "2거래일 연속" in msg, msg
    # 🔴 cron 을 앞당기라는 결론으로 읽히지 않게 경고가 함께 나가야 한다
    assert "08:58:30" in msg and "A-2" in msg, msg
    # 소급본(None)은 정상으로도 위반으로도 세지 않는다 — 건너뛰고 그 뒤를 본다
    msg2 = CE.margin_streak_flag(12, [("20260822", None), ("20260821", 20)])
    assert msg2 and "2거래일 연속" in msg2, msg2
    # 마진을 못 잰 날(소급/None)만 있으면 판정하지 않는다
    assert CE.margin_streak_flag(None, [("20260821", 20)]) is None


def test_late_runs_are_not_counted_as_tight_margin():
    """⑥ 🔴 개장 **후** 실행은 「마진 빠듯함」연속에 넣지 않는다.

    둘은 다른 사건이다 — 지각은 별도 적신호(`개장 후 N분`)로 이미 올라간다.
    실측이 이 구분의 필요를 보여줬다: 08-18·08-14 다이제스트는 각각 개장 452분·635분
    **후**에 생성된 수동 실행분인데, 부호만 보고 세면 "마진 빠듯함 4일 연속"이 된다.
    그렇게 뭉개면 진짜 마진 소진 추세를 수동 실행 이력이 덮어버린다.
    """
    # 오늘이 지각(음수)이면 tight 판정 자체를 하지 않는다
    assert CE.margin_streak_flag(-420, [("20260821", 12)]) is None
    # 과거 지각일은 **중립** — 연속을 끊지도, 위반으로 세지도 않는다
    msg = CE.margin_streak_flag(12, [("20260822", -27136), ("20260821", 20)])
    assert msg and "2거래일 연속" in msg, msg
    # 과거가 전부 지각뿐이면 연속이 성립하지 않는다(오늘 1일뿐)
    assert CE.margin_streak_flag(12, [("20260822", -454), ("20260821", -424)]) is None
    # 여유 있는 날이 끼면 연속이 끊긴다
    assert CE.margin_streak_flag(12, [("20260822", 300), ("20260821", 5)]) is None


def test_is_tight_boundaries():
    """⑦ 경계 — 0초는 tight, 30초는 아니다(임계는 미만 비교), 음수는 tight 아님."""
    assert CE._is_tight(0) is True
    assert CE._is_tight(29) is True
    assert CE._is_tight(30) is False
    assert CE._is_tight(-1) is False
    assert CE._is_tight(None) is False


def test_history_parses_fixed_generation_line():
    """⑥ 이력 파서 — 다이제스트 생성 줄의 고정 형식을 실제로 읽는다.

    형식이 바뀌면 추이가 조용히 빈 표가 된다(그 자체가 이 프로젝트의 단골 실패다).
    """
    with tempfile.TemporaryDirectory() as tmp:
        # 정상 장전본 — 08:59:48 생성 → 마진 +12초
        io.open(os.path.join(tmp, "evidence_MW0602-20260821_pre.md"),
                "w", encoding="utf-8").write(
            "# 미륵이 증거 다이제스트\n\n"
            "- 생성 2026-08-21 08:59:48 KST · PC **MW0602** (`host`)\n")
        # 소급본 — 대상일과 생성일이 다르다 → 미측정으로 표시돼야 한다
        io.open(os.path.join(tmp, "evidence_MW0602-20260820_pre.md"),
                "w", encoding="utf-8").write(
            "- 생성 2026-08-23 15:02:00 KST · PC **MW0602** (`host`)\n")
        # 다른 PC / 다른 국면은 섞이면 안 된다
        io.open(os.path.join(tmp, "evidence_MW0601-20260819_pre.md"),
                "w", encoding="utf-8").write("- 생성 2026-08-19 08:50:00 KST\n")
        io.open(os.path.join(tmp, "evidence_MW0602-20260819_post.md"),
                "w", encoding="utf-8").write("- 생성 2026-08-19 16:30:00 KST\n")

        hist = CE.read_margin_history(tmp, "MW0602", date(2026, 8, 24))
        got = dict(hist)
        assert got.get("20260821") == 12, hist
        assert "20260820" in got and got["20260820"] is None, hist
        assert "20260819" not in got, "다른 PC·다른 국면이 섞였다: %s" % hist


def test_holiday_suppression_list_is_locked():
    """⑦ 휴장일 강등 목록이 **6종**으로 잠겨 있다 (486차 F-1, 계획 B 동반).

    과잉 억제가 이 기능의 최대 위험이다 — 목록이 늘면 진짜 결함이 있는 거래일에
    적신호가 통째로 사라질 수 있다. 늘리려면 이 테스트를 고쳐야 한다.
    """
    assert len(CE.HOLIDAY_SUPPRESS) == 6, CE.HOLIDAY_SUPPRESS
    keep, sup = CE.split_holiday_flags([
        "당일 날짜 토큰 파일 0개 — 프로그램이 안 돌았거나",
        "장후인데 **15:10 청산 경로가 아무 흔적도 남기지 않았다**",
        "완료 마커 **`eod_retrain_done`** 없음",
        "미커밋 변경 3건",                      # 휴장일에도 유효한 사실 → 남는다
        "PC명 태그 누락 커밋 2건",              # 〃
        "설정 불변식 `CB_CONSEC_STOP_LIMIT` = `2` (기대 `9999`)",   # 〃
    ])
    assert len(sup) == 3, sup
    assert len(keep) == 3, keep
    assert any("미커밋" in k for k in keep)
    assert any("설정 불변식" in k for k in keep), "불변식 불일치는 휴장일에도 올려야 한다"


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
