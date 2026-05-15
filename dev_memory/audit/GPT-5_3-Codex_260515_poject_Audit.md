# Mireuk Project Audit Report

- Audit date: 2026-05-15
- Auditor: GitHub Copilot (GPT-5.3-Codex)
- Scope: Full repository structure, operational risk, architecture quality, robustness roadmap

## 1) 프로젝트 전체 구조 분석

### 1.1 시스템 성격
본 프로젝트는 단순 전략 스크립트가 아니라 실거래 운영형 플랫폼에 가깝다.
- 브로커 계층: Cybos/Kiwoom 병행 구조
- 실시간 수집: 틱/호가/분봉/수급/매크로
- 피처 엔진: 기술/옵션/매크로/미시구조
- 모델/의사결정: 멀티호라이즌 + 앙상블 + 게이트
- 안전장치: Circuit Breaker, Kill Switch, Emergency Exit, Profit Guard
- 운영 UI: PyQt 대시보드
- 학습/검증: 온라인 학습, 배치 재학습, 백테스트

### 1.2 구조적 강점
- Broker Factory 도입으로 백엔드 전환 가능성 확보
- 안전장치 계층이 명시적으로 존재
- 파이프라인 개념(매분 9단계)이 운영 문서와 코드에 반영
- 수익/예측/리스크 관련 DB 분리 저장으로 관측성 기반은 존재

### 1.3 구조적 병목
- main.py 중심의 제어 집중(연결, 파이프라인, 주문, 복원, UI 동기화까지 집약)
- dashboard/main_dashboard.py 비대화로 UI와 운영로직 경계 약화
- 문서와 실제 코드의 괴리(README 일부 경로/모듈 설명이 최신 구조와 불일치)

## 2) 핵심 문제점 (근거 중심)

### P0. 런타임 오케스트레이션 집중
- main.py가 과도한 책임을 보유
- 영향: 변경 반경 확대, 장애 원인 고립 어려움, 회귀 위험 증가

### P1. 예외 처리 전략 과완화
- broad except Exception 다수 사용(핵심 파일에 집중)
- 영향: 치명 오류와 복구 가능 오류가 동일하게 처리되어 상태 왜곡 가능

### P2. 문서-코드 동기화 부족
- README가 키움 중심/과거 구조를 일부 유지
- 실제 운영은 AGENTS/CLAUDE 규칙(런처 사용, 환경 고정)에 더 의존
- 영향: 온보딩/핸드오프 실패 위험

### P3. 브로커 중립화 미완료
- 코드 내 legacy naming/connect_kiwoom alias/kiwoom 참조 흔적 잔존
- 영향: 백엔드 전환 시 유지보수 혼선, 장애 대응 시 해석 비용 증가

### P4. 테스트 체계 부재
- pytest/unittest 기반 자동 회귀 검증 없음
- 영향: 실거래 전 변경 검증 비용 증가, 품질 편차 확대

### P5. 외부 데이터 품질 관리 약함
- 매크로 수집 실패 시 더미/폴백이 가능하나 품질 상태가 전략 판단에 충분히 강제 반영되지 않음
- 영향: 데이터 저품질 상태의 의사결정 위험

## 3) 강건한 개선안 (Robust)

### R1. main.py 책임 분해 (최우선)
아래 서비스로 단계 분리:
1. BrokerRuntimeService
2. MinutePipelineService
3. OrderLifecycleService
4. SessionRecoveryService

효과: 장애 격리, 변경 범위 축소, 검증 가능성 상승

### R2. 예외 정책 3계층화
- recoverable: 피처 일부 실패, 폴백 허용
- degraded: 데이터 품질 저하/지연 증가, 진입 축소 또는 수동모드
- fatal: 주문/포지션 동기화 실패, 즉시 진입 차단/비상모드

효과: "안 죽지만 망가진 상태"를 방지

### R3. 문서 단일 진실원천 체계
- README: 현재 구조/실행법만
- AGENTS/CLAUDE: 운영 절대규칙
- CYBOS_PLUS_REFACTOR_PLAN: 이관 진행상태

효과: 운영 혼선 제거, 인수인계 안정화

### R4. 브로커 Capability Matrix 도입
항목별 지원/검증 상태를 명시:
- connect, balance, order, fill-callback, tick, hoga, investor-tr, server-label

효과: "구현됨"과 "검증됨"을 분리 관리

### R5. 최소 회귀 테스트 도입
우선순위(순수 로직 위주):
- 앙상블 판단
- 체크리스트/게이트
- 서킷브레이커 트리거
- 포지션 사이징

효과: 전략/리스크 로직 변경의 안전장치 확보

### R6. 데이터 품질 플래그 강제 반영
feature bundle에 source/age/stale/fallback_used/supported 포함
-> STEP6 진입결정에 quality score 연동

효과: 저품질 데이터 환경에서 자동 방어 강화

## 4) 기발한 고도화안 (Creative Upgrade)

### U1. Alpha Engine vs Execution Governor 이원화
- Alpha Engine: 방향/확률 생성
- Execution Governor: 실행가능성(품질/지연/독성/브로커 상태/세션건강) 판단

효과: 모델 성능과 실행 리스크를 독립 최적화

### U2. Tradability Score 도입
confidence 단일값 대신 아래 결합 점수 사용:
tradability = f(confidence, data_quality, latency, toxicity, session_health)

효과: 진입/사이징/자동모드 결정의 실전 적합도 상승

### U3. Challenger 확장
전략만이 아니라 실행 정책도 shadow 비교:
- execution policy challenger
- risk policy challenger
- entry filter challenger

효과: 실전 리스크 없이 운영정책 진화 가능

