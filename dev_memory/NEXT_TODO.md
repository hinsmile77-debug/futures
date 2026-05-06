# 다음 할 일 목록 — futures (미륵이)

> 검증 필요 항목, 예정된 작업, 알려진 잠재 이슈.

### 완료 처리 규칙
- 완료 시 `[DONE YYYY-MM-DD]` 태그 추가
- DONE 태그 후 1주일 경과 시 삭제

---

## 즉시 확인 필요 (추가됨 2026-05-06 추가 세션)

### [V32] SendOrderFO 실제 체결 확인 [다음 장중]
- **내용**: `SendOrderFO` 전환 후 모의투자 계좌에 실제 주문이 접수되는지
- **방법**: SYSTEM.log `[OrderDiag] SendOrderFO request ...` + `SendOrderFO 접수 rq=진입 ...` 확인. HTS 모의계좌 체결 내역 확인
- **기준**: `KOA_NORMAL_FUT_ORD` TR 이름으로 콜백 수신 (기존 `KOA_NORMAL_SELL_KP_ORD` 아님). [RC4109] 오류 미발생
- **실패 시**: hoga_gb="3" → "1"(지정가+price 입력) 시도 또는 code 형식 변경

### [V33] Fix B 낙관적 오픈 진단 확인 [다음 장중]
- **내용**: 진입 후 `[FixB] 낙관적 오픈 완료 direction=... status=SHORT ...` 로그 확인
- **방법**: SYSTEM.log에서 `[FixB]` 태그 검색
- **기준**: status=SHORT/LONG, optimistic=True → 이중진입 방지 동작 확인
- **실패 시**: `[FixB] open_position 실패 ... err=<원인>` 로그에서 실패 원인 파악

### [V34] 프로그램매매 FID 확정 [다음 장중]
- **내용**: `P00101` 타입='프로그램매매' FID 202/204/210/212/928/929 의미 확인
- **방법**: PROBE.log `[PROBE-ALLRT-FIDS] type='프로그램매매'` 재확인. FID 928/929는 프로그램 매수/매도 누적 순매수금액 추정
- **활용**: FID 확정 시 `_on_receive_real_data()`에 프로그램매매 실시간 파싱 경로 추가 가능

---

## 즉시 확인 필요 (추가됨 2026-05-06)

### [V30] OPW20006 BrokerSync 정상 동작 확인 [다음 장중]
- **내용**: `_sync_position_from_broker()` 호출 시 `선옵잔고상세현황` 레코드에서 잔고 행이 실제로 파싱되는지
- **방법**: SYSTEM.log `[BrokerSync] OPW20006 rows=N` 확인. N > 0이면 레코드명 수정 성공
- **기준**: 포지션 보유 중 rows=포지션 수량, FLAT 상태 rows=0
- **실패 시**: `_MULTI_RECORD` / `_SINGLE_RECORD` 이름을 enc 파일 재조회해 재확인

### [V31] Fix B 이중진입 방지 확인 [다음 장중]
- **내용**: 진입 주문 후 `position.status == 'LONG'`(또는 SHORT)이 즉시 설정되는지, 같은 방향 재진입이 차단되는지
- **방법**: SYSTEM.log `[Position] 낙관적 오픈 LONG N계약 @ XXXX` 로그 확인. 이후 같은 방향 체크리스트 진입 조건이 "포지션 보유 중" 차단되는지 확인
- **기준**: `SendOrder ret=0` 직후 `position.status != 'FLAT'` → 다음 분봉에서 체크리스트 진입 차단
- **Chejan 있을 경우**: `apply_entry_fill()` 로그 `체결보정 LONG N계약 @ XXXX | 평균=XXXX 보유=N계약` 확인 (수량 불변)

---

## 즉시 확인 필요 (추가됨 2026-05-04 야간 2세션)

### [V26] Kiwoom SendOrder 실제 체결 확인 [SUPERSEDED → V32]
- SendOrder가 SendOrderFO로 교체됨 (2026-05-06). V32로 대체됨.

### [V27] TP1/TP2 부분 청산 API 동작 확인 [다음 장중 포지션 보유 후]
- **내용**: TP1 도달 시 `_execute_partial_exit(price, stage=1)` 호출 → 33% 청산 주문 전송
- **방법**: TRADE 로그 `[Position] 부분청산 N계약 @ XXXX | 잔여=M계약` 확인
- **기준**: `partial_1_done=True` + Kiwoom 체결 내역 + trades.db PARTIAL 레코드

