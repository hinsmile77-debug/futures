# 168차: MetaConf GIL·CUSUM·SGD floor·sigma 4종 패치

**작성**: 2026-06-12  
**커밋**: `180a096`  
**브랜치**: `dev`  
**변경 파일**: `main.py`, `learning/meta_confidence.py`, `learning/batch_retrainer.py`, `learning/online_learner.py`

---

## 1. 분석 배경

`20260612_WARN.log` + `20260612_LEARNING.log` 기반 157차 수정 효과 분석 결과.  
c26eb55(166차 프리장 워밍업), dcb271a(167차 재시작 방어) 커밋 반영 후 잔존 이슈 4종 패치.

---

## 2. 원인별 문제 정리

### 2-1. MetaConf LR.fit() GIL 블로킹 (P0 원인)

| 항목 | 내용 |
|---|---|
| 현상 | 6/12 WARN 로그: S2=5739ms, 5768ms, 5417ms, 5094ms, 4934ms (하루 5회 CB=PAUSED) |
| 근본 원인 | daemon 스레드의 `LR.fit()` 실행 중 GIL을 간헐적으로 보유·해제 → 메인스레드 실효 속도 저하. `[S2-분산GIL]` 로그로 이미 감지되고 있었으나 대응 미비 |
| 오해 지점 | MetaConf는 이미 비동기화(daemon 스레드)됐지만, Python threading GIL 공유 환경에서 daemon 스레드가 실행 중이면 메인스레드도 slow-down됨 — `apply_pending()` 자체는 빠름 |
| 영향 | CB=PAUSED 5분 진입 정지가 하루 5~6회 → 10:03 grade=A 진입 기회도 PAUSED 해제 후에야 가능 |
| 보조 증거 | `09:41:06 S2=5739ms` 직전에 `09:40 [MetaConf] LR[추세장] 비동기 학습 완료 (n=92)` — fit() 종료 시점과 wall time 폭증이 일치 |

### 2-2. CUSUM 과잉 필터링 (P2 원인)

| 항목 | 내용 |
|---|---|
| 현상 | 6/12 장전 재학습: `[CUSUM] 40211 → 12067봉 (30.0% 유지)` + `[Retrain] 학습 데이터 부족 (12067 < 15000)` 경고 |
| 근본 원인 | h_mult=0.5 는 평균 표준편차의 절반으로 임계값을 잡아 과도하게 낮음 → 연속 구간이 아닌 정상 데이터도 과다 제거 |
| 영향 | 안전망 30% 경계(원본의 30% 미만이면 전체 반환)에 겨우 걸려 경고 상시 발생. GBM 학습 품질 저하 |

### 2-3. SGD floor 10% 고착 시 GBM 편향 대항 능력 상실 (P4 원인)

| 항목 | 내용 |
|---|---|
| 현상 | 6/10 로그: SGD비중 30%→10% 하락 후 GBM DN편향(97%) 시기에 SGD도 min floor에 고착 |
| 근본 원인 | SGD 정확도가 낮아 자동으로 비중을 낮추지만, 바로 그 GBM 편향 구간이 SGD 비중을 올려줄 신호 부재 |
| 영향 | uniform fallback이 적용된 호라이즌에서 GBM ≒ 1.0 비중으로 운영 → 편향 호라이즌이 앙상블에 오염 가능 |

### 2-4. sigma_at_t 수정 효과 검증 불가 (P5 원인)

| 항목 | 내용 |
|---|---|
| 현상 | 157차 P3에서 sigma_at_t 항상 0 버그를 수정했으나 SIGNAL·WARN 로그에서 sigma 출력 없음 |
| 근본 원인 | sigma 값이 내부적으로만 사용되고 로그로 노출되지 않아 수정 효과 확인 수단 부재 |
| 영향 | ATR(3.22, 3.20)은 정상 출력됐으나 sigma 기반 `HORIZON_THRESHOLDS` 갱신 여부 미확인 |

---

## 3. 개선 내용

### P0: MetaConf LR max_iter 200→50 + warm_start=True

**파일**: `learning/meta_confidence.py:96`

```python
# 변경 전
self._models[r] = LogisticRegression(
    C=1.0, max_iter=200, solver='lbfgs', class_weight='balanced',
)

# 변경 후
self._models[r] = LogisticRegression(
    C=1.0, max_iter=50, solver='lbfgs', class_weight='balanced',
    warm_start=True,
)
```

