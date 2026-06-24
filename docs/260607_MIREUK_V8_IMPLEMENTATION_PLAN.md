# 미륵이 v8.0 구현 계획서 (Implementation Plan + Todo List)

> 작성일: 2026-06-07 / 마지막 업데이트: **2026-06-24 (242차)**
> 기반 문서: `개선_feature_builder_improvements.md` / `미륵8.0 scalper_horizon_priority.md` / 아이디어 A~E / 호라이즌별 봉 입력 3단계 로드맵  
> 현재 파이프라인 참조: `Minute pipeline.txt`

> 미륵이 v7.0 last 119차 세션 완료 커밋: bd87f06  
> **Phase 0·1·2 코드 전 항목 완료 (2026-06-24 기준). Phase 2 재학습 완료.**

- 확인된 버그 2건: `vwap_momentum` (119차 완료), `prev_day_same_hour_ret` (재설계 방식으로 수정 완료)
- Phase 0·1: 6/7~6/8 (119~124차) 구현 완료
- Phase 2 구조: 6/7 (120차) 구현, 6/8 (121차) 버그 수정 + Backfill + 최초 재학습
- Phase 2 EOD 자동화: 6/24 (242차) `EOD_RETRAIN.bat --phase2` 영구 추가, 재학습 재실행

**v8.0 목표**
- 버그 전수 제거 → 피처 신뢰도 확보
- 피처 반감기·응집도·시간대 전략으로 단기 Precision +3~5%
- 호라이즌별 완성봉 입력으로 각 모델의 근본 입력 데이터 정합성 확보
- 학습 윈도우 분리로 전체 정확도 +2~3% 장기 확보
- **v7.x 고질 진입0 문제의 7개 원인 축 구조적 해소** (커밋 이력 기반 분석 → 본 문서 부록 참조)

---

## 전체 개선 항목 통합 우선순위

| 우선순위 | 항목 | 분류 | 기대 효과 | 모델 재학습 | 상태 |
|---------|------|------|---------|-----------|------|
| **S0** ✅ | `vwap_momentum` 버그 수정 | 버그 | 피처 복구 | 불필요 | **완료** (119차) |
| **S0** ✅ | `prev_day_same_hour_ret` 버그 수정 | 버그 | 피처 복구 | 불필요 | **완료** (재설계) |
| **1** ✅ | 피처 반감기 적응 정규화 (아이디어 B) | 피처 | Precision +3~5% | 불필요 | **완료** (120차) |
| **2** ✅ | 호라이즌 응집도 게이트 (아이디어 A) | 앙상블 | FP -2~4% | 불필요 | **완료** (124차) |
| **3** ✅ | 시간대별 호라이즌 활성화 | 전략 | 구간별 손실 방어 | 불필요 | **완료** (124차) |
| **4** ✅ | ATR 레짐별 호라이즌 자동전환 | 전략 | 변동성 매칭 | 불필요 | **완료** (124차) |
| **5** ✅ | `entry_ok` 규칙 기반 게이팅 | 안전 | 슬리피지 방어 | 불필요 | **완료** (124차) |
| **6** ✅ | 나머지 FeatureBuilder 6개 항목 | 피처 | 모델 품질 | 불필요 | **완료** (120~124차) |
| **7** ✅ | **호라이즌별 완성봉 입력 (Phase A~C)** | 구조 | 입력 정합성 확보 | **필수** | **완료** (120차 구조 + 6/24 재학습) |
| **8** ✅ | 호라이즌별 학습 윈도우 분리 (아이디어 E) | 학습 | 정확도 +2~3% | **필수** | **완료** (242차 — 값 조정 반영, 아래 참조) |
| **9** | Platt Scaling 호라이즌별 독립 적용 | 보정 | 앙상블 왜곡 제거 | 불필요 | ⚠️ Phase 3 대기 |
| **10** | 역방향 손절 예측 서브모델 (아이디어 C) | 모델 | FP -30~40% 추가 | 필요 | ❌ 안정화 후 |
| **11** | MFE 기반 레이블 재설계 | 레이블 | 장기 모델 품질 | 필요 | ❌ Phase 5+ |

---

## PHASE 0 — 즉시 버그 수정 (재학습 불필요)

### 0-1. `prev_day_same_hour_ret` `timedelta(minutes=0)` 버그

**파일**: `features/feature_builder.py:570`

```python
# 수정 전
prev_ts_m1 = (prev_d - datetime.timedelta(minutes=0)).strftime("%Y-%m-%d ") \
             + (dt - datetime.timedelta(minutes=1)).strftime("%H:%M:%S")

# 수정 후
prev_ts_m1 = prev_d.strftime("%Y-%m-%d ") \
             + (dt - datetime.timedelta(minutes=1)).strftime("%H:%M:%S")
```

**효과**: 전일 동시간대 수익률이 항상 0을 반환하던 문제 즉시 해결

---

### 0-2. 나머지 FeatureBuilder 항목 (2~8순위)

**파일**: `features/feature_builder.py`

| 항목 | 위치 | 수정 내용 |
|------|------|---------|
| `ema_cross` 이진→연속 | 491줄 | `(ema5 - ema20) / (ema20 + 1e-9)` |
| `tick_size` 설정화 | 331줄 | `config/settings.py`의 `TICK_SIZE = 0.05`로 이전 |
| `avg_volume` 분리 | 264줄 | `bar_volume=vol`, `avg_volume=rolling_mean` |
| `atr_expansion_rate` 신규 | ATR 블록 후 | `(atr[-1] - atr[-2]) / atr[-2]` |
| `investor_age_norm` 정규화 | 384줄 | `min(age, 300.0) / 300.0` |

---

## PHASE 1 — 단기 피처·전략 개선 (재학습 불필요)

### 1-1. 피처 반감기 적응 정규화 (아이디어 B)

**목적**: 같은 피처도 호라이즌별로 유효 시간이 다름 — OFI는 1m에서 1.0, 30m에서 0.0

**파일 신규**: `features/feature_decay.py`

```python
# 각 피처의 호라이즌별 유효 가중치 (0.0~1.0)
FEATURE_HALFLIFE = {
    #                   1m    3m    5m   10m   15m   30m
    "ofi_norm":       (1.0,  0.8,  0.5, 0.15, 0.0,  0.0),
    "mlofi_norm":     (1.0,  0.7,  0.4, 0.1,  0.0,  0.0),
    "cvd_delta_norm": (0.7,  1.0,  0.9, 0.4,  0.1,  0.0),
    "microprice_bias":(1.0,  0.9,  0.6, 0.2,  0.0,  0.0),
    "queue_directional_depletion": (1.0, 0.8, 0.5, 0.1, 0.0, 0.0),
    "vwap_position":  (0.3,  0.6,  0.9, 1.0,  0.95, 0.8),
    "vwap_momentum":  (0.4,  0.7,  1.0, 0.9,  0.7,  0.4),
    "hurst":          (0.0,  0.1,  0.4, 0.8,  1.0,  1.0),
    "bb_position":    (0.2,  0.4,  0.7, 1.0,  1.0,  0.9),
    "macro_risk_on":  (0.0,  0.0,  0.2, 0.5,  0.8,  1.0),
    "opt_pcr_ratio":  (0.0,  0.1,  0.3, 0.7,  1.0,  1.0),
}
_H_IDX = {"1m": 0, "3m": 1, "5m": 2, "10m": 3, "15m": 4, "30m": 5}

def get_horizon_features(features: dict, horizon: str) -> dict:
    """호라이즌 전용 피처 사본 — 반감기 가중치 적용. <0.5ms"""
    idx = _H_IDX.get(horizon, 0)
    scaled = dict(features)
    for feat, weights in FEATURE_HALFLIFE.items():
        if feat in scaled:
            scaled[feat] = scaled[feat] * weights[idx]
    return scaled
```

