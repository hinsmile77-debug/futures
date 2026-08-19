# -*- coding: utf-8 -*-
"""[MW0601 478차 후속 / FZ-1·FZ-3·FZ-4] 메인 이벤트 루프 동결 워치독 회귀 고정.

## 무엇을 지키는가

2026-08-19 13:41:21, 메인(Qt) 스레드가 `_qt_app.exec_()` 아래 네이티브 코드에서
스핀에 빠져 QTimer 전부가 죽었다 — 매분 파이프라인, 15:10 강제청산(절대원칙 §1),
453차 D2 SchedForceExit 안전망, CB⑤, 그리고 15:40 자동종료까지. 프로그램이 끝나지
않은 것은 그 결과였다.

이 테스트가 고정하는 불변식은 셋이다:

  ① 판정 로직 — 오탐(정상 블로킹)과 미탐(진짜 동결) 경계, 그리고 "연속" 정의
  ② 배선 — 하트비트 갱신 지점이 실제로 존재하고, 감시자가 이벤트 루프 **밖**에 있을 것
     (누군가 QTimer로 되돌리면 이번 사고를 그대로 재현한다)
  ③ 워커 이상 소요 가드(FZ-4) 임계가 정상 실측(1.5초)과 병리(601초) 사이에 있을 것

⚠ 실제 동결을 유발하는 통합 리허설은 이 테스트로 대체되지 않는다 —
   절차는 `dev_memory/NEXT_TODO.md` FZ-1 항목 참조(sleep 주입 → 재기동 확인).
"""
import datetime
import os
import re
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.freeze_watchdog import FreezeWatchdog, evaluate, in_window  # noqa: E402


# ── ① 판정 로직 ────────────────────────────────────────────────────────────

def test_정상_하트비트는_스트라이크를_쌓지_않는다():
    assert evaluate(5.0, 180.0, 0, 2, True) == (0, False)


def test_실측_최장_정상블로킹은_오탐하지_않는다():
    """2026-07-30 _tick_header 9.5초 / 2026-06-26 수급 7.2초 / 2026-08-10 CB⑤ 7.6초.

    이 셋은 전부 '정상 범위의 느림'이며 워치독이 건드리면 안 된다.
    """
    for age in (7.2, 7.6, 9.5, 60.0, 179.9):
        assert evaluate(age, 180.0, 0, 2, True) == (0, False), age


def test_1회_초과로는_발화하지_않는다_연속_2회가_조건():
    strikes, fire = evaluate(200.0, 180.0, 0, 2, True)
    assert (strikes, fire) == (1, False)
    strikes, fire = evaluate(230.0, 180.0, strikes, 2, True)
    assert (strikes, fire) == (2, True)


def test_중간에_하트비트가_돌아오면_스트라이크가_리셋된다():
    strikes, _ = evaluate(200.0, 180.0, 0, 2, True)
    assert strikes == 1
    strikes, fire = evaluate(3.0, 180.0, strikes, 2, True)      # 되살아남
    assert (strikes, fire) == (0, False)
    strikes, fire = evaluate(200.0, 180.0, strikes, 2, True)    # 다시 1부터
    assert (strikes, fire) == (1, False)


def test_하트비트_미시작은_동결로_보지_않는다():
    """기동 중(이벤트 루프 진입 전)을 동결로 오인하면 부팅 자체가 불가능해진다.

    계측 4원칙 ② — '미측정'과 '값이 0'을 같게 표현하지 않는다.
    """
    assert evaluate(None, 180.0, 5, 2, True) == (0, False)


def test_감시구간_밖이면_스트라이크가_리셋된다():
    """구간 경계를 걸친 누적이 다음 날 첫 검사에서 오발화하는 것을 막는다."""
    assert evaluate(9999.0, 180.0, 1, 2, False) == (0, False)


def test_감시구간_판정():
    w = ("09:00", "15:45")
    assert in_window(datetime.time(9, 0), w)
    assert in_window(datetime.time(13, 41), w)
    assert in_window(datetime.time(15, 45), w)
    assert not in_window(datetime.time(8, 59), w)
    assert not in_window(datetime.time(15, 46), w)


def test_구간설정이_깨지면_감시를_끄지_않고_항상_감시한다():
    """설정 오타로 감시가 조용히 사라지는 쪽이 더 위험하다(계측 4원칙 ④)."""
    assert in_window(datetime.time(3, 0), None)
    assert in_window(datetime.time(3, 0), ("이상한값", "15:45"))


