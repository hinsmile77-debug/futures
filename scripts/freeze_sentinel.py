# -*- coding: utf-8 -*-
"""[MW0601 490차 / F-M] 프로세스 밖 동결 센티넬 (FZ-2) — **알림 전용**.

## 왜 프로세스 밖인가

FZ-1 워치독(478차 후속)은 라이브 프로세스 **안의 파이썬 스레드**다. 그래서 GIL을
쥔 채 반환하지 않는 동결에서는 감시자 자신이 함께 멈춘다 — 검사도 발화도 못 한다.

2026-08-24 15:40:20 실측(이상점 1-12·1-14):
  마감 스레드가 `_on_gbm_retrain_done()` → `self.dashboard.set_model_status(...)` 로
  워커 스레드에서 Qt 위젯을 만져 데드락에 빠졌다. 그 순간부터
  `logs/crash_fault.log` 의 30초 `[TS]` 하트비트가 **15:40:03 에서 함께 끊겼다** —
  FZ-1이 살아 있었다면 그 줄은 계속 찍혔어야 한다. 프로세스는 살아 있었으므로
  런처 RESTART_LOOP(프로세스 종료가 트리거)도 재기동하지 않았고, 마감 절차 12종이
  미실행으로 끝났으며 EOD 재학습은 20분을 헛기다렸다.

임계(`FREEZE_WATCHDOG_STALL_SEC`)를 조정해서 풀리는 문제가 아니다. **감시 위치의
문제**다. 그래서 이 센티넬은 별개 프로세스로 돈다.

🔴 **FZ-1을 제거하지 않는다.** FZ-1은 「메인 루프가 느려지는 동결」에는 여전히
   유효하고, 하드 종료 → 런처 재기동 → 세션 복원 왕복을 할 수 있는 유일한 장치다.
   이것은 교체가 아니라 **2층 추가**다.

## 무엇을 하고, 무엇을 하지 않는가

한다:  3신호(하트비트 · `[TS]` · SYSTEM.log)의 나이를 재고, 셋 다 정체면 경보를
       로그 · 마커 파일 · (옵션)메시지박스로 남긴다.

하지 않는다: **하드 종료.** `FREEZE_SENTINEL_KILL_ENABLED` 는 자리만 있고 구현이
       없다. F-2 가드가 「알림 전용 — 주문 없음」으로 시작한 것과 같은 이유이며,
       승격은 주간회의 안건이다 — 감시자가 새 사고를 만드는 것이 여기서 가장
       피해야 할 결과다. 특히 하드 종료는 15:10 이후에는 런처 재기동을 유발하지
       않으므로(오버나이트 금지 정책) 이득 없이 마감 절차만 더 확실히 죽인다.

## 왜 3신호를 함께 보는가

단일 신호는 전부 오탐원이 있다:
  · 하트비트 파일  — `FREEZE_WATCHDOG_HEARTBEAT_FILE=False` 면 아예 없다
  · `[TS]`         — `FREEZE_WATCHDOG_TS_HEARTBEAT=False` 면 안 찍힌다
  · SYSTEM.log     — 조용한 구간(점심 무신호)에는 정상적으로 뜸해질 수 있다
셋 다 낡아야 동결로 본다. 그리고 **「없음」은 「낡음」이 아니다** — 하나라도
미측정이면 `UNKNOWN` 으로 남긴다(계측 4원칙 ②). 기동 전·비거래일을 동결로
오인하지 않기 위해서다.

## 왜 DB를 읽지 않는가

감시 창이 장중을 포함한다(CLAUDE.md 「장중 라이브 DB 분석 금지」 08:45~15:35).
2026-08-10에 점검 세션의 DB 전수 스캔이 파이프라인을 7,619ms로 늘려 CB⑤를
자가유발한 전례가 있다. 이 센티넬은 **작은 파일 3개의 mtime/끝줄만** 본다.

## 사용법

    python scripts/freeze_sentinel.py             # 감시 창 동안 주기 감시
    python scripts/freeze_sentinel.py --once      # 즉시 1회 판정(점검·리허설용)
    python scripts/freeze_sentinel.py --once --at-time "2026-08-24 15:45:00"
        # 과거 로그를 그대로 재생 입력으로 쓴다 — 2026-08-24 crash_fault.log 87덤프

런처가 사이드카로 띄운다. 종료코드:

    0  정상(살아 있음)     3  🔴 동결 감지
    5  판정 불가(입력 결손) 6  비거래일·설정 비활성·감시창 밖

근거: `docs/정기점검/매일점검/MW0601-20260824-점검리포트.md` §2 F-M (이상점 1-14),
      CLAUDE.md 실전 전환 기준 ② ⓑ.
"""
from __future__ import print_function

