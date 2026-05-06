# 미륵이 (futures) 현재 개발 상태

> 마지막 업데이트: 2026-05-06 (추가2) — trade_type 청산 오류(B47) + gubun='4' 차단(B48)
> 이 파일이 가장 먼저 읽혀야 한다.

---

## 운영 환경

| 항목 | 값 |
|---|---|
| Python | 3.7 32-bit (`py37_32`) |
| 선물 분봉 TR | OPT50029 (수정 완료 — 구: OPT10080) |
| 모드 | 모의투자 (실전 미전환) |

---

## Phase 완료 현황

| Phase | 코드 | 검증 상태 |
|---|---|---|
| Phase 0 — 설계·인프라 | ✅ | ✅ 완료 |
| Phase 1 — 핵심 시스템 | ✅ | ⏳ 모의계좌 실시간 동작 확인 필요 |
| Phase 2 — 안전장치·백테스트 | ✅ | ⏳ CB 5종 테스트 + 26주 WF 데이터 필요 |
| Phase 3 — 알파 강화 | ✅ | ⏳ 실데이터 정확도 검증 필요 |
| Phase 4 — 차별화 (RL·베이지안·뉴스) | ✅ | ⏳ 실거래 데이터 검증 필요 |
| Phase 5 — 실전 운영 | — | 미진입 |
| Phase 6 — 알파 리서치 봇 | ✅ (유전자 진화 완료) | ⏳ main.py 연결 미완 |

---

## 2026-05-06 세션 주요 수정 (Fix B + OPW20006 enc 분석)

| 항목 | 수정 내용 |
|---|---|
| **[B45] OPW20006 레코드명 오타 수정** | `api_connector.py` `_MULTI_RECORD = "선옵잔고상세현황"` (現況·황). 기존 `현활`(活) 오타로 모든 GetCommData 반환값이 blank였음. enc 파일 직접 분석으로 확정 |
| **OPW20006 필드 목록 수정** | `보유수량` 삭제 (OPW20006에 없음), `잔고수량` 유지 (enc offset 66 확인). CS "잔고수량 없음" 오답으로 제거했던 것을 복원. `조회건수` 교차검증 추가 |
| **Fix B — 낙관적 포지션 오픈** | `position_tracker.py`에 `_optimistic` 플래그 + `apply_entry_fill()` 보정 경로 추가. `main.py` line 2660(production)에 `position.open_position()` + `_optimistic=True` 삽입. 모의투자 이중진입 방지 |
| **TR 조사 절차 수립** | `dev_memory/kiwoom_api_tr_investigation.md` 신설. enc 파일(ZIP+CP949) 읽기 절차, GetRepeatCnt/GetCommData 패턴, OPW20006 함정 표 포함 |

### [B46] SendOrderFO 전환 (추가 수정)

| 항목 | 내용 |
|---|---|
| **증상** | `[RC4109] 모의투자 종목코드가 존재하지 않습니다` — `KOA_NORMAL_SELL_KP_ORD` 발생 |
| **원인** | `SendOrder`는 주식 전용. 선물은 `SendOrderFO` 사용 필수 |
| **Fix** | `api_connector.py` `send_order_fo()` 신설. main.py 진입/청산/긴급청산 헬퍼 전환 |
| **`send_order_fo` 파라미터** | `hoga_gb="3"` (선물시장가) / `trade_type` 1=매수, 2=매도 |

**Fix B 진단 로그**: `[FixB] 낙관적 오픈 완료 direction=LONG status=LONG qty=1 optimistic=True` — 2026-05-06 WARN.log에서 정상 확인됨.

### [B47] SendOrderFO trade_type 청산 오류 수정 (2026-05-06 추가)

| 항목 | 내용 |
|---|---|
| **증상** | 14:28 LONG 진입 후 TP1/하드스톱/15:10 강제청산 주문이 60분간 체결 안 됨. EXIT pending 60초마다 set/clear 반복 |
| **원인** | `_send_kiwoom_exit_order`에서 `trade_type=2`(매도 개시=신규 SHORT) 사용. 선물 LONG 청산은 `trade_type=4`(매도 청산) 필수. 모의투자 서버에서 신규매도로 해석 → 체결 처리 안 됨 |
| **Fix** | `trade_type = 4 if LONG else 3` (매도청산/매수청산). `_KiwoomOrderAdapter.send_market_order()`도 동일하게 수정 |

### [B48] gubun='4' 노이즈 이벤트 차단 (2026-05-06 추가)

| 항목 | 내용 |
|---|---|
| **증상** | 매 주문마다 `gubun='4'`, `order_no=''`, `fill_qty=0`, `status=''` 이벤트 추가 도착. ChejanFlow/ChejanMatch 로그 오염 |
| **Fix** | `_ts_on_chejan_event` 진입부에 `if _gubun not in ("0", "1"): return` 추가 |

### 현재 주문 흐름 (B46·B47·Fix B 모두 적용 후)

```
_execute_entry()
→ SendOrderFO COM API, trade_type=1(LONG)/2(SHORT)   ← [B46] 선물 주문 함수
→ _set_pending_order(ENTRY)
→ position.open_position(direction, price, qty)        ← 낙관적 오픈 (Fix B)
→ position._optimistic = True

_send_kiwoom_exit_order()
→ SendOrderFO COM API, trade_type=4(LONG청산)/3(SHORT청산)   ← [B47] 청산 타입 수정

OnReceiveChejanData 콜백
→ gubun='4' → early return (노이즈 차단) [B48]
→ gubun='0' fill_qty=0 → 접수 이벤트 (pending 유지)
→ gubun='0' fill_qty>0 → 체결 이벤트 → apply_entry_fill()/apply_exit_fill()

[Chejan 진입 체결 시]
→ apply_entry_fill() → _optimistic=True + 방향 일치 → 가격 보정만 (수량 불변)

[Chejan 미수신(모의투자 일부)]
→ 낙관적 포지션 그대로 유지 → 이중진입 없음
```

### OPW20006 교훈

```
enc 파일: C:\OpenAPI\data\opw20006.enc (ZIP → OPW20006.dat CP949)
올바른 레코드명: 선옵잔고상세현황 / 선옵잔고상세현황합계
확인된 필드: 종목코드, 종목명, 매매일자, 매매구분("매수"=LONG/"매도"=SHORT),
             잔고수량(offset 66), 매입단가, 매매금액, 현재가, 평가손익, 손익율, 평가금액
키움 CS 오답: "잔고수량 없음" → enc 파일로 반증. CS 답변 맹신 금지.
```

---

## 2026-05-04 세션 주요 수정 (야간 2세션 — Kiwoom API 주문 연결 + 부분 청산 완성)

