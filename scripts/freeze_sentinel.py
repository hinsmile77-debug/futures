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

2단계(**[MW0602 2026-10-24 사용자 결정]** `FREEZE_SENTINEL_KILL_ENABLED`):
       **보유 중** 동결에 한해 프로세스를 끊어 런처 재기동 → 포지션 복원 → 손절 즉시
       재판정 왕복을 태운다. 조건 6종(장중 창 · 보유 중 · FZ-1 신호 2종 정지 ·
       PID 확인 · 하루 상한/쿨다운 · 수동 진단 제외)은 `kill_decision()` 위 주석.
       종전(490차)에는 「알림 전용 — 승격은 주간회의 안건」이었다. 바뀐 이유:
       Cybos/CREON API 에 서버 측 스톱이 없어(2026-10-24 조사) 동결 = 손절 부재이고,
       실계좌(2026-10-13~)에서 그 구멍의 비용이 사람이 PC 앞에 있는지에 달려 있었다.
       ⚠ 15:10 이후에는 런처가 재기동하지 않으므로 창을 15:05 에서 닫는다.

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

def judge(ages, stall_sec=300.0, exit_flag_age=None, close_done_age=None,
          shutdown_age=None):
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
        shutdown_age: [MW0601 513차] `data/shutdown_normal_<date>.txt` 의 **나이(초)**.
              `_exit_normally` 와 같은 뜻(프로세스가 스스로 종료했다)이되 **런처가
              지우지 않는** 날짜본이라 판정 시점에 실제로 존재한다.
              None = 마커 없음(**미측정**).

    Returns:
        dict(level, rc, headline, details[], stale[], unmeasured[], state)

    판정:
      ① 측정된 신호가 하나도 없다            → UNKNOWN (조용히 OK로 넘기지 않는다)
      ② 측정된 신호가 **전부** 정체
         · 정상 종료 플래그가 신호보다 **뒤**  → NOT_APPLICABLE (state=EXITED)
         · 종료 마커가 **가장 오래된** 신호보다 뒤 → NOT_APPLICABLE (state=EXITED)
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
        _max_stale_age = max(ages[n] for n in stale)
        if exit_flag_age is not None and exit_flag_age < _min_stale_age:
            details.append(
                "%-16s %.0fs 전 — 정상 종료 플래그(가장 최근 정체 신호 %.0fs 보다 뒤)"
                % ("_exit_normally", exit_flag_age, _min_stale_age))
            return {"level": "NOT_APPLICABLE", "rc": RC_NOT_APPLICABLE,
                    "state": "EXITED",
                    "headline": "정상 종료 확인 — 감시 종료 (동결이 아니다)",
                    "details": details, "stale": stale, "unmeasured": unmeasured}
        # [MW0601 513차] **종료 마커** — 위 플래그와 같은 사실을 재는데, 런처가
        # 지우지 않으므로 판정 시점에 실제로 존재한다(그 플래그는 사실상 항상 없다).
        #
        # ⚠ **비교 기준이 위 축과 다르다 — `max`(가장 오래된 정체 신호)다.**
        #   이 마커는 「프로세스가 종료한 시각」이므로, 가장 오래된 신호보다 뒤이기만
        #   하면 「정체 신호 전부가 이 종료 이전의 것」이 성립한다. 여기에 `min`(가장
        #   최근 신호)을 쓰면 **종료 직후에 남는 로그 한 줄**(`[System] 자동 종료 실행`
        #   — 마커보다 수백 ms 뒤)에 매번 걸려 실패한다. 498차 F-10 이 실전에서 한
        #   번도 성립하지 못한 원인이 정확히 그 기준 선택이었다(2026-08-25~09-01
        #   매일 45회 가짜 CRITICAL — 마커 15:40:11 vs 마지막 신호 15:40:26).
        #
        # 🔴 **08-19 형은 그대로 지킨다.** 그날은 13:41 동결이라 프로세스가 종료하지
        #   않았고 마커 자체가 없다 → 미측정 → CRITICAL. 그리고 **존재만으로 판정하지
        #   않는다** — 오전에 한 번 정상 종료(마커 기록)한 뒤 재기동한 세션이 오후에
        #   얼어붙으면 마커가 신호들보다 **먼저**라 여기서 걸러진다.
        if shutdown_age is not None and shutdown_age < _max_stale_age:
            details.append(
                "%-16s %.0fs 전 — 종료 마커(가장 오래된 정체 신호 %.0fs 보다 뒤)"
                % ("shutdown_normal", shutdown_age, _max_stale_age))
            return {"level": "NOT_APPLICABLE", "rc": RC_NOT_APPLICABLE,
                    "state": "EXITED",
                    "headline": "정상 종료 확인(종료 마커) — 감시 종료 (동결이 아니다)",
                    "details": details, "stale": stale, "unmeasured": unmeasured}
        # [MW0601 498차 / F-10] 두 번째 독립 증거 — 마감 완료 마커.
        # `_exit_normally` 와 **같은 시각 비교 규칙**이다(존재만으로 판정하지 않는다).
        if close_done_age is not None and close_done_age < _min_stale_age:
            details.append(
                "%-16s %.0fs 전 — 일일 마감 완료 마커(가장 최근 정체 신호 %.0fs 보다 뒤)"
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
        if shutdown_age is None:
            details.append("%-16s **미측정**(마커 없음) — 동결 판정 유지"
                           % "shutdown_normal")
        else:
            details.append(
                "%-16s %.0fs 전 — 가장 오래된 정체 신호(%.0fs)보다 **먼저**다"
                "(이 세션의 종료가 아니다)"
                % ("shutdown_normal", shutdown_age, _max_stale_age))
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


def shutdown_marker_age(root, now, day):
    """[MW0601 513차] `data/shutdown_normal_<date>.txt` 의 나이(초).

    `main.py:_write_exit_normally_flag()` 가 `_exit_normally` 와 **함께** 쓰는
    날짜본 사본이다. 런처(`start_mireuk.bat:597~598`)가 `_exit_normally` 를 읽은
    직후 지우므로, 프로세스 밖 센티넬이 판정 시점에 볼 수 있는 정상 종료의 증거는
    사실상 이것뿐이다.

    ⚠ 없거나 읽기 실패면 **None(미측정)** — `exit_flag_age()` 와 같은 규약이다.
      미측정은 `judge()` 에서 **동결 판정 유지**로 처리된다(감시자가 조용해지는
      것이 오탐보다 나쁘다).
    ⚠ 파일 mtime 을 쓴다(내용이 아니라) — 형식이 바뀌면 파싱 실패 → 미측정 →
      가짜 CRITICAL 로 되돌아가기 때문이다.
    ⚠ 날짜가 파일명에 박혀 있어 어제 마커가 오늘 판정에 끼어들지 않는다. 그래도
      `judge()` 는 **시각을 비교**한다 — 이중 안전장치다.
    """
    path = os.path.join(root, "data",
                        "shutdown_normal_%s.txt" % day.strftime("%Y%m%d"))
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


def log_armed(root, day, window, stall, check, kill_note="알림 전용 — 하드 종료 없음"):
    """감시 개시를 파일에 남긴다 — **센티넬 자신의 생존 증거**.

    F-2 가드의 `log_armed()` 와 같은 취지다. 이 콘솔은 아무도 보지 않으므로,
    기동 줄이 없으면 센티넬이 조용히 죽어도 그 사실이 어디에도 남지 않는다 —
    감시자가 스스로 「조용한 부재」에 빠지는 것이 가장 나쁘다.
    """
    return log_line(root, day, (
        "[FreezeSentinel] %s ARMED pid=%s 창=%s~%s 정지임계=%.0fs 주기=%.0fs (%s)"
        % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), os.getpid(),
           window[0], window[1], stall, check, kill_note)
    ))