**main.py 연결 위치**: STEP 5 직전, `get_horizon_features(features, h)` 호출 후 `get_feature_vector()`

**예산**: dict copy + 곱셈 = **<0.5ms** (77ms 예산 내 안전)

---

### 1-2. 호라이즌 응집도 게이트 — 시계열 정렬 강화 (아이디어 A)

**현재**: `CoherenceGate` (ensemble_decision.py 3-10)는 방향 비율만 체크  
**추가**: 상위→하위 호라이즌 순서로 정렬되는 **시계열 캐스케이드** 확인

**파일**: `strategy/ensemble_decision.py` (CoherenceGate 직후 추가)

```python
def compute_cascade_coherence(horizon_proba: dict) -> float:
    """
    30m→15m→10m→5m→3m→1m 순서로 같은 방향이 '흘러내려오는' 정렬도.
    뒤에서 앞으로 역행(하위만 방향 있음)이면 노이즈성 스파이크.
    반환: 0.0(완전 불일치) ~ 1.0(완전 정렬)
    """
    cascade = ["30m", "15m", "10m", "5m", "3m", "1m"]
    dirs = [horizon_proba.get(h, {}).get("direction", 0) for h in cascade]
    target = dirs[-1]  # 1m 방향 기준
    if target == 0:
        return 0.5    # FLAT → 중립
    aligned = 0
    for d in reversed(dirs):
        if d == target:
            aligned += 1
        else:
            break
    return aligned / len(dirs)

# 사용 (CoherenceGate 결과 보강)
cascade_score = compute_cascade_coherence(horizon_proba)
if cascade_score < 0.34:          # 상위 2개 이상 역행
    result["direction"] = FLAT
    result["grade"]     = "X"
    result["cascade_blocked"] = True
```

**기존 CoherenceGate와 관계**: 기존 게이트는 "몇 개가 동방향인가(비율)", 이 추가는 "어느 방향에서 왔는가(순서)" → 상호 보완적

---

### 1-3. 시간대별 호라이즌 활성화

**파일**: `strategy/ensemble_decision.py` 또는 `config/settings.py`

```python
HORIZON_TIME_POLICY = {
    # (from_hhmm, to_hhmm): enabled_horizons
    (  900,  905): [],              # cold-start — 전 호라이즌 차단
    (  905,  930): ["1m","3m","5m"],# 개장 초 — 단기만, confidence +5%
    (  930, 1440): None,            # 전 호라이즌 (None = 전체 허용)
    ( 1440, 1510): ["1m","3m"],     # 마감 청산 집중 — 30m 비활성
}

def get_active_horizons(hhmm: int) -> list | None:
    for (start, end), horizons in HORIZON_TIME_POLICY.items():
        if start <= hhmm < end:
            return horizons
    return None
```

**ATR 연동 수익 목표**:
```python
ATR_MULTIPLIER = {"1m": 0.3, "3m": 0.5, "5m": 0.7}
tp_points = atr * ATR_MULTIPLIER.get(active_horizon, 0.5)
```

---

### 1-4. ATR 레짐별 호라이즌 자동전환

**파일**: `strategy/ensemble_decision.py`

```python
def select_entry_horizon(atr: float, threshold_1m: float) -> str | None:
    """기존 threshold_feasibility 피처 역활용 — 추가 인프라 불필요"""
    feasibility = atr / (threshold_1m + 1e-9)
    if feasibility < 0.8:    return None   # 저변동성 → 진입 차단
    elif feasibility < 1.5:  return "1m"   # 적정 변동성
    elif feasibility < 2.5:  return "3m"   # 중간 변동성
    else:                    return "5m"   # 고변동성
```

---

### 1-5. `entry_ok` 규칙 기반 게이팅

**파일**: `features/feature_builder.py` — `build()` 반환 직전

```python
features["entry_ok"] = 1.0 if (
    features.get("toxicity_score", 1.0)     < 0.6 and
    features.get("feature_quality_score", 0.0) > 0.7 and
    features.get("spread_ticks", 99.0)       <= 1.0
) else 0.0
```

**체크리스트 연동**: `checklist.py`에서 `entry_ok == 0.0`이면 즉시 X 등급

---

## PHASE 2 — 호라이즌별 완성봉 입력 (구조 개선 + 재학습 필수)

> **전제**: Phase 0·1 완료 후 시작. 이 Phase 완료 시 **전 모델(GBM·SGD·RF) 재학습** 필수.

### 2-A. `BarAggregator` 신규

**파일 신규**: `features/bar_aggregator.py`

```python
class BarAggregator:
    """1분봉 → N분봉 완성 감지 및 집계"""
    HORIZONS = [1, 3, 5, 10, 15, 30]

    def __init__(self):
        self._bufs = {h: [] for h in self.HORIZONS if h > 1}
        self._last = {h: None for h in self.HORIZONS}

    def push(self, bar_1m: dict) -> dict:
        """완성봉 반환: {h: bar_dict(완성) or None(미완성)}"""
        result = {1: bar_1m}
        self._last[1] = bar_1m
        for h in [3, 5, 10, 15, 30]:
            self._bufs[h].append(bar_1m)
            if len(self._bufs[h]) >= h:
                agg = self._aggregate(self._bufs[h])
                self._last[h] = agg
                self._bufs[h] = []
                result[h] = agg
            else:
                result[h] = None  # 미완성 → 직전 완성봉 사용
        return result

    def get_last(self, h: int) -> dict | None:
        return self._last.get(h)

    def _aggregate(self, bars: list) -> dict:
        b0 = bars[0]
        return {
            "ts":       bars[-1]["ts"],
            "open":     b0["open"],
            "high":     max(b["high"] for b in bars),
            "low":      min(b["low"] for b in bars),
            "close":    bars[-1]["close"],
            "volume":   sum(b["volume"] for b in bars),
            "buy_vol":  sum(b.get("buy_vol", 0) for b in bars),
            "sell_vol": sum(b.get("sell_vol", 0) for b in bars),
            "bid1":     bars[-1].get("bid1", 0),
            "ask1":     bars[-1].get("ask1", 0),
        }

    def reset_daily(self):
        for h in [3, 5, 10, 15, 30]:
            self._bufs[h].clear()
            self._last[h] = None
        self._last[1] = None
```

**미사용 `MultiTimeframeAnalyzer` 처리**: `features/technical/multi_timeframe.py`의 5m·15m 집계 로직을 `BarAggregator`로 통합 후 deprecate.

---

### 2-B. `FeatureBuilder.build_for_horizon()` 추가

**파일**: `features/feature_builder.py`

```python
def build_for_horizon(self, bar_n: dict, horizon_min: int) -> dict:
    """
    N분봉 기준 bar-level 피처 재계산.
    반드시 build(bar_1m) 호출 후 사용 — 내부 상태는 1m에서 갱신 완료.
    """
    feats = dict(self._last_features)   # 1m 기반 복사
    close = bar_n["close"]
    high  = bar_n["high"]
    low   = bar_n["low"]
    vol   = bar_n["volume"]
    open_ = bar_n["open"]

    # N분봉 bar-level 피처 덮어쓰기
    feats["atr"] = max(high - low, 0.5)   # N분봉 True Range 직접 사용
    feats["bar_volume"] = float(vol)
    feats[f"ret_{horizon_min}m"] = (close - open_) / (open_ + 1e-9)

    # 반감기 적용 (Phase 1-1)
    from features.feature_decay import get_horizon_features
    return get_horizon_features(feats, f"{horizon_min}m")
```

