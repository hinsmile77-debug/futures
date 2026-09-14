# -*- coding: utf-8 -*-
"""[MW0601 561차] `CpSysDib.FutureJpBid` **미사용 필드 대역** 프로브.

왜 필요한가
-----------
561차 딥다이브에서 단위(계약 수 = 잔량)는 세 가지 간접 근거로 확인했다.

  1. 가격 단조성 — 매도 2~6 오름차순 / 매수 19~23 내림차순 ⇒ 가격 축 매핑이 맞다
  2. Cybos 는 **잔량과 건수를 별도 필드로 준다**(`FutOptRest` 사례)
  3. 5단 합 > 1단 잔량이 항상 성립 (`session_bars` 대조, 위반 0건)

**직접 대사는 못 했다.** 우리가 읽는 대역은 2~11(매도)·19~28(매수)뿐이고,
**12~18 과 29~ 가 무엇인지 모른다.** 거기에 `총매도잔량`·`총매수잔량`·`건수` 가
있으면 우리 5단 합을 그 총잔량과 **직접 맞춰볼 수 있다**(완전 검증). 동시에
「5단 너머에 얼마나 더 있는가」도 알 수 있다.

무엇을 하는가
-------------
실시간 구독을 **새로 만들지 않는다.** `CpSysDib.FutureJpBid` 를 **1회 구독**해
스냅샷 몇 개를 받고, 헤더 0~45 를 통째로 찍어 값의 모양으로 의미를 추정한다.
값만 보고 단정하지 않는다 — 아래 판별 규칙을 함께 출력한다.

  · 가격형 : 1000 대 실수, 단조 배열
  · 잔량형 : 작은 정수, **5단 합과 같거나 큰 값**이 총잔량 후보
  · 건수형 : 잔량형보다 **작거나 같은** 정수 (주문 1건당 최소 1계약)
  · 시각형 : HHMM / HHMMSS 꼴

🔴 **장 마감 후 전용.** COM 구독은 라이브 파이프라인과 같은 프로세스 자원을 쓴다.
장중에 새 구독을 붙이는 것은 456차 규약(장중 부하 금지)의 취지에 어긋난다.
그리고 장중에는 미륵이 본체가 이미 같은 객체를 구독 중이라 간섭 위험이 있다.

실행 (py37_32 · Cybos Plus 로그인 · **미륵이 본체 종료 후**)
---------------------------------------------------------
    python scripts/probe_futurejpbid_fields.py            # 기본 5스냅샷
    python scripts/probe_futurejpbid_fields.py --snaps 20
    python scripts/probe_futurejpbid_fields.py --code A056A

종료코드: 0 = 정상 · 2 = 장중 차단 · 3 = COM/구독 실패
"""
from __future__ import print_function

import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.dll_bootstrap import ensure_conda_dll_path  # noqa: E402

ensure_conda_dll_path()

import argparse  # noqa: E402
import time  # noqa: E402

from utils.analysis_db import guard_intraday  # noqa: E402

CHANNEL = "probe_futurejpbid_fields"
PROGID = "CpSysDib.FutureJpBid"
MAX_HEADER = 46          # 0~45 까지 훑는다. 없는 인덱스는 예외로 걸러진다.

# 561차 시점에 **우리가 읽고 있는** 대역 — 나머지가 조사 대상이다.
KNOWN = {
    2: "매도호가1", 3: "매도호가2", 4: "매도호가3", 5: "매도호가4", 6: "매도호가5",
    7: "매도잔량1", 8: "매도잔량2", 9: "매도잔량3", 10: "매도잔량4", 11: "매도잔량5",
    19: "매수호가1", 20: "매수호가2", 21: "매수호가3", 22: "매수호가4", 23: "매수호가5",
    24: "매수잔량1", 25: "매수잔량2", 26: "매수잔량3", 27: "매수잔량4", 28: "매수잔량5",
}


def _guess(idx, vals):
    """값의 모양으로 성격을 추정한다 — **단정하지 않는다**."""
    nums = [v for v in vals if isinstance(v, (int, float))]
    if not nums:
        return "비수치(%s)" % type(vals[0]).__name__
    lo, hi = min(nums), max(nums)
    if all(float(v).is_integer() for v in nums):
        if 900 <= lo <= 1600 and hi - lo < 200:
            return "가격형? (정수 1000대)"
        if 0 <= lo and hi <= 5:
            return "소정수 — 건수/단수 후보"
        if 0 <= lo and hi <= 2000:
            return "정수 — **잔량/건수 후보**"
        if 100000 <= lo <= 235959:
            return "시각형? (HHMMSS)"
        if 0 <= lo <= 2359 and hi <= 2359:
            return "시각형? (HHMM)"
        return "정수"
    if 900 <= lo <= 1600:
        return "가격형 (실수 1000대)"
    return "실수"


