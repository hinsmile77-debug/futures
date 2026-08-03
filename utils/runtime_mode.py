# utils/runtime_mode.py — 실행 모드 판별 (프로덕션 / 테스트)
"""[MW0601 422차] 테스트 실행이 프로덕션 부작용을 내지 못하게 막는 단일 판별점.

## 왜 생겼나 — 2026-08-03 장전 CB 허위 알림 30건

08-03 07:36~08:05에 `[CRITICAL] [CB] 당일 시스템 정지 | 연속 손절 3회`,
`[CB] API 지연 6.0초 — 즉시 청산` 등 CRITICAL 6종이 5회(총 30건) 발화했다.
장중 370분은 전부 `state=NORMAL`이었고 실제 CB 발동은 0건이었다.

발화 주체는 `tests/test_circuit_breaker.py`였다. 이 테스트는 실제
`CircuitBreaker`를 구동하는데, CB의 알림·로그 경로가 프로덕션 싱글톤이라
다음 3개 경로로 실제 부작용이 나갔다:

  1. `logger.critical/warning` (`logging.getLogger("SYSTEM")`) → `YYYYMMDD_SYSTEM.log` / `WARN.log`
  2. `log_manager.system(msg, "CRITICAL")` → `_write_to_file` → 같은 파일
  3. `notify_circuit_breaker()` → `utils.notify._send()` → Slack 큐

문구가 "연속 손절 3회"인 것이 결정적 단서였다 — 운영값
`CB_CONSEC_STOP_LIMIT = 9999`(모의투자 한정 예외) 아래에서는 진짜 트리거가
그 문구를 만들 수 없고, 테스트가 모듈 상수를 3으로 patch하기 때문에만 나온다.

**손익 영향은 없다. 위험한 것은 진짜 CB 발동이 이 노이즈에 묻히는 것**이고,
실전 전환 기준 ②(CB 1회 이상 정상 작동 확인)의 관측 신뢰도가 여기 걸려 있다.

## 왜 "자동 감지"를 쓰지 않는가 (재론 금지)

`"pytest" in sys.modules` / `sys.argv[0]` 패턴매칭 같은 휴리스틱 감지는
쓰지 않는다. **오탐 한 번이면 프로덕션에서 CB 경보가 통째로 침묵**하는데,
그것은 지금 고치려는 문제(노이즈)보다 훨씬 나쁜 실패 모드다. 이 판별은
`MIREUK_TEST_MODE` 환경변수 **명시적 opt-in만** 인정하며, 변수가 없으면
언제나 프로덕션으로 판정한다(fail-safe 방향이 프로덕션).

테스트 쪽 활성화는 두 겹으로 걸어둔다:
  - `tests/conftest.py` — pytest 실행 시 자동 (test 모듈 import보다 먼저)
  - 각 테스트 파일 상단 2줄 — `python tests/test_x.py` 직접 실행 대비

## 주의

이 모듈은 **프로젝트 내부 import를 하지 않는다**. `utils.logger`가
`config.settings`를 import하고 로그 초기화가 그보다 앞서야 하므로,
순환 import를 원천 차단하기 위해 표준 라이브러리만 쓴다.
"""
import os

#: 테스트 모드를 켜는 환경변수. 값이 있고 "0"/"false"/"" 가 아니면 활성.
TEST_MODE_ENV = "MIREUK_TEST_MODE"

_FALSY = {"", "0", "false", "no", "off"}


def is_test_mode() -> bool:
    """테스트 실행 중이면 True.

    환경변수를 **호출 시점마다** 읽는다(캐시하지 않음) — conftest·테스트 헤더가
    import 순서에 따라 늦게 설정될 수 있는데, 캐시하면 그 설정이 무시된다.
    비용은 dict 조회 1회라 프로덕션 경로에서도 무시할 수 있다.
    """
    return str(os.environ.get(TEST_MODE_ENV, "")).strip().lower() not in _FALSY


def enable_test_mode() -> None:
    """테스트 하네스에서 호출 — 프로덕션 부작용(로그 파일·Slack)을 차단한다.

    `setdefault`가 아니라 명시 대입이다. 이미 "0"으로 꺼둔 채 테스트를 돌리는
    경우가 오염의 원인이 되므로, 테스트 하네스의 의도를 우선한다.
    """
    os.environ[TEST_MODE_ENV] = "1"
