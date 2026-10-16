# 미륵이 증거 다이제스트 — 2026-09-30 / PRE

- 생성 2026-09-30 08:59:41 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/rcw-01jv3tupzgtxasljstumuc9v/mnt/futures`
- 점검 범위: pre (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260930` · `2026-09-30` · `260930` · `0930`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **16개** 파일 · 16개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `claude_resume_{DATE}.log` | 1 | `logs/claude_resume_20260930.log` | 137B | 09-30 07:22 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260930.log` | 123B | 09-30 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260930.log` | 139B | 09-30 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260930.json` | 245B | 09-30 08:59 |
| `launcher_{DATE}_084000_10534.log` | 1 | `logs/Mireuk_batch/launcher_20260930_084000_10534.log` | 53.7KB | 09-30 08:59 |
| `{DATE}_DATA.log` | 1 | `logs/20260930_DATA.log` | 894B | 09-30 08:58 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260930_DEBUG.log` | 0B | 09-30 08:40 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260930_HEALTH.log` | 0B | 09-30 08:40 |
| `{DATE}_HOGA.log` | 1 | `logs/20260930_HOGA.log` | 1.2MB | 09-30 08:59 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260930_LEARNING.log` | 51.8KB | 09-30 08:59 |
| `{DATE}_MICRO.log` | 1 | `logs/20260930_MICRO.log` | 31.8KB | 09-30 08:59 |
| `{DATE}_PROBE.log` | 1 | `logs/20260930_PROBE.log` | 12.1KB | 09-30 08:58 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260930_SIGNAL.log` | 5.8KB | 09-30 08:59 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260930_SYSTEM.log` | 27.0KB | 09-30 08:59 |
| `{DATE}_TRADE.log` | 1 | `logs/20260930_TRADE.log` | 167B | 09-30 08:41 |
| `{DATE}_WARN.log` | 1 | `logs/20260930_WARN.log` | 3.3KB | 09-30 08:41 |

## 2. 코드·커밋 상태

- HEAD `89836e3` · 브랜치 `v9-dev` · 미커밋 3건 · 실질 변경 **미측정**(git diff 실패) — 실패 명령: `git diff --numstat → (git 타임아웃 25s — 자식 종료함) git diff --numstat` · 인덱스락 없음
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
```
M docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md
?? dev_memory/_tmp_append_20260929.txt
?? dev_memory/_tmp_append_todo_20260929.txt
```

**당일(2026-09-30) 커밋**
```
(당일 커밋 없음 — 커밋 가능 상태였음)
```

**최근 커밋 12건**
```
89836e3 [MW0601] 639차 후속: 신동 목표 v1 vs v2 확대 비교 — 흐름 5일 + 75일 가격 대리(개정 문서 §8-4)
d9b4063 [MW0601] 637·638·640차 점검 산출물 + 639차 기록 — 9/28·9/29 장전·장중·장후
39f795a [MW0601] 639차: 신동 규격 v2 개정 — 1차 목표가 진입가 뒤에 놓이는 결함 수정
c03b55d [MW0602] 597차 체리픽: 맥점 08:45 결손 차트 TR 보충 — 런처 GUARD 는 보류 (원 2e46abc, dev)
558bd88 [MW0602] 598차 후속 체리픽: requirements.txt 에 markdown==3.4.4 (원 3edd93d, dev)
c561094 [MW0602] 598차 체리픽: 신동 섀도 SHADOW_X4NFA · 채점표 표시 3종 · RETRACTED 로그 · 09:00 봉 결손 내성 (원 6b71762, dev)
3ac32ef [MW0601] 641차 후속: 장후 자동조치 — 637-2 · 638-1
f1efe56 [MW0601] 632차 후속5: MW0602 적용가이드 §10 대응 — 신동 재현 테스트를 PC별로 가르고 불변식으로 보강 + §11 답변
b851e32 [MW0601] 632차 후속4: 신동 일일 리포트 — 파일명·제목·메일에 PC명 표기
b8e9047 [MW0601] 632차 후속: 신동 일일 리포트 — 거래 흐름+손익 vs 섀도 흐름+손익 · PDF · 메일 자동 발송
ba09d5a [MW0602] 적용가이드 §8~§10: MW0602 실행 결과 + 별건 확인요청
1c4afed [MW0601] 636차 후속: 장후 자동조치 — 고도화 방안 2·3·4 (DB pruning 롤백 사실 기록 · 락 이름변경 우회 · md 제목 손상 경고)
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

### 차단 게이트 전수 인벤토리 — 40개 중 **9개 꺼짐**

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
| `SHINDONG_DAILY_REPORT_ENABLED` | True | — |
| `SHINDONG_ENABLED` | True | — |
| `SHINDONG_REPORT_MAIL_ENABLED` | True | — |
| `SHINDONG_RUNNER_SHADOW_ENABLED` | True | — |
| `SIGNAL_DECAY_EXIT_ENABLED` | True | — |
| `SIZING_TARGET_CAPITAL_ENABLED` | True | — |
| `TP1_TICK_ENABLED` | True | — |
| `VOLATILITY_BURST_GUARD_ENABLED` | True | — |
| `WEEKLY_OPTION_FLOW_ENABLED` | True | — |

## 4. 마커·리포트 · 로그 다이제스트

_본문 미열람(설정): `20260930_HOGA.log` 1.2MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/12개 (중요도순). 제외: `launcher_20260930_084000_10534.log`, `freeze_sentinel_20260930.log`, `claude_resume_20260930.log`, `force_flat_guard_20260930.log`_

### `logs/20260930_TRADE.log` — 167B · 2행 · 최종 08:41:04

- 형식 평문 · 시각 인식 2행 · INFO=2

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-30 08:40:58 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-30 08:41:04 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
  …
2026-09-30 08:40:58 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-30 08:41:04 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×2

**컴포넌트 상위 15** — `Position`×1, `ProfitGuard`×1

### `logs/20260930_WARN.log` — 3.3KB · 36행 · 최종 08:41:38

- 형식 평문 · 시각 인식 36행 · WARNING=36

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-30 08:41:07 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-30 08:41:07 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 47ms
2026-09-30 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 172ms account=333044256
2026-09-30 08:41:08 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-09-30 08:41:08 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-09-30 09:00:19 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 30.8ms | size=1955x1124 candles=16 grid=5.4 spans=0.0 candles=0.9 dir=0.0 regime=0.0 markers=0.0 axes=23.2 cross=0.0 | slow_cnt=4 total_cnt=8 overlay_cnt=48
2026-09-30 09:00:34 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 39.8ms | size=1955x1124 candles=16 grid=7.6 spans=0.0 candles=0.8 dir=0.0 regime=0.0 markers=0.0 axes=29.6 cross=0.0 | slow_cnt=5 total_cnt=17 overlay_cnt=83
2026-09-30 09:00:44 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 33.4ms | size=1955x1124 candles=16 grid=6.3 spans=0.0 candles=0.7 dir=0.0 regime=0.0 markers=0.0 axes=24.9 cross=0.0 | slow_cnt=6 total_cnt=18 overlay_cnt=113
2026-09-30 09:00:54 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 44.2ms | size=1955x1124 candles=16 grid=8.8 spans=0.0 candles=0.8 dir=0.0 regime=0.0 markers=0.0 axes=32.8 cross=0.0 | slow_cnt=7 total_cnt=19 overlay_cnt=143
2026-09-30 09:01:00 [WARNING] SYSTEM: [HealthPolicy] Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=2277ms quality=1.00 cache=0s exc10m=0) | cause=S5(996ms)
```