---

### 2-C. `main.py` STEP 5 호라이즌별 분기

**파일**: `main.py` (STEP 4~5 사이)

```python
# STEP 4 완료 후 — bar_aggregator는 __init__에서 self.bar_aggregator = BarAggregator()
completed_bars = self.bar_aggregator.push(bar)

# STEP 5 — 호라이즌별 feat_vec 캐시 관리
H_MINS = {"1m":1, "3m":3, "5m":5, "10m":10, "15m":15, "30m":30}
for h_name, h_min in H_MINS.items():
    if completed_bars.get(h_min) is not None:
        # 봉 완성 → 호라이즌 전용 피처·벡터 갱신
        h_feats = self.feature_builder.build_for_horizon(completed_bars[h_min], h_min)
        self._hz_feat_cache[h_name] = self.feature_builder.feats_to_vec(
            h_feats, self.model.feature_names
        )
    # 미완성이면 _hz_feat_cache 그대로 (직전 완성봉 예측 재사용)

# predict_proba에 per-horizon 벡터 전달
horizon_proba = self.model.predict_proba_multi(self._hz_feat_cache)
```

**`predict_proba_multi()` 시그니처 변경**:
```python
# model/multi_horizon_model.py
def predict_proba_multi(self, feat_vecs: dict) -> dict:
    """feat_vecs = {"1m": np.array, "3m": np.array, ...}"""
    results = {}
    for horizon, clf in self.models.items():
        fv = feat_vecs.get(horizon, feat_vecs.get("1m"))  # fallback
        ...
```

---

### 2-D. 호라이즌별 학습 윈도우 분리 (아이디어 E) ✅ 완료 (242차, 2026-06-24)

**파일**: `learning/batch_retrainer.py`

**원안 vs 실제 구현 차이**:

V8 원안(90/60/48)은 온라인학습 메모리 개념으로 설계됐으나, 배치 EOD 재학습에 적용하면
`MIN_TRAIN_BARS_PER_HORIZON`(3m=5000, 5m=3000)보다 낮아 항상 건너뜀 → 배치 재학습에 실효 없음.

실제 구현: MIN_TRAIN_BARS와 동등하거나 큰 값으로 조정 + 안전 fallback(미달 시 전체 사용)

```python
# 원안 (온라인학습 메모리 개념 — 배치 재학습에 미적용)
# TRAINING_WINDOW_BARS = {"1m": 90, "3m": 60, "5m": 48, "10m": "session_all", ...}

# 실제 구현 (learning/batch_retrainer.py)
TRAINING_WINDOW_BARS = {
    "1m":   None,   # Phase 2 미사용 (raw_features 경로)
    "3m":   5000,   # 최근 5k봉 상한 — Stage 3(50일+) 이후 단기 반응 효과 발현
    "5m":   3000,   # 최근 3k봉 상한
    "10m":  None,   # session_all 의도: 추후 세션 필터 구현 예정
    "15m":  None,
    "30m":  None,   # multi_day: weeks_back 전체 사용
}
```

**동작 조건**: `len(records) > window AND window >= MIN_TRAIN_BARS_PER_HORIZON` 충족 시만 트림.
- 현재(데이터 2.5주): 3m=5330봉>5000, window=5000≥5000 → 최신 5000봉으로 트림 활성화
- Stage 3 이후(50일+): 3m ~30k봉 → window=5000으로 최근 5주 집중 학습
- 30m은 None → weeks_back 전체 사용으로 장기 맥락 최대화

**로그 확인**: `[Retrain-P2] 3m TRAINING_WINDOW=5000 적용 (5330→5000봉 최신 우선)`

---

## PHASE 3 — 중장기 고도화 (안정화 후)

### 3-1. Platt Scaling 호라이즌별 독립 적용

**현재**: 앙상블 단일 Platt (`ensemble_calibrator`) + 3m fallback  
**목표**: 각 호라이즌 GBM 모델에 독립 Platt 파라미터 피팅

**검증 선행 조건**: Phase 2 완료 후 각 호라이즌 실 정확도 측정 → ECE 계산 → 편차 큰 호라이즌만 우선 적용

---

### 3-2. 역방향 손절 예측 서브모델 (아이디어 C)

**목표**: "진입 후 30초 내 역방향 1ATR 이동" 확률을 별도 SGD로 예측 → 0.4 초과 시 차단

```python
# 레이블: 진입 후 조기 손절 발생 = 1
# 기존 SGD 인프라 재사용 — CybosSGDOnlineLearner에 anti_signal 채널 추가
anti_prob = self.online_learner.predict_proba("anti_1m", feat_vec)
if anti_prob and anti_prob.get("up", 0) > 0.4:
    entry_blocked = True
```

---

### 3-3. MFE 기반 레이블 재설계 (학술 방법론)

**Phase 5 실전 전환 이후 적용**

```python
# 1m 레이블: 단순 방향 → "1분 내 목표 수익 도달 여부"
# MFE = Maximum Favorable Excursion (최대 유리 이동)
label_1m = 1 if max_high[t:t+1] - close[t] > threshold_tp else (
           -1 if close[t] - min_low[t:t+1] > threshold_tp else 0
)
```

---

## 미륵이 환경 제약 확인

| 항목 | 제약 | Phase 0~1 | Phase 2 |
|------|------|-----------|---------|
| Python 3.7 32-bit | deque, dict 연산 제한적 | ✅ 안전 | ✅ 안전 |
| 77ms 파이프라인 예산 | 반감기 계산 <0.5ms | ✅ 안전 | ⚠️ bar_aggregator push + 6×build_for_horizon 검증 필요 |
| GBM 30분 재학습 | 6모델 → 윈도우 분리 시 데이터 로딩 증가 | 해당없음 | ⚠️ 재학습 시간 측정 후 조정 |
| COM 콜백 규칙 | dynamicCall·emit 금지 | 무관 | 무관 |
| Cybos Plus | 실시간 데이터 소스 | 무관 | 무관 |

---

## TODO LIST

> 마지막 갱신: 2026-06-24 (242차)

### ✅ Phase 0 완료 (2026-06-07~08, 119~124차)

- [x] `feature_builder.py` — `prev_day_same_hour_ret` 버그: `update_prev_day_same_hour_ret()` 메서드로 재설계 수정
- [x] `feature_builder.py:491` — `ema_cross` 이진→연속값 `(ema5-ema20)/(ema20+1e-9)` 수정
- [x] `feature_builder.py:331` — `tick_size` `config/settings.py TICK_SIZE`로 설정화 (235차)
- [x] `feature_builder.py:264` — `avg_volume` / `bar_volume` 분리
- [x] `feature_builder.py` ATR 블록 후 — `atr_expansion_rate` 신규 추가
- [x] `feature_builder.py:384` — `investor_age_sec` → `/300.0` 정규화
- [x] `feature_builder.py` build() 반환 전 — `entry_ok` 게이팅 추가

### ✅ Phase 1 완료 (2026-06-07~08, 120~124차)

