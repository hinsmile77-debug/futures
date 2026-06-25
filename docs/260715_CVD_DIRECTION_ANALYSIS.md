# cvd_direction 일방향 고착 원인 분석 및 개선 계획

> 작성일: 2026-06-25 (250차 세션)
> 분석 트리거: EOD 재학습 로그 `[ScalerRefresh] CORE 'cvd_direction' raw_std≈0(0.0490) → identity(0,1) 강제`
> 단기 개선(1번): 2026-06-25 구현 완료

---

## 1. 현상 확인

EOD P8 스케일러 재적합 시 6개 전 호라이즌에서 동일 경고 발생:

```
[ScalerRefresh] 1m CORE 'cvd_direction' raw_std≈0(0.0490) → identity(0,1) 강제
[ScalerRefresh] 3m CORE 'cvd_direction' raw_std≈0(0.0490) → identity(0,1) 강제
... (15m·30m 동일)
```

처음에는 "강한 일방향 장" 현상으로 추정했으나, 10거래일 DB 실측 결과 **오랫동안 지속되는 구조적 결함**임을 확인.

### 실측 분포 (2026-06-10 ~ 2026-06-25, 총 12거래일)

| 날짜 | n | `cvd_direction` std | 음수(-0.5) 비율 | `cvd_delta_norm` std | 음수 비율 |
|---|---|---|---|---|---|
| 2026-06-10 | 378 | 0.0763 | **0.0%** | 0.6270 | 53.7% |
| 2026-06-11 | 366 | 0.0581 | **0.0%** | 0.6639 | 46.7% |
| 2026-06-12 | 364 | 0.0857 | **0.0%** | 0.6083 | 48.9% |
| 2026-06-15 | 340 | 0.0383 | **0.0%** | 0.6137 | 45.3% |
| 2026-06-16 | 359 | 0.1033 | **0.0%** | 0.6111 | 48.5% |
| 2026-06-17 | 368 | 0.0634 | **0.0%** | 0.5918 | 43.5% |
| 2026-06-18 | 301 | 0.1455 | **0.0%** | 0.6173 | 44.9% |
| 2026-06-19 | 368 | 0.0730 | **0.0%** | 0.6464 | 47.0% |
| 2026-06-22 | 347 | 0.0653 | **0.0%** | 0.6166 | 44.7% |
| 2026-06-23 | 339 | 0.0712 | **0.0%** | 0.6163 | 55.5% |
| 2026-06-24 | 313 | 0.0399 | **0.0%** | 0.6404 | 47.6% |
| 2026-06-25 | 369 | 0.0518 | **0.0%** | 0.6285 | 45.8% |

**`cvd_direction = -0.5` 값이 12거래일 동안 단 한 번도 나타나지 않음.**
`cvd_delta_norm`은 동기간 std 0.59~0.66, 음수 비율 43~55%로 정상 양방향 분포.

---

## 2. 원인 분석: 3중 복합 고장

```
[Layer 1] Cybos buy_vol 시스템적 편향
         ↓
[Layer 2] cumulative_cvd 단조증가
         ↓
[Layer 3] cvd_norm=1.0 고착 + cvd_direction=+0.5 고착
```

### Layer 1 — Cybos buy_vol 시스템적 편향 (데이터 레이어)

`raw_candles`에 `buy_vol`·`sell_vol` 컬럼이 존재하며 NULL 없이 100% 채워져 있으나,
실측 결과 **시장 방향과 무관하게 buy_vol이 항상 sell_vol을 초과**:

```
2026-06-25 09:00~09:09 (시장 -14pt 하락 구간):
  09:00  C=1463.86 mid=1464.28 C<mid(하락봉)  buy=508  sell=371  delta=+137
  09:01  C=1459.28 mid=1460.83 C<mid(하락봉)  buy=518  sell=416  delta=+102
  09:05  C=1454.38 mid=1456.03 C<mid(하락봉)  buy=706  sell=452  delta=+254
  09:08  C=1450.26 mid=1451.07 C<mid(하락봉)  buy=1051 sell=512  delta=+539
```