</details>

**WARNING — 태그 11종 (상위 11)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 11 | 08:41:07 | 09:00:06 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `ChartDBG` | 7 | 08:59:47 | 09:00:54 | paintEvent slow 108.7ms | size=1955x1124 candles=15 grid=36.6 spans=0.5 candles=21.0 dir=0.0 regime=0.1 markers=0.2 axes=31.8 cross=0.0 | slow_cnt=1 total_cnt=1 overlay_cnt=0 |
| `SessionBackfill` | 6 | 08:41:38 | 08:41:38 | OHLCV 불일치 ts=2026-09-29 09:57:00 cols=['open'] existing_source=rt |
| `출처축` | 2 | 08:41:08 | 08:41:08 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |
| `SessionStateDrop` | 2 | 08:41:08 | 08:41:08 | 완료 마커 소실 ['p8_last_success_date', 'eod_retrain_ok_date'] — 날짜 전환(2026-09-29 → 2026-09-30)이 새 딕셔너리를 만들면서 이어받지 않았다 (호출부=session_recovery_service.py:increment_session). F-1 미적용 상태에서는 이것이 현재 동작이며, 이 줄의 출현 자체가 0907 리포트 이상점 1-4(판정 근거 정합성)의 확인 수단… |
| `PipePerf` | 2 | 09:00:02 | 09:00:02 | total=2277ms | S0=3ms S1=14ms S2=0ms S3=0ms S4=348ms S5=996ms S6=790ms S7=100ms S8=24ms |
| `CB⑤` | 2 | 09:00:03 | 09:00:03 | 파이프라인 2277ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `OptionFlowChart` | 1 | 08:41:18 | 08:41:18 | 그리기 65.5ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 861x1001 |
| `Health` | 1 | 09:00:02 | 09:00:02 | level=WARNING degraded=OFF | latency=2277ms | quality=1.00 | cache_age=53s | exceptions_10m=0 |
| `MainStallTrace` | 1 | 09:00:06 | 09:00:06 | 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260930.log |
| `HealthPolicy` | 1 | 09:01:00 | 09:01:00 | Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=2277ms quality=1.00 cache=0s exc10m=0) | cause=S5(996ms) |

**채널** — `SYSTEM`×35, `HEALTH`×1

**컴포넌트 상위 15** — `LiveDBG`×11, `ChartDBG`×7, `SessionBackfill`×6, `출처축`×2, `SessionStateDrop`×2, `PipePerf`×2, `CB⑤`×2, `OptionFlowChart`×1, `Health`×1, `MainStallTrace`×1, `HealthPolicy`×1

### `logs/20260930_SYSTEM.log` — 27.0KB · 237행 · 최종 08:59:23

- 형식 평문 · 시각 인식 230행 · INFO=230, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-30 08:40:44 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=29120 | 행감지=30s all_threads=True
2026-09-30 08:40:45 [INFO] SYSTEM: [DBInit] 합계 0.43s | predictions=0.04s trades=0.21s daily_stats=0.01s shap=0.02s raw_data=0.11s broker_pnl=0.01s broker_recon=0.01s premarket_levels=0.03s
2026-09-30 08:40:45 [INFO] SYSTEM: [System] DB 초기화 완료 (0.4s)
2026-09-30 08:40:45 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-30 08:40:45 [INFO] SYSTEM: 미륵이 초기화
  …
2026-09-30 09:01:00 [INFO] SYSTEM: [CVD-ANCHOR] ts=09:00 vol=1110 | live_buy=669 shadow_buy=564 anchor_buy=564 | resid(anchor)=0 resid(shadow)=0 unknown_ticks=0 resets=0
2026-09-30 09:01:00 [INFO] SYSTEM: [ShadowSession] LIVE 전환 | 09:00 | core=90 z=2 가상PnL=+0.0pt
2026-09-30 09:01:00 [INFO] SYSTEM: [ShadowSession] LIVE 전환 | 09:00 | core=90 z=2 가상PnL=+0.0pt
2026-09-30 09:01:00 [INFO] SYSTEM: [S6Detail] ensemble=1ms checklist_pre=15ms meta_gate=13ms gates=1ms imp=0ms shap=9ms corr=0ms dash_ui=1ms tail=20ms
2026-09-30 09:01:00 [INFO] SYSTEM: [PipePerf][DBG] total=833ms | S0=3ms S1=140ms S2=0ms S3=0ms S4=228ms S5=388ms S6=61ms S7=10ms S8=3ms
```

</details>

**채널** — `SYSTEM`×230

**컴포넌트 상위 15** — `CybosRT-TICK`×36, `CybosSub`×21, `System`×17, `TickUI`×16, `CybosRT-ROLLOVER`×16, `BAR-CLOSE`×16, `CVD-ANCHOR`×16, `SYSTEM`×9, `PreMarket`×9, `CybosRT-START`×6, `Notify`×5, `BrokerSync`×4, `BalanceUI`×4, `-`×4, `LEVELS 08:50`×4

### `logs/20260930_SIGNAL.log` — 5.8KB · 123행 · 최종 08:59:00

- 형식 평문 · 시각 인식 123행 · WARNING=66, INFO=57

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-30 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.451
2026-09-30 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.429
2026-09-30 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.425
2026-09-30 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.434
2026-09-30 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.441
  …
2026-09-30 09:01:00 [INFO] SIGNAL: [AutoMasked] 이상값 3개 즉시 격리 예측 (CORE 제외): ['quality_investor_reason_code', 'poc_distance', 'va_bandwidth']
2026-09-30 09:01:00 [INFO] SIGNAL: [FQAdj] fq=1.00 → min_conf 0.45→0.42 (완화)
2026-09-30 09:01:00 [INFO] SIGNAL: 앙상블: dir=+0 conf=0.0% grade=X micro=혼합
2026-09-30 09:01:00 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: FLAT수렴 / conf미달(0.000<mc0.421) | 참고: 이상값피처(quality_investor_reason_code(candidate),poc_distance,va_bandwidth)
2026-09-30 09:01:00 [INFO] SIGNAL: [SHS-EKS-Bar] GAP_OPEN #2 경과=820ms delayed=False policy_blocked=True conf=0.0% core측정=False core통과=False → conf_max 산입=False
```

</details>

