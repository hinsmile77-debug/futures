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

→ 위 4가지 모두 충족 시 실전 전환
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

---

> 이 로드맵은 진행 상황에 따라 지속 갱신됩니다.
> 우선순위는 변경 가능하지만, **Phase 2 안전장치는 절대 건너뛰지 않습니다.**