- [x] `features/feature_decay.py` 신규 — `FEATURE_HALFLIFE` 테이블 + `get_horizon_features()`
- [x] `main.py` STEP 5 — `get_horizon_features()` + `BAR_CACHE_DECAY` 호라이즌별 feat_vec 분기
- [x] `model/ensemble_decision.py` — `compute_cascade_coherence()` 추가 (임계 0.25)
- [x] `model/ensemble_decision.py` — `select_entry_horizon()` ATR 레짐 자동전환
- [x] `config/settings.py` — `HORIZON_TIME_POLICY` + `HORIZON_COLDSTART_MIN_PASS` cold-start 2단계
- [x] `main.py` — `_get_active_horizons()` 시간대 정책 연동
- [x] `strategy/entry/checklist.py` — `entry_ok == 0.0` 즉시 X등급 조건 추가
- [x] `model/ensemble_decision.py` — FL 조기 감쇠 `_fl_streak` 10분 임계
- [x] `main.py` — `_diagnose_zero_entry()` 진입0 자동 원인 진단 로그
- [x] `main.py` — `feature_quality_score` 기반 dynamic_mc 양방향 조정
- [x] `model/multi_horizon_model.py` — 이상값 피처 3개+ 시 `AutoMaskedFallback` 자동 발동

### ✅ Phase 2 완료 (2026-06-07~08, 120~121차 + 2026-06-24, 242차)

- [x] `features/bar_aggregator.py` 신규 — `BarAggregator` 클래스 (120차, 6/7)
- [x] `main.py __init__` — `self.bar_aggregator = BarAggregator()` + `_hz_feat_cache = {}` (120차)
- [x] `main.py` STEP 5 — `bar_aggregator.push(bar)` + 호라이즌별 feat_vec 캐시 로직 (120차)
- [x] `main.py` STEP 5 — 봉 완성 간격 중 캐시 신뢰도 감쇠 `BAR_CACHE_DECAY` (120차)
- [x] `features/feature_builder.py` — `build_for_horizon()` 메서드 추가 (120차)
- [x] `model/multi_horizon_model.py` — `predict_proba_multi(feat_vecs: dict)` 시그니처 변경 (120차)
- [x] `model/multi_horizon_model.py` — `validate_horizon_scaler_consistency()` 추가 (120차)
- [x] `utils/db_utils.py` — `raw_features_horizon` 테이블 + `buy_vol/sell_vol` 컬럼 + `save_horizon_features()` (120차)
- [x] `learning/batch_retrainer.py` — `MIN_TRAIN_BARS_PER_HORIZON` + `_retrain_phase2()` + `use_horizon_features=` (120차)
- [x] `scripts/eod_retrain.py` — `--phase2` 플래그 추가 (120차)
- [x] `scripts/aggregate_and_backfill.py` 신규 — 기존 72k봉 소급 백필 스크립트 (120차)
- [x] **Backfill 실행** — `aggregate_and_backfill.py --weeks 10` (6/8, 121차)
- [x] **GBM Phase 2 최초 재학습** — `eod_retrain.py --phase2 --weeks 10` (6/8, 121차)
- [x] `learning/batch_retrainer.py` — `TRAINING_WINDOW_BARS` 호라이즌별 윈도우 상한 (242차, 6/24)
- [x] `EOD_RETRAIN.bat` — `--phase2` 플래그 영구 추가 (242차, 6/24)
- [x] **GBM Phase 2 재학습 재실행** — 6/8~6/24 레거시 경로 덮어씌움 복구 (242차, 6/24)
  - 결과: 3m 0.45→0.52, 5m 0.39→0.54, 10m 0.42→0.55, **15m 0.33→0.62, 30m 0.29→0.60** ⬆
- [ ] `learning/online_learner.py` — SGD도 호라이즌별 feat_vec 수신 ← **잔여 미완**
- [ ] `features/technical/multi_timeframe.py` — BarAggregator 통합 후 deprecate ← **잔여 미완**

### 🔜 Phase 2 재학습 로드맵 (Stage 2·3)

| Stage | 시점 | 내용 |
|---|---|---|
| Stage 1 | 6/8 + **6/24 완료** | Phase 2 코드 + Backfill + 재학습 (OFI·CVD C등급 0 fill) |
| **Stage 2** | **~7/8 이후** | `buy_vol/sell_vol` 30일 누적 후 `eod_retrain.py --phase2 --weeks 4` 재실행 → 1m/3m OFI·CVD 정상 학습 |
| **Stage 3** | **~7/28 이후** | 50일+ go-forward 전 호라이즌 재학습 `--weeks 8` → Phase 2 성능 완전 발현 |

### ⏳ Phase 3 대기 (안정화 후)

- [ ] Platt Scaling 호라이즌별 독립 적용 (ECE 측정 후 대상 호라이즌 결정 — 238차 피드백 루프 버그 수정 후 재학습 중)
- [ ] `learning/online_learner.py` — `anti_signal` 채널 추가 (아이디어 C, 역방향 손절 예측)
- [ ] MFE 기반 레이블 재설계 (Phase 5 실전 전환 이후)

---

## 구현 이력 요약

| 날짜 | 차수 | 작업 |
|---|---|---|
| 2026-06-07 | 119차 | vwap_momentum 버그 수정, OFI 부호 복원 |
| 2026-06-07 | 120차 | Phase 2 전체 구조 구현 (BarAggregator, build_for_horizon, DB 스키마, Phase 2 재학습 경로) |
| 2026-06-07 | 121차 | Phase 2 버그 3종 수정 + Backfill 실행 + Phase 2 최초 재학습 완료 |
| 2026-06-08 | 122~123차 | UI v8.0 표시 + Phase 2 bar_age 시각화 |
| 2026-06-08 | 124차 | Phase 1 전략 개선 (HORIZON_TIME_POLICY, cascade_coherence, FL 감쇠, entry_ok) |
| 2026-06-11 | 163차 | HistGBM 전환 (GIL-free) — Phase 2 모델이 레거시 경로로 덮어씌워지기 시작 |
| 2026-06-17 | 191차 | EOD 재학습 OOM 해결 — py310_64 장외 스케줄러 분리 |
| 2026-06-24 | 242차 | **EOD_RETRAIN.bat `--phase2` 영구 추가 + TRAINING_WINDOW_BARS 구현 + Phase 2 재학습 재실행** |

### 2026-06-24 (242차) 상세 작업

1. **V8 구현 상태 점검** — 커밋 이력 전수 검토로 Phase 2 재학습 공백 기간(6/8~6/24) 확인
2. **EOD_RETRAIN.bat `--phase2` 추가** — 자동 일일 재학습이 레거시 경로로 실행되던 문제 영구 수정
3. **Phase 2 재학습 재실행** — `eod_retrain.py --phase2 --weeks 10` (2.3분 소요)
   - 1m: 건너뜀 (raw_features_horizon에 1m 행 없음, 설계상 정상)
   - 3m: 0.4474 → 0.5245 (+7.7%p)
   - 5m: 0.3921 → 0.5370 (+14.5%p)
   - 10m: 0.4222 → 0.5541 (+13.2%p)
   - **15m: 0.3305 → 0.6165 (+28.6%p)**
   - **30m: 0.2909 → 0.5984 (+30.7%p)**
4. **TRAINING_WINDOW_BARS 구현** — `learning/batch_retrainer.py` Phase 2-D 항목 완료
   - V8 원안(90/60/48): 배치 MIN_BARS 미달로 실효 없음 → 3m=5000, 5m=3000으로 조정

---

## 구현 순서 권고

```
Week 1
  Phase 0: 버그 7건 + FeatureBuilder 항목 → 커밋 1개

Week 1~2
  Phase 1-1: feature_decay.py + main.py 연동 → 커밋
  Phase 1-2: cascade_coherence + CoherenceGate 보강 → 커밋
  Phase 1-3/4: 시간대 정책 + ATR 레짐 전환 → 커밋
  Phase 1-5: entry_ok 게이팅 → 커밋

Week 3~4 (별도 브랜치)
  Phase 2-A: BarAggregator 신규 → 단독 테스트
  Phase 2-B: build_for_horizon() → feature 분포 검증
  Phase 2-C: main.py STEP 5 분기 → 파이프라인 77ms 측정
  Phase 2-D: 학습 윈도우 분리 → 전 모델 재학습 → 정확도 비교

Phase 3: 모의투자 2주 이상 안정 확인 후 착수
```

