# 미륵이 정기 점검 계획서 — 모델·진입품질 미세조정

> 작성: 2026-06-24 (241차-b 세션 종료 후)
> 목적: DB 트렌드 분석 → 편향·이상점 감지 → 파라미터 미세조정의 주기적 실행

---

## 배경 — 이번 세션에서 발견된 것들

6/8 완성봉 커밋 전후 DB 딥다이브 결과 4가지 독립적 버그·설계 결함이 발견·수정됨:

| 차수 | 커밋 | 발견 방법 | 수정 내용 |
|---|---|---|---|
| 237 | aa42a22 | trades DB `hurst_bucket=""` 7건 → -2.9M 손실 | hurst_ready 플래그 + C급 P2-b setter |
| 238 | b24d9ba | ensemble_calibrator.pkl A≈0 → 상수 0.21 출력 | confidence_raw 캐시 저장 (피드백 루프 차단) |
| 239 | 6ff7bc6 | C급 conf_floor 미적용 → 14:04(-1.27M) 통과 | P5 경로 conf<0.33 차단 추가 |
| 240 | a36c04b | MetaConf blended_conf ≥ take_thr 구조적 불가 | CONF_HIGH 0.60→0.37, 임계값 전면 하향 |
| 241-b | 62e66b4 | 1m DN 편향 47~64% 무감지 → acc 0.047 하락 | _bias_buf 윈도우·임계값 4종 조정 |

---

## 점검 주기 체계

```
매일 (장 마감 후)     → Section 1, 2
매주 월요일 (장 전)   → Section 3, 4, 5
매월 1일              → Section 6 (전략 건전성 종합)
```

---

## Section 1 — 매일 점검 (장 마감 후 5분)

### 1-A. Platt 보정기 상태

**조회 방법:**
```python
import joblib, numpy as np
obj = joblib.load("data/ensemble_calibrator.pkl")
lr  = obj["model"]
A, B = lr.coef_[0][0], lr.intercept_[0]
probs = obj["probs"]
print(f"A={A:.4f}  B={B:.4f}  n={obj['n']}")
print(f"probs 범위: {min(probs):.3f}~{max(probs):.3f}  평균={sum(probs)/len(probs):.3f}")
# 보정 시뮬: calibrate(0.40)
cal = 1/(1+np.exp(-(A*0.40+B)))
print(f"calibrate(0.40) → {cal:.4f}")
```

**이상 판정 기준:**
| 지표 | 정상 범위 | 이상 기준 | 조치 |
|---|---|---|---|
| A (기울기) | -2.0 ~ -0.2 | \|A\| < 0.05 | pkl 삭제 → cold-start |
| probs 범위 | 0.25 ~ 0.55 | max-min < 0.05 | 피드백 루프 재발 의심 → 238차 수정 재확인 |
| calibrate(0.40) | 0.28 ~ 0.38 | < 0.22 또는 = calibrate(0.80) | 상수 출력 → pkl 삭제 |
| n (누적 샘플) | ≥ 80 | < 80 | cold-start 중 (정상, 80분 대기) |

**조치 명령:**
```bash
# 이상 시 초기화
del data\ensemble_calibrator.pkl
# 다음 기동에서 cold-start → 약 80봉 후 자동 재학습
```

---

### 1-B. 1m 방향 편향 확인

**조회 방법 (SQL):**
```sql
SELECT
    date(ts) as d,
    ROUND(100.0*SUM(CASE WHEN direction=-1 THEN 1 ELSE 0 END)/COUNT(*),1) as pred_dn_pct,
    ROUND(100.0*SUM(CASE WHEN actual=-1 THEN 1 ELSE 0 END)/COUNT(*),1)   as real_dn_pct,
    ROUND(AVG(CASE WHEN correct=1 THEN 1.0 ELSE 0.0 END),3) as acc
FROM predictions
WHERE horizon='1m' AND correct IS NOT NULL AND actual IS NOT NULL
  AND date(ts) >= date('now','-5 days')
GROUP BY d ORDER BY d;
```

**이상 판정:**
| 지표 | 정상 | 경보 | 조치 |
|---|---|---|---|
| 예측DN% - 실제DN% | ±10%p 이내 | > +20%p | BiasReset 임계 재검토, SGD reset 로그 확인 |
| 1m acc | ≥ 0.34 | < 0.30 | SGD 편향 점검 → online_learner.reset_daily() 고려 |
| FLAT 예측비율 | 15 ~ 35% | < 10% | 1m DN 편향 심화 → BiasReset 발동 여부 확인 |

