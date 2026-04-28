# 다음 할 일 목록 — futures (미륵이)

> 검증 필요 항목, 예정된 작업, 알려진 잠재 이슈.

### 완료 처리 규칙
- 완료 시 `[DONE YYYY-MM-DD]` 태그 추가
- DONE 태그 후 1주일 경과 시 삭제

---

## 즉시 확인 필요

### [V1] OPT50029 초기 분봉 로드 확인 (A0166000 적용 후)
- **내용**: `GetRepeatCnt > 0` 확인 — 장 시작 직후 초기 분봉 수신 여부
- **방법**: 09:00 직후 재시작 → `[DBG TR-5] GetRepeatCnt=N` 로그 확인
- **기준**: rows > 0 (분봉 히스토리 정상 로드)
- **파일**: `collection/kiwoom/realtime_data.py`, `api_connector.py`

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

## 즉시 확인 필요 (추가됨 2026-04-28)

### [V6] ATR 플로어 적용 후 진입 품질 확인
- **내용**: 재시작 직후 첫 분봉에서 손절 범위 ≥ 0.75pt 확인
- **기준**: `[Position] 진입 LONG @ XXXX | 손절=XXXX` 로그에서 (entry - 손절) ≥ 0.75pt

### [V7] 포지션 복원 로그 확인
- **내용**: LONG 중 재시작 → `[Position] 이전 포지션 복원: LONG 1계약 @ XXXX` 로그
- **기준**: 재시작 후 FLAT 상태가 아닌 기존 포지션 유지

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