import argparse
import datetime
import io
import json
import os
import subprocess
import sys
import time

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

RC_OK = 0
RC_FROZEN = 3
RC_UNKNOWN = 5
RC_NOT_APPLICABLE = 6

#: 3신호 이름 — 판정문·로그가 같은 문자열을 쓴다.
SIG_HEARTBEAT = "heartbeat"
SIG_TS = "crash_fault[TS]"
SIG_SYSLOG = "SYSTEM.log"


# ── 판정 (순수 함수 — 테스트가 여기를 고정한다) ────────────────────────────

def judge(ages, stall_sec=300.0, exit_flag_age=None, close_done_age=None):
    """3신호의 나이(초)로 동결을 판정한다. 파일 IO 없이 값만 본다.

    Args:
        ages: {신호이름: 나이초 또는 None}. **None = 미측정**(파일 없음/파싱 실패).
              0.0(방금 갱신)과 다른 사실이므로 절대 같은 값으로 뭉개지 않는다
              (계측 4원칙 ②).
        stall_sec: 이보다 낡으면 그 신호는 「정체」.
        exit_flag_age: [MW0601 493차 후속5 / F-Z] `data/_exit_normally` 의 **나이(초)**.
              None = 플래그 없음 또는 읽기 실패(**미측정**).
        close_done_age: [MW0601 498차 / F-10] `data/daily_close_done_<date>.txt` 의
              **나이(초)**. None = 마커 없음(**미측정**).

    Returns:
        dict(level, rc, headline, details[], stale[], unmeasured[], state)

    판정:
      ① 측정된 신호가 하나도 없다            → UNKNOWN (조용히 OK로 넘기지 않는다)
      ② 측정된 신호가 **전부** 정체
         · 정상 종료 플래그가 신호보다 **뒤**  → NOT_APPLICABLE (state=EXITED)
         · 마감 완료 마커가 신호보다 **뒤**    → INFO           (state=NORMAL_CLOSE)
         · 그 외                              → CRITICAL       (state=FROZEN)
      ③ 그 외(하나라도 신선)                  → OK             (state=WATCHING)
    ⚠ ②의 분모는 **측정된 신호**다. 미측정을 정체로 세면 기동 전 시각에 오탐이 나고,
      신선으로 세면 진짜 동결을 놓친다 — 어느 쪽으로도 뭉개지 않고 분모에서 뺀다.

    ── [MW0601 493차 후속5 / F-Z] 「정상 종료」와 「동결」을 가른다 ──────────────

    종전에는 둘이 **같은 CRITICAL 문자열**이었다. 그래서 매일 정상 마감 뒤
    15:45~16:30 에 **43회**의 가짜 동결 경보가 떴고 팝업까지 한 번 떴다.
    이런 것이 쌓이면 **진짜 얼어붙은 날에도 무시하게 된다** — 2026-08-19 에
    실제로 동결이 나 15:10 강제청산이 통째로 지나갔고, 그때 포지션이 없었던 것은
    운이었다.

    🔴 **그 08-19 형을 놓치면 안 된다.** 그날 프로세스는 **살아 있었고**
    `_exit_normally` 는 **쓰이지 않았다**(정상 종료가 아니었으니까). 그래서
    "플래그가 신호보다 뒤" 조건은 그 시나리오에서 성립하지 않는다 — 여전히
    CRITICAL 이 나온다. 아래 두 가지가 그 안전 여백이다:
      · **플래그 존재만으로 판정하지 않는다.** 어제 것이 남아 있을 수 있으므로
        **시각을 비교**한다(플래그가 가장 오래된 정체 신호보다 뒤여야 한다).
      · **미측정이면 종전대로 CRITICAL.** 감시자가 조용해지는 것이 오탐보다 나쁘다.

    ── [MW0601 498차 / F-10] 마감 완료 마커를 **두 번째 독립 증거**로 쓴다 ────────

    위 F-Z 는 `_exit_normally` 하나에 걸려 있었다. 그런데 그 플래그는 **프로세스가
    실제로 종료할 때** 런처가 쓰는 것이라, 마감은 정상 종료했는데 프로세스가 아직
    떠 있는 구간(15:40~자동종료)에서는 **없다**. 2026-08-26 이 그 상태였다 —
    `daily_close_done` 이 15:40:23 에 찍혔고 로그 종료시각도 5거래일 중앙값과
    델타 +0분인데, 15:45 부터 **33분 연속 CRITICAL** 이 나갔다(이상점 1-11).

    그래서 `data/daily_close_done_<date>.txt` 를 **정상 마감의 독립 증거**로 더한다.
    이 마커는 마감 절차의 거의 마지막에 한 경로로만 찍히므로 오탐 여지가 없다.
    「없던 데이터가 아니라 아무도 안 본 데이터」(계측 4원칙 ⑤)의 또 다른 사례다.

    🔴 **안전 여백 — 무디게 만들지 않는다.** 세 가지로 08-19 형을 지킨다:
      · `_exit_normally` 와 **같은 시각 비교 규칙**을 쓴다(마커가 가장 오래된 정체
        신호보다 뒤여야 한다). 08-19 는 13:41 동결이라 마커 자체가 없다 → CRITICAL.
      · 마커가 **미측정이면 종전대로 CRITICAL.** 존재만으로 판정하지 않는다.
      · 결과는 `EXITED` 처럼 감시 종료가 아니라 **INFO 강등 + 감시 계속**이다.
        마감 뒤 진짜 동결도 관측은 계속되며, 다만 최고 등급 경보·팝업·마커를
        내지 않는다. 「조용해지는 것」과 「등급을 낮추는 것」은 다르다.
    """
    stale, fresh, unmeasured, details = [], [], [], []
    for name in (SIG_HEARTBEAT, SIG_TS, SIG_SYSLOG):
        age = ages.get(name)
        if age is None:
            unmeasured.append(name)
            details.append("%-16s **미측정** (파일 없음 또는 파싱 실패)" % name)
            continue
        if age >= stall_sec:
            stale.append(name)
            details.append("%-16s %.0fs 전 (임계 %.0fs) — 정체" % (name, age, stall_sec))
        else:
            fresh.append(name)
            details.append("%-16s %.0fs 전 — 신선" % (name, age))

    if not stale and not fresh:
        return {"level": "UNKNOWN", "rc": RC_UNKNOWN, "state": "UNKNOWN",
                "headline": "판정에 필요한 3신호가 모두 없다 — 센티넬이 돌았지만 "
                            "아무것도 보장하지 못했다",
                "details": details, "stale": stale, "unmeasured": unmeasured}

    if not fresh:
        # [F-Z] 정상 종료였는가 — **플래그가 가장 오래된 정체 신호보다 뒤**여야 한다.
        # `exit_flag_age`(초)가 정체 신호들의 최소 나이보다 **작다** = 플래그가 더
        # 최근이다. 어제 남은 플래그는 나이가 훨씬 크므로 여기서 걸러진다.
        _min_stale_age = min(ages[n] for n in stale)
        if exit_flag_age is not None and exit_flag_age < _min_stale_age:
            details.append(
                "%-16s %.0fs 전 — 정상 종료 플래그(가장 오래된 정체 신호 %.0fs 보다 뒤)"
                % ("_exit_normally", exit_flag_age, _min_stale_age))
            return {"level": "NOT_APPLICABLE", "rc": RC_NOT_APPLICABLE,
                    "state": "EXITED",
                    "headline": "정상 종료 확인 — 감시 종료 (동결이 아니다)",
                    "details": details, "stale": stale, "unmeasured": unmeasured}
        # [MW0601 498차 / F-10] 두 번째 독립 증거 — 마감 완료 마커.
        # `_exit_normally` 와 **같은 시각 비교 규칙**이다(존재만으로 판정하지 않는다).
        if close_done_age is not None and close_done_age < _min_stale_age:
            details.append(
                "%-16s %.0fs 전 — 일일 마감 완료 마커(가장 오래된 정체 신호 %.0fs 보다 뒤)"
                % ("daily_close_done", close_done_age, _min_stale_age))
            return {"level": "INFO", "rc": RC_NOT_APPLICABLE, "state": "NORMAL_CLOSE",
                    "headline": "정상 마감 후 정지 — 동결이 아니다 (감시는 계속하되 "
                                "경보 등급을 낮춘다)",
                    "details": details, "stale": stale, "unmeasured": unmeasured}

        if exit_flag_age is None:
            # ⚠ **미측정을 정상 종료로 읽지 않는다.** 08-19 형 동결이 정확히 이 상태다
            #   (프로세스는 살아 있고 플래그는 안 쓰였다).
            details.append("%-16s **미측정**(플래그 없음/읽기 실패) — 동결 판정 유지"
                           % "_exit_normally")
        else:
            details.append(
                "%-16s %.0fs 전 — 정체 신호(%.0fs)보다 **오래됐다**(이전 세션 잔재)"
                % ("_exit_normally", exit_flag_age, _min_stale_age))
        # [498차 F-10] 마감 마커 축도 **어느 쪽이든 한 줄 남긴다** — 미측정을
        # 침묵으로 처리하면 "왜 CRITICAL 인가"가 판정문에서 사라진다(계측 4원칙 ②·③).
        if close_done_age is None:
            details.append("%-16s **미측정**(마커 없음) — 동결 판정 유지"
                           % "daily_close_done")
        else:
            details.append(
                "%-16s %.0fs 전 — 정체 신호(%.0fs)보다 **먼저**다(마감 뒤 정지가 아니다)"
                % ("daily_close_done", close_done_age, _min_stale_age))
        return {"level": "CRITICAL", "rc": RC_FROZEN, "state": "FROZEN",
                "headline": "라이브 프로세스 동결 — 측정 가능한 신호 %d종이 전부 %.0fs 이상 "
                            "정체다. 프로세스는 살아 있을 수 있으나 아무 일도 하지 않는다 "
                            "(런처 재기동도 걸리지 않는다)" % (len(stale), stall_sec),
                "details": details, "stale": stale, "unmeasured": unmeasured}

    return {"level": "OK", "rc": RC_OK, "state": "WATCHING",
            "headline": "정상 — 신선한 신호 %d종 (%s)" % (len(fresh), ", ".join(fresh)),
            "details": details, "stale": stale, "unmeasured": unmeasured}