### U4. 장애 재현 패킷(Replay Pack)
장애 시점의 bar/hoga/features/broker-state/pending-order/UI-mode를 묶어 저장

효과: 다음 세션 재현/원인규명 시간 대폭 단축

### U5. 시스템 헬스 대시보드 분리
PnL/예측과 별개로 운영 건강 지표 상시 표시:
- tick/hoga gap
- TR latency
- cache age
- investor fetch success ratio
- exception density

효과: 알파 저하와 시스템 저하를 즉시 분리 진단

## 5) 실행 우선순위 (권장)
1. main.py, dashboard/main_dashboard.py 책임 분해 설계 확정
2. 예외 처리 3계층 정책 도입
3. 문서 동기화(README/운영문서)
4. 브로커 Capability Matrix + 장중 검증 체크리스트
5. 순수로직 회귀 테스트 최소세트 구축
6. Tradability Score 및 Execution Governor 적용

## 6) 결론
현재 프로젝트는 기능 폭은 매우 넓고 운영 노하우도 축적되어 있으나,
핵심 리스크는 "중앙집중 제어 + 완화된 예외 처리 + 문서 괴리 + 테스트 부재"다.

위 개선안을 순서대로 적용하면,
- 장애 대응력
- 변경 안전성
- 백엔드 전환 안정성
- 실거래 운영 신뢰성
이 동시에 향상된다.

## 7) 즉시 실행 가능한 2주 액션플랜 (파일 단위)

### 운영 원칙
- 절대원칙(15:10 강제청산, CORE 3피처, COM 콜백 안전) 위배 변경 금지
- 실행/검증은 start_mireuk.bat 기준으로 수행
- 각 작업은 완료 조건(DoD) 충족 시에만 다음 단계로 진행

### Week 1 (구조 안정화 + 리스크 격리)

#### Day 1: 분해 설계 고정
1. 파일: main.py
	작업: TradingSystem 책임을 4개 서비스 경계로 주석/섹션 라벨링
	완료조건: connect/pipeline/order/recovery 흐름이 코드 상에서 분리 지점으로 명확화
2. 파일: dev_memory/audit/GPT-5_3-Codex_260515_poject_Audit.md
	작업: 분해 기준(서비스 경계/입출력) 확정 메모 추가
	완료조건: 다음 개발자가 그대로 분해 착수 가능

##### Day 1 구현 메모 (확정 경계/입출력)
아래 4개 서비스 경계를 main.py에 라벨로 반영했다.

1. BrokerRuntimeService
	입력: 계좌설정, 대시보드 종목선택, broker backend 상태
	출력: 실거래 코드(_futures_code), realtime_data, investor timer, startup sync 상태
	핵심 함수: connect_broker()

2. MinutePipelineService
	입력: 분봉 bar, 누적 micro-feature 상태, 리스크/포지션 컨텍스트
	출력: 진입/청산 의사결정, 주문요청, DB/대시보드 업데이트
	핵심 함수: run_minute_pipeline()

3. OrderLifecycleService
	입력: direction/qty, account_no, futures_code, broker order API
	출력: ret code, pending order 상태, 체결 반영 결과
	핵심 함수: _send_broker_entry_order(), _send_broker_exit_order()

4. SessionRecoveryService
	입력: session_state.json, trades.db 당일 이력
	출력: 세션카운트, 복원 로그, pnl/학습/추이 패널 초기상태
	핵심 함수: _increment_session(), _restore_daily_state(), _restore_panels_from_history()

##### Day 1 DoD 체크 결과
- [x] connect 흐름 경계 표시
- [x] pipeline 흐름 경계 표시
- [x] order 흐름 경계 표시
- [x] recovery 흐름 경계 표시
- [x] 서비스별 입출력 계약 메모 문서화

#### Day 2: 브로커 런타임 분리 1차
1. 파일: new strategy/runtime/broker_runtime_service.py
	작업: connect_broker 관련 로직 이관(계좌 선택, 코드 결정, realtime/investor timer 시작)
	완료조건: main.py에서 서비스 호출 1라인 진입으로 대체 가능
2. 파일: main.py
	작업: connect_broker 내부를 서비스 위임 구조로 축소
	완료조건: 기능 동등성 유지 + 기존 로그 키워드 유지

##### Day 2 구현 메모 (브로커 런타임 분리 1차)
아래 변경으로 connect_broker 핵심 로직을 서비스로 이관했다.

1. 신규 파일 생성
	- strategy/runtime/broker_runtime_service.py
	- strategy/runtime/__init__.py

2. BrokerRuntimeService 이관 범위
	- login_and_prepare(): 로그인, 계좌선택, 서버라벨 판별, 종목코드 결정, 계약스펙 반영
	- start_realtime_and_investor(): realtime 생성/시작, investor timer 시작, ticker probe

3. main.py 위임 변경
	- TradingSystem.__init__에 broker_runtime_service 주입
	- connect_broker()는 service 호출 + 핵심 안전처리(코드 불일치 강제 FLAT, emergency_exit 동기화) 중심으로 축소

##### Day 2 DoD 체크 결과
- [x] 계좌 선택 로직 서비스 이관
- [x] 종목코드 결정 로직 서비스 이관
- [x] realtime/investor timer 시작 로직 서비스 이관
- [x] main.py connect_broker 서비스 위임 구조 적용
- [x] main.py, broker_runtime_service.py 정적 오류 없음

#### Day 3: 세션 복원 분리
1. 파일: new strategy/runtime/session_recovery_service.py
	작업: 포지션/패널 복원 함수 이관
	완료조건: run() 진입부에서 복원 호출이 서비스 단일 호출로 정리
2. 파일: main.py
	작업: _restore_* 계열을 위임 호출로 축소
	완료조건: main.py 순수 오케스트레이션 가독성 개선

