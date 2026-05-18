# 📊 2026-05-18 미륵이 로그 종합 분석

> 분석일시: 2026-05-18
> 분석 도구: openCode
> 데이터 소스: trades.db, predictions.db, SESSION_LOG.md, DECISION_LOG.md

---

## 1. 거래 요약

| # | 진입시각 | 청산시각 | 방향 | 계약 | 진입가 | 청산가 | PnL(pt) | PnL(원) | 결과 | 사유 |
|---|----------|----------|------|------|--------|--------|---------|---------|------|------|
| 1 | 09:24 | 09:52 | LONG | 1 | 1131.93 | 1139.22 | +7.29 | +362,902 | ✅ | 외부체결(HTS/수동) |
| 2 | 09:24 | 09:56 | LONG | 2 | 1131.93 | 1146.09 | +14.16 | +1,412,804 | ✅ | TP3(전량) |
| 3 | 09:59 | 10:00 | LONG | 1 | 1151.49 | 1156.92 | +5.44 | +270,023 | ✅ | TP1 부분청산 33% |
| 4 | 09:59 | 10:01 | LONG | 1 | 1151.49 | 1160.18 | +8.70 | +433,023 | ✅ | TP2 부분청산 33% |
| 5 | 09:59 | 10:04 | LONG | 2 | 1151.49 | 1154.91 | +3.43 | +339,046 | ✅ | 하드스톱 (수익구간) |
| 6 | 10:12 | 10:15 | LONG | 1 | 1158.85 | 1147.88 | -10.97 | -549,988 | ❌ | 외부체결(HTS/수동) |
| 7 | 10:29 | 10:33 | LONG | 2 | 1157.82 | 1162.79 | +4.97 | +493,887 | ✅ | TP1 부분청산 33% |
| 8 | 10:29 | 10:38 | LONG | 5 | 1157.82 | 1156.95 | -0.87 | -225,784 | ❌ | 하드스톱 |
| 9 | 11:07 | 11:13 | LONG | 1 | 1173.02 | 1177.66 | +4.64 | +230,240 | ✅ | TP1 부분청산 33% |
| 10 | 11:07 | 11:14 | LONG | 1 | 1173.02 | 1179.20 | +6.18 | +307,240 | ✅ | TP2(전량) |
| 11 | 11:17 | 11:22 | LONG | 2 | 1181.21 | 1184.66 | +3.45 | +341,786 | ✅ | TP1 부분청산 33% |
| 12 | 11:17 | 11:23 | LONG | 2 | 1181.21 | 1187.41 | +6.20 | +616,786 | ✅ | TP2 부분청산 33% |
| 13 | 11:17 | 11:25 | LONG | 2 | 1181.21 | 1190.25 | +9.04 | +900,786 | ✅ | TP3(전량) |

> **일간 순이익: +4,932,751원** (13건 중 11승 2패, 승률 84.6%, 총 99.46pt)

### 진입 그룹별 집계

| 진입그룹 | 진입시각 | 계약 | 구성 | 총 PnL | 결과 |
|----------|----------|------|------|--------|------|
| 진입① | 09:24 | 5계약 | TP1 외부청산(1) + TP3(2) + stuck 해소(2) | +1,775,706 | 혼합 (stuck 이슈) |
| 진입② | 09:59 | 4계약 | TP1(1) + TP2(1) + 하드스톱(2) | +1,042,092 | ✅ TP시퀀스 정상 |
| 진입③ | 10:12 | 1계약 | 외부청산(1) | -549,988 | ❌ 브로커 잔여물 |
| 진입④ | 10:29 | 7계약 | TP1(2) + 하드스톱(5) | +268,103 | 혼합 (잔여물 오염) |
| 진입⑤ | 11:07 | 2계약 | TP1(1) + TP2 전량(1) | +537,480 | ✅ (ProfitGuard 무력화) |
| 진입⑥ | 11:17 | 6계약 | TP1(2) + TP2(2) + TP3(2) | +1,859,358 | ✅ 완벽 TP시퀀스 |

