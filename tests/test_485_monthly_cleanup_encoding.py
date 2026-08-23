# -*- coding: utf-8 -*-
"""[MW0602 485차 F-7] monthly_cleanup.py stdout 인코딩 불변식.

무엇을 발견했나 (2026-08-21, 0821 리포트 1-16)
---------------------------------------------
2026-08-21(금) EOD 체인에서 월간 로그 정리가 **첫 발화** 했는데, 헤더 첫
비-ASCII print(EM DASH `—`)에서 `UnicodeEncodeError`로 즉사해 한 파일도
정리하지 못했다. 원인: `campaign_steps.py`가 `stdout=subprocess.PIPE`로
호출하면 Windows 기본 `cp949`가 적용되는데, 캠페인 체인 스크립트 중 이
파일에만 `sys.stdout.reconfigure(encoding="utf-8")` 블록이 빠져 있었다.

문자를 지우는 방향(`—` → `-`)으로 고치지 않았다 — 그러면 이 파일은 살지만
같은 결함이 다음에 추가되는 스크립트에서 되살아난다. 원인은 인코딩이다.

이 파일이 고정하는 불변식 2종
-----------------------------
① 소스에 reconfigure 블록이 존재한다 (지우면 여기서 깨진다)
② cp949 파이프 환경(PYTHONIOENCODING=cp949)에서 dry-run이 UnicodeEncodeError
   없이 완주한다 — rc=0(정상) 또는 rc=2(장중 가드 guard_intraday)만 허용

라이브 검증은 O-20: 2026-08-28(금) EOD 요약행 `월간 로그 정리=OK` +
`data/monthly_cleanup_last_run.txt` = `202608`.

실행:
    pytest tests/test_485_monthly_cleanup_encoding.py
"""
import io
import os
import subprocess
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCRIPT = os.path.join(_ROOT, "scripts", "monthly_cleanup.py")


def test_1_source_has_reconfigure_block():
    """① reconfigure 블록 존재 — 캠페인 체인 공통 관용구와 같은 형태여야 한다."""
    with io.open(_SCRIPT, encoding="utf-8") as f:
        src = f.read()
    assert 'sys.stdout.reconfigure(encoding="utf-8")' in src
    assert 'sys.stderr.reconfigure(encoding="utf-8")' in src


def test_2_dry_run_survives_cp949_pipe():
    """② cp949 파이프에서 비-ASCII print()가 죽지 않는다.

    campaign_steps.py의 호출 조건(stdout=PIPE + cp949)을 재현한다.
    dry-run(기본값 — `--apply` 없음)이라 파일시스템 변경이 없다.
    """
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "cp949"   # PIPE 호출 시의 기본 인코딩을 강제 재현
    env.pop("PYTHONUTF8", None)         # UTF-8 모드가 켜져 있으면 재현이 무효가 된다

    r = subprocess.run(
        [sys.executable, _SCRIPT],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
        timeout=300,
    )
    out = r.stdout.decode("utf-8", "replace")
    assert "UnicodeEncodeError" not in out, out[-2000:]
    # rc=2는 장중 가드(guard_intraday) — 인코딩 생존과 무관한 정상 차단이므로 허용.
    assert r.returncode in (0, 2), "rc=%s\n%s" % (r.returncode, out[-2000:])
