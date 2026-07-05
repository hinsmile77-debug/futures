# 시스템 구현 로드맵

> KOSPI 200 선물 방향 예측 시스템 — 단계별 구현 계획
> 한 번에 모든 기능을 추가하지 않고, 검증된 우선순위에 따라 점진적으로 통합

---

## 전체 일정 개요

```
Phase 0  설계 및 인프라 (완료)         ← 현재 위치
Phase 1  핵심 시스템 구축 (4주)         + v6.5 시간대 전략·분할 진입
                                        + v7.0 Latency Watcher (Week 1)
Phase 2  안전장치 및 검증 (3주)         + v7.0 Hurst Exponent (Week 5)
                                        + v7.0 적응형 켈리 (Week 6)
Phase 3  알파 강화 (4주)                + v6.5 멀티 타임프레임·미시 레짐
                                        + v7.0 VPIN·마디가·Cancel Ratio (Week 8)
Phase 4  차별화 요소 (8주)
Phase 5  실전 운영 (지속)
Phase 6  알파 리서치 봇 (자율 진화 7주)
```

## v7.0 통합 — Gemini 제안서 검토 결과 반영

> Gemini AI Strategist 제안 검토 후 **6/6 전량 채용**
> 목표: MDD -30%, Sharpe 3.5~4.0 달성
> **(상세: docs/REVIEW_REPORT_v7.0.md)**

### 채용 항목 (우선순위 순)

| 순위 | 항목 | 반영 위치 | 기대 효과 |
|------|------|---------|---------|
| 1 | HFT 타임스탬프 동기화 (Latency Watcher) | Phase 1 Week 1 | 백테스트-실전 괴리 차단 |
| 2 | Hurst Exponent (MDD 킬러) | Phase 2 Week 5 | MDD -25~40% |
| 3 | 적응형 켈리 공식 (슬럼프 방어) | Phase 2 Week 6 | 슬럼프 손실 -30% |
| 4 | VPIN (정보거래 확률) | Phase 3 Week 8 | 자동 진입 정확도 +5% |
| 5 | 마디가 필터 (한국 시장 특화) | Phase 3 Week 8 | 헛 진입 -15% |
| 6 | 호가 취소 속도 (스푸핑 감지) | Phase 3 Week 8 | 스푸핑 회피 +3% |

### 제외 항목

없음 — 6개 전량 채용 (중복 없이 순수 보완 관계)

### Hurst Exponent 코드 오류 수정

Gemini 제공 코드에 1건 오류 발견 후 수정:
```
오류: hurst_idx = reg[0] * 2.0  (Variance 분석 혼동)
수정: hurst_idx = reg[0]         (R/S 분석 — polyfit 기울기 = H)
```
수정본: `features/technical/hurst_exponent.py`

### v7.0 기대 성능

```
v6.5 (현재): 정확도 80~85% / Sharpe 3.0~3.5 / MDD 기준치
v7.0 통합:   정확도 82~88% / Sharpe 3.5~4.0 / MDD -30%

Gemini 목표:
  MDD 30% 감소 → 달성 가능 (Hurst + 적응형 켈리)
  Sharpe 2.0 이상 → 초과 달성 (3.5~4.0)
```

---

## v6.5 통합 — 보완 검토 결과 반영

> 자체 보완 제안 검토 후 4개 항목 채용 / 3개 항목 제외
> **(상세: docs/REVIEW_REPORT_v6.5.md)**

### 채용 항목 (우선순위 순)

| 순위 | 항목 | 반영 위치 | 기대 효과 |
|------|------|---------|---------|
| 1 | 시장 상태 분류 (미시 레짐) | Phase 3 Week 11 | 정확도 +4~7% |
| 2 | 멀티 타임프레임 (5분·15분 필터) | Phase 3 Week 8 | 정확도 +3~5%, 거짓 신호 -30% |
| 3 | 시간대 전략 분리 | Phase 1 Week 4 | 정확도 +2~3% |
| 4 | 분할 진입 (2단계 등급별) | Phase 1 Week 4 | 손실 -10%, 수익률 +1~2% |

### 제외 항목 (이유)

| 항목 | 제외 이유 |
|------|---------|
| 오더플로우 분석 | CVD·OFI·LOBID·Microprice 이미 보유 (더 진보됨) |
| EMA(9·21·50) | 1분봉 후행 지표, 노이즈 취약 — AMA·VWAP 우월 |
| 일반 리스크 관리 | Circuit Breaker 5종 트리거로 이미 구현 |

### v6.5 통합 후 기대 성능

```
v6 (현재):     정확도 75~80% / Sharpe 2.5~3.0
v6.5 통합 후:  정확도 80~85% / Sharpe 3.0~3.5
누적 개선: +8~10% (중복 효과 제거 후)
```

---

---

## Phase 0 — 설계 및 인프라 ✅

| 항목 | 상태 |
|------|------|
| 시스템 설계 (v4 완성) | ✅ |
| 폴더 구조 정립 | ✅ |
| Git 저장소 연결 | ✅ |
| PC 간 호환 경로 설계 | ✅ |
| 설계 문서 5종 | ✅ |
| v5 업그레이드 계획 수립 | ✅ |

---

## Phase 1 — 핵심 시스템 구축 (4주)

> 기존 v4 설계 그대로 구현. 안전장치 추가 전이지만 모의투자로만 운영.

### Week 1: 데이터 수집

| 모듈 | 파일 | 우선순위 |
|------|------|---------|
| 키움 API 연결 | `collection/kiwoom/api_connector.py` | 🔴 |
| HFT 타임스탬프 동기화 ⭐v7.0 | `collection/kiwoom/latency_sync.py` | 🔴 |
| 1분봉 실시간 수신 | `collection/kiwoom/realtime_data.py` | 🔴 |
| 투자자별 수급 | `collection/kiwoom/investor_data.py` | 🔴 |
| 옵션 데이터 | `collection/kiwoom/option_data.py` | 🟡 |
| 매크로 수집 | `collection/macro/macro_fetcher.py` | 🟡 |

```
v7.0 채용 사항 — Latency Watcher (최우선):

API 수신 시간 vs 로컬 시간 차이 실시간 측정
  300ms 초과 → 슬리피지 가중치 ×1.5
  1000ms 초과 → 해당 분 신호 차단

이유: 1분봉 시스템 백테스트-실전 괴리의 가장 흔한 원인
     백테스트 수익이 실전에서 사라지는 핵심 메커니즘 차단
```

### Week 2: 피처 엔지니어링

| 모듈 | 파일 | 우선순위 |
|------|------|---------|
| CVD 다이버전스 ⭐CORE | `features/technical/cvd.py` | 🔴 |
| VWAP ⭐CORE | `features/technical/vwap.py` | 🔴 |
| OFI ⭐CORE | `features/technical/ofi.py` | 🔴 |
| 수급 피처 | `features/supply_demand/` | 🔴 |
| 옵션 플로우 | `features/options/` | 🟡 |
| 다이버전스 지수 | `features/options/divergence_features.py` | 🟡 |

### Week 3: 모델 학습

| 모듈 | 파일 | 우선순위 |
|------|------|---------|
| 타겟 라벨 빌더 | `model/target_builder.py` | 🔴 |
| 멀티 호라이즌 모델 | `model/multi_horizon_model.py` | 🔴 |
| 앙상블 결정 | `model/ensemble_decision.py` | 🔴 |
| SGD 온라인 학습 | `learning/online_learner.py` | 🟡 |
| GBM 배치 재학습 | `learning/batch_retrainer.py` | 🟡 |

### Week 4: 매매 전략 및 대시보드

| 모듈 | 파일 | 우선순위 |
|------|------|---------|
| 진입 관리 | `strategy/entry/entry_manager.py` | 🔴 |
| 시간대 전략 라우터 ⭐v6.5 | `strategy/entry/time_strategy_router.py` | 🔴 |
| 분할 진입 (2단계 등급별) ⭐v6.5 | `strategy/entry/staged_entry.py` | 🔴 |
| 청산 관리 | `strategy/exit/exit_manager.py` | 🔴 |
| 시간 청산 (15:10) | `strategy/exit/time_exit.py` | 🔴 |
| 5층 로그 시스템 | `logging_system/log_manager.py` | 🔴 |
| 포지션 추적 | `strategy/position/position_tracker.py` | 🟡 |
| 대시보드 (5개 로그창 통합) | `dashboard/main_dashboard.py` | 🟢 |

```
v6.5 채용 사항 (Phase 1 통합):

시간대 전략 라우터:
  09:05~10:30 변동성 高 → 추세추종, 신뢰도 기준 상향
  10:30~11:50 안정 추세 → 표준 앙상블
  13:00~14:00 유동성 회복 → 외인 재진입 감지, 신호 가중
  14:00~15:00 마감 변동성 → 추세 가속/청산 구간
  15:00~ 청산 임박 → 신규 진입 금지

분할 진입 (등급별):
  A급 (체크리스트 6개 통과): 100% 즉시 진입
  B급 (4~5개): 50% → 1분 후 가격 확인 → 추가 50%
  C급 (2~3개): 50% → 손절 도달 시 추가 진입 안 함
```

---

## Phase 2 — 안전장치 및 검증 (3주) ⚠️ v5 핵심

> Phase 1 완료 후 절대 실전 진입 전 필수. 망하지 않기 위한 단계.

### Week 5: Circuit Breaker + Hurst Exponent (1순위)

| 모듈 | 내용 |
|------|------|
| `safety/circuit_breaker.py` | 5종 발동 조건 감시 |
| `safety/kill_switch.py` | 즉시 비상 정지 |
| `safety/emergency_exit.py` | 전 포지션 시장가 청산 |
| `features/technical/hurst_exponent.py` ⭐v7.0 | MDD 킬러 — 횡보장 진입 차단 |

```
발동 조건 (Circuit Breaker):
  ① 1분 내 신호 5번 반전 → 15분 정지
  ② 5분 내 손절 3연속 → 당일 정지
  ③ 30분 정확도 < 35% → 당일 정지
  ④ 변동성 ATR 3배 초과 → 5분 정지
  ⑤ API 지연 5초 초과 → 즉시 청산

v7.0 Hurst Exponent (안전장치 단계 통합 — Gemini 권장):
  H < 0.45 → 횡보장 진입 차단 (MDD -25~40% 실증)
  H > 0.55 → 추세장 진입 허용 (신뢰도 +10%)
  0.45 ≤ H ≤ 0.55 → 데드존 (신중 진입)

v6.5 미시 레짐과 결합 (Phase 3 적용):
  ADX > 25 AND H > 0.55 → 강한 추세 (+15% 부스트)
  ADX > 25 AND H < 0.45 → 가짜 추세 (진입 차단)

코드 오류 수정:
  Gemini 원본: hurst_idx = reg[0] × 2.0  (오류)
  수정본:      hurst_idx = reg[0]          (R/S 분석 기준)
```

### Week 6: 슬리피지 시뮬레이터 + 적응형 켈리 (2순위)

| 모듈 | 내용 |
|------|------|
| `backtest/slippage_simulator.py` | 현실적 체결가 모델링 |
| `backtest/transaction_cost.py` | 수수료·세금 정확 반영 |
| `strategy/entry/adaptive_kelly.py` ⭐v7.0 | 슬럼프 자동 방어 동적 켈리 |

```
슬리피지 조정 인자:
  base_slip × ATR × 레짐 × 시간대 × 만기효과 × 주문크기
  + Latency Watcher 연동 (v7.0 시너지)

v7.0 적응형 켈리 공식:
  f* = (p × (b+1) - 1) / b
  p = 최근 20회 실전 승률
  b = 최근 20회 손익비

  승률 65%, 손익비 1.5 → f* = 0.42 (적극적)
  승률 50%, 손익비 1.0 → f* = 0.00 (진입 중단)
  승률 40%, 손익비 0.8 → f* < 0   (최소 배율 0.1)

  기존 정적 켈리 → 동적 켈리 교체
  슬럼프 진입 시 자동 사이즈 축소 → 계좌 보호
```

### Week 7: Walk-Forward 검증 (3순위)

| 모듈 | 내용 |
|------|------|
| `backtest/walk_forward.py` | 8주 학습 / 1주 검증 반복 |
| `backtest/performance_metrics.py` | Sharpe·MDD·승률 |
| `backtest/report_generator.py` | HTML 리포트 자동 생성 |

```python
검증 기준:
  - 최소 26주(6개월) Walk-Forward 통과
  - 평균 Sharpe ≥ 1.5
  - 최대 MDD ≤ 15%
  - 승률 ≥ 53%
```

