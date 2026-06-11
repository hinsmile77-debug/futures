# 방향 편향 근본 개선 Implementation Plan

**작성**: 2026-06-11  
**배경**: 6/11 장 분석에서 확인된 3m DN=68%/UP=2%, 5m DN=72%/UP=8% 고착 문제 근본 해결  
**관련 커밋**: 165차 (88cf7fd)

---

## 1. 근본 원인 진단

방향 편향은 단일 원인이 아닌 3층 중첩 구조다.

```
Layer 1: 데이터 드리프트
  최근 하락장 레이블이 26주 훈련셋 후반부를 지배
  → 동일 weight로 학습 시 DOWN 패턴 과잉 학습

Layer 2: 레이블 중첩 (Overlapping Labels)
  t=09:01 3m 레이블과 t=09:02 3m 레이블이 2분 겹침
  → GBM이 동일 하락 패턴을 반복·중복 학습
  → 하락 구간에서 DOWN 신호 밀도 인위 증폭

Layer 3: 레짐 미분리
  상승장·하락장·횡보장을 단일 GBM으로 혼합 학습
  → 최근 DOWN 레짐 패턴이 전체 모델을 오염
  → 시장 전환 후에도 이전 레짐의 편향 잔존
```

---

## 2. 학술·금융 실전 근거 요약

| 방법론 | 출처 | 실증 효과 |
|---|---|---|
| Dynamic Class Weight + Time Decay | EWMM(arXiv 2404.08136), IEEE Dynamically Weighted Balanced Loss(2021) | 클래스 불균형 >3:1 환경에서 F1 +15~25% |
| CUSUM Filter (이벤트 기반 샘플링) | Lopez de Prado, AFML 2018, 5장 | 정보 밀도 향상, KOSPI 관련 arXiv 2504.02249에서 정확도 +5~12% 확인 |
| Triple Barrier Labeling | Lopez de Prado, AFML 2018, 3장 | 변동성 환경별 레이블 분포 자연 균형화 |
| Sample Uniqueness Weighting | AFML 2018, 4장 | 중복 레이블 문제 정량화·제거 |
| Regime-Conditional Modeling | arXiv 2402.05272 (S&P500/DAX/Nikkei) | MDD 26~39% 감소, 레짐 전환 시 편향 재발 근절 |
| Meta-Labeling | Lopez de Prado 2017 (Guggenheim) | Precision +30~50%, 진입 품질 분리 |
| Focal Loss | Lin et al., 2017 (RetinaNet) | 쉬운 샘플 억제, 어려운 샘플 집중 학습 |
| Purged K-Fold CV | AFML 2018, 7장 | 룩어헤드 바이어스 제거, 검증 신뢰도 향상 |
| Time-Decayed Sample Weighting | 업계 표준 (Two Sigma, AQR 방식) | 오래된 레짐 영향 지수적 감쇠 |

---

## 3. 구현 완료

### 3.1 165차 (2026-06-11, 커밋 88cf7fd)

#### P0: 동적 역빈도 + 시간감쇠 Class Weight

**파일**: `learning/batch_retrainer.py`, `model/multi_horizon_model.py`  
**함수**: `_make_sample_weight(y, horizon_key)`

```
이전: 정적 _CW_3M = {FL:0.75, UP:1.35, DN:0.90} — 오늘의 시장 변화 무관
이후: 재학습 시마다 최근 N봉 분포 자동 반영
      halflife=100봉 지수감쇠 → 오래된 하락장 영향 감쇠
      역빈도 가중치 → DOWN 과다면 DN 자동 하향, UP 자동 상향
      클리핑 중간값×3 → 한 클래스 극단 희소 시 역보정 폭발 방지
      호라이즌별 FLAT 상한 유지 (FL 고착 방지)
```

**검증**: DOWN 70% 편향 데이터 → UP=1.873, DN=0.534 (자동 역보정 확인)

**파라미터**:
```python
_DYN_HALFLIFE   = 100   # 반감기 봉 수 (≈100분)
_DYN_CLIP_RATIO = 3.0   # 최대 가중치 = 중간값 × 배율
_FLAT_CAP = {"1m": 0.85, "3m": 0.75, "5m": 0.85, "10m": 0.80, "15m": 0.75, "30m": 0.70}
```

---

#### P1: CUSUM 이벤트 필터

**파일**: `learning/batch_retrainer.py`  
**함수**: `_cusum_filter(records, close_map, h_mult=0.5)`  
**삽입 위치**: `_load_from_db` (MAX_TRAIN_BARS 처리 후), `_retrain_phase2` (records 빌드 후)

