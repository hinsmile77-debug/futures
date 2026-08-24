# 미륵이 증거 다이제스트 — 2026-08-20 / PRE

- 생성 2026-08-20 09:01:07 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/zealous-festive-ritchie/mnt/futures`
- 점검 범위: pre (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260820` · `2026-08-20` · `260820` · `0820`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **13개** 파일 · 13개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260820.json` | 244B | 08-20 09:01 |
| `launcher_{DATE}_084001_9654.log` | 1 | `logs/Mireuk_batch/launcher_20260820_084001_9654.log` | 54.0KB | 08-20 09:01 |
| `{DATE}_DATA.log` | 1 | `logs/20260820_DATA.log` | 1.1KB | 08-20 09:01 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260820_DEBUG.log` | 580B | 08-20 09:01 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260820_HEALTH.log` | 142B | 08-20 09:01 |
| `{DATE}_HOGA.log` | 1 | `logs/20260820_HOGA.log` | 1.7MB | 08-20 09:01 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260820_LEARNING.log` | 47.8KB | 08-20 09:01 |
| `{DATE}_MICRO.log` | 1 | `logs/20260820_MICRO.log` | 42.0KB | 08-20 09:01 |
| `{DATE}_PROBE.log` | 1 | `logs/20260820_PROBE.log` | 1.7KB | 08-20 08:58 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260820_SIGNAL.log` | 19.4KB | 08-20 09:01 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260820_SYSTEM.log` | 29.3KB | 08-20 09:01 |
| `{DATE}_TRADE.log` | 1 | `logs/20260820_TRADE.log` | 167B | 08-20 08:41 |
| `{DATE}_WARN.log` | 1 | `logs/20260820_WARN.log` | 1.7KB | 08-20 09:01 |

## 2. 코드·커밋 상태

- HEAD `f94536f` · 브랜치 `v9-dev` · 미커밋 457건
```
M .claude/commands/dailycheck.md
 M .claude/skills/mireuk-daily-check/RUN_ON_MW0602.md
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
 M ROADMAP.md
 M SETUP_GUIDE.md
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
 M config/secrets_example.py
 M config/strategy_params.py
… 외 417건
```

**당일(2026-08-20) 커밋**
```
f94536f [MW0601] 473차 F1~F3 검증 완료: F-8 Phase B 라이브 확인 — 배선 무결 + 경고 전제 정정
```

**최근 커밋 12건**
```
f94536f [MW0601] 473차 F1~F3 검증 완료: F-8 Phase B 라이브 확인 — 배선 무결 + 경고 전제 정정
091783c [MW0601] 480차 후속3: DECISION_LOG 테스트 집계 정정 — 576 passed / 신규 38건
ac73a18 [MW0601] 480차 후속2: F-5 폴백 경고 테스트를 전체 스위트에서도 통과하게 — caplog 제거
af2dbcc [MW0601] 480차 후속: F-2 수동 실행(--once)은 경보 마커를 남기지 않는다
c30e414 [MW0601] 480차 (3/3): 로드맵·dev_memory — 전환기준 ② 선행 ⓑ 추가 + 워치독 임계 26주 WFA 편입
9bb58eb [MW0601] 480차 (2/3): 0819 리포트 F-3·F-4·G-2 — ofi_norm 분포 프로브 + WaitDC 폴백 마커 + 로그 종료시각 기준선
ea60409 [MW0601] 480차 (1/3): 0819 리포트 F-2·G-1·F-5 — 프로세스 밖 FLAT 가드 + 하트비트 파일 + 진입 파라미터 승계
2330a66 [MW0601] 479차 후속: 배포 검증에서 발견 — pipeperf(SYSTEM 소급 glob, dev 전용) 예외 등록 + 문서 dev 특이점 2건
fdd80f5 [MW0601] 479차 (3/3): v9-dev 전용분 — 476차 스킬/설정 + test_476 + dev_memory 기록
49980d9 [MW0601] 479차 (2/3): 로그 채널별 차등 보관 — 측정 근거 + 압축 단계 + EOD 체인 발화 배선
59c516a [MW0601] 479차 (1/3): 476차 보관정책 재설계분 커밋 — monthly_cleanup 안전화 + 보관정책 문서
552d982 [MW0601] 478차 후속 검증: 장후 재기동·세션 복원 실행 — FZ-1 라이브 확인 + 누락 daily_close 복구
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
| `MODEL_LABEL_STATE_UNLOCK_ENABLED` | `—` | `True` | **미발견 ⚠** | 468차 G-1. 사이즈 제한 해제를 이벤트→상태 판정으로. **라이브 미검증** — `사이즈 축소 ×0.6` 0건 확인 전까지 CLAUDE.md ⑧ 해제 금지 |
| `PRE_RETRAIN_DONE_BY_EOD_ENABLED` | `—` | `True` | **미발견 ⚠** | 468차 F-1. EOD 완료로 `_pre_retrain_done` 해제 — G-1의 동반 스위치 |
| `ZONE_ENTRY_BAN_ENFORCE` | `—` | `False` | **미발견 ⚠** | 462차 P1-a. 🔴 True면 라이브 진입이 즉시 준다. 위반 7건이 오히려 흑자(+596,858원)라 [53] 채널 판정 전까지 False 유지 |
| `ZONE_ENTRY_BAN_SHADOW_ENABLED` | `—` | `True` | **미발견 ⚠** | 462차 P1-a 섀도. 집행과 무관하게 위반 계측은 항상 켜져 있어야 한다 |
| `PIPE_LATENCY_EXCLUDE_MODEL_SWAP` | `—` | `True` | **미발견 ⚠** | 462차 P2. 모델 교체 구간을 CB⑤ 판정용 지연에서만 차감(원값은 `raw=…ms`로 존치) |
| `VALIDATION_CAMPAIGN["mode"]` | `standing` | `standing` | 일치 | 2026-08-01 상시 운영 전환 |

> 이 표는 **의도한 예외가 여전히 의도대로인지** 보는 것이다. `불일치`는 누군가 바꿨다는 뜻이고, 바꿨다면 `dev_memory/DECISION_LOG.md` 에 근거가 있어야 한다.

### 차단 게이트 전수 인벤토리 — 30개 중 **8개 꺼짐**

| 플래그 | 값 | 기록됨 |
|---|---|---|
| `CB3_P4_GRADE_BLOCK_ENABLED` | False | 기록됨 |
| `FORCE_FLAT_GUARD_ORDER_ENABLED` | False | 기능토글 |
| `FP_CRITICAL_GRADE_BLOCK_ENABLED` | False | 기록됨 |
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

_본문 미열람(설정): `20260820_HOGA.log` 1.7MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/11개 (중요도순). 제외: `20260820_PROBE.log`, `launcher_20260820_084001_9654.log`, `20260820_DEBUG.log`_

### `logs/20260820_TRADE.log` — 167B · 2행 · 최종 08:41:29

- 형식 평문 · 시각 인식 2행 · INFO=2

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-20 08:41:24 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-20 08:41:29 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
  …
2026-08-20 08:41:24 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-20 08:41:29 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×2

**컴포넌트 상위 15** — `Position`×1, `ProfitGuard`×1

### `logs/20260820_WARN.log` — 1.7KB · 12행 · 최종 09:01:03

- 형식 평문 · 시각 인식 12행 · WARNING=12

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-20 08:41:32 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-08-20 08:41:32 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 31ms
2026-08-20 08:41:32 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 141ms account=333044256
2026-08-20 08:41:35 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3250ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[]
2026-08-20 08:41:40 [WARNING] SYSTEM: [LiveDBG] _restore_panels_worker 지연 4125ms — live 중단 원인 분석용
  …
2026-08-20 09:01:02 [WARNING] SYSTEM: [PipePerf] total=2353ms | S0=13ms S1=34ms S2=0ms S3=0ms S4=541ms S5=1200ms S6=498ms S7=22ms S8=44ms
2026-08-20 09:01:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2353ms | quality=0.86 | cache_age=89s | exceptions_10m=0
2026-08-20 09:01:02 [WARNING] SYSTEM: [CB⑤] 파이프라인 2353ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s]
2026-08-20 09:01:02 [WARNING] SYSTEM: [CB⑤] 파이프라인 2353ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s]
2026-08-20 09:01:03 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4344ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[]
```

