# 세션 이력 — futures (미륵이)

> 최신순 정렬.

---

## 2026-05-04 (야간 세션 — FID 탐색·PROBE 진단·수급 TR 수정)

**작업**: PROBE 진단 로그 분석 → FID 오류 확정 수정 + 신규 FID 상수 추가 + 수급 TR 코드 수정

### 핵심 수정 6건

| 항목 | 내용 |
|---|---|
| **[B40] FID_OI = 291 치명적 오류 수정** | `config/constants.py` FID_OI 291 → 195. FID 291은 예상체결가(선물호가잔량 기준)이며 미결제약정이 아님. PROBE-ALLRT-FIDS 스캔으로 FID 195=207357(미결제약정) 확정 |
| **option_data.py 하드코딩 291 수정** | `collection/kiwoom/option_data.py` 하드코딩 291 두 곳 → `FID_OI` 임포트로 교체 |
| **신규 FID 상수 추가** | `FID_EXPECTED_PRICE=291`, `FID_KOSPI200_IDX=197`(KOSPI200지수), `FID_BASIS=183`(시장베이시스), `FID_UPPER_LIMIT=305`(선물상한가), `FID_LOWER_LIMIT=306`(선물하한가) |
| **TR_INVESTOR_OPTIONS 수정** | `config/constants.py` opt50014 → opt50008. opt50014는 선물가격대별비중차트요청으로 잘못 사용됨 확인 |
| **PROBE 진단 인프라 신설** | `utils/logger.py` LAYER_PROBE 추가(DEBUG+콘솔). `api_connector.py` PROBE-ALLRT(신규 실시간 타입 전수 FID 스캔), probe_investor_ticker() 신설 |
| **PROBE 스캔 범위 확장** | PROBE-ALLRT FID 스캔: 1~50 → 1~99 (bid/ask qty FID 51~99 구간 추가) |

### PROBE-ALLRT 실행 결과 (2026-05-04)

**선물시세 FID 주요 발견:**
```
FID 195 = '207357'    → 미결제약정 (진짜 OI) ← FID_OI 수정 근거
FID 197 = '+1049.66'  → KOSPI200 지수 현재가 (신규)
FID 183 = '+1.04'     → 시장베이시스 (신규)
```

**선물호가잔량 FID 발견:**
```
FID 291 = '+1020.60'  → 예상체결가 (기존 FID_OI=291이 이것을 읽고 있었음 ← 버그)
FID 41, 51, 61, 71    → 호가/잔량 (확인)
```

**신규 실시간 타입 발견:**
```
파생실시간상하한: FID 305=+1078.35(상한가), FID 306=-918.65(하한가)
주식예상체결: FID 10(예상가), 11(전일비), 12(등락률%) — 선물코드로 장마감후 수신
프로그램매매: code='P00101' — FID 스캔 미완료 (다음 장중 재시도 필요)
투자자ticker: 모의투자 서버 미지원 확인 (8가지 코드 조합 모두 ret=0이나 데이터 없음)
```

---

## 2026-05-04 (오후 세션 — 부트스트랩·SGD·UI)

**작업**: SGD 치킨에그 부트스트랩 해결 + log_loss 호환성 수정 + watchdog 개선 + 대시보드 UI

### 핵심 수정 6건

| 항목 | 내용 |
|---|---|
| **[B37] SGD log_loss 크래시** | `learning/online_learner.py` `loss="log_loss"` → `"log"`. sklearn 1.0.2는 "log_loss" 미지원 → 매분 ValueError 크래시 |
| **부트스트랩 치킨에그 해결** | STEP 5 앞 early return 제거 → GBM/SGD 미학습 시 1/3 균등 예측으로 STEP 9까지 진행 → DB 저장 → 다음 분 STEP1 검증 → STEP2 learn() 호출 → SGD 학습 시작 |
| **watchdog 임계값 상향** | 60/120/180s → 90/150/240s. 1분봉 주기=60s 기준 30s 버퍼 확보로 race condition 방지 |
| **`_last_recovery_ts` 중복 복구 방지** | 동일 ts 분봉이 watchdog 복구를 반복 실행하던 버그 수정. 복구 완료 ts 기록 + `run_minute_pipeline` 진입 시 초기화 |
| **Guard-C1/C2 `notify_pipeline_ran()`** | 비정상 분봉 차단 return 전 watchdog 카운터 리셋 추가 |
| **`_dir_ko` NameError** | early return 제거 후 STEP 7 도달 가능 → `_dir_ko = "상승"/"하락"/"관망"` 정의 추가 |