**BiasReset 발동 로그 확인 포인트 (LEARNING.log):**
```
[BiasReset] 1m DN편향 63% → uniform fallback 적용 (20분 후 자동해제)
[BiasReset] 1m DN편향 → uniform fallback 해제 (정상화)
```

---

### 1-C. 오늘 진입 품질 스냅샷

**조회 방법 (SQL):**
```sql
-- 오늘 실행 건 요약
SELECT
    time(entry_ts) as t, direction, grade,
    net_pnl_krw, exit_reason
FROM trades
WHERE date(entry_ts) = date('now')
ORDER BY entry_ts;

-- conf(ema) 분포 (오늘)
SELECT
    CAST(ROUND(confidence*10)*10 AS INT) as cb,
    COUNT(*) as n,
    SUM(entry_executed) as exec
FROM ensemble_decisions
WHERE date(ts) = date('now')
GROUP BY cb ORDER BY cb;
```

**이상 판정:**
| 지표 | 정상 | 경보 |
|---|---|---|
| C급 진입 중 conf<0.33 건수 | 0건 | > 0건 → 239차 수정 미적용 확인 |
| hurst_bucket="" 거래 건수 | 0건 | > 0건 → 237차 수정 미적용 확인 |
| 최대 단건 손실 | < -500K | > -800K → 손실 케이스 분석 |

---

## Section 2 — 매일 점검 (장 마감 후 10분)

### 2-A. MetaConf 상태

**조회 방법 (JSON):**
```python
import json
with open("meta_gate_tuning_metrics.json") as f:
    m = json.load(f)
print(f"avg_meta_confidence: {m['avg_meta_confidence']}")
print(f"take 비율: {m['realized_actions']['take']}/{m['count']}")
# best_grid
bg = m['best_grid']
print(f"best threshold: take={bg['take_threshold']} match={bg['match_rate']:.3f}")
print(f"take_count={bg['take_count']}  reduce_count={bg['reduce_count']}")
```

**DB 조회:**
```sql
SELECT
    date(ts) as d,
    SUM(CASE WHEN meta_action='take' THEN 1 ELSE 0 END) as takes,
    SUM(CASE WHEN meta_action='reduce' THEN 1 ELSE 0 END) as reduces,
    SUM(CASE WHEN meta_action='skip' THEN 1 ELSE 0 END) as skips,
    COUNT(*) as total,
    ROUND(AVG(meta_confidence),4) as avg_blended
FROM ensemble_decisions
WHERE date(ts) >= date('now','-5 days')
GROUP BY d ORDER BY d;
```

**이상 판정 및 미세조정 파라미터:**
| 지표 | 정상 목표 | 현재 | 파라미터 | 조정 방향 |
|---|---|---|---|---|
| take 비율 | 5~15% | ~1% | `take_floor` (meta_gate.py) | 낮추면 take↑ |
| avg_blended | 0.38~0.50 | 0.38 | `CONF_HIGH` (meta_confidence.py) | 0.37 기준 (240차) |
| skip 비율 | 50~70% | ~50% | `reduce_base` | 낮추면 reduce↑ |

**240차 수정 후 추적:**
```
기대값: take 5~15%, blended P90=0.50+
이상 시: meta_conf_state.pkl 삭제 → cold-start 재학습 (30봉)
```

---

## Section 3 — 매주 월요일 (장 전)

### 3-A. Calibration ECE 주간 추이

**조회 방법 (JSON):**
```python
import json
with open("calibration_metrics.json") as f:
    m = json.load(f)

print("=== 전체 (all) ===")
print(f"count={m['all']['overall']['count']}  acc={m['all']['overall']['accuracy']:.4f}")
print(f"ECE={m['all']['overall']['ece']:.4f}")

print("\n=== 최근 (recent, platt_since) ===")
print(f"platt_since={m['platt_since']}")
print(f"count={m['recent']['overall']['count']}  acc={m['recent']['overall']['accuracy']:.4f}")
print(f"ECE={m['recent']['overall']['ece']:.4f}")

print("\n=== 호라이즌별 recent acc ===")
for hz, v in m['recent']['by_horizon'].items():
    print(f"  {hz}: acc={v['accuracy']:.4f}  ECE={v['ece']:.4f}")
```

