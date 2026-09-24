# -*- coding: utf-8 -*-
"""[MW0602 557차] 수익 패널 GP(가상) 별도집계 — **590차에 퇴역, strftime 가드만 남는다.**

590차(2026-09-24 사용자 지시)가 GP(GB·GS) 표시를 **신동 가상거래**로 교체했다:
  · 1분봉 차트 GP 마커 → 신동 마커(`_draw_sd_markers`)
  · 손익 추이 패널 「GP(가상) 합산」 체크박스 → **[미륵]/[신동] 전환 버튼**
그 결과 이 파일의 GP 패널·차트 회귀(test_1~8, 10~14, source_wiring)는 시험할 코드가
사라져 삭제했다. 같은 성질의 불변식(가상은 trades 무오염 · 브로커 net 부분선택 ·
평문 배너 · 점선·라벨 클램프 · 방향별 마커)은 `tests/test_590_shindong_chart_pnl.py` 가
신동 기준으로 다시 건다.

🔴 **test_9 는 지우지 말 것** — CLAUDE.md 「PyQt5 paintEvent 예외」 절이 이 노드 id 를
  회귀 가드로 인용한다(프로덕션 코드 전수 strftime non-ASCII 검사).

실행: `C:\\Users\\pc1\\anaconda3\\python.exe -m pytest tests/test_557_gp_pnl_panel.py`
"""
import io
import os
import re
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


def test_9_no_non_ascii_inside_strftime_format():
    """`strftime` 포맷 문자열에 non-ASCII 를 넣지 말 것.

    이 env 의 `locale.getlocale()` 은 `(None, None)`(LC_CTYPE "C")이라 로케일
    코덱이 ASCII 다 — `getpreferredencoding()` 이 cp949 인 것과 별개다. 그래서
    `datetime.strftime("GP진입 %H:%M")` 은 `UnicodeEncodeError` 를 낸다.

    🔴 그 자체는 **잡을 수 있는 예외**지만, `paintEvent` 안에서 나면 PyQt5 가
      **프로세스를 그냥 죽인다**(2026-09-10 실측: 차트가 통째로 사라졌다).
      그러니 이 검사는 「더 넓은 규약」의 한 사례만 잡는 것이다 —
      **paint 경로에서는 예외가 날 수 있는 호출을 하지 말거나 감싸라.**

    ⚠ 시각은 ASCII 포맷으로 만들고 한글은 **뒤에 이어붙일 것**.
    ⚠ [2026-09-10 정정] 초판 docstring 이 이것을 「BLAS 즉사와 같은 계열」이라 썼고
      `grab()`/`render(QImage)` 도 즉사한다고 썼다. **둘 다 틀렸다** — 재인용 금지
      (`dev_memory/DECISION_LOG.md` 557차 후속2 §1 정정 블록).

    검사 범위는 **프로덕션 코드 전체**다(dashboard 뿐이었다 → 확대).
    """
    _pat = re.compile(r"""strftime\(\s*(['"])(.*?)\1""")
    _skip_dirs = {".git", "_archive", "node_modules", "__pycache__",
                  "data", "logs", "docs", "tests", ".claude", "dev_memory"}
    bad = []
    for root, dirs, files in os.walk(_ROOT):
        dirs[:] = [d for d in dirs if d not in _skip_dirs and not d.startswith(".")]
        for fn in files:
            if not fn.endswith(".py"):
                continue
            path = os.path.join(root, fn)
            try:
                lines = io.open(path, encoding="utf-8").readlines()
            except (OSError, UnicodeDecodeError):
                continue
            for lineno, line in enumerate(lines, 1):
                for m in _pat.finditer(line):
                    if any(ord(ch) > 127 for ch in m.group(2)):
                        bad.append("%s:%d  %s" % (
                            os.path.relpath(path, _ROOT), lineno, line.strip()[:90]))
    assert not bad, (
        "strftime 포맷에 non-ASCII — paint 경로면 프로세스가 죽는다:\n"
        + "\n".join(bad))
