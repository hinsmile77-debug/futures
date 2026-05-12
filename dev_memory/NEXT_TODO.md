# 다음 할 일 목록 — futures (미륵이)

> 검증 필요 항목, 예정된 작업, 알려진 잠재 이슈.

### 완료 처리 규칙
- 완료 시 `[DONE YYYY-MM-DD]` 태그 추가
- DONE 태그 후 1주일 경과 시 삭제

---

## 2026-05-12 챔피언-도전자 시스템 + MicroRegimeClassifier 연결

- [DONE 2026-05-12] `MicroRegimeClassifier` → `main.py` 연결 (ADX 실계산, 5-레짐, 탈진 감지)
- [DONE 2026-05-12] RegimeChampGate [§20] 구현 — 챔피언=None 레짐 진입 차단 (`main.py` STEP 6)
- [DONE 2026-05-12] `_MICRO_EN` 탈진 추가 + `strategy_params.py` EXHAUSTION 오버라이드 3종
- [DONE 2026-05-12] `dashboard/main_dashboard.py` `lbl_micro_regime` 헤더 배지 + `update_micro_regime()` 어댑터
- [DONE 2026-05-12] `challenger_panel.py` `_lbl_cur_regime` 상태바 + `update_micro_regime()` 메서드
- [DONE 2026-05-12] `CHALLENGER_SYSTEM_PLAN.md` 전면 재작성 (완료 체크·설계 상세·검증 계획)

### 챔피언-도전자 검증 항목 (실 데이터 필요)

- [V-C1] 탈진 레짐 실발동 확인 (장 중 SIGNAL.log `[MicroRegime] 레짐 변경 → 탈진` 확인)
- [V-C2] RegimeChampGate 차단 동작 확인 (탈진 레짐에서 진입 시도 시 `grade=X·[RegimeChampGate]` 로그 확인)
- [V-C3] Shadow WARNING 발송 확인 (일별 마감 후 경보 탭 WARNING 표시)
- [V-C4] 미시 레짐 헤더 배지 갱신 확인 (헤더 `lbl_micro_regime`가 매분 정확히 갱신되는지)

---

## 2026-05-12 로그 분석 기반 버그 수정

- [DONE 2026-05-12] MetaConf `loss="log_loss"` → `loss="log"` 수정 (`learning/meta_confidence.py`) — sklearn 1.0.2 호환
- [DONE 2026-05-12] `config/secrets.py` 계좌번호 `7034809431` → `333042073` 수정
- [DONE 2026-05-12] ExitCooldown 중복 로그 제거 (`main.py` `_exit_cooldown_applied_this_fill` 플래그)
- [DONE 2026-05-12] CB HALTED 상태 Sizer 억제 (`main.py` `is_entry_allowed()` 게이트)
- [DONE 2026-05-12] TRADE.log 한글 깨짐 3곳 수정 (`strategy/position/position_tracker.py` line 464/487/513)
- [DONE 2026-05-12] `api_connector.py` 잔고 sanity check — liquidation_eval=0 대체 시 WARNING, profit_rate 이상값 경고

- [NEXT 2026-05-13] `CybosInvestorRaw 후보 없음` 09:00~10:44 갭 원인 조사
  - 7건 거래가 모두 수급 데이터 없는 구간에서 발생
  - `CpSysDib.CpSvrNew7212`가 장 시작 직후 미응답하는 조건 확인
  - 필요 시 warmup 대기(장 시작 후 N분 수급 신호 차단) 도입 검토

- [NEXT 2026-05-13] 2026-05-12 CB 발동 후 재시작 첫 장에서 MetaConf 정상 학습 확인
  - LEARNING.log에서 `MetaConf 학습 오류` 메시지 완전 소멸 확인
  - MetaConf `model_fitted=True` 및 `confidence_score` 범위 정상 확인

---

## 2026-05-11 자동 로그인

- [DONE 2026-05-11] `scripts/cybos_autologin.py` — `ncStarter.exe /prj:cp` 기반 모의투자 자동 로그인 정상 동작 확인
  - 실행파일 `_ncStarter_.exe` → `ncStarter.exe /prj:cp` 변경
  - 팝업 대기 10s → Enter → 3초 후 스크립트 종료 흐름 확정
  - 모의투자 접속 버튼 좌표 `(1416, 645)` 확정

- [NEXT 2026-05-12] `start_mireuk.bat` 에서 autologin 스크립트 선행 호출 연결 검증
  - autologin 완료 후 메인 시스템이 이미 연결된 Cybos에 접속하는 타이밍 확인

---

## 2026-05-10 Cybos Plus follow-up

### 2026-05-11 log review update

- [DONE 2026-05-11] review latest `start_mireuk_cybos_test.bat` run logs for Cybos startup and realtime evidence
  - confirmed:
    - Cybos account fallback worked: configured `7034809431` -> runtime `333042073`
    - `CpTd0723` mock no-data (`97007`) was interpreted as flat without blocking startup
    - UI boot + Qt event loop entry completed through Cybos path
    - realtime-derived `MICRO` ticks were still being produced after `09:03`
  - caution:
    - `SYSTEM` log still said `FC0 실시간 틱 대기 중`, which is a Kiwoom-specific waiting message and can be misleading on Cybos
    - `MICRO-MINUTE` log kept repeating `ts=2026-05-11 09:03:00`, so Cybos minute-close / handoff behavior still needs explicit validation

### 2026-05-11 리팩토링 완료 선언

미륵이 브로커 백엔드가 **키움 OpenAPI+ → Cybos Plus** 로 전면 리팩토링 완료됐다.
키움 관련 TR/FID 코드는 이제 레거시이며, 신규 작업은 모두 Cybos Plus 기준으로 수행한다.

- [DONE 2026-05-11] 선물 투자자 수급 수집 (`request_investor_futures` / `request_program_investor`) 다중 후보 실구현
- [DONE 2026-05-11] 미결제약정(OI) `FutureCurOnly` 실시간 저장 (`realtime_data._last_oi`)
- [DONE 2026-05-11] `DivergencePanel` 선물 수급 섹션 추가 (외인/개인/기관/차익/비차익/OI 2×3 그리드)

### NEXT after 2026-05-11 review

- [DONE 2026-05-11] fix startup crash caused by `None` formatting in Cybos balance logging
- [DONE 2026-05-11] harden `MetaConf` training input normalization so ragged feature vectors do not reach fit/buffer
- [DONE 2026-05-11] switch sizer balance source from fixed fallback to latest Cybos summary
- [DONE 2026-05-11] route `CpTd6197` validation output into `SYSTEM.log`
- [DONE 2026-05-11] document Cybos daily-pnl source-of-truth rule (`CpTd6197` first, HTS reference-only)
- [DONE 2026-05-11] replace account-panel `포지션 복원` path with `잔고 새로고침` + `F5`
- [DONE 2026-05-11] force dashboard balance rows to clear immediately on final exit to `FLAT`

- [NEXT 2026-05-12] verify final-exit balance UI clears immediately on the next TP2 / full-close case
  - check:
    - `[BalanceUI] force flat rows reason=final_exit:...`
    - `[BalanceRefresh] trigger=ExitFillFlow mode=final retries=250ms,1200ms`
    - subsequent `BalanceUI ... rows=0`

- [NEXT 2026-05-12] confirm no stale cached balance row reappears after post-exit refresh retries
  - goal:
    - ensure `_last_balance_result` and dashboard rendering stay aligned after `FLAT`

- [NEXT 2026-05-12] verify whether Cybos realtime is truly flowing end-to-end or only partially flowing into micro/hoga paths
  - check:
    - `collection/cybos/realtime_data.py` tick callback count during market hours
    - dashboard current price panel changes from Cybos stream
    - whether minute bars are actually closing with advancing timestamps

- [DONE 2026-05-11] verify Cybos realtime receipt outside main UI with `scripts/check_cybos_realtime.py`
  - command:
    - `python scripts/check_cybos_realtime.py --listen-sec 20`
  - result:
    - `IsConnect=1`
    - `TradeInit=0`
    - realtime code `A0166`
    - tick count `71`
    - hoga count `228`
    - script returned `PASS`
  - interpretation:
    - `FutureCurOnly` / `FutureJpBid` broker receipt is confirmed
    - remaining issue scope moves to main runtime integration, minute-close progression, or status/log interpretation

