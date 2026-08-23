# -*- coding: utf-8 -*-
"""분석 스크립트용 라이브 DB 접근 가드 (456차 / Wave 0 · F8).

## 왜 필요한가 — 2026-08-10 실측

13:47:08 파이프라인 **7,619ms**로 CB⑤(임계 5,000ms)가 발동해 5분간 신규 진입이
정지됐다. 포지션이 FLAT이라 실손해는 없었으나, 원인은 시장이 아니라 **점검 세션이
장중에 라이브 DB를 전수 스캔한 것**이었다.

지연 프로파일이 원인을 특정한다:

| 시각 | total | 프로파일 | 해석 |
|---|---|---|---|
| 09:42·10:37·11:50·13:23 | 3.2~3.9s | `S0 ≈ 3,100ms` 단독 | 장중 재학습 직후 모델 리로드 (정례) |
| **13:47:07** | **7,619ms** | `S0=3ms` / **S1=3,098 · S4=1,951** · S2=305 · S7=749 · S8=525 | DB 접근 단계가 **동시** 지연 |

S0(모델 로드)은 멀쩡한데 DB를 만지는 단계만 전부 느려졌다.

## 메커니즘 — 잠금 경합이 **아니다**

처음엔 SQLite 잠금 경합을 의심했으나 실측으로 반증됐다:

    raw_data.db     journal_mode=wal   468 MB
    predictions.db  journal_mode=wal   835 MB

**WAL 모드에서는 읽기가 쓰기를 막지 않는다.** 따라서 `mode=ro`나 `busy_timeout`으로는
이 지연을 막을 수 없다 — 원인은 **IO 대역폭과 OS 페이지 캐시 압박**이다. 1.3GB짜리 두
테이블에서 큰 JSON 페이로드를 통째로 긁으면 라이브 파이프라인이 쓰던 캐시가 밀려난다.

그래서 이 모듈은 **접속 옵션이 아니라 실행 시점을 막는다.**
`connect_ro()`의 읽기전용은 지연 대책이 아니라 *실수로 라이브 DB에 쓰는 것*을 막는
별개의 안전장치다 — 두 목적을 섞어 이해하지 말 것.

## 사용법

    from utils.analysis_db import guard_intraday, connect_ro

    def main():
        guard_intraday("core_feature_discovery")   # 장중이면 여기서 종료
        con = connect_ro(RAW_DB)

장중에 꼭 돌려야 하면 환경변수로 명시적 동의를 남긴다(무단 우회 방지):

    MIREUK_ALLOW_INTRADAY_ANALYSIS=1 python scripts/core_feature_discovery.py

근거: `docs/정기점검/매일점검/MW0601-20260810-점검리포트.md` §3-2 / F8,
`docs/정기점검/매일점검/0810_Fix_고도화_통합구현계획_MW0601.md` Wave 0.
"""
from __future__ import print_function

import os
import sqlite3
import sys

ALLOW_ENV = "MIREUK_ALLOW_INTRADAY_ANALYSIS"

#: guard_intraday()가 장중에 종료할 때 쓰는 종료코드.
#: 0(정상)·1(예외)과 구분해 EOD 체인이 "정책상 스킵"을 식별할 수 있게 한다.
EXIT_INTRADAY_BLOCKED = 2


def is_live_window(dt=None):
    """라이브 파이프라인 활성 구간 여부 (프리장 08:45 ~ 본장 마감).

    `utils.time_utils.is_trading_session()`을 그대로 쓴다 — 공휴일·만기일 조기마감을
    이미 처리하는 단일 진실원이다. 여기서 시각을 다시 정의하면 두 번째 진실원이 된다.

    time_utils import 실패 시(경량 환경) **False를 반환하지 않는다** — 판단 불가를
    차단 실패로 바꾸면 가드가 조용히 무력화된다. 평일 08:45~15:35로 보수 폴백한다.
    """
    try:
        from utils.time_utils import is_trading_session
        return bool(is_trading_session(dt))
    except Exception:
        import datetime
        if dt is None:
            dt = datetime.datetime.now()
        if dt.weekday() >= 5:
            return False
        return datetime.time(8, 45) <= dt.time() <= datetime.time(15, 35)