</details>

**WARNING — 태그 4종 (상위 4)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 7 | 08:41:32 | 09:01:03 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `PipePerf` | 2 | 09:01:02 | 09:01:02 | total=2353ms | S0=13ms S1=34ms S2=0ms S3=0ms S4=541ms S5=1200ms S6=498ms S7=22ms S8=44ms |
| `CB⑤` | 2 | 09:01:02 | 09:01:02 | 파이프라인 2353ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `Health` | 1 | 09:01:02 | 09:01:02 | level=WARNING degraded=OFF | latency=2353ms | quality=0.86 | cache_age=89s | exceptions_10m=0 |

**채널** — `SYSTEM`×11, `HEALTH`×1

**컴포넌트 상위 15** — `LiveDBG`×7, `PipePerf`×2, `CB⑤`×2, `Health`×1

### `logs/20260820_SYSTEM.log` — 29.3KB · 229행 · 최종 09:01:05

- 형식 평문 · 시각 인식 222행 · INFO=222, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-20 08:40:50 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=13140 | 행감지=30s all_threads=True
2026-08-20 08:41:10 [INFO] SYSTEM: [System] DB 초기화 완료
2026-08-20 08:41:10 [INFO] SYSTEM: [System] 미륵이 초기화
2026-08-20 08:41:10 [INFO] SYSTEM: 미륵이 초기화
2026-08-20 08:41:10 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-08-19) 종가 버퍼 로드: 296봉
  …