##### Day 3 구현 메모 (세션 복원 분리)
아래 변경으로 세션 복원 책임을 SessionRecoveryService로 분리했다.

1. 신규 파일 생성
	- strategy/runtime/session_recovery_service.py

2. SessionRecoveryService 이관 범위
	- restore_on_startup(): 세션번호 증가 + 당일 거래복원 + 패널 선조회 예약
	- increment_session(): session_state.json 갱신/증가
	- restore_daily_state(): trades.db 기반 거래/PnL 복원
	- restore_panels_from_history(): 학습/효과검증/추이 패널 선조회

3. main.py 위임 변경
	- TradingSystem.__init__에 session_recovery_service 주입
	- run()에서 복원 절차를 단일 호출로 변경
	  (self.session_recovery_service.restore_on_startup(self))
	- _increment_session, _restore_daily_state, _restore_panels_from_history는 호환 래퍼로 축소

##### Day 3 DoD 체크 결과
- [x] session recovery 전용 서비스 파일 분리
- [x] run() 진입부 복원 절차 단일 서비스 호출로 정리
- [x] _restore_* 계열 main.py 위임 구조로 축소
- [x] main.py, session_recovery_service.py 정적 오류 없음

#### Day 4: 예외 정책 3계층 도입
1. 파일: new utils/error_policy.py
	작업: recoverable/degraded/fatal 분류 유틸 및 로깅 정책 구현
	완료조건: 최소 3개 핵심 경로에서 공통 유틸 사용
2. 파일: main.py
	작업: broad except 일부를 분류형 처리로 교체
	완료조건: fatal 발생 시 진입 차단 또는 safe mode 전환
3. 파일: features/feature_builder.py
	작업: 피처 실패를 recoverable로 일관 처리 + 품질 플래그 생성
	완료조건: 피처 실패 시 파이프라인 지속 + 상태 노출

##### Day 4 구현 메모 (예외 정책 3계층 도입)
아래 변경으로 예외 분류를 런타임 동작과 연결했다.

1. 신규 파일 생성
	- utils/error_policy.py
	- 구성: ErrorLevel(recoverable/degraded/fatal), classify_exception(), apply_error_policy()

2. main.py 분류형 처리 적용
	- _on_candle_closed(): run_minute_pipeline 예외를 분류 처리
	  - default=fatal
	  - fatal 시 자동진입 OFF + 15분 쿨다운(safe mode)
	- _fetch_investor_data(): degraded 정책 적용
	- _refresh_pnl_history(): recoverable 정책 적용(이력 갱신/패널 갱신)

3. feature_builder.py 품질 플래그 도입
	- calculator 예외 발생 시 recoverable 카운팅 + degraded 상태 누적
	- 출력 플래그 추가:
	  - feature_recoverable_errors
	  - feature_degraded
	  - feature_quality_score
	  - quality_option_available / quality_macro_available / quality_supply_available

##### Day 4 DoD 체크 결과
- [x] error_policy 유틸 신설
- [x] main.py 핵심 3경로 분류형 처리 적용
- [x] fatal 시 safe mode(자동진입 OFF + 15분 쿨다운) 전환 연결
- [x] feature_builder recoverable 누적 + 품질 플래그 노출
- [x] 관련 파일 정적 오류 없음

#### Day 5: 문서 동기화 1차
1. 파일: README.md
	작업: 실제 실행법(런처 우선), 현재 폴더 구조, 레거시 표기 정리
	완료조건: 존재하지 않는 파일/모듈 참조 제거
2. 파일: CYBOS_PLUS_REFACTOR_PLAN.md
	작업: 완료/미완료 상태 최신화
	완료조건: 장중 실검증 잔여 항목이 체크리스트로 명시

##### Day 5 구현 메모 (문서 동기화 1차)
아래 문서를 실제 코드/구조 기준으로 동기화했다.

1. README.md 정리
	- 직접 python main.py 실행 안내를 런처 우선 방식으로 수정
	- 현재 존재하는 디렉터리/문서 기준으로 구조 설명 축소 정리
	- docs 하위의 비실존 문서 참조 제거, 루트 문서 중심 링크로 정리

2. CYBOS_PLUS_REFACTOR_PLAN.md 최신화
	- 완료 항목에 runtime service 분리(Day2/Day3) 반영
	- 분류형 예외 정책(Day4) 반영
	- investor_data 상태를 placeholder -> 연결 완료/정밀화 필요로 정정
	- 남은 작업을 실검증/고도화 중심으로 재정리

##### Day 5 DoD 체크 결과
- [x] README 실행 절차 현행화(런처 우선)
- [x] 문서 내 비실존 구조/파일 참조 정리
- [x] CYBOS 리팩터링 계획서 완료/미완료 상태 갱신
- [x] 장중 실검증 잔여 항목 체크리스트 유지

### Week 2 (검증 체계 + 실행 품질 강화)

#### Day 6: Capability Matrix 도입
1. 파일: new docs/BROKER_CAPABILITY_MATRIX.md
	작업: kiwoom/cybos/simulation 기능별 지원/검증 상태 표 생성
	완료조건: connect, balance, order, fill, tick, hoga, investor, server-label 상태 포함
2. 파일: main.py
	작업: 시작 시 capability 요약 로그 출력
	완료조건: 런타임 시작 로그만으로 미검증 기능 식별 가능

##### Day 6 구현 메모 (Capability Matrix)
아래 변경으로 브로커 capability를 문서/런타임 양쪽에서 확인 가능하게 만들었다.

1. 문서 산출물 추가
	- docs/BROKER_CAPABILITY_MATRIX.md
	- kiwoom/cybos/simulation 기준으로 support vs verification 분리 표 작성
	- startup 로그의 capability 필드 정의 명시

