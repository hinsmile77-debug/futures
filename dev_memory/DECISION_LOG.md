# 설계 결정 및 버그 근본 원인 로그 — futures (미륵이)

---

## 2026-05-06 버그 수정

### [B45] OPW20006 GetCommData 전부 blank — 레코드명 오타 2자
**파일**: `collection/kiwoom/api_connector.py`
**증상**: `GetRepeatCnt("OPW20006", "선옵잔고상세현황")` = 0, `GetCommData` 전부 빈 문자열 반환
**원인 (2중 오타)**:
- 멀티 레코드명 `선옭잔고상세현활` — `옵`(→`옭`) + `황`(況→`활`活) 두 글자 모두 틀림
- GetRepeatCnt 2번째 파라미터가 잘못된 레코드명이면 0 반환 → 전체 루프 미실행
**확인 방법**: `C:\OpenAPI\data\opw20006.enc` (ZIP → `OPW20006.dat` CP949) 직접 조회 → `@START_선옵잔고상세현황` 확인
**Fix**: `_MULTI_RECORD = "선옵잔고상세현황"`, `_SINGLE_RECORD = "선옵잔고상세현황합계"` enc 파일 기준으로 교체
**추가 수정**: `보유수량` 삭제(OPW20006에 없음), `잔고수량` 복원(enc offset 66 확인), `조회건수` 교차검증 추가
**교훈**: 한글 오타는 육안으로 구별 불가 → 레코드명 문제 의심 시 즉시 enc 파일 확인.

---

## 2026-05-06 설계 결정

### [D21] 키움 TR 조사 표준: enc 파일 우선
**결정**: TR 필드/레코드명 문제 발생 시 키움 CS 문의나 Q&A 검색보다 `C:\OpenAPI\data\<tr코드소문자>.enc` 파일을 먼저 조회.
**이유**: 2026-05-06 OPW20006 조사에서 CS 답변("잔고수량 없음")이 틀렸고 enc 파일이 정확함을 확인. enc 파일은 KOA SDK 설치 시 포함되며 실제 API 동작의 진실 원천.
**절차**: enc=ZIP → 내부 `.dat`(CP949) → `@START_레코드명` → 필드명 탭구조. 전체 절차: `dev_memory/kiwoom_api_tr_investigation.md`.

### [D22] 낙관적 포지션 오픈 패턴 (`_optimistic` 플래그)
**결정**: `SendOrder ret=0` 직후 `position.open_position()` 호출 + `_optimistic=True` 설정. Chejan 체결 콜백이 수신되면 `apply_entry_fill()`의 보정 경로로 가격만 업데이트(수량 증가 없음). Chejan 미수신(모의투자) 시엔 낙관적 오픈 그대로 유지.
**이유**: 모의투자 서버는 Chejan 없이 진입 후 같은 방향 신호가 다음 분봉에 재발생하면 이중 오픈 가능. `_optimistic` 플래그로 두 경로(Chejan 있음/없음)를 단일 포지션으로 수렴.
**한계**: 실서버에서 Chejan이 다른 가격으로 오면 entry_price가 보정됨 — 슬리피지 측정에 유리. 단, 주문 거부(ret≠0) 시 `open_position()` 호출 전 return되므로 오픈 안 됨.

---

## 2026-05-04 버그 수정 (야간 2세션)

### [B42] Kiwoom 주문 전달 누락 — 4회 거래 로그, Kiwoom 0건
**파일**: `collection/kiwoom/api_connector.py`, `strategy/entry/entry_manager.py`, `strategy/exit/exit_manager.py`, `main.py`
**증상**: TRADE 로그에 4회 진입/청산 기록 있으나 Kiwoom 모의계좌 잔고에 체결 내역 전혀 없음
**원인 (3중 복합)**:
1. `api_connector.py`에 `send_order()` 메서드 없음 → `EntryManager._send_order()` / `ExitManager._send_close_order()`가 `self._api.send_order()` 호출 시 `AttributeError`
2. `entry_manager.py`/`exit_manager.py` `acc_no = ""` — 빈 계좌번호 (발견되었으나 1번 오류로 도달 불가)
3. `main.py`에서 `EntryManager`/`ExitManager` 미사용 — `position.open_position()` / `close_position()` 직접 호출 → API 주문 경로 자체 없었음
**Fix**:
- `api_connector.py`: `send_order(rqname, screen_no, acc_no, order_type, code, qty, price, hoga_gb, org_order) -> int` 추가
- `entry_manager.py`/`exit_manager.py`: `acc_no = _secrets.ACCOUNT_NO`
- `main.py`: `_send_kiwoom_entry_order()` / `_send_kiwoom_exit_order()` 헬퍼 추가. 진입/청산 직전 호출