---

## 2. 진입지점 이상점

### 🔴 이상점 A: 브로커 잔여물 오염 — 의도치 않은 포지션 확대 (10:12, 10:29)

| 시각 | 상황 | 결과 |
|------|------|------|
| **10:12** | 앙상블 `grade=X, conf=0.495, meta=skip` → 진입 불가 판정. 그러나 trades.db에 A등급 LONG 1계약이 `외부체결(HTS/수동)`으로 기록됨 | -549,988원 (당일 최대 손실) |
| **10:29** | 시스템 의도 4계약 진입 → 브로커 sync 후 잔여 3계약 포함 → **7계약**으로 진입 | 의도치 않은 3계약 초과 리스크 |

**원인**: B106-B108 수정(51차) 이전에는 TP 청산 중 Chejan 콜백이 `pending=None` 상태로 external fill 오탐 → 계약 불일치 누적. 09:24 stuck 해소 과정에서 남은 잔여물이 반대 포지션으로 전환.

**앙상블 신호 검증**:
```
10:12 ensemble: dir=+1, conf=0.4949, grade=X, auto=0, meta=skip, meta_confidence=0.308
```
→ 자동화 시스템은 절대 진입하지 않았을 시점. 100% 수동/잔여물 개입.

### 🔴 이상점 B: ProfitGuard 재시작 소멸 (B113, 10:38→10:57)

```
10:38  ProfitGuard-L4 발동: 연속 2회 손실 → 당일 진입 중단 선언
10:57  시스템 재시작 → _profit_guard_blocked 메모리 소멸
       session_state.json에 ProfitGuard 상태 미저장
11:07  LONG 2계약 @ 1173.02 진입 허용 (ProfitGuard 무력화)
```

**비고**: 11:07→11:14 수익 시퀀스(+537,480원)로 결과는 좋았으나, 만약 CB가 필요한 손실 구간이었다면 규칙 위반으로 이어졌을 치명적 설계 결함.

### 🟡 이상점 C: 앙상블 vs 메타게이트 판단 충돌 (10:29)

동일 진입 그룹 내에서 앙상블과 메타게이트 의견이 **정반대**였던 유일한 사례:

| 신호 | 앙상블 | 메타게이트 | 결과 |
|------|--------|-----------|------|
| 09:59 | conf=0.92, grade=A, auto=1 | meta=take, mconf=0.67 | ✅ 대성공 (+17.56pt) |
| **10:29** | **conf=0.61, grade=B, auto=1** | **meta=skip, mconf=0.45** | ❌ 하드스톱 (-0.87pt×5) |
| 11:07 | conf=0.64, grade=B, auto=1 | meta=take, mconf=0.79 | ✅ 성공 (+10.82pt) |
| 11:17 | conf=0.87, grade=A, auto=1 | meta=take, mconf=0.89 | ✅ 대성공 (+18.70pt) |

> **발견**: 앙상블과 메타게이트가 일치할 때(take+take or skip+skip) 100% 수익. 불일치 시(ensemble=take, meta=skip) → 손실. 메타게이트 의견을 무시하고 ensemble auto_entry=True만으로 진입한 것이 10:29 손실의 근본 원인.

### 🟡 이상점 D: Hurst 전반부 fallback (09:00~10:34)

- 10:34까지 `hurst=0.500` 고정 (60봉 버퍼 미충족 → dead code 상태였던 50차 이전)
- 10:35부터 실측 `hurst=0.122~0.143` (강한 평균회귀) → 후반부만 실값 사용
- 50차(B105) 수정이 5/17 커밋 → 5/18 **실행 중 프로세스에 미반영**. 5/19가 첫 실적용

### 🟡 이상점 E: 모든 등급이 GRADE=A

13건 전체가 `grade=A`. 등급 분포가 단일화되어 있어 등급별 차등 진입(size_mult, staged_entry)이 전혀 작동하지 않음. Grade B/C가 없으면 리스크 차등화의 의미가 퇴색된다.