**이상 판정 및 미세조정 파라미터:**
| 지표 | 정상 | 경보 | 파라미터 | 조정 |
|---|---|---|---|---|
| overall ECE | < 0.10 | > 0.15 | Platt A/B | pkl 삭제 cold-start |
| recent acc | ≥ 0.33 | < 0.30 | GBM 재학습 주기 | `RETRAIN_WEEKS_BACK` |
| conf~80% acc | ≥ 0.35 | < 0.25 | Platt 역보정 | pkl 삭제 |
| 1m vs 30m acc 격차 | < 0.05 | > 0.08 | 호라이즌 가중치 | F1 AdaptiveWeight |

---

### 3-B. GBM 모델 건전성

**조회 방법:**
```python
import pickle, joblib, os
MODEL_DIR = "model/horizons"
for hz in ['1m','3m','5m','10m','15m','30m']:
    m = joblib.load(f"{MODEL_DIR}/gbm_{hz}.pkl")
    with open(f"{MODEL_DIR}/feature_names_{hz}.pkl",'rb') as f:
        fn = pickle.load(f)
    n_feat_model = getattr(m, 'n_features_in_', '?')
    opts = [n for n in fn if 'opt' in n.lower()]
    print(f"{hz}: GBM={n_feat_model}  pkl={len(fn)}  opt={opts}")
```

**이상 판정:**
| 지표 | 정상 | 경보 | 조치 |
|---|---|---|---|
| GBM n_features == pkl 수 | 일치 | 불일치 | EOD 재학습 강제 실행 |
| 1m opt 피처 수 | 0개 | > 0개 | JSON 레지스트리 슬라이싱 확인 |
| 5m opt 피처 | opt_pcr_slope_norm만 | opt_chain_pcr 포함 | JSON 슬라이싱 재확인 |

**파라미터 미세조정 기준:**

```
feature_names_*.pkl vs JSON horizon_feature_sets.json 불일치 시:
→ python scripts/eod_retrain.py --force --weeks 26
```

---

### 3-C. 진입 등급·conf_floor 효과 주간 분석

**조회 방법 (SQL):**
```sql
-- 주간 C급 conf_floor 차단 효과
SELECT
    date(ts) as d,
    COUNT(*) as c_grade_exec,
    SUM(CASE WHEN confidence < 0.33 THEN 1 ELSE 0 END) as would_block,
    ROUND(AVG(confidence),4) as avg_conf
FROM ensemble_decisions
WHERE grade='C' AND entry_executed=1
  AND date(ts) >= date('now','-7 days')
GROUP BY d ORDER BY d;

-- 거래 결과 by 등급 (주간)
SELECT
    grade,
    COUNT(*) as n,
    SUM(CASE WHEN net_pnl_krw>0 THEN 1 ELSE 0 END) as wins,
    ROUND(AVG(net_pnl_krw)) as avg_pnl,
    ROUND(SUM(net_pnl_krw)) as sum_pnl
FROM trades
WHERE date(entry_ts) >= date('now','-7 days')
GROUP BY grade ORDER BY grade;
```

**파라미터 미세조정 기준:**
| 지표 | 현재 값 | 파라미터 | 조정 기준 |
|---|---|---|---|
| conf_floor | 0.33 | `ENS_CONF_FLOOR_FOR_AUTO` (settings.py) | C급 acc 지속 < 40% → 0.35 검토 |
| C급 size mult | 설정값 | `C_AUTO_EXP_SIZE_MULT` | C급 EV 음수 지속 → 비활성화 |
| 시간대별 차단 | — | `C_AUTO_EXP_ZONES` | 특정 zone에서 손실 집중 시 제거 |

---

### 3-D. 1m 호라이즌 acc 주간 추이 + BiasReset 효과

