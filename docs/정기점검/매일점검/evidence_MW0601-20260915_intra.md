# 미륵이 증거 다이제스트 — 2026-09-15 / INTRA

- 생성 2026-09-15 12:27:05 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/busy-inspiring-pasteur/mnt/futures`
- 점검 범위: pre, intra (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260915` · `2026-09-15` · `260915` · `0915`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **17개** 파일 · 17개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260915.log` | 124B | 09-15 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260915.log` | 139B | 09-15 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260915.json` | 244B | 09-15 12:26 |
| `launcher_{DATE}_084000_5416.log` | 1 | `logs/Mireuk_batch/launcher_20260915_084000_5416.log` | 4.1MB | 09-15 12:27 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260915.log` | 2.9KB | 09-15 08:41 |
| `retrain_intraday_{DATE}_110001.log` | 1 | `logs/retrain_intraday_20260915_110001.log` | 3.2KB | 09-15 11:00 |
| `{DATE}_DATA.log` | 1 | `logs/20260915_DATA.log` | 182.8KB | 09-15 12:27 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260915_DEBUG.log` | 128.0KB | 09-15 12:27 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260915_HEALTH.log` | 3.1KB | 09-15 12:14 |
| `{DATE}_HOGA.log` | 1 | `logs/20260915_HOGA.log` | 28.8MB | 09-15 12:27 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260915_LEARNING.log` | 181.4KB | 09-15 12:27 |
| `{DATE}_MICRO.log` | 1 | `logs/20260915_MICRO.log` | 545.1KB | 09-15 12:27 |
| `{DATE}_PROBE.log` | 1 | `logs/20260915_PROBE.log` | 57.5KB | 09-15 12:26 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260915_SIGNAL.log` | 267.0KB | 09-15 12:27 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260915_SYSTEM.log` | 426.0KB | 09-15 12:27 |
| `{DATE}_TRADE.log` | 1 | `logs/20260915_TRADE.log` | 167B | 09-15 08:41 |
| `{DATE}_WARN.log` | 1 | `logs/20260915_WARN.log` | 3.4MB | 09-15 12:27 |

## 2. 코드·커밋 상태

- HEAD `646eac3` · 브랜치 `v9-dev` · 미커밋 644건 · 실질 변경 **미측정**(git diff 실패) · 인덱스락 없음
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
… 외 604건
```

**당일(2026-09-15) 커밋**
```
646eac3 [MW0601] 582차 후속: 편집 스크립트가 남긴 홀로 CR 제거 (기능 무변경)
499eb64 [MW0601] 582차: 「잠정」에 실측 뒤집힘률을 붙인다 (표시 전용)
7bc79e7 [MW0601] 581차: 전환 세로선이 안 보이던 것 수정 — 실측 대비 Δ4 → Δ65~105 (표시 전용)
d1a19e6 [MW0601] 580차: 실시간 오버레이 미표시 수정 — 장중에 상태·배지를 다시 센다 (표시 전용)
```

