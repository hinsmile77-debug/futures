# 미륵이 증거 다이제스트 — 2026-09-21 / INTRA

- 생성 2026-09-21 12:27:56 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/lucid-peaceful-pascal/mnt/futures`
- 점검 범위: pre, intra (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260921` · `2026-09-21` · `260921` · `0921`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **19개** 파일 · 19개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260921.log` | 124B | 09-21 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260921.log` | 140B | 09-21 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260921.json` | 244B | 09-21 12:27 |
| `launcher_{DATE}_084001_27124.log` | 1 | `logs/Mireuk_batch/launcher_20260921_084001_27124.log` | 4.2MB | 09-21 12:27 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260921.log` | 15.6KB | 09-21 12:22 |
| `retrain_intraday_20260701_{DATE}01.log` | 1 | `logs/retrain_intraday_20260701_092101.log` | 4.6KB | 07-01 09:21 |
| `retrain_intraday_{DATE}_100011.log` | 1 | `logs/retrain_intraday_20260921_100011.log` | 5.7KB | 09-21 10:00 |
| `retrain_intraday_{DATE}_121621.log` | 1 | `logs/retrain_intraday_20260921_121621.log` | 5.7KB | 09-21 12:17 |
| `{DATE}_DATA.log` | 1 | `logs/20260921_DATA.log` | 181.8KB | 09-21 12:27 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260921_DEBUG.log` | 126.4KB | 09-21 12:27 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260921_HEALTH.log` | 3.9KB | 09-21 12:23 |
| `{DATE}_HOGA.log` | 1 | `logs/20260921_HOGA.log` | 26.7MB | 09-21 12:27 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260921_LEARNING.log` | 400.1KB | 09-21 12:27 |
| `{DATE}_MICRO.log` | 1 | `logs/20260921_MICRO.log` | 536.8KB | 09-21 12:27 |
| `{DATE}_PROBE.log` | 1 | `logs/20260921_PROBE.log` | 113.3KB | 09-21 12:27 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260921_SIGNAL.log` | 299.7KB | 09-21 12:27 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260921_SYSTEM.log` | 451.4KB | 09-21 12:27 |
| `{DATE}_TRADE.log` | 1 | `logs/20260921_TRADE.log` | 2.4KB | 09-21 12:24 |
| `{DATE}_WARN.log` | 1 | `logs/20260921_WARN.log` | 3.4MB | 09-21 12:27 |

## 2. 코드·커밋 상태

- HEAD `850cfad` · 브랜치 `v9-dev` · 미커밋 714건 · 실질 변경 **미측정**(git diff 실패) · 인덱스락 없음
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
 M COLLECT_REGULAR_EOD.bat
 M INSTALL.bat
 M LAUNCH_API.bat
 M MIREUK_DAILYCHECK_HANDOFF.md
 M P7_SHADOW_EOD.bat
 M ROADMAP.md
 M SETUP_GUIDE.md
 M TASK_CLAUDE_WAKE_INSTALL.bat
 M TASK_CLAUDE_WAKE_VERIFY.bat
 M TASK_REGULAR_COLLECT_INSTALL.bat
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
… 외 674건
```

**당일(2026-09-21) 커밋**
```
850cfad [MW0601] 611차 후속: 보조 수집의 오류가 핵심 경로를 막았다 — settings 이름 오류 + 호출 배치
da2506d [MW0601] 611차: 개인은 위클리에서 거래하는데 우리는 먼스리를 보고 있었다 — 7222 위클리 수급 수집
45938ef [MW0601] 610차: 색으로만 나뉘던 경계에 선을 긋는다 — 가격모델 50%·80% 띠 (표시 전용)
1a16a15 [MW0601] 609차: 09:30 이 올라오면 08:50 이 사라졌다 — 두 스테이지를 함께 그린다 (표시 전용)
```