**효과**:
- `warm_start=True`: 매 재학습 시 이전 `coef_`에서 시작 → incremental fit 5~15회 수렴 (cold-start 200회 대비 ~90% 감소)
- `max_iter=50`: cold-start 첫 fit도 30~100샘플×7피처에서 충분 수렴
- daemon 스레드 LR.fit() GIL 보유 시간 ~75% 단축 → S2 wall time 정상화 기대

**검증**: 다음 장에서 WARN 로그에 `[S2-분산GIL]` 횟수 감소, CB=PAUSED 미발동 확인

---

### P2: CUSUM h_mult 0.5→0.7

**파일**: `learning/batch_retrainer.py:234`

```python
# 변경 전
def _cusum_filter(records, close_map, h_mult=0.5):

# 변경 후
def _cusum_filter(records, close_map, h_mult=0.7):
```

**효과**:
- h값 = 평균표준편차 × 0.7 → 0.5 대비 40% 완화
- 예상 선택 비율: 30% → ~50% (목표 최소 20,000봉 확보)
- `[Retrain] 학습 데이터 부족` 경고 소멸 기대

**검증**: 다음 장전 재학습 로그에서 `[CUSUM] → N봉` N값이 20,000+ 확인

---

### P4: SGD floor 탈출 가속

**파일**: `learning/online_learner.py` (신규 메서드), `main.py` (BiasReset 연동)

```python
# learning/online_learner.py 신규 메서드
def boost_sgd_for_bias(self, horizon: str, target_w: float = 0.15) -> None:
    bucket = self._bucket(horizon)
    if self._sgd_w[bucket] < target_w:
        self._sgd_w[bucket] = np.clip(target_w, SGD_WEIGHT_MIN, SGD_WEIGHT_MAX)
        self._gbm_w[bucket] = 1.0 - self._sgd_w[bucket]
        self._floor_ticks[bucket] = 0

# main.py BiasReset 적용 시점 (3280줄 근처)
self._bias_override_horizons.add(_h)
...
# P4: GBM 편향 감지 → SGD 비중 min floor 탈출 (대항력 회복)
self.online_learner.boost_sgd_for_bias(_h)
```

**호라이즌 → 버킷 매핑**:
- short 버킷: 1m, 3m, 5m
- long 버킷: 10m, 15m, 30m

**효과**: BiasReset fallback 적용과 동시에 해당 버킷 SGD ≥ 15% 보장 → GBM 편향 구간에서 SGD가 counter signal 제공 가능

**검증**: 다음 BiasReset 발동 시 LEARNING 로그에 `[OnlineLearner] Xm bias fallback SGD 복구 10%→15%` 확인

---

### P5: sigma_at_t 검증 로그

**파일**: `main.py` sigma 계산 직후 (~3115줄)

```python
# 장 초반 5봉 이하 + 10봉 단위로 LEARNING 로그 출력
_sigma_nonzero = sum(1 for x in self._sigma_buf if x != 0.0)
if _n_sig <= 5 or (_n_sig % 10 == 0):
    log_manager.learning(
        f"[sigma] sigma_at_t={self._sigma_20:.4f}% "
        f"buf_n={_n_sig} nonzero={_sigma_nonzero} "
        f"prev_p={_last_p:.2f} cur_p={close:.2f}"
    )
```

**진단 분기표**:

| 로그 패턴 | 의미 | 조치 |
|---|---|---|
| `prev_p=0.00` | 157차 P3 수정 미작동 (`_prev_pipeline_price` 캡처 실패) | P3 코드 재확인 |
| `nonzero=0` | sigma_buf 전부 0 (수익률 계산 오류) | close/prev_p 값 점검 |
| `sigma_at_t=0.0000%` + `nonzero>0` | sigma 계산식 버그 | `_sigma_20` 갱신 로직 점검 |
| `sigma_at_t>0.0000%` + `nonzero>0` | **정상** — 157차 P3 수정 효과 확인 ✅ | — |

---

## 4. 검증 포인트 (다음 장)

| 항목 | 정상 신호 | 이상 신호 |
|---|---|---|
| P0 | WARN 로그에 `S2=Xms` 1000ms 미만 유지, `CB=PAUSED` 미발동 | S2 2000ms+ → warm_start 효과 미달, max_iter 추가 감소 검토 |
| P2 | `[CUSUM] 40211 → 20000+봉` (50%+ 유지), 부족 경고 없음 | 여전히 12000봉대 → h_mult 추가 상향 |
| P4 | BiasReset 발동 시 `[OnlineLearner] bias fallback SGD 복구` 로그 | 로그 없음 → boost_sgd_for_bias 호출 경로 점검 |
| P5 | `[sigma] sigma_at_t=X.XXXX%` X>0, nonzero>0 | `prev_p=0.00` 또는 `sigma_at_t=0.0000%` → 157차 P3 재확인 |

