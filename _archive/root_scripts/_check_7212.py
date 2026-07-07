"""
_check_7212.py → _check_investor_tr.py 역할
투자자 수급 TR 구조 진단 (장 중 실행)

확인된 TR (대신증권 자료실 seq=85):
  CpSysDib.CpSvrNew7221 — 투자자별 매매종합서비스
    입력: SetInputValue(0, ord('1')) = 49
    행(ri): 0=거래소주식, 1=코스닥주식, 2=선물, 3=옵션콜, 4=옵션풋 ...
    열(fi): 0=개인매도, 1=개인매수, 2=개인순매수
            3=외인매도, 4=외인매수, 5=외인순매수
            6=기관매도, 7=기관매수, 8=기관순매수

실행:
    conda activate py37_32
    python _check_7212.py
"""
from __future__ import annotations

import sys

try:
    from win32com.client import Dispatch
except ImportError:
    print("[ERROR] pywin32 없음. py37_32 환경에서 실행하세요.")
    sys.exit(1)


_INVEST_INDEX = {
    0: "거래소주식", 1: "코스닥주식", 2: "선물", 3: "옵션콜", 4: "옵션풋",
    5: "주식콜", 6: "주식풋", 7: "스타지수선물", 8: "주식선물",
}


def _s(v) -> str:
    if v is None:
        return ""
    try:
        return str(v).strip()
    except Exception:
        return repr(v)


def _probe(progid: str, inputs=(), n_header=32, n_field=12, n_row=25):
    print(f"\n{'='*60}")
    print(f"TR: {progid}")
    print(f"입력: {inputs}")
    print('='*60)
    try:
        obj = Dispatch(progid)
    except Exception as e:
        print(f"  [FAIL] Dispatch 실패: {e}")
        return

    for idx, val in inputs:
        obj.SetInputValue(idx, val)

    try:
        ret = obj.BlockRequest()
    except Exception as e:
        print(f"  [FAIL] BlockRequest 실패: {e}")
        return

    try:
        status = int(obj.GetDibStatus())
        msg    = _s(obj.GetDibMsg1())
    except Exception:
        status = -999
        msg    = "?"

    print(f"  ret={ret}  status={status}  msg='{msg}'")
    if ret not in (0, None) or status != 0:
        print("  [FAIL] 응답 에러 — 데이터 없음")
        return

    # GetHeaderValue
    print("\n  [GetHeaderValue] 비어있지 않은 항목:")
    found_h = False
    for i in range(n_header):
        try:
            v = _s(obj.GetHeaderValue(i))
            if v:
                print(f"    hv[{i:2d}] = '{v}'")
                found_h = True
        except Exception:
            break
    if not found_h:
        print("    (없음)")

    # GetDataValue
    print(f"\n  [GetDataValue] 최대 {n_row}행 × {n_field}열:")
    for ri in range(n_row):
        row = {}
        any_val = False
        for fi in range(n_field):
            try:
                v = _s(obj.GetDataValue(fi, ri))
                if v:
                    row[fi] = v
                    any_val = True
            except Exception:
                pass
        if not any_val and ri > 0:
            print(f"    row[{ri}]: 빈값 → 종료")
            break
        label = _INVEST_INDEX.get(ri, f"idx{ri}")
        if row:
            print(f"    row[{ri:2d}]({label}): {row}")
            # 7221 특화 해석
            if progid == "CpSysDib.CpSvrNew7221":
                ind_net = row.get(2, "?")
                fi_net  = row.get(5, "?")
                inst_net = row.get(8, "?")
                print(f"          → 개인순매수={ind_net}, 외인순매수={fi_net}, 기관순매수={inst_net}")
        elif ri == 0:
            print(f"    row[0]: 모든 필드 빈값")


def main():
    print("=" * 60)
    print("투자자 수급 TR 구조 진단")
    print("Cybos Plus 로그인 + 장 중에 실행하세요")
    print("=" * 60)

    # ── 1. CpSyrNew7221: 투자자별 매매종합 (공식 확인 TR) ────────────
    print("\n▶ [선물 투자자 수급 — 공식 확인 TR]")
    _probe("CpSysDib.CpSvrNew7221", [(0, ord('1'))])   # 선물계약 단위
    _probe("CpSysDib.CpSvrNew7221", [(0, ord('0'))])   # 금액 단위 (비교용)
    _probe("CpSysDib.CpSvrNew7221", [])                # 입력 없음 (비교용)

    # ── 2. CpSvr8119: 프로그램 매매 ───────────────────────────────
    print("\n▶ [프로그램 매매]")
    _probe("Dscbo1.CpSvr8119", [])
    _probe("Dscbo1.CpSvrNew8119", [])
    _probe("CpSysDib.ProgramTrade", [])
    _probe("Dscbo1.ProgramTrade", [])

    # ── 3. 구 TR 명칭 확인 (오사용 진단) ─────────────────────────
    print("\n▶ [기존 코드에서 사용한 잘못된 TR — 응답 여부만 확인]")
    _probe("CpSysDib.CpSvrNew7212", [(0, 1)])

    print("\n\n진단 완료. 위 출력을 복사해서 Claude에게 전달하세요.")


if __name__ == "__main__":
    main()
