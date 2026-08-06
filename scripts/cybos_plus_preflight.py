# -*- coding: utf-8 -*-
"""
Cybos Plus session preflight.

Exit codes:
    0 = all checks passed
    1 = COM connection failed
    2 = TradeInit failed
    3 = exception while dispatching COM
    4 = account mismatch (설정 계좌가 브로커 세션에 없음)   [2026-08-06 추가]
    5 = watchdog timeout (판정 불능)                       [2026-08-06 추가]

[2026-08-06] CHECK 4/4(계좌 대조)와 워치독 추가.
기존 preflight 는 "연결됐고 TradeInit 이 되면 통과"였다. 그래서 **엉뚱한 계좌에
붙은 세션도 그대로 통과**시켰고, 미륵이가 설정 계좌가 아닌 555011215 에 붙어
91분간 운영된 사고(2026-08-06)를 여기서 걸러내지 못했다. TradeInit 은 이미
호출하고 있으므로 AccountNumber 를 한 번 더 읽는 비용은 사실상 0이다.

워치독을 붙인 이유: 2026-08-06 실서버 세션에서 TradeInit 이 CPTRADE 창을 띄운 채
120초를 넘겨 멈추는 것을 실측했다(모의서버는 15ms). 이 스크립트는 아침 기동
체인 한복판이라 여기서 멈추면 그날 매매가 통째로 막힌다.
"""
import datetime
import os
import struct
import sys

if struct.calcsize("P") != 4:
    print("[ERROR] 32-bit Python is required, current=%d-bit" % (struct.calcsize("P") * 8))
    sys.exit(3)

import win32com.client

# 계좌 대조 로직은 check_cybos_account.py 단일 출처를 쓴다(같은 디렉터리).
# 정규화 규칙이 런타임과 어긋나면 오탐으로 아침 기동이 죽으므로 복제하지 않는다.
# config/secrets.py 를 읽으려면 프로젝트 루트도 필요하다.
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (_HERE, _ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from check_cybos_account import (          # noqa: E402
    arm_watchdog, normalize_expected, normalize_accounts, is_account_ok,
    print_tradeinit_hint, make_output_safe, EXIT_ACCOUNT_MISMATCH, EXIT_TIMEOUT,
)

WATCHDOG_SEC = 20


def main():
    make_output_safe()
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("[%s] Cybos Plus Preflight Check start" % ts)
    arm_watchdog(WATCHDOG_SEC, EXIT_TIMEOUT)

    try:
        cp = win32com.client.Dispatch("CpUtil.CpCybos")
        is_connect = cp.IsConnect
        server_type = cp.ServerType
    except Exception as exc:
        print("[CHECK 1/4] COM Dispatch failed: %s" % exc)
        sys.exit(3)

    print("[CHECK 1/4] IsConnect=%d  %s" % (
        is_connect, "connected" if is_connect == 1 else "disconnected"))
    if is_connect != 1:
        print("[ERROR] Cybos Plus COM is not connected.")
        sys.exit(1)

    print("[CHECK 2/4] ServerType=%s" % server_type)

    # [2026-08-06] 판정이 반대로 적혀 있던 것을 실측으로 교정.
    # 실서버 접속 상태에서 직접 조회한 결과 ServerType=2 → 1=모의 / 2=실서버.
    # 기존 코드는 `== 2`를 모의로 봐서 **실서버를 "Mock server"로 기록**했다.
    # 표준 출처: config/constants.py:is_cybos_simulation (여기선 preflight의
    # 무의존성을 지키려 리터럴을 두되, 값이 바뀌면 그쪽과 함께 고칠 것).
    trade_init_param = 0
    try:
        is_mock = int(server_type) == 1
    except (TypeError, ValueError):
        # 판정 불능 시 실서버로 간주한다 - 모의로 오판하면 실자금이 위험하다.
        is_mock = False
    if is_mock:
        trade_init_param = 1
        print("[CHECK 3/4] Mock server detected (ServerType=%s) -- TradeInit(1)" % server_type)
    else:
        print("[CHECK 3/4] Real server detected (ServerType=%s) -- TradeInit(0)" % server_type)

    try:
        trade = win32com.client.Dispatch("CpTrade.CpTdUtil")
        ret = trade.TradeInit(trade_init_param)
    except Exception as exc:
        print("[CHECK 3/4] TradeInit exception: %s" % exc)
        print_tradeinit_hint()
        sys.exit(2)

    print("[CHECK 3/4] TradeInit(%d)=%s  %s" % (
        trade_init_param, ret, "success" if ret in (0, None) else "failed"))
    if ret not in (0, None):
        print("[ERROR] TradeInit failed with ret=%s" % ret)
        print_tradeinit_hint()
        sys.exit(2)

    # ── CHECK 4/4: 계좌 대조 ──────────────────────────────────────────
    # 설정 계좌(config/secrets.py:ACCOUNT_NO)가 이 세션에 실제로 있는지 본다.
    # 없다면 로그인 ID 가 평소와 다르거나 모의계좌가 재발급된 것이며, 그대로
    # 기동하면 잘못된 세션 위에서 하루를 보내게 된다(2026-08-06 사고).
    try:
        from config import secrets as _secrets          # noqa: E402
        expected = normalize_expected(getattr(_secrets, "ACCOUNT_NO", ""))
    except Exception as exc:
        print("[CHECK 4/4] config/secrets.py 로드 실패: %s" % exc)
        sys.exit(3)

    if not expected:
        print("[CHECK 4/4] 설정 계좌(config/secrets.py:ACCOUNT_NO)가 비어 있습니다.")
        sys.exit(3)

    try:
        accounts = normalize_accounts(trade.AccountNumber)
    except Exception as exc:
        print("[CHECK 4/4] AccountNumber 조회 예외: %s" % exc)
        sys.exit(2)

    print("[CHECK 4/4] 계좌목록=%s  설정=%s" % (accounts, expected))
    if not is_account_ok(expected, accounts):
        # 자동 채택하지 않는다 - 브로커 세션에 맞춰 계좌를 갈아타던 폴백이
        # 2026-08-06 사고의 직접 원인이었고 이미 제거됐다(main.py).
        print("[ERROR] 설정 계좌가 브로커 세션 목록에 없습니다.")
        print("        설정(config/secrets.py:ACCOUNT_NO) = %s" % expected)
        print("        브로커 세션 계좌목록               = %s"
              % (accounts if accounts else "(비어 있음 - 조회 실패 가능)"))
        print("[HINT]  모의계좌가 재발급된 경우 config/secrets.py 의 아래 3개 항목을")
        print("        새 계좌 정보로 직접 갱신하십시오:")
        print("            ACCOUNT_NO          = 앞 9자리 (예: 333-044256 -> \"333044256\")")
        print("            ACCOUNT_GOODS_CODE  = 뒤 2자리 상품관리구분코드 (선물 \"50\")")
        print("            ACCOUNT_PWD         = 계좌 비밀번호")
        print("[HINT]  Cybos 로그인 ID 가 평소와 다른 경우에도 이 오류가 납니다 -")
        print("        그때는 secrets 를 고치지 말고 올바른 ID 로 재로그인하십시오.")
        sys.exit(EXIT_ACCOUNT_MISMATCH)

    print("[PASS] All preflight checks passed (%s)" % (
        datetime.datetime.now().strftime("%H:%M:%S")))
    sys.exit(0)


if __name__ == "__main__":
    main()
