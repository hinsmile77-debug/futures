# 미륵이 증거 다이제스트 — 2026-08-25 / PRE

- 생성 2026-08-25 08:59:41 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/blissful-admiring-bell/mnt/futures`
- 점검 범위: pre (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260825` · `2026-08-25` · `260825` · `0825`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **15개** 파일 · 15개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260825.log` | 125B | 08-25 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260825.log` | 140B | 08-25 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260825.json` | 244B | 08-25 08:59 |
| `launcher_{DATE}_084000_11357.log` | 1 | `logs/Mireuk_batch/launcher_20260825_084000_11357.log` | 50.0KB | 08-25 08:59 |
| `{DATE}_DATA.log` | 1 | `logs/20260825_DATA.log` | 914B | 08-25 08:58 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260825_DEBUG.log` | 0B | 08-25 08:40 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260825_HEALTH.log` | 0B | 08-25 08:40 |
| `{DATE}_HOGA.log` | 1 | `logs/20260825_HOGA.log` | 1.2MB | 08-25 08:59 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260825_LEARNING.log` | 48.9KB | 08-25 08:59 |
| `{DATE}_MICRO.log` | 1 | `logs/20260825_MICRO.log` | 32.2KB | 08-25 08:59 |
| `{DATE}_PROBE.log` | 1 | `logs/20260825_PROBE.log` | 1.7KB | 08-25 08:58 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260825_SIGNAL.log` | 18.5KB | 08-25 08:59 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260825_SYSTEM.log` | 24.3KB | 08-25 08:59 |
| `{DATE}_TRADE.log` | 1 | `logs/20260825_TRADE.log` | 167B | 08-25 08:41 |
| `{DATE}_WARN.log` | 1 | `logs/20260825_WARN.log` | 1.2KB | 08-25 08:55 |

## 2. 코드·커밋 상태

- HEAD `f18cdad` · 브랜치 `v9-dev` · 미커밋 499건 · 실질 변경 0건 · 코드(.py) 0건 · EOL 파생 499건 (추적변경 499 · 미추적 0 · 삭제 0 · core.autocrlf=미설정) · 인덱스락 없음
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
```
M .claude/commands/dailycheck.md
 M .claude/skills/mireuk-daily-check/SKILL.md
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
 M config/krx_holidays.py
… 외 459건
```

**당일(2026-08-25) 커밋**
```
f18cdad [MW0601] 492차 후속: 배포 피처셋 vs 노이즈 하한선 대조 (§17) — 배포 67개 중 하한 초과 9개(13%)
fc9f843 [MW0601] 492차: 피처 수명(persistence) 분석 — 호라이즌 배정 근거 없음 확정 · 재검증 규약 신설 · L0/L1 참고계측 확장
```

