# 미륵이 증거 다이제스트 — 2026-09-28 / PRE

- 생성 2026-09-28 08:59:06 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/rcw-01cno3vmgxfy5t2hnq1dvod2/mnt/futures`
- 점검 범위: pre (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260928` · `2026-09-28` · `260928` · `0928`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **15개** 파일 · 15개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260928.log` | 125B | 09-28 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260928.log` | 140B | 09-28 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260928.json` | 245B | 09-28 08:58 |
| `launcher_{DATE}_084001_3298.log` | 1 | `logs/Mireuk_batch/launcher_20260928_084001_3298.log` | 53.7KB | 09-28 08:58 |
| `{DATE}_DATA.log` | 1 | `logs/20260928_DATA.log` | 894B | 09-28 08:58 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260928_DEBUG.log` | 0B | 09-28 08:40 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260928_HEALTH.log` | 0B | 09-28 08:40 |
| `{DATE}_HOGA.log` | 1 | `logs/20260928_HOGA.log` | 1.3MB | 09-28 08:59 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260928_LEARNING.log` | 55.3KB | 09-28 08:59 |
| `{DATE}_MICRO.log` | 1 | `logs/20260928_MICRO.log` | 32.6KB | 09-28 08:59 |
| `{DATE}_PROBE.log` | 1 | `logs/20260928_PROBE.log` | 12.1KB | 09-28 08:58 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260928_SIGNAL.log` | 6.5KB | 09-28 08:59 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260928_SYSTEM.log` | 27.0KB | 09-28 08:59 |
| `{DATE}_TRADE.log` | 1 | `logs/20260928_TRADE.log` | 167B | 09-28 08:41 |
| `{DATE}_WARN.log` | 1 | `logs/20260928_WARN.log` | 2.7KB | 09-28 08:58 |

## 2. 코드·커밋 상태

- HEAD `c2d5eee` · 브랜치 `v9-dev` · 미커밋 1건 · 실질 변경 **미측정**(git diff 실패) · 인덱스락 없음
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
```
M docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md
```

**당일(2026-09-28) 커밋**
```
(당일 커밋 없음 — 커밋 가능 상태였음)
```

**최근 커밋 12건**
```
c2d5eee [MW0601] 631차: Claude 앱 — 19:20 업데이트 창이 VS Code Claude Code 까지 죽이던 것 수정 + 절전 해제 시 앱 자동 복구
91f5afe [MW0601] 631차: PC 종료→절전 해제→Cybos Plus→미륵이 실전 흐름 확인 기록 (1차 로그인 37초·DB 초기화 0.4초)
ddcddef [MW0601] 631차 딥다이브2 후속: Cybos 연결 확인을 매번 새 프로세스로 — 자동로그인이 성공을 실패로 오판해 세션을 끊던 원인
b7b274b [MW0601] 631차 딥다이브2: 15:58 기동 실패 — 금요일 종료 작업이 최대 절전이라 Cybos 세션만 끊긴 채 CpStart 생존
da5a604 [MW0601] 631차 후속: GP 분석 캐시를 GP_test/ 로 분리 — 파일은 남기고 미추적 목록에서만 숨김
3d68065 [MW0601] 631차 후속: git 밖 작업 코드 6개 — 섀도 게이트·피터 수집기·롤 정책 대조 (라이브 미배선)
4575a77 [MW0601] 631차 후속: 미커밋 기록 일괄 — 매일점검 리포트·증거, 주간 리포트 0923, GP 연구 문서
ddf376c [MW0601] 631차 후속: data/peter_feed/ 무시 + 송신 도구 git add -f
b4f7127 [MW0601] 631차 기록: 0926 휴장일 점검 리포트 · 딥다이브 · 구현 결과 + dev_memory
44c0a71 [MW0601] 631차 F-4: 증거 수집기 휴장일 인식 — 거래일 전제 적신호 9종 생략
bc81108 [MW0601] 631차 F-3·F-3b: 런처는 자동로그인이 끝나고 연결이 10초 유지된 뒤 출발
4aecc7f [MW0601] 631차 F-6·F-7·F-8: 자동로그인 재시도가 살아 있는 세션을 죽이지 않게
```

PC명 태그 규약: 최근 12건 모두 `[MW####]` 접두 확인

## 3. 설정 불변식 — 절대원칙·한시예외 (config/settings.py)

| 상수 | 현재값 | 기대값 | 판정 | 왜 보는가 |
|---|---|---|---|---|
| `CB_CONSEC_STOP_LIMIT` | `3` | `3` | 일치 | [2026-09-02 519차] 모의 한정 예외 해제 — 9999→3 복원(절대원칙 ② 문구와 일치). ⚠ 값 복원만으로 실전 전환 기준 ⑤가 충족되지 않는다 … |
| `CB3_P4_GRADE_BLOCK_ENABLED` | `False` | `False` | 일치 | 30m 퇴역으로 CB③-P4 상시 RESTRICTED 고착 → 차단만 비활성 (296·297차) |
| `FP_CRITICAL_GRADE_BLOCK_ENABLED` | `False` | `False` | 일치 | PSI 계측 결함으로 차단만 비활성. 371차 분위수 재설계 후 라이브 관찰 중 |
| `MAX_CONTRACTS` | `3` | `3` | 일치 | 431차 10→3 인하. 실전 자본 확정 시 재산출 대상 |
| `SIZING_TARGET_CAPITAL_ENABLED` | `True` | `True` | 일치 | 모의투자 한정. False 전환은 단독 지시로 읽지 말 것 (손실 구간 복원 위험) |
| `SIZING_TARGET_CAPITAL_KRW` | `50_000_000` | — | 값 확인 | 현행 5천만원. 실전 전환 기준 ⑧의 남은 해제 조건 |
| `HURST_WINDOW_N` | `90` | `90` | 일치 | 317차 재보정. 26주 WFA마다 재검증 |
| `HURST_MAX_LAG` | `9` | `9` | 일치 | 317차 재보정. 26주 WFA마다 재검증 |
| `VALIDATION_REPORT_KEEP_WEEKS` | `4` | `4` | 일치 | 주간 리포트 FIFO 보관 |
| `CB_ACCURACY_MIN_30M` | `0.28` | `0.28` | 일치 | CB③ 임계. 98차(2026-06-02) FLAT 예측 제외 + 0.35→0.28. CLAUDE.md 문구 정정 완료(461차 F-3) |
| `CB_ACC_RESTRICTED_MIN` | `0.30` | `0.30` | 일치 | WATCH→RESTRICTED 경계. 30m 구조적 성능(0.3052)과 거의 같아 CB③-P4 비활성의 직접 원인 |
| `CB_ACCURACY_MIN_30M_STRICT` | `0.42` | `0.42` | 일치 | 과신 연속 시 강화 임계 (0.50→0.42 완화) |
| `TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED` | `False` | `False` | 일치 | 311차 후속4가 처음부터 False로 신설(섀도). CLAUDE.md 한시예외 4번째 + 실전 전환 기준 ⑨ 등재(461차 F-4). ⚠ 복원 선행조건: sp… |
| `LIMIT_PIN_ENTRY_BLOCK_ENABLED` | `True` | `True` | 일치 | 호가 상하한 핀 진입 차단 — 켜져 있어야 정상 |
| `HURST_SOFT_BLOCK_ENABLED` | `True` | `True` | 일치 | Hurst 소프트 차단(사이즈 0.5배). 316~318차 재보정 계열 |
| `HEALTH_DEGRADED_BLOCK_AUTO_ENTRY` | `True` | `True` | 일치 | Degraded 상태 자동진입 차단 — 켜져 있어야 정상 |
| `CB_PIPE_PAUSE_MS` | `5_000` | `5_000` | 일치 | CB⑤ 실질 구현. `CB_API_LATENCY_LIMIT` 은 Kiwoom 레거시로 Cybos에서 미사용 |
| `ENTRY_HORIZON_B1` | `3.2` | `3.2` | 일치 | 1m/3m 경계 [374차 1.5→3.5, 387차 3.5→3.2] — 드리프트 항목 |
| `ENTRY_HORIZON_B2` | `4.4` | `4.4` | 일치 | 3m/5m 경계 [374차 2.5→4.0, 387차 4.0→4.4] — 드리프트 항목 |
| `CB_DAILY_HALT_FULL_BLOCK` | `3` | `3` | 일치 | HALT 3회 → 완전 관망 |
| `FUTURES_COMMISSION_RATE` | `_BROKER_SPEC["one_way_commission_rate"]` | `_BROKER_SPEC["one_way_commission_rate"]` | 일치 | 495차 후속 — 로그인 채널 감지로 **파생**. 숫자 리터럴로 되돌아가면 회귀(2026-05-11~08-25 6개월간 1/6.54 사고). 실제 요율은 채널… |
| `FUTURES_COMMISSION_RATE_EFFECTIVE_FROM` | `_BROKER_SPEC["effective_from"]` | `_BROKER_SPEC["effective_from"]` | 일치 | 시계열 불연속 경계 — 이 날짜 앞뒤 손익 직접 비교 금지의 근거(461차 mdd_pct 유형) |
| `COST_MODEL_COMMISSION_RATE` | `0.000015` | `0.000015` | 일치 | 캠페인·섀도 계측 전용 요율. 라이브와 **의도적으로 갈라져 있다**(493차 F-3 핀). 주간회의 승인 시 라이브와 같은 값으로 교체 — 그때 이 기대값도 … |
| `COST_MODEL_COMMISSION_RATE_PINNED` | `True` | `True` | 일치 | 라이브와 계측이 갈린 상태임을 매일 명시. 승인 교체 후에도 True면 그것이 이상 |
| `VALIDATION_CAMPAIGN["mode"]` | `standing` | `standing` | 일치 | 2026-08-01 상시 운영 전환 |

