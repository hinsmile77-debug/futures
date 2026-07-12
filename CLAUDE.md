# futures — 미륵이 (KOSPI 200 선물 자동매매)

## 프로젝트 개요

KOSPI 200 선물 1분봉 기반 방향 예측 + 자동매매 시스템 (별칭: **미륵이**).

상세 문서:
```
@CORE.md          (핵심 판단 규칙 — 코딩 전 반드시 확인)
@ROADMAP.md       (Phase별 구현 계획 + 마일스톤 체크리스트)
@PROJECT_DESIGN.md (전체 설계 명세 — 상세 참고용)
```

---

## 운영 환경

| 항목 | 값 |
|---|---|
| Python (런타임) | **3.7 32-bit** (`conda env: py37_32`) — Cybos Plus COM/OCX 필수 |
| Python (재학습) | **3.10 64-bit** (`conda env: py310_64`) — GBM/RF 배치 학습 전용 (226차, OOM 방지) |
| OS | Windows 전용 (Cybos Plus COM/OCX) |
| scipy | **1.5.4** (32-bit DLL 충돌 회피) |
| scikit-learn | 1.0.2, joblib 1.1.1 |
| 선물 분봉 TR | **OPT50029** (선물분차트요청) — OPT10080 사용 금지 |

> **재학습 환경 분리 이유**: py37_32에서 numpy float32 배열 OOM 반복으로 모델 미교체 → CB③ HALT 유발.
> `retrain_eod.py` / `retrain_intraday.py`는 `py310_64`에서 실행되며 `pickle protocol=4`로 저장해 py37_32 런타임에서 로드 호환.
> EOD 로그에 `Python 3.10.20 64-bit`가 찍혀도 정상 — 이상 환경이 아님.
> `EOD_RETRAIN.bat`도 **`py310_64`** 전용 (191차 결정). `scripts\eod_retrain.py`도 동일. 두 파일 모두 py37_32 언급은 구버전 잔재이며, py37_32로 실행하면 OOM 재발 — 다시 거론하지 말 것.

---

## 절대 원칙 (변경 불가)

### 1. 오버나이트 금지 — 15:10 강제 청산
```
15:10 전 포지션 무조건 청산 (수익/손실 무관)
이유: 1분봉 시스템은 야간 데이터 없음 + 갭 리스크가 시스템 전체를 무력화
```

### 2. Circuit Breaker — Phase 2에서 반드시 구현 (건너뛰기 금지)
발동 조건 5종:
- ① 1분 내 신호 5번 반전 → 15분 정지
- ② 5분 내 손절 3연속 → 당일 정지
- ③ 30분 정확도 < 35% → 당일 정지
- ④ 변동성 ATR 3배 초과 → 5분 정지
- ⑤ API 지연 5초 초과 → 즉시 청산

> **[2026-07-05 모의투자 한정 예외] CB②** — `config/settings.py:CB_CONSEC_STOP_LIMIT = 9999` (사실상 비활성).
> 사유: 실투 전환 전에는 거래 기회 확보와 데이터 축적(레이블·SGD 온라인학습·SHAP 심사 표본)이
> 우선이며, 3연속 기준을 그대로 적용하면 모의투자 중 당일 정지가 잦아 표본이 희소해진다.
> **실투 전환 전 반드시 2~3으로 복원 필수** — 아래 "실전 전환 기준"에 체크리스트 항목으로 등록.
> (근거: `docs/260704_SYSTEM_AUDIT_UPGRADE_PROPOSAL.md` §7-1, P0)

> **[2026-07-06 한시 예외] CB③-P4** — `config/settings.py:CB3_P4_GRADE_BLOCK_ENABLED = False`
> (C등급 자동진입 차단만 비활성, accuracy_buf 누적·acc30m_stage 추적·대시보드 표시는 유지).
> 사유: 296차가 30m 호라이즌을 앙상블·CoherenceGate·CascadeCoherence에서 전면 퇴역 확정
> (EOD full_cv acc=0.3052 — 랜덤 이하). CB③-P4는 그 퇴역된 30m 정확도만으로 RESTRICTED를
> 판정하는데, `CB_ACC_RESTRICTED_MIN`(0.30)이 30m의 확정된 구조적 성능(0.3052)과 거의 같아
> 정상 샘플링 변동만으로 상시 RESTRICTED에 붙박여 무관한 정상 호라이즌의 C등급 진입까지
> 차단하는 부작용이 292차 진입0 딥다이브에서 실측됨(acc30m=0.0%로 C등급 상시 차단).
> **실투 전환 전 반드시 재검토** — 30m 재도입 또는 CB③ 기준 호라이즌 교체 시 True로 복원.
> (근거: 292차·296차·297차 커밋, 진입0 딥다이브)

