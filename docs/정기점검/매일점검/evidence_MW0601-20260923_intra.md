# 미륵이 증거 다이제스트 — 2026-09-23 / INTRA

- 생성 2026-09-23 12:35:26 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/gallant-adoring-clarke/mnt/futures`
- 점검 범위: pre, intra (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260923` · `2026-09-23` · `260923` · `0923`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **21개** 파일 · 21개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260923.log` | 125B | 09-23 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260923.log` | 140B | 09-23 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260923.json` | 243B | 09-23 12:35 |
| `launcher_{DATE}_084001_1592.log` | 1 | `logs/Mireuk_batch/launcher_20260923_084001_1592.log` | 4.6MB | 09-23 12:35 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260923.log` | 14.1KB | 09-23 11:55 |
| `position_state.json.gen_{DATE}_103601` | 1 | `data/position_state.json.gen_20260923_103601` | 1.5KB | 09-23 10:36 |
| `position_state.json.gen_{DATE}_103613` | 1 | `data/position_state.json.gen_20260923_103613` | 1.5KB | 09-23 10:36 |
| `position_state.json.gen_{DATE}_103930` | 1 | `data/position_state.json.gen_20260923_103930` | 1.5KB | 09-23 10:36 |
| `retrain_intraday_{DATE}_104702.log` | 1 | `logs/retrain_intraday_20260923_104702.log` | 5.7KB | 09-23 10:47 |
| `retrain_intraday_{DATE}_115350.log` | 1 | `logs/retrain_intraday_20260923_115350.log` | 5.7KB | 09-23 11:54 |
| `{DATE}_DATA.log` | 1 | `logs/20260923_DATA.log` | 236.4KB | 09-23 12:35 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260923_DEBUG.log` | 132.6KB | 09-23 12:35 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260923_HEALTH.log` | 2.9KB | 09-23 12:14 |
| `{DATE}_HOGA.log` | 1 | `logs/20260923_HOGA.log` | 30.3MB | 09-23 12:35 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260923_LEARNING.log` | 500.2KB | 09-23 12:35 |
| `{DATE}_MICRO.log` | 1 | `logs/20260923_MICRO.log` | 611.2KB | 09-23 12:35 |
| `{DATE}_PROBE.log` | 1 | `logs/20260923_PROBE.log` | 142.3KB | 09-23 12:34 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260923_SIGNAL.log` | 369.7KB | 09-23 12:35 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260923_SYSTEM.log` | 556.8KB | 09-23 12:35 |
| `{DATE}_TRADE.log` | 1 | `logs/20260923_TRADE.log` | 8.4KB | 09-23 12:31 |
| `{DATE}_WARN.log` | 1 | `logs/20260923_WARN.log` | 3.5MB | 09-23 12:35 |

## 2. 코드·커밋 상태

- HEAD `1dbf49b` · 브랜치 `v9-dev` · 미커밋 750건 · 실질 변경 **미측정**(git diff 실패) · 인덱스락 없음
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
 M TASK_CLAUDE_HIBERNATE_INSTALL.bat
 M TASK_CLAUDE_WAKE_INSTALL.bat
 M TASK_CLAUDE_WAKE_VERIFY.bat
 M TASK_OPTION_BACKFILL_INSTALL.bat
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
… 외 710건
```

**당일(2026-09-23) 커밋**
```
1dbf49b [MW0601] 603차 후속4: 잔존물의 범인은 예약작업이 아니라 「지우지 못하는 git」이었다
9b63de5 [MW0601] 603차 후속3: MW0602 의 등록검증을 역이식 — 그리고 「자가진단은 선택」이 틀렸다
d9c852f [MW0601] Claude 세션 야간 유실 차단 - 최대절전 전환 + 인앱 업데이터 소화 창
```

