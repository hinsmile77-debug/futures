# 미륵이 대신증권 Cybos Plus 리팩토링 구현계획

## 목적

현재 미륵이는 키움 OpenAPI+ 중심으로 구현되어 있고, 브로커 API 의존이 `main.py`, `collection/kiwoom/*`, 일부 `strategy/*`, 대시보드 문구까지 넓게 퍼져 있다.

이 문서의 목표는 미륵이를 대신증권 `Cybos Plus` 기반으로 전환할 때,

- 어떤 구조로 리팩토링할지
- 어떤 순서로 구현할지
- 무엇을 먼저 검증해야 하는지
- 실제 작업용 TODO를 어떻게 나눌지

를 한 번에 실행 가능한 형태로 정리하는 것이다.

## 현재 구조 요약

확인한 핵심 결합 지점:

- [main.py](/abs/c:/Users/82108/PycharmProjects/futures/main.py:60)
  - `KiwoomAPI`, `RealtimeData`, `LatencySync`를 직접 import
  - 브로커 인스턴스 생성, 로그인, 잔고조회, 주문, 체결 반영까지 직접 제어
- [collection/kiwoom/api_connector.py](/abs/c:/Users/82108/PycharmProjects/futures/collection/kiwoom/api_connector.py:50)
  - 키움 COM/OCX 래퍼의 중심
  - 로그인, TR, 실시간, 주문, 체결 이벤트 처리 집중
- [collection/kiwoom/realtime_data.py](/abs/c:/Users/82108/PycharmProjects/futures/collection/kiwoom/realtime_data.py:43)
  - 키움 실시간 체결/호가 포맷에 직접 의존
- [strategy/entry/entry_manager.py](/abs/c:/Users/82108/PycharmProjects/futures/strategy/entry/entry_manager.py:33)
  - 타입 힌트와 주문 호출 모델이 키움 기준
- [strategy/exit/exit_manager.py](/abs/c:/Users/82108/PycharmProjects/futures/strategy/exit/exit_manager.py:32)
  - 청산 주문 경로가 키움 기준
- [collection/kiwoom/__init__.py](/abs/c:/Users/82108/PycharmProjects/futures/collection/kiwoom/__init__.py:1)
  - 상위 코드가 `collection.kiwoom` 패키지명 자체에 의존

현재 구조의 문제:

- 브로커 교체가 아니라 브로커 내부구현 + 상위 비즈니스 로직까지 함께 수정해야 한다.
- 실시간 이벤트 포맷과 주문 포맷이 전략/운영 로직에 스며들어 있다.
- `KiwoomAPI`를 대체하려면 동일 이름의 대체품을 억지로 맞추거나, 구조 자체를 한 번 추상화해야 한다.

## 리팩토링 목표

최종 목표는 "키움에서 사이보스로 갈아탄 미륵이"가 아니라, 아래 구조를 갖춘 "브로커 교체 가능한 미륵이"다.

- 브로커 공통 인터페이스 도입
- `KiwoomBroker` / `CybosBroker` 병렬 지원
- 실시간 시세, 호가, 주문, 체결, 잔고를 브로커 중립 모델로 정규화
- 전략 로직은 브로커명을 몰라도 동작
- 대시보드와 운영 로그는 브로커 차이를 표시하되, 핵심 로직은 공통 경로 사용

## 권장 전략

### 원칙

1. 키움 코드를 바로 삭제하지 않는다.
2. 먼저 브로커 추상화 계층을 만든다.
3. 그 다음 Cybos Plus 어댑터를 붙인다.
4. 마지막에 설정값으로 브로커를 선택하게 만든다.

### 이유

- 현재 미륵이는 실거래/체결/잔고 경로가 예민하다.
- 키움 경로를 보존해야 회귀검증 기준선이 생긴다.
- Cybos Plus 이슈가 생겨도 키움 경로로 빠르게 비교 가능하다.

## 목표 아키텍처

### 신규 패키지 구조 제안

```text
collection/
  broker/
    __init__.py
    base.py
    models.py
    event_bus.py
  kiwoom/
    ...
  cybos/
    __init__.py
    api_connector.py
    realtime_data.py
    investor_data.py
    balance.py
    order_adapter.py
```