2. 런타임 로깅 추가
	- main.py
	- TradingSystem._collect_broker_capability_summary() 추가
	- TradingSystem._log_broker_capability_summary() 추가
	- run() 시작 직후 capability 요약 1줄 출력

3. 로그 필드
	- connect, balance, order, fill
	- tick/hoga (event count 포함)
	- investor (fetch_count, runtime_supported)
	- server label

##### Day 6 DoD 체크 결과
- [x] BROKER_CAPABILITY_MATRIX 문서 생성
- [x] connect/balance/order/fill/tick/hoga/investor/server 항목 포함
- [x] main.py 시작 시 capability 요약 로그 출력 연결
- [x] 시작 로그만으로 미검증 항목 식별 가능

#### Day 7: 최소 회귀 테스트 골격 생성
1. 파일: new tests/test_ensemble_decision.py
	작업: 방향/신뢰도/등급 회귀 케이스 작성
	완료조건: 주요 분기 정상 통과
2. 파일: new tests/test_meta_gate.py
	작업: gate block/reduce/pass 케이스 작성
	완료조건: 임계값 회귀 보장
3. 파일: new tests/test_circuit_breaker.py
	작업: 5종 트리거 케이스 최소 세트 작성
	완료조건: 오발동/미발동 기본 케이스 검증

##### Day 7 구현 메모 (최소 회귀 테스트 골격)
아래 테스트 골격을 unittest 기반으로 생성했다.

1. tests/test_ensemble_decision.py
	- up 우세 시 direction=1, grade=A 회귀 케이스
	- 레짐 임계 미달 시 grade=X 회귀 케이스
	- flat 우세 시 direction=0 회귀 케이스

2. tests/test_meta_gate.py
	- flat 신호 시 skip 강제 회귀 케이스
	- 방향성 신호에서 action/핵심 필드 존재 검증 케이스

3. tests/test_circuit_breaker.py
	- 연속 손절 3회 -> HALTED
	- 신호 반전 누적 -> PAUSED
	- API 지연 스파이크 -> PAUSED

##### Day 7 DoD 체크 결과
- [x] tests 디렉터리 생성
- [x] test_ensemble_decision.py 생성
- [x] test_meta_gate.py 생성
- [x] test_circuit_breaker.py 생성
- [x] 테스트 파일 정적 오류 없음

#### Day 8: 데이터 품질 플래그 전파
1. 파일: collection/macro/macro_fetcher.py
	작업: source, age_sec, stale, fallback_used 노출 강화
	완료조건: get_features/get_stats에서 품질 상태 일관 반환
2. 파일: collection/cybos/investor_data.py
	작업: supported/source/reason를 feature와 함께 제공
	완료조건: STEP6에서 수급 품질 판단 가능
3. 파일: features/feature_builder.py
	작업: option/macro/investor 품질 플래그 병합
	완료조건: 단일 feature bundle에서 품질 상태 확인 가능

##### Day 8 구현 메모
- collection/macro/macro_fetcher.py
	- macro_quality_available/stale/age_sec/fallback_used/source_code를 get_features에 포함
	- source 추적(yfinance/naver/dummy) 및 get_stats 품질 필드 확장
- collection/cybos/investor_data.py
	- quality_investor_supported/futures/program/option_supported 추가
	- stale/age_sec/fetch_count/source_code/reason_code를 feature에 수치형으로 노출
- features/macro/macro_feature_transformer.py
	- macro_quality_* 키를 변환 단계에서 passthrough 하도록 반영
- features/feature_builder.py
	- macro/investor/option 품질 플래그를 통합 품질 번들로 병합
	- stale/fallback/unavailable 상황을 feature_quality_score penalty에 반영

##### Day 8 DoD 체크 결과
- [x] macro_fetcher에서 품질 상태 일관 반환
- [x] investor_data에서 supported/source/reason 계열 품질 플래그 노출
- [x] feature_builder에서 option/macro/investor 품질 플래그 병합
- [x] 변환 경로(macro_feature_transformer)에서 품질 키 보존
- [x] 변경 파일 정적 오류 없음

#### Day 9: Execution Governor 1차
1. 파일: new strategy/runtime/execution_governor.py
	작업: tradability score 계산(confidence+quality+latency+toxicity)
	완료조건: pass/reduce/block 의사결정 반환
2. 파일: main.py
	작업: STEP6 진입 직전에 governor 연동
	완료조건: score 저하 시 자동 진입 억제 확인

##### Day 9 구현 메모
- strategy/runtime/execution_governor.py
	- ExecutionGovernor 1차 구현
	- 입력: confidence, quality_score, latency_sec, toxicity_score
	- 출력: action(pass/reduce/block), size_multiplier, tradability_score, reason, components
	- Hard block 규칙: latency_sec >= 5.0 이면 점수와 무관하게 block
- strategy/runtime/__init__.py
	- ExecutionGovernor export 추가
- main.py
	- TradingSystem 초기화 시 self.execution_governor 주입
	- STEP6 직전(horizon calibration 직후) governor 선평가 연동
	- decision["execution_governor"]로 전달 후 STEP7 수량/진입 판단에 반영
	- block: grade=X + qty=0, reduce: qty에 size_multiplier 적용
	- 운영 로그 추가: [ExecutionGovernor] action/score/size_mult/reason

##### Day 9 DoD 체크 결과
- [x] execution_governor.py 신규 생성
- [x] tradability score(confidence+quality+latency+toxicity) 계산 구현
- [x] pass/reduce/block 의사결정 반환
- [x] STEP6 진입 직전에 governor 연동
- [x] score 저하 시 자동 진입 억제/축소 반영
- [x] 변경 파일 정적 오류 없음