### 대시보드 UI 개선 3건

| 항목 | 내용 |
|---|---|
| **파라미터 중요도 툴팁** | SHAP 개념 설명 + 업데이트 조건 (GBM 미학습 → 0.0%, 월요일 08:50 재학습 시 자동 갱신) |
| **파라미터 상관계수 툴팁** | 표시 형식 설명 + 업데이트 조건 |
| **섹션 간격 조정** | 모델상태행↔호라이즌 +8px, 섹션 구분선 앞 +16px · 뒤 +12px |

### 검증 확인

```
2026-05-04 13:44:00 [INFO] LEARNING: [OnlineLearner] 1m 초기 학습 완료
2026-05-04 13:44:00 [INFO] LEARNING: [OnlineLearner] 3m 초기 학습 완료
2026-05-04 13:44:00 [INFO] LEARNING: [OnlineLearner] 5m 초기 학습 완료
2026-05-04 13:44:00 [INFO] LEARNING: [OnlineLearner] 15m 초기 학습 완료
← log_loss 수정 + 부트스트랩 fix 후 정상 학습 확인
← 2분 만에 15m 학습 = 이전 세션 DB 15분 전 예측 활용 (정상 동작)
```

---

## 2026-05-04 (오전 세션)

**작업**: 모의투자 실시간 분봉 수신 경로 확립 + 파이프라인 watchdog 오작동 근본 수정

### 커밋 1건 (이번 세션)

| 커밋 | 내용 |
|---|---|
| (이번 세션) | fix: 모의투자 SetRealReg A0166000 + WARN 로그 분리 + 파이프라인 watchdog 수정 |

---

### [1] WARN 로그 분리 — SYSTEM.log는 INFO만, 경보는 WARN.log + 경보 탭

**문제**: WARNING 이상 메시지가 SYSTEM.log와 경보 탭 양쪽에 혼재.

**수정** (`utils/logger.py`):
- `_MaxLevelFilter(max_level)` 클래스 추가 — `levelno < max_level` 만 통과
- SYSTEM 파일 핸들러에 `_MaxLevelFilter(logging.WARNING)` 부착 → INFO 전용
- `warn_fh` (TimedRotatingFileHandler `YYYYMMDD_WARN.log`) 추가 — WARNING+ 전용

**수정** (`dashboard/main_dashboard.py`):
- `log_panel.append()`: `tag in ("WARN", "ERROR", "CRITICAL")` → 경보 탭만 기록 (`return`)

---

### [2] OPT50029 → SetRealReg 전환 (모의투자 서버 폴링 불가)

**발견**: 모의투자 서버에서 OPT50029(선물분차트요청) rows=0 — 라이브 데이터 미제공.

**수정** (`main.py`):
- 기존: `rt_code = get_realtime_futures_code()` (→ `101W06`) + `is_mock_server=True`
- 변경: `code = get_nearest_futures_code()` (→ `A0166000`) + `realtime_code=code` + `is_mock_server=False`
- 결과: SetRealReg로 A0166000 실시간 틱 구독 → 모의투자 서버에서 정상 수신 확인

---

### [3] SetRealReg 코드 불일치 버그 수정 (101W06 vs A0166000)

**원인**: 이전에 `rt_code = get_realtime_futures_code()` → `101W06` 반환. 실제 틱은 `A0166000`으로 수신 → 콜백 필터에서 전량 차단.

**수정** (`realtime_data.py`):
- `_rt_code` 필드: `101W06` → `A0166000`
- `_on_real_data()` 필터: `code.strip() != self._rt_code.strip()` 조건으로 차단 없어짐

---

### [4] 진단 로깅 추가 (sys_log — SYSTEM 레이어)

**추가 로그 포인트** (`realtime_data.py`, `api_connector.py`):
- `[RT-CB]` — 새 실시간 키 첫 수신 시 (code/type/등록키)
- `[RT-DATA]` — 틱 수신 #1~5, 이후 100회마다
- `[RT-RAW]` — raw_price/raw_vol (첫 5틱)
- `[RT-BAR]` — price/vol/bar_min/cur_min (첫 5틱)
- `[BAR-CLOSE]` — 매 분봉 확정 시 OHLCV
- `[RT-DATA] 필터제외` — 코드·타입 불일치 틱 (첫 5틱)

