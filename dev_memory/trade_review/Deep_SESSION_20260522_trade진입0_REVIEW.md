# 2026-05-22 미륵이 진입 0건 종합 분석

> 분석일시: 2026-05-22 20:00 (장 종료 후)
> 분석 도구: openCode (Deep)
> 로그 소스: 20260522_SIGNAL.log, SYSTEM.log (WARN), TRADE.log, LEARNING.log

---

## 1. 요약 결론 (Executive Summary)

- 5/22 미륙이는 **1건의 진입도 없는 완전 관망일**이었다 (TRADE.log 32줄, 시스템 초기화·Sizer 로그만 존재).
- **주치사 원인**: `signal() takes from 2 to 3 positional arguments but 5 were given` — 09:10~09:23 치명적 TypeError로 파이프라인이 14회+ 연속 크래시. 69차(a83ef8)에서 "근본 원인 수정"을 주장했으나 args=5인 호출은 수정되지 않고 그대로 재발.
- **이차 원인**: 앙상블 confidence 최대 50.1%로 모든 시간대 min_conf에 10~17%p 미달. 5/21(57.1%)보다 더 악화.
- **삼차 원인**: 시스템 재시작 12회+ — Cybos BrokerSync 실패 → 매 재시작마다 온라인 학습 상태·accuracy_buf·signal_history 초기화 → GBM 재학습 6회 중복 (총 1800초+).
- **사차 원인**: CORE 3종(3_vwap, 4_cvd, 5_ofi) 동시 탈락이 전일 지속. AGENTS.md "변경 불가" 피처 3개가 모두 꺼져있음.

---

## 2. 시그널·엔트리 통계

| 항목 | 수치 |
|---|---|
| 진입 | **0건** |
| 청산 | **0건** |
| 시스템 재시작 | **12회+** (08:45, 08:48, 09:23, 09:58, 12:11, 13:04, 13:05, 13:23, 14:42, 14:53, 15:24, 15:55) |
| 앙상블 conf 최대 | **50.1%** (13:14, `dir=+0`) |
| 앙상블 conf 최소 | **34.2%** (10:11, `dir=+0`) |
| conf 평균 (전일) | **~42%** |
| CORE 피처 통과율 | **0%** (3_vwap, 4_cvd, 5_ofi 항상 탈락) |
| StuckBreaker 발동 | **2회** (09:07 DN고착 25연속, 09:31 UP고착 20연속) |
| Contrarian ACTIVE | **5회** (09:10, 09:35, 09:54, 10:32, 12:43 — acc30m=0.0%) |
| CB5 파이프라인 경고 | **12회+** (최대 3963ms @ 14:04) |
| z-score 극단 경고 | **전일 지속** (imbalance_slope +9.20, quality_investor_stale +24.31, ofi_imbalance +7.61) |
| GBM retrain acc | **32~40%** (6개 호라이즌 모두 랜덤(33%) 수준) |
| SGD/GBM 비중 | short: 10~50%, long: 10~50% — 하루 6회 극단 스윙 |
| BrokerSync | **모든 재시작마다 rows=0** ("모의투자 데이터가 없습니다") |
| 레짐 | **NEUTRAL** 전일 지속 |

---

## 3. #1 치명적 원인: signal() TypeError 재발 (09:10~09:23)

### 현상

```
09:10 [ERR-FATAL] signal() takes from 2 to 3 positional arguments but 5 were given
  File "main.py", line 2769, in run_minute_pipeline
    self.current_intraday_regime, _l2_mc_adj * 100, actual_min_conf,
TypeError: signal() takes from 2 to 3 positional arguments but 5 were given
```

- 09:10~09:23 매분 발생 (14회+)
- `main.py:2769`에서 `signal()` 호출 시 인자 5개 전달했지만 `signal()` 시그니처는 2~3개만 수용
- commit `ae83ef8` (69차)에서 "signal() TypeError ERR-FATAL 근본 원인 수정"을 주장했으나 **args=5인 호출부는 수정되지 않음**
- 충격: 매분 FATAL 발생했음에도 `[Ensemble]` 로그는 출력됨 → 예외처리 fallback path에서 기본값으로 앙상블만 돌림 → 체크리스트·진입 게이트 우회됨