#### Day 10: 운영 대시보드 헬스 탭 1차
1. 파일: dashboard/main_dashboard.py
	작업: 시스템 헬스(지연, 갭, 캐시 age, 예외 밀도) 표시 영역 추가
	완료조건: PnL 외 운영건강 지표 실시간 확인 가능
2. 파일: logging_system/log_manager.py
	작업: 헬스 지표 수집 이벤트 추가
	완료조건: 헬스 탭 데이터 소스 일원화

##### Day 10 구현 메모
- logging_system/log_manager.py
	- HEALTH 레이어 추가 (LAYERS 확장)
	- LogEntry에 created_at 타임스탬프 추가
	- 최근 구간 레벨 카운트 집계 API 추가: get_level_counts(since_sec, layer)
	- health(msg, level) 편의 메서드 추가
- dashboard/main_dashboard.py
	- 우측 로그 패널에 "6 운영 헬스" 탭 추가
	- 상단 지표 카드 4종 추가:
		- API 지연(ms)
		- 피처 품질(feature_quality_score)
		- 캐시 나이(sec)
		- 예외 밀도(최근 10분)
	- 헬스 지표 갱신 메서드 추가: update_health_metrics(...)
	- 어댑터 API 추가:
		- update_runtime_health(data)
		- append_health_log(msg, level)
- main.py
	- HEALTH 레이어를 대시보드 헬스 탭으로 subscribe
	- 매분 파이프라인에서 _emit_runtime_health(...) 호출 추가
	- 헬스 스냅샷 구성:
		- latency_ms: LatencySync offset
		- quality_score: feature_quality_score
		- cache_age_sec: max(macro cache age, investor age)
		- exception_density_10m: SYSTEM 레이어 WARNING/ERROR/CRITICAL 집계
	- 상태 레벨(INFO/WARNING/CRITICAL) 산출 후 상태변경/비정상 시 HEALTH 로그 발행
	- update_system_status latency도 실측값으로 반영

##### Day 10 DoD 체크 결과
- [x] 운영 헬스 탭(지연/품질/캐시/예외밀도) UI 추가
- [x] log_manager에 HEALTH 이벤트 소스 추가
- [x] main.py 매분 헬스 스냅샷 생성 및 대시보드 연동
- [x] 비정상 구간 HEALTH 로그 자동 발행
- [x] 변경 파일 정적 오류 없음

#### Day 10-2: 헬스 임계값 Config화 + N분 트렌드 스파크라인
1. 파일: config/settings.py
	작업: 헬스 임계값/트렌드 윈도우/Degraded 정책 상수화
	완료조건: 운영 중 settings 값만 조정해 튜닝 가능
2. 파일: dashboard/main_dashboard.py
	작업: 헬스 탭 최근 N분 미니 스파크라인 표시
	완료조건: 운영 헬스 변화 방향을 한눈에 확인

##### Day 10-2 구현 메모
- config/settings.py
	- HEALTH_LATENCY_WARN_MS / CRIT_MS
	- HEALTH_QUALITY_WARN / CRIT
	- HEALTH_CACHE_AGE_WARN_SEC / CRIT_SEC
	- HEALTH_EXCEPTION_DENSITY_WARN_10M / CRIT_10M
	- HEALTH_TREND_WINDOW_MIN
	- HEALTH_DEGRADED_* 정책 상수
- dashboard/main_dashboard.py
	- 헬스 카드 색상 임계값 하드코딩 제거 -> settings 상수 사용
	- 헬스 탭에 상태 라벨(현재 레벨/모드) 추가
	- 최근 N분 Health Score 스파크라인(유니코드 블록) 추가
	- update_runtime_health에 trend_window_min / health_level / degraded_mode 인자 반영

##### Day 10-2 DoD 체크 결과
- [x] 헬스 임계값 settings.py 상수화
- [x] 헬스 탭 색상/판정에 config 임계값 반영
- [x] 최근 N분 스파크라인 UI 추가
- [x] 변경 파일 정적 오류 없음

#### Day 11: 운영 헬스 기반 자동 Degraded Mode 전환 정책
1. 파일: main.py
	작업: health 레벨 기반 degraded mode enter/exit 자동 전환
	완료조건: 경고 연속 구간에서 자동으로 보수 운용 전환
2. 파일: main.py (STEP7)
	작업: degraded mode 시 진입 신뢰도/수량 정책 적용
	완료조건: 자동 진입 품질 저하 국면에서 노출 축소

##### Day 11 구현 메모
- main.py
	- _classify_health_level(): config 임계값 기반 INFO/WARNING/CRITICAL 판정
	- _update_degraded_mode():
		- WARNING/CRITICAL 연속 N분 -> 자동 진입
		- INFO 연속 M분 -> 자동 해제
	- _emit_runtime_health()에서 health level 계산 + degraded 모드 상태 갱신
- STEP7 진입정책 연결
	- degraded mode ON:
		- confidence < HEALTH_DEGRADED_MIN_CONF -> 진입 차단(X)
		- 그 외 수량에 HEALTH_DEGRADED_SIZE_MULT 적용
	- 차단 사유 로그/패널 이유 문구에 degraded 조건 반영

##### Day 11 DoD 체크 결과
- [x] 헬스 레벨 기반 degraded enter/exit 자동 전환 구현
- [x] degraded mode 진입 신뢰도 하한 정책 적용
- [x] degraded mode 수량 축소 정책 적용
- [x] HEALTH 로그/시스템 로그로 상태 전환 추적 가능
- [x] 변경 파일 정적 오류 없음

## 8) 작업 백로그 (우선순위별 파일 목록)

