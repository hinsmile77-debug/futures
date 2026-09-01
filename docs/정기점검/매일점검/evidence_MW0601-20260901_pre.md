# 미륵이 증거 다이제스트 — 2026-09-01 / PRE

- 생성 2026-09-01 09:00:46 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/zen-laughing-darwin/mnt/futures`
- 점검 범위: pre (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260901` · `2026-09-01` · `260901` · `0901`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **18개** 파일 · 18개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260901.log` | 125B | 09-01 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260901.log` | 139B | 09-01 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260901.json` | 244B | 09-01 09:00 |
| `launcher_{DATE}_084002_20299.log` | 1 | `logs/Mireuk_batch/launcher_20260901_084002_20299.log` | 61.7KB | 09-01 09:00 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260901.log` | 2.9KB | 09-01 09:00 |
| `retrain_intraday_20260716_10{DATE}.log` | 1 | `logs/retrain_intraday_20260716_100901.log` | 4.5KB | 07-16 10:09 |
| `retrain_intraday_20260807_{DATE}03.log` | 1 | `logs/retrain_intraday_20260807_090103.log` | 4.5KB | 08-07 09:01 |
| `{DATE}_DATA.log` | 1 | `logs/20260901_DATA.log` | 1.1KB | 09-01 09:00 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260901_DEBUG.log` | 624B | 09-01 09:00 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260901_HEALTH.log` | 142B | 09-01 09:00 |
| `{DATE}_HOGA.log` | 1 | `logs/20260901_HOGA.log` | 1.4MB | 09-01 09:00 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260901_LEARNING.log` | 55.5KB | 09-01 09:00 |
| `{DATE}_MICRO.log` | 1 | `logs/20260901_MICRO.log` | 35.9KB | 09-01 09:00 |
| `{DATE}_PROBE.log` | 1 | `logs/20260901_PROBE.log` | 1.7KB | 09-01 08:58 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260901_SIGNAL.log` | 26.6KB | 09-01 09:00 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260901_SYSTEM.log` | 26.8KB | 09-01 09:00 |
| `{DATE}_TRADE.log` | 1 | `logs/20260901_TRADE.log` | 167B | 09-01 08:41 |
| `{DATE}_WARN.log` | 1 | `logs/20260901_WARN.log` | 2.9KB | 09-01 09:00 |

## 2. 코드·커밋 상태

- HEAD `c5eddda` · 브랜치 `v9-dev` · 미커밋 513건 · 실질 변경 0건 · 코드(.py) 0건 · EOL 파생 513건 (추적변경 513 · 미추적 0 · 삭제 0 · core.autocrlf=미설정) · 인덱스락 없음
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
```
M .claude/commands/dailycheck.md
 M .claude/skills/mireuk-daily-check/config_dailycheck_targets.json
 M .claude/skills/mireuk-daily-check/references/evidence_map.md
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
 M challenger/challenger_db.py
 M challenger/challenger_engine.py
 M challenger/promotion_manager.py
 M challenger/variants/base_challenger.py
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
… 외 473건
```

**당일(2026-09-01) 커밋**
```
(당일 커밋 없음 — 커밋 가능 상태였음)
```

**최근 커밋 12건**
```
c5eddda [MW0601] 508차: F-6 배포 — Restart Armistice 고착 해소 (2026-08-31 자동진입 0건)
db48586 [MW0601] 507차 후속: 리포트 제8부에 커밋 해시 기입
2d6a1bb [MW0601] 507차 후속: 장후 자동조치 — F-7·F-8·F-11·F-12·F-14 + G-4·G-5
f01080b [MW0601] 문서: MW0602 장후 자동조치 예약작업 설치 지침 (mireuk-postmarket-autofix)
da120b1 [MW0601] 점검 프롬프트: 8월 10만원 이상 손실일 딥다이브 지시 추가
5cf1eab [MW0601] 금요일점검 주간 산출물: 2026-08-28 3종 + 4주 FIFO 보관 정리
4b494df [MW0601] 매일점검 산출물: 2026-08-27 점검리포트 + 증거 다이제스트 2건
81096d5 [MW0601] 504차 후속: 기동 패널 복원 4단계 체인 — 워커 스레드 QTimer 미발화 수정
6dfe6d7 [MW0601] 504차: 8월 손실일 딥다이브 + 손익추이2(CREON 반사실)·거래 출처 필터
fc05088 [MW0601] test_479 오탐 정정: broker_net_chain_audit.py를 _COMPRESSED_AWARE에 등록
1c51249 [MW0601] dev 502차 후속 체리픽: U-1 te ready 플래그 + U-2 [57] 게이트 섀도 배선
614eda2 [MW0601] dev 501차 D1 정정 실행 완료 — daily_broker_pnl 브로커net 재산출
```

PC명 태그 규약: 최근 12건 모두 `[MW####]` 접두 확인

## 3. 설정 불변식 — 절대원칙·한시예외 (config/settings.py)

| 상수 | 현재값 | 기대값 | 판정 | 왜 보는가 |
|---|---|---|---|---|
| `CB_CONSEC_STOP_LIMIT` | `9999` | `9999` | 일치 | 모의투자 한정 예외(CB② 사실상 비활성). 실투 전환 전 2~3 복원 필수. 재검토 기한 2026-08-29 |
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

### 차단 게이트 전수 인벤토리 — 33개 중 **9개 꺼짐**

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

_본문 미열람(설정): `20260901_HOGA.log` 1.4MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/16개 (중요도순). 제외: `20260901_MICRO.log`, `20260901_DATA.log`, `20260901_PROBE.log`, `launcher_20260901_084002_20299.log`, `20260901_DEBUG.log`, `mainstall_traceback_20260901.log`, `freeze_sentinel_20260901.log`, `force_flat_guard_20260901.log`_

### `logs/20260901_TRADE.log` — 167B · 2행 · 최종 08:41:04

- 형식 평문 · 시각 인식 2행 · INFO=2

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-01 08:41:00 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-01 08:41:04 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
  …
2026-09-01 08:41:00 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-01 08:41:04 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×2

**컴포넌트 상위 15** — `Position`×1, `ProfitGuard`×1

### `logs/20260901_WARN.log` — 2.9KB · 24행 · 최종 09:00:06

- 형식 평문 · 시각 인식 24행 · WARNING=24

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-01 08:41:07 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-01 08:41:07 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 47ms
2026-09-01 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 188ms account=333044256
2026-09-01 08:41:11 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3125ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3125 band=INFO since_pipe_s=NA
2026-09-01 08:41:14 [WARNING] SYSTEM: [LiveDBG] _restore_panels_worker 지연 3500ms — live 중단 원인 분석용
  …
2026-09-01 09:00:02 [WARNING] SYSTEM: [CB⑤] 파이프라인 1651ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s]
2026-09-01 09:00:06 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 6250ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=6250 band=WARN since_pipe_s=0.1
2026-09-01 09:00:06 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260901.log
2026-09-01 09:01:00 [WARNING] SYSTEM: [HealthPolicy] Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=1651ms quality=0.86 cache=0s exc10m=0) | cause=S5(1207ms)
2026-09-01 09:01:01 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2141ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2141 band=INFO since_pipe_s=0.1
```

</details>

**WARNING — 태그 7종 (상위 7)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 15 | 08:41:07 | 09:01:01 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `Canary` | 2 | 08:55:08 | 08:55:08 | scaler 노후=0h  z경고피처=13개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| `PipePerf` | 2 | 09:00:01 | 09:00:01 | total=1651ms | S0=2ms S1=8ms S2=0ms S3=0ms S4=110ms S5=1207ms S6=305ms S7=15ms S8=4ms |
| `CB⑤` | 2 | 09:00:02 | 09:00:02 | 파이프라인 1651ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `Health` | 1 | 09:00:01 | 09:00:01 | level=WARNING degraded=OFF | latency=1651ms | quality=0.86 | cache_age=39s | exceptions_10m=0 |
| `MainStallTrace` | 1 | 09:00:06 | 09:00:06 | 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260901.log |
| `HealthPolicy` | 1 | 09:01:00 | 09:01:00 | Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=1651ms quality=0.86 cache=0s exc10m=0) | cause=S5(1207ms) |

**채널** — `SYSTEM`×23, `HEALTH`×1

**컴포넌트 상위 15** — `LiveDBG`×15, `Canary`×2, `PipePerf`×2, `CB⑤`×2, `Health`×1, `MainStallTrace`×1, `HealthPolicy`×1

### `logs/20260901_SYSTEM.log` — 26.8KB · 229행 · 최종 09:00:44

- 형식 평문 · 시각 인식 222행 · INFO=222, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-01 08:40:34 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=17924 | 행감지=30s all_threads=True
2026-09-01 08:40:49 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-01 08:40:49 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-01 08:40:49 [INFO] SYSTEM: 미륵이 초기화
2026-09-01 08:40:49 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-08-31) 종가 버퍼 로드: 384봉
  …
2026-09-01 09:01:17 [INFO] SYSTEM: [CybosRT-TICK] #3000 code=A0569 raw_time=90117 parsed=09:01:17 price=1064.38 vol=1 bid1=1064.16 ask1=1064.38 flag=49 side=BUY anchor=1/0
2026-09-01 09:01:20 [INFO] SYSTEM: [TickUI] alive ticks=3059 code=A0569 close=1063.68
2026-09-01 09:01:24 [INFO] SYSTEM: [CybosRT-TICK] #3100 code=A0569 raw_time=90124 parsed=09:01:24 price=1062.92 vol=1 bid1=1062.94 ask1=1063.04 flag=50 side=SELL anchor=0/1
2026-09-01 09:01:26 [INFO] SYSTEM: [OptionChain][Worker] 완료 1475ms | target=24 valid=24 PCR=0.896 ATM_PCR=0.896 GEX=34.59B
2026-09-01 09:01:32 [INFO] SYSTEM: [CybosRT-TICK] #3200 code=A0569 raw_time=90132 parsed=09:01:32 price=1064.76 vol=1 bid1=1064.70 ask1=1064.76 flag=49 side=BUY anchor=1/0
```

