# 미륵이 대신증권 Cybos Plus 리팩토링 구현계획

## 목적

현재 미륵이는 원래 키움 OpenAPI+ 중심 구조였고, 이번 세션에서 `Cybos Plus`를 병행 가능한 브로커 백엔드로 연결했다.  
이 문서는 처음 계획 문서가 아니라, **현재 시점 기준 진행상황이 반영된 실행 계획 문서**다.

핵심 목표:

- 키움 전용 의존을 브로커 추상화 뒤로 이동
- `KiwoomBroker` / `CybosBroker` 병행 지원
- `main.py`를 브로커 중립 런타임으로 전환
- Cybos 실시간/주문/체결/잔고를 실제 운용 수준까지 검증

---

## 현재 진행상황 요약

### 완료된 항목

- `collection/broker/*` 브로커 추상화 계층 도입 완료
- `main.py`가 `create_broker()` 경유로 브로커를 생성하도록 전환 완료
- `BROKER_BACKEND` 설정값으로 `kiwoom` / `cybos` 선택 가능
- `collection/cybos/*` 기본 런타임 구현 완료
  - `CpUtil.CpCybos`
  - `CpTdUtil.TradeInit`
  - `CpTd0723` 잔고조회
  - `CpTd6831` 시장가 주문 경로
  - `CpFConclusion` 체결 이벤트 구독
  - `FutureCurOnly` / `FutureJpBid` 실시간 구독 래퍼
- `FutureMst` 스냅샷 필드 인덱스 실측 기준 보정 완료
- `scripts/check_cybos_session.py` 추가 완료
- `start_mireuk_cybos_test.bat` 시험운전 배치 추가 완료
- `main.py` Cybos 시작 시 로그인 계좌와 `secrets.py` 계좌가 다르면 런타임 계좌를 자동 전환하도록 보정 완료
- Cybos 시험 런처로 `main.py` UI 부팅 / startup sync / realtime start / Qt 루프 진입까지 확인 완료

### 아직 남은 항목

- 장중 `FutureCurOnly` 틱 / `FutureJpBid` 호가 실시간 이벤트 실검증
- `CpTd6831` 주문 후 `CpFConclusion` 체결 payload 실검증
- Cybos 수급 데이터(`investor_data`) 실TR 구현
- Cybos 서버구분 표시를 Kiwoom 호환값 우회가 아닌 브로커 인지형 로직으로 정리
- UI stylesheet parse warning 정리

---

## 현재 구조

### 브로커 계층

- [collection/broker/base.py](/abs/c:/Users/82108/PycharmProjects/futures/collection/broker/base.py:1)
- [collection/broker/factory.py](/abs/c:/Users/82108/PycharmProjects/futures/collection/broker/factory.py:1)
- [collection/broker/kiwoom_broker.py](/abs/c:/Users/82108/PycharmProjects/futures/collection/broker/kiwoom_broker.py:1)
- [collection/broker/cybos_broker.py](/abs/c:/Users/82108/PycharmProjects/futures/collection/broker/cybos_broker.py:1)
- [collection/broker/models.py](/abs/c:/Users/82108/PycharmProjects/futures/collection/broker/models.py:1)

### Cybos 구현

- [collection/cybos/api_connector.py](/abs/c:/Users/82108/PycharmProjects/futures/collection/cybos/api_connector.py:1)
- [collection/cybos/realtime_data.py](/abs/c:/Users/82108/PycharmProjects/futures/collection/cybos/realtime_data.py:1)
- [collection/cybos/investor_data.py](/abs/c:/Users/82108/PycharmProjects/futures/collection/cybos/investor_data.py:1)

### main 연결부

- [main.py](/abs/c:/Users/82108/PycharmProjects/futures/main.py:109)
- [config/settings.py](/abs/c:/Users/82108/PycharmProjects/futures/config/settings.py:22)

---

## 단계별 계획과 상태

## Phase 0. 사전 조사 / 스파이크

### 목표

Cybos Plus가 선물 자동매매에 필요한 최소 기능을 제공하는지 확인한다.

### 상태

- [DONE] 32비트 Python + `pywin32` 필요 조건 확인
- [DONE] Cybos Plus COM 객체 생성 가능 여부 확인
- [DONE] `CpUtil.CpCybos`, `CpTdUtil`, `CpFutureCode` 확인
- [DONE] `FutureCurOnly`, `FutureJpBid`, `FutureMst` 확인
- [DONE] `CpTd0723`, `CpTd6831`, `CpFConclusion` 사용 대상 확인
- [DONE] 모의투자 세션에서 `IsConnect=1`, `TradeInit=0` 확인
- [DONE] `CpTd0723` 무포지션 응답(`97007`) 해석 확인
- [DONE] `FutureMst` 필드 인덱스 실측 보정

### 산출물

- [scripts/check_cybos_session.py](/abs/c:/Users/82108/PycharmProjects/futures/scripts/check_cybos_session.py:1)
- [dev_memory/SESSION_LOG.md](/abs/c:/Users/82108/PycharmProjects/futures/dev_memory/SESSION_LOG.md:7)
- [dev_memory/DECISION_LOG.md](/abs/c:/Users/82108/PycharmProjects/futures/dev_memory/DECISION_LOG.md:7)

---

## Phase 1. 브로커 추상화 도입

### 목표