| 항목 | 수정 내용 |
|---|---|
| **[B42] Kiwoom 주문 전달 누락 수정** | `api_connector.py` `send_order()` 신설. `entry_manager.py`/`exit_manager.py` `acc_no=""` → `_secrets.ACCOUNT_NO`. main.py에 `_send_kiwoom_entry_order()` / `_send_kiwoom_exit_order()` 헬퍼 추가 → 진입/청산 모든 경로에서 실 API 호출 |
| **부분 청산 완성 (TP1/TP2)** | `PositionTracker.partial_close(exit_price, qty, reason)` 신설. `_execute_partial_exit(price, stage)` + `_post_partial_exit(result, stage)` — PARTIAL_EXIT_RATIOS 기반 API→DB→대시보드 전체 연결 |
| **`_KiwoomOrderAdapter` 신설** | main.py 모듈레벨 어댑터 클래스. `EmergencyExit.set_order_manager()` 에 주입 — CB/KillSwitch 긴급청산도 실 API로 연결 |
| **주문/체결 탭 실데이터 메트릭** | LatencySync.summary() → `update_order_metrics(trades, avg_lat_ms, peak_lat_ms, samples)` 매분 갱신. 하드코딩 더미값 제거 |
| **로그 좌측 정렬** | `QTextCursor` + `QTextBlockFormat.setAlignment(Qt.AlignLeft)` 기반 `_insert_html_left()` / `_insert_html_center()` static 메서드. append()/append_restore()/append_separator() 전부 교체 |

### 수정 후 주문 흐름

```
run_minute_pipeline()
→ STEP 7 진입: _send_kiwoom_entry_order(direction, qty) → SendOrder COM API
→                position.open_position(...)
→ STEP 8 청산:
    손절/15:10/트레일: _send_kiwoom_exit_order(qty) → SendOrder COM API
                       position.close_position(...)
    TP1/TP2:           _execute_partial_exit(price, stage)
                       → _send_kiwoom_exit_order(partial_qty) → SendOrder COM API
                       → position.partial_close(...)
                       → _post_partial_exit(result, stage)
CB/KillSwitch:     _KiwoomOrderAdapter.send_market_order() → SendOrder COM API
```

### OnReceiveChejanData 콜백 현황

- ✅ **구현 완료**: `_ts_on_chejan_event()` — gubun='0'(주문/체결) 처리. fill_qty>0 체결 이벤트로 포지션 보정
- ✅ **B47 수정**: trade_type 청산 타입 오류 수정 → EXIT 체결 정상화 (다음 장중 [V35] 확인 필요)
- ✅ **B48 수정**: gubun='4' 노이즈 이벤트 early return 차단
- ⏳ **미확인**: trade_type=4 수정 후 EXIT 체결 Chejan 즉시 수신 → [V35] 다음 장중 확인

---

## 2026-05-04 세션 주요 수정 (야간 — FID 탐색·PROBE 진단·수급 TR 수정)

| 항목 | 수정 내용 |
|---|---|
| **[B40] FID_OI = 291 → 195 수정** | `config/constants.py` + `option_data.py` 하드코딩 2곳. FID 291 = 예상체결가(선물호가잔량), FID 195 = 미결제약정(선물시세). PROBE 스캔으로 확정 |
| **신규 FID 상수 5개 추가** | `FID_EXPECTED_PRICE=291`, `FID_KOSPI200_IDX=197`, `FID_BASIS=183`, `FID_UPPER_LIMIT=305`, `FID_LOWER_LIMIT=306` |
| **TR_INVESTOR_OPTIONS 수정** | opt50014(선물가격대별비중차트요청·잘못 사용) → opt50008(투자자별매도수금액요청) |
| **PROBE 진단 인프라** | LAYER_PROBE 추가, PROBE-ALLRT 전수 FID 스캔, probe_investor_ticker(). 스캔 범위 1~99로 확장 |
| **투자자ticker 모의투자 미지원 확인** | 8가지 코드/타입 조합 전부 ret=0이나 데이터 수신 없음 → 실서버 전환 시 재테스트 필요 |

### 확정된 FID 매핑 (선물시세 기준)

| FID | 값 | 의미 |
|---|---|---|
| 10 | +1049.65 | 현재가 |
| 15 | 거래량 | 거래량 |
| 41 | 매도1호가 | (선물호가잔량에서 수신) |
| 51 | 매수1호가 | (선물호가잔량에서 수신) |
| 195 | 207357 | **미결제약정** (진짜 OI) |
| 197 | +1049.66 | KOSPI200 지수 현재가 |
| 183 | +1.04 | 시장베이시스 |
| 291 | +1020.60 | 예상체결가 (OI 아님! — 선물호가잔량 기준) |
| 305 | +1078.35 | 선물 당일 상한가 |
| 306 | -918.65 | 선물 당일 하한가 |

---

## 2026-05-04 세션 주요 수정 (저녁 — 다이버전스 패널 수급 데이터 흐름)

| 항목 | 수정 내용 |
|---|---|
| **수급 TR 수집 구조 전환** | `investor_data.fetch_all()` → COM 콜백 체인(run_minute_pipeline) 외부로 이동. `_investor_timer` QTimer 60s 신설. STEP4에서 직접 호출 시 0xC0000409 스택 오버런 위험 해소 |
| **investor_data.fetch_*() 수정** | `self._api.set_input_value()`+`comm_rq_data()` (존재하지 않는 메서드) → `self._api.request_tr()` 전환. TR 응답 rows를 인라인으로 직접 파싱 |
| **api_connector._parse_tr_row 확장** | OPT50029만 지원 → opt10059(`순매수`), opt50014(`콜순매수`/`풋순매수`), opt10060(`차익순매수`/`비차익순매수`) 필드 추가 |
| **logger.py DATA 레이어 추가** | `LAYER_DATA="DATA"` 신설. investor_data 오류가 파일 핸들러 없이 사라지던 문제 해결 |
| **투자자 포지션 매트릭스 개선** | `rt_strd`/`fi_strangle` 하드코딩 0 → 실제 `abs(콜)+abs(풋)` 총합 표시 |
| **옵션 구간별 거래량 UI 연결** | `DivergencePanel.update_data()` oz_* 위젯 갱신 구현. `get_zone_data()` 신설 — ATM=현재 전체 수집 데이터 기반 투자자별 %, ITM/OTM=0 (추후 개선) |
| **_fill_dummy_options 기관 추가** | `institution` 더미 추가 → zone % 합계 정상화 |

### 수정 후 수급 데이터 흐름