- [NEXT 2026-05-12] replace Kiwoom-specific waiting/status wording in `main.py`
  - current issue:
    - `장중 — FC0 실시간 틱 대기 중` is shown even on Cybos runs
  - goal:
    - broker-aware waiting message so Cybos runs are not diagnosed with the wrong mental model

- [DONE 2026-05-11] make waiting-status wording broker-aware in `main.py`
  - result:
    - Kiwoom: `Kiwoom FC0 실시간 틱 대기 중`
    - Cybos: `Cybos 실시간 분봉 대기 중 (FutureCurOnly/FutureJpBid 수신 시 자동 진행)`

- [DONE 2026-05-11] fix Cybos minute pipeline timestamp repetition bug (MICRO-MINUTE ts=09:03:00)
  - root cause:
    - `run_minute_pipeline()` reset `_last_recovery_ts = ""` at line 871 on every call
    - recovery path (`_try_pipeline_recovery`) set guard → called pipeline → guard erased → could re-fire after 4 min
    - result: same 09:03 bar re-processed every ~4 min indefinitely
  - fix:
    - moved `_last_recovery_ts = ""` reset from `run_minute_pipeline()` to `_on_candle_closed()`
    - now only real bar-close events clear the guard; recovery calls leave it intact

- [NEXT 2026-05-12] run one Cybos-focused realtime probe script outside main UI
  - goal:
    - separate broker realtime receipt from main-loop / dashboard-state interpretation
  - expected:
    - `FutureCurOnly` ticks increase
    - `FutureJpBid` hoga events increase
    - last tick time and price continue advancing during KRX hours

- [DONE 2026-05-11] add `scripts/check_cybos_realtime.py` for Cybos-only realtime verification
  - scope:
    - `FutureCurOnly` tick count
    - `FutureJpBid` hoga count
    - progress prints during listen window
    - PASS/WARN/FAIL exit result for quick operator judgment

- [DONE 2026-05-11] add Cybos `BAR-CLOSE` system log emission
  - goal:
    - make minute close progression observable like Kiwoom path
  - file:
    - `collection/cybos/realtime_data.py`

### DONE today

- [DONE 2026-05-10] implement concrete `collection/cybos/` runtime path for connection, balance, snapshot, realtime, and fill wiring
- [DONE 2026-05-10] add `scripts/check_cybos_session.py` for admin 32-bit Cybos smoke testing
- [DONE 2026-05-10] add `start_mireuk_cybos_test.bat` for safe Cybos-only startup without changing default Kiwoom execution
- [DONE 2026-05-10] correct `FutureMst` field indices after live snapshot validation
- [DONE 2026-05-10] fix Cybos startup account mismatch by auto-switching runtime account to the signed-on broker account when `secrets.py` account is not present in session
- [DONE 2026-05-10] verify `main.py` can boot UI and enter Qt event loop through Cybos backend

### NEXT priority

- [NEXT 2026-05-12] verify live market realtime flow during KRX hours
  - confirm `FutureCurOnly` tick events increase
  - confirm `FutureJpBid` hoga events increase
  - confirm dashboard price panel updates from Cybos stream

- [NEXT 2026-05-12] run one mock futures order through `CpTd6831`
  - expected:
    - order request success
    - `CpFConclusion` event arrives
    - pending order / position / dashboard reflect fill correctly

- [NEXT 2026-05-12] validate Cybos fill payload against active `main.py` order state machine
  - check:
    - `trade_gubun`
    - `order_gubun`
    - `order_status`
    - `position_qty`
    - `closable_qty`

- [DONE 2026-05-11] replace Cybos investor-data placeholder with real Cybos investor/program TR mapping
  - `CpSysDib.CpSvrNew7212` (idx0=1, 1개월 누적): 선물/콜/풋 투자자별 순매수 확정
  - `get_panel_data()` rt_call/rt_put/fi_call/fi_put/rt_bias/fi_bias 실제값 연결
  - option_flow_supported 자동 활성화

- [NEXT 2026-05-12] run `_probe_8119_fields.py` during market hours (09:00~15:30)
  - goal: confirm h[0]=차익매수, h[2]=차익순매수, h[3]=비차익매수, h[5]=비차익순매수
  - command: `py37_32\python.exe -X utf8 scripts/_probe_8119_fields.py`
  - if layout differs: update arb_net/nonarb_net index in `request_program_investor()`

- [NEXT 2026-05-12] verify investor-flow pipeline update every minute
  - confirm: "대기" → actual values in divergence panel after first `fetch_all()`
  - check: `[CybosInvestorRaw] futures via CpSysDib.CpSvrNew7212` in SYSTEM.log

- [DONE 2026-05-11] fix dashboard stylesheet parse warnings
  - root cause:
    - `}}` at end of non-f-string in Python = literal two `}` chars, not f-string escape
    - Qt stylesheet parser received `QFrame{...;}}` (extra `}`) → parse warning
  - fixed locations in `dashboard/strategy_dashboard_tab.py`:
    - `_card()` function
    - `_HeaderCard.__init__()`
    - `_StageTable` `QTableWidget` stylesheet (×2 tables)
  - fix: removed extra `}` from the closing of each `QHeaderView::section{...}` and `QFrame{...}` block

- [DONE 2026-05-11] fix Cybos server label / realtime method wording in `main.py`
  - scope:
    - login info log (line ~720)
    - system startup log (line ~2608)
  - fix:
    - broker name checked via `broker.name == "cybos"`
    - Cybos: server label = `"Cybos 실서버"`, rt method = `"FutureCurOnly/Subscribe"`
    - Kiwoom: original `GetServerGubun` path retained

## 2026-05-08 역방향진입 / PnL 분리 / 학습 방화벽 후속

### [DONE 2026-05-08] 당일 자동종료 후 수동 재시작 시 중복 종료 재실행 방지
- **내용**:
  1. `auto_shutdown_done_date == today` 인 상태에서 장마감 이후 재시작하면 `_daily_close_done`까지 복구
  2. `daily_close()` 초입에서 같은 날짜 자동종료 완료 이력을 다시 확인해 재실행 차단
  3. 자동 종료 알림/프로그램 종료가 당일 1회만 실행되도록 이중 방어
- **범위**: `main.py`

### [DONE 2026-05-08] 봉차트 우측 여백/마커 시인성/토글 UX 개선
- **내용**:
  1. 차트 우측에 10봉 크기 여백 추가
  2. LONG/SHORT 진입 마커를 더 큰 배지형 스타일로 개선
  3. `LONG` 라벨은 위쪽, `SL` 라벨칩은 아래쪽으로 고정하고 마커 겹침 회피 로직 추가
  4. 단축키를 다시 누르면 봉차트 윈도우가 닫히는 토글 동작 적용
- **범위**: `dashboard/main_dashboard.py`

### [DONE 2026-05-08] 1계약 TP1 보호전환 선택형 UI + 수동청산 버튼 실주문 연결
- **내용**:
  1. 청산관리 탭에 `TP1 본절보호 / 본절+alpha / ATR 기반 보호이익` 버튼 및 툴팁 추가
  2. 1계약 TP1 도달 시 선택 모드에 따라 보호전환하도록 구현
  3. `33% / 50% / 전량 청산` 버튼을 실제 수동청산 주문으로 연결
  4. 1계약 보유 시 `33%`, `50%` 클릭을 자동 `전량청산`으로 승격
- **범위**: `dashboard/main_dashboard.py`, `main.py`, `strategy/position/position_tracker.py`

### [NEXT 2026-05-09] 수동청산 버튼 체결 검증
- **내용**:
  1. 2계약 이상 보유 상태에서 `33%`, `50%`, `전량 청산` 각각 1회씩 클릭
  2. WARN.log `[ManualExit] 요청 pct=... send_qty=... kind=...` 확인
  3. TRADE.log `[주문요청] 수동 ... 청산 ... 체결대기` 및 체결 후 PnL 갱신 확인
  4. `trades.db`에 부분청산 레코드가 정상 적재되는지 확인