2026-08-20 09:01:00 [INFO] SYSTEM: [ShadowSession] LIVE 전환 | 09:00 | core=100 z=0 가상PnL=+0.0pt
2026-08-20 09:01:02 [INFO] SYSTEM: [S6Detail] ensemble=14ms checklist_pre=156ms meta_gate=244ms gates=46ms imp=0ms shap=10ms corr=0ms dash_ui=0ms tail=27ms
2026-08-20 09:01:02 [INFO] SYSTEM: [PipePerf][DBG] total=2353ms | S0=13ms S1=34ms S2=0ms S3=0ms S4=541ms S5=1200ms S6=498ms S7=22ms S8=44ms
2026-08-20 09:01:05 [INFO] SYSTEM: [CybosRT-TICK] #4100 code=A0569 raw_time=90105 parsed=09:01:05 price=1045.44 vol=1 bid1=1045.44 ask1=1045.50 flag=50 side=SELL anchor=0/1
2026-08-20 09:01:10 [INFO] SYSTEM: [TickUI] alive ticks=4185 code=A0569 close=1045.92
```

</details>

**채널** — `SYSTEM`×222

**컴포넌트 상위 15** — `CybosRT-TICK`×46, `CybosSub`×21, `System`×17, `TickUI`×17, `CybosRT-ROLLOVER`×16, `BAR-CLOSE`×16, `CVD-ANCHOR`×16, `SYSTEM`×9, `PreMarket`×9, `CybosRT-START`×6, `Notify`×5, `BrokerSync`×4, `BalanceUI`×4, `-`×4, `EarlyWarmup`×3

### `logs/20260820_SIGNAL.log` — 19.4KB · 150행 · 최종 09:01:02

- 형식 평문 · 시각 인식 150행 · WARNING=96, INFO=54

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-20 08:40:46 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.419
2026-08-20 08:40:46 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.400
2026-08-20 08:40:46 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.396
2026-08-20 08:40:46 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.404
2026-08-20 08:40:46 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.409
  …
2026-08-20 09:01:02 [WARNING] SIGNAL: [ScalerFloor] 30m 'macro_us10y_chg' scale=0.1711 → floor=0.25 적용 (z-score 폭발 방지)
2026-08-20 09:01:02 [WARNING] SIGNAL: [ScalerFloor] 30m 'macro_risk_on' scale=0.0447 → floor=0.50 적용 (z-score 폭발 방지)
2026-08-20 09:01:02 [WARNING] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0429 → floor=0.15 적용 (z-score 폭발 방지)
2026-08-20 09:01:02 [WARNING] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.1231 → floor=0.20 적용 (z-score 폭발 방지)
2026-08-20 09:01:02 [INFO] SIGNAL: [ScalerRefresh] ts=09:00 trigger=B_OPEN elapsed=infmin n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.04s
```

</details>

**WARNING — 태그 4종 (상위 4)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerRefresh` | 42 | 08:45:03 | 09:01:02 | 1m CORE 'ofi_norm' raw_std≈0(0.0379) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ScalerFloor` | 36 | 09:01:02 | 09:01:02 | 1m 'macro_vix' scale=0.0136 → floor=0.10 적용 (z-score 폭발 방지) |
| `Model` | 12 | 09:01:00 | 09:01:00 | 1m 극단 z-score 3개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 6 | 09:01:00 | 09:01:00 | ts=09:00 horizon=1m age=2m max_z=-15.07(institution_futures_net) extreme=3 |

**채널** — `SIGNAL`×150

**컴포넌트 상위 15** — `ScalerFloor`×60, `ScalerRefresh`×48, `Model`×18, `DynMC`×7, `ScalerMonitor`×6, `TimeRouter`×3, `SIGNAL`×2, `EnsembleGater`×1, `FeatureBuilder`×1, `GapOffset`×1, `DayRegimeShadow`×1, `AutoMasked`×1, `ZeroDiag`×1

### `logs/20260820_LEARNING.log` — 47.8KB · 270행 · 최종 09:01:02

- 형식 평문 · 시각 인식 270행 · WARNING=130, INFO=140

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-20 08:41:12 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-08-20 08:41:14 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00049 auc=0.464 out_max=0.3127 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과
2026-08-20 08:41:14 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00002 auc=0.499 out_max=0.3750 (기준 auc<0.53 and span<0.020, 기저율=0.3750 n=80) → 보정 미적용, raw 통과
2026-08-20 08:41:14 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00062 auc=0.538 out_max=0.3559 (n=135) → 보정 재적용
2026-08-20 08:41:14 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00047 auc=0.523 out_max=0.3646 (기준 auc<0.53 and span<0.020, 기저율=0.3643 n=140) → 보정 미적용, raw 통과 [기존 fitted 해제]
  …
2026-08-20 08:55:03 [INFO] LEARNING: [MetaConf] 상태 복원 완료: meta_conf_state.pkl (fitted=[추세장, 횡보장, 급변장, 혼합], total=8718, ver=5)
2026-08-20 08:55:04 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-08-20 08:59:01 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-08-20 09:00:59 [INFO] LEARNING: [sigma] sigma_at_t=0.0000% buf_n=0 nonzero=0 prev_p=0.00 cur_p=1046.90
2026-08-20 09:01:02 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=500 feat=97
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 130 | 08:41:14 | 08:41:24 | 축퇴 감지 — span=0.00049 auc=0.464 out_max=0.3127 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과 |

**채널** — `LEARNING`×270

**컴포넌트 상위 15** — `Calibration`×255, `ScalerWarmup`×6, `ExtremityCorrector`×2, `Consolidator`×2, `RF`×1, `DriftAdjuster`×1, `SHAP`×1, `MetaConf`×1, `sigma`×1

### `logs/20260820_HEALTH.log` — 142B · 1행 · 최종 09:01:02

- 형식 평문 · 시각 인식 1행 · WARNING=1

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-20 09:01:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2353ms | quality=0.86 | cache_age=89s | exceptions_10m=0
  …
2026-08-20 09:01:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2353ms | quality=0.86 | cache_age=89s | exceptions_10m=0
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 1 | 09:01:02 | 09:01:02 | level=WARNING degraded=OFF | latency=2353ms | quality=0.86 | cache_age=89s | exceptions_10m=0 |

**채널** — `HEALTH`×1

**컴포넌트 상위 15** — `Health`×1

### `logs/20260820_MICRO.log` — 42.0KB · 114행 · 최종 09:01:05

