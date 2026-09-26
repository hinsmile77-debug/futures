# 미륵이 증거 다이제스트 — 2026-09-15 / PRE

- 생성 2026-09-15 09:00:53 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/zen-optimistic-bardeen/mnt/futures`
- 점검 범위: pre (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260915` · `2026-09-15` · `260915` · `0915`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **16개** 파일 · 16개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260915.log` | 124B | 09-15 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260915.log` | 139B | 09-15 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260915.json` | 243B | 09-15 09:00 |
| `launcher_{DATE}_084000_5416.log` | 1 | `logs/Mireuk_batch/launcher_20260915_084000_5416.log` | 57.7KB | 09-15 09:00 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260915.log` | 2.9KB | 09-15 08:41 |
| `{DATE}_DATA.log` | 1 | `logs/20260915_DATA.log` | 1.1KB | 09-15 09:00 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260915_DEBUG.log` | 623B | 09-15 09:00 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260915_HEALTH.log` | 0B | 09-15 08:40 |
| `{DATE}_HOGA.log` | 1 | `logs/20260915_HOGA.log` | 1.6MB | 09-15 09:00 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260915_LEARNING.log` | 56.2KB | 09-15 09:00 |
| `{DATE}_MICRO.log` | 1 | `logs/20260915_MICRO.log` | 37.0KB | 09-15 09:00 |
| `{DATE}_PROBE.log` | 1 | `logs/20260915_PROBE.log` | 1.7KB | 09-15 08:58 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260915_SIGNAL.log` | 18.7KB | 09-15 09:00 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260915_SYSTEM.log` | 29.7KB | 09-15 09:00 |
| `{DATE}_TRADE.log` | 1 | `logs/20260915_TRADE.log` | 167B | 09-15 08:41 |
| `{DATE}_WARN.log` | 1 | `logs/20260915_WARN.log` | 3.3KB | 09-15 09:00 |

## 2. 코드·커밋 상태

- HEAD `d1c17c8` · 브랜치 `v9-dev` · 미커밋 640건 · 실질 변경 **미측정**(git diff 실패) · 인덱스락 없음
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
```
M .claude/commands/dailycheck.md
 M .claude/skills/mireuk-daily-check/config_dailycheck_targets.json
 M .claude/skills/mireuk-daily-check/references/invariants.md
 M .claude/skills/mireuk-daily-check/references/phases.md
 M .claude/skills/mireuk-daily-check/references/postmortem.md
 M .claude/skills/mireuk-daily-check/references/report_template.md
 M .gitignore
 M CLAUDE.md
 M INSTALL.bat
 M LAUNCH_API.bat
 M MIREUK_DAILYCHECK_HANDOFF.md
 M ROADMAP.md
 M SETUP_GUIDE.md
 M TASK_CLAUDE_WAKE_INSTALL.bat
 M TASK_CLAUDE_WAKE_VERIFY.bat
 M backtest/param_optimizer.py
 M backtest/slippage_simulator.py
 M backtest/transaction_cost.py
 M backtest/walk_forward.py
 M challenger/challenger_engine.py
 M challenger/promotion_manager.py
 M challenger/variants/champion_tp1_skip_trail.py
 M collection/broker/base.py
 M collection/broker/cybos_broker.py
 M collection/broker/factory.py
 M collection/cybos/api_connector.py
 M collection/cybos/investor_data.py
 M collection/cybos/realtime_data.py
 M collection/kiwoom/api_connector.py
 M collection/kiwoom/investor_data.py
 M collection/macro/macro_fetcher.py
 M collection/macro/micro_regime.py
 M collection/options/pcr_store.py
 M collection/provenance.py
 M config/capital.py
 M config/constants.py
 M config/dailycheck_targets.json
 M config/krx_holidays.py
 M config/secrets_example.py
 M config/settings.py
… 외 600건
```

**당일(2026-09-15) 커밋**
```
(당일 커밋 없음 — 커밋 가능 상태였음)
```

**최근 커밋 12건**
```
d1c17c8 [MW0601] 580차: 잔고 배지 2행 고정높이 — 캔들차트 세로 확보 (표시 전용)
632207f [MW0601] 579차: 보유 중 레벨선 — 진입·하드스톱·TP1/2/3·트레일링 (표시 전용)
11e4c8c [MW0601] 578차: 진입단계 카드 상하 여백 제거 — 캔들차트 세로 추가 확보 (표시 전용)
cbe158a [MW0601] 577차: 호라이즌 스트립 1행화 + 진입단계 표 10행 고정 — 캔들차트 세로 확보 (표시 전용)
d595127 [MW0601] 576차: 좌측 중단 행을 **진짜 배너**로 옮김 + 공용 위젯화 (표시 전용)
34d53dd [MW0601] 575차 후속: 구현계획 부록 A-0 범위 정정 (배너 좌측 중단은 구현됨)
5479e79 [MW0601] 575차: 보조 모니터 배너 좌측 중단 — 상태·현재가·포지션 (표시 전용)
4d63137 [MW0601] 574차: 겹치는 우상단 요약 제거 + 문턱 설명을 레전드로 (표시 전용)
c3d9655 [MW0601] 573차: 히스토그램에 활성 문턱 띠 + 「당일 중앙값 대비」 라벨 (표시 전용)
118f23a [MW0601] 572차: 전환 지점 세로선 — 가격 영역과 전환 레인을 눈으로 잇는다 (표시 전용)
432b0aa [MW0601] 571차: 맥점 오버레이 P7 — 시안 대비 누락분 보완(전환 레인·원계열 2단·레전드·거래 면/칩) + 칩 충돌 공유 회피
4cd1419 [MW0601] 570차 후속: 「거래미륵」 토글이 마커를 못 끄던 결함 + 피터 입력 진입 동선 (표시 전용)
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