**검증된 동작** (2026-05-04 로그):
```
[RT-CB] code='A0166000' type='선물시세' 등록키=[('A0166000', '선물시세')]  ✅
[RT-RAW] raw_price='+1038.55' raw_vol='+1'                                  ✅
[BAR-CLOSE] ts=11:22 O=1038.55 C=1038.80 V=25  (매분 정상 확정)            ✅
```

---

### [5] run_minute_pipeline watchdog 영구 미해제 버그 수정 (B35)

**증상**: `[BAR-CLOSE]` 매 분 정상 → `[Notify] ⚠ 파이프라인 2분 지연` 여전히 발동.

**원인** (`main.py` line 424-426):
```python
if not self.model.is_ready():
    log_manager.signal("모델 미학습 상태 — 예측 건너뜀")
    return  # ← notify_pipeline_ran() 호출 없이 종료
```
모델 미학습 상태에서 STEP 5 직전 early return → `notify_pipeline_ran()` (line 667) 영구 미호출 → watchdog 2분 경보 지속.

**수정**: `return` 전에 `self.dashboard.notify_pipeline_ran()` 추가.

---

### [6] B14 OFI 영구 0 수정 — 선물호가잔량 콜백 신설

**발견 계기**: 로그에서 `[RT-CB] type='선물호가잔량'`이 이미 도착 중인 것을 확인 → 콜백만 없어서 버려지고 있었음.

**원인**: `선물시세`(FC0) FID에는 bid/ask(41/51/61/71)가 없음. `_on_real_data()`에서 읽어도 항상 0 → `ofi.update_hoga()` 미호출 → OFI=0 고정.

**수정**:
- `api_connector.py`: `register_realtime(sopt_type=)` 파라미터 추가 (`"1"` = 기존 유지 추가)
- `realtime_data.py`: `on_hoga` 콜백 파라미터 + `_on_hoga_data()` 신설. `start()`에서 선물호가잔량 추가 등록. `_on_real_data()`에서 bid/ask 읽기 제거 → `_last_bid1/ask1` 사용
- `main.py`: `_on_hoga_update()` 신설, `_on_tick_price_update`에서 OFI 코드 제거

---

## 2026-04-30 (이번 세션)

**작업**: SIMULATION 코드 전면 제거 + 자동 종료 + 패널 이전 데이터 지속 + 성장 추이 대시보드

### 커밋 3건

| 커밋 | 내용 |
|---|---|
| `4ae73ae` | refactor: SIMULATION/더미 모드 코드 전면 제거 |
| `5f1919b` | feat: 일일 마감 후 자동 프로그램 종료 + 슬랙 알림 |
| `8ae19eb` | feat: 자가학습·효과검증 이전 데이터 지속 + 성장 추이 대시보드 |

---

### [1] SIMULATION 코드 전면 제거 (commit: 4ae73ae)

**배경**: 로그에 "더미 모델 주입", "모드=SIMULATION"이 출력 → 미륵이는 실전 시스템이므로 SIMULATION 분기 자체가 불필요. 모의투자는 키움 API 계좌 레벨에서만 제어.

**제거된 코드:**

| 파일 | 제거 내용 |
|---|---|
| `main.py` | `--mode` argparse, `self.mode`, 더미 모델 주입 블록, `stop_sim_timer()` 호출, `argparse` 임포트 |
| `dashboard/main_dashboard.py` | `sim_mode` 파라미터, `_sim_timer`, `_start/_stop_sim_timer()`, `_sim_tick()` 130줄 |
| `model/multi_horizon_model.py` | `force_ready_for_test()` 더미 모델 주입 메서드 |
| `config/settings.py` | `TRADE_MODE = "SIMULATION"` 상수 |

**결과**: `python main.py` 단일 경로. 모의/실전 구분은 키움 계좌 레벨 전용.

---

### [2] 일일 마감 후 자동 종료 + 슬랙 알림 (commit: 5f1919b)

**흐름**: 15:40 `_scheduler_tick` → `daily_close()` 완료 → 슬랙 종료 알림 → `QTimer.singleShot(15_000, _auto_shutdown)` → `_qt_app.quit()`

**슬랙 종료 알림 내용**: 거래수 / 승패 / 승률 / PnL / 재학습 결과 / 다음 시작 안내 (내일 08:45)

**15초 대기 이유**: Slack 큐 워커가 HTTP 전송(최대 5초) + rate-limit 1초/건 처리 대기. Qt 이벤트 루프는 계속 돌아 UI 반응 유지.