- 형식 평문 · 시각 인식 114행 · DEBUG=114

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-20 08:45:03 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1051.26/1 ask1=1052.20/1 mp={'microprice_tick': 1051.73, 'midprice_tick': 1051.73, 'depth_bias_tick': 0.6476} mlofi_tick=None queue=None
2026-08-20 08:45:03 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1051.26/1 ask1=1052.16/11 mp={'microprice_tick': 1051.335, 'midprice_tick': 1051.71, 'depth_bias_tick': 0.0901} mlofi_tick=-12.6167 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 10.0, 'bid_cancel_add_rati…
2026-08-20 08:45:03 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1051.26/1 ask1=1052.16/11 mp={'microprice_tick': 1051.335, 'midprice_tick': 1051.71, 'depth_bias_tick': 0.0901} mlofi_tick=0.0 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -…
2026-08-20 08:45:03 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1051.26/4 ask1=1052.16/11 mp={'microprice_tick': 1051.5, 'midprice_tick': 1051.71, 'depth_bias_tick': 0.1654} mlofi_tick=-11.1167 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 3.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
2026-08-20 08:45:03 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1051.26/2 ask1=1052.16/11 mp={'microprice_tick': 1051.3985, 'midprice_tick': 1051.71, 'depth_bias_tick': 0.1063} mlofi_tick=-2.0 queue={'depletion_bid': 2.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
  …
2026-08-20 09:00:54 [DEBUG] MICRO: [MICRO-TICK] #7500 bid1=1047.22/1 ask1=1047.38/2 mp={'microprice_tick': 1047.2733, 'midprice_tick': 1047.3, 'depth_bias_tick': -0.226} mlofi_tick=5.9 queue={'depletion_bid': 1.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 1.0, 'bid_cancel_add_ratio': 0…
2026-08-20 09:00:59 [DEBUG] MICRO: [MICRO-MINUTE] #16 ts=2026-08-20 09:00:00 close=1046.90 bias=-0.002483 slope=-0.380852 depth_bias=0.0183 mlofi_norm=-0.041710 mlofi_pressure=-1 mlofi_slope=-51.401667 queue_signal=-0.0040 queue_ma=0.0107 queue_momentum=-0.0124 depletion=0.5000 refill=0.5000 imbala…
2026-08-20 09:01:03 [DEBUG] MICRO: [MICRO-TICK] #7600 bid1=1047.02/1 ask1=1047.40/1 mp={'microprice_tick': 1047.21, 'midprice_tick': 1047.21, 'depth_bias_tick': 0.1046} mlofi_tick=5.9333 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio…
2026-08-20 09:01:05 [DEBUG] MICRO: [MICRO-TICK] #7700 bid1=1045.54/1 ask1=1045.76/1 mp={'microprice_tick': 1045.65, 'midprice_tick': 1045.65, 'depth_bias_tick': -0.2194} mlofi_tick=0.0 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
2026-08-20 09:01:11 [DEBUG] MICRO: [MICRO-TICK] #7800 bid1=1045.88/1 ask1=1046.02/1 mp={'microprice_tick': 1045.95, 'midprice_tick': 1045.95, 'depth_bias_tick': -0.0987} mlofi_tick=-2.2833 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_rat…
```

</details>

**채널** — `MICRO`×114

**컴포넌트 상위 15** — `MICRO-TICK`×98, `MICRO-MINUTE`×16

### `logs/20260820_DATA.log` — 1.1KB · 5행 · 최종 09:01:00

- 형식 평문 · 시각 인식 5행 · INFO=5

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-20 08:58:06 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=150799 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-08-20 08:58:06 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-08-20 08:58:36 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=150803 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-08-20 08:58:36 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-08-20 09:01:00 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
  …
2026-08-20 08:58:06 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=150799 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-08-20 08:58:06 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-08-20 08:58:36 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=150803 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-08-20 08:58:36 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-08-20 09:01:00 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
```

</details>

**채널** — `DATA`×5

**컴포넌트 상위 15** — `CybosInvestor`×4, `DivergencePanel`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 0 |
| 진입 등록(`[Position] 진입`) | 0 |
| 체결(`[체결진입]`) | 0 |
| 청산(`체결청산`) | 0 |
| 차단(`[차단]`) | 0 |
| 사이저 호출(`[Sizer]`) | 0 |

### 메인 스레드 블로킹 2건 · 최대 4344ms · 5초 초과 0건

상위 — 4344ms, 3250ms

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260820_WARN.log`
```
--- 메인 스레드 블로킹 ×2(표본)
08:41:35 2026-08-20 08:41:35 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3250ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[]
09:01:03 2026-08-20 09:01:03 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4344ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[]
```

### `logs/20260820_SYSTEM.log`
```
--- PSI ×1(표본)
09:01:00 2026-08-20 09:01:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.008 level=0 (heartbeat)
```

### `logs/20260820_SIGNAL.log`
```
--- 기동 복원 ×7(표본)
08:40:46 2026-08-20 08:40:46 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.419
08:40:46 2026-08-20 08:40:46 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.400
08:40:46 2026-08-20 08:40:46 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.396
08:40:46 2026-08-20 08:40:46 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.404
```

### `logs/20260820_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:41:14 2026-08-20 08:41:14 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00049 auc=0.464 out_max=0.3127 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과
08:41:14 2026-08-20 08:41:14 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00002 auc=0.499 out_max=0.3750 (기준 auc<0.53 and span<0.020, 기저율=0.3750 n=80) → 보정 미적용, raw 통과
08:41:14 2026-08-20 08:41:14 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00062 auc=0.538 out_max=0.3559 (n=135) → 보정 재적용
08:41:14 2026-08-20 08:41:14 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00047 auc=0.523 out_max=0.3646 (기준 auc<0.53 and span<0.020, 기저율=0.3643 n=140) → 보정 미적용, raw 통과 [기존 fitted 해제]
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260820_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:24 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:41 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260820_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 6 | 08:41:32 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 6 | 09:01:02 [WARNING] total=2353ms | S0=13ms S1=34ms S2=0ms S3=0ms S4=541ms S5=1200ms S6=498ms S7=22ms S8=44ms |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 6 | 09:01:02 [WARNING] total=2353ms | S0=13ms S1=34ms S2=0ms S3=0ms S4=541ms S5=1200ms S6=498ms S7=22ms S8=44ms |

- 이 로그 생존구간: 08:41 ~ 09:01

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260820_SYSTEM.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 89 | 08:40:50 [INFO] 활성화 | file=logs\crash_fault.log PID=13140 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 120 | 08:49:00 [INFO] code=A0569 from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 87 | 08:54:00 [INFO] code=A0569 from=08:53 to=08:54 |

- 이 로그 생존구간: 08:40 ~ 09:01

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260820_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 55 | 08:45:03 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0379) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 88 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0366) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 81 | 08:55:04 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0428) → identity(0,1) 강제 (FLAT 100% 방지) |

