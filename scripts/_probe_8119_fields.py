# Dscbo1.CpSvr8119 / CpSvrNew8119 / CpSvrNew8119Chart 필드 레이아웃 확인 스크립트.
# 장 중(09:00~15:30)에 실행해야 실제 값이 나온다.
# 실행: py37_32\python.exe -X utf8 scripts/_probe_8119_fields.py
from __future__ import annotations
import io, sys, time

if sys.stdout.encoding and sys.stdout.encoding.lower() in ("cp949", "mbcs"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import struct
if struct.calcsize("P") * 8 != 32:
    print(f"[경고] 현재 Python: {struct.calcsize('P') * 8}-bit. 32-bit(py37_32) 필요.")
    sys.exit(1)

TARGETS = [
    ("Dscbo1.CpSvr8119",          []),
    ("Dscbo1.CpSvrNew8119",       []),
    ("Dscbo1.CpSvrNew8119Chart",  []),
    # DsCbo1.CpSvrNew8119Day: 날짜 입력 시도
    ("DsCbo1.CpSvrNew8119Day",    [(0, 1)]),   # 구분=1 (당일?)
]


def safe_str(v):
    if v is None:
        return ""
    try:
        return str(v).strip()
    except Exception:
        return ""


def probe(label: str, progid: str, inputs: list) -> None:
    import win32com.client
    try:
        obj = win32com.client.Dispatch(progid)
    except Exception as e:
        print(f"\n[{label}] CLASSNOTREG: {e}")
        return

    for idx, val in inputs:
        try:
            obj.SetInputValue(idx, val)
        except Exception as e:
            print(f"  SetInputValue({idx},{val}): {e}")

    ret    = obj.BlockRequest()
    try:
        status = int(obj.GetDibStatus())
    except Exception:
        status = -99
    try:
        msg = safe_str(obj.GetDibMsg1())
    except Exception:
        msg = ""

    print(f"\n{'='*64}")
    print(f"  [{label}]  progid={progid}  inputs={inputs}")
    print(f"  ret={ret}  status={status}  msg={msg!r}")

    # 헤더 전체 출력
    nonzero_h = []
    for i in range(40):
        try:
            v = safe_str(obj.GetHeaderValue(i))
            if v and v != "0":
                nonzero_h.append((i, v))
        except Exception:
            break
    if nonzero_h:
        print(f"  헤더 비제로: {nonzero_h}")
    else:
        # 제로인 경우에도 값 있는 인덱스 표시
        zeroes = []
        for i in range(40):
            try:
                v = safe_str(obj.GetHeaderValue(i))
                if v:
                    zeroes.append((i, v))
            except Exception:
                break
        if zeroes:
            print(f"  헤더(모두 0): 인덱스 {[x[0] for x in zeroes]} ({len(zeroes)}개)")
        else:
            print("  헤더: 빈값")

    # 행 데이터 전체 출력
    row_count = 0
    for ri in range(20):
        row_vals = []
        any_nonzero = False
        for fi in range(10):
            try:
                v = safe_str(obj.GetDataValue(fi, ri))
                row_vals.append(v)
                if v and v not in ("0", "0.0"):
                    any_nonzero = True
            except Exception:
                break
        if not any_nonzero and ri > 0:
            break
        if row_vals:
            marker = " *" if any_nonzero else ""
            print(f"  row[{ri:02d}]: {row_vals}{marker}")
            row_count += 1

    print(f"  => {row_count}행")
    time.sleep(0.5)


def main():
    import pythoncom, win32com.client
    pythoncom.CoInitialize()

    cp = win32com.client.Dispatch("CpUtil.CpCybos")
    if cp.IsConnect != 1:
        print("[FAIL] Cybos Plus API 미연결")
        sys.exit(1)

    print("[INFO] Cybos 연결 확인. 8119 계열 프로브 시작.")
    print("[주의] 장 중(09:00~15:30)에 실행해야 실제 값이 나옵니다.")

    for label, progid, inputs in [(p, p, i) for p, i in TARGETS]:
        probe(label, progid, inputs)

    print("\n[완료]")


if __name__ == "__main__":
    main()
