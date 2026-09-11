# 미륵이 증거 다이제스트 — 2026-09-11 / PRE

- 생성 2026-09-11 09:01:16 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/eager-intelligent-noether/mnt/futures`
- 점검 범위: pre (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260911` · `2026-09-11` · `260911` · `0911`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **16개** 파일 · 16개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260911.log` | 125B | 09-11 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260911.log` | 139B | 09-11 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260911.json` | 243B | 09-11 09:01 |
| `launcher_{DATE}_084001_23715.log` | 1 | `logs/Mireuk_batch/launcher_20260911_084001_23715.log` | 65.7KB | 09-11 09:01 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260911.log` | 2.9KB | 09-11 09:00 |
| `{DATE}_DATA.log` | 1 | `logs/20260911_DATA.log` | 1.3KB | 09-11 09:01 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260911_DEBUG.log` | 1.1KB | 09-11 09:01 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260911_HEALTH.log` | 277B | 09-11 09:01 |
| `{DATE}_HOGA.log` | 1 | `logs/20260911_HOGA.log` | 1.6MB | 09-11 09:01 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260911_LEARNING.log` | 60.6KB | 09-11 09:01 |
| `{DATE}_MICRO.log` | 1 | `logs/20260911_MICRO.log` | 38.2KB | 09-11 09:01 |
| `{DATE}_PROBE.log` | 1 | `logs/20260911_PROBE.log` | 1.7KB | 09-11 08:58 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260911_SIGNAL.log` | 27.0KB | 09-11 09:01 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260911_SYSTEM.log` | 29.7KB | 09-11 09:01 |
| `{DATE}_TRADE.log` | 1 | `logs/20260911_TRADE.log` | 167B | 09-11 08:41 |
| `{DATE}_WARN.log` | 1 | `logs/20260911_WARN.log` | 3.8KB | 09-11 09:01 |

## 2. 코드·커밋 상태

- HEAD `ac042a0` · 브랜치 `v9-dev` · 미커밋 557건 · 실질 변경 **미측정**(git diff 실패) · 인덱스락 없음
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
```
M .claude/commands/dailycheck.md
 M .claude/skills/mireuk-daily-check/config_dailycheck_targets.json
 M .claude/skills/mireuk-daily-check/references/invariants.md
 M .claude/skills/mireuk-daily-check/references/phases.md
 M .claude/skills/mireuk-daily-check/references/postmortem.md
 M .claude/skills/mireuk-daily-check/references/report_template.md
 M .gitignore
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
 M collection/kiwoom/api_connector.py
 M collection/kiwoom/investor_data.py
 M collection/macro/macro_fetcher.py
 M collection/macro/micro_regime.py
 M collection/options/pcr_store.py
 M collection/provenance.py
 M config/capital.py
 M config/dailycheck_targets.json
 M config/krx_holidays.py
 M config/secrets_example.py
 M config/settings.py
 M config/strategy_params.py
 M config/strategy_registry.py
 M dashboard/main_dashboard.py
… 외 517건
```

**당일(2026-09-11) 커밋**
```
(당일 커밋 없음 — 커밋 가능 상태였음)
```

**최근 커밋 12건**
```
ac042a0 [MW0601] 556차 후속: 장후 자동조치 기록 — 리포트 제4부 + dev_memory + 09-09·09-10 점검 산출물
5f8e40e [MW0601] 556차 후속: 장후 자동조치 — F-5(Armistice 고착 오탐)·G-4(래치 스냅샷)·G-1(상태파일 회전)
da66651 [MW0601] 555차 후속2: 출처축(P0)·차트 Y축(P1)·라벨 레지스트리(P2) + GP 마커 재지정
106f6e2 [MW0601] 555차 병합: GP 청산 패널 갱신 트리거 + 출처축 화이트리스트
c08128f [MW0601] 555차 후속: 손익 추이 「출처」축을 화이트리스트로 뒤집음 — 모르는 라벨은 auto 가 아니다
c91d591 [MW0601] 555차: GP 가상 청산이 손익 추이 패널을 갱신하지 않던 결함 — run_shadow 반환값 신설
bd33401 [MW0601] 554차: 테스트가 심은 유령 포지션 — 격리 2겹 + 복원 가드 + 대조 축 분리
f6ac416 [MW0601] 553차 후속4: GP 병행운용 Phase 4 — 수익 판넬 「GP(가상)」 구분
fec531c [MW0601] 553차 후속3: GP 병행운용 Phase 3 — 도전자 2종 배선 + 관측 개시(2026-09-10)
c384f8c [MW0601] 553차 후속2: ma_basis=cont 확정 + GP 병행운용 Phase 2(엔진 결함 5건)
a791389 [MW0601] 553차 후속: GP 병행운용 Phase 1 — MA20/MA60 배선 + 죽은 지표 교체
70ebd33 [MW0601] 553차: GP 규칙 병행운용 Phase 0 — 사전등록(비용 CYBOS·CREON 분리) + 차트 GP 마커
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

_본문 미열람(설정): `20260911_HOGA.log` 1.6MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/14개 (중요도순). 제외: `20260911_PROBE.log`, `launcher_20260911_084001_23715.log`, `20260911_DEBUG.log`, `mainstall_traceback_20260911.log`, `freeze_sentinel_20260911.log`, `force_flat_guard_20260911.log`_

