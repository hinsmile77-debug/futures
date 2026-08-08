# utils/dll_bootstrap.py
"""[MW0601 448차] conda env의 `Library\\bin`을 PATH에 보장 — BLAS 크래시 방지.

무엇을 고치는가
----------------
작업 스케줄러 `MireukiEODRetrain`이 **conda 활성화 없이** py310_64의 `python.exe`를
직접 호출한다. 그러면 그 env의 `Library\\bin`이 PATH에 없고, numpy의 MKL이 그 경로에서
delay-load하는 `mkl_core.3.dll`을 못 찾아 **프로세스가 통째로 즉사**한다
(`0xC06D007F` = STATUS_DELAY_LOAD_FAILED, **stderr 무출력**).

448차 실측(MW0601):

    PATH                            np.dot
    system32만                      ✗ 0xC06D007F
    + <env>\\Library\\bin             ✓
    <env>루트만(Library\\bin 없음)    ✗
    conda activate 전체 세트         ✓

→ **`<env>\\Library\\bin` 하나가 필요충분**이다.

⚠ **`os.add_dll_directory()`로는 못 고친다 — 실측으로 확인했다.**
   MKL의 delay-load는 `LOAD_LIBRARY_SEARCH_*` 플래그 없는 평범한 `LoadLibrary`를
   쓰므로 add_dll_directory 목록을 보지 않고 **PATH만** 본다. 448차 대조:

    조치 없음                ✗       PATH append   ✓
    os.add_dll_directory()  ✗       PATH prepend  ✓

   따라서 이 모듈은 반드시 `os.environ["PATH"]`를 고친다.

⚠ **numpy import 전에 호출해야 한다.** import 자체는 성공하고 첫 BLAS 호출(`np.dot`·
   `np.corrcoef` 등)에서 죽으므로, 늦게 부르면 "임포트는 됐는데 나중에 죽는" 형태가
   된다. 진입점 최상단에서 부를 것.

왜 스케줄러 설정이 아니라 코드로 고치나
----------------------------------------
스케줄러 Execute를 conda 활성화 bat으로 바꾸는 방법도 있으나, 그것은 **PC 로컬 설정
이라 git으로 공유되지 않는다** — 다른 PC나 새 PC에서 같은 사고가 반복되고, 수동 실행·
IDE 실행 등 다른 호출 경로는 여전히 무방비다. 이 모듈은 저장소에 담기므로 **모든
호출 경로와 모든 PC**에 자동 적용된다.

⚠ 자식 프로세스도 자동으로 보호된다 — `os.environ` 수정은 프로세스 환경 블록을
   바꾸고 `subprocess`가 기본으로 그것을 상속한다(`campaign_steps.run_campaign_steps()`
   가 리포트 생성기를 자식으로 띄우는 경로가 바로 이 사고의 현장이었다).

⚠ **경로를 하드코딩하지 않는다** — `sys.executable`에서 유도하므로 py37_32/py310_64,
   다른 PC의 다른 설치 경로에서도 그대로 맞는다.
"""
from __future__ import annotations

import os
import sys

__all__ = ["ensure_conda_dll_path"]

# 이 env 안에서 DLL이 놓이는 하위 경로들. `Library\bin`이 실측상 필요충분이지만
# conda 배포에 따라 나머지가 존재할 수 있어 있으면 함께 넣는다(없으면 조용히 건너뜀).
_SUBDIRS = (
    os.path.join("Library", "bin"),
    os.path.join("Library", "mingw-w64", "bin"),
    os.path.join("Library", "usr", "bin"),
)


def ensure_conda_dll_path(verbose: bool = False) -> list:
    """실행 중인 인터프리터의 conda env DLL 경로를 PATH 앞에 보장한다.

    Returns: 이번 호출로 **새로 추가된** 경로 목록(이미 있었으면 빈 리스트).
    Windows가 아니면 아무것도 하지 않는다.
    """
    if os.name != "nt":
        return []

    env_root = os.path.dirname(os.path.abspath(sys.executable))
    cur = os.environ.get("PATH", "")
    # 대소문자 무시 + 끝 역슬래시 무시로 중복 판정(윈도우 PATH 관례)
    have = {p.strip().rstrip("\\").lower() for p in cur.split(os.pathsep) if p.strip()}

    added = []
    for sub in _SUBDIRS:
        d = os.path.join(env_root, sub)
        if not os.path.isdir(d):
            continue
        if d.rstrip("\\").lower() in have:
            continue
        added.append(d)

    if added:
        # **앞에 붙인다** — 다른 conda 설치(예: base env)가 이미 PATH에 있을 때
        # 이 env의 것이 먼저 걸리게 한다. 448차 실측상 append로도 동작했지만
        # (파일명이 `mkl_core.2.dll` vs `.3.dll`로 달라 충돌이 아니었다), 버전이
        # 같은 이름으로 겹치는 조합에서는 prepend만 안전하다.
        os.environ["PATH"] = os.pathsep.join(added + ([cur] if cur else []))
        if verbose:
            sys.stderr.write("[dll_bootstrap] PATH 보강: %s\n" % os.pathsep.join(added))
    return added


def selftest() -> int:
    """BLAS가 실제로 살아 있는지 확인 — 진입점에서 조기 실패시키는 용도.

    Returns: 0 정상 / 1 numpy 미설치(무해) / 2 **BLAS 사망**.
    ⚠ `np.dot`은 실패 시 예외가 아니라 **프로세스 즉사**라 try/except로 못 잡는다.
      그래서 이 함수는 '살아남으면 정상'이라는 형태로만 쓸 수 있다 — 죽으면 여기서
      죽는다(그리고 그게 낫다: 조용한 실패보다 시끄러운 실패).
    """
    try:
        import numpy as np
    except Exception:
        return 1
    a = np.ones((2, 2))
    float(np.dot(a, a).sum())      # 여기서 죽으면 프로세스가 통째로 죽는다
    return 0


if __name__ == "__main__":
    added = ensure_conda_dll_path(verbose=True)
    print("env root :", os.path.dirname(os.path.abspath(sys.executable)))
    print("added    :", added or "(이미 충족)")
    rc = selftest()
    print("selftest :", {0: "BLAS OK", 1: "numpy 없음(무해)"}.get(rc, rc))
    sys.exit(0 if rc in (0, 1) else 2)
