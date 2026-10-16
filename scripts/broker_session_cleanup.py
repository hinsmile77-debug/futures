# -*- coding: utf-8 -*-
"""장후 CREON/Cybos Plus API 세션 정리 — 연결이 살아 있을 때 PlusDisconnect() 로 내린다.

[MW0601 2026-10-16] 배경 (docs/정기점검/매일점검/MW0601-20261016-CREON기동-coStarter크래시-딥다이브.md)
    미륵이는 15:47 자동 종료하지만 API 세션(CpStart·DibServer)은 그대로 남는다. 밤사이 서버
    쪽 연결이 끊기면 프로세스만 남은 「좀비」가 되고, 다음 날 08:35 첫 COM 접속에 DibServer 가
    죽는다(09-24 · 10-05 · 10-06 · 10-13 · 10-15 · 10-16 전부 08:35:10–14). 좀비 CpStart 는 kill 로도
    안 내려가 coStarter 가 「이미 실행중 → 예」 에서 크래시한다(ACCESS_VIOLATION 팝업).

    좀비가 된 뒤에는 정리 수단이 없지만, **연결이 살아 있을 때의 PlusDisconnect() 는 CpStart 를
    실제로 내렸다**(2026-10-15 13:41 실측, 관리자 Stop-Process 는 무효였다). 그래서 좀비가 되기 전,
    장후 작업이 끝난 시각에 내린다.

    32bit 파이썬(py37_32)으로 실행해야 한다(Cybos COM).

종료 코드
    0  정리 완료(CpStart 내려감) 또는 정리할 세션 없음
    2  PlusDisconnect 후에도 CpStart 생존
    5  COM 판독 실패
출력 한 줄: ``RESULT=<상태> ...`` (호출하는 PS 스크립트가 로그에 옮긴다)
"""
from __future__ import print_function

import sys
import time


def _cpstart_pids():
    import psutil
    return [p.pid for p in psutil.process_iter(["name"])
            if (p.info["name"] or "").lower() == "cpstart.exe"]


def main(wait_sec=20.0):
    before = _cpstart_pids()
    if not before:
        print("RESULT=NO_SESSION cpstart=0")
        return 0
    try:
        import win32com.client as w
        c = w.Dispatch("CpUtil.CpCybos")
        conn = int(c.IsConnect)
        st = int(c.ServerType)
    except Exception as e:
        print("RESULT=PROBE_FAIL cpstart=%s err=%s" % (before, e))
        return 5
    # 연결이 끊긴 좀비에도 한 번은 요청해 본다 — 효과는 미검증이지만 해가 없다.
    try:
        c.PlusDisconnect()
        asked = "ok"
    except Exception as e:
        asked = "err:%s" % e
    end = time.time() + wait_sec
    while time.time() < end and _cpstart_pids():
        time.sleep(0.5)
    left = _cpstart_pids()
    state = "DISCONNECTED" if not left else ("ZOMBIE_LEFT" if conn != 1 else "STILL_ALIVE")
    print("RESULT=%s was_connected=%d server_type=%d plus_disconnect=%s cpstart_before=%s cpstart_after=%s"
          % (state, conn, st, asked, before, left))
    return 0 if not left else 2


if __name__ == "__main__":
    sys.exit(main())