**신규 메서드**: `_auto_shutdown()` — `logger.info` + `log_manager.system` + `_qt_app.quit()`

---

### [3] 자가학습·효과검증·추이 패널 이전 데이터 지속 (commit: 8ae19eb)

**문제**: 재시작 후 08:45~09:00 사이 파이프라인 미실행 구간에 자가학습/효과검증 패널이 빈값 표시.

**해결**: `_restore_panels_from_history()` 신설 — 로그인 후 500ms 뒤 DB 이력으로 세 패널 선조회.
- EfficacyPanel: trades.db/predictions.db 쿼리 → 어제까지 누적 데이터 즉시 표시
- LearningPanel: GBM 상태·raw candle 수 등 DB 기반 값 즉시 표시
- TrendPanel: 일/주/월/연간 집계 즉시 표시

**스냅샷 저장**: `daily_close()` 내 `save_daily_stats()` — SGD정확도·검증건수를 `daily_stats` 테이블에 영속. 다음날 SGD 정확도 표시에 사용.

---

### [4] 📈 성장 추이 대시보드 신설 (commit: 8ae19eb)

**신규 클래스**: `TrendPanel` (~200줄) — 중앙 탭 7번째 `"📈 성장 추이"`

**구성**:
- 상단 스파크라인 3줄: PnL `▁▂▃▄▅▆▇█` / 승률 / SGD정확도 (최근 20일)
- 4탭: 일별(30일) / 주별(12주) / 월별(12개월) / 연간
- 각 탭: 기간·거래·승/패·승률·PnL(원)·SGD정확도(일별만) 스크롤 테이블
- 색상: 승률 기준(≥60%초록/≥53%청록/≥45%주황/<45%빨강), PnL(양수초록/음수빨강)

**갱신 시점**: 시작 선조회 + 15:40 일일 마감 후 자동 갱신

**신규 DB 기능** (`utils/db_utils.py`):
- `daily_stats` 테이블: date/trades/wins/pnl_krw/sgd_accuracy/verified_count
- `save_daily_stats()` / `fetch_trend_daily/weekly/monthly/yearly()`
- 집계 쿼리는 trades.db 직접 GROUP BY (별도 테이블 불필요)

**탭 순서 변경**: 다이버전스/SHAP/청산/진입/🧠자가학습/🎯효과검증/**📈성장추이**/알파봇

---

## 2026-04-30 (심야 세션)

**작업**: 🎯 학습 효과 검증기 패널 신설 — 자가학습이 실제로 수익에 기여하는가 시각화

### EfficacyPanel 구현

**핵심 질문**: "높은 신뢰도 예측이 실제로 돈을 버는가?"

#### 신규 파일·함수

- `utils/db_utils.py`: 검증 쿼리 4종 추가
  - `fetch_calibration_bins(days_back=30)` — confidence 구간별(5단위) 실제 적중률
  - `fetch_grade_stats()` — 등급별 건수/승률/평균pts/합계pts
  - `fetch_regime_stats()` — 레짐별 건수/승률/평균pts
  - `fetch_accuracy_history(limit=200)` — 최근 N개 예측 correct 이력
- `dashboard/main_dashboard.py`: `class EfficacyPanel` (~250줄) 신설
  - Section 1: 신뢰도 캘리브레이션 테이블 (✓우수/≈양호/▲과소신뢰/▼과신)
  - Section 2: 등급별 매매 성과 테이블 (A/B/C/X/?)
  - Section 3: 학습 성장 곡선 스파크라인 `▁▂▃▄▅▆▇█` + 초기 vs 최근 Δ
  - Section 4: 레짐별 성과 게이지 바 (RISK_ON/NEUTRAL/RISK_OFF)
  - 상단 KPI 배지 4개: 전체승률/A등급승률/캘리브레이션점수/학습효과Δ
  - 종합 평가 배너: ✅/⚡/⚠️ 자동 판정
- `DashboardAdapter.update_efficacy(data)` — 위임 메서드 추가
- `main.py`:
  - `_gather_efficacy_stats()` 메서드 추가 (DB 쿼리 → dict 반환)
  - `_efficacy_tick` 카운터 추가
  - 5분마다(`_efficacy_tick % 5 == 1`) `update_efficacy()` 호출

#### 탭 순서 변경
- 기존: 다이버전스/SHAP/청산/진입/🧠자가학습/알파봇
- 변경: 다이버전스/SHAP/청산/진입/🧠자가학습/**🎯효과검증**/알파봇