### [NEXT 2026-05-09] 1계약 TP1 보호전환 3모드 장중 검증
- **내용**:
  1. `본절보호`, `본절+alpha`, `ATR 기반 보호이익`을 각각 한 번씩 선택
  2. WARN.log `[ExitConfig] ...`, `[SingleContractTP1] ... mode=...` 확인
  3. TP1 도달 후 stop price가 의도한 값으로 이동하는지 확인
  4. 재시작 후 `session_state.json` 복원값과 UI 선택 상태가 일치하는지 확인

### [NEXT 2026-05-09] 장마감 이후 수동 재시작 재현 검증
- **내용**:
  1. 같은 날짜 장마감 이후 프로그램을 수동 재시작
  2. 자동 종료 안내 문구와 `[System] 자동 종료 실행` 로그가 다시 나오지 않는지 확인
  3. `session_state.json`의 `auto_shutdown_done_date` 유지 여부 확인

### [NEXT 2026-05-09] 봉차트 마커 충돌/토글 UX 실운영 검증
- **내용**:
  1. LONG 진입과 SL 손절 마크가 같은 봉 또는 인접 봉에 찍히는 구간 확인
  2. 위/아래 강제 분리와 충돌 회피가 실제로 충분한지 시각 검증
  3. 봉차트 단축키를 연속 입력해 열기/닫기 토글이 안정적으로 반복되는지 확인

### [DONE 2026-05-08] 역방향진입 자동진입 전용 토글 구현
- **내용**: 진입관리 패널 상단에 `역방향 진입` 토글 추가, 자동진입 판단 방향만 반전
- **범위**: UI 토글, 세션 저장/복원, 주문 직전 방향 반전, 로그 반영

### [DONE 2026-05-08] 진입관리 패널 `원신호 / 실행신호` 동시 표시
- **내용**: 미륵이 원판단과 최종 실행 방향을 함께 표시
- **범위**: 진입관리 카드, 경고 문구, `TRADE/SIGNAL` 로그

### [DONE 2026-05-08] 손익 PnL / 손익 추이에 `실행 / 순방향` 병기
- **내용**: 손익 카드와 일별/주별/월별 손익 추이에 실행 손익과 순방향 손익을 동시에 표시
- **범위**: `dashboard/main_dashboard.py`, `trades` 저장 컬럼, 복원 경로

### [DONE 2026-05-08] 역방향진입이 학습/통계에 섞이지 않도록 방화벽 적용
- **내용**: 등급 통계, 레짐 통계, 추이 통계, daily PF, daily close snapshot을 순방향 기준으로 고정
- **범위**: `utils/db_utils.py`, `main.py`, `strategy/position/position_tracker.py`

### [NEXT 2026-05-09] 역방향진입 ON/OFF UI 실동작 검증
- **내용**:
  1. ON/OFF 클릭 시 진입관리 패널 `원신호 / 실행신호` 변화 확인
  2. `session_state.json` 재시작 복원 확인
  3. `TRADE/SIGNAL` 로그 `역방향진입=ON/OFF` 표기 확인

### [NEXT 2026-05-09] 실청산 1회 기준 `실행 / 순방향` 손익 수치 검증
- **내용**:
  1. 청산 후 손익 PnL 카드 `실행 / 순방향` 값 확인
  2. 손익 추이 탭 일별/주별/월별 누적과 요약 카드 값 확인
  3. `trades.db`의 `forward_*` 컬럼과 UI 값 대조

### [NEXT 2026-05-09] 학습/효과검증 패널 비오염 검증
- **내용**:
  1. 역방향진입 ON 상태 거래가 있어도 `fetch_grade_stats()`, `fetch_regime_stats()`, `fetch_trend_*()`가 순방향 기준으로 유지되는지 확인
  2. effect validation / learning / daily close 리포트가 역방향 실행손익에 끌려가지 않는지 점검

## 즉시 확인 필요 (추가됨 2026-05-08 6차 세션)

### [V52] PnL 수치 절반으로 줄었는지 확인 [DONE 2026-05-08]
- **내용**: B64 수정 후 1pt 수익 = 250,000원 (이전: 500,000원)으로 정확히 절반
- **방법**: TRADE 로그 `PnL=+Xpt (Y원)` 에서 `Y = X × qty × 250,000 - 수수료(왕복~79,500원)` 확인
- **기준**: 1계약 1pt 수익 시 → 250,000 - 79,500 ≈ **170,500원** 표시 (이전: 499,500원)
- **완료 근거**: `normalize_trade_pnl(1152.7, 1, 1.5) -> gross=375,000 / commission=8,645 / net=366,355` 확인. `fetch_today_trades('2026-05-08')` 합계도 정규화 기준 `-1,618,766원`으로 일치.

### [V57] 잔고 패널 실현손익 vs 손익 추이 오늘 값 일치 확인 [다음 재시작 후]
- **내용**: `OPW20006` summary blank 상황에서도 잔고 패널 `실현손익`과 `손익 추이` 오늘 일별 값이 같은지 확인
- **방법**:
  1. 미륵이 재시작
  2. 장중 또는 장후 `OPW20006` blank fallback 유도
  3. 잔고 패널 `실현손익`과 `손익 추이` 오늘 `P/L 원` 비교
- **기준**: 둘 다 `trades.db net_pnl_krw` 합계와 동일. 재시작 직후 `0`으로 잠깐 덮어쓰지 않아야 함

### [V58] 키움 HTS 실현손익 vs 내부 정규화 손익 차이 재대조 [다음 장중]
- **내용**: HTS `실현손익`과 내부 `net_pnl_krw` 합계 차이가 수수료/세금/브로커 기준 차이인지 재확인
- **방법**:
  1. HTS 실시간 잔고 `실현손익` 캡처
  2. `fetch_today_trades(today)` 합계와 비교
  3. WARN.log에서 fallback 대신 브로커 원문 summary가 들어온 시점 대조
- **기준**: 브로커 원문이 내려온 시점의 차이 규모와 방향을 기록. 차이가 지속되면 수수료 모델 또는 브로커 포함 비용 재조정

### [V59] trades.db migration 후 손익 추이 주/월 집계 이상 여부 확인 [다음 실행]
- **내용**: `entry_ts -> exit_ts` 기준 변경 후 주간/월간 누적 PnL이 기대대로 보이는지 확인
- **방법**: 대시보드 `손익 추이` 탭에서 일별/주별/월별 테이블 값과 `SELECT exit_ts, pnl_krw FROM trades` 집계 대조
- **기준**: 당일/주간/월간 누적이 동일한 정규화 손익 기준으로 이어지고, 청산일 기준으로 행이 배치됨

### [V53] CB③ 30m 피드 확인 [장 시작 2시간 후]
- **내용**: STEP 1에서 30m 호라이즌만 `record_accuracy()` 호출되는지, 20샘플 전에 HALT 없는지 확인
- **방법**: WARN.log `[CB③ 경고 1/2]` 또는 `[CB] 당일 시스템 정지 | 30분 정확도` 로그 시각 확인
- **기준**: 09:00 기준 20개 30m 검증은 오전 11:30~12:00경부터 가능. 그 전 HALT 없으면 정상

### [V54] 청산 후 ExitCooldown 차단 확인 [다음 TP/손절 청산 시]
- **내용**: TP청산 후 2분, 손절청산 후 3분 이내 STEP 7 진입 차단 로그 확인
- **방법**: WARN.log `[ExitCooldown] TP1 후 2분 재진입 금지 until HH:MM:SS` → 해당 시간 이전 `[진입]` 로그 없음 확인
- **기준**: 차단 이유 로그 `[차단] 청산 후 쿨다운 — N초 후 재진입 가능` 출력

### [V55] Hurst 차단 로그 확인 [장 중]
- **내용**: Hurst < 0.45 구간에서 `[차단] Hurst X.XXX < 0.45 — 횡보 레짐 진입 차단` 로그 확인
- **방법**: WARN.log 또는 SIGNAL 로그 grep
- **기준**: Hurst 값 로그에 표시 + 해당 분 진입 없음 확인

