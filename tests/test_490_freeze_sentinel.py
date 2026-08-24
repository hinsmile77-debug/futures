# -*- coding: utf-8 -*-
"""[MW0601 490차 / F-M] 프로세스 밖 동결 센티넬(FZ-2) 판정 규약.

## 왜 이 테스트가 필요한가

FZ-1 워치독은 라이브 프로세스 **안의** 파이썬 스레드라 GIL 점유형 동결에서
스스로 굶는다 — 2026-08-24 15:40:20 에 `crash_fault.log` 의 30초 `[TS]` 하트비트가
다른 모든 것과 함께 끊긴 것이 실증이다(이상점 1-14). FZ-2 는 그 사각을 메우는
**2층**이며, 이 저장소의 안전장치 중 「감시자 자신이 죽는 실패」를 다루는 유일한
것이다. 판정 규약이 조용히 흔들리면 그 사실을 아무도 모른다.

## 고정하는 규약 셋

1. **AND 판정** — 측정된 신호가 **전부** 정체일 때만 동결이다. 하나라도 신선하면
   프로세스는 살아 있다(단일 신호 오탐 방지).
2. **미측정 ≠ 정체** — 파일이 없는 신호는 분모에서 뺀다. 정체로 세면 기동 전
   시각에 오탐, 신선으로 세면 진짜 동결을 놓친다(계측 4원칙 ②).
3. **알림 전용** — 하드 종료 경로가 코드에 없어야 한다. 승격은 주간회의 안건이며,
   감시자가 새 사고를 만드는 것이 여기서 가장 피해야 할 결과다.
"""
import ast
import io
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
_SCRIPTS = os.path.join(_ROOT, "scripts")
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)

import freeze_sentinel as FS  # noqa: E402

_SRC = os.path.join(_SCRIPTS, "freeze_sentinel.py")
_STALL = 300.0


def _ages(hb, ts, syslog):
    return {FS.SIG_HEARTBEAT: hb, FS.SIG_TS: ts, FS.SIG_SYSLOG: syslog}


def test_3신호_전부_정체면_동결():
    v = FS.judge(_ages(600.0, 600.0, 600.0), stall_sec=_STALL)
    assert v["level"] == "CRITICAL"
    assert v["rc"] == FS.RC_FROZEN
    assert len(v["stale"]) == 3


@pytest.mark.parametrize("fresh_idx", [0, 1, 2])
def test_하나라도_신선하면_정상(fresh_idx):
    """단일 신호로 판정하면 안 된다 — 셋 다 각자의 오탐원이 있다."""
    vals = [600.0, 600.0, 600.0]
    vals[fresh_idx] = 1.0
    v = FS.judge(_ages(*vals), stall_sec=_STALL)
    assert v["level"] == "OK", v["headline"]
    assert v["rc"] == FS.RC_OK


def test_전부_미측정이면_조용히_OK가_아니라_UNKNOWN():
    v = FS.judge(_ages(None, None, None), stall_sec=_STALL)
    assert v["level"] == "UNKNOWN"
    assert v["rc"] == FS.RC_UNKNOWN
    assert len(v["unmeasured"]) == 3


def test_미측정은_정체로_세지_않는다():
    """하트비트 파일만 있고 낡았다 = 동결. 나머지 둘의 부재를 정체로 세면 안 되지만,
    **측정된 것이 전부 정체**라는 사실은 그대로다 — 분모에서 빼는 것이지 무시가 아니다."""
    v = FS.judge(_ages(600.0, None, None), stall_sec=_STALL)
    assert v["level"] == "CRITICAL"
    assert v["unmeasured"] == [FS.SIG_TS, FS.SIG_SYSLOG]
    # 반대 방향: 측정된 하나가 신선하면 나머지가 없어도 정상이다.
    v2 = FS.judge(_ages(1.0, None, None), stall_sec=_STALL)
    assert v2["level"] == "OK"


def test_임계_경계():
    """`>=` 로 판정한다 — 정확히 임계인 값은 정체다(경계를 흔들지 않는다)."""
    assert FS.judge(_ages(_STALL, _STALL, _STALL), stall_sec=_STALL)["level"] == "CRITICAL"
    eps = _STALL - 0.001
    assert FS.judge(_ages(eps, eps, eps), stall_sec=_STALL)["level"] == "OK"


def test_판정문에_세_신호가_모두_적힌다():
    """운영자가 로그 한 줄로 어느 신호가 죽었는지 알아야 한다(계측 4원칙 ③)."""
    v = FS.judge(_ages(600.0, None, 1.0), stall_sec=_STALL)
    joined = chr(10).join(v["details"])
    for name in (FS.SIG_HEARTBEAT, FS.SIG_TS, FS.SIG_SYSLOG):
        assert name in joined, "%s 가 판정문에 없다" % name
    assert "미측정" in joined


def test_하드_종료_경로가_없다():
    """🔴 1단계는 알림 전용이다. 승격은 주간회의 안건 — 코드가 앞서가면 안 된다."""
    src = io.open(_SRC, encoding="utf-8").read()
    tree = ast.parse(src)
    banned = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            owner = getattr(node.func.value, "id", "")
            if (owner, node.func.attr) in (("os", "_exit"), ("os", "kill"),
                                           ("sys", "exit")):
                # `sys.exit(main())` 최상단 진입점만 허용 — 그것은 종료코드 반환이다.
                if node.func.attr == "exit" and node.lineno > len(src.splitlines()) - 4:
                    continue
                banned.append("%s.%s at line %d" % (owner, node.func.attr, node.lineno))
    assert not banned, (
        "FZ-2 에 하드 종료 경로가 생겼다 — 1단계는 알림 전용이다 (490차 F-M): %s"
        % banned
    )
    assert "taskkill" not in src, "FZ-2 가 taskkill 을 부른다 — 알림 전용 규약 위반"


def test_TS_꼬리_탐색이_점진적으로_넓어진다():
    """동결 뒤에는 덤프가 쏟아져 마지막 `[TS]` 를 뒤로 밀어낸다 — 2026-08-24 실측
    5.1MB 파일에서 끝에서 약 450KB 앞이었다. 고정 꼬리(64KB)면 **진짜 동결일에만**
    못 찾는다."""
    src = io.open(_SRC, encoding="utf-8").read()
    assert "max_scan_bytes" in src, "TS 꼬리 탐색 상한 인자가 없다"
    assert "span = min(span * 2" in src, (
        "TS 꼬리를 넓히지 않는다 — 동결 직후 덤프에 밀려 미측정이 된다 (490차 F-M 회귀)"
    )


def test_감시창이_마감_이후까지_본다():
    """FZ-1 의 `("09:00","15:45")` 는 2026-08-24 동결을 아슬아슬하게 벗어난다."""
    from config.settings import FREEZE_SENTINEL_WINDOW as w
    end_h, end_m = [int(x) for x in str(w[1]).split(":")]
    assert (end_h, end_m) >= (16, 0), (
        "FZ-2 감시 창이 16:00 이전에 끝난다 — 15:40 마감 동결과 EOD 인계 구간을 놓친다"
    )
