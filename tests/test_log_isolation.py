"""[MW0601 422차] 테스트 실행이 프로덕션 로그·알림을 오염시키지 않는지 회귀 검증.

지키려는 불변식 — **테스트 모드에서는 로그 파일에 단 한 줄도 쓰지 않고,
Slack 큐에도 아무것도 넣지 않는다. 단, 검증 대상 로직 자체는 그대로 돈다.**

왜 필요한가: 2026-08-03 07:36~08:05에 `tests/test_circuit_breaker.py`가 5회
실행되며 프로덕션 로그(`20260803_SYSTEM.log`/`WARN.log`)에 CRITICAL CB 알림
30건을 남겼다 — `[CB] 당일 시스템 정지 | 연속 손절 3회`, `[CB] API 지연 6.0초
— 즉시 청산` 등. 그날 장중 370분은 전부 `state=NORMAL`이었고 실제 CB 발동은
0건이었다. 손익 영향은 없지만 **진짜 CB 발동이 그 노이즈에 묻힌다**는 것이
위험이고, 실전 전환 기준 ②(CB 1회 이상 정상 작동 확인)의 관측 신뢰도가
여기 걸려 있다.

이 파일이 깨지면 그 오염 경로가 되살아난 것이다. 가드를 지우고 싶어졌다면
`utils/runtime_mode.py`의 "왜 자동 감지를 쓰지 않는가"를 먼저 읽을 것.

실행: python tests/test_log_isolation.py   (COM/브로커 불필요)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["MIREUK_TEST_MODE"] = "1"  # [422차] 프로덕션 로그·Slack 오염 차단

import logging
import unittest
from unittest.mock import patch

from utils.runtime_mode import TEST_MODE_ENV, is_test_mode
from utils.logger import LAYER_SYSTEM, LAYER_WARN, setup_logging


def _log_path(layer):
    from datetime import date

    from config.settings import LOG_DIR

    return os.path.join(LOG_DIR, "%s_%s.log" % (date.today().strftime("%Y%m%d"), layer))


def _line_count(path):
    """파일이 없으면 0 — 로그가 아직 하루치도 안 생긴 환경에서도 동작해야 한다."""
    if not os.path.exists(path):
        return 0
    with open(path, "rb") as f:
        return sum(1 for _ in f)


class RuntimeModeTests(unittest.TestCase):
    def test_test_mode_is_active_under_harness(self):
        self.assertTrue(is_test_mode())

    def test_absent_env_means_production(self):
        """가드는 **명시적 opt-in만** 인정한다 — 환경변수가 없으면 프로덕션.

        이 방향(fail-safe = 프로덕션)이 뒤집히면 실제 운영에서 CB 경보가
        통째로 침묵할 수 있다. 08-03 노이즈보다 훨씬 나쁜 실패 모드다.
        """
        saved = os.environ.pop(TEST_MODE_ENV, None)
        try:
            self.assertFalse(is_test_mode())
            for falsy in ("0", "false", "no", "off", ""):
                os.environ[TEST_MODE_ENV] = falsy
                self.assertFalse(is_test_mode(), "%r는 비활성이어야 한다" % falsy)
        finally:
            if saved is None:
                os.environ.pop(TEST_MODE_ENV, None)
            else:
                os.environ[TEST_MODE_ENV] = saved
        self.assertTrue(is_test_mode())  # 원복 확인


class LogFileIsolationTests(unittest.TestCase):
    def test_no_file_handlers_in_test_mode(self):
        setup_logging()  # 이미 초기화됐으면 no-op
        for layer in (LAYER_SYSTEM, LAYER_WARN):
            handlers = logging.getLogger(layer).handlers
            self.assertTrue(handlers, "%s 로거에 핸들러가 하나도 없으면 "
                                      "lastResort가 stderr로 샌다" % layer)
            for h in handlers:
                self.assertIsInstance(
                    h, logging.NullHandler,
                    "%s에 %s가 붙어 있다 — 테스트가 파일/콘솔로 샌다"
                    % (layer, type(h).__name__),
                )

    def test_circuit_breaker_trigger_writes_nothing_to_log_files(self):
        """08-03 사건의 직접 재현 — CB를 실제로 발동시키고 로그 증가분을 센다."""
        from config.constants import CB_STATE_HALTED
        from safety.circuit_breaker import CircuitBreaker

        watched = [_log_path(LAYER_SYSTEM), _log_path(LAYER_WARN)]
        before = [_line_count(p) for p in watched]

        with patch("safety.circuit_breaker.CB_CONSEC_STOP_LIMIT", 3):
            cb = CircuitBreaker()
            cb.record_stop_loss()
            cb.record_stop_loss()
            cb.record_stop_loss()

        # 검증 대상 로직은 그대로 돌아야 한다 — 가드가 CB를 무력화하면 안 된다.
        self.assertEqual(cb.state, CB_STATE_HALTED)

        after = [_line_count(p) for p in watched]
        for path, b, a in zip(watched, before, after):
            self.assertEqual(a, b, "%s에 %d줄이 추가됐다 — 테스트가 프로덕션 "
                                   "로그를 오염시키고 있다" % (os.path.basename(path), a - b))


class SlackIsolationTests(unittest.TestCase):
    def test_notify_does_not_touch_slack_queue(self):
        import utils.notify as notify

        with patch.object(notify, "get_slack_queue") as mock_q:
            notify.notify_circuit_breaker("테스트 트리거", "테스트 조치")
            mock_q.assert_not_called()


if __name__ == "__main__":
    unittest.main()
