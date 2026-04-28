# 설계 결정 및 버그 근본 원인 로그 — futures (미륵이)

---

## 2026-04-28 버그 수정 (오후 세션)

### [B13] CVD direction 항상 0 — FC0 FID10 부호 오해
**파일**: `collection/kiwoom/realtime_data.py`
**증상**: `[DBG-F4]` buyvol=161 sllvol=0 (100% buy), CVD delta=0
**원인**: FC0 FID10(`현재가`) 앞 부호(+/-)는 전일대비 방향이지 틱 방향이 아님. 처음에 `raw_price.startswith('-')` 방식으로 틱 방향 판단 시도 → 모든 틱이 buy로 분류
**Fix**: tick test 방식 채용 — `is_buy_tick = price >= self._prev_tick_price` (Lee-Ready 근사). `_prev_tick_price` 인스턴스 변수 추가, bar dict에 `buy_vol`/`sell_vol` 누적

### [B14] OFI 영구 0 — bid/ask FH0 전용 FID 미수신 (미해결)
**파일**: `collection/kiwoom/realtime_data.py`, `main.py`
**증상**: `[DBG-F4]` bid=0.00 ask=0.00, OFI=0
**원인**: FC0(선물시세)는 체결 데이터 전용 — FID41(매도1호가)/FID51(매수1호가)를 포함하지 않음. bid/ask는 FH0(선물호가잔량) 실시간 타입에서만 수신 가능
**현재 상태**: `_on_tick_price_update()`에 `ofi.update_hoga()` 호출 추가했으나 `if bid1 and ask1` 조건이 항상 False → OFI 여전히 0
**근본 해결**: FH0 별도 `register_realtime()` + 호가 전용 콜백 필요 (모의투자 서버 지원 여부 미확인)

### [B15] 손절 exit price = close가 (항상 불리)
**파일**: `main.py`
**증상**: LONG 손절 시 `close_position(close, "하드스톱")` — close가가 stop_price보다 낮아도 close가로 청산 → PnL 과소계산
**원인**: `_check_exit_triggers()` 호출 시 bar dict를 전달하지 않아 bar low와 stop_price 비교 불가
**Fix**: `_check_exit_triggers(price, features, decision, bar)` 파라미터 추가. LONG 손절: `exit_price = max(stop_price, bar_low)`, SHORT 손절: `exit_price = min(stop_price, bar_high)`

### [B16] 5층 로그 탭 1·3·5 빈 화면
**파일**: `main.py`
**증상**: 대시보드 로그 탭 1(시스템)/3(주문체결)/5(모델AI) 항상 빈 화면
**원인**: `log_manager.subscribe()` 어디에도 등록 없음 — LogManager 버퍼에만 쌓이고 대시보드 미전달
**Fix**: `__init__`에 배선 추가:
```python
log_manager.subscribe("SYSTEM",   lambda e: self.dashboard.append_sys_log_tagged(e.message, e.level))
log_manager.subscribe("TRADE",    lambda e: self.dashboard.append_trade_log(e.message))
log_manager.subscribe("LEARNING", lambda e: self.dashboard.append_model_log(e.message))
```

### [B17] PnL 수치 하드코딩 — "+12,000원" 고정
**파일**: `dashboard/main_dashboard.py`
**증상**: 미실현손익/일일누적/VaR 수치가 고정값으로 표시
**원인**: `LogPanel._build()`에서 라벨(`QLabel`)을 로컬 변수로만 생성 → `self`에 참조 없음 → `update_pnl_metrics()` 메서드 추가해도 라벨 접근 불가
**Fix**: `self._pnl_vals = {}`, `self._pnl_bars = {}` dict에 라벨 참조 저장. `update_pnl_metrics(unrealized_krw, daily_pnl_krw, var_krw)` 메서드 추가

### [B18] 신뢰도 "신뢰도 — %" 고정
**파일**: `dashboard/main_dashboard.py`
**증상**: 현재가 우측 신뢰도 레이블이 항상 "신뢰도 — %"
**원인**: `PredictionPanel.update_data()`에 `conf` 파라미터 없음 → `lbl_conf` 미갱신
**Fix**: `update_data(conf=None)` 파라미터 추가, `lbl_conf.setText(f"신뢰도 {conf*100:.1f}%")`

### [B19] 호라이즌 카드·체크리스트 갱신 안됨
**파일**: `main.py`
**증상**: 대시보드 예측 패널 호라이즌별 신호/확률 및 체크리스트 9항목 갱신 없음
**원인**: `main.py`의 `run_minute_pipeline`에서 `dashboard.update_prediction()` / `update_entry()` 호출 없음
**Fix**: STEP 6 이후 호라이즌 키 매핑(`{"1m":"1분",...}`) + 매분 `update_prediction()` / `update_entry(checks_ui)` 호출 추가

---

## 설계 결정 (2026-04-28 오후)

### [D09] 손절 exit price = stop_price (bar low 기반 보정)
**결정**: 하드스톱 발동 시 `exit_price = max(stop_price, bar_low)` (LONG 기준)
**이유**: close가로 청산하면 bar 내에서 손절선을 이미 통과한 케이스에서도 close가 기준으로 PnL이 계산되어 손실 과소계산. 실제 체결은 손절선 도달 시점에 이루어지므로 stop_price 기준이 현실적
**주의**: bar_low > stop_price인 경우(갭 상황)도 있으므로 max()로 방어

### [D10] CVD 틱 방향 — tick test (Lee-Ready 근사)
**결정**: `is_buy_tick = (price >= prev_price)` — 전 틱 대비 가격 상승 → buy tick
**이유**: FC0 FID10 부호는 전일대비 방향이지 틱 방향이 아님. Kiwoom API에는 틱 방향 직접 제공 FID 없음. Lee-Ready 근사가 bid/ask 부재 시 표준적 대안
**한계**: 동가(price == prev_price) → buy로 처리 (보수적). OFI bid/ask 없이는 한계 존재

### [D11] Path B raw_data.db 13거래일 축적 계획
**결정**: `raw_candles`(OHLCV) + `raw_features`(JSON) DB에 매분 저장. 13거래일 후 `batch_retrainer.py`로 첫 실제 모델 학습
**이유**: 더미 GBM 모델 → 랜덤 예측. 실제 시장 데이터로 학습된 모델 없이는 Phase 3 신호 품질 검증 불가
**시작일**: 2026-04-28. 목표: 약 2026-05-15 (13거래일 후)

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