---

## 3. 청산지점 이상점

### 🔴 이상점 F: 09:24 진입 — TP2/TP3 23분간 stuck (09:27~09:50)

| 시각 | 이벤트 |
|------|--------|
| 09:24 | LONG 5계약 진입 @ 1131.74 (A등급) |
| 09:26 | TP1 +7.25pt 정상 체결 (+360,902원) |
| 09:27~09:50 | **23분간 stuck** — 매분 broker sync 경고 반복, TP2/TP3 미발동 |
| 09:51~09:56 | 재시작 후 수동 청산으로 해소 |

**원인**:
1. 53차(B110:B111) IntrabarTPCheck 코드가 10:51 커밋 → 실행 중 미반영
2. initial_quantity=5, stage_plan=(2,1,2) → TP1 2계약 주문 → **1계약만 체결(partial fill)** → pending stuck
3. pending EXIT_PARTIAL 상태에서 TP2·TP3 체크 불가 → 1분 주기 파이프라인에서만 재점검 → 가격이 이미 TP3 위여도 대기

### 🔴 이상점 G: TP 청산 시 계약 수 불일치 — partial fill cascade

- **09:24** 진입: 5계약 → TP1 2계약 주문 → 1계약 체결 → pending stuck → 09:52/09:56 수동/TP3 혼합
- **10:29** 진입: 7계약(의도4+잔여3) → TP1 2계약 체결 → 잔여 5계약 전부 하드스톱. TP2 발동 기회조차 없었음

> 전형적인 Chejan partial fill race condition (B106/B108). 51차 수정이 10:51 커밋으로 당일 미적용.

### 🟡 이상점 H: 외부청산(HTS/수동) 2회 발생

- ID=1 (09:52): stuck 해소 과정에서 수동 개입
- ID=6 (10:15): 브로커 잔여물 수동 청산

> 자동화 신뢰도 저하 징후. stuck과 잔여물이 없었다면 수동 개입은 불필요했을 것.

---

## 4. 성공/실패 원인 분석

### ✅ 성공 요인

| 요인 | 세부 내용 | 영향도 |
|------|-----------|--------|
| **고신뢰도 추세 동조** | 09:59(conf=0.92), 11:17(conf=0.87) — 전 호라이즌(1m~30m) LONG 방향 일치 + meta=take | 매우 높음 |
| **TP3 전량 달성 3회** | 09:56(+14.16pt), 11:14(+6.18pt), 11:25(+9.04pt) — 3단계 이익실현 설계 효과적 | 높음 |
| **meta=take + ensemble=take 일치** | 공명 시 100% 승률 (3회 진입, 8건 청산 모두 수익) | 높음 |
| **ATR 기반 TP 설계** | 추세 확장 시 TP3까지 여유 있게 도달. 11:17 진입 +18.70pt 기록 | 중간 |
| **CORE 3 게이트 통과** | checklist.py D99 수정(5/17)으로 CORE 3 중 하나라도 ✗ 시 X등급 → 이날 진입 모두 CORE 3 통과 | 중간 |

### ❌ 실패 요인

| 요인 | 세부 내용 | 영향도 |
|------|-----------|--------|
| **B106/B108 Race Condition** | pending 등록 순서 역전 + Chejan 방향 오탐 → partial fill stuck → TP 지연·계약 불일치 | 매우 높음 |
| **IntrabarTPCheck 부재** | 53차 수정(10:51 커밋)이 실행 중 미반영 → stuck 케이스에서 최대 1분 대기 강제 | 매우 높음 |
| **브로커 sync 잔여물** | 09:24 stuck 해소 과정에서 남은 미체결이 반대 포지션으로 전환 → ID=6 -55만원 손실 | 높음 |
| **ProfitGuard 미영속화** | 재시작 시 CB 방어벽 붕괴 → B113 심각한 설계 결함 | 높음 |
| **meta=skip 무시** | 10:29 진입: ensemble은 grade B auto=1, meta는 skip(mconf=0.45). meta 의견 무시하고 진입 → 손실 | 높음 |
| **Hurst 전반부 fallback** | 35분간 허스트 실측 불가(50차 미적용) → 추세/평균회귀 판단 무력화 | 중간 |
| **48차~53차 코드 미적용** | 10:51 이전 커밋분이 실행 중 프로세스에 미반영 → stuck·partial fill 관련 수정 무효 | 중간 |