**최근 커밋 12건**
```
1dbf49b [MW0601] 603차 후속4: 잔존물의 범인은 예약작업이 아니라 「지우지 못하는 git」이었다
9b63de5 [MW0601] 603차 후속3: MW0602 의 등록검증을 역이식 — 그리고 「자가진단은 선택」이 틀렸다
d9c852f [MW0601] Claude 세션 야간 유실 차단 - 최대절전 전환 + 인앱 업데이터 소화 창
421c2ce [MW0601] 620차 후속: 장후 자동조치 기록 — F-3 종결 · 오늘치 리포트·증거 커밋
e294cc3 [MW0601] 620차: 안 걸어본 축이 있었다 — 종료 원인 3축 대사
373c908 [MW0601] 618차 후속: 스위트 기준선 기록 — 기존 실패 9건, 전부 618차 이전
49a2244 [MW0601] 618차: 재기동은 흔적을 남겨야 하고, 빈 봉은 세어야 한다
39d4af5 [MW0601] 617차 후속: dev_memory 기록 — 대시보드 크래시 원인·조치·남은 과제
e3e5d91 [MW0601] 617차 후속: 표시 위젯 한 줄이 엔진을 죽였다 — 폭 0 캔버스와 무가드 슬롯
c69e061 [MW0601] 611차 후속4: 데이터를 보기 전에 기준을 못 박는다 — [80] 사전등록
bad6454 [MW0602] 583차: 수급 오전이 비는 건 구조다 — 백필을 EOD 에 걸고, 미연결을 한도소진과 구분한다
f536354 [MW0601] 611차 후속3: 08:45 는 우리 결손이 아니었다 — 원천에 없다 (+ 시작 시각 여유)
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

_본문 미열람(설정): `20260923_HOGA.log` 30.3MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/16개 (중요도순). 제외: `20260923_MICRO.log`, `20260923_DATA.log`, `20260923_PROBE.log`, `launcher_20260923_084001_1592.log`, `20260923_DEBUG.log`, `mainstall_traceback_20260923.log`, `freeze_sentinel_20260923.log`, `force_flat_guard_20260923.log`_

### `logs/20260923_TRADE.log` — 8.4KB · 56행 · 최종 12:31:27

- 형식 평문 · 시각 인식 56행 · INFO=56

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-23 08:41:03 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-23 08:41:08 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-23 09:44:01 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,725,029) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-23 09:49:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,725,029) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-23 09:55:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,725,029) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
  …
2026-09-23 11:30:21 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-23 11:53:43 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-23 12:10:45 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-23 12:23:00 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-23 12:31:27 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×56

**컴포넌트 상위 15** — `Sizer`×22, `ProfitGuard`×7, `Chejan`×7, `Position`×5, `주문요청`×3, `모드필터 차단`×2, `자동진입 차단`×1, `진입체크`×1, `체결진입`×1, `체결진입보정`×1, `TickTP1`×1, `TP1 부분청산`×1, `TickStop-S0C`×1, `청산 완료`×1, `MarginCap`×1

### `logs/20260923_WARN.log` — 3.5MB · 17210행 · 최종 12:35:22

- 형식 평문 · 시각 인식 17210행 · CRITICAL=1, WARNING=17209

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-23 08:41:12 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-23 08:41:12 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 31ms
2026-09-23 08:41:14 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2500ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2500 band=INFO since_pipe_s=NA
2026-09-23 08:41:14 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 2422ms account=333044256
2026-09-23 08:41:14 [WARNING] SYSTEM: [LiveDBG] _ts_sync_position_from_broker BlockRequest 2419ms — 메인 스레드 2419ms 점유
  …
2026-09-23 12:36:01 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 211.3ms | size=2115x1174 candles=225 grid=45.1 spans=7.2 candles=11.1 dir=0.8 regime=10.0 markers=127.8 axes=7.6 cross=0.0 | slow_cnt=29 total_cnt=29 overlay_cnt=275
2026-09-23 12:36:11 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 195.0ms | size=2115x1174 candles=225 grid=82.7 spans=18.6 candles=9.6 dir=0.8 regime=9.7 markers=69.0 axes=3.0 cross=0.0 | slow_cnt=30 total_cnt=30 overlay_cnt=305
2026-09-23 12:36:21 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 90.1ms | size=2115x1174 candles=225 grid=32.5 spans=7.0 candles=8.6 dir=0.7 regime=3.7 markers=34.8 axes=1.3 cross=0.0 | slow_cnt=31 total_cnt=31 overlay_cnt=324
2026-09-23 12:36:32 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 85.8ms | size=2115x1174 candles=225 grid=29.1 spans=8.7 candles=8.6 dir=0.7 regime=5.1 markers=30.9 axes=1.2 cross=0.0 | slow_cnt=32 total_cnt=32 overlay_cnt=354
2026-09-23 12:36:34 [WARNING] SYSTEM: [LiveDBG] _fetch_investor_data 지연 587ms — 메인 스레드 587ms 점유 (live 중단 원인 후보)
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `Health` | 1 | 11:55:05 | 11:55:05 | level=CRITICAL degraded=OFF | latency=5214ms | quality=1.00 | cache_age=93s | exceptions_10m=3 | exc_tags=[BarGap]×1 [LEVELS]×1 [RESTART]×1 |

<details><summary>CRITICAL/Health 원문 1건</summary>

```
2026-09-23 11:55:05 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=5214ms | quality=1.00 | cache_age=93s | exceptions_10m=3 | exc_tags=[BarGap]×1 [LEVELS]×1 [RESTART]×1
```

</details>

**WARNING — 태그 35종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 16858 | 09:00:49 | 12:36:32 | paintEvent slow 94.0ms | size=1799x832 candles=16 grid=31.0 spans=0.0 candles=31.0 dir=0.0 regime=0.0 markers=0.0 axes=32.0 cross=0.0 | slow_cnt=1 total_cnt=1 |
| `LiveDBG` | 192 | 08:41:12 | 12:36:34 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `OptionFlowChart` | 23 | 10:47:12 | 12:32:00 | 그리기 88.2ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 861x1001 |
| `출처축` | 14 | 08:41:14 | 12:31:33 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |
| `PipePerf` | 12 | 09:00:02 | 12:13:01 | total=1967ms | S0=5ms S1=39ms S2=0ms S3=0ms S4=186ms S5=629ms S6=1017ms S7=77ms S8=13ms |
| `CB⑤` | 10 | 09:00:02 | 12:13:02 | 파이프라인 1967ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `ScalerRefresh` | 9 | 09:08:00 | 12:16:00 | 5분 누적 수익률 -0.274% (임계 ±0.255%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `Health` | 8 | 09:00:02 | 12:13:01 | level=WARNING degraded=OFF | latency=1967ms | quality=0.86 | cache_age=38s | exceptions_10m=0 |
| `ChejanFlow` | 7 | 10:36:00 | 10:39:30 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A056A' | fill_price=0.0 | fill_qty=2 | gubun='0' | order_no='1686' | pending='ENTRY:SHORT qty=2 filled=0 order_no=? reason=진입 req_at=10:36:00.655' | positi… |
| `ChejanMatch` | 7 | 10:36:00 | 10:39:30 | order_no='1686' | pending='ENTRY:SHORT qty=2 filled=0 order_no=1686 reason=진입 req_at=10:36:00.655' | pending_matched=True |
| `SessionBackfill` | 6 | 08:41:44 | 08:41:44 | OHLCV 불일치 ts=2026-09-22 09:30:00 cols=['open'] existing_source=rt |
| `PendingOrder` | 6 | 10:36:00 | 10:39:30 | set {'kind': 'ENTRY', 'direction': 'SHORT', 'raw_direction': 'SHORT', 'reverse_entry_enabled': False, 'qty': 2, 'price_hint': 1119.02, 'reason': '진입', 'hint_source': '', 'atr': 1.0257, 'grade': 'A', 'stage': None, 'order_no': '', 'filled_q… |

**채널** — `SYSTEM`×17201, `HEALTH`×9

**컴포넌트 상위 15** — `ChartDBG`×16858, `LiveDBG`×192, `OptionFlowChart`×23, `출처축`×14, `PipePerf`×12, `CB⑤`×10, `Health`×9, `ScalerRefresh`×9, `ChejanFlow`×7, `ChejanMatch`×7, `SessionBackfill`×6, `PendingOrder`×6, `BarGap`×6, `OptionChain`×6, `RESTART`×6

### `logs/20260923_SYSTEM.log` — 556.8KB · 3910행 · 최종 12:35:06

- 형식 평문 · 시각 인식 3887행 · INFO=3887, PLAIN=23

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-23 08:40:33 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=23656 | 행감지=30s all_threads=True
2026-09-23 08:40:51 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-23 08:40:51 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-23 08:40:51 [INFO] SYSTEM: 미륵이 초기화
2026-09-23 08:40:51 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-09-22) 종가 버퍼 로드: 381봉
  …
2026-09-23 12:36:33 [INFO] SYSTEM: [System] 대기 중 | 장중 — Cybos 실시간 분봉 대기 중 (FutureCurOnly/FutureJpBid 수신 시 자동 진행) | 레짐=NEUTRAL | 포지션=FLAT | 12:36:33
2026-09-23 12:36:33 [INFO] SYSTEM: [CybosInvestorRaw] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:+703,foreign:+46,institution:-798} amt_mn={individual:+198329,foreign:+17982,institution:-229985}
2026-09-23 12:36:33 [INFO] SYSTEM: [CybosInvestorRaw] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:+703,foreign:+46,institution:-798} amt_mn={individual:+198329,foreign:+17982,institution:-229985}
2026-09-23 12:36:33 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=-22891 nonarb=-621566
2026-09-23 12:36:33 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=-22891 nonarb=-621566
```

</details>

**채널** — `SYSTEM`×3887

**컴포넌트 상위 15** — `CybosInvestorRaw`×850, `CybosRT-TICK`×756, `TickUI`×227, `CybosRT-ROLLOVER`×224, `BAR-CLOSE`×224, `CVD-ANCHOR`×224, `S6Detail`×210, `PipePerf`×210, `CybosSub`×147, `System`×99, `OptionChain`×53, `MicroRegime`×47, `CybosRT-START`×42, `BalanceUI`×40, `SYSTEM`×39

### `logs/20260923_SIGNAL.log` — 369.7KB · 3227행 · 최종 12:35:00

- 형식 평문 · 시각 인식 3227행 · WARNING=1188, INFO=2039

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-23 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.435
2026-09-23 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.422
2026-09-23 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.414
2026-09-23 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.410
2026-09-23 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.418
  …
