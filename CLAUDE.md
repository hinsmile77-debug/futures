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
| Python | **3.7 32-bit** (`conda env: py37_32`) |
| OS | Windows 전용 (키움 OpenAPI+ COM/OCX) |
| scipy | **1.5.4** (32-bit DLL 충돌 회피) |
| scikit-learn | 1.0.2, joblib 1.1.1 |
| 선물 분봉 TR | **OPT50029** (선물분차트요청) — OPT10080 사용 금지 |

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

### 3. CORE 피처 3개 — 절대 교체 불가
| 피처 | 파일 | 이유 |
|---|---|---|
| CVD 다이버전스 | `features/technical/cvd.py` | 단기 최강 방향 신호 |
| VWAP 위치 | `features/technical/vwap.py` | 기관 알고리즘 기준선 |
| OFI 불균형 | `features/technical/ofi.py` | 1~3분 방향 선행 |

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
→ 실전 첫 1개월: 최대 사이즈의 30%로 시작
```