**최근 커밋 12건**
```
f18cdad [MW0601] 492차 후속: 배포 피처셋 vs 노이즈 하한선 대조 (§17) — 배포 67개 중 하한 초과 9개(13%)
fc9f843 [MW0601] 492차: 피처 수명(persistence) 분석 — 호라이즌 배정 근거 없음 확정 · 재검증 규약 신설 · L0/L1 참고계측 확장
91c6120 [MW0601] 491차: 0824 장후 fix 9건 구현 — F-L·F-M·F-N·F-G·F-K·F-I·F-B·F-F·F-D (+ lock_guard 콘솔)
d66ec0d [MW0601] 점검 산출물 적재: 0812~0824 일일점검 증거 27건 · 리포트 2건 · 0821 주간 3종 · 26주 WFA 피처셋 재검증
4dbdf80 [MW0601] 489차: 주간회의 승인 6건 — ⑨ WFA 이관 · [46]③ 재등록+배선 · 좀비결정 7건 분류 · [8]② 계측 이식
10178cb [MW0601] 489차 A-1: CB② 카운트를 절대원칙 문구에 맞춘다 — 시간창 + 포지션 단위 (한도 무변경)
9acc983 [MW0601] 488차 후속: 라이브 데이터에 고정된 캠페인 테스트 4개 재설계 — FAIL 12건 해소
7e82dcd [MW0601] 488차: [35] 유령 하드스톱 — 439차 "모집단 소멸" 서술 MW0601 비적용 + drop-max 계측
7451a64 [MW0601] dev_memory: MW0601_이관_점검사항 7건 조사 결과 기록
f628b83 [MW0601] 멀티PC 정책 폐기 후속: 운영 문서 3건에 남은 상호조율 관행 정리
302c8b5 [MW0601] 487차 후속 cherry-pick 조정: ConstOut 채널 번호 [51] 유지 (F-9 재배정 미적용)
1c4c6d1 [MW0602] 487차 후속: F-8(B)+F-9 구현 — 채널 [50]/[54] 브랜치 미가용 표기(감지형) + ConstOut [51]→[54] 재배정
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
| `VALIDATION_CAMPAIGN["mode"]` | `standing` | `standing` | 일치 | 2026-08-01 상시 운영 전환 |

> 이 표는 **의도한 예외가 여전히 의도대로인지** 보는 것이다. `불일치`는 누군가 바꿨다는 뜻이고, 바꿨다면 `dev_memory/DECISION_LOG.md` 에 근거가 있어야 한다.

_이 브랜치(`v9-dev`) 범위 밖 **5건** — 표에서 제외했다(계측 4원칙 ③): `MODEL_LABEL_STATE_UNLOCK_ENABLED`(→dev), `PRE_RETRAIN_DONE_BY_EOD_ENABLED`(→dev), `ZONE_ENTRY_BAN_ENFORCE`(→dev), `ZONE_ENTRY_BAN_SHADOW_ENABLED`(→dev), `PIPE_LATENCY_EXCLUDE_MODEL_SWAP`(→dev)._
> 제외는 "없어도 된다"가 아니라 "이 브랜치에는 기능 자체가 없다"는 뜻이다. 이식 여부는 별개 안건이며 주간회의에서 정한다.

### 차단 게이트 전수 인벤토리 — 32개 중 **9개 꺼짐**

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
| `MC_CONF_GAP_ALERT_ENABLED` | True | — |
| `SIGNAL_DECAY_EXIT_ENABLED` | True | — |
| `SIZING_TARGET_CAPITAL_ENABLED` | True | — |
| `TP1_TICK_ENABLED` | True | — |
| `VOLATILITY_BURST_GUARD_ENABLED` | True | — |

## 4. 마커·리포트 · 로그 다이제스트

_본문 미열람(설정): `20260825_HOGA.log` 1.2MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/11개 (중요도순). 제외: `launcher_20260825_084000_11357.log`, `freeze_sentinel_20260825.log`, `force_flat_guard_20260825.log`_

### `logs/20260825_TRADE.log` — 167B · 2행 · 최종 08:41:43

- 형식 평문 · 시각 인식 2행 · INFO=2

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-25 08:41:38 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-25 08:41:43 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
  …
2026-08-25 08:41:38 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-25 08:41:43 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×2

**컴포넌트 상위 15** — `Position`×1, `ProfitGuard`×1

### `logs/20260825_WARN.log` — 1.2KB · 14행 · 최종 08:55:17

- 형식 평문 · 시각 인식 14행 · WARNING=14

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-25 08:41:46 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-08-25 08:41:46 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 63ms
2026-08-25 08:41:46 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 188ms account=333044256
2026-08-25 08:41:49 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3016ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3016 band=INFO since_pipe_s=NA
2026-08-25 08:41:53 [WARNING] SYSTEM: [LiveDBG] _restore_panels_worker 지연 3578ms — live 중단 원인 분석용
  …
2026-08-25 09:00:01 [WARNING] SYSTEM: [PipePerf] total=1683ms | S0=2ms S1=12ms S2=0ms S3=0ms S4=125ms S5=799ms S6=706ms S7=11ms S8=28ms
2026-08-25 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1683ms | quality=0.86 | cache_age=9s | exceptions_10m=0
2026-08-25 09:00:02 [WARNING] SYSTEM: [CB⑤] 파이프라인 1683ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s]
2026-08-25 09:00:02 [WARNING] SYSTEM: [CB⑤] 파이프라인 1683ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s]
2026-08-25 09:00:08 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 8625ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=8625 band=WARN since_pipe_s=0.2
```

</details>

**WARNING — 태그 5종 (상위 5)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 7 | 08:41:46 | 09:00:08 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `Canary` | 2 | 08:55:17 | 08:55:17 | scaler 노후=0h  z경고피처=13개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| `PipePerf` | 2 | 09:00:01 | 09:00:01 | total=1683ms | S0=2ms S1=12ms S2=0ms S3=0ms S4=125ms S5=799ms S6=706ms S7=11ms S8=28ms |
| `CB⑤` | 2 | 09:00:02 | 09:00:02 | 파이프라인 1683ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `Health` | 1 | 09:00:01 | 09:00:01 | level=WARNING degraded=OFF | latency=1683ms | quality=0.86 | cache_age=9s | exceptions_10m=0 |

**채널** — `SYSTEM`×13, `HEALTH`×1

**컴포넌트 상위 15** — `LiveDBG`×7, `Canary`×2, `PipePerf`×2, `CB⑤`×2, `Health`×1

### `logs/20260825_SYSTEM.log` — 24.3KB · 206행 · 최종 08:59:33

- 형식 평문 · 시각 인식 199행 · INFO=199, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-25 08:40:54 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=5080 | 행감지=30s all_threads=True
2026-08-25 08:41:25 [INFO] SYSTEM: [System] DB 초기화 완료
2026-08-25 08:41:25 [INFO] SYSTEM: [System] 미륵이 초기화
2026-08-25 08:41:25 [INFO] SYSTEM: 미륵이 초기화
2026-08-25 08:41:25 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-08-24) 종가 버퍼 로드: 384봉
  …