### [V56] ATR 차단 확인 [ATR 낮은 구간]
- **내용**: ATR < 1.0pt 구간에서 `[차단] ATR X.XXpt < 1.0pt — 변동성 부족` 로그 확인
- **참고**: 오늘(20260508) ATR=1.37pt였으므로 1.0pt 미만 구간은 더 약한 시장 — 차단 기대

---

## 즉시 확인 필요 (추가됨 2026-05-07 5차 세션)

### [DONE 2026-05-07] STRATEGY_PARAMS_GUIDE.md §1~§20 전체 준수 점검
- 93% 구현 확인. 실제 미구현 2건(strategy_events, shadow_ev) 이번 세션에서 구현 완료.
- VolatilityTargeter / DynamicSizer: 가이드 지시에 따라 "shadow test 후 적용" 의도적 보류 — 정상.

### [V49] shadow_candidate.json IPC 흐름 end-to-end 확인 [다음 장외 최적화 실행 후]
- **내용**: `param_optimizer.propose_for_shadow()` 실행 → `data/shadow_candidate.json` 생성 → 다음날 `daily_close()` → `_load_shadow_candidate()` → `ShadowEvaluator` 인스턴스화 로그 확인
- **방법**:
  1. CLI에서 `python backtest/param_optimizer.py --shadow` 실행
  2. `data/shadow_candidate.json` 파일 존재 확인 (candidate_version, candidate_params, wfa_sharpe 포함)
  3. 다음 일일 마감 후 WARN.log `[ShadowMode] ShadowEvaluator 초기화 완료` 확인
- **기준**: JSON 파일 생성 + 마감 로그에 shadow 초기화 출력

### [V50] strategy_events 테이블 기록 확인 [다음 버전 등록 또는 shadow 시작 시]
- **내용**: `strategy_registry.db`의 `strategy_events` 테이블에 `VERSION_REGISTERED`, `SHADOW_START`, `HOTSWAP_APPROVED/DENIED` 이벤트가 기록되는지 확인
- **방법**: `SELECT * FROM strategy_events ORDER BY id DESC LIMIT 10`
- **기준**: `event_type`, `event_at`, `message` 컬럼이 채워진 행 존재

### [V51] 전략 대시보드 이벤트 로그 표시 확인 [다음 실행]
- **내용**: `strategy_dashboard_tab.py` `_StrategyLog` 패널이 `strategy_events` 기반으로 갱신되는지
- **방법**: 대시보드 → 전략 탭 → 로그 패널에 한국어 이벤트 표시 확인
- **기준**: `버전 등록 | v1.0 | 2026-05-07 ...` 형태로 표시 (fallback: 버전 목록)

---

## 즉시 확인 필요 (추가됨 2026-05-07 4차 세션)

### [V47] 포지션 복원 버튼 동작 확인 [다음 모의투자 장중]
- **내용**: "포지션 복원" 버튼 클릭 → `PositionRestoreDialog` 표시 → 값 입력 후 복원 → 잔고 패널 갱신
- **방법**:
  1. 재시작 후 포지션 0.00 상태에서 버튼 클릭
  2. LONG / 진입가(pt) / 수량 / ATR 입력 후 "복원" 클릭
  3. WARN.log `[PositionRestore] 완료: ...  손절=X.XX  TP1=X.XX  TP2=X.XX` 확인
  4. 잔고 패널: 방향·진입가·평가손익 갱신 확인
- **기준**: WARN 로그 출력 + 패널 비FLAT 표시 + 쿨다운 미작동

### [V48] B60 수정 후 잔고 패널 수치 HTS 대조 확인 [다음 포지션 보유 중]
- **내용**: 합성 잔고행의 `총매매 / 평가손익 / 손익율` 이 HTS 수치와 ±5% 이내인지 확인
- **방법**: LONG 포지션 보유 중 HTS "선물 실시간 잔고" 패널 vs 미륵이 대시보드 잔고 패널 스크린샷 비교
- **기준**: 총매매 = entry_pt × qty × 250,000. 손익율(%) = pnl_krw / eval_krw × 100

### [V44/B62] 모의서버 startup sync FLAT 오염 해소 확인 [다음 재시작]
- **내용**: LONG 포지션 중 재시작 → `[BrokerSync] 모의투자 blank-rows → 저장 포지션 유지` WARN.log 확인
- **기준**: position_state.json `"status": "LONG"` 그대로 유지 (FLAT으로 덮어쓰지 않음)
- **실패 시**: GetServerGubun 호출 오류 여부 확인 (try/except → `_is_mock=False`로 fallback)

---

## 즉시 확인 필요 (추가됨 2026-05-07 3차 세션)

### [V42] SHORT 진입 Chejan 체결 확인 [다음 장중]
- **배경**: CB③(30분 정확도 <35%) 발동으로 이번 세션에서 SHORT 진입 없었음
- **내용**: SHORT ENTRY 주문 → Chejan 접수 → Chejan 체결 end-to-end 확인
- **방법**: WARN.log `[ChejanFlow] fill_qty>0 status=체결 kind=ENTRY SHORT` 확인
- **기준**: `[PendingOrder] clear` 가 타임아웃이 아닌 체결로 발생 (filled_qty>0 경로)

### [V43] B56 쿨다운 실제 차단 확인 [다음 ENTRY 미체결 시]
- **내용**: ENTRY 주문 미체결 소멸 후 `[EntryCooldown] ENTRY 미체결 소멸 → 2분 재진입 금지 until HH:MM:SS` WARN.log 출력 + 2분간 STEP 7 진입 차단
- **방법**: WARN.log에서 `[EntryCooldown]` 로그 확인 후 2분 이내 `[EntryAttempt]` 없음 확인
- **기준**: 이전처럼 매 2분마다 반복 진입 없음

### [B56 / BalanceChejanFlow] 조사 완료 [DONE 2026-05-07]
- 09:56~10:09 구간 gubun='1' 잔고 Chejan 이벤트 없음 확인 (WARN.log 전수 분석)
- balance Chejan FLAT 경로는 당시 미작동 → 비이슈 종료
- B56 적용으로 해당 경로도 이제 자동 쿨다운 처리됨

---

## 즉시 확인 필요 (추가됨 2026-05-06 추가 세션)

### [V35] B54 통합 파라미터 후 ENTRY/EXIT Chejan 체결 확인 [DONE 2026-05-07] (구: trade_type=4)
- **변경**: B47(trade_type=4)·B54(lOrdKind=1+slby_tp)로 두 번 수정됨. 현재 코드는 B54 기준
- **방법**: WARN.log `[ChejanFlow] fill_qty>0 status=체결` + `[PendingOrder] clear` 확인 (타임아웃 아닌 체결 clear)
- **확인 포인트**:
  - LONG 진입: `[주문요청] LONG` → Chejan 접수 → Chejan 체결 → `[PendingOrder] clear` (300s 이내)
  - SHORT 진입: `[주문요청] SHORT` → Chejan 접수(order_no 확인) → Chejan 체결 (B54 효과)
  - LONG EXIT: `[ExitAttempt]` → `[ExitSendOrderResult] ret=0` → Chejan 체결 → position FLAT
- **실패 시**: `[OrderDiag] SendOrderFO` 로그에서 slby_tp 값 확인 후 enc 파일 재조사

### [V32] SendOrderFO 실제 체결 확인 [DONE 2026-05-06]
- 진입 주문은 정상 체결됨 확인 (10:48, 10:50, 11:35 체결 로그). EXIT 주문 미체결은 trade_type=2(신규매도) 오류 때문. B47 수정으로 해결 (trade_type=4 매도청산 전환).

### [V33] Fix B 낙관적 오픈 진단 확인 [DONE 2026-05-06]
- 14:28:00 `[FixB] 낙관적 오픈 완료 direction=LONG status=LONG qty=1 optimistic=True` 로그 WARN.log에서 확인됨.

### [V34] 프로그램매매 FID 확정 [다음 장중]
- **내용**: `P00101` 타입='프로그램매매' FID 202/204/210/212/928/929 의미 확인
- **방법**: PROBE.log `[PROBE-ALLRT-FIDS] type='프로그램매매'` 재확인. FID 928/929는 프로그램 매수/매도 누적 순매수금액 추정
- **활용**: FID 확정 시 `_on_receive_real_data()`에 프로그램매매 실시간 파싱 경로 추가 가능

