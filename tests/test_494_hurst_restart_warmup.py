# -*- coding: utf-8 -*-
"""[MW0602 494차] F-5 회귀 — 장중 재기동 시 Hurst 워밍업 버퍼 복원.

**무엇을 고정하는가.**

① 재기동(빈 버퍼)에 당일 분봉을 주입하면 `hurst_ready`가 **즉시** True가 된다.
   — 0825 12:20:58 A등급 후보가 `[차단] Hurst 미계산 — 워밍업 중`으로 사라진 자리.
② 정상 기동일(버퍼가 이미 차 있음)에는 **아무 일도 일어나지 않는다.**
   — 계측·복원이 정상 경로를 바꾸면 그 자체가 회귀다.
③ 파라미터 3종은 **소스에서** 읽어 확인한다. 317차 4단계 검증으로 잡은 값이고
   26주 WFA 재검증 항목이라, 이 작업이 곁다리로 건드리지 않았음을 고정한다.

실행:
    python tests/test_494_hurst_restart_warmup.py
"""
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAILURES = []


def _read(rel):
    with io.open(os.path.join(_ROOT, rel), encoding="utf-8") as f:
        return f.read()


def _fb():
    from features.feature_builder import FeatureBuilder
    return FeatureBuilder()


def test_restart_restores_buffer_and_readiness():
    from config.settings import HURST_WARMUP_COLDSTART_MIN, HURST_WINDOW_N

    fb = _fb()
    assert len(fb._close_history) == 0, "재기동 직후는 빈 버퍼여야 한다(전제)"

    closes = [330.0 + (i % 7) * 0.05 for i in range(HURST_WARMUP_COLDSTART_MIN + 5)]
    n = fb.set_intraday_close_history(closes)
    assert n == len(closes), n
    assert len(fb._close_history) == len(closes)
    # 이 시점에 파이프라인이 돌면 hurst_ready=True 경로로 들어간다.
    assert len(fb._close_history) >= HURST_WARMUP_COLDSTART_MIN

    # maxlen 초과분은 앞에서 밀린다 — 최신 N개만 남아야 한다.
    fb2 = _fb()
    long_closes = [330.0 + i * 0.01 for i in range(HURST_WINDOW_N + 40)]
    fb2.set_intraday_close_history(long_closes)
    assert len(fb2._close_history) == HURST_WINDOW_N
    assert fb2._close_history[-1] == long_closes[-1], "최신 봉이 남아야 한다"


def test_no_op_when_buffer_already_warm():
    """정상 기동일 동작 불변 — 이미 찬 버퍼는 덮어쓰지 않는다."""
    fb = _fb()
    fb._close_history.append(300.0)
    fb._close_history.append(301.0)
    before = list(fb._close_history)
    assert fb.set_intraday_close_history([999.0] * 50) == 0
    assert list(fb._close_history) == before


def test_empty_and_bad_input_are_safe():
    fb = _fb()
    assert fb.set_intraday_close_history(None) == 0
    assert fb.set_intraday_close_history([]) == 0
    assert fb.set_intraday_close_history([0, 0.0, None]) == 0
    assert len(fb._close_history) == 0


def test_reset_daily_still_clears_buffer():
    """317차가 넣은 일일 리셋을 깨지 않았는가 — 깨면 전일 종가가 창에 섞인다."""
    fb = _fb()
    fb.set_intraday_close_history([330.0 + i * 0.01 for i in range(50)])
    fb.reset_daily()
    assert len(fb._close_history) == 0


def test_call_site_is_inside_intraday_branch():
    """🔴 호출이 **장중 분기 안**에 있어야 한다 — 09:00 이전 기동에서 부르면
    전일 봉이 없더라도 이 경로가 정상 콜드스타트를 건드릴 여지를 만든다."""
    src = _read("main.py")
    i_restart = src.find("[RESTART] 장중 재시작 감지")
    i_call = src.find("_load_intraday_close_history_at_restart()")
    assert i_restart > 0 and i_call > i_restart, "재기동 로그 뒤에서 호출돼야 한다"
    # `if is_market_open(_startup_now):` 블록 안인지 — 들여쓰기로 확인
    line = src[src.rfind("\n", 0, i_call) + 1:i_call]
    assert line.startswith("            "), "장중 분기(12칸 들여쓰기) 안이어야 한다: %r" % line
    # 당일만 조회하는가 (전일 종가 오염 금지)
    assert 'WHERE ts >= ? AND ts < ?' in src
    assert '_today + "Z"' in src


def test_hurst_params_untouched():
    """317차 파라미터 3종 무변경 — 26주 WFA 재검증 항목이다."""
    s = _read("config/settings.py")
    for name, val in (("HURST_WINDOW_N", "90"),
                      ("HURST_MAX_LAG", "9"),
                      ("HURST_WARMUP_COLDSTART_MIN", "40")):
        assert ("%s = %s" % (name, val)) in s, "%s 가 %s 가 아니다" % (name, val)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    for fn in (test_restart_restores_buffer_and_readiness,
               test_no_op_when_buffer_already_warm,
               test_empty_and_bad_input_are_safe,
               test_reset_daily_still_clears_buffer,
               test_call_site_is_inside_intraday_branch,
               test_hurst_params_untouched):
        try:
            fn()
            print("[ok]   %s" % fn.__name__)
        except Exception as e:
            print("[FAIL] %s: %r" % (fn.__name__, e))
            FAILURES.append(fn.__name__)
    print("-" * 60)
    print("전부 통과" if not FAILURES else "실패 %d건: %s" % (len(FAILURES), FAILURES))
    sys.exit(1 if FAILURES else 0)