### [B43] 부분 청산 미완성 — flag 세우기만, 실제 청산 없음
**파일**: `strategy/exit/exit_manager.py`, `strategy/position/position_tracker.py`, `main.py`
**증상**: `is_tp1_hit()` 조건 충족 시 `partial_1_done = True` 만 기록, 주문 미전송 + 수량 미감소
**원인**: `exit_manager._execute_partial_exit()`가 수량 감소(`self._tracker.quantity -= partial_qty`)는 했으나 `partial_close()` 메서드가 `PositionTracker`에 없었음. trades.db INSERT / dashboard 갱신 경로도 없었음
**Fix**:
- `PositionTracker.partial_close(exit_price, qty, reason) -> Dict` 추가 (pnl 계산 + quantity 감소 + _save_state)
- `main.py._execute_partial_exit(price, stage)`: API 주문 → `position.partial_close()` → `partial_N_done=True` → `_post_partial_exit()`
- `_post_partial_exit(result, stage)`: CB/Kelly 기록 + trades.db INSERT + 대시보드 PnL 갱신

### [B44] QTextEdit 로그 가운데 정렬 — HTML div 미적용
**파일**: `dashboard/main_dashboard.py`
**증상**: `<div style="text-align:left;">` HTML 추가 후에도 로그가 가운데 정렬 유지
**원인**: `QTextEdit.append(html)` 메서드가 이전 블록의 Qt document alignment를 상속. `append_separator()`의 `text-align:center` CSS가 Qt document level 정렬 변경 → 이후 모든 `append()` 블록에 center alignment 전파. HTML CSS는 Qt 렌더링에서 Qt 수준 alignment보다 우선순위 낮음
**Fix**: `QTextCursor` + `QTextBlockFormat.setAlignment(Qt.AlignLeft)` — Qt document 수준에서 명시적 지정. `_insert_html_left()` / `_insert_html_center()` static 메서드로 분리

---

## 2026-05-04 설계 결정 (야간 2세션)

### [D18] send_order() → ret=0 즉시 포지션 반영 (OnReceiveChejanData 미구현)
**결정**: `SendOrder` ret=0(접수 성공) 시 즉시 `position.open_position()` / `close_position()` 호출. 실제 체결 확인(OnReceiveChejanData 콜백) 없이 진행.
**이유**: OnReceiveChejanData 콜백 구현은 체결가/슬리피지 측정에 필요하나, 시장가 주문(`hoga_gb="03"`)은 접수=체결로 간주해도 무방. 모의투자 단계에서 정확한 체결가보다 흐름 검증이 우선.
**미래 작업**: [T6] OnReceiveChejanData 구현 → 실체결가·슬리피지·지연 시간 정확 측정

### [D19] _KiwoomOrderAdapter — EmergencyExit 역방향 의존 해소
**결정**: main.py 모듈레벨에 `_KiwoomOrderAdapter(kiwoom_api, futures_code, acc_no)` 어댑터 정의. `EmergencyExit.set_order_manager(adapter)` 주입.
**이유**: `EmergencyExit`가 `KiwoomAPI`를 직접 참조하면 순환 의존 + 테스트 불가. 어댑터 패턴으로 인터페이스 격리. CB/KillSwitch 긴급청산도 동일 `send_order()` 경로 사용 가능.

### [D20] 슬리피지 지표 → 지연 지표로 대체 (임시)
**결정**: 주문/체결 탭 상단 메트릭을 슬리피지(실체결가-주문가) 대신 API 지연(LatencySync avg/peak ms)으로 표시.
**이유**: OnReceiveChejanData 없이 실체결가 알 수 없음. API 지연은 LatencySync로 이미 측정 중이며 슬리피지와 간접 상관 있음.
**복원 조건**: OnReceiveChejanData 구현 후 실체결가 vs 주문가 차이로 슬리피지 계산 → 메트릭 교체.

---

## 2026-05-04 버그 수정 (야간 세션)