---

## 5. 개선 제안

### 🔧 즉시 적용 필요 (이미 식별된 버그 수정)

| # | 내용 | 관련 버그 | 상태 |
|---|------|----------|------|
| 1 | **ProfitGuard 상태 영속화** — `session_state.json`에 L4 상태(day_stop, consecutive_loss) 저장, 재시작 시 복원 | B113 | NEXT_TODO |
| 2 | **IntrabarTPCheck 작동 검증** — 5/19 실세션에서 B114 진단 로그 확인 후 실제 수정 | B114 | 진단 대기 |
| 3 | **stale broker_sync_reason 초기화** — FLAT 전환 시 `"flat after exit"` 덮어쓰기 | B112 | 커밋 완료 |
| 4 | **MIN_TRAIN_BARS 3000→5000 복원** — 5/26경 raw_data.db 5,000행 돌파 예상 시점 | D101 | 모니터링 |

### 💡 기발한 개선 아이디어

#### 아이디어 5: "Ghost Position Detector" — 미아 포지션 자동 청산

**문제**: 09:24 진입이 32분간 stuck → TP2/TP3 전혀 미발동
**해결**: 포지션 오픈 후 15분간 TP가 단 한 번도 발동하지 않으면 **강제 전량 청산**

```
if time_since_entry > 900 and not any([partial_1_done, partial_2_done]):
    logger.warning("[Ghost] 15분간 TP 미발동 → 강제 청산")
    force_exit(price, reason="GHOST_TIMEOUT")
```

- 하루 Ghost 발동 1회 허용, 2회 시 당일 진입 금지
- partial fill로 인한 pending stuck이 청산 지연으로 이어지는 최악 시나리오 방지
- 구현 위치: `strategy/position/position_tracker.py` 또는 `main.py` run_minute_pipeline

#### 아이디어 6: "Resonance Score" — 앙상블×메타게이트 공명도 기반 진입 결정

**문제**: 10:29 진입에서 ensemble=enter, meta=skip 충돌 → 손실. 모든 공명 케이스에서 100% 승률
**해결**: meta_action이 "skip"이면 ensemble grade·confidence와 무관하게 진입 금지

```python
if meta_action == "skip":
    logger.warning(f"[Resonance] meta=skip → 진입 금지 (ensemble={ensemble_confidence:.2f})")
    return grade_X, block_entry
elif meta_action == "reduce":
    size_mult *= 0.5  # meta가 망설이면 규모 축소
```

- 데이터 기반: 5/18 meta=skip에서 진입 시 100% 손실 (1/1). meta=take에서 진입 시 100% 수익 (3/3)
- 구현 위치: `strategy/ops/verdict_engine.py` 또는 `strategy/entry/meta_gate.py`

#### 아이디어 7: "1m Lead Signal Filter" — 1분봉 선행 방향 필터

**문제**: 5/15~5/18 공통 — 전호라이즌 방향이 LONG인데 1m 신호가 100% 확률로 반대일 때 진입 → 손실
**해결**: 1m horizon 방향이 ensemble 방향과 반대 + confidence=1.0 이면 진입 취소

```python
if ensemble_direction != signal_1m["direction"] and signal_1m["confidence"] >= 0.95:
    logger.warning("[1mFilter] 1m 역방향 95%+ 확률 → 진입 금지")
    return block_entry
```

- 1m 신호는 가장 빠른 반응 속도 → 추세 반전의 조기 경보 역할
- 구현 위치: `strategy/entry/checklist.py` 10번째 항목으로 추가