</details>

**채널** — `SYSTEM`×222

**컴포넌트 상위 15** — `CybosRT-TICK`×37, `CybosSub`×21, `System`×18, `TickUI`×17, `CybosRT-ROLLOVER`×16, `BAR-CLOSE`×16, `CVD-ANCHOR`×16, `SYSTEM`×9, `PreMarket`×9, `CybosRT-START`×6, `Notify`×5, `BrokerSync`×4, `BalanceUI`×4, `-`×4, `EarlyWarmup`×3

### `logs/20260901_SIGNAL.log` — 26.6KB · 216행 · 최종 09:00:06

- 형식 평문 · 시각 인식 216행 · WARNING=127, INFO=89

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-01 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.416
2026-09-01 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.408
2026-09-01 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.404
2026-09-01 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.412
2026-09-01 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.424
  …
2026-09-01 09:01:00 [WARNING] SIGNAL: [ScalerMonitor] ts=09:00 horizon=15m age=1m max_z=-6.22(ofi_imbalance) extreme=4
2026-09-01 09:01:00 [WARNING] SIGNAL: [ScalerMonitor] ts=09:00 horizon=30m age=1m max_z=-6.22(ofi_imbalance) extreme=4
2026-09-01 09:01:00 [INFO] SIGNAL: [AutoMasked] 이상값 4개 즉시 격리 예측 (CORE 제외): ['ofi_imbalance', 'cancel_add_ratio', 'quality_investor_reason_code', 'macro_nasdaq_chg']
2026-09-01 09:01:00 [INFO] SIGNAL: 앙상블: dir=+0 conf=0.0% grade=X micro=혼합
2026-09-01 09:01:00 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: FLAT수렴 / conf미달(0.000<mc0.424) | 참고: 이상값피처(ofi_imbalance(candidate),cancel_add_ratio,quality_investor_reason_code(candidate))
```

</details>

**WARNING — 태그 5종 (상위 5)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerRefresh` | 60 | 08:45:08 | 09:00:02 | 1m CORE 'ofi_norm' raw_std≈0(0.0205) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ScalerFloor` | 42 | 09:00:02 | 09:00:02 | 1m 'macro_sp500_chg' scale=0.0574 → floor=0.15 적용 (z-score 폭발 방지) |
| `Model` | 12 | 09:00:00 | 09:00:00 | 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 12 | 09:00:00 | 09:01:00 | ts=08:59 horizon=1m age=1m max_z=-7.42(prev_day_same_hour_ret) extreme=1 |
| `ConfFloorGuard` | 1 | 09:00:01 | 09:00:01 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4240 (conf_floor=0.330, min_conf=0.424, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×216

**컴포넌트 상위 15** — `ScalerFloor`×96, `ScalerRefresh`×67, `Model`×18, `ScalerMonitor`×12, `DynMC`×7, `SIGNAL`×4, `TimeRouter`×3, `ZeroDiag`×2, `EnsembleGater`×1, `FeatureBuilder`×1, `GapOffset`×1, `DayRegimeShadow`×1, `ConfFloorGuard`×1, `Ensemble`×1, `AutoMasked`×1

### `logs/20260901_LEARNING.log` — 55.5KB · 318행 · 최종 09:00:02

- 형식 평문 · 시각 인식 318행 · WARNING=152, INFO=166

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-01 08:40:50 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-01 08:40:51 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3129 < conf_floor=0.3300 (span=0.00067 auc=0.544 out_max=0.3129, 기저율=0.3125 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-09-01 08:40:51 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00018 auc=0.508 out_max=0.3054 (기준 auc<0.53 and span<0.020, 기저율=0.3053 n=95) → 보정 미적용, raw 통과
2026-09-01 08:40:51 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00022 auc=0.436 out_max=0.1126 (기준 auc<0.53 and span<0.020, 기저율=0.1125 n=80) → 보정 미적용, raw 통과
2026-09-01 08:40:51 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00058 auc=0.537 out_max=0.2913 (n=110) → 보정 재적용
  …
2026-09-01 09:00:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0000% buf_n=0 nonzero=0 prev_p=0.00 cur_p=1063.20
2026-09-01 09:00:02 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=500 feat=97
2026-09-01 09:01:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0000% buf_n=1 nonzero=1 prev_p=1063.20 cur_p=1062.10
2026-09-01 09:01:00 [INFO] LEARNING: ✓ 1m 예측 적중 (conf=42.4% DN)
2026-09-01 09:01:00 [INFO] LEARNING: [SGD] 1건 학습 | SGD비중=30% 50분정확도=50.0%
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 152 | 08:40:51 | 08:40:59 | 하한 도달불가 — out_max=0.3129 < conf_floor=0.3300 (span=0.00067 auc=0.544 out_max=0.3129, 기저율=0.3125 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |

**채널** — `LEARNING`×318

**컴포넌트 상위 15** — `Calibration`×299, `ScalerWarmup`×7, `ExtremityCorrector`×2, `Consolidator`×2, `sigma`×2, `RF`×1, `DriftAdjuster`×1, `SHAP`×1, `MetaConf`×1, `LEARNING`×1, `SGD`×1

### `logs/20260901_HEALTH.log` — 142B · 2행 · 최종 09:00:01

- 형식 평문 · 시각 인식 2행 · WARNING=1, INFO=1

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-01 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1651ms | quality=0.86 | cache_age=39s | exceptions_10m=0
2026-09-01 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=744ms | quality=0.86 | cache_age=98s | exceptions_10m=0
  …
2026-09-01 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1651ms | quality=0.86 | cache_age=39s | exceptions_10m=0
2026-09-01 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=744ms | quality=0.86 | cache_age=98s | exceptions_10m=0
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 1 | 09:00:01 | 09:00:01 | level=WARNING degraded=OFF | latency=1651ms | quality=0.86 | cache_age=39s | exceptions_10m=0 |

**채널** — `HEALTH`×2

**컴포넌트 상위 15** — `Health`×2

### `logs/retrain_intraday_20260716_100901.log` — 4.5KB · 39행 · 최종 10:09:36

- 형식 평문 · 시각 인식 39행 · INFO=39

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-07-16 10:09:01,735 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-16 10:09:01,735 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-07-16 10:09:01,735 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-16 10:09:01,736 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_de5f6a4a.json
2026-07-16 10:09:04,490 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-07-16 10:09:36,601 [INFO] LEARNING: [Retrain] 30m 교체 (intraday — CV 없음 | fit=1.43s | old_acc=0.2874)
2026-07-16 10:09:36,604 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-07-16 10:09:36,604 [INFO] LEARNING: [Retrain] 완료 | 32.1초 | 성공=6/6 호라이즌
2026-07-16 10:09:36,606 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 34.9s 데이터=20000행
2026-07-16 10:09:36,607 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_de5f6a4a.json
```