2026-08-25 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.033 level=0 (heartbeat)
2026-08-25 09:00:01 [INFO] SYSTEM: [S6Detail] ensemble=63ms checklist_pre=34ms meta_gate=485ms gates=11ms imp=0ms shap=16ms corr=0ms dash_ui=1ms tail=95ms
2026-08-25 09:00:01 [INFO] SYSTEM: [PipePerf][DBG] total=1683ms | S0=2ms S1=12ms S2=0ms S3=0ms S4=125ms S5=799ms S6=706ms S7=11ms S8=28ms
2026-08-25 09:00:07 [INFO] SYSTEM: [CybosRT-TICK] #2200 code=A0569 raw_time=90002 parsed=09:00:02 price=1026.32 vol=6 bid1=1026.30 ask1=1026.64 flag=49 side=BUY anchor=6/0
2026-08-25 09:00:15 [INFO] SYSTEM: [CybosRT-TICK] #2300 code=A0569 raw_time=90015 parsed=09:00:15 price=1025.90 vol=1 bid1=1025.90 ask1=1026.38 flag=50 side=SELL anchor=0/1
```

</details>

**채널** — `SYSTEM`×199

**컴포넌트 상위 15** — `CybosRT-TICK`×28, `CybosSub`×21, `System`×17, `TickUI`×15, `CybosRT-ROLLOVER`×15, `BAR-CLOSE`×15, `CVD-ANCHOR`×15, `SYSTEM`×9, `PreMarket`×9, `CybosRT-START`×6, `Notify`×5, `BrokerSync`×4, `BalanceUI`×4, `-`×4, `EarlyWarmup`×3

### `logs/20260825_SIGNAL.log` — 18.5KB · 208행 · 최종 08:59:00

- 형식 평문 · 시각 인식 208행 · WARNING=109, INFO=99

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-25 08:40:48 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.426
2026-08-25 08:40:48 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.442
2026-08-25 08:40:48 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.421
2026-08-25 08:40:48 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.418
2026-08-25 08:40:48 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.426
  …
2026-08-25 09:00:02 [WARNING] SIGNAL: [ScalerFloor] 30m 'macro_risk_on' scale=0.4386 → floor=0.50 적용 (z-score 폭발 방지)
2026-08-25 09:00:02 [WARNING] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0396 → floor=0.15 적용 (z-score 폭발 방지)
2026-08-25 09:00:02 [WARNING] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.0993 → floor=0.20 적용 (z-score 폭발 방지)
2026-08-25 09:00:02 [INFO] SIGNAL: [ScalerRefresh] ts=08:59 trigger=C_PERIODIC elapsed=infmin n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.03s
2026-08-25 09:00:10 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → GAP_OPEN: 시초가 급변 — 고신뢰·소규모 진입만 허용
```

</details>