오늘(2026-06-25) 전체 통계:
- 전체 353봉 중 buy_vol > sell_vol: **348봉 = 98.6%**
- 하락봉(close < mid) 164봉 중 buy_vol > sell_vol: **159봉 = 97.0%**

**Cybos Plus의 "매수체결량"이 표준적인 체결방향(buyer-initiated vs seller-initiated) 분류와
다른 기준을 사용하는 것으로 추정.** 정확한 정의는 Cybos Plus 문서 확인 필요.

### Layer 2 — cumulative_cvd 단조증가 (누적 레이어)

`features/technical/cvd.py:70` — `update_from_bar()`:
```python
delta = buy_vol - sell_vol   # Cybos 편향으로 항상 양수
self._cumulative_cvd += delta # 세션 내내 단조증가
```

- 매봉 delta > 0 → `_cumulative_cvd`가 세션 내내 단조증가
- 세션 간 이월: 어제 15:08 `cvd=1.0` → 오늘 09:00 `cvd=1.0` (reset_daily 후에도 즉시 복원)

### Layer 3 — 정규화 수식 붕괴 (계산 레이어)

`features/technical/cvd.py:103`:
```python
cvd_abs_max = max(abs(v) for v in cvds) or 1.0  # 단조증가 시 항상 최신값
cvd_norm    = cumulative_cvd / cvd_abs_max       # = 1.0 (분자=분모)
cvd_slope   = cvds[-1] - cvds[0]                 # 항상 > 0 (단조증가)
direction   = 1 if cvd_slope > 0 else ...        # 항상 1
```

단조증가 수열에서 `max(window) = window[-1] = _cumulative_cvd` → 비율 항상 1.0.

### 결과적 영향

- **`cvd_direction`: 97~99% 구간 +0.5 고착** — 사실상 상수 피처
- **`cvd_norm` (a.k.a. `cvd`): 항상 1.0** — 동일 문제
- GBM 26주 학습 데이터에서 cvd_direction ≈ 상수 → GBM 트리 분기 기여도 0
- CORE 면제(AutoMask exempt) + ScalerRefresh identity 보호가 **망가진 신호를 보호**하는 역설
- identity 스케일러로 인한 분포 불일치: 학습 스케일러(26주 정상 분포) vs 추론 스케일러(단일 장, std≈0)

---

## 3. 대체 피처: cvd_delta_norm

`features/feature_builder.py:559`:
```python
_rng_hilo = max(high - low, 1e-9)
_bull_v   = vol * max(close - low,  0.0) / _rng_hilo   # Williams 매수비중
_bear_v   = vol * max(high - close, 0.0) / _rng_hilo   # Williams 매도비중
features["cvd_delta_norm"] = (_bull_v - _bear_v) / (vol + 1e-9)
# = (2×close − high − low) / (high − low)   →  [-1, +1]
```

- **Cybos buy_vol 미사용** → 편향 없음
- **종가 위치 기반**: 종가가 바 상단 → 양수(매수압), 하단 → 음수(매도압)
- **이미 feature_names.pkl(97개) 포함** → 재학습 없이 즉시 교체 가능
- 12거래일 실측: std 0.59~0.66, 음수 43~55% (**정상 양방향 분포**)

---

## 4. 개선 계획

### 단기: CORE 피처 교체 — **2026-06-25 구현 완료**

**변경 파일**: `config/settings.py`, `model/multi_horizon_model.py`,
`strategy/entry/checklist.py`, `main.py`

#### 변경 내용