</details>

**채널** — `LEARNING`×27, `RETRAIN_INTRADAY`×6, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×20, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `CUSUM`×1

### `logs/retrain_intraday_20260807_090103.log` — 4.5KB · 39행 · 최종 09:01:47

- 형식 평문 · 시각 인식 39행 · INFO=39

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-07 09:01:03,400 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-07 09:01:03,400 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-08-07 09:01:03,400 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-07 09:01:03,400 [INFO] RETRAIN_INTRADAY: 파라미터: force=False intraday=True result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_40c7d357.json
2026-08-07 09:01:07,156 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-08-07 09:01:47,800 [INFO] LEARNING: [Retrain] 30m 교체 (intraday — CV 없음 | fit=0.95s | old_acc=0.4289)
2026-08-07 09:01:47,839 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-08-07 09:01:47,839 [INFO] LEARNING: [Retrain] 완료 | 40.7초 | 성공=6/6 호라이즌
2026-08-07 09:01:47,840 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 44.4s 데이터=4800행
2026-08-07 09:01:47,841 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_40c7d357.json
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

### 메인 스레드 블로킹 4건 · 최대 6250ms · 5초 초과 1건

상위 — 6250ms, 3125ms, 2891ms, 2141ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:00:06 | 6250ms | 1651ms | **4599ms (74%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260901_WARN.log`
```
--- Traceback ×1(표본)
09:00:06 2026-09-01 09:00:06 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260901.log
--- 메인 스레드 블로킹 ×4(표본)
08:41:11 2026-09-01 08:41:11 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3125ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3125 band=INFO since_pipe_s=NA
08:46:05 2026-09-01 08:46:05 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2891ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2891 band=INFO since_pipe_s=NA
09:00:06 2026-09-01 09:00:06 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 6250ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=6250 band=WARN since_pipe_s=0.1
09:01:01 2026-09-01 09:01:01 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2141ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2141 band=INFO since_pipe_s=0.1
```

### `logs/20260901_SYSTEM.log`
```
--- PSI ×1(표본)
09:00:00 2026-09-01 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
```

### `logs/20260901_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
09:00:01 2026-09-01 09:00:01 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4240 (conf_floor=0.330, min_conf=0.424, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- 기동 복원 ×7(표본)
08:40:31 2026-09-01 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.416
08:40:31 2026-09-01 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.408
08:40:31 2026-09-01 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.404
08:40:31 2026-09-01 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.412
```

### `logs/20260901_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:51 2026-09-01 08:40:51 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3129 < conf_floor=0.3300 (span=0.00067 auc=0.544 out_max=0.3129, 기저율=0.3125 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:51 2026-09-01 08:40:51 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00018 auc=0.508 out_max=0.3054 (기준 auc<0.53 and span<0.020, 기저율=0.3053 n=95) → 보정 미적용, raw 통과
08:40:51 2026-09-01 08:40:51 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00022 auc=0.436 out_max=0.1126 (기준 auc<0.53 and span<0.020, 기저율=0.1125 n=80) → 보정 미적용, raw 통과
08:40:51 2026-09-01 08:40:51 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00058 auc=0.537 out_max=0.2913 (n=110) → 보정 재적용
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260901_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:00 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:41 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260901_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 13 | 08:41:07 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 11 | 08:55:08 [WARNING] scaler 노후=0h  z경고피처=13개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 11 | 08:55:08 [WARNING] scaler 노후=0h  z경고피처=13개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |

- 이 로그 생존구간: 08:41 ~ 09:01

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260901_SYSTEM.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 88 | 08:40:34 [INFO] 활성화 | file=logs\crash_fault.log PID=17924 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 122 | 08:49:00 [INFO] code=A0569 from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 93 | 08:54:00 [INFO] code=A0569 from=08:53 to=08:54 |

- 이 로그 생존구간: 08:40 ~ 09:01

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260901_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 67 | 08:45:08 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0205) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 142 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0170) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 135 | 08:55:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0274) → identity(0,1) 강제 (FLAT 100% 방지) |