**최근 커밋 12건**
```
646eac3 [MW0601] 582차 후속: 편집 스크립트가 남긴 홀로 CR 제거 (기능 무변경)
499eb64 [MW0601] 582차: 「잠정」에 실측 뒤집힘률을 붙인다 (표시 전용)
7bc79e7 [MW0601] 581차: 전환 세로선이 안 보이던 것 수정 — 실측 대비 Δ4 → Δ65~105 (표시 전용)
d1a19e6 [MW0601] 580차: 실시간 오버레이 미표시 수정 — 장중에 상태·배지를 다시 센다 (표시 전용)
d1c17c8 [MW0601] 580차: 잔고 배지 2행 고정높이 — 캔들차트 세로 확보 (표시 전용)
632207f [MW0601] 579차: 보유 중 레벨선 — 진입·하드스톱·TP1/2/3·트레일링 (표시 전용)
11e4c8c [MW0601] 578차: 진입단계 카드 상하 여백 제거 — 캔들차트 세로 추가 확보 (표시 전용)
cbe158a [MW0601] 577차: 호라이즌 스트립 1행화 + 진입단계 표 10행 고정 — 캔들차트 세로 확보 (표시 전용)
d595127 [MW0601] 576차: 좌측 중단 행을 **진짜 배너**로 옮김 + 공용 위젯화 (표시 전용)
34d53dd [MW0601] 575차 후속: 구현계획 부록 A-0 범위 정정 (배너 좌측 중단은 구현됨)
5479e79 [MW0601] 575차: 보조 모니터 배너 좌측 중단 — 상태·현재가·포지션 (표시 전용)
4d63137 [MW0601] 574차: 겹치는 우상단 요약 제거 + 문턱 설명을 레전드로 (표시 전용)
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

_본문 미열람(설정): `20260915_HOGA.log` 28.8MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/15개 (중요도순). 제외: `20260915_DATA.log`, `20260915_PROBE.log`, `launcher_20260915_084000_5416.log`, `20260915_DEBUG.log`, `mainstall_traceback_20260915.log`, `freeze_sentinel_20260915.log`, `force_flat_guard_20260915.log`_

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

### `logs/20260915_WARN.log` — 3.4MB · 16552행 · 최종 12:27:05

- 형식 평문 · 시각 인식 16552행 · CRITICAL=1, WARNING=16551

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-15 08:41:19 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-15 08:41:19 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 62ms
2026-09-15 08:41:19 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 172ms account=333044256
2026-09-15 08:41:21 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-09-15 08:41:21 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-09-15 12:28:14 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 78.0ms | size=1533x900 candles=219 grid=31.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=47.0 axes=0.0 cross=0.0 | slow_cnt=16436 total_cnt=22809
2026-09-15 12:28:16 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 94.0ms | size=1533x900 candles=219 grid=31.0 spans=0.0 candles=16.0 dir=0.0 regime=0.0 markers=47.0 axes=0.0 cross=0.0 | slow_cnt=16437 total_cnt=22810
2026-09-15 12:28:16 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 78.0ms | size=1533x900 candles=219 grid=31.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=47.0 axes=0.0 cross=0.0 | slow_cnt=16438 total_cnt=22811
2026-09-15 12:28:17 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 62.0ms | size=1533x900 candles=219 grid=15.0 spans=0.0 candles=16.0 dir=0.0 regime=0.0 markers=31.0 axes=0.0 cross=0.0 | slow_cnt=16439 total_cnt=22812
2026-09-15 12:28:18 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 63.0ms | size=1533x900 candles=219 grid=31.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=32.0 axes=0.0 cross=0.0 | slow_cnt=16440 total_cnt=22813
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `SHS-EKS` | 1 | 09:05:00 | 09:05:00 | Early Kill Switch 발동 — 일시 관망 conf_max=34.4% bars=5 → 스케일러·conf 회복 시 자동 재개 (09:20부터 30분 간격 평가) |

<details><summary>CRITICAL/SHS-EKS 원문 1건</summary>

```
2026-09-15 09:05:00 [CRITICAL] SYSTEM: [SHS-EKS] Early Kill Switch 발동 — 일시 관망 conf_max=34.4% bars=5 → 스케일러·conf 회복 시 자동 재개 (09:20부터 30분 간격 평가)
```

</details>

**WARNING — 태그 16종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 16440 | 09:01:42 | 12:28:18 | paintEvent slow 31.0ms | size=1886x916 candles=17 grid=15.0 spans=0.0 candles=16.0 dir=0.0 regime=0.0 markers=0.0 axes=0.0 cross=0.0 | slow_cnt=1 total_cnt=1 |
| `LiveDBG` | 31 | 08:41:19 | 12:28:04 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `SHAP` | 11 | 10:45:01 | 12:26:01 | 슬로우 감지 941ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림) |
| `PipePerf` | 10 | 09:01:01 | 11:52:02 | total=1241ms | S0=2ms S1=64ms S2=10ms S3=0ms S4=97ms S5=945ms S6=88ms S7=29ms S8=7ms |
| `Health` | 10 | 09:01:01 | 12:13:00 | level=WARNING degraded=OFF | latency=1241ms | quality=0.86 | cache_age=98s | exceptions_10m=0 |
| `CB⑤` | 10 | 09:01:01 | 11:52:02 | 파이프라인 1241ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `ScalerRefresh` | 9 | 09:22:00 | 12:23:01 | 5분 누적 수익률 +0.496% (임계 ±0.366%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `CB③-P4` | 8 | 10:16:00 | 12:23:01 | acc30m 단계 전환: NORMAL → RESTRICTED (acc=23.3%) |
| `SHS-EKS` | 7 | 09:05:00 | 11:29:00 | Early Kill Switch 발동 conf_max=34.4% < 발동선=39.9%(mc=41.9%-margin2.0%p) core_pass=0/5봉(측정 0봉) → 일시 관망 (09:20부터 30분 간격 자동 회복 평가, 마감 11:30) |
| `SessionBackfill` | 4 | 08:41:51 | 08:41:51 | OHLCV 불일치 ts=2026-09-14 10:51:00 cols=['open'] existing_source=rt |
| `HealthPolicy` | 3 | 10:42:00 | 11:53:00 | Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=1305ms quality=1.00 cache=0s exc10m=0) | cause=S4(610ms) |
| `출처축` | 2 | 08:41:21 | 08:41:21 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |

**채널** — `SYSTEM`×16542, `HEALTH`×10

**컴포넌트 상위 15** — `ChartDBG`×16440, `LiveDBG`×31, `SHAP`×11, `PipePerf`×10, `Health`×10, `CB⑤`×10, `ScalerRefresh`×9, `SHS-EKS`×8, `CB③-P4`×8, `SessionBackfill`×4, `HealthPolicy`×3, `출처축`×2, `SessionStateDrop`×2, `Contrarian`×2, `MainStallTrace`×1

### `logs/20260915_SYSTEM.log` — 426.0KB · 3161행 · 최종 12:27:00

- 형식 평문 · 시각 인식 3151행 · INFO=3151, PLAIN=10

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-15 08:40:34 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=24544 | 행감지=30s all_threads=True
2026-09-15 08:40:53 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-15 08:40:53 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-15 08:40:53 [INFO] SYSTEM: 미륵이 초기화
2026-09-15 08:40:53 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-09-14) 종가 버퍼 로드: 384봉
  …
2026-09-15 12:28:00 [INFO] SYSTEM: [BAR-CLOSE][CYBOS] ts=12:27 O=1046.40 H=1047.42 L=1046.38 C=1047.32 V=277
2026-09-15 12:28:00 [INFO] SYSTEM: [CVD-ANCHOR] ts=12:27 vol=277 | live_buy=197 shadow_buy=139 anchor_buy=139 | resid(anchor)=0 resid(shadow)=0 unknown_ticks=0 resets=0
2026-09-15 12:28:01 [INFO] SYSTEM: [S6Detail] ensemble=2ms checklist_pre=17ms meta_gate=10ms gates=0ms imp=0ms shap=1ms corr=6ms dash_ui=0ms tail=16ms
2026-09-15 12:28:01 [INFO] SYSTEM: [PipePerf][DBG] total=485ms | S0=3ms S1=55ms S2=24ms S3=0ms S4=73ms S5=250ms S6=53ms S7=22ms S8=5ms
2026-09-15 12:28:09 [INFO] SYSTEM: [TickUI] alive ticks=69545 code=A056A close=1047.22
```