# ── 입력 수집 ──────────────────────────────────────────────────────────────

def _pc_id():
    try:
        from utils.db_utils import pc_id
        return pc_id()
    except Exception:
        import platform
        import re
        host = platform.node() or ""
        m = re.search(r"(MW\d{4})", host, re.IGNORECASE)
        return m.group(1).upper() if m else (host[:32] or "UNKNOWN")


def heartbeat_age(root, now, day, pc=None):
    """하트비트 JSON의 `written_at` 나이. 파일이 없거나 파싱 불가면 None."""
    try:
        from config.settings import FREEZE_WATCHDOG_HEARTBEAT_PATH as tpl
    except Exception:
        tpl = "data/heartbeat_{pc}_{date}.json"
    path = os.path.join(root, tpl.format(pc=pc or _pc_id(), date=day.strftime("%Y%m%d")))
    try:
        with io.open(path, "r", encoding="utf-8") as f:
            hb = json.load(f)
    except Exception:
        return None
    try:
        written = datetime.datetime.strptime(str(hb.get("written_at"))[:19],
                                             "%Y-%m-%dT%H:%M:%S")
    except (ValueError, TypeError):
        return None
    return max(0.0, (now - written).total_seconds())


_TS_PREFIX = "[TS]"


def ts_age(root, now, tail_bytes=65536, max_scan_bytes=16 * 1024 * 1024):
    """`logs/crash_fault.log` 최신 `[TS]` 줄의 나이.

    ⚠ 파일 mtime 이 아니라 **줄 안의 시각**을 읽는다. mtime 은 다른 기록(fault 덤프)
      으로도 갱신되므로 「FZ-1 스레드가 아직 도는가」를 못 재는데, 그것이 이 신호가
      재려는 바로 그 사실이다(2026-08-24 실측: 덤프는 계속 쌓였고 `[TS]` 만 끊겼다).

    ⚠ **꼬리를 고정 크기로 읽으면 안 된다.** 동결 뒤에는 `FaultHandler` 덤프가
      쏟아져 마지막 `[TS]` 를 파일 뒤쪽으로 밀어낸다 — 2026-08-24 실측: 5.1MB 파일에서
      마지막 `[TS]` 가 끝에서 **6,709줄(약 450KB) 앞**이었고, 64KB 꼬리로는 못 찾아
      「미측정」이 나온다. 하필 진짜 동결일에만 못 찾는 형태라, 초판이 그대로 있었으면
      이 센티넬은 자기가 잡으려던 사건에서만 눈이 멀었을 것이다.
      → 찾을 때까지 꼬리를 2배씩 넓힌다(상한 `max_scan_bytes`).
    """
    path = os.path.join(root, "logs", "crash_fault.log")
    try:
        size = os.path.getsize(path)
    except Exception:
        return None
    stamp = None
    span = int(tail_bytes)
    while stamp is None:
        try:
            with io.open(path, "rb") as f:
                if size > span:
                    f.seek(size - span)
                blob = f.read().decode("utf-8", "replace")
        except Exception:
            return None
        for line in blob.splitlines():
            if _TS_PREFIX in line:
                stamp = line
        if stamp is not None or span >= size or span >= max_scan_bytes:
            break
        span = min(span * 2, size, max_scan_bytes)
    if stamp is None:
        return None
    # 형식 예: `[TS] 2026-08-24 15:40:03`
    body = stamp.split(_TS_PREFIX, 1)[1].strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return max(0.0, (now - datetime.datetime.strptime(body[:19], fmt)).total_seconds())
        except ValueError:
            continue
    return None