2026-09-23 12:36:00 [INFO] SIGNAL: [IntradayRegime] CRASH → DAY_RISK_OFF | day=-1.72% ATR=1.00 z=1
2026-09-23 12:36:00 [INFO] SIGNAL: [FQAdj] fq=1.00 → min_conf 0.65→0.62 (완화)
2026-09-23 12:36:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=50.2% grade=X regime=NEUTRAL
2026-09-23 12:36:00 [INFO] SIGNAL: 앙상블: dir=+0 conf=50.2% grade=X micro=횡보장
2026-09-23 12:36:00 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: FLAT수렴 / conf미달(0.502<mc0.620) | 참고: 이상값피처(program_arb_net(candidate))
```

</details>

**WARNING — 태그 9종 (상위 9)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 774 | 09:00:02 | 12:33:04 | 1m 'macro_risk_on' scale=0.4440 → floor=0.50 적용 (z-score 폭발 방지) |
| `Model` | 156 | 09:01:00 | 12:32:00 | 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 144 | 09:01:00 | 12:35:00 | ts=09:00 horizon=1m age=1m max_z=+4.19(quality_investor_reason_code) extreme=2 adj=1 |
| `WeightCollapse` | 42 | 09:07:00 | 12:33:03 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `Checklist` | 41 | 09:06:00 | 12:02:00 | 신뢰도 미달 35.6% < 39.2% → 강제 X등급 |
| `ScalerRefresh` | 18 | 08:45:14 | 08:45:14 | 1m CORE 'cvd_divergence' raw_std≈0(0.0308) → identity(0,1) 강제 (FLAT 100% 방지) |
| `PCR-Dampen` | 5 | 09:10:00 | 09:44:01 | opt_pcr_* 피처 D_FORCE 발동 → 30분간 0.3× 감쇠 적용 |
| `MetaGate` | 5 | 10:55:00 | 12:03:00 | meta_conf 5회 연속 과소 → 다음 배치 재학습 대기 (streak=5) |
| `ConstOut` | 3 | 10:14:00 | 11:26:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |

**채널** — `SIGNAL`×3227

**컴포넌트 상위 15** — `ScalerFloor`×816, `SIGNAL`×420, `MetaGate`×242, `Ensemble`×224, `Model`×210, `FQAdj`×207, `ZeroDiag`×187, `ScalerMonitor`×144, `Checklist`×117, `ATR-Horizon`×63, `ScalerRefresh`×55, `차단`×54, `DynMC`×53, `MicroRegime`×47, `WeightCollapse`×42

### `logs/20260923_LEARNING.log` — 500.2KB · 3379행 · 최종 12:35:00

- 형식 평문 · 시각 인식 3379행 · WARNING=1056, INFO=2323

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-23 08:40:53 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-23 08:40:54 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00004 auc=0.481 out_max=0.3375 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과
2026-09-23 08:40:54 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00022 auc=0.453 out_max=0.1501 (기준 auc<0.53 and span<0.020, 기저율=0.1500 n=80) → 보정 미적용, raw 통과
2026-09-23 08:40:54 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00147 auc=0.452 out_max=0.3631 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
2026-09-23 08:40:54 [INFO] LEARNING: [Calibration:30m] 축퇴 해소 — span=0.00136 auc=0.573 out_max=0.1248 (n=145) → 보정 재적용
  …
2026-09-23 12:35:00 [INFO] LEARNING: [SGD] 2건 학습 | SGD비중=30% 50분정확도=0.0%
2026-09-23 12:36:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0000% buf_n=4 nonzero=4 prev_p=1113.90 cur_p=1113.84
2026-09-23 12:36:00 [INFO] LEARNING: ✓ 1m 예측 적중 (conf=44.0% FL)
2026-09-23 12:36:00 [INFO] LEARNING: ✓ 30m 예측 적중 (conf=39.6% FL)
2026-09-23 12:36:00 [INFO] LEARNING: [SGD] 2건 학습 | SGD비중=30% 50분정확도=0.0%
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:1m` | 405 | 08:40:54 | 12:31:22 | 축퇴 감지 — span=0.00004 auc=0.481 out_max=0.3375 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과 |
| `Calibration:30m` | 329 | 08:40:54 | 12:31:21 | 축퇴 감지 — span=0.00022 auc=0.453 out_max=0.1501 (기준 auc<0.53 and span<0.020, 기저율=0.1500 n=80) → 보정 미적용, raw 통과 |
| `Calibration:10m` | 99 | 08:40:54 | 12:31:22 | 축퇴 감지 — span=0.00021 auc=0.509 out_max=0.4223 (기준 auc<0.53 and span<0.020, 기저율=0.4222 n=90) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:3m` | 93 | 08:40:54 | 12:31:22 | 축퇴 감지 — span=0.00147 auc=0.452 out_max=0.3631 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과 |
| `Calibration:15m` | 68 | 08:40:55 | 12:31:21 | 축퇴 감지 — span=0.00144 auc=0.527 out_max=0.3758 (기준 auc<0.53 and span<0.020, 기저율=0.3750 n=120) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:5m` | 52 | 08:40:55 | 12:31:19 | 축퇴 감지 — span=0.00049 auc=0.514 out_max=0.3353 (기준 auc<0.53 and span<0.020, 기저율=0.3350 n=200) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:ensemble` | 9 | 08:41:03 | 12:31:22 | 복원한 보정기가 축퇴 상태 — span=0.00163 auc=0.497 out_max=0.3407 (n=1184) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다. |
| `Buffer-Timing` | 1 | 11:56:01 | 11:56:01 | total=371ms raw_fetch=3ms pred_select=4ms pred_update=7ms pred_insert=1ms verified=3 |

**채널** — `LEARNING`×3379

**컴포넌트 상위 15** — `Calibration:1m`×807, `Calibration:30m`×654, `LEARNING`×640, `SGD`×211, `Calibration:10m`×187, `Calibration:3m`×179, `sigma`×156, `Calibration:15m`×136, `Calibration:5m`×99, `Bias`×64, `Bias⚠`×57, `OnlineLearner`×40, `ScalerWarmup`×37, `MetaConf`×31, `Calibration:ensemble`×18

### `logs/20260923_HEALTH.log` — 2.9KB · 20행 · 최종 12:14:00

- 형식 평문 · 시각 인식 20행 · CRITICAL=1, WARNING=8, INFO=11

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-23 09:00:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1967ms | quality=0.86 | cache_age=38s | exceptions_10m=0
2026-09-23 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=759ms | quality=0.86 | cache_age=97s | exceptions_10m=0
2026-09-23 09:27:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=321ms | quality=1.00 | cache_age=181s | exceptions_10m=0
2026-09-23 09:28:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=342ms | quality=1.00 | cache_age=57s | exceptions_10m=0
2026-09-23 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 327ms (표본 20분)
  …
2026-09-23 11:55:05 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=5214ms | quality=1.00 | cache_age=93s | exceptions_10m=3 | exc_tags=[BarGap]×1 [LEVELS]×1 [RESTART]×1
2026-09-23 11:56:01 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=1484ms | quality=1.00 | cache_age=150s | exceptions_10m=4 | exc_tags=[BarGap]×1 [CB]×1 [LEVELS]×1 외 1종
2026-09-23 11:57:00 [INFO] HEALTH: [Health] level=INFO degraded=ON | latency=280ms | quality=1.00 | cache_age=24s | exceptions_10m=4 | exc_tags=[BarGap]×1 [CB]×1 [LEVELS]×1 외 1종
2026-09-23 12:13:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1248ms | quality=1.00 | cache_age=148s | exceptions_10m=3 | exc_tags=[BarGap]×1 [LEVELS]×1 [RESTART]×1
2026-09-23 12:14:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=187ms | quality=1.00 | cache_age=23s | exceptions_10m=3 | exc_tags=[BarGap]×1 [LEVELS]×1 [RESTART]×1
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `Health` | 1 | 11:55:05 | 11:55:05 | level=CRITICAL degraded=OFF | latency=5214ms | quality=1.00 | cache_age=93s | exceptions_10m=3 | exc_tags=[BarGap]×1 [LEVELS]×1 [RESTART]×1 |

<details><summary>CRITICAL/Health 원문 1건</summary>

```
2026-09-23 11:55:05 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=5214ms | quality=1.00 | cache_age=93s | exceptions_10m=3 | exc_tags=[BarGap]×1 [LEVELS]×1 [RESTART]×1
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 8 | 09:00:02 | 12:13:01 | level=WARNING degraded=OFF | latency=1967ms | quality=0.86 | cache_age=38s | exceptions_10m=0 |