**조회 방법 (SQL):**
```sql
-- 1m 방향 편향 주간
SELECT
    date(ts) as d,
    ROUND(100.0*SUM(CASE WHEN direction=-1 THEN 1 ELSE 0 END)/COUNT(*),1) pred_dn,
    ROUND(100.0*SUM(CASE WHEN actual=-1 THEN 1 ELSE 0 END)/COUNT(*),1) real_dn,
    ROUND(100.0*SUM(CASE WHEN direction=0 THEN 1 ELSE 0 END)/COUNT(*),1) pred_flat,
    ROUND(100.0*SUM(CASE WHEN actual=0 THEN 1 ELSE 0 END)/COUNT(*),1) real_flat,
    ROUND(AVG(CASE WHEN correct=1 THEN 1.0 ELSE 0.0 END),4) acc
FROM predictions
WHERE horizon='1m' AND correct IS NOT NULL AND actual IS NOT NULL
  AND date(ts) >= date('now','-7 days')
GROUP BY d ORDER BY d;
```

**파라미터 미세조정 기준 (241차-b):**
| 지표 | 정상 | 조정 대상 | 기준 |
|---|---|---|---|
| 1m DN 편향 Δ | < ±10%p | `_BIAS_RESET_THR["1m"]` = 0.62 | DN 50~60%인데 acc<0.35 지속 → 0.58 검토 |
| BiasReset 발동 빈도 | 주 1~3회 | `_dn_up_streak` = 8 | 발동 0회+acc 낮음 → 6분으로 단축 |
| BiasReset 오발동 | 0회 | `_acc_ok_for_bias` = 0.50 | 발동 후 acc 개선 없으면 0.48 강화 |
| bias_buf 45봉 충족 시간 | 45분 | `_BIAS_MAXLEN["1m"]` | 점심 편향 감지 느리면 60 검토 |

---

## Section 4 — 매주 월요일 (선택)

### 4-A. MetaConf LR 품질 — CONF_HIGH 적정성 (240차 후속)

**조회 방법:**
```python
import sqlite3, json, numpy as np

db = sqlite3.connect("data/db/predictions.db")
cur = db.cursor()
CONF_HIGH = 0.37   # 현재 설정값

cur.execute("""
    SELECT p.confidence, p.correct
    FROM predictions p
    WHERE p.horizon='1m' AND p.correct IS NOT NULL
      AND p.ts >= date('now','-7 days')
""")
rows = cur.fetchall()

counts = {0:0, 1:0, 2:0, 3:0}
for conf, correct in rows:
    if correct and float(conf) >= CONF_HIGH: q=3
    elif correct:                             q=2
    elif float(conf) < CONF_HIGH:            q=1
    else:                                     q=0
    counts[q] += 1

n = len(rows)
weights = [0.0, 1/3, 2/3, 1.0]
expected = sum(counts[q]*weights[q] for q in range(4))/n
labels = ["Q0(틀림+고신뢰)","Q1(틀림+저신뢰)","Q2(맞음+저신뢰)","Q3(맞음+고신뢰)"]
for q in range(4):
    print(f"{labels[q]}: {counts[q]:5d}건({counts[q]/n*100:.1f}%)")
print(f"기대 meta_conf 평균: {expected:.4f}")
```

**파라미터 미세조정 기준:**
| 지표 | 목표 | 조정 기준 |
|---|---|---|
| Q3 비율 | 15~30% | < 10% → CONF_HIGH 낮추기 (현재 0.37) |
| Q0 비율 | 30~60% | < 20% → CONF_HIGH 높이기 |
| 기대 meta_conf | 0.35~0.45 | 변화 없으면 CONF_HIGH 유지 |
| take 비율 (DB) | 5~15% | 지속 1% 이하 → take_floor 추가 하향 |

**CONF_HIGH 조정 레인지:** 0.33 ~ 0.42 (현재 0.37)
```
CONF_HIGH 낮추면: Q3↓ Q0↑ → 쌍봉 더 강해짐 (차별화↑, 평균score↓)
CONF_HIGH 높이면: Q3↑ Q0↓ → Q1/Q2 중심 (평균score↑, 차별화↓)
```

---

### 4-B. 진입 gate 체인 효과 분석

**조회 방법 (SQL):**
```sql
-- gate 차단 사유별 집계 (최근 1주)
SELECT
    entry_block_reason,
    COUNT(*) as n,
    ROUND(AVG(confidence),4) as avg_conf
FROM ensemble_decisions
WHERE date(ts) >= date('now','-7 days')
  AND entry_block_reason IS NOT NULL
  AND entry_block_reason != ''
GROUP BY entry_block_reason
ORDER BY n DESC
LIMIT 20;
```