**WARNING — 태그 4종 (상위 4)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 30 | 09:00:03 | 09:00:03 | 1m 'macro_vix' scale=0.0208 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerRefresh` | 12 | 08:45:08 | 09:00:03 | 1m CORE 'cvd_divergence' raw_std≈0(0.0082) → identity(0,1) 강제 (FLAT 100% 방지) |
| `Model` | 12 | 09:00:00 | 09:00:01 | 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 12 | 09:00:00 | 09:01:00 | ts=08:59 horizon=1m age=1m max_z=-5.73(institution_futures_net) extreme=2 adj=2 |

**채널** — `SIGNAL`×123

**컴포넌트 상위 15** — `ScalerFloor`×48, `Model`×18, `ScalerRefresh`×18, `ScalerMonitor`×12, `DynMC`×7, `SIGNAL`×4, `TimeRouter`×3, `FQAdj`×2, `ZeroDiag`×2, `SHS-EKS-Bar`×2, `EnsembleGater`×1, `FeatureBuilder`×1, `GapOffset`×1, `MA-cont`×1, `DayRegimeShadow`×1

### `logs/20260930_LEARNING.log` — 51.8KB · 291행 · 최종 08:59:00

- 형식 평문 · 시각 인식 291행 · WARNING=140, INFO=151

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-30 08:40:46 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-30 08:40:49 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00039 auc=0.444 out_max=0.3126 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과
2026-09-30 08:40:49 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00142 auc=0.408 out_max=0.2382 (기준 auc<0.53 and span<0.020, 기저율=0.2375 n=80) → 보정 미적용, raw 통과
2026-09-30 08:40:49 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00033 auc=0.441 out_max=0.3626 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
2026-09-30 08:40:50 [WARNING] LEARNING: [Calibration:5m] 하한 도달불가 — out_max=0.3253 < conf_floor=0.3300 (span=0.00041 auc=0.608 out_max=0.3253, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
  …
2026-09-30 09:00:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0000% buf_n=0 nonzero=0 prev_p=0.00 cur_p=1098.24
2026-09-30 09:00:03 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=500 feat=97
2026-09-30 09:01:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0000% buf_n=1 nonzero=1 prev_p=1098.24 cur_p=1100.60
2026-09-30 09:01:00 [INFO] LEARNING: ✗ 1m 예측 실패 (conf=44.8% 예측=FL 실제=UP)
2026-09-30 09:01:00 [INFO] LEARNING: [SGD] 1건 학습 | SGD비중=30% 50분정확도=50.0%
```

</details>

**WARNING — 태그 7종 (상위 7)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:1m` | 53 | 08:40:49 | 08:40:58 | 축퇴 감지 — span=0.00039 auc=0.444 out_max=0.3126 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과 |
| `Calibration:30m` | 44 | 08:40:49 | 08:40:58 | 축퇴 감지 — span=0.00142 auc=0.408 out_max=0.2382 (기준 auc<0.53 and span<0.020, 기저율=0.2375 n=80) → 보정 미적용, raw 통과 |
| `Calibration:3m` | 17 | 08:40:49 | 08:40:57 | 축퇴 감지 — span=0.00033 auc=0.441 out_max=0.3626 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과 |
| `Calibration:5m` | 10 | 08:40:50 | 08:40:57 | 하한 도달불가 — out_max=0.3253 < conf_floor=0.3300 (span=0.00041 auc=0.608 out_max=0.3253, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:15m` | 8 | 08:40:50 | 08:40:58 | 축퇴 감지 — span=0.00064 auc=0.510 out_max=0.4253 (기준 auc<0.53 and span<0.020, 기저율=0.4250 n=80) → 보정 미적용, raw 통과 |
| `Calibration:10m` | 7 | 08:40:52 | 08:40:56 | 축퇴 감지 — span=0.00041 auc=0.510 out_max=0.4552 (기준 auc<0.53 and span<0.020, 기저율=0.4550 n=200) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:ensemble` | 1 | 08:40:58 | 08:40:58 | 복원한 보정기가 하한 도달불가 — out_max=0.3070 < conf_floor=0.3300 (span=0.00442 auc=0.539 out_max=0.3070, n=1776) → 보정 미적용으로 시작, raw 통과. 축퇴(auc/span)와 별개 사유이며, 표본이 쌓여 출력상한이 하한 위로 올라오면 fit()에서 자동 재적용된다. |

**채널** — `LEARNING`×291

**컴포넌트 상위 15** — `Calibration:1m`×104, `Calibration:30m`×88, `Calibration:3m`×32, `Calibration:5m`×19, `Calibration:15m`×15, `Calibration:10m`×13, `ScalerWarmup`×6, `ExtremityCorrector`×2, `Calibration:ensemble`×2, `Consolidator`×2, `sigma`×2, `RF`×1, `DriftAdjuster`×1, `SHAP`×1, `MetaConf`×1

### `logs/20260930_MICRO.log` — 31.8KB · 100행 · 최종 08:59:38

- 형식 평문 · 시각 인식 100행 · DEBUG=100

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-30 08:45:08 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1099.14/2 ask1=1099.52/1 mp={'microprice_tick': 1099.3934, 'midprice_tick': 1099.33, 'depth_bias_tick': -0.3472} mlofi_tick=None queue=None
2026-09-30 08:45:08 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1099.14/1 ask1=1099.52/2 mp={'microprice_tick': 1099.2667, 'midprice_tick': 1099.33, 'depth_bias_tick': -0.4645} mlofi_tick=-4.4333 queue={'depletion_bid': 1.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 1.0, 'bid_cancel_add_ratio'…
2026-09-30 08:45:08 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1099.14/1 ask1=1099.52/2 mp={'microprice_tick': 1099.2667, 'midprice_tick': 1099.33, 'depth_bias_tick': -0.3971} mlofi_tick=-2.5167 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_rati…
2026-09-30 08:45:08 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1099.16/1 ask1=1099.54/1 mp={'microprice_tick': 1099.35, 'midprice_tick': 1099.35, 'depth_bias_tick': -0.4758} mlofi_tick=13.1333 queue={'depletion_bid': -0.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
2026-09-30 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1099.18/1 ask1=1099.48/1 mp={'microprice_tick': 1099.33, 'midprice_tick': 1099.33, 'depth_bias_tick': -0.4691} mlofi_tick=-5.1833 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
  …
2026-09-30 09:00:40 [DEBUG] MICRO: [MICRO-TICK] #6100 bid1=1098.16/1 ask1=1098.22/1 mp={'microprice_tick': 1098.19, 'midprice_tick': 1098.19, 'depth_bias_tick': 0.0575} mlofi_tick=-5.5167 queue={'depletion_bid': -0.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio…
2026-09-30 09:00:44 [DEBUG] MICRO: [MICRO-TICK] #6200 bid1=1099.02/1 ask1=1099.06/1 mp={'microprice_tick': 1099.04, 'midprice_tick': 1099.04, 'depth_bias_tick': 0.0353} mlofi_tick=5.2167 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio…
2026-09-30 09:00:49 [DEBUG] MICRO: [MICRO-TICK] #6300 bid1=1100.30/1 ask1=1100.36/2 mp={'microprice_tick': 1100.32, 'midprice_tick': 1100.33, 'depth_bias_tick': -0.0022} mlofi_tick=-4.45 queue={'depletion_bid': 1.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 1.0, 'bid_cancel_add_ratio':…
2026-09-30 09:00:54 [DEBUG] MICRO: [MICRO-TICK] #6400 bid1=1100.48/1 ask1=1100.60/1 mp={'microprice_tick': 1100.54, 'midprice_tick': 1100.54, 'depth_bias_tick': 0.0184} mlofi_tick=6.1 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
2026-09-30 09:01:00 [DEBUG] MICRO: [MICRO-MINUTE] #16 ts=2026-09-30 09:00:00 close=1100.60 bias=-0.000277 slope=0.338578 depth_bias=-0.0107 mlofi_norm=0.035880 mlofi_pressure=1 mlofi_slope=63.385000 queue_signal=0.0000 queue_ma=0.0385 queue_momentum=-0.0368 depletion=0.5004 refill=0.4996 imbalance_…
```