- 이 로그 생존구간: 08:40 ~ 09:01

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260819 | 17:02 | 로그 본문 |
| 20260818 | 15:40 | 로그 본문 |
| 20260817 | 17:58 | 로그 본문 |
| 20260814 | 15:40 | 로그 본문 |
| 20260813 | 15:40 | 로그 본문 |
| **중앙값** | **15:40** | 기준선 |
| **오늘 20260820** | **09:01** | 로그 본문 |

- 델타 **-399분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 1.9MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 검증
### [정정] 위 478차 후속2 항목은 **최초 보고가 아니다** — 미종료 딥다이브가 정본
### [478차 후속 구현] FZ-1~FZ-9 배포 — 동결 워치독 + 위상 분리 + 워커 가드
### [478차 후속 검증] 장후 재기동·세션 복원 실행 — FZ-1 라이브 배선 확인 + 누락 daily_close 복구
## 2026-08-18 (MW0601 476차 후속 — 점검 산출물 보관정책 이식) [479차 세션에서 소급 기록]
### [1] monthly_cleanup.py가 백업 없는 시계열 원자재를 지우도록 대기 중이었다 (P0급)
## 2026-08-19 (MW0601 479차 — 로그 채널별 차등 보관: 측정·압축·발화 배선)
### [1] 476차 §6-1 미결(차등 보관) 측정으로 종결 — 3계층 확정
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
1 이후 구간에서 결측이 되는
  것은 정상이다(`ready=False` 처리). 그것을 결함으로 보고 백필을 재시도하지 말 것.
- **검증**: 위 전부 로그·DB 실측. 상세 표는
  `docs/정기점검/매일점검/MW0601-20260819-미종료-딥다이브.md` §9.

## 2026-08-18 (MW0601 476차 후속 — 점검 산출물 보관정책 이식) [479차 세션에서 소급 기록]

### [1] monthly_cleanup.py가 백업 없는 시계열 원자재를 지우도록 대기 중이었다 (P0급)

**증상**: `scripts/monthly_cleanup.py`가 `PRED_KEEP_DAYS=60`으로 `predictions` ·
`ensemble_decisions` · `meta_labels` 행을 삭제하도록 돼 있고, NEXT_TODO에
`[NEXT 2026-07-01] --apply`가 미완료 항목으로 두 번 걸려 있었다. 실행됐다면
2026-08-19 기준 `ensemble_decisions` 10,168행(41.5%) · `predictions` 55,324행(54.4%) ·
`meta_labels` 55,182행(55.4%)이 사라졌다. predictions.db는 gitignore + 백업 7일 →
삭제 = 영구 소실.

**결정**: DB 행 삭제를 기본 비활성(`--allow-db-prune` 필요)으로, 켜더라도
`_MIN_KEEP_DAYS_DB = 190`(26주 182일 + 여유) 하한 강제. `LOG_KEEP_DAYS` 30 → 190.

**Why**: 실측 소급 인용 꼬리가 182일 = 26주 WFA 주기. 증거 다이제스트는 원본 로그가
있어야 재생성되므로 로그 보관이 증거의 재생성 가능성을 결정한다. FP-CRITICAL·
TOX-SEVERE-SPREAD와 반대 방향의 같은 결함(저쪽은 계측이 안 돌았고, 이쪽은 계측을
지우는 코드가 돌기를 기다렸다).

**How to apply**: monthly_cleanup.py — ALLOW_DB_PRUNE 플래그, 보관 하한, 파일명 날짜
판정, 보호 패턴, 삭제 목록 전부 인쇄. collect_evidence.py — `--pc` 인자(우선순위
인자 > MIREUK_PC_ID > 호스트명), UNKNOWN이면 프룬 중단. 전문:
`docs/정기점검/보관정책_MW0601-20260818.md`.

**검증**: dry-run 190일 컷 전 테이블 0행 · `tests/test_476_evidence_retention.py` 12 passed.

## 2026-08-19 (MW0601 479차 — 로그 채널별 차등 보관: 측정·압축·발화 배선)

### [1] 476차 §6-1 미결(차등 보관) 측정으로 종결 — 3계층 확정