### 차단 게이트 전수 인벤토리 — 34개 중 **9개 꺼짐**

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
| `SIGNAL_DECAY_EXIT_ENABLED` | True | — |
| `SIZING_TARGET_CAPITAL_ENABLED` | True | — |
| `TP1_TICK_ENABLED` | True | — |
| `VOLATILITY_BURST_GUARD_ENABLED` | True | — |

## 4. 마커·리포트 · 로그 다이제스트

_본문 미열람(설정): `20260915_HOGA.log` 1.6MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/13개 (중요도순). 제외: `launcher_20260915_084000_5416.log`, `20260915_DEBUG.log`, `mainstall_traceback_20260915.log`, `freeze_sentinel_20260915.log`, `force_flat_guard_20260915.log`_

### `logs/20260915_TRADE.log` — 167B · 2행 · 최종 08:41:14

- 형식 평문 · 시각 인식 2행 · INFO=2

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-15 08:41:08 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-15 08:41:14 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
  …
2026-09-15 08:41:08 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-15 08:41:14 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×2

**컴포넌트 상위 15** — `Position`×1, `ProfitGuard`×1

### `logs/20260915_WARN.log` — 3.3KB · 29행 · 최종 09:00:04

- 형식 평문 · 시각 인식 29행 · WARNING=29

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-15 08:41:19 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-15 08:41:19 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 62ms
2026-09-15 08:41:19 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 172ms account=333044256
2026-09-15 08:41:21 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-09-15 08:41:21 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-09-15 09:01:01 [WARNING] SYSTEM: [CB⑤] 파이프라인 1241ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s]
2026-09-15 09:01:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2391ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2391 band=INFO since_pipe_s=0.1
2026-09-15 09:01:42 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 31.0ms | size=1886x916 candles=17 grid=15.0 spans=0.0 candles=16.0 dir=0.0 regime=0.0 markers=0.0 axes=0.0 cross=0.0 | slow_cnt=1 total_cnt=1
2026-09-15 09:01:46 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4547ms — 메인 스레드 블로킹 발생 | pipe_elapsed=41 watchdog_alerted=[] | [MainStall] stall_ms=4547 band=INFO since_pipe_s=44.3
2026-09-15 09:02:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2141ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2141 band=INFO since_pipe_s=0.1
```

</details>

**WARNING — 태그 9종 (상위 9)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 14 | 08:41:19 | 09:02:02 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `SessionBackfill` | 4 | 08:41:51 | 08:41:51 | OHLCV 불일치 ts=2026-09-14 10:51:00 cols=['open'] existing_source=rt |
| `출처축` | 2 | 08:41:21 | 08:41:21 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |
| `SessionStateDrop` | 2 | 08:41:21 | 08:41:21 | 완료 마커 소실 ['p8_last_success_date', 'eod_retrain_ok_date'] — 날짜 전환(2026-09-14 → 2026-09-15)이 새 딕셔너리를 만들면서 이어받지 않았다 (호출부=session_recovery_service.py:increment_session). F-1 미적용 상태에서는 이것이 현재 동작이며, 이 줄의 출현 자체가 0907 리포트 이상점 1-4(판정 근거 정합성)의 확인 수단… |
| `PipePerf` | 2 | 09:01:01 | 09:01:01 | total=1241ms | S0=2ms S1=64ms S2=10ms S3=0ms S4=97ms S5=945ms S6=88ms S7=29ms S8=7ms |
| `CB⑤` | 2 | 09:01:01 | 09:01:01 | 파이프라인 1241ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `MainStallTrace` | 1 | 08:41:25 | 08:41:25 | 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260915.log |
| `Health` | 1 | 09:01:01 | 09:01:01 | level=WARNING degraded=OFF | latency=1241ms | quality=0.86 | cache_age=98s | exceptions_10m=0 |
| `ChartDBG` | 1 | 09:01:42 | 09:01:42 | paintEvent slow 31.0ms | size=1886x916 candles=17 grid=15.0 spans=0.0 candles=16.0 dir=0.0 regime=0.0 markers=0.0 axes=0.0 cross=0.0 | slow_cnt=1 total_cnt=1 |

**채널** — `SYSTEM`×28, `HEALTH`×1

**컴포넌트 상위 15** — `LiveDBG`×14, `SessionBackfill`×4, `출처축`×2, `SessionStateDrop`×2, `PipePerf`×2, `CB⑤`×2, `MainStallTrace`×1, `Health`×1, `ChartDBG`×1

### `logs/20260915_SYSTEM.log` — 29.7KB · 256행 · 최종 09:00:51

- 형식 평문 · 시각 인식 249행 · INFO=249, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-15 08:40:34 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=24544 | 행감지=30s all_threads=True
2026-09-15 08:40:53 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-15 08:40:53 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-15 08:40:53 [INFO] SYSTEM: 미륵이 초기화
2026-09-15 08:40:53 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-09-14) 종가 버퍼 로드: 384봉
  …
2026-09-15 09:02:00 [INFO] SYSTEM: [CVD-ANCHOR] ts=09:01 vol=1156 | live_buy=753 shadow_buy=550 anchor_buy=550 | resid(anchor)=0 resid(shadow)=0 unknown_ticks=0 resets=0
2026-09-15 09:02:00 [INFO] SYSTEM: [IntradayRegime] NORMAL → CRASH | day=0.31% atr=1.00 z=7
2026-09-15 09:02:01 [INFO] SYSTEM: [S6Detail] ensemble=0ms checklist_pre=2ms meta_gate=7ms gates=0ms imp=0ms shap=1ms corr=0ms dash_ui=0ms tail=83ms
2026-09-15 09:02:01 [INFO] SYSTEM: [PipePerf][DBG] total=854ms | S0=2ms S1=105ms S2=6ms S3=0ms S4=114ms S5=512ms S6=96ms S7=14ms S8=5ms
2026-09-15 09:02:03 [INFO] SYSTEM: [CybosRT-TICK] #4700 code=A056A raw_time=90203 parsed=09:02:03 price=1042.30 vol=1 bid1=1042.20 ask1=1042.32 flag=50 side=SELL anchor=0/1
```