</details>

**채널** — `MICRO`×100

**컴포넌트 상위 15** — `MICRO-TICK`×84, `MICRO-MINUTE`×16

### `logs/20260930_DATA.log` — 894B · 6행 · 최종 08:58:41

- 형식 평문 · 시각 인식 6행 · INFO=6

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-30 08:58:11 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=-197 individual=+90 institution=+102 oi=0 call_foreign=-280 put_foreign=+177 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-09-30 08:58:11 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=True program_supported=False option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=runtime_disabled
2026-09-30 08:58:41 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=-206 individual=+94 institution=+107 oi=0 call_foreign=-286 put_foreign=+157 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-09-30 08:58:41 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=True program_supported=False option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=runtime_disabled
2026-09-30 09:00:00 [INFO] DATA: [DivergencePanel] source=cybos status=partial div=-300 futures(fi=-206 rt=+94 inst=+107) call(fi=-286 rt=+283) put(fi=+157 rt=-148) bias(fi=-1.00 rt=1.00) program(arb=+0 nonarb=+0 total=+0)
  …
2026-09-30 08:58:11 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=True program_supported=False option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=runtime_disabled
2026-09-30 08:58:41 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=-206 individual=+94 institution=+107 oi=0 call_foreign=-286 put_foreign=+157 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-09-30 08:58:41 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=True program_supported=False option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=runtime_disabled
2026-09-30 09:00:00 [INFO] DATA: [DivergencePanel] source=cybos status=partial div=-300 futures(fi=-206 rt=+94 inst=+107) call(fi=-286 rt=+283) put(fi=+157 rt=-148) bias(fi=-1.00 rt=1.00) program(arb=+0 nonarb=+0 total=+0)
2026-09-30 09:01:00 [INFO] DATA: [DivergencePanel] source=cybos status=partial div=-300 futures(fi=-206 rt=+94 inst=+107) call(fi=-286 rt=+283) put(fi=+157 rt=-148) bias(fi=-1.00 rt=1.00) program(arb=+0 nonarb=+0 total=+0)
```

</details>

**채널** — `DATA`×6

**컴포넌트 상위 15** — `CybosInvestor`×4, `DivergencePanel`×2

### `logs/20260930_PROBE.log` — 12.1KB · 4행 · 최종 08:58:41

- 형식 평문 · 시각 인식 4행 · INFO=4

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-30 08:41:08 [INFO] PROBE: [CybosInvestorProbe] not implemented; extra_codes=['A056A']
2026-09-30 08:58:11 [INFO] PROBE: [CybosProbe] CpSysDib.CpSvrNew7221 ok status=0 nonempty_headers=3 rows=30
2026-09-30 08:58:11 [INFO] PROBE: [CybosProbe][RAW] CpSysDib.CpSvrNew7221 field_limit=64 headers={0: '28', 1: '28', 2: '75'} rows_sample=[{0: '0', 1: '0', 2: '0', 3: '0', 4: '0', 5: '0', 6: '0', 7: '0', 8: '0', 9: '0', 10: '0', 11: '0', 12: '0', 13: '0', 14: '0', 15: '0', 16: '0', 17: '0', 18: '0',…
2026-09-30 08:58:41 [INFO] PROBE: [CybosProbe] CpSysDib.CpSvrNew7221 ok status=0 nonempty_headers=3 rows=30
  …
2026-09-30 08:41:08 [INFO] PROBE: [CybosInvestorProbe] not implemented; extra_codes=['A056A']
2026-09-30 08:58:11 [INFO] PROBE: [CybosProbe] CpSysDib.CpSvrNew7221 ok status=0 nonempty_headers=3 rows=30
2026-09-30 08:58:11 [INFO] PROBE: [CybosProbe][RAW] CpSysDib.CpSvrNew7221 field_limit=64 headers={0: '28', 1: '28', 2: '75'} rows_sample=[{0: '0', 1: '0', 2: '0', 3: '0', 4: '0', 5: '0', 6: '0', 7: '0', 8: '0', 9: '0', 10: '0', 11: '0', 12: '0', 13: '0', 14: '0', 15: '0', 16: '0', 17: '0', 18: '0',…
2026-09-30 08:58:41 [INFO] PROBE: [CybosProbe] CpSysDib.CpSvrNew7221 ok status=0 nonempty_headers=3 rows=30
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

### 메인 스레드 블로킹 3건 · 최대 6359ms · 5초 초과 1건

상위 — 6359ms, 3438ms, 2891ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:00:06 | 6359ms | 2277ms | **4082ms (64%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260930_WARN.log`
```
--- 메인 스레드 블로킹 ×3(표본)
08:41:11 2026-09-30 08:41:11 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3438ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3438 band=INFO since_pipe_s=NA
08:59:50 2026-09-30 08:59:50 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2891ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2891 band=INFO since_pipe_s=NA
09:00:06 2026-09-30 09:00:06 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 6359ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=6359 band=WARN since_pipe_s=0.3
```

### `logs/20260930_SYSTEM.log`
```
--- PSI ×1(표본)
09:00:00 2026-09-30 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
```

### `logs/20260930_SIGNAL.log`
```
--- 기동 복원 ×7(표본)
08:40:41 2026-09-30 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.451
08:40:41 2026-09-30 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.429
08:40:41 2026-09-30 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.425
08:40:41 2026-09-30 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.434
```