```
[QTimer 60s]
→ _fetch_investor_data()
→ investor_data.fetch_all()
→   fetch_futures(): request_tr(opt10059) → rows 파싱 → _futures 캐시 갱신
→   fetch_options(): request_tr(opt50014) → rows 파싱 → _call/_put 캐시 갱신
→   fetch_program(): request_tr(opt10060) → rows 파싱 → _program_* 캐시 갱신
→ DATA.log 기록

[run_minute_pipeline - COM 콜백 체인 내]
STEP4: get_features() → 캐시 읽기만 (TR 호출 없음)
       get_zone_data() → 캐시 기반 zone % 계산
→ update_divergence({..., "zones": {...}})
→ DivergencePanel.update_data() → 바이어스 바 + 포지션 카드 + oz_* zone 바 갱신
```

### 남은 한계
- ITM/OTM 구간: opt50014는 전체 합산만 제공 → ATM에 전체 표시, ITM/OTM=0
  - 정확한 구분은 행사가별 개별 TR 조회(여러 번) 필요 (추후 구현)

---

## 2026-05-04 세션 주요 수정 (오후 — 부트스트랩·SGD·UI)

| 항목 | 수정 내용 |
|---|---|
| **[B37] SGD log_loss → log** | `online_learner.py` `loss="log_loss"` → `"log"`. sklearn 1.0.2 호환. 매분 ValueError 크래시 해결 |
| **부트스트랩 치킨에그 해결** | STEP 5 early return 제거 → 미학습 시 1/3 균등 예측 → STEP 9 DB 저장 → SGD 학습 활성화 |
| **watchdog 임계값** | 60/120/180s → 90/150/240s (1분봉 30s 버퍼) |
| **`_last_recovery_ts` 중복 복구 방지** | 동일 ts 반복 복구 스킵 + `run_minute_pipeline` 진입 시 초기화 |
| **Guard-C1/C2 `notify_pipeline_ran()`** | 비정상 분봉 차단 return 경로에 watchdog 카운터 리셋 추가 |
| **`_dir_ko` NameError 수정** | STEP 7 진입 시 변수 정의 추가 |
| **파라미터 중요도·상관계수 툴팁** | SHAP 개념·업데이트 조건 툴팁 추가 |
| **대시보드 섹션 간격** | 섹션 구분선 앞 16px·뒤 12px로 시인성 향상 |

### SGD 학습 파이프라인 현황 (2026-05-04 13:44 확인)

```
[OnlineLearner] 1m/3m/5m/15m 초기 학습 완료 ← log_loss 수정 + 부트스트랩 정상화
10m·30m: 이전 세션 미실행 구간 ts 없음 → 장 진행 중 자동 채워짐
```

---

## 2026-05-04 세션 주요 수정 (B14 OFI 수정 — 선물호가잔량 콜백)

| 항목 | 수정 내용 |
|---|---|
| **B14 OFI 영구 0 수정** | `선물호가잔량` 콜백 `_on_hoga_data()` 신설. bid/ask를 `_last_bid1/ask1`에 저장, `_current_bar` 동기화, `on_hoga` 콜백으로 OFI 누적 |
| **`sopt_type` 파라미터 추가** | `api_connector.register_realtime()` — `"1"` 전달 시 기존 등록 유지하고 추가 등록 (선물호가잔량 등록에 사용) |
| **OFI 경로 분리** | `_on_tick_price_update`에서 OFI 제거 → `_on_hoga_update()` 전담. 선물시세 틱이 아닌 실제 호가 이벤트마다 OFI 누적 |

### 수정 후 데이터 흐름

```
선물시세    → _on_real_data()  → price/vol 조립 → bar 업데이트
선물호가잔량 → _on_hoga_data() → bid/ask 읽기  → _last_bid1/ask1 저장
                                              → _current_bar bid/ask 동기화
                                              → _on_hoga_update() → ofi.update_hoga()
```

---

## 2026-05-04 세션 주요 수정 (모의투자 SetRealReg + WARN 로그 분리 + 파이프라인 watchdog 수정)

| 항목 | 수정 내용 |
|---|---|
| **WARN 로그 분리** | `utils/logger.py` — `_MaxLevelFilter(WARNING)` 추가. SYSTEM 파일핸들러는 INFO만 기록. `YYYYMMDD_WARN.log` 별도 핸들러 추가. 대시보드 경보탭만 WARN+ 표시 |
| **OPT50029 → SetRealReg 전환** | 모의투자 서버에서 OPT50029 rows=0 — 실시간 데이터 미제공. `is_mock_server=False` + `realtime_code=A0166000`으로 SetRealReg 활성화 |
| **SetRealReg 코드 수정 (B33)** | 기존 `rt_code=101W06` → `realtime_code=A0166000`. 콜백 필터 code 불일치 해결 |
| **파이프라인 watchdog 수정 (B35)** | `run_minute_pipeline()` 모델 미학습 early return 전에 `notify_pipeline_ran()` 추가. 기존: line 426 return → line 667 미도달 → watchdog 영구 발동 |
| **진단 로깅 추가** | `[RT-CB]` `[RT-DATA]` `[RT-RAW]` `[RT-BAR]` `[BAR-CLOSE]` SYSTEM.log 기록. 실시간 분봉 수신 경로 end-to-end 확인 가능 |

### 모의투자 실시간 분봉 수신 확인 결과 (2026-05-04 로그)

```
[RT-CB] code='A0166000' type='선물시세' 등록키=[('A0166000', '선물시세')]
[RT-RAW] raw_price='+1038.55' raw_vol='+1'
[BAR-CLOSE] ts=11:22 O=1038.55 H=1038.80 L=1038.45 C=1038.80 V=25  ✅ 매 분 정상
```

---

## 2026-04-30 세션 주요 수정 (SIMULATION 제거 + 자동 종료 + 성장 추이 대시보드)

| 항목 | 수정 내용 |
|---|---|
| **SIMULATION 코드 전면 제거** | `--mode` argparse / `self.mode` / 더미 모델 주입 / `_sim_timer` / `force_ready_for_test()` / `TRADE_MODE` 상수 제거. 단일 실전 경로만 유지 |
| **일일 마감 자동 종료** | `daily_close()` 완료 → 슬랙 종료 알림(거래수·승률·PnL·재학습·다음시작) → 15초 후 `_qt_app.quit()`. `_auto_shutdown()` 신설 |
| **패널 이전 데이터 지속** | `_restore_panels_from_history()` — 시작 500ms 후 DB 이력으로 자가학습·효과검증·추이 패널 선조회. 파이프라인 첫 실행 전 빈값 방지 |
| **daily_stats 스냅샷 저장** | `daily_close()` 내 `save_daily_stats()` — SGD정확도·검증건수·PnL을 `daily_stats` 테이블에 영속 |
| **📈 성장 추이 탭 신설** | `TrendPanel` — 일별(30일)/주별(12주)/월별(12개월)/연간 4탭. 스파크라인(PnL·승률·SGD정확도) + 스크롤 테이블. 탭 순서: …자가학습/효과검증/**성장추이**/알파봇 |
| **DB 집계 쿼리 4종** | `fetch_trend_daily/weekly/monthly/yearly()` + `daily_stats` 테이블 + `save_daily_stats()` |

