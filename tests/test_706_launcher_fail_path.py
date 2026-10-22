# -*- coding: utf-8 -*-
"""[MW0601 2026-10-23 706차] CREON 실거래 런처 실패 경로 회귀 가드.

10-23 04:12 수동 실행에서 `/prj:cp /id:smart7na` 가 Smart1na 계좌(783293269)로 붙었고,
가드는 막았지만 실패 뒤가 세 가지로 나빴다.

1. `LAUNCH_API.bat :end_error` 가 `PAUSE` + `CMD /K` 로 끝나 창이 영원히 남았다.
   `CREON Plus` 작업은 `MultipleInstances=IgnoreNew` · 시간 제한 없음이라, 그 창이 열려
   있는 동안 08:35 트리거가 무시된다.
2. 계좌 불일치 실패가 잘못된 세션(CpStart·DibServer)을 살려둔 채 끝났다 — 10-16 08:35
   좀비 크래시 경로.
3. 원인 가설 D(저장 ID 우선)를 판정할 레지스트리 표본이 없었다.

덧붙여 `'��그램' is not recognized` — 한글 REM 줄이 중간에서 잘려 명령으로 실행됐다.
"""
import io
import os
import re
import time

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BAT = os.path.join(_ROOT, "LAUNCH_API.bat")
_AUTO = os.path.join(_ROOT, "scripts", "cybos_autologin.py")


def _bat_lines():
    with io.open(_BAT, encoding="utf-8") as fh:
        return fh.read().splitlines()


def _end_error_block():
    lines = _bat_lines()
    i = next(n for n, l in enumerate(lines) if l.strip().lower() == ":end_error")
    out = []
    for l in lines[i + 1:]:
        if l.startswith(":") and not l.startswith("::"):
            break
        out.append(l)
    return out


def test_end_error_does_not_hold_the_task():
    body = [l.strip().upper() for l in _end_error_block() if not l.strip().upper().startswith("REM")]
    assert "PAUSE" not in body, "PAUSE 는 작업을 Running 으로 붙잡아 다음 트리거를 막는다"
    assert not any(l.startswith("CMD /K") for l in body)
    assert any(re.match(r"TIMEOUT /T \d+", l) for l in body)
    assert body[-1].startswith("EXIT /B"), "실패 코드를 작업 스케줄러에 남기고 끝낼 것"


def test_launch_api_rem_lines_are_ascii():
    bad = ["%d: %s" % (n, l.strip()[:80]) for n, l in enumerate(_bat_lines(), 1)
           if re.match(r"^\s*(REM\b|::)", l, re.IGNORECASE) and re.search(r"[^\x00-\x7f]", l)]
    assert not bad, "한글 REM 은 잘린 조각이 명령으로 실행될 수 있다:\n" + "\n".join(bad)


def _src():
    with io.open(_AUTO, encoding="utf-8") as fh:
        return fh.read()


def _slice_by_next_def(src, name):
    m = re.search(r"^def %s\(.*?(?=^def |\Z)" % re.escape(name), src, re.S | re.M)
    return m.group(0)


def test_mismatch_path_kills_wrong_session_before_return():
    body = _slice_by_next_def(_src(), "_creon_real_cmdline_login")
    i = body.index("기대(실서버·%s)와 다르다. 실패 처리")
    tail = body[i:]
    ret = tail.index("return False")
    assert "_kill_cybos_procs(_REAL_KILL_NAMES)" in tail[:ret]
    assert "_starter_registry_snapshot()" in tail[:ret]


def test_login_logs_registry_snapshot_before_shellexecute():
    body = _slice_by_next_def(_src(), "_creon_real_cmdline_login")
    assert body.index("로그인 전 starter 레지스트리") < body.index("win32api.ShellExecute")


def _load_snapshot():
    src = _src()
    m = re.search(r"^_STARTER_REG_KEYS = \(.*?\)\n", src, re.S | re.M)
    ns = {"time": time}
    exec(m.group(0), ns)
    exec(_slice_by_next_def(src, "_starter_registry_snapshot"), ns)
    return ns


def test_registry_snapshot_never_raises_and_names_all_keys():
    ns = _load_snapshot()
    out = ns["_starter_registry_snapshot"]()
    for short in ("CREON\\starter", "CREON\\dstarter", "DAISHIN\\starter"):
        assert short in out
    # 키가 없을 때도 예외 없이 「(없음)」으로 남긴다 (계측 4원칙 ② — 미측정 ≠ 빈칸)
    ns["_STARTER_REG_KEYS"] = (r"Software\__mireuk_no_such_key__\OPTIONS",)
    assert "(없음)" in ns["_starter_registry_snapshot"]()