---

## 2026-04-30 (저녁 세션)

**작업**: 손익 추이 패널 신설 — 일별·주별·월별 누적 P&L 테이블

### PnlHistoryPanel 구현
- 5층 모니터링 로그에 6번째 탭 **"📊 손익 추이"** 추가
- **요약 카드 6개**: 거래일·총거래·총승률·총손익·최대MDD·최장연승 — 색상 조건부 갱신
- **일별 테이블** (60일 최신→구): 날짜·거래·승·패·승률·P/L pt·P/L원·누적원
  - 수익일: 연한 초록(15,45,25) / 손실일: 연한 빨강(50,18,18) 행 배경
  - 당일 행 황색 + 볼드 강조
- **주별 테이블** (13주): MDD원 컬럼 추가
- **월별 테이블**: 샤프 지수 (월 내 일별 PnL 연율화 √252) 추가
  - 샤프 ≥1.0: 초록 / ≥0.5: 노랑 / <0: 빨강
- `QTableWidget` 다크테마 스타일링, `QHeaderView.Stretch` 전체 컬럼 자동 비율 분배

### 데이터 흐름
- `db_utils.fetch_pnl_history(limit_days=90)`: 체결 완료 거래 SELECT
- `main._refresh_pnl_history()`: `_post_exit()` + `daily_close()` + `_restore_daily_state()` 3곳 호출
- 임포트: `QTableWidget·QTableWidgetItem·QHeaderView` 추가

---

## 2026-04-30 (오후 세션)

**작업**: 재시작 연속성 — 당일 거래 이력 대시보드 복원 + 세션 카운터 + UI 개선

### PnL 탭 갱신 누락 수정 [B27/B28]
- `_post_exit()`: 청산 직후 `update_pnl_metrics()` + `append_pnl_log()` 즉시 호출
- `_execute_entry()`: 진입 시 `append_pnl_log()`로 진입 이벤트 PnL 탭 기록

### UI 폰트 시인성 개선
- 전체 하드코딩 `font-size:Xpx` → `S.f(X)` 교체 (특히 5층 모니터링 로그 QTextEdit)
- `ScreenScale` 전면 재작성: `fit_scale = min(sw/1680, sh/1000)` + `dpi_bonus=(dpr-1)×0.10`
  - 3840×2160 @ 150% DPI → 자동 1.45× 적용 (기존 1.30× 고정)
  - `S.info()` 헤더에 `3840×2160 (DPI 1.50× UI 1.45×)` 표시

### 재시작 연속성 [B29]
- **`PositionTracker.restore_daily_stats(rows)`**: trades.db 당일 행으로 일일 PnL·승패 통계 재적산
- **`LogPanel.append_restore(key, msg, ts, val)`**: 이탤릭·회색 `[복원]` 태그 항목 표시
- **`LogPanel.append_separator(key, msg)`**: 탭 내 `<hr>` 구분선
- **`DashboardAdapter`**: `append_restore_trade/pnl()`, `append_trade/pnl_separator()` 추가
- **`db_utils.fetch_today_trades(today_str)`**: 당일 체결 거래 SELECT 헬퍼
- **`main._increment_session()`**: `data/session_state.json`에 당일 세션 번호 누적
- **`main._restore_daily_state()`**: `run()` 내 `dashboard.show()` 직후 호출
  - trades.db 당일 행 재생 → 주문/체결·손익 탭에 [복원] 이탤릭 항목
  - 세션 구분선 `── 세션 #N 시작 — X건 복원 ──`
  - `position_tracker.restore_daily_stats()` 연동

---

## 2026-04-30 (오전 세션)

**작업**: 대시보드 시뮬 FILL 이상가격 이상점 진단 + 시뮬/실거래 분리 수정

### 이상점 진단
- 로그: `[FILL] FILL 매도 5계약 @388.48 슬리피지 1.4틱` — 실거래 가격(~1007pt)과 대비 비정상 가격
- **원인**: `MireukDashboard`가 `kiwoom=None`으로 생성되면 무조건 `_start_sim_timer()` 호출. 타이머의 초기 가격이 `388.50` 하드코딩 → 키움 연결 전 약 수초~수십초 동안 시뮬 FILL 로그(388.xx)가 주문/체결 탭에 출력됨
- 실제 거래 영향: 없음 (UI 패널 출력만, `position_tracker` 미영향)