def main():
    ap = argparse.ArgumentParser(description="FutureJpBid 미사용 필드 대역 프로브 (561차)")
    ap.add_argument("--code", default=None, help="종목코드 (기본: ui_prefs 또는 근월물 프로브)")
    ap.add_argument("--snaps", type=int, default=5, help="수집할 스냅샷 수")
    ap.add_argument("--timeout", type=int, default=60, help="대기 상한(초)")
    args = ap.parse_args()

    guard_intraday(CHANNEL)

    try:
        import pythoncom
        import win32com.client
    except Exception as e:                                   # noqa: BLE001
        print("[%s] COM 모듈 없음: %r" % (CHANNEL, e))
        return 3

    code = args.code
    if not code:
        try:
            from collection.cybos.api_connector import CybosAPIConnector
            code = CybosAPIConnector().get_nearest_mini_futures_code()
        except Exception as e:                               # noqa: BLE001
            print("[%s] 근월물 코드 조회 실패: %r — --code 로 지정할 것" % (CHANNEL, e))
            return 3
    print("[%s] 대상 종목 %s · 스냅샷 %d개 수집" % (CHANNEL, code, args.snaps))

    pythoncom.CoInitialize()
    samples = []
    try:
        obj = win32com.client.Dispatch(PROGID)
        obj.SetInputValue(0, code)
        obj.Subscribe()
        t0 = time.time()
        # 🔴 콜백을 쓰지 않는다 — 절대원칙 §4(콜백 내 dynamicCall/emit 금지)를
        #    건드리지 않으려고 **폴링**으로 읽는다. 프로브 전용이라 허용된다.
        seen = None
        while len(samples) < args.snaps and time.time() - t0 < args.timeout:
            pythoncom.PumpWaitingMessages()
            row = {}
            for i in range(MAX_HEADER):
                try:
                    row[i] = obj.GetHeaderValue(i)
                except Exception:
                    pass
            key = tuple(sorted(row.items()), )
            if row and key != seen:
                seen = key
                samples.append(row)
            time.sleep(0.2)
        try:
            obj.Unsubscribe()
        except Exception:
            pass
    except Exception as e:                                   # noqa: BLE001
        print("[%s] 구독 실패: %r" % (CHANNEL, e))
        return 3
    finally:
        pythoncom.CoUninitialize()

    if not samples:
        print("[%s] 스냅샷 0개 — 장 마감 후에는 호가가 갱신되지 않을 수 있다. "
              "장중 재시도는 금지(456차)이므로 다음 거래일 15:35 직후를 노릴 것." % CHANNEL)
        return 0

    idxs = sorted(set(i for s in samples for i in s))
    print("\n" + "=" * 78)
    print("헤더 인덱스별 값 (%d 스냅샷)" % len(samples))
    print("=" * 78)
    print("%-5s %-14s %-34s %s" % ("idx", "기지(561차)", "값 표본", "추정"))
    print("-" * 78)
    ask5 = bid5 = None
    for i in idxs:
        vals = [s[i] for s in samples if i in s]
        shown = ", ".join(str(v) for v in vals[:3])
        print("%-5d %-14s %-34s %s"
              % (i, KNOWN.get(i, ""), shown[:34], _guess(i, vals)))
    # 5단 합과 대조 — 총잔량 후보 찾기
    try:
        s0 = samples[-1]
        ask5 = sum(int(s0[i]) for i in (7, 8, 9, 10, 11) if int(s0.get(i, 0)) > 0)
        bid5 = sum(int(s0[i]) for i in (24, 25, 26, 27, 28) if int(s0.get(i, 0)) > 0)
    except Exception:
        pass
    if ask5 is not None:
        print("-" * 78)
        print("마지막 스냅샷 5단 합 : 매도 %d · 매수 %d" % (ask5, bid5))
        print("⇒ 위 표에서 이 값과 **같거나 큰 정수** 필드가 총잔량 후보다.")
        print("  같으면 5단이 전부 = 호가창 전체, 크면 5단 너머에 더 있다는 뜻이다.")
        print("  이 값보다 **작은** 정수 필드는 건수(주문 수) 후보다.")
    print("=" * 78)
    print("⚠ 값 모양만으로 단정하지 말 것 — 후보를 좁힌 뒤 여러 시점에서 재확인한다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