def syslog_age(root, now, day):
    """`logs/{date}_SYSTEM.log` 최종 기록 나이(mtime 기준). 없으면 None.

    ⚠ `time.time()` 이 아니라 인자로 받은 `now` 를 기준으로 잰다 — `--at-time` 재생이
      성립하려면 세 신호가 **같은 기준 시각**을 써야 한다. 초판이 여기만 벽시계를
      써서, 과거 로그를 재생하면 이 신호만 항상 「정체」로 나왔다.
    """
    path = os.path.join(root, "logs", "%s_SYSTEM.log" % day.strftime("%Y%m%d"))
    try:
        if not os.path.exists(path):
            return None
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(path))
        return max(0.0, (now - mtime).total_seconds())
    except Exception:
        return None


def exit_flag_age(root, now):
    """[MW0601 493차 후속5 / F-Z] `data/_exit_normally` 의 나이(초).

    없거나 읽기 실패면 **None(미측정)** — 0 이나 큰 수로 위장하지 않는다.
    미측정은 `judge()` 에서 **동결 판정 유지**로 처리된다(감시자가 조용해지는 것이
    오탐보다 나쁘다).

    ⚠ 파일 mtime 을 쓴다. 안의 ISO 시각을 파싱할 수도 있지만, 그 형식이 바뀌면
      파싱 실패 → 미측정 → 가짜 CRITICAL 로 되돌아간다. mtime 은 런처가 파일을
      지우기 전까지 그 세션의 종료 시각을 그대로 들고 있어 더 견고하다.
    ⚠ **플래그의 존재만으로 판정하지 않는다** — 나이를 돌려주는 이유가 그것이다.
      런처가 읽은 뒤 지우므로 보통은 없지만, 남아 있으면 어제 것일 수 있다.
    """
    path = os.path.join(root, "data", "_exit_normally")
    try:
        mtime = os.path.getmtime(path)
    except Exception:
        return None
    try:
        return max(0.0, (now - datetime.datetime.fromtimestamp(mtime)).total_seconds())
    except Exception:
        return None


