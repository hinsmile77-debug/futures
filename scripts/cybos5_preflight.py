# -*- coding: utf-8 -*-
"""
Cybos5 세션 사전 검증 스크립트

CYBOS5.bat에서 호출:
    python scripts\cybos5_preflight.py

종료 코드:
    0 = 모든 체크 통과
    1 = COM 연결 실패 (IsConnect != 1)
    2 = TradeInit 실패
    3 = COM Dispatch 예외 발생
"""
import sys
import struct
import datetime

if struct.calcsize("P") != 4:
    print("[ERROR] 32-bit Python 필요 -- 현재 %d-bit" % (struct.calcsize("P") * 8))
    sys.exit(3)

import win32com.client

# ---------------------------------------------------------------------------
def main():
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("[%s] Cybos5 Preflight Check 시작" % ts)

    # ── CHECK 1/3: COM 연결 ──
    try:
        c = win32com.client.Dispatch("CpUtil.CpCybos")
        is_connect = c.IsConnect
        server_type = c.ServerType
    except Exception as e:
        print("[CHECK 1/3] COM Dispatch 실패: %s" % e)
        sys.exit(3)

    print("[CHECK 1/3] IsConnect=%d  %s" % (
        is_connect, "✓ 연결됨" if is_connect == 1 else "✗ 미연결"))

    if is_connect != 1:
        print("[ERROR] Cybos5 COM 연결 안 됨 -- HTS 실행 상태 확인 필요")
        sys.exit(1)

    # ── CHECK 2/3: ServerType ──
    print("[CHECK 2/3] ServerType=%s" % server_type)

    # ── CHECK 3/3: TradeInit ──
    # ServerType: 정수 2 = 모의투자, 1 = 실거래 (문자열 "모의" 포함 여부도 fallback 허용)
    trade_init_param = 0  # 기본값: 실거래
    try:
        is_mock = (int(server_type) == 2)
    except (TypeError, ValueError):
        is_mock = server_type is not None and u"모의" in str(server_type)
    if is_mock:
        print("[CHECK 3/3] ServerType=%s (모의투자) -- TradeInit(1) 사용" % server_type)
        trade_init_param = 1
    else:
        print("[CHECK 3/3] ServerType=%s (실거래) -- TradeInit(%d) 시도" % (server_type, trade_init_param))

    try:
        t = win32com.client.Dispatch("CpTrade.CpTdUtil")
        ret = t.TradeInit(trade_init_param)
    except Exception as e:
        print("[CHECK 3/3] TradeInit 예외 발생: %s" % e)
        sys.exit(2)

    print("[CHECK 3/3] TradeInit(%d)=%d  %s" % (
        trade_init_param, ret, "✓ 성공" if ret in (0, None) else "✗ 실패"))

    if ret not in (0, None):
        print("[ERROR] TradeInit 실패 (ret=%d) -- 모의/실거래 서버 타입 확인 필요" % ret)
        sys.exit(2)

    # ── 통과 ──
    print("[PASS] 모든 Preflight 체크 통과 (%s)" % (
        datetime.datetime.now().strftime("%H:%M:%S")))
    sys.exit(0)


if __name__ == "__main__":
    main()