**WARNING — 태그 5종 (상위 5)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerRefresh` | 60 | 08:45:17 | 09:00:02 | 1m CORE 'ofi_norm' raw_std≈0(0.0231) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ScalerFloor` | 30 | 09:00:02 | 09:00:02 | 1m 'macro_vix' scale=0.0144 → floor=0.10 적용 (z-score 폭발 방지) |
| `Model` | 12 | 09:00:00 | 09:00:00 | 1m 극단 z-score 4개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 6 | 09:00:00 | 09:00:00 | ts=08:59 horizon=1m age=1m max_z=+17.78(cancel_add_ratio) extreme=4 |
| `ConfFloorGuard` | 1 | 09:00:01 | 09:00:01 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4420 (conf_floor=0.330, min_conf=0.442, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×208

**컴포넌트 상위 15** — `ScalerFloor`×96, `ScalerRefresh`×67, `Model`×18, `DynMC`×7, `ScalerMonitor`×6, `TimeRouter`×3, `SIGNAL`×2, `Ensemble`×2, `EnsembleGater`×1, `FeatureBuilder`×1, `GapOffset`×1, `DayRegimeShadow`×1, `AutoMasked`×1, `ConfFloorGuard`×1, `ZeroDiag`×1

### `logs/20260825_LEARNING.log` — 48.9KB · 276행 · 최종 08:59:00

- 형식 평문 · 시각 인식 276행 · WARNING=133, INFO=143

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-25 08:41:27 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-08-25 08:41:29 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00031 auc=0.443 out_max=0.3626 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
2026-08-25 08:41:29 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00052 auc=0.500 out_max=0.3127 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과
2026-08-25 08:41:29 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00022 auc=0.538 out_max=0.2942 (n=85) → 보정 재적용
2026-08-25 08:41:29 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2942 < conf_floor=0.3300 (span=0.00022 auc=0.538 out_max=0.2942, 기저율=0.2941 n=85) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
  …
2026-08-25 08:55:17 [INFO] LEARNING: [MetaConf] 상태 복원 완료: meta_conf_state.pkl (fitted=[추세장, 횡보장, 급변장, 혼합], total=11203, ver=5)
2026-08-25 08:55:17 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-08-25 08:59:00 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-08-25 09:00:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0000% buf_n=0 nonzero=0 prev_p=0.00 cur_p=1026.22
2026-08-25 09:00:02 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=500 feat=97
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 133 | 08:41:29 | 08:41:38 | 축퇴 감지 — span=0.00031 auc=0.443 out_max=0.3626 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과 |

**채널** — `LEARNING`×276

**컴포넌트 상위 15** — `Calibration`×260, `ScalerWarmup`×7, `ExtremityCorrector`×2, `Consolidator`×2, `RF`×1, `DriftAdjuster`×1, `SHAP`×1, `MetaConf`×1, `sigma`×1

### `logs/20260825_MICRO.log` — 32.2KB · 92행 · 최종 08:59:31

- 형식 평문 · 시각 인식 92행 · DEBUG=92

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-25 08:45:17 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1029.92/1 ask1=1030.22/1 mp={'microprice_tick': 1030.07, 'midprice_tick': 1030.07, 'depth_bias_tick': -0.1543} mlofi_tick=None queue=None
2026-08-25 08:45:17 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1029.98/1 ask1=1030.22/1 mp={'microprice_tick': 1030.1, 'midprice_tick': 1030.1, 'depth_bias_tick': -0.1543} mlofi_tick=2.2833 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -…
2026-08-25 08:45:17 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1029.92/1 ask1=1030.22/1 mp={'microprice_tick': 1030.07, 'midprice_tick': 1030.07, 'depth_bias_tick': -0.1543} mlofi_tick=-2.2833 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
2026-08-25 08:45:17 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1029.82/1 ask1=1030.22/1 mp={'microprice_tick': 1030.02, 'midprice_tick': 1030.02, 'depth_bias_tick': -0.1131} mlofi_tick=-2.2833 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
2026-08-25 08:45:17 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1029.50/1 ask1=1029.92/1 mp={'microprice_tick': 1029.71, 'midprice_tick': 1029.71, 'depth_bias_tick': 0.033} mlofi_tick=-5.4167 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
  …
2026-08-25 08:59:45 [DEBUG] MICRO: [MICRO-TICK] #5400 bid1=1026.60/1 ask1=1027.00/1 mp={'microprice_tick': 1026.8, 'midprice_tick': 1026.8, 'depth_bias_tick': 0.0} mlofi_tick=1.3 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.0,…
2026-08-25 08:59:57 [DEBUG] MICRO: [MICRO-TICK] #5500 bid1=1026.86/1 ask1=1027.24/1 mp={'microprice_tick': 1027.05, 'midprice_tick': 1027.05, 'depth_bias_tick': -0.2533} mlofi_tick=0.2 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
2026-08-25 09:00:00 [DEBUG] MICRO: [MICRO-MINUTE] #15 ts=2026-08-25 08:59:00 close=1026.22 bias=-0.010975 slope=0.271690 depth_bias=-0.1709 mlofi_norm=0.018576 mlofi_pressure=1 mlofi_slope=-29.390000 queue_signal=0.0461 queue_ma=0.0224 queue_momentum=0.0262 depletion=0.4979 refill=0.5021 imbalance_…
2026-08-25 09:00:07 [DEBUG] MICRO: [MICRO-TICK] #5600 bid1=1025.94/1 ask1=1026.22/1 mp={'microprice_tick': 1026.08, 'midprice_tick': 1026.08, 'depth_bias_tick': -0.3965} mlofi_tick=6.1 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
2026-08-25 09:00:13 [DEBUG] MICRO: [MICRO-TICK] #5700 bid1=1025.72/1 ask1=1026.26/1 mp={'microprice_tick': 1025.99, 'midprice_tick': 1025.99, 'depth_bias_tick': -0.007} mlofi_tick=-0.05 queue={'depletion_bid': 3.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
```

</details>

**채널** — `MICRO`×92

**컴포넌트 상위 15** — `MICRO-TICK`×77, `MICRO-MINUTE`×15

### `logs/20260825_DATA.log` — 914B · 5행 · 최종 08:58:51

- 형식 평문 · 시각 인식 5행 · INFO=5

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-25 08:58:21 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=149991 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-08-25 08:58:21 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-08-25 08:58:51 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=149988 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-08-25 08:58:51 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-08-25 09:00:00 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
  …
2026-08-25 08:58:21 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=149991 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-08-25 08:58:21 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-08-25 08:58:51 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=149988 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-08-25 08:58:51 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-08-25 09:00:00 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
```

</details>

**채널** — `DATA`×5

**컴포넌트 상위 15** — `CybosInvestor`×4, `DivergencePanel`×1

### `logs/20260825_PROBE.log` — 1.7KB · 11행 · 최종 08:58:51

- 형식 평문 · 시각 인식 11행 · WARNING=10, INFO=1

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-25 08:41:47 [INFO] PROBE: [CybosInvestorProbe] not implemented; extra_codes=['A0569']
2026-08-25 08:58:21 [WARNING] PROBE: [CybosProbe] CpSysDib.CpSvrNew7221 dispatch/request failed: (-2147221008, 'CoInitialize가 호출되지 않았습니다.', None, None)
2026-08-25 08:58:21 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-08-25 08:58:21 [WARNING] PROBE: [CybosProbe] CpSysDib.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-08-25 08:58:21 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrade dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
  …
2026-08-25 08:58:51 [WARNING] PROBE: [CybosProbe] CpSysDib.CpSvrNew7221 dispatch/request failed: (-2147221008, 'CoInitialize가 호출되지 않았습니다.', None, None)
2026-08-25 08:58:51 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-08-25 08:58:51 [WARNING] PROBE: [CybosProbe] CpSysDib.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-08-25 08:58:51 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrade dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-08-25 08:58:51 [WARNING] PROBE: [CybosProbe] CpSysDib.FutureTrade dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `CybosProbe` | 10 | 08:58:21 | 08:58:51 | CpSysDib.CpSvrNew7221 dispatch/request failed: (-2147221008, 'CoInitialize가 호출되지 않았습니다.', None, None) |

**채널** — `PROBE`×11

**컴포넌트 상위 15** — `CybosProbe`×10, `CybosInvestorProbe`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 0 |
| 진입 등록(`[Position] 진입`) | 0 |
| 체결(`[체결진입]`) | 0 |
| 청산(`체결청산`) | 0 |
| 차단(`[차단]`) | 0 |
| 사이저 호출(`[Sizer]`) | 0 |

### 메인 스레드 블로킹 2건 · 최대 8625ms · 5초 초과 1건

상위 — 8625ms, 3016ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:00:08 | 8625ms | 1683ms | **6942ms (80%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260825_WARN.log`
```
--- 메인 스레드 블로킹 ×2(표본)
08:41:49 2026-08-25 08:41:49 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3016ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3016 band=INFO since_pipe_s=NA
09:00:08 2026-08-25 09:00:08 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 8625ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=8625 band=WARN since_pipe_s=0.2
```

### `logs/20260825_SYSTEM.log`
```
--- PSI ×1(표본)
09:00:00 2026-08-25 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.033 level=0 (heartbeat)
```

### `logs/20260825_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
09:00:01 2026-08-25 09:00:01 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4420 (conf_floor=0.330, min_conf=0.442, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- 기동 복원 ×7(표본)
08:40:48 2026-08-25 08:40:48 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.426
08:40:48 2026-08-25 08:40:48 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.442
08:40:48 2026-08-25 08:40:48 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.421
08:40:48 2026-08-25 08:40:48 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.418
```

### `logs/20260825_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:41:29 2026-08-25 08:41:29 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00031 auc=0.443 out_max=0.3626 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
08:41:29 2026-08-25 08:41:29 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00052 auc=0.500 out_max=0.3127 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과
08:41:29 2026-08-25 08:41:29 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00022 auc=0.538 out_max=0.2942 (n=85) → 보정 재적용
08:41:29 2026-08-25 08:41:29 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2942 < conf_floor=0.3300 (span=0.00022 auc=0.538 out_max=0.2942, 기저율=0.2941 n=85) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260825_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:38 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:41 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260825_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 6 | 08:41:46 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 8 | 08:55:17 [WARNING] scaler 노후=0h  z경고피처=13개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 8 | 08:55:17 [WARNING] scaler 노후=0h  z경고피처=13개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |

- 이 로그 생존구간: 08:41 ~ 09:00

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260825_SYSTEM.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 87 | 08:40:54 [INFO] 활성화 | file=logs\crash_fault.log PID=5080 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 98 | 08:49:00 [INFO] code=A0569 from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 68 | 08:54:00 [INFO] code=A0569 from=08:53 to=08:54 |

- 이 로그 생존구간: 08:40 ~ 09:00

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260825_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 67 | 08:45:17 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0231) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 134 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0235) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 127 | 08:55:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0258) → identity(0,1) 강제 (FLAT 100% 방지) |