---

---

## 부록 A — 진입0 문제 분석: v7.x 고질 원인 계보 (커밋 이력 기반)

> 분석 기준: 커밋 60차~119차 이력 전수 검토 / 키워드: 진입0·FL편향·conf미달·EKS·스케일러·방향비대칭·이중패널티

### 원인 축 A — FLAT 편향 고착 (방향 예측 불능)

| 차수 | 현상 | 처방 | 재발 여부 |
|------|------|------|---------|
| 85·**113차** | 10m/15m FL 100% 고착 | FL class_weight 명시 (`_CW_10M FL=0.80`) | **재발** (동일 근본 원인) |
| **98차** | 30m FLAT 편향 | CB③ FLAT 예측 제외 + 임계값 완화 | — |
| **81차** | NEUTRAL 방향 동방향 8회+ 고착 | `DirectionalStuckBreaker` 신규 | — |
| **100차** | GBM 5분 연속 상수 출력 | 상수 출력 감지 → 해당 호라이즌 가중치 0 | — |
| **113차** | FL 90%+ 20분 지속 | `_bias_override_horizons` uniform fallback | — |

**구조적 원인**: 1분봉 피처를 모든 호라이즌이 공유 → 시간 규모가 다른 모델들이 동일 신호에 반응 → FLAT으로 수렴. 85차 처방이 113차에서 같은 근본 원인으로 재발한 것이 이를 증명.

---

### 원인 축 B — 신뢰도(confidence) 만성 미달

| 차수 | 현상 | 처방 |
|------|------|------|
| **98차** | REGIME_MIN_CONFIDENCE 0.52 → 진입 차단 | 0.52→0.42 완화 |
| **98차** | min_conf 급등 후 복귀 지연 | 동적 MC 구현, MC_ABS_CEIL 0.75→0.62 |
| **102차** | MC_STEP_LIMIT 과대 → 빠른 상승·느린 하강 | 0.08→0.03 속도 제한 |
| **110차** | conf 42~45% vs mc 43% 상시 미달 | EKS 해제 창 + ShortHorizonOverride |

**구조적 원인**: 모든 호라이즌이 동일 1분봉 피처 공유 → 앙상블 시 방향 상쇄 → confidence가 0.33~0.42 구간에 밀집. min_conf 완화로 대증 치료를 반복했으나 근본 원인(피처 공유) 미처리.

---

### 원인 축 C — EKS(Extended Kill Switch) 과잉 발동

| 차수 | 현상 | 처방 |
|------|------|------|
| **112차** | 장 마감~다음날 ~17h → EarlyWarmup 24h 미달 → EKS | 24h→**4h** 완화 |
| **104차** | EKS 발동 후 수동 해제 전까지 하루 종일 진입0 | 09:20 자동 해제 창 신규 |
| **104차** | EKS 발동 원인 불투명 | 원인 추론 로그 강화 |

---

### 원인 축 D — 스케일러·피처 불일치

| 차수 | 현상 | 처방 |
|------|------|------|
| **95·98차** | feature_names.pkl vs scaler_*.pkl 불일치 → ERR-FATAL | `validate_and_resync()` 자동 복구 |
| **114차** | shap_feature_registry 87→105 불일치 → 재학습 사고 | P0~P4 registry 정합성 검증 |
| **100차** | SGD 스케일러 버그 → 상수 출력 | 스케일러 재적합 3종 |

**v8.0 신규 위험**: Phase 2에서 호라이즌별 봉 분리 시 스케일러도 분리 → 새로운 불일치 경로 생성. `validate_horizon_scaler_consistency()` 추가 필수.

---

### 원인 축 E — 이상값 피처의 정상 신호 압도

| 차수 | 현상 | 처방 |
|------|------|------|
| **110차** | opt_pcr_slope_norm z=+9.21 → OFI UP 신호 상쇄 → conf 42~45% 수렴 | D_FORCE 후 opt_pcr 30분 감쇠 타이머 |
| **109차** | 이상값 피처 1개로 하루 종일 진입0 | `MaskedFallback` 극단 피처 격리 재예측 |
| **110·115차** | SCALER_CLIP_FEATURES 미비 | clip 피처 목록 대폭 확장 |

---

### 원인 축 F — 방향 비대칭(단방향 편향)

| 차수 | 현상 | 처방 |
|------|------|------|
| **72차** | OFI·CVD 롱 편향 구조 | `bull/bear_reversal_signal` 양방향 분리 |
| **72차** | SP500 레짐 임계값 비대칭 | -1.0%→-0.5% 대칭화 |
| **119차** | `ofi_imbalance abs()` → 방향 소실 | 부호 유지 `np.clip` ← **최근 수정** |
| **119차** | `vwap_momentum` 항상 0 | `vwap_position` 참조로 교체 ← **최근 수정** |

---

### 원인 축 G — 이중 패널티·중복 차단 구조

| 차수 | 현상 | 처방 |
|------|------|------|
| **103차** | mlofi_norm → MetaGate + EnsembleGater 이중 패널티 → blended_conf < 0.56 → X | MetaGate 담당 피처 제거 |
| **103차** | toxicity → ExecutionGovernor + ToxicityGate 이중 계산 → size 0.3× 복합 축소 | 단일 처리 경로 통합 |
| **72차** | RL HOLD 페널티 CB·체크리스트와 중복 | 페널티 제거 |
| **101차 후속** | CoherenceGate가 TrendGate 추세를 차단 | TrendGate active 시 CoherenceGate 면제 |

---

## 부록 B — v8.0 개선 효과 평가

### Phase별 진입0 원인 축 대응 매핑

| 원인 축 | v8.0 대응 항목 | 해결 수준 | 기대 효과 |
|---------|--------------|---------|---------|
| **A. FLAT 편향** | Phase 2 호라이즌별 봉 분리 + Phase 1 반감기 | **구조적 해소** | ★★★★★ |
| **B. 신뢰도 미달** | Phase 1 반감기로 각 모델 신호 순도 향상 | **구조적 개선** | ★★★★ |
| **C. EKS 과잉** | 직접 개선 없음 (112차 4h 완화로 대부분 해결됨) | 유지 | ★★ |
| **D. 스케일러 불일치** | Phase 2 봉 분리 시 스케일러도 분리 → 신규 위험 발생 | **위험 증가** ⚠️ | 추가 방안 필수 |
| **E. 이상값 압도** | Phase 1 반감기로 문제 피처 영향 호라이즌별 제한 | 간접 개선 | ★★★ |
| **F. 방향 비대칭** | Phase 0 버그 수정 (119차 포함) 완료 | **즉각 해소** | ★★★★★ |
| **G. 이중 패널티** | Phase 1 `entry_ok` 단일 게이팅으로 정리 | 부분 개선 | ★★★ |

### 드라마틱한 개선이 기대되는 2가지 메커니즘

**메커니즘 1 — FLAT 편향의 구조적 해소 (Phase 2)**