</details>

**채널** — `SYSTEM`×249

**컴포넌트 상위 15** — `CybosRT-TICK`×52, `CybosSub`×21, `System`×18, `TickUI`×17, `CybosRT-ROLLOVER`×17, `BAR-CLOSE`×17, `CVD-ANCHOR`×17, `SYSTEM`×9, `PreMarket`×9, `CybosRT-START`×6, `Notify`×5, `BrokerSync`×4, `BalanceUI`×4, `-`×4, `LEVELS 08:50`×4

### `logs/20260915_SIGNAL.log` — 18.7KB · 199행 · 최종 09:00:11

- 형식 평문 · 시각 인식 199행 · WARNING=139, INFO=60

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-15 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.409
2026-09-15 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.401
2026-09-15 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.397
2026-09-15 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.405
2026-09-15 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.419
  …
2026-09-15 09:02:01 [WARNING] SIGNAL: [ScalerFloor] 30m 'macro_krw_chg' scale=0.0855 → floor=0.10 적용 (z-score 폭발 방지)
2026-09-15 09:02:01 [WARNING] SIGNAL: [ScalerFloor] 30m 'macro_risk_on' scale=0.4386 → floor=0.50 적용 (z-score 폭발 방지)
2026-09-15 09:02:01 [WARNING] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0506 → floor=0.15 적용 (z-score 폭발 방지)
2026-09-15 09:02:01 [WARNING] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.0970 → floor=0.20 적용 (z-score 폭발 방지)
2026-09-15 09:02:01 [INFO] SIGNAL: [ScalerRefresh] ts=09:01 trigger=D_FORCE feat=quality_investor_reason_code repeat=2회 n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.03s
```

</details>

**WARNING — 태그 5종 (상위 5)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 60 | 09:00:02 | 09:02:01 | 1m 'macro_vix' scale=0.0340 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerRefresh` | 48 | 08:45:21 | 08:59:00 | 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ScalerMonitor` | 18 | 09:00:00 | 09:02:00 | ts=08:59 horizon=1m age=1m max_z=-13.03(institution_futures_net) extreme=1 adj=1 |
| `Model` | 12 | 09:00:00 | 09:00:00 | 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ConfFloorGuard` | 1 | 09:00:00 | 09:00:00 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4190 (conf_floor=0.330, min_conf=0.419, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×199

**컴포넌트 상위 15** — `ScalerFloor`×78, `ScalerRefresh`×55, `Model`×18, `ScalerMonitor`×18, `DynMC`×7, `SIGNAL`×6, `TimeRouter`×3, `ZeroDiag`×3, `DayRegimeShadow`×2, `AutoMasked`×2, `EnsembleGater`×1, `FeatureBuilder`×1, `GapOffset`×1, `MA-cont`×1, `ConfFloorGuard`×1

### `logs/20260915_LEARNING.log` — 56.2KB · 326행 · 최종 09:00:02

- 형식 평문 · 시각 인식 326행 · WARNING=155, INFO=171

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-15 08:40:55 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-15 08:40:58 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00152 auc=0.458 out_max=0.3632 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
2026-09-15 08:40:58 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00199 auc=0.409 out_max=0.3509 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과
2026-09-15 08:40:58 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00014 auc=0.532 out_max=0.2763 (n=105) → 보정 재적용
2026-09-15 08:40:58 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2763 < conf_floor=0.3300 (span=0.00014 auc=0.532 out_max=0.2763, 기저율=0.2762 n=105) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
  …
2026-09-15 09:01:01 [INFO] LEARNING: [SGD] 1건 학습 | SGD비중=30% 50분정확도=50.0%
2026-09-15 09:02:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0000% buf_n=2 nonzero=2 prev_p=1044.08 cur_p=1042.66
2026-09-15 09:02:00 [INFO] LEARNING: ✓ 1m 예측 적중 (conf=37.4% DN)
2026-09-15 09:02:01 [INFO] LEARNING: [SGD] 1건 학습 | SGD비중=30% 50분정확도=50.0%
2026-09-15 09:02:01 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=500 feat=97
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 155 | 08:40:58 | 08:41:08 | 축퇴 감지 — span=0.00152 auc=0.458 out_max=0.3632 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과 |

**채널** — `LEARNING`×326

**컴포넌트 상위 15** — `Calibration`×304, `ScalerWarmup`×7, `sigma`×3, `ExtremityCorrector`×2, `Consolidator`×2, `LEARNING`×2, `SGD`×2, `RF`×1, `DriftAdjuster`×1, `SHAP`×1, `MetaConf`×1

### `logs/20260915_MICRO.log` — 37.0KB · 115행 · 최종 09:00:51

- 형식 평문 · 시각 인식 115행 · DEBUG=115

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-15 08:45:22 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1041.00/4 ask1=1041.24/1 mp={'microprice_tick': 1041.192, 'midprice_tick': 1041.12, 'depth_bias_tick': -0.0901} mlofi_tick=None queue=None
2026-09-15 08:45:22 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1041.00/3 ask1=1041.24/1 mp={'microprice_tick': 1041.18, 'midprice_tick': 1041.12, 'depth_bias_tick': -0.1723} mlofi_tick=-1.0 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': 0.…
2026-09-15 08:45:22 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1041.00/3 ask1=1041.24/1 mp={'microprice_tick': 1041.18, 'midprice_tick': 1041.12, 'depth_bias_tick': -0.0491} mlofi_tick=-5.05 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
2026-09-15 08:45:22 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1041.00/2 ask1=1041.24/1 mp={'microprice_tick': 1041.16, 'midprice_tick': 1041.12, 'depth_bias_tick': -0.1487} mlofi_tick=-1.0 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': 0.…
2026-09-15 08:45:22 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1041.00/2 ask1=1041.24/1 mp={'microprice_tick': 1041.16, 'midprice_tick': 1041.12, 'depth_bias_tick': 0.0034} mlofi_tick=-4.4333 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
  …
2026-09-15 09:01:41 [DEBUG] MICRO: [MICRO-TICK] #7500 bid1=1043.20/2 ask1=1043.30/1 mp={'microprice_tick': 1043.2667, 'midprice_tick': 1043.25, 'depth_bias_tick': 0.1476} mlofi_tick=-3.4 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
2026-09-15 09:01:46 [DEBUG] MICRO: [MICRO-TICK] #7600 bid1=1042.88/1 ask1=1042.96/3 mp={'microprice_tick': 1042.9, 'midprice_tick': 1042.92, 'depth_bias_tick': -0.1848} mlofi_tick=-7.9167 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 2.0, 'bid_cancel_add_ratio…
2026-09-15 09:01:56 [DEBUG] MICRO: [MICRO-TICK] #7700 bid1=1042.36/1 ask1=1042.44/1 mp={'microprice_tick': 1042.4, 'midprice_tick': 1042.4, 'depth_bias_tick': -0.1234} mlofi_tick=5.85 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': 0…
2026-09-15 09:02:00 [DEBUG] MICRO: [MICRO-MINUTE] #17 ts=2026-09-15 09:01:00 close=1042.66 bias=0.001327 slope=1.685825 depth_bias=0.0632 mlofi_norm=-0.017028 mlofi_pressure=-1 mlofi_slope=132.668333 queue_signal=-0.0361 queue_ma=0.0124 queue_momentum=-0.0571 depletion=0.5000 refill=0.5000 imbalanc…
2026-09-15 09:02:03 [DEBUG] MICRO: [MICRO-TICK] #7800 bid1=1042.22/1 ask1=1042.30/1 mp={'microprice_tick': 1042.26, 'midprice_tick': 1042.26, 'depth_bias_tick': 0.0347} mlofi_tick=7.8 queue={'depletion_bid': -0.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -…
```

</details>

**채널** — `MICRO`×115

**컴포넌트 상위 15** — `MICRO-TICK`×98, `MICRO-MINUTE`×17

### `logs/20260915_DATA.log` — 1.1KB · 7행 · 최종 09:00:00

- 형식 평문 · 시각 인식 7행 · INFO=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-15 08:58:25 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=130466 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-09-15 08:58:25 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-09-15 08:58:56 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=130466 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-09-15 08:58:56 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-09-15 09:00:00 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
  …
2026-09-15 08:58:56 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=130466 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-09-15 08:58:56 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-09-15 09:00:00 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
2026-09-15 09:01:00 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
2026-09-15 09:02:00 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
```

</details>

**채널** — `DATA`×7

**컴포넌트 상위 15** — `CybosInvestor`×4, `DivergencePanel`×3

### `logs/20260915_PROBE.log` — 1.7KB · 11행 · 최종 08:58:56

- 형식 평문 · 시각 인식 11행 · WARNING=10, INFO=1

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-15 08:41:21 [INFO] PROBE: [CybosInvestorProbe] not implemented; extra_codes=['A056A']
2026-09-15 08:58:25 [WARNING] PROBE: [CybosProbe] CpSysDib.CpSvrNew7221 dispatch/request failed: (-2147221008, 'CoInitialize가 호출되지 않았습니다.', None, None)
2026-09-15 08:58:25 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-09-15 08:58:25 [WARNING] PROBE: [CybosProbe] CpSysDib.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-09-15 08:58:25 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrade dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
  …
2026-09-15 08:58:56 [WARNING] PROBE: [CybosProbe] CpSysDib.CpSvrNew7221 dispatch/request failed: (-2147221008, 'CoInitialize가 호출되지 않았습니다.', None, None)
2026-09-15 08:58:56 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-09-15 08:58:56 [WARNING] PROBE: [CybosProbe] CpSysDib.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-09-15 08:58:56 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrade dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-09-15 08:58:56 [WARNING] PROBE: [CybosProbe] CpSysDib.FutureTrade dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `CybosProbe` | 10 | 08:58:25 | 08:58:56 | CpSysDib.CpSvrNew7221 dispatch/request failed: (-2147221008, 'CoInitialize가 호출되지 않았습니다.', None, None) |

**채널** — `PROBE`×11

**컴포넌트 상위 15** — `CybosProbe`×10, `CybosInvestorProbe`×1

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

### 메인 스레드 블로킹 5건 · 최대 6047ms · 5초 초과 1건

상위 — 6047ms, 4719ms, 4547ms, 2391ms, 2141ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 08:41:25 | 6047ms | **미측정** | — |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260915_WARN.log`
```
--- Traceback ×1(표본)
08:41:25 2026-09-15 08:41:25 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260915.log
--- 메인 스레드 블로킹 ×5(표본)
08:41:25 2026-09-15 08:41:25 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 6047ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=6047 band=WARN since_pipe_s=NA
09:00:04 2026-09-15 09:00:04 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4719ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4719 band=INFO since_pipe_s=0.1
09:01:02 2026-09-15 09:01:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2391ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2391 band=INFO since_pipe_s=0.1
09:01:46 2026-09-15 09:01:46 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4547ms — 메인 스레드 블로킹 발생 | pipe_elapsed=41 watchdog_alerted=[] | [MainStall] stall_ms=4547 band=INFO since_pipe_s=44.3
```

### `logs/20260915_SYSTEM.log`
```
--- PSI ×1(표본)
09:00:00 2026-09-15 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.002 level=0 (heartbeat)
```

### `logs/20260915_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
09:00:00 2026-09-15 09:00:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4190 (conf_floor=0.330, min_conf=0.419, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- 기동 복원 ×7(표본)
08:40:31 2026-09-15 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.409
08:40:31 2026-09-15 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.401
08:40:31 2026-09-15 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.397
08:40:31 2026-09-15 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.405
```

### `logs/20260915_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:58 2026-09-15 08:40:58 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00152 auc=0.458 out_max=0.3632 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
08:40:58 2026-09-15 08:40:58 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00199 auc=0.409 out_max=0.3509 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과
08:40:58 2026-09-15 08:40:58 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00014 auc=0.532 out_max=0.2763 (n=105) → 보정 재적용
08:40:58 2026-09-15 08:40:58 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2763 < conf_floor=0.3300 (span=0.00014 auc=0.532 out_max=0.2763, 기저율=0.2762 n=105) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260915_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:08 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:41 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260915_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 19 | 08:41:19 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 9 | 09:00:04 [WARNING] _tick_header 간격 4719ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4719 band=… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 10 | 09:00:04 [WARNING] _tick_header 간격 4719ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4719 band=… |

- 이 로그 생존구간: 08:41 ~ 09:02

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260915_SYSTEM.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 92 | 08:40:34 [INFO] 활성화 | file=logs\crash_fault.log PID=24544 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 136 | 08:49:01 [INFO] code=A056A from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 110 | 08:54:00 [INFO] code=A056A from=08:53 to=08:54 |

- 이 로그 생존구간: 08:40 ~ 09:02

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260915_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 62 | 08:45:21 [WARNING] 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 87 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0320) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 123 | 08:55:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0308) → identity(0,1) 강제 (FLAT 100% 방지) |