def close_done_age(root, now, day):
    """[MW0601 498차 / F-10] `data/daily_close_done_<date>.txt` 의 나이(초).

    없거나 읽기 실패면 **None(미측정)** — `exit_flag_age()` 와 같은 규약이다.
    미측정은 `judge()` 에서 **동결 판정 유지**로 처리된다.

    ⚠ 파일 mtime 을 쓴다(내용이 아니라). `_exit_normally` 와 같은 이유 —
      내용 형식이 바뀌면 파싱 실패 → 미측정 → 가짜 CRITICAL 로 되돌아간다.
    ⚠ 날짜가 파일명에 박혀 있으므로 어제 마커가 오늘 판정에 끼어들지 않는다.
      그래도 `judge()` 는 **시각을 비교**한다 — 이중 안전장치다.
    """
    path = os.path.join(root, "data",
                        "daily_close_done_%s.txt" % day.strftime("%Y%m%d"))
    try:
        mtime = os.path.getmtime(path)
    except Exception:
        return None
    try:
        return max(0.0, (now - datetime.datetime.fromtimestamp(mtime)).total_seconds())
    except Exception:
        return None


def collect(root, now, day):
    return {
        SIG_HEARTBEAT: heartbeat_age(root, now, day),
        SIG_TS:        ts_age(root, now),
        SIG_SYSLOG:    syslog_age(root, now, day),
    }