```
이전: 모든 1분봉을 균등하게 학습 → 연속 하락 구간 반복 학습
이후: CUSUM 누적통계 > 동적 임계값인 시점만 선택
      → 연속 하락/상승 구간에서 이벤트 수 자동 감소
      → UP 이벤트와 DN 이벤트 발생 횟수 균형화
```

**안전망**: 필터 후 샘플이 원본 30% 미만이면 전체 사용

**검증**: 연속하락 60봉 → 19봉 선택 (31.7%), 횡보 60봉 → 47봉 (과잉 필터 없음)

---

#### P3: MetaGate 방향 편향 감지

**파일**: `strategy/entry/meta_gate.py`  
**메서드**: `_bias_penalty(direction)`, `_direction_buf = deque(maxlen=30)`

```
이전: MetaGate는 신호 강도만 보고 편향 여부 인식 불가
이후: 최근 30 evaluate() 호출의 방향 기록
      동일 방향 비율 >70% 시 blended_conf 패널티 (최대 0.05)
      70%→0.02, 100%→0.05 선형 스케일
```

**설계 의도**: 모델이 지속적으로 한 방향만 예측할 때 MetaGate 단계에서 자동 감지·경감. 진입을 완전 차단하지 않고 소폭 하향하여 정상 추세는 유지.

---

## 4. 구현 예정

### 4.1 P1-B: Triple Barrier 레이블링 (이번 주 중)

**파일**: `learning/batch_retrainer.py`  
**대상 함수**: `_path_conditioned_label()` 교체 또는 병행

**사전 필요 작업** (지금 당장 구현 불가한 이유):
- `HORIZON_THRESHOLDS["1m"] = 0.0003` (0.03%) — 현재 고정 임계값
- KOSPI200 선물 1분봉 ATR은 약 0.10~0.25% 추정 (실측 필요)
- ATR 배율 잘못 설정 시 전체 레이블 분포 급변 위험

**필요 선행 작업**:
```
① 실제 장 데이터에서 1분봉 ATR_20 분포 측정
② tp_mult = 현재_threshold / ATR_median 역산
③ 소량 백테스트로 레이블 분포 검증 (FLAT 비율 30~40% 목표)
```

**구현 계획**:
```python
def _triple_barrier_label(close_map, ts, h_min, atr_20, tp_mult=1.0, sl_mult=1.0):
    """
    ATR 비례 Triple Barrier:
    익절선 = c0 + ATR × tp_mult
    손절선 = c0 - ATR × sl_mult
    시간선 = h_min 봉 후
    → 세 장벽 중 먼저 도달하는 방향으로 레이블
    """
```

---

### 4.2 P2: Regime-Conditional GBM 분리 (다음 주)

**파일**: `learning/batch_retrainer.py`, `model/multi_horizon_model.py`, `main.py`

**아키텍처**:
```
현재: GBM_1개 × 모든 레짐 데이터 혼합
       → 하락장 데이터가 최근 우세하면 DOWN 편향 전이

목표: GBM_레짐별 × 호라이즌별 (soft blending)
       GBM[RISK_ON][3m], GBM[NEUTRAL][3m], GBM[RISK_OFF][3m]
       ...

예측: regime_proba로 soft blend
  final = w[RISK_ON]*gbm_on.predict() + w[NEUTRAL]*gbm_neutral.predict() + w[RISK_OFF]*gbm_off.predict()
```

**사전 필요 확인**:
- [ ] `raw_features` JSON에 regime 필드 존재 여부 확인
- [ ] 레짐별 샘플 수 확인 (최소 5,000봉 per regime 필요)
- [ ] model 파일 구조 변경 계획 (gbm_3m.pkl → gbm_RISK_ON_3m.pkl 등)

**구현 단계**:
```
Step 1: _load_from_db에서 regime 컬럼 추출
Step 2: _train_horizon에 regime 파라미터 추가
Step 3: 레짐별 모델 저장/로드 (경로 변경)
Step 4: multi_horizon_model.predict_proba에 soft blending 추가
Step 5: main.py에서 current_regime → regime_proba 변환 전달
```

---

### 4.3 P4: Sample Uniqueness Weighting (장기)

**개념**: 중복 레이블(overlapping labels) 문제 정량화
- 각 샘플이 몇 개의 다른 샘플과 레이블을 공유하는지 계산
- 공유 비율이 높을수록 학습 가중치 감소

**AFML 구현 참고**:
```python
def get_uniqueness(close_times, molecule):
    # 각 관측치의 레이블 유효 구간과 다른 관측치와의 겹침 비율
    # uniqueness = 1 / (겹치는 레이블 수)
    # sample_weight = 겹침이 적은 샘플 우선
```

