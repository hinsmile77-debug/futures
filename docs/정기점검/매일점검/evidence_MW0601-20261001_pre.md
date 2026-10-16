# 미륵이 증거 다이제스트 — 2026-10-01 / PRE

- 생성 2026-10-01 08:59:42 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/rcw-01svmzf2vvabemjwrjg81f4w/mnt/futures`
- 점검 범위: pre (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20261001` · `2026-10-01` · `261001` · `1001`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **20개** 파일 · 20개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `claude_resume_{DATE}.log` | 1 | `logs/claude_resume_20261001.log` | 271B | 10-01 07:48 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20261001.log` | 125B | 10-01 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20261001.log` | 140B | 10-01 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20261001.json` | 244B | 10-01 08:59 |
| `launcher_{DATE}_084001_30537.log` | 1 | `logs/Mireuk_batch/launcher_20261001_084001_30537.log` | 53.7KB | 10-01 08:58 |
| `retrain_intraday_20260701_13{DATE}.log` | 1 | `logs/retrain_intraday_20260701_131001.log` | 4.6KB | 07-01 13:10 |
| `retrain_intraday_20260703_13{DATE}.log` | 1 | `logs/retrain_intraday_20260703_131001.log` | 4.6KB | 07-03 13:10 |
| `retrain_intraday_20260731_13{DATE}.log` | 1 | `logs/retrain_intraday_20260731_131001.log` | 4.5KB | 07-31 13:10 |
| `retrain_intraday_20260819_10{DATE}.log` | 1 | `logs/retrain_intraday_20260819_101001.log` | 2.4KB | 08-19 10:10 |
| `{DATE}_DATA.log` | 1 | `logs/20261001_DATA.log` | 890B | 10-01 08:58 |
| `{DATE}_DEBUG.log` | 1 | `logs/20261001_DEBUG.log` | 0B | 10-01 08:40 |
| `{DATE}_HEALTH.log` | 1 | `logs/20261001_HEALTH.log` | 0B | 10-01 08:40 |
| `{DATE}_HOGA.log` | 1 | `logs/20261001_HOGA.log` | 1.4MB | 10-01 08:59 |
| `{DATE}_LEARNING.log` | 1 | `logs/20261001_LEARNING.log` | 56.4KB | 10-01 08:59 |
| `{DATE}_MICRO.log` | 1 | `logs/20261001_MICRO.log` | 33.3KB | 10-01 08:59 |
| `{DATE}_PROBE.log` | 1 | `logs/20261001_PROBE.log` | 12.1KB | 10-01 08:58 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20261001_SIGNAL.log` | 6.6KB | 10-01 08:59 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20261001_SYSTEM.log` | 27.7KB | 10-01 08:59 |
| `{DATE}_TRADE.log` | 1 | `logs/20261001_TRADE.log` | 167B | 10-01 08:41 |
| `{DATE}_WARN.log` | 1 | `logs/20261001_WARN.log` | 3.7KB | 10-01 08:59 |

## 2. 코드·커밋 상태

- HEAD `67cff42` · 브랜치 `v9-dev` · 미커밋 10건 · 실질 변경 4건 · 코드(.py) 0건 · EOL 파생 0건 (추적변경 4 · 미추적 6 · 삭제 0 · core.autocrlf=미설정) · 인덱스락 없음
  - 실질 변경 파일: `dev_memory/DECISION_LOG.md`, `dev_memory/NEXT_TODO.md`, `docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md`, `docs/정기점검/수익률향상_누적대장.md`
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
```
M dev_memory/DECISION_LOG.md
 M dev_memory/NEXT_TODO.md
 M docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md
 M docs/정기점검/수익률향상_누적대장.md
?? docs/신동거래/일일/신동_일일_MW0601_20260930.md
?? docs/신동거래/일일/신동_일일_MW0601_20260930.svg
?? docs/정기점검/매일점검/MW0601-20260930-점검리포트.md
?? docs/정기점검/매일점검/evidence_MW0601-20260930_intra.md
?? docs/정기점검/매일점검/evidence_MW0601-20260930_post.md
?? docs/정기점검/매일점검/evidence_MW0601-20260930_pre.md
```

**당일(2026-10-01) 커밋**
```
(당일 커밋 없음 — 커밋 가능 상태였음)
```

**최근 커밋 12건**
```
67cff42 [MW0601] 645차 후속: 장후 자동조치 — F-4 · G-1 · G-2 · F-1
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

_본문 미열람(설정): `20261001_HOGA.log` 1.4MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/16개 (중요도순). 제외: `retrain_intraday_20260819_101001.log`, `20261001_MICRO.log`, `20261001_DATA.log`, `20261001_PROBE.log`, `launcher_20261001_084001_30537.log`, `claude_resume_20261001.log`, `freeze_sentinel_20261001.log`, `force_flat_guard_20261001.log`_

### `logs/20261001_TRADE.log` — 167B · 2행 · 최종 08:41:04

- 형식 평문 · 시각 인식 2행 · INFO=2

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-01 08:40:59 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-01 08:41:04 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
  …
2026-10-01 08:40:59 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-01 08:41:04 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×2

**컴포넌트 상위 15** — `Position`×1, `ProfitGuard`×1

### `logs/20261001_WARN.log` — 3.7KB · 29행 · 최종 08:59:41

