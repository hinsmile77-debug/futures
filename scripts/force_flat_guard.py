# -*- coding: utf-8 -*-
"""[MW0601 480차 / F-2] 15:12 프로세스 밖 FLAT 가드 — 절대원칙 §1의 최후 방어선.

## 왜 별개 프로세스인가

절대원칙 §1(15:10 강제청산)의 방어선은 셋인데 **전부 같은 프로세스 안**에 있다:

    STEP 8 청산 감시  →  _ts_scheduler_force_exit_net(453차 D2)  →  15:18 안전망

2026-08-19 13:41:21, 메인(Qt) 스레드가 네이티브 스핀에 빠지자 이 셋이 **동시에**
죽었다. 프로세스는 살아 있어 런처 RESTART_LOOP도 재기동하지 않았고, 15:10·15:18·
15:40 앵커가 전부 무흔적으로 지나갔다. 그날 포지션이 FLAT이었던 것은 설계가 아니라
**우연이다** — 18분 전인 13:23:31에 마지막 포지션이 닫혔을 뿐이다.

FZ-1 워치독(478차 후속)이 이 구멍의 **15:10 이전** 구간을 메운다(하드 종료 → 런처
재기동 → 세션 복원). 그러나 FZ-1은 스스로 적고 있듯 *"15:10 이후 발화면 런처가
재기동하지 않는다"*(오버나이트 금지 정책). **15:10~15:35 구간은 여전히 비어 있고,
그 구간이 정확히 §1의 집행 시각이다.** 이 스크립트가 그 구간을 본다.

## 무엇을 하고, 무엇을 하지 않는가

한다:  ① 하트비트 파일로 라이브 프로세스 생존 판정  ② `position_state.json`으로
       미청산 판정  ③ 로그·마커 파일·(옵션)메시지박스로 **경보**

하지 않는다: **주문**. 별도 프로세스가 브로커에 청산 주문을 넣으면 이중 청산·수량
불일치 위험이 있다(`FORCE_FLAT_GUARD_ORDER_ENABLED`는 자리만 있고 구현이 없다).
승격 여부는 주간회의 안건이다.

## 왜 DB를 읽지 않는가

판정 시각 15:12는 **장중**이다(CLAUDE.md "장중 라이브 DB 분석 금지" 08:45~15:35).
2026-08-10에 점검 세션의 DB 전수 스캔이 파이프라인을 7,619ms로 늘려 CB⑤를
자가유발한 전례가 있다. 그래서 이 가드는 **작은 JSON 파일 2개만** 읽는다 —
`trades.db`조차 열지 않는다. 안전장치가 새 사고를 만드는 것이 여기서 가장 피해야
할 결과다.

## 사용법

    python scripts/force_flat_guard.py            # 15:12까지 대기 후 1회 판정
    python scripts/force_flat_guard.py --once     # 즉시 1회 판정(점검·리허설용)
    python scripts/force_flat_guard.py --at 15:12 --once

런처(`start_mireuk.bat`)가 main.py 기동 직전에 사이드카로 띄운다. 종료코드:

    0  정상(FLAT 확인)            3  🔴 미청산 경보
    4  프로세스 정지(FLAT)        5  판정 불가(입력 결손)  6  비거래일·대상 아님

근거: `docs/정기점검/매일점검/MW0601-20260819-점검리포트-post.md` §2 F-2,
      `MW0601-20260819-미종료-딥다이브.md` §5 P0-1.
"""
from __future__ import print_function

import argparse
import datetime
import json
import os
import subprocess
import sys
import time

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

RC_OK = 0
RC_UNCLOSED = 3
RC_PROCESS_DEAD = 4
RC_UNKNOWN = 5
RC_NOT_APPLICABLE = 6


# ── 판정 (순수 함수 — 테스트가 여기를 고정한다) ────────────────────────────

