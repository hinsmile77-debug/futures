# -*- coding: utf-8 -*-
"""
[진단 전용 · 읽기 전용] 단일 인스턴스 가드(`start_mireuk.bat` `[GUARD]`)가 무엇을
잡는지 눈으로 확인한다.

왜 필요한가 (2026-08-25 493차, 리포트 이상점 1-8 / 제1부-C)
-----------------------------------------------------------------
런처 로그 11개 전수에서 `[WARN] 이미 실행 중인 main.py 프로세스가 감지됐습니다.`가
**10회**, `[GUARD] 기존 main.py 없음`이 **0회**다. 전날 정상 종료가 로그로 확인되는
날에도(08-21 금 `auto_shutdown` → 주말 → 08-24 월 감지) 전부 감지가 떴다.
프로브 자체는 정상 동작함이 확인됐으므로(H1 기각), **판정식이 미륵이가 아닌 다른
파이썬 프로세스를 잡아 `p.terminate()` 해 왔을 개연성**이 남았다.

그런데 그 사실을 확인할 수 없다. 런처의 판정 근거 3갈래가 전부 폐기되기 때문이다:
  (a) 종료코드   — "찾았다"(1)와 "예외로 죽었다"(1)가 같은 값
  (b) 표준오류   — 줄 끝 `2>NUL` 로 traceback 폐기
  (c) 표준출력   — 프로브의 `PID=… cmd=…` 가 런처 로그에 11개 전수 **0건**
                   (`CALL :L` 로 쓴 줄만 로그에 들어간다)

이 스크립트는 그 (c)를 사람 손으로 대신 본다.

무엇을 하지 않는가 (안전)
-----------------------------------------------------------------
* **프로세스를 절대 종료하지 않는다.** `terminate`/`kill` 호출이 이 파일에 없다.
* 파일을 쓰지 않는다. DB에 접속하지 않는다. 주문을 내지 않는다.
* `main.py` / `config/settings.py` / 매매 로직을 import 하지 않는다.
  표준 라이브러리와 `psutil` 만 쓴다. **장중에 실행해도 안전하다.**

실행
-----------------------------------------------------------------
    32비트(런처가 실제로 쓰는 환경 — 이게 기준이다):
      C:\\Users\\82108\\anaconda3\\envs\\py37_32\\python.exe scripts\\diag_guard_processes.py

    64비트(사각지대 대조용):
      C:\\Users\\82108\\anaconda3\\python.exe scripts\\diag_guard_processes.py

  두 결과의 `판독불가` 개수가 다르면, 32비트 프로브가 64비트 프로세스의 명령줄을
  못 읽어 **미탐**한다는 뜻이다(계측 4원칙 ② — 미측정을 불일치로 바꿔 읽는 것).

이 파일의 위치
-----------------------------------------------------------------
F-U(단일 인스턴스 가드 재작성)의 프로브 원형이다. F-U 구현 시
`scripts/guard_single_instance.py` 로 정리하면서 종료코드 3분류(0/1/3)와
로그 기록을 붙인다. 그때까지는 진단 전용으로 둔다.
"""

from __future__ import print_function

import datetime
import os
import struct
import sys

try:
    import psutil
except ImportError:
    print("[FATAL] psutil 이 없습니다. 런처의 [GUARD] 프로브도 같은 이유로 실패합니다.")
    print("        설치: pip install psutil")
    sys.exit(2)


# 런처가 실제로 쓰는 판정식과 **글자 하나까지 같게** 유지할 것.
# start_mireuk.bat:435 / start_mireuk_CREON.bat:377
NEEDLE = "main.py"

WORKDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIREUK_MAIN = os.path.normcase(os.path.join(WORKDIR, "main.py"))

# 아침 기동 창 — 런처가 08:40:00 에 뜨고 [GUARD] 프로브는 약 08:40:24 에 돈다.
# 08:40:37 에 terminate 가 돌므로, 그 직후에 켜진 프로세스는
# "죽고 곧바로 다시 켜진" 것일 수 있다.
SUSPECT_FROM = (8, 35)
SUSPECT_TO = (8, 50)


def _fmt_time(ts):
    try:
        return datetime.datetime.fromtimestamp(ts).strftime("%H:%M:%S")
    except Exception:
        return "??:??:??"


def _in_suspect_window(ts):
    try:
        t = datetime.datetime.fromtimestamp(ts)
    except Exception:
        return False
    if t.date() != datetime.date.today():
        return False
    lo = t.replace(hour=SUSPECT_FROM[0], minute=SUSPECT_FROM[1], second=0, microsecond=0)
    hi = t.replace(hour=SUSPECT_TO[0], minute=SUSPECT_TO[1], second=0, microsecond=0)
    return lo <= t <= hi


def collect():
    """파이썬 프로세스를 전수 수집한다. 종료하지 않는다."""
    rows = []
    unreadable = []
    for proc in psutil.process_iter(["pid", "name", "cmdline", "create_time", "exe"]):
        info = proc.info or {}
        name = (info.get("name") or "")
        if "python" not in name.lower():
            continue

        cmdline = info.get("cmdline")
        # 계측 4원칙 ② — "못 읽었다"와 "빈 명령줄"을 같은 값으로 표현하지 않는다.
        # 32비트 파이썬에서 64비트 프로세스를 읽으면 psutil 이 None 을 준다.
        readable = cmdline is not None
        cmd = " ".join(c for c in (cmdline or []) if c)

        # cwd 는 권한이 없으면 못 읽는다 — 그 사실도 값으로 남긴다.
        try:
            cwd = proc.cwd()
        except Exception:
            cwd = None

        row = {
            "pid": info.get("pid"),
            "name": name,
            "created": info.get("create_time") or 0,
            "exe": info.get("exe") or "",
            "cmd": cmd,
            "readable": readable,
            "cwd": cwd,
        }
        rows.append(row)
        if not readable:
            unreadable.append(row)

    rows.sort(key=lambda r: r["created"])
    return rows, unreadable