- 형식 평문 · 시각 인식 29행 · WARNING=29

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-01 08:41:07 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-10-01 08:41:07 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 15ms
2026-10-01 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 187ms account=333044256
2026-10-01 08:41:08 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-10-01 08:41:08 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-10-01 08:59:52 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 31.5ms | size=1955x1124 candles=15 grid=8.5 spans=0.0 candles=0.7 dir=0.0 regime=0.0 markers=0.0 axes=21.0 cross=0.0 | slow_cnt=3 total_cnt=5 overlay_cnt=4
2026-10-01 08:59:54 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 30.8ms | size=1955x1124 candles=15 grid=9.1 spans=0.0 candles=0.6 dir=0.0 regime=0.0 markers=0.0 axes=19.6 cross=0.0 | slow_cnt=4 total_cnt=6 overlay_cnt=6
2026-10-01 08:59:57 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 33.4ms | size=1955x1124 candles=15 grid=11.1 spans=0.0 candles=0.6 dir=0.0 regime=0.0 markers=0.0 axes=20.4 cross=0.0 | slow_cnt=5 total_cnt=7 overlay_cnt=13
2026-10-01 08:59:59 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 36.9ms | size=1955x1124 candles=15 grid=10.8 spans=0.0 candles=0.6 dir=0.0 regime=0.0 markers=0.0 axes=24.2 cross=0.0 | slow_cnt=6 total_cnt=10 overlay_cnt=18
2026-10-01 08:59:59 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 31.1ms | size=1955x1124 candles=15 grid=9.8 spans=0.0 candles=0.6 dir=0.0 regime=0.0 markers=0.0 axes=19.2 cross=0.0 | slow_cnt=7 total_cnt=11 overlay_cnt=18
```

</details>

**WARNING — 태그 6종 (상위 6)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 10 | 08:41:07 | 08:59:45 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `ChartDBG` | 7 | 08:59:41 | 08:59:59 | paintEvent slow 56.0ms | size=1955x1124 candles=15 grid=36.0 spans=0.4 candles=1.1 dir=0.0 regime=0.0 markers=0.4 axes=1.9 cross=0.0 | slow_cnt=1 total_cnt=1 overlay_cnt=0 |
| `SessionBackfill` | 6 | 08:41:38 | 08:41:38 | OHLCV 불일치 ts=2026-09-30 10:39:00 cols=['open'] existing_source=rt |
| `출처축` | 2 | 08:41:08 | 08:41:08 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |
| `SessionStateDrop` | 2 | 08:41:08 | 08:41:08 | 완료 마커 소실 ['p8_last_success_date', 'eod_retrain_ok_date'] — 날짜 전환(2026-09-30 → 2026-10-01)이 새 딕셔너리를 만들면서 이어받지 않았다 (호출부=session_recovery_service.py:increment_session). F-1 미적용 상태에서는 이것이 현재 동작이며, 이 줄의 출현 자체가 0907 리포트 이상점 1-4(판정 근거 정합성)의 확인 수단… |
| `OptionFlowChart` | 2 | 08:41:18 | 08:57:33 | 그리기 68.7ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 874x1001 |

**채널** — `SYSTEM`×29

**컴포넌트 상위 15** — `LiveDBG`×10, `ChartDBG`×7, `SessionBackfill`×6, `출처축`×2, `SessionStateDrop`×2, `OptionFlowChart`×2

### `logs/20261001_SYSTEM.log` — 27.7KB · 213행 · 최종 08:59:41

- 형식 평문 · 시각 인식 207행 · INFO=207, PLAIN=6

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-01 08:40:45 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=4436 | 행감지=30s all_threads=True
2026-10-01 08:40:45 [INFO] SYSTEM: [DBInit] 합계 0.47s | predictions=0.05s trades=0.23s daily_stats=0.01s shap=0.02s raw_data=0.12s broker_pnl=0.01s broker_recon=0.01s premarket_levels=0.03s
2026-10-01 08:40:45 [INFO] SYSTEM: [System] DB 초기화 완료 (0.5s)
2026-10-01 08:40:45 [INFO] SYSTEM: [System] 미륵이 초기화
2026-10-01 08:40:45 [INFO] SYSTEM: 미륵이 초기화
  …
2026-10-01 08:59:09 [INFO] SYSTEM: [CanaryShadow] ts=08:59 z경고=17개 (08:55 최종 4개 대비 +13) — 재측정만, 재적합 없음
2026-10-01 08:59:23 [INFO] SYSTEM: [TickUI] alive ticks=2267 code=A056A close=1078.66
2026-10-01 08:59:36 [INFO] SYSTEM: [CybosRT-TICK] #2300 code=A056A raw_time=85936 parsed=08:59:36 price=1078.30 vol=1 bid1=1078.34 ask1=1078.50 flag=50 side=SELL anchor=0/1
2026-10-01 08:59:41 [INFO] SYSTEM: [ChartDBG] 창 크기판정 OK S=1.40 minW=1075 minH=767 maxW=3034 avail=2560x1400 screen=\\.\DISPLAY2 win=1989x1303 canvas=1955x1124
2026-10-01 08:59:59 [INFO] SYSTEM: [CybosRT-TICK] #2400 code=A056A raw_time=85959 parsed=08:59:59 price=1076.18 vol=1 bid1=1076.18 ask1=1076.54 flag=50 side=SELL anchor=0/1
```

</details>

**채널** — `SYSTEM`×207

**컴포넌트 상위 15** — `CybosRT-TICK`×29, `CybosSub`×21, `System`×17, `TickUI`×15, `CybosRT-ROLLOVER`×14, `BAR-CLOSE`×14, `CVD-ANCHOR`×14, `SYSTEM`×9, `PreMarket`×9, `CybosRT-START`×6, `BrokerSync`×4, `BalanceUI`×4, `Notify`×4, `LEVELS 08:50`×4, `CybosInvestorRaw`×4

### `logs/20261001_SIGNAL.log` — 6.6KB · 54행 · 최종 08:59:00

- 형식 평문 · 시각 인식 54행 · WARNING=12, INFO=42

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-01 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.451
2026-10-01 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.429
2026-10-01 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.425
2026-10-01 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.434
2026-10-01 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.441
  …
