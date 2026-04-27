# 다음 할 일 목록 — futures (미륵이)

> 검증 필요 항목, 예정된 작업, 알려진 잠재 이슈.

### 완료 처리 규칙
- 완료 시 `[DONE YYYY-MM-DD]` 태그 추가
- DONE 태그 후 1주일 경과 시 삭제

---

## 즉시 확인 필요

### [V1] GetRepeatCnt = 0 원인 최종 확인
- **내용**: record_name 수정 후에도 0이 반환되는지 확인
- **방법**: `meta["record_name"]` 출력 → 콜백 수신값 직접 확인
- **기준**: GetRepeatCnt 반환값 > 0 (정상 분봉 데이터 수신)
- **파일**: `collection/kiwoom/api_connector.py`

### [V2] 모의계좌 실시간 분봉 수신 동작 확인
- **내용**: Phase 1 완료 기준 — 키움 API 1분봉 수신 + 파이프라인 end-to-end 동작
- **기준**: `on_candle_closed` → `run_minute_pipeline` → 예측값 로그 출력

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

### [P1] GetCommData 응답 지연 — 모의투자 서버
- GetMasterCodeList("10")이 모의투자 서버에서 None 반환 가능
- 근월물 fallback: 날짜 계산 (3·6·9·12월 두 번째 목요일) 동작 확인 필요

### [P2] py37_32 패키지 호환성
- scipy 1.5.4 고정 필수 (1.7.x DLL 충돌)
- torch 설치 시 32-bit 호환 버전 확인 필요 (PPO GPU 가속 미사용 시 numpy fallback)

### [P3] 뉴스 감성 분석 — HF API 연결 실패 시 fallback
- `features/sentiment/kobert_sentiment.py`: HF API 오프라인 시 키워드 사전 fallback
- 실전 환경에서 fallback 동작 확인 필요

### [P4] 알파 풀 JSON 파일 증가
- `research_bot/alpha_pool.py`: MAX_ACTIVE=50 제한 있으나 퇴역 알파 파일 관리 정책 미확정
