# 설계 결정 및 버그 근본 원인 로그 — futures (미륵이)

---

## 2026-04-27 버그 수정

### [B06] 근월물 코드 포맷 오류 — 날짜계산 fallback "101W06"
**파일**: `collection/kiwoom/api_connector.py`
**증상**: OPT50029 rows=0, FC0 실시간 틱 미수신
**원인**: `GetFutureList()`, `GetMasterCodeList("10")` 모두 모의투자 서버에서 빈값 반환 → 날짜계산 fallback `101W06` 사용 → Kiwoom 실제 코드 포맷과 불일치
**Fix**: `GetFutureCodeByIndex(0)` 0순위 추가 → `A0166000` (실제 근월물 코드)

### [B07] RT_FUTURES 실시간 타입명 오류 — "FC0" vs "선물시세"
**파일**: `config/constants.py`
**증상**: FC0 틱 콜백 영구 미처리 (key 불일치)
**원인**: `OnReceiveRealData(sCode, sRealType, ...)` 에서 `sRealType`은 KOA 코드(`FC0`)가 아닌 한국어 명칭(`선물시세`). 등록 key = `("A0166000", "FC0")`이나 실제 콜백 = `("A0166000", "선물시세")` → dict 조회 실패
**Fix**: `RT_FUTURES = "선물시세"`, `RT_FUTURES_HOGA = "선물호가잔량"`

### [B08] GetRepeatCnt record_name 빈 문자열 처리 오류
**파일**: `collection/kiwoom/api_connector.py`
**증상**: GetRepeatCnt = 0 (OPT50029 콜백에서 record_name='' 수신)
**원인**: `meta.get("record_name") or rq_name` — `""` 빈 문자열은 falsy → rq_name(`"init_1min"`) fallback → GetRepeatCnt에 잘못된 record_name 전달
**Fix**: `meta.get("record_name", "")` — 빈 문자열도 그대로 전달

### [B09] EmergencyExit.get_position() AttributeError
**파일**: `safety/emergency_exit.py`
**증상**: 긴급정지 시 `AttributeError: 'PositionTracker' has no attribute 'get_position'`
**원인**: `PositionTracker`는 `get_position()` 메서드 없음 — `status`, `quantity`, `entry_price` 속성을 직접 보유
**Fix**: `_get_position()`에서 속성 직접 읽기 + `set_futures_code()` 메서드 추가

### [B10] run_minute_pipeline ts datetime → str 변환 누락
**파일**: `main.py`
**증상**: `TypeError: strptime() argument 1 must be str, not datetime.datetime`
**원인**: `realtime_data.py`의 candle dict `ts` 필드는 `datetime` 객체이나 `verify_and_update(current_ts: str, ...)` 는 문자열 기대
**Fix**: `ts_raw.strftime("%Y-%m-%d %H:%M:%S")` 변환 추가

### [B11] PredictionPanel _hz_labels 미초기화 (AttributeError)
**파일**: `dashboard/main_dashboard.py`
**증상**: `AttributeError: 'PredictionPanel' has no attribute '_hz_labels'`
**원인**: `__init__`에서 `_build()` 먼저 호출 후 dict 초기화 → `_build()` 안에서 dict 참조 시 미존재
**Fix**: `_build()` 맨 앞에서 dict 초기화 (IDE 파일 덮어쓰기로 재발 방지)

### [B12] mk_val_label align 파라미터 누락
**파일**: `dashboard/main_dashboard.py`
**증상**: `TypeError: mk_val_label() got an unexpected keyword argument 'align'`
**원인**: `AlphaPanel` 등 여러 곳에서 `align=Qt.AlignCenter` 전달하나 함수 시그니처에 없음
**Fix**: `mk_val_label(text, color, size, bold, align=None)` 추가

---

## 설계 결정 (2026-04-27)

### [D07] GetFutureCodeByIndex(0) 0순위 조회
**결정**: 근월물 코드 조회 우선순위: `GetFutureCodeByIndex(0)` → `GetFutureList()` → `GetMasterCodeList("10")` → 날짜계산
**이유**: KOA 공식 API로 근월물 직접 반환, 모의투자 서버에서도 동작

### [D08] _build()에서 dict 초기화 (UI 패널 패턴)
**결정**: 대시보드 패널 `_build()` 메서드 맨 앞에서 인스턴스 dict 초기화
**이유**: IDE(PyCharm)가 파일 저장 시 `__init__` 순서를 복구하는 현상 반복 발생