2026-10-01 08:46:00 [INFO] SIGNAL: [MA-cont] 2026-10-01 연속 MA 버퍼 프라이밍 61봉 (버퍼 61)
2026-10-01 08:48:00 [INFO] SIGNAL: [ScalerRefresh] ts=— trigger=A_WARMUP pre_market_phase1_3bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.02s
2026-10-01 08:50:00 [INFO] SIGNAL: [ScalerRefresh] ts=— trigger=A_WARMUP pre_market_phase2_5bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.20s
2026-10-01 08:55:00 [INFO] SIGNAL: [ScalerRefresh] ts=— trigger=A_WARMUP pre_market_phase3_10bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.02s
2026-10-01 08:59:00 [INFO] SIGNAL: [ScalerRefresh] ts=— trigger=A_WARMUP pre_market_phase4_14bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.02s
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerRefresh` | 12 | 08:45:08 | 08:45:08 | 1m CORE 'cvd_divergence' raw_std≈0(0.0354) → identity(0,1) 강제 (FLAT 100% 방지) |

**채널** — `SIGNAL`×54

**컴포넌트 상위 15** — `ScalerFloor`×18, `ScalerRefresh`×17, `DynMC`×7, `Model`×6, `TimeRouter`×2, `EnsembleGater`×1, `FeatureBuilder`×1, `GapOffset`×1, `MA-cont`×1

### `logs/20261001_LEARNING.log` — 56.4KB · 311행 · 최종 08:59:00

- 형식 평문 · 시각 인식 311행 · WARNING=153, INFO=158

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-01 08:40:46 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-10-01 08:40:50 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00023 auc=0.498 out_max=0.2501 (기준 auc<0.53 and span<0.020, 기저율=0.2500 n=80) → 보정 미적용, raw 통과
2026-10-01 08:40:50 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00133 auc=0.314 out_max=0.1882 (기준 auc<0.53 and span<0.020, 기저율=0.1875 n=80) → 보정 미적용, raw 통과
2026-10-01 08:40:50 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00023 auc=0.451 out_max=0.3001 (기준 auc<0.53 and span<0.020, 기저율=0.3000 n=80) → 보정 미적용, raw 통과
2026-10-01 08:40:50 [INFO] LEARNING: [Calibration:30m] 축퇴 해소 — span=0.00291 auc=0.531 out_max=0.2765 (n=160) → 보정 재적용
  …
2026-10-01 08:48:00 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-10-01 08:50:00 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-10-01 08:55:00 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-10-01 08:55:08 [INFO] LEARNING: [MetaConf] 상태 복원 완료: meta_conf_state.pkl (fitted=[추세장, 횡보장, 급변장, 혼합], total=12231, ver=5)
2026-10-01 08:59:00 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
```

</details>

**WARNING — 태그 7종 (상위 7)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:1m` | 57 | 08:40:50 | 08:40:59 | 축퇴 감지 — span=0.00023 auc=0.498 out_max=0.2501 (기준 auc<0.53 and span<0.020, 기저율=0.2500 n=80) → 보정 미적용, raw 통과 |
| `Calibration:30m` | 44 | 08:40:50 | 08:40:58 | 축퇴 감지 — span=0.00133 auc=0.314 out_max=0.1882 (기준 auc<0.53 and span<0.020, 기저율=0.1875 n=80) → 보정 미적용, raw 통과 |
| `Calibration:3m` | 20 | 08:40:50 | 08:40:58 | 축퇴 감지 — span=0.00023 auc=0.451 out_max=0.3001 (기준 auc<0.53 and span<0.020, 기저율=0.3000 n=80) → 보정 미적용, raw 통과 |
| `Calibration:10m` | 12 | 08:40:50 | 08:40:57 | 축퇴 감지 — span=0.00066 auc=0.479 out_max=0.2628 (기준 auc<0.53 and span<0.020, 기저율=0.2625 n=80) → 보정 미적용, raw 통과 |
| `Calibration:5m` | 11 | 08:40:50 | 08:40:58 | 축퇴 감지 — span=0.00029 auc=0.518 out_max=0.3627 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과 |
| `Calibration:15m` | 8 | 08:40:50 | 08:40:59 | 축퇴 감지 — span=0.00191 auc=0.467 out_max=0.3884 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과 |
| `Calibration:ensemble` | 1 | 08:40:59 | 08:40:59 | 복원한 보정기가 축퇴 상태 — span=0.00282 auc=0.515 out_max=0.2963 (n=2072) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다. |

**채널** — `LEARNING`×311

**컴포넌트 상위 15** — `Calibration:1m`×113, `Calibration:30m`×88, `Calibration:3m`×38, `Calibration:10m`×22, `Calibration:5m`×21, `Calibration:15m`×14, `ScalerWarmup`×5, `ExtremityCorrector`×2, `Calibration:ensemble`×2, `Consolidator`×2, `RF`×1, `DriftAdjuster`×1, `SHAP`×1, `MetaConf`×1

### `logs/retrain_intraday_20260701_131001.log` — 4.6KB · 39행 · 최종 13:10:32

- 형식 평문 · 시각 인식 39행 · INFO=39

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-07-01 13:10:01,542 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-01 13:10:01,542 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-07-01 13:10:01,542 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-01 13:10:01,542 [INFO] RETRAIN_INTRADAY: 파라미터: force=False intraday=True result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_b5fe16cc.json
2026-07-01 13:10:02,960 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-07-01 13:10:32,209 [INFO] LEARNING: [Retrain] 30m 교체 (intraday — CV 없음 | fit=1.41s | old_acc=nan)
2026-07-01 13:10:32,213 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-07-01 13:10:32,214 [INFO] LEARNING: [Retrain] 완료 | 29.3초 | 성공=6/6 호라이즌
2026-07-01 13:10:32,215 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 30.7s 데이터=20000행
2026-07-01 13:10:32,217 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_b5fe16cc.json
```

</details>

**채널** — `LEARNING`×27, `RETRAIN_INTRADAY`×6, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×20, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `CUSUM`×1

### `logs/retrain_intraday_20260703_131001.log` — 4.6KB · 39행 · 최종 13:10:31