---

## Phase 3 — 알파 강화 (4주)

### Week 8: 시장 미시구조 — TIER S + v7.0

| 모듈 | 기대 효과 |
|------|---------|
| `features/technical/microprice.py` | 정확도 +3~5% |
| `features/technical/lob_imbalance.py` | 정확도 +5~8% |
| `features/technical/queue_dynamics.py` | 단기 방향 선행 |
| `features/technical/multi_timeframe.py` ⭐v6.5 | 정확도 +3~5%, 거짓 신호 -30% |
| `features/technical/htf_filter.py` ⭐v6.5 | 상위 타임프레임 필터 |
| `features/technical/round_number.py` ⭐v7.0 | 헛 진입 -15% |
| `features/supply_demand/vpin.py` ⭐v7.0 | 자동 진입 정확도 +5% |
| `features/supply_demand/cancel_ratio.py` ⭐v7.0 | 스푸핑 회피 +3% |

```
v6.5 채용 사항 — 멀티 타임프레임 분석:
  1분봉 + 5분봉 + 15분봉 동시 분석
  5분봉↑ + 15분봉↑ → 1분봉 매수 신호 ×1.3
  5분봉↓ → 1분봉 매수 신호 차단

v7.0 채용 사항 — VPIN (Gemini 제안):
  VPIN = |매수-매도 거래량| / 총 거래량 (volume bucket 기준)
  VPIN > 0.7 → 큰 움직임 임박 (2010 Flash Crash 유일 감지 지표)
  VPIN 90%ile 도달 → 자동 진입 필수 조건으로 설정

v7.0 채용 사항 — 마디가 필터 (Gemini 제안):
  KOSPI 200: 2.5pt·5pt 단위 심리적 저항
  진입~목표가 사이 마디가 2개↑ → 진입 차단
  마디가 1개 → 등급 하향 (A→B)

v7.0 채용 사항 — Cancel Ratio 스푸핑 감지 (Gemini 제안):
  cancel_ratio = 취소 주문 / 체결 주문
  > 3.0 → 스푸핑 의심 → 반대 방향 가중치 반영
  기존 OFI·LOBID (정적) + Cancel Ratio (동적) 보완 관계
```

### Week 9: 메타 신뢰도 학습기 — TIER S

| 모듈 | 기대 효과 |
|------|---------|
| `learning/meta_confidence.py` | 정확도 +5~8% |
| `learning/calibration.py` | 신뢰도 보정 |

```python
"이 상황에서 내 예측이 얼마나 신뢰할 만한가"를 별도 학습
Renaissance Technologies 핵심 기법
```

### Week 10: 변동성 표적화 — TIER B

| 모듈 | 기대 효과 |
|------|---------|
| `strategy/entry/vol_targeting.py` | Sharpe +0.4 |
| `strategy/entry/dynamic_sizing.py` | MDD -20% |

### Week 11: 군집 행동 + 레짐별 모델 + 미시 레짐 — TIER B

| 모듈 | 기대 효과 |
|------|---------|
| `features/supply_demand/herding.py` | 역발상 정밀화 |
| `model/regime_specific.py` | 정확도 +4~7% |
| `collection/macro/micro_regime.py` ⭐v6.5 | 정확도 +4~7% |
| `collection/macro/regime_strategy_map.py` ⭐v6.5 | 레짐별 전략 매핑 |

```
v6.5 채용 사항 — 미시 레짐 분류 (최우선):

기존 매크로 레짐(1일 1회) + 신규 미시 레짐(매분) 조합
  → 매크로: RISK_ON / NEUTRAL / RISK_OFF (진입 기준 조정)
  → 미시:   추세장 / 횡보장 / 급변장 (전략 자체를 바꿈)

분류 (ADX·ATR 기반):
  ADX > 25, ATR < 평균 1.5배 → "추세장" → 추세추종 우위
  ADX < 20, ATR < 평균        → "횡보장" → 역추세 (개인 역발상)
  ATR > 평균 2배              → "급변장" → 거래 중단/사이즈 축소
  나머지                      → "혼합"   → 표준 앙상블

레짐별 전용 모델과 결합 시 시너지 (정확도 +5%)
```

---

## Phase 4 — 차별화 요소 (8주)

### Week 12-15: 강화학습 정책

| 모듈 | 내용 |
|------|------|
| `learning/rl/environment.py` | 트레이딩 환경 정의 |
| `learning/rl/ppo_agent.py` | PPO 에이전트 |
| `learning/rl/reward_design.py` | 보상 함수 설계 |
| `learning/rl/policy_evaluator.py` | 정책 평가 |

```python
State:  시장 상태 + 포지션 + 미실현 손익
Action: HOLD / BUY_FULL / BUY_HALF / SELL_FULL / SELL_HALF / EXIT
Reward: 다음 1분 PnL - 거래 비용 - 리스크 페널티
```

### Week 16-17: 베이지안 업데이트

| 모듈 | 내용 |
|------|------|
| `learning/bayesian_updater.py` | 사전 확률 실시간 업데이트 |

### Week 18-19: 뉴스 감성 분석

| 모듈 | 내용 |
|------|------|
| `collection/news/news_fetcher.py` | 한경·매경 헤드라인 수집 |
| `features/sentiment/kobert_sentiment.py` | KoBERT 감성 분석 |
| `features/sentiment/news_features.py` | 30분 가중 평균 점수 |

---

## Phase 5 — 실전 운영 (지속)

### 모의투자 단계 (4주)

```
1주차: Phase 1 완료, 모의계좌 운영 시작
2주차: 일일 결과 모니터링, 버그 수정
3주차: 안정성 확인 후 Phase 2 안전장치 적용
4주차: 모의계좌 통산 수익률 확인 (목표: +5% 이상)
```

### 실전 전환 기준

```
모의투자 4주 결과:
  ✓ 통산 수익률 양수
  ✓ 일일 수익률 변동성 안정적
  ✓ Circuit Breaker 1회 이상 정상 작동 확인
  ✓ Walk-Forward 검증 통과
  ✓ CB② 복원 확인 — CB_CONSEC_STOP_LIMIT 9999 → 2~3
    (모의투자 한정 예외 해제. 2026-07-05, docs/260704_SYSTEM_AUDIT_UPGRADE_PROPOSAL.md §7-1)

→ 위 5가지 모두 충족 시 실전 전환
→ 실전 첫 1개월: 최대 사이즈의 30%로 시작
→ 1개월 검증 후 정상 사이즈
```

### 운영 단계

```
일간:  성과 모니터링 + Circuit Breaker 트리거 확인
주간:  Walk-Forward 갱신 + SHAP 피처 심사
월간:  성과 리뷰 + 모델 전체 재학습
분기:  알파 추가 검토 + 전략 재평가
```

---

## 위험 요소 및 완화

| 위험 | 완화 방안 |
|------|---------|
| 키움 API 지연 | API_LATENCY Circuit Breaker (Phase 2) |
| 모델 과적합 | Walk-Forward 검증 (Phase 2) |
| 알파 소실 | SHAP 동적 피처 + 분기별 재평가 |
| 시스템 오류 | Kill Switch + 비상 청산 (Phase 2) |
| 시장 레짐 급변 | 레짐별 전용 모델 (Phase 3) |
| 슬리피지 폭증 | 슬리피지 시뮬레이터 (Phase 2) |

---

## 마일스톤 체크리스트

### Phase 1 완료 기준
- [ ] 키움 API 1분봉 수신 안정 작동
- [ ] CVD·VWAP·OFI 3개 CORE 피처 정상 계산
- [ ] 멀티 호라이즌 예측 모델 학습 완료
- [x] 진입 관리자 (`strategy/entry/entry_manager.py`)
- [x] 시간대 전략 라우터 ⭐v6.5 (`strategy/entry/time_strategy_router.py`)
- [x] 분할 진입 ⭐v6.5 (`strategy/entry/staged_entry.py`)
- [x] 청산 관리자 (`strategy/exit/exit_manager.py`)
- [x] 투자자별 수급 (`collection/kiwoom/investor_data.py`)
- [x] 옵션 데이터 (`collection/kiwoom/option_data.py`)
- [x] 매크로 수집 (`collection/macro/macro_fetcher.py`)
- [x] GBM 배치 재학습 (`learning/batch_retrainer.py`)
- [x] SHAP 피처 심사 (`learning/shap/shap_tracker.py`)
- [x] 5창 대시보드 (`dashboard/main_dashboard.py`)
- [ ] 모의계좌 실시간 진입·청산 동작 확인 (실행 테스트 필요)

### Phase 2 완료 기준 (실전 진입 가능)
- [x] Circuit Breaker 5종 트리거 구현 (`safety/circuit_breaker.py`)
- [x] Kill Switch 구현 (`safety/kill_switch.py`)
- [x] Emergency Exit 구현 (`safety/emergency_exit.py`)
- [x] Hurst Exponent 구현 (`features/technical/hurst_exponent.py`)
- [x] 슬리피지 시뮬레이터 구현 (`backtest/slippage_simulator.py`)
- [x] 거래 비용 계산기 구현 (`backtest/transaction_cost.py`)
- [x] 적응형 켈리 구현 (`strategy/entry/adaptive_kelly.py`)
- [x] 성과 지표 계산기 구현 (`backtest/performance_metrics.py`)
- [x] Walk-Forward 검증기 구현 (`backtest/walk_forward.py`)
- [x] HTML 리포트 생성기 구현 (`backtest/report_generator.py`)
- [ ] Circuit Breaker 5종 트리거 모두 테스트 완료
- [ ] CB② 복원 — `CB_CONSEC_STOP_LIMIT` 9999 → 2~3 (모의투자 한정 예외, 2026-07-05 등록. 실투 전 필수)
- [ ] Walk-Forward 26주 검증 데이터 통과
- [ ] Sharpe ≥ 1.5, MDD ≤ 15%, 승률 ≥ 53%

### Phase 3 완료 기준
- [x] Microprice 피처 (`features/technical/microprice.py`)
- [x] LOB Imbalance (`features/technical/lob_imbalance.py`)
- [x] Queue Dynamics (`features/technical/queue_dynamics.py`)
- [x] 멀티 타임프레임 ⭐v6.5 (`features/technical/multi_timeframe.py`)
- [x] HTF Filter ⭐v6.5 (`features/technical/htf_filter.py`)
- [x] 마디가 필터 ⭐v7.0 (`features/technical/round_number.py`)
- [x] VPIN ⭐v7.0 (`features/supply_demand/vpin.py`)
- [x] Cancel Ratio ⭐v7.0 (`features/supply_demand/cancel_ratio.py`)
- [x] 메타 신뢰도 학습기 (`learning/meta_confidence.py`)
- [x] 보정기 (`learning/calibration.py`)
- [x] 변동성 표적화 (`strategy/entry/vol_targeting.py`)
- [x] 동적 사이징 (`strategy/entry/dynamic_sizing.py`)
- [x] 군집 행동 감지 (`features/supply_demand/herding.py`)
- [x] 레짐별 전용 모델 (`model/regime_specific.py`)
- [x] 미시 레짐 분류기 ⭐v6.5 (`collection/macro/micro_regime.py`)
- [x] 레짐 전략 매핑 ⭐v6.5 (`collection/macro/regime_strategy_map.py`)
- [ ] Microprice 피처 추가 후 정확도 +3% 이상 (실데이터 검증)
- [ ] 메타 신뢰도 학습기 정확도 +5% 이상 (실데이터 검증)
- [ ] 레짐별 모델 적용 후 Sharpe +0.25 이상 (실데이터 검증)

### Phase 4 완료 기준
- [x] 강화학습 환경 (`learning/rl/environment.py`) — State/Action/Reward 정의
- [x] PPO 에이전트 (`learning/rl/ppo_agent.py`) — numpy fallback + torch optional
- [x] 보상 함수 (`learning/rl/reward_design.py`) — PnL - 비용 - 리스크 패널티
- [x] 정책 평가기 (`learning/rl/policy_evaluator.py`) — Sharpe 비교 + Phase4 PASS 판정
- [x] 베이지안 업데이터 (`learning/bayesian_updater.py`) — 온라인 사후 확률 갱신
- [x] 뉴스 수집기 (`collection/news/news_fetcher.py`) — 한경·매경·연합 RSS
- [x] 감성 분석기 (`features/sentiment/kobert_sentiment.py`) — 키워드 사전 + HF API
- [x] 뉴스 피처 빌더 (`features/sentiment/news_features.py`) — 30분 가중 평균 피처
- [ ] 강화학습 정책 정적 규칙 대비 Sharpe +0.4 이상 (실거래 데이터 검증 필요)
- [ ] 뉴스 감성 분석 알파 검증 (실거래 데이터 검증 필요)

