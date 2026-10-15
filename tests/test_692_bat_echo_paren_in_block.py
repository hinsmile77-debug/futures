# -*- coding: utf-8 -*-
"""[MW0601 2026-10-15] 배치 괄호 블록 안 ECHO 의 미이스케이프 `)` 회귀 가드.

LAUNCH_API.bat 의 `IF "!PREFLIGHT_ERR!"=="5" ( ECHO … 응답 없음(판정 불능). )` 한 줄이
블록을 조기에 닫아, cmd 가 바깥 IF 블록 파싱에서 「. 은(는) 예상되지 않았습니다」로
배치를 즉사시켰다(exit 255). 2026-08-06 도입 → 2026-10-15 발견, 두 달간 런처가
preflight 직전에 매번 조용히 죽었다(「session ready」 기록 0건).

검사: 들여쓴(= 블록 안으로 보이는) ECHO 줄에서 `^` 로 이스케이프되지 않은 `)` 를 찾는다.
리다이렉트 뒤(`>>` 이후)는 파일명이라 제외한다. 들여쓰기 기준의 휴리스틱이므로
블록 밖이지만 들여쓴 ECHO 도 걸릴 수 있다 — 그때는 괄호를 빼거나 `^)` 로 쓴다.
"""
import os
import re

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BATS = [f for f in os.listdir(_ROOT) if f.lower().endswith(".bat")]
_ECHO = re.compile(r"^\s+ECHO\b(.*)$", re.IGNORECASE)


def _offenders(path):
    bad = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for no, line in enumerate(fh, 1):
            m = _ECHO.match(line.rstrip("\r\n"))
            if not m:
                continue
            body = m.group(1).split(">")[0]
            if re.search(r"(?<!\^)\)", body):
                bad.append("%s:%d: %s" % (os.path.basename(path), no, line.strip()[:120]))
    return bad


def test_root_bats_found():
    assert "LAUNCH_API.bat" in _BATS and "start_mireuk.bat" in _BATS


def test_no_unescaped_close_paren_in_block_echo():
    bad = []
    for name in _BATS:
        bad += _offenders(os.path.join(_ROOT, name))
    assert not bad, "괄호 블록 안 ECHO 의 `)` 는 `^)` 로 이스케이프할 것:\n" + "\n".join(bad)