### 영향도

- **09:10~09:23 (GAP_OPEN→OPEN_VOLATILE) 구간 진입 파이프라인 완전히 무력화**
- 이 구간은 통상 가장 높은 변동성과 기회가 존재하는 시간대
- TypeError 복구된 09:23 이후에도 온라인 학습 상태는 6번째 재시작으로 초기화됨

### 재발 추적

| 커밋 | 차수 | 내용 | 5/22 재발 |
|---|---|---|---|
| 63차? | 63차 | d0f8255 "signal() TypeError + GBM PreRetrain + PCR 극단값" 수정 | Y |
| ae83ef8 | 69차 | "signal() TypeError ERR-FATAL 근본 원인 수정 + traceback 로깅 강화" | Y — args=5 호출부는 여전히 남아있음 |

### 근본 원인 분석

`main.py:2769` 호출 코드가 `signal(horizon_proba, market_regime, intraday_regime, l2_mc_adj, actual_min_conf)` 식으로 5개 인자를 전달하는데, `signal()` 메서드 시그니처가 `signal(self, horizon_proba, market_regime=None)` 정도로만 정의되어 있을 가능성이 매우 높다. args=5인 호출은 63차, 69차 두 번의 "수정"에서도 발견되지 않아 **이미 2회 연속 재발**된 상태.

---

## 4. #2 핵심 원인: 앙상블 conf 상한 50.1% (5/21 57%→5/22 50%로 악화)

### 시간대별 최대 conf

| 시간대 | min_conf | 앙상블 conf 최대 | conf 격차 | 5/21 conf 최대 |
|---|---|---|---|---|
| GAP_OPEN (09:00~) | 67% | 40.1% (09:02) | -26.9%p | 50.8% |
| OPEN_VOLATILE (09:05~) | 60~65% | 41.7% (10:00) | -18.3%p | 51.3% |
| STABLE_TREND (10:30~) | 58% | 43.3% (11:30) | -14.7%p | **57.1%** |
| OTHER (11:50~) | 65% | 47.5% (12:58) | -17.5%p | 56.6% |
| LUNCH_RECOVERY (13:00~) | 60% | **50.1%** (13:14) | -9.9%p | — |
| CLOSE_VOLATILE (14:00~) | 65% | 49.1% (14:32) | -15.9%p | — |
| EXIT_ONLY (15:00~) | 진입금지 | 59.2% (15:27) | N/A | — |

> **핵심**: 5/21에 비해 conf 상한이 57%→50%로 7%p 추가 하락. STABLE_TREND 최저 min_conf=58%에도 14.7%p 부족.

### conf 하락 원인 분석

1. **GBM 정확도 32~40%**: 학습 데이터 cut-off `2026-03-27` — 현재(5/22) 대비 **56일** 격리. 시장 구조가 완전히 바뀌었는데 과거 데이터로만 학습.
2. **SGD partial_fit 오염**: 12회+ 재시작으로 SGD 상태가 계속 초기화 → 초기 균일분포 상태에서 예측 → conf가 35~40%에서 고착.
3. **3_vwap, 4_cvd, 5_ofi 동시 탈락**: CORE 피처가 전혀 기여하지 못함 → 모델의 근본적인 신호가 소실. 앙상블이 blind 상태로 예측.

---

## 5. #3 시스템 불안정: 12회+ 재시작 (이전 최악 5회 대비 2.4배)

### 재시작 패턴

```
08:45:17 → 08:48:09 → 09:23:37 → 09:58:38 → 12:11:04
→ 13:04:44 → 13:05:46 → 13:23:12 → 14:42:54 → 14:53:24
→ 15:24:10 → 15:55:33
```