### [B40] FID_OI = 291 치명적 오류 — 예상체결가를 미결제약정으로 사용
**파일**: `config/constants.py`, `collection/kiwoom/option_data.py`, `collection/kiwoom/realtime_data.py`
**증상**: 미결제약정(OI) 값이 ~207357이 아닌 ~1020.60 수준의 이상값 반환. OFI 계산 및 옵션 OI 전부 오염.
**원인**: `FID_OI = 291`은 `선물호가잔량` 타입의 FID로 **예상체결가** 필드. 미결제약정은 `선물시세` 타입의 FID 195.
PROBE-ALLRT-FIDS 스캔으로 확정:
```
선물호가잔량 FID 291 = '+1020.60'  → 예상체결가
선물시세    FID 195 = '207357'    → 미결제약정 (진짜 OI)
```
**Fix**:
- `constants.py`: `FID_OI = 291` → `195`. `FID_EXPECTED_PRICE = 291` 추가(명확한 명명).
- `option_data.py`: 하드코딩 291 두 곳 → `FID_OI` import 사용.
**교훈**: FID 번호는 실시간 타입(선물시세 vs 선물호가잔량)에 종속됨. 동일 FID가 타입마다 다른 데이터를 반환할 수 있음. PROBE 스캔 없이 FID 번호를 가정하면 안 됨.

### [B41] TR_INVESTOR_OPTIONS 잘못된 TR 연속 오류 → 옵션 수급 수집 포기
**파일**: `config/constants.py`, `collection/kiwoom/investor_data.py`
**증상**: 옵션 투자자별 콜/풋 순매수 데이터 항상 0 또는 빈값
**원인 탐색 과정**:
- 1차 시도 `opt50014` → KOA Studio 확인: 선물가격대별비중차트요청 (무관)
- 2차 시도 `opt50008` → KOA Studio 확인: 프로그램매매추이차트요청 (옵션 아님)
  - INPUT: 종목코드=P0010I(코스피), 시간구분=1, 거래소구분=1
  - OUTPUT: 투자자별순매수금액(KRW) — 콜/풋 구분 없음
- KOA Studio 전체 탐색 결과: 콜/풋 순매수를 투자자별로 제공하는 TR 없음
**최종 Fix**:
- `TR_INVESTOR_OPTIONS` 상수 삭제
- `fetch_options()` → 더미 고정, 코드에 "TR 없음" 명시
- opt50008은 `TR_PROGRAM_TRADE_INVESTOR`로 용도 변경 → 프로그램매매 투자자별 KRW 수집에 활용
**교훈**: KOA TR 명칭·용도는 번호로 추정하지 말고 KOA Studio에서 INPUT/OUTPUT 필드 직접 확인 필수.

---

## 2026-05-04 설계 결정 (야간 세션)

### [D15] 선물 FID 확정 매핑 (PROBE-ALLRT 스캔 기반)
**결정**: 아래 FID를 constants.py 상수로 확정.

| 상수 | FID | 실시간 타입 | 값(예시) |
|---|---|---|---|
| FID_OI | 195 | 선물시세 | 207357 (미결제약정) |
| FID_EXPECTED_PRICE | 291 | 선물호가잔량 | +1020.60 (예상체결가) |
| FID_KOSPI200_IDX | 197 | 선물시세 | +1049.66 (KOSPI200 지수) |
| FID_BASIS | 183 | 선물시세 | +1.04 (시장베이시스) |
| FID_UPPER_LIMIT | 305 | 파생실시간상하한 | +1078.35 (당일 상한가) |
| FID_LOWER_LIMIT | 306 | 파생실시간상하한 | -918.65 (당일 하한가) |

**이유**: PROBE-ALLRT-FIDS 실시간 스캔으로 실측 확인된 값. 기존 KOA 문서 번호와 다를 수 있으므로 실측 우선.

### [D17] 옵션 투자자별 TR 없음 확정 → opt50008 용도 전환
**결정**:
- 옵션 투자자별 콜/풋 순매수 TR은 KOA에 존재하지 않음. `fetch_options()`는 더미 고정.
- opt50008(프로그램매매추이차트요청)은 `TR_PROGRAM_TRADE_INVESTOR`로 전환:
  - `fetch_program_investor()` 신설 — 투자자별 프로그램매매 순매수금액(KRW) 수집
  - 피처 3개 추가: `program_foreign/institution/individual_net_krw`