# ── 출력 ──────────────────────────────────────────────────────────────────

def log_line(root, day, text):
    """센티넬 전용 로그 — 실패해도 센티넬을 멈추지 않는다.

    `encoding="utf-8"` 명시 이유는 FZ-1·F-2와 같다: py37_32 기본 인코딩이 cp949라
    em dash(—) 하나에 `UnicodeEncodeError` 가 나고, 예외를 삼키면 기록이 통째로
    사라진다(478차 후속 §8-2 실측).
    """
    try:
        _dir = os.path.join(root, "logs")
        if not os.path.isdir(_dir):
            os.makedirs(_dir)
        with io.open(os.path.join(_dir, "freeze_sentinel_%s.log" % day.strftime("%Y%m%d")),
                     "a", encoding="utf-8", errors="replace") as f:
            f.write(text + chr(10))
        return True
    except Exception as exc:
        print("[FreezeSentinel] 로그 기록 실패: %s" % exc, file=sys.stderr)
        return False


def log_armed(root, day, window, stall, check):
    """감시 개시를 파일에 남긴다 — **센티넬 자신의 생존 증거**.

    F-2 가드의 `log_armed()` 와 같은 취지다. 이 콘솔은 아무도 보지 않으므로,
    기동 줄이 없으면 센티넬이 조용히 죽어도 그 사실이 어디에도 남지 않는다 —
    감시자가 스스로 「조용한 부재」에 빠지는 것이 가장 나쁘다.
    """
    return log_line(root, day, (
        "[FreezeSentinel] %s ARMED pid=%s 창=%s~%s 정지임계=%.0fs 주기=%.0fs "
        "(알림 전용 — 하드 종료 없음)"
        % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), os.getpid(),
           window[0], window[1], stall, check)
    ))


def emit(root, day, verdict, popup=True, manual=False):
    """경보를 남긴다 — 로그 · (경보 시)마커 파일 · (옵션)메시지박스.

    Slack은 쓰지 않는다(사용자 결정: 개발단계 직접 모니터링).
    ⚠ `manual=True`(`--once` 수동 실행)면 **마커를 남기지 않는다.** 점검 중에 손으로
    돌린 진단이 다음날 증거 인벤토리에 「경보」로 섞이면 진짜 발화와 구분되지 않는다
    (F-2 가드가 개발 중 실제로 그렇게 오염시킨 전례).
    """
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    body = ["[FreezeSentinel] %s %s%s" % (stamp, verdict["level"],
                                          " (수동 실행 — 마커 미기록)" if manual else ""),
            "  " + verdict["headline"]]
    body += ["  · " + d for d in verdict["details"]]
    text = chr(10).join(body)

    log_line(root, day, text)
    print(text)

    if not manual and verdict["level"] in ("CRITICAL", "UNKNOWN"):
        try:
            data_dir = os.path.join(root, "data")
            if not os.path.isdir(data_dir):
                os.makedirs(data_dir)
            with io.open(os.path.join(data_dir, "freeze_sentinel_alert_%s.txt"
                                      % day.strftime("%Y%m%d")),
                         "a", encoding="utf-8", errors="replace") as f:
                f.write(text + chr(10))
        except Exception as exc:
            print("[FreezeSentinel] 마커 기록 실패: %s" % exc, file=sys.stderr)

    if popup and verdict["level"] == "CRITICAL":
        _popup(verdict)