### A급 (이번 2주 필수)
- main.py
- dashboard/main_dashboard.py
- features/feature_builder.py
- collection/macro/macro_fetcher.py
- collection/cybos/investor_data.py
- README.md
- CYBOS_PLUS_REFACTOR_PLAN.md

### B급 (같이 진행 권장)
- strategy/runtime/broker_runtime_service.py (신규)
- strategy/runtime/session_recovery_service.py (신규)
- strategy/runtime/execution_governor.py (신규)
- utils/error_policy.py (신규)
- docs/BROKER_CAPABILITY_MATRIX.md (신규)
- tests/test_ensemble_decision.py (신규)
- tests/test_meta_gate.py (신규)
- tests/test_circuit_breaker.py (신규)

## 9) 일일 완료 체크리스트 (복붙용)

- [ ] 오늘 변경 파일 목록 기록
- [ ] 절대원칙 위반 여부 확인(15:10 청산/CORE 3피처/COM 콜백 안전)
- [ ] broad except 신규 추가 여부 점검
- [ ] start_mireuk_cybos_test.bat 기준 기본 부팅 검증
- [ ] 주요 로그 키워드 정상 출력 확인
- [ ] dev_memory/audit 문서에 당일 결과 5줄 요약 기록

## 10) Day10-2 + Day11 반영본 하루 운용 검증 체크리스트

### 10.1 운용 전(시작 전 5분)
- [ ] settings.py 현재값 스냅샷 저장(핫리로드 옵션, degraded 정책 옵션 포함)
- [ ] HEALTH_POLICY_HOT_RELOAD_ENABLED=True 확인
- [ ] HEALTH_DEGRADED_BLOCK_AUTO_ENTRY / HEALTH_DEGRADED_BLOCK_MANUAL_ENTRY 초기값 기록
- [ ] 대시보드 6 운영 헬스 탭 진입 가능 확인

#### 10.1-A 2026-05-15 사전점검 결과 (07:38 KST)

근거 로그 요약:
- 07:38:01 DB 초기화 완료
- 07:38:06 startup sync begin(account=333042073, code=0565)
- 07:38:36 startup sync 결과 verified=False, block_new_entries=True
- 07:38:36 Capability: broker=cybos, balance/order/fill/tick/hoga/investor 일부 미검증
- 07:38:36 Qt 이벤트 루프 진입

설정 스냅샷(검증 시작 시점):
- HEALTH_POLICY_HOT_RELOAD_ENABLED=True
- HEALTH_POLICY_HOT_RELOAD_INTERVAL_SEC=5
- HEALTH_DEGRADED_BLOCK_AUTO_ENTRY=True
- HEALTH_DEGRADED_BLOCK_MANUAL_ENTRY=False
- HEALTH_DEGRADED_MIN_CONF=0.62

사전점검 체크:
- [x] settings.py 현재값 스냅샷 저장(본 섹션 기록으로 대체)
- [x] HEALTH_POLICY_HOT_RELOAD_ENABLED=True 확인
- [x] HEALTH_DEGRADED_BLOCK_AUTO_ENTRY / HEALTH_DEGRADED_BLOCK_MANUAL_ENTRY 초기값 기록
- [ ] 대시보드 6 운영 헬스 탭 진입 가능 확인 (수동 UI 확인 필요)

운영 전 주의사항:
- startup sync가 verified=False 상태라 자동진입은 block_new_entries=True 조건으로 차단 중.
- 장중 검증(10.2~10.5)은 브로커 sync 정상화 이후에만 유효하게 판정.

### 10.2 장중 관찰(30~60분)
- [ ] HEALTH 로그에 헬스 상태 메시지 주기적으로 출력 확인
- [ ] 헬스 탭 상태 라벨(상태/Mode) 업데이트 확인
- [ ] 스파크라인 3종(Health Score/지연/품질) 실시간 갱신 확인
- [ ] WARNING 또는 CRITICAL 구간에서 Degraded Mode 자동 진입 확인
- [ ] INFO 연속 구간에서 Degraded Mode 자동 해제 확인

### 10.3 핫리로드 즉시 반영 검증(재시작 금지)
- [ ] 운용 중 settings.py에서 HEALTH_DEGRADED_BLOCK_MANUAL_ENTRY 값을 토글
- [ ] 5~10초 내 SYSTEM 로그에 "[HealthPolicy] settings.py 핫리로드 반영" 출력 확인
- [ ] 반영 로그에 block_auto/block_manual 값이 수정값과 일치하는지 확인
- [ ] 앱 재시작 없이 정책 반영 유지 확인

### 10.4 자동/수동 진입 정책 검증(Degraded Mode 기준)
- [ ] 자동진입: confidence < HEALTH_DEGRADED_MIN_CONF 에서 차단 로그 확인
- [ ] 자동진입: confidence >= HEALTH_DEGRADED_MIN_CONF 에서 수량 축소 적용 확인
- [ ] 수동진입: block_manual=False 일 때 동일 confidence에서 진입 허용 확인
- [ ] 수동진입: block_manual=True 로 변경 후 동일 confidence에서 차단 확인

### 10.5 로그 키워드 검증
- [ ] [HealthPolicy] settings.py 핫리로드 반영
- [ ] [HealthPolicy] 자동 Degraded Mode 진입
- [ ] [HealthPolicy] 자동 Degraded Mode 해제
- [ ] [차단] 자동진입 Degraded 정책 차단
- [ ] [차단] 수동진입 Degraded 정책 차단 (block_manual=True 시)

### 10.6 종료 판정(하루 운용 완료)
- [ ] 위 10.2~10.5 항목 중 필수 8개 이상 충족
- [ ] 치명 오류(주문/포지션 동기화 실패) 0건
- [ ] "핫리로드 반영" 로그 최소 1회 + 자동/수동 차단 동작 각 1회 이상 확인
- [ ] 최종 결과를 5줄 요약으로 본 문서 말미 또는 당일 세션 로그에 기록