**파라미터 미세조정 기준:**
| 차단 사유 | 비율 | 조정 기준 |
|---|---|---|
| Hurst 미계산 차단 | < 5% | > 10% → hurst_ready 조기 충족 여부 확인 |
| conf_floor 차단 | < 10% | > 20% → ENS_CONF_FLOOR 상향 검토 |
| CB HALTED | 0% | > 0% → CB 조건 완화 여부 검토 |
| JointGateBlock | 5~15% | > 25% → MetaGate/ToxGate 파라미터 점검 |

---

## Section 5 — 매주 월요일 (심층)

### 5-A. 호라이즌별 예측 정확도 추이 (4주)

**조회 방법 (SQL):**
```sql
SELECT
    horizon,
    strftime('%Y-W%W', ts) as week,
    ROUND(AVG(CASE WHEN correct=1 THEN 1.0 ELSE 0.0 END),4) as acc,
    ROUND(AVG(confidence),4) as avg_conf,
    COUNT(*) as n
FROM predictions
WHERE correct IS NOT NULL
  AND ts >= date('now','-28 days')
GROUP BY horizon, week
ORDER BY horizon, week;
```

**미세조정 트리거:**
| 현상 | 파라미터 | 조치 |
|---|---|---|
| 1m acc < 30m acc 격차 > 0.08 | F1 AdaptiveWeight | 1m 가중치 자동 감소 확인 |
| 특정 호라이즌 acc 2주 연속 < 0.30 | GBM 재학습 주기 | `RETRAIN_WEEKS_BACK` 증가 검토 |
| acc 전 호라이즌 동시 하락 | 피처 드리프트 | PSI 점검 → 스케일러 재적합 |

---

### 5-B. 시간대·레짐별 거래 품질 분석

**조회 방법 (SQL):**
```sql
-- 시간대별 PnL (최근 4주)
SELECT
    hour_bucket as hr,
    COUNT(*) as n,
    SUM(CASE WHEN net_pnl_krw>0 THEN 1 ELSE 0 END) as wins,
    ROUND(AVG(net_pnl_krw)) as avg_pnl,
    ROUND(SUM(net_pnl_krw)) as sum_pnl
FROM trades
WHERE date(entry_ts) >= date('now','-28 days')
  AND hurst_bucket != ''
GROUP BY hr ORDER BY hr;

-- Hurst bucket별 PnL
SELECT
    hurst_bucket,
    COUNT(*) as n,
    ROUND(SUM(CASE WHEN net_pnl_krw>0 THEN 1.0 ELSE 0.0 END)/COUNT(*),3) as wr,
    ROUND(AVG(net_pnl_krw)) as avg_pnl
FROM trades
WHERE date(entry_ts) >= date('now','-28 days')
GROUP BY hurst_bucket;
```

**미세조정 트리거:**
| 현상 | 파라미터 | 조치 |
|---|---|---|
| 특정 시간대 avg_pnl < -100K | `C_AUTO_EXP_ZONES` | 해당 zone 제거 검토 |
| hurst=mean-revert EV < 0 | Hurst 진입 차단 기준 | < 0.45 → < 0.50 강화 검토 |
| 특정 레짐 승률 < 45% | `REGIME_MIN_CONFIDENCE` | 해당 레짐 최소신뢰도 상향 |

---

## Section 6 — 매월 1일 (종합 점검)

### 6-A. Walk-Forward 전략 건전성

**체크리스트:**
```
□ 롤링 20일 Sharpe ≥ 1.0
□ 롤링 20일 MDD ≤ 15%
□ 롤링 20일 승률 ≥ 50%
□ CUSUM 상태 = CLEAR (strategy_report 확인)
□ PSI < 0.1 (전 CORE 피처)
```

**Phase 5 진입 조건 재검토 (매월):**
```
① 모의투자 4주 통산 수익률 양수
② Circuit Breaker 1회 이상 정상 작동 확인
③ Walk-Forward 26주 통과 (Sharpe≥1.5, MDD≤15%, 승률≥53%)
④ 일일 수익률 변동성 안정적
```

---

### 6-B. 파라미터 전체 현황표 (매월 기준값 갱신)