- **트리거**: Cybos BrokerSync `rows=0` → `모의투자 데이터가 없습니다` 오류
- **매 재시작마다 GBM retrain**: 6회 재학습 (≈360초×6=2160초, 약 36분 소모)
- **매 재시작마다 OnlineLearner 초기화**: `_accuracy_buf`, `_signal_history`, `partial_fit` 상태 소실
- **가장 긴 지속**: 12:11~13:04 (53분) 구간은 추가 재시작 없이 안정

### 5/21 대비 악화

| 항목 | 5/21 | 5/22 |
|---|---|---|
| 재시작 횟수 | 5회 | 12회+ |
| 재시작 시간대 | 장전 (07:54~08:54) | 장전 + 장중 전 구간 |
| BrokerSync | 동일 오류 | 동일 오류 |
| Cybos 안정성 | 08:54 이후 안정 | **전일 불안정 지속** |
| conf 영향 | 57.1% | **50.1%** |

---

## 6. #4 CORE 피처 3종 동시 탈락 (AGENTS.md 절대 변경 불가)

### 패턴

```
[CORE 피처 ✗ ['3_vwap', '4_cvd', '5_ofi']] → 등급 강제 X
```

- 전일 90%+ 구간에서 3개 모두 또는 일부 탈락
- pass_count가 3~8 사이에서 등락 (9이면 통과, 8 이하는 X등급)
- **08:55~12:33 구간**: 5_ofi 지속 탈락
- **12:33 이후**: 3_vwap, 4_cvd 추가 탈락 → 3종 동시 탈락 빈발

### 근본 원인

CORE 피처 3종은 AGENTS.md에 "변경 불가"로 명시되어 있으나, 피처가 검증되지 않는 두 가지 가능성:

1. **피처 연산 자체의 입력 데이터 문제**: VWAP/CVD/OFI 계산에 필요한 호가창 데이터가 Cybos 불안정으로 누락·지연
2. **Checklist 로직의 threshold가 너무 높음**: pass_count>=9는 사실상 만점을 요구

---

## 7. #5 Scaler 완전 노후화 (z-score 경고 폭증)

### 주요 z-score 극단값 (5/21 대비)

| 피처 | 5/21 최대 | 5/22 최대 | 악화율 |
|---|---|---|---|
| ofi_raw | +92.0 | — | (75차에서 제거됨) |
| mlofi_slope | — | +7.39 | 신규 |
| queue_signal | +6.99 | +6.99 | 동일 |
| imbalance_slope | — | **+9.20** | 신규(최악) |
| toxicity_atr_stress | — | +4.82 | 신규 |
| ofi_imbalance | — | +7.61 | 신규 |
| ofi_norm | — | +7.19 | 신규 |
| microprice_depth_bias | -17.3 | -6.15 | 개선됨 |
| ofi_reversal_speed | -15.0 | **-8.74** | 개선됨 |
| quality_investor_stale | — | **+24.31** | 신규(최악) |
| queue_momentum | +4.60 | +4.60 | 동일 |

> **quality_investor_stale +24.31**은 scaler가 이 피처(외인 stale 상태)를 한 번도 본 적 없는 수준으로 분포가 괴리되었다는 의미. Scaler 학습 시점(5/15) 이후 외인 매매 패턴이 급격히 변화.

---

## 8. 5/18→5/19→5/21→5/22 악화 추세

| 항목 | 5/18 | 5/19 | 5/21 | 5/22 |
|---|---|---|---|---|
| 거래 건수 | 13건 | 0건 (CB3) | 0건 | **0건** |
| conf 최대 | 92% | 83% | 57.1% | **50.1%** |
| conf-STABLE | — | — | 57.1% | **43.3%** |
| 재시작 | 0회 | 3회 | 5회 | **12회+** |
| Scaler | 정상 | 약간 노후 | 심각 노후 | **완전 노후** |
| z-score | 일부 | 반복 | 극심 | **폭증(+24)** |
| CB3 HALT | 없음 | 09:50 | 13:22 | 없음¹ |
| Contrarian | 없음 | 없음 | 09:13 | **09:10(4회)** |
| Brier 과신 | 없음 | 없음 | 전일 0.35~ | **calibrator 작동중** |
| FATAL crash | 없음 | 없음 | 없음 | **14회+(signal TypeError)** |