# ── 발화 경로 (os._exit 가로채기) ────────────────────────────────────────────

def test_발화하면_fault로그에_기록하고_on_fire를_부른다(tmp_path):
    log = str(tmp_path / "crash_fault.log")
    fired = []
    wd = FreezeWatchdog(
        beat_fn=lambda: 0.0,                 # epoch 0 → 나이가 사실상 무한
        active_fn=lambda: True,
        context_fn=lambda: "  position=SHORT 1ct  **미청산=예**",
        on_fire=lambda: fired.append(True),  # os._exit 대체
        stall_sec=180.0, strikes=2, window=None,
        fault_log_path=log, ts_heartbeat=False,
    )
    assert wd.check_once() is False          # 1스트라이크
    assert fired == []
    assert wd.check_once() is True           # 2스트라이크 → 발화
    assert fired == [True]

    text = open(log, encoding="utf-8", errors="replace").read()
    assert "CRITICAL" in text
    # 15:10 이후 발화 시 런처가 재기동하지 않으므로, 미청산 여부가 반드시 남아야 한다.
    assert "미청산=예" in text


def test_active_fn이_False면_발화하지_않는다(tmp_path):
    """자동종료 완료·비거래일 — 이벤트 루프가 멈추는 것이 정상인 상태."""
    fired = []
    wd = FreezeWatchdog(
        beat_fn=lambda: 0.0, active_fn=lambda: False,
        on_fire=lambda: fired.append(True),
        stall_sec=180.0, strikes=1, window=None,
        fault_log_path=str(tmp_path / "f.log"), ts_heartbeat=False,
    )
    assert wd.check_once() is False
    assert fired == []


def test_active_fn이_예외를_던져도_감시는_계속된다(tmp_path):
    """판단 실패로 감시가 꺼지면 안 된다 — 실패는 '감시 계속' 쪽으로 편향시킨다."""
    def _boom():
        raise RuntimeError("판단 불가")
    fired = []
    wd = FreezeWatchdog(
        beat_fn=lambda: 0.0, active_fn=_boom,
        on_fire=lambda: fired.append(True),
        stall_sec=180.0, strikes=1, window=None,
        fault_log_path=str(tmp_path / "f.log"), ts_heartbeat=False,
    )
    assert wd.check_once() is True
    assert fired == [True]


def test_한글과_em대시가_섞여도_기록이_유실되지_않는다(tmp_path):
    """py37_32의 기본 인코딩은 cp949이고 cp949는 em dash(—)를 못 쓴다.

    `open(path, "a")`(인코딩 미지정)로 두면 UnicodeEncodeError가 나고 예외 방어가
    그것을 삼켜 **발화 기록이 통째로 사라진다**(개발 중 실측). 동결 프로세스의
    마지막 증언이므로 유실이 곧 실명이다.
    """
    log = str(tmp_path / "crash_fault.log")
    wd = FreezeWatchdog(
        beat_fn=lambda: 0.0, on_fire=lambda: None,
        stall_sec=180.0, strikes=1, window=None,
        fault_log_path=log, ts_heartbeat=False,
    )
    wd.check_once()
    text = open(log, encoding="utf-8", errors="replace").read()
    assert "CRITICAL" in text and "동결" in text


def test_ts_하트비트가_fault로그에_시각을_남긴다(tmp_path):
    """[FZ-5] faulthandler 덤프 블록에는 타임스탬프가 없어 08-19 분석에서 시각을
    블록 개수로 역산해야 했다. 30초마다 [TS] 한 줄이 그 문제를 없앤다."""
    log = str(tmp_path / "crash_fault.log")
    import time as _t
    wd = FreezeWatchdog(
        beat_fn=lambda: _t.time(), window=None,
        fault_log_path=log, ts_heartbeat=True,
    )
    wd.check_once()
    assert "[TS]" in open(log, encoding="utf-8", errors="replace").read()


# ── ② 배선 불변식 ──────────────────────────────────────────────────────────

def _main_src():
    with open(os.path.join(_ROOT, "main.py"), encoding="utf-8") as f:
        return f.read()


def test_하트비트_갱신_지점이_최소_3곳_존재한다():
    """5초 전용 타이머 / 30초 스케줄러 / 매분 파이프라인 — 삼중화.

    하나만 남기면 그 경로가 막힐 때 워치독이 **오탐으로 거래를 끊는다**.
    """
    src = _main_src()
    assert len(re.findall(r"self\._main_beat\s*=\s*time\.time\(\)", src)) >= 3