def judge(now, heartbeat, position, stale_sec=180.0):
    """가드 판정. 파일 IO 없이 값만 본다.

    Args:
        now:       판정 시각(datetime).
        heartbeat: 하트비트 JSON dict. **파일이 없으면 None** — "없음"과
                   "낡음"은 다른 사실이므로 같은 값으로 뭉개지 않는다(계측 4원칙 ②).
        position:  `data/position_state.json` dict. 없으면 None.
        stale_sec: 하트비트가 이보다 낡으면 라이브 프로세스가 멈춘 것으로 본다.

    Returns:
        dict(level, rc, headline, details[])

    판정 우선순위는 **위험이 큰 쪽이 이긴다**:
      ① 미청산 + 프로세스 정지 → CRITICAL (아무도 닫아줄 수 없다)
      ② 미청산 + 프로세스 생존 → CRITICAL (15:10을 이미 2분 넘겼다)
      ③ FLAT   + 프로세스 정지 → WARNING  (오늘은 무해하나 구멍은 열려 있다)
      ④ 입력 결손              → UNKNOWN  (조용히 OK로 넘기지 않는다)
      ⑤ FLAT   + 프로세스 생존 → OK
    """
    details = []

    # ── 하트비트 나이 ──
    beat_age = None
    alive = None            # True/False/None(판정불가)
    if heartbeat is None:
        details.append("하트비트 파일 없음 — 라이브 프로세스 생존 판정 불가 "
                       "(FREEZE_WATCHDOG_HEARTBEAT_FILE 확인)")
    else:
        wa = heartbeat.get("written_at")
        try:
            written = datetime.datetime.strptime(str(wa)[:19], "%Y-%m-%dT%H:%M:%S")
        except (ValueError, TypeError):
            written = None
        if written is None:
            details.append("하트비트 written_at 파싱 불가: %r" % (wa,))
        else:
            beat_age = (now - written).total_seconds()
            # 워치독 자신이 본 이벤트 루프 나이도 함께 본다. 파일은 최신인데
            # beat_age_sec이 큰 상태 = 워치독은 살아 있고 메인만 죽은 것이다.
            loop_age = heartbeat.get("beat_age_sec")
            alive = (beat_age <= stale_sec) and not (
                loop_age is not None and float(loop_age) > stale_sec
            )
            details.append(
                "하트비트: 파일 %.0fs 전 기록 · 이벤트루프 나이 %s · pid=%s · strikes=%s"
                % (beat_age,
                   "미측정" if loop_age is None else "%.0fs" % float(loop_age),
                   heartbeat.get("pid"), heartbeat.get("strikes"))
            )
            if not alive:
                details.append("→ 임계 %.0fs 초과 — 라이브 프로세스가 멈춘 것으로 본다"
                               % stale_sec)

    # ── 포지션 ──
    unclosed = None
    if position is None:
        details.append("position_state.json 없음 — 미청산 판정 불가")
    else:
        status = str(position.get("status") or "").upper()
        qty = position.get("quantity") or 0
        try:
            qty = int(qty)
        except (TypeError, ValueError):
            qty = 0
        unclosed = (status not in ("", "FLAT")) or qty > 0
        details.append(
            "포지션: status=%s qty=%s · 최종갱신=%s (%s)"
            % (status or "(공란)", qty,
               position.get("last_update_ts"), position.get("last_update_reason"))
        )
        # 파일이 오늘 것이 아닌데 FLAT이면 정상이다 — 이 파일은 포지션이 바뀔 때만
        # 갱신되므로, 오늘 거래가 없었으면 어제 청산 상태 그대로 남는다.
        saved = str(position.get("saved_at") or "")[:10]
        if saved and saved != now.strftime("%Y-%m-%d"):
            details.append("→ 파일 날짜가 오늘이 아니다(%s). FLAT이면 정상(오늘 진입 없음), "
                           "FLAT이 아니면 전일 포지션 잔류다" % saved)

    # ── 결론 ──
    if unclosed:
        if alive is False:
            return {
                "level": "CRITICAL", "rc": RC_UNCLOSED,
                "headline": "미청산 포지션 + 라이브 프로세스 정지 — "
                            "아무도 닫아줄 수 없다. 절대원칙 §1 즉시 개입 필요",
                "details": details,
            }
        return {
            "level": "CRITICAL", "rc": RC_UNCLOSED,
            "headline": "15:10 강제청산 이후에도 포지션이 남아 있다 — 절대원칙 §1 확인 필요",
            "details": details,
        }
    if alive is False:
        return {
            "level": "WARNING", "rc": RC_PROCESS_DEAD,
            "headline": "라이브 프로세스 정지(포지션은 FLAT) — 오늘 실손해는 없으나 "
                        "15:40 일일마감·EOD 체인이 실행되지 않는다",
            "details": details,
        }
    if alive is None or unclosed is None:
        return {
            "level": "UNKNOWN", "rc": RC_UNKNOWN,
            "headline": "판정에 필요한 입력이 없다 — 가드가 돌았지만 아무것도 보장하지 못했다",
            "details": details,
        }
    return {
        "level": "OK", "rc": RC_OK,
        "headline": "정상 — 포지션 FLAT · 라이브 프로세스 생존",
        "details": details,
    }