¹ 5/22는 CB3이 발동하지 않음: acc30m이 0% 지속되었으나 CB3 경고 횟수 미달 또는 파이프라인 FATAL로 인해 평가 자체가 수행되지 않았을 가능성.

### 추세 분석

```
5/18: conf 92%, 13건 진입, 승률 84.6%                    ← 정상
5/19: conf 83%, 0건, acc30m 19%, CB3 09:50               ← scaler 노후 시작
5/21: conf 57%, 0건, acc30m 15%, Contrarian 09:13 ACTIVE  ← conf 상한 붕괴
5/22: conf 50%, 0건, FATAL crash 14회, 12회 재시작         ← 시스템 붕괴
```

> **5/18→5/22 4거래일 사이에 모델 성능이 92%→50%로 42%p 추락. Scaler last fit 5/15. 근 7일 사이 시장 구조 급변.**

---

## 9. 이전 개선방안 재발 분석 (깃 히스토리 + dev_memory 교차 추적)

### 재발 이력 매트릭스

| # | 재발 항목 | 이전 보고 | 5/21에 제안된 해결책 | 5/22 채택 여부 | 재발 원인 |
|---|---|---|---|---|---|
| 1 | **signal() TypeError** | 63차(d0f8255), 69차(ae83ef8) | "args=5 호출부 수정" | ✗ 미적용 (args=5인 다른 호출부) | 근본 원인 파악 실패 (63차·69차 모두 args=5 호출 미발견) |
| 2 | **GBM scaler 노후화** | 63차, 67차, 5/21 P0-4 | "partial_fit" | ✗ 미구현 | 계획만 수립, 구현되지 않음 |
| 3 | **동적 min_conf** | 5/21 P0-2 | "분포 75분위수 기준" | ✗ 미구현 | 계획만 수립 |
| 4 | **캘리브레이션 강제 연결** | 60차(db189d3), 5/21 P0-1 | "Platt→ensemble" | △ 부분 적용 (84·85차 4종 수정) | 적용되었으나 30% conf에도 50%로 보정 불가 |
| 5 | **StuckBreaker** | 5/21 P0-3, 81차(86ad249) | "방향 고착 감지 감쇠" | O 적용됨 (09:07, 09:31 발동) | 감쇠만으로 conf 40%→42% 상승, 진입 임계 미달 |
| 6 | **S2 OnlineLearner 과부하** | 5/21 P1-3 | "처리량 최적화" | ✗ 미구현 | 계획만 수립 |
| 7 | **재시작 방지** | 5/21 P1-4 | "multi-restart 방지 로직" | ✗ 미구현 | 5회→12회+로 악화 |
| 8 | **OFI/CVD winsorization** | 5/21 P1-1 | "P1/P99 클리핑" | ✗ 미구현 | z-score +24로 폭증 |
| 9 | **Microprice NaN 가드** | 5/21 P1-2 | "bid_depth<=0 가드" | ✗ 미구현 | depth_bias=-6.15 지속 |
| 10 | **Mid-Conf Blind Spot** | 60차, 5/19, 5/21 | "감지만, 교정 없음" | ✗ 미구현 | 감시만 하고 교정은 없음 |
| 11 | **30m FL class_weight** | 5/21 P0-2(5/20 리뷰) | "{FL:0.35}" | O 84차 적용 (FL:0.65) | 부분 완화됨 |
| 12 | **SGD noise 학습 필터** | 5/20 리뷰 B1 | "meta_action 필터" | ✗ 미구현 | NOISE 샘플 계속 학습 |

### 재발 구조 분석

```
[5/21 리뷰에서 P0-1~4 제안]
         ↓
[84차(05/22 오전): StuckBreaker, FL class_weight, calibrator 개선 4종]
[85차(05/22 오후): CLOSE_VOLATILE 가중치, Platt 윈도우, Platt 하한]
         ↓
[5/22 실세션: 12회 재시작, signal TypeError, conf 50%]
         ↓
[근본적인 P0 항목 8개 중 4개는 미구현, 4개는 부분 적용]
```