| 항목 | 변경 전 | 변경 후 |
|---|---|---|
| `CORE_FEATURES_BY_GROUP["short"]["cvd"]` | `"cvd_direction"` | `"cvd_delta_norm"` |
| `CORE_MASK_EXEMPT_BY_GROUP["short"]` | `{"cvd_direction", "cvd", "cvd_divergence", ...}` | `{"cvd_delta_norm", "cvd_divergence", ...}` |
| `MultiHorizonModel._CORE_MASK_EXEMPT` | `"cvd_direction"`, `"cvd"` 포함 | 제거, `"cvd_delta_norm"` 추가 |
| 체크리스트 4번 입력값 (단기 그룹) | `_dir_sign(features["cvd_direction"])` → `int` | `float(features["cvd_delta_norm"])` → `float` |
| 체크리스트 평가 로직 | `cvd_direction > 0` (항상 True) | `cvd_delta_norm > 0` (실질 평가) |

#### 즉시 효과

- AutoMask: `cvd_delta_norm` 극단 z는 보호 (강한 방향 신호), `cvd_direction`·`cvd`는 보호 해제
- ScalerRefresh CORE 보호: `cvd_direction` identity 강제 → 해제 (D_FORCE 정상 작동)
- 체크리스트 4번: 하락봉에서 `cvd_delta_norm < 0` → SHORT 정상 평가
- **재학습 불필요**: `cvd_delta_norm`은 이미 pkl 97개 포함

#### 남은 문제

- `cvd_direction`·`cvd_norm`은 pkl에 여전히 존재 → GBM이 상수 피처로 계속 학습
- Cybos buy_vol 편향 자체는 해소되지 않음 (CVDCalculator 내부)
- cumulative CVD 누적 방식 변경 없음

---

### 중기: CVDCalculator 누적 방식 재설계 — **2026-07-14 이후**

*전제: Phase D 재검증(opt_gex_bn·opt_chain_pcr 4,000행 달성) 이후 재학습 시점에 함께 적용*

#### 방안 A — delta-of-cumulative 방식 (권장)

`features/technical/cvd.py` `compute()` 내 cvd_slope 계산 교체:

```python
# 현재: 누적값 10봉 slope → 단조증가 시 항상 양수
cvd_slope = cvds[-1] - cvds[0]

# 개선: 봉별 delta의 rolling 합산 (상대적 방향)
bar_deltas = [cvds[i] - cvds[i-1] for i in range(1, len(cvds))]
cvd_slope  = sum(bar_deltas[-5:])   # 최근 5봉 delta 합
# → 매봉 buy_vol 편향이 있어도 "직전 봉 대비 더 많이 샀나"를 비교 → 상대적 방향 회복
```

`cvd_norm` 정규화도 수정:
```python
# 현재: cumulative / max(window) → 항상 1.0
cvd_abs_max = max(abs(v) for v in cvds) or 1.0
cvd_norm    = cumulative_cvd / cvd_abs_max

# 개선: 세션 내 detrended CVD 사용
_rolling_mean = sum(cvds) / len(cvds)
_centered_cvds = [v - _rolling_mean for v in cvds]
cvd_abs_max   = max(abs(v) for v in _centered_cvds) or 1.0
cvd_norm      = (self._cumulative_cvd - _rolling_mean) / cvd_abs_max
```

#### 방안 B — cvd_direction 재정의 (대안)

Cybos buy_vol 없이 price-action으로 완전 재정의:
```python
# feature_builder.py 내 cvd_direction 계산 교체
features["cvd_direction"] = float(np.sign(features["cvd_delta_norm"])) * 0.5
# -1/0/+1 이산값이지만 cvd_delta_norm 기반 → Cybos 편향 없음
```

#### 적용 조건

- EOD 재학습(full_cv=True) 직전에 코드 적용 → 26주 데이터 기반 재학습으로 수정 효과 반영
- 학습 후 cvd_direction의 음수 비율이 30% 이상인지 로그 확인
- SHAP 피처 중요도에서 cvd_direction 기여도 상승 여부 확인

---

### 장기: Cybos buy_vol 데이터 실증 조사 — **2026-08-01 이후**

