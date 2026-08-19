# -*- coding: utf-8 -*-
"""[MW0601 480차 / F-4] EOD `WaitDC` 폴백 가시화 — 정적 불변식.

2026-08-19, `daily_close()`가 아예 실행되지 않은(라이브 프로세스 동결) 상태에서
EOD 재학습이 20분 대기 후 **강제 진행**해 6/6 호라이즌을 교체했다. 결과는 성공이었지만
그 사실은 로그 1줄로만 남았고, 다음날 완료 마커(`data/eod_retrain_done_*.txt`)만 보면
정상 완주와 **구분되지 않는다** — 계측 4원칙 ④가 금지하는 형태다.

⚠ 파일은 `retrain_eod.py`(리포 루트)다. 08-19 리포트 §2 F-4는 `scripts/eod_retrain.py`로
  적었으나 `WaitDC`도 마커 기록도 그쪽에 없다(실측 확인) — 이 테스트가 정본 위치를 고정한다.
⚠ `py310_64` 전용 파일이다(191차). 여기서는 실행하지 않고 소스만 본다.
"""
import ast
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_PATH = os.path.join(ROOT, "retrain_eod.py")


def _src():
    with open(SRC_PATH, encoding="utf-8") as f:
        return f.read()


def test_대기_결과를_버리지_않는다():
    """`_wait_for_daily_close()`의 반환값이 어딘가에 대입돼야 한다 —
    호출만 하고 버리면 폴백 여부를 알 수 없다(종전 코드가 그랬다)."""
    tree = ast.parse(_src())
    assigned = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            f = node.value.func
            if isinstance(f, ast.Name) and f.id == "_wait_for_daily_close":
                assigned = True
    assert assigned, "_wait_for_daily_close() 반환값이 버려지고 있다 (F-4 회귀)"


def test_마커에_폴백_여부_토큰이_들어간다():
    src = _src()
    assert "daily_close_seen:" in src
    assert "wait_dc_timeout:" in src


def test_완료마커와_실패마커_둘_다에_남는다():
    """실패 조사에서도 '오늘 daily_close가 없었다'는 1급 단서다."""
    src = _src()
    assert src.count("_dc_note") >= 3, "완료/실패 마커 양쪽 기록을 확인할 수 없다"


def test_토큰은_true_false_문자열이다():
    """마커 파서가 붙을 때 값 형식이 흔들리면 안 된다."""
    src = _src()
    assert '"true" if _dc_ok else "false"' in src
    assert '"false" if _dc_ok else "true"' in src