### 핵심 인터페이스 초안

`collection/broker/base.py`

```python
class BrokerAPI:
    def connect(self) -> bool: ...
    def is_connected(self) -> bool: ...
    def get_account_list(self) -> list[str]: ...
    def request_futures_balance(self, account_no: str) -> dict: ...
    def subscribe_ticks(self, code: str) -> None: ...
    def unsubscribe_ticks(self, code: str) -> None: ...
    def subscribe_orderbook(self, code: str) -> None: ...
    def send_market_order(
        self,
        account_no: str,
        code: str,
        side: str,
        qty: int,
        reduce_only: bool = False,
    ) -> dict: ...
    def register_tick_callback(self, callback) -> None: ...
    def register_orderbook_callback(self, callback) -> None: ...
    def register_fill_callback(self, callback) -> None: ...
    def register_msg_callback(self, callback) -> None: ...
```

### 브로커 중립 데이터 모델

`collection/broker/models.py`

- `TickEvent`
- `OrderBookEvent`
- `OrderRequest`
- `OrderAck`
- `FillEvent`
- `PositionSnapshot`
- `BalanceSnapshot`

필수 원칙:

- 키움 FID, Cybos 필드명은 어댑터 내부에서만 사용
- 상위 레이어에는 정규화된 필드만 올린다
- `LONG/SHORT`, `BUY/SELL`, `OPEN/CLOSE`, `qty`, `avg_price`, `filled_qty` 같은 공통 의미로만 전달한다

## Cybos Plus 전환 시 주의점

사전 가정과 체크포인트:

- Windows 전용 COM 기반일 가능성이 높으므로 실행 환경 제약을 먼저 검증해야 한다.
- 현재 프로젝트는 키움 기준 32-bit Python/Windows 제약이 이미 강하다.
- Cybos Plus도 런타임, 관리자 권한, HTS 로그인 선행 여부, 실시간 수신 방식, 주문/체결 콜백 방식이 다를 수 있으므로 사전 스파이크가 필요하다.

즉, 구현 전에 아래를 먼저 확인해야 한다.

- Python 비트수 요구사항
- HTS/플러스 실행 및 로그인 선행 조건
- 선물 실시간 체결/호가 구독 가능 여부
- 선물 주문 API 지원 범위
- 체결/잔고 이벤트 수신 방식
- API 호출 제한과 reconnect 정책

## 단계별 구현계획

## Phase 0. 사전 조사 및 스파이크

### 목표

Cybos Plus로 선물 자동매매에 필요한 최소 기능이 실제로 가능한지 확인한다.

### 확인 항목

- 계좌 로그인 절차
- 선물 현재가/체결/호가 실시간 구독 방식
- 선물 종목코드 체계
- 잔고/미체결/체결 조회 API
- 시장가 진입/청산 주문 API
- 주문 접수/체결 이벤트 콜백
- 재연결 또는 세션 끊김 대응 방식

### 산출물

- `docs/cybos_plus_api_notes.md`
- 기능 매핑표
- "구현 가능 / 우회 필요 / 불가" 판정표

### 종료 기준

아래 5개가 모두 확인되면 다음 단계로 간다.

- 로그인 가능
- 선물 실시간 체결 수신 가능
- 선물 호가 수신 가능
- 선물 주문 전송 가능
- 체결 또는 잔고 반영 이벤트 확인 가능

## Phase 1. 브로커 추상화 도입

### 목표

상위 로직이 `KiwoomAPI` 대신 `BrokerAPI`를 바라보게 만든다.

### 작업 범위

- `collection/broker/base.py` 생성
- `collection/broker/models.py` 생성
- `collection/broker/__init__.py` 생성
- 키움 래퍼를 `KiwoomBroker` 어댑터로 감싸기
- `main.py`에서 직접 `KiwoomAPI()` 생성하지 않고 팩토리 사용

### 수정 대상 후보