---

## 즉시 확인 필요 (추가됨 2026-05-06)

### [V30] OPW20006 BrokerSync 정상 동작 확인 [DONE 2026-05-06]
- SYSTEM.log에서 `[BrokerSync] OPW20006 rows=1` 확인됨. 레코드명 `선옵잔고상세현황` 수정 성공.

### [V31] Fix B 이중진입 방지 확인 [DONE 2026-05-06]
- 14:28:00 `[FixB] 낙관적 오픈 완료` 로그 확인됨. 이후 분봉에서 이중진입 없음 (LONG 상태 유지 중 재진입 차단 동작).

---

## 즉시 확인 필요 (추가됨 2026-05-04 야간 2세션)

### [V26] Kiwoom SendOrder 실제 체결 확인 [SUPERSEDED → V32]
- SendOrder가 SendOrderFO로 교체됨 (2026-05-06). V32로 대체됨.

### [V27] TP1/TP2 부분 청산 API 동작 확인 [다음 장중 포지션 보유 후]
- **내용**: TP1 도달 시 `_execute_partial_exit(price, stage=1)` 호출 → 33% 청산 주문 전송
- **방법**: TRADE 로그 `[Position] 부분청산 N계약 @ XXXX | 잔여=M계약` 확인
- **기준**: `partial_1_done=True` + Kiwoom 체결 내역 + trades.db PARTIAL 레코드

### [V28] 주문/체결 탭 실데이터 메트릭 표시 확인 [다음 실행]
- **내용**: 상단 `당일 거래` / `평균 지연` / `최대 지연` / `수신 횟수` 가 실데이터로 갱신되는지
- **방법**: 대시보드 실행 → 주문/체결 탭 → 분봉 처리 후 수치 변화 확인
- **기준**: "——" 대신 숫자 표시 (지연 ms 단위, 수신 횟수 증가)

### [V29] 로그 좌측 정렬 시각 확인 [다음 실행]
- **내용**: 주문/체결·손익·모델AI 탭 로그가 좌측 정렬로 출력되는지
- **방법**: 대시보드 실행 후 각 탭에서 로그 텍스트 정렬 확인
- **기준**: 구분선만 중앙 정렬, 나머지 모든 로그 좌측 정렬

---

## 즉시 확인 필요 (추가됨 2026-05-04 야간)

### [V22] opt50008 행 구조 확인 — 투자자별 vs 시간별 [다음 장중]
- **배경**: KOA Studio에서 opt50008 = 프로그램매매추이차트요청 확인. 출력: 체결시간·투자자별순매수금액
- **미확인**: 행이 투자자 유형별(개인/외인/기관...)인지 vs 시간대별인지 구조 불명
- **방법**: 다음 장중 DATA.log에서 `[TR-DISCOVER] opt50008 첫수신 rows=N fields=[...]` 확인
  - rows=10이면 투자자별(INVESTOR_KEYS 순서) 가능성 높음
  - rows=수십~수백이면 시간별 시계열로 판단 → 파싱 로직 수정 필요
- **기준**: `program_foreign_net_krw` 피처가 0이 아닌 값으로 채워지면 파싱 성공

### [V25] fetch_program_investor() 정상 동작 확인 [다음 장중]
- **내용**: opt50008 호출 성공 + `_program_investor` 캐시에 값이 채워지는지
- **방법**: DATA.log `[Investor] 프로그램투자자별 rows=N | 외인=±X 개인=±Y (KRW)` 확인
- **기준**: rows > 0 AND 외인/개인 값 중 하나라도 0이 아님
- **실패 시**: screen_no 충돌 가능성 — 2013 → 다른 번호로 변경

### [V23] 프로그램매매 실시간 FID 캡처 [다음 장중]
- **내용**: code=`P00101` type=`프로그램매매` FID 스캔 — 차익/비차익 순매수 FID 번호 확인
- **방법**: 장중 PROBE.log `[PROBE-ALLRT-FIDS] type='프로그램매매'` 항목 확인
- **활용**: FID 확정되면 opt10060 TR 폴링 → 실시간 수신으로 교체 가능

### [V24] 투자자ticker 실서버 지원 확인 [실서버 전환 후]
- **내용**: 실서버 전환 후 `투자자ticker` 실시간 타입 동작 여부 확인
- **방법**: 실서버 연결 후 PROBE.log `[PROBE-ALLRT] type='투자자ticker'` 수신 확인
- **배경**: 모의투자 서버 — 8가지 코드 조합 전부 ret=0이나 데이터 없음. 실서버 전용 추정

---

## 즉시 확인 필요

### [V1] OPT50029 초기 분봉 로드 확인 [SUPERSEDED 2026-05-04]
- 모의투자 서버에서 OPT50029 rows=0 확인됨 — SetRealReg(A0166000) 전환으로 대체
- 실 서버 전환 시 OPT50029 초기 히스토리 로드 재확인 필요

### [V20] SGD 지속 학습 확인
- **내용**: 매분 LEARNING 로그에 `[SGD] N건 학습 | SGD비중=30% 50분정확도=xx%` 출력되는지
- **방법**: 5층 로그 > 학습 탭. 초기 학습 완료 이후 매분 갱신 확인
- **기준**: 50분정확도 값이 분 단위로 변화 (현재 1/3 확률 학습 시작 → 실데이터 누적 후 개선 기대)

### [V21] SGD 10m·30m 호라이즌 학습 확인
- **내용**: 10m·30m가 현재 미학습 — 해당 ts DB 레코드 없어서 건너뜀
- **방법**: 장 진행 1시간 후 LEARNING 로그에 `[OnlineLearner] 10m 초기 학습 완료` 출력 확인
- **기준**: 13:44 + 10분 = 13:54 분봉 처리 시 자동으로 학습됨

### [V19] OFI bid/ask 정상 수신 확인
- **내용**: `[DBG-F4]` 로그에서 `bid=XXX.XX ask=XXX.XX` 가 0이 아닌 값으로 표시되는지
- **방법**: 재시작 후 첫 분봉 확정 후 DEBUG 로그 확인
- **기준**: bid > 0 AND ask > 0 → `ofi.update_hoga()` 정상 호출됨
- **파일**: `collection/kiwoom/realtime_data.py` `_on_hoga_data()`

### [V18] 파이프라인 watchdog 정상 해제 확인 [DONE 2026-05-04]
- watchdog 임계값 90/150/240s 적용 + log_loss 크래시 해결로 파이프라인 정상 완료
- "1분 30초 미실행" 경보는 크래시 구간(13:36~13:41)에서만 발생 → 정상

### [V2] run_minute_pipeline 완전 검증 [DONE 2026-04-27]
- `on_candle_closed` 호출 확인됨, 파이프라인 진입 확인됨

### [V3] run_minute_pipeline 예측값 출력까지 완전 검증 [DONE 2026-04-28]
- tick→분봉→on_candle_closed→pipeline→LONG 1계약 @ 1008.2 확인
- [Ensemble] dir=+1 conf=76.8% grade=A / [Checklist] 6/9 통과 자동진입 확인
- 더미 모델 기반 — 예측값은 무의미, 파이프라인 연결만 확인

### [V4] STEP 8 청산 트리거 + trades.db 저장 확인 [DONE 2026-04-28]
- trades.db 2건: 12:44 -0.10pt 하드스톱, 12:46 -0.70pt 하드스톱 확인
- `[Position] 청산 LONG @ 1009.45 | PnL=-0.10pt` 로그 확인

### [V5] STEP 9 predictions.db 저장 확인 [DONE 2026-04-28]
- predictions.db 30행 확인 (12:29·12:30 각 6 호라이즌)

---

---

## 즉시 확인 필요 (추가됨 2026-04-29)

### [V9] 다이버전스 패널 외인 데이터 표시 확인
- **내용**: 재시작 후 "외인 콜순매수", "외인 풋순매수", "다이버전스" 카드가 실제 값 표시하는지
- **방법**: 파이프라인 실행 후 `[Investor]` 로그 + 대시보드 다이버전스 탭 확인
- **기준**: "——" 대신 숫자 표시 (시뮬: 랜덤, 실거래: TR 실데이터)