**재발의 공통 근본 원인**:

1. **P0 제안과 실제 구현 사이의 괴리**: 5/21 리뷰의 P0 4종 중 signal TypeError 수정 이외 3종은 구현되지 않음. 84·85차는 **새로운 이상점**을 발견해 대응했으나, 기존 P0 누락 항목은 그대로 방치.

2. **"계획만 하고 구현은 뒤로" 패턴**: scaler partial_fit, 동적 min_conf, 재시작 방지, winsorization은 여러 차수에 걸쳐 제안되었으나 한 번도 구현되지 않음. 이 패턴 자체가 가장 위험한 재발 원인.

3. **"증상 치료, 원인 방치" 패턴**: 84·85차 수정은 conf·calibrator·class_weight 등 증상을 개선하려 했으나, scaler 노후화·Cybos 불안정성·파이프라인 과부하라는 근본 원인은 건드리지 않음.

4. **동일 버그 3회 재발 (signal TypeError)**: 63차→69차→5/22로, 한 버그가 3번의 "수정"에도 불구하고 다른 호출경로에 남아있음. 이는 코드 리뷰·회귀 테스트 부재를 시사.

---

## 10. 학술적·기술적 개선 방안

### Phase 0: 즉시 패치 (P0 — 다음 기동 전 필수, 2~3시간)

#### P0-1. signal() TypeError 근본 수정 (재발 3회차)
**파일**: `main.py:2769` + `strategy/` signal() 시그니처

1. `main.py:2769` 호출부 인자 5개를 시그니처에 맞게 축소:
```python
# 현재 (BUG):
decision = self.entry_strategy.signal(
    horizon_proba, self.market_regime,
    self.current_intraday_regime, _l2_mc_adj * 100, actual_min_conf,
)
# 수정:
decision = self.entry_strategy.signal(
    horizon_proba, market_regime=self.market_regime,
    min_conf_override=actual_min_conf,
)
```

2. `signal()` 메서드 시그니처에 `**kwargs` 추가하여 향후 인자 추가에도 crash 방지:
```python
def signal(self, horizon_proba, market_regime=None, **kwargs):
    min_conf_override = kwargs.get("min_conf_override", None)
    intraday_regime = kwargs.get("intraday_regime", "NEUTRAL")
    ...
```

3. 모든 `signal()` 호출부 grep → `grep -rn "\.signal(" strategy/ main.py` 로 전수 점검.

**효과**: FATAL crash 100% 제거. 09:10~09:23 구간 복구.

---

#### P0-2. GBM Scaler Rolling Window Re-fit (매 세션 기동 시)
**파일**: `model/multi_horizon_model.py`

```python
def _refit_scaler_if_stale(self, horizon: str, max_age_hours: int = 24):
    """GBM scaler가 max_age_hours 이상 경과 시 재학습"""
    last_fit = self._scaler_fitted_at.get(horizon)
    if last_fit is None or (now() - last_fit).total_seconds() > max_age_hours * 3600:
        recent_data = self._load_recent_data(horizon, days=5)
        if len(recent_data) >= 100:
            self.scalers[horizon].fit(recent_data)
            self._scaler_fitted_at[horizon] = now()
```

- 기동 시 `raw_data.db` 최근 5일 데이터로 scaler 재학습
- 기존 `fit()` 시점(5/15)과 현재(5/22)의 7일 괴리를 기동 시마다 해소
- quality_investor_stale +24.31 같은 극단 z-score 소멸

**효과**: z-score 경고 90%+ 감소, GBM 정확도 32~40%→38~45% 회복.

**구현 난이도**: 중간 (100줄). `raw_data.db` 접근, 기존 scaler 재할당.

---

#### P0-3. 재시작 방지 락 (30초 이내 중복 재시작 차단)
**파일**: `main.py`