### `logs/20260911_TRADE.log` — 167B · 2행 · 최종 08:41:05

- 형식 평문 · 시각 인식 2행 · INFO=2

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-11 08:40:59 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-11 08:41:05 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
  …
2026-09-11 08:40:59 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-11 08:41:05 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×2

**컴포넌트 상위 15** — `Position`×1, `ProfitGuard`×1

### `logs/20260911_WARN.log` — 3.8KB · 28행 · 최종 09:01:00

- 형식 평문 · 시각 인식 28행 · WARNING=28

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-11 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-11 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 15ms
2026-09-11 08:41:10 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 2031ms account=333044256
2026-09-11 08:41:10 [WARNING] SYSTEM: [LiveDBG] _ts_sync_position_from_broker BlockRequest 2034ms — 메인 스레드 2034ms 점유
2026-09-11 08:41:10 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-09-11 09:02:01 [WARNING] SYSTEM: [PipePerf] total=1264ms | S0=2ms S1=18ms S2=7ms S3=0ms S4=99ms S5=891ms S6=152ms S7=90ms S8=4ms
2026-09-11 09:02:01 [WARNING] SYSTEM: [PipePerf] total=1264ms | S0=2ms S1=18ms S2=7ms S3=0ms S4=99ms S5=891ms S6=152ms S7=90ms S8=4ms
2026-09-11 09:02:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1264ms | quality=0.74 | cache_age=153s | exceptions_10m=0
2026-09-11 09:02:01 [WARNING] SYSTEM: [CB⑤] 파이프라인 1264ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s]
2026-09-11 09:02:01 [WARNING] SYSTEM: [CB⑤] 파이프라인 1264ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s]
```

</details>

**WARNING — 태그 9종 (상위 9)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 10 | 08:41:08 | 09:00:05 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `PipePerf` | 4 | 09:00:01 | 09:02:01 | total=1810ms | S0=5ms S1=15ms S2=0ms S3=0ms S4=121ms S5=908ms S6=734ms S7=18ms S8=9ms |
| `CB⑤` | 4 | 09:00:02 | 09:02:01 | 파이프라인 1810ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `출처축` | 2 | 08:41:10 | 08:41:10 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |
| `SessionStateDrop` | 2 | 08:41:10 | 08:41:10 | 완료 마커 소실 ['p8_last_success_date', 'eod_retrain_ok_date'] — 날짜 전환(2026-09-10 → 2026-09-11)이 새 딕셔너리를 만들면서 이어받지 않았다 (호출부=session_recovery_service.py:increment_session). F-1 미적용 상태에서는 이것이 현재 동작이며, 이 줄의 출현 자체가 0907 리포트 이상점 1-4(판정 근거 정합성)의 확인 수단… |
| `Canary` | 2 | 08:55:10 | 08:55:10 | scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| `Health` | 2 | 09:00:01 | 09:02:01 | level=WARNING degraded=OFF | latency=1810ms | quality=0.86 | cache_age=34s | exceptions_10m=0 |
| `MainStallTrace` | 1 | 09:00:05 | 09:00:05 | 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260911.log |
| `HealthPolicy` | 1 | 09:01:00 | 09:01:00 | Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=1810ms quality=0.86 cache=0s exc10m=0) | cause=S5(908ms) |

**채널** — `SYSTEM`×26, `HEALTH`×2

**컴포넌트 상위 15** — `LiveDBG`×10, `PipePerf`×4, `CB⑤`×4, `출처축`×2, `SessionStateDrop`×2, `Canary`×2, `Health`×2, `MainStallTrace`×1, `HealthPolicy`×1

### `logs/20260911_SYSTEM.log` — 29.7KB · 251행 · 최종 09:01:11

- 형식 평문 · 시각 인식 244행 · INFO=244, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-11 08:40:33 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=6780 | 행감지=30s all_threads=True
2026-09-11 08:40:49 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-11 08:40:49 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-11 08:40:49 [INFO] SYSTEM: 미륵이 초기화
2026-09-11 08:40:49 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-09-10) 종가 버퍼 로드: 383봉
  …
2026-09-11 09:02:10 [INFO] SYSTEM: [ProgramRaw] raw_program_trade 보존 시작 — ts=2026-09-11 09:02:00 필드 56개 (세션 1회 로그)
2026-09-11 09:02:10 [INFO] SYSTEM: [CybosRT-TICK] #3500 code=A056A raw_time=90210 parsed=09:02:10 price=1070.60 vol=1 bid1=1070.50 ask1=1070.62 flag=49 side=BUY anchor=1/0
2026-09-11 09:02:17 [INFO] SYSTEM: [CybosRT-TICK] #3600 code=A056A raw_time=90217 parsed=09:02:17 price=1071.82 vol=1 bid1=1071.80 ask1=1071.86 flag=50 side=SELL anchor=0/1
2026-09-11 09:02:23 [INFO] SYSTEM: [TickUI] alive ticks=3676 code=A056A close=1072.06
2026-09-11 09:02:25 [INFO] SYSTEM: [CybosRT-TICK] #3700 code=A056A raw_time=90225 parsed=09:02:25 price=1071.58 vol=2 bid1=1071.48 ask1=1071.56 flag=49 side=BUY anchor=2/0
```

</details>

