# 2026-05-22 미륵이 진입 0건 종합 리뷰

> 작성일: 2026-05-22  
> 작성자: Codex  
> 분석 범위: `logs/20260522_{SIGNAL,SYSTEM,WARN,TRADE,LEARNING,DEBUG}.log`, `dev_memory/*`, 최근 git 이력(`69차~85차`), 기존 리뷰 문서  
> 저장 목적: 5/22 `진입 0`의 직접 원인, 재발 원인, 환경 제약을 반영한 실행 방안, 중장기 학술적 개선안 정리

---

## 1. 결론 요약

5/22 미륵이는 단순히 "신뢰도가 조금 부족해서" 진입 0이 된 것이 아니다. 실제로는 아래 네 층이 동시에 겹쳤다.

1. **치명적 런타임 결함**
   - `2026-05-22 09:10:00 ~ 09:23:00` 구간에 `signal() takes from 2 to 3 positional arguments but 5 were given`가 분봉마다 재발했다.
   - `WARN.log` traceback 기준 발생 위치는 `main.py:2769`.
   - 69차(`ae83ef8`)에서 같은 계열 문제를 "근본 수정"했다고 기록했지만, 호출 규약이 다른 잔존 경로가 남아 있었다.

2. **앙상블 confidence 붕괴**
   - 5/22 `SIGNAL.log`에서 앙상블 confidence는 대체로 `34%~50%`에 머물렀다.
   - 최고치는 `13:14`의 `50.1%`였고, 시간대별 min_conf를 끝내 넘지 못했다.
   - 5/21 최고치 `57.1%`보다 더 악화됐다.

3. **재시작 루프와 학습 연속성 파괴**
   - `08:45, 08:48, 09:23, 09:58, 12:11, 13:04, 13:05, 13:23, 14:42, 14:53, 15:24, 15:55`에 걸친 다수 재시작이 관측된다.
   - 공통 패턴은 `BrokerSync rows=0` + `97007 모의투자 데이터가 없습니다`.
   - 재시작마다 `OnlineLearner`, 정확도 버퍼, 신호 이력, 장중 적응 상태가 실질적으로 리셋된다.

4. **CORE 3종 게이트 상시 탈락**
   - AGENTS 규칙상 변경 불가인 `VWAP/CVD/OFI`가 체크리스트에서 반복적으로 탈락했다.
   - 10:00 이후에는 `CORE 피처 ✗ ['4_cvd', '5_ofi']`, `['3_vwap', '4_cvd', '5_ofi']`가 장시간 반복된다.
   - 즉, 모델 confidence가 낮은 데다 진입 체크리스트의 핵심 근거도 비활성 상태였다.

핵심 한 줄 요약:

> **5/22 진입 0은 "모델 약화" 하나의 문제가 아니라, 런타임 예외 재발 + 재시작 루프 + stale scaler/재학습 품질 저하 + CORE 피처 불합격이 동시 중첩된 시스템성 실패다.**

---

## 2. 5/22 실로그 기반 직접 원인

### 2.1 치명적 원인 1: 09:10~09:23 분봉 파이프라인 FATAL 재발

`logs/20260522_WARN.log`:

```text
09:10:00 [ERR-FATAL] minute_pipeline: signal() takes from 2 to 3 positional arguments but 5 were given
...
File "main.py", line 2769, in run_minute_pipeline
  self.current_intraday_regime, _l2_mc_adj * 100, actual_min_conf,
TypeError: signal() takes from 2 to 3 positional arguments but 5 were given
```

이 구간은 장 초반 핵심 시간대다. 진입 기회가 가장 많은 구간에서 파이프라인이 연속 예외를 맞았고, 이는 단순 경고가 아니라 `ERR-FATAL`이다.

중요한 점은 이번 문제가 "전략 signal"이 아니라 **로깅 인터페이스 `log_manager.signal(...)` 호출 규약 불일치 재발**로 보인다는 점이다.  
69차 수정은 `msg, "WARNING"` 형태를 `msg, level="WARNING"`으로 바꿨지만, 5/22 traceback은 여전히 다중 인자 호출이 남아 있음을 보여준다.

즉, 재발 구조는 다음과 같다.