> **[2026-07-08 한시 예외] FP-CRITICAL** — `config/settings.py:FP_CRITICAL_GRADE_BLOCK_ENABLED = False`
> (RegimeFingerprint PSI CRITICAL 시 진입 차단만 비활성, PSI 계산·로그·대시보드 표시는 유지).
> 사유: 이 게이트는 2026-05-07 배선됐으나 학습분포 저장 함수가 프로덕션에서 호출된 적이
> 없어 2026-07-07(299차)까지 약 2개월간 PSI=0.0 고정(사실상 죽은 코드, 미발동)이었음.
> 299차가 임시 부트스트랩 기준선을, 302차가 실제 WFA 26주 기준선을 배선해 "부활"시켰으나,
> 부활 후 이틀 연속(07-07·07-08) 서로 다른 기준선에서 공통적으로 PSI가 하루 종일
> CRITICAL(임계 0.30 대비 최대 4배)에 고착 — 신규 진입 이틀 다 0건. CORE 피처(예: ofi_norm)
> 학습분포가 균등폭 10-bin 중 한 구간에 98%+ 몰리는 첨봉 분포라, 라이브 값이 그 구간을
> 벗어나기만 해도 PSI가 수학적으로 크게 튀는 계측 결함으로 추정 — 진짜 시장 구조 변화
> 감지가 아닐 가능성이 높음. CB②/CB③-P4와 같은 취지로 차단만 비활성.
> **실투 전환 전 반드시 재검토** — 분위수 기반 bin 등 계측 재설계 후 정상 구간에서 PSI가
> 오르내리는 것을 확인하고 True로 복원할 것.
> (근거: 303차, `dev_memory/DECISION_LOG.md` 303차 항목)

### 3. CORE 피처 — 호라이즌 그룹별 분리 (절대 교체 불가)

피처 유효 구간이 호라이즌마다 달라 단일 CORE를 전 호라이즌에 강제하면
10m~30m에서 ofi_norm(틱 잡음)·cvd_divergence(희석) 등이 역효과.
호라이즌 그룹별로 의미 있는 CORE를 분리 정의한다.

| 그룹 | 호라이즌 | CORE 피처 | 파일 | 체크리스트 규칙 |
|---|---|---|---|---|
| **단기** | 1m·3m·5m | CVD 다이버전스 | `features/technical/cvd.py` | 미통과 → 등급 하락 |
| **단기** | 1m·3m·5m | VWAP 위치 | `features/technical/vwap.py` | 미통과 → **강제 X** |
| **단기** | 1m·3m·5m | OFI 불균형 | `features/technical/ofi.py` | 미통과 → 등급 하락 |
| **중기** | 10m·15m | VWAP 위치 | `features/technical/vwap.py` | 미통과 → **강제 X** |
| **장기** | 30m | opt_chain_pcr | `collection/option/option_chain.py` | 미통과 → 등급 하락 |

> `macro_vix`는 2026-06-25 CORE 강등. 일봉 VIX → 분봉 상수, SHAP 기여 ≈ 0, 임계 VIX 27.5 평상시 항상 통과 확인. 보조 피처로 GBM 피처셋에 유지.
> `macro_risk_off`는 2026-06-25 CORE 해제. 모든 호라이즌 feature_names_hz 미포함 확인 (GBM gain=0, SHAP=0). 체크리스트·SGD 경로에도 없음. MacroFeatureTransformer 계산은 유지.

```
설정: config/settings.py  HORIZON_CORE_GROUP, CORE_FEATURES_BY_GROUP
모델: model/multi_horizon_model.py  _CORE_MASK_EXEMPT_BY_HZ (AutoMask 면제)
진입: strategy/entry/checklist.py  entry_horizon 인자로 그룹 결정
```

### 4. COM 콜백 내 dynamicCall·emit 금지
```python
# 콜백(_on_receive_tr_data 등) 내부에서 허용:
#   상태 변수 저장 + QEventLoop.quit() 만
# 금지:
#   dynamicCall, pyqtSignal.emit()
# 이유: 0xC0000409 STATUS_STACK_BUFFER_OVERRUN 크래시
```

### 5. GetRepeatCnt / GetCommData 파라미터 구분
```python
GetRepeatCnt(sTrCode, sRecordName)   # 2번째: record_name (콜백 수신값)
GetCommData(sTrCode, sRQName, ...)   # 2번째: rq_name
# meta.get("record_name") or rq_name  으로 fallback
```