### [V10] 진입 관리 탭 체크리스트 표시 확인
- **내용**: 체크리스트 아이콘이 V/X/— 3가지 상태 올바르게 표시되는지
- **조건 1**: 장 중 FLAT 상태 → V/X 표시 (체크리스트 평가됨)
- **조건 2**: 포지션 보유 중 또는 EXIT_ONLY 구간 → — 표시 (평가 안 됨)
- **V10a**: "산출 수량" N계약 표시 확인 (기존: "——" 고정)
- **V10b**: "당일 진입 통계" 매분 갱신 확인 (진입 0회→N회 업데이트)

---

## 즉시 확인 필요 (추가됨 2026-04-28)

### [V6] ATR 플로어 적용 후 진입 품질 확인 [DONE 2026-04-28]
- stop_dist=0.75pt 로그에서 정확히 확인됨
- `[DBG-F4]` ATR floor + `[DBG-STOP]` 하드스톱 발동 경로 모두 검증

### [V7] 포지션 복원 로그 확인
- **내용**: LONG 중 재시작 → `[Position] 이전 포지션 복원: LONG 1계약 @ XXXX` 로그
- **기준**: 재시작 후 FLAT 상태가 아닌 기존 포지션 유지

### [V8] CVD tick test 효과 검증
- **내용**: buyvol/sllvol이 실제로 분리되는지 확인 (이전엔 항상 buyvol=100%)
- **방법**: `[DBG-F4]` 로그에서 `buyvol`/`sllvol` 값이 다양하게 분포하는지 확인
- **기준**: 상승 틱에서 buy_vol > 0, 하락 틱에서 sell_vol > 0으로 분리됨

---

## 즉시 확인 필요 (추가됨 2026-04-30 자가학습 연결 세션)

### [V11] SGD 학습 로그 확인 [DONE 2026-05-04]
- 13:44 재시작 2분 후 1m/3m/5m/15m 초기 학습 완료 확인
- 이전 세션 DB 레코드 활용 (features 예측 당시 저장 → 올바른 supervised learning)

### [V12] GBM 일일 마감 재학습 확인 (15:40)
- **내용**: `daily_close()` 호출 시 `[GBM] 일일 마감 재학습 완료` 또는 `건너뜀` 로그
- **방법**: 15:40 이후 학습 탭 로그 확인
- **기준**: raw_candles 5000행 미만이면 "건너뜀", 이후엔 재학습 완료

### [V13] features 전체 저장 확인
- **내용**: predictions.db의 features 컬럼이 이제 20개 이상 피처를 저장하는지 확인
- **방법**: `SELECT length(features) FROM predictions LIMIT 5` — 기존 20개(~400자) → 전체(~1000자 이상)

### [V14] 🎯 효과 검증기 패널 표시 확인
- **내용**: "🎯 효과 검증" 탭이 정상 렌더링되는지 확인
- **방법**: 대시보드 실행 → 중앙 탭 6번째 "🎯 효과 검증" 클릭
- **조건 1**: 체결 완료 거래 0건 시 → "데이터 수집 중 (0건 체결)" 배너 표시
- **조건 2**: 체결 완료 거래 10건 이상 시 → 캘리브레이션·등급별·레짐별 테이블 수치 표시
- **조건 3**: 5분 주기 갱신 (패널이 빈 "——" 상태에서 수치로 전환되는지)

---

## 즉시 확인 필요 (추가됨 2026-04-30 이번 세션)

### [V15] 자동 종료 슬랙 알림 + 프로그램 종료 확인
- **내용**: 15:40 `daily_close()` 완료 후 슬랙 알림 수신 + 15초 후 프로그램 실제 종료
- **방법**: 테스트용 시간 임시 변경 (`datetime.time(15, 40)` → 현재 시간) 또는 실제 15:40 대기
- **기준**: 슬랙 알림 2건(일일 요약 + 종료 안내) + 15초 후 대시보드 창 닫힘

### [V16] 성장 추이 탭 렌더링 확인
- **내용**: "📈 성장 추이" 탭 7번째 탭이 정상 표시되는지
- **방법**: 대시보드 실행 → 중앙 탭 7번째 "📈 성장 추이" 클릭
- **조건 1**: 체결 데이터 0건 시 → "데이터 없음" 표시
- **조건 2**: 체결 데이터 있으면 일별/주별/월별/연간 탭에 집계 행 표시
- **조건 3**: 시작 500ms 후 선조회 동작 확인 (콘솔 오류 없이)

### [V17] daily_stats 스냅샷 저장 확인
- **내용**: 15:40 일일 마감 후 `trades.db`의 `daily_stats` 테이블에 당일 행 삽입 확인
- **방법**: `SELECT * FROM daily_stats ORDER BY date DESC LIMIT 5`
- **기준**: 오늘 날짜의 행이 trades·wins·pnl_krw·sgd_accuracy 포함하여 저장

---

## 예정된 작업

### [T1] 모의투자 4주 운영
- **전제**: [V1], [V2] 확인 완료 후
- **기준** (4주 완료 시 실전 전환 가능):
  - 통산 수익률 양수
  - Circuit Breaker 1회 이상 정상 작동
  - 일일 수익률 변동성 안정적

### [T2] Circuit Breaker 5종 트리거 테스트
- 각 트리거를 의도적으로 발동시켜 정지·청산 동작 확인
- `safety/circuit_breaker.py` + `safety/emergency_exit.py`
- **주의**: 중복발동 버그 수정됨 (2026-04-30) — 이제 PAUSED/HALTED 상태에서 재발동 없음
- **확인 포인트**: 발동 1회만 슬랙 전송되는지 + 대시보드 SYSTEM탭/경보탭에 표시되는지

### [T3] Walk-Forward 검증 (26주 데이터 필요)
- **기준**: Sharpe ≥ 1.5, MDD ≤ 15%, 승률 ≥ 53%
- `backtest/walk_forward.py` — 8주 학습 / 1주 검증 반복
- 실거래 데이터 26주 확보 후 실행

### [T4] ResearchBot → main.py 연결 (장외 자동 리서치)
- `research_bot/alpha_scheduler.py` — 16:00 자동 실행 스케줄러
- main.py에 연결하여 장외 자동 활성화
- **주의**: 자동 통합은 절대 금지 — 팝업 알림 + 사용자 검토 후 수동 통합

### [T5] PPO 정책 검증 — Sharpe +0.4 목표
- 실거래 데이터 확보 후 `learning/rl/policy_evaluator.py`로 평가
- 정적 규칙 대비 Sharpe +0.4 이상 확인 후 실전 적용

---

## 알려진 잠재 이슈

### [P0] [DBG] 출력문 정리 예정
- `api_connector.py`, `realtime_data.py`, `main.py`에 디버그 print 잔존
- 파이프라인 안정 확인 후 일괄 제거 (시스템 안정 전 제거 금지)

### [P1] GetMasterCodeList("10") — 모의투자 서버 빈값
- 모의투자 서버에서 None/빈값 반환 가능 (실 서버에서는 정상)
- `GetFutureCodeByIndex(0)` 추가로 우선순위 보완됨 — 해결됨

### [P2] py37_32 패키지 호환성
- scipy 1.5.4 고정 필수 (1.7.x DLL 충돌)
- torch 설치 시 32-bit 호환 버전 확인 필요 (PPO GPU 가속 미사용 시 numpy fallback)

### [P3] 뉴스 감성 분석 — HF API 연결 실패 시 fallback
- `features/sentiment/kobert_sentiment.py`: HF API 오프라인 시 키워드 사전 fallback
- 실전 환경에서 fallback 동작 확인 필요

### [P4] 알파 풀 JSON 파일 증가
- `research_bot/alpha_pool.py`: MAX_ACTIVE=50 제한 있으나 퇴역 알파 파일 관리 정책 미확정

### [P6] FID_BID_PRICE=41 / FID_ASK_PRICE=51 명칭 역전 의심
- KOA 개발가이드에서 FID 41=매도1호가, 51=매수1호가 가능성 시사
- 현재 constants.py는 41=BID(매수), 51=ASK(매도)로 정의됨
- ofi.py에서 매수/매도 방향 계산에 사용 중 — 역전이면 OFI 방향 반전 버그
- **수정 전 반드시**: ofi.py 계산 방향 확인 후 결정 (섣부른 수정 금지)