```
[현재] 1분봉 OFI → 30m 모델도 동일 입력
     → 30m 모델 FL 고착 → 앙상블 15% 가중치가 항상 FLAT 투표
     → up/down_score 상쇄 → confidence 0.33~0.42 수렴 → 진입0

[Phase 2 후] 1분봉 OFI → 1m 모델에만 강하게 (반감기 1.0)
            30분봉 VWAP/macro → 30m 모델에만 강하게 (반감기 1.0)
            → 각 모델이 자신의 시간 규모 신호 포착
            → UP/DOWN 확률 분포 1/3 이탈 → confidence 상승
```

추정 효과: FLAT 고착 빈도 -50%, confidence 평균 +0.05~0.08, 진입 가능 분 +20~30%

**메커니즘 2 — 방향 비대칭 버그 전수 수정 (Phase 0)**

`ofi_imbalance abs()` 제거 후 OFI가 부호를 유지하면 숏 방향 체크리스트 통과율이 롱과 대등해짐.
**숏 진입 기회 현재 대비 약 2배 증가** 가능. 방향 편중으로 인한 진입0 즉각 해소.

### 정량 기대치

| 지표 | v7.x (115차 재훈련 기준) | v8.0 Phase 1 예상 | v8.0 Phase 2 예상 |
|------|------------------------|-----------------|-----------------|
| 1m 정확도 | 42.9% | 45~47% | 47~52% |
| 5m 정확도 | 56.9% | 58~60% | 60~65% |
| 30m 정확도 | 58.4% | 59~61% | 63~68% |
| 일평균 진입 기회 | 0~3회 | 3~6회 | 5~10회 |
| Precision (A등급) | 추정 60~65% | 65~70% | 70~75% |

> **주의**: Phase 2는 재학습 없이는 효과 없음. 코드만 변경하고 기존 모델 유지 시 입력 분포 불일치로 성능 저하.

---

## 부록 C — 진입0 씨앗 제거 추가 방안 (v8.0 전용)

### 추가 방안 1 — FL 고착 조기 감쇠 (20분 대기 → 10분 조기 차단)

**문제**: 현재 FL 90%+ **20분** 지속 후 uniform fallback → 20분 동안 앙상블 오염  
**파일**: `strategy/ensemble_decision.py`

```python
# FL 70%+ 10분이면 가중치 점진 감쇠 (uniform 전 단계)
if fl_ratio > 0.70 and fl_streak_min >= 10:
    horizon_weights[h] *= 0.2    # 점진적 감쇠
    log("[EarlyFLDamp] %s fl=%.0f%% %dmin → weight×0.2", h, fl_ratio*100, fl_streak_min)
if fl_ratio > 0.90 and fl_streak_min >= 20:
    horizon_weights[h] = 0.0     # 기존 처리 유지
```

---

### 추가 방안 2 — 봉 완성 간격 중 캐시 신뢰도 감쇠 (Phase 2 전용)

**문제**: Phase 2에서 3m 봉 완성 후 1~2분이 지난 캐시 예측으로 진입하는 위험  
**파일**: `main.py` STEP 5

```python
BAR_CACHE_DECAY = {3: 0.97, 5: 0.95, 10: 0.93, 15: 0.92, 30: 0.90}
# 매분: cached_conf[h] *= BAR_CACHE_DECAY[h_min]  (봉 미완성 분에만 적용)
# 봉 완성 시: cached_conf[h] = 신규 예측값으로 리셋
```

---

### 추가 방안 3 — AutoMaskedFallback 자동 발동 (이상값 피처 3개+ 시)

**문제**: 현재 MaskedFallback은 수동 트리거(D_FORCE 연동). 이상값 피처가 3개+ 동시 발생 시 자동 발동 필요  
**파일**: `model/multi_horizon_model.py`

```python
outlier_feats = [f for f in feature_names if abs(z_scores[f]) > 4.0]
if len(outlier_feats) >= 3:
    masked_result = self._predict_masked(x, outlier_feats)
    if masked_result["confidence"] - raw_result["confidence"] >= 0.05:
        result = masked_result
        log("[AutoMasked] %d feats masked, conf +%.3f", len(outlier_feats), gain)
```

---

### 추가 방안 4 — feature_quality_score 기반 동적 min_conf 양방향 조정

**문제**: 현재 min_conf는 레짐 기반 단방향. 피처 품질 우수 시 진입 기회를 늘리는 하향 조정 없음  
**파일**: `main.py` STEP 5 후

```python
fq = features.get("feature_quality_score", 0.5)
if fq >= 0.9:    dynamic_mc -= 0.03   # 피처 품질 우수 → 진입 완화
elif fq < 0.6:   dynamic_mc += 0.05   # 피처 품질 불량 → 진입 강화
# 반드시 MC_ABS_CEIL 범위 내에서만 조정
```

---

### 추가 방안 5 — Phase 2 스케일러 정합성 검증 (신규 위험 방어)

**문제**: Phase 2에서 호라이즌별 봉 분리 후 스케일러도 분리 → 불일치 ERR-FATAL 신규 경로 생성  
**파일**: `model/multi_horizon_model.py`

```python
def validate_horizon_scaler_consistency(self):
    """호라이즌별 스케일러가 해당 N분봉 데이터로 적합됐는지 메타 검증"""
    for h, scaler in self.scalers.items():
        h_meta = self._scaler_meta.get(h, {})
        if h_meta.get("bar_horizon") != h:
            log.warning("[ScalerMeta] %s 스케일러 봉 불일치 → 재적합 예약", h)
            self._mark_retrain_needed(h)
```

---

### 추가 방안 6 — cold-start 진입 억제 2단계 세분화

**문제**: 09:00~09:05 차단 외 09:05~09:15 구간이 무방비. 이 구간은 갭 리스크와 스케일러 미워밍업이 겹침

```
09:00~09:05: 전 차단 (cold-start, 기존 유지)
09:05~09:10: 1m만 허용, A등급 7/7 충족 시만 진입 (극선별)
09:10~09:15: 1m·3m, A등급 6/7 이상
09:15~     : 전 정상 가동
14:00~15:00: 30m 비활성 (현재 봉이 마감 후를 포함할 위험)
15:00~15:10: 1m·3m만, 청산 집중 (look-ahead 방지)
```

---

### 추가 방안 7 — 진입0 자동 원인 진단 로그

**문제**: 진입0 발생 시 원인 파악에 수동 로그 분석 필요. 반복 재발의 근본 원인  
**파일**: `main.py`

```python
def _diagnose_zero_entry(self, features, horizon_proba, ensemble_result):
    reasons = []
    if ensemble_result.get("coherence_blocked"):  reasons.append("CoherenceGate")
    if ensemble_result.get("cascade_blocked"):    reasons.append("CascadeCoherence")
    if ensemble_result.get("direction") == 0:     reasons.append("FLAT수렴")
    if self._is_eks_active():                     reasons.append("EKS발동")
    conf, mc = ensemble_result.get("confidence", 0), self._current_mc
    if conf < mc:   reasons.append(f"conf미달({conf:.3f}<mc{mc:.3f})")
    fl_horizons = [h for h, v in horizon_proba.items() if v.get("flat", 0) > 0.7]
    if fl_horizons: reasons.append(f"FL고착({','.join(fl_horizons)})")
    outliers = [f for f in features if abs(self._z_score(f, features[f])) > 4.0]
    if outliers:    reasons.append(f"이상값피처({','.join(outliers[:2])})")
    if reasons:
        log_manager.signal(f"[ZeroDiag] 진입X 원인: {' / '.join(reasons)}")
```

---

### 추가 방안 요약 및 우선순위