상위 로직이 `KiwoomAPI` 대신 `BrokerAPI`를 바라보게 만든다.

### 상태

- [DONE] `BrokerAPI` 인터페이스 도입
- [DONE] `create_broker()` 팩토리 도입
- [DONE] `KiwoomBroker` 래핑
- [DONE] `main.py` 브로커 팩토리 사용으로 전환
- [DONE] `BROKER_BACKEND` 설정값 도입
- [DONE] `EntryManager` / `ExitManager` 타입 의존 일부 완화

### 남은 작업

- [TODO] `main.py` 내부 키움 명명 흔적 정리
- [TODO] 주문/체결 런타임 로직을 서비스 계층으로 한 번 더 분리할지 결정

---

## Phase 2. CybosBroker 구현

### 목표

`BrokerAPI`를 만족하는 Cybos 런타임을 실제로 붙인다.

### 상태

- [DONE] `CybosBroker` 생성
- [DONE] `connect()`
- [DONE] `get_account_list()`
- [DONE] `get_nearest_futures_code()`
- [DONE] `request_futures_balance()`
- [DONE] `send_market_order()`
- [DONE] `register_fill_callback()`
- [DONE] `register_msg_callback()`
- [DONE] `create_realtime_data()`
- [DONE] `create_investor_data()` placeholder

### 남은 작업

- [TODO] `investor_data` 실TR 구현
- [TODO] 주문/체결 payload 실거래 흐름 검증 후 추가 보정

---

## Phase 3. 메인 런타임 연결

### 목표

`main.py`가 브로커 중립적으로 startup sync / 주문 / 실시간을 수행하도록 만든다.

### 상태

- [DONE] `connect_broker()` 경유 시작
- [DONE] startup broker sync가 Cybos 잔고 TR과 연결
- [DONE] Cybos 계좌 목록이 `secrets.py`와 다를 때 자동 fallback
- [DONE] `EmergencyExit` 주문 어댑터가 Cybos 계좌를 사용하도록 연결
- [DONE] 시험 런처에서 UI 부팅 및 Qt 루프 진입 확인

### 남은 작업

- [TODO] `GetServerGubun` 호환 우회 제거
- [TODO] 브로커별 서버 라벨 표시 분리

---

## Phase 4. 실시간 / 주문 / 체결 실검증

### 목표

장중에 Cybos가 실제로 틱/호가/주문/체결을 `main.py`와 UI에 반영하는지 확인한다.

### 상태

- [DONE] 실시간 구독 객체 생성 / 시작 로그 확인
- [DONE] 장외 상태(`state=99`)에서 스냅샷 값 정상 확인
- [PENDING] 장중 틱 수신 확인
- [PENDING] 장중 호가 수신 확인
- [PENDING] 모의 1계약 주문 확인
- [PENDING] 체결 이벤트가 포지션/UI에 반영되는지 확인

### 검증 방법

장중에 아래 순서로 확인:

1. [start_mireuk_cybos_test.bat](/abs/c:/Users/82108/PycharmProjects/futures/start_mireuk_cybos_test.bat:1) 실행
2. 가격 UI 갱신 여부 확인
3. `scripts/check_cybos_session.py --listen-sec 20` 재확인
4. `--send-order --side BUY --qty 1`로 모의 주문
5. `CpFConclusion` payload와 `main.py` pending order 처리 비교

---

## Phase 5. UI / 운영 정리

### 목표

Cybos 시험운전이 계속 가능하도록 운영 도구와 문서를 정리한다.

### 상태

- [DONE] Cybos 전용 시험운전 배치 추가
- [DONE] Cybos 세션 체크 스크립트 추가
- [DONE] 세션 메모 문서 반영

### 남은 작업

- [TODO] stylesheet parse warning 원인 수정
- [TODO] README / 운영 문서에 Cybos 시험운전 절차 반영 여부 결정
- [TODO] Cybos를 기본 브로커로 전환할 조건 정의

---

## 현재 리스크

### 1. 장중 실시간 미검증

- 현재까지는 주말 세션 기준 확인이라 장중 이벤트 루프가 실제로 들어오는지 아직 최종 확인 전

### 2. 주문/체결 payload 미세 차이 가능성

- `CpFConclusion`의 필드가 현재 `main.py` pending order 흐름과 100% 일치하는지는 실제 체결 케이스로 추가 검증 필요

### 3. 수급 데이터 미구현

- Cybos `investor_data`는 아직 no-op 상태

### 4. UI 경고 노이즈

- `Could not parse stylesheet ...` 경고가 디버깅 신호를 가릴 수 있음

---

## 추천 다음 순서

1. 장중 실시간 틱/호가 수신 확인
2. 모의 1계약 주문 / 체결 확인
3. 체결 payload 보정
4. Cybos `investor_data` 실구현
5. UI stylesheet warning 정리
6. 그 다음에야 `BROKER_BACKEND` 기본값 전환 여부 판단

---

## 최종 판단

현재 상태는:

- `Cybos Plus 연결 구현 완료`
- `main.py Cybos 부팅 성공`
- `잔고/스냅샷/계좌 fallback 완료`
- `장중 실시간 및 주문/체결 실검증만 남은 상태`

즉, 이번 작업은 아직 "키움 제거 완료"가 아니라  
**"Cybos를 병행 가능한 실행 백엔드로 올리고, 시험운전 가능한 상태까지 진입"**한 단계다.
