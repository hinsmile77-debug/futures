# 세션 이력 — futures (미륵이)

> 최신 순 정렬.

---

## 2026-07-02 (275차 — conf/mc 통과율 0 딥다이브 + 진단 스크립트 버그 2종 수정)

**트리거**: 사용자 보고 "금일 conf 평균이 mc 기준보다 낮아 통과율이 거의 0이다" — 딥다이브 후
"상큼한 개선제안" 요청.

### 데이터 조사

- `predictions` 5m 일별 평균 confidence(06-19→07-02): 0.4498, 0.4326, 0.4207, 0.4559, 0.4320,
  0.4953, 0.4140, 0.4322, **0.3912(07-01)**, **0.3895(07-02)** — 06-29 이후 하락 추세, 오늘만의
  이상치 아님
- `calibration_report.md` 최근구간: accuracy **32.78%**(3분류 랜덤 33.3%와 사실상 동일),
  bin별 accuracy가 **역전**(0.8~0.9=31.36% < 0.3~0.4=33.64%) — 고신뢰일수록 더 틀림
- `strategy/entry/checklist.py:115`의 `min_conf_effective`(0.56~0.58)가 `confidence`
  (raw, oggi 0.35~0.44대)와 직접 비교되는 1차 게이트라 여기서부터 이미 거의 다 막힘
- `drift_adjuster_state.json` acc_history 최근 10개: `0.5,0.35,0.2648,0.5,0.5,0.1562,0.5,
  0.3333,0.5,0.5` — 표본 부족 구간에서 극단값 노이즈 큼
- CB③(30분 정확도<35%→당일 정지) 임계와 30m 호라이즌 누적 accuracy(32.88%)가 근접 —
  실제 오늘 CB③ 발동 여부는 로그 미확인(다음 세션 후보)

### 버그 발견 ① — `scripts/generate_meta_gate_tuning_report.py`

`meta_labels` 소스 그리드서치에서 `row["meta_confidence"]` 컬럼이 애초에 SELECT에 없어
(`ml.meta_score`만 존재, 별칭 불일치) `"meta_confidence" in row.keys()`가 항상 False →
매번 `predictions.confidence`(raw)로 조용히 폴백. 게다가 `meta_labels.meta_score`는
`learning/meta_labeling.py`에서 보듯 연속 신뢰도가 아니라 **0.0/0.5/1.0 이진 판정 라벨**이라
애초에 confidence 그리드서치 대상이 될 수 없는 컬럼이었음. 리포트의 "avg_meta_confidence=0.46 ↔
권장 임계 0.65~0.71" 비교는 설계가 잘못된 산출물.

### 버그 발견 ② — `rollout_readiness_report.md`의 위험 신호 누락

`generate_calibration_report.py`가 이미 `conf_inversion` 감지기(고신뢰 구간이 저신뢰보다
3%p 이상 덜 정확하면 발동)를 계산해 `calibration_metrics.json`에 기록해두고 있었는데,
`generate_rollout_readiness_report.py`는 이 필드를 전혀 읽지 않고 ECE 스칼라 하나만으로
`small_size` 승격을 추천 중 — ECE는 평균 오차라 이런 역전을 못 잡음.

### 수정 (커밋 d9bf4f0)

| 파일 | 변경 |
|---|---|
| `scripts/generate_meta_gate_tuning_report.py` | `meta_labels` fetch 쿼리에 `ensemble_decisions.meta_confidence`를 `(SELECT ts, meta_confidence, MAX(id) AS id FROM ensemble_decisions GROUP BY ts)` 서브쿼리로 LEFT JOIN(ts 기준, SQLite의 단일 MAX 집계 bare-column 규칙 이용해 최신 1건만). `build_metrics()`가 이 실제 blended_conf를 사용하도록 변경, ensemble_fallback 소스 분기는 미변경 |
| `scripts/generate_rollout_readiness_report.py` | `decide_stage()` 최상단에 `conf_inversion` 가드 추가 — 감지되면 ECE/PnL 무관하게 `shadow` 강제 반환(사유 문자열에 high_acc/low_acc/gap 포함). `Checklist`에 `Confidence inversion: none/DETECTED` 라인, `metrics`에 `conf_inversion` 필드 추가 |

### 검증 (수정 직후 재실행)

- `generate_meta_gate_tuning_report.py 5m`: avg_meta_confidence 0.4612→**0.2171**(flat_signal
  스킵 시 meta_confidence=0.0 다수 포함 — 정상), best grid match율 73.59%→**76.40%**
- `generate_rollout_readiness_report.py`: 시뮬레이션으로 conf_inversion 강제 주입 시
  ECE=0.05·PnL 양호해도 `shadow`로 정확히 강등되는 것 확인. 단 현재 실제 gap=2.85%p로
  발동 임계(3%p) 바로 아래라 오늘 리포트는 여전히 `small_size` — 273차 EKS 마진 이슈와
  동일 패턴(근소 미달로 안전장치 미발동)

### 커밋 범위

[[feedback_git_commit_scope]] 원칙에 따라 `scripts/*.py` 2개만 커밋. 재생성된
`meta_gate_tuning_report.md`/`.json`, `rollout_readiness_report.md`/`.json`은 PC별 로컬
런타임 산출물이라 커밋 대상에서 제외(작업트리에 M 상태로 남는 게 정상).

### 남은 작업 (NEXT_TODO 275차)

- conf 하락(06-29~) 근본 원인 조사 — EOD 재학습 데이터 품질/canary z경고/scaler refit 로그 대조
- CB③ 오늘 실제 발동 여부 확인 — 30m accuracy(32.88%)가 이미 임계(35%) 밑
- conf_inversion 임계값(3%p) 근소 미달 관찰 — 필요 시 하향 검토
- drift_adjuster 최소 표본수 가드 검토

---

## 2026-07-02 (274차 — 진입0 딥다이브 + ATR 적응형 상한 · Hurst/MR 조건부 완화)

**트리거**: 07-02 09:00~12:30 장중 실거래 진입 0건 — 사용자 요청으로 원인 딥다이브.

### 로그 기반 퍼널 분석 (216분봉)

```
216 분봉 실행
 → ~200 : 방향無/신뢰도 미달로 즉시 X등급 (모델이 확신 못 준 정상 관망)
 → 9    : 등급 A/B 도달 (진짜 기회) — 09:08, 09:10, 10:21, 10:22, 10:25, 10:27, 10:28, 10:33, 10:36
   → 2건 EKS 발동 관망 차단 (09:08, 09:10) — 의도된 안전장치, 정상
   → 5건 ATR_MAX_ENTRY(3.5pt) 상한 차단 (10:21~10:28 연속, ATR 4.2~4.6pt)
   → 2건 Hurst<0.45 횡보 게이트 차단 (10:33, 10:36)
 → 실제 진입: 0건
```

### 근본 원인 ① — `ATR_MAX_ENTRY=3.5pt` 정적 상한의 만성적 시대 뒤처짐

06-30(263차) 도입 당시 NEXT_TODO에 "1주일 후 재조정 검토" 항목이 이미 있었음.
06-24~07-02 7거래일 1분봉 ATR 중앙값을 뽑아보니 3.49~6.23pt로 **거의 매일 3.5pt 문턱 근처거나 상회** —
"예외적 고변동 상황"이 아니라 현재가 정상 레짐이고 3.5pt가 낡은 값이었음이 실증됨.

### 근본 원인 ② — Hurst 게이트가 MR(평균회귀) 모드까지 함께 차단

`main.py`의 `_hurst_ok`가 `entry_mode`를 구분하지 않고 전체 진입을 차단. `checklist.py`의
`MEAN_REVERSION` 모드는 원래 Hurst가 낮은(횡보) 구간용 대응 전략인데, 발동 조건
(`VWAP 1.5σ 이탈 AND exhaustion≥0.70` 동시충족)이 너무 빡빡해 최근 2거래일 0회 발동 —
결과적으로 Hurst<0.45 구간은 "TF도 막히고 MR도 안 켜지는" 완전 무전략 관망 구간이었음.

### 수정 (커밋 예정)

| 파일 | 변경 |
|---|---|
| `config/settings.py` | `ATR_ADAPTIVE_MAX_WINDOW=60`·`ATR_ADAPTIVE_MAX_MULT=1.25`·`ATR_ADAPTIVE_MAX_CEILING=6.0`·`ATR_ADAPTIVE_MIN_SAMPLES=20` 추가. `MR_EXHAUSTION_MIN_WEAK=0.60`·`MR_WEAK_SIZE_MULT=0.5` 추가 |
| `main.py` | `self._atr_recent_window`(deque maxlen=60) 신설, 매분 ATR 적재. 진입 판정 시 표본≥20이면 `상한=clamp(정적3.5, 최근60분평균×1.25, 절대상한6.0)`으로 동적 계산해 `_atr_ok`에 적용. `_hurst_ok`에 `entry_mode=="MEAN_REVERSION"` 예외 추가 — MR 모드는 Hurst 값과 무관하게 통과. 차단 로그·대시보드 `_atr_state`도 적응형 값 기준으로 갱신 |
| `strategy/entry/checklist.py` | VWAP MR 체크를 `exhaustion≥0.70`(정상, 풀사이즈) / `0.60~0.70`(약한 MR, `_mr_weak=True`) 2단계로 분리. 약한 MR은 등급 결정 후 `size_mult *= MR_WEAK_SIZE_MULT(0.5)` 적용 |

### 위험 수용

- ATR 적응형 상한 상향은 손절거리(ATR×1.5)가 커지는 트레이드를 허용 — Sizer 공식이 `수량 ∝ 1/ATR`이라
  계약 수는 자동으로 줄어듦(별도 사이즈 조정 로직 불필요). 표본 20개 미만(장 시작 직후) 구간은 기존
  정적 3.5pt를 그대로 사용해 cold-start 리스크는 없음.
- 약한 MR(0.60~0.70)은 사이즈 0.5배로 리스크를 억제했으나 실거래 성과는 미검증 — NEXT_TODO 274차
  항목으로 1~2주 관찰 예정.

---

## 2026-07-01 (264차 — EKS 오발동·z경고 과측정 3종 근본 수정)

**트리거**: 오늘 장 시작 로그 딥다이브 — `[09:05] EKS 발동 conf_max=0.0% bars=5` + `z경고14개` 원인 조사.

### 로그 재구성 (실제 발생 경위)

```
08:45  EarlyWarmup: 30봉(어제 데이터) → refit → scaler_age=0h ✓
08:47  Phase1 (bar3): refit → z_after(3봉) 낮음 → "성공"으로 보임
08:49  Phase2 (bar5): refit → z_after(5봉) 낮음 → "성공"으로 보임
08:55  Canary: n_rows=60 측정 → z=14 (임계12 초과) → Canary refit 발동
         ← is_open_volatile·hurst_ready 등 _Z_WARN_EXEMPT 피처가 어제 봉에서 +4 과산출
09:00  파이프라인 2447ms(장시작버스트) → delayed=True
09:00~09:04  HORIZON_TIME_POLICY=(900,905):[] → active_horizons=[] → conf=0.0
09:05  EKS 판정: _is_cold_start=(conf==0.0 AND delayed==0) = False → EKS 오발동!
         ← 09:00 장시작버스트 delayed_count=1이 cold-start 탐지 무너뜨림
```

### Bug 1: EKS cold-start 오발동 — `safety/system_health.py`

- **원인**: `HORIZON_TIME_POLICY=(900,905):[]`가 09:00~09:05 전 호라이즌 차단(conf=0.0 설계적). 09:00 장시작버스트가 `delayed_count=1`을 만들어 `_is_cold_start=(conf==0.0 AND delayed==0) = False` → EKS 발동.
- **수정**: `_gap_open_policy_blocked_count` 카운터 추가. `active_horizons_blocked=True` 봉을 별도 추적. `_is_cold_start = conf==0.0 AND (delayed+policy_blocked >= bar_count)`.
- **효과**: 오늘 케이스 — delayed=1 + policy_blocked=4 = 5 = bar_count → cold-start 정상 판정 → EKS 미발동.

### Bug 2: `canary_z_warn_count` `_Z_WARN_EXEMPT` 누락 — `model/multi_horizon_model.py`

- **원인**: 260차에서 `predict_proba`에 `_Z_WARN_EXEMPT={bull_reversal_signal, hurst_ready, is_close_volatile, is_open_volatile}` 추가했으나, `canary_z_warn_count`는 미적용. 60봉 윈도우에 어제 세션 봉(is_open_volatile z≈5.0, hurst_ready z≈4.5 등)이 포함되어 +4 과산출.
- **수정**: `canary_z_warn_count`에 `predict_proba`와 동일한 `_Z_WARN_EXEMPT` 필터 적용.
- **효과**: Canary z=14 → ~10, Phase1·2 refit 효과가 정확히 반영됨.

### Bug 3: `_last_canary_z_warn` stale — `main.py`

- **원인**: EKS 원인 진단 시 `_last_canary_z_warn`이 08:55 Canary refit 착수 전 값(14)으로 고정. refit 후 값이 반영되지 않아 오진단.
- **수정**: Canary refit 완료 후 `_last_canary_z_warn`과 `system_health.update_z_warn()` 갱신.

### Escape 체인 분석 (커밋 이력 기반)

- **214차**: PRE_MARKET_REFIT_STEPS `{1}→{3}` — 1봉 역효과 실측(z 6→14 악화)으로 3봉부터.
- **247차**: `PRE_MARKET_SCALER_BARS=30` — 500봉에서 30봉으로 단기화. 검증 데이터: 6/23~6/25 모두 z<12 달성.
- **259~260차**: `_Z_WARN_EXEMPT`에 이진·시간 플래그 추가. **`canary_z_warn_count` 미반영으로 Canary 측정과 predict_proba 측정값 괴리 발생** → 오늘 7/1 z=14 (실제 ~10).

### 커밋

- `332e6c4` — `264차: EKS 오발동·z경고 과측정 3종 근본 수정`

---

## 2026-06-30 (263차 추가 — 진입 안전장치 3종: ATR상한·시가이격·인트라바스톱)

**트리거**: 09:44:54 SHORT 4계약 진입 → 6분 만에 -137만원 하드스톱 손실. 사후 딥다이브 분석.

### 손실 원인 분석

- 당일 시가 1364.66, 진입가 1332.32 = **시가 대비 -32pt 추격 SHORT** (낙폭 소진 구간)
- 진입 시 ATR ≈ **4.09pt** (ATR_STOP_MULT×1.5 = 손절거리 6.14pt) → 1분봉 시스템 과도
- 하드스톱 발동 분봉(09:50)에서 청산 요청가 1338.46 → 실체결 1339.13 = **+0.67pt 슬리피지**
- 체크리스트는 9개 항목 모두 분봉 맥락만 봤고, 당일 시가 이격을 보지 않음

### 구현 (커밋 23b25ce)

**[A] ATR 상한 필터** (`config/settings.py`, `main.py`)
- `ATR_MAX_ENTRY = 3.5` 추가 — ATR > 3.5pt 시 진입 차단
- `_atr_ok = ATR_MIN_ENTRY <= atr <= ATR_MAX_ENTRY` (기존: 하한만)
- 오늘 케이스: ATR=4.09 > 3.5 → **차단됨**

**[B] OPEN_VOLATILE 시가 이격 필터** (`config/settings.py`, `main.py`)
- `ATR_OPEN_GAP_MULT = 5.0` 추가
- 조건: OPEN_VOLATILE + TREND_FOLLOW + gap_in_direction > ATR×5 → 진입 차단
- `_open_gap_ok` 플래그, `_gate_checks["open_gap_ok"]`, 진단 메시지 포함
- 오늘 케이스: 32.3pt > 4.09×5=20.4pt → **차단됨**

**[D] 인트라바 스톱 히트** (`strategy/position/position_tracker.py`, `main.py`)
- `is_stop_hit_intrabar(bar_low, bar_high)` 메서드 추가
- `_check_exit_triggers` + `_ts_check_exit_triggers` 양쪽 적용
- 종가가 스톱 위에 있어도 분봉 고가(SHORT)/저가(LONG)가 스톱 터치 시 즉시 청산
- `bar["key"]` → `bar.get("key", price)` 안전 접근으로 KeyError 방지 병행

---

## 2026-06-30 (263차 — EOD 재학습 pkl 경합 방지)

**트리거**: 오후 미륵이 지연 종료 현상 조사 → daily_close STEP 3 대기 중 MireukiEODRetrain 동시 실행 경합 위험 발견.

### 조사 내용

- 15:40:25 daily_close() 진입, STEP 3 장중 GBM 재학습 진행 중 감지
- 15:45 MireukiEODRetrain 실행 → pkl 동시 기록 경합 가능성 존재
- `retrain_eod_20260630.log` 확인: 6/6 호라이즌 정상 완료 (오늘은 EOD가 마지막 기록)

### 구현 (커밋 5aed765)

`retrain_eod.py` — `_wait_for_daily_close(max_wait_min=20, poll_sec=30)`:
- `data/_exit_normally` 파일의 오늘 날짜 확인 → daily_close 완료 검증
- 미완료 시 30초 폴링, 최대 20분 대기
- 타임아웃 시 슬랙 경보 후 강제 진행

### 운영 조치

- 윈도우 스케줄러 `MireukiEODRetrain` **15:45 → 16:10** 변경 완료 (1차 방어선)
- 코드 대기 로직 (2차 안전장치)

---

## 2026-06-30 (262차 — SHORT 진입·손실청산 감사 개선 4종)

**트리거**: 09:44 short 진입과 손실 청산 감사 요청.

### 감사 결과 (7개 이슈 발견)

SHORT 진입 3종:
- MR SHORT `bull_exhaustion > 0.0` 임계 부재 (exhaustion 구조상 0.0 or 0.60~1.0)
- MR 모드에서 #7 직전봉 체크가 트렌드 추종 기준 그대로 적용돼 MR 타이밍 손실
- cvd_delta_norm SHORT 체크 단기 노이즈 (통과율 미검증 — 모니터링 과제)

손실 청산 4종:
- TP1 부분청산 후 잔여분 손절 미이동 → EV 역전 구조 (핵심)
- 0~0.5ATR 수익 구간 트레일링 무방비 지대
- 1계약 TP1 arm: `_ts_execute_partial_exit`에 기구현 확인 (수정 불필요)
- 분봉 종가 기반 손절 시간 지연 (실시간 틱 연동 필요 — 중장기 과제)

### 구현 내용 (커밋 b28a0cb)

| 파일 | 변경 |
|---|---|
| `config/settings.py` | `MR_EXHAUSTION_MIN = 0.70` 신규 상수 |
| `strategy/entry/checklist.py` | MR 탈진 임계 `>= 0.70` 적용, #7 MR 모드 분기 추가 |
| `strategy/position/position_tracker.py` | 0.5ATR 트레일링 단계 + `get_trailing_reference_price` 동기화 |
| `main.py` | `_post_partial_exit(stage=1)` 후 잔여분 손절 → 진입가 자동 이동 |

---

## 2026-06-29 (260차 — Extreme 피처 Top5 딥다이브 이상점 5종 수정)

**트리거**: 오늘 누적 extreme 피처 Top5 대시보드 스크린샷 — hurst_ready(162회), is_close_volatile(54회), toxicity_spread_stress(48회), bull_reversal_signal(30회), atr_expansion_rate(18회) 딥다이브 요청.

### 이상점 분석 및 수정

| 피처 | 이상 유형 | 수정 | 파일 |
|---|---|---|---|
| `atr_expansion_rate` | unbounded, z=18.32 | `np.clip(-0.5, 0.5)` + `_prev_atr > 1e-6` | `feature_builder.py:346` |
| `bull_reversal_signal` | 쿨다운 없는 과발동 30회 | warmup 20봉 억제 + 5봉 쿨다운 | `ofi_reversal.py` |
| `toxicity_spread_stress` | 스케일러 μ=0.978 역전 | `_MACRO_SCALE_FLOOR[...]=0.25` | `multi_horizon_model.py` |
| `hurst_ready` | binary 플래그 z≈4.5 | `_Z_WARN_EXEMPT` 등록 | `multi_horizon_model.py` |
| `is_close_volatile` | 시간 binary z≈5.5 | `_Z_WARN_EXEMPT` 등록 | `multi_horizon_model.py` |
| `is_open_volatile` | 시간 binary (예방적) | `_Z_WARN_EXEMPT` 등록 | `multi_horizon_model.py` |

### 핵심 판단

- `toxicity_spread_stress` μ=0.978은 235차 tick_size 수정 이전 훈련 데이터 고착. SCALE_FLOOR=0.25로 임시 억제, EOD 재학습으로 자연 해소 예정.
- `bull_reversal_signal` 5봉 쿨다운은 단기 반전 신호 특성상 보수적 설정. 실전 검증 후 조정 가능.

---

## 2026-06-29 (259차 — bull_reversal_signal z>4 과발동 + HealthPolicy 동적화)

**트리거**: 11:04:58 bull_reversal_signal z=+5.89 전 호라이즌 동시 발생 → conf 36% 26분 고착 + HealthPolicy 상시 차단 → 이후 흐름 딥다이브 및 개선 구현 요청.

### 분석 과정

1. **bull_reversal_signal 정체 확인**: `ofi_reversal.py` — 이진(0/1) OFI 반전 신호. 발동 시 항상 z≈5.89 (mean≈0.01, σ≈0.17). 전 호라이즌 동시 발생은 동일 OFI 데이터 공유로 구조적 불가피.

2. **conf 36.0% 26분 고착 원인**: bull_reversal_signal=1이 GBM UP 방향 편향 → 30m 역방향/CoherenceGate와 결합해 conf=36% 고착. ConstOut으로 인한 것이 아니라 GBM 내부 편향 고착.

3. **MetaGate take 신호 발생 확인**: 11:13(47.5%), 11:15(49.5%), 11:17(50.8%), 11:18(50.8%) meta_conf=take — 신호는 있었으나 HealthPolicy(0.62 고정)에 최종 차단.

4. **MetaGate min_conf=0.570 "고착" 오해 해소**: STEP 1 검증 루프(default 0.57)와 STEP 6 진입 판단(actual_min_conf=0.39) 두 경로가 같은 타임스탬프에 찍혀서 착시. 실제 진입 판단은 0.39 정상 사용.

5. **HealthPolicy Degraded Mode 차단 구조**: 고정 0.62가 현 conf(32~38%) 대비 과도 → zone_mc 기준 동적화로 개선.

6. **257차 효과 실증**: 11:31:58 RETRAIN에서 STABLE_TREND 0.420→0.357 (MC_PERCENTILE 수정 첫 확인), grade=C 최초 출현.

### 핵심 결정

- 이진 피처는 `_MACRO_SCALE_FLOOR`(floor=0.45) + `_Z_WARN_EXEMPT`로 이중 처리
- HealthPolicy Degraded min_conf를 `max(actual_min_conf, 0.30)` 동적화
- DynMC ConstOut 15% 필터로 고착 conf 제외

### 수정 파일

`model/multi_horizon_model.py`, `main.py` | 커밋: `3281067` (259차)

---

## 2026-06-29 (258차 — save_horizon_features 4인자 버그 수정)

**트리거**: WARN 로그 86회 `[DBQueue] 쓰기 실패: save_horizon_features() takes 3 positional arguments but 4 were given` 발견 → 즉시 수정.

### 핵심 결정

- 호출에서 `_regime` 제거 (2군데). 스키마 변경 불필요 — raw_features_horizon에 regime 컬럼 없음.
- 옵션 B(regime 컬럼 추가)는 ALTER TABLE 위험 + 당장 불필요 → 기각.

### 수정 파일

`main.py` | 커밋: `ea5f4f7` (258차)

---

## 2026-06-29 (257차 — DynMC MC 기준 상향 원인 5종 수정)

**트리거**: 6/29 오전 진입 0회. 앙상블 conf 추이 분석 + 6/26 대비 MC 상향 원인 딥다이브 요청.

### 분석 과정

1. **앙상블 conf 추이 분석** — meta_gate_tuning_metrics.json에서 오늘 blended_conf=0.333~0.499, take_thr=0.570 → 17%p 갭. Platt 캘리브레이터가 raw conf를 35~45%로 압축하는 구조적 상한 확인.

2. **6/25 vs 6/29 진입 비교** — 6/25: 수동 버튼 클릭 2회 + 자동 1회(DynMC=0.25). 6/29: EKS 09:05 발동 후 미해제, 진입 0회. 6/25는 EKS 없었고 MC=0.25(낮음), 6/29는 MC=0.54~0.57(코드 기본값에서 시작).

3. **MC 상향 원인 추적** — SIGNAL 로그 비교:
   - 6/25 09:00: `FQAdj min_conf 0.26→0.25` (mc_history 복원 성공 → 0.250)
   - 6/29 09:00: `FQAdj min_conf 0.67→0.64` (코드 기본값 0.670 그대로)
   - 6/29 09:11: `DynMC RETRAIN base=0.510 STABLE_TREND 0.540→0.510`

4. **mc_history DB 실체 확인** — `data/mc_history.db` 0 bytes(내 쿼리가 빈 파일 생성). 실제 DB는 `data/db/mc_history.db` (DB_DIR 기반). 오늘 20건만 존재, 이전 날 기록 없음 → 기동 복원 0건 → 코드 기본값(0.54) 사용.

5. **MC_PERCENTILE 버그 확인** — `int(n × 0.65 / 100) = int(n × 0.0065)` → n=2086 기준 idx=13 (0.6%분위, 실측 conf_p65=0.17). 의도는 65분위이나 /100으로 인해 최솟값 근방 사용 중.

### 핵심 결정

- **MC_STEP_LIMIT 0.03→0.08**: 복원 실패 시 코드 기본값에서 목표까지 5시간→1시간 내 수렴
- **MC_PERCENTILE 수정**: `/100` 제거로 진짜 65분위 사용 (p65 0.17→0.38~0.42)
- **빈 DB fallback 0.35**: 복원 실패 시 코드 기본값(0.54~0.67)이 아닌 안전값 적용
- **cold-start EKS 면제**: conf=0%+delayed=0 조합 → cold-start로 감별, EKS 미발동
- **EKS 회복 로그 INFO→WARNING**: 미충족 조건 명시로 진단 가시성 확보

### 수정 파일

`config/settings.py`, `strategy/entry/time_strategy_router.py`, `safety/system_health.py`
커밋: `f4b7806` (257차)

---

## 2026-06-29 (256차 — EKS 로그 메시지 정정)

**트리거**: 장기 중단(약 41일) 후 재시작 로그에서 `[SHS-EKS] Early Kill Switch 발동 — 당일 관망 선언. conf_max=0.0% bars=5` 메시지 분석 요청. EKS가 영구 차단처럼 보이는 문제 + 실제 코드 상 자동 회복 메커니즘 확인 요청.

### 핵심 결정

- **EKS 자동 회복 코드 검증**: `can_attempt_recovery()` + `try_eks_recovery()` 정상 구현 확인 (09:20부터 30분 간격, 11:30 마감)
- **메시지 정정**: "당일 관망 선언" → "일시 관망 (30분 간격 자동 회복 평가)" 전면 교체
- **EKS 해제 Slack 알림 신설**: 발동은 CRITICAL 알림 있었으나 해제 알림 누락 → `notify_kill_switch_cleared()` 추가

### 수정 파일

`safety/system_health.py`, `main.py` (2곳), `utils/notify.py`, `dashboard/main_dashboard.py`

---

## 2026-06-28 (255차 — CREON Plus 자동 로그인 완전 구현)

**트리거**: CREON Plus 로그인 시 CREON Plus 드롭다운 미선택, 자격증명 미입력, 모의투자 접속 팝업 미처리 문제.

### 핵심 결정

- **좌표 기반 접근**: CREON 로그인 창 전체가 HTCAPTION+HTRANSPARENT 구조 → 텍스트/UIA 탐지 불가 → 픽셀 스캔 + 히트테스트로 좌표 확정
- **드롭다운 선택**: 헤더 click(+90,+15) → hover 400ms → click(+65,+85) (단일 클릭만, 반복 시 창 드래그)
- **자격증명 분리**: CREON=`creonplus`, CYBOS=`cybosplus` (CredTarget 브로커별 분기)
- **모의투자 팝업**: in-window GDI 오버레이 → EnumWindows 불가 → win_origin+(365,317) 고정 좌표

### 실증 검증

- `IsConnect=1, ServerType=1` 확인 (모의투자 로그인 성공)
- em-dash 인코딩 오류 수정, UTF-8 stdout 강제 설정

---

## 2026-06-26 (254차 — 거래소 서킷브레이커 감지·대응·대시보드 표시)

**트리거**: 6/26 KRX CB 1단계 발동 (KOSPI 8% 이상 하락) → 파이프라인 4분 미실행 WARN. 이후 CB 대응 구현 + 대시보드 배지 추가 요청.

### 결정 사항

- **감지 기준**: 240초(4분) 미수신 + `broker.is_connected=True` → CB 즉시 확정 (네트워크 구분)
- **관망 기간**: 10분 (KRX 단일가매매 10분 전 구간 커버)
- **포지션 처리**: CB 해제 첫 분봉 close로 즉시 force_exit → 관망 10분 → 진입 재개
- **일일 마감 리셋**: CB 3단계(장 조기 종료) 시 다음날 CB 모드 잔류 방지

### 배지 디자인 (lbl_ecb)

- 위치: 헤더 매크로레짐(`lbl_regime`) 배지 왼쪽, 평소 숨김
- CB 발동: `#7a0000` 빨강 + `#FF5252` 테두리, "KRX CB ⏸ / 재개≈HH:MM"
- 관망 중: `#7a3800` 주황 + `#FFB74D` 테두리, "관망 N분 / HH:MM 재개" (매분 갱신)

### 수정 파일

`main.py`, `dashboard/main_dashboard.py`

**커밋**: `a320849` (254차)

---

## 2026-06-26 (253차 — 6/26 장중 분석 7종 수정)

**트리거**: 6/26 모의투자 첫 장 — EKS 발동, OptionChainWorker 크래시 2회, CB⑤ 기준 초과 블로킹 2회. launcher_20260626_084000.log 전체 분석 요청.

### 딥다이브 결과 (5개 주제)

**① OptionChainWorker 크래시 (09:11, 09:21)**
- 원인: `_poll_option_chain` line 2572 — `deleteLater()` 후 C++ 소멸, Python wrapper 살아있어 `.isRunning()` → RuntimeError
- 수정: try/except RuntimeError → `self._option_chain_worker = None`

**② 메인 스레드 블로킹 2건**
- 09:01 (7,187ms): `_fetch_investor_data` → BlockRequest(CpSysDib.CpSvrNew7221) 09:00 서버 피크. COM STA 메시지 펌프는 COM 이벤트(파이프라인)는 허용, Qt 타이머(_tick_header) 불허.
- 09:23 (14,828ms): 재시작 직후 `_apply()` 4개 패널 직렬 → 4단계 QTimer 체인으로 분해
- InvestorWorker QThread 분리 검토 → COM STA 위반 위험 + 09:00-09:02 guard로 충분 → **기각**

**③ EKS 과발동 원인 — z경고 12개**
- `toxicity_atr_stress`: SCALER_CLIP_FEATURES 미등록 → 고변동성 장 z>4
- `quality_investor_age_sec`: clip 범위 버그 (0,180.0) → 정규화값 [0,1]에 무효. (0,0.60)으로 수정
- ScalerFloor σ 하한 추가: quality(0.15), toxicity(0.20) → z_max<4 보장

**④ ScalerFloor WARNING 72개 폭증 원인**
- macro 피처는 일봉 상수 → 30봉 window σ<floor 구조적 정상
- `_apply_macro_scale_floor`에 trigger_type 파라미터 추가 → pre-market/EOD: INFO, 장중: WARNING
- 개선안 B (mean=0) 검토: macro_us10y_chg mean=-0.483 → z=-4.83 EXTREME 발생 확인(py37_32 scaler pkl 직접 로드 테스트) → **기각**

**⑤ EarlyWarmup 17h — EOD P8 정상인데 왜 경고?**
- EARLY_WARMUP_MIN_AGE_HOURS=4.0 (247차) → 매 영업일 15:47→08:45=17h>4h 항상 발동. 설계 의도.
- retrain_eod.py가 `p8_last_success_date`만 쓰고 `eod_retrain_ok_date`는 안 씀 → daily_close(15:40) 레이스 → PreRetrain fallback 의존. `eod_retrain_ok_date` 추가 기록으로 해결.

### 수정 파일

`main.py`, `config/settings.py`, `model/multi_horizon_model.py`, `retrain_eod.py`, `strategy/runtime/session_recovery_service.py`

**커밋**: `8952dd7` (253차)

---

## 2026-06-25 (252차 — macro_risk_off CORE 해제)

**트리거**: ScalerFloor 로그 `macro_krw_chg 0.0776→0.10`, `macro_risk_off 0.4221→0.50` 딥다이브 + 피처 이득 분석 요청.

### 딥다이브 결과

**ScalerFloor 흐름**:
- `refit_scalers_only()` → `StandardScaler().fit(X_97feat)` → `_apply_macro_scale_floor()` 순서
- `macro_krw_chg` σ_raw=0.0776: KRW 변동성 비정상 저조 (≈0.23%/일). floor=0.10 → 실전 z-score 폭발 방지 ✓
- `macro_risk_off` σ_raw=0.4221: Bernoulli p=0.232 (23.2% 봉에서 발동). floor=0.50 → 발동했지만 예측 경로 무관

**피처 이득 분석**:
- `macro_krw_chg`: 10m gain 3.4%(7위/11), 30m gain 6.3%(6위/11) → **유지 결정**
- `macro_risk_off`: 전 호라이즌 feature_names_hz.pkl 미포함. SHAP=0, gain=0 → **CORE 해제 결정**

**경로 확인 (macro_risk_off)**:
- `checklist.py` → 없음 ✓
- `online_learner.py` → 없음 ✓
- `CORE_MASK_EXEMPT_BY_GROUP` settings.py → mid/long 양쪽 등록 확인 → 제거 대상
- `horizon_feature_sets.json` → `_feature_status_summary.macro_relearn_required`에만 있음 (피처셋 정의 아님)

### 수정 (252차)

- `CORE_MASK_EXEMPT_BY_GROUP["mid"]["long"]`에서 제거
- `_CORE_MASK_EXEMPT` frozenset에서 제거
- `_MACRO_SCALE_FLOOR`에서 제거
- `CLAUDE.md` CORE 해제 이력 추가

**커밋**: `e37f815`

---

## 2026-06-25 (251차 — macro_vix CORE 강등)

**트리거**: EOD 로그 `[ScalerRefresh] CORE 'macro_vix' raw_std=0.0309 → identity(0,1) 강제` 반복 경보 딥다이브 요청.

### 딥다이브 결과

**raw_std=0.0309 원인 (5계층)**:
1. Cboe CDN `VIX_History.csv` = 일봉 종가 → 장 내 상수
2. `vix_norm = (vix-15)/25` → 하루 종일 동일값
3. ScalerWarmup 500봉 윈도우에 전날 데이터 포함 → 날짜 경계 VIX jump가 소량 std 발생 (0 아닌 0.031 이유)
4. `raw_std < 0.05` → identity 강제(scale=1.0)
5. `_MACRO_SCALE_FLOOR["macro_vix"]=0.10` 미동작 — identity 후 scale=1.0 > floor=0.10 → 조건 미충족

**피처 가치 평가**:
- SHAP 중요도: 주 24=0.000669, 주 25–26=0.000 → 사실상 최하위
- 체크리스트: mid 그룹 slot 4 임계 `macro_vix < 0.5` = VIX < 27.5 → 평상시 항상 통과 (무의미)
- 동일 정보: `macro_risk_off`(VIX>28 이진), `atr`(중요도 0.33)이 이미 포착

### 수정 (251차)

`macro_vix`를 중기/장기 CORE에서 강등, 보조 피처로 유지:
- `CORE_FEATURES_BY_GROUP["mid/long"]` macro 키 제거
- `CORE_MASK_EXEMPT_BY_GROUP["mid/long"]` macro_vix 제거
- `_CORE_MASK_EXEMPT` frozenset에서 macro_vix 제거
- 중기 slot `4_cvd` → True 고정 (CVD·OFI처럼 면제)
- `_MACRO_SCALE_FLOOR["macro_vix"]=0.10` 및 `active_features` 유지

**커밋**: `f157046`

---

## 2026-06-25 (250차 — 30m 비활성화·CB③ 억제·CORE 피처 교체·feature_names_hz JSON 정정)

**트리거**: 장중 ERR-FATAL `X has 12 features, but HistGradientBoostingClassifier expecting 97` (09:00:59) + EOD 로그 `cvd_direction raw_std≈0(0.0490)` 경보.

### 발견 1 — feature_names_hz.pkl · 모델 불일치 (ERR-FATAL 원인)

Phase C 슬라이싱 도입 이후 retrain에서 모델 정확도 미달 시 `_save_feature_names(h_names, hz)` 가 `replaced=False` 상태에서도 실행 → `feature_names_3m.pkl`=12개 vs `gbm_3m.pkl`=97피처 → `_hz_feat_indices` 슬라이싱 → `xs=12`-dim → ERR-FATAL. (246차에서 근본 수정, 250차에서 방어 코드 추가)

**방어 코드 추가** (`multi_horizon_model.py`): `clf.predict_proba(xs)` 직전 `xs.shape[1] != clf.n_features_in_` 체크 → 불일치 시 ERR-FATAL 대신 `default_result` fallback + ERROR 로그.

**불일치 파일 삭제 처리**: EOD 재학습(force=True) 이전 상태에서 `feature_names_{3m-30m}.pkl` 삭제 → EOD가 재생성하여 현재 정합 (6/6 일치).

### 발견 2 — 30m 피처 미탑재 구조적 저성능

EOD CV acc=0.2796 (랜덤 0.333 이하). need_add 7개(opt_gex_bn·opt_chain_pcr 등) 미탑재.
- **30m 역방향 필터 비활성화** (`ensemble_decision.py`): grade=X 강제 제거, 플래그만 기록
- **CB③ acc30m HALT 억제** (`circuit_breaker.py`): HALT/경고 미발동, 버퍼·P4 stage 추적 유지
- 재활성화 조건: opt 피처 4,000행 달성(≈07-02) + 30m CV acc ≥ 0.33

### 발견 3 — cvd_direction 12거래일 일방향 고착

12거래일 실측: cvd_direction 음수(-0.5) 비율 **0.0%** (12일 내내). cvd_norm=1.000 고착.
- **Layer 1**: Cybos buy_vol 시스템 편향 (buy>sell 98.6%, 하락봉에서도 97.0%)
- **Layer 2**: cumulative_cvd 단조증가 → cvd_slope 항상 양수
- **Layer 3**: cvd_abs_max = window[-1] (항상 최대값) → cvd_norm = 1.0

**대체 피처 `cvd_delta_norm`**: price-action(Williams A/D) 기반, Cybos 미사용, std 0.59~0.66, 음수 43~55% (정상 양방향). 이미 pkl 97개 포함 → 재학습 불필요.

**CORE 교체** (`config/settings.py`, `multi_horizon_model.py`, `checklist.py`, `main.py`):
- CORE_FEATURES_BY_GROUP["short"]["cvd"]: `cvd_direction` → `cvd_delta_norm`
- CORE_MASK_EXEMPT: `cvd_direction`·`cvd` 제거, `cvd_delta_norm` 추가
- checklist 4번·main.py 2곳·DBG 로그 교체

### 발견 4 — feature_names_hz JSON 오표기

`horizon_feature_sets.json`의 `in_pkl` 표기 vs 실제 pkl 전체 교차검증:
- `threshold_feasibility` (15m·30m): `in_pkl` → **`need_add`** 정정
- `queue_directional_depletion` (1m): `in_pkl` → **`need_add`** 정정

### 커밋

`1bdc971` (250차) — 9개 파일, 660 additions / 52 deletions

---

## 2026-06-25 (249차 — poll_option_chain BlockRequest QThread 분리)

**문제**: `_poll_option_chain()` QTimer 콜백에서 `Dscbo1.OptionMst.BlockRequest()` 루프가 메인 스레드를 ~3초 점유 → 틱·파이프라인·UI 정지.

**원인**: ATM ±30pt 범위 옵션 ~24종목 × (BlockRequest ~100ms + pause 50ms) = ~3.6초를 메인 스레드에서 동기 실행.

**수정**: `OptionChainWorker(QThread)` 신규 생성. 워커 스레드에서 `CoInitialize()` + 새 `Dscbo1.OptionMst` `Dispatch()` 후 BlockRequest 루프 실행. `result_ready` 시그널로 메인 스레드에 결과 반환. `OptionChainSnapshot`은 COM 코드 전부 제거 후 상태 관리 전용으로 슬림화.

**Cybos 안전 근거**: api_connector.py 주석 — BlockRequest 응답이 메인 스레드 Windows 메시지 큐 경유. QThread 분리 시 메인 Qt 이벤트 루프가 정상 펌핑하므로 응답 전달 보장. 데드락 없음.

**커밋**: `745e444` (249차), 3 files, +419 -291

---

## 2026-06-25 (248차 — EXIT stuck 무한루프 수정 + ManualExit override 확장)

**Work**: `20260625_WARN.log` 딥다이브 — 14:11~14:14 동안 order_no=4280 EXIT 부분체결 stuck이 매분 반복되며 수동 청산까지 4분 이상 차단된 현상 근본 원인 분석 및 수정.

**근본 원인 3건**:
1. `last_fill_at = now()` 무한 리셋 → 타이머가 매분 60s로 초기화돼 루프 탈출 불가
2. ManualExit가 CB HALT일 때만 stuck EXIT pending override — 브로커 확인된 stuck은 운영자도 손댈 수 없음
3. 오해 로그: "pending 소멸, 긴급청산 시도"라고 찍히지만 실제 소멸 없음

**추가 발견**: 오늘 케이스의 진짜 원인은 **부분 Chejan 유실** (2계약 거래소 체결, 1번째 Chejan만 수신). expected_remaining 탐지가 prev_pos_qty drift로 실패하는 구조적 한계 확인.

**오늘 전체 거래 흐름 분석** (TRADE.log):
- 11:13 SHORT 3계약 → TP1 +2.57pt, 하드스톱 (pending_miss 1건 포함)
- 13:04 LONG 6계약 → TP1+TP2 정상 체결, 13:15 하드스톱 1계약 stuck → 13:16 잔여청산 + 동일 분봉 LONG 5계약 재진입
- 13:23 TP1 4280 1/2 체결 후 stuck → 14:11~14:14 stuck 루프
- 14:21~14:22 외부진입 4676/4678 (LONG 1계약씩), 14:24 외부 청산 4694 (SHORT 5계약 전량)

**수정** (`main.py`, 커밋 `26f3d9f`, +26 -4):
- `_broker_confirm_count` 카운터 (3회 → 자동 pending 소멸 + TP 재점검)
- ManualExit: `_broker_confirm_count >= 1`이면 stuck EXIT pending override 허용

**커밋**: `26f3d9f` (248차), 1 file, +26 -4

---

## 2026-06-25 (247차 — 프리장 scaler 재적합 window 단기화)

**Work**: `20260625_WARN.log` EarlyWarmup 완료 후 z경고 폭증(23개) 미해결 현상 딥다이브. 5일치 로그 실증 분석 + 실데이터 시뮬레이션으로 근본 원인 규명 → PRE_MARKET_SCALER_BARS=30 도입.

**근본 원인**: 모든 pre-market refit이 `lookback_bars=500` 공유 → 어제 490봉 압도 → scaler 어제 기준 고착. 실측: 6/24 z경고 `16→16→16→16` (4회 재적합, 0% 변화).

**60봉 1차 시도 → 불채택**: 6/25 bar3에서 z 악화 회귀(500봉=14 → 60봉=26). 6/23·6/24 Canary 시점에도 여전히 임계(12) 초과.

**30봉 채택 근거**: 5일 실데이터 시뮬레이션에서 bar5 이후 z<12 달성율 100%. `opt_pcr_*` 7개 추가 zero-std(비CORE, scale_=1.0 안전처리). `cvd_direction` zero-std는 30봉·60봉 동일로 차별 없음.

**커밋**: `169b793` (247차), 2 files, +34 -12

---

## 2026-06-25 (246차 — Phase C pkl-모델 불일치 근본 수정 + Canary refit 완료 보장)

**Work**: `20260625_WARN.log` 전체 딥다이브 → 245차 수정 이후에도 ERR-FATAL이 09:00~10:36 지속된 원인 분석 → 근본 수정 4건 + 검증 후 추가 수정 2건.

**이슈 1 — 타임아웃 SIGKILL → 모델·pkl 원자성 파괴**:
- `_train_horizon()` 내부에서 `gbm_{h}.pkl` 저장 완료 → subprocess SIGKILL → `_save_feature_names()` 미실행
- `feature_names_{h}.pkl` = 12개 (미갱신), `clf.n_features_in_` = 97 → `_hz_feat_indices` 슬라이싱 오활성화
- **수정 FIX-A**: `_load_all()` 불일치 감지 + `.mismatch_bak` 자동 백업 + 97개 fallback
- **수정 FIX-B**: `_save_model()` 내부 모델+pkl 원자적 동시 저장. Phase C 피처 수 변경 경고 로그. `replaced=False` 시 외부 저장 차단

**이슈 2 — Canary refit 완료 미대기 → 미갱신 scaler로 장 진입**:
- z경고 23개 → Canary refit 기동 → `_scaler_refresh_running=True`
- ScalerWarmup 즉시 `_warmup_done_event.set()` (refit 완료 안 기다림) → `_canary_stale=True`여도 wait가 즉시 반환
- **수정 FIX-C**: Canary refit 성공 시 `_pre_market_scaler_refitted=True` 설정
- **수정 FIX-D**: refit 실행 중엔 `_wait_refit_done` 스레드로 완료 대기 후 event set (85초 상한)

**커밋 이력 교차검증 (병렬 fork 에이전트 2개)**:
- BUG 추가 발견: FIX-A의 `os.rename` → `os.replace` (Windows WinError 183, 매 시작 ERROR 반복)
- WARNING: FIX-D의 대기 상한 120초 > wait timeout 90초 불균형 → 85초로 수정
- 243차(08:03)가 Phase 2 경로에 `_save_feature_names` 최초 추가 → 같은 날 09:27 SIGKILL이 즉시 불일치를 만든 것 확인

**커밋**: `1242963` (246차), 3 files, +121 -12

---

## 2026-06-25 (245차 — SGD 스케일러 피처 수 불일치 ERR-FATAL 버그 수정)

**Work**: 장중 운영 중 `X has 11/12/15 features, but StandardScaler is expecting 97 features` ERR-FATAL 경보 딥다이브 → 원인 특정 → 방어 코드 추가.

**에러 발원지**: `online_learner.py:136` `scaler.partial_fit(x2d)` — SGD 온라인 학습 단계.

**버그 원인**:
- Phase C (호라이즌별 피처 슬라이싱) 구현 후, SGD 스케일러가 초기 타이밍에 97개 전체 피처로 `partial_fit`되어 굳음
- 이후 `_hz_feat_indices` 복원 → 11~15개 슬라이싱 피처 투입 → `n_features_in_=97` 충돌
- `learn()`에 피처 수 방어 코드 없어 ValueError → ERR-FATAL 매 분봉 반복

**진단 증거**: 에러 숫자(11/12/15)가 `feature_names_hz_*.pkl` 크기와 1:1 일치.

**수정**: `learning/online_learner.py` `learn()` — `scaler.partial_fit()` 전 `n_features_in_` 불일치 감지 시 `_do_sgd_reset()` 자동 실행.

**커밋**: (245차)

---

## 2026-06-25 (244차 — Q3 N분봉 완성 주기 배포 절충안 구현)

**Work**: `docs/q3_proba_deploy_guide.md` 가이드 기반 Q3 절충안 전체 구현. 학습-추론 분포 불일치 해소 + 스캘퍼 기회 손실 최소화.

**구현 내용**:
1. **`features/bar_aggregator.py`**: `_hz_bar_age` 내부 추적 + `get_bar_age(hz)` / `is_bar_fresh(hz, max_age)` 메서드 추가. `reset_daily()`에 `_hz_bar_age.clear()` 추가.
2. **`config/settings.py`**: `HZ_DEPLOY_POLICY` 상수 추가 — `1m=always`, `3m/5m=bar_only(age≤0)`, `10m/15m=bar_plus1(age≤1)`, `30m=filter_only`.
3. **`main.py`**: 모듈 레벨 `_is_deployable(hz, bar_aggregator)` 함수 추가. 피처 벡터 `* _decay` 제거(완성봉 원본 그대로 투입). 배포 정책 미충족 호라이즌 `horizon_proba`에서 제거. `[Deploy]` 상태 로그 추가.
4. **`model/ensemble_decision.py`**: 30m 가중치 0→재정규화(Decorrelator·F1 추적은 유지). 30m 역방향 시 `grade=X` / `auto_entry=False`. `30m_filter_blocked` 키를 모든 반환 dict에 추가.

**변경 전 → 후**:
```
[전] 매분 → 모든 hz → decay 피처 → predict_proba() → confidence × decay
[후] 매분 → hz별 배포 판정 (완성봉 타이밍 기준)
       1m        → 항상 배포
       3m/5m     → age=0만 배포
       10m/15m   → age≤1만 배포
       30m       → 항상 배포, 앙상블 가중합 제외 → 역방향 시 grade=X
```

**커밋**: `c3931d4` (244차)

---

## 2026-06-24 (방향 편향 근본 개선 — 구현 상태 검토·버그 수정·P2 사전 준비)

**Work**: `docs/260611_DIRECTION_BIAS_IMPROVEMENT_PLAN.md` 기반 방향 편향 근본 개선 전체 구현 상태 점검 → 파라미터 불일치 버그 발견·수정 → 미구현 3종 적기 판단 → P2 사전 준비 구현.

**발견 및 수정**:
1. **버그 수정**: `_DYN_HALFLIFE`·`_FLAT_CAP` 불일치 — `batch_retrainer.py`(halflife=70, 3m/5m cap=0.55)와 `multi_horizon_model.py`(halflife=100, 3m/5m cap=0.75~0.85)가 "동일 로직 유지 필수" 주석을 위반하고 있었음 → `multi_horizon_model.py`를 `batch_retrainer.py` 기준으로 동기화 (`model/multi_horizon_model.py:84-89`)
2. **P2 사전 준비 구현**: `raw_features_horizon` 테이블에 `regime TEXT DEFAULT 'NEUTRAL'` 컬럼 추가. 스키마·마이그레이션(`init_raw_data_db`)·저장 함수·`main.py` 큐 4곳 수정. 오늘부터 `current_regime` 값이 매분 기록됨.

**미구현 3종 적기 판단**:
- P1-B Triple Barrier: **보류** — `_path_conditioned_label()`+`USE_ROLLING_SIGMA_THRESHOLD`가 이미 Triple Barrier 3장벽과 동등한 구조. P0~P3 효과 검증 중 레이블 체계 변경 금지. 2~3주 후 재검토.
- P2 Regime-Conditional GBM: **불가 (데이터 부족)** — regime_history 10일치만 존재(26주 필요), 실제 구현 적기 ≈ 2027년 1월. 금일 컬럼 추가로 데이터 누적 시작.
- P4 Sample Uniqueness: **불가** — P2 의존.

**변경 파일**:
- `model/multi_horizon_model.py` — `_DYN_HALFLIFE` 100→70, `_FLAT_CAP` 전체 동기화
- `utils/db_utils.py` — `raw_features_horizon` 스키마 `regime` 컬럼 추가 + 마이그레이션 + `save_horizon_features` 시그니처 변경
- `main.py` — `horizon_features` 큐 튜플에 `regime` 추가 (put 2곳 + 워커 언팩 1곳)

---

## 2026-06-24 (242차 — V8 Phase 2 완료 점검 + 재학습 재실행 + TRAINING_WINDOW_BARS)

**Work**: V8 구현 계획서 기반 현재 고도화 상태 전수 점검 → 커밋 이력으로 Phase 2 재학습 공백(6/8~6/24 레거시 경로 덮어씌움) 확인 → 수정 3종 + 문서 정리.

**수정**:
1. `EOD_RETRAIN.bat`: `--phase2` 플래그 영구 추가 (커밋 1293022)
2. Phase 2 재학습 재실행: `eod_retrain.py --phase2 --weeks 10` → 5/6 호라이즌 교체 (30m +30.7%p, 15m +28.6%p)
3. `TRAINING_WINDOW_BARS` 구현: `learning/batch_retrainer.py` Phase 2-D 항목 완료 (커밋 1e32131)
4. V8 계획서 전면 업데이트: TODO 완료 처리 + 구현 이력 + 원안/실제 차이 명시 (커밋 e7c5e90, e872899)

**V8 잔여 판정**:
- SGD 호라이즌별 feat_vec → 구현 불필요 확정 (B군 교체 방식이 최종 설계)
- multi_timeframe.py → Stage 2(~7/8) 때 삭제 (dead code)

**커밋**: 1293022, 1e32131, e7c5e90, e872899

---

## 2026-06-24 (241차 — 장마감 종료·EOD 흐름 점검 + EOD_RETRAIN.bat py310_64 수정)

**Work**: 장마감 후 프로그램 종료 흐름(15:10→15:18→15:40 DailyClose→자동 종료)과 EOD 흐름(작업 스케줄러 `retrain_eod.py`) 전체 코드 점검 및 오늘 실측 상태 확인.

**점검 결과**:
- 종료 흐름 정상 — `daily_close()` 22단계 완료 후 `_qt_app.quit()`, 런처 AUTO-RESTART 중단 확인
- 오늘 상태: 자동 종료 완료 / EOD 마커 완료(15:48, 6/6 호라이즌) / P8 스케일러 완료
- `eod_retrain_ok_date` 공백은 설계상 정상 (daily_close 15:40 시점 마커 없음 → 내일 fallback 자동 처리)

**수정**:
- `EOD_RETRAIN.bat`: `conda activate py37_32` → `py310_64` (191차 결정 실제 반영)
- `CLAUDE.md`: 운영 환경 섹션에 EOD_RETRAIN.bat·scripts/eod_retrain.py py310_64 전용 note 추가 — 재거론 방지

**커밋**: 241차 (2de2afc)

---

## 2026-06-24 (236차 — 저신뢰 자동진입 차단 3중 안전장치)

**Work**: 6/24 일중 거래 3건 분석 → conf<35% 신호 EV=-34K/건 확인 → 자동진입 차단 로직 3개 추가.

**분석 결과**:
- Case 1 (10:26 SHORT conf=36.6%): TP1+하드스톱 net -198K원
- Case 2 (13:09 SHORT conf=37.3%): TP1+TP2 net +612K원
- Case 3 (14:04 LONG conf=27%): 하드스톱 2분 -1,271K원 ← 핵심 문제
- 5거래일 차단 시뮬레이션: 총 17건 중 11건 차단, 순익 +304K원 개선 (손실 3.1M 회피, 이익 2.8M 포기)

**수정**:
- `config/settings.py`: `ENS_CONF_FLOOR_FOR_AUTO = 0.33` 추가
- `strategy/entry/checklist.py`: conf < floor 시 `auto_entry = False` 강제 (등급 유지, 자동실행만 차단)
- `main.py` `_is_degraded_entry_blocked`: lookahead 파라미터 추가 + 선제차단 로직
- `main.py` 진입부: `_joint_blocked` 체크 (MetaGate×ToxGate 합산 < 0.50 시 차단)
- `main.py`: `self._last_pipe_ms` 매 사이클 저장

**커밋**: 236차 (894151b)

---

## 2026-06-24 (235차-d — connect_broker pt_value 갱신 누락 수정 + 이상점 정리)

**Work**: 재시작 후 금일 커밋 5개 정상작동 점검 → 이상점 3건 발견·수정.

**발견 이슈**:
- `connect_broker`: `set_tick_size`만 호출, `self._pt_value` 갱신 + `position.set_pt_value()` 누락 — [MED]
- `feature_builder.py` line 34 주석: "기본값은 일반선물(0.05)이나" 스테일 — [LOW]
- `main.py` `FUTURES_PT_VALUE` 미사용 임포트 잔존 — [LOW]

**수정**:
- `main.py` connect_broker: `self._pt_value = _spec["pt_value"]` + `self.position.set_pt_value()` 추가
- `features/feature_builder.py` line 34: 주석 "미니선물(0.02)"로 교정
- `main.py` line 81: `FUTURES_PT_VALUE` 임포트 제거

**커밋**: 235차-d (3169a8d)

---

## 2026-06-24 (235차 — 미니선물 전용 설정 전면 교정)

**Work**: 미니선물 전용 운영을 위한 제반 설정 점검 → 이슈 6건 발견 및 전체 수정.

**발견 이슈**:
- `ui_prefs.json`: market="KOSPI200 **선물**"(일반), symbol_code="A0169000"(일반선물 9월물) — [HIGH] 잘못 저장됨
- `secrets.py`: `FUTURES_CODE_PREFIX` 키 없음 — [HIGH] CodeGuard 작동 불가
- `settings.py`: `TICK_SIZE=0.05`(일반선물) — [HIGH] 미니선물 기준 0.02여야 함
- `feature_builder._DEFAULT_TICK_SIZE`: EarlyWarmup 기간 0.05 적용 — [MED]
- `main.py` 초기 `_pt_value`: 250,000(일반선물) — [MED] connect_broker 전 오계산
- `main.py` 하드코딩 `250_000`: PnL·평가금액 고정 — [MED]

**수정 (235차 3개 커밋)**:
- `ui_prefs.json`: "KOSPI200 미니선물" / "A0567000  미니 F 202607" 교정
- `config/secrets.py` (로컬): `FUTURES_CODE_PREFIX = "A05"` 추가
- `broker_runtime_service._resolve_trade_code()`: CodeGuard — A05 계열 외 코드 확정 시 기동 중단
- `features/feature_builder.py`: `_DEFAULT_TICK_SIZE = MINI_FUTURES_TICK_SIZE(0.02)`
- `main.py`: 초기 `_pt_value = MINI_FUTURES_PT_VALUE(50,000)` + `250_000 → self._pt_value`
- `config/settings.py`: `TICK_SIZE = 0.05 → 0.02` + `MAX_CONTRACTS` 미니선물 기준 주석
- `docs/260624_mireuk2_migration_plan.md`: 일반선물 미륵이2 마이그레이션 계획 문서화

**핵심 아키텍처 결정**:
- 미륵이: 미니선물(A05xxx) 전용 영구 고정
- 미륵이2(일반선물): 별도 코드 분기 금지 → 설정 주도 단일 코드베이스 (`FUTURES_CODE_PREFIX`만 다름)

**커밋**: 235차 (c836e5e), 235차-b (02cb0ce), 235차-c (7f03a56, 이번 세션)

---

## 2026-06-24 (234차 — 재시동 버그 수정 + 종목변경 배지)

**Work**: X버튼 재시작 후 프로세스 미종료 근본 원인 분석 및 수정, GUARD 커밋 이력 무결성 점검.

**분석 발견**:
- 08:40 스케줄러 자동 기동 시 기존 main.py 프로세스 살아있어 GUARD 취소됨
- 229차-b `super().closeEvent(event)` 만으로는 `quitOnLastWindowClosed` 미보장 → 프로세스 미종료
- 커밋 이력 정리: 228차-c(GUARD 기본N) → 229차(완전종료고정) → 229차-b(3-way다이얼) → 233차(장전 자동Y) → 234차(quit 강제) 순 진화
- 233차에서 GUARD 장전 자동 Y 수정은 오늘 08:40 재발 방지 (배치 기본값 N→Y)
- 234차는 229차-b에서 잔존한 프로세스 미종료 구조적 결함 해소

**수정 (3종)**:
- `dashboard/main_dashboard.py` closeEvent: `super().closeEvent()` 뒤 `QApplication.quit()` 명시 추가
- `main.py` run(): `exec_()` 반환 후 `sys.exit(0)` 추가 (COM 비데몬 스레드 방지)
- `dashboard/main_dashboard.py` + `main.py`: 종목변경 재시작 배지 (AUTO-RESTART 경유)

**커밋**: 234차 (64ad55e)

---

## 2026-06-24 (232차 — macro_risk_off 이진 피처 ScaleFloor 추가)

**Work**: 금일 09:05 EKS 발동 원인 딥다이브 → `macro_risk_off` z폭발 버그 수정.

**분석 발견**:
- 09:05:57 EKS 발동(당일 관망): z경고 33개 + 장 시작 5봉 conf=0% (FLAT 수렴)
- `macro_risk_off` = 이진(0/1) 피처인데 장 시작 급락 시 z=+15.78σ 폭발
- 근본 원인: warmup 500봉이 risk_off=0 전부 → D_FORCE 재적합 시 risk_off=1 봉 1~2개 추가 → raw_std=0.063 > identity 강제 임계(0.05) → identity 해제 → ScaleFloor 미등록 → z 폭발
- 192차에서 AutoMask CORE 면제 추가 시 ScaleFloor 등록을 함께 했어야 했는데 누락
- D_FORCE가 macro_risk_off 이상 z로 재트리거 → 재적합 → 여전히 이상 z 악순환 확인
- WarmupRetrain GBM 미실행: 예약 로그만 있고 서브프로세스 시작 없음, retrain_intraday_20260624 미생성
- EKS 동적 회복 로직 확인: 09:20 첫 시도, 30분 간격 최대 5회, 11:30 마감
- EKS 커밋 이력: 86차 최초 → 177차 z조건 완화(5→15) → 203차 stale z_warn 고착 버그 수정

**수정 (4종)**:
- `model/multi_horizon_model.py` `_MACRO_SCALE_FLOOR`: `macro_risk_off/on/event_flag` floor=0.50 추가
  - 이진 피처 이론 최대 σ=0.5 → floor=0.5 → z ≤ 2.0 보장
- `main.py` L5309: EKS 해제(`try_eks_recovery()=True`) 직후 GBM 경량 재학습 즉시 트리거
  - 장전 기동 + EOD 성공 스킵으로 WarmupRetrain 미실행 시 EKS 해제 후 당일 데이터 반영 공백 해소
- `main.py` L7317: `daily_close()` 완료 즉시 `_exit_normally` 플래그 생성 (Qt 타이머 누락 방지)
- `start_mireuk_Cybos.bat` L270: GUARD 시각 분기 — 장전 자동 Y / 장중 사용자 직접 선택

**커밋**: 232차 (4238538), 232차-b (ca55a8c), 233차 (3d33950, 이번 세션)

---

## 2026-06-23 (231차 — EOD 점검 + macro/ScalerWarmup/피처셋 3종 수정)

**Work**: EOD 로그 이상점 분석 → 3종 버그 수정 + 피처 활성화/삭제 + 문서 정비.

**분석 발견**:
- EOD Python 환경 `3.10 64-bit` → 의도적 설계 확인 (226차 py310_64 이관, CLAUDE.md 미반영이었음)
- `macro_sp500_chg` 장중 간헐적 0 (11:59~12:02, 14:09~14:11, 15:03~15:04) — Yahoo daily prev 미취득 시 0 강제
- `ScalerWarmup feat=120` vs GBM 학습 `feat=97` 불일치 — DB 최대 키 봉 기준으로 X 구성해서 발생
- need_add 피처 중 threshold_feasibility(5,101행), queue_directional_depletion(4,253행) 이미 4,000행 초과 → 5일·3일 지연 미활성화 상태
- bull_exhaustion_signal 2행(0.0%), bull_reversal_signal 145행(0.2%) — 즉시 삭제 대상
- bear_reversal_signal: 191차 삭제 처리됐으나 JSON include에 미반영 상태
- 매크로 Phase A 이후(06-16~) 수집 정상 (VIX 96~100%, src=4.0) / 프리장 13행 NULL 구조적

**수정 (3종)**:
- `collection/macro/macro_fetcher.py`: `_last_chg` 캐시 추가 — prev 미취득 시 0 강제 → 마지막 성공값 재사용
- `learning/batch_retrainer.py` `load_features_for_warmup()`: feature_names.pkl(97개) 우선 로드 → X(500,97) 직접 구성 (120→97 재정렬 로직 스킵)
- `featureset by horizon/horizon_feature_sets.json`: threshold_feasibility·queue_directional_depletion 활성화, bear/bull_reversal_signal·bull_exhaustion_signal 삭제

**문서 정비**:
- `CLAUDE.md`: Python 환경 테이블 py37_32(런타임)/py310_64(재학습) 분리 + 이유 설명 추가
- `dev_memory/DECISION_LOG.md`: 226차 GBM 64비트 이관 결정 기록
- `docs/260617_FEATURE_ADD_TIMING_REPORT.md`: 오늘 활성화/삭제 현황 반영

**커밋**: 231차 (이번 세션)

---

## 2026-06-23 (229차 — X 버튼 종료/재시작 선택 + 이중 인스턴스 방지 완성)

**Work**: 이중 subprocess 원인 규명 → 런처 이중 실행 + X 버튼 재시작 흐름 정비.

**분석 발견**:
- 이중 인스턴스 원인: `launcher_20260623_115926` (11:59 시작)가 14:58:30까지 실행 중인 상태에서 사용자가 14:09:15에 새 런처 수동 실행 → 두 main.py 공존
- UI X 클릭 → Python exit(0) → 런처 파이프 구조(python | powershell) 때문에 ERRORLEVEL이 항상 0 → 런처가 정상/비정상 구분 불가 → 무조건 RESTART_LOOP
- 사용자: "창 닫았으니 종료된 줄 알고" 스케줄러 클릭 → 런처 #2 → 이중 인스턴스
- 배치창 X = CTRL_CLOSE_EVENT → Python 강제 종료 (closeEvent 없음, 포지션 청산 보장 없음)

**수정 (229차 3개 커밋: 6bd1014, bc97fa3, 3fbb292)**:
- `dashboard/main_dashboard.py` closeEvent: 3-way 다이얼로그 추가
  - "완전 종료" → `_exit_normally` 플래그 생성 → 런처 종료
  - "재시작 (10초 후)" → 플래그 없음 → AUTO-RESTART 유지
  - "취소" → 거래 계속
- `main.py` `_write_exit_normally_flag()` 신설, `_auto_shutdown()`에 연결
- `start_mireuk_Cybos.bat` RESTART_LOOP 직후 `_exit_normally` 체크 → 정상 종료 시 재시작 안 함
- `start_mireuk_Cybos.bat` 시작 시 잔류 플래그 정리 + psutil 단일 인스턴스 가드(228차-c)

**올바른 종료-재시작 흐름 (229차 이후)**:
- 완전 종료: 미륵이 UI X → "완전 종료" → 런처 자동 종료 (배치창 X 불필요)
- 장중 재시작: 미륵이 UI X → "재시작 (10초 후)" → 10초 후 자동 재기동
- 배치창 X: 비상 강제 종료 전용 (포지션 청산 보장 없음, 정상 운영 중 사용 금지)

**커밋**: 229차 (6bd1014·bc97fa3·3fbb292)

---

## 2026-06-23 (228차 — ExchangeCB 미감지 버그 수정)

**Work**: 금일 14:34~14:58 거래소 CB 24분간 ExchangeCB 모드 미발동 원인 분석 → 수정.

**분석 발견**:
- `_try_pipeline_recovery()` 복구 스킵 경로(line 7515)에 `notify_pipeline_ran()` 존재
  → 워치독 타이머 90초마다 리셋 → elapsed_s 항상 90s → 300s(ExchangeCB 임계) 영구 미도달
- 금일 14:34:30 복구 성공 후 14:34~14:58 24분간 ExchangeCB 미진입, 매 90초 Slack 도배
- 단일가 tick 14:33:35~42에 ts=14:33:00으로 수백 개 쏟아짐 (파이프라인 영향 없음)
- CB④ ATR 3.5배 → 5분 정지, AutoMask, X등급 정상 작동
- 14:59 즉시 재크래시(2회): 추정 원인 OptionChain 3초 블로킹 + CB 특수 상태 조합
- PnL=+1,399,653원 복원 (10건 거래, FLAT 포지션)

**수정 (228차 68b6095)**:
- `__init__`: `_last_real_pipeline_dt` 신설 — 실제 분봉 완료 시각(복구 스킵·가드 제외)
- `run_minute_pipeline()` 말미: `_last_real_pipeline_dt = datetime.datetime.now()` 갱신
- `_try_pipeline_recovery()` 복구 스킵 경로: `notify_pipeline_ran()` 제거 → 워치독 자연 누적 허용
  + `_real_elapsed > 600s` 시 ExchangeCB 강제 진입(안전망)
- `_on_pipeline_watchdog()`: `elapsed_s` vs `_real_gap` 중 큰 값으로 ExchangeCB 판단
- `_try_pipeline_recovery()` `age_s > 600` 경로: 장중이면 ExchangeCB 자동 진입

**커밋**: 228차 (68b6095)

---

## 2026-06-23 (227차 — 거래소 서킷브레이커 CB 재개 대응 강화)

**Work**: 금일 KOSPI CB 1단계(8% 하락, 14:14~14:34 30분 거래 중단) 로그 분석 → 대응 로직 개선.

**분석 발견**:
- 226차 GBM-64: 14:34:30 `[GBM-64] 64비트 서브프로세스 재학습 시작 pid=8932` 정상 작동 확인
- ExchangeCB 모드 미감지: 14:14~14:34 분봉 없음인데 `[ExchangeCB]` 로그 없음 (이중 인스턴스 watchdog 혼선)
- 이중 인스턴스: 14:09:34 + 14:09:43 두 번 재시작 → 모든 LEARNING 로그 두 줄씩
- CB PAUSED at 14:34 (CB⑤ 파이프라인 지연), 14:39 해제 정상 복귀
- `_post_exchange_cb_resume()`에 GBM 재학습 없음 → CB 후에도 구형 모델 유지

**수정 (227차 ae41af1)**:
- `_post_exchange_cb_resume()`: ⑥ GBM 재학습(`_start_gbm_retrain_subprocess`) ⑦ CB③ 쿨다운 30샘플 ⑧ 워치독 리셋 추가
- ExchangeCB 진입 시 `set_gbm_retrain_active(True)` → CB⑤ 임계 완화
- ExchangeCB 해제 시 `set_gbm_retrain_active(False)` 복원

**커밋**: 227차 (ae41af1)

---

## 2026-06-23 (226차 — GBM 재학습 64비트 subprocess 이관)

**Work**: 12:00 재시작 후 로그 점검 → OOM 반복 확인 → subprocess 이관.

**분석 발견**:
- 225차 P0(sigma) 수정 완전 성공: 12:02~ nonzero=1, 12:06~ sigma_at_t=0.0466%
- 225차 P1(deferred 큐) 완전 성공: 12:24 `[ConstOut] 재적합 완료 → acc30m 버퍼 리셋` 정상 출현
- CB③ 재시작으로 초기화 → 13:00 LONG 진입 확인
- OOM 패턴: 12:01·12:24·12:54·13:29·13:52 전부 `Unable to allocate 14.8 MiB (39876×97 float32)` — 32비트 단편화
- GBM 모델 미교체 → 30m ConstOut 반복 → sigma=0 시절 학습된 구형 모델 유지

**수정 (모두 226차 054c21d)**:
- `retrain_intraday.py` 신규: py310_64 전용 재학습 스크립트 (argv: result_json force intraday)
- `config/settings.py`: `PYTHON_64_EXEC` 상수 추가
- `main.py`: `_start_gbm_retrain_subprocess()` 헬퍼 신설
- `main.py`: PreRetrain·WarmupRetrain·STEP3·_start_manual_retrain 4곳 모두 subprocess 이관
- `main.py` S0-A: `subprocess.poll()` 완료 감지 → `_on_gbm_retrain_done()` 직접 호출
- `main.py` S0-B: deferred_callbacks 큐는 `const_out_done` 전용 유지

**커밋**: 226차 (054c21d)

---

## 2026-06-23 (225차 — sigma=0 버그·QTimer daemon thread 미전달·CB③ 재트리거 3종 수정)

**Work**: 20260623 장중 로그(LEARNING + SYSTEM) 딥다이브 → CB③ 종일 HALT 미해제 원인 3종 발굴·수정.

**분석 발견**:
- `sigma_at_t=0.0000% nonzero=0` 종일 지속: `_on_tick_price_update()`가 파이프라인 진입 전 `_last_pipeline_price`를 현재봉 close로 덮어써 ret=0 고착
- QTimer daemon thread 미전달: SYSTEM.log에 `[GBM] 배치 재학습 완료` 미등장 → GBM worker 4곳 + ConstOut worker 모두 콜백 미실행 확인
- CB③ 재트리거: 10:15 refit → reset_acc30m_buffer() 미호출 → 7샘플 만에 10:22 즉시 재HALT
- 오늘 CB③ HALT 10:22 발동 후 11:30 이후까지 미해제 (lift_cb3_halt() 미호출)
- 30m acc30m: 0%(0/30) 종일 유지, Contrarian 11:02 ACTIVE, Brier 패널티 11:19 발동

**수정 (모두 225차 58b3c1b)**:
- `main.py`: `self._sigma_prev_price` 전용 변수 신설 + 파이프라인 말미 커밋 (sigma=0 수정)
- `main.py`: GBM worker 4곳 + ConstOut worker 1곳 QTimer → `_deferred_callbacks` 큐 교체
- `main.py`: S0 시작에 큐 drain 블록 추가 + 15분마다 CB③ 재시도 추가
- `circuit_breaker.py`: `_cb3_reset_cooldown_samples=15` 쿨다운 신설
- `main.py`: GBM 재학습 타임아웃 1800s → 600s 단축

**커밋**: 225차 (58b3c1b)

---

## 2026-06-23 (224차 — SGD 붕괴 복구 임계 완화 + BiasReset 연계 SGD 리셋)

**Work**: 오늘 5m DN 편향 흐름 로그 분석 → 2개 구조적 문제 발견·수정.

**분석 발견**:
- 5m DN=83% 편향에서 SGD 붕괴 자동복구 미발동: SGD 출력이 95% 임계에 미달 (5m는 극단 확신을 잘 찍지 않는 특성)
- 09:58 BiasReset 발동 후 `boost_sgd_for_bias`가 오염된 파라미터 상태에서 UP 고착 → 10:03~10:19 conf=34.0% UP 연속 실패
- 4일치 로그 분석: 발동 케이스 11건 Bias% 최솟값 76%, 평균 87.4% → 80% 임계에 4%p 마진 확보

**수정**:
- `online_learner.py`: `_COLLAPSE_THR=0.80`, `_COLLAPSE_TICKS=12` 클래스 상수로 분리 (하드코딩 제거)
- `online_learner.py`: `_do_sgd_reset()` 공통 메서드 추출, `reset_sgd_for_bias()` 신규 추가
- `main.py` L3545: `boost_sgd_for_bias` → `reset_sgd_for_bias` 교체 (가중치 boost → 전체 리셋)

**커밋**: 224차 (c9c2d74)

---

## 2026-06-23 (223차 — BiasReset uniform fallback 고착 버그 수정)

**Work**: 장중 10m·3m FL편향 고착 원인 분석 → 2개 연쇄 버그 발견·수정.

**분석 발견**:
- BiasReset 발동 시 `_bias_buf`를 클리어하지 않아 FL 26건 잔존 → 해제 조건 영구 미달
- uniform fallback 후 `direction=0` 예측이 10분 뒤 verified될 때 FL로 카운트 → 해제 불가 무한루프
- 오늘 09:42 발동 후 `[Bias⚠]` 경고가 장중 내내 반복 출력되고 앙상블에서 10m이 uniform으로 고착됨

**수정**:
- `main.py` BiasReset 발동 시 `_bias_buf[h].clear()` + `streak=0` + `timer=20` 추가
- `main.py` bias_override active 호라이즌의 `_bias_buf` 기록 스킵
- `main.py` 20분 자동 해제 타이머 (`_bias_override_timer`) 신설 — 타이머 0 도달 시 override 해제
- GBM 재학습·일간 리셋 함수에 `_bias_override_timer` 초기화 추가

**오늘 거래 결과**: 1차 +760,602원(TP1+TP2) / 2차 -92,184원(하드스톱) → 누적 **+668,418원**

**커밋**: 223차 (ca33da8)

---

## 2026-06-23 (222차 — EOD 마커 파일명 불일치 + retrain_str NameError 수정)

**Work**: 장전 점검 중 PreRetrain 불필요 발동 원인 추적 → 2개 버그 발견·수정.

**분석 발견**:
- `retrain_eod.py`는 `strftime("%Y%m%d")` (하이픈 없음: `20260622`), `main.py`는 `isoformat()` (하이픈 있음: `2026-06-22`) 불일치로 마커 파일을 항상 못 찾음 → 매일 PreRetrain 강제 발동
- `daily_close()` notify() f-string에 `retrain_str` 정의 누락 → 어제 15:40 NameError로 DailyClose 비정상 종료
- 두 버그 독립적: NameError가 없었어도 하이픈 불일치로 동일하게 PreRetrain 강제 발동

**수정**:
- `main.py pre_market_setup() ~L3015`: `_prev.isoformat()` → `_prev.strftime('%Y%m%d')`
- `main.py daily_close() ~L6805`: `datetime.date.today().isoformat()` → `datetime.date.today().strftime('%Y%m%d')`
- `main.py daily_close() ~L7127`: `retrain_str` 정의 추가 (`_eod_retrain_ok` 참조)

**커밋**: 222차

---

## 2026-06-22 (221차 — BlockRequest 레이스 컨디션 분할체결 qty 누락 방어)

**Work**: 14:46 매도진입 후 14:56 재진입이 "청산 전 재진입"인지 딥다이브 → 레이스 컨디션 버그 확정·수정.

**분석 발견**:
- 14:56 재진입은 14:52 청산 완료 후 쿨다운 경과된 정상 B등급 신호 (버그 아님)
- 14:46에서 `[Position] 진입 SHORT` 로그 없이 Chejan이 먼저 처리되는 레이스 컨디션 발생
- Cybos BlockRequest가 COM 이벤트 루프 pump → `open_position()` 전에 Chejan 4회 선행 처리
- 보정 분기 조건(`optimistic_opened=True, status==SHORT, _optimistic=False`)이 2번째+ 체결에서 True
  → VWAP만 업데이트, qty 증가 없음 → 오늘은 1계약 실체결이라 무해, 실전 전량체결 시 qty 불일치 위험
- 단순 `quantity += fill_qty` 수정은 정상 케이스 4계약→7계약 이중 카운팅 발생하므로 기각

**수정**:
- `main.py _ts_execute_entry FixB ~L10299`: `open_position()` 성공 후 `_pending_order["open_position_done"] = True`
- `main.py _ts_handle_entry_fill_cybos_safe 보정 분기 ~L10397`: 조건에 `pending.get("open_position_done")` 추가
  → False(레이스 컨디션) 시 else→apply_entry_fill 증량 경로로 qty 올바르게 누적

**커밋**: `9ad777c` (221차)

---

## 2026-06-22 (220차 — 15:10 강제청산 FLAT불일치 버그 + 15:18 FINAL_CLOSE 안전망)

**Work**: 15:20 Cybos 잔고 3계약 미청산 사고 분석 → 로그 딥다이브 → 2개 버그 확정·수정.

**분석 발견**:
- 14:56 진입 3계약, 14:58~15:00 3×1계약 순차 청산 → ChejanFlow 체결 확인 → 시스템 FLAT 착각
- Cybos 잔고 15:00:39에 여전히 `잔고수량=3` 반환 (모의투자 잔고 지연 or 첫 번째 4계약 진입 잔여분)
- 15:10 `should_force_exit()` 발동 → `_send_broker_exit_order(qty=0)` → FLAT 가드 `-1` 반환 → 무효
- 14:46 진입: Cybos BlockRequest COM 이벤트 루프 pump → Chejan이 `open_position()` 보다 먼저 실행 (레이스컨디션) → qty=1 고착 → 1계약만 체결됐으므로 정상 완료 (오늘은 사고 無)

**수정**:
- `time_exit.py`: `should_final_close()` 추가 (15:18 FINAL_CLOSE 방어선)
- `main.py __init__`: `_final_close_done` 플래그
- `main.py _ts_broker_direct_force_exit`: 신규 함수 — `request_futures_balance` 직접 조회 후 `send_market_order` (FLAT 가드 우회)
- `main.py _ts_check_exit_triggers:8174`: 15:10 강제청산 — `_integrity_broker_qty` 폴백 + FLAT 시 BrokerDirect 분기
- `main.py _check_exit_triggers:6248`: 분봉 기반 경로 동일 패턴
- `main.py _ts_check_exit_triggers:8222`: 15:18 FINAL_CLOSE 블록

**커밋**: `f412df8` (220차)

---

## 2026-06-22 (219차 — 브로커 잔여계약 PnL 누락·Sizer 잔고·TRADE 로그 3버그 수정)

**Work**: 실시간 잔고 패널 이상점 딥다이브 → CpTd6197 헤더 원시값 + TRADE 로그 교차분석으로 3버그 확정·수정.

**분석 발견**:
- `CpTd6197 header 6` = -96,999원(브로커 실현손익), 엔진 누적 = -353,129원
- 13:28→13:33 사이 브로커 +485,500원 변화(2계약분) vs 엔진 +240,528원(1계약분) → Chejan 콜백 1회 누락 확인
- `header 7` = 미실현 손익(포지션 없으면 0), `header 8` = header6+header7
- `총평가수익률`(header2=익일예탁금)이 Sizer 잔고 소스로 설계됐지만 `총매매`(예탁금)가 앞에 있어 항상 정적값 반환

**수정**:
- `main.py` Bug1: 잔여계약 `close_position("stuck_exit_remainder")` → trades DB·PnL 탭 기록
- `main.py` Bug2: `_ts_extract_sizer_balance` 키 순서 `총평가수익률→총매매→추정자산`
- `main.py` Bug3: blank-as-flat 강제 경로에 `log_manager.trade("[BrokerSync] blank-as-flat 강제:...")` 추가

**커밋**: `4d2b8bf` (219차)

---

## 2026-06-22 (218차 — DriftRetrain 32-bit OOM 수정 + 재시도 쿨다운)

**Work**: 장중 DriftRetrain이 17회 연속 즉시 실패해 CB③ HALT까지 이어진 구조 버그 수정.

**원인 확정**:
- `_load_from_db()` 내 `np.array(39880, 97, float32)` = 14.8 MiB 연속 블록 할당 실패 (32-bit OOM)
- 기존 20,000행 슬라이싱이 np.array 생성 이후에 위치해 실효 없음
- 실패 시 `_last_retrain` 미갱신 → 다음 분 조건 즉시 재충족 → 무한 루프

**수정**:
- `learning/batch_retrainer.py`: `_load_from_db(intraday=)` 파라미터 추가 + CUSUM 후 np.array 전 레코드 사전 제한
- `main.py`: `_drift_retrain_last_attempt` 추가 + 조건A/B에 5분 쿨다운

**커밋**: `f2cb738` (218차)

---

## 2026-06-22 (217차 — 호라이즌 자격 조건 수정 + GDI 크래시 방지 + 런처 자동 재시작)

**Work**: 호라이즌 자격 현황 1m/3m/10m 영구 WAIT 원인 분석 및 수정, 장중 재시작 시 GDI 크래시 방지, 런처 자동 재시작 루프 추가.

**원인 확정**:
- 1m/3m WAIT: SGD conf 필터 0.52가 단기 호라이즌 전량 차단 → trained_cycles=0 → 영구 WAIT
- 10m WAIT: BAR_CACHE_DECAY(0.93^age) 추가 감쇠 → trained_cycles=1
- GDI 크래시: ui_prefs.json `w=3030, h=1460` → DPI 150% → 물리 DIB 38.6 MB → 32-bit 단편화로 CreateDIBSection FAILED
- 런처: crash 후 자동 재시작 없음, 로그 한글 UTF-16 깨짐

**수정**:
- `config/settings.py`: `HORIZON_QUALIFY_MIN_TRAINED = {"1m":0, "3m":0, "10m":1, "5m":3, "15m":3, "30m":3}`
- `main.py`: 자격 판정 2곳에 `_need_trained` 호라이즌별 분리 적용
- `dashboard/main_dashboard.py`: `_CHART_MAX_LOGICAL_W/H=1920/1060` 상수 + restore/close/paintEvent 3중 가드
- `data/ui_prefs.json`: `w=3030→1920, h=1460→1060` 즉시 교정
- `start_mireuk_Cybos.bat`: 장중 자동 재시작 루프(최대 5회, Cybos 재연결 포함) + PYTHONUTF8=1

**커밋**: `752a8c9` (217차)

---

## 2026-06-22 (216차 — CB③ HALT 원인해소 후 거래 재개)

**Work**: CB③(30분 정확도 저하) HALT 후 ConstOut 스케일러 재적합 + GBM 재학습이 완료돼도 거래가 재개되지 않는 구조 결함 수정.

**원인 확정**:
- `_trigger_halt()` 호출 시 HALT 원인 코드를 저장하는 필드 없음
- `reset_acc30m_buffer()`는 acc 버퍼만 지우고 `_state` 변경 없음
- HALT 해제 경로가 `reset_daily()`(다음 날) 외에 없어 당일 거래 영구 불가

**수정**:
- `circuit_breaker.py`: `_halt_cause` 필드 + `_trigger_halt(cause=)` 파라미터 + `lift_cb3_halt()` 신규 메서드
- `main.py`: `_on_gbm_retrain_done` 성공 블록에 `lift_cb3_halt()` 호출
- CB② (연속 손절) HALT는 해제 불가 보호, daily_halt_count ≥ 3 시 완전 관망 정책 유지

**커밋**: `059bbe4` (216차)

---

## 2026-06-22 (215차 — minute_chart 예외 가드 + 좌측패널 카드 업데이트 불가 근인 확인)

**Work**: 좌측패널 `DirectionIndicatorWidget`/`ConfTrendWidget` 종일 업데이트 안 되는 문제 로그 분석.

**원인 확정**:
- 1차 세션(09:00~10:32): `AttributeError: 'DashboardAdapter' has no attribute 'minute_chart_set_direction'` 매분 → STEP9 미도달 → DB 0건 → 위젯 데이터 없음
- 두 위젯 자체는 정상 (DB에 데이터 있으면 정상 갱신)

**수정**: `run_minute_pipeline` 내 `minute_chart_set_regime`/`set_direction` 호출을 try-except로 감쌈 (차트 갱신 실패가 파이프라인 차단 방지)

**커밋**: `1b2bbcd` (215차)

---

## 2026-06-22 (214차 — ERR-FATAL 수정 + 프리장 Phase 재설계 + RT 08:45 선행구독)

**Work**: 6/22 장초반 로그 분석 → ERR-FATAL 매분 반복(자동진입 영구 차단) 수정 + 201차 프리장 Phase 실측 결과 반영 재설계.

**원인 확정**:
- P0: 210차에서 `main.py` 호출 추가했으나 `DashboardAdapter` 어댑터 등록 누락 → 매분 ERR-FATAL
- P1: Cybos RT 구독 08:55 시작 → 최대 4~6봉 수집 → Phase3·4 발동 불가
- P1: 1봉 refit 역효과 실측 (z경고 6→14개)
- P2: paintEvent 15-16ms가 정상인데 WARN 수백 건 출력 (103KB)

**수정**:
- `DashboardAdapter.minute_chart_set_direction` 바인딩 추가
- `PRE_MARKET_REFIT_STEPS`: `{1,5,10,14}` → `{3,5,10,14}`
- EarlyWarmup 트리거 직후 Cybos RT `realtime_data.start()` 08:45 선행 호출
- `_pm_refit_worker` z경고 악화 감지 WARNING 로그
- ChartDBG paintEvent 임계 10ms → 30ms

**커밋**: `995a2d4` (214차)

---

## 2026-06-19 (211~213차 — 차트 복원 완전 해결 + 5종 개선)

**Work**: 자동팝업 재시동 시 차트 창이 DPI 1.5×로 비정상 확대되는 근본 원인을 로그 분석으로 확정, 음수 y 좌표 차단으로 해결. 5종 별도 개선 커밋.

**근본 원인 확정**:
- `QWindowsWindow::setGeometry: Unable to set geometry 3030x1460+3369-8 → 4547x2124`
- 보조 모니터 avail.top()=-7에서 y=-7(=avail.top())로 setGeometry 호출
- Qt 프레임 계산 중 y=-8로 변환 → avail.top()=-7 밖 1px → Windows DPI 가상화 발동
- Python 3.7 32-bit(96DPI) + 144DPI 보조모니터 → 3030×1.5=4547, 1460×1.5=2190

**212차 핵심 수정**: `y<0` → `y=0` 보정 (restore_saved_geometry + _center_on_second_screen)

**213차 추가 수정**:
- model/multi_horizon_model.py: 스케일러 pickle.dump(protocol=4) (joblib 내부 BYTEARRAY8=opcode63 → Python 3.7 KeyError 크래시 수정)
- learning/calibration.py: protocol=4 통일
- dashboard/panels/conf_trend_widget.py: ConfTrend 디버그 로그 WARNING→DEBUG (30초마다 6개 WARNING 오염 수정)
- dashboard/panels/dynamic_mc_panel.py: 대규모 정리 (-533 lines)
- start_mireuk_Cybos.bat: 런처 로그 자동 저장 (logs\Mireuk_batch\, 최신 10개 보관)

**커밋**: 211차(27dafe1) 212차(76d14b6) 213차(0274cd4)

---

## 2026-06-19 (210차 — 1분봉 차트 X축 방향예측·레짐 레인 구현)

**Work**: `MinuteChartCanvas` X축 위에 방향예측 레인(UP/DOWN/FLAT, 현재봉 빈칸)과 레짐 레인(추세/횡보/급변/혼합/탈진) 두 개의 색상 바 추가. 팝업 봉차트(`CandleChartDialog`)에도 동일 구현.

**변경**:
- `main_dashboard.py`: `_dir_map`, `set_direction_at()`, `_draw_direction_bar()` 추가; 세션 복원 2곳에 `_dir_map` 복원; `minute_chart_set_direction()` 퍼블릭 메서드
- `utils/db_utils.py`: `fetch_direction_today()` — `ensemble_decisions → {ts: int}`
- `main.py`: STEP6 앙상블 방향 확정 직후 `minute_chart_set_direction(ts, direction)` 호출
- `candle_chart_dialog.py`: 3-axes matplotlib 레이아웃, `_fetch_candle_decisions()`, 시그널 4인자

**재시작 복원**: `ensemble_decisions` 테이블에서 당일 전체 복원 (`fetch_direction_today`)

**커밋**: 210차 (2e9b9f0)

---

## 2026-06-19 (208차 — 좌측 패널 멀티 호라이즌 예측 카드 제거)

**Work**: 좌측 패널에서 6개 호라이즌 예측 카드(▲/▼/%) 제거, On/Off 체크박스만 유지.

**변경**:
- `hz_title` 레이아웃에서 제거
- 6개 QFrame 예측 카드 → hgrid 미표시 (update_data 내부 참조만 보존)
- `cb_wrap`: HBox→VBox, 이름 레이블 추가, row 0으로 이동
- `_model_row` 레이아웃에서 제거 (위젯 객체 보존)

**커밋**: 208차 (3c7af18)

---

## 2026-06-19 (207차 — 1분봉 차트 닫기·재열기·재시동 복원 4종 수정)

**Work**: 14:29 장중 재시동 후 차트 데이터 미복원 + 윈도우 위치 미복원 딥다이브 → 근본 원인 2개 확정 → 전체 복원 흐름 재설계.

**근본 원인**:
1. **데이터 미복원**: `_reload_today_bg()`(threading.Thread)에서 `QTimer.singleShot(lambda)`가 Qt 이벤트 루프 없는 배경 스레드에 귀속 → 영원히 발동 안 됨 → `_apply_reload_result()` 미호출 → 빈 차트
2. **geometry 미저장**: `MireukDashboard.closeEvent()` 미존재 → 메인 종료 시 Qt 부모-자식 소멸 경로로 `MinuteChartDialog.closeEvent()` 미호출 → `chart_dialog_geometry` 미저장
3. **자동팝업 geometry 무시**: `auto_popup=True` 경로가 `_center_on_second_screen()` 고정이었음

**수정 내용**:
- `pyqtSignal(list, list, list) _sig_reload_done` 클래스 속성 추가 → cross-thread 안전 전달
- `_reload_today_bg`: `QTimer.singleShot(lambda)` 완전 제거 → `_sig_reload_done.emit()` 교체
- `_apply_reload_result()`: `reset_session` + `_regime_map` 복원 + `_post_reload_hook` 원자 처리
- `_start_reload_thread()`: `_reload_running` 플래그로 동시 실행 방지
- `toggle_minute_chart_dialog()`: 재열기 시 `_start_reload_thread()` 추가 + 항상 `restore_saved_geometry()` 사용
- `MireukDashboard.closeEvent()` 신규 추가: `_minute_chart_dialog.close()` 명시 호출
- `_post_reload_hook` + `set_minute_chart_post_reload_hook` 어댑터 → 재시동 active position 마커 복원
- `main.py`: `_chart_reload_hook` 등록

**커밋**: 207차 (240e9c6)

---

## 2026-06-19 (206차 — poc_distance z폭발 근본 수정: VP 버퍼 DB 복원)

**Work**: 장중 재시작 후 poc_distance z폭발 원인 딥다이브 → VP 버퍼 cold-start 구조 확정 → DB 복원으로 근본 수정.

**원인 확정**:
- `VolumeProfileCalculator` 버퍼가 재시작 시 항상 빈 상태로 초기화
- `_restore_analysis_buffers()`이 SHAP/Corr는 복원하나 VP 버퍼 복원 경로 없음
- 재시작 후 bars 1~9: poc_distance=0.0, bars 10~59: 짧은 윈도우 POC 불안정
- 스케일러 std(0.00417)가 cold-start 0.0값 오염으로 낮게 학습 → z 임계 낮음
- z>4 조건: poc_distance > ±0.0167 = KOSPI 200 기준 ±5.5포인트 이격

**수정 내용**:
- `utils/db_utils.py`: `fetch_recent_raw_candles(limit=60)` 신규 추가
- `main.py` import: `fetch_recent_raw_candles` 추가
- `main.py` `_restore_analysis_buffers()`: VP 버퍼 복원 블록 추가 (raw_candles 60봉 → `_vol_profile.update()`)

**Fix 2(clip) 기각**: Fix 1 이후 남는 z>4 = 진성 시장 신호 → 클리핑 시 신호 손실. 이득 없음.

**커밋**: 206차

---

## 2026-06-19 (205차 — 5m FL편향·30m acc 10%·SGD 15% 악순환 4종 수정)

**Work**: 장중 5m FL편향 80% 지속 + 30m 정확도 10% (DriftRetrain 발동) + SGD 15% 동시 발생 딥다이브 → 구조적 악순환 4종 수정.

**원인 확정**:
- DriftRetrain 완료 후 BiasReset·SGD 상태가 구 GBM 기준 그대로 남아 재학습 효과 무산 (버그)
- SGD CUT_THR 30m=0.52 — 30m는 랜덤워크에 근접해 구조적으로 달성 불가 → 매분 -0.02씩 바닥 수렴
- DriftRetrain 60분 대기 — acc=10% 극단 혼란에도 조기 대응 불가
- PATH_LABEL_RATIO 전역 0.55 — 30m 훈련 데이터에서 FL 레이블 과소 → GBM UP/DN 과잉 예측

**수정 내용**:
- `main.py` `_on_gbm_retrain_done`: 재학습 성공 시 `_bias_override_horizons` 클리어 + `reset_daily()` 추가
- `online_learner.py`: `_CUT_THR["30m"]` 0.52 → 0.42
- `main.py` DriftRetrain: 조건B 추가 (acc<15% + n>=15 + 30분 → 조기 트리거)
- `batch_retrainer.py`: `PATH_LABEL_RATIO_BY_HZ` dict 추가 (1m~30m 호라이즌별 분리, 두 호출 위치 적용)

**커밋**: 205차 (`aca776c`)

---

## 2026-06-19 (204차 — ConfTrend refresh 장 후반 지연 근본 수정)

**Work**: ConfTrendWidget.refresh가 09:31 280ms → 11:53 2297ms로 선형 악화 → 원인 3개 확정 후 수정.

**원인 확정**:
1. **step3 906ms** — 매 30초마다 `sqlite3.connect()` 신규 연결 생성. WAL 파일이 하루종일 누적(기본 wal_autocheckpoint=1000페이지)되어 연결 오픈 시 WAL 헤더 파싱 비용이 선형 증가
2. **step2 343ms (trades DB)** — `substr(entry_ts,1,10)=?` 함수 적용으로 `idx_entry_ts` 인덱스 미사용 → 풀스캔
3. **step2 증가분 (log 파일)** — 매 30초마다 TRADE.log 처음부터 전체 재읽기. 장 후반 ~170분치 누적으로 O(N) 증가

**수정 내용**:
- `utils/db_utils.py`: `PRAGMA wal_autocheckpoint=100` — WAL 100페이지마다 체크포인트(기본 1000 → 100)
- `conf_trend_widget.py/_get_pred_conn()`: PREDICTIONS_DB 영구 read 연결 (인스턴스 수명 내 1회만 연결, 오류 시 재연결)
- `conf_trend_widget.py/_completed_from_db()`: `substr(entry_ts,1,10)=?` → `entry_ts >= ? AND entry_ts < ?` (idx_entry_ts 활성화)
- `conf_trend_widget.py/_completed_from_log()`: `_log_offset` / `_log_cache` 캐싱으로 신규 라인만 증분 읽기

**예상 효과**: step2 ≈0ms, step3 ≈30ms 이하로 장 후반까지 유지

**커밋**: 204차

---

## 2026-06-19 (203차 — EKS z_ok 영구 차단 버그 수정)

**Work**: 6/19 장중 EKS 회복 불가(`z_ok=False(z=18)` 5회 반복) 원인 딥다이브 → 1줄 수정.

**원인 확정**:
- Canary 블록이 `pre_market_setup()` 안에 있어 **08:55 1회만** 실행됨
- 이 시점(전날 스케일러 기준) z=18 → `_last_canary_z_warn = 18` 저장
- PreMarket refit 완료 후 실제 z=4로 줄었지만 `_last_canary_z_warn`은 절대 갱신되지 않음
- EKS 회복 평가에서 이 stale 값을 사용 → `z_ok = 18 < 15 = False` → 회복 불가
- 반면 SHS `_z_warn_count`는 매분 파이프라인에서 4로 정상 갱신 중 (두 경로 분리 버그)

**수정 내용**:
- `main.py:5054`: `getattr(self, "_last_canary_z_warn", 0)` → `getattr(self.model, "last_z_warn_count", 0)`
- `safety/system_health.py:185`: 독스트링 `< 5` → `< 15` 불일치 수정

**오늘 장 관찰 사항**:
- EKS 발동 09:05, 회복 시도 5회(09:20~11:24) 모두 z_ok=False(z=18)로 실패
- conf_hits=10/10 (필요 3), scaler_ok=True 충족 — z_ok만 막고 있었음
- ConfTrendWidget.refresh slow: 281~2297ms (장 후반 step3+step4 병목)
- 5m FL편향 80%, 30m 정확도 10% → DriftRetrain 경량 재학습 11:52 발동

**커밋**: 203차

---

## 2026-06-19 (201차 — 프리장 갭오픈 즉시 반영 점진 scaler 재적합)

**Work**: 6/19 장초반 EKS 발동(conf_max=0.0%, bars=5) 원인 딥다이브 → 근본 수정 구현.

**원인 확정**:
- `_on_pre_market_bar()`가 피처를 계산하면서 `raw_data.db`에 저장하지 않음
- EarlyWarmup·Canary refit·PreMarket refit 모두 `load_features_for_warmup()` → 전날 DB만 읽음
- 갭오픈 이후 분포가 재적합에 전혀 반영 안 됨 → z경고 18개 → conf≈50% → EKS
- 104차(EarlyWarmup 도입)부터 177차(EKS z=15 완화)까지 7세대 Escape 패턴의 종착지

**핵심 수정**:
- `save_candle_and_features(candle, ts, _pm_feats)` 동기 저장 추가 (1줄이 핵심)
- `PRE_MARKET_REFIT_MIN_BARS=3` 제거 → `PRE_MARKET_REFIT_STEPS={1,5,10,14}` 점진 4회 재적합
- 각 Phase 완료 시 z경고 before→after 비교 로그

**커밋**: `6e844da` (201차)

---

## 2026-06-18 (199차 — UI 응답없음·파이프라인 멈춤 근본 수정)

**Work**: 장중 파이프라인 반복 멈춤(8회 재시작)·UI 응답없음 원인을 LiveDBG 진단으로 추적·수정.

**원인 확정**:
- 주범: conf_trend_widget.py (오늘 신설) — 30초 타이머로 전체 ensemble_decisions 렌더링
  - 12:17 (195행, 7.8초/30초 블로킹) → 최초 공백. 행 누적으로 점진 악화, 장중 8회 재시작
- 부원인: MinuteChartDialog 3688x2060 거대 캔버스 / 장외 BalanceRefresh BlockRequest 71초 블로킹

**핵심 수정**:
- conf_trend_widget.py: MAX_ROWS=30, in-place 업데이트, setUpdatesEnabled, 범위 쿼리
- main_dashboard.py: 차트 비동기 로딩, mouseMoveEvent throttle, 거대 캔버스 가드
- main.py: 장외 BlockRequest 가드 (BalanceRefresh, SyncPosition)
- session_recovery_service.py: restore_panels DB 쿼리 백그라운드화
- 전체: substr(ts) → 범위 쿼리 (idx 활성화, predictions.db 439MB)

**신규 추가**: conf_trend_widget.py, candle_chart_dialog.py, direction_indicator_dialog.py

---

# ?몄뀡 ?대젰 ??futures (誘몃Ⅵ??

> 理쒖떊???뺣젹.

---

## 2026-06-17 (191차 — EOD 재학습 OOM 해결 + py310_64 장외 스케줄러 분리)

**Work**: 매일 15:40 EOD 재학습이 py37_32 메모리 단편화로 OOM 실패하는 문제를 py310_64 장외 스케줄러 분리로 근본 해결.

### 에러 분석

```
numpy.core._exceptions._ArrayMemoryError:
  Unable to allocate 22.2 MiB for an array with shape (30060, 97) and data type float64
```
- 원인: 32-bit Python 2GB 가상 주소 공간 단편화 → 연속 22.2 MiB 할당 불가
- 발생 위치: `StandardScaler.fit_transform` 내부 `temp = X - T` 임시 배열
- `full_cv=True` (EOD 전용 20k 캡 해제) 상태에서 전체 30k행 처리 중 발생

### 구현

| 파일 | 내용 |
|---|---|
| `learning/batch_retrainer.py` | `pickle.dump(..., protocol=4)` 4곳 추가 |
| `retrain_eod.py` | py310_64 독립 재학습 스크립트 (완료 마커 생성) |
| `register_eod_scheduler.ps1` | 윈도우 스케줄러 15:45 등록 |
| `_measure_retrain.py` | 소요 시간 실측 스크립트 |
| `_check_pkl_compat.py` | pkl 호환성 검증 스크립트 |

### 실측 (py310_64, 40,080행×97열)

- 데이터 로드: 39.9s / 재학습(GBM+RF): 169.2s / **합계 209.4s**
- peak 메모리: ~200 MB (OOM 없음)
- pkl 호환 확인: py37_32에서 6/6 호라이즌 로드 성공

| 수정 | 커밋 |
|---|---|
| protocol=4 + 장외 스크립트 + 스케줄러 | `7d73e47` 191차 |

---

## 2026-06-17 (190차 — SGD 학습 B군 피처 N분봉 교정)

**Work**: 189차 분석에서 도출된 SGD 학습-예측 피처 불일치 문제의 중간 단계 교정 구현. B군(봉 크기 의존) 피처만 선별해 N분봉 캐시값으로 교체.

### 구현 내용 (`main.py:5659-5686`)

SGD learn() 직전, `_dx_full`(1분봉 피처 97개) 중 B군 인덱스를 `_hz_feat_cache[horizon]`(N분봉값)으로 덮어씀. 슬라이싱(`_h_idx_learn`) 전에 교정하므로 호라이즌별 피처셋에 B군이 포함된 경우 정확히 반영됨.

```
for _dv in _sgd_deferred_verified:
    _dx_full = 1분봉 피처 97개  ← DB
    if 장기 호라이즌 AND 캐시 있음:
        B군 피처 인덱스 → N분봉 캐시값으로 덮어쓰기
    _dx_learn = _dx_full[슬라이싱]  ← 교정 포함
    learn(_dx_learn)
```

**교정 대상:**
- 10m: `hurst`, `mlofi_slope`, `vwap_momentum`, `cvd_monotone_ratio`
- 15m: `volume_acceleration`, `avg_volume`, `atr_ratio`, `toxicity_atr_stress`
- 30m: `atr_ratio`, `toxicity_score_ma`, `queue_signal_ma`, `toxicity_atr_stress`, `threshold_feasibility`

**안전장치:** 캐시 없는 구간(장 초반 N분) 교정 스킵. 피처명 미존재 시 `ValueError`로 조용히 통과.

**A군(옵션·매크로·VWAP) 유지 이유:** 1m봉값 = Nm봉값이므로 교정 불필요.

### A안 전체 구현 일정 확정

`docs/260617_SGD_NMIN_FEATURE_CORRECTION_PLAN.md` 작성. Phase C 재학습 완료 + 모의투자 4주 후(2026-07~08 예상)로 A안 구현 일정 확정. 현 중간 단계로 핵심 B군 오염 제거.

| 수정 | 파일 | 커밋 |
|---|---|---|
| SGD B군 피처 N분봉 교정 | `main.py` | `b886b0c` 190차 |
| SGD N분봉 교정 검토 문서 | `docs/260617_SGD_NMIN_FEATURE_CORRECTION_PLAN.md` | `c836bfc` |

---

## 2026-06-17 (189차 — SGD UP/DN 붕괴 감지 + BAR_CACHE_DECAY 적용 + FULL_RESET_PENDING 수정)

**Work**: 장중 `15m sgd=u=0.998 11분 고착` 알림을 계기로 SGD 붕괴 감지 구조 점검. 오늘 50분정확도 분포 전체 분석(358분). BAR_CACHE_DECAY 미사용 발견 및 적용. N분봉 현실화 구조 설계 검토.

### [A] SGD UP/DN 붕괴 감지 추가 (`learning/online_learner.py`)

기존: `flat > 0.95` 연속 15회만 감지 → UP/DN 붕괴 방치.
오늘 실제: `30m u=1.000 19분`, `5m d=1.000 4분`, `10m d=1.000 9분` 동시 붕괴 방치 확인.

`_sgd_fl_collapse_ticks` → `_sgd_collapse_ticks` + `_sgd_collapse_dir` 통합.
UP/DN/FL 중 어느 방향이든 0.95 초과 15분 연속 시 해당 호라이즌 SGD 리셋.
방향 전환 시 카운터 초기화. `reset_daily`/`reset_full`에도 새 변수 초기화 추가.

### [B] SGD_FULL_RESET_PENDING 수정 (`config/settings.py`)

오늘 14:21 GBM 재학습 완료 후 SGD비중 26%→30%, 50분정확도 48.9%→50.0% 갑자기 초기화 원인 추적.
`settings.py:109` `SGD_FULL_RESET_PENDING = True`가 파일에 잔존 → 재시작마다 첫 GBM 재학습 시 `reset_full()` 반복 발동.
`False`로 수정. threshold 교체 등 필요 시 수동으로 True 세팅 후 재시작.

### [C] BAR_CACHE_DECAY 실제 적용 (`main.py:3916-3920`)

`_BAR_CACHE_DECAY = {3:0.97, 5:0.95, 10:0.93, 15:0.92, 30:0.97}` 정의만 있고 미사용이었음.
캐시 존재 시 `bar_age`와 무관하게 원값 그대로 사용 → 30m는 29분간 동일 피처 입력 → conf 고착.
`_hz_feat_vecs[h] = cache[h] * decay^age` 적용.
30m bar_age=19 → 0.97^19=0.56배 감쇠 → 시간 경과 시 conf가 자연스럽게 중립으로 이동.

### [D] 오늘 50분정확도 분포 분석 (참고 기록)

| 구간 | 빈도 | 원인 |
|---|---|---|
| 0.0% | 32분(8.9%) | SGD 붕괴 |
| 50.0% | 41분(11.5%) | acc_buf 비어있음(fallback) |
| <33.3% | 86분(24.0%) | 랜덤 이하 |
| ≥48% | 140분(39.1%) | 정상 |

P2-D 필터(conf<0.52)가 오늘 89.4% 차단 → 실학습 분당 0~1건. "N건 학습" 로그는 검증 건수(≠실학습 건수).
"50분정확도" 라벨은 ACCURACY_WINDOW=100 기준 실제 100분 윈도우.

### [E] N분봉 피처 현실화 구조 검토 (설계 논의, 미수정)

- GBM 학습(Phase 2): N분봉 재계산 피처 ✅
- GBM 예측: `_hz_feat_cache[h]` N분봉 피처 ✅
- SGD 예측: `_hz_feat_vecs[h]` N분봉 피처 ✅
- SGD 학습: `_dv.get("features")` DB 저장 1분봉 피처 ❌ → 예측-학습 피처값 불일치
- 피처 이름(NAME) 세트는 `horizon_feature_sets.json`으로 호라이즌별 고정. 불일치는 이름이 아닌 값(VALUE)의 출처 문제.
- N분봉 캐시 없을 때 전 호라이즌 동일하게 `get_horizon_features(1m피처, h)` 반감기 fallback 사용. 3m는 2분, 30m는 29분간 fallback.

| 수정 | 파일 | 커밋 |
|---|---|---|
| SGD UP/DN 붕괴 감지 통합 | `learning/online_learner.py` | `1f1445c` 189차 |
| SGD_FULL_RESET_PENDING False | `config/settings.py` | `1f1445c` 189차 |
| BAR_CACHE_DECAY 실제 적용 | `main.py` | `1f1445c` 189차 |

---

## 2026-06-16 (182차 — EOD MemoryError 복구 + validate_and_resync() 허위 정합성오류·재학습 무한루프 버그 수정)

**Work**: 오늘 15:40 EOD가 MemoryError로 중단된 것을 점검·복구. 복구 과정에서 발견된 "[Model] 정합성 오류 6개 호라이즌" 로그(오늘 7회 발생)를 딥다이브해 별도의 구조적 버그를 확정·수정.

### [A] EOD MemoryError 점검 + 수동 복구

15:40:25 EOD GBM 재학습(`weeks_back=26, full_cv=True`) 중 15:41:25 `MemoryError: Unable to allocate 29.7 MiB for array shape (40093, 97)` 발생 — 06-11 동일 패턴 재발(32-bit 프로세스 가상주소공간 고갈 추정). `daily_close()`가 예외를 캐치하지 못해 P8 스케일러 재적합·Platt/MetaConf 저장·일일 리셋·WAL 체크포인트가 전부 스킵된 채 강제 종료됨.

- `scripts/catch_up_eod.py` 실행 — GBM 재학습(40,093행, 6/6 호라이즌, cv_acc 36~43%) + P8 스케일러 재적합(6/6) + WAL 체크포인트(6/6 DB) 전부 OK로 복구
- `main.py:6546` `retrain_now()` 호출을 try/except로 감싸 — 재학습이 예외로 죽어도 이후 EOD 단계(P8·Platt·MetaConf 저장·일일 리셋·WAL 체크포인트)는 계속 진행되도록 구조적으로 고침. 다음 동일 사고 발생 시 수동 복구 불필요

### [B] `validate_and_resync()` 허위 정합성오류 + 재학습 무한 재트리거 버그 발견·수정

복구 과정에서 "[Model] 정합성 오류 6개 호라이즌 ... 즉시 재학습 필요"가 오늘 09:01·09:42·11:39·11:45·12:02·12:57·13:03 총 7회(일부 6분 간격 페어) 발생한 것을 확인 → 딥다이브.

**Root cause**: `model/multi_horizon_model.py:805` `validate_and_resync()`가 스케일러 차원(항상 전체 97개 — `batch_retrainer.py:563` "스케일러는 97개 전체 피처 기준" 참조)을 Phase C 호라이즌별 슬라이싱된 피처 수(12~15개)와 비교 — 슬라이싱은 스케일링 *후* GBM 입력 단계에서만 적용되므로 이 비교는 구조적으로 영원히 불일치. 불일치 시 `_is_fitted[h]=False`로 전 호라이즌을 비활성화 → `predict_proba()`가 GBM 대신 `_default_result()`(33.3%/33.3%/33.3% FLAT)로 대체. 더 나아가 `main.py:2632` `_on_gbm_retrain_done()`이 이 결과로 즉시 `_start_manual_retrain(reason="resync_mismatch")`를 재트리거 — 재학습 완료마다 똑같은 허위 불일치가 재발해 비계획적 GBM 재학습이 반복됨 (오늘 앞서 분석한 PipePerf "[GBM재학습중]" 09:26-09:28·11:14-11:15 정체와 연관 가능).

**Fix**: 비교 기준을 슬라이싱된 `horizon_feature_names` 크기 대신 `len(self.feature_names)`(전체 97개, 스케일러의 실제 적합 기준)로 교정.

**검증**: 수정 후 `MultiHorizonModel()` 직접 인스턴스화 → `validate_and_resync()` 호출 → `BAD HORIZONS: []`, 6개 호라이즌 전부 `fitted=True` 확인.

### 검증

`main.py`, `model/multi_horizon_model.py` `ast.parse` 통과. 라이브 프로세스는 재시작 후 반영.

---

## 2026-06-16 (181차 — time_zone 크래시 수정 + Hurst 미진입 딥다이브 + 진입단계 추적 카드 전면 개선 + 로그 파일화)

**Work**: 사용자가 공유한 `cybos_plus_launch.log` 크래시 로그와 신뢰도게이트 대시보드 캡처(14:32/14:33 "8.진입후보"인데 미진입)를 각각 딥다이브해 근본 원인을 확정·수정. 이어서 대시보드 "금일 Conf → 진입단계 추적" 카드를 STEP7 마스터 게이트까지 반영하도록 전면 개선했다.

### [A] `time_zone` UnboundLocalError 수정

`run_minute_pipeline()`에서 체크리스트 선행평가(`main.py:4444`)와 `decision["meta_gate"] = self.meta_gate.evaluate(..., time_zone=time_zone, ...)`(`main.py:4472`)가 STEP7에서야 할당되는 `time_zone`을 그보다 먼저 참조 — `UnboundLocalError`로 매분 `minute_pipeline` 크래시(WARN.log: 12:58~13:02 5회 연속 확인). 두 지점 모두 같은 값으로 이미 위(4232행)에서 할당돼 있던 `_tz`를 쓰도록 교정 — 동작 변화 없이 크래시만 제거.

### [B] 14:32/14:33 "8.진입후보"인데 미진입 — Hurst 필터 딥다이브

DEBUG.log 대조 결과 체크리스트는 등급 A까지 통과(`[DBG-F7a] checklist 7/9 → A`)했으나 `hurst=0.417/0.390 < HURST_RANGE_THRESHOLD(0.45)` → STEP7 마스터 게이트 `_hurst_ok` 조건에서 차단(`main.py:5092`, `:5243`). 차단사유 로그(`log_manager.signal`)가 대시보드 버퍼에만 쌓이고 파일 로거로는 안 나가 `.log` grep으로 추적 불가했던 것도 진단을 어렵게 한 원인 — [D]에서 해소. 근본적으로는 대시보드 "8.진입후보" 단계가 체크리스트/메타/톡시시티만 보고 판정하며 CB·Hurst·ATR·쿨다운 등 STEP7 마스터 게이트 나머지 조건을 전혀 반영하지 않았던 것이 원인 — [C]에서 해소.

### [C] "금일 Conf → 진입단계 추적" 카드 전면 개선

| 항목 | 내용 | 파일 |
|---|---|---|
| STEP7 게이트 16조건 DB 저장 | CB/HC/브로커sync/쿨다운/청산쿨다운/재시작유예/무결성/역방향클램프/Hurst/ATR/모드필터/수량/거래량/IntradayRegime/EKS + 우선순위 기반 차단사유(`_entry_block_reason`)를 `decision`에 담아 STEP9에서 저장 | `main.py` |
| 기존 차단사유 로그 중복 제거 | STEP7 말미의 동일 elif 체인을 삭제하고 위에서 산출한 `_entry_block_reason` 재사용 | `main.py` |
| DB 컬럼 6종 추가 | `entry_gate_json/entry_final_ok/entry_qty/entry_mode/entry_executed/entry_block_reason` 마이그레이션 | `utils/db_utils.py` |
| STEP9 INSERT 확장 | `save_step9_batch()` 컬럼·바인딩 추가 | `learning/prediction_buffer.py` |
| 단계 체계 재정비 | 7(Auto불가, 체크리스트) → **8.STEP7 차단**(구체 사유) → **9.진입후보(최종)** → **10.진입완료** | `dashboard/panels/dynamic_mc_panel.py` |
| 신규 컬럼 "차단사유" | 단계 0~10 전부에 대해 사람이 읽는 한 줄 설명 표시 | 〃 |
| 게이트 상세 툴팁 | 진입단계/차단사유 셀 호버 시 16개 조건 ✓/✗ 전체 표시 | 〃 |
| 범례 갱신 | 카드 제목 툴팁을 새 단계 체계로 교체 | 〃 |

### [D] 차단사유 로그 파일 영속화

`LogManager.log()`가 대시보드 버퍼 적재에 더해 `utils.logger.get_logger(layer)`(SYSTEM/SIGNAL/TRADE/LEARNING/DEBUG, HEALTH→SYSTEM)로도 동시에 기록하도록 브리지 추가 (`logging_system/log_manager.py`). `log_manager.signal/system/trade/health`로만 남기던 메시지가 이제 `.log` 파일 grep으로도 확인된다.

### 검증

- `python -m py_compile main.py utils/db_utils.py learning/prediction_buffer.py logging_system/log_manager.py dashboard/panels/dynamic_mc_panel.py` 통과
- 라이브 미반영 — main.py/prediction_buffer.py 변경은 다음 재시작부터 적용. DB 컬럼은 `init_predictions_db()`가 재시작 시 자동 `ALTER TABLE`
- PyQt5 대시보드 렌더링은 미검증(UI 미기동) — 다음 장 재시작 후 카드 표시 확인 필요

### 비고

- 작업 중 `learning/prediction_buffer.py`에 본 세션과 무관한 미커밋 변경(180차의 `_db_write_lock` 직렬화·서브타이밍 계측)이 이미 있었음 — 별도 세션 작업으로 확인, 본 세션 변경과 충돌 없음.

---

## 2026-06-16 (180차 — CB 파이프라인 정체 진단 + 워치독 무한루프 버그 수정)

**Work**: 사용자가 CB 발동 로그(`S2=5976ms` 등)와 15:10 이후 90초 간격 반복 경보 로그 제공 → 두 건 모두 딥다이브로 근본 원인 확정 후 패치.

### [A] PipePerf "S2" 라벨 오프셋 버그 발견 + 수정

`_st.append(("S2", ...))` 등 마커가 각 STEP **시작 지점**에 찍히는데, `_all_steps_str`는 마커 자기 이름을 그 직전 구간 소요시간에 매칭 → 로그의 `S2=Xms`가 실제로는 STEP1(`verify_and_update`, 검증) 본문 시간이었음 (진짜 STEP2 SGD는 항상 5~13ms). 이 때문에 STEP2 내부에 이미 있던 자체 진단(`[S2-느림]`/`[S2-분산GIL]`, `main.py:3469~3507`)이 한 번도 발동하지 않았음 — 엉뚱한 구간을 보고 있었기 때문.

- `main.py` `_all_steps_str` 조립부: `_st[i][0]` → `_st[i-1][0]`로 라벨 교정 (마커 위치는 그대로, 표기만 수정 — 내부 위치 참조 로직 영향 없음)

### [B] `verify_and_update()` 서브타이밍 계측 추가

`learning/prediction_buffer.py`에 `raw_fetch`/`pred_select`/`pred_update`/`pred_insert` 4구간 perf_counter 분해. 총합 300ms 초과 시 `[Buffer-Timing] total=... raw_fetch=... pred_select=... pred_update=... pred_insert=... verified=N`을 LEARNING.log에 출력 — 다음 정체 시 정확한 병목 구간 확정용.

### [C] `verify_and_update()` DB 락·타임아웃 개선

- `utils/db_utils.py` `get_conn()`에 `timeout` 파라미터 추가 (기본 10.0초 유지, 다른 호출부 무영향)
- `verify_and_update()`의 RAW_DATA_DB/PREDICTIONS_DB 접근을 앱 공용 `_db_write_lock`(`utils.db_utils._lock`)으로 감싸 `_db_write_worker`와 동일 프로세스 내 SQLite 락 경합 제거
- 두 접근 모두 `timeout=3.0`으로 단축 — 막혀도 10초 대신 3초 안에 fail-fast, 해당 분 검증 스킵 후 다음 분 재시도

### [D] 워치독 무한루프 버그 수정 (15:10 이후 90초 경보 반복)

`_try_pipeline_recovery()`(`main.py:7071`)의 "이미 복구한 분봉" 스킵 분기가 `notify_pipeline_ran()`을 호출해 매번 워치독 경과시간을 0으로 리셋 → 15:10 강제청산 이후 실분봉이 더 안 들어오는 정상 상태인데도 90초 경보가 영원히 반복되고 150s/240s/300s(거래소 CB 대기) 단계로 절대 에스컬레이션되지 않음. 부가로 첫 복구 시도는 `_on_candle_closed()`의 `is_force_exit_time` 가드를 우회해 `run_minute_pipeline()`을 강제청산 후에도 1회 더 실행시키는 부작용도 있었음.

- `_on_pipeline_watchdog()`(`main.py:6936`)·`_try_pipeline_recovery()`(`main.py:7071`) 양쪽에 `is_force_exit_time(now)` 가드 추가 — 15:10 이후는 워치독·복구 시도 자체를 끔

### 검증

3개 파일(`main.py`, `learning/prediction_buffer.py`, `utils/db_utils.py`) `ast.parse` 문법 검증 통과. 라이브 프로세스는 재시작 후 반영.

---

## 2026-06-16 (179차 — Phase C 슬라이싱 버그 수정 + SGD 최적화 + CORE 그룹 분리 + UI 개선)

**Work**: 178차 호라이즌 피처셋 인프라 적용 후 발생한 ERR-FATAL 다수 수정 → SGD P0·P1·P2 최적화 → CORE 호라이즌 그룹별 분리 → 동적피처 패널 Phase A·B·C 구현 → 점심 추세 진입 최적화.

### [A] Phase C 슬라이싱 버그 수정 (ERR-FATAL 연쇄 해소)

| 버그 | 파일 | 원인 | 수정 |
|---|---|---|---|
| `X has 12 features, but StandardScaler expecting 97` | `multi_horizon_model.py` `predict_proba` | 슬라이싱→스케일러 순서 오류 | 스케일러(97개)→슬라이싱(12개)으로 교정 |
| `X has 97 features, but HistGBM expecting 12` | `multi_horizon_model.py` `_predict_masked` | 동일 누락 | 동일 교정 |
| 스케일러 피처 수 불일치 방어 | `multi_horizon_model.py` `predict_proba` 진입부 | 재학습 전환기 구 스케일러 잔존 | 불일치 감지 → None 처리(5분 스로틀 경고) |
| `_train_horizon` 스케일러 12개 저장 | `batch_retrainer.py` | `X_h`(슬라이싱)로 스케일러 적합 | `X_full`(97개)로 스케일러, GBM은 슬라이싱값 사용 |
| `refit_scalers_only` `horizons=[]` 지속 | `multi_horizon_model.py` | `_is_fitted=False` 시 전 호라이즌 skip | `_is_fitted` 조건 제거 (스케일러는 독립 재적합 가능) |
| scaler pkl 12개짜리 잔존 | model/scaler/ | 이전 재학습에서 저장 | 6개 파일 삭제 → 재시작 시 97개 재생성 |

결과: 12:03:02 C_PERIODIC `horizons=['1m',...] elapsed=0.20s` — 스케일러 정상 갱신 확인.

### [B] SGD P0·P1·P2 최적화

| 개선 | 파일 | 내용 |
|---|---|---|
| P0: 피처 슬라이싱 | `main.py` | `learn()`·`predict_proba()` 호라이즌별 `_hz_feat_indices` 슬라이싱. 1m SGD가 macro_vix(EX) 등 잡음 피처 학습 차단 |
| P1-B: 호라이즌별 독립 가중치 | `online_learner.py` | short/long 2버킷 → 6개 호라이즌 완전 독립. 임계값 차등(1m BOOST=58% / 30m BOOST=65%) |
| P1-C: sample_weight FLAT 억제 | `online_learner.py` | FLAT 비율>50% 시 FLAT 0.5배 / UP·DN 1.5배 |
| P2-D: 고신뢰도 학습 필터 | `main.py` | conf<0.52 예측 결과 학습 제외 |
| P2-E: 초기 GBM FLAT 편향 대항 | `online_learner.py` | flat_score>0.60 감지 시 학습건<50이라도 SGD 20% 즉시 투입 |

### [C] CORE 호라이즌 그룹별 분리

단기(1m~5m): CVD·VWAP★·OFI / 중기(10m~15m): VWAP★·macro_vix / 장기(30m): opt_chain_pcr·macro_vix

| 수정 | 파일 |
|---|---|
| `HORIZON_CORE_GROUP`, `CORE_FEATURES_BY_GROUP`, `CORE_MASK_EXEMPT_BY_GROUP` 상수 | `config/settings.py` |
| `_CORE_MASK_EXEMPT` 전체 union 확장 + `_CORE_MASK_EXEMPT_BY_HZ` 호라이즌별 맵 | `model/multi_horizon_model.py` |
| `entry_horizon`, `macro_vix`, `opt_chain_pcr` 인자 추가. 그룹별 4번(CVD→대체)·5번(OFI→중기 면제) 분화. VWAP 강제X 장기 해제 | `strategy/entry/checklist.py` |
| 체크리스트 두 호출에 `entry_horizon`·`macro_vix`·`opt_chain_pcr` 전달 + VIX·PCR 캐싱 | `main.py` |
| CORE 설명 텍스트 호라이즌 그룹별로 교체 | `dashboard/main_dashboard.py` |
| CORE 정의 섹션 재작성 | `CLAUDE.md` |

### [D] 동적피처 패널 Phase A·B·C 구현

`FeaturePanel` 전체 재작성:
- **Phase A**: 헤더(진입 호라이즌 배지 + 그룹별 통과수 요약) + 단기/중기/장기 CORE GroupBox(색상 분리)
- **Phase B**: SHAP 바 + 상태(핵심/안정/약화) + `★강제X` 마크 + VIX·PCR 실측값 인라인
- **Phase C**: CORE × 호라이즌 5×6 신호 매트릭스 (●포함 ○pending ✕제거 —미해당), 진입 호라이즌 열 강조

### [E] 점심 추세 진입 최적화

12:32~12:45 추세 상승 14분 진입 미발생 원인 분석 → 3종 최적화:
- ① STABLE_TREND/LUNCH_RECOVERY 시간대 Checklist min_conf 48%로 완화 (기존 62%)
- ② TrendGate ON 시 MetaGate 편향패널티 비활성화 (추세를 편향으로 오인 차단)
- ③ STABLE_TREND/LUNCH_RECOVERY 시간대 reduce_thr -0.04p 완화 (0.427→0.387)
역산: 12:45 blended=0.482>0.387 + conf=49%≥48% → 진입 후보 ✅

### 기타 수정·개선
- `scaler_monitor_panel`: `_needs_insert` 매분 저장 → 스케일러탭 정상 표시
- `threshold_monitor_panel`: "다음 갱신" 카드 추가 (금요일 기준)
- `main.py` `_gather_learning_stats()`: `ol.BUCKET_SHORT` → `ol.horizon_accuracy(hz)`
- `main_dashboard.py` `_build_matrix()`: `C['muted']` → `C['text2']`

### 실거래 (모의투자)
- 11:43 LONG 1계약 @ 1390.58 → TP3 청산 @ 1392.08 **+1.5pt / +72,914원** ✅

---

## 2026-06-15 (178차 — 호라이즌별 피처셋 인프라 + opt_chain 버그 3종 수정)

**Work**: 기획안(호라이즌별 최적피처셋 v1.0) 검토 → Phase A~D 구현 + opt_chain 수집 버그 발견/수정.

### 한 일

| 항목 | 내용 | 파일 |
|---|---|---|
| [A] macro 복구 | yfinance 429 → Cboe CDN/Treasury XML/Yahoo v8 daily/Naver+frankfurter 교체. fallback_used=0, source_code=4 달성 | `collection/macro/macro_fetcher.py` |
| [B] 피처셋 JSON | 6개 호라이즌 × include/exclude/need_add 명세. 교차검증(PASS) | `featureset by horizon/horizon_feature_sets.json` |
| [C] 인프라 구현 | `horizon_feature_registry.py` 신규. batch_retrainer X 슬라이싱 + per-horizon pkl 저장. multi_horizon_model 슬라이싱 인덱스 사전계산 + predict_proba 호라이즌별 슬라이싱 | `features/horizon_feature_registry.py`, `learning/batch_retrainer.py`, `model/multi_horizon_model.py` |
| [D] Walk-Forward | 10m/15m/30m 검증 → REGRESS. 원인: opt_gex_bn/chain_pcr DB 미수집. 결정: opt 4주 후 재검증, 현재 97개 유지 | `featureset by horizon/validation_results.md` |
| Bug 1 | `_chain_feats` → `feature_builder.build()` 미전달 (opt_chain/gex/atm 모두 DB 저장 안 됨) | `main.py` L3537 |
| Bug 2 | `_option_chain_timer` 미생성 → `_poll_option_chain()` 한 번도 호출 안 됨 | `main.py` `run()` |
| Bug 3 | `_investor_timer` 미생성 → 수급 데이터 장중 주기 갱신 없음 | `main.py` `run()` |

### 다음 할 일

- 다음 장: opt_chain 수집 로그 확인 + DB opt_chain_pcr 키 저장 여부
- opt 4주 축적 후 Phase D 재검증
- Phase E: SHAP Tracker 6개 호라이즌 확장

---

## 2026-06-11 (156차 — _gbm_retrain_running 고착 + MIN_TRAIN_BARS 이중 체크 + C_PERIODIC 독립)

**Work**: SIGNAL.log 분석 → 스케일러 98분 미갱신 원인 딥다이브 → P1/P2/P3 수정.

### 한 일

| Fix | 내용 | 파일 |
|---|---|---|
| A (분석) | 20260611_SIGNAL.log 전체 분석 — macro_vix z=+35.24 고착·스케일러 91→98분 미갱신·MetaConf 과소·ConstOut 6회·StuckBreaker streak=13·진입0 확인 | 로그 분석 |
| B (딥다이브) | 스케일러 미갱신 원인 추적: 08:55 GBM 재학습 ok=False → `_gbm_retrain_running` 고착 → Phase B 전 구간 차단 (C_PERIODIC 60분 포함) | LEARNING.log + main.py + batch_retrainer.py |
| P1-A | 4개 worker(`_retrain_worker`×2, `_intraday_retrain_worker`, `_pre_retrain_worker`)에 `ok=False` 즉시 `_gbm_retrain_running = False` 리셋 추가 | `main.py` L708/2192/2640/3179 |
| P1-B | `_gbm_retrain_started_at` 추적 변수 추가(init+4곳). Phase B 직전 30분 타임아웃 강제 해제 | `main.py` L407/699/2177/2628/3167/3628-3636 |
| P2 | `_load_from_db` 조기 체크(feat_rows 기준, 미래가격 제거 전) 삭제 → 미래가격 제거 후 `len(records)` 기준으로 이동 | `learning/batch_retrainer.py` L689-693 삭제, L752-758 추가 |
| P3 | Phase B 조건 분리: B/C_PERIODIC은 `_gbm_retrain_running` 무관 실행. D_FORCE만 내부에서 GBM 재학습 중 skip | `main.py` L3612-3660 |

### 스케일러 미갱신 근본 원인 (규명)

```
08:55:05 GBM 재학습 시작 (weeks_back=10)
08:55:22 DB 로드 완료: 14766행 × 97피처
         → feat_rows=16387로 조기 체크 통과 (미래가격 제거 전)
         → 미래가격 제거 후 14766행 (1621행 드랍)
         → retrain_now() 두 번째 체크: 14766 < 15000 → ok=False
         → _on_gbm_retrain_done QTimer 미발화(daemon thread 불안정)
         → _gbm_retrain_running = True 고착
09:00~15:00 Phase B: `not _gbm_retrain_running` 조건 → C_PERIODIC 60분 전 구간 차단
         → 스케일러 98분 미갱신
```

### 155차 효과 점검

| 항목 | 155차 수정 | 내일 예상 효과 |
|---|---|---|
| macro_vix z=+35.24 | `_MACRO_SCALE_FLOOR["macro_vix"]=0.10` 추가 | z폭발 억제 |
| conf=100% FLAT | Fix1+2+3 (직접 가중합·0.85 cap·PROB_FLOOR) | FLAT 고착 차단 |
| GBM 데이터 부족 | RETRAIN_WEEKS_BACK 10→26 | 충분한 데이터 확보 |
| EKS 기준 | DynMC GAP_OPEN mc 연동 | 0.45 고정 기준 제거 |

---

## 2026-06-11 (155차 — EKS min_conf 통합 + conf=100% FLAT 방어 3종 + SHAP 폴백 개선)

**Work**: 금일 SIGNAL.log 분석 → 3개 독립 이슈 수정.

### 한 일

| Fix | 내용 | 파일 |
|---|---|---|
| A | EKS 발동/회복 기준을 DynMC GAP_OPEN mc로 통합. 고정 0.45 → `gap_open_mc` 파라미터. 회복 max(mc,0.42) floor 제거 | `safety/system_health.py`, `main.py` |
| B-1 | flat_score 직접 가중합 (1-up-down 수식 제거 + 정규화). up/down 반올림→0 → flat=1.0 팽창 근본 차단 | `model/ensemble_decision.py` |
| B-2 | FLAT 방향 0.85 cap 추가. 기존 UP/DN에만 cap → FLAT 누락 구멍 패치 | `model/ensemble_decision.py` |
| B-3 | `_PROB_FLOOR=0.0001` — `predict_proba`·`_predict_masked` 양쪽. 극소값 반올림→0 원천 차단 | `model/multi_horizon_model.py` |
| C | SHAP 3-tier fallback: TreeExplainer → per-class tree 중요도 → global. `get_class_ranking()` 신규. `weekly_review()` `direction_top` dict 추가 | `learning/shap/shap_tracker.py` |

### conf=100% 탈출 경로 (이번 세션 규명)

기존 135차·143차 수정에서도 살아남은 탈출 경로 발견:
- GBM: `up=0.00004, down=0.00004, flat=0.70`
- CONF_CLIP(0.80) 미발동 (flat < 0.80)
- `round(up, 4)=0.0`, `round(down, 4)=0.0`
- `flat_score = max(0, 1-0-0) = 1.0`
- calibration·0.85 cap 모두 우회 → `conf=100%`

Fix1+2+3 세 층으로 봉쇄.

---

## 2026-06-10 (142차 — EOD 자동종료 흐름 6종 안전화)

**Work**: 장마감 후 GBM 학습·EOD 작업·자동종료 흐름 전체 점검 → 이상점 6개 발견 → 우선순위 순서대로 전부 구현.

### 한 일

| Fix | 내용 | 파일 |
|---|---|---|
| A | `_ShutdownSignal(QObject)` 추가 + `QueuedConnection` 연결 — DailyClose 스레드의 `QTimer.singleShot` 비-Qt 스레드 호출 근본 수정 | `main.py` |
| B | `_schedule_shutdown()` 신규 메서드 — Qt 위젯 접근(append_sys_log)·QTimer 모두 메인 스레드에서 실행 보장 | `main.py` |
| C | `_run_daily_close` try/except + `_emit_done` 플래그 — `daily_close()` 예외 시에도 종료 시그널 emit 보장 | `main.py` |
| D | DBWriter 큐 플러시 (`put(None)` + `join()`) — 마지막 분봉 candle/feature 기록 유실 방지 | `main.py` |
| E | WAL 체크포인트 대상 6개 DB 전체 확장 (기존 2개) + `EOD_WAL_CHECKPOINT_DBS` 상수화 | `main.py`, `config/settings.py` |
| F | EOD `retrain_now(force=False)` 명시 — standalone `eod_retrain.py`(`force=True`)와 의도 차이 주석 기록 | `main.py` |

### 이상점 분석

| 이상점 | 증거 | 원인 |
|---|---|---|
| 자동 종료 간헐 미발동 | `QTimer.singleShot` 이 DailyClose 스레드에서 호출 | DailyClose는 일반 Python thread — Qt 이벤트 루프 없음, 타이머 미발화 |
| 예외 시 프로그램 무한 실행 | `_daily_close_done=True` 선점 후 thread 시작 | 예외 발생 시 `QTimer.singleShot` 미등록, 재진입 차단으로 무한 실행 |
| 마지막 분봉 DB 유실 가능 | `_db_write_queue.put(None)` 코드 없음 | `_qt_app.quit()` 시 daemon thread 강제 종료 → 큐 미처리 항목 드랍 |
| 4개 DB WAL 미체크포인트 | TRADES/SHAP/CHALLENGER/SCALER_MONITOR 누락 | 누락 DB WAL 파일 매일 누적 → 다음날 기동 지연 |
| Qt 위젯 비-Qt 스레드 접근 | `append_sys_log()` → `QTextEdit.insertHtml()` | DailyClose 스레드에서 Qt 위젯 직접 조작 |
| force 불일치 | in-process `force=False`, standalone `force=True` | 의도 차이이나 주석 없어 혼란 유발 |

---

## 2026-06-09 (135차 — Meta skip·conf=100% 4종 근본 원인 수정)

**Work**: 6/9 장중 로그(SIGNAL.log) 전수 분석 → MetaGate skip 과발동 2종 + SGD 붕괴 + conf=100% FLAT 고착 원인 규명 → 5개 파일 패치.

### 한 일

| Fix | 내용 | 파일 |
|---|---|---|
| A-1 | MetaGate reduce_thr 공식 수정: `max(0.43, min_conf+0.04)` → `max(0.38, min_conf)` (오프셋 제거) | `strategy/entry/meta_gate.py` |
| A-2 | actual_min_conf(존+FQAdj 반영값)를 MetaGate.evaluate()에 전달 (UI 표시 mc ≠ 실제 mc 불일치) | `main.py` STEP 6 |
| B-1 | SGD 붕괴 보완: meta_conf < 0.15 시 rule-based floor로 하한 보정 | `strategy/entry/meta_gate.py` |
| B-2 | MetaConfidenceLearner 붕괴 자동 감지·복구: `_is_collapsed()` + `_reset_model()` (최근 30회 max < 0.05) | `learning/meta_confidence.py` |
| C | AutoMask CORE 피처 면제: `_CORE_MASK_EXEMPT` frozenset — cvd/vwap/ofi 계열 xs=0.0 대체 차단 | `model/multi_horizon_model.py` |
| D-1 | cvd_direction, cvd → `DFORCE_EXCLUDE_FEATURES` 추가 (이산 피처 D_FORCE로 해소 불가) | `config/settings.py` |
| D-2 | `refit_scalers_only()` CORE 피처 scale 보호: `scale_<0.05`이면 이전 mean/scale 복원 | `model/multi_horizon_model.py` |

### conf=100% FLAT 고착 원인 분석

```
12:49  D_FORCE feat=cvd_direction repeat=2회 → refit_scalers_only(500봉)
       500봉 전부 cvd_direction=-1 (하루종일 하락장)
       StandardScaler: mean=-1, std=0 → scale=1 (sklearn divide-by-zero fallback)
12:50~ scaler.transform(-1) = (-1-(-1))/1 = 0.0 → GBM에 "중립 CVD" 전달
       GBM: up≈0.001, flat≈0.998, down≈0.001
       flat_score = 1.0 - 0.001 - 0.001 = 0.998 → conf=100.0% 표시
       dir=+0 → grade=X → 진입 전면 차단 (12:50~13:11+ 21분간)
```

CONF_CLIP=0.92가 무효한 이유: CONF_CLIP은 개별 호라이즌 direction confidence에 적용되며, `flat_score = 1.0 - up_score - down_score`는 raw 확률 잔여값이라 클리핑 경로를 통과하지 않음.

### Meta skip 원인 체인 (이전 세션 이월 분석)

```
[문제 1] reduce_thr = max(0.43, min_conf+0.04) = max(0.43, 0.398+0.04) = 0.438
         blended = ens×0.6 + meta×0.4 ≈ 0.42 < 0.438 → skip (임계가 너무 높음)

[문제 2] actual_min_conf = max(decision["min_conf"], zone_mc) = 0.398 (OPEN_VOLATILE)
         UI는 mc=0.390 표시 → MetaGate에 0.390 전달 → reduce_thr=0.430 계산 → 오판

[문제 3] 극단 z-score → AutoMasked → 연속 오예측 → SGD "항상 틀림" 학습
         → prob[1]=0 고착 → meta_raw=0.000 → blended ≈ ens×0.6 → reduce_thr 미달
```

### 다음 할 일

- 내일 장: 135차 패치 효과 확인 (상세 NEXT_TODO 참조)
- GBM 재학습 (131차+133차+135차 반영) — 계속 이월

---

## 2026-06-09 (134차 — 파이프라인 지연 CB⑤ 근본 원인 2종 제거)

**Work**: 09:32 CB⑤ (8872ms) 패치 이후 재시동에서 탈출한 10:23 CB⑤ (5943ms) 딥다이브 분석 → `scaler_monitor.db` EXCLUSIVE lock 경합 근본 원인 확인 → Fix 7/8/9 구현. Fix 3/4/6 완성 포함.

### 한 일

| Fix | 내용 | 파일 |
|---|---|---|
| Fix 3 | STEP 4 candle/horizon_features DB → `_db_write_queue.put_nowait()` (큐 포화 시 동기 fallback) | `main.py` |
| Fix 4 | `daily_close()` WAL TRUNCATE 체크포인트 (PREDICTIONS_DB·RAW_DATA_DB) | `main.py` |
| Fix 6 | PipePerf CB임박 스텝별 breakdown 로그 (≥5s 전체, >1s 100ms 초과 스텝) | `main.py` |
| Fix 7 | `predict_proba()` 내 sync `insert_events_batch()` 제거 → `last_monitor_rows` + `_db_write_worker` 큐 처리 | `main.py`, `model/multi_horizon_model.py` |
| Fix 8 | `scaler_monitor.db` WAL 모드 (`insert_events_batch`, `update_event_refresh`) | `model/scaler_monitor_db.py` |
| Fix 9 | monitor rows 조건부 수집 — extreme>0 or age>90m만 기록 | `model/multi_horizon_model.py` |

### 10:23 CB⑤ 탈출 원인 분석

```
Phase C/ConstOut 재적합(10:22) → update_event_refresh() → scaler_monitor.db EXCLUSIVE lock
STEP 5 predict_proba() → insert_events_batch() → 동일 DB lock 대기 (timeout=5s)
= 5943ms 파이프라인 (5s 대기 + 943ms 나머지)
```

**왜 Fix 1~6으로 못 막았나**: Fix 3(STEP 4 비동기)은 STEP 4만 커버. STEP 5 내부 `insert_events_batch()`는 별개 경로. `scaler_monitor.db`는 PREDICTIONS_DB/RAW_DATA_DB와 다른 파일 — WAL 전환이 별도로 필요했음.

### 다음 할 일

- 내일 장: CB⑤ 재발 없음, PipePerf 스텝별 분포 확인
- GBM 재학습 (131차+133차 반영) — 이월

---

## 2026-06-09 (133차 — 이진 피처 D_FORCE 차단 + EKS 재시작 안정화)

**Work**: 6/9 SIGNAL·SYSTEM·TRADE·LEARNING 로그 전수 분석 → 132차 패치 동작 확인 + 잔존 진입0 원인 딥다이브 + 3종 추가 패치.

### 6/9 로그 분석 결과

| 개선 (110차) | 실제 동작 |
|---|---|
| ① opt_pcr clip | `opt_pcr_bullish=+22.34` — 대상 피처 미포함 → ❌ |
| ② EKS P3 임계 | GAP_OPEN 봉 부족으로 P3 자체 실행 안됨 → ❌ |
| ③ CoherenceGate 차등 | 09:08, 09:27 차단 로그 확인 → ✅ |
| ④ ShortHorizonOverride | 로그 없음 (FLAT 연속 아닌 dir=-1 반복) → 미발동 |
| ⑤ Platt 보정기 | 복원/저장 로그 없음 → 미작동 |
| ⑥ PCR 감쇠 | `opt_pcr_bullish` D_FORCE 당시 trigger_reason이 cvd → 미발동 |

| 개선 (132차) | 실제 동작 |
|---|---|
| min_conf KeyError 수정 | 08:45 기동(패치 前)에서 발생, 09:13 재시작 후 적용 → ✅ |
| EKS bars=3 조건 | 09:13+ 재시작 후 bars=0 → 판정 유예 반복 → ⚠ 추가 패치 필요 |
| CB⑤ 완화 구간 09:10 | S2=5~9초 지연으로 CB⑤ 13회 발동 → 여전히 심각 |

### 133차 패치 3종

| 패치 | 대상 | 파일 |
|---|---|---|
| DFORCE_EXCLUDE_FEATURES | is_open_volatile, opt_pcr_bullish/bearish D_FORCE 제외 | settings.py, multi_horizon_model.py |
| opt_pcr_bullish/bearish CLIP | (0.0, 1.0) 추가 | settings.py |
| EKS 09:15+ 재시작 | GAP_OPEN 봉 없으면 미발동 확정 | system_health.py |

---

## 2026-06-09 (132차 — 장전/장시작 연쇄 오류 7종 패치)

**Work**: 금일 장전·장시작 로그 2회 분석 → 이상점 7종 근본 원인 파악 + 즉시 패치.

### 한 것

**1차 로그 분석 (08:46~09:02)**

- [A] **이상점 분석** — 3종 이상점 연쇄 구조 파악
  - `EarlyWarmup scaler 노후=16h` → 08:45 전날 데이터로 refit → `Canary z경고=12개` (당일 분포 괴리)
  - `파이프라인 6133ms` → CB⑤ 5분 정지
  - `ERR-FATAL: 'min_conf'` KeyError × 2회 → 자동진입 OFF + 15분 쿨다운

- [수정1] **ensemble_decision.py 조기 반환 dict에 min_conf 추가** — `active_horizons` 전체 차단 시 FLAT 반환하는 dict에 `min_conf`, `trend_boost_applied` 등 정규 키 전부 추가. **ERR-FATAL 근본 원인 제거.** (`model/ensemble_decision.py:290`)

- [수정2] **main.py decision["min_conf"] → decision.get() 안전 접근** — 방어 레이어 추가. `_zone_mc = get_zone_min_confidence(…)` 로 fallback. (`main.py:3606`)

- [수정3] **Canary z경고 임계 EarlyWarmup 후 완화** — `_early_warmup_started=True` 시 임계 5→12개. 전날 scaler 기반 장전 z-score 괴리는 구조적 현상이므로 허위 알림 억제. (`main.py:2325`)

- [수정4] **CB⑤ 장 시작 구간 임계 완화** — 09:00~09:02 구간 5000ms → 9000ms. EarlyWarmup·ScalerWarmup·GBM PreRetrain 동시 부하 대응. (`safety/circuit_breaker.py:408`)

**2차 로그 분석 (09:06)**

- [B] **이상점 분석** — EKS·Degraded Mode 연쇄 오발동 구조 파악
  - 09:01-02 ERR-FATAL → `record_gap_open_bar` 미호출 → GAP_OPEN bars=1
  - 09:04-05 파이프라인 지연 → HealthPolicy CRITICAL × 2 → `warn_streak=2.0`
  - 09:06: EKS 발동(bars=1, conf=39.6%) + Degraded Mode 동시 진입 → 당일 관망

- [수정5] **EKS 최솟 bars=3 조건 추가** — `EKS_MIN_BARS=3`. bars < 3이면 발동 유예, 경고만 기록. ERR-FATAL로 GAP_OPEN 데이터 부족 시 당일 관망 오선언 방지. (`safety/system_health.py:84`)

- [수정6] **Degraded Mode 장 시작 10분 유예** — 09:00~09:10 이내 `warn_streak` 임계 도달해도 Degraded Mode 진입 차단. 파이프라인 버스트→CRITICAL→Degraded 경로 봉쇄. (`main.py:1231`)

- [수정7] **CB⑤ 완화 구간 09:10으로 확장** — 09:02→09:10. 오늘 09:06도 5591ms였으므로 ERR-FATAL 복구까지 실제 10분 소요. (`safety/circuit_breaker.py:408`)

### 수정 파일 목록

| 파일 | 수정 |
|---|---|
| `model/ensemble_decision.py` | 조기 반환 dict min_conf 등 누락 키 추가 |
| `main.py` | decision.get() 안전 접근, Canary z임계 완화, Degraded Mode 유예 |
| `safety/circuit_breaker.py` | CB⑤ 완화 구간 09:00~09:10 |
| `safety/system_health.py` | EKS_MIN_BARS=3 조건 추가 |

### 현재 상태

오늘 장에서 ERR-FATAL → EKS → Degraded Mode 3중 연쇄로 사실상 전일 관망.  
수정 1~7 적용 후 내일 장에서 정상 운영 여부 확인 필요.  
GBM 재학습(131차 미완료) 여전히 필요.

---

## 2026-06-08 (131차 — 진입0 분석 + 5종 패치)

**Work**: 6/8 진입0(A/B/C 0건) 원인 분석 → 패치 5종 구현.

### 한 것

- [A] **6/8 진입0 원인 분석** — grade: A=0, B=0, C=4(1.2%), X=331(98.8%). 주원인 3가지 특정
  - CascadeCoherence FL 끼임: 125건(37%) — 30m/15m/10m=DN, 5m/3m=FL → score=0.17 → 임계 차단
  - 신뢰도 미달: 161건(48%) — conf 평균 33.2% vs mc=42% (MC_FLOOR가 실 conf보다 높음)
  - CORE CVD/OFI 불일치: 22건(7%)

- [B] **mc=62% 소스 추적** — 11:51 OTHER 전환 후 62%가 Checklist에 적용됨. 코드 상 65%가 나와야 하지만 62%가 로그에 기록. 산술적으로 설명 불가한 값. 단, OTHER는 allow_new_entry=False 구간이므로 실제 진입에 무관. 부수적으로 _restore_mc_from_history SELECT 버그(base_mc 누락) 발견

- [C] **131차 패치 5종 구현 및 커밋** (커밋: )
  - CascadeCoherence FL 제외: directional 호라이즌만 집계 (오늘 케이스 0.17→1.00)
  - CascadeCoherence 임계값: 0.34→0.25
  - MC_ABS_FLOOR: 0.42→0.25, REGIME_MIN_CONF NEUTRAL/RISK_ON 동기화
  - BiasReset coldstart FL 기준: 10분→5분 (startup_warmup 구간 한정)
  - CORE CVD/OFI: 강제X→pass_count-1 (VWAP는 강제X 유지)
  - 부록: _restore_mc_from_history SELECT base_mc 누락 버그 수정

---

## 2026-06-08 (130차 — CVD SHAP 복구 + SHAP 추천 3단 개선 + 코드 정리)

**Work**: 동적 피처(SHAP) 탭 3가지 실질적 문제 점검 및 전면 수정.

### 한 것

- [A] **CVD 다이버전스 SHAP 기여도 복구** — rank 63/101 → 재학습 후 상위 예상
  - `features/technical/cvd.py`: signal_strength 공식 버그 수정. `cvd_slope / price_slope` (단위 불일치: 계약수 ÷ 포인트 = 항상 1000배 이상 → clamped to 3 → strength=1.0 이진화) → `abs(cvd_slope_norm)` (이미 일중 max 대비 정규화된 값)
  - `features/feature_builder.py`: buy_vol fallback `vol/2` (delta=0 → CVD 고착) → 가격기반 추정 `vol × (close-low) / range`. cvd_divergence 부호 수정 (다이버전스=음수, 동방향=양수)
  - `data/db/raw_data.db`: 72,591봉 소급 재계산 (backup: `.bak_20260608_151648`). 이진값 2종 → 1,789 unique값, -1~+1 연속

- [B] **"현재 세트 재학습" 버튼 영구 비활성화 버그 수정**
  - `main.py` `_on_gbm_retrain_done`: 재학습 완료(성공/실패 모두) 후 `_update_shap_dashboard()` 호출 추가 → 장 마감 후에도 버튼 enabled 복원
  - `main.py` `_on_force_feature_retrain_requested`: 진입 로그 + try-except 추가 (무음 실패 방지)

- [C] **SHAP 추천 알고리즘 3단 개선** (`learning/shap/shap_tracker.py`)
  - Layer 1: `update()` 주별 deduplication — 같은 week 엔트리는 최신으로 교체 (기존: 12개 모두 week 24 중복 저장)
  - `_load_history()`: 파일 로드 시에도 주별 dedup 적용 (기존 JSON 12개 → 1개로 축약)
  - Layer 2: `_find_declining_features()` 주별 dedup + "4연속 하락" → "4회 중 3회 이상" 완화 (노이즈 1회 허용)
  - Layer 3: `weekly_review()` 절대값 임계 추가 (importance < mean×0.3 → 즉시 후보), 대상 하위 20%로 확대, 최대 3개 후보
  - `_suggest_replacement()`: `already_suggested` 파라미터로 후보마다 다른 교체 피처 반환

- [D] **update_shap 3중 정의 → 1개로 통합** (`dashboard/main_dashboard.py`)
  - 제거: 죽은코드 (core_vals/rank_vals 미정의 → NameError), 중간버전 (action_state 없어 버튼 상태 미갱신)
  - 유지: action_state 포함 완전 버전 (btn_apply_candidate·btn_force_retrain·btn_reset_feature_set 상태 갱신)
  - 잘못 배치된 `# 패널 4: 청산 관리 패널` 주석도 함께 제거

### 다음 할 것

- [X] **앱 재시작 후 GBM 재학습** — cvd_divergence 연속값 DB를 모델이 학습해야 SHAP 개선 반영
- [DONE 2026-06-08] **`_up_r` UnboundLocalError 조사 완료** — 129차에서 이미 수정됨. 상세: 아래 131차 세션 참조

---

## 2026-06-08 (131차 — `_up_r` UnboundLocalError 근인 조사)

**Work**: 13:06~13:11 SYSTEM 로그 `UnboundLocalError: local variable '_up_r' referenced before assignment` 발생 원인 분석.

### 조사 결과

**버그 발생 경위**:
- 126차 코드(12:26 커밋): `_fl_r = 0.0`만 초기화. `_up_r`/`_dn_r`은 `if _tot >= 15:` 블록 안에서만 사용 → 정상
- 13:06~13:11: **미커밋 편집 중** `_dir_bias_r = max(_up_r, _dn_r, _fl_r)` 코드를 블록 밖에 추가, 그러나 초기화는 `_fl_r = 0.0`만 남겨둔 채 실행
- `_tot < 15`인 호라이즌이 loop 첫 번째로 등장 → `_up_r` 미할당 상태로 `max()` 호출 → UnboundLocalError
- **129차(14:59)에서 수정 완료**: `_fl_r = 0.0` → `_up_r = _dn_r = _fl_r = 0.0` (main.py:2777)

**현재 상태**: 수정 완료, 재발 없음.

---

## 2026-06-08 (129차 — 3m/5m FL 편향 구조 버그 수정)

**Work**: 실세션 로그 분석(14:09~14:46) → 3m FL편향 100%, 5m FL편향 80%+ 지속 원인 파악 및 구조 버그 3종 수정.

### 한 것

- [A] **F1AdaptiveWeight FL 스킵 버그 수정** — `update()`에서 `predicted==0(FL)` 이면 return하는 코드 제거. FL만 반복 예측 시 obs 미누적 → min_obs 미달 → 동적 가중치 억제 영구 비활성 버그 근본 수정. (`model/ensemble_decision.py:139`)
- [B] **_fl_streak 임계값 70%→50%** — 3m conf 46~55% 수준의 FL 편향이 70% 임계를 못 넘어 감쇠 미발동. 50%로 낮춰 10분 연속 FL 50%+ 시 weight×0.2 감쇠 발동. (`model/ensemble_decision.py:322`)
- [C] **BiasReset 발동 조건 완화** — FL 임계 20분→10분, UP/DN 10분→5분, tot≥20→15, bias≥90%→80%. 오늘 3m FL 100%가 18분 지속돼도 BiasReset 미발동(20분 미달) 재발 방지. (`main.py:2797-2799`)

### 로그 분석 주요 발견

- 3m: 적중률 4~17%, FL편향 83~100% (26분 연속 FL만 예측)
- 5m: 적중률 16~27%, FL편향 77~92%
- 15m: 적중률 61% — 유일하게 정상 작동 (DN 방향 포착)
- 30m: 적중률 46~60% — 양호
- 1m: UP편향 65%, 적중률 23%
- SGD 비중: 30%→10% 자동 감소 (GBM 주도 전환 — GBM 자체가 FL 편향이 문제)

---

## 2026-06-08 (125차 — Extreme 피처 5종 z-score 억제)

**Work**: 대시보드 ScalerMonitor Top5 분석 → extreme 발생 피처 5종 원인 파악 및 수정.

### 수정 내역

| # | 피처 | 파일 | 변경 | 효과 |
|---|---|---|---|---|
| A | `vwap_momentum` | `features/feature_builder.py:536` | `np.clip(..., -2.0, 2.0)` 추가 | max\|z\| 46→9 이하 |
| B | `opt_pcr_extreme` | `features/options/option_features.py:65` | × 0.5 스케일 반감 | max\|z\| 16→8 수준 |
| C | `ret_1m/5m/15m` | `features/feature_builder.py:496` | ±1%/2%/5% 클리핑 | fat-tail 억제 |
| D | `cvd_direction` | `features/feature_builder.py:146` | × 0.5 → {-0.5, 0, 0.5} | max\|z\| 6.7→3.3 |
| E | 수급 8개 피처 | `features/feature_builder.py:370` | `sign × log1p(\|v\|/1000)` 로그 압축 | 드리프트 근본 억제 |

### 설계 결정

- `opt_pcr_extreme` 삭제 대신 반감: GBM/SGD 피처 벡터 순서 유지. NEXT_TODO 제거 조건(재학습 후) 유지.
- 수급 피처 클리핑 대신 로그: ±20000계약 → ±3.0으로 압축, 극단 이벤트 정보 손실 없음.

### 커밋

- 125차 커밋 (이번 세션)

---

## 2026-06-08 (123차 — 대시보드 유효성 점검 + Phase 2 bar_age 시각화)

**Work**: v8.0 구현에 따른 대시보드 전체 유효성 점검 → 이슈 2건 발견/수정.

### 점검 결과 요약

Phase 2 bar_age/BAR_CACHE_DECAY 효과가 대시보드에 미반영된 것을 발견.

### 수정 내역

| # | 항목 | 파일 | 내용 |
|---|---|---|---|
| 1 | Phase 2 bar_age 미표시 | `dashboard/main_dashboard.py`, `main.py` | PredictionPanel 호라이즌 카드에 `{_age}m전` 표시 + stale시 주황 dashed 테두리 |
| 2 | lbl_futures_code 하드코딩 | `dashboard/main_dashboard.py` | "F202606" → `_MARKET_SYMBOLS` 기반 동적 계산 |

### 주요 변경

**bar_age 시각화** (`PredictionPanel.update_data`):
- 시그니처: `bar_ages: dict = None` 파라미터 추가
- 각 호라이즌 카드 pct 레이블: `age > 0`이면 `"58.3% 2m전"` 형식 표시
- stale 기준: `age > h_min // 2` (30m봉 15분 초과 등) → 카드 테두리 주황 dashed + 텍스트 주황
- `update_prediction(bar_ages=None)` 어댑터 파라미터 추가
- `main.py` line 3756: `bar_ages=self._hz_bar_age` 전달

**lbl_futures_code 동적화**:
- 기동 시 `_MARKET_SYMBOLS["KOSPI200 선물"][0]`에서 텍스트 추출 → 7월 이후도 올바른 근월물 코드 표시

### 이상 없음 확인

- `update_price`: main.py 양쪽 모두 `self.realtime_data.code` 실제 전달 (기본값 F202606 미사용)
- BAR_CACHE_DECAY confidence 감쇠: horizon_proba에 이미 반영 후 대시보드 전달 (앙상블 계산 정상)
- `_update_symbol_label`: cmb_symbol 변경 시 lbl_futures_code 갱신 정상

### 커밋

- `123차 커밋` (이번 세션)

---

## 2026-06-08 (122차 — UI v7.0→v8.0 + Phase 3 깜박임 배지)

**Work**: 사용자 요청으로 대시보드 버전 표시 업데이트 + Phase 3 착수 예정 알림 배지 추가.

### 수정 내역

- 파일 주석/docstring/윈도우 타이틀/헤더 타이틀 모두 v7.0 → v8.0
- `lbl_phase3 = QLabel("Phase 3 예정")` — 주황색 배지, 제목 오른쪽 배치
- 툴팁: 착수 조건(모의투자 4주 수익 양수 + CB 작동 확인) + 구현 예정 3종 안내
- `_phase3_blink_timer` (800ms QTimer): `_blink_phase3()` 메서드로 주황↔배경색 토글

### 커밋

- `e5d5474` — 122차: UI 버전 v7.0→v8.0 표시 + Phase 3 깜박임 알림 배지

---

## 2026-06-08 (121차 — Phase 2 백필/재학습 3종 버그 수정)

**Work**: Phase 2 재학습 실행 → 3종 치명 버그 발견/수정. cp949 UnicodeEncodeError 수정.

### 버그 현황

Phase 2 재학습 실행 결과 30m 성능이 0.5841→0.4902로 급락. 원인 추적 결과 3종 버그 발견.

### 수정 내역

| # | 파일 | 버그 | 수정 |
|---|---|---|---|
| 1 | `scripts/aggregate_and_backfill.py` | raw_features_horizon에 12피처만 저장 (OHLCV 기반) | raw_features 테이블과 JOIN → 105+피처 base에 atr/bar_volume/ret_Nm 오버라이드 |
| 2 | `learning/batch_retrainer.py` | Phase 2 재학습 시 feature_names.pkl을 3m 피처 12개로 덮어쓰기 | `_load_feature_names()` 신규 → 105개 백업 후 루프 완료 후 복원 |
| 3 | `learning/batch_retrainer.py` | 3m~30m X 행렬 119~120차원 (raw_features_horizon 추가 피처 혼입) | `use_feat_names = _existing_feat_names` 105개 고정 |
| 4 | `scripts/eod_retrain.py` | ✓, − 특수문자 cp949 UnicodeEncodeError | OK, -- ASCII 대체 |

### 검증 결과 (수정 후)

```
feature_names.pkl: 105 features
gbm_1m~gbm_30m: 모두 105차원 일치
Phase 1 재학습으로 30m 복원: 0.4902 → 0.5864
```

### 커밋

- `ad44efe` — 121차: Phase 2 백필/재학습 3종 버그 수정

---

## 2026-06-06 (119차 — FeatureBuilder 양방향성 버그 수정 4건)

**Work**: FeatureBuilder 양방향성 점검 보고서 검토 → 확정 버그 수정 + 피처 개선 구현.

### 점검 결과 요약

선물 양방향성(롱/숏 대칭) 관점에서 피처 레벨과 전략 레벨을 분리 점검.
- **진입 로직** (`strategy/entry/checklist.py`): 롱/숏 조건 완벽 대칭 — 문제 없음
- **피처 레벨**: 버그 2건 + 개선 2건 발견

### 수정 내역

| # | 항목 | 파일 | 내용 |
|---|---|---|---|
| 1 | `vwap_momentum` 항상 0 버그 | `feature_builder.py:519` | `features.get("vwap")` → `features.get("vwap_position")`, `_vh[-5]>0` 조건 제거 |
| 2 | `ofi_imbalance` 방향 손실 | `ofi.py:125` | `abs(ofi_norm)/3.0` → `np.clip(ofi_norm/3.0, -1.0, 1.0)` |
| 3 | `volume_acceleration` 클리핑 | `feature_builder.py:514` | `np.clip(..., -3.0, 3.0)` 추가 |
| 4 | `queue_directional_depletion` 신규 | `queue_dynamics.py`, `feature_builder.py` | 매도호가-매수호가 고갈 방향 강도 [-1, 1] |

### 보고서에서 버그 오분류 확인

외부 보고서 2순위로 제시된 `prev_day_same_hour_ret` 계산 버그는 코드 직접 확인 결과 **버그 아님**. `timedelta(minutes=0)`은 의미없는 코드이나 `c0 = 전일 동시간-1분`, `c1 = 전일 동시간`으로 수익률 올바르게 계산됨. 가독성 개선 수준으로 재분류.

### 잔여 항목 (미구현)

- `ema_cross` 이진값 → 연속값 전환 (4순위 — 다음 세션)
- `avg_volume` 이름 분리 `bar_volume` + `avg_volume` (이동평균)
- `tick_size = 0.05` config 설정화
- shap_feature_registry에 `queue_directional_depletion` 수동 추가

---

## 2026-06-05 (118차 — daily_close Qt 메인 스레드 블로킹 버그 수정)

**Work**: UI 먹통 원인 분석 + `daily_close()` 백그라운드 스레드 분리.

### 증상 및 원인

**증상**: 미륵이 기동 후 마우스를 올리면 UI 먹통. 실제로는 기동 ~38초 뒤 자동 발생.

**타임라인**:
| 시각 | 이벤트 |
|---|---|
| 17:26:53 | 기동 |
| 17:27:31 | `_scheduler_tick` 첫 발동 (30초 QTimer) → `daily_close()` 조건 충족 |
| 17:27:32 | `[FeatureBuilder] 전일 종가 버퍼 갱신` — 마지막 로그 |
| 17:27:32~ | `retrain_now(weeks_back=10)` Qt 메인 스레드 동기 실행 → **freeze** |

**근본 원인**: `_scheduler_tick`이 Qt 메인 스레드에서 실행되고, 조건(`now≥15:40 AND is_trading_day AND not _daily_close_done`) 충족 시 `daily_close()` 직접 호출. `daily_close()`가 `retrain_now()` (10주 GBM 훈련) + `model._load_all()` + P8 스케일러 재적합을 동기 호출 → Qt 이벤트 루프 완전 차단.

### 수정 내역

| # | 내용 | 파일 |
|---|---|---|
| 1 | Qt 타이머 `_investor_timer`, `_option_chain_timer` → 스레드 분기 전 메인 스레드 stop | `main.py` |
| 2 | `_daily_close_running` 플래그 추가 → 재진입 방지 | `main.py` |
| 3 | `_daily_close_done = True` 즉시 선점 → 30초마다 반복 진입 방지 | `main.py` |
| 4 | `daily_close()` 전체를 `DailyClose` 데몬 스레드로 실행 | `main.py` |
| 5 | `_pre_market_done/stage1_done` 리셋을 스레드 finally로 이동 | `main.py` |

### 참고 — 117차 STEP 3/EOD 직렬화와의 관계

117차에서 `_gbm_retrain_done_event.wait(timeout=40*60)` 를 `daily_close()` 안에 추가했는데, 이제 `daily_close()` 자체가 백그라운드 스레드에서 실행되므로 해당 wait도 Qt 메인 스레드를 블록하지 않아 안전.

---

## 2026-06-05 (117차 — 종료 흐름 구조 수정 + microprice 버그 방어)

**Work**: 금일 로그 이상점 전수 점검 + STEP 3/EOD 재학습 경합 근본 수정 + microprice debug log 방어.

### 이상점 점검 결과

| 시각 | 이상점 | 조치 |
|---|---|---|
| 13:47~13:54 | microprice KeyError ERR-FATAL 8회 | debug log `.get()` + try/except 추가 (코드 수정) |
| 15:29~15:50 | STEP 3/EOD 재학습 경합 — 15m/30m/RF EOD 미반영 | `_gbm_retrain_done_event` 직렬화 구현 |
| 12:43~14:30 | S2 5000ms+ 지연 / 13242ms 최대 | 116차 DB 배치화 효과 내일 실측 필요 |
| 하루 종일 | EffectReports IndexError 반복 | 116차 수정 세션 여부 불명 — 내일 확인 |

### 수정 내역

| # | 내용 | 파일 |
|---|---|---|
| 1 | microprice debug log 방어 — 18개 키 직접 참조 → `.get(, 0.0)` + try/except | `features/feature_builder.py` |
| 2 | `_gbm_retrain_done_event` 초기화 (init에 set 상태로) | `main.py` |
| 3 | 재학습 시작 4곳 `.clear()` — 수동/장중재시작/PreRetrain/STEP 3 | `main.py` |
| 4 | `_on_gbm_retrain_done` `.set()` — daemon 완료 시 Event 해제 | `main.py` |
| 5 | `daily_close()` STEP 3 완료 대기 블록 — 최대 40분 `Event.wait()` | `main.py` |

### 설계 정리 (개념 문서화)

- STEP 3 재학습: 장중 주기 (daemon thread, _gbm_retrain_running 플래그)
- EOD 재학습: 15:40 daily_close() 동기 호출 — 오늘 데이터 전체 반영 확정
- EarlyWarmup(08:45): 스케일러만 재적합, 매 영업일 발동 (age > 4h)
  - Canary stale 해소가 목적 → 08:55 90초 대기 없이 즉시 PreRetrain 진입 가능
- PreRetrain(08:55): GBM 전체 재학습, `_warmup_retrain_pending=True` 시만 발동 (재시동 후만)
- should_retrain_weekly/monthly: 조건 시간대가 파이프라인 실행 전이라 사실상 미발동 (레거시)

---

## 2026-06-05 (116차 — subprocess/DB 병목 수정 + 로그 레벨 정비)

**Work**: 장 중 WARN.log 분석. EffectReports subprocess IndexError, 파이프라인 13초 지연(CB 발동), BrokerSync 과다 경고 3건 모두 수정.

### 수정 내역

| # | 증상 | 원인 | 수정 |
|---|---|---|---|
| 1 | `[EffectReports] run failed ... IndexError` | Python 3.7 32bit `text=True` pipe → 한글 출력 UnicodeDecodeError → `_readerthread` buffer 비어 → `stdout[0]` IndexError | `main.py` `_run_effect_report_script`: `capture_output=True, text=True` → `stdout=PIPE, stderr=PIPE` + 수동 decode (utf-8→cp949 fallback) |
| 2 | 146KB ConstOut 스팸 | `run_microstructure_ab_backtest.py`가 과거 prediction 전수 순회 시 `EnsembleDecision.compute()`가 매 row마다 `SIGNAL` logger에 `[ConstOut]` WARNING 발생 | 스크립트 상단 `logging.getLogger("SIGNAL").setLevel(logging.ERROR)` 추가 |
| 3 | `[PipePerf] total=13242ms` → CB 5분 진입 정지 | `db_utils.get_conn()` 매 호출마다 SQLite 연결 오픈. Windows Python 3.7 32bit = 연결 1회 ~260ms. STEP 1 24연결=6250ms, STEP 9 7연결=1753ms, STEP 4 2연결. | `verify_and_update` 배치화(24→2연결), `save_step9_batch` 신규(7→1연결), `save_candle_and_features` 신규(2→1연결) |
| 4 | BrokerSync WARNING 과다(5개/회) | `before=FLAT + rows=0` 모의투자 정상 응답을 WARNING으로 기록 | `before=FLAT` 조건 시 WARNING→DEBUG/INFO. 실전 포지션 보유 중 rows=0은 WARNING 유지 |

### 예상 효과

- 파이프라인 13242ms → ~2500ms (CB_PIPE_PAUSE_MS 5000ms 이하 복귀)
- WARN.log 노이즈 대폭 감소

### 변경 파일

- `main.py`, `learning/prediction_buffer.py`, `utils/db_utils.py`, `scripts/run_microstructure_ab_backtest.py`, `dashboard/main_dashboard.py`

---

## 2026-06-05 (115차 — Extreme 피처 절대값→상대값 정규화 전면 구현)

**Work**: 스케일러 extreme 피처 Top5(microprice z7.42, toxicity_cancel_stress z7.60, mlofi_slope z7.31, quality_investor_age_sec z7.08, vwap z6.73) 원인 분석. 91개 피처 전수 조사 후 절대값 14개 식별. 7종 개선 구현. 재훈련 완료.

### 구현 내용

| 작업 | 파일 | 내용 |
|---|---|---|
| **Phase 1: SCALER_CLIP_FEATURES 확장** | `config/settings.py` | microprice(1150~1500), vwap(동일), toxicity_cancel_stress(0~0.5), quality_investor_age_sec(0~180), quality_macro_age_sec(0~3600), macro_vix_abs(10~60), feature_recoverable_errors(0~3), mlofi_slope ±500→±300 |
| **Phase 2-A: macro_vix_abs 제거** | `features/macro/macro_feature_transformer.py`, `shap_feature_registry.json` | macro_vix 정규화 피처로 완전 대체. 파생 정보 손실 없음 |
| **Phase 2-B: feature_recoverable_errors 제거** | `features/feature_builder.py`, `shap_feature_registry.json` | feature_degraded 0/1 플래그로 충분, σ≈0 z폭발 원천 제거 |
| **Phase 4: Gap Offset 구현** | `model/multi_horizon_model.py`, `main.py` | 장 시작 첫 분봉 close를 기준으로 microprice/vwap offset 보정. Phase 2-C/D 완료 전 임시 방어 |
| **Phase 2-C/D: microprice/vwap 절대값 제거** | `features/feature_builder.py`, `shap_feature_registry.json` | 파생 피처(bias/slope/depth_bias, position/above_vwap)로 완전 대체 |
| **Phase 3-A: cvd/cvd_slope 일중 정규화** | `features/technical/cvd.py`, `features/feature_builder.py` | cvd_norm = cvd / daily_max, cvd_slope_norm 동일. 피처명 유지(cvd, cvd_slope) |
| **Phase 3-B: queue 비율화** | `features/technical/queue_dynamics.py`, `features/feature_builder.py` | depletion_ratio = depletion/(depletion+refill), refill_ratio 동일. 유동성 수준 독립 |

### 추가 작업

- `docs/260605_FEATURE_NORMALIZATION_PLAN.md` 신규 — 피처 분류, 구현 계획, 재훈련 방법 포함
- `scripts/eod_retrain.py` 신규 — 장 마감 후 독립 실행 EOD 재학습 스크립트
- `EOD_RETRAIN.bat` 신규 — 더블클릭 실행 배치 파일

### 재훈련 결과

| 항목 | 값 |
|---|---|
| 데이터 | 16,406행 × 105피처 (cutoff 2026-03-27) |
| 소요 시간 | 1830초 (30.5분) |
| 성공 호라이즌 | 6/6 |
| GBM acc | 1m 0.4287 / 3m 0.5527 / 5m 0.5692 / 10m 0.5798 / 15m 0.5905 / 30m 0.5841 |
| RF OOB | 1m 0.456 / 3m 0.375 / 5m 0.388 / 10m 0.445 / 15m 0.461 / 30m 0.499 |

### 발견된 이슈

1. **feat=105(GBM) vs feat=118(ScalerWarmup) 불일치**: 오늘 장 중 DB에 저장된 과거 행에 microprice/vwap 등 이전 피처 포함. 내일부터 새 피처 구조 데이터 축적 시 자연 해소.
2. **cvd/queue 변환 데이터 혼재**: DB 과거 데이터는 절대값(cvd~±50000), 오늘 이후는 정규화값(-1~+1). 첫 재훈련은 혼재 데이터로 학습됨. 2~3일 후 DB 데이터 교체되면 정상화.
3. **재훈련 30분 소요**: n_estimators=300 + 16,000봉 × 24 fit. 장 중 강제 재훈련 시 CB⑤ 위험.

---

## 2026-06-05 (114차 — 재학습 피처셋 불일치 사고 분석 + P0~P4 개선)

**Work**: 금일(2026-06-05) 12:19:53 `reset to baseline` 이후 ScalerWarmup 입력이 feat=108→85로 급감하고 long 50분 정확도가 14~20%로 붕괴한 원인을 로그 3중 분석. 원인 계층(4레이어)을 특정 후 P0 긴급 수동 복구 + P1~P4 코드 개선 4종 구현.

### 이상점 타임라인

| 시각 | 이벤트 |
|---|---|
| 08:55 / 12:03 | 배치 재학습 시작 → 피처 12627/12605 < 15000 → 즉시 실패 |
| 12:19:53 | `[FeatureOps] 재학습 진행 중 - reset to baseline feature set` → registry.active_features 87개로 저장 |
| 12:39 | ScalerWarmup feat=108 → **feat=85** 전환 (registry 기준 필터) |
| 12:39~ | long 50분 정확도 14~20%로 급락 (scaler 0-패딩 왜곡) |
| 13:03 | P0 복구 적용 후 feat=105 복귀 확인 |

### 원인 계층 분석

| 레이어 | 원인 |
|---|---|
| L1 | `load_features_for_warmup`이 registry.active_features(87개)로 raw feat_names 필터 |
| L2 | `refit_scalers_only`에서 85→105 0-패딩 → scaler 왜곡 |
| L3 | `_on_reset_feature_set_requested`가 active_features를 먼저 저장, 재학습 실패해도 롤백 없음 |
| L4 | `weeks_back=8` 실측 12,605봉 < MIN_TRAIN_BARS 15,000 → 재학습 구조적 실패 |

### 구현 내용

**P0 긴급 수동복구** (`_fix_registry_p0.py`):
- `shap_feature_registry.json` active/baseline_features 87→105개로 교체
- 백업: `shap_feature_registry.json.bak_20260605_125941`

**P1** `learning/batch_retrainer.py:436-473`:
- `load_features_for_warmup`에서 managed_feats(registry 필터) 블록 전체 제거
- ScalerWarmup은 raw feat_names 그대로 반환, `refit_scalers_only`에서 model 기준 align

**P2** `main.py`:
- `_on_reset_feature_set_requested`: 변경 전 `self._reset_rollback_active`에 이전 active_features 저장
- `_on_gbm_retrain_done` 성공: `_reset_rollback_active = None` 클리어
- `_on_gbm_retrain_done` 실패: registry 이전 값으로 롤백 + WARN 로그

**P3** `model/multi_horizon_model.py`:
- `_check_registry_feature_consistency()` 신규
- `_load_all()` 이후 호출, registry.active_features vs feature_names.pkl 개수 불일치 시 ERROR 로그

**P4** `learning/batch_retrainer.py` + `main.py` 3곳:
- `weeks_back` 기본값 8→10 (실측 ~15,750봉 → MIN_TRAIN_BARS 15,000 달성)

### 추가로 발견된 사실

- `baseline_features`가 87개로 잘못 고정됐던 이유: 과거 어느 시점 active=87개 상태에서 "현재 적용" 버튼이 눌려 baseline이 덮어써짐
- registry에만 있고 pkl에 없는 피처 3개(`ofi_raw`, `ofi_reversal_signal`, `toxicity_spread_stress`) — SHAP 심사에서 제거됐지만 registry에 잔존
- pkl에는 있고 registry에 없던 피처 21개 — baseline 관리 갭에서 누락

---

## 2026-06-05 (113차 — 실세션 로그 종합 분석 + FL 편향 고착 4종 구조 개선)

**Work**: 오늘 장(2026-06-05) 로그 전체(09:00~11:39)와 1분봉 차트를 교차 분석해 이상점 7종을 분류하고 인과 흐름을 추적. 기존 개선이력과 대조해 신규 작업 4개(P1·P2·P3·P5)를 식별·구현. P4(EarlyWarmup 가드)는 오늘 지연 원인이 EarlyWarmup이 아닌 EKS임을 확인해 취소.

### 이상점 분류

| ID | 시간 | 증상 | 근본 원인 |
|---|---|---|---|
| A | 09:11~12 | 처리 18s/45s → CB=PAUSED | EKS 발동 후 스케일러 재적합 + 파이프라인 경합 |
| B | 세션 전체 | 10m/15m FL 100% 고착 | `balanced` class_weight → 훈련 데이터 FL 과다 구간 편향 억압 불가 |
| C | 09:00~10:18 | 30m UP 편향 0% 정확도 | 8주 학습 데이터가 상승 편향 + class_weight 설정 |
| D | 10:18 | CB③ HALTED (30m=0%) | C의 연쇄 결과 |
| E | 10:30 | 세션 최저점 반전 완전 미스 | CB=HALTED + 전 호라이즌 FL 예측 동시 |
| F | 10:40~ | 5m 정확도 20%로 급락 | 10:30 반등 구간 FL 편향 전이 |
| G | 10:18~11:39 | CB③ 33~50% 진동 → 해제 불가 | RESET_MARGIN 5%p → 33% 경계 2분 연속 정상 달성 불가 |

### 이력 대조 결과

| 제안 | 판정 | 근거 |
|---|---|---|
| P1: 10m/15m class_weight 명시 | 기존 결정 번복 | 85차에서 balanced 유지 결정했으나 오늘 재발 → 새 근거 |
| P2: 편향 고착 uniform fallback | **진짜 신규** | CURRENT_STATE 1495라인 "미완료" 명시됨 |
| P3: CB③ 해제 마진 축소 | **신규 튜닝** | 이력 없음, 초기값 유지됐던 것 |
| P4: EarlyWarmup 가드 | **취소(오진)** | 오늘 원인은 EarlyWarmup이 아닌 EKS |
| P5: 15m 독립 CB 이벤트 | 인식됐으나 미구현 | DECISION_LOG 1007라인 "CB③이 5m편향 포착 불가" |

### 구현 내용

#### P1 — `learning/batch_retrainer.py`
```python
_CW_10M = {DIRECTION_FLAT: 0.80, DIRECTION_UP: 1.10, DIRECTION_DOWN: 1.10}
_CW_15M = {DIRECTION_FLAT: 0.75, DIRECTION_UP: 1.15, DIRECTION_DOWN: 1.15}
```
`_make_sample_weight()` 10m/15m 분기 추가. `compute_sample_weight("balanced")` 제거.

#### P2 — `main.py` 4곳
- `__init__`: `_bias_fl_streak: dict`, `_bias_override_horizons: set` 추가
- bias 감지 블록 (STEP 1 후): FL 90%+ AND tot≥20 AND 연속 20분 → `_bias_override_horizons.add(h)` + `[BiasReset]` 로그 + `circuit_breaker.record_horizon_fl_bias()` 호출
- STEP 5 블렌딩 직후: `if h_name in self._bias_override_horizons` → `{1/3, 1/3, 1/3, direction:0, conf:1/3}` 치환
- `reset_daily()`: `_bias_fl_streak`, `_bias_override_horizons` 리셋

#### P3 — `config/settings.py`
```python
CB_CB3_WARN_RESET_MARGIN = 0.03  # 0.05 → 0.03 (28%+5%=33% 경계 진동 해소)
```

#### P5 — `safety/circuit_breaker.py`
- `__init__`: `_horizon_fl_bias_streak: dict`, `_horizon_fl_bias_warned: set` 추가
- `record_horizon_fl_bias(horizon, fl_ratio, streak)` 신규 메서드: streak≥30 시 CRITICAL 로그 + Slack
- `reset_daily()`: 두 변수 리셋

### 수정 파일

| 파일 | 변경 내용 |
|---|---|
| `learning/batch_retrainer.py` | `_CW_10M`, `_CW_15M` 추가, `_make_sample_weight` 10m/15m 분기 |
| `main.py` | `_bias_fl_streak`, `_bias_override_horizons`, bias override 로직, STEP 5 치환, reset |
| `config/settings.py` | `CB_CB3_WARN_RESET_MARGIN` 0.05→0.03 |
| `safety/circuit_breaker.py` | `record_horizon_fl_bias()`, FL bias 추적 상태변수, reset |

---

## 2026-06-05 (112차 — 실시간 로그 분석 + 개선이력 대조 + 신규 버그 3종 수정)

**Work**: 오늘 장(2026-06-05) 로그를 6개 이상점으로 분류하고 인과 흐름을 추적. 기존 개선이력과 대조해 실질 신규 작업 3개를 식별하고 즉시 구현.

### 이상점 요약 (로그 기반)

| 시간 | 이벤트 | 원인 |
|---|---|---|
| 08:55 | Canary: scaler_age=17h, z경고=9개 | 전날 장 마감 후 scaler 미갱신 |
| 09:05 | EKS 발동 (conf_max=36.8%) | scaler 노후로 conf 구조적 저하 |
| 09:11~09:44 | CB⑤ 4회 + 파이프라인 지연 반복 | scaler 재적합 daemon과 GBM 연산 경합 추정 |
| 09:21 | EKS 해제 (scaler_age=0.1h, conf=44.2%) | 재적합 후 정상화 — P3 완화 조건 동작 확인 ✅ |
| 09:41 | ShadowSession BLOCKED (acc30m=16.7%) | 09:40 이전 게이트 미통과 |
| 10:16 | CB③ RESTRICTED (acc30m=0.0%) | 5m 모델 상수 출력 오염 추정 |
| 10:18 | CB③ 당일 정지 | acc30m 0% 2회 연속 |
| 10:27 | ConstOut [5m] 감지 → 재적합 시작 | CB③ 정지 이후 사후 감지 |

### 개선이력 대조 결과

| 제안 | 판정 | 비고 |
|---|---|---|
| 장전 재적합 | **신규 gap** | EarlyWarmup 구현됐으나 >24h 조건이 ~17h 케이스를 커버 못 함 |
| CB③ 샘플 수 가드 | **신규 레이어** | 온라인 러너엔 있으나 CB③ 차원 가드 없음 |
| EKS-acc30m 연계 | 낮은 우선순위 | ShadowSession+CB③ 이중 방어 중 |
| STEP별 타이머 | 기존 구현됨 | 107차 완료(DEBUG 레벨) — 개선 불필요 |
| ConstOut N 단축 | 낮은 우선순위 | ShortHorizonOverride가 대안, 근본은 scaler |
| Contrarian streak 버그 | **신규 버그** | CLEARED→WATCHING 시 streak 미리셋으로 즉시 재진입 |

### 구현 완료

| 작업 | 파일 | 내용 |
|---|---|---|
| P1: EarlyWarmup 24h→4h | ,  |  추가, 매 영업일 장전 항상 발동 |
| P2: CB③ 샘플 수 상향 | ,  | ,  두 곳, 경고·HALT에  표시 |
| P6: Contrarian streak 리셋 |  | CLEARED→WATCHING 시 streak/last_dir/active_dir 리셋 |

### 110차 개선 검증 결과

-  — P3 완화 조건(max(mc,0.42)) 동작 확인 ✅
- , , ,  — 당일 정지로 진입 없어 미발동, 다음 장 재확인 필요

---

## 2026-06-04 (111? ? ??? ??? ?? ???? ?? ?? + ???? ?? ??)

**Work**: ??? ??? ??? ?? ?? ???? ?? ????. `?? conf ? ???? ??` ???? ?? ??? ????, 8?? ?? ??/?? ??/??? ????, `?? ???` ??? ??? ??? ??? ??? ???? ????. ????? `????` ??? ?? ?? ??? ?? ????? `trades.db` + ?? `TRADE.log` ??? ????.

### 1. UI ?? ??

| ?? | ?? |
|---|---|
| `?? ???` ?? | ?? 2? ?? ??, 1? ?? ? ??? ??? |
| `?? conf ? ???? ??` | `??/conf` 2? ? ? `??/conf/mc/?/dir/grade/gate/meta-tox/????` ?? |
| `mc ?? ??` | ?? ?? ? ???? ?? ?? |
| ??? ?? | `QLabel` ? read-only `QTextEdit`, ??? ?? |

### 2. ???? ?? ??

- 8?? ?? ??? ??? ??
- ?? ?? ??? 8?? ??? ?? ?? ??
- `meta/tox` ?? `meta_action/meta_confidence`, `toxicity_action/toxicity_score` ?? ??
- ??? ? ? ??, ??? ??/?? ??

### 3. ???? ?? ??

**Files**: `dashboard/panels/dynamic_mc_panel.py`

- `trades.db`? `entry_ts/direction/quantity/grade/had_partial_fill` ??
- ?? `logs/YYYYMMDD_TRADE.log` ?? `[????]`, `[??????]`, `[?????] ????` ?? fallback ??
- `ensemble_decisions.ts` ? ????? ? ?? ?? `?2?` ?? ??
- ?? ?? ??? ??? ?? ???? ??? `8. ????` ??
- `????` ? ??? ????/??/??/???? ??/?? ?? ??

### 4. ?? ??? ?? ??

- `predictions.db` ?? 2026-06-04 `ensemble_decisions` 387? ??
- `trades.db` ?? 2026-06-04 ?? 0?
- `20260604_TRADE.log` ?? `????/??????/????` ?? ??
- ??? ?? ???? `8. ????` ???? **?? ?? ?? ??? ??**? ??

### 5. ??

- `python -m py_compile dashboard\panels\dynamic_mc_panel.py`
- `trades.db` ??? ??
- 2026-06-04 ?? `ensemble_decisions` ?? / `trades` ?? ?? ??

---

## 2026-06-04 (110차 — 진입0 6중 원인 분석 + 개선 6종 전면 구현)

**Work**: 오늘 장 전체 로그(SIGNAL/WARN/SYSTEM) 3중 교차 분석 → 진입0 원인 체계화 → 개선 6종 구현 + 구문 검증.

### 1. 진입0 타임라인 재구성

| 시각 | 이벤트 |
|---|---|
| 09:05 | EKS 발동 conf_max=40.2%, core_pass=0/5봉 → 첫 세션 전체 차단 |
| 09:21 | TrendGate ON streak=10 — 이미 EKS 차단 상태라 무력 |
| 10:53 | 재기동 — DynMC 복원 (mc 43.0~43.9%) |
| 12:45~13:15 | conf 43~45% 달성 — 전부 dir=+0 (FLAT) → 진입 불가 |
| 13:43~13:46 | opt_pcr_slope_norm z=+9.21, ofi_imbalance z=+6.35 동시 폭발 |
| 15:10 | 강제 청산 (포지션 없음) |

실제 차트: 09:00~09:40 +27pt, 11:30~14:00 +35pt — 41pt 레인지 전부 관망.

### 2. 개선 6종 구현

| # | 파일 | 내용 |
|---|---|---|
| ① | `config/settings.py` | `opt_pcr_slope_norm: (-3.0, 3.0)` → SCALER_CLIP_FEATURES 추가 |
| ② | `safety/system_health.py`, `main.py` | EKS P3 해제 임계값 고정 0.50 → `max(mc, 0.42)` |
| ③ | `model/ensemble_decision.py` | CoherenceGate: GAP_OPEN·TrendGate ON 구간 0.60→0.50 |
| ④ | `model/ensemble_decision.py` | ShortHorizonOverride: FLAT 5봉+ 연속 + 1m/3m+OFI/CVD 합의 → 방향 채택 |
| ⑤ | `learning/calibration.py`, `main.py`, `config/settings.py` | Platt 보정기 save/load 영속화 — 재시동 시 pkl 복원 |
| ⑥ | `model/multi_horizon_model.py` | D_FORCE opt_pcr 발동 → 30분간 opt_pcr_* 피처 0.3× 감쇠 |

### 3. 핵심 분석 발견

- **캘리브레이션 문제**: calibration_metrics.json ECE=0.250. conf=45% 출력 시 실제 acc=36.3%(bin=4). mc 기준 자체가 실제 정확도와 단절되어 있음.
- **PCR 후행 구조**: opt_pcr_slope_norm은 선물 가격 대비 1~2시간 후행. OFI(실시간 호가)와 충돌 시 방향 소거 구조적 문제.
- **EKS P3 임계값 과도**: conf>=50% 고정 → 오늘처럼 conf_max=45%인 날 하루 전체 차단. mc 기반 동적 임계값으로 변경.

---

## 2026-06-04 (109차 — 진입 미발생 원인 분석 + MaskedFallback + PriceStructureBoost)

**Work**: 12:44:30 이후 로그 분석 → 진입 미발생 3가지 원인 특정 → opt_pcr 원시 데이터 검증 → 안 1(MaskedFallback), 안 2(PriceStructureBoost) 구현 + ScalerMonitorPanel 툴팁 추가.

### 1. 12:44:30 이후 로그 분석 결과

**결론**: 오늘 하루 전체 grade=X, 진입 0건. 원인 3가지 중첩.

| 원인 | 내용 |
|---|---|
| ① 앙상블 conf 구조적 저하 | dir=+0, conf=42~45% — 50% 미만이라 방향성 없음으로 판정 |
| ② TrendGate→Checklist 차단 | streak=10 발동 → dir=+1 but conf=33% < 동적임계값(42.6%) → Checklist X |
| ③ opt_pcr_slope_norm 하루 종일 \|z\|>4 | D_FORCE 매 5분 반복 — OFI 상승신호와 충돌해 방향성 희석 |

**특이점**: 13:29~13:32 `dir=+0 conf=62.2%` — 외인 풋 대규모 매수(하락 헤지) 신호가 모델에서 DOWN 방향 62%로 인식됐으나 롱 전용 시스템이라 dir=0 처리.

### 2. opt_pcr 원시 데이터 검증

**100% 실제 시장 신호** (데이터 이상 아님). 외인 옵션 포지션 구조 전환:

| 시각 | call_foreign | put_foreign | PCR | 해석 |
|---|---|---|---|---|
| 12:44 | -3,779 | -299 | 0.079 | 숏스트랭글 (콜+풋 매도) |
| 13:04 | -4,253 | +46 | 0.011 | 풋 순매수 전환 시작 |
| 13:42 | -4,117 | +1,173 | 0.285 | 풋 매수 급가속 |
| 14:24 | -4,782 | +6,008 | 1.256 | **pcr_bearish=1 발동** |
| 14:28 | -4,691 | +6,445 | 1.374 | 합성 숏 / 하방 헤지 완성 |

`opt_pcr_bearish z=+11.14` 원인: 이진 피처(0/1), 500봉 내 PCR≥1.2 사례 거의 없어 mean≈0, std≈0.09 → z=(1-0)/0.09≈11. 데이터 이상 아닌 희귀 이벤트.

### 3. ScalerMonitorPanel 툴팁 추가

`dashboard/panels/scaler_monitor_panel.py` — "오늘 refresh 이벤트" QGroupBox에 `setToolTip()` 추가. A/B/C/D 트리거 종류 + D_FORCE 발동 조건·쿨다운·반복 원인 HTML 툴팁.

### 4. 안 1 — 이상값 피처 격리 예측 (MaskedFallback)

**Files**: `model/multi_horizon_model.py`, `main.py`

- `_extreme_feat_streak` 에서 연속 5분 이상 극단인 피처 → `_chronic` 목록 추출
- `_predict_masked(x2d_proc, chronic)`: 격리 피처를 0으로 치환 후 GBM만 재호출 (수 ms)
- main.py: masked GBM + SGD 블렌딩 → `_masked_hp_blended`
- 정상 앙상블 dir=FLAT이고 masked conf − raw conf ≥ 5%p이면 masked 결과 채택
- 로그: `[MaskedFallback] ['opt_pcr_slope_norm'] 격리 → conf 43%→61% dir=+1 grade=C`

### 5. 안 2 — 가격 구조 TrendGate 부스트 (PriceStructureBoost)

**Files**: `strategy/entry/trend_persistence.py`, `main.py`

- `_price_structure(bars, n=5)`: 최근 5봉 HH-HL(+1) / LH-LL(-1) / 기타(0) 판정
- `update(features, recent_bars=None)`: streak≥5 + 가격구조 동일방향 + (OFI or CVD 동의) → `min_conf_override` 0.44→0.38 추가 완화
- main.py: `_price_struct_buf = deque(maxlen=8)` 추가, 매분 bar high/low 적재
- TrendGate 로그에 `[가격구조부스트]` 태그 추가

### 잔존 미검증

- MaskedFallback / PriceStructureBoost 효과: 다음 장 실데이터로 발동 여부 확인 필요
- opt_pcr_slope_norm 극단값: 오늘 스케일러 분포가 특수했으나 일반화 여부 미확인

---

## 2026-06-04 (107차 추가 — S2 실세션 분석 + flush_fit incremental + S1~S8 의미 정리)

**Work**: 107차 fix 적용 후 실세션(12:45~15:04) CB⑤ 재분석. flush_fit incremental 추가 최적화. PipePerf 단계 의미 정리.

### 1. S2 fix 후 실세션 분석

- S2: 4~5초 → **500~800ms** (개선 확인)
- CB⑤ 잔여 원인: S2 단독이 아닌 **S2+S6+S7 합산 초과** 구조  
  `예) total=1061ms | S2=595ms S5=122ms S6=181ms S7=143ms`
- S6 스파이크(14:36 1113ms): ConstOut D_FORCE 이후 백그라운드 CPU 경합 추정
- S7: 진입 실행+대시보드 갱신 합산 (100~250ms)

### 2. flush_fit incremental 최적화 (commit `16ab6cd`)

- 기존: `_partial_fit()` 매번 `_X_buf[-100:]` 100샘플 전체 재학습 (~700ms)
- 개선: `_partial_fit_incremental(n_new)` — 신규 6샘플만 학습 (~40ms)
- `_last_fit_count` 추가로 flush 주기 내 신규 샘플 수 추적
- 초회(not _fitted)는 전체 배치 1회 유지

### 3. PipePerf 단계 의미 정리 (S1-8의미.txt)

| 마커 | 내용 |
|---|---|
| S2 | SGD 온라인 자가학습 |
| S6 | 앙상블 진입 판단 (방향·신뢰도·등급·Checklist·MetaGate·TrendGate) |
| S7 | 진입 실행 + 대시보드 전체 갱신 |
| S8 | 청산 트리거 감시 |

---

## 2026-06-04 (107차 세션 마무리 — 재시동 점검 완료 + EffectReports 에러 분석)

**Work**: 10:53:33 재시동 후 107차·106차 수정 내용 전수 확인. EffectReports 에러 원인 분석 및 진단 로그 개선.

### 1. 10:53:33 재시동 후 점검 결과

| 확인 항목 | 기준 | 결과 |
|---|---|---|
| 버그 #1 (CybosApiConnector NameError) | NameError 없음 | ✅ WARN 전체 없음 |
| 투자자 수급 | `source=CpSvrNew7221 supported=True` | ✅ 10:53:33~ 정상 |
| S2 속도 | PipePerf S2 ≤ 1000ms | ✅ 재시동 후 PipePerf 경고 0건 (재시동 전: 3,700~7,000ms 매분) |
| DivergencePanel | 매분 수급 반영 | ✅ 10:54~ div=+260, futures(fi/rt/inst 정상) |
| OptionChain stale 복구 | stale 감지 후 refresh | ✅ 10:18 stale 감지→refresh, 이후 10:23/33/43/58 정상 갱신 |

### 2. EffectReports `list index out of range` 분석

**현상**: `generate_rollout_readiness_report.py`, `run_microstructure_ab_backtest.py` 2종이 09:00~15분 주기로 실패.
에러 메시지: `[EffectReports] run failed <script>: list index out of range` (except 블록 로그 형식 = subprocess.run() 자체 예외).

**직접 실행 결과**: 두 스크립트 모두 직접 실행 시 성공 → 스크립트 코드 자체는 문제 없음.

**핵심 관찰**:
- `generate_calibration_report.py`, `generate_meta_gate_tuning_report.py` → 성공 (비교군)
- 실패 2종만 `ensemble_decisions`/`meta_labels`/`raw_data.db` 추가 접근 또는 EnsembleDecision 임포트
- 스크립트 자체는 성공하므로 main.py 실행 중에만 재현 (장 시간 중 DB 잠금 등 가능성)

**조치**: `main.py:4769` except 블록에 `traceback.format_exc()` 추가. `rc != 0` 브랜치에 stdout도 추가.
→ 다음 장 시간 WARN.log에서 정확한 스택 트레이스로 원인 특정 가능.

### 3. 잔존 Known Issue

- `[CybosProbe] CpSysDib.ProgramTrade dispatch/request failed (-2147221005)` — 프로그램매매 TR 미연결 (기존 known)
- `program_source=mapping_pending` — 동일

---

## 2026-06-04 (107차 — 실세션 점검 + CybosApiConnector NameError + S2 개선)

**Work**: 104~106차 개선 후 재시작(10:18) 로그 점검. 버그 2종 발견·수정.

### 1. 실세션 점검 결과 (10:18:36 이후)

**정상 확인**:
- 옵션 체인: 10:23 `[OptionChain] avail=True PCR=0.205 GEX=584B` ✅
- DynMC 기동 복원: GAP_OPEN(0.452), OPEN_VOLATILE(0.439) 등 5개 zone 복원 ✅
- ConstOut 자동복구: 10:14 1m 감지 → D_FORCE → 10:15 해소 ✅
- StuckBreaker: DN streak=8~28 감쇠 작동 ✅
- CoherenceGate: score=0.33~0.50 차단 로그 ✅

**문제 발견**:
- 투자자 수급: `[CybosProbe] CpSysDib.CpSvrNew7221 dispatch/request failed: name 'CybosApiConnector' is not defined` 매 1분 반복 → 수급 `supported=False`
- S2 파이프라인: PipePerf `S2=4~6초` 지속 → CB 경고 반복, 일부 분 CB "5회 진입 불가"
- 진입 현황: conf 33~42% < mc 43.9%, grade=X, 진입 0건

### 2. CybosApiConnector NameError 수정 (api_connector.py:921-922)

`_probe_investor_tr()` 내 `_probe_dump_done` 참조에서 클래스명 오타.
`CybosApiConnector` → `CybosAPI` (실제 클래스명은 `class CybosAPI`).
이 버그로 7221 probe가 BlockRequest 성공 후 dump 코드에서 NameError 발생 → None 반환 → 투자자 수급 미수집 유지.

### 3. S2 파이프라인 지연 원인 분석 및 개선

**근본 원인**: `MetaConfidenceLearner.record_outcome()` 호출마다 `_partial_fit()` (100샘플 × 7피처 SGD 배치) 실행.
verified 6건/분 → `record_outcome()` 6회 → `_partial_fit()` 6회/분 → S2=4~5초.

**확인 근거**: StuckBreaker로 FLAT 예측이 많아지는 09:57~10:00 구간에서 S2가 1~2초로 빨라짐.
FLAT 예측 → `meta_gate.evaluate()` early-return → `record_outcome()` 미호출 → `_partial_fit()` 0회.
세션 시작 후 약 9분(MIN_SAMPLES=50 도달) 이후부터 S2가 급격히 느려지는 패턴도 일치.

**수정**:
- `meta_confidence.py`: `record_outcome()`에서 `_partial_fit()` 직접 호출 제거 → `_fit_pending=True` 플래그만 설정. `flush_fit()` 메서드 신규 추가.
- `main.py` STEP 2 말미: `self.meta_gate.learner.flush_fit()` 1회 호출.
- 진단 로그 추가: `[S2] meta=Xms learn=Xms flush=Xms verified=N` (DEBUG.log, 500ms 초과 시).
- 예상: 6회/분 → 1회/분, S2 4~5초 → ~0.7초.

---

## 2026-06-04 (106차 — 다이버전스 패널 투자자 수급 + 옵션 체인 미수집 원인 분석·수정)

**Work**: UI 다이버전스 패널에서 투자자 수급 데이터 전체 미수집("대기") + 옵션 체인 "미수집" 원인을 조사하고 수정.

### 1. 투자자 수급 TR 오사용 버그 발견 (CpSvrNew7212 → 7221)

**조사 경위**:
- SYSTEM 로그에서 매분 `[CybosInvestorRaw] futures via CpSysDib.CpSvrNew7212 supported=False nets={}` 반복 확인
- `_probe_investor_tr`이 성공(probe ≠ None)인데도 `nets={}` → rows가 비어있거나 파싱 실패
- 대신증권 자료실(seq=85 "[파이썬] 투자자별 매매 종합 예제") 직접 확인

**버그**: 코드에서 사용한 `CpSysDib.CpSvrNew7212`는 존재하지 않는 TR명.

**정확한 TR**: `CpSysDib.CpSvrNew7221` (투자자별 매매종합서비스)
- 입력: `SetInputValue(0, ord('1'))` = 49 (선물계약 단위)
- 행(ri) = 상품종류: ri=2 → 선물, ri=3 → 옵션콜, ri=4 → 옵션풋
- 열(fi) = 투자자: fi=2 → 개인순매수, fi=5 → 외인순매수, fi=8 → 기관순매수

**수정 파일**: `collection/cybos/api_connector.py`
- `request_investor_futures()` candidates[0]: `CpSyrNew7212 (0,1)` → `CpSyrNew7221 (0, ord('1'))`
- 파싱 로직 전면 재작성: row-by-investor → row-by-product × col-by-investor
- `_7221_INVEST_INDEX` 상수 추가 (행 인덱스 의미 문서화)
- `_probe_investor_tr`: logger → system_logger, 헤더 범위 24→32, fi 범위 10→15, ri 범위 20→30, 세션 1회 raw 덤프

### 2. 옵션 체인 미수집 원인 (3가지)

**원인 1 — 캐시 stale**:
- 캐시 생성일: 2026-05-13. 현재 spot: **1385** (A0566 선물)
- 캐시 max strike: **1340** < ATM 필터 하한 1355 → `_filter_atm` 0개 반환

**원인 2 — ATM miss 시 재로드 없음**:
- `if not target: logger.warning(...); return _empty()` — stale 캐시 계속 재사용

**원인 3 — 장 시작 즉시 폴링 없음**:
- `_option_chain_timer.start(300_000)` 후 300초 대기, 즉시 1회 호출 없음
- `_investor_timer`는 즉시 `_fetch_investor_data()` 호출하는 것과 대조

**수정**:
- `option_chain_snapshot.py` `_poll()`: ATM miss → `_fetch_and_cache_chain()` 즉시 재로드 → 재필터
- `option_chain_snapshot.py` `_poll()`: valid snapshots=0 → `_chain_raw=[]` 초기화 (다음 poll 강제 재로드)
- `broker_runtime_service.py` `ensure_market_open_runtime_started()`: 타이머 시작 후 즉시 `_poll_option_chain()` 1회 호출
- `data/option_chain.json` 삭제 (stale 캐시 제거)

### 3. 로그 시스템 개선

- `option_chain_snapshot.py`: `logger("OPTIONS")` → `system_logger("SYSTEM")` (initialize/refresh/warning 전환)
- `main.py` `_poll_option_chain()` 예외 핸들링: `logger.debug` → `logger.warning`
- 진단 스크립트 `_check_7212.py` 업데이트 (7212 → 7221 기준으로 재작성)

### 4. 확인 필요 (다음 기동)

1. SYSTEM.log: `[CybosProbe] CpSysDib.CpSyrNew7221 ok status=0` 기동 직후 1회
2. SYSTEM.log: `[CybosProbe][RAW] CpSysDib.CpSyrNew7221 headers=... rows_sample=...` (raw 구조 확인)
3. DATA.log: `[CybosInvestor] futures supported=True source=CpSysDib.CpSyrNew7221 foreign=±XXX`
4. SYSTEM.log: `[OptionChain] 초기화 완료: 체인 캐시 0 종목` → 즉시 CpUtil.CpOptionCode 수집
5. SYSTEM.log: `[OptionChain] 갱신 X.Xs | PCR=... avail=True`
6. 패널 UI: 외인순매수/개인순매수/기관순매수 수치 표시 + 옵션 체인 "경신: HH:MM" 표시

---

## 2026-06-03 (103차 — 방향/진입 모델 중복 피처 분석 + 2종 구조 개선)

**Work**: 방향모델(GBM+SGD+RF+EnsembleGater)과 진입모델(Checklist+MetaGate+ExecutionGovernor+ToxicityGate) 사이의 중복 데이터 사용 3종 분석 후 우선순위 1·2 수정.

### 1. 중복 패턴 분석 (3종)

**Confidence 중복** (우선순위3 — 구조적, 유지):
- EnsembleDecision → AdaptiveGater → Checklist → MetaGate → ExecutionGovernor → PositionSizer로 5단계 통과
- 각 단계가 다른 정보(맥락·운영품질·레짐)를 사용하므로 제거 불가. P1/P2(mc 상한 캡)로 이미 경계선 상황 완화됨

**Toxicity 중복** (우선순위2 — size 0.3× 과소 축소):
- ToxicityGate(전담, 0.5×)와 ExecutionGovernor(toxicity×0.15 가중)가 동일 toxicity_score를 독립 사용
- 두 게이트 모두 reduce 시 0.5×0.6=0.3× 복합 축소

**Microstructure 중복** (우선순위1 — 진입0 직접 경로):
- EnsembleGater: mlofi_norm(28%)+cancel_add_ratio(10%) → confidence ±12%
- MetaGate: 동일 피처를 lob_imbalance/VPIN proxy로 재사용 → meta_conf 독립 산정 → blended_conf 추가 하락
- mlofi_norm 불리 시 EnsembleGater 패널티 후 MetaGate도 패널티 → blended_conf < 0.56 → action=skip → grade=X

### 2. [103-P1] Microstructure 중복 해소 — MetaGate에서 EnsembleGater 담당 피처 제거

**Files**: `learning/meta_confidence.py`, `strategy/entry/meta_gate.py`

- `meta_gate.py`: `lob_imbalance = features.get("mlofi_norm")` 및 `vpin_proxy = cancel_add_ratio/3.0` 계산·전달 제거
- `meta_confidence.py`: `build_meta_features()` 파라미터 9개→7개 (lob_imbalance, vpin 제거)
  - `_coerce_feature_vector()` len 검사: 9→7
  - `_rule_based_confidence()` 언패킹에서 lob/vpin 제거, `if vpin > 0.7` 조건 삭제
  - MetaConfidenceLearner는 메모리 내 버퍼만 유지(pkl 없음) → 재기동 시 자동 7-dim으로 재학습

**진입0 개선 메커니즘**:
- 수정 전: mlofi_norm 불리 → Gater -12% → MetaGate 추가 패널티 → blended_conf 0.519 < 0.56 → skip → X
- 수정 후: mlofi_norm 불리 → Gater -12%만 → MetaGate는 regime/hurst/atr/정확도 기반 독립 평가 → blended_conf 0.575 ≥ 0.56 → reduce (진입 허용)

### 3. [103-P2] Toxicity 중복 해소 — ExecutionGovernor에서 toxicity 항 제거

**Files**: `strategy/runtime/execution_governor.py`, `main.py`

- `execution_governor.py`: `toxicity_passability × 0.15` 항 제거, 가중치 재분배 (0.35/0.30/0.20 → 0.40/0.35/0.25)
  - `toxicity_score` 파라미터: 하위 호환용으로 optional 유지(default=0.0), 내부 미사용
  - `components` dict에서 toxicity 항 제거
- `main.py`: `_gov_toxicity` 변수 및 `toxicity_score=_gov_toxicity` 인자 제거

**size 정상화**:
- 수정 전: ToxicityGate reduce(0.5×) + ExecutionGovernor reduce(0.6×) = 0.3× 복합
- 수정 후: ToxicityGate가 단독 처리 → 0.5× 단일 적용

---

## 2026-06-02 (102차 — 진입0 3중 분석 + 안전장치 P0~P8 구현)

**Work**: 금일 장중 진입 0건 원인을 SIGNAL/SYSTEM/WARN 로그 3중 분석 후 구조적 개선 8종 구현.

### 1. 진입0 원인 분석 (3라운드)

**1라운드 (SIGNAL 로그)**:
- 09:00 스케일러 age=641분 → microprice z=+1423, 극단 z 34개 → conf 고착 45~46%
- CoherenceGate 하루 내내 차단 (score 0.33~0.67, 임계값 0.60)
- grade C 5회 모두 Checklist 신뢰도 미달로 강제 X

**2라운드 (SYSTEM 로그 추가)**:
- 09:01~09:14: ERR-FATAL 14회 (105 vs 106 피처 불일치) → 파이프라인 완전 불능 14분
- 09:31: CB⑤ 16,616ms → CB PAUSED
- 09:50: ShadowSession BLOCKED (acc30m=30.0%)
- 11:51: CB③ 당일 정지 (acc30m=26.9%)
- CRASH +12%p가 actual_min_conf에 더해진 채 Checklist 전달 → grade=C 강제 X 메커니즘 코드 확인

**3라운드 (커밋 타이밍 분석)**:
- grade 분포: A=0, B=0, C=5, X=364 → 자동진입 조건 하루 전혀 미충족
- 101차 커밋(TrendBoost/FlatCap/CoherenceGate 면제): 15:24/15:25 → 오늘 장중 미적용
- 커밋 적용은 재기동 이후부터 → ef31bfd 09:48 이후 반영 등 타이밍 분석

### 2. P0 — feature/scaler 정합성 자동 검증 (multi_horizon_model.py, main.py)

- `validate_and_resync()` 신규: 로드 후 feature_names vs scaler 차원 불일치 호라이즌 비활성화
- `_load_all()` 말미 자동 호출 (초기 로드·GBM 재학습 완료·EOD 모두)
- `_pipeline_fatal_streak`: 연속 ERR-FATAL 2회 → validate_and_resync() + 즉시 재학습

### 3. P1 — Checklist min_conf CRASH 패널티 분리 (main.py)

- `_zone_base_mc` 저장 (L2·TrendGate 적용 전)
- Checklist 직전 `_checklist_min_conf = min(actual_min_conf, _zone_base_mc + 0.04)`
- TrendGate active 추가 cap: `min(_checklist_min_conf, _tp["min_conf_override"] + 0.02)`
- `[P1] Checklist min_conf 분리` 로그

### 4. P2 — 동적 mc 상한 캡 + 속도 제한 (settings.py, time_strategy_router.py)

- `MC_ABS_CEIL` 0.75→0.62, `MC_STEP_LIMIT` 0.08→0.03
- `MC_ZONE_MAX=0.65` 신규 (zone_mc 절대 상한, restore 경로 포함)
- `update_dynamic_mc()` zone loop + `_restore_mc_from_history()`에 적용

### 5. P3 — grade=C→X 신뢰도 차단 카운터 (checklist.py, main.py, daily_exporter.py)

- `checklist.py`: `conf_check_failed: True` 플래그 반환
- `main.py`: `_checklist_conf_fail_count` + `_ccf_today` 캡처(리셋 전 저장 버그 수정)
- `daily_exporter.py`: `build_report(extra_stats)` → 리포트 말미 `CL신뢰도차단: N회`

### 6. P4 — CB③ 4단계화 (settings.py, circuit_breaker.py, main.py)

- `CB_ACC_WATCH_MIN=0.35`, `CB_ACC_RESTRICTED_MIN=0.30`
- `_acc30m_stage`: NORMAL/WATCH/RESTRICTED 실시간 추적
- RESTRICTED 시 C등급 진입 차단 (`is_grade_restricted()`)
- `status_dict()`, `reset_daily()` 반영

### 7. P5 — C등급 실험적 자동 진입 (settings.py, main.py)

- `ENTRY_GRADE_C_AUTO_EXP=False` 기본값 OFF
- 조건: TrendGate active + STABLE_TREND/LUNCH_RECOVERY + CB NORMAL + not RESTRICTED
- size = `_qty_auto × C_AUTO_EXP_SIZE_MULT(0.3)` (C 기준의 절반)
- A/B auto 블록 다음 elif로 삽입, 기존 manual else 유지

### 8. P6 — ShadowSession BLOCKED 알림 (shadow_session.py)

- `_blocked_since`, `_blocked_last_notify` 변수 추가
- 30분 지속 시 Slack 알림 + 30분마다 반복
- 권장 대응 분기: acc30m 구간별 메시지 (재학습 트리거 / 관망 / CoreHealth 확인)
- BLOCKED→LIVE 복구 시 타이머 리셋

### 9. P7 — 재기동 원인 로깅 (main.py)

- `_restart_cause`: STARTUP/MANUAL/AUTO_DISCONNECT
- 자동 재연결 분기에서만 `AUTO_DISCONNECT` 마킹 → WARNING
- 수동 재기동은 MANUAL INFO (오늘 7회 재기동은 의도적)

### 10. P8 — EOD 스케일러 재적합 (main.py)

- `daily_close()` GBM retrain + `_load_all()` 직후 `refit_scalers_only(500봉, "E_EOD")` 동기 실행
- 08:55 ScalerWarmup 스킵 조건 `_warmup_retrain_pending` → `_gbm_retrain_running` 변경
- 내일 시초 scaler age 보장 (641분 재발 방지)

### 수정 파일 (102차)

| 파일 | P번호 |
|---|---|
| `model/multi_horizon_model.py` | P0 |
| `safety/circuit_breaker.py` | P4 |
| `safety/shadow_session.py` | P6 |
| `strategy/entry/checklist.py` | P3 |
| `strategy/entry/time_strategy_router.py` | P2 |
| `strategy/ops/daily_exporter.py` | P3 |
| `config/settings.py` | P2, P4, P5 |
| `main.py` | P0, P1, P3, P4, P5, P7, P8 |

---

## 2026-06-02 (99·100차 — 저변동성 인식 피처 + GBM 붕괴 방어 3종)

**Work**: 장 후 세션 로그 분석(12:56~14:01) → FL/UP 편향 급등 원인 규명 → 구조적 개선 5종 구현.

### 1. 로그 분석 — 15m 상수 출력 붕괴 확인 (99차 배경)

- 13:00~13:35: 15m confidence = 39.3% UP 20분 고착 (동일 값 반복)
- 13:36~14:01: 15m confidence = 44.1% FL 25분 고착
- 30m: UP편향 77% (UP=23/30) — 방향은 맞으나 이전 실패로 acc=33%
- SGD비중: 13:16 10% 바닥 도달 → 이후 고착
- 원인: GBM 스케일러 노후로 모든 입력이 동일 리프 → 상수 확률 출력

### 2. 저변동성 인식 피처 2종 추가 (99차)

| 피처 | 의미 | 값 범위 |
|---|---|---|
| `threshold_feasibility` | ATR / (1m_threshold × price) | <1=FLAT 우세, >1=UP/DN 빈번 |
| `micro_regime_code` | 직전 분 레짐 수치화 | 0=횡보·1=혼합·2=추세·3=탈진·4=급변 |

- `features/feature_builder.py`: `build()` 파라미터 `micro_regime` 추가, `HORIZON_THRESHOLDS` import
- `main.py`: `build()` 호출에 `micro_regime=self.current_micro_regime` (1분 lag) 전달
- `main.py` `daily_close()`: `current_micro_regime = "혼합"` 리셋 추가
- 다음 GBM 배치 재학습 시 자동 포함 (DB raw_features에 즉시 저장됨)

### 3. GBM 상수 출력 감지 + 앙상블 제외 (100차-1)

- `model/ensemble_decision.py`: `EnsembleDecision`에 `_CONST_OUT_N=5`, `_CONST_OUT_RANGE=0.005` 추가
- 5분 연속 동일 direction + confidence max-min < 0.5%p → 해당 호라이즌 weight=0 + 재정규화
- 전환 시 SIGNAL WARNING 로그 (1회), 해소 시 자동 복귀
- `result["const_output_horizons"]` 노출 → main.py 스케일러 재적합 훅과 연동
- `reset_daily()` 확장: hist·stuck 상태 초기화

### 4. SGD 바닥 회복 경로 (100차-2)

- `learning/online_learner.py`: 바닥(10%) 30회 조정(≈90분) + 50분정확도≥40% → 0.5%p 회복
- 최대 5%p까지(15%) 허용 — 급격한 복귀로 인한 conf 불안정 방지
- `reset_daily()` 버그 수정: `_gbm_w`·`_bucket_learn_count` 루프 위치 오류 (for h → for bk)

### 5. 상수 출력 → 스케일러 재적합 훅 (100차-3)

- `main.py`: `decision["const_output_horizons"]` 비어있지 않으면 daemon 스레드로 `refit_scalers_only(D_FORCE)` 실행
- `_const_out_refit_until`: 30분 쿨다운 (중복 실행 방지)
- `_scaler_refresh_running` 플래그 공유 (Phase B와 동일 락)

### 수정 파일

| 파일 | 변경 |
|---|---|
| `features/feature_builder.py` | `threshold_feasibility`, `micro_regime_code` 추가, `build()` 파라미터 |
| `model/ensemble_decision.py` | ConstOut 감지 + 제외 + reset_daily |
| `learning/online_learner.py` | SGD 바닥 회복 + reset_daily 버그 수정 |
| `main.py` | micro_regime 전달, ConstOut 훅, _const_out_refit_until |

---

## 2026-06-02 (98차 계속 — 진입0 구조 개선 전면)

**Work**: 6/2 장 중 진입0 원인 다중 분석 및 수정. 커밋 20여 건.

### 1. GBM 재학습 완료 (105피처)
- shap_feature_registry 91→108개 (신규 17개 수동 추가)
- force=True, weeks_back=26, 84분 소요
- acc 향상: 1m 0.362→0.419, 5m 0.473→0.504, 30m 0.478→0.512

### 2. mc 복원 버그 수정 + REGIME_MIN_CONF 동기화
- `_restore_mc_from_history()`: `r.get()` → `r["key"]` 직접 접근 (sqlite3.Row에 .get() 없음)
- 5개 zone 모두 복원 확인 (이전에는 GAP_OPEN만 복원)
- REGIME_MIN_CONFIDENCE['NEUTRAL'] 코드 기본값 0.52→0.42
- MC_ABS_FLOOR 0.50→0.42 (SGD 블렌딩 희석 고려)

### 3. ShadowSession z 조건 완화 + BLOCKED 복구
- 급변장 toxicity_atr_stress z=+19로 BLOCKED 고착 문제
- _GATE_ZSCORE_WARN: 2→50 (사실상 비활성)
- BLOCKED 상태에서 acc30m + core_health 충족 시 LIVE 복구 허용
- 배지 툴팁에 [Note 2026-06-02] 완화 사유 추가

### 4. quality_investor_fetch_count z=+8 수정
- 소급 99.9% = 0, 스케일러 평균≈0 → 실시간 60이면 z=+8
- investor_data.py: min(count, 60)→min(count, 5)
- SCALER_CLIP_FEATURES: (0, 5) 추가
- D_FORCE 반복 트리거 해소

### 5. Layer 2 발동/복귀 조건 전면 양방향 수정
- 발동 조건: day_ret≤-1.8% → |day_ret|≥1.8% (abs() 적용, 전면)
- 복귀 조건: bounce+OFI 제거 → ATR < 1.2 + z극단 < 3 (방향 중립)
- 이유: 선물 양방향 — 하락 지속 시 bounce=0%, OFI 음수로 CRASH 고착
- 툴팁 추가: 발동/복귀 조건 전체 + ± 표시

### 6. CoherenceGate FLAT 제외 + 임계값 완화
- 문제: 4/6=0.667 < 0.67 수학 오류 + FLAT 편향 시 DN 3/6=0.50 차단
- FLAT 예측 호라이즌 제외 후 방향성만 계산
- COHERENCE_GATE_MIN: 0.67→0.60

### 7. CB③ 30m FLAT 편향 수정
- CB③: FLAT 예측(direction=0) 제외, 방향성 예측만 acc 집계
- CB_ACCURACY_MIN_30M: 0.35→0.28 (FLAT 제외 후 랜덤 기준=50%)
- PATH_LABEL_RATIO: 0.45→0.55 (FLAT 레이블 과다 완화)
- _CW_30M: balanced→{FL:0.70, UP:1.15, DN:1.15}

### 8. UI 업데이트
- 앙상블 등급 카드 툴팁: CoherenceGate 예시 + 동적 min_conf + F1 가중치
- 앙상블 신호 방향 툴팁: STEP4.5 CoherenceGate + GBM/SGD/RF + 동적 min_conf
- 신뢰도 툴팁: actual_min_conf 동적 계산 설명
- mc 이력 ts: mmdd-hhmm 형식 (0602-0935)
- 30m 카드 라벨 FLAT 기준 툴팁

---

## 2026-06-01 (98차 — 동적 min_conf + GBM 105피처 재학습)

**Work**: 진입0 근본 원인 분석 → GBM 재학습 → 동적 mc 구현. 신규 파일 4개, 수정 파일 4개.

### 진입0 분석 및 GBM 재학습

#### 1. 원인 파악
- 97차 후 GBM 재학습이 자동으로 됐으나 89개 피처 기반 (신규 17개 미포함)
- `shap_feature_registry.json`의 active_features가 91개로 신규 피처를 필터링
- conf 평균 0.406 → min_conf 0.57 기준 전 390봉 grade=X → 진입0

#### 2. 해결: shap_feature_registry 수동 갱신
```python
# active_features: 91개 → 108개 (신규 17개 추가)
# ema_cross, bb_position, ret_1m/5m/15m, time_sin/cos,
# is_open/close_volatile, poc_distance, in_value_area, va_bandwidth, poc_above,
# cvd_delta_norm, volume_acceleration, vwap_momentum, prev_day_same_hour_ret
```

#### 3. GBM 재학습 (force=True, weeks_back=26)
- 실행: 22:04~23:28 (84분)
- 105개 피처, 44,520봉 학습
- 1m: 0.362→0.419 / 5m: 0.473→0.504 / 30m: 0.478→0.512 향상

#### 4. 재학습 후 conf 분포 변화
- 재학습 전: avg=0.406, max=0.584, min_conf 통과=0건
- 재학습 후: avg=0.698, max=0.920, min_conf=0.57 기준 42건 통과

#### 5. 금일 실 데이터 진입 시뮬
- mc=0.65: 22건, 승률 77%, +1,056만원
- mc=0.70: 17건, 승률 82%, +888만원
- 오늘 실제 상승장(1351→1420, +5.1%) — GBM이 13:56~14:00 DN 구간 정확히 포착

### 동적 mc 설계 및 구현

#### 설계: Rolling Percentile Gate vs 고정 mc 비교
- 고정 mc=0.65: 22건 77% +1,056만원
- Rolling p80 w=60: 12건 75% +506만원
- **결론: 고정 mc 우위** — conf 전반 높은 날은 percentile gate가 오히려 진입 제한

#### 구현 (주기 1 + 주기 2)
- **주기 1**: GBM 재학습 완료 즉시 → `_on_gbm_retrain_done` 콜백에서 `_recalibrate_mc('RETRAIN')`
- **주기 2**: 매일 08:55 워밍업 완료 후 → `_scaler_warmup_worker`에서 `_recalibrate_mc('DAILY_WARMUP')`
- `update_dynamic_mc()`: conf p65 기준 base_mc 계산 + step clamp(±8%p) + 시간대 배율
- `mc_history.db`: 변경 이력 영구 저장
- `DynamicMcPanel`: 시간대별 mc 카드 + 금일 conf 추이 히트맵 + 통과율 게이지 + 이력 테이블

#### 즉시 실행 결과
- 최근 3,789봉 conf avg=0.441 → p65 ≈ 0.45 → floor=0.50 적용 → base_mc=0.50
- STABLE_TREND: 0.540→0.500 / OPEN_VOLATILE: 0.600→0.510

---

## 2026-06-01 (97차 — F1 고도화 전면 구현: P1~P6c + 개선 1~7)

**Work**: F1_IMPROVEMENT_MASTER_PLAN.md 작성 후 로드맵 P1~P6c 전체 구현. 신규 파일 3개, 수정 파일 7개, 소급 190일(71,155봉) 피처 갱신 2회.

### 구현 내용

#### P2 / 개선 3 — 방향성 피처 17개 추가
- **1차 (P2, 14개)**: `time_sin/cos`, `is_open/close_volatile`, `ret_1m/5m/15m`, `ema_cross`, `bb_position`, `cvd_delta_norm`, `poc_distance`, `in_value_area`, `va_bandwidth`, `poc_above`
- **2차 (개선 3, 3개)**: `volume_acceleration`(3봉 거래량 변화율), `vwap_momentum`(5봉 VWAP 기준 속도), `prev_day_same_hour_ret`(전일 동시간대 수익률)
- **신규 파일**: `features/technical/volume_profile.py` (POC/Value Area, n=60봉 롤링)
- `scripts/backfill_features.py` `--update-features` 모드 추가 → 소급 190일 2회 완전 갱신

#### P3b — 코히어런스 게이트
- `COHERENCE_GATE_MIN=0.67` — active_horizons 중 4개 이상 동방향 미달 시 grade=X
- `result["coherence_blocked"]` 필드 추가 → 디버깅 가능

#### P3 — HorizonF1AdaptiveWeight
- EMA(decay=0.95, floor=0.30) 기반 F1 추적 → HorizonDecorrelator 가중치에 f1² 곱셈 적용
- main.py STEP 1 전 호라이즌 `record_horizon_verification()` 자동 누적

#### P4 — 시간대 × 호라이즌 min_conf 2D 표
- `MIN_CONF_TABLE` (OPEN_VOLATILE 30m=0.70 등 상위 강화)
- main.py STEP 6 앙상블 직전 conf 미달 호라이즌 필터링 (최소 2개 보장)

#### P5 — 호라이즌별 최적 σ_k
- `scripts/optimize_sigma_k.py` 신규 — 71,144봉 기반 11개 k 탐색
- 결과: 1m/3m/5m=0.41, 10m/15m=0.38, 30m=0.33
- `SIGMA_K_PER_HORIZON` 딕셔너리 → batch_retrainer에서 호라이즌별 k 사용

#### P6b — 경로 조건부 레이블
- `_path_conditioned_label()` — 중간 역행 > threshold × 0.45 → FLAT 처리
- UP/DOWN 레이블 순도 향상 (오염 15~25% 제거 목표)

#### P6c — RF 이종 앙상블
- `model/rf_horizon_model.py` 신규 (n=150, balanced, oob_score=True, n_jobs=1)
- batch_retrainer GBM 완료 후 RF 자동 학습·저장 (rf_horizons.pkl)
- main.py STEP 5: GBM+SGD 결과에 RF 0.30 blend
- GBM 재학습 완료 콜백(`_on_gbm_retrain_done`)에서 RF pkl 자동 reload

#### 개선 1 마무리
- `MIN_TRAIN_BARS`: 5,000 (13거래일) → **15,000 (40거래일)**

#### 개선 4 — 학습 레이블 고정화
- `USE_FIXED_LABEL_THRESHOLD=True` → 학습은 HORIZON_THRESHOLDS 고정값
- 실전 rolling sigma / 검증 sigma_at_t 재현 유지 (별개 메커니즘)

#### 개선 6 — GBM 파라미터 강화
- `n_estimators`: 200 → **300** / `learning_rate`: 0.05 → **0.04**

### 마스터 플랜 문서
- `docs/F1_IMPROVEMENT_MASTER_PLAN.md` 전면 재작성 — 구현 완료 14개 항목 + 미구현 3개 + F1 목표 시나리오

---

## 2026-06-01 (95차 — Phase A·C: 스케일러 워밍업 + Robust 전처리)

**Work**: 2026-06-01 진입 0건 원인 분석 후 SCALER_ROBUST_PLAN.md 작성 및 Phase A·C 구현. 4개 파일 변경 + 1개 신규.

### 원인 분석 (2026-06-01 진입 0건)

- **근본 원인**: 스케일러 65시간 노후화(금요일 마감 후 미갱신) → ATR z=+5.04, avg_volume z=+4.22
- 연쇄: 09:00 파이프라인 7.2초(CB⑤ 5분 정지) → 09:06~09:55 grade=X → 09:55 CB③ CRITICAL 당일 정지
- spread_ticks z=+6.45(10:12)이 장중 최대 극단값, clip 없어 무방비

### 구현 내용

#### Phase A — 08:55 스케일러 워밍업
- `load_features_for_warmup(lookback_bars)`: raw_data.db 최근 500봉 X 로드 (라벨 불필요, managed feature set 적용)
- `refit_scalers_only(X, feature_names)`: 6 호라이즌 scaler.fit() + pkl 저장 + `_scaler_fitted_at` 갱신. GBM 모델 불변(트리 스케일 불변)
- `main.py _scaler_warmup_worker`: `_warmup_retrain_pending=False`일 때만 daemon thread 실행. GBM 재학습 예약 시 스킵(재학습이 스케일러 포함)

#### Phase C — Robust 전처리 `apply_robust_preprocess()`
- 모듈 수준 함수로 분리 → 4경로(fit/predict_proba/refit_scalers_only/retrain_now) 단일 출처 공유
- atr, avg_volume: `log1p(max(x, 0))` — 양수 long-tail 완화
- spread_ticks: `clip(0, 20.0)` — 오늘 z=+6.45 cap
- mlofi_slope: `clip(-500, 500)` — 분포 -722~+1127 제한
- SGD 경로(`online_learner`) 미적용

### 주요 검토 결과

- cancel_add_ratio: tick 단위 `_stable_cancel_add_ratio(log1p+clip)` 이미 적용 → 1순위 제외, DB 클린업만 해당
- ofi_norm/mlofi_norm: clip(-3,3) 있음, 오늘 극단 z는 스케일러 노후화 원인 → Phase A 우선 후 재평가
- spread_ticks: clip 없는 상태에서 오늘 최대값 → 즉시 1순위 처리

---

## 2026-06-01 (94차 — 스케일러 강건화 완성 + 운영 클린업)

**Work**: SCALER_ROBUST_PLAN.md Phase B·D + 섹션 8·9 전체 구현. SYSTEM.log 200MB/일 버그 수정. 11개 파일 변경 + 3개 신규.

### 구현 내용

#### 1. Phase B — 정기/강제 스케일러 refresh (SCALER_ROBUST_PLAN.md)
- `check_refresh_trigger(bar_dt, extreme_feats)` — D_FORCE(극단z 연속 3분/2회반복) > B_OPEN(장초 15분) > C_PERIODIC(60분) 우선순위 트리거
- `refit_scalers_only(trigger_ts=, trigger_type=, trigger_reason=)` — 완료 후 scaler_monitor.db UPDATE
- main.py Phase B 데몬 스레드: `_scaler_refresh_running` 중복 방지
- settings.py Phase B/C/D 상수 6개 추가

#### 2. Phase D — cancel_add_ratio DB 클린업
- raw_data.db raw_features에서 `|cancel_add_ratio| > 10` 인 11행 삭제 (2026-05-08 13:31~41, 최대 7.49억 이상치)
- 정리 후 7252행 → MIN_TRAIN_BARS 3000→5000 복원
- `scripts/cleanup_cancel_add_ratio.py` 신규 (dry-run/--apply 모드)

#### 3. 운영 클린업
- **SYSTEM.log 200MB/일 버그 수정**: `[CybosEvent] recv begin/end` + `[CybosRT-EVENT] dispatch` INFO→DEBUG (api_connector.py:245/255 + realtime_data.py:141)
  - 내일부터 SYSTEM.log 5MB/일 예상 (40배 감소)
- `scripts/monthly_cleanup.py` 신규: 30일 로그·90일 shap·60일 예측·7일 백업 자동 삭제
- 오늘 즉시: raw_data 백업 2개(41.6MB) + trades 백업 2개(0.1MB) + 4월 로그 삭제

#### 4. 섹션 8 — scaler_monitor.db 수집 레이어
- `model/scaler_monitor_db.py` 신규: `init_db`, `insert_events_batch`, `update_event_refresh`, `aggregate_daily`, `insert_daily`
- `predict_proba(monitor_ts=ts)`: 호라이즌별 age_minutes·max_z·extreme_count 수집 → batch INSERT
- `[ScalerMonitor]` 구조화 로그: 노후 90분+ 또는 극단z 발생 시 WARN
- `daily_close()`: `aggregate_daily` + `insert_daily` (grade_x_minutes + cb3_triggered)

#### 5. 섹션 9 — ScalerMonitorPanel UI
- `dashboard/panels/scaler_monitor_panel.py` 신규 (60초 갱신)
- 3개 섹션: 실시간(호라이즌별 노후·극단z) + Top5 extreme + 일별 이력 20거래일
- 색상: 노후<30분=초록/30~90분=노랑/>90분=빨강, extreme=주황, D_FORCE=파랑
- main_dashboard.py에 "🔬 스케일러" 탭 삽입

### 진단 발견 사항
- SYSTEM.log 근본 원인: 호가 이벤트(초당 1~2회) INFO 로그 → 하루 200MB. 단 3줄 수정으로 해결
- raw_data.db: 구버전(2026-05-08) cancel_add_ratio가 raw 정수값 그대로 저장됨. 현재 코드 `_stable_cancel_add_ratio`는 `clip(log1p(d)-log1p(r), -3, 3)` 정상
- shap.db 성장률: 650MB/월 예상 → monthly_cleanup 90일 롤링 필수

---

## 2026-05-30 (91·92차 — rolling σ 방법3 Phase 1+2 구현 + ATR 완전 제거)

**Work**: 방법3(rolling sigma × k=0.41) 단독 채택 구현. Phase 1(핵심 로직) + Phase 2(ATR 제거) 완료. 커밋 2개(91차 c9e4f82, 92차 9751c96). 4개 파일 변경.

### 분석 내용

#### 1. σ_1min 일별/시간대별 변화 실측
- 일별 sigma: 0.044~0.218%, 최고/최저 4.9배 차이
- 시간대별: 09:00 sigma=0.241% / 13:30 sigma=0.098% → **2.45배 차이**
- 5/19 이후 저변동성 진입: p50 0.129% → 0.065% (절반 급감)

#### 2. 방법3 선택 근거 (3가지 방법 비교)
- 방법1 (현재 정적): FLAT std=14.4%p, 진입 0 재발 위험
- 방법2 (σ_1min×√t): 방법1과 실질 동일 (최적 sigma_1min=0.041% = 방법1 threshold)
- 방법3 (rolling×k): **FLAT std=3.2%p**, 저변동성 날도 26~39% 안정

#### 3. k=0.41 산출 흐름
- 탐색법: rolling 20봉 sigma에서 FLAT 34% 달성하는 k 탐색
- k=0.41 → FLAT 33.6%, 주별 최적 k 범위 0.40~0.45 (안정)
- 주기적 재보정 불필요 — Phase A UPDATE 경보 발생 시만 재산출

#### 4. 진입 시점 분석
- 09:00~09:19: sigma_20봉 미수집 → 진입 금지
- 09:20~09:29: A등급만, min_conf 0.60, size×0.5
- 09:30~: 표준 진입 (SGD warmup 30봉 완료, 10m Qualification 달성)

#### 5. SGD 운영 흐름 (방법3 도입 후)
- actual 레이블: prediction_buffer가 현재 HORIZON_THRESHOLDS(rolling σ×k)로 생성
- 방안B(P1): 예측 시점 sigma 저장 → verify 시 사용 (미구현, P1-a~d 잔여)
- SGD는 변동성 대비 상대 강도를 학습 (일관성 있음)

#### 6. 주기적 재보정 불필요 확인
- settings.py HORIZON_THRESHOLDS는 시작 직후 5분 폴백으로만 사용
- 5분 이후: rolling σ×k가 자동 대체 → 재보정 의미 없음
- k=0.41은 Phase A UPDATE 경보 발생 시에만 재산출

### 구현 내용

#### [91차] Phase 1 — rolling σ 핵심 구현 (c9e4f82)
- **config/settings.py**: `SIGMA_K=0.41`, `SIGMA_W=20`, `SIGMA_W_MIN=5`, `USE_ROLLING_SIGMA_THRESHOLD=True`, `PRE_RETRAIN_SIZE_MULT=0.6`
- **batch_retrainer._load_from_db()**: 봉별 rolling σ×k 레이블 생성 (방법B 핵심) — FLAT std 14%p→3.2%p
- **main.py**:
  - `_sigma_buf`, `_sigma_20`, `_sigma_ready`, `_last_sigma_20`, `_pre_retrain_done` 초기화
  - 매분 파이프라인: sigma_buf 갱신 → HORIZON_THRESHOLDS 매분 rolling σ×k 갱신
  - 진입 게이트: 09:20 미만 금지 / 09:20~09:29 A등급·size×0.5 / 09:30 표준
  - `_on_gbm_retrain_done`: 첫 재학습 완료 시 `_pre_retrain_done=True`
  - `daily_close`: EOD sigma 저장 + 버퍼 초기화 + `_pre_retrain_done=False` 리셋

#### [92차] Phase 2 — ATR 완전 제거 (9751c96)
- **main.py**: `_log_threshold_monitor()` 함수 제거, `_threshold_monitor_tick` 제거, 30분 tick 블록 제거
- **config/settings.py**: `HORIZON_THRESHOLD_MULT`, `HORIZON_THRESHOLD_OPEN_MULT` 제거, `HORIZON_THRESHOLDS_BASE` 주석 갱신

#### 추가 구현 (미커밋)
- **dashboard/panels/threshold_monitor_panel.py**: Phase A k값/FLAT 비율 모니터 UI (신규)
- **dashboard/main_dashboard.py**: "📐 임계값 모니터" 탭 추가
- **docs/ROLLING_SIGMA_IMPL_PLAN.md**: Phase 0~3 구현 계획 문서 (91차에 커밋)

---

## 2026-05-30 (90차 — 임계값 데이터 기반 재보정 + 운영/연구 병렬 구조 + Phase A WFA 모니터)

**Work**: 2026-04-28~05-29 DB 기반 임계값 분석 → 6개 호라이즌 threshold 재보정 + 운영(대칭)/연구(비대칭) 병렬 구조 설계·구현 + SGD 완전 리셋 자동화 + Phase A 롤링 재보정 모니터 구현. 커밋 1개. 8개 파일 변경/신규.

### 분석 내용

#### 1. 임계값 현실화 필요성 분석
- 기간: 2026-04-28 ~ 2026-05-29, 장중 연속봉만 (갭·이상치 제거)
- 1분봉 6,795개 → 3분봉 2,314개 → 30분봉 232개
- 33/34/33 목표 분포 달성 threshold:
  - 1m: -0.041%/+0.041% | 3m: -0.073%/+0.074% | 5m: -0.089%/+0.095%
  - 10m: -0.124%/+0.172% | 15m: -0.133%/+0.177% | 30m: -0.129%/+0.262%
- 현행 vs 데이터 기반 괴리: 15m +42% 과다, 30m +63% 과다 (FLAT 비율 심각 왜곡)

#### 2. 모델A(±0.05%) vs 모델B(데이터 기반) 비교 분석
- 정확도: 1m·30m는 B 우세, 3m·5m는 A 우세
- Brier Score: 1m·15m·30m는 B 우세
- 불일치 구간 PnL: 10m -0.095pts/건, 15m -0.066pts/건, 30m -0.375pts/건 손해 (B가 스킵한 게 정답)
- ATR 동적 threshold: 현행 BASE 너무 높아 거의 항상 BASE 사용 (동적 미발동). 새 BASE로 15m 발동률 4%→12%, 30m 3%→15%

#### 3. WFA 모니터 방안 설계
- Phase A (현재): 매주 금요일 롤링 재보정 — FLAT drift ±6%p, threshold δ ±15% 경보
- Phase B (+6주): DriftDetector 재활용 Brier Score CUSUM 모니터
- Phase C (+26주): PARAM_SPACE 통합 WFA

### 구현 내용

#### config/settings.py
- `HORIZON_THRESHOLDS` 6개 값 교체 (1m 0.0005→0.00041, 5m 0.0011→0.00092, 10m 0.0016→0.00148, 15m 0.0022→0.00155, 30m 0.0032→0.00196, 3m 현행 유지)
- `HORIZON_THRESHOLDS_BASE`: `dict(HORIZON_THRESHOLDS)` 자동 동기화
- `HORIZON_THRESHOLDS_RESEARCH` 신규: 비대칭 딕셔너리 6개, ATR 갱신 비대상
- `SGD_FULL_RESET_PENDING = True`: threshold 교체 후 SGD 1회 완전 리셋 플래그

#### model/target_builder.py
- `build_targets_asymmetric()` 신규: `{"down": float, "up": float}` 비대칭 임계값으로 레이블 생성 (연구용)

#### model/multi_horizon_model.py + learning/batch_retrainer.py (동기화)
- class_weight 재조정 (새 임계값 기준 FLAT~33% 균형으로 강한 FL 억압 불필요):
  - 1m: FL 0.60 → 0.85 (이전 이상점 7-A 수정값)
  - 5m: FL 0.58 → 0.85
  - 30m: FL 0.65 → 1.00 (balanced)
  - 3m: FL 0.75 유지 (threshold 미변경)
  - 10m/15m: compute_sample_weight("balanced") 유지

#### learning/online_learner.py
- `reset_full()` 신규: SGDClassifier + StandardScaler 완전 재생성, 모든 버퍼·카운터 초기화. 임계값 교체 후 이력 오염 방지용.

#### main.py
- `from learning.threshold_recalibrator import ThresholdRecalibrator` import 추가
- `__init__`: `self.threshold_recalibrator = ThresholdRecalibrator()` 초기화
- `_on_gbm_retrain_done()`: `SGD_FULL_RESET_PENDING == True` 시 `reset_full()` 1회 호출 후 플래그 False
- `daily_close()`: 매주 금요일 `threshold_recalibrator.run()` 호출 + 경보 시 WARNING 로그

#### learning/threshold_recalibrator.py (신규)
- `ThresholdRecalibrator` 클래스: Phase A 핵심 로직
- 연속봉 수익률 분포 재산출, 33/67 분위수 기반 대칭 임계값 산출
- FLAT drift(목표 34%), threshold δ, ATR ratio 3지표 계산
- 경보: FLAT ±6%p → WATCHLIST, threshold δ ±15% → UPDATE
- 결과 저장: `data/db/threshold_monitor.db`

#### docs/THRESHOLD_WFA_MONITOR.md (신규)
- Phase A~C 전체 설계 문서화 (단계별 구조, 지표, 구현 위치, DB 스키마)

### 첫 실행 결과 (2026-05-30)
- 3m: UPDATE (FLAT 27.7%, delta +23.5%) — 현행 보류 판단 유효, 데이터 누적 필요
- 30m: UPDATE (FLAT 27.5%, delta +19.6%) — 4.4주 불안정성 범위, 3~4주 추이 관찰 후 재검토
- 1m/5m/10m/15m: WATCHLIST (ATR ratio 이상)

---

## 2026-05-29 (89차 — Qualification 세션 필터 + 호라이즌별 정확도 + 툴팁)

**Work**: 88차 구현 직후 실세션 스크린샷에서 발견된 2가지 이슈 수정 + 툴팁 추가. 커밋 1개. 3개 파일 변경.

### 구현 내용

#### 1. 세션 필터 추가 (`main.py`)
- 증상: 세션 시작 직후 10m/15m/30m이 v4/t4 ACTIVE — 이전 세션 carry-over 예측이 카운팅됨
- 원인: `pred_buffer.verify_and_update()`가 어제 14:40~15:10 구간의 예측을 오늘 09:00 직후 즉시 verified 처리. CB③에는 `_session_start_ts` 필터가 있으나 qualification 카운팅에는 없었음
- 수정: `if _h in self._horizon_runtime_state and _pred_ts_q >= self._session_start_ts:` — 이번 세션 예측만 카운팅

#### 2. 호라이즌별 정확도 버퍼 (`learning/online_learner.py`)
- 증상: 모든 카드 acc=0% 고착
- 원인: `online_learner.horizon_accuracy(_h)` 메서드가 없어 `hasattr` 분기에서 항상 0.0 반환
- 수정:
  - `_horizon_acc_buf: Dict[str, deque]` 추가 (6개 호라이즌 × maxlen=ACCURACY_WINDOW=150)
  - `learn()`: 버킷 버퍼에 이어 `_horizon_acc_buf[horizon]`에도 correct 기록
  - `horizon_accuracy(h)`: 5건 미만 시 0.0 반환 (초기 불안정값 표시 억제)
  - `reset_daily()`: 호라이즌 버퍼도 초기화

#### 3. 자격 현황 라벨 툴팁 (`dashboard/main_dashboard.py`)
- "호라이즌 자격 현황 (사이클 추적)" 라벨에 `setToolTip()` 부착
- 툴팁 내용: 카드 상태(WAIT/ACTIVE/PENALIZED/BLOCKED) 설명, vN/tN 의미, acc% 정의(최근 150건 적중률, 5건 미만=0%), `recent_accuracy()` 차이(버킷 평균 vs 호라이즌 개별), 30m 주의사항(acc 5건 충족 ~1주), Phase 상태(현재 추적+UI만)

---

## 2026-05-29 (88차 — 호라이즌 자격 추적 Phase 1+2 구현)

**Work**: 멀티호라이즌 앙상블 자격 추적 시스템 Phase 1(상태 추적) + Phase 2(대시보드 dry-run) 구현. 장중 `name 'settings' is not defined` CRITICAL 버그 수정. 커밋 1개. 3개 파일 변경.

### 구현 내용

#### 1. Phase 1 — `_horizon_runtime_state` 상태 추적 (`main.py`)
- `__init__`: `_horizon_runtime_state` 딕셔너리 추가 (6개 호라이즌 × verified_cycles/trained_cycles/qualified/active/status/weight/recent_accuracy)
- STEP 1 verified 루프 끝: `verified_cycles += 1`, `recent_accuracy` 동기화, 자격 조건(`verified≥3 AND trained≥3`) 충족 시 `qualified=True` + SIGNAL 로그
- STEP 2 SGD learn 루프 이후: `online_learner._horizon_counts[h]` → `trained_cycles` 동기화, 자격 조건 재확인
- STEP 6 직후: `dashboard.update_qualification(self._horizon_runtime_state)` 호출
- `daily_close()`: `_horizon_runtime_state` 전체 리셋 (전 호라이즌 not_qualified 상태로)
- Phase 1은 상태 추적만 — 앙상블 비중·진입 로직 변경 없음

#### 2. Phase 2 — 호라이즌 자격 현황 카드 (`dashboard/main_dashboard.py`)
- `EntryPanel.__init__`: `_qualify_cards: dict = {}` 추가
- `EntryPanel._build()`: 모드/시간대 섹션 이후 자격 현황 카드 섹션 삽입 (2×3 그리드, 6개 카드)
- 각 카드: 호라이즌명 / 상태(WAIT·ACTIVE·PENALIZED·BLOCKED) / 사이클 진행(v0/t0·acc=0%)
- `EntryPanel.update_qualification(state)`: 상태별 색상 코딩 — ACTIVE=녹, WAIT=회, PENALIZED=주황, BLOCKED=빨
- `MireukDashboard.update_qualification(state)`: `entry_panel.update_qualification(state)` 위임

#### 3. 설정 상수 (`config/settings.py`)
- `HORIZON_QUALIFY_MIN_CYCLES = 3` — 자격 획득 최소 사이클 수
- `QUALIFY_QUALITY_MIN_SAMPLES = 10` — 품질 게이트 평가 최소 샘플 수

#### 4. 버그 수정 — `settings` 네임스페이스 오류 (`main.py`)
- 증상: 장중 재시작 후 매분 `[ERR-FATAL] minute_pipeline: name 'settings' is not defined` CRITICAL
- 원인: `getattr(settings, "HORIZON_QUALIFY_MIN_CYCLES", 3)` — `settings`는 `runtime_settings`로 임포트됨
- 수정: `settings.` → `runtime_settings.` 2곳 (`replace_all`)

---

## 2026-05-22 (87차 — Layer 2 UI 개선 + update_layer2() 파이프라인 연결)

**Work**: Layer 2 Intraday Gate 패널 발동지표 UI 재정비 3종, 조건 체크 로그 단순화, `_layer2_log` 초기값 설정, `update_layer2()` main.py 연결. 커밋 1개. 2개 파일 변경.

### 구현 내용

#### 1. 발동 지표 7개 → 6개 재정비 (`dashboard/main_dashboard.py`)
- `시가-0.8&15m` 항목 제거 (Layer 2 조건 로그에서 이미 반영됨)
- 당일 수익률 임계값 표시: `≤−1.0%` → `≤−0.8%|≤−1.0%` (2단계 임계값 명시)
- Contrarian 임계값: `강제승격` → `ACTIVE`
- 당일 수익률 3색 로직: 빨강(≤−1.0%) / 오렌지(≤−0.8%) / 기본색

#### 2. Layer 2 조건 체크 로그 단순화 (`dashboard/main_dashboard.py`)
- 기존: 4섹션(진입허용·신뢰도강화·사이즈축소·복귀체크) + 수치 나열
- 신규: 3줄 고정 포맷 (진입 허용 / 신뢰도 강화 / 사이즈 축소)
  - NORMAL: 롱/숏 모두 허용 / 추가 가산 없음 / ×1.0
  - DAY_RISK_OFF: 신규 롱 금지 숏만 허용 / +5%p / ×0.5
  - CRASH: 원칙적으로 신규 진입 전부 금지 / +12%p / ×0.3
- DAY_RISK_OFF / CRASH 상태 시: 복귀 조건 체크 3항목 추가 표시 (반등 +0.5% / OFI15m > 0 / ATR < 1.2, ✔/✘)

#### 3. `_layer2_log` 초기값 설정 (`dashboard/main_dashboard.py`)
- 기동 직후 로그 박스가 비어있던 문제 해소
- `_build()` 내 `_layer2_log` 생성 직후 NORMAL 기본 텍스트 삽입

#### 4. `update_layer2()` main.py 파이프라인 연결 (`main.py`)
- 82차부터 NEXT_TODO로 미뤄진 항목 완료
- STEP 4 인트라데이 레짐 계산 직후 `self.dashboard.update_layer2(self.intraday_regime.status_dict())` 1줄 추가
- 매분 발동지표 + 조건 로그가 실시간 갱신됨

---

## 2026-05-22 (86차 — 5/22 진입 0 P0 구현 + EOD 스케일러 초기화)

**Work**: Deep·Codex 5/22 진입 0 원인 분석 리뷰를 바탕으로 P0 5종 구현 + EOD 스케일러 초기화 3종 수정. 총 8개 파일 변경, 커밋 1개.

### 구현 내용

#### 1. System Health Score (SHS) + Early Kill Switch (EKS) 신규 (`safety/system_health.py`)
- SHS = 100 - restart×8 - z_warn×2.5 - (1-core_pass)×25 - s2_latency×5
- SHS < 60 → 진입 차단 + 슬랙 경고 (5점 추가 하락마다 재알림)
- EKS: 09:05 1회 판정 — GAP_OPEN conf_max < 45% AND CORE 통과율 0% → 당일 관망 선언
- `reset_daily()` 추가 — 15:40 마감 시 EKS·GAP_OPEN 상태 초기화

#### 2. SHS 슬랙 알림 (`utils/notify.py`)
- `notify_shs_alert()`: SHS < 60 또는 5점 추가 하락 시 구성 요소 포함 경고
- `notify_kill_switch()`: EKS 발동 시 CRITICAL 알림

#### 3. SHS UI 배지 (`dashboard/main_dashboard.py`)
- 상단 헤더 `lbl_shs` 배지: ♥ SHS N(녹) / ⚠ SHS N(주황, 차단) / ⛔ 관망일(빨)
- `DashboardAdapter.update_shs_badge()` 추가

#### 4. Warm Scaler Canary (`model/multi_horizon_model.py`)
- `canary_stale_age_hours()`: scaler pkl mtime 기준 최대 노후 시간
- `canary_z_warn_count()`: X_recent 피처로 극단 z피처 수 반환
- `_load_all()`: `_scaler_fitted_at[h]` = pkl mtime 동기화 추가 — 재시작 후 in-memory 노후 시계 정확성 보장

#### 5. Warm Scaler Canary + SHS 연동 (`main.py`)
- `pre_market_setup()` 08:55: Canary 검사 + 슬랙 경고
- `_canary_load_z_warn()`: raw_data.db 최근 60행으로 z_warn 산출
- SHS 업데이트 (z_warn, core_pass, s2_latency, restart_count) + badge 갱신
- EKS 판정·GAP_OPEN 기록 로직 삽입
- `_final_entry_ok` 조건에 `kill_switch_active` 차단 추가

#### 6. log_manager **_kwargs 방어 가드 (`logging_system/log_manager.py`)
- `signal()`, `system()`, `trade()` 에 `**_kwargs` 추가
- 5/22 ERR-FATAL (signal() args=5) 재발 원천 차단

#### 7. CORE 피처 진단 로그 (`strategy/entry/checklist.py`)
- CORE 탈락 시 raw값 포함 상세 로그: `VWAP pos=±X.XXX need >0 (LONG) bear_exh=0.00 | CVD dir=±1 need >0 | OFI pres=±1 need >0`

#### 8. EOD 스케일러 초기화 (`main.py` daily_close)
- `self.model._load_all()` 을 `if retrain_ok:` 밖으로 이동 — 재학습 실패 시에도 최신 pkl 로드
- `self.system_health.reset_daily()` 추가 — EKS·GAP_OPEN 상태 다음날 이월 방지

### P0 조사 결과 (미구현 잔여)

| 항목 | Deep | Codex | 상태 |
|---|---|---|---|
| signal() TypeError | P0-1 | P0-1 | ✅ 이번 세션 |
| CORE 진단 로그 | P0-4 | P0-3 | ✅ 이번 세션 |
| 재시작 방지 락 | P0-3 | P0-2 | ❌ **미구현** |
| Scaler Auto Re-fit | P0-2 | P1-1 | △ Canary만 (감지, re-fit 없음) |
| S2 병목 배치화 | P1-2 | P0-4 | ❌ 병목 위치 재확인 필요 |

> 재시작 방지 락: `_restart_armistice_until`(진입만 차단)과 별개로 BrokerSync→connect_broker() 재호출 경로 차단 필요. 재시작 12회 → conf 50% 붕괴의 직접 원인.

---

## 2026-05-22 (85차 — 모의투자 세션 이상점 7·8 deep dive + 구조적 수정 4종)

**Work**: 14:53~15:09 모의투자 세션 로그 이상점 7·8을 deep dive 분석하여 구조적 원인을 규명하고 5개 파일에 걸쳐 수정 4종을 구현. 커밋 1개 (`67f974e`).

### 분석·수정 이상점 요약

| 이상점 | 증상 | 근본 원인 | 수정 |
|--------|------|-----------|------|
| 7 | 1m/5m 호라이즌 FL 편향 87%/100% | `balanced` class_weight만 적용 — FL 명시적 완화 없음. HORIZON_THRESHOLDS 경계 케이스 + 오후 저변동성 구간. CLOSE_VOLATILE 구간 단기 FL편향이 앙상블 up/dn score 희석 | A: `_CW_1M={FL:0.60}`, `_CW_5M={FL:0.58}` 추가. D: CLOSE_VOLATILE 단기 0.6× 가중치 축소 |
| 8 | 10m conf 50~55% 과도 압축 | `_preload_horizon_calibration()` 18,000건 전체 평균 Platt → 현재 구간 과소평가. balanced class_weight GBM predict_proba 절대값 낮춤. `_apply_horizon_calibration()` 하한 없음 → raw_conf 80%까지 낮춤 | B: WINDOW 500→200, 재보정 주기 50→20. C: 10m/15m raw_conf×0.85 하한 |

### 구현 내용

**`model/multi_horizon_model.py`** (이상점 7-A)
- `_CW_1M = {FLAT: 0.60, UP: 1.20, DN: 1.20}` 추가 (85차 신규 — 1m FL 87% 편향)
- `_CW_5M = {FLAT: 0.58, UP: 1.21, DN: 1.21}` 추가 (85차 신규 — 5m FL 100% 편향)
- `_make_sample_weight()`: 1m/5m 분기 추가

**`learning/batch_retrainer.py`** (이상점 7-A — 학습기 일관성)
- `_CW_1M`, `_CW_5M` 동일하게 추가. `_make_sample_weight()` 동기화

**`learning/calibration.py`** (이상점 8-B)
- `WINDOW = 200` (500 → 200 축소, 현재 시장 반영 속도 향상)
- 재보정 주기: `% 50` → `% 20` (200건 윈도우에서 50건 주기 너무 느림)

**`main.py`** (이상점 8-C + 이상점 7-D 연결)
- `_apply_horizon_calibration()`: 10m/15m Platt 하한 `raw_conf×0.85` 추가 (과도 압축 방지)
- `ensemble.compute()` 호출에 `time_zone=get_time_zone()` 추가 (CLOSE_VOLATILE 전달)

**`model/ensemble_decision.py`** (이상점 7-D)
- `compute()` 파라미터에 `time_zone: str = ""` 추가
- CLOSE_VOLATILE 구간 단기(1m/3m/5m) 가중치 0.6× 축소 후 재정규화 (10m/15m 기여도 상대 확대)

### 두 이상점 연결

단기 FL편향(이상점 7) → 앙상블 up/dn score 희석 → conf 저하 + 10m Platt 과압축(이상점 8) → 중기 DN 신호 약화 → 시너지로 진입 신호 차단. CLOSE_VOLATILE 구간에서 이 두 효과가 복합적으로 작용해 13개 분봉 연속 X등급 발생.

---

## 2026-05-22 (84차 — 모의투자 세션 이상점 3~6 deep dive + 구조적 수정 4종)

**Work**: 12:11~12:48 모의투자 세션 로그 이상점 3~6을 deep dive 분석하여 구조적 원인을 규명하고 5개 파일에 걸쳐 수정 4종을 구현. 커밋 1개.

### 분석·수정 이상점 요약

| 이상점 | 증상 | 근본 원인 | 수정 |
|--------|------|-----------|------|
| 3 | 30m 예측 12:42~12:48 7연속 실패 | `_CW_30M = {FL:0.5}` 과도한 다운웨이팅 → GBM 30m이 FL 상황에서 DN 오분류 + TrendGate DN active → StuckBreaker 억제 해소 | FL=0.65, UP/DN=1.18로 완화 |
| 4 | 50분 정확도 급락 추이 | `ACCURACY_WINDOW=50`인데 3 호라이즌/분 → 실질 17분 윈도우. 매 샘플 즉시 가중치 조정 → 연속 실패 시 1분 내 SGD 비중 급감 | ACCURACY_WINDOW→150 (실질 50분), `_ADJUST_EVERY=3` 분봉 단위 1회 조정 |
| 5 | Bias 통계 분봉 1건 단위 (통계 의미 없음) | `_h_stats`가 매분 초기화. UP/DN 추적 없이 tot=1이라 100%/0%만 출력 | 30건 롤링 버퍼, 15건 이상 시 75% 초과 편향 감지, UP/DN/FL 모두 추적 |
| 6 | conf 전체 구간 60% 미달 | ① SGD 초기 균일분포 희석, ② 앙상블 conf↔3m 보정기 분포 미스매치, ③ 6호라이즌 불합의, ④ 30m FL 편향(이상점 3과 동일 원인) | A:SGD 초기 GBM 전용, B:앙상블 전용 보정기, C:불합의 패널티, D:CORR_ADJ 30m 하향 |

### 구현 내용

**`model/multi_horizon_model.py`** (이상점 3)
- `_CW_30M = {FL:0.5, UP:1.25, DN:1.25}` → `{FL:0.65, UP:1.18, DN:1.18}` (FL 다운웨이팅 완화)

**`learning/batch_retrainer.py`** (이상점 3 — 일관성)
- `_CW_30M` 동일하게 수정 (학습기 일관성)

**`learning/online_learner.py`** (이상점 4 + 이상점 6-A)
- `ACCURACY_WINDOW = 50` → `150` (3 호라이즌/분 × 50분)
- `_ADJUST_EVERY = 3` 상수 추가 (분봉 단위 1회 조정)
- `_bucket_learn_count` 버킷별 호출 카운터 추가
- `blend_with_gbm()`: h_count < 30이면 `w_gbm=0.95, w_sgd=0.05` 초기 GBM 전용 모드 추가
- `reset_daily()`에 `_bucket_learn_count` 리셋 추가

**`model/ensemble_decision.py`** (이상점 6-B + 6-C)
- `from learning.calibration import PredictionCalibrator` import 추가
- `self.ensemble_calibrator = PredictionCalibrator(method="platt")` 추가 (앙상블 전용 보정기)
- `compute()`: 합의도 패널티 블록 추가 (6호라이즌 중 ≤2 합의 시 conf×0.92, 패널티만)
- `compute()`: Platt 보정 로직 — ensemble_calibrator 우선, 미학습 시 3m fallback
- `record_ensemble_outcome(raw_conf, correct)` 메서드 추가

**`config/settings.py`** (이상점 6-D)
- `ENSEMBLE_WEIGHTS_CORR_ADJ`: 30m 0.20→0.15, 나머지 균등 +0.01 조정

**`main.py`** (이상점 5 + 이상점 6-B 연결)
- `_bias_buf`: 30건 롤링 버퍼 (per-horizon). 매분 초기화 해소
- `_bias_log_tick`: 10분 요약 출력 카운터
- STEP 1 Bias 통계: 롤링 버퍼 기반 재작성 — 15건 이상 시 75% 초과 편향 감지, UP/DN/FL 추적
- `_ensemble_conf_cache`: 앙상블 보정기 학습용 conf 캐시 (1m 검증용)
- STEP 6 후: `self._ensemble_conf_cache[ts] = confidence` 저장 (캐시 크기 35건 제한)
- STEP 1 1m 검증 시: `ensemble.record_ensemble_outcome(conf, correct)` 호출
- `reset_daily()`: `_bias_buf` 초기화 + `_ensemble_conf_cache` 초기화

### 보너스 위험 판단 (이상점 6-C)
합의도 보너스 (+5%) 초기 제안을 4개 동시 구현 이득 검토 과정에서 제외. 전 호라이즌 합의 시에도 모델 편향이 있으면 오히려 7연속 실패 (이상점 3 사례와 동일 구조). 패널티만 구현하여 하방 보호에 집중.

---

## 2026-05-22 (83차 — 탈진장 ATR ratio 문턱 재설계)

**Work**: `MicroRegimeClassifier`에서 탈진장(REGIME_EXHAUSTION)이 급변장(REGIME_VOLATILE)과 동일한 ATR 문턱(1.5)을 공유해 사실상 dead code로 존재하던 구조적 버그를 재설계. 급변장과 겹치지 않는 독립 구간(1.2 ~ 1.5)으로 분리하고, 양방향 대칭(`bull_exhaustion`) 추가 및 불필요한 `ofi_reversal_speed` 조건 제거. 커밋 1개.

### 발견된 구조적 버그 2종

| # | 버그 | 파일 | 상태 |
|---|---|---|---|
| B1 | `ATR_EXHAUSTION_MULT = 1.5` = `ATR_VOLATILE_MULT = 1.5` — 급변장 판정이 먼저 실행돼 탈진장 도달 불가 (dead code) | `micro_regime.py` | **수정** |
| B2 | exhaustion_conds 내 `abs(ofi_reversal_speed) > 0` — `bear_exhaustion`이 이미 CVD+OFI 복합 파생 신호이므로 중복이자 추가 차단 조건 | `micro_regime.py` | **제거** |

### 구현 내용

**`collection/macro/micro_regime.py`**

1. **상수 재설계**: `ATR_EXHAUSTION_MULT = 1.5` 삭제 → `ATR_EXHAUSTION_MIN = 1.2` 신설 (탈진장 ATR 하한; 상한은 기존 `ATR_VOLATILE_MULT = 1.5` 공유)
2. **독립 구간**: `exhaustion_conds` 판정을 `1.2 ≤ atr_ratio < 1.5`로 변경 → 급변장(`≥ 1.5`)과 완전 분리
3. **양방향 대칭**: `bear_exhaustion > 0` 단독 → `(bear_exhaustion > 0 or bull_exhaustion > 0)` — SHORT MR 탈진도 포착
4. **`bull_exhaustion` 파라미터 추가**: `push_1m_candle` / `_classify` 시그니처 확장
5. **`ofi_reversal_speed` 파라미터 제거**: `push_1m_candle` / `_classify` 에서 완전 삭제

**`main.py`**

- `push_1m_candle()` 호출부: `ofi_reversal_speed` 제거 + `bull_exhaustion = features.get("bull_exhaustion")` 추가

### 레짐별 ATR 구간 (변경 후)

| 레짐 | ATR ratio 구간 |
|---|---|
| 급변장 | ≥ 1.5 (또는 z_warn≥3, atr≥1.25+ADX≥30) |
| **탈진장** | **1.2 ≤ ratio < 1.5** + (bear/bull_exhaustion > 0) + VWAP 1.5σ 이탈 |
| 추세장 | ADX≥25 + ratio < 1.5 |
| 횡보장 | ADX<20 + ratio < 1.3 |
| 혼합 | 나머지 |

### 실세션 확인 사항 (2026-05-23)

1. `[MicroRegime] 혼합 → 탈진 (ADX=XX.X, ATR=X.XXXX, ratio=1.2X~1.4X)` 로그 첫 발생 확인
2. 발화 시 SIGNAL 로그에서 `bear_exhaustion > 0` or `bull_exhaustion > 0` + `vwap_position` 절대값 ≥ 1.5 동시 확인
3. 탈진장 진입 후 체크리스트: `min_conf_effective = 0.56`, `entry_mode = MEAN_REVERSION` 적용 확인

---

## 2026-05-22 (82차 — Layer 2 인트라데이 게이트 UI 패널 + L2 토글 영속성 및 즉시 적용)

**Work**: 진입 관리 탭의 Pre-flight 체크리스트 패널을 좌(5):우(6) 양분. 오른쪽에 Layer 2 IntradayTacticalRegime 전용 패널 신설. L2 ON/OFF 버튼 설정 영속성(ui_prefs.json) 구현 및 장중 토글 시 main.py 3개 게이팅 포인트에 즉시 반영. 커밋 1개.

### 구현 내용

**`dashboard/main_dashboard.py`**

1. **레이아웃 양분** — 기존 Pre-flight 섹션을 `QHBoxLayout(ratio 5:6)`으로 분리. 왼쪽=9개 체크리스트, 오른쪽=Layer 2 패널.

2. **Layer 2 패널 (오른쪽 3단)**
   - **상단 상태 카드**: L2 ON/OFF 버튼(체크블 QPushButton) + 레짐 상태(NORMAL/DAY_RISK_OFF/CRASH) 색상 표시 + 전환 레이블(`prev→current`)
   - **중단 7개 지표**: 당일 수익률≤−1%, 시가−0.8%&15m, 15m 수익률, 30m 수익률, ATR ratio, z극단 수, Contrarian ACTIVE — 발동 항목 빨간색 강조
   - **하단 조건 체크 로그** (`QTextEdit` readonly): 진입허용·신뢰도강화·사이즈축소·복귀체크 4섹션 실시간 표시

3. **영속성** — `_save_layer2_gate_pref()` / `_load_layer2_gate_pref()` 신규. `data/ui_prefs.json`의 `"layer2_gate_enabled"` 키. 로드 시 `blockSignals` 처리.

4. **신규 API**
   - `is_layer2_gate_enabled() → bool` — DashboardProxy 경유로 main.py에 노출
   - `update_layer2(status_dict, min_conf_base)` — IntradayTacticalRegime `status_dict()` 결과를 패널에 반영
   - `sig_layer2_gate_toggled` pyqtSignal — DashboardProxy에 위임 속성으로 노출

**`main.py`**

- `_l2_gate_on` 플래그를 파이프라인 틱당 1회 계산 (`getattr` 방어 폴백 포함)
- 3개 게이팅 포인트 모두 `_l2_gate_on` 분기 추가:
  - Point 1: `min_conf_adjust()` (신뢰도 강화) 우회
  - Point 2: `is_long_allowed()` / `is_short_allowed()` (방향 차단) 우회 → 전 방향 허용
  - Point 3: `size_mult()` (사이즈 축소) 우회
- `sig_layer2_gate_toggled.connect(_on_layer2_gate_ui_toggled)` 연결 + 핸들러 신규

### 실세션 확인 사항 (2026-05-23)

1. 재시작 후 L2 ON/OFF 버튼 상태가 이전 설정 복원되는지 (ui_prefs.json)
2. 장중 L2 OFF 토글 시 `[IntradayRegime] Layer 2 Gate UI=OFF (우회 모드)` WARN 로그
3. L2 OFF 상태에서 CRASH 레짐에서도 LONG/SHORT 차단 없이 진입 허용 확인
4. `update_layer2()` 호출 연결 확인 — main.py STEP 9 (또는 STEP 6) 에서 호출 추가 여부

---

## 2026-05-22 (81차 — Platt 보정 기동 사전 fit + EnsembleDecision 2차 압축 연결)

**Work**: GBM 모델이 "99.9% 확신" 과신 출력 → 실제 정확도 40% 수준 문제를 Platt Scaling으로 억제. 4가지 버그를 수정하고 기동 시 DB에서 calibrator를 사전 fit하도록 구조 개선. 커밋 1개.

### 발견된 버그 4종 (모두 수정 완료)

| # | 버그 | 파일 | 상태 |
|---|---|---|---|
| B1 | `self.calibrator` 미선언 → `hasattr` 항상 False → 보정 코드 **절대 실행 안 됨** | `model/ensemble_decision.py` | **수정** |
| B2 | `.transform()` 미존재 → `AttributeError` (올바른 메서드는 `.calibrate()`) | `model/ensemble_decision.py` | **수정** |
| B3 | 보정 후 `confidence`만 갱신, `grade`·`auto_entry`는 구식 값 유지 → A등급인데 conf=0.40 모순 | `model/ensemble_decision.py` | **수정** |
| B4 (근본) | `horizon_calibrator`가 매 기동마다 0샘플 fresh 생성 — DB 24,626건 있어도 로드 코드 없음 → 첫 100건 동안 보정 비활성 | `main.py` | **수정** |

### 수정 내용

**`model/ensemble_decision.py`**
- `__init__`: `self.calibrator = None` 추가 (main.py에서 주입 대기)
- stuck-breaker 재결정 직후(grade 계산 전): Platt 보정 블록 삽입 — `calibrate("3m", confidence)`, clip(0~0.85), up/down score 동기화
- `result` dict: `"confidence_raw"` 필드 추가 (보정 전 원본 보존)

**`main.py`**
- `__init__` (line ~188): `_preload_horizon_calibration()` 호출 + `self.ensemble.calibrator = self.horizon_calibrator` 주입
- `_preload_horizon_calibration()` 신규 메서드: `predictions` DB 최근 18,000건 로드 → `horizon_calibrator.record()` 일괄 적재 → `fit_all()` → 첫 tick부터 보정 활성

### 보정 흐름 (수정 후)

```
기동: DB 18,000건 로드 → fit_all() → 즉시 활성
  ↓
_apply_horizon_calibration()  ← 1차: 각 호라이즌 raw prob → calibrated (cap 0.85)
  ↓
EnsembleDecision.compute()    ← 가중합 → AdaptiveGater → StuckBreaker
  ↓
Platt 보정 블록               ← 2차: 앙상블 confidence → calibrate("3m") (cap 0.85)
  ↓
grade/auto_entry 계산         ← 보정된 confidence 기준
```

### 수정 파일

| 파일 | 변경 내용 |
|---|---|
| `model/ensemble_decision.py` | `self.calibrator = None`, Platt 보정 블록 (grade 전), `confidence_raw` 필드 |
| `main.py` | `_preload_horizon_calibration()` 신규, `ensemble.calibrator` 주입 |

### 실세션 확인 사항 (2026-05-23)

1. 기동 시 `[Calib] 기동 사전 학습 완료: N건` 로그 (N≥1000이면 정상, 0이면 DB 쿼리 오류)
2. 기동 직후 첫 분봉부터 `[Calib] clipped` 로그 **감소** (보정이 이미 낮춰줘서 0.85 초과 드묾)
3. `confidence` 값이 이전 대비 낮아짐 (0.85→0.60대, 과신 억제 확인)
4. `confidence_raw` 필드가 `result` dict에 포함됨 (대시보드 JSON 확인)
5. `grade`가 보정 후 confidence 기준으로 재계산됨 (A→B 또는 B→X 강등 확인)

---

## 2026-05-21 (76~80차 — TrendPersistenceGate 대칭 구현 + Layer 2 완전 통합 + 대시보드 깜빡임)

**Work**: 원웨이 추세장(한 방향으로 지속 상승/하락하는 날) 진입 기회 부재 문제를 TrendPersistenceGate로 해결. UP/DN 대칭 구현, Layer 2 3종 기능 완전 통합, 등급카드 깜빡임 UI 추가. 커밋 4개 (77차: 02a1731, 78차: a84d787, 79차: 19d5f13, 80차: 365b22d).

### 76차 — CVD 단조성 비율 피처

`feature_builder.py`에 `cvd_monotone_ratio` 추가 — 최근 20개 CVD 값 중 상승 이동 비율(0~1). GBM이 원웨이 추세를 명시적으로 학습할 수 있는 피처. `_cvd_history = deque(maxlen=21)` 추가.

### 77차 — TrendPersistenceGate 최초 통합

UP-only 버전 TrendPersistenceGate를 main.py에 통합. streak≥10분 시 UP 방향 actual_min_conf를 0.44로 완화. import·초기화·STEP 6 블록·reset_daily 4곳 삽입. 커밋 02a1731.

### 78차 — Layer 2 완전 통합 (3종)

Layer 2 IntradayTacticalRegime의 3가지 미구현 기능 완전 통합:
- `min_conf_adjust()`: DAY_RISK_OFF +5%p, CRASH +12%p. TrendGate 이후 순서로 적용 (TrendGate가 낮추고, Layer 2가 올림).
- `size_mult()`: DAY_RISK_OFF ×0.5, CRASH ×0.3. Toxicity gate 이후 적용.
- `allow_crash_grade_a_short()`: CRASH 상태에서 A등급 숏에 한해 예외 허용.
커밋 a84d787.

### 79차 — TrendPersistenceGate DOWN 대칭 구현

77차 UP-only 문제 발견: 하락 원웨이장은 대응 불가. trend_persistence.py 전면 재작성:
- UP streak: `above_vwap=1 AND cvd_direction=1`
- DN streak: `above_vwap=0 AND cvd_direction=-1`
- hard_break 비대칭: UP=-300, DN=+200 (숏스퀴즈가 더 빠르고 파괴적이므로 DN을 더 민감하게)
- return dict: `up_active/up_streak/dn_active/dn_streak/min_conf_override` 확장
- main.py STEP 6도 듀얼 streak 대응으로 수정
커밋 19d5f13.

### 80차 — 대시보드 등급카드 깜빡임 UI

TrendGate 활성 상태를 시각적으로 표시. `EntryPanel`의 앙상블 등급/체크리스트 등급 카드 테두리를:
- UP 원웨이 모드: 녹색(#3FB950) ↔ 기본 600ms 토글
- DN 원웨이 모드: 오렌지(#D29922) ↔ 기본 600ms 토글
`_trend_blink_timer`, `_on_trend_blink_tick()`, `set_trend_gate_mode()` 추가. main.py STEP 6에서 `set_trend_gate_mode()` 호출.
커밋 365b22d.

### 설계 결정 핵심

1. **hard_break 비대칭 (-300 vs +200)**: 하락 중 CVD 급반등(숏스퀴즈)은 상승 중 CVD 급반락보다 훨씬 빠르고 파괴적 → DN streak를 더 민감하게 리셋.
2. **min_conf 적용 순서**: TrendGate가 먼저 낮추고(원웨이 완화), Layer 2가 나중에 올림(레짐 위험 반영). 순서 역전 시 TrendGate 효과가 무력화될 수 있음.
3. **대시보드 mode 기준**: 방향(direction)이 아니라 streak 활성(up_active/dn_active) 기준. 방향이 반대여도 streak가 살아있으면 표시.

---

## 2026-05-21 (72차 — 방향 비대칭 편향 6종 수정)

**Work**: 신호 설계의 방향 비대칭 편향(directional asymmetry bias) 전수 점검 및 2단계 수정. 설계 의도와 달리 LONG 또는 SHORT 한 방향을 체계적으로 편애하는 코드 패턴을 6종 발견·수정.

### 1단계 수정 (4항목)

| 항목 | 수정 내용 | 수정 파일 |
|---|---|---|
| **① OFI 역전 신호 양방향화** | `ofi_reversal_signal`(LONG 전용) → `bull_reversal_signal` + `bear_reversal_signal` 분리. 구 신호 deprecated alias 유지 | `features/technical/ofi_reversal.py`, `features/feature_builder.py` |
| **② CVD 탈진 양방향화** | `cvd_exhaustion`(하락 탈진만 계산, SHORT MR에도 오용) → `bear_exhaustion`(하락 압력 소진, LONG MR용) + `bull_exhaustion`(상승 압력 소진, SHORT MR용) 분리 | `features/technical/cvd_exhaustion.py`, `features/feature_builder.py`, `strategy/entry/checklist.py`, `main.py`, `collection/macro/micro_regime.py`, `challenger/variants/vwap_reversal.py`, `challenger/variants/exhaustion_regime.py` |
| **③ 이전 봉 방향 3-state화** | `prev_bar_bullish: bool`(도지=False → SHORT 조건 충족) → `prev_bar_direction: int` (+1/0/-1). 도지는 LONG·SHORT 모두 불통과 | `strategy/entry/checklist.py`, `main.py` |
| **④ PCR 극단값 양방향화** | `opt_pcr_extreme`(풋 극단만 정의) → `pcr_extreme_bearish` + `pcr_extreme_bullish`(PCR≤0.67) + `pcr_extreme_signed`(연속 강도 [-1,+1]) 추가 | `collection/options/pcr_store.py`, `features/options/option_features.py` |

### 2단계 수정 (2항목)

| 항목 | 수정 내용 | 수정 파일 |
|---|---|---|
| **⑤ S&P500 레짐 임계값 대칭화** | `sp500_chg_pct < -1.0` → `< -0.5`. 상승 기준(+0.5%)과 하락 기준(-1.0%)의 비대칭 → 대칭 ±0.5% | `collection/macro/regime_classifier.py` |
| **⑥ RL HOLD 페널티 제거** | `hold_penalty = 0.001`(position=0 홀드 시 미미한 페널티) → `hold_penalty = 0.0`. 직접 편향은 아니지만 CB·체크리스트 외부 제어와 중복, 간접 편향 증폭 가능성 제거 | `learning/rl/reward_design.py` |

### 핵심 버그 (가장 의미론적으로 잘못된 코드)

SHORT MR 진입 체크(vwap_position > +1.5)에서 `bear_exhaustion > 0` 조건을 사용하고 있었음. 하락 압력 소진 = LONG 신호인데 SHORT 역추세 진입을 허가. 수정: SHORT MR → `bull_exhaustion > 0` (상승 압력 소진 = SHORT 역추세 정당성). Python 단위 검증으로 의미론적 정확성 확인.

### 수정 파일 (총 12개)

`features/technical/cvd_exhaustion.py`, `features/technical/ofi_reversal.py`, `features/feature_builder.py`, `strategy/entry/checklist.py`, `main.py`, `collection/macro/micro_regime.py`, `challenger/variants/vwap_reversal.py`, `challenger/variants/exhaustion_regime.py`, `collection/options/pcr_store.py`, `features/options/option_features.py`, `collection/macro/regime_classifier.py`, `learning/rl/reward_design.py`

### 검증 확인 항목

- bear/bull_exhaustion 교차 발화 없음 (bear 시나리오에서 bull=0, 반대도 동일)
- bull/bear_reversal_signal 교차 발화 없음
- checklist SHORT MR이 bear_exhaustion으로 발화되지 않음 (의미론적 정확성)
- 도지(direction=0) LONG·SHORT 모두 체크 #7 실패
- pcr_extreme_signed: 풋 극단=+1.0, 콜 극단=-1.0, 중립=0.0
- SP500 -0.6%가 score=-1 기여 (수정 전: 중립)
- HOLD reward=0.0 (페널티 없음)

---

## 2026-05-21 (71차 — 자동진입관리 UI 카드 구조 개편)

**Work**: 진입관리탭 자동진입관리 패널의 카드 배치를 개편. 앙상블 등급·체크리스트 등급·최종진입 카드 분리 표시 + 레이아웃 빈 공간 해소.

### 주요 변경 내용

| 항목 | 변경 내용 |
|---|---|
| **신뢰도 카드 → 앙상블 등급 카드** | 신뢰도 % 표시 제거 (멀티호라이즌 앙상블 패널과 중복) → EnsembleDecision 반환 A/B/C/X 등급 표시 |
| **진입 등급 카드 → 체크리스트 등급** | 라벨명 변경 + 각종 게이트 차단 전 순수 체크리스트 grade (`_cr["grade"]`) 표시 |
| **최종진입 카드 신규** | 앙상블+체크리스트 종합 최종 판정. `direction!=0 AND _final_grade in (A,B)` 시 "진입" (녹색 600ms 깜박임 테두리), 나머지 "진입대기" |
| **레이아웃 재구성** | QGridLayout(3열) → VBoxLayout + info_row0(HBox) + info_row1(HBox). row0 2카드·row1 3카드 각각 균등 폭 |
| **수량 카드 균등 폭** | 산출수량·진입수량·최대허용수량 각각 `stretch=1` 추가 → 상위 행과 동일한 1/3 폭 |

### 수정 파일

| 파일 | 변경 내용 |
|---|---|
| `dashboard/main_dashboard.py` | EntryPanel 카드 재구성 (레이아웃·라벨·blink 타이머·툴팁 전면 개편) |
| `main.py` | `update_entry()` 호출에 `ensemble_grade=grade`, `checklist_grade=_cr["grade"]`, `final_entry=bool` 추가 |

### 데이터 흐름 (신규)

```
EnsembleDecision.compute() → grade (앙상블 등급) → 앙상블 등급 카드
EntryChecklist.evaluate()  → _cr["grade"] (체크리스트 등급) → 체크리스트 등급 카드
_final_grade in (A,B) + direction!=0 → final_entry bool → 최종진입 카드
```

---

## 2026-05-20 (69차 — 68차 개선 검증 + signal() TypeError ERR-FATAL 근본 원인 수정)

**Work**: 11:46:31 재시작 후 68차 개선 3항목 실세션 검증 완료. 09:14~09:25 로그 재분석에서 `signal() takes 2 positional arguments but 3 were given` ERR-FATAL 근본 원인 규명 → 3개 파일 수정.

### 68차 개선 검증 결과 (11:46:31 재시작 후)

| 항목 | 결과 |
|---|---|
| `conf < min_conf` 분봉 ERR-FATAL 소멸 | **확인** — 11:46:31 이후 ERR-FATAL minute_pipeline 경보 없음 |
| `[Checklist] 신뢰도 미달 → 강제 X등급` 로그 | **정상** — 매분 `XX.X% < YY.Y% → 강제 X등급` 정상 출력 |
| watchdog 경보 거짓 경보 여부 | **정상** — 재시작 후 watchdog 허위 경보 없음 |
| 시간대 전환 | **정상** — 11:50:26 `OTHER: 기타 구간` 전환, min_conf=65% 정상 적용 |
| CB⑤ 9138ms 발동 | **정상** — 11:54 실제 처리 지연 → 5분 CB 정지 (허위 경보 아님) |

### 신규 버그 발견 및 분석

09:14 ~ 09:25 ERR-FATAL 8회 이상: `signal() takes 2 positional arguments but 3 were given`

| 항목 | 내용 |
|---|---|
| 발생 구간 | OPEN_VOLATILE (09:05~10:30), 11:46:31 재시작 후 미재현 (구간 지남) |
| 주요 원인 1 | `validate_health_policy_hotreload.py` `_Collector.signal(self, msg)` — level 파라미터 없음. monkey-patch 중 pipeline이 `log_manager.signal(msg, "WARNING")` 호출 시 TypeError |
| 주요 원인 2 | `main.py` `_hc_block`·IntradayRegime 차단 로직 3곳: positional `"WARNING"` 인수 사용 |
| traceback 부재 | `error_policy.py` FATAL 처리 시 traceback 미캡처 → 정확한 실패 라인 파악 불가 |
| 미해결 모순 | SIGNAL: `conf=35.2% < 63% → 신뢰도 체크 실패`. DEBUG: `pass_count=6` (CORE 체크 실행됨). traceback 수집 후 다음 발생 시 재분석 예정 |

### 수정 내용 (69차)

| 파일 | 변경 내용 |
|---|---|
| `utils/error_policy.py` | `import traceback` 추가. RECOVERABLE·DEGRADED·FATAL 3케이스 모두 `traceback.format_exc()` 로깅 |
| `scripts/validate_health_policy_hotreload.py` | `_Collector.signal(self, msg)` → `_Collector.signal(self, msg, level="INFO")` |
| `main.py` | `_hc_block` + IntradayRegime 롱차단 + 숏차단 3곳: `"WARNING"` positional → `level="WARNING"` keyword |

### 69차 실세션 확인 사항 (2026-05-21)

1. ERR-FATAL `signal() takes 2 positional arguments but 3 were given` 재발 없음
2. `[보호] 고신뢰 연속오답 N회 — 신규 진입 차단` 정상 출력 (TypeError 없음)
3. `[IntradayRegime] CRASH — 신규 롱 금지` 정상 출력 (TypeError 없음)
4. 다음 ERR-FATAL 발생 시 WARN.log에 traceback 포함 (파일명·라인번호 확인)

---

## 2026-05-20 (68차 — minute_pipeline ERR-FATAL 실제 근본 원인 발견 및 최종 수정)

**Work**: 11:04:01 재시작 후 `ERR-FATAL minute_pipeline`가 매분 반복. 1차 수정(81e0784, `main.py`) 후 재시작에도 11:37~11:42 동일 경보 지속. 2차 분석에서 실제 원인이 `checklist.py`에 있음을 규명하고 최종 수정.

### 증상 요약

| 시각 | 관측 |
|---|---|
| 11:04:01 | Cybos 재시작 완료 |
| 11:06:01~11:12:01 | `conf=43.4% grade=X` 분봉마다 `ERR-FATAL minute_pipeline` 반복 |
| 11:06:33~11:12:30 | watchdog 90초 경보 반복 (파이프라인이 `notify_pipeline_ran()` 미도달) |
| 11:24:51 | 81e0784 커밋 — `main.py` `entry_mode` 기본값 추가 (잘못된 진단) |
| 11:37:01~11:42:00 | 재시작 후에도 동일 `ERR-FATAL minute_pipeline` 재발 |

### 1차 진단의 오류 (81e0784)

- **잘못된 진단**: `main.py` STEP 7의 `entry_mode` (값: "auto"/"hybrid"/"manual")를 진입 블록 밖에서 참조한다고 판단 → `main.py`에 기본값 추가
- **실제 버그 위치**: `strategy/entry/checklist.py:95` — **별개의 `entry_mode`** (값: "TREND_FOLLOW"/"MEAN_REVERSION")

### 실제 근본 원인

```python
# checklist.py — evaluate() 함수 내 (수정 전)

checks = {}

# 2. 신뢰도 미달 시 조기 반환 (line 84~96)
if not checks["2_confidence"]:
    return {
        ...
        "entry_mode": entry_mode,   # ← line 95: 여기서 참조
    }

entry_mode = "TREND_FOLLOW"         # ← line 100: 여기서 첫 할당 (너무 늦음)
```

Python은 함수 내 어디서든 변수가 할당되면 함수 전체 스코프에서 로컬 변수로 취급.
신뢰도 미달(confidence < min_conf) 경로가 line 100 이전에 line 95를 참조 → `UnboundLocalError`.
`conf=43.4%`는 min_conf(≥58%)에 항상 미달 → 매 분봉마다 예외 발생.

### 최종 수정 내용

| 파일 | 변경 내용 |
|---|---|
| `strategy/entry/checklist.py` | `entry_mode = "TREND_FOLLOW"` 초기화를 `checks = {}` 바로 다음(line 77)으로 이동 — 모든 조기 반환 경로보다 먼저 할당 보장 |

### 수정 후 기대 동작

1. 신뢰도 미달 분봉(grade=X)에서 예외 없이 정상 조기 반환 처리됨
2. `ERR-FATAL minute_pipeline` 경보 소멸
3. 파이프라인이 끝까지 완료 → watchdog 허위 경보 소멸

### 운영 확인 포인트 (2026-05-21)

1. `grade=X` 분봉에서 `ERR-FATAL minute_pipeline` 경보가 더 이상 없는지 확인
2. watchdog 경보가 실제 분봉 미수신 상황에서만 뜨는지 확인
3. `[Checklist] 신뢰도 미달` 로그 정상 출력 확인 (예외 없이 체크리스트 조기 반환 처리)

---

## 2026-05-20 (67차 — 장중 로그 분석 + 모델 이상점 5종 확인 + 3종 수정)

**Work**: 09:34~10:51 장중 로그를 AI 분석 관점으로 점검. 이상점 5가지를 코드 레벨에서 검증하고 즉시 수정 가능한 3종 수정 완료. SYSTEM 정확도=0.0%의 진짜 원인 규명.

### 발견된 이상점 및 처리

| # | 이상점 | 판정 | 처리 |
|---|---|---|---|
| 1 | online_learner scaler.partial_fit() 최초 1회만 호출 | **버그** | **수정 완료** |
| 2 | SYSTEM 정확도=0.0% — 오해 유발 레이블 | **구조 이슈** | **로그 개선 완료** |
| 3 | horizon별 편향(5m UP편향, 30m FL편향) 미추적 | **감지 부재** | **진단 로그 추가** |
| 4 | conf=0.85 상한 클립 — 로그에서 포화 여부 불명 | **로그 미흡** | **DEBUG 로그 추가** |
| 5 | 6분 주기 처리시간 스파이크(3~5초) | **구조 한계** | 추가 진단 필요 |

### SYSTEM 정확도=0.0% 실제 원인 (규명 완료)

61차에서 "파라미터 누락 수정"으로 기록됐지만 오늘도 여전히 0.0%였음. 두 가지 구조 원인이 있었음:

- **원인 A (세션 초반 30분 공백)**: `_pred_ts >= _session_start_ts` 필터로 재시작 전 예측 제외. 09:34:45 시작 시 30m 예측 ts(09:04~)가 필터를 통과 못 해 `record_accuracy()` 미호출 → `_accuracy_buf` 비어 0/1=0.0 (의도적 안전장치, 정상)
- **원인 B (30분 이후에도 0%인 이유)**: 10:04~10:51 구간 30m 예측 실제 정확도가 수치적으로 매우 낮음 (FL 과신 → 실제 UP/DN 연속). 0.0%는 실제 모델 성능이 낮은 진실된 값

### 수정 내용

| 항목 | 파일 | 변경 내용 |
|---|---|---|
| scaler 적응 학습 수정 | `learning/online_learner.py` | `if not _fitted:` 조건 제거 → 매 샘플마다 `partial_fit()` 호출 |
| SYSTEM 로그 레이블 명확화 | `dashboard/main_dashboard.py` | `정확도=X%` → `CB③30m=X%(N건)` / 샘플 없으면 `집계중` 표시 |
| cb3_samples 파라미터 추가 | `dashboard/main_dashboard.py` | `update_system_status()` `cb3_samples` 파라미터 신규 |
| cb3_samples 전달 | `main.py` | `_cb_status.get("cb3_samples", 0)` 전달 추가 |
| horizon별 편향 진단 로그 | `main.py` | STEP 1 직후 `[Bias]` 로그 추가 — 호라이즌별 적중률 + UP/FL 편향 자동 표시 |
| conf 클립 DEBUG 로그 | `main.py` | `_calibrated_raw > 0.85`이면 `[Calib] clipped` DEBUG 로그 |

### 67차 실세션 확인 사항 (2026-05-21)

1. **SYSTEM 로그 형식**: `CB=NORMAL | 처리시간=Xms | CB③30m=XX%(N건)` 또는 `집계중` 표시 확인
2. **[Bias] 로그**: 매분 horizon별 적중률과 UP편향/FL편향 태그 발생 확인
3. **scaler 적응**: SGD비중이 이전보다 안정적으로 유지되는지 (30%→10% 급감 여부 관찰)
4. **[Calib] clipped** DEBUG 로그: 30m conf=85.0% 반복 시 발생 여부 확인 (DEBUG 레벨)

---

## 2026-05-20 (66차 — SHAP 중요도·파라미터 상관계수 이상점 점검 및 4종 수정)

**Work**: 대시보드 "파라미터 중요도(SHAP)"와 "파라미터 상관계수" 업데이트 상태 점검. 이상점 4종 발견 후 우선순위 순으로 전부 수정 완료.

### 발견된 이상점 요약

| # | 이상점 | 심각도 |
|---|---|---|
| 1 | `_refresh_shap_state()` 임계값 30 vs `SHAP_MIN_DATA_POINTS`=100 불일치 → RESTORED값이 LIVE로 둔갑 | **높음** |
| 2 | `_update_shap_dashboard()` 메서드 중복 정의 (구버전 데드코드 + 인코딩 깨진 문자열) | 낮음 |
| 3 | `_shap_feature_window` 재시작 후 미복원 → 30분간 SHAP 계산 공백 | 중간 |
| 4 | `_build_param_corr_string()` `short_names` 키 인코딩 깨짐 → 레이블 매칭 실패 | 낮음 |

### 수정 내용 (4종)

| Fix | 파일 | 변경 내용 |
|---|---|---|
| Fix 1 | `learning/shap/shap_tracker.py` | `update()` → `bool` 반환 (실계산 True, skip False) |
| Fix 1 | `main.py` | `SHAP_MIN_DATA_POINTS` import 추가. `_refresh_shap_state()` 임계값 30 → `SHAP_MIN_DATA_POINTS`. `update()` 반환값으로 `_live_shap_ready` 제어 |
| Fix 2 | `main.py` | 구버전 `_update_shap_dashboard()` 중복 정의 (line 820~861) 제거 |
| Fix 3 | `main.py` | `_restore_analysis_buffers()`에 `_shap_feature_window` DB 복원 추가 |
| Fix 4 | `main.py` | `_build_param_corr_string()` `short_names` 키 정상 UTF-8 한글로 교체 |

### 66차 실세션 확인 사항 (2026-05-21)

1. **SHAP LIVE 전환 타이밍**: 재시작 후 DB에 100건 이상 raw_features가 있으면 기동 직후 `_live_shap_ready=True`로 전환되는지 확인
2. **SHAP LIVE 전환 로그**: `[SHAP] 중요도 갱신 완료 (n=XX)` 로그 발생 시점이 분봉 100개 이후인지 확인
3. **대시보드 RESTORED/LIVE 구분**: 기동 직후 100개 미만 구간에서 SHAP이 LIVE 표시되지 않는지 확인
4. **상관계수 레이블**: 파라미터 상관계수 표시에서 CVD/VWAP/OFI 등 정상 한글 축약어 표시 확인

---

## 2026-05-20 (65차 — 신뢰도·VWAP 흐름 분석 + 진입 체크리스트 7종 개선)

**Work**: 10:01 로그 기반 "매수 방향 → X등급" 흐름 정밀 분석. 신뢰도·VWAP 이상점 4종(사용자 제시) 점검 후 추가 이상점 3종 발견. 총 7종 개선을 체크리스트·라우터·대시보드·main 4개 파일에 구현.

### 분석 요약 (2026-05-20 10:01 기준)

| 구간 | 상태 |
|---|---|
| dir=+1 conf=43.2% | 신뢰도 미달 (OPEN_VOLATILE 기준 63%) |
| CORE ['3_vwap'] 실패 | 가격이 VWAP 아래 → 매수 방향 불일치 |
| 최종 등급 X (pass_count=7) | CORE 실패 강제 X |
| 09:05~09:34 | opt_pcr_slope_norm 극단값, cvd_slope, ofi 이상 z-score 반복 → confidence 40%대 고착 |

### 수정 내용 (7종)

| # | 파일 | 변경 내용 |
|---|---|---|
| ① | `strategy/entry/checklist.py` | 신뢰도 미달 시 즉시 X 반환 — CORE와 동일 강제 차단 |
| ② | `strategy/entry/time_strategy_router.py` + `main.py` | `get_zone_min_confidence()` 추가. `actual_min_conf = max(레짐 기준, 시간대 기준)`. 전 구간(checklist·update_prediction·update_data) 통일 |
| ③ | `main.py` | `checklist.evaluate()` 호출에 `cvd_exhaustion`·`micro_regime` 추가 — VWAP 역추세 예외 분기 실제 작동 |
| ④ | `dashboard/main_dashboard.py` | `_conf_chk_name_label` 저장 → `update_data()`에서 매분 `"신뢰도 ≥ {min_conf:.0%}"` 갱신 |
| ⑤ | `strategy/entry/checklist.py` | CVD·OFI 중립(0) 양방향 통과 차단 — `>= 0` → `> 0` |
| ⑥ | `strategy/entry/checklist.py` | 외인 방향 OR → AND — 콜/풋 순매수 양수 AND 상대우위 모두 충족 필요 |
| ⑦ | `main.py` | 손실률 분모 `50_000_000` 하드코딩 → `max(_ts_current_sizer_balance(self), 50_000_000)` |

### 65차 실세션 확인 사항 (2026-05-21)

1. **신뢰도 강제 X**: SIGNAL 로그에 `[Checklist] 신뢰도 미달 XX.X% < YY.Y% → 강제 X등급` 로그 발생 확인
2. **min_conf 통일**: OPEN_VOLATILE 구간 체크리스트 판정이 63% 기준 적용 확인 (NEUTRAL 레짐 시 58% 아님)
3. **VWAP 역추세 분기**: `cvd_exhaustion > 0` + `vwap_position < -1.5` 동시 발생 시 `[Checklist] 통과 X/9 → 등급 X (모드=MEAN_REVERSION)` 로그
4. **UI 레이블**: 진입 관리 탭 체크리스트 "신뢰도 ≥ 58%" → 시간대별 실제 기준(%%) 표시 확인
5. **CVD·OFI 0값 차단**: cvd_direction=0 시 `4_cvd` X로 처리되는지 DEBUG 로그 확인

---

## 2026-05-20 (64차 — 09:34 재시작 점검 + 3종 이상점 수정)

**Work**: 63차 수정 후 09:34:44 장중 재시작 결과 점검. 크래시 복구는 성공했으나 성능/재학습 타이밍 이상점 2종 + 옵션체인 블로킹 1종을 추가 발견하여 수정.

### 장중 이벤트 타임라인 (5/20 재시작 기준)

| 시각 | 이벤트 | 판정 |
|---|---|---|
| 09:34:44 | 재시작 | — |
| 09:35:00 | `[WarmupRetrain]` STEP 3에서 GBM 재학습 시작 | ❌ (P1 수정 전) |
| 09:35:05 | `[CB] 5분 진입 정지` — 파이프라인 5026ms | ❌ CB⑤ 발동 |
| 09:38:44 | `[Retrain]` 완료 | ✅ |
| 09:39:45 | CB PAUSED 확인 | ✅ |
| 09:41:03 | `[CB⑤] 3347ms 경고` | ❌ OptionChain BlockRequest 루프 |
| 09:41:03 | CB 해제 | ✅ |
| 전 구간 | signal() takes 2 크래시 재발 없음, PCR/investor_age z-score 경고 없음 | ✅ |

### 수정 내용

| 파일 | 변경 내용 |
|---|---|
| `main.py` | P1: `connect_broker()` 장중(09:00~15:10) 완료 시 즉시 GBM 재학습 스레드 시작. 첫 파이프라인 STEP 3 skip 보장 |
| `main.py` | P2: `__init__`에 `_gbm_retrain_running: bool = False`, `_last_close: float = 0.0` 명시적 초기화 |
| `main.py` | P3: STEP 4에서 `option_chain_snap.refresh()` 제거 → `get_features()` 캐시 읽기만. `_poll_option_chain()` QTimer 콜백 신규 추가. `daily_close()`에 `_option_chain_timer.stop()` |
| `strategy/runtime/broker_runtime_service.py` | P3: `_option_chain_timer = QTimer()` 생성 + `ensure_market_open_runtime_started()`에서 `start(300_000)` |

### 64차 실세션 확인 사항 (2026-05-21)

1. 장중 재시작 시: `[WarmupRetrain] 장중 재시작 — GBM 즉시 재학습 시작` 로그 발생
2. 첫 파이프라인 CB⑤ 없음: 재시작 후 첫 파이프라인 처리시간 < 5000ms
3. 옵션체인 폴링 분리: `[OptionChain] 갱신 X.Xs` 로그가 파이프라인 PipePerf 외부에서 발생
4. STEP 4 지연 해소: `[PipePerf]` S4 수치 100ms 이하 유지

---

## 2026-05-20 (63차 — 5/20 로그 이상점 분석 + 파이프라인 크래시 버그 5종 수정)

**Work**: 5/20 실세션 로그 전수 분석(5/18 대비 비교 포함). 2단계 장애 확인 — 1단계 CB⑤ 지연, 2단계 `log_manager.signal()` 시그니처 버그로 09:14부터 파이프라인 매분 크래시. 총 4개 파일 5개 버그 수정.

### 장중 이벤트 타임라인 (5/20)

| 시각 | 이벤트 | 원인 |
|---|---|---|
| 08:45 | startup sync rows=0 → blank-as-flat | Cybos 모의투자 잔고 TR 미반환 (무해) |
| 09:00:06 | 파이프라인 **6179ms** → CB⑤ 5분 정지 | GBM 재학습(242초) + 첫 파이프라인 CPU 경합 |
| 09:00~09:15 | 전 구간 grade=X, conf 33~42% | CORE 피처 실패 + z-score 극단값 |
| 09:01 | HealthPolicy **Degraded Mode** 진입 | 6179ms 초과 |
| 09:04~09:12 | CB⑤ 경고 1~3초대 반복 | 재학습 완료 전 CPU 압박 지속 |
| 09:09 | IntradayRegime **NORMAL → CRASH** | day_ret 급락 감지 |
| 09:14:02 | **파이프라인 예외 크래시 시작** | `signal() takes 2 args but 3 given` |
| 09:15~09:17 | watchdog 복구 실패 매분 반복 | 동일 코드 경로 재실행 → 동일 예외 |
| 09:17:02 | `[복구 실패] 파이프라인 예외` 확인 | signal() 버그 직접 증거 |
| 전일 | 실제 매매 0건, 포지션 FLAT 유지 | CB 정지 + X등급 → 매매 사고 없음 |

### 수정 버그 (우선순위 순)

| # | 버그 | 파일 | 심각도 |
|---|---|---|---|
| 1 | `log_manager.signal(msg, "WARNING")` → `takes 2 args but 3 given` 파이프라인 매분 크래시 | `logging_system/log_manager.py` | **CRITICAL** |
| 2 | `opt_pcr_slope_norm=-5.87` 고정 — call=0 시 PCR=6.59억 → slope 극단 음수 → clip -1.0 | `collection/options/pcr_store.py` | HIGH |
| 3 | GBM 재학습 09:00 충돌 — 242초 재학습이 첫 파이프라인과 겹쳐 CB⑤ 발동 | `main.py` | HIGH |
| 4 | `quality_investor_age_sec` z=+45.70 — 09:00 첫 파이프라인 직전 age≈840초 | `features/feature_builder.py` | MEDIUM |

### 수정 내용

| 파일 | 변경 내용 |
|---|---|
| `logging_system/log_manager.py` | `signal(msg)` → `signal(msg, level="INFO")` — `system()`·`trade()`·`health()`와 시그니처 통일 |
| `collection/options/pcr_store.py` | `call_abs < PCR_MIN_CALL_ABS(1000)` 시 버퍼 스킵. `PCR_MAX=4.0` 상한 캡. 콜 미로드 방어 |
| `main.py` | `pre_market_setup()` 끝에 `[PreRetrain]` 블록 추가 — 08:55에 warmup 재학습 사전 시작 |
| `features/feature_builder.py` | `investor_age_sec = min(..., 300.0)` — 5분 상한. 840초 → 300초 → z-score 폭주 감소 |

### 5/18 vs 5/20 개선 비교

| 항목 | 5/18 | 5/20 | 판정 |
|---|---|---|---|
| z-score 감지 기능 | 없음 | 매분 전 호라이즌 경고 | ✅ 추가됨 |
| GBM 재학습 시간 | 61.8초 (10피처) | 242.5초 (91피처) | ❌ 악화 |
| 첫 진입 시각 | 09:23 (9/9 통과) | 없음 (X등급 지속) | ❌ |
| 매매 사고 | 없음 | 없음 (FLAT 유지) | ✅ |
| GBM 정확도 | 37~40% | 33~38% | ❌ 소폭 하락 |

### 잠재 버그 현황 (발화 전 확인)

- `잔고 TR 파싱` — `'총매매'·'총평가손익'·'총평가수익률'` 3개 필드에 동일 잔고값. 실전 전환 전 수정 필요.
- `프로그램 매매 TR 미발견` — `program_supported=False` 매분 반복. 피처 공백 지속.

---

## 2026-05-19 (62차 — 매크로 레짐 종합 강화: Layer 2 IntradayTacticalRegime + micro 1.5 + 레짐 대시보드 탭)

**Work**: 5/19 제로트레이드 근본원인 분석 완결 이후, 시스템이 "장전 매크로 분위기"만 참고하고 "장중 국내 선물 붕괴"를 레짐으로 인식 못하는 구조 결함을 매크로 레짐 2계층으로 해결. macro_fetcher 초회 fetch=0 편향, micro_regime ATR 둔감 2개 버그도 함께 수정.

### 주요 작업

| 항목 | 내용 |
|---|---|
| macro_fetcher 첫 fetch=0 버그 수정 | `_first_fetch_done` 플래그 추가. 초회는 `_prev` 시딩만, 2회차부터 실 변화량 계산 |
| IntradayTacticalRegime 신규 구현 | `collection/macro/intraday_tactical_regime.py` 신규. NORMAL/DAY_RISK_OFF/CRASH 3상태. 매분 day_ret·ATR·z_warn·contrarian 기반 전환. RECOVERY 3조건 복귀 로직 |
| micro_regime ATR 둔감 수정 | `ATR_VOLATILE_MULT` 2.0→1.5. 복합 조건 추가 (z_warn≥3 OR atr≥1.25+ADX≥30). 5/19 폭락일 급변장 0회 → 수정 후 발동 예상 |
| main.py Layer 2 통합 | import·인스턴스화·매분 update 파이프라인 삽입 (contrarian 이후 지점). 진입 차단 로직 2종 (롱금지/숏금지) + block reason 로그 체인. `reset_daily()` 연결 |
| RegimePanel 신규 구현 | `dashboard/panels/regime_panel.py` 신규. Layer1/Layer2/Micro 3배지 행 + 진입정책 GridLayout + 레짐 이력 로그 |
| main_dashboard "🌐 레짐" 탭 추가 | `mid_tabs.addTab(regime_panel)`. `update_supply_macro()` → `regime_panel.update_layer1()` 훅. `update_micro_regime()` → `regime_panel.update_micro()` 훅 |
| Cybos COM 세션만료 크래시 진단 | 기동 직후 exit code 1 (Python traceback 없음) = Cybos 프로세스 없이 COM dispatch 시 C레벨 크래시. 해결: CYBOS_PLUS.bat → CYBOS5.bat 재기동 후 실행 |

### 신규 파일

| 파일 | 내용 |
|---|---|
| `collection/macro/intraday_tactical_regime.py` | IntradayTacticalRegime: 매분 장중 레짐 분류기. 진입정책 테이블 내장 |
| `dashboard/panels/regime_panel.py` | RegimePanel: Layer1/2/Micro 3계층 실시간 모니터 위젯 |

### 수정 파일

| 파일 | 변경 내용 |
|---|---|
| `collection/macro/macro_fetcher.py` | `_first_fetch_done` 플래그. 초회 시딩 전용 경로 분기 |
| `collection/macro/micro_regime.py` | `ATR_VOLATILE_MULT` 2.0→1.5. `z_warn_count` 파라미터 추가. 복합 급변 조건 |
| `main.py` | IntradayTacticalRegime import/인스턴스/파이프라인/차단/reset 전체 |
| `dashboard/main_dashboard.py` | "🌐 레짐" 탭 + `regime_panel.update_layer1/micro()` 훅 |

### 발견된 버그 (전부 수정 완료)

| 버그 | 근본 원인 | 수정 |
|---|---|---|
| 매크로 chg 첫 fetch 항상 0 | `_prev` 없으면 변화량=0 → NEUTRAL 편향 | `_first_fetch_done` 분기 |
| micro_regime 5/19 급변장 0회 | `ATR_VOLATILE_MULT=2.0` — ATR ratio 최댓값 1.33으로 임계값 미달 | 1.5로 완화 + 복합 조건 |

### 미확인 (다음 장 기동 필요)

1. `[IntradayRegime] NORMAL → DAY_RISK_OFF` 로그 당일 하락 시 발생 여부
2. `[IntradayRegime] DAY_RISK_OFF — 신규 롱 금지` 차단 로그 발생 여부
3. "🌐 레짐" 탭 정상 표시 및 Layer1/2/Micro 배지 실시간 갱신
4. micro_regime 급변장 발동 확인 (장중 ATR 확대 구간)
5. macro_fetcher 2회차부터 chg 실수치 정상 계산 로그

---

## 2026-05-19 (61차 — CB HALT 장중 분석 + 대시보드 지표 버그 5종 수정 + CB⑤ Cybos 재설계)

**Work**: 오늘 장중 CB=HALTED 발동(11:11~12:19) 원인을 분석하고, 분석 과정에서 발견된 대시보드 지표 버그 5종을 수정. Cybos 리팩토링 누락으로 CB⑤가 실질 비활성 상태였던 구조 결함을 파이프라인 처리시간 기반으로 재설계.

### 주요 작업

| 항목 | 내용 |
|---|---|
| CB HALT 원인 분석 | 50분정확도 50%→21% 하락. 15m/10m 고신뢰(70~85%) 역추세 연속 오답. Mid-Conf Blind Spot + CB③ strict 모드 발동 추정 |
| 예측 로그 direction 추가 | `main.py` — 실패 로그에 `예측=DN 실제=UP` 방향 추가. 방향성 분석 가능해짐 |
| 정확도=0.0% 버그 수정 | `main.py` — `update_system_status()` 호출 시 `accuracy=_acc30m` 파라미터 누락 수정 |
| API지연=0ms 버그 발견·수정 | Cybos 리팩토링 시 `latency_sync.record()` 연결 누락으로 항상 0ms 고정. CB⑤도 사실상 비활성 상태였음 |
| CB⑤ Cybos 재설계 | 파이프라인 처리시간을 대체 지표로. `record_pipe_latency()` 신규. 1초→경고, 5초→5분 PAUSE |
| 파이프라인 타이머 | `main.py` — `_pipe_t0` 시작, `_pipe_ms` 계산 후 CB·헬스·SYSTEM 로그 공용 |
| 모델 AI 카드 버그 수정 | 정확도(50분)/SGD비중/자가학습 초기값("61.4%","34%","● 활성") 고정 버그 — `_model_vals` 참조 저장 + `update_model_cards()` 신규 + 매분 갱신 연결 |
| 헬스 카드 "처리시간" 전환 | "API 지연" → "처리시간". HealthPanel·LogPanel 양쪽. 툴팁(구간·동작 안내) + underline dotted 스타일 |
| HealthPanel 임계값 정합 | 내부 기본값 500→1000ms(경고), 1000→5000ms(임계) — CB_PIPE 기준과 통일 |
| 스파크라인 레이블 수정 | "API 지연 추이" → "처리시간 추이" 2곳 (초기문자열·동적 setText) |
| 테스트 추가 | `test_circuit_breaker.py` — `record_pipe_latency` 경고(1500ms→NORMAL) + 정지(6000ms→PAUSED) |

### 발견된 버그 (전부 수정 완료)

| 버그 | 근본 원인 | 수정 |
|---|---|---|
| `정확도=0.0%` 항상 표시 | `update_system_status()` accuracy 파라미터 누락 | `accuracy=_acc30m` 전달 |
| `API지연=0ms` 항상 표시 | `latency_sync.record()` 실제 코드에서 한 번도 호출 안 됨 (Cybos 리팩토링 누락) | 파이프라인 처리시간으로 대체 |
| CB⑤ 실질 비활성 | 위와 동일 — `record_api_latency(0.0)` 항상 0 | `record_pipe_latency()` 신규 |
| 모델 AI 카드 고정값 | `_model_vals` dict 미생성으로 위젯 참조 없음 | 참조 저장 + 업데이트 함수 |

---

## 2026-05-19 (60차 — 5/19 CB③ 심층분석 기반 안전장치 6종 + Shadow/Contrarian 구현)

**Work**: 5/19 세션 CB③ 조기 정지(09:50, acc30m=19%) 원인을 두 분석가 관점으로 분석 후, 즉시 구현 가능한 안전장치 6종을 우선순위 순서대로 전체 구현. 매분 파이프라인 전체 흐름 문서화.

### 주요 작업

| 항목 | 내용 |
|---|---|
| 1순위: Mid-Conf Blind Spot Tracker | `circuit_breaker.py` — 60~85% 구간 연속 오답 추적. 7연속 → strict 모드(임계값 35%→50%). `settings.py` 3개 상수 추가 |
| 2순위: Brier Score 실시간 추적 | `circuit_breaker.py` — `brier = (conf-actual)²` 이동평균(10건). >0.35 경고, >0.45 사이즈 50% 패널티. `brier_size_mult` 속성 추가 |
| 3순위: 재시작 루프 브레이커 | `circuit_breaker.py` — `_daily_halt_count` 추적. 2회→50%, 3회→완전관망. `restart_size_mult` / `is_restart_blocked()` 추가 |
| 4순위: 장 시작 5분 DNA 진단 | `safety/market_dna.py` **신규** — 09:00~09:04 첫 5봉으로 방향일치·거래량·z-score·CORE 4항목 진단. 3/4 이상 이상 → dna_mult=0.25 |
| 5순위: CORE Health Score → Sizer 연동 | `features/core_health.py` **신규** — streak+z_warn 기반 0~100 점수화. `position_sizer.py` — core_health_mult/brier_mult/restart_mult/dna_mult 4개 안전 배수 파라미터 추가 |
| 6순위: Shadow Session | `safety/shadow_session.py` **신규** — acc30m≥40%+CoreHealth≥70+z_warn<2 게이트. 09:40 이전 통과→LIVE, 미통과→BLOCKED 상태 머신 |
| 6순위: Contrarian Mode | `safety/contrarian_mode.py` **신규** — acc30m<25%+동방향10연속+NEUTRAL 3조건. WATCHING→ARMED→ACTIVE 상태 머신. 가상 역베팅 PnL 집계 |
| 6순위: 실험 게이트 대시보드 탭 | `dashboard/panels/experiment_gate_panel.py` **신규** — Shadow/Contrarian 상태·조건·가상PnL 시각화. `main_dashboard.py` "🧪 실험 게이트" 탭 추가 |
| 파이프라인 전체 문서화 | `docs/PIPELINE_FLOW.md` **신규** — STEP 1~9 전체 흐름, 안전 배수 조합 매트릭스, CB 상태 조합표 |

### 5/19 CB③ 분석 핵심 발견

| 발견 | 내용 |
|---|---|
| 09:34 이후 30분 예측 전부 오답 | acc30m이 단조 감소. 신규 정답 추가 없이 오답만 쌓임 |
| Overconfidence | conf 48~83%인데 30m 정확도 0% → Brier Score 0.45+ |
| CORE 피처 붕괴 | 09:15~09:50 vwap/ofi 반복 탈락 — 엔진 경고등 켜진 채 액셀 |
| NEUTRAL 레짐 LONG 일변도 | 09:15~09:50 전 시그널 dir=+1. 방향 편향 차단기 부재 |
| 죽음의 재시작 루프 | 3회 연속 재시작(08:45→10:06→10:13) 모두 동일 실패 반복 |

### 안전 배수 조합 (5/19 재현 시 예상값)

```
core_health_mult × brier_mult × restart_mult × dna_mult
= 0.5 × 0.5 × 0.5 × 0.25 = 0.031 → 사실상 0계약
```

### 수정 파일 (60차)

| 파일 | 변경 내용 |
|---|---|
| `config/settings.py` | CB 신규 상수 9개 (Mid-Conf 3, Brier 3, HALT 2 + 기존 구조 유지) |
| `safety/circuit_breaker.py` | Mid-Conf·Brier·재시작루프 3종 추가. status/state_dict/reset 모두 반영 |
| `safety/market_dna.py` | **신규** — 장 시작 5분 DNA 진단기 |
| `safety/shadow_session.py` | **신규** — Shadow Session 상태 머신 |
| `safety/contrarian_mode.py` | **신규** — 역모델 스위치 트래커 |
| `features/core_health.py` | **신규** — CORE 피처 건강 점수 계산기 |
| `model/multi_horizon_model.py` | `last_z_warn_count` 속성 노출, 예측 결과에 `extreme_count` 포함 |
| `strategy/entry/position_sizer.py` | 안전 배수 4종 파라미터 추가 (core_health/brier/restart/dna) |
| `dashboard/panels/experiment_gate_panel.py` | **신규** — Shadow + Contrarian 모니터 UI |
| `dashboard/main_dashboard.py` | "🧪 실험 게이트" 탭 mid_tabs 마지막에 추가 |
| `main.py` | MarketDNA·CoreHealth·Shadow·Contrarian 초기화·매분업데이트·Sizer연결·reset_daily 전체 |
| `docs/PIPELINE_FLOW.md` | **신규** — 매분 파이프라인 전체 흐름 문서 |

### 커밋
- 60차: 5/19 CB③ 분석 기반 안전장치 6종 + Shadow/Contrarian 모의투자 검증 패널 구현

---

## 2026-05-19 (59차 — 손익추이 DB 초기화 버튼 추가)

**Work**: 손익추이 DB 초기화 기능을 우측 상단 서버 선택 행에 UI 추가.

### 주요 작업

| 항목 | 내용 |
|---|---|
| DB초기화 버튼 UI | `MireukDashboard._rdo_row`에 🔓 체크박스 + "DB초기화" 버튼 추가 (모의투자/실서버/상태유지 우측) |
| 잠금 설계 | 기본 비활성, 🔓 체크 시 버튼 활성(빨간 스타일), 초기화 후 자동 잠금 복원 |
| 확인 다이얼로그 | Cancel 기본값, "되돌릴 수 없음" 경고 |
| 백업 + 초기화 | 타임스탬프 백업(`trades_backup_YYYYMMDD_HHMMSS.db`) 생성 후 trades/daily_stats/daily_broker_pnl 전체 삭제 + sqlite_sequence 리셋 + VACUUM |
| 패널 즉시 갱신 | `self.log_panel.refresh_pnl_history([])` 로 손익추이 탭 즉시 빈 상태로 갱신 |
| 패널 참조 버그 수정 | `getattr(self, "_pnl_history_panel", None)` → `self.log_panel.refresh_pnl_history([])` |

### 수정 파일 (59차)

| 파일 | 변경 내용 |
|---|---|
| `dashboard/main_dashboard.py` | `_rdo_row` DB초기화 버튼 추가, `_on_db_reset_clicked()` 핸들러 신규 |

### 커밋
- `f4607c2` — 59차: 손익추이 DB 초기화 버튼 추가

---

## 2026-05-18 (58차 — 5/18 세션 심층분석 기반 안전장치 6종 구현)

**Work**: 5/18 트레이딩 세션 심층 리뷰(수익률 상위 1% 트레이더 2인 분석 종합 + 자체 로그 분석)에서 도출된 우선순위 6개 안전장치 전체 구현. B113 설계 결정 번복(실손 데이터 근거).

### 주요 작업

| 항목 | 내용 |
|---|---|
| P0: PG+CB 상태 영속화 | `circuit_breaker.py` / `profit_guard.py` — `to_state_dict()` / `from_state_dict()` 추가. `session_recovery_service.py` — 재시작 시 복원 로직 추가. `main.py` — `_write_session_state()`가 PG+CB 상태 직렬화. `_load_state_persist_flag()` 추가. |
| P0: 상태유지 체크박스 | `dashboard/main_dashboard.py` — "상태유지" QCheckBox를 모의투자/실서버 동일 행 우측에 추가. `_save_ui_prefs()` / `_restore_ui_prefs()` 연동. `state_persist_enabled` 키 저장. |
| P1-a: Restart Armistice | `main.py` — `_restart_armistice_until` (90초) + `_restart_armistice_sync_count` (≥2 clean) 양쪽 모두 통과 전까지 신규 진입 차단. 브로커 sync 클리어 구간에서 sync_count 증가. |
| P1-b: Position Integrity Checksum | `main.py` — `_ts_check_position_integrity()` 신규 함수. engine_qty vs broker_qty vs pending_qty 삼각 검증. 불일치 2회: WARNING + Slack 알림. 3회: 진입 차단. `_integrity_broker_qty`는 balance 이벤트에서 갱신. |
| P2-b: Setup Expectancy Ledger | `utils/db_utils.py` — trades 테이블에 `meta_action`, `hurst_bucket`, `hour_bucket`, `was_restart_after`, `had_partial_fill` 컬럼 마이그레이션. `main.py` — 진입 시 컨텍스트 저장, `_record_trade_result()`에서 5컬럼 INSERT. |
| P2-b: 셋업 기대값 패널 | `dashboard/panels/setup_expectancy_panel.py` — 신규 생성. meta_action / hurst_bucket / hour_bucket / grade 4개 섹션, 시간 필터 4종(전체/오늘/이번주/이번달), 1분 자동 갱신, showEvent 즉시 갱신. `dashboard/main_dashboard.py` — "📊 셋업 기대값" 탭 mid_tabs 마지막에 추가. |
| P3-a: OnlineLearner 오염 학습 보호 | `main.py` — `_stuck_this_minute` 플래그. ENTRY/EXIT stuck(각 60초/10초 임계) 발생 분봉은 STEP 2 SGD 학습 전체 스킵. |
| P3-b: Reverse Entry Clamp | `main.py` — `_last_exit_direction` 추가. 청산 후 180초 이내 반대 방향 진입 차단. `_last_exit_ts`는 기존 변수 재사용. |

### 수정 파일 (58차)

| 파일 | 변경 내용 |
|---|---|
| `safety/circuit_breaker.py` | `to_state_dict()` / `from_state_dict()` 추가 |
| `strategy/profit_guard.py` | `to_state_dict()` / `from_state_dict()` 추가 |
| `strategy/runtime/session_recovery_service.py` | `restore_daily_state()` — PG+CB 상태 복원 블록 추가 |
| `utils/db_utils.py` | `_migrate_trades_db()` — 셋업 태그 5컬럼 마이그레이션 추가 |
| `main.py` | `__init__` 신규 변수 7개, `_load_state_persist_flag()`, `_write_session_state()` PG/CB 직렬화, broker sync 구간 armistice 카운터, `_integrity_broker_qty` 갱신, STEP 2 stuck 학습 가드, STEP 7 Armistice+Integrity+ReverseClamp 조건 추가, `_record_trade_result()` 5컬럼 확장, `_ts_apply_exit_cooldown()` last_exit_direction, `_ts_check_position_integrity()` 신규 함수 |
| `dashboard/main_dashboard.py` | `chk_state_persist` 체크박스 생성·배치·연결·저장·복원, `setup_expectancy_panel` 탭 추가 |
| `dashboard/panels/setup_expectancy_panel.py` | 신규 생성 — 셋업 기대값 집계 패널 |

---

## 2026-05-18 (57차 — UI 체크박스 설정 유지 버그 수정)

**Work**: 슬랙알림·중패널_Auto·우패널_Auto 체크박스 설정이 프로그램 재시작 시 기본값 True로 초기화되는 버그 원인 분석 및 수정.

### 주요 작업

| 작업 | 내용 |
|---|---|
| B120 분석 | `_restore_ui_prefs` 내 종목 복원 중 `_on_symbol_changed` → `_save_ui_prefs` 호출 시 체크박스가 아직 기본값 True 상태 → 파일에 덮어씀 → 다음 실행 시 True로 복원되는 사이클 확인 |
| B120 수정 | `_restore_ui_prefs` 내 `_on_symbol_changed(selected_symbol)` → `_update_symbol_label(selected_symbol)` 교체 (dashboard/main_dashboard.py L7814) |
| 중복 시그널 제거 | `main.py` L4128~4130: `chk_slack.stateChanged` → `_save_ui_prefs` 연결 제거. `main_dashboard.py` L7610에 `toggled` 연결이 이미 존재해 중복이었음 |

### 버그 발견 (B120)

| 항목 | 내용 |
|---|---|
| 증상 | 중패널_Auto·우패널_Auto를 해제하고 종료해도 다음 실행 시 체크됨 |
| 원인 | `_restore_ui_prefs` 실행 순서 — 종목 복원(L7813)이 슬랙/mid/right 복원(L7816~)보다 먼저, `_on_symbol_changed` 내부에서 `_save_ui_prefs` 호출 → 파일에 True 덮어씀 |
| 수정 | `_on_symbol_changed` → `_update_symbol_label` 교체 (저장 트리거 없음) |

---

## 2026-05-18 (56차 — 상단 배지 5종 점검·수정)

**Work**: 대시보드 상단 배지(FLAT·위클리·감마스퀴즈·NEUTRAL·L2) 전체 업데이트 흐름 점검. 갱신 누락 3종·툴팁 오류 2종·dead code 1종 수정.

### 주요 작업

| 작업 | 내용 |
|---|---|
| FLAT 배지 갱신 누락 수정 | `DashboardAdapter.update_position()`에 `lbl_pos` 헤더 배지 갱신 로직 추가. LONG=녹색·SHORT=빨강·FLAT=회색 |
| 위클리 배지 월요일 만기 추가 | `_calc_cycle_badge()` 목요일 전용 → 월/목 양방향. `[월]위클리 D-x` / `[목]위클리 D-x` / `[목]월간 D-x` 형식 |
| 감마스퀴즈 배지 갱신 누락 수정 | `update_option_chain()`에 `_update_gamma_badge()` 추가. `opt_gex_bn`·`opt_gex_sign` 기반 판정. 초기값 "감마스퀴즈" → "감마 —" |
| NEUTRAL 배지 툴팁 오류 수정 | "매분 갱신" → "08:55 장전 1회 수집, 당일 고정" |
| NEUTRAL 배지 usd_krw 누락 수정 | `update_supply_macro()` 호출에 `usd_krw=macro_data["usd_krw_chg_pct"]` 추가. 로그에 항상 +0.00 출력되던 문제 수정 |
| L2 dead code 제거 | `_tier.check()`의 `if max_qty == 0:` 분기 — `stop_tier_hit is not None` 블록 이후라 절대 도달 불가. 제거. |
| L2 툴팁 개선 | "거래중단 임계 도달 시 금일 거래 영구 중단" → Tier 4 400만원 기준·상태값 명시 |

### 버그 발견 요약 (B116~B119)

| ID | 증상 | 원인 | 수정 |
|---|---|---|---|
| B116 | FLAT 배지 포지션 전환 후에도 "FLAT" 고정 | `update_position()`이 `exit_panel`만 갱신, `lbl_pos` 미갱신 | `lbl_pos` setText+setStyleSheet 추가 |
| B117 | 위클리 배지가 항상 목요일 만기 기준 | `_calc_cycle_badge()`가 목요일만 계산 | 월/목 양방향, 더 가까운 쪽 선택 |
| B118 | 감마스퀴즈 배지 초기값 고정 | `update_option_chain()`이 div_panel만 갱신, `lbl_gamma` 미갱신 | `_update_gamma_badge()` 추가 |
| B119 | NEUTRAL 로그 USD/KRW=+0.00 항상 출력 | `update_supply_macro()` 호출 시 `usd_krw` 인수 누락 | `usd_krw` 인수 추가 |

---

## 2026-05-18 (55차 — 옵션 체인 스냅샷 파이프라인 완성 + B115 front month 만기 버그 수정)

**Work**: Cybos 옵션 OI 수집 탐색 결과를 바탕으로 `OptionChainSnapshot` 클래스를 `main.py` STEP 4에 통합하고 대시보드 '다이버전스 + 포지션' 탭 하단에 옵션 체인 시각화 섹션 추가. 실세션 재시작(15:16) 후 UI 점검에서 PCR=1.000/OI=0 이상 발견 → 5월 만기(5/14) 이후 `_filter_front_month`가 여전히 "2605"(5월)를 선택하는 B115 버그 확인 및 수정.

### 주요 작업

| 작업 | 내용 |
|---|---|
| `collection/options/option_chain_snapshot.py` 신규 | 5분마다 `CpUtil.CpOptionCode` + `Dscbo1.OptionMst` BlockRequest 폴링 → PCR/ATM OI/GEX 7개 피처 계산 |
| `main.py` STEP 4 통합 5곳 | import·`__init__`·`connect_broker`·STEP4·`reset_daily`. refresh() 반환값으로 실제 갱신 시에만 dashboard 업데이트 |
| 대시보드 옵션 섹션 | DivergencePanel 기존 섹션 간격 스퀴즈 후 하단 추가: freshness progress bar (초록→주황→빨강) + 카드 5개(체인 PCR/ATM PCR/GEX/콜 OI/풋 OI) |
| `MainDashboard.update_option_chain()` | div_panel.update_option_chain() 위임 메서드 + main.py 연결 |
| B115 수정 | `_option_expiry()` — 해당 월 2번째 목요일 계산. `_filter_front_month` — 만기 지난 달 skip → 현물월 자동 선택 |

### 버그 발견 및 수정 (B115)

| 항목 | 내용 |
|---|---|
| 증상 | 15:23 수집 후 UI에 "수집완료" 표시, PCR=1.000·OI=0·GEX=0.0B |
| 원인 | `_filter_front_month`가 ym 알파벳 정렬 첫 번째("2605") 선택 → 5월 만기(5/14) 이후 모든 OI=0. BlockRequest는 dib_status=0이나 OI 필드 0 반환 → call_oi=0 → PCR default 1.0 |
| 수정 | `_option_expiry(year, month)` 추가 (2번째 목요일). ym 순회 시 `today ≤ expiry` 첫 달 선택 |
| 검증 | 2605: 만기 5/14 < 오늘 5/18 → SKIP. 2606: 만기 6/11 ≥ 오늘 → USE. 6월 ATM 범위(1190-1250) 콜25+풋25=50개 확인 |

---

## 2026-05-18 (54차 — B112/B114 개선 + 실세션 로그 분석)

**Work**: 10:57:19 재시작 이후 로그를 분석하여 ProfitGuard-L4 무력화(B113), stale broker_sync_reason 재발(B112), IntrabarTPCheck 미발동(B114) 3종의 버그를 발견. B113은 시험가동 중 유지 결정. B112·B114 개선 구현 완료.

### 오늘 실세션 흐름 요약

| 시각 | 이벤트 |
|---|---|
| 09:24 | LONG 5계약 @ 1131.74 진입 (A등급) |
| 09:26 | TP1 +7.25pt (+360,902원) |
| 09:27~09:50 | stuck — 브로커 동기화 매분 경고 (TP2/TP3 미발동) |
| 09:51~09:56 | 재시작 후 수동 청산으로 해소 |
| 09:59 | LONG 4계약 @ 1151.52 진입 |
| 10:00 | TP1 +5.43pt → 10:01 TP2 +8.69pt (1분 간격 정상) |
| 10:04 | 하드스톱 잔여 2계약 청산 |
| 10:29 | LONG 4계약 진입 (브로커 잔여 3계약 포함 → 7계약) |
| 10:33 | TP1 2계약 체결 → 10:38 하드스톱 5계약 전량 청산 |
| 10:38 | **ProfitGuard-L4 발동** — 2연속 손실 → 당일 진입 중단 선언 |
| 10:57:19 | **재시작** — ProfitGuard 상태 소멸(B113) |
| 11:07 | LONG 2계약 @ 1173.02 (ProfitGuard 무력화로 진입 허용) |
| 11:13 | TP1 +4.64pt → 11:14 TP2(전량) +6.18pt |
| 11:17 | LONG 6계약 @ 1181.20 진입 |
| 11:22 | TP1 2계약 → 11:23 TP2 2계약 → 11:25 TP3 2계약 전부 성공 |

### 주요 발견

| 발견 | 내용 |
|---|---|
| B113: ProfitGuard 재시작 소멸 | 10:38 L4 발동 후 10:57:19 재시작 → `_profit_guard_blocked` 메모리에만 존재, 파일 미저장 → 11:07 진입 허용. 결과는 수익이나 CB 무력화는 심각한 설계 결함 |
| B112 재발: stale broker_sync_reason | 11:09 EntryStuck 해소 캐시(`entry stuck resolved broker LONG 2 @ 1173.02`)가 11:14 FLAT 이후에도 클리어되지 않아 11:17 EntryAttempt까지 오염 |
| B114: IntrabarTPCheck 미발동 | 11:13 TP1 체결 후 `[IntrabarTPSchedule]` 로그도 `[IntrabarTPCheck]` 로그도 없음. 근본 원인 불명확 — 진단 로그 추가로 5/19 파악 예정 |
| Hurst 실계산 확인 | 10:35부터 `hurst=0.122`, 이후 0.133~0.143 실계산값 출력. 10:34까지는 60봉 버퍼 부족으로 fallback=0.500 정상 |
| 53차 Fix 미적용 | 세션 시작(08:45) 후 53차 커밋(10:51) → 실행 중 프로세스에 미반영. 5/19 세션이 첫 적용 |

### 수정 내용

| 파일 | 변경 |
|---|---|
| `main.py` (L4803~4807) | [B112] `_ts_on_chejan_event` — 청산 완전 체결 후 FLAT이면 `_broker_sync_last_error = "flat after exit"` |
| `main.py` (L930~943) | [B114 진단] `_clear_pending_order` — QTimer 스케줄 시 `[IntrabarTPSchedule]` WARN 로그 + price=0 시 취소 로그 |
| `main.py` (L4029~4041) | [B114 진단] `_ts_intrabar_tp_check` — 가드 3케이스(pending 존재/FLAT/price=0) 각각 WARN 로그 |

---

## 2026-05-18 (53차 — 2차 목표 도달 후 미청산 버그 2종 수정)

**Work**: 실세션 스크린샷에서 2차 목표(TP2)가 "도달"로 표시됐음에도 청산이 실행되지 않는 흐름을 제보받음. `exit_manager.py`, `position_tracker.py`, `main.py` (`_ts_check_exit_triggers`, `_ts_execute_partial_exit`, `_clear_pending_order`, Chejan 콜백), `dashboard/main_dashboard.py` 전체 흐름을 코드 추적하여 버그 2종을 도출하고 수정 완료.

### 주요 발견

| 발견 | 내용 |
|---|---|
| TP2·TP3 "도달" 오표시 (대시보드) | `pending_active=True`이고 `pending_kind="EXIT_PARTIAL"`, `pending_stage=1`인 상태에서도 `st_shap_trig`(TP2)·`st_opt_trig`(TP3)에 초록 "도달" 표시. `pending_stage` 값을 참조하지 않아 운영자가 "TP2가 도달했는데 청산 왜 안 되지?"로 혼동 |
| Pending 해소 후 최대 1분 TP 지연 | `_clear_pending_order()` 이후 TP 재점검은 다음 분봉 파이프라인 시작 시에만 실행. TP1 완료 직후 가격이 TP3 위에 있어도 다음 분봉 종가까지 대기 |
| 당일 사례 재구성 | initial_quantity=5, stage_plan=(2,1,2). TP1 2계약 주문 → 1계약 체결(partial fill) → `pending_active=True, filled=1/2` 상태로 TP2·TP3 발동 차단. stuck 감지(10초)로 eventual 해소되지만 그 사이 추가 지연 |

### 수정 내용

| 파일 | 변경 |
|---|---|
| `main.py` | `_clear_pending_order()`: `_cleared_kind = str(self._pending_order.get("kind"))` 먼저 캡처. `_cleared_kind in ("EXIT_PARTIAL", "EXIT_MANUAL_PARTIAL")` + 포지션 잔존 시 `QTimer.singleShot(300, _ts_intrabar_tp_check)` 스케줄 |
| `main.py` | `_ts_intrabar_tp_check()` 신규 함수: pending 없음·포지션 존재·가격 유효 3중 확인 후 TP1→TP2→TP3 순차 `_execute_partial_exit` 호출 (각 단계 후 pending 재확인) |
| `main.py` | `TradingSystem._intrabar_tp_check = _ts_intrabar_tp_check` 등록 |
| `dashboard/main_dashboard.py` | 청산 트리거 배지 override 블록: `pending_stage` 기반으로 주문중인 TP 행(`st_cvd_trig`/`st_shap_trig`/`st_opt_trig`)에 "주문중" 오버레이, 미발동 상위 TP는 "대기" 교체 |

---

## 2026-05-18 (52차 — 손익 패널 4종 불일치 원인 분석 + 수정)

**Work**: 실세션 스크린샷에서 실시간 잔고 금일손익(3,006,750) / 손익 PnL 탭(2,261,018) / 손익 추이 탭(3,555,000) / HTS(2,877,000) 네 패널 값이 제각각인 현상을 요청받음. 각 패널의 데이터 소스·업데이트 흐름을 코드로 추적하여 원인을 규명하고 수정까지 완료.

### 주요 발견

| 발견 | 내용 |
|---|---|
| B109 — broker_daily_pnl 오염 | Cybos `CpTd6197` `today_pnl`이 포지션 보유 중 미실현 포함값을 반환 → `broker_daily_pnl` 테이블에 저장 → 손익 추이 탭 3,555,000원 (gross 총합 2,281,000원 초과) |
| 손익 추이 갱신 타이밍 버그 | `_refresh_pnl_history()`는 거래 청산 시에만 호출됨. 이후 잔고 TR이 broker_daily_pnl을 올바른 값으로 갱신해도 손익 추이 탭은 재구성 안 됨 |
| 실시간 잔고 vs HTS 차이 | CpTd6197(잔고패널) vs CpTd0723 계열(HTS) — TR 종류·수수료 처리 기준 상이. STALE 32초 상태도 원인 |
| PnL 탭 vs HTS 차이 | 엔진은 `FUTURES_COMMISSION_RATE×2` 수수료 차감 순손익, HTS는 별도 기준 |

### 수정 내용

| 파일 | 변경 |
|---|---|
| `main.py` (5101~5116) | `upsert_daily_broker_pnl(_today_str, ...)` 호출을 `self.position.status == "FLAT"` 조건 안으로 이동 — 포지션 보유 중 미실현 포함값 저장 차단 |
| `main.py` (5101~5116) | FLAT 확인 후 저장 직후 `self._refresh_pnl_history()` 호출 추가 — 잔고 TR 갱신 시 손익 추이 탭 즉시 동기화 |

### 검증 논리

- 오늘 실거래 6건 gross 합계: 45.63pt × 50,000 = 2,281,500원 → 수수료 차감 후 2,261,018원 = PnL 탭 값과 일치 ✓
- 3,555,000원은 gross를 초과하므로 trades.db에서 올 수 없음 → broker_daily_pnl 캐시 오염 확인
- FLAT 시점 저장 + 즉시 refresh로 두 패널 동기화 예상

---

## 2026-05-18 (51차 — 부분청산 Race Condition 버그 3종 수정)

**Work**: 실거래 로그에서 `[PNL] 체결진입`이 반복되고 부분청산 로그가 없는 현상을 발견. 코드 전체 분석(exit_manager, position_tracker, main.py Chejan 흐름)으로 버그 3종을 도출 및 수정. 실로그로 fix 검증 완료.

### 주요 발견

| 발견 | 내용 |
|---|---|
| B106 Race Condition | `_ts_execute_partial_exit()`가 주문 후 pending 등록 순서 — 수동청산과 반대. BlockRequest 메시지 펌프 중 Chejan이 pending=None 도착 → external fill 오탐 |
| B107 partial_done 리셋 | `apply_entry_fill()` 분할체결마다 `partial_N_done=False` 무조건 리셋 — TP 실행 후 추가 체결 오면 이중청산 위험 |
| B108 Chejan 오탐 매칭 | `order_no=""` pending에 방향 검증 없이 첫 체결이 모두 매칭 — ENTRY/EXIT 혼용 위험 |

### 수정 내용

| 파일 | 변경 |
|---|---|
| `main.py` | `_ts_execute_partial_exit()`: `_set_pending_order()` 선등록 → `_send_broker_exit_order()` → `ret≠0` 시 `_clear_pending_order()` 롤백 |
| `main.py` | `_ts_on_chejan_event_cybos_safe()`: `_dir_ok` 조건 — ENTRY pending은 동방향, EXIT_* pending은 역방향 체결만 매칭 |
| `strategy/position/position_tracker.py` | `apply_entry_fill()`: `_is_new_position` 플래그로 FLAT→진입 시에만 partial_done 리셋 |

### 검증 결과

- 09:59 LONG 4계약 분할체결 진입 (1+1+1+1, order_no=1598)
- 10:00 TP1 부분청산 1계약 @ 1156.92 → +5.43pt (+270,023원) ✅
- 10:01 TP2 부분청산 1계약 @ 1160.18 → +8.69pt (+433,023원) ✅
- 10:04 하드스톱 전량청산 2계약 @ 1154.91 → +3.42pt ✅
- WARN 로그: `[PendingOrder] set` → `[ChejanFlow] 접수` → `[PartialExitSendOrderResult] ret=0` 순서 확인 (Race Condition 해소 증거)

---

## 2026-05-17 (50차 — 5/15 거래 검토 기반 전략 핵심 수정 6종)

**Work**: 5/15 미륵이 거래 로그를 Deep 분석(openCode)으로 검토한 결과 이상점 5종이 도출됨. 5/16~5/17 커밋(40~49차)이 대시보드/Cybos 연동에 집중되어 전략 핵심 파일이 미수정 상태임을 확인 후 우선순위 순으로 6종을 일괄 구현.

### 주요 발견

| 발견 | 내용 |
|---|---|
| Hurst 미계산 (B105) | feature_builder.py에 calculate_hurst 호출 없어 전 기간 hurst=0.5 고정. Hurst 필터 완전 무효화 |
| CVD=X 진입 허용 | 5/15 09:49 CVD=X에서 Grade A 자동 진입 → -45만원. checklist 단순 카운트 구조가 원인 |
| GBM Retrain = raw_data.db | trades.db(거래기록)와 raw_data.db(피처데이터)는 별개. DB 초기화는 GBM 학습 데이터에 무영향 |
| MIN_TRAIN_BARS=5000 병목 | raw_data.db 3,432행으로 기준 미달 → Retrain 계속 실패. 3,000으로 한시적 하향 |

### 수정 내용

| 파일 | 변경 |
|---|---|
| strategy/entry/checklist.py | CORE 3개(CVD·VWAP·OFI) 하드게이트 추가 |
| main.py | EXIT stuck 타임아웃 30s→10s + 반대 포지션 즉시 force_exit |
| main.py | [SizerMatch] 로그 추가 |
| features/feature_builder.py | Hurst 실계산 연결 — 60봉 버퍼 + calculate_hurst 호출 |
| learning/batch_retrainer.py | MIN_TRAIN_BARS 5000→3000 한시적 |
| config/settings.py | CB_CONSEC_STOP_LIMIT 3→2 |

## 2026-05-16 (43李????먯씡 異붿씠 ?⑤꼸 UI 媛쒖꽑: ?뚯뒪 泥댄겕諛뺤뒪 + ?쒖떆 ?뺣━)

**Work**: `PnlHistoryPanel` (?먯씡 異붿씠 ?????곗씠???쒖떆 諛⑹떇???꾨㈃ ?뺣━?덈떎. 湲곗〈 "?ㅽ뻾 +xxx / ??+yyy" ?댁쨷 ?쒖떆瑜?泥댄겕諛뺤뒪 ?좏깮 湲곕컲 ?⑥씪 媛??쒖떆濡?援먯껜?섍퀬, ?ㅻ뜑쨌??먯꽌 遺덊븘?뷀븳 ?덉씠釉붿쓣 ?쒓굅?덈떎.

### 蹂寃??댁뿭

| ??ぉ | ?댁슜 |
|---|---|
| 泥댄겕諛뺤뒪 異붽? | ?쇰퀎쨌二쇰퀎쨌?붾퀎 ??컮 ?곗륫 肄붾꼫??"?쒕갑?? / "??갑?? QCheckBox 諛곗튂 (`Qt.TopRightCorner`) |
| 泥댄겕諛뺤뒪 ?숈옉 | ?쒕갑?λ쭔 ??exec P/L, ??갑?λ쭔 ??forward P/L, ???????⑹궛 |
| ?ㅻ뜑 ?뺣━ | `"P/L pt(?ㅽ뻾/??"` ??`"P/L pt"` ??紐⑤뱺 `(?ㅽ뻾/??` ?쒓린 ?쒓굅 |
| ? ?쒖떆 ?뺣━ | `"?ㅽ뻾 +xx / ??+yy"` ??泥댄겕諛뺤뒪 湲곗? ?⑥씪 媛?(`+xx??) |
| MDD쨌?ㅽ봽쨌?꾩쟻 ?곕룞 | `_mdd_sel`, `_sharpe_sel` ?ы띁媛 泥댄겕諛뺤뒪 ?곹깭 諛섏쁺???ш퀎??|
| ?붿빟 移대뱶 ?곕룞 | 珥??먯씡쨌理쒕? MDD???좏깮 ?뚯뒪 湲곗? ?⑥씪 媛??쒖떆 |

### ?좉퇋 硫붿꽌??
| 硫붿꽌??| ??븷 |
|---|---|
| `_sel_val(exec, fwd)` | 泥댄겕諛뺤뒪 ?곹깭濡?諛섑솚媛?寃곗젙 (exec / fwd / exec+fwd) |
| `_fmt_val(exec, fwd, ...)` | `_sel_val` 湲곕컲 ?щ㎎??|
| `_fmt_single(val, ...)` | ?대? 寃곗젙???⑥씪 媛??щ㎎??|
| `_mdd_sel(rows)` | ?좏깮 ?뚯뒪 湲곗? MDD 怨꾩궛 |
| `_sharpe_sel(grp)` | ?좏깮 ?뚯뒪 湲곗? Sharpe 怨꾩궛 |
| `_on_source_changed()` | 泥댄겕諛뺤뒪 蹂寃???4媛?鍮뚮뜑 ?ы샇異?|

### ?섏젙 ?뚯씪

- `dashboard/main_dashboard.py` ??`PnlHistoryPanel` ?대옒???꾩껜 (?ㅻ뜑 3媛? `_build()`, 鍮뚮뜑 4媛? ?좉퇋 硫붿꽌??7媛?

---

## 2026-05-16 (42李???Cybos ?붽퀬 Chejan 踰꾧렇 洹쇰낯 ?먯씤 遺꾩꽍 + 4醫??섏젙)

**Work**: ?ㅺ굅??濡쒓렇?먯꽌 諛쒓껄??`?깃툒=BROKER` / `?몃?泥닿껐(HTS/?섎룞)` ?⑦꽩怨?5/15 11:54 CB??諛쒕룞???멸낵 愿怨꾨? 肄붾뱶 ?섏??먯꽌 ?꾩쟾??異붿쟻??4媛吏 踰꾧렇瑜??섏젙?덈떎.

### 諛쒓껄??踰꾧렇 ?붿빟

| 踰꾧렇 | ?뚯씪 | 利앹긽 |
|---|---|---|
| ?붽퀬 Chejan??EXIT pending ?뚮㈇ | `main.py` `_ts_sync_from_balance_payload` | ?먮룞留ㅻℓ 泥?궛???몃?泥닿껐濡??ㅻ텇瑜?|
| `sync_from_broker` TP ?뚮옒洹?珥덇린??| `position_tracker.py` `sync_from_broker` | TP1 以묐났 諛쒕룞 ???ㅼ＜臾?諛섎났 ?꾩넚 |
| `sync_from_broker` grade ??뼱?곌린 | `position_tracker.py` `sync_from_broker` | ?좏샇 ?깃툒 A?묪ROKER ?ㅼ뿼 |
| `EmergencyExit` pending 誘몃벑濡?| `emergency_exit.py` `execute()` | CB 鍮꾩긽泥?궛 泥닿껐????긽 ?몃?泥닿껐濡?湲곕줉 |

### ?멸낵 ?ъ뒳 (5/15 ?ㅺ굅??

```
?붽퀬 Chejan ??EXIT pending ?뚮㈇ ??TP1 泥닿껐 Chejan 誘몃ℓ移????몃?泥닿껐 ?ㅻ텇瑜???remaining_fill > 0 ??갑???ъ쭊?????섎씫?μ뿉????갑???ъ???利됱떆 ?먯젅 ??record_stop_loss()
??CB???먮뒗 CB??ATR 湲됰벑) 諛쒕룞 ??emergency_exit()
??pending 誘몃벑濡??곹깭濡?鍮꾩긽泥?궛 二쇰Ц ???몃?泥닿껐(HTS/?섎룞) 湲곕줉
```

### ?섏젙 ?댁뿭

| ??ぉ | ?뚯씪 | 蹂寃?|
|---|---|---|
| Fix 1: EXIT pending 以??붽퀬 Chejan ?뚮㈇ 諛⑹? | `main.py` | `_ts_sync_from_balance_payload` ??EXIT pending 吏꾪뻾 以묒씠硫?`_clear_pending_order` 嫄대꼫? |
| Fix 2: ?숇갑??sync ??TP ?뚮옒洹?蹂댁〈 | `position_tracker.py` | `sync_from_broker` ??`same_side_sync` ????`partial_1/2/3_done` 由ъ뀑 ????|
| Fix 3: ?숇갑??sync ??湲곗〈 grade 蹂댁〈 | `position_tracker.py` | `sync_from_broker` ??`same_side_sync` + grade媛 BROKER媛 ?꾨땶 寃쎌슦 湲곗〈 grade ?좎? |
| Fix 4: EmergencyExit pending ?좊벑濡?| `emergency_exit.py` + `main.py` | `pending_registrar` 肄쒕갚 異붽?, 鍮꾩긽泥?궛 二쇰Ц ??`EXIT_FULL` pending ?깅줉 |

### CB??諛쒕룞 ???쒖떆 蹂??
```
# 媛쒖꽑 ??[10:46] 吏꾩엯 SHORT 1怨꾩빟 @ 1228.3355555533333 ?깃툒=BROKER  (횞3)
[11:55] 泥?궛 SHORT 1怨꾩빟 @ 1205.74 (?몃?泥닿껐(HTS/?섎룞))   (횞3)

# 媛쒖꽑 ??[10:46] 吏꾩엯 SHORT 3怨꾩빟 @ 1228.34 ?깃툒=A
[11:54] 泥?궛 SHORT 3怨꾩빟 @ 1205.77 (CB??鍮꾩긽泥?궛) +22.57pt
```

---

## 2026-05-16 (41李???CB??遺꾩꽍 + HORIZON_THRESHOLDS ?щ낫??+ 紐⑤땲?곕쭅쨌?댄똻 媛뺥솕)

**Work**: 5/15 CB??30遺??뺥솗??誘몃떖 2???곗냽) 諛쒕룞 ?먯씤??洹쇰낯?곸쑝濡?遺꾩꽍?섍퀬, HORIZON_THRESHOLDS瑜?KOSPI200 1200pt ?쒖옣 ?꾩떎??留욊쾶 ?щ낫?뺥뻽?? 30遺?二쇨린 threshold 紐⑤땲?곕쭅??main.py??異붽??섍퀬, ??쒕낫??CB 諛곗?쨌?뚮씪誘명꽣 以묒슂?꽷룸????몃씪?댁쫵 ?쇰꺼???곸꽭 ?댄똻??遺숈???

### ?섏젙 ?댁뿭

| ??ぉ | ?뚯씪 | 蹂寃?|
|---|---|---|
| HORIZON_THRESHOLDS ?щ낫??| `config/settings.py` | 1m:0.0002??.0005, 3m:0.0003??.0008, 5m:0.0004??.0011, 10m:0.0006??.0016, 15m:0.0008??.0022, 30m:0.0012??.0032 |
| `_threshold_monitor_tick` 移댁슫??異붽? | `main.py` | line 286, 30遺?二쇨린 ?몄텧??|
| `_log_threshold_monitor()` 硫붿꽌???좎꽕 | `main.py` | line 1213-1255, Static쨌ATR dynamic 鍮꾧탳 濡쒓렇, ?덉젙??媛먯? ??ATR ?꾪솚 ?쒖븞 |
| GBM ?ы븰???꾨즺 ??紐⑤땲???몄텧 | `main.py` | line 1208-1210, `_on_gbm_retrain_done()` ?덉뿉??`_log_threshold_monitor(atr, price)` |
| ?뚯씠?꾨씪??30遺?二쇨린 紐⑤땲???몄텧 | `main.py` | line 1583-1585, `_threshold_monitor_tick % 30 == 0` 議곌굔 |
| `_CB_TIP` ?щ옓 ?뚮┝ ?뱀뀡 異붽? | `dashboard/main_dashboard.py` | ???щ옓 ?뚮┝ ?댁슜 ?뱀뀡 (?ㅽ겕諛뺤뒪 + 5媛??몃━嫄???묓몴), 湲곗〈 ?™넂???щ쾲??|
| `param_title` ?댄똻 ?쇱쿂 ?덈룄???뚯씠釉?| `dashboard/main_dashboard.py` | line 890-991, ???쇱쿂蹂??대? ?덈룄???뚯씠釉?異붽? (CORE 泥?줉/?좏깮 ?⑹깋/?몃? ?뚯깋) |
| `_HZ_TIP` ?좉퇋 ?뺤쓽 + `hz_title` ?곌껐 | `dashboard/main_dashboard.py` | line 614-710, 硫???몃씪?댁쫵 ?덉륫 6?뱀뀡 ?댄똻 (?앹꽦쨌寃利씲톞hreshold쨌acc쨌紐⑤땲?곕쭅) |

### ?듭떖 ?ㅺ퀎 ?먯튃 (41李?

- **HORIZON_THRESHOLDS ?щ낫??湲곗?**: 2026-05 ?쇱쨷 怨좎???~96pt 湲곕컲 ?_1min??.47pt, threshold ??0.4~0.5? ??FLAT 29~37% 紐⑺몴 (3???쒕뜡 33%???좎쓽誘?洹쇱젒)
- **?⑥씪 吏꾩엯???꾪뙆**: `config/settings.py` 1怨??섏젙 ??`batch_retrainer.py`쨌`prediction_buffer.py`쨌`target_builder.py` ?먮룞 ?꾪뙆. ?곸슜 ??GBM ?ы븰???꾩닔
- **紐⑤땲?곕쭅 援ъ“**: 30遺?二쇨린 + GBM ?ы븰???꾨즺 ??`_log_threshold_monitor()` ??紐⑤뜽 AI??뿉 stable_count 湲곕컲 ?덉젙/珥덇낵 ?먯젙 + ATR ?숈쟻 ?꾪솚 ?쒖븞
- **ATR ?숈쟻 諛⑹떇**: ?④린???뺤쟻 ?щ낫?뺤쑝濡?泥섎━. ?덉젙???뺤씤 ??`threshold = max(base, atr/price 횞 mult)` ?숈쟻 諛⑹떇?쇰줈 ?꾪솚 ?덉젙
- **threshold ??븷 紐낇솗??*: ??쒕낫??移대뱶 %??GBM+SGD 異쒕젰媛믪씠硫?threshold 誘몄궗?? threshold???숈뒿 ?쇰꺼 ?앹꽦쨌寃利?梨꾩젏 湲곗?留?
### CB??洹쇰낯 ?먯씤 (遺꾩꽍 ?꾨즺, 肄붾뱶 ?섏젙)

- **warn_count 援ъ“??痍⑥빟**: 30遺??대룞?됯퇏?먯꽌 ??踰?35% 誘몃떖 ???ㅼ쓬 遺꾨룄 嫄곗쓽 ?숈씪 ?섏? ??寃쎄퀬 1遺???利됱떆 HALT
- **threshold ?덈Т ??쓬**: 1200pt ?쒖옣?먯꽌 湲곗〈 threshold(30m=0.12%)??FLAT 24%留????ъ떎??2??臾몄젣 ???쒕뜡 湲곗???50%??洹쇱젒 ??CB??35% 湲곗? 臾댁쓽誘?- **?섏젙**: HORIZON_THRESHOLDS ?꾩껜 ??1.6횞 ?곹뼢 ??FLAT 29~37%濡?蹂듭썝 ??CB??35% 湲곗????ㅼ쭏???섎?瑜?媛吏?
### 湲곕룞 ???덉긽 ?뺤씤 濡쒓렇 (41李?

```
?ㅼ쓬??08:45 湲곕룞 ??GBM warmup retrain ?먮룞 諛쒕룞
??_log_threshold_monitor() ?몄텧 ??"紐⑤뜽 AI" ??뿉 濡쒓렇:
  [THRESH] 30m threshold=0.0032 | ATR_dynamic=X.XXXX | static??(or ?잸TR?꾪솚沅뚯옣)
  stable_count=N/6 ???덉젙: ???꾨? ?뺤쟻 ??/ 珥덇낵: ??ATR ?숈쟻 ?꾪솚 沅뚯옣
```

---

## 2026-05-16 (40李????μ쟾 ?쒕룞 ?먮쫫 ?먭? + ?щ옓 ?뚮┝ + UI 泥댄겕諛뺤뒪)

**Work**: 08:45 ?먮룞 湲곕룞 ??09:00 泥????섏떊源뚯????꾩껜 ?먮쫫??媛먯궗?섍퀬 ?댁긽??6醫낆쓣 ?섏젙?덈떎. ?щ옓 ?뚮┝ ??援ш컙 異붽?, ??쒕낫???щ옓 On/Off 泥댄겕諛뺤뒪 ?좎꽕, GBM ?ы븰???곕が ?ㅻ젅???꾪솚, BAT ?뚯씪 ?몄뀡 ?댁쨷 ?뺤씤???꾨즺?덈떎.

### ?섏젙 ?댁뿭

| ??ぉ | ?뚯씪 | 蹂寃?|
|---|---|---|
| 08:45??8:55 pre_market_setup ??대컢 ?듯빀 | `main.py` | ????대㉧ 釉붾줉??08:55 ?⑥씪 釉붾줉?쇰줈 ?듯빀. ?ㅼ떆媛?援щ룆 ?ъ쟾 ?쒖옉(`_rd.start`) ?ы븿 |
| 08:55 ?ㅻ깄???뚮컢??異붽? | `main.py`, `collection/cybos/realtime_data.py` | `pre_market_setup()` ?앹뿉 `_prime_from_snapshot()` ?몄텧. `start()` 吏꾩엯 ??`_last_price > 0`?대㈃ 以묐났 BlockRequest skip |
| GBM ?ы븰?????곕が ?ㅻ젅??| `main.py` | `_on_gbm_retrain_done()` 肄쒕갚 異붽?. `threading.Thread(daemon=True)` + `QTimer.singleShot(0, callback)`?쇰줈 硫붿씤 ?ㅻ젅??釉붾줈???쒓굅 |
| 08:58 broker sync ?좎떎??| `main.py` | `_scheduler_tick`??08:58~09:00 援ш컙 broker sync pre-execution. `_pre_sync_attempted` ?뚮옒洹몃줈 以묐났 諛⑹? |
| `start_mireuk.bat` ?몄뀡 ?댁쨷 ?뺤씤 | `start_mireuk.bat` | preflight ??3s ?湲?+ Cybos ?몄뀡 ?ы솗?? ?딆뼱議뚯쑝硫?`EXIT /B 1` |
| CLAUDE.md ??꾩뒪?ы봽 援먯젙 | `CLAUDE.md` | `08:45` ??`08:55 留ㅽ겕濡??섏쭛 ???덉쭚 ?먮떒 + ?ㅼ떆媛?援щ룆 ?ъ쟾 ?쒖옉` |
| ?щ옓 ?뚮┝ ??援ш컙 異붽? | `utils/notify.py` | `_SLACK_ENABLED` ?뚮옒洹? `set_slack_enabled()`, `is_slack_enabled()`, `notify_startup`, `notify_premarket_ready`, `notify_first_tick`, `notify_broker_sync_blocked`, `notify_connection_lost`, `notify_pipeline_delayed` |
| ?щ옓 ?뚮┝ ?곕룞 | `main.py` | 湲곕룞 ?깃났/?ㅽ뙣, ?μ쟾 以鍮? 泥??? broker sync 誘멸?利? ?곌껐 ?딄?, ?뚯씠?꾨씪??90s 吏??媛곴컖 ?щ옓 諛쒖넚 |
| ??쒕낫???щ옓 On/Off 泥댄겕諛뺤뒪 | `dashboard/main_dashboard.py` | `chk_slack` QCheckBox 異붽?. `res_box`???쇱そ ?뺣젹. `ui_prefs.json` ??Β룸났??|
| `run()` 泥댄겕諛뺤뒪 ??`_SLACK_ENABLED` ?곕룞 | `main.py` | `stateChanged` ?쒓렇?먮줈 `set_slack_enabled` + `_save_ui_prefs` ?곕룞 |

### ?듭떖 ?ㅺ퀎 ?먯튃 (40李?

- **08:55 ?⑥씪 吏꾩엯??*: ?꾨━留덉폆 以鍮?留ㅽ겕濡쑣룸젅吏?? ?ㅼ떆媛?援щ룆 ?ъ쟾 ?쒖옉??08:55 ?⑥씪 釉붾줉?쇰줈 ?듯빀 ??08:45~09:00 援ш컙 濡쒖쭅 媛꾩냼??- **?ㅻ깄???좎썙諛?*: 08:55 `pre_market_setup()` 吏곹썑 `_prime_from_snapshot()` ??09:00 `start()` 吏꾩엯 ??BlockRequest ?놁씠 利됱떆 tick ?섏떊 媛??- **GBM 鍮꾩감??*: ?ы븰?듭쓣 ?곕が ?ㅻ젅?쒕줈 遺꾨━ ??09:00 媛??ㅽ뵂 援ш컙 硫붿씤 ?ㅻ젅???먯쑀 諛⑹?
- **broker sync ?좎떎??*: 08:58??誘몃━ sync ??09:00~09:05 GAP_OPEN 援ш컙?먯꽌 block_new_entries=False ?뺣낫
- **?щ옓 ?뚮┝ On/Off**: `_SLACK_ENABLED` ?꾩뿭 ?뚮옒洹?+ 泥댄겕諛뺤뒪 ???μ쨷 ?뚮┝ ??깂 ?놁씠 ?꾩슂 ?쒕쭔 ?쒖꽦??媛??
### 湲곕룞 ???덉긽 ?щ옓 ?먮쫫

```
08:55  notify_premarket_ready  ??"?μ쟾 以鍮??꾨즺 ??| ?덉쭚 / 醫낅ぉ"
09:00  notify_first_tick       ??"泥?遺꾨큺 ?섏떊 ??(09:01) O=... H=... L=... C=..."
(?댁긽 ?놁쑝硫??댄썑 嫄곕옒 ?쒖옉)
?ㅽ뙣 ?? notify_broker_sync_blocked / notify_connection_lost / notify_pipeline_delayed
```

---

## 2026-05-15 (39李????좊Ъ 濡ㅼ삤踰??먮룞???꾨㈃ 媛뺥솕)

**Work**: ?쒖옣援щ텇 肄ㅻ낫?먯꽌 ?좏깮??醫낅ぉ肄붾뱶媛 留뚭린?먯쓣 ???먮룞?쇰줈 洹쇱썡/洹쇱＜臾쇰줈 ?꾪솚?섎뒗 濡쒖쭅???쇰컲?좊Ъ쨌誘몃땲?좊Ъ 紐⑤몢??嫄몄퀜 ?몄떖?섍쾶 ?꾩꽦?덈떎.

### ?섏젙 ?댁뿭

| ??ぉ | ?뚯씪 | 蹂寃?|
|---|---|---|
| `_build_market_symbols()` ?좎꽕 | `dashboard/main_dashboard.py` | ?섎뱶肄붾뵫 `_MARKET_SYMBOLS` ??湲곕룞 ?좎쭨 湲곗? ?숈쟻 怨꾩궛?쇰줈 援먯껜. `_nth_thursday`, `_next_valid_contracts`, `_futures_code8` ?ы띁 異붽? |
| `set_selected_symbol()` ?좎꽕 | `dashboard/main_dashboard.py` | 釉뚮줈而??꾨줈釉???肄ㅻ낫 ?먮룞 ?숆린?? 肄ㅻ낫???녿뒗 肄붾뱶???숈쟻 ?쎌엯. `MireukDashboard` + `DashboardAdapter` ?묒そ 異붽? |
| `get_nearest_normal_futures_code()` ?좎꽕 | `collection/cybos/api_connector.py` | ?쇰컲?좊Ъ(A01xxx) FutureMst BlockRequest ?꾨줈釉? `price > 0` 議곌굔?쇰줈 留뚭린 肄붾뱶 ?먮룞 skip |
| `_resolve_trade_code()` ?쇰컲?좊Ъ ?꾨줈釉?異붽? | `strategy/runtime/broker_runtime_service.py` | ?쇰컲?좊Ъ??FutureMst ?꾨줈釉뚮줈 洹쇱썡臾??뺤젙 + `[CodeRoll]` 寃쎄퀬 + `set_selected_symbol` ?몄텧 |
| `check_rollover()` ?좎꽕 | `strategy/runtime/broker_runtime_service.py` | ?μ쨷 濡ㅼ삤踰?媛먯떆. WARNING 濡쒓렇 + UI 媛깆떊. ?ш뎄?낆? ?ш린?숈뿉 ?꾩엫 |
| `_scheduler_tick()` 濡ㅼ삤踰?媛먯떆 二쇨린 異붽? | `main.py` | 60 tick(30遺?留덈떎 `check_rollover()` ?몄텧. `_rollover_detected` ?뚮옒洹몃줈 諛섎났 ?뚮┝ ?듭젣. ???쒖옉 ??珥덇린??|

### ?듭떖 ?ㅺ퀎 ?먯튃 (39李?

- **?숈쟻 ?щ낵 紐⑸줉**: `_MARKET_SYMBOLS`??湲곕룞 ?쒖젏 ?좎쭨瑜?湲곗??쇰줈 ?앹꽦 ???뚯뒪肄붾뱶 ?섏젙 ?놁씠 ??遺꾧린 濡ㅼ삤踰??먮룞 諛섏쁺
- **?쇰컲?좊Ъ ?듯빀**: 湲곗〈 誘몃땲?좊Ъ留??꾨줈釉뚰븯??援ъ“瑜??쇰컲?좊Ъ(遺꾧린臾?源뚯? ?뺤옣. ????FutureMst `price > 0` 寃利앹쑝濡??숈씪 諛⑹떇 ?곸슜
- **UI ?숆린??*: ?꾨줈釉?寃곌낵濡?肄ㅻ낫瑜?利됱떆 ?낅뜲?댄듃 ???댁쁺?먭? ?ㅼ젣 ?ъ슜 肄붾뱶瑜?UI?먯꽌 ?뺤씤 媛??- **?μ쨷 媛먯떆**: ?ш뎄???놁씠 濡쒓렇+UI留?媛깆떊 ???대┛ ?ъ???由ъ뒪???놁쓬

### 湲곕룞 ???덉긽 濡쒓렇 ?먮쫫 (濡ㅼ삤踰?諛쒖깮 ?ㅼ쓬??

```
[NormalProbe] 洹쇱썡臾??뺤젙 code=A0169 price=327.45  ???쇰컲?좊Ъ 洹쇱썡臾?[CodeRoll] ?쇰컲?좊Ъ 肄붾뱶 援먯껜: UI=A0166 ??洹쇱썡臾?A0169 (留뚭린 濡ㅼ삤踰?
[MiniProbe]  洹쇱썡臾??뺤젙 code=A0567 price=327.40   ??誘몃땲?좊Ъ 洹쇱썡臾?[CodeRoll] 誘몃땲?좊Ъ 肄붾뱶 援먯껜: UI=A0566 ??洹쇱썡臾?A0567 (留뚭린 濡ㅼ삤踰?
```

---

## 2026-05-15 (38李????μ쨷 ?먭?: BlockRequest ?곕뱶???섏젙 + ?좊Ъ 濡ㅼ삤踰?泥섎━)

**Work**: 09:18 湲곕룞 濡쒓렇?먯꽌 ??媛吏 移섎챸 踰꾧렇瑜??뺤씤?섍퀬 ?섏젙?덈떎.  
??`_run_block_request` COM STA ?곕뱶?쎌쑝濡?CpTd0723/FutureMst媛 ??긽 30珥???꾩븘????block_new_entries=True 怨좎갑  
??A0565(5?붾Ъ, 2026-05-14 留뚭린)瑜?洹몃?濡?援щ룆 ?????곗씠??0嫄? ?뚯씠?꾨씪??誘몃룞??
### ?섏젙 ?댁뿭

| ??ぉ | ?뚯씪 | 蹂寃?|
|---|---|---|
| FIX-1: BlockRequest 硫붿떆吏 ?뚰븨 猷⑦봽 | `collection/cybos/api_connector.py` | `done.wait(30)` ??`done.wait(0.01)` + `PumpWaitingMessages()` 猷⑦봽濡?援먯껜 |
| FIX-2: `get_nearest_mini_futures_code` ?ъ옉??| `collection/cybos/api_connector.py` | 吏곸젒 BlockRequest ??`_run_block_request` ?ъ슜, `price > 0` 議곌굔?쇰줈 留뚭린 肄붾뱶 ?먮룞 skip |
| FIX-3: `_resolve_trade_code` ??긽 洹쇱썡臾??꾨줈釉?| `strategy/runtime/broker_runtime_service.py` | UI ??κ컪 臾닿??섍쾶 ??긽 ?꾨줈釉? 濡ㅼ삤踰???`[CodeRoll]` 寃쎄퀬 濡쒓렇 |
| FIX-4: `_scheduler_tick` broker sync ?ъ떆??| `main.py` | startup sync ?ㅽ뙣 ??3遺?媛꾧꺽 ?μ쨷 ?먮룞 ?ъ떆??|
| 媛먯궗臾몄꽌 ?낅뜲?댄듃 | `dev_memory/audit/GPT-5_3-Codex_260515_poject_Audit.md` | 09:18 ?μ쨷 ?먭? ?뱀뀡 異붽? (BUG-1/2, FIX-1~4, DoD 泥댄겕) |

### 踰꾧렇 ?듭떖 ?먯씤

**BUG-1 ??BlockRequest ?곕뱶??*:  
`_run_block_request`媛 諛깃렇?쇱슫???ㅻ젅?쒖뿉??BlockRequest瑜??ㅽ뻾?섎㈃??硫붿씤 ?ㅻ젅?쒕뒗 `done.wait(30)`?쇰줈 ?꾩쟾 李⑤떒?쒕떎. Cybos??BlockRequest???몄텧 ?ㅻ젅?쒖쓽 Windows 硫붿떆吏 ?먮줈 ?묐떟??蹂대궡?붾뜲, 諛깃렇?쇱슫???ㅻ젅?쒖뿉??硫붿떆吏 ?뚰봽媛 ?녾퀬 硫붿씤 ?ㅻ젅?쒕룄 留됲? ?덉뼱 ?곴뎄 ?곕뱶????30珥???꾩븘??  
`_probe_investor_tr()`媛 硫붿씤 ?ㅻ젅??吏곸젒 ?몄텧濡??뺤긽 ?숈옉?섎뒗 寃껋씠 鍮꾧탳 洹쇨굅.

**BUG-2 ??留뚭린 肄붾뱶 援щ룆**:  
2026-05-14(2李?紐⑹슂????A0565 留뚭린. ?ㅼ쓬??2026-05-15) 湲곕룞 ??UI????λ맂 A0565媛 洹몃?濡??ъ슜?쒕떎. `_resolve_trade_code`??`ui_code`媛 鍮꾩뼱 ?덉? ?딆쑝硫?`get_nearest_mini_futures_code()`瑜??몄텧?섏? ?딆븘 留뚭린 肄붾뱶瑜?寃利앺븯吏 ?딅뒗?? Cybos??留뚭린 肄붾뱶??tick???꾩넚?섏? ?딆븘 ?곗씠??0嫄?

### ?꾩옱 ?곹깭

- BlockRequest ?곕뱶???섏젙?????ㅼ쓬 湲곕룞?먯꽌 CpTd0723/FutureMst媛 ~1珥????꾨즺 ?덉긽
- 濡ㅼ삤踰?泥섎━ ?섏젙????A0565 skip ??A0566 ?먮룞 ?좏깮
- broker sync ?ъ떆??異붽?????startup ?ㅽ뙣 ??3遺????먮룞 ?ъ떆??
### ?몄뀡 留덇컧 硫붾え

- ?ㅼ쓬 湲곕룞 ??`[MiniProbe] 洹쇱썡臾??뺤젙 code=A0566`, `[BrokerSync] verified=True`, `[CybosRT-TICK] #1` ??濡쒓렇瑜??쒖꽌?濡??뺤씤?댁빞 ??- 媛쒖꽑 ?ы빆???ㅼ젣濡??숈옉?섎뒗吏 ?μ쨷 泥?湲곕룞?먯꽌 寃利??꾩슂

---

## 2026-05-15 (37李????댁쁺 ?ъ뒪 以묒븰 ?⑤꼸 異붽?)

**Work**: `dashboard/main_dashboard.py`??以묒븰 ?⑤꼸(mid_tabs)??`?뺧툘 ?댁쁺 ?ъ뒪` ??쓣 ?ㅼ젣 異붽??덈떎. 湲곗〈?먮뒗 ?섎떒 濡쒓렇 ?⑤꼸??6踰???뿉留??덈뜕 ?ъ뒪 酉곕? ?댁쁺?먭? 以묒븰 ?곸뿭?먯꽌??諛붾줈 蹂????덇쾶 ??꼈??

### ?섏젙 ?댁뿭

| ??ぉ | ?뚯씪 | 蹂寃?|
|---|---|---|
| 以묒븰 ?ъ뒪 ?⑤꼸 異붽? | `dashboard/main_dashboard.py` | `HealthPanel` ?좎꽕, `mid_tabs`??`?뺧툘 ?댁쁺 ?ъ뒪` ???쎌엯 |
| ?고????ъ뒪 ?숆린??| `dashboard/main_dashboard.py` | `update_runtime_health()`?먯꽌 濡쒓렇 ?⑤꼸 + 以묒븰 ?ъ뒪 ?⑤꼸 ?숈떆 媛깆떊 |

### ?꾩옱 ?곹깭

- 以묒븰 ?⑤꼸?먯꽌 API 吏??/ ?쇱쿂 ?덉쭏 / 罹먯떆 ?섏씠 / ?덉쇅 諛?꾨? 諛붾줈 ?뺤씤?????덈떎
- ?섎떒 濡쒓렇 ?⑤꼸??`6 ?댁쁺 ?ъ뒪`???붾젅硫뷀듃由?濡쒓렇?? 以묒븰 `?뺧툘 ?댁쁺 ?ъ뒪`???댁쁺?먭? 蹂대뒗 ?붿빟 酉곕줈 ??븷??遺꾨━?덈떎
- 以묒븰 ?ъ뒪 ?⑤꼸??`Health Score`???꾩쭅 ?꾩떆 ?낅젰媛믪쑝濡??곌껐?섏뼱 ?덉뼱, 李⑦썑 ?ㅼ젣 ?곗떇 ?곌껐???꾩슂?섎떎

### ?몄뀡 留덇컧 硫붾え

- ?대쾲 ?몄뀡???꾨씫遺꾩? ?쒗뿬????쓣 留뚮뱾?덉?留?以묒븰 ?⑤꼸???ｌ? ?딆? 寃꺿앹씠?덇퀬, ?꾩옱???닿껐?먮떎
- ?ㅼ쓬 ?몄뀡?먯꽌 ?ㅼ젣 `Health Score` 怨꾩궛 濡쒖쭅???곗씠??湲곕컲?쇰줈 ?곌껐?섎㈃ ?꾩꽦?꾧? ?щ씪媛꾨떎

## 2026-05-15 (36李???Cybos ?먮룞 濡쒓렇??紐⑥쓽?ъ옄 ?좏깮 李??먯? 踰꾧렇 ?섏젙)

**Work**: `scripts/cybos_autologin.py`??紐⑥쓽?ъ옄 ?좏깮 李??먯? ?ㅽ뙣(`candidates=[]`) 踰꾧렇瑜??섏젙?덈떎. "紐⑥쓽?ъ옄 ?좏깮" ?ㅼ씠?쇰줈洹멸? Cybos 硫붿씤 ?꾨젅?꾩쓽 ?먯떇 李쎌쑝濡??앹꽦?섎뒗 寃쎌슦 `EnumWindows`/`FindWindow` 紐⑤몢 ?먯??섏? 紐삵븯??洹쇰낯 ?먯씤???닿껐?덈떎. 怨듭??ы빆 ?앹뾽 泥섎━ ?⑥닔???좎꽕?덈떎.

### ?섏젙 ?댁뿭

| ??ぉ | ?뚯씪 | 蹂寃?|
|---|---|---|
| `_find_mock_dialog_hwnd()` ?좎꽕 | `scripts/cybos_autologin.py` | 1李?FindWindow ??2李?EnumWindows ??3李?#32770 ?대옒????4李?`EnumChildWindows` ?꾩닔 ?먯깋(踰꾪듉 諛쒓껄 ??`GetParent`濡??ㅼ씠?쇰줈洹?蹂듭썝) |
| min_wait 以?利됱떆 ?먯? | `scripts/cybos_autologin.py` | 20珥?留밸ぉ???湲???留ㅼ큹 ?먯?, 媛먯? 利됱떆 ?대┃?쇰줈 媛쒖꽑 |
| `_click_mock_access_in_window()` ?좎꽕 | `scripts/cybos_autologin.py` | 踰꾪듉 ?먯?/?대┃ 濡쒖쭅 遺꾨━. ?뺥솗 ?띿뒪????遺遺??띿뒪????媛???꾨옒 踰꾪듉 ??Enter ?쒖꽌 fallback |
| `_close_dialog_window()` ?좎꽕 | `scripts/cybos_autologin.py` | ?リ린/?뺤씤 BM_CLICK, ?놁쑝硫?WM_CLOSE |
| `_dismiss_notice_popups(timeout=10)` ?좎꽕 | `scripts/cybos_autologin.py` | 紐⑥쓽?ъ옄 ?묒냽 吏곹썑 怨듭??ы빆 ?앹뾽 ?먯? + ?リ린 (FindWindow + EnumWindows ?댁쨷?? |
| 4李??먯깋 議곌굔 ?뺣???| `scripts/cybos_autologin.py` | ACCESS_KW ?⑥닚 OR ??"紐⑥쓽?ъ옄" AND "?묒냽" ?숈떆 議곌굔?쇰줈 ?ㅽ깘 諛⑹?. top-level 李쎌씠 ?꾨땶 踰꾪듉 吏곸젒 遺紐??ㅼ씠?쇰줈洹?瑜?諛섑솚?섎룄濡??섏젙 |
| 濡쒓렇???먮쫫 臾몄꽌??| `docs/CYBOS_AUTOLOGIN_FLOW.md` | ?꾩껜 ?먮쫫 ?ㅼ씠?닿렇??+ ?④퀎蹂??곸꽭 + ?ㅼ젙 ?곸닔 + ?ㅻ쪟 ??????묒꽦 |

### 踰꾧렇 ?듭떖 ?먯씤

`EnumWindows`???곗뒪?ы넲 吏곴퀎 ?먯떇(top-level)留??닿굅?쒕떎. Cybos Plus媛 "紐⑥쓽?ъ옄 ?좏깮" ?ㅼ씠?쇰줈洹몃? 硫붿씤 ?꾨젅?꾩쓽 ?먯떇 李?`CreateWindowEx(parent=frame_hwnd)`)?쇰줈 ?앹꽦?섎㈃ `EnumWindows`? `FindWindow` 紐⑤몢 ?먯????ㅽ뙣?쒕떎. 4李??먯깋(?꾩껜 李쎌쓽 `EnumChildWindows` + 踰꾪듉 ?띿뒪??寃??+ `GetParent`)????耳?댁뒪瑜?而ㅻ쾭?쒕떎.

### ?몄뀡 留덇컧 硫붾え

- 肄붾뱶 ?섏젙 ?꾨즺, ?ㅼ젣 ?ㅽ뻾?쇰줈 4李??먯깋 吏꾩엯 ?щ? ?뺤씤 ?꾩슂
- 怨듭??ы빆 ?앹뾽 ?쒕ぉ??"怨듭??ы빆" ???ㅻⅨ ?⑦꽩?대㈃ `NOTICE_KEYWORDS` ?곸닔 ?뺤옣 ?꾩슂

---

## 2026-05-15 (35李????댁쁺 ?ъ뒪 怨좊룄??+ ?ъ쟾?먭? + 媛먯궗臾몄꽌 諛섏쁺)

**Work**: Day10-2/Day11 ?꾩냽 ?붽뎄?ы빆(Degraded auto/manual ?뺤콉 遺꾨━, ?ъ뒪 3?쇱씤 ?ㅽ뙆?щ씪?? ?ㅼ젙 ?ル━濡쒕뱶)??援ы쁽?덇퀬, 寃利??섎꽕???ㅽ뻾 諛??μ떆?????ъ쟾?먭? 寃곌낵瑜?媛먯궗臾몄꽌 ##10??諛섏쁺?덈떎.

### ?섏젙 ?댁뿭

| ??ぉ | ?뚯씪 | 蹂寃?|
|---|---|---|
| Degraded ?뺤콉 遺꾨━ | `config/settings.py`, `main.py` | `HEALTH_DEGRADED_BLOCK_AUTO_ENTRY`, `HEALTH_DEGRADED_BLOCK_MANUAL_ENTRY` 異붽?. ?먮룞/?섎룞 吏꾩엯 李⑤떒 遺꾨━ |
| ?ㅼ젙 ?ル━濡쒕뱶 | `config/settings.py`, `main.py` | `HEALTH_POLICY_HOT_RELOAD_ENABLED`, `HEALTH_POLICY_HOT_RELOAD_INTERVAL_SEC` 異붽?. `settings.py` mtime 媛먯떆 + `importlib.reload` 諛섏쁺 |
| ?ъ뒪 ??3?쇱씤 ?몃젋??| `dashboard/main_dashboard.py` | Health Score + 吏??+ ?덉쭏 ?ㅽ뙆?щ씪???숈떆 ?쒖떆, ?고???threshold 二쇱엯 吏??|
| 寃利??섎꽕??| `scripts/validate_health_policy_hotreload.py` | ?ル━濡쒕뱶 濡쒓렇/auto-manual 李⑤떒/45????45遺? ?쒕??덉씠??寃利??ㅽ겕由쏀듃 異붽? |
| 媛먯궗臾몄꽌 泥댄겕由ъ뒪???뺤옣 | `dev_memory/audit/GPT-5_3-Codex_260515_poject_Audit.md` | ##10 ?섎（ ?댁슜 寃利?泥댄겕由ъ뒪??異붽? + 07:38 ?ъ쟾?먭? 寃곌낵 諛섏쁺 |

### 寃利?寃곌낵

- `scripts/validate_health_policy_hotreload.py` ?ㅽ뻾 寃곌낵: **PASS**
  - `hotreload_log_count: 1`
  - auto/manual 李⑤떒 遺꾨━ ?숈옉 ?뺤씤
  - 45???쒕??덉씠?섏뿉??auto/manual 李⑤떒 移댁슫??媛곴컖 諛쒖깮
- ?μ떆?????ъ쟾?먭? 濡쒓렇 諛섏쁺:
  - startup sync `verified=False`, `block_new_entries=True`
  - Capability ?쇰? 誘멸?利??곹깭 ?뺤씤

### ?몄뀡 留덇컧 硫붾え

- 肄붾뱶/?뺤쟻 吏꾨떒 湲곗? ?좉퇋 ?ㅻ쪟???뺤씤?섏? ?딆쓬
- ?ъ쟾?먭? 湲곗? ?꾩쭅 ?섎룞 UI ?뺤씤 ??ぉ(?ъ뒪 ??吏꾩엯 媛??? 誘몄껜???곹깭濡??좎?

## 2026-05-14 (34李???吏꾩엯愿由????쒓컙? 媛?대뱶 UI 媛뺥솕 + 沅뚯옣 ?깃툒/?ㅻ쾭?쇱씠??諛곗?)

**Work**: `dashboard/main_dashboard.py`??吏꾩엯愿由???쓣 ?쒓컙? 湲곕컲 ?댁슜 媛?대뱶 ?⑤꼸濡??뺤옣?덈떎. ?꾩옱 zone 踰붿쐞, 理쒖냼 ?좊ː?? ?ъ씠利?諛곗쑉, 吏꾩엯 ?덉슜 ?щ?瑜??ㅼ떆媛꾩쑝濡??몄텧?섍퀬, 沅뚯옣 ?깃툒 踰꾪듉 媛뺤“? 留뚭린??FOMC ?ㅻ쾭?쇱씠??諛곗???異붽??덈떎.

### ?섏젙 ?댁뿭

| ??ぉ | ?뚯씪 | 蹂寃?|
|---|---|---|
| ?쒓컙? ?ㅻ챸以??ㅼ떆媛꾪솕 | `dashboard/main_dashboard.py` | KST 湲곗? ?꾩옱 `zone`, ?쒓컙 踰붿쐞, `conf??, `size횞`, `吏꾩엯?덉슜/?좉퇋吏꾩엯湲덉?`瑜?30珥?二쇨린濡?媛깆떊 |
| ?쒓컙? 移?UI 異붽? | `dashboard/main_dashboard.py` | `GAP_OPEN`~`EXIT_ONLY` 6媛?zone 踰꾪듉 移?異붽?, ?꾩옱 zone ?됱긽 媛뺤“ |
| 沅뚯옣 ?깃툒 踰꾪듉 ?곕룞 | `dashboard/main_dashboard.py` | ?꾩옱 zone??`size_mult`瑜?`ENTRY_GRADE`? 留ㅽ븨??A/B/C 吏꾩엯 踰꾪듉??`沅뚯옣` ?쒖떆, ?ъ슜???섎룞 ?좏깮? `?좏깮` ?쒖떆濡?蹂꾨룄 ?좎? |
| 留뚭린??FOMC ?ㅻ쾭?쇱씠??諛곗? | `dashboard/main_dashboard.py` | `TimeStrategyRouter.apply_expiry_override()` / `apply_fomc_override()`瑜?UI ?쒖떆 寃쎈줈???곌껐??`留뚭린???곸슜以?, `留뚭린 ?꾩씪 ?곸슜以?, `FOMC ?곸슜以? 諛곗? ?몄텧 |
| ?몄뀡 臾몄꽌 ?뺣━ | `dev_memory/*.md` | ?ㅻ뒛 UI 媛뺥솕 ?묒뾽 湲곗??쇰줈 ?몄뀡 ?몃뱶?ㅽ봽 媛깆떊 |

### ?ㅺ퀎/?숈옉 ?붿빟

- ?ㅻ챸以꾩? ?뺤쟻 臾멸뎄媛 ?꾨땲??`TimeStrategyRouter` 寃곌낵瑜?吏곸젒 ?쎈뒗??- ?쒓컙? 移⑹뿉??`09:00-09:05` 媛숈? 踰붿쐞瑜??④퍡 ?쒖떆???댁쁺?먭? 利됱떆 援ш컙???앸퀎?????덈떎
- 沅뚯옣 ?깃툒? zone 湲곕컲 `size_mult`瑜?媛??媛源뚯슫 `ENTRY_GRADE[A/B/C].size_mult`? 留ㅽ븨?쒕떎
- 沅뚯옣 ?곹깭? ?섎룞 ?좏깮 ?곹깭???숈떆??蹂댁씠寃??? ?댁쁺?먭? ?꾩옱 ?섎룞 ?ㅻ쾭?쇱씠?쒕? ?덈뒗吏 ?쒕늿??援щ텇?????덈떎

### 寃利??곹깭

- `dashboard/main_dashboard.py` ?뺤쟻 遺꾩꽍 ?ㅻ쪟 ?놁쓬
- ?ㅼ젣 PyQt ?고????붾㈃ ?뺤씤? ?꾩쭅 誘몄떎??- `data/session_state.json` 蹂寃쎌? ?고???移댁슫??利앷????곕Ⅸ ?먮룞 媛깆떊?쇰줈 蹂댁씠硫? ?대쾲 ?몄뀡 而ㅻ컠 ??곸뿉???ы븿?섏? ?딆쓬

## 2026-05-14 (33李???Cybos ?μ쇅 startup crash ?꾪솕 + ?몄뀡 留덇컧 ?뺣━)

**Work**: `2026-05-14 20:26` KST ?ш린??濡쒓렇 湲곗??쇰줈 Cybos ?μ쇅 startup crash瑜?異붿쟻?섍퀬, ?μ쇅 ?ㅼ떆媛?援щ룆 寃쎈줈瑜?1李?李⑤떒?덈떎. ?몄뀡 醫낅즺 ??`SESSION_LOG`, `CURRENT_STATE`, `NEXT_TODO`, `DECISION_LOG`???④퍡 ?뺣━?덈떎.

### ?섏젙 ?댁뿭

| ??ぉ | ?뚯씪 | 蹂寃?|
|---|---|---|
| ?μ쇅 ?ㅼ떆媛?援щ룆 李⑤떒 | `main.py` | `connect_broker()`?먯꽌 `is_market_open()` ?뺤씤 ???μ쇅?먮뒗 `RealtimeData.start()`? ?섍툒 `QTimer` ?쒖옉??蹂대쪟. ?μ쇅 ?湲?紐⑤뱶 濡쒓렇 異붽? |
| 留ㅽ겕濡?fetch ?몄씠利??꾪솕 | `collection/macro/macro_fetcher.py` | yfinance ?ㅼ쨷 ?ㅼ슫濡쒕뱶瑜?`threads=False`濡?怨좎젙, stdout/stderr ?듭젣, 15遺?cooldown 異붽?, fallback key瑜?`main.py` 湲곕? ?щ㎎怨??쇱튂??|
| ?ㅽ???寃쎄퀬 ?꾪솕 | `dashboard/main_dashboard.py` | ?붽퀬 `QTableWidget` stylesheet瑜??⑥닚?뷀빐 parse warning ?먯씤 踰붿쐞瑜?異뺤냼 |
| ?몄뀡 ?몃뱶?ㅽ봽 ?뺣━ | `dev_memory/*.md` | ?ㅻ뒛 ?묒뾽 ?붿빟, ?꾩옱 ?곹깭, ?꾩냽 TODO, ?ㅺ퀎寃곗젙/踰꾧렇 湲곕줉 ?낅뜲?댄듃 |

### 濡쒓렇 湲곕컲 吏꾨떒 寃곕줎

- ?뺤긽 ?μ쨷 ?ш린??`2026-05-14 14:09:23`)? `startup sync -> realtime start -> tick/hoga ?섏떊`源뚯? 吏꾪뻾??- ?쇨컙 ?ш린??`2026-05-14 20:18:19`, `20:20:15`, `20:26:13`)? 怨듯넻?곸쑝濡?`CpTd0723` ?붽퀬 TR timeout, `FutureMst` snapshot timeout ??怨㏓컮濡??ㅼ떆媛??쒖옉 寃쎈줈濡?吏꾩엯
- 留덉?留??щ?(`2026-05-14 20:26:13` ?쒖옉)??`20:26:43 balance timeout -> 20:27:13 snapshot timeout -> 20:27:17 Qt loop -> -1073741819` ?⑦꽩?쇰줈 醫낅즺
- ?곕씪???대쾲 ?몄뀡??1李?寃곕줎? "?μ쇅 timeout ?곹깭?먯꽌 ?ㅼ떆媛?援щ룆??媛뺥뻾?섎뒗 寃쎈줈媛 COM access violation???좊컻??媛?μ꽦???믩떎"??寃?
### 寃利??곹깭

- `python -m py_compile main.py dashboard\main_dashboard.py collection\macro\macro_fetcher.py` ?듦낵
- 理쒖떊 ?μ쇅 launcher ?ъ떎??寃利앹? ?꾩쭅 誘몄떎??- `Could not parse stylesheet of object QTableWidget(...)` 寃쎄퀬???먯씤 踰붿쐞瑜?以꾩?吏留??꾩쟾 ?댁냼 ?щ????ъ떎???뺤씤 ?꾩슂

## 2026-05-14 (32李???2李?媛먯궗 P3 4醫??섏젙)

**Work**: 2李?媛먯궗 蹂닿퀬??`CODEX_SESSION_20260514_PROJECT_AUDIT.md`) P3 ??ぉ 4醫?媛쒖꽑.

### ?섏젙 ?댁뿭

| ??ぉ | ?뚯씪 | 蹂寃?|
|---|---|---|
| M5: Dynamic Sizing 0 ?섎졃 | `strategy/entry/dynamic_sizing.py` | `MIN_COMBINED_FRACTION=0.12` 異붽? ??7?⑺꽣 怨깆씠 ?꾧퀎媛?誘몃쭔?대㈃ `_blocked()` 諛섑솚 (怨쇱냼 媛뺤젣 吏꾩엯 李⑤떒) |
| M6: 09:00~09:05 誘몃텇瑜?| `config/settings.py` / `utils/time_utils.py` / `strategy/entry/time_strategy_router.py` | `GAP_OPEN("09:00","09:05")` 援ш컙 ?좎꽕. `min_confidence=0.67, size_mult=0.5, allow_new_entry=True` |
| M7: StandardScaler ?명썑??| `model/multi_horizon_model.py` | `_scaler_fitted_at` ??꾩뒪?ы봽 湲곕줉 ??`predict_proba()`?먯꽌 90遺?珥덇낵 ??WARNING + |z|>4 洹밸떒 ?쇱쿂 寃쎄퀬 |
| 留뚭린??FOMC 遺??| `utils/time_utils.py` / `strategy/entry/time_strategy_router.py` | ?붾Ъ 留뚭린??怨꾩궛(`get_monthly_expiry_date`) + FOMC ?좎쭨 紐⑸줉 + `apply_expiry_override()` / `apply_fomc_override()` 異붽? |

---

## 2026-05-14 (31李???2李?媛먯궗 P1 5醫??섏젙)

**Work**: 2李?媛먯궗 P1 ??ぉ 5醫?援ы쁽 (KST ??꾩〈 쨌 GBM ?뚮씪誘명꽣 쨌 silent except 쨌 CORE 寃쎈낫 쨌 EnsembleGater ?⑤씪???숈뒿).

### ?섏젙 ?댁뿭

| ?곗꽑?쒖쐞 | ??ぉ | ?뚯씪 | 蹂寃?|
|---|---|---|---|
| P1 (C3) | KST ??꾩〈 ?꾩껜 ?곸슜 | `utils/time_utils.py` ??10媛?紐⑤뱢 | `KST = timezone(+9)` ?곸닔 + `now_kst()` ?ы띁. 紐⑤뱺 `datetime.now()` 援먯껜 |
| P1 (H1) | silent except ?μ븷 ????쒓굅 | `main.py` | 8怨?`except Exception: pass` ??`logger.warning/debug` |
| P1 (H2) | CORE ?쇱쿂 0 ?대갚 ??ERROR 寃쎈낫 | `features/feature_builder.py` | CVD/VWAP/OFI ?곗냽 ?ㅽ뙣 3????ERROR 濡쒓렇 + Slack 寃쎈낫 |
| P1 (M1) | GBM ?뚮씪誘명꽣 遺덉씪移?| `config/settings.py` / `model/multi_horizon_model.py` / `learning/batch_retrainer.py` | `GBM_MIN_SAMPLES_LEAF=10` 怨듭쑀 ?곸닔 ?????숈뒿湲??숈씪 ?뚮씪誘명꽣 |
| P1 (H4) | EnsembleGater 怨좎젙 媛以묒튂 | `model/ensemble_gater.py` / `model/ensemble_decision.py` / `main.py` | `record_outcome()` ?⑤씪???숈뒿 (lr=0.005) + ?뚯씪 ?곸냽 |

---

## 2026-05-14 (30李????꾩껜 媛먯궗 + 踰꾧렇 ?섏젙 + ?ㅽ뀅 紐⑤뱢 援ы쁽)

**Work**: 媛먯궗 蹂닿퀬??`CODEX_SESSION_20260514_PROJECT_AUDIT.md`) 湲곕컲 ?쒖뒪???꾩껜 肄붾뱶 媛먯궗 ???곗꽑?쒖쐞蹂?踰꾧렇 ?섏젙 ???듭떖 ?ㅽ뀅 紐⑤뱢 3媛?援ы쁽 + main.py ?곌껐.

### 踰꾧렇 ?섏젙 (P0~P3)

| ?곗꽑?쒖쐞 | ID | ?뚯씪 | ?먯씤 | ?섏젙 |
|---|---|---|---|---|
| P0 | ??| `strategy/entry/checklist.py` | FLAT(0) 諛⑺뼢??`is_long=False`濡??됯??섏뼱 理쒕? 8/9 SHORT 泥댄겕 ?듦낵 ??A湲?AUTO SHORT 媛??| FLAT 議곌린 諛섑솚(X?깃툒, auto_entry=False) |
| P1 | B75 | `features/feature_builder.py` | `bar["close"]` 吏곸젒 ?묎렐 ??KeyError / ZeroDivision. 9媛?怨꾩궛 釉붾줉 ?덉쇅 ?꾪뙆 | safe `bar.get()` + 9媛?釉붾줉 媛쒕퀎 try/except + 湲곕낯媛?fallback |
| P1 | B76 | `features/technical/ofi.py` | `flush_minute()` ??`_prev_*` 誘몄큹湲고솕 ???ㅼ쓬 遺꾨큺 泥???stale delta | `flush_minute()` 留먮???`_prev_*=None` 4媛?由ъ뀑 |
| P1 | B77 | `safety/circuit_breaker.py` | ATR 踰꾪띁 ?좎뼵留??덇퀬 以묒븰媛??됲솢 ?놁쓬 ???쒓컙 湲됰벑 ?ㅻ컻??| 利됱떆 諛쒕룞 + 踰꾪띁 以묒븰媛?0.7諛?湲곗? 吏??湲됰벑 媛먯? 異붽? |
| P2 | B78 | `main.py` | `pre_market_setup()`???붾? 留ㅽ겕濡??섎뱶肄붾뵫, `MacroFetcher` 誘몄뿰寃?| ??API ?곕룞 (`macro_fetcher.get_features()` + 횞100 ?⑥쐞 蹂?? |
| P2 | ??| `collection/broker/kiwoom_broker.py` | `InvestorData(kiwoom_api=None)` ??API 誘몄＜??| `InvestorData(kiwoom_api=self._api)` |
| P2 | ??| `strategy/position/position_tracker.py` | ?몄퐫??源⑥쭊 臾몄옄??`"???????곸벉"` 4媛쒖냼 | `"?ъ????놁쓬"` ?뺤젙 |
| P3 | ??| `strategy/entry/entry_manager.py` | main.py?먯꽌 ??踰덈룄 ?몄뒪?댁뒪?붾릺吏 ?딆? Dead Code (Kiwoom ?꾩슜 API ?쒕챸) | ?뚯씪 ??젣 |
| P3 | ??| `main.py` | `_send_kiwoom_entry/exit_order` ?⑥닔紐??붿〈 (Cybos 留덉씠洹몃젅?댁뀡 誘몄셿) | `_send_broker_entry/exit_order` rename (13媛쒖냼) |
| P3 | ??| `features/technical/cvd.py` | `update()` 蹂댄빀 ??price==prev) `delta=qty`濡?Long 諛붿씠?댁뒪 ?꾩쟻 | `delta=0` (以묐┰) 泥섎━ |

### ?ㅽ뀅 紐⑤뱢 援ы쁽

| ?뚯씪 | ?댁슜 |
|---|---|
| `features/macro/macro_feature_transformer.py` | VIX/SP500/?섏뒪????9媛??뺢퇋???쇱쿂. MacroFetcher ??ML ?낅젰 蹂?? |
| `learning/self_learning/daily_consolidator.py` | ?쒓컙?蹂??뺥솗??吏묎퀎 ????깅뒫 援ш컙 confidence ?⑤꼸?? `data/zone_penalty.json` ?곸냽. |
| `learning/self_learning/drift_adjuster.py` | 5??濡ㅻ쭅 ?뺥솗??異붿씠 ??SGD alpha ?숈쟻 議곗젙. ?쒕━?꾪듃 媛먯? ??alpha횞1.5, ?뚮났 ??alpha횞0.8. `data/drift_adjuster_state.json` ?곸냽. |
| `collection/options/pcr_store.py` | ?몄씤 肄????쒕ℓ?섎줈 PCR 怨꾩궛. 20遺?濡ㅻ쭅. 誘몄?????以묐┰(1.0) 諛섑솚. |
| `features/options/option_features.py` | PCR ??6媛??뺢퇋???쇱쿂 (pcr_norm, bearish/bullish/extreme 諛붿씠?덈━, slope_norm, available). |

### main.py ?곌껐

- import 5媛?異붽?
- `__init__`: 5媛??몄뒪?댁뒪 異붽?
- STEP 4: `pcr_store.update()` ??`macro_transformer.transform()` ??`option_feat_calc.transform()` ??`feature_builder.build(macro_data=, option_data=)`
- STEP 1: 5m ?몃씪?댁쫵 寃곌낵瑜?`daily_consolidator.record(zone, correct)` ?곌껐
- `daily_close()`: `consolidate()` + `drift_adjuster.record_accuracy()` + SGD alpha 媛깆떊 + `pcr_store.reset_daily()`

### 蹂대쪟 ??ぉ

- `research_bot/code_generators/` ?ㅼ?以꾨윭 ?곌껐 ??ROADMAP.md Phase 6 ?뱀뀡??蹂대쪟 ?댁쑀쨌?좏뻾議곌굔 湲곕줉

### ?듭떖 諛쒓껄 ?ы빆

- **FLAT?묨UTO SHORT ?좎옱 踰꾧렇**: 媛??以묒슂??諛쒓껄. FLAT(0)??Boolean False濡??됯? ??is_long=False ??SHORT 泥댄겕 8/9 ?듦낵 媛?? 媛먯궗 蹂닿퀬?쒖뿉 ?녿뜕 ?좉퇋 P0 踰꾧렇.
- **媛먯궗 蹂닿퀬???щ텇瑜?*: `entry_manager.py:237` P0(Cybos ?ㅻ뜑 遺덇?) ??P3(Dead Code). main.py?먯꽌 ?몄뒪?댁뒪?붾맂 ???놁쓬.
- **MacroFetcher ?⑥쐞 遺덉씪移?*: MacroFetcher 諛섑솚? ?뚯닔(0.005=0.5%), RegimeClassifier ?낅젰? ?쇱꽱??0.5=0.5%) ??횞100 蹂???꾩슂. ?붾? 肄붾뱶媛 ??踰꾧렇瑜??④린怨??덉뿀??
- **?몄퐫??源⑥쭚 ?ㅼ젣 4媛쒖냼**: 媛먯궗 蹂닿퀬?쒕뒗 2媛?蹂닿퀬, ?ㅼ젣 grep?쇰줈 4媛쒖냼(152쨌318쨌463쨌520?? 諛쒓껄.

---

## 2026-05-14 (29李???CB HALT ?ы썑 議곗궗 + 紐⑤뜽 ?좊ː??3醫?媛쒖꽑)

**Work**

?ㅻ뒛(2026-05-14) 11:22~11:36 諛쒖깮??CB HALT ?ш굔???ы썑 議곗궗?섍퀬, 踰꾧렇 3醫?利됱떆 ?섏젙 + ?щ컻 諛⑹? 媛쒖꽑 3醫?援ы쁽.

### ?ш굔 媛쒖슂

- 11:22 CB??30遺??뺥솗??遺議? 諛쒕룞?쇰줈 `CB_STATE_HALTED`
- ?댄썑 誘몄껌???ъ????붿〈, ?섎룞 泥?궛 踰꾪듉 臾댄슚 ?꾩긽 諛쒖깮
- 10:32~10:42 GBM??conf=1.000 LONG ?좏샇 11???곗냽 ?ㅽ뙋(?ㅼ젣: DOWN) ??CB???몃━嫄?
### 踰꾧렇 ?섏젙 (B84~B86)

| 踰꾧렇 | ?뚯씪 | ?먯씤 | ?섏젙 |
|---|---|---|---|
| **B84** EXIT pending stuck (Chejan ?대깽???좎떎) | `main.py` | 泥닿껐 泥댁옍???좎떎?섎㈃ filled=3/4 怨좎갑, `_ts_resolve_stuck_exit_pending`??`expected_remaining` 鍮꾧탳 ?놁씠 qty?? 濡??ㅽ뙋 | `prev_pos_qty` ?????`expected_remaining = prev_pos_qty - pending.qty` 鍮꾧탳 異붽? |
| **B85** CB HALT ???ъ???誘몄껌??| `safety/circuit_breaker.py` | `_trigger_halt()`媛 CB????諛쒕룞 ??`_emergency_exit` 肄쒕갚???몄텧?섏? ?딆쓬 | `_trigger_halt()` 留먮???`if self._emergency_exit: self._emergency_exit()` 異붽? |
| **B86** CB HALT 以??섎룞 泥?궛 遺덇? | `main.py` | `_on_manual_exit_requested`?먯꽌 pending 二쇰Ц 議댁옱 ??CB HALT ?щ? 遺덈Ц?섍퀬 return | CB HALT ?곹깭硫?pending 媛뺤젣 ?뚮㈇ ??泥?궛 吏꾪뻾?섎룄濡?遺꾧린 異붽? |

### 紐⑤뜽 ?좊ː??媛쒖꽑 (C09~C11)

| 媛쒖꽑 | ?뚯씪 | ?댁슜 |
|---|---|---|
| **C09** GBM 怨쇱떊 ?대━??| `model/multi_horizon_model.py` | `CONF_CLIP = 0.92`. conf > 0.92 珥덇낵遺꾩쓣 ?섎㉧吏 ???대옒?ㅼ뿉 洹좊벑 遺꾨같. ??1 蹂댁〈. |
| **C10** CB???숈쟻 ?꾧퀎媛?| `safety/circuit_breaker.py` + `main.py` | conf ??0.85 ?ㅻ쪟 5???곗냽 ???뺥솗???꾧퀎媛?0.35 ??0.50 ?먮룞 ?곹뼢. `record_accuracy(confidence=)` ?꾨떖 |
| **C11** ?몄뀡 ?ъ떆??GBM 利됱떆 ?ы븰??| `main.py` | `_warmup_retrain_pending` ?뚮옒洹? `connect_broker()` ??set ??泥??뚯씠?꾨씪??STEP 3?먯꽌 `retrain_now(force=True)` ?몄텧 |

### CB??諛쒕룞 ?뺣떦??寃利?
- DB 荑쇰━濡??뱀씪 30遺??몃씪?댁쫵 ?덉륫 ?꾩닔 ?뺤씤
- `_session_start_ts = 10:31:10` (蹂듭썝 ?꾨즺 ?쒓컖) ?댄썑 ?섑뵆 20嫄?湲곗? ?뺥솗??
  - 11:22 ?뺤씤 湲곗? ??acc ??5% (寃쎄퀬 1/2), 11:36 ?뺤씤 ??acc ??9.5% (寃쎄퀬 2/2 ??HALT)
- **寃곕줎: ?ㅻ컻???꾨떂. 10:32~10:42 紐⑤뜽 媛깆떊 ?녿뒗 ?ъ떆??吏곹썑 援ъ떇 GBM???곗냽 怨쇱떊 ?ㅽ뙋??寃껋씠 ?뺣떦???몃━嫄?**

### ?섏젙 ?뚯씪 紐⑸줉

- `main.py` ??B84쨌B86쨌C10쨌C11 (4嫄?
- `safety/circuit_breaker.py` ??B85쨌C10 (2嫄?
- `model/multi_horizon_model.py` ??C09 (1嫄?
- `config/settings.py` ??C10 ?곸닔 3媛?異붽?

---

## 2026-05-14 (28李???L2 ?곴뎄以묐떒 諛곗? UI + 吏꾩엯愿由?紐⑤뱶 ?꾪꽣 2?쒖쐞 援ы쁽)

**Work**

ProfitGuard L2 Tier Gate ?곴뎄以묐떒 ?곹깭瑜???쒕낫?쒖뿉 ?쒓컖?뷀븯怨? 吏꾩엯愿由???쓽 ?깃툒蹂?諛곗?瑜??ㅼ젣 ?꾪꽣留곸쑝濡??곌껐?덈떎.

### 媛쒖꽑 C07: L2 ?곴뎄以묐떒 諛곗? ?쒓컖??
**?뚯씪**: `dashboard/main_dashboard.py`, `strategy/profit_guard.py`, `main.py`

**?댁슜**:
- `profit_guard.py`:
  - `_TierGate.halt_threshold`, `_TierGate.halt_tier` ?꾨줈?쇳떚 異붽?
  - `ProfitGuard.get_l2_halt_info()` 硫붿꽌??異붽? ??`{'is_halted': bool, 'halt_threshold': float, 'halt_tier': int}` 諛섑솚
- `dashboard/main_dashboard.py`:
  - `self.lbl_l2_halt` 諛곗? ?앹꽦 (CB 諛곗? ?ㅻⅨ履?
  - `update_l2_halt_badge(is_halted, threshold)` 硫붿꽌??異붽?
  - ?쒖꽦 ?곹깭: **?뵏 L2 以묐떒 (N.NM??** 鍮④컯 諛곗? (C62828)
  - 鍮꾪솢?? 諛곗? ?④?
- `main.py`:
  - STEP 9 吏곹썑 留ㅻ텇 L2 halt ?곹깭 議고쉶 諛???쒕낫??媛깆떊

**諛곗? ?쒖떆 洹쒖튃**:
- L2 halt ?쒖꽦 ??鍮④컯 諛곗? + ?꾧퀎媛??쒖떆 (諛깅쭔 ???⑥쐞)
- L2 halt 鍮꾪솢????諛곗? ?④?
- ?몃쾭: "嫄곕옒以묐떒 ?꾧퀎 ?꾨떖 ??湲덉씪 嫄곕옒 ?곴뎄 以묐떒" ?댄똻

### 媛쒖꽑 C08: 吏꾩엯愿由?紐⑤뱶 ?꾪꽣 2?쒖쐞 援ы쁽

**?뚯씪**: `main.py`

**?댁슜**:
- STEP 7 吏꾩엯 吏곸쟾??紐⑤뱶蹂??깃툒 ?꾪꽣 異붽?
- ?곗꽑?쒖쐞:
  1. **L2 ProfitGuard 泥댄겕** (?섏씡 蹂댁〈 ?꾨왂, ?쒖뒪??李⑥썝)
  2. **紐⑤뱶 ?꾪꽣 泥댄겕** (?좏샇 媛뺣룄 ?좏샇?? ?ъ슜???좏깮)
- 紐⑤뱶蹂??덉슜 ?깃툒:
  - `"auto"` (A ?깃툒吏꾩엯): A湲됰쭔
  - `"hybrid"` (B ?깃툒吏꾩엯, 湲곕낯媛?: A, B湲?  - `"manual"` (C ?깃툒吏꾩엯): A, B, C湲?- ?꾪꽣 李⑤떒 ??濡쒓렇:
  - 紐⑤뱶?꾪꽣 李⑤떒: `"[紐⑤뱶?꾪꽣] C湲??좏샇 ??hybrid 紐⑤뱶(['A', 'B']) 遺덉씪移???吏꾩엯 李⑤떒"`
  - ?먮룞 吏꾩엯 ??吏꾩엯 ?ㅽ뻾 ?먮뒗 紐⑤뱶?꾪꽣 李⑤떒

**?ㅺ퀎 寃利??щ?**:
```
湲덉씪 ?섏씡 50留뚯썝 + C湲??좏샇 + B ?깃툒吏꾩엯 紐⑤뱶
??L2 泥댄겕: min_mult=0.6, 0.6 >= 0.6 ???듦낵
??紐⑤뱶?꾪꽣: C in [A,B] ????李⑤떒 (L2 ?듦낵?덉쑝??紐⑤뱶?먯꽌 ?꾪꽣??
??寃곌낵: 吏꾩엯 遺덇? (?먯씤: 紐⑤뱶?꾪꽣)
```

### ?ㅺ퀎 寃곗젙

- L2 ?곗꽑?쒖쐞 1?쒖쐞: ?쒖뒪???섏씡 蹂댁〈 ?뺤콉? ?ъ슜??紐⑤뱶 ?좏깮蹂대떎 ?곗꽑
- 紐⑤뱶 ?곗꽑?쒖쐞 2?쒖쐞: L2 ?듦낵 ???ъ슜???좏샇 媛뺣룄 ?꾪꽣留?(Auto/Hybrid/Manual)
- 李⑤떒 ?ъ쑀 紐낇솗?? 濡쒓렇??L2 ?먮뒗 紐⑤뱶?꾪꽣 以?臾댁뾿??李⑤떒?덈뒗吏 ?쒖떆

### 寃利?寃곌낵

- ??Auto ON/OFF 諛곗?: ?꾨꼍?섍쾶 援ы쁽/?묐룞 以?  - ?좏샇 ?곌껐: ??  - ?곹깭 愿由? ??  - 吏꾩엯 濡쒖쭅 ?쒖뼱: ??  - 濡쒓렇 湲곕줉: ??- ??L2 halt 諛곗?: 留ㅻ텇 ?숆린?? ?뺤긽 ?쒖떆
- ??紐⑤뱶 ?꾪꽣: L2 ?ㅼ쓬 2?쒖쐞濡??묐룞 ?뺤씤

### ?뚮젮吏?臾몄젣

- 吏꾩엯愿由???쓽 A/B/C ?깃툒吏꾩엯 踰꾪듉 UI??議댁옱?섏?留??ㅼ젣 紐⑤뱶 ?숈옉? ?꾩쟾??誘멸뎄????**?대쾲 ?뚯감?먯꽌 媛쒖꽑 C08濡??꾩꽦**
- profit_guard_prefs.json??profit_tiers 以묐났 ?꾧퀎媛?([500000] 2媛? ?뺣━ ?꾩슂 (湲곕뒫??臾몄젣 ?놁쓬, 媛?낆꽦 媛쒖꽑)

---

## 2026-05-13 (26李????묒뾽?ㅼ?以꾨윭 ?쒖꽌?섏〈 濡쒓렇??異⑸룎 遺꾩꽍 + ?ㅼ? ?먮룞濡쒓렇??媛쒖꽑???뺣━)

**Work**

Windows ?묒뾽?ㅼ?以꾨윭?먯꽌 `start_mireuk.bat` ?댄썑 `start_kiwoom.bat` ?ㅽ뻾 ???ㅼ? ?먮룞濡쒓렇?몄씠 ?ㅽ뙣?섎뒗 ?쒖꽌 ?섏〈 臾몄젣瑜??먯씤 遺꾩꽍?섍퀬, ?쒖꽌? 臾닿??섍쾶 ?숈옉?섎룄濡?媛쒖꽑?덉쓣 ?ㅺ퀎?덈떎.

### 踰꾧렇 B83: `mireuk -> kiwoom` ?쒖꽌?먯꽌 ?ㅼ? ?먮룞濡쒓렇???ㅽ뙣

**愿痢?*:
- `kiwoom -> mireuk`: ?????뺤긽
- `mireuk -> kiwoom`: ?ㅼ? ?먮룞濡쒓렇???ㅽ뙣

**?먯씤 遺꾩꽍 ?붿빟**:
1. **?덈?醫뚰몴 湲곕컲 GUI 留ㅽ겕濡?痍⑥빟??*
  - ?ㅼ? 濡쒓렇???먮룞?붽? ?덈?醫뚰몴 ?대┃/遺숈뿬?ｊ린 諛⑹떇???? Cybos/誘몃Ⅵ??李쎌쓽 Z-order 蹂?붾줈 ?대┃ ??곸씠 ?붾뱾由?
2. **蹂댁븞 紐⑤뱢 ?ㅼ엯???꾪궧 異⑸룎 媛?μ꽦**
  - Cybos 怨꾩뿴 ?ㅽ뻾 ???꾩뿭 ?ㅼ엯?????섍꼍?먯꽌 援ы삎 SendKeys 怨꾩뿴????遺덉븞?뺥빐吏?
3. **?대┰蹂대뱶 ?섏〈 ?낅젰 寃쏀빀**
  - `Ctrl+V` 以묒떖 ?낅젰? ? ?꾨줈?몄뒪 ?숈떆?숈옉/?대┰蹂대뱶 ?먯쑀??痍⑥빟.

### 媛쒖꽑 C06: ?ㅼ? ?먮룞濡쒓렇??寃쎈줈瑜?李?媛앹껜 湲곕컲(pywinauto)?쇰줈 ?꾪솚 ?쒖븞

**?곸슜 ????몃? ?꾨줈?앺듃)**:
- `C:/Users/82108/PycharmProjects/auto_trader_kiwoom/start_kiwoom.bat`
- `C:/Users/82108/PycharmProjects/auto_trader_kiwoom/kiwoom_autologin.py` (?좉퇋 ?쒖븞)

**?듭떖 諛⑺뼢**:
- PowerShell ?덈?醫뚰몴/?대┰蹂대뱶 諛⑹떇 ???pywinauto濡?濡쒓렇??李?媛앹껜瑜?吏곸젒 李얠븘 ?ъ빱??+ 而⑦듃濡??낅젰
- `start_kiwoom.bat`?먯꽌 py37_32 ?섍꼍 ?쒖꽦????Python autologin ?몄텧
- ?낅젰媛믪? ?ㅽ겕由쏀듃 ?섎뱶肄붾뵫 湲덉?(?섍꼍蹂??蹂댁븞 ??μ냼 ?ъ슜)

**湲곕? ?④낵**:
- ?ㅽ뻾 ?쒖꽌 臾닿? (`mireuk -> kiwoom`, `kiwoom -> mireuk` 紐⑤몢 ?덉젙)
- ?댁긽??李??꾩튂/Z-order 蹂???댁꽦 ?μ긽
- ?대┰蹂대뱶 寃쏀빀 媛먯냼

---

## 2026-05-13 (24李???遊됱감??泥?궛 留덉빱 ?쒖씤??媛쒖꽑 + TP/SL 而щ윭 ?뺣━)

**Work**

遊됱감??泥?궛 ?쒓린 媛?낆꽦??媛쒖꽑?섍린 ?꾪빐 泥?궛 諛곗?/?쇰꺼 ?뚮뜑留곸쓣 2?④퀎濡?議곗젙. 1李⑤줈 ?꾩씠肄?諛곗?瑜??쒓굅?섍퀬 ?띿뒪??以묒떖?쇰줈 ?⑥닚?뷀븳 ?? 2李⑤줈 吏꾩엯 留덉빱???議고솕瑜??꾪빐 泥?궛遊됱뿉 ?뚰삎 ?ㅽ꺃??T/S/P) 留덉빱瑜??щ룄??

### 媛쒖꽑 C04: 泥?궛 ?쇰꺼 ?띿뒪??以묒떖 ?뚮뜑留?
**?뚯씪**: `dashboard/main_dashboard.py`

**?댁슜**:
- `_draw_exit_marker()`?먯꽌 湲곗〈 ?ㅼ씠??而?P 諛곗? + 移?諛뺤뒪 議고빀 ?쒓굅
- TP/SL/PX瑜??띿뒪??以묒떖?쇰줈 ?쒖떆?섎룄濡??뺣━
- ?ㅽ겕 ?뚮쭏 媛?낆꽦 蹂댁셿???꾪빐 ?띿뒪??洹몃┝???덉씠??異붽?

### 媛쒖꽑 C05: 泥?궛遊??뚰삎 ?ㅽ꺃??留덉빱 ?щ룄??(吏꾩엯留덉빱? 議고솕)

**?뚯씪**: `dashboard/main_dashboard.py`

**?댁슜**:
- ?ъ슜???쇰뱶諛?諛섏쁺: 泥?궛遊됱뿉 吏꾩엯 留덉빱? ?좎궗???쒓컖 ?듭빱 ?꾩슂
- `_draw_exit_stamp()` ?ы띁 異붽?
- 泥?궛 ??낅퀎 ?뚰삎 ?ㅽ꺃??glyph) ?곸슜:
  - TP(WIN): `T`
  - SL(LOSS): `S`
  - PX/PARTIAL: `P`
- ?쇰꺼 ?쒖옉?먯쓣 ?곗륫?쇰줈 ?ㅽ봽?뗮빐 ?ㅽ꺃?꾩? 寃뱀묠 諛⑹?

### 踰꾧렇 B82: 泥?궛 ?뺣낫媛 ?띿뒪?몃쭔 ?덉쓣 ??遊??꾩튂 ?몄?媛 ?대젮?

**?뚯씪**: `dashboard/main_dashboard.py`

**利앹긽**: ?띿뒪?몃쭔 ?④린硫?泥?궛 ?쒖젏/媛寃⑹쓽 ?뺥솗??遊??꾩튂瑜?吏곴??곸쑝濡??곕씪媛湲??대젮?.

**?먯씤**: 留덉빱 ?쒓컖 ?듭빱媛 ?щ씪???쇰꺼??罹붾뱾 援곗쭛 ?꾩뿉???먮Ⅴ???띿뒪?몄쿂??蹂댁엫.

**?섏젙**: ?뚰삎 ?ㅽ꺃?꾨? 泥?궛 媛寃?醫뚰몴???ㅼ떆 諛곗튂??遊??쇰꺼 ?곌껐??蹂듭썝.

---

## 2026-05-13 (23李???泥?궛愿由?UX/?곹깭 ?숆린??媛쒖꽑 + ?먮룞 ??蹂듦? 濡쒖쭅 蹂닿컯)

**Work**

泥?궛愿由???쓽 ?곹깭 諛곗?? ?ㅼ껜寃??뚯씠?꾨씪??媛?吏???ㅽ몴?쒕? 以꾩씠湲??꾪븳 理쒖냼?섏젙 7嫄??곸슜. ENTRY 吏곹썑 紐⑺몴 ?꾨떖 ?ㅽ깘??李⑤떒?섍퀬, ?섎룞 ???꾪솚 ???좏쑕 蹂듦? 濡쒖쭅???ъ빱???쒕룞源뚯? ?뺤옣.

### 媛쒖꽑 C01: 泥?궛 諛곗? ?곹깭 enum ?꾩엯 + pending/移댁슫?몃떎???곗씠???곌껐

**?뚯씪**: `dashboard/main_dashboard.py`, `main.py`

**?댁슜**:
- `TriggerBadgeState` enum 異붽? (`媛먯떆以??湲??곗젙以??꾨떖/?꾨즺/二쇱쓽/二쇰Ц以?蹂댄샇?꾪솚`)
- `run_minute_pipeline`??`dashboard.update_position(...)` payload???꾨옒 異붽?:
  - `pending_active`, `pending_kind`, `pending_reason`, `pending_stage`, `pending_filled`, `pending_qty`
  - `time_exit_countdown_sec`
- ?쒓컙泥?궛 諛곗?瑜?`T-mm:ss` / `?꾨컯 mm:ss` / `諛쒕룞`?쇰줈 ?쒖떆

### 踰꾧렇 B79: 遺遺꾩껌???꾨즺 ??`二쇰Ц以? 諛곗? ?붿긽 (泥닿컧 吏??

**?뚯씪**: `main.py`

**利앹긽**: Chejan 泥닿껐???꾨즺?먮뒗??泥?궛愿由???? ?ㅼ쓬 遺꾨큺源뚯? `二쇰Ц以? ?곹깭媛 ?⑤뒗 ?꾩긽.

**?먯씤**: 泥?궛 ?⑤꼸 ?곹깭 媛깆떊??留ㅻ텇 ?뚯씠?꾨씪??以묒떖?쇰줈 ?숈옉. Chejan fill 吏곹썑 pending 蹂寃??뚮㈇??利됱떆 諛섏쁺?섏? ?딆쓬.

**?섏젙**:
- `_ts_push_exit_panel_now()` ?ы띁 異붽? (Chejan 吏곹썑 利됱떆 `update_position`)
- `_clear_pending_order()`?먯꽌 pending ?뚮㈇ 吏곹썑 利됱떆 ?⑤꼸 媛깆떊 ?몄텧
- `_ts_on_chejan_event_cybos_safe()`?먯꽌 泥닿껐 泥섎━ 吏곹썑 利됱떆 ?⑤꼸 媛깆떊 ?몄텧

### 踰꾧렇 B80: ENTRY 吏곹썑 `3李?紐⑺몴 34% ?꾨떖` ?ㅽ몴??
**?뚯씪**: `dashboard/main_dashboard.py`

**利앹긽**: 諛⑷툑 吏꾩엯??吏곹썑?몃뜲 3李?紐⑺몴媛 `?꾨떖`濡??쒖떆?섎뒗 false positive.

**?먯씤**: ENTRY 遺꾪븷泥닿껐 寃쎄퀎?먯꽌 tp 媛??뱁엳 `tp3`)??0/鍮꾩젙?곸쑝濡??ㅼ뼱?ㅻ㈃ 鍮꾧탳?앹씠 ??긽 李몄씠 ?????덉쓬.

**?섏젙**:
- `tp1/tp2/tp3 <= 0` 諛⑹뼱 ?뺢퇋??(`entry 짹 ATR 諛곗닔`濡?利됱떆 蹂댁젙)
- `pending_kind == "ENTRY"` ?숈븞 紐⑺몴 ?꾨떖 ?먯젙 ?좉툑
- 1/2/3李?紐⑺몴 諛곗? ?곹깭瑜?`?곗젙以??쇰줈 紐낆떆 ?쒖떆

### 媛쒖꽑 C02: ?쒖옉 吏곹썑 ?붽퀬-???뺣젹 怨듬갚 ?쒓굅

**?뚯씪**: `main.py`

**?댁슜**: `connect_broker()`?먯꽌 `_sync_position_from_broker()` 吏곹썑
- 蹂댁쑀 ?ъ??섏씠硫?`set_ui_position_mode()`
- FLAT?대㈃ `set_ui_ready_mode()`
瑜?利됱떆 ?몄텧??startup 紐⑤뱶 怨듬갚 ?쒓굅.

### 媛쒖꽑 C03: ?섎룞 ???꾪솚 ?좏쑕 蹂듦? ?먯젙 媛뺥솕

**?뚯씪**: `dashboard/main_dashboard.py`

**?댁슜**: `UiAutoTabController` ?좏쑕 ?먯젙(`_managed_widgets_under_mouse`)??- `hasFocus()`
- `QApplication.focusWidget()` 湲곗? ?섏쐞 ?꾩젽 ?ъ빱??瑜?異붽???留덉슦?????ㅻ낫???쒕룞???좏쑕 由ъ뀑?쇰줈 媛꾩＜.

---

## 2026-05-13 (22李???Cybos 二쇰Ц/泥닿껐 ?뚯씠?꾨씪??踰꾧렇 ?섏젙 + 利됱떆泥?궛 UI 遺덉씪移??닿껐)

**Work**

Cybos 誘몃땲?좊Ъ 二쇰Ц쨌泥닿껐 濡쒓렇 遺꾩꽍?쇰줈 踰꾧렇 4醫?諛쒓껄쨌?섏젙. 利됱떆泥?궛 ??UI ?붽퀬媛 1怨꾩빟 怨좎갑?섎뒗 臾몄젣??3以?蹂듯빀 ?먯씤 遺꾩꽍 諛??섏젙. 誘몃Ⅵ??李?理쒖긽??怨좎젙 ?댁젣.

### 踰꾧렇 B75: `or unfilled_qty == 0` ??遺遺꾩껜寃?泥?肄쒕갚 ??pending 議곌린 ?뚮㈇

**?뚯씪**: `main.py` (Cybos ?몃뱾??諛?Kiwoom ?덇굅???몃뱾??

**利앹긽**: 9怨꾩빟 吏꾩엯 二쇰Ц??15怨꾩빟?쇰줈 遺??덇퀬, 媛?遺꾨큺留덈떎 ?섎뱶?ㅽ넲 二쇰Ц ?щ컻??

**?먯씤**: Cybos `unfilled_qty`????긽 0 諛섑솚. `filled_qty >= qty or unfilled_qty == 0` 議곌굔?먯꽌 泥?泥닿껐 肄쒕갚??pending???뚮㈇ ???댄썑 泥닿껐??`_ts_handle_external_fill` 寃쎈줈濡??섎윭 ?섎웾???섎せ 異붽?.

**?섏젙**: ???몃뱾??紐⑤몢 `or unfilled_qty == 0` 議곌굔 ?쒓굅.

---

### 踰꾧렇 B76: ?숆????ㅽ뵂 ??遺꾪븷泥닿껐 ?섎웾 以묐났 ?곸궛

**?뚯씪**: `main.py`

**利앹긽**: B75 ?섏젙 ?꾩뿉???ъ????섎웾 珥덇낵. 9怨꾩빟 二쇰Ц ??泥?泥닿껐??VWAP 蹂댁젙(?섎웾 遺덈?) ???댄썑 泥닿껐留덈떎 `apply_entry_fill(add=True)` ???섎웾 以묐났.

**?먯씤**: ?숆????ㅽ뵂 二쇰Ц??泥?泥닿껐 ?꾨즺(optimistic 蹂댁젙) ?댄썑 異붽? 泥닿껐??吏꾩엯 異붽? 寃쎈줈濡??섎윭 `quantity += fill_qty` 以묐났 ?곸궛.

**?섏젙**: `_set_pending_order` 吏곹썑 `pending["optimistic_opened"] = True` + `partial_fill_count` ?뚮옒洹? ??踰덉㎏ ?댄썑 泥닿껐 ??VWAP留?蹂댁젙, ?섎웾? 遺덈?.

---

### 踰꾧렇 B77: EXIT 遺꾪븷泥닿껐 ??CB/Kelly 以묐났 湲곕줉 + 吏묎퀎 誘명씉

**?뚯씪**: `main.py`

**利앹긽**: 2??遺꾪븷泥닿껐 ??CB/Kelly媛 2??湲곕줉. ?듦퀎 ?섏씡瑜??쒓끝.

**?먯씤**: 泥닿껐 肄쒕갚留덈떎 `_post_partial_exit` / `_ts_record_nonfinal_exit` ?몄텧.

**?섏젙**: `_ts_agg_exit_fill` / `_ts_build_agg_exit_result` ?ы띁 異붽?. 留덉?留?泥닿껐(is_last_fill)?먯꽌留?吏묎퀎 寃곌낵濡??듦퀎 諛섏쁺. 以묎컙 泥닿껐? 濡쒓렇留?

---

### 踰꾧렇 B78 (蹂듯빀): 利됱떆泥?궛 ??UI ?붽퀬 1怨꾩빟 怨좎갑

**?뚯씪**: `main.py`, `dashboard/main_dashboard.py`

**利앹긽**: 利됱떆泥?궛 踰꾪듉 ?대┃ ??Cybos HTS??0怨꾩빟?몃뜲 誘몃Ⅵ??UI "?ㅼ떆媛??붽퀬"??蹂댁쑀??1 吏??

**?먯씤 3醫?*:
1. **Race condition**: `BlockRequest()` ?대? 硫붿떆吏 ?뚰봽濡?泥닿껐 肄쒕갚??`_set_pending_order` 蹂대떎 癒쇱? ?꾩갑 ??`pending=None` ??`_ts_handle_external_fill` 泥섎━ ??`_ts_force_balance_flat_ui` 誘명샇異?2. **?몃?泥닿껐 寃쎈줈 ?꾨씫**: `_ts_handle_external_fill` 理쒖쥌 泥?궛 ??`_ts_force_balance_flat_ui` + QTimer 誘명샇異????붽퀬 ?⑤꼸 利됱떆 誘멸갚??3. **Cybos status 釉붾옲??*: `GetHeaderValue(44)/(15)` 紐⑤몢 `""` 諛섑솚 ??`status=""` ??`is_final_fill=False` ??泥닿껐 肄쒕갚 ?곴뎄 臾댁떆 ??`position.status` LONG 怨좎갑 ???⑹꽦 ??1怨꾩빟 ?앹꽦

**?섏젙 4嫄?*:
- `_on_manual_exit_requested`: `_set_pending_order`瑜?`_send_kiwoom_exit_order` ?꾩쑝濡??대룞, ?ㅽ뙣 ??濡ㅻ갚
- `_ts_handle_external_fill`: 理쒖쥌 泥?궛 ??`_ts_force_balance_flat_ui` + QTimer(250ms, 1200ms) 異붽?
- `_ts_on_chejan_event_cybos_safe`: `is_final_fill` ?대갚 ??`status=""` + `fill_qty > 0` + `fill_price > 0` ??泥닿껐濡?媛꾩＜
- `_ts_push_balance_to_dashboard`: pending EXIT 議댁옱 ???⑹꽦 1怨꾩빟 ???앹꽦 ?듭젣

---

### 湲고?

- `dashboard/main_dashboard.py`: `WindowStaysOnTopHint` ?쒓굅 ??誘몃Ⅵ??李?理쒖긽??怨좎젙 ?댁젣

---

## 2026-05-13 (21李???遺꾨큺 ?뚯씠?꾨씪??NameError + 醫낅ぉ肄붾뱶 遺덉씪移??ш퀬 遺꾩꽍쨌諛⑹?梨?

**Work**

?μ쨷 status bar ?湲???NameError ?먯씤 洹쒕챸, 10:11:27 ?ъ떆?묒쑝濡?A0565/A0666 醫낅ぉ肄붾뱶 遺덉씪移??ш퀬 ?꾩껜 寃쎌쐞 遺꾩꽍 ??諛⑹?梨?3醫?援ы쁽. 遊됱감???댁쥌 媛寃??쇱옱 臾몄젣 ?섏젙.

### 踰꾧렇 B72: `run_minute_pipeline` ??`candle` NameError濡?留ㅻ텇 ?뚯씠?꾨씪???щ옒??
**?뚯씪**: `main.py:1776`

**利앹긽**: 遺꾨큺 status bar媛 怨꾩냽 "?湲? ?곹깭. WARN 濡쒓렇??`NameError: name 'candle' is not defined` 留ㅻ텇 諛섎났.

**?먯씤**: 梨뷀뵾???꾩쟾??Shadow ?ㅽ뻾 釉붾줉?먯꽌 ?뚮씪誘명꽣紐?`bar`媛 留욎?留?`candle`??李몄“. `run_minute_pipeline(self, bar: dict)` ?쒓렇?덉쿂?몃뜲 1776踰덉㎏ 以?`candle if isinstance(candle, dict)` ?ㅽ?.

**?섏젙**: `candle` ??`bar` ?⑥씪 ?쇱씤 ?섏젙.

---

### ?ш퀬 遺꾩꽍 ??10:11:27 ?ъ떆?묒쑝濡??명븳 醫낅ぉ肄붾뱶 遺덉씪移?(A0565 vs A0666)

**寃쎌쐞**:
1. 10:11:27 DB ?ъ큹湲고솕 ???쒖뒪???ъ떆??諛쒖깮
2. `ui_prefs.json`??`"symbol_code": "A0565000"` (誘몃땲?좊Ъ) ??????ъ떆????`_futures_code = A0565`
3. 釉뚮줈而??붽퀬?먮뒗 A0666(KOSPI200 ?좊Ъ) SHORT @ 1922.80 議댁옱
4. `BrokerSync verified=False, block_new_entries=True` ??吏꾩엯 李⑤떒?섏뿀?쇰굹 泥?궛? ?덉슜
5. A0565 ?꾩옱媛(~1177)瑜?A0666 ?ъ???1922.80) 湲곗? ?꾩옱媛濡??ъ슜 ??TP2 議곌굔 異⑹”(+745pt)
6. 10:12:00 TP2 泥?궛 二쇰Ц??A0565 肄붾뱶濡?諛쒖넚 ??A0565 LONG @ 1177.3 泥닿껐
7. ?쒖뒪???대? ?곹깭: FLAT(?ㅼ씤??. ?ㅼ젣 釉뚮줈而? A0666 SHORT 誘몄껌??+ A0565 LONG ?좉퇋 ?앹꽦

### 踰꾧렇 B73: ?ъ떆??肄붾뱶 遺덉씪移????섎せ??醫낅ぉ?쇰줈 泥?궛 二쇰Ц 諛쒖넚

**?뚯씪**: `strategy/position/position_tracker.py`, `main.py`

**?먯씤**: `position_state.json`??醫낅ぉ肄붾뱶媛 ?놁뼱 ?ъ떆????????ъ???A0666)怨?`_futures_code`(A0565) 遺덉씪移섎? 媛먯? 遺덇?. `block_new_entries`??吏꾩엯留?李⑤떒?섎?濡?泥?궛? ?섎せ??肄붾뱶濡?吏꾪뻾?? `_ts_on_chejan_event_cybos_safe`?먯꽌 泥닿껐 肄붾뱶 誘멸?利???A0565 泥닿껐???ъ????낅뜲?댄듃濡?泥섎━.

**?섏젙 3媛?*:
- `position_tracker.py`: `_futures_code`/`_loaded_futures_code` ?꾨뱶 + `set_futures_code()` + `force_flat()` + `_save_state()`??`futures_code` ??ぉ 異붽? + `load_state()`?먯꽌 蹂듭썝
- `main.py:connect_broker()`: `_futures_code` ?뺤젙 ??`_loaded_futures_code`? 鍮꾧탳 ??遺덉씪移????ъ???媛뺤젣 FLAT + CRITICAL 濡쒓렇
- `main.py:_ts_on_chejan_event_cybos_safe`: 泥닿껐 肄붾뱶 ??`_futures_code` ??WARNING + ?ъ???諛섏쁺 嫄곕?

### 踰꾧렇 B74: 遊됱감???댁쥌 醫낅ぉ 媛寃??쇱옱 ??Y異??ㅼ???遺뺢눼

**?뚯씪**: `collection/cybos/realtime_data.py`, `dashboard/main_dashboard.py`

**?먯씤**: ?ъ떆????A0666 罹붾뱾(~1922)怨??ъ떆????A0565 罹붾뱾(~1177)??`_closed_candles`???쇱옱. `paintEvent`媛 ?꾩껜 罹붾뱾 媛寃?踰붿쐞(lo??177, hi??930)濡?Y異뺤쓣 洹몃젮 媛쒕퀎 遊??吏곸엫(2~5pt)??1?쎌? 誘몃쭔?쇰줈 ?쒖떆?? `reload_today()`??DB?먯꽌 ?댁쥌 罹붾뱾??援щ텇 ?놁씠 濡쒕뱶.

**?섏젙 3媛?*:
- `realtime_data.py`: 罹붾뱾 dict??`"code": self.code` 異붽?
- `main_dashboard.py:on_candle_closed()`: ?섏떊 肄붾뱶 ??`_instrument_code` ??`_closed_candles` ?꾩껜 珥덇린??- `main_dashboard.py:reload_today()`: `_trim_to_last_price_group()` 異붽? ???곗냽 遊?媛?4% 珥덇낵 媛寃??먰봽 媛먯? ???댁쟾 ?곗씠??踰꾨┝

---

## 2026-05-13 (20李???Cybos 誘몃땲?좊Ъ ?ㅼ떆媛??뚯씠?꾨씪???뺣┰ + 肄붾뱶 泥닿퀎 ?ㅼ쬆)

**Work**

??媛쒖떆 ??遊뉗씠 09:00 ?댄썑 ?꾪? ?묐룞?섏? ?딆? ?먯씤??議곗궗?섍퀬, Cybos COM ?좊Ъ 肄붾뱶 泥닿퀎瑜??ㅼ쬆?곸쑝濡??뺤씤?덈떎. 誘몃땲?좊Ъ ?ㅼ떆媛?援щ룆??臾댁쓬 ?ㅽ뙣?섎뜕 洹쇰낯 ?먯씤???섏젙?섍퀬, KOSPI200 誘몃땲?좊Ъ 洹쇱썡臾?肄붾뱶 ?먯깋 諛⑸쾿???뺣┰?덈떎.

### 踰꾧렇 B70: Cybos FutureCurOnly ??8??肄붾뱶 臾댁쓬 ?ㅽ뙣

**?뚯씪**: `main.py`, `collection/cybos/api_connector.py`

**利앹긽**: ??媛쒖떆 ??09:00~09:23 ?숈븞 SIGNAL쨌TRADE 濡쒓렇媛 ?꾩쟾??鍮꾩뼱 ?덉뿀?? `[System] ?湲?以?| ?μ쨷 ??Cybos ?ㅼ떆媛?遺꾨큺 ?湲?以? 猷⑦봽媛 怨꾩냽 諛섎났?섎ŉ ?뚯씠?꾨씪??吏꾩엯 ?놁쓬.

**?먯씤**: `data/ui_prefs.json` ????λ맂 醫낅ぉ肄붾뱶媛 `A0565000` (8?먮━) ?뺤떇?댁뿀怨? ?닿쾬??洹몃?濡?`Dscbo1.FutureCurOnly.SetInputValue(0, code)` ???꾨떖. Cybos COM ?ㅼ떆媛?援щ룆 媛앹껜??8?먮━ 肄붾뱶瑜??먮윭 ?놁씠 ?섎씫?섏?留????대깽?몃? ?꾪? 諛쒖깮?쒗궎吏 ?딅뒗 臾댁쓬 ?ㅽ뙣. 5?먮━ 肄붾뱶(`A0565`)留??뺤긽 ?묐룞.

**?섏젙**: `main.py::connect_broker()`?먯꽌 UI 肄붾뱶 ?뺢퇋????8?먮━ + ??"000" ?대㈃ 留덉?留?3?먮━ ?쒓굅. `A0565000 ??A0565`, `A0166000 ??A0166`.

### ?ㅼ쬆 D48: Cybos COM ?좊Ъ 肄붾뱶 ?닿굅 媛앹껜蹂?諛섑솚 ?덈ぉ

**寃쎌쐞**: `CpUtil.CpKFutureCode`媛 KOSPI200 誘몃땲?좊Ъ 肄붾뱶瑜?諛섑솚??寃껋쑝濡?媛?뺥븯怨?以묎컙 ?섏젙?먯꽌 ?ъ슜?덈떎媛, ?섏떊??媛寃⑹씠 ~1938pt濡?KOSPI200(~380pt) ?섏?怨??꾪? ?щ씪 議곗궗??

**寃곕줎**:

| COM 媛앹껜 | 諛섑솚 ?곹뭹 | 肄붾뱶 ??| A05xxx ?ы븿 |
|---|---|---|---|
| `CpUtil.CpFutureCode` | KOSPI200 ?쇰컲?좊Ъ留?| A0166, A0169... | ??|
| `CpUtil.CpKFutureCode` | **肄붿뒪??50 ?좊Ъ留?* | A0666, A0669... | ??|
| `Dscbo1.FutureMst` ?꾨줈釉?| 媛쒕퀎 肄붾뱶 ?좏슚???뺤씤 | ??| ??(吏곸젒 ?꾨줈釉? |

KOSPI200 誘몃땲?좊Ъ(A05xxx)???닿굅?섎뒗 ?꾩슜 Cybos COM 媛앹껜??議댁옱?섏? ?딅뒗?? FutureMst ?꾨줈釉뚮쭔 ?ъ슜 媛??

### ?ㅼ쬆 D49: KOSPI200 誘몃땲?좊Ъ 肄붾뱶 洹쒖튃

`A05 + ?곕룄?앹옄由?+ ??hex uppercase)`: 2026-05=A0565, 2026-06=A0566, 2026-12=A056C. `CpFutureCode` ?닿굅 紐⑸줉???놁쑝硫?FutureMst BlockRequest DibStatus=0 + price>0?쇰줈 ?좏슚???먯젙.

### 援ы쁽: FutureMst ?꾨줈釉?湲곕컲 誘몃땲?좊Ъ 洹쇱썡臾??먯깋

**?뚯씪**: `collection/cybos/api_connector.py`, `collection/broker/cybos_broker.py`, `scripts/check_cybos_realtime.py`

- `api_connector.get_nearest_mini_futures_code()`: ?ㅻ뒛遺??7媛쒖썡 ?꾨낫 肄붾뱶瑜?FutureMst BlockRequest濡??꾨줈釉뚰빐 泥??좏슚 肄붾뱶 諛섑솚
- `cybos_broker.get_nearest_mini_futures_code()`: ?꾩엫 硫붿꽌??異붽?
- `main.py`: 誘몃땲?좊Ъ ?좏깮 ??UI 肄붾뱶 ?곗꽑, ?놁쑝硫?FutureMst ?꾨줈釉?寃곌낵 ?ъ슜. `broker_code`(?쇰컲?좊Ъ ?꾩슜 A01xxx)??誘몃땲?좊Ъ fallback?쇰줈 ?덈? ?ъ슜 遺덇?
- `check_cybos_realtime.py --mini`: CpKFutureCode ?ъ슜 ?쒓굅, FutureMst ?꾨줈釉뚮줈 援먯껜 + 寃곌낵 name ?쒖떆 媛쒖꽑

### 踰꾧렇 B71: ?ㅻ뒛 KOSDAQ150 ?좊Ъ 1怨꾩빟 ?섎せ 吏꾩엯

**寃쎌쐞**: 以묎컙 ?섎せ???섏젙(CpKFutureCode ??A0666 肄붾뱶 ?ъ슜) ?곹깭濡?遊뉗씠 ?ㅽ뻾?? `get_contract_spec("A0666")`: "0666".startswith("05") = False ??`pt_value=250,000` ??`is_mini=False` ??`min_qty=1`. 09:33??SHORT 1怨꾩빟 @ 1922.8 吏꾩엯. 醫낅ぉ ?먯껜??KOSPI200 誘몃땲?좊Ъ???꾨땶 肄붿뒪??50 ?좊Ъ.

**?곹깭**: 理쒖쥌 ?섏젙(?뺢퇋?? ?꾨즺?? 遊??ъ떆????A0565 援щ룆?쇰줈 ?뺤긽???덉젙.

---

## 2026-05-12 (19李????섏씡蹂댁〈 ???ㅼ젙媛??ъ떆???곸냽??

**Work**

?섏씡蹂댁〈 ???섎떒 ?ㅼ젙媛믪쓣 蹂寃???`?곸슜`?대룄 ?ъ떆????湲곕낯媛믪쑝濡?由ъ뀑?섎뜕 臾몄젣瑜??섏젙?덈떎.

### 踰꾧렇: ProfitGuard ?ㅼ젙???고??꾨쭔 諛섏쁺?섍퀬 ?붿뒪????μ씠 ?놁뿀??
**?뚯씪**: `dashboard/panels/profit_guard_panel.py`

**利앹긽**: `???곸슜` ?대┃ 吏곹썑?먮뒗 媛믪씠 諛섏쁺?섏?留? ?꾨줈洹몃옩 ?ъ떆????L1~L4 媛믪씠 湲곕낯媛믪쑝濡?蹂듦?.

**?먯씤**:
- `_on_config_changed()`媛 `guard.update_config(cfg)`留??몄텧?섍퀬 ?곸냽 ??μ쓣 ?섏? ?딆쓬
- ?쒖옉 ??guard 二쇱엯(`set_profit_guard`)? 硫붾え由?湲곕낯 config瑜?洹몃?濡??ъ슜

**?섏젙**:
- ????뚯씪 寃쎈줈 ?곸닔 異붽?: `data/profit_guard_prefs.json`
- `Apply` ??`_save_cfg_to_disk(cfg)` ?몄텧
- ?⑤꼸 珥덇린????`_restore_settings_ui_from_disk()` ?몄텧濡?UI ?좊컲??- `set_profit_guard()`?먯꽌 ?붿뒪???ㅼ젙 ?곗꽑 濡쒕뱶 ??guard??`update_config()` ?곸슜
- 濡쒕뱶 ?ㅽ뙣/?뚯씪 ?놁쓬? 湲곗〈 湲곕낯媛믪쑝濡??덉쟾 ?대갚

### 援ы쁽 ?곸꽭

- `import json`, `import os` 異붽?
- `_save_cfg_to_disk()` / `_load_cfg_from_disk()` / `_restore_settings_ui_from_disk()` 硫붿꽌???좎꽕
- `ProfitGuardConfig.to_dict()` ?щ㎎??洹몃?濡??ъ슜??踰꾩쟾 ?ы븿 JSON ???(`version: 1`)
- `profit_tiers`??list/tuple 湲몄씠 寃利???`(threshold, min_mult, max_qty)`濡??뚯떛

### 寃利?
- `get_errors` 湲곗? `dashboard/panels/profit_guard_panel.py` ?????ㅻ쪟 ?놁쓬

---

## 2026-05-12 (18李????먮룞 濡쒓렇??踰꾧렇 3醫??섏젙 + UI 醫낅ぉ ?곸냽??+ 誘몃땲?좊Ъ 怨꾩빟 ?ㅽ럺 ?숆린??+ ProfitGuard ?щ옒???섏젙)

**Work**

?ㅻ뒛 ???댁쁺 ??諛쒓껄??踰꾧렇 4嫄댁쓣 ?섏젙?섍퀬, ?쇰컲?좊Ъ/誘몃땲?좊Ъ ?꾪솚 ???고???怨꾩빟 ?ㅽ럺??UI ?좏깮???곕씪媛?꾨줉 ?뺣━?????몄뀡 留덈Т由ы뻽??

### 援ы쁽 0: UI ?좏깮 醫낅ぉ肄붾뱶 湲곗? 怨꾩빟 ?ㅽ럺 ?숆린??
**?뚯씪**: `config/constants.py`, `main.py`, `strategy/position/position_tracker.py`, `strategy/entry/position_sizer.py`, `strategy/entry/entry_manager.py`, `strategy/exit/exit_manager.py`, `collection/kiwoom/investor_data.py`, `collection/cybos/investor_data.py`

**利앹긽**: UI?먯꽌 `KOSPI200 誘몃땲?좊Ъ`???좏깮?대룄 ?고????대????쇰컲?좊Ъ `pt_value=250,000` 諛?湲곕낯 二쇰Ц 肄붾뱶 媛?뺤쓣 ?좎??????덉뼱, ?먯씡쨌?ъ씠吏빧룹＜臾맞룹닔湲?議고쉶媛 ?쒕줈 ?ㅻⅨ 怨꾩빟??媛由ы궗 ?꾪뿕???덉뿀??

**?섏젙**:
- `config/constants.py` ??`get_contract_spec(code)` 異붽?
- `main.py::connect_broker()` ?먯꽌 UI ?좏깮 醫낅ぉ肄붾뱶瑜??곗꽑 ?곸슜?섍퀬, ?대떦 肄붾뱶濡?`pt_value`/怨꾩빟 ?쇰꺼 ?뺤젙
- `PositionTracker`, `PositionSizer`, `EntryManager`, `ExitManager`, `InvestorData` ???꾩옱 怨꾩빟 ?ㅽ럺/醫낅ぉ肄붾뱶 ?꾪뙆
- 誘몃땲?좊Ъ? `pt_value=50,000`, 理쒖냼 吏꾩엯 ?섎웾 3怨꾩빟 洹쒖튃 諛섏쁺

### 踰꾧렇 1: `cybos_autologin.py` ??`sys.exit(0)` 議곌린 醫낅즺

**?뚯씪**: `scripts/cybos_autologin.py` line 635

**利앹긽**: `_handle_mock_select_dialog()` ??紐⑥쓽?ъ옄 ?앹뾽 泥섎━ ??`sys.exit(0)` ?몄텧濡?STEP 5(?곌껐 ?湲?猷⑦봽)媛 ?ㅽ뻾?섏? ?딆븘 BAT ?뚯씪?먯꽌 `[ERROR] Auto-login failed.` 異쒕젰.

**?섏젙**: `sys.exit(0)` ??`return True` 濡?蹂寃? STEP 5媛 ?뺤긽 ?ㅽ뻾?섏뼱 `[OK] CybosPlus ?곌껐 ?깃났 (ServerType=1)` 異쒕젰.

### 踰꾧렇 2: `start_mireuk.bat` ??`%ERRORLEVEL%` 吏???뺤옣 踰꾧렇

**?뚯씪**: `start_mireuk.bat` line 113

**利앹긽**: Python ?먮룞 濡쒓렇???깃났 ?꾩뿉??`[ERROR] Auto-login failed.` 媛 怨꾩냽 異쒕젰??

**?먯씤**: Windows CMD `IF (...) IF %ERRORLEVEL% NEQ 0` 援ъ“?먯꽌 `%`???뚯떛 ?쒖젏???뺤옣?섏뼱 ?몃? `IF`??議곌굔媛?1)???대? `IF`??怨좎젙?? `IsConnect=0` 遺꾧린?먯꽌 autologin???ㅽ뻾?대룄 ?대? `IF`????긽 `1 NEQ 0 = true`.

**?섏젙**: `IF %ERRORLEVEL% NEQ 0` ??`IF !ERRORLEVEL! NEQ 0` (吏???뺤옣, `SETLOCAL EnableDelayedExpansion` ?대? ?좎뼵??.

### 踰꾧렇 3: Dashboard 醫낅ぉ肄붾뱶쨌?쒖옣援щ텇 ?좏깮 誘몄쁺??
**?뚯씪**: `dashboard/main_dashboard.py`

**利앹긽**: ?꾨줈洹몃옩 ?ъ떆????醫낅ぉ肄붾뱶 肄ㅻ낫諛뺤뒪媛 湲곕낯媛믪쑝濡?珥덇린?붾맖.

**?섏젙**: `data/ui_prefs.json`???좏깮媛????蹂듭썝. `_save_ui_prefs()` / `_restore_ui_prefs()` 硫붿꽌??異붽?. `blockSignals(True/False)`濡?蹂듭썝 以??쇰뱶諛?猷⑦봽 諛⑹?.

**?몃? 蹂寃?*:
- `import json` 異붽?
- `from config.settings import DATA_DIR` 異붽?
- `_UI_PREFS_FILE = os.path.join(DATA_DIR, "ui_prefs.json")` ?곸닔 異붽?
- `symbol_code` 湲곕컲 ????щ㎎(`version`, `market`, `symbol_code`, `symbol_text`) ?꾩엯
- `_on_symbol_changed()` ?앹뿉 `self._save_ui_prefs()` ?몄텧
- `_build_ui()` 肄ㅻ낫 ?ㅼ젙 ?꾨즺 ??`self._restore_ui_prefs()` ?몄텧

**異붽? ?먯씤 ?섏젙**:
- ?쒖옉 ??`self._on_symbol_changed(self.cmb_symbol.currentText())` 媛 蹂듭썝 ?꾩뿉 ?ㅽ뻾?섎ŉ 湲곕낯媛믪쓣 `ui_prefs.json`??癒쇱? ??ν븯??臾몄젣 ?뺤씤
- `_update_symbol_label()` 濡??쇰꺼 媛깆떊怨???μ쓣 遺꾨━?? ?쒖옉 吏곹썑 湲곕낯媛???뼱?곌린 ?쒓굅

### 踰꾧렇 4: ProfitGuard "?곸슜" 踰꾪듉 ?대┃ ???꾨줈洹몃옩 醫낅즺

**?뚯씪**: `dashboard/panels/profit_guard_panel.py`

**利앹긽**: Apply 踰꾪듉 ?대┃ ???꾨줈洹몃옩??利됱떆 醫낅즺??

**?먯씤**: `fetch_today_trades()`媛 `sqlite3.Row` 媛앹껜瑜?諛섑솚?섎뒗?? Python 3.7??`sqlite3.Row`??`.get()` 硫붿꽌?쒕? 吏?먰븯吏 ?딆쓬. `_run_simulation()` ?대??먯꽌 `AttributeError` 諛쒖깮 ??PyQt5 signal-slot ?덉쇅 ?꾪뙆 ??`QApplication` 醫낅즺.

**?섏젙**:
- `_rows_to_dicts()` static method 異붽? ??`sqlite3.Row` ??`dict` 蹂??(?됰퀎 try/except)
- `refresh()`, `_auto_refresh()` ?먯꽌 `self._today_trades` ?????蹂??- `_run_simulation()` ??`_run_simulation_inner()` 遺꾨━, ?몃? try/except濡??섑븨
- `_on_config_changed()` ?꾩껜 try/except濡??섑븨

### 寃利?
- `python -m py_compile dashboard/main_dashboard.py` ?듦낵
- PyQt ??쒕낫???ъ깮???ㅻ땲?レ쑝濡?`?쒖옣援щ텇/醫낅ぉ肄붾뱶` ??????숈씪 媛?蹂듭썝 ?뺤씤
- ?꾩옱 `data/ui_prefs.json` ??留덉?留??좏깮媛?????숈옉 ?뺤씤

---

## 2026-05-12 (17李???4-Layer ?섏씡 蹂댁〈 媛??(ProfitGuard) 援ы쁽 + ?뮥 ??쒕낫????

**Work**

湲덉씪 ?μ쨷 理쒕? ?꾩쟻 ?먯씡 +337留뚯썝??留덇컧 ??-166留뚯썝?쇰줈 諛섏쟾??臾몄젣瑜?遺꾩꽍?섍퀬, ?뺣낫???댁씡??蹂댁〈?섎뒗 4-Layer ProfitGuard ?쒖뒪?쒖쓣 援ы쁽?덈떎.

### ?ㅻ뒛 ?먯씡 遺꾩꽍 (20260512_TRADE.log)

| 泥?궛 ?쒓컖 | 諛⑺뼢 | ?먯씡 | ?댁쑀 |
|---|---|---|---|
| 10:13~10:22 | LONG횞4 | +??337留?(?꾩쟻 理쒓퀬?? | TP2 ?곗냽 |
| 10:28~12:46 | ?쇳빀 | 湲됯꺽 ?섎씫 | ?섎뱶?ㅽ넲 ?곗냽 |
| 15:10 | ?붿뿬 ?ъ???| 媛뺤젣 泥?궛 | ?ㅻ쾭?섏씠??湲덉? |
| 理쒖쥌 | ??| **-166留뚯썝** | 異붿꽭 諛섏쟾 ????ㅽ뙣 |

**?듭떖 臾몄젣**: 怨좎젏 ?ъ꽦 ?꾩뿉??吏꾩엯 湲곗????숈씪?섍쾶 ?좎??섏뼱 ?먯떎 ?곗냽 援ш컙?먯꽌 ?섎뱶?ㅽ넲 3?곕컻濡??댁씡 ?꾨? 諛섎궔.

### 援ы쁽: ProfitGuard 4-Layer ?ㅺ퀎

| ?덉씠??| ?대쫫 | 諛쒕룞 議곌굔 | ?④낵 |
|---|---|---|---|
| L1 | DailyPnlTrailingGuard | peak ??200留?+ ?꾩옱 ??peak 횞 (1-35%) | ?뱀씪 吏꾩엯 ?꾩쟾 ?뺤? |
| L2 | ProfitTierGate | 援ш컙蹂?理쒖냼 ?깃툒 ?붽뎄 (0?묬, 100?묬, 200?묪, 300?묨, 400留? 吏꾩엯 ?뺤?) | ?댁씡 援ш컙蹂?蹂댁닔??吏꾩엯 |
| L3 | AfternoonRiskMode | 150留? ?섏씡 + 13???댄썑 3??珥덇낵 吏꾩엯 ?쒕룄 | ?ㅽ썑 吏꾩엯 ?잛닔 ?쒗븳 |
| L4 | ProfitProtectionCB | 150留? ?섏씡 以?2?곗냽 ?먯떎 | 利됱떆 吏꾩엯 ?뺤? |

**?쒕??덉씠??寃곌낵 (湲덉씪 ?곗씠??**:
- 梨뷀뵾??媛???놁쓬): **-1,664,257??*
- 梨뚮┛?(L1+L4 ?곸슜): **??+456,651??* (12:46 ?댄썑 吏꾩엯 李⑤떒?쇰줈 ?먯떎 諛⑹뼱)

### ?좉퇋 ?뚯씪

| ?뚯씪 | ??븷 |
|---|---|
| `strategy/profit_guard.py` | 4-Layer ProfitGuard ?듭떖 濡쒖쭅 + `ProfitGuardConfig` + `simulate()` |
| `dashboard/panels/profit_guard_panel.py` | ?뮥 ?섏씡 蹂댁〈 ?? PnL DNA ?쒓컖??+ ?ㅼ젙 ?щ씪?대뜑 + 梨뷀뵾??梨뚮┛? 鍮꾧탳 ?뚯씠釉?+ ?밴툒 ?쒖븞 |

### ?섏젙 ?뚯씪

| ?뚯씪 | 蹂寃?|
|---|---|
| `main.py` | STEP 7 吏꾩엯 ??`profit_guard.is_entry_allowed()` 寃뚯씠???쎌엯 |
| `main.py` | `_post_exit()`: `profit_guard.on_trade_close()` ?몄텧 |
| `main.py` | `_execute_entry()`: `profit_guard.on_entry()` ?몄텧 |
| `main.py` | `daily_close()`: `profit_guard.reset_daily()` ?몄텧 |
| `main.py` | `_refresh_pnl_history()`: `dashboard.refresh_profit_guard()` ?몄텧 |
| `dashboard/main_dashboard.py` | "?뮥 ?섏씡 蹂댁〈" ??異붽? + `set_profit_guard()` / `refresh_profit_guard()` ?대뙌??|

### ??쒕낫????援ъ꽦

1. **?곹깭 ?뱀뀡**: L1~L4 諛곗?(珥덈줉/鍮④컯) + 5媛??듭떖 吏??+ PnL DNA 留됰? (PnL 異붿씠?졖룻뵾??룻븯??諛붾떏??
2. **?ㅼ젙 ?뱀뀡**: ?몃젅??鍮꾩쑉 ?щ씪?대뜑 (15~60%), 紐⑤뱺 ?뚮씪誘명꽣 ?ㅽ?諛뺤뒪, Apply/Reset 踰꾪듉
3. **鍮꾧탳 ?뱀뀡**: 梨뷀뵾??vs 梨뚮┛? 6???뚯씠釉?(珥앹넀?돠룰굅?섏닔쨌?밸쪧쨌理쒕??쇳겕쨌MDD쨌李⑤떒嫄곕옒) + 李⑤떒 嫄곕옒 紐⑸줉
4. **?쒖븞 ?뱀뀡**: 3媛吏 梨뚮┛? 蹂??(怨듦꺽??0%쨌?쒖?35%쨌蹂댁닔??5%) + ?⑷툑 ?쒓컙? 留됰? 李⑦듃 + 李⑤떒 濡쒓렇

### ?⑥? 寃利?
- V-PG1~V-PG5: ?μ쨷 L1~L4 ?ㅼ젣 諛쒕룞 ?뺤씤 + UI ?곗씠??諛섏쁺

---

## 2026-05-12 (15李???梨뷀뵾???꾩쟾???쒖뒪???꾨㈃ 援ы쁽 + MicroRegimeClassifier ?곌껐)

## 2026-05-12 (16李???WARN ?몄씠利?2?④퀎 媛먯텞: Cybos + BalanceUI/Refresh ?덉씠?몃━諛?INFO)

**Work**

?ㅻ뒛 ?μ쨷 濡쒓렇 遺꾩꽍 ??諛섎났??WARNING ??＜ 援ш컙??肄붾뱶 ?덈꺼?먯꽌 2?④퀎濡??щ텇瑜섑뻽??

### 1李?(Cybos API 怨꾩링)

| ?뚯씪 | 蹂寃?|
|---|---|
| `collection/cybos/api_connector.py` | `_system_info_throttled()` 異붽? (?ㅻ퀎 理쒖냼 媛꾧꺽) |
| `collection/cybos/api_connector.py` | `[CybosInvestorRaw] ... TR ?꾨낫 ?놁쓬` WARNING ??10遺??덉씠?몃━諛?INFO |
| `collection/cybos/api_connector.py` | `[CybosDailyPnl] profit_rate ?댁긽媛? ?щ벑湲? `>200%`留?WARNING, `50~200%`??10遺??덉씠?몃━諛?INFO |

### 2李?(硫붿씤 ?고???Balance 怨꾩링)

| ?뚯씪 | 蹂寃?|
|---|---|
| `main.py` | `_ts_should_emit_throttled`, `_ts_system_info_throttled`, `_ts_logger_info_throttled` 異붽? |
| `main.py` | `[BalanceRefresh] trigger/request/result` 怨꾩뿴 WARNING ???덉씠?몃━諛?INFO |
| `main.py` | `[BalanceUI] raw/computed/push/force flat/skipped empty` 諛섎났 WARNING ???덉씠?몃━諛?INFO |
| `main.py` | ?ㅼ젣 ?μ븷??寃쎄퀬(`request returned None`, empty account ????WARNING ?좎? |

### ?④낵

- `WARN.log`?먯꽌 遺꾨떦 諛섎났 吏꾨떒??硫붿떆吏??鍮꾩쨷????텛怨? ?ㅼ젣 ????꾩슂 ?대깽??CRITICAL/?ㅼ옣??WARNING) 媛?쒖꽦???믪???
- 寃쎄퀬 ?쇰줈瑜?以꾩씠硫댁꽌??吏꾨떒 ?뺣낫??INFO 梨꾨꼸濡??좎??덈떎.

### ?⑥? ?꾩냽

- ?덉씠?몃━諛?媛꾧꺽(30/60/120珥? 10遺? ?댁쁺 ?쒖?媛??뺤젙
- ?μ쨷 ?ш?????CB HALTED ?곹깭 ?곸냽 蹂듭썝 ?꾨씫 ?щ?????곹샇?묒슜 ?먭?

---

## 2026-05-12 (15李???梨뷀뵾???꾩쟾???쒖뒪???꾨㈃ 援ы쁽 + MicroRegimeClassifier ?곌껐)

**Work**

Champion-Challenger ?쒖뒪?쒖쓽 ?듭떖 誘몄셿??遺遺꾩쓣 諛쒓껄쨌?섏젙?덈떎.

### ?듭떖 諛쒓껄: MicroRegimeClassifier 誘몄뿰寃?
`main.py`??`regime_classifier.classify_micro(adx_dummy=22.0, ...)` 濡?4-?덉쭚 ?⑥닚 遺꾨쪟湲곕? ?곌퀬 ?덉뿀?? `MicroRegimeClassifier` (5-?덉쭚, ADX ?ㅺ퀎?? ?덉쭊 媛먯?)媛 `collection/macro/micro_regime.py`???꾩꽦???덉뿀吏留??곌껐?섏? ?딆븯?? ADX=22.0 怨좎젙媛믪쑝濡??명빐 ??긽 "?쇳빀" ?덉쭚留??먯젙?섏뿀怨? ?덉쭊 ?덉쭚? ??踰덈룄 諛쒕룞?섏? ?딆븯??

### 援ы쁽 紐⑸줉

| # | ?뚯씪 | ?댁슜 |
|---|---|---|
| C1 | `main.py` | `MicroRegimeClassifier` import + `__init__` ?몄뒪?댁뒪??|
| C2 | `main.py` STEP 4 | `adx_dummy=22.0` ?쒓굅 ??`push_1m_candle()` ?ㅽ샇異?(ADX ?ㅺ퀎?걔?-?덉쭚) |
| C3 | `main.py` STEP 4 | `dashboard.update_micro_regime()` + ?덉쭚 蹂寃???SIGNAL 濡쒓렇 |
| C4 | `main.py` `_MICRO_EN` | `"?덉쭊": "EXHAUSTION"` 異붽? (strategy_params 議고쉶 ?꾨씫 ?닿껐) |
| C5 | `main.py` daily_close | `micro_regime_clf.reset_daily()` 異붽? |
| C6 | `main.py` STEP 6 짠20 | RegimeChampGate ??梨뷀뵾??None ?덉쭚 吏꾩엯 李⑤떒 寃뚯씠??|
| C7 | `config/strategy_params.py` | EXHAUSTION ?덉쭚 ?ㅻ쾭?쇱씠??3醫?(RISK_ON쨌NEUTRAL쨌RISK_OFF횞?덉쭊=9999) |
| C8 | `dashboard/main_dashboard.py` | `lbl_micro_regime` ?ㅻ뜑 諛곗? + `update_micro_regime()` ?대뙌??硫붿꽌??|
| C9 | `dashboard/panels/challenger_panel.py` | `_lbl_cur_regime` ?곹깭諛?+ `update_micro_regime()` 硫붿꽌??|
| C10 | `dev_memory/CHALLENGER_SYSTEM_PLAN.md` | ?꾨㈃ ?ъ옉?????꾨즺 泥댄겕由ъ뒪?맞룹꽕怨??곸꽭쨌寃利?怨꾪쉷 |
| C11 | `dev_memory/CURRENT_STATE.md` | 15李??ㅻ뜑 + 梨뷀뵾???꾩쟾???쒖뒪???뱀뀡 異붽? |

### RegimeChampGate [짠20] ?ㅺ퀎

- `challenger_engine.registry.get_regime_champion(micro_regime)` 諛섑솚媛?遺꾧린:
  - `None` ??`direction=0, grade="X"` (吏꾩엯 李⑤떒) + SIGNAL 濡쒓렇
  - `CHAMPION_BASELINE_ID` ??湲곕낯 梨뷀뵾???ъ슜 (?숈긽釉??좏샇 洹몃?濡?
  - 湲고? ID ???꾨Ц媛 梨뷀뵾???쒖꽦 (?숈긽釉??좏샇 蹂닿컯 濡쒓렇)
- ?덉쭊(EXHAUSTION) ?덉쭚? 湲곕낯 champion=None?대씪 吏꾩엯 遺덇? (?섎룞 ?밴꺽 ?꾩슂)

### 誘명빐寃???ぉ

- V-C1~V-C4: ?덉쭊 ?ㅻ컻?쇑텴ate 李⑤떒쨌Shadow WARNING쨌諛곗? 媛깆떊 ?뺤씤 (?ㅻ뜲?댄꽣 ?꾩슂)

---

## 2026-05-12 (14李???濡쒓렇 遺꾩꽍 + 6醫?踰꾧렇 ?섏젙)

**Work**

濡쒓렇 遺꾩꽍 (`logs/20260512_*.log`) 湲곕컲?쇰줈 6醫?踰꾧렇瑜?諛쒓껄쨌?섏젙?덈떎.

### ?섏젙 紐⑸줉

| # | ?뚯씪 | ?섏젙 ?댁슜 |
|---|---|---|
| B56 | `learning/meta_confidence.py` | `SGDClassifier(loss="log_loss")` ??`loss="log"` (sklearn 1.0.2 ?명솚) |
| D35 | `config/secrets.py` | `ACCOUNT_NO = "7034809431"` ??`"333042073"` (Kiwoom ?붿뿬媛??쒓굅) |
| B57 | `main.py` | ExitCooldown 以묐났 濡쒓렇 ?쒓굅 (`_exit_cooldown_applied_this_fill` ?뚮옒洹몃줈 以묐났 寃쎈줈 李⑤떒) |
| B58 | `main.py` | CB HALTED ?곹깭?먯꽌 Sizer/Checklist 怨꾩궛???듭젣?섏? ?딅뜕 臾몄젣 ?섏젙 (`is_entry_allowed()` 寃뚯씠??異붽?) |
| B58b | `main.py` | ?湲?heartbeat??CB ?곹깭 ?쒖떆 異붽? (`_log_waiting_status`) |
| B59 | `strategy/position/position_tracker.py` | TRADE.log ?쒓? 源⑥쭚 3怨??섏젙 (line 464: TP1 arm, line 487: assert 硫붿떆吏, line 513: TP1 蹂댄샇?꾪솚) |
| B60 | `collection/cybos/api_connector.py` | ?붽퀬 sanity check ??`liquidation_eval=0 ???듭씪?덊긽湲??泥???WARNING`, `profit_rate > 짹50%` ?댁긽媛?寃쎄퀬 異붽? |

### 濡쒓렇 吏꾨떒 ?붿빟

- **LEARNING.log**: 09:17~?λ쭏媛??대궡 `The loss log_loss is not supported` ??MetaConf 硫뷀? ?덉씠???꾨Т?ν솕. B56?쇰줈 ?닿껐.
- **WARN.log**: 怨꾩쥖踰덊샇 遺덉씪移?(`7034809431 not in session`), CybosInvestorRaw 105???곗냽 ?꾨낫 ?놁쓬(09:00~10:44), ExitCooldown 以묐났(吏꾩엯쨌泥?궛留덈떎 2??, CB ??HALT 10:20:59 諛쒕룞.
- **TRADE.log**: Sizer媛 CB HALT ?댄썑?먮룄 怨꾩냽 怨꾩궛쨌濡쒓렇 異쒕젰, ?붽퀬 480,707,716 怨좎젙(?섎（ 醫낆씪), ?쒓? 源⑥쭚.
- **SIGNAL.log**: CB HALT ?댄썑?먮룄 `conf=100.0%` ?좏샇 ?앹꽦 吏??(吏꾩엯? ?놁뿀?쇰굹 濡쒓렇 ?몄씠利?.
- **二쇱슂 愿李?*: MetaConf ?ㅻ쪟 ??SGD ?⑤씪?명븰??誘몃룞????30遺??뺥솗??19% ??CB ???뱀씪 ?뺤? ?멸낵愿怨??뺤씤.

### 誘명빐寃???ぉ

- `CybosInvestorRaw ?꾨낫 ?놁쓬` 1?쒓컙45遺?媛?(09:00~10:44): `CpSysDib.CpSvrNew7212`媛 ???쒖옉 吏곹썑 誘몄쓳?? 7嫄?嫄곕옒媛 ??媛??덉뿉??諛쒖깮. ?먯씤 誘명솗?????ㅼ쓬 ?몄뀡 異붽? 議곗궗.
- `珥앺룊媛?섏씡瑜? ?꾨뱶媛 KRW(?듭씪?덊긽?꾧툑)瑜??닿퀬 ?덉뼱 ?꾨뱶紐낃낵 ?섎? 遺덉씪移????섎룄???ㅺ퀎?대굹 WARNING 濡쒓렇 異붽?(B60) ?꾨즺.

---

## 2026-05-11 (13李???cybos_autologin.py ?꾩꽦 + ?뺤긽 ?숈옉 ?뺤씤)

**Work**
- `scripts/cybos_autologin.py` ?ㅽ뻾 ?뚯씪 蹂寃? `_ncStarter_.exe` ??`ncStarter.exe /prj:cp` (諛붾줈 媛湲??띿꽦 湲곗?)
  - `CYBOS_EXE = r"C:\DAISHIN\STARTER\ncStarter.exe"`, `CYBOS_ARGS = "/prj:cp"` 遺꾨━
- 紐⑥쓽?ъ옄 ?앹뾽 ?湲?`MOCK_POPUP_MIN_WAIT`: 20s ??**10s**
- 10珥??湲??꾨즺 ???먮쫫 ?뺤젙:
  1. `send_keys("{ENTER}")` ??Enter ?낅젰
  2. 3珥??湲?  3. `sys.exit(0)` ???ㅽ겕由쏀듃 醫낅즺
  - 以묎컙??李??먯??섎㈃ `(1416, 645)` 踰꾪듉 ?대┃ ???곌껐/李??뚮㈇ ??利됱떆 醫낅즺 (湲곗〈 濡쒖쭅 ?좎?)
- **?뺤긽 ?숈옉 ?뺤씤** ??`python scripts/cybos_autologin.py` ?ㅽ뻾 ??紐⑥쓽?ъ옄 濡쒓렇???꾨즺

**Key coordinates (?뺤젙)**
- 鍮꾨?踰덊샇 ?낅젰 醫뚰몴: `(971, 695)`
- 紐⑥쓽?ъ옄 ?묒냽 踰꾪듉: `(1416, 645)`

**Remaining**
- `start_mireuk.bat` ?먯꽌 autologin ?몄텧 ?곌껐 ?뺤씤

---

## 2026-05-11 (12李????ъ옄???섍툒 TR ?뺤젙 + ?ㅼ씠踰꾩쟾???⑤꼸 UI ?뺥빀??

**Work**
- TR ?먯깋: `scripts/run_cybos_investor_discovery.py` (43媛??꾨낫 ?쇨큵 ?꾨줈釉? ?ㅽ뻾 ??`CpSysDib.CpSvrNew7212` ?뺤젙 (score=428, likely_investor_grid). ?덉??ㅽ듃由?555媛?ProgID ?닿굅 ?ы븿.
- `scripts/_probe_7212_dates.py` ?ㅽ뻾 ??idx0=N??N媛쒖썡 湲곌컙 肄붾뱶???뺤씤. idx0=1(理쒓렐 1媛쒖썡) 梨꾪깮.
- `collection/cybos/api_connector.py`:
  - `_FUTURES_INVESTOR_NAME_MAP` 異붽? (?쒓? ?ъ옄?먮챸 ??INVESTOR_KEYS)
  - `request_investor_futures()` candidates 1?쒖쐞: `("CpSysDib.CpSvrNew7212", [(0, 1)])`
  - New7212 ?꾩슜 ?뚯떛 遺꾧린: row[0]=?ъ옄?먮챸, row[3]=?좊Ъ, row[6]=肄? row[9]=??  - `request_program_investor()` candidates: `Dscbo1.CpSvr8119`, `Dscbo1.CpSvrNew8119` (?덉??ㅽ듃由?寃利? 異붽?. ?꾩껜 0 ?ㅻ뜑 ??skip.
- `collection/cybos/investor_data.py`:
  - `fetch_futures_investor()`: call_nets/put_nets ??`_call/_put` 諛섏쁺, `option_flow_supported` ?먮룞 ?쒖꽦??  - `get_panel_data()`: rt_call/rt_put/fi_call/fi_put/rt_bias/fi_bias ?섎뱶肄붾뵫 0 ???ㅼ젣媛??곌껐 [B54]
  - ?곹깭 ?띿뒪?? option_flow_supported ??"futures/option flow live" ?먮룞 諛섏쁺
  - reset_daily(): `_option_flow_reason` 珥덇린媛?蹂듭썝
- `dashboard/main_dashboard.py`:
  - ??컻???좏샇 ?됱긽 ?꾩쟾 ?섏젙: `'留ㅼ닔'`?믩묠媛꾩깋(?섎씫?좏샇), `'留ㅻ룄'`?믪큹濡앹깋 [D33]
- `config/constants.py`: `CORE_FEATURES` `"ofi_imbalance"` ??`"ofi_norm"` ?듭씪 [B55]
- ?좉퇋 ?ㅽ겕由쏀듃: `scripts/_probe_8119_fields.py` (??以?Dscbo1.CpSvr8119 ?꾨뱶 ?덉씠?꾩썐 ?뺤씤??

**Validated results (??以??ㅻ뜲?댄꽣)**
- ?몄씤 ?좊Ъ ?쒕ℓ?? -131,592 / 媛쒖씤: +43,521 / 湲곌?: +77,015 (怨꾩빟?? 1媛쒖썡 ?꾩쟻)
- ?ㅼ씠踰꾩쟾?? -175,113 = -131,592 - 43,521 怨꾩궛 ?쇱튂
- ATM 援ш컙鍮? ?몄씤 17%, 媛쒖씤 43%, 湲곌? 41% (肄????덈?媛?湲곕컲)
- 誘멸껐?쒖빟?? 195,996 (FutureCurOnly ?ㅻ뜑 14踰?
- ?꾨줈洹몃옩 李⑥씡/鍮꾩감?? 0 (??留덇컧 ???뺤긽)
- SHAP ?뚮씪誘명꽣 以묒슂??0.0%: GBM 誘명븰???곹깭, ?뺤긽

**Remaining follow-up**
- `_probe_8119_fields.py` ??以?09:00~15:30) ?ㅽ뻾 ??h[0~5] ?덉씠?꾩썐 寃利?- ?ㅼ젣 ?뚯씠?꾨씪??留ㅻ텇 ?낅뜲?댄듃?먯꽌 ?ъ옄???섍툒 ?곗씠???먮쫫 ?뺤씤 (?湲겸넂?ㅼ닔移??꾪솚)

## 2026-05-11 (Cybos balance / learning / UI sync stabilization)

**Work**
- Fixed the Cybos startup crash in `main.py` caused by formatting a `None` realized-pnl value during balance logging.
- Hardened `learning/meta_confidence.py` so invalid or ragged meta feature vectors are normalized or rejected before buffering/fitting.
- Updated `strategy/entry/position_sizer.py` and `main.py` so sizing now uses the latest Cybos balance summary instead of a fixed `100,000,000` fallback.
- Added `CpTd6197` daily pnl/account-summary fetch in `collection/cybos/api_connector.py` and routed validation logs into `SYSTEM.log`.
- Verified and documented the current Cybos daily-pnl mapping rule: raw `CpTd6197` headers are the source of truth; HTS is reference-only.
- Replaced the dashboard `?ъ???蹂듭썝` control with `?붽퀬 ?덈줈怨좎묠` and bound `F5` to the balance-only refresh path.
- Fixed final-exit UI lag by clearing dashboard balance rows immediately on confirmed `FLAT` and retrying broker refresh after exit.

**Validated results**
- `MetaConf` repeated training error (`setting an array element with a sequence`) disappeared after restart.
- `[Sizer] ?붽퀬=` now reflects broker values such as `500,000,000`.
- `SYSTEM.log` now records:
  - `[CybosDailyPnl] ...`
  - `[CybosDailyPnlHeaders] ...`
- Verified current `CpTd6197` mapping on 2026-05-11:
  - `header 1` = deposit cash
  - `header 2` = next-day deposit cash
  - `header 5` = previous-day pnl
  - `header 6` = today's realized pnl
  - `header 9` = liquidation evaluation amount
- Confirmed current mock-environment behavior:
  - `header 2 == header 9`
  - `header 5 == 0`

**Remaining follow-up**
- Re-run one TP2/full-exit case and confirm the new `force flat rows` path removes stale balance rows immediately.

## 2026-05-10 (Cybos Plus refactor validation / session close-out)

**Work**
- Implemented real `CybosAPI` runtime path under `collection/cybos/`:
  - `CpUtil.CpCybos` connection check
  - `CpTdUtil.TradeInit`
  - `CpTd0723` futures balance
  - `CpTd6831` futures market order path
  - `CpFConclusion` fill subscription
  - `FutureCurOnly` / `FutureJpBid` realtime subscription wrapper
- Added `scripts/check_cybos_session.py` to verify Cybos session, account, balance, snapshot, realtime, and optional order/fill flow from an admin 32-bit Python prompt.
- Added `start_mireuk_cybos_test.bat` so Cybos can be test-driven without changing the default Kiwoom launcher or global broker setting.
- Verified Cybos session manually on 32-bit Python:
  - `IsConnect=1`
  - `ServerType=1`
  - `TradeInit=0`
  - account list includes `333042073`
- Verified Cybos mock balance behavior:
  - `CpTd0723` returns `Count=0` with `97007` no-data message when the mock account has no futures position
  - startup sync now safely interprets this as `FLAT`
- Corrected `FutureMst` header index mapping after live snapshot check:
  - `price/open/high/low` now use `71/72/73/74`
  - `cum_volume` now uses `75`
  - ask/bid top levels now use `37/54`
  - ask/bid qty1 now use `42/59`
- Fixed runtime account mismatch on `main.py` Cybos startup:
  - if `config/secrets.py` account is not present in the active Cybos SignOn account list, runtime now switches to the logged-in Cybos account automatically
  - this resolved `CpTd0723 InputCheck Type:0 account number error`
- Ran `main.py` through the Cybos test launcher and confirmed:
  - UI boot completes
  - broker startup sync completes
  - Cybos balance sync reaches `FLAT`
  - realtime object starts
  - Qt event loop enters normally

**Observed issues**
- `Could not parse stylesheet ...` warnings appear during dashboard startup. These are UI stylesheet parsing warnings, not Cybos COM connection failures.
- Cybos investor-data path is still a zero/no-op scaffold, so strategy/UI values that depend on investor flow are not yet broker-native on Cybos.
- Realtime tick/hoga and order/fill loops are still only partially validated because current verification was done on `2026-05-10` (Sunday, market closed).

**Validation summary**
- Connection: verified
- Balance TR (`CpTd0723`): verified
- Snapshot (`FutureMst`): verified after field-index correction
- Realtime subscription wiring: startup verified, live market event flow still pending
- Order/fill (`CpTd6831` + `CpFConclusion`): wiring implemented, live mock order validation still pending

## 2026-05-11 (Cybos test launcher log review)

**Work**
- Reviewed the latest run results around `start_mireuk_cybos_test.bat` and compared them against the existing Cybos follow-up memo.
- Confirmed that the Cybos launcher path entered the main UI and Qt loop successfully again.
- Confirmed runtime account fallback worked as intended:
  - configured account `7034809431`
  - active Cybos session account `333042073`
- Confirmed Cybos startup balance sync behaved as expected for mock no-position state:
  - `CpTd0723`
  - `DibStatus=0`
  - `97007` no-data message
  - interpreted as `FLAT`

**Observed evidence**
- `SYSTEM` showed:
  - `[System] cybos ?ㅼ떆媛??섏떊 ?쒖옉 ??A0166`
  - repeated waiting status lines saying `FC0 ?ㅼ떆媛????湲?以?
- `MICRO` log still produced tick-derived updates after `09:03`, including:
  - `MICRO-TICK #1` at `09:03:45`
  - `MICRO-TICK #100` at `09:03:52`
  - `MICRO-TICK #13300` at `09:23:58`
- This means today's Cybos run does **not** look like a clean "no realtime at all" failure.

**Open inconsistency**
- The UI/system status message is still Kiwoom-specific (`FC0`) and is misleading during Cybos runs.
- `MICRO-MINUTE` repeatedly logged `ts=2026-05-11 09:03:00` deep into the session, so minute-close progression or downstream handoff still needs focused validation.
- `HOGA.log` only contained the earlier Kiwoom-run block from `08:42~08:54`, so Cybos hoga visibility is still not cleanly separated in current logging.

**Interpretation**
- Current best reading is:
  - Cybos realtime likely reached at least part of the runtime graph
  - but broker-aware status messaging and/or minute-pipeline observability are still incomplete
  - therefore "complete realtime verification" should remain open, but the risk has narrowed from "no data" to "partial flow / incorrect interpretation"

## 2026-05-11 (Cybos follow-up implementation)

**Work**
- Updated `main.py` waiting-status text to be broker-aware instead of always referring to Kiwoom `FC0`.
- Added Cybos `BAR-CLOSE` system logging in `collection/cybos/realtime_data.py` so minute-close progression can be observed directly in `SYSTEM.log`.
- Added `scripts/check_cybos_realtime.py` for UI-independent Cybos realtime verification.

**Why this matters**
- Previous Cybos runs could look like "no realtime" from `SYSTEM` alone because the waiting text still referenced Kiwoom FC0 semantics.
- Cybos also lacked a direct `BAR-CLOSE` system log, which made it harder to distinguish:
  - no realtime
  - realtime without minute close
  - minute close happening but downstream interpretation failing

**Verification**
- `python -m py_compile main.py collection/cybos/realtime_data.py scripts/check_cybos_realtime.py`

**Next**
- Run `scripts/check_cybos_realtime.py` during KRX hours.
- Compare:
  - script tick/hoga counts
  - `SYSTEM.log` Cybos `BAR-CLOSE`
  - `MICRO-MINUTE` timestamp progression

## 2026-05-11 (Cybos realtime script validation)

**Work**
- Ran `python scripts/check_cybos_realtime.py --listen-sec 20` from the project root during market hours.

**Observed result**
- `IsConnect = 1`
- `TradeInit = 0`
- realtime code resolved to `A0166`
- snapshot query succeeded
- tick count `71`
- hoga count `228`
- final status `PASS`

**Interpretation**
- Cybos broker-level realtime receipt is now directly verified for both:
  - `FutureCurOnly`
  - `FutureJpBid`
- This materially reduces uncertainty around the Cybos COM/session layer.
- Remaining debugging focus should move to:
  - `main.py` runtime interpretation
  - Cybos minute-close progression
  - `MICRO-MINUTE` timestamp behavior

## 2026-05-08 (10李? - ?먮룞醫낅즺 ?ъ떎??諛⑹? + 遊됱감???쒖씤???좉? 媛쒖꽑

**?묒뾽**
- `main.py`?먯꽌 ?뱀씪 ?먮룞醫낅즺媛 ?대? ?앸궃 ???섎룞 ?ъ떆?묓빐???ㅼ떆 `daily_close()`? `_auto_shutdown()`???ㅽ뻾?섏? ?딅룄濡?蹂듦뎄/媛??濡쒖쭅??蹂닿컯?덈떎.
- ?몄뀡 蹂듭썝 ??`auto_shutdown_done_date == today` ?닿퀬 ?λ쭏媛??댄썑硫?`_daily_close_done = True`源뚯? ?④퍡 ?명똿?섎룄濡??섏젙?덈떎.
- `daily_close()` 珥덉엯?먮룄 媛숈? ?좎쭨 ?ъ떎??諛⑹? 媛?쒕? 異붽??? 蹂듦뎄 ?곹깭媛 ?붾뱾?ㅻ룄 ?뱀씪 ?λ쭏媛???以묐났 醫낅즺媛 ?ㅼ떆 ?ㅽ뻾?섏? ?딅룄濡??댁쨷 諛⑹뼱瑜??ｌ뿀??
- `dashboard/main_dashboard.py` 遺꾨큺/遊됱감?몄뿉 ?곗륫 10遊??щ갚??異붽???留덉?留?遊됯낵 吏꾩엯/泥?궛 留덉빱媛 媛?μ옄由ъ? 遺숈? ?딅룄濡?媛쒖꽑?덈떎.
- 吏꾩엯 LONG/SHORT 留덉빱瑜?????諛곗????ㅽ??쇰줈 諛붽씀怨? 留덉빱 寃뱀묠 ?뚰뵾 濡쒖쭅???ｌ뼱 媛숈? 遊?洹쇱젒 媛寃⑸??먯꽌???쒖씤?깆쓣 ?믪???
- `SL` ?쇰꺼移⑹? ??긽 ?꾨옒履? `LONG` ?쇰꺼? ??긽 ?꾩そ?쇰줈 ??媛뺥븯寃?遺꾨━?섎룄濡??ㅽ봽??洹쒖튃??怨좎젙?덈떎.
- 遊됱감???⑥텞?ㅻ뒗 ?댁젣 ?좉? 諛⑹떇?쇰줈 ?숈옉?? ?ㅼ떆 ?꾨Ⅴ硫??덈룄?곌? ?ロ엳?꾨줉 諛붽엥??

**諛섏쁺**
- `main.py`
  - `_restore_auto_shutdown_state()`???뱀씪 ?λ쭏媛??댄썑 `_daily_close_done` 蹂듦뎄 異붽?
  - `daily_close()` 珥덉엯??`auto_shutdown_done_date == today` ?ъ떎??李⑤떒 媛??異붽?
- `dashboard/main_dashboard.py`
  - `MinuteChartCanvas.RIGHT_PADDING_BARS = 10` 異붽?
  - 罹붾뱾/異?留덉빱/?몃젅?대뱶 ?ㅽ뙩 ?뚮뜑留곸쓣 `?ㅼ젣 遊???+ ?곗륫 ?⑤뵫` 湲곗??쇰줈 ?뺣젹
  - 吏꾩엯 留덉빱 ?ㅽ???媛쒗렪, 留덉빱 異⑸룎 ?뚰뵾 濡쒖쭅 異붽?
  - `LONG` ?쇰꺼 ?꾩そ 怨좎젙, `SL` ?쇰꺼移??꾨옒履?怨좎젙
  - `toggle_minute_chart_dialog()`瑜??닿린/?リ린 ?좉? ?숈옉?쇰줈 蹂寃?
**寃利?*
- `python -m py_compile main.py`
- `python -m py_compile dashboard/main_dashboard.py`

**?ㅼ쓬 ?ㅼ슫???뺤씤 ?ъ씤??*
- 媛숈? ?좎쭨 ?λ쭏媛??댄썑 ?섎룞 ?ъ떆?????먮룞 醫낅즺 ?뚮┝怨??꾨줈洹몃옩 醫낅즺媛 ?ㅼ떆 ?ㅽ뻾?섏? ?딅뒗吏 ?뺤씤
- 遊됱감?몄뿉??留덉?留?遊??곗륫 ?щ갚??10遊??섏??쇰줈 ?좎??섎뒗吏 ?뺤씤
- `LONG` 吏꾩엯 留덉빱? `SL` 移⑹씠 媛숈? 遊됱뿉??寃뱀튌 ?????꾨옒 遺꾨━媛 異⑸텇?쒖? ?뺤씤
- 遊됱감???⑥텞???ъ엯????李쎌씠 利됱떆 ?ロ엳?붿? ?뺤씤

## 2026-05-08 (9李? - 1怨꾩빟 TP1 蹂댄샇?꾪솚 ?좏깮??+ 泥?궛愿由????섎룞泥?궛 ?곌껐

**?묒뾽**
- `main.py`, `strategy/position/position_tracker.py`?먯꽌 1怨꾩빟 TP1 ?꾨떖 ???꾨웾泥?궛 ???蹂댄샇?꾪솚?쇰줈 諛붽씀??寃쎈줈瑜??좎??섎릺, 蹂댄샇諛⑹떇??`蹂몄젅蹂댄샇 / 蹂몄젅+alpha / ATR 湲곕컲 蹂댄샇?댁씡` 3媛?紐⑤뱶濡??좏깮 媛?ν븯寃??뺤옣?덈떎.
- ?좏깮??TP1 蹂댄샇?꾪솚 紐⑤뱶??`data/session_state.json`??`tp1_single_contract_mode`濡????蹂듭썝?섎룄濡??곌껐?덈떎.
- `dashboard/main_dashboard.py` 泥?궛愿由???뿉 TP1 蹂댄샇?꾪솚 踰꾪듉 3媛쒖? ?ㅻ챸 ?댄똻??異붽??덈떎.
- 媛숈? ??쓽 `33% / 50% / ?꾨웾 泥?궛` 踰꾪듉???ㅼ젣 ?섎룞泥?궛 二쇰Ц 踰꾪듉?쇰줈 ?곌껐?덈떎.
- 1怨꾩빟 ?ъ??섏뿉??`33%` ?먮뒗 `50%`瑜??뚮????뚮뒗 二쇰Ц 吏곸쟾 ?먮룞?쇰줈 `?꾨웾泥?궛`?쇰줈 ?밴꺽?섎룄濡?泥섎━?덈떎.
- ?섎룞 遺遺꾩껌?곗? `EXIT_MANUAL_PARTIAL` pending kind濡?遺꾨━???먮룞 TP1/TP2 ?뚮옒洹몄? ?꾩쿂由?寃쎈줈媛 ?욎씠吏 ?딅룄濡?援ъ꽦?덈떎.
- TP1 蹂댄샇?꾪솚 UI 異붽? 以?諛쒖깮???쒓? 源⑥쭚? ??臾몄옄?댁쓣 ?좊땲肄붾뱶 ?댁뒪耳?댄봽 臾몄옄?대줈 移섑솚???덉젙?뷀뻽??

**諛섏쁺**
- `dashboard/main_dashboard.py`
  - `ExitPanel.sig_tp1_protect_mode_changed`, `sig_manual_exit_requested` 異붽?
  - TP1 蹂댄샇?꾪솚 踰꾪듉 3醫?+ ?댄똻 + ?좏깮 ?ㅽ???異붽?
  - ?섎룞泥?궛 踰꾪듉 3醫낆쓣 ?ㅼ젣 ?쒓렇?먮줈 ?곌껐?섍퀬, ?ъ????놁쓣 ??鍮꾪솢?깊솕
- `main.py`
  - `_on_tp1_protect_mode_changed()` / `_restore_tp1_protect_mode_setting()` 異붽?
  - `_on_manual_exit_requested()` 異붽?
  - `_ts_handle_exit_fill()`??`EXIT_MANUAL_PARTIAL` 遺꾧린 異붽?
  - 1怨꾩빟 TP1 蹂댄샇?꾪솚 ?ㅽ뻾 ???좏깮 紐⑤뱶? 蹂댄샇??쓣 濡쒓렇???④린?꾨줉 蹂닿컯
- `strategy/position/position_tracker.py`
  - `arm_tp1_single_contract_with_mode()` 異붽?

**寃利?*
- `python -m py_compile main.py dashboard/main_dashboard.py strategy/position/position_tracker.py` ?듦낵
- UI ?쒓? 源⑥쭚 ?섏젙 ??`dashboard/main_dashboard.py` ?⑤룆 `py_compile` ?ш?利??듦낵

**?ㅼ쓬 ?μ쨷 ?뺤씤 ?ъ씤??*
- WARN.log `[ExitConfig] 1怨꾩빟 TP1 蹂댄샇?꾪솚 紐⑤뱶 -> ...`
- WARN.log `[SingleContractTP1] ... mode=breakeven|breakeven_plus|atr_profit`
- WARN.log `[ManualExit] ?붿껌 pct=... send_qty=... kind=...`
- TRADE.log `[二쇰Ц?붿껌] ?섎룞 ... 泥?궛 ... 泥닿껐?湲?

---

## 2026-05-08 (9李?- ??갑?μ쭊???ㅽ뻾 ?ㅻ쾭?덉씠 + ?쒕갑???ㅽ뻾 ?먯씡 遺꾨━ + ?숈뒿/?듦퀎 諛⑺솕踰?

**?묒뾽**
- `dashboard/main_dashboard.py`
  - 吏꾩엯愿由??⑤꼸??`??갑??吏꾩엯` ?좉? 異붽?.
  - `?먯떊??/ ?ㅽ뻾?좏샇` ?숈떆 ?쒖떆 異붽?.
  - ?먯씡 PnL 移대뱶??`?ㅽ뻾 / ?쒕갑?? ?먯씡 ?숈떆 ?쒖떆 異붽?.
  - ?먯씡 異붿씠 ???쇰퀎/二쇰퀎/?붾퀎 ?쒖? ?붿빟 移대뱶??`?ㅽ뻾 / ?? 蹂묎린 異붽?.
- `main.py`
  - ?먮룞吏꾩엯 ?꾩슜 諛⑺뼢 諛섏쟾 濡쒖쭅 ?곌껐.
  - `TRADE` / `SIGNAL` 濡쒓렇??`?먯떊??, `?ㅽ뻾?좏샇`, `??갑?μ쭊??ON/OFF` 諛섏쁺.
  - `data/session_state.json`??`reverse_entry_enabled` ???蹂듭썝 ?곌껐.
  - 泥닿껐 ???寃쎈줈瑜?`_record_trade_result()`濡??듯빀???ㅽ뻾 ?먯씡怨??쒕갑???먯씡???④퍡 ?곸옱.
  - ?쇱씪 PF, daily_close, registry snapshot ???숈뒿/?듦퀎 寃쎈줈???쒕갑???먯씡 湲곗??쇰줈 ?꾪솚.
- `strategy/position/position_tracker.py`
  - ?ъ??섏씠 `raw_direction`, `reverse_entry_enabled`瑜?異붿쟻?섎룄濡??뺤옣.
  - ?ㅽ쁽/誘몄떎??紐⑤몢 `executed`? `forward` ?먯씡??蹂꾨룄濡?怨꾩궛?섎룄濡?蹂닿컯.
- `utils/db_utils.py`
  - `trades` 留덉씠洹몃젅?댁뀡??`raw_direction`, `executed_direction`, `reverse_entry_enabled`, `forward_*` 而щ읆 異붽?.
  - `fetch_grade_stats()`, `fetch_regime_stats()`, `fetch_trend_*()`媛 ?쒕갑??而щ읆 湲곗??쇰줈 吏묎퀎?섎룄濡??섏젙.

**寃利?*
- `python -m py_compile main.py dashboard/main_dashboard.py strategy/position/position_tracker.py utils/db_utils.py` ?듦낵.
- ?댁쁺 寃利앹? ?ㅼ쓬 ?몄뀡?먯꽌 ?ㅼ젣 UI濡??뺤씤 ?꾩슂:
  - `??갑?μ쭊?? ON/OFF ??吏꾩엯愿由??⑤꼸 `?먯떊??/ ?ㅽ뻾?좏샇` 諛섏쁺 ?щ?
  - ?먯씡 PnL 移대뱶? ?먯씡 異붿씠 ??`?ㅽ뻾 / ?쒕갑?? 蹂묎린 ?щ?
  - ?④낵寃利??숈뒿/異붿씠 ?⑤꼸???쒕갑???먯씡 湲곗??쇰줈 ?좎??섎뒗吏 ?щ?

## 2026-05-08 (6李? ??PnL ?뱀닔 ?섏젙 + CB??媛쒖꽑 + 吏꾩엯 寃뚯씠??蹂닿컯 (Hurst/ATR/ExitCooldown)

**怨꾧린**: 20260508 WARN.log?먯꽌 ??媛吏 踰꾧렇 + ??媛吏 肄붾뱶 媛?諛쒓껄

### ?듭떖 ?섏젙 6嫄?
| # | ?뚯씪 | ?댁슜 |
|---|---|---|
| B64 | `config/constants.py`, `main.py` | `FUTURES_MULTIPLIER` 500k??50k ?꾩닔 援먯껜. `FUTURES_PT_VALUE=250_000` ?좎꽕. `FUTURES_TICK_VALUE`=12,500?먯쑝濡??뺤젙 |
| B65 | `strategy/position/position_tracker.py`, `config/settings.py` | ?섏닔猷?諛섏쁺: `_calc_commission()` 異붽?, 3媛?泥?궛 寃쎈줈(close/partial/apply_exit_fill) ?곸슜. ?뺣났 ~79,500??怨꾩빟 |
| CB??1 | `main.py` STEP 1 | `record_accuracy()` ?몄텧??`v["horizon"] == "30m"` ?꾪꽣 異붽? (湲곗〈: 6媛??쇳빀 ??3?섑뵆 HALT) |
| CB??2 | `safety/circuit_breaker.py` | 2???곗냽 誘몃떖 ??HALT (1?뚮뒗 WARNING+Slack). 理쒖냼 20?섑뵆 蹂댄샇 |
| Gate-1 | `main.py` STEP 7 | `hurst >= HURST_RANGE_THRESHOLD(0.45)` 吏꾩엯 寃뚯씠???곌껐 (settings.py ?곸닔???덉뿀?쇰굹 寃뚯씠??誘몄뿰寃? |
| Gate-2 | `main.py` `_post_exit()` | `_exit_cooldown_until` 異붽?: TP泥?궛??遺? ?먯젅泥?궛??遺??ъ쭊??李⑤떒 |
| Gate-3 | `config/settings.py`, `main.py` | `ATR_MIN_ENTRY = 1.0pt` 異붽?. STEP 7??`atr >= ATR_MIN_ENTRY` 議곌굔 異붽? |

### ?ㅻ뒛 濡쒓렇?먯꽌 諛쒓껄???⑦꽩 (?섏젙 ??諛⑹뼱 媛??
- 09:34 CB???ㅻ컻?? 3?섑뵆(???몃씪?댁쫵 ?쇳빀)濡?HALT ??B64쨌CB??1 ?섏젙?쇰줈 諛⑹뼱
- 10:13 TP泥?궛 ??10:14 利됱떆?ъ쭊?? Gate-2 荑⑤떎??2遺꾩쑝濡?李⑤떒
- 10:24 ?먯젅 ??10:25 利됱떆?ъ쭊????CB??2/3 ?꾨떖: Gate-2 荑⑤떎??3遺꾩쑝濡?李⑤떒

---

## 2026-05-07 (5李? ??Phase 5 QA ?섏젙 + STRATEGY_PARAMS_GUIDE 以???먭? + strategy_events ?뚯씠釉?+ shadow_ev 珥덇린??
**?묒뾽**: QA ?몃뜑 ?ㅽ뻾 ??諛쒓껄??踰꾧렇 ?섏젙 ??STRATEGY_PARAMS_GUIDE.md 짠1~짠20 ?꾩껜 以???먭? ????誘멸뎄????ぉ ?ㅼ젣 肄붾뱶濡?援ы쁽

### QA ?섏젙 (qa_strategy_seeder.py 16/16 PASS ?ъ꽦)

| 踰꾧렇 | ?꾩튂 | ?섏젙 ?댁슜 |
|---|---|---|
| `%+,.0f` Python 3.7 誘몄???| `strategy/ops/daily_exporter.py` L67, `dashboard/strategy_dashboard_tab.py` L887 | `%+,.0f` ??`%+.0f` (comma 援щ텇??誘몄??? |
| `det.get_level()` AttributeError | `strategy/ops/daily_exporter.py` L93, `dashboard/strategy_dashboard_tab.py` L~1295, `main.py` daily_close | `MultiMetricDriftDetector.get_levels()` 諛섑솚媛믪씠 dict ??`max(det.get_levels().values())` |
| cp949 肄섏넄 UnicodeEncodeError | `scripts/qa_strategy_seeder.py` `run_report()` | UnicodeEncodeError fallback: `sys.stdout.buffer.write(report.encode("utf-8", errors="replace"))` |

### STRATEGY_PARAMS_GUIDE.md 以???먭? 寃곌낵 (짠1~짠20)

?꾩껜 93% 援ы쁽 ?꾨즺. ?ㅼ젣 誘멸뎄??2嫄??뺤씤:

| ??ぉ | ?뱀뀡 | ?곹깭 |
|---|---|---|
| `strategy_events` ?뚯씠釉?| 짠8 StrategyRegistry | 誘멸뎄????**?대쾲 ?몄뀡 援ы쁽** |
| `shadow_ev` 珥덇린??寃쎈줈 | 짠20 Hot-Swap 寃뚯씠??| `self._shadow_ev = None` ?좎뼵留???**?대쾲 ?몄뀡 援ы쁽** |
| `VolatilityTargeter` | 짠13 | ?섎룄??蹂대쪟 (媛?대뱶: "shadow test ?듦낵 ???곸슜") |
| `DynamicSizer` | 짠13 | ?섎룄??蹂대쪟 (?숈씪 ?댁쑀) |

### 援ы쁽????ぉ

**`config/strategy_registry.py`**:
- `strategy_events` ?뚯씠釉?(`_init_db()`): `id, version, event_type, event_at, message, note`
- `log_event(event_type, message, note, version)` 硫붿꽌??異붽?
- `get_event_log(version, limit)` 硫붿꽌??異붽?
- `register_version()` ?꾨즺 ??`log_event("VERSION_REGISTERED", ...)` ?먮룞 湲곕줉

**`backtest/param_optimizer.py`**:
- `propose_for_shadow(best_params, wfa_result, note)` 硫붿꽌??異붽?
- `apply_best()` ???`data/shadow_candidate.json` ???꾨낫 ?뚮씪誘명꽣 湲곕줉 (?쇱씠釉??뚮씪誘명꽣 利됱떆 蹂寃?湲덉?)
- Shadow candidate IPC ?⑦꽩: `OPT_RESULT_DIR/../../shadow_candidate.json` ??`data/shadow_candidate.json`

**`main.py`**:
- `start_shadow_mode(candidate_params, wfa_sharpe, candidate_version)` 硫붿꽌?? `ShadowEvaluator` ?몄뒪?댁뒪??- `_load_shadow_candidate()` 硫붿꽌?? `data/shadow_candidate.json` ?쎄린 ??`start_shadow_mode()` ?몄텧
- `daily_close()`: verdict 怨꾩궛 ??`log_event(event_type=_action, ...)` 湲곕줉. 留덉?留됱뿉 `_load_shadow_candidate()` ?몄텧

**`dashboard/strategy_dashboard_tab.py`**:
- `_StrategyLog.refresh(all_versions, event_log=None)` ?ъ옉?? `event_log` ?덉쑝硫??대깽??濡쒓렇 ?쒖떆, ?놁쑝硫?踰꾩쟾 紐⑸줉 fallback
- `_EVENT_KOR` dict: ?쒓뎅???대깽??????대쫫
- `StrategyPanel._refresh_ui()`: `get_event_log(limit=40)` ?몄텧 ??`log_panel.refresh()` ?꾨떖

**`strategy/ops/hotswap_gate.py`**:
- reject 寃쎈줈: `log_event("HOTSWAP_DENIED", reason, version=shadow_ev.version)` 異붽?
- approve 寃쎈줈: `log_event("HOTSWAP_APPROVED", ...)` + `shadow_candidate.json` ??젣

### ?섏젙???뚯씪

`strategy/ops/daily_exporter.py`, `dashboard/strategy_dashboard_tab.py`, `scripts/qa_strategy_seeder.py`, `config/strategy_registry.py`, `backtest/param_optimizer.py`, `main.py`, `strategy/ops/hotswap_gate.py`

---

## 2026-05-07 (4李? ???ㅼ떆媛??붽퀬 UI ?⑹꽦 ???섏젙 + 紐⑥쓽?ъ옄 startup sync 踰꾧렇 ?섏젙 + ?ъ????섎룞 蹂듭썝 踰꾪듉

**?묒뾽**: ??쒕낫???ㅼ떆媛??붽퀬 ?⑤꼸 ?곗씠??遺?뺥솗 臾몄젣 3醫??곗냽 吏꾨떒 諛??섏젙

### 濡쒓렇/?ㅽ겕由곗꺑 湲곕컲 吏꾨떒 寃곌낵

| ?꾩긽 | ?먯씤 | Fix |
|---|---|---|
| 珥앸ℓ留?576,500 (HTS 288,250,000) | ?뱀닔 ?ㅻ쪟: `entry 횞 qty 횞 500,000/1,000 = 576,500` | `entry 횞 qty 횞 250,000` (KOSPI200 ?좊Ъ 怨꾩빟 ?뱀닔) |
| 珥앺룊媛?먯씡 blank | ?⑷퀎 吏묎퀎 媛??`(pnl_sum or not rows)` ??pnl=0?대㈃ blank | 媛???쒓굅 ????긽 媛??ㅼ젙 |
| ?됯??먯씡(?? 0.00 | ?⑹꽦 ??議곌굔 `not rows` ??blank rows=[{...}] 耳?댁뒪 ?듦낵 紐삵븿 | `_has_real_row` ?섎?濡좎쟻 寃?щ줈 援먯껜 |
| 泥?궛媛??blank | ?⑹꽦 ?됱뿉 `二쇰Ц媛?μ닔?? ?꾨뱶 ?놁쓬 | `"二쇰Ц媛?μ닔??: str(qty)` 異붽? |
| ?먯씡??0.00% | pt 湲곗? 怨꾩궛: `pnl_pts/entry` ???섎? ?놁쓬 | won 湲곗?: `pnl_krw/eval_krw` |
| ??쒕낫???꾨? 0.00 (?ъ떆???? | startup sync媛 紐⑥쓽?ъ옄 blank rows瑜?"臾댄룷吏???쇰줈 ?댁꽍 ??`sync_flat_from_broker()` ?몄텧 ??position_state.json ??뼱? | 紐⑥쓽?ъ옄 ?쒕쾭 媛먯? ??FLAT 媛뺤젣 李⑤떒 |

### ?섏젙 3嫄?
**[B60/B61] ?⑹꽦 ??+ ?⑷퀎 吏묎퀎 踰꾧렇 ?섏젙 (`main.py` `_ts_push_balance_to_dashboard`)**:
```python
# 1. ?섎?濡좎쟻 blank 寃??_has_real_row = any(any(str(v).strip() for v in r.values()) for r in rows)
if not _has_real_row and self.position.status != "FLAT":

# 2. ?뱀닔 ?섏젙
_pnl_krw = _pnl_pts * 250_000   # 湲곗〈: 500_000
_eval_krw = _entry * _qty * 250_000  # 湲곗〈: entry 횞 qty 횞 500,000/1,000

# 3. ?꾨뱶 異붽?
"二쇰Ц媛?μ닔??: str(_qty),   # ??쒕낫??col-3 留ㅽ븨

# 4. ?먯씡??won 湲곗?
"?먯씡??: f"{(_pnl_krw / _eval_krw * 100.0):.2f}" if _eval_krw else "0.00"

# 5. ?⑷퀎 媛????pnl_sum=0 耳?댁뒪???ㅼ젙
if not str(summary.get("珥앺룊媛?먯씡") or "").strip():
    summary["珥앺룊媛?먯씡"] = f"{pnl_sum:.0f}"
```

**[B62] 紐⑥쓽?ъ옄 startup sync FLAT ??뼱?곌린 諛⑹? (`main.py` `_ts_sync_position_from_broker`)**:
```python
# blank rows AND 紐⑥쓽?ъ옄 ?쒕쾭 AND ????ъ????덉쓬 ??FLAT 媛뺤젣 湲덉?
_server_gubun = self.kiwoom.get_login_info("GetServerGubun")
_is_mock = (_server_gubun == "1")
if _is_mock and self.position.status != "FLAT":
    log_manager.system("[BrokerSync] 紐⑥쓽?ъ옄 blank-rows ??????ъ????좎?", "WARNING")
    _ts_push_balance_to_dashboard(self, result)
    return
```

**[B63] ?ъ????섎룞 蹂듭썝 踰꾪듉 (`dashboard/main_dashboard.py`, `main.py`)**:
- `PositionRestoreDialog`: 諛⑺뼢/吏꾩엯媛/?섎웾/ATR ?낅젰 ?ㅼ씠?쇰줈洹?- `AccountInfoPanel.btn_position_restore`: 二쇳솴??踰꾪듉 (?ㅼ떆媛??붽퀬 ?⑤꼸 ?곗긽??
- `AccountInfoPanel.sig_position_restore(str, float, int, float)` ?쒓렇??- `_ts_manual_position_restore()`: `sync_from_broker()` ?몄텧 ???먯젅/TP ?먮룞 ?ш퀎????300ms ???붽퀬 UI 媛깆떊
- **HTML ?댄똻 3?뱀뀡**: ?ъ슜紐⑹쟻 / ?ъ슜諛⑸쾿(吏꾩엯媛 ?섏궛踰??ы븿) / ATR 李몄“(`[DBG-F4] ATR floor=`)

### ?ㅻ뒛 ?뺤씤??以묒슂 ?ъ떎

- **15:10 媛뺤젣泥?궛 ?뺤긽 ?숈옉 ?뺤씤**: `position_state.json` `last_update_reason="apply_exit_fill_final:15:10 媛뺤젣泥?궛"` at 15:25:59 ??媛뺤젣泥?궛 寃쎈줈 ?뺤긽
- **KOSPI200 ?좊Ъ 怨꾩빟 ?뱀닔**: 250,000??pt (2017???댄썑 湲곗?). HTS 留ㅼ엯湲덉븸 = entry 횞 qty 횞 250,000
- **踰꾧렇 泥댁씤 ?뺤젙**: `load_state()` LONG 蹂듭썝 ??`sync_from_broker()` blank rows ??`sync_flat_from_broker()` ??JSON ??뼱? ???ㅼ쓬 ?ъ떆??FLAT ????쒕낫??0.00

### ?섏젙 ?뚯씪

- `main.py` ??`_ts_push_balance_to_dashboard`, `_ts_sync_position_from_broker`, `_ts_manual_position_restore` (?좉퇋)
- `dashboard/main_dashboard.py` ??`PositionRestoreDialog` (?좉퇋), `AccountInfoPanel` 踰꾪듉/?쒓렇???몃뱾???댄똻 異붽?

---

## 2026-05-07 (3李? ??B56 荑⑤떎??以묒븰??+ B52/B53 ?ъ쭊??猷⑦봽 洹쇰낯 ?섏젙

**?묒뾽**: 09:56~10:07 ENTRY 8??諛섎났 吏꾩엯 ?먯씤 遺꾩꽍 ??`_clear_pending_order()` 以묒븰?붾줈 ?섏젙

### 濡쒓렇 遺꾩꽍 寃곌낵

| ?쒓컖 | ?대깽??|
|---|---|
| 09:56~10:07 | SHORT쨌LONG 援먮?濡?2遺꾨쭏??ENTRY 8??諛섎났 |
| 10:14:00 | LONG 1怨꾩빟 吏꾩엯 ??利됱떆 泥닿껐 (B54 ?뺤씤) |
| 10:34:01 | ?섎뱶?ㅽ넲 泥?궛 @ 1114.95 (-7.35pt / -3,675,000?? |
| 10:38 ?댄썑 | Sizer留??몄텧, 吏꾩엯 ?놁쓬 (CB??諛쒕룞?쇰줈 ?뱀씪 HALTED 異붿젙) |

### ?먯씤 吏꾨떒

B53 荑⑤떎??蹂??`_entry_cooldown_until`)媛 ?ㅼ젣濡??ㅼ젙?섏? ?딅뒗 耳?댁뒪 3媛吏:
1. B52 荑⑤떎??肄붾뱶媛 `if _optimistic:` 釉붾줉 ?대? ??`_optimistic=False`?대㈃ 荑⑤떎???놁씠 pending留??댁젣
2. `_ts_on_order_message` 嫄곕? 寃쎈줈 ??`_clear_pending_order()` ?몄텧?섎굹 荑⑤떎??誘몄꽕??3. balance Chejan FLAT 寃쎈줈 ???숈씪

WARN.log 遺꾩꽍: 09:56~10:09 援ш컙??gubun='1' ?붽퀬 Chejan ?대깽???놁쓬 ?뺤씤 ??`_ts_sync_from_balance_payload`???먯씤 ?꾨떂.
`order_no!=''`??二쇰Ц??2遺???clear????`_ts_on_order_message` 嫄곕? 寃쎈줈媛 ?쇰? ?묐룞??寃껋쑝濡?異붿젙.

### ?섏젙 3嫄?
**[B56] `_clear_pending_order()` 荑⑤떎??以묒븰??(main.py L258-272)**:
```python
def _clear_pending_order(self) -> None:
    if self._pending_order is not None:
        logger.warning("[PendingOrder] clear %s", self._pending_order)
        if (self._pending_order.get("kind") == "ENTRY"
                and self._pending_order.get("filled_qty", 0) == 0):
            self._entry_cooldown_until = datetime.datetime.now() + datetime.timedelta(minutes=2)
            logger.warning("[EntryCooldown] ENTRY 誘몄껜寃??뚮㈇ ??2遺??ъ쭊??湲덉? until %s", ...)
    self._pending_order = None
```

**[B52] `_optimistic` ?섏〈 遺꾨━ (main.py L555-585)**:
- `_reset_position()`? `_optimistic==True`???뚮쭔 (湲곗〈 ?좎?)
- 荑⑤떎???ㅼ젙? ENTRY ??꾩븘?껋씠硫???긽 (`_optimistic` 臾닿?)

**[B56] balance Chejan FLAT 二쇱꽍 異붽? (main.py L2712)**:
- qty<=0 遺꾧린??"`_clear_pending_order()` ?댁뿉??B56 ?먮룞 泥섎━" 二쇱꽍

### ?섏젙 ?뚯씪

- `main.py` ??3怨??섏젙 (`_clear_pending_order`, B52 釉붾줉, balance Chejan 二쇱꽍)

---

## 2026-05-06 (2李? ??WARN.log 遺꾩꽍 + trade_type 泥?궛 ?ㅻ쪟(B47) + gubun='4' 李⑤떒(B48)

**?묒뾽**: 20260506 TRADE쨌SYSTEM쨌WARN 濡쒓렇 遺꾩꽍 ??肄붾뱶 媛쒖꽑???좏슚??寃????B47쨌B48 ?섏젙

### 濡쒓렇 遺꾩꽍 寃곌낵 ?붿빟

| ?쒓컖 | ?대깽??|
|---|---|
| 10:48~10:52 | LONG 吏꾩엯횞2 ??TP1 泥?궛 媛?+0.95pt, +1.10pt (?뺤긽 泥닿껐) |
| 11:07 ?댄썑 | ?섎뱶?ㅽ넲 2??(-1.99pt, -2.16pt) |
| 11:35:31 | [泥닿껐吏꾩엯] LONG @ 1128.8 ??Chejan fill_qty>0 ?뺤긽 ?섏떊 ?뺤씤 |
| 14:28:00 | LONG @ 1133.9 吏꾩엯 ??TP1 EXIT 二쇰Ц ?꾩넚 |
| 14:28~15:24 | EXIT 二쇰Ц 60珥덈쭏????꾩븘?꺿넂?щ컻??臾댄븳 諛섎났 (Chejan 泥닿껐 誘몄닔?? |
| 14:38:00 | CB??諛쒕룞 (30遺??뺥솗??33.3% < 35%) ???뱀씪 HALTED |
| 15:24:58 | 理쒖큹 泥닿껐 Chejan (fill_qty=1) ???ъ???醫낅즺 @ 1128.7 (-5.20pt) |

### ?먯씤 吏꾨떒

**WARN.log?먯꽌 諛쒓껄???⑦꽩**:
- `[PendingOrder] set EXIT_FULL TP1` ??60珥???`[PendingOrder] clear` 諛섎났 (泥닿껐 ?놁쓬)
- 留?60珥덈쭏????TP1/?섎뱶?ㅽ넲 EXIT 二쇰Ц 諛쒗뻾 ??Chejan fill ?놁쓬 ????꾩븘??- `[ChejanFlow] gubun='4' order_no='' status='' fill_qty=0` ??留?二쇰Ц留덈떎 ?몄씠利??대깽??
**洹쇰낯 ?먯씤**: `_send_kiwoom_exit_order`?먯꽌 `trade_type=2`(留ㅻ룄 媛쒖떆=?좉퇋 SHORT) ?ъ슜. ?좊Ъ LONG ?ъ???泥?궛? `trade_type=4`(留ㅻ룄 泥?궛)?댁뼱???? 紐⑥쓽?ъ옄 ?쒕쾭媛 ?좉퇋留ㅻ룄 二쇰Ц?쇰줈 ?댁꽍 ???좊Ъ醫낅ぉ 肄붾뱶媛 ?녿뒗 ?좉퇋留ㅻ룄濡?泥섎━ ??泥닿껐 遺덇?.

**媛쒖꽑??A(unfilled_qty fallback)쨌B(FID 異붽?) 臾댄슚??*: WARN.log 遺꾩꽍 寃곌낵 FID ?뚯떛 ?ㅽ뙣媛 ?꾨떂 ?뺤씤 ????媛쒖꽑??紐⑤몢 遺덊븘??

### ?섏젙 2嫄?
**[B47] trade_type 泥?궛 ?ㅻ쪟 (main.py)**:
```python
# _send_kiwoom_exit_order (line 1103)
# Before: trade_type = 2 if LONG else 1  (?좉퇋媛쒖떆 ???ㅻ쪟)
# After:  trade_type = 4 if LONG else 3  (泥?궛 ???щ컮由?

# _KiwoomOrderAdapter.send_market_order (line 2715)
# Before: trade_type = 2 if SELL else 1
# After:  trade_type = 4 if SELL else 3
```

**[B48] gubun='4' ?몄씠利?李⑤떒 (main.py `_ts_on_chejan_event`)**:
```python
_gubun = str(payload.get("gubun", "")).strip()
if _gubun not in ("0", "1"):
    return  # 紐⑥쓽?ъ옄 ?뱀쑀??gubun='4' ?몄씠利??대깽??李⑤떒
```

### 遺???④낵 ?닿껐

- **15:10 媛뺤젣泥?궛 ?꾨씫**: `_has_pending_order()=True`濡??명빐 紐⑤뱺 exit trigger媛 李⑤떒?섎뜕 援ъ“??B47 ?섏젙?쇰줈 ?④퍡 ?닿껐?? trade_type=4 ?섏젙 ??EXIT 泥닿껐??利됱떆 ?대（?댁?硫?pending???댁냼 ??媛뺤젣泥?궛 寃쎈줈 ?뺤긽??

### ?섏젙 ?뚯씪

- `main.py` ??3怨??섏젙

### Git commit

- `3cd9677` ??fix: SendOrderFO trade_type 泥?궛 ?ㅻ쪟 ?섏젙 + gubun='4' early return

---

## 2026-05-06 (Fix B ?댁쨷吏꾩엯 諛⑹? + OPW20006 enc ?뚯씪 遺꾩꽍 + TR 議곗궗 ?덉감 ?섎┰)

**?묒뾽**:
1. Fix B (?숆????ъ????ㅽ뵂) ??`position_tracker.py` + `main.py` ?곸슜
2. OPW20006 enc ?뚯씪 吏곸젒 遺꾩꽍 ???ㅼ? CS ?ㅻ떟 諛쒓껄 + api_connector.py ?꾨㈃ ?섏젙
3. TR 議곗궗 ?덉감 臾몄꽌??(dev_memory + claude memory)

### Fix B ??紐⑥쓽?ъ옄 ?댁쨷吏꾩엯 諛⑹?

Kiwoom 紐⑥쓽?ъ옄?먯꽌 Chejan 肄쒕갚 ?놁씠 ?ъ??섏씠 ?댁쨷 ?ㅽ뵂?섎뜕 援ъ“??臾몄젣瑜?`_optimistic` ?뚮옒洹??⑦꽩?쇰줈 ?닿껐.

| ?뚯씪 | ?섏젙 ?댁슜 |
|---|---|
| `strategy/position/position_tracker.py` | `_optimistic: bool = False` ?꾨뱶 異붽?. `apply_entry_fill()`??蹂댁젙 寃쎈줈 異붽? (諛⑺뼢 ?쇱튂 ??媛寃⑸쭔 ?낅뜲?댄듃, ?섎웾 誘몄쬆媛). `_reset_position()`??`_optimistic = False` 異붽? |
| `main.py` (line 2660) | `_set_pending_order()` 吏곹썑 `position.open_position()` + `_optimistic = True` ?쎌엯 ??**production 踰꾩쟾** (line 2684 monkeypatch ??? |

**?먮쫫**:
```
SendOrder ret=0
??_set_pending_order()
??position.open_position(direction, price, qty)  ???숆????ㅽ뵂
??position._optimistic = True
[Chejan ?덉쓣 寃쎌슦]
??apply_entry_fill() ??_optimistic=True + direction ?쇱튂 ??媛寃?蹂댁젙留?(?섎웾 利앷? ?놁쓬)
[Chejan ?놁쓣 寃쎌슦(紐⑥쓽?ъ옄)]
???대? ?ㅽ뵂???ъ??섏쑝濡?留ㅻℓ 怨꾩냽
```

### OPW20006 enc ?뚯씪 遺꾩꽍

| 諛쒓껄 | ?댁슜 |
|---|---|
| **?덉퐫?쒕챸 ?ㅽ? ?뺤젙** | `?꾪솢`(域? ??`?꾪솴`(力?. 湲곗〈 blank 諛섑솚 洹쇰낯 ?먯씤 |
| **?ㅼ? CS ?ㅻ떟** | "?붽퀬?섎웾 ?놁쓬" ??enc ?뚯씪??議댁옱 (offset 66, len 9). CS ?듬? 遺덉떊 援먰썕 |
| **蹂댁쑀?섎웾 ?쒓굅** | OPW20006??議댁옱?섏? ?딅뒗 ?꾨뱶 (CS ?덈궡 湲곕컲 ?섎せ 異붽?). `_FIELDS`?먯꽌 ??젣 |
| **議고쉶嫄댁닔 援먯감寃利?* | ?⑥씪 ?덉퐫??`?좎샃?붽퀬?곸꽭?꾪솴?⑷퀎.議고쉶嫄댁닔` ??硫??cnt ?щ줈?ㅼ껜??異붽? |

**?섏젙 ?뚯씪**: `collection/kiwoom/api_connector.py` ??`_MULTI_RECORD`, `_SINGLE_RECORD`, `_FIELDS` ?꾨㈃ 援먯껜

### TR 議곗궗 ?덉감 ?섎┰

- `dev_memory/kiwoom_api_tr_investigation.md` ?좎꽕 ??enc ?뚯씪 ?쎄린 ?덉감쨌肄붾뱶쨌GetRepeatCnt/GetCommData ?⑦꽩쨌OPW20006 ?⑥젙 ??- `reference_kiwoom_tr_enc.md` claude memory ?????吏꾩떎 ?먯쿇쨌議곗궗 ?쒖꽌쨌援먰썕 ?곴뎄 蹂댁〈

### [異붽? ?몄뀡] SendOrderFO ?꾪솚 + Fix B 吏꾨떒

?ㅼ젣 ?ㅽ뻾 ??`[RC4109] 紐⑥쓽?ъ옄 醫낅ぉ肄붾뱶媛 議댁옱?섏? ?딆뒿?덈떎` ?ㅻ쪟 諛쒖깮 ???먯씤 遺꾩꽍 諛?異붽? ?섏젙.

**[B46] SendOrder ??SendOrderFO**

| ??ぉ | ?댁슜 |
|---|---|
| **利앹긽** | `[RC4109] 紐⑥쓽?ъ옄 醫낅ぉ肄붾뱶媛 議댁옱?섏? ?딆뒿?덈떎` + TR=`KOA_NORMAL_SELL_KP_ORD`(二쇱떇 留ㅻ룄) |
| **?먯씤** | `SendOrder`??二쇱떇 二쇰Ц ?⑥닔 ???좊Ъ???ъ슜 遺덇?. `KOA_NORMAL_SELL_KP_ORD` TR??諛쒖깮?섎ŉ 肄붾뱶 嫄곕? |
| **Fix** | `api_connector.py` `send_order_fo()` ?좎꽕 (COM `SendOrderFO`), `hoga_gb="3"`(?좊Ъ?쒖옣媛) |
| **main.py** | `_send_kiwoom_entry/exit_order()` + `_KiwoomOrderAdapter.send_market_order()` ??`send_order_fo()` ?꾪솚 |

**Fix B 吏꾨떒 濡쒓렇 異붽?**

`[EntryPendingCreated] position='FLAT'` ??`open_position()` silent ?ㅽ뙣 ?섏떖. ?먯씤 ?뚯븙???꾪빐 try/except + `[FixB]` WARNING 濡쒓렇 異붽?.
- ?깃났 ?? `[FixB] ?숆????ㅽ뵂 ?꾨즺 direction=SHORT status=SHORT ...`
- ?ㅽ뙣 ?? `[FixB] open_position ?ㅽ뙣 ... err=<?먯씤>`

**?꾨줈洹몃옩留ㅻℓ FID 諛쒓껄 (PROBE)**

```
code='P00101' type='?꾨줈洹몃옩留ㅻℓ'
FID 202=200850, 204=14145360 (留ㅼ닔?꾩쟻湲덉븸瑜?
FID 210=-7828, 212=+354793   (?쒕ℓ??愿??
FID 928=-2275318, 929=-10544  (?꾩쟻 ?꾨줈洹몃옩 ?쒕ℓ??
```
??V23 寃利???ぉ FID ?뺤젙 媛?μ꽦 ?믪쓬 (?μ쨷 ?ы솗???꾩슂)

### ?섏젙 ?뚯씪 紐⑸줉 (?꾩껜 ?몄뀡)

- `strategy/position/position_tracker.py`
- `main.py`
- `collection/kiwoom/api_connector.py`
- `dev_memory/kiwoom_api_tr_investigation.md` (?좉퇋)

---

## 2026-05-04 (?쇨컙 2?몄뀡 ??Kiwoom API 二쇰Ц ?곌껐 + 遺遺?泥?궛 ?꾩꽦 + ??쒕낫??媛쒖꽑)

**?묒뾽**: 濡쒓렇??4??嫄곕옒 湲곕줉???덉쑝??Kiwoom 紐⑥쓽怨꾩쥖 ?붽퀬??嫄곕옒 ?댁뿭 ?놁쓬 ???먯씤 遺꾩꽍 + 援ъ“???섏젙

### 洹쇰낯 ?먯씤 遺꾩꽍

Kiwoom 二쇰Ц???꾨떖?섏? ?딆? ?댁쑀 3媛吏:
1. `api_connector.py`??`send_order()` 硫붿꽌???먯껜媛 ?놁뿀????EntryManager/ExitManager??`_send_*_order()`媛 `self._api`媛 None??寃쎌슦留??쒕? 泥섎━?섍퀬, None???꾨땶 寃쎌슦 議댁옱?섏? ?딅뒗 硫붿꽌?쒕? ?몄텧???ㅻ쪟
2. `entry_manager.py` / `exit_manager.py`??`acc_no = ""` ??怨꾩쥖踰덊샇 鍮?臾몄옄?대줈 二쇰Ц ?꾩넚 ?쒕룄
3. `main.py`?먯꽌 `EntryManager` / `ExitManager`瑜??ъ슜?섏? ?딄퀬 吏곸젒 `position.open_position()` / `close_position()` ?몄텧 ??API 二쇰Ц ?꾩넚 寃쎈줈 ?꾪? ?놁뿀??
### ?듭떖 ?섏젙 5嫄?
| ??ぉ | ?뚯씪 | ?댁슜 |
|---|---|---|
| **send_order() ?좎꽕** | `collection/kiwoom/api_connector.py` | `SendOrder` COM API ?섑븨. order_type 1=?좉퇋留ㅼ닔쨌2=?좉퇋留ㅻ룄, hoga_gb="03"=?쒖옣媛, ret=0=?깃났 |
| **acc_no="" ?섏젙** | `entry_manager.py`, `exit_manager.py` | `acc_no = ""` ??`acc_no = _secrets.ACCOUNT_NO` |
| **main.py 吏꾩엯 二쇰Ц ?ы띁** | `main.py` | `_send_kiwoom_entry_order(direction, qty)` ??LONG?뭪ype1, SHORT?뭪ype2. `_execute_entry()` ???ъ???吏꾩엯 ??API ?몄텧 |
| **main.py 泥?궛 二쇰Ц ?ы띁** | `main.py` | `_send_kiwoom_exit_order(qty)` ??LONG泥?궛?뭪ype2留ㅻ룄, SHORT泥?궛?뭪ype1留ㅼ닔. `_check_exit_triggers()` 媛?泥?궛 ??API ?몄텧 |
| **遺遺?泥?궛 ?꾩꽦** | `position_tracker.py`, `main.py` | `PositionTracker.partial_close(exit_price, qty, reason)` ?좎꽕. `_execute_partial_exit(price, stage)` + `_post_partial_exit(result, stage)` ??TP1(33%)/TP2(33%) 遺遺꾩껌??API ??DB ????쒕낫???꾩껜 ?곌껐 |

### ??쒕낫??二쇰Ц/泥닿껐 ??媛쒖꽑 2嫄?
| ??ぉ | ?댁슜 |
|---|---|
| **?ㅻ뜲?댄꽣 硫뷀듃由?* | ?곷떒 ?щ━?쇱? 吏?쒕? ?섎뱶肄붾뵫 ??LatencySync ?ㅻ뜲?댄꽣濡?援먯껜. `update_order_metrics(trades, avg_lat_ms, peak_lat_ms, samples)` 異붽?. 留ㅻ텇 ?뚯씠?꾨씪????`latency_sync.summary()` ????쒕낫???꾩넚 |
| **濡쒓렇 醫뚯륫 ?뺣젹** | `QTextEdit.append()` ?댁쟾 釉붾줉 Qt alignment ?곸냽 臾몄젣 ??`QTextCursor` + `QTextBlockFormat.setAlignment(Qt.AlignLeft)` 湲곕컲 `_insert_html_left()` / `_insert_html_center()` static 硫붿꽌?쒕줈 ?꾩쟾 ?닿껐 |

### ?섏젙 ?뚯씪 紐⑸줉

- `collection/kiwoom/api_connector.py` ??`send_order()` 異붽?
- `main.py` ??吏꾩엯/泥?궛 ?ы띁, `_execute_partial_exit`, `_post_partial_exit`, `_KiwoomOrderAdapter`
- `strategy/entry/entry_manager.py` ??acc_no ?섏젙
- `strategy/exit/exit_manager.py` ??acc_no ?섏젙
- `strategy/position/position_tracker.py` ??`partial_close()` 異붽?
- `dashboard/main_dashboard.py` ???ㅻ뜲?댄꽣 硫뷀듃由?+ QTextCursor ?뺣젹

---

## 2026-05-04 (?쇨컙 ?몄뀡 ??FID ?먯깋쨌PROBE 吏꾨떒쨌?섍툒 TR ?섏젙)

**?묒뾽**: PROBE 吏꾨떒 濡쒓렇 遺꾩꽍 ??FID ?ㅻ쪟 ?뺤젙 ?섏젙 + ?좉퇋 FID ?곸닔 異붽? + ?섍툒 TR 肄붾뱶 ?섏젙

### ?듭떖 ?섏젙 6嫄?
| ??ぉ | ?댁슜 |
|---|---|
| **[B40] FID_OI = 291 移섎챸???ㅻ쪟 ?섏젙** | `config/constants.py` FID_OI 291 ??195. FID 291? ?덉긽泥닿껐媛(?좊Ъ?멸??붾웾 湲곗?)?대ŉ 誘멸껐?쒖빟?뺤씠 ?꾨떂. PROBE-ALLRT-FIDS ?ㅼ틪?쇰줈 FID 195=207357(誘멸껐?쒖빟?? ?뺤젙 |
| **option_data.py ?섎뱶肄붾뵫 291 ?섏젙** | `collection/kiwoom/option_data.py` ?섎뱶肄붾뵫 291 ??怨???`FID_OI` ?꾪룷?몃줈 援먯껜 |
| **?좉퇋 FID ?곸닔 異붽?** | `FID_EXPECTED_PRICE=291`, `FID_KOSPI200_IDX=197`(KOSPI200吏??, `FID_BASIS=183`(?쒖옣踰좎씠?쒖뒪), `FID_UPPER_LIMIT=305`(?좊Ъ?곹븳媛), `FID_LOWER_LIMIT=306`(?좊Ъ?섑븳媛) |
| **TR_INVESTOR_OPTIONS ?섏젙** | `config/constants.py` opt50014 ??opt50008. opt50014???좊Ъ媛寃⑸?蹂꾨퉬以묒감?몄슂泥?쑝濡??섎せ ?ъ슜???뺤씤 |
| **PROBE 吏꾨떒 ?명봽???좎꽕** | `utils/logger.py` LAYER_PROBE 異붽?(DEBUG+肄섏넄). `api_connector.py` PROBE-ALLRT(?좉퇋 ?ㅼ떆媛?????꾩닔 FID ?ㅼ틪), probe_investor_ticker() ?좎꽕 |
| **PROBE ?ㅼ틪 踰붿쐞 ?뺤옣** | PROBE-ALLRT FID ?ㅼ틪: 1~50 ??1~99 (bid/ask qty FID 51~99 援ш컙 異붽?) |

### PROBE-ALLRT ?ㅽ뻾 寃곌낵 (2026-05-04)

**?좊Ъ?쒖꽭 FID 二쇱슂 諛쒓껄:**
```
FID 195 = '207357'    ??誘멸껐?쒖빟??(吏꾩쭨 OI) ??FID_OI ?섏젙 洹쇨굅
FID 197 = '+1049.66'  ??KOSPI200 吏???꾩옱媛 (?좉퇋)
FID 183 = '+1.04'     ???쒖옣踰좎씠?쒖뒪 (?좉퇋)
```

**?좊Ъ?멸??붾웾 FID 諛쒓껄:**
```
FID 291 = '+1020.60'  ???덉긽泥닿껐媛 (湲곗〈 FID_OI=291???닿쾬???쎄퀬 ?덉뿀????踰꾧렇)
FID 41, 51, 61, 71    ???멸?/?붾웾 (?뺤씤)
```

**?좉퇋 ?ㅼ떆媛????諛쒓껄:**
```
?뚯깮?ㅼ떆媛꾩긽?섑븳: FID 305=+1078.35(?곹븳媛), FID 306=-918.65(?섑븳媛)
二쇱떇?덉긽泥닿껐: FID 10(?덉긽媛), 11(?꾩씪鍮?, 12(?깅씫瑜?) ???좊Ъ肄붾뱶濡??λ쭏媛먰썑 ?섏떊
?꾨줈洹몃옩留ㅻℓ: code='P00101' ??FID ?ㅼ틪 誘몄셿猷?(?ㅼ쓬 ?μ쨷 ?ъ떆???꾩슂)
?ъ옄?릘icker: 紐⑥쓽?ъ옄 ?쒕쾭 誘몄????뺤씤 (8媛吏 肄붾뱶 議고빀 紐⑤몢 ret=0?대굹 ?곗씠???놁쓬)
```

---

## 2026-05-04 (?ㅽ썑 ?몄뀡 ??遺?몄뒪?몃옪쨌SGD쨌UI)

**?묒뾽**: SGD 移섑궓?먭렇 遺?몄뒪?몃옪 ?닿껐 + log_loss ?명솚???섏젙 + watchdog 媛쒖꽑 + ??쒕낫??UI

### ?듭떖 ?섏젙 6嫄?
| ??ぉ | ?댁슜 |
|---|---|
| **[B37] SGD log_loss ?щ옒??* | `learning/online_learner.py` `loss="log_loss"` ??`"log"`. sklearn 1.0.2??"log_loss" 誘몄?????留ㅻ텇 ValueError ?щ옒??|
| **遺?몄뒪?몃옪 移섑궓?먭렇 ?닿껐** | STEP 5 ??early return ?쒓굅 ??GBM/SGD 誘명븰????1/3 洹좊벑 ?덉륫?쇰줈 STEP 9源뚯? 吏꾪뻾 ??DB ??????ㅼ쓬 遺?STEP1 寃利???STEP2 learn() ?몄텧 ??SGD ?숈뒿 ?쒖옉 |
| **watchdog ?꾧퀎媛??곹뼢** | 60/120/180s ??90/150/240s. 1遺꾨큺 二쇨린=60s 湲곗? 30s 踰꾪띁 ?뺣낫濡?race condition 諛⑹? |
| **`_last_recovery_ts` 以묐났 蹂듦뎄 諛⑹?** | ?숈씪 ts 遺꾨큺??watchdog 蹂듦뎄瑜?諛섎났 ?ㅽ뻾?섎뜕 踰꾧렇 ?섏젙. 蹂듦뎄 ?꾨즺 ts 湲곕줉 + `run_minute_pipeline` 吏꾩엯 ??珥덇린??|
| **Guard-C1/C2 `notify_pipeline_ran()`** | 鍮꾩젙??遺꾨큺 李⑤떒 return ??watchdog 移댁슫??由ъ뀑 異붽? |
| **`_dir_ko` NameError** | early return ?쒓굅 ??STEP 7 ?꾨떖 媛????`_dir_ko = "?곸듅"/"?섎씫"/"愿留?` ?뺤쓽 異붽? |

### ??쒕낫??UI 媛쒖꽑 3嫄?
| ??ぉ | ?댁슜 |
|---|---|
| **?뚮씪誘명꽣 以묒슂???댄똻** | SHAP 媛쒕뀗 ?ㅻ챸 + ?낅뜲?댄듃 議곌굔 (GBM 誘명븰????0.0%, ?붿슂??08:50 ?ы븰?????먮룞 媛깆떊) |
| **?뚮씪誘명꽣 ?곴?怨꾩닔 ?댄똻** | ?쒖떆 ?뺤떇 ?ㅻ챸 + ?낅뜲?댄듃 議곌굔 |
| **?뱀뀡 媛꾧꺽 議곗젙** | 紐⑤뜽?곹깭?됤넄?몃씪?댁쫵 +8px, ?뱀뀡 援щ텇????+16px 쨌 ??+12px |

### 寃利??뺤씤

```
2026-05-04 13:44:00 [INFO] LEARNING: [OnlineLearner] 1m 珥덇린 ?숈뒿 ?꾨즺
2026-05-04 13:44:00 [INFO] LEARNING: [OnlineLearner] 3m 珥덇린 ?숈뒿 ?꾨즺
2026-05-04 13:44:00 [INFO] LEARNING: [OnlineLearner] 5m 珥덇린 ?숈뒿 ?꾨즺
2026-05-04 13:44:00 [INFO] LEARNING: [OnlineLearner] 15m 珥덇린 ?숈뒿 ?꾨즺
??log_loss ?섏젙 + 遺?몄뒪?몃옪 fix ???뺤긽 ?숈뒿 ?뺤씤
??2遺?留뚯뿉 15m ?숈뒿 = ?댁쟾 ?몄뀡 DB 15遺????덉륫 ?쒖슜 (?뺤긽 ?숈옉)
```

---

## 2026-05-04 (?ㅼ쟾 ?몄뀡)

**?묒뾽**: 紐⑥쓽?ъ옄 ?ㅼ떆媛?遺꾨큺 ?섏떊 寃쎈줈 ?뺣┰ + ?뚯씠?꾨씪??watchdog ?ㅼ옉??洹쇰낯 ?섏젙

### 而ㅻ컠 1嫄?(?대쾲 ?몄뀡)

| 而ㅻ컠 | ?댁슜 |
|---|---|
| (?대쾲 ?몄뀡) | fix: 紐⑥쓽?ъ옄 SetRealReg A0166000 + WARN 濡쒓렇 遺꾨━ + ?뚯씠?꾨씪??watchdog ?섏젙 |

---

### [1] WARN 濡쒓렇 遺꾨━ ??SYSTEM.log??INFO留? 寃쎈낫??WARN.log + 寃쎈낫 ??
**臾몄젣**: WARNING ?댁긽 硫붿떆吏媛 SYSTEM.log? 寃쎈낫 ???묒そ???쇱옱.

**?섏젙** (`utils/logger.py`):
- `_MaxLevelFilter(max_level)` ?대옒??異붽? ??`levelno < max_level` 留??듦낵
- SYSTEM ?뚯씪 ?몃뱾?ъ뿉 `_MaxLevelFilter(logging.WARNING)` 遺李???INFO ?꾩슜
- `warn_fh` (TimedRotatingFileHandler `YYYYMMDD_WARN.log`) 異붽? ??WARNING+ ?꾩슜

**?섏젙** (`dashboard/main_dashboard.py`):
- `log_panel.append()`: `tag in ("WARN", "ERROR", "CRITICAL")` ??寃쎈낫 ??쭔 湲곕줉 (`return`)

---

### [2] OPT50029 ??SetRealReg ?꾪솚 (紐⑥쓽?ъ옄 ?쒕쾭 ?대쭅 遺덇?)

**諛쒓껄**: 紐⑥쓽?ъ옄 ?쒕쾭?먯꽌 OPT50029(?좊Ъ遺꾩감?몄슂泥? rows=0 ???쇱씠釉??곗씠??誘몄젣怨?

**?섏젙** (`main.py`):
- 湲곗〈: `rt_code = get_realtime_futures_code()` (??`101W06`) + `is_mock_server=True`
- 蹂寃? `code = get_nearest_futures_code()` (??`A0166000`) + `realtime_code=code` + `is_mock_server=False`
- 寃곌낵: SetRealReg濡?A0166000 ?ㅼ떆媛???援щ룆 ??紐⑥쓽?ъ옄 ?쒕쾭?먯꽌 ?뺤긽 ?섏떊 ?뺤씤

---

### [3] SetRealReg 肄붾뱶 遺덉씪移?踰꾧렇 ?섏젙 (101W06 vs A0166000)

**?먯씤**: ?댁쟾??`rt_code = get_realtime_futures_code()` ??`101W06` 諛섑솚. ?ㅼ젣 ?깆? `A0166000`?쇰줈 ?섏떊 ??肄쒕갚 ?꾪꽣?먯꽌 ?꾨웾 李⑤떒.

**?섏젙** (`realtime_data.py`):
- `_rt_code` ?꾨뱶: `101W06` ??`A0166000`
- `_on_real_data()` ?꾪꽣: `code.strip() != self._rt_code.strip()` 議곌굔?쇰줈 李⑤떒 ?놁뼱吏?
---

### [4] 吏꾨떒 濡쒓퉭 異붽? (sys_log ??SYSTEM ?덉씠??

**異붽? 濡쒓렇 ?ъ씤??* (`realtime_data.py`, `api_connector.py`):
- `[RT-CB]` ?????ㅼ떆媛???泥??섏떊 ??(code/type/?깅줉??
- `[RT-DATA]` ?????섏떊 #1~5, ?댄썑 100?뚮쭏??- `[RT-RAW]` ??raw_price/raw_vol (泥?5??
- `[RT-BAR]` ??price/vol/bar_min/cur_min (泥?5??
- `[BAR-CLOSE]` ??留?遺꾨큺 ?뺤젙 ??OHLCV
- `[RT-DATA] ?꾪꽣?쒖쇅` ??肄붾뱶쨌???遺덉씪移???(泥?5??

**寃利앸맂 ?숈옉** (2026-05-04 濡쒓렇):
```
[RT-CB] code='A0166000' type='?좊Ъ?쒖꽭' ?깅줉??[('A0166000', '?좊Ъ?쒖꽭')]  ??[RT-RAW] raw_price='+1038.55' raw_vol='+1'                                  ??[BAR-CLOSE] ts=11:22 O=1038.55 C=1038.80 V=25  (留ㅻ텇 ?뺤긽 ?뺤젙)            ??```

---

### [5] run_minute_pipeline watchdog ?곴뎄 誘명빐??踰꾧렇 ?섏젙 (B35)

**利앹긽**: `[BAR-CLOSE]` 留?遺??뺤긽 ??`[Notify] ???뚯씠?꾨씪??2遺?吏?? ?ъ쟾??諛쒕룞.

**?먯씤** (`main.py` line 424-426):
```python
if not self.model.is_ready():
    log_manager.signal("紐⑤뜽 誘명븰???곹깭 ???덉륫 嫄대꼫?")
    return  # ??notify_pipeline_ran() ?몄텧 ?놁씠 醫낅즺
```
紐⑤뜽 誘명븰???곹깭?먯꽌 STEP 5 吏곸쟾 early return ??`notify_pipeline_ran()` (line 667) ?곴뎄 誘명샇異???watchdog 2遺?寃쎈낫 吏??

**?섏젙**: `return` ?꾩뿉 `self.dashboard.notify_pipeline_ran()` 異붽?.

---

### [6] B14 OFI ?곴뎄 0 ?섏젙 ???좊Ъ?멸??붾웾 肄쒕갚 ?좎꽕

**諛쒓껄 怨꾧린**: 濡쒓렇?먯꽌 `[RT-CB] type='?좊Ъ?멸??붾웾'`???대? ?꾩갑 以묒씤 寃껋쓣 ?뺤씤 ??肄쒕갚留??놁뼱??踰꾨젮吏怨??덉뿀??

**?먯씤**: `?좊Ъ?쒖꽭`(FC0) FID?먮뒗 bid/ask(41/51/61/71)媛 ?놁쓬. `_on_real_data()`?먯꽌 ?쎌뼱????긽 0 ??`ofi.update_hoga()` 誘명샇異???OFI=0 怨좎젙.

**?섏젙**:
- `api_connector.py`: `register_realtime(sopt_type=)` ?뚮씪誘명꽣 異붽? (`"1"` = 湲곗〈 ?좎? 異붽?)
- `realtime_data.py`: `on_hoga` 肄쒕갚 ?뚮씪誘명꽣 + `_on_hoga_data()` ?좎꽕. `start()`?먯꽌 ?좊Ъ?멸??붾웾 異붽? ?깅줉. `_on_real_data()`?먯꽌 bid/ask ?쎄린 ?쒓굅 ??`_last_bid1/ask1` ?ъ슜
- `main.py`: `_on_hoga_update()` ?좎꽕, `_on_tick_price_update`?먯꽌 OFI 肄붾뱶 ?쒓굅

---

## 2026-04-30 (?대쾲 ?몄뀡)

**?묒뾽**: SIMULATION 肄붾뱶 ?꾨㈃ ?쒓굅 + ?먮룞 醫낅즺 + ?⑤꼸 ?댁쟾 ?곗씠??吏??+ ?깆옣 異붿씠 ??쒕낫??
### 而ㅻ컠 3嫄?
| 而ㅻ컠 | ?댁슜 |
|---|---|
| `4ae73ae` | refactor: SIMULATION/?붾? 紐⑤뱶 肄붾뱶 ?꾨㈃ ?쒓굅 |
| `5f1919b` | feat: ?쇱씪 留덇컧 ???먮룞 ?꾨줈洹몃옩 醫낅즺 + ?щ옓 ?뚮┝ |
| `8ae19eb` | feat: ?먭??숈뒿쨌?④낵寃利??댁쟾 ?곗씠??吏??+ ?깆옣 異붿씠 ??쒕낫??|

---

### [1] SIMULATION 肄붾뱶 ?꾨㈃ ?쒓굅 (commit: 4ae73ae)

**諛곌꼍**: 濡쒓렇??"?붾? 紐⑤뜽 二쇱엯", "紐⑤뱶=SIMULATION"??異쒕젰 ??誘몃Ⅵ?대뒗 ?ㅼ쟾 ?쒖뒪?쒖씠誘濡?SIMULATION 遺꾧린 ?먯껜媛 遺덊븘?? 紐⑥쓽?ъ옄???ㅼ? API 怨꾩쥖 ?덈꺼?먯꽌留??쒖뼱.

**?쒓굅??肄붾뱶:**

| ?뚯씪 | ?쒓굅 ?댁슜 |
|---|---|
| `main.py` | `--mode` argparse, `self.mode`, ?붾? 紐⑤뜽 二쇱엯 釉붾줉, `stop_sim_timer()` ?몄텧, `argparse` ?꾪룷??|
| `dashboard/main_dashboard.py` | `sim_mode` ?뚮씪誘명꽣, `_sim_timer`, `_start/_stop_sim_timer()`, `_sim_tick()` 130以?|
| `model/multi_horizon_model.py` | `force_ready_for_test()` ?붾? 紐⑤뜽 二쇱엯 硫붿꽌??|
| `config/settings.py` | `TRADE_MODE = "SIMULATION"` ?곸닔 |

**寃곌낵**: `python main.py` ?⑥씪 寃쎈줈. 紐⑥쓽/?ㅼ쟾 援щ텇? ?ㅼ? 怨꾩쥖 ?덈꺼 ?꾩슜.

---

### [2] ?쇱씪 留덇컧 ???먮룞 醫낅즺 + ?щ옓 ?뚮┝ (commit: 5f1919b)

**?먮쫫**: 15:40 `_scheduler_tick` ??`daily_close()` ?꾨즺 ???щ옓 醫낅즺 ?뚮┝ ??`QTimer.singleShot(15_000, _auto_shutdown)` ??`_qt_app.quit()`

**?щ옓 醫낅즺 ?뚮┝ ?댁슜**: 嫄곕옒??/ ?뱁뙣 / ?밸쪧 / PnL / ?ы븰??寃곌낵 / ?ㅼ쓬 ?쒖옉 ?덈궡 (?댁씪 08:45)

**15珥??湲??댁쑀**: Slack ???뚯빱媛 HTTP ?꾩넚(理쒕? 5珥? + rate-limit 1珥?嫄?泥섎━ ?湲? Qt ?대깽??猷⑦봽??怨꾩냽 ?뚯븘 UI 諛섏쓳 ?좎?.

**?좉퇋 硫붿꽌??*: `_auto_shutdown()` ??`logger.info` + `log_manager.system` + `_qt_app.quit()`

---

### [3] ?먭??숈뒿쨌?④낵寃利씲룹텛???⑤꼸 ?댁쟾 ?곗씠??吏??(commit: 8ae19eb)

**臾몄젣**: ?ъ떆????08:45~09:00 ?ъ씠 ?뚯씠?꾨씪??誘몄떎??援ш컙???먭??숈뒿/?④낵寃利??⑤꼸??鍮덇컪 ?쒖떆.

**?닿껐**: `_restore_panels_from_history()` ?좎꽕 ??濡쒓렇????500ms ??DB ?대젰?쇰줈 ???⑤꼸 ?좎“??
- EfficacyPanel: trades.db/predictions.db 荑쇰━ ???댁젣源뚯? ?꾩쟻 ?곗씠??利됱떆 ?쒖떆
- LearningPanel: GBM ?곹깭쨌raw candle ????DB 湲곕컲 媛?利됱떆 ?쒖떆
- TrendPanel: ??二????곌컙 吏묎퀎 利됱떆 ?쒖떆

**?ㅻ깄?????*: `daily_close()` ??`save_daily_stats()` ??SGD?뺥솗?꽷룰?利앷굔?섎? `daily_stats` ?뚯씠釉붿뿉 ?곸냽. ?ㅼ쓬??SGD ?뺥솗???쒖떆???ъ슜.

---

### [4] ?뱢 ?깆옣 異붿씠 ??쒕낫???좎꽕 (commit: 8ae19eb)

**?좉퇋 ?대옒??*: `TrendPanel` (~200以? ??以묒븰 ??7踰덉㎏ `"?뱢 ?깆옣 異붿씠"`

**援ъ꽦**:
- ?곷떒 ?ㅽ뙆?щ씪??3以? PnL `?곣뻷?꺿뻹?끸뻻?뉍뻽` / ?밸쪧 / SGD?뺥솗??(理쒓렐 20??
- 4?? ?쇰퀎(30?? / 二쇰퀎(12二? / ?붾퀎(12媛쒖썡) / ?곌컙
- 媛??? 湲곌컙쨌嫄곕옒쨌???㉱룹듅瑜졖텾nL(??쨌SGD?뺥솗???쇰퀎留? ?ㅽ겕濡??뚯씠釉?- ?됱긽: ?밸쪧 湲곗?(??0%珥덈줉/??3%泥?줉/??5%二쇳솴/<45%鍮④컯), PnL(?묒닔珥덈줉/?뚯닔鍮④컯)

**媛깆떊 ?쒖젏**: ?쒖옉 ?좎“??+ 15:40 ?쇱씪 留덇컧 ???먮룞 媛깆떊

**?좉퇋 DB 湲곕뒫** (`utils/db_utils.py`):
- `daily_stats` ?뚯씠釉? date/trades/wins/pnl_krw/sgd_accuracy/verified_count
- `save_daily_stats()` / `fetch_trend_daily/weekly/monthly/yearly()`
- 吏묎퀎 荑쇰━??trades.db 吏곸젒 GROUP BY (蹂꾨룄 ?뚯씠釉?遺덊븘??

**???쒖꽌 蹂寃?*: ?ㅼ씠踰꾩쟾??SHAP/泥?궛/吏꾩엯/?쭬?먭??숈뒿/?렞?④낵寃利?**?뱢?깆옣異붿씠**/?뚰뙆遊?
---

## 2026-04-30 (?ъ빞 ?몄뀡)

**?묒뾽**: ?렞 ?숈뒿 ?④낵 寃利앷린 ?⑤꼸 ?좎꽕 ???먭??숈뒿???ㅼ젣濡??섏씡??湲곗뿬?섎뒗媛 ?쒓컖??
### EfficacyPanel 援ы쁽

**?듭떖 吏덈Ц**: "?믪? ?좊ː???덉륫???ㅼ젣濡??덉쓣 踰꾨뒗媛?"

#### ?좉퇋 ?뚯씪쨌?⑥닔

- `utils/db_utils.py`: 寃利?荑쇰━ 4醫?異붽?
  - `fetch_calibration_bins(days_back=30)` ??confidence 援ш컙蹂?5?⑥쐞) ?ㅼ젣 ?곸쨷瑜?  - `fetch_grade_stats()` ???깃툒蹂?嫄댁닔/?밸쪧/?됯퇏pts/?⑷퀎pts
  - `fetch_regime_stats()` ???덉쭚蹂?嫄댁닔/?밸쪧/?됯퇏pts
  - `fetch_accuracy_history(limit=200)` ??理쒓렐 N媛??덉륫 correct ?대젰
- `dashboard/main_dashboard.py`: `class EfficacyPanel` (~250以? ?좎꽕
  - Section 1: ?좊ː??罹섎━釉뚮젅?댁뀡 ?뚯씠釉?(?볦슦???덉뼇???꿸낵?뚯떊猶??쇨낵??
  - Section 2: ?깃툒蹂?留ㅻℓ ?깃낵 ?뚯씠釉?(A/B/C/X/?)
  - Section 3: ?숈뒿 ?깆옣 怨≪꽑 ?ㅽ뙆?щ씪??`?곣뻷?꺿뻹?끸뻻?뉍뻽` + 珥덇린 vs 理쒓렐 ?
  - Section 4: ?덉쭚蹂??깃낵 寃뚯씠吏 諛?(RISK_ON/NEUTRAL/RISK_OFF)
  - ?곷떒 KPI 諛곗? 4媛? ?꾩껜?밸쪧/A?깃툒?밸쪧/罹섎━釉뚮젅?댁뀡?먯닔/?숈뒿?④낵?
  - 醫낇빀 ?됯? 諛곕꼫: ?????좑툘 ?먮룞 ?먯젙
- `DashboardAdapter.update_efficacy(data)` ???꾩엫 硫붿꽌??異붽?
- `main.py`:
  - `_gather_efficacy_stats()` 硫붿꽌??異붽? (DB 荑쇰━ ??dict 諛섑솚)
  - `_efficacy_tick` 移댁슫??異붽?
  - 5遺꾨쭏??`_efficacy_tick % 5 == 1`) `update_efficacy()` ?몄텧

#### ???쒖꽌 蹂寃?- 湲곗〈: ?ㅼ씠踰꾩쟾??SHAP/泥?궛/吏꾩엯/?쭬?먭??숈뒿/?뚰뙆遊?- 蹂寃? ?ㅼ씠踰꾩쟾??SHAP/泥?궛/吏꾩엯/?쭬?먭??숈뒿/**?렞?④낵寃利?*/?뚰뙆遊?
---

## 2026-04-30 (????몄뀡)

**?묒뾽**: ?먯씡 異붿씠 ?⑤꼸 ?좎꽕 ???쇰퀎쨌二쇰퀎쨌?붾퀎 ?꾩쟻 P&L ?뚯씠釉?
### PnlHistoryPanel 援ы쁽
- 5痢?紐⑤땲?곕쭅 濡쒓렇??6踰덉㎏ ??**"?뱤 ?먯씡 異붿씠"** 異붽?
- **?붿빟 移대뱶 6媛?*: 嫄곕옒?셋룹킑嫄곕옒쨌珥앹듅瑜졖룹킑?먯씡쨌理쒕?MDD쨌理쒖옣?곗듅 ???됱긽 議곌굔遺 媛깆떊
- **?쇰퀎 ?뚯씠釉?* (60??理쒖떊?믨뎄): ?좎쭨쨌嫄곕옒쨌?뮤룻뙣쨌?밸쪧쨌P/L pt쨌P/L?먃룸늻?곸썝
  - ?섏씡?? ?고븳 珥덈줉(15,45,25) / ?먯떎?? ?고븳 鍮④컯(50,18,18) ??諛곌꼍
  - ?뱀씪 ???⑹깋 + 蹂쇰뱶 媛뺤“
- **二쇰퀎 ?뚯씠釉?* (13二?: MDD??而щ읆 異붽?
- **?붾퀎 ?뚯씠釉?*: ?ㅽ봽 吏??(?????쇰퀎 PnL ?곗쑉????52) 異붽?
  - ?ㅽ봽 ??.0: 珥덈줉 / ??.5: ?몃옉 / <0: 鍮④컯
- `QTableWidget` ?ㅽ겕?뚮쭏 ?ㅽ??쇰쭅, `QHeaderView.Stretch` ?꾩껜 而щ읆 ?먮룞 鍮꾩쑉 遺꾨같

### ?곗씠???먮쫫
- `db_utils.fetch_pnl_history(limit_days=90)`: 泥닿껐 ?꾨즺 嫄곕옒 SELECT
- `main._refresh_pnl_history()`: `_post_exit()` + `daily_close()` + `_restore_daily_state()` 3怨??몄텧
- ?꾪룷?? `QTableWidget쨌QTableWidgetItem쨌QHeaderView` 異붽?

---

## 2026-04-30 (?ㅽ썑 ?몄뀡)

**?묒뾽**: ?ъ떆???곗냽?????뱀씪 嫄곕옒 ?대젰 ??쒕낫??蹂듭썝 + ?몄뀡 移댁슫??+ UI 媛쒖꽑

### PnL ??媛깆떊 ?꾨씫 ?섏젙 [B27/B28]
- `_post_exit()`: 泥?궛 吏곹썑 `update_pnl_metrics()` + `append_pnl_log()` 利됱떆 ?몄텧
- `_execute_entry()`: 吏꾩엯 ??`append_pnl_log()`濡?吏꾩엯 ?대깽??PnL ??湲곕줉

### UI ?고듃 ?쒖씤??媛쒖꽑
- ?꾩껜 ?섎뱶肄붾뵫 `font-size:Xpx` ??`S.f(X)` 援먯껜 (?뱁엳 5痢?紐⑤땲?곕쭅 濡쒓렇 QTextEdit)
- `ScreenScale` ?꾨㈃ ?ъ옉?? `fit_scale = min(sw/1680, sh/1000)` + `dpi_bonus=(dpr-1)횞0.10`
  - 3840횞2160 @ 150% DPI ???먮룞 1.45횞 ?곸슜 (湲곗〈 1.30횞 怨좎젙)
  - `S.info()` ?ㅻ뜑??`3840횞2160 (DPI 1.50횞 UI 1.45횞)` ?쒖떆

### ?ъ떆???곗냽??[B29]
- **`PositionTracker.restore_daily_stats(rows)`**: trades.db ?뱀씪 ?됱쑝濡??쇱씪 PnL쨌?뱁뙣 ?듦퀎 ?ъ쟻??- **`LogPanel.append_restore(key, msg, ts, val)`**: ?댄깶由?룻쉶??`[蹂듭썝]` ?쒓렇 ??ぉ ?쒖떆
- **`LogPanel.append_separator(key, msg)`**: ????`<hr>` 援щ텇??- **`DashboardAdapter`**: `append_restore_trade/pnl()`, `append_trade/pnl_separator()` 異붽?
- **`db_utils.fetch_today_trades(today_str)`**: ?뱀씪 泥닿껐 嫄곕옒 SELECT ?ы띁
- **`main._increment_session()`**: `data/session_state.json`???뱀씪 ?몄뀡 踰덊샇 ?꾩쟻
- **`main._restore_daily_state()`**: `run()` ??`dashboard.show()` 吏곹썑 ?몄텧
  - trades.db ?뱀씪 ???ъ깮 ??二쇰Ц/泥닿껐쨌?먯씡 ??뿉 [蹂듭썝] ?댄깶由???ぉ
  - ?몄뀡 援щ텇??`?? ?몄뀡 #N ?쒖옉 ??X嫄?蹂듭썝 ??`
  - `position_tracker.restore_daily_stats()` ?곕룞

---

## 2026-04-30 (?ㅼ쟾 ?몄뀡)

**?묒뾽**: ??쒕낫???쒕? FILL ?댁긽媛寃??댁긽??吏꾨떒 + ?쒕?/?ㅺ굅??遺꾨━ ?섏젙

### ?댁긽??吏꾨떒
- 濡쒓렇: `[FILL] FILL 留ㅻ룄 5怨꾩빟 @388.48 ?щ━?쇱? 1.4?? ???ㅺ굅??媛寃?~1007pt)怨??鍮?鍮꾩젙??媛寃?- **?먯씤**: `MireukDashboard`媛 `kiwoom=None`?쇰줈 ?앹꽦?섎㈃ 臾댁“嫄?`_start_sim_timer()` ?몄텧. ??대㉧??珥덇린 媛寃⑹씠 `388.50` ?섎뱶肄붾뵫 ???ㅼ? ?곌껐 ?????섏큹~?섏떗珥??숈븞 ?쒕? FILL 濡쒓렇(388.xx)媛 二쇰Ц/泥닿껐 ??뿉 異쒕젰??- ?ㅼ젣 嫄곕옒 ?곹뼢: ?놁쓬 (UI ?⑤꼸 異쒕젰留? `position_tracker` 誘몄쁺??

### ?섏젙 (`dashboard/main_dashboard.py`, `main.py`)
- `MireukDashboard.__init__(sim_mode=True)` ?뚮씪誘명꽣 異붽? ??`sim_mode=False`?대㈃ ??대㉧ 誘몄깮??- `DashboardAdapter.__init__(sim_mode=True)` + `create_dashboard(sim_mode=True)` ?숈씪?섍쾶 ?꾪뙆
- `main.py`: `create_dashboard(sim_mode=(self.mode == "SIMULATION"))` ??live 紐⑤뱶???쒕? ??대㉧ ?먯껜 ?놁쓬
- `main.py`: `stop_sim_timer()` ?몄텧??`if self.mode == "SIMULATION":` 議곌굔 ?대?濡??대룞
- `_sim_tick()` FILL/PENDING 濡쒓렇 ?욎뿉 `[SIM]` ?묐몢??異붽?

---

## 2026-04-29 (?쇨컙 ?몄뀡)

**?묒뾽**: 硫???몃씪?댁쫵 ?덉륫 ?곗씠???먮쫫 ?먭? + 2媛?踰꾧렇 ?섏젙

### 吏꾨떒
- ??쒕낫?쒖뿉??1遺?30遺?6媛?移대뱶媛 紐⑤몢 ?숈씪??媛?72.2%) ?쒖떆
- ?먯씤 1 (?ㅺ굅??: `main.py` `_preds_ui` 援ъ꽦 ??`1-confidence` 洹쇱궗 ??3?대옒???뺣쪧 ?⑹궛 ?ㅻ쪟
- ?먯씤 2 (?쒕?): ?⑥씪 `trend` 媛믪쑝濡?6媛??몃씪?댁쫵 ?앹꽦 ??媛?遺꾩궛 ?놁쓬

### ?섏젙
- **main.py** L359-361: `_preds_ui` ?뺣쪧媛믪쓣 `r["up"]`/`r["down"]`/`r["flat"]` 吏곸젒 李몄“
- **main_dashboard.py** L1555-1563: ?몃씪?댁쫵蹂??낅┰ ? `[0.06, 0.08, 0.10, 0.13, 0.16, 0.20]` ?곸슜. `hold` ??`flat` ???듭씪

---

## 2026-04-29 (?ㅽ썑 ?몄뀡)

**?묒뾽**: ??쒕낫??3媛????곗씠??諛곗꽑 ?꾩꽦 + 踰꾧렇 7醫??섏젙

### 二쇰Ц/泥닿껐 ???댄똻
- `_ORDER_TAB_TIP` ?곸닔: 吏꾩엯 ?먮쫫(???? + 泥?궛 ?먮쫫(P1~P6) HTML ?붿빟
- `QToolTip` CSS ?ㅽ겕?뚮쭏, `setTabToolTip()` ?곸슜

### ?몄씤 ?곗씠??"-" ?먯씤 吏꾨떒 諛??섏젙 [B16~B18]
- **洹쇰낯 ?먯씤**: `InvestorData` ?꾪룷?맞룹씤?ㅽ꽩?ㅽ솕 ?놁쓬 ??`feature_builder.build(supply_demand=None)` 怨좎젙
- `main.py`: `InvestorData` import + `__init__` ?몄뒪?댁뒪??+ STEP 4 `fetch_all()` + `supply_demand` ?꾨떖
- `main.py` STEP 4 ?? `update_divergence()` 留ㅻ텇 ?몄텧 (rt_bias/fi_bias/contrarian/div_score 怨꾩궛)
- `DivergencePanel.update_data()`: fi_call/fi_put/fi_strangle 移대뱶 setText ?꾨씫 異붽?
- `connect_kiwoom()`: `investor_data._api = self.kiwoom` 二쇱엯
- `daily_close()`: `investor_data.reset_daily()` 異붽?

### 泥?궛 愿由????곗씠??諛곗꽑 [B23~B25]
- **洹쇰낯 ?먯씤**: `main.py`??`update_position()` ?몄텧 ?놁쓬 ??泥?궛 ?⑤꼸???ㅼ젣 ?ъ????곗씠??誘몄쟾??- **B23** (`main.py`): STEP 8 吏곹썑 `update_position()` 異붽? ??`PositionTracker` ?ㅼ젣 媛?`stop_price`=?몃젅?쇰쭅 ?ㅽ넲, `tp1_price`, `tp2_price`, `entry_time`, `partial_1/2_done`) ?꾨떖
- **B24** (`ExitPanel.update_data()` ?ъ옉??:
  - `status='FLAT'` ??`_reset_display()` ??紐⑤뱺 ?꾨뱶 "?붴? 珥덇린??  - `trail_stop` = ?꾩옱 `stop_price` (?몃젅?쇰쭅 ?대룞 諛섏쁺), `hard_stop` = entry짹ATR횞1.5 (理쒖큹媛?
  - 誘몄떎???먯씡: `(cur?뭙ntry) 횞 mult 횞 qty 횞 500,000?? (LONG/SHORT 諛⑺뼢 諛섏쁺)
  - 蹂댁쑀 ?쒓컙: `entry_time`?먯꽌 寃쎄낵 遺?怨꾩궛
  - 遺遺꾩껌??諛? `partial1`/`partial2` ?뚮옒洹???"?꾨즺/?湲? + ?꾨줈洹몃젅?ㅻ컮 100/0
- **B25** (?쒕? 猷⑦봽): `status='LONG'` ??異붽?, `stop`/`tp1`/`tp2` 援ъ“?? `partial1`/`partial2` ??湲곕컲 ?쒕?

### 吏꾩엯 愿由???踰꾧렇 4醫??섏젙 [B19~B22]
- **B19**: 泥댄겕由ъ뒪???됯?瑜?CB쨌?쒓컙 議곌굔 釉붾줉 諛뽰쑝濡?遺꾨━ ??FLAT+諛⑺뼢 ?덉쑝硫???긽 ?됯?
- **B20**: `checks.get(attr, None)` ??None?대㈃ ?뚯깋 "?? (湲곗〈: 鍮?dict ??鍮④컙 X)
- **B21**: `update_entry(qty=0)` ?뚮씪誘명꽣 + `e_qty` ?쇰꺼 媛깆떊
- **B22**: `EntryPanel.update_stats()` + `DashboardAdapter.update_entry_stats()` 異붽?, STEP 9 ??留ㅻ텇 ?몄텧

---

## 2026-04-28 (?ㅽ썑 ?몄뀡)

**?묒뾽**: 紐⑥쓽?ъ옄 ?ㅺ굅??寃利?+ ?댁긽??吏꾨떒쨌?섏젙 + ??쒕낫???곗씠??諛곗꽑 ?꾩꽦

### Path B ?명봽??援ъ텞 (而ㅻ컠 60233d6)
| ?뚯씪 | ?댁슜 |
|---|---|
| `config/settings.py` | `RAW_DATA_DB` 寃쎈줈 異붽? |
| `utils/db_utils.py` | `raw_candles` + `raw_features` ?뚯씠釉? save/get ?⑥닔 4媛?異붽? |
| `main.py` STEP 4 | `save_candle(bar)` + `save_features(ts, features)` ?몄텧 ??13嫄곕옒???곗씠??異뺤쟻 ?쒖옉 |
| `learning/prediction_buffer.py` | actual ?쇰꺼: `raw_candles` ?ㅼ쥌媛 湲곕컲 怨꾩궛?쇰줈 援먯껜 (placeholder ?쒓굅) |
| `utils/logger.py` | DEBUG ?덉씠??`logging.DEBUG` 怨좎젙 (INFO ?덈꺼??debug() 異쒕젰 李⑤떒?섎뜕 踰꾧렇 ?섏젙) |

### ?붾쾭洹?濡쒓렇 異붽? (而ㅻ컠 60233d6)
`[DBG-F4]` ATR floor + ?듭떖 ?쇱쿂 / `[DBG-F6]` ?몃씪?댁쫵蹂??덉륫 / `[DBG-CB]` CB ?곹깭 /
`[DBG-F7]` 吏꾩엯 4議곌굔 / `[DBG-F7a]` 泥댄겕由ъ뒪??9??ぉ / `[DBG-F7b]` ?ъ씠? ?낆텧??/
`[DBG-F8]` ?ъ????먯젅쨌TP쨌誘몄떎??PnL / `[DBG-STOP]` ?섎뱶?ㅽ넲 諛쒕룞 ?뺣낫

### ??쒕낫???곗씠??諛곗꽑 ?꾩꽦 (而ㅻ컠 c8018ed)
| 踰꾧렇 | ?섏젙 |
|---|---|
| ?좊ː??`lbl_conf` ??긽 "??%" | `PredictionPanel.update_data(conf=)` ?뚮씪誘명꽣 異붽? |
| ?몃씪?댁쫵 移대뱶쨌泥댄겕由ъ뒪??媛깆떊 ?덈맖 | `run_minute_pipeline` ?먯꽌 `update_prediction()` + `update_entry()` 留ㅻ텇 ?몄텧 |
| 5痢?濡쒓렇 ??1쨌2쨌3 鍮??붾㈃ | `log_manager.subscribe()` SYSTEM/TRADE/LEARNING 諛곗꽑 ?곌껐 (`__init__`?먯꽌) |
| PnL ?섏튂 "+12,000?? ?섎뱶肄붾뵫 | `LogPanel.update_pnl_metrics()` 異붽?, 留ㅻ텇 ?ㅼ떆媛??꾩넚 |

### ?ㅺ굅???댁긽???섏젙 (而ㅻ컠 5db134e)
| # | ?댁긽??| ?섏젙 |
|---|---|---|
| B13 | CVD buyvol=100% ??FC0 FID10 遺?멸? ??諛⑺뼢 ?꾨떂 | tick test (prev_price 鍮꾧탳 Lee-Ready 洹쇱궗)濡?援먯껜 |
| B15 | ?먯젅媛 ?꾨땶 close媛濡?泥?궛 (??긽 遺덈━) | `_check_exit_triggers(bar=)` ?꾨떖, exit_price = stop_price 蹂댁젙 |

### 誘명빐寃??댁뒋
| # | ?댁슜 |
|---|---|
| B14 | bid/ask=0 ??FC0??FID41/51 誘명룷?? FH0(?좊Ъ?멸??붾웾) 蹂꾨룄 ?깅줉 ?꾩슂 ??OFI ?곴뎄 0 |

### ?ㅺ굅???ㅽ뻾 寃곌낵 (濡쒓렇 湲곕컲)
- ATR floor 0.75pt ?꾩쟾 寃利?(`stop_dist=0.75pt` ?뺥솗???뺤씤)
- 泥댄겕由ъ뒪??8/9 ?뺤긽 ?됯? (foreign 誘멸뎄??1媛쒕쭔 ??
- 吏꾩엯 LONG @1008.40, stop=1007.65 ?뺤긽 吏꾩엯
- stop_dist=-0.15pt ???먯젅 諛쒕룞 ?덉긽 (TRADE 濡쒓렇 蹂꾨룄 ?뺤씤)
- CVD/OFI 0媛? CVD??3遺??댁긽 ?꾩쟻 ??怨꾩궛?섎?濡?珥덇린 0 ?뺤긽

---

## 2026-04-27 (?ㅼ쟾~?ㅽ썑 ?몄뀡)

**?묒뾽**: ?ㅼ떆媛?遺꾨큺 ?뚯씠?꾨씪??end-to-end ?뺤긽 ?숈옉 ?ъ꽦

### ?듭떖 踰꾧렇 ?섏젙 (7嫄?

| # | ?뚯씪 | 踰꾧렇 | ?섏젙 |
|---|---|---|---|
| B06 | api_connector.py | 洹쇱썡臾?肄붾뱶 ?щ㎎ ?ㅻ쪟 (`101W06` ?좎쭨怨꾩궛 fallback) | `GetFutureCodeByIndex(0)` = `A0166000` 0?쒖쐞 異붽? |
| B07 | constants.py | `RT_FUTURES="FC0"` ??Kiwoom sRealType? ?쒓뎅??紐낆묶 | `"FC0"` ??`"?좊Ъ?쒖꽭"`, `"FH0"` ??`"?좊Ъ?멸??붾웾"` |
| B08 | api_connector.py | GetRepeatCnt record_name fallback ?ㅻ쪟 (`or rq_name`) | `meta.get("record_name","")` ??鍮?臾몄옄??洹몃?濡??꾨떖 |
| B09 | emergency_exit.py | `PositionTracker.get_position()` ?놁쓬 (AttributeError) | ?띿꽦(`status`/`quantity`/`entry_price`) 吏곸젒 ?쎄린 + `set_futures_code()` 異붽? |
| B10 | main.py | `run_minute_pipeline` ??candle `ts`媛 datetime 媛앹껜?몃뜲 str 痍④툒 | `ts_raw.strftime(...)` 蹂??異붽? |
| B11 | main_dashboard.py | `PredictionPanel._build()`?먯꽌 `_hz_labels` 誘몄큹湲고솕 | `_build()` 留??욎뿉??dict 珥덇린??|
| B12 | main_dashboard.py | `mk_val_label(align=...)` ?뚮씪誘명꽣 ?놁쓬 (TypeError) | `align=None` ?뚮씪誘명꽣 異붽? |

### 湲곕뒫 異붽?
- ??쒕낫???ㅻ뜑 ?곗륫: ?댁긽???꾨옒??而ㅻ컠 ?댁떆(`#4a00e5e`) ?쒖떆

### 寃利?寃곌낵
- `GetFutureCodeByIndex(0)='A0166000'` ??洹쇱썡臾?肄붾뱶 ?뺤젙
- `type=?좊Ъ?쒖꽭` ???뺤긽 ?섏떊 ?뺤씤
- `on_candle_closed` ??`run_minute_pipeline` ?몄텧 ?뺤씤 (?뚯씠?꾨씪???숈옉)
- ??쒕낫???뺤긽 湲곕룞 ?뺤씤

---

## 2026-04-27 (?덈꼍 ?몄뀡)

**?묒뾽**: dev_memory 援ъ“ ?좎꽕 + CLAUDE.md ?묒꽦
- Claude ?꾨줈?앺듃 硫붾え由?`project_futures.md`, `feedback_kiwoom_com.md`)瑜?dev_memory濡??댁쟾
- CURRENT_STATE / DECISION_LOG / SESSION_LOG / NEXT_TODO ?묒꽦
- CLAUDE.md: ?덈? ?먯튃쨌?뚯씠?꾨씪?맞룻솗瑜?湲곗?쨌Phase ?꾪솴 ?뺣━

---

## 2026-04-26 (?몄뀡 3~4?뚯감 ?⑹궛)

**?묒뾽**: Phase 0~6 ?꾩껜 肄붾뱶 援ы쁽 ?꾨즺

### Phase 0 (?꾨즺)
- ?꾩껜 ?대뜑 援ъ“ ?앹꽦
- config/settings.py, constants.py, logging_system ???명봽??
### Phase 1 (肄붾뱶 ?꾨즺)
- `collection/kiwoom/api_connector.py` ??KiwoomAPI (QAxWidget, 濡쒓렇??TR/?ㅼ떆媛?
- `collection/kiwoom/realtime_data.py` ??FC0 ????1遺꾨큺 議곕┰, OPT10080?뭀PT50029 珥덇린濡쒕뱶
- `collection/kiwoom/latency_sync.py` ??HFT ??꾩뒪?ы봽 ?숆린??(v7.0)
- `main.py` ??QApplication + QTimer ?대깽??猷⑦봽, on_candle_closed ??run_minute_pipeline

**踰꾧렇 ?섏젙**:
- TR 肄붾뱶 OPT10080 ??OPT50029
- COM 肄쒕갚 ?ㅽ깮 ?ㅻ쾭???⑦꽩 ?섏젙
- record_name vs rq_name ?쇰룞 ?섏젙
- GetCommDataEx ??GetCommData
- 洹쇱썡臾?議고쉶 3?④퀎 fallback

### Phase 2 (肄붾뱶 ?꾨즺)
- `safety/kill_switch.py`, `safety/emergency_exit.py`, `safety/circuit_breaker.py`
- `backtest/slippage_simulator.py`, `backtest/transaction_cost.py`
- `backtest/performance_metrics.py`, `backtest/walk_forward.py`, `backtest/report_generator.py`
- `main.py` ??KillSwitch + EmergencyExit ?곌껐

### Phase 3 (肄붾뱶 ?꾨즺)
- Week 8: microprice, lob_imbalance, queue_dynamics, multi_timeframe, htf_filter, round_number, vpin, cancel_ratio
- Week 9: meta_confidence, calibration
- Week 10: vol_targeting, dynamic_sizing
- Week 11: herding, regime_specific, micro_regime, regime_strategy_map

### Phase 4 (肄붾뱶 ?꾨즺)
- RL: environment, ppo_agent, reward_design, policy_evaluator
- 踰좎씠吏?? bayesian_updater
- ?댁뒪: news_fetcher, kobert_sentiment, news_features

### Phase 5 ?ъ쟾 肄붾뵫 (?꾨즺)
- strategy/entry: time_strategy_router, staged_entry, entry_manager
- strategy/exit: exit_manager
- collection/kiwoom: investor_data, option_data
- collection/macro: macro_fetcher
- learning: batch_retrainer, shap_tracker
- dashboard: main_dashboard (5李??ㅽ겕?뚮쭏)

### Phase 6 (肄붾뱶 ?꾨즺)
- ?좎쟾???뚰뙆: alpha_gene, alpha_evaluator, random_searcher, genetic_searcher
- alpha_pool, evolution_engine, alpha_scheduler, bot_main
- ?밴꺽 湲곗?: IC??.02, Sharpe??.8, OOS Sharpe>0, n_samples??00

---

## 2026-04 (珥덇린)

**?묒뾽**: ?꾨줈?앺듃 ?ㅺ퀎
- ?쒖뒪???꾪궎?띿쿂 v4 ?ㅺ퀎 ?꾨즺
- v6.5 蹂댁셿 寃??(?쒓컙?쨌遺꾪븷吏꾩엯쨌硫?고??꾪봽?덉엫쨌誘몄떆?덉쭚 梨꾩슜)
- v7.0 Gemini ?쒖븞 寃????6/6 ?꾨웾 梨꾩슜
- Hurst Exponent 怨듭떇 ?ㅻ쪟 ?섏젙 (reg[0]횞2.0 ??reg[0])
## 2026-05-06 (?몄뀡 留덇컧 ?뺣━)

**?묒뾽**
- `BrokerSync` startup 李⑤떒 ?먯씤??異붿쟻?덇퀬, `OPW20006` ?묐떟???ㅼ젣 誘몃낫?좉? ?꾨땲?쇰룄 blank placeholder row留??ㅻ뒗 寃쎌슦媛 ?덉쓬???뺤씤?덈떎.
- `2026-05-06 10:48:19` ?꾪썑 遺덉씪移?援ш컙??濡쒓렇 湲곗??쇰줈 ?ш뎄?깊뻽怨? 怨쇨굅 濡쒓렇留뚯쑝濡쒕뒗 "二쇰Ц ?ㅽ뙣 ??濡쒖뺄 ?ъ??섏씠 ?대뼡 寃쎈줈濡???λ릱?붿?"瑜?利됱떆 利앸챸?섍린 ?대졄?ㅻ뒗 愿痢?怨듬갚???뺤씤?덈떎.
- `collection/kiwoom/api_connector.py`, `main.py`, `strategy/position/position_tracker.py`??二쇰Ц/硫붿떆吏/泥닿껐/?붽퀬/蹂듭썝 寃쎈줈 ?붾쾭洹몃? 珥섏킌??異붽??덈떎.
- `python -m py_compile main.py collection\kiwoom\api_connector.py strategy\position\position_tracker.py` 寃利앹쓣 ?듦낵?덈떎.

**?듭떖 諛섏쁺**
- `OPW20006` ?붿껌??怨꾩쥖 鍮꾨?踰덊샇瑜??④퍡 二쇱엯?섍퀬, ?묐떟??`nonempty_rows` / `blank_row_count` / `all_blank_rows`濡?遺꾨━??湲곕줉?섎룄濡??섏젙.
- startup broker sync?먯꽌 blank row-only ?묐떟? hard mismatch媛 ?꾨땲??"臾댄룷吏??FLAT) ?꾨낫"濡??댁꽍?섎룄濡?蹂댁젙.
- 二쇰Ц 寃쎈줈??`EntryAttempt`, `EntrySendOrderResult`, `PendingOrder`, `OrderMsgDiag` 異붽?.
- Chejan 寃쎈줈??`ChejanDiag`, `ChejanFlow`, `ChejanMatch`, `EntryFillFlow`, `ExitFillFlow`, `BalanceChejanFlow` 異붽?.
- `position_state.json` ?????`last_update_reason`, `last_update_ts`瑜??④퍡 ?④린怨?蹂듭썝 ??`PositionDiag`濡??몄텧.

**?ㅼ쓬 ?쒖옉 吏곹썑 ?뺤씤 ?쒖꽌**
1. `OPW20006-REQ`, `OPW20006-RESP`, `OPW20006-DIAG`
2. `BrokerSyncFlatPlaceholder` 諛?`BrokerSync` status ?꾩씠
3. `EntryAttempt -> EntrySendOrderResult -> PendingOrder -> OrderMsgDiag -> ChejanFlow`
4. `PositionDiag`
5. 遺덉씪移섍? ?щ컻?섎㈃ `PendingOrder`, `ChejanDiag`, `BalanceChejanFlow`, `PositionDiag`瑜?媛숈? ??꾨씪?몄쑝濡??議?
---

## 2026-05-06 (?몄뀡 留덈Т由?- ?ㅼ떆媛??붽퀬 ?⑤꼸 ?곌껐/蹂댁젙/UI ?뺣━)

**?묒뾽**
- 醫뚯륫 ?곷떒 ?ㅻ뜑??`怨꾩쥖踰덊샇`, `?꾨왂紐? 肄ㅻ낫? ???踰꾪듉???щ같移섑븯怨???媛꾧꺽???뺣젹?덈떎.
- 醫뚯륫 而щ읆??2??援ъ“濡??ы렪???곷떒 `?ㅼ떆媛??붽퀬`, ?섎떒 `硫???몃씪?댁쫵 ?덉륫 + ?뚮씪誘명꽣 遺꾩꽍` ?⑤꼸濡?遺꾨━?덈떎.
- `?ㅼ떆媛??붽퀬` 移대뱶???쇱씠釉?寃뚯씠吏, ?⑷퀎 6媛? 醫낅ぉ蹂??붽퀬 ?뚯씠釉붿쓣 異붽??덈떎.
- `OPW20006` ?묐떟???곷떒 ?⑤꼸???곌껐?섍퀬 startup sync 諛??붽퀬 Chejan ?댄썑 ?먮룞 媛깆떊?섎룄濡??곌껐?덈떎.
- 移대뱶 ?대? 蹂댁“ ?쇰꺼???쒓굅?섍퀬 ?고듃/媛꾧꺽/?ㅼ쓣 ?섎떒 ?⑤꼸怨?留욎톬??
- ?⑷퀎移??뚮젅?댁뒪????愿꾪샇(`[ ]`)瑜??쒓굅?덈떎.

**吏꾨떒**
- `2026-05-06 18:51:29 [BalanceUIFallback]` 濡쒓렇濡??뺤씤??寃곌낵, ?ν썑/臾댄룷吏???곹깭?먯꽌 `OPW20006`??`rows=0` + summary ?꾨? 怨듬??쇰줈 ?대젮?ㅻ뒗 耳?댁뒪媛 議댁옱?덈떎.
- ?곕씪???곷떒 ?⑤꼸??鍮꾨뒗 吏곸젒 ?먯씤? UI ?먯껜蹂대떎 `OPW20006` ?⑤룆 ?묐떟 ?좊ː??遺議깆씠?덈떎.
- `珥앸ℓ留?珥앺룊媛?먯씡/?ㅽ쁽?먯씡/珥앺룊媛/珥앺룊媛?섏씡瑜?異붿젙?먯궛` 6媛쒕? ?꾨? `OPW20006` ?먮Ц留뚯쑝濡???긽 梨꾩슦??寃껋? 遺덉븞?뺥븯?ㅺ퀬 ?먮떒?덈떎.

**諛섏쁺**
- `collection/kiwoom/api_connector.py`
  - `二쇰Ц媛?μ닔?? ?꾨뱶 異붽?.
  - summary single-field probe瑜??섏쭛?섍퀬 ?꾨? blank??寃쎌슦 `[OPW20006-SUMMARY-BLANK]` 濡쒓렇瑜??④린?꾨줉 蹂닿컯.
- `main.py`
  - `_push_balance_to_dashboard()` / `_refresh_dashboard_balance()` 異붽?.
  - startup sync 吏곹썑? ?붽퀬 Chejan ?댄썑 ?붽퀬 ?⑤꼸 ?먮룞 媛깆떊.
  - summary blank????`珥앸ℓ留?珥앺룊媛?먯씡/珥앺룊媛`???붽퀬???⑹궛, `?ㅽ쁽?먯씡`? `daily_stats().pnl_krw`, `珥앺룊媛?섏씡瑜?異붿젙?먯궛`? 怨꾩궛媛?0 湲곕컲 fallback ?곸슜.
  - fallback ?곸슜 ??`[BalanceUIFallback]` 濡쒓렇 異쒕젰.
- `dashboard/main_dashboard.py`
  - `AccountInfoPanel` 異붽? 諛?醫뚯륫 ?곷떒 移대뱶??
  - ?⑷퀎移?湲곕낯 ?쒖떆瑜?怨듬??쇰줈 蹂寃쏀븯怨?`[ ]` ?쒓굅.

**寃利?*
- `python -m py_compile dashboard/main_dashboard.py main.py collection/kiwoom/api_connector.py` ?듦낵.
- ?ㅼ젣 ?ㅼ? ?쇱씠釉?媛믨낵 ?붾㈃媛믪쓽 ?꾩쟾 ?쇱튂 寃利앹? ?ㅼ쓬 ?몄뀡?먯꽌 異붽? ?뺤씤 ?꾩슂.
## 2026-05-08 (7李? - Ensemble upgrade 寃利?泥닿퀎 ?뺣━ + ?④낵寃利?UI ??+ ?먮룞 由ы룷???댄똻 蹂닿컯

**?묒뾽**
- `ENSEMBLE_SIGNAL_UPGRADE_PLAN.md` 湲곗??쇰줈 Sprint 1~4 援ы쁽 ?곹깭瑜??ъ젏寃?섍퀬 臾몄꽌 ?곷떒???꾩옱 ?곹깭, ?ν썑 怨쇱젣, ?④낵 寃利?泥댄겕由ъ뒪?몃? 諛섏쁺.
- `predictions` ?먰솗瑜?`up_prob/down_prob/flat_prob`) ???寃쎈줈? `ensemble_decisions` gating/`toxicity_*` ???而щ읆???먭??섍퀬 ?μ쨷 ??λ텇源뚯? ?뺤씤.
- `A/B`, `Calibration`, `Meta Gate`, `Rollout` 4醫?由ы룷?몃? 二쇨린 ?ㅽ뻾?섎룄濡?`main.py`???곌껐.
  - calibration/meta/rollout: 15遺?二쇨린
  - A/B backtest: 30遺?二쇨린
- 由ы룷???ㅻ깄?룹쓣 `effect_monitor_history.json`???꾩쟻 ??ν븯怨? `dashboard/main_dashboard.py`??`?④낵 寃利? ?⑤꼸???대? ??4媛?`A/B`, `Calibration`, `Meta Gate`, `Rollout`) 異붽?.
- 媛???뿉 ?꾩옱 媛?+ detail + 媛꾨떒 ?ㅽ뙆?щ씪?몄쓣 ?쒖떆?섍퀬, 媛????섎?瑜??댄똻?쇰줈 遺李?

**寃利?*
- `py_compile`濡?`main.py`, `dashboard/main_dashboard.py` 臾몃쾿 寃利??듦낵.
- `EfficacyPanel` ?앹꽦 ???대? 由ы룷????4媛쒓? ?ㅼ젣濡?留뚮뱾?댁??붿? ?뺤씤.
- 由ы룷??4醫??ъ깮???뺤씤:
  - `microstructure_ab_metrics.json`
  - `calibration_metrics.json`
  - `meta_gate_tuning_metrics.json`
  - `rollout_readiness_metrics.json`
- `effect_monitor_history.json` 珥덇린 ?ㅻ깄???앹꽦 ?뺤씤.
- ???댄똻 ?꾨씫 ?먯씤 ?먭?:
  - 理쒖큹?먮뒗 `EfficacyPanel`???꾨땶 ?ㅻⅨ ?⑤꼸 履쎌뿉 ?ㅼ젙?섏뼱 ?ㅼ젣 ??뿏 誘몃컲??  - ?댄썑 `EfficacyPanel._report_tabs.tabBar().setTabToolTip(...)` 寃쎈줈濡??섏젙 ???고???媛앹껜?먯꽌 臾몄옄??議댁옱 ?뺤씤

**?꾩옱 愿李곌컪**
- A/B 理쒓렐 ?ㅻ깄?? `ab_pnl_delta=-3.60pt`, `ab_accuracy_delta=-0.10%p`
- Calibration 理쒓렐 ?ㅻ깄?? `overall_ece=0.399783`
- Meta Gate 理쒓렐 ?ㅻ깄?? `meta_labels=34`, `best_grid.match_rate=41.18%`
- Rollout 理쒓렐 ?ㅻ깄?? `recommended_stage=shadow`

**?먮떒**
- 援ы쁽 踰붿쐞???곷떦 遺遺??꾨즺?먯?留??댁쁺 ?밴꺽 愿?먯뿉?쒕뒗 ?ъ쟾??`shadow` ?좎?媛 ???
- 媛?????꾩냽 怨쇱젣??calibration 媛쒖꽑(temperature scaling ??怨?A/B ?댁쐞 援ш컙 ?먯씤 遺꾩꽍.

---

## 2026-05-08 (8李? - PnL 湲곗? ?듭씪 + trades.db ?뺢퇋??+ ?붽퀬/?먯씡 異붿씠 ?쇱튂??
**?묒뾽**
- ?ㅼ? HTS `?ㅽ쁽?먯씡`, 誘몃Ⅵ???붽퀬 ?⑤꼸 `?ㅽ쁽?먯씡`, `?먯씡 異붿씠` ?ㅻ뒛 ?먯씡???쒕줈 ?ㅻⅤ寃?蹂댁씠???먯씤????텛?곹뻽??
- `logs/20260508_WARN.log`, `trades.db`, `PositionTracker.daily_stats()`瑜??議고빐 ??媛믪씠 ?쒕줈 ?ㅻⅨ ?먯쿇怨??ㅻⅨ 怨꾩궛?앹뿉 臾띠뿬 ?덉쓬???뺤씤?덈떎.
- `utils/db_utils.py`???뺢퇋???먯씡 怨꾩궛 ?⑥닔? `trades` ?뚯씠釉?留덉씠洹몃젅?댁뀡??異붽??덈떎.
- `main.py`??3媛?嫄곕옒 ???寃쎈줈瑜?紐⑤몢 `250,000??pt - ?뺣났 ?섏닔猷? 湲곗? ??μ쑝濡??듭씪?덈떎.
- `?ㅽ쁽?먯씡` fallback 濡쒖쭅??`?ㅻ뒛 ?뺢퇋??嫄곕옒?⑷퀎 -> 留덉?留??뺤긽 釉뚮줈而?媛?-> ?대? daily_stats` ?쒖쑝濡??덉젙?뷀뻽??
- `?먯씡 異붿씠` ?⑤꼸? `entry_ts`媛 ?꾨땲??`exit_ts` 湲곗??쇰줈 ?쇱옄 吏묎퀎瑜??섎룄濡?議곗젙?덈떎.
- ?ъ떆??蹂듭썝 ??`position.restore_daily_stats()` ?꾩뿉 `reset_daily()`瑜??몄텧?섎룄濡??섏젙?덇퀬, `reset_daily()`媛 ?섏닔猷뚮룄 ?④퍡 珥덇린?뷀븯?꾨줉 蹂닿컯?덈떎.

**?듭떖 吏꾨떒**
- 湲곗〈 `?먯씡 異붿씠`??`trades.db.pnl_krw`瑜?洹몃?濡??ъ슜?덈뒗?? ?ㅻ뒛 嫄곕옒 ?덉뿉 怨쇨굅 `500,000??pt` 怨꾩궛媛믨낵 ?좉퇋 `250,000??pt - ?섏닔猷? 怨꾩궛媛믪씠 ?쇱옱???덉뿀??
- 湲곗〈 ?붽퀬 ?⑤꼸 fallback `?ㅽ쁽?먯씡`? `PositionTracker.daily_stats()`瑜?湲곗??쇰줈 ?꾩옱 怨듭떇?쇰줈 ?ъ궛異쒗뻽湲??뚮Ц??DB 吏묎퀎? 利됱떆 ?닿툔?щ떎.
- `OPW20006` summary blank ?묐떟 ??fallback??`0` ?먮뒗 ?대?媛믪쑝濡?踰덇컝????뼱?⑥졇, 媛숈? ?몄뀡 ?덉뿉?쒕룄 `?ㅽ쁽?먯씡`??`-1,985,122 -> 0 -> -1,618,767 -> 0`泥섎읆 ?붾뱾由????덉뿀??

**諛섏쁺**
- `utils/db_utils.py`
  - `normalize_trade_pnl()` 異붽?
  - `trades` ?뚯씠釉붿뿉 `gross_pnl_krw`, `commission_krw`, `net_pnl_krw`, `formula_version` 異붽?
  - 湲곗〈 嫄곕옒???먮룞 ?뺢퇋??migration 異붽?
  - `fetch_today_trades()` / `fetch_pnl_history()`瑜?`exit_ts` 湲곗? + `COALESCE(net_pnl_krw, pnl_krw)` 諛섑솚?쇰줈 ?섏젙
- `main.py`
  - 3媛?嫄곕옒 INSERT 寃쎈줈 紐⑤몢 ?뺢퇋???먯씡 ??μ쑝濡??듭씪
  - `_restore_daily_state()` 蹂듭썝 ??`self.position.reset_daily()` ?몄텧
  - `_ts_push_balance_to_dashboard()` fallback `?ㅽ쁽?먯씡` ?곗꽑?쒖쐞 蹂댁젙
- `strategy/position/position_tracker.py`
  - `reset_daily()`??`_daily_commission = 0.0` 異붽?
- `dashboard/main_dashboard.py`
  - `PnlHistoryPanel.refresh()` 吏묎퀎 湲곗? ?쒓컖??`exit_ts` ?곗꽑?쇰줈 蹂寃?
**寃利?*
- `py_compile`濡?`main.py`, `utils/db_utils.py`, `strategy/position/position_tracker.py`, `dashboard/main_dashboard.py` 臾몃쾿 寃利??듦낵.
- DB migration ?ㅽ뻾 ??`fetch_today_trades('2026-05-08')` ?⑷퀎媛 `-1,618,766???쇰줈 ?뺢퇋??湲곗???留욊쾶 ?듭씪?⑥쓣 ?뺤씤.
- `trades` ?뚯씠釉?議고쉶 寃곌낵 `formula_version = 2`濡??ㅻ뒛 嫄곕옒 27嫄댁씠 紐⑤몢 媛깆떊?섏뿀怨?留덉?留?嫄곕옒 ?덉떆??`gross=375,000`, `commission=8,645`, `net=366,355`濡??뺤긽 ?뺤씤.
## 2026-05-11 Cybos order/fill diagnostics follow-up

- Cybos realtime itself was healthy, but live order/fill verification exposed two integration bugs:
  - `?묒닔` (`order_status=1`) events were arriving with `filled_qty=1`, and the shared Chejan handler treated them as final fills. That caused false entry/exit application at `0.0` or fallback `price_hint=4.88`.
  - minute rollover callback could re-enter the Qt event loop before `current_bar/current_min` were cleared, so the same minute close was emitted repeatedly (`[CybosRT-ROLLOVER]` / `[BAR-CLOSE][CYBOS]` spam).
- Fixes applied:
  - `collection/cybos/realtime_data.py`
    - clear `_current_bar` / `_current_min` before invoking the candle-closed callback to stop duplicate minute-close emissions during re-entrancy.
  - `main.py`
    - extend Cybos no-order-number pending timeout from `60s` to `180s` to tolerate delayed mock acceptance callbacks.
    - add `*_cybos_safe` overrides for Chejan handling so only `status == "泥닿껐"` mutates position state; `?묒닔/?뺤젙?뺤씤/痍⑥냼?뺤씤` now only mark acceptance/pending metadata.
    - entry-fill helper override now treats the pre-fill snapshot as the string form returned by `_ts_get_position_snapshot()` instead of assuming a dict.
- Next validation needed after restart:
  - one Cybos entry should no longer create a fake `@ 0.0` or `@ 4.88` fill before the actual `泥닿껐`.
- repeated `[CybosRT-ROLLOVER] from=09:58 to=09:59` spam should stop.
- `BalanceRefresh` / broker sync should no longer drift into phantom multi-contract residuals after a single-contract trade.

---

## 2026-05-13 (25李?- 泥?궛愿由?遺꾪븷泥?궛/?몃젅?쇰쭅/李⑦듃 留덉빱/?몃?泥닿껐 ?숆린??蹂닿컯)

**?묒뾽**
- `strategy/position/position_tracker.py`
  - TP3/3?④퀎 遺遺꾩껌??怨꾪쉷(`33% / 33% / 34%`)怨?`initial_quantity` 湲곗? stage 怨꾩궛??異붽??덈떎.
  - ?섎룞 `33% / 50% / ?꾨웾` 泥?궛 ?댄썑?먮룄 stage 吏꾪뻾瑜좎씠 ?먯쭊???섎웾 湲곗??쇰줈 ?좎??섎룄濡?`_sync_partial_progress()`瑜??꾩엯?덈떎.
  - `sync_from_broker()`媛 媛숈? 諛⑺뼢 ?ъ????щ룞湲고솕 ??`initial_quantity`, `entry_time`, `stop_price`, `trailing_anchor_price`瑜?蹂댁〈?섎룄濡?蹂닿컯?덈떎.
  - `update_trailing_stop()`??2ATR 援ш컙??`current_price` 湲곗????꾨땲??`trailing_anchor_price` 湲곗? 異붿쟻?쇰줈 諛붽엥??
  - `peek_saved_entry_time()`瑜?異붽????ъ떆????startup sync ?쒖뿉????λ맂 吏꾩엯?쒓컖??蹂듭썝 ?뚰듃濡??ъ슜?????덇쾶 ?덈떎.
- `dashboard/main_dashboard.py`
  - 泥?궛愿由???쓽 `3李?紐⑺몴 34%`瑜??ㅼ젣 TP3? ?곌껐?덇퀬, 遺遺꾩껌??寃뚯씠吏瑜??먯쭊???섎웾 湲곗? 怨꾩빟?섎줈 ?쒓린?섎룄濡??뺣━?덈떎.
  - `?몃젅?쇰쭅 湲곗?`, `?꾩옱 ?ㅽ뻾 ?ㅽ넲`, `珥덇린 ?섎뱶 ?ㅽ넲` ?댄똻??異붽??덈떎.
  - 吏꾩엯留덉빱媛 sync ??理쒖떊 遺꾨큺?쇰줈 ?곕씪媛吏 ?딅룄濡?`sync_active_trade()`?먯꽌 湲곗〈 `entry_ts`瑜?蹂댁〈?섎룄濡??섏젙?덈떎.
- `main.py`
  - 泥?궛愿由??⑤꼸??`pt_value`, `stage_plan`, `trail_basis`瑜??꾨떖?섎룄濡??뺣━?덈떎.
  - stuck exit timeout ??釉뚮줈而??붽퀬濡?癒쇱? ?ш?利앺븯??`_ts_resolve_stuck_exit_pending()` 寃쎈줈瑜?異붽??덈떎.
  - ?몃?吏꾩엯 泥닿껐 ?숆린????`250ms / 1200ms` ?붽퀬 ?ъ“???몃━嫄곕? ?ｌ뼱 Chejan ?쇰? ?꾨씫 ??UI ?붽퀬瑜?釉뚮줈而?湲곗??쇰줈 蹂댁젙?섍쾶 ?덈떎.

**?먯씤 遺꾩꽍 ?붿빟**
- 泥?궛愿由???쓽 `?몃젅?쇰쭅 湲곗?`? ?ㅼ젣 湲곗?媛믪씠 ?꾨땲??`?꾩옱 ?ㅽ뻾 ?ㅽ넲` 蹂듭젣媛믪씠?????쇱씤???④퍡 ?붾뱾??蹂댁???
- ?ㅼ젣 ?붿쭊 履쎌뿉?쒕룄 same-side broker sync媛 ?ㅼ뼱?ㅻ㈃ `_recalculate_levels()`媛 ?대? ?뚯뼱?щ┛ ?ㅽ넲??珥덇린 ?섎뱶?ㅽ넲 履쎌쑝濡??섎룎由????덉뿀??
- 吏꾩엯留덉빱??`sync_active_trade()`媛 ?몄텧???뚮쭏??`entry_ts`瑜??덈줈 ??뼱?⑥꽌 ?쒖쭊???쒖젏 怨좎젙 + ?먯꽑 異붿쟻?앹씠 ?꾨땲???쒕룞湲고솕 ?쒖젏 ?щ같移섃앸줈 蹂댁???
- ?몃?吏꾩엯 `order_no=3970` ?щ???濡쒖뺄??泥닿껐 4嫄대쭔 諛쏆븯怨?釉뚮줈而??붽퀬??5怨꾩빟?댁뼱?? 留덉?留?1怨꾩빟 泥닿껐 ?꾨씫??釉뚮줈而??붽퀬 ?ъ“?뚮줈 蹂댁젙???꾩슂媛 ?뺤씤?먮떎.

**寃利?*
- `python -m py_compile strategy\position\position_tracker.py main.py dashboard\main_dashboard.py config\settings.py`
- `python -m py_compile dashboard\main_dashboard.py`
- `python -m py_compile main.py`

**?⑥? ?뺤씤 ?ъ씤??*
- ?ㅼ젣 ?μ쨷?먯꽌 same-side broker sync媛 ?ㅼ뼱???ㅼ뿉??`stop_price`媛 ?ㅻ줈 臾쇰윭?섏? ?딅뒗吏 濡쒓렇濡??뺤씤 ?꾩슂
- ?몃?吏꾩엯 ?ㅺ퀎??泥닿껐?먯꽌 `[BalanceRefresh] trigger=ExternalFill entry retries=250ms,1200ms` ??UI ?붽퀬媛 釉뚮줈而??섎웾怨??쇱튂?섎뒗吏 ?ш?利??꾩슂

## 2026-05-16 (41李???Threshold ?щ낫??+ Dashboard 媛쒖꽑 + B51 ?ロ뵿??

### 媛쒖슂
- 5??珥?怨좊??숈꽦 ?μ꽭 湲곕컲?쇰줈 `HORIZON_THRESHOLDS` ?щ낫??- Dashboard 媛쒖꽑: PnlHistoryPanel ?뚯뒪 ?좏깮 泥댄겕諛뺤뒪, ?댄똻 由ъ튂 HTML ?꾪솚
- Threshold Monitor: GBM ?ы븰??30遺?二쇨린濡?ATR ?숈쟻 vs Static 鍮꾧탳 紐⑤뜽 AI??湲곕줉
- EmergencyExit pending_registrar 異붽? ??CB 鍮꾩긽泥?궛 Chejan ?몃?泥닿껐 ?ㅻ텇瑜?諛⑹?
- BrokerSync / PositionTracker same-side ?숆린??蹂닿컯
- [B51] DashboardAdapter.chk_slack ?몄텧 ?꾨씫 ??exit code 1 ?щ옒???ロ뵿??
### ?섏젙 ?댁뿭

| ?뚯씪 | 蹂寃?|
|---|---|
| `config/settings.py` | `HORIZON_THRESHOLDS` ?щ낫??(1m 0.0002??.0005, ?꾩껜 ??2.5諛??곹뼢) |
| `dashboard/main_dashboard.py` | `_HZ_TIP` ?좉퇋, `_CB_TIP` ??뒳???뚮┝ ?댁슜 異붽?, `PredictionPanel` ?댄똻 HTML 由ъ튂 ?щ㎎, `PnlHistoryPanel` ?쒕갑????갑??泥댄겕諛뺤뒪 + `_sel_val/_fmt_val/_fmt_single/_mdd_sel/_sharpe_sel/_on_source_changed` 異붽?, `DashboardAdapter.chk_slack` + `_save_ui_prefs` ?꾩엫 異붽? |
| `main.py` | `_threshold_monitor_tick` 移댁슫?? `_log_threshold_monitor()` 硫붿꽌?? GBM ?ы븰??30遺?二쇨린 threshold 湲곕줉, EmergencyExit `pending_registrar` ?곌껐, `_ts_sync_from_balance_payload` EXIT pending 吏꾪뻾 以?pending ?뚮㈇ 諛⑹? |
| `safety/emergency_exit.py` | `pending_registrar` ?뚮씪誘명꽣 異붽?, `set_pending_registrar()` 硫붿꽌??異붽? |
| `strategy/position/position_tracker.py` | same-side sync ??grade 蹂댁〈 (BROKER ??뼱?곌린 諛⑹?), partial_done ?뚮옒洹?蹂댁〈 |

### 踰꾧렇 ?섏젙: B51 (移섎챸)

**利앹긽**: `start_mireuk.bat` ?ㅽ뻾 ??`[Capability]` 濡쒓렇 吏곹썑 `exit code: 1`濡?醫낅즺. `[System] Qt ?대깽??猷⑦봽 吏꾩엯` 誘몄텧??

**?먯씤**: 40李?而ㅻ컠?먯꽌 `MireukDashboard.chk_slack` QCheckBox瑜?異붽??섍퀬 `main.py`??`run()`?먯꽌 `self.dashboard.chk_slack.isChecked()` ?몄텧 肄붾뱶??異붽??덉쑝?? `DashboardAdapter.__init__`??`self.chk_slack = self._win.chk_slack` ?몄텧???꾨씫????`AttributeError`.

**Fix**: `DashboardAdapter.__init__`??`self.chk_slack = self._win.chk_slack` + `_save_ui_prefs` ?꾩엫 硫붿꽌??異붽? (`dashboard/main_dashboard.py` L7286, L7303).

### 寃利?- `start_mireuk.bat` ?ъ떎????Cybos ?곌껐 ?깃났, `[System] Qt ?대깽??猷⑦봽 吏꾩엯`源뚯? 吏꾪뻾 ?뺤씤 (?몄뀡 醫낅즺 ???ш린???꾩슂)
- `py_compile` 臾몃쾿 寃利??꾩슂

### ?⑥? ?뺤씤 ?ъ씤??- Threshold ?곹뼢 ???μ쨷 FLAT 鍮꾩쑉 紐⑺몴 ?ъ꽦 ?щ? (29~37%) ?ㅼ젣 濡쒓렇 ?뺤씤
- PnlHistoryPanel 泥댄겕諛뺤뒪 (?쒕갑????갑???좉?) ?숈옉 ?뺤씤
- 鍮꾩긽泥?궛 ??`pending_registrar` ??Chejan 泥닿껐 留ㅼ묶 濡쒓렇 ?뺤씤

---

## 2026-05-16 세션 마감 (46차: 손익추이 패널 버그 4종 수정)

### 개요
PnlHistoryPanel의 체크박스 필터링 로직 및 손익 계산 버그 4종 일괄 수정.
- 역방향 체크박스가 모든 거래의 forward_pnl을 보여주던 의미론 버그
- 미니선물 pt_value 5배 과대계상 (250k → 50k)
- ui_prefs.json 덮어쓰기로 체크박스 상태가 재시작 후 초기화되던 버그
- 총 손익이 브로커 P&L을 거래 행 수만큼 중복 합산하던 버그

### 수정 내역

| 파일 | 변경 |
|---|---|
|  |   컬럼 추가,  3→4,  추가,  파라미터화,  pt_value 연동 |
|  |  추가,   사용,   로드,  단순화,  추가,  읽고-병합-쓰기로 변경, 브로커 P&L ★ 제거 |
|  |   전달 |

### 버그 수정 상세

#### [B52] 역방향 체크박스 의미론 오류 → 2배 과대계상
- **증상**: 역방향 체크 시 모든 거래의 를 표시, 순+역 모두 체크 시  합산으로 2배
- **원인**:  로직이  필터링이 아닌 pnl 소스 전환이었음
- **Fix**: 로  기준 행 필터링 후 항상  사용

#### [B53] 미니선물 5배 과대계상 (pt_value 하드코딩)
- **증상**: 미니선물(50k)인데 250k로 계산 → 5배 부풀린 pnl_krw DB 저장
- **원인**: 이  하드코딩
- **Fix**:  파라미터 추가, 로 →→ 결정. 버전 v3→v4 bump으로 기존 레코드 재마이그레이션

#### [B54] 체크박스 상태 재시작 후 초기화
- **증상**: 종목/슬랙/서버모드 변경 시 가 pnl_cb_* 키 삭제
- **원인**:  후 파일 덮어씀
- **Fix**: 저장 전 기존 파일 읽고 로 병합

#### [B55] 총 손익 중복 계산
- **증상**: 총 손익이 65,138,190원으로 실제(2,468,190원)의 26배
- **원인**:  — 5/15 11거래 행×6,267,000원
- **Fix**:  기준 고유 날짜 1회만 합산

### 검증
- 총 손익 기대값: +2,468,190원 (일별 누적 마지막값과 일치)
- 미니선물 v4 마이그레이션 시뮬: 5/14 14,501,807원→2,900,361원 (5배 정상화)
-  문법 검사 통과

### 잔여 이슈
- 5/14 DB 2.9M vs 실제 ~1.5M: 수량(qty) 과다 기록 문제 — pt_value와 별개 이슈로 추가 분석 필요
-  변경사항 포함 (이번 세션 외 변경분)

---

## 2026-05-16 세션 마감 (46차: 손익추이 패널 버그 4종 수정)

### 개요
PnlHistoryPanel의 체크박스 필터링 로직 및 손익 계산 버그 4종 일괄 수정.
- 역방향 체크박스가 모든 거래의 forward_pnl을 보여주던 의미론 버그
- 미니선물 pt_value 5배 과대계상 (250k → 50k)
- ui_prefs.json 덮어쓰기로 체크박스 상태가 재시작 후 초기화되던 버그
- 총 손익이 브로커 P&L을 거래 행 수만큼 중복 합산하던 버그

### 수정 내역

| 파일 | 변경 |
|---|---|
| `utils/db_utils.py` | `fetch_pnl_history()` `reverse_entry_enabled` 컬럼 추가, `TRADE_PNL_FORMULA_VERSION` 3→4, `_get_pt_value_from_prefs()` 추가, `normalize_trade_pnl(pt_value=)` 파라미터화, `_migrate_trades_db` pt_value 연동 |
| `dashboard/main_dashboard.py` | `_active_rows()` 추가, `_group()` `_active_rows()` 사용, `refresh()` `reverse_entry_enabled` 로드, `_build_daily/weekly/monthly/summary` 단순화, `_sharpe_grp()` 추가, `_save_ui_prefs()` 읽고-병합-쓰기로 변경, 브로커 P&L 별표 제거 |
| `main.py` | `_trade_metrics_pair` `self._pt_value` 전달 |

### 버그 수정 상세

**[B52] 역방향 체크박스 의미론 오류 → 2배 과대계상**
- 증상: 역방향 체크 시 모든 거래의 forward_pnl_krw를 표시, 순+역 모두 체크 시 exec+fwd 합산으로 2배
- 원인: _sel_val(exec, fwd) 로직이 reverse_entry_enabled 필터링이 아닌 pnl 소스 전환이었음
- Fix: _active_rows()로 reverse_entry_enabled 기준 행 필터링 후 항상 pnl_krw 사용

**[B53] 미니선물 5배 과대계상 (pt_value 하드코딩)**
- 증상: 미니선물(50k)인데 250k로 계산 → 5배 부풀린 pnl_krw DB 저장
- 원인: normalize_trade_pnl이 FUTURES_PT_VALUE=250,000 하드코딩
- Fix: pt_value 파라미터 추가, _get_pt_value_from_prefs()로 ui_prefs.json → symbol_code → get_contract_spec()["pt_value"] 결정. 버전 v3→v4 bump으로 기존 레코드 재마이그레이션

**[B54] 체크박스 상태 재시작 후 초기화**
- 증상: 종목/슬랙/서버모드 변경 시 _save_ui_prefs()가 pnl_cb_* 키 삭제
- 원인: prefs = {새 딕셔너리} 후 파일 덮어씀
- Fix: 저장 전 기존 파일 읽고 prefs.update()로 병합

**[B55] 총 손익 중복 계산**
- 증상: 총 손익이 65,138,190원으로 실제(2,468,190원)의 26배
- 원인: broker_total 계산이 행 단위 반복 — 5/15 11거래 행 × 6,267,000원
- Fix: broker_days 집합 기준 고유 날짜 1회만 합산

### 검증
- 총 손익 기대값: +2,468,190원 (일별 누적 마지막값과 일치)
- 미니선물 v4 마이그레이션 시뮬: 5/14 14,501,807원→2,900,361원 (5배 정상화)
- py_compile 문법 검사 통과

### 잔여 이슈
- 5/14 DB 2.9M vs 실제 ~1.5M: 수량(qty) 과다 기록 문제 — pt_value와 별개 이슈로 추가 분석 필요

---

## 2026-05-17 세션 마감 (47~48차 + DB 초기화)

### 개요
손익추이 주별 탭 이상점 분석 및 수정, trades.db 전체 초기화.

### 수정 내역

**[47차] 주별/월별 브로커 정산값 적용 + MDD 일별 집계 (de10444)**
- _broker_adj_krw(grp): 날짜별로 묶어 broker_pnl 우선 적용
- _mdd_daily(grp): 거래 단위 진동 제거 (5/13 63건 내부 단타 노이즈 차단)
- _build_weekly/_build_monthly: 브로커 정산 원 + 일별 MDD 적용

**[48차] 주별/월별 pt-원 불일치 수정 (e47f27b)**
- 원인: pt는 DB 소스, 원은 broker 정산 혼용 → W20 pt(-27.33pt) 원(+3,446,763원) 모순
- 결정: 주별/월별은 pt+원 모두 DB 일관 사용. 일별 탭만 broker 정산 표시.
- _broker_adj_krw() 제거, _build_weekly/_build_monthly pkrw 복원
- _mdd_daily() DB 전용으로 변경 (broker 미적용, 일별 집계는 유지)

**[DB 초기화]**
- 백업: data/db/trades_backup_20260517.db (92KB, 191건)
- 초기화: trades(191건), daily_stats(10행), daily_broker_pnl(2행) 전체 삭제 + VACUUM
- 목적: 2026-05-19(월)부터 오염 없는 데이터로 손익추이 유효성 검증

### 수정 후 주별 탭 기대 값 (DB 일관)

| 항목 | 수정 전 | 수정 후 |
|---|---|---|
| W20 P/L pt | -27.33pt | -24.93pt |
| W20 P/L 원 | +3,446,763원 (broker 혼용) | -1,599,354원 (DB 일관) |
| W20 방향 | pt(-) 원(+) 모순 | pt(-) 원(-) 일치 |
| W20 MDD | -6,997,034원 (trade 단위) | -5,616,847원 (일별 집계) |

### 설계 원칙 확정

- 일별 탭: broker 정산값 우선 (정확도 최우선)
- 주별/월별 탭: DB 계산값 일관 (pt↔원 방향 보장)
- MDD: trade 단위 아닌 일별 집계 (단타 진동 제거)
## 2026-05-18 세션 마감 (GBM/SHAP 운영 패치 + 중패널 운영화)

### 개요
GBM 배치 재학습 산출물 형식을 런타임 로더와 맞추고, 좌하단 파라미터 중요도/상관계수와 중패널 `동적 피처 (SHAP)` 탭을 실제 데이터 기반 운영 패널로 연결했다. 재시작 직후 복원 로직, SHAP history 호환성 방어, 운영 버튼 흐름, 툴팁 설명까지 함께 정리했다.

### 수정 내역

| 파일 | 변경 |
|---|---|
| `learning/batch_retrainer.py` | scaler 저장, `feature_names.pkl` 저장, DB 기반 feature schema를 가장 풍부한 행 기준으로 선택, `shap_feature_registry.json`의 managed feature set 반영 |
| `main.py` | 상관계수/SHAP 런타임 배선, restored/live 분리, SHAP dashboard payload 구성, feature registry 로드/저장, 운영 버튼 액션(추천 적용/재학습/원복), retrain 후 pending 변경 정리 |
| `learning/shap/shap_tracker.py` | current ranking 외에 최근 rank/쿨다운/교체 로그 조회 메서드 추가, history 길이 불일치 방어 |
| `utils/db_utils.py` | `fetch_recent_raw_features()`, `save_shap_scores()` 추가 |
| `dashboard/main_dashboard.py` | 중패널 SHAP 탭에 운영 플로우 카드 추가, 실데이터 기반 update_shap 확장, 섹션/버튼 툴팁 추가, adapter kwargs 전달 보강 |

### 핵심 결과

- GBM 배치 재학습 결과가 이제 `gbm_*.pkl + scaler_*.pkl + feature_names.pkl` 형태로 저장되어 런타임 `MultiHorizonModel._load_all()`과 일치한다.
- 좌하단 `파라미터 상관계수`는 더 이상 중요도 요약 문자열이 아니라 실제 계산값(`rho`)을 사용한다.
- 재시작 직후 SHAP/상관계수는 저장된 `raw_features`/history를 바탕으로 복원 가능하며, 이후 분봉이 쌓이면 live 상태로 전환된다.
- 중패널 `동적 피처 (SHAP)`은 SHAP current ranking, weekly review, cooldown, replace_log를 이용하는 운영 패널로 확장되었다.
- 운영 버튼 플로우(`추천 1 적용 + 재학습`, `현재 세트 재학습`, `세트 원복`)를 추가하고 `data/db/shap_feature_registry.json` 기반 managed feature set으로 재학습을 제어하도록 설계했다.

### 런타임/디버깅 메모

- 14:22 재시작: `DB_DIR` import 누락으로 `NameError` 발생, 수정 완료.
- 14:27 재시작: `shap_tracker_history.json`의 과거 importance 길이와 현재 feature_names 길이 불일치로 `weekly_review()` / `_find_declining_features()`에서 `IndexError` 발생, history filtering 방어 추가 후 수정 완료.
- 14:28 재시작: 애플리케이션 자체는 SHAP/UI 패치를 통과했고, 최종 종료 원인은 `U-CYBOS/CYBOS Plus is not connected` 외부 브로커 세션 미연결이었다.

### 검증

- `python -m py_compile main.py learning\batch_retrainer.py learning\shap\shap_tracker.py utils\db_utils.py dashboard\main_dashboard.py`
- `create_dashboard()` 및 `dashboard.update_shap(..., action_state=...)` 직접 호출 성공
- 런처 재현으로 SHAP/UI 패치 관련 startup crash 제거 확인 후, 최종 블로커가 CYBOS 미연결 예외임을 확인
## 2026-05-22 (82차 — Micro Regime Warmup UI + 신뢰도 워밍업 명시화)

**Work**: 장중 재시작/초기 구간에 ADX fallback 15.0, `atr_ratio≈1.00` 이 그대로 미시 레짐에 반영되어 헤더 `횡보장` 해석이 과신될 수 있는 문제를 정리했다. 미시 레짐 계산기에 워밍업 메타를 추가하고, 헤더 상단에 `레짐 워밍업` 진행률과 남은 시간을 표시하도록 연결했다.

### 변경 내용

| 파일 | 변경 |
|---|---|
| `collection/macro/micro_regime.py` | 파일 정리 + `warmup` 상태 계산 추가 (`L1 TR/ATR seed` / `L2 ADX warmup` / `L3 ATR avg warmup` / `READY`) |
| `collection/macro/micro_regime.py` | 캔들 버퍼 길이를 `max(adx_window+5, MIN_CANDLES_FOR_ATR+atr_window)` 로 확장해 ATR avg 20샘플이 실제로 다 차기 전에 버퍼 상한에 걸리지 않도록 수정 |
| `main.py` | `_mr["warmup"]` 을 대시보드로 전달하는 훅 추가 |
| `dashboard/main_dashboard.py` | 헤더 `lbl_micro_regime` 아래 워밍업 상태 라벨 + progress bar 추가, `update_micro_regime_warmup()` 어댑터 추가 |

### 핵심 결과

- 미시 레짐은 이제 워밍업 중일 때 `레짐 워밍업` 상태를 명시적으로 보여준다.
- 워밍업 단계는 `L1 → L2 → L3 → READY` 로 구분된다.
- 남은 시간은 `remaining_bars` 기준으로 분 단위 안내된다.
- `ATR avg` 준비가 완료되기 전에는 상단 배지 해석에 보조 설명이 함께 붙는다.
- 캔들 버퍼 길이 부족 때문에 `ATR avg 20샘플` 완료 전에 close buffer가 잘리는 구조적 문제를 함께 수정했다.

### 검증

- `python -m py_compile collection\macro\micro_regime.py dashboard\main_dashboard.py main.py`
- 간단한 시뮬레이션으로 `1, 4, 5, 13, 14, 23, 24분` 지점의 `warmup.level/progress/remaining_bars` 확인
- 완료 시점: `24번째 1분봉` 에서 `READY`

---
## 2026-06-04 (108차 세션 마무리 — CB⑤ 경고 저감 구조 개선 + ProgramTrade probe 루프 중단)

**Work**: 사용자 요청에 따라 파이프라인 경고 지속 원인 4종을 직접 완화했다. EffectReports를 파이프라인 밖으로 분리하고, HealthPolicy degraded 집계를 완화하고, ProgramTrade probe 반복 실패를 실시간 루프에서 중단하고, ConstOut 직후 3분 쿨다운을 추가했다.

### 1. 적용한 구조 개선

| 항목 | 조치 | 파일 |
|---|---|---|
| EffectReports 동기 실행 제거 | 매분 파이프라인 말미 `subprocess.run()` 제거, 전용 `QTimer` + daemon worker로 분리 | `main.py` |
| CB⑤ 1000~1300ms 완화 | degraded warn streak / warn ratio에 soft weight 적용 | `main.py` |
| ProgramTrade probe 루프 중단 | 정기 투자자 데이터 수집에서 `include_program=False` 적용 | `main.py`, `collection/cybos/investor_data.py` |
| ConstOut 직후 heavy cooldown | 180초 동안 추가 scaler refresh / EffectReports / heavy panel refresh 유예 | `main.py` |

### 2. 기대 효과

- `EffectReports` 실패나 지연이 더 이상 CB⑤ 파이프라인 SLA를 직접 밀지 않음
- `1006ms`, `1054ms` 같은 경계값 초과 경고만으로 HealthPolicy가 바로 Degraded Mode에 들어갈 가능성 감소
- `[CybosProbe] ProgramTrade ... -2147221005` 분당 반복 로그 중단
- ConstOut 직후 refit/report/panel 부하 중첩 완화

### 3. 검증

- `python -m py_compile main.py collection\cybos\investor_data.py` 통과
- 장중 실운영 검증은 아직 미실시
- 다음 확인 포인트:
  - WARN.log: CB⑤ 총건수 및 `HealthPolicy` degraded 진입 빈도 감소 여부
  - SYSTEM/WARN.log: `EffectReports`가 worker 경로에서만 도는지 여부
  - SYSTEM/DATA.log: ProgramTrade probe 반복 실패 로그 소거 여부
  - ConstOut 직후 3분 동안 heavy refresh skip 로그 확인

### 4. 잔존 이슈

- EffectReports의 `list index out of range` 자체는 아직 미해결이며, 다만 메인 파이프라인과 분리되어 영향도가 낮아짐
- ProgramTrade는 수동 probe 스크립트로만 추가 진단 가능하며, 운영 타이머에서는 비활성 상태

---

## 2026-06-08 (124차 — v8.0 Phase 0: 시간대 정책·캐스케이드 게이트·FL 감쇠·entry_ok 등)

**Work**: 재학습 불필요 인프라(Phase 0) 구현 14건. main.py 연결·feature_builder 버그 수정은 다음 세션.

| # | 항목 | 파일 |
|---|---|---|
| 1 | TICK_SIZE = 0.05 설정화 | config/settings.py |
| 2 | HORIZON_TIME_POLICY + HORIZON_COLDSTART_MIN_PASS | config/settings.py |
| 3 | compute_cascade_coherence() — 30m→1m 정렬 점수 | model/ensemble_decision.py |
| 4 | select_entry_horizon() — ATR 기반 최적 호라이즌 선택 | model/ensemble_decision.py |
| 5 | FL 조기 감쇠 _fl_streak — FL 70%+ 10분→weight×0.2 | model/ensemble_decision.py |
| 6 | active_horizons 앙상블 적용 — 비활성 weight=0 | model/ensemble_decision.py |
| 7 | CascadeCoherence gate — score < 0.34 차단 | model/ensemble_decision.py |
| 8 | entry_ok 파라미터 — 0.0이면 즉시 X등급 | strategy/entry/checklist.py |
| 9 | is_market_open / minutes_to_close 만기일 15:20 수정 | utils/time_utils.py |
| 10 | scaler_events 컬럼 확장 + 자동 마이그레이션 | model/scaler_monitor_db.py |
| 11 | ScalerMonitorPanel Top5 6컬럼 확장 (raw→pre, μ/σ) | dashboard/panels/scaler_monitor_panel.py |
| 12 | CYBOS_PLUS.bat STEP 0 (close_other_windows.ps1 신규) | CYBOS_PLUS.bat |
| 13 | docs 정리 — 구버전 3개 삭제, V8 통합 계획서 신규 | docs/ |
| 14 | SGD_FEATURE_VECTOR.md 갱신 | docs/ |

**미구현 (다음 세션)**: main.py 연결(active_horizons/entry_ok/select_entry_horizon/cascade_blocked), feature_builder.py 버그 5건

## 2026-06-25 (243차 — Phase 2 재학습 경로 피처 슬라이싱 수정)

### 작업 개요

모델 운영 Audit (Q1~Q3) + V8 구현 현황 검토 후, Audit에서 지적된 최우선 결함 수정.

**Audit 핵심 발견**

| 항목 | 판정 | 핵심 결함 |
|---|---|---|
| Q1: GBM 피처 분리 | ❌ 미분리 | Phase 2 경로(_retrain_phase2)가 horizon_feature_sets.json 슬라이싱 미적용 |
| Q2: 독립 Proba 산출 | ⚠️ 부분 | 입력 봉 데이터는 분리, GBM 피처 공간(97개)은 비분리 |
| Q3: N분봉 완성 주기 배포 | ❌ 설계상 매분 배포 | N분봉은 캐시 갱신 주기, decay 보완 (설계 의도) |

**V8 현황 (242차 기준 정리)**
- Phase 0·1·2 코드 전 항목 완료 ✅
- Phase 2 재학습: 6/8 최초 → EOD_RETRAIN.bat --phase2 누락으로 16일 레거시 덮어씌워짐 → 6/24 재실행으로 복구
- TRAINING_WINDOW_BARS (3m:5000, 5m:3000) 구현 완료 ✅
- SGD 호라이즌별 feat_vec: 구현 불필요 확정 (미래 데이터 오염 위험)
- multi_timeframe.py: dead code — Stage 2~7/8 처리

### 변경 파일

| 파일 | 변경 내용 |
|---|---|
| `learning/batch_retrainer.py` | `_retrain_phase2()`에 Phase C 슬라이싱 블록 추가 |

### 수정 상세

- `get_available_feature_set(hz, use_feat_names)` 호출로 JSON 기반 호라이즌 전용 피처셋 조회
- 슬라이싱 있으면: `X_h_p2 = X_hz[:, h_idx]`, `X_full=X_hz(97개)` → 스케일러 전체 피처 fit 유지
- `_save_feature_names(h_names_p2, horizon_key=hz)` → `feature_names_{hz}.pkl` 저장
- JSON 없거나 분리 불필요 시 fallback(기존 동작) 유지

### 검증

- py310_64 py_compile OK
- 커밋: 2f2cb8e (243차)

### 잔여 항목

- Platt Scaling 호라이즌별 독립 적용: Phase 3 대기
- TRAINING_WINDOW 효과: Stage 3 (50일+) 이후 발현 예정
- Q3 (N분봉 완성 주기): 설계 의도 — 변경 없음

## 2026-06-30 — 브랜치 전략 + 설정 분기

**브랜치 결정**
- maitreya_dist(CREON) → dev merge 완료 (커밋 7170511)
- 향후: dev = 단일 개발 기준선, maitreya_dist = 배포 전용

**설정 분기 추가 (커밋 8d2470b)**
- BROKER_TYPE env var 신설: cybos(MW0601) / creon(MW0602)
- bat 4개에 SET BROKER_TYPE 주입
- set_cybos_credential.py: 양쪽 자격증명 지원
- cybos_autologin.py: 로그 파일명 BROKER_TYPE 기반으로 변경

**다음 단계**: origin/dev push → MW0601 git pull 검증