### [V28] 주문/체결 탭 실데이터 메트릭 표시 확인 [다음 실행]
- **내용**: 상단 `당일 거래` / `평균 지연` / `최대 지연` / `수신 횟수` 가 실데이터로 갱신되는지
- **방법**: 대시보드 실행 → 주문/체결 탭 → 분봉 처리 후 수치 변화 확인
- **기준**: "——" 대신 숫자 표시 (지연 ms 단위, 수신 횟수 증가)

### [V29] 로그 좌측 정렬 시각 확인 [다음 실행]
- **내용**: 주문/체결·손익·모델AI 탭 로그가 좌측 정렬로 출력되는지
- **방법**: 대시보드 실행 후 각 탭에서 로그 텍스트 정렬 확인
- **기준**: 구분선만 중앙 정렬, 나머지 모든 로그 좌측 정렬

---

## 즉시 확인 필요 (추가됨 2026-05-04 야간)

### [V22] opt50008 행 구조 확인 — 투자자별 vs 시간별 [다음 장중]
- **배경**: KOA Studio에서 opt50008 = 프로그램매매추이차트요청 확인. 출력: 체결시간·투자자별순매수금액
- **미확인**: 행이 투자자 유형별(개인/외인/기관...)인지 vs 시간대별인지 구조 불명
- **방법**: 다음 장중 DATA.log에서 `[TR-DISCOVER] opt50008 첫수신 rows=N fields=[...]` 확인
  - rows=10이면 투자자별(INVESTOR_KEYS 순서) 가능성 높음
  - rows=수십~수백이면 시간별 시계열로 판단 → 파싱 로직 수정 필요
- **기준**: `program_foreign_net_krw` 피처가 0이 아닌 값으로 채워지면 파싱 성공

### [V25] fetch_program_investor() 정상 동작 확인 [다음 장중]
- **내용**: opt50008 호출 성공 + `_program_investor` 캐시에 값이 채워지는지
- **방법**: DATA.log `[Investor] 프로그램투자자별 rows=N | 외인=±X 개인=±Y (KRW)` 확인
- **기준**: rows > 0 AND 외인/개인 값 중 하나라도 0이 아님
- **실패 시**: screen_no 충돌 가능성 — 2013 → 다른 번호로 변경

### [V23] 프로그램매매 실시간 FID 캡처 [다음 장중]
- **내용**: code=`P00101` type=`프로그램매매` FID 스캔 — 차익/비차익 순매수 FID 번호 확인
- **방법**: 장중 PROBE.log `[PROBE-ALLRT-FIDS] type='프로그램매매'` 항목 확인
- **활용**: FID 확정되면 opt10060 TR 폴링 → 실시간 수신으로 교체 가능

### [V24] 투자자ticker 실서버 지원 확인 [실서버 전환 후]
- **내용**: 실서버 전환 후 `투자자ticker` 실시간 타입 동작 여부 확인
- **방법**: 실서버 연결 후 PROBE.log `[PROBE-ALLRT] type='투자자ticker'` 수신 확인
- **배경**: 모의투자 서버 — 8가지 코드 조합 전부 ret=0이나 데이터 없음. 실서버 전용 추정

---

## 즉시 확인 필요

### [V1] OPT50029 초기 분봉 로드 확인 [SUPERSEDED 2026-05-04]
- 모의투자 서버에서 OPT50029 rows=0 확인됨 — SetRealReg(A0166000) 전환으로 대체
- 실 서버 전환 시 OPT50029 초기 히스토리 로드 재확인 필요

### [V20] SGD 지속 학습 확인
- **내용**: 매분 LEARNING 로그에 `[SGD] N건 학습 | SGD비중=30% 50분정확도=xx%` 출력되는지
- **방법**: 5층 로그 > 학습 탭. 초기 학습 완료 이후 매분 갱신 확인
- **기준**: 50분정확도 값이 분 단위로 변화 (현재 1/3 확률 학습 시작 → 실데이터 누적 후 개선 기대)