- 인터페이스 계약 자체를 통일하지 않았다.
- 호출부 전체 전수검사를 하지 않았다.
- 특정 재현 경로만 수정하고 종료했다.

이것이 "고쳤는데 또 터진" 첫 번째 명확한 원인이다.

### 2.2 직접 원인 2: 앙상블 confidence 상한 자체가 낮음

`logs/20260522_SIGNAL.log` 기준 주요 구간:

- `09:00~09:05`: `40.0%` 전후, `GAP_OPEN min_conf=67%` 완전 미달
- `09:05~10:30`: `39%~42%`, `OPEN_VOLATILE min_conf=60%` 미달
- `10:30~11:50`: `36%~43.3%`, `STABLE_TREND min_conf=58%` 미달
- `11:50~13:00`: `38%~47.5%`, `OTHER min_conf=65%` 미달
- `13:00~14:00`: `40%~50.1%`, `LUNCH_RECOVERY min_conf=60%` 미달

5/21의 문제는 "57.1%까지는 나왔는데 58%에 못 닿았다"였다.  
5/22는 그보다 더 나빠져서 **상한이 50.1%**였다.

즉 5/22는 threshold 미세조정만으로 해결될 상황이 아니었다.  
신호 생성층에서 이미 정보력이 붕괴한 상태였다.

### 2.3 직접 원인 3: Checklist A와 Ensemble X의 계층 불일치

`SIGNAL.log`에서 반복적으로 다음 패턴이 나온다.

```text
10:24:01 [Ensemble] dir=+1 conf=39.5% grade=X
10:24:01 [Checklist] 통과 8/9 → 등급 A
```

동일 패턴은 `10:31`, `10:48`, `10:55`, `11:07` 등에서도 보인다.

이것이 뜻하는 바:

- 체크리스트는 구조적으로 진입 찬성이다.
- 하지만 앙상블 등급은 계속 `X`다.
- 즉, "시장 미확신"과 "구조적 진입 조건 충족"이 분리되어 서로 다른 레이어가 충돌한다.

이 현상은 운영적으로 매우 중요하다.  
왜냐하면 미륵이는 단순히 "체크리스트가 너무 빡빡해서" 못 들어간 것이 아니고, **확률 모델 레이어가 먼저 죽어 있기 때문**이다.

### 2.4 직접 원인 4: CORE 3종 불합격 지속

`SIGNAL.log`:

- `10:00`: `CORE 피처 ✗ ['4_cvd', '5_ofi']`
- `10:04`: `CORE 피처 ✗ ['3_vwap', '4_cvd', '5_ofi']`
- `12:33`: `CORE 피처 ✗ ['3_vwap', '4_cvd', '5_ofi']`
- `13:06`: `CORE 피처 ✗ ['3_vwap', '4_cvd', '5_ofi']`

AGENTS/CLAUDE 규칙상 이 세 피처는 직접 손대기 어렵다. 따라서 해석은 두 갈래다.

1. 피처 연산은 맞는데 입력 데이터 품질이 나쁘다.
2. 피처는 살아 있지만 체크리스트 문턱이 현 시장에서 과도하다.

5/22에서는 둘 다 가능성이 있다.  
다만 재시작 루프, BrokerSync 불안정, z-score 폭증을 함께 보면 **입력 데이터 품질/상태 연속성 문제의 비중이 더 크다**고 보는 것이 합리적이다.

---

## 3. 5/22를 더 악화시킨 구조적 배경

### 3.1 BrokerSync는 "flat으로 해석"했는데 시스템은 계속 재시작함

`SYSTEM/WARN.log`에는 반복적으로 다음이 보인다.

- `block_new_entries=False`
- `blank/no holdings response interpreted as flat`
- 그 직후 또 재시작

이 말은, 설계상으로는 "빈 응답이면 flat으로 보고 계속 가자"가 이미 들어가 있는데, 실제 운영 흐름에서는 여전히 **재시작 트리거가 우세**하다는 뜻이다.

즉, 과거에 "startup flat placeholder" 문제를 완화했지만, 운영 경로의 다른 곳에서 여전히 재시작을 유도한다.  
이 역시 "한 경로 수정, 전체 상태기계 미통합"의 반복이다.

### 3.2 재학습은 자주 돌지만 품질은 개선되지 않음