**최근 커밋 12건**
```
850cfad [MW0601] 611차 후속: 보조 수집의 오류가 핵심 경로를 막았다 — settings 이름 오류 + 호출 배치
da2506d [MW0601] 611차: 개인은 위클리에서 거래하는데 우리는 먼스리를 보고 있었다 — 7222 위클리 수급 수집
45938ef [MW0601] 610차: 색으로만 나뉘던 경계에 선을 긋는다 — 가격모델 50%·80% 띠 (표시 전용)
1a16a15 [MW0601] 609차: 09:30 이 올라오면 08:50 이 사라졌다 — 두 스테이지를 함께 그린다 (표시 전용)
3067c8b [MW0601] 608차 후속: P7 .bat 이 한글 주석 때문에 안 돌았다 — cmd 는 바이트 오프셋으로 읽는다
79b4664 [MW0601] 608차: P7 홀딩 섀도 사전등록 — 피터리에게서 가져온 게 아니라 그를 보다가 발견한 것
32eb908 [MW0601] 607차: 8월 사료 백필 — 월간 요약이 DB 가 아니라 코드에 박혀 있었다
0b2b36f [MW0601] 606차 후속2: 장후 자동조치 기록 — 제10부 + dev_memory
6c204d2 [MW0601] 606차 후속: 장후 자동조치 — G-3 + F-16 대행
e808409 [MW0601] 603차 후속2: .ps1/.bat BOM 을 정반대로 넣었다
5f4f94d [MW0601] 603차 후속: MW0602 수신 자동화 — 「푸시해두면 올라오나」의 답은 아니오다
5aa3138 [MW0601] 603차: 9월 초순 백필 — 그가 「맥점」이라 쓴 줄이 파서에 없었다
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

### 차단 게이트 전수 인벤토리 — 35개 중 **9개 꺼짐**

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
| `WEEKLY_OPTION_FLOW_ENABLED` | True | — |

## 4. 마커·리포트 · 로그 다이제스트

_본문 미열람(설정): `20260921_HOGA.log` 26.7MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/17개 (중요도순). 제외: `retrain_intraday_20260701_092101.log`, `20260921_MICRO.log`, `20260921_DATA.log`, `20260921_PROBE.log`, `launcher_20260921_084001_27124.log`, `20260921_DEBUG.log`, `mainstall_traceback_20260921.log`, `freeze_sentinel_20260921.log`_

### `logs/20260921_TRADE.log` — 2.4KB · 18행 · 최종 12:24:23

- 형식 평문 · 시각 인식 18행 · INFO=18

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-21 08:41:01 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-21 08:41:06 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-21 10:00:01 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-21 10:00:07 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-21 10:21:59 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
  …
2026-09-21 12:13:01 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,631,211) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-21 12:16:12 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-21 12:16:16 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-21 12:24:18 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-21 12:24:23 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×18

**컴포넌트 상위 15** — `Sizer`×7, `Position`×5, `ProfitGuard`×5, `Hurst 미계산 차단`×1

### `logs/20260921_WARN.log` — 3.4MB · 16555행 · 최종 12:27:55

- 형식 평문 · 시각 인식 16507행 · ERROR=1, WARNING=16506, PLAIN=48

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-21 08:41:09 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-21 08:41:09 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 15ms
2026-09-21 08:41:09 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 125ms account=333044256
2026-09-21 08:41:09 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-09-21 08:41:09 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-09-21 12:29:03 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 93.0ms | size=1886x916 candles=221 grid=31.0 spans=0.0 candles=15.0 dir=0.0 regime=0.0 markers=47.0 axes=0.0 cross=0.0 | slow_cnt=322 total_cnt=322
2026-09-21 12:29:03 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 78.0ms | size=1886x916 candles=221 grid=31.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=47.0 axes=0.0 cross=0.0 | slow_cnt=323 total_cnt=323
2026-09-21 12:29:04 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 125.0ms | size=1886x916 candles=221 grid=47.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=78.0 axes=0.0 cross=0.0 | slow_cnt=324 total_cnt=324
2026-09-21 12:29:04 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 94.0ms | size=1886x916 candles=221 grid=31.0 spans=0.0 candles=0.0 dir=0.0 regime=16.0 markers=47.0 axes=0.0 cross=0.0 | slow_cnt=325 total_cnt=325
2026-09-21 12:29:05 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 93.0ms | size=1886x916 candles=221 grid=47.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=46.0 axes=0.0 cross=0.0 | slow_cnt=326 total_cnt=326
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| ERROR | `LiveDBG` | 1 | 09:07:14 | 09:07:14 | _tick_header 간격 15531ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=15531 band=ALERT since_pipe_s=0.2 |

<details><summary>ERROR/LiveDBG 원문 1건</summary>

```
2026-09-21 09:07:14 [ERROR] SYSTEM: [LiveDBG] _tick_header 간격 15531ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=15531 band=ALERT since_pipe_s=0.2
```

</details>

**WARNING — 태그 15종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 16334 | 08:59:05 | 12:29:05 | paintEvent slow 63.0ms | size=1886x916 candles=15 grid=32.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=0.0 axes=31.0 cross=0.0 | slow_cnt=1 total_cnt=1 |
| `LiveDBG` | 77 | 08:41:09 | 12:26:20 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `ERR-DEGRADED` | 16 | 12:16:24 | 12:23:24 | investor_timer_fetch: name 'settings' is not defined |
| `Health` | 15 | 09:00:02 | 12:23:00 | level=WARNING degraded=OFF | latency=2169ms | quality=0.86 | cache_age=44s | exceptions_10m=0 |
| `출처축` | 10 | 08:41:09 | 12:24:26 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |
| `PipePerf` | 10 | 09:00:02 | 11:41:02 | total=2169ms | S0=3ms S1=33ms S2=1ms S3=0ms S4=152ms S5=753ms S6=1155ms S7=49ms S8=23ms |
| `CB⑤` | 10 | 09:00:02 | 11:41:03 | 파이프라인 2169ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `ScalerRefresh` | 7 | 09:05:00 | 12:01:00 | 5분 누적 수익률 +0.678% (임계 ±0.611%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `SessionBackfill` | 5 | 08:41:39 | 08:41:39 | OHLCV 불일치 ts=2026-09-18 09:45:00 cols=['open'] existing_source=rt |
| `MainStallTrace` | 5 | 09:00:06 | 12:22:09 | 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260921.log |
| `HealthPolicy` | 4 | 09:01:01 | 11:42:01 | Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=2169ms quality=0.86 cache=0s exc10m=0) | cause=S6(1155ms) |
| `RESTART` | 4 | 10:00:15 | 12:24:29 | 장중 재시작 감지 10:00 — GapOffset=복원됨  pre_market_scaler=False |

**채널** — `SYSTEM`×16492, `HEALTH`×15

**컴포넌트 상위 15** — `ChartDBG`×16334, `LiveDBG`×78, `-`×48, `ERR-DEGRADED`×16, `Health`×15, `출처축`×10, `PipePerf`×10, `CB⑤`×10, `ScalerRefresh`×7, `SessionBackfill`×5, `MainStallTrace`×5, `HealthPolicy`×4, `RESTART`×4, `LEVELS`×4, `Contrarian`×4

### `logs/20260921_SYSTEM.log` — 451.4KB · 3385행 · 최종 12:27:33

- 형식 평문 · 시각 인식 3370행 · INFO=3370, PLAIN=15

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-21 08:40:33 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=3604 | 행감지=30s all_threads=True
2026-09-21 08:40:50 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-21 08:40:50 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-21 08:40:50 [INFO] SYSTEM: 미륵이 초기화
2026-09-21 08:40:50 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-09-18) 종가 버퍼 로드: 384봉
  …
2026-09-21 12:29:00 [INFO] SYSTEM: [BAR-CLOSE][CYBOS] ts=12:28 O=1110.16 H=1110.38 L=1109.00 C=1109.20 V=305
2026-09-21 12:29:00 [INFO] SYSTEM: [CVD-ANCHOR] ts=12:28 vol=305 | live_buy=196 shadow_buy=97 anchor_buy=97 | resid(anchor)=0 resid(shadow)=0 unknown_ticks=0 resets=0
2026-09-21 12:29:00 [INFO] SYSTEM: [MicroRegime] 혼합 → 횡보장 (ADX=15.0, ATR=0.735, ratio=1.00, 근거=none, z=0)
2026-09-21 12:29:00 [INFO] SYSTEM: [S6Detail] ensemble=1ms checklist_pre=17ms meta_gate=7ms gates=0ms imp=0ms shap=1ms corr=0ms dash_ui=0ms tail=1ms
2026-09-21 12:29:00 [INFO] SYSTEM: [PipePerf][DBG] total=273ms | S0=2ms S1=26ms S2=0ms S3=0ms S4=58ms S5=142ms S6=29ms S7=12ms S8=3ms
```