- 이 로그 생존구간: 08:40 ~ 09:00

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260824 | 15:40 | 로그 본문 |
| 20260821 | 15:40 | 로그 본문 |
| 20260820 | 21:17 | 로그 본문 |
| 20260819 | 17:02 | 로그 본문 |
| 20260818 | 15:40 | 로그 본문 |
| **중앙값** | **15:40** | 기준선 |
| **오늘 20260825** | **09:00** | 로그 본문 |

- 델타 **-400분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.3MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 산출 — 피처별 수명 스펙트럼 (분류·정제 통과 56개 중 **25개 발굴**)
### 왜 분류가 먼저여야 하는가 — §14 초판 tau 상위 15개 중 **11개가 부적격**이었다
### 오측정 10건 — 전부 통계 지식이 아니라 **절차 부재**였다
### 부수 발견 — 중복·선형종속
### 배선 2건 — 둘 다 **판정 무영향**(사전등록 §9-4 불변)
### 문서 정정 2건 (재인용 금지)
### 판정 경로 무접촉 확인
### §17 후속 (같은 세션) — 배포 피처셋 vs 노이즈 하한선 대조
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
. 실제 손실은 ① **계열 검정의 검정력**
   (§14-5 p=0.1426) ② SHAP 기여 분산 ③ 신호 다양성 과대 표시.
   정정 반영: CLAUDE.md · 스펙 §3 · 보고서 §15-7 · 권고 A-15.
2. **CLAUDE.md 455차의 "L1(`core_feature_discovery` … 노이즈 벤치마크 포함)"이 코드와
   어긋났다** — 노이즈 벤치마크는 L1'에만 있었다(461차 F-3·483차와 같은 유형).
   이번 배선으로 실제로 병기가 생겨 정확한 문구로 갱신했다.

### 판정 경로 무접촉 확인

`build_matrix`·`analyze`·`classify` 시그니처 무변경. `feature_health_report.collect()`
반환 확장은 자기 파일 안에서만 쓰이고 `generate_featureset_health_report.py`는 자체
collect를 갖고 있어 영향 범위가 닫힌다. 주간 리포트 등급 분포(`DEAD=14 CRITICAL=20
WARN=9 OK=101`)·신규 이상 3건 수정 전후 동일, 섹션 구조 차이는 `§2-c` 추가뿐.
py37_32 컴파일 + py310_64 실행 + `horizon_signal_tradability`·`ic_decay_catalog`
import 회귀까지 확인.