---

## 2026-04-26 버그 수정

### [B01] TR 코드 오류 — OPT10080 → OPT50029
**파일**: `config/constants.py`
**증상**: 선물 분봉 TR 호출 실패
**원인**: OPT10080은 주식분봉차트조회요청 (주식 전용), 선물에 사용 불가
**Fix**: `TR_FUTURES_1MIN = "OPT50029"` (선물분차트요청 — KOA 공식)

### [B02] COM 콜백 스택 오버런 — 0xC0000409
**파일**: `collection/kiwoom/api_connector.py`
**증상**: `_on_receive_tr_data` 콜백에서 `GetRepeatCnt`/`GetCommData` 호출 → 크래시
**원인**: 키움 OCX는 COM 이벤트 스택 위 재진입(reentrant) dynamicCall 불허
**Fix**:
- 콜백: 메타데이터(tr_code, prev_next, record_name) 저장 + QEventLoop.quit() 만
- exec_() 복귀 후 정상 루프에서 `get_repeat_cnt()` → `_parse_tr_row()` 실행

### [B03] record_name vs rq_name 혼동
**파일**: `collection/kiwoom/api_connector.py`
**증상**: GetRepeatCnt 반환값 = 0 (데이터 미조회)
**원인**: GetRepeatCnt 2번째 파라미터에 rq_name 전달 → record_name이어야 함
**Fix**: `meta.get("record_name") or rq_name` fallback 패턴
```python
GetRepeatCnt(sTrCode, sRecordName)   # 2번째: record_name
GetCommData(sTrCode, sRQName, ...)   # 2번째: rq_name
```

### [B04] GetCommDataEx → GetCommData
**파일**: `collection/kiwoom/api_connector.py`
**증상**: 서명 오류로 데이터 조회 실패
**Fix**: `GetCommDataEx` → `GetCommData` (올바른 API 이름)

### [B05] Hurst Exponent 공식 오류 (Gemini 원본)
**파일**: `features/technical/hurst_exponent.py`
**원인**: Gemini 제공 코드에 오류 포함
```python
# 오류: Variance 분석 혼동
hurst_idx = reg[0] * 2.0
# 수정: R/S 분석 기준 (polyfit 기울기 = H)
hurst_idx = reg[0]
```

---

## 설계 결정

### [D01] 근월물 코드 조회 우선순위
**결정**: GetFutureList() → GetMasterCodeList("10") → 날짜 계산 fallback
**이유**: GetMasterCodeList("10")은 모의투자 서버에서 None 반환 가능

### [D02] PPO 에이전트 — numpy fallback + torch optional
**결정**: `learning/rl/ppo_agent.py`는 numpy만으로도 실행 가능하게 구현
**이유**: py37_32 환경에서 torch 설치 불안정 가능성

### [D03] 알파 리서치 봇 — 자동 통합 절대 금지
**결정**: `백테스트 자동 큐: OFF`, `자동 통합: OFF`
**이유**: 검증 없는 알파가 실전 시스템에 자동 반영되면 포트폴리오 전체가 무너질 수 있음
**승격 기준**: IC≥0.02, Sharpe≥0.8, OOS Sharpe>0, n_samples≥300

### [D04] scipy 버전 고정 — 1.5.4
**결정**: `scipy==1.5.4`
**이유**: scipy 1.7.x → py37_32 환경에서 DLL 충돌 발생

### [D05] 대시보드 — PyQt5 없을 때 텍스트 fallback
**결정**: `dashboard/main_dashboard.py`는 PyQt5 없어도 동작
**이유**: 서버/자동화 환경에서도 로그 확인 가능하도록

### [D06] v7.0 Gemini 제안 전량 채용 (6/6)
**결정**: Latency·Hurst·적응형켈리·VPIN·마디가·Cancel Ratio 모두 채용
**목표**: Sharpe 3.5~4.0, MDD -30%
**근거**: 6개 전부 순수 보완 관계 (중복 없음)

---

## 절대 원칙 (변경 불가)

| 원칙 | 내용 |
|---|---|
| 오버나이트 금지 | 15:10 강제 청산, 예외 없음 |
| Circuit Breaker | Phase 2에서 반드시 구현, 건너뛰기 금지 |
| CORE 3개 | CVD·VWAP·OFI 절대 교체 불가 |
| COM 콜백 | dynamicCall·emit 콜백 내부 금지 |