---

## 현재 대시보드 탭 구조

### 중앙 탭 (mid_tabs) — 8개
| 번호 | 탭 이름 | 클래스 |
|---|---|---|
| 1 | 다이버전스 + 포지션 | `DivergencePanel` |
| 2 | 동적 피처 (SHAP) | `FeaturePanel` |
| 3 | 청산 관리 | `ExitPanel` |
| 4 | 진입 관리 | `EntryPanel` |
| 5 | 🧠 자가학습 | `LearningPanel` |
| 6 | 🎯 효과 검증 | `EfficacyPanel` |
| **7** | **📈 성장 추이** | **`TrendPanel`** (신규) |
| 8 | 알파 리서치 봇 | `AlphaPanel` |

### 우측 5층 로그 탭 — 6개
| 탭 | 내용 |
|---|---|
| 1 시스템/경보 | SYSTEM/WARNING 레벨 통합 (2 경보탭 공유) |
| 2 경보 | WARN/ERROR/CRITICAL 전용 |
| 3 주문/체결 | TRADE 레이어 + FILL/PENDING 태그 |
| 4 손익 | PnL 로그 + 미실현·일일·VaR 수치 |
| 5 모델 AI | LEARNING/MODEL 레이어 |
| 6 📊 손익 추이 | 일별·주별·월별 누적 P&L 테이블 (기존 PnlHistoryPanel) |

---

## 2026-04-30 세션 주요 수정 (파이프라인 감시 경보 버그 2종 수정 + 분봉 툴팁)

| 항목 | 수정 내용 |
|---|---|
| **경보 누락 버그 1** | `_tick_header()` — `_watchdog_alerted.add(threshold)` 가 콜백 체크 **이전**에 실행되어, 콜백 미등록 시 임계값을 소비하고 나중에 콜백 등록 후에도 영구 누락. **수정**: 콜백 실행 후에만 소비(`add` 위치 교체) |
| **경보 누락 버그 2** | `append_sys_log_tagged()` — `level="WARNING"` 체크 조건이 `("WARN", "ERROR", "CRITICAL")` 이라 `"WARNING"` 이 불일치 → SYSTEM 태그로 처리되어 경보 탭 미표시. **수정**: `{"WARNING": "WARN"}.get(level, level)` 정규화 추가 |
| **분봉 라벨 툴팁** | `_PIPE_HEALTH_TIP` 상수 추가 — 파이프라인 심박 막대 기능 + 3단계 자동 조치(60/120/180초) + 긴급복구 루틴 + 원인 목록. 분봉 라벨·진행 바·경과 라벨 3개 위젯 연결 |

### 버그 발생 경위 (실제 시퀀스)

```
1. __init__: _header_timer 시작 → _pipe_elapsed_s 증가 시작
2. connect_kiwoom() 진행 중 (수십 초 소요)
   → 60/120초 도달 시 threshold 소비되나 callback=None → 알림 없음
3. set_pipeline_watchdog_cb() 호출 → callback 등록
4. pipeline 정상 실행 → notify_pipeline_ran() → _watchdog_alerted.clear()
5. pipeline 재정지 → 60초 후 threshold 60 재진입
   → 이때 callback 존재해야 발동되는데...
   → _pipe_elapsed_s += 1 로직에서 threshold 60을 콜백 없이 소비했다면 영구 누락!
```

---

## 2026-04-30 세션 주요 수정 (비정상 분봉 가드 + 진입 신뢰성 강화)

| 항목 | 수정 내용 |
|---|---|
| **Guard-C1 가격 0 차단** | `run_minute_pipeline()` 앞단 — close/high/low ≤ 0 이면 경보 로그 후 즉시 return. ATR 음수·손절가 오작동 원천 차단 |
| **Guard-C2 고가<저가 차단** | high < low 역전 분봉 경보 후 즉시 return. 음의 TR → ATR 오염 방지 |
| **Guard-C3 volume=0 진입 차단** | volume=0 경보 로그 + `_bar_volume_zero` 플래그 설정. STEP 7 진입 조건에 `and not _bar_volume_zero` 추가. 청산은 차단 안 함(가격 기반) |
| **Guard-F1 CORE 피처 NaN/Inf 교정** | STEP 4 후 vwap_position / cvd_direction / ofi_pressure 에 NaN·Inf 검출 시 0으로 교정 + 경보 로그 |
| **daily_loss_pct 계산 수정** | 기존: `abs(pnl_pts) / 1_000` (실질적으로 항상 통과) → 수정: `max(-pnl_krw, 0) / 50_000_000` (5천만원 기준 실손실률). 체크리스트 9번 리스크 한도 실질화 |
| **`import math` 추가** | main.py 최상단 — Guard-F1 NaN/Inf 검사용 |

### 가드 점검 결과 요약 (조사 기반)

| 구간 | 수정 전 | 수정 후 |
|---|---|---|
| 분봉 수신 (realtime_data) | abs() 변환만 | 변경 없음 (수신 레이어는 OK) |
| 파이프라인 앞단 (main.py) | **없음** | **C1/C2/C3 가드 추가** |
| CORE 피처 (STEP 4 후) | **없음** | **F1 NaN/Inf 교정** |
| 진입 조건 (STEP 7) | CB+시간+등급+수량 | **volume=0 차단 추가** |
| 청산 조건 (STEP 8) | 완전 (변경 없음) | 변경 없음 |
| 리스크 한도 (체크리스트 9) | **pts/1000 — 항상 통과** | **KRW/5천만 — 실질 2% 한도** |
| Circuit Breaker | 완전 (변경 없음) | 변경 없음 |

### 남은 한계 (개선 불가·저우선)

- OFI/CVD 극단값 제한 없음 — signal_strength 과대 가능 (CB④ ATR 3배 트리거로 간접 방어)
- account_balance 하드코딩(5천만) — 실제 잔고 연동 시 개선 필요
- ATR floor(0.5pt)로 비정상 소ATR 방어는 유지

---

## 2026-04-30 세션 주요 수정 (파이프라인 생존 감시 + 자동 복구)