</details>

**채널** — `SYSTEM`×3370

**컴포넌트 상위 15** — `CybosInvestorRaw`×830, `CybosRT-TICK`×601, `CybosRT-ROLLOVER`×220, `BAR-CLOSE`×220, `CVD-ANCHOR`×220, `TickUI`×219, `S6Detail`×206, `PipePerf`×206, `CybosSub`×105, `System`×84, `MicroRegime`×49, `RegimeFingerprint`×38, `CybosRT-START`×30, `OptionChain`×29, `SYSTEM`×25

### `logs/20260921_SIGNAL.log` — 299.7KB · 2694행 · 최종 12:27:01

- 형식 평문 · 시각 인식 2694행 · WARNING=967, INFO=1727

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-21 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.421
2026-09-21 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.409
2026-09-21 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.401
2026-09-21 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.397
2026-09-21 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.405
  …
2026-09-21 12:29:00 [WARNING] SIGNAL: [ScalerMonitor] ts=12:28 horizon=30m age=4m max_z=+4.63(toxicity_score) extreme=1 adj=1
2026-09-21 12:29:00 [INFO] SIGNAL: [FQAdj] fq=1.00 → min_conf 0.65→0.62 (완화)
2026-09-21 12:29:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=46.8% grade=X regime=NEUTRAL
2026-09-21 12:29:00 [INFO] SIGNAL: 앙상블: dir=+0 conf=46.8% grade=X micro=횡보장
2026-09-21 12:29:00 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: FLAT수렴 / conf미달(0.468<mc0.620) | 참고: 이상값피처(toxicity_score)
```

</details>

**WARNING — 태그 9종 (상위 9)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 570 | 09:00:02 | 12:25:01 | 1m 'macro_vix' scale=0.0412 → floor=0.10 적용 (z-score 폭발 방지) |
| `Model` | 132 | 09:00:00 | 12:25:01 | 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 115 | 09:00:00 | 12:29:00 | ts=08:59 horizon=1m age=1m max_z=+13.83(institution_futures_net) extreme=1 adj=1 |
| `Checklist` | 56 | 09:06:00 | 12:20:01 | 신뢰도 미달 36.7% < 37.9% → 강제 X등급 |
| `WeightCollapse` | 46 | 09:07:01 | 12:26:01 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ScalerRefresh` | 42 | 08:45:09 | 08:59:00 | 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ConstOut` | 3 | 11:01:00 | 12:13:01 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `MetaGate` | 2 | 09:44:00 | 10:13:00 | meta_conf 5회 연속 과소 → 다음 배치 재학습 대기 (streak=5) |
| `PCR-Dampen` | 1 | 09:12:01 | 09:12:01 | opt_pcr_* 피처 D_FORCE 발동 → 30분간 0.3× 감쇠 적용 |

**채널** — `SIGNAL`×2694

**컴포넌트 상위 15** — `ScalerFloor`×588, `SIGNAL`×412, `Ensemble`×208, `FQAdj`×203, `ZeroDiag`×196, `MetaGate`×193, `Model`×174, `ScalerMonitor`×115, `Checklist`×73, `ScalerRefresh`×68, `ATR-Horizon`×59, `MicroRegime`×49, `WeightCollapse`×46, `차단`×43, `DynMC`×41

### `logs/20260921_LEARNING.log` — 400.1KB · 2844행 · 최종 12:27:01

- 형식 평문 · 시각 인식 2844행 · WARNING=770, INFO=2074

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-21 08:40:52 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-21 08:40:52 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00104 auc=0.454 out_max=0.3630 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
2026-09-21 08:40:52 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00014 auc=0.514 out_max=0.2876 (기준 auc<0.53 and span<0.020, 기저율=0.2875 n=80) → 보정 미적용, raw 통과
2026-09-21 08:40:52 [INFO] LEARNING: [Calibration:3m] 축퇴 해소 — span=0.00030 auc=0.538 out_max=0.2708 (n=85) → 보정 재적용
2026-09-21 08:40:52 [WARNING] LEARNING: [Calibration:3m] 하한 도달불가 — out_max=0.2708 < conf_floor=0.3300 (span=0.00030 auc=0.538 out_max=0.2708, 기저율=0.2706 n=85) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
  …
2026-09-21 12:28:00 [INFO] LEARNING: [SGD] 2건 학습 | SGD비중=30% 50분정확도=50.0%
2026-09-21 12:29:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0000% buf_n=4 nonzero=4 prev_p=1110.12 cur_p=1109.20
2026-09-21 12:29:00 [INFO] LEARNING: ✗ 1m 예측 실패 (conf=45.2% 예측=FL 실제=DN)
2026-09-21 12:29:00 [INFO] LEARNING: ✗ 30m 예측 실패 (conf=36.9% 예측=FL 실제=UP)
2026-09-21 12:29:00 [INFO] LEARNING: [SGD] 2건 학습 | SGD비중=30% 50분정확도=50.0%
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:1m` | 276 | 08:40:52 | 12:24:18 | 축퇴 감지 — span=0.00163 auc=0.527 out_max=0.3610 (기준 auc<0.53 and span<0.020, 기저율=0.3600 n=150) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:30m` | 253 | 08:40:52 | 12:24:18 | 축퇴 감지 — span=0.00104 auc=0.454 out_max=0.3630 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과 |
| `Calibration:5m` | 79 | 08:40:52 | 12:24:18 | 축퇴 감지 — span=0.00116 auc=0.367 out_max=0.3379 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과 |
| `Calibration:10m` | 64 | 08:40:52 | 12:24:17 | 하한 도달불가 — out_max=0.3258 < conf_floor=0.3300 (span=0.00147 auc=0.600 out_max=0.3258, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:3m` | 55 | 08:40:52 | 12:24:16 | 축퇴 감지 — span=0.00014 auc=0.514 out_max=0.2876 (기준 auc<0.53 and span<0.020, 기저율=0.2875 n=80) → 보정 미적용, raw 통과 |
| `Calibration:15m` | 37 | 08:40:53 | 12:24:15 | 하한 도달불가 — out_max=0.3299 < conf_floor=0.3300 (span=0.00369 auc=0.582 out_max=0.3299, 기저율=0.3280 n=125) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:ensemble` | 5 | 08:41:01 | 12:24:18 | 복원한 보정기가 축퇴 상태 — span=0.00163 auc=0.497 out_max=0.3407 (n=1184) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다. |
| `Buffer-Timing` | 1 | 11:41:00 | 11:41:00 | total=386ms raw_fetch=3ms pred_select=3ms pred_update=21ms pred_insert=0ms verified=3 |

**채널** — `LEARNING`×2844

**컴포넌트 상위 15** — `LEARNING`×643, `Calibration:1m`×548, `Calibration:30m`×500, `SGD`×207, `sigma`×166, `Calibration:5m`×156, `Calibration:10m`×118, `Calibration:3m`×105, `Bias⚠`×93, `Calibration:15m`×74, `Bias`×70, `OnlineLearner`×37, `MetaConf`×34, `ScalerWarmup`×26, `ExtremityCorrector`×10

### `logs/20260921_HEALTH.log` — 3.9KB · 27행 · 최종 12:23:00

- 형식 평문 · 시각 인식 27행 · WARNING=15, INFO=12

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-21 09:00:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2169ms | quality=0.86 | cache_age=44s | exceptions_10m=0
2026-09-21 09:01:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1044ms | quality=0.86 | cache_age=103s | exceptions_10m=0
2026-09-21 09:02:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1085ms | quality=0.74 | cache_age=163s | exceptions_10m=0
2026-09-21 09:03:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=534ms | quality=0.94 | cache_age=39s | exceptions_10m=0
2026-09-21 09:07:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2728ms | quality=1.00 | cache_age=97s | exceptions_10m=0
  …
2026-09-21 12:04:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=282ms | quality=1.00 | cache_age=59s | exceptions_10m=0
2026-09-21 12:20:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=378ms | quality=1.00 | cache_age=52s | exceptions_10m=6 | exc_tags=[ERR-DEGRADED]×4 [LEVELS]×1 [RESTART]×1
2026-09-21 12:21:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=480ms | quality=1.00 | cache_age=113s | exceptions_10m=7 | exc_tags=[ERR-DEGRADED]×5 [LEVELS]×1 [RESTART]×1
2026-09-21 12:22:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=379ms | quality=1.00 | cache_age=172s | exceptions_10m=8 | exc_tags=[ERR-DEGRADED]×6 [LEVELS]×1 [RESTART]×1
2026-09-21 12:23:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=388ms | quality=1.00 | cache_age=48s | exceptions_10m=9 | exc_tags=[ERR-DEGRADED]×7 [LEVELS]×1 [RESTART]×1
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 15 | 09:00:02 | 12:23:00 | level=WARNING degraded=OFF | latency=2169ms | quality=0.86 | cache_age=44s | exceptions_10m=0 |

**채널** — `HEALTH`×27

**컴포넌트 상위 15** — `Health`×24, `HealthTrend`×3

### `logs/retrain_intraday_20260921_100011.log` — 5.7KB · 43행 · 최종 10:00:57

- 형식 평문 · 시각 인식 43행 · WARNING=2, INFO=41

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-21 10:00:11,923 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-21 10:00:11,924 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-09-21 10:00:11,924 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-21 10:00:11,924 [INFO] RETRAIN_INTRADAY: [DLL] BLAS 경로 이미 충족
2026-09-21 10:00:11,924 [INFO] RETRAIN_INTRADAY: 파라미터: force=False intraday=True horizons=ALL result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_d87c865f.json
  …
2026-09-21 10:00:57,308 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-09-21 10:00:57,309 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-09-21 10:00:57,310 [INFO] LEARNING: [Retrain] 완료 | 41.8초 | 성공=6/6 호라이즌
2026-09-21 10:00:57,311 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 45.4s 데이터=4800행
2026-09-21 10:00:57,313 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_d87c865f.json
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `BackfillFilter` | 1 | 10:00:25 | 10:00:25 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 26133/45621 제외 (418차 결정 1) — 남은 19488행 |
| `UnitMismatch` | 1 | 10:00:25 | 10:00:25 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/19488행 제외 (559차 P1'-2) — 남은 18042행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |

**채널** — `LEARNING`×28, `RETRAIN_INTRADAY`×7, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×21, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `DLL`×1, `BackfillFilter`×1, `UnitMismatch`×1, `CUSUM`×1

### `logs/retrain_intraday_20260921_121621.log` — 5.7KB · 43행 · 최종 12:17:06

- 형식 평문 · 시각 인식 43행 · WARNING=2, INFO=41

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-21 12:16:21,095 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-21 12:16:21,095 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-09-21 12:16:21,096 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-21 12:16:21,096 [INFO] RETRAIN_INTRADAY: [DLL] BLAS 경로 이미 충족
2026-09-21 12:16:21,096 [INFO] RETRAIN_INTRADAY: 파라미터: force=False intraday=True horizons=ALL result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_7d650730.json
  …
2026-09-21 12:17:06,738 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-09-21 12:17:06,738 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-09-21 12:17:06,739 [INFO] LEARNING: [Retrain] 완료 | 42.3초 | 성공=6/6 호라이즌
2026-09-21 12:17:06,740 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 45.6s 데이터=4800행
2026-09-21 12:17:06,741 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_7d650730.json
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `BackfillFilter` | 1 | 12:16:35 | 12:16:35 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 25997/45619 제외 (418차 결정 1) — 남은 19622행 |
| `UnitMismatch` | 1 | 12:16:35 | 12:16:35 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/19622행 제외 (559차 P1'-2) — 남은 18176행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |

**채널** — `LEARNING`×28, `RETRAIN_INTRADAY`×7, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×21, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `DLL`×1, `BackfillFilter`×1, `UnitMismatch`×1, `CUSUM`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 0 |
| 진입 등록(`[Position] 진입`) — **엔진** | 0 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 0 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 0 |
| 차단(`[차단]`) | 43 |
| 사이저 호출(`[Sizer]`) | 7 |

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **3계약**×7

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×7

### 차단 사유 43건 · 25종

| 건수 | 사유 |
|---|---|
| 14 | 등급X — 미통과 항목: 2_confidence |
| 2 | 등급X — 미통과 항목: 3_vwap, 6_foreign |
| 2 | ATR 0.92pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.83pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.71pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.69pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | 등급X — StartupWarmup 재가동 초기화 대기(약 2분 남음) |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar |
| 1 | Hurst 미계산 — 워밍업 중 자동진입 차단 (hurst=0.500) |
| 1 | Hurst 미계산 — 워밍업 중 (hurst=0.500) |
| 1 | ATR 0.85pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.93pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.94pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.99pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.96pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.91pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.80pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.73pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.84pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.66pt < 1.0pt — 변동성 부족 (휩쏘 위험) |

**체크리스트 미통과 항목 누적** — `2_confidence`×14, `3_vwap`×3, `6_foreign`×3, `4_cvd`×1, `5_ofi`×1, `7_prev_bar`×1

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### 메인 스레드 블로킹 29건 · 최대 15531ms · 5초 초과 5건

상위 — 15531ms, 10875ms, 9282ms, 6797ms, 6188ms, 4110ms, 3953ms, 3938ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:00:06 | 6797ms | 2169ms | **4628ms (68%)** |
| 09:07:14 | 15531ms | 2728ms | **12803ms (82%)** |
| 09:45:06 | 6188ms | 1000ms | **5188ms (84%)** |
| 09:55:11 | 10875ms | 836ms | **10039ms (92%)** |
| 12:22:09 | 9282ms | 480ms | **8802ms (95%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260921_WARN.log`
```
--- Traceback ×8(표본)
??:??:?? Traceback (most recent call last):
??:??:?? Traceback (most recent call last):
??:??:?? Traceback (most recent call last):
??:??:?? Traceback (most recent call last):
--- [SHAP] 슬로우 ×1(표본)
12:08:01 2026-09-21 12:08:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 927ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×8(표본)
08:41:12 2026-09-21 08:41:12 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3453ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3453 band=INFO since_pipe_s=NA
08:59:08 2026-09-21 08:59:08 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3031ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3031 band=INFO since_pipe_s=NA
09:00:06 2026-09-21 09:00:06 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 6797ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=6797 band=WARN since_pipe_s=0.2
09:01:02 2026-09-21 09:01:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2297ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2297 band=INFO since_pipe_s=0.2
```