**우선순위**: P2 완료 후 검토

---

## 5. 검증 기준

### 5.1 P0+P1+P3 (165차) 효과 검증 — 6/12 장 후 확인

| 항목 | 6/11 기준 | 6/12 목표 | 측정 방법 |
|---|---|---|---|
| 3m/5m DN 비율 | 68~72% | 30~50% | predictions.db WHERE horizon='3m' |
| UP 예측 건수 | 2~8% | 30% 이상 | 호라이즌별 방향 분포 |
| CUSUM 필터율 | N/A | 40~70% 유지 | [CUSUM] 로그 |
| P3 편향패널티 발동 | N/A | 12시 이후 발동 확인 | [MetaGate] 편향패널티 로그 |
| 재학습 시 동적 가중치 | 고정값 | UP/DN 비율이 장 상황에 따라 변화 | [Retrain] 동적가중치 로그 |

### 5.2 Triple Barrier (P1-B) 완료 기준
- [ ] FLAT 비율 25~40% 유지 (현재 고정임계값 기준과 유사한 수준)
- [ ] UP/DN 비율 균등화 (각 30~40%)
- [ ] 5일 장 데이터 검증 후 배포

### 5.3 Regime GBM (P2) 완료 기준
- [ ] 레짐별 샘플 수 각 5,000봉 이상
- [ ] 레짐 전환 시 방향 분포 안정적 유지
- [ ] Walk-Forward 검증: Sharpe 개선 또는 동등 유지

---

## 6. 우선순위 및 일정

```
2026-06-11 (완료) ── 165차
  ✅ P0: 동적 class weight + 시간감쇠
  ✅ P1: CUSUM 이벤트 필터
  ✅ P3: MetaGate 편향 감지 패널티

2026-06-12 ── 효과 검증
  → 6/12 장 데이터로 DN 비율, CUSUM 필터율, P3 패널티 발동 확인
  → 이상점 발견 시 파라미터 미세조정 (halflife, h_mult, bias 임계값)

2026-06-중순 ── P1-B: Triple Barrier
  사전 조건: ATR 실측 → tp_mult 역산 → 소량 검증
  예상 소요: 2~4시간 구현 + 1일 검증

2026-06-하순 ── P2: Regime-Conditional GBM
  사전 조건: raw_features regime 컬럼 확인 + 레짐별 샘플 수 확인
  예상 소요: 4~6시간 구현 + 3일 검증
```

---

## 7. 구현 원칙

1. **단계적 검증**: 각 변경 후 최소 1장 운영 데이터로 효과 확인 후 다음 단계
2. **안전망 의무화**: 모든 필터/가중치 변경에 fallback 조건 포함
3. **로그 의무화**: 파라미터 값 DEBUG 레벨 이상으로 기록 (효과 추적 가능하게)
4. **배치 재학습 우선**: P0/P1은 재학습 시 적용 — 즉시 효과는 다음 재학습 사이클부터
5. **Triple Barrier 조건**: ATR 실측 없이 tp_mult 추정으로 배포 금지

---

## 8. 관련 파일 변경 이력

| 커밋 | 내용 |
|---|---|
| 164차 (f03bfff) | 6/11 분석 5종 수정: cold-start floor 0.45, toxicity spread 8.0, sigma_at_t 버그 수정, calibration window 100, class weight UP 강화 |
| 165차 (88cf7fd) | 방향편향 근본개선 3종: P0+P1+P3 |

## 9. 참고 코드 스니펫

### 동적 가중치 동작 원리

```python
# DOWN 70% 편향 → 역빈도 계산 예시
# 입력: y에 DN=70%, UP=15%, FL=15%
# decay 적용 후 weighted_counts:
#   DN: 약 0.45 (70%이지만 오래된 데이터 감쇠)
#   UP: 약 0.10
#   FL: 약 0.10
# total = 0.65
# inv_freq: DN=0.65/(3×0.45)=0.48, UP=0.65/(3×0.10)=2.17, FL=2.17
# 클리핑 후(중간값=0.48, max_w=1.44): UP=1.44, FL=0.75(cap), DN=0.48
# 결과: UP 가중치가 DN의 3배 → 모델이 UP 예측에 더 집중
```

### CUSUM 동작 원리

```python
# 연속 하락 구간 (10봉씩 0.1포인트 하락):
# s_neg가 계속 누적 → h 임계값 도달마다 이벤트 발생
# 결과: 60봉 하락 구간에서 6~10개 이벤트만 선택
#       (반복 학습 패턴 제거, 정보 밀도 증가)
```