def emit(root, day, verdict, popup=True, manual=False):
    """경보를 남긴다 — 로그 · (경보 시)마커 파일 · (옵션)메시지박스.

    Slack은 쓰지 않는다(사용자 결정: 개발단계 직접 모니터링).
    메일은 여기서 보내지 않는다 — 주기 감시 루프가 **동결 첫 확정 때만** 따로 부른다
    (`build_alert_mail` · `send_mail_async`, MW0602 F-1009).
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


# ── 메일 (MW0602 F-1009) ──────────────────────────────────────────────────
#
# 종전 경보는 로그 · 마커 · 팝업뿐이라 **트레이딩 PC 앞에 사람이 없으면 아무도
# 몰랐다.** 실계좌 전환(2026-10-13) 뒤로는 포지션을 든 채 얼어붙어도 15:10 강제청산이
# 돌지 않는다는 점이 그대로 손실 위험이다. 그래서 동결 첫 확정 때 메일 1통, 회복 때
# 1통을 보낸다. 형식은 신동 일일리포트(`[신동][<PC>] …`)에 맞춘다.
#
# ⚠ 제목·본문 생성은 순수 함수다(테스트가 고정). 발송은 별도 스레드 — SMTP 가
#   최대 30초 막혀도 감시 주기가 밀리지 않게 한다. 실패는 로그 한 줄로 남기고
#   센티넬은 계속 돈다(계측 4원칙 ④ — 「안 보냈다」를 조용히 넘기지 않는다).

MAIL_TAG_ALERT = "[긴급이상]"
MAIL_TAG_RECOVER = "[이상해소]"
# [MW0602 2026-10-17] 긴급 알림 카탈로그(utils/alert_mail.CATALOG) 코드 — 동결은 S-04.
#   제목 머리 `[긴급이상][PC][S-04]` 로 main 이 보내는 다른 S/A/B 경보와 같은 형식이 된다.
ALERT_CODE_FREEZE = "S-04"
ALERT_CODE_NOT_STARTED = "S-05"


def build_alert_mail(verdict, pc, now, stall_sec):
    """동결 경보 메일의 (제목, 본문). 파일 IO 없음."""
    hhmm = now.strftime("%H:%M")
    mins = int(round(float(stall_sec) / 60.0))
    subject = "%s[%s][%s] 미륵이 동결 — %d분 이상 무응답 %s" % (
        MAIL_TAG_ALERT, pc, ALERT_CODE_FREEZE, mins, hhmm)
    lines = [
        "%s PC 의 미륵이가 %s 기준으로 얼어붙은 것으로 보입니다." % (pc, now.strftime("%Y-%m-%d %H:%M:%S")),
        "프로세스는 살아 있을 수 있으나 아무 일도 하지 않으며, 런처의 자동 재시작도 걸리지 않습니다.",
        "",
        "지금 확인할 것",
        "  1. 트레이딩 PC 화면 — 미륵이 창이 응답하는지",
        "  2. 증권사 HTS — 보유 포지션이 있는지 (동결 중에는 손절·15:10 강제청산이 돌지 않습니다)",
        "  3. 응답이 없으면 미륵이를 재시작하세요",
        "",
        "판정 근거",
        "  " + str(verdict.get("headline", "")),
    ]
    lines += ["  · " + str(d) for d in verdict.get("details", [])]
    lines += ["", "— 미륵이 %s 동결 센티넬(FZ-2) 자동 발송. 같은 동결로는 다시 보내지 않고, "
                  "회복되면 %s 메일을 보냅니다." % (pc, MAIL_TAG_RECOVER)]
    return subject, chr(10).join(lines)


def build_recovery_mail(pc, since, now):
    """회복 메일의 (제목, 본문). `since` 는 경보 시각(None 이면 지속시간 생략)."""
    dur, dur_body = "", ""
    if since is not None:
        _m = max(0, int(round((now - since).total_seconds() / 60.0)))
        dur = " — 지속 %d분" % _m              # alert_mail 해소 제목과 같은 꼬리
        dur_body = " (%d분간)" % _m
    subject = "%s[%s][%s] 미륵이 동결 회복 %s%s" % (
        MAIL_TAG_RECOVER, pc, ALERT_CODE_FREEZE, now.strftime("%H:%M"), dur)
    body = chr(10).join([
        "%s PC 의 미륵이 신호가 %s 에 다시 들어오기 시작했습니다%s."
        % (pc, now.strftime("%Y-%m-%d %H:%M:%S"), dur_body),
        "동결 동안 놓친 손절·청산이 없었는지 증권사 HTS 의 포지션과 체결 내역을 확인하세요.",
        "",
        "— 미륵이 %s 동결 센티넬(FZ-2) 자동 발송." % pc,
    ])
    return subject, body


def _slack_post(text, level="CRITICAL"):
    """[MW0602 2026-10-17] 메일과 함께 Slack 에도 한 줄 — 실패는 조용히 넘긴다(메일이 본선)."""
    try:
        from utils.notify import notify
        notify(text, level=level)
        return True
    except Exception:
        return False


def send_mail_async(root, day, subject, body, sender=None, slack_too=False, slack=None):
    """별도 스레드로 보낸다 — 반환: 시작한 스레드. 결과는 센티넬 로그에 한 줄.

    `slack_too` 면 메일과 **함께** Slack 에 제목 한 줄을 보내고(ALERT_MAIL_SLACK_TOO),
    메일이 실패하면 Slack 에 실패 사실을 한 줄 더 남긴다 — 메일만 믿다 조용히 잃지 않게.
    """
    import threading
    _slack = slack or _slack_post

    def _run():
        if slack_too:
            try:
                _slack(subject, "CRITICAL" if subject.startswith(MAIL_TAG_ALERT) else "INFO")
            except Exception:
                pass
        try:
            if sender is None:
                from utils import mailer
                rcpt = mailer.send_mail(subject, body)
            else:
                rcpt = sender(subject, body)
            log_line(root, day, "[FreezeSentinel] %s 메일 발송 성공 → %s | %s"
                     % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        ", ".join(rcpt or []), subject))
        except Exception as exc:
            # 예외 메시지에 비밀번호는 실리지 않는다(mailer 규약) — 종류와 문구만 남긴다.
            log_line(root, day, "[FreezeSentinel] %s 메일 발송 실패(%s: %s) | %s"
                     % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        type(exc).__name__, exc, subject))
            if slack_too and type(exc).__name__ != "MailDisabled":
                try:
                    _slack("[FreezeSentinel] 메일 발송 실패(%s) — %s" % (type(exc).__name__, subject),
                           "CRITICAL")
                except Exception:
                    pass

    th = threading.Thread(target=_run, name="FreezeSentinelMail")
    th.daemon = False   # 감시 창이 끝나 main 이 반환해도 보내던 메일은 마저 보낸다
    th.start()
    return th


# ── [MW0602 2026-10-24 사용자 결정] 2단계 — 동결 시 강제 재기동 ────────────────
#
# 왜: 신동·피터·미륵 손절은 **프로그램이 가격을 보고 내는 주문**이다. Cybos/CREON Plus
#   API 에는 서버 측 스톱(감시) 주문이 없다(`docs/신동거래_V4/서버측_스톱주문_지원여부_조사_
#   MW0602-20261024.md`). 그래서 프로세스가 얼어붙으면 손절이 **아예 나가지 않는다** —
#   1단계(알림)는 사람이 PC 앞에 있을 때만 구멍을 막는다.
#   2단계는 얼어붙은 프로세스를 끊어 런처 RESTART_LOOP 를 태운다 →
#   새 프로세스가 `position_state.json` 에서 포지션·손절선(`ext_stop` 포함)을 복원 →
#   `main._ts_restart_stop_check_tick` 이 첫 실시간가로 손절을 즉시 재판정한다.
#
# 🔴 감시자가 새 사고를 만드는 것이 여기서 가장 피해야 할 결과다 — 그래서 조건을 전부 건다:
#   ① 장중 창(`FREEZE_SENTINEL_KILL_WINDOW`, 기본 09:00~15:05). 런처는 15:10 이후 종료에서
#      재기동하지 않으므로(오버나이트 금지) 그 뒤의 하드 종료는 이득 없이 마감만 죽인다.
#   ② **보유 중**(`position_state.json` 오늘자 · FLAT 아님). 무포지션 동결은 위험이 없다.
#   ③ 정체 임계 `FREEZE_SENTINEL_KILL_STALL_SEC`(기본 180초)로 `judge()` 가 CRITICAL 이고,
#      **FZ-1 스레드 신호 2종(하트비트 파일 · `[TS]`)이 둘 다 측정되고 둘 다 정체**.
#      이 둘은 메인 루프와 무관한 스레드가 30초마다 쓰므로, 둘 다 180초 멎었다는 것은
#      GIL 까지 잡힌 동결이다(메인 루프만 멎은 동결은 FZ-1 이 스스로 os._exit 한다).
#   ④ 대상 PID = **하트비트 파일의 pid**. psutil 로 살아 있는 python · 이 저장소의
#      `main.py` · 하트비트보다 먼저 생성됨(PID 재사용 차단)을 모두 확인한다.
#      재기동 중인 새 프로세스는 아직 하트비트를 안 썼으므로(옛 PID = 이미 죽음) 대상이 아니다.
#   ⑤ 하루 최대 `FREEZE_SENTINEL_KILL_MAX_PER_DAY`(2)회 · 직전 종료 뒤 `..._COOLDOWN_SEC`(600초).
#      기록은 `data/freeze_kill_<date>.json` — 센티넬이 재기동돼도 잊지 않는다.
#   ⑥ `--once`(수동 진단)는 **판정만 출력하고 절대 죽이지 않는다.**

KILL_RECORD_TPL = "data/freeze_kill_%s.json"


def position_state(root, now):
    """`data/position_state.json` → {status, quantity, entry_source, stop_price} 또는 None(미측정).

    오늘 저장분만 인정한다(어제 파일은 미측정). FLAT 도 그대로 돌려준다 — 판정은 호출자 몫.
    """
    try:
        with io.open(os.path.join(root, "data", "position_state.json"), "r", encoding="utf-8") as f:
            st = json.load(f)
        saved = datetime.datetime.strptime(str(st.get("saved_at"))[:19], "%Y-%m-%dT%H:%M:%S")
    except Exception:
        return None
    if saved.date() != now.date():
        return None
    return {"status": str(st.get("status") or ""),
            "quantity": int(st.get("quantity") or 0),
            "entry_source": st.get("entry_source"),
            "stop_price": st.get("stop_price"),
            "saved_at": saved}


def _heartbeat_pid(root, day, pc=None):
    """하트비트 파일의 (pid, written_at) — 없거나 깨졌으면 (None, None)."""
    try:
        from config.settings import FREEZE_WATCHDOG_HEARTBEAT_PATH as tpl
    except Exception:
        tpl = "data/heartbeat_{pc}_{date}.json"
    path = os.path.join(root, tpl.format(pc=pc or _pc_id(), date=day.strftime("%Y%m%d")))
    try:
        with io.open(path, "r", encoding="utf-8") as f:
            hb = json.load(f)
        pid = int(hb.get("pid"))
        written = datetime.datetime.strptime(str(hb.get("written_at"))[:19], "%Y-%m-%dT%H:%M:%S")
        return pid, written
    except Exception:
        return None, None


def resolve_target(root, day, pc=None, psutil_mod=None):
    """하드 종료 대상 확인 — {"ok": bool, "pid": int|None, "why": str}.

    하트비트의 pid 가 지금도 살아 있는 **이 저장소의 main.py python 프로세스**이고,
    그 프로세스가 하트비트 기록 시각보다 먼저 생성됐을 때만 ok.
    """
    pid, written = _heartbeat_pid(root, day, pc)
    if pid is None:
        return {"ok": False, "pid": None, "why": "하트비트 pid 미측정"}
    try:
        ps = psutil_mod
        if ps is None:
            import psutil as ps
    except Exception as exc:
        return {"ok": False, "pid": pid, "why": "psutil 없음(%s)" % type(exc).__name__}
    try:
        p = ps.Process(pid)
        name = (p.name() or "").lower()
        cmd = p.cmdline() or []
        cwd = ""
        try:
            cwd = p.cwd() or ""
        except Exception:
            pass
        created = datetime.datetime.fromtimestamp(p.create_time())
    except Exception as exc:
        return {"ok": False, "pid": pid, "why": "pid %d 프로세스 없음/접근 불가(%s)" % (pid, type(exc).__name__)}
    if "python" not in name:
        return {"ok": False, "pid": pid, "why": "pid %d 는 python 이 아니다(%s)" % (pid, name)}
    tgt = os.path.normcase(os.path.join(os.path.abspath(root), "main.py"))
    mains = [os.path.normcase(c if os.path.isabs(c) else os.path.join(cwd or "?", c))
             for c in cmd if (c or "").lower().endswith("main.py")]
    if tgt not in mains:
        return {"ok": False, "pid": pid, "why": "pid %d 는 이 저장소의 main.py 가 아니다(%s)" % (pid, " ".join(cmd))}
    if created > written + datetime.timedelta(seconds=2):
        return {"ok": False, "pid": pid, "why": "pid %d 가 하트비트(%s)보다 나중에 생겼다 — PID 재사용"
                % (pid, written.strftime("%H:%M:%S"))}
    return {"ok": True, "pid": pid, "why": "pid %d main.py (생성 %s · 하트비트 %s)"
            % (pid, created.strftime("%H:%M:%S"), written.strftime("%H:%M:%S"))}


def load_kill_history(root, day):
    """오늘 강제 종료 기록(list of dict) — 없으면 []."""
    try:
        with io.open(os.path.join(root, KILL_RECORD_TPL % day.strftime("%Y%m%d")), "r", encoding="utf-8") as f:
            rows = json.load(f)
        return rows if isinstance(rows, list) else []
    except Exception:
        return []


def append_kill_record(root, day, rec):
    path = os.path.join(root, KILL_RECORD_TPL % day.strftime("%Y%m%d"))
    rows = load_kill_history(root, day) + [rec]
    try:
        d = os.path.dirname(path)
        if not os.path.isdir(d):
            os.makedirs(d)
        tmp = path + ".tmp"
        with io.open(tmp, "w", encoding="utf-8") as f:
            f.write(json.dumps(rows, ensure_ascii=False, indent=1))
        os.replace(tmp, path)
        return True
    except Exception as exc:
        print("[FreezeSentinel] 강제 종료 기록 실패: %s" % exc, file=sys.stderr)
        return False


def kill_decision(ages, now, kill_stall_sec, window, position, history,
                  max_per_day=2, cooldown_sec=600.0,
                  exit_flag_age=None, close_done_age=None, shutdown_age=None):
    """강제 재기동을 할 것인가 — 순수 함수(대상 PID 확인은 호출자가 따로 한다).

    Returns: {"kill": bool, "reason": str, "verdict": judge 결과}
    """
    v = judge(ages, stall_sec=kill_stall_sec, exit_flag_age=exit_flag_age,
              close_done_age=close_done_age, shutdown_age=shutdown_age)

    def _no(why):
        return {"kill": False, "reason": why, "verdict": v}

    if not _in_window(now, window):
        return _no("강제 재기동 창(%s~%s) 밖" % (window[0], window[1]))
    if v["level"] != "CRITICAL":
        return _no("정체 %.0fs 기준 %s" % (kill_stall_sec, v["level"]))
    for sig in (SIG_HEARTBEAT, SIG_TS):
        if sig not in v["stale"]:
            return _no("%s 가 정체로 측정되지 않았다(미측정 또는 신선) — FZ-1 스레드 신호 2종이 "
                       "둘 다 멎어야 한다" % sig)
    if position is None:
        return _no("포지션 상태 미측정(position_state.json 오늘자 없음) — 보유 중일 때만 끊는다")
    if position.get("status") in ("", "FLAT") or int(position.get("quantity") or 0) <= 0:
        return _no("무포지션(FLAT) — 동결이어도 손절 위험이 없다")
    if len(history) >= int(max_per_day):
        return _no("오늘 강제 재기동 %d회 — 상한 %d회 도달(사람이 볼 것)" % (len(history), int(max_per_day)))
    if history:
        try:
            last = datetime.datetime.strptime(str(history[-1].get("at"))[:19], "%Y-%m-%d %H:%M:%S")
            if (now - last).total_seconds() < float(cooldown_sec):
                return _no("직전 강제 재기동 %s 뒤 %.0fs — 쿨다운 %.0fs"
                           % (last.strftime("%H:%M:%S"), (now - last).total_seconds(), float(cooldown_sec)))
        except Exception:
            pass
    return {"kill": True, "verdict": v,
            "reason": "보유 중(%s %d계약) 동결 — 정체 %.0fs 이상 · FZ-1 신호 2종 정지"
                      % (position.get("status"), int(position.get("quantity") or 0), kill_stall_sec)}


def hard_kill(pid, psutil_mod=None, wait_sec=10.0):
    """대상 프로세스를 끊는다 — (ok, 설명). `_exit_normally` 를 쓰지 않으므로 런처가 재기동한다."""
    try:
        ps = psutil_mod
        if ps is None:
            import psutil as ps
        p = ps.Process(pid)
        p.kill()
        try:
            p.wait(timeout=wait_sec)
        except Exception:
            pass
        return True, "pid %d 종료 요청 완료" % pid
    except Exception as exc:
        return False, "pid %d 종료 실패(%s: %s)" % (pid, type(exc).__name__, exc)


def build_kill_mail(decision, target, ok, msg, pc, now, position):
    """강제 재기동 메일의 (제목, 본문). S-04 의 2단계 — 같은 동결로 1단계 메일이 따로 가지 않는다."""
    subject = "%s[%s][%s] 미륵이 동결 — 강제 재기동 %s %s" % (
        MAIL_TAG_ALERT, pc, ALERT_CODE_FREEZE, "실행" if ok else "실패", now.strftime("%H:%M"))
    pos = position or {}
    lines = [
        "%s PC 의 미륵이가 보유 중에 얼어붙어 동결 센티넬이 프로세스를 끊었습니다%s." % (
            pc, "" if ok else " — **종료에 실패했습니다**"),
        "",
        "보유 포지션(마지막 저장): %s %s계약 · 진입 주체 %s · 손절선 %s" % (
            pos.get("status"), pos.get("quantity"), pos.get("entry_source") or "미륵", pos.get("stop_price")),
        "조치: %s" % msg,
        "",
        "이후 흐름",
        "  1. 런처가 10초 뒤 미륵이를 다시 띄웁니다 (15:10 이후면 재기동 없음)",
        "  2. 새 프로세스가 포지션·손절선을 복원하고 첫 실시간가로 손절을 즉시 재판정합니다",
        "  3. 신호가 다시 들어오면 [이상해소] 메일이 옵니다 — 안 오면 HTS 에서 직접 청산하세요",
        "",
        "판정 근거",
        "  " + decision.get("reason", ""),
        "  대상 확인: " + target.get("why", ""),
    ]
    lines += ["  · " + str(d) for d in decision.get("verdict", {}).get("details", [])]
    lines += ["", "— 미륵이 %s 동결 센티넬(FZ-2) 자동 발송." % pc]
    return subject, chr(10).join(lines)


def try_kill(root, now, ages, kcfg, flags, pc, psutil_mod=None, execute=True):
    """판정 → 대상 확인 → (execute 면) 기록 · 종료. 반환: dict(done, decision, target, ok, msg, position)."""
    position = position_state(root, now)
    history = load_kill_history(root, now.date())
    dec = kill_decision(ages, now, kcfg["stall"], kcfg["window"], position, history,
                        max_per_day=kcfg["max_per_day"], cooldown_sec=kcfg["cooldown"],
                        exit_flag_age=flags.get("exit"), close_done_age=flags.get("close"),
                        shutdown_age=flags.get("shutdown"))
    out = {"done": False, "decision": dec, "target": None, "ok": False, "msg": "", "position": position}
    if not dec["kill"]:
        return out
    tgt = resolve_target(root, now.date(), pc, psutil_mod)
    out["target"] = tgt
    if not tgt["ok"]:
        dec["kill"] = False
        dec["reason"] = "대상 확인 실패 — " + tgt["why"]
        return out
    if not execute:
        out["msg"] = "수동 진단 — 실행하지 않음(판정만)"
        return out
    # 기록을 **먼저** 남긴다 — 새 프로세스가 기동하며 이 파일로 「동결 강제 재기동 뒤」임을 안다.
    append_kill_record(root, now.date(), {
        "at": now.strftime("%Y-%m-%d %H:%M:%S"), "pid": tgt["pid"], "reason": dec["reason"],
        "ages": dict((k, (None if v is None else round(float(v), 1))) for k, v in ages.items()),
        "position": dict((k, v) for k, v in (position or {}).items() if k != "saved_at"),
    })
    ok, msg = hard_kill(tgt["pid"], psutil_mod)
    out.update(done=True, ok=ok, msg=msg)
    return out


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


def _hm(text, default):
    try:
        h, m = [int(x) for x in str(text).split(":")]
        return datetime.time(h, m)
    except Exception:
        return default


class PremarketWatch(object):
    """[MW0602 2026-10-17 / S-05] 장전 미기동·기동 실패 감시.

    main 이 안 떴으면 main 은 스스로 알릴 수 없다 — 그래서 프로세스 밖 센티넬이 맡는다.
    판정: `ALERT_PREMARKET_START_HM`(08:52) 이후 **오늘 SYSTEM.log 가 없다**.
      · 어제 파일·하트비트는 보지 않는다 — 「오늘 기동했는가」만 묻는다.
      · 파일이 생기면 해소 메일 1통(지속 N분).
    발송은 utils.alert_mail(proc="sentinel") 에피소드 — 재기동해도 같은 날 다시 안 보낸다.
    """

    def __init__(self, root, start_hm, mailer=None):
        self.root = root
        self.start = start_hm
        self._mailer = mailer

    def mailer(self):
        if self._mailer is None:
            from utils.alert_mail import AlertMailer
            self._mailer = AlertMailer(proc="sentinel")
        return self._mailer

    def not_started(self, now):
        return now.time() >= self.start and syslog_age(self.root, now, now.date()) is None

    def tick(self, now):
        """반환: "RAISED" / "RESOLVED" / "OPEN" / "OK" / "BEFORE"."""
        if now.time() < self.start:
            return "BEFORE"
        try:
            m = self.mailer()
            if self.not_started(now):
                if m.is_open(ALERT_CODE_NOT_STARTED):
                    return "OPEN"
                m.raise_alert(
                    ALERT_CODE_NOT_STARTED,
                    "%s 현재 오늘 SYSTEM.log 없음 — 미륵이가 기동하지 않았다" % now.strftime("%H:%M"),
                    ["기준: logs/%s_SYSTEM.log 부재 (판정 시작 %s)"
                     % (now.strftime("%Y%m%d"), self.start.strftime("%H:%M")),
                     "작업 스케줄러 \\Maitreya(08:40) 실행 결과를 확인하세요"])
                return "RAISED"
            if m.is_open(ALERT_CODE_NOT_STARTED):
                m.resolve(ALERT_CODE_NOT_STARTED, note="오늘 SYSTEM.log 생성 확인 — 기동됨")
                return "RESOLVED"
        except Exception:
            return "OK"
        return "OK"


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
    mail_on = bool(_cfg("FREEZE_SENTINEL_MAIL_ENABLED", False))
    mail_recover = mail_on and bool(_cfg("FREEZE_SENTINEL_MAIL_RECOVERY", True))
    slack_too = bool(_cfg("ALERT_MAIL_SLACK_TOO", False))

    if not _cfg("FREEZE_SENTINEL_ENABLED", True):
        print("[FreezeSentinel] 설정 비활성(FREEZE_SENTINEL_ENABLED=False) — 종료")
        return RC_NOT_APPLICABLE

    # [MW0602 2026-10-24] 2단계 — 보유 중 동결이면 강제 재기동(조건은 kill_decision 주석)
    kill_on = bool(_cfg("FREEZE_SENTINEL_KILL_ENABLED", False))
    kcfg = {"stall": float(_cfg("FREEZE_SENTINEL_KILL_STALL_SEC", 180.0)),
            "window": _cfg("FREEZE_SENTINEL_KILL_WINDOW", ("09:00", "15:05")),
            "max_per_day": int(_cfg("FREEZE_SENTINEL_KILL_MAX_PER_DAY", 2)),
            "cooldown": float(_cfg("FREEZE_SENTINEL_KILL_COOLDOWN_SEC", 600.0))}
    kill_note = ("보유 중 동결 강제 재기동 ON — 정체 %.0fs · 창 %s~%s · 하루 %d회"
                 % (kcfg["stall"], kcfg["window"][0], kcfg["window"][1], kcfg["max_per_day"])
                 if kill_on else "알림 전용 — 하드 종료 없음")

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
                        close_done_age=close_done_age(root, now, now.date()),
                        shutdown_age=shutdown_marker_age(root, now, now.date()))
        emit(root, now.date(), verdict, popup=popup, manual=True)
        if kill_on:
            # ⚠ 수동 진단은 **절대 죽이지 않는다**(execute=False) — 판정만 보여준다.
            _ages = collect(root, now, now.date())
            _k = try_kill(root, now, _ages, kcfg,
                          {"exit": exit_flag_age(root, now),
                           "close": close_done_age(root, now, now.date()),
                           "shutdown": shutdown_marker_age(root, now, now.date())},
                          _pc_id(), execute=False)
            print("[FreezeSentinel] 강제 재기동 판정(수동 — 실행 안 함): %s · %s" % (
                "대상" if _k["decision"]["kill"] else "아님", _k["decision"]["reason"]))
        return verdict["rc"]

    log_armed(root, now.date(), window, stall, check, kill_note)
    # [F-1009] 메일 상태도 생존 증거와 함께 남긴다 — 「켜져 있는 줄 알았는데 꺼져
    # 있었다」를 사후에 가를 수 있게(계측 4원칙 ④).
    try:
        from utils import mailer as _ml
        _mcfg, _missing = _ml.smtp_config()
        _mail_state = ("ON → " + ", ".join(_mcfg["to"])) if (mail_on and _mcfg) else (
            "OFF(설정 비활성)" if not mail_on else "OFF(SMTP 미설정: " + ", ".join(_missing) + ")")
    except Exception as exc:
        _mail_state = "OFF(메일 모듈 로드 실패: %s)" % type(exc).__name__
    log_line(root, now.date(), "[FreezeSentinel] 메일 경보 %s" % _mail_state)
    print("[FreezeSentinel] 감시 시작 pid=%d 창=%s~%s (%s)"
          % (os.getpid(), window[0], window[1], kill_note))

    pc = _pc_id()
    premarket = PremarketWatch(root, _hm(_cfg("ALERT_PREMARKET_START_HM", "08:52"),
                                         datetime.time(8, 52)))
    last_rc = RC_NOT_APPLICABLE
    alerted = False
    alerted_at = None      # [F-1009] 회복 메일의 지속시간 계산용
    close_logged = False   # [498차 F-10] NORMAL_CLOSE 는 상태 전이 시 1회만 남긴다
    while True:
        now = datetime.datetime.now()
        _pm = premarket.tick(now)          # [S-05] 창 밖(08:52~09:00)에서도 돈다
        if _pm in ("RAISED", "RESOLVED"):
            log_line(root, now.date(), "[FreezeSentinel] %s 장전 기동 감시 %s"
                     % (now.strftime("%Y-%m-%d %H:%M:%S"), _pm))
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

        _ages = collect(root, now, now.date())
        _flags = {"exit": exit_flag_age(root, now),
                  "close": close_done_age(root, now, now.date()),
                  "shutdown": shutdown_marker_age(root, now, now.date())}
        verdict = judge(_ages, stall_sec=stall, exit_flag_age=_flags["exit"],
                        close_done_age=_flags["close"], shutdown_age=_flags["shutdown"])
        last_rc = verdict["rc"]
        if kill_on:
            # [MW0602 2026-10-24] 2단계 — 1단계 경보(300초)보다 먼저(180초) 온다.
            #   실행했으면 이번 주기의 1단계 경보는 건너뛴다(같은 동결로 메일 2통 금지).
            #   alerted=True 로 두어 새 프로세스 신호가 들어오면 회복 메일이 나간다.
            try:
                _k = try_kill(root, now, _ages, kcfg, _flags, pc)
            except Exception as exc:
                _k = None
                log_line(root, now.date(), "[FreezeSentinel] %s 강제 재기동 판정 예외(%s: %s) — 알림만 계속"
                         % (now.strftime("%Y-%m-%d %H:%M:%S"), type(exc).__name__, exc))
            if _k is not None and _k["decision"]["kill"] and not _k["done"]:
                log_line(root, now.date(), "[FreezeSentinel] %s 강제 재기동 보류 — %s"
                         % (now.strftime("%Y-%m-%d %H:%M:%S"), _k["decision"]["reason"]))
            elif _k is not None and not _k["decision"]["kill"] and _k["target"] is not None:
                log_line(root, now.date(), "[FreezeSentinel] %s 강제 재기동 보류 — %s"
                         % (now.strftime("%Y-%m-%d %H:%M:%S"), _k["decision"]["reason"]))
            if _k is not None and _k["done"]:
                emit(root, now.date(), _k["decision"]["verdict"], popup=False, manual=False)
                log_line(root, now.date(), "[FreezeSentinel] %s 🔴 강제 재기동 %s — %s · %s"
                         % (now.strftime("%Y-%m-%d %H:%M:%S"), "실행" if _k["ok"] else "실패",
                            _k["decision"]["reason"], _k["msg"]))
                if mail_on:
                    _s, _b = build_kill_mail(_k["decision"], _k["target"], _k["ok"], _k["msg"],
                                             pc, now, _k["position"])
                    send_mail_async(root, now.date(), _s, _b, slack_too=slack_too)
                if not alerted:
                    alerted_at = now
                alerted = True
                time.sleep(check)
                continue
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
            if not alerted:
                alerted_at = now
                if mail_on and _pm == "OPEN":
                    # [S-05] 오늘 기동 자체가 없었다 — 이미 「장전 미기동」으로 알렸다.
                    #   어제 남은 하트비트 때문에 「동결」로 한 통 더 가지 않게 한다.
                    log_line(root, now.date(), "[FreezeSentinel] %s 동결 메일 생략 — S-05 미기동 "
                             "에피소드 진행 중" % now.strftime("%Y-%m-%d %H:%M:%S"))
                elif mail_on:
                    # 같은 동결의 반복 주기에는 보내지 않는다 — 팝업과 같은 경보 피로 규칙.
                    _s, _b = build_alert_mail(verdict, pc, now, stall)
                    send_mail_async(root, now.date(), _s, _b, slack_too=slack_too)
            alerted = True
        elif verdict["level"] == "OK" and alerted:
            alerted = False
            log_line(root, now.date(),
                     "[FreezeSentinel] %s 회복 — 신호가 다시 신선해졌다"
                     % now.strftime("%Y-%m-%d %H:%M:%S"))
            if mail_recover:
                _s, _b = build_recovery_mail(pc, alerted_at, now)
                send_mail_async(root, now.date(), _s, _b, slack_too=slack_too)
            alerted_at = None
        time.sleep(check)


if __name__ == "__main__":
    sys.exit(main())