### `logs/20260930_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:49 2026-09-30 08:40:49 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00039 auc=0.444 out_max=0.3126 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과
08:40:49 2026-09-30 08:40:49 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00142 auc=0.408 out_max=0.2382 (기준 auc<0.53 and span<0.020, 기저율=0.2375 n=80) → 보정 미적용, raw 통과
08:40:49 2026-09-30 08:40:49 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00033 auc=0.441 out_max=0.3626 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
08:40:50 2026-09-30 08:40:50 [WARNING] LEARNING: [Calibration:5m] 하한 도달불가 — out_max=0.3253 < conf_floor=0.3300 (span=0.00041 auc=0.608 out_max=0.3253, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260930_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:40:58 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:40 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260930_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 20 | 08:41:07 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 16 | 08:59:47 [WARNING] paintEvent slow 108.7ms | size=1955x1124 candles=15 grid=36.6 spans=0.5 candles=21.0 dir=0.0 regime=0.1 marke… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 16 | 08:59:47 [WARNING] paintEvent slow 108.7ms | size=1955x1124 candles=15 grid=36.6 spans=0.5 candles=21.0 dir=0.0 regime=0.1 marke… |

- 이 로그 생존구간: 08:41 ~ 09:01

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260930_SYSTEM.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 92 | 08:40:44 [INFO] 활성화 | file=logs\crash_fault.log PID=29120 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 125 | 08:49:01 [INFO] code=A056A from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 91 | 08:54:00 [INFO] code=A056A from=08:53 to=08:54 |

- 이 로그 생존구간: 08:40 ~ 09:01

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260930_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 44 | 08:45:08 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0082) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 78 | 09:00:00 [WARNING] 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 77 | 09:00:00 [WARNING] 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |

- 이 로그 생존구간: 08:40 ~ 09:01

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260929 | 15:47 | 로그 본문 |
| 20260928 | 15:47 | 로그 본문 |
| 20260926 | 16:50 | 로그 본문 |
| 20260924 | 10:58 | 로그 본문 |
| 20260923 | 18:44 | 로그 본문 |
| **중앙값** | **15:47** | 기준선 |
| **오늘 20260930** | **09:01** | 로그 본문 |

- 델타 **-406분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.3MB · 마지막 갱신 2026-09-29 18:50

최근 헤딩 8개:
```
## 2026-09-28 (MW0601 634차 — 장중 점검)
## 2026-09-28 (MW0601 635차 — 장후 점검)
## 2026-09-28 (MW0601 636차 — 장후 자동조치: 고도화 방안 2·3·4 구현 + DB pruning 「삭제 성공」 판단 정정)
## 2026-09-29 (MW0601 637차 — 장전 점검)
## 2026-09-29 (MW0601 638차 — 장중 점검)
## 2026-09-29 (MW0601 639차 — 신동 규격 v2 개정: 1차 목표가 진입가 뒤에 놓이는 결함) — ✅ **커밋 39f795a (사용자 지시 2026-09-29 「v2 작업을 먼저 커밋」)**
## 2026-09-29 (MW0601 640차 — 장후 점검)
## 2026-09-29 (MW0601 641차 — 장후 자동조치: 637-2 crash_fault.log 네이티브 오류 집계 + 638-1 git 실패 진단·이중 방어)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
tp1_reached는 값 전부 NULL이라 exit_stage 우선 사용).

⚠ **코드 변경 없음(일반 장후 점검 세션 — `mireuk-postmarket-autofix` 자동조치 예약이 아님).** `git commit`·`git push` 하지 않았음 — 사용자가 직접 확인 후 커밋한다.

## 2026-09-29 (MW0601 641차 — 장후 자동조치: 637-2 crash_fault.log 네이티브 오류 집계 + 638-1 git 실패 진단·이중 방어)

**증상**: ① `logs/crash_fault.log` 는 파일명에 날짜가 없어 수집기 §1 당일 인벤토리에 안 잡히고, `utils/wer_crash.py:crash_fault_events()` 는 `[START]`/`[CLEAN EXIT]` 만 파싱해 **프로세스가 살아남은** `Windows fatal exception` 은 어느 절에도 안 떴다 — 2026-09-28 access violation 4건(부팅 3 + 11:33 장중 1)이 그날 장전 리포트에서 0회 등장. ② 2026-09-29 12:27 장중 수집에서 `git diff` 실패 직후 0바이트 `.git/index.lock` 이 남았는데, 다이제스트엔 「git diff 실패」만 있어 어느 하위 명령이 어떤 rc·stderr 로 죽었는지 특정 불가.

**원인**: ① 파서가 종료 판정(3축 대사) 용도로만 설계돼 「살아남은 오류」 축이 없었다. ② `git_change_profile()` 이 `run_git()` 반환 문자열(이미 rc·stderr 를 담고 있음)을 버리고 `measured=False` 만 남겼다.

**결정**:
1. (637-2) `crash_fault_events()` 에 PID별 `fatal`(kind + 직전 표식 시각 `after`) 과 `fatal_total` 추가. 파일 부재 시 `fatal_total=None`(미측정 ≠ 0). 기존 키·판정 무변경.
2. 수집기 §9 3축 대사 표에 `crash_fault.log(Windows fatal exception — 살아남은 것 포함)` 행 + PID별 줄(종류별 건수 · 직전 표식 시각 · 정규장 09:00 이후 건수), §11 적신호에 **1건부터** 등재. `wer_crash_section()` 이 `fau` 를 반환하도록 변경.
3. (638-1) `run_git()` 이 `GIT_OPTIONAL_LOCKS=0` 을 환경변수로도 넘긴다(플래그는 최상위 git 에만, 환경변수는 자식 git 까지 상속). `git_change_profile()` 에 `fail_reason`(실패 명령 + rc·stderr) 추가, §2·§11 에 렌더링.
4. G-2(access violation 경고 문턱 5건)는 **구현하지 않는다** — 리포트 스스로 「관측일 3건, 313차 미통과, 문턱 확정 안 함」. §11 은 문턱 없이 건수만 올린다. NEXT_TODO 641-1 로 이월.
5. P5-17 은 관찰 등록 단계(변경대상 「제안 아님」, 기대효과 미산정)라 6칸 미충족 → 구현 대상 아님(640-1 유지).

**Why**: 계측 4원칙 ②·③ — 「파일명 규칙 때문에 안 보인다」는 탈락이 가시화되지 않은 사례이고, 「git diff 실패」는 사유 없는 폴백이었다. 638-1 의 환경변수 이중화는 **원인 확정이 아니라 이중 방어**다(마운트 경유 환경에서 플래그만으로 락을 못 막았다는 것은 추정).

**How to apply**: `after` 는 **발생 시각이 아니라 하한**이다(faulthandler 머리줄에 시각 없음) — 리포트에서 "HH:MM 이후"로 적을 것. §11 에 이 줄이 뜨면 §9 PID별 줄로 부팅 구간/장중을 가른다. 다음 `git diff` 실패 시 §2 「실패 명령:」 문자열로 원인을 좁힐 것.

**검증**: `tests/test_641_crash_fault_fatal_and_git_diag.py` 12건 + `test_620`·`test_624` 회귀 통과(35 passed, py37_32). 실데이터 재생: `--date 2026-09-28` → 4건(09:00 이후 1건, 11:33:47 이후), `--date 2026-09-29` → 3건(09:00 이후 0건) — 장전·장후 리포트의 손 집계와 일치. 수집 후 `.git/index.lock` 없음. 전체 스위트 결과는 아래 줄.
**전체 스위트**(py37_32): 2448 passed · **12 failed** · 3 skipped — 12건 전부 이번 변경과 무관한 기존 실패(	est_457 main_dashboard peter_paste · 	est_498 CybosInvestor 미등록 · 	est_483 fuoption 사본 · 	est_504 4 · 	est_477·	est_493·	est_554·	est_621·	est_628 각 1). 어느 것도 wer_crash·collect_evidence 를 참조하지 않는다(grep 확인). 전일(636차) 기준선 14건보다 적다.

```