```
[Platt 보정]
  ENS_CONF_FLOOR_FOR_AUTO = 0.33          (마지막 조정: 236차)
  ensemble_calibrator.pkl 재보정 주기     (마지막: 238차 cold-start)

[MetaConf]
  CONF_HIGH                = 0.37          (마지막 조정: 240차)
  take_floor A/B/C         = 0.43/0.44/0.45 (마지막: 240차)
  take_ceil  A/B/C         = 0.55/0.56/0.57 (마지막: 240차)
  reduce_base A/B/C        = 0.27/0.28/0.30 (마지막: 240차)

[편향 감지]
  _BIAS_MAXLEN 1m          = 45봉           (마지막: 241차-b)
  _BIAS_RESET_THR 1m       = 0.62           (마지막: 241차-b)
  _acc_ok_for_bias 1m      = 0.50           (마지막: 241차-b)
  _dn_up_streak 1m         = 8분            (마지막: 241차-b)
  로그 경보 UP/DN           = 0.60           (마지막: 241차-b)
  로그 경보 FL              = 0.65           (마지막: 241차-b)

[진입 차단]
  hurst_ready 차단         = True           (마지막: 237차)
  C급 conf_floor           = 0.33           (마지막: 239차)
  JointGateBlock mult 기준  = 0.50           (마지막: 236차)
```

---

## Todo List — 다음 점검 예정 작업

### 즉시 (다음 거래일)

- [ ] **241차-b BiasReset 발동 확인** — `[DN편향⚠]`, `[BiasReset] 1m` 로그 출현 여부 확인
- [ ] **238차 Platt cold-start 완료 확인** — 15:40 EOD 후 `ensemble_calibrator.pkl` 저장 및 A값 확인
- [ ] **240차 MetaConf take 비율 변화** — `meta_gate_tuning_metrics.json` take_count 1% → 5%+ 달성 여부

### 이번 주 (6/25~6/27)

- [ ] **1m acc 개선 추적** — 0.342 → 0.360+ 달성 여부 (예측DB 분석)
- [ ] **MetaConf blended_conf P90** — 0.46 → 0.50+ 달성 여부
- [ ] **conf_floor 효과 집계** — C급 차단 건수, 차단 대상 PnL 분석

### 다음 주 (6/30~7/4)

- [ ] **CONF_HIGH 재검토** — Q3 비율 15~30% 확인, 미달 시 CONF_HIGH 조정 (-0.01~-0.02)
- [ ] **BiasReset 임계 재검토** — 오발동 0건 확인, 발동 지연 > 10분 시 streak 6분 검토
- [ ] **MetaConf take_floor 재검토** — take 비율 5%+ 미달 시 0.43→0.40 추가 하향

### 매월 (7/1)

- [ ] **Walk-Forward 월간 결과** — Sharpe, MDD, 승률 체크
- [ ] **파라미터 전체 현황표 갱신** (Section 6-B 업데이트)
- [ ] **실전 전환 조건 재검토**

---

## 분석 스크립트 위치

| 분석 | 스크립트 경로 |
|---|---|
| conf(ema) + 호라이즌 정확도 | `_analyze_0608.py` (루트) |
| 1m 방향 편향 딥다이브 | 이 세션 scratchpad |
| MetaConf 임계값 시뮬 | 이 세션 scratchpad |
| conf_floor 영향 분석 | 이 세션 scratchpad |

> 주기적 분석 스크립트 정규화 필요 → `scripts/analysis/` 폴더로 이동 권장

---

문서 구조 요약:

주기	섹션	소요시간	핵심 체크
매일	1-A~C	~5분	Platt A값, 1m DN편향 Δ, 오늘 진입 이상
매일	2-A	~3분	MetaConf take 비율, blended avg
매주	3-A~D	~20분	ECE 추이, GBM 피처 수 일치, conf_floor 효과, BiasReset 발동
매주	4-A~B	~15분	CONF_HIGH 적정성, gate 차단 사유
매주	5-A~B	~15분	호라이즌 acc 4주, 시간대·Hurst PnL
매월	6-A~B	~30분	WalkForward 건전성, 파라미터 현황표 갱신

각 섹션에 조회 SQL/Python + 이상 판정 기준 + 조정 대상 파라미터 + 조정 방향이 한 세트로 묶여 있어, 다음 세션에서 바로 실행 가능합니다.


*마지막 갱신: 2026-06-24 | 다음 갱신 예정: 2026-06-30*
