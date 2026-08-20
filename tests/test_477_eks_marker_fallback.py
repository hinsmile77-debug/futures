# -*- coding: utf-8 -*-
"""[MW0602 477차 F-2] EKS 원인 태깅의 p8_last_success_date 마커파일 폴백.

무엇을 지키는가
---------------
EKS 발동 원인 태깅(main.py `_eks_causes` 블록)이 스케일러 노후와 휴장/중단갭을
구분할 때, session_state의 `p8_last_success_date`가 비어 있어도(또는 기록만
실패했어도) **EOD 마커파일(data/eod_retrain_done_{어제}.txt)로 폴백**해
정확한 태그를 낸다 — `_ts_resolve_p8_ok_date()`.

왜 필요한가 (0820 점검 이상점 1-1 / F-2)
-----------------------------------------
F-1 이전 롤오버가 `p8_last_success_date`를 매 거래일 지워 항상 빈 값이었고,
`!= 어제`가 항상 성립해 진짜 스케일러 노후를 `휴장/중단갭`으로 상시 오분류했다
(`스케일러{n}h노후` 분기 도달 불가). F-1이 키를 보존해 자연 해소되지만,
**F-1 없이도 정확해야 하는 방어선**이 이 폴백이다 — retrain_eod.py가 성공
시에만 쓰는 마커파일(08:55 PreRetrain 폴백과 같은 원천)이 이미 있는데 쓰지
않고 있었다. session_state 기록만 실패하는 날(retrain_eod.py:195-196의
"무해" 예외 경로)도 이 폴백만이 덮는다.

EKS는 상시 발동하지 않으므로(최근 10거래일 전부 미발동 — cold-start) 라이브
관측은 발동일까지 기한 없이 대기한다. 단위 테스트가 유일한 상시 방어다.

실행: pytest tests/test_477_eks_marker_fallback.py
      (COM/브로커 불필요 — enable_test_mode 후 import main)
"""
import datetime
import os
import shutil
import sys
import tempfile

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

import main  # noqa: E402

_YESTERDAY = datetime.date.today() - datetime.timedelta(days=1)
_Y_ISO = _YESTERDAY.isoformat()
_STALE_ISO = (datetime.date.today() - datetime.timedelta(days=3)).isoformat()


def _with_marker_dir(marker_for=None):
    """임시 data 디렉터리 — marker_for(date)가 주어지면 그 날짜 마커를 만든다."""
    d = tempfile.mkdtemp(prefix="test477_eks_")
    if marker_for is not None:
        mf = os.path.join(d, "eod_retrain_done_%s.txt" % marker_for.strftime("%Y%m%d"))
        with open(mf, "w", encoding="utf-8") as f:
            f.write("test marker")
    return d


def test_session_state_fresh_is_trusted():
    """T1 — session_state가 어제면 그대로 신뢰(마커 조회 불요)."""
    d = _with_marker_dir(marker_for=None)
    try:
        assert main._ts_resolve_p8_ok_date(_Y_ISO, _YESTERDAY, data_dir=d) == _Y_ISO
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_empty_falls_back_to_marker():
    """T2 — 빈 값 + 어제 마커 존재 → 어제로 폴백 (F-1 이전 롤오버 소실 커버).

    이 폴백이 없으면 진짜 스케일러 노후가 휴장/중단갭으로 오분류된다 —
    사고에서 '스케일러{n}h노후' 분기가 도달 불가였던 바로 그 경로다.
    """
    d = _with_marker_dir(marker_for=_YESTERDAY)
    try:
        assert main._ts_resolve_p8_ok_date("", _YESTERDAY, data_dir=d) == _Y_ISO
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_empty_without_marker_stays_empty():
    """T3 — 빈 값 + 마커 없음 → 빈 값 유지 (P8 실패일은 갭 태그가 옳다)."""
    d = _with_marker_dir(marker_for=None)
    try:
        assert main._ts_resolve_p8_ok_date("", _YESTERDAY, data_dir=d) == ""
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_stale_write_failure_covered_by_marker():
    """T4 — 낡은 값 + 어제 마커 존재 → 어제로 폴백.

    retrain_eod.py의 session_state 기록만 실패한 날("무해" 예외 경로,
    :195-196)을 덮는다 — 마커는 성공 시에만 쓰이므로 마커가 더 신뢰원천이다.
    """
    d = _with_marker_dir(marker_for=_YESTERDAY)
    try:
        assert main._ts_resolve_p8_ok_date(_STALE_ISO, _YESTERDAY, data_dir=d) == _Y_ISO
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_stale_without_marker_kept_as_is():
    """T5 — 낡은 값 + 마커 없음 → 낡은 값 유지 (어제 P8 미실행 = 갭 태그가 옳다)."""
    d = _with_marker_dir(marker_for=None)
    try:
        assert main._ts_resolve_p8_ok_date(_STALE_ISO, _YESTERDAY, data_dir=d) == _STALE_ISO
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_eks_block_uses_resolver():
    """T6 — 소스 수준 회귀 방어: EKS 원인 태깅 블록이 폴백 헬퍼를 부른다.

    호출이 빠지면(누군가 .get()으로 되돌리면) T1~T5가 전부 통과해도 실경로는
    사고 이전으로 돌아간다 — 471차 T8과 같은 방식으로 소스에 못 박는다.
    """
    main_path = os.path.join(_ROOT, "main.py")
    with open(main_path, encoding="utf-8") as f:
        src = f.read()
    anchor = src.find("_eks_causes = []")
    assert anchor != -1, "EKS 원인 태깅 블록(_eks_causes)이 main.py에서 사라졌다"
    window = src[anchor:anchor + 1500]
    assert "_ts_resolve_p8_ok_date(" in window, (
        "EKS 원인 태깅이 _ts_resolve_p8_ok_date() 폴백을 거치지 않는다 — "
        "session_state 단독 의존으로 회귀하면 스케일러 노후가 다시 "
        "휴장/중단갭으로 오분류된다 (0820 이상점 1-1)"
    )