def test_워치독은_이벤트루프_밖_스레드다_QTimer로_되돌리면_실패한다():
    """누군가 FreezeWatchdog을 QTimer로 옮기면 2026-08-19 사고가 그대로 재현된다.

    이 시스템의 안전장치는 전부 '메인 이벤트 루프 생존'을 암묵 전제로 쌓여 있고,
    그 전제가 깨진 것이 이번 사고다. 감시자만은 그 전제 밖에 있어야 한다.
    """
    with open(os.path.join(_ROOT, "utils", "freeze_watchdog.py"), encoding="utf-8") as f:
        src = f.read()
    assert "threading.Thread" in src
    # 산문(docstring)에는 QTimer를 언급한다 — 사고 경위 설명이다. 금지되는 것은
    # **의존**이므로 import 문만 본다.
    assert not re.search(r"^\s*(from|import)\s+PyQt5", src, re.M)


def test_하트비트_0값이_미측정으로_오독되지_않는다():
    """`if not beat` 로 쓰면 epoch 0.0이 falsy라 '하트비트 없음'과 같아진다.

    그 둘은 정반대 결과를 낸다(판정 보류 vs 발화). 계측 4원칙 ②.
    """
    import time as _t
    fired = []
    wd = FreezeWatchdog(
        beat_fn=lambda: 0.0, on_fire=lambda: fired.append(True),
        stall_sec=180.0, strikes=1, window=None, ts_heartbeat=False,
        fault_log_path=None,
    )
    assert wd.check_once() is True and fired == [True]

    fired2 = []
    wd2 = FreezeWatchdog(
        beat_fn=lambda: None, on_fire=lambda: fired2.append(True),
        stall_sec=180.0, strikes=1, window=None, ts_heartbeat=False,
        fault_log_path=None,
    )
    assert wd2.check_once() is False and fired2 == []


def test_워치독이_이벤트루프_진입_전에_기동된다():
    """`exec_()` 다음에 두면 영원히 실행되지 않는다."""
    src = _main_src()
    i_start = src.index("self._start_freeze_watchdog()")
    i_exec = src.index("_qt_app.exec_()")
    assert i_start < i_exec


def test_옵션체인_타이머는_다른_COM타이머와_위상이_분리돼_있다():
    """[FZ-3] 수급·지수 타이머와 같은 초에 만료하면 COM 활동이 한 초에 몰린다.

    08-19 동결은 그 초(:21)에 시작된 옵션 워커 기동과 1초 이내로 일치했다.
    """
    src = _main_src()
    assert re.search(
        r"QTimer\.singleShot\(\s*\d+_?\d*\s*,\s*self\._option_chain_timer\.start\s*\)", src
    ), "옵션 체인 타이머가 오프셋 없이 즉시 start() 되고 있다 — FZ-3 회귀"


# ── ③ 워커 이상 소요 가드 (FZ-4) ───────────────────────────────────────────

def test_워커_가드_임계가_정상과_병리_사이에_있다():
    """정상 실측 1,461~1,628ms(08-19 30회) < 임계 < 병리 601,493ms(08-19 동결)."""
    from collection.options.option_chain_worker import (
        _COLLECT_ABORT_SEC, _RESULT_DISCARD_SEC,
    )
    assert 1.7 < _RESULT_DISCARD_SEC < 601.0
    assert _RESULT_DISCARD_SEC <= _COLLECT_ABORT_SEC < 601.0


def test_이상소요면_피처를_폐기한다():
    """빈 dict 반환 → OptionChainSnapshot이 '이전 피처 유지'로 처리한다.

    병리값(PCR=0.103 / GEX=+169B)을 쓰는 것보다 안 쓰는 것이 낫다.
    08-19에 그 값이 저장되지 않은 것은 설계가 막아서가 아니라 우연이었다
    (죽은 메인 루프에 Qt 큐드 시그널이 배달되지 못했을 뿐).
    """
    from collection.options import option_chain_worker as w

    snap = w.OptionChainSnapshot if hasattr(w, "OptionChainSnapshot") else None
    assert snap is None    # 워커 모듈은 스냅샷을 모른다(관심사 분리 확인)

    from collection.options.option_chain_snapshot import OptionChainSnapshot
    s = OptionChainSnapshot()
    s._last_features = {"opt_chain_pcr": 1.0, "opt_chain_available": 1.0}
    s.on_worker_done({}, [])                       # 폐기된 결과 수신
    assert s.get_features()["opt_chain_pcr"] == 1.0    # 이전 피처 유지


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
