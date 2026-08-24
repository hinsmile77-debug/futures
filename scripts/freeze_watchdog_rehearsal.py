# -*- coding: utf-8 -*-
"""[MW0601 478차 후속 / FZ-1 검증] 동결 워치독 리허설 — 라이브 발동 확인.

## 왜 유닛 테스트로 충분하지 않은가

`tests/test_478_freeze_watchdog.py`는 판정 로직과 배선을 고정하지만,
**"실제로 프로세스가 죽고 런처가 다시 띄우는가"** 는 확인하지 않는다.
471차 F-1이 남긴 교훈이 정확히 이것이다 — 15:10 강제청산 경로가 6개월간
"코드에 있으니 지켜진다"고 믿어졌으나 구조적으로 도달 불가였고, 어떤
테스트도 그것을 잡지 못했다. 집행 경로의 생존은 리허설로만 확인된다.

## 세 가지 모드

    python scripts/freeze_watchdog_rehearsal.py --dry
        워치독을 실제로 돌려 하트비트를 끊었을 때 발화 **판정**까지만 확인한다.
        os._exit을 가로채므로 아무 프로세스도 죽지 않는다. 언제 돌려도 안전하다.

    python scripts/freeze_watchdog_rehearsal.py --gil
        [490차 F-M] **GIL 점유형 동결** 시나리오. `time.sleep()` 이 아니라 C 확장
        블로킹으로 GIL 을 붙잡아, FZ-1 이 그 유형에서 **원리적으로 발동 불가**임을
        재현한다. 그리고 같은 상황을 프로세스 밖 센티넬(FZ-2, `scripts/
        freeze_sentinel.py`)이 잡아내는지 3신호 판정으로 확인한다.

    python scripts/freeze_watchdog_rehearsal.py --live-instructions
        라이브 미륵이에서 하는 절차를 출력한다(실행하지 않는다).

## 왜 `--gil` 이 따로 필요한가 (2026-08-24 이상점 1-14)

`--dry` 는 "하트비트를 **갱신하지 않는다**"를 흉내 낸다 — 감시 스레드 자신은
멀쩡히 돈다. 그런데 2026-08-24 15:40:20 의 실제 동결은 그 형태가 아니었다:
마감 스레드가 워커에서 Qt 위젯을 만져 **GIL 을 쥔 채 반환하지 않았고**, 그래서
감시 스레드가 바이트코드를 한 줄도 실행하지 못했다(`crash_fault.log` 의 30초
`[TS]` 하트비트가 `15:40:03` 에서 함께 끊긴 것이 증거).

즉 `--dry` 가 통과해도 이 유형은 **여전히 못 잡는다.** 임계 조정으로 풀리는
문제가 아니라 **감시 위치의 문제**이며, 그것이 FZ-2 를 프로세스 밖에 둔 이유다.

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


def _hold_gil(seconds):
    """GIL 을 붙잡은 채 `seconds` 만큼 반환하지 않는다 — C 확장 블로킹으로 재현.

    ⚠ `time.sleep()` 을 쓰면 안 된다. sleep 은 GIL 을 **놓으므로** 다른 파이썬
      스레드가 정상적으로 돈다 — 그것은 2026-08-24 동결의 재현이 아니라
      `--dry` 가 이미 하는 「하트비트 미갱신」의 반복이다.

    여기서는 `zlib` 압축(C 확장, GIL 유지)을 반복해 붙잡는다. 실제 사고는
    PyQt 위젯 접근 데드락이었지만, 감시 스레드 관점에서 관측되는 사실
    (**바이트코드를 한 줄도 못 돈다**)은 동일하다.
    """
    import zlib
    blob = os.urandom(1 << 20)
    deadline = time.time() + seconds
    while time.time() < deadline:
        zlib.compress(blob, 9)


def run_gil():
    """[490차 F-M] GIL 점유형 동결 — FZ-1 미탐 실증 + FZ-2 탐지 확인."""
    log_path = os.path.join("logs", "freeze_watchdog_rehearsal_gil.log")
    fired = {"n": 0}
    beat = {"t": time.time()}
    ticks = {"n": 0}

    def _beat_fn():
        ticks["n"] += 1          # 감시 스레드가 실제로 돈 횟수
        return beat["t"]

    wd = FreezeWatchdog(
        beat_fn=_beat_fn,
        active_fn=lambda: True,
        context_fn=lambda: "  (GIL 리허설 — 실제 포지션 아님)",
        on_fire=lambda: fired.__setitem__("n", fired["n"] + 1),
        check_sec=0.5,
        stall_sec=1.5,
        strikes=2,
        window=None,
        fault_log_path=log_path,
        ts_heartbeat=True,
    )

    print("[GIL 리허설] check=0.5s stall=1.5s strikes=2 — 운영값의 압축판")
    print("기록: %s" % log_path)
    wd.start()
    time.sleep(1.0)
    beat["t"] = time.time()
    ticks_before = ticks["n"]

    print()
    print("[1단계] GIL 을 8초간 점유한다 (zlib C 확장 루프 — sleep 아님)")
    print("        하트비트는 갱신하지 않는다. FZ-1 임계(1.5s×2)를 훨씬 넘긴다.")
    t0 = time.time()
    _hold_gil(8.0)
    held = time.time() - t0
    ticks_during = ticks["n"] - ticks_before
    wd.stop()

    print("        점유 %.1fs 동안 감시 스레드가 돈 횟수 = %d회 "
          "(정상이라면 약 %d회)" % (held, ticks_during, int(held / 0.5)))
    print("        FZ-1 발화 = %d회" % fired["n"])

    # ── 판정 ─────────────────────────────────────────────────────────────
    # ⚠ 이 리허설의 "통과"는 **FZ-1이 발화하는 것이 아니다.** 발화하지 못한다는
    #   사실을 실증하는 것이 목적이다(1-14). CPython 은 스레드 전환 간격마다
    #   GIL 을 넘겨줄 수 있어 감시 스레드가 몇 번 돌 수도 있으므로, "0회"를
    #   요구하지 않고 **현저한 감소**를 본다.
    expected = max(1, int(held / 0.5))
    starved = ticks_during < expected * 0.5
    print()
    if starved:
        print("[판정] 재현 성공 — 감시 스레드가 굶었다(%d/%d회). FZ-1 은 이 유형에서"
              % (ticks_during, expected))
        print("       원리적으로 신뢰할 수 없다. 그래서 FZ-2(프로세스 밖)가 필요하다.")
    else:
        print("[판정] 재현 실패 — 감시 스레드가 정상 빈도로 돌았다(%d/%d회)."
              % (ticks_during, expected))
        print("       이 환경에서는 GIL 점유가 충분히 강하지 않다(운영 PC 에서 다시 볼 것).")

    # ── FZ-2 쪽 확인 ─────────────────────────────────────────────────────
    print()
    print("[2단계] 같은 상황을 프로세스 밖 센티넬(FZ-2)이 잡는가 — 순수 판정 함수 확인")
    try:
        from scripts.freeze_sentinel import judge, SIG_HEARTBEAT, SIG_TS, SIG_SYSLOG
    except ImportError:
        sys.path.insert(0, os.path.join(_ROOT, "scripts"))
        from freeze_sentinel import judge, SIG_HEARTBEAT, SIG_TS, SIG_SYSLOG

    frozen = judge({SIG_HEARTBEAT: 600.0, SIG_TS: 600.0, SIG_SYSLOG: 600.0}, stall_sec=300.0)
    alive = judge({SIG_HEARTBEAT: 5.0, SIG_TS: 600.0, SIG_SYSLOG: 600.0}, stall_sec=300.0)
    unknown = judge({SIG_HEARTBEAT: None, SIG_TS: None, SIG_SYSLOG: None}, stall_sec=300.0)
    print("        3신호 전부 정체  → %s (rc=%d)" % (frozen["level"], frozen["rc"]))
    print("        하나라도 신선    → %s (rc=%d)" % (alive["level"], alive["rc"]))
    print("        전부 미측정      → %s (rc=%d)" % (unknown["level"], unknown["rc"]))
    ok = (frozen["level"] == "CRITICAL" and alive["level"] == "OK"
          and unknown["level"] == "UNKNOWN")
    print("        판정 로직 %s" % ("OK" if ok else "실패 — FZ-2 판정이 규약과 다르다"))

    print()
    print("[3단계] 2026-08-24 실제 로그 재생 (있으면)")
    print("        python scripts/freeze_sentinel.py --once "
          "--at-time \"2026-08-24 15:50:00\" --no-popup")
    print("        기대: CRITICAL · rc=3 (heartbeat·[TS]·SYSTEM.log 3신호 전부 정체)")
    print()
    print("⚠ 하드 종료 승격은 이 리허설로 확인되지 않는다 — FZ-2 는 **알림 전용**이고")
    print("  승격은 주간회의 안건이다.")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description="FZ-1/FZ-2 동결 감시 리허설")
    ap.add_argument("--dry", action="store_true",
                    help="워치독을 압축 임계로 돌려 발화 판정까지 확인(프로세스 안 죽음)")
    ap.add_argument("--gil", action="store_true",
                    help="[490차 F-M] GIL 점유형 동결 재현 — FZ-1 미탐 실증 + FZ-2 판정 확인")
    ap.add_argument("--live-instructions", action="store_true",
                    help="라이브 리허설 절차를 출력한다(실행하지 않음)")
    args = ap.parse_args()

    # [490차 F-M] cp949 콘솔이 em dash(—) 하나에 UnicodeEncodeError 를 낸다 —
    # 478차 후속 §8-2 가 FZ-1 발화 기록을 통째로 잃은 것과 같은 원인이다.
    # 리허설 출력이 인코딩 때문에 끊기면 판정문을 못 읽는다.
    try:
        from utils.analysis_db import utf8_console
        utf8_console()
    except Exception:
        for _stream in ("stdout", "stderr"):
            try:
                getattr(sys, _stream).reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass

    if args.live_instructions:
        print(_LIVE_STEPS)
        return 0
    if args.dry:
        return run_dry()
    if args.gil:
        return run_gil()
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