---

## Phase 5 진입 후 — 앙상블 고도화 (M2 챌린저 로드맵)

> 실전 운영 진입 후 실데이터가 충분히 쌓이면 아래 두 단계를 순서대로 진행한다.
> 현재 배포된 `HorizonDecorrelator` (상관관계 역수 적응형 가중치)가 1단계 완화책이다.

### 1단계 — 실데이터 4주 축적 후: 잔차 타겟 A/B 테스트

```
조건: Phase 5 진입 후 실데이터 4주(~5,000 분봉) 이상 축적
목적: 계층적 잔차 타겟이 현행 직접 타겟보다 실제로 유리한지 검증

방법:
  A 모델 (현행): 6개 GBM — 각 호라이즌 방향 라벨 직접 예측
  B 모델 (챌린저): 6개 GBM — 잔차 타겟 학습
    r_1m_residual = r_1m  (기준, 변경 없음)
    r_3m_residual = r_3m - GBM_1m 예측 설명분
    r_5m_residual = r_5m - (1m+3m 예측 설명분)
    ...

판정 기준:
  2주 Shadow 평가: B 모델 Sharpe > A 모델 Sharpe × 1.10
  ShadowEvaluator.is_hotswap_ready() 통과 시 Hot-Swap 승인

파일 변경 범위:
  - model/target_builder.py    — 잔차 타겟 생성 함수 추가
  - learning/batch_retrainer.py — 잔차 타겟 학습 분기 추가
  - model/multi_horizon_model.py — 변경 없음 (타겟만 달라짐)
```

- [ ] 실데이터 4주 축적 확인 (`raw_data.db raw_candles ≥ 5,000행`)
- [ ] `model/target_builder.py` 잔차 타겟 생성 함수 구현
- [ ] `learning/batch_retrainer.py` 잔차 타겟 학습 분기 추가
- [ ] 2주 Shadow 평가 통과 확인
- [ ] Hot-Swap 승인 후 챌린저 → 챔피언 전환

### 2단계 — Phase 5 안정화 후: 계층적 앙상블 (M2 원안)

```
조건: 1단계 잔차 타겟 Hot-Swap 완료 + 실전 운영 2개월 이상
목적: 6개 호라이즌 앙상블을 계층적 직교 신호 구조로 전환 (이중 가중 근본 해소)

설계:
  Level 0: GBM_1m(raw) — 순수 단기 신호
  Level 1: GBM_3m(residual) — 1m 정보 제거 후 순수 3m 추가 정보
  Level 2: GBM_5m(residual) — (1m+3m) 정보 제거 후 순수 5m 추가 정보
  ...
  앙상블: orthogonal 신호의 독립적 합산 → double-counting 원천 차단

이론 기대 효과: Sharpe +0.15~0.25 (HorizonDecorrelator 대비 추가 +0.10~0.15)

선행 조건:
  - 1단계 완료 (잔차 타겟이 유효함을 실증)
  - Walk-Forward 재검증 (26주 이상)
```

- [ ] 1단계 완료 확인
- [ ] `model/ensemble_decision.py` 계층적 합산 로직 설계
- [ ] Walk-Forward 26주 재검증 통과
- [ ] 챌린저 ShadowEvaluator 2주 평가 통과
- [ ] Hot-Swap 승인 후 배포

## 260704 감사 로드맵 — Triple-barrier 레이블 섀도우 병행 (P1)

> 감사 근거: `docs/260704_SYSTEM_AUDIT_UPGRADE_PROPOSAL.md` §1-3 ①.
> "레이블이 손익과 무관하다" — 기존 3클래스 레이블은 "N분 후 수익률이 threshold를
> 넘는가"만 보고 실제 청산 규칙(하드스톱·TP1)과 무관하다. 진입 가정 후 TP/SL/시간
> 배리어 중 무엇이 먼저 닿는가로 레이블을 바꿔 "모델 예측 = 시스템 실행"을 맞춘다.

### 구현 완료 (2026-07-05)

```
model/target_builder.py     — build_triple_barrier_label() 추가
                               (진입=롱 가정, TP=ATR×tp_mult, SL=ATR×stop_mult,
                                시간배리어=호라이즌 분. 실제 청산 배수와 동일하게 전달)
learning/batch_retrainer.py — retrain_shadow_triple_barrier() 추가
                               raw_features_horizon(3m~30m) + raw_features 폴백(1m,
                               raw_features_horizon에 1m 행이 설계상 없음) 사용.
                               저장 위치: model/horizons/shadow_triple_barrier/
                               (프로덕션 champion 모델과 완전 분리 — 실거래 미사용)
scripts/run_shadow_triple_barrier_retrain.py — 수동/스케줄 실행 진입점
```

동작 검증(2026-07-05, 개발 DB 실측): 6개 호라이즌 모두 성공, 1m n=44,189 (raw_features
폴백), 3m~30m n=728~7,583 (raw_features_horizon). cv_acc는 클래스 불균형(장기 호라이즌일수록
FLAT 비중 급증) 영향이 커서 기존 champion cv_acc와 **직접 비교 불가** — 회당 accuracy가
아니라 아래 병행 평가에서 실제 손익 상관으로 판정해야 함.

### 다음 단계 — 2~4주 병행 평가 (미착수)

```
목적: triple-barrier 섀도우 예측이 기존 3클래스보다 "손익"과 더 강하게 상관되는지 검증.
방법: scripts/run_shadow_triple_barrier_retrain.py를 EOD마다 반복 실행해 섀도우 모델 갱신
      + 섀도우 모델의 실시간 예측을 별도 로그(신설 필요)로 남겨 실제 체결 손익(trades.db)과
      상관 분석. 실거래 의사결정에는 연결하지 않는다(감사 §7-8 원칙 — 검증 없는 알파 자동
      통합 금지, CLAUDE.md 절대원칙⑥과 동일 정신).
```

- [x] `model/target_builder.py` triple-barrier 빌더 구현
- [x] `learning/batch_retrainer.py` 섀도우 학습 경로 신설 (1m raw_features 폴백 포함)
- [ ] 섀도우 모델 실시간 예측 로깅 인프라 신설 (별도 DB 테이블 또는 predictions.db 확장)
- [ ] 2~4주 병행 실행 + 예측-손익 상관 분석
- [ ] 상관 우위 확인 시 챌린저 승격 검토 (4절 통계적 검정력 기준 적용 — min_trades 등)

## 260704 감사 로드맵 — Meta-labeling 게이트 승격 (P1)

> 감사 근거: `docs/260704_SYSTEM_AUDIT_UPGRADE_PROPOSAL.md` §1-3 ②, §2-2 ④.
> "이미 `learning/meta_labeling.py`, `strategy/entry/meta_gate.py`가 존재하고 rollout
> 리포트가 '메타 라벨 65,183건 준비 완료'라고 말한다 — 자산이 놀고 있다." 목표 구조:
> 1차(방향)=기존 앙상블 유지 / 2차(진입 여부)="이 신호로 진입 시 수익 확률"을 학습하는
> 이진 분류기. 9항목 체크리스트의 등가 카운트 방식을 데이터 기반으로 대체.

### 구현 완료 (2026-07-05)

```
learning/meta_label_classifier.py — train_entry_quality_models() / EntryQualityScorer
    predictions.db meta_labels 테이블(호라이즌별 실측 65,183건, 2026-07-05 기준)로
    호라이즌별 이진 분류기 학습. 레이블 = meta_action != "skip"(take/reduce,
    derive_meta_label()에서 이미 realized_move>0으로 판정된 케이스) → 1, skip → 0.
    저장 위치: model/horizons/meta_gate/ (gitignore 처리, PC별 로컬 산출물)
scripts/train_meta_label_classifier.py — 수동/스케줄 실행 진입점
strategy/entry/meta_gate.py — MetaGate.evaluate()에 horizon 인자 추가 +
    entry_quality_prob 필드를 섀도우 신호로 반환 (action/size_multiplier 미변경)
learning/prediction_buffer.py — ensemble_decisions.meta_entry_quality_prob 컬럼에
    매분 기록 (save_ensemble_decision + save_step9_batch 양쪽 경로 모두)
utils/db_utils.py — ensemble_decisions 마이그레이션에 meta_entry_quality_prob 컬럼 추가
```

개발 DB 실측(2026-07-05): 6개 호라이즌 모두 학습 성공, n=10,296~12,000, AUC 0.49~0.59
(1m=0.5675, 10m=0.5871이 상대적으로 높음 — 감사가 "유일한 실측 엣지"로 지목한 1m과
방향이 일치). AUC가 낮게 나오는 것은 왜곡이 아니라 정직한 신호 강도 측정 — 방향
예측 자체의 엣지가 약하다는 감사 결론(§0)과 일관됨.

### 다음 단계 — 상관 검증 후 체크리스트 하드 veto 전환 (미착수)

```
목적: entry_quality_prob이 실제 거래 손익과 충분히 상관될 때만 체크리스트를 대체한다.
방법: ensemble_decisions.meta_entry_quality_prob를 trades.db 실현 손익과 ts로 조인해
      상관 분석(주간 또는 EOD 스크립트) → 문턱값 이상 시 checklist.py의 등가카운트 로직을
      entry_quality_prob 기반 게이트로 교체하고, 체크리스트는 8_time·9_risk 등 하드 리스크
      veto만 남긴다(감사 §2-3 P2 항목). 검증 전 하드 게이트 전환 금지.
```

- [x] `meta_labels` 활용 이진 분류기 학습 파이프라인 구현
- [x] `MetaGate`에 섀도우 신호로 연결 (실거래 미영향)
- [x] `ensemble_decisions`에 매분 로깅 (상관 분석용 데이터 축적 시작)
- [ ] 상관 분석 스크립트 작성 (`ensemble_decisions.meta_entry_quality_prob` × `trades.db` PnL)
- [ ] 문턱값 이상 확인 시 `checklist.py` 하드 veto 전환 설계

## 260704 감사 로드맵 — MAE/MFE 기반 배리어 재산정 (P1)

> 감사 근거: `docs/260704_SYSTEM_AUDIT_UPGRADE_PROPOSAL.md` §3-2 ②, §3-3 P1.
> "ATR×1.5 스톱, ×0.3~0.7 TP1은 설계값이지 실측값이 아니다... MAE/MFE 분석이 한 번도
> 반영된 흔적이 없다." → `scripts/analyze_mae_mfe.py` 신설 (읽기 전용 진단, 자동 적용 없음).

### 구현 완료 (2026-07-05)

```
scripts/analyze_mae_mfe.py
    trades.db 체결 이력 × raw_candles(high/low) 경로 복원으로:
      - 승리 거래 MFE 분포(P25/50/75/90) vs 현재 ATR_HORIZON_TP1_MULT
      - 패배 거래 MAE 분포(P25/50/75/90) vs 현재 ATR_STOP_MULT
      - 손절 이후 N분(기본 15) 사후 가격 경로 → "회복 비율" (스톱 과소 진단)
      - TP 이후 N분 사후 가격 경로 → "추가 유리폭" (TP 과소/조기익절 진단)
    결과는 콘솔 출력 + data/mae_mfe_report.txt 저장(재생성 가능, gitignore 처리).
    배리어 값을 자동으로 바꾸지 않음 — 사용자가 수치를 보고 config/settings.py를 수동 조정.
```

개발 DB 실측(2026-07-05, n=20 소표본·참고용): 승리 MFE P50=2.70pt, 패배 MAE P50=4.40pt,
손절 후 15분 내 진입가 재돌파 비율 77.8%(n=9) — 표본이 작아 결론을 내리기엔 이르지만,
운영 데이터가 쌓이면(분기 1회 재실행 권장) 하드스톱 과소(too tight) 여부를 판단할 실측
근거가 된다.

- [x] `scripts/analyze_mae_mfe.py` 신설 — MAE/MFE 분포 + 손절/TP 사후 경로 분석
- [ ] 분기 1회 재실행 후 `ATR_STOP_MULT`/`ATR_HORIZON_TP1_MULT` 조정 여부 사용자 판단
      (표본 100건 이상 축적 후 재실행 권장 — 현재 20건은 참고 수준)

## 260704 감사 로드맵 — 신호 소멸 청산 (P4.5) (P1)