**측정**(2026-08-19): ① 점검 문서의 로그 파일 인용 558건 전수 — 과거분은 WARN
1건(1일)뿐, HOGA·SYSTEM 포함 전부 당일 인용. ② 원본 .log를 소급 glob하는 소비자는
TRADE(5개 스크립트)·SIGNAL(2)·PROBE(1)뿐, 합계 39MB. ③ 용량 96%(SYSTEM 3.8GB +
HOGA 2.4GB)는 소급 소비자 0. ④ HOGA는 원시 5호가 잔량의 유일 원장(raw_data.db에
호가 테이블 없음). ⑤ 압축률 실측 HOGA 8% · SYSTEM 2%.

**결정**: Tier A(TRADE·SIGNAL·PROBE) 원본 190일 유지 / Tier B(SYSTEM·HOGA·MICRO 등
9종) 30일 후 월 zip → 압축본 190일 컷, 단 HOGA 압축본은 삭제 면제(주간회의 결정 전
보수 기본값) / Tier C(crash·날짜없음·json) 기존 보호. 발화 지점은 campaign_steps.py
(EOD 체인 공용 모듈) 한 곳 — 매월 첫 캠페인 실행일 마지막 스텝, 마커
data/monthly_cleanup_last_run.txt(gitignore).

**Why**: "측정 없는 차등은 근거 없는 30일의 반복"(476차) — 측정으로 근거를 만든 뒤
차등했다. 압축(이동)이지 삭제(소실)가 아니므로 HOGA 원장이 보존된다.

**How to apply**: monthly_cleanup.py [0]장중가드/[1a]압축/[1b]원본컷(Tier B 구조적
제외)/[1c]압축본컷(HOGA 면제) + campaign_steps.py monthly_cleanup_due()/마커 +
tests/test_479_log_retention_tiers.py 10케이스. 전문:
`docs/정기점검/보관정책_로그차등_MW0601-20260819.md`.

**검증**: 22 passed(476+479) · dry-run 삭제 0건 · 첫 --apply 실측
4,878MB→210.5MB(4.3%), logs/ 6.5GB→1.78GB, CRC 검증 경고 0건.
2026-08-21(금) EOD 로그의 `월간 로그 정리 → 완료`가 배선 라이브 검증.
MW0602 배포: 커밋 (1/3)(2/3)을 dev에 체리픽 — 절차는 위 문서 §5.

```

</details>

### dev_memory/NEXT_TODO.md — 1001.2KB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 477차 후속1~3 — 476차 Fix 구현 완료 (MW0601, 2026-08-18 · 커밋 3건)
### 477차 후속5 — 476차 §3 고도화 방안 조사 결과 (MW0601, 2026-08-18 · 조사만)
### 477차 후속6 — GR-1 구현 완료 (MW0601, 2026-08-18)
### 477차 후속7 — GR-3 구현 완료 (MW0601, 2026-08-18)
### 478차 — 장전 점검 (MW0601, 2026-08-19 · 분석만, 코드 0건)
### 478차 후속 — 장중 점검 (MW0601, 2026-08-19 · 분석만, 코드 0건)
### 478차 후속 — 08-19 메인 스레드 라이브락(미종료 사고) Fix (MW0601, 상세: MW0601-20260819-미종료-딥다이브.md §5)
### 478차 후속2 — 장후 점검 (MW0601, 2026-08-19 · 분석만, 코드 0건)
```