*전제: Phase 5(실전 전환) 진입 전 데이터 레이어 신뢰성 확보*

#### 조사 항목

1. **Cybos Plus API 문서 확인**: `선물분차트` TR의 `매수체결량`·`매도체결량` 정의
   - 체결방향(aggressive buyer vs. seller) 기반인가?
   - 단순 호가 상의 buy/sell 집계인가?
   - 다른 TR에서 올바른 체결방향 데이터를 제공하는가?

2. **Cybos 편향 정량화**: 음수 delta 비율 변화 추이 모니터링
   - 현재(2026-06-25): delta > 0 비율 98.6%
   - 기대값(올바른 분류): 50% 수준

3. **올바른 경로 선택**:
   - Cybos가 올바른 체결방향 데이터를 제공하면 → `update_from_bar()`에서 해당 필드 사용
   - 제공하지 않으면 → **`cvd_delta_norm` (price-action 기반)을 공식 CVD 방향 피처로 확정**,
     `cvd_direction`·`cvd` 피처를 pkl에서 제거하고 feature_builder 단순화

#### 데이터 검증 쿼리

```sql
-- 날짜별 delta 음수 비율 모니터링
SELECT
    substr(ts,1,10) AS date,
    COUNT(*) AS n,
    SUM(CASE WHEN buy_vol > sell_vol THEN 1 ELSE 0 END) AS buy_gt_sell,
    ROUND(AVG(CASE WHEN buy_vol > sell_vol THEN 1.0 ELSE 0.0 END)*100, 1) AS buy_gt_pct
FROM raw_candles
WHERE ts >= '2026-07-01'
GROUP BY 1
ORDER BY 1;
```

---

## 5. 타임라인 요약

| 시점 | 작업 | 상태 |
|---|---|---|
| **2026-06-25** | CORE 피처 교체 (`cvd_direction` → `cvd_delta_norm`) | ✅ 완료 |
| **2026-06-25** | 체크리스트 4번 입력 교체 (`cvd_delta_norm` 사용) | ✅ 완료 |
| **2026-07-14 이후** | CVDCalculator delta-of-cumulative 방식 전환 (Phase D 재검증 시 함께) | ⏳ 예정 |
| **2026-07-14 이후** | cvd_direction·cvd 피처 pkl 제거 검토 (재학습 후 SHAP 확인 후 결정) | ⏳ 조건부 |
| **2026-08-01 이후** | Cybos buy_vol 실제 정의 조사 + 데이터 레이어 근본 수정 | ⏳ 예정 |

---

## 6. 재활성화(중기) 체크리스트

중기 작업(CVDCalculator 재설계) 완료 후 검증 항목:

- [ ] `cvd_direction` 음수 비율 ≥ 30% (12거래일 실측)
- [ ] `cvd_norm` (`cvd`) 값이 0~1 범위 내 분산 (1.0 고착 해소)
- [ ] SHAP 피처 중요도에서 `cvd_direction` 기여도 유의미 (현재 0에 가까움)
- [ ] 스케일러 raw_std ≥ 0.05 (identity 강제 미발동)
- [ ] EOD 재학습 후 체크리스트 4번 통과율 30~70% (현재: 거의 100% 통과 — 상수여서)

---

## 7. 관련 파일

| 파일 | 역할 |
|---|---|
| `features/technical/cvd.py` | CVDCalculator — 중기 수정 대상 |
| `features/feature_builder.py` | `cvd_delta_norm` 계산 (Williams A/D 기반) |
| `config/settings.py` | `CORE_FEATURES_BY_GROUP`, `CORE_MASK_EXEMPT_BY_GROUP` |
| `model/multi_horizon_model.py` | `_CORE_MASK_EXEMPT` frozenset |
| `strategy/entry/checklist.py` | 체크리스트 4번 단기 그룹 CVD 평가 |
| `main.py` | 체크리스트 호출 시 `cvd_delta_norm` 전달 |