### 수정 (`dashboard/main_dashboard.py`, `main.py`)
- `MireukDashboard.__init__(sim_mode=True)` 파라미터 추가 → `sim_mode=False`이면 타이머 미생성
- `DashboardAdapter.__init__(sim_mode=True)` + `create_dashboard(sim_mode=True)` 동일하게 전파
- `main.py`: `create_dashboard(sim_mode=(self.mode == "SIMULATION"))` — live 모드는 시뮬 타이머 자체 없음
- `main.py`: `stop_sim_timer()` 호출을 `if self.mode == "SIMULATION":` 조건 내부로 이동
- `_sim_tick()` FILL/PENDING 로그 앞에 `[SIM]` 접두사 추가

---

## 2026-04-29 (야간 세션)

**작업**: 멀티 호라이즌 예측 데이터 흐름 점검 + 2개 버그 수정

### 진단
- 대시보드에서 1분~30분 6개 카드가 모두 동일한 값(72.2%) 표시
- 원인 1 (실거래): `main.py` `_preds_ui` 구성 시 `1-confidence` 근사 → 3클래스 확률 합산 오류
- 원인 2 (시뮬): 단일 `trend` 값으로 6개 호라이즌 생성 → 값 분산 없음

### 수정
- **main.py** L359-361: `_preds_ui` 확률값을 `r["up"]`/`r["down"]`/`r["flat"]` 직접 참조
- **main_dashboard.py** L1555-1563: 호라이즌별 독립 σ `[0.06, 0.08, 0.10, 0.13, 0.16, 0.20]` 적용. `hold` → `flat` 키 통일

---

## 2026-04-29 (오후 세션)

**작업**: 대시보드 3개 탭 데이터 배선 완성 + 버그 7종 수정

### 주문/체결 탭 툴팁
- `_ORDER_TAB_TIP` 상수: 진입 흐름(①~⑤) + 청산 흐름(P1~P6) HTML 요약
- `QToolTip` CSS 다크테마, `setTabToolTip()` 적용

### 외인 데이터 "-" 원인 진단 및 수정 [B16~B18]
- **근본 원인**: `InvestorData` 임포트·인스턴스화 없음 → `feature_builder.build(supply_demand=None)` 고정
- `main.py`: `InvestorData` import + `__init__` 인스턴스화 + STEP 4 `fetch_all()` + `supply_demand` 전달
- `main.py` STEP 4 후: `update_divergence()` 매분 호출 (rt_bias/fi_bias/contrarian/div_score 계산)
- `DivergencePanel.update_data()`: fi_call/fi_put/fi_strangle 카드 setText 누락 추가
- `connect_kiwoom()`: `investor_data._api = self.kiwoom` 주입
- `daily_close()`: `investor_data.reset_daily()` 추가

### 청산 관리 탭 데이터 배선 [B23~B25]
- **근본 원인**: `main.py`에 `update_position()` 호출 없음 → 청산 패널에 실제 포지션 데이터 미전달
- **B23** (`main.py`): STEP 8 직후 `update_position()` 추가 — `PositionTracker` 실제 값(`stop_price`=트레일링 스톱, `tp1_price`, `tp2_price`, `entry_time`, `partial_1/2_done`) 전달
- **B24** (`ExitPanel.update_data()` 재작성):
  - `status='FLAT'` → `_reset_display()` — 모든 필드 "——" 초기화
  - `trail_stop` = 현재 `stop_price` (트레일링 이동 반영), `hard_stop` = entry±ATR×1.5 (최초값)
  - 미실현 손익: `(cur−entry) × mult × qty × 500,000원` (LONG/SHORT 방향 반영)
  - 보유 시간: `entry_time`에서 경과 분 계산
  - 부분청산 바: `partial1`/`partial2` 플래그 → "완료/대기" + 프로그레스바 100/0
- **B25** (시뮬 루프): `status='LONG'` 키 추가, `stop`/`tp1`/`tp2` 구조화, `partial1`/`partial2` 틱 기반 시뮬

### 진입 관리 탭 버그 4종 수정 [B19~B22]
- **B19**: 체크리스트 평가를 CB·시간 조건 블록 밖으로 분리 → FLAT+방향 있으면 항상 평가
- **B20**: `checks.get(attr, None)` — None이면 회색 "—" (기존: 빈 dict → 빨간 X)
- **B21**: `update_entry(qty=0)` 파라미터 + `e_qty` 라벨 갱신
- **B22**: `EntryPanel.update_stats()` + `DashboardAdapter.update_entry_stats()` 추가, STEP 9 후 매분 호출

