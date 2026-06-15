# Phase D Walk-Forward 검증 결과
> 생성: 2026-06-15 18:25  |  학습기간: 16주  |  CV: 5폴드
> DB: 24726 행 / 118 피처

## 정확도 비교 (공유 97개 vs 호라이즌별 레지스트리)

| 호라이즌 | 공유(N개) | Registry | Δ_Reg | Additive | Δ_Add | 판정 |
|---|---|---|---|---|---|---|
| 10m | 0.4104 (97개) | 0.4073 (13개) | -0.0031 | 0.4104 (99개) | +0.0000 | REGRESS  -0.0031 |
| 15m | 0.3957 (97개) | 0.3909 (17개) | -0.0048 | 0.3957 (99개) | +0.0000 | REGRESS  -0.0048 |
| 30m | 0.3911 (97개) | 0.3538 (14개) | -0.0373 | 0.3911 (100개) | +0.0000 | REGRESS  -0.0373 |

## 호라이즌별 상세

### 10m
- 공유 피처셋 97개 CV: [0.357, 0.4149, 0.5093, 0.3688, 0.4018]
- 레지스트리  13개 CV: [0.3392, 0.4295, 0.5004, 0.3749, 0.3926]
- 가산(Additive) 99개 CV: [0.357, 0.4149, 0.5093, 0.3688, 0.4018]
- DB 가용 신규 피처 (2개): `cvd_monotone_ratio, micro_regime_code`

### 15m
- 공유 피처셋 97개 CV: [0.3591, 0.4048, 0.4489, 0.3691, 0.3965]
- 레지스트리  17개 CV: [0.3815, 0.3647, 0.4397, 0.3861, 0.3824]
- 가산(Additive) 99개 CV: [0.3591, 0.4048, 0.4489, 0.3691, 0.3965]
- DB 가용 신규 피처 (2개): `threshold_feasibility, opt_pcr_extreme_bearish`

### 30m
- 공유 피처셋 97개 CV: [0.3378, 0.372, 0.4426, 0.4079, 0.395]
- 레지스트리  14개 CV: [0.3354, 0.3261, 0.4152, 0.3504, 0.3417]
- 가산(Additive) 100개 CV: [0.3378, 0.372, 0.4426, 0.4079, 0.395]
- DB 가용 신규 피처 (3개): `threshold_feasibility, opt_pcr_extreme_bearish, micro_regime_code`

## 진단 및 수정 전략

### REGRESS 원인 분석
1. **opt 시리즈 미수집**: opt_gex_bn(ρ=0.290), opt_chain_pcr(ρ=0.245) 등 핵심 신호가
   아직 Cybos 옵션 수집 미안정으로 DB에 없음 → registry 피처셋이 빈약해짐
2. **노이즈 피처 제거 효과 < 유용 피처 제거 손실**: registry가 mlofi/microprice 등을
   제거하는데 이들이 현재 GBM에서 사용하는 정보를 담고 있음
3. **학습 샘플 수 감소**: 피처 축소로 GBM 표현력 하락 (N=24726, 5폴드 CV)

### 수정 전략 (Additive 우선)
- **즉시**: 제거 없이 신규 피처 추가 (Additive 전략)
  - bear_reversal_signal, cvd_monotone_ratio, micro_regime_code,
    queue_directional_depletion, threshold_feasibility, opt_pcr_extreme_bearish
  → 이미 DB에 수집 중 → `feature_names.pkl`에 추가 후 retrain
- **opt 수집 안정화 후**: opt_gex_bn / opt_chain_pcr / opt_atm_* DB 축적 확인 후
  registry 기반 strict 피처 선택 재검증

### 다음 액션
- [ ] Additive 전략 적용: 공유 pkl에 6개 신규 피처 추가 후 retrain
- [ ] opt_chain_snapshot 수집 상태 확인 (Cybos 옵션 데이터 흐름)
- [ ] opt 시리즈 수집 안정화 후 Phase D 재검증