| 항목 | 수정 내용 |
|---|---|
| **파이프라인 감시 콜백** | `main_dashboard.py` — `MireukDashboard._watchdog_alerted` (set) + `_pipeline_recovery_cb` 추가. `_tick_header()`에서 60/120/180초 임계값 초과 시 1회만 콜백 발동. `notify_pipeline_ran()` 시 플래그 초기화 |
| **`set_pipeline_watchdog_cb()`** | `DashboardAdapter`에 추가 — main.py → dashboard 역방향 콜백 등록 인터페이스 |
| **`_on_pipeline_watchdog()`** | `main.py` — 60s: 경보 로그(WARNING), 120s: 경보 + 슬랙, 180s: 경보 + 슬랙 + 강제 복구 |
| **`_try_pipeline_recovery()`** | `main.py` — `raw_candles` DB 최신 분봉(10분 이내) 읽어 `run_minute_pipeline()` 강제 재실행. 포지션 보유 중 장기 정지 시 추가 경보 |
| **`log_manager.warn` 오류 수정** | `warn()` 메서드 없음 → 전체 `log_manager.system(msg, "WARNING")` 으로 교체. SYSTEM layer + WARNING level → `append_sys_log_tagged` → 1 시스템·2 경보 탭 동시 기록 |

### 파이프라인 감시 3단계 동작

| 경과 | 동작 |
|---|---|
| **60초** | 경보 탭 경고 — 분봉 수신 지연, 장 시간 확인 안내 |
| **120초** | 경보 탭 경고 + 슬랙 알림 — 60초 내 미복구 시 자동 조치 예고 |
| **180초** | 경보 탭 + 슬랙 + `_try_pipeline_recovery()` 자동 실행 |

### 복구 루틴 조건 분기

- `raw_candles` 없음 → 경보 로그 후 종료 (포지션 있으면 추가 경보)
- 최신 분봉 > 10분 전 → 복구 포기 (장외 시간 판단)
- 최신 분봉 ≤ 10분 → `run_minute_pipeline(bar)` 강제 실행 → `notify_pipeline_ran()` 자동 호출 → 감시 플래그 리셋

---

## 2026-04-30 세션 주요 수정 (PnL 재시작 복원 수정 + 분봉 모니터 툴팁)

| 항목 | 수정 내용 |
|---|---|
| **PnL 재시작 복원 [B30]** | `main.py` `_restore_daily_state()` — `restore_daily_stats()` 호출 후 `dashboard.update_pnl_metrics(0.0, daily_pnl_krw, 0.0)` 추가. 재시작 후 미실현손익·일일누적·VaR 패널이 "——원" 로 리셋되던 버그 수정 |
| **분봉 모니터 툴팁** | `dashboard/main_dashboard.py` — `_CANDLE_MONITOR_TIP` 상수 추가. "다음 분봉 ▷" 라벨·진행 바·초 라벨, "↑ 마지막 갱신" 라벨·경과 라벨 5개 위젯에 동일 툴팁 연결. 라벨에 점선 밑줄(cursor:help) 표시 |

### PnL 복원 버그 근본 원인 (B30)
- `_restore_daily_state()`에서 `position.restore_daily_stats(rows)` 로 내부 통계(`_daily_pnl_pts` 등)는 정상 복원
- 그러나 UI 패널에 `dashboard.update_pnl_metrics()` 호출이 없어 화면은 초기값 "——원" 유지
- 수정: `daily_stats()` 로 복원된 값을 읽어 즉시 패널 반영. 미실현/VaR는 0 (첫 분봉 수신 후 갱신됨)

---

## 2026-04-30 세션 주요 수정 (CB 중복발동 수정 + 슬랙 타임스탬프)

| 항목 | 수정 내용 |
|---|---|
| **CB 중복 슬랙 발동 수정** | `_trigger_halt()` — HALTED 상태 조기 반환 체크 추가 (기존: 체크 없음 → 정확도 35% 미만 지속 시 매분 슬랙 재전송) |
| **CB `_trigger_pause()` 방어** | PAUSED 상태에서도 재발동 방지. 기존엔 `HALTED`만 막음 → `PAUSED·HALTED` 모두 차단 |
| **CB 트리거⑤ API지연 방어** | `record_api_latency()` — PAUSED·HALTED 상태에서 슬랙·청산 콜백 중복 호출 방지 조건 추가 |
| **CB → UI 로그 연결** | `circuit_breaker.py`가 `logger.getLogger("SYSTEM")`만 사용해 UI 미출력. `log_manager` import 추가 + `_trigger_pause/halt`, `_check_pause_expiry`, `reset_daily` 전부 `log_manager.system()` 호출 추가 → 대시보드 SYSTEM/경보 탭 표시 |
| **슬랙 타임스탬프** | `utils/notify.py` — `notify()` 내 `[HH:MM:SS]` 자동 첨부. 모든 알림에 전송 시각 표시 |
| **슬랙 주문·체결 함수 추가** | `notify_order()`, `notify_execution()` 함수 신설 (방향·수량·가격·손익 포함) |

### CB 중복 발동 원인 (근본 원인 분석)
- **트리거③ 정확도**: 30분 정확도 < 35% 동안 매분 `record_accuracy()` → `_trigger_halt()` 호출. 기존엔 HALTED 체크 없어 매분 슬랙 재전송
- **트리거④ ATR**: ATR 3배 초과 지속 시 매분 `_trigger_pause()` 호출. 기존엔 PAUSED 상태에서도 재발동 + `_pause_until` 갱신 + 슬랙 재전송
- **UI 미출력**: `circuit_breaker.py`의 `logger`는 파일/콘솔 전용 (`logging.getLogger`). 대시보드 `log_manager`와 별개 시스템이라 UI에 아무것도 안 보임

---

## 2026-04-30 세션 주요 수정 (자가학습 연결)

| 항목 | 수정 내용 |
|---|---|
| **STEP 2 SGD 연결** | `main.py` STEP 2 — STEP 1 검증 결과(verified)의 피처 dict로 `OnlineLearner.learn()` 호출. 매 검증건마다 즉시 `partial_fit` |
| **STEP 3 GBM 연결** | `main.py` STEP 3 — `should_retrain_weekly()` / `should_retrain_monthly()` 조건 충족 시 `batch_retrainer.retrain_now()` 호출 후 `model._load_all()`로 즉시 반영 |
| **SGD 블렌딩 적용** | `main.py` STEP 5 — GBM `predict_proba()` 직후 호라이즌별 `online_learner.blend_with_gbm()` 적용. SGD 미학습(fitted=False) 시엔 GBM 단독 사용 |
| **features 전체 저장** | `main.py` STEP 9 — `list(features.items())[:20]` → 전체 피처 저장 (SGD 학습 입력 완전성 확보) |
| **daily_close 재학습** | `main.py` 15:40 마감 시 `batch_retrainer.retrain_now(weeks_back=8)` 호출 후 모델 reload |
| **BatchRetrainer 초기화** | `main.py __init__` — `self.batch_retrainer = BatchRetrainer()` 추가 |
| **_load_from_db 재작성** | `batch_retrainer.py` — pandas 의존 제거, `raw_features`/`raw_candles` 테이블 직접 읽기. numpy 기반 X 행렬 + `build_single_target()` 라벨 생성 |
| **prediction_buffer features** | `prediction_buffer.py` `verify_and_update()` — SELECT에 `features` 컬럼 추가, 반환 dict에 JSON 파싱된 `features` 포함 |