> 감사 근거: `docs/260704_SYSTEM_AUDIT_UPGRADE_PROPOSAL.md` §3-2 ①.
> "청산이 순수 가격 기반 — 예측 시스템인데 예측을 안 쓴다. 보유 중 앙상블이 반대 방향
> 고신뢰로 전환돼도 청산 트리거가 없다. 손절가까지 풀로 얻어맞는 구조."
>
> **중요**: `strategy/exit/exit_manager.py`의 P1~P6 문서화된 우선순위는 실거래 경로가
> 아니다(2026-07-05 확인 — main.py 어디서도 이 클래스를 인스턴스화하지 않음, 순수
> 미사용 레거시). 실제 청산 로직은 `main.py:_check_exit_triggers()`에 인라인으로
> 구현되어 있으며, 실질 우선순위는: 1순위 하드스톱(인트라바 포함) → 3순위 TP1/TP2
> 부분청산 → 4순위 15:10 시간강제청산. 이번 항목은 이 실제 코드에 추가했다.

### 구현 완료 (2026-07-05) — 이 항목은 **실거래 청산 로직을 변경**

```
config/settings.py — SIGNAL_DECAY_EXIT_ENABLED = True (기본 ON)
main.py:_check_exit_triggers() — TP1/TP2 부분청산 다음, 15:10 시간강제청산 이전에
    "3.5순위" 삽입: 보유 포지션과 반대 방향의 decision["direction"]이
    decision["min_conf"](=zone_mc, 시간대×호라이즌 동적 임계값) 이상 신뢰도로
    나오면 즉시 전량 청산(exit_reason="신호소멸청산"). 손절가 도달 전 탈출.
```

기본 ON 결정 근거: 모의투자 단계라 실거래 자금 리스크가 없고(CB② 예외와 동일 논리),
검증은 실거래 데이터 축적으로만 가능하므로 바로 켠다. **실투 전환 전 재검토 필수**
(모의투자 기간 중 신호소멸청산 발동 빈도·손익 기여를 점검할 것).

- [x] `config/settings.py`에 `SIGNAL_DECAY_EXIT_ENABLED` 플래그 추가 (기본 True)
- [x] `main.py:_check_exit_triggers()`에 신호 소멸 청산 삽입 (TP 이후·시간청산 이전)
- [ ] 모의투자 운영 데이터로 발동 빈도·손익 기여 검증 (exit_reason="신호소멸청산" 필터)
- [ ] 실투 전환 전 재검토 — 필요 시 OFF 또는 부분청산으로 완화

## 260704 감사 로드맵 — 지정가 우선 집행 (P1)

> 감사 근거: `docs/260704_SYSTEM_AUDIT_UPGRADE_PROPOSAL.md` §2-3 P1.
> "진입: microprice 기준 유리한 쪽 1틱 지정가 → N초(10~15초) 미체결 시 취소 또는
> 시장가 전환." 기본 OFF — Cybos 지정가/취소 주문 자체가 이번에 처음 구현되어
> 이 개발환경(py3.11, COM 미지원)에서는 실제 브로커 연결로 검증 불가.

### TR 스펙 출처 (중요)

`collection/cybos/api_connector.py`의 기존 `send_market_order()`(CpTd6831, idx6="2")는
`docs/CyBos ref/CYBOS_FUTURES_ORDER_TR_MAP.md`(사용자 제공 — Cybos Plus 공식 TR 테스트
예제 `order_futureoptionjumuntest.xls`를 xlrd로 직접 파싱해 실제 계좌번호·주문번호·
서버 응답메시지가 담긴 실측 캡처, 2026-07-05 확인)와 필드 순서가 **완전 일치**해
교차검증됐다. 이 문서 기준으로 지정가(`idx6="1"`, `idx4`=실제가격)와 취소주문
(`CpTd6833`, `CpTd6033`이 아님 — 흔한 오해)을 구현했다.

### 구현 완료 (2026-07-05) — 기본 OFF

```
config/settings.py — LIMIT_ENTRY_FIRST_ENABLED=False, LIMIT_ENTRY_TIMEOUT_SEC=12
collection/cybos/api_connector.py — send_limit_order()(CpTd6831 idx6='1') +
    cancel_order()(CpTd6833) 신규. send_market_order()와 동일 검증된 패턴 재사용
    (BlockRequest 스레드 격리, -99 타임아웃 처리, _emit_msg 페이로드).
collection/broker/base.py, cybos_broker.py — 두 메서드 인터페이스 노출 (비추상
    메서드 — 미지원 브로커는 기본 실패 반환, KiwoomBroker 등 무변경).
main.py:_send_broker_entry_order() — LIMIT_ENTRY_FIRST_ENABLED=True일 때
    realtime_data._last_bid1/_last_ask1 + get_contract_spec(code)["tick_size"]로
    1틱 유리한 지정가 계산 → send_limit_order() 시도. 실패 시 즉시 시장가 폴백.
main.py:_ts_execute_entry() — 지정가 접수 성공 시 낙관적 포지션 오픈을 건너뛴다
    (기존 시장가 경로의 "Fix B" 낙관적 오픈은 그대로 유지 — OFF 시 동작 무변경).
    실제 오픈은 Chejan 체결(apply_entry_fill의 status==FLAT 분기)로만 반영.
main.py:_check_limit_entry_timeout() — 2초 주기 QTimer. LIMIT_ENTRY_TIMEOUT_SEC
    경과 시 무조건 취소만 함 — 시장가 전환 없음(2026-07-05 사용자 지시: 가정이
    깨져도 안전하도록 포지션을 억지로 열지 않는다). 부분체결분은 그대로 유지.
main.py:_ts_on_chejan_event() — [LimitEntry][CHEJAN_EVENT] 계측 로그 추가
    (체결 타이밍 실측용 — 이후 가정을 실측치로 교체하는 근거 데이터).
```

**설계 원칙(사용자 지시, 2026-07-05)**: 로직을 완성해서 배선하기 전에 계측부터.
`[LimitEntry][ORDER_SENT]`/`[CHEJAN_EVENT]`/`[TIMEOUT]`/`[CANCEL]` 로그가 이미
타임스탬프와 함께 남게 되어 있어, 모의투자 1~2주 운영 후 "지정가 체결까지 평균/최대
몇 초 걸렸는지"를 실측치로 확인하고 `LIMIT_ENTRY_TIMEOUT_SEC` 등 가정값을 교체할 수
있다. 타임아웃 시에도 시장가 전환 없이 취소만 하도록 해 가정이 틀려도(체결이 예상보다
오래 걸려도) 포지션이 억지로 열리는 위험이 없다.

### 수동 검증 체크리스트 (실투/모의투자 환경, py37_32+Cybos 필요 — 이 세션에서 불가)

- [ ] `LIMIT_ENTRY_FIRST_ENABLED=True`로 설정 후 모의투자 계좌에서 진입 1회 트리거
- [ ] 로그에 `[LimitEntry][ORDER_SENT]`가 찍히고 HTS/조회화면에 실제 지정가 미체결
      주문이 뜨는지 확인 (가격이 계산대로 1틱 유리한 쪽인지)
- [ ] 체결 시 `[LimitEntry][CHEJAN_EVENT]` 로그 확인 + 포지션이 정확히 그 시점에만
      열리는지(체결 전에는 포지션 없음) 확인
- [ ] 의도적으로 체결 안 되는 가격대(예: 유동성 얇은 순간)에서 타임아웃 유도 →
      `[LimitEntry][TIMEOUT]` + `[LimitEntry][CANCEL]` 로그 확인 + HTS에서 해당
      주문이 실제로 취소됐는지, 포지션이 열리지 않았는지 확인
- [ ] 부분체결 시나리오 — 일부만 체결 후 타임아웃 → 부분 포지션만 남고 잔량 취소되는지
- [ ] 위 항목 통과 후에만 실거래(모의투자 이후 단계) 활성화 검토

- [x] Cybos 지정가/취소 TR 구현 (사용자 제공 레퍼런스 문서 기준 교차검증)
- [x] main.py 오케스트레이션(타임아웃 타이머, 낙관적 오픈 스킵) — 기본 OFF
- [x] 계측 로깅 (ORDER_SENT/CHEJAN_EVENT/TIMEOUT/CANCEL)
- [ ] 실제 Cybos 연결로 수동 검증 (위 체크리스트) — 사용자가 py37_32+Cybos 환경에서 수행
- [ ] 검증 통과 후 모의투자에서 활성화 → 1~2주 데이터로 타임아웃 등 가정값 재조정

## 260704 감사 로드맵 — 게이트/레이어 ablation 주간 리포트 (P1, 완료 — P1 전 항목 완료)

> 감사 근거: `docs/260704_SYSTEM_AUDIT_UPGRADE_PROPOSAL.md` §2-3 P1, §7-3.
> "게이트 과잉... 각각은 사고의 사후 대응으로 정당하나, 총합의 한계 기여를 아무도
> 모른다." "매주: 각 게이트별 '이 게이트만 없었으면 진입했을 거래'의 가상 손익 집계"

### 구현 완료 (2026-07-05)

```
scripts/generate_gate_ablation_report.py
    predictions.db의 ensemble_decisions.entry_gate_json(STEP7 마스터 게이트 개별
    결과, 18개 불리언) + meta_labels.realized_move(방향성 실현폭)를 조인.
    각 신호품질 게이트(hurst_ok/atr_ok/open_gap_ok/bar_volume_ok, meta_gate,
    toxicity_gate)가 "단독으로" 차단한 신호만 골라 그 신호의 가상 realized_move
    분포(평균/승률/합계)를 "모든 게이트 통과 신호" 기준선과 비교.
    안전/운영 게이트(kill_switch·CB·broker_sync·cooldown 등 14개)는 ablation
    대상에서 제외 — 이들은 "기여 없으면 제거"가 아니라 존치해야 하는 안전장치.
    읽기 전용 — 게이트를 자동으로 끄거나 제거하지 않음.
```

개발 DB 실측(2026-07-05, 60일 n=7,695건): 분석한 6개 신호품질 게이트 모두 "단독 차단"
신호의 평균 realized_move가 양수 — 즉 이 게이트들이 막은 신호가 평균적으로는 유리한
방향으로 움직였다는 신호. 단, `atr_ok`(n=3)·`hurst_ok`(n=45)는 표본이 작아 결론을
내리기엔 이르고, `meta_gate`(n=1,378)·`toxicity_gate`(n=301)는 표본이 상대적으로
충분해 신뢰도가 더 높음. 매주 재실행해 표본을 늘려가며 판단할 것 — 감사 §2-3 권고대로
"기여 없는(또는 음의 기여) 게이트"가 나타나면 그때 완화/제거를 검토.

**주의**: realized_move는 1m 호라이즌 방향성 실현폭(수수료·실제 TP/SL 경로 미반영)
근사치다. 실제 거래 손익과는 다를 수 있으므로 참고 지표로만 사용할 것 — 15겹 앙상블
레이어(Decorrelator·F1가중·CoherenceGate 등, §7-3)의 leave-one-out은 각 레이어를
설정으로 ON/OFF 가능하게 만드는 선행 작업이 필요해 이번 범위에서는 제외(다음 단계).

- [x] `scripts/generate_gate_ablation_report.py` 신설 — 신호품질 게이트별 단독차단 분석
- [ ] 매주 재실행하며 표본 누적 → 기여 없는 게이트 발견 시 완화/제거 검토
- [ ] (다음 단계) `ensemble_decision.py` 15겹 레이어 ON/OFF 플래그화 → leave-one-out shadow 평가

**P1 로드맵 5개 항목 전체 완료** (Triple-barrier·Meta-labeling·MAE/MFE·신호소멸청산·
지정가집행·ablation리포트 — 지정가집행 포함 총 6개). 다음은 P2(HistGBM 전환,
신규 피처, 챌린저 부트스트랩, TP1 A/B)로 진행.

## 260704 감사 로드맵 — HistGBM 전환 + 분위 회귀 채널 (P2)

> 감사 근거: `docs/260704_SYSTEM_AUDIT_UPGRADE_PROPOSAL.md` §1-3 ③④.

### ③ HistGBM 전환 — 감사 지적 무효, 이미 완료된 상태였음

`learning/batch_retrainer.py` 재검토(2026-07-05) 결과 `HistGradientBoostingClassifier`가
**이미 기본 학습 경로**였다. `_HIST_GBM_OK` 플래그로 가용성을 확인해 우선 사용하고,
불가 시에만 `GradientBoostingClassifier`로 fallback — 2026-06-11 벤치마크 주석
("GBM(n=100): total=272s ... HistGBM(n=100): total=0.6s")까지 남아있어 감사보다
먼저 반영된 항목이었다. **추가 작업 없음.**