**채널** — `SYSTEM`×244

**컴포넌트 상위 15** — `CybosRT-TICK`×42, `CybosSub`×21, `System`×18, `TickUI`×18, `CybosRT-ROLLOVER`×17, `BAR-CLOSE`×17, `CVD-ANCHOR`×17, `SYSTEM`×9, `PreMarket`×9, `CybosRT-START`×6, `CybosInvestorRaw`×6, `Notify`×5, `BrokerSync`×4, `BalanceUI`×4, `-`×4

### `logs/20260911_SIGNAL.log` — 27.0KB · 272행 · 최종 09:01:00

- 형식 평문 · 시각 인식 272행 · WARNING=145, INFO=127

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-11 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.415
2026-09-11 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.429
2026-09-11 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.408
2026-09-11 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.404
2026-09-11 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.412
  …
2026-09-11 09:02:01 [WARNING] SIGNAL: [ScalerFloor] 30m 'macro_us10y_chg' scale=0.0745 → floor=0.25 적용 (z-score 폭발 방지)
2026-09-11 09:02:01 [WARNING] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0746 → floor=0.15 적용 (z-score 폭발 방지)
2026-09-11 09:02:01 [WARNING] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.1233 → floor=0.20 적용 (z-score 폭발 방지)
2026-09-11 09:02:01 [INFO] SIGNAL: [ScalerRefresh] ts=09:01 trigger=D_FORCE feat=quality_investor_reason_code repeat=2회 n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.03s
2026-09-11 09:02:01 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: FLAT수렴 / conf미달(0.000<mc0.429) | 참고: 이상값피처(quality_investor_stale(candidate),quality_investor_reason_code(candidate),feature_quality_score(candidate))
```

</details>

**WARNING — 태그 5종 (상위 5)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 84 | 09:00:02 | 09:02:01 | 1m 'macro_vix' scale=0.0172 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerRefresh` | 30 | 08:45:10 | 09:02:01 | 1m CORE 'ofi_norm' raw_std≈0(0.0234) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ScalerMonitor` | 18 | 09:00:00 | 09:02:00 | ts=08:59 horizon=1m age=1m max_z=+4.32(cancel_add_ratio) extreme=2 adj=2 |
| `Model` | 12 | 09:00:00 | 09:00:00 | 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ConfFloorGuard` | 1 | 09:00:01 | 09:00:01 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4290 (conf_floor=0.330, min_conf=0.429, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×272

**컴포넌트 상위 15** — `ScalerFloor`×168, `ScalerRefresh`×38, `Model`×18, `ScalerMonitor`×18, `DynMC`×7, `SIGNAL`×6, `TimeRouter`×3, `ZeroDiag`×3, `DayRegimeShadow`×2, `AutoMasked`×2, `EnsembleGater`×1, `FeatureBuilder`×1, `GapOffset`×1, `MA-cont`×1, `ConfFloorGuard`×1

### `logs/20260911_LEARNING.log` — 60.6KB · 349행 · 최종 09:01:00

- 형식 평문 · 시각 인식 349행 · WARNING=167, INFO=182

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-11 08:40:51 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-11 08:40:51 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00039 auc=0.462 out_max=0.2751 (기준 auc<0.53 and span<0.020, 기저율=0.2750 n=80) → 보정 미적용, raw 통과
2026-09-11 08:40:51 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2377 < conf_floor=0.3300 (span=0.00047 auc=0.579 out_max=0.2377, 기저율=0.2375 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-09-11 08:40:51 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00166 auc=0.413 out_max=0.3257 (기준 auc<0.53 and span<0.020, 기저율=0.3250 n=80) → 보정 미적용, raw 통과
2026-09-11 08:40:51 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00004 auc=0.518 out_max=0.2174 (기준 auc<0.53 and span<0.020, 기저율=0.2174 n=115) → 보정 미적용, raw 통과
  …
2026-09-11 09:01:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0000% buf_n=1 nonzero=1 prev_p=1068.34 cur_p=1071.18
2026-09-11 09:02:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0000% buf_n=2 nonzero=2 prev_p=1071.18 cur_p=1070.72
2026-09-11 09:02:00 [INFO] LEARNING: ✗ 1m 예측 실패 (conf=44.3% 예측=UP 실제=FL)
2026-09-11 09:02:01 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=500 feat=97
2026-09-11 09:02:01 [INFO] LEARNING: [SGD] 1건 학습 | SGD비중=30% 50분정확도=50.0%
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 167 | 08:40:51 | 08:40:59 | 축퇴 감지 — span=0.00039 auc=0.462 out_max=0.2751 (기준 auc<0.53 and span<0.020, 기저율=0.2750 n=80) → 보정 미적용, raw 통과 |

**채널** — `LEARNING`×349

**컴포넌트 상위 15** — `Calibration`×329, `ScalerWarmup`×8, `sigma`×3, `ExtremityCorrector`×2, `RF`×1, `Consolidator`×1, `DriftAdjuster`×1, `SHAP`×1, `MetaConf`×1, `LEARNING`×1, `SGD`×1

### `logs/20260911_HEALTH.log` — 277B · 3행 · 최종 09:01:00

- 형식 평문 · 시각 인식 3행 · WARNING=2, INFO=1

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-11 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1810ms | quality=0.86 | cache_age=34s | exceptions_10m=0
2026-09-11 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=668ms | quality=0.86 | cache_age=92s | exceptions_10m=0
2026-09-11 09:02:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1264ms | quality=0.74 | cache_age=153s | exceptions_10m=0
  …
2026-09-11 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1810ms | quality=0.86 | cache_age=34s | exceptions_10m=0
2026-09-11 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=668ms | quality=0.86 | cache_age=92s | exceptions_10m=0
2026-09-11 09:02:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1264ms | quality=0.74 | cache_age=153s | exceptions_10m=0
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 2 | 09:00:01 | 09:02:01 | level=WARNING degraded=OFF | latency=1810ms | quality=0.86 | cache_age=34s | exceptions_10m=0 |

**채널** — `HEALTH`×3

**컴포넌트 상위 15** — `Health`×3

### `logs/20260911_MICRO.log` — 38.2KB · 113행 · 최종 09:01:12

- 형식 평문 · 시각 인식 113행 · DEBUG=113

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-11 08:45:10 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1072.04/1 ask1=1072.72/2 mp={'microprice_tick': 1072.2667, 'midprice_tick': 1072.38, 'depth_bias_tick': -0.0205} mlofi_tick=None queue=None
2026-09-11 08:45:10 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1072.04/2 ask1=1072.82/1 mp={'microprice_tick': 1072.56, 'midprice_tick': 1072.43, 'depth_bias_tick': 0.0159} mlofi_tick=6.0167 queue={'depletion_bid': 0.0, 'depletion_ask': 1.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0…
2026-09-11 08:45:11 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1072.04/1 ask1=1072.82/1 mp={'microprice_tick': 1072.43, 'midprice_tick': 1072.43, 'depth_bias_tick': -0.0774} mlofi_tick=-1.0 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': 0.…
2026-09-11 08:45:11 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1072.04/1 ask1=1072.82/2 mp={'microprice_tick': 1072.3, 'midprice_tick': 1072.43, 'depth_bias_tick': -0.1573} mlofi_tick=-1.0 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 1.0, 'bid_cancel_add_ratio': -0.…
2026-09-11 08:45:11 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1072.04/1 ask1=1072.82/1 mp={'microprice_tick': 1072.43, 'midprice_tick': 1072.43, 'depth_bias_tick': -0.0774} mlofi_tick=1.0 queue={'depletion_bid': -0.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.…
  …
2026-09-11 09:01:57 [DEBUG] MICRO: [MICRO-TICK] #7300 bid1=1070.96/1 ask1=1071.10/2 mp={'microprice_tick': 1071.0066, 'midprice_tick': 1071.03, 'depth_bias_tick': -0.216} mlofi_tick=-6.6 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio…
2026-09-11 09:02:00 [DEBUG] MICRO: [MICRO-MINUTE] #17 ts=2026-09-11 09:01:00 close=1070.72 bias=-0.001102 slope=0.812690 depth_bias=-0.0727 mlofi_norm=0.044084 mlofi_pressure=1 mlofi_slope=45.823333 queue_signal=0.0407 queue_ma=-0.0053 queue_momentum=0.0403 depletion=0.5000 refill=0.5000 imbalance_…
2026-09-11 09:02:06 [DEBUG] MICRO: [MICRO-TICK] #7400 bid1=1070.78/1 ask1=1070.92/1 mp={'microprice_tick': 1070.85, 'midprice_tick': 1070.85, 'depth_bias_tick': -0.1543} mlofi_tick=1.6833 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_rati…
2026-09-11 09:02:15 [DEBUG] MICRO: [MICRO-TICK] #7500 bid1=1070.12/1 ask1=1070.24/2 mp={'microprice_tick': 1070.16, 'midprice_tick': 1070.18, 'depth_bias_tick': -0.223} mlofi_tick=-3.5333 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio…
2026-09-11 09:02:20 [DEBUG] MICRO: [MICRO-TICK] #7600 bid1=1072.04/2 ask1=1072.14/1 mp={'microprice_tick': 1072.1067, 'midprice_tick': 1072.09, 'depth_bias_tick': 0.1571} mlofi_tick=2.05 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio…
```

</details>

**채널** — `MICRO`×113

**컴포넌트 상위 15** — `MICRO-TICK`×96, `MICRO-MINUTE`×17

### `logs/20260911_DATA.log` — 1.3KB · 10행 · 최종 09:01:00

- 형식 평문 · 시각 인식 10행 · INFO=10

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-11 08:58:14 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=128662 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-09-11 08:58:14 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-09-11 08:58:44 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=128659 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-09-11 08:58:44 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-09-11 09:00:00 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
  …
2026-09-11 09:01:00 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
2026-09-11 09:02:00 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
2026-09-11 09:02:10 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=-644 individual=-385 institution=+1062 oi=128659 call_foreign=+519 put_foreign=+421 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-09-11 09:02:10 [INFO] DATA: [CybosInvestor] program supported=True state=unknown source=Dscbo1.CpSvr8111 arb=-57379 nonarb=-22600 total=-79979 reason=verified field mapping (cybosplus docs, 2026-07-05)
2026-09-11 09:02:10 [INFO] DATA: [CybosInvestor] fetch#3 futures_supported=True program_supported=True option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=Dscbo1.CpSvr8111
```

</details>

**채널** — `DATA`×10

**컴포넌트 상위 15** — `CybosInvestor`×7, `DivergencePanel`×3

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

### 메인 스레드 블로킹 1건 · 최대 5109ms · 5초 초과 1건

상위 — 5109ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:00:05 | 5109ms | 1810ms | **3299ms (65%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260911_WARN.log`
```
--- Traceback ×1(표본)
09:00:05 2026-09-11 09:00:05 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260911.log
--- 메인 스레드 블로킹 ×1(표본)
09:00:05 2026-09-11 09:00:05 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 5109ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=5109 band=WARN since_pipe_s=0.1
```

### `logs/20260911_SYSTEM.log`
```
--- PSI ×1(표본)
09:00:00 2026-09-11 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.004 level=0 (heartbeat)
```

### `logs/20260911_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
09:00:01 2026-09-11 09:00:01 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4290 (conf_floor=0.330, min_conf=0.429, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- 기동 복원 ×7(표본)
08:40:30 2026-09-11 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.415
08:40:30 2026-09-11 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.429
08:40:30 2026-09-11 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.408
08:40:30 2026-09-11 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.404
```

### `logs/20260911_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:51 2026-09-11 08:40:51 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00039 auc=0.462 out_max=0.2751 (기준 auc<0.53 and span<0.020, 기저율=0.2750 n=80) → 보정 미적용, raw 통과
08:40:51 2026-09-11 08:40:51 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2377 < conf_floor=0.3300 (span=0.00047 auc=0.579 out_max=0.2377, 기저율=0.2375 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:51 2026-09-11 08:40:51 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00166 auc=0.413 out_max=0.3257 (기준 auc<0.53 and span<0.020, 기저율=0.3250 n=80) → 보정 미적용, raw 통과
08:40:51 2026-09-11 08:40:51 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00004 auc=0.518 out_max=0.2174 (기준 auc<0.53 and span<0.020, 기저율=0.2174 n=115) → 보정 미적용, raw 통과
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260911_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:40:59 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:40 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260911_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 13 | 08:41:08 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 10 | 08:55:10 [WARNING] scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 15 | 08:55:10 [WARNING] scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |

- 이 로그 생존구간: 08:41 ~ 09:02

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260911_SYSTEM.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 90 | 08:40:33 [INFO] 활성화 | file=logs\crash_fault.log PID=6780 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 126 | 08:49:02 [INFO] code=A056A from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 107 | 08:54:00 [INFO] code=A056A from=08:53 to=08:54 |

- 이 로그 생존구간: 08:40 ~ 09:02

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260911_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 68 | 08:45:10 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0234) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 136 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0275) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 190 | 09:00:00 [WARNING] 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |

- 이 로그 생존구간: 08:40 ~ 09:02

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260910 | 15:40 | 로그 본문 |
| 20260909 | 15:40 | 로그 본문 |
| 20260908 | 15:40 | 로그 본문 |
| 20260907 | 21:59 | 로그 본문 |
| 20260906 | 20:39 | 로그 본문 |
| **중앙값** | **15:40** | 기준선 |
| **오늘 20260911** | **09:02** | 로그 본문 |

- 델타 **-398분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.9MB · 마지막 갱신 2026-09-10 18:10

최근 헤딩 8개:
```
## 2026-09-10 (MW0601 556차 후속 — 장후 자동조치: F-5·G-4·G-1 + 제3부 결론 정정 2건)
### F-5. Armistice 「고착」 ERROR 는 장중 재기동의 정상 워밍업을 오탐하고 있었다
### G-4. ProfitGuard L2 래치가 「무엇 때문에 잠갔는지」를 남기지 않았다
### G-1. `position_state.json` 이 덮어써지기 전 세대를 남기지 않았다
### 🔴 장후 리포트 제3부 결론 정정 2건
### 🔴 부수 발견 — `state_persist_enabled=False` 는 모든 차단 래치를 재기동으로 초기화한다
### 자동조치가 하지 않은 것
### 테스트
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
틀렸다. 14:41 재기동에서 풀렸다.**
- Tier4 차단 로그 **마지막은 14:40:00**(`logs/20260910_SIGNAL.log` 384건 중 최종행).
- **14:41:01 세 번째 재기동**(`SYSTEM.log:4579`) — 제3부는 이 재기동을 인지하지 못했다.
- 그 복원이 `sys=+0원(0레그) 외부=+7,384,826원(4레그)`(`:4653`).
- **14:41 이후 ProfitGuard 차단 로그 0건**, 같은 구간 SIGNAL 188행(파이프라인 생존).
⇒ 제3부가 적은 "14:50 신규진입 금지 구간 진입으로 자연 소멸"은 사실이 아니다.

**정정 ② — O-t2「재기동이 래치를 상태 파일에서 되살린다」는 지금 성립하지 않는다.**
- `data/ui_prefs.json:state_persist_enabled = False` → `main.py:3505` 가
  `profit_guard_state` 를 **pop 한다**.
- `data/session_state.json` 의 `profit_guard_state` 는 **null**, 오늘 로그에
  `[ProfitGuard] 상태 복원` 줄 **0건**(과거 로그에는 있다).
⇒ 12:20 즉시 재latch 의 원인은 래치 복원이 아니라 **복원된 손익 자체의 오염**이다
(12:17:52 복원 `sys=+6,921,594원(2레그)`).

**그 오염의 원인도 확정**: `git log -S"PHANTOM_STATE_ARTIFACT"` 결과 이 라벨은
**14:35:53 `c08128f`(555차 후속)** 에 도입됐다 — 09:38 `bd33401`(554차)이 아니다.
그래서 12:17 복원은 두 유령 레그를 시스템 성과로 셌고, 14:41 복원은 제외했다.
⚠ **제3부 §4-1 표의 「554-1(F-1) ✅완료-커밋확인 / `bd33401`」도 이 지점에서
부정확하다** — 화이트리스트 상수는 그날 있었지만 오늘의 유령 레그를 실제로 걸러낸
라벨은 14:35 커밋에서 왔다.

**정정되지 않는 사실**: 한 프로세스 안에서 래치는 재평가되지 않는다
(`_TierGate.check()` 첫 줄 `if self._halted: return True`). 오늘 풀린 것은 재기동이
우연히 입력을 다시 만들어 줬기 때문이지 설계가 정정을 반영해서가 아니다 —
**F-1(래치 재평가 설계)의 필요성은 그대로다.**

### 🔴 부수 발견 — `state_persist_enabled=False` 는 모든 차단 래치를 재기동으로 초기화한다

`main.py:3498~3506` 은 이 플래그가 False 면 `profit_guard_state` 와
`circuit_breaker_state` 를 세션 상태에서 **빼고 저장한다**. 오늘은 그 덕에 잘못된
래치가 풀렸지만, 대칭적으로 **정당한 차단(CB②·CB③ 당일 정지 포함)도 재기동 한 번으로
풀린다.** 오늘 재기동은 최소 3회였다.
⇒ 설정 토글이라 자동조치 범위 밖이다(C등급). NEXT_TODO 556-4 로 등록하고, 실전 전환
기준 ②(CB 정상 작동 확인)와의 관계를 주간회의에서 판단할 것.

### 자동조치가 하지 않은 것

- **F-1**(래치 재평가) — 리포트가 「사용자 판단 필요」·「리스크 정책 변경」·「회귀 위험
  크다」로 표기. 안전장치를 **여는** 방향이라 자동조치 금지.
- **F-3**(장중 브로커 잔고 주기 재대사, P0) — 9p-3 사용자 조치 5번이 우선순위를
  사용자에게 맡김. 브로커 어댑터·청산 경로에 닿는다.
- **F-4** — O-i4 가 「조건이 정상 작동」으로 판정해 할 일 소멸.
- **G-2** — 「536-2와 통합해 주간회의」 명시.
- **G-3** — A등급이나 하루 G 3건 상한에 걸려 이월(다음 회차 1순위).
- **제5부 수익률 향상방안** — 오늘 엔진 자체 진입 0건, 신규 방안 0건이 리포트 결론.

### 테스트

`tests/test_556_postmarket_autofix.py` **17건 통과**.
기존 스위트는 153파일을 6배치로 나눠 실행 — 실패 8건 + 수집 오류 5건.
**변경 파일 전부를 HEAD 로 되돌려 같은 배치를 재실행한 결과 전원 동일하게 실패**하므로
**전부 기존 실패이며 이번 변경과 무관**하다(대조 로그: 세션 스크래치패드
`out_*.txt` vs `head_*.txt`).

⚠ **`tests/` 전체를 한 번에 돌리면 수집 단계에서 pytest 가 죽는다**
(`ValueError: I/O operation on closed file`). 이번 변경 이전부터 그렇다 —
`test_497_*` ~ `test_529_*` 배치 구간. 다음 회차도 배치 실행을 쓸 것.
⚠ `conda run` 에 `-s`(capture 해제)를 주면 conda 자체가 크래시 리포트를 띄우고
멈춘다 — 쓰지 말 것.

산출물: `docs/정기점검/매일점검/MW0601-20260910-점검리포트.md` 제4부 append,
커밋 `5f8e40e`.

```

</details>

### dev_memory/NEXT_TODO.md — 1.4MB · 마지막 갱신 2026-09-10 18:11

최근 헤딩 8개:
```
## 2026-09-09 (MW0601 549차 — 장전 점검)
## 2026-09-09 (MW0601 550차 — 장중 점검)
## 2026-09-09 (MW0601 551차 — 장후 점검, 종합 완성본)
## 2026-09-10 (MW0601 554차 — 장전 점검)
## 2026-09-10 (MW0601 — 장중 점검)
## 2026-09-10 (MW0601 556차 후속 — 장후 자동조치)
### 이월·승인 대기 (자동조치 범위 밖)
### 다음 세션 관측
```

미완료 체크박스 **2586건** (끝에서 30건)
```
- [ ] **O-t3 (내일 장후 판정)** `[ConfFloorGuard]` 오실레이션 패턴 지속 여부.
- [ ] **O-t4 (5거래일 누적 또는 26주 WFA 판정)** 오늘 케이스3 유형(conf가 min_conf 근소
- [ ] **554-1 (P0, 신규 / F-1)** ProfitGuard Tier4 판정에서 `entry_source`가 없거나
- [ ] **554-2 (P1, 신규 / F-2)** 포지션 복원 시 `entry_source is None`이면
- [ ] **554-3 (확인 필요, 장후)** 554-1 이월 포지션의 실제 출처 규명 — 장중 라이브 DB
- [ ] **554-4 (P2, 고도화 제안 / G-1)** `position_state.json` 덮어쓰기 전 회전 백업
- [ ] **554-5 (P2, 고도화 제안 / G-2)** `[ExternalEntry]`류 외부 진입 감지를 "엔진
- [ ] **O-p2 (장후 판정)** ProfitGuard Tier4 당일 영구 중단이 15:10까지 유지되는가
- [ ] **O-p3 (다음 세션 장전 판정)** `[SessionStateDrop]` 재발 지속 여부 + F-1(538-4)
- [ ] **O-p4 (오늘 중 재확인)** `.git/index.lock`(09:01 생성) 스테일 확정·회수 여부 —
- [ ] **O-p5 (장후 판정)** `[ConfFloorGuard]` 오실레이션 패턴 지속 여부(09:00:00 재현
- [ ] **F-3 (P0, 신규)** 장중 브로커 잔고 주기적 재대사(5~10분 간격) 신설 — 기동 시
- [ ] **F-4 (P1, 신규)** `[UnreconciledExit]`(554차 신설) 발동 조건 재검토 — 오늘
- [ ] **G-3 (고도화)** 재기동 시 엔진-브로커 상태 불일치 발견 이벤트를 별도 카운터로
- [ ] **O-i1 (장후 판정)** 12:17 재기동의 실제 원인(사용자 수동 재시작 여부) 확인.
- [ ] **O-i2 (장후 판정)** `trades.db`의 08:45 허구 2레그(+6,921,594원) + 12:17~12:18
- [ ] **O-i3 (장후 판정)** ProfitGuard Tier4 당일 영구 중단 15:10까지 유지 확정(O-p2 계승).
- [ ] **O-i4 (장후 판정)** `[UnreconciledExit]`이 12:17~12:18 청산에서 실제로 평가됐는지
- [ ] **O-i5 (장후 재확인)** 매분 루프 커버리지 12:30~15:10 공백은 이번 점검이 15:10
- [ ] 🔴 **556-4 (신규 · C등급)** `data/ui_prefs.json:state_persist_enabled = False`
- [ ] **556-5 (기록 결손)** `DECISION_LOG.md` 에 **555차·556차 본문 항목이 없다.**
- [ ] **556-6 (G-3 이월 · A등급)** 재기동 시 엔진↔브로커 상태 불일치 발견 이벤트를
- [ ] **556-7 (테스트 인프라)** `pytest tests/` 전체 실행이 **수집 단계에서**
- [ ] **556-8 (기존 실패 8건 대장)** 아래는 HEAD 에서도 동일하게 실패하는 **기존**
- [ ] **F-1 (승인 대기, 리포트 제3부 §2)** ProfitGuard Tier4 래치를 「정정 가능한
- [ ] **F-3 (P0, 승인 대기)** 장중 브로커 잔고 주기 재대사 — 09-10 이월 그대로.
- [ ] **G-2 (주간회의)** 외부 진입 감지를 「엔진 기동 전 포지션」까지 확장 — 536-2와 통합.
- [ ] **O-t2′** 내일 장중 재기동이 있으면 `[Armistice] … 고착[sync]` / `[time]` 중
- [ ] **O-t6** ProfitGuard 래치가 실제로 걸리는 날 `[ProfitGuard][LatchSnapshot]` 이
- [ ] **O-t7** 포지션이 열리고 닫히는 날 `data/position_state.json.gen_*` 이 최대
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
se`
      유지 여부 결정. 이 값이 False 라 `main.py:3505` 가 `profit_guard_state` ·
      `circuit_breaker_state` 를 세션 상태에서 빼고 저장한다 ⇒ **ProfitGuard·CB 의
      차단 래치가 재기동으로 전부 초기화된다.** 2026-09-10 은 그 덕에 잘못된 Tier4
      래치가 14:41 재기동에서 풀렸지만(리포트 4-2 정정 ①), 대칭적으로 **정당한
      차단도 재시작 한 번에 풀린다** — 그날 재기동은 최소 3회였다.
      ⚠ 실전 전환 기준 ②(CB 정상 작동 확인)와 직접 관계 — 주간회의 안건.
- [ ] **556-5 (기록 결손)** `DECISION_LOG.md` 에 **555차·556차 본문 항목이 없다.**
      오늘 커밋은 555차 후속2까지 갔고 장후 리포트 §8 은 "556차 항목 추가 완료"라
      적었으나 실제 마지막 항목은 554차(장전)다. 두 세션 기록을 소급 보완할지 결정.
- [ ] **556-6 (G-3 이월 · A등급)** 재기동 시 엔진↔브로커 상태 불일치 발견 이벤트를
      별도 카운터로 누적 기록 — F-3 적용 전 임시 안전판. 자동조치 하루 G 3건 상한에
      걸려 미착수. **다음 회차 1순위.**
- [ ] **556-7 (테스트 인프라)** `pytest tests/` 전체 실행이 **수집 단계에서**
      `ValueError: I/O operation on closed file` 로 죽는다(`test_497_*`~`test_529_*`
      구간). 이번 변경 이전부터 존재. 원인 모듈 특정 필요 — 그전까지는 배치 실행.
      ⚠ `conda run` 에 `-s` 를 주면 conda 자체가 크래시 리포트로 멈춘다.
- [ ] **556-8 (기존 실패 8건 대장)** 아래는 HEAD 에서도 동일하게 실패하는 **기존**
      실패다. 이번 변경과 무관하나 누적 방치 중 — 별건 처리 필요.
      `test_456_wave1_stats_and_shs::test_trend_sql_counts_positions_not_legs` ·
      `test_477_f1_f5_saturation_psi::test_step9_batch_placeholders_match_params` ·
      `test_483_git_lock_guard::test_sibling_copy_matches_canonical[fuoption]` ·
      `test_493_commission_rate_and_net_recon::test_cost_formulas_do_not_use_live_rate` ·
      `test_553_gp_chart_markers::test_loader_is_safe_before_phase3` ·
      `test_553_gp_pnl_panel::test_gp_uses_mini_futures_multiplier` ·
      `test_553_gp_pnl_panel::test_gp_defaults_off_when_unset` ·
      `test_554_position_state_isolation::test_missing_reference_skips_check_but_is_not_silent`
      (단독 실행은 통과 — 테스트 순서 간섭)
- [ ] **F-1 (승인 대기, 리포트 제3부 §2)** ProfitGuard Tier4 래치를 「정정 가능한
      재평가」로 바꿀지 — **여전히 필요하다.** 09-10 에 래치가 풀린 것은 재기동이
      우연히 입력을 다시 만들어 준 결과이지 설계가 정정을 반영한 것이 아니다
      (`_TierGate.check()` 첫 줄 `if self._halted: return True` 는 그대로).
      ⚠ 안전장치를 **여는** 방향이라 섀도 선행 + 사용자 승인 필수.
- [ ] **F-3 (P0, 승인 대기)** 장중 브로커 잔고 주기 재대사 — 09-10 이월 그대로.
- [ ] **G-2 (주간회의)** 외부 진입 감지를 「엔진 기동 전 포지션」까지 확장 — 536-2와 통합.

### 다음 세션 관측

- [ ] **O-t2′** 내일 장중 재기동이 있으면 `[Armistice] … 고착[sync]` / `[time]` 중
      어느 쪽도 **뜨지 않는지** 확인(F-5 라이브 검증). 워밍업 90초 구간에 ERROR 가
      뜨면 이번 수정이 안 먹은 것이다.
- [ ] **O-t6** ProfitGuard 래치가 실제로 걸리는 날 `[ProfitGuard][LatchSnapshot]` 이
      **1줄** 남고 구성 레그가 실리는지(G-4 라이브 검증).
- [ ] **O-t7** 포지션이 열리고 닫히는 날 `data/position_state.json.gen_*` 이 최대
      3개까지만 쌓이는지, 손절 조정으로 링이 소모되지 않는지(G-1 라이브 검증).

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

### `data/heartbeat_MW0601_20260911.json` — 243B · 09-11 09:01:11
```json
{
 "pid": 6780,
 "written_at": "2026-09-11T09:02:11",
 "beat_epoch": 1789084930.4534683,
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

- 파일 최종 기록: **09-11 08:46:00**

| 키 | 값 | 수집 대상일(2026-09-11)과 일치 |
|---|---|---|
| `date` | 2026-09-11 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 127개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260910-점검리포트.md` | 103.5KB | 09-10 18:08 |
| `docs/정기점검/매일점검/evidence_MW0601-20260910_post.md` | 84.6KB | 09-10 16:20 |
| `docs/정기점검/매일점검/evidence_MW0601-20260910_intra.md` | 69.2KB | 09-10 12:29 |
| `docs/정기점검/매일점검/evidence_MW0601-20260910_pre.md` | 56.9KB | 09-10 09:01 |
| `docs/정기점검/매일점검/MW0601-20260909-점검리포트.md` | 62.1KB | 09-09 16:30 |
| `docs/정기점검/매일점검/evidence_MW0601-20260909_post.md` | 78.6KB | 09-09 16:18 |
| `docs/정기점검/매일점검/evidence_MW0601-20260909_intra.md` | 62.0KB | 09-09 12:29 |
| `docs/정기점검/매일점검/evidence_MW0601-20260909_pre.md` | 53.9KB | 09-09 09:01 |

### `docs/정기점검/금요일점검` — 60개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260904.json` | 2.9KB | 09-04 15:50 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260904.md` | 4.9KB | 09-04 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260904.json` | 38.4KB | 09-04 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260904.md` | 31.4KB | 09-04 15:50 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260904.json` | 105.4KB | 09-04 15:50 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260904.md` | 185.3KB | 09-04 15:50 |
| `docs/정기점검/금요일점검/weekly_prompt.txt` | 2.6KB | 08-31 00:05 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260828.json` | 2.9KB | 08-28 15:50 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. `logs/20260911_WARN.log`: **Traceback** 출현 1건 — 크래시/메모리 계열
2. 메인 스레드 정지 5초 초과 **1건** (최대 5109ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
3. `logs/20260911_LEARNING.log`: **축퇴** 8건(표본)
4. 미커밋 변경 557건 — **실질 변경 미측정**(git diff 실패). 원시 건수만으로는 착시인지 알 수 없다

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260911*.log` (Windows) / `grep 강제청산 logs/*20260911*.log`*