</details>

**채널** — `SYSTEM`×3151

**컴포넌트 상위 15** — `CybosInvestorRaw`×826, `CybosRT-TICK`×700, `CybosRT-ROLLOVER`×223, `BAR-CLOSE`×223, `CVD-ANCHOR`×223, `TickUI`×222, `S6Detail`×209, `PipePerf`×209, `System`×59, `MicroRegime`×43, `RegimeFingerprint`×38, `OptionChain`×25, `CybosSub`×21, `IntradayRegime`×16, `SYSTEM`×9

### `logs/20260915_SIGNAL.log` — 267.0KB · 2433행 · 최종 12:27:00

- 형식 평문 · 시각 인식 2433행 · WARNING=826, INFO=1607

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-15 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.409
2026-09-15 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.401
2026-09-15 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.397
2026-09-15 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.405
2026-09-15 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.419
  …
2026-09-15 12:28:01 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m', '5m'] 중 미배포=['10m', '15m', '3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=None)
2026-09-15 12:28:01 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=NEUTRAL [WeightCollapse]
2026-09-15 12:28:01 [INFO] SIGNAL: [InstabilityGate] (섀도) 레짐전환 4회/10분 — 활성 시 min_conf +5%p 예상(미적용)
2026-09-15 12:28:01 [INFO] SIGNAL: 앙상블: dir=+0 conf=85.0% grade=X micro=추세장
2026-09-15 12:28:01 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: FLAT수렴
```

</details>

**WARNING — 태그 9종 (상위 9)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 546 | 09:00:02 | 12:23:02 | 1m 'macro_vix' scale=0.0340 → floor=0.10 적용 (z-score 폭발 방지) |
| `Checklist` | 69 | 09:11:00 | 12:06:01 | 신뢰도 미달 34.5% < 37.9% → 강제 X등급 |
| `Model` | 58 | 09:00:00 | 12:24:00 | 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 58 | 09:00:00 | 12:24:00 | ts=08:59 horizon=1m age=1m max_z=-13.03(institution_futures_net) extreme=1 adj=1 |
| `ScalerRefresh` | 48 | 08:45:21 | 08:59:00 | 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| `WeightCollapse` | 43 | 09:07:00 | 12:28:01 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ConstOut` | 2 | 09:54:00 | 10:59:00 | 5m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `ConfFloorGuard` | 1 | 09:00:00 | 09:00:00 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4190 (conf_floor=0.330, min_conf=0.419, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |
| `MetaGate` | 1 | 11:46:00 | 11:46:00 | meta_conf 5회 연속 과소 → 다음 배치 재학습 대기 (streak=5) |

**채널** — `SIGNAL`×2433

**컴포넌트 상위 15** — `ScalerFloor`×564, `SIGNAL`×418, `ZeroDiag`×209, `Ensemble`×207, `FQAdj`×206, `MetaGate`×175, `Model`×70, `ScalerRefresh`×69, `Checklist`×69, `ATR-Horizon`×64, `SHS-EKS`×64, `ScalerMonitor`×58, `MicroRegime`×43, `WeightCollapse`×43, `차단`×38

### `logs/20260915_LEARNING.log` — 181.4KB · 1677행 · 최종 12:27:00

- 형식 평문 · 시각 인식 1677행 · WARNING=161, INFO=1516

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-15 08:40:55 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-15 08:40:58 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00152 auc=0.458 out_max=0.3632 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
2026-09-15 08:40:58 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00199 auc=0.409 out_max=0.3509 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과
2026-09-15 08:40:58 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00014 auc=0.532 out_max=0.2763 (n=105) → 보정 재적용
2026-09-15 08:40:58 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2763 < conf_floor=0.3300 (span=0.00014 auc=0.532 out_max=0.2763, 기저율=0.2762 n=105) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
  …
2026-09-15 12:28:00 [INFO] LEARNING: ✗ 30m 예측 실패 (conf=51.2% 예측=UP 실제=DN)
2026-09-15 12:28:00 [INFO] LEARNING: [Bias⚠] 1m 적중=33%(15/45) UP=13 DN=1 FL=31 [FL편향⚠ 69%]
2026-09-15 12:28:00 [INFO] LEARNING: [Bias⚠] 3m 적중=23%(7/30) UP=2 DN=8 FL=20 [FL편향⚠ 67%]
2026-09-15 12:28:00 [INFO] LEARNING: [Bias⚠] 5m 적중=43%(13/30) UP=1 DN=7 FL=22 [FL편향⚠ 73%]
2026-09-15 12:28:01 [INFO] LEARNING: [SGD] 2건 학습 | SGD비중=30% 50분정확도=0.0%
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 161 | 08:40:58 | 11:48:00 | 축퇴 감지 — span=0.00152 auc=0.458 out_max=0.3632 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과 |

**채널** — `LEARNING`×1677

**컴포넌트 상위 15** — `LEARNING`×662, `Calibration`×315, `SGD`×209, `sigma`×196, `Bias`×90, `Bias⚠`×72, `OnlineLearner`×45, `MetaConf`×41, `ScalerWarmup`×21, `BiasReset`×8, `SHAP`×6, `RF`×2, `ExtremityCorrector`×2, `Consolidator`×2, `GBM-64`×2

### `logs/20260915_HEALTH.log` — 3.1KB · 21행 · 최종 12:14:01

- 형식 평문 · 시각 인식 21행 · WARNING=10, INFO=11

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-15 09:01:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1241ms | quality=0.86 | cache_age=98s | exceptions_10m=0
2026-09-15 09:02:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=854ms | quality=0.74 | cache_age=158s | exceptions_10m=0
2026-09-15 09:08:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1009ms | quality=1.00 | cache_age=149s | exceptions_10m=2 | exc_tags=[SHS-EKS]×2
2026-09-15 09:09:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=495ms | quality=1.00 | cache_age=24s | exceptions_10m=2 | exc_tags=[SHS-EKS]×2
2026-09-15 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 348ms (표본 20분)
  …
2026-09-15 11:31:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=349ms | quality=1.00 | cache_age=57s | exceptions_10m=2 | exc_tags=[SHAP]×2
2026-09-15 11:52:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1929ms | quality=1.00 | cache_age=29s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-09-15 11:53:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=362ms | quality=1.00 | cache_age=88s | exceptions_10m=2 | exc_tags=[SHAP]×2
2026-09-15 12:13:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=367ms | quality=1.00 | cache_age=182s | exceptions_10m=2 | exc_tags=[SHAP]×2
2026-09-15 12:14:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=438ms | quality=1.00 | cache_age=57s | exceptions_10m=1 | exc_tags=[SHAP]×1
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 10 | 09:01:01 | 12:13:00 | level=WARNING degraded=OFF | latency=1241ms | quality=0.86 | cache_age=98s | exceptions_10m=0 |

**채널** — `HEALTH`×21

**컴포넌트 상위 15** — `Health`×20, `HealthTrend`×1

### `logs/retrain_intraday_20260915_110001.log` — 3.2KB · 24행 · 최종 11:00:18

- 형식 평문 · 시각 인식 24행 · WARNING=2, INFO=22

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-15 11:00:01,094 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-15 11:00:01,095 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-09-15 11:00:01,095 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-15 11:00:01,095 [INFO] RETRAIN_INTRADAY: [DLL] BLAS 경로 이미 충족
2026-09-15 11:00:01,095 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_63bd0243.json
  …
2026-09-15 11:00:18,838 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-09-15 11:00:18,840 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-09-15 11:00:18,840 [INFO] LEARNING: [Retrain] 완료 | 14.6초 | 성공=1/1 호라이즌
2026-09-15 11:00:18,840 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 17.7s 데이터=4800행
2026-09-15 11:00:18,842 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_63bd0243.json
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `BackfillFilter` | 1 | 11:00:10 | 11:00:10 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 27597/45614 제외 (418차 결정 1) — 남은 18017행 |
| `UnitMismatch` | 1 | 11:00:10 | 11:00:10 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/18017행 제외 (559차 P1'-2) — 남은 16571행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |

**채널** — `LEARNING`×14, `RETRAIN_INTRADAY`×7, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×12, `RETRAIN_INTRADAY`×6, `DLL`×1, `BackfillFilter`×1, `UnitMismatch`×1, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

### `logs/20260915_MICRO.log` — 545.1KB · 1461행 · 최종 12:27:05

- 형식 평문 · 시각 인식 1461행 · DEBUG=1461

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-15 08:45:22 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1041.00/4 ask1=1041.24/1 mp={'microprice_tick': 1041.192, 'midprice_tick': 1041.12, 'depth_bias_tick': -0.0901} mlofi_tick=None queue=None
2026-09-15 08:45:22 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1041.00/3 ask1=1041.24/1 mp={'microprice_tick': 1041.18, 'midprice_tick': 1041.12, 'depth_bias_tick': -0.1723} mlofi_tick=-1.0 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': 0.…
2026-09-15 08:45:22 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1041.00/3 ask1=1041.24/1 mp={'microprice_tick': 1041.18, 'midprice_tick': 1041.12, 'depth_bias_tick': -0.0491} mlofi_tick=-5.05 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
2026-09-15 08:45:22 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1041.00/2 ask1=1041.24/1 mp={'microprice_tick': 1041.16, 'midprice_tick': 1041.12, 'depth_bias_tick': -0.1487} mlofi_tick=-1.0 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': 0.…
2026-09-15 08:45:22 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1041.00/2 ask1=1041.24/1 mp={'microprice_tick': 1041.16, 'midprice_tick': 1041.12, 'depth_bias_tick': 0.0034} mlofi_tick=-4.4333 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
  …
2026-09-15 12:27:32 [DEBUG] MICRO: [MICRO-TICK] #121500 bid1=1047.14/3 ask1=1047.18/2 mp={'microprice_tick': 1047.164, 'midprice_tick': 1047.16, 'depth_bias_tick': 0.0462} mlofi_tick=0.0 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio…
2026-09-15 12:27:45 [DEBUG] MICRO: [MICRO-TICK] #121600 bid1=1047.26/1 ask1=1047.30/1 mp={'microprice_tick': 1047.28, 'midprice_tick': 1047.28, 'depth_bias_tick': -0.0484} mlofi_tick=-0.5 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_rati…
2026-09-15 12:27:59 [DEBUG] MICRO: [MICRO-TICK] #121700 bid1=1047.30/2 ask1=1047.36/1 mp={'microprice_tick': 1047.34, 'midprice_tick': 1047.33, 'depth_bias_tick': 0.4751} mlofi_tick=0.0 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
2026-09-15 12:28:00 [DEBUG] MICRO: [MICRO-MINUTE] #223 ts=2026-09-15 12:27:00 close=1047.32 bias=0.000979 slope=-0.429880 depth_bias=0.0929 mlofi_norm=0.041415 mlofi_pressure=1 mlofi_slope=47.505000 queue_signal=-0.0131 queue_ma=-0.0310 queue_momentum=0.0544 depletion=0.5000 refill=0.5000 imbalance…
2026-09-15 12:28:11 [DEBUG] MICRO: [MICRO-TICK] #121800 bid1=1047.18/1 ask1=1047.28/2 mp={'microprice_tick': 1047.2134, 'midprice_tick': 1047.23, 'depth_bias_tick': 0.1492} mlofi_tick=8.1833 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 1.0, 'bid_cancel_add_ra…
```

</details>

**채널** — `MICRO`×1461

**컴포넌트 상위 15** — `MICRO-TICK`×1238, `MICRO-MINUTE`×223

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 0 |
| 진입 등록(`[Position] 진입`) — **엔진** | 0 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 0 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 0 |
| 차단(`[차단]`) | 38 |
| 사이저 호출(`[Sizer]`) | 0 |

### 차단 사유 38건 · 9종

| 건수 | 사유 |
|---|---|
| 28 | SHS-EKS 당일 관망 활성 — z경고11개+conf34%미달 |
| 3 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 9.8pt > ATR×5.0=8.0pt (시가=1039.48 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 10.3pt > ATR×5.0=7.8pt (시가=1039.48 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 11.9pt > ATR×5.0=6.7pt (시가=1039.48 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 11.1pt > ATR×5.0=6.7pt (시가=1039.48 반등위험) |
| 1 | ATR 0.92pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.91pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.95pt < 1.0pt — 변동성 부족 (휩쏘 위험) |

### 메인 스레드 블로킹 22건 · 최대 6047ms · 5초 초과 1건

상위 — 6047ms, 4719ms, 4547ms, 4437ms, 4343ms, 3953ms, 3687ms, 3656ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 08:41:25 | 6047ms | **미측정** | — |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260915_WARN.log`
```
--- ConstOut ×1(표본)
10:59:00 2026-09-15 10:59:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작 | bias_override=N gbm_raw(3m=0.3623)
--- Traceback ×1(표본)
08:41:25 2026-09-15 08:41:25 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260915.log
--- [SHAP] 슬로우 ×8(표본)
10:45:01 2026-09-15 10:45:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 941ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
10:56:01 2026-09-15 10:56:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 983ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
11:22:01 2026-09-15 11:22:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 926ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
11:30:01 2026-09-15 11:30:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1088ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×8(표본)
08:41:25 2026-09-15 08:41:25 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 6047ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=6047 band=WARN since_pipe_s=NA
09:00:04 2026-09-15 09:00:04 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4719ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4719 band=INFO since_pipe_s=0.1
09:01:02 2026-09-15 09:01:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2391ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2391 band=INFO since_pipe_s=0.1
09:01:46 2026-09-15 09:01:46 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4547ms — 메인 스레드 블로킹 발생 | pipe_elapsed=41 watchdog_alerted=[] | [MainStall] stall_ms=4547 band=INFO since_pipe_s=44.3
```

### `logs/20260915_SYSTEM.log`
```
--- ConstOut ×7(표본)
09:54:00 2026-09-15 09:54:00 [INFO] SYSTEM: [ConstOut] 5m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.6488) | 앙상블 제외는 유지
10:59:00 2026-09-15 10:59:00 [INFO] SYSTEM: [ConstOut] heavy cooldown armed until 11:01:00 (const_output)
10:59:00 2026-09-15 10:59:00 [INFO] SYSTEM: [ConstOut][Worker] 시작 hz=['3m']
10:59:00 2026-09-15 10:59:00 [INFO] SYSTEM: [ConstOut][Worker] 완료 hz=['3m'] load=121ms fit=53ms total=177ms
--- PSI ×8(표본)
09:00:00 2026-09-15 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.002 level=0 (heartbeat)
09:05:00 2026-09-15 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.002 level=0 (heartbeat)
09:11:00 2026-09-15 09:11:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.002 level=0 (heartbeat)
09:17:00 2026-09-15 09:17:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.002 level=0 (heartbeat)
```

### `logs/20260915_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
09:00:00 2026-09-15 09:00:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4190 (conf_floor=0.330, min_conf=0.419, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- ConstOut ×4(표본)
09:54:00 2026-09-15 09:54:00 [WARNING] SIGNAL: [ConstOut] 5m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
09:56:00 2026-09-15 09:56:00 [INFO] SIGNAL: [ConstOut] 5m 상수 출력 해소 → 앙상블 복귀
10:59:00 2026-09-15 10:59:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+0) → 앙상블 제외
11:01:03 2026-09-15 11:01:03 [INFO] SIGNAL: [ConstOut] 3m 상수 출력 해소 → 앙상블 복귀
--- WeightCollapse ×8(표본)
09:07:00 2026-09-15 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.3% grade=X regime=NEUTRAL [WeightCollapse]
09:10:00 2026-09-15 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=34.9% grade=X regime=NEUTRAL [WeightCollapse]
09:13:00 2026-09-15 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=34.9% grade=X regime=NEUTRAL [WeightCollapse]
09:16:00 2026-09-15 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.3% grade=X regime=NEUTRAL [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:31 2026-09-15 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.409
08:40:31 2026-09-15 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.401
08:40:31 2026-09-15 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.397
08:40:31 2026-09-15 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.405
--- 안전망 ×8(표본)
09:07:00 2026-09-15 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-09-15 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-09-15 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-09-15 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
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
| 09:00 | 정규장 개장 · 매분 루프 시작 | 14 | 09:00:04 [WARNING] _tick_header 간격 4719ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4719 band=… |
| 10:00 | 장중 초반 | 1558 | 09:54:00 [WARNING] paintEvent slow 47.0ms | size=1533x900 candles=56 grid=16.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=… |
| 12:00 | 장중 중간점 | 1084 | 11:54:01 [WARNING] paintEvent slow 47.0ms | size=1533x900 candles=56 grid=16.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=… |

- 이 로그 생존구간: 08:41 ~ 12:28

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260915_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 92 | 08:40:34 [INFO] 활성화 | file=logs\crash_fault.log PID=24544 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 136 | 08:49:01 [INFO] code=A056A from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 187 | 08:54:00 [INFO] code=A056A from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 194 | 09:54:00 [INFO] code=A056A from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 173 | 11:54:01 [INFO] code=A056A from=11:53 to=11:54 |
| 14:00 | _장중 후반 · 장중 재학습 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 12:28

**매분 루프 커버리지 09:00~15:10: 209/371분 (56.3%)**

연속 3분 이상 기록 없는 구간 1개:

| 시작 | 끝 | 분 |
|---|---|---|
| 12:29 | 15:10 | 162 |

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260915_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 62 | 08:45:21 [WARNING] 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 87 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0320) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 158 | 08:55:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0308) → identity(0,1) 강제 (FLAT 100% 방지) |
| 10:00 | 장중 초반 | 146 | 09:54:00 [WARNING] 5m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| 12:00 | 장중 중간점 | 176 | 11:56:00 [WARNING] 신뢰도 미달 34.7% < 62.0% → 강제 X등급 |

- 이 로그 생존구간: 08:40 ~ 12:28

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
| **오늘 20260915** | **12:28** | 로그 본문 |

- 델타 **-192분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.0MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-15 (MW0601 568차 — 장전 점검)
### 증상
### 원인
### 결정
### Why
### How to apply
### 검증
### 병행 세션
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
d_20260914.log:264-265` "[P8] session_state
  p8_last_success_date + eod_retrain_ok_date 기록 완료", 완료 마커 파일
  `data/eod_retrain_done_20260914.txt` 존재, `phase2_fallback: true`).
  즉 09-15 아침 소실은 EOD 실패의 결과가 아니라 위 구조적 코드 결함의 발현.

### 결정

- ↩️ **09-14 장후(563차) 판정 정정**: 그 세션은 "1-1([SessionStateDrop])·O-p3는
  오늘 원인이 다름(EOD 실패로 인한 결과)"이라며 09-14 발생분을 "5거래일 연속
  재현" 집계에서 제외했다. 오늘 증거로 그 전제(EOD 실패)가 틀렸음이 확인됐으므로
  **09-14도 포함해 재현 일수를 다시 센다.** 로그 실측: `SessionStateDrop`
  발생일 = 09-08·09-09·09-10·09-11·(주말)·09-14·09-15 = **6거래일 연속**
  (09-07은 0건 — `grep -c SessionStateDrop logs/2026090[7-9]_WARN.log
  logs/2026091[0-5]_WARN.log` 실측).
  09-14 563차 절 본문은 고치지 않는다 — 정정은 이 항목에 남긴다(append 규약).
- F-1(538차/538-4, "승인 재요청" 상태) — **신규 Fix 아님, 기존 항목에 증거
  보강**. 코드 변경은 이번 세션에서 하지 않았다(장전 규약).
- 오늘 아침 실제 동작 영향은 없었음을 확인 — `main.py:6120` 이하의 완료 마커
  파일(`eod_retrain_done_{d}.txt`) 직접 확인 폴백이 정상 작동해 08:55
  `[PreRetrain]` 스킵이 정상적으로 이뤄짐(`logs/20260915_SYSTEM.log:158-159`).
  단, `p8_last_success_date`를 쓰는 `main.py:9049` EKS 원인 분류 경로는
  이런 폴백이 없어 canary 노후 시 오판 위험이 남는다(오늘은 미발동, 실측 영향 없음).
- 그 외 신규 이상점 없음. `[CybosProbe]` 10건(F-3, 0819 종결)·
  `joblib=1.1.0`(491차 기지)·`[ConfFloorGuard]` 09:00:00 1회(09-14와 동일
  패턴, 지속 확인만)는 전부 기존 등록 사안이라 재상정하지 않음(함정①).
  수집기 `git diff` 실패(실질 변경 미측정, 미커밋 640건)도 기존 TODO
  544-6/549-4 재현으로 처리.

### Why

- 함정①(이미 반영된 것 재상정 금지) 준수 — F-1을 새 Fix로 올리지 않고 기존
  538-4에 증거만 첨부. CybosProbe·joblib 버전차·ConfFloorGuard 패턴도 grep으로
  기존 등록 확인 후 "이미 반영된 사안"/"확인 필요"로 분류.
- 계측 4원칙 ④(폴백 가시화)의 반대 방향 사례로 등록 — "정상 성공"이 다음날
  "실패처럼 보이는" 왜곡. 정상값이 폴백값처럼 보이는 것도 같은 계열의 위험.

### How to apply

- 이번 세션은 코드를 변경하지 않았다(장전 규약 — 라이브 프로세스 가동 중).
  F-1(538-4) 적용 승인 시 다음 장후 세션에서
  `strategy/runtime/session_recovery_service.py:increment_session()`에
  `_MARKER_KEYS` 이어받기 로직 추가 예정.

### 검증

- `logs/retrain_eod_20260914.log` 전문 확인으로 09-14 EOD 성공 사실 직접 확인.
- `strategy/runtime/session_recovery_service.py` 코드 직접 읽어 소실 메커니즘
  확정(가설 아님).
- `logs/20260907_WARN.log` ~ `logs/20260915_WARN.log` 전수 grep으로 6거래일
  연속 재현 실측.
- `main.py` 마커 소비처 3곳(6103·9049·12919행) grep으로 전수 확인, 폴백
  경로(6120행 이하) 정상 작동을 오늘 로그로 재확인.

### 병행 세션

- 이 세션 시작 시 당일(2026-09-15 00:00~) 커밋 0건 확인, 병행 산출물 없음.
  `.git/index.lock` 없음(`git_lock_guard.py --check` rc=0, "정상 — 락 없음").
  모든 git 조회는 `--no-optional-locks` 사용.

산출물: `docs/정기점검/매일점검/MW0601-20260915-점검리포트.md`(장전 절 신규
생성), `docs/정기점검/매일점검/evidence_MW0601-20260915_pre.md`(수집기 자동
생성). 커밋 대기: 위 2개 파일 + `dev_memory/DECISION_LOG.md`·`NEXT_TODO.md`
(경로 명시 add 필요 — `git add .` 금지, 640건 대부분 EOL 파생 혼입 주의).

```

</details>

### dev_memory/NEXT_TODO.md — 1.5MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-11 (MW0601 557차 후속 — 장중 점검)
## 2026-09-11 (MW0601 558차 후속 — 장후 자동조치)
### 이월·승인 대기 (자동조치 범위 밖 — 변경 없음)
### 다음 세션 관측
## 2026-09-14 (MW0601 560차 — 장전 점검)
## 2026-09-14 (MW0601 562차 — 장중 점검)
## 2026-09-14 (MW0601 563차 — 장후 점검, 종합 완성본)
## 2026-09-15 (MW0601 568차 — 장전 점검)
```

미완료 체크박스 **2670건** (끝에서 30건)
```
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
- [ ] 🔴 **F-1 (538-4) — 오늘 증거 보강, 승인 대기 지속.** `session_recovery_service.py:
- [ ] ↩️ **09-14 563차 판정 정정** — "SessionStateDrop 09-14 발생분은 EOD 실패 결과라 5거래일
- [ ] **G-1 (P2, 신규)** `_log_session_rollover()` 경고 로그에 `eod_retrain_done_{prev_date}.txt`
- [ ] 신규 Fix/고도화 없음 — 그 외는 전부 기존 등록 사안 재확인만: `[CybosProbe]` 10건(F-3,
- [ ] **O-p1 (다음 거래일 09-16 장전 판정)** `[SessionStateDrop]` 09-16 아침 재현 여부
- [ ] **O-p2 (다음 장후 판정)** 08:41:25 메인 스레드 블로킹 6047ms가 개장 준비 시간대
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
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

## 2026-09-15 (MW0601 568차 — 장전 점검)

- [ ] 🔴 **F-1 (538-4) — 오늘 증거 보강, 승인 대기 지속.** `session_recovery_service.py:
      increment_session()` 날짜 전환 시 EOD/P8 완료 마커(`p8_last_success_date`·
      `eod_retrain_ok_date`) 이어받기. 오늘 09-14 EOD 성공(`logs/retrain_eod_20260914.log`
      17:15:37 확인) 뒤에도 09-15 아침 마커가 소실됨을 확인해, 이 결함이 "EOD 실패 시에만"이
      아니라 **날짜 전환마다 항상 발생**하는 구조적 문제임을 코드로 확정(`increment_session`이
      새 딕셔너리를 5개 키로만 구성). 근거: `docs/정기점검/매일점검/MW0601-20260915-점검리포트.md`
      이상점 1-1.
- [ ] ↩️ **09-14 563차 판정 정정** — "SessionStateDrop 09-14 발생분은 EOD 실패 결과라 5거래일
      연속 재현 집계에서 제외" 판정은 전제가 틀렸다(09-14 EOD는 성공했다). 재현일 재계산:
      09-08·09-09·09-10·09-11·09-14·09-15 = 6거래일 연속(09-07 0건). 09-14 절 본문은 수정하지
      않음(append 규약), 정정은 09-15 DECISION_LOG 항목에 기록.
- [ ] **G-1 (P2, 신규)** `_log_session_rollover()` 경고 로그에 `eod_retrain_done_{prev_date}.txt`
      존재 여부(=전날 EOD 성공 여부)를 함께 찍어, 다음에 같은 경고가 뜰 때 "구조적 버그 때문인지
      진짜 EOD 실패 때문인지"를 로그 한 줄로 즉시 구분 가능하게 한다. F-1과 독립 적용 가능.
- [ ] 신규 Fix/고도화 없음 — 그 외는 전부 기존 등록 사안 재확인만: `[CybosProbe]` 10건(F-3,
      0819 종결, 재상정 금지), `joblib=1.1.0` vs 문서 1.1.1(491차 기지), `[ConfFloorGuard]`
      09:00:00 1회(09-14와 동일 패턴, 09-14 563차가 이미 지속-종결 판정), 수집기 `git diff`
      실패·미커밋 640건 실질변경 미측정(기존 544-6/549-4 재현).
- [ ] **O-p1 (다음 거래일 09-16 장전 판정)** `[SessionStateDrop]` 09-16 아침 재현 여부
      (F-1 미적용 유지 시 재현 확실시 — 구조적 버그이므로). 재현되면 "7거래일 연속"으로 갱신.
- [ ] **O-p2 (다음 장후 판정)** 08:41:25 메인 스레드 블로킹 6047ms가 개장 준비 시간대
      (08:40~08:42)의 정상 패턴인지 — 최근 5거래일 같은 시간대 블로킹 분포와 비교 필요
      (이번 세션은 시간 관계상 비교하지 않음). 482차 F-3 섀도 계측 대상 구간.

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

### `data/heartbeat_MW0601_20260915.json` — 244B · 09-15 12:26:59
```json
{
 "pid": 24544,
 "written_at": "2026-09-15T12:27:59",
 "beat_epoch": 1789442876.739831,
 "beat_age_sec": 2.5,
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

- 파일 최종 기록: **09-15 11:01:02**

| 키 | 값 | 수집 대상일(2026-09-15)과 일치 |
|---|---|---|
| `date` | 2026-09-15 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 138개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260915-점검리포트.md` | 24.8KB | 09-15 09:12 |
| `docs/정기점검/매일점검/evidence_MW0601-20260915_pre.md` | 55.3KB | 09-15 09:02 |
| `docs/정기점검/매일점검/MW0601-20260914-3m호라이즌_ConstOut루프-딥다이브.md` | 28.7KB | 09-14 16:51 |
| `docs/정기점검/매일점검/MW0601-20260914-점검리포트.md` | 77.8KB | 09-14 16:29 |
| `docs/정기점검/매일점검/evidence_MW0601-20260914_post.md` | 77.8KB | 09-14 16:19 |
| `docs/정기점검/매일점검/evidence_MW0601-20260914_intra.md` | 65.8KB | 09-14 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20260914_pre.md` | 51.2KB | 09-14 09:01 |
| `docs/정기점검/매일점검/MW0601-20260911-점검리포트.md` | 70.1KB | 09-11 17:37 |

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

1. `logs/20260915_WARN.log`: ERROR 이상 1건
2. `logs/20260915_WARN.log`: **Traceback** 출현 1건 — 크래시/메모리 계열
3. `logs/20260915_SYSTEM.log`: 매분 루프 커버리지 209/371분 (56.3%) — 루프가 빠진 구간이 있다
4. `logs/20260915_SYSTEM.log`: 12:29~15:10 **연속 162분 매분 루프 기록 없음**
5. 메인 스레드 정지 5초 초과 **1건** (최대 6047ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
6. `logs/20260915_WARN.log`: **ConstOut** 1건(표본)
7. `logs/20260915_SYSTEM.log`: **ConstOut** 7건(표본)
8. `logs/20260915_SIGNAL.log`: **WeightCollapse** 8건(표본)
9. `logs/20260915_SIGNAL.log`: **ConstOut** 4건(표본)
10. `logs/20260915_LEARNING.log`: **축퇴** 8건(표본)
11. 미커밋 변경 644건 — **실질 변경 미측정**(git diff 실패). 원시 건수만으로는 착시인지 알 수 없다

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260915*.log` (Windows) / `grep 강제청산 logs/*20260915*.log`*