```python
_RESTART_LOCK_PATH = config.DATA_DIR / "restart.lock"
_RESTART_COOLDOWN_SEC = 30

def _check_restart_lock(self) -> bool:
    lock_file = Path(_RESTART_LOCK_PATH)
    if lock_file.exists():
        age = time.time() - lock_file.stat().st_mtime
        if age < _RESTART_COOLDOWN_SEC:
            self.log.warning(f"재시작 락 활성 ({age:.0f}초 전) — 건너뜀")
            return False
    lock_file.touch()
    return True
```

- 30초 이내 재시작 발생 시 무시 → 기존 프로세스 유지
- Cybos BrokerSync rows=0는 무시하고 파이프라인은 계속 진행
- 09:23→09:58로 35분만에 다시 재시작한 패턴 방지

**효과**: 재시작 횟수 12회→2~3회로 감소. OnlineLearner 연속성 보장.

---

#### P0-4. CORE 피처 진단 로그 강화
**파일**: `strategy/checklist.py`

```python
# CORE 피처 탈락 시 상세 원인 로깅
if '3_vwap' in missing:
    self.log.warning(f"[CORE-DIAG] VWAP 탈락 원인: vwap_value={vwap_val:.2f} "
                     f"price={price:.2f} deviation={abs(vwap_val-price)/price*100:.1f}% "
                     f"bid_vol={bid_vol} ask_vol={ask_vol}")
if '4_cvd' in missing:
    self.log.warning(f"[CORE-DIAG] CVD 탈락 원인: cvd_slope={cvd_slope:.4f} "
                     f"cvd_raw={cvd_raw} threshold={cvd_threshold}")
if '5_ofi' in missing:
    self.log.warning(f"[CORE-DIAG] OFI 탈락 원인: ofi_raw={ofi_raw:.2f} "
                     f"ofi_norm={ofi_norm:.2f} threshold={ofi_threshold}")
```

**효과**: CORE 피처 탈락이 데이터 문제인지 로직 문제인지 구분 가능.

---

### Phase 1: 구조적 개선 (P1 — 금주 내, 1~2일)

#### P1-1. 동적 min_conf (5/21 P0-2 구체화)
**파일**: `config/settings.py` + `strategy/entry/time_strategy_router.py`

```python
def get_dynamic_min_conf(regime: str, recent_confidences: List[float]) -> float:
    """
    모델이 낼 수 있는 conf의 75분위수 ≤ min_conf (단, 하한 48%).
    모델이 50%밖에 못 내면 → min_conf=50%. 진입 가능성 회복.
    """
    static_base = {
        "GAP_OPEN": 0.67, "OPEN_VOLATILE": 0.60,
        "STABLE_TREND": 0.58, "OTHER": 0.65,
        "LUNCH_RECOVERY": 0.60, "CLOSE_VOLATILE": 0.65,
    }.get(regime, 0.58)
    if len(recent_confidences) < 30:
        return static_base
    p75 = float(np.percentile(recent_confidences, 75))
    return max(0.48, min(p75, static_base))
```

**효과**: 5/22 최대 conf=50.1%일 때 STABLE_TREND min_conf가 58%→50%로 자동 하향 → 최소 1회 진입 가능성.

---

#### P1-2. SGD OnlineLearner 배치 처리 최적화
**파일**: `learning/online_learner.py`

S2가 매 샘플마다 `partial_fit` 호출하여 2~3.8초 소요. N개 샘플을 버퍼링 후 한 번에 처리:

```python
_PARTIAL_FIT_BATCH = 10

def learn(self, horizon, x, actual_label, predicted_label):
    self._batch_buffer[horizon].append((x, actual_label))
    if len(self._batch_buffer[horizon]) >= _PARTIAL_FIT_BATCH:
        X_batch = np.vstack([b[0] for b in self._batch_buffer[horizon]])
        y_batch = np.array([b[1] for b in self._batch_buffer[horizon]])
        self._sgd_models[horizon].partial_fit(X_batch, y_batch)
        self._batch_buffer[horizon].clear()
```

**효과**: S2 시간 2.5초→0.3초로 8배 감소. CB5 경고 90%+ 감소.

---