- [main.py](/abs/c:/Users/82108/PycharmProjects/futures/main.py:60)
- [collection/kiwoom/api_connector.py](/abs/c:/Users/82108/PycharmProjects/futures/collection/kiwoom/api_connector.py:50)
- [collection/kiwoom/realtime_data.py](/abs/c:/Users/82108/PycharmProjects/futures/collection/kiwoom/realtime_data.py:43)
- [collection/kiwoom/__init__.py](/abs/c:/Users/82108/PycharmProjects/futures/collection/kiwoom/__init__.py:1)

### 종료 기준

- 키움 브로커가 새 인터페이스를 통해 기존 기능을 유지
- 기존 실시간 수신과 주문 경로가 회귀 없이 동작

## Phase 2. Cybos Plus 어댑터 구현

### 목표

키움과 동일한 `BrokerAPI` 인터페이스를 만족하는 `CybosBroker`를 구현한다.

### 작업 범위

- `collection/cybos/api_connector.py`
- `collection/cybos/realtime_data.py`
- `collection/cybos/balance.py`
- `collection/cybos/order_adapter.py`
- `collection/cybos/__init__.py`

### 구현 포인트

- Cybos 원시 이벤트를 `TickEvent`, `OrderBookEvent`, `FillEvent`로 정규화
- 주문 결과를 공통 응답 포맷으로 변환
- 실시간 구독/해지 인터페이스를 키움과 동일하게 제공
- 잔고/포지션 조회 결과를 현재 대시보드가 기대하는 필드로 맞춤

### 종료 기준

- 같은 상위 로직에서 `KiwoomBroker` 대신 `CybosBroker`만 바꿔도 실행 가능

## Phase 3. 메인 시스템 결합부 분리

### 목표

`main.py`의 브로커 직접 의존을 서비스 계층으로 떼어낸다.

### 작업 범위

- 브로커 생성 팩토리 도입
- 주문 헬퍼 `_send_kiwoom_entry_order`, `_send_kiwoom_exit_order`, `_KiwoomOrderAdapter` 제거 또는 일반화
- 체결 이벤트 후처리를 브로커 중립 핸들러로 이동
- 잔고조회 및 재동기화 로직 일반화

### 신규 구조 제안

```text
collection/broker/factory.py
services/broker_runtime.py
services/order_execution.py
services/balance_sync.py
```

### 수정 대상 후보

- [main.py](/abs/c:/Users/82108/PycharmProjects/futures/main.py:1669)
- [main.py](/abs/c:/Users/82108/PycharmProjects/futures/main.py:3990)

### 종료 기준

- `main.py`는 `broker.send_market_order(...)`, `broker.request_futures_balance(...)` 같은 공통 메서드만 호출
- 키움/사이보스 분기문이 `main.py`에 거의 남지 않음

## Phase 4. 전략 레이어 정리

### 목표

전략 코드가 더 이상 키움 클래스를 타입 힌트나 구현 가정으로 직접 참조하지 않게 만든다.

### 작업 범위

- `strategy/entry/entry_manager.py`의 `KiwoomAPI` 타입 힌트 제거
- `strategy/exit/exit_manager.py`의 `KiwoomAPI` 타입 힌트 제거
- 주문 결과 처리 포맷을 브로커 중립화
- 종목코드 하드코딩 제거

### 수정 대상 후보

- [strategy/entry/entry_manager.py](/abs/c:/Users/82108/PycharmProjects/futures/strategy/entry/entry_manager.py:33)
- [strategy/exit/exit_manager.py](/abs/c:/Users/82108/PycharmProjects/futures/strategy/exit/exit_manager.py:32)

### 종료 기준

- 전략 레이어는 `BrokerAPI` 또는 더 좁은 `OrderExecutor` 인터페이스만 사용

## Phase 5. 대시보드 및 운영도구 정리

### 목표

UI와 운영 로그에 남은 "키움 고정 문구"를 브로커 중립 표현으로 바꾼다.

### 작업 범위

- 상태 표시문구를 `브로커 연결`, `실시간 연결`, `주문 응답`, `체결 반영` 중심으로 수정
- 현재 브로커명을 UI 상단에 명시
- 키움 전용 장애 문구를 일반화

### 수정 대상 후보