- 형식 평문 · 시각 인식 39행 · INFO=39

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-07-03 13:10:01,002 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-03 13:10:01,002 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-07-03 13:10:01,002 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-03 13:10:01,002 [INFO] RETRAIN_INTRADAY: 파라미터: force=False intraday=True result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_70667bac.json
2026-07-03 13:10:02,457 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-07-03 13:10:31,964 [INFO] LEARNING: [Retrain] 30m 교체 (intraday — CV 없음 | fit=1.42s | old_acc=nan)
2026-07-03 13:10:31,967 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-07-03 13:10:31,968 [INFO] LEARNING: [Retrain] 완료 | 29.5초 | 성공=6/6 호라이즌
2026-07-03 13:10:31,970 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 31.0s 데이터=20000행
2026-07-03 13:10:31,972 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_70667bac.json
```

</details>

**채널** — `LEARNING`×27, `RETRAIN_INTRADAY`×6, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×20, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `CUSUM`×1

### `logs/retrain_intraday_20260731_131001.log` — 4.5KB · 39행 · 최종 13:10:36

- 형식 평문 · 시각 인식 39행 · INFO=39

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-07-31 13:10:01,458 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-31 13:10:01,458 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-07-31 13:10:01,458 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-31 13:10:01,459 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_dbb6d0ae.json
2026-07-31 13:10:03,670 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-07-31 13:10:36,755 [INFO] LEARNING: [Retrain] 30m 교체 (intraday — CV 없음 | fit=1.36s | old_acc=0.3033)
2026-07-31 13:10:36,758 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-07-31 13:10:36,759 [INFO] LEARNING: [Retrain] 완료 | 33.1초 | 성공=6/6 호라이즌
2026-07-31 13:10:36,761 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 35.3s 데이터=20000행
2026-07-31 13:10:36,762 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_dbb6d0ae.json
```

</details>

**채널** — `LEARNING`×27, `RETRAIN_INTRADAY`×6, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×20, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `CUSUM`×1

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

### 메인 스레드 블로킹 2건 · 최대 4016ms · 5초 초과 0건

상위 — 4016ms, 3532ms

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20261001_WARN.log`
```
--- 메인 스레드 블로킹 ×2(표본)
08:41:11 2026-10-01 08:41:11 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4016ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=4016 band=INFO since_pipe_s=NA
08:59:45 2026-10-01 08:59:45 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3532ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3532 band=INFO since_pipe_s=NA
```

### `logs/20261001_SIGNAL.log`
```
--- 기동 복원 ×7(표본)
08:40:42 2026-10-01 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.451
08:40:42 2026-10-01 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.429
08:40:42 2026-10-01 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.425
08:40:42 2026-10-01 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.434
```

### `logs/20261001_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:50 2026-10-01 08:40:50 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00023 auc=0.498 out_max=0.2501 (기준 auc<0.53 and span<0.020, 기저율=0.2500 n=80) → 보정 미적용, raw 통과
08:40:50 2026-10-01 08:40:50 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00133 auc=0.314 out_max=0.1882 (기준 auc<0.53 and span<0.020, 기저율=0.1875 n=80) → 보정 미적용, raw 통과
08:40:50 2026-10-01 08:40:50 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00023 auc=0.451 out_max=0.3001 (기준 auc<0.53 and span<0.020, 기저율=0.3000 n=80) → 보정 미적용, raw 통과
08:40:50 2026-10-01 08:40:50 [INFO] LEARNING: [Calibration:30m] 축퇴 해소 — span=0.00291 auc=0.531 out_max=0.2765 (n=160) → 보정 재적용
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20261001_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:40:59 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:40 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261001_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 20 | 08:41:07 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 9 | 08:57:33 [WARNING] 그리기 99.4ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 752x1287 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 9 | 08:57:33 [WARNING] 그리기 99.4ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 752x1287 |

- 이 로그 생존구간: 08:41 ~ 08:59

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261001_SYSTEM.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 93 | 08:40:45 [INFO] 활성화 | file=logs\crash_fault.log PID=4436 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 101 | 08:49:01 [INFO] code=A056A from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 67 | 08:54:00 [INFO] code=A056A from=08:53 to=08:54 |

- 이 로그 생존구간: 08:40 ~ 08:59

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261001_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 50 | 08:45:08 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0354) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 3 | 08:50:00 [INFO] ts=— trigger=A_WARMUP pre_market_phase2_5bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elap… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 2 | 08:55:00 [INFO] ts=— trigger=A_WARMUP pre_market_phase3_10bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] ela… |

- 이 로그 생존구간: 08:40 ~ 08:59

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260930 | 15:47 | 로그 본문 |
| 20260929 | 15:47 | 로그 본문 |
| 20260928 | 15:47 | 로그 본문 |
| 20260926 | 16:50 | 로그 본문 |
| 20260924 | 10:58 | 로그 본문 |
| **중앙값** | **15:47** | 기준선 |
| **오늘 20261001** | **08:59** | 로그 본문 |

- 델타 **-408분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.3MB · 마지막 갱신 2026-09-30 17:45