미완료 체크박스 **1501건** (끝에서 30건)
```
- [ ] **F-2 15:10 프로세스 밖 최후 방어선 (P0, F-1 다음)** —
- [ ] **F-3 `ofi_norm` 원값 분포 프로브 (P1)** — `scripts/ofi_norm_distribution_probe.py` 신설(읽기 전용,
- [ ] **F-4 EOD `WaitDC` 폴백 마커 가시화 (P2)** — `scripts/eod_retrain.py`가
- [ ] **G-1 하트비트를 별도 파일로 분리 (F-1과 같은 커밋)** — 오늘 `data/session_state.json` mtime은
- [ ] **G-2 수집기 §7에 "로그 생존구간 vs 직전 5거래일 중앙값" 대조 상설 편입** —
- [ ] **G-3 `[Position] 진입` 로그를 포지션 개시 3경로 공통으로 승격** —
- [ ] **G-7 착수 조건 성립** — IntradayRegime 전이 **51회(반일)** vs 08-18 22회(종일).
- [ ] **P-1** — 08:40 기동 정상 완료(`[FaultHandler] 활성화` → `[System] Qt 이벤트 루프 진입`).
- [ ] **P-2** — SYSTEM 로그 생존구간이 15:40까지. 15:20 이전 종료면 **P0 재발, 최상단**
- [ ] **P-3** — `[Position] 진입` 없이 `[체결진입]`만 있는 포지션. 1건 이상이면 O-2 누적 2건 → F-5 상향
- [ ] **P-4** — `ofi_norm` identity 강제율(종일). 3거래일 연속 90%+면 CORE 재심사 안건 상정
- [ ] **P-5** — IntradayRegime 종일 전이. 40회 이상 2일 연속이면 G-7 즉시 착수
- [ ] **P-6** — `[BrokerPnl] EOD 확정 — gross … net …`(G-D). 미출현이면 GR-3 배선 재확인
- [ ] **P-7** — `data/daily_close_done_20260820.txt` 생성 여부
- [ ] **R-후보(5거래일 누적 후 판정)** — 등급 인플레(원시 C → A급) 축. 오늘 2건 승1 패1이고
- [ ] **[실전전환기준 ②에 선행 확인사항 추가 제안]** — *"장중 프로세스 정지 감지·조치 경로 1회 실측"*.
- [ ] **[로드맵] 26주 WFA 재검증 항목에 라이브니스 워치독 임계(180초) 편입 제안** —
- [ ] **[08-29 CB② 보강]** — 오늘 **CASE-02(11:11 SHORT 3계약)가 한 포지션으로 `연속 손절 1회`·`2회`를
- [ ] **F-2 유지 — 후속2 고유 항목.** 딥다이브 P0-1은 스스로 *"15:10 이후 동결이면 런처가
- [ ] **G-1 조정** — 딥다이브 P0-1의 `_main_beat`를 파일로도 내보내는 형태로, **P0-1과 같은 커밋**.
- [ ] **G-2 병합** — 딥다이브 **P2-2**(장중 로그 침묵)와 같은 커밋. 잡는 구간이 다르다 —
- [ ] **딥다이브 고유 항목은 그대로 채택** — P1-1(COM 타이머 위상 분리 +17s) ·
- [ ] **FZ-1L (P1) 라이브 리허설** — 하드 종료 → 런처 RESTART_LOOP 재기동 → 세션 복원의
- [ ] **FZ-10 (주간회의 안건) 26주 WFA 재검증 항목 편입** — FZ-1L을 471차 G-3(15:10 경로
- [ ] **FZ-8 (선택) 풀 덤프 WinDbg 분석** — `c:	mp\mireuk_freeze_20260819_pid21612.dmp`
- [ ] **FZ-11 (관찰, 08-20) 워치독 오탐 0건 확인** — `logs/crash_fault.log`의 `[TS]` 줄에서
- [ ] **[MW0601 479차] HOGA 압축본 190일 컷 면제 해제 여부 — 주간회의 안건.**
- [ ] **[MW0601 479차] 월간 로그 정리 배선 라이브 검증** — 2026-08-21(금) EOD 로그에서
- [ ] **[MW0601 479차] MW0602 배포 확인** — dev 체리픽 push 완료 후, MW0602에서
- [ ] **`raw_data.db`(508MB)·`shap_tracker.db`(132MB) 보관정책 부재** — 별도 조사
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
복).** 딥다이브 **P0-2**로 대체.
      ⚠ 조치 자체는 여전히 필요하다 — `Stop-Process -Id 21612 -Force`.
      **덤프는 이미 보존됨**(`c:\tmp\mireuk_freeze_20260819_pid21612.dmp`, 1.29GB)
- [x] ~~**F-1 외부 라이브니스 워치독**~~ → **철회.** 딥다이브 **P0-1**(인프로세스
      `threading.Thread(daemon)` + `_main_beat` + 180초×2회 → `os._exit(43)` →
      런처 RESTART_LOOP 자동 재기동)이 우월하다 — 외부 프로세스는 정지를 알려도 **복구시키지 못한다**
- [ ] **F-2 유지 — 후속2 고유 항목.** 딥다이브 P0-1은 스스로 *"15:10 이후 동결이면 런처가
      재시작하지 않는다"*고 적었다. **그 빈 구간이 정확히 절대원칙 §1의 집행 시각(15:10~15:35)이다.**
      `scripts/force_flat_guard.py` + `FORCE_FLAT_GUARD_ENABLED=False`(섀도, 알림만)
- [ ] **G-1 조정** — 딥다이브 P0-1의 `_main_beat`를 파일로도 내보내는 형태로, **P0-1과 같은 커밋**.
      ⚠ 별도 하트비트를 새로 만들지 말 것(이중 진실원천)
- [ ] **G-2 병합** — 딥다이브 **P2-2**(장중 로그 침묵)와 같은 커밋. 잡는 구간이 다르다 —
      P2-2는 *장중 침묵*, G-2는 *장후 조기종료*
- [ ] **딥다이브 고유 항목은 그대로 채택** — P1-1(COM 타이머 위상 분리 +17s) ·
      P1-2(워커 이상소요·이상결과 가드) · P2-1(`crash_fault.log` 시각 부여).
      ⚠ P2-1은 본 점검도 같은 애로를 겪었다 — 블록 개수를 역산해 시각을 추정해야 했다

#### FZ 후속 — 478차 후속 구현(2026-08-19) 이후 남은 것

- [ ] **FZ-1L (P1) 라이브 리허설** — 하드 종료 → 런처 RESTART_LOOP 재기동 → 세션 복원의
      **실제 왕복은 아직 미관측**이다. 절차: `python scripts/freeze_watchdog_rehearsal.py
      --live-instructions`. 임시 sleep 주입 훅으로 1회 확인 후 **훅 제거**할 것 —
      사고 유발기를 프로덕션 코드에 상시로 두지 않는다. 모의·FLAT·08:45~08:55 한정
- [ ] **FZ-10 (주간회의 안건) 26주 WFA 재검증 항목 편입** — FZ-1L을 471차 G-3(15:10 경로
      리허설)과 같은 성격으로 26주 주기에 넣을지 결정. 별도 캘린더를 만들면 CB②·
      CB③-P4·FP-CRITICAL처럼 "재검토하기로 했는데 안 함"이 된다(317차 원칙)
- [ ] **FZ-8 (선택) 풀 덤프 WinDbg 분석** — `c:	mp\mireuk_freeze_20260819_pid21612.dmp`
      메인 스레드 네이티브 스택으로 스핀 DLL 특정. FZ-3(위상 분리)는 **원인 확정이 아니라
      폭 좁히기**이므로, 이것이 확정되기 전에는 "겹침을 없앴으니 안 난다"고 쓰지 말 것
- [ ] **FZ-11 (관찰, 08-20) 워치독 오탐 0건 확인** — `logs/crash_fault.log`의 `[TS]` 줄에서
      `beat_age`가 장중 내내 0~5초를 유지하는지. 30초 이상 튀는 구간이 있으면 임계
      재검토 전에 **그 블로킹의 정체를 먼저 밝힐 것**(그것이 진짜 수확이다)

- [ ] **[MW0601 479차] HOGA 압축본 190일 컷 면제 해제 여부 — 주간회의 안건.**
  원시 5호가의 유일 원장(raw_data.db에 호가 테이블 없음) + CORE 피처 점질량 조사
  (CLAUDE.md §3)가 원시 재생을 요구할 수 있어 보수 기본값 = 무기한 보존(~3.3MB/일).
  근거: `docs/정기점검/보관정책_로그차등_MW0601-20260819.md` §7.
- [ ] **[MW0601 479차] 월간 로그 정리 배선 라이브 검증** — 2026-08-21(금) EOD 로그에서
  `[검증 캠페인] 월간 로그 정리 → 완료` + `data/monthly_cleanup_last_run.txt=202608` 확인.
- [ ] **[MW0601 479차] MW0602 배포 확인** — dev 체리픽 push 완료 후, MW0602에서
  `git pull` → `python scripts/monthly_cleanup.py` dry-run(삭제 0건·번들 목록 타당성)
  → 첫 금요일 EOD 자동 실행 확인. 절차: 보관정책_로그차등 문서 §5.
- [ ] **`raw_data.db`(508MB)·`shap_tracker.db`(132MB) 보관정책 부재** — 별도 조사
  (476차 §6-3에서 이월).

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

### `data/heartbeat_MW0601_20260820.json` — 244B · 08-20 09:01:04
```json
{
 "pid": 13140,
 "written_at": "2026-08-20T09:01:04",
 "beat_epoch": 1787184063.9644706,
 "beat_age_sec": 0.3,
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

### `docs/정기점검/매일점검` — 51개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260819-미종료-딥다이브.md` | 26.0KB | 08-19 17:07 |
| `docs/정기점검/매일점검/MW0601-20260819-점검리포트-post.md` | 42.9KB | 08-19 16:39 |
| `docs/정기점검/매일점검/evidence_MW0601-20260819_post.md` | 63.9KB | 08-19 16:22 |
| `docs/정기점검/매일점검/MW0601-20260819-점검리포트-intra.md` | 33.7KB | 08-19 12:42 |
| `docs/정기점검/매일점검/evidence_MW0601-20260819_intra.md` | 59.8KB | 08-19 12:26 |
| `docs/정기점검/매일점검/MW0601-20260819-점검리포트-pre.md` | 33.8KB | 08-19 09:11 |
| `docs/정기점검/매일점검/evidence_MW0601-20260819_pre.md` | 46.2KB | 08-19 09:00 |
| `docs/정기점검/매일점검/MW0601-20260818-고도화방안검토.md` | 16.3KB | 08-18 23:04 |

### `docs/정기점검/금요일점검` — 53개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/MW0601/profit_guard_latch_20260818.json` | 7.6KB | 08-18 22:58 |
| `docs/정기점검/금요일점검/MW0601/profit_guard_latch_20260818.md` | 3.8KB | 08-18 22:58 |
| `docs/정기점검/금요일점검/weekly_prompt.txt` | 1.8KB | 08-16 15:46 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260814.md` | 4.9KB | 08-14 15:50 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260814.json` | 2.9KB | 08-14 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260814.md` | 26.2KB | 08-14 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260814.json` | 34.4KB | 08-14 15:50 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260814.md` | 163.4KB | 08-14 15:49 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. 설정 불변식 `MODEL_LABEL_STATE_UNLOCK_ENABLED` = `None` (기대 `True`) — 468차 G-1. 사이즈 제한 해제를 이벤트→상태 판정으로. **라이브 미검증** — `사이즈 축소 ×0.6` 0건 확인 전까지 CLAUDE.md ⑧ 해제 금지
2. 설정 불변식 `PRE_RETRAIN_DONE_BY_EOD_ENABLED` = `None` (기대 `True`) — 468차 F-1. EOD 완료로 `_pre_retrain_done` 해제 — G-1의 동반 스위치
3. 설정 불변식 `ZONE_ENTRY_BAN_ENFORCE` = `None` (기대 `False`) — 462차 P1-a. 🔴 True면 라이브 진입이 즉시 준다. 위반 7건이 오히려 흑자(+596,858원)라 [53] 채널 판정 전까지 False 유지
4. 설정 불변식 `ZONE_ENTRY_BAN_SHADOW_ENABLED` = `None` (기대 `True`) — 462차 P1-a 섀도. 집행과 무관하게 위반 계측은 항상 켜져 있어야 한다
5. 설정 불변식 `PIPE_LATENCY_EXCLUDE_MODEL_SWAP` = `None` (기대 `True`) — 462차 P2. 모델 교체 구간을 CB⑤ 판정용 지연에서만 차감(원값은 `raw=…ms`로 존치)
6. `logs/20260820_LEARNING.log`: **축퇴** 8건(표본)
7. 미커밋 변경 457건

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260820*.log` (Windows) / `grep 강제청산 logs/*20260820*.log`*