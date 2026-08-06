# -*- coding: utf-8 -*-
"""Cybos 세션 계좌 대조 - 설정 계좌가 브로커 세션에 실제로 있는지 확인한다.

[왜 필요한가 - 2026-08-06 사고]
로그인 성공 판정이 `IsConnect == 1` 하나였다. 그래서 "연결은 됐지만 엉뚱한
계좌에 붙은" 세션을 아무도 걸러내지 못했고, 미륵이가 설정 계좌(333042073)가
아닌 555011215 에 붙어 91분간 운영됐다(잔고 0 → 증거금 부족으로 진입 8건 차단).
`cybos_autologin.py` 는 "이미 연결됨 → 로그인 생략" 이라 그 세션을 스스로
복구하지도 못했다. 이 스크립트는 그 판정에 계좌 축을 추가한다.

    세션 정상 = IsConnect == 1  그리고  secrets.ACCOUNT_NO ∈ CpTdUtil.AccountNumber

[2단계 검사 - TradeInit 을 함부로 부르지 않는다]
계좌 목록을 읽으려면 `TradeInit` 이 필수인데, 2026-08-06 실서버 세션에서 이
호출이 CPTRADE 창을 띄운 채 120초를 넘겨 멈추는 것을 실측했다(모의서버에서는
같은 호출이 15ms 에 반환). 그래서:

    Stage 1  IsConnect != 1  -> 즉시 exit 1.  **TradeInit 을 호출하지 않는다**
    Stage 2  연결됐을 때만 TradeInit + AccountNumber

덕분에 이 스크립트를 폴링 루프에서 반복 호출해도 미연결 구간에서는
TradeInit 이 한 번도 실행되지 않는다.

[워치독]
COM 이 블로킹하면 예외도 sys.exit 도 먹지 않는다(위 실측에서 외부 강제종료가
필요했다). 데몬 타이머로 os._exit 를 걸어 반드시 빠져나온다.

Exit codes:
    0 = 계좌 일치
    1 = 미연결 (IsConnect != 1)        -- TradeInit 미호출
    2 = TradeInit 실패
    3 = COM 예외 / 환경 오류 (32비트 아님, secrets 없음 등)
    4 = 연결됐으나 설정 계좌가 세션 목록에 없음
    5 = 워치독 타임아웃 (판정 불능)

판정 불능(2·3·5)은 전부 실패로 처리한다 - "확인 못 했으니 통과"는 위 사고를
그대로 재현하는 정책이다.
"""
from __future__ import print_function

import argparse
import os
import struct
import sys
import threading

EXIT_OK = 0
EXIT_NOT_CONNECTED = 1
EXIT_TRADEINIT_FAILED = 2
EXIT_COM_ERROR = 3
EXIT_ACCOUNT_MISMATCH = 4
EXIT_TIMEOUT = 5

DEFAULT_TIMEOUT_SEC = 20

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)


# ── 순수 함수 (COM 무관 - 단위테스트 대상) ────────────────────────────────
# 정규화 규칙은 런타임과 **문자 단위로 동일해야 한다**. 어긋나면 오탐으로
# 아침 기동이 죽는다. 기준: strategy/runtime/broker_runtime_service.py
# `_select_account` 및 main.py `_get_active_account_no`.
#   expected = str(secrets.ACCOUNT_NO or "").strip()
#   accounts = [str(x).strip() for x in (raw or []) if str(x).strip()]
# 상품관리구분코드('-50', secrets.ACCOUNT_GOODS_CODE)는 비교 대상이 아니다.

def normalize_expected(value):
    """설정 계좌번호 정규화."""
    return str(value if value is not None else "").strip()


def normalize_accounts(raw):
    """브로커 계좌목록 정규화 - 공백 제거 후 빈 항목 탈락."""
    out = []
    try:
        items = list(raw or [])
    except TypeError:
        return out
    for item in items:
        text = str(item if item is not None else "").strip()
        if text:
            out.append(text)
    return out


def is_account_ok(expected, accounts):
    """설정 계좌가 세션 목록에 있는가.

    **목록이 비면 False 다** - 런타임(`_get_active_account_no`)과 의도적으로
    다른 지점이다. 런타임은 장중 매매를 세우지 않으려 관대하지만, 런처는
    기동 시점이라 엄격해도 손해가 없다. 판정 불능은 실패로 본다.
    """
    return bool(accounts) and bool(expected) and expected in accounts