- 이 로그 생존구간: 08:40 ~ 09:02

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260914 | 21:21 | 로그 본문 |
| 20260911 | 15:40 | 로그 본문 |
| 20260910 | 15:40 | 로그 본문 |
| 20260909 | 15:40 | 로그 본문 |
| 20260908 | 15:40 | 로그 본문 |
| **중앙값** | **15:40** | 기준선 |
| **오늘 20260915** | **09:02** | 로그 본문 |

- 델타 **-398분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.0MB · 마지막 갱신 2026-09-14 18:08

최근 헤딩 8개:
```
### 원인
### 증상 2 — ERR-FATAL 크래시로 자동진입 15분 정지 (P0)
### 증상 3 — `[Position] 진입` 로그 누락 (P1)
### 결정
### Why
### How to apply
### 검증
### 병행 세션
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
한
"(추정귀속) — Chejan 선행 체결 레이스 지문 가능성"(O-i1) 가설은 **기각**한다.
실제 원인은 TRADE 로그에서 `[Sizer]`→`[진입체크]`→`[Chejan] 상태=접수`로 바로
이어지고 그 사이 `[Position] 진입` 줄 자체가 안 찍힌 것 — 코드 추적은 다음
세션 과제.

### 결정

- F-1(P0, 승인 대기): EOD 데이터 풀 부족 조사 — `BackfillFilter` 마커 부여
  기준 확인, `MIN_TRAIN_BARS`/필터 범위 재설계 여부는 매매 정책 영향으로
  사용자 승인 필요(C등급). 코드 변경 없음(조사 계획만).
- F-2(P0, 저위험·즉시 적용 가능): `log_manager.signal()` 두 호출부(8671·8690)를
  `%` 연산자 사전 포맷으로 수정. 회귀 위험 낮음(로그 포맷만 변경). 이 세션은
  장후 규약상 코드를 변경하지 않았다 — 계획만 제시, 승인 시 다음 세션 적용.
- G-1(P2): `BackfillFilter` 마커 실제 범위를 CLAUDE.md·DECISION_LOG에 정확히
  문서화(F-1과 함께).
- 트레이드 `exit_stage='TRAIL_AFTER_TP1'` 오분류(오늘 1건 -183,558원)는 **함정①
  확인 결과 기존 결함(F-10/P5-06)의 반복**임을 확인 — 신규 이상점으로 올리지
  않고 누적대장(`docs/정기점검/수익률향상_누적대장.md`) P5-06 표본만 갱신
  (20건/6거래일, 누계 -14,707,793원).
- 1-1(`[SessionStateDrop]`)·O-p3는 오늘 원인이 다름(EOD 실패로 인한 결과이지
  기존 마커 소실 버그의 재현이 아님)을 확인 — "5거래일 연속 재현" 카운트에서
  오늘을 제외하고 다음 EOD 성공일 이후로 판정 이월.
- O-p1(수급 피처 표준편차 정상화)은 판정 보류로 전환 — 필터 자체는 정상
  작동했으나(1,446행 제외 확인) 재학습이 끝까지 완주하지 못해 결과 검증 불가.

### Why

- 계측 4원칙 ④(폴백 가시화) — `retrain_eod.py:396`의 오류 메시지("DB 데이터
  없음")가 실제 원인(필터 후 표본 부족)과 다른 일반 메시지라 원인 파악에
  시간이 걸렸다. F-1에 메시지 구체화를 포함.
- 함정①(이미 반영된 것 재상정 금지) — `exit_stage` 오분류를 신규로 올리지
  않기 위해 DECISION_LOG를 grep해 F-10/P5-06 선례를 먼저 확인했고,
  `ConstOut`↔`BiasReset` 사슬도 병행 세션 딥다이브가 이미 제안한 수정안을
  재상정하지 않고 관측(O-t1)으로만 이관했다.
- 병행 세션 확인(§0) — 장중 절 이후 추가 커밋 2건(561차 후속 포함)과 신규
  딥다이브 문서 1건을 확인·역링크(F-AE) 완료. 매매 정책 변경 없음을 각각
  확인했다.

### How to apply

- F-1·F-2 모두 이번 세션은 코드를 변경하지 않았다(장후 조사·계획만).
  승인 시 다음 세션에서 적용.

### 검증

- 09-01~09-11 8거래일 EOD 로그 전수 대조로 "오늘이 첫 발동"임을 확인.
- `raw_data.db` 직접 조회(79거래일·28,099행 마커 확인)로 `BackfillFilter`
  범위가 문서 서술보다 넓음을 실측 확인.
- `main.py` 전수에서 `log_manager.signal/system(` 호출부 4곳을 대조해 실제
  버그가 있는 곳(8671·8690)과 정상인 곳(14940·15953)을 구분.
- `ensemble_decisions`·`trades` 직접 조회로 O-i1(진입 출처)을 확정, 3원 대사
  로그 축 불일치(0=1=1)를 정확히 특정.

### 병행 세션

장중 절 이후 당일 커밋 2건 추가 확인(`fdbbf2a` 12:22:38, `67aeb88` 12:39:05 —
둘 다 561차 계열, 매매 정책 무변경 명시). 신규 딥다이브 문서 1건 확인·역링크
완료(`MW0601-20260914-3m호라이즌_ConstOut루프-딥다이브.md`, 13:56 최종수정,
아직 미커밋). `.git/index.lock` 없음(수집기 자가점검 확인). 읽기 전용 git은
전량 `--no-optional-locks`. 코드 변경 없음. DB 조회는 15:35 이후(장 마감 후)에만
읽기 전용으로 수행(라이브 DB 스캔 금지 규약 위반 아님).

산출물: `docs/정기점검/매일점검/MW0601-20260914-점검리포트.md`(장후 절 append —
0p-A~C·제3~7부·9p 종합), `docs/정기점검/매일점검/evidence_MW0601-20260914_post.md`
(수집기 자동 생성), `docs/정기점검/수익률향상_누적대장.md`(P5-06 갱신).
커밋 대기: 위 3개 파일 + `dev_memory/DECISION_LOG.md`·`NEXT_TODO.md`(경로 명시
add 필요 — `git add .` 금지, 630건 대부분 EOL 파생 혼입 주의).

```

</details>

### dev_memory/NEXT_TODO.md — 1.5MB · 마지막 갱신 2026-09-14 18:05

최근 헤딩 8개:
```
## 2026-09-11 (MW0601 557차 — 장전 점검)
## 2026-09-11 (MW0601 557차 후속 — 장중 점검)
## 2026-09-11 (MW0601 558차 후속 — 장후 자동조치)
### 이월·승인 대기 (자동조치 범위 밖 — 변경 없음)
### 다음 세션 관측
## 2026-09-14 (MW0601 560차 — 장전 점검)
## 2026-09-14 (MW0601 562차 — 장중 점검)
## 2026-09-14 (MW0601 563차 — 장후 점검, 종합 완성본)
```

미완료 체크박스 **2664건** (끝에서 30건)
```
- [ ] 신규 Fix/고도화 없음 — F-1·F-3·544-6·531-3은 기존 승인 대기 상태 유지
- [ ] 🔵 **558-2 (신규 · 선행 결함, 미조치)** `utils/db_utils.py` 에 모듈 레벨
- [ ] **558-3 (556-8 대장 추가)** `test_504_pnl_history_creon_tab` 2건
- [ ] **544-6 (이월 유지)** 수집기 `git diff` 재시도 — 오늘은 **재현되지 않았다**
- [ ] 🔴 **F-1** ProfitGuard Tier4 래치 「정정 가능한 재평가」 전환 — 승인 대기.
- [ ] 🔴 **F-3 (P0)** 장중 브로커 잔고 주기 재대사 — 승인 대기(우선순위 사용자 위임).
- [ ] 🔴 **556-4** `state_persist_enabled=False` 유지 여부 — 주간회의(실전 전환 기준 ②).
- [ ] **G-2** 외부 진입 감지 확장 — 536-2와 통합해 주간회의.
- [ ] **556-5** `DECISION_LOG` 555차·556차 본문 결손 소급 보완 여부.
- [ ] **556-7** `pytest tests/` 전체 수집 단계 사망 — 원인 모듈 특정 필요.
- [ ] **O-t8 (다음 재기동 시)** `broker_sync_recon` 에 행이 실제로 쌓이는지 —
- [ ] **O-t2′·O-t6·O-t7** (556차 후속 F-5·G-4·G-1 라이브 검증) — 변경 없이 유지.
- [ ] 🔴 **F-1 (538-4) 승인 재요청 (P1, 4거래일 연속 재현)** `[SessionStateDrop]` 완료
- [ ] 신규 Fix/고도화 없음 — 549-4(수집기 git diff 재시도)는 기존 승인·처리 대기 상태
- [ ] **O-p1 (오늘 장후 판정)** 2026-09-13(559차) 배포 `INVESTOR_UNIT_MISMATCH_EXCLUDE_ENABLED=True`가
- [ ] **O-p2 (장중~장후 판정)** `[ConfFloorGuard]` 09:00:00 1회 발동이 오늘 오실레이션으로
- [ ] **O-p3 (다음 거래일 09-15 장전 판정)** `[SessionStateDrop]` 5거래일 연속 재현 여부.
- [ ] 신규 Fix/고도화 없음 — 09:36 장중 재학습 실패는 병행 세션(`d9bdea6`)이 이미
- [ ] ↩️ **O-p1 전제 정정** — `INVESTOR_UNIT_MISMATCH_EXCLUDE_ENABLED` 소비 지점이
- [ ] **O-i1 (신규, 장후 판정)** 10:51:01 SHORT 2계약 진입이 `[Position] 진입`
- [ ] **1-4 (P2, 저우선)** 병합 커밋 `19c4076`에 PC명 태그(`[MW0601]`) 없음 —
- [ ] **O-p3 (변경 없음)** `[SessionStateDrop]` 5거래일 연속 재현 여부 — 다음
- [ ] 🔴 **F-1 (P0, 신규, 승인 대기) EOD 재학습 학습 데이터 풀 부족 조사·조치** —
- [ ] 🔴 **F-2 (P0, 신규, 저위험·즉시 적용 가능) `log_manager.signal()` printf
- [ ] **G-1 (P2, 신규)** `BackfillFilter`의 `feature_quality_score==0.3` 마커
- [ ] **O-t1 (다음 EOD 성공일 또는 F-1 승인 후 판정)** 병행 개발 세션의
- [ ] **O-t2 (F-1 조사 완료 시 판정)** `BackfillFilter` 마커가 광범위한 초기
- [ ] **O-t3 (다음 거래일 09-15 장후 판정)** 내일 EOD 재학습이 정상 완료되는지 —
- [ ] **1-8 (P1, 신규, 다음 세션 코드 추적)** `[Position] 진입` 로그 한 줄이
- [ ] P5-06(누적대장) 표본 갱신 — 오늘 1건 -183,558원 추가(20건/6거래일,
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
히는 정확한 조건 확인
      ② `MIN_TRAIN_BARS` 조정 또는 필터 범위 재정의 여부는 매매 정책 영향으로
      사용자 승인 필요(C등급). 근거: `docs/정기점검/매일점검/MW0601-20260914-점검리포트.md`
      이상점 1-5, `logs/retrain_eod_20260914.log`.
- [ ] 🔴 **F-2 (P0, 신규, 저위험·즉시 적용 가능) `log_manager.signal()` printf
      인자 오용 수정** — `main.py:8690`(P2 conf_floor 동적 하한 분기)이 오늘
      14:25:00 실제로 크래시해 자동진입이 15분간(14:25~14:41) 전면 정지됐다
      (`[ERR-FATAL] minute_pipeline: signal() takes from 2 to 3 positional
      arguments but 5 were given`). `logging_system/log_manager.py:175`의
      `signal(self, msg, level="INFO", **_kwargs)`가 `%`-스타일 다중 인자를
      지원하지 않는데 호출부가 4개 위치 인자를 그대로 넘겨 발생. 동일 패턴이
      `main.py:8671`(ColdStart 분기)에도 있음(오늘은 미발동, 조건 성립 시
      동일하게 크래시). 수정안: 두 호출부 모두 `%` 연산자로 사전 포맷팅한 단일
      문자열로 교체(다른 정상 호출부, 14940·15953행과 동일 패턴). 회귀 위험
      낮음(로그 포맷만 변경). 근거: 이상점 1-6·1-7, `logs/20260914_WARN.log`
      14:25:00.
- [ ] **G-1 (P2, 신규)** `BackfillFilter`의 `feature_quality_score==0.3` 마커
      부여 기준을 CLAUDE.md·DECISION_LOG에 정확히 문서화 — F-1 조사와 함께
      진행. 현재 문서는 "07-13 사고 25거래일"만 언급하나 실측은 79거래일을
      포함한다.
- [ ] **O-t1 (다음 EOD 성공일 또는 F-1 승인 후 판정)** 병행 개발 세션의
      `MW0601-20260914-3m호라이즌_ConstOut루프-딥다이브.md`가 제안한 P0-1
      (ConstOut 판정에서 BiasReset 구간 억제) 적용 여부와, 적용 시 CB③ 판정
      가용시간(오늘 47분/370분=13%) 개선 여부. 이 세션은 매매 정책 무변경만
      확인하고 신규 Fix로 재상정하지 않음(함정① 준수, 이미 그 문서에 제안돼 있음).
- [ ] **O-t2 (F-1 조사 완료 시 판정)** `BackfillFilter` 마커가 광범위한 초기
      백필 구간 전체를 가리키는 것으로 확정되면 `MIN_TRAIN_BARS`·필터 적용
      범위 재설계를 주간회의 안건으로 상정할지 결정.
- [ ] **O-t3 (다음 거래일 09-15 장후 판정)** 내일 EOD 재학습이 정상 완료되는지 —
      오늘과 같은 필터 조합이 다시 걸려 또 실패하면 P0 유지·우선순위 최상향.
- [ ] **1-8 (P1, 신규, 다음 세션 코드 추적)** `[Position] 진입` 로그 한 줄이
      10:51:01 진입에서 누락됨(`ensemble_decisions`·`trades`는 정상 일치 —
      3원 대사 중 로그 축만 불일치). Chejan 체결 흐름이 특정 순서로 들어올 때
      이 로그가 생략되는 코드 경로가 있는지 확인 필요.
- [x] O-p1 — 판정 보류로 전환(EOD 재학습 미완주로 표준편차 정상화 확인 불가).
      필터 자체는 오늘 밤 로더에서 실제로 작동해 1,446행 제외를 확인했으나
      재학습이 끝까지 완주하지 못해 결과 검증이 막혔다 — 다음 EOD 성공일로 이월.
- [x] O-p2 — 15:40 요약 로그(`ConfFloorGuard 도달가능 19분·도달불가 200분`)로
      최종 확인, 지속(종결) 유지.
- [x] O-p3 — 오늘은 EOD 실패라는 별도 원인 때문에 마커가 없음을 확인,
      "5거래일 연속 재현" 카운트에서 오늘을 제외하고 다음 거래일로 판정 이월.
- [x] O-i1 — `ensemble_decisions`(ts=10:50:00, entry_executed=1, entry_qty=2,
      meta_gate_horizon='3m', grade=C→A) + `trades`(entry_source='SYSTEM_AUTO')
      대조로 정상 엔진 진입 확정. 외부/유령 진입 아님 — Chejan 레이스 가설은
      기각(원인은 로그 라인 누락, 위 1-8로 별도 등록).
- [ ] P5-06(누적대장) 표본 갱신 — 오늘 1건 -183,558원 추가(20건/6거래일,
      누계 -14,707,793원). F-10 승인 여부 여전히 사용자 결정 대기.

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

### `data/heartbeat_MW0601_20260915.json` — 243B · 09-15 09:00:52
```json
{
 "pid": 24544,
 "written_at": "2026-09-15T09:01:52",
 "beat_epoch": 1789430511.9976606,
 "beat_age_sec": 0.8,
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

- 파일 최종 기록: **09-15 08:45:59**

| 키 | 값 | 수집 대상일(2026-09-15)과 일치 |
|---|---|---|
| `date` | 2026-09-15 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 136개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260914-3m호라이즌_ConstOut루프-딥다이브.md` | 28.7KB | 09-14 16:51 |
| `docs/정기점검/매일점검/MW0601-20260914-점검리포트.md` | 77.8KB | 09-14 16:29 |
| `docs/정기점검/매일점검/evidence_MW0601-20260914_post.md` | 77.8KB | 09-14 16:19 |
| `docs/정기점검/매일점검/evidence_MW0601-20260914_intra.md` | 65.8KB | 09-14 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20260914_pre.md` | 51.2KB | 09-14 09:01 |
| `docs/정기점검/매일점검/MW0601-20260911-점검리포트.md` | 70.1KB | 09-11 17:37 |
| `docs/정기점검/매일점검/evidence_MW0601-20260911_post.md` | 73.1KB | 09-11 16:19 |
| `docs/정기점검/매일점검/evidence_MW0601-20260911_intra.md` | 61.2KB | 09-11 12:29 |

### `docs/정기점검/금요일점검` — 60개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260913.json` | 3.0KB | 09-13 14:43 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260913.md` | 5.0KB | 09-13 14:43 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260911.json` | 2.9KB | 09-11 15:56 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260911.md` | 4.9KB | 09-11 15:56 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260911.json` | 38.8KB | 09-11 15:56 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260911.md` | 32.1KB | 09-11 15:56 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260911.json` | 115.4KB | 09-11 15:56 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260911.md` | 189.4KB | 09-11 15:56 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. `logs/20260915_WARN.log`: **Traceback** 출현 1건 — 크래시/메모리 계열
2. 메인 스레드 정지 5초 초과 **1건** (최대 6047ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
3. `logs/20260915_LEARNING.log`: **축퇴** 8건(표본)
4. 미커밋 변경 640건 — **실질 변경 미측정**(git diff 실패). 원시 건수만으로는 착시인지 알 수 없다

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260915*.log` (Windows) / `grep 강제청산 logs/*20260915*.log`*