### [V21] SGD 10m·30m 호라이즌 학습 확인
- **내용**: 10m·30m가 현재 미학습 — 해당 ts DB 레코드 없어서 건너뜀
- **방법**: 장 진행 1시간 후 LEARNING 로그에 `[OnlineLearner] 10m 초기 학습 완료` 출력 확인
- **기준**: 13:44 + 10분 = 13:54 분봉 처리 시 자동으로 학습됨

### [V19] OFI bid/ask 정상 수신 확인
- **내용**: `[DBG-F4]` 로그에서 `bid=XXX.XX ask=XXX.XX` 가 0이 아닌 값으로 표시되는지
- **방법**: 재시작 후 첫 분봉 확정 후 DEBUG 로그 확인
- **기준**: bid > 0 AND ask > 0 → `ofi.update_hoga()` 정상 호출됨
- **파일**: `collection/kiwoom/realtime_data.py` `_on_hoga_data()`

### [V18] 파이프라인 watchdog 정상 해제 확인 [DONE 2026-05-04]
- watchdog 임계값 90/150/240s 적용 + log_loss 크래시 해결로 파이프라인 정상 완료
- "1분 30초 미실행" 경보는 크래시 구간(13:36~13:41)에서만 발생 → 정상

### [V2] run_minute_pipeline 완전 검증 [DONE 2026-04-27]
- `on_candle_closed` 호출 확인됨, 파이프라인 진입 확인됨

### [V3] run_minute_pipeline 예측값 출력까지 완전 검증 [DONE 2026-04-28]
- tick→분봉→on_candle_closed→pipeline→LONG 1계약 @ 1008.2 확인
- [Ensemble] dir=+1 conf=76.8% grade=A / [Checklist] 6/9 통과 자동진입 확인
- 더미 모델 기반 — 예측값은 무의미, 파이프라인 연결만 확인

### [V4] STEP 8 청산 트리거 + trades.db 저장 확인 [DONE 2026-04-28]
- trades.db 2건: 12:44 -0.10pt 하드스톱, 12:46 -0.70pt 하드스톱 확인
- `[Position] 청산 LONG @ 1009.45 | PnL=-0.10pt` 로그 확인

### [V5] STEP 9 predictions.db 저장 확인 [DONE 2026-04-28]
- predictions.db 30행 확인 (12:29·12:30 각 6 호라이즌)

---

---

## 즉시 확인 필요 (추가됨 2026-04-29)

### [V9] 다이버전스 패널 외인 데이터 표시 확인
- **내용**: 재시작 후 "외인 콜순매수", "외인 풋순매수", "다이버전스" 카드가 실제 값 표시하는지
- **방법**: 파이프라인 실행 후 `[Investor]` 로그 + 대시보드 다이버전스 탭 확인
- **기준**: "——" 대신 숫자 표시 (시뮬: 랜덤, 실거래: TR 실데이터)

### [V10] 진입 관리 탭 체크리스트 표시 확인
- **내용**: 체크리스트 아이콘이 V/X/— 3가지 상태 올바르게 표시되는지
- **조건 1**: 장 중 FLAT 상태 → V/X 표시 (체크리스트 평가됨)
- **조건 2**: 포지션 보유 중 또는 EXIT_ONLY 구간 → — 표시 (평가 안 됨)
- **V10a**: "산출 수량" N계약 표시 확인 (기존: "——" 고정)
- **V10b**: "당일 진입 통계" 매분 갱신 확인 (진입 0회→N회 업데이트)

---

## 즉시 확인 필요 (추가됨 2026-04-28)

### [V6] ATR 플로어 적용 후 진입 품질 확인 [DONE 2026-04-28]
- stop_dist=0.75pt 로그에서 정확히 확인됨
- `[DBG-F4]` ATR floor + `[DBG-STOP]` 하드스톱 발동 경로 모두 검증

### [V7] 포지션 복원 로그 확인
- **내용**: LONG 중 재시작 → `[Position] 이전 포지션 복원: LONG 1계약 @ XXXX` 로그
- **기준**: 재시작 후 FLAT 상태가 아닌 기존 포지션 유지