---

## 🎯 학습 효과 검증기 패널 (신규 — 2026-04-30)

| 항목 | 내용 |
|---|---|
| **위치** | 중앙 탭 6번째 "🎯 효과 검증" (🧠자가학습 탭 오른쪽) |
| **EfficacyPanel** | `dashboard/main_dashboard.py` `class EfficacyPanel` |
| **update_efficacy()** | `DashboardAdapter.update_efficacy(data)` → `efficacy_panel.update_data(data)` |
| **_gather_efficacy_stats()** | `main.py` — DB 쿼리 후 5분마다 호출 (`_efficacy_tick % 5 == 1`) |
| **DB 쿼리 4종** | `utils/db_utils.py` — `fetch_calibration_bins` / `fetch_grade_stats` / `fetch_regime_stats` / `fetch_accuracy_history` |

### 패널 4-Section 구성
1. **신뢰도 캘리브레이션** — confidence 구간별 실제 적중률 테이블 (✓ 우수 / ▲ 과소신뢰 / ▼ 과신)
2. **등급별 매매 성과** — A/B/C/X/? 등급별 건수·승률·평균pts·합계pts
3. **학습 성장 곡선** — `▁▂▃▄▅▆▇█` 스파크라인 + 초기 50회 vs 최근 50회 Δ
4. **레짐별 성과** — RISK_ON/NEUTRAL/RISK_OFF 승률 게이지 바 + 평균pts

### KPI 상단 배지 4개
- 전체 승률 / A등급 승률 / 캘리브레이션 점수 / 학습 효과 Δ

### 종합 평가 배너 기준
- A등급 승률 ≥60% + 전체 ≥53% → ✅ 학습 효과 확인
- 전체 ≥50% → ⚡ 개선 중
- 전체 <50% → ⚠️ 모델 재점검 권장

---

## 🧠 자가학습 모니터 패널 (신규)

| 항목 | 내용 |
|---|---|
| **위치** | 중앙 탭 5번째 "🧠 자가학습" |
| **LearningPanel** | `dashboard/main_dashboard.py` `class LearningPanel` |
| **update_learning()** | `DashboardAdapter.update_learning(data)` → `learn_panel.update_data(data)` |
| **_gather_learning_stats()** | `main.py` — SGD/GBM/버퍼 통계 수집 후 매분 호출 |
| **_verified_today** | 당일 검증 건수 누적 카운터 (15:40 리셋) |
| **_horizon_counts** | `OnlineLearner._horizon_counts` — 호라이즌별 학습 건수 |

### 패널 구성
1. **요약 카드 4개** — 오늘 검증 건수 / SGD 50분 정확도(색상) / GBM 마지막 재학습 / 데이터 축적%
2. **SGD 섹션** — GBM↔SGD 블렌딩 그라데이션 바 + 6개 호라이즌 카드(정확도/학습건수/배지)
3. **GBM 섹션** — 마지막 재학습 / 재학습 횟수 / 다음 스케줄 + 5000행 축적 진행 바
4. **예측 버퍼 테이블** — 6 호라이즌 × (정확도 / 게이지 / 추세▲▼━)

### 정확도 색상 기준
- ≥62%: 초록 (SGD 비중 증가 중)
- 55~62%: 청록
- 48~55%: 주황
- <48%: 빨강 (SGD 비중 감소 중)

---

## 자가학습 파이프라인 현재 상태

| 항목 | 상태 |
|---|---|
| SGD 온라인 학습 (STEP 2) | ✅ **연결 완료** |
| GBM 배치 재학습 (STEP 3) | ✅ **연결 완료** (주간/월간 + 일일 마감) |
| SGD 블렌딩 (STEP 5) | ✅ **연결 완료** |
| features 전체 저장 (STEP 9) | ✅ **수정 완료** |
| BatchRetrainer DB 로드 | ✅ **raw_features 연동 완료** |
| 실제 학습 가동 조건 | ⏳ raw_candles 5000행 축적 필요 (2026-04-28 시작, 약 2.5주) |

---

## 2026-04-28 세션 주요 수정 (오전)

| 항목 | 수정 내용 |
|---|---|
| PredictionPanel dict reset 재발 수정 | `__init__` 277~279 줄의 reset이 `_build()` 호출 후에 위치해 항상 빈 dict → 선언을 `_build()` 앞으로 이동, `_build()` 내 중복 초기화 제거 |
| 시뮬레이션 타이머 조건부 시작 | `kiwoom=None`일 때만 `_start_sim_timer()` 호출. `update_price()` 첫 수신 시 `_stop_sim_timer()` 자동 호출 |
| sim timer 참조 저장 | `self._sim_timer`로 저장 (`stop()` 호출 가능하도록) |
| force_ready_for_test() 추가 | SIMULATION 모드 파이프라인 통과 검증용 더미 GBM 모델 주입 (`.pkl` 저장 없음) |
| 파이프라인 전체 검증 완료 [V3] | tick→분봉→pipeline→LONG 1계약 @ 1008.2 / 12:29 확인 |
| predictions.db 저장 확인 [V5] | 12:29·12:30 각 6 호라이즌 = 30행 확인 |
| trades.db 저장 누락 수정 | `_post_exit()`에 trades.db INSERT 추가. `position_tracker.close_position()` result에 `entry_ts`·`grade` 추가 |
| 대시보드 가격 동기화 | `run_minute_pipeline()` 진입 시 `dashboard.update_price(bar['close'])` 호출 추가 (기존엔 시뮬 타이머 ~388만 표시됨) |

## 2026-04-30 세션 주요 수정 (저녁)

| 항목 | 수정 내용 |
|---|---|
| 손익 추이 패널 신설 | 5층 로그 6번째 탭 "📊 손익 추이". 일별(60일)·주별(13주)·월별 `QTableWidget` 누적 P&L 테이블 + 요약 카드 6개 |
| 수익/손실 행 배경 | 수익일 연한 초록 / 손실일 연한 빨강 / 당일 황색 볼드 강조 |
| 월별 샤프 지수 | 월 내 일별 PnL 기반 연율화 샤프(√252), 색상 조건부(초록/노랑/빨강) |
| 주별 MDD | 주간 내 순차 누적 기준 최대 낙폭(원) 표시 |
| `fetch_pnl_history()` | db_utils.py 추가 — 체결 완료 거래 최근 90일 SELECT |
| `_refresh_pnl_history()` | main.py 추가 — _post_exit / daily_close / _restore_daily_state 3곳 자동 갱신 |

