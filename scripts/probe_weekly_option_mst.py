"""
[MW0601 623차] 위클리 옵션 코드가 `Dscbo1.OptionMst` 에서 조회되는가 — 612-6 1단계 프로브.

배경: `CpUtil.CpOptionCode` 는 먼스리 전용이다(4,600종목 = KIS 마스터 type 5/6 과 정확히 일치,
2026-09-22 조사보고 §5). 위클리 코드를 Cybos 에서 얻는 서비스가 레지스트리에 없어서,
**코드를 KRX 표준코드에서 직접 만든다.**

코드 규칙 (2026-09-23 실측): Cybos 옵션코드 = KRX 표준코드[3:11]
    KR4B016AA487 → B016AA48   (먼스리 2610 1120.0 콜)
    먼스리 4,602종목 전수 대조 **4,602/4,602 일치**(행사가까지).
    같은 규칙을 위클리에 적용하면
    KR4B09FEA490 → B09FEA49   ((목)위클리 2609W4 1120.0 콜)
    KR4BAFBZA490 → BAFBZA49   ((월)위클리 2609W4 1120.0 콜)

이 스크립트는 그 코드를 OptionMst 에 넣어 OI(hv99)·gamma(hv110) 가 오는지만 본다.
조회 수는 `--codes` 개수만큼(기본 6건) — 장중에도 부하 무시 수준이다.
"""
from __future__ import annotations

import argparse
import struct
import sys
import time

_DEFAULT = [
    ("먼스리 C", "B016AA48"), ("먼스리 P", "C016AA48"),
    ("목위클 C", "B09FEA49"), ("목위클 P", "C09FEA49"),
    ("월위클 C", "BAFBZA49"), ("월위클 P", "CAFBZA49"),
]
_HV = [(0, "code?"), (1, "name?"), (99, "OI"), (110, "gamma%"), (108, "delta%?"), (111, "theta?"), (112, "vega?")]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--codes", default="", help="label=code,label=code … (기본 6건)")
    ap.add_argument("--dump", type=int, default=0, help="헤더 0..N-1 전량 덤프(첫 코드만)")
    args = ap.parse_args()
    if struct.calcsize("P") != 4:
        print("32-bit Python 필요 (py37_32)")
        return 2

    targets = _DEFAULT
    if args.codes:
        targets = [tuple(p.split("=", 1)) for p in args.codes.split(",") if "=" in p]

    import pythoncom
    from win32com.client import Dispatch
    pythoncom.CoInitialize()
    try:
        cy = Dispatch("CpUtil.CpCybos")
        if not bool(cy.IsConnect):
            print("Cybos 미연결")
            return 2
        oc = Dispatch("CpUtil.CpOptionCode")
        mst = Dispatch("Dscbo1.OptionMst")
        for i, (label, code) in enumerate(targets):
            try:
                name = oc.CodeToName(code)
            except Exception as exc:
                name = "<ERR %s>" % exc
            mst.SetInputValue(0, code)
            mst.BlockRequest()
            st, msg = mst.GetDibStatus(), mst.GetDibMsg1()
            vals = []
            for idx, tag in _HV:
                try:
                    vals.append("%s[%d]=%s" % (tag, idx, mst.GetHeaderValue(idx)))
                except Exception as exc:
                    vals.append("%s[%d]=<ERR>" % (tag, idx))
            print("%-8s %-9s CodeToName=%r dib=%s msg=%r" % (label, code, name, st, msg))
            print("         " + " | ".join(vals))
            if args.dump and i == 0:
                for idx in range(args.dump):
                    try:
                        print("   hv%3d = %r" % (idx, mst.GetHeaderValue(idx)))
                    except Exception:
                        pass
            time.sleep(0.3)
        return 0
    finally:
        pythoncom.CoUninitialize()


if __name__ == "__main__":
    sys.exit(main())