- [dashboard/main_dashboard.py](/abs/c:/Users/82108/PycharmProjects/futures/dashboard/main_dashboard.py:454)
- [MIREUKI_OVERVIEW.md](/abs/c:/Users/82108/PycharmProjects/futures/MIREUKI_OVERVIEW.md:11)
- [README.md](/abs/c:/Users/82108/PycharmProjects/futures/README.md:4)

### 종료 기준

- 사용자가 현재 어떤 브로커로 실행 중인지 즉시 알 수 있음
- 장애 메시지가 특정 브로커 용어에 묶여 있지 않음

## Phase 6. 병행 운영 및 전환

### 목표

키움과 Cybos Plus를 병행 검증한 뒤 안전하게 기본 브로커를 전환한다.

### 롤아웃 순서

1. 키움 + 새 추상화 계층 회귀검증
2. Cybos 실시간 수신만 연결한 shadow 모드
3. Cybos 잔고조회/주문 모의 검증
4. Cybos 소량 실주문 검증
5. 기본 브로커 전환
6. 키움 경로 유지 여부 결정

### 종료 기준

- 장중 실시간 수신 안정성 확인
- 진입/청산/부분청산/긴급청산 전부 성공
- 재시작 후 포지션/잔고 재동기화 성공

## 브로커 기능 매핑표 초안

| 기능 | 현재 키움 구현 | 목표 공통 인터페이스 | Cybos 구현 메모 |
| --- | --- | --- | --- |
| 로그인 | `KiwoomAPI` 연결/로그인 | `connect()` | 세션/HTS 선행조건 확인 필요 |
| 연결상태 | 키움 상태 조회 | `is_connected()` | 연결상태 API 확인 |
| 선물 종목 조회 | 키움 방식 | `resolve_futures_code()` 또는 config | Cybos 종목 체계 조사 필요 |
| 틱 실시간 | `register_realtime()` | `subscribe_ticks()` | 실시간 체결 object 확인 |
| 호가 실시간 | `register_realtime()` | `subscribe_orderbook()` | 실시간 호가 object 확인 |
| 주문 | `send_order_fo()` | `send_market_order()` | 선물 주문 object 확인 |
| 체결 이벤트 | `OnReceiveChejanData` | `register_fill_callback()` | 주문/체결 callback 확인 |
| 잔고조회 | `request_futures_balance()` | `request_futures_balance()` | 선물 잔고 object 확인 |
| 메시지/오류 | `register_msg_callback()` | `register_msg_callback()` | 에러코드 매핑 필요 |

## 리스크와 대응

### 1. COM 이벤트 모델 차이

리스크:

- 키움과 Cybos의 이벤트 타이밍/콜백 구조가 다르면 현재 체결 후처리 로직이 깨질 수 있다.

대응:

- 이벤트를 바로 전략에 연결하지 말고 `FillEvent`로 한 번 정규화한다.

### 2. 선물 API 지원 차이

리스크:

- 주식 위주 예제는 많아도 선물 주문/잔고/실시간 지원이 제한적일 수 있다.

대응:

- Phase 0에서 선물 기능을 먼저 스파이크한다.

### 3. 재시작 동기화 실패

리스크:

- 장중 재시작 시 실제 포지션과 내부 상태 불일치가 발생할 수 있다.

대응:

- 브로커별 `PositionSnapshot` 정규화와 부팅 직후 강제 동기화 루틴을 만든다.

### 4. 운영 환경 제약

리스크:

- 32-bit Python, 관리자 권한, HTS 실행 순서 같은 환경 의존이 크다.

대응:

- 런처/체크리스트/운영 문서를 함께 갱신한다.

## 우선순위별 TODO

## A. 사전 조사

- [ ] Cybos Plus 선물 실시간 체결 API 지원 여부 확인
- [ ] Cybos Plus 선물 호가 API 지원 여부 확인
- [ ] Cybos Plus 선물 주문 API 지원 여부 확인
- [ ] 체결/잔고 이벤트 콜백 방식 확인
- [ ] Python 비트수/실행조건/로그인 선행조건 정리
- [ ] 종목코드 체계와 월물 전환 방식 정리
- [ ] 호출 제한/재연결 정책 정리
- [ ] 결과를 `docs/cybos_plus_api_notes.md`에 문서화

