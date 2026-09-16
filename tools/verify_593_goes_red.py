# -*- coding: utf-8 -*-
"""[MW0601 593차] 회귀 테스트가 **고치기 전 코드에서 정말 실패하는가**.

왜 필요한가
-----------
초록불만 본 회귀 테스트는 고장을 잡을지 알 수 없다. 이 프로젝트가 반복해서
당한 「배선했는데 아무도 소비하지 않는 것」의 테스트판이다 — 검사가 조건을
못 짚고 있어도 통과는 통과라 아무도 모른다.

무엇을 하나
-----------
593차 **직전** 백업을 `main_dashboard.py` 자리에 잠깐 올려 테스트를 돌리고,
결과와 상관없이 **반드시 되돌린다**(finally). 되돌리기가 실패하면 크게 외친다.

  · 기대: 고치기 전 → **FAIL**, 지금 코드 → PASS
  · 고치기 전에도 통과하면 그 검사는 이 버그를 못 짚는 것이다.

실행:
    conda run -n py37_32 python tools/verify_593_goes_red.py
"""
import os
import shutil
import subprocess
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_LIVE = os.path.join(_ROOT, "dashboard", "main_dashboard.py")
_TEST = os.path.join("tests", "test_593_peter_layer_isolation.py")
_HOLD = _LIVE + ".593verify_hold"


def _pick_backup():
    """593차 직전 백업 — 가장 최근 것. 없으면 멈춘다(추측하지 않는다)."""
    d = os.path.dirname(_LIVE)
    baks = sorted(f for f in os.listdir(d) if f.startswith("main_dashboard.py.bak_"))
    if not baks:
        raise SystemExit("백업이 없다 — 이 검사를 할 수 없다.")
    return os.path.join(d, baks[-1])


def _run():
    p = subprocess.run([sys.executable, "-m", "pytest", _TEST, "-q"],
                       cwd=_ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return p.returncode, p.stdout.decode("utf-8", "replace")


def main():
    bak = _pick_backup()
    print("직전 백업: %s" % os.path.basename(bak))
    if os.path.exists(_HOLD):
        raise SystemExit("이전 실행이 중간에 죽었다 — %s 를 먼저 손으로 되돌려라." % _HOLD)

    shutil.copy2(_LIVE, _HOLD)          # 지금 코드를 안전한 곳에 둔다
    try:
        shutil.copy2(bak, _LIVE)        # 고치기 전 코드를 올린다
        rc, out = _run()
        print("\n── 고치기 전 코드로 실행 ──")
        print(out.strip()[-1400:])
    finally:
        shutil.copy2(_HOLD, _LIVE)      # 무슨 일이 있어도 되돌린다
        os.remove(_HOLD)
        print("\n원상복구 완료 — main_dashboard.py 는 593차 적용본이다.")

    rc2, out2 = _run()
    print("\n── 지금 코드로 실행 ──")
    print(out2.strip()[-600:])

    print("\n" + "=" * 56)
    if rc != 0 and rc2 == 0:
        print("✅ 검사가 제 일을 한다 — 고치기 전 FAIL, 지금 PASS.")
    elif rc == 0:
        print("❌ 고치기 전 코드에서도 통과했다 — 이 검사는 593차 버그를 못 짚는다.")
    else:
        print("❌ 지금 코드에서 실패한다 — 되돌리기나 수정에 문제가 있다.")
    print("=" * 56)


if __name__ == "__main__":
    main()