> 이 표는 **의도한 예외가 여전히 의도대로인지** 보는 것이다. `불일치`는 누군가 바꿨다는 뜻이고, 바꿨다면 `dev_memory/DECISION_LOG.md` 에 근거가 있어야 한다.

_이 브랜치(`v9-dev`) 범위 밖 **5건** — 표에서 제외했다(계측 4원칙 ③): `MODEL_LABEL_STATE_UNLOCK_ENABLED`(→dev), `PRE_RETRAIN_DONE_BY_EOD_ENABLED`(→dev), `ZONE_ENTRY_BAN_ENFORCE`(→dev), `ZONE_ENTRY_BAN_SHADOW_ENABLED`(→dev), `PIPE_LATENCY_EXCLUDE_MODEL_SWAP`(→dev)._
> 제외는 "없어도 된다"가 아니라 "이 브랜치에는 기능 자체가 없다"는 뜻이다. 이식 여부는 별개 안건이며 주간회의에서 정한다.

### 차단 게이트 전수 인벤토리 — 38개 중 **9개 꺼짐**

| 플래그 | 값 | 기록됨 |
|---|---|---|
| `CB3_P4_GRADE_BLOCK_ENABLED` | False | 기록됨 |
| `FORCE_FLAT_GUARD_ORDER_ENABLED` | False | 기능토글 |
| `FP_CRITICAL_GRADE_BLOCK_ENABLED` | False | 기록됨 |
| `FREEZE_SENTINEL_KILL_ENABLED` | False | 기능토글 |
| `HEALTH_DEGRADED_BLOCK_MANUAL_ENTRY` | False | 기록됨 |
| `LIMIT_ENTRY_FIRST_ENABLED` | False | 기능토글 |
| `LOSS_TIER1_QTY1_ENABLED` | False | 기능토글 |
| `TICKUI_TRACE_ENABLED` | False | 기능토글 |
| `TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED` | False | 기록됨 |
| `ATR_EXPIRY_CEILING_ENABLED` | True | — |
| `CHASE_FILTER_ENABLED` | True | — |
| `CONF_STUCK_BOOST_ENABLED` | True | — |
| `COUNTERTREND_CAP_ENABLED` | True | — |
| `DAILY_CLOSE_FORCE_EXIT_ENABLED` | True | — |
| `FORCE_FLAT_GUARD_ENABLED` | True | — |
| `FREEZE_SENTINEL_ENABLED` | True | — |
| `FREEZE_WATCHDOG_ENABLED` | True | — |
| `HEALTH_DEGRADED_BLOCK_AUTO_ENTRY` | True | — |
| `HEALTH_DEGRADED_ENABLED` | True | — |
| `HEALTH_LATENCY_TREND_ENABLED` | True | — |
| `HEALTH_POLICY_HOT_RELOAD_ENABLED` | True | — |
| `HEALTH_RETRAIN_RELAX_ENABLED` | True | — |
| `HURST_REGIME_ATR_MULT_ENABLED` | True | — |
| `HURST_SOFT_BLOCK_ENABLED` | True | — |
| `LIMIT_PIN_ENTRY_BLOCK_ENABLED` | True | — |
| `LOSS_TIER1_ENABLED` | True | — |
| `LOSS_TIER1_QTY1_TICK_ENABLED` | True | — |
| `LOSS_TIER1_TICK_ENABLED` | True | — |
| `MAIN_STALL_TRACEBACK_ENABLED` | True | — |
| `MC_CONF_GAP_ALERT_ENABLED` | True | — |
| `OPTION_BOOK_ENABLED` | True | — |
| `SHINDONG_ENABLED` | True | — |
| `SHINDONG_RUNNER_SHADOW_ENABLED` | True | — |
| `SIGNAL_DECAY_EXIT_ENABLED` | True | — |
| `SIZING_TARGET_CAPITAL_ENABLED` | True | — |
| `TP1_TICK_ENABLED` | True | — |
| `VOLATILITY_BURST_GUARD_ENABLED` | True | — |
| `WEEKLY_OPTION_FLOW_ENABLED` | True | — |

## 4. 마커·리포트 · 로그 다이제스트

_본문 미열람(설정): `20260928_HOGA.log` 1.3MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/11개 (중요도순). 제외: `launcher_20260928_084001_3298.log`, `freeze_sentinel_20260928.log`, `force_flat_guard_20260928.log`_

### `logs/20260928_TRADE.log` — 167B · 2행 · 최종 08:41:08

- 형식 평문 · 시각 인식 2행 · INFO=2

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-28 08:41:02 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-28 08:41:08 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
  …
2026-09-28 08:41:02 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-28 08:41:08 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×2

**컴포넌트 상위 15** — `Position`×1, `ProfitGuard`×1

### `logs/20260928_WARN.log` — 2.7KB · 31행 · 최종 08:58:35