# ── 입출력 ────────────────────────────────────────────────────────────────

def _read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


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


def heartbeat_path(root, day, pc=None):
    try:
        from config.settings import FREEZE_WATCHDOG_HEARTBEAT_PATH as tpl
    except Exception:
        tpl = "data/heartbeat_{pc}_{date}.json"
    return os.path.join(root, tpl.format(pc=pc or _pc_id(), date=day.strftime("%Y%m%d")))


def emit(root, day, verdict, popup=True, manual=False):
    """경보를 남긴다 — 로그 · (경보 시)마커 파일 · (옵션)메시지박스.

    Slack은 쓰지 않는다(사용자 결정: 개발단계 직접 모니터링, feedback 메모 참조).
    마커 파일을 두는 이유는 일일 점검 수집기가 §1 인벤토리에서 자동으로 집어
    다음 점검에 눈에 띄게 하기 위해서다 — 사람이 그 시각에 화면을 보고 있지
    않아도 사실이 남는다.

    ⚠ `manual=True`(`--once` 수동 실행)면 **마커를 남기지 않는다.** 점검 중에 손으로
    돌린 진단이 다음날 증거 인벤토리에 "경보"로 섞이면, 진짜 15:12 발화와 구분되지
    않아 수집기가 거짓 적신호를 만든다(개발 중 실제로 그렇게 오염시켰다).
    콘솔과 로그에는 그대로 남으므로 정보가 사라지지는 않는다.
    """
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    body = ["[ForceFlatGuard] %s %s%s" % (stamp, verdict["level"],
                                          " (수동 실행 — 마커 미기록)" if manual else ""),
            "  " + verdict["headline"]]
    body += ["  · " + d for d in verdict["details"]]
    text = "\n".join(body)

    log_dir = os.path.join(root, "logs")
    try:
        os.makedirs(log_dir, exist_ok=True)
        with open(os.path.join(log_dir, "force_flat_guard_%s.log" % day.strftime("%Y%m%d")),
                  "a", encoding="utf-8", errors="replace") as f:
            f.write(text + "\n")
    except Exception as exc:
        print("[ForceFlatGuard] 로그 기록 실패: %s" % exc, file=sys.stderr)

    print(text)

    if not manual and verdict["level"] in ("CRITICAL", "WARNING", "UNKNOWN"):
        try:
            data_dir = os.path.join(root, "data")
            os.makedirs(data_dir, exist_ok=True)
            with open(os.path.join(data_dir, "force_flat_alert_%s.txt" % day.strftime("%Y%m%d")),
                      "a", encoding="utf-8", errors="replace") as f:
                f.write(text + "\n")
        except Exception as exc:
            print("[ForceFlatGuard] 마커 기록 실패: %s" % exc, file=sys.stderr)

    if popup and verdict["level"] == "CRITICAL":
        _popup(verdict)


