# CpSysDib.CpSvrNew7212 날짜 범위 확인 스크립트.
# 동일 TR을 서로 다른 입력값으로 호출하여
# 헤더의 시작일/종료일 변화와 외인 선물순매수 값 변화를 비교한다.
# 실행: py37_32\python.exe -X utf8 scripts/_probe_7212_dates.py
from __future__ import annotations
import io, sys, time, datetime

if sys.stdout.encoding and sys.stdout.encoding.lower() in ("cp949", "mbcs"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PROGID = "CpSysDib.CpSvrNew7212"
TODAY_8 = datetime.date.today().strftime("%Y%m%d")   # "20260511"
TODAY_6 = datetime.date.today().strftime("%y%m%d")   # "260511"

# 외인 행에서 선물순매수(field[3]) 추출용 이름 집합
TARGET_NAMES = {"외국인", "개인", "기관계"}

def safe_str(v):
    if v is None:
        return ""
    try:
        return str(v).strip()
    except Exception:
        return ""

def safe_int(v, default=0):
    try:
        text = safe_str(v).replace(",", "")
        if not text:
            return default
        return int(float(text))
    except Exception:
        return default

def probe(label: str, inputs: list) -> None:
    import win32com.client
    obj = win32com.client.Dispatch(PROGID)
    for idx, val in inputs:
        obj.SetInputValue(idx, val)
    ret    = obj.BlockRequest()
    status = safe_int(getattr(obj, "GetDibStatus", lambda: 0)())
    msg    = safe_str(getattr(obj, "GetDibMsg1",   lambda: "")())

    h0 = safe_str(obj.GetHeaderValue(0))
    h1 = safe_str(obj.GetHeaderValue(1))  # 시작일
    h2 = safe_str(obj.GetHeaderValue(2))  # 종료일
    h3 = safe_str(obj.GetHeaderValue(3))  # 행 수?

    print(f"\n{'='*60}")
    print(f"  [{label}]  inputs={inputs}")
    print(f"  ret={ret}  status={status}  msg={msg!r}")
    print(f"  header[0]={h0!r}  [1(시작일?)]={h1!r}  [2(종료일?)]={h2!r}  [3]={h3!r}")
    print(f"  {'투자자':<10} {'선물순매수':>14} {'콜순매수':>14} {'풋순매수':>14}")
    print(f"  {'-'*54}")

    row_count = 0
    for ri in range(20):
        try:
            name = safe_str(obj.GetDataValue(0, ri))
        except Exception:
            break
        if not name and ri > 0:
            break
        fut_net  = safe_str(obj.GetDataValue(3, ri))
        call_net = safe_str(obj.GetDataValue(6, ri))
        put_net  = safe_str(obj.GetDataValue(9, ri))
        marker = " ◀" if name in TARGET_NAMES else ""
        print(f"  {name:<10} {fut_net:>14} {call_net:>14} {put_net:>14}{marker}")
        row_count += 1

    print(f"  ({row_count}행)")
    time.sleep(0.4)   # Cybos TR 쓰로틀

def main():
    import pythoncom, win32com.client
    pythoncom.CoInitialize()

    cp = win32com.client.Dispatch("CpUtil.CpCybos")
    if cp.IsConnect != 1:
        print("[FAIL] Cybos Plus API 미연결")
        sys.exit(1)

    print(f"TODAY_8={TODAY_8}  TODAY_6={TODAY_6}")
    print("* 같은 케이스에서 헤더 날짜와 값이 변하면 '입력이 날짜를 제어함'")

    # ── 케이스 1: 입력 없음 (기본 누적?) ─────────────────────
    probe("입력없음(기본)", [])

    # ── 케이스 2~5: idx0 에 정수형 입력 시도 ────────────────
    # SetInputValue(0, string) → "범위 벗어남" 오류 확인
    # → 정수형으로 재시도
    for v in [0, 1, 2, 50]:
        probe(f"idx0={v}(int)", [(0, v)])

    # ── 케이스 6~7: idx1, idx2 에 날짜 입력 (idx0은 정수) ────
    probe("idx0=0, idx1=TODAY_8", [(0, 0), (1, TODAY_8)])
    probe("idx0=1, idx1=TODAY_8, idx2=TODAY_8", [(0, 1), (1, TODAY_8), (2, TODAY_8)])

    print("\n[완료]")

if __name__ == "__main__":
    main()
