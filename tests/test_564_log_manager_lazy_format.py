# -*- coding: utf-8 -*-
"""[MW0601 564차] `log_manager.*` 지연 포매팅 오용 — 회귀 가드.

무엇을 막는가
-------------
`log_manager.signal/system/...` 은 **stdlib logger 가 아니다.** `(msg, level="INFO")`
라 `log.info(fmt, a, b)` 같은 **지연 포매팅을 지원하지 않는다.** 그런데 생김새가
똑같아서 호출부가 printf 관행대로 부르기 쉽다.

🔴 2026-09-14 14:25 실측 — `main.py` conf_floor 분기가

    log_manager.signal("[P2] conf_floor dynamic=%.1f%% ...", a, b, c)

로 불러 `TypeError: signal() takes from 2 to 3 positional arguments but 5 were given`
→ **minute_pipeline 전체가 죽고** ERR-FATAL 핸들러가 **자동진입을 15분 껐다.**
자동진입 **하나**를 끄려던 분기가 **전부**를 껐다.

5/22 에 `**_kwargs` 로 **키워드** 인자는 이미 막아 뒀다. 막지 못한 것은 **위치**
인자였다. 564차가 두 가지를 함께 했다:

  ① 호출부 2곳 수정 (ColdStart · conf_floor) — `%` 로 미리 조립
  ② 로거에 `*_fmt_args` 안전망 — 인자가 있으면 조립해서 살리고 **오용을 경고**한다
     (삼키지 않는다). 인자가 없으면 **기존 경로 그대로**다.

⚠ ②는 호출부를 안 고쳐도 된다는 뜻이 아니다. 로그 한 줄 때문에 파이프라인이
  죽지 않게 하는 안전망이고, 경고가 호출부 수정을 유도한다.
"""
from __future__ import print_function

import ast
import glob
import io
import os
import re
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

_LEVELS = {"INFO", "WARNING", "ERROR", "DEBUG", "CRITICAL"}


def _channel_methods():
    src = io.open(os.path.join(_ROOT, "logging_system", "log_manager.py"),
                  encoding="utf-8").read()
    return set(re.findall(r"def (\w+)\(self, msg: str", src))


def _lazy_calls(path, methods):
    """`log_manager.<ch>(fmt, a, b, ...)` — 위치 인자 3개 이상인 호출."""
    try:
        src = io.open(path, encoding="utf-8").read()
        tree = ast.parse(src)
    except Exception:
        return []
    out = []
    for n in ast.walk(tree):
        if not isinstance(n, ast.Call):
            continue
        f = n.func
        if not (isinstance(f, ast.Attribute) and f.attr in methods):
            continue
        if not (isinstance(f.value, ast.Name) and f.value.id == "log_manager"):
            continue
        if len(n.args) >= 3:          # (msg, level, ...) 를 넘어선다 = 지연 포매팅
            out.append((path, n.lineno, len(n.args)))
    return out


# ─────────────────────── ① 호출부 ───────────────────────
def test_no_lazy_format_call_sites():
    """지연 포매팅 호출이 0건이어야 한다 — 이게 파이프라인을 죽인 형태다."""
    methods = _channel_methods()
    assert "signal" in methods and "system" in methods
    files = [os.path.join(_ROOT, "main.py")]
    for pat in ("strategy/**/*.py", "collection/**/*.py", "learning/*.py", "model/*.py"):
        files += glob.glob(os.path.join(_ROOT, pat), recursive=True)
    bad = []
    for f in files:
        bad += _lazy_calls(f, methods)
    assert not bad, (
        "log_manager 를 지연 포매팅으로 부르는 곳이 있다 — 미리 조립할 것:\n  " +
        "\n  ".join("%s:%d (인자 %d개)" % (os.path.relpath(p, _ROOT), ln, na)
                    for p, ln, na in bad))


# ─────────────────────── ② 로거 안전망 ───────────────────────
def _fresh():
    from logging_system.log_manager import LogManager
    lm = LogManager()
    cap = []
    lm.log = lambda ch, msg, level="INFO": cap.append((ch, msg, level))
    LogManager._lazy_fmt_warned.clear()
    return lm, cap


def test_normal_calls_unchanged():
    """인자 없/1개 경로는 **아무것도 바뀌지 않아야** 한다."""
    lm, cap = _fresh()
    lm.signal("[X] 평범")
    assert cap[-1] == ("SIGNAL", "[X] 평범", "INFO")
    lm.system("[Y] 경고", "WARNING")
    assert cap[-1] == ("SYSTEM", "[Y] 경고", "WARNING")


def test_lazy_format_is_rescued_not_raised():
    """오늘 죽은 그 호출이 이제 정확한 메시지로 기록된다."""
    lm, cap = _fresh()
    lm.signal("[P2] conf_floor dynamic=%.1f%% (static=%.1f%%) → auto_entry=OFF "
              "(conf=%.1f%%)", 37.1, 33.0, 35.4)
    msgs = [m for ch, m, _ in cap if ch == "SIGNAL"]
    assert msgs, "SIGNAL 이 기록되지 않았다"
    assert "37.1%" in msgs[-1] and "33.0%" in msgs[-1] and "35.4%" in msgs[-1]


def test_misuse_is_warned_not_swallowed():
    """살려내되 **조용히 넘어가지 않는다** — 경고가 호출부 수정을 유도한다."""
    lm, cap = _fresh()
    lm.signal("[ColdStart] pass=%d < required=%d (%d~%d)", 3, 5, 9, 11)
    warn = [m for ch, m, lv in cap if "[LogFmt]" in m]
    assert warn, "오용을 경고하지 않는다 — 삼키면 영원히 안 고쳐진다"
    assert "호출부를 고칠 것" in warn[0]


def test_warning_is_deduplicated():
    """같은 오용이 매분 반복돼도 로그를 덮지 않는다."""
    lm, cap = _fresh()
    for _ in range(5):
        lm.signal("[Dup] v=%d", 1, 2)
    assert len([m for ch, m, lv in cap if "[LogFmt]" in m]) == 1


def test_mixed_form_keeps_level():
    """`(msg, level, *args)` 혼합형은 level 을 지켜야 한다."""
    lm, cap = _fresh()
    lm.system("[Z] v=%d", "WARNING", 7)
    assert cap[-1] == ("SYSTEM", "[Z] v=7", "WARNING")


def test_bad_format_still_does_not_raise():
    """포맷 자체가 틀려도 죽지 않는다 — 로그는 파이프라인을 멈출 권한이 없다."""
    lm, cap = _fresh()
    lm.signal("[W] %d 개", "문자열")       # %d 에 문자열
    assert cap, "예외로 죽었다"


def test_kwargs_guard_still_present():
    """5/22 의 `**_kwargs` 가드를 없애지 않았는지 — 둘 다 있어야 한다."""
    src = io.open(os.path.join(_ROOT, "logging_system", "log_manager.py"),
                  encoding="utf-8").read()
    assert "**_kwargs" in src, "5/22 키워드 가드가 사라졌다"
    assert "*_fmt_args" in src, "564차 위치 가드가 사라졌다"