| 방안 | 파일 | Phase | 진입0 씨앗 제거 대상 | 필수 여부 |
|------|------|-------|-------------------|---------|
| 1. FL 조기 감쇠 | ensemble_decision.py | 1 | 축 A 고착 조기 차단 | 권장 |
| 2. 캐시 신뢰도 감쇠 | main.py | 2 (전용) | Phase 2 신규 위험 | 권장 |
| 3. AutoMaskedFallback | multi_horizon_model.py | 1 | 축 E 이상값 압도 | 권장 |
| 4. fq 기반 mc 양방향 | main.py | 1 | 축 B 신뢰도 미달 | 선택 |
| 5. 스케일러 정합성 검증 | multi_horizon_model.py | 2 (전용) | 축 D 신규 위험 | **필수** |
| 6. cold-start 2단계 | config/settings.py | 1 | 축 C EKS 보완 | 권장 |
| 7. 진입0 진단 로그 | main.py | 1 | 운영 디버깅 | **필수** |

**Phase 2에서 방안 5·7 미포함 시 Phase 2가 새로운 진입0 원인을 만들 가능성 높음.**

---

---

## 부록 D — Raw DB 구조 분석 + Phase 2 재학습 방안

> 분석 기준: `data/db/raw_data.db` 실측 / `learning/batch_retrainer.py` / `utils/db_utils.py`

### D-1. Raw DB 현황 (실측)

**DB 파일 위치**
```
data/db/raw_data.db      ← 재학습 핵심 (72k봉)
data/db/predictions.db   ← 호라이즌별 예측 로그
data/db/trades.db        ← 매매 이력
data/db/shap_tracker.db  ← SHAP 기여도
```

**raw_candles 실측 현황**
```
기간: 2025-08-19 ~ 2026-06-05  (약 10개월)
총 행: 72,288봉 / 일평균: ~385봉
```

| 컬럼 | 저장 여부 | Phase 2 필요 여부 |
|------|---------|-----------------|
| ts, open, high, low, close | ✅ | ✅ N분봉 집계 핵심 |
| volume, bid1, ask1, oi | ✅ (NULL 가능) | ✅ spread/toxicity용 |
| **buy_vol** | ❌ **미저장** | ⚠️ CVD/OFI 집계에 필요 |
| **sell_vol** | ❌ **미저장** | ⚠️ CVD/OFI 집계에 필요 |

**raw_features 실측 현황**
```
총 행: 72,277봉 (candles와 1:1)
피처 수: 114개 (JSON blob)
호라이즌 컬럼: 없음 — 모두 1m 기반
```

**현재 재학습 흐름의 구조적 문제**
```
_load_from_db()
  └─ raw_features → X 행렬 [15,750행 × 114피처]   ← 전 호라이즌 동일 X
  └─ raw_candles(close만) → y_1m, y_3m, ..., y_30m  ← 라벨만 다름

_train_horizon("1m",  X, y_1m)   ← 동일 1분봉 피처
_train_horizon("3m",  X, y_3m)   ← 동일 1분봉 피처  ← 문제
_train_horizon("30m", X, y_30m)  ← 동일 1분봉 피처  ← 문제
```

30m 모델이 1분봉 OFI를 그대로 학습 → FLAT 편향 + confidence 미달의 DB 레벨 근본 원인.

---

### D-2. Phase 2 재학습을 위한 DB 구조 변경

**변경 1 — raw_candles에 buy_vol/sell_vol 추가**

```sql
ALTER TABLE raw_candles ADD COLUMN buy_vol  INTEGER DEFAULT 0;
ALTER TABLE raw_candles ADD COLUMN sell_vol INTEGER DEFAULT 0;
```

`db_utils.py` `save_candle()` 및 `save_candle_and_features()` INSERT 파라미터에 `buy_vol`, `sell_vol` 동시 추가.

**변경 2 — raw_features_horizon 신규 테이블 (핵심)**

```sql
CREATE TABLE IF NOT EXISTS raw_features_horizon (
    ts       TEXT NOT NULL,
    horizon  TEXT NOT NULL,   -- "1m","3m","5m","10m","15m","30m"
    features TEXT NOT NULL,   -- JSON (호라이즌별 반감기 적용 포함)
    PRIMARY KEY (ts, horizon)
);
CREATE INDEX IF NOT EXISTS idx_rfh_horizon ON raw_features_horizon(horizon, ts);
```

**변경 3 — raw_candles_aggregated (N분봉 집계 캐시)**

```sql
CREATE TABLE IF NOT EXISTS raw_candles_aggregated (
    ts       TEXT NOT NULL,
    horizon  TEXT NOT NULL,
    open  REAL, high  REAL, low  REAL, close REAL,
    volume INTEGER, buy_vol INTEGER, sell_vol INTEGER,
    PRIMARY KEY (ts, horizon)
);
```

---

### D-3. 호라이즌별 MIN_TRAIN_BARS 재설정

기존 단일 기준(15,000행) 대신 호라이즌별 시간 등가 기준 적용:

| 호라이즌 | 기존 기준 | Phase 2 기준 | 72k봉 기준 가용 행 | 충족 여부 |
|---------|---------|------------|-----------------|---------|
| 1m | 15,000 | 15,000 | 72,288 | ✅ |
| 3m | 15,000 | 5,000 | 24,096 | ✅ |
| 5m | 15,000 | 3,000 | 14,457 | ✅ |
| 10m | 15,000 | 1,500 | 7,228 | ✅ |
| 15m | 15,000 | 1,000 | 4,819 | ✅ |
| 30m | 15,000 | **500** | 2,409 | ✅ |

```python
# batch_retrainer.py 상단 상수 교체
MIN_TRAIN_BARS_PER_HORIZON = {
    "1m": 15000, "3m": 5000, "5m": 3000,
    "10m": 1500, "15m": 1000, "30m": 500,
}
```

**결론**: 기존 72k 봉 데이터로 **Phase 2 즉시 재학습 가능**.

---

### D-4. Backfill 피처 품질 등급

OFI·CVD는 tick 수준 데이터(buy_vol/sell_vol)가 없어 backfill 시 0으로 채워짐.

| 등급 | 피처 | backfill 방법 |
|------|------|-------------|
| **A — 완전 계산** | `ret_Nm`, `atr`, `atr_expansion_rate`, `ema_cross`, `bb_position`, `hurst`, `vwap_position`, `above_vwap`, `threshold_feasibility` | OHLCV로 정상 계산 |
| **B — 근사 가능** | `spread_ticks`, `volume_acceleration`, `bar_volume` | OHLCV 기반 추정 |
| **C — 0으로 채움** | `ofi_norm`, `mlofi_norm`, `cvd_delta_norm`, `cvd_slope`, `microprice_bias`, `queue_directional_depletion` | tick 데이터 없음 — FEATURE_HALFLIFE가 장기 모델 보상 |

**핵심 insight**: C등급 피처는 단기(1m/3m) 호라이즌에서만 중요(반감기 1.0)하고, 장기(10m+) 모델에서는 이미 반감기 0에 가까움. 따라서 backfill 품질 한계가 **장기 모델에는 영향 없고 단기 모델은 go-forward 데이터로 보완** 가능.

---

### D-5. 코드 변경 목록

**`batch_retrainer.py` — `_load_from_db()` Phase 2 분기**