def guard_intraday(script_name, dt=None, exit_on_block=True):
    """장중이면 경고 후 종료. 장외면 아무것도 하지 않는다.

    Args:
        script_name: 경고에 표시할 스크립트 이름.
        dt: 판정 시각(테스트용). None이면 현재.
        exit_on_block: False면 종료하지 않고 bool만 반환(테스트/호출자 판단용).

    Returns:
        bool — 차단 대상이면 True.
    """
    # 이 경고문 자체가 cp949로 못 쓰는 문자를 담고 있다(U+2014 등). 콘솔을 먼저 열지
    # 않으면 "장중 실행을 막는 경고"가 UnicodeEncodeError로 죽는다 — 2026-08-10
    # core_feature_discovery 크래시와 같은 실패 양식이다.
    utf8_console()

    if not is_live_window(dt):
        return False

    if os.environ.get(ALLOW_ENV, "").strip() not in ("", "0", "false", "False"):
        print(
            "[AnalysisGuard] %s — 장중이지만 %s=1 로 명시 허용됨. "
            "라이브 파이프라인 지연(CB⑤) 위험을 감수하고 진행한다."
            % (script_name, ALLOW_ENV),
            file=sys.stderr,
        )
        return False

    print(
        "\n".join([
            "",
            "=" * 72,
            "[AnalysisGuard] 장중 실행 차단 — %s" % script_name,
            "=" * 72,
            "  라이브 파이프라인이 동작 중입니다(프리장 08:45 ~ 본장 마감).",
            "  이 스크립트는 라이브 DB를 대량 읽으므로 IO·페이지캐시 경합으로",
            "  파이프라인을 지연시켜 CB⑤(5초 초과)를 유발할 수 있습니다.",
            "",
            "  2026-08-10 13:47 실측: 파이프라인 7,619ms → 신규 진입 5분 정지.",
            "",
            "  조치: 장 마감 후(15:35 이후) 실행하십시오.",
            "  꼭 지금 실행해야 하면:  set %s=1" % ALLOW_ENV,
            "=" * 72,
            "",
        ]),
        file=sys.stderr,
    )
    if exit_on_block:
        sys.exit(EXIT_INTRADAY_BLOCKED)
    return True


def connect_ro(db_path, timeout=5.0):
    """읽기전용 커넥션. 실패 시 일반 커넥션으로 폴백한다.

    ⚠ **지연 대책이 아니다.** WAL 모드에서 읽기는 쓰기를 막지 않으므로 읽기전용은
    파이프라인 지연과 무관하다. 목적은 분석 스크립트가 **실수로 라이브 DB에 쓰는 것**을
    막는 것뿐이다.

    폴백이 필요한 이유: WAL DB를 `mode=ro`로 열려면 `-shm` 파일이 이미 있거나 디렉터리에
    쓰기 권한이 있어야 한다. 라이브 프로세스가 죽은 뒤에는 `-shm`이 정리돼 실패할 수
    있는데, 그때 분석이 통째로 막히면 안 된다.
    """
    uri = "file:%s?mode=ro" % db_path.replace("?", "%3f").replace("#", "%23")
    try:
        con = sqlite3.connect(uri, uri=True, timeout=timeout)
        con.execute("SELECT 1")          # 실제 접근 가능 여부 확인
        return con
    except sqlite3.Error as exc:
        print(
            "[AnalysisGuard] 읽기전용 열기 실패(%s) → 일반 커넥션으로 폴백: %s"
            % (exc, os.path.basename(db_path)),
            file=sys.stderr,
        )
        return sqlite3.connect(db_path, timeout=timeout)


def lower_priority():
    """프로세스 우선순위를 낮춘다(최선 노력). 실패해도 무해.

    장중 명시 허용(`MIREUK_ALLOW_INTRADAY_ANALYSIS=1`) 경로에서 라이브 프로세스에
    CPU를 양보하기 위한 것이다. psutil이 없으면 조용히 넘어간다.
    """
    try:
        import psutil
        p = psutil.Process()
        if sys.platform == "win32":
            p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
            try:
                p.ionice(psutil.IOPRIO_VERYLOW)
            except Exception:
                pass
        else:
            p.nice(10)
        return True
    except Exception:
        return False


def utf8_console():
    """cp949 콘솔 인코딩 가드 — CLI 실행 시에만 호출할 것.

    455차가 `horizon_signal_tradability.py`·`ic_decay_catalog.py`에 넣은 `_utf8_console()`과
    동일 구현이다. 그 둘이 import 하는 **base 모듈(`core_feature_discovery`)에는 빠져
    있어서** 2026-08-10 `UnicodeEncodeError`로 죽었다(cp949가 `≈`를 못 쓴다).
    여기 모아 세 스크립트가 같은 것을 쓰게 한다.

    ⚠ import 시점에 부르지 말 것 — 중첩 래퍼로 출력이 유실된다.
    """
    for stream in ("stdout", "stderr"):
        try:
            getattr(sys, stream).reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