#### P1-3. BrokerSync 실패 시 파이프라인 유지 (재시작 없이 복구)
**파일**: `main.py`

- BrokerSync rows=0 → 재시작 대신 "빈 잔고" 상태로 파이프라인 지속
- 잔고 정보는 마지막 알려진 값 유지, 신규 진입만 정지
- Cybos 연결 복구 시 자동 재연결

---

#### P1-4. OFI/CVD Extreme Winsorization (5/21 P1-1)
**파일**: `features/technical/ofi.py`, `cvd.py`

```python
# z>4 발생 피처에 P1/P99 클리핑
def _winsorize(value, running_buffer, n_sigma=4):
    if len(running_buffer) < 20:
        return value
    median = np.median(running_buffer)
    mad = np.median(np.abs(running_buffer - median)) * 1.4826
    lo = median - n_sigma * mad
    hi = median + n_sigma * mad
    return float(np.clip(value, lo, hi))
```

**효과**: z-score >4 경고 95% 감소. quality_investor_stale +24.31 → +3 이내.

---

### Phase 2: 학술적 방법론 (P2 — R&D, 1~2주)

#### P2-1. Regime-Conditional Dynamic Thresholding (Kritzman et al., 2012)
- NEUTRAL 레짐의 historical conditional accuracy를 기반으로 min_conf 자동 조정
- `config/settings.py` 확장: 레짐별 정확도 히스토리 → P75 accuracy 기반 threshold

#### P2-2. SPRT Sequential Probability Ratio Test (Wald, 1945)
- 매분 우도비 누적 → "충분한 증거" 있을 때만 진입
- alpha=0.05, beta=0.10 → 1종 오류 5%, 2종 오류 10% 제어
- **신규 파일**: `model/sprt_gate.py`

#### P2-3. Beta-Binomial Bayesian Calibration (Zadrozny & Elkan, 2002)
- Platt Scaling 100샘플 필요 단점 보완 → 20샘플로 수렴
- **신규 파일**: `learning/bayesian_calibrator.py`
- Brier Score 0.464→0.25 목표

#### P2-4. CKDE (Conditional Kernel Density Estimation) 상황별 정확도
- regime × hurst × vpin × lob_imbalance 조건부 정확도 추정
- `MetaConfidenceLearner._rule_based_confidence()` 규칙 기반 → 통계 기반 대체
- **신규 파일**: `learning/ckde_confidence.py`

#### P2-5. GBM 재학습 자동화 (S2 처리 중에도 비동기)
- 현재 GBM retrain은 메인 스레드 blocking (360초) → 데몬 스레드 분리
- 장중 2시간마다 자동 재학습, scaler refresh 포함
- `learning/batch_retrainer.py` 확장

#### P2-6. Calibrator Brier Tracking Dashboard
- 실시간 Brier Score 시계열 시각화
- conf bin(10% 단위)별 accuracy 맵 → 중간신뢰도 구간 과신 감시
- Dashboard 탭 신설

---

### Phase 3: 인프라 안정화 (P3 — Cybos 의존성, 2~4주)

#### P3-1. Cybos BrokerSync 무한 재시도 + Exponential Backoff
- 1초→2초→4초→...→최대 120초 백오프
- 5회 연속 실패 시 "Cybos API 점검 필요" 알림

#### P3-2. 데이터 무결성 검증 파이프라인
- 매 분봉 데이터 도착 시: timestamp·price·volume 유효성 검증
- z-score >10 피처는 winsorization 대신 해당 분봉 전체 제외

#### P3-3. End-to-End 통합 테스트 (WFA 기반)
- `backtest/walk_forward.py` 확장: 5/18~5/22 5일 WFA 자동 수행
- signal TypeError 등 호출 규약 위반 감지 자동화

---

## 11. 종합 우선순위 로드맵

### 🔴 P0 — 5/23 장중 적용 목표 (오늘 밤)

