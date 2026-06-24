# 미륵이 모델 운영 종합 Audit 보고서

> 작성일: **2026-06-25 (243차)**  
> 기준 브랜치: `dev` / 기준 커밋: `28dcab9`  
> Audit 범위: 모델 피처 분리·Proba 산출·배포 주기 + V8 Phase 0~2 구현 현황

---

## 목차

1. [Audit 질문 및 판정 요약](#1-audit-질문-및-판정-요약)
2. [Q1 — 호라이즌별 GBM 피처는 분리되어 있는가](#2-q1--호라이즌별-gbm-피처는-분리되어-있는가)
3. [Q2 — Proba는 호라이즌별 독립 GBM 피처 그룹으로 산출되는가](#3-q2--proba는-호라이즌별-독립-gbm-피처-그룹으로-산출되는가)
4. [Q3 — Proba는 N분봉 완성 주기로 산출·배포되는가](#4-q3--proba는-n분봉-완성-주기로-산출배포되는가)
5. [V8 구현 현황 (242차 기준)](#5-v8-구현-현황-242차-기준)
6. [243차 수정 사항](#6-243차-수정-사항)
7. [종합 판정표](#7-종합-판정표)
8. [잔여 권고 사항](#8-잔여-권고-사항)

---

## 1. Audit 질문 및 판정 요약

| # | 질문 | 판정 (수정 전) | 판정 (243차 수정 후) |
|---|---|---|---|
| Q1 | 호라이즌별 GBM 피처는 분리되어 있는가 | ❌ 미분리 (Phase 2 경로) | ✅ 수정 완료 (다음 EOD 재학습 시 적용) |
| Q2 | Proba는 호라이즌별 독립 피처 그룹으로 산출되는가 | ⚠️ 부분 | ✅ 수정 완료 (다음 EOD 재학습 시 적용) |
| Q3 | Proba는 N분봉 완성 주기로 산출·배포되는가 | ❌ 설계상 매분 배포 | ❌ 동일 (설계 의도 — 변경 없음) |

---

## 2. Q1 — 호라이즌별 GBM 피처는 분리되어 있는가

### 아키텍처 개요

피처 분리를 담당하는 레이어는 세 단계로 구성된다.

```
featureset by horizon/horizon_feature_sets.json
  └── features/horizon_feature_registry.py
        └── get_available_feature_set(hz, all_feature_names)
              └── learning/batch_retrainer.py (학습 시 슬라이싱)
              └── model/multi_horizon_model.py (추론 시 슬라이싱)
```

`horizon_feature_sets.json`은 2026-06-15 작성, 6개 호라이즌별 피처 목록이 정의되어 있다.

### 수정 전 상태

| 재학습 경로 | 피처 분리 | 근거 |
|---|---|---|
| Phase 1 (`retrain_now`) | ✅ 적용됨 | `get_available_feature_set()` → `X[:, h_idx]` 슬라이싱 후 `_train_horizon()` 호출 |
| Phase 2 (`_retrain_phase2`) | ❌ 미적용 | `use_feat_names`(97개 전체)를 그대로 사용, `h_idx=None` |

**핵심 경위**: 2026-06-24 (242차) `EOD_RETRAIN.bat`에 `--phase2` 플래그가 영구 추가된 이후, Phase 2 경로가 기본 재학습 경로로 고정되었다. 그런데 Phase 2 경로에는 JSON 슬라이싱이 없었으므로 `horizon_feature_sets.json`에 정의된 분리 의도가 실제 모델에 전혀 반영되지 않은 상태였다.

**스케일러 설계**는 의도적으로 전체 피처(97개) 기준을 유지한다. 이는 `predict_proba()` 경로 및 `validate_and_resync()` 체크와의 정합성 보장을 위해서다.

```
스케일러 fit:  X_full(97개) → StandardScaler
GBM 입력:     scaler.transform(X_full)[:, h_idx]  ← 스케일 후 슬라이싱
```

### 수정 후 상태 (243차)

**파일**: `learning/batch_retrainer.py` — `_retrain_phase2()` L928~961

```python
# Phase C: horizon_feature_sets.json 기반 호라이즌별 피처 슬라이싱
_h_names_p2 = None
_h_idx_p2 = None
try:
    from features.horizon_feature_registry import get_available_feature_set as _get_avail_p2
    _h_names_p2 = _get_avail_p2(hz, use_feat_names)
except ImportError:
    pass

if _h_names_p2 and len(_h_names_p2) < len(use_feat_names):
    _h_idx_p2 = [use_feat_names.index(n) for n in _h_names_p2]
    X_h_p2 = X_hz[:, _h_idx_p2]
else:
    _h_names_p2 = use_feat_names
    _h_idx_p2 = None
    X_h_p2 = X_hz

result = self._train_horizon(
    hz, X_h_p2, y_hz,
    feature_names=_h_names_p2,
    force=force, full_cv=full_cv,
    X_full=X_hz if _h_idx_p2 is not None else None,   # 스케일러: 97개 전체
    h_idx=_h_idx_p2,                                   # GBM: 슬라이싱
)
self._save_feature_names(_h_names_p2, horizon_key=hz)  # feature_names_{hz}.pkl 저장
```

**안전 보장**:
- JSON 없거나 분리 불필요 시 `_h_idx_p2=None` → 기존 동작(97개 전체) fallback
- `validate_and_resync()`: `scaler.n_features_in_=97 = len(feature_names)` → 불일치 없음
- `predict_proba()` 스케일러 피처 수 방어 로직 통과

---

## 3. Q2 — Proba는 호라이즌별 독립 GBM 피처 그룹으로 산출되는가

### 추론 경로 (`predict_proba`)

```
입력: feat_vec (97개) + hz_feat_vecs[h] (호라이즌별 완성봉 피처)
  ↓
scaler[h].transform(hz_feat_vecs[h])       ← 호라이즌별 독립 스케일러 (97개 기준)
  ↓
scaled[:, _hz_feat_indices[h]]             ← h_idx 슬라이싱 (수정 후 정상화)
  ↓
models[h].predict_proba(sliced)            ← 호라이즌 전용 GBM
  ↓
Proba[h]
```

### 수정 전 문제

| 레이어 | 수정 전 상태 |
|---|---|
| 입력 데이터 (`hz_feat_vecs[h]`) | ✅ 호라이즌별 완성봉 기반 — 분리됨 |
| 스케일러 (`scalers[h]`) | ✅ 호라이즌별 독립 저장 (동일 97개 피처 공간) |
| GBM 입력 슬라이싱 (`_hz_feat_indices`) | ❌ `None` — Phase 2 재학습이 `feature_names_{hz}.pkl`을 97개 전체로 저장했으므로 `h_names == feature_names` → 슬라이싱 없음 |
| GBM 모델 | ✅ 호라이즌별 독립 모델 |

### 수정 후 연쇄 효과

다음 EOD 재학습 이후:

```
_save_feature_names(h_names_p2, horizon_key=hz)
  → feature_names_{hz}.pkl = 호라이즌 전용 피처 목록

MultiHorizonModel._load_all()
  → horizon_feature_names[hz] = 호라이즌 전용 피처 목록

_rebuild_hz_feat_indices()
  → h_names ≠ feature_names(97개)
  → _hz_feat_indices[hz] = np.array([...]) 세팅

predict_proba()
  → xs = scaled[:, _hz_feat_indices[hz]]  ← 슬라이싱 적용
```

---

## 4. Q3 — Proba는 N분봉 완성 주기로 산출·배포되는가

### 판정: 매분 산출 (N분봉은 피처 갱신 주기, decay로 신뢰도 보완)

이 항목은 설계 의도이며 결함이 아니다. Q3는 **미해소**로 남기되, 설계 선택임을 명시한다.

### 실제 동작

```
매 1분봉 run_minute_pipeline
  │
  ├─ bar_aggregator.push(bar_1m)
  │     N분봉 완성 시 → build_for_horizon() → _hz_feat_cache[h] 갱신, _hz_bar_age[h]=0
  │     미완성 시       → _hz_bar_age[h] += 1
  │
  ├─ hz_feat_vecs[h] = _hz_feat_cache[h] × decay^age
  │
  ├─ predict_proba(feat_vec, hz_feat_vecs=hz_feat_vecs)    ← 매분 실행
  │
  └─ confidence[h] *= decay_factor^age                     ← 추가 감쇠
```

### Decay 계수

| 호라이즌 | Decay | 완성 후 N-1분 경과 시 잔존 신뢰도 |
|---|---|---|
| 3m | 0.97 | 2분 경과: 0.97² = 0.94 |
| 5m | 0.95 | 4분 경과: 0.95⁴ = 0.81 |
| 10m | 0.93 | 9분 경과: 0.93⁹ = 0.52 |
| 15m | 0.92 | 14분 경과: 0.92¹⁴ = 0.31 |
| 30m | 0.97 | 29분 경과: 0.97²⁹ = 0.42 |

### 잠재 위험 (미해소)

decay된 피처 벡터가 GBM에 투입되나 GBM은 decay 없는 값으로 학습됨 → 학습·추론 분포 불일치. GBM 트리 구조는 선형 모델보다 내성이 있으나, decay^age가 0.5 이하인 구간(10m 9분 경과 등)에서 피처 왜곡 가능성 상존.

**대안 (미적용)**: 피처값은 decay 없이 유지하고, confidence만 decay 적용. 단, 피처값을 유지하면 "봉 기준점이 다른 데이터로 추론"하는 개념적 오염이 발생하므로 현재 설계도 합리적.

---

## 5. V8 구현 현황 (242차 기준)

### 완료 항목 (S0~8 전 항목)

| 우선순위 | 항목 | 분류 | 완료 시점 |
|---|---|---|---|
| S0 | `vwap_momentum` 버그 수정 | 버그 | 119차 |
| S0 | `prev_day_same_hour_ret` timedelta(0) 버그 수정 | 버그 | 재설계 |
| 1 | 피처 반감기 적응 정규화 (아이디어 B) | 피처 | 120차 — `features/feature_decay.py` 신규 |
| 2 | 호라이즌 캐스케이드 응집도 게이트 (아이디어 A) | 앙상블 | 124차 — `compute_cascade_coherence()` |
| 3 | 시간대별 호라이즌 활성화 | 전략 | 124차 — `HORIZON_TIME_POLICY` |
| 4 | ATR 레짐별 호라이즌 자동전환 | 전략 | 124차 — `select_entry_horizon()` |
| 5 | `entry_ok` 규칙 기반 게이팅 | 안전 | 124차 |
| 6 | FeatureBuilder 버그 6종 수정 | 피처 | 120~124차 |
| 7 | 호라이즌별 완성봉 입력 (Phase A~C) | 구조 | 120차 구조 + 6/24 재학습 |
| 8 | 호라이즌별 학습 윈도우 분리 (Phase 2-D) | 학습 | 242차 — `TRAINING_WINDOW_BARS` 3m:5000, 5m:3000 |

### 핵심 이력: EOD_RETRAIN.bat --phase2 16일 누락

```
2026-06-08 (121차): Phase 2 재학습 최초 완료
2026-06-08 ~ 2026-06-23: EOD_RETRAIN.bat에 --phase2 누락
                          → 16일간 레거시 Phase 1 경로로 덮어씌워짐
2026-06-24 (242차): --phase2 영구 추가 + 재학습 재실행으로 복구
```

### 미완료·설계 변경 항목

| 항목 | 상태 | 사유 |
|---|---|---|
| Platt Scaling 호라이즌별 독립 적용 | ⚠️ Phase 3 대기 | 재학습 불필요, 안정화 후 진행 |
| SGD 호라이즌별 feat_vec | **구현 불필요 확정** | 전체 `_hz_feat_cache` 교체 시 미래 데이터 오염 |
| `multi_timeframe.py` dead code | **Stage 2~7/8 처리** | 프로젝트 전체 임포트 없음 |
| 역방향 손절 예측 서브모델 (아이디어 C) | ❌ 안정화 후 | — |
| MFE 기반 레이블 재설계 | ❌ Phase 5+ | — |

### 세션 기간 주요 개선 (132~242차, 6/9~6/24)

| 차수 | 개선 내용 |
|---|---|
| 232차 | `macro_risk_off/on/event_flag` ScaleFloor 0.5 — 이진 피처 z폭발 방지 |
| 233차 | DailyClose `_exit_normally` 즉시 생성 + GUARD 장전 자동 Y |
| 234차 | 종목변경 재시작 배지 — 실투자 안전 종목 전환 |
| 235차 | TICK_SIZE 동적 주입 + 종목전환 안전절차 다이얼로그 |
| 236차 | 저신뢰 자동진입 차단 3중 안전장치 |
| 237차 | Hurst 미계산 자동진입 차단 — `hurst_ready` 플래그 + C급 경로 |
| 238차 | Platt 보정기 피드백 루프 버그 수정 — `confidence_raw` 캐시 저장 |
| 240차 | MetaConf CONF_HIGH 재보정 + 임계값 하향 — blended_conf 실측 반영 |
| 241차 | 1m SGD DN 편향 모니터링 강화 — 4종 파라미터 조정 |
| 242차 | TRAINING_WINDOW_BARS + EOD_RETRAIN.bat `--phase2` 영구 추가 |

---

## 6. 243차 수정 사항

### 변경 파일

`learning/batch_retrainer.py` — `_retrain_phase2()` 내부 (L928~961)

**변경 규모**: 33줄 삽입, 1줄 교체

### 변경 전 → 후

**변경 전**
```python
result = self._train_horizon(
    hz, X_hz, y_hz,
    feature_names=use_feat_names,   # 97개 전체 — JSON 무시
    force=force, full_cv=full_cv
    # X_full=None, h_idx=None
)
# feature_names_{hz}.pkl 저장 없음
```

**변경 후**
```python
# horizon_feature_sets.json 조회
_h_names_p2 = get_available_feature_set(hz, use_feat_names)  # 호라이즌 전용 피처셋

if _h_names_p2 and len(_h_names_p2) < len(use_feat_names):
    _h_idx_p2 = [use_feat_names.index(n) for n in _h_names_p2]
    X_h_p2 = X_hz[:, _h_idx_p2]
else:
    _h_names_p2, _h_idx_p2, X_h_p2 = use_feat_names, None, X_hz

result = self._train_horizon(
    hz, X_h_p2, y_hz,
    feature_names=_h_names_p2,
    force=force, full_cv=full_cv,
    X_full=X_hz if _h_idx_p2 is not None else None,  # 스케일러: 97개 전체 fit
    h_idx=_h_idx_p2,                                  # GBM: 스케일 후 슬라이싱
)
self._save_feature_names(_h_names_p2, horizon_key=hz)  # feature_names_{hz}.pkl 저장
```

### 적용 확인 방법

다음 EOD 재학습 후 로그에서 확인:

```
[Retrain-P2] 1m 피처 슬라이싱: 97 → N개 (horizon_feature_sets.json)
[Retrain-P2] 3m 피처 슬라이싱: 97 → M개 (horizon_feature_sets.json)
[Retrain-P2] 5m 피처 슬라이싱: 97 → K개 (horizon_feature_sets.json)
...
```

로그 미출력 시 → JSON에 해당 호라이즌 미등록 또는 전체 피처셋과 동일한 경우 (fallback 동작).

---

## 7. 종합 판정표

| 항목 | 수정 전 | 수정 후 (243차) | 비고 |
|---|---|---|---|
| **Q1: GBM 피처 분리** | ❌ Phase 2 경로 미분리 | ✅ 수정 완료 | 다음 EOD 재학습 후 적용 |
| **Q2: 독립 Proba 산출** | ⚠️ 데이터 분리, 피처 공간 비분리 | ✅ 수정 완료 | `_hz_feat_indices` 자동 세팅 |
| **Q3: N분봉 완성 주기 배포** | ❌ 매분 배포 + decay | ❌ 동일 | 설계 의도 — 변경 없음 |
| **V8 Phase 0·1 구현** | ✅ | ✅ | 119~124차 완료 |
| **V8 Phase 2 구조** | ✅ | ✅ | BarAggregator + raw_features_horizon |
| **V8 Phase 2 재학습** | ⚠️ 16일 누락 후 복구 | ✅ | 242차 재실행, 243차 경로 수정 |
| **Phase 2-D TRAINING_WINDOW** | ✅ | ✅ | Stage 3(50일+) 효과 발현 예정 |
| **ScaleFloor 이진 피처** | ✅ | ✅ | 232차 적용 |
| **진입 안전장치 3중** | ✅ | ✅ | 236~237차 적용 |
| **Platt Scaling 독립 적용** | ⚠️ Phase 3 대기 | ⚠️ Phase 3 대기 | 재학습 불필요 |

---

## 8. 잔여 권고 사항

### 단기 모니터링 (다음 1~3 거래일)

- [ ] EOD 재학습 후 `[Retrain-P2] *m 피처 슬라이싱:` 로그 확인
- [ ] `feature_names_{hz}.pkl` 파일 크기 비교 (슬라이싱 적용 시 97개보다 작아야 함)
- [ ] main.py 재기동 후 `[Model] *m 전용 피처셋 로드: N개` 로그 확인

### Stage 2 (30일+)

- [ ] buy_vol/sell_vol 30일 누적 후 1m/3m 재학습 → OFI/CVD 단기 모델 추가 개선

### Stage 3 (50일+)

- [ ] TRAINING_WINDOW 3m:5000 / 5m:3000 실제 적용 여부 확인  
  → `[Retrain-P2] *m TRAINING_WINDOW=N 적용 (rows→N봉)` 로그 출력

### Phase 3 (안정화 후)

- [ ] Platt Scaling 호라이즌별 독립 적용 — 앙상블 왜곡 제거
- [ ] Q3 재검토: decay 피처 투입 → GBM 학습-추론 불일치 해소 방안  
  (피처값 decay 없이 confidence만 감쇠하는 방식으로 전환 고려)

---

*미륵이 KOSPI200 선물 자동매매 v8.0 — 모델 운영 Audit 2026-06-25*