### 6. 알파 리서치 봇 — 자동 통합 절대 금지
```
백테스트 자동 큐: OFF
자동 통합: OFF (사용자 검토 필수)
이유: 검증 없는 알파 자동 통합은 시스템 전체를 망가뜨림
```

---

## 매분 실행 파이프라인 (9단계)

```
08:55  매크로 수집 → 시장 레짐 (RISK_ON / NEUTRAL / RISK_OFF) + 실시간 구독 사전 시작
09:00  장 시작

[매분]
STEP 1: 과거 예측 검증 (T-1·T-3·T-5·T-10·T-15·T-30분 채점)
STEP 2: SGD 온라인 자가학습 (즉시 업데이트)
STEP 3: GBM 배치 재학습 (30분마다)
STEP 4: 피처 생성 (수급·옵션·기술·매크로)
STEP 5: 멀티 호라이즌 예측 (1·3·5·10·15·30분)
STEP 6: 앙상블 진입 판단 + 등급 (A/B/C/X)
STEP 7: 진입 실행
STEP 8: 청산 트리거 감시 (P1~P6 우선순위)
STEP 9: 예측 DB 저장

15:10  강제 청산
15:40  자가학습 일일 마감 + SHAP 피처 심사
```

---

## 확률 판단 기준

| 범위 | 의미 | 행동 |
|---|---|---|
| 50~55% | 중립 | 관망 |
| 55~60% | 약한 방향성 | 관망 |
| 60~70% | 명확한 방향 | 진입 고려 |
| 70% 이상 | 강한 추세 | 적극 진입 |

---

## Phase 완료 현황

| Phase | 내용 | 코드 | 검증 |
|---|---|---|---|
| Phase 0 | 설계·인프라 | ✅ | ✅ |
| Phase 1 | 핵심 시스템 (데이터·피처·모델·전략) | ✅ | ⏳ 모의투자 필요 |
| Phase 2 | 안전장치 + Walk-Forward | ✅ | ⏳ CB 테스트·26주 데이터 필요 |
| Phase 3 | 알파 강화 (미시구조·레짐) | ✅ | ⏳ 실데이터 검증 필요 |
| Phase 4 | 차별화 (RL·베이지안·뉴스) | ✅ | ⏳ 실거래 데이터 필요 |
| Phase 5 | 실전 운영 | — | 미진입 |
| Phase 6 | 알파 리서치 봇 | ✅ (유전자 진화) | ⏳ 장외 스케줄 미연결 |

---

## 실전 전환 기준 (Phase 5 진입 조건)

```
① 모의투자 4주 통산 수익률 양수
② Circuit Breaker 1회 이상 정상 작동 확인
③ Walk-Forward 26주 통과 (Sharpe ≥ 1.5, MDD ≤ 15%, 승률 ≥ 53%)
④ 일일 수익률 변동성 안정적
⑤ CB② 복원 확인 — `CB_CONSEC_STOP_LIMIT` 9999 → 2~3 (모의투자 한정 예외 해제, 절대원칙 §2 참조)
⑥ CB③-P4 재검토 — `CB3_P4_GRADE_BLOCK_ENABLED` False → 복원 여부 결정 (30m 재도입 또는
   CB③ 기준 호라이즌 교체 시 True, 그렇지 않으면 CB③ 자체를 다른 호라이즌 기준으로 재설계
   — 절대원칙 §2 참조)
⑦ FP-CRITICAL 재검토 — `FP_CRITICAL_GRADE_BLOCK_ENABLED` False → PSI 계측(균등폭 10-bin)을
   분위수 기반 등으로 재설계하고, 정상 구간에서 PSI가 오르내리는 것을 실측 확인한 뒤 True로
   복원 (절대원칙 §2 참조)
⑧ SIZING_TARGET_CAPITAL_ENABLED 재검토 — `config/settings.py:SIZING_TARGET_CAPITAL_ENABLED`
   True(모의투자 한정) → 실전 자본 규모에 맞게 `SIZING_TARGET_CAPITAL_KRW`(현재 1억원)를
   재설정한 뒤 False로 전환(사이징 계산에 실제 브로커 잔고를 그대로 사용). 모의 잔고(4.9억)가
   실전 자본과 크게 다르면 PositionSizer의 base_risk가 왜곡돼 계약수 산출이 부정확해지므로
   실전 전환 시 반드시 재검토 (근거: 311차 후속, `dev_memory/NEXT_TODO.md` 참조)
→ 실전 첫 1개월: 최대 사이즈의 30%로 시작
```