#### 아이디어 8: "Breathing Room" — 노이즈 구간 하드스톱 동적 확장

**문제**: 10:29 진입 → 10:38 하드스톱. 9분간 가격이 좁은 레인지에서 진동하다 stop hit
**해결**: 진입 직전 N분간 가격 변동폭(high-low)이 평소 대비 2배 이상이면, 하드스톱 폭을 1.3~1.5배 확장

```python
recent_range = max(highs[-3:]) - min(lows[-3:])
range_ratio = recent_range / avg_range_20min
if range_ratio > 2.0:
    stop_width = base_stop_width * 1.5
    logger.info(f"[BreathingRoom] 노이즈 구간 감지 → 손절폭 {stop_width:.1f}pt로 확장")
```

- fake breakout / whipsaw 구간에서 조기 청산 방지
- 구현 위치: `strategy/position/position_tracker.py` stop_price 계산 시

#### 아이디어 9: "Reverse Entry Clamp" — 반대 방향 진입 3분 대기

**문제**: 청산 직후 곧바로 반대 방향 신호 발생 시 연속 손실로 이어지는 패턴 (5/15 이상점 C, 5/18 10:04→10:12)
**해결**: 청산 후 180초 이내 반대 방향 진입 신호는 **1차 skip**

```python
if position.status == "FLAT" and time_since_last_exit < 180:
    if entry_direction != last_exit_direction:
        logger.warning("[ReverseClamp] 청산 후 3분 이내 역방향 진입 금지")
        return block_entry
```

- 연속 손실 패턴(5/15: SHORT 손절 → LONG 손실, 5/18: LONG 손절 → LONG 잔여물 손실) 차단
- 구현 위치: `strategy/entry/meta_gate.py` 또는 `strategy/runtime/execution_governor.py`

#### 아이디어 10: "Day Shape Memory" — 일중 CVD 패턴 유사도 경고

**문제**: 오늘의 CVD 궤적이 과거 손실일과 유사한지 실시간 판단 불가
**해결**: 매 30분마다 오늘의 CVD 곡선을 과거 20일 동시간대와 DTW 비교

```python
# 매 30분 호출
similar_days = dtw_search(today_cvd_slice, historical_cvd_db, top_k=3)
loss_ratio = sum(1 for d in similar_days if d["daily_pnl"] < 0) / len(similar_days)
if loss_ratio >= 0.67:
    size_mult *= 0.5
    logger.warning(f"[ShapeMemory] 유사 패턴 {loss_ratio:.0%} 손실 → 규모 축소")
```

- 구현 위치: `strategy/regime_fingerprint.py` 확장 또는 신규 `strategy/pattern_memory.py`
- 리서치 선행 필요: 20일 CVD DB 구축 → DTW 임계값 튜닝 → WFA 검증

---

## 6. 앙상블·메타게이트 신호 분석

### 진입 시점별 앙상블 상태

| 진입 | 시각 | dir | conf | grade | meta_action | mconf | toxicity | 결과 |
|------|------|-----|------|-------|-------------|-------|----------|------|
| ① | 09:24 | +1 | 0.67 | B | reduce | 0.59 | reduce | 혼합 (stuck) |
| ② | 09:59 | +1 | 0.92 | A | **take** | 0.67 | reduce | ✅ 성공 |
| ③ | 10:12 | +1 | 0.49 | X | **skip** | 0.31 | reduce | ❌ 잔여물 |
| ④ | 10:29 | +1 | 0.61 | B | **skip** | 0.45 | pass | ❌ 손실 |
| ⑤ | 11:07 | -1 | 0.64 | B | **take** | 0.79 | reduce | ✅ 성공 |
| ⑥ | 11:17 | +1 | 0.87 | A | **take** | 0.89 | reduce | ✅ 대성공 |

> **핵심 인사이트**: `meta=take`일 때 승률 100% (3/3), `meta=skip`일 때 승률 0% (악상블 의견 무시하고 진입한 10:29). **meta_action은 ensemble confidence보다 더 신뢰성 높은 진입 필터**다.