## 2026-04-30 세션 주요 수정 (오후)

| 항목 | 수정 내용 |
|---|---|
| PnL 탭 즉시 갱신 [B27/B28] | `_post_exit()` / `_execute_entry()` 내 `update_pnl_metrics()` + `append_pnl_log()` 직접 호출 추가 |
| ScreenScale 전면 재작성 | `fit_scale=min(sw/1680,sh/1000)` + `dpi_bonus=(dpr-1)×0.10`. 3840×2160@150%→1.45× 자동 적용 |
| 폰트 시인성 개선 | QTextEdit/배지/버튼 전 하드코딩 px → `S.f()` 교체, 5층 로그 12px 기준 |
| 재시작 연속성 [B29] | `trades.db` 당일 거래 → 주문/체결·손익 탭 `[복원]` 이탤릭 재표시, 세션 카운터(`session_state.json`), `restore_daily_stats()` 통계 재적산 |

## 2026-04-30 세션 주요 수정 (오전)

| 항목 | 수정 내용 |
|---|---|
| FILL 이상가격 이상점 진단 | 대시보드 `_sim_tick()` 시뮬 타이머가 키움 연결 전 창1 주문/체결 탭에 `FILL 매도 5계약 @388.48` 가짜 로그를 출력하는 것으로 확인 — 실제 거래 무관 |
| 시뮬 모드 완전 분리 [B26] | `MireukDashboard.__init__(sim_mode=True)` 파라미터 추가. `live` 모드(`sim_mode=False`)면 시뮬 타이머 자체 미생성. `DashboardAdapter` / `create_dashboard()` 동일하게 `sim_mode` 전파 |
| main.py 모드 연동 | `create_dashboard(sim_mode=(self.mode == "SIMULATION"))` 전달. `stop_sim_timer()` 호출을 `if self.mode == "SIMULATION":` 조건 내부로 이동 (live 모드에서 불필요한 호출 제거) |
| [SIM] 태그 추가 | `_sim_tick()` FILL/PENDING 로그 앞에 `[SIM]` 접두사 추가 — 시뮬 로그와 실거래 로그 육안 구분 가능 |

## 2026-04-29 세션 주요 수정 (오후 추가)

| 항목 | 수정 내용 |
|---|---|
| 멀티 호라이즌 `_preds_ui` 확률 오류 수정 | `main.py` STEP 5→UI 변환 시 `1-confidence` 근사 → `r["up"]`/`r["down"]`/`r["flat"]` 직접 참조로 교체. 3클래스 합≠1 오류 제거 |
| 시뮬레이션 호라이즌 다양성 수정 | `main_dashboard.py` `_sim_tick`: 단일 trend 기반 → 호라이즌별 σ `[0.06~0.20]` 독립 노이즈 적용 (장기일수록 불확실성 증가). `hold` 키 → `flat`으로 실거래 경로와 통일 |

## 2026-04-29 세션 주요 수정

| 항목 | 수정 내용 |
|---|---|
| 주문/체결 탭 툴팁 | `dashboard/main_dashboard.py`: `_ORDER_TAB_TIP` 상수 추가 + `QToolTip` CSS + `setTabToolTip()` — 진입 흐름(①~⑤) + 청산 흐름(P1~P6) HTML 툴팁 |
| 외인 데이터 "-" 수정 [B16] | `InvestorData` 미임포트·미인스턴스화 확인 → `main.py` import 추가, `__init__`에 인스턴스화, STEP 4에 `fetch_all()` + `supply_demand=supply_feats` 전달 |
| 다이버전스 패널 배선 [B17] | `dashboard.update_divergence()` 미호출 → STEP 4 직후 rt_bias/fi_bias/contrarian/div_score 계산 후 매분 호출 |
| 외인 카드 업데이트 누락 [B18] | `DivergencePanel.update_data()`: fi_call/fi_put/fi_strangle 카드 setText 3줄 추가 |
| investor_data api 주입 | `connect_kiwoom()` 내 `self.investor_data._api = self.kiwoom` 추가 (실거래 시 TR 폴링 활성화) |
| investor_data 일일 리셋 | `daily_close()`에 `self.investor_data.reset_daily()` 추가 |
| 체크리스트 전부 X 버그 [B19] | 체크리스트 평가를 CB·시간 조건 블록 밖으로 분리 → FLAT+방향 있으면 항상 평가, 대시보드 항상 갱신 |
| 체크 미평가 시 X 표시 [B20] | `update_data()`: `checks.get(attr, None)` → None이면 회색 "—" 표시 (기존: False → 빨간 X) |
| 산출 수량 —— [B21] | `update_entry(qty=0)` 파라미터 추가 + `e_qty` 라벨 갱신 로직 추가 |
| 당일 진입 통계 고정 [B22] | `EntryPanel.update_stats()` + `DashboardAdapter.update_entry_stats()` 추가, STEP 9 후 매분 `position.daily_stats()` 기반 갱신 |
| 청산 패널 데이터 배선 [B23] | `main.py` STEP 8 직후 `update_position()` 추가 — PositionTracker 실제 값(`stop_price`, `tp1_price`, `tp2_price`, `entry_time`, `partial_1/2_done`) 전달 |
| ExitPanel.update_data() 재작성 [B24] | FLAT 상태 → `_reset_display()` "——" 표시 / LONG·SHORT: 실제 스톱·목표가 사용, 보유 시간 계산, PnL KRW 방향 반영, 부분청산 바 갱신 |
| 시뮬 루프 청산 패널 수정 [B25] | `status='LONG'` + `stop`/`tp1`/`tp2` 구조화, `partial1`/`partial2` 틱 기반 시뮬 |

## 2026-04-28 세션 주요 수정 (오후)