```python
def _load_from_db(self, weeks_back: int, use_horizon_features: bool = False):
    if use_horizon_features and self._has_horizon_features_table():
        return self._load_from_db_phase2(weeks_back)
    return self._load_from_db_legacy(weeks_back)   # 기존 경로 완전 유지

def _load_from_db_phase2(self, weeks_back: int):
    """Phase 2: raw_features_horizon 테이블에서 호라이즌별 독립 로드"""
    result = {}
    for hz, h_min in HORIZONS.items():
        min_bars = MIN_TRAIN_BARS_PER_HORIZON[hz]
        rows = self._fetch_horizon_features(hz, weeks_back)
        if len(rows) < min_bars:
            logger.warning("[Retrain-P2] %s 부족 %d < %d", hz, len(rows), min_bars)
            result[hz] = None
            continue
        X_hz, feat_names = self._build_X(rows, hz)
        y_hz = self._build_y_horizon(rows, hz, h_min)
        result[hz] = (X_hz, y_hz, feat_names)
    return result
```

**`retrain_now()` — Phase 2 경로 분기**

```python
def retrain_now(self, weeks_back=10, use_horizon_features=False, force=False):
    data = self._load_from_db(weeks_back, use_horizon_features)

    if isinstance(data, dict):          # Phase 2 경로
        for hz, pack in data.items():
            if pack is None: continue
            X_hz, y_hz, feat_names_hz = pack
            self._train_horizon(hz, X_hz, y_hz, feat_names_hz, force)
    else:                               # Legacy 경로 (Phase 0~1)
        X, y_dict, feat_names = data
        for hz in HORIZONS:
            self._train_horizon(hz, X, y_dict[hz], feat_names, force)
```

**`db_utils.py` — 신규 저장 함수**

```python
def save_horizon_features(ts: str, horizon: str, features: dict) -> None:
    """N분봉 완성 시 호라이즌별 피처 저장 (Phase 2 전용)"""
    execute(
        RAW_DATA_DB,
        "INSERT OR REPLACE INTO raw_features_horizon (ts, horizon, features) VALUES (?,?,?)",
        (ts, horizon, json.dumps(features, ensure_ascii=False)),
    )
```

**`main.py` — STEP 4 후 호라이즌별 피처 저장**

```python
# Phase 2: 봉 완성 시 호라이즌 피처 저장
for h_min, h_name in [(3,"3m"),(5,"5m"),(10,"10m"),(15,"15m"),(30,"30m")]:
    if completed_bars.get(h_min) is not None:
        h_feats = self.feature_builder.build_for_horizon(completed_bars[h_min], h_min)
        save_horizon_features(ts, h_name, h_feats)
# 1m은 기존 save_candle_and_features() 유지
```

**`scripts/eod_retrain.py` — --phase2 플래그 추가**

```python
parser.add_argument("--phase2", action="store_true",
                    help="Phase 2: 호라이즌별 피처 테이블 사용")
result = retrainer.retrain_now(
    weeks_back=args.weeks,
    use_horizon_features=args.phase2,
    force=args.force,
)
```

---

### D-6. Backfill 스크립트 설계 (`scripts/aggregate_and_backfill.py`)

Phase 2 배포 직후 1회 실행. 기존 raw_candles(72k행) → N분봉 집계 → 호라이즌별 피처 backfill.

```python
"""
scripts/aggregate_and_backfill.py — Phase 2 배포 직후 1회 실행
기존 raw_candles → N분봉 집계 → raw_features_horizon 생성
"""
from features.bar_aggregator import BarAggregator
from features.feature_decay import get_horizon_features, BACKFILL_QUALITY

HORIZONS_TO_BACKFILL = [3, 5, 10, 15, 30]  # 1m은 raw_features 그대로 사용

for h_min in HORIZONS_TO_BACKFILL:
    bars_1m = fetch_all_candles_from_db(weeks_back=10)
    aggregator = BarAggregator()
    count = 0

    for bar in bars_1m:
        completed = aggregator.push(bar)
        if completed.get(h_min) is None:
            continue

        agg_bar = completed[h_min]

        # A등급: OHLCV로 계산
        feats = compute_ohlcv_features(agg_bar, h_min)

        # C등급: 0으로 채움 (FEATURE_HALFLIFE가 장기 모델 보상)
        for feat in BACKFILL_QUALITY["C"]:
            feats[feat] = 0.0

        # 반감기 적용
        feats = get_horizon_features(feats, f"{h_min}m")
        save_horizon_features(agg_bar["ts"], f"{h_min}m", feats)
        count += 1

    logger.info("[Backfill] %dm 완료 — %d행 저장", h_min, count)
```

---

### D-7. 단계별 재학습 로드맵

```
[Stage 1 — Phase 2 코드 완성 당일]

  Step 1. DB 스키마 변경
    ALTER TABLE raw_candles ADD buy_vol/sell_vol
    CREATE TABLE raw_features_horizon
    CREATE TABLE raw_candles_aggregated

  Step 2. Backfill 실행 (30분 내외)
    python scripts/aggregate_and_backfill.py --weeks 10
    → raw_features_horizon: A·B등급 피처 포함, C등급 0

  Step 3. Phase 2 즉시 재학습
    python scripts/eod_retrain.py --phase2 --weeks 10 --force
    → 6개 모델 호라이즌별 독립 X로 학습
    → 기대: 5m/10m/15m/30m +3~5%, 1m/3m 유사

  Step 4. 스케일러 정합성 검증
    validate_horizon_scaler_consistency() 자동 실행

──────────────────────────────────────────────
[Stage 2 — Phase 2 배포 후 +30일]

  buy_vol/sell_vol 30일치 누적 → OFI/CVD 포함 1m/3m 재학습
    python scripts/eod_retrain.py --phase2 --weeks 4
    → 1m/3m 모델 Stage 1 대비 추가 향상

──────────────────────────────────────────────
[Stage 3 — Phase 2 배포 후 +50일]

  전 호라이즌 go-forward 데이터 충분
    python scripts/eod_retrain.py --phase2 --weeks 8
    → 전 호라이즌 호라이즌별 봉 기반 완전 재학습
    → Phase 2 성능 완전 발현
```

---

### D-8. 재학습 검증 지표 (Phase 2 전·후 비교 기준)

| 지표 | v7.x 기준 (115차) | Stage 1 목표 | Stage 3 목표 |
|------|-----------------|------------|------------|
| 1m 정확도 | 42.9% | 43~45% | **47~52%** |
| 5m 정확도 | 56.9% | 60~62% | **62~65%** |
| 30m 정확도 | 58.4% | 62~64% | **64~68%** |
| FLAT 비율 (10m/15m) | ~40%+ | ~33% | **~28~32%** |
| 일평균 진입 기회 | 0~3회 | 3~5회 | **5~10회** |

---

### D-9. Phase 2 재학습 Todo 추가

**즉시 처리 (Phase 2-A 전에 선행)**
- [ ] `utils/db_utils.py` — `raw_candles` `buy_vol`/`sell_vol` 컬럼 추가 + INSERT 수정
- [ ] `utils/db_utils.py` — `init_raw_data_db()` `raw_features_horizon` 테이블 생성 추가
- [ ] `utils/db_utils.py` — `save_horizon_features()` 신규 함수 추가

**Phase 2 구현과 세트**
- [ ] `learning/batch_retrainer.py` — `MIN_TRAIN_BARS_PER_HORIZON` 상수 추가
- [ ] `learning/batch_retrainer.py` — `_load_from_db_phase2()` 분기 구현
- [ ] `learning/batch_retrainer.py` — `retrain_now(use_horizon_features=)` 파라미터 추가
- [ ] `scripts/eod_retrain.py` — `--phase2` 플래그 추가
- [ ] `scripts/aggregate_and_backfill.py` 신규 — Phase 2 배포 직후 1회 실행용
- [ ] `main.py` STEP 4 후 — `save_horizon_features()` 호출 추가 (봉 완성 시)

---

*미륵이 KOSPI200 선물 자동매매 v8.0 — 2026-06-07*