**채널** — `HEALTH`×20

**컴포넌트 상위 15** — `Health`×17, `HealthTrend`×3

### `logs/retrain_intraday_20260923_104702.log` — 5.7KB · 43행 · 최종 10:47:49

- 형식 평문 · 시각 인식 43행 · WARNING=2, INFO=41

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-23 10:47:02,095 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-23 10:47:02,095 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-09-23 10:47:02,095 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-23 10:47:02,095 [INFO] RETRAIN_INTRADAY: [DLL] BLAS 경로 이미 충족
2026-09-23 10:47:02,095 [INFO] RETRAIN_INTRADAY: 파라미터: force=False intraday=True horizons=ALL result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_abb64ad3.json
  …
2026-09-23 10:47:49,395 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-09-23 10:47:49,396 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-09-23 10:47:49,396 [INFO] LEARNING: [Retrain] 완료 | 43.1초 | 성공=6/6 호라이즌
2026-09-23 10:47:49,397 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 47.3s 데이터=4800행
2026-09-23 10:47:49,399 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_abb64ad3.json
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `BackfillFilter` | 1 | 10:47:17 | 10:47:17 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 25324/45615 제외 (418차 결정 1) — 남은 20291행 |
| `UnitMismatch` | 1 | 10:47:17 | 10:47:17 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/20291행 제외 (559차 P1'-2) — 남은 18845행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |

**채널** — `LEARNING`×28, `RETRAIN_INTRADAY`×7, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×21, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `DLL`×1, `BackfillFilter`×1, `UnitMismatch`×1, `CUSUM`×1

### `logs/retrain_intraday_20260923_115350.log` — 5.7KB · 43행 · 최종 11:54:33

- 형식 평문 · 시각 인식 43행 · WARNING=2, INFO=41

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-23 11:53:50,647 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-23 11:53:50,648 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-09-23 11:53:50,648 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-23 11:53:50,648 [INFO] RETRAIN_INTRADAY: [DLL] BLAS 경로 이미 충족
2026-09-23 11:53:50,648 [INFO] RETRAIN_INTRADAY: 파라미터: force=False intraday=True horizons=ALL result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_4c9d0229.json
  …
2026-09-23 11:54:33,556 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-09-23 11:54:33,557 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-09-23 11:54:33,557 [INFO] LEARNING: [Retrain] 완료 | 39.7초 | 성공=6/6 호라이즌
2026-09-23 11:54:33,558 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 42.9s 데이터=4800행
2026-09-23 11:54:33,560 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_4c9d0229.json
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `BackfillFilter` | 1 | 11:54:06 | 11:54:06 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 25258/45613 제외 (418차 결정 1) — 남은 20355행 |
| `UnitMismatch` | 1 | 11:54:06 | 11:54:06 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/20355행 제외 (559차 P1'-2) — 남은 18909행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |

**채널** — `LEARNING`×28, `RETRAIN_INTRADAY`×7, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×21, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `DLL`×1, `BackfillFilter`×1, `UnitMismatch`×1, `CUSUM`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 1 |
| 진입 등록(`[Position] 진입`) — **엔진** | 1 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 1 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 1 |
| 차단(`[차단]`) | 54 |
| 사이저 호출(`[Sizer]`) | 22 |

### 포지션 1건 · 승 1 (100%) · 합계 +0.56pt (+6,044원)  ※ 레그 2행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 출처 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|---|
| 10:36:00 | 엔진 | SHORT | 2 | 3m | 2 | +0.56 | +6,044 | 하드스톱(틱) |

**청산 레그 2행** (부분청산 1 · 전량청산 1)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 10:36:13 | 부분 | 1 | +0.56 | +17,022 | TP1 부분청산 33% |
| 10:39:30 | 전량 | 1 | -0.00 | -10,978 | 하드스톱(틱) |

**청산 사유 분포(레그 단위)** — `TP1 부분청산 33%`×1, `하드스톱(틱)`×1

> 최종 청산이 하드스톱·손절 계열인 포지션 1/1건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 +6,044 = 포지션합 +6,044 → OK · `[청산 완료]` 1건 = 조립 포지션 1건 → OK

### 진입 1건

| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|
| 10:36:00 | SHORT | 2 | 1119.02 | 3m | neutral |

계약수 분포 — 2계약×1

등급 분포 — `A급(원시C)`×1

**진입한 건들의 체크리스트 미통과 항목** — `cvd`×1, `chas`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **2계약**×2, **3계약**×20

실제 진입 계약수 — **2계약**×1

> ⚠ 사이저는 최대 **3계약**을 냈는데 실제 진입 최대는 **2계약**이다. 게이트 배수(meta·tox 등)에 눌린 것인지 확인하라 — 실전 전환 기준 ⑧의 `sizing_inversion_watch` 채널이 이것을 본다.

배수 조합 상위 — `conf=0.6 regime=1.0 safe=1.00`×19, `conf=0.6 regime=0.8 safe=1.00`×3

### 차단 사유 54건 · 44종

| 건수 | 사유 |
|---|---|
| 9 | 등급X — 미통과 항목: 2_confidence |
| 2 | ATR 0.96pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.93pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 8.3pt > ATR×5.0=7.0pt (시가=1133.30 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 9.4pt > ATR×5.0=6.9pt (시가=1133.30 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 7.6pt > ATR×5.0=7.0pt (시가=1133.30 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 7.5pt > ATR×5.0=6.8pt (시가=1133.30 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 7.1pt > ATR×5.0=6.9pt (시가=1133.30 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 7.0pt > ATR×5.0=6.9pt (시가=1133.30 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 7.4pt > ATR×5.0=6.6pt (시가=1133.30 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 8.4pt > ATR×5.0=6.0pt (시가=1133.30 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 9.1pt > ATR×5.0=6.0pt (시가=1133.30 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 10.3pt > ATR×5.0=6.0pt (시가=1133.30 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 9.8pt > ATR×5.0=6.1pt (시가=1133.30 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 10.1pt > ATR×5.0=5.6pt (시가=1133.30 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 11.0pt > ATR×5.0=5.8pt (시가=1133.30 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 11.4pt > ATR×5.0=5.7pt (시가=1133.30 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 11.8pt > ATR×5.0=5.6pt (시가=1133.30 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 12.4pt > ATR×5.0=5.6pt (시가=1133.30 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 13.4pt > ATR×5.0=5.5pt (시가=1133.30 반등위험) |

**체크리스트 미통과 항목 누적** — `2_confidence`×9

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 8건

- `×1 [LEVELS]×1 외 1종` ×3
- `5분 진입 정지 | 파이프라인 5214ms — 처리 지연 (임계=5000ms)` ×2
- `일시 정지 해제 — 정상 복귀` ×2
- `연속 손절 1회 (300초 창, 포지션 단위)` ×1

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 48건 · 최대 7234ms · 5초 초과 4건

상위 — 7234ms, 6594ms, 6156ms, 5609ms, 4907ms, 4813ms, 4578ms, 4516ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:00:05 | 5609ms | 1967ms | **3642ms (65%)** |
| 09:05:06 | 7234ms | 453ms | **6781ms (94%)** |
| 10:48:06 | 6156ms | 3950ms | **2206ms (36%)** |
| 11:55:05 | 6594ms | 5214ms | **1380ms (21%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260923_WARN.log`
```
--- [CB] ×4(표본)
10:39:30 2026-09-23 10:39:30 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
11:55:05 2026-09-23 11:55:05 [WARNING] SYSTEM: [CB] 5분 진입 정지 | 파이프라인 5214ms — 처리 지연 (임계=5000ms)
11:55:05 2026-09-23 11:55:05 [WARNING] SYSTEM: [CB] 5분 진입 정지 | 파이프라인 5214ms — 처리 지연 (임계=5000ms)
11:56:01 2026-09-23 11:56:01 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=1484ms | quality=1.00 | cache_age=150s | exceptions_10m=4 | exc_tags=[BarGap]×1 [CB]×1 [LEVELS]×1 외 1종
--- [ExitCooldown] ×2(표본)
10:39:30 2026-09-23 10:39:30 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:42:30)
10:39:30 2026-09-23 10:39:30 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:42:30)
--- level=CRITICAL ×1(표본)
11:55:05 2026-09-23 11:55:05 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=5214ms | quality=1.00 | cache_age=93s | exceptions_10m=3 | exc_tags=[BarGap]×1 [LEVELS]×1 [RESTART]×1
--- 메인 스레드 블로킹 ×8(표본)
08:41:14 2026-09-23 08:41:14 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2500ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2500 band=INFO since_pipe_s=NA
09:00:05 2026-09-23 09:00:05 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 5609ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=5609 band=WARN since_pipe_s=0.1
09:00:53 2026-09-23 09:00:53 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4516ms — 메인 스레드 블로킹 발생 | pipe_elapsed=45 watchdog_alerted=[] | [MainStall] stall_ms=4516 band=INFO since_pipe_s=48.5
09:05:06 2026-09-23 09:05:06 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 7234ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=7234 band=WARN since_pipe_s=0.2
```

### `logs/20260923_SYSTEM.log`
```
--- CIRCUIT ×2(표본)
11:55:05 2026-09-23 11:55:05 [INFO] SYSTEM: [Notify] 🚨 [11:55:05] [미륵이] Circuit Breaker 발동!
11:55:05 2026-09-23 11:55:05 [INFO] SYSTEM: [Notify] 🚨 [11:55:05] [미륵이] Circuit Breaker 발동!
--- ConstOut ×3(표본)
10:14:00 2026-09-23 10:14:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3545) | 앙상블 제외는 유지
10:23:00 2026-09-23 10:23:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3999) | 앙상블 제외는 유지
11:26:00 2026-09-23 11:26:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.5547) | 앙상블 제외는 유지
--- PSI ×8(표본)
09:00:00 2026-09-23 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:06:00 2026-09-23 09:06:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:11:00 2026-09-23 09:11:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:17:00 2026-09-23 09:17:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
--- [CB] ×2(표본)
12:01:01 2026-09-23 12:01:01 [INFO] SYSTEM: [CB] 일시 정지 해제 — 정상 복귀
12:01:01 2026-09-23 12:01:01 [INFO] SYSTEM: [CB] 일시 정지 해제 — 정상 복귀
```

### `logs/20260923_SIGNAL.log`
```
--- CIRCUIT ×1(표본)
11:58:01 2026-09-23 11:58:01 [INFO] SIGNAL: [차단] Circuit Breaker PAUSED — 진입 불가 (CB 해제까지 대기)
--- ConstOut ×8(표본)
10:14:00 2026-09-23 10:14:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.0470 dir=-1)
10:14:00 2026-09-23 10:14:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
10:14:00 2026-09-23 10:14:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
10:15:00 2026-09-23 10:15:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.0470 dir=-1)
--- WeightCollapse ×8(표본)
09:07:00 2026-09-23 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
09:10:00 2026-09-23 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=84.4% grade=X regime=RISK_ON [WeightCollapse]
09:13:00 2026-09-23 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=84.4% grade=X regime=RISK_ON [WeightCollapse]
09:16:00 2026-09-23 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=84.4% grade=X regime=RISK_ON [WeightCollapse]
--- 기동 복원 ×8(표본)
08:40:30 2026-09-23 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.435
08:40:30 2026-09-23 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.422
08:40:30 2026-09-23 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.414
08:40:30 2026-09-23 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.410
--- 안전망 ×8(표본)
09:07:00 2026-09-23 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-09-23 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-09-23 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-09-23 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20260923_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:54 2026-09-23 08:40:54 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00004 auc=0.481 out_max=0.3375 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과
08:40:54 2026-09-23 08:40:54 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00022 auc=0.453 out_max=0.1501 (기준 auc<0.53 and span<0.020, 기저율=0.1500 n=80) → 보정 미적용, raw 통과
08:40:54 2026-09-23 08:40:54 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00147 auc=0.452 out_max=0.3631 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
08:40:54 2026-09-23 08:40:54 [INFO] LEARNING: [Calibration:30m] 축퇴 해소 — span=0.00136 auc=0.573 out_max=0.1248 (n=145) → 보정 재적용
```

### `logs/20260923_HEALTH.log`
```
--- [CB] ×2(표본)
11:56:01 2026-09-23 11:56:01 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=1484ms | quality=1.00 | cache_age=150s | exceptions_10m=4 | exc_tags=[BarGap]×1 [CB]×1 [LEVELS]×1 외 1종
11:57:00 2026-09-23 11:57:00 [INFO] HEALTH: [Health] level=INFO degraded=ON | latency=280ms | quality=1.00 | cache_age=24s | exceptions_10m=4 | exc_tags=[BarGap]×1 [CB]×1 [LEVELS]×1 외 1종
--- level=CRITICAL ×1(표본)
11:55:05 2026-09-23 11:55:05 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=5214ms | quality=1.00 | cache_age=93s | exceptions_10m=3 | exc_tags=[BarGap]×1 [LEVELS]×1 [RESTART]×1
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260923_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:03 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 10:00 | 장중 초반 | 9 | 09:55:00 [INFO] 미니선물 실효잔고=50,000,000(실제잔고=35,725,029) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1) |

- 이 로그 생존구간: 08:41 ~ 12:31

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260923_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 20 | 08:41:12 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 221 | 08:55:15 [WARNING] scaler 노후=0h  z경고피처=20개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 799 | 08:55:15 [WARNING] scaler 노후=0h  z경고피처=20개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 10:00 | 장중 초반 | 1562 | 09:54:00 [WARNING] paintEvent slow 78.0ms | size=1663x832 candles=70 grid=31.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=… |
| 12:00 | 장중 중간점 | 432 | 11:54:00 [WARNING] 그리기 102.2ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 861x1001 |

- 이 로그 생존구간: 08:41 ~ 12:36

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260923_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 94 | 08:40:33 [INFO] 활성화 | file=logs\crash_fault.log PID=23656 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 132 | 08:49:00 [INFO] code=A056A from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 188 | 08:54:00 [INFO] code=A056A from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 198 | 09:54:00 [INFO] code=A056A from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 202 | 11:54:00 [INFO] intraday 2026-09-23 — 6패널 수집, 메인 스레드로 넘긴다 [futures_flow option_chain option_flow prediction price rv_iv] |
| 14:00 | _장중 후반 · 장중 재학습 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 12:36

**매분 루프 커버리지 09:00~15:10: 217/371분 (58.5%)**

연속 3분 이상 기록 없는 구간 1개:

| 시작 | 끝 | 분 |
|---|---|---|
| 12:37 | 15:10 | 154 |

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260923_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 56 | 08:45:14 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0308) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 76 | 09:00:02 [WARNING] 1m 'macro_risk_on' scale=0.4440 → floor=0.50 적용 (z-score 폭발 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 147 | 09:00:02 [WARNING] 1m 'macro_risk_on' scale=0.4440 → floor=0.50 적용 (z-score 폭발 방지) |
| 10:00 | 장중 초반 | 212 | 09:54:00 [WARNING] 신뢰도 미달 31.7% < 39.2% → 강제 X등급 |
| 12:00 | 장중 중간점 | 203 | 11:54:00 [WARNING] 1m 극단 z-score 6개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |

- 이 로그 생존구간: 08:40 ~ 12:36

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260922 | 15:47 | 로그 본문 |
| 20260921 | 17:30 | 로그 본문 |
| 20260920 | 18:39 | 로그 본문 |
| 20260918 | 15:47 | 로그 본문 |
| 20260917 | 20:33 | 로그 본문 |
| **중앙값** | **17:30** | 기준선 |
| **오늘 20260923** | **12:36** | 로그 본문 |

- 델타 **-294분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.3MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-23 (MW0601 603차 후속4 — 잔존물의 범인은 예약작업이 아니라 「지우지 못하는 git」이었다)
### 0. 치운 것
### 1. 범인 추적 — 소유자는 단서가 아니었다
### 2. 이미 알고 있던 문제였고, 도구에 구멍이 있었다
### 3. 고친 것 — 새 도구를 만들지 않고 있는 것을 넓혔다
### 4. 배선 — 치우는 일은 **삭제가 되는 쪽**이 한다
### 5. 예방 — 애초에 안 만드는 쪽
### 6. 자가유발 여부
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
.
   같은 날 커밋이 `Claude 세션 야간 유실 차단 - 최대절전 전환` 이다.
3. Windows 예약작업 중 **git 을 도는 것은 「피터 사료 송신」 하나뿐**이고, 매매
   자동화(마흐디·메시아·미륵이·정규수집)는 git 을 안 건드린다.

🔴 결론 — **예약작업의 산물이 아니다.** 코웍(리눅스 샌드박스) 세션의 git 작업이다.
  그리고 git 이 고장난 것도 아니다. git 은 임시파일을 만들고 **지우면서** 끝나는데
  마운트가 그 `unlink` 를 EPERM 으로 막는다 — **정상 동작의 청소 단계가 권한에
  막혀 쓰레기가 된다.** 두 갈래다:
    tmp_obj_*  이미 있는 객체를 또 쓰면 임시본을 unlink -> 막힘 -> 잔존
    *.lock     rename 이 아니라 unlink 로 끝나는 경로, 또는 중단(최대절전) -> 잔존

### 2. 이미 알고 있던 문제였고, 도구에 구멍이 있었다

`mireuk-daily-check/SKILL.md` 가 이미 적고 있었다 — 0바이트 `index.lock` 이
**53.5시간**(08-21) · **3시간 21분**(08-24) 남아 커밋 불가였던 사고, 그리고
「읽기전용 git 에 `--no-optional-locks` 를 붙인다」는 규약. 도구도 있다
(`scripts/git_lock_guard.py`, 3중 조건 회수).

**그런데 그 도구는 `index.lock` **하나만** 본다.** `HEAD.lock` 은 커밋을 똑같이
막는데 보지 않았다 — 이번에 실제로 `HEAD.lock` 이 있는 채로 프리플라이트가
「정상」이라 답할 뻔했다. `tmp_obj_*` 40개는 아예 시야 밖이었다.

### 3. 고친 것 — 새 도구를 만들지 않고 있는 것을 넓혔다

`scripts/git_lock_guard.py` 에 `scan_extra()` · `sweep_extra()` 추가.

**두 갈래로 나눈다 — 막는 것과 어지르는 것은 다르다.**

| | 대상 | 종료코드 |
|---|---|---|
| T1 잠금 | `HEAD.lock` · `config.lock` · `packed-refs.lock` · `refs/**/*.lock` · `logs/**/*.lock` | 2/3 에 **반영** |
| T2 부스러기 | `objects/**/tmp_obj_*` · `tmp_pack_*` · `*.lock.stale_*` | 세어서 보여만 준다 |

🔴 판정 조건이 `index.lock` 과 **다르다.** 0바이트 조건을 쓰지 않는다 —
  `HEAD.lock`·ref 락은 새 sha 를 **써 넣은 뒤** rename 하므로 정상적으로도
  0바이트가 아니다. 0바이트를 요구하면 진짜 스테일을 놓친다. 나이 + git 프로세스
  0개 둘로 판정하고, 프로세스를 못 세면 판정하지 않는다(계측 4원칙 ②).

🔴 `_fmt()` 가 `index.lock` 만 보므로, T1 이 살아 있는데 「OK」로 찍히는 것을
  막으려고 요약 표시를 `LOCK` 으로 바꾼다. **요약 한 줄이 거짓말하면 도구가 없는
  것만 못하다.**

🔴 회수 실패(코웍의 EPERM)는 **성공한 척하지 않는다** — 「회수 실패 … 삭제 권한이
  없는 환경일 수 있다」로 적고 T1 이면 스테일로 계속 센다.

검증(합성 잔존물 4개): 3시간짜리 T1 2개·T2 1개는 스테일 판정 rc=2, `--check` 로는
한 개도 안 지웠고, 방금 만든 `config.lock` 은 판정보류로 남겼다. `--reclaim` 에서
오래된 3개만 사라지고 방금 것은 그대로, rc=3.

### 4. 배선 — 치우는 일은 **삭제가 되는 쪽**이 한다

- MW0601 `scripts/peter_feed_push_MW0601.bat` (작업 「피터 사료 송신」, 평일 16:00)
- MW0602 `tools/peter_pull.py` (작업 「피터 사료 수신」, 평일 16:30)

둘 다 push/pull **전에** `git_lock_guard.py --reclaim` 을 돌리고 로그에 남긴다.
🔴 rc 는 무시한다 — 위생은 본작업의 전제조건이 아니다(2/3 은 판정 결과일 뿐).

### 5. 예방 — 애초에 안 만드는 쪽

`peter-daily/SKILL.md` 에 **git 호출 규약**을 실었다(미륵이 스킬과 같은 줄):
읽기전용 git 전부에 `--no-optional-locks`, **세션이 손으로 치는 명령도 예외 없음**.

⚠ 이 세션이 그 규약을 어겼다. `git log`·`git show`·`git ls-tree` 를 맨손으로 쳤다.
  미륵이 스킬에만 있고 피터 스킬에는 없었다 — 그래서 옮겨 적었다.

### 6. 자가유발 여부

**절반은 자가유발이다.** 09-22 23:39~23:46 잔존물의 주체는 특정하지 못했지만,
이 세션이 규약 없이 친 git 명령들이 같은 종류의 잔존물을 만들 수 있었고 실제로
경고가 찍혔다. 도구의 `HEAD.lock` 구멍은 483차 설계 시점의 누락이다.

```

</details>

### dev_memory/NEXT_TODO.md — 1.6MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 신규 등록
### 확인 완료 (617차 후속2가 재확인, 신규 아님)
## 2026-09-22 (MW0601 617차 후속3 — 장후 점검)
### 신규 등록
### 확인 완료 (617차 후속3이 재확인·최종판정, 신규 아님)
## 2026-09-23 (MW0601 604차 — 장전 점검)
### 신규 등록
### 확인 완료 (604차가 재확인, 신규 아님)
```

미완료 체크박스 **2815건** (끝에서 30건)
```
- [ ] **606-6 (P2) 전체 테스트 스위트 access violation 은 teardown 에서 난다 — 재분류**
- [ ] **606-7 화면 코드 세션 — `dashboard/main_dashboard.py` 작업 마친 뒤 실패 5건 재확인**
- [ ] **O-p1 (오늘 장중·장후 판정)** `[HealthPolicy] Degraded 선제차단` 09:01:01·
- [ ] **O-p2 (다음 SessionStateDrop 재현 시)** F-1(538-4) 재현이 정규 거래일 08:41
- [ ] **P2 (신규, 저우선)** `joblib` 버전 문서 불일치 — `CLAUDE.md`는 "1.1.1"로
- [ ] **P2 (신규)** `collect_evidence.py` 자체 실행에서 `git diff` 호출이 실패해
- [ ] **O-i1 (오늘 장후 판정)** `[OptionFlow]` 실패 태그 재발 여부·`option_flow.db`
- [ ] **O-i2 (오늘 장후·내일 판정)** `[LiveDBG] _fetch_investor_data 지연` 경고
- [ ] **G-1 (P2, 저우선, 이 점검 세션 제안)** 장중 라이브 배포 시 "재기동 직후
- [ ] **F-1 (P2, 신규) `.git/index.lock` 반복 재발 원인 규명** — 이 세션도
- [ ] **O-p1 (오늘 장중·장후 판정)** `[HealthPolicy] Degraded 선제차단`
- [ ] **O-p2 (5거래일 후 판정 — 313차 원칙, 표본 부족 상태 결론 금지)**
- [ ] **O-p3 (오늘 세션 종료 시 판정)** `.git/index.lock` 최종 상태
- [ ] **O-p4 (다음 점검)** `collect_evidence.py`의 `git diff` 실패
- [ ] **무가드 표시 슬롯 15건 가드** — `python scripts/audit_qtimer_slot_guards.py`
- [ ] **엔진 슬롯 3건 처분 결정(주간회의)** — `main.py:TradingSystem` 의
- [ ] **재기동 원인 표기** — 크래시 재기동이 `cause=STARTUP` 으로 남아 정상
- [ ] 반영 확인 — 다음 재기동 후 좌측 스플리터를 끝까지 끌어 **접히지 않는지**
- [ ] **O-i1 (오늘 장후 또는 다음 재기동 시 판정)** 크래시 수정(커밋 `e3e5d91`)의
- [ ] **O-i2 (26주 WFA 주기, 기존 채널에 표본만 추가)** `sizing_inversion_watch`
- [ ] **F-1(지속) git lock 원인 가설 추가** — 장중 12:35경 재발 시각이 병행
- [ ] **[사용자 판단 필요] 크래시 수정 재기동 시점** — 지금(포지션 FLAT, 재기동
- [ ] **F-3 (P1, 신규) 2차 무흔적 크래시(1-7) 원인 규명** — 15:08:06경
- [ ] **G-3 (P2, 신규) 런처의 "무흔적 즉사" vs "행 멈춤" 구분 계측** —
- [ ] **O-t1 (다음 거래일부터 상시)** 1-7과 같은 무흔적 즉사 재현 여부 —
- [ ] **O-t3 (5거래일 누적 후 판정)** CB③ 판정가능시간 0분 재현 빈도(1-8) —
- [ ] **O-t4 (26주 WFA 주기, O-i2 계승)** `sizing_inversion_watch`([28])
- [ ] **[권고, 급하지 않음] Windows 이벤트 뷰어에서 15:08:06~08 오류 이벤트
- [ ] **O-p1 (오늘 장중 판정)** `raw_candles`/`session_bars` "영구결손 367봉"(09:02~09:21) 표시 —
- [ ] **O-p2 (다음 세션 시작 시 판정)** `.git/index.lock` 회수 여부 — 사용자가 Windows에서
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
-gap`
      로 가드 커버리지 재확인) (b) 606-4의 09-17 access violation과 동일
      계열 (c) 1-5와 같은 GUI 렌더링 계열이지만 이번엔 네이티브 크래시라
      Python이 못 잡음. Windows 이벤트 뷰어(응용 프로그램 로그,
      15:08:06~08 필터) 확인이 다음 조사 단계 — 리눅스 샌드박스에서는
      접근 불가, 사용자 조치로 이관.
- [ ] **G-3 (P2, 신규) 런처의 "무흔적 즉사" vs "행 멈춤" 구분 계측** —
      현재 런처 로그는 둘 다 "일시적 크래시"로 뭉뚱그린다. 정상종료 플래그
      없음 + `FreezeWatchdog` 발동 로그 없음 조합이면 "원인불명 즉사"로
      별도 태그하도록 제안(계측 4원칙 ④ 연장).
- [ ] **O-t1 (다음 거래일부터 상시)** 1-7과 같은 무흔적 즉사 재현 여부 —
      재현 시 F-3 가설 (a)~(c) 중 어느 쪽에 부합하는지 로그로 재확인.
- [ ] **O-t3 (5거래일 누적 후 판정)** CB③ 판정가능시간 0분 재현 빈도(1-8) —
      다음 5거래일 중 2회 이상이면 26주 WFA 재검증 항목 신설 검토
      (`references/invariants.md` §5 편입 여부).
- [ ] **O-t4 (26주 WFA 주기, O-i2 계승)** `sizing_inversion_watch`([28])
      qty≥3 표본 — 오늘 2건 추가(사이저 3계약→실제 2계약, 게이트 배수
      meta×0.5·toxicity×0.7 원인).
- [ ] **[권고, 급하지 않음] Windows 이벤트 뷰어에서 15:08:06~08 오류 이벤트
      확인** — F-3의 실마리. 오늘 손해가 없어 긴급하지 않음.

### 확인 완료 (617차 후속3이 재확인·최종판정, 신규 아님)

- [x] O-i1(크래시 수정 `e3e5d91`의 라이브 반영 여부) — **판정 완료: 반영됨.**
      15:08:30 재기동(1-7의 결과)이 디스크의 최신 코드를 다시 읽어들여
      의도치 않은 경로로 배포까지 끝났다. 장중 F-2·사용자 조치 4번은
      "완료(의도치 않은 경로)"로 종결.
- [x] O-p3(`.git/index.lock` 최종 상태) — **판정 완료: 오늘 하루 STALE
      미해소.** 12:35 생성분이 세션 종료 시점까지 그대로 남음, 이 세션도
      회수 실패(`Operation not permitted`) — 사용자 조치 1번으로 이관.
- [x] `collect_evidence.py` git diff 실패(1-3) — **장후 수집은 정상 작동**
      (실질 변경 5건 정상 산출). 09-21·09-22 3연속 실패 후 처음 성공 —
      완전 해소가 아니라 간헐적 재현으로 재분류.
- [x] EOD `GuardGhost`(12건)·`GuardFair`(6건, 전부 1m) — 457차 F7 ⑤안의
      설계대로 정상 동작(08-25·09-04·09-09·09-11·09-21에 이미 확인된
      패턴). 오늘 장중재학습이 2회(그중 1회는 1-5 크래시의
      WarmupRetrain)로 평소보다 잦아 경고 횟수만 늘었을 뿐.
- [x] 오늘 진입 2건 "A급(원시C)" 상향, 체크리스트 미통과(`cvd`·`fore`·
      `prev`·`chas`) — 전부 등급 하락 사유일 뿐 VWAP 강제X 위반 없음.
      절대원칙 ③ 준수 확인.

## 2026-09-23 (MW0601 604차 — 장전 점검)

### 신규 등록
- [ ] **O-p1 (오늘 장중 판정)** `raw_candles`/`session_bars` "영구결손 367봉"(09:02~09:21) 표시 —
      09:01 시점 조기 집계로 인한 artifact로 추정(당일 예상 총 411봉 중 아직 17봉만
      경과). 장중·장후 재수집 시 정상적으로 채워지는지 확인, 실제 결손이면 새 이상점으로 등록.
- [ ] **O-p2 (다음 세션 시작 시 판정)** `.git/index.lock` 회수 여부 — 사용자가 Windows에서
      `python scripts/git_lock_guard.py --reclaim` 실행 후 `--check`가 OK 반환하는지 확인.

### 확인 완료 (604차가 재확인, 신규 아님)
- [x] F-1(538-4) `SessionStateDrop` — 09-23도 재현(08:41:15). 근본 원인 미해결 상태 지속.
      실제 EOD/P8은 `retrain_eod_20260922.log`로 정상 완료 확인(계측 4원칙 ② 사례).
- [x] 606-3 미커밋 3파일 — diff 크기 재확인(1,332/1,433/4,247줄), 사용자 검토 대기 지속.
- [x] `.git/index.lock` STALE — 09-22 장후부터 미회수 지속, 오늘도 리눅스 세션에서 회수 불가.

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

### `data/heartbeat_MW0601_20260923.json` — 243B · 09-23 12:35:04
```json
{
 "pid": 6512,
 "written_at": "2026-09-23T12:36:34",
 "beat_epoch": 1790134593.6877573,
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

- 파일 최종 기록: **09-23 12:31:33**

| 키 | 값 | 수집 대상일(2026-09-23)과 일치 |
|---|---|---|
| `date` | 2026-09-23 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

### `raw_candles` 절단선·결손 (618차)

| 항목 | 값 |
|---|---|
| `raw_candles` 당일 max ts | **12:35** |
| 절단선(파생 = 강제청산 − 2분) | `15:08` |
| 판정 | **결손** — 아래 목록과 그 시각의 `[START]`/`[CLEAN EXIT]` 대조 |
| `raw_candles` 당일 행수 | 224 |
| `session_bars` 당일 행수 | 224 (기대 411) |

- 결손 **0봉**
- ⚠ **영구 결손 160봉** (`session_bars` 에도 없음): 10:45, 10:46, 11:29, 11:52, 12:09, 12:22, 12:30, 12:36, 12:37, 12:38, 12:39, 12:40, 12:41, 12:42, 12:43, 12:44, 12:45, 12:46, 12:47, 12:48

- 라이브 로그 대조: `logs/20260923_SYSTEM.log` 의 `[BarGap]` 줄
  - 기동 직후 1줄(분그리드 기준) + 15:46 보충 직후 1줄(확정). **한 줄도 없으면 계측이 죽은 것**이지 결손이 없는 것이 아니다.

> 결손 ts 는 그날 재기동 시각과 1:1 대응한다(실측 2026-09-07~09-22: 결손일 3/12일, 12봉, 09-21 은 8회 재기동에 7봉). `[Shutdown] intent=` 줄과 함께 보면 그 재기동이 사용자 의도인지 하드킬인지까지 갈린다.


### 프로세스 종료 3축 대사 (620차)

| 축 | 상태 |
|---|---|
| 런처 로그(기동 PID·재시작 분류) | 측정됨 — 기동 7회 · 재시작 6회 |
| `crash_fault.log`(정상종료 기록) | 측정됨 — PID 7개 |
| Windows WER(네이티브 예외) | **미측정** — 비Windows 플랫폼 — WER 이벤트 로그가 없다 |

| 미륵이 PID | 기동 | 정상종료 기록 | WER 네이티브 예외 | 판정 |
|---|---|---|---|---|
| 23656 | 08:40:33 | 10:45:48 | 없음 | 판정불가 — WER **미측정** |
| 23860 | 10:46:11 | 11:29:20 | 없음 | 판정불가 — WER **미측정** |
| 21744 | 11:29:42 | 11:52:46 | 없음 | 판정불가 — WER **미측정** |
| 8124 | 11:53:08 | 12:09:50 | 없음 | 판정불가 — WER **미측정** |
| 10340 | 12:10:11 | 12:22:06 | 없음 | 판정불가 — WER **미측정** |
| 20224 | 12:22:27 | 12:30:33 | 없음 | 판정불가 — WER **미측정** |
| 6512 | 12:30:54 | 없음 | 없음 | 판정불가 — WER **미측정** |


> 🔴 **「WER 기록 없음」을 「크래시가 아니다」로 읽지 말 것.** 참인 것은 **「미처리 네이티브 예외는 아니었다」까지**다 — `sys.exit`·창 닫기·`TerminateProcess`(하드킬)는 전부 이벤트를 안 남긴다. 종료 *의도*는 618차가 넣은 `[Shutdown] intent=` 줄과 함께 봐야 갈린다.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 163개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260923-점검리포트.md` | 13.0KB | 09-23 09:06 |
| `docs/정기점검/매일점검/evidence_MW0601-20260923_pre.md` | 57.2KB | 09-23 09:02 |
| `docs/정기점검/매일점검/MW0601-20260922-점검리포트.md` | 99.0KB | 09-22 17:46 |
| `docs/정기점검/매일점검/evidence_MW0601-20260922_post.md` | 86.9KB | 09-22 16:22 |
| `docs/정기점검/매일점검/evidence_MW0601-20260922_intra.md` | 70.4KB | 09-22 12:35 |
| `docs/정기점검/매일점검/evidence_MW0601-20260922_pre.md` | 54.0KB | 09-22 09:00 |
| `docs/정기점검/매일점검/MW0601-20260921-점검리포트.md` | 73.2KB | 09-21 16:30 |
| `docs/정기점검/매일점검/evidence_MW0601-20260921_post.md` | 82.1KB | 09-21 16:19 |

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

1. `logs/20260923_WARN.log`: ERROR 이상 1건
2. `logs/20260923_SYSTEM.log`: 매분 루프 커버리지 217/371분 (58.5%) — 루프가 빠진 구간이 있다
3. `logs/20260923_SYSTEM.log`: 12:37~15:10 **연속 154분 매분 루프 기록 없음**
4. `logs/20260923_HEALTH.log`: ERROR 이상 1건
5. 사이저 최대 3계약 → 실제 진입 최대 2계약 — 게이트 배수에 눌림 (sizing_inversion_watch 대상)
6. 메인 스레드 정지 5초 초과 **4건** (최대 7234ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
7. `logs/20260923_WARN.log`: **level=CRITICAL** 1건(표본)
8. `logs/20260923_SYSTEM.log`: **ConstOut** 3건(표본)
9. `logs/20260923_SIGNAL.log`: **WeightCollapse** 8건(표본)
10. `logs/20260923_SIGNAL.log`: **ConstOut** 8건(표본)
11. `logs/20260923_LEARNING.log`: **축퇴** 8건(표본)
12. `logs/20260923_HEALTH.log`: **level=CRITICAL** 1건(표본)
13. 미커밋 변경 750건 — **실질 변경 미측정**(git diff 실패). 원시 건수만으로는 착시인지 알 수 없다

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260923*.log` (Windows) / `grep 강제청산 logs/*20260923*.log`*