산출물: 보고서 §14~§16, `docs/정기점검/26주WFA_MW0601-20260824/lifetime*.{py,json,txt}`
(공통기반 `lifetime_lib.py` — 하루 격자 정렬·NaN-aware ACF·연속값 tau·censored 표기).

**⚠ 이 세션은 사용자 지시로 커밋했다** — 491차 후속(§12·§13 · `live_only`·`live_null`·
`corr`·`robustness`)의 미커밋분이 같은 커밋에 포함된다(파일이 섞여 분리 불가).

### §17 후속 (같은 세션) — 배포 피처셋 vs 노이즈 하한선 대조

사용자 질문 "h=5 하한 미달 69개를 제외한 피처를 호라이즌 피처셋으로 쓰고 있는지 확인".
**답은 정반대다.** 배포 진실(`feature_names_{hz}.pkl`) 대조 결과:

| 호라이즌 | 배포 | 하한초과 | 하한미달 | 미평가 |
|---|---|---|---|---|
| 1m | 8 | 1 | 6 | 1 |
| 3m | 12 | 1 | 9 | 2 |
| 5m | 12 | 1 | 6 | 5 |
| 10m | 11 | 3 | 3 | 5 |
| 15m | 13 | 3 | 7 | 3 |
| **30m** | 11 | **0** | 7 | 4 |
| 합계 | 67 | **9 (13%)** | 38 | 20 |

- h=5 하한 초과 **12개 중 배포된 것은 `vwap_position` 하나**다. 나머지 11개는 미배포.
- **30m은 하한 초과가 22개인데 배포는 0개.** 그 창 최고인 `vwap_position`(|t|=10.46)이
  30m 피처셋에 없다. 296차 앙상블 퇴역과 정합하나 **30m은 CB③의 유일한 입력원**이다.
- CORE 중 하한을 넘는 것은 `vwap_position`(6.68)뿐 — `ofi_norm` **0.07** ·
  `cvd_divergence` 0.74 · `cvd_delta_norm` 0.57. 고도화3 63피처 전수검증의
  "CORE가 노이즈와 구분되지 않는다"가 다른 창·다른 방법으로 재확인됐다.
- 10m이 가장 양호(배포 11개 중 미달 3개). 단 중기 CORE 체크리스트는 도달 불가(474차).

**원인은 선정 기준이 IC가 아니라 SHAP이기 때문**이다. 이 불일치는 0802 계획 §2의
**L5(모델정합) 2×2 분면**("L1 비유의 ∧ SHAP 상위 → DROP 후보")이 잡으려던 바로 그것인데,
L5는 Phase C로 **미구현**이라 자동으로 드러나지 않고 있었다.
⇒ **A-19 신설: L5 구현을 A-18(하한선 조건화)보다 먼저.** 분면 없이 조건화하면
"잡음을 크게 쓰는 중"과 "단변량으로만 약한 것"을 구분하지 못한다.
⚠ 지금 조건화하면 배포 67개 중 38개가 자격 상실, 30m은 전량 탈락한다.

⚠ **"IC 높은 걸 넣으면 된다"로 가면 안 된다**: 하한 초과 상위 5개는 선형종속 수급 군집이고
전부 누적/비정상형(ACF1 0.994~0.998)이라 동시 추세 공유일 수 있다. 같은 창 L2 합격은 0셀.
미평가 20개는 이진 플래그로 `MIN_DISTINCT=20` 미달이며 "나쁘다"가 아니라 "못 잰다"이다.

⚠ **부수 관찰**: 중복 판정이 창에 의존한다 — 라이브 31일에서 |r|=0.999976이던
`foreign_retail_divergence ~ retail_futures_net`이 40거래일 군집에는 안 나오고
h=15 |t|가 4.64 vs 0.08로 갈린다. A-15에 조사 항목으로 편입.

산출물: 보고서 §17, `lifetime_deployed_vs_noise.{py,txt,json}`.
기존 스크립트 무수정(판정 경로 무접촉).

```

</details>

### dev_memory/NEXT_TODO.md — 1.2MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 490차 후속2 항목 중 이번 조사로 갱신된 것
## MW0601 491차 후속2 — 배터리 통계 취약점 3종 후속 (팻테일·동률·점질량)
### 참고 — 이번 점검에서 "이미 정상"으로 확인된 것 (재조사 불필요)
### 신규 분석 스크립트 작성 시 상시 주의
## 492차 (2026-08-25) — 피처 수명 분석 후속 · 주간회의 안건
### 주간회의 안건 (신규)
### 다음 26주 창 사전등록 대상
### 상시 주의 (규약)
```