`logs/20260522_LEARNING.log`:

- `08:55` 재학습 시작, `361.3초`
- `09:23` 재학습 시작, `370.8초`
- `09:58` 재학습 시작, `366.0초`
- `12:11` 재학습 시작, `373.2초`
- `13:04`, `13:05`, `13:23`에도 반복

문제는 재학습 자체가 아니라 **재학습 품질과 효율**이다.

- cutoff가 `2026-03-27`
- 사용 데이터는 `4976~5238행`
- 5/22 현재와는 괴리가 큰 과거 분포
- 새 모델 acc도 다수 구간에서 `0.31~0.39`

즉,

- 재학습은 무겁고 오래 걸린다.
- 그런데 최신 장세 적응은 약하다.
- 재시작이 많아질수록 학습/예측 품질보다 오버헤드만 커진다.

### 3.3 S2 병목이 상시 존재

`WARN.log`의 `PipePerf`:

- `09:00 total=2639ms | S2=2364ms`
- `10:35 total=2945ms | S2=2758ms`
- `14:04 total=3963ms | S2=3803ms`

결론은 분명하다.

- 분봉 파이프라인에서 S2가 주된 병목이다.
- 5/21 리뷰에서 이미 S2 최적화가 제안되었지만 미구현 상태였다.
- 병목이 남아 있으니 CB5 경고는 계속 누적되고, 지연 상태에서 적응학습까지 불안정해진다.

---

## 4. git + dev_memory 기준 "왜 개선이 재발했는가"

아래는 5/19~5/22 주요 흐름 요약이다.

- `67f974e` / 85차: 1m/5m FL 편향, CLOSE_VOLATILE 가중치, Platt window, 10m 하한
- `39bea37` / 84차: 30m FL 완화, ACCURACY_WINDOW, bias buffer, ensemble calibrator
- `7402148` / 83차: exhaustion ATR 문턱 재설계
- `86ad249` / 81차: DirectionalStuckBreaker
- `ae83ef8` / 69차: `signal()` TypeError 수정 주장

`dev_memory/SESSION_LOG.md`, `DECISION_LOG.md`, `NEXT_TODO.md`를 같이 보면 반복되는 패턴이 있다.

### 4.1 패턴 A: 이상점 deep dive는 빠른데, 기반 문제는 늦다

최근 작업의 강점:

- 로그 이상점을 매우 빠르게 잡아낸다.
- FL 편향, calibration 과압축, intraday regime dead code 같은 구조 문제를 잘 찾는다.

최근 작업의 약점:

- 재시작 방지
- scaler stale 처리
- 전체 호출부 인터페이스 검증
- S2 성능 최적화

같은 **기반 안정성 문제**는 여러 차수에 걸쳐 "계획"으로만 남는다.

### 4.2 패턴 B: 한 버그를 "한 경로"만 수정한다

69차 사례가 대표적이다.

- monkey patch 수집기 `_Collector.signal()` 시그니처 보강
- 일부 `log_manager.signal(..., "WARNING")`를 keyword 인자로 변경

하지만 5/22는 다른 다중 인자 호출이 남아 있었다.

즉, 원인이 "특정 한 줄"이 아니라

- `signal` 인터페이스 계약이 느슨하고
- 호출부가 프로젝트 전역에 퍼져 있고
- 이를 전수 검증하는 안전장치가 없는 것

인데, 수정은 국소적으로만 했다.

### 4.3 패턴 C: threshold/weight 수정이 상위 원인을 가린다

84차, 85차는 모두 의미 있는 개선이다.  
하지만 5/22 실세션을 보면 더 상위 원인이 있었다.

- 재시작 루프
- 런타임 FATAL
- stale training cutoff
- CORE 입력 품질 저하

이 상태에서는 class weight나 calibration tuning이 효과를 내더라도, 시스템 전체 성능 개선으로 연결되기 어렵다.

즉, **"정교한 미세 조정"이 "기초 체력 붕괴"를 덮고 있었다.**

### 4.4 패턴 D: 운영 지표가 재시작 오염을 반영하지 못한다

`DEBUG.log`에서 `acc30m`은 장중 일부 시점에 `0.0% → 100.0% → 0.0%`처럼 급변한다.