### `logs/20260921_SYSTEM.log`
```
--- ConstOut ×5(표본)
10:01:00 2026-09-21 10:01:00 [INFO] SYSTEM: [DynMC] ConstOut 고착 conf 제외: [0.34] → 386건 제거 (잔여 1858건)
11:01:00 2026-09-21 11:01:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3846) | 앙상블 제외는 유지
11:10:00 2026-09-21 11:10:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3749) | 앙상블 제외는 유지
12:13:01 2026-09-21 12:13:01 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4274) | 앙상블 제외는 유지
--- PSI ×8(표본)
09:00:00 2026-09-21 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:05:00 2026-09-21 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:11:00 2026-09-21 09:11:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:17:00 2026-09-21 09:17:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
```

### `logs/20260921_SIGNAL.log`
```
--- ConstOut ×8(표본)
09:44:00 2026-09-21 09:44:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=- raw=STUCK | live(range=0.0150 dir=+1) raw(range=0.0010 dir=+1)
09:45:01 2026-09-21 09:45:01 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=- raw=STUCK | live(range=0.0190 dir=+1) raw(range=0.0010 dir=+1)
11:01:00 2026-09-21 11:01:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.0100 dir=+0)
11:01:00 2026-09-21 11:01:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
--- WeightCollapse ×8(표본)
09:07:01 2026-09-21 09:07:01 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
09:10:00 2026-09-21 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=84.4% grade=X regime=RISK_ON [WeightCollapse]
09:13:00 2026-09-21 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
09:16:00 2026-09-21 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
--- 기동 복원 ×8(표본)
08:40:30 2026-09-21 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.421
08:40:30 2026-09-21 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.409
08:40:30 2026-09-21 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.401
08:40:30 2026-09-21 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.397
--- 안전망 ×8(표본)
09:07:01 2026-09-21 09:07:01 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-09-21 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-09-21 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-09-21 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20260921_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:52 2026-09-21 08:40:52 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00104 auc=0.454 out_max=0.3630 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
08:40:52 2026-09-21 08:40:52 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00014 auc=0.514 out_max=0.2876 (기준 auc<0.53 and span<0.020, 기저율=0.2875 n=80) → 보정 미적용, raw 통과
08:40:52 2026-09-21 08:40:52 [INFO] LEARNING: [Calibration:3m] 축퇴 해소 — span=0.00030 auc=0.538 out_max=0.2708 (n=85) → 보정 재적용
08:40:52 2026-09-21 08:40:52 [WARNING] LEARNING: [Calibration:3m] 하한 도달불가 — out_max=0.2708 < conf_floor=0.3300 (span=0.00030 auc=0.538 out_max=0.2708, 기저율=0.2706 n=85) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260921_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:01 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 10:00 | 장중 초반 | 2 | 10:00:01 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:41 ~ 12:24

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260921_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 16 | 08:41:09 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 367 | 08:59:05 [WARNING] paintEvent slow 63.0ms | size=1886x916 candles=15 grid=32.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 674 | 08:59:05 [WARNING] paintEvent slow 63.0ms | size=1886x916 candles=15 grid=32.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=… |
| 10:00 | 장중 초반 | 1247 | 09:54:01 [WARNING] paintEvent slow 78.0ms | size=1886x916 candles=70 grid=47.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=… |
| 12:00 | 장중 중간점 | 665 | 11:54:01 [WARNING] paintEvent slow 93.0ms | size=1886x1167 candles=188 grid=31.0 spans=0.0 candles=16.0 dir=0.0 regime=0.0 marke… |

- 이 로그 생존구간: 08:41 ~ 12:29

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260921_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 91 | 08:40:33 [INFO] 활성화 | file=logs\crash_fault.log PID=3604 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 134 | 08:49:00 [INFO] code=A056A from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 200 | 08:54:00 [INFO] code=A056A from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 269 | 09:54:00 [INFO] code=A056A from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 158 | 11:54:00 [INFO] code=A056A from=11:53 to=11:54 |
| 14:00 | _장중 후반 · 장중 재학습 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 12:29

**매분 루프 커버리지 09:00~15:10: 210/371분 (56.6%)**

연속 3분 이상 기록 없는 구간 1개:

| 시작 | 끝 | 분 |
|---|---|---|
| 12:30 | 15:10 | 161 |

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260921_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 56 | 08:45:09 [WARNING] 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 95 | 08:50:02 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0413) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 225 | 08:55:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0403) → identity(0,1) 강제 (FLAT 100% 방지) |
| 10:00 | 장중 초반 | 151 | 09:54:00 [WARNING] 신뢰도 미달 31.9% < 37.9% → 강제 X등급 |
| 12:00 | 장중 중간점 | 135 | 11:54:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m', '5m'] 중 미배포=['10m', '15m', '3m', '5m'] → flat_score=1.0 안전망 발동 (ac… |

- 이 로그 생존구간: 08:40 ~ 12:29

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260920 | 18:39 | 로그 본문 |
| 20260918 | 15:47 | 로그 본문 |
| 20260917 | 20:33 | 로그 본문 |
| 20260916 | 17:21 | 로그 본문 |
| 20260915 | 17:41 | 로그 본문 |
| **중앙값** | **17:41** | 기준선 |
| **오늘 20260921** | **12:29** | 로그 본문 |

- 델타 **-312분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.1MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-21 (MW0601 609차 — 장전 점검)
### 0. 브랜치·환경·설정 불변식 — 전부 정상
### 1. 신규 발견 — `SessionStateDrop`(F-1/538-4)이 이번엔 비거래일(9/20 일요일)에 재현됐다
### 2. 미커밋 707건 재확인 — 실질 변경은 3파일뿐, 나머지는 EOL 착시
### 3. `PHANTOM_STATE_ARTIFACT`·`ChartDBG paintEvent slow` — 확인 결과 둘 다 기존 등록 사안
### 자가유발 여부
### 4. 후속 — 이 점검 세션 자신이 `.git/index.lock`을 남겼다 (사용자 조치 1번으로 격상)
### 자가 점검 (갱신)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
 계열 재현 관측은 해당 거래일 로그만이 아니라 **직전
비거래일(주말·공휴일) 로그까지 포함**해 확인할 것. `session_recovery_service.py`의
`increment_session()`은 프로세스가 뜨는 모든 시점(거래일 여부 무관)에 실행되므로
결함 자체도 거래일에 국한되지 않는다.

**검증**: `grep -n "SessionStateDrop" logs/20260921_*.log` → 0건(전체 로그 8종
확인) / `grep -n "SessionStateDrop" logs/20260920_*.log` → 2건 확인(14:09:42).
`data/session_state.json` 직접 열람으로 마커 키 부재 재확인.

### 2. 미커밋 707건 재확인 — 실질 변경은 3파일뿐, 나머지는 EOL 착시

**증상**: `git status --short` 707건 표시, `collect_evidence.py` 자체 실행은
"실질 변경 미측정(git diff 실패)"으로 판정 보류했다(수집기 자체의 git diff 호출이
이번 실행에서 실패 — 원인 미상, P2 후보).

**결정**: 세션이 직접 `git --no-optional-locks diff --numstat -w`(줄바꿈 무시)로
재확인 — 실질 변경은 `features/levels/levels_store.py`(+69/-1) ·
`features/levels/premarket_levels.py`(+24/-7) · `scripts/cybos_autologin.py`(+33/-14)
3개뿐이고, 이는 606-3(09-18)에 이미 "타 세션 작업 중"으로 등록된 바로 그 3파일과
정확히 일치한다. 나머지 604건(이번엔 -w 적용 시 diff 자체가 0건으로 사라짐)은
전부 CRLF/LF 파생.

**Why**: 함정① 재확인 — 이미 등록된 사안을 새로 발견한 양 올리지 않기 위해
파일명까지 대조했다.

**검증**: `git diff --stat -w` 결과 3파일·126줄 변경만 출력, 그 외 0건.

### 3. `PHANTOM_STATE_ARTIFACT`·`ChartDBG paintEvent slow` — 확인 결과 둘 다 기존 등록 사안

`[출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT']`(08:41:09, 2건)은
554차에 이미 "테스트가 심은 상태파일 흔적, 거래 아님, 성과 집계 제외"로 분류된
라벨이다(`config/constants.py:249`, DECISION_LOG 43271행 부근에 "기존 등록,
신규 아님" 기록 확인). `[ChartDBG] paintEvent slow`(09:00~09:02 386건)는
`NEXT_TODO.md`의 F-1p(P1, 3일째 증가 추세)로 이미 추적 중 — 오늘 3분간 386건은
최근 며칠 하루 3만~4만 건대에 비해 오히려 적은 수준.

### 자가유발 여부

이 세션은 라이브 DB를 조회하지 않았다(수집기는 로그·설정·git 전용). 코드 변경
없음. 커밋 없음(장전 규칙). `.git/index.lock` 신규 생성 없음(작업 종료 시 재확인).

### 4. 후속 — 이 점검 세션 자신이 `.git/index.lock`을 남겼다 (사용자 조치 1번으로 격상)

**증상**: 위 항목들을 정리하던 도중 09:01:49에 `.git/index.lock`(0바이트)이 생긴 것을
뒤늦게 발견했다. 이 세션은 처음부터 끝까지 `--no-optional-locks`를 붙였는데도 생겼다.

**결정**: `git_lock_guard.py --check` → `STALE`(exit=2) 확정. `--reclaim` 시도 →
`Operation not permitted`로 실패(리눅스 샌드박스 마운트 `unlink` EPERM — SKILL.md
§0에 이미 문서화된 바로 그 제약). 리포트 최상단 헤더 + 1-1(P1) + 사용자 조치 1번으로
승격해 기록했다.

**Why**: 어느 명령이 만들었는지는 특정하지 못했다(전부 `--no-optional-locks` 사용
확인했음에도 발생) — 향후 이런 사례가 반복되면 "옵션을 붙여도 100% 방지되지 않는다"는
쪽으로 SKILL.md §0 문구를 재검토할 근거가 된다. 이번엔 원인 규명보다 **STALE 확정 +
회수 안내**를 정확히 남기는 것을 우선했다(사용자가 안전하게 지울 수 있도록).

**검증**: `python scripts/git_lock_guard.py --check` 종료코드 2 재확인, 세션 종료
직전에도 락 존재 재확인(아래 자가점검 갱신).

### 자가 점검 (갱신)

읽기 전용 git 전량 `--no-optional-locks` 사용(그럼에도 락 발생 — 위 4번 참조) ·
`git add`/커밋 미실행 · `dev`/`main` 미접촉 · 작업 종료 시 `.git/index.lock` **존재함**
(STALE 확정, 사용자 조치 1번으로 리포트 최상단에 반영). 리포트는 신규 생성(장전 첫
파일) — append 규약 위반 없음.

```

</details>

### dev_memory/NEXT_TODO.md — 1.5MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 2026-09-18 606차 장후 — 신규 3건 + 이월 항목 판정 완료
## 2026-09-18 (MW0601 606차 후속 — 장후 자동조치)
### C등급 — 자동조치가 손대지 않는다 (사용자 결정 필요)
### 신규 — 606차 후속이 발견 (오늘 거래와 무관)
### 완료 (606차 후속이 닫음)
## 2026-09-21 (MW0601 609차 — 장전 점검)
### 신규 등록
### 확인 완료 (609차가 재확인, 신규 아님)
```

미완료 체크박스 **2785건** (끝에서 30건)
```
- [ ] **A-1 (P1, 신규)** `tests/test_dashboard_smoke.py::test_main_dashboard_builds` 가
- [ ] **A-2 (P2, 신규 · 문서 정정)** 「pytest 재실행은 conda 부재로 실패」는 **오진**이다.
- [ ] **A-3 (P2, 신규 · 사용자 몫)** 09:37:33 에 뜰 `conda run … pytest tests/test_597_order_v…`
- [ ] **F-3 형제 1건 (P2)** `main.py:14880` `logger.critical("[System] 키움 연결 실패 — 종료")`
- [ ] **F-1(538-4) 승인 대기 — 10거래일째 재현** (09-04 532차 최초 등록). 오늘 08:41:09 재현 확인,
- [ ] **O-t4 1일차 관측 완료** — 09-18 09:00:00 `[ConfFloorGuard]` out_max=0.3479, F-10(600차)
- [ ] **1-2(09-17 access violation) 우선순위 결정 — 여전히 사용자 몫** (2026-09-17 601차 9p-3
- [ ] **미커밋 3파일 지속** — `features/levels/levels_store.py`·`premarket_levels.py`(롤 정책
- [ ] 🔴 **O-i1 (신규, P1) `.git/index.lock` 원인불명 생성 — 12:37 이후 재판정 필요.** 12:27:27
- [ ] **F-1(538-4) 승인 대기 — 11거래일째 재현** (09-04 532차 최초 등록). 09-18 장중에도
- [ ] **O-t4 1일차 관측 지속** — 09-18 09:00:00 `[ConfFloorGuard]` out_max=0.3479, 장중에도
- [ ] **미커밋 3파일 지속 + dev_memory 2파일 추가 미커밋** — 실질 변경 5파일
- [ ] **G-2 (P2, 신규)** 증거수집기가 실행 "시작 시점"만 락 유무를 자가점검하는데, 수집 종료
- [ ] 🔴 **F-16 (P1, 신규 · 사용자 몫) `.git/index.lock` 회수 필요** — 16:14·16:22 재확인
- [ ] **F-17 (P2, 신규) F-16 완료 후 미커밋 코드 3건 + 오늘 산출물 커밋** — 경로 명시해
- [ ] **P-1 (신규, 사용자 결정) 캠페인 표본 기아 완화 사다리 2단계 적용 여부** — 09-18
- [ ] **O-t7 (2026-09-21 08:41)** `[SessionStateDrop]` 12거래일째 재현 여부 — F-1(538-4)
- [ ] **O-t8 (2026-09-21 09:00, 구 O-t4 2일차)** `[ConfFloorGuard] out_max` — 09-18 저녁
- [ ] **1-2 정정 기록** — 장전 절 "10거래일째"는 영업일 계산 오류(09-04~09-18 실제
- [ ] **606-1 표본 기아 사다리 2단계 — `MetaGate take_ceil 0.570 → 0.52` 적용 여부**
- [ ] **606-2 F-1(538-4) `SessionStateDrop` 완료 마커 캐리오버 수정 승인 여부**
- [ ] **606-3 미커밋 코드 3건 diff 검토 후 커밋** — `features/levels/levels_store.py`
- [ ] **606-4 09-17 access violation 원인 조사 우선순위 결정** — 09-17 이후 라이브
- [ ] **606-5 (P2) `scripts/git_lock_guard.py` 정본/사본 드리프트 — 어느 쪽을 살릴지 결정**
- [ ] **606-6 (P2) 전체 테스트 스위트 access violation 은 teardown 에서 난다 — 재분류**
- [ ] **606-7 화면 코드 세션 — `dashboard/main_dashboard.py` 작업 마친 뒤 실패 5건 재확인**
- [ ] **O-p1 (오늘 장중·장후 판정)** `[HealthPolicy] Degraded 선제차단` 09:01:01·
- [ ] **O-p2 (다음 SessionStateDrop 재현 시)** F-1(538-4) 재현이 정규 거래일 08:41
- [ ] **P2 (신규, 저우선)** `joblib` 버전 문서 불일치 — `CLAUDE.md`는 "1.1.1"로
- [ ] **P2 (신규)** `collect_evidence.py` 자체 실행에서 `git diff` 호출이 실패해
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
t_493_commission_rate_and_net_recon` · `test_457_fallback_visibility`.
      현재 `dashboard/` 에 백업 12개(09-14~09-17)가 쌓인 **작업 중 상태**라
      귀속은 **추정**이다. 그 세션이 마친 뒤 재확인해야 확정된다.
      (`test_554_position_state_isolation` · `test_477_f1_f5_saturation_psi` 는
       `main.py` 참조 기존 실패 — 별건)

### 완료 (606차 후속이 닫음)

- [x] **F-16 `.git/index.lock` 회수** — 12:27:27 생성 0바이트 락, 나이 약 5시간,
      git 프로세스 0개로 STALE 재확인 후 회수. `git_lock_guard.py --check` → exit=0.
      ⚠ **원인은 여전히 미상** — 관측 `O-t9`(재발 여부)는 열려 있다.
      ⚠ 어제(09-17 16:19 커밋 잔재)와 **증상은 같고 원인은 다르다.** 「어제 고쳤으니
      해결」로 읽지 말 것.
- [x] **595-1 정규수집 자동 발화 확인** (오늘 장후 §4-1 항목 2 「사용자 몫」) —
      `Mireuk_RegularCollect_1552` State=Ready · LastRun=2026-09-18 15:52:52 ·
      LastResult=0 · **NextRun=2026-09-21 15:52:52**. `NextRun` 이 다음 영업일로
      잡혀 있는 것이 스케줄러 생존 증거다(수동 실행이면 갱신 안 됨). ⇒ 종결.
- [x] **G-3 락 회수 안내 양식 고정** — `references/report_template.md` §9p-3.
      ⚠ **MW0602 는 브랜치가 갈라져 `git pull` 로 못 받는다**(함정 ③) — 필요하면 파일 전달.

## 2026-09-21 (MW0601 609차 — 장전 점검)

**근거**: `docs/정기점검/매일점검/MW0601-20260921-점검리포트.md` 장전(pre) 절,
`dev_memory/DECISION_LOG.md` 2026-09-21(609차).

### 신규 등록

- [ ] **O-p1 (오늘 장중·장후 판정)** `[HealthPolicy] Degraded 선제차단` 09:01:01·
      09:03:01 2건 관측(개장 버스트 구간, cause=S6(1155ms)·S5(534ms) — 기존 F-1p류
      S0(모델 리로드) 원인과 다르다). 하루 종일 소수·개장구간 한정이면 정상 판정,
      장중 지속되거나 실제 자동진입 차단으로 이어지면 P1 격상.
- [ ] **O-p2 (다음 SessionStateDrop 재현 시)** F-1(538-4) 재현이 정규 거래일 08:41
      기동인지 비거래일(주말 등) 기동인지 구분해 기록할 것 — 09-21 08:41 로그에는
      경고가 없었으나, 이는 해소가 아니라 **09-20(일, 휴장일) 14:09:42에 이미
      재현되어 넘길 마커가 남아있지 않았기 때문**(609차 확인, 상세는 DECISION_LOG
      2026-09-21 609차 항목 1). 다음 세션은 이 사실을 놓치고 "해소"로 오판하지 말 것.
- [ ] **P2 (신규, 저우선)** `joblib` 버전 문서 불일치 — `CLAUDE.md`는 "1.1.1"로
      적고 있으나 실측 런타임은 최소 8개 이상 일자에 걸쳐 일관되게 `joblib=1.1.0`
      (609차 확인). 운영 영향 없음(장기간 이 값으로 정상 동작 중) — CLAUDE.md
      문구 정정만 필요. 우선순위 낮음.
- [ ] **P2 (신규)** `collect_evidence.py` 자체 실행에서 `git diff` 호출이 실패해
      §2가 "실질 변경 미측정"으로 판정 보류됨(609차, 오늘 pre 실행). 세션이 수동으로
      `git --no-optional-locks diff --numstat -w`를 돌려 우회 확인은 했으나(3파일만
      실질 변경), 수집기 자체의 git diff 호출 방식(타임아웃·인자 등)을 점검해
      재발을 막을 것.

### 확인 완료 (609차가 재확인, 신규 아님)

- [x] `[출처축] PHANTOM_STATE_ARTIFACT` 08:41:09 2건 — 554차 기존 등록 라벨, 신규 아님.
- [x] `[ChartDBG] paintEvent slow` 09:00~09:02 386건 — 기존 F-1p 추적 중, 오늘 건수는
      최근 며칠 대비 낮은 수준.
- [x] 미커밋 707건 중 실질 변경은 606-3 항목의 그 3파일뿐(`levels_store.py`·
      `premarket_levels.py`·`cybos_autologin.py`) — `git diff --stat -w`로 재확인,
      나머지는 EOL 파생.

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

### `data/heartbeat_MW0601_20260921.json` — 244B · 09-21 12:27:29
```json
{
 "pid": 26196,
 "written_at": "2026-09-21T12:28:59",
 "beat_epoch": 1789961339.4681253,
 "beat_age_sec": 0.4,
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

- 파일 최종 기록: **09-21 12:24:29**

| 키 | 값 | 수집 대상일(2026-09-21)과 일치 |
|---|---|---|
| `date` | 2026-09-21 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 155개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260921-점검리포트.md` | 19.0KB | 09-21 09:16 |
| `docs/정기점검/매일점검/evidence_MW0601-20260921_pre.md` | 54.1KB | 09-21 09:02 |
| `docs/정기점검/매일점검/MW0601-20260918-점검리포트.md` | 70.0KB | 09-18 17:59 |
| `docs/정기점검/매일점검/evidence_MW0601-20260918_post.md` | 78.3KB | 09-18 16:18 |
| `docs/정기점검/매일점검/evidence_MW0601-20260918_intra.md` | 64.9KB | 09-18 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20260918_pre.md` | 56.5KB | 09-18 09:03 |
| `docs/정기점검/매일점검/MW0601-20260917-점검리포트.md` | 158.1KB | 09-17 18:05 |
| `docs/정기점검/매일점검/evidence_MW0601-20260917_post.md` | 77.3KB | 09-17 16:19 |

### `docs/정기점검/금요일점검` — 60개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260918.json` | 3.0KB | 09-18 15:55 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260918.md` | 5.0KB | 09-18 15:55 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260918.json` | 38.8KB | 09-18 15:55 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260918.md` | 32.4KB | 09-18 15:55 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260918.json` | 118.7KB | 09-18 15:55 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260918.md` | 194.6KB | 09-18 15:55 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260913.json` | 3.0KB | 09-13 14:43 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260913.md` | 5.0KB | 09-13 14:43 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. `logs/20260921_WARN.log`: ERROR 이상 1건
2. `logs/20260921_WARN.log`: **Traceback** 출현 8건 — 크래시/메모리 계열
3. `logs/20260921_SYSTEM.log`: 매분 루프 커버리지 210/371분 (56.6%) — 루프가 빠진 구간이 있다
4. `logs/20260921_SYSTEM.log`: 12:30~15:10 **연속 161분 매분 루프 기록 없음**
5. 메인 스레드 정지 5초 초과 **5건** (최대 15531ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
6. `logs/20260921_SYSTEM.log`: **ConstOut** 5건(표본)
7. `logs/20260921_SIGNAL.log`: **WeightCollapse** 8건(표본)
8. `logs/20260921_SIGNAL.log`: **ConstOut** 8건(표본)
9. `logs/20260921_LEARNING.log`: **축퇴** 8건(표본)
10. 미커밋 변경 714건 — **실질 변경 미측정**(git diff 실패). 원시 건수만으로는 착시인지 알 수 없다

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260921*.log` (Windows) / `grep 강제청산 logs/*20260921*.log`*