---

## 2026-05-15 ���� ���� �߰� �޸�

�α� ���:
- 09:11:13 startup sync begin(account=333042073, code=0565)
- 09:11:43 `CpTrade.CpTd0723` 30�� timeout -> `verified=False`, `block_new_entries=True`
- 09:15:38 `Dscbo1.FutureMst` 30�� timeout -> snapshot �� ���� 0���� ����
- 09:16:08 `FutureCurOnly` tick subscribe �Ϸ�
- 09:16:08 `FutureJpBid` hoga subscribe �Ϸ�
- 09:16:08 investor futures TR(`CpSysDib.CpSvrNew7212`) ���� ����
- 09:16:09 Capability: `investor=Y/Y(fetch=1,runtime=Y)` ������ `tick=Y/N(0)`, `hoga=Y/N(0)`
- 09:16:13 ���� ��� �α� �� ���μ��� ���� �ڵ� `-1073741819 (0xC0000005)`

Ȯ�ε� ������:
- ���� �ڵ� ���� �� 09:00�� �ǽð� ������ ������ �� �ִ� ������ �־���
- ���� ���� ���� �ÿ��� `CpTd0723`, `FutureMst` BlockRequest�� ���� 30�� timeout
- timeout ���Ŀ��� �ǽð� ���� ��ü�� �Ϸ�ǹǷ�, �� ���� ������ "���� ���� ��"�� �ƴ϶� "���� �� ù COM �̺�Ʈ �Ǵ� ���� UI ���� ���"�� ��ҵ�
- ���� �ڵ�� Python ���ܰ� �ƴ� access violation(`0xC0000005`)�̹Ƿ� COM/Qt ��� �Ǵ� UI ��ü ���� ������ ����

�ݿ��� ���� ����:
- `strategy/runtime/broker_runtime_service.py`
  - ���� �⵿ �� �� ���� ������ `ensure_market_open_runtime_started()`�� �ǽð� ����/������ Ÿ�̸� �ڵ� ���� ����
  - ���� scheduler tick������ �̽��� ���¸� ��Ȯ���Ͽ� �ڵ� ����
- `collection/cybos/realtime_data.py`
  - `start()` �ܰ躰 ���� �α� �߰�
  - `snapshot begin/end`, `tick subscribe begin/end`, `hoga subscribe begin/end`
  - `SubscribeLatest()` ��� `Subscribe()` ������� ���� ���� ������ �켱
  - COM �̺�Ʈ �б� ���� �α�(`[CybosRT-EVENT]`) �߰�
- `collection/cybos/api_connector.py`
  - `create_subscription()` ���ο� `Dispatch`, `SetInputValue`, `WithEvents`, `subscribe` ���� �α� �߰�
  - COM callback `OnReceived()` ����/���� �α�(`[CybosEvent] recv begin/end`) �߰�
- `main.py`
  - ù ƽ UI �ݿ� ��ο� `[TickUI] begin -> minute_chart_tick -> update_price -> end` �α� �߰�

�ؼ�:
- 2026-05-15 09:16 이후 로그 분석, "데이터 수신 분리 후 상태가" 라는 관점에서 1분 이상으로 더 이상 이슈이지 아닌지
- 이슈 1단계 결과로는 `CpTd0723`/`FutureMst` timeout, 2단계 결과로는 실시간 구독 후 첫 이벤트 처리 시점의 access violation 가능성
- 다음 부팅 시점에서는 `[CybosSub]`, `[CybosEvent]`, `[CybosRT-EVENT]`, `[TickUI]` 등 순서대로 정상 흐름인지 확인과 crash 원인은 추가 Confirm 필요

---

## 2026-05-15 09:18 장중 점검 — 문제점 확인 및 개선 구현

### 장중 점검 로그 개요 (09:18:52 기동)

```
09:18:55  [BrokerSync] startup sync begin account=333042073 code=0565
          CpTrade.CpTd0723 BlockRequest 시작 → 30초 대기
09:19:25  TIMEOUT 30s progid=CpTrade.CpTd0723
          [BrokerSync] status verified=False, block_new_entries=True
          ← 자동매매 영구 차단 상태로 고착
09:19:25  Dscbo1.FutureMst snapshot begin code=A0565 → 30초 대기
09:19:55  TIMEOUT 30s progid=Dscbo1.FutureMst
          snapshot end price=0.00 oi=0 bid1=0.00 ask1=0.00
09:19:56  FutureCurOnly / FutureJpBid 구독 성공
          [Capability] tick=Y/N(0), hoga=Y/N(0) ← 이벤트 0건
09:20:56  투자자 데이터 동일값 반복 (틱 유입 없음)
```

---

### 확인된 문제점 (2건, 모두 치명적)

#### BUG-1: `_run_block_request` COM STA 데드락 (항상 30초 타임아웃)

| 항목 | 내용 |
|---|---|
| 영향 범위 | `CpTrade.CpTd0723` (잔고 TR), `Dscbo1.FutureMst` (스냅샷) |
| 결과 | 기동마다 60초 추가 지연 + `block_new_entries=True` 고착 → 자동매매 불가 |
| 근거 | `_probe_investor_tr()`는 메인 스레드 직접 호출 → 정상 동작. `_run_block_request()`는 백그라운드 스레드 → 항상 타임아웃 |