### 진입 성공 케이스 공통점

- meta_confidence ≥ 0.67 (중간 신뢰도 이상)
- 1m horizon confidence ≥ 0.89 (단기 신호 강함)
- toxicity_action이 `reduce`여도 meta=take → 진입 가능 (09:59, 11:07, 11:17)

### 진입 실패 케이스 공통점

- meta=skip → ensemble이 강제 진입 (10:29)
- 브로커 잔여물 → 앙상블·메타 모두 skip/grade X인데도 진입 (10:12)
- Hurst fallback(0.5) → 추세/평균회귀 판단 불가 상태에서 진입

---

## 7. 우선순위 로드맵

| 우선순위 | 항목 | 예상 효과 | 구현 난이도 | 검증 방법 |
|----------|------|-----------|-------------|-----------|
| **P0** | ProfitGuard 영속화 (B113) | CB 무력화 방지 | 낮음 (session_state.json에 2개 필드 추가) | 재시작 테스트 |
| **P0** | IntrabarTPCheck 검증·수정 (B114) | TP stuck 방지 | 낮음 (진단 로그 확인 후 미세조정) | 5/19 실세션 로그 |
| **P1** | Resonance Score (아이디어 6) | 10:29형 손실 100% 차단 | 낮음 (if문 1줄) | WFA 6주 시뮬레이션 |
| **P1** | Ghost Position Detector (아이디어 5) | 장기 stuck 시 자동 해소 | 중간 (타이머·카운터 추가) | stuck 시뮬레이션 |
| **P2** | 1m Lead Signal Filter (아이디어 7) | 급반전 조기 감지 | 낮음 (checklist 10번째 항목) | 과거 데이터 백테스트 |
| **P2** | Breathing Room (아이디어 9) | noise stop-out 감소 | 중간 (ATR 동적 계산) | 6주 WFA 변동성 구간 |
| **P3** | Reverse Entry Clamp (아이디어 9) | 연속 손실 패턴 차단 | 낮음 (타이머 추가) | 1~2주 실전 관찰 |
| **P3** | Day Shape Memory (아이디어 10) | 패턴 기반 리스크 조정 | 높음 (DTW 로직·DB 구축) | 리서치 2주 후 판단 |

---

## 8. 결론

5/18은 표면적으로 **+493만원(승률 84.6%)** 의 성공적인 하루였으나, 그 이면에는 통제되지 않은 위험 구간이 다수 존재했다:

1. **B106-B108 Race Condition** → 09:24 stuck, 10:12 잔여물 -55만원 손실로 이어짐. 51차 수정이 당일 미반영.
2. **ProfitGuard 재시작 붕괴** → CB 방어벽이 무력화된 상태로 11:07 진입. 이날은 운 좋게 수익이었으나 확률적 도박.
3. **앙상블 vs 메타게이트 충돌 무시** → 10:29 진입은 meta가 skip 의견을 냈으나 ensemble auto_entry=True만으로 진입 → 손실.

**운에 의존하지 않는 시스템을 위해** 최우선으로 ProfitGuard 영속화 + Resonance Score(meta=skip 시 진입 금지)를 적용해야 한다. 5/19 세션에서 51→57차 수정이 모두 반영되면 stuck/partial fill 문제는 상당 부분 해소될 것으로 예상된다.

---

## 9. Codex 추가 분석 및 의견

### 9-1. 로그 교차검증 기준 핵심 판단

실로그(`20260518_SIGNAL.log`, `20260518_WARN.log`, `20260518_TRADE.log`)와 코드(`main.py`, `CURRENT_STATE.md`)를 교차검증한 결과, 본 문서의 큰 방향성은 매우 타당하다. 특히 아래 3가지는 **실제 운영 리스크**로 확정해도 무방하다.