최근 헤딩 8개:
```
## 2026-09-29 (MW0601 639ì°¨ â ì ë ê·ê²© v2 ê°ì : 1ì°¨ ëª©íê° ì§ì
## 2026-09-29 (MW0601 640ì°¨ â ì¥í ì ê²)
## 2026-09-29 (MW0601 641ì°¨ â ì¥í ìëì¡°ì¹: 637-2 crash_fault.log ë¤ì´í°ë¸ ì¤ë¥ ì§ê³ + 638-1 git ì¤í¨ ì§ë¨Â·ì´ì¤ ë°©ì´)
## 2026-09-30 (MW0601 642ì°¨ â ì¥ì  ì ê²)
## 2026-09-30 (MW0601 642ì°¨ íì â ì¥ì  ì ê² ëì¤ `.git/index.lock` ì¤ì¸¡ ë°ìÂ·íì)
## 2026-09-30 (MW0601 643ì°¨ â ì¥ì¤ ì ê²)
## 2026-09-30 (MW0601 644ì°¨ â ì¥í ì ê²)
## 2026-09-30 (MW0601 645ì°¨ â ì¥í ìëì¡°ì¹: F-4 ë½ ì£¼ì¸ ì§ë¨ Â· G-1 PreRetrain ì°í íì Â· G-2 git 1í ì¤ë
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
 íì¸: â ì±ê³µ â ì¤íµ / â ì ì ê²½ë¡ / â  ì¤í / ð´ ì°í ì¤í¨ / â ë¯¸ì¸¡ì (ë¡ê·¸ ìì)ã í ì¤ + ìë¬¸ ìµë 4ì¤(`â¦ ì¸ Nì¤`). ë¶ë¥ ë¬¸êµ¬ 5ì¢ì `main.py` ìë¬¸ê³¼ ëì¡°íë íì¤í¸ë¡ ê³ ì (ë¬¸êµ¬ê° ë°ëë©´ ì¡°ì©í ì£½ë ê²ì ë§ëë¤).
4. (G-2) `scripts/git_snapshot.py` ì ì¤ â `status --porcelain=v2 --branch` **1í**ë¡ ë¸ëì¹Â·HEADÂ·upstreamÂ·ìì¬/ë¤ì§Â·ë³ê²½ ìë¥¼ ë½ê³ , `--log N` ì +1í. í¸ì¶ ì í ë½ ì ë¬´ë¥¼ ë¹êµí´ ãì´ ì í¸ì´ ë½ì ë¨ê²¼ë¤ãë©´ rc=2. **ì íì  ëêµ¬** â SKILL.md Â§0-â¢ ì ãì´ê±¸ ì°ë¼ãë ê¶ê³  ì¶ê°ë ì¤í¬ ê°ì (ì ì¥ì ì ë³¸ + ì± ì ì¥ë³¸ ëì ìì )ì´ë¼ íì§ ììë¤ â NEXT_TODO 645-3.
5. (F-1) `dev_memory/_tmp_append_20260929.txt`Â·`_tmp_append_todo_20260929.txt` ì­ì (0ë°ì´í¸Â·ë¯¸ì¶ì  íì¸ í). ì»¤ë° ëì ìë.
6. íì§ ìì ê²: F-2(ë¬¸ì ì ëª© ë³µì â ë¦¬í¬í¸ê° ì¬ì©ì íë¨ì¼ë¡ ì§ì ), F-3(ë½ ë¶ì¤ë¬ê¸° â ì¬ì©ì ì ìì. ì°¸ê³ : Windows ìª½ ì¤ì¸¡ì `index.lock.stale_20260930*` 2ê°ë **ë³´ì´ì§ ìê³ ** `index.lock.stale.5`(09-28 08:59) 1ê°ë§ ë¨ì ìë¤), F-5(evidence_map.md ì¤í¤ë§ â ë¦¬í¬í¸ê° ãì¬ì©ì ì¹ì¸ íã ì§ì  â C), G-3(ì¸ì ì¢ë£ ì§ì  ìë ë½ì²´í¬ â SKILL.md ì ì°¨ ê°ì ì´ë¼ ì¬ì©ì íì¸ íì â ëê¸°. ëêµ¬ë `git_lock_diag.py --recheck` ë¡ ì¤ë¹ë¨).

**Why**: ê³ì¸¡ 4ìì¹ â¡(íë¡ì¸ì¤ ëª©ë¡ ë¯¸ì¸¡ì ì `None`, 0ê°ì êµ¬ë¶) Â· â£(ì°í ì±ê³µ ì¬ë¶ë¥¼ ë¤ì´ì ì¤í¸ì ê°ìí). íì /ì§ë¨ ë¶ë¦¬ë ãê°ì íì ì ë ê³³ì ì ì¼ë©´ íìª½ë§ ê³ ì³ì ¸ ê°ë¼ì§ë¤ã(483ì°¨ íì3) ìì¹ì ì°ì¥.

**How to apply**: ë½ì ë°ê²¬íë©´ `python scripts/git_lock_diag.py --recheck 30` â `ORPHAN` ì´ë©´ `git_lock_guard.py --reclaim` ëì, `HELD` ë©´ ëªë ¹ì¤ì git ì´ ë²ì¸ íë³´ì´ë ê¸°ë¤ë¦°ë¤, ì¬ê´ì¸¡ ìë©¸ì´ë©´ ê°ë 2 ë¡ ê¸°ë¡. ë¤ì ë½ ì¬í íë³¸ë¶í° ê°ëë³ë¡ ì¼ë¤(O-i1).

**ê²ì¦**: `tests/test_645_git_lock_diag_preretrain_snapshot.py` ì ê· + `test_483`Â·`test_523`Â·`test_641`Â·`test_620`Â·`test_631` íê·: 86 passed Â· 1 failed(`test_483` fuoption ì¬ë³¸ â ê¸°ì¡´ ì¤í¨, ì 2ë²). ì¤ë°ì´í°: `preretrain_bypass_lines(2026-09-30)` â ãâ ì°í íì¸ ì±ê³µ â ì¤íµã(ì¥ì  ë¦¬í¬í¸ ì íì ê³¼ ì¼ì¹), `git_snapshot.snapshot(log_n=2)` â git í¸ì¶ 2íÂ·ë¸ëì¹ v9-dev, ìì§ í `.git/index.lock` ìì.

```

</details>

### dev_memory/NEXT_TODO.md — 1.6MB · 마지막 갱신 2026-09-30 17:45

최근 헤딩 8개:
```
## 2026-09-29 (MW0601 638차 — 장중 점검)
## 2026-09-29 (MW0601 640차 — 장후 점검)
## 2026-09-29 (MW0601 641차 — 장후 자동조치)
## 2026-09-30 (MW0601 642차 — 장전 점검)
## 2026-09-30 (MW0601 642차 후속 — 장전 점검 도중 `.git/index.lock` 실측·회수)
## 2026-09-30 (MW0601 643차 — 장중 점검) 신규 항목
## 2026-09-30 (MW0601 644차 — 장후 점검)
## 2026-09-30 (MW0601 645차 — 장후 자동조치)
```