이는 실제 시장 적합도 변화라기보다,

- 재시작으로 표본 수가 초기화되거나
- 유효 샘플이 매우 적은 상태에서 비율만 출렁이거나
- 세션 경계가 끊긴 결과

일 가능성이 높다.

따라서 Contrarian, ShadowSession, CB accuracy 류 진단은 5/22에 **부분적으로 오염된 지표**일 수 있다.  
이 점을 반영하지 않고 "acc30m가 0이니 반대로만 가자" 식으로 해석하면 또 다른 오판이 된다.

---

## 5. 5/22 문제를 미륵이 환경에 맞게 재정의하면

미륵이는 일반적인 서버형 ML 트레이딩 시스템이 아니다.

- Python 3.7 32-bit
- Windows COM/OCX
- Cybos 실시간 의존
- PyQt 이벤트 루프
- 테스트 프레임워크 부재
- CORE 3종 피처 변경 금지

따라서 해결책도 "최신 아키텍처로 재구축"이 아니라 아래 원칙을 따라야 한다.

1. **콜백 안정성 우선**
   - COM/Qt 안전 규칙 위반 금지
   - 런타임 예외 제거가 최우선

2. **입력 연속성 우선**
   - 재시작 억제
   - BrokerSync 실패와 진입 엔진 중단을 분리

3. **stale 적응 우선**
   - scaler/학습 분포를 최신화
   - 다만 CORE 3종 수식 자체는 건드리지 않음

4. **진단 가능성 우선**
   - 무엇이 탈락했는지보다 왜 탈락했는지 남겨야 함

---

## 6. 실행 방안

## 6.1 즉시 우선순위 P0

### P0-1. `log_manager.signal` 호출 규약 전수 정리

목표:

- 5/22 FATAL 재발을 완전히 차단

방법:

- `main.py`, `strategy/*`, `safety/*`, `learning/*` 전역에서 `log_manager.signal(` 호출부를 grep
- `msg` 외 추가 값 전달은 모두 f-string으로 1개 문자열로 접기
- `level`은 오직 keyword로만 전달
- 가능하면 logger facade에 `*args` 금지 가드 추가

이 조치는 효과 대비 비용이 가장 높다.  
이 문제를 남긴 채 다른 개선을 해도 장 초반에 또 무너질 수 있다.

### P0-2. 재시작 락 또는 backoff 도입

목표:

- `rows=0` 같은 일시 문제로 장중 상태를 계속 초기화하지 않기

방법:

- `최근 N초 내 재시작 금지`
- `BrokerSync rows=0`는 즉시 재시작 대신 `degraded/flat-shadow` 상태로 유지
- 재연결/재조회는 backoff로 처리

핵심은 "연결 품질 저하"와 "프로세스 재시작"을 분리하는 것이다.

### P0-3. CORE 피처 탈락 진단 로그 추가

목표:

- `3_vwap`, `4_cvd`, `5_ofi`가 왜 떨어지는지 가시화

방법:

- 체크리스트에서 `False`만 찍지 말고
- 해당 피처의 원시값, 정규화값, threshold, 보조 상태를 함께 로깅

CORE 3종은 직접 변경 금지이므로, 더더욱 **진단 투명성**이 필요하다.

### P0-4. S2 병목 축소

목표:

- `PipePerf` 경고 상시화 해소

방법:

- OnlineLearner `partial_fit` 호출 수를 배치화
- 조정 주기를 틱당 다회 호출이 아니라 분봉당 1회 수준으로 제한
- 장중 heavy retrain과 online update가 겹칠 때 우선순위 조정

---

## 6.2 단기 구조 개선 P1

### P1-1. stale scaler 적응

권장 방식:

- 기동 시 최근 N일 raw feature로 scaler refresh 또는 rolling refit
- 최소한 stale age를 기록하고 경고

중요:

- CORE 피처 수식을 바꾸는 것이 아니라
- **정규화기와 feature distribution alignment**를 최신화하는 작업이다

5/22에서는 `mlofi_slope`, `queue_signal`, `queue_signal_ma` 등이 반복적으로 extreme z-score를 냈다.  
이는 수식 자체보다 **현재 분포와 scaler 기준의 괴리** 가능성이 더 크다.