---

## 2026-04-28 (오후 세션)

**작업**: 모의투자 실거래 검증 + 이상점 진단·수정 + 대시보드 데이터 배선 완성

### Path B 인프라 구축 (커밋 60233d6)
| 파일 | 내용 |
|---|---|
| `config/settings.py` | `RAW_DATA_DB` 경로 추가 |
| `utils/db_utils.py` | `raw_candles` + `raw_features` 테이블, save/get 함수 4개 추가 |
| `main.py` STEP 4 | `save_candle(bar)` + `save_features(ts, features)` 호출 → 13거래일 데이터 축적 시작 |
| `learning/prediction_buffer.py` | actual 라벨: `raw_candles` 실종가 기반 계산으로 교체 (placeholder 제거) |
| `utils/logger.py` | DEBUG 레이어 `logging.DEBUG` 고정 (INFO 레벨이 debug() 출력 차단하던 버그 수정) |

### 디버그 로그 추가 (커밋 60233d6)
`[DBG-F4]` ATR floor + 핵심 피처 / `[DBG-F6]` 호라이즌별 예측 / `[DBG-CB]` CB 상태 /
`[DBG-F7]` 진입 4조건 / `[DBG-F7a]` 체크리스트 9항목 / `[DBG-F7b]` 사이저 입출력 /
`[DBG-F8]` 포지션 손절·TP·미실현 PnL / `[DBG-STOP]` 하드스톱 발동 정보

### 대시보드 데이터 배선 완성 (커밋 c8018ed)
| 버그 | 수정 |
|---|---|
| 신뢰도 `lbl_conf` 항상 "— %" | `PredictionPanel.update_data(conf=)` 파라미터 추가 |
| 호라이즌 카드·체크리스트 갱신 안됨 | `run_minute_pipeline` 에서 `update_prediction()` + `update_entry()` 매분 호출 |
| 5층 로그 탭 1·2·3 빈 화면 | `log_manager.subscribe()` SYSTEM/TRADE/LEARNING 배선 연결 (`__init__`에서) |
| PnL 수치 "+12,000원" 하드코딩 | `LogPanel.update_pnl_metrics()` 추가, 매분 실시간 전송 |

### 실거래 이상점 수정 (커밋 5db134e)
| # | 이상점 | 수정 |
|---|---|---|
| B13 | CVD buyvol=100% — FC0 FID10 부호가 틱 방향 아님 | tick test (prev_price 비교 Lee-Ready 근사)로 교체 |
| B15 | 손절가 아닌 close가로 청산 (항상 불리) | `_check_exit_triggers(bar=)` 전달, exit_price = stop_price 보정 |

### 미해결 이슈
| # | 내용 |
|---|---|
| B14 | bid/ask=0 — FC0에 FID41/51 미포함, FH0(선물호가잔량) 별도 등록 필요 → OFI 영구 0 |

### 실거래 실행 결과 (로그 기반)
- ATR floor 0.75pt 완전 검증 (`stop_dist=0.75pt` 정확히 확인)
- 체크리스트 8/9 정상 평가 (foreign 미구현 1개만 ✗)
- 진입 LONG @1008.40, stop=1007.65 정상 진입
- stop_dist=-0.15pt → 손절 발동 예상 (TRADE 로그 별도 확인)
- CVD/OFI 0값: CVD는 3분 이상 누적 후 계산되므로 초기 0 정상

---

## 2026-04-27 (오전~오후 세션)

**작업**: 실시간 분봉 파이프라인 end-to-end 정상 동작 달성

### 핵심 버그 수정 (7건)

| # | 파일 | 버그 | 수정 |
|---|---|---|---|
| B06 | api_connector.py | 근월물 코드 포맷 오류 (`101W06` 날짜계산 fallback) | `GetFutureCodeByIndex(0)` = `A0166000` 0순위 추가 |
| B07 | constants.py | `RT_FUTURES="FC0"` — Kiwoom sRealType은 한국어 명칭 | `"FC0"` → `"선물시세"`, `"FH0"` → `"선물호가잔량"` |
| B08 | api_connector.py | GetRepeatCnt record_name fallback 오류 (`or rq_name`) | `meta.get("record_name","")` — 빈 문자열 그대로 전달 |
| B09 | emergency_exit.py | `PositionTracker.get_position()` 없음 (AttributeError) | 속성(`status`/`quantity`/`entry_price`) 직접 읽기 + `set_futures_code()` 추가 |
| B10 | main.py | `run_minute_pipeline` — candle `ts`가 datetime 객체인데 str 취급 | `ts_raw.strftime(...)` 변환 추가 |
| B11 | main_dashboard.py | `PredictionPanel._build()`에서 `_hz_labels` 미초기화 | `_build()` 맨 앞에서 dict 초기화 |
| B12 | main_dashboard.py | `mk_val_label(align=...)` 파라미터 없음 (TypeError) | `align=None` 파라미터 추가 |