미완료 체크박스 **2910건** (끝에서 30건)
```
- [ ] **637-1 (P1)** `dev_memory/NEXT_TODO.md` 606-4(09-17 access violation 원인 조사 우선순위 결정)에 09-28(4건)·09-29(3건) 재현을 근거로 추가 — 사용자가 우선순위를 정할 때 참고. 전부 부팅 구간(정규장 개시 전) 한정, 정규장 개시 후 재현 0건. 새 조사 착수는 사용자 결정…
- [ ] **637-2 (P2, 신규)** `scripts/collect_evidence.py` §1 당일 파일 인벤토리·§11 자동 적신호가 `logs/crash_fault.log`(날짜 토큰 없는 누적 로그)를 구조적으로 못 본다 — `crash_fault_events()`(§9)는 "정상종료 기록" 판정용이지 "access violation 건수 …
- [ ] **633-1 (P2)** 사용자 확인 대기 유지 — `docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md` 제목 손상, 0929 장전에도 미확인·미커밋 상태 지속(3번째 날).
- [ ] **638-1 (P1, 신규)** `scripts/collect_evidence.py`의 `git diff`(미커밋 변경량 측정) subprocess 호출부 — 실패 시 정확한 명령·종료코드·stderr를 다이제스트에 로깅하도록 강화 + `GIT_OPTIONAL_LOCKS=0` 환경변수를 `--no-optional-locks` 플래그와 함께 이…
- [ ] **638-2 (사용자, 대기)** `.git/index.lock`(2026-09-29 12:27:19 생성) 판정보류 지속 중(12:32 기준 나이 338초, 임계 600초 미도달) — 600초 경과 후 사용자가 본인 컴퓨터에서 직접 `python scripts/git_lock_guard.py --check` 재실행, 스테일이면 `--recl…
- [ ] **606-4 (참고 보강)** 09-28 소급 access violation 4건 중 1건이 부팅 구간이 아니라 11:33경(장중)에도 발생했음을 추가 확인 — 조사 우선순위 결정은 여전히 사용자 몫.
- [ ] **633-1 (P2)** 사용자 확인 대기 유지 — `docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md` 제목 손상, 0929 장중에도 미확인·미커밋 지속(3번째 날, 변화 없음).
- [ ] **640-1** P5-17(5m 호라이즌 TIER1_EARLY→INITIAL_STOP 연쇄 손절 관찰) — 오늘 CASE4·5·8 3건/1거래일, 합계 −380,476원. 신규 채널(`horizon_5m_early_stop_watch` 가칭) 신설 여부는 사용자 판단 — 우선은 다음 장후들이 5m 호라이즌 진입 결과를 계속 케이스로 기록해 표…
- [ ] **640-3 (사용자, 참고)** 신동(별도 매매 모듈) v2 개정(639차, 별도 세션) — 내일(09-30) 자동 기동 시 라이브 반영 예정. 규격 준수 근거로 개정됐으나 과거 5거래일 재현에서는 v1(결함 버전)이 오히려 손실이 적었다는 상반된 실측 기록 있음 — 사용자가 `docs/신동거래/신동_개정_v2_1차목표역전_20260929.…
- [ ] **O-t1** 09-30 장전 부팅 구간 access violation 재현 여부(3일 연속 뒤 4일째 확인) — 606-4 우선순위 결정 참고자료 계속 축적.
- [ ] **O-t2** 09-30 장전 거래일 전환 시 SessionStateDrop 재현 여부 확인(근본원인 606-2 미해결로 재현 예상, 예상대로면 지속 기록만).
- [ ] **633-1 (P2)** 사용자 확인 대기 유지 — 문서 제목 손상, 0929 장후에도 미확인·미커밋 지속(4일째).
- [ ] **641-1 (G-2, 보류)** 부팅 구간 access violation 경고 **문턱** 신설 여부 — 관측일 3건(09-17·09-28·09-29)뿐이라 313차 가드 미통과. 지금 §11 은 문턱 없이 1건부터 건수만 올린다. 관측일이 더 쌓이면(예: 10거래일) 분포를 보고 문턱을 정할 것. 606-4(원인 조사 우선순위, 사용자 결…
- [ ] **642-1 (P2)** `dev_memory/_tmp_append_20260929.txt`·`_tmp_append_todo_20260929.txt` 정리 — 0바이트 미추적 스크래치 파일 2건 발견. 라이브 프로세스 미참조 재확인 후 삭제. 근거: 0930 장전 이상점 1-3.
- [ ] **642-2 (G-1, 고도화 제안)** `scripts/collect_evidence.py` §9에 `[PreRetrain]` "EOD 마커 파일 직접 확인" 우회 성공 여부를 자동 표시 — 현재는 로그 직접 grep 필요. 근거: 0930 장전 SessionStateDrop 재현 시 우회 확인에 수동 grep 소요.
- [ ] **633-1 (P2)** 사용자 확인 대기 유지 — 문서 제목 "재" 글자 손상, 0930 장전에도 미확인·미커밋 지속(**5일째**, 변화 없음).
- [ ] **642-3 (사용자, Windows 환경)** `.git/index.lock.stale_20260930001115_6` 삭제 — 이 세션(device_bash 리눅스 VM)에서는 `Operation not permitted`로 불가. 2026-08-21 `index.lock.stale_20260929033733_6`와 함께 정리 권장.
- [ ] **642-4 (조건부 고도화)** `git --no-optional-locks diff`가 오늘 실제로 `.git/index.lock`을 남긴 사례 확인(09-30 09:00:35 KST) — 다음에 같은 현상이 또 재현되면(장전·장중·장후 무관) G-1급 고도화로 "세션 종료 직전 `git_lock_guard.py --check` 자동 실행…
- [ ] **F-4** `scripts/git_lock_guard.py`·`scripts/collect_evidence.py:run_git()`에 진단 로깅 추가 — `.git/index.lock`이 `--no-optional-locks` 부착 상태에서도 생성될 때, 직전 실행된 git 하위명령을 특정할 수 있도록(`GIT_TRACE` 등). 근거: 2…
- [ ] **G-2** 점검 세션의 git 상태 확인을 `git status --porcelain=v2 --branch` 한 번으로 통합하는 헬퍼 제안 — `branch`·`status`·`log`를 연달아 실행하는 시점에 두 번 다 락이 발생한 공통점에서 착안. F-4로 원인 특정 후 설계.
- [ ] **O-i1** 다음 거래일(2026-10-01) 점검에서도 `.git/index.lock` 현상이 재현되는지 관찰 — 재현되면 "구조적 현상"으로 격상, 아니면 완화 검토.
- [ ] `.git/index.lock.stale_20260930033834_6` 삭제(Windows 환경에서만 가능, 코웍 세션은 EPERM으로 불가) — 장중 643차 회수 부스러기.
- [ ] **644-1 (F-4, P1로 상향)** `.git/index.lock`이 오늘 하루 세 번(장전·장중·장후) 재현됨. 장후는 STALE 없이 4분 만에 자연 소멸 — 앞의 두 번(둘 다 STALE→`--reclaim`)과 성격이 다름. `scripts/git_lock_guard.py`에 락 생성 전후 프로세스 스냅샷 진단 로깅 추가 검토. …
- [ ] **644-2 (G-3, 고도화 제안)** 점검 세션이 보고서를 다 쓰기 직전 `git_lock_guard.py --check`를 자동으로 한 번 더 실행해 결과를 보고서에 자동 기재하는 방안 — 642-4가 조건부 등록한 것을 오늘 재발 3회로 정식 승격. 근거: 0930 장후 제3부.
- [ ] **644-3 (F-5, P2)** `.claude/skills/mireuk-daily-check/references/evidence_map.md` §8의 DB 스키마 서술이 `v9-dev` 최신 실측과 어긋남 — `trades`에 `tp1_reached`·`exit_trigger`·`exit_outcome` 컬럼이 이미 있음(문서엔 없음), …
- [ ] **O-t1(10-01 판정)** P5-17(오후장 5m SHORT `TIER1_EARLY`→`INITIAL_STOP` 연쇄손절)이 09-29·09-30 이틀 연속 재현(5건/2거래일, 누계 -733,310원). 3일째도 재현되면 채널 신설(`horizon_5m_early_stop_watch`) 여부를 사용자에게 공식 상정. 근거: 0930 장…
- [ ] **645-1 (O-i1 보강)** 다음 `.git/index.lock` 재현 시 `python scripts/git_lock_diag.py --recheck 30` 결과(갈래 1/2)를 리포트에 기록 — 3건 이상 쌓이면 원인 가설 재검토.
- [ ] **645-2 (사용자/별도 세션, fuoption 저장소)** `fuoption/scripts/git_lock_guard.py` 사본을 정본(futures, 636차 `_sideline` 반영본)과 재통일 — `test_483::test_sibling_copy_matches_canonical` 이 636차 이후 계속 실패 중. 다른 저장소라 …
- [ ] **645-3 (사용자 확인, 스킬 개정)** SKILL.md §0-③·§7 에 ① 「상태 확인은 `scripts/git_snapshot.py` 한 번으로」 ② 「보고서 마무리 직전 `git_lock_diag.py --recheck 30` 실행 결과를 자동 기재」(G-3) 추가 여부 — 저장소 정본 + 앱 저장본 동시 수정 필요라 자동조치에서 …
- [ ] **644-3 / F-5 유지(C — 사용자 승인 대기)** evidence_map.md §8 스키마 갱신 — 리포트가 「사용자 승인 후 별도 세션」 지정.
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
점검 세션의 git 상태 확인을 `git status --porcelain=v2 --branch` 한 번으로 통합하는 헬퍼 제안 — `branch`·`status`·`log`를 연달아 실행하는 시점에 두 번 다 락이 발생한 공통점에서 착안. F-4로 원인 특정 후 설계.
- [ ] **O-i1** 다음 거래일(2026-10-01) 점검에서도 `.git/index.lock` 현상이 재현되는지 관찰 — 재현되면 "구조적 현상"으로 격상, 아니면 완화 검토.
- [ ] `.git/index.lock.stale_20260930033834_6` 삭제(Windows 환경에서만 가능, 코웍 세션은 EPERM으로 불가) — 장중 643차 회수 부스러기.

## 2026-09-30 (MW0601 644차 — 장후 점검)

- [x] **644-0(오늘 판정 완료)** 절대원칙 6종·EOD·P8·15:10 강제청산 전부 확인 — 상세는 0930 장후 리포트 「종합」 절 참조.
- [ ] **644-1 (F-4, P1로 상향)** `.git/index.lock`이 오늘 하루 세 번(장전·장중·장후) 재현됨. 장후는 STALE 없이 4분 만에 자연 소멸 — 앞의 두 번(둘 다 STALE→`--reclaim`)과 성격이 다름. `scripts/git_lock_guard.py`에 락 생성 전후 프로세스 스냅샷 진단 로깅 추가 검토. 근거: 0930 장후 이상점 1-5(갱신), 제2부.
- [ ] **644-2 (G-3, 고도화 제안)** 점검 세션이 보고서를 다 쓰기 직전 `git_lock_guard.py --check`를 자동으로 한 번 더 실행해 결과를 보고서에 자동 기재하는 방안 — 642-4가 조건부 등록한 것을 오늘 재발 3회로 정식 승격. 근거: 0930 장후 제3부.
- [ ] **644-3 (F-5, P2)** `.claude/skills/mireuk-daily-check/references/evidence_map.md` §8의 DB 스키마 서술이 `v9-dev` 최신 실측과 어긋남 — `trades`에 `tp1_reached`·`exit_trigger`·`exit_outcome` 컬럼이 이미 있음(문서엔 없음), `ensemble_decisions`는 60컬럼 실측(문서는 50컬럼+존재하지 않는 `min_conf_effective` 언급). 갱신 시 저장소 정본과 앱 저장 스킬 둘 다 수정 필요(SKILL.md 규약). 근거: 0930 장후 이상점 1-7.
- [ ] **O-t1(10-01 판정)** P5-17(오후장 5m SHORT `TIER1_EARLY`→`INITIAL_STOP` 연쇄손절)이 09-29·09-30 이틀 연속 재현(5건/2거래일, 누계 -733,310원). 3일째도 재현되면 채널 신설(`horizon_5m_early_stop_watch`) 여부를 사용자에게 공식 상정. 근거: 0930 장후 제4·5부.

## 2026-09-30 (MW0601 645차 — 장후 자동조치)

- [x] **644-1 / F-4 완료** — `scripts/git_lock_diag.py`(락 주인 진단 ORPHAN/HELD/… + `--recheck`) 신설, 수집기 §2 배선. 판정 정본 `git_lock_guard.py` 무변경.
- [x] **642-2 / G-1 완료** — 수집기 §9 「PreRetrain 우회 확인」 한 줄(`preretrain_bypass_lines`).
- [x] **643 G-2 완료(도구만)** — `scripts/git_snapshot.py`(git 1회 상태 스냅샷). 사용 권고 문구는 645-3.
- [x] **642-1 완료** — `dev_memory/_tmp_append_20260929*.txt` 0바이트 2건 삭제.
- [ ] **645-1 (O-i1 보강)** 다음 `.git/index.lock` 재현 시 `python scripts/git_lock_diag.py --recheck 30` 결과(갈래 1/2)를 리포트에 기록 — 3건 이상 쌓이면 원인 가설 재검토.
- [ ] **645-2 (사용자/별도 세션, fuoption 저장소)** `fuoption/scripts/git_lock_guard.py` 사본을 정본(futures, 636차 `_sideline` 반영본)과 재통일 — `test_483::test_sibling_copy_matches_canonical` 이 636차 이후 계속 실패 중. 다른 저장소라 자동조치 범위 밖.
- [ ] **645-3 (사용자 확인, 스킬 개정)** SKILL.md §0-③·§7 에 ① 「상태 확인은 `scripts/git_snapshot.py` 한 번으로」 ② 「보고서 마무리 직전 `git_lock_diag.py --recheck 30` 실행 결과를 자동 기재」(G-3) 추가 여부 — 저장소 정본 + 앱 저장본 동시 수정 필요라 자동조치에서 보류.
- [ ] **644-3 / F-5 유지(C — 사용자 승인 대기)** evidence_map.md §8 스키마 갱신 — 리포트가 「사용자 승인 후 별도 세션」 지정.

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

### `data/heartbeat_MW0601_20261001.json` — 244B · 10-01 08:59:39
```json
{
 "pid": 4436,
 "written_at": "2026-10-01T08:59:39",
 "beat_epoch": 1790812778.6329253,
 "beat_age_sec": 0.8,
 "watching": false,
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

- 파일 최종 기록: **10-01 08:46:00**

| 키 | 값 | 수집 대상일(2026-10-01)과 일치 |
|---|---|---|
| `date` | 2026-10-01 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

- **PreRetrain 우회 확인**: ✅ 우회 확인 **성공** → 스킵. session_state 마커는 비어 있었고 EOD 마커 파일로 메웠다(SessionStateDrop 재현, 실질 피해 없음)
  - `2026-10-01 08:55:09 [INFO] SYSTEM: [PreRetrain] EOD 마커 파일 직접 확인 (1일 전: 2026-09-30) → PreRetrain 스킵 (session_state 미기록 보완)`
  - `2026-10-01 08:55:09 [INFO] SYSTEM: [PreRetrain] 08:55 사전 재학습 스킵 — 1영업일 전(2026-09-30) EOD 재학습 성공 (동일 데이터 중복 불필요) | WarmupRetrain 예약 소진`

### `raw_candles` 절단선·결손 (618차)

(`raw_candles` 조회 실패 — **미측정**)


### 프로세스 종료 3축 대사 (620차)

| 축 | 상태 |
|---|---|
| 런처 로그(기동 PID·재시작 분류) | 측정됨 — 기동 1회 · 재시작 0회 |
| `crash_fault.log`(정상종료 기록) | 측정됨 — PID 1개 |
| `crash_fault.log`(`Windows fatal exception` — 살아남은 것 포함) | 측정됨 — **3건** |
| Windows WER(네이티브 예외) | **미측정** — 비Windows 플랫폼 — WER 이벤트 로그가 없다 |

- PID 4436: `Windows fatal exception` **3건** (access violation 3) — 직전 표식 시각 08:40:45 · 정규장(09:00) 이후 **0건**
  - 시각은 **발생 하한**이다(머리줄에 시각이 없다). 프로세스가 죽지 않은 오류이므로 위 종료 판정과 별개로 읽을 것. 스택은 `logs/crash_fault.log` 원문

| 미륵이 PID | 기동 | 정상종료 기록 | WER 네이티브 예외 | 판정 |
|---|---|---|---|---|
| 4436 | 08:40:45 | 없음 | 없음 | 판정불가 — WER **미측정** |


> 🔴 **「WER 기록 없음」을 「크래시가 아니다」로 읽지 말 것.** 참인 것은 **「미처리 네이티브 예외는 아니었다」까지**다 — `sys.exit`·창 닫기·`TerminateProcess`(하드킬)는 전부 이벤트를 안 남긴다. 종료 *의도*는 618차가 넣은 `[Shutdown] intent=` 줄과 함께 봐야 갈린다.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 181개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260930-점검리포트.md` | 96.5KB | 09-30 17:45 |
| `docs/정기점검/매일점검/evidence_MW0601-20260930_post.md` | 87.8KB | 09-30 16:18 |
| `docs/정기점검/매일점검/evidence_MW0601-20260930_intra.md` | 77.7KB | 09-30 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20260930_pre.md` | 62.7KB | 09-30 09:01 |
| `docs/정기점검/매일점검/evidence_MW0601-20260929_pre.md` | 59.0KB | 09-29 18:50 |
| `docs/정기점검/매일점검/evidence_MW0601-20260929_post.md` | 90.0KB | 09-29 18:50 |
| `docs/정기점검/매일점검/evidence_MW0601-20260929_intra.md` | 74.7KB | 09-29 18:50 |
| `docs/정기점검/매일점검/evidence_MW0601-20260928_pre.md` | 56.8KB | 09-29 18:50 |

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

1. `logs/20261001_LEARNING.log`: **축퇴** 8건(표본)
2. `logs/crash_fault.log`: `Windows fatal exception` **3건** (정규장 09:00 이후 0건) — 프로세스는 살아남았다. §9 「프로세스 종료 3축 대사」 아래 PID별 표를 볼 것 (641차 637-2)
3. 미커밋 변경 10건 (실질 4건 · 코드 0건 · EOL 파생 0건)

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20261001*.log` (Windows) / `grep 강제청산 logs/*20261001*.log`*