- 형식 평문 · 시각 인식 31행 · WARNING=31

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-28 08:41:11 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-28 08:41:11 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 62ms
2026-09-28 08:41:11 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 187ms account=333044256
2026-09-28 08:41:11 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-09-28 08:41:11 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-09-28 09:00:04 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4219ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4219 band=INFO since_pipe_s=0.1
2026-09-28 09:00:04 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 37.6ms | size=1955x1124 candles=16 grid=11.0 spans=0.0 candles=0.7 dir=0.0 regime=0.0 markers=0.0 axes=24.5 cross=0.0 | slow_cnt=2 total_cnt=8 overlay_cnt=54
2026-09-28 09:00:14 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 37.3ms | size=1955x1124 candles=16 grid=13.8 spans=0.0 candles=0.8 dir=0.0 regime=0.0 markers=0.0 axes=20.7 cross=0.0 | slow_cnt=3 total_cnt=9 overlay_cnt=82
2026-09-28 09:00:16 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 42.5ms | size=1955x1124 candles=16 grid=13.4 spans=0.0 candles=0.7 dir=0.0 regime=0.0 markers=0.0 axes=26.9 cross=0.0 | slow_cnt=4 total_cnt=10 overlay_cnt=87
2026-09-28 09:00:16 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 36.8ms | size=1955x1124 candles=16 grid=14.5 spans=0.0 candles=0.7 dir=0.0 regime=0.0 markers=0.0 axes=20.1 cross=0.0 | slow_cnt=5 total_cnt=11 overlay_cnt=87
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 11 | 08:41:11 | 09:00:04 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `SessionBackfill` | 6 | 08:41:42 | 08:41:42 | OHLCV 불일치 ts=2026-09-23 09:44:00 cols=['open'] existing_source=rt |
| `ChartDBG` | 5 | 08:59:36 | 09:00:16 | paintEvent slow 55.9ms | size=1955x1124 candles=15 grid=28.6 spans=0.0 candles=0.6 dir=0.0 regime=0.0 markers=0.0 axes=25.4 cross=0.0 | slow_cnt=1 total_cnt=4 overlay_cnt=1 |
| `출처축` | 2 | 08:41:11 | 08:41:11 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |
| `OptionFlowChart` | 2 | 08:41:21 | 08:58:35 | 그리기 73.7ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 874x1001 |
| `PipePerf` | 2 | 09:00:02 | 09:00:02 | total=2296ms | S0=3ms S1=38ms S2=0ms S3=0ms S4=149ms S5=1671ms S6=375ms S7=47ms S8=13ms |
| `CB⑤` | 2 | 09:00:02 | 09:00:02 | 파이프라인 2296ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `Health` | 1 | 09:00:02 | 09:00:02 | level=WARNING degraded=OFF | latency=2296ms | quality=1.00 | cache_age=43s | exceptions_10m=0 |

**채널** — `SYSTEM`×30, `HEALTH`×1

**컴포넌트 상위 15** — `LiveDBG`×11, `SessionBackfill`×6, `ChartDBG`×5, `출처축`×2, `OptionFlowChart`×2, `PipePerf`×2, `CB⑤`×2, `Health`×1

### `logs/20260928_SYSTEM.log` — 27.0KB · 225행 · 최종 08:59:03

- 형식 평문 · 시각 인식 218행 · INFO=218, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-28 08:40:48 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=19608 | 행감지=30s all_threads=True
2026-09-28 08:40:48 [INFO] SYSTEM: [DBInit] 합계 0.42s | predictions=0.04s trades=0.20s daily_stats=0.01s shap=0.01s raw_data=0.10s broker_pnl=0.01s broker_recon=0.01s premarket_levels=0.04s
2026-09-28 08:40:48 [INFO] SYSTEM: [System] DB 초기화 완료 (0.4s)
2026-09-28 08:40:48 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-28 08:40:48 [INFO] SYSTEM: 미륵이 초기화
  …
2026-09-28 09:00:02 [INFO] SYSTEM: [S6Detail] ensemble=14ms checklist_pre=25ms meta_gate=272ms gates=22ms imp=0ms shap=2ms corr=0ms dash_ui=1ms tail=38ms
2026-09-28 09:00:02 [INFO] SYSTEM: [PipePerf][DBG] total=2296ms | S0=3ms S1=38ms S2=0ms S3=0ms S4=149ms S5=1671ms S6=375ms S7=47ms S8=13ms
2026-09-28 09:00:08 [INFO] SYSTEM: [CybosRT-TICK] #2500 code=A056A raw_time=90008 parsed=09:00:08 price=1115.94 vol=1 bid1=1115.80 ask1=1116.00 flag=49 side=BUY anchor=1/0
2026-09-28 09:00:14 [INFO] SYSTEM: [CybosRT-TICK] #2600 code=A056A raw_time=90014 parsed=09:00:14 price=1117.78 vol=1 bid1=1117.76 ask1=1117.82 flag=50 side=SELL anchor=0/1
2026-09-28 09:00:17 [INFO] SYSTEM: [CybosRT-TICK] #2700 code=A056A raw_time=90017 parsed=09:00:17 price=1117.54 vol=1 bid1=1117.44 ask1=1117.56 flag=49 side=BUY anchor=1/0
```

</details>

**채널** — `SYSTEM`×218

**컴포넌트 상위 15** — `CybosRT-TICK`×32, `CybosSub`×21, `System`×17, `TickUI`×15, `CybosRT-ROLLOVER`×15, `BAR-CLOSE`×15, `CVD-ANCHOR`×15, `SYSTEM`×9, `PreMarket`×9, `CybosRT-START`×6, `Notify`×5, `BrokerSync`×4, `BalanceUI`×4, `-`×4, `LEVELS 08:50`×4

### `logs/20260928_SIGNAL.log` — 6.5KB · 106행 · 최종 08:59:01

- 형식 평문 · 시각 인식 106행 · WARNING=54, INFO=52

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-28 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.434
2026-09-28 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.451
2026-09-28 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.429
2026-09-28 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.425
2026-09-28 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.434
  …
2026-09-28 09:00:02 [WARNING] SIGNAL: [ScalerFloor] 30m 'macro_risk_on' scale=0.4982 → floor=0.50 적용 (z-score 폭발 방지)
2026-09-28 09:00:02 [WARNING] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0702 → floor=0.15 적용 (z-score 폭발 방지)
2026-09-28 09:00:02 [WARNING] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.1326 → floor=0.20 적용 (z-score 폭발 방지)
2026-09-28 09:00:02 [INFO] SIGNAL: [ScalerRefresh] ts=08:59 trigger=C_PERIODIC elapsed=infmin n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.02s
2026-09-28 09:00:04 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → GAP_OPEN: 시초가 급변 — 고신뢰·소규모 진입만 허용
```

</details>

**WARNING — 태그 4종 (상위 4)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 24 | 09:00:02 | 09:00:02 | 1m 'macro_us10y_chg' scale=0.1404 → floor=0.25 적용 (z-score 폭발 방지) |
| `ScalerRefresh` | 12 | 08:45:12 | 08:48:00 | 1m CORE 'ofi_norm' raw_std≈0(0.0473) → identity(0,1) 강제 (FLAT 100% 방지) |
| `Model` | 12 | 09:00:00 | 09:00:01 | 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 6 | 09:00:00 | 09:00:01 | ts=08:59 horizon=1m age=1m max_z=+7.74(institution_futures_net) extreme=2 adj=2 |

**채널** — `SIGNAL`×106

**컴포넌트 상위 15** — `ScalerFloor`×42, `Model`×18, `ScalerRefresh`×18, `DynMC`×7, `ScalerMonitor`×6, `TimeRouter`×3, `SIGNAL`×2, `EnsembleGater`×1, `FeatureBuilder`×1, `GapOffset`×1, `MA-cont`×1, `DayRegimeShadow`×1, `FQAdj`×1, `Ensemble`×1, `EntryGate`×1

### `logs/20260928_LEARNING.log` — 55.3KB · 308행 · 최종 08:59:01