1. **09:24 partial fill stuck + pending 꼬임**
   - TP1 2계약 주문 중 1계약만 먼저 체결되며 pending이 비정상적으로 길게 잔류했다.
   - 이후 09:52 외부 체결이 pending 없이 먼저 들어와 청산 정합성이 무너진 흔적이 있다.

2. **10:38 ProfitGuard-L4 발동 후 10:57 재시작으로 무력화**
   - 이는 단순 편의 이슈가 아니라, 당일 리스크 차단 규칙이 재시작 한 번으로 우회되는 구조적 결함이다.
   - 11:07 진입이 수익으로 끝났기 때문에 덮인 것이지, 시스템 관점에서는 가장 위험한 종류의 결함이다.

3. **실패 원인의 우선순위는 신호보다 실행 리스크**
   - 이날의 손실 핵심은 "알파 부족"보다 `pending/잔여물/sync/재시작` 문제였다.
   - 즉, 전략 고도화보다 먼저 주문 상태기계와 세션 연속성을 고쳐야 한다.

### 9-2. 본 문서에서 보정하면 더 정확해지는 부분

- **"모든 등급이 GRADE=A"는 사실과 다름**
  - 5/18 전체 SIGNAL.log에는 A/B/C/X가 모두 등장한다.
  - 다만 "실제 진입이 발생한 구간은 A 편중이 강했다"는 식으로 표현하면 더 정확하다.

- **10:12 진입 해석은 재점검 필요**
  - 현재 저장된 SIGNAL.log 기준 10:12:00에는 `grade=A`, `Checklist 9/9`가 기록되어 있다.
  - 따라서 "그 시점은 원래 X등급이라 자동진입 불가였다"는 서술은 현 로그 기준으로는 단정하기 어렵다.
  - 더 정확한 표현은 "10:12 손실은 잔여물/브로커 정합성 이슈가 개입했을 가능성이 높다" 쪽이다.

- **Resonance Score는 아이디어이자 동시에 일부는 이미 코드 반영 상태**
  - 현재 `main.py`에는 `meta_action == "skip"`이면 `grade=X`, `qty=0`으로 막는 로직이 이미 존재한다.
  - 따라서 우선순위는 "신규 구현"보다 "실세션에서 실제로 veto가 일관되게 적용되는지 검증"이다.

### 9-3. 개선안별 Codex 의견

| 항목 | Codex 의견 | 구현 여부 |
|------|------------|----------|
| ProfitGuard 영속화 | **반드시 P0**. 재시작 우회는 실전 시스템에서 허용 불가 | 미구현 |
| IntrabarTPCheck | 방향 정확. stuck 해소의 핵심 축 | 구현 완료, 실세션 검증 대기 |
| stale broker_sync_reason 초기화 | 적절한 수정. 오염된 차단 사유를 줄임 | 구현 완료 |
| Ghost Position Detector | 유효. 단, "시간 초과" 단독 조건보다 "엔진/브로커 수량 불일치 지속"과 결합 권장 | 미구현 |
| Resonance Score | 아이디어 우수. 단, 핵심 veto 로직은 이미 일부 반영 | 부분 구현 |
| 1m Lead Signal Filter | 잠재력 높음. 바로 하드블록보다 shadow mode 검증 추천 | 미구현 |
| Breathing Room | 승률 개선 가능성 있으나 손실 꼬리 확대 위험. `size down`과 세트 권장 | 미구현 |
| Reverse Entry Clamp | 실제 체감 개선 가능. 구현 난이도 대비 효율 좋음 | 일부만 존재 |
| Day Shape Memory | 리서치 가치는 높지만 현재 우선순위는 낮음 | 미구현 |

### 9-4. 최종 의견

이날은 표면 손익이 매우 좋았지만, 시스템 완성도 관점에서는 **"돈을 벌면서도 위험한 결함이 드러난 날"** 에 가깝다. 상위 시스템으로 가려면 "좋은 신호를 더 잘 찾는 것"보다 먼저, **나쁜 실행 상태에서는 아예 거래하지 않도록 만드는 것**이 우선이다.