**이유**: opt50008이 투자자 유형별 프로그램매매 KRW를 제공하므로, 옵션 대신 프로그램매매 수급 신호로 활용 가능. 외인 프로그램매매 순매수 방향은 단기 선물 방향과 상관관계 있음.
**미확인**: opt50008 행 구조(투자자별 순서 vs 시간별 시계열) — [V22] 다음 장중 TR-DISCOVER 로그로 확인 예정.

### [D16] PROBE-ALLRT 범용 실시간 타입 모니터링 패턴
**결정**: `api_connector._on_receive_real_data()`에서 신규 실시간 타입 첫 수신 시 FID 1~99, 100~400, 900~960 전수 스캔 후 PROBE.log에 기록.
**이유**: 키움 API는 실시간 타입별 FID 목록을 공식 문서로 완전하게 제공하지 않음. 실측이 유일한 확인 방법.
**발견된 신규 타입**: 파생실시간상하한(A0166000), 주식예상체결(A0166000·장마감후), 프로그램매매(P00101·FID 미확정), 선물옵션우선호가, 선물이론가
**유지 조건**: 파이프라인 안정화 후에도 PROBE 인프라는 유지 (실서버 전환 시 새 FID 발견 가능).

---

## 2026-05-04 버그 수정

### [B31] WARN 메시지 SYSTEM.log 혼재
**파일**: `utils/logger.py`, `dashboard/main_dashboard.py`
**증상**: WARNING 로그가 SYSTEM.log와 경보 탭 양쪽에 출력. 시스템 탭 노이즈.
**원인**: SYSTEM 파일핸들러에 레벨 상한 없음 → WARNING+ 모두 수신. 대시보드도 WARN 태그를 "all" + "warn" 양쪽에 기록.
**Fix**:
- `_MaxLevelFilter(max_level)` 클래스 추가. SYSTEM 핸들러에 `_MaxLevelFilter(logging.WARNING)` → INFO만 통과
- `warn_fh` TimedRotatingFileHandler 추가 (`YYYYMMDD_WARN.log`) WARNING+
- 대시보드 `append()`: WARN/ERROR/CRITICAL → `self.append("warn", ...)` 후 즉시 return (시스템 탭 미기록)

### [B32] OPT50029 모의투자 서버 rows=0
**파일**: `collection/kiwoom/realtime_data.py`, `main.py`
**증상**: 폴링 30초마다 `[POLL] rows=0 — 빈 응답` — 분봉 미수신
**원인**: 키움 모의투자 서버는 OPT50029(선물분차트요청) 응답 데이터 미제공. 실 서버 전용.
**Fix**: 폴링 방식 포기 → SetRealReg 실시간 구독 방식으로 전환 (`is_mock_server=False`). 모의투자에서도 SetRealReg A0166000은 정상 동작 확인.

### [B33] SetRealReg 코드 불일치 — 101W06 등록 vs A0166000 수신
**파일**: `main.py`, `collection/kiwoom/realtime_data.py`
**증상**: 틱 수신 로그 없음 — `_on_real_data()` 콜백 진입 자체가 없음
**원인**: `get_realtime_futures_code()` → `101W06` 반환. SetRealReg에 `101W06` 등록. 실제 콜백은 `A0166000`으로 수신 → 필터 `code.strip() != self._rt_code.strip()` 조건 → 전량 차단
**Fix**: `main.py`에서 `code = get_nearest_futures_code()` (A0166000) 로 통일. `realtime_code=code` 전달.

### [B34] 폴링 _last_polled_ts 스테일 타임스탬프 초기화
**파일**: `collection/kiwoom/realtime_data.py`
**증상**: 폴링 첫 실행에서 `completed_min <= _last_polled_ts` 항상 True → 새 분봉 미감지
**원인**: `_start_polling()`이 기존 candle 덱의 `ts` (모의투자 고정값 e.g. 10:14)로 `_last_polled_ts` 초기화 → 벽시계 `completed_min`(11:xx)과 비교 시 항상 ≤
**Fix**: `_start_polling()`에서 `self._last_polled_ts = None` 설정. `_poll_opt50029()`에서 `None` 체크 후 첫 실행 허용.

### [B35] run_minute_pipeline early return — notify_pipeline_ran() 미호출
**파일**: `main.py`
**증상**: `[BAR-CLOSE]` 매 분 정상 → `[Notify] ⚠ 파이프라인 2분 지연` 경보 영구 발동
**원인**: `if not self.model.is_ready(): return` (line 426) — STEP 5 직전 조기 종료. `notify_pipeline_ran()` (line 667) 영구 미호출 → `_pipe_elapsed_s` 누적 → watchdog 발동
**Fix**: return 직전에 `self.dashboard.notify_pipeline_ran()` 추가.
**교훈**: early return이 있는 파이프라인 함수는 모든 return 경로에서 상태 리셋 필수. Guard-C1/C2 return도 동일 패턴 검토 필요.