- 형식 평문 · 시각 인식 308행 · WARNING=150, INFO=158

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-28 08:40:50 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-28 08:40:53 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00131 auc=0.530 out_max=0.3722 (기준 auc<0.53 and span<0.020, 기저율=0.3714 n=105) → 보정 미적용, raw 통과 [기존 fitted 해제]
2026-09-28 08:40:53 [WARNING] LEARNING: [Calibration:30m] 하한 도달불가 — out_max=0.3017 < conf_floor=0.3300 (span=0.00316 auc=0.566 out_max=0.3017, 기저율=0.3000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-09-28 08:40:53 [INFO] LEARNING: [Calibration:1m] 축퇴 해소 — span=0.00146 auc=0.532 out_max=0.3554 (n=110) → 보정 재적용
2026-09-28 08:40:53 [INFO] LEARNING: [Calibration:30m] 도달불가 해소 — out_max=0.3434 < conf_floor=0.3300 (n=85) → 보정 재적용
  …
2026-09-28 08:55:01 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-09-28 08:55:11 [INFO] LEARNING: [MetaConf] 상태 복원 완료: meta_conf_state.pkl (fitted=[추세장, 횡보장, 급변장, 혼합], total=8550, ver=5)
2026-09-28 08:59:01 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-09-28 09:00:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0000% buf_n=0 nonzero=0 prev_p=0.00 cur_p=1115.78
2026-09-28 09:00:02 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=500 feat=97
```

</details>

**WARNING — 태그 7종 (상위 7)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:1m` | 51 | 08:40:53 | 08:41:02 | 축퇴 감지 — span=0.00131 auc=0.530 out_max=0.3722 (기준 auc<0.53 and span<0.020, 기저율=0.3714 n=105) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:30m` | 50 | 08:40:53 | 08:41:01 | 하한 도달불가 — out_max=0.3017 < conf_floor=0.3300 (span=0.00316 auc=0.566 out_max=0.3017, 기저율=0.3000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:3m` | 17 | 08:40:53 | 08:41:02 | 하한 도달불가 — out_max=0.3129 < conf_floor=0.3300 (span=0.00067 auc=0.553 out_max=0.3129, 기저율=0.3125 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:10m` | 15 | 08:40:54 | 08:41:02 | 축퇴 감지 — span=0.00083 auc=0.525 out_max=0.4100 (기준 auc<0.53 and span<0.020, 기저율=0.4095 n=105) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:5m` | 10 | 08:40:53 | 08:41:00 | 축퇴 감지 — span=0.00119 auc=0.490 out_max=0.3631 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과 |
| `Calibration:15m` | 6 | 08:40:57 | 08:41:01 | 축퇴 감지 — span=0.00128 auc=0.529 out_max=0.3356 (기준 auc<0.53 and span<0.020, 기저율=0.3350 n=200) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:ensemble` | 1 | 08:41:02 | 08:41:02 | 복원한 보정기가 축퇴 상태 — span=0.00163 auc=0.497 out_max=0.3407 (n=1184) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다. |

**채널** — `LEARNING`×308

**컴포넌트 상위 15** — `Calibration:1m`×100, `Calibration:30m`×99, `Calibration:3m`×33, `Calibration:10m`×28, `Calibration:5m`×19, `Calibration:15m`×12, `ScalerWarmup`×6, `ExtremityCorrector`×2, `Calibration:ensemble`×2, `Consolidator`×2, `RF`×1, `DriftAdjuster`×1, `SHAP`×1, `MetaConf`×1, `sigma`×1

### `logs/20260928_MICRO.log` — 32.6KB · 96행 · 최종 08:59:01

- 형식 평문 · 시각 인식 96행 · DEBUG=96

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-28 08:45:12 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1113.50/1 ask1=1113.82/6 mp={'microprice_tick': 1113.5457, 'midprice_tick': 1113.66, 'depth_bias_tick': -0.3364} mlofi_tick=None queue=None
2026-09-28 08:45:12 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1113.50/1 ask1=1113.74/2 mp={'microprice_tick': 1113.58, 'midprice_tick': 1113.62, 'depth_bias_tick': -0.2739} mlofi_tick=-8.45 queue={'depletion_bid': -0.0, 'depletion_ask': 4.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -…
2026-09-28 08:45:12 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1113.50/1 ask1=1113.74/2 mp={'microprice_tick': 1113.58, 'midprice_tick': 1113.62, 'depth_bias_tick': -0.2739} mlofi_tick=0.0 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0…
2026-09-28 08:45:12 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1113.50/1 ask1=1113.74/1 mp={'microprice_tick': 1113.62, 'midprice_tick': 1113.62, 'depth_bias_tick': -0.2147} mlofi_tick=1.0 queue={'depletion_bid': -0.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.…
2026-09-28 08:45:12 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1113.50/1 ask1=1113.74/2 mp={'microprice_tick': 1113.58, 'midprice_tick': 1113.62, 'depth_bias_tick': -0.2739} mlofi_tick=-1.0 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 1.0, 'bid_cancel_add_ratio': -0…
  …
2026-09-28 08:59:55 [DEBUG] MICRO: [MICRO-TICK] #5800 bid1=1116.02/1 ask1=1116.20/1 mp={'microprice_tick': 1116.11, 'midprice_tick': 1116.11, 'depth_bias_tick': -0.8141} mlofi_tick=-3.2833 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_rati…
2026-09-28 09:00:00 [DEBUG] MICRO: [MICRO-MINUTE] #15 ts=2026-09-28 08:59:00 close=1115.78 bias=-0.002717 slope=0.501622 depth_bias=-0.0629 mlofi_norm=-0.077961 mlofi_pressure=-1 mlofi_slope=-42.491667 queue_signal=0.0583 queue_ma=0.0063 queue_momentum=0.0200 depletion=0.5017 refill=0.4983 imbalanc…
2026-09-28 09:00:03 [DEBUG] MICRO: [MICRO-TICK] #5900 bid1=1115.00/1 ask1=1115.16/2 mp={'microprice_tick': 1115.0533, 'midprice_tick': 1115.08, 'depth_bias_tick': -0.2083} mlofi_tick=3.2333 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 1.0, 'bid_cancel_add_rat…
2026-09-28 09:00:11 [DEBUG] MICRO: [MICRO-TICK] #6000 bid1=1116.24/1 ask1=1116.48/2 mp={'microprice_tick': 1116.32, 'midprice_tick': 1116.36, 'depth_bias_tick': -0.1491} mlofi_tick=5.65 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 1.0, 'bid_cancel_add_ratio':…
2026-09-28 09:00:16 [DEBUG] MICRO: [MICRO-TICK] #6100 bid1=1118.24/2 ask1=1118.38/1 mp={'microprice_tick': 1118.3333, 'midprice_tick': 1118.31, 'depth_bias_tick': 0.1957} mlofi_tick=9.7167 queue={'depletion_bid': 0.0, 'depletion_ask': 1.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio…
```

</details>

**채널** — `MICRO`×96

**컴포넌트 상위 15** — `MICRO-TICK`×81, `MICRO-MINUTE`×15

### `logs/20260928_DATA.log` — 894B · 5행 · 최종 08:58:45

- 형식 평문 · 시각 인식 5행 · INFO=5

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-28 08:58:15 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=-96 individual=-113 institution=+230 oi=0 call_foreign=-356 put_foreign=+121 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-09-28 08:58:15 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=True program_supported=False option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=runtime_disabled
2026-09-28 08:58:45 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=-90 individual=-119 institution=+230 oi=0 call_foreign=-363 put_foreign=+123 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-09-28 08:58:45 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=True program_supported=False option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=runtime_disabled
2026-09-28 09:00:00 [INFO] DATA: [DivergencePanel] source=cybos status=partial div=+29 futures(fi=-90 rt=-119 inst=+230) call(fi=-363 rt=+349) put(fi=+123 rt=-107) bias(fi=-1.00 rt=1.00) program(arb=+0 nonarb=+0 total=+0)
  …
2026-09-28 08:58:15 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=-96 individual=-113 institution=+230 oi=0 call_foreign=-356 put_foreign=+121 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-09-28 08:58:15 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=True program_supported=False option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=runtime_disabled
2026-09-28 08:58:45 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=-90 individual=-119 institution=+230 oi=0 call_foreign=-363 put_foreign=+123 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-09-28 08:58:45 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=True program_supported=False option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=runtime_disabled
2026-09-28 09:00:00 [INFO] DATA: [DivergencePanel] source=cybos status=partial div=+29 futures(fi=-90 rt=-119 inst=+230) call(fi=-363 rt=+349) put(fi=+123 rt=-107) bias(fi=-1.00 rt=1.00) program(arb=+0 nonarb=+0 total=+0)
```

</details>

**채널** — `DATA`×5

**컴포넌트 상위 15** — `CybosInvestor`×4, `DivergencePanel`×1

### `logs/20260928_PROBE.log` — 12.1KB · 4행 · 최종 08:58:45

- 형식 평문 · 시각 인식 4행 · INFO=4

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-28 08:41:12 [INFO] PROBE: [CybosInvestorProbe] not implemented; extra_codes=['A056A']
2026-09-28 08:58:15 [INFO] PROBE: [CybosProbe] CpSysDib.CpSvrNew7221 ok status=0 nonempty_headers=3 rows=30
2026-09-28 08:58:15 [INFO] PROBE: [CybosProbe][RAW] CpSysDib.CpSvrNew7221 field_limit=64 headers={0: '28', 1: '28', 2: '75'} rows_sample=[{0: '0', 1: '0', 2: '0', 3: '0', 4: '0', 5: '0', 6: '0', 7: '0', 8: '0', 9: '0', 10: '0', 11: '0', 12: '0', 13: '0', 14: '0', 15: '0', 16: '0', 17: '0', 18: '0',…
2026-09-28 08:58:45 [INFO] PROBE: [CybosProbe] CpSysDib.CpSvrNew7221 ok status=0 nonempty_headers=3 rows=30
  …
2026-09-28 08:41:12 [INFO] PROBE: [CybosInvestorProbe] not implemented; extra_codes=['A056A']
2026-09-28 08:58:15 [INFO] PROBE: [CybosProbe] CpSysDib.CpSvrNew7221 ok status=0 nonempty_headers=3 rows=30
2026-09-28 08:58:15 [INFO] PROBE: [CybosProbe][RAW] CpSysDib.CpSvrNew7221 field_limit=64 headers={0: '28', 1: '28', 2: '75'} rows_sample=[{0: '0', 1: '0', 2: '0', 3: '0', 4: '0', 5: '0', 6: '0', 7: '0', 8: '0', 9: '0', 10: '0', 11: '0', 12: '0', 13: '0', 14: '0', 15: '0', 16: '0', 17: '0', 18: '0',…
2026-09-28 08:58:45 [INFO] PROBE: [CybosProbe] CpSysDib.CpSvrNew7221 ok status=0 nonempty_headers=3 rows=30
```

</details>

**채널** — `PROBE`×4

**컴포넌트 상위 15** — `CybosProbe`×3, `CybosInvestorProbe`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 0 |
| 진입 등록(`[Position] 진입`) — **엔진** | 0 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 0 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 0 |
| 차단(`[차단]`) | 0 |
| 사이저 호출(`[Sizer]`) | 0 |

### 메인 스레드 블로킹 3건 · 최대 4219ms · 5초 초과 0건

상위 — 4219ms, 3656ms, 3156ms

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260928_WARN.log`
```
--- 메인 스레드 블로킹 ×3(표본)
08:41:14 2026-09-28 08:41:14 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3656ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3656 band=INFO since_pipe_s=NA
08:59:35 2026-09-28 08:59:35 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3156ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3156 band=INFO since_pipe_s=NA
09:00:04 2026-09-28 09:00:04 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4219ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4219 band=INFO since_pipe_s=0.1
```

### `logs/20260928_SYSTEM.log`
```
--- PSI ×1(표본)
09:00:00 2026-09-28 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.000 level=0 (heartbeat)
```

### `logs/20260928_SIGNAL.log`
```
--- 기동 복원 ×7(표본)
08:40:45 2026-09-28 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.434
08:40:45 2026-09-28 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.451
08:40:45 2026-09-28 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.429
08:40:45 2026-09-28 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.425
```

### `logs/20260928_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:53 2026-09-28 08:40:53 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00131 auc=0.530 out_max=0.3722 (기준 auc<0.53 and span<0.020, 기저율=0.3714 n=105) → 보정 미적용, raw 통과 [기존 fitted 해제]
08:40:53 2026-09-28 08:40:53 [WARNING] LEARNING: [Calibration:30m] 하한 도달불가 — out_max=0.3017 < conf_floor=0.3300 (span=0.00316 auc=0.566 out_max=0.3017, 기저율=0.3000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:53 2026-09-28 08:40:53 [INFO] LEARNING: [Calibration:1m] 축퇴 해소 — span=0.00146 auc=0.532 out_max=0.3554 (n=110) → 보정 재적용
08:40:53 2026-09-28 08:40:53 [WARNING] LEARNING: [Calibration:30m] 하한 도달불가 — out_max=0.3285 < conf_floor=0.3300 (span=0.00403 auc=0.595 out_max=0.3285, 기저율=0.3263 n=95) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260928_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:02 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:41 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260928_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 18 | 08:41:11 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 13 | 08:58:35 [WARNING] 그리기 77.7ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 752x1287 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 13 | 08:58:35 [WARNING] 그리기 77.7ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 752x1287 |

- 이 로그 생존구간: 08:41 ~ 09:00

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260928_SYSTEM.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 95 | 08:40:48 [INFO] 활성화 | file=logs\crash_fault.log PID=19608 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 110 | 08:49:00 [INFO] code=A056A from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 76 | 08:54:01 [INFO] code=A056A from=08:53 to=08:54 |

- 이 로그 생존구간: 08:40 ~ 09:00

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260928_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 44 | 08:45:12 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0473) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 55 | 09:00:00 [WARNING] 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 54 | 09:00:00 [WARNING] 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |

- 이 로그 생존구간: 08:40 ~ 09:00

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260926 | 16:50 | 로그 본문 |
| 20260924 | 10:58 | 로그 본문 |
| 20260923 | 18:44 | 로그 본문 |
| 20260922 | 15:47 | 로그 본문 |
| 20260921 | 17:30 | 로그 본문 |
| **중앙값** | **16:50** | 기준선 |
| **오늘 20260928** | **09:00** | 로그 본문 |

- 델타 **-470분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.3MB · 마지막 갱신 2026-09-26 16:54

최근 헤딩 8개:
```
### How to apply
### 검증
## 2026-09-23 (MW0601 624차 — 장후 자동조치: 「무흔적 크래시」 하나는 동결 감시자의 자기 종료였다)
## 2026-09-23 (MW0601 625차 — Ctrl+Shift+X 1분봉 차트: 창이 화면보다 넓어 못 줄이고, 4K 로 옮기면 봉이 사라졌다)
## 2026-09-24 (MW0601 630차 — 줄끝 규칙을 저장소 안으로 + 가드가 못 보던 잠금: 「오염 759개」는 오판이었다)
## 2026-09-26 (MW0601 631차 — 휴장일 점검: 부팅 직후 DB 초기화가 3분 넘게 안 끝났다)
## 2026-09-26 (MW0601 632차 — 장중 재점검, 10:44 절로부터 27분 뒤: 무변화 확인 + 수집기 자가점검 사례)
## 2026-09-26 (MW0601 631차 후속 — 장후: 휴장일 상황 동결 확인 + F-4 범위 확장)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
약 460MB 전수 스캔. 캐시 따뜻 0.6s / 운영 13–19s(08-18 13s→09-24 19s, 행 수 따라 선형 증가) / 오늘 부팅 직후 ≥210s. 부분 인덱스로 0.0000s 실측(권고 F-1a). 오늘 10배 지연 원인은 부팅 직후 I/O 경합 가설(미확정)이나 Fix가 원인 확정을 불필요하게 만든다. 10:35 세션은 사용자 수동 종료로 확인. ② 1-2 세 기동 모두 작업 스케줄러 수동 실행(이벤트 110), 놓친 작업 자동 실행 아님(153 거부). 자동로그인 1차 시도가 32초째 공지사항(=로그인 성공 신호)을 닫고도 IsConnect 미검출로 타임아웃 → 2차가 kill(실패, "이미 실행중") → 그 사이 런처가 IsConnect=1로 통과. 런처 STEP 4는 autologin 진행 여부를 안 본다. ③ 1-3 수집기 FZ-6 규칙에 영업일 판정 없음, `config/krx_holidays.py`에 09-26 휴장 등록돼 있음.
- 구현(631차): 1순위 `95eb59d`(F-1a 부분 인덱스 idx_pred_prob_null · F-2 [DBInit] · F-5 [BOOT]) · 2순위 `4aecc7f`(F-6 재시도 전 연결 재확인 · F-7 kill 실패 보고 · F-8 diag 줄별 시각) · 3순위 `bc81108`(F-3 data/autologin.lock 대기 · F-3b IsConnect 10초 연속) · 4순위 `44c0a71`(F-4 수집기 휴장일 — 장후 세션 범위 확장 반영, 거래일 전제 9종 생략·인프라 유지). Why: 부팅 직후 기동 지연·로그인 경합·휴일 오경보 셋 다 매매 경로 밖이라 휴장일에 적용 가능. How to apply: 9/28 첫 기동 `[DBInit] 합계` 1초대면 F-1a 확인; 자동로그인 변경은 라이브 리허설 전. 주의: test_458 이 운영 DB로 init_all_dbs 를 불러 12:32:45 운영 predictions.db 에 색인이 생겼다(무해, 631-15로 격리 등록).
- 딥다이브2(631차): 15:58 미륵이 기동 실패(STEP 4 300초 미연결)의 원인 = `pc_shutdown_friday`(9/23부터 `shutdown /h` 최대 절전) 수동 실행 15:54:01 → 잠자기 15:54:02 → DibServer 소켓 종료 15:54:03(10053) → 깨어남 15:55:14(재부팅 아님) → CpStart 생존 → LAUNCH_API 15:57:29 "Already connected"로 로그인 생략 → 미연결 지속(16:05 IsConnect=0). F-3b 는 원인 아님(300초 내내 미연결). 부수 확정: DibServer 10:22:26 소켓 종료 = 런처 출발 27초 뒤 → 오전 1-2(자동로그인 재시도가 세션 끊음) 확정 격상. 권고 S-1: 절전 전 Cybos·미륵이 프로세스 정리(한량이 저장소 파일).
- 딥다이브2 후속(631차): ① Cybos CpStart/DibServer 는 관리자에서도 taskkill 거부(보안 모듈) → 절전 전 정리는 CpCybos.PlusDisconnect()(세션 종료 + 프로세스 자체 종료 실측) — 한량이 333e3ee. ② 핵심 원인 확정: 한 프로세스가 CpUtil.CpCybos 를 붙든 뒤 Cybos 인스턴스가 바뀌면 그 프로세스는 영원히 IsConnect=0 → 자동로그인이 성공한 로그인(공지사항 출현)을 120초 후 실패로 오판하고 다음 시도가 세션을 끊었다(16:16:40·16:19:06). 새 프로세스는 같은 시각 1. 수정: _is_connected/probe_connected 를 매번 새 프로세스로. F-6 은 이 수정 전엔 무효였다. Why: 오전 10:19·오후 16:14 실패의 공통 뿌리. How to apply: CpCybos 연결 확인을 한 프로세스에서 반복하지 말 것.
- 실전 확인(631차): 16:36 PC 종료 → PlusDisconnect·Cybos 종료 → 절전/해제 → 16:38:35 Cybos Plus 가 미연결 정확 인식·1차 로그인 37초 → 16:39:29 미륵이 STEP4 즉시 통과·DB 초기화 0.4s·16:40:26 기동 완료. 15:58 실패 경로 해소 확인.
- Claude 앱(631차): ① claude_update_window 의 taskkill /IM claude.exe 가 VS Code Claude Code 확장(같은 이름)까지 죽였다 → WindowsApps\Claude_* 만 종료하도록 생성기(scripts/claude_hibernate_setup.ps1)·생성본 모두 수정(12/14 대상, 확장 2개 제외 실측). ② 절전 해제는 로그온이 아니라 시작 프로그램이 안 돈다 → 예약작업 claude_resume_ensure(Power-Troubleshooter ID 1)가 45초 뒤 데스크톱 앱이 없으면 AUMID 로 실행(scripts/claude_ensure_running.ps1 · claude_resume_task.ps1). 실행 경로(앱이 꺼진 상태)는 미시험.

```

</details>

### dev_memory/NEXT_TODO.md — 1.6MB · 마지막 갱신 2026-09-26 16:33

최근 헤딩 8개:
```
### 확인 완료 (604차 후속이 재확인·재분류, 신규 아님)
## 2026-09-23 (MW0601 604차 후속2 — 장후 점검: 재기동 10회 확대 + 마감작업 누락 직전)
### 신규 등록
### 확인 완료 (604차 후속2가 재확인·재분류, 신규 아님)
## 2026-09-23 (MW0601 624차 — 장후 자동조치)
## 2026-09-26 (MW0601 631차 — 휴장일 점검)
## 2026-09-26 (MW0601 632차 — 장중 재점검)
## 2026-09-26 (MW0601 631차 후속 — 장후)
```

미완료 체크박스 **2854건** (끝에서 30건)
```
- [ ] **O-t3 (계승, 5거래일 누적)** CB③ 판정가능시간 0분 재현 — 오늘도 0분/0분
- [ ] **O-t4 (계승, O-i2)** `sizing_inversion_watch`([28]) — 오늘 표본 +1건
- [ ] **624-2** intent 줄 없는 `[CLEAN EXIT]` 9건(2026-09-23 10:45~15:19)의 종료 경로 규명 —
- [ ] 624-3 F-4(`system.run()` try/except) **보류 — 전제 약화**. 2026-09-23 11종료 중 파이썬 예외 0건.
- [ ] 624-4 22160(13:51:44 무기록 종료) — 622차 적용 재시작이었는지 사용자 확인.
- [ ] 624-5 증거 수집기가 비Windows 에서 돌아 §9-d WER 축이 「미측정」 — 2일 연속(620·624).
- [ ] F-5 런처 안전망 보강 · F-6 마감작업 생존 의존성 — 주간회의 안건(604차 후속2 등록분, 변동 없음).
- [ ] **624-6** 2026-09-23 전체 스위트 신규 실패 5건(이번 변경 무관, 당일 타 작업 유래 추정): test_457(peter_paste 폴백 플래그) · test_498(CybosInvestor 대사로그 RECON_INVENTORY 미등록) · test_493(generate_validation_campaign_report.py:…
- [ ] **631-1** 9/28(월) 첫 기동 `FaultHandler 활성화 → DB 초기화 완료` 간격 확인(재부팅 직후면 특히). 20초 초과 시 1-1 재현.
- [ ] **631-2 (F-1)** `utils/db_utils.py:_migrate_predictions_db()` 역채움 UPDATE를 1회 마커(`PRAGMA user_version` 등)로 건너뛰기 — 매 기동 454MB 풀스캔 제거.
- [ ] **631-3 (F-2)** `init_all_dbs()` 단계별 소요시간 `[DBInit]` 로그(계측 4원칙 ④).
- [ ] **631-4 (F-3)** 미륵이 런처 STEP 4: 자동로그인 스크립트 실행 중이면 준비 판정 보류.
- [ ] **631-5 (F-4)** `collect_evidence.py` §11 영업일 판정 — 휴장일 가짜 동결 경보 제거.
- [ ] **632-1** `scripts/collect_evidence.py` 실행 중 `.git/index.lock`이 0.1분(약 6초) 생성됐다 자연 해소된 경로 특정 — 어느 내부 호출이 `--no-optional-locks` 없이 인덱스에 쓰는지 grep으로 확인 (P2, 장후 또는 여유 있을 때).
- [ ] **632-2** 미륵이 점검 예약작업(장중)이 같은 날 약 20분 간격으로 두 번 발화된 것으로 관측됨 — 트리거 설정 확인 필요(코드 사안 아님, 운영 사안. 사용자 확인 권장).
- [ ] **631-6 (F-4 범위확장)** `collect_evidence.py` §11 적신호 생성부를 `--phase` 무관 영업일 게이트로 — 휴장일이면 8개 규칙 전부 생략, "휴장일" 배너만 출력. 631-1~631-5(장중 등록분)는 변경 없음.
- [ ] **631-6** 미커밋 3건 커밋 권고(사용자 결정) — 되돌리면 캐시(`roll_adj` 262건) TypeError + 0917 자동로그인 결함 부활. 두 커밋 분리. 근거: 0926 리포트 추기.
- [ ] **631-7** `premarket_levels.compute_manual()` 에 `roll_adj` 전달 누락 — `ROLL_POLICY=adjust` 켜기 전 수정.
- [ ] **631-8** `cybos_autologin._is_already_running_text()` any → "이미실행" 필수로 축소(오탐 여지 제거).
- [ ] **631-9** dev 이식 결정(사용자): `723c208` 은 무충돌 적용 가능(권고) · `46f3ee7` 은 충돌 3곳 + dev 에 roll_days 라벨 배치 없음 → 보류 권고. `v9-dev` push 여부도 함께.
- [ ] **631-10 (F-1a, 1순위)** `_migrate_predictions_db()` 역채움 UPDATE 앞에 부분 인덱스 `idx_pred_prob_null`(WHERE 세 확률 IS NULL) — 복사본 실측 UPDATE 0.6s→0.0000s, 생성 1회 6.3s. 631-2(user_version 마커안)를 대체.
- [ ] **631-11 (F-5)** 초기화 중 런처 콘솔에 `[BOOT] DB 초기화 중…` 진행 표시 — 0926 사용자가 "안 올라온다"고 판단해 수동 종료.
- [ ] **631-12 (F-6/F-7/F-8)** 자동로그인: 재시도 직전 `_is_connected()` 재확인 · kill 실패 가시화 · diag 줄별 시각. F-6은 모의 리허설 1회 후.
- [ ] **631-13 (F-3/F-3b)** 런처 STEP 4: autologin 락 대기 + IsConnect 연속 10초 유지 판정.
- [ ] **631-14 (F-4/G-1)** 스킬 폴더 `collect_evidence.py`에 `config/krx_holidays.py`(파일경로 로드) 휴장일 판정 — FZ-6·480차 규칙 스킵 + 배너.
- [ ] **631-15** `tests/test_458_p0_quiet_window.py:163` 이 운영 DB 경로로 `init_all_dbs()` 를 호출한다 — 임시 DB_DIR 로 격리할 것(2026-09-26 이 테스트가 운영 predictions.db 에 색인을 만들었다; 이번엔 무해).
- [ ] **631-16 (S-1, 권고)** `auto_trader_kiwoom/scripts/shutdown_friday.bat`(한량이 저장소): `shutdown /h` 직전 CpStart·ncStarter·DibServer·미륵이 main.py 종료 — 절전 해제 후 끊긴 세션을 든 CpStart 가 남아 LAUNCH_API 가 "Already…
- [ ] **631-17 (S-2/S-3)** `LAUNCH_API.bat`: CpStart 시작 < 마지막 절전 해제면 연결 불신 → 자동로그인 / `[CHECK] IsConnect` 값을 로그 파일에도 기록.
- [ ] **631-18 (S-4)** `start_mireuk.bat` STEP 4 실패 시 "CpStart 생존·미연결 = 절전 해제 후 끊김" 힌트.
- [ ] **631-19** 옛 Cybos 생존 상태 자동로그인 1차 성공 여부 — 다음 절전 해제 아침 diag 로그로 확인(새 프로세스 IsConnect 확인 라이브 검증)
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
 `--no-optional-locks` 없이 인덱스에 쓰는지 grep으로 확인 (P2, 장후 또는 여유 있을 때).
- [ ] **632-2** 미륵이 점검 예약작업(장중)이 같은 날 약 20분 간격으로 두 번 발화된 것으로 관측됨 — 트리거 설정 확인 필요(코드 사안 아님, 운영 사안. 사용자 확인 권장).

## 2026-09-26 (MW0601 631차 후속 — 장후)
- [ ] **631-6 (F-4 범위확장)** `collect_evidence.py` §11 적신호 생성부를 `--phase` 무관 영업일 게이트로 — 휴장일이면 8개 규칙 전부 생략, "휴장일" 배너만 출력. 631-1~631-5(장중 등록분)는 변경 없음.
- [ ] **631-6** 미커밋 3건 커밋 권고(사용자 결정) — 되돌리면 캐시(`roll_adj` 262건) TypeError + 0917 자동로그인 결함 부활. 두 커밋 분리. 근거: 0926 리포트 추기.
- [ ] **631-7** `premarket_levels.compute_manual()` 에 `roll_adj` 전달 누락 — `ROLL_POLICY=adjust` 켜기 전 수정.
- [ ] **631-8** `cybos_autologin._is_already_running_text()` any → "이미실행" 필수로 축소(오탐 여지 제거).
- [ ] **631-9** dev 이식 결정(사용자): `723c208` 은 무충돌 적용 가능(권고) · `46f3ee7` 은 충돌 3곳 + dev 에 roll_days 라벨 배치 없음 → 보류 권고. `v9-dev` push 여부도 함께.
- [ ] **631-10 (F-1a, 1순위)** `_migrate_predictions_db()` 역채움 UPDATE 앞에 부분 인덱스 `idx_pred_prob_null`(WHERE 세 확률 IS NULL) — 복사본 실측 UPDATE 0.6s→0.0000s, 생성 1회 6.3s. 631-2(user_version 마커안)를 대체.
- [ ] **631-11 (F-5)** 초기화 중 런처 콘솔에 `[BOOT] DB 초기화 중…` 진행 표시 — 0926 사용자가 "안 올라온다"고 판단해 수동 종료.
- [ ] **631-12 (F-6/F-7/F-8)** 자동로그인: 재시도 직전 `_is_connected()` 재확인 · kill 실패 가시화 · diag 줄별 시각. F-6은 모의 리허설 1회 후.
- [ ] **631-13 (F-3/F-3b)** 런처 STEP 4: autologin 락 대기 + IsConnect 연속 10초 유지 판정.
- [ ] **631-14 (F-4/G-1)** 스킬 폴더 `collect_evidence.py`에 `config/krx_holidays.py`(파일경로 로드) 휴장일 판정 — FZ-6·480차 규칙 스킵 + 배너.
- [x] **631-10/11** F-1a·F-2·F-5 구현 `95eb59d` — 9/28 첫 기동 `[DBInit] 합계` 1초대 확인 대기
- [x] **631-12** F-6·F-7·F-8 구현 `4aecc7f` — 라이브 리허설 미실시(다음 LAUNCH_API 진단 로그 시각 확인)
- [x] **631-13** F-3·F-3b 구현 `bc81108` — 라이브 연결 상태 rc=0 확인(11.8s)
- [x] **631-14** F-4 구현 `44c0a71` — 영업일 출력 불변 확인
- [ ] **631-15** `tests/test_458_p0_quiet_window.py:163` 이 운영 DB 경로로 `init_all_dbs()` 를 호출한다 — 임시 DB_DIR 로 격리할 것(2026-09-26 이 테스트가 운영 predictions.db 에 색인을 만들었다; 이번엔 무해).
- [ ] **631-16 (S-1, 권고)** `auto_trader_kiwoom/scripts/shutdown_friday.bat`(한량이 저장소): `shutdown /h` 직전 CpStart·ncStarter·DibServer·미륵이 main.py 종료 — 절전 해제 후 끊긴 세션을 든 CpStart 가 남아 LAUNCH_API 가 "Already connected"로 로그인 생략(0926 15:57 실측).
- [ ] **631-17 (S-2/S-3)** `LAUNCH_API.bat`: CpStart 시작 < 마지막 절전 해제면 연결 불신 → 자동로그인 / `[CHECK] IsConnect` 값을 로그 파일에도 기록.
- [ ] **631-18 (S-4)** `start_mireuk.bat` STEP 4 실패 시 "CpStart 생존·미연결 = 절전 해제 후 끊김" 힌트.
- [x] **631-16** 절전 전 Cybos 세션 정리 — auto_trader_kiwoom `333e3ee`(PlusDisconnect; 강제 종료는 보안 모듈이 거부)
- [ ] **631-19** 옛 Cybos 생존 상태 자동로그인 1차 성공 여부 — 다음 절전 해제 아침 diag 로그로 확인(새 프로세스 IsConnect 확인 라이브 검증)

```

</details>

### dev_memory/CURRENT_STATE.md — 529.7KB · 마지막 갱신 2026-08-19 17:43

최근 헤딩 8개:
```
### 3. 재시작 직후 restored/live 분리
### 4. 중패널 `동적 피처 (SHAP)` 상태
### 5. 오늘 확인된 startup 이슈와 현재 최종 블로커
## 2026-05-22 (82차) — Micro Regime Warmup UI
### 배경
### 현재 상태
### 구현 파일 (82차)
### 다음 확인 사항
```

_(참고용 — 필요하면 직접 열 것)_

### dev_memory/SESSION_LOG.md — 576.7KB · 마지막 갱신 2026-08-12 18:40

최근 헤딩 8개:
```
## 2026-07-08 (304차 — 진입관리 탭 UI 정리: 원신호/실행신호 폭 축소+차단사유/레짐 이전, 상태스트립·자격현황 카드 제거, 방향인디케이터 카드 축소)
### 구현
### 검증
## 2026-07-08 (304차 후속 — daily_close() 백그라운드 스레드 Qt 위젯 직접조작으로 인한 access violation 크래시 루프 수정)
### 실측한 증상
### 원인 규명
### 구현
### 검증
```

_(참고용 — 필요하면 직접 열 것)_

## 9. 당일 JSON/JSONL 산출물

### `data/heartbeat_MW0601_20260928.json` — 245B · 09-28 08:58:42
```json
{
 "pid": 19608,
 "written_at": "2026-09-28T09:00:12",
 "beat_epoch": 1790553611.9124238,
 "beat_age_sec": 0.7,
 "watching": true,
 "strikes": 0,
 "stall_sec": 180.0,
 "strikes_needed": 2,
 "check_sec": 30.0,
 "window": [
  "09:00",
  "15:45"
 ],
 "fired": false
}
```

### `data/session_state.json` — 기동 마커 스냅샷 (날짜 토큰 없어 인벤토리 미포함)

- 파일 최종 기록: **09-28 08:46:00**

| 키 | 값 | 수집 대상일(2026-09-28)과 일치 |
|---|---|---|
| `date` | 2026-09-28 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

### `raw_candles` 절단선·결손 (618차)

| 항목 | 값 |
|---|---|
| `raw_candles` 당일 max ts | **08:59** |
| 절단선(파생 = 강제청산 − 2분) | `15:08` |
| 판정 | **결손** — 아래 목록과 그 시각의 `[START]`/`[CLEAN EXIT]` 대조 |
| `raw_candles` 당일 행수 | 15 |
| `session_bars` 당일 행수 | 15 (기대 411) |

- 결손 **0봉**
- ⚠ **영구 결손 369봉** (`session_bars` 에도 없음): 09:00, 09:01, 09:02, 09:03, 09:04, 09:05, 09:06, 09:07, 09:08, 09:09, 09:10, 09:11, 09:12, 09:13, 09:14, 09:15, 09:16, 09:17, 09:18, 09:19

- 라이브 로그 대조: `logs/20260928_SYSTEM.log` 의 `[BarGap]` 줄
  - 기동 직후 1줄(분그리드 기준) + 15:46 보충 직후 1줄(확정). **한 줄도 없으면 계측이 죽은 것**이지 결손이 없는 것이 아니다.

> 결손 ts 는 그날 재기동 시각과 1:1 대응한다(실측 2026-09-07~09-22: 결손일 3/12일, 12봉, 09-21 은 8회 재기동에 7봉). `[Shutdown] intent=` 줄과 함께 보면 그 재기동이 사용자 의도인지 하드킬인지까지 갈린다.


### 프로세스 종료 3축 대사 (620차)

| 축 | 상태 |
|---|---|
| 런처 로그(기동 PID·재시작 분류) | 측정됨 — 기동 1회 · 재시작 0회 |
| `crash_fault.log`(정상종료 기록) | 측정됨 — PID 1개 |
| Windows WER(네이티브 예외) | **미측정** — 비Windows 플랫폼 — WER 이벤트 로그가 없다 |

| 미륵이 PID | 기동 | 정상종료 기록 | WER 네이티브 예외 | 판정 |
|---|---|---|---|---|
| 19608 | 08:40:48 | 없음 | 없음 | 판정불가 — WER **미측정** |


> 🔴 **「WER 기록 없음」을 「크래시가 아니다」로 읽지 말 것.** 참인 것은 **「미처리 네이티브 예외는 아니었다」까지**다 — `sys.exit`·창 닫기·`TerminateProcess`(하드킬)는 전부 이벤트를 안 남긴다. 종료 *의도*는 618차가 넣은 `[Shutdown] intent=` 줄과 함께 봐야 갈린다.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 169개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260926-점검리포트.md` | 67.5KB | 09-26 16:43 |
| `docs/정기점검/매일점검/evidence_MW0601-20260926_intra_1107.md` | 41.3KB | 09-26 11:07 |
| `docs/정기점검/매일점검/evidence_MW0601-20260926_post.md` | 41.7KB | 09-26 11:06 |
| `docs/정기점검/매일점검/evidence_MW0601-20260926_intra.md` | 41.7KB | 09-26 10:44 |
| `docs/정기점검/매일점검/MW0601-20260901-점검리포트.md` | 121.4KB | 09-24 18:10 |
| `docs/정기점검/매일점검/MW0601-20260826-점검리포트.md` | 224.8KB | 09-24 18:10 |
| `docs/정기점검/매일점검/MW0601-20260923-점검리포트.md` | 80.7KB | 09-23 17:41 |
| `docs/정기점검/매일점검/evidence_MW0601-20260923_post.md` | 91.3KB | 09-23 16:21 |

### `docs/정기점검/금요일점검` — 60개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260923.json` | 3.0KB | 09-23 15:56 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260923.md` | 4.9KB | 09-23 15:56 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260923.json` | 38.8KB | 09-23 15:56 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260923.md` | 32.3KB | 09-23 15:56 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260923.json` | 121.3KB | 09-23 15:55 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260923.md` | 195.2KB | 09-23 15:55 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260918.json` | 3.0KB | 09-18 15:55 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260918.md` | 5.0KB | 09-18 15:55 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. `logs/20260928_LEARNING.log`: **축퇴** 8건(표본)
2. 미커밋 변경 1건 — **실질 변경 미측정**(git diff 실패). 원시 건수만으로는 착시인지 알 수 없다

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260928*.log` (Windows) / `grep 강제청산 logs/*20260928*.log`*