즉, 5/18의 핵심 교훈은 아래 한 줄로 요약된다.

> **알파 부족보다 실행 무결성 부족이 더 큰 리스크였다.**

---

## 10. 상위 1% 트레이더 관점 추가 제안

### 제안 A: Restart Armistice

**개념**: 장중 재시작 후 일정 시간 자동진입 금지 + broker sync 2회 연속 clean pass 전까지 보호모드 유지

- 재시작 후 60~120초 자동진입 금지
- `broker_sync_verified=True`가 2회 연속 확인되기 전까지 신규 진입 차단
- 재시작 직후 첫 진입은 수동 승인 또는 size 50% 제한

**이득**:
- 10:57→11:07 같은 "재시작 직후 우회 진입" 사고를 원천 차단
- session_state 복원 실패, 잔고 지연, blank-as-flat 오판의 피해 축소

### 제안 B: Position Integrity Checksum

**개념**: 매분 엔진 포지션과 브로커 포지션, pending 상태를 비교해 무결성 점수 산출

체크 예시:
- `engine position qty`
- `broker closable qty`
- `pending order qty`
- `마지막 체결 후 expected qty`

판정:
- 1회 불일치: 경고
- 2회 연속 불일치: 신규 진입 금지
- 3회 연속 불일치: Safe-flat 또는 강제 점검 모드

**이득**:
- 잔여물 오염, 외부체결, partial fill cascade를 신호 레벨이 아니라 운영 레벨에서 차단
- "왜 들어갔지?"보다 먼저 "지금 들어가도 되는 상태인가?"를 점검하게 됨

### 제안 C: Shadow Veto Board

**개념**: 새로운 필터를 바로 실전에 적용하지 말고 2주간 그림자 판정만 기록

대상:
- 1m Lead Signal Filter
- Day Shape Memory
- Breathing Room
- Reverse Entry Clamp

기록:
- "차단했을지 여부"
- "차단했으면 손익이 어떻게 달라졌는지"
- "기존 진입 대비 개선폭"

**이득**:
- 과최적화 없이 실제 기대값 개선 여부 판단 가능
- 상위권 트레이더의 전형적인 검증 방식에 가깝다

### 제안 D: Setup Expectancy Ledger

**개념**: 거래를 시간순이 아니라 셋업 유형별로 분리 집계

예시 태그:
- `meta=take / skip / reduce`
- `grade A/B/C`
- `1m same-side / opposite`
- `Hurst trend / mean-revert`
- `restart_after_boot`
- `partial_fill_occurred`

**이득**:
- "어떤 날 벌었는가"가 아니라 "어떤 구조에서 벌고 잃는가"가 드러남
- 이후 모델·게이트 고도화의 근거 데이터가 생김

### 제안 E: Execution Risk First Policy

**개념**: 신호 강도보다 실행 무결성을 우선하는 정책을 명문화

진입 금지 조건 예시:
- pending order 존재
- 직전 3분 내 broker sync ambiguity
- 장중 재시작 직후
- 외부체결 감지 후 1회 재동기화 미완료
- engine qty vs broker qty mismatch

**이득**:
- "좋은 신호인데 왜 안 들어갔지?"보다 "나쁜 상태라서 안 들어갔다"는 일관성을 확보
- 장기적으로 MDD와 대형 사고 확률을 크게 낮춤

### 상위 1% 관점 결론

상위 1% 선물 트레이더는 대개 신호 하나를 더 추가하기 전에, **시스템이 스스로를 속이지 못하게 만드는 장치**를 먼저 넣는다. 이 관점에서 5/18의 다음 우선순위는 아래가 가장 적절하다.

1. `ProfitGuard 영속화`
2. `Restart Armistice`
3. `Position Integrity Checksum`
4. `IntrabarTPCheck 실세션 검증`
5. `Shadow Veto 방식의 신규 필터 검증`

신호는 이미 충분히 좋다. 이제 필요한 것은 **더 똑똑한 진입**보다 **절대 망가지지 않는 실행 체계**다.
