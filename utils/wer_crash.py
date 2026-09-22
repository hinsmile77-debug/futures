# -*- coding: utf-8 -*-
"""[MW0601 620차] Windows 응용 프로그램 오류(WER) 기록 <-> 미륵이 프로세스 종료 대사.

무엇을 막는가
-------------
2026-09-22 이상점 1-7 은 「15:08:06 무흔적 종료」였고, 그날 장후 F-3 은 원인 가설
3개를 나열한 채 *"Windows 이벤트 뷰어 확인은 이 세션(리눅스 샌드박스)이 할 수 없다"*
며 사용자 조치로 넘겼다. 그런데 그 기록은 **처음부터 이 PC 에 있었다** — 아무도 안
본 축이었을 뿐이다. 493차 수수료 대사(예탁현금이 매분 오고 있었는데 6개월간 아무도
안 봤다)·FP-CRITICAL 죽은 게이트와 같은 계열이며, 계측 4원칙 ⑤(대사는 모든 축을
걸어라)가 정확히 이 경우를 위해 쓰였다.

무엇을 말할 수 있고 무엇을 말할 수 없나 — ⚠ 이 구분이 이 모듈의 전부다
-----------------------------------------------------------------------
WER `Application Error`(Id=1000) 는 **미처리 네이티브 예외로 죽은 프로세스**만
기록한다. 따라서

  · 이벤트 **있음** + PID 일치 -> 그 종료는 **네이티브 크래시 확정**이다.
                                  faulting module 이 원인 계열까지 준다
                                  (실측: Qt5Core.dll / ucrtbase.dll).
  · 이벤트 **없음**            -> **「미처리 네이티브 예외는 아니었다」까지만** 참이다.
                                  `sys.exit`·창 닫기·`TerminateProcess`(하드킬) 는
                                  전부 이벤트를 남기지 않는다.

🔴 **「이벤트 없음 = 크래시가 아니다」로 읽지 말 것.** 그것은 사전등록된 확인 수단
하나로 확정을 쓰는 것이고(SKILL.md §0 함정① 정합성 게이트 — 2026-09-07 532차 F-1
에서 실제로 발생한 오류다), 618차가 넣은 `[Shutdown] intent=` 로그와 **함께** 봐야
종료 의도까지 갈린다.

세 축을 따로 읽고 한자리에서 맞춘다
-----------------------------------
    런처 로그        "일시적 크래시" / "정상 종료"  <- **분류일 뿐 근거가 아니다**
    crash_fault.log  [START] / [CLEAN EXIT] PID=   <- 프로세스 자신의 종료 기록
    Windows WER      Application Error Id=1000      <- OS 가 본 네이티브 예외

한 축만 보면 나머지가 사각지대가 된다. 2026-09-22 15:08 이 그 실증이다 —
런처는 「일시적 크래시」, crash_fault 는 `[CLEAN EXIT]`, WER 는 **무기록**이었다.

읽기 전용이다. 이벤트 로그를 지우거나 쓰지 않는다.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys

# 미륵이 main.py 가 자기 PID 를 남기는 유일한 줄.
#   2026-09-22 08:40:33 [INFO] SYSTEM: [FaultHandler] 활성화 | ... PID=22668 | ...
_RE_FAULTHANDLER = re.compile(
    r"^(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2}).*?\[FaultHandler\][^|]*\|.*?PID=(\d+)"
)
# [AUTO-RESTART] #1 시도 (시각=1508) -- 10초 후 재시작...
_RE_RESTART_AT = re.compile(r"\[AUTO-RESTART\]\s*#\d+\s*시도\s*\(시각=(\d{4})\)")
# [AUTO-RESTART] main.py 가 326분 실행됨 -- 일시적 크래시, 카운터 초기화.
_RE_RESTART_KIND = re.compile(
    r"\[AUTO-RESTART\]\s*main\.py\s*가\s*(\d+)분\s*실행됨\s*--\s*([^,]+)"
)
# [START] 2026-09-22T15:08:30  PID=28960 ... / [CLEAN EXIT] 2026-09-22T15:47:15  PID=28960
_RE_FAULT_EVT = re.compile(
    r"^\[(START|CLEAN EXIT)\]\s+(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})\s+PID=(\d+)"
)

# Application Error(Id=1000) 의 Properties 배열 — **로캘 독립**이다.
# 메시지 본문("Faulting application name: ...")은 OS 언어에 따라 번역되므로 쓰지 않는다.
#   [0] app name  [3] module name  [6] exception code  [8] process id(hex)  [10] app path
_PS_TEMPLATE = (
    "$ErrorActionPreference='SilentlyContinue';"
    "$e=@(Get-WinEvent -FilterHashtable @{LogName='Application';Id=1000;"
    "StartTime=(Get-Date '%(d)s 00:00:00');EndTime=(Get-Date '%(d)s 23:59:59')});"
    "'###OK###';"
    "foreach($x in $e){$p=$x.Properties;"
    "if($p.Count -ge 11){"
    "'{0}|{1}|{2}|{3}|{4}|{5}' -f $x.TimeCreated.ToString('HH:mm:ss'),"
    "$p[0].Value,$p[3].Value,$p[6].Value,$p[8].Value,$p[10].Value}}"
)


def _unmeasured(reason):
    """미측정을 0 건과 구분해 돌려준다 — 계측 4원칙 ②."""
    return {"measured": False, "reason": reason, "events": []}


def wer_app_faults(day_txt, timeout=90, _runner=None):
    """그날 **모든** 응용 프로그램의 네이티브 크래시(WER Id=1000) 목록.

    ⚠ `python.exe` 로 좁히지 않는다 — **일부러**다. 2026-09-17 실측에서 대신 데이터
    서버 `DIBSERVER.EXE` 가 `c0000005`(액세스 위반)로 세 번 죽은 것이 잡혔는데,
    이것은 미륵이 프로세스가 아니면서 미륵이 시세 공급에 직접 영향을 준다.
    python 으로 걸러냈다면 그 축이 통째로 사라졌을 것이다(계측 4원칙 ⑤).
    귀속은 호출부가 `reconcile()` 의 `rows`(미륵이) / `others`(그 외)로 가른다.

    반환: {"measured": bool, "reason": str, "events": [...]}
      events[i] = {"time","app","module","code","pid","path"}  (pid 는 10진 int)

    ⚠ `measured=False` 는 **「크래시 0건」이 아니라 「재지 못했다」**다.
      비Windows·PowerShell 부재·이벤트 로그 권한 부족이 전부 여기로 온다.

    `_runner` 는 테스트 주입용이다(문자열을 돌려주는 콜러블). 실제 PowerShell 을
    부르지 않고 파서만 검증할 수 있게 열어 둔다.
    """
    if _runner is None:
        if not sys.platform.startswith("win"):
            return _unmeasured("비Windows 플랫폼 — WER 이벤트 로그가 없다")
        script = _PS_TEMPLATE % {"d": day_txt}
        p = None
        try:
            p = subprocess.Popen(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
            out, _err = p.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            try:
                p.kill()
                p.communicate(timeout=5)
            except Exception:
                pass
            return _unmeasured("PowerShell 타임아웃 %ss — 자식 종료함" % timeout)
        except Exception as e:
            if p is not None and p.poll() is None:
                try:
                    p.kill()
                except Exception:
                    pass
            return _unmeasured("PowerShell 실행 불가: %s" % e)
        if p.returncode != 0:
            return _unmeasured(
                "PowerShell rc=%s %s" % (p.returncode, out.decode("utf-8", "replace")[:200])
            )
        raw = out.decode("utf-8", "replace")
    else:
        raw = _runner(day_txt)

    # '###OK###' 가 없으면 조회 자체가 안 돈 것이다 — 빈 출력과 구분한다(계측 4원칙 ④).
    if "###OK###" not in raw:
        return _unmeasured("WER 조회가 완료 표식을 남기지 않았다 (권한·정책 확인 필요)")

    events = []
    for line in raw.split("###OK###", 1)[1].splitlines():
        line = line.strip()
        if not line or line.count("|") < 5:
            continue
        t, app, mod, code, pid_hex, path = line.split("|", 5)
        try:
            pid = int(pid_hex.strip(), 16)
        except ValueError:
            pid = None
        events.append({
            "time": t.strip(), "app": app.strip(), "module": mod.strip(),
            "code": code.strip(), "pid": pid, "path": path.strip(),
        })
    events.sort(key=lambda e: e["time"])
    return {"measured": True, "reason": "", "events": events}


def launcher_processes(root, ymd):
    """런처 로그에서 그날 미륵이 `main.py` 프로세스의 기동 PID 와 재시작 분류를 뽑는다.

    반환: {"measured","reason","starts":[{"time","pid"}],"restarts":[{"at","kind"}],"files":[...]}
    """
    d = os.path.join(root, "logs", "Mireuk_batch")
    if not os.path.isdir(d):
        return {"measured": False, "reason": "logs/Mireuk_batch 없음",
                "starts": [], "restarts": [], "files": []}
    files = sorted(f for f in os.listdir(d)
                   if f.startswith("launcher_%s" % ymd) and f.endswith(".log"))
    if not files:
        return {"measured": False,
                "reason": "그날 런처 로그 없음 — 런처를 안 썼거나 파일명 규칙이 바뀌었다",
                "starts": [], "restarts": [], "files": []}

    starts, restarts = [], []
    pend_kind = None
    for fn in files:
        try:
            fh = open(os.path.join(d, fn), "r", encoding="utf-8", errors="replace")
        except Exception:
            continue
        with fh:
            for line in fh:
                m = _RE_FAULTHANDLER.search(line)
                if m:
                    starts.append({"time": m.group(2), "pid": int(m.group(3))})
                    continue
                m = _RE_RESTART_KIND.search(line)
                if m:
                    # 분류는 이 줄, 시각은 다음 '#N 시도' 줄에 있다.
                    pend_kind = m.group(2).strip()
                    continue
                m = _RE_RESTART_AT.search(line)
                if m:
                    hhmm = m.group(1)
                    restarts.append({"at": "%s:%s" % (hhmm[:2], hhmm[2:]),
                                     "kind": pend_kind or "(분류줄 없음)"})
                    pend_kind = None
    starts.sort(key=lambda s: s["time"])
    return {"measured": True, "reason": "", "starts": starts,
            "restarts": restarts, "files": files}


def crash_fault_events(root, day_txt):
    """`logs/crash_fault.log` 의 그날 `[START]` / `[CLEAN EXIT]` 를 PID 별로 모은다.

    🔴 `covered` 를 함께 돌려준다 — **「그날 행이 하나도 없다」와 「정상 종료가 없었다」는
    다르다.** `crash_fault.log` 는 롤링 파일이라 며칠 지나면 그 날짜 구간이 통째로
    사라진다(실측 2026-09-17 은 행 0개). 이 둘을 같은 값으로 두면 과거 날짜를 재생할
    때마다 **전 프로세스가 「하드킬」로 오판**된다 — 계측 4원칙 ②.
    """
    p = os.path.join(root, "logs", "crash_fault.log")
    if not os.path.exists(p):
        return {"measured": False, "reason": "logs/crash_fault.log 없음",
                "by_pid": {}, "covered": False}
    by_pid = {}
    try:
        fh = open(p, "r", encoding="utf-8", errors="replace")
    except Exception as e:
        return {"measured": False, "reason": "crash_fault.log 열기 실패: %s" % e,
                "by_pid": {}, "covered": False}
    with fh:
        for line in fh:
            m = _RE_FAULT_EVT.match(line.strip())
            if not m or m.group(2) != day_txt:
                continue
            kind, tm, pid = m.group(1), m.group(3), int(m.group(4))
            rec = by_pid.setdefault(pid, {"start": None, "clean_exit": None})
            if kind == "START":
                rec["start"] = tm
            else:
                rec["clean_exit"] = tm
    return {"measured": True, "reason": "", "by_pid": by_pid,
            "covered": bool(by_pid)}


def reconcile(launcher, wer, fault):
    """세 축을 PID 로 맞춘다.

    반환 rows[i] = {"pid","started","clean_exit","wer","verdict"}
      · wer 가 dict -> 그 종료는 네이티브 크래시 **확정**
      · wer 가 None  -> 「미처리 네이티브 예외는 아니다」까지만 (위 모듈 설명 참조)

    `others` 는 그날 크래시했지만 미륵이 `main.py` PID 가 아닌 python 프로세스다.
    형제 프로젝트·점검 스크립트·대시보드가 섞여 들어오므로 **미륵이 사고로 세지 말 것.**
    """
    wer_by_pid = {}
    if wer.get("measured"):
        for e in wer["events"]:
            if e["pid"] is not None:
                wer_by_pid.setdefault(e["pid"], e)

    # 그날 구간이 롤링으로 잘려나간 로그를 "종료 기록 없음"으로 읽으면 안 된다.
    fault_covered = fault.get("measured") and fault.get("covered", bool(fault.get("by_pid")))

    rows = []
    mireuk_pids = set()
    for s in launcher.get("starts", []):
        pid = s["pid"]
        mireuk_pids.add(pid)
        fr = fault.get("by_pid", {}).get(pid, {})
        ev = wer_by_pid.get(pid)
        if not wer.get("measured"):
            verdict = "판정불가 — WER **미측정**"
        elif ev is not None:
            verdict = "**네이티브 크래시 확정** (%s / %s)" % (ev["module"], ev["code"])
        elif fr.get("clean_exit"):
            verdict = "네이티브 예외 아님 + 프로세스가 **정상 종료 기록을 남김**"
        elif not fault_covered:
            # 축이 하나 비었다 — 단정하지 않는다(계측 4원칙 ②).
            verdict = ("네이티브 예외 아님 + 정상종료 축 **미측정**"
                       "(`crash_fault.log` 에 그날 행이 없다 — 롤링으로 잘렸을 수 있다)")
        else:
            verdict = "네이티브 예외 아님 + 정상 종료 기록도 **없음** — 하드킬/무흔적"
        rows.append({
            "pid": pid, "started": s["time"],
            "clean_exit": fr.get("clean_exit"),
            "wer": ev, "verdict": verdict,
        })

    others = []
    if wer.get("measured"):
        others = [e for e in wer["events"] if e["pid"] not in mireuk_pids]
    return {"rows": rows, "others": others, "mireuk_pids": sorted(mireuk_pids)}