### [P5] bid/ask = 0 — OFI 영구 0 [DONE 2026-05-04]
- 선물호가잔량 콜백 `_on_hoga_data()` 신설 + `sopt_type="1"` 추가 등록으로 해결
- 모의투자 서버에서 선물호가잔량 수신 확인됨 (로그에서 확인)
- **검증 필요**: [V19] 재시작 후 `[DBG-F4]` 에서 bid/ask 값 확인
## 2026-05-07 세션 후속

### DONE 처리
- [DONE 2026-05-07] **[B52]** ENTRY 타임아웃 시 낙관적 포지션 FLAT 복원 구현 (`main.py` L544). **[V39] 장중 동작 확인** ✅
- [DONE 2026-05-07] **[V35/V41]** B54(lOrdKind=1+slby_tp) 완전 검증 — LONG 진입/EXIT 즉시 체결. PnL 배수 500,000원/pt 확인
- [DONE 2026-05-07] **[B49]** EXIT 경로 진단 로그 추가 — 하드스톱/시간청산 앞뒤에 `[ExitAttempt]` + `[ExitSendOrderResult]` 추가
- [DONE 2026-05-07] **[B50]** price_hint float 오차 수정 — `round(exit_price, 2)` 적용 (하드스톱/시간청산)
- [DONE 2026-05-07] **[B53]** ENTRY 타임아웃 후 2분 쿨다운 구현 — `_entry_cooldown_until` 설정 + STEP 7 진입 조건 차단 + `[EntryCooldown]` 차단 로그 + `[차단] ENTRY 타임아웃 쿨다운` 이유 로그
- [DONE 2026-05-07] **BrokerSync CRITICAL → WARNING** — position_state.json 잔여로 매 시작 시 CRITICAL 출력되던 것 WARNING으로 완화 (blank rows FLAT 처리는 정상 동작)
- [DONE 2026-05-07] **[B54]** SendOrderFO 파라미터 통일 — `api_connector.send_order_fo(slby_tp="")`추가. 모든 진입/청산/긴급청산을 `lOrdKind=1(신규매매) + sSlbyTp` 방향 명시로 변경. trade_type=2(SHORT)가 new convention에서 "정정"으로 해석되어 서버 조용히 거부되는 원인 해결
- [DONE 2026-05-07] **[EntrySendResult]** `log_manager.system()` 추가 — `_ts_execute_entry` 내 ret 값이 대시보드 SYSTEM 탭에 표시됨 (기존: file logger만)

### [V41] B54 SHORT/EXIT Chejan 정상 수신 확인 [DONE 2026-05-07]
- LONG 진입 즉시 체결 (접수+체결 10:14:00 동시) ✅
- LONG EXIT 즉시 체결 (접수+체결 10:34:01 동시), `[ExitAttempt]`/`[ExitSendOrderResult]` 정상 ✅
- SHORT 진입은 이번 세션에서 미발생 (CB ③ 발동으로 당일 정지). SHORT Chejan 검증은 다음 세션

### 다음 실행 최우선 검증

### [V39] B52 ENTRY 타임아웃 복원 동작 확인 [다음 장중]
- **내용**: ENTRY 체결 안 됨 → 60s 타임아웃 → `[FixB] ENTRY 타임아웃 → 낙관적 포지션 FLAT 복원` 로그 확인
- **기준**: WARN.log에 `[FixB] ENTRY 타임아웃` 로그 + 이후 position.status=FLAT + EXIT 루프 미발생
- **실패 시**: `_optimistic` 플래그 설정 시점 (`position_tracker.py`) 재확인 필요

### [V40] EXIT 경로 진단 로그 확인 [다음 포지션 청산 시]
- **내용**: 하드스톱/시간청산 발동 시 `[ExitAttempt]` → `[ExitSendOrderResult] ret=0` 로그 순서 확인
- **기준**: ret=0이면 `[PendingOrder] set EXIT_FULL`, ret≠0이면 `[Exit] ... 주문 실패` 로그
- **활용**: EXIT 무응답 시 ret 값으로 키움 API 오류 코드 즉시 특정 가능

## 2026-05-06 세션 후속

### DONE 처리
- [DONE 2026-05-06] BrokerSync startup 차단 원인 1차 규명
- [DONE 2026-05-06] 주문/체결/복원 디버그 관측점 대폭 추가
- [DONE 2026-05-06] 포지션 state 저장 메타(`last_update_reason`, `last_update_ts`) 추가

### 다음 실행 최우선 검증
- [V30] blank placeholder `OPW20006` 응답이 실제로 FLAT 판정으로 해석되는지 검증
- [V31] `ret=-302` 또는 주문 실패 상황에서 로컬 LONG 오픈/복원 불일치가 재발하는지 검증
- [V32] `EntryAttempt -> PendingOrder -> OrderMsgDiag -> ChejanFlow -> PositionDiag` end-to-end 인과관계 검증

### 새 작업
- [T6] startup sync 이후 신규 진입 gate 정책 재검토 (`verified=False`와 `blank row`를 분리)
- [T7] 디버그 로그 정리 단계 준비 (유효 관측점 유지, 과도한 로그는 다음 안정화 후 축소)
## 2026-05-06 세션 마감 반영

### [V36] 실시간 잔고 패널 UI 재구성 + 대괄호 제거 [DONE 2026-05-06]
- 좌측 컬럼 2단 분할, `실시간 잔고` 카드/게이지/합계 6개/잔고 테이블 추가 완료.
- 헤더 `계좌번호`, `전략명` 콤보 정렬 완료.
- 합계칸 `[ ]` 플레이스홀더 제거 완료.

### [V37] OPW20006 blank summary fallback 적용 [DONE 2026-05-06]
- `OPW20006` summary가 전부 blank일 때도 상단 패널이 비지 않도록 fallback 적용 완료.
- `총매매/총평가손익/총평가`는 잔고행 합산, `실현손익`은 `daily_stats().pnl_krw`, `총평가수익률/추정자산`은 계산값/0 기반으로 채움.

### [V38] 실시간 잔고 원본값 검증 + 전용 계좌합계 TR 분리 검토 [다음 세션]
- **내용**: `OPW20006`이 장후/무포지션에서 summary/rows를 모두 비우는 케이스가 확인되었으므로, 합계 6개를 전용 계좌합계 TR로 분리할지 검토.
- **방법**: 장중/장후 각각에서 `OPW20006-SUMMARY-BLANK`, `BalanceUIFallback` 로그와 화면값 비교.
- **기준**: 장중에도 summary blank가 반복되면 `총매매/총평가손익/실현손익/총평가/총평가수익률/추정자산` 전용 TR 추가 구현.
---

## 2026-05-07 Log Review Update (after 2026-05-06 10:14)

### DONE / outcome reflected

- [DONE 2026-05-07] **[V30] BrokerSync blank placeholder handling verified**
  - Evidence:
    - `2026-05-06 14:11:20 [BrokerSync] raw rows=1 nonempty_rows=0 all_blank_rows=True`
    - `2026-05-06 14:11:20 [BrokerSyncFlatPlaceholder] ... before='FLAT'`
    - `2026-05-06 14:11:20 [BrokerSync] status verified=True block_new_entries=False reason=blank/no holdings response interpreted as flat`
  - Conclusion:
    - blank placeholder row is no longer treated as hard mismatch
    - startup no longer blocks new entries in this case

- [DONE 2026-05-07] **[V32] Entry -> pending -> Chejan acceptance chain verified for live path**
  - Evidence:
    - `2026-05-06 14:28:00 [EntryAttempt]`
    - `2026-05-06 14:28:00 [EntrySendOrderResult] ret=0`
    - `2026-05-06 14:28:00 [PendingOrder] set kind='ENTRY'`
    - `2026-05-06 14:28:00 [ChejanFlow] ... status='접수' order_no='0076887'`
    - `2026-05-06 14:28:00 [ChejanMatch] pending_matched=True`
  - Conclusion:
    - request -> pending -> Chejan order acceptance path is now observable end-to-end
    - remaining gap is not "no Chejan at all" but delayed/missing fill on some orders