---

### [B36] OFI 영구 0 — 선물시세에 bid/ask FID 없음 (B14 해결)
**파일**: `collection/kiwoom/realtime_data.py`, `main.py`, `collection/kiwoom/api_connector.py`
**증상**: `[DBG-F4]` bid=0.00 ask=0.00, OFI pressure=0 영구 고정
**원인**: `선물시세`(FC0) 콜백에는 FID 41/51/61/71(bid/ask) 미포함. `_on_real_data()`에서 읽어도 빈 문자열 반환 → bid1=ask1=0 → `if bid1 and ask1:` 조건 항상 False → `ofi.update_hoga()` 미호출
**발견 계기**: SetRealReg 등록 후 SYSTEM.log에 `[RT-CB] type='선물호가잔량'`이 찍히는 것 확인 → 이미 수신 중이었으나 콜백 없어 버려지고 있었음
**Fix**:
- `api_connector.register_realtime()` — `sopt_type` 파라미터 추가 (`"1"` = 기존 등록 유지 추가)
- `realtime_data`: `on_hoga` 콜백 파라미터 추가, `_on_hoga_data()` 신설. `start()`에서 `sopt_type="1"`로 선물호가잔량 추가 등록
- `_on_real_data()`에서 bid/ask 읽기 제거 → `_last_bid1/ask1` 사용
- `main._on_hoga_update()` 신설 → `ofi.update_hoga()` 직접 호출
- `_on_tick_price_update()`에서 OFI 코드 제거 (전담 경로 분리)

---

## 2026-05-04 버그 수정 (오후 세션)

### [B37] SGD `loss="log_loss"` — scikit-learn 1.0.2 불호환
**파일**: `learning/online_learner.py`
**증상**: `ValueError: The loss log_loss is not supported` — 매분 파이프라인 크래시. on_candle_closed 예외로 pipeline 미완료 → watchdog 연속 발동
**원인**: scikit-learn 1.1+ 에서 `"log_loss"` alias 추가. py37_32 환경은 1.0.2 → `"log_loss"` 미인식
**Fix**: `loss="log_loss"` → `loss="log"` (1.0.2 공식 이름)
**교훈**: CLAUDE.md 운영환경에 scikit-learn 1.0.2 명시됨 — 버전 의존 API는 환경표 대조 필요

### [B38] SGD 부트스트랩 치킨에그 — early return이 DB 저장 차단
**파일**: `main.py`
**증상**: 장 시작 후 시그널 로그가 33.3% 고정, SGD 영구 미학습
**원인**: `if not _gbm_ready and not _sgd_ready: return` (STEP 5 직전) → STEP 9 미실행 → predictions DB 미저장 → 다음 분 STEP 1 검증 없음 → STEP 2 learn() 미호출 → SGD 영구 unfit 상태
**Fix**: early return 제거. GBM/SGD 미학습 시 1/3 균등 예측으로 STEP 9까지 진행 (DB 저장 → 다음 분 SGD 학습 트리거)
**교훈**: 파이프라인 early return은 "하위 스텝이 필요로 하는 상태"를 함께 막는지 항상 확인

### [B39] `_last_recovery_ts` 미초기화 — 동일 ts 반복 복구
**파일**: `main.py`
**증상**: watchdog 복구가 같은 분봉(ts=13:08)을 13:13과 13:17 두 번 처리
**원인**: 복구 완료 후 `notify_pipeline_ran()`으로 watchdog 리셋 → 240s 후 재발동 → 동일 ts로 재복구
**Fix**: `_last_recovery_ts` 필드로 마지막 복구 ts 기록. 동일 ts면 스킵 + `notify_pipeline_ran()`. `run_minute_pipeline` 진입 시 `""` 초기화

---

## 2026-05-04 설계 결정

### [D12] SetRealReg(A0166000) — 모의투자 실시간 분봉 수신 표준 경로
**결정**: 모의투자 서버에서도 OPT50029 폴링 사용 금지. SetRealReg + `RT_FUTURES="선물시세"` + code=`A0166000` 단일 경로로 통일.
**이유**: OPT50029는 실 서버에서만 라이브 데이터 제공. 모의투자에서는 rows=0. SetRealReg A0166000은 모의/실전 양쪽에서 동작 확인됨.
**영향**: `is_mock_server` 파라미터 사실상 불필요 (실전 서버 전환 시에도 동일 경로 사용).