</details>

### dev_memory/NEXT_TODO.md — 1.6MB · 마지막 갱신 2026-09-29 18:50

최근 헤딩 8개:
```
## 2026-09-28 (MW0601 633차 — 장전 점검)
## 2026-09-28 (MW0601 634차 — 장중 점검)
## 2026-09-28 (MW0601 635차 — 장후 점검)
## 2026-09-28 (MW0601 636차 — 장후 자동조치)
## 2026-09-29 (MW0601 637차 — 장전 점검)
## 2026-09-29 (MW0601 638차 — 장중 점검)
## 2026-09-29 (MW0601 640차 — 장후 점검)
## 2026-09-29 (MW0601 641차 — 장후 자동조치)
```

미완료 체크박스 **2895건** (끝에서 30건)
```
- [ ] **633-1 (P2, 신규)** `docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md` 1행 마크다운 제목(`# 재시작...`) 손상 상태로 미커밋 — 사용자에게 의도한 편집인지 확인 후, 아니라면 `git checkout --`로 복원. 근거: 0928 장전 리포트 이상점 1-1.
- [ ] **633-2 (고도화, P2)** `[PreRetrain]` 판정에서 `data/eod_retrain_done_{d}.txt` 마커 파일 직접 확인 경로를 "미기록 보완"이 아니라 1차 확인 경로로 격상 검토 — 근거: `SessionStateDrop`(606-2 근본원인 미해결) 발생 시마다(09-14·09-17·09-21·09-22·09-…
- [ ] **633-3 (고도화, P2)** 커밋 전 프리플라이트(`scripts/git_lock_guard.py` 또는 별도 스크립트)에 "마크다운 파일 첫 줄이 `# `로 시작하다가 사라졌는가" 같은 가벼운 문서 손상 탐지 경고 추가 검토 — 근거: 0928 이상점 1-1(재현 1건, 원인 미상).
- [ ] **633-4** `opt_chain_pcr`(옵션체인 → 30m CORE 피처 입력) 로드 로그가 0928 장전(08:40~09:00) 구간에 미확인 — 장중 점검에서 재확인.
- [ ] **633-5 (P1, 신규)** `.git/index.lock`(0바이트) 스테일 확정 후에도 `--reclaim`이 `EPERM`으로 실패 — 코웍 마운트 경유 세션의 구조적 한계(SKILL.md 예고대로 재현). 사용자가 로컬에서 직접 삭제하거나 `--reclaim` 재시도 필요. 근거: 0928 장전 리포트 이상점 1-2.
- [ ] **634-1 (P2, 고도화)** `scripts/git_lock_guard.py --reclaim`이 `unlink` 실패(`EPERM`) 시 `os.rename()`으로 `<파일>.stale.<pid>` 우회를 자동 시도하도록 — 단 "스테일 확정" 판정 후에만 동작하고 "판정보류"에서는 지금처럼 손대지 않아야 함. 근거: 0928 장전·…
- [ ] **634-2** 사용자 확인 대기 유지 — `docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md` 제목 손상(633-1 계승). 잠금 해소로 이제 언제든 `git checkout --`로 되돌릴 수 있음, 의도한 편집인지 확인 먼저.
- [ ] **635-1** `docs/정기점검/수익률향상_누적대장.md`의 P5-03(TP1 비중·보호 트레일 오프셋)에 09-28 CASE-01을 표본으로 추가(3m, TP1 33%→TRAIL_AFTER_TP1, 발동가 1107.22, 발동 직후 저가 1106.26, 미실현 추가폭 약 0.96pt) — 다음 장후가 대장 파일에 직접 반영할 것.
- [ ] **635-2** `.claude/skills/mireuk-daily-check/references/evidence_map.md` §8-3 갱신 — v9-dev `trades` 테이블에 `tp1_reached`·`exit_trigger`·`exit_outcome` 컬럼이 이미 존재함(2026-09-28 `PRAGMA table_info` 실측,…
- [ ] **635-3 (고도화, P2)** `learning/batch_retrainer.py:prune_raw_data_db()` — "DB pruning 실패: database table is locked" 경고가 실제로는 4개 테이블 DELETE 성공(오늘 22,860행) 후 `PRAGMA wal_checkpoint(PASSIVE)` 단계에서만 …
- [ ] **633-1 (P2)** 사용자 확인 대기 유지 — `docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md` 제목 손상(633-1/634-2 계승, 0928 장후에도 미확인 상태 지속).
- [ ] **636-1 (사용자, 1분)** `scripts/git_lock_guard.py` 정본을 fuoption 사본(`..\fuoption\scripts\git_lock_guard.py`)에 복사 — 자동조치 세션의 덮어쓰기가 권한 거부됨. 복사 전까지 `test_483::test_sibling_copy_matches_canonical[fuopt…
- [ ] **636-2 (승인 대기, P2)** `prune_raw_data_db()` 실제 삭제 수정 — DELETE 루프 뒤 `conn.commit()`, `PRAGMA wal_checkpoint(PASSIVE)`는 별도 try(실패해도 삭제는 유지, 로그 `완료(체크포인트 보류)`). 현재는 자기 트랜잭션 안 체크포인트 → `database tab…
- [ ] **636-3 (C — 사용자 지시 필요)** 고도화 방안 1: `[PreRetrain]` 판정에서 마커 파일(`data/eod_retrain_done_{날짜}.txt`)을 1차 경로로 격상. main.py 재학습 스킵 순서 변경이라 자동조치 범위 밖. 606-2 근본수정과 함께 판단.
- [ ] **636-4 (정리)** DECISION_LOG 636차 항목은 작업본에 append 만 됐고 **미커밋** — 같은 파일에 다른 세션(신동 R3 딥다이브)의 미커밋 변경(전 파일 줄바꿈 변경 + 중간 삽입)이 있어 골라 커밋할 수 없었다. 그 세션 커밋 때 함께 들어가면 된다.
- [ ] **636-5 (정리)** `md_title_guard.py`를 SKILL.md 커밋 전 프리플라이트(`git_lock_guard.py --check` 옆)에 한 줄 추가할지 결정.
- [ ] **637-1 (P1)** `dev_memory/NEXT_TODO.md` 606-4(09-17 access violation 원인 조사 우선순위 결정)에 09-28(4건)·09-29(3건) 재현을 근거로 추가 — 사용자가 우선순위를 정할 때 참고. 전부 부팅 구간(정규장 개시 전) 한정, 정규장 개시 후 재현 0건. 새 조사 착수는 사용자 결정…
- [ ] **637-2 (P2, 신규)** `scripts/collect_evidence.py` §1 당일 파일 인벤토리·§11 자동 적신호가 `logs/crash_fault.log`(날짜 토큰 없는 누적 로그)를 구조적으로 못 본다 — `crash_fault_events()`(§9)는 "정상종료 기록" 판정용이지 "access violation 건수 …
- [ ] **633-1 (P2)** 사용자 확인 대기 유지 — `docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md` 제목 손상, 0929 장전에도 미확인·미커밋 상태 지속(3번째 날).
- [ ] **638-1 (P1, 신규)** `scripts/collect_evidence.py`의 `git diff`(미커밋 변경량 측정) subprocess 호출부 — 실패 시 정확한 명령·종료코드·stderr를 다이제스트에 로깅하도록 강화 + `GIT_OPTIONAL_LOCKS=0` 환경변수를 `--no-optional-locks` 플래그와 함께 이…
- [ ] **638-2 (사용자, 대기)** `.git/index.lock`(2026-09-29 12:27:19 생성) 판정보류 지속 중(12:32 기준 나이 338초, 임계 600초 미도달) — 600초 경과 후 사용자가 본인 컴퓨터에서 직접 `python scripts/git_lock_guard.py --check` 재실행, 스테일이면 `--recl…
- [ ] **606-4 (참고 보강)** 09-28 소급 access violation 4건 중 1건이 부팅 구간이 아니라 11:33경(장중)에도 발생했음을 추가 확인 — 조사 우선순위 결정은 여전히 사용자 몫.
- [ ] **633-1 (P2)** 사용자 확인 대기 유지 — `docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md` 제목 손상, 0929 장중에도 미확인·미커밋 지속(3번째 날, 변화 없음).
- [ ] **640-1** P5-17(5m 호라이즌 TIER1_EARLY→INITIAL_STOP 연쇄 손절 관찰) — 오늘 CASE4·5·8 3건/1거래일, 합계 −380,476원. 신규 채널(`horizon_5m_early_stop_watch` 가칭) 신설 여부는 사용자 판단 — 우선은 다음 장후들이 5m 호라이즌 진입 결과를 계속 케이스로 기록해 표…
- [ ] **640-2** `docs/정기점검/수익률향상_누적대장.md` P5-03에 0928 CASE-01 표본이 아직 반영되지 않음(635-1 계승, 2회째 미처리 확인) — 다음 세션이 직접 대장 파일을 열어 반영할 것.
- [ ] **640-3 (사용자, 참고)** 신동(별도 매매 모듈) v2 개정(639차, 별도 세션) — 내일(09-30) 자동 기동 시 라이브 반영 예정. 규격 준수 근거로 개정됐으나 과거 5거래일 재현에서는 v1(결함 버전)이 오히려 손실이 적었다는 상반된 실측 기록 있음 — 사용자가 `docs/신동거래/신동_개정_v2_1차목표역전_20260929.…
- [ ] **O-t1** 09-30 장전 부팅 구간 access violation 재현 여부(3일 연속 뒤 4일째 확인) — 606-4 우선순위 결정 참고자료 계속 축적.
- [ ] **O-t2** 09-30 장전 거래일 전환 시 SessionStateDrop 재현 여부 확인(근본원인 606-2 미해결로 재현 예상, 예상대로면 지속 기록만).
- [ ] **633-1 (P2)** 사용자 확인 대기 유지 — 문서 제목 손상, 0929 장후에도 미확인·미커밋 지속(4일째).
- [ ] **641-1 (G-2, 보류)** 부팅 구간 access violation 경고 **문턱** 신설 여부 — 관측일 3건(09-17·09-28·09-29)뿐이라 313차 가드 미통과. 지금 §11 은 문턱 없이 1건부터 건수만 올린다. 관측일이 더 쌓이면(예: 10거래일) 분포를 보고 문턱을 정할 것. 606-4(원인 조사 우선순위, 사용자 결…
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
후 사용자가 본인 컴퓨터에서 직접 `python scripts/git_lock_guard.py --check` 재실행, 스테일이면 `--reclaim`, 여전히 판정보류면 대기. 절대 원격 세션에서 지우지 말 것(EPERM 위험).
- [x] **633-4 종결** — `opt_chain_pcr` 로드 로그 미확인 항목, 0929 장중에 `[OptionChain][Worker]`/`[OptionBook]` 09:01:29~09:42:13 반복 정상 완료로 해소 확인.
- [ ] **606-4 (참고 보강)** 09-28 소급 access violation 4건 중 1건이 부팅 구간이 아니라 11:33경(장중)에도 발생했음을 추가 확인 — 조사 우선순위 결정은 여전히 사용자 몫.
- [ ] **633-1 (P2)** 사용자 확인 대기 유지 — `docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md` 제목 손상, 0929 장중에도 미확인·미커밋 지속(3번째 날, 변화 없음).

- [x] **638-2 갱신 — 종결(주 이슈)** `.git/index.lock` 12:37 스테일 확정 → `git_lock_guard.py --reclaim`으로 정상 회수, 커밋 가능 상태 복귀 확인. 잔여 부스러기(`index.lock.stale_20260929033733_6`) 정리만 선택사항으로 남김(급하지 않음, 사용자 한가할 때).

## 2026-09-29 (MW0601 640차 — 장후 점검)

- [ ] **640-1** P5-17(5m 호라이즌 TIER1_EARLY→INITIAL_STOP 연쇄 손절 관찰) — 오늘 CASE4·5·8 3건/1거래일, 합계 −380,476원. 신규 채널(`horizon_5m_early_stop_watch` 가칭) 신설 여부는 사용자 판단 — 우선은 다음 장후들이 5m 호라이즌 진입 결과를 계속 케이스로 기록해 표본(`min_samples=20` 且 `min_days=10`)을 쌓는다. 근거: 0929 장후 제4·5부.
- [ ] **640-2** `docs/정기점검/수익률향상_누적대장.md` P5-03에 0928 CASE-01 표본이 아직 반영되지 않음(635-1 계승, 2회째 미처리 확인) — 다음 세션이 직접 대장 파일을 열어 반영할 것.
- [ ] **640-3 (사용자, 참고)** 신동(별도 매매 모듈) v2 개정(639차, 별도 세션) — 내일(09-30) 자동 기동 시 라이브 반영 예정. 규격 준수 근거로 개정됐으나 과거 5거래일 재현에서는 v1(결함 버전)이 오히려 손실이 적었다는 상반된 실측 기록 있음 — 사용자가 `docs/신동거래/신동_개정_v2_1차목표역전_20260929.md`를 확인해 유지/보류 판단 필요. 미륵이 선물 점검 범위 밖(참고 전달만).
- [x] **O-p1 관련 이월** — 오늘 EOD가 정상 기록한 `p8_last_success_date`·`eod_retrain_ok_date`(2026-09-29)는 내일(09-30) 장전이 거래일 전환 재현 여부를 다시 판정할 대상 — O-t2로 등록.
- [ ] **O-t1** 09-30 장전 부팅 구간 access violation 재현 여부(3일 연속 뒤 4일째 확인) — 606-4 우선순위 결정 참고자료 계속 축적.
- [ ] **O-t2** 09-30 장전 거래일 전환 시 SessionStateDrop 재현 여부 확인(근본원인 606-2 미해결로 재현 예상, 예상대로면 지속 기록만).
- [ ] **633-1 (P2)** 사용자 확인 대기 유지 — 문서 제목 손상, 0929 장후에도 미확인·미커밋 지속(4일째).

## 2026-09-29 (MW0601 641차 — 장후 자동조치)

- [x] **637-2 완료** — `crash_fault.log` 의 `Windows fatal exception` 을 PID별로 집계해 수집기 §9 표·§11 적신호에 올린다(`utils/wer_crash.py` `fatal`/`fatal_total`, `collect_evidence.py:fatal_exception_lines`). 검증: 09-28 4건 · 09-29 3건 재현. `tests/test_641_*`.
- [x] **638-1 완료** — `run_git()` 에 `GIT_OPTIONAL_LOCKS=0` 환경변수 이중 전달 + `git_change_profile()` `fail_reason`(실패 명령·rc·stderr) 을 §2·§11 에 표기. ⚠ 락 생성 원인 확정이 아니다 — 다음 `git diff` 실패 때 §2 「실패 명령:」 으로 원인을 좁혀 이 항목을 재평가할 것.
- [ ] **641-1 (G-2, 보류)** 부팅 구간 access violation 경고 **문턱** 신설 여부 — 관측일 3건(09-17·09-28·09-29)뿐이라 313차 가드 미통과. 지금 §11 은 문턱 없이 1건부터 건수만 올린다. 관측일이 더 쌓이면(예: 10거래일) 분포를 보고 문턱을 정할 것. 606-4(원인 조사 우선순위, 사용자 결정 대기)와 함께 볼 것.

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

### `data/heartbeat_MW0601_20260930.json` — 245B · 09-30 08:59:39
```json
{
 "pid": 29120,
 "written_at": "2026-09-30T09:00:39",
 "beat_epoch": 1790726438.4513333,
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

- 파일 최종 기록: **09-30 08:46:00**

| 키 | 값 | 수집 대상일(2026-09-30)과 일치 |
|---|---|---|
| `date` | 2026-09-30 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

### `raw_candles` 절단선·결손 (618차)

| 항목 | 값 |
|---|---|
| `raw_candles` 당일 max ts | **09:00** |
| 절단선(파생 = 강제청산 − 2분) | `15:08` |
| 판정 | **결손** — 아래 목록과 그 시각의 `[START]`/`[CLEAN EXIT]` 대조 |
| `raw_candles` 당일 행수 | 16 |
| `session_bars` 당일 행수 | 16 (기대 411) |

- 결손 **0봉**
- ⚠ **영구 결손 368봉** (`session_bars` 에도 없음): 09:01, 09:02, 09:03, 09:04, 09:05, 09:06, 09:07, 09:08, 09:09, 09:10, 09:11, 09:12, 09:13, 09:14, 09:15, 09:16, 09:17, 09:18, 09:19, 09:20

- 라이브 로그 대조: `logs/20260930_SYSTEM.log` 의 `[BarGap]` 줄
  - 기동 직후 1줄(분그리드 기준) + 15:46 보충 직후 1줄(확정). **한 줄도 없으면 계측이 죽은 것**이지 결손이 없는 것이 아니다.

> 결손 ts 는 그날 재기동 시각과 1:1 대응한다(실측 2026-09-07~09-22: 결손일 3/12일, 12봉, 09-21 은 8회 재기동에 7봉). `[Shutdown] intent=` 줄과 함께 보면 그 재기동이 사용자 의도인지 하드킬인지까지 갈린다.


### 프로세스 종료 3축 대사 (620차)

| 축 | 상태 |
|---|---|
| 런처 로그(기동 PID·재시작 분류) | 측정됨 — 기동 1회 · 재시작 0회 |
| `crash_fault.log`(정상종료 기록) | 측정됨 — PID 1개 |
| `crash_fault.log`(`Windows fatal exception` — 살아남은 것 포함) | 측정됨 — **3건** |
| Windows WER(네이티브 예외) | **미측정** — 비Windows 플랫폼 — WER 이벤트 로그가 없다 |

- PID 29120: `Windows fatal exception` **3건** (access violation 3) — 직전 표식 시각 08:40:44 · 정규장(09:00) 이후 **0건**
  - 시각은 **발생 하한**이다(머리줄에 시각이 없다). 프로세스가 죽지 않은 오류이므로 위 종료 판정과 별개로 읽을 것. 스택은 `logs/crash_fault.log` 원문

| 미륵이 PID | 기동 | 정상종료 기록 | WER 네이티브 예외 | 판정 |
|---|---|---|---|---|
| 29120 | 08:40:44 | 없음 | 없음 | 판정불가 — WER **미측정** |


> 🔴 **「WER 기록 없음」을 「크래시가 아니다」로 읽지 말 것.** 참인 것은 **「미처리 네이티브 예외는 아니었다」까지**다 — `sys.exit`·창 닫기·`TerminateProcess`(하드킬)는 전부 이벤트를 안 남긴다. 종료 *의도*는 618차가 넣은 `[Shutdown] intent=` 줄과 함께 봐야 갈린다.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 177개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/evidence_MW0601-20260929_pre.md` | 59.0KB | 09-29 18:50 |
| `docs/정기점검/매일점검/evidence_MW0601-20260929_post.md` | 90.0KB | 09-29 18:50 |
| `docs/정기점검/매일점검/evidence_MW0601-20260929_intra.md` | 74.7KB | 09-29 18:50 |
| `docs/정기점검/매일점검/evidence_MW0601-20260928_pre.md` | 56.8KB | 09-29 18:50 |
| `docs/정기점검/매일점검/evidence_MW0601-20260928_post.md` | 84.8KB | 09-29 18:50 |
| `docs/정기점검/매일점검/evidence_MW0601-20260928_intra.md` | 74.0KB | 09-29 18:50 |
| `docs/정기점검/매일점검/MW0601-20260929-점검리포트.md` | 87.5KB | 09-29 18:50 |
| `docs/정기점검/매일점검/MW0601-20260928-점검리포트.md` | 81.3KB | 09-28 17:47 |

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

1. 메인 스레드 정지 5초 초과 **1건** (최대 6359ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
2. `logs/20260930_LEARNING.log`: **축퇴** 8건(표본)
3. `logs/crash_fault.log`: `Windows fatal exception` **3건** (정규장 09:00 이후 0건) — 프로세스는 살아남았다. §9 「프로세스 종료 3축 대사」 아래 PID별 표를 볼 것 (641차 637-2)
4. 미커밋 변경 3건 — **실질 변경 미측정**(git diff 실패). 원시 건수만으로는 착시인지 알 수 없다 · 실패 명령: `git diff --numstat → (git 타임아웃 25s — 자식 종료함) git diff --numstat`

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260930*.log` (Windows) / `grep 강제청산 logs/*20260930*.log`*