## B. 브로커 추상화

- [ ] `collection/broker/base.py` 생성
- [ ] `collection/broker/models.py` 생성
- [ ] `collection/broker/factory.py` 생성
- [ ] 공통 브로커 이벤트 콜백 등록 규약 정의
- [ ] 주문/체결/잔고 공통 응답 포맷 정의
- [ ] 키움 래퍼를 `KiwoomBroker`로 감싸는 어댑터 추가
- [ ] 키움 회귀테스트 체크리스트 작성

## C. Cybos 패키지 구현

- [ ] `collection/cybos/__init__.py` 생성
- [ ] `collection/cybos/api_connector.py` 생성
- [ ] `collection/cybos/realtime_data.py` 생성
- [ ] `collection/cybos/balance.py` 생성
- [ ] `collection/cybos/order_adapter.py` 생성
- [ ] Cybos 원시 이벤트를 공통 모델로 정규화
- [ ] Cybos 오류코드/메시지 매핑 작성

## D. 메인 결합부 리팩토링

- [ ] `main.py`의 키움 직접 import 제거
- [ ] 브로커 팩토리 기반 생성으로 변경
- [ ] `_KiwoomOrderAdapter`를 브로커 중립 어댑터로 교체
- [ ] `_send_kiwoom_entry_order()` 공통화
- [ ] `_send_kiwoom_exit_order()` 공통화
- [ ] 잔고조회/재동기화 로직 공통화
- [ ] 체결 후처리 로직을 브로커 이벤트 핸들러로 분리

## E. 전략 레이어 정리

- [ ] `EntryManager` 타입 힌트에서 키움 의존 제거
- [ ] `ExitManager` 타입 힌트에서 키움 의존 제거
- [ ] 종목코드 하드코딩 제거
- [ ] 주문 응답 처리 포맷 공통화
- [ ] 비정상 주문 응답 처리 규약 통일

## F. 대시보드 및 문서

- [ ] 대시보드 키움 전용 문구를 브로커 중립 문구로 변경
- [ ] 현재 사용 브로커 표시 추가
- [ ] README 브로커 구조 설명 갱신
- [ ] 운영 문서에 Cybos 실행 절차 추가
- [ ] 장애 대응 문서에 브로커별 체크리스트 추가

## G. 검증

- [ ] 키움 경로 회귀검증
- [ ] Cybos 로그인 검증
- [ ] Cybos 실시간 체결 수신 검증
- [ ] Cybos 호가 수신 검증
- [ ] Cybos 진입 주문 검증
- [ ] Cybos 청산 주문 검증
- [ ] Cybos 부분청산 검증
- [ ] Cybos 긴급청산 검증
- [ ] 재시작 후 포지션 재동기화 검증
- [ ] 장중 연결 끊김 후 복구 검증

## 추천 구현 순서

### Sprint 1

- Cybos 선물 API 가능 범위 조사
- 브로커 공통 인터페이스 설계
- 키움 경로를 새 인터페이스에 맞춰 래핑

### Sprint 2

- `main.py` 브로커 팩토리 전환
- 주문/체결/잔고 공통 모델 도입
- 키움 회귀검증

### Sprint 3

- Cybos 실시간 체결/호가 구현
- Cybos 잔고조회 구현
- Cybos 주문/체결 이벤트 구현

### Sprint 4

- 대시보드/문서 정리
- shadow 운영
- 소량 실주문 검증

### Sprint 5

- 기본 브로커 전환 여부 결정
- 키움 유지/제거 전략 결정

## 구현 우선순위 결론

가장 안전한 경로는 아래 순서다.

1. Cybos 선물 API 스파이크
2. 브로커 추상화 계층 도입
3. 키움을 새 인터페이스 위로 먼저 올리기
4. Cybos 어댑터 구현
5. `main.py` 결합부 제거
6. shadow 검증 후 실거래 전환

즉, 이번 작업의 핵심은 "키움 코드를 사이보스로 치환"하는 것이 아니라, "미륵이의 브로커 의존 구조를 분리한 뒤 Cybos Plus를 새 브로커로 꽂는 것"이다.