# ── 워치독 ────────────────────────────────────────────────────────────────
def make_output_safe():
    """진단 출력이 콘솔 인코딩 때문에 죽지 않게 한다.

    [2026-08-06] 이 파일을 처음 쓸 때 안내문에 em-dash(U+2014)를 넣었다가
    cp949 콘솔에서 UnicodeEncodeError 가 났다. 그 자체도 문제지만 진짜 위험은
    **안전 검사의 종료코드가 바뀌는 것**이다 - exit 2(TradeInit 실패)나
    exit 4(계좌 불일치)를 돌려줘야 할 자리에서 트레이스백으로 죽으면 런처가
    전혀 다른 원인으로 오진한다. 문자 하나가 판정을 뒤집으면 안 된다.

    현재 두 파일 모두 cp949 로 인코딩 가능한 문자만 쓰지만, 나중에 누가 한 글자
    넣는 것만으로 재발할 수 있으므로 경로 자체를 막아둔다.
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")   # py3.7+
        except Exception:
            pass


def print_tradeinit_hint():
    """TradeInit 실패/블로킹의 알려진 원인 안내.

    [2026-08-06 실측] 실서버 세션에서 TradeInit(0) 이 ret=-1 로 실패했고, 그때
    CYBOS Plus 가 아래 모달을 띄웠다:

        CPTRADE - "주문오브젝트 사용 동의를 하지 않으셨습니다.
                   주문오브젝트 사용동의는 Plus 도움말의 주문오브젝트를 참고하시기 바랍니다."

    이 모달은 **클릭할 때까지 무한 대기**한다. 같은 날 아침 preflight 가 120초를
    넘겨 멈춘 것도 동일 원인이었다(무인 기동이라 아무도 확인을 누르지 않았다).
    워치독이 필요한 이유가 바로 이것이다 - 모달은 timeout 이 없다.
    """
    sys.stdout.write(
        "[HINT] TradeInit 실패/무응답의 가장 흔한 원인은 **주문오브젝트 사용 동의 미설정**입니다.\n"
        "       CYBOS Plus 에서 'CPTRADE - 주문오브젝트 사용 동의를 하지 않으셨습니다' 모달이\n"
        "       떠 있으면 그것입니다. 이 모달은 클릭 전까지 무한 대기하므로 무인 기동을 막습니다.\n"
        "       조치: CYBOS Plus 도움말 > 주문오브젝트 > 사용 동의 설정 후 재로그인.\n"
        "[HINT] 모의투자 세션에서는 동의가 이미 되어 있어 TradeInit 이 즉시(15ms) 성공합니다 -\n"
        "       실서버 세션에서만 이 오류가 난다면 그쪽 동의가 빠진 것입니다.\n"
    )
    sys.stdout.flush()


def arm_watchdog(timeout_sec, exit_code=EXIT_TIMEOUT):
    """timeout_sec 후 프로세스를 강제 종료하는 데몬 타이머를 건다.

    os._exit 를 쓰는 이유: COM 블로킹 중에는 예외/sys.exit 가 동작하지 않는다.
    os._exit 는 버퍼를 flush 하지 않으므로 메시지를 먼저 직접 flush 한다.
    """
    def _fire():
        sys.stderr.write(
            "[TIMEOUT] %d초 내 응답 없음 - 판정 불능으로 종료합니다 "
            "(TradeInit 블로킹 추정).\n" % timeout_sec
        )
        sys.stderr.flush()
        sys.stdout.flush()
        os._exit(exit_code)

    timer = threading.Timer(timeout_sec, _fire)
    timer.daemon = True
    timer.start()
    return timer


# ── 본체 ──────────────────────────────────────────────────────────────────
def main(argv=None):
    parser = argparse.ArgumentParser(description="Cybos 세션 계좌 대조")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SEC,
                        help="워치독 타임아웃(초). 기본 %d" % DEFAULT_TIMEOUT_SEC)
    parser.add_argument("--expected", default=None,
                        help="설정 계좌 직접 지정(미지정 시 config/secrets.py 에서 로드)")
    args = parser.parse_args(argv)
    make_output_safe()

    if struct.calcsize("P") != 4:
        print("[ERROR] 32비트 Python 이 필요합니다. 현재=%d비트"
              % (struct.calcsize("P") * 8))
        return EXIT_COM_ERROR

    arm_watchdog(args.timeout)

    # ── 설정 계좌 로드 ────────────────────────────────────────────────
    expected = normalize_expected(args.expected)
    if not expected:
        if _ROOT not in sys.path:
            sys.path.insert(0, _ROOT)
        try:
            from config import secrets as _secrets
        except Exception as exc:
            print("[ERROR] config/secrets.py 를 읽을 수 없습니다: %s" % exc)
            return EXIT_COM_ERROR
        expected = normalize_expected(getattr(_secrets, "ACCOUNT_NO", ""))
    if not expected:
        print("[ERROR] 설정 계좌(config/secrets.py:ACCOUNT_NO)가 비어 있습니다.")
        return EXIT_COM_ERROR

    try:
        import win32com.client
    except Exception as exc:
        print("[ERROR] pywin32 임포트 실패: %s" % exc)
        return EXIT_COM_ERROR

    # ── Stage 1: 연결 확인 (TradeInit 호출 안 함) ─────────────────────
    try:
        cp = win32com.client.Dispatch("CpUtil.CpCybos")
        is_connect = int(cp.IsConnect)
        server_type = cp.ServerType
    except Exception as exc:
        print("[CHECK 1/2] COM Dispatch 실패: %s" % exc)
        return EXIT_COM_ERROR

    try:
        from config.constants import is_cybos_simulation
        server_label = "모의투자" if is_cybos_simulation(server_type) else "실서버"
    except Exception:
        server_label = "?"

    print("[CHECK 1/2] IsConnect=%d ServerType=%s(%s)"
          % (is_connect, server_type, server_label))
    if is_connect != 1:
        print("[FAIL] Cybos 세션이 연결돼 있지 않습니다 - 계좌 조회를 생략합니다.")
        return EXIT_NOT_CONNECTED

    # ── Stage 2: TradeInit + 계좌 조회 ────────────────────────────────
    trade_init_param = 1 if server_label == "모의투자" else 0
    try:
        trade = win32com.client.Dispatch("CpTrade.CpTdUtil")
        ret = trade.TradeInit(trade_init_param)
    except Exception as exc:
        print("[CHECK 2/2] TradeInit 예외: %s" % exc)
        print_tradeinit_hint()
        return EXIT_TRADEINIT_FAILED
    if ret not in (0, None):
        print("[CHECK 2/2] TradeInit(%d)=%s 실패" % (trade_init_param, ret))
        print_tradeinit_hint()
        return EXIT_TRADEINIT_FAILED

    try:
        accounts = normalize_accounts(trade.AccountNumber)
    except Exception as exc:
        print("[CHECK 2/2] AccountNumber 조회 예외: %s" % exc)
        return EXIT_TRADEINIT_FAILED

    print("[CHECK 2/2] TradeInit(%d)=%s 계좌목록=%s"
          % (trade_init_param, ret, accounts))

    if is_account_ok(expected, accounts):
        print("[PASS] 설정 계좌 %s 가 세션에 있습니다." % expected)
        return EXIT_OK

    # ── 불일치 ────────────────────────────────────────────────────────
    # 자동 채택하지 않는다. 계좌를 브로커 세션에 맞춰 갈아타던 폴백이
    # 2026-08-06 사고의 직접 원인이었고 그래서 제거됐다(main.py
    # `_get_active_account_no`). 갱신은 사용자가 직접 한다.
    print("[FAIL] 설정 계좌가 브로커 세션 목록에 없습니다.")
    print("       설정(config/secrets.py:ACCOUNT_NO) = %s" % expected)
    print("       브로커 세션 계좌목록               = %s"
          % (accounts if accounts else "(비어 있음 - 조회 실패 가능)"))
    print("[HINT] 모의계좌가 재발급된 경우 config/secrets.py 의 아래 3개 항목을")
    print("       새 계좌 정보로 직접 갱신하십시오:")
    print("           ACCOUNT_NO          = 앞 9자리 (예: 333-044256 -> \"333044256\")")
    print("           ACCOUNT_GOODS_CODE  = 뒤 2자리 상품관리구분코드 (선물 \"50\")")
    print("           ACCOUNT_PWD         = 계좌 비밀번호")
    print("[HINT] Cybos 로그인 ID 가 평소와 다른 경우에도 이 오류가 납니다 -")
    print("       그때는 secrets 를 고치지 말고 올바른 ID 로 재로그인하십시오.")
    return EXIT_ACCOUNT_MISMATCH


if __name__ == "__main__":
    sys.exit(main())