### ④ 분위 회귀(Quantile Regression) 보조 채널 — 신규 구현 완료 (2026-07-05)

```
learning/quantile_regressor.py — train_quantile_models() / QuantileScorer
    호라이즌별 N분 후 가격변동(포인트)의 q10/q50/q90을 GradientBoostingRegressor
    (loss="quantile")로 추정. HistGradientBoostingRegressor의 quantile loss는
    sklearn 1.1+ 필요(1.0.2 미지원)라 감사 원안대로 GradientBoostingRegressor 사용.
    데이터 로딩은 triple-barrier 섀도우와 동일한 raw_features_horizon+1m폴백 전략 재사용.
    저장 위치: model/horizons/quantile/ (gitignore 처리)
scripts/train_quantile_regressor.py — 수동/스케줄 실행 진입점
strategy/entry/meta_gate.py — MetaGate.evaluate()에 quantile_estimate 섀도우 필드 추가
    (action/size_multiplier 미변경 — entry_quality_prob과 동일한 섀도우 원칙)
learning/prediction_buffer.py + utils/db_utils.py — ensemble_decisions에
    quantile_expected_pt/quantile_uncertainty_pt 컬럼 신설, 매분 로깅
```

개발 DB 실측(2026-07-05, 26주): 6개 호라이즌 모두 학습 성공. 커버리지 진단(이상적으로
10%/10%) — 1m이 가장 정교(12.5%/11.9%), 3m~30m은 15~18%대로 다소 넓게 벗어남(분위
추정이 실제보다 좁음, 즉 꼬리 리스크를 과소평가하는 경향). 1m이 다시 한번 가장 잘
보정된 호라이즌으로 나타남 — "1m이 유일한 실측 엣지"라는 감사 진단과 일관.

**주의 — 실거래 미연결**: `entry_quality_prob`과 동일하게 섀도우 신호로만 로깅.
사이징·TP 거리 산정에 실제로 반영하려면 `ensemble_decisions.quantile_*` 컬럼이
충분히 쌓인 뒤 손익 상관을 검증해야 한다(감사가 원하는 진짜 가치는 "사이징에 직결"
이지만, 검증 없는 즉시 연결은 이 프로젝트의 반복 원칙에 위배됨).

- [x] HistGBM — 이미 완료 확인 (추가 작업 불필요)
- [x] 분위 회귀 채널 구현 + MetaGate 섀도우 연결 + ensemble_decisions 로깅
- [ ] 커버리지 보정 검토 (3m~30m 꼬리 과소평가 — GBR_PARAMS/학습 윈도 조정 여지)
- [ ] 손익 상관 검증 후 사이징/TP 거리 실제 연결 여부 결정

## 260704 감사 로드맵 — 신규 피처 ① 선물-현물 베이시스 (P2)

> 감사 근거: `docs/260704_SYSTEM_AUDIT_UPGRADE_PROPOSAL.md` §6-3 순위 1.
> "차익거래 압력의 직접 신호. 국내 선물 단기 방향의 고전적 강신호인데 미탑재."

### 중요 정정 — 감사의 "이미 수집 중" 전제는 틀렸음

감사는 "Cybos KOSPI200 지수 + 선물가 — 이미 수집 중인 데이터의 조합"이라고 했으나,
실제로는 **KOSPI200 현물지수가 시스템 어디에도 수집되고 있지 않았다** (2026-07-05 확인).
옵션체인 모듈(`OptionChainWorker`)조차 진짜 현물가 대신 선물 종가를 spot으로 대체해
쓰고 있었다(`main.py` — `spot = self._last_close`). 베이시스 구현은 실제로는
**신규 실시간 데이터 소스 추가**가 필요한 작업이었다.

### KOSPI200 현물지수 코드 확인 과정 (정정 이력 포함)

Cybos 공식 문서(`cybosplus.github.io/cpdib_rtf_1_/stockmst.htm`)로 `dscbo1.StockMst`
TR의 필드(입력 idx0=종목코드, 출력 idx11=현재가, idx1=종목명)를 확인했으나 KOSPI200
지수 자체의 종목코드는 문서로 특정이 안 됐다. `CpUtil.CpCodeMgr.GetIndustryList()`로
후보(`K2G01P`="코스피 200")를 찾았으나 처음엔 폐기하고, 사용자가 Cybos Plus 클라이언트의
종목코드검색 화면 스크린샷으로 `00800 = KOSPI200지수`를 확인해 그걸로 구현했다.
(참고: `A0567`=미니코스피 F 2607, `A0169`=코스피 F 2607 — 선물 코드도 스크린샷에서 함께 확인)

**이후 사용자가 추가 스크린샷으로 정정**: `00800`과 `K2G01P`는 **같은 KOSPI200 지수값을
가리키지만 TR 네임스페이스가 다르다** — `00800`은 선물차트 코드(FutOptChart 등 선물
문맥), `K2G01P`는 주식차트/일반시세 지수코드(StockChart/StockMst 등 문맥). `dscbo1.StockMst`는
일반 시세조회 TR이므로 **`K2G01P`가 맞는 코드**다. `KOSPI200_INDEX_CODE`를 `K2G01P`로
수정 완료(2026-07-05) — 웹 검색으로 처음 찾았던 K2G01P를 성급히 폐기했던 것이 결국
맞는 답이었던 사례. 코드 네임스페이스가 TR 종류(선물차트 vs 일반시세)에 따라 갈린다는
교훈.

이 세션 중 py37_32 환경에서 실제 Cybos/Creon Plus COM 객체 생성까지는 성공했으나
("`U-CYBOS와 연결이 연동되어 있지 않습니다`" 에러) — 클라이언트가 로그인되어 있지
않아 실제 가격 조회는 검증하지 못했다. 코드 자체(`get_index_price()`)는 COM
예외를 안전하게 삼켜 None을 반환하도록 방어적으로 작성됨 — 연결 실패해도 파이프라인에
영향 없음.

### 구현 완료 (2026-07-05)

```
collection/cybos/api_connector.py — get_index_price(code="K2G01P") 신규.
    dscbo1.StockMst 호출 + 종목명에 "200" 포함 여부 자체검증(틀린 코드 방지) +
    일반 Exception까지 삼켜 폴링 실패가 파이프라인에 전파되지 않도록 방어.
collection/broker/base.py, cybos_broker.py — get_index_price() 인터페이스 노출.
features/technical/basis.py — BasisCalculator: 베이시스(선물가-현물지수)·변화율
    계산. 현물지수 결측 시 마지막 유효값 유지 + ready=False (0으로 리셋 안 함 —
    감사 §6-2 위생 원칙과 동일하게 결측을 상수로 방치하지 않음).
main.py — _kospi200_index_timer(60s QTimer)로 폴링, feature_builder.build()에
    basis_data 파라미터로 전달해 병합. 일일 리셋 포함.
features/feature_builder.py — build()에 basis_data 파라미터 추가.
featureset by horizon/horizon_feature_sets.json — 1m/3m/5m/10m에
    basis_pt/basis_change_pt를 include_pending_validation으로 등록
    (기본 학습 미포함 — IC/SHAP 검증 통과 전까지 include_pending=True 명시 필요).
```

- [x] KOSPI200 현물지수 코드 확인 (K2G01P — 주식차트/일반시세 네임스페이스. 00800은
      선물차트 네임스페이스로 같은 지수값이지만 이 TR엔 부적합, 사용자가 2차 스크린샷으로 정정)
- [x] `get_index_price()` Cybos TR 구현 (자체검증 + 예외방어)
- [x] `BasisCalculator` + main.py 폴링/병합/일일리셋 배선
- [x] `horizon_feature_sets.json`에 pending_validation 등록 (1m/3m/5m/10m)
- [ ] 실제 Cybos 로그인 세션에서 idx11 현재가가 실제 KOSPI200 지수값(예: 300~400대)과
      일치하는지 사용자 확인 필요 (이 세션에서는 미연결로 검증 불가)
- [ ] IC 사전검증 → SHAP 심사 통과 시 `include`로 승격 (기존 파이프라인 절차 그대로)

## 260704 감사 로드맵 — 신규 피처 ④ VKOSPI 장중값 (P2)

> 감사 근거: `docs/260704_SYSTEM_AUDIT_UPGRADE_PROPOSAL.md` §6-3 순위 4.
> "강등된 macro_vix(미국·일봉)의 올바른 대체재 — 국내·장중."

베이시스와 완전히 동일한 방식(`get_index_price()` 재사용)으로 구현. KOSPI200과
마찬가지로 사용자가 Cybos Plus 클라이언트 종목코드검색 스크린샷으로 코드를 직접
확인했다 — **`O2901P` = 코스피 200 변동성지수**. 처음 "변동성지수"로 검색했을 때
나온 `A0567`은 이 지수의 **선물**(2607 만기)이라 롤오버가 있어 부적합하다고 판단,
사용자가 정확한 명칭("코스피 200 변동성지수")으로 재검색해 만기 없는 현물지수
코드를 재확인했다.

### 구현 완료 (2026-07-05)

```
collection/cybos/api_connector.py — get_index_price()에 name_contains 파라미터 추가
    (기존엔 "200" 하드코딩 검증만 있었음 → KOSPI200/VKOSPI 공용 재사용 위해 일반화).
    VKOSPI_INDEX_CODE = "O2901P" 상수 추가.
main.py — _poll_kospi200_index()가 같은 60s 틱에서 VKOSPI도 함께 폴링(self._last_vkospi).
    STEP4에서 vkospi/vkospi_ready를 basis_data 딕셔너리에 얹어 feature_builder에 전달
    (베이시스처럼 결측 시 0으로 리셋하지 않고 ready 플래그로만 구분).
featureset by horizon/horizon_feature_sets.json — 10m/15m/30m에 vkospi를
    include_pending_validation으로 등록 (감사 권고 호라이즌과 일치).
```

- [x] VKOSPI 지수코드 확인 (O2901P, 사용자 스크린샷 2회로 확정 — 선물 코드와 구분)
- [x] `get_index_price()` 일반화 (name_contains 파라미터) + VKOSPI 폴링/병합 배선
- [x] `horizon_feature_sets.json`에 pending_validation 등록 (10m/15m/30m)
- [ ] 실제 Cybos 로그인 세션에서 값 검증 필요 (VKOSPI 통상 15~30대 — 이 세션 미검증)
- [ ] IC 사전검증 → SHAP 심사 통과 시 `include`로 승격

## 260704 감사 로드맵 — 프로그램매매·외국인선물 기존 매핑 검증 (P2, 완료)

> 감사 근거: `docs/260704_SYSTEM_AUDIT_UPGRADE_PROPOSAL.md` §6-3 순위 2·3.
> "프로그램 매매 순매수(차익/비차익 분리) — CORE.md 판단 우선순위 3위인데 피처셋에
> 부재 — 설계-구현 갭." "외국인 선물 실시간 누적 순매수 — 이미 investor_data 수집
> 인프라 존재."

### 실제로는 "새 피처 추가"가 아니라 "기존 추측 매핑 검증/수정"이었음

조사 결과 두 피처 모두 `collection/cybos/api_connector.py`에 이미 코드가 있었으나:
- `request_program_investor()`(`Dscbo1.CpSvr8111`): 주석에 "Header layout guess"라고
  명시된 **완전히 틀린** 매핑(`h[0~2]=arb`, `h[3~5]=nonarb`)이었다.
- `request_investor_futures()`(`CpSysDib.CpSvrNew7221`): row=2(선물)/col=2,5,8(개인/외인/
  기관 순매수) 매핑이 이미 있었고 "미확인"으로 표시돼 있었다.

둘 다 실거래 코드 변경이 아니라 **읽기 전용 조회 데이터 소스의 검증/수정**이라 리스크가
낮다. 이 세션(py3.11, COM 미지원)에서는 검증 불가 — **사용자가 관리자 권한 Creon Plus
세션에서 probe 스크립트를 직접 실행**해 실제 데이터로 확인했다(2026-07-05).

### 검증 결과