- 이 로그 생존구간: 08:40 ~ 09:01

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260831 | 15:40 | 로그 본문 |
| 20260830 | 00:07 | 로그 본문 |
| 20260828 | 15:40 | 로그 본문 |
| 20260827 | 15:40 | 로그 본문 |
| 20260826 | 15:40 | 로그 본문 |
| **중앙값** | **15:40** | 기준선 |
| **오늘 20260901** | **09:01** | 로그 본문 |

- 델타 **-399분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.5MB · 마지막 갱신 2026-08-31 18:50

최근 헤딩 8개:
```
### 검증 종합
## 2026-08-31 (MW0601 508차 — F-6 배포: Restart Armistice 고착 해소)
### 사실 — 종일 자동진입 0건의 단일 원인
### 원인 — 카운터를 올리는 경로가 둘 다 도달 불가였다
### 기회비용 (참고 — 손익 추정으로 쓰지 말 것)
### 조치
### 검증
### 부수 사실 — 갭 손실과 자동매매 정지는 같은 뿌리다
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
 시 1회뿐이라
재평가 기회가 없었다.

🔴 **승격에 필요한 정보는 처음부터 다 있었다.** 같은 08:41:05에
`[BrokerSync] status verified=True block_new_entries=False reason=synced LONG 4 @ 1068.47`
이 찍혀 있었다 — 없던 데이터가 아니라 **아무도 안 본 데이터**다(계측 4원칙 ⑤와 동형).

대조군이 원인을 확정한다:

| 거래일 | `armistice cleared` | Armistice 차단 |
|---|---|---|
| 08-25 ~ 08-28 | 각 1건 | **0건** |
| 08-31 | **0건** | **47건** |

### 기회비용 (참고 — 손익 추정으로 쓰지 말 것)

Armistice가 **단독** 차단한 5분(봉 시각): 13:22 · 14:03 · 14:11 · 14:13 · 14:14.
전부 LONG · grade C. 3분 선도수익 +0.68 / +2.30 / +1.68 / +0.12 / +1.46pt =
**방향 5/5 적중, 합 +6.24pt/계약**. ⚠ n=5이고 실제 청산은 TP/손절 계단이라
손익 추정치가 아니다 — "막힌 신호가 무작위가 아니었다" 이상으로 읽지 말 것.
나머지 11분은 `qty_ok`(10) · `mode_filter_ok`(9) · `cb_normal`(3)도 함께 걸려 있어
유예가 풀렸어도 진입하지 않았다.

### 조치

**F-6** `main.py` — 인라인 블록을 **`_ts_evaluate_armistice(self, now_dt)`** 로 분리.
인라인이면 스텁 self로 구동할 수 없어 회귀 테스트가 소스 문자열 검사로 전락한다
(471차 F-1과 같은 이유).

- **승격**: `sync_count < 2` AND `time_ok` AND `_broker_sync_verified is True`
  AND `_broker_sync_block_new_entries is False` → `sync_count = 2`, WARNING 1회.
- **고착 경보**: `_in_armistice` 이고 **09:30 이후**면 5분 스로틀 **ERROR**.
  종전에는 `[차단]` INFO 한 줄뿐이라 하루를 통째로 잃고도 경보가 없었다
  (계측 4원칙 ④). 등급과 무관하게 찍는다 — 등급이 X뿐인 것 자체가 증상일 수 있다.
- `__init__` 에 `_armistice_promoted_logged` · `_armistice_stuck_last_log` **명시
  초기화**(`getattr` 폴백 금지 — 계측 4원칙 ④).

🔴 **90초 시간 조건은 AND로 유지했다.** 떼면 P1-a 원목적(재시작 직후 브로커 상태
미확인 진입 차단)이 무력화된다. 테스트 T3·T8이 이 불변식을 못박는다.

⚠ **안전성 손실 0.** `_broker_sync_block_new_entries` 는 이 승격과 무관하게 최종
진입 조건에서 따로 평가된다 — 승격 후 브로커가 나빠지면 그쪽이 막는다.

### 검증

- `tests/test_506_armistice_release.py` 신설 — **33항목 전부 통과**.
  T1 정방향 / T2 역방향(sync 미검증 → 3시간 뒤에도 미해제) /
  **T3 90초 AND 불변식** / **T4 08-31 재현**(non-blank 기동이어도 해제, 단독 차단
  5분이 모두 열림) / T5·T5b 고착 ERROR + 스로틀 + 오탐 없음 / T6 승격 로그 1회 /
  T7 `block_new_entries=True` 면 미승격 / T8 소스·배선·`__init__` 불변식.
- 전체 스위트 **1,033 통과 / 3 실패 / 1 skip / 4 xfail** (6분 58초).
  실패 3건 전량 **선행 실패** — `git stash push -- main.py` 로 되돌린 뒤 같은
  3건이 **동일하게 실패**하는 것을 실측했다
  (`test_483_git_lock_guard[fuoption]` · `test_504_pnl_history_creon_tab` 2건).
- `test_500_*` 5파일은 507차가 등록한 대로 pytest 수집 시 `SystemExit: 0`
  (단독 실행 스크립트) — `--ignore` 로 제외. 오늘 작업과 무관.
- `main.py` CRLF 18,463/18,463 보존(변경 전과 동일). AST 파싱 통과.

### 부수 사실 — 갭 손실과 자동매매 정지는 같은 뿌리다

이월 LONG 4계약이 1068.47 → 1041.18 갭에 맞아 08:45:06 하드스톱 **-5,461,928원**.
당일 총 -6,389,518원의 **85.5%**다. 절대원칙 §1(15:10 강제청산)은 엔진이 연
포지션을 전제하는데 **외부에서 들어와 이월된 포지션에는 장전 강제청산 경로가 없다.**
그리고 바로 그 포지션이 Armistice 고착의 방아쇠였다.
⇒ 「장전 이월 포지션 처리」는 F-6과 **별개 안건**으로 NEXT_TODO에 남긴다.

```