def _popup(verdict):
    """트레이딩 PC 앞 사람에게 즉시 보이게 한다 — 이 시각에는 사람이 개입할 수 있다."""
    msg = (verdict["headline"] + chr(10) + chr(10) + chr(10).join(verdict["details"]))
    msg = msg.replace("'", "").replace('"', "")
    ps = (
        "Add-Type -AssemblyName PresentationFramework; "
        "[System.Windows.MessageBox]::Show('%s', "
        "'[Mireuk] 동결 센티넬 FZ-2', 'OK', 'Error')" % msg
    )
    try:
        subprocess.Popen(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
    except Exception as exc:
        print("[FreezeSentinel] 팝업 실패(무해): %s" % exc, file=sys.stderr)


# ── 진입점 ────────────────────────────────────────────────────────────────

def _cfg(name, default):
    try:
        import config.settings as st
        return getattr(st, name, default)
    except Exception:
        return default


def _in_window(now, window):
    try:
        h0, m0 = [int(x) for x in str(window[0]).split(":")]
        h1, m1 = [int(x) for x in str(window[1]).split(":")]
    except Exception:
        return True
    t = now.time()
    return datetime.time(h0, m0) <= t <= datetime.time(h1, m1)


def main(argv=None):
    ap = argparse.ArgumentParser(description="프로세스 밖 동결 센티넬 FZ-2 (F-M, 알림 전용)")
    ap.add_argument("--once", action="store_true", help="주기 감시 없이 즉시 1회 판정")
    ap.add_argument("--stall-sec", type=float, default=None, help="정체 판정 임계초")
    ap.add_argument("--check-sec", type=float, default=None, help="감시 주기 초")
    ap.add_argument("--at-time", default=None,
                    help="판정 기준 시각 'YYYY-MM-DD HH:MM:SS' — 과거 로그 재생용")
    ap.add_argument("--no-popup", action="store_true", help="메시지박스 억제")
    ap.add_argument("--root", default=_ROOT)
    args = ap.parse_args(argv)

    # cp949 콘솔이 em dash 를 못 쓴다 — 경보 문구가 인코딩 때문에 사라지면
    # 이 센티넬은 아무것도 한 게 없다(478차 후속 §8-2와 같은 이유).
    try:
        from utils.analysis_db import utf8_console
        utf8_console()
    except Exception:
        for _stream in ("stdout", "stderr"):
            try:
                getattr(sys, _stream).reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass

    root = os.path.abspath(args.root)
    stall = args.stall_sec if args.stall_sec is not None else _cfg("FREEZE_SENTINEL_STALL_SEC", 300.0)
    check = args.check_sec if args.check_sec is not None else _cfg("FREEZE_SENTINEL_CHECK_SEC", 60.0)
    window = _cfg("FREEZE_SENTINEL_WINDOW", ("09:00", "16:30"))
    popup = (not args.no_popup) and bool(_cfg("FREEZE_SENTINEL_POPUP", True))

    if not _cfg("FREEZE_SENTINEL_ENABLED", True):
        print("[FreezeSentinel] 설정 비활성(FREEZE_SENTINEL_ENABLED=False) — 종료")
        return RC_NOT_APPLICABLE

    # 🔴 하드 종료 승격은 주간회의 안건이다. 플래그가 켜져 있어도 여기서 멈춘다 —
    #    구현 없이 켠 플래그가 조용히 "동작한다"고 읽히는 것을 막는다.
    if _cfg("FREEZE_SENTINEL_KILL_ENABLED", False):
        print("[FreezeSentinel] ⚠ FREEZE_SENTINEL_KILL_ENABLED=True 인데 **하드 종료는 "
              "미구현**이다. 알림 전용으로 계속 진행한다 (승격은 주간회의 안건).",
              file=sys.stderr)

    now = datetime.datetime.now()
    if args.at_time:
        now = datetime.datetime.strptime(args.at_time[:19], "%Y-%m-%d %H:%M:%S")

    try:
        from utils.time_utils import is_trading_day
        trading = is_trading_day(now)
    except Exception:
        trading = now.weekday() < 5
    if not trading:
        print("[FreezeSentinel] 비거래일 — 감시 대상 아님")
        return RC_NOT_APPLICABLE

    if args.once or args.at_time:
        # [MW0601 498차 / F-10] ⚠ 종전 이 경로는 `exit_flag_age` 를 **아예 넘기지
        #   않았다** — 그래서 손으로 돌린 `--once` 진단은 정상 종료를 항상 미측정으로
        #   읽어 가짜 CRITICAL 을 냈다(2026-08-26 16:17 실측). 주기 감시 경로와 같은
        #   입력을 주는 것이 맞다. 판정 함수를 고치는 것이 아니라 **입력 결손**이었다.
        verdict = judge(collect(root, now, now.date()), stall_sec=stall,
                        exit_flag_age=exit_flag_age(root, now),
                        close_done_age=close_done_age(root, now, now.date()))
        emit(root, now.date(), verdict, popup=popup, manual=True)
        return verdict["rc"]

    log_armed(root, now.date(), window, stall, check)
    print("[FreezeSentinel] 감시 시작 pid=%d 창=%s~%s (알림 전용)"
          % (os.getpid(), window[0], window[1]))

    last_rc = RC_NOT_APPLICABLE
    alerted = False
    close_logged = False   # [498차 F-10] NORMAL_CLOSE 는 상태 전이 시 1회만 남긴다
    while True:
        now = datetime.datetime.now()
        if not _in_window(now, window):
            # 창 밖이면 쉰다. 창이 끝났으면 종료한다(하루 1회 사이드카).
            try:
                h1, m1 = [int(x) for x in str(window[1]).split(":")]
            except Exception:
                h1, m1 = 16, 30
            if now.time() > datetime.time(h1, m1):
                print("[FreezeSentinel] 감시 창 종료 — 정상 종료")
                return last_rc
            time.sleep(min(60.0, check))
            continue

        verdict = judge(collect(root, now, now.date()), stall_sec=stall,
                        exit_flag_age=exit_flag_age(root, now),
                        close_done_age=close_done_age(root, now, now.date()))
        last_rc = verdict["rc"]
        if verdict.get("state") == "NORMAL_CLOSE":
            # [MW0601 498차 / F-10] 정상 마감 뒤 정지 — **감시는 계속하되** 최고
            # 등급 경보를 내지 않는다. 종전에는 여기서 매 주기 CRITICAL 이 나가
            # 15:45~16:17 에만 33회가 쌓였다(이상점 1-11). 경보 피로가 쌓이면
            # 진짜 동결(2026-08-19 13:41)이 같은 문구에 묻힌다.
            # ⚠ 감시 자체를 끄지 않는 이유: 마감 뒤에도 관측은 남아야 한다.
            if not close_logged:
                # manual=False 로 둔다 — 이건 손으로 돌린 진단이 아니라 진짜 관측이다.
                # INFO 는 마커·팝업 대상이 아니므로 로그에만 남는다(emit 참조).
                emit(root, now.date(), verdict, popup=False, manual=False)
                close_logged = True
            alerted = False
            time.sleep(check)
            continue
        close_logged = False
        if verdict.get("state") == "EXITED":
            # [MW0601 493차 후속5 / F-Z 변경 ②] 정상 종료가 확인되면 **창 종료를
            # 기다리지 않고 빠져나온다.** 종전에는 15:45~16:30 동안 매 주기 가짜
            # CRITICAL 을 냈다(2026-08-25 실측 43회 + 팝업 1회).
            log_line(root, now.date(),
                     "[FreezeSentinel] %s 정상 종료 확인 — 감시 종료"
                     % now.strftime("%Y-%m-%d %H:%M:%S"))
            return verdict["rc"]
        if verdict["level"] == "CRITICAL":
            # 같은 동결로 매 주기 팝업을 띄우면 사람이 화면을 못 쓴다 — 첫 확정에만
            # 팝업·마커를 내고 이후는 로그만 남긴다(경보 피로 방지).
            emit(root, now.date(), verdict, popup=(popup and not alerted), manual=alerted)
            alerted = True
        elif verdict["level"] == "OK" and alerted:
            alerted = False
            log_line(root, now.date(),
                     "[FreezeSentinel] %s 회복 — 신호가 다시 신선해졌다"
                     % now.strftime("%Y-%m-%d %H:%M:%S"))
        time.sleep(check)


if __name__ == "__main__":
    sys.exit(main())