### Still open / narrowed by log review

- [OPEN 2026-05-07] **[V31] historical local/broker mismatch around 10:48:19 still not fully explained**
  - Evidence:
    - `2026-05-06 10:48:19 [WARN] [Entry] ... ret=-302`
    - `2026-05-06 10:48:19 [TRADE] [Position] 진입 LONG 1계약 @ 1124.1`
    - `2026-05-06 10:48:31 [Position] 이전 포지션 복원`
  - Current judgment:
    - this mismatch is historical and predates the later diagnostics/fixes
    - do not treat it as reproduced after the 14:11 restart

- [OPEN 2026-05-07] **[V41] SHORT entry and EXIT Chejan fill still need dedicated proof**
  - What is verified now:
    - LONG entry acceptance Chejan exists
    - LONG exit final fill Chejan exists at `2026-05-06 15:24:58`
  - What is still missing:
    - clean SHORT entry case with `status='접수'` and matched order number
    - clean SHORT exit fill case

- [OPEN 2026-05-07] **[V42] EXIT pending timeout loop root cause narrowed to fill latency / no immediate fill**
  - Evidence:
    - from `2026-05-06 14:29:00` to `15:24:01`, repeated:
      - `PartialExitAttempt` / `PartialExitSendOrderResult ret=0`
      - `PendingOrder set`
      - timeout clear after about 1-2 minutes
    - first actual exit acceptance/fill only appears at `2026-05-06 15:24:58`
  - Conclusion:
    - this is no longer pointing first at `trade_type` mismatch
    - likely remaining issue is one of:
      - mock-server fill/accept delay
      - wrong/ambiguous FO parameter combination on some exit paths
      - pending timeout policy being too aggressive before broker response

- [OPEN 2026-05-07] **[V43] ENTRY timeout clear still releases retry too early when only Chejan acceptance exists**
  - Evidence:
    - `2026-05-06 14:28:00` entry receives Chejan `status='접수'` with order number
    - but pending is cleared at `14:29:00` with `filled_qty=0`
    - system then moves on immediately into exit logic because optimistic LONG remains open
  - Risk:
    - acceptance without fill can still leave local state ahead of broker reality
  - Next check:
    - distinguish `accepted(order_no assigned)` from `filled(fill_qty > 0)` in timeout handling

- [OPEN 2026-05-07] **[V38] balance summary fallback still operationally necessary**
  - Evidence:
    - `2026-05-06 18:51:29 [BalanceUIFallback] summary blank from OPW20006; rows=0`
  - Conclusion:
    - startup flat interpretation is fixed
    - summary fields from `OPW20006` are still not reliable enough to retire fallback

### Immediate next tasks

- [T8] split pending order state into `accepted` vs `filled`
  - Goal:
    - when `order_no` is assigned by Chejan, mark accepted and do not recycle the order as if nothing happened
  - Priority:
    - highest

- [T9] review ENTRY/EXIT timeout policy
  - Goal:
    - stop 1-minute timeout clears from causing repeated resend loops while broker-side order is still live
  - Check against:
    - `14:28:00 -> 14:29:00` ENTRY
    - `14:29:00 -> 15:24:58` EXIT loop

- [T10] verify one clean SHORT scenario end-to-end
  - Need logs for:
    - `EntryAttempt`
    - `EntrySendOrderResult ret=0`
    - `ChejanFlow status='접수'`
    - `ChejanFlow status='체결'` or explicit non-fill evidence

- [T11] verify whether `gubun='4'` is now safely ignorable in active code path
  - Historical log still shows `gubun='4'` noise on 2026-05-06
  - Need next-run proof that logic ignores it without side effects

### 2026-05-07 balance UI wiring update

- [DONE 2026-05-07] **[B57] broker balance summary now uses auxiliary Kiwoom futures TRs**
  - `request_futures_balance()` now keeps `OPW20006` as canonical row source
  - added auxiliary summary enrichment from:
    - `OPW20007`: `약정금액합계`, `평가손익합계`, `청산가능수량`
    - `OPW20008`: `추정예탁총액` / `예탁총액`
    - `OPW20003`: `총손익`, `수익율`, `예탁총액`
  - goal:
    - HTS 상단 요약값이 비어도 미륵이 실시간잔고 UI summary가 따라오게 연결

- [NEXT 2026-05-07] **[V44] live verification on account balance panel**
  - confirm dashboard summary updates from broker values:
    - `실현손익`
    - `추정자산`
    - `총매매`
    - `총평가손익`
  - confirm position row still maps correctly for startup broker sync:
    - `종목코드`
    - `매매구분`
    - `잔고수량`
    - `주문가능수량`

- [NEXT 2026-05-07] **[V45] validate OPW20003 input convention in live/mock environment**
  - current assumption:
    - `시장구분="0"` with same-day `시작일자/종료일자`
  - if `OPW20003` returns blank/None in practice:
    - capture request/response log
    - verify exact Kiwoom convention from local enc / guide notes
    - adjust without breaking `OPW20006/20007/20008` path

- [CHECK 2026-05-07] **12:13 restart log verdict**
  - `2026-05-07 12:13:48` proves the new auxiliary probes are wired:
    - `OPW20007.*`
    - `OPW20008.*`
    - `OPW20003.*`
  - but all values are still blank at restart, so startup-only balance UI improvement is not yet confirmed

- [DONE 2026-05-07] **[B58] refresh balance UI immediately after normal fill flows**
  - added `_ts_refresh_dashboard_balance(self)` after:
    - `EntryFillFlow`
    - `ExitFillFlow` final
    - `ExitFillFlow` partial/remaining
  - reason:
    - 12:15~12:18 logs show fills are normal, but no balance refresh is triggered because `gubun='1'` balance Chejan is absent

- [NEXT 2026-05-07] **[V46] verify post-fill balance refresh logs after next run**
  - expected after next fill:
    - balance TR request/response logs right after `EntryFillFlow` or `ExitFillFlow`
    - dashboard summary no longer stuck at startup zeros
## 2026-05-08 Ensemble Upgrade session close-out

### DONE reflected today

- [DONE 2026-05-08] `ENSEMBLE_SIGNAL_UPGRADE_PLAN.md` 에 `Update Status`, `Next Work`, `Effect Validation Checklist` 반영
- [DONE 2026-05-08] 대시보드 중간 패널에 `A/B / Calibration / Meta Gate / Rollout` 효과 검증 탭 추가
- [DONE 2026-05-08] 네 리포트 자동 주기 실행 연결
  - `Calibration / Meta Gate / Rollout`: 15분
  - `A/B`: 30분
- [DONE 2026-05-08] `effect_monitor_history.json` 추이 스냅샷 저장 시작
- [DONE 2026-05-08] `EfficacyPanel` 탭 툴팁 오배선 버그 수정 및 실제 툴팁 표시 검증 완료
- [DONE 2026-05-08] `predictions` 원확률 저장, `ensemble_decisions` gating/toxicity/meta 저장, `MICRO-MINUTE <-> raw_features` 대조 경로까지 검증 완료

### NEXT priority

- [NEXT 2026-05-09] horizon별 `temperature scaling` 도입
  - 목표: `ECE 0.399783` 개선
  - 결과물: calibration before/after 비교 리포트

- [NEXT 2026-05-09] A/B negative delta 원인 분석
  - 현재: `pnl delta=-3.60pt`, `accuracy delta=-0.10%p`, `changed sample=53`
  - 목표: 어떤 gating / microstructure 신호가 손익 악화에 기여했는지 구간별 분석

- [NEXT 2026-05-09] `meta_labels` 추가 축적 후 threshold 재튜닝
  - 현재 표본: `34`
  - 목표: `take/reduce/skip` 임계값 재추천 및 실제 손실 회피 효과 검증

- [NEXT 2026-05-09] rollout 승격 재평가
  - 현재 추천 단계: `shadow`
  - 승격 조건: calibration 개선 + meta 표본 증가 + A/B 재개선 확인

- [NEXT 2026-05-09] toxicity gate 장중 발동률 집계
  - `pass/reduce/block` 저장분이 다음 장중부터 누적되므로 실제 분포 확인 필요

---