**근본 원인**:  
`_run_block_request()`는 백그라운드 스레드에서 `BlockRequest()`를 실행하면서
메인 스레드는 `done.wait(30)` 으로 완전 차단한다.  
Cybos Plus의 `BlockRequest`는 호출 스레드의 **Windows 메시지 큐로 응답**을 전달하는데,  
백그라운드 스레드에는 메시지 펌프가 없어 응답이 영구 대기 → 30초 후 TimeoutError.  
메인 스레드도 `done.wait()`으로 막혀 있어 `pythoncom.PumpWaitingMessages()`가 호출되지 않는다.

#### BUG-2: 만기된 선물 코드 구독 (틱 데이터 미수신)

| 항목 | 내용 |
|---|---|
| 영향 범위 | 미니선물 코드 선택 전체 (롤오버 미처리) |
| 결과 | A0565(5월물, 2026-05-14 만기) 구독 → Cybos가 만기 코드에 tick 미전송 → 분봉 파이프라인 미동작 |
| 근거 | `[DBG CK-3] 금월물코드=A0565 is_mini=True` — UI 저장값 A0565 그대로 사용 |

**근본 원인**:  
`_resolve_trade_code()`에서 UI에 A0565가 저장되어 있으면  
`get_nearest_mini_futures_code()` 자체를 호출하지 않는다.  
2026-05-14 만기 이후에도 UI 저장값이 그대로 사용되어  
만기 코드(A0565)로 구독 → 실시간 데이터 0건.

---

### 구현된 개선 사항 (3파일, 4건)

#### FIX-1: `_run_block_request` 메시지 펌핑 루프 도입
**파일**: `collection/cybos/api_connector.py`

```python
# Before: 메인 스레드 완전 차단
if not done.wait(timeout_sec):
    raise TimeoutError(...)

# After: 10ms 간격 COM 메시지 처리하며 대기
deadline = time.time() + timeout_sec
while True:
    if done.wait(timeout=0.01):
        break
    if time.time() >= deadline:
        raise TimeoutError(...)
    if pythoncom is not None:
        try:
            pythoncom.PumpWaitingMessages()
        except Exception:
            pass
```

- 백그라운드 스레드의 `BlockRequest`가 메인 스레드 메시지 큐로 응답을 보낼 수 있게 됨
- 기대 완료 시간: 30초 타임아웃 → **1~3초 내 정상 완료**

#### FIX-2: `get_nearest_mini_futures_code()` `_run_block_request` 전환
**파일**: `collection/cybos/api_connector.py`

- 기존: 메인 스레드에서 직접 `BlockRequest()` 호출, 만기 코드 skip 로직 없음
- 변경: `_run_block_request` 사용, 각 후보 코드에서 `price > 0` 조건으로 만기 코드 자동 skip
- A0565 → price=0(만기) → skip, A0566 → price>0 → **근월물로 확정 반환**

#### FIX-3: `_resolve_trade_code()` 항상 근월물 프로브
**파일**: `strategy/runtime/broker_runtime_service.py`

```python
# Before: UI 값이 있으면 get_nearest_mini_futures_code() 미호출
if is_mini_selected:
    if not ui_code:
        ui_code = system.broker.get_nearest_mini_futures_code()
    code = ui_code

# After: 미니선물 선택 시 항상 프로브, 롤오버 시 경고 로그
if is_mini_selected:
    probed = system.broker.get_nearest_mini_futures_code()
    if probed:
        if probed != ui_code:
            logger.warning("[CodeRoll] 미니선물 코드 교체: UI=%s → 근월물=%s", ui_code, probed)
        code = probed
    else:
        logger.warning("[CodeRoll] 미니선물 프로브 실패 — UI 코드 사용: %s", ui_code)
        code = ui_code
```

#### FIX-4: `_scheduler_tick()` broker sync 장중 재시도
**파일**: `main.py`

- startup balance TR 실패로 `block_new_entries=True`가 된 경우
- 30초 tick마다 체크, **3분 간격으로** `_ts_sync_position_from_broker()` 재시도
- FIX-1로 BlockRequest가 정상화되면 재시도 성공 → `block_new_entries=False` → 자동매매 활성화

---

### 개선 후 기대 기동 로그

```
[MiniProbe] skip code=A0565 ret=0 status=0 price=0.0   ← 만기 자동 skip
[MiniProbe] 근월물 확정 code=A0566 price=XXX.XX         ← 6월물 확정
[CodeRoll] 미니선물 코드 교체: UI=A0565 → 근월물=A0566  ← 롤오버 알림
[DBG CK-3] 금월물코드=A0566 ...
[BrokerSync] startup sync 완료: FLAT -> FLAT            ← 타임아웃 없음
[BrokerSync] status verified=True block_new_entries=False
[CybosRT-START] snapshot end code=A0566 price=XXX.XX   ← 가격 정상 수신
[Capability] tick=Y/N(0) hoga=Y/N(0)                   ← 구독 직후
[CybosRT-TICK] #1 code=A0566 ...                        ← 분봉 파이프라인 시작
```

---

### 2026-05-15 장중 점검 DoD 체크

- [x] `_run_block_request` COM 메시지 펌핑 루프 적용 (api_connector.py)
- [x] `get_nearest_mini_futures_code()` `_run_block_request` 기반 재작성 (만기 코드 자동 skip)
- [x] `_resolve_trade_code()` 미니선물 항상 프로브, 롤오버 경고 로그 추가
- [x] `_scheduler_tick()` broker sync 미검증 시 3분 간격 장중 재시도
- [ ] 다음 기동 시 `[MiniProbe] 근월물 확정 code=A0566` 로그 확인
- [ ] `[BrokerSync] status verified=True block_new_entries=False` 확인
- [ ] `[CybosRT-TICK] #1 code=A0566` 분봉 데이터 수신 확인
- [ ] 10.2~10.5 장중 점검 항목 재검증 (FIX 적용 후 재기동)