def _popup(verdict):
    """트레이딩 PC 앞 사람에게 즉시 보이게 한다 — 이 시각에는 사람이 개입할 수 있다.

    별도 프로세스로 띄우고 기다리지 않는다. 실패는 삼킨다(경보 수단 하나가
    막혔다고 나머지 기록까지 잃으면 안 된다).
    """
    msg = (verdict["headline"] + "\n\n" + "\n".join(verdict["details"]))
    msg = msg.replace("'", "").replace('"', "")
    ps = (
        "Add-Type -AssemblyName PresentationFramework; "
        "[System.Windows.MessageBox]::Show('%s', "
        "'[Mireuk] 15:12 FLAT 가드 — 절대원칙 1', 'OK', 'Error')" % msg
    )
    try:
        subprocess.Popen(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
    except Exception as exc:
        print("[ForceFlatGuard] 팝업 실패(무해): %s" % exc, file=sys.stderr)


# ── 진입점 ────────────────────────────────────────────────────────────────

def _cfg(name, default):
    try:
        import config.settings as st
        return getattr(st, name, default)
    except Exception:
        return default


def main(argv=None):
    ap = argparse.ArgumentParser(description="15:12 프로세스 밖 FLAT 가드 (F-2)")
    ap.add_argument("--at", default=None, help="판정 시각 HH:MM (기본: FORCE_FLAT_GUARD_AT)")
    ap.add_argument("--once", action="store_true", help="대기 없이 즉시 1회 판정")
    ap.add_argument("--stale-sec", type=float, default=None,
                    help="하트비트 정지 판정 임계초 (기본: 설정값)")
    ap.add_argument("--no-popup", action="store_true", help="메시지박스 억제")
    ap.add_argument("--root", default=_ROOT)
    args = ap.parse_args(argv)

    # cp949 콘솔이 em dash(—)를 못 쓴다 — FZ-1이 같은 이유로 발화 기록을 통째로
    # 잃은 전례가 있다(478차 후속 §8-2). 경보 문구가 인코딩 때문에 사라지면
    # 이 가드는 아무것도 한 게 없다.
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
    at = args.at or _cfg("FORCE_FLAT_GUARD_AT", "15:12")
    stale = args.stale_sec if args.stale_sec is not None else _cfg(
        "FORCE_FLAT_GUARD_HEARTBEAT_STALE_SEC", 180.0)
    popup = (not args.no_popup) and bool(_cfg("FORCE_FLAT_GUARD_POPUP", True))

    if not _cfg("FORCE_FLAT_GUARD_ENABLED", True):
        print("[ForceFlatGuard] 설정 비활성(FORCE_FLAT_GUARD_ENABLED=False) — 종료")
        return RC_NOT_APPLICABLE

    now = datetime.datetime.now()
    try:
        from utils.time_utils import is_trading_day
        trading = is_trading_day(now)
    except Exception:
        trading = now.weekday() < 5
    if not trading:
        print("[ForceFlatGuard] 비거래일 — 판정 대상 아님")
        return RC_NOT_APPLICABLE

    if not args.once:
        hh, mm = [int(x) for x in str(at).split(":")]
        target = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
        if target < now:
            print("[ForceFlatGuard] 판정 시각 %s 이 이미 지났다 — 즉시 1회 판정" % at)
        else:
            print("[ForceFlatGuard] 대기 — %s 에 판정 (pid=%d)" % (at, os.getpid()))
            while datetime.datetime.now() < target:
                time.sleep(min(30.0, max(1.0, (target - datetime.datetime.now()).total_seconds())))
        now = datetime.datetime.now()

    day = now.date()
    hb = _read_json(heartbeat_path(root, day))
    pos = _read_json(os.path.join(root, "data", "position_state.json"))
    verdict = judge(now, hb, pos, stale_sec=stale)
    emit(root, day, verdict, popup=popup, manual=bool(args.once))
    return verdict["rc"]


if __name__ == "__main__":
    sys.exit(main())