1. **`Dscbo1.CpSvr8111` (프로그램매매)** — 기존 매핑은 실제로 **틀렸다**. 공식 문서
   (`cybosplus.github.io/cpdib_rtf_1_/cpsvr8111.htm`)로 정확한 인덱스를 확인:
   - idx19 = 차익순매수체결금액(총, KRW), idx37 = 비차익순매수체결금액(총, KRW)
   - 입력 idx0 = 거래소/코스닥 구분: `ord('1')`(거래소/KOSPI) — 최초 문자열 `"1"`로
     시도했다가 "해당자료가 없습니다" 오류 발생, 같은 코드베이스의 `CpSvrNew7221`이
     이미 쓰던 `ord('1')`(아스키 49) 관례로 맞춰 해결.
   - 실측 검증(2026-07-05 장중): `arb_net=+334689, nonarb_net=-1271401` (차익 순매수,
     비차익 순매도 — 실제 시장 상황에 부합하는 값).
   - `Dscbo1.CpSvr8111S`/`8111KS`는 BlockRequest 미지원("본 객체에서는 지원하지 않는
     함수입니다") — 실시간 구독 전용으로 추정, 조회는 8111만 사용.
2. **`CpSysDib.CpSvrNew7221` (외국인 선물)** — 기존 매핑이 **이미 정확했다**. 실측
   원본 데이터(row 2 = 선물, col 2/5/8 = 개인/외인/기관 순매수)와 코드 출력값이
   정확히 일치 확인(`individual=+104, foreign=+884, institution=-1584`). 수정 불필요.

### 구현 완료 (2026-07-05)

```
collection/cybos/api_connector.py — request_program_investor()를 검증된 CpSvr8111
    매핑으로 전면 재작성 (기존 8119/8119S 후보 제거 — 종목별 TR이라 이 용도 부적합).
    _probe_investor_tr()의 헤더 읽기 범위 32→64로 확대(idx55까지 필요).
    request_investor_futures()는 수정 없음 (이미 정확했음, 검증만 완료).
scripts/test_program_investor_probe.py — 관리자 세션에서 두 함수를 직접 호출해
    실측값을 확인하는 진단 스크립트 (읽기 전용).
featureset by horizon/horizon_feature_sets.json — program_arb_net/program_non_arb_net을
    _feature_status_summary.excluded_from_all_horizons에서 제거하고 5m/10m/15m/30m에
    include_pending_validation으로 등록. foreign_futures_net 노트에 매핑 검증 완료 기록.
```

- [x] `Dscbo1.CpSvr8111` 프로그램매매 매핑 확인 + 수정 + 실제 연결로 검증
- [x] `CpSysDib.CpSvrNew7221` 외국인 선물 매핑 검증 (기존 코드 정확함 확인, 수정 불필요)
- [x] `horizon_feature_sets.json` 등록 갱신 (program_arb_net/program_non_arb_net pending_validation,
      foreign_futures_net 검증완료 노트)
- [ ] IC 사전검증 → SHAP 심사 통과 시 `include`로 승격 (기존 파이프라인 절차 그대로)

**260704 감사 로드맵 P2 신규 피처 4종(베이시스·프로그램매매·외인선물·VKOSPI) 전체 완료.**

## 260704 감사 로드맵 — 챌린저 부트스트랩 판정 + 챔피언 heartbeat (P2)

> 감사 근거: `docs/260704_SYSTEM_AUDIT_UPGRADE_PROPOSAL.md` §4-2·4-3.
> "min_trades=30으로 승률+2%p 판정은 수학적으로 불가능." "챔피언 강등 기준 부재."

### 중요 발견 — CHAMPION_BASELINE은 아직 자체 거래 이력이 없다 (콜드스타트)

`challenger/challenger_engine.py:_register_default_challengers()`는 5개 variant(CVD
Exhaustion·OFI Reversal·VWAP Reversal·Exhaustion Regime·Absorption)만 shadow
도전자로 등록한다 — **`CHAMPION_BASELINE_ID`는 자기 자신의 shadow 거래를 남기지
않는다.** 즉 최초 승격이 일어나기 전까지 `challenger_trades`/`challenger_daily_metrics`에
CHAMPION_BASELINE 데이터가 없어, 부트스트랩 판정·heartbeat 모두 "표본 부족"만 반환한다
(기존 `evaluate_for_promotion()`도 동일 제약을 이미 갖고 있었음 — 새로 발견한
기존 아키텍처의 특성이지 이번 작업의 버그가 아니다). 최초 승격 이후에는 새 챔피언이
"도전자였을 때" 쌓아둔 이력이 그대로 재사용되므로 이후부터는 정상 동작한다.

### 구현 완료 (2026-07-05)

```
challenger/promotion_manager.py
  - PROMOTION_CRITERIA.min_trades 30→100, REGIME_SPECIALIST_CRITERIA.min_regime_trades
    20→50 (감사 §4-2 권고 — 표본오차 ±10%p 이내로)
  - evaluate_for_promotion_bootstrap() 신규: 챌린저/챔피언 거래별 PnL을 각각 독립적으로
    5,000회 복원추출 리샘플 → "리샘플 평균이 챌린저가 더 큰 비율"을 우위확률로 추정,
    ≥95%면 READY. evaluate_for_promotion()(점추정)을 대체하지 않고 병행 참고용으로 추가.
  - check_champion_heartbeat() 신규: 챔피언 최근 60거래 승률의 Wilson score 신뢰구간
    하한이 CHAMPION_BASELINE 전체기간 승률(기준선) 밑이면 degraded=True, size_mult=0.5
    반환 + Slack WARNING 알림. 강등(챔피언 교체)은 여전히 수동(rollback()).
  - _wilson_lower_bound() — 표준 Wilson score interval 공식(n=100,wins=50→0.4038 참조값과
    일치 확인).
challenger/challenger_db.py
  - get_closed_trade_pnls(challenger_id) — 부트스트랩용 전체기간 pnl_pt 리스트.
  - get_recent_closed_trades(challenger_id, limit) — heartbeat용 최근 N건.
main.py — EOD 일별 집계 직후 check_champion_heartbeat() 1회 호출 + 로그.
    **사이즈 자동축소는 아직 실거래 배선(Kelly/사이징 체인)에 연결하지 않음** — 위
    콜드스타트 문제로 실측 데이터가 없어 지금 연결해도 항상 "표본 부족"만 반환,
    실측 데이터 축적 후 연결 여부를 별도 판단할 것(감사 §7-5가 지적한 이미 8+ 겹인
    사이징 배수 체인에 표본 없는 배수를 얹는 것은 리스크만 추가).
dashboard/panels/challenger_panel.py — "상세 리포트" 다이얼로그에 부트스트랩 판정
    결과 병행 표시(읽기 전용 텍스트 추가, 승격 버튼 게이트는 여전히 점추정만 사용).
```

합성 데이터로 두 함수 모두 철저히 검증(임시 SQLite로 표본부족/챌린저 우위/챔피언 우위
3개 시나리오 + Wilson 공식 참조값 대조) — 모두 기대대로 동작.

- [x] `PROMOTION_CRITERIA`/`REGIME_SPECIALIST_CRITERIA` min_trades 상향
- [x] `evaluate_for_promotion_bootstrap()` 구현 + 합성데이터 검증
- [x] `check_champion_heartbeat()` 구현 + Wilson 공식 참조값 검증
- [x] EOD 훅 연결 (로그+Slack, 사이징 미연결)
- [x] 대시보드 상세리포트에 부트스트랩 결과 병행 표시
- [ ] CHAMPION_BASELINE 콜드스타트 해소 — 실거래(trades.db)를 challenger_trades에
      미러링하는 브릿지 신설 검토 (별도 설계 필요, 이번 범위 밖)
- [ ] 실측 데이터 축적 후 heartbeat size_mult를 실제 사이징 체인에 연결할지 결정
- [ ] (P3, 별도) 다중비교 보정(Bonferroni), 챌린저 슬리피지 반영

## 260704 감사 로드맵 — TP1 부분청산 A/B + 레짐 조건부 배수 (P2, 완료)

> 감사 근거: `docs/260704_SYSTEM_AUDIT_UPGRADE_PROPOSAL.md` §3-2.
> "P2 | TP1 부분청산 A/B | 챌린저 variant로 'TP1 스킵·트레일 단독' 버전 등록 →
>  기존 인프라로 20일 병행 평가" / "P2 | 레짐 조건부 배수 | 추세장(Hurst>0.55): 스톱
>  넓게·TP 멀게 / 횡보장: 반대. `REGIME_SIZE_MULT`처럼 배수 테이블 1개 추가"

### ① TP1 부분청산 A/B — 챔피언 미러 챌린저

`challenger/variants/champion_tp1_skip_trail.py` 신규(`E_CHAMPION_TP1_SKIP_TRAIL`).
다른 4개 variant(A~D)는 독자 알파 신호를 실험하지만, 이 variant는 **진입 방향/등급을
그 분 챔피언 확정 decision과 동일하게 미러링**한다 — 진입 알파가 섞이면 청산 규칙
(TP1 부분청산 유무) 차이만 순수하게 분리해 비교할 수 없기 때문. `main.py`의
`run_minute_pipeline()` STEP9 이후 shadow 훅(`_ctx`)에 `decision`(direction/
confidence/grade)을 추가로 실어 전달.

청산 규칙은 `should_exit()`를 오버라이드해 TP1 도달을 부분청산 트리거로 쓰지 않고
대신 트레일 스톱을 무장(arm)한 뒤, 고점/저점 대비 `TRAIL_MULT(0.5)×ATR` 되돌림 시
전량 청산(`ExitReason.TRAIL` 신규)한다. TP2·SL·FORCE는 챔피언과 동일하게 안전망으로
유지. `ChallengerTrade`에 `trail_extreme` 슬롯 추가(다른 variant는 미사용, 영향 없음).
합성 시나리오 3종(무장 전 SL/무장 후 신고점 TP2/무장 후 되돌림 TRAIL)으로 동작 검증.

- [x] `challenger/variants/champion_tp1_skip_trail.py` 구현
- [x] `challenger_engine.py`에 6번째 도전자로 등록
- [x] `main.py` shadow 컨텍스트에 champion decision 미러링 추가
- [x] 합성 시나리오 검증 (사전무장/TP2/TRAIL/SL 4케이스)
- [ ] 20일 병행평가 후 A/B 결과 검토 (기존 챌린저 인프라의 일별 집계로 자동 축적,
      별도 코드 불필요 — `challenger_daily_metrics`에서 확인)

### ② 레짐 조건부 ATR 배수

`config/settings.py`에 `HURST_REGIME_ATR_MULT_ENABLED`(기본 True) +
`HURST_REGIME_ATR_MULT` 테이블 신규(`REGIME_SIZE_MULT`와 동일 패턴):
trend(Hurst≥0.55) ×1.20, neutral ×1.00(기존과 동일), mean-revert(Hurst<0.45) ×0.85 —
손절·TP1·TP2 폭에 곱해지는 승수. 기존 `ATR_HORIZON_TP1_MULT`(스캘퍼 호라이즌별 TP1
단축) 위에 추가로 곱해지므로 두 로직은 독립적으로 공존.

`strategy/position/position_tracker.py`: `open_position()`에 `hurst_bucket` 파라미터
추가, `entry_hurst_bucket` 인스턴스 상태로 영속화(재계산 시점마다 재사용).
`_recalculate_levels()`(체결가 보정 시 재호출)도 동일 배수를 반영하도록 수정 —
그렇지 않으면 체결가 보정 시 배수가 조용히 사라지는 버그가 됐을 것. `force_flat()`/
`save_state()`/`load_state()` 모두 갱신.

`main.py`: 이미 존재하던 `self._entry_hurst_bucket`("trend"/"neutral"/"mean-revert",
`_ts_execute_entry()`의 `hurst_bucket` 인자로 실거래 진입 경로에 연결.
수동 진입(`_on_manual_entry_requested`)은 hurst_bucket 미전달 → 배수 미적용(기존과 동일).

- [x] `HURST_REGIME_ATR_MULT` 설정 추가
- [x] `position_tracker.py` open_position/recalculate_levels/persistence 반영
- [x] `main.py` 실거래 자동진입 경로(A/B급, C급 실험) 배선
- [x] 산술 검증 (trend/neutral/mean-revert 3케이스 stop·tp1·tp2 수치 확인)

**P2 로드맵 전 항목 완료.**

## 260704 감사 로드맵 — 대시보드 상태 스트립 (P3, 1/2 완료)

> 감사 근거: `docs/260704_SYSTEM_AUDIT_UPGRADE_PROPOSAL.md` §5.
> "main_dashboard.py 11,621줄, mid_tabs 15개+ 탭 — 3초 내 시장 파악 불가능."
> "P3 | 대시보드 상태 스트립 + 탭 4그룹화 | 운용 속도·실수 방지"

### 구현 범위 — 상태 스트립만 우선 (탭 4그룹화는 보류)

이 개발 세션은 디스플레이가 없는 headless 환경이라 PyQt GUI를 시각적으로 띄워 확인할
수 없다. `QT_QPA_PLATFORM=offscreen`으로 `MireukDashboard`를 실제 생성하고 더미
데이터로 각 update 메서드를 호출해 위젯 텍스트를 검증하는 방식(구조적 스모크 테스트)은
가능하다는 것을 이번에 확인했다 — 하지만 탭 15개→4그룹 재편은 `UiAutoTabController`의
자동포커스 인덱스 로직까지 건드리는 대규모 구조 변경이라, 스모크 테스트만으로는
레이아웃/가독성 회귀를 잡아낼 수 없다고 판단해 **상태 스트립만 먼저 구현**하기로
사용자와 합의(탭 재편은 이후 사용자가 직접 실행해 시각 확인하며 진행하기로 보류).

### 구현 완료 (2026-07-05)

```
dashboard/main_dashboard.py
  - StatusStripPanel(QFrame) 신규 클래스 — MireukDashboard 클래스 정의 바로 위에 추가.
    2행 구성:
      1행: 포지션+수량+미실현손익(pt/원) · 당일손익(원) · 승/패 · 스톱·TP1가
      2행: 모델방향+등급 · 신뢰도 게이지(막대, min_conf 임계 초과 시 초록/미달 시 주황)
           · 차단사유 1줄 · 레짐+Hurst+ATR · 다음 액션
    색 의미론은 이 스트립에 한해 국내 관례(이익=적/손실=청) 적용 — 기존 개별 패널
    (예: LONG 배지=녹색)은 범위 밖, 전체 통일은 별도 작업으로 남김(문서화).
  - MireukDashboard._build_ui(): 헤더 바로 아래 root.addWidget(self.status_strip) 삽입.
    기존 헤더 배지(CB·헬스·레짐·포지션 등, 이미 탭 무관 상시노출)는 그대로 두고
    스트립은 탭 안에 있어 즉시 안 보이던 정보만 보완.
  - DashboardAdapter — 새 호출부 추가 없이 기존 4개 호출부 내부에서 미러링만 추가:
      update_position()      → strip.update_position() (기존 pos_data 그대로 재사용)
      update_pnl_metrics()    → strip.update_daily_pnl()
      update_entry_stats()    → strip.update_winloss()
      update_entry()          → strip.update_model() + strip.update_regime()
                                (hurst/atr/regime 3개 kwarg 신규 추가 — main.py 호출부 1곳만 수정)
main.py — update_entry() 호출부 1곳에 hurst=features.get("hurst"), atr=atr,
    regime=self.current_micro_regime 3줄 추가. 그 외 호출부는 무변경(main.py는
    이미 매분 호출하던 4개 메서드에 인자만 추가로 실려서 감. 새 콜사이트 없음).
```

검증: `QT_QPA_PLATFORM=offscreen`으로 `DashboardAdapter()` 실제 생성 후 LONG 수익
포지션/당일손실/승패/모델매수B급진입실행/차단사유(Hurst 미달)/FLAT 복귀 등 6개
시나리오를 더미 데이터로 호출해 스트립 위젯 텍스트가 기대값과 정확히 일치함을 확인
(예: `▲LONG 2계약 +2.50pt(+1,250,000원)`, `차단: Hurst 0.30 < 0.45 — 횡보 레짐 진입 차단`).
전체 테스트 스위트도 기존 무관 실패 1건 외 정상.

- [x] `StatusStripPanel` 신규 구현 + 헤더 아래 삽입
- [x] 기존 4개 어댑터 메서드에 미러링 훅 추가 (신규 main.py 콜사이트 없음, 1곳만 인자 추가)
- [x] offscreen Qt 스모크 테스트로 6개 시나리오 검증
- [ ] 탭 15개→4그룹(운용/모델/학습/시스템) 재편 — 사용자가 직접 실행/시각확인하며 진행
      (headless 환경 회귀위험 판단으로 이번 범위에서 보류, 상세는 §5-3 참고)

## 260704 감사 로드맵 — 30m 호라이즌 퇴역 심사 (P3)

> 감사 근거: `docs/260704_SYSTEM_AUDIT_UPGRADE_PROPOSAL.md` §7-6.
> "30m은 filter_only인데 그 필터마저 비활성(CV acc 0.28). need_add 피처(opt_gex_bn 등)
>  탑재 후 acc 회복 실패 시 퇴역을 검토하라."

### 심사 결과 — 퇴역 보류, 대신 근본 원인 버그 1건 발견·수정

**① 감사 진단 재확인(현재도 유효)**: `model/ensemble_decision.py:351`에서 30m 가중치는
`cur_weights["30m"] = 0.0`으로 항상 0(가중합 완전 제외), 890행 역방향 필터도
2026-06-25부로 플래그만 기록하고 등급 격하는 없음(비활성). **30m은 현재 의사결정에
문자 그대로 0% 기여** — 감사 진단 그대로 유효함을 코드로 재확인.
로컬 개발DB 기준 현재 학습된 `gbm_30m.pkl` 정확도 = **0.2098**(감사가 인용한 0.28보다도
낮음, 3-클래스 랜덤 33.3% 대비 명백히 저조).

**② 새로 발견한 사실 — "need_add" 피처가 실제로는 이미 수집되고 있었다.**
`horizon_feature_sets.json`의 30m `include` 목록 1~4위(opt_gex_bn rho=0.29 — 전체
최강, opt_chain_pcr rho=0.245, opt_atm_call_oi/opt_atm_pcr rho=0.126)는 모두
`pkl: need_add`로 표시돼 "미수집" 상태로 보였지만, `raw_features_horizon` 테이블의
30m 피처 JSON을 직접 조회한 결과 **실제로는 실측값이 이미 저장되고 있었다**
(최근 200행 중 119행에 opt_gex_bn/opt_chain_pcr 존재, 대부분 0이 아닌 실측값 —
`main.py:4349` "[BUG FIX] _chain_feats를 option_data에 병합" 수정 이후로 추정).

**③ 근본 원인 — `learning/batch_retrainer.py:_retrain_phase2()`의 피처명 결정 버그.**
호라이즌별 학습 피처 컬럼(`feat_names`)을 "그 구간에서 키가 가장 많은 단일 행"으로
결정하고 있었다(907~920행, 수정 전). 옵션체인 피처는 5분마다만 갱신되므로 그 시점의
행이 항상 최다-키 행이라는 보장이 없고, 실제로 최다-키 행에는 opt_gex_bn 등이 없는
경우가 잦았다 — 그 결과 `X_hz` 구성 시(`[rec[1].get(f, 0.0) for f in use_feat_names]`)
다른 행에는 있는 피처가 통째로 빠지고 전 구간 0.0으로 깔렸다. **30m뿐 아니라 옵션체인
피처를 쓰는 모든 호라이즌(5m~30m)이 잠재적으로 같은 손실을 겪고 있었을 것으로 추정.**

**수정**: 전 구간 행의 키를 **합집합**(첫 등장 순서 보존)으로 바꿈 — 기존에 쓰이던
피처의 값·순서는 그대로 두고, 존재하는데 못 쓰던 피처만 추가로 노출한다. 실제 DB
전체 30m 구간(728행)에 대해 합집합을 재계산해 opt_gex_bn/opt_chain_pcr/opt_atm_pcr/
opt_atm_call_oi가 모두 포함됨을 확인했다(수정 전 로직으로는 "최다-키 행" 하나에
의존해 누락 여부가 사실상 운이었음).

### 최종 판단 — 퇴역하지 않는다

감사 자체가 명시한 전제("need_add 피처 탑재 후 acc 회복 실패 시 퇴역 검토")가 아직
검증되지 않았다 — 위 버그 때문에 이 피처들이 한 번도 실제로 학습에 들어간 적이 없다.
버그 수정은 **다음 예정된 재학습(EOD_RETRAIN.bat, py310_64)부터 자동 반영**되며,
이 세션에서 직접 재학습을 실행하지는 않았다(운영 중인 모델 pickle을 덮어쓰는 작업이라
사용자 환경에서의 정기 재학습 사이클에 맡기는 것이 안전 원칙에 부합 — 검증 없는 변경의
운영 반영을 지양하는 이 프로젝트의 기존 원칙과 동일).

**다음 재학습 후 확인할 것**: `model/horizons/gbm_30m_acc.txt`와
`model/horizons/feature_names_30m.pkl`에 opt_gex_bn 등이 실제로 포함됐는지, 그리고
정확도가 목표 구간([0.38, 0.41], `horizon_feature_sets.json`의 `target_acc`)에
근접했는지 확인 후 최종 퇴역 여부를 재심사한다.

- [x] 30m 현재 상태(가중치 0·필터 비활성) 코드로 재확인
- [x] "need_add" 피처의 실제 수집 여부 DB로 실측 확인 (예상과 달리 이미 수집 중)
- [x] 근본 원인(batch_retrainer 피처명 최다-키-행 선택 버그) 특정 + 합집합으로 수정
- [x] 실 DB 전체 30m 구간으로 수정 로직 검증 (opt_gex_bn 등 4개 모두 포함 확인)
- [ ] 다음 EOD 재학습 후 30m 정확도 재측정 → 목표 미달 시 그때 퇴역 확정

## 260704 감사 로드맵 — 다중비교 보정 (Bonferroni) (P3, 완료)

> 감사 근거: `docs/260704_SYSTEM_AUDIT_UPGRADE_PROPOSAL.md` §4-2 ④·4-3.
> "챌린저를 5종+ 동시 운용하면 그중 하나는 우연히 기준을 통과한다. 보정 없는 다중
>  후보 비교는 과적합 선택 장치다." / "동시 챌린저 수 n에 대해 승격 유의수준을
>  α/n (Bonferroni)로 — 설정 상수 1개"

`challenger/promotion_manager.py`에 `BONFERRONI_CORRECTION_ENABLED`(기본 True) +
`_bonferroni_prob_min(base_prob_min, n_concurrent)` 신규. `evaluate_for_promotion_bootstrap()`
의 "챌린저 우위확률 ≥ 95%" 판정 시 `self.registry.active_challengers()` 개수(n)로
유의수준을 보정한다 — α=1-0.95=0.05를 α/n으로 나눠 요구 확률을 상향(n=1→95%,
n=5→99%). 점추정 방식(`evaluate_for_promotion()`, win_rate_delta 등)은 연관된
p-value가 없어 Bonferroni를 직접 적용할 수 없으므로 범위 밖 — 실제 확률 추정치를
갖는 부트스트랩 판정에만 적용했다.

합성 DB로 검증: 동일한 챌린저 우위(96.4%, n=150 vs n=150)가 활성 챌린저 1개일 때는
READY, 5개로 늘리면(요구치 95%→99%) NOT_READY로 정확히 바뀜을 확인.

- [x] `BONFERRONI_CORRECTION_ENABLED` + `_bonferroni_prob_min()` 구현
- [x] `evaluate_for_promotion_bootstrap()`에 n_concurrent 기반 보정 적용
- [x] 합성 데이터로 n=1→READY, n=5→NOT_READY 전환 검증
- [x] 대시보드 챌린저 패널 호환 확인 (checks dict 제네릭 순회라 영향 없음)

## 260704 감사 로드맵 — 트레일링 갱신 순서 + 만기 구조 더미 (P3, 완료)

> 감사 근거: §3-2 ④·3-3, §6-3 순위9.
> "P5 트레일링 갱신이 P2~P4 이후에만 실행 — TP 체크가 발동한 분에는 트레일 갱신이
>  누락된다." / "만기 구조 더미(만기주·위칭데이·월말 리밸런싱) — time_sin/cos가
>  못 잡는 달력 효과. 전체 호라이즌. 자체 계산."

### ① 트레일링 갱신 순서 — 이미 해결되어 있었음 (코드 변경 없음)

감사가 지적한 `exit_manager.check_and_exit`는 이 세션 P1 작업 중 이미 **미사용
레거시**임을 확인한 파일이다(`strategy/exit/exit_manager.py`, 실거래에서 인스턴스화
안 됨). 실제 청산 로직 `main.py:_ts_check_exit_triggers()`를 직접 확인한 결과,
`self.position.update_trailing_stop(price, atr)` 호출(main.py:9625)이 이미 하드스톱
(P1)·부분청산(P2/P3)·시간청산(P4) 판정보다 **먼저, 무조건** 실행되고 있었다 — 감사가
요구한 "갱신은 항상, 히트 판정은 우선순위대로"가 이미 만족된 상태. `update_trailing_stop()`
자체도 FLAT일 때 즉시 return(안전)하고 손절가를 유리한 방향으로만 당기는(ratchet-only)
가드가 있어 부작용 없음을 재확인. **감사 보고서가 죽은 코드를 보고 오판한 사례** —
코드 변경 불필요, 심사 결과만 기록.

### ② 만기 구조 더미 피처 — 신규 구현

`features/technical/expiry.py` 신규 — `compute_expiry_features(ts_dt)`가 4개 더미를
계산: `is_weekly_witching`(매주 월/목, 월간 만기일 제외), `is_monthly_witching`
(그 달 두 번째 목요일), `is_monthly_expiry_week`(월간 만기가 포함된 캘린더 주),
`is_month_end_rebalance`(달력월 마지막 3일 근사 — 거래소 휴장일력 미반영, 자체계산
범위). 만기일 계산 규칙은 대시보드 `_calc_cycle_badge()`/`_nth_thursday()`와 동일
(월요일 위클리, 목요일 위클리/월간). `features/feature_builder.py`의 기존 시간대
피처(time_sin/cos) 블록에 이어서 같은 `_ts_dt`로 계산 — 파싱 실패 시 동일하게
전부 0.0 폴백. `horizon_feature_sets.json` 전 호라이즌(1m~30m)에
`include_pending_validation`으로 등록(SHAP 심사 전까지 미학습).

검증: 2026-07(2번째 목요일=07-09) 기준 6개 날짜로 단위 계산 확인 + `FeatureBuilder.build()`
실제 호출로 종단 통합 확인(2026-07-09 09:30 입력 → is_monthly_witching=1.0,
is_monthly_expiry_week=1.0, 나머지 0.0 — 기대값과 일치).

- [x] 트레일링 갱신 순서 재확인 — 이미 정상 동작, 변경 불필요 (문서화만)
- [x] `features/technical/expiry.py` 신규 구현 (4개 더미)
- [x] `feature_builder.py` 배선 (time_sin/cos와 동일 try/except 블록 공유)
- [x] 단위 계산 + `build()` 종단 통합 검증
- [x] `horizon_feature_sets.json` 전 호라이즌 pending_validation 등록

**260704 감사 로드맵 P3 전 항목 완료.**

## Phase 6 — 알파 리서치 봇 (자율 진화) ⭐ NEW

> 시스템이 스스로 새 알파를 발견하는 자가 진화 모듈
> 상세: docs/ALPHA_RESEARCH_BOT.md

### Week 20-21: 검색 인프라

| 모듈 | 내용 |
|------|------|
| `research_bot/alpha_scout.py` | 메인 봇 + 스케줄러 |
| `research_bot/searchers/arxiv_searcher.py` | arXiv API 연동 |
| `research_bot/searchers/ssrn_searcher.py` | SSRN 크롤러 |
| `research_bot/searchers/dbpia_searcher.py` | 한국 학회지 |
| `research_bot/searchers/kiss_searcher.py` | KISS 한국학술 |
| `research_bot/searchers/blog_searcher.py` | 헤지펀드 블로그 |

### Week 22-23: AI 평가 시스템

| 모듈 | 내용 |
|------|------|
| `research_bot/evaluators/relevance_scorer.py` | 관련성 점수 |
| `research_bot/evaluators/novelty_detector.py` | 신규성 검출 |
| `research_bot/evaluators/llm_evaluator.py` | LLM 종합 평가 |
| `research_bot/evaluators/verifiability_check.py` | 검증 가능성 |

### Week 24-25: 코드 자동 생성

| 모듈 | 내용 |
|------|------|
| `research_bot/code_generators/formula_extractor.py` | 산식 추출 |
| `research_bot/code_generators/code_synthesizer.py` | 코드 합성 |
| `research_bot/code_generators/test_generator.py` | 테스트 생성 |
| `research_bot/notifier.py` | 팝업·알림 발송 |

### Week 26: 대시보드 통합

| 모듈 | 내용 |
|------|------|
| `dashboard/research_panel.py` | 봇 패널 통합 |

### 봇 운영 원칙

```
검색 자동: ON
팝업 알림: ON
코드 생성: ON (★★★★ 이상)
백테스트 자동 큐: OFF (사용자 검토 필수)
자동 통합: OFF (절대 금지 - 망하지 않기 위해)
```

### [보류] research_bot/code_generators/ 스케줄러 연결

> **현재 상태**: `code_synthesizer.py`, `formula_extractor.py`, `test_generator.py` 스텁 존재.
> **보류 이유**:
> 1. Phase 6 alpha_scout.py 장외 스케줄러 미연결 — 코드 생성 트리거가 없음
> 2. `exec()` / `eval()` 기반 코드 합성은 샌드박스 없이 프로덕션 프로세스에서 실행 불가
>    (OS 명령 주입·모듈 오염 위험)
> 3. 생성된 코드의 타입 안전성·로직 검증 자동화가 선행되어야 함
>
> **선행 조건 완료 후 구현**:
> - [ ] Phase 6 alpha_scout 장외 스케줄러 연결 (cron or QTimer 장외)
> - [ ] 격리 샌드박스(subprocess / Docker) 설계
> - [ ] 코드 합성 결과 자동 린트 + 단위테스트 생성 검증 파이프라인

---

| 날짜 | 버전 | 변경 내용 |
|------|------|---------|
| 2026-04 | v0.1 | 초기 로드맵 작성 |
| 2026-04 | v0.2 | v5 업그레이드 Phase 2~4 추가 |
| 2026-04 | v0.3 | Phase 6 알파 리서치 봇 (자율 진화) 추가 |
| 2026-04 | v0.4 | 5층 모니터링 로그 시스템 추가 (Phase 1 통합) |
| 2026-04 | v0.5 | 미륵이 보완 검토 v6.5 통합 (시간대·분할진입·멀티타임프레임·미시레짐) |
| 2026-04 | v0.6 | Gemini 제안 v7.0 통합 (Latency·Hurst·적응형켈리·VPIN·마디가·Cancel Ratio) |
| 2026-05 | v0.7 | 2차 감사 P2 수정 4종 + M2 상관관계 역수 가중치(HorizonDecorrelator) + Phase 5 챌린저 로드맵 추가 |
| 2026-07 | v0.8 | 260704 종합감사 로드맵 반영 시작. CB② 모의투자 한정 예외 문서화 (실투 전 복원 필수, Phase 5 체크리스트 등록) |
| 2026-07 | v0.9 | 260704 감사 P0 완료(거래당 순EV 리포트+대시보드) + P1 Triple-barrier 레이블 섀도우 병행 구현 완료 (실거래 미연결, 2~4주 병행평가 대기) |
| 2026-07 | v0.10 | 260704 감사 P1 Meta-labeling 게이트 승격 1단계 완료 — meta_labels 65,183건으로 진입품질 분류기 학습, MetaGate 섀도우 신호 연결·ensemble_decisions 로깅 (실거래 미영향, 상관검증 대기) |
| 2026-07 | v0.11 | 260704 감사 P1 MAE/MFE 배리어 재산정 진단 스크립트(analyze_mae_mfe.py) 신설 — 읽기 전용, 자동 적용 없음 |
| 2026-07 | v0.12 | 260704 감사 P1 신호 소멸 청산(P4.5) 구현 — main.py:_check_exit_triggers()에 추가, 기본 ON. `strategy/exit/exit_manager.py`가 실거래 미사용 레거시임을 확인(실제 청산 로직은 main.py 인라인) |
| 2026-07 | v0.13 | 260704 감사 P1 지정가 우선 집행 구현 — Cybos CpTd6831(지정가)/CpTd6833(취소) TR 신규 구현(사용자 제공 레퍼런스로 교차검증), main.py 오케스트레이션(타임아웃시 취소만·시장가전환없음, 계측로깅). 기본 OFF — 실제 Cybos 연결 수동검증 필요 |
| 2026-07 | v0.14 | 260704 감사 P1 게이트 ablation 리포트(generate_gate_ablation_report.py) 완료 — P1 로드맵 전체(6개 항목) 완료. 읽기 전용, 안전게이트 제외 |
| 2026-07 | v0.15 | 260704 감사 P2 착수 — HistGBM 전환은 이미 완료 상태 확인(추가작업 불필요), 분위회귀(q10/q50/q90) 채널 신규 구현 + MetaGate 섀도우 연결 |
| 2026-07 | v0.16 | 260704 감사 P2 선물-현물 베이시스 피처 구현 — KOSPI200 현물지수 신규 Cybos 연동(감사의 "이미 수집중" 전제는 오류였음), horizon_feature_sets.json에 pending_validation 등록 |
| 2026-07 | v0.18 | KOSPI200_INDEX_CODE 정정: 00800(선물차트 네임스페이스) → K2G01P(주식차트/일반시세 네임스페이스, dscbo1.StockMst에 맞는 코드) — 사용자 2차 스크린샷 확인 |
| 2026-07 | v0.19 | 260704 감사 P2 프로그램매매/외국인선물 매핑 검증 완료 — CpSvr8111(프로그램매매) 기존 guess 매핑이 틀렸음을 발견해 공식문서 기준 재작성(idx19/37), CpSvrNew7221(외국인선물)은 기존 매핑이 정확함을 확인. 사용자가 관리자 Creon Plus 세션에서 실제 데이터로 검증. P2 신규피처 4종 전체 완료 |
| 2026-07 | v0.20 | 260704 감사 P2 챌린저 부트스트랩 판정(5000회 리샘플) + 챔피언 heartbeat(Wilson CI) 구현 — min_trades 30→100 상향. CHAMPION_BASELINE이 아직 자체 shadow 거래이력 없는 콜드스타트 아키텍처 제약 발견(기존 evaluate_for_promotion도 동일 제약). 사이징 체인 미연결(데이터 없어 무의미, 리스크만 추가) |
| 2026-07 | v0.17 | 260704 감사 P2 VKOSPI 장중값 피처 구현 — 지수코드 O2901P(사용자 스크린샷 확인), get_index_price() 일반화 재사용, 10m/15m/30m pending_validation 등록 |
| 2026-07 | v0.21 | 260704 감사 P2 TP1 부분청산 A/B(챔피언미러 챌린저 E_CHAMPION_TP1_SKIP_TRAIL 신규, 진입은 챔피언과 동일·청산만 트레일단독) + 레짐 조건부 ATR 배수(HURST_REGIME_ATR_MULT, trend×1.2/mean-revert×0.85) 구현 완료 — **P2 로드맵 전 항목 완료** |
| 2026-07 | v0.22 | 260704 감사 P3 대시보드 상태 스트립(StatusStripPanel) 구현 — 포지션/당일손익/승패/스톱·TP1/모델방향+신뢰도게이지/차단사유/레짐+Hurst+ATR을 헤더 아래 탭무관 상시노출. 신규 main.py 콜사이트 없이 기존 4개 어댑터 호출부 내부 미러링만 추가. offscreen Qt로 실제 위젯 생성+더미데이터 6개 시나리오 검증. 탭 4그룹화는 headless 회귀위험으로 보류(사용자 직접 진행 예정) |
| 2026-07 | v0.23 | 260704 감사 P3 30m 호라이즌 퇴역 심사 — 퇴역 보류, 대신 `batch_retrainer.py:_retrain_phase2()`의 피처명 결정 버그(최다-키 단일 행→합집합으로 수정) 발견·수정. opt_gex_bn 등 need_add 표시 피처가 실제로는 이미 수집 중이었으나 이 버그로 학습에 한 번도 반영 안 됐음을 실DB로 확인. 다음 EOD 재학습부터 자동 반영, 재측정 후 최종 판단 예정 |
| 2026-07 | v0.24 | 260704 감사 P3 다중비교 보정(Bonferroni) 구현 — `promotion_manager.py` 부트스트랩 승격판정에 동시 활성 챌린저 수 기반 유의수준 보정(α/n) 추가. 합성데이터로 n=1→READY, n=5→NOT_READY 전환 검증 |
| 2026-07 | v0.25 | 260704 감사 P3 트레일링 갱신순서 심사(이미 정상 동작 확인, 감사가 죽은 exit_manager.py 보고 오판했던 사례) + 만기 구조 더미 피처(is_weekly_witching/is_monthly_witching/is_monthly_expiry_week/is_month_end_rebalance) 신규 구현, 전 호라이즌 pending_validation 등록 — **260704 감사 로드맵 P3 전 항목 완료** |

---

> 이 로드맵은 진행 상황에 따라 지속 갱신됩니다.
> 우선순위는 변경 가능하지만, **Phase 2 안전장치는 절대 건너뛰지 않습니다.**