### P1-2. 동적 min_conf

5/21식 "57.1% vs 58%" 상황뿐 아니라, 5/22식 40~50%대 붕괴에도 대응하려면 고정 threshold만으로는 부족하다.

권장:

- 시간대 기본 min_conf는 유지
- 다만 최근 롤링 confidence 분포와 calibration 품질을 함께 반영
- 예: `max(lower_bound, min(static_base, recent_p75_or_p80))`

단, 5/22처럼 시스템이 고장 난 날에는 threshold만 낮추는 것은 위험하다.  
따라서 동적 min_conf는 반드시 아래와 결합해야 한다.

- 런타임 건강도
- restart count
- CORE 피처 상태
- stale z-score 정도

즉, **confidence 기반 진입 문턱을 낮추되, 시스템 건강도가 나쁜 날은 오히려 더 보수적으로 가야 한다.**

### P1-3. BrokerSync와 진입 가능 상태 분리

현재는 "잔고 조회 불안정"이 너무 쉽게 "세션 전체 재가동"으로 번진다.

권장 상태기계:

1. `healthy`
2. `broker_degraded`
3. `signal_degraded`
4. `no_new_entries_but_keep_pipeline`
5. `fatal_restart_required`

5/22의 다수 상황은 사실 `fatal_restart_required`가 아니라  
`no_new_entries_but_keep_pipeline` 또는 `broker_degraded`에 가까웠다.

### P1-4. retrain 정책 정리

현재 문제:

- 장중 재시작마다 6분 이상 재학습 반복
- cutoff는 오래된 과거
- 최신 적응은 약함

권장:

- pre-open retrain은 유지
- 장중 재시작 시 full retrain 자동 재실행은 제한
- incremental refresh와 full retrain을 분리

---

## 6.3 학술적·고급 방법론 P2

아래 방법은 미륵이 환경에 맞게 "가볍고 점진적으로" 도입해야 한다.

### P2-1. Regime-Conditional Thresholding

아이디어:

- 동일 confidence라도 레짐별 실제 hit-rate가 다르다.
- 따라서 min_conf를 고정값이 아니라 `(레짐, 시간대, 최근 calibration quality)` 조건부로 산정한다.

미륵이에 맞는 형태:

- `NEUTRAL + CORE 3종 중 2개 이하 정상 + z_warn>k`면 threshold 강화
- `TREND + TrendGate active + calibration stable`이면 threshold 완화

즉, 단순 확률값이 아니라 **시장상태 조건부 의사결정**으로 바꾸는 것이다.

### P2-2. Sequential Probability Ratio Test, SPRT

아이디어:

- 한 분봉 단위 confidence만 보지 않고
- 연속된 증거 누적으로 진입 여부를 판단

미륵이에 적합한 이유:

- 1분마다 noisy signal이 흔들릴 때 즉시 진입보다 안정적
- TrendGate, Contrarian, Layer2와도 결합 가능

주의:

- 구현은 가볍게 해야 하며 COM/Qt 콜백 흐름을 방해하면 안 된다.
- 순수 상태 누적 객체로 두고, 분봉 파이프라인에서만 업데이트하는 것이 안전하다.

### P2-3. Bayesian / Beta-Binomial Calibration

Platt는 충분한 샘플이 쌓이기 전 불안정할 수 있다.  
미륵이처럼 세션이 자주 끊기는 환경에서는 베이지안 완화가 유리하다.

기대 효과:

- 적은 표본에서도 과신 완화
- `acc30m` 같은 지표가 샘플 수에 따라 요동치는 문제를 완화

### P2-4. Hidden-State / State-Space 접근

직접 HMM을 크게 넣기보다, 미륵이에서는 경량 latent-state 개념만 도입해도 효과가 있다.

예:

- `signal_quality_state = {stable, stale, broken}`
- 관측치는 `restart_count`, `z_warn`, `pipe_latency`, `core_pass_count`, `broker_sync_health`

즉 "시장 상태"와 별도로 **시스템 상태 은닉 레짐**을 두는 것이다.  
5/22는 시장보다 시스템이 더 나빴다. 이 둘을 같은 레짐으로 다루면 항상 해석이 꼬인다.