</details>

### dev_memory/NEXT_TODO.md — 1.3MB · 마지막 갱신 2026-08-31 18:50

최근 헤딩 8개:
```
### MW0601 507차 (2026-08-31 16:17~16:4x — 장후 점검)
## MW0601 507차 후속 — 장후 자동조치 이월분 (2026-08-31 자동)
### C등급 — 주문·청산 경로 (사용자 지시 없이는 착수 금지)
### C등급 — 판정 기준·표본 (사용자 승인 필요)
### F-4 — 등급상 자동 가능이나 **일부러 멈춤** (근거 있음)
### 고도화 이월 (오늘 상한 3건 소진: G-4·G-5 완료)
### 제5부 수익률 방안 이월
### 정비
```

미완료 체크박스 **2220건** (끝에서 30건)
```
- [ ] **P5-08** 자가유발 안전장치 발동의 진입공백 비용 환산 — n=1(계열 2). 4주 · `min_days=10`
- [ ] **P5-05 판정 유예 → 2026-09-04 재판정** — 08-27·08-28 장후 미실행으로 2거래일 결장(1-23)
- [ ] 🔴 **1. 오늘 09:28~15:03 증권사 화면에서 직접 매매했는지 확인** — 아니오면 즉시 정지 + 계좌 확인
- [ ] 🔴 **2. 내일 09:30 「재시작 유예」 차단 지속 여부 확인** — 지속이면 F-6 최우선 지시
- [ ] 🔴 **3. 오늘 저녁 증권사 화면에서 선물 잔고 0 직접 확인** (장전 조치 2·장중 2-B 승계)
- [ ] **4. net 대사 9만원 차이 — 사용자 조치 없음. 내일 재발 시 조사 지시**(O-t1)
- [ ] **5. CB② 복원 결정** (기한 2026-08-29 경과) — 오늘 「2회」 2번 도달.
- [ ] **6. 08-27·08-28 매일점검 장후 미실행 원인 확인** (2거래일 연속 · 대장 3일 미갱신 유발)
- [ ] **7. 주간회의 안건 3건** — ⓐ 전환기준 ③ 승률의 gross/net 정의 ⓑ F-15 외부진입 손익 처리
- [ ] **8. 커밋 대기 (세 세션 모두 커밋하지 않았다)** — ⚠ `git add .` 금지
- [ ] **F-1 (P0)** blank-rows 폴백을 "유지"에서 "잠금"으로 — `main.py:17107~17132`
- [ ] **F-2 (P0)** `BrokerDirectExit` 주문 실패 재시도 — 🔴 **주간회의 안건**
- [ ] **F-3 (P1)** 15:10 미체결 **진입** 주문 일괄 취소 — 주문 경로.
- [ ] **F-6 (P0)** Restart Armistice 고착 해소 — `main.py:8537~8556`
- [ ] **F-10 (P1)** `partial_1_done` 에 사유 축 — `position_tracker.py:1509~1513`
- [ ] **F-5 (P2)** 08-28 손익 기록 정정 + `METRIC_REDEFINITION` 마커
- [ ] **F-15 (P2)** 외부 진입을 브로커 net 판정 경로에서 분리 — 🔴 **주간회의 안건**
- [ ] **F-13 (P2)** `PIPE_LATENCY_EXCLUDE_MODEL_SWAP` `dev` → `v9-dev` 이식 여부
- [ ] **승률의 정의** — 실전 전환 기준 ③ 「승률 ≥ 53%」가 gross 인지 net 인지
- [ ] **CB② 복원 여부** — 재검토 기한 2026-08-29 경과. 절대원칙 §2 / 전환기준 ⑤.
- [ ] **F-4 (P1)** 일일 마감 손익을 **브로커 포지션 축**과 대사 — `main.py:daily_close()`
- [ ] **G-2** 「장 마감 후 잔고 최종 확인」 잡 — 15:50에 브로커 잔고 1회 조회,
- [ ] **G-1** `position_recon_shadow` — 매분 「엔진 포지션 vs 브로커 잔고 캐시」 대조.
- [ ] **G-3** `entry_gate_stuck_shadow` — 차단 사유별 연속 지속시간 매분 누적,
- [ ] **G-6** `selfinduced_cb_shadow` — CB 발동 직전 60초에 `ConstOut` 재적합 /
- [ ] **P5-06** 분할체결 손절을 손절률 분모에서 되찾는다 — **관찰은 오늘 시작됐다**
- [ ] **P5-07** `net_breakeven_pt`(= 왕복수수료 ÷ (계약수 × 50,000)) 를 청산 시점에
- [ ] **P5-08** 자가유발 CB 발동을 진입공백 비용으로 환산 — G-6 선행.
- [ ] `tests/test_500_*.py` 5개 파일이 pytest 수집 시 `SystemExit: 0` 을 낸다
- [ ] 선행 실패 3건 정리 — `test_483_git_lock_guard[fuoption]`(형제 프로젝트 사본
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
다.** 🔴 주간회의.
- [ ] **CB② 복원 여부** — 재검토 기한 2026-08-29 경과. 절대원칙 §2 / 전환기준 ⑤.

### F-4 — 등급상 자동 가능이나 **일부러 멈춤** (근거 있음)

- [ ] **F-4 (P1)** 일일 마감 손익을 **브로커 포지션 축**과 대사 — `main.py:daily_close()`
      · 🔴 **캐시(`_integrity_broker_qty`) 기반 약한 버전은 만들지 말 것.**
        08-28 사고 당시 그 값이 `broker_cached=0ct` 였다(증권사엔 4계약).
        넣으면 「브로커 종가 포지션 확인: FLAT ✅」이 **틀린 안심**으로 찍힌다 —
        「대사 일치」 문구가 신뢰를 보증한 493차 실패와 동형이다.
      · **15:40에 잔고 TR 을 실제로 1회 거는 버전으로만** 의미가 있다.
        거래 프로세스 안에서 COM 통신을 새로 여는 변경이라 **프로그램을 켜고
        확인해야 검증된다** — 무인 자동조치 범위 밖.
      · ⇒ 사용자 승인 + 유인 검증 세션에서 착수.

### 고도화 이월 (오늘 상한 3건 소진: G-4·G-5 완료)

- [ ] **G-2** 「장 마감 후 잔고 최종 확인」 잡 — 15:50에 브로커 잔고 1회 조회,
      non-FLAT 이면 알림 + `logs/` 기록. **주문 없음 = 이중 청산 위험 0.**
      · 🔴 **다음 회차 1순위.** 이번 사고 546만원 중 대부분이 「금요일 15:50 알림
        1건」으로 회피 가능했다. `scripts/force_flat_guard.py` 를 확장하지 말고
        **그 앞단에 신설**할 것(리포트 G-2 변경대상 칸).
      · 검증: 08-28 15:50 리플레이로 `LONG 4계약` 탐지 + 최근 20거래일 오탐 0.
- [ ] **G-1** `position_recon_shadow` — 매분 「엔진 포지션 vs 브로커 잔고 캐시」 대조.
      · **캐시를 쓴다 — TR 추가 호출 0회.** 차단 없음. 섀도 4주 후 승격 판단.
      · ⚠ F-4와 같은 한계를 공유한다(캐시가 틀리면 못 잡는다) — 그래도 **갈라짐이
        발생한 분**을 잡는 것이 목적이라 가치가 다르다. 승격 시 그 한계를 명기할 것.
- [ ] **G-3** `entry_gate_stuck_shadow` — 차단 사유별 연속 지속시간 매분 누적,
      개장 후 30분 이상이면 경보 등급 상향. `_entry_block_reason` 이 이미 사유
      문자열을 만든다 = **새 계산 0회.** F-6 ⓒ항과 묶어서 구현할 것.
- [ ] **G-6** `selfinduced_cb_shadow` — CB 발동 직전 60초에 `ConstOut` 재적합 /
      `retrain_intraday` 완료 / 모델 pkl mtime 갱신 / `HealthPolicy cause=S0` 중
      하나가 있으면 `selfinduced=1` 태그. `predictions.db` 컬럼 1개. **CB 동작 무변경.**
      · CLAUDE.md 456차가 세운 「자가유발은 전환기준 ②의 근거로 쓰지 말 것」 규율을
        사람이 매번 손으로 하는 것을 없앤다. 4주 뒤 자동 제외 승격 판단.

### 제5부 수익률 방안 이월

- [ ] **P5-06** 분할체결 손절을 손절률 분모에서 되찾는다 — **관찰은 오늘 시작됐다**
      (G-5). 판정식: G-5 「미대응」이 10거래일 중 3일 이상에서 1건 이상 → F-10 승인.
- [ ] **P5-07** `net_breakeven_pt`(= 왕복수수료 ÷ (계약수 × 50,000)) 를 청산 시점에
      `predictions.db` 에 적재. **계측만 — 임계 변경 제안 없음.** 섀도 15거래일,
      `min_samples=20 且 min_days=10` 도달 시 사전등록 판정식 적용.
      · F-11이 승패 축을 이미 갈라 두었으므로 그 위에 얹으면 된다.
- [ ] **P5-08** 자가유발 CB 발동을 진입공백 비용으로 환산 — G-6 선행.

### 정비

- [ ] `tests/test_500_*.py` 5개 파일이 pytest 수집 시 `SystemExit: 0` 을 낸다
      (단독 실행 스크립트라 모듈 끝에서 `sys.exit(0)`). 전체 스위트를 돌릴 때마다
      `--ignore` 5개를 붙여야 한다. `if __name__ == "__main__":` 로 감싸거나
      `tests/scripts/` 로 옮길 것. **검사 내용 자체는 정상 통과한다.**
- [ ] 선행 실패 3건 정리 — `test_483_git_lock_guard[fuoption]`(형제 프로젝트 사본
      불일치, 08-26부터) · `test_504_pnl_history_creon_tab` 2건(504차 커밋).

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

### `data/heartbeat_MW0601_20260901.json` — 244B · 09-01 09:00:39
```json
{
 "pid": 17924,
 "written_at": "2026-09-01T09:01:09",
 "beat_epoch": 1788220868.3483934,
 "beat_age_sec": 1.0,
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

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 86개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260831-점검리포트.md` | 203.4KB | 08-31 18:13 |
| `docs/정기점검/매일점검/evidence_MW0601-20260831_post.md` | 79.5KB | 08-31 16:17 |
| `docs/정기점검/매일점검/evidence_MW0601-20260831_intra.md` | 65.5KB | 08-31 12:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20260831_pre.md` | 57.8KB | 08-31 09:00 |
| `docs/정기점검/매일점검/MW0601-20260831-8월손실일-딥다이브.md` | 22.2KB | 08-31 00:18 |
| `docs/정기점검/매일점검/dailycheck_prompt.txt` | 13.2KB | 08-31 00:05 |
| `docs/정기점검/매일점검/MW0601-20260827-점검리포트.md` | 90.4KB | 08-27 12:43 |
| `docs/정기점검/매일점검/evidence_MW0601-20260827_intra.md` | 66.2KB | 08-27 12:27 |

### `docs/정기점검/금요일점검` — 60개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/weekly_prompt.txt` | 2.6KB | 08-31 00:05 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260828.json` | 2.9KB | 08-28 15:50 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260828.md` | 4.9KB | 08-28 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260828.md` | 28.7KB | 08-28 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260828.json` | 35.2KB | 08-28 15:50 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260828.md` | 178.7KB | 08-28 15:50 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260828.json` | 97.7KB | 08-28 15:50 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260821.md` | 167.8KB | 08-23 21:57 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. `logs/20260901_WARN.log`: **Traceback** 출현 1건 — 크래시/메모리 계열
2. 메인 스레드 정지 5초 초과 **1건** (최대 6250ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
3. `logs/20260901_LEARNING.log`: **축퇴** 8건(표본)

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260901*.log` (Windows) / `grep 강제청산 logs/*20260901*.log`*