미완료 체크박스 **1893건** (끝에서 30건)
```
- [ ] **FZ-2 하드 종료 승격 여부 (주간회의 안건)** —
- [ ] **FZ-2 라이브 첫 발화·오탐 관찰 (다음 거래일부터)** —
- [ ] **F-L·F-N 라이브 왕복 확인 (다음 15:40)** —
- [ ] **F-I·F-K·F-G 첫 라이브 값 확인 (다음 거래일 장후)** —
- [ ] **A-6** L2(`horizon_signal_tradability.py`) 출력에 **노이즈 하한선 병기**.
- [ ] **A-7** L1·L2 출력 헤더에 관찰창의 **일중/오버나이트 드리프트** 1줄.
- [ ] **B-6** 라이브 **SHORT 건당 손익이 LONG의 1/12**인 이유 조사.
- [ ] **B-7** `scripts/backfill_features.py:_BACKFILL_COMPUTED_KEYS` **26키 전체**의
- [ ] **A-8** L2에 **잭나이프 t** 병기 + `drop_worst_days` 적용 옵션.
- [ ] **A-9** L1·L2에 **동률 탈락 건수·비율** 출력 (계측 4원칙 ③).
- [ ] **A-10** **층간 게이트** — L1 유효일 0 또는 `MIN_DAYS` 미만인 피처를 L2 합격자로 올리지 않는다
- [ ] **A-11** **점질량·거래수 정규화 지표** 병기 — 피처별 최빈값 질량, 질량 제외 유효표본,
- [ ] **B-8** rank 구현 **사본 8벌 → 정본 1벌 통합**
- [ ] **B-9** **clip 경계 인공 점질량** 조사.
- [ ] 새 분석 스크립트 스캐폴드에 **`utils.dll_bootstrap.ensure_conda_dll_path()` 기본 포함**.
- [ ] **A-12** 수명 기반 호라이즌 분리는 **추진하지 않는다** — §14 여섯 갈래 무의미 ·
- [ ] **A-13** `vwap_position` **h=30 최강**(t=−9.12, 유일한 다중비교 생존)을 §7-1 부호
- [ ] **A-14** `opt_pcr_extreme_signed` / `opt_pcr_norm` **완전 중복** 처분
- [ ] **A-15** 수급 5종 **유효 자유도 재산정** — 계열·그룹 집계에 반영.
- [ ] **A-16** 옵션 체인 5종(계단형)에 **갱신주기 10분** 명시 · decay 계열 지표 산출 대상
- [ ] **A-17** 🔴 **배포 중인데 시간축 이상인 피처 6건 처분** — 주간 리포트 §2-c 첫 실행:
- [ ] **A-18** L1 **노이즈 하한선을 통과 조건에 포함**할지 결정.
- [ ] **A-19** 🔴 **L5(모델정합) 구현을 A-18보다 먼저 한다** — 0802 계획 Phase C.
- [ ] **B-10** 계열별 호라이즌 특화를 **사전등록 항목**으로 등록. §14-5 순열 p=0.1426은
- [ ] **B-11** 순열·집계 코드에 **NaN 가드 공통화**. 이번에 NaN 전파가 p를 0에 붙였다
- [ ] **B-12** tau ≤ 1분 16개는 **1분봉 격자로 판정 불가** — 초 단위 데이터가 있어야 한다.
- [ ] **B-13** 피처 등록 시 **유형 태그(D/B/C/S/I/N)를 메타데이터로 부착**.
- [ ] 26주 재검증 착수 시 **`피처_재검증_및_호라이즌배정_원칙.md`를 먼저 열 것.**
- [ ] **임계 상수가 두 곳에 복사돼 있다** — `feature_health_report.py`의 `SHAPE_*` ↔
- [ ] 자기상관·수명 지표의 널은 **`shuffle`이다.** `phase_randomize`는 ACF를 보존해
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
에 반영.
      ⚠ 다중비교 임계 영향은 **0.033으로 미미**(2026-08-25 정정). 실제 손실은 계열 검정
      검정력이다. 비용 중.
      🔴 **[§17 추가] 중복 판정이 창에 의존한다** — 라이브 31일에서 `|r|=0.999976`이던
      `foreign_retail_divergence ~ retail_futures_net`이 40거래일 L1 군집에는 안 나오고,
      h=15 `|t|`가 **4.64 vs 0.08**로 갈린다(`|r|≈1`이면 불가능한 차이). 결측 패턴
      차이인지 창 의존성인지 조사할 것.
- [ ] **A-16** 옵션 체인 5종(계단형)에 **갱신주기 10분** 명시 · decay 계열 지표 산출 대상
      제외. `opt_chain_pcr`은 §3 30m CORE다. 비용 소.
- [ ] **A-17** 🔴 **배포 중인데 시간축 이상인 피처 6건 처분** — 주간 리포트 §2-c 첫 실행:
      `macro_us10y_chg`(3m·10m) · `macro_vix`(10m·30m) · `macro_sp500_chg`(10m) ·
      `time_cos`(30m, 결정론형) · `opt_pcr_extreme`(10m) · `opt_pcr_bearish`(30m).
      전부 **하루 안에서 상수**다. ※ CLAUDE.md가 이미 `macro_vix`를 "일봉 → 분봉 상수"로
      CORE 강등한 이력과 일치. 비용 중.
- [ ] **A-18** L1 **노이즈 하한선을 통과 조건에 포함**할지 결정.
      ⚠ **기준 강화 = 사전등록 변경**이라 주간회의 전용. 지금은 병기(▽)만 하고 판정과 무관.
      🔴 **[§17 추가] 조건화하면 배포 67개 중 38개가 후보 자격을 잃는다. 30m은 전량 탈락.**
      배포 피처셋과 하한선은 현재 거의 무관하다 — 하한 초과 9개(13%)뿐이고, h=5에서는
      초과 12개 중 배포된 것이 `vwap_position` 하나다. CORE도 `vwap_position`(6.68)만
      넘고 `ofi_norm` **0.07** · `cvd_divergence` 0.74 · `cvd_delta_norm` 0.57은 미달인데,
      절대원칙 §3은 CORE를 **교체 불가**로 못 박고 있다 — 문턱 문제인지 피처 문제인지
      먼저 가려야 한다.
- [ ] **A-19** 🔴 **L5(모델정합) 구현을 A-18보다 먼저 한다** — 0802 계획 Phase C.
      §17이 드러낸 것은 **선정 기준(SHAP)과 검정 기준(IC)이 어긋난다**는 사실이고,
      L5의 2×2 분면(L1 비유의 ∧ SHAP 상위 → DROP 후보)이 정확히 그 지점을 분해한다.
      분면 없이 하한선만 조건화하면 '잡음을 크게 쓰는 중'과 '단변량으로만 약한 것'을
      구분하지 못한다. 비용 중.

### 다음 26주 창 사전등록 대상

- [ ] **B-10** 계열별 호라이즌 특화를 **사전등록 항목**으로 등록. §14-5 순열 p=0.1426은
      기각이 아니라 **판정 미달**이다. 등록문에 고정할 것: 대상 필터(유형 N + 중복 축약) ·
      계열 정규식 **문자열 그대로** · 통계량(**기울기**, argmax 아님 — h=30 편향 방어) ·
      순열 20,000회 · **p<0.05 불변** · 계열당 **유효 자유도 ≥ 5** · 백필 제외.
- [ ] **B-11** 순열·집계 코드에 **NaN 가드 공통화**. 이번에 NaN 전파가 p를 0에 붙였다
      (실제 0.1426). 다른 배터리에도 같은 패턴이 있을 수 있다.
- [ ] **B-12** tau ≤ 1분 16개는 **1분봉 격자로 판정 불가** — 초 단위 데이터가 있어야 한다.
      "수명이 없다"가 아니라 "못 잰다"이다. 비용 대.
- [ ] **B-13** 피처 등록 시 **유형 태그(D/B/C/S/I/N)를 메타데이터로 부착**.
      분류 없이 지표를 매기면 다른 양을 잰다(§14 초판 상위 15개 중 11개 부적격).

### 상시 주의 (규약)

- [ ] 26주 재검증 착수 시 **`피처_재검증_및_호라이즌배정_원칙.md`를 먼저 열 것.**
      L1→L2→L3를 바로 돌리지 말고 **유형 분류 → 중복 축약 → 데이터 정제**를 선행한다.
      CLAUDE.md 「주기적 재검증 항목」에 못 박혀 있다.
- [ ] **임계 상수가 두 곳에 복사돼 있다** — `feature_health_report.py`의 `SHAPE_*` ↔
      규약 문서 §2. 한쪽만 바꾸면 주간 리포트와 26주 재검증이 다른 판정을 낸다.
- [ ] 자기상관·수명 지표의 널은 **`shuffle`이다.** `phase_randomize`는 ACF를 보존해
      `tau_null ≈ tau_real`이 되어 검정이 조용히 무력화된다(에러가 안 난다).

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

### `data/heartbeat_MW0601_20260825.json` — 244B · 08-25 08:59:17
```json
{
 "pid": 5080,
 "written_at": "2026-08-25T09:00:17",
 "beat_epoch": 1787616017.0765476,
 "beat_age_sec": 0.9,
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

### `docs/정기점검/매일점검` — 68개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260824-점검리포트.md` | 191.2KB | 08-24 16:39 |
| `docs/정기점검/매일점검/evidence_MW0601-20260824_post.md` | 70.6KB | 08-24 16:21 |
| `docs/정기점검/매일점검/evidence_MW0601-20260824_intra.md` | 65.2KB | 08-24 12:26 |
| `docs/정기점검/매일점검/evidence_MW0601-20260824_pre.md` | 47.4KB | 08-24 08:59 |
| `docs/정기점검/매일점검/dailycheck_prompt.txt` | 13.0KB | 08-23 16:51 |
| `docs/정기점검/매일점검/MW0601-20260821-점검리포트.md` | 208.7KB | 08-21 16:54 |
| `docs/정기점검/매일점검/evidence_MW0601-20260821_post.md` | 74.4KB | 08-21 16:22 |
| `docs/정기점검/매일점검/evidence_MW0601-20260821_intra.md` | 57.0KB | 08-21 12:27 |

### `docs/정기점검/금요일점검` — 58개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/weekly_prompt.txt` | 2.4KB | 08-24 15:09 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260821.md` | 167.8KB | 08-23 21:57 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260821.md` | 4.9KB | 08-21 15:50 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260821.json` | 2.9KB | 08-21 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260821.md` | 26.2KB | 08-21 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260821.json` | 34.4KB | 08-21 15:50 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260821.json` | 91.9KB | 08-21 15:49 |
| `docs/정기점검/금요일점검/MW0602/0816_주간회의_검토보고_MW0602.md` | 39.2KB | 08-20 21:31 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. 메인 스레드 정지 5초 초과 **1건** (최대 8625ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
2. `logs/20260825_LEARNING.log`: **축퇴** 8건(표본)

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260825*.log` (Windows) / `grep 강제청산 logs/*20260825*.log`*