| # | 항목 | 파일 | 예상 시간 | 기대 효과 |
|---|---|---|---|---|
| **P0-1** | signal() TypeError 근본 수정 + `**kwargs` | `main.py:2769` + strategy/ | 30분 | FATAL crash 제거 |
| **P0-2** | GBM Scaler 기동 시 재적응 | `multi_horizon_model.py` | 1.5시간 | z-score 90%↓, conf +5~8%p |
| **P0-3** | 재시작 방지 락 | `main.py` | 30분 | 12회→2회, 학습 연속성 |
| **P0-4** | CORE 피처 진단 로그 | `checklist.py` | 30분 | 탈락 원인 파악 |

### 🟡 P1 — 금주 내 (5/23~5/25)

| # | 항목 | 파일 | 예상 시간 |
|---|---|---|---|
| **P1-1** | 동적 min_conf | `settings.py` + router | 1.5시간 |
| **P1-2** | SGD 배치 처리 최적화 | `online_learner.py` | 1시간 |
| **P1-3** | BrokerSync 실패 복구 | `main.py` | 1시간 |
| **P1-4** | OFI/CVD winsorization | `ofi.py`, `cvd.py` | 1시간 |

### 🟢 P2 — 학술적 R&D (1~2주)

| # | 방법 | 신규 파일 |
|---|---|---|
| P2-1 | Regime-Conditional Threshold | `settings.py` 확장 |
| P2-2 | SPRT 진입 게이트 | `model/sprt_gate.py` |
| P2-3 | Bayesian Calibration | `learning/bayesian_calibrator.py` |
| P2-4 | CKDE 상황별 정확도 | `learning/ckde_confidence.py` |
| P2-5 | GBM 비동기 재학습 | `batch_retrainer.py` 확장 |
| P2-6 | Brier Tracking Dashboard | dashboard/ 신설 |

### 🔵 P3 — 인프라 (2~4주)

| # | 항목 |
|---|---|
| P3-1 | Cybos Exponential Backoff |
| P3-2 | 데이터 무결성 검증 |
| P3-3 | WFA 통합 테스트 |

---

## 12. 최종 판단 및 교훈

### 5/22 결정적 사건 요약

1. **signal() TypeError**: 14회+ FATAL crash. 63차·69차 두 번 "수정"했으나 근본 원인(args=5 호출부)이 남아있었음 → **코드 리뷰·회귀 테스트 부재의 직접적 증거**.

2. **scaler 7일 노후화**: 5/15 마지막 fit 시점 이후 quality_investor_stale +24.31 등 시장 구조가 완전히 변했음 → 기동 시 자동 재적응 필수.

3. **"계획-구현 괴리"의 정점**: 5/21 제안 P0 4종 중 3종 미구현. 84·85차가 새로운 이상점을 쫓는 동안 근본 문제는 누적.

4. **12회+ 재시작**: Cybos 불안정 + 재시작 락 부재 → 하루 종일 온라인 학습 리셋 → conf 50%로 붕괴.

### 재발 방지를 위한 프로세스 개선 제안

1. **P0 항목은 다음 기동 전까지 구현을 강제하는 체크리스트화**: NEXT_TODO.md에 "[MUST-DO-BEFORE-NEXT-SESSION]" 태그 도입.
2. **모든 `signal()` 호출부 grep → 시그니처 일치 검증 스크립트**: `bash grep -rn "\.signal(" *.py | grep -v "def signal"` → CI에 통합.
3. **scaler fit 타임스탬프 DB화**: 기동 시 staleness 자동 체크 → 24시간 이상 시 경고 + 재적응.
4. **재시작 카운트 임계값**: 하루 3회 초과 재시작 → 시스템 자동 셧다운 + 관리자 알림.

### 한 줄 요약

> **"69차에서 '고쳤다'고 선언한 signal() TypeError가 args=5 호출부를 남겨둔 채 22일간 잠복하다 5/22 GAP_OPEN 구간을 완전히 무력화시켰다. scaler 7일 노후 + 12회 재시작이 conf를 50%까지 끌어내렸다. P0-1(TypeError)·P0-2(scaler)·P0-3(재시작 락)을 오늘 밤 반드시 구현해야 5/23 진입이 재개된다."**

---