| 항목 | 수정 내용 |
|---|---|
| Path B DB 인프라 구축 | `utils/db_utils.py`에 `raw_candles`/`raw_features` 테이블 + save/get 함수 4개 추가. `config/settings.py`에 `RAW_DATA_DB` 경로 추가. STEP 4에서 매분 분봉·피처 저장 시작 — 13거래일 후 실제 모델 학습 가능 |
| CVD 틱 방향 수정 [B13] | FC0 FID10 부호(전일대비 방향)를 틱 방향으로 오해 → tick test(prev_price 비교, Lee-Ready 근사)로 교체. `realtime_data.py`에 `_prev_tick_price` 추가, bar dict에 `buy_vol`/`sell_vol` 누적 |
| 손절 exit price 보정 [B15] | `_check_exit_triggers(bar=)`에 bar 파라미터 추가. LONG 손절 시 `exit_price = max(stop_price, bar_low)` — close가가 아닌 손절가 기준 |
| 디버그 로그 8포인트 추가 | [DBG-F4] ATR+핵심피처 / [DBG-F6] 호라이즌예측 / [DBG-CB] CB상태 / [DBG-F7] 진입조건 / [DBG-F7a] 체크리스트 / [DBG-F7b] 사이저 / [DBG-F8] 포지션PnL / [DBG-STOP] 하드스톱 |
| DEBUG 레이어 레벨 수정 | `utils/logger.py`: LOG_LEVEL=INFO여서 DEBUG 레이어도 INFO → debug() 차단. `logging.DEBUG` 고정으로 수정 |
| 대시보드 신뢰도 갱신 | `PredictionPanel.update_data(conf=)` 파라미터 추가 → `lbl_conf` "신뢰도 76.8%" 표시 |
| 대시보드 호라이즌/체크리스트 갱신 | `run_minute_pipeline`에서 `update_prediction()` + `update_entry()` 매분 호출 추가 |
| 대시보드 5층 로그 배선 | `main.py __init__`에서 `log_manager.subscribe()` SYSTEM/TRADE/LEARNING 콜백 등록 |
| 대시보드 PnL 실시간 갱신 | `LogPanel.update_pnl_metrics()` 추가 + `_pnl_vals`/`_pnl_bars` dict 저장 (이전엔 로컬 변수 → 업데이트 불가) |
| 실거래 검증 결과 | LONG @1008.40 stop=1007.65, ATR floor stop_dist=0.75pt 확인 [V6 DONE], 체크리스트 8/9 통과 |

## 2026-04-27 세션 주요 수정

| 항목 | 수정 내용 |
|---|---|
| 근월물 코드 | `GetFutureCodeByIndex(0)` 0순위 추가 → `A0166000` 확정 (구: 날짜계산 fallback `101W06`) |
| 실시간 타입명 | `RT_FUTURES="FC0"` → `"선물시세"`, `RT_FUTURES_HOGA="FH0"` → `"선물호가잔량"` |
| GetRepeatCnt | `or rq_name` fallback 제거 → `""` 빈 문자열 그대로 전달 |
| EmergencyExit | `get_position()` 없음 → 속성 직접 읽기 + `set_futures_code()` 추가 |
| run_minute_pipeline | candle `ts`(datetime) → `strftime` 문자열 변환 |
| 대시보드 | PredictionPanel `_build()` 맨 앞에서 dict 초기화 (IDE 순서 복구 방지) |
| 대시보드 | `mk_val_label` `align` 파라미터 추가 |
| 대시보드 | 헤더 우측 커밋 해시 표시 (해상도 아래) |

## 2026-04-26 세션 주요 수정

| 항목 | 수정 내용 |
|---|---|
| TR 코드 | OPT10080 → **OPT50029** (`config/constants.py`) |
| COM 콜백 | 메타데이터만 저장 + QEventLoop.quit(), 실제 API 호출은 exec_() 복귀 후 |
| GetRepeatCnt | 2번째 파라미터: rq_name → **record_name** |
| 근월물 조회 | GetFutureList() 우선 → GetMasterCodeList("10") → 날짜 계산 fallback |
| GetCommDataEx | → **GetCommData** (서명 오류 수정) |
| 대시보드 | `create_dashboard()` 시작 시 show(), 5분마다 대기 상태 로그 |

---

## 현재 차단 이슈

| 이슈 | 원인 | 상태 |
|---|---|---|
| OFI 영구 0 (B14) | 선물호가잔량 콜백 신설 + `sopt_type="1"` 추가 등록으로 해결 | ✅ 해결 |
| CVD tick test 효과 | 다음 실행에서 buy_vol/sell_vol이 실제 분리되는지 [V8] 확인 필요 | ⏳ 검증 대기 |
| OPT50029 초기 분봉 rows=0 | 모의투자 서버에서 OPT50029 미지원 확인. SetRealReg(A0166000)으로 전환 완료 | ✅ 해결 |
| [DBG] 출력문 정리 | 디버그 print 잔존 | 🔧 안정화 후 제거 |
| Walk-Forward 26주 | 실거래 데이터 미확보 | ⏳ 장기 과제 |
| Path B 모델 학습 | 13거래일 raw_candles 축적 후 가능 (2026-04-28 축적 시작) | ⏳ 약 2.5주 후 |

---

## 성능 목표

| 버전 | 정확도 | Sharpe | MDD |
|---|---|---|---|
| v6 (기준) | 75~80% | 2.5~3.0 | — |
| v6.5 (현재) | 80~85% | 3.0~3.5 | — |
| v7.0 (목표) | 82~88% | 3.5~4.0 | -30% |

---

## 형제 프로젝트 참조

- 한량이(주식 자동매매): `auto_trader_kiwoom/dev_memory/CURRENT_STATE.md`
## 2026-05-06 최신 반영

| 항목 | 상태 |
|---|---|
| 체결 소스 오브 트루스 | `OnReceiveChejanData` + pending order 매칭 경로를 기준으로 추적하도록 보강됨 |
| startup broker sync | `OPW20006` blank placeholder row-only 응답을 hard mismatch가 아니라 FLAT 후보로 해석하도록 보정됨 |
| futures balance 진단 | `OPW20006-REQ`, `OPW20006-RESP`, `OPW20006-DIAG` 추가 |
| 주문 경로 진단 | `EntryAttempt`, `EntrySendOrderResult`, `PendingOrder`, `EntryPendingCreated`, `OrderMsgDiag` 추가 |
| Chejan/잔고 진단 | `ChejanDiag`, `ChejanFlow`, `ChejanMatch`, `ChejanDedup`, `EntryFillFlow`, `ExitFillFlow`, `BalanceChejanFlow`, `BrokerSyncFlatPlaceholder` 추가 |
| 포지션 복원 메타 | `position_state.json`에 `last_update_reason`, `last_update_ts` 저장 및 `PositionDiag` 복원 로그 추가 |
| 오늘 확인된 유력 원인 | startup sync 차단은 blank placeholder row 오판 가능성이 가장 높음 |
| 잔여 리스크 | `2026-05-06 10:48:19` 불일치의 정확한 과거 원인은 다음 실행 로그로 최종 증명 필요 |
| 운영 리스크 | CB 저정확도 halt 및 strategy gate 정책은 별도 검토 필요 |