### 기능 추가
- 대시보드 헤더 우측: 해상도 아래에 커밋 해시(`#4a00e5e`) 표시

### 검증 결과
- `GetFutureCodeByIndex(0)='A0166000'` — 근월물 코드 확정
- `type=선물시세` 틱 정상 수신 확인
- `on_candle_closed` → `run_minute_pipeline` 호출 확인 (파이프라인 동작)
- 대시보드 정상 기동 확인

---

## 2026-04-27 (새벽 세션)

**작업**: dev_memory 구조 신설 + CLAUDE.md 작성
- Claude 프로젝트 메모리(`project_futures.md`, `feedback_kiwoom_com.md`)를 dev_memory로 이전
- CURRENT_STATE / DECISION_LOG / SESSION_LOG / NEXT_TODO 작성
- CLAUDE.md: 절대 원칙·파이프라인·확률 기준·Phase 현황 정리

---

## 2026-04-26 (세션 3~4회차 합산)

**작업**: Phase 0~6 전체 코드 구현 완료

### Phase 0 (완료)
- 전체 폴더 구조 생성
- config/settings.py, constants.py, logging_system 등 인프라

### Phase 1 (코드 완료)
- `collection/kiwoom/api_connector.py` — KiwoomAPI (QAxWidget, 로그인/TR/실시간)
- `collection/kiwoom/realtime_data.py` — FC0 틱 → 1분봉 조립, OPT10080→OPT50029 초기로드
- `collection/kiwoom/latency_sync.py` — HFT 타임스탬프 동기화 (v7.0)
- `main.py` — QApplication + QTimer 이벤트 루프, on_candle_closed → run_minute_pipeline

**버그 수정**:
- TR 코드 OPT10080 → OPT50029
- COM 콜백 스택 오버런 패턴 수정
- record_name vs rq_name 혼동 수정
- GetCommDataEx → GetCommData
- 근월물 조회 3단계 fallback

### Phase 2 (코드 완료)
- `safety/kill_switch.py`, `safety/emergency_exit.py`, `safety/circuit_breaker.py`
- `backtest/slippage_simulator.py`, `backtest/transaction_cost.py`
- `backtest/performance_metrics.py`, `backtest/walk_forward.py`, `backtest/report_generator.py`
- `main.py` — KillSwitch + EmergencyExit 연결

### Phase 3 (코드 완료)
- Week 8: microprice, lob_imbalance, queue_dynamics, multi_timeframe, htf_filter, round_number, vpin, cancel_ratio
- Week 9: meta_confidence, calibration
- Week 10: vol_targeting, dynamic_sizing
- Week 11: herding, regime_specific, micro_regime, regime_strategy_map

### Phase 4 (코드 완료)
- RL: environment, ppo_agent, reward_design, policy_evaluator
- 베이지안: bayesian_updater
- 뉴스: news_fetcher, kobert_sentiment, news_features

### Phase 5 사전 코딩 (완료)
- strategy/entry: time_strategy_router, staged_entry, entry_manager
- strategy/exit: exit_manager
- collection/kiwoom: investor_data, option_data
- collection/macro: macro_fetcher
- learning: batch_retrainer, shap_tracker
- dashboard: main_dashboard (5창 다크테마)

### Phase 6 (코드 완료)
- 유전자 알파: alpha_gene, alpha_evaluator, random_searcher, genetic_searcher
- alpha_pool, evolution_engine, alpha_scheduler, bot_main
- 승격 기준: IC≥0.02, Sharpe≥0.8, OOS Sharpe>0, n_samples≥300

---

## 2026-04 (초기)

**작업**: 프로젝트 설계
- 시스템 아키텍처 v4 설계 완료
- v6.5 보완 검토 (시간대·분할진입·멀티타임프레임·미시레짐 채용)
- v7.0 Gemini 제안 검토 후 6/6 전량 채용
- Hurst Exponent 공식 오류 수정 (reg[0]×2.0 → reg[0])