### [D14] 선물호가잔량 — sopt_type="1" 추가 등록 패턴
**결정**: `선물시세` 등록(`sopt_type="0"`) 직후 `선물호가잔량`을 `sopt_type="1"`로 추가 등록. 기존 선물시세 등록이 초기화되지 않음.
**이유**: SetRealReg는 `"0"` 전달 시 같은 화면·코드의 기존 등록 전체 초기화. `"1"` 전달 시 기존 유지하고 추가만 함. 호가 데이터는 이미 수신 중이었으므로 SetRealReg 재호출 없이 콜백만 추가해도 되지만, 명시적 등록으로 의도를 명확히 함.

### [D13] WARN/SYSTEM 로그 이중 분리
**결정**: INFO 이하 → SYSTEM.log + 시스템 탭. WARNING 이상 → WARN.log + 경보 탭. 두 채널은 완전 분리.
**이유**: 운영 중 시스템 탭이 WARNING 메시지로 가득 차면 INFO 흐름 파악 어려움. 경보는 별도 탭으로 집중 확인.
**구현**: `_MaxLevelFilter` + `warn_fh` + 대시보드 append 분기.

---

## 2026-04-30 설계 결정 (이번 세션)

### [D1] SIMULATION 모드 완전 제거 — 코드 레벨 분기 폐기

**결정**: `--mode simulation/live` argparse, `self.mode` 인스턴스 변수, 더미 모델 주입 (`force_ready_for_test()`), `_sim_timer` 시뮬 타이머 전량 삭제.

**이유**: 미륵이는 실전 시스템. 모의투자 vs 실전 구분은 키움 API 계좌 레벨에서만 제어하면 충분. 코드 레벨 분기는 오히려 혼동을 유발 (로그에 "더미 모델 주입", "모드=SIMULATION" 노출로 사용자 혼란). SIMULATION 분기를 유지하면 향후 실전 전환 시에도 조건 분기가 남아 잠재적 버그 원인이 됨.

**파급 범위**: main.py 130줄 감소, main_dashboard.py 130줄(시뮬 tick 전체) 감소, multi_horizon_model.py 28줄 감소. 총 191줄 삭제.

---

### [D2] 자동 종료 타이밍 — 15초 QTimer.singleShot

**결정**: `daily_close()` 완료 후 슬랙 알림 발송 → `QTimer.singleShot(15_000, _auto_shutdown)` → `_qt_app.quit()`.

**이유**: Slack 큐 워커는 데몬 스레드 (비동기). 프로세스 종료 즉시 대기 메시지가 소실될 수 있음. HTTP 타임아웃(5초) + rate-limit 슬립(1초/건) × 약 3건 = 최대 18초이나 실제로는 12초 이내 처리. 15초는 안전 여유. 대안으로 `queue.Queue.join()` 블로킹 flush 검토했으나 Qt 이벤트 루프를 15초 블로킹하는 단점 → `singleShot` 비차단 방식 채택.

---

### [D3] 성장 추이 데이터 소스 — trades.db 직접 집계

**결정**: 별도 집계 테이블 없이 `trades.db`에서 `GROUP BY date(entry_ts)` 등으로 직접 집계. 단, SGD 정확도(in-memory)는 `daily_stats` 테이블에 별도 스냅샷.

**이유**: `trades.db`는 이미 완전한 체결 이력 보유. 중복 저장보다 실시간 집계가 단순하고 일관성 있음. SGD 정확도만 예외 (in-memory 버퍼라 재시작 시 초기화됨).

---

### [D4] 패널 선조회 — QTimer.singleShot(500ms)

**결정**: `run()` 내 `_restore_daily_state()` 직후 `QTimer.singleShot(500, self._restore_panels_from_history)` 호출.

**이유**: 키움 로그인 + 대시보드 표시 직후 즉시 DB 쿼리하면 이벤트 루프 진입 전 호출 가능. 500ms 딜레이로 Qt 이벤트 루프 안착 후 호출 보장. DB 쿼리 실패 시 `logger.debug`로만 기록 (비크리티컬 — 파이프라인 첫 실행 시 자연스럽게 갱신됨).

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