### [V8] CVD tick test 효과 검증
- **내용**: buyvol/sllvol이 실제로 분리되는지 확인 (이전엔 항상 buyvol=100%)
- **방법**: `[DBG-F4]` 로그에서 `buyvol`/`sllvol` 값이 다양하게 분포하는지 확인
- **기준**: 상승 틱에서 buy_vol > 0, 하락 틱에서 sell_vol > 0으로 분리됨

---

## 즉시 확인 필요 (추가됨 2026-04-30 자가학습 연결 세션)

### [V11] SGD 학습 로그 확인 [DONE 2026-05-04]
- 13:44 재시작 2분 후 1m/3m/5m/15m 초기 학습 완료 확인
- 이전 세션 DB 레코드 활용 (features 예측 당시 저장 → 올바른 supervised learning)

### [V12] GBM 일일 마감 재학습 확인 (15:40)
- **내용**: `daily_close()` 호출 시 `[GBM] 일일 마감 재학습 완료` 또는 `건너뜀` 로그
- **방법**: 15:40 이후 학습 탭 로그 확인
- **기준**: raw_candles 5000행 미만이면 "건너뜀", 이후엔 재학습 완료

### [V13] features 전체 저장 확인
- **내용**: predictions.db의 features 컬럼이 이제 20개 이상 피처를 저장하는지 확인
- **방법**: `SELECT length(features) FROM predictions LIMIT 5` — 기존 20개(~400자) → 전체(~1000자 이상)

### [V14] 🎯 효과 검증기 패널 표시 확인
- **내용**: "🎯 효과 검증" 탭이 정상 렌더링되는지 확인
- **방법**: 대시보드 실행 → 중앙 탭 6번째 "🎯 효과 검증" 클릭
- **조건 1**: 체결 완료 거래 0건 시 → "데이터 수집 중 (0건 체결)" 배너 표시
- **조건 2**: 체결 완료 거래 10건 이상 시 → 캘리브레이션·등급별·레짐별 테이블 수치 표시
- **조건 3**: 5분 주기 갱신 (패널이 빈 "——" 상태에서 수치로 전환되는지)

---

## 즉시 확인 필요 (추가됨 2026-04-30 이번 세션)

### [V15] 자동 종료 슬랙 알림 + 프로그램 종료 확인
- **내용**: 15:40 `daily_close()` 완료 후 슬랙 알림 수신 + 15초 후 프로그램 실제 종료
- **방법**: 테스트용 시간 임시 변경 (`datetime.time(15, 40)` → 현재 시간) 또는 실제 15:40 대기
- **기준**: 슬랙 알림 2건(일일 요약 + 종료 안내) + 15초 후 대시보드 창 닫힘

### [V16] 성장 추이 탭 렌더링 확인
- **내용**: "📈 성장 추이" 탭 7번째 탭이 정상 표시되는지
- **방법**: 대시보드 실행 → 중앙 탭 7번째 "📈 성장 추이" 클릭
- **조건 1**: 체결 데이터 0건 시 → "데이터 없음" 표시
- **조건 2**: 체결 데이터 있으면 일별/주별/월별/연간 탭에 집계 행 표시
- **조건 3**: 시작 500ms 후 선조회 동작 확인 (콘솔 오류 없이)

### [V17] daily_stats 스냅샷 저장 확인
- **내용**: 15:40 일일 마감 후 `trades.db`의 `daily_stats` 테이블에 당일 행 삽입 확인
- **방법**: `SELECT * FROM daily_stats ORDER BY date DESC LIMIT 5`
- **기준**: 오늘 날짜의 행이 trades·wins·pnl_krw·sgd_accuracy 포함하여 저장

---

## 예정된 작업

### [T1] 모의투자 4주 운영
- **전제**: [V1], [V2] 확인 완료 후
- **기준** (4주 완료 시 실전 전환 가능):
  - 통산 수익률 양수
  - Circuit Breaker 1회 이상 정상 작동
  - 일일 수익률 변동성 안정적

### [T2] Circuit Breaker 5종 트리거 테스트
- 각 트리거를 의도적으로 발동시켜 정지·청산 동작 확인
- `safety/circuit_breaker.py` + `safety/emergency_exit.py`
- **주의**: 중복발동 버그 수정됨 (2026-04-30) — 이제 PAUSED/HALTED 상태에서 재발동 없음
- **확인 포인트**: 발동 1회만 슬랙 전송되는지 + 대시보드 SYSTEM탭/경보탭에 표시되는지

