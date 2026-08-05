"""[MW0601 435차] 대시보드 위젯 생성 스모크 테스트 — 기동 전면 실패 회귀 방지.

지키려는 불변식 — **위젯이 생성된다.** `_build()`가 예외 없이 끝나야 한다.

왜 필요한가 (실제 사고, 2026-08-05)
------------------------------------
431차가 `EntryPanel._TIP_QTY` 툴팁 마지막 줄에 `... (%d계약) ..." % MAX_CONTRACTS`를
추가했다. 인접 문자열 리터럴은 **컴파일 시점에 하나로 합쳐진 뒤** `%` 연산이 적용되므로
포매팅 대상이 툴팁 32줄 전체가 됐고, 본문의 리터럴 `%`("기본리스크 = 잔고 × 1%" 등)까지
변환지정자로 해석돼 터졌다:

    ValueError: unsupported format character '?' (0xa) at index 169
      dashboard/main_dashboard.py:3504  EntryPanel._build()

결과: **08:40 장전 자동기동이 5회 재시작 전부 동일 지점에서 실패**, 09:00 개장 시점에
프로세스 0개. 08:57에 수동 수정본으로 겨우 복구했다(개장 3분 전).

**`py_compile` rc=0은 기동 검증이 아니다.** 431차 검증 항목에 py_compile 양 환경 rc=0이
있었고 실제로 통과했다 — 문법 오류가 아니라 `_build()` **실행 시점**의 오류라 정적
컴파일로는 원리상 잡을 수 없다. 단위테스트도 사이저·게이트 로직만 덮었고 위젯 생성
경로는 비어 있었다.

이 파일이 깨지면 그 사고가 재발한 것이다. 대시보드를 건드린 커밋은 이 테스트를 통과해야
한다 — 특히 **툴팁/라벨 문자열에 `%`를 쓰는 변경**이 그렇다.

무엇을 덮고 무엇을 안 덮나
--------------------------
- 덮는다: 위젯 트리 생성(`__init__`/`_build`), 툴팁·라벨 문자열 포매팅, 시그널 연결,
  초기 스타일시트 적용까지. 즉 "기동해서 창이 뜨는가"의 핵심 경로.
- 안 덮는다: 런타임 데이터 갱신(update_* 계열), COM/브로커 연동, Qt 이벤트 루프.
  그건 통합 테스트 영역이고 이 테스트의 목적이 아니다.

실행:
    pytest tests/test_dashboard_smoke.py
    python tests/test_dashboard_smoke.py      (COM/브로커 불필요)

⚠ 헤드리스 환경이어야 한다 — `QT_QPA_PLATFORM=offscreen`을 **QApplication 생성 전에**
   세운다(아래 모듈 상단). 순서가 바뀌면 실제 창을 띄우려다 CI/서버에서 죽는다.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# [422차] 프로덕션 로그·Slack 오염 차단 — conftest가 없는 직접 실행 경로용 2겹 방어.
os.environ["MIREUK_TEST_MODE"] = "1"
# ⚠ QApplication import/생성보다 **먼저** 세워야 한다.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtWidgets import QApplication  # noqa: E402

_APP = None


def _app():
    """QApplication은 프로세스당 1개만 존재할 수 있다 — 재사용한다."""
    global _APP
    if _APP is None:
        _APP = QApplication.instance() or QApplication(sys.argv)
    return _APP


def test_entry_panel_builds():
    """431차 후속2가 죽었던 바로 그 위젯. `_TIP_QTY` 툴팁이 여기 있다."""
    _app()
    from dashboard.main_dashboard import EntryPanel
    w = EntryPanel()
    assert w is not None


def test_entry_panel_tooltips_are_plain_strings():
    """툴팁이 **이미 포맷된 문자열**인지 확인 — 미치환 변환지정자가 남으면 안 된다.

    431차 사고의 본질은 "포매팅이 의도한 범위를 넘었다"였다. 그 역방향(포매팅을
    빼먹어 `%d`가 사용자에게 그대로 보이는 것)도 같은 코드에서 나오기 쉬우므로
    함께 막는다. `%%`(이스케이프된 리터럴 %)는 정상이므로 제거한 뒤 검사한다.
    """
    _app()
    from dashboard import main_dashboard as md

    bad = []
    for name in dir(md):
        if not name.startswith("_TIP"):
            continue
        val = getattr(md, name)
        if not isinstance(val, str):
            continue
        probe = val.replace("%%", "")
        for spec in ("%d", "%s", "%f", "%.1f", "%.2f", "%r"):
            if spec in probe:
                bad.append((name, spec))
    assert not bad, "툴팁에 미치환 변환지정자가 남아 있다: %s" % bad


def test_main_dashboard_builds():
    """전체 대시보드 창 생성 — 기동 경로 종단."""
    _app()
    from dashboard.main_dashboard import MireukDashboard
    w = MireukDashboard()
    assert w is not None


def _run_all():
    fns = [(k, v) for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    failed = 0
    for name, fn in fns:
        try:
            fn()
            print("  [OK]   %s" % name)
        except Exception as e:
            failed += 1
            print("  [FAIL] %s -> %s: %s" % (name, type(e).__name__, e))
    print("\n%d/%d 통과" % (len(fns) - failed, len(fns)))
    return 1 if failed else 0


if __name__ == "__main__":
    print("대시보드 위젯 스모크 (QT_QPA_PLATFORM=%s)" % os.environ.get("QT_QPA_PLATFORM"))
    raise SystemExit(_run_all())
