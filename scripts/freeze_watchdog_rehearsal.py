# -*- coding: utf-8 -*-
"""[MW0601 478차 후속 / FZ-1 검증] 동결 워치독 리허설 — 라이브 발동 확인.

## 왜 유닛 테스트로 충분하지 않은가

`tests/test_478_freeze_watchdog.py`는 판정 로직과 배선을 고정하지만,
**"실제로 프로세스가 죽고 런처가 다시 띄우는가"** 는 확인하지 않는다.
471차 F-1이 남긴 교훈이 정확히 이것이다 — 15:10 강제청산 경로가 6개월간
"코드에 있으니 지켜진다"고 믿어졌으나 구조적으로 도달 불가였고, 어떤
테스트도 그것을 잡지 못했다. 집행 경로의 생존은 리허설로만 확인된다.

## 두 가지 모드

    python scripts/freeze_watchdog_rehearsal.py --dry
        워치독을 실제로 돌려 하트비트를 끊었을 때 발화 **판정**까지만 확인한다.
        os._exit을 가로채므로 아무 프로세스도 죽지 않는다. 언제 돌려도 안전하다.

    python scripts/freeze_watchdog_rehearsal.py --live-instructions
        라이브 미륵이에서 하는 절차를 출력한다(실행하지 않는다).

## 라이브 리허설 판정 기준

정상 = `logs/crash_fault.log`에 아래가 순서대로 남고, 런처 로그에
`[AUTO-RESTART] main.py 재시작`이 이어진다:

    [TS] ... beat_age=0s   ...  (평시)
    [TS] ... beat_age=185s ...  (1스트라이크)
    [FreezeWatchdog] CRITICAL 메인 이벤트 루프 동결 판정 — 하드 종료

⚠ 반드시 **모의투자 계좌 · FLAT 상태 · 장 시작 전(08:45~08:55)** 에 할 것.
  포지션을 들고 하면 재기동 사이 공백에 청산 감시가 잠시 비는 창이 생긴다.
  15:10 이후에는 하지 말 것 — 런처가 재기동하지 않는다(오버나이트 금지 정책).
"""
from __future__ import annotations

import argparse
import os
import sys
import time

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.freeze_watchdog import FreezeWatchdog     # noqa: E402


_LIVE_STEPS = """
라이브 리허설 절차 (모의투자 · FLAT · 08:45~08:55)
────────────────────────────────────────────────────────────
1. 미륵이를 평소대로 기동한다(start_mireuk.bat).
   기동 직후 SYSTEM 로그에 다음 줄이 있어야 한다:
       [FreezeWatchdog] 기동 — 하트비트 180s 정체 ×2회 연속 시 os._exit(43)
   없으면 여기서 중단하고 설정(FREEZE_WATCHDOG_ENABLED / MIREUK_FREEZE_WATCHDOG)을 확인한다.

2. logs/crash_fault.log 를 tail 한다. 30초마다 다음이 찍혀야 한다:
       [TS] 2026-..T08:5X:XX beat_age=0s watching=True strikes=0
   beat_age가 계속 0~5초면 하트비트 3중화가 정상이다.

3. 동결을 주입한다. 대시보드 파이썬 콘솔이 없으므로, 가장 간단한 방법은
   디버거 없이 메인 스레드를 붙잡는 것이다 — 권장하지 않는 방법(강제 일시정지)
   대신 **아래 --dry 모드로 판정 경로를 확인**하고, 실제 하드 종료 동작은
   4번의 수동 확인으로 대체한다.

4. 하드 종료·재기동 경로 확인(주입 없이):
   a) 작업관리자에서 main.py 프로세스를 '일시 중단(Suspend)'한다
      (Process Explorer 등). 이것이 동결과 등가다 — 스레드가 전부 멈춘다.
      ⚠ 워치독 스레드도 함께 멈추므로 발화하지 않는다. 즉 이 방법은
        **워치독 검증에는 쓸 수 없다** — 프로세스 단위 정지이기 때문이다.
   b) 대신 메인 스레드만 붙잡아야 한다. 실전 재현은 어려우므로, 다음 배포에서
      임시 디버그 훅(예: 환경변수 MIREUK_DEBUG_FREEZE_SEC=400 이면 기동 후
      60초 시점에 메인에서 time.sleep(400))을 넣어 1회 확인하고 제거한다.
      이 훅은 상시 코드에 남기지 않는다 — 사고 유발기를 프로덕션에 두지 않는다.

5. 판정: crash_fault.log 에 CRITICAL 블록이 남고, 런처 로그
   logs/Mireuk_batch/launcher_*.log 에 [AUTO-RESTART] 가 이어지면 통과.
   재기동 후 세션 복원(session_recovery_service)이 포지션·카운터를 되살리는지
   대시보드로 확인한다.
────────────────────────────────────────────────────────────
"""


def run_dry():
    """워치독을 실제 스레드로 돌려 발화 판정까지 확인한다(프로세스는 안 죽는다)."""
    log_path = os.path.join("logs", "freeze_watchdog_rehearsal.log")
    fired = {"n": 0}
    beat = {"t": time.time()}

    wd = FreezeWatchdog(
        beat_fn=lambda: beat["t"],
        active_fn=lambda: True,
        context_fn=lambda: "  (리허설 — 실제 포지션 아님)",
        on_fire=lambda: fired.__setitem__("n", fired["n"] + 1),
        check_sec=1.0,          # 리허설은 1초 주기로 압축
        stall_sec=3.0,          # 180초 대신 3초
        strikes=2,
        window=None,
        fault_log_path=log_path,
        ts_heartbeat=True,
    )

    print("리허설 시작 — check=1s stall=3s strikes=2 (운영값 30/180/2의 압축판)")
    print("기록: %s" % log_path)

    wd.start()
    print("\n[1단계] 하트비트 정상 — 5초간 발화하지 않아야 한다")
    for _ in range(5):
        beat["t"] = time.time()
        time.sleep(1.0)
    assert fired["n"] == 0, "정상 하트비트인데 발화했다 — 오탐 (운영 배포 금지)"
    print("       OK — 발화 0회")

    print("\n[2단계] 하트비트 정지 — 2회 연속 스트라이크 후 발화해야 한다")
    time.sleep(8.0)     # 갱신 없음
    wd.stop()
    if fired["n"] >= 1:
        print("       OK — 발화 %d회" % fired["n"])
    else:
        print("       실패 — 하트비트가 멈췄는데 발화하지 않았다 (미탐)")
        return 1

    print("\n판정: 통과. 운영 임계(180s×2)에서도 같은 경로를 탄다.")
    print("      다만 **하드 종료·런처 재기동은 이 리허설로 확인되지 않는다** —")
    print("      --live-instructions 의 4·5번을 별도로 수행할 것.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="FZ-1 동결 워치독 리허설")
    ap.add_argument("--dry", action="store_true",
                    help="워치독을 압축 임계로 돌려 발화 판정까지 확인(프로세스 안 죽음)")
    ap.add_argument("--live-instructions", action="store_true",
                    help="라이브 리허설 절차를 출력한다(실행하지 않음)")
    args = ap.parse_args()

    if args.live_instructions:
        print(_LIVE_STEPS)
        return 0
    if args.dry:
        return run_dry()
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