### [T3] Walk-Forward 검증 (26주 데이터 필요)
- **기준**: Sharpe ≥ 1.5, MDD ≤ 15%, 승률 ≥ 53%
- `backtest/walk_forward.py` — 8주 학습 / 1주 검증 반복
- 실거래 데이터 26주 확보 후 실행

### [T4] ResearchBot → main.py 연결 (장외 자동 리서치)
- `research_bot/alpha_scheduler.py` — 16:00 자동 실행 스케줄러
- main.py에 연결하여 장외 자동 활성화
- **주의**: 자동 통합은 절대 금지 — 팝업 알림 + 사용자 검토 후 수동 통합

### [T5] PPO 정책 검증 — Sharpe +0.4 목표
- 실거래 데이터 확보 후 `learning/rl/policy_evaluator.py`로 평가
- 정적 규칙 대비 Sharpe +0.4 이상 확인 후 실전 적용

---

## 알려진 잠재 이슈

### [P0] [DBG] 출력문 정리 예정
- `api_connector.py`, `realtime_data.py`, `main.py`에 디버그 print 잔존
- 파이프라인 안정 확인 후 일괄 제거 (시스템 안정 전 제거 금지)

### [P1] GetMasterCodeList("10") — 모의투자 서버 빈값
- 모의투자 서버에서 None/빈값 반환 가능 (실 서버에서는 정상)
- `GetFutureCodeByIndex(0)` 추가로 우선순위 보완됨 — 해결됨

### [P2] py37_32 패키지 호환성
- scipy 1.5.4 고정 필수 (1.7.x DLL 충돌)
- torch 설치 시 32-bit 호환 버전 확인 필요 (PPO GPU 가속 미사용 시 numpy fallback)

### [P3] 뉴스 감성 분석 — HF API 연결 실패 시 fallback
- `features/sentiment/kobert_sentiment.py`: HF API 오프라인 시 키워드 사전 fallback
- 실전 환경에서 fallback 동작 확인 필요

### [P4] 알파 풀 JSON 파일 증가
- `research_bot/alpha_pool.py`: MAX_ACTIVE=50 제한 있으나 퇴역 알파 파일 관리 정책 미확정

### [P6] FID_BID_PRICE=41 / FID_ASK_PRICE=51 명칭 역전 의심
- KOA 개발가이드에서 FID 41=매도1호가, 51=매수1호가 가능성 시사
- 현재 constants.py는 41=BID(매수), 51=ASK(매도)로 정의됨
- ofi.py에서 매수/매도 방향 계산에 사용 중 — 역전이면 OFI 방향 반전 버그
- **수정 전 반드시**: ofi.py 계산 방향 확인 후 결정 (섣부른 수정 금지)

### [P5] bid/ask = 0 — OFI 영구 0 [DONE 2026-05-04]
- 선물호가잔량 콜백 `_on_hoga_data()` 신설 + `sopt_type="1"` 추가 등록으로 해결
- 모의투자 서버에서 선물호가잔량 수신 확인됨 (로그에서 확인)
- **검증 필요**: [V19] 재시작 후 `[DBG-F4]` 에서 bid/ask 값 확인
## 2026-05-06 세션 후속

### DONE 처리
- [DONE 2026-05-06] BrokerSync startup 차단 원인 1차 규명
- [DONE 2026-05-06] 주문/체결/복원 디버그 관측점 대폭 추가
- [DONE 2026-05-06] 포지션 state 저장 메타(`last_update_reason`, `last_update_ts`) 추가

### 다음 실행 최우선 검증
- [V30] blank placeholder `OPW20006` 응답이 실제로 FLAT 판정으로 해석되는지 검증
- [V31] `ret=-302` 또는 주문 실패 상황에서 로컬 LONG 오픈/복원 불일치가 재발하는지 검증
- [V32] `EntryAttempt -> PendingOrder -> OrderMsgDiag -> ChejanFlow -> PositionDiag` end-to-end 인과관계 검증

### 새 작업
- [T6] startup sync 이후 신규 진입 gate 정책 재검토 (`verified=False`와 `blank row`를 분리)
- [T7] 디버그 로그 정리 단계 준비 (유효 관측점 유지, 과도한 로그는 다음 안정화 후 축소)