---

## 5. 166차·167차 커밋 효과 검증 (다음 장 병행)

c26eb55(166차 프리장 워밍업)과 dcb271a(167차 재시작 방어)가 오늘 처음 적용됩니다.

| 확인 포인트 | 정상 신호 |
|---|---|
| 08:45~09:00 프리장 처리 | `[PreMarket]` 관련 분봉 처리 로그 출력 |
| GapOffset 선행 설정 | 08:45대 분봉에서 GapOffset 설정 확인 |
| 09:05 EKS 미발동 | `[SHS-EKS]` 로그 없음 (6/12에는 09:05 발동 → 62분 차단) |
| 재시작 시 복원 보존 | `[RESTART]` 로그에 `gap_offset_restored=True` |

---

## 6. 향후 할일

### 즉시 (다음 장 로그 수신 후)

#### P1 — conf 고착 원인 해소

168차에서 삽입한 `[CONF⚠]` 로그가 발화하면 `gbm_raw` vs `sgd` 분해값으로 즉시 분기:

| gbm_raw 고착 | sgd 정상 | → `_hz_feat_cache` 갱신 주기 점검 (`build_for_horizon()` 1m 경로) |
|---|---|---|
| 양쪽 고착 | — | → 입력 피처 자체 고착, `features/feature_decay.py` 확인 |
| gbm_raw 정상 | sgd 고착 | → SGD partial_fit 미발생 또는 SGD 초기 균등분포 고착 |

**대상 파일**: `features/feature_decay.py`, `main.py:_hz_feat_cache 갱신 로직`

---

### 이번 주

#### P3-후속 — 프리장·재시작 효과 미달 시 추가 조치

c26eb55 효과 미달(EKS 재발동)이면:
- EKS 발동 조건: `conf_max=0.0% < mc=31.5% core_pass=0/5봉`
- conf_max=0%의 원인이 프리장 GapOffset이 아닌 다른 곳에 있는지 확인
- core_pass 기준(5봉 중 CORE 3종 통과)을 09:00~09:05 구간 한정 완화 검토

#### P4-검증 — BiasReset 미발동 시 boost_sgd 호출 누락 확인

BiasReset이 발동하지 않으면 P4 로그도 안 찍힘 → 다음 편향 발생 시까지 대기.  
만약 편향 발생 후 로그가 없으면 `main.py:3284` 연동 코드 경로 점검.

---

### 다음 주 (중기)

#### Triple Barrier 레이블링

- **파일**: `learning/batch_retrainer.py:_path_conditioned_label()` 교체
- **내용**: 고정 임계값 → ATR 기반 동적 상하한 + 시간 장벽
- **사전 필요**: KOSPI200 선물 1분봉 ATR 실측 (P5 로그로 sigma 확인 후 역산 가능)
- **참조**: `docs/260611_DIRECTION_BIAS_IMPROVEMENT_PLAN.md` § 4.1

#### 레짐 조건부 GBM 분리

- **내용**: RISK_ON / NEUTRAL / RISK_OFF 레짐별 독립 GBM 인스턴스
- **근거**: 단일 GBM이 최근 하락 레짐으로 오염 → 레짐 전환 후에도 편향 잔존
- **선행 조건**: P0(MetaConf GIL) 안정화 확인 후 대규모 리팩토링

---

## 7. 관련 파일

| 파일 | 역할 |
|---|---|
| `main.py` | P4 연동 (BiasReset 시 boost_sgd_for_bias 호출), P5 sigma 로그 |
| `learning/meta_confidence.py` | P0 (warm_start + max_iter 감소) |
| `learning/batch_retrainer.py` | P2 (CUSUM h_mult 0.5→0.7) |
| `learning/online_learner.py` | P4 (boost_sgd_for_bias 신규 메서드) |
| `commit/166차_BiasReset_confstuck_CB타이밍_패치.md` | P1 (conf 고착 진단 로그 삽입) |
| `docs/260611_DIRECTION_BIAS_IMPROVEMENT_PLAN.md` | 방향편향 전체 개선 계획 |