def main():
    bits = struct.calcsize("P") * 8
    now = datetime.datetime.now()

    print("=" * 78)
    print(" 단일 인스턴스 가드 진단 — 읽기 전용 (아무 프로세스도 종료하지 않는다)")
    print(" 실행 시각 : %s" % now.strftime("%Y-%m-%d %H:%M:%S"))
    print(" 이 파이썬 : %d-bit  %s" % (bits, sys.executable))
    print(" 미륵이 본체 기준 경로 : %s" % MIREUK_MAIN)
    print(" 런처 판정식 : 이름에 'python' 포함 AND 명령줄 어딘가에 '%s' 글자 포함" % NEEDLE)
    print("=" * 78)

    rows, unreadable = collect()

    print("\n[1] 지금 돌고 있는 파이썬 프로세스 — 켜진 시각 순 (총 %d개)\n" % len(rows))
    if not rows:
        print("  (없음)")

    guard_hits = []
    for r in rows:
        hit = r["readable"] and (NEEDLE in r["cmd"])
        is_mireuk = MIREUK_MAIN in os.path.normcase(r["cmd"])
        suspect = _in_suspect_window(r["created"])

        mark = []
        if hit and is_mireuk:
            mark.append("본체")
        elif hit:
            mark.append("** 가드가 잡는다(미륵이 아님) **")
        if not r["readable"]:
            mark.append("판독불가(권한)")
        if suspect:
            mark.append("<< 08:35~08:50 기동")

        print("  PID=%-7s 기동=%s  %-14s %s" % (
            r["pid"], _fmt_time(r["created"]), r["name"],
            (" ".join(mark)) if mark else ""))
        print("      cmd : %s" % (r["cmd"] if r["readable"] else "(명령줄을 읽을 수 없음)"))
        if r["cwd"]:
            print("      cwd : %s" % r["cwd"])

        if hit:
            guard_hits.append((r, is_mireuk))

    print("\n" + "-" * 78)
    print("[2] 런처 [GUARD] 가 지금 실행되면 어떻게 되는가")
    print("-" * 78)
    if not guard_hits:
        print("  일치 0개 → '[GUARD] 기존 main.py 없음 -- 단일 인스턴스 확인.' 로 갔을 것이다.")
        print("  ⚠ 런처 로그 11개에서 이 줄은 0번 나왔다. 지금과 아침의 상황이 다르다는 뜻이다.")
    else:
        for r, is_mireuk in guard_hits:
            verdict = "미륵이 본체 (정상 대상)" if is_mireuk else "🔴 미륵이가 아니다 — 종료 대상이 되면 안 된다"
            print("  PID=%-7s %s" % (r["pid"], verdict))
            print("      cmd : %s" % r["cmd"])
        print("")
        print("  → 런처였다면 이 %d개 전부에 p.terminate() 를 호출했을 것이다." % len(guard_hits))
        print("    (런처는 대상 목록을 로그에 남기지 않는다 — 그래서 이 스크립트가 필요하다)")

    print("\n" + "-" * 78)
    print("[3] 32/64비트 사각지대")
    print("-" * 78)
    print("  판독불가(명령줄 접근 거부) : %d개" % len(unreadable))
    if unreadable:
        for r in unreadable:
            print("      PID=%-7s %-14s exe=%s" % (r["pid"], r["name"], r["exe"] or "(불명)"))
        print("")
        print("  ⚠ 런처 코드는 이것을 (cmdline or []) 로 받아 **불일치**로 처리한다.")
        print("    즉 '못 읽었다'가 '아니다'로 조용히 바뀐다 — 진짜 중복 인스턴스를 놓칠 수 있다.")
        print("    (계측 4원칙 ② — 미측정 ≠ 0)")
    else:
        print("  이 파이썬(%d-bit)에서는 전부 읽혔다." % bits)
    print("  → 32비트와 64비트로 각각 한 번씩 돌려 이 숫자를 비교할 것.")

    print("\n" + "-" * 78)
    print("[4] 아침 창(08:35~08:50)에 켜진 파이썬")
    print("-" * 78)
    morning = [r for r in rows if _in_suspect_window(r["created"])]
    if not morning:
        print("  없음. (아침에 종료됐다가 다시 켜진 흔적이 지금은 안 보인다는 뜻이다.")
        print("   → 아침에 잡힌 것은 '죽은 뒤 재기동되지 않은 프로세스'이거나 단명 프로세스다.)")
    else:
        for r in morning:
            print("  PID=%-7s 기동=%s  %s" % (r["pid"], _fmt_time(r["created"]), r["name"]))
            print("      cmd : %s" % (r["cmd"] if r["readable"] else "(판독불가)"))
        print("")
        print("  ⚠ 08:40:37 직후에 켜진 것이 있으면, 런처가 죽인 뒤 그 프로그램의")
        print("    감시 장치가 다시 켠 것일 수 있다 — 그것이 매일 죽어 온 범인이다.")

    print("\n" + "=" * 78)
    print(" 끝. 이 스크립트는 아무것도 종료하지 않았다.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