### P2-5. Conformal or Reliability-Aware Abstention

진입 0을 무조건 나쁘게 보면 안 된다.  
다만 5/22는 "정상적 보수성"이 아니라 "고장 때문에 못 들어간 abstention"이었다.

따라서 향후에는 abstention을 두 종류로 분리해야 한다.

1. `informative abstention`
   - 모델이 정직하게 확신이 없음

2. `pathological abstention`
   - 시스템 오류, stale scaler, input degradation 때문에 확률이 의미 없음

이 구분은 실전 운영에서 매우 중요하다.

---

## 7. 재발 방지 프로세스 제안

### 7.1 `MUST-BEFORE-NEXT-RUN` 태그 도입

`NEXT_TODO.md`에 아래 종류를 분리해야 한다.

- `MUST-BEFORE-NEXT-RUN`
- `SHOULD-THIS-WEEK`
- `RND-LATER`

5/21 리뷰에서 제안된 핵심 안정화 과제들이 5/22 실세션 전까지 구현되지 않았고, 대신 더 세밀한 이상점 개선이 먼저 들어갔다.  
앞으로는 런타임 안정성 항목을 최상위 강제 우선순위로 묶어야 한다.

### 7.2 인터페이스 전수검사 스크립트

특히 `log_manager.signal/system`, `dashboard.*`, `broker.*` 같은 넓게 쓰이는 인터페이스는

- 호출 시그니처
- keyword 사용 규칙
- positional 인자 금지

를 정적 grep 수준으로라도 체크해야 한다.

테스트 프레임워크가 없기 때문에 이런 정적 점검이 더 중요하다.

### 7.3 세션 연속성 지표를 별도 관리

필수 로그:

- restart_count_today
- time_since_last_restart
- valid_acc30m_sample_count
- calibrator_sample_count
- core_feature_health_count

이 값이 낮거나 불안정하면 `acc30m`, `Contrarian`, `ShadowSession` 해석에 경고를 붙여야 한다.

---

## 8. 최종 종합 방안

### 종합 판단

5/22의 진입 0은 다음 우선순위로 해석해야 한다.

1. **가장 먼저 런타임 FATAL과 재시작 루프를 제거**
2. **그 다음 입력/정규화 연속성(stale scaler, CORE 입력 품질) 복구**
3. **그 다음 confidence 구조(min_conf, calibration, class weight) 미세조정**
4. **그 후에야 고급 연구형 개선(SPRT, Bayesian calibration, conditional thresholding) 도입**

최근 세션들은 3, 4번을 열심히 하고 있었고, 1, 2번이 상대적으로 늦었다.  
그래서 개선이 "맞는 방향인데 효과가 누적되지 않는" 상황이 반복됐다.

### 실전형 실행 순서

1. `signal()`/로깅 호출 규약 전수 정리
2. 재시작 backoff/락 도입
3. CORE 피처 진단 로그 강화
4. OnlineLearner S2 병목 완화
5. scaler stale 감시 및 refresh
6. BrokerSync degraded 상태기계 분리
7. 이후 동적 min_conf, Bayesian calibration, SPRT 순으로 연구 도입

### 최종 한 줄

> **5/22의 실패는 "모델이 못 맞췄다"가 아니라 "불안정한 시스템 위에서 모델 미세조정을 반복한 결과, 런타임·연속성·입력 품질 문제가 다시 전면화된 날"이었다. 다음 개선은 반드시 안정성 우선으로 재정렬되어야 한다.**

---

## 9. 참고한 내부 자료

- `logs/20260522_WARN.log`
- `logs/20260522_SIGNAL.log`
- `logs/20260522_TRADE.log`
- `logs/20260522_LEARNING.log`
- `logs/20260522_DEBUG.log`
- `dev_memory/CURRENT_STATE.md`
- `dev_memory/NEXT_TODO.md`
- `dev_memory/SESSION_LOG.md`
- `dev_memory/DECISION_LOG.md`
- `dev_memory/trade_review/Deep_SESSION_20260521_trade진입0_REVIEW.md`
- `dev_memory/trade_review/Deep_SESSION_20260522_trade진입0_REVIEW.md`
- git commits: `ae83ef8`, `86ad249`, `39bea37`, `67f974e`, `cf81537`
